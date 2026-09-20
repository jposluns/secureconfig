# Ollama: it has no built-in authentication or TLS

Ollama's local HTTP API has **no native inbound authentication and no TLS**. A reachable listener gives callers inference and management capabilities, including model acquisition, replacement, export, and deletion. Model metadata may disclose templates and system prompts. Cloud credentials can also authorize upstream use. These capabilities do not establish arbitrary access to every host file. The security boundary for remote access is an authenticating proxy or tunnel, with a policy that separates inference from administration. See the [authentication reference](https://docs.ollama.com/api/authentication) and [server implementation](https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go).

This guide's baseline is **Ollama v0.34.2**, identified as the latest release when checked on **20 September 2026**, at commit **`dfabde4539e42ba1e1eab50a3a50b88aea7958a0`**. Review subsequent releases before changing the deployment pin. See the [release](https://github.com/ollama/ollama/releases/tag/v0.34.2) and [release commit](https://github.com/ollama/ollama/commit/dfabde4539e42ba1e1eab50a3a50b88aea7958a0).

The standalone binary defaults to `127.0.0.1:11434`. The official Docker image instead sets `OLLAMA_HOST=0.0.0.0:11434` inside the container. Under ordinary bridge networking, a bare `-p 11434:11434` publishes that unauthenticated API on every host interface by default. Container binding and host publication are different controls. See the [pinned FAQ](https://github.com/ollama/ollama/blob/v0.34.2/docs/faq.mdx), [Dockerfile](https://github.com/ollama/ollama/blob/v0.34.2/Dockerfile), and [Docker publication reference](https://docs.docker.com/engine/network/port-publishing/).

Rules:

1. Leave the host listener on loopback unless a restricted private path is required.
2. Never expose an unprotected wildcard host listener. Free compute, model tampering, model export, disclosed metadata, and unintended upstream use are meaningful exposure.
3. Publish only an authenticated TLS boundary. Restrict inference identities to the exact inference operations they need.

The numbered settings build one deployment. Merge the selected systemd settings into one drop-in and choose one fronting authentication arrangement. The proxy alternatives are replacements, not additional public paths.

## 1. Make the private listener explicit

**Tier-1 rationale:** an independently reachable backend bypasses every authentication and transport control at the proxy.

For a host-installed systemd service, use `systemctl edit ollama.service`:

```ini
[Service]
Environment="OLLAMA_HOST=127.0.0.1:11434"
```

After assembling the settings below, run `systemctl daemon-reload` and `systemctl restart ollama.service` with the required administrative privileges. Setting the variable in an interactive shell does not change an already running systemd service. See the [Linux environment instructions](https://github.com/ollama/ollama/blob/v0.34.2/docs/faq.mdx).

For the official image under bridge networking, retain its internal wildcard listener and use this publication with a host-run proxy:

```text
-p 127.0.0.1:11434:11434
```

Use Docker Engine **28.0 or later** for this localhost-publication boundary. Before 28.0, other hosts on the same layer-2 segment can reach localhost-published ports; upgrade or leave the port unpublished. Alternatively, omit publication and attach the proxy to a restricted container network. Address Ollama by its container name there: a proxy container's own `127.0.0.1` does not reach Ollama. See [Docker port publishing](https://docs.docker.com/engine/network/port-publishing/).

With `--network host`, Docker ignores `-p`; there is no publication address to constrain. Override the image's `OLLAMA_HOST` with loopback or the deliberately selected private interface, and restrict that private interface to authorized peers.

Loopback permits local callers. An unpublished container remains reachable by permitted network peers. Inspect IPv4, IPv6, every publication, and additional network attachments. A missing `ss` listener does not establish that Docker NAT publication is absent.

**Exposed/fixed comparison, REASONED:** no deployed Ollama host or external observer is available here. An outside observer can obtain an HTTP response from the exposed backend on 11434; after the fix, that direct path is unreachable while the approved proxy path completes inference.

## 2. Put authentication, TLS, and MFA at the fronting layer

**Tier-1 rationale:** every accepted remote request needs an authenticated caller and protected transport.

The local API does not require authentication. Ollama cloud API keys and signing in concern upstream services; they do not protect the local listener. Despite its name, **`OLLAMA_AUTH` is a client-side outbound-signing setting, not an inbound server-authentication switch**. See the [authentication reference](https://docs.ollama.com/api/authentication) and [pinned client implementation](https://github.com/ollama/ollama/blob/v0.34.2/api/client.go).

Ollama serves plaintext HTTP. An `https://` prefix in `OLLAMA_HOST` does not install certificates or enable server TLS. See [server startup](https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go) and [HTTP serving](https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go).

### Option A: reverse proxy with TLS and Basic authentication

Keep Ollama on loopback and publish only the proxy. This nginx fragment belongs inside the existing `http` context; see [nginx.md](nginx.md) for the surrounding configuration. It includes C3's inference-only policy and C6's example admission budgets:

```nginx
# http context: define each zone once.
limit_req_zone $binary_remote_addr zone=ollama_rate:10m rate=2r/s;
limit_conn_zone $server_name zone=ollama_active:10m;

server {
    listen 443 ssl;
    server_name ollama.example.com;

    ssl_certificate     /etc/letsencrypt/live/ollama.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ollama.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    auth_basic           "Ollama";
    auth_basic_user_file /etc/nginx/.htpasswd;

    location = /api/chat {
        if ($request_method != POST) { return 405; }

        client_max_body_size 1m;
        limit_req zone=ollama_rate burst=4 nodelay;
        limit_req_status 429;
        limit_conn ollama_active 4;
        limit_conn_status 429;

        proxy_pass http://127.0.0.1:11434;
        proxy_set_header Host localhost:11434;
        proxy_read_timeout 300s;
    }

    location / {
        return 404;
    }
}
```

Substitute the hostname and certificate paths. Generate password entries with `htpasswd -B -C 12`, using its interactive password prompt and the intended password-file path and username. Bare `-B` defaults to bcrypt cost 5, below OWASP's minimum of 10; regenerate existing cost-5 hashes. Protect the password file and its backups. See [nginx Basic authentication](https://nginx.org/en/docs/http/ngx_http_auth_basic_module.html), [htpasswd](https://httpd.apache.org/docs/2.4/programs/htpasswd.html), and [OWASP password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).

Authentication is at `server` scope so every permitted location inherits it. Do not disable it in an added inference location. A denied path or method can return 404 or 405 before authentication; those responses do not imply access to Ollama.

Retain `proxy_set_header Host localhost:11434;` in every proxied location. The relevant loopback-bound host middleware can reject a public hostname with 403. This rewrite makes that middleware accept the proxy's backend request; **it is not authentication**. See the [pinned host middleware](https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go).

`proxy_read_timeout 300s` permits slow model responses but limits the interval between upstream reads. It is not a five-minute generation deadline: continuous streaming can outlast it. Enforce any total execution deadline in the application or gateway and propagate cancellation. See the [timeout reference](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_read_timeout).

TLS termination protects the client-to-proxy leg. If the proxy and Ollama are on different hosts, protect the backend transport with a tunnel or another verified encrypted transport. See [nginx TLS configuration](https://nginx.org/en/docs/http/ngx_http_ssl_module.html).

### Caddy alternative

The corresponding authentication and path policy in [caddy.md](caddy.md) is:

```caddyfile
ollama.example.com {
    @chat {
        path /api/chat
        method POST
    }

    handle @chat {
        basic_auth {
            admin $2a$14$REPLACE_WITH_HASH_FROM_caddy_hash-password
        }
        reverse_proxy 127.0.0.1:11434 {
            header_up Host localhost:11434
        }
    }

    handle {
        respond 404
    }
}
```

Generate the hash with `caddy hash-password`. The exact matcher and fallback keep other paths private. Stock Caddy has no built-in rate-limiting directive; provide the admission and resource controls in C6 through a suitable fronting layer before publishing this alternative. See [Basic authentication](https://caddyserver.com/docs/caddyfile/directives/basic_auth), [request matchers](https://caddyserver.com/docs/caddyfile/matchers), [exclusive handles](https://caddyserver.com/docs/caddyfile/directives/handle), and [reverse proxy configuration](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy).

### Bearer-only clients

For clients that only send bearer tokens, replace the Basic-auth directives and the two locations in the nginx TLS server with the following. Retain its certificates, protocols, and the `http`-context zones:

```nginx
auth_basic off;

location = /api/chat {
    if ($http_authorization != "Bearer REPLACE_WITH_LONG_RANDOM_TOKEN") { return 401; }
    if ($request_method != POST) { return 405; }

    client_max_body_size 1m;
    limit_req zone=ollama_rate burst=4 nodelay;
    limit_req_status 429;
    limit_conn ollama_active 4;
    limit_conn_status 429;

    proxy_pass http://127.0.0.1:11434;
    proxy_set_header Host localhost:11434;
    proxy_read_timeout 300s;
}

location / {
    return 404;
}
```

Generate the token per [authentication.md](authentication.md) and keep it out of the repository. The exact comparison followed by `return 401` is valid nginx syntax, but it is a **shared static credential stored in configuration, with no constant-time verification guarantee**. Protect configuration dumps, backups, and deployment output. Prefer Basic authentication or an Access service token where suitable. See the [nginx rewrite module](https://nginx.org/en/docs/http/ngx_http_rewrite_module.html).

Apply this authentication check to **every** permitted location added later. Do not retain the former catch-all proxy alongside the allowlist. A token-checking catch-all authenticates management operations too, granting token holders more authority than inference requires.

### Mutual TLS for machine clients

An alternative authentication choice inside the existing TLS server is:

```nginx
ssl_client_certificate /etc/nginx/ollama-client-ca.pem;
ssl_verify_client on;
```

Use a dedicated client CA and define certificate issuance, expiry, and revocation procedures. Remove the Basic-auth requirement if choosing mTLS alone. Combining Basic authentication and mTLS is valid when deliberate; copying fragments must not make both accidental requirements. Retain the inference allowlist and admission controls. See [nginx client-certificate verification](https://nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_verify_client).

### Option B: Cloudflare Tunnel with Access

Follow [cloudflare.md](cloudflare.md) and add an Access policy, or a service-token policy for API clients, on the published hostname. The [Ollama FAQ](https://github.com/ollama/ollama/blob/v0.34.2/docs/faq.mdx) documents tunnelling to `http://localhost:11434`; adding Access authenticates that route, but a direct tunnel to Ollama still gives valid callers its management surface.

For the inference-only deployment, point the tunnel at the local policy proxy instead. Adapt the nginx server above to `listen 127.0.0.1:11435;`, remove its TLS directives, and remove its Basic-auth directives when Access is the selected authentication boundary. Retain the exact locations, limits, and upstream Host rewrite. Route the tunnel to `http://127.0.0.1:11435`. Keep both local listeners unreachable from untrusted peers.

Retain the tunnel route's HTTP Host Header setting of `localhost:11434`, named `originRequest.httpHostHeader` in a config-file tunnel. The final proxy hop also sets that Host header before reaching Ollama. See [origin parameters](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/origin-parameters/) and [Access service tokens](https://developers.cloudflare.com/cloudflare-one/access-controls/service-credentials/service-tokens/).

Access authentication does not itself supply the inference rate, concurrency, or resource budgets. Retain C6's controls; [Cloudflare WAF rate-limiting rules](https://developers.cloudflare.com/waf/rate-limiting-rules/) can provide an additional rate boundary. Configure trusted client-address handling if rate accounting must distinguish callers behind the connector.

MFA: Ollama has no local login, so a second factor comes from the fronting layer: an Access policy backed by an MFA-enforcing identity provider, or an [Authelia](https://www.authelia.com/)-protected proxy. See [mfa.md](mfa.md). Machine service tokens are not a human MFA flow.

**Exposed/fixed comparison, REASONED:** no live proxy, credentials, certificates, or Access deployment is available here. An unprotected listener accepts anonymous inference or exposes credentials over plaintext; the fixed remote path rejects missing or invalid credentials and uses verified TLS for accepted requests.

## 3. Reserve management for administrators

**Tier-1 rationale:** an inference credential must not authorize model replacement, deletion, uploads, or server-initiated transfers.

The C2 server permits only native chat. Its essential routing policy is:

```nginx
# Inside the existing authenticated TLS server.
# Retain C6's admission directives in this permitted location.
location = /api/chat {
    if ($request_method != POST) { return 405; }

    proxy_pass http://127.0.0.1:11434;
    proxy_set_header Host localhost:11434;
    proxy_read_timeout 300s;
}

location / {
    return 404;
}
```

This illustrates the routing component already assembled in C2; do not add duplicate locations. For bearer authentication, retain the token check from C2 inside each permitted location.

Add separately reviewed exact locations only when the application requires them, for example `/api/generate` or `/v1/chat/completions`. Repeat method restrictions, authentication, admission limits, and upstream settings. Allowing `/api/` or `/v1/` wholesale defeats this policy. See nginx [location selection](https://nginx.org/en/docs/http/ngx_http_core_module.html#location) and [return directives](https://nginx.org/en/docs/http/ngx_http_rewrite_module.html).

**A public `/api/tags` may intentionally return 404 even with valid credentials.** Use an allowed inference operation to verify public authentication, and the private administrative path to inspect model inventory.

Keep these operations private:

| API | Authority to keep private |
|---|---|
| `POST /api/pull` | Fetch models and consume local storage and network capacity. |
| `POST /api/push` | Upload model material; upstream registry authorization is separate. |
| `POST /api/create` | Create or replace model definitions and process uploaded model files. |
| `POST /api/copy` | Create another model name. |
| `DELETE /api/delete` | Remove models and associated data. |
| `POST /api/blobs/:digest` | Upload bytes into the model store. |
| `HEAD /api/blobs/:digest` | Discover whether a particular blob exists. |

Methods and blob semantics come from the [pinned API reference](https://github.com/ollama/ollama/blob/v0.34.2/docs/api.md). Administrators can use the loopback endpoint from a restricted host session, or a separately authenticated and network-restricted administrative path. An inference credential must not grant access to that path.

Also exclude account operations, experimental web operations, diagnostics, and unused compatibility routes. The pin registers `/api/me`, `/api/signout`, `/api/user/keys/:encodedKey`, `/api/experimental/web_search`, `/api/experimental/web_fetch`, and a desktop proxy route. Default denial avoids maintaining an exhaustive blacklist. See [route registration](https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go).

Current create requests map filenames to uploaded blob digests. The implementation validates relative filenames and digest paths. Historical arbitrary host-file read/write reports must not be presented as documented v0.34.2 functionality. See [create validation](https://github.com/ollama/ollama/blob/v0.34.2/server/create.go) and [blob-path validation](https://github.com/ollama/ollama/blob/v0.34.2/manifest/paths.go).

Pull, push, and creation still provide server-side transfer and storage authority: an **SSRF-relevant egress and disk-fill surface**. The pin includes redirect restrictions; `insecure` changes protections, including the default same-host redirect restriction in the registry request helper. This is not evidence of an unrestricted, demonstrated SSRF vulnerability. Blocking public management also prevents inference callers from selecting insecure transfers. See [transfer implementation](https://github.com/ollama/ollama/blob/v0.34.2/server/images.go) and [redirect hardening](https://github.com/ollama/ollama/commit/dfabde4539e42ba1e1eab50a3a50b88aea7958a0).

A path allowlist does not constrain model names or generation parameters inside allowed requests. C6 and C7 address those boundaries.

**Exposed/fixed comparison, REASONED:** no live Ollama, proxy, or disposable model fixtures are available here. A valid credential on the former catch-all proxy can create a model alias; the inference-only boundary refuses that operation without forwarding it, while a private administrator can complete it.

## 4. Limit additional browser origins

**Tier-1 rationale:** a browser on a trusted machine must not grant arbitrary websites access to its reachable inference service.

If an explicitly required browser frontend needs an additional origin, add:

```ini
[Service]
Environment="OLLAMA_ORIGINS=https://chat.example.com"
```

Otherwise, leave additional origins unset and remove inherited wildcard assignments. Avoid `*` and blanket extension-origin patterns.

**`OLLAMA_ORIGINS` adds to built-in origins; it does not replace them.** The pin retains localhost, loopback, wildcard-port origins, and application/file/webview schemes. Neither an empty value nor one explicit origin creates an exclusive one-origin policy. See [pinned `AllowedOrigins`](https://github.com/ollama/ollama/blob/v0.34.2/envconfig/config.go).

CORS is not caller authentication and does not constrain a non-browser client. An exclusive browser policy belongs at the frontend boundary. Cross-origin authentication also needs a deliberate preflight policy. C2's POST-only example is intended for non-browser clients or a same-origin backend arrangement; it rejects browser preflight OPTIONS requests.

**Exposed/fixed comparison, REASONED:** no live endpoint or browser frontend is available here. A wildcard additional-origin configuration permits an unwanted website's browser requests; removing that wildcard refuses unnecessary additional origins while an intended browser flow still works. Built-in origins remain exceptions to test, not evidence of an exclusive policy.

## 5. Use a dedicated account and protect the model store

**Tier-1 rationale:** model-store writes and a compromised inference process must not inherit root privileges or unrelated application secrets.

For the vendor-style Linux service:

```ini
[Service]
User=ollama
Group=ollama
UMask=0077
Environment="OLLAMA_MODELS=/var/lib/ollama/models"
```

Ensure the account exists and pre-provision the store. For new directories, an administrator can use `install -d -o ollama -g ollama -m 0700 /var/lib/ollama /var/lib/ollama/models`. Plan migration separately if models already exist elsewhere.

| Object | Proposed ownership and mode |
|---|---|
| `/var/lib/ollama` and model-store directories | `ollama:ollama`, `0700` |
| Model-store regular files | `ollama:ollama`, `0600` |
| Service unit and administrative configuration | Root-owned and not writable by `ollama` |
| Proxy credentials and TLS private keys | Accessible to the required proxy identity, not Ollama |

The account and writable-store requirements follow the [Linux instructions](https://github.com/ollama/ollama/blob/v0.34.2/docs/linux.mdx) and [installer](https://github.com/ollama/ollama/blob/v0.34.2/scripts/install.sh). The restrictive modes are deployment policy; `UMask` is a systemd setting, not an Ollama option. See the [systemd execution reference](https://github.com/systemd/systemd/blob/v257/man/systemd.exec.xml).

`UMask` does not repair existing permissions or ACLs. Inspect existing directories, files, parent-directory access, and backups. Preserve required GPU device-group access. `OLLAMA_MODELS` relocates models, not the entire service home or its signing keys. Do not assume the official container inherits the installer's service-user arrangement.

**Exposed/fixed comparison, REASONED:** no running service, model store, or test identities are available here. Root execution or a broadly writable store permits wider damage or model replacement; the fixed service uses its dedicated identity, required model operations succeed, and an unrelated identity cannot modify the store.

## 6. Bound inference pressure and distinguish limits from defaults

**Tier-1 rationale:** anonymous traffic and compromised authenticated clients must encounter finite admission and resource budgets.

These are illustrative settings to size against the selected models and hardware:

```ini
[Service]
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_MAX_QUEUE=16"
Environment="OLLAMA_KEEP_ALIVE=1m"
Environment="OLLAMA_CONTEXT_LENGTH=4096"
```

At v0.34.2, parallelism defaults to **1**, queue capacity to **512**, and keep-alive to **5 minutes**. Loaded-model capacity is selected automatically when not explicitly configured. See the [environment configuration](https://github.com/ollama/ollama/blob/v0.34.2/envconfig/config.go) and [scheduler](https://github.com/ollama/ollama/blob/v0.34.2/server/sched.go).

Context defaults are **VRAM-dependent: 4K, 32K, or 256K**. The dedicated context document describes 4K below 24 GiB, 32K for the intermediate VRAM band, and 256K at 48 GiB or more. The pinned FAQ's universal 4096 statement is inconsistent with that dedicated document; this example sets 4096 explicitly. See the [pinned context reference](https://github.com/ollama/ollama/blob/v0.34.2/docs/context-length.mdx).

C2 already includes these nginx admission controls. Define the zones once in `http`:

```nginx
limit_req_zone $binary_remote_addr zone=ollama_rate:10m rate=2r/s;
limit_conn_zone $server_name zone=ollama_active:10m;
```

Retain these directives in each permitted inference location:

```nginx
client_max_body_size 1m;
limit_req zone=ollama_rate burst=4 nodelay;
limit_req_status 429;
limit_conn ollama_active 4;
limit_conn_status 429;
```

These are example budgets, not universal recommendations. The first zone accounts by source address; the second shares an active-request budget for this server name. Configure trusted client-address handling when another proxy is in front. The connection limiter does not cap every idle or incomplete connection. See [request limiting](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html), [connection limiting](https://nginx.org/en/docs/http/ngx_http_limit_conn_module.html), and [body-size limits](https://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size).

Context length and keep-alive are **defaults, not mandatory ceilings**. Request parameters can override them, and model defaults also matter. A trusted application or gateway must validate permitted models, `options.num_ctx`, output limits such as `options.num_predict`, and `keep_alive` when untrusted callers receive inference access. A deployment policy might allow one approved model, context at most 4096, at most 128 generated tokens, and keep-alive at most one minute; the nginx path policy does not implement those JSON validations. See [override semantics](https://github.com/ollama/ollama/blob/v0.34.2/docs/faq.mdx) and [request types](https://github.com/ollama/ollama/blob/v0.34.2/api/types.go).

Ollama scheduling limits are not total RAM, VRAM, disk, or HTTP-connection caps. Apply host/container budgets appropriate to the deployment. Use a finite application deadline where required; the nginx idle-read timeout alone is insufficient.

Per [authentication.md](authentication.md) rule 9, authenticated but unthrottled inference remains a denial-of-wallet risk. Apply the same admission controls to the Caddy and Access alternatives.

**Exposed/fixed comparison, REASONED:** no inference runtime, model workload, or GPU is available here. Excess requests enter larger queues or consume more concurrent work in the exposed configuration; explicit admission limits reject excess, accepted requests complete, and normal service recovers. GPU-specific capacity claims require GPU hardware; HTTP admission checks do not.

## 7. Control model provenance and registry transfers

**Tier-1 rationale:** API access must not become permission to install or export arbitrary model material.

Make acquisition an administrative provisioning step. For an illustrative controlled registry, this is a private `POST /api/pull` request body:

```json
{
  "model": "registry.example.com/team/app:release-2026-09",
  "insecure": false,
  "stream": false
}
```

Substitute the approved registry and release before sending it through the private administrative path. Fully qualified registry/namespace/model/tag names are supported. Unqualified names default to Ollama's registry, and an omitted tag defaults to `latest`. See [pinned name parsing](https://github.com/ollama/ollama/blob/v0.34.2/types/model/name.go).

Record the approved artifact or model digest independently, then compare it with deployed inventory before admitting traffic. `/api/tags` supplies model digests. Preserve approved bytes or a controlled registry artifact: a named tag alone does not guarantee immutability. See [model inventory](https://docs.ollama.com/api/tags).

An alternative for a reviewed local GGUF artifact is this **Modelfile**, not a Dockerfile:

```dockerfile
FROM /srv/ollama-import/app.gguf
```

Independently verify the artifact's approved SHA-256 before administrative import. The administrative CLI reads the path during import; this does not mean arbitrary remote API callers can read that host path. See the [Modelfile reference](https://github.com/ollama/ollama/blob/v0.34.2/docs/modelfile.mdx) and [CLI import flow](https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go).

A digest establishes byte identity, not publisher trust or model safety. Do not assume a universal `model@sha256` deployment recipe or native signature enforcement. Restrict deployment egress when only approved registries may be contacted. Keep export authority and registry credentials on the administrative side.

**Exposed/fixed comparison, REASONED:** no controlled registry, approved model artifacts, or live inventory is available here. Exposed management lets callers choose acquisition/export targets and mutate models; the fixed deployment admits independently recorded artifacts through administrators and denies mutation to inference identities.

## 8. Disable unused cloud execution

**Tier-1 rationale:** an exposed local API must not spend the host's upstream authority or send prompts to an unintended remote service.

For a local-only deployment:

```ini
[Service]
Environment="OLLAMA_NO_CLOUD=1"
```

Restart Ollama after changing it. This is the documented control for cloud models and web search. See the [pinned FAQ](https://github.com/ollama/ollama/blob/v0.34.2/docs/faq.mdx).

This is not a general no-network switch. It does not replace management-route restrictions or registry egress policy. `OLLAMA_REMOTES` concerns remote-model hosts; it is not a pull/push registry allowlist. See [environment configuration](https://github.com/ollama/ollama/blob/v0.34.2/envconfig/config.go).

**Exposed/fixed comparison, REASONED:** no signed-in server, authorized cloud fixture, or live local model is available here. A cloud-enabled signed-in server completes an authorized cloud-model request; after disabling cloud functionality, that request is refused while local inference still completes.

## 9. Keep diagnostics private and disable request-body logging

**Tier-1 rationale:** operational endpoints and diagnostic files can disclose deployment details and submitted prompts.

C3's default-deny location also covers diagnostics. Keep `/`, `/api/version`, `/api/status`, `/api/tags`, `/api/ps`, and `/api/show` private unless individually required. Model details may contain templates and system prompts. See the [router](https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go) and [model-details reference](https://docs.ollama.com/api-reference/show-model-details).

Use:

```ini
[Service]
Environment="OLLAMA_DEBUG=0"
Environment="OLLAMA_DEBUG_LOG_REQUESTS=false"
```

Request debugging writes request bodies and replay scripts into a temporary directory. Disabling it prevents new captures; existing captures still need a retention and deletion policy. Protect diagnostic files and ensure proxy/application logging does not independently capture credentials or prompts. See [logging configuration](https://github.com/ollama/ollama/blob/v0.34.2/envconfig/config.go) and the [request logger](https://github.com/ollama/ollama/blob/v0.34.2/server/inference_request_log.go).

No `/metrics` registration appears in the reviewed main router; do not assume a native metrics port. The HTTP server deliberately uses `DefaultServeMux` with a pprof comment, but this review did not establish whether the shipped binary links and registers profiling handlers. Include `/debug/pprof/` in live inventory and public-denial checks. Do not claim either default availability or that `OLLAMA_DEBUG=0` disables profiling. See [HTTP server construction](https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go).

**Exposed/fixed comparison, REASONED:** no runtime, diagnostic files, or live profiling inventory is available here. An exposed deployment returns operational metadata and may capture request bodies; the fixed public boundary denies diagnostics, administrators retain necessary visibility, and disabled request logging creates no new capture.

For the host-installed, local-only example, the assembled systemd drop-in is:

```ini
[Service]
User=ollama
Group=ollama
UMask=0077
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_MODELS=/var/lib/ollama/models"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_MAX_QUEUE=16"
Environment="OLLAMA_KEEP_ALIVE=1m"
Environment="OLLAMA_CONTEXT_LENGTH=4096"
Environment="OLLAMA_NO_CLOUD=1"
Environment="OLLAMA_DEBUG=0"
Environment="OLLAMA_DEBUG_LOG_REQUESTS=false"
```

Add C4's explicit origin only if required, and remove inherited unwanted origins. Apply this to the existing service, reload systemd, and restart once the account, store, and proxy configuration are ready. Preserve GPU access required by the installed service.

## Common mistakes

- Publishing `11434:11434` and assuming the standalone loopback default protects the official container.
- Using `-p` as a host-networking control, or treating an absent `ss` listener as proof that Docker has no published path.
- Treating cloud login, API keys, `OLLAMA_AUTH`, a Host rewrite, or CORS as local inbound authentication.
- Adding `https://` to `OLLAMA_HOST` and assuming the backend now serves TLS.
- Authenticating `/api/generate` while leaving management or compatibility routes reachable.
- Retaining a catch-all proxy beside an inference allowlist, or omitting the bearer check from a newly permitted location.
- Expecting public `/api/tags` to return 200 after intentionally making inventory private.
- Treating one `OLLAMA_ORIGINS` value as an exclusive browser-origin policy.
- Treating context length, keep-alive, or `proxy_read_timeout` as enforced total resource or execution ceilings.
- Assuming a model tag is immutable, `OLLAMA_NO_CLOUD` blocks every network transfer, or `OLLAMA_REMOTES` restricts registries.
- Running as root, leaving the store broadly writable, or assuming `UMask` repairs existing files.
- Disabling debug logging without handling existing captures, or assuming that also disables profiling.

## Verify

All service-behavior checks below are **REASONED, not demonstrated**. The authoring environment has no Ollama, Docker, Podman, nginx, or Caddy executable in `PATH`, no Ollama runtime or GPU, and no supplied authorized deployment, external observer, credentials, or model fixtures. Filesystem and network restrictions prevent provisioning a live comparison here. **Lack of a GPU alone would not prevent listener, API, CORS, or management testing.**

Local validation covered the four Bash fragments with `bash -n`, ShellCheck 0.11.0, and the repository's strict guard-convention scanner. Guard-only tests rejected 74 invalid or incomplete positional-input cases under `bash -u`; four substituted controls reached local markers in place of the operational branch. These observations establish shell and outer-guard behavior only. Native proxy parsing and every service comparison remain open under `OLLAMA-LIVE-1`. The whole-corpus gate suite was not run against this drop-in.

Paste complete blocks, including the parentheses, marker, and count checks. Substitute inside the single quotes on each `set --` line; a literal apostrophe requires shell escaping. The guards assume normal shell builtins and cannot protect a fragment pasted from below them. Use curl 7.75.0 or later for the displayed `exitcode` and `errormsg` variables.

Use isolated exposed and fixed deployments with disposable fixtures. Do not make production public to obtain a baseline. Record binary/image identity, effective configuration, observer location, HTTP results, completed response bodies, upstream observations, state changes, and cleanup without secrets.

### V1. Inspect the listener, identity, and store

**REASONED:** no deployed service, container runtime, store, or test identities are available. Run this on the deployment host with enough privilege to inspect processes and sockets. Use `NONE` for a host-only deployment:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'ollama.service' 'REPLACE_WITH_CONTAINER_NAME_OR_NONE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not inspecting"; exit 1; }
  shift
  [ "$#" -eq 2 ] || { echo "supply unit and container name or NONE"; exit 1; }
  case "$1|$2" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|'|'*|*'|'|*'||'*|*[[:space:]]*)
      echo "replace both values; not inspecting"; exit 1 ;;
    *)
      systemctl cat -- "$1"
      systemctl show --property=User,Group,UMask,Environment,MainPID -- "$1"
      ps -C ollama -o pid,user,group,args
      ss -tlnp
      stat -c '%U:%G %a %n' /var/lib/ollama /var/lib/ollama/models
      getfacl -p /var/lib/ollama /var/lib/ollama/models
      if [ "$2" != NONE ]; then
        docker ps --format 'table {{.Names}}\t{{.Ports}}'
        docker inspect --format '{{json .HostConfig.PortBindings}} {{json .NetworkSettings.Networks}} {{json .Config.User}}' -- "$2"
      fi
      ;;
  esac
)
```

For container-only deployments, systemd inspection may be inapplicable. Inspect the actual container process identity and mounted store; an empty configured container user is not proof of an unprivileged process. Inspect every relevant network namespace, IPv4/IPv6 address, publication, and network attachment.

The exposed comparison shows unintended listeners/publications, root execution, or writable model state. The fixed comparison shows the intended private path and dedicated identity. Check existing regular files and ACLs, service-home signing keys, root-owned configuration, and proxy key separation too.

From an unrelated unprivileged test account, run `test -w /var/lib/ollama/models` and inspect its exit status; writable access is a failure of the proposed policy. In an isolated store, confirm that identity cannot create a disposable file, while the service identity can perform the approved import/inference workflow. Pair ownership inspection with V4's successful administrative operation and V3's inference control.

Expected behavior follows C1's [Docker publication reference](https://docs.docker.com/engine/network/port-publishing/) and C5's [Linux service instructions](https://github.com/ollama/ollama/blob/v0.34.2/docs/linux.mdx).

### V2. Probe direct-backend bypass from another machine

**REASONED:** no deployed target or disallowed external observer is available. Use the actual deployment address, not a documentation address. For IPv6, supply the actual address enclosed in square brackets inside the quotes. Repeat for each deployed address family and publication:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "supply exactly one address; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|*'<'*|*'>'*|*example.com*|""|*@*|*/*|*\?*|*\#*|*[[:space:]]*|203.0.113.*|198.51.100.*|192.0.2.*|*2001:db8*)
      echo "supply the real deployment address; not probing"; exit 1 ;;
    *)
      curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
        -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "http://$1:11434/api/tags"
      ;;
  esac
)
```

Exposed: an HTTP response establishes that the direct port answered, even if its status is an error. Fixed: refusal or timeout attributable to the actual disallowed remote path, paired with successful inference through the approved proxy.

Read `err`, not merely the exit number. A resolver failure, local socket error, wrong address, stopped service, or unexplained timeout is inconclusive. Correlate the result with V1 and firewall evidence. See C1's [binding documentation](https://github.com/ollama/ollama/blob/v0.34.2/docs/faq.mdx).

### V3. Verify authentication and TLS with a real inference request

**REASONED:** no proxy deployment, trusted certificates, credentials, or loaded model is available. Prepare a small approved local model and a request body file such as `chat.json`:

```json
{
  "model": "REPLACE_WITH_APPROVED_LOCAL_MODEL",
  "messages": [
    {
      "role": "user",
      "content": "Reply with the word ready."
    }
  ],
  "stream": false,
  "options": {
    "num_predict": 16
  }
}
```

Replace the model before probing. Keep fixture prompts non-sensitive.

Prepare client configuration files with mode `0600` in a private directory. For Basic authentication, the correct-credential file contains:

```text
user = "admin:REPLACE_WITH_PASSWORD"
```

Prepare a separate file containing the deliberately wrong password and a separate empty file for no credentials. For bearer authentication, use this file content instead:

```text
header = "Authorization: Bearer REPLACE_WITH_TOKEN"
```

For mTLS, add the required trust and certificate paths:

```text
cacert = "/absolute/path/to/server-ca.pem"
cert = "/absolute/path/to/client-cert.pem"
key = "/absolute/path/to/client-key.pem"
```

Use the normal trust store when appropriate. Escape backslashes and double quotes according to curl's configuration-file syntax. Never put live passwords, bearer tokens, or Access secrets on the command line.

Inspect these files before use: allow only the intended authentication, trust, client-certificate, and test-header settings. Do not include URLs, redirects, proxy settings, insecure TLS options, extra transfers, or request/output overrides. An intentional `resolve` entry can support a hostname-negative test against the same server address. The files are trusted test inputs, not a safe format for untrusted instructions.

The following reusable probe reads the client configuration on stdin, keeping credentials off curl's argv. It supports the concrete operations in V3 through V8. Use `/dev/null` as the body for GET, HEAD, and OPTIONS. Use `application/octet-stream` for blob bytes and `application/json` for JSON fixtures.

```bash
(
  set +x
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ENDPOINT_URL' 'POST' 'REPLACE_WITH_BODY_FILE_OR_DEV_NULL' 'REPLACE_WITH_CURL_CONFIG_FILE' 'application/json'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 5 ] || { echo "supply URL, method, body file, client config, and content type"; exit 1; }
  case "$1|$2|$3|$4|$5" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|'|'*|*'|'|*'||'*|*[[:cntrl:]]*)
      echo "replace every value; not probing"; exit 1 ;;
    *)
      case "$1" in
        *@*|*\?*|*\#*|*[[:space:]]*) echo "use a URL without credentials, query, or fragment"; exit 1 ;;
        https://*|http://127.0.0.1:11434/*|http://localhost:11434/*) ;;
        *) echo "use HTTPS, or the administrative loopback endpoint"; exit 1 ;;
      esac
      case "$2" in
        GET|HEAD|OPTIONS)
          [ "$3" = /dev/null ] || { echo "use /dev/null for this method"; exit 1; } ;;
        POST|DELETE) ;;
        *) echo "unsupported test method"; exit 1 ;;
      esac
      case "$5" in
        application/json|application/octet-stream) ;;
        *) echo "choose the fixture content type"; exit 1 ;;
      esac
      [ -r "$3" ] || { echo "body file is unreadable"; exit 1; }
      [ -r "$4" ] || { echo "client config is unreadable"; exit 1; }
      case "$(< "$4")" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*)
          echo "replace placeholders in the client config; not probing"; exit 1 ;;
      esac
      case "$2" in
        HEAD) set -- "$4" --head --url "$1" ;;
        GET|OPTIONS) set -- "$4" --request "$2" --url "$1" ;;
        POST|DELETE) set -- "$4" --request "$2" --url "$1" \
          --header "Content-Type: $5" --data-binary "@$3" ;;
      esac
      curl -q -g -sS --config - --noproxy '*' --connect-timeout 5 --max-time 120 \
        --dump-header /dev/stderr \
        -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "${@:2}" < "$1"
      ;;
  esac
)
```

For the public authentication comparison, use the actual HTTPS `/api/chat` URL, POST, and the same valid `chat.json` each time:

| Client configuration | Exposed comparison | Fixed comparison |
|---|---|---|
| Empty, no credentials | Unprotected API completes inference. | Basic/bearer boundary rejects with 401 and no upstream inference request. |
| Deliberately wrong credentials | Credentials do not protect an unprotected API. | Request is rejected, never accepted inference. |
| Correct credentials | Request completes. | HTTP 200 with a completed, successful inference response. |

For mTLS, retain a valid client certificate while testing missing Basic credentials if both mechanisms are deliberately required. Test missing and untrusted client certificates separately; both must fail before inference. nginx may report a TLS failure or a proxy rejection depending on the failure stage.

Repeat the valid request with a correct hostname and trust chain, an unrelated valid CA trust file, and a wrong hostname directed to the same server. Correct trust succeeds; wrong trust or hostname must fail certificate verification. Do not use `-k`. A missing local certificate file is not evidence that the server enforced mTLS.

For Access, use protected client-config header entries for the required service-token fields. Verify missing/wrong-token denial and valid-token inference. For a human MFA policy, use the actual browser login flow; a service-token request does not demonstrate MFA.

Retain the original model-inventory check with corrected expectations: use V3 with `GET /api/tags` and `/dev/null`. On the public C3 boundary, expect 404 even with valid inference credentials. On the approved private administrative path, expect 200 with model-list JSON. A public 404 is not an authentication test.

A streamed 200 alone does not prove model work succeeded. Inspect the complete response, including completion and error fields. Transport failures, rate-limit rejection, missing models, and timeouts are distinct from authentication denial. Inspect proxy and upstream records without logging credentials or bodies.

These comparisons follow C2's [authentication reference](https://docs.ollama.com/api/authentication), [nginx Basic authentication](https://nginx.org/en/docs/http/ngx_http_auth_basic_module.html), [client-certificate verification](https://nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_verify_client), and the [curl manual](https://curl.se/docs/manpage.html).

### V4. Exercise management authorization and blob writes

**REASONED:** no isolated model store, registry fixtures, administrative identity, or live proxy is available. Use V3's reusable probe against three paths: an isolated exposed catch-all proxy, the fixed public inference proxy, and the private administrative endpoint. Direct loopback requests run on the service host with an empty client configuration.

Prepare valid, disposable fixtures. The exposed comparison must demonstrate actual authorized operations, not malformed-request errors.

| Operation for V3 | Body or fixture | Evidence to retain |
|---|---|---|
| `POST /api/copy` | `{"source":"REPLACE_WITH_SOURCE_MODEL","destination":"REPLACE_WITH_DISPOSABLE_ALIAS"}` | Alias appears in private `/api/tags` inventory after exposed/private success. |
| `POST /api/create` | `{"model":"REPLACE_WITH_DISPOSABLE_MODEL","from":"REPLACE_WITH_REVIEWED_GGUF_MODEL","stream":false}` | Successful completion and the new definition in private inventory. |
| `POST /api/pull` | C7's pull body, substituted for a small controlled registry fixture. | Successful transfer and the expected deployed digest. |
| `POST /api/push` | `{"model":"REPLACE_WITH_CONTROLLED_EXPORT_MODEL","insecure":false,"stream":false}` | Authorized test registry receives the intended disposable artifact. |
| `DELETE /api/delete` | `{"model":"REPLACE_WITH_DISPOSABLE_ALIAS"}` | Only the selected disposable name disappears. |
| `POST /api/blobs/sha256:REPLACE_WITH_FIXTURE_SHA256` | A small file containing unique non-sensitive bytes; use `application/octet-stream`. | Upload succeeds and subsequent HEAD finds that digest. |
| `HEAD /api/blobs/sha256:REPLACE_WITH_FIXTURE_SHA256` | `/dev/null` | Existence result distinguishes a stored fixture from a fresh absent digest. |

Substitute the JSON values before use. Calculate the blob fixture's SHA-256 locally with `sha256sum` and place its hexadecimal digest after `sha256:` in the URL. Never use a disk-filling workload.

For the fixed public boundary, every management request must return 404 without an upstream request or state change, even with valid inference credentials. Confirm the operation succeeds for the private administrator, then remove disposable aliases/models and clean up the isolated registry/store. Do not manually delete shared production blobs.

Also test the account and experimental methods registered at the pin: POST to `/api/me`, `/api/signout`, `/api/experimental/web_search`, and `/api/experimental/web_fetch`, plus DELETE to `/api/user/keys/:encodedKey`, using an isolated account where state can change. Inventory the deployed desktop proxy route and unused compatibility endpoints and confirm public denial. Never sign out or delete keys on a production account merely to obtain evidence.

Use proxy upstream-status records or equivalent observation to distinguish a proxy-generated 404 from an upstream error. Pair each denial set with successful public `/api/chat`.

The discriminators are C3's [API methods](https://github.com/ollama/ollama/blob/v0.34.2/docs/api.md), [route registration](https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go), and [create validation](https://github.com/ollama/ollama/blob/v0.34.2/server/create.go).

### V5. Compare browser origins and preflights

**REASONED:** no live backend or authorized browser frontend is available. Use V3 with OPTIONS, `/dev/null`, and a client configuration containing these non-secret test headers:

```text
header = "Origin: https://REPLACE_WITH_BROWSER_ORIGIN"
header = "Access-Control-Request-Method: POST"
header = "Access-Control-Request-Headers: content-type"
```

Run against the private test backend to isolate Ollama's CORS behavior, then against the actual frontend boundary. Repeat with the required origin, an unrelated controlled origin, representative built-in origins, and no Origin header.

Exposed: with wildcard additional origins, the unrelated browser origin is permitted. Fixed: unnecessary additional origins are refused; required origins still work. Inspect access-control response headers and perform an actual browser request, because curl itself does not enforce CORS.

For the C2 POST-only proxy, OPTIONS returns 405 and is not forwarded. That is the expected non-browser policy, not a successful cross-origin frontend deployment. If a cross-origin browser frontend is required, demonstrate its separately designed preflight/authentication flow, including any authorization header it needs.

Repeat the actual POST with and without Origin. Removing Origin must not bypass proxy authentication; a non-browser caller with valid credentials is not constrained by CORS. The built-in origins remain as described by C4's [AllowedOrigins implementation](https://github.com/ollama/ollama/blob/v0.34.2/envconfig/config.go).

### V6. Exercise finite admission and resource budgets

**REASONED:** no inference runtime, loaded models, capacity fixture, or GPU is available. The following probe launches exactly eight requests, each bounded to 120 seconds, waits for every child, and retains separate results. Use only an isolated capacity test with the same small, valid chat fixture as V3:

```bash
(
  set +x
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_CHAT_URL' 'REPLACE_WITH_CHAT_BODY_FILE' 'REPLACE_WITH_CURL_CONFIG_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 3 ] || { echo "supply URL, body file, and client config"; exit 1; }
  case "$1|$2|$3" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|'|'*|*'|'|*'||'*|*[[:cntrl:]]*)
      echo "replace every value; not probing"; exit 1 ;;
    *)
      case "$1" in
        *@*|*\?*|*\#*|*[[:space:]]*) echo "use a URL without credentials, query, or fragment"; exit 1 ;;
        https://*/api/chat) ;;
        *) echo "use the HTTPS chat URL"; exit 1 ;;
      esac
      [ -r "$2" ] || { echo "body file is unreadable"; exit 1; }
      [ -r "$3" ] || { echo "client config is unreadable"; exit 1; }
      case "$(< "$3")" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*)
          echo "replace placeholders in the client config; not probing"; exit 1 ;;
      esac
      ollama_probe_dir=$(mktemp -d) || { echo "cannot create result directory"; exit 1; }
      chmod 700 "$ollama_probe_dir" || { echo "cannot protect results"; exit 1; }
      ollama_probe_pids=()
      for ollama_probe_n in 1 2 3 4 5 6 7 8; do
        curl -q -g -sS --config - --noproxy '*' --connect-timeout 5 --max-time 120 \
          --request POST --header 'Content-Type: application/json' --data-binary "@$2" \
          --output "$ollama_probe_dir/$ollama_probe_n.body" \
          -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1" \
          < "$3" > "$ollama_probe_dir/$ollama_probe_n.status" \
          2> "$ollama_probe_dir/$ollama_probe_n.stderr" &
        ollama_probe_pids+=("$!")
      done
      for ollama_probe_pid in "${ollama_probe_pids[@]}"; do
        if wait "$ollama_probe_pid"; then
          :
        else
          echo "one transfer failed; inspect its status and stderr"
        fi
      done
      printf 'Results retained in %s\n' "$ollama_probe_dir"
      ;;
  esac
)
```

Exposed: without admission limits, the workload reaches Ollama subject to its own scheduler. Fixed: excess requests receive the configured proxy 429 responses while accepted requests complete. Inspect limiter/upstream evidence to identify which control acted. After the bounded burst ends and the rate budget recovers, repeat one ordinary request and require successful inference.

A fast fixture may not hold four requests active simultaneously. To demonstrate the connection limit separately, use a bounded fixture that keeps four accepted requests active, pace their admission within the rate budget, then attempt one additional request from another test client. It must be rejected while the accepted requests complete; freeing a slot must permit another request. An eight-request burst alone does not prove both limiters acted.

Using V3, also perform these comparisons:

| Operation | Exposed versus fixed evidence |
|---|---|
| Submit a valid chat JSON file of 1,048,577 bytes, using harmless JSON whitespace for padding. | Without the selected body cap it can reach upstream; the 1 MiB public limit returns 413 without an upstream request. Pair with a small accepted body. |
| Request a second approved small model and inspect private `GET /api/ps`. | Compare automatic loaded-model behavior with the explicit one-model budget; record loading, eviction, and recovery. |
| Send a request without `keep_alive`, then inspect `/api/ps` before and after the selected expiry. | Compare the five-minute default with the configured one-minute default, allowing observation overhead. |
| Attempt `options.num_ctx: 8192`, `options.num_predict: 256`, `keep_alive: "2m"`, and a disallowed model under the illustrative gateway policy. | Direct Ollama may accept overrides; the validating gateway must reject or constrain them. Environment defaults and the nginx path policy alone do not pass this check. |
| Fill the scheduler queue with an isolated bounded workload that actually enters it. | Compare default and explicit queue capacities using scheduler observations and completed requests. Do not infer that the seventeenth HTTP request must return 503. |

The public four-active-request budget may prevent a single test client from filling Ollama's sixteen-entry scheduler queue. Test scheduler behavior separately through the isolated private test path, with an explicit workload bound and cleanup. Do not remove production proxy limits.

These comparisons follow C6's [scheduler](https://github.com/ollama/ollama/blob/v0.34.2/server/sched.go), [request override types](https://github.com/ollama/ollama/blob/v0.34.2/api/types.go), and nginx [request](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html), [connection](https://nginx.org/en/docs/http/ngx_http_limit_conn_module.html), and [body](https://nginx.org/en/docs/http/ngx_http_core_module.html#client_max_body_size) limits.

### V7. Check provenance, cloud disablement, and administrative egress

**REASONED:** no approved artifact inventory, controlled registry, cloud credentials, or live server is available.

Use V3 for private `GET /api/tags`. Compare each deployed model digest with the independently approved inventory. For a GGUF import, compare `sha256sum /srv/ollama-import/app.gguf` with the approved artifact checksum before import. The raw GGUF SHA-256 and a model manifest digest are different identifiers; record each for its purpose.

Exposed: callers can install or export arbitrary chosen material through public management. Fixed: V4's public mutations are denied, administrative provisioning yields the approved model digest, and ordinary inference succeeds. Where registry exclusivity is required, compare an approved transfer with a small transfer to a separately controlled disallowed registry. The egress boundary must deny the latter without blocking the former.

For C8, use V3's POST `/api/chat` with a currently authorized cloud-model fixture and a non-sensitive prompt. In the isolated cloud-enabled state, establish a completed response. After setting `OLLAMA_NO_CLOUD=1` and restarting, require a cloud-disabled refusal, then repeat the local-model positive control. An invalid model or missing upstream credential is not proof of cloud disablement.

Sources: C7's [model inventory](https://docs.ollama.com/api/tags) and [transfer implementation](https://github.com/ollama/ollama/blob/v0.34.2/server/images.go), and C8's [cloud-disable documentation](https://github.com/ollama/ollama/blob/v0.34.2/docs/faq.mdx).

### V8. Inspect diagnostics, profiling, and prompt captures

**REASONED:** no running binary, diagnostic fixtures, or service temporary directory is available.

Use V3's probe with valid public inference credentials and then through the private administrative path:

| Method | Path | Body |
|---|---|---|
| GET | `/` | `/dev/null` |
| GET | `/api/version` | `/dev/null` |
| GET | `/api/status` | `/dev/null` |
| GET | `/api/tags` | `/dev/null` |
| GET | `/api/ps` | `/dev/null` |
| POST | `/api/show` | `{"model":"REPLACE_WITH_APPROVED_LOCAL_MODEL"}` in a substituted fixture file |
| GET | `/debug/pprof/` | `/dev/null` |

Exposed: registered operational routes disclose their responses through the catch-all boundary. Fixed: public requests return 404 without reaching upstream, while private administrative diagnostics still work. Pair the denial set with successful public chat.

For `/debug/pprof/`, first observe the actual private binary. If no handler exists, record that absence; do not call it proof that debug settings disabled profiling. If it exists, retain the observed response and demonstrate public denial.

For logging, use an isolated service and a unique non-sensitive prompt. With request debugging deliberately enabled only for the comparison, send one completed V3 request and inspect the service's actual temporary-directory namespace for `ollama-request-logs-*`, request bodies, and replay scripts. Then apply C9, restart, send another completed request, and verify that no new request capture is created. Account for a service-specific `TMPDIR` or private temporary namespace. Retain timestamps and file evidence without sharing captured prompts or credentials, then clean up the test captures.

Expected behavior follows C9's [router](https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go) and [request logger](https://github.com/ollama/ollama/blob/v0.34.2/server/inference_request_log.go).

### Native proxy parsing

Parsing is an offline check, but it was **not demonstrated here** because nginx and Caddy are absent. On the deployment host, run `nginx -t` against the assembled configuration and real referenced certificate/password files before reloading. For the Caddy alternative, run `caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile`.

These commands validate configuration acceptance; they do not prove authentication, management denial, TLS enforcement, or resource behavior. Avoid sharing `nginx -T` output from a bearer configuration because it contains the shared token. See the [nginx command reference](https://nginx.org/en/docs/switches.html) and [Caddy validation reference](https://caddyserver.com/docs/command-line#caddy-validate).

### Demonstration backlog

| ID | Status | Closure evidence |
|---|---|---|
| **OLLAMA-LIVE-1** | **OPEN - REASONED; service behavior and native proxy parsing not demonstrated** | On v0.34.2 or a newly reviewed explicit pin, load the assembled service/proxy configuration and reproduce every applicable exposed/fixed comparison above in isolated states. Record binary/image identity, effective configuration, commands, responses, upstream observations, completed positive controls, state changes, and cleanup without secrets. Include IPv4/IPv6 and Docker bypass paths; absent/wrong/correct authentication; TLS trust and mTLS negatives; all management methods and blob writes; browser preflights and actual calls; finite admission, scheduler observations, parameter overrides, and recovery; effective identity, ACLs, and model digests; controlled registry transfers; cloud disablement; diagnostic denial, prompt-capture behavior, and actual profiling availability. Use CPU fixtures where sufficient and GPU hardware for GPU-specific claims. Configuration inspection or `nginx -t` alone does not close this row. |

## Sources (checked September 2026)

- Ollama v0.34.2 release: https://github.com/ollama/ollama/releases/tag/v0.34.2
- Ollama release commit and redirect hardening: https://github.com/ollama/ollama/commit/dfabde4539e42ba1e1eab50a3a50b88aea7958a0
- Ollama repository at the reviewed tag: https://github.com/ollama/ollama/tree/v0.34.2
- Ollama FAQ: https://docs.ollama.com/faq
- Pinned FAQ, service environment, proxy examples, overrides, and cloud disablement: https://github.com/ollama/ollama/blob/v0.34.2/docs/faq.mdx
- Local API authentication: https://docs.ollama.com/api/authentication
- Official Docker image wildcard listener: https://github.com/ollama/ollama/blob/v0.34.2/Dockerfile
- Linux service instructions: https://github.com/ollama/ollama/blob/v0.34.2/docs/linux.mdx
- Linux installer and service account: https://github.com/ollama/ollama/blob/v0.34.2/scripts/install.sh
- Environment configuration and additive origins: https://github.com/ollama/ollama/blob/v0.34.2/envconfig/config.go
- API methods and blob operations: https://github.com/ollama/ollama/blob/v0.34.2/docs/api.md
- HTTP serving, routes, and host middleware: https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go
- Client-side outbound signing: https://github.com/ollama/ollama/blob/v0.34.2/api/client.go
- Server startup and administrative import: https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go
- Create-file validation: https://github.com/ollama/ollama/blob/v0.34.2/server/create.go
- Blob-path validation: https://github.com/ollama/ollama/blob/v0.34.2/manifest/paths.go
- Registry transfers and redirect restrictions: https://github.com/ollama/ollama/blob/v0.34.2/server/images.go
- Registry and model-name parsing: https://github.com/ollama/ollama/blob/v0.34.2/types/model/name.go
- Modelfile reference: https://github.com/ollama/ollama/blob/v0.34.2/docs/modelfile.mdx
- Model inventory and digests: https://docs.ollama.com/api/tags
- Model details: https://docs.ollama.com/api-reference/show-model-details
- Scheduler: https://github.com/ollama/ollama/blob/v0.34.2/server/sched.go
- VRAM-dependent context defaults: https://github.com/ollama/ollama/blob/v0.34.2/docs/context-length.mdx
- Request options and overrides: https://github.com/ollama/ollama/blob/v0.34.2/api/types.go
- Request-body logging: https://github.com/ollama/ollama/blob/v0.34.2/server/inference_request_log.go
- Docker publication and the pre-28.0 same-L2 caveat: https://docs.docker.com/engine/network/port-publishing/
- systemd identities, environment, and umask: https://github.com/systemd/systemd/blob/v257/man/systemd.exec.xml
- nginx Basic authentication: https://nginx.org/en/docs/http/ngx_http_auth_basic_module.html
- nginx TLS and client-certificate verification: https://nginx.org/en/docs/http/ngx_http_ssl_module.html
- nginx locations and request-body size: https://nginx.org/en/docs/http/ngx_http_core_module.html
- nginx conditions and returns: https://nginx.org/en/docs/http/ngx_http_rewrite_module.html
- nginx proxy headers and timeout semantics: https://nginx.org/en/docs/http/ngx_http_proxy_module.html
- nginx request-rate limiting: https://nginx.org/en/docs/http/ngx_http_limit_req_module.html
- nginx connection limiting: https://nginx.org/en/docs/http/ngx_http_limit_conn_module.html
- nginx configuration testing: https://nginx.org/en/docs/switches.html
- Apache htpasswd bcrypt options: https://httpd.apache.org/docs/2.4/programs/htpasswd.html
- OWASP bcrypt work-factor guidance: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- Caddy Basic authentication: https://caddyserver.com/docs/caddyfile/directives/basic_auth
- Caddy request matchers: https://caddyserver.com/docs/caddyfile/matchers
- Caddy exclusive handles: https://caddyserver.com/docs/caddyfile/directives/handle
- Caddy reverse proxy: https://caddyserver.com/docs/caddyfile/directives/reverse_proxy
- Caddy validation and password hashing: https://caddyserver.com/docs/command-line
- Cloudflare Tunnel origin parameters: https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/origin-parameters/
- Cloudflare Access service tokens: https://developers.cloudflare.com/cloudflare-one/access-controls/service-credentials/service-tokens/
- Cloudflare WAF rate-limiting rules: https://developers.cloudflare.com/waf/rate-limiting-rules/
- curl configuration input, timeouts, and write-out variables: https://curl.se/docs/manpage.html
