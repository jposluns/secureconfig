# AI infrastructure services: SearxNG, LocalAI, Text Embeddings Inference, LangServe, Mem0, and Onyx

These services expose search, inference, embeddings, document access, or an agent's memory. Their authentication stories differ: SearxNG and LangServe require a fronting layer or application authentication, LocalAI and Text Embeddings Inference each have a key that is unset by default, and Mem0 and Onyx ship authentication on. The deployment command decides what the network sees. Mem0's Compose file and Onyx's development Compose publish backing services beside the authenticated application, where application login cannot protect them.

Keep the application and its backing services private, publish only an authenticated TLS ingress, and keep or enable native authentication wherever it exists.

## Deployment forms and controls

Defaults below describe the vendor examples checked on 2026-09-13. A **host publication** is Docker's mapping, not the application's own listening address. The listed ports are an inventory of those examples; inspect the running deployment for additions and changed host ports.

| Tool and launch form | Default listener or host publication | Authentication by default | Also published beside it | Bind or publication control | Authentication control |
| --- | --- | --- | --- | --- | --- |
| SearxNG, direct | Application: `127.0.0.1:8888` | None | No container publication in this form | `server.bind_address` and `server.port` in `settings.yml` | [Front it](fronting-auth.md) |
| SearxNG, documented Docker run | All host interfaces, `8888:8080` | None | No other mapping in the cited run | Replace with `127.0.0.1:8888:8080`, or publish nothing | [Front it](fronting-auth.md) |
| LocalAI, documented Docker run | All host interfaces, `8080:8080` | Off: native key is unset | No additional publications established by the verified record | Replace with `127.0.0.1:8080:8080`, or publish nothing | Set `LOCALAI_API_KEY`; `LOCALAI_AUTH=true` enables multi-user OAuth with per-user keys |
| Text Embeddings Inference, documented Docker run | All host interfaces, `8080:80` | Partial: `--api-key` / `API_KEY` is unset by default, and even when set it covers the inference routes only | On the same port, outside the key: `/`, `/health`, `/ping`, `/metrics`, `/docs`, `/api-doc/openapi.json` (in the documented HTTP build `/metrics` is served on this main port; `--prometheus-port`, default `9000`, starts a separate exporter only in the gRPC build) | Replace with `127.0.0.1:8080:80`, or publish nothing | Set `--api-key` or `API_KEY`, and front the service, because the key alone leaves the routes above open |
| LangServe, quickstart | Application: `localhost:8000` | None supplied; the application author provides authentication | No container publication in this form | `host=` in `uvicorn.run` | FastAPI dependencies, or [front it](fronting-auth.md) |
| Mem0, server Compose | Application: `0.0.0.0:8000` inside the container; all host interfaces, `8888:8000` | On: bearer JWT, per-user `X-API-Key`, or legacy admin key | PostgreSQL `8432:5432`; dashboard `3000:3000`, both on all host interfaces | Remove PostgreSQL's publication; remove or loopback-scope API and dashboard mappings | Keep authentication enabled; do not set `AUTH_DISABLED=true` |
| Onyx, production Compose | nginx host publications `80:80` and `443:443` | On: email/password | Backing services have no host publications | Keep backing services unpublished; configure the intended TLS ingress | Keep the built-in login; `AUTH_TYPE` is inert since v4.4.0 |
| Onyx, development Compose | nginx `80:80` and `3000:80` from the base file, plus API `8080:8080` from the override; all on every host interface | On at the application | PostgreSQL `5432:5432`, OpenSearch `9200:9200`, inference `9000:9000`, Redis `6379:6379`, MinIO `9004:9000` and `9005:9001`, code interpreter `8000:8000` | Use production Compose, or remove every unnecessary publication from the effective configuration | Application authentication is on; it does not reach the backing ports |

## 1. Bind privately, including every container publication

For a process running directly on the host, bind it to loopback explicitly. SearxNG already defaults to `127.0.0.1`, but LocalAI defaults to `:8080` and Text Embeddings Inference to `0.0.0.0:3000`, so bind those yourself: LocalAI `LOCALAI_ADDRESS=127.0.0.1:8080` (or `--address`), TEI `--hostname 127.0.0.1` with the intended `--port` (its CLI port default `3000` is distinct from the container port `80`). SearxNG's settings belong under `server:` in `settings.yml`:

```yaml
server:
  bind_address: "127.0.0.1"
  port: 8888
```

LangServe's quickstart uses:

```python
uvicorn.run(app, host="localhost", port=8000)
```

For containers, remove host publications when the proxy reaches the application over a private container network. Where a proxy running on the host needs a published backend port, use the loopback mapping in the table. Replace the existing mapping; adding another mapping does not remove the original.

A container's loopback address belongs to that container. Do not change its application bind to `127.0.0.1` and expect another container to reach it. Restrict the host publication, or leave the service unpublished on the network shared with its proxy.

