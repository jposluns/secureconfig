# GitLab: the fail-safe front door, the plain-HTTP listener, and the CI runner as a code-execution host

GitLab CE is a self-hosted DevOps and Git forge. It serves repositories over HTTP and SSH, runs issue tracking, a container registry, and CI/CD pipelines through operator-registered runners. This guide helps your AI assistant check that a self-hosted deployment is configured securely and can be recovered: rotate the first-run root password, bind privately and enable TLS, close or gate registration, require a second factor, keep visibility private, govern runners and pipelines, lock down the bundled internal services, and back the instance up.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/gitlab.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against GitLab v19.5.3, Omnibus GitLab 19.5.3+ce.0, and Omnibus GitLab EE 19.5.3+ee.0; 1 further source carries no recorded version. Metadata reviewed 2026-11-10; documentation checked November 2026. The guide records 60 claims, all reasoned from cited sources and any earlier-form run, not a live demonstration of the shipped form.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

Unlike a forge whose first run is an open installer or a world-known key, GitLab ships a fail-safe front door: the root admin is seeded with a forced random password, self-service signups are held for admin approval, default project and group visibility is private, and webhook SSRF to the local network is off. So the real exposure is not the login page. It is the plain-HTTP, all-interfaces listener that ships before you set `external_url https`, and the CI/CD runner. A runner executing a pipeline runs the project's `.gitlab-ci.yml` as arbitrary code on the runner host, so a reachable instance becomes remote code execution the moment a runner is attached and a pipeline can be triggered. This guide pins GitLab v19.5.3 and reads every application default from the `v19.5.3-ee` source and every package default from Omnibus `19.5.3+ce.0`. The application config file is `gitlab.yml`; the Omnibus package config is `/etc/gitlab/gitlab.rb`. Runner hardening is [self-hosted-ci-runners.md](self-hosted-ci-runners.md); this guide owns the server-side exposure, its operation, and its recovery.

## 1. Pick an install method and harden that one

