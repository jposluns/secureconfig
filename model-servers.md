# Model servers: llama.cpp, vLLM, TGI, SGLang, Triton, and LM Studio

Self-hosted model servers follow the [ollama.md](ollama.md) pattern: exposing one means someone else's prompts run on your GPU. Most default to local use, but vLLM, TGI, and Triton bind to `0.0.0.0` out of the box, and Triton enables no authentication by default (its native controls, gRPC mutual TLS and shared-secret restricted APIs, do not replace the gateway). Keep every server on loopback or a private network, require an API key where the server supports one, and terminate TLS in front. LocalAI is an OpenAI-compatible model server too, but its bind and authentication controls are documented in [ai-infra-services.md](ai-infra-services.md) rather than here, so the facts live in one place.

## llama.cpp (llama-server)

`llama-server` listens on `127.0.0.1:8080` by default; keep that bind. Require a key, and hand it to the server in a file rather than on the command line: a key expanded into `--api-key` sits in argv, where `ps` and `/proc/<pid>/cmdline` show it to other local accounts for the server's whole lifetime, and quoting does not change that. At the pinned llama.cpp commit, `--api-key-file` reads the keys from a file, one per line, and the pinned README documents no stdin input for them. Create the file once, as the account that runs `llama-server`:

```bash
(
  set -eC
  umask 077
  mkdir -p -- "$HOME/.config/llama-server"
  chmod 700 -- "$HOME/.config/llama-server"
  if [ -e "$HOME/.config/llama-server/api-keys" ] || [ -L "$HOME/.config/llama-server/api-keys" ]; then
    echo 'api-keys already exists in ~/.config/llama-server; nothing written'; exit 2
  fi
  openssl rand -hex 32 > "$HOME/.config/llama-server/api-keys"
)
```

`umask 077` applies before anything is written, so the directory is created mode `0700` and the file mode `0600`. The block makes the directory mode `0700` first and then refuses when `api-keys` already exists in any form (a regular file, a FIFO, or a symlink, dangling or not), so running the block again cannot replace a key your clients already hold; `set -C` also refuses an existing regular file, and the explicit check handles the other forms. As with the other writers in this guide, these checks hold only in owner-only directories no other account can replace. If `openssl` fails, the block leaves an empty file behind: delete it before running the block again, and the launch block below refuses to start on it. The key goes from `openssl` straight into the file, so it never passes through a shell variable or a command line. Add one line per further client key; at the pinned commit a line that begins with `#` is a comment. Clients running as that account on this host can read the same file; give remote clients their copy through your secret store ([secrets.md](secrets.md)). The file holds the key in plaintext at rest, readable by that account, by root, and by any backup that copies it, so keep it and its backups out of source control.

Start the server from the file:

```bash
(
  { unset -n LLAMA_API_KEY LLAMA_ARG_API_KEY_FILE && unset -v LLAMA_API_KEY LLAMA_ARG_API_KEY_FILE; } 2>/dev/null ||
    { echo 'cannot clear LLAMA_API_KEY or LLAMA_ARG_API_KEY_FILE in this shell; not starting'; exit 2; }
  set -- "${!LLAMA_ARG_@}"
  [ "$#" -eq 0 ] || { printf 'LLAMA_ARG_* variables set in this shell:'; printf ' %s' "$@"; printf '; unset them first; not starting\n'; exit 2; }
  grep -q '^[^#[:space:]]' "$HOME/.config/llama-server/api-keys" ||
    { echo 'no key line in ~/.config/llama-server/api-keys; not starting'; exit 2; }
  llama-server -m model.gguf --api-key-file "$HOME/.config/llama-server/api-keys"
)
```

The pinned README also lists `LLAMA_API_KEY` as an environment input for `--api-key` and `LLAMA_ARG_API_KEY_FILE` for `--api-key-file`. The block clears both names first and refuses to start when it cannot (a readonly name in your shell), so an inherited value can neither become a key nor point the server at a different file. It then refuses to start while any other `LLAMA_ARG_*` variable is set in the calling shell, naming each: the pinned README gives most llama-server options an `LLAMA_ARG_*` environment input, `LLAMA_ARG_HOST` for `--host` among them, so an inherited one would start the server differently from what the block shows, on another interface included. Unset them, or start from a clean shell. A key passed through `LLAMA_API_KEY` would stay out of argv but remain readable through `/proc/<pid>/environ` by the same account and by root for the server's whole lifetime; the file avoids that channel.

The block refuses a file with no line that starts with a key character, so a file of blank lines and `#` comments alone is refused, but it cannot tell a real key from other text, and what llama-server does with a file that holds no key line was not checked at the pinned commit. Confirm the key is enforced by probing the llama.cpp backend DIRECTLY on its own host and port from the trusted network (not through the proxy, which returns its own 401/200 regardless): a no-key request must be refused there and a keyed request accepted.

Native TLS exists when the binary is built with OpenSSL (`-DLLAMA_OPENSSL=ON`): `--ssl-key-file` and `--ssl-cert-file` take PEM files ([self-signed.md](self-signed.md) or [free-certificates.md](free-certificates.md)). A reverse proxy per [nginx.md](nginx.md)/[caddy.md](caddy.md) is the alternative when your build lacks SSL support.

## vLLM (OpenAI-compatible server)