Docker publications without a host IP expose the port on all host interfaces. On Linux, Docker's forwarding rules can bypass the chains used by UFW; a UFW deny is not a substitute for removing the publication ([docker.md](docker.md)).

Compose overrides need particular care. An ordinary `ports:` list can merge with the base list and retain the public mapping. Edit the base mapping, or use Compose's documented `!reset` mechanism to remove the list. For example, an override for Mem0 can remove PostgreSQL's publication:

```yaml
services:
  postgres:
    ports: !reset []
```

This removes only PostgreSQL's publication. The API and dashboard still need the treatment described below. Include the override in the actual deployment invocation, and inspect the merged configuration and running publications using Verify check 2. If the installed Compose rejects `!reset`, edit the base file instead; do not replace it with an ordinary empty list and assume the publication disappeared.

## 2. Put TLS and authentication at the ingress

Use [nginx.md](nginx.md), [caddy.md](caddy.md), or [traefik.md](traefik.md) for TLS. The proxy reaches loopback when it runs on the host, or the application's service address when both run on a private container network. Only the intended ingress receives public traffic.

For human access, add the login and identity policy in [fronting-auth.md](fronting-auth.md). For machine clients, enforce a credential at the proxy, such as the bearer-token pattern in [ollama.md](ollama.md). Protect every route that reaches the service's capabilities; a login page on the UI does not establish protection of the API.

A private route through [tailscale.md](tailscale.md) or an authenticated tunnel through [cloudflare.md](cloudflare.md) is another option. A tunnel still needs an access policy.

Onyx's production Compose publishes only nginx. That establishes the intended publication boundary; it does not, by itself, demonstrate a working certificate or the deployed access policy.

## 3. Auth absent or unset

### SearxNG

The direct configuration binds loopback, but the documented Docker command publishes `8888:8080` without a host IP. Use `127.0.0.1:8888:8080` behind a host proxy, or remove the publication behind a containerized proxy.

SearxNG has no authentication in the verified configuration. Put access control in front of it. An open search service lets other people make search requests through your deployment.

Set a unique `server.secret_key` (environment `SEARXNG_SECRET`): it is a cryptographic secret, not user authentication, and SearxNG exits at startup in production rather than run with the shipped `ultrasecretkey` placeholder. SearxNG also fetches remote URLs server-side and its image proxy follows redirects, so it is an SSRF vector: keep it behind the fronting auth and restrict its outbound reach so a search or image fetch cannot be steered at your internal services or the cloud metadata address ([egress-metadata.md](egress-metadata.md)).

### LocalAI

LocalAI has native authentication; the documented deployment leaves it off unless configured. Set a strong, unique value in the service's runtime environment:

```dotenv
LOCALAI_API_KEY=REPLACE_WITH_LONG_RANDOM_KEY
```

For multi-user OAuth and per-user keys, the documented control is:

```dotenv
LOCALAI_AUTH=true
```

Use the vendor's multi-user setup instructions when choosing that mode. Keep authentication at the ingress as well, and replace the documented `8080:8080` publication with the private arrangement in section 1.

### Text Embeddings Inference

The documented Docker run publishes host port 8080 to container port 80. Replace `8080:80` with `127.0.0.1:8080:80` behind a host proxy, or publish nothing behind a containerized proxy.

There is a native inbound control, and it is off until you set it. The CLI reference documents `--api-key`, with the environment variable `API_KEY`. With no key set the server responds to every request; with one set, a request must carry the key as a bearer token in the `Authorization` header. Set it, and front the service as well, because one static key is not a user model.

The key does not cover the whole port. In the HTTP server the key middleware is applied to the inference routes alone, and the health routes `/`, `/health` and `/ping`, the Prometheus route `/metrics`, and the OpenAPI surface `/docs` and `/api-doc/openapi.json` are merged into the same application beside that layer rather than beneath it. They answer anonymously on the published port with a key set. Read `/metrics` yourself before deciding that is acceptable: it reports model identity and request volumes. Checked against v1.9.0; treat it as version-specific and re-read for your own version.

Two defaults compound it. `--hostname` defaults to `0.0.0.0`, so the process listens on every interface inside its namespace and the publication alone decides what reaches it. In the documented HTTP build `/metrics` is served on the main application port, not on a separate listener (the `--prometheus-port` default `9000` starts a standalone exporter only in the gRPC build), so publishing the main port publishes `/metrics` with it; do not rely on leaving `9000` unpublished to hide it. Confirm which build you run before deciding either is closed.

Do not assume a token used to download a model authenticates incoming embedding requests.

### LangServe

Lifecycle note, as of September 2026: LangServe was deprecated on 2024-11-18. Its README recommends LangGraph Platform for new projects. Existing deployments still need these controls while they remain in service.

