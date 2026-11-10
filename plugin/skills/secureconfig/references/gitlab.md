# GitLab: the fail-safe front door, the plain-HTTP listener, and the CI runner as a code-execution host

GitLab CE is a self-hosted DevOps and Git forge. It serves repositories over HTTP and SSH, runs issue tracking, a container registry, and CI/CD pipelines through operator-registered runners. This guide helps your AI assistant check that a deployment is configured securely: rotate the first-run root password, bind privately and set `external_url`, enable TLS, close or gate registration, require a second factor, keep visibility private, and treat every registered runner as a code-execution host.

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

Written against GitLab v19.5.3 and Omnibus GitLab 19.5.3+ce.0; 1 further source carries no recorded version. Metadata reviewed 2026-11-10; documentation checked November 2026. The guide records 23 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

Unlike a forge whose first run is an open installer or a world-known key, GitLab ships a fail-safe front door: the root admin is seeded with a forced random password, self-service signups are held for admin approval, default project and group visibility is private, and webhook SSRF to the local network is off. So the real exposure is not the login page. It is the plain-HTTP, all-interfaces listener that ships before you set `external_url https`, and the CI/CD runner. A runner executing a pipeline runs the project's `.gitlab-ci.yml` as arbitrary code on the runner host, so a reachable instance becomes remote code execution the moment a runner is attached and a pipeline can be triggered. This guide pins GitLab v19.5.3 and reads every application default from the `v19.5.3-ee` source and every package default from Omnibus `19.5.3+ce.0`. The application config file is `gitlab.yml`; the Omnibus package config is `/etc/gitlab/gitlab.rb`. Runner hardening is [self-hosted-ci-runners.md](self-hosted-ci-runners.md); this guide owns the server-side exposure.

## 1. Know the first-run root account and rotate it

GitLab's root admin is not an open installer. The production seed `003_admin.rb` skips creation when an admin already exists, builds the account with `admin: true`, and when `GITLAB_ROOT_PASSWORD` is blank it sets `password_automatically_set = true` and `force_random_password = true`, then prints "You'll be prompted to create one on your first visit." A preset password is used verbatim only when `GITLAB_ROOT_PASSWORD` is set, and it is echoed to the console only when `display_initial_root_password` is true. In Omnibus and the Docker image the generated password is captured and, by the image's effective default, written to `/etc/gitlab/initial_root_password`, a root-readable file the documentation says is deleted on the first reconfigure or restart after 24 hours. Rotate the root password on first sign-in, and in Omnibus read then clear that file. Read it with `docker exec -it gitlab grep 'Password:' /etc/gitlab/initial_root_password`, or preset it through `gitlab_rails['initial_root_password']` in `gitlab.rb`. [Root seed: random password, admin flag and console output](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/db/fixtures/production/003_admin.rb) (skip-if-admin lines 1-4, `admin: true` line 13, `force_random_password` lines 18-20, preset lines 21-22, display lines 37-42, prompt line 44). [Omnibus initial-password attributes](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-cookbooks/gitlab/attributes/default.rb) (`initial_root_password = nil` line 761, `display_initial_root_password = false` line 764, `store_initial_root_password = false` line 765), [config template](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-config-template/gitlab.rb.template) (preset line 868, display line 878, store toggle and `/etc/gitlab/initial_root_password` path lines 880-881). [Migration recipe passes the preset through](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-cookbooks/gitlab/recipes/database_migrations.rb) (`initial_root_password` read line 22, `GITLAB_ROOT_PASSWORD` set line 31), [Docker install docs: reading and deleting the file](https://docs.gitlab.com/install/docker/installation/).

## 2. Bind privately and set `external_url`

