# Workflow and agent orchestrators: Prefect, Dagster, Airflow, Temporal, Flower, Argo

Prefect, Dagster, Airflow, Temporal, Flower and Argo Workflows schedule, run or monitor jobs and pipelines, and their consoles and APIs can start code on workers. This guide helps your AI assistant configure each securely, including no public UI or API, MFA for people, separate machine-client credentials, and limited worker egress.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/workflow-orchestrators.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against Prefect Basic Auth minimum 3.1.8, Dagster OSS 1.13.24, Apache Airflow 3.3.2, Temporal Go SDK codec source v1.28.0, Flower v2.2.0, Argo Workflows v3.7.18 and v4.1.4, Prefect Blocks source 3.1.8, and Apache Airflow historical configuration 2.11.0, plus 10 more recorded bases; 1 further source is pinned to a commit and 7 carry no recorded version. Metadata reviewed 2026-10-05; documentation checked October 2026. The guide records 62 claims: 3 demonstrated by a check that ran and 59 reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

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
and workflow controls: Prefect 3.1.8 block-document read routes accept `include_secrets`, and
`Secret.get()` returns the underlying value. These source files do not establish per-caller authorization
for `include_secrets`; restrict API and worker access, and keep credentials out of flow parameters and logs.

## Dagster (OSS)

The open-source `dagster-webserver` (as of 1.13.24, run directly or by `dagster dev`) binds `127.0.0.1` on port
3000 unless a flag or an environment variable sets the host or a nonzero port, and with no port set either way, or a port
of 0, it moves to a free port when 3000 is taken. The official Helm chart (as of 1.13.24) always passes `-h 0.0.0.0`,
on the Service port, 80 by default, behind a Service of type `ClusterIP` by default. The open-source
`dagster-webserver` ships no built-in login or access control: the inspected open-source webserver applies no
authenticating middleware.
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
visitor as an admin, and with FAB leave `[fab] auth_role_public` and legacy `AUTH_ROLE_PUBLIC` in `webserver_config.py` unset.
A configured public role can make the FAB logged-in check pass for an anonymous visitor and can supply that
role's permissions; check the effective configuration and anonymous API behavior after deployment.

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
and Variables hold credentials for the systems your DAGs reach, protected at rest by the `[core] fernet_key`, so
restrict permissions on Connections and Variables and protect the metadata database, the Fernet key, and any
secrets backend, since encryption at rest and UI masking do not stop an authorized workload from using them. An
empty `[core] fernet_key` selects `_NullFernet`, which does not encrypt newly stored values; configured
comma-separated keys use `MultiFernet`; preserve keys needed to decrypt existing ciphertext. Keep every secret out of the repository
([secrets.md](secrets.md)), and publish 8080 to loopback for the proxy (`127.0.0.1:8080:8080`) rather than to
every interface, behind your fronting layer.

## Temporal (self-hosted)

With no authorizer configured, the server runs the default `noopAuthorizer`, which the documentation says
"allows every API request, with no authentication or access control" at all, including administrative
operations. Configure both an `Authorizer` and a `ClaimMapper`: leaving either selector empty selects a no-op, and the
no-op claim mapper grants system-admin claims, so both matter. For the built-in JWT implementation set
`global.authorization.authorizer: default`, `global.authorization.claimMapper: default`, and a trusted
`global.authorization.jwtKeyProvider.keySourceURIs`, with the required audience and frontend TLS configured, so
protected workflow API calls require sufficient mapped claims. The programmatic equivalents for the built-in JWT
implementation are `temporal.WithAuthorizer()` and `temporal.WithClaimMapper()`. The built-in default authorizer permits health-check APIs without claims. This is entirely separate from Web
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
Codec Server independently of the UI and the frontend. The Temporal Go SDK v1.28.0 codec HTTP handler
accepts encode/decode POSTs without an authentication check; a deployed server needs its own access control.

## Flower (for Celery)

Flower binds every interface by default (as of v2.2.0, `--address` is empty, meaning all interfaces, and `--port`
defaults to 5555, unless `--unix_socket` names a socket path, `FLOWER_`-prefixed environment variables set them, or
a `flowerconfig.py` in the working directory, which it loads without being asked, does) with authentication disabled
unless you configure it. When no
authentication is configured its HTTP API
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

With `--unix_socket` set to a filesystem path, Flower v2.2.0 passes Tornado a fixed mode, `0o777`, for the socket
file: each start deletes any socket left at that path, creates a new one and applies that mode, so a `chmod` of the
socket is undone at the next start. On Linux, connecting needs write permission on the socket and search permission
on every directory in its path, so the socket's mode lets any unprivileged local account that can search the
directory connect. A Linux process whose effective `CAP_DAC_OVERRIDE` or `CAP_DAC_READ_SEARCH` applies to the
directories bypasses the search check: root on the host does, and so does root in a container that shares the
host's user namespace, since Docker's default capabilities include `CAP_DAC_OVERRIDE`. A capability inside a
separate Linux user namespace applies only to files whose owner and group are mapped there. Put the socket in a directory of its own,
owned by Flower's user, with a group that only the proxy uses and mode `0750`, and with no ACL entry that grants
anyone else search. Set that owner, group and mode in whatever creates the directory, because files under `/run` are
cleared at boot and systemd's `RuntimeDirectory=` creates its directory with mode `0755` unless
`RuntimeDirectoryMode=` sets another. When the proxy runs in another container and shares the directory through a
volume, permissions are checked against numeric IDs, not names, after any user-namespace or idmapped-mount mapping,
so the proxy's process must hold the directory's group, as the kernel sees it, as its primary or a supplementary
group. Use a filesystem path, never an abstract socket name (one beginning with a NUL byte): Tornado applies no mode
to such a name, and on Linux file permissions have no meaning for abstract sockets.

## Argo Workflows

At Argo Workflows v3.7.18 and v4.1.4, Argo Server binds `:<port>` (`:2746` by default) using
Go's `tcp` listener: a wildcard bind, with IPv4/IPv6 availability determined by the host. There is no
bind-address flag. The CLI defaults are `--secure=true`, `--auth-mode=client` and `--hsts=true`;
flags or their `ARGO_*` environment equivalents can override them. Client mode uses the caller's
Kubernetes credentials and permissions. At v4.1.4 it also validates the token with a
`SelfSubjectReview`, requiring Kubernetes 1.28 or later.

**The shipped quick-start manifests override the authentication default.** At both tags,
`manifests/quick-start-minimal.yaml`, `manifests/quick-start-mysql.yaml` and
`manifests/quick-start-postgres.yaml` pass `--auth-mode server --auth-mode client`; v4.1.4 also ships
`manifests/quick-start-telemetry.yaml` with those arguments. They leave TLS enabled. Following the
quick-start therefore leaves 2746 open to anonymous callers who can reach it, acting with the
`argo-server` ServiceAccount's permissions. Its `argo-server-cluster-role` is bound cluster-wide and
permits creating, listing, updating and deleting workflows and templates, as well as getting and
creating Secrets. The quick-start also binds `argo-server-clusterworkflowtemplate-role`. These are
demo installations: the quick-start docs explicitly say they are unsuitable for production.

The sources used to build `manifests/install.yaml` set only `args: [server]`, retaining client auth
and TLS, and bind the same `argo-server-cluster-role` to the server account. The sources for
`manifests/namespace-install.yaml` add `--namespaced` and instead bind the namespace-scoped
`argo-server-role`. Neither enables server auth or disables TLS. In all these manifests the
`argo-server` Service omits `type` (Kubernetes defaults it to `ClusterIP`) and maps port 2746 to
2746. That does not publish it on the internet, but does not authenticate reachable callers either.

Remove `--auth-mode=server` from the effective configuration. Adding client or SSO mode does not
remove anonymous access while server mode remains: a request without credentials falls back to the
server's own Kubernetes clients. In local mode those use the server's kubeconfig credentials instead.
`--auth-mode=sso` provides OIDC login; enable SSO RBAC (`sso.rbac.enabled: true`) and map groups to
narrowly scoped ServiceAccounts with `workflows.argoproj.io/rbac-rule` and
`workflows.argoproj.io/rbac-rule-precedence`. Without SSO RBAC, authenticated users share the server's
permissions. Store OAuth client credentials in Kubernetes Secrets referenced by the SSO configuration,
and feed API tokens to clients through protected input rather than command-line arguments
([secrets.md](secrets.md)).

Keep 2746 private behind an authenticating HTTPS proxy, with MFA enforced at the identity provider
([fronting-auth.md](fronting-auth.md), [mfa.md](mfa.md)); restrict direct Pod and Service access with
NetworkPolicy and do not publish the port publicly. Enforce private exposure at the network and
Service layers. Keep TLS enabled and provision a certificate trusted by clients using
`--tls-certificate-secret-name`. With secure mode enabled and no certificate Secret name supplied,
the server generates a self-signed certificate; failure to load a named Secret fails startup.
`--secure=false` switches the same listener to plaintext, and HSTS has no effect without TLS.
The server's `/metrics` endpoint shares this listener and uses the auth gate unless
`ARGO_SERVER_METRICS_AUTH=false`; server mode also admits anonymous metrics requests.
Limit the namespaces and permissions available to the server, SSO accounts, and workflow execution
accounts. Permission to submit workflows permits arbitrary containers by default (workflow restrictions
and admission policies can constrain the permitted specs), and powerful execution accounts or privileged
Pods can turn an exposed API into cluster compromise.

## Verify

REASONED: following block; every probe in the following block (the ss inventory, the Prefect, Dagster, Airflow, Temporal, Flower and Argo anonymous and authorized calls, the Flower socket-directory stat and getfacl lines, and the guarded direct-origin probe) is covered by this declaration. The declaration for those probes rests on the guide's cited entries Prefect, security settings; Dagster webserver and UI; Apache Airflow FAB provider, API authentication; Apache Airflow running in Docker; Temporal, self-hosted security; Flower configuration; and Argo anonymous fallback when server mode is enabled. The authoring environment has no container runtime, Kubernetes cluster or orchestrator install, and no network access to obtain one. During marking review (October 2026) the block passed bash -n under bash 5.3.9 and ShellCheck 0.11.0 and ran with stub ss, curl and temporal and no network: each illustrative probe reached only the stubs. The origin guard in that stub run (marking review, October 2026) printed its substitute-your-origin-URL refusal unchanged, the paste-the-whole-block refusal without its set -- line, the exactly-1-value refusal when shortened and the http-or-https refusal for an ftp:// URL, and passed a substituted https:// URL to the stub. The October 2026 marking review reported piped-input helper checks, including header encoding, JSON escaping and invalid Argo tokens; these are historical observations, not new runs. In the first TODO 50 review, the unchanged and changed blocks ran from files with hidden prompts driven through a pseudo-terminal, dummy credentials, and stubs for every external command (the Python stub delegated only the known helpers to the isolated interpreter). No probe reached a service. Before the change, all three authenticated labels still ran when their helper exited 73, including after partial output. An empty terminal response produced a Basic header with an empty value for Prefect and JSON containing an empty username or password for Airflow; those helpers succeeded. Argo rejected an empty response, but its curl still ran with empty stdin. After the change, valid dummy inputs reached all three authenticated curl stubs with the expected header or JSON. Each empty credential, each helper exit 73 and each partial-output failure printed the matching credential-helper refusal and skipped only that authenticated probe; the other labelled calls were unchanged. These local runs test shell control flow, not service authentication. During marking review (October 2026), the second TODO 50 review ran the unchanged and revised blocks from files under bash 5.3.9(1)-release and Python 3.14.4 with dummy credentials on a pseudo-terminal, stubs for every external command and only the known credential helpers delegated to the scratch interpreter. Under bash -e before that revision, each helper exit 73, partial-output failure or empty credential stopped the calling shell at that authenticated probe, so later probes did not run. In those second-review fixtures, where every other external-command stub succeeded, each refusal skipped only its authenticated request and all later probes ran. Valid credentials reached all three authenticated curl stubs with the expected header or JSON before and after, with and without bash -e. All four empty credential cases and each helper failure were also checked without errexit before and after. With PYTHONOPTIMIZE=1 and an empty Argo token, the unchanged helper sent an empty bearer header; the revised helper refused it and skipped the Argo authenticated request, with and without bash -e. In that second review, every completed sequence reached the unchanged direct-origin placeholder refusal; all files exited 2, either at the first unhandled refusal before that revision under bash -e or at the final origin guard. These runs checked shell flow and credential encoding only, not service authentication. During marking review (October 2026), the third TODO 50 review ran the unchanged and revised blocks from files under bash 5.3.9(1)-release and Python 3.14.4 through a pseudo-terminal with dummy credentials, stubs for every external command and only the three exact credential helpers delegated to the isolated scratch interpreter. No probe reached a service or read the host socket paths. Before this revision, under bash -e, exit 1 from ss, Temporal, stat or getfacl, and curl exits 6, 7 or 28 from each anonymous or default-account probe, stopped the file at that label and skipped the remaining probes. After this revision, under bash -e, those same cases reached every later label and the final origin-placeholder refusal. Each authenticated curl exit 6, 7 or 28, helper exit 73, partial-output failure and empty credential case reached all later probes before and after; helper refusals sent no authenticated request. Valid dummy credentials produced the expected Basic header, JSON and bearer header before and after. An empty Argo token was also refused with PYTHONOPTIMIZE=1 before and after. With a substituted origin URL, origin curl exits 6, 7 and 28 were reported before and after. The missing-set-line, short-set-line and ftp:// origin cases refused without an origin request before and after. The revised files exited 0 after their labelled continuation messages, including the final origin refusal; this status means the sequence continued, not that any service was secure. These stub runs establish shell flow and encoding only, not service authentication. The stat and getfacl observations are recorded after the block. These probes are reasoned, not demonstrated, because the authoring environment has no container runtime, so no
live orchestrator was stood up in its exposed or fixed state. For Argo, the authoring host forbids opening listeners without an isolated network namespace, and has none;
no Kubernetes cluster is available. Its listener, TLS and authentication checks remain REASONED.
The exception is the Flower unix-socket stat mode
and named-ACL checks, demonstrated without a container and recorded after the block. Each names its expected
exposed and fixed result so it discriminates against a live instance, based on the cited vendor documentation
and pinned sources across all six tools. The `*.internal` hostnames are examples for a reachable vantage (you have not isolated the
port yet, or you are on an allowed network); substitute your own. For every negative check run the matched
authorized call against the SAME origin, and separately probe the origin directly from an untrusted vantage with
the guarded block at the end, because a rejection seen only through a proxy does not prove the origin enforces
anything. The write-out fields need curl 7.75.0 or newer; never use `-k`.

