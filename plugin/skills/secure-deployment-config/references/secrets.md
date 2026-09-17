# Secrets: keeping keys out of repositories

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

   ```bash
   printf '%s' "$TOKEN" | docker login ghcr.io -u "$USER" --password-stdin
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

## Verify

```bash
gitleaks git . && echo clean
grep -rlIE "sk-|AKIA|ASIA|ghp_|-----BEGIN" --exclude-dir=node_modules --exclude-dir=.git .   # crude but fast; -l prints only the filename (never the matching secret), -I skips binaries, --exclude-dir skips a whole tree rather than filtering matched lines
```

On every push, gitleaks must exit 0 with no findings (the `&& echo clean` then prints `clean`). The grep is a supplementary pattern search, not proof that no secret is present: treat any filename it prints as a finding to inspect privately, empty output as no match for these patterns only, and a non-zero exit caused by a read error as a failed check. gitleaks, which scans by rule rather than by a few prefixes, is the primary gate.

## Sources (checked September 2026)

- OWASP Secrets Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- gitleaks: https://github.com/gitleaks/gitleaks
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
