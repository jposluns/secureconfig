# Secrets: keeping keys out of repositories

Secrets are passwords, API keys, tokens and private keys services use to prove their identity. This guide helps your AI assistant handle them securely, including no plaintext secrets in git, images or logs (encrypt any a team must version), random generation, scans before every push, and rotation first after leaks.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/secrets.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against Git ignore patterns 2.42.0, gitleaks git/dir path argument 8.19.1 to 8.30.1, gitleaks 8.19.0 git/dir source flag v8.19.0, gitleaks detect before 8.19.0 v8.18.4, OpenSSL random bytes 3.0, Python secrets 3.13, Vite environment variables 6, and GNU Bash reference manual bash-5.3; 1 further source is pinned to a commit and 18 carry no recorded version. Metadata reviewed 2026-10-05; documentation checked September 2026. The guide records 25 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

Leaked API keys and credentials in public repositories are the most common security incident in AI-assisted projects, and scanners harvest fresh commits within minutes. [authentication.md](authentication.md) states the baseline; this guide covers the handling.

## Rules

1. **Secrets never enter version control.** Add `.env`, `.env.*` (frameworks such as Next.js load `.env.local` and `.env.production`, so ignoring `.env` alone leaves those committable), `*.key`, and `*.pem` to `.gitignore` before the first commit, allowlisting only a no-secret template such as `!.env.example`; `.gitignore` does not untrack a file that is already committed. Load secrets from environment variables or a secret manager (AWS Secrets Manager, Google Secret Manager, Azure Key Vault, or your platform's store per [paas.md](paas.md)).
2. **Secrets never enter images or build logs.** Never put secrets in Dockerfile `ENV` or `ARG`: Docker documents that both are exposed in the final image; `ENV` also persists in containers from the image, while build arguments may persist in image metadata, provenance attestations and image history. `docker image history` shows an image's history; the reference's example history output shows an `ENV` instruction with its value. As this guide's assessment, `docker image history` does not show every secret value. Pass runtime secrets at runtime ([docker.md](docker.md)); for a secret needed during a build, use a temporary secret mount for that build instruction and do not copy or print it into the image. Do not print secrets in application or CI logs.
3. **Generate secrets randomly** (`openssl rand -base64 32`; `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`), 1 per service and environment, never shared between staging and production.
4. **Scan before every push.** [gitleaks](https://github.com/gitleaks/gitleaks) or [trufflehog](https://github.com/trufflesecurity/trufflehog) as a pre-commit hook and in CI:
   ```bash
   gitleaks git .          # scans the repository history; use 8.19.1 or later
   gitleaks dir .          # scans the working tree
   ```

   By source reading without a run, `git` and `dir` use a positional path at v8.19.1, defaulting to `.` if omitted or empty; the earlier review records this handling through v8.30.1. At v8.19.0, both commands instead read a `source` flag and do not use `args`. Across all seven top-level `cmd/` files, only `detect` and `protect` register `source`, each locally with default `.`; none registers it on the root, `git` or `dir`. Root `initConfig` also reads `source` when both `--config` and `GITLEAKS_CONFIG` are empty or unset; all three lookups call `log.Fatal` on error. Neither command has an observed result here.

   At v8.17.0, v8.18.0 and v8.18.4, `detect` reads `source` and selects files with `--no-git`, stdin otherwise with `--pipe`, and Git history otherwise. At all three tags the root registers persistent `--source` with default `.`.
5. **Secrets never enter a command line.** A process's arguments are readable through `/proc/<pid>/cmdline`, which is what `ps` prints; on a default Linux that means every other user on the host, for as long as the process runs, and the command is then written to your shell history. A `hidepid` proc mount or a separate PID namespace narrows who can see it, neither is the default, and neither covers the history. Prefer a flag that reads from stdin (`htpasswd -i`, `docker login --password-stdin`, `gh auth login --with-token`), a file the tool reads itself (`~/.pgpass`, `curl --netrc`; create it with `umask 077` and keep it mode `0600`, since it stores the secret in plaintext and PostgreSQL ignores a `~/.pgpass` that group or others can read), or an environment variable where the tool offers nothing better. As this guide's advice, where a value has to be typed, use `read -rs` to keep terminal input hidden (`-s`) and preserve backslashes (`-r`); as this guide's assessment, because `read` consumes input rather than a command, this keeps the typed value out of shell history. Bash documents that `set -x` prints commands and arguments after expansion; therefore, as this guide's advice, a script that expands a secret into a pipeline (including the `printf`-into-`--password-stdin` pattern below) must turn tracing off around it, because reading from stdin protects the argument list but not the trace.

   This block assumes a clean Bash shell and prompts for the registry token instead of using an ambient `TOKEN`. As this guide's advice, paste the token alone at the hidden prompt: a multi-line paste leaves every line after the first for your shell to run. The block resets `DEBUG`, `RETURN` and `ERR` traps with `trap - DEBUG RETURN ERR`, turns tracing, allexport and errexit off with `set +x +a +e`, then enables pipefail with `set -o pipefail`. It clears inherited `TOKEN` attributes via `unset -n` and `unset -v`, unsets `IFS` with `unset -n IFS` (which also removes an `IFS` nameref) and refuses a readonly `IFS`, then unsets the unexported variable with an `EXIT` trap. It exits without continuing if `TOKEN` cannot be cleared, `IFS` is readonly or `read` fails, and refuses an empty value, a placeholder or a control character. As this guide's assessment under these clean-shell assumptions, the entered token stays out of history, argv and the environment; process memory is still readable by the same account and root, and this does not erase an earlier export. Docker stores the login in its configured credential store or configuration file, as described in rule 9.

   ```bash
   (
     trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
     set +x +a +e
     set -o pipefail
     { unset -n TOKEN && unset -v TOKEN; } 2>/dev/null ||
       { echo 'cannot clear TOKEN in this shell'; exit 2; }
     { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell'; exit 2; }
     trap 'unset -v TOKEN' EXIT
     printf 'Registry token (input hidden): '
     IFS= read -r -s TOKEN || { printf '\n'; echo 'no secret read'; exit 2; }
     printf '\n'
     case "$TOKEN" in
       ''|*REPLACE_WITH_*|*[[:cntrl:]]*) echo 'empty secret, placeholder or control character'; exit 2 ;;
     esac
     printf '%s' "$TOKEN" | docker login ghcr.io -u "$USER" --password-stdin
   )
   ```

   There is no probe for this rule, and the obvious one is worse than none. `ps -eo args | grep -i 'password\|token\|secret'` finds only commands that spell the word out, such as `docker login --password hunter2`. It does not match `htpasswd -cbs .htpasswd admin Xk29fQ7LmVt3w9Zr`, or `mysql -pHunter2`, or `curl -u admin:hunter2`, because a real secret is a random string and `.htpasswd` does not contain the word "password". A snapshot also misses every short-lived process, which is most of them. A check that reads clean while the exposure is running is worse than no check, so this rule is enforced by review and by reaching for the stdin flag, not by grep.

6. **CI/CD secrets live in the platform's secret store** (for example GitHub Actions secrets), scoped to the jobs that need them, never echoed into logs or artefacts.
7. **Keys and customer data stay out of AI-model prompts.** A prompt to a public LLM, or to a hosted API outside your data agreement, becomes that provider's chat transcript and log, which the leak section below counts the same as any other chat or log. Keep API keys and credentials out of prompts entirely, user and system alike, and keep customer data out of any prompt to a service outside your data agreement. A system prompt is not a secret store and is not a security control: OWASP records credentials or a role and permission map placed there as System Prompt Leakage, disclosable by a plain extraction request, so keep them out and enforce authorization outside the model. A tool that needs a credential loads a scoped, revocable one through its own configuration, outside the model's context, so no prompt can echo it ([mcp-servers.md](mcp-servers.md)).
8. **Confidential business rules are secrets too.** A confidential pricing formula, allocation rule, or customer-specific process is protected because it is confidential, not because it is code. Keep it out of public repositories, out of anything that ships to the browser (a `NEXT_PUBLIC_` or `VITE_` value, or logic implemented in client-shipped code or a source map, per [web-exposure.md](web-exposure.md)), and out of a public LLM, on the same reasoning as a key.
9. **Credential-bearing config files stay out of the repository too.** Some working files hold live credentials in plaintext, so keep them, and any copy of them, out of version control alongside `.env` and `*.pem`. With local state, the default, a Terraform state file is written as plaintext in the working directory and can contain secret resource values, including any marked `sensitive`; gitignore `*.tfstate` and `*.tfstate.*` (the state, its `.backup`, and per-workspace copies). A kubeconfig can embed a base64 client private key in `client-key-data`, or a bearer token. `~/.docker/config.json` holds registry logins base64-encoded, which is encoding rather than encryption, whenever Docker keeps them in the file rather than an external credential store. The rule-4 scanners may flag a committed one, but a base64-wrapped key or an unpatterned password can pass them clean, so never rely on them: the fix is to not commit the file.

## When a secret leaks

Order matters:

1. **Rotate first.** Revoke the exposed credential at its provider and issue a new one. A secret that reached a public repository, a chat, a log, or a paste is compromised even if deleted seconds later; scrapers and forks already have it.
2. Only then clean the history if required (for example with [git-filter-repo](https://github.com/newren/git-filter-repo)), understanding that cleaning is hygiene, never containment: it does not unpublish anything.
3. Check provider logs for use of the leaked credential during the exposure window.

## Encrypting secrets that must be versioned

When a team needs configuration secrets in git (for example GitOps deployments), encrypt them: [sops](https://github.com/getsops/sops) with [age](https://github.com/FiloSottile/age) keys encrypts the values inside YAML/JSON/ENV files while leaving the structure diffable. The decryption key itself stays out of the repository.

## Verify (REASONED: scanner outcomes follow the cited gitleaks source, by source reading, and README, and secret-handling guidance; no exposed/fixed scan run is recorded)

```bash
gitleaks git . && echo clean
grep -rlIE "sk-|AKIA|ASIA|ghp_|-----BEGIN" --exclude-dir=node_modules --exclude-dir=.git .   # -r recurses, -l prints only the filename (never the matching secret), -I assumes unprocessed input does not match after null binary data is discovered, --exclude-dir skips a whole tree rather than filtering matched lines; -E uses extended regular expressions; as this guide's assessment, this scan is crude but fast
```

On every push, gitleaks (8.19.1 or later; see rule 4 for older releases) must exit 0 with no findings (the `&& echo clean` then prints `clean`). As this guide's assessment, the grep is a supplementary pattern search, not proof that no secret is present: as this guide's advice, treat any filename it prints as a finding to inspect privately, empty output as no match for these patterns only, and a non-zero exit caused by a read error as a failed check. gitleaks, which scans by rule rather than by a few prefixes, is the primary gate.

## Sources (checked September 2026)

- Docker build variables (`ENV` persists in containers; build arguments may persist in metadata, provenance and history), at 4e9a5751518ed8223a8dcde53693badddd72604f: https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/build/building/variables.md#L17-L52
- Docker build secrets (temporary mounts for build instructions), at 4e9a5751518ed8223a8dcde53693badddd72604f: https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/build/building/secrets.md#L13-L22
- Docker image history command (image history and creation-command output), at 4e9a5751518ed8223a8dcde53693badddd72604f: https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/data/cli/engine/docker_image_history.yaml#L1-L118
- OWASP Secrets Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- AWS Secrets Manager overview (rolling, checked October 2026): https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html
- Google Cloud Secret Manager overview (rolling, checked October 2026): https://docs.cloud.google.com/secret-manager/docs/overview
- Azure Key Vault overview (rolling, checked October 2026): https://learn.microsoft.com/en-us/azure/key-vault/general/overview
- gitleaks 8.19.1 to 8.30.1 path handling, v8.19.1 `git` source reading without a run (checked October 2026): https://github.com/gitleaks/gitleaks/blob/9463ffaa5e9efc94ee235972d1519eac2844fad3/cmd/git.go#L33-L42
- gitleaks 8.19.1 to 8.30.1 path handling, v8.19.1 `dir` source reading without a run (checked October 2026): https://github.com/gitleaks/gitleaks/blob/9463ffaa5e9efc94ee235972d1519eac2844fad3/cmd/directory.go#L26-L34
- gitleaks 8.19.1 to 8.30.1, earlier review: v8.30.1 `git` path handling (checked October 2026): https://github.com/gitleaks/gitleaks/blob/v8.30.1/cmd/git.go#L33-L43
- gitleaks 8.19.1 to 8.30.1, earlier review: v8.30.1 `dir` path handling (checked October 2026): https://github.com/gitleaks/gitleaks/blob/v8.30.1/cmd/directory.go#L25-L34
- gitleaks 8.19.1 to 8.30.1, earlier review: v8.30.1 default exit codes (checked October 2026): https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md#L645-L653
- gitleaks v8.19.0 root flags and conditional `source` lookup, source reading without a run (checked October 2026): https://github.com/gitleaks/gitleaks/blob/44ad62e0b103f7907c4b3dd494aca64e4fefd94f/cmd/root.go
- gitleaks v8.19.0 `git` flags and unused positional path, source reading without a run (checked October 2026): https://github.com/gitleaks/gitleaks/blob/44ad62e0b103f7907c4b3dd494aca64e4fefd94f/cmd/git.go
- gitleaks v8.19.0 `dir` flags and unused positional path, source reading without a run (checked October 2026): https://github.com/gitleaks/gitleaks/blob/44ad62e0b103f7907c4b3dd494aca64e4fefd94f/cmd/directory.go
- gitleaks v8.19.0 local `detect` flags and scan selection, source reading without a run (checked October 2026): https://github.com/gitleaks/gitleaks/blob/44ad62e0b103f7907c4b3dd494aca64e4fefd94f/cmd/detect.go
- gitleaks v8.19.0 local `protect` flags, source reading without a run (checked October 2026): https://github.com/gitleaks/gitleaks/blob/44ad62e0b103f7907c4b3dd494aca64e4fefd94f/cmd/protect.go
- gitleaks v8.19.0 `stdin` registration, source reading without a run (checked October 2026): https://github.com/gitleaks/gitleaks/blob/44ad62e0b103f7907c4b3dd494aca64e4fefd94f/cmd/stdin.go
- gitleaks v8.19.0 `version` registration, source reading without a run (checked October 2026): https://github.com/gitleaks/gitleaks/blob/44ad62e0b103f7907c4b3dd494aca64e4fefd94f/cmd/version.go
- gitleaks v8.19.0 top-level command inventory, source reading without a run (checked October 2026): https://github.com/gitleaks/gitleaks/tree/44ad62e0b103f7907c4b3dd494aca64e4fefd94f/cmd
- gitleaks v8.19.0 `generate` directory listing only, source reading without a run (checked October 2026): https://github.com/gitleaks/gitleaks/tree/44ad62e0b103f7907c4b3dd494aca64e4fefd94f/cmd/generate
- gitleaks v8.18.4 README `--source` default (checked October 2026): https://github.com/gitleaks/gitleaks/blob/02808f45d038526bfcceebcbf6421c1047997ff9/README.md#L162
- gitleaks v8.18.4 README `detect` and `--no-git` (checked October 2026): https://github.com/gitleaks/gitleaks/blob/02808f45d038526bfcceebcbf6421c1047997ff9/README.md#L172-L183
- gitleaks v8.18.4 root persistent `--source`, source reading without a run (checked October 2026): https://github.com/gitleaks/gitleaks/blob/02808f45d038526bfcceebcbf6421c1047997ff9/cmd/root.go#L41-L65
- gitleaks root persistent `--source` comparison with v8.18.4: v8.17.0 source reading without a run (checked October 2026): https://github.com/gitleaks/gitleaks/blob/7804d652c0460f0b61ea9bb2c1f202bfcdbbf144/cmd/root.go#L38-L56
- gitleaks root persistent `--source` comparison with v8.18.4: v8.18.0 source reading without a run (checked October 2026): https://github.com/gitleaks/gitleaks/blob/45266551ba14dcc339106a08acf6cd0a5e81c76f/cmd/root.go#L38-L56
- gitleaks v8.18.4 `detect` scan selection, source reading without a run (checked October 2026): https://github.com/gitleaks/gitleaks/blob/02808f45d038526bfcceebcbf6421c1047997ff9/cmd/detect.go
- gitleaks `detect` comparison with v8.18.4: v8.17.0 source reading without a run (checked October 2026): https://github.com/gitleaks/gitleaks/blob/7804d652c0460f0b61ea9bb2c1f202bfcdbbf144/cmd/detect.go
- gitleaks `detect` comparison with v8.18.4: v8.18.0 source reading without a run (checked October 2026): https://github.com/gitleaks/gitleaks/blob/45266551ba14dcc339106a08acf6cd0a5e81c76f/cmd/detect.go
- trufflehog: https://github.com/trufflesecurity/trufflehog
- sops: https://github.com/getsops/sops and age: https://github.com/FiloSottile/age
- git-filter-repo: https://github.com/newren/git-filter-repo
- proc_pid_cmdline(5), for why a command line is readable by other users: https://man7.org/linux/man-pages/man5/proc_pid_cmdline.5.html
- docker login, for `--password-stdin`, and that `~/.docker/config.json` stores credentials base64-encoded when no credential store is set: https://docs.docker.com/reference/cli/docker/login/
- Terraform, that local state is written as a plaintext file that can hold secret resource values: https://developer.hashicorp.com/terraform/language/manage-sensitive-data
- Kubernetes kubeconfig API, for `client-key-data` (a client key, serialized base64) and the bearer `token`: https://kubernetes.io/docs/reference/config-api/kubeconfig.v1/
- gh auth login, for `--with-token`: https://cli.github.com/manual/gh_auth_login
- htpasswd, for `-i` and what Apache says about `-b`: https://httpd.apache.org/docs/2.4/programs/htpasswd.html
- OWASP GenAI, LLM07:2025 System Prompt Leakage (a system prompt is not a secret and should not hold credentials or a role and permission map): https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/
- PostgreSQL password file, that `~/.pgpass` must disallow all group and world access (`0600` is the documented example) or PostgreSQL ignores it: https://www.postgresql.org/docs/current/libpq-pgpass.html
- curl `.netrc`, that the file should not be readable by anyone besides the user: https://everything.curl.dev/usingcurl/netrc.html
- Next.js environment variables, that `.env.local`, `.env.production`, and other `.env.*` files are loaded (so they hold secrets and belong in `.gitignore`): https://nextjs.org/docs/app/guides/environment-variables
- Git 2.42.0 ignore patterns, negation and already-tracked files (checked October 2026): https://git-scm.com/docs/gitignore/2.42.0
- OpenSSL 3.0 `rand` byte count and `-base64` encoding (checked October 2026): https://docs.openssl.org/3.0/man1/openssl-rand/
- Python 3.13 `secrets.token_urlsafe` (checked October 2026): https://docs.python.org/3.13/library/secrets.html#secrets.token_urlsafe
- Vite 6 environment variables (`VITE_` values exposed to client code) (checked October 2026): https://v6.vite.dev/guide/env-and-mode
- GNU Bash reference manual, bash-5.3 (checked October 2026): read `-r`/`-s` 5629-5637 https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5629; `set -a` 5917-5921 https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5917; `allexport` 6000-6001 https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n6000; `set -x` 6122-6128 https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n6122; turning set options off 6194-6196 https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n6194; `declare` attributes 5161-5195 https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5161; `unset -n`/`-v` 4852-4876 https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n4852; `trap` and sigspecs 4740-4808 https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n4740; errexit 5929-5944 https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5929; pipefail 6062-6065 https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n6062
- GNU grep file and directory selection (`-r`, `-I`, `--exclude-dir`; rolling) (checked October 2026): https://www.gnu.org/software/grep/manual/html_node/File-and-Directory-Selection.html
- GNU grep general output control (`-l`; rolling) (checked October 2026): https://www.gnu.org/software/grep/manual/html_node/General-Output-Control.html
- GNU grep Programs (`-E` selects extended regular expressions; rolling) (checked October 2026): https://www.gnu.org/software/grep/manual/html_node/grep-Programs.html
- GNU grep exit status (0 match, 1 no match, 2 error; rolling) (checked October 2026): https://www.gnu.org/software/grep/manual/html_node/Exit-Status.html


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- git-ignore: Git ignore patterns (2.42.0)
- gitleaks: gitleaks git/dir path argument (8.19.1 to 8.30.1)
- gitleaks-8190: gitleaks 8.19.0 git/dir source flag (v8.19.0)
- gitleaks-detect: gitleaks detect before 8.19.0 (v8.18.4)
- trufflehog: TruffleHog (unknown)
- sops: SOPS (unknown)
- age: age (unknown)
- git-filter-repo: git-filter-repo (unknown)
- openssl-rand: OpenSSL random bytes (3.0)
- python-secrets: Python secrets (3.13)
- docker-build: Docker build and image history documentation (4e9a5751518ed8223a8dcde53693badddd72604f)
- proc: Linux procfs (unknown)
- docker: Docker login (unknown)
- terraform: Terraform (unknown)
- kubernetes: Kubernetes kubeconfig (unknown)
- gh: GitHub CLI (unknown)
- apache: htpasswd (unknown)
- postgres: PostgreSQL password file (unknown)
- curl: curl netrc (unknown)
- next: Next.js (unknown)
- vite-env: Vite environment variables (6)
- aws-store: AWS Secrets Manager overview (unknown)
- google-store: Google Cloud Secret Manager overview (unknown)
- azure-store: Azure Key Vault overview (unknown)
- bash: GNU Bash reference manual (bash-5.3)
- grep: GNU grep (unknown)
- owasp: OWASP secret handling (unknown)

Claims (full source mapping in the JSON block below):

- gitignore (REASONED; owasp, next, git-ignore): Ignore .env, .env.*, *.key and *.pem before committing; allow only a secret-free template. Already tracked files remain tracked.
- runtime-storage (REASONED; owasp, docker-build, aws-store, google-store, azure-store): Load secrets from environment or a secret manager, including AWS Secrets Manager, Google Secret Manager, Azure Key Vault or the platform store; never put secrets in Dockerfile ENV/ARG, images or build logs; use temporary secret mounts for build-time secrets.
- image-history (REASONED; docker-build): The Docker image history reference's example history output shows an ENV instruction with its value; Docker image history shows image history; as this guide's assessment, Docker image history does not show every secret value.
- random (REASONED; owasp, openssl-rand, python-secrets): Generate a random secret per service and environment with the shown OpenSSL or Python command; never share staging and production credentials.
- scanners (REASONED; gitleaks, trufflehog): Scan before every push and in CI with gitleaks or TruffleHog. By source reading at every gitleaks tag from v8.19.1 to v8.30.1, cited at both ends, without a run, git and dir take the scan path from a positional argument that defaults to the current directory, as the shown gitleaks git . and gitleaks dir . commands need.
- scanners-8190 (REASONED; gitleaks-8190): By source reading without a run at v8.19.0, only detect and protect register source across all seven top-level cmd files, each locally; neither git nor dir uses args. Both commands, and root initConfig when both --config and GITLEAKS_CONFIG are empty or unset, read source and call log.Fatal on lookup error; no run outcome is established.
- scanners-detect (REASONED; gitleaks-detect): By source reading without a run at v8.17.0, v8.18.0 and v8.18.4, detect reads source and selects files with --no-git, otherwise stdin with --pipe, otherwise Git history. At all three tags the root registers persistent --source with default '.'.
- argv (REASONED; proc, apache): Arguments expose secrets through procfs, ps and shell history; hidepid or PID namespaces narrow process visibility without covering history.
- stdin (REASONED; apache, docker, gh): Use htpasswd -i, docker login --password-stdin or gh auth login --with-token to avoid secret arguments.
- credential-files (REASONED; postgres, curl): Protect plaintext credential files with umask 077 and mode 0600; PostgreSQL ignores group/world-readable .pgpass.
- shell-input (REASONED; bash, docker, proc): As this guide's assessment, hidden read input avoids history; as this guide's advice, tracing must be off around expansion. The clean-Bash login block clears inherited TOKEN attributes, turns tracing, allexport and errexit off, enables pipefail, and removes TOKEN on exit.
- shell-limits (REASONED; bash, proc, docker): As this guide's assessment under the stated clean-Bash assumptions, the prompted token stays out of argv and environment; same-account/root memory access and earlier exports remain outside this protection.
- argv-review (REASONED; proc): A ps/grep snapshot misses unlabelled secrets and short-lived processes; review secret-input paths instead of treating a clean snapshot as proof.
- ci-store (REASONED; owasp): Scope CI/CD platform secrets to the jobs needing them; never echo them into logs or artefacts.
- prompt-secrets (REASONED; owasp): Keep credentials out of all model prompts and customer data outside unapproved services; system prompts are disclosable and authorization belongs outside the model.
- business-rules (REASONED; owasp, next, vite-env): Keep confidential business logic out of public repositories, browser-shipped code and public LLM prompts; public environment prefixes and source maps can expose it.
- terraform-state (REASONED; terraform): Default local Terraform state is plaintext and may contain sensitive values; ignore *.tfstate and `*.tfstate.*` including backups and workspace copies.
- kubeconfig (REASONED; kubernetes): Kubeconfig can embed a base64 client-key-data private key or bearer token; exclude credential-bearing files and copies from version control.
- docker-store (REASONED; docker, owasp): Docker stores logins in its credential store or base64-encoded config.json; encoding is not encryption and scanners can miss encoded or unpatterned secrets.
- leak-rotation (REASONED; owasp): Revoke and replace a leaked credential before cleanup; deletion cannot undo public repository, chat, log or paste exposure.
- history-cleanup (REASONED; git-filter-repo, owasp): History rewriting with git-filter-repo is hygiene after rotation, not containment or unpublishing.
- leak-audit (REASONED; owasp): Review provider logs for use of the leaked credential during its exposure window.
- encrypted-git (REASONED; sops, age): SOPS with age encrypts YAML/JSON/ENV values while preserving structure for secrets that must be versioned; keep decryption keys outside the repository.
- verify-scan (REASONED; gitleaks): With gitleaks 8.19.1 or later, gitleaks must exit 0 with no findings before clean is printed; the v8.30.1 README lists exit 0 for no leaks and 1 for leaks or an error. This rule-based scan is the primary gate.
- verify-patterns (REASONED; grep, owasp): Supplementary grep prints filenames only, when null binary data is discovered assumes unprocessed input does not match, skips excluded trees; as this guide's advice, a non-zero exit caused by a read error is a failed check; as this guide's assessment, empty output is not proof of no secret. GNU grep documents -E as extended regular expression syntax.

````json
{
  "schema": 1,
  "checked": "2026-10-05",
  "documentation_checked": "2026-09",
  "body_sha256": "78cb9a974aecadb0b951192b146f9c657d0dc9f98471b619905490a4b90e67ba",
  "components": {
    "git-ignore": {
      "name": "Git ignore patterns",
      "basis": "2.42.0",
      "sources": {
        "s90ce7c8605d9": "https://git-scm.com/docs/gitignore/2.42.0"
      }
    },
    "gitleaks": {
      "name": "gitleaks git/dir path argument",
      "basis": "8.19.1 to 8.30.1",
      "sources": {
        "s4e82b98bf700": "https://github.com/gitleaks/gitleaks/blob/9463ffaa5e9efc94ee235972d1519eac2844fad3/cmd/git.go#L33-L42",
        "sc7929445f947": "https://github.com/gitleaks/gitleaks/blob/9463ffaa5e9efc94ee235972d1519eac2844fad3/cmd/directory.go#L26-L34",
        "s2a515c553a16": "https://github.com/gitleaks/gitleaks/blob/v8.30.1/cmd/git.go#L33-L43",
        "s3cedc5927daf": "https://github.com/gitleaks/gitleaks/blob/v8.30.1/cmd/directory.go#L25-L34",
        "s8b08240c42e9": "https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md#L645-L653"
      }
    },
    "gitleaks-8190": {
      "name": "gitleaks 8.19.0 git/dir source flag",
      "basis": "v8.19.0",
      "sources": {
        "s38ee01a95c8c": "https://github.com/gitleaks/gitleaks/blob/44ad62e0b103f7907c4b3dd494aca64e4fefd94f/cmd/root.go",
        "s5abcb8b428db": "https://github.com/gitleaks/gitleaks/blob/44ad62e0b103f7907c4b3dd494aca64e4fefd94f/cmd/git.go",
        "s8db158cb815b": "https://github.com/gitleaks/gitleaks/blob/44ad62e0b103f7907c4b3dd494aca64e4fefd94f/cmd/directory.go",
        "s68724a6b5a24": "https://github.com/gitleaks/gitleaks/blob/44ad62e0b103f7907c4b3dd494aca64e4fefd94f/cmd/detect.go",
        "s913053b5ad1e": "https://github.com/gitleaks/gitleaks/blob/44ad62e0b103f7907c4b3dd494aca64e4fefd94f/cmd/protect.go",
        "s189c08d2f974": "https://github.com/gitleaks/gitleaks/blob/44ad62e0b103f7907c4b3dd494aca64e4fefd94f/cmd/stdin.go",
        "s4b5d9b2ab7a1": "https://github.com/gitleaks/gitleaks/blob/44ad62e0b103f7907c4b3dd494aca64e4fefd94f/cmd/version.go",
        "s8a2e9dc86ccd": "https://github.com/gitleaks/gitleaks/tree/44ad62e0b103f7907c4b3dd494aca64e4fefd94f/cmd",
        "s43b67b6788dd": "https://github.com/gitleaks/gitleaks/tree/44ad62e0b103f7907c4b3dd494aca64e4fefd94f/cmd/generate"
      }
    },
    "gitleaks-detect": {
      "name": "gitleaks detect before 8.19.0",
      "basis": "v8.18.4",
      "sources": {
        "s6686fd9533da": "https://github.com/gitleaks/gitleaks/blob/02808f45d038526bfcceebcbf6421c1047997ff9/README.md#L162",
        "s71b141fe4768": "https://github.com/gitleaks/gitleaks/blob/02808f45d038526bfcceebcbf6421c1047997ff9/README.md#L172-L183",
        "s342bdd9096ec": "https://github.com/gitleaks/gitleaks/blob/02808f45d038526bfcceebcbf6421c1047997ff9/cmd/root.go#L41-L65",
        "sc8ca694b4c7a": "https://github.com/gitleaks/gitleaks/blob/02808f45d038526bfcceebcbf6421c1047997ff9/cmd/detect.go",
        "sdf22d8b973ff": "https://github.com/gitleaks/gitleaks/blob/7804d652c0460f0b61ea9bb2c1f202bfcdbbf144/cmd/detect.go",
        "sc459999393a5": "https://github.com/gitleaks/gitleaks/blob/45266551ba14dcc339106a08acf6cd0a5e81c76f/cmd/detect.go",
        "s0c9e8f865e54": "https://github.com/gitleaks/gitleaks/blob/7804d652c0460f0b61ea9bb2c1f202bfcdbbf144/cmd/root.go#L38-L56",
        "seb8727e916d2": "https://github.com/gitleaks/gitleaks/blob/45266551ba14dcc339106a08acf6cd0a5e81c76f/cmd/root.go#L38-L56"
      }
    },
    "trufflehog": {
      "name": "TruffleHog",
      "basis": "unknown",
      "sources": {
        "s5450689a9bb8": "https://github.com/trufflesecurity/trufflehog"
      }
    },
    "sops": {
      "name": "SOPS",
      "basis": "unknown",
      "sources": {
        "s78c5bb528dc4": "https://github.com/getsops/sops"
      }
    },
    "age": {
      "name": "age",
      "basis": "unknown",
      "sources": {
        "sca8b0d211739": "https://github.com/FiloSottile/age"
      }
    },
    "git-filter-repo": {
      "name": "git-filter-repo",
      "basis": "unknown",
      "sources": {
        "s95bf8a949d5e": "https://github.com/newren/git-filter-repo"
      }
    },
    "openssl-rand": {
      "name": "OpenSSL random bytes",
      "basis": "3.0",
      "sources": {
        "s11d11381b080": "https://docs.openssl.org/3.0/man1/openssl-rand/"
      }
    },
    "python-secrets": {
      "name": "Python secrets",
      "basis": "3.13",
      "sources": {
        "sd2e8196eaa96": "https://docs.python.org/3.13/library/secrets.html#secrets.token_urlsafe"
      }
    },
    "docker-build": {
      "name": "Docker build and image history documentation",
      "basis": "4e9a5751518ed8223a8dcde53693badddd72604f",
      "sources": {
        "sd8afa286c173": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/build/building/variables.md#L17-L52",
        "s07e00829f121": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/build/building/secrets.md#L13-L22",
        "s6283b172a5c6": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/data/cli/engine/docker_image_history.yaml#L1-L118"
      }
    },
    "proc": {
      "name": "Linux procfs",
      "basis": "unknown",
      "sources": {
        "s801d5f1ee88d": "https://man7.org/linux/man-pages/man5/proc_pid_cmdline.5.html"
      }
    },
    "docker": {
      "name": "Docker login",
      "basis": "unknown",
      "sources": {
        "sf8243a183d67": "https://docs.docker.com/reference/cli/docker/login/"
      }
    },
    "terraform": {
      "name": "Terraform",
      "basis": "unknown",
      "sources": {
        "s8efa1a4bb953": "https://developer.hashicorp.com/terraform/language/manage-sensitive-data"
      }
    },
    "kubernetes": {
      "name": "Kubernetes kubeconfig",
      "basis": "unknown",
      "sources": {
        "se41a53ea6778": "https://kubernetes.io/docs/reference/config-api/kubeconfig.v1/"
      }
    },
    "gh": {
      "name": "GitHub CLI",
      "basis": "unknown",
      "sources": {
        "sf0b01ee9b3e1": "https://cli.github.com/manual/gh_auth_login"
      }
    },
    "apache": {
      "name": "htpasswd",
      "basis": "unknown",
      "sources": {
        "scde9004bb967": "https://httpd.apache.org/docs/2.4/programs/htpasswd.html"
      }
    },
    "postgres": {
      "name": "PostgreSQL password file",
      "basis": "unknown",
      "sources": {
        "s198d4780d9a4": "https://www.postgresql.org/docs/current/libpq-pgpass.html"
      }
    },
    "curl": {
      "name": "curl netrc",
      "basis": "unknown",
      "sources": {
        "s3a0a54039912": "https://everything.curl.dev/usingcurl/netrc.html"
      }
    },
    "next": {
      "name": "Next.js",
      "basis": "unknown",
      "sources": {
        "s964651d4eed4": "https://nextjs.org/docs/app/guides/environment-variables"
      }
    },
    "vite-env": {
      "name": "Vite environment variables",
      "basis": "6",
      "sources": {
        "sba07c9b57bd9": "https://v6.vite.dev/guide/env-and-mode"
      }
    },
    "aws-store": {
      "name": "AWS Secrets Manager overview",
      "basis": "unknown",
      "sources": {
        "s81b41c17ad57": "https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html"
      }
    },
    "google-store": {
      "name": "Google Cloud Secret Manager overview",
      "basis": "unknown",
      "sources": {
        "scd27be211781": "https://docs.cloud.google.com/secret-manager/docs/overview"
      }
    },
    "azure-store": {
      "name": "Azure Key Vault overview",
      "basis": "unknown",
      "sources": {
        "seb86b29f4951": "https://learn.microsoft.com/en-us/azure/key-vault/general/overview"
      }
    },
    "bash": {
      "name": "GNU Bash reference manual",
      "basis": "bash-5.3",
      "sources": {
        "sb38bf74a89b0": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5629",
        "s8c59508bd4c8": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5917",
        "s04ec4ba49971": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n6000",
        "se62fd3ad4fc3": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n6122",
        "s2df39d2c9c1c": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n6194",
        "s8447036b2114": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5161",
        "s3255eca7e496": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n4852",
        "s93dcf5ba0a87": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n4740",
        "s8016d1aecfca": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5929",
        "sf6c6f542c26c": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n6062"
      }
    },
    "grep": {
      "name": "GNU grep",
      "basis": "unknown",
      "sources": {
        "s33689bc366bf": "https://www.gnu.org/software/grep/manual/html_node/File-and-Directory-Selection.html",
        "s2c1251092e66": "https://www.gnu.org/software/grep/manual/html_node/General-Output-Control.html",
        "sea43e82b0753": "https://www.gnu.org/software/grep/manual/html_node/Exit-Status.html",
        "sbd30b628a5b8": "https://www.gnu.org/software/grep/manual/html_node/grep-Programs.html"
      }
    },
    "owasp": {
      "name": "OWASP secret handling",
      "basis": "unknown",
      "sources": {
        "s26a987a1053b": "https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html",
        "s4564d1912a87": "https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/"
      }
    }
  },
  "claims": {
    "gitignore": {"text": "Ignore .env, .env.*, *.key and *.pem before committing; allow only a secret-free template. Already tracked files remain tracked.", "components": ["owasp", "next", "git-ignore"], "sources": ["owasp:s26a987a1053b", "next:s964651d4eed4", "git-ignore:s90ce7c8605d9"], "status": "REASONED"},
    "runtime-storage": {"text": "Load secrets from environment or a secret manager, including AWS Secrets Manager, Google Secret Manager, Azure Key Vault or the platform store; never put secrets in Dockerfile ENV/ARG, images or build logs; use temporary secret mounts for build-time secrets.", "components": ["owasp", "docker-build", "aws-store", "google-store", "azure-store"], "sources": ["owasp:s26a987a1053b", "docker-build:sd8afa286c173", "docker-build:s07e00829f121", "aws-store:s81b41c17ad57", "google-store:scd27be211781", "azure-store:seb86b29f4951"], "status": "REASONED"},
    "image-history": {"text": "The Docker image history reference's example history output shows an ENV instruction with its value; Docker image history shows image history; as this guide's assessment, Docker image history does not show every secret value.", "components": ["docker-build"], "sources": ["docker-build:s6283b172a5c6"], "status": "REASONED"},
    "random": {"text": "Generate a random secret per service and environment with the shown OpenSSL or Python command; never share staging and production credentials.", "components": ["owasp", "openssl-rand", "python-secrets"], "sources": ["owasp:s26a987a1053b", "openssl-rand:s11d11381b080", "python-secrets:sd2e8196eaa96"], "status": "REASONED"},
    "scanners": {"text": "Scan before every push and in CI with gitleaks or TruffleHog. By source reading at every gitleaks tag from v8.19.1 to v8.30.1, cited at both ends, without a run, git and dir take the scan path from a positional argument that defaults to the current directory, as the shown gitleaks git . and gitleaks dir . commands need.", "components": ["gitleaks", "trufflehog"], "sources": ["gitleaks:s4e82b98bf700", "gitleaks:sc7929445f947", "gitleaks:s2a515c553a16", "gitleaks:s3cedc5927daf", "trufflehog:s5450689a9bb8"], "status": "REASONED"},
    "scanners-8190": {"text": "By source reading without a run at v8.19.0, only detect and protect register source across all seven top-level cmd files, each locally; neither git nor dir uses args. Both commands, and root initConfig when both --config and GITLEAKS_CONFIG are empty or unset, read source and call log.Fatal on lookup error; no run outcome is established.", "components": ["gitleaks-8190"], "sources": ["gitleaks-8190:s38ee01a95c8c", "gitleaks-8190:s5abcb8b428db", "gitleaks-8190:s8db158cb815b", "gitleaks-8190:s68724a6b5a24", "gitleaks-8190:s913053b5ad1e", "gitleaks-8190:s189c08d2f974", "gitleaks-8190:s4b5d9b2ab7a1", "gitleaks-8190:s8a2e9dc86ccd", "gitleaks-8190:s43b67b6788dd"], "status": "REASONED"},
    "scanners-detect": {"text": "By source reading without a run at v8.17.0, v8.18.0 and v8.18.4, detect reads source and selects files with --no-git, otherwise stdin with --pipe, otherwise Git history. At all three tags the root registers persistent --source with default '.'.", "components": ["gitleaks-detect"], "sources": ["gitleaks-detect:s6686fd9533da", "gitleaks-detect:s71b141fe4768", "gitleaks-detect:s342bdd9096ec", "gitleaks-detect:sc8ca694b4c7a", "gitleaks-detect:sdf22d8b973ff", "gitleaks-detect:sc459999393a5", "gitleaks-detect:s0c9e8f865e54", "gitleaks-detect:seb8727e916d2"], "status": "REASONED"},
    "argv": {"text": "Arguments expose secrets through procfs, ps and shell history; hidepid or PID namespaces narrow process visibility without covering history.", "components": ["proc", "apache"], "sources": ["proc:s801d5f1ee88d", "apache:scde9004bb967"], "status": "REASONED"},
    "stdin": {"text": "Use htpasswd -i, docker login --password-stdin or gh auth login --with-token to avoid secret arguments.", "components": ["apache", "docker", "gh"], "sources": ["apache:scde9004bb967", "docker:sf8243a183d67", "gh:sf0b01ee9b3e1"], "status": "REASONED"},
    "credential-files": {"text": "Protect plaintext credential files with umask 077 and mode 0600; PostgreSQL ignores group/world-readable .pgpass.", "components": ["postgres", "curl"], "sources": ["postgres:s198d4780d9a4", "curl:s3a0a54039912"], "status": "REASONED"},
    "shell-input": {"text": "As this guide's assessment, hidden read input avoids history; as this guide's advice, tracing must be off around expansion. The clean-Bash login block clears inherited TOKEN attributes, turns tracing, allexport and errexit off, enables pipefail, and removes TOKEN on exit.", "components": ["bash", "docker", "proc"], "sources": ["bash:sb38bf74a89b0", "bash:s8c59508bd4c8", "bash:s04ec4ba49971", "bash:se62fd3ad4fc3", "bash:s2df39d2c9c1c", "bash:s8447036b2114", "bash:s3255eca7e496", "bash:s93dcf5ba0a87", "bash:s8016d1aecfca", "bash:sf6c6f542c26c", "docker:sf8243a183d67", "proc:s801d5f1ee88d"], "status": "REASONED"},
    "shell-limits": {"text": "As this guide's assessment under the stated clean-Bash assumptions, the prompted token stays out of argv and environment; same-account/root memory access and earlier exports remain outside this protection.", "components": ["bash", "proc", "docker"], "sources": ["bash:sb38bf74a89b0", "bash:s8c59508bd4c8", "bash:s04ec4ba49971", "bash:se62fd3ad4fc3", "bash:s2df39d2c9c1c", "bash:s8447036b2114", "bash:s3255eca7e496", "bash:s93dcf5ba0a87", "bash:s8016d1aecfca", "bash:sf6c6f542c26c", "proc:s801d5f1ee88d", "docker:sf8243a183d67"], "status": "REASONED"},
    "argv-review": {"text": "A ps/grep snapshot misses unlabelled secrets and short-lived processes; review secret-input paths instead of treating a clean snapshot as proof.", "components": ["proc"], "sources": ["proc:s801d5f1ee88d"], "status": "REASONED"},
    "ci-store": {"text": "Scope CI/CD platform secrets to the jobs needing them; never echo them into logs or artefacts.", "components": ["owasp"], "sources": ["owasp:s26a987a1053b"], "status": "REASONED"},
    "prompt-secrets": {"text": "Keep credentials out of all model prompts and customer data outside unapproved services; system prompts are disclosable and authorization belongs outside the model.", "components": ["owasp"], "sources": ["owasp:s26a987a1053b", "owasp:s4564d1912a87"], "status": "REASONED"},
    "business-rules": {"text": "Keep confidential business logic out of public repositories, browser-shipped code and public LLM prompts; public environment prefixes and source maps can expose it.", "components": ["owasp", "next", "vite-env"], "sources": ["owasp:s26a987a1053b", "owasp:s4564d1912a87", "next:s964651d4eed4", "vite-env:sba07c9b57bd9"], "status": "REASONED"},
    "terraform-state": {"text": "Default local Terraform state is plaintext and may contain sensitive values; ignore *.tfstate and `*.tfstate.*` including backups and workspace copies.", "components": ["terraform"], "sources": ["terraform:s8efa1a4bb953"], "status": "REASONED"},
    "kubeconfig": {"text": "Kubeconfig can embed a base64 client-key-data private key or bearer token; exclude credential-bearing files and copies from version control.", "components": ["kubernetes"], "sources": ["kubernetes:se41a53ea6778"], "status": "REASONED"},
    "docker-store": {"text": "Docker stores logins in its credential store or base64-encoded config.json; encoding is not encryption and scanners can miss encoded or unpatterned secrets.", "components": ["docker", "owasp"], "sources": ["docker:sf8243a183d67", "owasp:s26a987a1053b"], "status": "REASONED"},
    "leak-rotation": {"text": "Revoke and replace a leaked credential before cleanup; deletion cannot undo public repository, chat, log or paste exposure.", "components": ["owasp"], "sources": ["owasp:s26a987a1053b"], "status": "REASONED"},
    "history-cleanup": {"text": "History rewriting with git-filter-repo is hygiene after rotation, not containment or unpublishing.", "components": ["git-filter-repo", "owasp"], "sources": ["git-filter-repo:s95bf8a949d5e", "owasp:s26a987a1053b"], "status": "REASONED"},
    "leak-audit": {"text": "Review provider logs for use of the leaked credential during its exposure window.", "components": ["owasp"], "sources": ["owasp:s26a987a1053b"], "status": "REASONED"},
    "encrypted-git": {"text": "SOPS with age encrypts YAML/JSON/ENV values while preserving structure for secrets that must be versioned; keep decryption keys outside the repository.", "components": ["sops", "age"], "sources": ["sops:s78c5bb528dc4", "age:sca8b0d211739"], "status": "REASONED"},
    "verify-scan": {"text": "With gitleaks 8.19.1 or later, gitleaks must exit 0 with no findings before clean is printed; the v8.30.1 README lists exit 0 for no leaks and 1 for leaks or an error. This rule-based scan is the primary gate.", "components": ["gitleaks"], "sources": ["gitleaks:s4e82b98bf700", "gitleaks:s2a515c553a16", "gitleaks:s8b08240c42e9"], "status": "REASONED", "verify": [1]},
    "verify-patterns": {"text": "Supplementary grep prints filenames only, when null binary data is discovered assumes unprocessed input does not match, skips excluded trees; as this guide's advice, a non-zero exit caused by a read error is a failed check; as this guide's assessment, empty output is not proof of no secret. GNU grep documents -E as extended regular expression syntax.", "components": ["grep", "owasp"], "sources": ["grep:s33689bc366bf", "grep:s2c1251092e66", "grep:sea43e82b0753", "grep:sbd30b628a5b8", "owasp:s26a987a1053b"], "status": "REASONED", "verify": [1]}
  }
}
````
<!-- version-basis:end -->