Keep the quickstart's loopback bind. LangServe makes the application author responsible for authentication, with FastAPI dependencies as the documented integration point. Implement that authentication or put the complete service behind an authenticating proxy, including callable routes.

## 4. A guarded front door with the backing store published beside it

Mem0 and Onyx's development Compose share this shape. The application has a real authentication gate, but a connection to the database, index, cache, or object-store port never passes through that gate.

A PostgreSQL password prompt does not fix this deployment boundary. The database remains reachable independently of the application. Remove its host publication and retain the database's own authentication as a separate control.

### Mem0

Keep authentication on. Protected API endpoints accept a bearer JWT from the dashboard login flow or an `X-API-Key` header. Per-user keys have the `m0sk_` prefix; the legacy `ADMIN_API_KEY` is also supported. Do not leave `AUTH_DISABLED=true` in a deployed environment. The server logs a warning at startup when it is enabled, and a different one when authentication is on and a NON-EMPTY `ADMIN_API_KEY` is shorter than 16 characters; an unset key takes a third branch of its own. The two are alternatives on one `if`/`elif`, so enabling `AUTH_DISABLED` suppresses the short-key warning rather than adding to it, and neither stops the start.

`JWT_SECRET` is not optional, and the server enforces it: with authentication on and no secret set it raises at startup and refuses to run. The documented `server/.env` sets it beside `OPENAI_API_KEY`, generated with `openssl rand -base64 48`, and the JWTs that carry a dashboard session are signed with it. Note what that enforcement implies: the only way to start this server without a signing secret is to turn authentication off altogether.

Register the first admin before the deployment is reachable from anywhere but the host. `POST /auth/register` succeeds only while no user exists and returns `403` afterwards, so an instance published before that call hands admin to whoever finds it first. Bootstrap it on the host, either with `make bootstrap` from `server/`, which starts Compose, creates the admin, and issues the first API key, or through the setup wizard while the dashboard is still host-only. The `/` redirect, `/docs`, and `/openapi.json` stay open in every configuration, so reaching one of those proves nothing about the protected endpoints.

The server Compose publishes three services:

- API: host 8888 to container 8000.
- PostgreSQL: host 8432 to container 5432.
- Dashboard: host 3000 to container 3000.

Remove PostgreSQL's host publication. For a host proxy, replace the API and dashboard mappings with `127.0.0.1:8888:8000` and `127.0.0.1:3000:3000`. For a containerized proxy, leave both unpublished and connect the proxy to their private network.

The dashboard's own authentication coverage is **unverified here**. Give it its own protected ingress route; the API's authentication does not establish the dashboard's policy.

The cited Compose command runs uvicorn with `--host 0.0.0.0 --port 8000 --reload`. `--reload` is a development-server flag. Remove it from a production invocation and retain the network restrictions above.

### Onyx

Use `deployment/docker_compose/docker-compose.prod.yml` as the production deployment basis. In the verified file, only nginx publishes host ports; the backing services stay on the Docker network.

The first user to sign up becomes an admin. Complete that sign-up while the deployment is still reachable only from the host, because until it happens the login page is an admin-enrolment form for whoever reaches it first.

`docker-compose.dev.yml` is an override, not a standalone file. Its own header gives the launch form as `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait`, so the effective configuration is the base file plus the override, and the base file publishes nginx on `${HOST_PORT_80:-80}:80` and `${HOST_PORT:-3000}:80`. Enumerate the merged result, not the override alone: an inventory taken from the override misses two published ports.

If the development file is running, remove the API publication and every backing publication listed in the table, except any deliberately retained loopback access. The six backing services account for seven host ports because MinIO publishes both its API and console. The API's 8080 publication is additional, and nginx's two come from the base file.

The development mappings include expressions such as `${POSTGRES_HOST_PORT:-5432}:5432`. Setting `POSTGRES_HOST_PORT` changes the host port. Leaving it empty selects the default. Neither action removes the publication. The same trap appears in Dify's plugin-daemon mapping in [agent-builders.md](agent-builders.md).

Email/password authentication is already enabled. `AUTH_TYPE` has had no effect since v4.4.0; the September 2026 documentation says removal is planned for v4.5. Do not set it expecting to change authentication.

The Docker documentation also describes access at `localhost:3000`. That is now established from the base Compose file rather than inferred: host 3000 maps to nginx's container port 80, and `web_server` carries no host publication of its own. So `localhost:3000` reaches nginx, not the web process directly, and the web process is not separately published.

For backing-service controls, see [postgresql.md](postgresql.md), [redis.md](redis.md), [minio.md](minio.md), and the OpenSearch material in [elasticsearch.md](elasticsearch.md). Those controls complement removing unnecessary publications.

Onyx also stores the credentials for each document-source connector you add through its UI (a retained `credential_json` per connector), so those are protected stored data, not just runtime configuration: give each connector the least privilege its source allows, protect the database and its backups where the credentials live, and rotate a connector's credential if the instance was ever exposed.

