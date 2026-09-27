---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "486088828da5dea283608a49ddf61fb9fb8138d8c0a9aa629c64bc397df58214",
  "components": {
    "anything": {
      "name": "AnythingLLM documentation",
      "basis": "unknown",
      "sources": {
        "s6b5aa8c91ad3": "https://docs.anythingllm.com/features/security-and-access"
      }
    },
    "lobe": {
      "name": "LobeHub",
      "basis": "v2.2.16",
      "sources": {
        "s78199d80212a": "https://lobehub.com/only-ai/markdown/docs/en/self-hosting/environment-variables/basic",
        "s977fd003b436": "https://github.com/lobehub/lobehub/blob/v2.2.16/docs/self-hosting/environment-variables/basic.mdx#L22-L32",
        "s84e88654e760": "https://lobehub.com/only-ai/markdown/docs/en/self-hosting/environment-variables/auth",
        "sdb87ee6e14a5": "https://github.com/lobehub/lobehub/blob/v2.2.16/docs/self-hosting/environment-variables/auth.mdx"
      }
    },
    "docker": {
      "name": "Docker CLI",
      "basis": "v27.5.1",
      "sources": {
        "s52c162a9786f": "https://github.com/docker/cli/blob/v27.5.1/docs/reference/commandline/container_run.md",
        "s8c2adc7212d7": "https://github.com/docker/cli/blob/v27.5.1/docs/reference/commandline/container_run.md#L626-L640",
        "s2611a6021e2f": "https://github.com/docker/cli/blob/v27.5.1/opts/env.go#L18-L31",
        "s9a4c6197f246": "https://github.com/docker/cli/blob/v27.5.1/pkg/kvfile/kvfile.go#L54-L69",
        "sdc1935b6999f": "https://github.com/docker/cli/blob/v27.5.1/opts/parse.go#L19-L39",
        "sd1025af9c6ff": "https://github.com/docker/cli/blob/v27.5.1/pkg/kvfile/kvfile.go#L121-L126"
      }
    },
    "compose": {
      "name": "Docker Compose",
      "basis": "v2.32.4",
      "sources": {
        "s14c0c0a70b7e": "https://github.com/docker/compose/blob/v2.32.4/go.mod#L5-L18",
        "se594167796f7": "https://github.com/docker/compose/blob/v2.32.4/pkg/compose/create.go#L1029-L1084",
        "sf6263e4f21f0": "https://github.com/docker/compose/blob/v2.32.4/pkg/compose/secrets.go#L101",
        "s0d8af80827c8": "https://github.com/docker/compose/blob/v2.32.4/pkg/compose/secrets.go#L31-L61"
      }
    },
    "compose-go": {
      "name": "compose-go",
      "basis": "v2.4.7",
      "sources": {
        "s25bb7bb5626f": "https://github.com/compose-spec/compose-go/blob/v2.4.7/types/project.go#L631-L664"
      }
    },
    "moby": {
      "name": "Moby",
      "basis": "v27.5.1",
      "sources": {
        "s638ae9c795a2": "https://github.com/moby/moby/blob/v27.5.1/api/types/container/config.go#L55",
        "sa3cf5ca8ad4d": "https://github.com/moby/moby/blob/v27.5.1/daemon/inspect.go#L107-L110"
      }
    },
    "chainlit": {
      "name": "Chainlit documentation",
      "basis": "unknown",
      "sources": {
        "sa8ffef5a2afe": "https://docs.chainlit.io/authentication/overview",
        "sfc1842532120": "https://docs.chainlit.io/authentication/password"
      }
    },
    "python": {
      "name": "Python documentation",
      "basis": "unknown",
      "sources": {
        "se86233c0ce69": "https://docs.python.org/3/library/os.html",
        "s7a54556e5dac": "https://docs.python.org/3/library/hmac.html"
      }
    },
    "owasp": {
      "name": "OWASP password guidance",
      "basis": "unknown",
      "sources": {
        "s49e8d76431d9": "https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html"
      }
    },
    "openhands": {
      "name": "OpenHands documentation",
      "basis": "unknown",
      "sources": {
        "s1756d23e1d0b": "https://docs.openhands.dev/overview/faqs",
        "s0ceb47353632": "https://docs.openhands.dev/openhands/usage/run-openhands/local-setup"
      }
    },
    "curl": {
      "name": "curl minimum write-out version",
      "basis": "7.75.0",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    }
  },
  "claims": {
    "anything-single": {"text": "Docker single-user password protection is optional and grants every holder settings/admin/chat access, not per-user isolation.", "components": ["anything"], "sources": ["anything:s6b5aa8c91ad3"], "status": "REASONED"},
    "anything-roles": {"text": "Multi-user mode is preferred: Admin has full access, Manager all workspaces without provider/store settings, Default only assigned workspaces.", "components": ["anything"], "sources": ["anything:s6b5aa8c91ad3"], "status": "REASONED"},
    "anything-mode": {"text": "Enabling multi-user mode cannot be reverted to single-user; choose deliberately.", "components": ["anything"], "sources": ["anything:s6b5aa8c91ad3"], "status": "REASONED"},
    "anything-bind": {"text": "Publish AnythingLLM only on loopback 3001 and put proxy TLS/login in front.", "components": ["anything", "docker"], "sources": ["anything:s6b5aa8c91ad3", "docker:s52c162a9786f"], "status": "REASONED"},
    "lobe-vault": {"text": "KEY_VAULTS_SECRET encrypts stored provider credentials; generate with openssl rand -base64 32 and preserve it for the data lifetime, not as a login password.", "components": ["lobe"], "sources": ["lobe:s78199d80212a", "lobe:s977fd003b436"], "status": "REASONED"},
    "lobe-session": {"text": "Better Auth requires AUTH_SECRET, generated the same way, to sign sessions.", "components": ["lobe"], "sources": ["lobe:s84e88654e760", "lobe:sdb87ee6e14a5"], "status": "REASONED"},
    "lobe-sso": {"text": "AUTH_SSO_PROVIDERS selects providers and matching credentials; AUTH_DISABLE_EMAIL_PASSWORD=1 forces SSO-only login.", "components": ["lobe"], "sources": ["lobe:s84e88654e760", "lobe:sdb87ee6e14a5"], "status": "REASONED"},
    "lobe-admission": {"text": "AUTH_ALLOWED_EMAILS defaults empty, permitting all emails; set explicit addresses/domains for registration.", "components": ["lobe"], "sources": ["lobe:s84e88654e760", "lobe:sdb87ee6e14a5"], "status": "REASONED"},
    "lobe-mfa": {"text": "Enforce MFA at the configured SSO provider; LobeChat login has no second factor of its own.", "components": ["lobe"], "sources": ["lobe:s84e88654e760"], "status": "REASONED"},
    "docker-input": {"text": "Docker --env-file reads a named file, not stdin; -e NAME uses CLI environment, while -e NAME=value exposes argv.", "components": ["docker"], "sources": ["docker:s52c162a9786f", "docker:s8c2adc7212d7", "docker:s2611a6021e2f", "docker:s9a4c6197f246"], "status": "REASONED"},
    "docker-envfile": {"text": "Bare names in env files import CLI environment; validate exactly the intended secret assignments and reject extra/missing/duplicate lines.", "components": ["docker"], "sources": ["docker:sdc1935b6999f", "docker:sd1025af9c6ff"], "status": "REASONED"},
    "compose-envfile": {"text": "Compose env_file resolves environment via compose-go v2.4.7, pinned by Compose v2.32.4.", "components": ["compose", "compose-go"], "sources": ["compose:s14c0c0a70b7e", "compose-go:s25bb7bb5626f"], "status": "REASONED"},
    "compose-secrets": {"text": "Compose file secrets mount read-only under /run/secrets; environment secrets are copied there, default 0444, and need an application reader.", "components": ["compose"], "sources": ["compose:se594167796f7", "compose:sf6263e4f21f0", "compose:s0d8af80827c8"], "status": "REASONED"},
    "lobe-file-input": {"text": "LobeHub documents environment inputs; the recorded v2.2.16 search found no KEY_VAULTS_SECRET_FILE, AUTH_SECRET_FILE or AUTH_GOOGLE_SECRET_FILE.", "components": ["lobe"], "sources": ["lobe:s977fd003b436", "lobe:sdb87ee6e14a5"], "status": "REASONED"},
    "lobe-file": {"text": "Create the durable plaintext env file once in protected directories; never replace a live encryption key, inspect default ACLs and discard partial failed writes.", "components": ["lobe", "docker"], "sources": ["lobe:s977fd003b436", "lobe:sdb87ee6e14a5", "docker:s52c162a9786f"], "status": "REASONED"},
    "lobe-launch": {"text": "Use validated env-file with loopback 3210 publication and non-secret SSO/admission settings on argv.", "components": ["lobe", "docker"], "sources": ["lobe:sdb87ee6e14a5", "docker:s52c162a9786f"], "status": "REASONED"},
    "container-secrets": {"text": "Environment values remain readable through Docker inspect for running/stopped containers and process environ during lifetime; env-file avoids CLI argv, not operator access.", "components": ["moby", "docker"], "sources": ["moby:s638ae9c795a2", "moby:sa3cf5ca8ad4d", "docker:s52c162a9786f"], "status": "REASONED"},
    "chainlit-default": {"text": "Chainlit applications are public by default; set CHAINLIT_AUTH_SECRET and at least one password/OAuth/header callback.", "components": ["chainlit"], "sources": ["chainlit:sa8ffef5a2afe"], "status": "REASONED"},
    "chainlit-callback": {"text": "Password callback returns a user on success and None on refusal; shared credential creates one identity without individual revocation.", "components": ["chainlit"], "sources": ["chainlit:sfc1842532120"], "status": "REASONED"},
    "chainlit-environment": {"text": "Example reads credentials once at import, fails on missing or empty values, and requires restart to adopt replacements.", "components": ["python", "chainlit"], "sources": ["python:se86233c0ce69", "chainlit:sfc1842532120"], "status": "REASONED"},
    "chainlit-comparison": {"text": "Both compare_digest calls run before combining results; content-based short-circuiting is avoided, but types/lengths and whole callback timing are not concealed.", "components": ["python"], "sources": ["python:s7a54556e5dac"], "status": "REASONED"},
    "chainlit-rotation": {"text": "Password replacement stops new logins, not existing signed sessions; rotate CHAINLIT_AUTH_SECRET too to invalidate them.", "components": ["chainlit"], "sources": ["chainlit:sa8ffef5a2afe"], "status": "REASONED"},
    "chainlit-accounts": {"text": "Chainlit persists users but supplies no password-account management; per-user store/verification are the application's responsibility, with Argon2id for new hashes.", "components": ["chainlit", "owasp"], "sources": ["chainlit:sfc1842532120", "owasp:s49e8d76431d9"], "status": "REASONED"},
    "chainlit-mfa": {"text": "Chainlit has no built-in MFA; use an enforcing identity provider or authenticating proxy.", "components": ["chainlit"], "sources": ["chainlit:sa8ffef5a2afe"], "status": "REASONED"},
    "openhands-boundary": {"text": "OpenHands is single-user; shared-key API access is not per-user identity, and execution isolation depends on backend/mount/socket choices.", "components": ["openhands"], "sources": ["openhands:s1756d23e1d0b"], "status": "REASONED"},
    "openhands-bind": {"text": "Quickstart publishes 3000 on every interface; use 127.0.0.1:3000:3000 and an authenticated tunnel.", "components": ["openhands"], "sources": ["openhands:s0ceb47353632"], "status": "REASONED"},
    "verify-listeners": {"text": "Inventory loopback UI listeners 3001/3210/3000; external refusal must name the real remote path, with DNS/local failures inconclusive.", "components": ["docker", "openhands", "curl"], "sources": ["docker:s52c162a9786f", "openhands:s0ceb47353632", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-login": {"text": "Verify proxy HTTPS and login requirement; generic API refusal is a deployment-specific check requiring an actual protected route.", "components": ["anything", "lobe", "chainlit", "openhands"], "sources": ["anything:s6b5aa8c91ad3", "lobe:s84e88654e760", "chainlit:sa8ffef5a2afe", "openhands:s1756d23e1d0b"], "status": "REASONED", "verify": [1]},
    "verify-registration": {"text": "A new Google identity absent from AUTH_ALLOWED_EMAILS should fail registration; this does not revoke an existing user's session.", "components": ["lobe"], "sources": ["lobe:s84e88654e760", "lobe:sdb87ee6e14a5"], "status": "REASONED", "verify": [1]},
    "verify-isolation": {"text": "User A's retrieval must succeed before user B is checked for denial; independently test documents, history, memory and caches, not login alone.", "components": ["anything"], "sources": ["anything:s6b5aa8c91ad3"], "status": "REASONED"}
  }
}
---
# Self-hosted chat and agent UIs: AnythingLLM, LobeChat, Chainlit, OpenHands

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| anything-single: Docker single-user password protection is optional and grants every holder settings/admin/chat access, not per-user isolation. | AnythingLLM documentation unknown | REASONED |
| anything-roles: Multi-user mode is preferred: Admin has full access, Manager all workspaces without provider/store settings, Default only assigned workspaces. | AnythingLLM documentation unknown | REASONED |
| anything-mode: Enabling multi-user mode cannot be reverted to single-user; choose deliberately. | AnythingLLM documentation unknown | REASONED |
| anything-bind: Publish AnythingLLM only on loopback 3001 and put proxy TLS/login in front. | AnythingLLM documentation unknown; Docker CLI v27.5.1 | REASONED |
| lobe-vault: KEY_VAULTS_SECRET encrypts stored provider credentials; generate with openssl rand -base64 32 and preserve it for the data lifetime, not as a login password. | LobeHub v2.2.16 | REASONED |
| lobe-session: Better Auth requires AUTH_SECRET, generated the same way, to sign sessions. | LobeHub v2.2.16 | REASONED |
| lobe-sso: AUTH_SSO_PROVIDERS selects providers and matching credentials; AUTH_DISABLE_EMAIL_PASSWORD=1 forces SSO-only login. | LobeHub v2.2.16 | REASONED |
| lobe-admission: AUTH_ALLOWED_EMAILS defaults empty, permitting all emails; set explicit addresses/domains for registration. | LobeHub v2.2.16 | REASONED |
| lobe-mfa: Enforce MFA at the configured SSO provider; LobeChat login has no second factor of its own. | LobeHub v2.2.16 | REASONED |
| docker-input: Docker --env-file reads a named file, not stdin; -e NAME uses CLI environment, while -e NAME=value exposes argv. | Docker CLI v27.5.1 | REASONED |
| docker-envfile: Bare names in env files import CLI environment; validate exactly the intended secret assignments and reject extra/missing/duplicate lines. | Docker CLI v27.5.1 | REASONED |
| compose-envfile: Compose env_file resolves environment via compose-go v2.4.7, pinned by Compose v2.32.4. | Docker Compose v2.32.4; compose-go v2.4.7 | REASONED |
| compose-secrets: Compose file secrets mount read-only under /run/secrets; environment secrets are copied there, default 0444, and need an application reader. | Docker Compose v2.32.4 | REASONED |
| lobe-file-input: LobeHub documents environment inputs; the recorded v2.2.16 search found no KEY_VAULTS_SECRET_FILE, AUTH_SECRET_FILE or AUTH_GOOGLE_SECRET_FILE. | LobeHub v2.2.16 | REASONED |
| lobe-file: Create the durable plaintext env file once in protected directories; never replace a live encryption key, inspect default ACLs and discard partial failed writes. | LobeHub v2.2.16; Docker CLI v27.5.1 | REASONED |
| lobe-launch: Use validated env-file with loopback 3210 publication and non-secret SSO/admission settings on argv. | LobeHub v2.2.16; Docker CLI v27.5.1 | REASONED |
| container-secrets: Environment values remain readable through Docker inspect for running/stopped containers and process environ during lifetime; env-file avoids CLI argv, not operator access. | Moby v27.5.1; Docker CLI v27.5.1 | REASONED |
| chainlit-default: Chainlit applications are public by default; set CHAINLIT_AUTH_SECRET and at least one password/OAuth/header callback. | Chainlit documentation unknown | REASONED |
| chainlit-callback: Password callback returns a user on success and None on refusal; shared credential creates one identity without individual revocation. | Chainlit documentation unknown | REASONED |
| chainlit-environment: Example reads credentials once at import, fails on missing or empty values, and requires restart to adopt replacements. | Python documentation unknown; Chainlit documentation unknown | REASONED |
| chainlit-comparison: Both compare_digest calls run before combining results; content-based short-circuiting is avoided, but types/lengths and whole callback timing are not concealed. | Python documentation unknown | REASONED |
| chainlit-rotation: Password replacement stops new logins, not existing signed sessions; rotate CHAINLIT_AUTH_SECRET too to invalidate them. | Chainlit documentation unknown | REASONED |
| chainlit-accounts: Chainlit persists users but supplies no password-account management; per-user store/verification are the application's responsibility, with Argon2id for new hashes. | Chainlit documentation unknown; OWASP password guidance unknown | REASONED |
| chainlit-mfa: Chainlit has no built-in MFA; use an enforcing identity provider or authenticating proxy. | Chainlit documentation unknown | REASONED |
| openhands-boundary: OpenHands is single-user; shared-key API access is not per-user identity, and execution isolation depends on backend/mount/socket choices. | OpenHands documentation unknown | REASONED |
| openhands-bind: Quickstart publishes 3000 on every interface; use 127.0.0.1:3000:3000 and an authenticated tunnel. | OpenHands documentation unknown | REASONED |
| verify-listeners: Inventory loopback UI listeners 3001/3210/3000; external refusal must name the real remote path, with DNS/local failures inconclusive. | Docker CLI v27.5.1; OpenHands documentation unknown; curl minimum write-out version 7.75.0 | REASONED |
| verify-login: Verify proxy HTTPS and login requirement; generic API refusal is a deployment-specific check requiring an actual protected route. | AnythingLLM documentation unknown; LobeHub v2.2.16; Chainlit documentation unknown; OpenHands documentation unknown | REASONED |
| verify-registration: A new Google identity absent from AUTH_ALLOWED_EMAILS should fail registration; this does not revoke an existing user's session. | LobeHub v2.2.16 | REASONED |
| verify-isolation: User A's retrieval must succeed before user B is checked for denial; independently test documents, history, memory and caches, not login alone. | AnythingLLM documentation unknown | REASONED |
<!-- version-basis:end -->

These tools hold provider API keys and full conversation history, and several are wide open the moment they start. Bind every one to loopback, front it with TLS and a login ([caddy.md](caddy.md)/[nginx.md](nginx.md), [free-certificates.md](free-certificates.md)), and turn on the tool's own authentication as a second layer, never as a substitute for the network boundary. See also [open-webui.md](open-webui.md) for the Open WebUI case, [secrets.md](secrets.md) for the provider keys these apps store, and [fronting-auth.md](fronting-auth.md)/[mfa.md](mfa.md) for the identity layer in front.

## AnythingLLM

Security features apply to the Docker deployment. Single-user mode offers an optional "Password Protect Instance" toggle: once set, anyone with that one password can use the instance, change any setting, and read every chat, so treat it as a screen door, not a real access-control boundary. Multi-user mode is the documented preferred setup: it adds Admin (full access including logs and analytics), Manager (all workspaces, no LLM/embedder/vector-database settings), and Default (only explicitly assigned workspaces) roles, each requiring its own login. Multi-user mode cannot be reverted to single-user once enabled, so decide before turning it on.

```bash
docker run -d -p 127.0.0.1:3001:3001 mintplexlabs/anythingllm
```

Keep it on loopback regardless of which mode you choose, and put the proxy's own TLS and login in front.

## LobeChat

`KEY_VAULTS_SECRET` is the key that encrypts stored provider credentials (AES-GCM); generate it with `openssl rand -base64 32`, and once set, never change it, or previously encrypted data becomes unreadable. LobeHub's own basic-variables page describes it loosely as "a password to access the LobeHub service", but its own warning on the same entry says the key is used to encrypt sensitive data: treat it as the encryption key, not the deployment's login gate. Real per-user login comes from LobeChat's Better Auth service: `AUTH_SECRET` (required, generated the same way) signs sessions, `AUTH_SSO_PROVIDERS` lists enabled SSO providers (for example `google,github,microsoft`) alongside the matching provider credentials each one needs (for example `AUTH_GOOGLE_ID`/`AUTH_GOOGLE_SECRET`), and `AUTH_DISABLE_EMAIL_PASSWORD=1` forces SSO-only login, hiding the password form entirely. `AUTH_ALLOWED_EMAILS` restricts registration to specific addresses or domains, but it defaults to empty, which allows every email through, so set it explicitly rather than relying on federation alone to gate access.

Keep the three secrets, `KEY_VAULTS_SECRET`, `AUTH_SECRET` and the Google OAuth client secret, off the `docker run` command line: a value given as `-e NAME=value` is in the docker CLI's argv, where `ps` and `/proc/<pid>/cmdline` show it to other local accounts while that command runs, and quoting does not change that. At docker/cli v27.5.1, `--env-file` reads environment variables from a file, through a loader that opens the named path and has no `-` stdin form, and `-e NAME` with no value takes the value from the CLI's own environment. Docker Compose's `env_file` reads a file of variables for a service through its own loader in compose-go (v2.4.7, the version Docker Compose v2.32.4 pins). A Compose `secrets` entry puts a value in a file under `/run/secrets/` instead: a file-sourced secret is bind-mounted read-only, and an environment-sourced one is copied into the container, mode `0444` by default, rather than mounted. That only helps if something reads the file into these variables, and LobeHub documents them as environment variables only; a search of its v2.2.16 tree finds no `KEY_VAULTS_SECRET_FILE`, `AUTH_SECRET_FILE` or `AUTH_GOOGLE_SECRET_FILE`. Use the `--env-file` file: `KEY_VAULTS_SECRET` must stay the same for the life of the data it encrypts, so it needs a durable home anyway, and a file keeps the values out of the CLI's own environment too. Create it once, as the account that runs `docker`. The block prompts for the Google client secret without echo, under CONTRIBUTING rule 7's `read` exception, and assumes a clean shell:

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set -eC
  umask 077
  if [ -e "$HOME/.config/lobechat/secrets.env" ] || [ -L "$HOME/.config/lobechat/secrets.env" ]; then
    echo 'a secrets.env already exists in ~/.config/lobechat; nothing written'; exit 2
  fi
  { unset -n gsec && unset -v gsec; } 2>/dev/null ||
    { echo 'cannot clear gsec in this shell; nothing written'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; nothing written'; exit 2; }
  printf 'Google OAuth client secret (input hidden): '
  IFS= read -r -s gsec || { printf '\n'; echo 'no client secret read; nothing written'; exit 2; }
  printf '\n'
  case "$gsec" in
    ""|*REPLACE_WITH_*|*[[:cntrl:]]*) echo 'empty client secret, placeholder or control character; nothing written'; exit 2 ;;
  esac
  set -- "$(openssl rand -base64 32)" "$(openssl rand -base64 32)"
  [ "${#1}" -eq 44 ] || { echo 'key generation failed; nothing written'; exit 2; }
  [ "${#2}" -eq 44 ] || { echo 'key generation failed; nothing written'; exit 2; }
  case "$1$2" in *[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=]*) echo 'key generation failed; nothing written'; exit 2 ;; esac
  mkdir -p -- "$HOME/.config/lobechat"
  chmod 700 -- "$HOME/.config/lobechat"
  printf 'KEY_VAULTS_SECRET=%s\nAUTH_SECRET=%s\nAUTH_GOOGLE_SECRET=%s\n' "$1" "$2" "$gsec" > "$HOME/.config/lobechat/secrets.env"
)
```

The block refuses to run when `~/.config/lobechat/secrets.env` already exists in any form, a dangling symlink included, before it prompts or generates anything, so a rerun cannot replace a `KEY_VAULTS_SECRET` that already encrypts data. `set -C` adds overwrite protection for an existing regular file only, not for every kind of target, and the existence check runs before the write rather than atomically with it, so both hold only in directories that no other account can write to or replace: `$HOME`, `~/.config` and the owner-only directory the block creates. For a deployment that already has these values, put its existing values in such a file instead of generating new ones. `umask 077` creates the directory mode `0700` and the file mode `0600`, unless the directory, or the parent it is created in, carries a default ACL: new files inherit that ACL in place of the umask, and `chmod 700` on the directory does not remove it. Check with `getfacl` before running the block; backlog row 1.141 tracks making the block refuse that case. The block writes nothing unless both generated values are 44 base64 characters and the prompted secret is non-empty, is not the placeholder and holds no control character. `read` stops at the first newline, so a newline cannot enter the value; the check refuses a carriage return or any other control character. Paste the secret alone at the hidden prompt: a multi-line paste leaves every line after the first for your shell to run. The generated values pass only through the subshell's positional parameters and the builtin `printf`, and the client secret through one variable local to the subshell, never a command line; the block clears inherited traps first because a DEBUG, RETURN or ERR trap from your shell could otherwise read them. A write failure can leave a partial file. The launch block below refuses the shapes it can detect, a generated value that is not 44 base64 characters, a missing or duplicated line, or any other line, but a client secret cut short still looks like a valid value and cannot be detected, so delete a file left by a failed run and create it again rather than starting on it. The file holds the secrets in plaintext at rest, readable by that account, by root and by any backup that copies it, so keep it and its backups out of source control ([secrets.md](secrets.md)). Start LobeChat from the file, with only non-secret values on its command line. Substitute your Google OAuth client ID and the addresses or domains allowed to register inside the single quotes on the `set --` line:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_GOOGLE_OAUTH_CLIENT_ID' 'admin@example.com,example.com'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not starting'; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo 'the set -- line needs exactly 2 values; not starting'; exit 2; }
  case "$1|$2" in *REPLACE_WITH_*) echo 'substitute the client ID inside the quotes on the set -- line; not starting'; exit 2 ;; esac
  { [ -n "$1" ] && [ -n "$2" ]; } || { echo 'empty value on the set -- line; not starting'; exit 2; }
  case "$1$2" in *[[:space:][:cntrl:]]*) echo 'whitespace or a control character on the set -- line; not starting'; exit 2 ;; esac
  f="$HOME/.config/lobechat/secrets.env"
  { [ -f "$f" ] && [ ! -L "$f" ]; } ||
    { echo 'need ~/.config/lobechat/secrets.env to be a regular file (it is missing, a symlink or another kind of file); not starting'; exit 2; }
  if grep -Eavqx -- 'KEY_VAULTS_SECRET=[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/]{43}=|AUTH_SECRET=[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/]{43}=|AUTH_GOOGLE_SECRET=[^[:cntrl:]]+' "$f"; then
    echo 'a line in ~/.config/lobechat/secrets.env is not one of the three secret lines; not starting'; exit 2
  else
    rc=$?; [ "$rc" -eq 1 ] || { echo 'could not check ~/.config/lobechat/secrets.env; not starting'; exit 2; }
  fi
  if grep -aq -- 'REPLACE_WITH_' "$f"; then
    echo 'a placeholder is still in ~/.config/lobechat/secrets.env; not starting'; exit 2
  else
    rc=$?; [ "$rc" -eq 1 ] || { echo 'could not check ~/.config/lobechat/secrets.env; not starting'; exit 2; }
  fi
  c=$(grep -Eacx -- 'KEY_VAULTS_SECRET=[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/]{43}=' "$f") || c=
  [ "$c" = 1 ] ||
    { echo 'need exactly one generated KEY_VAULTS_SECRET line in ~/.config/lobechat/secrets.env, or could not check it; not starting'; exit 2; }
  c=$(grep -Eacx -- 'AUTH_SECRET=[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/]{43}=' "$f") || c=
  [ "$c" = 1 ] ||
    { echo 'need exactly one generated AUTH_SECRET line in ~/.config/lobechat/secrets.env, or could not check it; not starting'; exit 2; }
  c=$(grep -Eacx -- 'AUTH_GOOGLE_SECRET=[^[:cntrl:]]+' "$f") || c=
  [ "$c" = 1 ] ||
    { echo 'need exactly one AUTH_GOOGLE_SECRET line in ~/.config/lobechat/secrets.env, or could not check it; not starting'; exit 2; }
  docker run -d -p 127.0.0.1:3210:3210 \
    --env-file "$HOME/.config/lobechat/secrets.env" \
    -e AUTH_DISABLE_EMAIL_PASSWORD=1 \
    -e AUTH_SSO_PROVIDERS=google \
    -e "AUTH_GOOGLE_ID=$1" \
    -e "AUTH_ALLOWED_EMAILS=$2" \
    lobehub/lobe-chat
)
```

