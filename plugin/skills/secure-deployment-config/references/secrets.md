---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "9e0117132811e99d3d70689f3d8c1e1350e24bccbabb95094dee0d370346f4f4",
  "components": {
    "owasp": {
      "name": "OWASP secret handling",
      "basis": "unknown",
      "sources": {
        "s26a987a1053b": "https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html",
        "s4564d1912a87": "https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/"
      }
    },
    "gitleaks": {
      "name": "gitleaks command minimum",
      "basis": "8.19+",
      "sources": {
        "s18cdf0069eb9": "https://github.com/gitleaks/gitleaks/blob/v8.19.0/README.md"
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
    }
  },
  "claims": {
    "gitignore": {"text": "Ignore .env, .env.*, *.key and *.pem before committing; allow only a secret-free template. Already tracked files remain tracked.", "components": ["owasp", "next"], "sources": ["owasp:s26a987a1053b", "next:s964651d4eed4"], "status": "REASONED"},
    "runtime-storage": {"text": "Load secrets from environment or a secret manager; keep them out of Dockerfile ENV/ARG, images and build logs.", "components": ["owasp"], "sources": ["owasp:s26a987a1053b"], "status": "REASONED"},
    "random": {"text": "Generate a random secret per service and environment with the shown OpenSSL or Python command; never share staging and production credentials.", "components": ["owasp"], "sources": ["owasp:s26a987a1053b"], "status": "REASONED"},
    "scanners": {"text": "Scan before every push and in CI; gitleaks git/dir require 8.19+, with detect and detect --no-git on older builds; TruffleHog is another scanner.", "components": ["gitleaks", "trufflehog"], "sources": ["gitleaks:s18cdf0069eb9", "trufflehog:s5450689a9bb8"], "status": "REASONED"},
    "argv": {"text": "Arguments expose secrets through procfs, ps and shell history; hidepid or PID namespaces narrow process visibility without covering history.", "components": ["proc", "apache"], "sources": ["proc:s801d5f1ee88d", "apache:scde9004bb967"], "status": "REASONED"},
    "stdin": {"text": "Use htpasswd -i, docker login --password-stdin or gh auth login --with-token to avoid secret arguments.", "components": ["apache", "docker", "gh"], "sources": ["apache:scde9004bb967", "docker:sf8243a183d67", "gh:sf0b01ee9b3e1"], "status": "REASONED"},
    "credential-files": {"text": "Protect plaintext credential files with umask 077 and mode 0600; PostgreSQL ignores group/world-readable .pgpass.", "components": ["postgres", "curl"], "sources": ["postgres:s198d4780d9a4", "curl:s3a0a54039912"], "status": "REASONED"},
    "shell-input": {"text": "Hidden read input avoids history; disable tracing around expansion. The clean-Bash login block clears inherited attributes and allexport and removes TOKEN on exit.", "components": ["docker", "proc"], "sources": ["docker:sf8243a183d67", "proc:s801d5f1ee88d"], "status": "REASONED"},
    "shell-limits": {"text": "The prompted token stays out of argv and environment; same-account/root memory access and earlier exports remain outside this protection.", "components": ["proc", "docker"], "sources": ["proc:s801d5f1ee88d", "docker:sf8243a183d67"], "status": "REASONED"},
    "argv-review": {"text": "A ps/grep snapshot misses unlabelled secrets and short-lived processes; review secret-input paths instead of treating a clean snapshot as proof.", "components": ["proc"], "sources": ["proc:s801d5f1ee88d"], "status": "REASONED"},
    "ci-store": {"text": "Scope CI/CD platform secrets to the jobs needing them; never echo them into logs or artefacts.", "components": ["owasp"], "sources": ["owasp:s26a987a1053b"], "status": "REASONED"},
    "prompt-secrets": {"text": "Keep credentials out of all model prompts and customer data outside unapproved services; system prompts are disclosable and authorization belongs outside the model.", "components": ["owasp"], "sources": ["owasp:s26a987a1053b", "owasp:s4564d1912a87"], "status": "REASONED"},
    "business-rules": {"text": "Keep confidential business logic out of public repositories, browser-shipped code and public LLM prompts; public environment prefixes and source maps can expose it.", "components": ["owasp", "next"], "sources": ["owasp:s26a987a1053b", "owasp:s4564d1912a87", "next:s964651d4eed4"], "status": "REASONED"},
    "terraform-state": {"text": "Default local Terraform state is plaintext and may contain sensitive values; ignore *.tfstate and *.tfstate.* including backups and workspace copies.", "components": ["terraform"], "sources": ["terraform:s8efa1a4bb953"], "status": "REASONED"},
    "kubeconfig": {"text": "Kubeconfig can embed a base64 client-key-data private key or bearer token; exclude credential-bearing files and copies from version control.", "components": ["kubernetes"], "sources": ["kubernetes:se41a53ea6778"], "status": "REASONED"},
    "docker-store": {"text": "Docker stores logins in its credential store or base64-encoded config.json; encoding is not encryption and scanners can miss encoded or unpatterned secrets.", "components": ["docker", "owasp"], "sources": ["docker:sf8243a183d67", "owasp:s26a987a1053b"], "status": "REASONED"},
    "leak-rotation": {"text": "Revoke and replace a leaked credential before cleanup; deletion cannot undo public repository, chat, log or paste exposure.", "components": ["owasp"], "sources": ["owasp:s26a987a1053b"], "status": "REASONED"},
    "history-cleanup": {"text": "History rewriting with git-filter-repo is hygiene after rotation, not containment or unpublishing.", "components": ["git-filter-repo", "owasp"], "sources": ["git-filter-repo:s95bf8a949d5e", "owasp:s26a987a1053b"], "status": "REASONED"},
    "leak-audit": {"text": "Review provider logs for use of the leaked credential during its exposure window.", "components": ["owasp"], "sources": ["owasp:s26a987a1053b"], "status": "REASONED"},
    "encrypted-git": {"text": "SOPS with age encrypts YAML/JSON/ENV values while preserving structure for secrets that must be versioned; keep decryption keys outside the repository.", "components": ["sops", "age"], "sources": ["sops:s78c5bb528dc4", "age:sca8b0d211739"], "status": "REASONED"},
    "verify-scan": {"text": "gitleaks must exit 0 with no findings before clean is printed; this rule-based scan is the primary gate.", "components": ["gitleaks"], "sources": ["gitleaks:s18cdf0069eb9"], "status": "REASONED", "verify": [1]},
    "verify-patterns": {"text": "Supplementary grep prints filenames only, skips binaries/excluded trees and treats read errors as failure; empty output is not proof of no secret. No grep manual is cited.", "components": ["owasp"], "sources": ["owasp:s26a987a1053b"], "status": "REASONED", "verify": [1]}
  }
}
---
# Secrets: keeping keys out of repositories

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| gitignore: Ignore .env, .env.*, *.key and *.pem before committing; allow only a secret-free template. Already tracked files remain tracked. | OWASP secret handling unknown; Next.js unknown | REASONED |
| runtime-storage: Load secrets from environment or a secret manager; keep them out of Dockerfile ENV/ARG, images and build logs. | OWASP secret handling unknown | REASONED |
| random: Generate a random secret per service and environment with the shown OpenSSL or Python command; never share staging and production credentials. | OWASP secret handling unknown | REASONED |
| scanners: Scan before every push and in CI; gitleaks git/dir require 8.19+, with detect and detect --no-git on older builds; TruffleHog is another scanner. | gitleaks command minimum 8.19+; TruffleHog unknown | REASONED |
| argv: Arguments expose secrets through procfs, ps and shell history; hidepid or PID namespaces narrow process visibility without covering history. | Linux procfs unknown; htpasswd unknown | REASONED |
| stdin: Use htpasswd -i, docker login --password-stdin or gh auth login --with-token to avoid secret arguments. | htpasswd unknown; Docker login unknown; GitHub CLI unknown | REASONED |
| credential-files: Protect plaintext credential files with umask 077 and mode 0600; PostgreSQL ignores group/world-readable .pgpass. | PostgreSQL password file unknown; curl netrc unknown | REASONED |
| shell-input: Hidden read input avoids history; disable tracing around expansion. The clean-Bash login block clears inherited attributes and allexport and removes TOKEN on exit. | Docker login unknown; Linux procfs unknown | REASONED |
| shell-limits: The prompted token stays out of argv and environment; same-account/root memory access and earlier exports remain outside this protection. | Linux procfs unknown; Docker login unknown | REASONED |
| argv-review: A ps/grep snapshot misses unlabelled secrets and short-lived processes; review secret-input paths instead of treating a clean snapshot as proof. | Linux procfs unknown | REASONED |
| ci-store: Scope CI/CD platform secrets to the jobs needing them; never echo them into logs or artefacts. | OWASP secret handling unknown | REASONED |
| prompt-secrets: Keep credentials out of all model prompts and customer data outside unapproved services; system prompts are disclosable and authorization belongs outside the model. | OWASP secret handling unknown | REASONED |
| business-rules: Keep confidential business logic out of public repositories, browser-shipped code and public LLM prompts; public environment prefixes and source maps can expose it. | OWASP secret handling unknown; Next.js unknown | REASONED |
| terraform-state: Default local Terraform state is plaintext and may contain sensitive values; ignore *.tfstate and *.tfstate.* including backups and workspace copies. | Terraform unknown | REASONED |
| kubeconfig: Kubeconfig can embed a base64 client-key-data private key or bearer token; exclude credential-bearing files and copies from version control. | Kubernetes kubeconfig unknown | REASONED |
| docker-store: Docker stores logins in its credential store or base64-encoded config.json; encoding is not encryption and scanners can miss encoded or unpatterned secrets. | Docker login unknown; OWASP secret handling unknown | REASONED |
| leak-rotation: Revoke and replace a leaked credential before cleanup; deletion cannot undo public repository, chat, log or paste exposure. | OWASP secret handling unknown | REASONED |
| history-cleanup: History rewriting with git-filter-repo is hygiene after rotation, not containment or unpublishing. | git-filter-repo unknown; OWASP secret handling unknown | REASONED |
| leak-audit: Review provider logs for use of the leaked credential during its exposure window. | OWASP secret handling unknown | REASONED |
| encrypted-git: SOPS with age encrypts YAML/JSON/ENV values while preserving structure for secrets that must be versioned; keep decryption keys outside the repository. | SOPS unknown; age unknown | REASONED |
| verify-scan: gitleaks must exit 0 with no findings before clean is printed; this rule-based scan is the primary gate. | gitleaks command minimum 8.19+ | REASONED |
| verify-patterns: Supplementary grep prints filenames only, skips binaries/excluded trees and treats read errors as failure; empty output is not proof of no secret. No grep manual is cited. | OWASP secret handling unknown | REASONED |
<!-- version-basis:end -->

