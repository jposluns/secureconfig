# Image-generation UIs: ComfyUI, Stable Diffusion WebUI, InvokeAI, Fooocus

None of these tools ships real authentication by default, and each accepts arbitrary Python through custom nodes or extensions. **Binding one to a public interface is host compromise, not just data exposure.** Keep every instance on loopback and reach it only through a tunnel or an authenticated TLS proxy: [fronting-auth.md](fronting-auth.md), [cloudflare.md](cloudflare.md), [tailscale.md](tailscale.md), or a reverse proxy per [nginx.md](nginx.md)/[caddy.md](caddy.md).

If you run any of these in a container, do not stop at the network boundary: a compromised custom node or extension can still reach whatever the container can reach, so apply [container-hardening.md](container-hardening.md) (a non-root user, a read-only filesystem where the tool allows it, no unnecessary mounts) as a second layer, not a substitute for keeping the port off the network.

## ComfyUI

`--listen` with no argument binds to `0.0.0.0,::` (every IPv4 and IPv6 interface); given an address it binds only there. The default with the flag absent is `127.0.0.1`, and the default port is `8188` (both as of v0.37.0). There is no built-in login: the server accepts any workflow from anyone who can reach it.

Custom nodes are the bigger risk. They run as plain Python with the same privileges as the server process; ComfyUI's own security update warns that `eval`/`exec` calls in a node are "direct attack vectors" for remote code execution. ComfyUI-Manager (the default node installer) had its own unauthenticated-RCE advisory, CVE-2025-67303 (GHSA-95pq-hr8p-f5g7): an unprotected alternate channel left the manager's data and configuration directories insufficiently protected by ComfyUI's web API access control, letting an attacker upload arbitrary files for full system compromise with no credentials at all. The fix spans both projects and needs both minimums together: ComfyUI v0.3.76 or later (adds the protected-directory API the fix depends on) and ComfyUI-Manager v3.38 or later (contains the fix itself). Keep both at or above those versions, and only install nodes you trust regardless.

```bash
python main.py --listen 127.0.0.1 --port 8188
```

Front it with a TLS proxy that adds login before anything reaches port 8188. If you must run untrusted workflows, `--disable-all-custom-nodes` starts the server with none of them loaded, and `--whitelist-custom-nodes FOLDER...` re-allows specific folders despite that flag; neither is a substitute for keeping the port off the network.

## AUTOMATIC1111 Stable Diffusion WebUI

`--listen` launches gradio bound to `0.0.0.0` (default `False`, i.e. loopback unless `GRADIO_SERVER_NAME` is set, below); `--port` defaults to `7860`. `--gradio-auth-path FILE` (a file of `user:password` entries, comma-delimited within a line or one per line, at v1.10.1) or `--gradio-auth user:pass` (comma-delimited for multiple users) requires a login before the UI loads; `--api-auth user:pass` does the same for the API. Both `user:pass` forms put the password in the launcher's argv, so use the file for the UI login, below; the API credential's other inputs are not yet traced (backlog row 1.142). The UI forms split each entry once, at its first `:`, so a UI password may contain `:`; `--api-auth` splits each entry at every `:`, so an API password containing `:` makes startup fail. No form allows a `,` in a password, since it separates entries. `--share` registers a public `*.gradio.live` relay URL, documented as intended for Colab, not a deployment mechanism, and it bypasses your network boundary entirely. `--enable-insecure-extension-access` reopens the extensions tab regardless of other flags and should stay off on anything reachable beyond loopback.

