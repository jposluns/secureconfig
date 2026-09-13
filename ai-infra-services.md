# AI infrastructure services: SearxNG, LocalAI, Text Embeddings Inference, LangServe, Mem0, and Onyx

These services expose search, inference, embeddings, document access, or an agent's memory. Their authentication stories differ: SearxNG and LangServe require a fronting layer or application authentication, LocalAI has a key that is unset by default, and Mem0 and Onyx ship authentication on. The deployment command decides what the network sees. Mem0's Compose file and Onyx's development Compose publish backing services beside the authenticated application, where application login cannot protect them.

Keep the application and its backing services private, publish only an authenticated TLS ingress, and keep or enable native authentication wherever it exists.

## Deployment forms and controls

Defaults below describe the vendor examples checked on 2026-09-13. A **host publication** is Docker's mapping, not the application's own listening address. The listed ports are an inventory of those examples; inspect the running deployment for additions and changed host ports.

| Tool and launch form | Default listener or host publication | Authentication by default | Also published beside it | Bind or publication control | Authentication control |
| --- | --- | --- | --- | --- | --- |
| SearxNG, direct | Application: `127.0.0.1:8888` | None | No container publication in this form | `server.bind_address` and `server.port` in `settings.yml` | [Front it](fronting-auth.md) |
| SearxNG, documented Docker run | All host interfaces, `8888:8080` | None | No other mapping in the cited run | Replace with `127.0.0.1:8888:8080`, or publish nothing | [Front it](fronting-auth.md) |
| LocalAI, documented Docker run | All host interfaces, `8080:8080` | Off: native key is unset | No additional publications established by the verified record | Replace with `127.0.0.1:8080:8080`, or publish nothing | Set `LOCALAI_API_KEY`; `LOCALAI_AUTH=true` enables multi-user OAuth with per-user keys |
| Text Embeddings Inference, documented Docker run | All host interfaces, `8080:80` | No inbound authentication documented in the verified quick tour; native control unverified | No additional publications established by the verified record | Replace with `127.0.0.1:8080:80`, or publish nothing | Enforce authentication at the proxy |
| LangServe, quickstart | Application: `localhost:8000` | None supplied; the application author provides authentication | No container publication in this form | `host=` in `uvicorn.run` | FastAPI dependencies, or [front it](fronting-auth.md) |
| Mem0, server Compose | Application: `0.0.0.0:8000` inside the container; all host interfaces, `8888:8000` | On: bearer JWT, per-user `X-API-Key`, or legacy admin key | PostgreSQL `8432:5432`; dashboard `3000:3000`, both on all host interfaces | Remove PostgreSQL's publication; remove or loopback-scope API and dashboard mappings | Keep authentication enabled; do not set `AUTH_DISABLED=true` |
| Onyx, production Compose | nginx host publications `80:80` and `443:443` | On: email/password | Backing services have no host publications | Keep backing services unpublished; configure the intended TLS ingress | Keep the built-in login; `AUTH_TYPE` is inert since v4.4.0 |
| Onyx, development Compose | API host publication `8080:8080`, on all interfaces | On at the application | PostgreSQL `5432:5432`, OpenSearch `9200:9200`, inference `9000:9000`, Redis `6379:6379`, MinIO `9004:9000` and `9005:9001`, code interpreter `8000:8000`; all on every host interface | Use production Compose, or remove every unnecessary publication from the effective configuration | Application login does not protect these backing ports |

## 1. Bind privately, including every container publication

For a process running directly on the host, retain its loopback bind. SearxNG's settings belong under `server:` in `settings.yml`:

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

Inbound authentication is not documented in the verified quick tour. Whether the deployed version has a native authentication flag is **unverified here**. Enforce authentication at the proxy; do not assume a token used to download a model authenticates incoming embedding requests.

### LangServe

Lifecycle note, as of September 2026: LangServe was deprecated on 2024-11-18. Its README recommends LangGraph Platform for new projects. Existing deployments still need these controls while they remain in service.

