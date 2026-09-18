# Workflow and agent orchestrators: Prefect, Dagster, Airflow, Temporal, Flower

These webservers and UIs schedule and trigger arbitrary code execution across your infrastructure, and most
ship with no authentication at all. Keep every one of them off the public internet and add auth before
anyone but you can reach the port. The same baseline applies across all of them: keep each UI and API origin on
loopback or a restricted private network, require HTTPS and an authenticating reverse proxy with MFA at the
identity provider for browser access, and protect the API routes as well as the HTML ones, configuring
machine-client authentication separately from interactive MFA ([fronting-auth.md](fronting-auth.md),
[mfa.md](mfa.md), [docker.md](docker.md)). Because each of these executes arbitrary tasks, also restrict every
worker's and task's egress to the destinations it needs and deny cloud metadata and unrelated internal
services; inbound authentication does not constrain what an executing workload reaches outward
([egress-metadata.md](egress-metadata.md)).

## Prefect (self-hosted server)

There is no default authentication; `prefect server start` accepts unauthenticated API calls until you set
one up. Built-in Basic Auth requires Prefect 3.1.8 or newer. It uses a single administrator/password string, set on the server with
`PREFECT_SERVER_API_AUTH_STRING` (or the `server.api.auth_string` setting) and the identical value on every
client with `PREFECT_API_AUTH_STRING` (`api.auth_string`); the UI prompts for the string on first load. This
is unrelated to Prefect Cloud: `PREFECT_API_KEY` authenticates only to Prefect Cloud, and if it happens to be
set alongside `PREFECT_API_AUTH_STRING` on a client talking to a self-hosted server, the key takes precedence
and the request fails with 401. Store the auth string in a secret manager or a private `.env` file, never in
the repository ([secrets.md](secrets.md)). Treat access to the server API as access to credential-bearing Blocks
and workflow controls: a block-document request can ask for stored secret values, and UI masking is not an
authorization boundary, so keep credentials out of flow parameters and logs and give each worker its own
narrowly scoped credentials.

## Dagster (OSS)

The open-source `dagster-webserver` (default port 3000; `dagster dev` binds it to `127.0.0.1`) ships no
built-in login or access control: the inspected open-source webserver applies no authenticating middleware.
Put it entirely behind an identity-aware fronting layer ([fronting-auth.md](fronting-auth.md)) or your own
reverse proxy with its own authentication ([nginx.md](nginx.md), [caddy.md](caddy.md)) plus MFA
([mfa.md](mfa.md)); for a proxy on the same host, bind the webserver explicitly with
`dagster-webserver --host 127.0.0.1 --port 3000`, and never publish the port directly.

## Apache Airflow

Airflow's own security model states it plainly: "Airflow doesn't support unauthenticated users by default"
and "Airflow is not designed to be exposed to untrusted users on the public internet"; every user of the UI
and API is assumed to be authenticated and known, and keeping it off the public internet is the deployment
manager's responsibility, not something the software enforces for you. The guidance below targets Airflow 3
(checked against 3.3.2 with FAB provider 3.9.0); earlier releases differ, so confirm your version. Airflow 2.11.0 governs API authentication through `[api] auth_backends`, defaulting to
`airflow.api.auth.backend.session`. Before 2.3 the setting was singular `auth_backend`; in 2.2.5 its default was
`airflow.api.auth.backend.deny_all`. Airflow 3's public API uses JWT independently of FAB's `[fab] auth_backends`.
Access is governed by a pluggable "auth manager". The default is the Simple Auth Manager, which the documentation marks for development and
testing only: it prints a warning banner on login, and its users and roles (`viewer`, `user`, `op`, `admin`)
come from `simple_auth_manager_users` in `[core]` (for example `bob:admin,peter:viewer`), with a password
auto-generated per user and printed to the webserver logs unless you set your own. For production, configure
the FAB auth manager instead: install the FAB provider, then set `[core] auth_manager` to
`airflow.providers.fab.auth_manager.fab_auth_manager.FabAuthManager` and confirm the effective manager with
`airflow config get-value core auth_manager`. `[fab] auth_backends` is a different setting that selects the
authentication backends for the FAB API, not the auth manager. Point FAB at LDAP, OAuth, or another real identity backend,
and put MFA at that identity provider ([mfa.md](mfa.md), [identity-providers.md](identity-providers.md)). Keep
`[core] simple_auth_manager_all_admins` unset or `False`, since setting it disables login and treats every
visitor as an admin, and with FAB leave `AUTH_ROLE_PUBLIC` unset in `webserver_config.py`, since setting it
(for example to `Admin`) grants unauthenticated visitors that role; check the effective configuration and
anonymous API behavior after deployment.