The block refuses the placeholder, an empty value, and whitespace or a control character on the `set --` line. It checks first that `~/.config/lobechat/secrets.env` is a regular file and not a symlink, so a FIFO in its place can neither block the check nor be read by it. It then reads the file as text (`grep -a`: without `-a`, a NUL could make a malformed line look valid to grep) and refuses to start unless the file holds exactly one line for each generated value and exactly one client secret line, no other line and no placeholder: at v27.5.1 an env-file line holding only a name takes its value from the CLI's own environment, which would bring back the channel the file replaces. It uses a count only from a `grep` that succeeded, says that it could not check when `grep` cannot read the file, and gives the same result in a shell that has `set -e` on. The patterns for the two generated values spell out their ASCII character sets rather than ranges such as `A-Z`, whose meaning can depend on the locale. The client secret pattern, `[^[:cntrl:]]+`, is the exception and depends on the locale: it refuses only control characters, and the locale decides which characters are control characters, as it does for the other `[:cntrl:]` checks, in the block that creates the file and on the `set --` line. A key of another shape from an existing deployment needs the matching pattern relaxed. This moves the secrets out of argv, not out of reach. Docker hands them to the container as environment variables, so anyone who can use the Docker socket can read them back with `docker inspect`, which returns the container's configuration with its `Env` list, for as long as the container exists, running or stopped; and the same user as the container's process, or root, can read them from that process's `/proc/<pid>/environ` for its whole lifetime. Socket access is root-equivalent already ([container-hardening.md](container-hardening.md)); grant it to nobody you would not trust with these keys. `-e NAME` with no value would keep them out of argv as well, but only under rule 7's guarded one-command prefix assignment, never an `export`, and the values would then sit in the CLI's own environment too. Neither form erases a value already recorded in shell history, tracing or a log.