Keep the quickstart's loopback bind. LangServe makes the application author responsible for authentication, with FastAPI dependencies as the documented integration point. Implement that authentication or put the complete service behind an authenticating proxy, including callable routes.

## 4. A guarded front door with the backing store published beside it

Mem0 and Onyx's development Compose share this shape. The application has a real authentication gate, but a connection to the database, index, cache, or object-store port never passes through that gate.

A PostgreSQL password prompt does not fix this deployment boundary. The database remains reachable independently of the application. Remove its host publication and retain the database's own authentication as a separate control.

### Mem0

Keep authentication on. Protected API endpoints accept a bearer JWT from the dashboard login flow or an `X-API-Key` header. Per-user keys have the `m0sk_` prefix; the legacy `ADMIN_API_KEY` is also supported. Do not leave `AUTH_DISABLED=true` in a deployed environment.

The server Compose publishes three services:

- API: host 8888 to container 8000.
- PostgreSQL: host 8432 to container 5432.
- Dashboard: host 3000 to container 3000.

Remove PostgreSQL's host publication. For a host proxy, replace the API and dashboard mappings with `127.0.0.1:8888:8000` and `127.0.0.1:3000:3000`. For a containerized proxy, leave both unpublished and connect the proxy to their private network.

The dashboard's own authentication coverage is **unverified here**. Give it its own protected ingress route; the API's authentication does not establish the dashboard's policy.

The cited Compose command runs uvicorn with `--host 0.0.0.0 --port 8000 --reload`. `--reload` is a development-server flag. Remove it from a production invocation and retain the network restrictions above.

### Onyx

Use `deployment/docker_compose/docker-compose.prod.yml` as the production deployment basis. In the verified file, only nginx publishes host ports; the backing services stay on the Docker network.

If the development file is running, remove the API publication and every backing publication listed in the table, except any deliberately retained loopback access. The six backing services account for seven host ports because MinIO publishes both its API and console. The API's 8080 publication is additional.

The development mappings include expressions such as `${POSTGRES_HOST_PORT:-5432}:5432`. Setting `POSTGRES_HOST_PORT` changes the host port. Leaving it empty selects the default. Neither action removes the publication. The same trap appears in Dify's plugin-daemon mapping in [agent-builders.md](agent-builders.md).

Email/password authentication is already enabled. `AUTH_TYPE` has had no effect since v4.4.0; the September 2026 documentation says removal is planned for v4.5. Do not set it expecting to change authentication.

The Docker documentation also describes access at `localhost:3000`. That access URL does not establish the web process's listening address. Its bind is **unverified in the supplied record**; include any running web process in the inventory rather than treating that URL as proof of a private bind.

For backing-service controls, see [postgresql.md](postgresql.md), [redis.md](redis.md), [minio.md](minio.md), and the OpenSearch material in [elasticsearch.md](elasticsearch.md). Those controls complement removing unnecessary publications.

## 5. MFA and secrets

Enforce MFA for human access through the identity provider or fronting layer ([mfa.md](mfa.md), [fronting-auth.md](fronting-auth.md)). Native MFA coverage for these six services is **unverified here**; this guide relies on the fronting policy.

Machine clients need separate credentials, with the narrowest permissions the application or gateway supports. Keep provider keys, service keys, and signing secrets out of source control and images; supply them at runtime per [secrets.md](secrets.md). A provider credential used by the application is not an inbound access control.

## Verify

**Demonstration status:** the placeholder guards and the placeholder-scan discrimination were exercised locally. Checks 2 to 7 below are **reasoned rather than demonstrated** against deployments. No container runtime, live service, external network vantage, TLS exchange, or browser authentication flow was exercised while authoring. The maintainer's verified vendor record supplies the deployment facts.

Use Bash for these blocks and curl 7.75.0 or newer for `exitcode` and `errormsg`. Copy each complete assignment-and-guard block. `unset` clears stale values and inherited variable attributes; the command remains inside the `case` arm so an unsubstituted value cannot launch a probe.

### 1. Reject unfinished configuration and probe values

Run this for each configuration or environment file you edited:

```bash
unset infra_config
infra_config=REPLACE_WITH_EDITED_CONFIG_FILE
case "${infra_config:-}" in
  *REPLACE_WITH_*|"") echo "substitute infra_config first; not checking" ;;
  *) grep -nH -o 'REPLACE_WITH_[[:alnum:]_]*' -- "$infra_config"
     printf 'grep_exit=%s\n' "$?" ;;
esac
```

**Broken:** unresolved values print their filename, line number, and placeholder token, followed by `grep_exit=0`. Stop and replace them. An unchanged filename placeholder prints `substitute infra_config first; not checking`.

**Fixed:** no placeholder matches print, followed by `grep_exit=1`. A file-read error is inconclusive, not a clean scan. This check prints only the matched placeholder tokens, rather than complete secret-bearing lines.

The address guards below likewise print `not probing` when required values are empty or still contain `REPLACE_WITH_`. Substituted values enter the probe arm. This is a prerequisite, not evidence that the deployment is private.

### 2. Inventory listeners, the merged Compose model, and running publications

**Reasoned, not demonstrated.** Run on the deployment host. For Compose, use the exact project, file selection, overrides, environment, and profiles used to start the deployment. Add those same options to these commands where needed:

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

**Reasoned, not demonstrated, including the cross-host vantage.** Probe every application or dashboard port found in check 2, using its actual host port. Include reachable LAN addresses and public IPv4/IPv6 addresses; bracket an IPv6 literal used in the HTTP URL. Exclude the intentionally public TLS ingress.

```bash
unset infra_host infra_port
infra_host=REPLACE_WITH_HOST_ADDRESS
infra_port=REPLACE_WITH_PORT
case "${infra_host:-}:${infra_port:-}" in
  *REPLACE_WITH_*|:*|*:) echo "substitute infra_host and infra_port first; not probing" ;;
  *) curl -q -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
       -w 'http=%{http_code} exit=%{exitcode} remote=%{remote_ip} time_connect=%{time_connect} err=%{errormsg}\n' \
       "http://$infra_host:$infra_port/" ;;
esac
```

**Broken:** any HTTP response, including `401`, proves the direct path exists. A completed TCP connection followed by an empty response, reset, or timeout also fails the private-network requirement.

**Fixed:** the connection to your actual backend address and port is refused, corroborated by check 2 and the working ingress in check 7.

A timeout alone is inconclusive. `http=000` can occur after a server accepts and stalls. Read `err`, `remote`, and `time_connect`; corroborate a connection timeout with the running publication inventory and evidence at the filtering point. DNS failures, local socket errors, or a test aimed at the wrong address never establish a block. Use check 4 as well to test TCP reachability independently of HTTP.

### 4. Probe every backing port

**Reasoned, not demonstrated.** From another host, run this for every private port found in check 2, including the application's ports from check 3.

For the unchanged vendor examples, Mem0 adds 8432 and 3000 beside API port 8888. Onyx development adds 5432, 9200, 9000, 6379, 9004, 9005, and 8000 beside API port 8080. Environment variables can move these ports; the running inventory is the authority.

```bash
unset infra_host infra_port
infra_host=REPLACE_WITH_HOST_ADDRESS
infra_port=REPLACE_WITH_PORT
case "${infra_host:-}:${infra_port:-}" in
  *REPLACE_WITH_*|:*|*:) echo "substitute infra_host and infra_port first; not probing" ;;
  *) nc -vz -w 5 "$infra_host" "$infra_port"
     printf 'exit=%s\n' "$?" ;;
esac
```

**Broken:** netcat reports a successful connection and `exit=0`. A database password prompt or a service that sends nothing after accepting does not change that result.

**Fixed:** netcat reports connection refused to your actual address and port, with a nonzero exit status, and check 2 confirms the private publication state.

A timeout remains inconclusive without corroborating configuration and filtering evidence. Unsupported options, name-resolution failures, local errors, or unexplained silence are not passes. In particular, BusyBox netcat may reject `-v`; use an implementation supporting these options.

### 5. Require authentication at the ingress

