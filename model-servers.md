# Model servers: llama.cpp, vLLM, TGI, SGLang, Triton, and LM Studio

Self-hosted model servers follow the [ollama.md](ollama.md) pattern: exposing one means someone else's prompts run on your GPU. Most default to local use, but vLLM, TGI, and Triton bind to `0.0.0.0` out of the box, and Triton enables no authentication by default (its native controls, gRPC mutual TLS and shared-secret restricted APIs, do not replace the gateway). Keep every server on loopback or a private network, require an API key where the server supports one, and terminate TLS in front. LocalAI is an OpenAI-compatible model server too, but its bind and authentication controls are documented in [ai-infra-services.md](ai-infra-services.md) rather than here, so the facts live in one place.

## llama.cpp (llama-server)

`llama-server` listens on `127.0.0.1:8080` by default; keep that bind. Require a key:

```bash
llama-server -m model.gguf --api-key "${LLAMA_API_KEY:?set a non-empty API key}"
# --api-key accepts a comma-separated list for multiple keys
```

Use a real generated key ([authentication.md](authentication.md)): the `${LLAMA_API_KEY:?...}` above stops the launch on an unset or empty value, but llama.cpp still discards a comma-only value or CSV fields that decode to empty (a literal `""`) and then starts unauthenticated, so confirm the key is enforced by probing the llama.cpp backend DIRECTLY on its own host and port from the trusted network (not through the proxy, which returns its own 401/200 regardless): a no-key request must be refused there and a keyed request accepted.

Native TLS exists when the binary is built with OpenSSL (`-DLLAMA_OPENSSL=ON`): `--ssl-key-file` and `--ssl-cert-file` take PEM files ([self-signed.md](self-signed.md) or [free-certificates.md](free-certificates.md)). A reverse proxy per [nginx.md](nginx.md)/[caddy.md](caddy.md) is the alternative when your build lacks SSL support.

## vLLM (OpenAI-compatible server)

vLLM's server supports requiring an API key; check `vllm serve --help` on your installed version for the current option name (the docs at https://docs.vllm.ai/ document it; this guide avoids pinning the flag because vLLM's CLI moves quickly). The key does not cover the whole server. vLLM's own security page states that it authenticates only the `/v1`, `/v2`, and `/inference` path prefixes, and lists `/invocations`, the SageMaker-compatible route, as requiring no key while reaching the same inference capability as the protected `/v1` routes; the profiler routes `/start_profile` and `/stop_profile` are likewise unauthenticated, and a plugin route outside those prefixes is unauthenticated unless the plugin enforces its own check. vLLM says plainly not to rely on the key alone. Allowlist only the routes your application needs at the proxy and refuse everything else there, `/invocations` included, rather than assuming the key covers the surface. vLLM binds every interface by default: `vllm serve` leaves `--host` unset, which listens on `0.0.0.0` (the startup log shows `http://0.0.0.0:8000`), so pass `--host 127.0.0.1` to keep it on loopback. vLLM can terminate TLS natively (`--ssl-keyfile`, `--ssl-certfile`, and `--ssl-ca-certs`, passed through to uvicorn), but fronting it with a TLS proxy or tunnel is the recommended pattern; either way keep the server itself on loopback or a private network.

## Hugging Face Text Generation Inference (TGI)

`text-generation-launcher` listens on `0.0.0.0:3000` by default (`--hostname`, env `HOSTNAME`; `--port`, env `PORT`), so a bare TGI container answers on every interface. Bind it to loopback, or publish nothing from the container network except the proxy:

Lifecycle note, as of September 2026: the TGI repository is in maintenance mode and was archived on 2026-03-21 (read-only). Hugging Face recommends vLLM, SGLang, or local engines such as llama.cpp going forward. A server that no longer receives fixes belongs behind the same controls as any other, and on a migration list.

```bash
text-generation-launcher --model-id REPLACE_WITH_MODEL_ID --hostname 127.0.0.1 --port 3000
```

The launcher reference lists `--api-key` (env `API_KEY`) without describing it. The router source shows what it does: when set, requests to the standard inference `base_routes` must carry a matching `Authorization: Bearer <key>` header or receive 401, while the health, info, and metrics routes stay unauthenticated. Builds that enable the KServe (`/v2/...`) endpoints register them outside that key middleware, `/v1/models` sits outside it too, and the Vertex feature route configured through `AIP_PREDICT_ROUTE` is registered after the auth layer as well, so those paths are unauthenticated; allowlist the routes you use and enforce the bearer check at the proxy. Treat it as a second layer and enforce the bearer check at the proxy too (pattern in [ollama.md](ollama.md)). The launcher has no TLS option, so front TGI per [nginx.md](nginx.md)/[caddy.md](caddy.md). The Prometheus listener (`--prometheus-port`, default 9000) is unauthenticated as well; keep it private.

