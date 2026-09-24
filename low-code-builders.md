# Low-code internal-tool builders: NocoDB, Baserow, Appsmith, Budibase, and Windmill

These tools sit on top of your databases and APIs and let people build internal apps, forms and
automations quickly. That is also the exposure. Each one stores credentials for the systems it connects
to, and Windmill runs arbitrary code by design. Three first-run patterns recur. On a fresh instance, the
first visitor becomes the administrator. Open signup is on by default. And the vendor's own sample
configuration ships fixed secrets that too many deployments keep. Keep every one of them private
([docker.md](docker.md), [cloud-firewalls.md](cloud-firewalls.md), [tunnels.md](tunnels.md)), claim the
admin account before the instance is reachable, and front the web UI per
[fronting-auth.md](fronting-auth.md), [nginx.md](nginx.md) or [caddy.md](caddy.md). Treat the database
behind each tool as a store of every connected system's credentials ([secrets.md](secrets.md)).
Versions checked: NocoDB 2026.09.0, Baserow 2.3.4, Appsmith v2.4.1, Budibase v3.46.0 and Windmill
v1.817.0.

## NocoDB

NocoDB listens on port 8080 (`process.env.PORT || '8080'`), and its entry point calls `listen` with no
host. For an omitted host, Node "will accept connections on the unspecified IPv6 address (`::`) when IPv6
is available, or the unspecified IPv4 address (`0.0.0.0`) otherwise", so the server listens on every
interface. The first account to sign up gets the super-admin role, and later self-signups are allowed
unless invite-only signup is on; `invite_only_signup` defaults to `false`. Claim the admin account first,
or seed it with `NC_ADMIN_EMAIL` and `NC_ADMIN_PASSWORD`, then turn on invite-only signup.

Two secrets need your attention:

- **`NC_CONNECTION_ENCRYPT_KEY`.** When it is unset, the encryption helper returns the value unchanged,
  so the credentials of every external database you connect are stored in plaintext in NocoDB's meta
  database. Set it before connecting a data source. The vendor docs warn that changing it later may
  break the application.
- **`NC_AUTH_JWT_SECRET`.** When it is unset, NocoDB generates one and stores it in the meta database,
  which is fine. The README's Docker example hard-codes one literal value
  (`569a1821-0a93-45e8-87ab-eb857f20a010`), so everyone who copies that example signs sessions with
  the same key. Generate your own.

The server trusts proxy headers and allows every CORS origin, so put it behind a proxy you control
rather than on the network directly. The README says the release binaries "are only for quick testing
locally"; production installs use the container image or the vendor's install script.

## Baserow

Baserow's default Compose file publishes the bundled Caddy on 80 and 443 at
`${HOST_PUBLISH_IP:-0.0.0.0}`, so every interface unless you set `HOST_PUBLISH_IP`. The vendor's install
guide warns that "docker when exposing ports on 0.0.0.0 will bypass any ufw firewall rules", and
suggests `-p 127.0.0.1:80:80 -p 127.0.0.1:443:443` if public exposure is not intended. The first user
to sign up is made staff (`is_staff=not User.objects.exists()`), and new signups are allowed by default
(`allow_new_signups` defaults to `True`). Sign up first, then turn off new signups in the admin
settings.

The Compose file refuses to start without `SECRET_KEY`, `DATABASE_PASSWORD` and `REDIS_PASSWORD`
(`${SECRET_KEY:?}`), and `.env.example` leaves them empty rather than shipping examples, so the secrets
are yours to generate. Baserow supports TOTP two-factor authentication in its core.

## Appsmith

Appsmith's Java server binds to `127.0.0.1` on 8080 by default (`APPSMITH_SERVER_ADDRESS`), inside a
container fronted by a bundled Caddy on port 80. The vendor's development Compose file publishes that
on host port 8080, and its AWS example on 80 and 443. Signup is enabled by default
(`APPSMITH_SIGNUP_DISABLED` defaults to `false`). On a fresh instance, the first user to sign up claims
the super-user slot while no users exist. Claim it before exposing the instance, then set
`APPSMITH_SIGNUP_DISABLED=true` or restrict signup with `APPSMITH_SIGNUP_ALLOWED_DOMAINS`.

Datasource credentials are encrypted with `APPSMITH_ENCRYPTION_PASSWORD` and
`APPSMITH_ENCRYPTION_SALT`. On first start, the image's entrypoint generates random 13-character values
for both. But the vendor's development Compose file sets both to `abcd`, and values passed from outside
override the generated ones. Anyone who copies that file encrypts every stored datasource credential
with a published key. Remove those two lines, or set long random values, before the first start.

