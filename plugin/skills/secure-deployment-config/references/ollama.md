# Ollama: it has no built-in authentication or TLS

Ollama runs AI language models on your own machine and serves them to other apps through a local web API. This guide helps your AI assistant configure it securely, including a private listener, login, TLS and MFA at a fronting layer, model management limited to administrators, and bounded inference load.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/ollama.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against Ollama v0.34.2, Docker Engine localhost boundary 28.0, systemd v257, Go go1.26.5, go1.26.0, go1.26.1, go1.26.2, go1.26.3, go1.26.4, go1.26.6, go1.26.7, go1.26.8, go1.26.9, and go1.26.10, and github.com/dgryski/trifles v0.0.0-20200323201526-dd97f9abfb48, plus 3 more recorded bases; 1 further source is pinned to a commit and 7 carry no recorded version. Metadata reviewed 2026-10-22; documentation checked September 2026. The guide records 79 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

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

Substitute the hostname and certificate paths. Generate password entries with `htpasswd -B -C 12`, using its interactive password prompt and the intended password-file path and username. The prompt keeps the password out of the command text, shell history and shell tracing; the account owner and root can still read it in the `htpasswd` process while it runs. Bare `-B` defaults to bcrypt cost 5, below OWASP's minimum of 10; regenerate existing cost-5 hashes. Protect the password file and its backups. See [nginx Basic authentication](https://nginx.org/en/docs/http/ngx_http_auth_basic_module.html), [htpasswd](https://httpd.apache.org/docs/2.4/programs/htpasswd.html), and [OWASP password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html).

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