MFA: enforce it at whichever SSO provider you list in `AUTH_SSO_PROVIDERS`; LobeChat's own login has no second factor of its own.

## Chainlit

Chainlit applications are public by default: no login, no gate, anyone who reaches the port gets the chat. Set `CHAINLIT_AUTH_SECRET` (generate one with `chainlit create-secret`; changing it logs out every user) and implement at least one auth callback: password authentication, OAuth, or header-based authentication. A callback that returns `None` refuses the login. There is no built-in MFA; put it behind an identity provider that enforces a second factor, or an [Authelia](https://www.authelia.com/)-fronted proxy.

```python
import hmac
import os
from typing import Optional

import chainlit as cl

# Read the credential from the environment, never from source. Chainlit's own example
# compares a literal "admin" against a literal "admin", which is a demonstration rather
# than a deployment. These two names are this application's own, not Chainlit's.
# Indexing os.environ raises KeyError if either is unset, which stops the process before
# the callback is ever registered; the explicit test is for a variable that is SET and
# empty, which indexing accepts and which would otherwise be a usable password.
EXPECTED_USER = os.environ["CHAINLIT_USER"].encode()
EXPECTED_PASSWORD = os.environ["CHAINLIT_PASSWORD"].encode()
if not EXPECTED_USER or not EXPECTED_PASSWORD:
    raise SystemExit("CHAINLIT_USER and CHAINLIT_PASSWORD must both be set and non-empty")


@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.User]:
    # compare_digest avoids content-based short-circuiting, so it does not leak how much of
    # the password was right; Python notes it can still reveal "the types and lengths of a
    # and b, but not their values". Both comparisons run before the `and` so that a short
    # circuit there cannot reveal which half failed. The callback as a whole is not constant
    # time and does not need to be; the point is that the secret is not compared with ==.
    ok_user = hmac.compare_digest(username.encode(), EXPECTED_USER)
    ok_password = hmac.compare_digest(password.encode(), EXPECTED_PASSWORD)
    if ok_user and ok_password:
        return cl.User(identifier=username)
    return None
```

That is one shared credential, which is a gate on the deployment rather than user accounts: everyone who gets in is the same `identifier`, and there is nobody to revoke individually.

Rotating it is two steps, not one. Changing the environment variable does nothing until the process restarts, because the value above is read once at import. And a new password stops future logins without ending current ones: Chainlit issues a session token signed with `CHAINLIT_AUTH_SECRET`, and that secret, not this password, is what invalidates the sessions already handed out. Change both when you mean to lock everyone out.

For real accounts, this callback is one of the options rather than the only one. Chainlit also supports OAuth and header-based authentication, which move the decision to an identity provider and are usually the better answer ([identity-providers.md](identity-providers.md), [oidc-integration.md](oidc-integration.md)). If you do manage passwords yourself, Chainlit persists user records but provides no password-account management, so the store and the verification are yours: keep a per-user hash from a slow algorithm, Argon2id for anything new, and call it inside this callback in place of the comparison above. The vendor's own advice is the short version of this, "hash password before storing them". A shared service credential still belongs in the environment ([secrets.md](secrets.md)); a per-user password hash belongs in the account store.

## OpenHands

OpenHands is built for a single user on their own workstation: the project's own FAQ states there is no built-in authentication, isolation, or scalability for shared use, and the open-source build authorizes API access with one shared key rather than per-user identity. It also executes agent-generated code against your workspace, with the isolation depending entirely on your deployment choice (a local process backend runs with your user's permissions; container backends can be weakened by broad mounts, privileged mode, or Docker-socket access). Do not expose it to anyone you would not hand a shell to. The project documents a Hardened Docker Installation guide for deployments that must sit on a shared network; multi-tenant use is an enterprise offering, not something the open-source build supports.