## 5. MFA and secrets

Enforce MFA for human access through the identity provider or fronting layer ([mfa.md](mfa.md), [fronting-auth.md](fronting-auth.md)). Native MFA coverage for these six services is **unverified here**; this guide relies on the fronting policy.

Machine clients need separate credentials, with the narrowest permissions the application or gateway supports. Keep provider keys, service keys, and signing secrets out of source control and images; supply them at runtime per [secrets.md](secrets.md). A provider credential used by the application is not an inbound access control.

## Verify

**Demonstration status:** the placeholder guards and the placeholder-scan discrimination were exercised locally, in `bash`, `dash` and BusyBox `ash`, with and without `set -u`. Checks 2 to 7 below are **reasoned rather than demonstrated** against deployments. The specific blocking capability is that the authoring environment has no container runtime, and with it no live service, no external network vantage, no TLS exchange and no browser authentication flow. Backlog row 2.24 tracks demonstrating those checks once a runtime is available: a reasoned check is a debt, not a destination. The maintainer's verified vendor record supplies the deployment facts, and each check below states the outcome it expects in both the exposed and the fixed state.

Use Bash for these blocks and curl 7.75.0 or newer for `exitcode` and `errormsg`. Copy each complete block, including the enclosing parentheses. The values go on the `set --` line, so no named variable is exposed to attributes or values the reader's shell already holds, and every probe sits behind a guard that leaves the subshell rather than running on an unsubstituted value. Substitute inside the single quotes and leave them in place. They are what keeps a URL's `&` from backgrounding the line and a `$(...)` or a backtick in a pasted value from running: the shell evaluates that value before any guard in the block can see it. Keep the quotes even for an empty value, and paste every block whole. Each block opens with a fixed marker on its `set --` line, and the guard lines below check that marker and count the values, so a fragment that keeps those lines but drops or shortens the `set --` line stops instead of running on whatever arguments your own shell already held. A fragment pasted from below the guard lines is not guarded at all, which is why the instruction is to paste whole blocks. One case is beyond a pasted block's reach: a shell that already holds the marker and the right number of plausible values is indistinguishable from the block having set them, so paste whole blocks rather than relying on the check to catch every way of not doing so.

### 1. Reject unfinished configuration and probe values

Run this for each configuration or environment file you edited:

```bash
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_EDITED_CONFIG_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not checking"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not checking"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the file name on the set -- line above; not checking"; exit 1 ;;
    *) if grep -nH -o 'REPLACE_WITH_[[:alnum:]_]*' -- "$1"; then grep_rc=0; else grep_rc=$?; fi
       printf 'grep_exit=%s\n' "$grep_rc" ;;
  esac
)
```

**Broken:** unresolved values print their filename, line number, and placeholder token, followed by `grep_exit=0`. Stop and replace them. An unchanged filename placeholder prints `substitute the file name on the set -- line above; not checking`.

**Fixed:** no placeholder matches print, followed by `grep_exit=1`. A file-read error is inconclusive, not a clean scan. This check prints only the matched placeholder tokens, rather than complete secret-bearing lines.

The address guards below likewise print `not probing` when required values are empty or still contain `REPLACE_WITH_`. Substituted values enter the probe arm. This is a prerequisite, not evidence that the deployment is private.

### 2. Inventory listeners, the merged Compose model, and running publications

**Reasoned, not demonstrated** (no container runtime in the authoring environment; row 2.24 tracks demonstrating it). Run on the deployment host. For Compose, use the exact project, file selection, overrides, environment, and profiles used to start the deployment. Add those same options to these commands where needed. What makes an inventory readable rather than guesswork is documented: Compose ps reports the running publication fields, Compose merge rules govern how an override's port list combines with the base, and Compose networking establishes that services reach each other with no host publication at all; all three are in Sources:

```bash
ss -tlnp
docker compose config
docker compose ps --format json
```

**Broken:** `ss` shows an application or backing listener on a wildcard or non-loopback host address; the merged Compose model retains an unwanted host publication; or the running service has a `Publishers` entry mapping it to an unintended host address and port.

**Fixed:** host application listeners are loopback-only; backing services have no host publications; any retained application publications are loopback-only; only the intended ingress is public. The running publications agree with the merged model.

Read the whole listener list, including IPv6 and listeners bound to a specific LAN address. Public SSH or other unrelated services are outside this guide's acceptance decision.

A Docker publication implemented through DNAT may not appear in host `ss` output. Read the actual host mappings in `Publishers`, including `PublishedPort`, rather than counting entries: a container port listed without a host publication is not the same thing. The real JSON output shape was not demonstrated here.

A Compose error, missing service, stopped application, or empty inventory is not a pass. `docker compose config` describes the intended configuration; it does not prove running containers were recreated with it. Its output can contain secrets, so inspect it privately.

### 3. Probe the application's direct ports from another host