vLLM's server requires an API key when one is set: at both pinned commits `--api-key` sets it, and when that flag is unset the server falls back to the `VLLM_API_KEY` environment variable. Flags move between vLLM releases, so confirm `--api-key` and `--config` in `vllm serve --help` on your installed version. Do not put the key on the command line, where `ps` and `/proc/<pid>/cmdline` show it to other local accounts for the server's whole lifetime. At the pinned commits `--config` reads the server options from a YAML file inside the process, so put the key in a file only the account running vLLM can read. Create it once, as that account:

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set -eC +x +a
  umask 077
  mkdir -p -- "$HOME/.config/vllm"
  chmod 700 -- "$HOME/.config/vllm"
  if [ -e "$HOME/.config/vllm/server.yaml" ] || [ -L "$HOME/.config/vllm/server.yaml" ]; then
    echo 'server.yaml already exists in ~/.config/vllm; nothing written'; exit 2
  fi
  set -- "$(openssl rand -hex 32)"
  [ "${#1}" -eq 64 ] || { echo 'key generation failed; nothing written'; exit 2; }
  case "$1" in *[!0123456789abcdef]*) echo 'key generation failed; nothing written'; exit 2 ;; esac
  printf 'api-key: "%s"\n' "$1" > "$HOME/.config/vllm/server.yaml"
)
```

The block makes the directory mode `0700` first, then refuses, before it generates a key, when `server.yaml` already exists in any form (a regular file, a FIFO, or a symlink, dangling or not), so a rerun cannot replace a key your clients already hold. It writes nothing unless the generated key is 64 hex characters. `umask 077` creates the directory mode `0700` and the file mode `0600`, and `set -C` still refuses to overwrite an existing regular file. These checks run before the write, not atomically with it, so they hold only while no other account can replace the directory or any directory above it: run the block in owner-only directories you control, such as your own home directory, never under a path another account can write to. The key passes only through the subshell's positional parameters and the builtin `printf`, never a command line; the block clears inherited traps first because a DEBUG, RETURN or ERR trap from your shell could otherwise read it, and it assumes a clean shell. Start the server with only non-secret values on its command line, substituting your model inside the quotes, and do not add `--api-key` there, which would put the value back in argv:

```bash
(
  { unset -n VLLM_API_KEY VLLM_USE_RUST_FRONTEND && unset -v VLLM_API_KEY VLLM_USE_RUST_FRONTEND; } 2>/dev/null ||
    { echo 'cannot clear VLLM_API_KEY or VLLM_USE_RUST_FRONTEND in this shell; not starting'; exit 2; }
  grep -Eq '^api-key: "[0123456789abcdef]{64}"$' "$HOME/.config/vllm/server.yaml" ||
    { echo 'no generated api-key line in ~/.config/vllm/server.yaml; not starting'; exit 2; }
  vllm serve 'REPLACE_WITH_MODEL' --host 127.0.0.1 --config "$HOME/.config/vllm/server.yaml"
)
```

The launch block clears `VLLM_API_KEY` first and refuses to start when it cannot (a readonly name in your shell), so an inherited value cannot stand in for the key, and it refuses a file with no generated `api-key` line. It clears `VLLM_USE_RUST_FRONTEND` the same way, because with that opt-in set the pinned server starts a Rust frontend process and hands it the non-default arguments, `api_key` included, as a JSON `--args-json` value on that process's command line. Keep `--config` and the path as two words: the pinned parser expands the file only when `--config` is an argument of its own, and it accepts `--config=FILE` without reading the file, so that server would start with no key. `--host 127.0.0.1` stays on the command line because it is not secret. vLLM merges the file's values into its argument list inside the Python process, and API server processes it starts receive their arguments through Python's `spawn` pipe rather than a command line, so the key stays out of `/proc/<pid>/cmdline` and `ps`. The HTTP server's startup log prints the non-default arguments with `api_key` redacted, but `vllm serve --grpc` logs its whole argument set unredacted, the key included, so protect that log if you use `--grpc`. The key remains in process memory and in the file (plaintext at rest, readable by that account and by root, so keep it and its backups out of source control). Clients read the key from the file's `api-key` line; give remote clients their copy through your secret store ([secrets.md](secrets.md)). A key passed through `VLLM_API_KEY` would stay out of argv but remain readable through `/proc/<pid>/environ` by the same account and by root for the server's whole lifetime, and in any process that inherits it; the file avoids that channel. This was read in the pinned source (cited in Sources). The pinned parser class was also run on its own, outside vLLM, with vLLM's logger stubbed and a minimal `serve` parser in place of vLLM's own: with `--config FILE` it turned the generated file's `api-key` line into a one-element key list, and with `--config=FILE` it left the key unset. No vLLM server was run.

The key does not cover the whole server. vLLM's own security page states that it authenticates only the `/v1`, `/v2`, and `/inference` path prefixes, and lists `/invocations`, the SageMaker-compatible route, as requiring no key while reaching the same inference capability as the protected `/v1` routes; the profiler routes `/start_profile` and `/stop_profile` are likewise unauthenticated, and a plugin route outside those prefixes is unauthenticated unless the plugin enforces its own check. vLLM says plainly not to rely on the key alone. Allowlist only the routes your application needs at the proxy and refuse everything else there, `/invocations` included, rather than assuming the key covers the surface. vLLM binds every interface by default: `vllm serve` leaves `--host` unset, which listens on `0.0.0.0` (the startup log shows `http://0.0.0.0:8000`), so pass `--host 127.0.0.1` to keep it on loopback. vLLM can terminate TLS natively (`--ssl-keyfile`, `--ssl-certfile`, and `--ssl-ca-certs`, passed through to uvicorn), but fronting it with a TLS proxy or tunnel is the recommended pattern; either way keep the server itself on loopback or a private network.

## Hugging Face Text Generation Inference (TGI)

`text-generation-launcher` listens on `0.0.0.0:3000` by default (as of v3.3.7; `--hostname`, env `HOSTNAME`; `--port`, env `PORT`). The image built from the repository's main `Dockerfile` sets `PORT=80`, so a bare container listens on port 80 instead, and on every interface: Docker sets `HOSTNAME` to the container's hostname (by default its short ID), which is not an IP address, and the router then falls back to `0.0.0.0`. Bind it to loopback (substitute your model ID inside the quotes in the block below), or publish nothing from the container network except the proxy:

Lifecycle note, as of September 2026: the TGI repository is in maintenance mode and was archived on 2026-03-21 (read-only). Hugging Face recommends vLLM, SGLang, or local engines such as llama.cpp going forward. A server that no longer receives fixes belongs behind the same controls as any other, and on a migration list.

```bash
text-generation-launcher --model-id 'REPLACE_WITH_MODEL_ID' --hostname 127.0.0.1 --port 3000
```

