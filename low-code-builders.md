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
interface; its code passes no host, so NocoDB offers no bind setting. Restrict it with the container
publication or a firewall. The first account to sign up gets the super-admin role, and later self-signups are allowed
unless invite-only signup is on; `invite_only_signup` defaults to `false`. Claim the admin account first,
or seed it with `NC_ADMIN_EMAIL` and `NC_ADMIN_PASSWORD`, then turn on invite-only signup.

Two secrets need your attention:

- **`NC_CONNECTION_ENCRYPT_KEY`.** When it is unset, the encryption helper returns the value unchanged,
  so the credentials of every external database you connect are stored in plaintext in NocoDB's meta
  database. Set it before connecting a data source; when it is set later, NocoDB encrypts the existing
  sources on startup.
- **`NC_AUTH_JWT_SECRET`.** When it is unset, NocoDB generates a UUID, stores it in the meta database
  as `nc_auth_jwt_secret` and uses it, which is fine. The README's Docker example hard-codes one literal
  value (`569a1821-0a93-45e8-87ab-eb857f20a010`), so everyone who copies that example signs sessions
  with the same key. Generate your own.

The entry file allows every CORS origin. It also enables Express's `trust proxy`, but startup then
resets that from `NC_TRUST_PROXY`, which trusts no proxy unless you set it; once a proxy is in front,
set it to that proxy's hop count or subnet, and never to `true` on a server clients can reach directly. The README says the release binaries "are only for quick testing
locally", and the 2026.09.0 GitHub release publishes no binaries; production installs use the
container image or the vendor's install script.

## Baserow

Baserow's default Compose file publishes the bundled Caddy on 80 and 443 at
`${HOST_PUBLISH_IP:-0.0.0.0}`, so every interface unless you set `HOST_PUBLISH_IP`. The vendor's install
guide warns that "docker when exposing ports on 0.0.0.0 will bypass any ufw firewall rules", and
suggests `-p 127.0.0.1:80:80 -p 127.0.0.1:443:443` if public exposure is not intended. The first user
to sign up is made staff (`is_staff=not User.objects.exists()`), and new signups are allowed by default
(`allow_new_signups` defaults to `True`). Sign up first, then turn off new signups in the admin
settings; a refused signup then fails with "Sign up is disabled."

The Compose file refuses to start without `SECRET_KEY`, `DATABASE_PASSWORD` and `REDIS_PASSWORD`
(`${SECRET_KEY:?}`), and `.env.example` leaves them empty rather than shipping examples, so the secrets
are yours to generate. Baserow's core registers a TOTP two-factor authentication provider.

## Appsmith

Appsmith's Java server binds to `127.0.0.1` on 8080 by default (`APPSMITH_SERVER_ADDRESS`), inside a
container fronted by a bundled Caddy on port 80. The vendor's development Compose file publishes that
on host port 8080, and its AWS example on 80 and 443. Signup is enabled by default
(`APPSMITH_SIGNUP_DISABLED` defaults to `false`). On a fresh instance, the first user to sign up claims
the super-user slot while no users exist. Claim it before exposing the instance, then set
`APPSMITH_SIGNUP_DISABLED=true` or restrict signup with `APPSMITH_SIGNUP_ALLOWED_DOMAINS`; a refused
signup gets the `SIGNUP_DISABLED` error, "Signup is restricted on this instance of Appsmith".

Datasource credentials are encrypted with `APPSMITH_ENCRYPTION_PASSWORD` and
`APPSMITH_ENCRYPTION_SALT`. On first start, the image's entrypoint generates random 13-character values
for both. But the vendor's development Compose file sets both to `abcd`, and values passed from outside
override the generated ones. Anyone who copies that file encrypts every stored datasource credential
with a published key. Remove those two lines, or set long random values, before the first start. On an
instance that already stored credentials under `abcd`, changing the pair presumably leaves them
unreadable, so plan to re-enter them (inferred from the encryption design, not tested).

## Budibase

Budibase's Compose file publishes its nginx proxy on `MAIN_PORT` (10000 in the sample `.env`) and its
LiteLLM service on `${LITELLM_PORT:-4000}`. The proxy forwards `/db/` to CouchDB. The sample
`hosting/.env` sets `JWT_SECRET` and `API_ENCRYPTION_KEY` to `testsecret`, and the CouchDB, MinIO and
Redis passwords, `INTERNAL_API_KEY` and `LITELLM_MASTER_KEY` to `budibase`, under a comment that says
"These should be updated". A search of the v3.46.0 source finds `testsecret` only in those sample files,
a DigitalOcean first-boot script, a test setup and a development script, and no code that checks for
it. With the sample file unchanged,
anyone who can reach the proxy can try `budibase`/`budibase` against CouchDB through `/db/`, and the
LiteLLM port answers to the master key `budibase`. Replace every one of those values before the first
start.