**Reasoned, not demonstrated, including the cross-host vantage** (no container runtime and no second host in the authoring environment; row 2.24 tracks demonstrating it). Probe every application or dashboard port found in check 2, using its actual host port. Include reachable LAN addresses and public IPv4/IPv6 addresses; bracket an IPv6 literal used in the HTTP URL. Exclude the intentionally public TLS ingress. The outcomes below rest on two sources: the curl manual for what its exit status, error text and timing actually report, and Docker's packet-filtering page for how a published port interacts with a host firewall, which is what makes a refusal meaningful rather than incidental.

```bash
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HOST_ADDRESS' 'REPLACE_WITH_PORT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1:$2" in
    *REPLACE_WITH_*|:*|*:) echo "substitute the address and port on the set -- line above; not probing"; exit 1 ;;
    *) curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
         -w 'http=%{http_code} exit=%{exitcode} remote=%{remote_ip} time_connect=%{time_connect} err=%{errormsg}\n' \
         "http://$1:$2/" ;;
  esac
)
```

**Broken:** any HTTP response, including `401`, proves the direct path exists. A completed TCP connection followed by an empty response, reset, or timeout also fails the private-network requirement.

**Fixed:** the connection to your actual backend address and port is refused, corroborated by check 2 and the working ingress in check 7.

A timeout alone is inconclusive. `http=000` can occur after a server accepts and stalls. Read `err`, `remote`, and `time_connect`; corroborate a connection timeout with the running publication inventory and evidence at the filtering point. DNS failures, local socket errors, or a test aimed at the wrong address never establish a block. Use check 4 as well to test TCP reachability independently of HTTP.

### 4. Probe every backing port

**Reasoned, not demonstrated** (no container runtime in the authoring environment; row 2.24 tracks demonstrating it). From another host, run this for every private port found in check 2, including the application's ports from check 3. The distinguishing authority here is the publication state, read together with the firewall configuration, per Docker's packet-filtering page and Compose ps in Sources: under Docker's default firewall integration a backing service with no host publication is not reachable from another host, so a refusal corroborated by check 2 means the boundary holds. That page also states the limit of the guarantee: with Docker's firewalling disabled and no replacement rules, every container port becomes accessible, published or not, so an unpublished port is evidence of the boundary only while that integration is in place. An answer from any of these ports means the boundary does not hold.

For the unchanged vendor examples, Mem0 adds 8432 and 3000 beside API port 8888. Onyx development adds 5432, 9200, 9000, 6379, 9004, 9005, and 8000 beside API port 8080, and nginx contributes 80 and 3000 from the base file. Environment variables can move these ports; the running inventory is the authority.

```bash
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HOST_ADDRESS' 'REPLACE_WITH_PORT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  if [ -z "$1" ] || [ -z "$2" ]; then echo "substitute the address and port on the set -- line above; not probing"; exit; fi
  case "$1:$2" in
    *REPLACE_WITH_*) echo "substitute the address and port on the set -- line above; not probing"; exit ;;
  esac
  if nc -vz -w 5 "$1" "$2"; then nc_rc=0; else nc_rc=$?; fi
  printf 'exit=%s\n' "$nc_rc"
)
```

**Broken:** netcat reports a successful connection and `exit=0`. A database password prompt or a service that sends nothing after accepting does not change that result.

**Fixed:** netcat reports connection refused to your actual address and port, with a nonzero exit status, and check 2 confirms the private publication state.

A timeout remains inconclusive without corroborating configuration and filtering evidence. Unsupported options, name-resolution failures, local errors, or unexplained silence are not passes. In particular, BusyBox netcat may reject `-v`; use an implementation supporting these options.

### 5. Require authentication at the ingress

**Reasoned, not demonstrated** (no container runtime in the authoring environment; row 2.24 tracks demonstrating it). Select a harmless request to a real protected capability. Its path, method, request body, and exact response for each installed tool are **unverified here**. Obtain them from that version's documentation and use the same request in check 7. What separates the exposed outcome from the fixed one is documented per service in Sources: Text Embeddings Inference answers every request until `--api-key` is set, LocalAI's key is unset by default, and Mem0 and Onyx both ship authentication on, so an anonymous `2xx` from any of them is the exposed state and a `401` or `403` is the fixed one. For example, Text Embeddings Inference's protected capability is `POST /embed` with the harmless body `{"inputs":"probe"}`: expect a `401` without the key and a `2xx` embedding with it (check 7).

Do not choose a health endpoint, documentation page, login page, or an invented path. A `404` or request-validation error cannot demonstrate authentication.

Test the ingress and the native layer as SEPARATE controls. Where a service's native key does not cover every route (Text Embeddings Inference leaves `/metrics`, `/docs` and the health routes outside it), also probe one of those uncovered routes anonymously THROUGH the public ingress: the fronting auth must gate it, so an anonymous `2xx` there is a finding even when the capability route is protected. Where the ingress and the application use different credentials, send the application's own credential WITHOUT the ingress credential and confirm the ingress still rejects it, so a keyed backend behind a TLS-only proxy cannot pass this check while the ingress itself is open.