## Budibase

Budibase's Compose file publishes its nginx proxy on `MAIN_PORT` (10000 in the sample `.env`) and its
LiteLLM service on `${LITELLM_PORT:-4000}`. The proxy forwards `/db/` to CouchDB. The sample
`hosting/.env` sets `JWT_SECRET` and `API_ENCRYPTION_KEY` to `testsecret`, and the CouchDB, MinIO and
Redis passwords, `INTERNAL_API_KEY` and `LITELLM_MASTER_KEY` to `budibase`, under a comment that says
"These should be updated". Nothing in the code rejects those values. With the sample file unchanged,
anyone who can reach the proxy can try `budibase`/`budibase` against CouchDB through `/db/`, and the
LiteLLM port answers to the master key `budibase`. Replace every one of those values before the first
start.

The first-run admin route `POST /api/global/users/init` needs no login and works until the first user
exists; after that it returns an error ("You cannot initialise once an global user has been created").
Create the admin first, or seed it with `BB_ADMIN_USER_EMAIL` and `BB_ADMIN_USER_PASSWORD`.

## Windmill

Windmill runs scripts in Python, TypeScript, Go, Bash and more on its workers, so a Windmill login is
code execution on your worker hosts. The server listens on port 8000 on every interface by default
(`DEFAULT_SERVER_BIND_ADDR` is `0.0.0.0`; set `SERVER_BIND_ADDR` to change it). A fresh instance has one
account, `admin@windmill.dev`, a super admin whose password is `changeme`; the README gives them as the
default credentials.

On a v1.817.0 loopback run with `SERVER_BIND_ADDR=127.0.0.1`, the only password user in a fresh database
was `admin@windmill.dev`, a super admin. Logging in with `changeme` returned `200` and a token, and
`whoami` confirmed super-admin rights. After the password was changed, `changeme` got `400` and the new
password `200`. The server's only listener was on 127.0.0.1, at the test port the run set. Change
the password before anything else can reach the server, and bind it privately.

The worker sandbox is not on by default either. `DISABLE_NSJAIL` defaults to `true` in the worker, and
on the loopback run, without nsjail installed, the worker logged "Nsjail sandboxing will NOT be
available". The vendor's Compose file runs the worker with `privileged: true` and publishes port 25 for
email triggers. Its debugger setting carries the vendor's warning: `REQUIRE_SIGNED_DEBUG_REQUESTS`
"Do NOT set to false on any internet-reachable deployment: it exposes an unauthenticated code-execution
debugger". Do not publish 25 unless you use email triggers.

## Verify

The sample-values check and the Windmill login pair were demonstrated; everything else here is
reasoned. The authoring host
has no container runtime, and NocoDB 2026.09.0, Baserow, Appsmith and Budibase ship for production as
container images, so none of them was run. NocoDB's npm package is older than 2026.09.0, and Windmill's
default all-interfaces bind was not observed, because the host forbids binding every interface. Backlog
row 1.109 tracks demonstrating the rest. On the host:

```bash
sudo ss -tlnp   # 8080 (NocoDB; Appsmith dev Compose), 80/443 (Baserow Caddy), 10000 and 4000 (Budibase), 8000 and 25 (Windmill): loopback or private only
```

Exposed, the reasoned expectation is a wildcard address for NocoDB's 8080, Windmill's 8000 and any
published Compose port; fixed means a loopback or private address.

Check the deployment's own environment for the vendor sample values. This was demonstrated against the
vendor files themselves: run on Budibase's sample `hosting/.env` it prints the `testsecret` and
`budibase` lines, and on Appsmith's development Compose file the two `abcd` lines; on a file with those
values replaced it prints "no vendor sample values found". It also flags the `changeme` Postgres
password in Windmill's Compose file.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ENV_OR_COMPOSE_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not checking"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not checking"; exit; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute your file on the set -- line above; not checking"; exit ;; esac
  [ -f "$1" ] || { echo "no such file: $1; not checking"; exit; }
  grep -n -E '=(testsecret|budibase|changeme)$|: *(abcd|changeme)$|569a1821-0a93-45e8-87ab-eb857f20a010' -- "$1" \
    && echo "FOUND vendor sample values: replace them" || echo "no vendor sample values found"
)
```

For Windmill, the demonstrated check is whether the default login still works. The password below is
the vendor's published default, not a secret, and a `400` is the fixed state.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_WINDMILL_BASE_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the base URL (https://...) on the set -- line above; not probing" ;;
    *) printf '%s' '{"email":"admin@windmill.dev","password":"changeme"}' |  # guard-conventions: allow the vendor's published default password, whose rejection is the fixed state
         curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 15 \
           -H 'Content-Type: application/json' --data-binary @- \
           -w 'default login: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1/api/auth/login" ;;
  esac
)
```