```bash
# REASONED: orchestrator checks follow the cited vendor documentation and pinned sources; no container runtime
# or Kubernetes cluster is available. Flower stat mode and named-ACL observations are recorded after this block.
# Credential guards assume a clean shell with trusted startup files and real builtins.
# Each capture ends with the helper status; strip it only after success, then feed curl on stdin.
ss -tlnp || echo 'ss: exited nonzero; continuing'   # TCP listeners in THIS network namespace only (4200/3000/8080/7233/8233/5555/2746): not a firewall,
           # publication, routing, or auth check. Inspect container publications and probe external
           # reachability separately; a wildcard bind is a prompt to investigate, not proof of exposure

# Prefect: an empty JSON filter. Once the auth string is set the anonymous call is 401 and the authorized call
# returns a JSON flow list; an anonymous list, even an empty one, is the finding. Feed the auth string on stdin.
# getpass prompts without echo on a terminal, so the auth string enters neither shell history nor set -x
# tracing; stdin closes the argv channel only, and the account owner and root can still read it in
# python3, the block's subshell and curl.
# Do NOT use /api/health or /api/ready as the authentication discriminator. Current server source exempts
# those GET paths; this behavior is version-dependent and was not present in 3.1.8.
# guard-conventions: allow probe of an illustrative internal host; no reader-substituted placeholder in this probe's argv
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
  -w '\nprefect-anon http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
  -H 'Content-Type: application/json' -X POST --data-binary '{}' http://prefect.internal:4200/api/flows/filter \
  || echo 'prefect-anon: exited nonzero; continuing'
(
  trap - DEBUG RETURN ERR
  set +x +a +e
  set -- "$(python3 -I -c 'import base64,getpass,sys; s=getpass.getpass("Prefect username:password: "); s or sys.exit("empty credential"); print("header = \"Authorization: Basic " + base64.b64encode(s.encode()).decode() + "\"")'; printf '\n%s' "$?")"
  case "$1" in
    *$'\n0') set -- "${1%$'\n'*}" ;;
    *) echo "prefect-auth: credential helper failed; not probing"; exit 2 ;;
  esac
  # guard-conventions: allow probe of an illustrative internal host; no reader-substituted placeholder in this probe's argv
  printf '%s' "$1" \
    | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 --config - \
        -w '\nprefect-auth http=%{http_code} exit=%{exitcode}\n' \
        -H 'Content-Type: application/json' -X POST --data-binary '{}' http://prefect.internal:4200/api/flows/filter
) || echo 'prefect-auth: skipped or failed; continuing'

# Dagster has no login of its own, so test /graphql, which can read configuration and launch runs.
# A RepositoryConnection containing nodes (including an empty nodes list) is a successful read.
# PythonError, top-level GraphQL errors, and transport failures are inconclusive.
# Test the proxy separately: send this identical query anonymously and authenticated to the SAME proxy URL.
# Test origin reachability independently; proxy authentication does not authenticate the OSS origin.
# guard-conventions: allow probe of an illustrative internal host; no reader-substituted placeholder in this probe's argv
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
  -w '\ndagster-anon http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
  -H 'Content-Type: application/json' -X POST \
  --data-binary '{"query":"{ repositoriesOrError { __typename ... on RepositoryConnection { nodes { name location { name } } } } }"}' http://dagster.internal:3000/graphql \
  || echo 'dagster-anon: exited nonzero; continuing'

# Airflow: obtaining a token from the documented Compose account is the finding. Send the credentials as JSON
# on stdin; FAB 3.9.0 returns 201 Created with a nonempty access_token when airflow/airflow works. Compare with a valid account on
# the same route (the second call below), and test an API read with no token then a token at the proxy and the
# origin. On Airflow 2 use its /api/v1/ endpoint and its own auth mechanism instead. The first call's body is
# fixed; never type a real password into it.
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
printf '%s' '{"username":"airflow","password":"airflow"}' \
  | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
      -w '\nairflow-token http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
      -H 'Content-Type: application/json' --data-binary @- https://airflow.example.com/auth/token \
      || echo 'airflow-token: exited nonzero; continuing'
# The valid-account comparison. getpass prompts without echo on a terminal, so the username and password enter
# neither shell history nor set -x tracing, and json.dumps escapes any double quote, backslash or control
# character in them, so the body stays one JSON object; stdin closes the argv channel only, and the account
# owner and root can still read the password in python3, the block's subshell and curl.
(
  trap - DEBUG RETURN ERR
  set +x +a +e
  set -- "$(python3 -I -c 'import getpass,json,sys; u=getpass.getpass("Airflow username: "); p=getpass.getpass("Airflow password: "); (u and p) or sys.exit("empty credential"); print(json.dumps({"username": u, "password": p}))'; printf '\n%s' "$?")"
  case "$1" in
    *$'\n0') set -- "${1%$'\n'*}" ;;
    *) echo "airflow-valid-token: credential helper failed; not probing"; exit 2 ;;
  esac
  # guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
  printf '%s' "$1" \
    | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        -w '\nairflow-valid-token http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        -H 'Content-Type: application/json' --data-binary @- https://airflow.example.com/auth/token
) || echo 'airflow-valid-token: skipped or failed; continuing'
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
  -w '\nairflow-pools-anon http=%{http_code} exit=%{exitcode}\n' https://airflow.example.com/api/v2/pools \
  || echo 'airflow-pools-anon: exited nonzero; continuing'

# Temporal: a protected read against the frontend gRPC port. With an Authorizer and ClaimMapper configured this
# is rejected without credentials (an mTLS deployment refuses the connection outright); a listing, even an empty
# one, is the finding. Health checks, TLS errors, missing namespaces, and unavailable services do not prove
# authorization, so use a real workflow list, not a health call, and run it with no ambient credentials set.
temporal workflow list --address temporal.internal:7233 --namespace default --limit 1 \
  || echo 'temporal: exited nonzero; continuing'

# Flower: the dashboard and the API. With Basic Auth an anonymous request is 401; with OAuth it is a 302 redirect into
# the login flow, not 401, so inspect the redirect without following it and confirm access with a
# valid session. An anonymous worker list from /api/workers is the finding; an API-disabled response does not
# prove the dashboard is protected.
# guard-conventions: allow probe of an illustrative internal host; no reader-substituted placeholder in this probe's argv
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 --dump-header - \
  -w '\nflower-ui http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' http://flower.internal:5555/ \
  || echo 'flower-ui: exited nonzero; continuing'
# guard-conventions: allow probe of an illustrative internal host; no reader-substituted placeholder in this probe's argv
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 --dump-header - \
  -w '\nflower-api http=%{http_code} exit=%{exitcode}\n' http://flower.internal:5555/api/workers \
  || echo 'flower-api: exited nonzero; continuing'

# Flower on a unix socket. The stat mode and named-ACL checks were demonstrated (recorded after this block); the
# socket line is reasoned, not demonstrated: this authoring environment has no Flower install, and the authoring
# host forbids opening listeners, unix sockets included (the expectation follows the cited Flower source). Expect the directory
# to grant nothing to "other" (750, or 2750 with setgid), owned by Flower's user and the proxy-only group,
# compared by number (%u:%g) from inside each container that uses it; the socket shows 777 by design. The mode
# bits do not show named ACL entries, so getfacl (from the acl package) should list only the user::, group:: and
# other:: access entries. Any named user: or group: entry whose own permissions include x is a finding, even where
# getfacl prints #effective: without x, because a later chmod of the directory resets mask:: to its group bits.
# default: entries set the ACL of files created inside, not access to the directory. Recheck after each reboot and
# deployment change. Substitute your socket's directory and path.
stat -c '%a %U:%G %u:%g %n' /run/flower /run/flower/flower.sock \
  || echo 'flower-stat: exited nonzero; continuing'
getfacl -p /run/flower \
  || echo 'flower-getfacl: exited nonzero; continuing'

# Argo: REASONED, not demonstrated; the authoring host forbids opening listeners without an isolated
# network namespace, and has none; no Kubernetes cluster is available.
# Server mode: an anonymous HTTP 200 containing a workflow list, even empty, is the finding,
# provided the server identity can list workflows in this namespace. Without server mode (client/sso only):
# a missing token is 401. A 403 means only that this operation was denied to the identity used; it does NOT
# prove server mode is off, since server mode can be enabled yet lack list RBAC in this namespace and also
# return 403, so confirm the configured --auth-mode separately. The matched authorized call must return
# HTTP 200 with a workflow list. A health endpoint is NOT the discriminator. Replace the hostname and
# namespace in BOTH calls; use a reachable allowed vantage and trusted TLS, configure the private CA if
# necessary, never -k. TLS/DNS errors, redirects, 404s, and 5xx are inconclusive.
# guard-conventions: allow probe of an illustrative internal host; no reader-substituted placeholder in this probe's argv
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 --dump-header - \
  -w '\nargo-anon http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
  https://argo.internal:2746/api/v1/workflows/argo \
  || echo 'argo-anon: exited nonzero; continuing'
# Enter a Kubernetes bearer token (client mode) or an Argo session token (SSO mode) with list permission in
# this namespace. The token goes to curl on stdin, never argv.
# getpass prompts without echo on a terminal, so the token enters neither shell history nor set -x
# tracing; stdin closes the argv channel only, and the account owner and root can still read it in
# python3, the block's subshell and curl.
(
  trap - DEBUG RETURN ERR
  set +x +a +e
  set -- "$(python3 -I -c 'import getpass,sys; t=getpass.getpass("Argo bearer token (without Bearer prefix): "); (t and all(33 <= ord(c) <= 126 for c in t)) or sys.exit("invalid token"); print("Authorization: Bearer " + t)'; printf '\n%s' "$?")"
  case "$1" in
    *$'\n0') set -- "${1%$'\n'*}" ;;
    *) echo "argo-auth: credential helper failed; not probing"; exit 2 ;;
  esac
  # guard-conventions: allow probe of an illustrative internal host; no reader-substituted placeholder in this probe's argv
  printf '%s' "$1" \
    | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 --dump-header - \
        --header @- -w '\nargo-auth http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        https://argo.internal:2746/api/v1/workflows/argo
) || echo 'argo-auth: skipped or failed; continuing'

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
    http://*|https://*)
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 -o /dev/null \
        -w 'origin http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1" ;;
    *) echo "give an http:// or https:// URL; not probing"; exit 2 ;;
  esac
) || echo 'origin: skipped or failed; continuing'
```