The documented quickstart itself runs `docker run ... -p 3000:3000 ... openhands/openhands`, which maps every interface, not loopback; change that to `-p 127.0.0.1:3000:3000` before anything else. Reach it only through an authenticated tunnel; there is no login screen to add in front of it, so identity has to come entirely from the proxy or tunnel layer.

## Verify

```bash
# REASONED: listener and UI checks follow the cited vendor documentation;
# the authoring host lacks an isolated network namespace for authorized live listeners.
ss -tlnp   # read every listener; 3001/3210/3000: each UI on 127.0.0.1 only
# from another host. Read err, not the number: it must name a refusal or timeout reaching YOUR
# address. An HTTP code means the port answered. A resolver failure, a local socket error, or a
# timeout that did not come from the remote address is inconclusive, never a pass.
(                                                       # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
    *) curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
         -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:3210/" ;;
  esac
)
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -s https://chat.example.com/api/some-endpoint      # without a key/token: 401
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -sI https://chat.example.com/                      # via the proxy: TLS, login required
# LobeChat SSO: attempt to register/sign in with a Google account that has never registered and is
#   NOT listed in AUTH_ALLOWED_EMAILS; expect rejection at registration, before any account or session
#   is created (AUTH_ALLOWED_EMAILS gates new registration; it does not revoke an already-registered
#   user's existing session)
```