## SGLang

`python -m sglang.launch_server` listens on `127.0.0.1:30000` by default (`--host`, `--port`); keep that bind. `--api-key` sets the key the OpenAI-compatible endpoints require, and `--admin-api-key` separately protects administrative endpoints (weight updates, cache flush, `/server_info`), which then require `Authorization: Bearer <admin key>`:

```bash
python -m sglang.launch_server --model-path REPLACE_WITH_MODEL_PATH --api-key "${SGLANG_API_KEY:?set a non-empty API key}" --admin-api-key "${SGLANG_ADMIN_KEY:?set a non-empty admin key}"
```

Use a real non-empty API key: SGLang serves ordinary requests whenever `--api-key` is empty, even when `--admin-api-key` is set, so an empty value leaves the OpenAI-compatible endpoints open.

Native TLS exists: `--ssl-keyfile` and `--ssl-certfile` take PEM files ([self-signed.md](self-signed.md) or [free-certificates.md](free-certificates.md)), `--ssl-ca-certs` names a CA bundle, and `--enable-ssl-refresh` hot-reloads renewed certificates. A reverse proxy remains the simpler choice when you already run one.

## NVIDIA Triton Inference Server

`tritonserver` starts three listeners on `0.0.0.0`: HTTP on 8000, gRPC on 8001, and Prometheus metrics on 8002. No authentication is enabled by default: its optional gRPC mutual TLS and restricted-API shared secrets can cover inference as well as model control, but do not replace the gateway. NVIDIA's secure deployment guidance is that Triton is a microservice that is "not exposed directly to an untrusted network": a dedicated gateway or proxy (NGINX, Envoy, Istio, Kong are the examples given) handles authorization, access control, and encryption, and Triton "handles only trusted, validated requests". Bind each listener privately and disable the protocols you do not use:

```bash
tritonserver --model-repository=/models --http-address=127.0.0.1 --grpc-address=127.0.0.1 --metrics-address=127.0.0.1
```

`--allow-http` and `--allow-grpc` default to true; NVIDIA recommends setting either to false when not required, and `--allow-metrics` switches off the metrics listener. For gRPC, `--grpc-use-ssl` with `--grpc-server-cert` and `--grpc-server-key` enables a TLS channel, and `--grpc-use-ssl-mutual` requires client certificates. HTTP has no TLS option; the proxy provides it. `--http-restricted-api` and `--grpc-restricted-protocol` fence the model-control APIs behind a shared-secret header, a useful second layer but not a substitute for the gateway. Builds with cloud endpoints add conditional listeners beyond these three: `AIP_MODE=PREDICTION` enables a Vertex AI endpoint (its port is `AIP_HTTP_PORT`, otherwise 8080), and a SageMaker endpoint may also be present, so disable the ones you do not use or add them to the bind inventory and the checks below.

## LM Studio (local server)

LM Studio's developer server is a desktop feature. The documentation addresses it at `http://localhost:1234` throughout (the port is a field in Developers Page > Server Settings), and "By default, LM Studio does not require authentication for API requests." The "Serve on Local Network" switch (or `lms server start --bind 0.0.0.0`) rebinds it to every interface; LM Studio's own note reads: "Any bind other than 127.0.0.1 exposes the server beyond localhost; we recommend enabling authentication." Leave that switch off. If another machine must reach it, first enable "Require Authentication" (LM Studio 0.4.0 or newer) and create a token under "Manage Tokens"; clients then send `Authorization: Bearer <token>`. The server settings list no TLS option, so anything beyond the local machine goes through a tailnet ([tailscale.md](tailscale.md)) or an authenticated TLS proxy, never a port-forward.

## text-generation-webui

One process, two surfaces: the Gradio UI (default `127.0.0.1:7860`) and, when started with `--api`, an OpenAI-compatible API (default `127.0.0.1:5000`, endpoints under `/v1`). Both default to loopback, and both start with no authentication.

`--listen` rebinds to `0.0.0.0`, and it widens both surfaces at once: opening the UI to your LAN also opens the API port whenever `--api` is set. `--listen-port` moves the UI port, `--api-port` moves the API port, and `--listen-host` picks a specific bind address instead of `0.0.0.0`; like the wider binding itself it takes effect only with `--listen`, and on its own it does nothing. Never start an internet-adjacent instance with `--share`: it publishes the UI through a public `*.gradio.live` tunnel, reachable by anyone who has the URL. `--public-api` does the same for the API through a Cloudflare tunnel. Treat both flags as publishing, not as remote access.