The first-run admin route `POST /api/global/users/init` needs no login and works until the first user
exists; after that it returns an error ("You cannot initialise once an global user has been created").
The route validates its request body before that check, so no read-only request shows whether an
instance is claimed. Create the admin first, or seed it with `BB_ADMIN_USER_EMAIL` and
`BB_ADMIN_USER_PASSWORD`.

## Windmill

Windmill runs scripts in Python, TypeScript, Go, Bash and more on its workers, so a Windmill login is
code execution on your worker hosts. The server listens on port 8000 on every interface by default
(`DEFAULT_SERVER_BIND_ADDR` is `0.0.0.0`; `SERVER_BIND_ADDR` changes it when you run the binary). In the
vendor's Compose file the server only `expose`s 8000 to the Compose network, and the bundled Caddy
publishes `80:80` and `25:25` on every host interface, so port 80 is where the login page is reachable.
A fresh database has one password user, `admin@windmill.dev`, a super admin whose password is
`changeme`; the README gives them as the default credentials.

On a v1.817.0 loopback run of the release binary with `SERVER_BIND_ADDR=127.0.0.1`, that was the only
password user in the fresh database, and it was a super admin. Logging in with `changeme` returned `200`
and a token, and `whoami` confirmed super-admin rights. After the password was changed, `changeme` got
`400` and the new password `200`. The server's only listener was on 127.0.0.1, at the test port the run
set. Change the password before anything else can reach the server. In Compose, bind Caddy's `ports:`
entries to `127.0.0.1` or a private address ([docker.md](docker.md)); `SERVER_BIND_ADDR=127.0.0.1` inside the
server container would presumably cut Caddy off from it (inferred, not tested).

The worker sandbox is not on by default either. `DISABLE_NSJAIL` defaults to `true` in the worker, and
on the loopback run, without nsjail installed, the worker logged "Nsjail sandboxing will NOT be
available". The vendor's Compose file runs the worker with `privileged: true` and publishes port 25 for
email triggers. Its debugger setting carries the vendor's warning: `REQUIRE_SIGNED_DEBUG_REQUESTS`
"Do NOT set to false on any internet-reachable deployment: it exposes an unauthenticated code-execution
debugger". Do not publish 25 unless you use email triggers.

## Verify

Three checks here were demonstrated: the sample-values check, the Windmill default-login pair, and the
TCP reachability probe's three outcomes. Everything else is reasoned. NocoDB 2026.09.0, Baserow,
Appsmith and Budibase ship for production as container images and the authoring host has no container
runtime. NocoDB also cannot run here outside a container: its server calls `listen` with no host, so it
can only bind every interface, which the host forbids; the same applies to Windmill's default bind.
Backlog row 1.109 tracks demonstrating the rest.

On the host, list the listeners, then read Docker's own publications, because a port published through
Docker's NAT may have no host socket at all, so absence from `ss` is not proof of isolation:

```bash
sudo ss -tlnp   # 8080 (NocoDB; Appsmith dev Compose), 80/443 (Baserow, Windmill Caddy), 10000 and 4000 (Budibase), 8000 and 25 (Windmill): loopback or private only
docker ps --format '{{.Names}}\t{{.Ports}}'   # every "0.0.0.0:" or ":::" publication is reachable from outside
```

Exposed, the reasoned expectation is a wildcard address, on the host or in a Docker publication, for any
of those ports; fixed means a loopback or private address only.