REASONED: preceding block; every probe in the block above, summarized here as findings, per the guide's cited entries Prefect, security settings; Dagster webserver and UI; Apache Airflow running in Docker; Temporal, self-hosted security; Temporal, Web UI configuration reference; Flower configuration; and Argo anonymous fallback when server mode is enabled. It adds no probe of its own; that block's local runs are recorded in the declaration before it, and no orchestrator was available in the authoring environment to show either state. Exposed, a listing answers without a credential; fixed, the anonymous call is refused while the matched authorized call succeeds. A DAG list, flow run, task graph, repository, or worker pool that renders without a credential is a finding; so
is a Temporal Service that answers `temporal workflow list` with no claim behind it, since the UI login does not
cover the frontend gRPC path.

DEMONSTRATED: the Flower socket-directory stat and getfacl checks in the items below, on directories only, exposed (mode 0755, or a named entry granting x) against fixed (mode 0750 with only the base entries). During marking review (October 2026) they were run again in a btrfs scratch directory with uutils stat 0.8.0 and getfacl 2.3.2 and printed the values recorded below; again no socket was created and no Flower process ran. The Flower unix-socket directory checks were demonstrated on the authoring host, on tmpfs, with directories only:
no socket was created and no Flower process ran.

- DEMONSTRATED: the mode check, exposed 0755 against fixed 0750; the marking-review run (October 2026, btrfs, uutils stat 0.8.0, getfacl 2.3.2) printed the same values. `stat -c '%a %U:%G %u:%g %n'` printed `755` for a directory created with mode `0755` and `750` for one created
  with `0750`; `getfacl -p` on the `0750` directory listed only `user::rwx`, `group::r-x` and `other::---`.
- DEMONSTRATED: a named entry on the fixed 0750 directory, before and after; the marking-review run (October 2026, btrfs, uutils stat 0.8.0, getfacl 2.3.2) printed the same values. After `setfacl -m u:nobody:--x` on the `0750` directory, `stat` still printed `750`. Only the trailing `+` in
  `ls -ld` and getfacl's `user:nobody:--x` line showed the named entry.
- DEMONSTRATED: the mask and chmod interaction, compared with the fixed 0750 directory in the first item, where `getfacl -p` listed only `user::rwx`, `group::r-x` and `other::---`; the marking-review run (October 2026, btrfs, uutils stat 0.8.0, getfacl 2.3.2) printed the same values, and access as nobody was again not tested. After `setfacl -m m::r--`, getfacl printed `user:nobody:--x` with `#effective:---`. While masked, `stat` printed `740`. A later
  `chmod 0750` reset `mask::` to `r-x`, and getfacl printed `user:nobody:--x` with no `#effective:` mark, so
  under acl(5) the entry's `x` is in effect again (access as `nobody` was not tested).

REASONED: the Flower service, cross-account and container checks remain unobserved, per the guide's cited Flower `--unix_socket` passes the fixed mode `0o777` entry (pinned v2.2.0 and v6.5.10, with unix(7), path_resolution(7), user_namespaces(7) and acl(5)). The authoring environment has no Flower install, no container runtime and no privilege to act as a second account, so neither an outside account's refusal at a 0750 directory (fixed) nor its traversal through a named x entry (exposed) was observed. During marking review (October 2026) the 2750 form and a default: entry were run in a btrfs scratch directory: after chmod 2750, uutils stat 0.8.0 printed 2750 (uutils mkdir 0.8.0 given -m 2750 had left 750); getfacl 2.3.2 listed default:user:nobody:--x beside an access ACL of only user::, group:: and other::, and a directory created inside inherited user:nobody:--x as an access entry. Not run: whether an account outside the proxy's group is refused at the directory, the socket's `777` after each
Flower start, and the `%u:%g` comparison from inside a container that
shares the directory.

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
  access to a Codec Server, so authenticate and restrict any Codec Server separately.

## Sources (checked October 2026)

These defaults are checked against Prefect 3.1.8+ for Basic Auth, Dagster 1.13.x, Apache Airflow 3.3.2 with FAB provider 3.9.0 (Airflow 2.11.0 noted where the configuration paths differ), Temporal Server 1.28.x and UI Server 2.34.x, and Flower 2.2.0; confirm your own versions, since several of these settings moved between releases. Argo Workflows listener, authentication paths, TLS and manifest settings were checked against tags v3.7.18 (66e32e5cc367f223e2ecf4fbe852b95eaed83034) and v4.1.4 (b5b4d665e9be9b87c115f943584c3e0ae96fe073). The install manifests were traced through their build recipes and Kustomize inputs; their generated YAML files were not present in the supplied trees. SSO setup, API examples and security guidance retain the release-3.7 documentation links.

- Prefect, security settings (`PREFECT_SERVER_API_AUTH_STRING`, `PREFECT_API_AUTH_STRING`, Cloud API keys
  taking precedence and causing 401) (rolling documentation, checked September 2026): https://docs.prefect.io/v3/advanced/security-settings