The launcher reference lists `--api-key` (env `API_KEY`) without describing it. At v3.3.7 the launcher takes that value from the flag or from `API_KEY` and then starts the router with it as a `--api-key` argument, so however you supply it, the key is readable through the router process's `ps` and `/proc/<pid>/cmdline` by other local accounts while TGI runs; no launcher input avoids that, and passing it through the environment does not help. TGI's native key is a control for network clients, not for other users of the host: run it where no account you do not trust can list its processes, and enforce the bearer check at the proxy. The router source shows what it does: when set, requests to the standard inference `base_routes` must carry a matching `Authorization: Bearer <key>` header or receive 401, while the health, info, and metrics routes stay unauthenticated. Builds that enable the KServe (`/v2/...`) endpoints register them outside that key middleware, `/v1/models` sits outside it too, and the Vertex feature route configured through `AIP_PREDICT_ROUTE` is registered after the auth layer as well, so those paths are unauthenticated; allowlist the routes you use and enforce the bearer check at the proxy. Treat it as a second layer and enforce the bearer check at the proxy too (pattern in [ollama.md](ollama.md)). The launcher has no TLS option, so front TGI per [nginx.md](nginx.md)/[caddy.md](caddy.md). The Prometheus listener (`--prometheus-port`, default 9000) is unauthenticated as well; keep it private.

## SGLang

`python -m sglang.launch_server` listens on `127.0.0.1:30000` by default (`--host`, `--port`; values as of v0.5.20); keep that bind. `--api-key` sets the key the OpenAI-compatible endpoints require, and `--admin-api-key` separately protects administrative endpoints (at v0.5.20, the weight-update endpoints and `/flush_cache` among them, but not `/server_info`; see below), which then require `Authorization: Bearer <admin key>`. Do not put either value on the command line: there it is readable through `ps` and `/proc/<pid>/cmdline` by other local accounts for the server's whole lifetime. At v0.5.20, `--config` reads the server options from a YAML file instead, and the pinned sources document no stdin or environment input for either key, so put both keys in a file that only the account running SGLang can read. Create it once, as that account:

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set -eC +x +a
  umask 077
  mkdir -p -- "$HOME/.config/sglang"
  chmod 700 -- "$HOME/.config/sglang"
  if [ -e "$HOME/.config/sglang/server.yaml" ] || [ -L "$HOME/.config/sglang/server.yaml" ]; then
    echo 'server.yaml already exists in ~/.config/sglang; nothing written'; exit 2
  fi
  set -- "$(openssl rand -hex 32)" "$(openssl rand -hex 32)"
  [ "${#1}" -eq 64 ] || { echo 'key generation failed; nothing written'; exit 2; }
  [ "${#2}" -eq 64 ] || { echo 'key generation failed; nothing written'; exit 2; }
  case "$1$2" in *[!0123456789abcdef]*) echo 'key generation failed; nothing written'; exit 2 ;; esac
  printf 'api-key: "%s"\nadmin-api-key: "%s"\n' "$1" "$2" > "$HOME/.config/sglang/server.yaml"
)
```

The block writes nothing unless both generated keys are 64 hex characters, because SGLang serves ordinary requests whenever the API key is empty, even when `--admin-api-key` is set, so an empty value would leave the OpenAI-compatible endpoints open. `umask 077` creates the directory mode `0700` and the file mode `0600`. The block makes the directory mode `0700` first and then refuses, before it generates a key, when `server.yaml` already exists in any form (a regular file, a FIFO, or a symlink, dangling or not), so a rerun cannot replace keys your clients already hold; `set -C` also refuses an existing regular file, and the explicit check handles the other forms. These checks hold only in owner-only directories no other account can replace. The keys pass only through the subshell's positional parameters and the builtin `printf`, never a command line; the block clears inherited traps first because a DEBUG, RETURN or ERR trap from your shell could otherwise read them, and it assumes a clean shell. Start the server with only non-secret values on its command line, substituting your model path inside the quotes, and do not add `--api-key` or `--admin-api-key` there, which would put the values back in argv:

```bash
python -m sglang.launch_server --model-path 'REPLACE_WITH_MODEL_PATH' --config "$HOME/.config/sglang/server.yaml"
```

Clients read the API key from the file's `api-key` line; give the admin key only to the operators who use the administrative endpoints. SGLang turns the file's values into an internal argument list before parsing them; that list lives inside the Python process, not in the kernel's `/proc/<pid>/cmdline`, so the keys stay out of `ps`. They remain in process memory and in the file (plaintext at rest, readable by that account and by root, so keep it and its backups out of source control), and SGLang itself hands them out. At v0.5.20 the launch path logs `server_args=` with every resolved field, both keys included, at INFO level, and `/server_info` (and its deprecated alias `/get_server_info`) returns the same fields plus `launch_command`, the argument list with the file's values merged in, to any request the ordinary API key authorizes, because it carries no admin auth level. This was read in the pinned source (cited in Sources), not run. So a holder of the API key can read the admin key. Either give the API key only to clients you would also trust with the administrative endpoints, or, if other clients must hold it, have the reverse proxy allow only the routes those clients need (which excludes `/server_info` and `/get_server_info`) and refuse every other route, the same allowlist the vLLM section prescribes; either way, protect the startup log.

Native TLS exists: `--ssl-keyfile` and `--ssl-certfile` take PEM files ([self-signed.md](self-signed.md) or [free-certificates.md](free-certificates.md)), `--ssl-ca-certs` names a CA bundle, and `--enable-ssl-refresh` hot-reloads renewed certificates. A reverse proxy remains the simpler choice when you already run one.

## NVIDIA Triton Inference Server

`tritonserver` starts three listeners on `0.0.0.0`: HTTP on 8000, gRPC on 8001, and Prometheus metrics on 8002. No authentication is enabled by default: its optional gRPC mutual TLS and restricted-API shared secrets can cover inference as well as model control, but do not replace the gateway. NVIDIA's secure deployment guidance is that Triton is a microservice that is "not exposed directly to an untrusted network": a dedicated gateway or proxy (NGINX, Envoy, Istio, Kong are the examples given) handles authorization, access control, and encryption, and Triton "handles only trusted, validated requests". Bind each listener privately and disable the protocols you do not use:

```bash
tritonserver --model-repository=/models --http-address=127.0.0.1 --grpc-address=127.0.0.1 --metrics-address=127.0.0.1
```

`--allow-http` and `--allow-grpc` default to true; NVIDIA recommends setting either to false when not required, and `--allow-metrics` switches off the metrics listener. For gRPC, `--grpc-use-ssl` with `--grpc-server-cert` and `--grpc-server-key` enables a TLS channel, and `--grpc-use-ssl-mutual` requires client certificates. HTTP has no TLS option; the proxy provides it. `--http-restricted-api` and `--grpc-restricted-protocol` fence the API groups you name (model-repository control, and inference too if you list it) behind a shared-secret header, a useful second layer against network clients but not a substitute for the gateway. The secret is part of the flag's value (`--http-restricted-api=<API_1>,<API_2>:<restricted-key>=<restricted-value>`), and `tritonserver` has no other input for it. Traced at the pinned source commit: `tritonserver` parses its options with `getopt_long` over argv, the two options hand their value straight to the restricted-feature parser, the parser opens no option or response file and reads nothing from stdin, and every environment variable read under `src/` has a non-secret name (the `AIP_*` and `SAGEMAKER_*` endpoint settings, the `OTEL_BSP_*` tracing settings, a gRPC response-delay setting and test-backend names). So the value sits in argv, readable through `ps` and `/proc/<pid>/cmdline` by other local accounts, as well as by the same account and root, for the server's whole lifetime; quoting does not change that, and no `tritonserver` launch form avoids it. Command-line auditing on the host (auditd `EXECVE` records, for example) can also record the value and keep it after the process exits. Under an orchestrator the same value also sits in the workload definition (a Kubernetes pod spec's `args`, for example) for everyone who can read it. A server's shared secret is neither throwaway nor short-lived, so it is no secret from other accounts on the host: do not rely on it as a control against them. Enforce authorization at the reverse proxy or gateway in front of Triton, which is the control, and treat the restricted-API value only as a check against network clients that reach Triton past it; rotate the value whenever an account you do not trust could have read it, or a command-line audit record holding it could have reached one. If you do not load and unload models at run time, leave `--model-control-mode` at its default, `none`, under which the model-control API returns an error for load and unload requests, whatever the secret. Builds with cloud endpoints add conditional listeners beyond these three: `AIP_MODE=PREDICTION` enables a Vertex AI endpoint (its port is `AIP_HTTP_PORT`, otherwise 8080), and a SageMaker endpoint may also be present, so disable the ones you do not use or add them to the bind inventory and the checks below.

## LM Studio (local server)

LM Studio's developer server is a desktop feature. The documentation addresses it at `http://localhost:1234` throughout (the port is a field in Developers Page > Server Settings), and "By default, LM Studio does not require authentication for API requests." The "Serve on Local Network" switch (or `lms server start --bind 0.0.0.0`) rebinds it to every interface; LM Studio's own note reads: "Any bind other than 127.0.0.1 exposes the server beyond localhost; we recommend enabling authentication." Leave that switch off. If another machine must reach it, first enable "Require Authentication" (LM Studio 0.4.0 or newer) and create a token under "Manage Tokens"; clients then send `Authorization: Bearer <token>`. The server settings list no TLS option, so anything beyond the local machine goes through a tailnet ([tailscale.md](tailscale.md)) or an authenticated TLS proxy, never a port-forward.