Auth is per surface, and neither control covers the other:

- UI: `--gradio-auth user:password` (or `--gradio-auth-path FILE` with `user:password` lines) turns on a Gradio login form. It does nothing for the API.
- API: `--api-key KEY` requires `Authorization: Bearer KEY` on the OpenAI-compatible routes such as `/v1/models` and `/v1/chat/completions`; the Anthropic-compatible `/v1/messages` route reads the same key from an `x-api-key` header instead. `--admin-key` guards the admin endpoints (model load and unload) and falls back to the `--api-key` value when unset; an admin key alone does not protect the ordinary routes. Without `--api-key`, the API answers anyone who can reach the port, even when the UI has a Gradio login in front of it. Starting the API logs the configured `--api-key` (and any distinct `--admin-key`) to stdout and the service log verbatim, so protect that output and rotate the key after any disclosure.

`--api --nowebui` runs the API alone, the right shape for a server where the UI has no business existing. `--ssl-keyfile` and `--ssl-certfile` give both surfaces TLS, but the better pattern is the usual one: keep both ports on loopback and front them with a reverse proxy that terminates TLS and enforces auth (`--subpath` exists for serving the UI under a proxy path). Without TLS, the Gradio login submits credentials in the clear.

One proxy detail is specific to this API: unless `--listen` (or `--public-api`) is set, it rejects any request whose `Host` header is not `localhost` or `127.0.0.1` with a `400`, so a reverse proxy in front of a loopback API must send `Host: localhost` upstream rather than forwarding the public hostname.

## The pattern, whatever the server

1. Bind to `127.0.0.1` (or a private container network); confirm with `ss -tlnp`.
2. Require a per-client API key at the server where supported, or at the proxy otherwise (bearer-token check per [ollama.md](ollama.md)); generate keys per [authentication.md](authentication.md).
3. TLS in front: [caddy.md](caddy.md), [nginx.md](nginx.md), [cloudflare.md](cloudflare.md), or [tailscale.md](tailscale.md).
4. Human-facing UIs on top of these servers ([open-webui.md](open-webui.md)) carry their own login and MFA ([mfa.md](mfa.md)).

## Verify

```bash
ss -tlnp   # every listener; 8080/8000/8001/8002/3000/9000/30000/5000/7860/1234. ss shows only a
           # namespace-local BIND, not a host firewall, a cloud security group, or Docker -p NAT
           # publication. From another host, probe EACH backend listener's own host and port (adapt the
           # subshell below, which shows the technique for one endpoint) and confirm each is refused
(
  # Feed the API key to curl on stdin (curl --header @-), never in argv:
  # -H "Authorization: Bearer KEY" is readable in ps / /proc/<pid>/cmdline.
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_API_KEY'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the API key on the set -- line above; not probing"; exit ;; esac
  curl -q -sS --noproxy '*' -w 'http=%{http_code} exit=%{exitcode}\n' https://models.example.com/v1/models   # PROXY-policy test: 401 without a key. TGI leaves /v1/models outside its native key middleware, so a 200 is not proof the backend enforces the key
  printf 'Authorization: Bearer %s\n' "$1" | curl -q -sS --noproxy '*' -w 'http=%{http_code} exit=%{exitcode}\n' -H @- https://models.example.com/v1/models   # positive control: 200 with a model list, printed
)
(
  set -- REPLACE_WITH_A_REAL_SERVED_MODEL
  case "$1" in ""|*REPLACE_WITH_*) echo 'substitute a real served model name on the set -- line above; not probing'; exit 2 ;; esac
  curl -q -sS --noproxy '*' -D - -o invocations-body.txt -w 'http=%{http_code}\n' -X POST -H 'Content-Type: application/json' \
    -d "{\"model\":\"$1\",\"messages\":[{\"role\":\"user\",\"content\":\"ping\"}]}" https://models.example.com/invocations
)
                                                        # vLLM /invocations needs JSON (a bare -d '{}' sends form
                                                        # content-type and fails the schema) and a REAL served model.
                                                        # Read the printed headers and saved body, not the status alone: an
                                                        # exposed vLLM given an unknown model also returns 404, so
                                                        # http=404 is AMBIGUOUS with the proxy's own denial. A
                                                        # vLLM-originated reply (200, or a JSON error body) means the
                                                        # route is reachable without the key; a 403/404 only proves
                                                        # denial if the PROXY rejected BEFORE forwarding (its route config
                                                        # or correlated upstream/backend logs) - a proxy that intercepts an
                                                        # upstream error (nginx proxy_intercept_errors) serves its own page
                                                        # while the no-key request reached vLLM, which is reachability, not
                                                        # denial. Treat anything ambiguous as inconclusive
```