The default application listener is plain HTTP on port 80 with host `localhost`. In source, `host` defaults to `localhost`, `https` defaults to false, and `port` is `https ? 443 : 80`, and the shipped `gitlab.yml.example` carries `host: localhost`, `port: 80` and `https: false`. In Omnibus every public URL, the nginx scheme and the listen ports are derived from a single `external_url` the installer generates; nginx `listen_port` and `listen_https` default to nil and are taken from the `external_url` scheme, and `redirect_http_to_https` defaults to false. So an `external_url http://...` serves the whole UI, git-over-HTTP and the API in clear text on port 80, on every interface. Set `external_url` to the public origin, and bind the listener to a private address or loopback behind a reverse proxy. In `/etc/gitlab/gitlab.rb`:

```ruby
external_url 'https://gitlab.example.com'
nginx['listen_addresses'] = ['127.0.0.1']
```

[Application listener defaults](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/initializers/1_settings.rb) (`host` localhost line 197, `https = false` line 200, `port` 443-or-80 line 201), [example config](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/gitlab.yml.example) (`host`, `port`, `https` lines 35-37), [Omnibus external_url and nginx defaults](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-config-template/gitlab.rb.template) (`external_url` line 32, `redirect_http_to_https` false line 2024, `listen_port` nil line 2072, `listen_https` nil line 2076).

## 3. Enable TLS

TLS is opt-in. An `external_url https://...` makes the bundled nginx terminate TLS, with a Let's Encrypt certificate or an explicit `ssl_certificate` and `ssl_certificate_key`; alternatively terminate TLS at a proxy in front of a loopback-bound instance. Until you do, the web UI, git-over-HTTP and the API cross the wire in clear text, so a non-loopback bind sends session cookies and Basic-auth git credentials to any on-path observer. Treat TLS as mandatory before the port is reachable beyond loopback. In `/etc/gitlab/gitlab.rb`:

```ruby
external_url 'https://gitlab.example.com'
nginx['redirect_http_to_https'] = true
nginx['ssl_certificate']     = '/etc/gitlab/ssl/gitlab.example.com.crt'
nginx['ssl_certificate_key'] = '/etc/gitlab/ssl/gitlab.example.com.key'
```