Check each environment and Compose file the deployment uses for the vendor sample values: run the block
once per file, including every file an `env_file:` line names. Substitute the file path inside the
single quotes (a path containing an apostrophe needs other quoting), and paste the whole block.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ENV_OR_COMPOSE_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not checking"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not checking"; exit; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute your file on the set -- line above; not checking"; exit ;; esac
  { [ -f "$1" ] && [ -r "$1" ]; } || { echo "cannot read $1 as a regular file; not checked"; exit; }
  grep -n -E '(^|[^A-Za-z0-9_])(testsecret|budibase|abcd|changeme|569a1821-0a93-45e8-87ab-eb857f20a010)([^A-Za-z0-9_]|$)' -- "$1"
  case "$?" in
    0) echo "FOUND vendor sample tokens: inspect each line above; replace every secret still set to one" ;;
    1) echo "no vendor sample tokens found" ;;
    *) echo "grep could not read $1; not checked" ;;
  esac
  if grep -q -E '^[[:space:]-]*NC_[A-Z_]+[[:space:]]*[:=]' -- "$1"; then
    if grep -q -E "^[[:space:]-]*NC_CONNECTION_ENCRYPT_KEY[[:space:]]*[:=][[:space:]]*[\"']?[^\"'[:space:]#]" -- "$1"; then
      echo "NC_CONNECTION_ENCRYPT_KEY is set to a non-empty value"
    else
      echo "NocoDB settings without an active, non-empty NC_CONNECTION_ENCRYPT_KEY: stored database credentials will be plaintext"
    fi
  fi
)
```

The search matches each sample value as a whole token wherever it appears, so it cannot report a file
clean while one of them is still in it; the cost is that it also reports harmless lines such as `image:
budibase/apps`, so inspect each hit. This was demonstrated. On Budibase's sample `hosting/.env` it
reported all eleven sample lines, on Appsmith's development Compose file the two `abcd` lines, and on
Windmill's Compose file its `changeme` Postgres password. It also reported Compose defaults
(`${JWT_SECRET:-testsecret}`), flow mappings and lists (`{COUCH_DB_PASSWORD: budibase, X: 1}`),
URL parameters (`&password=changeme&`) and trailing punctuation. On NocoDB's sample `docker.env` it
reported the missing encryption key, and it did the same for an empty, quoted-empty, commented-out or
comment-only key, while a real key printed "is set". On copies with the values replaced it printed "no
vendor sample tokens found", and on an unreadable path it reported that it did not check.

For Windmill, check whether the default login still works. The password below is the vendor's
published default, not a secret, so it is fine in the request body. Substitute the base URL (for
example the Caddy address on port 80) inside the single quotes.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_WINDMILL_BASE_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the base URL on the set -- line above; not probing" ;;
    *) printf '%s' '{"email":"admin@windmill.dev","password":"changeme"}' |
         curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 15 \
           -H 'Content-Type: application/json' --data-binary @- \
           -w 'default login: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1/api/auth/login" ;;
  esac
)
```

Exposed, the default login gets `200` with a token; fixed, it gets `400` (both observed with this block
on the loopback run). Before trusting a `400`, log in once with your real credentials, so that a dead
service is not read as fixed.

For Budibase, two reasoned requests use the published sample values, which are not secrets. Substitute
the proxy URL (`http://HOST:10000` in the sample setup) and the LiteLLM URL inside the single quotes.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_BUDIBASE_PROXY_URL' 'REPLACE_WITH_LITELLM_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1|$2" in
    *REPLACE_WITH_*|"|"*|*"|"|*[[:cntrl:]]*) echo "substitute both URLs on the set -- line above; not probing" ;;
    *) printf 'user = "budibase:budibase"\n' | curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 \
         --max-time 15 --config - -w 'couchdb sample login: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
         "$1/db/_session?basic=true"
       printf 'Authorization: Bearer budibase\n' | curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 \
         --max-time 15 -H @- -w 'litellm sample key: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
         "$2/v1/models" ;;
  esac
)
```

Exposed, either line gets `200`, which means the sample secret is live. Fixed, the CouchDB sample login
gets `401` ("Username or password wasn't recognized", per CouchDB's `/_session` reference) and the
LiteLLM sample key gets `401` (the `/v1/models` comparison in [litellm.md](litellm.md)). Confirm each
service answers your real credentials as the positive control. Budibase's first-run admin route has no
equivalent probe: its request validation runs before the "already initialised" check, so a request
either fails validation in both states or, with a valid body on a fresh instance, creates the admin.
Claim the admin yourself before the proxy is reachable.

For NocoDB, Baserow and Appsmith, check signup by hand, reasoned from source. In a private browser
window, open the instance's sign-up page and try to create an account with an address you control.
Exposed: the account is created, or, on a fresh instance, you become its administrator. Fixed: the
signup is refused. The backends' refusal messages are NocoDB's "Not allowed to signup, contact super
admin.", Baserow's "Sign up is disabled." and Appsmith's `SIGNUP_DISABLED` error ("Signup is restricted
on this instance of Appsmith"); the web UIs may word them differently or hide the sign-up link, which
also counts as refused. Delete any test account the exposed state let you create, then sign in as your
admin as the positive control.

Finally, from a host that should not have access, try a TCP connection to each published port. The
block uses bash's `/dev/tcp`, so it works for SMTP on 25 as well as the web ports. Substitute the
address inside the single quotes.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_THE_SERVICE_ADDRESS'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|""|*[[:cntrl:]]*|*/*) echo "substitute a bare address on the set -- line above; not probing"; exit ;; esac
  for p in 80 443 8080 10000 4000 8000 25; do
    # shellcheck disable=SC2016  # the single-quoted script is meant to expand $1 and $2 in the child shell
    timeout 5 bash -c ': > "/dev/tcp/$1/$2"' probe "$1" "$p" 2>/dev/null
    case "$?" in
      0) echo "$1:$p connected: reachable" ;;
      124) echo "$1:$p timed out: filtered, or nothing answered" ;;
      *) echo "$1:$p refused or failed" ;;
    esac
  done
)
```