Do not put a credential on the command line or in `COMMANDLINE_ARGS`. `--gradio-auth user:pass` sits in argv, where `ps` and `/proc/<pid>/cmdline` show it to other local accounts for the UI's whole lifetime, and quoting does not change that. `COMMANDLINE_ARGS` in the environment is the other way in: at import the WebUI appends its contents to `sys.argv`, and the value stays readable through `/proc/<pid>/environ` by the same account and by root; `webui.sh` sets it from `webui-user.sh`. At startup, v1.10.1's launcher prints `Launching Web UI with arguments:` followed by `shlex.join(sys.argv[1:])`, and `sys.argv` already includes `COMMANDLINE_ARGS` by then, so every `--gradio-auth` and `--api-auth` password, from the command line or from `COMMANDLINE_ARGS`, is echoed in clear text to stdout, and from there into the terminal, `docker logs`, the journal or any log that captures it. `--gradio-auth-path` puts only the path in that line: the WebUI reads the file itself, and at the pinned tag its only reader is the credential loader, which prints nothing. That echo is the reason to use the file, and the reason never to put a credential in `COMMANDLINE_ARGS`. The pinned sources document no stdin input for the login. Create the file once, as the account that runs the WebUI; the block assumes a clean shell:

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set -eC +x +a
  umask 077
  if [ -e "$HOME/.config/stable-diffusion-webui/gradio-auth" ] || [ -L "$HOME/.config/stable-diffusion-webui/gradio-auth" ]; then
    echo 'a gradio-auth file already exists in ~/.config/stable-diffusion-webui; nothing written'; exit 2
  fi
  set -- "$(openssl rand -hex 32)"
  [ "${#1}" -eq 64 ] || { echo 'password generation failed; nothing written'; exit 2; }
  case "$1" in *[!0123456789abcdef]*) echo 'password generation failed; nothing written'; exit 2 ;; esac
  mkdir -p -- "$HOME/.config/stable-diffusion-webui"
  chmod 700 -- "$HOME/.config/stable-diffusion-webui"
  printf 'admin:%s\n' "$1" > "$HOME/.config/stable-diffusion-webui/gradio-auth"
)
```

The block refuses to run when `~/.config/stable-diffusion-webui/gradio-auth` already exists in any form, a dangling symlink included, before it generates anything. `set -C` adds overwrite protection for an existing regular file only, not for every kind of target, and the existence check runs before the write rather than atomically with it, so both hold only in directories that no other account can write to or replace: `$HOME`, `~/.config` and the owner-only directory the block creates. `umask 077` creates the directory mode `0700` and the file mode `0600`, unless the directory, or the parent it is created in, carries a default ACL: new files inherit that ACL in place of the umask, and `chmod 700` on the directory does not remove it. Check with `getfacl` before running the block; backlog row 1.141 tracks making the block refuse that case. The block writes nothing unless the generated password is 64 hex characters, because at v1.10.1 the reader splits each entry once on `:`, so a line of `admin:` would be the user `admin` with an empty password; hex holds no comma or colon for the file format to split on. The password passes only through the subshell's positional parameters and the builtin `printf`, never a command line, and the block clears inherited traps first because a DEBUG, RETURN or ERR trap from your shell could otherwise read it. Read the password back from the file privately when you need it: it is plaintext at rest, readable by that account, by root and by any backup that copies it, so keep it and its backups out of source control ([secrets.md](secrets.md)). A further user is another `user:password` line. Start the WebUI from the file:

```bash
(
  { unset -n COMMANDLINE_ARGS && unset -v COMMANDLINE_ARGS; } 2>/dev/null ||
    { echo 'cannot clear COMMANDLINE_ARGS in this shell; not starting'; exit 2; }
  { unset -n GRADIO_SERVER_NAME && unset -v GRADIO_SERVER_NAME; } 2>/dev/null ||
    { echo 'cannot clear GRADIO_SERVER_NAME in this shell; not starting'; exit 2; }
  f="$HOME/.config/stable-diffusion-webui/gradio-auth"
  { [ -f "$f" ] && [ ! -L "$f" ]; } ||
    { echo 'need ~/.config/stable-diffusion-webui/gradio-auth to be a regular file (it is missing, a symlink or another kind of file); not starting'; exit 2; }
  if grep -Eavqx -- '[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-]+:[0123456789abcdef]{64}' "$f"; then
    echo 'a line in ~/.config/stable-diffusion-webui/gradio-auth is not a user name and a 64-hex password; not starting'; exit 2
  else
    rc=$?; [ "$rc" -eq 1 ] || { echo 'could not check ~/.config/stable-diffusion-webui/gradio-auth; not starting'; exit 2; }
  fi
  if grep -Eaqx -- '[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-]+:[0123456789abcdef]{64}' "$f"; then :; else
    rc=$?; [ "$rc" -eq 1 ] || { echo 'could not check ~/.config/stable-diffusion-webui/gradio-auth; not starting'; exit 2; }
    echo 'no user:password line in ~/.config/stable-diffusion-webui/gradio-auth; not starting'; exit 2
  fi
  d=$(awk -F: 'seen[$1]++ { dup = 1 } END { if (dup) print "duplicate"; else if (NR > 0) print "ok" }' "$f") || d=
  case "$d" in
    ok) ;;
    duplicate) echo 'a user name is on more than one line in ~/.config/stable-diffusion-webui/gradio-auth; not starting'; exit 2 ;;
    *) echo 'could not check ~/.config/stable-diffusion-webui/gradio-auth; not starting'; exit 2 ;;
  esac
  python launch.py --server-name 127.0.0.1 --port 7860 --gradio-auth-path "$HOME/.config/stable-diffusion-webui/gradio-auth"
)
```

Of the login, only the path is on the command line, and only the path appears in the startup line. The block clears `COMMANDLINE_ARGS` first and refuses to start when it cannot (a readonly name in your shell), so an inherited value can add neither `--listen`, `--share` nor a `--gradio-auth` or `--api-auth` password; put any other flag you need on the command line itself. It passes `--server-name 127.0.0.1` explicitly because the loopback default is not the WebUI's own: at v1.10.1, without `--listen` or `--server-name` the WebUI hands Gradio no server name, and Gradio 3.41.2 then binds to `GRADIO_SERVER_NAME` from the environment, falling back to `127.0.0.1` only when it is unset, so an inherited `GRADIO_SERVER_NAME=0.0.0.0` would bind every interface. The block also clears `GRADIO_SERVER_NAME` with the same fail-closed guard. If you start through `webui.sh` instead, keep every credential out of `COMMANDLINE_ARGS` in `webui-user.sh`. The block checks first that the file is a regular file and not a symlink, so a FIFO in its place can neither block the check nor be read by it. It then reads the file as text (`grep -a`: without `-a`, a NUL could make a malformed line look valid to grep) and refuses a file with no login line, with any line that is not a user name and a 64-hex password, the shape the block above writes, or with the same user name on two lines, because Gradio 3.41.2 keeps the logins in a dictionary keyed by user name, so only the last password given for that user would work. The patterns spell out their ASCII character sets rather than ranges such as `a-f`, whose meaning can depend on the locale, and the duplicate check compares names byte for byte. That check passes only when `awk` exits 0 and prints `ok`, which its program does only after reading at least one line and finding no user name twice, so an exit status alone never counts as a pass. When `grep` or `awk` cannot read the file, the block says that it could not check and refuses, and it gives the same result in a shell that has `set -e` on. If you set a password of your own, relax that pattern, but never let a line with an empty password through. The password stays in the file and in the WebUI's memory, readable by that account and by root, and moving it out of argv does not erase a value already in shell history or a log.

Read from the code, not run: at v1.10.1 the WebUI serves `GET /internal/sysinfo` and `GET /internal/sysinfo-download`, which return its system-information report, and that report carries `COMMANDLINE_ARGS` from the environment unredacted, alongside the process's argv. The argv listing hides an element only when it equals the `--gradio-auth` or `--api-auth` value exactly, so the single-token form `--gradio-auth=user:pass` is not hidden, and a password in `COMMANDLINE_ARGS` appears verbatim in the environment section. The two routes are registered with no dependency, and at the Gradio release v1.10.1 pins (3.41.2) the login is checked per route rather than by middleware, so by that reading they answer without a login even when the Gradio login is on. Nobody has yet observed this on a running instance; backlog row 1.143 tracks confirming it. Do three things regardless: use `--gradio-auth-path`, which puts only a path in the report; never put a credential in `COMMANDLINE_ARGS`; and have the reverse proxy refuse every path that begins `/internal/sysinfo`, which covers `/internal/sysinfo-download` too, since the report still carries the rest of the argv and environment.

Even with `--gradio-auth-path` set, put TLS in front; the login alone only gates plaintext HTTP. `--server-name` sets the address the WebUI binds to; the block's `--server-name 127.0.0.1` is that bind address, so change it only when you mean to serve another interface.

## InvokeAI

InvokeAI's `invokeai.yaml` uses a flat schema (current as of InvokeAI 6.14.1, `schema_version: 4.0.2`): `host` (default `127.0.0.1`) and `port` (default `9090`) are top-level keys, not nested under a `Web Server` or `InvokeAI` section. Setting `host: 0.0.0.0` serves the local network with no login at all in the default single-user mode. `INVOKEAI_HOST` and `INVOKEAI_PORT` override the same settings from the environment.

An experimental multi-user mode exists: add `multiuser: true` to `invokeai.yaml` to require per-user login (username and password, stateless JWT sessions), and `strict_password_checking: true` to enforce a minimum password (8+ characters, upper, lower, and a digit) rather than just warning on a weak one. Restarting the server logs every user out. Outside multi-user mode, treat InvokeAI as having no login and keep it on loopback regardless.

```yaml
# invokeai.yaml, flat schema (schema_version 4.0.2, InvokeAI 6.14.1 and later)
host: 127.0.0.1
port: 9090
multiuser: true
strict_password_checking: true
```

## Fooocus

`--listen` exposes the UI to the network (optionally to a specific address); `--port` sets the port; `--share` registers a public `*.gradio.live` endpoint, same relay mechanism and same caution as above. Fooocus's own README states access is unauthenticated by default. Optional basic auth comes from an `auth.json` file with `user`/`pass` entries (no dedicated command-line auth flag exists); use it, but still keep the instance off any public interface.

```json
[
  {"user": "admin", "pass": "REPLACE_WITH_LONG_RANDOM_VALUE"}
]
```

## Verify

```bash
ss -tlnp   # read every listener; 8188/7860/9090: each service on 127.0.0.1 only
# each must be unreachable from another host. Read err, not the number: it must name a refusal or
# timeout reaching YOUR address. An HTTP code means the port answered. A resolver failure, a local
# socket error, or a timeout that did not come from the remote address is inconclusive.
(                                                   # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
    *) for p in 8188 7860 9090; do                              # ComfyUI, SD WebUI, InvokeAI
         curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
           -w "port=$p http=%{http_code} exit=%{exitcode} err=%{errormsg}\n" "http://$1:$p/"
       done ;;
  esac
)
# guard-conventions: allow probe of a fixed loopback target; no reader-substituted placeholder in this probe's argv
curl -q -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:9090/api/v1/boards/
                                                       # from the host itself, InvokeAI multiuser mode: 401
                                                       # without a Bearer token, never the app itself
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -sI https://imagegen.example.com/                # via the proxy: TLS, and a login prompt
                                                       # or 401 without credentials, before the UI loads