Exposed, the default login gets `200` with a token; fixed, it gets `400` (both observed with this
block on the loopback run). Before trusting a `400`, log in
once with your real credentials, so that a dead service is not read as fixed. The reasoned checks for
the other tools follow the same shape. From a host that should not have access, NocoDB, Baserow,
Appsmith and Budibase should refuse the connection. On each instance, a signup attempt with a fresh
address should be refused once you have turned signup off. On Budibase, `POST /api/global/users/init`
should return the "cannot initialise" error. The distinguishing behaviour for each is in the cited
source.

## Sources (checked September 2026)

- NocoDB 2026.09.0 port default: https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/Noco.ts
- NocoDB 2026.09.0 entry point (listen with no host, trust proxy, CORS): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/run/dockerEntry.ts
- NocoDB 2026.09.0 first user and signup: https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/services/users/users.service.ts
- NocoDB 2026.09.0 app settings (`invite_only_signup`): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/interface/AppSettings.ts
- NocoDB 2026.09.0 credential encryption: https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/encryptDecrypt.ts
- NocoDB 2026.09.0 README (Docker example JWT secret, binaries note): https://github.com/nocodb/nocodb/blob/2026.09.0/README.md
- Node.js v22 `server.listen` with an omitted host: https://github.com/nodejs/node/blob/v22.22.1/doc/api/net.md
- Baserow 2.3.4 Compose file: https://github.com/baserow/baserow/blob/2.3.4/docker-compose.yml
- Baserow 2.3.4 install with Docker (ufw warning): https://github.com/baserow/baserow/blob/2.3.4/docs/installation/install-with-docker.md
- Baserow 2.3.4 first user and signup: https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/core/user/handler.py
- Baserow 2.3.4 settings model (`allow_new_signups`): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/core/models.py
- Baserow 2.3.4 sample environment: https://github.com/baserow/baserow/blob/2.3.4/.env.example
- Appsmith v2.4.1 server properties (bind address, signup): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/resources/application-ce.properties
- Appsmith v2.4.1 first super user: https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/solutions/ce/UserSignupCEImpl.java
- Appsmith v2.4.1 image entrypoint (generated encryption values): https://github.com/appsmithorg/appsmith/blob/v2.4.1/deploy/docker/fs/opt/appsmith/entrypoint.sh
- Appsmith v2.4.1 development Compose file: https://github.com/appsmithorg/appsmith/blob/v2.4.1/deploy/docker/docker-compose.yml
- Budibase v3.46.0 sample environment: https://github.com/Budibase/budibase/blob/v3.46.0/hosting/.env
- Budibase v3.46.0 Compose file: https://github.com/Budibase/budibase/blob/v3.46.0/hosting/docker-compose.yaml
- Budibase v3.46.0 proxy configuration (`/db/`): https://github.com/Budibase/budibase/blob/v3.46.0/hosting/proxy/nginx.prod.conf
- Budibase v3.46.0 public worker routes: https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/index.ts
- Budibase v3.46.0 admin init: https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/controllers/global/users.ts
- Windmill v1.817.0 README (default credentials): https://github.com/windmill-labs/windmill/blob/v1.817.0/README.md
- Windmill v1.817.0 server defaults: https://github.com/windmill-labs/windmill/blob/v1.817.0/backend/src/main.rs
- Windmill v1.817.0 worker (`DISABLE_NSJAIL`): https://github.com/windmill-labs/windmill/blob/v1.817.0/backend/windmill-worker/src/worker.rs
- Windmill v1.817.0 Compose file: https://github.com/windmill-labs/windmill/blob/v1.817.0/docker-compose.yml
- Windmill v1.817.0 seeded-user migrations: https://github.com/windmill-labs/windmill/blob/v1.817.0/backend/migrations/20220123221903_first.up.sql and https://github.com/windmill-labs/windmill/blob/v1.817.0/backend/migrations/20220816185849_remove_non_admin_users.up.sql