Generate the hash with `caddy hash-password`. Run it without `--plaintext`, which would put the password in its arguments, and enter the password at its prompt. The prompt keeps the password out of the command text, shell history and shell tracing; the account owner and root can still read it in the `caddy` process while it runs. The exact matcher and fallback keep other paths private. Stock Caddy has no built-in rate-limiting directive; provide the admission and resource controls in C6 through a suitable fronting layer before publishing this alternative. See [Basic authentication](https://caddyserver.com/docs/caddyfile/directives/basic_auth), [request matchers](https://caddyserver.com/docs/caddyfile/matchers), [exclusive handles](https://caddyserver.com/docs/caddyfile/directives/handle), and [reverse proxy configuration](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy).

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

For the inference-only deployment, point the tunnel at the local policy proxy instead. Adapt the nginx server above to `listen 127.0.0.1:11435;`, remove its TLS directives, and remove its Basic-auth directives when Access is the selected authentication boundary. Retain the exact locations, limits, and upstream Host rewrite. Route the tunnel to `http://127.0.0.1:11435`. Keep both local listeners unreachable from untrusted peers. On a Mac running the Ollama desktop app, its Claude Desktop gateway, when on, also uses `127.0.0.1:11435` (section 9): this guide's inference, not observed, is that the gateway and this proxy would both try to bind that port.

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

Context defaults are **VRAM-dependent: 4K, 32K, or 256K**. The dedicated context document describes 4K below 24 GiB, 32K for the intermediate VRAM band, and 256K at 48 GiB or more; the implementation selects these tiers slightly lower, at roughly 23 GiB and 47 GiB of summed detected VRAM after the configured GPU overhead, so treat the documented figures as nominal. The pinned FAQ's universal 4096 statement is inconsistent with that dedicated document; this example sets 4096 explicitly. See the [pinned context reference](https://github.com/ollama/ollama/blob/v0.34.2/docs/context-length.mdx) and [server startup](https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go).

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

No `/metrics` registration appears in the [reviewed main router](https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go); do not assume a native metrics port. The [CLI entry point](https://github.com/ollama/ollama/blob/v0.34.2/main.go#L3-L13) runs the CLI built by [`NewCLI`](https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go#L2377-L2654), which [registers](https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go#L2632-L2654) the [serve command (`start` alias)](https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go#L2469-L2475), whose [server path](https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go#L2093-L2109) calls [`server.Serve`](https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go#L1938-L2060) (the [`server` import](https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go#L3-L60) names the [`server` package](https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go#L1)) when invoked as `serve` or `start`. That function [registers the generated router with `http.Handle("/", h)`](https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go#L1987-L1992), creates an HTTP server with a [nil `Handler` and a comment saying `http.DefaultServeMux` was chosen to get `net/http/pprof` for free](https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go#L2001-L2011), and [serves the listener](https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go#L2052-L2057). The [server import block](https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go#L3-L54) has no `net/http/pprof` import. This guide's source assessment is that first-party code in v0.34.2 registers no pprof handler: its non-test Go code has no `net/http/pprof` import, pprof handler registration, or `/debug/pprof` route. A `go list` import resolution run for this guide on 21 October 2026 with Go 1.26.5, for the main package at v0.34.2 (commit `dfabde45`) on linux, darwin and windows amd64 with cgo on and off, listed neither `net/http/pprof` nor `runtime/pprof` in any of its six package lists (413 to 419 import paths each). Twelve further `go list -deps .` runs for this guide on 21 October 2026, in the v0.34.2 tree root with Go 1.26.5 on a linux/amd64 host, `GOFLAGS=-mod=readonly` and the default `GOPROXY`, each exited 0 and listed neither `net/http/pprof` nor `runtime/pprof` in any of their twelve package lists (411 to 418 import paths each; the only path containing `pprof` in each is `internal/runtime/pprof/label`): default tags on linux and darwin arm64 with cgo on and off, and on windows arm64 and freebsd, openbsd, netbsd and solaris amd64 with cgo off; and, with cgo off, `-tags updater_live` on windows amd64 and darwin arm64 and `-tags release,library` on linux amd64. The darwin arm64 list with `-tags updater_live` is identical to the one without. In the tree's first-party `//go:build` lines at v0.34.2, the custom tags `integration` (for example [`integration/basic_test.go`](https://github.com/ollama/ollama/blob/v0.34.2/integration/basic_test.go#L1)), `fast`, `release` and `library` ([`integration/reg_groups_test.go`](https://github.com/ollama/ollama/blob/v0.34.2/integration/reg_groups_test.go#L1)), `generate` ([`integration/generate_jinja_test.go`](https://github.com/ollama/ollama/blob/v0.34.2/integration/generate_jinja_test.go#L1)) and `updater_live` ([`app/updater/updater_live_test.go`](https://github.com/ollama/ollama/blob/v0.34.2/app/updater/updater_live_test.go#L1)) gate only `_test.go` files, and `appengine` and `os400` appear only in the [constraint of `readline/term.go`, whose only import is `syscall`](https://github.com/ollama/ollama/blob/v0.34.2/readline/term.go#L1-L7). This guide's inference, not run, is that the test-only tags select no additional first-party non-test files, because `_test.go` files are not part of a non-test build ([`go build` ignores files that end in `_test.go`](https://github.com/golang/go/blob/go1.26.5/src/cmd/go/alldocs.go#L83) in Go 1.26.5), so they leave the main package's first-party imports unchanged; the dependency search below ignores build constraints, so which dependency modules' files those tags select was not determined, though the sweep below shows that `generate` selects a `github.com/rivo/uniseg` file.

A further 227 `go list -deps .` runs were made for this guide on 22 October 2026 in the v0.34.2 tree (commit `dfabde45`) with Go 1.26.5 on a linux/amd64 host, using `/usr/local/go/bin/go` with `GOENV=off`, `GOTOOLCHAIN=local`, `GOWORK=off`, `GOFLAGS=-mod=readonly`, `GOPROXY=off` and a module cache filled by `go mod download` (all modules verified, with a clean tree afterwards); like the runs above, they resolve imports without compiling a binary or running Ollama code. They cover default tags for all 47 GOOS/GOARCH pairs that Go 1.26.5's `go tool dist list` reports, with cgo off, and for the 40 of those that report cgo support, with cgo on; and, with cgo off and on, the tag sets `updater_live`, `release,library`, `appengine`, `os400`, `appengine,os400`, `integration,fast,generate,release,library,updater_live` and those six tags plus `appengine` and `os400`, each on linux 386, amd64, arm and arm64, darwin amd64 and arm64, windows 386, amd64 and arm64, and aix ppc64. The 182 runs that exited 0 listed neither `net/http/pprof` nor `runtime/pprof`, and the only path containing `pprof` in any of their lists is `internal/runtime/pprof/label`: 82 default-tag runs, covering every pair with cgo off except the five below and every cgo-capable pair with cgo on, and all 100 runs with the `updater_live`, `release,library`, `appengine`, `os400` and `appengine,os400` tag sets. The other 45 exited 1. With cgo off, android 386, amd64 and arm and ios arm64 reported that the pair "requires external (cgo) linking, but cgo is not enabled" and ios amd64 reported "default PIE binary requires external (cgo) linking, but cgo is not enabled"; a `go list -e` rerun of each listed only the main package, carrying that error. The 40 runs with a tag set containing `generate` reported `found packages uniseg (doc.go) and main (gen_breaktest.go)` in the `github.com/rivo/uniseg` v0.4.7 module; their `go list -e` reruns listed neither pprof package but marked `github.com/rivo/uniseg` with that load error, so its imports may be incomplete. In the same session, a search of the main module's non-test Go files found no `"net/http/pprof"` or `"runtime/pprof"` import, and a `go list` query over the standard library named only `net/http/pprof` and `testing/internal/testdeps` as packages depending on either. Listing the dependency modules to search first failed with `go: module lookup disabled by GOPROXY=off`; a rerun the same day with the default `GOPROXY`, after `go mod download all` (whose added `go.sum` lines were then reverted), listed 108 dependency modules besides the main module, each with a directory, and every one was searched for those import paths in non-test Go files and for the text `/debug/pprof`. That search ignores build constraints, so it over-approximates. It found `"net/http/pprof"` or `"runtime/pprof"` only in `package main` commands (seven in `github.com/dgryski/trifles`, plus `github.com/klauspost/compress/s2/cmd/s2c`, `golang.org/x/text/collate/tools/colcmp` and `golang.org/x/tools/cmd/deadcode`, `goimports` and `ssadump`), in the `golang.org/x/tools` internal packages `go/analysis/internal/checker` and `internal/tool`, and as string data in `golang.org/x/tools/internal/stdlib`; it found `/debug/pprof` only in the `package main` command `github.com/dgryski/trifles/fastpprof`. None of those package paths, and no `github.com/dgryski/trifles` or `golang.org/x/tools` package, appears in the output of any of the 227 runs or the 45 `go list -e` reruns. This guide's inference, not run, is that these matches add no `net/http/pprof` or `runtime/pprof` import to the graphs of those runs. It judges reachability only against those runs' graphs, and the same searches, run over the main module the same day, ignore build constraints and found neither import nor `/debug/pprof` text there.

A source reading for this guide on 26 October 2026, with no Go code built or run, followed those import paths through the extracted sources of the 93 dependency modules whose zips v0.34.2's [`go.sum`](https://github.com/ollama/ollama/blob/v0.34.2/go.sum) lists, from the module cache of the 22 October 2026 sweep; each of those zips has a `.ziphash` and an `h1:` hash recomputed from its contents that match `go.sum`. The other 15 modules in that cache, including `golang.org/x/tools` v0.38.0, have no `go.sum` hash for their module zip (nine have only a `/go.mod` line), so the reading excluded them and did not read them. Reading the package clause and imports of every non-test Go file in those 93 modules and in the main module, ignoring build constraints, found `net/http/pprof` or `runtime/pprof` imported only by the `package main` files of ten commands. Those ten commands are [`cstbucket`](https://github.com/dgryski/trifles/blob/dd97f9abfb48/cstbucket/main.go#L1-L17), [`fastpprof`](https://github.com/dgryski/trifles/blob/dd97f9abfb48/fastpprof/main.go#L1-L13), [`jumpreplica`](https://github.com/dgryski/trifles/blob/dd97f9abfb48/jumpreplica/main.go#L1-L18), [`lz`](https://github.com/dgryski/trifles/blob/dd97f9abfb48/lz/lz.go#L1-L11), [`matcher`](https://github.com/dgryski/trifles/blob/dd97f9abfb48/matcher/main.go#L1-L13), [`quantiles`](https://github.com/dgryski/trifles/blob/dd97f9abfb48/quantiles/main.go#L1-L22) and [`udprelay`](https://github.com/dgryski/trifles/blob/dd97f9abfb48/udprelay/main.go#L1-L26) in `github.com/dgryski/trifles` v0.0.0-20200323201526-dd97f9abfb48, [`s2/cmd/s2c`](https://github.com/klauspost/compress/blob/v1.18.3/s2/cmd/s2c/main.go#L1-L27) in `github.com/klauspost/compress` v1.18.3 and [`collate/tools/colcmp`](https://github.com/golang/text/blob/v0.30.0/collate/tools/colcmp/colcmp.go#L5-L22) in `golang.org/x/text` v0.30.0. The text `/debug/pprof` appears in those modules only in [the `package main` command `github.com/dgryski/trifles/fastpprof`](https://github.com/dgryski/trifles/blob/dd97f9abfb48/fastpprof/main.go#L16-L42) and in a `github.com/pelletier/go-toml/v2` v2.2.2 test file, at [line 1571](https://github.com/pelletier/go-toml/blob/v2.2.2/marshaler_test.go#L1571) and [line 1649](https://github.com/pelletier/go-toml/blob/v2.2.2/marshaler_test.go#L1649). Following imports from every main-module package through the non-test files of packages other than `package main`, with standard-library packages taken as leaves, reached no file importing either pprof package and no import path outside those 93 modules and the standard library. The `golang.org/x/text` and `golang.org/x/exp` packages that import `golang.org/x/tools` packages are imported in those modules only by `package main` and test files, and the main module imports none of them. This guide's inference, not run, is that none of those 93 dependency modules adds `net/http/pprof` or `runtime/pprof` to a build of v0.34.2's main package at these module versions, for any GOOS/GOARCH pair, cgo setting or tag set, because a `package main` command is not imported by other packages. The reading does not cover the standard library, whose importers of either package come only from the linux/amd64 query above, other Go versions, or what the failed runs or a shipped binary would contain.

In Go 1.26.5, `net/http/pprof`'s [`init` function](https://github.com/golang/go/blob/go1.26.5/src/net/http/pprof/pprof.go#L96-L106) registers `/debug/pprof/` and its `cmdline`, `profile`, `symbol` and `trace` paths, each prefixed with the method `GET` unless the `httpmuxgo121` GODEBUG setting is `1`, through [`http.HandleFunc`, which registers on `DefaultServeMux`](https://github.com/golang/go/blob/go1.26.5/src/net/http/server.go#L2870-L2878); a server's [`Handler` is `http.DefaultServeMux` if nil](https://github.com/golang/go/blob/go1.26.5/src/net/http/server.go#L2971), as [its request dispatch applies](https://github.com/golang/go/blob/go1.26.5/src/net/http/server.go#L3302-L3306). A `go list` of the `server` package's Go files on linux amd64 in the same session includes `routes.go`. This guide's inference, not run, is that a build whose import graph includes `net/http/pprof` would serve those paths on the Ollama listener through `Serve`'s nil `Handler`, and that the builds above whose graphs exclude it get no handler from that package. It assumes that a package outside the graph is not linked, so its `init` never runs, and that no other linked code registers a `/debug/pprof/` handler, which this guide checked in first-party code and, by a search for the text `/debug/pprof`, in the 93 dependency modules whose zips `go.sum` hashes.

v0.34.2's [`go.mod` declares `go 1.26.0`](https://github.com/ollama/ollama/blob/v0.34.2/go.mod#L3) with no `toolchain` line, a requirement that the Go 1.26.5 used for these runs satisfies. This guide's reading of the release configuration, which shows the builds intended and not what a published artifact contains, is that the [Dockerfile's Go build stage](https://github.com/ollama/ollama/blob/v0.34.2/Dockerfile#L249-L263) downloads the Go release named by that `go` line and builds the main package with `CGO_ENABLED=1`, `-trimpath -buildmode=pie` and no `-tags`. By the same reading, the [macOS build script](https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_darwin.sh#L88-L89) sets `GOOS=darwin GOARCH=$ARCH CGO_ENABLED=1` for a CMake build whose [Go step](https://github.com/ollama/ollama/blob/v0.34.2/cmake/local.cmake#L656-L703) runs `go build -trimpath` on the main package with `CGO_ENABLED=1` and no `-tags`. By the same reading, the [Windows build script](https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L864-L919) builds the CLI with no `-tags`, and its [`checkEnv` function sets `CGO_ENABLED=1` unconditionally](https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L296) and [runs before the build steps](https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L1299), so its [default CLI build, whose `go build` sets no `GOARCH`](https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L895-L907), uses `CGO_ENABLED=1`, as does its arm64 build, whose wrapper sets `GOOS=windows`, `GOARCH=arm64` and `CGO_ENABLED=1` explicitly. By the same reading, for the default build, the architecture `checkEnv` [selects](https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L210-L230) is [copied to `TARGET_ARCH`](https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L231), which reaches that build only as [its output directory](https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L295). By the same reading, the release workflow's [macOS](https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L71-L82) and [Windows](https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L355-L379) jobs set up Go with `go-version-file: go.mod` before running those scripts. By the same reading, the workflow's [`GOFLAGS` value](https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L13-L25) carries one `-ldflags` flag (`-w -s` and two `-X` settings) and no `-tags`, and the [macOS job's](https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L34) and [Windows job's](https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L340) environments apply it, so those environments add no `-tags` to the scripts' builds. By the same reading, the workflow's [`linux-depends` job](https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L479-L556) passes that value as a Docker build argument only to dependency targets, none of which is or copies from the [Dockerfile's](https://github.com/ollama/ollama/blob/v0.34.2/Dockerfile) Go build stage. By the same reading, the [`docker-build-push` job](https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L561-L661), whose builds do reach that stage, names `GOFLAGS` without a value among its build arguments and sets the workflow value in its environment; whether the build receives that value depends on Docker build tooling not traced here, and [the stage's own `GOFLAGS` default](https://github.com/ollama/ollama/blob/v0.34.2/Dockerfile#L249-L263) carries no `-tags` either. The sweep's matching default-tag runs (linux, darwin and windows amd64 and arm64, cgo on and off) list neither pprof package, but with Go 1.26.5, which need not be the Go release those builds use.

A source reading for this guide on 26 October 2026, with no Go code built or run, compared the standard library of every other stable Go 1.26.x release, Go 1.26.0 to 1.26.4 and 1.26.6 to 1.26.10, with that of Go 1.26.5, the release the `go list` runs above used. Each release's source tarball was fetched from go.dev on 26 October 2026, and the fetch record shows its SHA-256 matching the value go.dev publishes; Sources cites each release's `goversion` line, `go/build` release-tag lines and `runtime/pprof` imports at its `go1.26.N` tag. In each of those releases, as in Go 1.26.5, `internal/goversion` sets `Version = 26`, from which `go/build` derives the release tags `go1.1` to `go1.26` (`go/build/build.go` lines 354 and 355). Reading the import declarations of the non-test Go files outside the `cmd` and `testdata` directories, ignoring build constraints, found `runtime/pprof` imported in each release only by `net/http/pprof`, by `testing/internal/testdeps` and by the `package main` command `simd/archsimd/_gen/simdgen`, at the same lines as in Go 1.26.5. The same reading found no file importing `net/http/pprof` or `testing/internal/testdeps`, and found the text `/debug/pprof` only in `net/http/pprof` and in doc comments of `runtime/pprof` and `runtime/trace`. A file-by-file comparison of each release's import lists with Go 1.26.5's, whose listed additions were each found in that release's source, found across the ten releases one added file, which has no imports, and added imports of 14 packages. Those packages are `bytes`, `crypto/internal/entropy/v1.0.0`, `crypto/internal/fips140/sha256`, `crypto/internal/sysrand`, `crypto/sha256`, `encoding/hex`, `internal/runtime/atomic`, `internal/stringslite`, `internal/syscall/unix`, `math`, `runtime`, `slices`, `sync` and `sync/atomic`; none is a pprof package or one of the importers above, and removed imports and files cannot add one. This guide's inference, not run, is that none of those releases adds `net/http/pprof` or `runtime/pprof` to a v0.34.2 build graph that the Go 1.26.5 runs above recorded without them, because in each release no standard-library package other than those importers imports either one. The reading compares source and checked no `go list` graph, so which files the build constraints and cgo select, and whether the builds that failed with Go 1.26.5 load, are recorded for Go 1.26.5 only. This guide uses the Go 1.26.5 tree here only as the comparison's base; the Go 1.26.5 standard-library question for the failed runs, other pairs and other tag sets stays as stated below.

These `go list` results resolve imports without building a binary and did not inspect the shipped release binary. Builds with Go releases outside the 1.26.x patch line, `go list` graphs for the other 1.26.x releases (including the Go 1.26.0 that `go.mod`'s `go` line names), the five cgo-off android and ios runs and the 40 `generate` runs that failed, the swept tag sets on GOOS/GOARCH pairs other than the ten they were run on, and other tag sets and combinations remain unestablished. For the Go 1.26.5 builds among those that load, the source readings above leave only standard-library imports open. Beyond this guide's inferences above, whether these or such builds give the served mux pprof handlers also remains unestablished. Shipped-binary pprof availability remains unestablished, and the comment alone does not establish it. This guide's advice: include `/debug/pprof/` in live inventory and public-denial checks. Do not claim either default availability or that `OLLAMA_DEBUG=0` disables profiling.

The desktop app main package [`./app/cmd/app`, whose files build only on windows or darwin and whose import block names no pprof package](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app.go#L1-L33), which the release scripts also build, was resolved by ten further `go list -e -deps ./app/cmd/app` runs made for this guide on 23 October 2026. They ran in the same tree and environment as the sweep above, on darwin and windows amd64 and arm64 and linux amd64, cgo off and on. No run listed `net/http/pprof` or `runtime/pprof`, and the only path containing `pprof` in any of their lists is `internal/runtime/pprof/label`. Every run carries a load error, and a package carrying one may list incomplete imports. Both linux amd64 runs fail on that constraint (`build constraints exclude all Go files`) and list only the main package, marked with that error, establishing only that the package has no linux files at this pin. All eight darwin and windows runs mark `app/ui` with `pattern app/dist: no matching files found`, because [its `//go:embed app/dist` directive](https://github.com/ollama/ollama/blob/v0.34.2/app/ui/app.go#L15-L16) names web assets that are not in the tree at this pin ([the macOS build script builds them with npm before its Go builds](https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_darwin.sh#L200-L216)). The four cgo-off darwin and windows runs cannot load [`app/webview`, which is cgo-only through its `import "C"`](https://github.com/ollama/ollama/blob/v0.34.2/app/webview/webview.go#L51) and also omit the main package's own cgo files ([`app_darwin.go`](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L10) and [`webview.go`](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/webview.go#L6)) with no error, while the cgo-on runs, the setting the release scripts use, load them. By source reading, not run, the import blocks of [`app/ui/app.go`](https://github.com/ollama/ollama/blob/v0.34.2/app/ui/app.go#L5-L13), [`app/ui/ui.go`](https://github.com/ollama/ollama/blob/v0.34.2/app/ui/ui.go#L6-L39) and [`app/ui/extract.go`](https://github.com/ollama/ollama/blob/v0.34.2/app/ui/extract.go#L5-L14), the three non-test Go files in `app/ui` at this pin, of [`app/webview/webview.go`](https://github.com/ollama/ollama/blob/v0.34.2/app/webview/webview.go#L53-L60), the only Go file in `app/webview`, and of the main package's [`app_darwin.go`](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L12-L44), [`webview.go`](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/webview.go#L8-L26) and [`codex_app_darwin.go`](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/codex_app_darwin.go#L5-L25) name neither `net/http/pprof` nor `runtime/pprof`. Not read here are the main package's other files, the imports of the packages those blocks name, and how `go list` records a package's imports despite these load errors, so whether the errors hide imports remains open. In the app's own non-test code read here, two listeners appear, both loopback. Neither v0.34.2 Codex Desktop integration file read here opens one: [`internal/proxy/codex_desktop.go`](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go) and [`app/cmd/app/codex_app_darwin.go`](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/codex_app_darwin.go), read whole, contain no `net.Listen` or `http.Server`, and the first [describes its handler as routing requests "using the existing Ollama listener"](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L59-L61) under [`/api/codex`, which it calls the "loopback-only Ollama server route"](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L26-L29). Where the Ollama server registers that handler is not in the pack this guide read, whether it is the desktop proxy route section 3 names was not checked, and [the `cmd/launch` `CodexApp` controller that the second file drives](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/codex_app_darwin.go#L35-L48) was not read. [Its `ServeHTTP`](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L156-L176) answers `403` unless [the request's remote address is `localhost` or a loopback IP](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L643-L653), answers `NotFound` outside that prefix, and serves `/_health` and [a `/_status` route reporting request counters and the last model, route and upstream status](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L517-L533) with no further check. [Other requests](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L192-L263) go to Ollama when the body's model is in the routing catalog file, [with only the `Accept`, `Content-Type`, `OpenAI-Beta` and `User-Agent` headers](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L358-L375) [copied](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L678-L684), and otherwise to the OpenAI API or the ChatGPT upstream, except that a request carrying the managed sentinel key and not routed to Ollama is answered `401`. This guide's inference, not observed: the loopback check reads the TCP peer address, so if the Ollama server serves this handler on its own listener, a request relayed by a proxy on the same host would pass it only when that proxy connects to Ollama over loopback, and then the policy proxy's default denial of unlisted paths, not this check, is what refuses `/api/codex` to remote callers. The UI listener is [`net.Listen("tcp", "127.0.0.1:0")`, or `127.0.0.1:3001` in dev mode](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app.go#L186-L196), and [`srv := &http.Server{Handler: uiServer.Handler()}` serves it with a non-nil `Handler`](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app.go#L279-L292), so, as this guide's inference from the Go sources cited above, a build that linked `net/http/pprof` would still not serve `DefaultServeMux`'s handlers on this listener. [The UI mux](https://github.com/ollama/ollama/blob/v0.34.2/app/ui/ui.go#L277-L320) registers `/api/v1/` routes behind [a token-cookie check that development mode skips](https://github.com/ollama/ollama/blob/v0.34.2/app/ui/ui.go#L193-L224), reverse-proxy routes for seven Ollama API paths (eight method patterns) and catch-all app routes, both wired without that check, and no `/debug/pprof` pattern. The second listener traced here is the macOS Claude Desktop gateway: [`app_darwin.go` is cgo-only through its `import "C"`](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L10), so the darwin cgo builds, the release setting, compile it, and [at startup the app reconciles that gateway](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L535), [starting it only when Claude Desktop is installed and configured to use it](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L546-L561). The app's Claude Desktop connect and model-mapping actions also start it without an already configured Claude Desktop, through [`setClaudeGatewayInstalled`](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L1202-L1229), [`prepareClaudeDesktopConnection`, which starts it before configuring Claude Desktop and stops it only when Claude Desktop does not end up using the gateway](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L1472-L1487), and [the model-mapping path](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L1639-L1661). However, [the start itself skips when Claude Desktop is not installed](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L592-L598). `setClaudeGatewayInstalled` also starts it before configuring Claude Desktop and stops it when Claude Desktop does not end up using the gateway, unless `effectiveClaudeDesktopAutoMode` has already returned an error. The model-mapping path, [when it finds no existing gateway](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L1568-L1573), stops it when its profile change returns an error other than `ErrClaudeDesktopRestartConfirmationRequired`, while [with an existing gateway it returns such an error joined with `restoreState()`'s result, without stopping it](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L1694-L1698). The start [constructs the gateway](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L614-L631) with [a listen address set to `proxy.DefaultClaudeDesktopListenAddr` beside a 750 ms start retry window](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L95-L96), [`127.0.0.1:11435`](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L23-L26) [copied to the gateway's own listen address at construction](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L131-L132), and [calls its `Start`, retrying briefly while the address is in use](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L944-L951). [`Start` listens there and serves an `http.Server` whose `Handler` is the gateway itself, non-nil](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L198-L221), and [its `ServeHTTP` serves only `/_ollama/health`, `/v1/models`, `/v1/messages/count_tokens` and `/v1/messages`, rejects a request whose first `Origin` header value is non-empty and answers other paths with `NotFound`](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L300-L361), with no `/debug/pprof` route. [Go 1.26.5's `Header.Get` returns a header's first value](https://github.com/golang/go/blob/go1.26.5/src/net/http/header.go#L43-L51); this guide's inference, not observed, is that a non-empty `Origin` value after an empty first one does not trigger that rejection. [Before that `Origin` check, `ServeHTTP` answers `403`](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L300-L361) to any request whose `Host` header [is not `localhost`, in any letter case, or a loopback IP literal, followed by the port the gateway is listening on](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L419-L435), so a `Host` with no port is refused too. Only `POST /v1/messages` passes to the gateway's reverse proxy, since the other routes return first: the gateway [removes `Authorization`, `Cookie` and `Proxy-Authorization`, sets `X-Api-Key: ollama` and the upstream `Host`, waits for the upstream, and forwards the request](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L363-L380) through a reverse proxy [whose transport's `Proxy` is nil](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L126-L130). [That wait](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L442-L511) dials the upstream over TCP until a connection succeeds or 10 seconds pass, and a success is reused for 5 seconds: [the constants `upstreamReadyTimeout` and `upstreamReadyTTL`](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L27-L31) hold those values, and [construction sets the wait from the first](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L143). [The start takes the upstream from `envconfig.ConnectableHost()` and refuses an `OLLAMA_HOST` whose port is the gateway's](https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L599-L609), then passes it as the gateway's Ollama URL: [`Host`](https://github.com/ollama/ollama/blob/v0.34.2/envconfig/config.go#L20-L60) reads `OLLAMA_HOST` [from the app process's environment](https://github.com/ollama/ollama/blob/v0.34.2/envconfig/config.go#L378-L380), defaulting to `http://127.0.0.1:11434`, and [`ConnectableHost`](https://github.com/ollama/ollama/blob/v0.34.2/envconfig/config.go#L62-L83) replaces an unspecified address with loopback. This guide's inference, not observed: if the app's own environment sets `OLLAMA_HOST` to another address, the gateway forwards Claude Desktop's messages there without the caller's `Authorization`, `Cookie` or `Proxy-Authorization` headers, so an authenticating proxy at that address that expects them would refuse those requests. [Model routing](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L594-L634) reads the body's `model` and admits it only when it [equals a listed model's gateway ID or Ollama model name](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L741-L748), [otherwise answering `400`](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L300-L361); it answers [`401`, `403`, `404` or `503`](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L807-L818) when that model's access check fails, and otherwise rewrites `model` to the listed Ollama model name. [A `400` from Ollama to a replayable `POST /v1/messages` is retried once](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L636-L724), with each image replaced by a text notice, under three further conditions. The error body, at most [64 KiB](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L27-L31), must decode as an `anthropic.ErrorResponse` whose `Type` is `error` and whose `Error.Type` is `invalid_request_error`, with a message that, ignoring letter case, contains `image` or `vision` and `not support` or `unsupported`. The JSON request body, at most 64 MiB, must name a string `model` that is not a listed model supporting vision, and at least one image must be replaced. By source reading, not run, the gateway keeps at most five models, each holding one of [five fixed Claude route IDs](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop_models.go#L16-L35) (`claude-fable-5`, `claude-opus-5`, `claude-sonnet-5`, `claude-haiku-4-5-20251001` and `claude-sonnet-4-6`), which [it assigns in that order unless the models already hold distinct ones](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop_models.go#L308-L353), and [with no configured models it uses](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L146-L148) [five built-in cloud models](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop_models.go#L183-L200). Of the models these files construct, only models named `kimi-k3:cloud`, such as the built-in one, [are marked as supporting vision](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop_models.go#L433-L467). [`/v1/models` lists only the models whose access check returns available](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L519-L555). [That check](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop_access.go#L55-L124) admits a local model only when the local inventory is known and lists it, and a cloud model only when Cloud is on, the account is signed in, the model's entitlement is known and the plan meets its requirement: an empty or `free` requirement admits any plan, and any other needs a plan that is neither empty nor `free`. Otherwise it reports `cloud_off`, `sign_in_required`, `upgrade_required` or `model_not_installed`, which the message and token-count routes [answer](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L807-L818) with `403`, `401`, `403` and `404`, or unknown availability with `verification_unavailable`, answered with `503`, when the inventory, Cloud status or account state is undetermined or a cloud model's entitlement is unknown. With no access resolver, [the gateway assumes Cloud on, a signed-in account and plan `pro`, and with no local-model lister it treats every local model as installed](https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L750-L799); the app callbacks that supply these and refresh the list are not traced here. This guide's inference, not observed: on a Mac running the desktop app with that gateway on, the gateway and the Option B policy proxy recipe's `listen 127.0.0.1:11435;` would both try to bind that address and port. The app does not serve the Ollama API listener itself: it runs [the separate `ollama` binary resolved at construction](https://github.com/ollama/ollama/blob/v0.34.2/app/server/server.go#L49-L51) [with `serve`, copying the app's own environment and, when the app's Expose setting is on, setting `OLLAMA_HOST=0.0.0.0`](https://github.com/ollama/ollama/blob/v0.34.2/app/server/server.go#L241-L252), the server the rest of this guide covers, and [restarts it in a supervision loop when it exits](https://github.com/ollama/ollama/blob/v0.34.2/app/server/server.go#L190-L225). So a desktop deployment can be exposed by that app setting, as well as by an `OLLAMA_HOST` in the app's own environment. By this guide's reading of the intended builds, not artifacts, the macOS script linked above builds this package with `GOARCH=amd64` and `arm64`, `CGO_ENABLED=1`, `GOOS=darwin` and no `-tags`. By the same reading, [`build_windows.ps1`'s `buildApp` runs `go build` with no `-tags`](https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L980-L1004), once as the default app build, which sets no `GOARCH` and uses the architecture `checkEnv` selects in its output file name only, under its unconditional `CGO_ENABLED=1`. By the same reading, [only when the cross-compile tools are present](https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L994-L997), `buildApp` runs that `go build` once more, for arm64, inside `withWindowsArm64GoEnv`, which sets `GOOS=windows`, `GOARCH=arm64` and `CGO_ENABLED=1`. These runs resolve imports without compiling and no shipped app binary was inspected; other Go versions, other GOOS/GOARCH pairs and tag sets, the imports the load errors above may hide, the gateway behaviour not traced above and every runtime response of these listeners remain unestablished.

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

REASONED: service-comparison scope from the cited v0.34.2 sources; no authorized live deployment or external observer. No service was started or contacted for these checks. All service-behavior checks below are **REASONED, not demonstrated**. The authoring environment has no Ollama, Docker, Podman, nginx, or Caddy executable in `PATH`, no Ollama runtime or GPU, and no supplied authorized deployment, external observer, credentials, or model fixtures. Filesystem and network restrictions prevent provisioning a live comparison here. **Lack of a GPU alone would not prevent listener, API, CORS, or management testing.**

REASONED: mixed local-validation evidence and unobserved service comparisons from the cited v0.34.2 sources; a fresh local run with Bash 5.3.9 bash -n and ShellCheck 0.11.0 run with -s bash accepted all four Verify shell fences with exit 0 and no output, establishing only syntax and lint results; native proxy parsing and live comparisons remain unobserved without the binaries and an authorized deployment; the following validation account is historical, including its 74-case count, guard-scanner result and drop-in gate statement, and that count was not re-established here. Local validation covered the four Bash fragments with `bash -n`, ShellCheck 0.11.0, and the repository's strict guard-convention scanner. Guard-only tests rejected 74 invalid or incomplete positional-input cases under `bash -u`; four substituted controls reached local markers in place of the operational branch. These observations establish shell and outer-guard behavior only. Native proxy parsing remains unconfirmed; every service comparison is REASONED from the cited v0.34.2 sources and vendor documentation. The whole-corpus gate suite was not run against this drop-in.

REASONED: shell preparation and limitations from the printed guards and curl reference. Local Bash 5.3.9 ran bash -n on all four Verify shell fences with exit 0 and no output. For each complete subshell, operational commands were replaced with local printf markers; valid controls were ollama.service/NONE, 192.168.50.7, and https://fixture.internal/api/chat with readable disposable JSON and empty mode-0600 client configuration files, POST and application/json where applicable. Replacing the first value after the marker with an empty string or bad value, keeping the original placeholders, or using set -- without arguments produced no operational marker and exit 1. The valid controls reached their markers; V6 wrote eight LOCAL_CURL status files in a mode-0700 directory. This tests only those shell cases, not address syntax, client configuration acceptance, inference, or deployment isolation. Paste complete blocks, including the parentheses, marker, and count checks. Substitute inside the single quotes on each `set --` line; a literal apostrophe requires shell escaping. The guards assume normal shell builtins and cannot protect a fragment pasted from below them. Use curl 7.75.0 or later for the displayed `exitcode` and `errormsg` variables.

REASONED: comparison procedure from the cited service and proxy sources; isolated exposed/fixed deployments, identities and observers are unavailable. Use isolated exposed and fixed deployments with disposable fixtures. Do not make production public to obtain a baseline. Record binary/image identity, effective configuration, observer location, HTTP results, completed response bodies, upstream observations, state changes, and cleanup without secrets.

### V1. Inspect the listener, identity, and store (REASONED: listener, systemd/container identity, publication, ownership, ACL and writable-store comparisons, with administrative and inference positive controls, follow C1 and C5; no deployed store, service identity or external observer. Local command-marker tests above do not inspect a deployment)

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

### V2. Probe direct-backend bypass from another machine (REASONED: direct-origin reachability and approved-proxy inference comparison follow C1 binding documentation; no live target or external observer. The local address-guard cases above establish no network outcome)

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

### V3. Verify authentication and TLS with a real inference request (REASONED: cited Ollama, proxy and curl behavior; no live proxy, certificates, credentials or model)

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

The following reusable probe reads the client configuration on stdin, keeping credentials off curl's argv. No credential is typed into the command, and the block's `set +x` turns tracing off before it reads the file, so neither shell history nor `set -x` tracing records the credentials; write the file with an editor, not a shell command, so preparing it does not put them in history either. Stdin closes the argv channel only: the account owner and root can still read the file and the memory of the block's subshell, whose placeholder check reads the file, and of curl. It supports the concrete operations in V3 through V8. Use `/dev/null` as the body for GET, HEAD, and OPTIONS. Use `application/octet-stream` for blob bytes and `application/json` for JSON fixtures.

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

### V4. Exercise management authorization and blob writes (REASONED: management, account, experimental and blob operations, public denial and private administrative success, cleanup and public-chat controls follow C3 API methods and route registration; no isolated model store, registry, identities or proxy. Python 3.14.4 json.loads accepted the four literal JSON bodies in this table; that is syntax only. sha256sum on a disposable file containing OLLAMA_VERIFY_FIXTURE followed by LF returned 9b18adfd436acae378346d9452646db562690662d43ded1df7adceea38540c95; no blob upload or existence check ran)

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

### V5. Compare browser origins and preflights (REASONED: required/unrelated/built-in/missing Origin, preflight, actual browser calls and authenticated/anonymous POST comparisons follow C4 AllowedOrigins and C2 proxy policies; no live backend, proxy or browser fixture. The header text was not exercised by a browser)

**REASONED:** no live backend or authorized browser frontend is available. Use V3 with OPTIONS, `/dev/null`, and a client configuration containing these non-secret test headers:

```text
header = "Origin: https://REPLACE_WITH_BROWSER_ORIGIN"
header = "Access-Control-Request-Method: POST"
header = "Access-Control-Request-Headers: content-type"
```

Run against the private test backend to isolate Ollama's CORS behavior, then against the actual frontend boundary. Repeat with the required origin, an unrelated controlled origin, representative built-in origins, and no Origin header.

Exposed: with wildcard additional origins, the unrelated browser origin is permitted. Fixed: unnecessary additional origins are refused; required origins still work. Inspect access-control response headers and perform an actual browser request, because curl itself does not enforce CORS.

For the C2 POST-only proxy, an OPTIONS request is not forwarded; the exact status depends on the variant: the nginx Basic-auth example returns 405, the nginx bearer variant returns 401 for a missing or wrong credential and 405 once a valid one passes, and the Caddy example falls through to 404. Each denies forwarding, so any of these is the expected non-browser policy, not a successful cross-origin frontend deployment. If a cross-origin browser frontend is required, demonstrate its separately designed preflight/authentication flow, including any authorization header it needs.

Repeat the actual POST with and without Origin. Removing Origin must not bypass proxy authentication; a non-browser caller with valid credentials is not constrained by CORS. The built-in origins remain as described by C4's [AllowedOrigins implementation](https://github.com/ollama/ollama/blob/v0.34.2/envconfig/config.go).

### V6. Exercise finite admission and resource budgets (REASONED: admission, body size, model loading, expiry, parameter overrides, queue capacity and recovery comparisons follow C6 scheduler/types and nginx limit references; no inference runtime, loaded model, capacity fixture or GPU. Local V6 marker files above demonstrate child completion only, not either limiter or successful inference)

**REASONED:** no inference runtime, loaded models, capacity fixture, or GPU is available. The following probe launches exactly eight requests, each bounded to 120 seconds, waits for every child, and retains separate results. Like V3's reusable probe, it reads the client configuration on each curl's stdin, keeping credentials off curl's argv. No credential is typed into the command, and the block's `set +x` turns tracing off before it reads the file, so neither shell history nor `set -x` tracing records the credentials; write the file with an editor, not a shell command, so preparing it does not put them in history either. Stdin closes the argv channel only: the account owner and root can still read the file and the memory of the block's subshell, whose placeholder check reads the file, and of each curl. Use only an isolated capacity test with the same small, valid chat fixture as V3:

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

### V7. Check provenance, cloud disablement, and administrative egress (REASONED: digest approval, private inventory, public mutation denial, allowed/disallowed registry transfers, cloud-enabled/disabled inference and local-model controls follow C7 and C8; no approved artifacts, controlled registries, cloud identity or live server)

**REASONED:** no approved artifact inventory, controlled registry, cloud credentials, or live server is available.

Use V3 for private `GET /api/tags`. Compare each deployed model digest with the independently approved inventory. For a GGUF import, compare `sha256sum /srv/ollama-import/app.gguf` with the approved artifact checksum before import. The raw GGUF SHA-256 and a model manifest digest are different identifiers; record each for its purpose.

Exposed: callers can install or export arbitrary chosen material through public management. Fixed: V4's public mutations are denied, administrative provisioning yields the approved model digest, and ordinary inference succeeds. Where registry exclusivity is required, compare an approved transfer with a small transfer to a separately controlled disallowed registry. The egress boundary must deny the latter without blocking the former.

For C8, use V3's POST `/api/chat` with a currently authorized cloud-model fixture and a non-sensitive prompt. In the isolated cloud-enabled state, establish a completed response. After setting `OLLAMA_NO_CLOUD=1` and restarting, require a cloud-disabled refusal, then repeat the local-model positive control. An invalid model or missing upstream credential is not proof of cloud disablement.

Sources: C7's [model inventory](https://docs.ollama.com/api/tags) and [transfer implementation](https://github.com/ollama/ollama/blob/v0.34.2/server/images.go), and C8's [cloud-disable documentation](https://github.com/ollama/ollama/blob/v0.34.2/docs/faq.mdx).

### V8. Inspect diagnostics, profiling, and prompt captures (REASONED: public/private diagnostics, actual profiling availability, public-chat controls and debug-enabled/disabled capture inspection follow C9 router/logger; no running binary, service temporary namespace or diagnostic fixtures. Python 3.14.4 json.loads accepted the literal show-request body; it establishes syntax only. Default-tag go list runs for linux, darwin and windows amd64, twelve further platform, cgo and tag variants, and the 182 of 227 runs in a 22 October 2026 Go 1.26.5 platform, cgo and tag-set sweep that exited 0 listed no net/http/pprof or runtime/pprof dependency; the sweep's other 45 runs failed, and none establishes a runtime response)

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

For `/debug/pprof/`, first observe the actual private binary; this guide's source trace does not establish its response. This guide's source assessment is that first-party v0.34.2 registers no pprof handler, and the `go list` runs for the platform, cgo and tag combinations listed in C9 found no `net/http/pprof` or `runtime/pprof` dependency in any run that loaded. Builds with Go releases outside the 1.26.x patch line, `go list` graphs for the other 1.26.x releases (C9 gives only an inference from source), the C9 runs that failed, the tagged sets on platforms not run, other tag sets, exposure through the served mux in such builds (C9 gives only this guide's inference for the builds that loaded) and shipped-binary pprof availability remain unestablished. If no handler exists, record that absence; do not call it proof that debug settings disabled profiling. If it exists, retain the observed response and demonstrate public denial.

For logging, use an isolated service and a unique non-sensitive prompt. With request debugging deliberately enabled only for the comparison, send one completed V3 request and inspect the service's actual temporary-directory namespace for `ollama-request-logs-*`, request bodies, and replay scripts. Then apply C9, restart, send another completed request, and verify that no new request capture is created. Account for a service-specific `TMPDIR` or private temporary namespace. Retain timestamps and file evidence without sharing captured prompts or credentials, then clean up the test captures.

Expected behavior follows C9's [router](https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go) and [request logger](https://github.com/ollama/ollama/blob/v0.34.2/server/inference_request_log.go).

### Native proxy parsing (REASONED: native acceptance and its limits follow the linked nginx/Caddy command references; neither executable is on PATH and deployment certificate/password files are unavailable. Neither native validation command ran)

Parsing is an offline check, but it was **not demonstrated here** because nginx and Caddy are absent. On the deployment host, run `nginx -t` against the assembled configuration and real referenced certificate/password files before reloading. For the Caddy alternative, run `caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile`.

These commands validate configuration acceptance; they do not prove authentication, management denial, TLS enforcement, or resource behavior. Avoid sharing `nginx -T` output from a bearer configuration because it contains the shared token. See the [nginx command reference](https://nginx.org/en/docs/switches.html) and [Caddy validation reference](https://caddyserver.com/docs/command-line#caddy-validate).

### Verification scope and local work (REASONED: service-comparison and native-parsing prerequisites from V1-V8 and the cited sources; no authorized deployment, external observer, service credentials or native proxy binaries. Historical local observations above are not new deployment evidence)

| Check scope | Status | Procedure and prerequisites |
|---|---|---|
| Service behavior | REASONED from the cited v0.34.2 sources and vendor documentation; not demonstrated | On v0.34.2 or a newly reviewed explicit pin, load the assembled service/proxy configuration and reproduce every applicable exposed/fixed comparison above in isolated states. Record binary/image identity, effective configuration, commands, responses, upstream observations, completed positive controls, state changes, and cleanup without secrets. Include IPv4/IPv6 and Docker bypass paths; absent/wrong/correct authentication; TLS trust and mTLS negatives; all management methods and blob writes; browser preflights and actual calls; finite admission, scheduler observations, parameter overrides, and recovery; effective identity, ACLs, and model digests; controlled registry transfers; cloud disablement; diagnostic denial, prompt-capture behavior, and actual profiling availability. Use CPU fixtures where sufficient and GPU hardware for GPU-specific claims. Configuration inspection or `nginx -t` alone does not demonstrate service behavior. |
| Native proxy parsing | Not demonstrated here because nginx and Caddy are absent; retained local work | Run the offline parsing checks above against the assembled configuration and real referenced certificate/password files. |

## Sources (checked September 2026)

- Ollama v0.34.2 release: https://github.com/ollama/ollama/releases/tag/v0.34.2
- Ollama release commit and redirect hardening: https://github.com/ollama/ollama/commit/dfabde4539e42ba1e1eab50a3a50b88aea7958a0
- Ollama repository at the reviewed tag: https://github.com/ollama/ollama/tree/v0.34.2
- Ollama FAQ: https://docs.ollama.com/faq
- Pinned FAQ, service environment, proxy examples, overrides, and cloud disablement: https://github.com/ollama/ollama/blob/v0.34.2/docs/faq.mdx
- Ollama local API authentication (rolling documentation, checked September 2026): https://docs.ollama.com/api/authentication
- Official Docker image wildcard listener: https://github.com/ollama/ollama/blob/v0.34.2/Dockerfile
- Linux service instructions: https://github.com/ollama/ollama/blob/v0.34.2/docs/linux.mdx
- Linux installer and service account: https://github.com/ollama/ollama/blob/v0.34.2/scripts/install.sh
- Environment configuration and additive origins: https://github.com/ollama/ollama/blob/v0.34.2/envconfig/config.go
- API methods and blob operations: https://github.com/ollama/ollama/blob/v0.34.2/docs/api.md
- HTTP serving, routes, and host middleware: https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go
- Client-side outbound signing: https://github.com/ollama/ollama/blob/v0.34.2/api/client.go
- Server startup and administrative import: https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go
- CLI entry point (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/main.go#L3-L13
- Serve command definition (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go#L2469-L2475
- CLI constructor NewCLI (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go#L2377-L2654
- Serve command registration (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go#L2632-L2654
- Serve command server path (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go#L2093-L2109
- Router attachment (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go#L1987-L1992
- HTTP server handler and pprof comment (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go#L2001-L2011
- HTTP listener serve call (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go#L2052-L2057
- HTTP server import block (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go#L3-L54
- Serve function (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go#L1938-L2060
- cmd package imports, including the server package (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go#L3-L60
- server package clause (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go#L1
- integration test build tag (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/integration/basic_test.go#L1
- fast, release and library test build tags (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/integration/reg_groups_test.go#L1
- generate test build tag (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/integration/generate_jinja_test.go#L1
- updater_live test build tag (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/updater/updater_live_test.go#L1
- readline terminal build constraint and syscall import (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/readline/term.go#L1-L7
- Go module `go` line (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/go.mod#L3
- Go module requirement blocks (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/go.mod#L5-L91
- Go module checksums (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/go.sum
- `github.com/dgryski/trifles` `cstbucket` command package clause and imports at v0.0.0-20200323201526-dd97f9abfb48 (checked October 2026): https://github.com/dgryski/trifles/blob/dd97f9abfb48/cstbucket/main.go#L1-L17
- `github.com/dgryski/trifles` `fastpprof` command package clause and imports at v0.0.0-20200323201526-dd97f9abfb48 (checked October 2026): https://github.com/dgryski/trifles/blob/dd97f9abfb48/fastpprof/main.go#L1-L13
- `github.com/dgryski/trifles` `jumpreplica` command package clause and imports at v0.0.0-20200323201526-dd97f9abfb48 (checked October 2026): https://github.com/dgryski/trifles/blob/dd97f9abfb48/jumpreplica/main.go#L1-L18
- `github.com/dgryski/trifles` `lz` command package clause and imports at v0.0.0-20200323201526-dd97f9abfb48 (checked October 2026): https://github.com/dgryski/trifles/blob/dd97f9abfb48/lz/lz.go#L1-L11
- `github.com/dgryski/trifles` `matcher` command package clause and imports at v0.0.0-20200323201526-dd97f9abfb48 (checked October 2026): https://github.com/dgryski/trifles/blob/dd97f9abfb48/matcher/main.go#L1-L13
- `github.com/dgryski/trifles` `quantiles` command package clause and imports at v0.0.0-20200323201526-dd97f9abfb48 (checked October 2026): https://github.com/dgryski/trifles/blob/dd97f9abfb48/quantiles/main.go#L1-L22
- `github.com/dgryski/trifles` `udprelay` command package clause and imports at v0.0.0-20200323201526-dd97f9abfb48 (checked October 2026): https://github.com/dgryski/trifles/blob/dd97f9abfb48/udprelay/main.go#L1-L26
- `github.com/dgryski/trifles` `fastpprof` command `/debug/pprof` handlers at v0.0.0-20200323201526-dd97f9abfb48 (checked October 2026): https://github.com/dgryski/trifles/blob/dd97f9abfb48/fastpprof/main.go#L16-L42
- `github.com/klauspost/compress` `s2/cmd/s2c` command package clause and imports at v1.18.3 (checked October 2026): https://github.com/klauspost/compress/blob/v1.18.3/s2/cmd/s2c/main.go#L1-L27
- `golang.org/x/text` `collate/tools/colcmp` command package clause and imports at v0.30.0 (checked October 2026): https://github.com/golang/text/blob/v0.30.0/collate/tools/colcmp/colcmp.go#L5-L22
- `github.com/pelletier/go-toml/v2` test file `/debug/pprof` text, first match at v2.2.2 (checked October 2026): https://github.com/pelletier/go-toml/blob/v2.2.2/marshaler_test.go#L1571
- `github.com/pelletier/go-toml/v2` test file `/debug/pprof` text, second match at v2.2.2 (checked October 2026): https://github.com/pelletier/go-toml/blob/v2.2.2/marshaler_test.go#L1649
- Dockerfile Go build stage (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/Dockerfile#L249-L263
- macOS build script Go environment (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_darwin.sh#L88-L89
- CMake Go build step and local payload target (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/cmake/local.cmake#L656-L703
- Windows build script CLI and arm64 builds (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L864-L919
- Windows build script architecture selection, from `ARCH` or host detection (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L210-L230
- Windows build script unconditional `CGO_ENABLED` setting in `checkEnv` (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L296
- Windows build script `checkEnv` call before the build steps (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L1299
- Windows build script default CLI build, its `go build` without `GOARCH` and its output directory argument (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L895-L907
- Windows build script selected architecture copied to `TARGET_ARCH` (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L231
- Windows build script output directory named from `TARGET_ARCH` (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L295
- Release workflow macOS Go setup and build (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L71-L82
- Release workflow Windows Go setup and build (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L355-L379
- Release workflow `GOFLAGS` value (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L13-L25
- Release workflow Windows job `GOFLAGS` environment (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L340
- Release workflow macOS job `GOFLAGS` environment (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L34
- Release workflow `linux-depends` job, its dependency targets and `GOFLAGS` build argument (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L479-L556
- Release workflow `docker-build-push` job, its value-less `GOFLAGS` build argument and environment (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L561-L661
- Desktop app main package constraint and imports (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app.go#L1-L33
- Desktop app loopback listener (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app.go#L186-L196
- Desktop app HTTP server with non-nil handler and serve call (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app.go#L279-L292
- Desktop app UI token-cookie check (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/ui/ui.go#L193-L224
- Desktop app UI mux routes (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/ui/ui.go#L277-L320
- Desktop app managed ollama serve process and Expose setting (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/server/server.go#L241-L252
- Desktop app embedded web assets directive (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/ui/app.go#L15-L16
- Desktop app webview cgo-only import (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/webview/webview.go#L51
- macOS build script desktop app npm and Go builds (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_darwin.sh#L200-L216
- Windows build script desktop app builds (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L980-L1004
- Desktop app `app_darwin.go` cgo-only import (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L10
- Desktop app main package webview cgo-only import (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/webview.go#L6
- Desktop app Claude gateway listen address and start retry window variables (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L95-L96
- Desktop app Claude gateway reconcile call (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L535
- Desktop app Claude gateway reconcile conditions (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L546-L561
- Desktop app Claude gateway start installed check (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L592-L598
- Desktop app Claude gateway `setClaudeGatewayInstalled` start and conditional stop (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L1202-L1229
- Desktop app Claude gateway `prepareClaudeDesktopConnection` start and conditional stop (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L1472-L1487
- Desktop app Claude gateway model-mapping start with no existing gateway, and in that case stop on a failed profile change other than restart confirmation (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L1639-L1661
- Desktop app Claude gateway model-mapping read of any existing gateway (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L1568-L1573
- Desktop app Claude gateway model-mapping failed profile change with an existing gateway, returned without a stop (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L1694-L1698
- Desktop app Claude gateway construction and start call (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L614-L631
- Desktop app Claude gateway start retry loop (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L944-L951
- Claude Desktop gateway default listen address (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L23-L26
- Claude Desktop gateway configured listen address copy (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L131-L132
- Claude Desktop gateway listener and HTTP server (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L198-L221
- Claude Desktop gateway routes (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L300-L361
- Claude Desktop gateway host allowlist (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L419-L435
- Claude Desktop gateway credential-header removal, `X-Api-Key` and `Host` rewrite, upstream wait and forwarding (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L363-L380
- Claude Desktop gateway reverse proxy and its transport with a nil `Proxy` (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L126-L130
- Claude Desktop gateway upstream readiness wait (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L442-L511
- Claude Desktop gateway body size limits and upstream wait and reuse durations (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L27-L31
- Claude Desktop gateway upstream wait set from its timeout at construction (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L143
- Claude Desktop gateway model routing and body rewrite (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L594-L634
- Claude Desktop gateway model ID and Ollama name match (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L741-L748
- Claude Desktop gateway access error statuses (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L807-L818
- Claude Desktop gateway image-rejection retry (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L636-L724
- Claude Desktop gateway model limit and five fixed route IDs (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop_models.go#L16-L35
- Claude Desktop gateway model selection and route assignment (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop_models.go#L308-L353
- Claude Desktop gateway built-in model fallback at construction (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L146-L148
- Claude Desktop gateway built-in cloud models (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop_models.go#L183-L200
- Claude Desktop gateway model construction and vision mark (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop_models.go#L433-L467
- Claude Desktop gateway model list filtered by access (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L519-L555
- Claude Desktop gateway model access rules and plan check (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop_access.go#L55-L124
- Claude Desktop gateway default access state and local-model facts (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L750-L799
- Desktop app Claude gateway upstream from `ConnectableHost` and gateway-port refusal (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L599-L609
- Environment `Host` parsing of `OLLAMA_HOST` and its default (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/envconfig/config.go#L20-L60
- Environment `ConnectableHost` loopback substitution (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/envconfig/config.go#L62-L83
- Environment `Var` read from the process environment (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/envconfig/config.go#L378-L380
- Desktop app UI `app.go` import block (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/ui/app.go#L5-L13
- Desktop app UI `ui.go` import block (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/ui/ui.go#L6-L39
- Desktop app webview package import block (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/webview/webview.go#L53-L60
- Desktop app `app_darwin.go` import block (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L12-L44
- Desktop app main package `webview.go` import block (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/webview.go#L8-L26
- Desktop app UI `extract.go` import block (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/ui/extract.go#L5-L14
- Desktop app `codex_app_darwin.go` import block (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/codex_app_darwin.go#L5-L25
- Desktop app Codex Desktop integration, read whole (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/codex_app_darwin.go
- Desktop app Codex Desktop controller interface and `launch.CodexApp` value (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/codex_app_darwin.go#L35-L48
- Codex Desktop proxy handler, read whole (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go
- Codex Desktop proxy `/api/codex` prefix comment (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L26-L29
- Codex Desktop proxy handler comment on the existing Ollama listener (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L59-L61
- Codex Desktop proxy loopback refusal, prefix, health and status routes (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L156-L176
- Codex Desktop proxy routing to Ollama or the native upstream and managed-key refusal (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L192-L263
- Codex Desktop proxy outbound rewrite and Ollama header reset (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L358-L375
- Codex Desktop proxy status response (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L517-L533
- Codex Desktop proxy loopback remote-address check (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L643-L653
- Codex Desktop proxy headers copied to Ollama (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L678-L684
- Desktop app managed ollama serve restart loop (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/server/server.go#L190-L225
- Desktop app ollama binary resolution (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/app/server/server.go#L49-L51
- Windows build script conditional arm64 app build (checked October 2026): https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L994-L997
- Go go1.26.5 net/http/pprof handler registration (checked October 2026): https://github.com/golang/go/blob/go1.26.5/src/net/http/pprof/pprof.go#L96-L106
- Go go1.26.5 http.HandleFunc on DefaultServeMux (checked October 2026): https://github.com/golang/go/blob/go1.26.5/src/net/http/server.go#L2870-L2878
- Go go1.26.5 Server Handler default (checked October 2026): https://github.com/golang/go/blob/go1.26.5/src/net/http/server.go#L2971
- Go go1.26.5 nil-Handler request dispatch (checked October 2026): https://github.com/golang/go/blob/go1.26.5/src/net/http/server.go#L3302-L3306
- Go go1.26.5 go build test-file exclusion (checked October 2026): https://github.com/golang/go/blob/go1.26.5/src/cmd/go/alldocs.go#L83
- Go go1.26.5 build -tags flag (checked October 2026): https://github.com/golang/go/blob/go1.26.5/src/cmd/go/alldocs.go#L236-L240
- Go go1.26.5 net/http `Header.Get` first value (checked October 2026): https://github.com/golang/go/blob/go1.26.5/src/net/http/header.go#L43-L51
- Go go1.26.5 `internal/goversion` `Version = 26` (checked October 2026): https://github.com/golang/go/blob/go1.26.5/src/internal/goversion/goversion.go#L12
- Go go1.26.5 `go/build` release tags derived from `goversion.Version` (checked October 2026): https://github.com/golang/go/blob/go1.26.5/src/go/build/build.go#L354-L355
- Go go1.26.5 `net/http/pprof` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.5/src/net/http/pprof/pprof.go#L88
- Go go1.26.5 `testing/internal/testdeps` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.5/src/testing/internal/testdeps/deps.go#L23
- Go go1.26.5 `simd/archsimd/_gen/simdgen` command import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.5/src/simd/archsimd/_gen/simdgen/main.go#L91
- Go go1.26.0 `internal/goversion` `Version = 26` (checked October 2026): https://github.com/golang/go/blob/go1.26.0/src/internal/goversion/goversion.go#L12
- Go go1.26.0 `go/build` release tags derived from `goversion.Version` (checked October 2026): https://github.com/golang/go/blob/go1.26.0/src/go/build/build.go#L354-L355
- Go go1.26.0 `net/http/pprof` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.0/src/net/http/pprof/pprof.go#L88
- Go go1.26.0 `testing/internal/testdeps` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.0/src/testing/internal/testdeps/deps.go#L23
- Go go1.26.0 `simd/archsimd/_gen/simdgen` command import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.0/src/simd/archsimd/_gen/simdgen/main.go#L91
- Go go1.26.1 `internal/goversion` `Version = 26` (checked October 2026): https://github.com/golang/go/blob/go1.26.1/src/internal/goversion/goversion.go#L12
- Go go1.26.1 `go/build` release tags derived from `goversion.Version` (checked October 2026): https://github.com/golang/go/blob/go1.26.1/src/go/build/build.go#L354-L355
- Go go1.26.1 `net/http/pprof` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.1/src/net/http/pprof/pprof.go#L88
- Go go1.26.1 `testing/internal/testdeps` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.1/src/testing/internal/testdeps/deps.go#L23
- Go go1.26.1 `simd/archsimd/_gen/simdgen` command import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.1/src/simd/archsimd/_gen/simdgen/main.go#L91
- Go go1.26.2 `internal/goversion` `Version = 26` (checked October 2026): https://github.com/golang/go/blob/go1.26.2/src/internal/goversion/goversion.go#L12
- Go go1.26.2 `go/build` release tags derived from `goversion.Version` (checked October 2026): https://github.com/golang/go/blob/go1.26.2/src/go/build/build.go#L354-L355
- Go go1.26.2 `net/http/pprof` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.2/src/net/http/pprof/pprof.go#L88
- Go go1.26.2 `testing/internal/testdeps` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.2/src/testing/internal/testdeps/deps.go#L23
- Go go1.26.2 `simd/archsimd/_gen/simdgen` command import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.2/src/simd/archsimd/_gen/simdgen/main.go#L91
- Go go1.26.3 `internal/goversion` `Version = 26` (checked October 2026): https://github.com/golang/go/blob/go1.26.3/src/internal/goversion/goversion.go#L12
- Go go1.26.3 `go/build` release tags derived from `goversion.Version` (checked October 2026): https://github.com/golang/go/blob/go1.26.3/src/go/build/build.go#L354-L355
- Go go1.26.3 `net/http/pprof` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.3/src/net/http/pprof/pprof.go#L88
- Go go1.26.3 `testing/internal/testdeps` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.3/src/testing/internal/testdeps/deps.go#L23
- Go go1.26.3 `simd/archsimd/_gen/simdgen` command import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.3/src/simd/archsimd/_gen/simdgen/main.go#L91
- Go go1.26.4 `internal/goversion` `Version = 26` (checked October 2026): https://github.com/golang/go/blob/go1.26.4/src/internal/goversion/goversion.go#L12
- Go go1.26.4 `go/build` release tags derived from `goversion.Version` (checked October 2026): https://github.com/golang/go/blob/go1.26.4/src/go/build/build.go#L354-L355
- Go go1.26.4 `net/http/pprof` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.4/src/net/http/pprof/pprof.go#L88
- Go go1.26.4 `testing/internal/testdeps` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.4/src/testing/internal/testdeps/deps.go#L23
- Go go1.26.4 `simd/archsimd/_gen/simdgen` command import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.4/src/simd/archsimd/_gen/simdgen/main.go#L91
- Go go1.26.6 `internal/goversion` `Version = 26` (checked October 2026): https://github.com/golang/go/blob/go1.26.6/src/internal/goversion/goversion.go#L12
- Go go1.26.6 `go/build` release tags derived from `goversion.Version` (checked October 2026): https://github.com/golang/go/blob/go1.26.6/src/go/build/build.go#L354-L355
- Go go1.26.6 `net/http/pprof` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.6/src/net/http/pprof/pprof.go#L88
- Go go1.26.6 `testing/internal/testdeps` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.6/src/testing/internal/testdeps/deps.go#L23
- Go go1.26.6 `simd/archsimd/_gen/simdgen` command import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.6/src/simd/archsimd/_gen/simdgen/main.go#L91
- Go go1.26.7 `internal/goversion` `Version = 26` (checked October 2026): https://github.com/golang/go/blob/go1.26.7/src/internal/goversion/goversion.go#L12
- Go go1.26.7 `go/build` release tags derived from `goversion.Version` (checked October 2026): https://github.com/golang/go/blob/go1.26.7/src/go/build/build.go#L354-L355
- Go go1.26.7 `net/http/pprof` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.7/src/net/http/pprof/pprof.go#L88
- Go go1.26.7 `testing/internal/testdeps` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.7/src/testing/internal/testdeps/deps.go#L23
- Go go1.26.7 `simd/archsimd/_gen/simdgen` command import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.7/src/simd/archsimd/_gen/simdgen/main.go#L91
- Go go1.26.8 `internal/goversion` `Version = 26` (checked October 2026): https://github.com/golang/go/blob/go1.26.8/src/internal/goversion/goversion.go#L12
- Go go1.26.8 `go/build` release tags derived from `goversion.Version` (checked October 2026): https://github.com/golang/go/blob/go1.26.8/src/go/build/build.go#L354-L355
- Go go1.26.8 `net/http/pprof` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.8/src/net/http/pprof/pprof.go#L88
- Go go1.26.8 `testing/internal/testdeps` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.8/src/testing/internal/testdeps/deps.go#L23
- Go go1.26.8 `simd/archsimd/_gen/simdgen` command import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.8/src/simd/archsimd/_gen/simdgen/main.go#L91
- Go go1.26.9 `internal/goversion` `Version = 26` (checked October 2026): https://github.com/golang/go/blob/go1.26.9/src/internal/goversion/goversion.go#L12
- Go go1.26.9 `go/build` release tags derived from `goversion.Version` (checked October 2026): https://github.com/golang/go/blob/go1.26.9/src/go/build/build.go#L354-L355
- Go go1.26.9 `net/http/pprof` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.9/src/net/http/pprof/pprof.go#L88
- Go go1.26.9 `testing/internal/testdeps` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.9/src/testing/internal/testdeps/deps.go#L23
- Go go1.26.9 `simd/archsimd/_gen/simdgen` command import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.9/src/simd/archsimd/_gen/simdgen/main.go#L91
- Go go1.26.10 `internal/goversion` `Version = 26` (checked October 2026): https://github.com/golang/go/blob/go1.26.10/src/internal/goversion/goversion.go#L12
- Go go1.26.10 `go/build` release tags derived from `goversion.Version` (checked October 2026): https://github.com/golang/go/blob/go1.26.10/src/go/build/build.go#L354-L355
- Go go1.26.10 `net/http/pprof` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.10/src/net/http/pprof/pprof.go#L88
- Go go1.26.10 `testing/internal/testdeps` import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.10/src/testing/internal/testdeps/deps.go#L23
- Go go1.26.10 `simd/archsimd/_gen/simdgen` command import of `runtime/pprof` (checked October 2026): https://github.com/golang/go/blob/go1.26.10/src/simd/archsimd/_gen/simdgen/main.go#L91
- Create-file validation: https://github.com/ollama/ollama/blob/v0.34.2/server/create.go
- Blob-path validation: https://github.com/ollama/ollama/blob/v0.34.2/manifest/paths.go
- Registry transfers and redirect restrictions: https://github.com/ollama/ollama/blob/v0.34.2/server/images.go
- Registry and model-name parsing: https://github.com/ollama/ollama/blob/v0.34.2/types/model/name.go
- Modelfile reference: https://github.com/ollama/ollama/blob/v0.34.2/docs/modelfile.mdx
- Ollama model inventory and digests (rolling documentation, checked September 2026): https://docs.ollama.com/api/tags
- Ollama model details (rolling documentation, checked September 2026): https://docs.ollama.com/api-reference/show-model-details
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


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- ollama: Ollama (v0.34.2)
- commit: Ollama release commit (dfabde4539e42ba1e1eab50a3a50b88aea7958a0)
- ollama-rolling: Ollama documentation (rolling) (unknown)
- docker: Docker Engine localhost boundary (28.0)
- systemd: systemd (v257)
- go: Go (go1.26.5)
- go-1-26-0: Go (go1.26.0)
- go-1-26-1: Go (go1.26.1)
- go-1-26-2: Go (go1.26.2)
- go-1-26-3: Go (go1.26.3)
- go-1-26-4: Go (go1.26.4)
- go-1-26-6: Go (go1.26.6)
- go-1-26-7: Go (go1.26.7)
- go-1-26-8: Go (go1.26.8)
- go-1-26-9: Go (go1.26.9)
- go-1-26-10: Go (go1.26.10)
- trifles: github.com/dgryski/trifles (v0.0.0-20200323201526-dd97f9abfb48)
- compress: github.com/klauspost/compress (v1.18.3)
- x-text: golang.org/x/text (v0.30.0)
- go-toml: github.com/pelletier/go-toml/v2 (v2.2.2)
- nginx: nginx (unknown)
- htpasswd: Apache htpasswd (unknown)
- caddy: Caddy (unknown)
- cloudflare: Cloudflare (unknown)
- owasp: OWASP password guidance (unknown)
- curl: curl (unknown)

Claims (full source mapping in the JSON block below):

- local-auth (REASONED; ollama, ollama-rolling): Local API has no inbound authentication; cloud keys and OLLAMA_AUTH concern upstream signing.
- local-tls (REASONED; ollama): Ollama serves plaintext; an https prefix in OLLAMA_HOST does not enable TLS.
- host-bind (REASONED; ollama, systemd): Standalone default is 127.0.0.1:11434; set OLLAMA_HOST in the service and reload/restart systemd.
- container-bind (REASONED; ollama, docker): Official image sets 0.0.0.0:11434 internally; bridge publication and container binding are separate.
- publication (REASONED; docker): Use 127.0.0.1:11434:11434 with Engine 28.0+; earlier same-L2 access defeats this boundary; unpublished private networks are an alternative.
- host-network (REASONED; ollama, docker): Host networking ignores publication flags; override the image listener and restrict authorized peers.
- basic-auth (REASONED; nginx): nginx server-scope Basic auth protects permitted locations; denied paths/methods may reject before authentication.
- password-hash (REASONED; htpasswd, owasp): Use prompted htpasswd -B -C 12; bare -B defaults to bcrypt cost 5, below the cited minimum 10.
- tls-proxy (REASONED; nginx): Publish authenticated TLS; encrypt the backend leg separately when proxy and Ollama are on different hosts.
- host-header (REASONED; ollama, nginx): Proxy Host localhost:11434 avoids loopback middleware hostname rejection; it is not authentication.
- idle-timeout (REASONED; nginx): proxy_read_timeout 300s limits gaps between reads, not total generation duration.
- caddy-policy (REASONED; caddy): Caddy Basic auth, exact POST /api/chat matcher and fallback deny other paths; supply admission limits separately.
- bearer-policy (REASONED; nginx): Exact nginx bearer comparison is a shared configuration secret without a constant-time guarantee; repeat it in every permitted location.
- mtls (REASONED; nginx): Dedicated client CA and ssl_verify_client require certificate lifecycle management; combine Basic auth only deliberately.
- access (REASONED; cloudflare, nginx): Access authenticates the tunnel; target a loopback policy proxy on 11435 to retain inference-only authorization.
- access-host (REASONED; cloudflare, ollama): originRequest.httpHostHeader and the final proxy retain localhost:11434; keep both local listeners private.
- access-limits (REASONED; cloudflare, nginx): Access authentication supplies no inference budgets; retain proxy limits, optionally add WAF rate limits and trusted client-address handling.
- mfa (REASONED; cloudflare): Human MFA belongs at the fronting identity layer; machine service tokens are not a human MFA flow.
- inference-policy (REASONED; nginx, ollama): Allow only exact required inference paths/methods; broad /api/ or /v1/ prefixes grant excessive authority.
- pull (REASONED; ollama): Keep POST /api/pull private: acquisition consumes storage and network capacity.
- push (REASONED; ollama): Keep POST /api/push private: export has separate upstream authorization.
- create (REASONED; ollama): Keep POST /api/create private: it creates/replaces definitions and processes uploaded model material.
- copy (REASONED; ollama): Keep POST /api/copy private: it creates another model name.
- delete (REASONED; ollama): Keep DELETE /api/delete private: it removes models and associated data.
- blob-write (REASONED; ollama): Keep POST /api/blobs/:digest private: it uploads model-store bytes.
- blob-read (REASONED; ollama): Keep HEAD /api/blobs/:digest private: it reveals blob existence.
- other-routes (REASONED; ollama): Default denial excludes account, experimental web, desktop proxy and unused compatibility routes. Source reading, not run: the Codex Desktop handler, which its comments place on the existing Ollama listener under /api/codex, opens no listener, and its peer check accepts any loopback TCP address, which this guide infers a same-host proxy has only over loopback.
- file-validation (REASONED; ollama): Create validates relative filenames and blob paths; arbitrary host-file access is not established at this pin.
- transfer (REASONED; ollama, commit): Management transfers are egress/disk-fill surfaces; insecure alters redirect protections, without demonstrating unrestricted SSRF.
- origins (REASONED; ollama): OLLAMA_ORIGINS adds to built-in origins; removing wildcards is neither authentication nor an exclusive-origin policy.
- service-user (REASONED; ollama): Use a dedicated account and writable store; preserve GPU access and do not assume the container shares installer identity.
- store (REASONED; ollama, systemd): Proposed 0700 directories, 0600 files and UMask=0077 need existing-permission/ACL inspection; separate service configuration and proxy keys.
- model-path (REASONED; ollama): OLLAMA_MODELS relocates models, not the entire service home or signing keys.
- loaded-models (REASONED; ollama): Loaded-model capacity is automatic unless configured; the example selects one model, not a total memory cap.
- parallel (REASONED; ollama): OLLAMA_NUM_PARALLEL defaults to 1.
- queue (REASONED; ollama): OLLAMA_MAX_QUEUE defaults to 512; the example selects 16 without promising the seventeenth HTTP request is refused.
- keep-alive (REASONED; ollama): Keep-alive defaults to five minutes; one minute is the example, and requests can override it.
- context (REASONED; ollama): Context defaults are VRAM-dependent 4K/32K/256K; implementation thresholds are roughly 23/47 GiB after overhead versus nominal 24/48 GiB.
- rate (REASONED; nginx): Example nginx source-address rate is 2r/s, burst 4 nodelay, with 429 responses; trusted client-address handling matters behind proxies.
- concurrency (REASONED; nginx): Example nginx server-name budget is four active requests with 429; it does not cap every idle/incomplete connection.
- body-limit (REASONED; nginx): Example body cap is 1 MiB; a larger valid fixture should get 413 without upstream work.
- parameters (REASONED; ollama): Gateway must validate model, num_ctx, num_predict and keep_alive; defaults/path allowlists do not enforce JSON ceilings.
- registry-names (REASONED; ollama): Fully qualified registry names are supported; unqualified names select Ollama's registry and omitted tags select latest.
- provenance (REASONED; ollama, ollama-rolling): Compare deployed tags digests with independent approval; mutable tags/digest equality do not establish publisher trust.
- local-import (REASONED; ollama): CLI imports reviewed local GGUF through a Modelfile; artifact SHA-256 and manifest digest are different identifiers.
- registry-egress (REASONED; ollama): Restrict acquisition/export to administrators and constrain egress; compare approved and controlled disallowed transfers.
- cloud (REASONED; ollama): OLLAMA_NO_CLOUD=1 disables cloud models and web search after restart; it is not a no-network switch.
- remotes (REASONED; ollama): OLLAMA_REMOTES selects remote-model hosts, not a registry allowlist.
- diagnostics (REASONED; ollama, ollama-rolling): Keep root, version, status, tags, ps and show private; model details can disclose templates/system prompts.
- request-logs (REASONED; ollama): Disable OLLAMA_DEBUG and OLLAMA_DEBUG_LOG_REQUESTS; existing request captures/replay scripts need separate cleanup.
- profiling (REASONED; ollama): No metrics route was found in the main router; this guide assesses that first-party v0.34.2 code registers no pprof handler. Shipped-binary pprof availability remains unestablished: observe the binary, deny public profiling, infer nothing from debug settings.
- profiling-scope (REASONED; ollama, trifles, compress, x-text): Go 1.26.5 go list runs for this guide found neither net/http/pprof nor runtime/pprof in the default-tag v0.34.2 main-package graph for every go tool dist list pair that loaded, cgo off and, where supported, on; five cgo-off android and ios runs failed. This guide infers no go.sum dependency adds either; Go outside 1.26.x, standard-library imports, those runs and served-mux exposure stay open.
- profiling-tags (REASONED; ollama, go): From source reading, v0.34.2's first-party custom tags integration, fast, generate, release, library and updater_live gate only _test.go files, which go build ignores; appengine and os400 appear only in readline/term.go, importing only syscall. The dependency search ignored build constraints, so which dependency files these tags select was not determined; go list runs show generate selects one.
- profiling-tag-runs (REASONED; ollama, go, trifles, compress, x-text): Go 1.26.5 go list runs for this guide found neither net/http/pprof nor runtime/pprof in the v0.34.2 main-package graph with tag set updater_live, release,library, appengine, os400 or appengine,os400 on the eight first-class pairs, windows arm64 and aix ppc64, cgo off and on. This guide infers no first-party or go.sum module file adds either; standard-library imports and Go outside 1.26.x are open.
- profiling-generate (REASONED; ollama, go): Go 1.26.5 go list runs for v0.34.2 with tag sets containing generate failed on all ten pairs tried, cgo off and on, reporting both uniseg and main packages in dependency github.com/rivo/uniseg v0.4.7; -e reruns listed neither pprof package but marked that package with a load error, so whether such builds import either remains open.
- profiling-go-versions (REASONED; go-1-26-0, go-1-26-1, go-1-26-2, go-1-26-3, go-1-26-4, go-1-26-6, go-1-26-7, go-1-26-8, go-1-26-9, go-1-26-10, go): Source reading, not run: Go 1.26.0 to 1.26.10 except 1.26.5 match 1.26.5: goversion is 26; ignoring build constraints, only net/http/pprof, testing/internal/testdeps and a package main command import runtime/pprof in non-test files outside cmd. No file imports the first two. This guide infers no such release adds either package to the 1.26.5 go list graphs; no graph was checked.
- profiling-deps-scan (REASONED; ollama, trifles, compress, x-text, go-toml): From source reading, ignoring build constraints, only package main files in the 93 dependency modules with go.sum zip hashes import net/http/pprof or runtime/pprof. Imports followed from first-party packages stay in those modules and the unread standard library, so this guide infers no such module adds either at those versions. The 15 cached modules with no go.sum zip hash were excluded.
- profiling-mux (REASONED; go, ollama): This guide's inference, not run: Go 1.26.5 net/http/pprof's init registers /debug/pprof/ handlers on http.DefaultServeMux, which a server with a nil Handler, as in v0.34.2's Serve, uses, so a build linking that package would serve them on the Ollama listener, while builds whose go list graph lacks it get none from it.
- profiling-release (REASONED; ollama): From this guide's reading of v0.34.2's Dockerfile, build scripts and release workflow, which show intended builds rather than artifact contents, the main package is built with no -tags, and with CGO_ENABLED=1 in the Dockerfile, the darwin build and both Windows CLI builds. The go.mod declares go 1.26.0, which the Dockerfile uses to choose Go, while this guide's go list runs used Go 1.26.5.
- profiling-app-runs (REASONED; ollama): Go 1.26.5 go list -e -deps runs for this guide list no net/http/pprof or runtime/pprof for the v0.34.2 desktop app main package on darwin/windows amd64 and arm64, cgo off and on; linux lists only the error-marked main package. Loaded cells mark app/ui (no app/dist); cgo-off cells cannot load cgo-only app/webview and omit the main package's cgo files with no error, so imports may be incomplete.
- profiling-app-listener (REASONED; ollama, go): From source reading, the app's UI listener is loopback (127.0.0.1:0, or 3001 in dev mode), served by an http.Server with a non-nil Handler whose mux has a token-cookie check on /api/v1 routes, proxy and catch-all routes without it, and no /debug/pprof pattern. This guide's inference, not run: even a build linking net/http/pprof would not serve DefaultServeMux handlers there.
- profiling-app-gateway (REASONED; ollama, go): From source reading, another loopback app listener is the Claude Desktop gateway on 127.0.0.1:11435, in macOS cgo builds, started only when Claude Desktop is installed. Its non-nil Handler refuses non-loopback Host values and a non-empty first Origin, serves four routes, not /debug/pprof, and forwards only POST /v1/messages, stripping caller auth headers, to the app's OLLAMA_HOST; not run.
- profiling-app-gateway-start (REASONED; ollama): Source reading, not run: startup starts the gateway only if Claude Desktop is installed and configured to use it; setClaudeGatewayInstalled, prepareClaudeDesktopConnection and model mapping start it if installed. The first two stop it unless Claude Desktop then uses it (the first not after an auto-mode error); mapping, if none existed, stops it on profile-change errors except restart confirmation.
- profiling-app-release (REASONED; ollama): By this guide's reading of intended builds, not artifacts, build_darwin.sh builds the app package with GOOS=darwin, CGO_ENABLED=1, amd64 and arm64 and no -tags. In build_windows.ps1, buildApp builds it with no -tags, by default setting no GOARCH under its unconditional CGO_ENABLED=1 and, when the cross-compile tools are present, for arm64 (GOOS=windows, GOARCH=arm64, CGO_ENABLED=1).
- desktop-app-server (REASONED; ollama): From source reading, the desktop app serves no HTTP on the Ollama API listener itself: it runs the separate ollama binary with serve and restarts it, and the spawn copies the app's own environment, setting OLLAMA_HOST=0.0.0.0 when the Expose setting is on, so that setting or an inherited OLLAMA_HOST can expose that process. No shipped app binary was inspected and no run observed these behaviours.
- verify-inventory (REASONED; ollama, docker, systemd): Inspect namespaces, publication, identity, store and ACLs; local ss output alone does not establish isolation.
- verify-bypass (REASONED; ollama, curl): HTTP means direct 11434 answered; fixed refusal needs the real remote path plus successful proxy inference; local errors are inconclusive.
- verify-auth (REASONED; nginx, ollama, curl): Absent/wrong credentials must refuse while correct credentials complete chat; streamed 200 alone is insufficient.
- verify-tls (REASONED; nginx, curl): Correct trust/hostname succeeds; wrong trust/hostname and missing/untrusted mTLS certificates must fail before inference.
- verify-management (REASONED; ollama): Public management must be denied without upstream mutation; private admin operations and public chat supply positive controls.
- verify-tags (REASONED; nginx, ollama-rolling): Public tags may return 404 with valid credentials; private tags should return model JSON; public 404 is not an authentication test.
- verify-origins (REASONED; ollama, nginx, caddy): Compare unwanted, required and built-in origins with actual browser calls; POST-only proxy preflight refusals differ by variant.
- verify-rate (REASONED; nginx): Eight bounded requests test admission with limiter/upstream evidence and recovery; the burst alone does not demonstrate both limiters.
- verify-concurrency (REASONED; nginx): Hold four accepted requests active within the rate budget, reject another, then confirm a freed slot accepts work.
- verify-scheduler (REASONED; ollama): Compare loading/eviction, keep-alive expiry and actual queue occupancy; public limits can prevent exercising the private queue.
- verify-cloud (REASONED; ollama): Authorized cloud chat works before disablement and refuses afterward while local chat succeeds; invalid credentials/models are inconclusive.
- verify-captures (REASONED; ollama): Compare completed canary requests with logging enabled/disabled in the actual temporary namespace; deny public diagnostics while private controls work.
- proxy-parsing (REASONED; nginx, caddy): nginx -t and caddy validate check configuration acceptance only; native parsing was not demonstrated here.
- curl-version (REASONED; curl): Displayed exitcode and errormsg write-out variables need curl 7.75.0 or later; no tested curl release is recorded.

````json
{
  "schema": 1,
  "checked": "2026-10-22",
  "documentation_checked": "2026-09",
  "body_sha256": "40580ccfc05b2a68a72437964ebc1ef686448452c444fa338c992705a3407b5b",
  "components": {
    "ollama": {
      "name": "Ollama",
      "basis": "v0.34.2",
      "sources": {
        "s96f77aee8bdd": "https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go",
        "sd146dc5d917d": "https://github.com/ollama/ollama/blob/v0.34.2/api/client.go",
        "s7478dad099ab": "https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go",
        "s9bf8940c3001": "https://github.com/ollama/ollama/blob/v0.34.2/main.go#L3-L13",
        "s8f4e8b651967": "https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go#L2469-L2475",
        "sc16932a1056b": "https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go#L2632-L2654",
        "s3db39cecc705": "https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go#L2377-L2654",
        "s8a310972e31d": "https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go#L2093-L2109",
        "s5a188d13a009": "https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go#L1987-L1992",
        "s0b381e62597c": "https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go#L2001-L2011",
        "sa340a3deada2": "https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go#L2052-L2057",
        "sbf4266cc6ffa": "https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go#L3-L54",
        "sce8e789d8d24": "https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go#L1938-L2060",
        "s4ded5c727f27": "https://github.com/ollama/ollama/blob/v0.34.2/cmd/cmd.go#L3-L60",
        "sc0d5747ba398": "https://github.com/ollama/ollama/blob/v0.34.2/server/routes.go#L1",
        "s98a6abaa3838": "https://github.com/ollama/ollama/blob/v0.34.2/integration/basic_test.go#L1",
        "s9a29ad2cbe09": "https://github.com/ollama/ollama/blob/v0.34.2/integration/reg_groups_test.go#L1",
        "s748c551a2a08": "https://github.com/ollama/ollama/blob/v0.34.2/integration/generate_jinja_test.go#L1",
        "sd7c08f30e61e": "https://github.com/ollama/ollama/blob/v0.34.2/app/updater/updater_live_test.go#L1",
        "s720db4671dfd": "https://github.com/ollama/ollama/blob/v0.34.2/readline/term.go#L1-L7",
        "sbca403d10498": "https://github.com/ollama/ollama/blob/v0.34.2/docs/faq.mdx",
        "s2abe15b73bce": "https://github.com/ollama/ollama/blob/v0.34.2/envconfig/config.go",
        "s8dc81acdfb10": "https://github.com/ollama/ollama/blob/v0.34.2/Dockerfile",
        "s8379cd00dbf9": "https://github.com/ollama/ollama/blob/v0.34.2/docs/api.md",
        "s01c0c71afa78": "https://github.com/ollama/ollama/blob/v0.34.2/server/create.go",
        "s1ded6de8ebe0": "https://github.com/ollama/ollama/blob/v0.34.2/manifest/paths.go",
        "s8b9d4257c3df": "https://github.com/ollama/ollama/blob/v0.34.2/server/images.go",
        "s453c95c884da": "https://github.com/ollama/ollama/blob/v0.34.2/docs/linux.mdx",
        "s52649b124738": "https://github.com/ollama/ollama/blob/v0.34.2/scripts/install.sh",
        "s27e1a359c744": "https://github.com/ollama/ollama/blob/v0.34.2/server/sched.go",
        "sfb778cd7de39": "https://github.com/ollama/ollama/blob/v0.34.2/api/types.go",
        "s4112a1bdf03c": "https://github.com/ollama/ollama/blob/v0.34.2/docs/context-length.mdx",
        "sa8c4675db386": "https://github.com/ollama/ollama/blob/v0.34.2/types/model/name.go",
        "s14266d6e90ae": "https://github.com/ollama/ollama/blob/v0.34.2/docs/modelfile.mdx",
        "sa89bd5d8e1f7": "https://github.com/ollama/ollama/blob/v0.34.2/server/inference_request_log.go",
        "s2422d51c7511": "https://github.com/ollama/ollama/blob/v0.34.2/go.mod#L3",
        "sc2b36fe862cd": "https://github.com/ollama/ollama/blob/v0.34.2/Dockerfile#L249-L263",
        "s048a8041e459": "https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_darwin.sh#L88-L89",
        "s69d878a2f01f": "https://github.com/ollama/ollama/blob/v0.34.2/cmake/local.cmake#L656-L703",
        "saffcf6c517dc": "https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L864-L919",
        "s50dc1a212bc5": "https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L71-L82",
        "s2c83e3be00ef": "https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L355-L379",
        "sfbdb6f7a76af": "https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L210-L230",
        "s0c28c94bb1ee": "https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L296",
        "sdc9725a324a3": "https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L1299",
        "s383b8a85907a": "https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L13-L25",
        "sdf3692260fb9": "https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L340",
        "s73deff2c03e1": "https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L895-L907",
        "s99ff5d94d99e": "https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L231",
        "s3d177b1fcaf1": "https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L295",
        "s54c3a8422a93": "https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L34",
        "s83f85bf889db": "https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L479-L556",
        "sae92e96027b1": "https://github.com/ollama/ollama/blob/v0.34.2/.github/workflows/release.yaml#L561-L661",
        "sc8a033a390da": "https://github.com/ollama/ollama/blob/v0.34.2/go.mod#L5-L91",
        "sfc02278c501f": "https://github.com/ollama/ollama/blob/v0.34.2/go.sum",
        "sad61f21372d7": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app.go#L1-L33",
        "s73b81a1f8d04": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app.go#L186-L196",
        "s67fd6cba9588": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app.go#L279-L292",
        "s243bac4ebddb": "https://github.com/ollama/ollama/blob/v0.34.2/app/ui/ui.go#L193-L224",
        "s4421d53f8855": "https://github.com/ollama/ollama/blob/v0.34.2/app/ui/ui.go#L277-L320",
        "sa4c68b27021b": "https://github.com/ollama/ollama/blob/v0.34.2/app/server/server.go#L241-L252",
        "sf38afcc73250": "https://github.com/ollama/ollama/blob/v0.34.2/app/ui/app.go#L15-L16",
        "s45897fae891f": "https://github.com/ollama/ollama/blob/v0.34.2/app/webview/webview.go#L51",
        "s46dc00636dd6": "https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_darwin.sh#L200-L216",
        "sde507d86d7ac": "https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L980-L1004",
        "s2b2be911f51e": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L10",
        "s84f1c8cf636d": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L95-L96",
        "sd92431ef4485": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L535",
        "sb5822b8eeabd": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L546-L561",
        "sb8e91213cc53": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L592-L598",
        "se1879bd92d00": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L1202-L1229",
        "s9a2533a8e3e0": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L1472-L1487",
        "s29f084ce74cf": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L1639-L1661",
        "s132b1b4bbbe5": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L614-L631",
        "s58d1846a87f0": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L944-L951",
        "s8b3afc8d9f86": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L23-L26",
        "sba33d5d074d0": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L131-L132",
        "s5897f909de84": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L198-L221",
        "saf6c2bd158fc": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L300-L361",
        "sd5ce93133b59": "https://github.com/ollama/ollama/blob/v0.34.2/app/server/server.go#L190-L225",
        "s80b241b854c7": "https://github.com/ollama/ollama/blob/v0.34.2/app/server/server.go#L49-L51",
        "se6c615cc2b3a": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/webview.go#L6",
        "s52f3436c9021": "https://github.com/ollama/ollama/blob/v0.34.2/scripts/build_windows.ps1#L994-L997",
        "sd1743f37dd2c": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L1568-L1573",
        "s8b982a956f29": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L1694-L1698",
        "s4100d1423b14": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L419-L435",
        "s4b2897a4f253": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L363-L380",
        "sc0473f9f9c2d": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L126-L130",
        "s879be6ebc8ca": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L442-L511",
        "s5804726fe842": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L594-L634",
        "s8aef89b5f98b": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L741-L748",
        "sc87414a09b6f": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L807-L818",
        "sfaac9168b667": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L636-L724",
        "s959e3b79b691": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L27-L31",
        "s90d8365f6905": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L143",
        "s11e3644384be": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L599-L609",
        "s6a1dfd450763": "https://github.com/ollama/ollama/blob/v0.34.2/envconfig/config.go#L20-L60",
        "s6cab16cc1556": "https://github.com/ollama/ollama/blob/v0.34.2/envconfig/config.go#L62-L83",
        "s99dbaec1750f": "https://github.com/ollama/ollama/blob/v0.34.2/envconfig/config.go#L378-L380",
        "sebb66adac984": "https://github.com/ollama/ollama/blob/v0.34.2/app/ui/app.go#L5-L13",
        "se3e2cfa03db9": "https://github.com/ollama/ollama/blob/v0.34.2/app/ui/ui.go#L6-L39",
        "sb7983eb0757d": "https://github.com/ollama/ollama/blob/v0.34.2/app/webview/webview.go#L53-L60",
        "sd4620366d20d": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/app_darwin.go#L12-L44",
        "sc918a5f51d7d": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/webview.go#L8-L26",
        "sb9475646ce87": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop_models.go#L16-L35",
        "s5f7ba12ad29a": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop_models.go#L308-L353",
        "s679019d0fd06": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L146-L148",
        "s886dd375d7b9": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop_models.go#L183-L200",
        "s47c363d28175": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop_models.go#L433-L467",
        "s24f723d1ab2a": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L519-L555",
        "s7521ebbabc63": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop_access.go#L55-L124",
        "sd3d0dcc68985": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/claude_desktop.go#L750-L799",
        "s18ae5e5655cf": "https://github.com/ollama/ollama/blob/v0.34.2/app/ui/extract.go#L5-L14",
        "s9338302936c6": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/codex_app_darwin.go#L5-L25",
        "see893978ecc6": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/codex_app_darwin.go",
        "s1db2e43b7b45": "https://github.com/ollama/ollama/blob/v0.34.2/app/cmd/app/codex_app_darwin.go#L35-L48",
        "s3f66206086dd": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go",
        "s141dcff0708a": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L26-L29",
        "s8ab7a3732a2c": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L59-L61",
        "s17e93913af2b": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L156-L176",
        "sf35837ccc256": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L192-L263",
        "s5ac8a92f00fd": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L358-L375",
        "s1cd9864b2a34": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L517-L533",
        "s848cbf05de34": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L643-L653",
        "s292d5f730519": "https://github.com/ollama/ollama/blob/v0.34.2/internal/proxy/codex_desktop.go#L678-L684"
      }
    },
    "commit": {
      "name": "Ollama release commit",
      "basis": "dfabde4539e42ba1e1eab50a3a50b88aea7958a0",
      "sources": {
        "s673919ab300f": "https://github.com/ollama/ollama/commit/dfabde4539e42ba1e1eab50a3a50b88aea7958a0"
      }
    },
    "ollama-rolling": {
      "name": "Ollama documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "sf49fae5df9fd": "https://docs.ollama.com/api/authentication",
        "s6c2961786919": "https://docs.ollama.com/api/tags",
        "s528f69db04e0": "https://docs.ollama.com/api-reference/show-model-details"
      }
    },
    "docker": {
      "name": "Docker Engine localhost boundary",
      "basis": "28.0",
      "sources": {
        "s1e53417c513d": "https://docs.docker.com/engine/network/port-publishing/"
      }
    },
    "systemd": {
      "name": "systemd",
      "basis": "v257",
      "sources": {
        "sd4c1aeb45417": "https://github.com/systemd/systemd/blob/v257/man/systemd.exec.xml"
      }
    },
    "go": {
      "name": "Go",
      "basis": "go1.26.5",
      "sources": {
        "sab55ef9009c4": "https://github.com/golang/go/blob/go1.26.5/src/net/http/pprof/pprof.go#L96-L106",
        "s2e779f75153e": "https://github.com/golang/go/blob/go1.26.5/src/net/http/server.go#L2870-L2878",
        "s038b2186ee21": "https://github.com/golang/go/blob/go1.26.5/src/net/http/server.go#L2971",
        "sa0c56e16001f": "https://github.com/golang/go/blob/go1.26.5/src/net/http/server.go#L3302-L3306",
        "s7f4cde22e030": "https://github.com/golang/go/blob/go1.26.5/src/cmd/go/alldocs.go#L83",
        "sdba7b87fda8d": "https://github.com/golang/go/blob/go1.26.5/src/cmd/go/alldocs.go#L236-L240",
        "s7290caae7a3c": "https://github.com/golang/go/blob/go1.26.5/src/net/http/header.go#L43-L51",
        "s0388b420c217": "https://github.com/golang/go/blob/go1.26.5/src/internal/goversion/goversion.go#L12",
        "sbf25f8fb5cce": "https://github.com/golang/go/blob/go1.26.5/src/go/build/build.go#L354-L355",
        "s41262ad87b65": "https://github.com/golang/go/blob/go1.26.5/src/net/http/pprof/pprof.go#L88",
        "s80e5cbbd9e14": "https://github.com/golang/go/blob/go1.26.5/src/testing/internal/testdeps/deps.go#L23",
        "s63df9d2be607": "https://github.com/golang/go/blob/go1.26.5/src/simd/archsimd/_gen/simdgen/main.go#L91"
      }
    },
    "go-1-26-0": {
      "name": "Go",
      "basis": "go1.26.0",
      "sources": {
        "s7670be382fd6": "https://github.com/golang/go/blob/go1.26.0/src/internal/goversion/goversion.go#L12",
        "s7134707033bd": "https://github.com/golang/go/blob/go1.26.0/src/go/build/build.go#L354-L355",
        "sc4d5a418cc8a": "https://github.com/golang/go/blob/go1.26.0/src/net/http/pprof/pprof.go#L88",
        "s63f63360f142": "https://github.com/golang/go/blob/go1.26.0/src/testing/internal/testdeps/deps.go#L23",
        "se924f730cd16": "https://github.com/golang/go/blob/go1.26.0/src/simd/archsimd/_gen/simdgen/main.go#L91"
      }
    },
    "go-1-26-1": {
      "name": "Go",
      "basis": "go1.26.1",
      "sources": {
        "sc2735a74234b": "https://github.com/golang/go/blob/go1.26.1/src/internal/goversion/goversion.go#L12",
        "sc15133c74365": "https://github.com/golang/go/blob/go1.26.1/src/go/build/build.go#L354-L355",
        "sd0122b4596e5": "https://github.com/golang/go/blob/go1.26.1/src/net/http/pprof/pprof.go#L88",
        "sa24dcdd9e52c": "https://github.com/golang/go/blob/go1.26.1/src/testing/internal/testdeps/deps.go#L23",
        "s2a55e411da1d": "https://github.com/golang/go/blob/go1.26.1/src/simd/archsimd/_gen/simdgen/main.go#L91"
      }
    },
    "go-1-26-2": {
      "name": "Go",
      "basis": "go1.26.2",
      "sources": {
        "sa8ba29c45871": "https://github.com/golang/go/blob/go1.26.2/src/internal/goversion/goversion.go#L12",
        "se0e77cda3f1d": "https://github.com/golang/go/blob/go1.26.2/src/go/build/build.go#L354-L355",
        "s058a974ee5d5": "https://github.com/golang/go/blob/go1.26.2/src/net/http/pprof/pprof.go#L88",
        "s019e0fb220fc": "https://github.com/golang/go/blob/go1.26.2/src/testing/internal/testdeps/deps.go#L23",
        "s8a4dc2d3db9b": "https://github.com/golang/go/blob/go1.26.2/src/simd/archsimd/_gen/simdgen/main.go#L91"
      }
    },
    "go-1-26-3": {
      "name": "Go",
      "basis": "go1.26.3",
      "sources": {
        "sdc07d97a87b6": "https://github.com/golang/go/blob/go1.26.3/src/internal/goversion/goversion.go#L12",
        "s5aea4d01f83c": "https://github.com/golang/go/blob/go1.26.3/src/go/build/build.go#L354-L355",
        "sed7ba616e62c": "https://github.com/golang/go/blob/go1.26.3/src/net/http/pprof/pprof.go#L88",
        "s040d1ea399ae": "https://github.com/golang/go/blob/go1.26.3/src/testing/internal/testdeps/deps.go#L23",
        "s898567a72486": "https://github.com/golang/go/blob/go1.26.3/src/simd/archsimd/_gen/simdgen/main.go#L91"
      }
    },
    "go-1-26-4": {
      "name": "Go",
      "basis": "go1.26.4",
      "sources": {
        "s2fd10ac9b790": "https://github.com/golang/go/blob/go1.26.4/src/internal/goversion/goversion.go#L12",
        "seae65bce1fda": "https://github.com/golang/go/blob/go1.26.4/src/go/build/build.go#L354-L355",
        "s860b46eaab36": "https://github.com/golang/go/blob/go1.26.4/src/net/http/pprof/pprof.go#L88",
        "s2104c8373c85": "https://github.com/golang/go/blob/go1.26.4/src/testing/internal/testdeps/deps.go#L23",
        "s0e9e578b8243": "https://github.com/golang/go/blob/go1.26.4/src/simd/archsimd/_gen/simdgen/main.go#L91"
      }
    },
    "go-1-26-6": {
      "name": "Go",
      "basis": "go1.26.6",
      "sources": {
        "s8b8ebc7e8db6": "https://github.com/golang/go/blob/go1.26.6/src/internal/goversion/goversion.go#L12",
        "s3709671e863b": "https://github.com/golang/go/blob/go1.26.6/src/go/build/build.go#L354-L355",
        "sb1475154fbb7": "https://github.com/golang/go/blob/go1.26.6/src/net/http/pprof/pprof.go#L88",
        "s974c60526bb6": "https://github.com/golang/go/blob/go1.26.6/src/testing/internal/testdeps/deps.go#L23",
        "s52851e8b4312": "https://github.com/golang/go/blob/go1.26.6/src/simd/archsimd/_gen/simdgen/main.go#L91"
      }
    },
    "go-1-26-7": {
      "name": "Go",
      "basis": "go1.26.7",
      "sources": {
        "s17ad8bf46090": "https://github.com/golang/go/blob/go1.26.7/src/internal/goversion/goversion.go#L12",
        "sd315e2226ae8": "https://github.com/golang/go/blob/go1.26.7/src/go/build/build.go#L354-L355",
        "s54141d62f948": "https://github.com/golang/go/blob/go1.26.7/src/net/http/pprof/pprof.go#L88",
        "sf081388dd0f7": "https://github.com/golang/go/blob/go1.26.7/src/testing/internal/testdeps/deps.go#L23",
        "s64e2db3b685b": "https://github.com/golang/go/blob/go1.26.7/src/simd/archsimd/_gen/simdgen/main.go#L91"
      }
    },
    "go-1-26-8": {
      "name": "Go",
      "basis": "go1.26.8",
      "sources": {
        "s6175e03794cf": "https://github.com/golang/go/blob/go1.26.8/src/internal/goversion/goversion.go#L12",
        "s7ed9d53e6261": "https://github.com/golang/go/blob/go1.26.8/src/go/build/build.go#L354-L355",
        "s88d4166a7bee": "https://github.com/golang/go/blob/go1.26.8/src/net/http/pprof/pprof.go#L88",
        "sa79ec4182285": "https://github.com/golang/go/blob/go1.26.8/src/testing/internal/testdeps/deps.go#L23",
        "s9ad74046b534": "https://github.com/golang/go/blob/go1.26.8/src/simd/archsimd/_gen/simdgen/main.go#L91"
      }
    },
    "go-1-26-9": {
      "name": "Go",
      "basis": "go1.26.9",
      "sources": {
        "s69637c613830": "https://github.com/golang/go/blob/go1.26.9/src/internal/goversion/goversion.go#L12",
        "sfd6e7fa1d8e8": "https://github.com/golang/go/blob/go1.26.9/src/go/build/build.go#L354-L355",
        "s71887e5f7cdf": "https://github.com/golang/go/blob/go1.26.9/src/net/http/pprof/pprof.go#L88",
        "s6728c0a5d0d1": "https://github.com/golang/go/blob/go1.26.9/src/testing/internal/testdeps/deps.go#L23",
        "s110ef73adaf3": "https://github.com/golang/go/blob/go1.26.9/src/simd/archsimd/_gen/simdgen/main.go#L91"
      }
    },
    "go-1-26-10": {
      "name": "Go",
      "basis": "go1.26.10",
      "sources": {
        "scff07ded2fad": "https://github.com/golang/go/blob/go1.26.10/src/internal/goversion/goversion.go#L12",
        "se93bdeb9d5e7": "https://github.com/golang/go/blob/go1.26.10/src/go/build/build.go#L354-L355",
        "sd61f4ff8d5d6": "https://github.com/golang/go/blob/go1.26.10/src/net/http/pprof/pprof.go#L88",
        "s9b82f1629b4d": "https://github.com/golang/go/blob/go1.26.10/src/testing/internal/testdeps/deps.go#L23",
        "s599b4645909f": "https://github.com/golang/go/blob/go1.26.10/src/simd/archsimd/_gen/simdgen/main.go#L91"
      }
    },
    "trifles": {
      "name": "github.com/dgryski/trifles",
      "basis": "v0.0.0-20200323201526-dd97f9abfb48",
      "sources": {
        "s38ad5e627932": "https://github.com/dgryski/trifles/blob/dd97f9abfb48/cstbucket/main.go#L1-L17",
        "seeae3b9d9459": "https://github.com/dgryski/trifles/blob/dd97f9abfb48/fastpprof/main.go#L1-L13",
        "s56182db1ad94": "https://github.com/dgryski/trifles/blob/dd97f9abfb48/jumpreplica/main.go#L1-L18",
        "s4e12f43a1afe": "https://github.com/dgryski/trifles/blob/dd97f9abfb48/lz/lz.go#L1-L11",
        "s6a11f78133a6": "https://github.com/dgryski/trifles/blob/dd97f9abfb48/matcher/main.go#L1-L13",
        "s82d128642faa": "https://github.com/dgryski/trifles/blob/dd97f9abfb48/quantiles/main.go#L1-L22",
        "s53fe5b36bae7": "https://github.com/dgryski/trifles/blob/dd97f9abfb48/udprelay/main.go#L1-L26",
        "s3c8772bb591f": "https://github.com/dgryski/trifles/blob/dd97f9abfb48/fastpprof/main.go#L16-L42"
      }
    },
    "compress": {
      "name": "github.com/klauspost/compress",
      "basis": "v1.18.3",
      "sources": {
        "sd309de5a57e2": "https://github.com/klauspost/compress/blob/v1.18.3/s2/cmd/s2c/main.go#L1-L27"
      }
    },
    "x-text": {
      "name": "golang.org/x/text",
      "basis": "v0.30.0",
      "sources": {
        "s7b232c7ac531": "https://github.com/golang/text/blob/v0.30.0/collate/tools/colcmp/colcmp.go#L5-L22"
      }
    },
    "go-toml": {
      "name": "github.com/pelletier/go-toml/v2",
      "basis": "v2.2.2",
      "sources": {
        "s263bb2467c05": "https://github.com/pelletier/go-toml/blob/v2.2.2/marshaler_test.go#L1571",
        "sf307292d806f": "https://github.com/pelletier/go-toml/blob/v2.2.2/marshaler_test.go#L1649"
      }
    },
    "nginx": {
      "name": "nginx",
      "basis": "unknown",
      "sources": {
        "sf32ce2956917": "https://nginx.org/en/docs/http/ngx_http_auth_basic_module.html",
        "s40bdf1af1596": "https://nginx.org/en/docs/http/ngx_http_core_module.html",
        "sf0bc2adae8cb": "https://nginx.org/en/docs/http/ngx_http_rewrite_module.html",
        "sda4ba3fcedbe": "https://nginx.org/en/docs/http/ngx_http_ssl_module.html",
        "sf3430c5a0b22": "https://nginx.org/en/docs/http/ngx_http_proxy_module.html",
        "sb3bee9429629": "https://nginx.org/en/docs/http/ngx_http_limit_req_module.html",
        "sddc43aac8779": "https://nginx.org/en/docs/http/ngx_http_limit_conn_module.html",
        "sa28876996ece": "https://nginx.org/en/docs/switches.html"
      }
    },
    "htpasswd": {
      "name": "Apache htpasswd",
      "basis": "unknown",
      "sources": {
        "scde9004bb967": "https://httpd.apache.org/docs/2.4/programs/htpasswd.html"
      }
    },
    "caddy": {
      "name": "Caddy",
      "basis": "unknown",
      "sources": {
        "sbc2bd9599bd1": "https://caddyserver.com/docs/caddyfile/directives/basic_auth",
        "s38b1b78ce980": "https://caddyserver.com/docs/caddyfile/matchers",
        "s39d7d5ee55e2": "https://caddyserver.com/docs/caddyfile/directives/handle",
        "s3865a73ccda3": "https://caddyserver.com/docs/caddyfile/directives/reverse_proxy",
        "sc5832c7dc52f": "https://caddyserver.com/docs/command-line"
      }
    },
    "cloudflare": {
      "name": "Cloudflare",
      "basis": "unknown",
      "sources": {
        "s4b65a8359a37": "https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/configure-tunnels/origin-parameters/",
        "s15ab6de85740": "https://developers.cloudflare.com/cloudflare-one/access-controls/service-credentials/service-tokens/",
        "sbd88e529ebf2": "https://developers.cloudflare.com/waf/rate-limiting-rules/"
      }
    },
    "owasp": {
      "name": "OWASP password guidance",
      "basis": "unknown",
      "sources": {
        "s49e8d76431d9": "https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html"
      }
    },
    "curl": {
      "name": "curl",
      "basis": "unknown",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    }
  },
  "claims": {
    "local-auth": {"text": "Local API has no inbound authentication; cloud keys and OLLAMA_AUTH concern upstream signing.", "components": ["ollama", "ollama-rolling"], "sources": ["ollama-rolling:sf49fae5df9fd", "ollama:s96f77aee8bdd", "ollama:sd146dc5d917d"], "status": "REASONED"},
    "local-tls": {"text": "Ollama serves plaintext; an https prefix in OLLAMA_HOST does not enable TLS.", "components": ["ollama"], "sources": ["ollama:s96f77aee8bdd", "ollama:s7478dad099ab"], "status": "REASONED"},
    "host-bind": {"text": "Standalone default is 127.0.0.1:11434; set OLLAMA_HOST in the service and reload/restart systemd.", "components": ["ollama", "systemd"], "sources": ["ollama:sbca403d10498", "ollama:s2abe15b73bce", "systemd:sd4c1aeb45417"], "status": "REASONED"},
    "container-bind": {"text": "Official image sets 0.0.0.0:11434 internally; bridge publication and container binding are separate.", "components": ["ollama", "docker"], "sources": ["ollama:s8dc81acdfb10", "docker:s1e53417c513d"], "status": "REASONED"},
    "publication": {"text": "Use 127.0.0.1:11434:11434 with Engine 28.0+; earlier same-L2 access defeats this boundary; unpublished private networks are an alternative.", "components": ["docker"], "sources": ["docker:s1e53417c513d"], "status": "REASONED"},
    "host-network": {"text": "Host networking ignores publication flags; override the image listener and restrict authorized peers.", "components": ["ollama", "docker"], "sources": ["ollama:s8dc81acdfb10", "docker:s1e53417c513d"], "status": "REASONED"},
    "basic-auth": {"text": "nginx server-scope Basic auth protects permitted locations; denied paths/methods may reject before authentication.", "components": ["nginx"], "sources": ["nginx:sf32ce2956917", "nginx:s40bdf1af1596", "nginx:sf0bc2adae8cb"], "status": "REASONED"},
    "password-hash": {"text": "Use prompted htpasswd -B -C 12; bare -B defaults to bcrypt cost 5, below the cited minimum 10.", "components": ["htpasswd", "owasp"], "sources": ["htpasswd:scde9004bb967", "owasp:s49e8d76431d9"], "status": "REASONED"},
    "tls-proxy": {"text": "Publish authenticated TLS; encrypt the backend leg separately when proxy and Ollama are on different hosts.", "components": ["nginx"], "sources": ["nginx:sda4ba3fcedbe"], "status": "REASONED"},
    "host-header": {"text": "Proxy Host localhost:11434 avoids loopback middleware hostname rejection; it is not authentication.", "components": ["ollama", "nginx"], "sources": ["ollama:s96f77aee8bdd", "nginx:sf3430c5a0b22"], "status": "REASONED"},
    "idle-timeout": {"text": "proxy_read_timeout 300s limits gaps between reads, not total generation duration.", "components": ["nginx"], "sources": ["nginx:sf3430c5a0b22"], "status": "REASONED"},
    "caddy-policy": {"text": "Caddy Basic auth, exact POST /api/chat matcher and fallback deny other paths; supply admission limits separately.", "components": ["caddy"], "sources": ["caddy:sbc2bd9599bd1", "caddy:s38b1b78ce980", "caddy:s39d7d5ee55e2", "caddy:s3865a73ccda3"], "status": "REASONED"},
    "bearer-policy": {"text": "Exact nginx bearer comparison is a shared configuration secret without a constant-time guarantee; repeat it in every permitted location.", "components": ["nginx"], "sources": ["nginx:sf0bc2adae8cb"], "status": "REASONED"},
    "mtls": {"text": "Dedicated client CA and ssl_verify_client require certificate lifecycle management; combine Basic auth only deliberately.", "components": ["nginx"], "sources": ["nginx:sda4ba3fcedbe"], "status": "REASONED"},
    "access": {"text": "Access authenticates the tunnel; target a loopback policy proxy on 11435 to retain inference-only authorization.", "components": ["cloudflare", "nginx"], "sources": ["cloudflare:s4b65a8359a37", "cloudflare:s15ab6de85740", "nginx:s40bdf1af1596"], "status": "REASONED"},
    "access-host": {"text": "originRequest.httpHostHeader and the final proxy retain localhost:11434; keep both local listeners private.", "components": ["cloudflare", "ollama"], "sources": ["cloudflare:s4b65a8359a37", "ollama:s96f77aee8bdd"], "status": "REASONED"},
    "access-limits": {"text": "Access authentication supplies no inference budgets; retain proxy limits, optionally add WAF rate limits and trusted client-address handling.", "components": ["cloudflare", "nginx"], "sources": ["cloudflare:sbd88e529ebf2", "nginx:sb3bee9429629"], "status": "REASONED"},
    "mfa": {"text": "Human MFA belongs at the fronting identity layer; machine service tokens are not a human MFA flow.", "components": ["cloudflare"], "sources": ["cloudflare:s15ab6de85740"], "status": "REASONED"},
    "inference-policy": {"text": "Allow only exact required inference paths/methods; broad /api/ or /v1/ prefixes grant excessive authority.", "components": ["nginx", "ollama"], "sources": ["nginx:s40bdf1af1596", "nginx:sf0bc2adae8cb", "ollama:s96f77aee8bdd"], "status": "REASONED"},
    "pull": {"text": "Keep POST /api/pull private: acquisition consumes storage and network capacity.", "components": ["ollama"], "sources": ["ollama:s8379cd00dbf9"], "status": "REASONED"},
    "push": {"text": "Keep POST /api/push private: export has separate upstream authorization.", "components": ["ollama"], "sources": ["ollama:s8379cd00dbf9"], "status": "REASONED"},
    "create": {"text": "Keep POST /api/create private: it creates/replaces definitions and processes uploaded model material.", "components": ["ollama"], "sources": ["ollama:s8379cd00dbf9", "ollama:s01c0c71afa78"], "status": "REASONED"},
    "copy": {"text": "Keep POST /api/copy private: it creates another model name.", "components": ["ollama"], "sources": ["ollama:s8379cd00dbf9"], "status": "REASONED"},
    "delete": {"text": "Keep DELETE /api/delete private: it removes models and associated data.", "components": ["ollama"], "sources": ["ollama:s8379cd00dbf9"], "status": "REASONED"},
    "blob-write": {"text": "Keep POST /api/blobs/:digest private: it uploads model-store bytes.", "components": ["ollama"], "sources": ["ollama:s8379cd00dbf9"], "status": "REASONED"},
    "blob-read": {"text": "Keep HEAD /api/blobs/:digest private: it reveals blob existence.", "components": ["ollama"], "sources": ["ollama:s8379cd00dbf9"], "status": "REASONED"},
    "other-routes": {"text": "Default denial excludes account, experimental web, desktop proxy and unused compatibility routes. Source reading, not run: the Codex Desktop handler, which its comments place on the existing Ollama listener under /api/codex, opens no listener, and its peer check accepts any loopback TCP address, which this guide infers a same-host proxy has only over loopback.", "components": ["ollama"], "sources": ["ollama:s96f77aee8bdd", "ollama:s3f66206086dd", "ollama:see893978ecc6", "ollama:s141dcff0708a", "ollama:s8ab7a3732a2c", "ollama:s17e93913af2b", "ollama:s848cbf05de34"], "status": "REASONED"},
    "file-validation": {"text": "Create validates relative filenames and blob paths; arbitrary host-file access is not established at this pin.", "components": ["ollama"], "sources": ["ollama:s01c0c71afa78", "ollama:s1ded6de8ebe0"], "status": "REASONED"},
    "transfer": {"text": "Management transfers are egress/disk-fill surfaces; insecure alters redirect protections, without demonstrating unrestricted SSRF.", "components": ["ollama", "commit"], "sources": ["ollama:s8b9d4257c3df", "commit:s673919ab300f"], "status": "REASONED"},
    "origins": {"text": "OLLAMA_ORIGINS adds to built-in origins; removing wildcards is neither authentication nor an exclusive-origin policy.", "components": ["ollama"], "sources": ["ollama:s2abe15b73bce"], "status": "REASONED"},
    "service-user": {"text": "Use a dedicated account and writable store; preserve GPU access and do not assume the container shares installer identity.", "components": ["ollama"], "sources": ["ollama:s453c95c884da", "ollama:s52649b124738"], "status": "REASONED"},
    "store": {"text": "Proposed 0700 directories, 0600 files and UMask=0077 need existing-permission/ACL inspection; separate service configuration and proxy keys.", "components": ["ollama", "systemd"], "sources": ["ollama:s453c95c884da", "systemd:sd4c1aeb45417"], "status": "REASONED"},
    "model-path": {"text": "OLLAMA_MODELS relocates models, not the entire service home or signing keys.", "components": ["ollama"], "sources": ["ollama:s2abe15b73bce", "ollama:s453c95c884da"], "status": "REASONED"},
    "loaded-models": {"text": "Loaded-model capacity is automatic unless configured; the example selects one model, not a total memory cap.", "components": ["ollama"], "sources": ["ollama:s2abe15b73bce", "ollama:s27e1a359c744"], "status": "REASONED"},
    "parallel": {"text": "OLLAMA_NUM_PARALLEL defaults to 1.", "components": ["ollama"], "sources": ["ollama:s2abe15b73bce", "ollama:s27e1a359c744"], "status": "REASONED"},
    "queue": {"text": "OLLAMA_MAX_QUEUE defaults to 512; the example selects 16 without promising the seventeenth HTTP request is refused.", "components": ["ollama"], "sources": ["ollama:s2abe15b73bce", "ollama:s27e1a359c744"], "status": "REASONED"},
    "keep-alive": {"text": "Keep-alive defaults to five minutes; one minute is the example, and requests can override it.", "components": ["ollama"], "sources": ["ollama:s2abe15b73bce", "ollama:sfb778cd7de39"], "status": "REASONED"},
    "context": {"text": "Context defaults are VRAM-dependent 4K/32K/256K; implementation thresholds are roughly 23/47 GiB after overhead versus nominal 24/48 GiB.", "components": ["ollama"], "sources": ["ollama:s4112a1bdf03c", "ollama:s96f77aee8bdd"], "status": "REASONED"},
    "rate": {"text": "Example nginx source-address rate is 2r/s, burst 4 nodelay, with 429 responses; trusted client-address handling matters behind proxies.", "components": ["nginx"], "sources": ["nginx:sb3bee9429629"], "status": "REASONED"},
    "concurrency": {"text": "Example nginx server-name budget is four active requests with 429; it does not cap every idle/incomplete connection.", "components": ["nginx"], "sources": ["nginx:sddc43aac8779"], "status": "REASONED"},
    "body-limit": {"text": "Example body cap is 1 MiB; a larger valid fixture should get 413 without upstream work.", "components": ["nginx"], "sources": ["nginx:s40bdf1af1596"], "status": "REASONED", "verify": [3]},
    "parameters": {"text": "Gateway must validate model, num_ctx, num_predict and keep_alive; defaults/path allowlists do not enforce JSON ceilings.", "components": ["ollama"], "sources": ["ollama:sbca403d10498", "ollama:sfb778cd7de39"], "status": "REASONED", "verify": [3]},
    "registry-names": {"text": "Fully qualified registry names are supported; unqualified names select Ollama's registry and omitted tags select latest.", "components": ["ollama"], "sources": ["ollama:sa8c4675db386"], "status": "REASONED"},
    "provenance": {"text": "Compare deployed tags digests with independent approval; mutable tags/digest equality do not establish publisher trust.", "components": ["ollama", "ollama-rolling"], "sources": ["ollama-rolling:s6c2961786919", "ollama:sa8c4675db386"], "status": "REASONED", "verify": [3]},
    "local-import": {"text": "CLI imports reviewed local GGUF through a Modelfile; artifact SHA-256 and manifest digest are different identifiers.", "components": ["ollama"], "sources": ["ollama:s14266d6e90ae", "ollama:s7478dad099ab"], "status": "REASONED", "verify": [3]},
    "registry-egress": {"text": "Restrict acquisition/export to administrators and constrain egress; compare approved and controlled disallowed transfers.", "components": ["ollama"], "sources": ["ollama:s8b9d4257c3df"], "status": "REASONED", "verify": [3]},
    "cloud": {"text": "OLLAMA_NO_CLOUD=1 disables cloud models and web search after restart; it is not a no-network switch.", "components": ["ollama"], "sources": ["ollama:sbca403d10498"], "status": "REASONED", "verify": [3]},
    "remotes": {"text": "OLLAMA_REMOTES selects remote-model hosts, not a registry allowlist.", "components": ["ollama"], "sources": ["ollama:s2abe15b73bce"], "status": "REASONED"},
    "diagnostics": {"text": "Keep root, version, status, tags, ps and show private; model details can disclose templates/system prompts.", "components": ["ollama", "ollama-rolling"], "sources": ["ollama:s96f77aee8bdd", "ollama-rolling:s528f69db04e0"], "status": "REASONED", "verify": [3]},
    "request-logs": {"text": "Disable OLLAMA_DEBUG and OLLAMA_DEBUG_LOG_REQUESTS; existing request captures/replay scripts need separate cleanup.", "components": ["ollama"], "sources": ["ollama:s2abe15b73bce", "ollama:sa89bd5d8e1f7"], "status": "REASONED", "verify": [3]},
    "profiling": {"text": "No metrics route was found in the main router; this guide assesses that first-party v0.34.2 code registers no pprof handler. Shipped-binary pprof availability remains unestablished: observe the binary, deny public profiling, infer nothing from debug settings.", "components": ["ollama"], "sources": ["ollama:s96f77aee8bdd", "ollama:s9bf8940c3001", "ollama:s8f4e8b651967", "ollama:sc16932a1056b", "ollama:s3db39cecc705", "ollama:s8a310972e31d", "ollama:s5a188d13a009", "ollama:s0b381e62597c", "ollama:sa340a3deada2", "ollama:sbf4266cc6ffa", "ollama:sce8e789d8d24", "ollama:s4ded5c727f27", "ollama:sc0d5747ba398"], "status": "REASONED", "verify": [3]},
    "profiling-scope": {"text": "Go 1.26.5 go list runs for this guide found neither net/http/pprof nor runtime/pprof in the default-tag v0.34.2 main-package graph for every go tool dist list pair that loaded, cgo off and, where supported, on; five cgo-off android and ios runs failed. This guide infers no go.sum dependency adds either; Go outside 1.26.x, standard-library imports, those runs and served-mux exposure stay open.", "components": ["ollama", "trifles", "compress", "x-text"], "sources": ["ollama:s9bf8940c3001", "ollama:s5a188d13a009", "ollama:s0b381e62597c", "ollama:sfc02278c501f", "trifles:s38ad5e627932", "trifles:seeae3b9d9459", "trifles:s56182db1ad94", "trifles:s4e12f43a1afe", "trifles:s6a11f78133a6", "trifles:s82d128642faa", "trifles:s53fe5b36bae7", "compress:sd309de5a57e2", "x-text:s7b232c7ac531"], "status": "REASONED", "verify": [3]},
    "profiling-tags": {"text": "From source reading, v0.34.2's first-party custom tags integration, fast, generate, release, library and updater_live gate only _test.go files, which go build ignores; appengine and os400 appear only in readline/term.go, importing only syscall. The dependency search ignored build constraints, so which dependency files these tags select was not determined; go list runs show generate selects one.", "components": ["ollama", "go"], "sources": ["ollama:s9bf8940c3001", "ollama:s98a6abaa3838", "ollama:s9a29ad2cbe09", "ollama:s748c551a2a08", "ollama:sd7c08f30e61e", "ollama:s720db4671dfd", "go:s7f4cde22e030"], "status": "REASONED", "verify": [3]},
    "profiling-tag-runs": {"text": "Go 1.26.5 go list runs for this guide found neither net/http/pprof nor runtime/pprof in the v0.34.2 main-package graph with tag set updater_live, release,library, appengine, os400 or appengine,os400 on the eight first-class pairs, windows arm64 and aix ppc64, cgo off and on. This guide infers no first-party or go.sum module file adds either; standard-library imports and Go outside 1.26.x are open.", "components": ["ollama", "go", "trifles", "compress", "x-text"], "sources": ["ollama:s9bf8940c3001", "ollama:s720db4671dfd", "go:sdba7b87fda8d", "ollama:sfc02278c501f", "trifles:s38ad5e627932", "trifles:seeae3b9d9459", "trifles:s56182db1ad94", "trifles:s4e12f43a1afe", "trifles:s6a11f78133a6", "trifles:s82d128642faa", "trifles:s53fe5b36bae7", "compress:sd309de5a57e2", "x-text:s7b232c7ac531"], "status": "REASONED", "verify": [3]},
    "profiling-generate": {"text": "Go 1.26.5 go list runs for v0.34.2 with tag sets containing generate failed on all ten pairs tried, cgo off and on, reporting both uniseg and main packages in dependency github.com/rivo/uniseg v0.4.7; -e reruns listed neither pprof package but marked that package with a load error, so whether such builds import either remains open.", "components": ["ollama", "go"], "sources": ["ollama:s9bf8940c3001", "go:sdba7b87fda8d"], "status": "REASONED"},
    "profiling-go-versions": {"text": "Source reading, not run: Go 1.26.0 to 1.26.10 except 1.26.5 match 1.26.5: goversion is 26; ignoring build constraints, only net/http/pprof, testing/internal/testdeps and a package main command import runtime/pprof in non-test files outside cmd. No file imports the first two. This guide infers no such release adds either package to the 1.26.5 go list graphs; no graph was checked.", "components": ["go-1-26-0", "go-1-26-1", "go-1-26-2", "go-1-26-3", "go-1-26-4", "go-1-26-6", "go-1-26-7", "go-1-26-8", "go-1-26-9", "go-1-26-10", "go"], "sources": ["go-1-26-0:s7670be382fd6", "go-1-26-0:sc4d5a418cc8a", "go-1-26-0:s63f63360f142", "go-1-26-0:se924f730cd16", "go-1-26-1:sc2735a74234b", "go-1-26-1:sd0122b4596e5", "go-1-26-1:sa24dcdd9e52c", "go-1-26-1:s2a55e411da1d", "go-1-26-2:sa8ba29c45871", "go-1-26-2:s058a974ee5d5", "go-1-26-2:s019e0fb220fc", "go-1-26-2:s8a4dc2d3db9b", "go-1-26-3:sdc07d97a87b6", "go-1-26-3:sed7ba616e62c", "go-1-26-3:s040d1ea399ae", "go-1-26-3:s898567a72486", "go-1-26-4:s2fd10ac9b790", "go-1-26-4:s860b46eaab36", "go-1-26-4:s2104c8373c85", "go-1-26-4:s0e9e578b8243", "go-1-26-6:s8b8ebc7e8db6", "go-1-26-6:sb1475154fbb7", "go-1-26-6:s974c60526bb6", "go-1-26-6:s52851e8b4312", "go-1-26-7:s17ad8bf46090", "go-1-26-7:s54141d62f948", "go-1-26-7:sf081388dd0f7", "go-1-26-7:s64e2db3b685b", "go-1-26-8:s6175e03794cf", "go-1-26-8:s88d4166a7bee", "go-1-26-8:sa79ec4182285", "go-1-26-8:s9ad74046b534", "go-1-26-9:s69637c613830", "go-1-26-9:s71887e5f7cdf", "go-1-26-9:s6728c0a5d0d1", "go-1-26-9:s110ef73adaf3", "go-1-26-10:scff07ded2fad", "go-1-26-10:sd61f4ff8d5d6", "go-1-26-10:s9b82f1629b4d", "go-1-26-10:s599b4645909f", "go:s0388b420c217", "go:s41262ad87b65", "go:s80e5cbbd9e14", "go:s63df9d2be607"], "status": "REASONED"},
    "profiling-deps-scan": {"text": "From source reading, ignoring build constraints, only package main files in the 93 dependency modules with go.sum zip hashes import net/http/pprof or runtime/pprof. Imports followed from first-party packages stay in those modules and the unread standard library, so this guide infers no such module adds either at those versions. The 15 cached modules with no go.sum zip hash were excluded.", "components": ["ollama", "trifles", "compress", "x-text", "go-toml"], "sources": ["ollama:s9bf8940c3001", "ollama:s2422d51c7511", "ollama:sc8a033a390da", "ollama:sfc02278c501f", "trifles:s38ad5e627932", "trifles:seeae3b9d9459", "trifles:s56182db1ad94", "trifles:s4e12f43a1afe", "trifles:s6a11f78133a6", "trifles:s82d128642faa", "trifles:s53fe5b36bae7", "trifles:s3c8772bb591f", "compress:sd309de5a57e2", "x-text:s7b232c7ac531", "go-toml:s263bb2467c05", "go-toml:sf307292d806f"], "status": "REASONED"},
    "profiling-mux": {"text": "This guide's inference, not run: Go 1.26.5 net/http/pprof's init registers /debug/pprof/ handlers on http.DefaultServeMux, which a server with a nil Handler, as in v0.34.2's Serve, uses, so a build linking that package would serve them on the Ollama listener, while builds whose go list graph lacks it get none from it.", "components": ["go", "ollama"], "sources": ["go:sab55ef9009c4", "go:s2e779f75153e", "go:s038b2186ee21", "go:sa0c56e16001f", "ollama:s0b381e62597c", "ollama:sa340a3deada2"], "status": "REASONED", "verify": [3]},
    "profiling-release": {"text": "From this guide's reading of v0.34.2's Dockerfile, build scripts and release workflow, which show intended builds rather than artifact contents, the main package is built with no -tags, and with CGO_ENABLED=1 in the Dockerfile, the darwin build and both Windows CLI builds. The go.mod declares go 1.26.0, which the Dockerfile uses to choose Go, while this guide's go list runs used Go 1.26.5.", "components": ["ollama"], "sources": ["ollama:s2422d51c7511", "ollama:sc2b36fe862cd", "ollama:s048a8041e459", "ollama:s69d878a2f01f", "ollama:saffcf6c517dc", "ollama:sfbdb6f7a76af", "ollama:s0c28c94bb1ee", "ollama:sdc9725a324a3", "ollama:s50dc1a212bc5", "ollama:s2c83e3be00ef", "ollama:s383b8a85907a", "ollama:sdf3692260fb9", "ollama:s73deff2c03e1", "ollama:s99ff5d94d99e", "ollama:s3d177b1fcaf1", "ollama:s54c3a8422a93", "ollama:s83f85bf889db", "ollama:sae92e96027b1"], "status": "REASONED"},
    "profiling-app-runs": {"text": "Go 1.26.5 go list -e -deps runs for this guide list no net/http/pprof or runtime/pprof for the v0.34.2 desktop app main package on darwin/windows amd64 and arm64, cgo off and on; linux lists only the error-marked main package. Loaded cells mark app/ui (no app/dist); cgo-off cells cannot load cgo-only app/webview and omit the main package's cgo files with no error, so imports may be incomplete.", "components": ["ollama"], "sources": ["ollama:sad61f21372d7", "ollama:sf38afcc73250", "ollama:s45897fae891f", "ollama:s2b2be911f51e", "ollama:se6c615cc2b3a"], "status": "REASONED"},
    "profiling-app-listener": {"text": "From source reading, the app's UI listener is loopback (127.0.0.1:0, or 3001 in dev mode), served by an http.Server with a non-nil Handler whose mux has a token-cookie check on /api/v1 routes, proxy and catch-all routes without it, and no /debug/pprof pattern. This guide's inference, not run: even a build linking net/http/pprof would not serve DefaultServeMux handlers there.", "components": ["ollama", "go"], "sources": ["ollama:s73b81a1f8d04", "ollama:s67fd6cba9588", "ollama:s243bac4ebddb", "ollama:s4421d53f8855", "go:sab55ef9009c4", "go:s2e779f75153e", "go:s038b2186ee21", "go:sa0c56e16001f"], "status": "REASONED"},
    "profiling-app-gateway": {"text": "From source reading, another loopback app listener is the Claude Desktop gateway on 127.0.0.1:11435, in macOS cgo builds, started only when Claude Desktop is installed. Its non-nil Handler refuses non-loopback Host values and a non-empty first Origin, serves four routes, not /debug/pprof, and forwards only POST /v1/messages, stripping caller auth headers, to the app's OLLAMA_HOST; not run.", "components": ["ollama", "go"], "sources": ["ollama:s2b2be911f51e", "ollama:s84f1c8cf636d", "ollama:sba33d5d074d0", "ollama:sb8e91213cc53", "ollama:s132b1b4bbbe5", "ollama:s58d1846a87f0", "ollama:s8b3afc8d9f86", "ollama:s5897f909de84", "ollama:saf6c2bd158fc", "ollama:s4100d1423b14", "ollama:s4b2897a4f253", "ollama:s11e3644384be", "ollama:s6a1dfd450763", "ollama:s6cab16cc1556", "ollama:s99dbaec1750f", "go:s7290caae7a3c"], "status": "REASONED"},
    "profiling-app-gateway-start": {"text": "Source reading, not run: startup starts the gateway only if Claude Desktop is installed and configured to use it; setClaudeGatewayInstalled, prepareClaudeDesktopConnection and model mapping start it if installed. The first two stop it unless Claude Desktop then uses it (the first not after an auto-mode error); mapping, if none existed, stops it on profile-change errors except restart confirmation.", "components": ["ollama"], "sources": ["ollama:sd92431ef4485", "ollama:sb5822b8eeabd", "ollama:se1879bd92d00", "ollama:s9a2533a8e3e0", "ollama:s29f084ce74cf", "ollama:sb8e91213cc53", "ollama:sd1743f37dd2c", "ollama:s8b982a956f29"], "status": "REASONED"},
    "profiling-app-release": {"text": "By this guide's reading of intended builds, not artifacts, build_darwin.sh builds the app package with GOOS=darwin, CGO_ENABLED=1, amd64 and arm64 and no -tags. In build_windows.ps1, buildApp builds it with no -tags, by default setting no GOARCH under its unconditional CGO_ENABLED=1 and, when the cross-compile tools are present, for arm64 (GOOS=windows, GOARCH=arm64, CGO_ENABLED=1).", "components": ["ollama"], "sources": ["ollama:s46dc00636dd6", "ollama:sde507d86d7ac", "ollama:s52f3436c9021", "ollama:s0c28c94bb1ee", "ollama:sdc9725a324a3", "ollama:saffcf6c517dc"], "status": "REASONED"},
    "desktop-app-server": {"text": "From source reading, the desktop app serves no HTTP on the Ollama API listener itself: it runs the separate ollama binary with serve and restarts it, and the spawn copies the app's own environment, setting OLLAMA_HOST=0.0.0.0 when the Expose setting is on, so that setting or an inherited OLLAMA_HOST can expose that process. No shipped app binary was inspected and no run observed these behaviours.", "components": ["ollama"], "sources": ["ollama:sa4c68b27021b", "ollama:sd5ce93133b59", "ollama:s80b241b854c7"], "status": "REASONED"},
    "verify-inventory": {"text": "Inspect namespaces, publication, identity, store and ACLs; local ss output alone does not establish isolation.", "components": ["ollama", "docker", "systemd"], "sources": ["ollama:s453c95c884da", "docker:s1e53417c513d", "systemd:sd4c1aeb45417"], "status": "REASONED", "verify": [1]},
    "verify-bypass": {"text": "HTTP means direct 11434 answered; fixed refusal needs the real remote path plus successful proxy inference; local errors are inconclusive.", "components": ["ollama", "curl"], "sources": ["ollama:sbca403d10498", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [2]},
    "verify-auth": {"text": "Absent/wrong credentials must refuse while correct credentials complete chat; streamed 200 alone is insufficient.", "components": ["nginx", "ollama", "curl"], "sources": ["nginx:sf32ce2956917", "ollama:s96f77aee8bdd", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [3]},
    "verify-tls": {"text": "Correct trust/hostname succeeds; wrong trust/hostname and missing/untrusted mTLS certificates must fail before inference.", "components": ["nginx", "curl"], "sources": ["nginx:sda4ba3fcedbe", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [3]},
    "verify-management": {"text": "Public management must be denied without upstream mutation; private admin operations and public chat supply positive controls.", "components": ["ollama"], "sources": ["ollama:s8379cd00dbf9", "ollama:s96f77aee8bdd", "ollama:s01c0c71afa78"], "status": "REASONED", "verify": [3]},
    "verify-tags": {"text": "Public tags may return 404 with valid credentials; private tags should return model JSON; public 404 is not an authentication test.", "components": ["nginx", "ollama-rolling"], "sources": ["ollama-rolling:s6c2961786919", "nginx:s40bdf1af1596"], "status": "REASONED", "verify": [3]},
    "verify-origins": {"text": "Compare unwanted, required and built-in origins with actual browser calls; POST-only proxy preflight refusals differ by variant.", "components": ["ollama", "nginx", "caddy"], "sources": ["ollama:s2abe15b73bce", "nginx:s40bdf1af1596", "nginx:sf0bc2adae8cb", "caddy:s38b1b78ce980"], "status": "REASONED", "verify": [3]},
    "verify-rate": {"text": "Eight bounded requests test admission with limiter/upstream evidence and recovery; the burst alone does not demonstrate both limiters.", "components": ["nginx"], "sources": ["nginx:sb3bee9429629", "nginx:sddc43aac8779"], "status": "REASONED", "verify": [4]},
    "verify-concurrency": {"text": "Hold four accepted requests active within the rate budget, reject another, then confirm a freed slot accepts work.", "components": ["nginx"], "sources": ["nginx:sddc43aac8779"], "status": "REASONED", "verify": [3]},
    "verify-scheduler": {"text": "Compare loading/eviction, keep-alive expiry and actual queue occupancy; public limits can prevent exercising the private queue.", "components": ["ollama"], "sources": ["ollama:s27e1a359c744", "ollama:s2abe15b73bce"], "status": "REASONED", "verify": [3]},
    "verify-cloud": {"text": "Authorized cloud chat works before disablement and refuses afterward while local chat succeeds; invalid credentials/models are inconclusive.", "components": ["ollama"], "sources": ["ollama:sbca403d10498"], "status": "REASONED", "verify": [3]},
    "verify-captures": {"text": "Compare completed canary requests with logging enabled/disabled in the actual temporary namespace; deny public diagnostics while private controls work.", "components": ["ollama"], "sources": ["ollama:sa89bd5d8e1f7", "ollama:s96f77aee8bdd"], "status": "REASONED", "verify": [3]},
    "proxy-parsing": {"text": "nginx -t and caddy validate check configuration acceptance only; native parsing was not demonstrated here.", "components": ["nginx", "caddy"], "sources": ["nginx:sa28876996ece", "caddy:sc5832c7dc52f"], "status": "REASONED"},
    "curl-version": {"text": "Displayed exitcode and errormsg write-out variables need curl 7.75.0 or later; no tested curl release is recorded.", "components": ["curl"], "sources": ["curl:s2b2686afaf41"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