Leaked API keys and credentials in public repositories are the most common security incident in AI-assisted projects, and scanners harvest fresh commits within minutes. [authentication.md](authentication.md) states the baseline; this guide covers the handling.

## Rules

1. **Secrets never enter version control.** Add `.env`, `.env.*` (frameworks such as Next.js load `.env.local` and `.env.production`, so ignoring `.env` alone leaves those committable), `*.key`, and `*.pem` to `.gitignore` before the first commit, allowlisting only a no-secret template such as `!.env.example`; `.gitignore` does not untrack a file that is already committed. Load secrets from environment variables or a secret manager (AWS Secrets Manager, Google Secret Manager, Azure Key Vault, or your platform's store per [paas.md](paas.md)).
2. **Secrets never enter images or build logs.** `ENV` and `ARG` values in a Dockerfile ship with the image and appear in `docker history`; pass secrets at runtime instead ([docker.md](docker.md)). Do not print secrets in application or CI logs.
3. **Generate secrets randomly** (`openssl rand -base64 32`; `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`), 1 per service and environment, never shared between staging and production.
4. **Scan before every push.** [gitleaks](https://github.com/gitleaks/gitleaks) or [trufflehog](https://github.com/trufflesecurity/trufflehog) as a pre-commit hook and in CI:
   ```bash
   gitleaks git .          # scans the repository history (git/dir need gitleaks 8.19+; older builds use "gitleaks detect" for history and "gitleaks detect --no-git" for the working tree)
   gitleaks dir .          # scans the working tree
   ```
5. **Secrets never enter a command line.** A process's arguments are readable through `/proc/<pid>/cmdline`, which is what `ps` prints; on a default Linux that means every other user on the host, for as long as the process runs, and the command is then written to your shell history. A `hidepid` proc mount or a separate PID namespace narrows who can see it, neither is the default, and neither covers the history. Prefer a flag that reads from stdin (`htpasswd -i`, `docker login --password-stdin`, `gh auth login --with-token`), a file the tool reads itself (`~/.pgpass`, `curl --netrc`; create it with `umask 077` and keep it mode `0600`, since it stores the secret in plaintext and PostgreSQL ignores a `~/.pgpass` that group or others can read), or an environment variable where the tool offers nothing better. Where a value has to be typed, `read -rs` keeps it off the screen, and what `read` consumes is input rather than a command, so no shell records it. One caveat: shell tracing (`set -x`) echoes the expanded command line, so a script that expands a secret into a pipeline (including the `printf`-into-`--password-stdin` pattern below) must turn tracing off around it, because reading from stdin protects the argument list but not the trace.

   This block assumes a clean Bash shell and prompts for the registry token instead of using an ambient `TOKEN`. It clears inherited attributes, turns tracing and allexport off, and unsets the unexported variable on exit. The entered token stays out of history, argv and the environment; process memory is still readable by the same account and root, and this does not erase an earlier export. Docker stores the login in its configured credential store or configuration file, as described in rule 9.

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

## Verify (REASONED: scanner outcomes follow the cited gitleaks documentation and secret-handling guidance; no exposed/fixed scan run is recorded)

```bash
gitleaks git . && echo clean
grep -rlIE "sk-|AKIA|ASIA|ghp_|-----BEGIN" --exclude-dir=node_modules --exclude-dir=.git .   # crude but fast; -l prints only the filename (never the matching secret), -I skips binaries, --exclude-dir skips a whole tree rather than filtering matched lines
```

On every push, gitleaks must exit 0 with no findings (the `&& echo clean` then prints `clean`). The grep is a supplementary pattern search, not proof that no secret is present: treat any filename it prints as a finding to inspect privately, empty output as no match for these patterns only, and a non-zero exit caused by a read error as a failed check. gitleaks, which scans by rule rather than by a few prefixes, is the primary gate.

## Sources (checked September 2026)

- OWASP Secrets Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- gitleaks (git/dir need 8.19+; v8.19.0 README): https://github.com/gitleaks/gitleaks/blob/v8.19.0/README.md
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