Set the second value on the `set --` line to the actual method, such as `GET` or `POST`. Keep the third value's empty quotes for a request without a body; otherwise put a harmless JSON test body there.

```bash
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PROTECTED_URL' 'REPLACE_WITH_HTTP_METHOD' ''
  # $3 is the harmless JSON request body. Keep the empty quotes if the request needs none.
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 3 ] || { echo "the set -- line needs exactly 3 values; not probing"; exit; }
  if [ -z "$1" ] || [ -z "$2" ]; then
    echo "fill in the URL and method on the set -- line above; not probing"; exit
  fi
  case "$1$2$3" in
    *REPLACE_WITH_*) echo "substitute the request values on the set -- line above; not probing"; exit ;;
  esac
  case "$1" in
    https://*) ;;
    *) echo "use a https:// URL; not probing"; exit ;;
  esac
  if [ -n "$3" ]; then
    set -- -H 'Content-Type: application/json' --data-binary "$3" -X "$2" "$1"
  else
    set -- -X "$2" "$1"
  fi
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -D - -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$@"
)
```

**Broken:** the anonymous request returns application data or performs the capability, typically with a `2xx` status.

**Fixed:** the request receives an authentication rejection, normally `401` or `403`, or an interactive sign-in redirect whose `Location` identifies the configured identity service. Check 7 must then succeed for the authorized caller.

A redirect alone is insufficient: inspect its destination. Do not follow it automatically and mistake a `200` login page for application access. TLS, connection, `5xx`, routing, and validation errors are inconclusive. Certificate verification stays enabled.

### 6. Exercise the capability without native credentials

**Reasoned, not demonstrated** (no container runtime in the authoring environment; row 2.24 tracks demonstrating it). For LocalAI or Text Embeddings Inference with a key set, Mem0, Onyx, or LangServe with application authentication, run the same harmless protected request against the private upstream from a trusted location that can reach it. Do not publish a port to perform this check. The same per-service passages in Sources supply the expected outcomes as in check 5, and one of them bounds this check rather than supporting it: the Text Embeddings Inference server source shows its key middleware covering the inference routes only, so an anonymous answer from `/metrics`, `/health` or `/docs` is not evidence that the key is unset.

For SearxNG, for LangServe relying entirely on its proxy, or for any service you have deliberately left unauthenticated on the private side, run this capability check through the authenticated HTTPS ingress. An intentionally unauthenticated private upstream cannot demonstrate native authentication.

```bash
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PROTECTED_URL' 'REPLACE_WITH_HTTP_METHOD' '' ''
  # $3 is the same harmless JSON body as checks 5 and 7 (keep the empty quotes if none is needed).
  # $4 is a credential header: leave it EMPTY for the anonymous run, put a WRONG credential for the
  # wrong-key run, and the VALID one for the positive control. Run this block three times against the
  # SAME private URL; the native layer must reject the first two and serve the third.
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 4 ] || { echo "the set -- line needs exactly 4 values; not probing"; exit; }
  if [ -z "$1" ] || [ -z "$2" ]; then
    echo "fill in the URL and method on the set -- line above; not probing"; exit
  fi
  case "$1$2$3$4" in
    *REPLACE_WITH_*) echo "substitute the request values on the set -- line above; not probing"; exit ;;
  esac
  case "$1" in
    http://*|https://*) ;;
    *) echo "use an http:// or https:// URL; not probing"; exit ;;
  esac
  if [ -n "$3" ] && [ -n "$4" ]; then
    set -- -H 'Content-Type: application/json' --data-binary "$3" -H "$4" -X "$2" "$1"
  elif [ -n "$3" ]; then
    set -- -H 'Content-Type: application/json' --data-binary "$3" -X "$2" "$1"
  elif [ -n "$4" ]; then
    set -- -H "$4" -X "$2" "$1"
  else
    set -- -X "$2" "$1"
  fi
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -D - -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$@"
)
```

**Broken:** the unauthenticated caller receives protected data or successfully invokes the capability.

**Fixed:** the configured authentication layer rejects that same valid request, while check 7 succeeds with credentials.

An unreachable upstream means native authentication was not tested; it does not prove that authentication works. Likewise, an unknown path, malformed request, or unavailable model does not demonstrate rejection of an anonymous caller. Run the block three times against the SAME private URL, varying only `$4`: empty (anonymous), a deliberately WRONG credential, then the VALID one. The native layer must reject the first two and serve the third; that valid-credential run is the positive control on the private backend, so the three together (anonymous reject, wrong-key reject, valid-key accept) establish the native gate rather than a coincidental error. Check 7 is the separate success test through the HTTPS ingress.