Exposed, a port reports "connected". Fixed, it reports "refused" or "timed out"; a cloud firewall that
drops packets produces the timeout. On a loopback test, an open port printed "connected", a closed one
"refused", and an unroutable test address "timed out". A "connected" on a port you did not mean to
publish is the finding.

## Sources (checked September 2026)

- NocoDB 2026.09.0 port default, JWT secret generation and proxy-trust reset: https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/Noco.ts
- NocoDB 2026.09.0 proxy trust default (`NC_TRUST_PROXY`): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/trustProxy.ts
- NocoDB 2026.09.0 entry point (listen with no host, CORS): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/run/dockerEntry.ts
- NocoDB 2026.09.0 first user, signup and its refusal message: https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/services/users/users.service.ts
- NocoDB 2026.09.0 app settings (`invite_only_signup`): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/interface/AppSettings.ts
- NocoDB 2026.09.0 admin from environment (`NC_ADMIN_EMAIL`, `NC_ADMIN_PASSWORD`): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/helpers/initAdminFromEnv.ts
- NocoDB 2026.09.0 credential encryption: https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/encryptDecrypt.ts and https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/helpers/initDataSourceEncryption.ts
- NocoDB 2026.09.0 README (Docker example JWT secret, binaries note): https://github.com/nocodb/nocodb/blob/2026.09.0/README.md
- NocoDB 2026.09.0 sample environment without an encryption key: https://github.com/nocodb/nocodb/blob/2026.09.0/docker-compose/examples/external-postgres-and-redis/docker.env
- Node.js v22 `server.listen` with an omitted host: https://github.com/nodejs/node/blob/v22.22.1/doc/api/net.md
- Baserow 2.3.4 Compose file: https://github.com/baserow/baserow/blob/2.3.4/docker-compose.yml
- Baserow 2.3.4 install with Docker (ufw warning): https://github.com/baserow/baserow/blob/2.3.4/docs/installation/install-with-docker.md
- Baserow 2.3.4 first user, signup and its refusal message: https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/core/user/handler.py
- Baserow 2.3.4 settings model (`allow_new_signups`): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/core/models.py
- Baserow 2.3.4 TOTP provider registration: https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/core/apps.py
- Baserow 2.3.4 sample environment: https://github.com/baserow/baserow/blob/2.3.4/.env.example
- Appsmith v2.4.1 server properties (bind address, signup): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/resources/application-ce.properties
- Appsmith v2.4.1 first super user: https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/solutions/ce/UserSignupCEImpl.java
- Appsmith v2.4.1 `SIGNUP_DISABLED` error: https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/exceptions/AppsmithError.java
- Appsmith v2.4.1 image entrypoint (generated encryption values): https://github.com/appsmithorg/appsmith/blob/v2.4.1/deploy/docker/fs/opt/appsmith/entrypoint.sh
- Appsmith v2.4.1 development Compose file: https://github.com/appsmithorg/appsmith/blob/v2.4.1/deploy/docker/docker-compose.yml
- Appsmith v2.4.1 AWS Compose example: https://github.com/appsmithorg/appsmith/blob/v2.4.1/deploy/aws_ami/docker-compose.yml
- Budibase v3.46.0 sample environment: https://github.com/Budibase/budibase/blob/v3.46.0/hosting/.env
- Budibase v3.46.0 Compose file: https://github.com/Budibase/budibase/blob/v3.46.0/hosting/docker-compose.yaml
- Budibase v3.46.0 proxy configuration (`/db/`): https://github.com/Budibase/budibase/blob/v3.46.0/hosting/proxy/nginx.prod.conf
- Budibase v3.46.0 public worker routes: https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/index.ts
- Budibase v3.46.0 admin init: https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/controllers/global/users.ts
- Budibase v3.46.0 admin init route and its validation: https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/routes/global/users.ts
- Apache CouchDB 3.5.2 `/_session` reference: https://github.com/apache/couchdb/blob/3.5.2/src/docs/src/api/server/authn.rst
- Windmill v1.817.0 README (default credentials): https://github.com/windmill-labs/windmill/blob/v1.817.0/README.md
- Windmill v1.817.0 server defaults: https://github.com/windmill-labs/windmill/blob/v1.817.0/backend/src/main.rs
- Windmill v1.817.0 worker (`DISABLE_NSJAIL`): https://github.com/windmill-labs/windmill/blob/v1.817.0/backend/windmill-worker/src/worker.rs
- Windmill v1.817.0 Compose file: https://github.com/windmill-labs/windmill/blob/v1.817.0/docker-compose.yml
- Windmill v1.817.0 seeded-user migrations: https://github.com/windmill-labs/windmill/blob/v1.817.0/backend/migrations/20220123221903_first.up.sql and https://github.com/windmill-labs/windmill/blob/v1.817.0/backend/migrations/20220816185849_remove_non_admin_users.up.sql