The official `docker-compose.yaml` takes the right first step and the wrong second one: it selects the FAB
auth manager, then seeds it with a known admin, `_AIRFLOW_WWW_USER_USERNAME` and `_AIRFLOW_WWW_USER_PASSWORD`
both defaulting to `airflow`, and gives the API a fallback signing secret, `AIRFLOW__API_AUTH__JWT_SECRET`
defaulting to `airflow_jwt_secret`, used whenever that variable is unset. Its header marks it
local-development only, but it is the quickstart the docs give for a local run, so a reader who brings it up
unchanged gets an `airflow`/`airflow` admin login exposed wherever port 8080 is reachable, and a
token-signing secret published in the vendor's file, which lets anyone forge an API token and impersonate an
existing user. Set the admin username and password before the first start creates the account (changing them
afterward does not reset the account already created, so update or delete that account instead), set your own
`AIRFLOW__API_AUTH__JWT_SECRET` (`openssl rand -hex 32`) and give it to every component that signs or
validates tokens. That is separate from the web and API signing secret `secret_key` (`[webserver] secret_key`
on 2.11.0, `[api] secret_key` on 3.3.2): provision a strong value for it too, because securing one does not
secure the other. Keep configuration exposure off as well (`AIRFLOW__WEBSERVER__EXPOSE_CONFIG=False` on 2.11.0,
`AIRFLOW__API__EXPOSE_CONFIG=False` on 3.3.2). An exposed Airflow is also a credential store: its Connections
and Variables hold credentials for the systems your DAGs reach, protected at rest by the `[core] fernet_key`
(an effectively empty key disables encryption for newly stored values; normal initialization generates a key,
and removing an existing key prevents decryption of existing ciphertext), so restrict permissions on Connections and
Variables and protect the metadata database, the Fernet key, and any secrets backend, since encryption at rest
and UI masking do not stop an authorized workload from using them. Keep every secret out of the repository
([secrets.md](secrets.md)), and publish 8080 to loopback for the proxy (`127.0.0.1:8080:8080`) rather than to
every interface, behind your fronting layer.

## Temporal (self-hosted)

With no authorizer configured, the server runs the default `noopAuthorizer`, which the documentation says
"allows every API request, with no authentication or access control" at all, including administrative
operations. Configure both an `Authorizer` and a `ClaimMapper`: leaving either selector empty selects a no-op, and the
no-op claim mapper grants system-admin claims, so both matter. For the built-in JWT implementation set
`global.authorization.authorizer: default`, `global.authorization.claimMapper: default`, and a trusted
`global.authorization.jwtKeyProvider.keySourceURIs` (the programmatic equivalents are `temporal.WithAuthorizer()`
and `temporal.WithClaimMapper()`), with the required audience and frontend TLS configured, so protected workflow API
calls require sufficient mapped claims. The built-in default authorizer permits health-check APIs without claims. This is entirely separate from Web
UI login: the UI's own config reference documents an `auth` block whose `enabled` flag turns UI login on and
whose `providers` list carries each OIDC entry (`type: oidc`, `providerUrl`, `issuerUrl`, `clientId`,
`clientSecret`, `callbackUrl`, `scopes`) for SSO into the dashboard. `enabled` is a sibling of `providers`, not
a field inside a provider entry, and with environment configuration it is `TEMPORAL_AUTH_ENABLED=true` alongside
the `TEMPORAL_AUTH_*` provider settings. That only gates the UI, not the server API a worker or CLI talks to
directly. mTLS secures
internode and frontend traffic separately again. Set up both layers; MFA comes from whichever identity
provider the UI's OIDC settings point at. Temporal also
persists workflow inputs, results, and history, so keep plaintext credentials out of them and fetch operational
secrets inside authorized workers; if you encrypt payloads with a Payload Codec, authenticate and restrict any
Codec Server independently of the UI and the frontend, because an exposed Codec Server can decode that data.

## Flower (for Celery)

Flower binds every interface by default (`--address` is empty, meaning all interfaces; `--port` defaults to
5555) with authentication disabled unless you configure it. When no authentication is configured its HTTP API
is disabled unless you set `FLOWER_UNAUTHENTICATED_API=true`, so keep that unset and never read an API
rejection as proof the dashboard itself is protected. `--basic-auth="user1:password1,user2:password2"`
turns on HTTP Basic Auth with a comma-separated credential list; OAuth 2.0 login against Google, GitHub,
GitLab, or Okta is enabled by setting `--auth_provider` to the provider's handler class plus `--oauth2_key`,
`--oauth2_secret`, `--oauth2_redirect_uri`, and an `--auth` regular expression of the email addresses allowed
to sign in. Supply the Basic Auth credential list through `FLOWER_BASIC_AUTH` and the OAuth client secret through
`FLOWER_OAUTH2_SECRET`, or set `basic_auth` and `oauth2_secret` in a protected configuration file, rather than on
the command line where they are readable in the process list ([secrets.md](secrets.md)). Prefer OAuth against a provider that enforces MFA over Basic Auth alone
([mfa.md](mfa.md)), and bind `--address=127.0.0.1` behind a proxy rather than relying on Basic Auth as the only
control.