## text-generation-webui

One process, two surfaces: the Gradio UI (default `127.0.0.1:7860`) and, when started with `--api`, an OpenAI-compatible API (default `127.0.0.1:5000`, endpoints under `/v1`). Both default to loopback, and both start with no authentication.

`--listen` rebinds to `0.0.0.0`, and it widens both surfaces at once: opening the UI to your LAN also opens the API port whenever `--api` is set. `--listen-port` moves the UI port, `--api-port` moves the API port, and `--listen-host` picks a specific bind address instead of `0.0.0.0`; like the wider binding itself it takes effect only with `--listen`, and on its own it does nothing. Never start an internet-adjacent instance with `--share`: it publishes the UI through a public `*.gradio.live` tunnel, reachable by anyone who has the URL. `--public-api` does the same for the API through a Cloudflare tunnel. Treat both flags as publishing, not as remote access.

Auth is per surface, and neither control covers the other:

- UI: `--gradio-auth-path FILE` turns on a Gradio login form from the `user:password` entries in the file; `--gradio-auth user:password` takes the same entries on the command line, where they do not belong (below). Neither does anything for the API.
- API: `--api-key KEY` requires `Authorization: Bearer KEY` on the OpenAI-compatible routes such as `/v1/models` and `/v1/chat/completions`; the Anthropic-compatible `/v1/messages` route reads the same key from an `x-api-key` header instead. `--admin-key` guards the admin endpoints (model load and unload) and falls back to the `--api-key` value when unset; an admin key alone does not protect the ordinary routes. Without `--api-key`, the API answers anyone who can reach the port, even when the UI has a Gradio login in front of it. At the pinned commits, starting the API logs the configured `--api-key` (and any distinct `--admin-key`) in plaintext at INFO level to stdout and the service log, so protect that output as you protect the key file below (owner-only, out of source control and out of shared log collection) and rotate the key after any disclosure.