**Reasoned, not demonstrated.** Select a harmless request to a real protected capability. Its path, method, request body, and exact response for each installed tool are **unverified here**. Obtain them from that version's documentation and use the same request in check 7.

Do not choose a health endpoint, documentation page, login page, or an invented path. A `404` or request-validation error cannot demonstrate authentication.

Set `infra_method` to the actual method, such as `GET` or `POST`. Leave `infra_json` empty for a request without a body; otherwise use a harmless JSON test body.

```bash
unset infra_url infra_method infra_json infra_args
infra_url=REPLACE_WITH_PROTECTED_URL
infra_method=REPLACE_WITH_HTTP_METHOD
infra_json='' # For a JSON request, set its harmless test body here.
case "${infra_url:-}|${infra_method:-}|${infra_json:-}" in
  *REPLACE_WITH_*|'|'*|*'||'*) echo "substitute the request values first; not probing" ;;
  https://*)
    infra_args=()
    if [ -n "$infra_json" ]; then
      infra_args=(-H 'Content-Type: application/json' --data-binary "$infra_json")
    fi
    curl -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
      -D - -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
      -X "$infra_method" "${infra_args[@]}" "$infra_url" ;;
  *) echo "use a https:// URL; not probing" ;;
esac
```

**Broken:** the anonymous request returns application data or performs the capability, typically with a `2xx` status.

**Fixed:** the request receives an authentication rejection, normally `401` or `403`, or an interactive sign-in redirect whose `Location` identifies the configured identity service. Check 7 must then succeed for the authorized caller.

A redirect alone is insufficient: inspect its destination. Do not follow it automatically and mistake a `200` login page for application access. TLS, connection, `5xx`, routing, and validation errors are inconclusive. Certificate verification stays enabled.

### 6. Exercise the capability without native credentials

**Reasoned, not demonstrated.** For LocalAI with a key, Mem0, Onyx, or LangServe with application authentication, run the same harmless protected request against the private upstream from a trusted location that can reach it. Do not publish a port to perform this check.

For SearxNG, Text Embeddings Inference without an established native control, or LangServe relying entirely on its proxy, run this capability check through the authenticated HTTPS ingress. An intentionally unauthenticated private upstream cannot demonstrate native authentication.

```bash
unset infra_url infra_method infra_json infra_args
infra_url=REPLACE_WITH_PROTECTED_URL
infra_method=REPLACE_WITH_HTTP_METHOD
infra_json='' # Use the same harmless request body as checks 5 and 7.
case "${infra_url:-}|${infra_method:-}|${infra_json:-}" in
  *REPLACE_WITH_*|'|'*|*'||'*) echo "substitute the request values first; not probing" ;;
  http://*|https://*)
    infra_args=()
    if [ -n "$infra_json" ]; then
      infra_args=(-H 'Content-Type: application/json' --data-binary "$infra_json")
    fi
    curl -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
      -D - -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
      -X "$infra_method" "${infra_args[@]}" "$infra_url" ;;
  *) echo "use an http:// or https:// URL; not probing" ;;
esac
```

**Broken:** the unauthenticated caller receives protected data or successfully invokes the capability.

**Fixed:** the configured authentication layer rejects that same valid request, while check 7 succeeds with credentials.

An unreachable upstream means native authentication was not tested; it does not prove that authentication works. Likewise, an unknown path, malformed request, or unavailable model does not demonstrate rejection of an anonymous caller.

Mem0 and Onyx ship authentication on, but the verified record does not establish the exact response code for a selected endpoint. Investigate a successful anonymous Mem0 request for `AUTH_DISABLED=true`, route coverage, and the running version; the response alone does not identify its cause.

### 7. Prove the protected service still works

**Reasoned, not demonstrated.** Repeat the capability request through the HTTPS ingress with valid credentials. Keep its method, path, and body the same as the anonymous test, allowing only the expected upstream-to-ingress URL change.

The header below is reader-supplied. For a configured bearer-token proxy it is `Authorization: Bearer` followed by the token. Mem0 accepts its native per-user key through `X-API-Key`, or a JWT through `Authorization: Bearer`. Other native credential transports are **unverified in the supplied record**. Where ingress and application require separate credentials, add both headers inside the guarded curl command using the deployed authentication design.

