---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "9cc7be319ef697fe33979310e2e75763e536a36da7b5acc86dc234ecadd52a05",
  "components": {
    "comfy": {
      "name": "ComfyUI",
      "basis": "v0.37.0",
      "sources": {
        "sbd178d58a098": "https://github.com/Comfy-Org/ComfyUI/blob/v0.37.0/comfy/cli_args.py#L63-L64",
        "s8b2f213483c1": "https://docs.comfy.org/development/comfyui-server/startup-flags",
        "sfde3f2261e67": "https://blog.comfy.org/p/comfyui-2025-jan-security-update",
        "sb5912e72af4b": "https://docs.comfy.org/registry/standards"
      }
    },
    "webui": {
      "name": "AUTOMATIC1111",
      "basis": "v1.10.1",
      "sources": {
        "s42a42cca605b": "https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/cmd_args.py#L87-L113",
        "s0195caed3cb9": "https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/initialize_util.py#L114-L139",
        "sd5f3496b66aa": "https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/webui.py#L70-L90",
        "s82803810022a": "https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/cmd_args.py#L6",
        "s914278bcbf70": "https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/shared_cmd_options.py#L7-L15",
        "s66a044b7666c": "https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/api/api.py#L199-L205",
        "sb59e633133f6": "https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/api/api.py#L274-L284",
        "s57d98254f09d": "https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/api/api.py#L689-L690",
        "s256946a60534": "https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/api/models.py#L221-L231",
        "s5b2e23d1781d": "https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/paths_internal.py#L12-L13",
        "sfa27f3a86456": "https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/launch_utils.py#L463-L464",
        "sebe977aeb6f3": "https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/sysinfo.py#L130-L148",
        "sc9117bccdef5": "https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/ui.py#L1223-L1232",
        "sd9d51e2b2963": "https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/initialize_util.py#L10-L15",
        "saf69abeba189": "https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/requirements_versions.txt#L11",
        "sf3f6d5cafad0": "https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/shared_init.py#L17-L24",
        "sbfd3d01539c3": "https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/ui_loadsave.py#L14-L73"
      }
    },
    "gradio": {
      "name": "Gradio",
      "basis": "3.41.2",
      "sources": {
        "s1bd30a313ec9": "https://github.com/gradio-app/gradio/blob/gradio@3.41.2/gradio/networking.py#L28",
        "sf85e6083e02e": "https://github.com/gradio-app/gradio/blob/gradio@3.41.2/gradio/routes.py#L193-L305",
        "s2ec1c2a1d665": "https://github.com/gradio-app/gradio/blob/gradio@3.41.2/gradio/routes.py#L128-L133",
        "s6f6c16695b71": "https://github.com/gradio-app/gradio/blob/gradio%403.41.2/gradio/networking.py#L24-L27",
        "s67ebd44760a7": "https://github.com/gradio-app/gradio/blob/gradio%403.41.2/gradio/networking.py#L133-L171"
      }
    },
    "invoke": {
      "name": "InvokeAI",
      "basis": "6.14.1",
      "sources": {
        "sb0dc1b679ef2": "https://invoke.ai/configuration/invokeai-yaml/",
        "s23a1a14da479": "https://invoke.ai/features/multi-user-mode/admin-guide/",
        "s4c6175f3800d": "https://invoke.ai/features/multi-user-mode/api-guide/"
      }
    },
    "fooocus": {
      "name": "Fooocus",
      "basis": "v2.5.5",
      "sources": {
        "s38232435e83d": "https://github.com/lllyasviel/Fooocus/blob/v2.5.5/readme.md#L296-L301",
        "s63ce6f5a8fa9": "https://github.com/lllyasviel/Fooocus/blob/v2.5.5/ldm_patched/modules/args_parser.py#L36",
        "sca9aed72a579": "https://github.com/lllyasviel/Fooocus/blob/v2.5.5/args_manager.py#L43-L47",
        "s456b2a263c88": "https://github.com/lllyasviel/Fooocus/blob/v2.5.5/launch.py#L13-L14",
        "s2eb7ac87bb1f": "https://github.com/lllyasviel/Fooocus/blob/v2.5.5/webui.py#L1120-L1128",
        "s35ce6e657cb8": "https://github.com/lllyasviel/Fooocus/blob/v2.5.5/entry_with_update.py#L16-L46",
        "s6157fae93872": "https://github.com/lllyasviel/Fooocus/blob/v2.5.5/Dockerfile#L17-L29",
        "s5c792b662186": "https://github.com/lllyasviel/Fooocus/blob/v2.5.5/entrypoint.sh#L33",
        "s79380d927e3b": "https://github.com/lllyasviel/Fooocus/blob/v2.5.5/docker-compose.yml#L6-L11",
        "s431336fa6375": "https://github.com/lllyasviel/Fooocus/blob/v2.5.5/docker.md#L19-L78",
        "scb18d8c421f5": "https://github.com/lllyasviel/Fooocus/blob/v2.5.5/.dockerignore#L53",
        "s170da4e26268": "https://github.com/lllyasviel/Fooocus/blob/v2.5.5/modules/auth.py#L8-L16",
        "s21eb28118a14": "https://github.com/lllyasviel/Fooocus/blob/v2.5.5/modules/auth.py#L19-L34",
        "sfcc14904297e": "https://github.com/lllyasviel/Fooocus/blob/v2.5.5/modules/auth.py#L37-L41",
        "s2ef62a4cd853": "https://github.com/lllyasviel/Fooocus/blob/v2.5.5/launch.py#L7-L9",
        "sc90edaf29ac7": "https://github.com/lllyasviel/Fooocus/blob/v2.5.5/requirements_versions.txt#L13"
      }
    },
    "engine": {
      "name": "Docker Engine minimum loopback boundary",
      "basis": "28.0",
      "sources": {
        "s1e53417c513d": "https://docs.docker.com/engine/network/port-publishing/"
      }
    },
    "compose": {
      "name": "Compose Specification",
      "basis": "914ec15d1fa4",
      "sources": {
        "sfb1cd5e15347": "https://github.com/compose-spec/compose-spec/blob/914ec15d1fa498969c0df5c1d672306db3256089/05-services.md#L1816-L1832",
        "s2d25c00e22f6": "https://github.com/compose-spec/compose-spec/blob/914ec15d1fa498969c0df5c1d672306db3256089/build.md#L21-L23",
        "s16a4e1bb5e9f": "https://github.com/compose-spec/compose-spec/blob/914ec15d1fa498969c0df5c1d672306db3256089/build.md#L50-L62"
      }
    },
    "compose-cli": {
      "name": "Docker Compose source",
      "basis": "v2.32.4",
      "sources": {
        "s0e2ca4d9b8c0": "https://github.com/docker/compose/blob/v2.32.4/cmd/compose/up.go#L147"
      }
    },
    "curl": {
      "name": "curl minimum write-out version",
      "basis": "7.75.0",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    },
    "comfy-min": {
      "name": "ComfyUI advisory minimum",
      "basis": "v0.3.76",
      "sources": {
        "s4ce66189c3c9": "https://github.com/Comfy-Org/ComfyUI-Manager/security/advisories/GHSA-95pq-hr8p-f5g7"
      }
    },
    "manager-min": {
      "name": "ComfyUI-Manager advisory minimum",
      "basis": "v3.38",
      "sources": {
        "s4ce66189c3c9": "https://github.com/Comfy-Org/ComfyUI-Manager/security/advisories/GHSA-95pq-hr8p-f5g7"
      }
    }
  },
  "claims": {
    "comfy-bind": {"text": "Default loopback:8188, bare --listen binds IPv4/IPv6 wildcards; explicit bind/port and proxy login.", "components": ["comfy"], "sources": ["comfy:sbd178d58a098", "comfy:s8b2f213483c1"], "status": "REASONED"},
    "comfy-nodes": {"text": "ComfyUI has no built-in login; Python custom nodes run with server privileges. Trust nodes and apply container containment.", "components": ["comfy"], "sources": ["comfy:sfde3f2261e67", "comfy:sb5912e72af4b", "comfy:s8b2f213483c1"], "status": "REASONED"},
    "fooocus-login": {"text": "Fooocus is unauthenticated by default and offers optional auth.json login; keep it off public interfaces.", "components": ["fooocus"], "sources": ["fooocus:s38232435e83d"], "status": "REASONED"},
    "manager": {"text": "Manager RCE advisory requires ComfyUI at least v0.3.76 and Manager at least v3.38 together.", "components": ["comfy-min", "manager-min"], "sources": ["comfy-min:s4ce66189c3c9", "manager-min:s4ce66189c3c9"], "status": "REASONED"},
    "node-flags": {"text": "--disable-all-custom-nodes and --whitelist-custom-nodes limit loaded nodes, not network exposure.", "components": ["comfy"], "sources": ["comfy:s8b2f213483c1"], "status": "REASONED"},
    "webui-auth": {"text": "UI auth file/list syntax, API-only auth, colon/comma parsing differences and plaintext HTTP require a TLS proxy.", "components": ["webui"], "sources": ["webui:s42a42cca605b", "webui:s0195caed3cb9", "webui:sd5f3496b66aa", "webui:s66a044b7666c"], "status": "REASONED"},
    "webui-flags": {"text": "--listen, port 7860, --share relay and insecure extension access affect exposure.", "components": ["webui"], "sources": ["webui:s42a42cca605b"], "status": "REASONED"},
    "api-input": {"text": "API credentials have no shipped stdin/file/environment/prompt input; settings and UI config do not populate api_auth.", "components": ["webui"], "sources": ["webui:s82803810022a", "webui:s914278bcbf70", "webui:sb59e633133f6", "webui:sf3f6d5cafad0", "webui:sbfd3d01539c3"], "status": "REASONED"},
    "api-leak": {"text": "cmd-flags reveals all options; API auth users can read API passwords, unauthenticated API can expose UI argv credentials.", "components": ["webui"], "sources": ["webui:sb59e633133f6", "webui:s57d98254f09d", "webui:s256946a60534"], "status": "REASONED"},
    "argv": {"text": "COMMANDLINE_ARGS becomes argv; launcher prints credentials and local argv/environment readers may read them.", "components": ["webui"], "sources": ["webui:s914278bcbf70", "webui:s5b2e23d1781d", "webui:sfa27f3a86456"], "status": "REASONED"},
    "file-create": {"text": "Create-once owner-only credential file uses hex password and clean-shell guards; ACLs, directory races, backups and plaintext storage limit protection. Shell/filesystem versions are unrecorded.", "components": ["webui"], "sources": ["webui:s0195caed3cb9"], "status": "REASONED"},
    "file-launch": {"text": "Clear inherited launch/bind variables, validate regular non-symlink credential file, reject empty/malformed/duplicate entries and read failures. Shell/grep/awk versions are unrecorded.", "components": ["webui", "gradio"], "sources": ["webui:s0195caed3cb9", "gradio:s2ec1c2a1d665"], "status": "REASONED"},
    "webui-bind": {"text": "Explicit --server-name overrides Gradio environment-based bind; without it GRADIO_SERVER_NAME can replace loopback.", "components": ["webui", "gradio"], "sources": ["webui:sd9d51e2b2963", "webui:saf69abeba189", "gradio:s1bd30a313ec9"], "status": "REASONED"},
    "sysinfo": {"text": "Unredacted environment and incomplete argv redaction in unauthenticated sysinfo routes are source-reasoned; proxy must deny the prefix.", "components": ["webui", "gradio"], "sources": ["webui:sebe977aeb6f3", "webui:sc9117bccdef5", "gradio:sf85e6083e02e"], "status": "REASONED"},
    "invoke-config": {"text": "Flat schema 4.0.2, host 127.0.0.1, port 9090 and INVOKEAI_HOST/PORT overrides; default single-user mode has no login.", "components": ["invoke"], "sources": ["invoke:sb0dc1b679ef2"], "status": "REASONED"},
    "invoke-login": {"text": "Experimental multiuser login/JWT and strict password checks; changing the stored JWT secret then restarting logs users out. Ordinary restart logout is not established; keep loopback and TLS.", "components": ["invoke"], "sources": ["invoke:s23a1a14da479"], "status": "REASONED"},
    "fooocus-flags": {"text": "Loopback by default, bare --listen wildcard, --share public relay; auth.json supplies optional login.", "components": ["fooocus"], "sources": ["fooocus:s38232435e83d", "fooocus:s63ce6f5a8fa9"], "status": "REASONED"},
    "fooocus-loader": {"text": "Isolated loader returns credentials only for valid data; unreadable raises PermissionError, malformed/empty returns none.", "components": ["fooocus"], "sources": ["fooocus:s21eb28118a14"], "status": "DEMONSTRATED", "evidence": "for a malformed file it printed `load_auth_data, e: ...` and returned no credentials; for an empty list (`[]`) it also returned none; and for a valid file it returned credentials."},
    "fooocus-auth": {"text": "Relative auth.json location, pass/hash SHA-256 handling, permissions and expected fail-open for malformed/empty data; no live server test.", "components": ["fooocus"], "sources": ["fooocus:s2eb7ac87bb1f", "fooocus:s170da4e26268", "fooocus:s21eb28118a14", "fooocus:sfcc14904297e", "fooocus:s2ef62a4cd853"], "status": "REASONED"},
    "fooocus-port": {"text": "Fooocus v2.5.5 pins Gradio 3.41.2; inherited port or occupied 7865 can move the UI; explicit --port makes Gradio try only that port.", "components": ["fooocus", "gradio"], "sources": ["fooocus:sca9aed72a579", "fooocus:s456b2a263c88", "gradio:s6f6c16695b71", "gradio:s67ebd44760a7", "fooocus:sc90edaf29ac7"], "status": "REASONED"},
    "fooocus-pin": {"text": "entry_with_update updates the checkout; use launch.py from exact v2.5.5, with working-tree caveat.", "components": ["fooocus"], "sources": ["fooocus:s35ce6e657cb8"], "status": "REASONED"},
    "container": {"text": "CMDARGS bare --listen plus wildcard publication exposes image; bridge uses internal wildcard and loopback publish, host networking needs loopback bind.", "components": ["fooocus", "engine"], "sources": ["fooocus:s6157fae93872", "fooocus:s5c792b662186", "fooocus:s79380d927e3b", "fooocus:s431336fa6375", "engine:s1e53417c513d"], "status": "REASONED"},
    "image-build": {"text": "Build pinned source, not unchecked GHCR default; Compose build/image pull policy and --build determine selected/tagged image.", "components": ["fooocus", "compose", "compose-cli"], "sources": ["fooocus:s79380d927e3b", "fooocus:s431336fa6375", "compose:sfb1cd5e15347", "compose:s2d25c00e22f6", "compose:s16a4e1bb5e9f", "compose-cli:s0e2ca4d9b8c0"], "status": "REASONED"},
    "auth-mount": {"text": "Image excludes auth.json; mount read-only, use built image user UID and mode 0400; remapped/rootless ownership is unchecked.", "components": ["fooocus"], "sources": ["fooocus:s6157fae93872", "fooocus:scb18d8c421f5", "fooocus:s21eb28118a14"], "status": "REASONED"},
    "argparse": {"text": "Isolated argparse definition yields loopback with no flag and wildcard for bare --listen; this is not a server demonstration.", "components": ["fooocus"], "sources": ["fooocus:s63ce6f5a8fa9"], "status": "DEMONSTRATED", "evidence": "returns `127.0.0.1` with no flag and `0.0.0.0` for a bare `--listen`."},
    "verify-network": {"text": "Inventory every service and port, confirm loopback service is up, probe actual IPv4/IPv6; container PORTS or host-network ss have different scope.", "components": ["comfy", "webui", "invoke", "fooocus", "engine", "curl"], "sources": ["comfy:sbd178d58a098", "webui:sd9d51e2b2963", "invoke:sb0dc1b679ef2", "fooocus:s63ce6f5a8fa9", "engine:s1e53417c513d", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-invoke": {"text": "Unauthenticated /api/v1/boards/ should answer in single-user mode and reject with 401 in multi-user mode; exposed status is unrecorded and no listener demonstration was available.", "components": ["invoke"], "sources": ["invoke:s23a1a14da479", "invoke:s4c6175f3800d"], "status": "REASONED", "verify": [1]},
    "verify-proxy": {"text": "TLS/header and browser checks should require login before UI; no service/proxy listeners were run.", "components": ["comfy", "fooocus"], "sources": ["comfy:s8b2f213483c1", "fooocus:s38232435e83d"], "status": "REASONED", "verify": [1]}
  }
}
---
# Image-generation UIs: ComfyUI, Stable Diffusion WebUI, InvokeAI, Fooocus

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| comfy-bind: Default loopback:8188, bare --listen binds IPv4/IPv6 wildcards; explicit bind/port and proxy login. | ComfyUI v0.37.0 | REASONED |
| comfy-nodes: ComfyUI has no built-in login; Python custom nodes run with server privileges. Trust nodes and apply container containment. | ComfyUI v0.37.0 | REASONED |
| fooocus-login: Fooocus is unauthenticated by default and offers optional auth.json login; keep it off public interfaces. | Fooocus v2.5.5 | REASONED |
| manager: Manager RCE advisory requires ComfyUI at least v0.3.76 and Manager at least v3.38 together. | ComfyUI advisory minimum v0.3.76; ComfyUI-Manager advisory minimum v3.38 | REASONED |
| node-flags: --disable-all-custom-nodes and --whitelist-custom-nodes limit loaded nodes, not network exposure. | ComfyUI v0.37.0 | REASONED |
| webui-auth: UI auth file/list syntax, API-only auth, colon/comma parsing differences and plaintext HTTP require a TLS proxy. | AUTOMATIC1111 v1.10.1 | REASONED |
| webui-flags: --listen, port 7860, --share relay and insecure extension access affect exposure. | AUTOMATIC1111 v1.10.1 | REASONED |
| api-input: API credentials have no shipped stdin/file/environment/prompt input; settings and UI config do not populate api_auth. | AUTOMATIC1111 v1.10.1 | REASONED |
| api-leak: cmd-flags reveals all options; API auth users can read API passwords, unauthenticated API can expose UI argv credentials. | AUTOMATIC1111 v1.10.1 | REASONED |
| argv: COMMANDLINE_ARGS becomes argv; launcher prints credentials and local argv/environment readers may read them. | AUTOMATIC1111 v1.10.1 | REASONED |
| file-create: Create-once owner-only credential file uses hex password and clean-shell guards; ACLs, directory races, backups and plaintext storage limit protection. Shell/filesystem versions are unrecorded. | AUTOMATIC1111 v1.10.1 | REASONED |
| file-launch: Clear inherited launch/bind variables, validate regular non-symlink credential file, reject empty/malformed/duplicate entries and read failures. Shell/grep/awk versions are unrecorded. | AUTOMATIC1111 v1.10.1; Gradio 3.41.2 | REASONED |
| webui-bind: Explicit --server-name overrides Gradio environment-based bind; without it GRADIO_SERVER_NAME can replace loopback. | AUTOMATIC1111 v1.10.1; Gradio 3.41.2 | REASONED |
| sysinfo: Unredacted environment and incomplete argv redaction in unauthenticated sysinfo routes are source-reasoned; proxy must deny the prefix. | AUTOMATIC1111 v1.10.1; Gradio 3.41.2 | REASONED |
| invoke-config: Flat schema 4.0.2, host 127.0.0.1, port 9090 and INVOKEAI_HOST/PORT overrides; default single-user mode has no login. | InvokeAI 6.14.1 | REASONED |
| invoke-login: Experimental multiuser login/JWT and strict password checks; changing the stored JWT secret then restarting logs users out. Ordinary restart logout is not established; keep loopback and TLS. | InvokeAI 6.14.1 | REASONED |
| fooocus-flags: Loopback by default, bare --listen wildcard, --share public relay; auth.json supplies optional login. | Fooocus v2.5.5 | REASONED |
| fooocus-loader: Isolated loader returns credentials only for valid data; unreadable raises PermissionError, malformed/empty returns none. | Fooocus v2.5.5 | DEMONSTRATED |
| fooocus-auth: Relative auth.json location, pass/hash SHA-256 handling, permissions and expected fail-open for malformed/empty data; no live server test. | Fooocus v2.5.5 | REASONED |
| fooocus-port: Fooocus v2.5.5 pins Gradio 3.41.2; inherited port or occupied 7865 can move the UI; explicit --port makes Gradio try only that port. | Fooocus v2.5.5; Gradio 3.41.2 | REASONED |
| fooocus-pin: entry_with_update updates the checkout; use launch.py from exact v2.5.5, with working-tree caveat. | Fooocus v2.5.5 | REASONED |
| container: CMDARGS bare --listen plus wildcard publication exposes image; bridge uses internal wildcard and loopback publish, host networking needs loopback bind. | Fooocus v2.5.5; Docker Engine minimum loopback boundary 28.0 | REASONED |
| image-build: Build pinned source, not unchecked GHCR default; Compose build/image pull policy and --build determine selected/tagged image. | Fooocus v2.5.5; Compose Specification 914ec15d1fa4; Docker Compose source v2.32.4 | REASONED |
| auth-mount: Image excludes auth.json; mount read-only, use built image user UID and mode 0400; remapped/rootless ownership is unchecked. | Fooocus v2.5.5 | REASONED |
| argparse: Isolated argparse definition yields loopback with no flag and wildcard for bare --listen; this is not a server demonstration. | Fooocus v2.5.5 | DEMONSTRATED |
| verify-network: Inventory every service and port, confirm loopback service is up, probe actual IPv4/IPv6; container PORTS or host-network ss have different scope. | ComfyUI v0.37.0; AUTOMATIC1111 v1.10.1; InvokeAI 6.14.1; Fooocus v2.5.5; Docker Engine minimum loopback boundary 28.0; curl minimum write-out version 7.75.0 | REASONED |
| verify-invoke: Unauthenticated /api/v1/boards/ should answer in single-user mode and reject with 401 in multi-user mode; exposed status is unrecorded and no listener demonstration was available. | InvokeAI 6.14.1 | REASONED |
| verify-proxy: TLS/header and browser checks should require login before UI; no service/proxy listeners were run. | ComfyUI v0.37.0; Fooocus v2.5.5 | REASONED |
<!-- version-basis:end -->

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

`--listen` launches gradio bound to `0.0.0.0` (default `False`, i.e. loopback unless `GRADIO_SERVER_NAME` is set, below); `--port` defaults to `7860`. `--gradio-auth-path FILE` (a file of `user:password` entries, comma-delimited within a line or one per line, at v1.10.1) or `--gradio-auth user:pass` (comma-delimited for multiple users) requires a login before the UI loads; `--api-auth user:pass` does the same for the API. Both `user:pass` forms put the password in the launcher's argv, so use the file for the UI login and an authenticating reverse proxy for the API, below. The UI forms split each entry once, at its first `:`, so a UI password may contain `:`; `--api-auth` splits each entry at every `:`, so an API password containing `:` makes startup fail. No form allows a `,` in a password, since it separates entries. `--share` registers a public `*.gradio.live` relay URL, documented as intended for Colab, not a deployment mechanism, and it bypasses your network boundary entirely. `--enable-insecure-extension-access` reopens the extensions tab regardless of other flags and should stay off on anything reachable beyond loopback.

At v1.10.1, the shipped WebUI has no stdin, direct environment, file, argument-file or prompt input for the API credential. This is CONTRIBUTING rule 7's third-exception finding, read from the code, not a live demonstration. A whole-tree search for `api_auth`, `api-auth` and `self.credentials`, followed through every assignment and use of the parsed value and credential dictionary, found only the string option in `cmd_args.py`, the `sys.argv` parser in `shared_cmd_options.py`, its alias in `shared.py`, the API credential loader and authentication dependency, and the sysinfo redactor. The generic `get_cmd_flags()` reader returns the namespace; it does not set credentials. The parser has no `fromfile_prefix_chars`, so `@file` cannot supply arguments; `--gradio-auth-path` feeds only the UI login. `config.json` and the settings API populate `shared.opts`, and `ui-config.json` restores component properties, not `cmd_opts.api_auth`. `COMMANDLINE_ARGS` still becomes `sys.argv`, as below. The pinned source trace is in Sources. The API also returns these values: `GET /sdapi/v1/cmd-flags` answers with every command-line option, because its response model is built from the whole argument parser. With `--api-auth`, any account that authenticates to the API reads every configured API user's password there; with `--api` enabled and no `--api-auth`, the API routes need no credentials, so anyone who reaches the API reads a `--gradio-auth` password the same way. `--gradio-auth-path` exposes only the path. Read from the code, not run.

An API credential supplied on the command line stays in argv for the process's lifetime, exposed to local argv readers and potentially retained by command-line auditing; the launcher also prints it at startup. Do not enable `--api-auth` on a host where other accounts or processes could read argv. The alternative is an authenticating TLS reverse proxy protecting every `/sdapi/v1/*` route in front of an explicit loopback bind (`--server-name 127.0.0.1`), following [fronting-auth.md](fronting-auth.md). The Gradio credential file does not protect the API: without `--api-auth`, the API registers its routes without its authentication dependency, so the proxy must enforce authentication before forwarding them.

Do not put a credential on the command line or in `COMMANDLINE_ARGS`. `--gradio-auth user:pass` sits in argv, where `ps` and `/proc/<pid>/cmdline` show it to other local accounts for the UI's whole lifetime, and quoting does not change that. `COMMANDLINE_ARGS` in the environment is the other way in: at import the WebUI appends its contents to `sys.argv`, and the value stays readable through `/proc/<pid>/environ` by the same account and by root; `webui.sh` sets it from `webui-user.sh`. At startup, v1.10.1's launcher prints `Launching Web UI with arguments:` followed by `shlex.join(sys.argv[1:])`, and `sys.argv` already includes `COMMANDLINE_ARGS` by then, so every `--gradio-auth` and `--api-auth` password, from the command line or from `COMMANDLINE_ARGS`, is echoed in clear text to stdout, and from there into the terminal, `docker logs`, the journal or any log that captures it. `--gradio-auth-path` puts only the path in that line: the WebUI reads the file itself, and at the pinned tag its only reader is the credential loader, which prints nothing. That echo is the reason to use the file, and the reason never to put a credential in `COMMANDLINE_ARGS`. The pinned sources document no stdin input for the login. Create the file once, as the account that runs the WebUI; the block assumes a clean shell:

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set -eC
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

Read from the code, not run: at v1.10.1 the WebUI serves `GET /internal/sysinfo` and `GET /internal/sysinfo-download`, which return its system-information report, and that report carries `COMMANDLINE_ARGS` from the environment unredacted, alongside the process's argv. The argv listing hides an element only when it equals the `--gradio-auth` or `--api-auth` value exactly, so neither single-token form `--gradio-auth=user:pass` nor `--api-auth=user:pass` is hidden, and a password in `COMMANDLINE_ARGS` appears verbatim in the environment section. The two routes are registered with no dependency, and at the Gradio release v1.10.1 pins (3.41.2) the login is checked per route rather than by middleware, so by that reading they answer without a login even when the Gradio login is on. Nobody has yet observed this on a running instance; backlog row 1.143 tracks confirming it. Do three things regardless: use `--gradio-auth-path`, which puts only a path in the report; never put a credential in `COMMANDLINE_ARGS`; and have the reverse proxy refuse every path that begins `/internal/sysinfo`, which covers `/internal/sysinfo-download` too, since the report still carries the rest of the argv and environment.

Even with `--gradio-auth-path` set, put TLS in front; the login alone only gates plaintext HTTP. `--server-name` sets the address the WebUI binds to; the block's `--server-name 127.0.0.1` is that bind address, so change it only when you mean to serve another interface.

## InvokeAI

InvokeAI's `invokeai.yaml` uses a flat schema (current as of InvokeAI 6.14.1, `schema_version: 4.0.2`): `host` (default `127.0.0.1`) and `port` (default `9090`) are top-level keys, not nested under a `Web Server` or `InvokeAI` section. Setting `host: 0.0.0.0` serves the local network with no login at all in the default single-user mode. `INVOKEAI_HOST` and `INVOKEAI_PORT` override the same settings from the environment.

An experimental multi-user mode exists: add `multiuser: true` to `invokeai.yaml` to require per-user login (username and password, stateless JWT sessions), and `strict_password_checking: true` to enforce a minimum password (8+ characters, upper, lower, and a digit) rather than just warning on a weak one. The JWT secret persists in the database. The [administrator guide](https://invoke.ai/features/multi-user-mode/admin-guide/#secret-key-management) instructs administrators to change that secret and then restart to log every user out; it does not establish logout on an ordinary restart. Outside multi-user mode, treat InvokeAI as having no login and keep it on loopback regardless.

```yaml
# invokeai.yaml, flat schema (schema_version 4.0.2, InvokeAI 6.14.1 and later)
host: 127.0.0.1
port: 9090
multiuser: true
strict_password_checking: true
```

## Fooocus

`--listen` with no argument binds to `0.0.0.0` (every IPv4 interface); given an address it binds only there, and with the flag absent Fooocus binds `127.0.0.1` (all as of v2.5.5). `--port` sets the port, which is `7865` by default, unless `GRADIO_SERVER_PORT` is set or 7865 is taken (below). `--share` registers a public `*.gradio.live` endpoint, same relay mechanism and same caution as above. Fooocus's own README states access is unauthenticated by default. Optional basic auth comes from an `auth.json` file with `user`/`pass` entries (no dedicated command-line auth flag exists); use it, but still keep the instance off any public interface.

```json
[
  {"user": "admin", "pass": "REPLACE_WITH_LONG_RANDOM_VALUE"}
]
```

Fooocus reads `auth.json` by a relative name from the checkout root, the directory `launch.py` changes into, so outside a container put the file next to `launch.py`, owned by the account that runs Fooocus, with mode `0400`. `auth.py` also accepts a `hash` entry in place of `pass`: the lowercase hex SHA-256 of the password. Its `auth_list_to_dict` (`auth.py:8-16`) stores `hash` as given and turns `pass` into that same digest, and its `check_auth` (`auth.py:37-41`) compares the hex SHA-256 of the password typed at login with the stored value, so a `hash` entry keeps the plaintext password out of the file. Check for the login prompt after every start rather than trusting that the file is present. Run on its own with no server started, the v2.5.5 loader (`load_auth_data`) raised `PermissionError` for a file it could not open, because its `open()` sits outside its `try`; for a malformed file it printed `load_auth_data, e: ...` and returned no credentials; for an empty list (`[]`) it also returned none; and for a valid file it returned credentials. From the launch call, which passes a login to gradio only when the loader returned credentials, an unreadable file should stop Fooocus before the UI starts, while a malformed file or an empty list should start the UI with no login. That last step is read from the source, not observed: no Fooocus server was run.

Pass the port explicitly as well as the bind. Fooocus hands gradio no port of its own: `launch.py` sets `GRADIO_SERVER_PORT` to `7865` only when that variable is not already set, so a `GRADIO_SERVER_PORT` inherited from your shell, a service unit or a container's environment moves the UI to whatever port it names. With no port passed, gradio 3.41.2 (the version Fooocus v2.5.5 pins) tries that value and then each port above it in turn, up to 100 ports by default, so a 7865 already in use moves the UI to a higher port with no error. `--port 7865` makes gradio try that port alone and fail to start if it is taken, which keeps the UI where your firewall rules and the Verify probe below expect it. `--listen 127.0.0.1` restates the default, so the launch line records the bind.

Start Fooocus with `launch.py` rather than the README's `entry_with_update.py`. The updater fetches `origin` and, when the checked-out branch can fast-forward to the remote branch of the same name, moves the branch to that commit and hard-resets the working tree before it imports `launch.py`, so a version you pinned on a branch does not stay pinned. `launch.py` is the same program without that step, and it is what the upstream container image runs. Clone the pinned tag:

```bash
git clone --branch v2.5.5 https://github.com/lllyasviel/Fooocus.git
```

After preparing the environment as the README describes, start it from the pinned checkout. The block starts Fooocus only when the checkout's HEAD is exactly the `v2.5.5` tag, and `./Fooocus` keeps a `CDPATH` in your shell from moving it elsewhere. It does not check the working tree, so if the clone printed an error, delete `./Fooocus` and clone again before starting:

```bash
(
  cd ./Fooocus || { echo 'no ./Fooocus checkout here; not starting'; exit 2; }
  [ "$(git describe --tags --exact-match 2>/dev/null)" = v2.5.5 ] ||
    { echo 'this is not the pinned v2.5.5 checkout; not starting'; exit 2; }
  python launch.py --listen 127.0.0.1 --port 7865
)
```

The upstream container image sets `ENV CMDARGS --listen` in its Dockerfile, and its `docker-compose.yml` and the `docker run` and `podman run` examples in its `docker.md` set `CMDARGS=--listen` again, so inside the container Fooocus binds `0.0.0.0`. Each of them also publishes `7865:7865` with no host address; Docker binds such a publication on every host address, `0.0.0.0` and `[::]` (this guide has not checked Podman's default). On a bridge network the wildcard inside the container is what lets a published port reach the UI, and it also lets any container on the same network reach it, with no login unless a valid `auth.json` is mounted (below). Keep the wildcard inside the container, publish to loopback only, and state the arguments: in the `docker run` and `podman run` examples, replace `-p 7865:7865` with `-p 127.0.0.1:7865:7865` and `-e CMDARGS=--listen` with `-e CMDARGS='--listen 0.0.0.0 --port 7865'`; in `docker-compose.yml`, make the `ports` entry `"127.0.0.1:7865:7865"` and the `CMDARGS` entry `CMDARGS=--listen 0.0.0.0 --port 7865`. Under host networking (`--network host`) nothing is published and the container's wildcard is the host's, so set `CMDARGS` to `--listen 127.0.0.1 --port 7865` there instead. A loopback publication is a reliable boundary only on Docker Engine 28.0 and later; see [docker.md](docker.md#1-publish-nothing-except-the-tls-proxy).

Build the image from the pinned checkout and run that local build, not the GHCR image. The upstream `docker-compose.yml` names both `build: .` and `image: ghcr.io/lllyasviel/fooocus`, so Compose may run the GHCR image it pulls rather than a build of your checkout, and the `docker run` example in the upstream `docker.md` runs `ghcr.io/lllyasviel/fooocus`; this guide has not checked that image's default tag against v2.5.5. With Compose, start it with `docker compose up --build`, or add `pull_policy: build` to the service so that every `docker compose up` builds it; the service keeps `image: ghcr.io/lllyasviel/fooocus`, so Compose tags its local build `ghcr.io/lllyasviel/fooocus`, not `fooocus`. With `docker run`, build it with `docker build . -t fooocus`, as the upstream `docker.md` describes, which tags the build `fooocus`, and run `fooocus` in place of `ghcr.io/lllyasviel/fooocus`.

The image build excludes `auth.json`, so mount it read-only at `/content/app/auth.json`: `-v /srv/fooocus/auth.json:/content/app/auth.json:ro` with `docker run`, or `- /srv/fooocus/auth.json:/content/app/auth.json:ro` under the service's `volumes:` in `docker-compose.yml`. Fooocus runs in the image as its unprivileged `user` account, so the host file must be owned by that account's uid and readable by no other account. Read the uid from the image you built: on the `docker build . -t fooocus` path, `docker run --rm --entrypoint id fooocus -u user` prints it; on the Compose path, run `docker compose build` and then `docker run --rm --entrypoint id ghcr.io/lllyasviel/fooocus -u user`, which reads the local build Compose tagged with that name. Then `sudo chown` the file to that uid and `sudo chmod 0400` it. Read from the source and not observed on a running server (above), an unreadable file should stop Fooocus from starting, and a malformed file or an empty list should start it with no login, so check for the login prompt. Under rootless Docker or user-namespace remapping the host-side owner differs; this guide has not checked that case.

## Verify

None of this guide's live Verify checks has a recorded demonstration. The missing capability is an isolated host or network namespace in which the services and their proxy may open listeners, as described for Fooocus below. Row 1.158 tracks the ComfyUI, AUTOMATIC1111, InvokeAI and proxy demonstrations; row 1.146 continues to track Fooocus.

The ComfyUI (8188), AUTOMATIC1111 (7860) and InvokeAI (9090) entries in the listener inventory and external probe loop are each REASONED, not demonstrated: the authoring host forbids opening a listener until an isolated network namespace exists, and it has none. From the cited ComfyUI v0.37.0 argument parser, AUTOMATIC1111 v1.10.1 `gradio_server_name()` and InvokeAI YAML Config reference, a host process bound to a wildcard address should appear that way in `ss` and answer the external probe with an HTTP code when the network permits it; bound to `127.0.0.1` as above, it should appear only on loopback and the external probe should report a refusal or timeout reaching your address. Confirm each service is running and answers on host loopback before interpreting an external refusal as the fixed state. These are expected outcomes from the sources, not observations.

The InvokeAI `/api/v1/boards/` check is also REASONED: the authoring host forbids opening a listener until an isolated network namespace exists, and it has none. The cited Multi-User Administrator Guide distinguishes the default single-user mode from `multiuser: true`, which requires a login. The [Multi-User API Guide](https://invoke.ai/features/multi-user-mode/api-guide/) documents the boards endpoint and missing-token `401`. The expected pair is an unauthenticated boards response in single-user mode (the cited guides give no status code for it; record the observed code) and `401` in multi-user mode; record both when demonstrating row 1.158.

The proxy check is REASONED: the authoring host forbids opening a listener until an isolated network namespace exists, and it has none, so no proxy or backend was run. Following [fronting-auth.md](fronting-auth.md), the expected exposed state serves the UI without proxy authentication, and the fixed state requires a login before the UI loads. Use your configured hostname in place of `imagegen.example.com`; the header request below checks the TLS connection and authentication response, and a browser check confirms the login gates the UI. Row 1.158 tracks both states.

The Fooocus entries below (port 7865 in the `ss` comment and in the probe loop) are REASONED, not demonstrated: the authoring host forbids opening a listener until an isolated network namespace exists, and it has none, so no Fooocus instance was run; row 1.146 tracks the demonstration. From the v2.5.5 sources cited below (the `--listen` default and its bare-flag constant in the argument parser, and the launch call that passes the bind and port to gradio), a Fooocus process started on the host with a bare `--listen` should show a wildcard listener on 7865 in `ss` and answer the probe from another host with an HTTP code; started as above, it should show `127.0.0.1:7865` in `ss`, and the probe should report a refusal or timeout reaching your address. The argument parse alone is demonstrated: `argparse` given that `--listen` definition (`type=str`, `default="127.0.0.1"`, `nargs="?"`, `const="0.0.0.0"`) returns `127.0.0.1` with no flag and `0.0.0.0` for a bare `--listen`. Confirm Fooocus is up and answers on the host itself before reading an external refusal as the fixed state. The `ss` expectations cover host processes only. For a container, the check is the PORTS column of `docker ps` plus the probe from another host, not `ss`, because socket visibility varies by Docker version and config (see [docker.md](docker.md#4-verify)): a container published as `7865:7865` should list the publication on every host address in the PORTS column and answer the probe with an HTTP code, and one published as `127.0.0.1:7865:7865` should list `127.0.0.1` as its only host address, with the probe reporting a refusal or timeout reaching your address. A publication with no host address binds `[::]` as well as `0.0.0.0`, so run the probe block twice, once with your public IPv4 address and once with your public IPv6 address in square brackets, each inside the quotes on the `set --` line. The block probes every port even when an earlier probe fails, so its exit status is not the verification result: read each `port=` line. Under rootful Docker's host networking nothing is published and the PORTS column is empty; the listener is in the host's network namespace, so read `ss` for it as for a host process: `127.0.0.1:7865` when fixed, or `0.0.0.0:7865` when `CMDARGS` still binds the wildcard, whether the image's default `--listen` was left in or a bridge-network `--listen 0.0.0.0` was copied over.

```bash
# REASONED inventory and external probes: ComfyUI 8188, AUTOMATIC1111 7860, InvokeAI 9090 (row 1.158);
# Fooocus 7865 (row 1.146). The authoring host forbids listeners without an isolated network namespace, and has none; expected outcomes and sources above.
ss -tlnp   # host processes: read every listener; 8188/7860/9090/7865: each service on 127.0.0.1 only
# each must be unreachable from another host. Read err, not the number: it must name a refusal or
# timeout reaching YOUR address. An HTTP code means the port answered. A resolver failure, a local
# socket error, or a timeout that did not come from the remote address is inconclusive. Every port is
# probed even after one fails, so the exit status is not the result; read each port= line.
# Run it once with your public IPv4 address, then again with your public IPv6 address in brackets.
(                                                   # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
    *) for p in 8188 7860 9090 7865; do                         # ComfyUI, SD WebUI, InvokeAI, Fooocus
         curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
           -w "port=$p http=%{http_code} exit=%{exitcode} err=%{errormsg}\n" "http://$1:$p/" || :
       done ;;
  esac
)
# REASONED: InvokeAI authentication; the authoring host forbids listeners without an isolated network namespace (row 1.158).
# guard-conventions: allow probe of a fixed loopback target; no reader-substituted placeholder in this probe's argv
curl -q -g -s --noproxy '*' -o /dev/null -w '%{http_code}\n' http://127.0.0.1:9090/api/v1/boards/
                                                       # from the host itself, InvokeAI multiuser mode: 401
                                                       # without a Bearer token, never the app itself
# REASONED: TLS and login; the authoring host forbids listeners without an isolated network namespace (row 1.158).
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -g -sI https://imagegen.example.com/                # via the proxy: TLS, and a login prompt
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
- ComfyUI-Manager security advisory, CVE-2025-67303, GHSA-95pq-hr8p-f5g7 (minimums ComfyUI v0.3.76 and Manager v3.38): https://github.com/Comfy-Org/ComfyUI-Manager/security/advisories/GHSA-95pq-hr8p-f5g7
- AUTOMATIC1111 Command Line Arguments and Settings wiki: https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Command-Line-Arguments-and-Settings
- AUTOMATIC1111 `--gradio-auth-path` ("set gradio authentication file path"), `--gradio-auth`, `--api-auth` and `--server-name` definitions (pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/cmd_args.py#L87-L113
- AUTOMATIC1111 credential reader: opens `cmd_opts.gradio_auth_path`, splits each line on `,` and each entry once on `:` (pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/initialize_util.py#L114-L139
- AUTOMATIC1111 passes the credential list to Gradio as `auth=` (`list(initialize_util.get_gradio_auth_creds()) or None`; pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/webui.py#L70-L90
- AUTOMATIC1111 API credential input trace: plain `ArgumentParser()` without argument-file support, string `--api-auth` defaulting to `None`, parsing of argv and the shared namespace alias (pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/cmd_args.py#L6, https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/cmd_args.py#L102, https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/shared_cmd_options.py#L7-L15 and https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/shared.py#L14-L20
- AUTOMATIC1111 API credential uses: conditional authentication dependency, credential comparison and the namespace-output reader (pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/api/api.py#L274-L284 and https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/api/api.py#L689-L690
- AUTOMATIC1111 settings inputs are separate from `cmd_opts.api_auth`: initialization and loading of `shared.opts`, settings API writes, and UI configuration restoration (pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/shared_init.py#L17-L24, https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/options.py#L144-L171, https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/options.py#L197-L206, https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/api/api.py#L678-L687, https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/ui.py#L1110-L1113 and https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/ui_loadsave.py#L14-L73
- AUTOMATIC1111 `--api-auth` parsing, `auth.split(":")` into a user and a password for each `,`-separated entry (pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/api/api.py#L199-L205
- AUTOMATIC1111 `/sdapi/v1/cmd-flags` returns every command-line option: the route, its handler, the response model built from the whole parser, and routes that need credentials only with `--api-auth` (pinned tag v1.10.1): https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/api/api.py#L222, https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/api/api.py#L689-L690, https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/api/models.py#L221-L231 and https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.10.1/modules/api/api.py#L274-L277
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
- InvokeAI YAML Config (6.14.1, schema 4.0.2, as recorded above; host/port defaults): https://invoke.ai/configuration/invokeai-yaml/
- InvokeAI Multi-User Administrator Guide: https://invoke.ai/features/multi-user-mode/admin-guide/
- InvokeAI Multi-User API Guide (boards endpoint and missing-token `401`): https://invoke.ai/features/multi-user-mode/api-guide/
- Fooocus README, UI access and authentication (`--listen`, `--port`, `--share`, `auth.json`; pinned tag v2.5.5): https://github.com/lllyasviel/Fooocus/blob/v2.5.5/readme.md#L296-L301
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0): https://curl.se/docs/manpage.html
- ComfyUI `--listen` default `127.0.0.1`, `0.0.0.0,::` when given without a value, and `--port` default `8188` (pinned tag v0.37.0): https://github.com/Comfy-Org/ComfyUI/blob/v0.37.0/comfy/cli_args.py#L63-L64
- Fooocus `--listen` default `127.0.0.1`, and `0.0.0.0` when given without a value (pinned tag v2.5.5): https://github.com/lllyasviel/Fooocus/blob/v2.5.5/ldm_patched/modules/args_parser.py#L36
- Fooocus sets no port default of its own (`port=None`, pinned tag v2.5.5): https://github.com/lllyasviel/Fooocus/blob/v2.5.5/args_manager.py#L43-L47
- Fooocus sets `GRADIO_SERVER_PORT` to `7865` only when it is unset (pinned tag v2.5.5): https://github.com/lllyasviel/Fooocus/blob/v2.5.5/launch.py#L13-L14
- Fooocus passes the bind, the port and the `auth.json` login to gradio (pinned tag v2.5.5): https://github.com/lllyasviel/Fooocus/blob/v2.5.5/webui.py#L1120-L1128
- Fooocus pins gradio 3.41.2 (pinned tag v2.5.5): https://github.com/lllyasviel/Fooocus/blob/v2.5.5/requirements_versions.txt#L13
- gradio 3.41.2 reads `GRADIO_SERVER_PORT` as the start of its port search, 100 ports long by default (pinned tag gradio@3.41.2): https://github.com/gradio-app/gradio/blob/gradio%403.41.2/gradio/networking.py#L24-L27
- gradio 3.41.2 tries only the passed port, or searches upward when none is passed, and raises when none is free (pinned tag gradio@3.41.2): https://github.com/gradio-app/gradio/blob/gradio%403.41.2/gradio/networking.py#L133-L171
- Fooocus `entry_with_update.py` fetches `origin` and fast-forwards the checked-out branch before importing `launch.py` (pinned tag v2.5.5): https://github.com/lllyasviel/Fooocus/blob/v2.5.5/entry_with_update.py#L16-L46
- Fooocus container image: `ENV CMDARGS --listen`, and the process runs as the unprivileged `user` account (pinned tag v2.5.5): https://github.com/lllyasviel/Fooocus/blob/v2.5.5/Dockerfile#L3 and https://github.com/lllyasviel/Fooocus/blob/v2.5.5/Dockerfile#L17-L29
- Fooocus container entrypoint runs `launch.py` with `CMDARGS` (pinned tag v2.5.5): https://github.com/lllyasviel/Fooocus/blob/v2.5.5/entrypoint.sh#L33
- Fooocus Compose file names both `build: .` and `image: ghcr.io/lllyasviel/fooocus`, publishes `7865:7865` and sets `CMDARGS=--listen` (pinned tag v2.5.5): https://github.com/lllyasviel/Fooocus/blob/v2.5.5/docker-compose.yml#L6-L11
- Fooocus Docker instructions (`-p 7865:7865`, `-e CMDARGS=--listen`, a `docker run` of `ghcr.io/lllyasviel/fooocus`, building locally; pinned tag v2.5.5): https://github.com/lllyasviel/Fooocus/blob/v2.5.5/docker.md#L19-L78
- Fooocus image build excludes `auth.json` (pinned tag v2.5.5): https://github.com/lllyasviel/Fooocus/blob/v2.5.5/.dockerignore#L53
- Fooocus reads `auth.json` by a relative name from the checkout root that `launch.py` changes into; `auth_list_to_dict` stores a `hash` entry as given and turns a `pass` entry into its SHA-256 hex digest; the loader opens the file outside its `try` and returns no credentials for a malformed file or an empty list; and `check_auth` compares the SHA-256 hex digest of the password typed at login with the stored value (pinned tag v2.5.5): https://github.com/lllyasviel/Fooocus/blob/v2.5.5/modules/constants.py#L5, https://github.com/lllyasviel/Fooocus/blob/v2.5.5/launch.py#L7-L9, https://github.com/lllyasviel/Fooocus/blob/v2.5.5/modules/auth.py#L8-L16, https://github.com/lllyasviel/Fooocus/blob/v2.5.5/modules/auth.py#L19-L34 and https://github.com/lllyasviel/Fooocus/blob/v2.5.5/modules/auth.py#L37-L41
- Docker port publishing (Engine 28.0 boundary qualification recorded above; with no host address, "the Docker daemon publishes ports to all host addresses (0.0.0.0 and [::])"): https://docs.docker.com/engine/network/port-publishing/
- Compose Specification, `pull_policy` (`build`: "Compose builds the image"; and "The `latest` tag is always pulled even when the `missing` pull policy is used"; pinned commit 914ec15d1fa4): https://github.com/compose-spec/compose-spec/blob/914ec15d1fa498969c0df5c1d672306db3256089/05-services.md#L1816-L1832
- Compose Specification, a service with both `build` and `image` (Compose "follows the rules defined by the `pull_policy` attribute"; if it is missing, "Compose attempts to pull the image first and then builds from source if the image isn't found", and a built image takes the `image` name, as the example shows; pinned commit 914ec15d1fa4): https://github.com/compose-spec/compose-spec/blob/914ec15d1fa498969c0df5c1d672306db3256089/build.md#L21-L23 and https://github.com/compose-spec/compose-spec/blob/914ec15d1fa498969c0df5c1d672306db3256089/build.md#L50-L62
- `docker compose up --build` ("Build images before starting containers"; pinned tag v2.32.4): https://github.com/docker/compose/blob/v2.32.4/cmd/compose/up.go#L147