```

## Common mistakes

- Adding `--listen`/`host: 0.0.0.0` "just to test from my phone" and forgetting it is still set a week later.
- Treating `--share` (Stable Diffusion WebUI, Fooocus) as a deployment option instead of a short-lived demo link.
- Installing a custom node or extension without reading it, on the assumption that "it's just a UI".
- Relying on the Gradio login (`--gradio-auth-path`) or Fooocus's `auth.json` alone: single-factor credentials over plain HTTP still leak on the wire without a TLS proxy in front.
- Passing `--gradio-auth user:pass` on the command line, where other local accounts can read the password through `ps` for as long as the UI runs and the launcher prints it at startup; or in `COMMANDLINE_ARGS`, where it is held in the environment, readable by the same account and by root, printed at startup the same way, and returned by `/internal/sysinfo` (read from the code, not run).
- Assuming InvokeAI's multi-user mode is on by default; the base install has no login at all, so loopback binding still carries the whole burden.

## Sources (checked September 2026)

- ComfyUI Startup Flags (`--listen`, `--port` defaults): https://docs.comfy.org/development/comfyui-server/startup-flags
- ComfyUI custom node security standards (eval/exec prohibited): https://docs.comfy.org/registry/standards
- ComfyUI 2025 Jan Security Update (custom node code-execution risk): https://blog.comfy.org/p/comfyui-2025-jan-security-update
- ComfyUI-Manager security advisory, CVE-2025-67303, GHSA-95pq-hr8p-f5g7 (both minimum versions): https://github.com/Comfy-Org/ComfyUI-Manager/security/advisories/GHSA-95pq-hr8p-f5g7
- AUTOMATIC1111 Command Line Arguments and Settings wiki: https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Command-Line-Arguments-and-Settings
- AUTOMATIC1111 `--gradio-auth-path` ("set gradio authentication file path"), `--gradio-auth`, `--api-auth` and `--server-name` definitions (pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/cmd_args.py#L87-L113
- AUTOMATIC1111 credential reader: opens `cmd_opts.gradio_auth_path`, splits each line on `,` and each entry once on `:` (pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/initialize_util.py#L114-L139
- AUTOMATIC1111 passes the credential list to Gradio as `auth=` (`list(initialize_util.get_gradio_auth_creds()) or None`; pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/webui.py#L70-L90
- AUTOMATIC1111 `--api-auth` parsing, `auth.split(":")` into a user and a password for each `,`-separated entry (pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/api/api.py#L199-L205
- AUTOMATIC1111 appends `COMMANDLINE_ARGS` from the environment to `sys.argv` (pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/paths_internal.py#L12-L13
- AUTOMATIC1111 launcher prints `shlex.join(sys.argv[1:])` at startup (pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/launch_utils.py#L463-L464
- AUTOMATIC1111 `webui.sh` sources `webui-user.sh` (pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/webui.sh#L18-L23
- AUTOMATIC1111 system-information report: `COMMANDLINE_ARGS` on the environment whitelist, the unredacted environment dump, and the exact-value argv redaction (pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/sysinfo.py#L33 and https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/sysinfo.py#L130-L148
- AUTOMATIC1111 `/internal/sysinfo` and `/internal/sysinfo-download` routes, registered with no dependency (pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/ui.py#L1223-L1232
- AUTOMATIC1111 pins Gradio 3.41.2 and adds only GZip and CORS middleware (pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/requirements_versions.txt#L11 and https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/initialize_util.py#L192-L214
- AUTOMATIC1111 `gradio_server_name()`: `--server-name`, else `0.0.0.0` with `--listen`, else `None` (pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/initialize_util.py#L10-L15
- Gradio 3.41.2 default bind, `LOCALHOST_NAME = os.getenv("GRADIO_SERVER_NAME", "127.0.0.1")` and `server_name = server_name or LOCALHOST_NAME` (pinned tag gradio@3.41.2): https://github.com/gradio-app/gradio/blob/gradio@3.41.2/gradio/networking.py#L28 and https://github.com/gradio-app/gradio/blob/gradio@3.41.2/gradio/networking.py#L120
- Gradio 3.41.2 checks the login per route, with `dependencies=[Depends(login_check)]` (pinned tag gradio@3.41.2): https://github.com/gradio-app/gradio/blob/gradio@3.41.2/gradio/routes.py#L193-L305
- Gradio 3.41.2 turns a list `auth` into a dictionary keyed by user name, so a later password for the same user name replaces an earlier one (pinned tag gradio@3.41.2): https://github.com/gradio-app/gradio/blob/gradio@3.41.2/gradio/routes.py#L128-L133
- InvokeAI YAML Config (host/port defaults): https://invoke.ai/configuration/invokeai-yaml/
- InvokeAI Multi-User Administrator Guide: https://invoke.ai/features/multi-user-mode/admin-guide/
- Fooocus repository README (`--listen`, `--share`, auth.json): https://github.com/lllyasviel/Fooocus
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0): https://curl.se/docs/manpage.html
- ComfyUI `--listen` default `127.0.0.1`, `0.0.0.0,::` when given without a value, and `--port` default `8188` (pinned tag v0.37.0): https://github.com/Comfy-Org/ComfyUI/blob/v0.37.0/comfy/cli_args.py#L63-L64