Mem0 and Onyx ship authentication on, but the verified record does not establish the exact response code for a selected endpoint. Investigate a successful anonymous Mem0 request for `AUTH_DISABLED=true`, route coverage, and the running version; the response alone does not identify its cause.

### 7. Prove the protected service still works

**Reasoned, not demonstrated** (no container runtime in the authoring environment; row 2.24 tracks demonstrating it). Repeat the capability request through the HTTPS ingress with valid credentials. Keep its method, path, and body the same as the anonymous test, allowing only the expected upstream-to-ingress URL change. The credential shapes this check needs are documented in Sources: Mem0 accepts a JWT or an `X-API-Key`, Onyx uses its email and password session, LocalAI and Text Embeddings Inference take their configured key, and a guide that cannot show this check succeeding has not established that the restriction left a working service behind.

The header below is reader-supplied. For a configured bearer-token proxy it is `Authorization: Bearer` followed by the token. Mem0 accepts its native per-user key through `X-API-Key`, or a JWT through `Authorization: Bearer`. Other native credential transports are **unverified in the supplied record**. Where ingress and application require separate credentials, add both headers inside the guarded curl command using the deployed authentication design.

```bash
(                              # a subshell, so your own script arguments are untouched
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PROTECTED_URL' 'REPLACE_WITH_HTTP_METHOD' '' 'REPLACE_WITH_HEADER_NAME: REPLACE_WITH_CREDENTIAL'
  # $3 is the same harmless JSON body as the anonymous check. Keep the empty quotes if none is needed.
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 4 ] || { echo "the set -- line needs exactly 4 values; not probing"; exit; }
  if [ -z "$1" ] || [ -z "$2" ] || [ -z "$4" ]; then
    echo "fill in the URL, method, and header on the set -- line above; not probing"; exit
  fi
  case "$1$2$3$4" in
    *REPLACE_WITH_*) echo "substitute the request values on the set -- line above; not probing"; exit ;;
  esac
  case "$1" in
    https://*) ;;
    *) echo "use a https:// URL; not probing"; exit ;;
  esac
  if [ -n "$3" ]; then
    set -- -H 'Content-Type: application/json' --data-binary "$3" -H "$4" -X "$2" "$1"
  else
    set -- -H "$4" -X "$2" "$1"
  fi
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -D - -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$@"
)
```

**Broken:** both anonymous and credentialed requests return protected data, or the credentialed request cannot reach a working application after the restrictions were applied. Connection failures, `401`/`403`, `5xx`, or a login page in place of the expected result do not establish a working protected service.

**Fixed:** the anonymous request is rejected and this credentialed request returns the expected application result, normally `2xx`. A `2xx` alone is insufficient; inspect the body to distinguish application output from a generic page.

Credentialed success can also occur on an exposed service. It only completes the verification when the negative checks above pass.

For browser access, use a fresh session subject to the MFA policy. **Broken:** password-only access reaches the protected application when the policy requires a second factor. **Fixed:** the configured MFA challenge appears before access, and completing it opens the intended application.

If the deployment trusts identity headers from a proxy, also perform the forged-header check in [fronting-auth.md](fronting-auth.md). **Broken:** a direct request carrying the forged identity reaches the application. **Fixed:** the direct connection is refused at the network boundary, and legitimate authenticated access works through the proxy. This browser and identity-header verification is also reasoned rather than demonstrated here.

## Common mistakes

- Running Onyx's development Compose on an exposed host because its login page works.
- Assuming Mem0's API authentication also protects PostgreSQL or establishes the dashboard's policy.
- Changing a `${VAR:-default}` host port and believing the publication disappeared.
- Adding a loopback mapping through a Compose override while retaining the original public mapping.
- Leaving `AUTH_DISABLED=true` in Mem0 after debugging.
- Setting Onyx's inert `AUTH_TYPE` and expecting an authentication change.
- Leaving LocalAI's native key unset, or mistaking an upstream provider token for inbound authentication.
- Inspecting only `ss`, only IPv4, or only the deployment host's own view.
- Accepting a timeout, an unknown endpoint's `404`, or a credentialed `200` as proof of protection.

## Sources (checked September 2026)

The service facts come from the maintainer's vendor-source verification record dated 2026-09-13. This authoring environment had no network; the pages were not reopened here. Docker and probe syntax also follow the cited sources already recorded in the repository's existing guides.

**Citation pinning:** the LangServe, Mem0, and Onyx citations below are pinned to commits, and each commit was opened and confirmed to contain the fact it is cited for.