- Prefect 3.1.8 release announcement, Basic Auth support added to the API and UI: https://github.com/PrefectHQ/prefect/releases/tag/3.1.8
- Prefect 3.1.8 block-document filter and ID read routes accept `include_secrets`, and `Secret.get()` returns the underlying value. Prefect 3.1.8 sources: https://github.com/PrefectHQ/prefect/blob/3.1.8/src/prefect/server/api/block_documents.py#L47-L70, https://github.com/PrefectHQ/prefect/blob/3.1.8/src/prefect/server/api/block_documents.py#L101-L119 and https://github.com/PrefectHQ/prefect/blob/3.1.8/src/prefect/blocks/system.py#L154-L159
- Apache Airflow FAB provider 3.9.0 reads `[fab] auth_role_public` with legacy `AUTH_ROLE_PUBLIC` fallback, attaches the public role's permissions to an anonymous user when that role exists, and pins Flask-AppBuilder 5.2.2. Apache Airflow FAB provider 3.9.0 sources: https://github.com/apache/airflow/blob/providers-fab/3.9.0/providers/fab/src/airflow/providers/fab/auth_manager/fab_auth_manager.py#L327-L381 and https://github.com/apache/airflow/blob/providers-fab/3.9.0/providers/fab/pyproject.toml#L75-L81
- Apache Airflow 3.3.2 `_NullFernet` and `get_fernet()` key selection: https://github.com/apache/airflow/blob/3.3.2/airflow-core/src/airflow/models/crypto.py#L47-L68 and https://github.com/apache/airflow/blob/3.3.2/airflow-core/src/airflow/models/crypto.py#L154-L173
- Temporal Go SDK v1.28.0 codec HTTP handler POST encode/decode paths and construction: https://github.com/temporalio/sdk-go/blob/v1.28.0/converter/codec.go#L284-L350
- Prefect self-hosted server, default port 4200 (rolling documentation, checked September 2026): https://docs.prefect.io/v3/how-to-guides/self-hosted/server-cli
- Dagster webserver and UI, default local port and no documented built-in auth (rolling documentation, checked September 2026): https://docs.dagster.io/guides/operate/webserver
- Dagster webserver `DEFAULT_WEBSERVER_HOST` "127.0.0.1" and port 3000 with the free-port fallback, and `dagster dev` forwarding `--host` only when one is given (pinned tag 1.13.24). The Dagster environment-variable routes (`DAGSTER_WEBSERVER_*` through `auto_envvar_prefix`, legacy `DAGIT_*` copied onto them, and the `dagster` CLI's `DAGSTER_CLI` prefix, which Click extends per subcommand, so `dagster dev` reads `DAGSTER_CLI_DEV_*`) (pinned tag 1.13.24). The Helm chart's webserver command, which hardcodes `-h 0.0.0.0` and takes the port from `dagsterWebserver.service.port` (80 by default, Service type `ClusterIP` by default) (pinned tag 1.13.24). Dagster 1.13.24 sources (1 of 3): https://github.com/dagster-io/dagster/blob/1.13.24/python_modules/dagster-webserver/dagster_webserver/cli.py#L41-L42, https://github.com/dagster-io/dagster/blob/1.13.24/python_modules/dagster-webserver/dagster_webserver/cli.py#L81-L96 and https://github.com/dagster-io/dagster/blob/1.13.24/python_modules/dagster-webserver/dagster_webserver/cli.py#L306-L311. Dagster 1.13.24 sources (2 of 3): https://github.com/dagster-io/dagster/blob/1.13.24/python_modules/dagster/dagster/_cli/dev.py#L251-L252, https://github.com/dagster-io/dagster/blob/1.13.24/python_modules/dagster-webserver/dagster_webserver/cli.py#L339-L351 and <https://github.com/dagster-io/dagster/blob/1.13.24/python_modules/dagster/dagster/_cli/__init__.py#L45-L50>. Click's subcommand prefix rule (pinned tag 8.5.0): https://github.com/pallets/click/blob/8.5.0/src/click/core.py#L476-L484. Dagster 1.13.24 sources (3 of 3): https://github.com/dagster-io/dagster/blob/1.13.24/helm/dagster/templates/helpers/_deployment-webserver.tpl#L86-L90, https://github.com/dagster-io/dagster/blob/1.13.24/helm/dagster/templates/helpers/_helpers.tpl#L55 and https://github.com/dagster-io/dagster/blob/1.13.24/helm/dagster/values.yaml#L54-L58
- Apache Airflow security overview (rolling documentation, checked September 2026): https://airflow.apache.org/docs/apache-airflow/stable/security/
- Apache Airflow, auth manager selection (`[core] auth_manager`, `airflow config get-value core auth_manager`) (Airflow 3.3.2 documentation): https://airflow.apache.org/docs/apache-airflow/3.3.2/core-concepts/auth-manager/index.html
- Apache Airflow FAB provider, API authentication (`[fab] auth_backends`, independent of the auth manager) (rolling documentation, checked September 2026): https://airflow.apache.org/docs/apache-airflow-providers-fab/stable/auth-manager/api-authentication.html
- Prefect server source (health and ready paths exempted from the auth string on GET): https://github.com/PrefectHQ/prefect/blob/9e560c9b6df4e19a5109a66e66d461f9facb538d/src/prefect/server/api/server.py
- Apache Airflow, quickstart (default port 8080): https://airflow.apache.org/docs/apache-airflow/stable/start.html
- Apache Airflow running in Docker, development Compose defaults for credentials, JWT signing and port publication (rolling documentation, checked September 2026): https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html
- Apache Airflow security model, authenticated users and private deployment (Airflow 3.3.2 documentation): https://airflow.apache.org/docs/apache-airflow/3.3.2/security/security_model.html
- Apache Airflow Simple auth manager, default for development/testing, configured users and generated passwords (Airflow 3.3.2 documentation): https://airflow.apache.org/docs/apache-airflow/3.3.2/core-concepts/auth-manager/simple/index.html
- Temporal, self-hosted security (`noopAuthorizer` default, `Authorizer`, `ClaimMapper`) (rolling documentation, checked September 2026): https://docs.temporal.io/self-hosted-guide/security
- Temporal, Web UI configuration reference (`auth.providers`, `enabled`, `type: oidc`, `providerUrl`,
  `clientId`, `clientSecret`, `callbackUrl`, `scopes`) (rolling documentation, checked September 2026): https://docs.temporal.io/references/web-ui-configuration
- Temporal CLI server reference, default frontend gRPC port 7233 and Web UI port 8233 (rolling documentation, checked September 2026): https://docs.temporal.io/cli/command-reference/server
- Flower configuration, `--address`, `--port` 5555 default, `--basic-auth`, `--auth_provider`, `--oauth2_key`, `--oauth2_secret`, `--oauth2_redirect_uri` and `--auth` (rolling documentation, checked September 2026): https://flower.readthedocs.io/en/latest/config.html
- Flower `port` default 5555, `address` default `''` and the `unix_socket` branch, the `FLOWER_` environment variables, and the implicit `flowerconfig.py` load from the working directory (pinned tag v2.2.0), with Tornado's `bind_sockets` treating an empty address as all interfaces (pinned tag v6.5.10). Flower v2.2.0 and Tornado v6.5.10 sources: https://github.com/mher/flower/blob/v2.2.0/flower/options.py#L7-L15, https://github.com/mher/flower/blob/v2.2.0/flower/options.py#L56-L57, https://github.com/mher/flower/blob/v2.2.0/flower/command.py#L39-L91, https://github.com/mher/flower/blob/v2.2.0/flower/app.py#L71-L76 and https://github.com/tornadoweb/tornado/blob/v6.5.10/tornado/netutil.py#L72-L73
- Flower `--unix_socket` passes the fixed mode `0o777` (pinned tag v2.2.0); Tornado's `bind_unix_socket` removes an existing socket at a filesystem path, binds, then applies that mode, and binds a name with a leading NUL with no mode (pinned tag v6.5.10). A connection to a stream socket on Linux needs write permission on that socket, and file permissions on Linux have no meaning for abstract sockets. Path lookup needs search permission on each directory, `CAP_DAC_OVERRIDE` overrides permission checks and `CAP_DAC_READ_SEARCH` grants search on directories. File permission checks in a user namespace compare IDs mapped back to the initial namespace, and a capability in a user namespace applies only to a file whose owner and group are mapped there. Docker's default capability set includes `CAP_DAC_OVERRIDE` (moby docker-v29.8.1); an idmapped mount changes ownership for that mount only; `RuntimeDirectoryMode=` defaults to `0755` (systemd v257); files under `/run` must be cleared at the beginning of the boot process (FHS 3.0). Named ACL entries grant access only up to the mask, changing a file's group permission bits sets its `ACL_MASK` entry, a directory's default ACL governs the initial ACL of objects created within it, and `getfacl` marks a limited entry `#effective:`; `stat -c` format sequences. Sources for this item (1 of 3): https://github.com/mher/flower/blob/v2.2.0/flower/app.py#L85-L89, https://github.com/tornadoweb/tornado/blob/v6.5.10/tornado/netutil.py#L215-L228, https://man7.org/linux/man-pages/man7/unix.7.html and https://man7.org/linux/man-pages/man7/path_resolution.7.html. Sources for this item (2 of 3): https://man7.org/linux/man-pages/man7/user_namespaces.7.html, https://www.kernel.org/doc/html/latest/filesystems/idmappings.html and https://github.com/moby/moby/blob/docker-v29.8.1/daemon/pkg/oci/caps/defaults.go#L4-L7. Sources for this item (3 of 3): https://github.com/systemd/systemd/blob/v257/man/systemd.exec.xml#L1630-L1640, https://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch03s15.html, https://man7.org/linux/man-pages/man5/acl.5.html, https://man7.org/linux/man-pages/man1/getfacl.1.html and https://man7.org/linux/man-pages/man1/stat.1.html
- Linux `ss` socket statistics (`iproute2` v6.15.0), with `-N`/`--net` to switch network namespace. The `iproute2` v6.15.0 `ss` manual sources: https://github.com/iproute2/iproute2/blob/v6.15.0/man/man8/ss.8#L7-L12 and https://github.com/iproute2/iproute2/blob/v6.15.0/man/man8/ss.8#L358-L359. Network namespaces isolating network devices, protocol stacks and port numbers (Linux man-pages-5.13). The Linux man-pages-5.13 source: https://github.com/mkerrisk/man-pages/blob/man-pages-5.13/man7/network_namespaces.7#L30-L40
- Argo CLI defaults and environment overrides: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/cmd/argo/commands/server.go#L191-L229), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/cmd/argo/commands/server.go#L195-L239).
- Argo TLS certificate selection and generation: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/cmd/argo/commands/server.go#L113-L137), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/cmd/argo/commands/server.go#L119-L143).
- Argo wildcard TCP listener and TLS wrapper: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/server/apiserver/argoserver.go#L263-L282), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/server/apiserver/argoserver.go#L299-L320).
- Argo anonymous fallback when server mode is enabled: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/server/auth/mode.go#L33-L44), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/server/auth/mode.go#L33-L44).
- Argo client credentials, server credentials and SSO RBAC selection: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/server/auth/gatekeeper.go#L166-L218), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/server/auth/gatekeeper.go#L189-L244).
- Argo quick-start auth override: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/quick-start/base/overlays/argo-server-deployment.yaml#L1-L15), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/quick-start/base/overlays/argo-server-deployment.yaml#L1-L15).
- Argo quick-start-minimal server deployment: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/quick-start-minimal.yaml#L3613-L3664), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/quick-start-minimal.yaml#L192772-L192823).
- Argo quick-start-mysql server deployment: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/quick-start-mysql.yaml#L3678-L3729), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/quick-start-mysql.yaml#L192838-L192889).
- Argo quick-start-postgres server deployment: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/quick-start-postgres.yaml#L3677-L3728), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/quick-start-postgres.yaml#L192837-L192888).
- Argo additional quick-start-telemetry server deployment: [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/quick-start-telemetry.yaml#L192919-L192970).
- Argo install manifest build recipes: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/Makefile#L493-L515), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/Makefile#L608-L634).
- Argo base server account, args and HTTPS readiness probe: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/base/argo-server/argo-server-deployment.yaml#L14-L34), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/base/argo-server/argo-server-deployment.yaml#L14-L34).
- Argo base Service ports (type omitted): [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/base/argo-server/argo-server-service.yaml#L1-L11), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/base/argo-server/argo-server-service.yaml#L1-L11).
- Argo namespace install server args overlay: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/namespace-install/overlays/argo-server-deployment.yaml#L1-L4), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/namespace-install/overlays/argo-server-deployment.yaml#L1-L4).
- Argo server ClusterRole permissions: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/cluster-install-no-crds/argo-server-rbac/argo-server-clusterole.yaml#L1-L65), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/cluster-install-no-crds/argo-server-rbac/argo-server-clusterole.yaml#L1-L67).
- Argo server ClusterRole binding: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/cluster-install-no-crds/argo-server-rbac/argo-server-clusterolebinding.yaml#L1-L11), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/cluster-install-no-crds/argo-server-rbac/argo-server-clusterolebinding.yaml#L1-L11).
- Argo namespace server Role permissions: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/namespace-install/argo-server-rbac/argo-server-role.yaml#L1-L65), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/namespace-install/argo-server-rbac/argo-server-role.yaml#L1-L67).
- Argo namespace server Role binding: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/namespace-install/argo-server-rbac/argo-server-rolebinding.yaml#L1-L11), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/namespace-install/argo-server-rbac/argo-server-rolebinding.yaml#L1-L11).
- Argo quick-start base resources, which include `cluster-install-no-crds`: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/quick-start/base/kustomization.yaml#L4-L5), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/quick-start/base/kustomization.yaml#L4-L5).
- Argo additional quick-start cluster-template permissions and bindings: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/quick-start/base/cluster-workflow-template-rbac.yaml#L1-L58), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/quick-start/base/cluster-workflow-template-rbac.yaml#L1-L58).
- Argo gatekeeper `Context` path to the same client selection: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/server/auth/gatekeeper.go#L106-L121), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/server/auth/gatekeeper.go#L133-L148).
- Argo metrics auth and conditional HSTS: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/server/apiserver/argoserver.go#L430-L449), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/server/apiserver/argoserver.go#L476-L494).
- Argo quick-start purpose and production warning: [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/docs/quick-start.md#L3-L34), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/docs/quick-start.md#L3-L34).
- Argo auth-mode history and hosted/local identities (v4.1.4 also documents the Kubernetes 1.28 requirement): [v3.7.18](https://github.com/argoproj/argo-workflows/blob/v3.7.18/docs/argo-server-auth-mode.md#L3-L9), [v4.1.4](https://github.com/argoproj/argo-workflows/blob/v4.1.4/docs/argo-server-auth-mode.md#L3-L9).
- Argo Workflows, [SSO and RBAC](https://argo-workflows.readthedocs.io/en/release-3.7/argo-server-sso/),
  [workflow-list API](https://argo-workflows.readthedocs.io/en/release-3.7/rest-examples/), and
  [security model](https://argo-workflows.readthedocs.io/en/release-3.7/security/).
- Apache Airflow API authentication setting and default (2.11.0 documentation): https://airflow.apache.org/docs/apache-airflow/2.11.0/configurations-ref.html#auth-backends
- Apache Airflow singular API authentication setting and deny-all default (2.2.5 documentation): https://airflow.apache.org/docs/apache-airflow/2.2.5/configurations-ref.html#auth-backend
- Apache Airflow Simple Auth Manager all-admin authentication bypass (3.3.2 documentation): https://airflow.apache.org/docs/apache-airflow/3.3.2/configurations-ref.html#simple-auth-manager-all-admins
- Apache Airflow public API JWT authentication (3.3.2 documentation): https://airflow.apache.org/docs/apache-airflow/3.3.2/security/api.html
- Apache Airflow development Compose FAB selection, administrator credentials and JWT fallback secret (pinned tag 3.3.2): https://raw.githubusercontent.com/apache/airflow/3.3.2/airflow-core/docs/howto/docker-compose/docker-compose.yaml
- Apache Airflow webserver secret_key and EXPOSE_CONFIG settings (2.11.0 documentation): https://airflow.apache.org/docs/apache-airflow/2.11.0/configurations-ref.html#secret-key, https://airflow.apache.org/docs/apache-airflow/2.11.0/configurations-ref.html#expose-config
- Apache Airflow API secret_key and EXPOSE_CONFIG settings (3.3.2 documentation): https://airflow.apache.org/docs/apache-airflow/3.3.2/configurations-ref.html#secret-key, https://airflow.apache.org/docs/apache-airflow/3.3.2/configurations-ref.html#expose-config


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- prefect: Prefect Basic Auth minimum (3.1.8)
- dagster: Dagster OSS (1.13.24)
- airflow: Apache Airflow (3.3.2)
- temporal-codec: Temporal Go SDK codec source (v1.28.0)
- flower: Flower (v2.2.0)
- argo-three: Argo Workflows (v3.7.18)
- argo-four: Argo Workflows (v4.1.4)
- prefect-blocks: Prefect Blocks source (3.1.8)
- airflow-two: Apache Airflow historical configuration (2.11.0)
- airflow-old: Apache Airflow historical default (2.2.5)
- fab-source: Apache Airflow FAB provider source (providers-fab/3.9.0)
- airflow-crypto: Apache Airflow crypto source (3.3.2)
- argo-docs: Argo Workflows documentation (release-3.7)
- prefect-source: Prefect server source (9e560c9b6df4e19a5109a66e66d461f9facb538d)
- prefect-rolling: Prefect documentation (rolling) (unknown)
- dagster-rolling: Dagster documentation (rolling) (unknown)
- airflow-rolling: Apache Airflow documentation (rolling) (unknown)
- fab-rolling: Apache Airflow FAB provider documentation (rolling) (unknown)
- temporal-rolling: Temporal documentation (rolling) (unknown)
- flower-rolling: Flower documentation (rolling) (unknown)
- tornado: Tornado (v6.5.10)
- docker: Moby Docker (docker-v29.8.1)
- linux: Linux permissions and tools (unknown)
- systemd: systemd (v257)
- fhs: Filesystem Hierarchy Standard (3.0)
- iproute2: iproute2 ss manual (v6.15.0)
- network-namespaces: Linux network namespaces manual (man-pages-5.13)

Claims (full source mapping in the JSON block below):

- fronting (REASONED; airflow, argo-docs, temporal-rolling): Keep UI/API origins private behind HTTPS and authentication; use IdP MFA for browsers and separate machine authentication, and constrain worker egress.
- prefect-auth (REASONED; prefect, prefect-rolling): Self-hosted Prefect defaults unauthenticated; Basic Auth from 3.1.8 uses matching server/client auth strings and prompts the UI.
- prefect-key (REASONED; prefect, prefect-rolling): Cloud-only PREFECT_API_KEY takes precedence over PREFECT_API_AUTH_STRING and produces 401 against a self-hosted server.
- prefect-secrets (REASONED; prefect-blocks, prefect-rolling): Protect the auth string and credential-bearing Blocks; Prefect 3.1.8 block-document read routes accept include_secrets, and Secret.get() returns the underlying value. Restrict API and worker access; UI masking does not enforce authorization.
- prefect-port (REASONED; prefect-rolling): The self-hosted Prefect server uses port 4200.
- dagster-bind (REASONED; dagster): Direct dagster-webserver/dev defaults to 127.0.0.1:3000, with flag/environment overrides and free-port fallback when the port is unset or 0; explicitly bind the private origin.
- dagster-helm (REASONED; dagster): The chart passes -h 0.0.0.0 on the Service port, default 80, with ClusterIP Service by default.
- dagster-auth (REASONED; dagster-rolling): OSS webserver has no built-in login or access control; protect all routes with an authenticating proxy.
- airflow-boundary (REASONED; airflow): Airflow assumes authenticated known users and is not designed for untrusted public exposure; deployment managers must keep it private.
- airflow-two-api (REASONED; airflow-two, airflow-old): Airflow 2.11.0 uses [api] auth_backends with session default; before 2.3 the name was auth_backend and 2.2.5 defaulted to deny_all.
- airflow-simple (REASONED; airflow): Airflow 3 defaults to development-only Simple Auth Manager, with configured users/roles and generated passwords printed to logs unless supplied.
- airflow-fab (REASONED; airflow, fab-rolling): For production install FAB and select FabAuthManager through [core] auth_manager; verify the effective manager and use an identity backend with MFA.
- airflow-api (REASONED; airflow, fab-rolling): Airflow 3 public API uses JWT independently of [fab] auth_backends, which selects FAB API backends rather than the auth manager.
- airflow-all-admins (REASONED; airflow): Keep simple_auth_manager_all_admins unset or False; enabling it disables login and grants every visitor admin.
- fab-public-role (REASONED; fab-source): Leave [fab] auth_role_public and legacy AUTH_ROLE_PUBLIC unset; a configured public role can make FAB treat an anonymous visitor as logged in and supply that role's permissions.
- airflow-compose-account (REASONED; airflow-rolling, fab-rolling, airflow): Development Compose selects FAB but defaults to airflow/airflow; set credentials before account creation and update/delete an existing account separately.
- airflow-jwt (REASONED; airflow-rolling, airflow): Replace Compose fallback AIRFLOW__API_AUTH__JWT_SECRET=airflow_jwt_secret and share the strong value with all signers/validators; the public fallback permits token forgery.
- airflow-secret-key (REASONED; airflow-two, airflow-rolling, airflow): Provision the independent secret_key too: [webserver] on 2.11.0 and [api] on 3.3.2.
- airflow-config (REASONED; airflow-two, airflow-rolling, airflow): Keep configuration exposure off with WEBSERVER__EXPOSE_CONFIG on 2.11.0 or API__EXPOSE_CONFIG on 3.3.2.
- airflow-fernet (REASONED; airflow-crypto, airflow-rolling): Protect Connections, Variables, database and Fernet keys; an empty [core] FERNET_KEY selects a no-encryption implementation for new values, while configured comma-separated keys use MultiFernet. Preserve keys needed to decrypt existing values; authorized workloads still use secrets.
- airflow-port (REASONED; airflow-rolling): Compose publishes 8080 on all interfaces; use 127.0.0.1:8080:8080 behind the fronting layer.
- temporal-authorizer (REASONED; temporal-rolling): Empty authorizer selects noopAuthorizer allowing every API request, including administration; configure default authorization with trusted JWT keys and audience.
- temporal-claims (REASONED; temporal-rolling): Empty claimMapper selects a no-op granting system-admin claims; configure both Authorizer and ClaimMapper, with frontend TLS.
- temporal-health (REASONED; temporal-rolling): The built-in default authorizer permits health checks without claims; health is not an authorization discriminator.
- temporal-ui (REASONED; temporal-rolling): UI OIDC auth.enabled is a sibling of providers; TEMPORAL_AUTH_ENABLED plus provider settings gates the UI only, with MFA at the IdP.
- temporal-tls (REASONED; temporal-rolling): Internode and frontend mTLS are separate from UI login and API authorization.
- temporal-payloads (REASONED; temporal-rolling, temporal-codec): Keep plaintext credentials out of persisted inputs/results/history; the Temporal Go SDK v1.28.0 codec HTTP handler accepts encode/decode POSTs without an authentication check, so authenticate and restrict a deployed Codec Server separately.
- temporal-ports (REASONED; temporal-rolling): Frontend gRPC uses 7233 and the Web UI 8233 in the cited CLI server reference.
- flower-bind (REASONED; flower, tornado): Flower defaults to wildcard address and 5555 unless Unix socket, FLOWER_ variables or implicit working-directory flowerconfig.py override; bind loopback explicitly.
- flower-api (REASONED; flower-rolling): Authentication defaults off; unauthenticated HTTP API is disabled unless FLOWER_UNAUTHENTICATED_API=true, which must not be mistaken for dashboard protection.
- flower-basic (REASONED; flower-rolling): Basic auth uses a comma-separated credential list; supply it through FLOWER_BASIC_AUTH or protected config rather than argv and retain private TLS fronting.
- flower-oauth (REASONED; flower-rolling): OAuth needs handler, client key/secret, redirect and allowed-email regex; protect the secret outside argv and prefer an MFA-enforcing provider.
- flower-socket (REASONED; flower, tornado, linux): Flower passes fixed mode 0777; Tornado removes/recreates filesystem sockets on startup, so chmod does not persist. Abstract sockets have no filesystem permission boundary.
- flower-directory (REASONED; linux): Restrict socket directory search with Flower ownership, proxy-only group, mode 0750 and no outsider ACL; directory access is essential because socket mode permits writes.
- flower-capabilities (REASONED; linux, docker): Applicable DAC capabilities bypass directory search checks; Docker defaults include CAP_DAC_OVERRIDE, while user namespaces and idmapped mounts change identity interpretation.
- flower-runtime-dir (REASONED; systemd, fhs): Reapply directory owner/group/mode on creation: /run is cleared at boot and RuntimeDirectory defaults 0755 unless RuntimeDirectoryMode overrides it.
- flower-numeric-ids (REASONED; linux): A proxy sharing the socket directory must hold the required numeric group after namespace/mount mappings; names alone do not establish access.
- argo-bind (REASONED; argo-three, argo-four): Argo Server binds wildcard :2746 with host-dependent IPv4/IPv6 support and no bind-address flag.
- argo-defaults (REASONED; argo-three, argo-four): Both tags default secure=true, auth-mode=client and hsts=true; flags and ARGO_ environment equivalents can override.
- argo-client (REASONED; argo-three, argo-four): Client mode uses caller Kubernetes credentials/RBAC; v4.1.4 validates via SelfSubjectReview and requires Kubernetes 1.28+.
- argo-quickstart (REASONED; argo-three, argo-four): Both tags' minimal/mysql/postgres quick-starts enable server plus client mode while retaining TLS; v4.1.4 telemetry does too. Anonymous callers inherit server permissions.
- argo-quickstart-rbac (REASONED; argo-three, argo-four): Quick-start binds cluster-wide workflow/template and Secret get/create permissions, plus cluster-workflow-template rights; it is demo-only.
- argo-installs (REASONED; argo-three, argo-four): Traced install inputs keep client auth/TLS with cluster-wide server RBAC; namespace-install adds --namespaced and namespace RBAC. Generated install YAML was absent.
- argo-service (REASONED; argo-three, argo-four): Base Service omits type, defaulting to ClusterIP, and maps 2746 to 2746; this does not authenticate reachable callers.
- argo-fallback (REASONED; argo-three, argo-four): Remove server auth mode: adding client/SSO does not prevent anonymous fallback to server credentials; local mode uses the server kubeconfig.
- argo-sso (REASONED; argo-docs, argo-three, argo-four): Enable sso.rbac.enabled and map groups to narrow ServiceAccounts through rbac-rule/precedence; without SSO RBAC, authenticated users share server permissions.
- argo-secrets (REASONED; argo-docs): Store SSO OAuth credentials in referenced Kubernetes Secrets and supply API tokens through protected input, not argv.
- argo-tls (REASONED; argo-three, argo-four): Keep TLS enabled with a trusted certificate Secret; no name generates a self-signed certificate, failed named-Secret loading fails startup, secure=false is plaintext and defeats HSTS.
- argo-metrics (REASONED; argo-three, argo-four): /metrics shares the server listener and auth gate unless ARGO_SERVER_METRICS_AUTH=false; server mode also admits anonymous metrics.
- argo-network (REASONED; argo-docs): Keep 2746 private behind authenticated HTTPS; restrict direct Pod/Service access and scope server, SSO and execution-account permissions. Workflow submission permits arbitrary containers unless constrained.
- verify-inventory (REASONED; flower, argo-three, iproute2, network-namespaces, prefect-rolling): ss inventories only the current namespace, not publication, routing or authentication; inspect publications and external reachability separately.
- verify-prefect (REASONED; prefect, prefect-source, prefect-rolling): Anonymous POST /api/flows/filter returning a JSON list is exposed; fixed is 401 with an authorized list on the same origin. Health/ready GET exemptions are version-dependent.
- verify-dagster (REASONED; dagster-rolling): A RepositoryConnection from /graphql is a read, including empty nodes; GraphQL/transport errors are inconclusive. Test proxy authentication and origin isolation separately.
- verify-airflow (REASONED; airflow-two, airflow-rolling, fab-rolling): FAB 3.9.0 returning 201 with access_token for airflow/airflow is exposed; pair a valid account and anonymous/authenticated API reads at proxy and origin. Airflow 2 uses its own API/auth.
- verify-temporal (REASONED; temporal-rolling): Credential-free workflow listing on 7233 is exposed; require rejection and a matched authorized call, not health, TLS errors or missing namespaces as proof of auth.
- verify-flower (REASONED; flower-rolling): Anonymous UI/API should yield Basic 401 or OAuth login redirect, with a valid-session control; API-disabled is not proof the dashboard is protected.
- verify-socket (REASONED; flower, linux): Directory/socket permissions, outsider denial, reboot persistence and container numeric IDs remain reasoned; no socket or Flower process ran.
- flower-stat-run (DEMONSTRATED; linux): Tmpfs directory-only stat distinguished 0755 and 0750; the 0750 directory initially had only base ACL entries.
- flower-acl-run (DEMONSTRATED; linux): A named nobody search ACL remained invisible in stat mode 750; ls and getfacl exposed the entry.
- flower-mask-run (DEMONSTRATED; linux): Changing the ACL mask hid named search permission; chmod 0750 restored its reported effectiveness. Access as nobody was not tested.
- verify-argo (REASONED; argo-three, argo-four, argo-docs): Anonymous workflow JSON is exposed when server RBAC permits; missing tokens should yield 401 without server mode. A 403 alone is inconclusive; pair authorized 200 and inspect auth modes.
- verify-origin (REASONED; airflow, argo-docs): Any HTTP response from the origin at an untrusted vantage proves publication; use the same responding allowed origin as control and treat connection errors/timeouts as inconclusive.

````json
{
  "schema": 1,
  "checked": "2026-10-05",
  "documentation_checked": "2026-10",
  "body_sha256": "7ee8cb8f3bb228a511d5acdd308e432758300b180eba9d74959d5fb637feaa62",
  "components": {
    "prefect": {
      "name": "Prefect Basic Auth minimum",
      "basis": "3.1.8",
      "sources": {
        "s12416d1a0d69": "https://github.com/PrefectHQ/prefect/releases/tag/3.1.8"
      }
    },
    "dagster": {
      "name": "Dagster OSS",
      "basis": "1.13.24",
      "sources": {
        "sab1b42d92f27": "https://github.com/dagster-io/dagster/blob/1.13.24/python_modules/dagster-webserver/dagster_webserver/cli.py#L41-L42",
        "s6bc57f86dfe1": "https://github.com/dagster-io/dagster/blob/1.13.24/python_modules/dagster-webserver/dagster_webserver/cli.py#L81-L96",
        "s2455602a504b": "https://github.com/dagster-io/dagster/blob/1.13.24/python_modules/dagster-webserver/dagster_webserver/cli.py#L306-L311",
        "s3c7d8f17f245": "https://github.com/dagster-io/dagster/blob/1.13.24/python_modules/dagster/dagster/_cli/dev.py#L251-L252",
        "s469c458c4a71": "https://github.com/dagster-io/dagster/blob/1.13.24/python_modules/dagster-webserver/dagster_webserver/cli.py#L339-L351",
        "s695dfd19dcca": "https://github.com/dagster-io/dagster/blob/1.13.24/helm/dagster/templates/helpers/_deployment-webserver.tpl#L86-L90",
        "sf6f027e96a0d": "https://github.com/dagster-io/dagster/blob/1.13.24/helm/dagster/templates/helpers/_helpers.tpl#L55",
        "seda3a1b24425": "https://github.com/dagster-io/dagster/blob/1.13.24/helm/dagster/values.yaml#L54-L58"
      }
    },
    "airflow": {
      "name": "Apache Airflow",
      "basis": "3.3.2",
      "sources": {
        "s1d0b86fe4334": "https://airflow.apache.org/docs/apache-airflow/3.3.2/security/security_model.html",
        "sad02a49561a0": "https://airflow.apache.org/docs/apache-airflow/3.3.2/core-concepts/auth-manager/simple/index.html",
        "s3be3e4616150": "https://airflow.apache.org/docs/apache-airflow/3.3.2/core-concepts/auth-manager/index.html",
        "s78c661193a1a": "https://airflow.apache.org/docs/apache-airflow/3.3.2/configurations-ref.html#simple-auth-manager-all-admins",
        "s963b49f58a13": "https://airflow.apache.org/docs/apache-airflow/3.3.2/security/api.html",
        "s705f1eb5de00": "https://raw.githubusercontent.com/apache/airflow/3.3.2/airflow-core/docs/howto/docker-compose/docker-compose.yaml",
        "sdfcfd543928c": "https://airflow.apache.org/docs/apache-airflow/3.3.2/configurations-ref.html#secret-key",
        "s4ed64009ed8f": "https://airflow.apache.org/docs/apache-airflow/3.3.2/configurations-ref.html#expose-config"
      }
    },
    "temporal-codec": {
      "name": "Temporal Go SDK codec source",
      "basis": "v1.28.0",
      "sources": {
        "s24435f531da0": "https://github.com/temporalio/sdk-go/blob/v1.28.0/converter/codec.go#L284-L350"
      }
    },
    "flower": {
      "name": "Flower",
      "basis": "v2.2.0",
      "sources": {
        "s25760fae7152": "https://github.com/mher/flower/blob/v2.2.0/flower/options.py#L7-L15",
        "s1f72a8415337": "https://github.com/mher/flower/blob/v2.2.0/flower/options.py#L56-L57",
        "s4dd518442b7f": "https://github.com/mher/flower/blob/v2.2.0/flower/command.py#L39-L91",
        "s4e49ebc71dc1": "https://github.com/mher/flower/blob/v2.2.0/flower/app.py#L71-L76",
        "s0fe6c77e9c9d": "https://github.com/mher/flower/blob/v2.2.0/flower/app.py#L85-L89"
      }
    },
    "argo-three": {
      "name": "Argo Workflows",
      "basis": "v3.7.18",
      "sources": {
        "s262098553d2f": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/cmd/argo/commands/server.go#L191-L229",
        "sbddb9f07a301": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/server/apiserver/argoserver.go#L263-L282",
        "s2ca4f14c3164": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/server/auth/gatekeeper.go#L166-L218",
        "sfbb904619bfa": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/quick-start/base/overlays/argo-server-deployment.yaml#L1-L15",
        "s0ac72aa1a86c": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/cluster-install-no-crds/argo-server-rbac/argo-server-clusterole.yaml#L1-L65",
        "s1689f25010be": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/quick-start/base/cluster-workflow-template-rbac.yaml#L1-L58",
        "sf0c3a52d3302": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/Makefile#L493-L515",
        "sfdcdf614ee37": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/base/argo-server/argo-server-deployment.yaml#L14-L34",
        "sc7ca3a37b16c": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/namespace-install/overlays/argo-server-deployment.yaml#L1-L4",
        "s01f102470d97": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/base/argo-server/argo-server-service.yaml#L1-L11",
        "s49cdaf0691c0": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/server/auth/mode.go#L33-L44",
        "sdb4a0c18b7c6": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/cmd/argo/commands/server.go#L113-L137",
        "s36759aec55fa": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/server/apiserver/argoserver.go#L430-L449",
        "s862033e52c9b": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/quick-start-minimal.yaml#L3613-L3664",
        "s73e9beeef775": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/quick-start-mysql.yaml#L3678-L3729",
        "s476ff15db454": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/quick-start-postgres.yaml#L3677-L3728",
        "sa4b2fa875915": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/cluster-install-no-crds/argo-server-rbac/argo-server-clusterolebinding.yaml#L1-L11",
        "s48db5ba07d23": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/quick-start/base/kustomization.yaml#L4-L5",
        "se3ffdf2973a6": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/namespace-install/argo-server-rbac/argo-server-role.yaml#L1-L65",
        "sb901e7f87b54": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/manifests/namespace-install/argo-server-rbac/argo-server-rolebinding.yaml#L1-L11",
        "s49a8855b6da2": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/docs/argo-server-auth-mode.md#L3-L9",
        "s64e74b0dbe95": "https://github.com/argoproj/argo-workflows/blob/v3.7.18/server/auth/gatekeeper.go#L106-L121"
      }
    },
    "argo-four": {
      "name": "Argo Workflows",
      "basis": "v4.1.4",
      "sources": {
        "s774215022573": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/cmd/argo/commands/server.go#L195-L239",
        "s0f074a9ac21e": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/server/apiserver/argoserver.go#L299-L320",
        "sb284f93cde9c": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/server/auth/gatekeeper.go#L189-L244",
        "s0871a1dd9b13": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/docs/argo-server-auth-mode.md#L3-L9",
        "sa7b9db8384be": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/quick-start/base/overlays/argo-server-deployment.yaml#L1-L15",
        "s79648b46d3f5": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/quick-start-telemetry.yaml#L192919-L192970",
        "sd2706d04971d": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/cluster-install-no-crds/argo-server-rbac/argo-server-clusterole.yaml#L1-L67",
        "sd920da4ad4b7": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/docs/quick-start.md#L3-L34",
        "s144b824252c1": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/Makefile#L608-L634",
        "s51645bfbc47c": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/base/argo-server/argo-server-deployment.yaml#L14-L34",
        "s5188f6f2efbb": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/namespace-install/overlays/argo-server-deployment.yaml#L1-L4",
        "s639e9fe0024e": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/base/argo-server/argo-server-service.yaml#L1-L11",
        "s4613c15c72af": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/server/auth/mode.go#L33-L44",
        "s0b16f1ac50df": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/cmd/argo/commands/server.go#L119-L143",
        "sa120f74372eb": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/server/apiserver/argoserver.go#L476-L494",
        "s6c08a5f34f2c": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/quick-start-minimal.yaml#L192772-L192823",
        "sa0bf6187d1db": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/quick-start-mysql.yaml#L192838-L192889",
        "s31f4a149576b": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/quick-start-postgres.yaml#L192837-L192888",
        "s3be9b03e29be": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/cluster-install-no-crds/argo-server-rbac/argo-server-clusterolebinding.yaml#L1-L11",
        "sc263bd937cf0": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/quick-start/base/kustomization.yaml#L4-L5",
        "s1b134f96428f": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/namespace-install/argo-server-rbac/argo-server-role.yaml#L1-L67",
        "s2418ee1aa49d": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/manifests/namespace-install/argo-server-rbac/argo-server-rolebinding.yaml#L1-L11",
        "se758d83aaf1f": "https://github.com/argoproj/argo-workflows/blob/v4.1.4/server/auth/gatekeeper.go#L133-L148"
      }
    },
    "prefect-blocks": {
      "name": "Prefect Blocks source",
      "basis": "3.1.8",
      "sources": {
        "s56081101d16a": "https://github.com/PrefectHQ/prefect/blob/3.1.8/src/prefect/server/api/block_documents.py#L47-L70",
        "s1eae2c5f9f5e": "https://github.com/PrefectHQ/prefect/blob/3.1.8/src/prefect/server/api/block_documents.py#L101-L119",
        "s46e69a2090c4": "https://github.com/PrefectHQ/prefect/blob/3.1.8/src/prefect/blocks/system.py#L154-L159"
      }
    },
    "airflow-two": {
      "name": "Apache Airflow historical configuration",
      "basis": "2.11.0",
      "sources": {
        "sb97f3044e215": "https://airflow.apache.org/docs/apache-airflow/2.11.0/configurations-ref.html#auth-backends",
        "sabb71378ad74": "https://airflow.apache.org/docs/apache-airflow/2.11.0/configurations-ref.html#secret-key",
        "s6813801b7880": "https://airflow.apache.org/docs/apache-airflow/2.11.0/configurations-ref.html#expose-config"
      }
    },
    "airflow-old": {
      "name": "Apache Airflow historical default",
      "basis": "2.2.5",
      "sources": {
        "s4e72b1f51038": "https://airflow.apache.org/docs/apache-airflow/2.2.5/configurations-ref.html#auth-backend"
      }
    },
    "fab-source": {
      "name": "Apache Airflow FAB provider source",
      "basis": "providers-fab/3.9.0",
      "sources": {
        "s3c94f0f7176a": "https://github.com/apache/airflow/blob/providers-fab/3.9.0/providers/fab/src/airflow/providers/fab/auth_manager/fab_auth_manager.py#L327-L381",
        "s5552a28ab9d8": "https://github.com/apache/airflow/blob/providers-fab/3.9.0/providers/fab/pyproject.toml#L75-L81"
      }
    },
    "airflow-crypto": {
      "name": "Apache Airflow crypto source",
      "basis": "3.3.2",
      "sources": {
        "sdeaf2f54c054": "https://github.com/apache/airflow/blob/3.3.2/airflow-core/src/airflow/models/crypto.py#L47-L68",
        "s70ea7631e820": "https://github.com/apache/airflow/blob/3.3.2/airflow-core/src/airflow/models/crypto.py#L154-L173"
      }
    },
    "argo-docs": {
      "name": "Argo Workflows documentation",
      "basis": "release-3.7",
      "sources": {
        "s6c8e78288632": "https://argo-workflows.readthedocs.io/en/release-3.7/security/",
        "s9898d4653a47": "https://argo-workflows.readthedocs.io/en/release-3.7/argo-server-sso/",
        "s96145eacf345": "https://argo-workflows.readthedocs.io/en/release-3.7/rest-examples/"
      }
    },
    "prefect-source": {
      "name": "Prefect server source",
      "basis": "9e560c9b6df4e19a5109a66e66d461f9facb538d",
      "sources": {
        "sa4574c7ed80f": "https://github.com/PrefectHQ/prefect/blob/9e560c9b6df4e19a5109a66e66d461f9facb538d/src/prefect/server/api/server.py"
      }
    },
    "prefect-rolling": {
      "name": "Prefect documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "sbe64d51110a2": "https://docs.prefect.io/v3/how-to-guides/self-hosted/server-cli",
        "s0ef73a227667": "https://docs.prefect.io/v3/advanced/security-settings"
      }
    },
    "dagster-rolling": {
      "name": "Dagster documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s4c04d5da5257": "https://docs.dagster.io/guides/operate/webserver"
      }
    },
    "airflow-rolling": {
      "name": "Apache Airflow documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s2d1891641c91": "https://airflow.apache.org/docs/apache-airflow/stable/security/",
        "s39bfd91c507b": "https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html"
      }
    },
    "fab-rolling": {
      "name": "Apache Airflow FAB provider documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s989f09d05161": "https://airflow.apache.org/docs/apache-airflow-providers-fab/stable/auth-manager/api-authentication.html"
      }
    },
    "temporal-rolling": {
      "name": "Temporal documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s12f2c64ad396": "https://docs.temporal.io/cli/command-reference/server",
        "s06d4f0dbd0c8": "https://docs.temporal.io/self-hosted-guide/security",
        "sa9d5614385ca": "https://docs.temporal.io/references/web-ui-configuration"
      }
    },
    "flower-rolling": {
      "name": "Flower documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "sb1ba69f79c9b": "https://flower.readthedocs.io/en/latest/config.html"
      }
    },
    "tornado": {
      "name": "Tornado",
      "basis": "v6.5.10",
      "sources": {
        "sc503b4425831": "https://github.com/tornadoweb/tornado/blob/v6.5.10/tornado/netutil.py#L72-L73",
        "s737c51cccd00": "https://github.com/tornadoweb/tornado/blob/v6.5.10/tornado/netutil.py#L215-L228"
      }
    },
    "docker": {
      "name": "Moby Docker",
      "basis": "docker-v29.8.1",
      "sources": {
        "s1f268e247a1f": "https://github.com/moby/moby/blob/docker-v29.8.1/daemon/pkg/oci/caps/defaults.go#L4-L7"
      }
    },
    "linux": {
      "name": "Linux permissions and tools",
      "basis": "unknown",
      "sources": {
        "s8ffd93b0efa4": "https://man7.org/linux/man-pages/man7/unix.7.html",
        "sfb53d2819cd0": "https://man7.org/linux/man-pages/man7/path_resolution.7.html",
        "s31f41c54750c": "https://man7.org/linux/man-pages/man5/acl.5.html",
        "s3cf3d5be0f64": "https://man7.org/linux/man-pages/man7/user_namespaces.7.html",
        "sa5ccbfea6e16": "https://www.kernel.org/doc/html/latest/filesystems/idmappings.html",
        "s08902025e5f9": "https://man7.org/linux/man-pages/man1/getfacl.1.html",
        "sa0d3793fabb7": "https://man7.org/linux/man-pages/man1/stat.1.html"
      }
    },
    "systemd": {
      "name": "systemd",
      "basis": "v257",
      "sources": {
        "s48ece26c16d3": "https://github.com/systemd/systemd/blob/v257/man/systemd.exec.xml#L1630-L1640"
      }
    },
    "fhs": {
      "name": "Filesystem Hierarchy Standard",
      "basis": "3.0",
      "sources": {
        "seafd8219f367": "https://refspecs.linuxfoundation.org/FHS_3.0/fhs/ch03s15.html"
      }
    },
    "iproute2": {
      "name": "iproute2 ss manual",
      "basis": "v6.15.0",
      "sources": {
        "s6cc7f285a0c7": "https://github.com/iproute2/iproute2/blob/v6.15.0/man/man8/ss.8#L358-L359",
        "s9fa9a260f1de": "https://github.com/iproute2/iproute2/blob/v6.15.0/man/man8/ss.8#L7-L12"
      }
    },
    "network-namespaces": {
      "name": "Linux network namespaces manual",
      "basis": "man-pages-5.13",
      "sources": {
        "s427c923e346f": "https://github.com/mkerrisk/man-pages/blob/man-pages-5.13/man7/network_namespaces.7#L30-L40"
      }
    }
  },
  "claims": {
    "fronting": {"text": "Keep UI/API origins private behind HTTPS and authentication; use IdP MFA for browsers and separate machine authentication, and constrain worker egress.", "components": ["airflow", "argo-docs", "temporal-rolling"], "sources": ["airflow:s1d0b86fe4334", "temporal-rolling:s06d4f0dbd0c8", "argo-docs:s6c8e78288632"], "status": "REASONED"},
    "prefect-auth": {"text": "Self-hosted Prefect defaults unauthenticated; Basic Auth from 3.1.8 uses matching server/client auth strings and prompts the UI.", "components": ["prefect", "prefect-rolling"], "sources": ["prefect:s12416d1a0d69", "prefect-rolling:s0ef73a227667"], "status": "REASONED"},
    "prefect-key": {"text": "Cloud-only PREFECT_API_KEY takes precedence over PREFECT_API_AUTH_STRING and produces 401 against a self-hosted server.", "components": ["prefect", "prefect-rolling"], "sources": ["prefect:s12416d1a0d69", "prefect-rolling:s0ef73a227667"], "status": "REASONED"},
    "prefect-secrets": {"text": "Protect the auth string and credential-bearing Blocks; Prefect 3.1.8 block-document read routes accept include_secrets, and Secret.get() returns the underlying value. Restrict API and worker access; UI masking does not enforce authorization.", "components": ["prefect-blocks", "prefect-rolling"], "sources": ["prefect-blocks:s56081101d16a", "prefect-blocks:s1eae2c5f9f5e", "prefect-blocks:s46e69a2090c4", "prefect-rolling:s0ef73a227667"], "status": "REASONED"},
    "prefect-port": {"text": "The self-hosted Prefect server uses port 4200.", "components": ["prefect-rolling"], "sources": ["prefect-rolling:sbe64d51110a2"], "status": "REASONED"},
    "dagster-bind": {"text": "Direct dagster-webserver/dev defaults to 127.0.0.1:3000, with flag/environment overrides and free-port fallback when the port is unset or 0; explicitly bind the private origin.", "components": ["dagster"], "sources": ["dagster:sab1b42d92f27", "dagster:s6bc57f86dfe1", "dagster:s2455602a504b", "dagster:s3c7d8f17f245", "dagster:s469c458c4a71"], "status": "REASONED"},
    "dagster-helm": {"text": "The chart passes -h 0.0.0.0 on the Service port, default 80, with ClusterIP Service by default.", "components": ["dagster"], "sources": ["dagster:s695dfd19dcca", "dagster:sf6f027e96a0d", "dagster:seda3a1b24425"], "status": "REASONED"},
    "dagster-auth": {"text": "OSS webserver has no built-in login or access control; protect all routes with an authenticating proxy.", "components": ["dagster-rolling"], "sources": ["dagster-rolling:s4c04d5da5257"], "status": "REASONED"},
    "airflow-boundary": {"text": "Airflow assumes authenticated known users and is not designed for untrusted public exposure; deployment managers must keep it private.", "components": ["airflow"], "sources": ["airflow:s1d0b86fe4334"], "status": "REASONED"},
    "airflow-two-api": {"text": "Airflow 2.11.0 uses [api] auth_backends with session default; before 2.3 the name was auth_backend and 2.2.5 defaulted to deny_all.", "components": ["airflow-two", "airflow-old"], "sources": ["airflow-two:sb97f3044e215", "airflow-old:s4e72b1f51038"], "status": "REASONED"},
    "airflow-simple": {"text": "Airflow 3 defaults to development-only Simple Auth Manager, with configured users/roles and generated passwords printed to logs unless supplied.", "components": ["airflow"], "sources": ["airflow:sad02a49561a0", "airflow:s3be3e4616150"], "status": "REASONED"},
    "airflow-fab": {"text": "For production install FAB and select FabAuthManager through [core] auth_manager; verify the effective manager and use an identity backend with MFA.", "components": ["airflow", "fab-rolling"], "sources": ["airflow:s3be3e4616150", "fab-rolling:s989f09d05161"], "status": "REASONED"},
    "airflow-api": {"text": "Airflow 3 public API uses JWT independently of [fab] auth_backends, which selects FAB API backends rather than the auth manager.", "components": ["airflow", "fab-rolling"], "sources": ["airflow:s3be3e4616150", "fab-rolling:s989f09d05161", "airflow:s963b49f58a13"], "status": "REASONED"},
    "airflow-all-admins": {"text": "Keep simple_auth_manager_all_admins unset or False; enabling it disables login and grants every visitor admin.", "components": ["airflow"], "sources": ["airflow:sad02a49561a0", "airflow:s78c661193a1a"], "status": "REASONED"},
    "fab-public-role": {"text": "Leave [fab] auth_role_public and legacy AUTH_ROLE_PUBLIC unset; a configured public role can make FAB treat an anonymous visitor as logged in and supply that role's permissions.", "components": ["fab-source"], "sources": ["fab-source:s3c94f0f7176a", "fab-source:s5552a28ab9d8"], "status": "REASONED"},
    "airflow-compose-account": {"text": "Development Compose selects FAB but defaults to airflow/airflow; set credentials before account creation and update/delete an existing account separately.", "components": ["airflow-rolling", "fab-rolling", "airflow"], "sources": ["airflow-rolling:s39bfd91c507b", "fab-rolling:s989f09d05161", "airflow:s705f1eb5de00"], "status": "REASONED"},
    "airflow-jwt": {"text": "Replace Compose fallback AIRFLOW__API_AUTH__JWT_SECRET=airflow_jwt_secret and share the strong value with all signers/validators; the public fallback permits token forgery.", "components": ["airflow-rolling", "airflow"], "sources": ["airflow-rolling:s39bfd91c507b", "airflow:s705f1eb5de00"], "status": "REASONED"},
    "airflow-secret-key": {"text": "Provision the independent secret_key too: [webserver] on 2.11.0 and [api] on 3.3.2.", "components": ["airflow-two", "airflow-rolling", "airflow"], "sources": ["airflow-rolling:s2d1891641c91", "airflow-two:sabb71378ad74", "airflow:sdfcfd543928c"], "status": "REASONED"},
    "airflow-config": {"text": "Keep configuration exposure off with WEBSERVER__EXPOSE_CONFIG on 2.11.0 or API__EXPOSE_CONFIG on 3.3.2.", "components": ["airflow-two", "airflow-rolling", "airflow"], "sources": ["airflow-rolling:s2d1891641c91", "airflow-two:s6813801b7880", "airflow:s4ed64009ed8f"], "status": "REASONED"},
    "airflow-fernet": {"text": "Protect Connections, Variables, database and Fernet keys; an empty [core] FERNET_KEY selects a no-encryption implementation for new values, while configured comma-separated keys use MultiFernet. Preserve keys needed to decrypt existing values; authorized workloads still use secrets.", "components": ["airflow-crypto", "airflow-rolling"], "sources": ["airflow-crypto:sdeaf2f54c054", "airflow-crypto:s70ea7631e820", "airflow-rolling:s2d1891641c91"], "status": "REASONED"},
    "airflow-port": {"text": "Compose publishes 8080 on all interfaces; use 127.0.0.1:8080:8080 behind the fronting layer.", "components": ["airflow-rolling"], "sources": ["airflow-rolling:s39bfd91c507b"], "status": "REASONED"},
    "temporal-authorizer": {"text": "Empty authorizer selects noopAuthorizer allowing every API request, including administration; configure default authorization with trusted JWT keys and audience.", "components": ["temporal-rolling"], "sources": ["temporal-rolling:s06d4f0dbd0c8"], "status": "REASONED"},
    "temporal-claims": {"text": "Empty claimMapper selects a no-op granting system-admin claims; configure both Authorizer and ClaimMapper, with frontend TLS.", "components": ["temporal-rolling"], "sources": ["temporal-rolling:s06d4f0dbd0c8"], "status": "REASONED"},
    "temporal-health": {"text": "The built-in default authorizer permits health checks without claims; health is not an authorization discriminator.", "components": ["temporal-rolling"], "sources": ["temporal-rolling:s06d4f0dbd0c8"], "status": "REASONED"},
    "temporal-ui": {"text": "UI OIDC auth.enabled is a sibling of providers; TEMPORAL_AUTH_ENABLED plus provider settings gates the UI only, with MFA at the IdP.", "components": ["temporal-rolling"], "sources": ["temporal-rolling:sa9d5614385ca"], "status": "REASONED"},
    "temporal-tls": {"text": "Internode and frontend mTLS are separate from UI login and API authorization.", "components": ["temporal-rolling"], "sources": ["temporal-rolling:s06d4f0dbd0c8"], "status": "REASONED"},
    "temporal-payloads": {"text": "Keep plaintext credentials out of persisted inputs/results/history; the Temporal Go SDK v1.28.0 codec HTTP handler accepts encode/decode POSTs without an authentication check, so authenticate and restrict a deployed Codec Server separately.", "components": ["temporal-rolling", "temporal-codec"], "sources": ["temporal-rolling:s06d4f0dbd0c8", "temporal-codec:s24435f531da0"], "status": "REASONED"},
    "temporal-ports": {"text": "Frontend gRPC uses 7233 and the Web UI 8233 in the cited CLI server reference.", "components": ["temporal-rolling"], "sources": ["temporal-rolling:s12f2c64ad396"], "status": "REASONED"},
    "flower-bind": {"text": "Flower defaults to wildcard address and 5555 unless Unix socket, FLOWER_ variables or implicit working-directory flowerconfig.py override; bind loopback explicitly.", "components": ["flower", "tornado"], "sources": ["flower:s25760fae7152", "flower:s1f72a8415337", "flower:s4dd518442b7f", "flower:s4e49ebc71dc1", "tornado:sc503b4425831"], "status": "REASONED"},
    "flower-api": {"text": "Authentication defaults off; unauthenticated HTTP API is disabled unless FLOWER_UNAUTHENTICATED_API=true, which must not be mistaken for dashboard protection.", "components": ["flower-rolling"], "sources": ["flower-rolling:sb1ba69f79c9b"], "status": "REASONED"},
    "flower-basic": {"text": "Basic auth uses a comma-separated credential list; supply it through FLOWER_BASIC_AUTH or protected config rather than argv and retain private TLS fronting.", "components": ["flower-rolling"], "sources": ["flower-rolling:sb1ba69f79c9b"], "status": "REASONED"},
    "flower-oauth": {"text": "OAuth needs handler, client key/secret, redirect and allowed-email regex; protect the secret outside argv and prefer an MFA-enforcing provider.", "components": ["flower-rolling"], "sources": ["flower-rolling:sb1ba69f79c9b"], "status": "REASONED"},
    "flower-socket": {"text": "Flower passes fixed mode 0777; Tornado removes/recreates filesystem sockets on startup, so chmod does not persist. Abstract sockets have no filesystem permission boundary.", "components": ["flower", "tornado", "linux"], "sources": ["flower:s0fe6c77e9c9d", "tornado:s737c51cccd00", "linux:s8ffd93b0efa4"], "status": "REASONED"},
    "flower-directory": {"text": "Restrict socket directory search with Flower ownership, proxy-only group, mode 0750 and no outsider ACL; directory access is essential because socket mode permits writes.", "components": ["linux"], "sources": ["linux:sfb53d2819cd0", "linux:s8ffd93b0efa4", "linux:s31f41c54750c"], "status": "REASONED"},
    "flower-capabilities": {"text": "Applicable DAC capabilities bypass directory search checks; Docker defaults include CAP_DAC_OVERRIDE, while user namespaces and idmapped mounts change identity interpretation.", "components": ["linux", "docker"], "sources": ["linux:s3cf3d5be0f64", "linux:sa5ccbfea6e16", "docker:s1f268e247a1f"], "status": "REASONED"},
    "flower-runtime-dir": {"text": "Reapply directory owner/group/mode on creation: /run is cleared at boot and RuntimeDirectory defaults 0755 unless RuntimeDirectoryMode overrides it.", "components": ["systemd", "fhs"], "sources": ["systemd:s48ece26c16d3", "fhs:seafd8219f367"], "status": "REASONED"},
    "flower-numeric-ids": {"text": "A proxy sharing the socket directory must hold the required numeric group after namespace/mount mappings; names alone do not establish access.", "components": ["linux"], "sources": ["linux:s3cf3d5be0f64", "linux:sa5ccbfea6e16"], "status": "REASONED"},
    "argo-bind": {"text": "Argo Server binds wildcard :2746 with host-dependent IPv4/IPv6 support and no bind-address flag.", "components": ["argo-three", "argo-four"], "sources": ["argo-three:s262098553d2f", "argo-four:s774215022573", "argo-three:sbddb9f07a301", "argo-four:s0f074a9ac21e"], "status": "REASONED"},
    "argo-defaults": {"text": "Both tags default secure=true, auth-mode=client and hsts=true; flags and ARGO_ environment equivalents can override.", "components": ["argo-three", "argo-four"], "sources": ["argo-three:s262098553d2f", "argo-four:s774215022573"], "status": "REASONED"},
    "argo-client": {"text": "Client mode uses caller Kubernetes credentials/RBAC; v4.1.4 validates via SelfSubjectReview and requires Kubernetes 1.28+.", "components": ["argo-three", "argo-four"], "sources": ["argo-three:s2ca4f14c3164", "argo-four:sb284f93cde9c", "argo-four:s0871a1dd9b13"], "status": "REASONED"},
    "argo-quickstart": {"text": "Both tags' minimal/mysql/postgres quick-starts enable server plus client mode while retaining TLS; v4.1.4 telemetry does too. Anonymous callers inherit server permissions.", "components": ["argo-three", "argo-four"], "sources": ["argo-three:sfbb904619bfa", "argo-four:sa7b9db8384be", "argo-four:s79648b46d3f5", "argo-three:s862033e52c9b", "argo-three:s73e9beeef775", "argo-three:s476ff15db454", "argo-three:s262098553d2f", "argo-three:s49cdaf0691c0", "argo-three:s2ca4f14c3164", "argo-four:s6c08a5f34f2c", "argo-four:sa0bf6187d1db", "argo-four:s31f4a149576b", "argo-four:s774215022573", "argo-four:s4613c15c72af", "argo-four:sb284f93cde9c"], "status": "REASONED"},
    "argo-quickstart-rbac": {"text": "Quick-start binds cluster-wide workflow/template and Secret get/create permissions, plus cluster-workflow-template rights; it is demo-only.", "components": ["argo-three", "argo-four"], "sources": ["argo-three:s0ac72aa1a86c", "argo-four:sd2706d04971d", "argo-three:s1689f25010be", "argo-four:sd920da4ad4b7", "argo-three:sa4b2fa875915", "argo-three:s48db5ba07d23", "argo-four:s3be9b03e29be", "argo-four:sc263bd937cf0"], "status": "REASONED"},
    "argo-installs": {"text": "Traced install inputs keep client auth/TLS with cluster-wide server RBAC; namespace-install adds --namespaced and namespace RBAC. Generated install YAML was absent.", "components": ["argo-three", "argo-four"], "sources": ["argo-three:sf0c3a52d3302", "argo-four:s144b824252c1", "argo-three:sfdcdf614ee37", "argo-four:s51645bfbc47c", "argo-three:sc7ca3a37b16c", "argo-four:s5188f6f2efbb", "argo-three:s262098553d2f", "argo-three:s0ac72aa1a86c", "argo-three:sa4b2fa875915", "argo-three:se3ffdf2973a6", "argo-three:sb901e7f87b54", "argo-four:s774215022573", "argo-four:sd2706d04971d", "argo-four:s3be9b03e29be", "argo-four:s1b134f96428f", "argo-four:s2418ee1aa49d"], "status": "REASONED"},
    "argo-service": {"text": "Base Service omits type, defaulting to ClusterIP, and maps 2746 to 2746; this does not authenticate reachable callers.", "components": ["argo-three", "argo-four"], "sources": ["argo-three:s01f102470d97", "argo-four:s639e9fe0024e"], "status": "REASONED"},
    "argo-fallback": {"text": "Remove server auth mode: adding client/SSO does not prevent anonymous fallback to server credentials; local mode uses the server kubeconfig.", "components": ["argo-three", "argo-four"], "sources": ["argo-three:s49cdaf0691c0", "argo-four:s4613c15c72af", "argo-three:s2ca4f14c3164", "argo-four:sb284f93cde9c", "argo-four:s0871a1dd9b13", "argo-three:s49a8855b6da2"], "status": "REASONED"},
    "argo-sso": {"text": "Enable sso.rbac.enabled and map groups to narrow ServiceAccounts through rbac-rule/precedence; without SSO RBAC, authenticated users share server permissions.", "components": ["argo-docs", "argo-three", "argo-four"], "sources": ["argo-docs:s9898d4653a47", "argo-three:s2ca4f14c3164", "argo-four:sb284f93cde9c"], "status": "REASONED"},
    "argo-secrets": {"text": "Store SSO OAuth credentials in referenced Kubernetes Secrets and supply API tokens through protected input, not argv.", "components": ["argo-docs"], "sources": ["argo-docs:s9898d4653a47", "argo-docs:s96145eacf345"], "status": "REASONED"},
    "argo-tls": {"text": "Keep TLS enabled with a trusted certificate Secret; no name generates a self-signed certificate, failed named-Secret loading fails startup, secure=false is plaintext and defeats HSTS.", "components": ["argo-three", "argo-four"], "sources": ["argo-three:sdb4a0c18b7c6", "argo-four:s0b16f1ac50df", "argo-three:s36759aec55fa", "argo-four:sa120f74372eb"], "status": "REASONED"},
    "argo-metrics": {"text": "/metrics shares the server listener and auth gate unless ARGO_SERVER_METRICS_AUTH=false; server mode also admits anonymous metrics.", "components": ["argo-three", "argo-four"], "sources": ["argo-three:s36759aec55fa", "argo-four:sa120f74372eb", "argo-three:s49cdaf0691c0", "argo-three:s2ca4f14c3164", "argo-four:s4613c15c72af", "argo-four:sb284f93cde9c", "argo-three:s64e74b0dbe95", "argo-four:se758d83aaf1f"], "status": "REASONED"},
    "argo-network": {"text": "Keep 2746 private behind authenticated HTTPS; restrict direct Pod/Service access and scope server, SSO and execution-account permissions. Workflow submission permits arbitrary containers unless constrained.", "components": ["argo-docs"], "sources": ["argo-docs:s6c8e78288632"], "status": "REASONED"},
    "verify-inventory": {"text": "ss inventories only the current namespace, not publication, routing or authentication; inspect publications and external reachability separately.", "components": ["flower", "argo-three", "iproute2", "network-namespaces", "prefect-rolling"], "sources": ["prefect-rolling:sbe64d51110a2", "flower:s25760fae7152", "argo-three:sbddb9f07a301", "iproute2:s6cc7f285a0c7", "network-namespaces:s427c923e346f", "iproute2:s9fa9a260f1de"], "status": "REASONED", "verify": [1]},
    "verify-prefect": {"text": "Anonymous POST /api/flows/filter returning a JSON list is exposed; fixed is 401 with an authorized list on the same origin. Health/ready GET exemptions are version-dependent.", "components": ["prefect", "prefect-source", "prefect-rolling"], "sources": ["prefect:s12416d1a0d69", "prefect-source:sa4574c7ed80f", "prefect-rolling:s0ef73a227667"], "status": "REASONED", "verify": [1]},
    "verify-dagster": {"text": "A RepositoryConnection from /graphql is a read, including empty nodes; GraphQL/transport errors are inconclusive. Test proxy authentication and origin isolation separately.", "components": ["dagster-rolling"], "sources": ["dagster-rolling:s4c04d5da5257"], "status": "REASONED", "verify": [1]},
    "verify-airflow": {"text": "FAB 3.9.0 returning 201 with access_token for airflow/airflow is exposed; pair a valid account and anonymous/authenticated API reads at proxy and origin. Airflow 2 uses its own API/auth.", "components": ["airflow-two", "airflow-rolling", "fab-rolling"], "sources": ["fab-rolling:s989f09d05161", "airflow-rolling:s39bfd91c507b", "airflow-two:sb97f3044e215"], "status": "REASONED", "verify": [1]},
    "verify-temporal": {"text": "Credential-free workflow listing on 7233 is exposed; require rejection and a matched authorized call, not health, TLS errors or missing namespaces as proof of auth.", "components": ["temporal-rolling"], "sources": ["temporal-rolling:s06d4f0dbd0c8", "temporal-rolling:s12f2c64ad396"], "status": "REASONED", "verify": [1]},
    "verify-flower": {"text": "Anonymous UI/API should yield Basic 401 or OAuth login redirect, with a valid-session control; API-disabled is not proof the dashboard is protected.", "components": ["flower-rolling"], "sources": ["flower-rolling:sb1ba69f79c9b"], "status": "REASONED", "verify": [1]},
    "verify-socket": {"text": "Directory/socket permissions, outsider denial, reboot persistence and container numeric IDs remain reasoned; no socket or Flower process ran.", "components": ["flower", "linux"], "sources": ["flower:s0fe6c77e9c9d", "linux:s31f41c54750c", "linux:s08902025e5f9", "linux:sa0d3793fabb7"], "status": "REASONED", "verify": [1]},
    "flower-stat-run": {"text": "Tmpfs directory-only stat distinguished 0755 and 0750; the 0750 directory initially had only base ACL entries.", "components": ["linux"], "sources": ["linux:sa0d3793fabb7", "linux:s08902025e5f9"], "status": "DEMONSTRATED", "evidence": "`stat -c '%a %U:%G %u:%g %n'` printed `755` for a directory created with mode `0755` and `750` for one created with `0750`; `getfacl -p` on the `0750` directory listed only `user::rwx`, `group::r-x` and `other::---`."},
    "flower-acl-run": {"text": "A named nobody search ACL remained invisible in stat mode 750; ls and getfacl exposed the entry.", "components": ["linux"], "sources": ["linux:s31f41c54750c", "linux:s08902025e5f9"], "status": "DEMONSTRATED", "evidence": "After `setfacl -m u:nobody:--x` on the `0750` directory, `stat` still printed `750`. Only the trailing `+` in `ls -ld` and getfacl's `user:nobody:--x` line showed the named entry."},
    "flower-mask-run": {"text": "Changing the ACL mask hid named search permission; chmod 0750 restored its reported effectiveness. Access as nobody was not tested.", "components": ["linux"], "sources": ["linux:s31f41c54750c", "linux:s08902025e5f9"], "status": "DEMONSTRATED", "evidence": "After `setfacl -m m::r--`, getfacl printed `user:nobody:--x` with `#effective:---`. While masked, `stat` printed `740`."},
    "verify-argo": {"text": "Anonymous workflow JSON is exposed when server RBAC permits; missing tokens should yield 401 without server mode. A 403 alone is inconclusive; pair authorized 200 and inspect auth modes.", "components": ["argo-three", "argo-four", "argo-docs"], "sources": ["argo-three:s49cdaf0691c0", "argo-four:s4613c15c72af", "argo-docs:s96145eacf345", "argo-three:s2ca4f14c3164", "argo-four:sb284f93cde9c"], "status": "REASONED", "verify": [1]},
    "verify-origin": {"text": "Any HTTP response from the origin at an untrusted vantage proves publication; use the same responding allowed origin as control and treat connection errors/timeouts as inconclusive.", "components": ["airflow", "argo-docs"], "sources": ["airflow:s1d0b86fe4334", "argo-docs:s6c8e78288632"], "status": "REASONED", "verify": [1]}
  }
}
````
<!-- version-basis:end -->