```bash
unset infra_url infra_method infra_json infra_args infra_auth_header
infra_url=REPLACE_WITH_PROTECTED_URL
infra_method=REPLACE_WITH_HTTP_METHOD
infra_json='' # Use the same harmless request body as the anonymous check.
infra_auth_header='REPLACE_WITH_HEADER_NAME: REPLACE_WITH_CREDENTIAL'
case "${infra_url:-}|${infra_method:-}|${infra_auth_header:-}|${infra_json:-}" in
  *REPLACE_WITH_*|'|'*|*'||'*) echo "substitute the request values first; not probing" ;;
  https://*)
    infra_args=()
    if [ -n "$infra_json" ]; then
      infra_args=(-H 'Content-Type: application/json' --data-binary "$infra_json")
    fi
    curl -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
      -D - -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
      -X "$infra_method" "${infra_args[@]}" -H "$infra_auth_header" "$infra_url" ;;
  *) echo "use a https:// URL; not probing" ;;
esac
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

**Citation pinning:** the Mem0 and Onyx Compose citations below are pinned to commits, and each commit was opened and confirmed to contain the fact it is cited for. The LangServe link is a repository root rather than a file, so it cannot be pinned the same way; it was read at commit `27e57afeda13007a7f4e007c5d1f5e8489963aa4`.

- [SearxNG server settings](https://docs.searxng.org/admin/settings/settings_server.html): `server.bind_address`, `server.port`, and direct defaults.
- [SearxNG Docker installation](https://docs.searxng.org/admin/installation-docker.html): documented `8888:8080` publication.
- [LocalAI getting started](https://localai.io/docs/basics/getting_started/): port 8080, Docker publication, `LOCALAI_API_KEY`, and `LOCALAI_AUTH`.
- [Text Embeddings Inference quick tour](https://huggingface.co/docs/text-embeddings-inference/en/quick_tour): container port 80 and host publication 8080.
- [LangServe repository README](https://github.com/langchain-ai/langserve): quickstart bind, application authentication responsibility, deprecation, and successor. Read at commit `27e57afeda13007a7f4e007c5d1f5e8489963aa4`.
- [Mem0 REST API](https://docs.mem0.ai/open-source/features/rest-api): authentication enabled by default, JWTs, `X-API-Key`, `m0sk_` keys, `ADMIN_API_KEY`, and `AUTH_DISABLED`.
- [Mem0 server Compose](https://github.com/mem0ai/mem0/blob/c7ee362aff94a369af70f13f2b4f853f6793ff4c/server/docker-compose.yaml): uvicorn command and API, PostgreSQL, and dashboard publications.
- [Onyx basic authentication](https://docs.onyx.app/deployment/authentication/basic.md): email/password authentication and inert `AUTH_TYPE`.
- [Onyx local Docker deployment](https://docs.onyx.app/deployment/local/docker.md): documented access at `localhost:3000`.
- [Onyx production Compose](https://github.com/onyx-dot-app/onyx/blob/a0370f232ba4e4625131fae518b86e5530e98ec5/deployment/docker_compose/docker-compose.prod.yml): nginx-only host publications.
- [Onyx development Compose](https://github.com/onyx-dot-app/onyx/blob/a0370f232ba4e4625131fae518b86e5530e98ec5/deployment/docker_compose/docker-compose.dev.yml): API and backing-service publications.
- [Docker packet filtering and firewalls](https://docs.docker.com/engine/network/packet-filtering-firewalls/): published ports and firewall interaction.
- [Compose networking](https://docs.docker.com/compose/how-tos/networking/): communication between services without host publication.
- [Compose merge rules](https://docs.docker.com/reference/compose-file/merge/): merged port lists and `!reset`.
- [Docker Compose ps](https://docs.docker.com/reference/cli/docker/compose/ps/): running service information and publication fields.
- [curl manual](https://curl.se/docs/manpage.html): request options, TLS verification, proxy bypass, timing, and error reporting.