For text-generation-webui, ask the API edge for the model list without a key. This step is reasoned, not demonstrated: the authoring environment has no container runtime to stand up a live instance, so the expected `401` is derived from the bearer-token check in `modules/api/script.py` (cited in Sources), not observed, and backlog row 1.50 tracks demonstrating the exposed and protected states. The block prints the `exitcode` and `errormsg` write-out variables, which need curl 7.75.0 or newer. A `200` with a model list means the API is open to anyone; a `401` means the key is enforced. A transfer error is inconclusive: a TLS failure (`exit=35` or `exit=60`) in particular means something did answer, since the API serves plain HTTP unless `--ssl-keyfile`/`--ssl-certfile` are set, so read the `exit` and `err` fields, fix any DNS, TLS, or client cause, and confirm the API listener's own address and port directly from the intended vantage. A `400` carrying `Invalid host header` is the API rejecting the forwarded `Host` (see the reverse-proxy note above), not an authentication result, and a rejection page from your proxy proves only the proxy.

```bash
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the host on the set -- line above; not probing" ;;
    *) curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
         -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "https://$1/v1/models" ;;
  esac
)
```

## Sources (checked September 2026)

- llama.cpp server README (defaults, --api-key, SSL flags): https://github.com/ggml-org/llama.cpp/blob/e0dff58475bc9ed68eedcb265ee998f2fcabb3b1/tools/server/README.md
- vLLM documentation: https://docs.vllm.ai/
- vLLM server host default (`FrontendArgs.host` defaults to `None`; checked 2026-09-14): https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/entrypoints/launchers/cli_args.py
- vLLM server socket bind (the launcher builds `(args.host or "", port)`, so an unset host binds every IPv4 interface, and renders the empty host as `0.0.0.0` in the startup log; checked 2026-09-14): https://github.com/vllm-project/vllm/blob/8c1557a79c539ffe82d004d2a0c8d7b5e71159ce/vllm/entrypoints/launchers/launcher.py
- vLLM security, API key authentication limitations (protected prefixes, unprotected `/invocations` and profiler routes): https://docs.vllm.ai/en/latest/usage/security/
- TGI launcher arguments (--hostname, --port, --api-key, --prometheus-port): https://huggingface.co/docs/text-generation-inference/reference/launcher
- TGI router source (what --api-key enforces): https://github.com/huggingface/text-generation-inference/blob/24ee40d143d8d046039f12f76940a85886cbe152/router/src/server.rs
- TGI repository (maintenance-mode notice, archived 2026-03-21): https://github.com/huggingface/text-generation-inference
- SGLang server arguments (--host, --port, --api-key, --admin-api-key, SSL flags; docs.sglang.ai redirects here): https://docs.sglang.io/docs/advanced_features/server_arguments
- Triton secure deployment considerations: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/customization_guide/deploy.html
- Triton quickstart (default listeners on 8000, 8001, 8002): https://github.com/triton-inference-server/server/blob/0194c3da9ddeeff07547f46aa058cf88acb51893/docs/getting_started/quickstart.md
- Triton inference protocols (gRPC SSL flags, restricted APIs): https://github.com/triton-inference-server/server/blob/c29bbe17eac256bbcd8fea47cde2f219d2be37cf/docs/customization_guide/inference_protocols.md
- Triton command line parser (address and port flags with defaults): https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc
- LM Studio local server: https://lmstudio.ai/docs/developer/core/server
- LM Studio serve on local network: https://lmstudio.ai/docs/developer/core/server/serve-on-network
- LM Studio server settings: https://lmstudio.ai/docs/developer/core/server/settings
- LM Studio authentication: https://lmstudio.ai/docs/developer/core/authentication
- LM Studio OpenAI compatibility (localhost:1234 examples): https://lmstudio.ai/docs/developer/openai-compat
- text-generation-webui README, command-line flags: https://github.com/oobabooga/text-generation-webui#command-line-flags
- text-generation-webui, OpenAI-compatible API documentation: https://github.com/oobabooga/text-generation-webui/blob/ceade2eb1ba3f84518076270df2240b6bbb01da0/docs/12%20-%20OpenAI%20API.md
- text-generation-webui, flag definitions and defaults (modules/shared.py): https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/modules/shared.py
- text-generation-webui, API bind and key checks (modules/api/script.py): https://github.com/oobabooga/text-generation-webui/blob/619a2b8ee4b7e48541a9be5c07e04cd31b91b44f/modules/api/script.py
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0): https://curl.se/docs/manpage.html
- SGLang `Serving` argument group: `host` default `127.0.0.1` and `port` default `30000` (pinned tag v0.5.20): https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/arg_groups/fields/serving.py#L72-L73