All three are secrets, and none belongs on the command line, where `ps` and `/proc/<pid>/cmdline` show it to other local accounts for the server's whole lifetime; quoting does not change that. Put the login in the `--gradio-auth-path` file. At the pinned `server.py` the loader reads `user:password` entries separated by commas or line breaks, strips the whitespace around each, and splits each entry at every `:`, so neither the user name nor the password may contain `:` or `,`. The block below allows only letters, digits, dot, underscore and hyphen in the user name and generates a hex password. Create the file once, as the account that runs text-generation-webui, substituting the user name inside the quotes on the `set --` line:

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set -eC +x +a
  umask 077
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_UI_USER'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; nothing written'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'the set -- line needs exactly 1 value, inside the quotes; nothing written'; exit 2; }
  case "$1" in ""|*REPLACE_WITH_*) echo 'substitute a user name inside the quotes on the set -- line above; nothing written'; exit 2 ;; esac
  case "$1" in *[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-]*) echo 'use only letters, digits, dot, underscore or hyphen in the user name; nothing written'; exit 2 ;; esac
  mkdir -p -- "$HOME/.config/text-generation-webui"
  chmod 700 -- "$HOME/.config/text-generation-webui"
  if [ -e "$HOME/.config/text-generation-webui/gradio-auth" ] || [ -L "$HOME/.config/text-generation-webui/gradio-auth" ]; then
    echo 'gradio-auth already exists in ~/.config/text-generation-webui; nothing written'; exit 2
  fi
  set -- "$1" "$(openssl rand -hex 16)"
  [ "${#2}" -eq 32 ] || { echo 'password generation failed; nothing written'; exit 2; }
  case "$2" in *[!0123456789abcdef]*) echo 'password generation failed; nothing written'; exit 2 ;; esac
  printf '%s:%s\n' "$1" "$2" > "$HOME/.config/text-generation-webui/gradio-auth"
)
```

The `set --` line opens with a marker the block checks, so a paste that drops that line is refused rather than run on your shell's own arguments. The block makes the directory mode `0700` first, then refuses, before it generates a password, when `gradio-auth` already exists in any form (a regular file, a FIFO, or a symlink, dangling or not); as with the vLLM block, that holds only in owner-only directories no other account can replace. `umask 077` creates the directory mode `0700` and the file mode `0600`, `set -C` still refuses to overwrite an existing regular file, and the block writes nothing unless the generated password is 32 hex characters. The password passes only through the subshell's positional parameters and the builtin `printf`; the block clears inherited traps first and assumes a clean shell. Read the password from the file once into your password manager. The file holds it in plaintext at rest, readable by that account and by root, so keep it and its backups out of source control.

The API keys have no file flag and no environment input at the pinned sources: the API reads them only from the parsed arguments. The pinned `modules/shared.py` does read further flags from `CMD_FLAGS.txt` in the user-data directory, and it splices them into Python's own argument list inside the process, so keys placed there stay out of `/proc/<pid>/cmdline`. Do not use the checkout's own `user_data/CMD_FLAGS.txt` for them: at the pinned commit it is a tracked file (it ships with three comment lines), so a key written there is a change to a tracked file that `git diff` prints and `git stash` copies into the repository, and the update wizard in `one_click.py` runs `git merge --autostash` (stashing the change) and offers `git reset --hard` (discarding it). This was read from the code, not run. Point `--user-data-dir` at a private directory outside the checkout instead, readable only by the account that runs text-generation-webui; it then stands in for the whole `user_data` directory (the model, LoRA and cache directories, among others, default under it), so copy across the models and settings you use. Write generated keys into a new `CMD_FLAGS.txt` there, as that account, substituting the directory's absolute path inside the quotes on the `set --` line (a path with spaces stays one value there). Write each `'` in the path as `'\''`; this is required, because a `'` left unescaped or escaped wrongly ends the quoting early, and the rest of the line can then change the path the block uses or run as shell syntax:

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set -eC +x +a
  umask 077
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PRIVATE_USER_DATA_DIR'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; nothing written'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'the set -- line needs exactly 1 value, inside the quotes; nothing written'; exit 2; }
  case "$1" in ""|*REPLACE_WITH_*) echo 'substitute the private user-data directory inside the quotes on the set -- line above; nothing written'; exit 2 ;; esac
  case "$1" in /*) ;; *) echo 'give the user-data directory as an absolute path; nothing written'; exit 2 ;; esac
  mkdir -p -- "$1"
  cd -- "$1"
  chmod 700 .
  (
    while :; do
      if [ -e .git ] || [ -L .git ]; then exit 3; fi
      if [ . -ef .. ]; then exit 0; fi
      cd -P .. || exit 4
    done
  ) || { echo 'that directory or one above it holds a .git entry, or the walk could not reach /; no key written'; exit 2; }
  if [ -e CMD_FLAGS.txt ] || [ -L CMD_FLAGS.txt ]; then
    echo 'CMD_FLAGS.txt already exists there; use a new private directory; no key written'; exit 2
  fi
  set -- "$(openssl rand -hex 32)" "$(openssl rand -hex 32)"
  [ "${#1}" -eq 64 ] || { echo 'key generation failed; nothing written'; exit 2; }
  [ "${#2}" -eq 64 ] || { echo 'key generation failed; nothing written'; exit 2; }
  case "$1$2" in *[!0123456789abcdef]*) echo 'key generation failed; nothing written'; exit 2 ;; esac
  printf -- '--api-key %s\n--admin-key %s\n' "$1" "$2" > CMD_FLAGS.txt
)
```

The block creates `CMD_FLAGS.txt` once and never appends to one. Its `set --` line opens with a marker the block checks, so a paste that drops that line is refused rather than run on your shell's own arguments. Before it generates a key, it refuses a relative path; a directory that holds a `.git` entry of any kind, or has one in any directory above it, whether a repository directory, a submodule's or worktree's `.git` file, a symlink or a malformed entry, which covers the checkout's own `user_data`; and a directory where `CMD_FLAGS.txt` already exists in any form, a dangling symlink included. The walk starts in the target directory and steps up with `cd -P ..` until `.` and `..` are the same directory, testing `.git` relative to each one, so symlinks are resolved and no path string is built: a newline or other unusual byte in a directory name, or a physical path longer than the system's path limit, cannot hide an ancestor's `.git`. It refuses if any step fails. The walk does not run git, so neither a git error nor an inherited `GIT_*` variable can let the write through. It cannot see a checkout reached through a bind mount, or a repository whose work tree is set elsewhere (a bare "dotfiles" repository used with `--work-tree=$HOME`, for example), so choose a directory you know is outside any checkout. Like the other writers' checks, the walk and the existence check run before the write, not atomically with it, so they hold only in owner-only directories no other account can change, and a `.git` created there between the check and the write is not seen. A directory the block refuses after entering it is left behind, empty if the block created it, and mode `0700`. The block makes the directory mode `0700` after entering it, so for a directory another account owns `chmod` itself fails and the block stops there, with `chmod`'s error rather than its own message and the directory's mode unchanged; run as root, that `chmod` succeeds on any directory, so do not run the block as root. `umask 077` creates the file mode `0600`, `set -C` also refuses an existing regular file (the explicit check handles the other forms), and the block writes nothing unless both keys are 64 hex characters. The keys pass only through the subshell's positional parameters and the builtin `printf`. Add any other flags you want in the file on new lines after the two key lines, and never add or edit a key line: the loader joins the file's lines before splitting them into arguments, and a later `--api-key` or `--admin-key` would silently replace a key. To rotate the keys, run the block again with a new private directory and move your settings across. Start `server.py` from the installation directory with only non-secret values on its command line, substituting the same path inside the quotes:

```bash
python server.py --user-data-dir 'REPLACE_WITH_PRIVATE_USER_DATA_DIR' --api --gradio-auth-path "$HOME/.config/text-generation-webui/gradio-auth"
```

Start it this way, directly, not through the one-click `start_*` scripts. At the pinned `one_click.py` the launcher joins its own arguments into one string without quoting them (line 24), builds `python server.py` plus that string (line 486) and runs the result through `bash` with `shell=True` (line 208), so a quoted path is split at its spaces and any shell syntax in it runs, and a key passed to those scripts would land on `server.py`'s command line again. This was read in the pinned source, not run. Clients read the API key from the file's `--api-key` line; give the admin key only to the operators who load and unload models. The keys remain in process memory, in the file, and in the startup log (above). The pinned `modules/shared.py`, imported with `--user-data-dir` pointing at a directory the block had written (a path containing a space, with a `--listen-port` line added after the key lines), parsed both keys and that flag from `CMD_FLAGS.txt` while the process's `/proc/self/cmdline` held neither; the launcher and API behaviour above was read in the pinned source (cited in Sources), and no text-generation-webui server was run.

`--api --nowebui` runs the API alone, the right shape for a server where the UI has no business existing. `--ssl-keyfile` and `--ssl-certfile` give both surfaces TLS, but the better pattern is the usual one: keep both ports on loopback and front them with a reverse proxy that terminates TLS and enforces auth (`--subpath` exists for serving the UI under a proxy path). Without TLS, the Gradio login submits credentials in the clear.

One proxy detail is specific to this API: unless `--listen` (or `--public-api`) is set, it rejects any request whose `Host` header is not `localhost` or `127.0.0.1` with a `400`, so a reverse proxy in front of a loopback API must send `Host: localhost` upstream rather than forwarding the public hostname.

## The pattern, whatever the server

1. Bind to `127.0.0.1` (or a private container network); confirm with `ss -tlnp`.
2. Require a per-client API key at the server where supported, or at the proxy otherwise (bearer-token check per [ollama.md](ollama.md)); generate keys per [authentication.md](authentication.md). Keep the key off the server's command line, child processes included: use stdin where the server offers it, otherwise a file the server reads itself, created owner-only, or the guarded one-command prefix assignment of CONTRIBUTING rule 7, which leaves the key readable through `/proc/<pid>/environ` for the server's lifetime. Where the server takes the secret only in argv (the TGI router's key, Triton's restricted-API value), its native check is a control against network clients, not against other local accounts; enforce auth at the proxy.
3. TLS in front: [caddy.md](caddy.md), [nginx.md](nginx.md), [cloudflare.md](cloudflare.md), or [tailscale.md](tailscale.md).
4. Human-facing UIs on top of these servers ([open-webui.md](open-webui.md)) carry their own login and MFA ([mfa.md](mfa.md)).

## Verify

```bash
ss -tlnp   # every listener; 8080/8000/8001/8002/3000/80/9000/30000/5000/7860/1234. ss shows only a
           # namespace-local BIND, not a host firewall, a cloud security group, or Docker -p NAT
           # publication. From another host, probe EACH backend listener's own host and port (adapt the
           # subshell below, which shows the technique for one endpoint) and confirm each is refused
pgrep -c -f -- '(^| )--((admin-)?api-key|admin-key|gradio-auth|http-restricted-api|grpc-restricted-protocol)( |=)'
           # counts visible command lines carrying one of those secret-bearing arguments; 0 means none was seen
           # right now, and any match needs a look. Triton's restricted-API secrets have no input outside the
           # flag value, so a match is expected while you use them. It does not see a key in a file the server
           # reads, in a server's environment (VLLM_API_KEY, LLAMA_API_KEY), inside another argument's value
           # (vLLM's Rust-frontend --args-json), on an abbreviated option that argparse or getopt_long accepts
           # (--api-k X, --http-restricted=...), or on a flag the pattern does not name
(
  # Feed the API key to curl on stdin (curl --header @-), never in argv:
  # -H "Authorization: Bearer KEY" is readable in ps / /proc/<pid>/cmdline.
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_API_KEY'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the API key on the set -- line above; not probing"; exit ;; esac
  curl -q -sS --noproxy '*' -w 'http=%{http_code} exit=%{exitcode}\n' https://models.example.com/v1/models   # PROXY-policy test: 401 without a key. TGI leaves /v1/models outside its native key middleware, so a 200 is not proof the backend enforces the key
  printf 'Authorization: Bearer %s\n' "$1" | curl -q -sS --noproxy '*' -w 'http=%{http_code} exit=%{exitcode}\n' -H @- https://models.example.com/v1/models   # positive control: 200 with a model list, printed
)
(
  set -- 'REPLACE_WITH_A_REAL_SERVED_MODEL'
  case "$1" in ""|*REPLACE_WITH_*) echo 'substitute a real served model name inside the quotes on the set -- line above; not probing'; exit 2 ;; esac
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

The `pgrep` line counts processes whose visible command line has an argument that is `--api-key`, `--admin-api-key`, `--admin-key`, `--gradio-auth`, `--http-restricted-api` or `--grpc-restricted-protocol` followed by a space or `=`, the forms in which llama-server, vLLM, SGLang, the TGI router, text-generation-webui and Triton take a secret on the command line; it prints a count and never a key, and it excludes itself. A count is a lead, not proof: an empty value, or an argument of unrelated text that contains ` --api-key `, matches too, and `0` means only that no visible process matched at that moment. It was demonstrated on the authoring host against stub processes that opened no listener (`python3` sleeping with the test arguments, procps-ng 4.0.4): `--api-key DUMMY_NOT_A_SECRET`, `--admin-key DUMMY_NOT_A_SECRET`, `--admin-api-key=DUMMY_NOT_A_SECRET`, `--gradio-auth u:DUMMY_NOT_A_SECRET`, `--http-restricted-api=model-repository:admin-key=DUMMY_NOT_A_SECRET`, `--grpc-restricted-protocol=model-repository:admin-key=DUMMY_NOT_A_SECRET` and an empty `--api-key=` each counted `1`, while `--api-key-file /x`, `--gradio-auth-path /x`, `--config /x`, `notes--api-key x`, `--admin-keys x`, `--http-restricted-api-x y`, `--args-json '{"api_key":["DUMMY_NOT_A_SECRET"]}'`, and the abbreviations `--api-k DUMMY_NOT_A_SECRET` and `--http-restricted=model-repository:k=DUMMY_NOT_A_SECRET` each counted `0`, so the line tells the file-based launch forms from the argv ones, and it misses a key inside a JSON argument or behind an abbreviated option (the pinned text-generation-webui parser keeps argparse's default prefix matching, and Triton's `getopt_long` accepts an unambiguous prefix). No model server was run for it. A `hidepid` proc mount limits the count to your own processes, and a process that has scrubbed its own arguments is not seen.

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

- llama.cpp server README (defaults, `--api-key` and its `LLAMA_API_KEY` environment input, `--api-key-file` ("path to file containing API keys, one per line") and its `LLAMA_ARG_API_KEY_FILE` environment input, the `LLAMA_ARG_*` environment inputs most options carry, `LLAMA_ARG_HOST` for `--host` among them, SSL flags): https://github.com/ggml-org/llama.cpp/blob/e0dff58475bc9ed68eedcb265ee998f2fcabb3b1/tools/server/README.md
- vLLM documentation: https://docs.vllm.ai/
- vLLM server host default (`FrontendArgs.host` defaults to `None`; checked 2026-09-14): https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/entrypoints/launchers/cli_args.py
- vLLM server socket bind (the launcher builds `(args.host or "", port)`, so an unset host binds every IPv4 interface, and renders the empty host as `0.0.0.0` in the startup log; checked 2026-09-14): https://github.com/vllm-project/vllm/blob/8c1557a79c539ffe82d004d2a0c8d7b5e71159ce/vllm/entrypoints/launchers/launcher.py
- vLLM security, API key authentication limitations (protected prefixes, unprotected `/invocations` and profiler routes): https://docs.vllm.ai/en/latest/usage/security/
- vLLM `--api-key` (`FrontendArgs.api_key`, a list of keys; read in source, not run): https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/entrypoints/launchers/cli_args.py#L304 and https://github.com/vllm-project/vllm/blob/8c1557a79c539ffe82d004d2a0c8d7b5e71159ce/vllm/entrypoints/launchers/cli_args.py#L296
- vLLM `VLLM_API_KEY`, declared in `envs.py` (https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/envs.py#L803, https://github.com/vllm-project/vllm/blob/8c1557a79c539ffe82d004d2a0c8d7b5e71159ce/vllm/envs.py#L801) and read as the fallback when `--api-key` is unset, the CLI taking precedence (identical at both commits): https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/entrypoints/serve/middleware/register.py#L32-L36
- vLLM `--config` YAML loader (expanded only when `--config` is its own argument, `.yaml` or `.yml` required, `yaml.safe_load`, each key turned into the option `--<key>` and merged into the in-process argument list before parsing): https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/utils/argparse_utils.py#L329-L330, #L517-L548, #L585-L596 and #L621-L622
- vLLM startup log of non-default arguments with `api_key` redacted (https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/entrypoints/serve/utils/api_utils.py#L271-L286), and the unredacted `--grpc` argument log: https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/entrypoints/launchers/grpc_server.py#L64
- vLLM API server processes started through `multiprocessing` `spawn`, arguments pickled rather than on a command line (https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/v1/utils.py#L210-L246), and the opt-in Rust frontend, started only when `VLLM_USE_RUST_FRONTEND` is set, which receives the non-default arguments, `api_key` included, as `--args-json` on its command line: https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/v1/utils.py#L384-L411 and https://github.com/vllm-project/vllm/blob/dee37d89115db4c94a820a79a78a7828e141c910/vllm/entrypoints/cli/serve.py#L63-L64
- TGI launcher arguments (--hostname, --port, --api-key, --prometheus-port): https://huggingface.co/docs/text-generation-inference/reference/launcher
- TGI launcher `hostname` default `0.0.0.0` and `port` default 3000, each also read from the environment (pinned tag v3.3.7, the last release before the repository was archived): https://github.com/huggingface/text-generation-inference/blob/v3.3.7/launcher/src/main.rs#L769-L774
- TGI image built from the repository's main `Dockerfile`, `ENV ... PORT=80` (pinned tag v3.3.7): https://github.com/huggingface/text-generation-inference/blob/v3.3.7/Dockerfile#L147-L149
- TGI router: a `--hostname` that does not parse as an IP address logs "Invalid hostname, defaulting to 0.0.0.0" and binds `0.0.0.0` (pinned tag v3.3.7): https://github.com/huggingface/text-generation-inference/blob/v3.3.7/router/src/server.rs#L1906-L1910
- TGI router source (what --api-key enforces): https://github.com/huggingface/text-generation-inference/blob/24ee40d143d8d046039f12f76940a85886cbe152/router/src/server.rs
- TGI repository (maintenance-mode notice, archived 2026-03-21): https://github.com/huggingface/text-generation-inference
- SGLang server arguments (--host, --port, --api-key, --admin-api-key, SSL flags; docs.sglang.ai redirects here): https://docs.sglang.io/docs/advanced_features/server_arguments
- Triton secure deployment considerations: https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/customization_guide/deploy.html
- Triton quickstart (default listeners on 8000, 8001, 8002): https://github.com/triton-inference-server/server/blob/0194c3da9ddeeff07547f46aa058cf88acb51893/docs/getting_started/quickstart.md
- Triton inference protocols (gRPC SSL flags, restricted APIs): https://github.com/triton-inference-server/server/blob/c29bbe17eac256bbcd8fea47cde2f219d2be37cf/docs/customization_guide/inference_protocols.md
- Triton command line parser (address and port flags with defaults): https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc
- Triton `--http-restricted-api` and `--grpc-restricted-protocol`, parsed from argv by `getopt_long` only (traced at 546a787 across `src/`: the option definitions, the parse loop and the two cases handing `optarg` to `ParseRestrictedFeatureOption`, no option or response file, and every `getenv`/`GetEnvironmentVariableOrDefault` under `src/` reading a non-secret name): https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/command_line_parser.cc#L508-L516, #L632-L640, #L1329-L1330, #L1420-L1423 and #L1561-L1566
- Triton restricted API groups, `inference` among them: https://github.com/triton-inference-server/server/blob/546a78766fb112128aa0b10a70c55f4f39c3b1df/src/restricted_features.h#L54-L57 and https://github.com/triton-inference-server/server/blob/c29bbe17eac256bbcd8fea47cde2f219d2be37cf/docs/customization_guide/inference_protocols.md#L153-L196
- Triton model control mode `NONE`, the default, returning an error for load and unload requests: https://github.com/triton-inference-server/server/blob/c29bbe17eac256bbcd8fea47cde2f219d2be37cf/docs/user_guide/model_management.md#L35-L45
- LM Studio local server: https://lmstudio.ai/docs/developer/core/server
- LM Studio serve on local network: https://lmstudio.ai/docs/developer/core/server/serve-on-network
- LM Studio server settings: https://lmstudio.ai/docs/developer/core/server/settings
- LM Studio authentication: https://lmstudio.ai/docs/developer/core/authentication
- LM Studio OpenAI compatibility (localhost:1234 examples): https://lmstudio.ai/docs/developer/openai-compat
- text-generation-webui README, command-line flags: https://github.com/oobabooga/text-generation-webui#command-line-flags
- text-generation-webui, OpenAI-compatible API documentation: https://github.com/oobabooga/text-generation-webui/blob/ceade2eb1ba3f84518076270df2240b6bbb01da0/docs/12%20-%20OpenAI%20API.md
- text-generation-webui, flag definitions and defaults (modules/shared.py): https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/modules/shared.py
- text-generation-webui, `--user-data-dir` and the in-process `CMD_FLAGS.txt` loader (lines whose first non-space character is `#` skipped, the rest split as shell words and spliced into Python's `sys.argv` before parsing): https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/modules/shared.py#L50 and #L221-L236, with the directory resolved at https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/modules/paths.py#L5-L21
- text-generation-webui, `user_data/CMD_FLAGS.txt` shipped as a tracked file of three comment lines: https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/user_data/CMD_FLAGS.txt
- text-generation-webui one-click launcher (its own arguments joined unquoted and run through `bash` as `server.py`'s command line, the update wizard's `git merge --autostash` and `git reset --hard`; read in source, not run): https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/one_click.py#L24, #L208, #L396, #L485-L486, #L504 and #L527
- text-generation-webui `--gradio-auth-path` loader (entries split at commas and line breaks, whitespace stripped, each split at every `:`): https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/server.py#L90-L95
- text-generation-webui, API bind and key checks (modules/api/script.py): https://github.com/oobabooga/text-generation-webui/blob/619a2b8ee4b7e48541a9be5c07e04cd31b91b44f/modules/api/script.py
- text-generation-webui, the API key and a distinct admin key logged in plaintext at INFO at startup: https://github.com/oobabooga/text-generation-webui/blob/c022565b1257a9c7d9a5128c8b4c03587559cf08/modules/api/script.py#L594-L597 and https://github.com/oobabooga/text-generation-webui/blob/619a2b8ee4b7e48541a9be5c07e04cd31b91b44f/modules/api/script.py#L599-L602
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0): https://curl.se/docs/manpage.html
- SGLang `host` and `port` field defaults, `127.0.0.1` and `30000` (pinned tag v0.5.20; that the `--host`/`--port` flags use these fields rests on the server-arguments docs above): https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/arg_groups/fields/serving.py#L72-L73
- SGLang `--config` ("Read CLI options from a config file. Must be a YAML file with configuration options."; pinned tag v0.5.20): https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/server_args.py#L397-L399
- SGLang configuration loader (`yaml.safe_load`, a `.yaml` or `.yml` suffix required, each key turned into the option `--<key>` and the values merged into the argument list before parsing; pinned tag v0.5.20): https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/utils/server_args_config_parser.py#L118-L187
- SGLang environment registry, checked for an API-key or admin-key entry and found to carry none (pinned tag v0.5.20): https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/environ.py
- SGLang key exposure at v0.5.20 (read in source, not run): the `api_key` and `admin_api_key` fields (https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/arg_groups/fields/serving.py#L155-L162), `resolved_dict` over every field and `_launch_command` joined from the merged argument list (https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/server_args.py#L311-L325 and #L736), the INFO log of `server_args=` (https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/entrypoints/engine.py#L1109), `/server_info` with no `auth_level` decorator (https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/entrypoints/http_server.py#L818-L850) and a normal endpoint requiring only the API key (https://github.com/sgl-project/sglang/blob/v0.5.20/python/sglang/srt/utils/auth.py#L145-L151)
- TGI launcher: `api_key` is `#[clap(long, env)]`, and the launcher pushes `--api-key` and the value into the router's arguments (pinned tag v3.3.7): https://github.com/huggingface/text-generation-inference/blob/v3.3.7/launcher/src/main.rs