For a multi-user chat or RAG deployment (AnythingLLM workspaces, or a shared assistant over shared documents), verify isolation at the data layer, not only at login. First, as user A, ask a question whose answer lives only in user A's documents or past conversations and confirm A's own document supplies the answer, the positive control that retrieval works at all; then ask the same question as user B and confirm B gets nothing of A's. A retrieval step that searches every user's embeddings without enforcing per-document access hands one user's content into another's session even though each logged in separately; scope retrieval to the requesting user's own documents or workspace, and where the store is pgvector the tenant row-level-security check in [vector-databases.md](vector-databases.md) is the store-side half. A retrieval filter alone does not isolate conversation history, memory, or a shared cache; check each of those the same way. This isolation check is REASONED, not demonstrated: the authoring environment has no live multi-user RAG deployment. Its expected isolation rests on the cited AnythingLLM workspace-role documentation and the pgvector row-level-security guidance linked above.

## Common mistakes

- Leaving Chainlit unauthenticated because "it's just for testing"; public by default means public the moment it is reachable.
- Treating AnythingLLM's single instance password as equivalent to per-user accounts; it grants full admin to whoever has it.
- Running OpenHands with a shared, long-lived API key exposed on the same network as untrusted users.
- Rotating LobeChat's `KEY_VAULTS_SECRET` after data has been encrypted with it, which makes that data unreadable.
- Passing `KEY_VAULTS_SECRET`, `AUTH_SECRET` or `AUTH_GOOGLE_SECRET` as `-e NAME=value`, which puts the value in the docker CLI's argv for other local accounts to read while the command runs.