The defaults below are read from the Omnibus Linux package, which is the recommended path for a single production server: one host, one `/etc/gitlab/gitlab.rb`, one upgrade surface. The official Docker image runs the same Omnibus build, so the same `gitlab.rb` settings apply, but you must persist `/etc/gitlab`, `/var/opt/gitlab` and `/var/log/gitlab` on volumes and pass configuration through `GITLAB_OMNIBUS_CONFIG` or the mounted file. Helm on Kubernetes is a larger and different configuration surface (separate PostgreSQL, Redis, registry and ingress), so the single-node hardening below maps to it only conceptually. Choose one method and harden it rather than mixing them. [Installation methods](https://docs.gitlab.com/install/), [Docker install](https://docs.gitlab.com/install/docker/installation/).

Edition does not change this guide. GitLab ships Community Edition and Enterprise Edition from the same Omnibus build, and an Enterprise package with no licence runs the GitLab Free tier, which is feature-identical to CE for every control here, so all of this guidance applies to an unlicensed EE install. The Premium and Ultimate features flagged below as not in CE are equally unavailable on unlicensed EE until you add a licence. The `19.5.3+ee.0` and `19.5.3+ce.0` `gitlab.rb.template` files are byte-identical, so every package default cited below holds on either package. [Install without a licence runs only Free features](https://docs.gitlab.com/administration/license/), [Omnibus EE config template](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ee.0/files/gitlab-config-template/gitlab.rb.template).

## 2. Know the first-run root account and rotate it

GitLab's root admin is not an open installer. The production seed `003_admin.rb` skips creation when an admin already exists, builds the account with `admin: true`, and when `GITLAB_ROOT_PASSWORD` is blank it sets `password_automatically_set = true` and `force_random_password = true`, then prints "You'll be prompted to create one on your first visit." A preset password is used verbatim only when `GITLAB_ROOT_PASSWORD` is set, and it is echoed to the console only when `display_initial_root_password` is true. The Omnibus package attributes are `initial_root_password = nil`, `display_initial_root_password = false` and `store_initial_root_password = false`, so the package does not persist the generated password to disk. The automatic write to `/etc/gitlab/initial_root_password`, a root-readable file the documentation says is removed on the first reconfigure or restart after 24 hours, is the Docker image's behaviour and a documented install step, not the package default. Rotate the root password on first sign-in, and where that file exists read then clear it. Read it with `docker exec -it gitlab grep 'Password:' /etc/gitlab/initial_root_password`, or preset it through `gitlab_rails['initial_root_password']` in `gitlab.rb`. [Root seed: random password, admin flag and console output](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/db/fixtures/production/003_admin.rb) (skip-if-admin lines 1-4, `admin: true` line 13, `force_random_password` lines 18-20, preset lines 21-22, display lines 37-42, prompt line 44). [Omnibus initial-password attributes](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-cookbooks/gitlab/attributes/default.rb) (`initial_root_password = nil` line 761, `display_initial_root_password = false` line 764, `store_initial_root_password = false` line 765), [config template](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-config-template/gitlab.rb.template) (preset line 868, display line 878, store toggle and `/etc/gitlab/initial_root_password` path lines 880-881). [Migration recipe passes the preset through](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-cookbooks/gitlab/recipes/database_migrations.rb) (`initial_root_password` read line 22, `GITLAB_ROOT_PASSWORD` set line 31), [Docker install docs: reading and deleting the file](https://docs.gitlab.com/install/docker/installation/).

## 3. Bind privately and set `external_url`

The default application listener is plain HTTP on port 80 with host `localhost`. In source, `host` defaults to `localhost`, `https` defaults to false, and `port` is `https ? 443 : 80`, and the shipped `gitlab.yml.example` carries `host: localhost`, `port: 80` and `https: false`. In Omnibus every public URL, the nginx scheme and the listen ports are derived from a single `external_url` the installer generates; `gitlab_rails['nginx']['listen_port']` and `gitlab_rails['nginx']['listen_https']` default to nil and are taken from the `external_url` scheme, and `redirect_http_to_https` defaults to false. So an `external_url http://...` serves the whole UI, git-over-HTTP and the API in clear text on port 80, on every interface. Set `external_url` to the public origin, and bind the listener to a private address or loopback behind a reverse proxy. These main-application nginx settings moved to the `gitlab_rails['nginx']` namespace in GitLab 19.2, so on an earlier release set the legacy bare `nginx['...']` keys instead, while `nginx['enable']` stays top-level in both. In `/etc/gitlab/gitlab.rb`:

```ruby
external_url 'https://gitlab.example.com'
gitlab_rails['nginx']['listen_addresses'] = ['127.0.0.1']
```

[Application listener defaults](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/initializers/1_settings.rb) (`host` localhost line 197, `https = false` line 200, `port` 443-or-80 line 201), [example config](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/gitlab.yml.example) (`host`, `port`, `https` lines 35-37), [Omnibus external_url and nginx defaults](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-config-template/gitlab.rb.template) (`external_url` line 32, `redirect_http_to_https` false line 2024, `listen_port` nil line 2072, `listen_https` nil line 2076).

## 4. Enable TLS, with bundled nginx or a proxy

TLS is opt-in. An `external_url https://...` makes the bundled nginx terminate TLS, with a Let's Encrypt certificate or an explicit `ssl_certificate` and `ssl_certificate_key`; alternatively terminate TLS at a proxy in front of a loopback-bound instance. Until you do, the web UI, git-over-HTTP and the API cross the wire in clear text, so a non-loopback bind sends session cookies and Basic-auth git credentials to any on-path observer. `letsencrypt['enable']` defaults to nil, so Let's Encrypt is off until you set it; with the bundled nginx, set `letsencrypt['enable'] = true` and a real `letsencrypt['contact_emails']` so expiry warnings reach you, and the certificate auto-renews because `letsencrypt['auto_renew']` defaults true. The bundled renewal runs on a periodic schedule, roughly every 4 days by default (`letsencrypt['auto_renew_day_of_month']` is `*/4`). Otherwise supply explicit `ssl_certificate` and `ssl_certificate_key` files, and either way turn on `redirect_http_to_https`, which defaults false. If you front GitLab with a reverse proxy (see [caddy.md](caddy.md), [nginx.md](nginx.md), [haproxy.md](haproxy.md) and [fronting-auth.md](fronting-auth.md)), either bind the bundled nginx to loopback with `gitlab_rails['nginx']['listen_addresses']` or disable it with `nginx['enable'] = false`, and make the proxy pass the HTTPS scheme through so GitLab builds correct URLs. Treat TLS as mandatory before the port is reachable beyond loopback. In `/etc/gitlab/gitlab.rb`:

```ruby
external_url 'https://gitlab.example.com'
gitlab_rails['nginx']['redirect_http_to_https'] = true
gitlab_rails['nginx']['ssl_certificate']     = '/etc/gitlab/ssl/gitlab.example.com.crt'
gitlab_rails['nginx']['ssl_certificate_key'] = '/etc/gitlab/ssl/gitlab.example.com.key'
```

[TLS, redirect, Let's Encrypt and nginx enable](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-config-template/gitlab.rb.template) (`redirect_http_to_https` false line 2024, `ssl_certificate` and `ssl_certificate_key` lines 2036-2037, `nginx['enable']` true line 2022, Let's Encrypt block lines 3153-3165, `letsencrypt['contact_emails']` line 3154, `letsencrypt['auto_renew']` true line 3162, `letsencrypt['auto_renew_day_of_month']` `*/4` line 3165), [SSL settings](https://docs.gitlab.com/omnibus/settings/ssl/), [nginx settings](https://docs.gitlab.com/omnibus/settings/nginx/).

## 5. Keep internal transport on sockets and loopback

On a single-node Omnibus install the application reaches its data services locally, not over the network: PostgreSQL's `postgresql['listen_address']` defaults to nil (UNIX socket only), Redis is reached over `redis_socket` rather than TCP, Gitaly listens on a UNIX socket path, and Workhorse listens on a socket by default. That is the secure default, so do not expose these services to the network on one host. Internal TLS is a multi-node concern: when you split a service onto its own node, enable transport TLS there (Gitaly `tls_listen_addr` and a `tls` block, `postgresql['ssl']`, which defaults `'on'`, and `redis['tls_port']`, which defaults nil), and keep the plaintext listeners off untrusted networks. [Internal service defaults](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-config-template/gitlab.rb.template) (`postgresql['listen_address']` nil line 1695, `postgresql['ssl']` on line 1764, `redis['tls_port']` nil line 1897, Gitaly socket and `tls_listen_addr` lines 2927-2931), [Redis and Workhorse socket defaults](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-cookbooks/gitlab/attributes/default.rb) (`redis_socket` line 521, workhorse `listen_network` unix line 961), [Gitaly TLS](https://docs.gitlab.com/administration/gitaly/tls_support/).

## 6. Close or gate registration, and require email confirmation

Self-service signup is on by default: `signup_enabled` defaults to true, surfaced as the admin setting of the same name. New signups are safer than an open forge because `require_admin_approval_after_user_signup` defaults to true, so a self-registered account is inactive until an admin approves it. Password sign-in itself is on by default for web and git. One further default is loose: `email_confirmation_setting` defaults to `'off'`, so a new account need not confirm its email, and the domain allowlist and `email_restrictions` ship empty. Do not rely on approval discipline alone for a private instance; clear "Allow new user accounts" under Admin, Settings, General, Sign-up restrictions, which sets `signup_enabled` false, or through `gitlab.rb` `gitlab_rails['gitlab_signup_enabled'] = false`. If you keep signup open, require email confirmation and restrict sign-up to allowed domains. [Signup and sign-in defaults](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/initializers/1_settings.rb) (`signup_enabled` true line 225, `signin_enabled` true line 226), [application setting defaults](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/app/models/application_setting_implementation.rb) (`password_authentication_enabled_for_git`/`_web` lines 176-177, `require_admin_approval_after_user_signup` true line 204, `signup_enabled` surfaced line 219, `email_confirmation_setting` off line 105, `domain_allowlist` line 93, `email_restrictions` lines 106-107), [email confirmation](https://docs.gitlab.com/security/user_email_confirmation/).

## 7. Require a second factor and raise the password policy

There is no instance-wide second-factor requirement by default: `require_two_factor_authentication` defaults to false and `two_factor_grace_period` is 48 hours. Enforcement is available on all tiers from Admin, Settings, General, Sign-in restrictions, and per group, so turn it on, at least for administrators, so local accounts are not password-only; remember that machine credentials still bypass it. The minimum password length default is 8; raise it. Admin mode is off by default (`admin_mode` false), so an administrator's session carries full admin rights throughout; enable it under Admin, Settings, General, Sign-in restrictions so administrators must re-authenticate before administrative actions, which limits a stolen admin session or token. In the admin UI, require two-factor authentication, enable admin mode, and set a longer minimum password length. [Two-factor and password defaults](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/app/models/application_setting_implementation.rb) (`DEFAULT_MINIMUM_PASSWORD_LENGTH = 8` line 37, `admin_mode` false line 43, `minimum_password_length` line 168, `require_two_factor_authentication` false line 205, `two_factor_grace_period` 48 line 287), [enforce 2FA for all users](https://docs.gitlab.com/security/two_factor_authentication/), [admin mode](https://docs.gitlab.com/administration/settings/sign_in_restrictions/).

## 8. Use external authentication and tighten sessions

CE can defer authentication to an external provider: LDAP, instance-wide SAML, and OpenID Connect through OmniAuth are all available in CE. Wiring one is an option, but running local accounts only is also a supportable posture; when you do, the compensating controls carry the whole weight, so keep sign-up closed, require a second factor for every account, enable admin mode, raise the password policy, and shorten sessions. Group-level SAML and SCIM provisioning are Premium and above, not CE, so do not plan around them on a CE instance. Sessions are long by default: `session_expire_delay` is 10080 minutes (7 days) and unauthenticated sessions last 2 hours; `notify_on_unknown_sign_in` defaults true, which is good. The failed-login unlock period and the `unique_ips_limit` controls ship disabled, so enable them to slow credential stuffing and session sharing. [Session and sign-in defaults](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/initializers/1_settings.rb) (`session_expire_delay` 10080 line 234, unauthenticated 2 hours line 236), [lockout and IP controls](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/app/models/application_setting_implementation.rb) (`notify_on_unknown_sign_in` true line 173, `failed_login_attempts_unlock_period_in_minutes` line 111, `unique_ips_limit_enabled` false line 288), [LDAP](https://docs.gitlab.com/administration/auth/ldap/), [OmniAuth providers](https://docs.gitlab.com/integration/omniauth/).

## 9. Scope tokens and SSH keys, and require expiry

GitLab issues many non-interactive credentials: personal, project and group access tokens, deploy tokens, deploy keys, impersonation tokens and the per-job CI token. Each is a machine credential that bypasses 2FA ([machine-auth.md](machine-auth.md)), so scope every one to least privilege, prefer a project or group access token over a personal one, and rotate them. Personal access tokens require an expiry by default: `require_personal_access_token_expiry` defaults to true; keep it. SSH key policy is open by default: the per-type key restrictions (`rsa_key_restriction` and the dsa, ecdsa and ed25519 equivalents) default to 0, which means any size is allowed and no type is forbidden, because `default_min_key_size` returns 0 outside FIPS mode. Set minimum key sizes, forbid weak types, and require key expiry. [PAT expiry and key restrictions](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/app/models/application_setting_implementation.rb) (`require_personal_access_token_expiry` true line 372, `rsa_key_restriction` line 210, dsa/ecdsa/ed25519 lines 94-98, `default_min_key_size` line 425), [token security](https://docs.gitlab.com/security/tokens/), [personal access tokens](https://docs.gitlab.com/user/profile/personal_access_tokens/).

## 10. Keep visibility private and tighten who can create namespaces

Default project, group and snippet visibility is private. All three admin defaults resolve to `default_projects_features['visibility_level']`, which the initializer sets to `Gitlab::VisibilityLevel::PRIVATE`, and the level constants are `PRIVATE = 0`, `INTERNAL = 10`, `PUBLIC = 20`. "Internal" is not private: it means visible to every signed-in non-external user, so on an instance that allows signup, internal content is readable by every approved registrant. Namespace creation is broad by default: `default_project_creation` is Developer-and-above, `can_create_group` defaults true, and `user_default_external` defaults false, so every approved user is a full internal user; `default_branch_protection` defaults to 2 (fully protected). Keep visibility private and restrict who can create groups and projects. [Visibility and creation defaults](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/app/models/application_setting_implementation.rb) (group, project and snippet visibility lines 77, 79, 81, `can_create_group` true line 318, `user_default_external` false line 295), [initializer defaults](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/initializers/1_settings.rb) (`default_projects_features` visibility line 243, `default_project_creation` line 186, `default_branch_protection` 2 line 189), [level constants](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/lib/gitlab/visibility_level.rb) (`PRIVATE`, `INTERNAL`, `PUBLIC` lines 29-31).

## 11. Protect branches in CE, and know what needs a paid tier

In CE, protect your default branch and release tags with protected branches and protected tags: they control who can push and who can merge, which is the CE-available guard against unreviewed changes to code that pipelines will execute. Several controls that readers expect are not in CE: push rules, merge-request approval rules and required approvers, code-owner approval, and protected environments with deployment approvals are Premium and above. Do not design your security model around them on a CE instance; instead use protected branches plus maintainer-only merge and review discipline. Tier labels shift, so re-check the tier badges for your version. [Protected branches](https://docs.gitlab.com/user/project/repository/branches/protected/), [push rules (Premium and above)](https://docs.gitlab.com/user/project/repository/push_rules/), [merge request approvals (Premium and above)](https://docs.gitlab.com/user/project/merge_requests/approvals/), [protected environments (Premium and above)](https://docs.gitlab.com/ci/environments/protected_environments/).

## 12. Govern CI/CD: every registered runner is a code-execution host

This is the sharp exposure. A runner executing a pipeline runs the project's `.gitlab-ci.yml` as arbitrary code on the runner host or container, not on the GitLab host. Runners are operator-registered: none ships or auto-registers, so no pipeline runs until an operator attaches a runner. That makes "exposed equals RCE" conditional on a registered runner plus a trigger path, and a push, a merge request, or a scheduled or triggered pipeline is such a path. Govern the server side: keep instance (shared) runners off untrusted projects and scope each runner to a project or group, and register with the current runner authentication tokens rather than the deprecated registration-token flow. Never put secrets in `.gitlab-ci.yml`; store them as CI/CD variables marked protected (exposed only to protected branches and tags) and masked, or as file variables. Scope the per-job `CI_JOB_TOKEN` with the job-token allowlist so a job reaches only the projects you list. Keep merge-request pipelines from forked, untrusted contributors off any runner that can reach secrets or internal networks. Choose runner executors by risk. Run a default Docker-executor runner for ordinary jobs: in non-privileged mode it isolates each job in its own container, so run jobs as a non-root user, drop SETUID and SETGID, and never pass `--privileged`, which would hand a job the host's root capabilities. Attach a second runner only for jobs that must use host kernel features such as Landlock or cgroups, and make it a shell executor. The shell executor runs job scripts directly on the host as the GitLab Runner user and can read other projects built on that host, so it is the highest-risk executor and is in maintenance mode. Harden it: give it a dedicated unprivileged service user with `--user` rather than root or a sudo-capable account, confine the service with systemd cgroup and resource limits and a Landlock policy, tag it and clear its Run-untagged-jobs setting so only tagged, trusted jobs reach it, and never attach it to shared or public projects. Runner configuration and isolation are [self-hosted-ci-runners.md](self-hosted-ci-runners.md). [GitLab runners](https://docs.gitlab.com/ci/runners/), [runner scope](https://docs.gitlab.com/ci/runners/runners_scope/), [new runner creation workflow](https://docs.gitlab.com/ci/runners/new_creation_workflow/), [runner executors](https://docs.gitlab.com/runner/executors/), [shell executor security](https://docs.gitlab.com/runner/executors/shell/), [runner security](https://docs.gitlab.com/runner/security/), [configure runners and tags](https://docs.gitlab.com/ci/runners/configure_runners/), [CI/CD variables](https://docs.gitlab.com/ci/variables/), [CI job token scoping](https://docs.gitlab.com/ci/jobs/ci_job_token/), [pipeline security](https://docs.gitlab.com/ci/pipeline_security/).

## 13. Know the registry, package and dependency-proxy surfaces

The bundled container registry is not enabled by default in Omnibus: `registry_enabled` defaults to false. It is turned on by configuring `registry_external_url`, and when on, its nginx vhost listens on port 5050 while the registry process itself listens on loopback `127.0.0.1:5000`. The project feature `container_registry` is true in the example config, but that gates the UI feature, not the service. The package registry and the dependency proxy are likewise off by default: `packages_enabled` and `dependency_proxy_enabled` default to nil (unset). If you enable any of these, publish 5050 deliberately, front it with the same TLS and authentication as the rest of the instance, note that they authenticate with the instance's own tokens, and set cleanup or expiration policies so storage and exposure do not grow unbounded. [Registry disabled by default](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-cookbooks/gitlab/attributes/default.rb) (`registry_enabled = false` line 298, `packages_enabled` nil line 251, `dependency_proxy_enabled` nil line 258), [registry URL, loopback process and 5050 vhost](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-config-template/gitlab.rb.template) (`registry_external_url` line 1192, `registry_http_addr` 127.0.0.1:5000 line 1219, nginx `listen_port` 5050 line 2635), [project feature flag](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/gitlab.yml.example) (`container_registry: true` line 175), [package administration](https://docs.gitlab.com/administration/packages/), [dependency proxy](https://docs.gitlab.com/user/packages/dependency_proxy/).

## 14. Protect the secrets at rest and plan for key loss

The instance's encryption secrets live in `/etc/gitlab/gitlab-secrets.json` in Omnibus; the template documents that this file is generated, can be synced between nodes, and can be prevented from regenerating. Its only protection at rest is filesystem permissions. That file keys the database-encrypted columns, so it holds the ability to read stored two-factor secrets, CI/CD variables and integration tokens. The consequences are two-sided: leak it and those secrets are exposed; lose it and the encrypted columns become unrecoverable even though the database restores. Protect the file and any backups the same way you protect the database, keep it out of the data backup (see the backup section), and treat key rotation as a deliberate operator procedure, not an automatic one. [Secrets file in the Omnibus template](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-config-template/gitlab.rb.template) (`gitlab-secrets.json` sync note line 2596, generation toggles lines 3189 and 3191), [the backup task and the secrets file](https://docs.gitlab.com/administration/backup_restore/backup_gitlab/).

## 15. Keep the bundled internal listeners and the SSH surface in check

Several services ship bundled and must stay local on a single node. Puma binds `127.0.0.1:8080`, Workhorse and the registry process bind loopback, and Gitaly, PostgreSQL and Redis are reached over UNIX sockets, so none of these should answer on a public interface. Git-over-SSH uses the host's own `sshd` on port 22 by default through gitlab-shell: `ssh_port` defaults to 22, and the Omnibus template documents the same `gitlab_shell_ssh_port = 22`. The optional bundled `gitlab-sshd` is off by default (`gitlab_sshd['enable']` false) and, when enabled, listens on `localhost:2222`. Publish and firewall port 22, and any 2222, deliberately rather than by default, and keep the internal listeners off the network. [Internal binds](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-config-template/gitlab.rb.template) (`puma['listen']` 127.0.0.1 line 1534, `puma['port']` 8080 line 1535, workhorse socket lines 1386-1388, `gitlab_shell_ssh_port = 22` line 833, `gitlab_sshd['enable']` false line 1654, `gitlab_sshd` listen `localhost:2222` line 1663), [gitlab-shell SSH port](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/initializers/1_settings.rb) (`ssh_port` 22 line 557).

## 16. Turn on rate limiting and make the client IP visible

Most request rate limits ship disabled: the `throttle_*` toggles for protected paths, authenticated and unauthenticated API, web and Git all default false. A couple are on: the raw-blob request limit is 300 per minute and the users-by-id limit is 300. For an internet-facing instance, enable the protected-paths throttle (to slow sign-in and password brute force) and the API and web throttles. The monitoring and metrics endpoints are gated to loopback by default: `gitlab_rails['monitoring_whitelist']` defaults to 127.0.0.0/8 and ::1/128, and the monitoring `ip_whitelist` to 127.0.0.1/8; keep that allowlist tight. If GitLab sits behind a proxy or CDN, set `gitlab_rails['trusted_proxies']` and `gitlab_rails['nginx']['real_ip_trusted_addresses']` (both default empty) so logs, rate limits and abuse controls see the real client IP and not the proxy ([cloudflare.md](cloudflare.md)). [Throttle and request-limit defaults](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/app/models/application_setting_implementation.rb) (`throttle_protected_paths_enabled` false line 268, `throttle_authenticated_api_enabled` false line 234, `throttle_unauthenticated_enabled` false line 274, `raw_blob_request_limit` 300 line 197, `users_get_by_id_limit` 300 line 316). The allowlist and proxy defaults are in [the Omnibus template](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-config-template/gitlab.rb.template) (`monitoring_whitelist` line 287, `trusted_proxies` line 248, `real_ip_trusted_addresses` line 2101) and the [monitoring ip_whitelist](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/initializers/1_settings.rb) (`monitoring['ip_whitelist']` 127.0.0.1/8 line 903). See also [rate limits](https://docs.gitlab.com/rate_limits/).

## 17. Keep bundled monitoring on loopback

GitLab bundles Prometheus and a set of exporters, enabled by default through `prometheus_monitoring`, and they bind loopback: Prometheus on `localhost:9090`, node_exporter on `localhost:9100`, gitlab_exporter on `localhost:9168`, and the Redis, PostgreSQL and Alertmanager exporters likewise on localhost. Keep every one of them off the public interface; they expose instance internals with no authentication of their own. GitLab also serves health endpoints: `/-/health`, `/-/readiness` and `/-/liveness`, plus a Prometheus `/-/metrics`. The detailed readiness and liveness output and the metrics endpoint are restricted to the monitoring allowlist from the previous section or a token, so do not open them to the internet. [Prometheus and exporter listen addresses](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-cookbooks/monitoring/attributes/default.rb) (`prometheus['listen_address']` localhost:9090 line 26, node_exporter localhost:9100 line 62, gitlab_exporter localhost line 120 and 9168 line 121, `prometheus_monitoring['enable']` true line 146), [Prometheus monitoring](https://docs.gitlab.com/administration/monitoring/prometheus/), [health check endpoints](https://docs.gitlab.com/administration/monitoring/health_check/).

## 18. Know what CE audits, and where the logs are

CE records a limited set of audit events and writes operational logs under `/var/log/gitlab`, including `gitlab-rails/production.log`, `gitlab-rails/audit_json.log` and `gitlab-rails/api_json.log`. The richer compliance tooling is not in CE: comprehensive audit events, audit-event streaming, the credentials inventory and the compliance center are Premium and above. So do not assume CE gives you a full audit trail; ship the logs off-host to your own log store and alerting, and treat that as the audit path. [Audit event reports (tiered)](https://docs.gitlab.com/administration/compliance/audit_event_reports/), [log locations and formats](https://docs.gitlab.com/administration/logs/).

## 19. Back up the data and the secrets, and drill a restore

`gitlab-backup create` writes one tar of application data: the database, repositories, LFS, uploads, CI artifacts, packages, the registry and more. It does not include the `/etc/gitlab` configuration, `gitlab-secrets.json`, object-storage contents, or the TLS and SSH host keys, so the tar alone cannot rebuild a working instance. Back up `/etc/gitlab/gitlab-secrets.json` and `/etc/gitlab/gitlab.rb` separately and store them apart from the data tar: the secrets file holds the database encryption key, and without it the restored 2FA secrets, CI/CD variables and tokens are unrecoverable. Send backups offsite and encrypt them (the task can upload to S3, GCS or Azure and encrypt at rest), keep local archives mode 0600 owned by the `git` user, and remember `backup_keep_time` prunes only local copies. A restore needs a GitLab version matching the backup: restore the secrets and config first, then the tar. A backup you have never restored is unproven, so run a periodic test-restore onto a scratch host as the only real evidence it works. [Backup scope, exclusions and encryption](https://docs.gitlab.com/administration/backup_restore/backup_gitlab/), [restore and version matching](https://docs.gitlab.com/administration/backup_restore/restore_gitlab/).

## 20. Stay patched: cadence and required upgrade stops

An exposed, unpatched forge is the real risk, so track releases and upgrade promptly. GitLab ships a minor release monthly and patch releases roughly twice a month; security fixes are backported to the current and previous two monthly releases, and high or critical issues get a dedicated patch. You cannot jump arbitrary versions: GitLab defines required upgrade stops you must pass through, and for the 19.x series they are 19.2, 19.5, 19.8 and 19.11, taking the latest patch of each stop. Let background migrations finish between steps, and use the official Upgrade Path tool to plan the exact route for your starting version. [Maintenance and release cadence](https://docs.gitlab.com/policy/maintenance/), [required upgrade stops and the upgrade path tool](https://docs.gitlab.com/update/upgrade_paths/), [upgrading GitLab](https://docs.gitlab.com/update/).

## 21. Secure outgoing and incoming email

If the instance sends mail, require SMTP TLS: `smtp_enable_starttls_auto` defaults true, so keep it on and verify the mail server's certificate. If you enable incoming email (Reply-by-email), you add a mailbox credential that must be protected like any other secret. Remember that notification emails can carry private issue, merge-request and code content, so scope who receives them and avoid sending instance mail through an untrusted relay. [SMTP and email defaults](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-config-template/gitlab.rb.template) (`smtp_enable_starttls_auto` true line 106, `incoming_email_enabled` line 340), [SMTP settings](https://docs.gitlab.com/omnibus/settings/smtp/), [incoming email](https://docs.gitlab.com/administration/incoming_email/).

## 22. Keep the webhook SSRF guard, and know the system-hook exception

Webhook and integration SSRF to the local network is fail-closed by default: `allow_local_requests_from_web_hooks_and_services` defaults to false, so a project webhook cannot reach loopback or internal IPs unless an admin widens it. Keep it off. One default is the opposite: admin system hooks may reach the local network, because `allow_local_requests_from_system_hooks` defaults to true. That is an admin-only surface, but note it is the reverse of the web-hook default, so treat system-hook targets with the same care. [Local-request SSRF defaults](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/app/models/application_setting_implementation.rb) (`allow_local_requests_from_system_hooks` true line 47, `allow_local_requests_from_web_hooks_and_services` false line 48).

## Exposure rules

Before GitLab is reachable beyond loopback, every one of these must hold:

- One install method is chosen and hardened, and its config and data paths are persisted.
- The root password is rotated from the generated value, and where `/etc/gitlab/initial_root_password` exists it is read and removed.
- `external_url` is the public origin, and the listener is on loopback or a private address behind a proxy; no plain HTTP is reachable from the network.
- TLS is on, through `external_url https://...` or a TLS-terminating proxy, and HTTP redirects to HTTPS.
- Internal services (Gitaly, PostgreSQL, Redis, Workhorse) stay on sockets or loopback, and internal TLS is used where a service is split onto its own node.
- Registration is closed (`signup_enabled` false) unless a public, self-service forge is intended; approval discipline is not relied on alone, and email confirmation and domain limits are on if signup is open.
- A second factor is required for every user, or at least for administrators, and the minimum password length is raised above 8.
- External authentication is wired where used, sessions are shortened from the 7-day default, and failed-login and IP limits are enabled.
- Tokens and SSH keys are scoped to least privilege with expiry required, and minimum SSH key sizes are set.
- Project, group and snippet visibility stay private, namespace creation is restricted, and the "internal" level is understood as visible to every signed-in non-external user.
- The default branch is protected; no Premium-only control (push rules, approval rules, protected environments) is assumed on a CE instance.
- Every registered runner is scoped and unprivileged, secrets live in protected and masked CI/CD variables not in `.gitlab-ci.yml`, the job-token allowlist is set, and no runner that can reach secrets serves untrusted fork pipelines.
- Ordinary jobs run on a non-privileged Docker-executor runner; any shell-executor runner is tag-gated to trusted jobs only, runs under a dedicated unprivileged user, and is never attached to shared or public projects.
- The container registry, package registry and dependency proxy, if enabled, publish deliberately behind the instance's TLS and authentication.
- `/etc/gitlab/gitlab-secrets.json` is protected like the database and excluded from the data backup, and key-loss impact is understood.
- The bundled internal listeners and the bundled monitoring stack stay on loopback, the monitoring allowlist is tight, and trusted proxies are set so the client IP is visible.
- Rate limiting is enabled for an internet-facing instance, and log shipping covers what CE does not audit.
- A data backup and a separate secrets and config backup run, are offsite and encrypted, and a restore has actually been drilled.
- The instance is on a current, patched release, upgraded through the required stops.
- Git-over-SSH on 22, and any bundled `gitlab-sshd` on 2222, are published and firewalled deliberately.
- The web-hook local-request guard keeps its fail-closed default, and system-hook targets are treated with the same care.

## Verify

REASONED: Verification preparation. A live GitLab stand-up opens listeners on 80, 443, 22 and, with the registry on, 5050; the authoring host forbids opening listeners without an isolated network namespace, and none was available. No GitLab instance, container runtime or test deployment was exercised here, so every outcome below is REASONED from the cited source and documentation, not demonstrated. The guarded Bash blocks were written to pass `bash -n` and ShellCheck cleanly and to refuse on unsubstituted placeholders before they reach `curl`; the repository gate suite's `bash -n` and ShellCheck passes cover them. Service behaviour is REASONED, not demonstrated. Run each exposed-versus-fixed comparison only against an isolated test deployment you control, never by weakening production, and keep versions, paths and credentials constant while changing the control under test. A rejection counts only when the positive control succeeds.

### Inventory the listeners and confirm the binds

REASONED: No GitLab instance runs here. `ss` inventories local binds in this namespace only, not firewall or NAT, and a failed netlink inventory proves no absence. Expect GitLab's nginx on 80 or 443, git-over-SSH on 22, and, only when the registry is configured, nginx on 5050. Treat a `0.0.0.0` or wildcard bind on any of those as exposed to every interface, which is the shipped default for the web listener. Confirm the actual external entry point separately.

```bash
# REASONED: no GitLab instance runs in the authoring environment; local listener inventory only.
(
  set +e
  if ! command -v ss > /dev/null 2>&1; then
    echo "ss is not installed; install iproute2 (or use lsof -iTCP -sTCP:LISTEN); not probing"
    exit 2
  fi
  listeners=$(ss -H -tlnp 2>/dev/null)
  rc=$?
  if [ "$rc" -ne 0 ]; then
    echo "ss exited $rc; the listener inventory is inconclusive"
    exit 3
  fi
  match=$(printf '%s\n' "$listeners" | awk '$4 ~ /:(80|443|22|5050)$/')
  if [ -z "$match" ]; then
    echo "no listener on 80, 443, 22 or 5050 in this namespace; GitLab may be elsewhere, not running, or on other ports"
    exit 0
  fi
  printf '%s\n' "$match"
  if printf '%s\n' "$match" | awk '$4 ~ /:(80|443|22|5050)$/ && (index($4, "0.0.0.0:") == 1 || index($4, "*:") == 1 || index($4, "[::]:") == 1) { found = 1 } END { exit !found }'; then
    echo "FINDING (REASONED): a GitLab port is bound to all interfaces; bind nginx privately or front it with a proxy, and firewall 22 and 5050 unless this exposure is intended"
  else
    echo "a non-wildcard host is bound; judge whether that interface is intended"
  fi
)
```

### Confirm TLS is on and the application, not an error, is served

REASONED: No GitLab instance runs here. A configured GitLab serves the sign-in page at `/users/sign_in`, whose markup carries the `new_user` sign-in form; an un-configured or broken instance returns an error page instead. The probe fetches `/users/sign_in` over HTTPS with certificate validation on, which also confirms TLS, and refuses placeholders before it calls `curl`; it sends no credential. Paste the whole block and substitute the two values inside the single quotes.

```bash
# REASONED: no GitLab instance runs in the authoring environment; unauthenticated GET only.
(
  set +x
  set +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_GITLAB_BASE_URL' 'REPLACE_WITH_CA_BUNDLE'
  if [ "${1-}" != PASTE_WHOLE_BLOCK ]; then
    echo "paste the whole block, including its set -- line; not probing"; exit 2
  fi
  shift
  if [ "$#" -ne 2 ]; then
    echo "the set -- line needs exactly 2 values; not probing"; exit 2
  fi
  for arg in "$@"; do
    case "$arg" in
      *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
        echo "substitute every placeholder inside the quotes; not probing"; exit 2 ;;
      *[[:cntrl:]]*)
        echo "control character in input; not probing"; exit 2 ;;
    esac
  done
  base=$1
  ca=$2
  case "$base" in
    https://*) ;;
    *) echo "an https:// base URL is required so no credential is sent in plaintext; not probing"; exit 2 ;;
  esac
  case "$base" in
    *'@'*|*'?'*|*'#'*|*' '*)
      echo "use a base URL without credentials, query, fragment or spaces; not probing"; exit 2 ;;
  esac
  case "$ca" in
    /*) ;;
    *) echo "an absolute CA bundle path is required; not probing"; exit 2 ;;
  esac
  if [ ! -f "$ca" ] || [ ! -r "$ca" ]; then
    echo "the CA bundle is not a readable file; not probing"; exit 2
  fi
  base=${base%/}
  case "$base" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute every placeholder inside the quotes; not probing"; exit 2 ;;
    *)
      body=$(curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert "$ca" \
        -w '\nHTTPSTATUS:%{http_code} exit=%{exitcode} err=%{errormsg}' \
        "$base/users/sign_in") ;;
  esac
  printf '%s\n' "$body" | tail -n 1
  if printf '%s\n' "$body" | grep -q 'name="new_user"'; then
    echo "expected fixed result: the sign-in page is served over TLS; the HTTPS fetch returned the status above, so TLS succeeded"
  else
    echo "the sign-in form was not found; judge the status line and body, since an error page or a redirect is not the configured application"
  fi
  echo "REASONED expectation: fixed serves the sign-in form over TLS; exit!=0 in the status line means TLS or the connection failed (inconclusive)."
)
```

### Confirm anonymous browsing matches your intent

REASONED: No GitLab instance runs here. By default GitLab lets anonymous callers reach the explore area, which lists only public projects; with default-private visibility that list is empty, so any project shown there is public and readable without a login. The probe fetches `/explore/projects` over HTTPS and reports the status; it does not follow redirects. Paste the whole block and substitute the two values inside the single quotes.

```bash
# REASONED: no GitLab instance runs in the authoring environment; unauthenticated GET only.
(
  set +x
  set +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_GITLAB_BASE_URL' 'REPLACE_WITH_CA_BUNDLE'
  if [ "${1-}" != PASTE_WHOLE_BLOCK ]; then
    echo "paste the whole block, including its set -- line; not probing"; exit 2
  fi
  shift
  if [ "$#" -ne 2 ]; then
    echo "the set -- line needs exactly 2 values; not probing"; exit 2
  fi
  for arg in "$@"; do
    case "$arg" in
      *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
        echo "substitute every placeholder inside the quotes; not probing"; exit 2 ;;
      *[[:cntrl:]]*)
        echo "control character in input; not probing"; exit 2 ;;
    esac
  done
  base=$1
  ca=$2
  case "$base" in
    https://*) ;;
    *) echo "an https:// base URL is required; not probing"; exit 2 ;;
  esac
  case "$ca" in
    /*) ;;
    *) echo "an absolute CA bundle path is required; not probing"; exit 2 ;;
  esac
  if [ ! -f "$ca" ] || [ ! -r "$ca" ]; then
    echo "the CA bundle is not a readable file; not probing"; exit 2
  fi
  base=${base%/}
  case "$base" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute every placeholder inside the quotes; not probing"; exit 2 ;;
    *)
      curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert "$ca" \
        -w 'anonymous /explore/projects -> http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "$base/explore/projects" ;;
  esac
  echo "REASONED expectation: a 200 means anonymous discovery is open (the default), and any project listed is public; a redirect to /users/sign_in means anonymous browsing is restricted; exit!=0 means TLS or the connection failed (inconclusive). Judge the listed projects against your intent."
)
```

### Check the Omnibus initial root password file

REASONED: No GitLab instance runs here. On Omnibus and the Docker image the generated root password is written to `/etc/gitlab/initial_root_password` and the documentation says it is deleted on the first reconfigure or restart after 24 hours, so a present file means the generated password has probably not been rotated. The check needs Docker access and reads the file's presence only; absence does not prove the password was rotated, and a present file means rotate root now. The container is named `gitlab`.

```bash
# REASONED: no GitLab instance runs in the authoring environment; file-presence check only.
# status: 1 when the file is present, 3 when the check did not run, 0 when the file is absent
(
  set -- "$(if docker exec gitlab sh -c 'test -f /etc/gitlab/initial_root_password && echo PRESENT || echo ABSENT' 2>/dev/null; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "${1%%$'\n'*}" "${1##*$'\n'}"              # the container's reply, then docker exec's exit status
  if [ "$2" = 0 ]; then
    case "$1" in
      PRESENT) echo 'initial_root_password present: rotate root and remove it'; exit 1 ;;
      ABSENT)  echo 'initial_root_password absent' ;;
      *)       echo 'the check did not run (unexpected reply from the gitlab container): not a result'; exit 3 ;;
    esac
  else
    echo 'the check did not run (docker exec failed for the gitlab container): fix the container, this is not a result'
    exit 3
  fi
)
```

### Inventory the bundled internal listeners

REASONED: No GitLab instance runs here. `ss` inventories local binds in this namespace only, not firewall or NAT, and a failed inventory proves no absence. GitLab's bundled Puma (8080), Prometheus (9090), node_exporter (9100) and gitlab_exporter (9168) should answer only on loopback, so a `0.0.0.0` or wildcard bind on any of them is internal exposure; bind them to loopback and keep them off the public network.

```bash
# REASONED: no GitLab instance runs in the authoring environment; local internal-listener inventory only.
(
  set +e
  if ! command -v ss > /dev/null 2>&1; then
    echo "ss is not installed; install iproute2 (or use lsof -iTCP -sTCP:LISTEN); not probing"
    exit 2
  fi
  listeners=$(ss -H -tlnp 2>/dev/null)
  rc=$?
  if [ "$rc" -ne 0 ]; then
    echo "ss exited $rc; the internal listener inventory is inconclusive"
    exit 3
  fi
  match=$(printf '%s\n' "$listeners" | awk '$4 ~ /:(8080|9090|9100|9168)$/')
  if [ -z "$match" ]; then
    echo "no bundled internal port (8080, 9090, 9100, 9168) is listening here; the services may be elsewhere, off, or on other ports"
    exit 0
  fi
  printf '%s\n' "$match"
  if printf '%s\n' "$match" | awk '$4 ~ /:(8080|9090|9100|9168)$/ && (index($4, "0.0.0.0:") == 1 || index($4, "*:") == 1 || index($4, "[::]:") == 1) { found = 1 } END { exit !found }'; then
    echo "FINDING (REASONED): a bundled internal service is bound to all interfaces; bind Puma, Prometheus and the exporters to loopback and keep them off the public network"
  else
    echo "the bundled internal services are on loopback or a non-wildcard host; confirm that host is not publicly reachable"
  fi
)
```

### Confirm a data backup and a separate secrets backup exist

REASONED: No GitLab instance runs here. A data backup under `gitlab-backup create` excludes `/etc/gitlab/gitlab-secrets.json`, so a working recovery needs both a recent data tar and a separate secrets backup; this check reads local file presence and age only. A missing or stale data tar, or a missing secrets file, means the instance is not recoverable, and absence of the directory is not proof a backup ran elsewhere. Point the paths at your own `backup_path` if you changed it.

```bash
# REASONED: no GitLab instance runs in the authoring environment; local backup-presence check only.
# status: 0 when a recent data tar and a secrets file are both present, 1 when either is missing or stale, 3 when the check did not run
(
  set +e
  dir=/var/opt/gitlab/backups
  if [ ! -d "$dir" ]; then
    echo "no backup directory at $dir; point this check at your backup_path; not a result"
    exit 3
  fi
  if find "$dir" -maxdepth 1 -type f -name '*_gitlab_backup.tar' -mtime -7 2>/dev/null | grep -q .; then
    echo "a data backup under 7 days old is present in $dir"
  else
    echo "FINDING (REASONED): no *_gitlab_backup.tar under 7 days old in $dir; the data backup may be missing or stale"
    exit 1
  fi
  if [ -f /etc/gitlab/gitlab-secrets.json ]; then
    echo "gitlab-secrets.json exists; confirm it is backed up SEPARATELY and off-host, since the data tar excludes it"
  else
    echo "FINDING (REASONED): /etc/gitlab/gitlab-secrets.json not found here; without the secrets file an encrypted-data restore is unusable"
    exit 1
  fi
)
```

## Sources (checked November 2026)

Repository sources are the GitLab monorepo at tag `v19.5.3-ee` (commit `b9b17a44ffb72a85fca47c5416a40a643c42996f`) and omnibus-gitlab at tag `19.5.3+ce.0` (commit `dbd814101106e4b386c68ca0761603e4ad693a11`); line numbers in the prose above are at those tags. GitLab CE is the FOSS-licensed subset of the `gitlab-org/gitlab` monorepo, and every file cited here is in that core subset, not the `ee/` tree; the clean FOSS mirror `gitlabhq/gitlabhq` lags the `-ee` tag, so the citations use `gitlab-org/gitlab` at `v19.5.3-ee`. Documentation pages under `https://docs.gitlab.com/` are the rolling, reader-facing administrator docs for the same product.

- GitLab root-account production seed, forced random password and console output (v19.5.3-ee): https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/db/fixtures/production/003_admin.rb
- GitLab application settings initializer: host, port, https, signup, signin, SSH port, visibility, sessions, monitoring allowlist and creation defaults (v19.5.3-ee): https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/initializers/1_settings.rb
- GitLab application setting defaults: approval, email confirmation, password policy, two-factor, visibility, key restrictions, throttles, SSRF guards and token expiry (v19.5.3-ee): https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/app/models/application_setting_implementation.rb
- GitLab visibility-level constants (v19.5.3-ee): https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/lib/gitlab/visibility_level.rb
- GitLab example application config: host, port, https and the container-registry feature (v19.5.3-ee): https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/gitlab.yml.example
- Omnibus GitLab config template: external_url, nginx, TLS, internal binds, registry, SSH, proxies and secrets file (19.5.3+ce.0): https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-config-template/gitlab.rb.template
- Omnibus GitLab attribute defaults: initial root password, registry, packages, Redis and Workhorse sockets (19.5.3+ce.0): https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-cookbooks/gitlab/attributes/default.rb
- Omnibus GitLab migration recipe: passing the preset root password through (19.5.3+ce.0): https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-cookbooks/gitlab/recipes/database_migrations.rb
- Omnibus GitLab monitoring attribute defaults: Prometheus and exporter listen addresses (19.5.3+ce.0): https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-cookbooks/monitoring/attributes/default.rb
- Omnibus GitLab EE config template, byte-identical to the CE template, recording the unlicensed-EE basis (19.5.3+ee.0): https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ee.0/files/gitlab-config-template/gitlab.rb.template
- GitLab installation methods (rolling documentation, checked November 2026): https://docs.gitlab.com/install/
- GitLab Docker install: initial root password file and its deletion (rolling documentation, checked November 2026): https://docs.gitlab.com/install/docker/installation/
- GitLab activate and license: installing without a licence enables only Free features (rolling documentation, checked November 2026): https://docs.gitlab.com/administration/license/
- GitLab Omnibus SSL settings (rolling documentation, checked November 2026): https://docs.gitlab.com/omnibus/settings/ssl/
- GitLab Omnibus nginx settings (rolling documentation, checked November 2026): https://docs.gitlab.com/omnibus/settings/nginx/
- GitLab Gitaly TLS support (rolling documentation, checked November 2026): https://docs.gitlab.com/administration/gitaly/tls_support/
- GitLab user email confirmation (rolling documentation, checked November 2026): https://docs.gitlab.com/security/user_email_confirmation/
- GitLab enforce two-factor authentication for all users (rolling documentation, checked November 2026): https://docs.gitlab.com/security/two_factor_authentication/
- GitLab sign-in restrictions and admin mode (rolling documentation, checked November 2026): https://docs.gitlab.com/administration/settings/sign_in_restrictions/
- GitLab LDAP administration (rolling documentation, checked November 2026): https://docs.gitlab.com/administration/auth/ldap/
- GitLab OmniAuth providers (rolling documentation, checked November 2026): https://docs.gitlab.com/integration/omniauth/
- GitLab token security (rolling documentation, checked November 2026): https://docs.gitlab.com/security/tokens/
- GitLab personal access tokens (rolling documentation, checked November 2026): https://docs.gitlab.com/user/profile/personal_access_tokens/
- GitLab protected branches (rolling documentation, checked November 2026): https://docs.gitlab.com/user/project/repository/branches/protected/
- GitLab push rules (rolling documentation, checked November 2026): https://docs.gitlab.com/user/project/repository/push_rules/
- GitLab merge request approvals (rolling documentation, checked November 2026): https://docs.gitlab.com/user/project/merge_requests/approvals/
- GitLab protected environments (rolling documentation, checked November 2026): https://docs.gitlab.com/ci/environments/protected_environments/
- GitLab runners (rolling documentation, checked November 2026): https://docs.gitlab.com/ci/runners/
- GitLab runner scope (rolling documentation, checked November 2026): https://docs.gitlab.com/ci/runners/runners_scope/
- GitLab new runner creation workflow (rolling documentation, checked November 2026): https://docs.gitlab.com/ci/runners/new_creation_workflow/
- GitLab Runner executors (rolling documentation, checked November 2026): https://docs.gitlab.com/runner/executors/
- GitLab Runner shell executor and its security (rolling documentation, checked November 2026): https://docs.gitlab.com/runner/executors/shell/
- GitLab Runner security for the shell and Docker executors (rolling documentation, checked November 2026): https://docs.gitlab.com/runner/security/
- GitLab configure runners, tags and run-untagged jobs (rolling documentation, checked November 2026): https://docs.gitlab.com/ci/runners/configure_runners/
- GitLab CI/CD variables (rolling documentation, checked November 2026): https://docs.gitlab.com/ci/variables/
- GitLab CI job token scoping (rolling documentation, checked November 2026): https://docs.gitlab.com/ci/jobs/ci_job_token/
- GitLab pipeline security (rolling documentation, checked November 2026): https://docs.gitlab.com/ci/pipeline_security/
- GitLab package administration (rolling documentation, checked November 2026): https://docs.gitlab.com/administration/packages/
- GitLab dependency proxy (rolling documentation, checked November 2026): https://docs.gitlab.com/user/packages/dependency_proxy/
- GitLab rate limits (rolling documentation, checked November 2026): https://docs.gitlab.com/rate_limits/
- GitLab Prometheus monitoring (rolling documentation, checked November 2026): https://docs.gitlab.com/administration/monitoring/prometheus/
- GitLab health check endpoints (rolling documentation, checked November 2026): https://docs.gitlab.com/administration/monitoring/health_check/
- GitLab audit event reports and tiers (rolling documentation, checked November 2026): https://docs.gitlab.com/administration/compliance/audit_event_reports/
- GitLab log locations and formats (rolling documentation, checked November 2026): https://docs.gitlab.com/administration/logs/
- GitLab back up your instance (rolling documentation, checked November 2026): https://docs.gitlab.com/administration/backup_restore/backup_gitlab/
- GitLab restore your instance (rolling documentation, checked November 2026): https://docs.gitlab.com/administration/backup_restore/restore_gitlab/
- GitLab maintenance and release cadence (rolling documentation, checked November 2026): https://docs.gitlab.com/policy/maintenance/
- GitLab required upgrade stops and upgrade path (rolling documentation, checked November 2026): https://docs.gitlab.com/update/upgrade_paths/
- GitLab upgrading (rolling documentation, checked November 2026): https://docs.gitlab.com/update/
- GitLab Omnibus SMTP settings (rolling documentation, checked November 2026): https://docs.gitlab.com/omnibus/settings/smtp/
- GitLab incoming email (rolling documentation, checked November 2026): https://docs.gitlab.com/administration/incoming_email/

<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, and any earlier-form run it rests on, not a live demonstration of the shipped form. Unknown means no version recorded.

Components (recorded basis):

- gitlab: GitLab (v19.5.3)
- gitlab-omnibus: Omnibus GitLab (19.5.3+ce.0)
- gitlab-omnibus-ee: Omnibus GitLab EE (19.5.3+ee.0)
- gitlab-docs: GitLab documentation (rolling) (unknown)

Claims (full source mapping in the JSON block below):

- install-method (REASONED; gitlab-docs): GitLab's recommended single-server path is the Omnibus Linux package, source of the defaults here; the Docker image runs the same build with /etc/gitlab and data on persistent volumes, and Helm on Kubernetes is a larger, different config surface. Pick one method and harden it.
- edition-ee-free (REASONED; gitlab-omnibus-ee, gitlab-docs): Edition makes no difference to this guide: an Enterprise package with no licence runs the GitLab Free tier, feature-identical to CE for every control here, and the Premium and Ultimate features flagged as not in CE are equally unavailable until a licence is added. The 19.5.3+ee.0 and 19.5.3+ce.0 gitlab.rb.template are byte-identical, so every package default here holds on either.
- root-random (REASONED; gitlab): The root admin is seeded with a forced random password when GITLAB_ROOT_PASSWORD is blank: 003_admin.rb skips creation if an admin exists, builds admin: true, sets password_automatically_set and force_random_password, and prints a first-visit prompt.
- root-preset (REASONED; gitlab): A preset root password is used verbatim only when GITLAB_ROOT_PASSWORD is set, and it is echoed to the console only when display_initial_root_password is true; otherwise the console shows a masked value.
- root-omnibus-file (REASONED; gitlab-omnibus, gitlab-docs): The Omnibus package attributes are initial_root_password nil, display false and store_initial_root_password false, so the package does not persist the generated password; the automatic write to /etc/gitlab/initial_root_password, deleted after 24 hours, is the Docker image behaviour and a documented install step, not the package default.
- net-host-http (REASONED; gitlab): The default application listener is plain HTTP on port 80 with host localhost: host defaults to localhost, https to false and port to 443-or-80, and gitlab.yml.example ships host localhost, port 80 and https false.
- net-external-url (REASONED; gitlab-omnibus): Omnibus derives every public URL, the nginx scheme and listen ports from a single external_url; the gitlab_rails['nginx'] listen_port and listen_https default nil and follow the scheme, and redirect_http_to_https defaults false, so external_url http serves the UI, git and API in clear text on 80.
- net-tls (REASONED; gitlab-omnibus, gitlab-docs): TLS is opt-in: external_url https makes bundled nginx terminate with Let's Encrypt or ssl_certificate and ssl_certificate_key, letsencrypt['enable'] defaults nil, and redirect_http_to_https defaults false; until TLS is on, the UI, git-over-HTTP and API cross the wire in clear text.
- letsencrypt-path (REASONED; gitlab-omnibus, gitlab-docs): With the bundled nginx, enable Let's Encrypt by setting letsencrypt['enable'] = true and a real letsencrypt['contact_emails'] so expiry warnings reach you; the certificate auto-renews because letsencrypt['auto_renew'] defaults true, renewing about every 4 days by default (letsencrypt['auto_renew_day_of_month'] is */4). Otherwise supply explicit ssl_certificate and ssl_certificate_key files.
- reverse-proxy (REASONED; gitlab-omnibus, gitlab-docs): To terminate TLS at a proxy, bind the instance privately: nginx['enable'] defaults true, so set gitlab_rails['nginx']['listen_addresses'] to loopback or disable bundled nginx with nginx['enable'] false, and make the proxy pass the HTTPS scheme through so GitLab builds correct URLs.
- internal-transport (REASONED; gitlab-omnibus, gitlab-docs): On a single node GitLab reaches PostgreSQL, Redis, Gitaly and Workhorse over UNIX sockets by default: postgresql['listen_address'] is nil, redis uses redis_socket, Gitaly and Workhorse use sockets. Internal TLS (gitaly tls_listen_addr, postgresql['ssl'] default on, redis['tls_port'] default nil) is for split nodes.
- signup-open (REASONED; gitlab): Self-service signup is on by default: signup_enabled defaults to true in the initializer and is surfaced as the admin setting of the same name.
- signup-approval (REASONED; gitlab): New signups are held for admin approval by default: require_admin_approval_after_user_signup defaults to true, so a self-registered account is inactive until approved; for a private forge set signup_enabled false rather than relying on approval.
- signin-password (REASONED; gitlab): Password sign-in is on by default: signin_enabled defaults to true, and password_authentication_enabled_for_git is true with password_authentication_enabled_for_web following signin_enabled.
- signup-confirmation (REASONED; gitlab, gitlab-docs): Beyond the signup on/off toggle, new accounts need not confirm their email by default: email_confirmation_setting defaults 'off', and the domain allowlist and email_restrictions ship empty. Require email confirmation and restrict sign-up to allowed domains if signup stays open.
- mfa-off (REASONED; gitlab, gitlab-docs): There is no instance-wide second-factor requirement by default: require_two_factor_authentication defaults false and two_factor_grace_period is 48 hours; enforcement is available on all tiers and per group, and machine credentials still bypass it.
- password-length (REASONED; gitlab): The minimum password length default is 8: DEFAULT_MINIMUM_PASSWORD_LENGTH is 8 and minimum_password_length uses it; raise it.
- admin-mode (REASONED; gitlab, gitlab-docs): Admin mode is off by default: admin_mode defaults false, so an administrator's session carries full admin rights throughout. Enable it under Admin, Settings, General, Sign-in restrictions so administrators must re-authenticate before administrative actions, which limits a stolen admin session or token.
- sso-ce (REASONED; gitlab-docs): CE supports external authentication: LDAP, instance-wide SAML and OpenID Connect via OmniAuth. Wiring one is an option, but running local accounts only is also supportable; then the compensating controls carry the weight, so keep sign-up closed, require 2FA for every account, enable admin mode, raise the password policy and shorten sessions. Group-level SAML and SCIM are Premium and above, not CE.
- session-controls (REASONED; gitlab): Sessions are long by default: session_expire_delay is 10080 minutes (7 days) and unauthenticated sessions last 2 hours; notify_on_unknown_sign_in defaults true. The failed-login unlock period and unique_ips_limit controls ship disabled; enable them to slow credential stuffing.
- token-taxonomy (REASONED; gitlab-docs): GitLab issues many non-interactive credentials: personal, project and group access tokens, deploy tokens, deploy keys, impersonation and CI job tokens. Each bypasses 2FA, so scope every one to least privilege, prefer a project or group token over a personal one, and rotate them.
- pat-expiry (REASONED; gitlab): Personal access tokens require an expiry by default: require_personal_access_token_expiry defaults true; scope PATs narrowly, since a token bypasses 2FA.
- ssh-key-policy (REASONED; gitlab): SSH key-type restrictions ship open: rsa, dsa, ecdsa and ed25519 key_restriction default to 0, meaning any size is allowed and no type is forbidden (default_min_key_size returns 0 outside FIPS). Set minimum key sizes, forbid weak types, and require key expiry.
- visibility-private (REASONED; gitlab): Default project, group and snippet visibility is private: all three defaults resolve to default_projects_features visibility, which the initializer sets to PRIVATE, where PRIVATE is 0, INTERNAL 10 and PUBLIC 20; internal admits every signed-in non-external user.
- default-roles (REASONED; gitlab): Namespace creation is broad by default: default_project_creation is Developer-and-above, can_create_group defaults true, and user_default_external defaults false, so every approved user is a full internal user; default_branch_protection defaults 2 (fully protected). Restrict who can create groups and projects.
- repo-protections-ce (REASONED; gitlab-docs): In CE, protect the default branch with protected branches and protected tags, controlling who can push and merge. Push rules, merge-request approval rules, code-owner approval and protected environments are Premium and above, not CE; use protected branches plus maintainer-only merge instead of relying on them.
- ci-rce (REASONED; gitlab-docs): A registered runner executing a pipeline runs the project's .gitlab-ci.yml as arbitrary code on the runner host; runners are operator-registered, so an exposed instance becomes code execution once a runner is attached and a pipeline can be triggered.
- runner-scoping (REASONED; gitlab-docs): Keep instance (shared) runners off untrusted projects: scope each runner to a project or group, and register with the current runner authentication tokens, not the deprecated registration-token flow. A runner attached to the instance runs any project's jobs as code.
- ci-variables (REASONED; gitlab-docs): Never put secrets in .gitlab-ci.yml. Store them as CI/CD variables marked protected (exposed only to protected branches and tags) and masked (hidden in job logs), or as file variables; masking has format rules and is not encryption-at-rest from the operator.
- ci-job-token (REASONED; gitlab-docs): Each job gets a CI_JOB_TOKEN that can call the API as the job's user; scope it with the job-token allowlist so a job reaches only the projects you list, rather than leaving the token able to reach every project the user can.
- pipeline-untrusted (REASONED; gitlab-docs): Pipelines for merge requests from forks run contributor-authored .gitlab-ci.yml; keep them off runners that hold secrets or reach internal networks, require approval to run fork pipelines, and do not expose protected variables to them.
- runner-executors (REASONED; gitlab-docs): Choose runner executors by risk: run a default Docker-executor runner for ordinary jobs, which in non-privileged mode isolates each job in its own container. Run jobs as a non-root user, drop SETUID and SETGID, and never pass --privileged, which would hand a job the host's root capabilities.
- shell-executor-hardening (REASONED; gitlab-docs): Attach a shell-executor runner only for jobs needing host kernel features: it runs job scripts on the host as the GitLab Runner user and can read other projects built there, the highest-risk executor. Harden it with a dedicated unprivileged --user, systemd cgroup and Landlock confinement, and Run-untagged-jobs cleared so only trusted tagged jobs reach it, never on shared or public projects.
- registry-off (REASONED; gitlab-omnibus, gitlab): The bundled container registry is off by default: registry_enabled defaults false; it is enabled by configuring registry_external_url, and when on its nginx vhost listens on 5050 with the registry process on loopback 127.0.0.1:5000; the project feature flag gates the UI, not the service.
- packages-depproxy (REASONED; gitlab-omnibus, gitlab-docs): The package registry and the dependency proxy are off by default: packages_enabled and dependency_proxy_enabled default nil (unset). If enabled, they authenticate with the instance's own tokens and share its TLS, so publish their endpoints deliberately and set cleanup or expiration policies.
- secrets-at-rest (REASONED; gitlab-omnibus): The instance encryption secrets live in /etc/gitlab/gitlab-secrets.json in Omnibus; the template documents that it is generated and can be synced, its only at-rest protection is filesystem permissions, and a leak undermines the data it keys.
- secrets-keys-loss (REASONED; gitlab-omnibus, gitlab-docs): gitlab-secrets.json keys the database-encrypted columns: 2FA secrets, CI/CD variables and integration tokens. Leak it and those secrets are exposed; lose it and the columns are unrecoverable even though the database restores. The template can prevent regeneration; rotation is a deliberate operator procedure.
- internal-listeners (REASONED; gitlab-omnibus): Bundled services bind locally by default and must stay there on a single node: Puma on 127.0.0.1:8080, Workhorse and the registry process on loopback, and Gitaly, PostgreSQL and Redis over UNIX sockets. Do not bind any of them to a public interface.
- monitoring-prometheus (REASONED; gitlab-omnibus, gitlab-docs): The bundled monitoring stack binds loopback: Prometheus on localhost:9090, node_exporter on localhost:9100, gitlab_exporter on localhost:9168, and the Redis, PostgreSQL and Alertmanager exporters likewise. prometheus_monitoring is enabled by default; keep every exporter off the public interface.
- monitoring-allowlist (REASONED; gitlab-omnibus, gitlab): GitLab's metrics and monitoring endpoints are gated to loopback by default: gitlab_rails['monitoring_whitelist'] defaults to 127.0.0.0/8 and ::1/128 and the monitoring ip_whitelist to 127.0.0.1/8. Keep the allowlist tight; widening it exposes health and metrics data.
- health-endpoints (REASONED; gitlab-docs): GitLab serves /-/health, /-/readiness and /-/liveness and a Prometheus /-/metrics endpoint; the detailed readiness and liveness output and metrics are restricted to the monitoring allowlist or a token, so do not open them to the internet.
- rate-limits (REASONED; gitlab, gitlab-docs): Most request rate limits ship disabled: the throttle_* toggles (protected paths, authenticated and unauthenticated API, web and Git) default false. The raw-blob (300/min) and users-by-id (300) limits are on. Enable the protected-paths and API throttles for an internet-facing instance.
- real-ip-proxy (REASONED; gitlab-omnibus): Behind a proxy or CDN, set gitlab_rails['trusted_proxies'] and gitlab_rails['nginx']['real_ip_trusted_addresses'] (both default empty) so logs, rate limits and abuse controls see the client IP, not the proxy. Without them every request appears to come from the proxy.
- audit-ce-tier (REASONED; gitlab-docs): CE records a limited set of audit events and writes logs under /var/log/gitlab (production.log, audit_json.log, api_json.log). Comprehensive audit events, audit-event streaming, the credentials inventory and the compliance center are Premium and above, not CE; ship logs off-host instead.
- backup-scope (REASONED; gitlab-docs): gitlab-backup create writes one tar of application data (database, repositories, LFS, uploads, artifacts, packages, registry and more). It does NOT include /etc/gitlab config, gitlab-secrets.json, object-storage contents, or TLS and SSH host keys, so the tar alone cannot rebuild a working instance.
- backup-secrets-separate (REASONED; gitlab-docs): Back up /etc/gitlab/gitlab-secrets.json and /etc/gitlab/gitlab.rb separately and store them apart from the data tar. The secrets file holds the database encryption key; without it, restored 2FA secrets, CI/CD variables and tokens are unrecoverable. Protect it like the database.
- backup-encryption-offsite (REASONED; gitlab-docs): Send backups offsite and encrypt them: the task can upload to S3, GCS or Azure and encrypt at rest. Keep local archives mode 0600 owned by the git user, and remember backup_keep_time prunes only local copies, not remote ones.
- restore-drill (REASONED; gitlab-docs): gitlab-backup restore needs a GitLab version matching the backup; restore the secrets and config files first, then the tar. A backup you have never restored is unproven, so run a periodic test-restore onto a scratch host as the only real evidence the backup works.
- upgrade-cadence (REASONED; gitlab-docs): GitLab ships a minor monthly and patch releases roughly twice monthly; security fixes are backported to the current and previous two monthly releases, and high or critical issues get a dedicated patch. Track security releases and upgrade promptly; an exposed, unpatched forge is the real risk.
- upgrade-stops (REASONED; gitlab-docs): You cannot jump arbitrary versions: GitLab has required upgrade stops you must pass through, and for 19.x they are 19.2, 19.5, 19.8 and 19.11, taking the latest patch of each. Let background migrations finish between steps, and use the official Upgrade Path tool to plan the route.
- email-security (REASONED; gitlab-omnibus, gitlab-docs): If you send mail, require SMTP TLS: smtp_enable_starttls_auto defaults true, so keep it on and verify the server certificate. Incoming email (Reply-by-email) adds a mailbox credential to protect, and notification emails can carry private issue and code content, so scope recipients.
- ssh-22 (REASONED; gitlab, gitlab-omnibus): Git-over-SSH uses the host sshd on port 22 via gitlab-shell by default (ssh_port 22), and the optional bundled gitlab-sshd is off by default and listens on localhost:2222 when enabled.
- ssrf-webhooks (REASONED; gitlab): Webhook and integration SSRF to the local network is fail-closed by default: allow_local_requests_from_web_hooks_and_services defaults false, so a webhook cannot reach loopback or internal IPs unless an admin widens it.
- ssrf-system-hooks (REASONED; gitlab): Admin system hooks may reach the local network by default: allow_local_requests_from_system_hooks defaults true, the opposite of the web-hook default; it is admin-only but worth the same care.
- verify-listeners (REASONED; gitlab, gitlab-omnibus): ss inventories local binds in this namespace only; expect nginx on 80 or 443, SSH on 22 and, with the registry on, 5050, and treat a wildcard bind on any as all-interfaces exposure; a failed inventory proves no absence.
- verify-tls (REASONED; gitlab): The probe fetches /users/sign_in over HTTPS with certificate validation on, so a completed fetch showing the new_user sign-in form confirms the application and TLS, while a nonzero exit means the handshake or connection failed and the result is inconclusive.
- verify-anon (REASONED; gitlab): By default GitLab serves /explore/projects to anonymous callers with 200, listing only public projects; with default-private visibility that list is empty, so any project shown is public, and a redirect to /users/sign_in means anonymous browsing is restricted.
- verify-rootfile (REASONED; gitlab-omnibus, gitlab-docs): On Omnibus the generated root password is written to /etc/gitlab/initial_root_password and deleted after 24 hours, so a present file means the generated password was probably not rotated; absence does not prove rotation, and a failed docker exec is not a result.
- verify-internal (REASONED; gitlab-omnibus, gitlab): ss inventories local binds in this namespace only; GitLab's bundled Puma (8080), Prometheus (9090), node_exporter (9100) and gitlab_exporter (9168) should answer only on loopback, so treat a wildcard bind on any as internal exposure; a failed inventory proves no absence.
- verify-backup (REASONED; gitlab-docs): The check lists a recent gitlab-backup data tar and a separate gitlab-secrets.json and reports presence; a missing or stale data tar, or a missing secrets file, means the instance is not recoverable, and absence of the directory is not proof a backup ran elsewhere.

````json
{
  "schema": 1,
  "checked": "2026-11-10",
  "documentation_checked": "2026-11",
  "body_sha256": "33847a992ac1079e1b78c026357603136dd1e2afd074ae038d543102b1d79a10",
  "components": {
    "gitlab": {
      "name": "GitLab",
      "basis": "v19.5.3",
      "sources": {
        "sfb8995e04c56": "https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/db/fixtures/production/003_admin.rb",
        "s89baa0ac55a5": "https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/initializers/1_settings.rb",
        "s39a414417912": "https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/app/models/application_setting_implementation.rb",
        "sfa55e9a8e36b": "https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/lib/gitlab/visibility_level.rb",
        "s975cf7efc7d9": "https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/gitlab.yml.example"
      }
    },
    "gitlab-omnibus": {
      "name": "Omnibus GitLab",
      "basis": "19.5.3+ce.0",
      "sources": {
        "sd8e89739412c": "https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-config-template/gitlab.rb.template",
        "s01015d478714": "https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-cookbooks/gitlab/attributes/default.rb",
        "sf630c13816a7": "https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-cookbooks/gitlab/recipes/database_migrations.rb",
        "s6a67a0d7b16d": "https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-cookbooks/monitoring/attributes/default.rb"
      }
    },
    "gitlab-omnibus-ee": {
      "name": "Omnibus GitLab EE",
      "basis": "19.5.3+ee.0",
      "sources": {
        "s64451838daff": "https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ee.0/files/gitlab-config-template/gitlab.rb.template"
      }
    },
    "gitlab-docs": {
      "name": "GitLab documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "sbb2857fe55a3": "https://docs.gitlab.com/install/",
        "s3b7ac561a92e": "https://docs.gitlab.com/install/docker/installation/",
        "s483220bc691e": "https://docs.gitlab.com/omnibus/settings/ssl/",
        "sb3186fea43e9": "https://docs.gitlab.com/omnibus/settings/nginx/",
        "s8e79437dfb4e": "https://docs.gitlab.com/administration/gitaly/tls_support/",
        "sa230674a0931": "https://docs.gitlab.com/security/user_email_confirmation/",
        "s0347014ce554": "https://docs.gitlab.com/security/two_factor_authentication/",
        "s035c6a51c221": "https://docs.gitlab.com/administration/auth/ldap/",
        "s75e0854bebc5": "https://docs.gitlab.com/integration/omniauth/",
        "s9382f6bad223": "https://docs.gitlab.com/security/tokens/",
        "sd0a809497adf": "https://docs.gitlab.com/user/profile/personal_access_tokens/",
        "sac048b94ad67": "https://docs.gitlab.com/user/project/repository/branches/protected/",
        "se768377d00ab": "https://docs.gitlab.com/user/project/repository/push_rules/",
        "sd24339a14064": "https://docs.gitlab.com/user/project/merge_requests/approvals/",
        "sc65c8ef0ffca": "https://docs.gitlab.com/ci/environments/protected_environments/",
        "s050e2202cf3c": "https://docs.gitlab.com/ci/runners/",
        "s08e832874541": "https://docs.gitlab.com/ci/runners/runners_scope/",
        "sd2cbff5d5d6e": "https://docs.gitlab.com/ci/runners/new_creation_workflow/",
        "s103dc59201ba": "https://docs.gitlab.com/ci/variables/",
        "saef0483b7be7": "https://docs.gitlab.com/ci/jobs/ci_job_token/",
        "s1bb67fcf69b5": "https://docs.gitlab.com/ci/pipeline_security/",
        "sec04b7174f3b": "https://docs.gitlab.com/administration/packages/",
        "s3cb2d218349c": "https://docs.gitlab.com/user/packages/dependency_proxy/",
        "s334e867d05ee": "https://docs.gitlab.com/rate_limits/",
        "s47f3b7f502d9": "https://docs.gitlab.com/administration/monitoring/prometheus/",
        "s4e0ac852b01a": "https://docs.gitlab.com/administration/monitoring/health_check/",
        "s51affdc58032": "https://docs.gitlab.com/administration/compliance/audit_event_reports/",
        "s41a105cf0512": "https://docs.gitlab.com/administration/logs/",
        "sf90ef57396f1": "https://docs.gitlab.com/administration/backup_restore/backup_gitlab/",
        "s6d0bfaef13bb": "https://docs.gitlab.com/administration/backup_restore/restore_gitlab/",
        "seafc653b2080": "https://docs.gitlab.com/policy/maintenance/",
        "s358d16058e6c": "https://docs.gitlab.com/update/upgrade_paths/",
        "s0b37ddbcc720": "https://docs.gitlab.com/update/",
        "s06477c467b71": "https://docs.gitlab.com/omnibus/settings/smtp/",
        "s739190aa3e20": "https://docs.gitlab.com/administration/incoming_email/",
        "s10026bf70b63": "https://docs.gitlab.com/administration/license/",
        "s3cd566256c20": "https://docs.gitlab.com/administration/settings/sign_in_restrictions/",
        "s108b5fccb33a": "https://docs.gitlab.com/runner/executors/",
        "sba387b3c1903": "https://docs.gitlab.com/runner/executors/shell/",
        "seb30e3937183": "https://docs.gitlab.com/runner/security/",
        "s9d69c01850b6": "https://docs.gitlab.com/ci/runners/configure_runners/"
      }
    }
  },
  "claims": {
    "install-method": {"text": "GitLab's recommended single-server path is the Omnibus Linux package, source of the defaults here; the Docker image runs the same build with /etc/gitlab and data on persistent volumes, and Helm on Kubernetes is a larger, different config surface. Pick one method and harden it.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:sbb2857fe55a3", "gitlab-docs:s3b7ac561a92e"], "status": "REASONED"},
    "edition-ee-free": {"text": "Edition makes no difference to this guide: an Enterprise package with no licence runs the GitLab Free tier, feature-identical to CE for every control here, and the Premium and Ultimate features flagged as not in CE are equally unavailable until a licence is added. The 19.5.3+ee.0 and 19.5.3+ce.0 gitlab.rb.template are byte-identical, so every package default here holds on either.", "components": ["gitlab-omnibus-ee", "gitlab-docs"], "sources": ["gitlab-omnibus-ee:s64451838daff", "gitlab-docs:s10026bf70b63"], "status": "REASONED"},
    "root-random": {"text": "The root admin is seeded with a forced random password when GITLAB_ROOT_PASSWORD is blank: 003_admin.rb skips creation if an admin exists, builds admin: true, sets password_automatically_set and force_random_password, and prints a first-visit prompt.", "components": ["gitlab"], "sources": ["gitlab:sfb8995e04c56"], "status": "REASONED"},
    "root-preset": {"text": "A preset root password is used verbatim only when GITLAB_ROOT_PASSWORD is set, and it is echoed to the console only when display_initial_root_password is true; otherwise the console shows a masked value.", "components": ["gitlab"], "sources": ["gitlab:sfb8995e04c56"], "status": "REASONED"},
    "root-omnibus-file": {"text": "The Omnibus package attributes are initial_root_password nil, display false and store_initial_root_password false, so the package does not persist the generated password; the automatic write to /etc/gitlab/initial_root_password, deleted after 24 hours, is the Docker image behaviour and a documented install step, not the package default.", "components": ["gitlab-omnibus", "gitlab-docs"], "sources": ["gitlab-omnibus:s01015d478714", "gitlab-omnibus:sd8e89739412c", "gitlab-omnibus:sf630c13816a7", "gitlab-docs:s3b7ac561a92e"], "status": "REASONED"},
    "net-host-http": {"text": "The default application listener is plain HTTP on port 80 with host localhost: host defaults to localhost, https to false and port to 443-or-80, and gitlab.yml.example ships host localhost, port 80 and https false.", "components": ["gitlab"], "sources": ["gitlab:s89baa0ac55a5", "gitlab:s975cf7efc7d9"], "status": "REASONED"},
    "net-external-url": {"text": "Omnibus derives every public URL, the nginx scheme and listen ports from a single external_url; the gitlab_rails['nginx'] listen_port and listen_https default nil and follow the scheme, and redirect_http_to_https defaults false, so external_url http serves the UI, git and API in clear text on 80.", "components": ["gitlab-omnibus"], "sources": ["gitlab-omnibus:sd8e89739412c"], "status": "REASONED"},
    "net-tls": {"text": "TLS is opt-in: external_url https makes bundled nginx terminate with Let's Encrypt or ssl_certificate and ssl_certificate_key, letsencrypt['enable'] defaults nil, and redirect_http_to_https defaults false; until TLS is on, the UI, git-over-HTTP and API cross the wire in clear text.", "components": ["gitlab-omnibus", "gitlab-docs"], "sources": ["gitlab-omnibus:sd8e89739412c", "gitlab-docs:s483220bc691e"], "status": "REASONED"},
    "letsencrypt-path": {"text": "With the bundled nginx, enable Let's Encrypt by setting letsencrypt['enable'] = true and a real letsencrypt['contact_emails'] so expiry warnings reach you; the certificate auto-renews because letsencrypt['auto_renew'] defaults true, renewing about every 4 days by default (letsencrypt['auto_renew_day_of_month'] is */4). Otherwise supply explicit ssl_certificate and ssl_certificate_key files.", "components": ["gitlab-omnibus", "gitlab-docs"], "sources": ["gitlab-omnibus:sd8e89739412c", "gitlab-docs:s483220bc691e"], "status": "REASONED"},
    "reverse-proxy": {"text": "To terminate TLS at a proxy, bind the instance privately: nginx['enable'] defaults true, so set gitlab_rails['nginx']['listen_addresses'] to loopback or disable bundled nginx with nginx['enable'] false, and make the proxy pass the HTTPS scheme through so GitLab builds correct URLs.", "components": ["gitlab-omnibus", "gitlab-docs"], "sources": ["gitlab-omnibus:sd8e89739412c", "gitlab-docs:sb3186fea43e9"], "status": "REASONED"},
    "internal-transport": {"text": "On a single node GitLab reaches PostgreSQL, Redis, Gitaly and Workhorse over UNIX sockets by default: postgresql['listen_address'] is nil, redis uses redis_socket, Gitaly and Workhorse use sockets. Internal TLS (gitaly tls_listen_addr, postgresql['ssl'] default on, redis['tls_port'] default nil) is for split nodes.", "components": ["gitlab-omnibus", "gitlab-docs"], "sources": ["gitlab-omnibus:sd8e89739412c", "gitlab-omnibus:s01015d478714", "gitlab-docs:s8e79437dfb4e"], "status": "REASONED"},
    "signup-open": {"text": "Self-service signup is on by default: signup_enabled defaults to true in the initializer and is surfaced as the admin setting of the same name.", "components": ["gitlab"], "sources": ["gitlab:s89baa0ac55a5", "gitlab:s39a414417912"], "status": "REASONED"},
    "signup-approval": {"text": "New signups are held for admin approval by default: require_admin_approval_after_user_signup defaults to true, so a self-registered account is inactive until approved; for a private forge set signup_enabled false rather than relying on approval.", "components": ["gitlab"], "sources": ["gitlab:s39a414417912"], "status": "REASONED"},
    "signin-password": {"text": "Password sign-in is on by default: signin_enabled defaults to true, and password_authentication_enabled_for_git is true with password_authentication_enabled_for_web following signin_enabled.", "components": ["gitlab"], "sources": ["gitlab:s89baa0ac55a5", "gitlab:s39a414417912"], "status": "REASONED"},
    "signup-confirmation": {"text": "Beyond the signup on/off toggle, new accounts need not confirm their email by default: email_confirmation_setting defaults 'off', and the domain allowlist and email_restrictions ship empty. Require email confirmation and restrict sign-up to allowed domains if signup stays open.", "components": ["gitlab", "gitlab-docs"], "sources": ["gitlab:s39a414417912", "gitlab-docs:sa230674a0931"], "status": "REASONED"},
    "mfa-off": {"text": "There is no instance-wide second-factor requirement by default: require_two_factor_authentication defaults false and two_factor_grace_period is 48 hours; enforcement is available on all tiers and per group, and machine credentials still bypass it.", "components": ["gitlab", "gitlab-docs"], "sources": ["gitlab:s39a414417912", "gitlab-docs:s0347014ce554"], "status": "REASONED"},
    "password-length": {"text": "The minimum password length default is 8: DEFAULT_MINIMUM_PASSWORD_LENGTH is 8 and minimum_password_length uses it; raise it.", "components": ["gitlab"], "sources": ["gitlab:s39a414417912"], "status": "REASONED"},
    "admin-mode": {"text": "Admin mode is off by default: admin_mode defaults false, so an administrator's session carries full admin rights throughout. Enable it under Admin, Settings, General, Sign-in restrictions so administrators must re-authenticate before administrative actions, which limits a stolen admin session or token.", "components": ["gitlab", "gitlab-docs"], "sources": ["gitlab:s39a414417912", "gitlab-docs:s3cd566256c20"], "status": "REASONED"},
    "sso-ce": {"text": "CE supports external authentication: LDAP, instance-wide SAML and OpenID Connect via OmniAuth. Wiring one is an option, but running local accounts only is also supportable; then the compensating controls carry the weight, so keep sign-up closed, require 2FA for every account, enable admin mode, raise the password policy and shorten sessions. Group-level SAML and SCIM are Premium and above, not CE.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:s035c6a51c221", "gitlab-docs:s75e0854bebc5"], "status": "REASONED"},
    "session-controls": {"text": "Sessions are long by default: session_expire_delay is 10080 minutes (7 days) and unauthenticated sessions last 2 hours; notify_on_unknown_sign_in defaults true. The failed-login unlock period and unique_ips_limit controls ship disabled; enable them to slow credential stuffing.", "components": ["gitlab"], "sources": ["gitlab:s89baa0ac55a5", "gitlab:s39a414417912"], "status": "REASONED"},
    "token-taxonomy": {"text": "GitLab issues many non-interactive credentials: personal, project and group access tokens, deploy tokens, deploy keys, impersonation and CI job tokens. Each bypasses 2FA, so scope every one to least privilege, prefer a project or group token over a personal one, and rotate them.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:s9382f6bad223", "gitlab-docs:sd0a809497adf"], "status": "REASONED"},
    "pat-expiry": {"text": "Personal access tokens require an expiry by default: require_personal_access_token_expiry defaults true; scope PATs narrowly, since a token bypasses 2FA.", "components": ["gitlab"], "sources": ["gitlab:s39a414417912"], "status": "REASONED"},
    "ssh-key-policy": {"text": "SSH key-type restrictions ship open: rsa, dsa, ecdsa and ed25519 key_restriction default to 0, meaning any size is allowed and no type is forbidden (default_min_key_size returns 0 outside FIPS). Set minimum key sizes, forbid weak types, and require key expiry.", "components": ["gitlab"], "sources": ["gitlab:s39a414417912"], "status": "REASONED"},
    "visibility-private": {"text": "Default project, group and snippet visibility is private: all three defaults resolve to default_projects_features visibility, which the initializer sets to PRIVATE, where PRIVATE is 0, INTERNAL 10 and PUBLIC 20; internal admits every signed-in non-external user.", "components": ["gitlab"], "sources": ["gitlab:s39a414417912", "gitlab:s89baa0ac55a5", "gitlab:sfa55e9a8e36b"], "status": "REASONED"},
    "default-roles": {"text": "Namespace creation is broad by default: default_project_creation is Developer-and-above, can_create_group defaults true, and user_default_external defaults false, so every approved user is a full internal user; default_branch_protection defaults 2 (fully protected). Restrict who can create groups and projects.", "components": ["gitlab"], "sources": ["gitlab:s89baa0ac55a5", "gitlab:s39a414417912"], "status": "REASONED"},
    "repo-protections-ce": {"text": "In CE, protect the default branch with protected branches and protected tags, controlling who can push and merge. Push rules, merge-request approval rules, code-owner approval and protected environments are Premium and above, not CE; use protected branches plus maintainer-only merge instead of relying on them.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:sac048b94ad67", "gitlab-docs:se768377d00ab", "gitlab-docs:sd24339a14064", "gitlab-docs:sc65c8ef0ffca"], "status": "REASONED"},
    "ci-rce": {"text": "A registered runner executing a pipeline runs the project's .gitlab-ci.yml as arbitrary code on the runner host; runners are operator-registered, so an exposed instance becomes code execution once a runner is attached and a pipeline can be triggered.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:s050e2202cf3c"], "status": "REASONED"},
    "runner-scoping": {"text": "Keep instance (shared) runners off untrusted projects: scope each runner to a project or group, and register with the current runner authentication tokens, not the deprecated registration-token flow. A runner attached to the instance runs any project's jobs as code.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:s08e832874541", "gitlab-docs:sd2cbff5d5d6e"], "status": "REASONED"},
    "ci-variables": {"text": "Never put secrets in .gitlab-ci.yml. Store them as CI/CD variables marked protected (exposed only to protected branches and tags) and masked (hidden in job logs), or as file variables; masking has format rules and is not encryption-at-rest from the operator.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:s103dc59201ba"], "status": "REASONED"},
    "ci-job-token": {"text": "Each job gets a CI_JOB_TOKEN that can call the API as the job's user; scope it with the job-token allowlist so a job reaches only the projects you list, rather than leaving the token able to reach every project the user can.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:saef0483b7be7"], "status": "REASONED"},
    "pipeline-untrusted": {"text": "Pipelines for merge requests from forks run contributor-authored .gitlab-ci.yml; keep them off runners that hold secrets or reach internal networks, require approval to run fork pipelines, and do not expose protected variables to them.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:s1bb67fcf69b5"], "status": "REASONED"},
    "runner-executors": {"text": "Choose runner executors by risk: run a default Docker-executor runner for ordinary jobs, which in non-privileged mode isolates each job in its own container. Run jobs as a non-root user, drop SETUID and SETGID, and never pass --privileged, which would hand a job the host's root capabilities.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:s108b5fccb33a", "gitlab-docs:seb30e3937183"], "status": "REASONED"},
    "shell-executor-hardening": {"text": "Attach a shell-executor runner only for jobs needing host kernel features: it runs job scripts on the host as the GitLab Runner user and can read other projects built there, the highest-risk executor. Harden it with a dedicated unprivileged --user, systemd cgroup and Landlock confinement, and Run-untagged-jobs cleared so only trusted tagged jobs reach it, never on shared or public projects.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:sba387b3c1903", "gitlab-docs:seb30e3937183", "gitlab-docs:s9d69c01850b6"], "status": "REASONED"},
    "registry-off": {"text": "The bundled container registry is off by default: registry_enabled defaults false; it is enabled by configuring registry_external_url, and when on its nginx vhost listens on 5050 with the registry process on loopback 127.0.0.1:5000; the project feature flag gates the UI, not the service.", "components": ["gitlab-omnibus", "gitlab"], "sources": ["gitlab-omnibus:s01015d478714", "gitlab-omnibus:sd8e89739412c", "gitlab:s975cf7efc7d9"], "status": "REASONED"},
    "packages-depproxy": {"text": "The package registry and the dependency proxy are off by default: packages_enabled and dependency_proxy_enabled default nil (unset). If enabled, they authenticate with the instance's own tokens and share its TLS, so publish their endpoints deliberately and set cleanup or expiration policies.", "components": ["gitlab-omnibus", "gitlab-docs"], "sources": ["gitlab-omnibus:s01015d478714", "gitlab-docs:sec04b7174f3b", "gitlab-docs:s3cb2d218349c"], "status": "REASONED"},
    "secrets-at-rest": {"text": "The instance encryption secrets live in /etc/gitlab/gitlab-secrets.json in Omnibus; the template documents that it is generated and can be synced, its only at-rest protection is filesystem permissions, and a leak undermines the data it keys.", "components": ["gitlab-omnibus"], "sources": ["gitlab-omnibus:sd8e89739412c"], "status": "REASONED"},
    "secrets-keys-loss": {"text": "gitlab-secrets.json keys the database-encrypted columns: 2FA secrets, CI/CD variables and integration tokens. Leak it and those secrets are exposed; lose it and the columns are unrecoverable even though the database restores. The template can prevent regeneration; rotation is a deliberate operator procedure.", "components": ["gitlab-omnibus", "gitlab-docs"], "sources": ["gitlab-omnibus:sd8e89739412c", "gitlab-docs:sf90ef57396f1"], "status": "REASONED"},
    "internal-listeners": {"text": "Bundled services bind locally by default and must stay there on a single node: Puma on 127.0.0.1:8080, Workhorse and the registry process on loopback, and Gitaly, PostgreSQL and Redis over UNIX sockets. Do not bind any of them to a public interface.", "components": ["gitlab-omnibus"], "sources": ["gitlab-omnibus:sd8e89739412c", "gitlab-omnibus:s01015d478714"], "status": "REASONED"},
    "monitoring-prometheus": {"text": "The bundled monitoring stack binds loopback: Prometheus on localhost:9090, node_exporter on localhost:9100, gitlab_exporter on localhost:9168, and the Redis, PostgreSQL and Alertmanager exporters likewise. prometheus_monitoring is enabled by default; keep every exporter off the public interface.", "components": ["gitlab-omnibus", "gitlab-docs"], "sources": ["gitlab-omnibus:s6a67a0d7b16d", "gitlab-docs:s47f3b7f502d9"], "status": "REASONED"},
    "monitoring-allowlist": {"text": "GitLab's metrics and monitoring endpoints are gated to loopback by default: gitlab_rails['monitoring_whitelist'] defaults to 127.0.0.0/8 and ::1/128 and the monitoring ip_whitelist to 127.0.0.1/8. Keep the allowlist tight; widening it exposes health and metrics data.", "components": ["gitlab-omnibus", "gitlab"], "sources": ["gitlab-omnibus:sd8e89739412c", "gitlab:s89baa0ac55a5"], "status": "REASONED"},
    "health-endpoints": {"text": "GitLab serves /-/health, /-/readiness and /-/liveness and a Prometheus /-/metrics endpoint; the detailed readiness and liveness output and metrics are restricted to the monitoring allowlist or a token, so do not open them to the internet.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:s4e0ac852b01a"], "status": "REASONED"},
    "rate-limits": {"text": "Most request rate limits ship disabled: the throttle_* toggles (protected paths, authenticated and unauthenticated API, web and Git) default false. The raw-blob (300/min) and users-by-id (300) limits are on. Enable the protected-paths and API throttles for an internet-facing instance.", "components": ["gitlab", "gitlab-docs"], "sources": ["gitlab:s39a414417912", "gitlab-docs:s334e867d05ee"], "status": "REASONED"},
    "real-ip-proxy": {"text": "Behind a proxy or CDN, set gitlab_rails['trusted_proxies'] and gitlab_rails['nginx']['real_ip_trusted_addresses'] (both default empty) so logs, rate limits and abuse controls see the client IP, not the proxy. Without them every request appears to come from the proxy.", "components": ["gitlab-omnibus"], "sources": ["gitlab-omnibus:sd8e89739412c"], "status": "REASONED"},
    "audit-ce-tier": {"text": "CE records a limited set of audit events and writes logs under /var/log/gitlab (production.log, audit_json.log, api_json.log). Comprehensive audit events, audit-event streaming, the credentials inventory and the compliance center are Premium and above, not CE; ship logs off-host instead.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:s51affdc58032", "gitlab-docs:s41a105cf0512"], "status": "REASONED"},
    "backup-scope": {"text": "gitlab-backup create writes one tar of application data (database, repositories, LFS, uploads, artifacts, packages, registry and more). It does NOT include /etc/gitlab config, gitlab-secrets.json, object-storage contents, or TLS and SSH host keys, so the tar alone cannot rebuild a working instance.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:sf90ef57396f1"], "status": "REASONED"},
    "backup-secrets-separate": {"text": "Back up /etc/gitlab/gitlab-secrets.json and /etc/gitlab/gitlab.rb separately and store them apart from the data tar. The secrets file holds the database encryption key; without it, restored 2FA secrets, CI/CD variables and tokens are unrecoverable. Protect it like the database.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:sf90ef57396f1"], "status": "REASONED"},
    "backup-encryption-offsite": {"text": "Send backups offsite and encrypt them: the task can upload to S3, GCS or Azure and encrypt at rest. Keep local archives mode 0600 owned by the git user, and remember backup_keep_time prunes only local copies, not remote ones.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:sf90ef57396f1"], "status": "REASONED"},
    "restore-drill": {"text": "gitlab-backup restore needs a GitLab version matching the backup; restore the secrets and config files first, then the tar. A backup you have never restored is unproven, so run a periodic test-restore onto a scratch host as the only real evidence the backup works.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:s6d0bfaef13bb"], "status": "REASONED"},
    "upgrade-cadence": {"text": "GitLab ships a minor monthly and patch releases roughly twice monthly; security fixes are backported to the current and previous two monthly releases, and high or critical issues get a dedicated patch. Track security releases and upgrade promptly; an exposed, unpatched forge is the real risk.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:seafc653b2080", "gitlab-docs:s0b37ddbcc720"], "status": "REASONED"},
    "upgrade-stops": {"text": "You cannot jump arbitrary versions: GitLab has required upgrade stops you must pass through, and for 19.x they are 19.2, 19.5, 19.8 and 19.11, taking the latest patch of each. Let background migrations finish between steps, and use the official Upgrade Path tool to plan the route.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:s358d16058e6c"], "status": "REASONED"},
    "email-security": {"text": "If you send mail, require SMTP TLS: smtp_enable_starttls_auto defaults true, so keep it on and verify the server certificate. Incoming email (Reply-by-email) adds a mailbox credential to protect, and notification emails can carry private issue and code content, so scope recipients.", "components": ["gitlab-omnibus", "gitlab-docs"], "sources": ["gitlab-omnibus:sd8e89739412c", "gitlab-docs:s06477c467b71", "gitlab-docs:s739190aa3e20"], "status": "REASONED"},
    "ssh-22": {"text": "Git-over-SSH uses the host sshd on port 22 via gitlab-shell by default (ssh_port 22), and the optional bundled gitlab-sshd is off by default and listens on localhost:2222 when enabled.", "components": ["gitlab", "gitlab-omnibus"], "sources": ["gitlab:s89baa0ac55a5", "gitlab-omnibus:sd8e89739412c"], "status": "REASONED"},
    "ssrf-webhooks": {"text": "Webhook and integration SSRF to the local network is fail-closed by default: allow_local_requests_from_web_hooks_and_services defaults false, so a webhook cannot reach loopback or internal IPs unless an admin widens it.", "components": ["gitlab"], "sources": ["gitlab:s39a414417912"], "status": "REASONED"},
    "ssrf-system-hooks": {"text": "Admin system hooks may reach the local network by default: allow_local_requests_from_system_hooks defaults true, the opposite of the web-hook default; it is admin-only but worth the same care.", "components": ["gitlab"], "sources": ["gitlab:s39a414417912"], "status": "REASONED"},
    "verify-listeners": {"text": "ss inventories local binds in this namespace only; expect nginx on 80 or 443, SSH on 22 and, with the registry on, 5050, and treat a wildcard bind on any as all-interfaces exposure; a failed inventory proves no absence.", "components": ["gitlab", "gitlab-omnibus"], "sources": ["gitlab:s89baa0ac55a5", "gitlab-omnibus:sd8e89739412c"], "status": "REASONED", "verify": [1]},
    "verify-tls": {"text": "The probe fetches /users/sign_in over HTTPS with certificate validation on, so a completed fetch showing the new_user sign-in form confirms the application and TLS, while a nonzero exit means the handshake or connection failed and the result is inconclusive.", "components": ["gitlab"], "sources": ["gitlab:s89baa0ac55a5"], "status": "REASONED", "verify": [2]},
    "verify-anon": {"text": "By default GitLab serves /explore/projects to anonymous callers with 200, listing only public projects; with default-private visibility that list is empty, so any project shown is public, and a redirect to /users/sign_in means anonymous browsing is restricted.", "components": ["gitlab"], "sources": ["gitlab:sfa55e9a8e36b"], "status": "REASONED", "verify": [3]},
    "verify-rootfile": {"text": "On Omnibus the generated root password is written to /etc/gitlab/initial_root_password and deleted after 24 hours, so a present file means the generated password was probably not rotated; absence does not prove rotation, and a failed docker exec is not a result.", "components": ["gitlab-omnibus", "gitlab-docs"], "sources": ["gitlab-omnibus:sd8e89739412c", "gitlab-docs:s3b7ac561a92e"], "status": "REASONED", "verify": [4]},
    "verify-internal": {"text": "ss inventories local binds in this namespace only; GitLab's bundled Puma (8080), Prometheus (9090), node_exporter (9100) and gitlab_exporter (9168) should answer only on loopback, so treat a wildcard bind on any as internal exposure; a failed inventory proves no absence.", "components": ["gitlab-omnibus", "gitlab"], "sources": ["gitlab-omnibus:s6a67a0d7b16d", "gitlab:s89baa0ac55a5"], "status": "REASONED", "verify": [5]},
    "verify-backup": {"text": "The check lists a recent gitlab-backup data tar and a separate gitlab-secrets.json and reports presence; a missing or stale data tar, or a missing secrets file, means the instance is not recoverable, and absence of the directory is not proof a backup ran elsewhere.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:sf90ef57396f1"], "status": "REASONED", "verify": [6]}
  }
}
````
<!-- version-basis:end -->