[TLS and redirect settings](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-config-template/gitlab.rb.template) (`redirect_http_to_https` false line 2024, `ssl_certificate` and `ssl_certificate_key` lines 2036-2037, Let's Encrypt block line 3153), [Docker install docs](https://docs.gitlab.com/install/docker/installation/).

## 4. Close or gate registration

Self-service signup is on by default: `signup_enabled` defaults to true, surfaced as the admin setting of the same name. New signups are safer than an open forge because `require_admin_approval_after_user_signup` defaults to true, so a self-registered account is inactive until an admin approves it. Do not rely on that approval discipline for a private instance; clear "Allow new user accounts" under Admin, Settings, General, Sign-up restrictions, which sets `signup_enabled` false. Password sign-in itself is on by default for web and git. In the admin UI, or through `gitlab.rb` `gitlab_rails['gitlab_signup_enabled'] = false`, close registration for a private forge. [Signup and sign-in defaults](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/initializers/1_settings.rb) (`signup_enabled` true line 225, `signin_enabled` true line 226), [application setting defaults](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/app/models/application_setting_implementation.rb) (`password_authentication_enabled_for_git`/`_web` lines 176-177, `require_admin_approval_after_user_signup` true line 204, `signup_enabled` surfaced line 219).

## 5. Require a second factor and raise the password policy

There is no instance-wide second-factor requirement by default: `require_two_factor_authentication` defaults to false and `two_factor_grace_period` is 48 hours. Enforcement is available on all tiers from Admin, Settings, General, Sign-in restrictions, so turn it on, at least for administrators, so local accounts are not password-only. The minimum password length default is 8; raise it. In the admin UI, require two-factor authentication and set a longer minimum password length. [Two-factor and password defaults](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/app/models/application_setting_implementation.rb) (`DEFAULT_MINIMUM_PASSWORD_LENGTH = 8` line 37, `minimum_password_length` line 168, `require_two_factor_authentication` false line 205, `two_factor_grace_period` 48 line 287), [enforce 2FA for all users](https://docs.gitlab.com/security/two_factor_authentication/).

## 6. Keep project and group visibility private

Default project, group and snippet visibility is private. All three admin defaults resolve to `default_projects_features['visibility_level']`, which the initializer sets to `Gitlab::VisibilityLevel::PRIVATE`, and the level constants are `PRIVATE = 0`, `INTERNAL = 10`, `PUBLIC = 20`. Keep them private. "Internal" is not private: it means visible to every signed-in non-external user, so on an instance that allows signup, internal content is readable by every approved registrant. [Visibility defaults resolve to private](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/app/models/application_setting_implementation.rb) (group, project and snippet defaults lines 77, 79, 81), [initializer default PRIVATE](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/initializers/1_settings.rb) (`default_projects_features` visibility line 243), [level constants](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/lib/gitlab/visibility_level.rb) (`PRIVATE`, `INTERNAL`, `PUBLIC` lines 29-31).

## 7. Govern CI/CD: every registered runner is a code-execution host

This is the sharp exposure. A runner executing a pipeline runs the project's `.gitlab-ci.yml` as arbitrary code on the runner host or container, not on the GitLab host. Runners are operator-registered: none ships or auto-registers, so no pipeline runs until an operator attaches a runner with a registration token. That makes "exposed equals RCE" conditional on a registered runner plus a trigger path, and a push, a merge request, or a scheduled or triggered pipeline is such a path. Run each runner as a dedicated, unprivileged account or in a throwaway container, scope registration to the smallest trust boundary, and keep untrusted merge-request pipelines off any runner that can reach secrets or internal networks. Runner configuration and isolation are [self-hosted-ci-runners.md](self-hosted-ci-runners.md). [GitLab runners documentation](https://docs.gitlab.com/ci/runners/).

## 8. Know the container registry surface

The bundled container registry is not enabled by default in Omnibus: `registry_enabled` defaults to false. It is turned on by configuring `registry_external_url`, and when on, its nginx vhost listens on port 5050 while the registry process itself listens on loopback `127.0.0.1:5000`. The project feature `container_registry` is true in the example config, but that gates the UI feature, not the service. If you enable the registry, publish 5050 deliberately and front it with the same TLS and authentication as the rest of the instance. [Registry disabled by default](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-cookbooks/gitlab/attributes/default.rb) (`registry_enabled = false` line 298), [registry URL, loopback process and 5050 vhost](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-config-template/gitlab.rb.template) (`registry_external_url` line 1192, `registry_http_addr` 127.0.0.1:5000 line 1219, nginx `listen_port` 5050 line 2635), [project feature flag](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/gitlab.yml.example) (`container_registry: true` line 175).

## 9. Understand the SSH surface

Git-over-SSH uses the host's own `sshd` on port 22 by default through gitlab-shell: `ssh_port` defaults to 22, and the Omnibus template documents the same `gitlab_shell_ssh_port = 22`. The optional bundled `gitlab-sshd` is off by default (`gitlab_sshd['enable']` false) and, when enabled, listens on `localhost:2222`. Publish and firewall port 22, and any 2222, deliberately rather than by default. [gitlab-shell SSH port](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/initializers/1_settings.rb) (`ssh_port` 22 line 557), [Omnibus SSH template](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-config-template/gitlab.rb.template) (`gitlab_shell_ssh_port = 22` line 833, `gitlab_sshd['enable']` false line 1654, `gitlab_sshd` listen `localhost:2222` line 1663).

## 10. Keep the webhook SSRF guard, and know the system-hook exception

Webhook and integration SSRF to the local network is fail-closed by default: `allow_local_requests_from_web_hooks_and_services` defaults to false, so a project webhook cannot reach loopback or internal IPs unless an admin widens it. Keep it off. One default is the opposite: admin system hooks may reach the local network, because `allow_local_requests_from_system_hooks` defaults to true. That is an admin-only surface, but note it is the reverse of the web-hook default, so treat system-hook targets with the same care. [Local-request SSRF defaults](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/app/models/application_setting_implementation.rb) (`allow_local_requests_from_system_hooks` true line 47, `allow_local_requests_from_web_hooks_and_services` false line 48).

## 11. Require token expiry and protect the secrets at rest

Personal access tokens require an expiry by default: `require_personal_access_token_expiry` defaults to true. Keep it, scope PATs narrowly, and remember that a token is a machine credential that bypasses 2FA ([machine-auth.md](machine-auth.md)). The instance's encryption secrets live in `/etc/gitlab/gitlab-secrets.json` in Omnibus; the template documents that this file is generated, can be synced between nodes, and can be prevented from regenerating. Its only protection at rest is filesystem permissions, so a leaked secrets file undermines the data it keys, including stored two-factor secrets, CI/CD variables and integration tokens. Protect that file and any backups the same way you protect the database. [PAT expiry default](https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/app/models/application_setting_implementation.rb) (`require_personal_access_token_expiry` true line 372), [secrets file in the Omnibus template](https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-config-template/gitlab.rb.template) (`gitlab-secrets.json` sync note line 2596, generation toggles lines 3189 and 3191).

## Exposure rules

Before GitLab is reachable beyond loopback, every one of these must hold:

- The root password is rotated from the generated value, and in Omnibus `/etc/gitlab/initial_root_password` is read and removed.
- `external_url` is the public origin, and the listener is on loopback or a private address behind a proxy; no plain HTTP is reachable from the network.
- TLS is on, through `external_url https://...` or a TLS-terminating proxy, and HTTP redirects to HTTPS.
- Registration is closed (`signup_enabled` false) unless a public, self-service forge is intended; approval discipline is not relied on alone.
- A second factor is required for every user, or at least for administrators, and the minimum password length is raised above 8.
- Project, group and snippet visibility stay private, and the "internal" level is understood as visible to every signed-in non-external user.
- Every registered runner is unprivileged and isolated, and no runner that can reach secrets or internal networks serves untrusted merge-request pipelines.
- The container registry, if enabled, publishes 5050 deliberately behind the instance's TLS and authentication.
- Git-over-SSH on 22, and any bundled `gitlab-sshd` on 2222, are published and firewalled deliberately.
- The web-hook local-request guard keeps its fail-closed default, and system-hook targets are treated with the same care.
- Personal access tokens keep their required expiry, and `/etc/gitlab/gitlab-secrets.json` and backups are protected like the database.

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

## Sources (checked November 2026)

Repository sources are the GitLab monorepo at tag `v19.5.3-ee` (commit `b9b17a44ffb72a85fca47c5416a40a643c42996f`) and omnibus-gitlab at tag `19.5.3+ce.0` (commit `dbd814101106e4b386c68ca0761603e4ad693a11`); line numbers in the prose above are at those tags. GitLab CE is the FOSS-licensed subset of the `gitlab-org/gitlab` monorepo, and every file cited here is in that core subset, not the `ee/` tree; the clean FOSS mirror `gitlabhq/gitlabhq` lags the `-ee` tag, so the citations use `gitlab-org/gitlab` at `v19.5.3-ee`. Documentation pages under `https://docs.gitlab.com/` are the rolling, reader-facing administrator docs for the same product.

- GitLab root-account production seed, forced random password and console output (v19.5.3-ee): https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/db/fixtures/production/003_admin.rb
- GitLab application settings initializer: host, port, https, signup, signin, SSH port and default visibility (v19.5.3-ee): https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/initializers/1_settings.rb
- GitLab application setting defaults: approval, password policy, two-factor, visibility, SSRF guards and token expiry (v19.5.3-ee): https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/app/models/application_setting_implementation.rb
- GitLab visibility-level constants (v19.5.3-ee): https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/lib/gitlab/visibility_level.rb
- GitLab example application config: host, port, https and the container-registry feature (v19.5.3-ee): https://gitlab.com/gitlab-org/gitlab/-/blob/v19.5.3-ee/config/gitlab.yml.example
- Omnibus GitLab config template: external_url, nginx, TLS, registry, SSH and secrets file (19.5.3+ce.0): https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-config-template/gitlab.rb.template
- Omnibus GitLab attribute defaults: initial root password and registry (19.5.3+ce.0): https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-cookbooks/gitlab/attributes/default.rb
- Omnibus GitLab migration recipe: passing the preset root password through (19.5.3+ce.0): https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-cookbooks/gitlab/recipes/database_migrations.rb
- GitLab Docker install: initial root password file and its deletion (rolling documentation, checked November 2026): https://docs.gitlab.com/install/docker/installation/
- GitLab enforce two-factor authentication for all users (rolling documentation, checked November 2026): https://docs.gitlab.com/security/two_factor_authentication/
- GitLab runners (rolling documentation, checked November 2026): https://docs.gitlab.com/ci/runners/

<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- gitlab: GitLab (v19.5.3)
- gitlab-omnibus: Omnibus GitLab (19.5.3+ce.0)
- gitlab-docs: GitLab documentation (rolling) (unknown)

Claims (full source mapping in the JSON block below):

- root-random (REASONED; gitlab): The root admin is seeded with a forced random password when GITLAB_ROOT_PASSWORD is blank: 003_admin.rb skips creation if an admin exists, builds admin: true, sets password_automatically_set and force_random_password, and prints a first-visit prompt.
- root-preset (REASONED; gitlab): A preset root password is used verbatim only when GITLAB_ROOT_PASSWORD is set, and it is echoed to the console only when display_initial_root_password is true; otherwise the console shows a masked value.
- root-omnibus-file (REASONED; gitlab-omnibus, gitlab-docs): In Omnibus the generated password is written to /etc/gitlab/initial_root_password; the attribute defaults are nil, display false and store false, the template documents the store toggle and path, the recipe passes a preset through, and docs say the file is deleted after 24 hours.
- net-host-http (REASONED; gitlab): The default application listener is plain HTTP on port 80 with host localhost: host defaults to localhost, https to false and port to 443-or-80, and gitlab.yml.example ships host localhost, port 80 and https false.
- net-external-url (REASONED; gitlab-omnibus): Omnibus derives every public URL, the nginx scheme and listen ports from a single external_url; nginx listen_port and listen_https default nil and follow the scheme, and redirect_http_to_https defaults false, so external_url http serves the UI, git and API in clear text on 80.
- net-tls (REASONED; gitlab-omnibus, gitlab-docs): TLS is opt-in: external_url https makes bundled nginx terminate with Let's Encrypt or ssl_certificate and ssl_certificate_key, or terminate at a proxy; until then the UI, git-over-HTTP and API cross the wire in clear text.
- signup-open (REASONED; gitlab): Self-service signup is on by default: signup_enabled defaults to true in the initializer and is surfaced as the admin setting of the same name.
- signup-approval (REASONED; gitlab): New signups are held for admin approval by default: require_admin_approval_after_user_signup defaults to true, so a self-registered account is inactive until approved; for a private forge set signup_enabled false rather than relying on approval.
- signin-password (REASONED; gitlab): Password sign-in is on by default: signin_enabled defaults to true, and password_authentication_enabled_for_git is true with password_authentication_enabled_for_web following signin_enabled.
- mfa-off (REASONED; gitlab, gitlab-docs): There is no instance-wide second-factor requirement by default: require_two_factor_authentication defaults false and two_factor_grace_period is 48 hours; enforcement is available on all tiers from the admin settings.
- password-length (REASONED; gitlab): The minimum password length default is 8: DEFAULT_MINIMUM_PASSWORD_LENGTH is 8 and minimum_password_length uses it; raise it.
- visibility-private (REASONED; gitlab): Default project, group and snippet visibility is private: all three defaults resolve to default_projects_features visibility, which the initializer sets to PRIVATE, where PRIVATE is 0, INTERNAL 10 and PUBLIC 20; internal admits every signed-in non-external user.
- ci-rce (REASONED; gitlab-docs): A registered runner executing a pipeline runs the project's .gitlab-ci.yml as arbitrary code on the runner host; runners are operator-registered, so an exposed instance becomes code execution once a runner is attached and a pipeline can be triggered.
- registry-off (REASONED; gitlab-omnibus, gitlab): The bundled container registry is off by default: registry_enabled defaults false; it is enabled by configuring registry_external_url, and when on its nginx vhost listens on 5050 with the registry process on loopback 127.0.0.1:5000; the project feature flag gates the UI, not the service.
- ssh-22 (REASONED; gitlab, gitlab-omnibus): Git-over-SSH uses the host sshd on port 22 via gitlab-shell by default (ssh_port 22), and the optional bundled gitlab-sshd is off by default and listens on localhost:2222 when enabled.
- ssrf-webhooks (REASONED; gitlab): Webhook and integration SSRF to the local network is fail-closed by default: allow_local_requests_from_web_hooks_and_services defaults false, so a webhook cannot reach loopback or internal IPs unless an admin widens it.
- ssrf-system-hooks (REASONED; gitlab): Admin system hooks may reach the local network by default: allow_local_requests_from_system_hooks defaults true, the opposite of the web-hook default; it is admin-only but worth the same care.
- pat-expiry (REASONED; gitlab): Personal access tokens require an expiry by default: require_personal_access_token_expiry defaults true; scope PATs narrowly, since a token bypasses 2FA.
- secrets-at-rest (REASONED; gitlab-omnibus): The instance encryption secrets live in /etc/gitlab/gitlab-secrets.json in Omnibus; the template documents that it is generated and can be synced, its only at-rest protection is filesystem permissions, and a leak undermines the data it keys.
- verify-listeners (REASONED; gitlab, gitlab-omnibus): ss inventories local binds in this namespace only; expect nginx on 80 or 443, SSH on 22 and, with the registry on, 5050, and treat a wildcard bind on any as all-interfaces exposure; a failed inventory proves no absence.
- verify-tls (REASONED; gitlab): The probe fetches /users/sign_in over HTTPS with certificate validation on, so a completed fetch showing the new_user sign-in form confirms the application and TLS, while a nonzero exit means the handshake or connection failed and the result is inconclusive.
- verify-anon (REASONED; gitlab): By default GitLab serves /explore/projects to anonymous callers with 200, listing only public projects; with default-private visibility that list is empty, so any project shown is public, and a redirect to /users/sign_in means anonymous browsing is restricted.
- verify-rootfile (REASONED; gitlab-omnibus, gitlab-docs): On Omnibus the generated root password is written to /etc/gitlab/initial_root_password and deleted after 24 hours, so a present file means the generated password was probably not rotated; absence does not prove rotation, and a failed docker exec is not a result.

````json
{
  "schema": 1,
  "checked": "2026-11-10",
  "documentation_checked": "2026-11",
  "body_sha256": "70975cd91d6e590208ea35dca514c61d8612705c6d4b8dc5c3d9fbad82f006ff",
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
        "sf630c13816a7": "https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/19.5.3+ce.0/files/gitlab-cookbooks/gitlab/recipes/database_migrations.rb"
      }
    },
    "gitlab-docs": {
      "name": "GitLab documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s3b7ac561a92e": "https://docs.gitlab.com/install/docker/installation/",
        "s0347014ce554": "https://docs.gitlab.com/security/two_factor_authentication/",
        "s050e2202cf3c": "https://docs.gitlab.com/ci/runners/"
      }
    }
  },
  "claims": {
    "root-random": {"text": "The root admin is seeded with a forced random password when GITLAB_ROOT_PASSWORD is blank: 003_admin.rb skips creation if an admin exists, builds admin: true, sets password_automatically_set and force_random_password, and prints a first-visit prompt.", "components": ["gitlab"], "sources": ["gitlab:sfb8995e04c56"], "status": "REASONED"},
    "root-preset": {"text": "A preset root password is used verbatim only when GITLAB_ROOT_PASSWORD is set, and it is echoed to the console only when display_initial_root_password is true; otherwise the console shows a masked value.", "components": ["gitlab"], "sources": ["gitlab:sfb8995e04c56"], "status": "REASONED"},
    "root-omnibus-file": {"text": "In Omnibus the generated password is written to /etc/gitlab/initial_root_password; the attribute defaults are nil, display false and store false, the template documents the store toggle and path, the recipe passes a preset through, and docs say the file is deleted after 24 hours.", "components": ["gitlab-omnibus", "gitlab-docs"], "sources": ["gitlab-omnibus:s01015d478714", "gitlab-omnibus:sd8e89739412c", "gitlab-omnibus:sf630c13816a7", "gitlab-docs:s3b7ac561a92e"], "status": "REASONED"},
    "net-host-http": {"text": "The default application listener is plain HTTP on port 80 with host localhost: host defaults to localhost, https to false and port to 443-or-80, and gitlab.yml.example ships host localhost, port 80 and https false.", "components": ["gitlab"], "sources": ["gitlab:s89baa0ac55a5", "gitlab:s975cf7efc7d9"], "status": "REASONED"},
    "net-external-url": {"text": "Omnibus derives every public URL, the nginx scheme and listen ports from a single external_url; nginx listen_port and listen_https default nil and follow the scheme, and redirect_http_to_https defaults false, so external_url http serves the UI, git and API in clear text on 80.", "components": ["gitlab-omnibus"], "sources": ["gitlab-omnibus:sd8e89739412c"], "status": "REASONED"},
    "net-tls": {"text": "TLS is opt-in: external_url https makes bundled nginx terminate with Let's Encrypt or ssl_certificate and ssl_certificate_key, or terminate at a proxy; until then the UI, git-over-HTTP and API cross the wire in clear text.", "components": ["gitlab-omnibus", "gitlab-docs"], "sources": ["gitlab-omnibus:sd8e89739412c", "gitlab-docs:s3b7ac561a92e"], "status": "REASONED"},
    "signup-open": {"text": "Self-service signup is on by default: signup_enabled defaults to true in the initializer and is surfaced as the admin setting of the same name.", "components": ["gitlab"], "sources": ["gitlab:s89baa0ac55a5", "gitlab:s39a414417912"], "status": "REASONED"},
    "signup-approval": {"text": "New signups are held for admin approval by default: require_admin_approval_after_user_signup defaults to true, so a self-registered account is inactive until approved; for a private forge set signup_enabled false rather than relying on approval.", "components": ["gitlab"], "sources": ["gitlab:s39a414417912"], "status": "REASONED"},
    "signin-password": {"text": "Password sign-in is on by default: signin_enabled defaults to true, and password_authentication_enabled_for_git is true with password_authentication_enabled_for_web following signin_enabled.", "components": ["gitlab"], "sources": ["gitlab:s89baa0ac55a5", "gitlab:s39a414417912"], "status": "REASONED"},
    "mfa-off": {"text": "There is no instance-wide second-factor requirement by default: require_two_factor_authentication defaults false and two_factor_grace_period is 48 hours; enforcement is available on all tiers from the admin settings.", "components": ["gitlab", "gitlab-docs"], "sources": ["gitlab:s39a414417912", "gitlab-docs:s0347014ce554"], "status": "REASONED"},
    "password-length": {"text": "The minimum password length default is 8: DEFAULT_MINIMUM_PASSWORD_LENGTH is 8 and minimum_password_length uses it; raise it.", "components": ["gitlab"], "sources": ["gitlab:s39a414417912"], "status": "REASONED"},
    "visibility-private": {"text": "Default project, group and snippet visibility is private: all three defaults resolve to default_projects_features visibility, which the initializer sets to PRIVATE, where PRIVATE is 0, INTERNAL 10 and PUBLIC 20; internal admits every signed-in non-external user.", "components": ["gitlab"], "sources": ["gitlab:s39a414417912", "gitlab:s89baa0ac55a5", "gitlab:sfa55e9a8e36b"], "status": "REASONED"},
    "ci-rce": {"text": "A registered runner executing a pipeline runs the project's .gitlab-ci.yml as arbitrary code on the runner host; runners are operator-registered, so an exposed instance becomes code execution once a runner is attached and a pipeline can be triggered.", "components": ["gitlab-docs"], "sources": ["gitlab-docs:s050e2202cf3c"], "status": "REASONED"},
    "registry-off": {"text": "The bundled container registry is off by default: registry_enabled defaults false; it is enabled by configuring registry_external_url, and when on its nginx vhost listens on 5050 with the registry process on loopback 127.0.0.1:5000; the project feature flag gates the UI, not the service.", "components": ["gitlab-omnibus", "gitlab"], "sources": ["gitlab-omnibus:s01015d478714", "gitlab-omnibus:sd8e89739412c", "gitlab:s975cf7efc7d9"], "status": "REASONED"},
    "ssh-22": {"text": "Git-over-SSH uses the host sshd on port 22 via gitlab-shell by default (ssh_port 22), and the optional bundled gitlab-sshd is off by default and listens on localhost:2222 when enabled.", "components": ["gitlab", "gitlab-omnibus"], "sources": ["gitlab:s89baa0ac55a5", "gitlab-omnibus:sd8e89739412c"], "status": "REASONED"},
    "ssrf-webhooks": {"text": "Webhook and integration SSRF to the local network is fail-closed by default: allow_local_requests_from_web_hooks_and_services defaults false, so a webhook cannot reach loopback or internal IPs unless an admin widens it.", "components": ["gitlab"], "sources": ["gitlab:s39a414417912"], "status": "REASONED"},
    "ssrf-system-hooks": {"text": "Admin system hooks may reach the local network by default: allow_local_requests_from_system_hooks defaults true, the opposite of the web-hook default; it is admin-only but worth the same care.", "components": ["gitlab"], "sources": ["gitlab:s39a414417912"], "status": "REASONED"},
    "pat-expiry": {"text": "Personal access tokens require an expiry by default: require_personal_access_token_expiry defaults true; scope PATs narrowly, since a token bypasses 2FA.", "components": ["gitlab"], "sources": ["gitlab:s39a414417912"], "status": "REASONED"},
    "secrets-at-rest": {"text": "The instance encryption secrets live in /etc/gitlab/gitlab-secrets.json in Omnibus; the template documents that it is generated and can be synced, its only at-rest protection is filesystem permissions, and a leak undermines the data it keys.", "components": ["gitlab-omnibus"], "sources": ["gitlab-omnibus:sd8e89739412c"], "status": "REASONED"},
    "verify-listeners": {"text": "ss inventories local binds in this namespace only; expect nginx on 80 or 443, SSH on 22 and, with the registry on, 5050, and treat a wildcard bind on any as all-interfaces exposure; a failed inventory proves no absence.", "components": ["gitlab", "gitlab-omnibus"], "sources": ["gitlab:s89baa0ac55a5", "gitlab-omnibus:sd8e89739412c"], "status": "REASONED", "verify": [1]},
    "verify-tls": {"text": "The probe fetches /users/sign_in over HTTPS with certificate validation on, so a completed fetch showing the new_user sign-in form confirms the application and TLS, while a nonzero exit means the handshake or connection failed and the result is inconclusive.", "components": ["gitlab"], "sources": ["gitlab:s89baa0ac55a5"], "status": "REASONED", "verify": [2]},
    "verify-anon": {"text": "By default GitLab serves /explore/projects to anonymous callers with 200, listing only public projects; with default-private visibility that list is empty, so any project shown is public, and a redirect to /users/sign_in means anonymous browsing is restricted.", "components": ["gitlab"], "sources": ["gitlab:sfa55e9a8e36b"], "status": "REASONED", "verify": [3]},
    "verify-rootfile": {"text": "On Omnibus the generated root password is written to /etc/gitlab/initial_root_password and deleted after 24 hours, so a present file means the generated password was probably not rotated; absence does not prove rotation, and a failed docker exec is not a result.", "components": ["gitlab-omnibus", "gitlab-docs"], "sources": ["gitlab-omnibus:sd8e89739412c", "gitlab-docs:s3b7ac561a92e"], "status": "REASONED", "verify": [4]}
  }
}
````
<!-- version-basis:end -->