## Sources (checked September 2026)

- AnythingLLM security and access documentation: https://docs.anythingllm.com/features/security-and-access
- LobeHub environment variables (KEY_VAULTS_SECRET): https://lobehub.com/only-ai/markdown/docs/en/self-hosting/environment-variables/basic
- LobeHub authentication service environment variables (Better Auth): https://lobehub.com/only-ai/markdown/docs/en/self-hosting/environment-variables/auth
- LobeHub `KEY_VAULTS_SECRET` callout, "This key is used to encrypt sensitive data." (pinned tag v2.2.16): https://github.com/lobehub/lobehub/blob/v2.2.16/docs/self-hosting/environment-variables/basic.mdx#L22-L32
- LobeHub `AUTH_SECRET` generated with `openssl rand -base64 32`, and `AUTH_GOOGLE_SECRET` as the "Client Secret of the Google OAuth application." (pinned tag v2.2.16): https://github.com/lobehub/lobehub/blob/v2.2.16/docs/self-hosting/environment-variables/auth.mdx
- Docker `container run` reference, `--env-file` ("Read in a file of environment variables"; pinned tag v27.5.1): https://github.com/docker/cli/blob/v27.5.1/docs/reference/commandline/container_run.md
- Docker `container run` reference, `--env VAR` with no value, which "checks the value the variable has in your local environment and passes it to the container" (pinned tag v27.5.1): https://github.com/docker/cli/blob/v27.5.1/docs/reference/commandline/container_run.md#L626-L640 and the `-e` validator's `os.LookupEnv`: https://github.com/docker/cli/blob/v27.5.1/opts/env.go#L18-L31
- Docker CLI env-file loading through `kvfile.Parse`, with `-e` parsed after the file "to allow override" (pinned tag v27.5.1): https://github.com/docker/cli/blob/v27.5.1/opts/parse.go#L19-L39
- Docker CLI key/value file parser, which opens the named path (`os.Open(filename)`) with no `-` stdin form, and looks up a line that holds only a name in the CLI's environment (pinned tag v27.5.1): https://github.com/docker/cli/blob/v27.5.1/pkg/kvfile/kvfile.go#L54-L69 and https://github.com/docker/cli/blob/v27.5.1/pkg/kvfile/kvfile.go#L121-L126
- Docker Compose pins compose-go v2.4.7 (pinned tag v2.32.4): https://github.com/docker/compose/blob/v2.32.4/go.mod#L5-L18
- compose-go service `env_file` resolution ("parses env_files set for services to resolve the actual environment map for services"; pinned tag v2.4.7): https://github.com/compose-spec/compose-go/blob/v2.4.7/types/project.go#L631-L664
- Docker Compose file-sourced secrets bind-mounted read-only under `/run/secrets/`, environment-sourced ones skipped there (pinned tag v2.32.4): https://github.com/docker/compose/blob/v2.32.4/pkg/compose/create.go#L1029-L1084
- Docker Compose environment-sourced secrets copied into the container under `/run/secrets/`, mode `0444` by default (pinned tag v2.32.4): https://github.com/docker/compose/blob/v2.32.4/pkg/compose/secrets.go#L31-L61 and https://github.com/docker/compose/blob/v2.32.4/pkg/compose/secrets.go#L101
- Moby container inspect returns `Config: ctr.Config`, whose `Env []string` holds the environment (pinned tag v27.5.1): https://github.com/moby/moby/blob/v27.5.1/daemon/inspect.go#L107-L110 and https://github.com/moby/moby/blob/v27.5.1/api/types/container/config.go#L55
- Chainlit authentication overview: https://docs.chainlit.io/authentication/overview
- Chainlit password authentication (`@cl.password_auth_callback` signature and example): https://docs.chainlit.io/authentication/password
- Python `hmac.compare_digest`, for what it does and does not conceal: https://docs.python.org/3/library/hmac.html
- Python `os.environ`, for what indexing a missing key does: https://docs.python.org/3/library/os.html
- OWASP Password Storage Cheat Sheet, for Argon2id over bcrypt in anything new: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- OpenHands FAQs (single-user design, no built-in auth, sandboxing, hardened deployment): https://docs.openhands.dev/overview/faqs
- OpenHands local setup (default docker port mapping): https://docs.openhands.dev/openhands/usage/run-openhands/local-setup
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0): https://curl.se/docs/manpage.html