## Verify

These probes are reasoned, not demonstrated: the authoring environment has no container runtime, so no live
orchestrator was stood up in its exposed or fixed state. Each names its expected exposed and fixed result so it
discriminates against a live instance; backlog row 2.34 tracks demonstrating them across all five tools. The
`*.internal` hostnames are examples for a reachable vantage (you have not isolated the port yet, or you are on
an allowed network); substitute your own. For every negative check run the matched authorized call against the
SAME origin, and separately probe the origin directly from an untrusted vantage with the guarded block at the
end, because a rejection seen only through a proxy does not prove the origin enforces anything. The write-out
fields need curl 7.75.0 or newer; never use `-k`.

```bash
ss -tlnp   # TCP listeners in THIS network namespace only (4200/3000/8080/7233/8233/5555): not a firewall,
           # publication, routing, or auth check. Inspect container publications and probe external
           # reachability separately; a wildcard bind is a prompt to investigate, not proof of exposure

# Prefect: an empty JSON filter. Once the auth string is set the anonymous call is 401 and the authorized call
# returns a JSON flow list; an anonymous list, even an empty one, is the finding. Feed the auth string on stdin.
# Do NOT use /api/health or /api/ready as the authentication discriminator. Current server source exempts
# those GET paths; this behavior is version-dependent and was not present in 3.1.8.
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
  -w '\nprefect-anon http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
  -H 'Content-Type: application/json' -X POST --data-binary '{}' http://prefect.internal:4200/api/flows/filter
python3 -c 'import base64,getpass; print("header = \"Authorization: Basic " + base64.b64encode(getpass.getpass("Prefect username:password: ").encode()).decode() + "\"")' \
  | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 --config - \
      -w '\nprefect-auth http=%{http_code} exit=%{exitcode}\n' \
      -H 'Content-Type: application/json' -X POST --data-binary '{}' http://prefect.internal:4200/api/flows/filter

# Dagster has no login of its own, so test /graphql, which can read configuration and launch runs.
# A RepositoryConnection containing nodes (including an empty nodes list) is a successful read.
# PythonError, top-level GraphQL errors, and transport failures are inconclusive.
# Test the proxy separately: send this identical query anonymously and authenticated to the SAME proxy URL.
# Test origin reachability independently; proxy authentication does not authenticate the OSS origin.
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
  -w '\ndagster-anon http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
  -H 'Content-Type: application/json' -X POST \
  --data-binary '{"query":"{ repositoriesOrError { __typename ... on RepositoryConnection { nodes { name location { name } } } } }"}' http://dagster.internal:3000/graphql

# Airflow: obtaining a token from the documented Compose account is the finding. Send the credentials as JSON
# on stdin; FAB 3.9.0 returns 201 Created with a nonempty access_token when airflow/airflow works. Compare with a valid account on
# the same route, and test an API read with no token then a token at the proxy and the origin. On Airflow 2 use
# its /api/v1/ endpoint and its own auth mechanism instead.
printf '{"username":"%s","password":"%s"}' 'airflow' 'airflow' \
  | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
      -w '\nairflow-token http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
      -H 'Content-Type: application/json' --data-binary @- https://airflow.example.com/auth/token
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
  -w '\nairflow-pools-anon http=%{http_code} exit=%{exitcode}\n' https://airflow.example.com/api/v2/pools

# Temporal: a protected read against the frontend gRPC port. With an Authorizer and ClaimMapper configured this
# is rejected without credentials (an mTLS deployment refuses the connection outright); a listing, even an empty
# one, is the finding. Health checks, TLS errors, missing namespaces, and unavailable services do not prove
# authorization, so use a real workflow list, not a health call, and run it with no ambient credentials set.
temporal workflow list --address temporal.internal:7233 --namespace default --limit 1

# Flower: the dashboard and the API. With Basic Auth an anonymous request is 401; with OAuth it is a 302 redirect into
# the login flow, not 401, so inspect the redirect without following it and confirm access with a
# valid session. An anonymous worker list from /api/workers is the finding; an API-disabled response does not
# prove the dashboard is protected.
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 --dump-header - \
  -w '\nflower-ui http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' http://flower.internal:5555/
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 --dump-header - \
  -w '\nflower-api http=%{http_code} exit=%{exitcode}\n' http://flower.internal:5555/api/workers

# Direct-origin reachability from an UNTRUSTED vantage (run from OUTSIDE your network). Paste the whole block and
# substitute your origin URL inside the quotes; any HTTP response means the origin is published and is itself the
# finding, whatever a fronting proxy does. First confirm this SAME origin URL responds from an allowed
# vantage, then probe it from the untrusted vantage. DNS, TLS, connection errors, and timeouts remain
# inconclusive. A responding public proxy is only a separate connectivity check.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ORIGIN_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute your origin URL on the set -- line above; not probing"; exit 2 ;;
    http://*|https://*) ;;
    *) echo "give an http:// or https:// URL; not probing"; exit 2 ;;
  esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 -o /dev/null \
    -w 'origin http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
)
```