- [SearxNG server settings](https://docs.searxng.org/admin/settings/settings_server.html): `server.bind_address`, `server.port`, and direct defaults.
- [SearxNG Docker installation](https://docs.searxng.org/admin/installation-docker.html): documented `8888:8080` publication.
- [LocalAI getting started](https://localai.io/docs/basics/getting_started/): port 8080, Docker publication, `LOCALAI_API_KEY`, and `LOCALAI_AUTH`.
- [Text Embeddings Inference quick tour](https://huggingface.co/docs/text-embeddings-inference/en/quick_tour): container port 80 and host publication 8080.
- [Text Embeddings Inference CLI arguments](https://huggingface.co/docs/text-embeddings-inference/en/cli_arguments): `--api-key` and `API_KEY`, the default-open behaviour without one, `--hostname` defaulting to `0.0.0.0`, and `--prometheus-port` defaulting to `9000`.
- [Text Embeddings Inference HTTP server at v1.9.0](https://github.com/huggingface/text-embeddings-inference/blob/v1.9.0/router/src/http/server.rs): the key middleware applied to the inference routes only, with the health, `/metrics` and OpenAPI routes merged beside it.
- [LangServe README at commit `27e57af`](https://github.com/langchain-ai/langserve/blob/27e57afeda13007a7f4e007c5d1f5e8489963aa4/README.md): quickstart bind, application authentication responsibility, deprecation on 2024-11-18, and successor.
- [Mem0 REST API](https://docs.mem0.ai/open-source/features/rest-api): authentication enabled by default, JWTs, `X-API-Key`, `m0sk_` keys, `ADMIN_API_KEY`, `AUTH_DISABLED` and its startup warning, `JWT_SECRET`, `make bootstrap`, the first-admin `POST /auth/register`, and the routes that stay open.
- [Mem0 server Compose](https://github.com/mem0ai/mem0/blob/c7ee362aff94a369af70f13f2b4f853f6793ff4c/server/docker-compose.yaml): uvicorn command and API, PostgreSQL, and dashboard publications.
- [Mem0 server `main.py`](https://github.com/mem0ai/mem0/blob/c7ee362aff94a369af70f13f2b4f853f6793ff4c/server/main.py): the startup `raise RuntimeError` when authentication is on and `JWT_SECRET` is unset, and the `if`/`elif` warning branches for `AUTH_DISABLED` and a short `ADMIN_API_KEY`. The REST API page describes the request-time responses; this file is the startup behaviour.
- [Onyx basic authentication](https://docs.onyx.app/deployment/authentication/basic.md): email/password authentication, the first user to sign up becoming an admin, and inert `AUTH_TYPE`.
- [Onyx local Docker deployment](https://docs.onyx.app/deployment/local/docker.md): documented access at `localhost:3000`.
- [Onyx production Compose](https://github.com/onyx-dot-app/onyx/blob/a0370f232ba4e4625131fae518b86e5530e98ec5/deployment/docker_compose/docker-compose.prod.yml): nginx-only host publications.
- [Onyx development Compose](https://github.com/onyx-dot-app/onyx/blob/a0370f232ba4e4625131fae518b86e5530e98ec5/deployment/docker_compose/docker-compose.dev.yml): API and backing-service publications, and its own header naming the two-file launch form.
- [Onyx base Compose](https://github.com/onyx-dot-app/onyx/blob/a0370f232ba4e4625131fae518b86e5530e98ec5/deployment/docker_compose/docker-compose.yml): nginx publishing `${HOST_PORT_80:-80}:80` and `${HOST_PORT:-3000}:80`, and `web_server` carrying no host publication.
- [Docker packet filtering and firewalls](https://docs.docker.com/engine/network/packet-filtering-firewalls/): published ports and firewall interaction.
- [Compose networking](https://docs.docker.com/compose/how-tos/networking/): communication between services without host publication.
- [Compose merge rules](https://docs.docker.com/reference/compose-file/merge/): merged port lists and `!reset`.
- [Docker Compose ps](https://docs.docker.com/reference/cli/docker/compose/ps/): running service information and publication fields.
- [curl manual](https://curl.se/docs/manpage.html): request options, TLS verification, proxy bypass, timing, and error reporting.
- [LocalAI CLI reference](https://localai.io/docs/reference/cli-reference/): the `--address` flag and `LOCALAI_ADDRESS` bind, default `:8080`.
- [SearxNG webapp implementation](https://raw.githubusercontent.com/searxng/searxng/d4ce87c23431f607162fc5c39ce52c538d64588f/searx/webapp.py): the production startup rejection of the `ultrasecretkey` placeholder and the image proxy following redirects.
- [Onyx data model](https://raw.githubusercontent.com/onyx-dot-app/onyx/15ead4ca364e654d40dac842ee9d0bb9e0fe5471/backend/onyx/db/models.py): the retained per-connector `Credential.credential_json` storage.
- [Text Embeddings Inference gRPC server](https://raw.githubusercontent.com/huggingface/text-embeddings-inference/1bb59202500e5f69dd8be63dd1604f7625124fbe/router/src/grpc/server.rs): the standalone Prometheus exporter (`prom_builder.install()`) of the gRPC build, distinct from the HTTP build's main-port `/metrics`.