A DAG list, flow run, task graph, repository, or worker pool that renders without a credential is a finding; so
is a Temporal Service that answers `temporal workflow list` with no claim behind it, since the UI login does not
cover the frontend gRPC path.

## Common mistakes

- Assuming Airflow's Simple Auth Manager, meant for development, is acceptable in production because it
  technically requires a password.
- Configuring Temporal's UI SSO and believing the server API is now protected too; they are independent.
- Setting `PREFECT_API_KEY` on a client that should be using `PREFECT_API_AUTH_STRING` against a self-hosted
  server, then debugging the resulting 401 as a server problem.
- Publishing Flower's `5555` or Dagster's `3000` straight to the internet "for the team" with no proxy.
- Storing credentials in Airflow Connections and Variables, Prefect Blocks, or Temporal payloads without
  restricting who can retrieve or use them. UI masking and database encryption do not enforce caller
  authorization. Temporal client-side payload encryption adds a separate boundary: decoding requires the key or
  access to an authorized Codec Server.

## Sources (checked September 2026)

These defaults are checked against Prefect 3.1.8+ for Basic Auth, Dagster 1.13.x, Apache Airflow 3.3.2 with FAB provider 3.9.0 (Airflow 2.11.0 noted where the configuration paths differ), Temporal Server 1.28.x and UI Server 2.34.x, and Flower 2.2.0; confirm your own versions, since several of these settings moved between releases.

- Prefect, security settings (`PREFECT_SERVER_API_AUTH_STRING`, `PREFECT_API_AUTH_STRING`, Cloud API keys
  taking precedence and causing 401): https://docs.prefect.io/v3/advanced/security-settings
- Prefect, self-hosted server (default port 4200): https://docs.prefect.io/v3/how-to-guides/self-hosted/server-cli
- Dagster, webserver and UI (default local port, no documented built-in auth): https://docs.dagster.io/guides/operate/webserver
- Apache Airflow, security overview: https://airflow.apache.org/docs/apache-airflow/stable/security/
- Apache Airflow, auth manager selection (`[core] auth_manager`, `airflow config get-value core auth_manager`): https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/auth-manager/index.html
- Apache Airflow FAB provider, API authentication (`[fab] auth_backends`, independent of the auth manager): https://airflow.apache.org/docs/apache-airflow-providers-fab/stable/auth-manager/api-authentication.html
- Prefect server source (health and ready paths exempted from the auth string on GET): https://github.com/PrefectHQ/prefect/blob/main/src/prefect/server/api/server.py
- Apache Airflow, quickstart (default port 8080): https://airflow.apache.org/docs/apache-airflow/stable/start.html
- Apache Airflow, running Airflow in Docker (the `docker-compose.yaml` default `airflow`/`airflow` web user via `_AIRFLOW_WWW_USER_*`, `AIRFLOW__API_AUTH__JWT_SECRET` default `airflow_jwt_secret`, FAB auth manager, port 8080 published on all interfaces, "for local development. Do not use it in a production deployment"; checked 2026-09-14): https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html
- Apache Airflow, security model ("doesn't support unauthenticated users", "not designed to be exposed... to
  untrusted users on the public internet"): https://airflow.apache.org/docs/apache-airflow/stable/security/security_model.html
- Apache Airflow, Simple auth manager (default, dev/test only, `simple_auth_manager_users`, generated
  passwords): https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/auth-manager/simple/index.html
- Temporal, self-hosted security (`noopAuthorizer` default, `Authorizer`, `ClaimMapper`): https://docs.temporal.io/self-hosted-guide/security
- Temporal, Web UI configuration reference (`auth.providers`, `enabled`, `type: oidc`, `providerUrl`,
  `clientId`, `clientSecret`, `callbackUrl`, `scopes`): https://docs.temporal.io/references/web-ui-configuration
- Temporal, CLI server reference (default frontend gRPC port 7233, Web UI port 8233): https://docs.temporal.io/cli/command-reference/server
- Flower, configuration (`--address`, `--port` 5555 default, `--basic-auth`, `--auth_provider`, `--oauth2_key`,
  `--oauth2_secret`, `--oauth2_redirect_uri`, `--auth`): https://flower.readthedocs.io/en/latest/config.html
