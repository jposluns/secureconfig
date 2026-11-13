# Forgejo: locking the installer, binding, TLS, authentication, and the Actions runner surface

Forgejo is a self-hosted Git forge, a community hard fork of Gitea. It serves repositories over HTTP and SSH, runs a package and container registry, and can run CI through Forgejo Actions. This guide helps your AI assistant check that a deployment is configured securely: lock the first-run installer before the port is reachable, bind privately and front it with TLS, close open registration, require a second factor, and treat any Actions runner as a code-execution host.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/forgejo.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against Forgejo v17.0.1; 1 further source carries no recorded version. Metadata reviewed 2026-11-10; documentation checked November 2026. The guide records 32 claims, all reasoned from cited sources and any earlier-form run, not a live demonstration of the shipped form.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

An exposed Forgejo whose first-run installer is still unlocked is an instant, unauthenticated admin takeover. `INSTALL_LOCK` defaults to `false`, and while it is false the whole web server serves only the installer at `/`. A single unauthenticated `POST /` then creates an `IsAdmin: true` account with an attacker-chosen password, writes `SECRET_KEY`, `INTERNAL_TOKEN` and the OAuth2 `JWT_SECRET` into `app.ini`, flips `INSTALL_LOCK` to true, and logs the caller in as that admin. From admin, Forgejo Actions plus an attacker-registered runner is code execution on the runner host. So reaching an un-installed Forgejo means owning the forge; reaching an installed one makes the fight authentication, registration, and the Actions and runner surface. The default listener binds `0.0.0.0:3000` as plain HTTP with `DOMAIN` `localhost`, so this guide pins Forgejo v17.0.1 and reads every default from source. The configuration file is `app.ini` (INI sections such as `[server]` and `[security]`), and the default web port is `3000`. [Server bind, port and protocol defaults](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/server.go) (`HTTP_ADDR` `0.0.0.0`, `HTTP_PORT` `3000`, `Protocol` HTTP and `DOMAIN` `localhost`, lines 150-154), [configuration cheat sheet](https://forgejo.org/docs/latest/admin/config-cheat-sheet/).

## 1. Lock the installer first, and never expose an un-installed Forgejo

`INSTALL_LOCK` defaults to `false`, both in code and in the shipped example configuration. `HasInstallLock` returns `Section("security").Key("INSTALL_LOCK").MustBool(false)`, and `app.example.ini` carries `INSTALL_LOCK = false`. Set it to `true` only after you have completed the install over a private channel. In `app.ini`:

```ini
[security]
INSTALL_LOCK = true
```

While `InstallLock` is false the process runs the installer, not the application. `cmd/web.go` calls `serveInstall` whenever `!setting.InstallLock`, and `install.Routes()` mounts `GET /` to the install form and `POST /` to `SubmitInstall` at the site root. That unauthenticated `POST /` builds a `&user_model.User{..., IsAdmin: true}` and calls `CreateUser`, so the first caller to reach an unlocked installer becomes a site administrator with a password of their choosing. The same request writes `security.INSTALL_LOCK=true`, generates an `INTERNAL_TOKEN`, an OAuth2 `JWT_SECRET` and a `SECRET_KEY` when each is unset, and saves them to `app.ini`, then sets a long-term-auth cookie and the session `uid` so the caller leaves the request logged in as the new admin. Complete the install over a loopback bind or an SSH tunnel such as `ssh -N -L 3000:127.0.0.1:3000 REPLACE_WITH_USER@REPLACE_WITH_HOST`, confirm `INSTALL_LOCK = true`, and only then open the port. [Install-lock default](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/setting.go) (`HasInstallLock`, lines 248-249), [install-lock load](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/security.go) (`InstallLock = HasInstallLock(rootCfg)`, line 435), [example config](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/custom/conf/app.example.ini) (`INSTALL_LOCK = false`, line 450). [serveInstall gate](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/cmd/web.go) (`if !setting.InstallLock`, lines 258-261; `install.Routes()`, line 149), [install routes](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/routers/install/routes.go) (`GET /` and `POST /`, lines 25-28), [install handler](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/routers/install/install.go) (`IsAdmin: true` and `CreateUser`, lines 548-560; `INSTALL_LOCK`, token and secret writes, lines 482 and 486-506 and 527; auto-login, lines 571-585).

## 2. Set a strong `SECRET_KEY`, and never ship the fallback key

If `SECRET_KEY` is unset, Forgejo does not fail. It falls back to a hardcoded literal `"!#@FDEWREWR&*("`, and a source comment states the default must not move off the widely used value. A deployment that never ran the installer, or never set the key, therefore runs on a world-known key. `SECRET_KEY` is the data-encryption key: the loader calls `keying.Init([]byte(SecretKey))`, and TOTP two-factor secrets are stored encrypted under it through `keying.TOTP.Encrypt(...)` in `SetSecret`. A default or leaked `SECRET_KEY` means those 2FA secrets, and other keyed data, are decryptable. Let the installer generate the key, or set a long random value yourself, in `app.ini`:

```ini
[security]
SECRET_KEY = REPLACE_WITH_A_LONG_RANDOM_VALUE
INTERNAL_TOKEN = REPLACE_WITH_A_GENERATED_TOKEN
```

`SECRET_KEY`, `INTERNAL_TOKEN` and the OAuth2 `JWT_SECRET` live as plaintext in `app.ini`; their only protection at rest is filesystem permissions, because the installer writes them with `SetValue` and `SaveTo` and there is no secret-manager integration. Keep `app.ini` off shared storage and readable only by the run account. By contrast, API access tokens are not stored in the clear: a token row keeps a sha256 `TokenHash`, a `TokenSalt` and a `TokenLastEight`, and the lookup compares hashes in constant time. [Secret-key fallback](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/security.go) (hardcoded `"!#@FDEWREWR&*("`, lines 437-441; `keying.Init`, line 443), [TOTP secret encryption](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/models/auth/twofactor.go) (`SetSecret` uses `keying.TOTP.Encrypt`, lines 89-90), [plaintext secret writes](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/routers/install/install.go) (secret `SetValue` and `SaveTo`, lines 482 and 486-506 and 527), [access-token hashing](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/models/auth/access_token.go) (`TokenHash`, `TokenSalt`, `TokenLastEight`, lines 67-69; generation, lines 108-113; constant-time compare, lines 188-189).

## 3. Bind privately, set `ROOT_URL`, and declare trusted proxies

The default listener binds every interface on port 3000 as plain HTTP, with `DOMAIN` `localhost`. Bind Forgejo to a private address, or keep it on loopback and front it with a reverse proxy. In `app.ini`:

```ini
[server]
HTTP_ADDR = 127.0.0.1
HTTP_PORT = 3000
ROOT_URL  = https://forge.example.com/
```

`ROOT_URL` defaults to `<proto>://<domain>:<port>`, for example `http://localhost:3000/`, and it drives absolute links, cookie scope and OAuth redirect URLs, so a wrong `ROOT_URL` behind a proxy breaks or weakens all three; set it to the public origin. When a proxy terminates the connection, declare it: `REVERSE_PROXY_TRUSTED_PROXIES` defaults to `127.0.0.0/8, ::1/128` and `REVERSE_PROXY_LIMIT` to 1, and header authentication through `ENABLE_REVERSE_PROXY_AUTHENTICATION` (header `X-WEBAUTH-USER`) is off by default. Do not enable header authentication unless the proxy is the sole network path and strips that header from client requests, because any party that can reach the port with the header set would be trusted as the named user. [Bind, port and ROOT_URL defaults](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/server.go) (`HTTP_ADDR`, `HTTP_PORT`, `DOMAIN`, lines 150-154; `ROOT_URL` default, lines 258-259), [trusted-proxy defaults](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/security.go) (`X-WEBAUTH-USER`, `REVERSE_PROXY_LIMIT` 1, trusted proxies `127.0.0.0/8, ::1/128`, lines 448-457), [reverse-proxy auth off](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/service.go) (`ENABLE_REVERSE_PROXY_AUTHENTICATION` default false, line 217).

## 4. Enable TLS

Native HTTPS exists but is opt-in. TLS is active only when `PROTOCOL=https`, which then uses `CERT_FILE` and `KEY_FILE` or the built-in ACME client; the default `PROTOCOL` is `http`, so an out-of-the-box Forgejo serves plain HTTP on port 3000. Enable native TLS, or terminate TLS at a reverse proxy in front of a loopback-bound Forgejo. In `app.ini`:

```ini
[server]
PROTOCOL  = https
CERT_FILE = /etc/forgejo/tls/cert.pem
KEY_FILE  = /etc/forgejo/tls/key.pem
```

Without TLS, a non-loopback bind sends session cookies and Basic-auth git credentials in clear text to any on-path observer, so treat TLS as mandatory before the port is reachable beyond loopback. The same port carries the web UI, the HTTP git transport and the API, so this one setting (or one terminating proxy) covers every HTTP surface. [TLS protocol gate](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/server.go) (HTTPS only when `PROTOCOL=https`, with `CERT_FILE`/`KEY_FILE` or ACME, lines 154-206), [example protocol default](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/custom/conf/app.example.ini) (`PROTOCOL` defaults to `http`, line 71).

## 5. Close registration and require sign-in to view

Open registration is on by default: `DISABLE_REGISTRATION` resolves through `MustBool()` to `false`, so anyone who can reach the instance can self-register. The instance is also browsable without a login by default, because `REQUIRE_SIGNIN_VIEW` resolves to `false`. Unless you intend a public, self-service forge, close both, or scope them deliberately. In `app.ini`:

```ini
[service]
DISABLE_REGISTRATION = true
REQUIRE_SIGNIN_VIEW  = true
```

Closing registration leaves admin-created accounts and any configured OAuth or LDAP source as the ways in; requiring sign-in to view keeps anonymous visitors off repository, user and organization pages. [Open registration default](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/service.go) (`DISABLE_REGISTRATION` `MustBool()`, line 171; `REQUIRE_SIGNIN_VIEW` `MustBool()`, line 215), [example registration defaults](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/custom/conf/app.example.ini) (`DISABLE_REGISTRATION = false`, line 784; `REQUIRE_SIGNIN_VIEW = false`, line 793).

## 6. Require a second factor and raise the password policy

There is no global second-factor requirement by default. `GLOBAL_TWO_FACTOR_REQUIREMENT` is empty, which resolves to `NoneTwoFactorRequirement`, `ENABLE_CAPTCHA` is false, `MIN_PASSWORD_LENGTH` is 8, `PASSWORD_COMPLEXITY` defaults to `off`, and `PASSWORD_CHECK_PWN` is false. Require 2FA for everyone, or at least for admins, and strengthen the password rules. In `app.ini`:

```ini
[security]
GLOBAL_TWO_FACTOR_REQUIREMENT = all
MIN_PASSWORD_LENGTH           = 12
PASSWORD_COMPLEXITY           = lower,upper,digit,spec
PASSWORD_CHECK_PWN            = true
```

A value of `admin` requires 2FA only for administrators; `all` requires it for every account. Forgejo supports TOTP and WebAuthn security keys as second factors, so pair the requirement with keys where you can. [Two-factor and password defaults](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/security.go) (`GLOBAL_TWO_FACTOR_REQUIREMENT` resolves to none, line 445; `MIN_PASSWORD_LENGTH` 8, line 459; `PASSWORD_CHECK_PWN` false, line 472; `PASSWORD_COMPLEXITY` defaults `off`, lines 482-491), [captcha off](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/service.go) (`ENABLE_CAPTCHA` default false, line 222).

## 7. Control repository and user visibility defaults

New accounts and repositories lean public. `DEFAULT_USER_VISIBILITY` resolves to the first allowed mode, which is `public`, `DEFAULT_KEEP_EMAIL_PRIVATE` is false, `DEFAULT_PRIVATE` is `last` with `FORCE_PRIVATE` false, and the HTTP git transport is enabled because `DISABLE_HTTP_GIT` is false. Decide these deliberately rather than inheriting them. In `app.ini`:

```ini
[service]
DEFAULT_USER_VISIBILITY    = limited
DEFAULT_KEEP_EMAIL_PRIVATE = true

[repository]
DEFAULT_PRIVATE = private
FORCE_PRIVATE   = true
```

`FORCE_PRIVATE = true` stops anyone making a repository public, and `DEFAULT_PRIVATE = private` makes new repositories private unless changed. Keep email addresses private to avoid leaking them in commit metadata on public pages. [User-visibility default](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/service.go) (`DEFAULT_KEEP_EMAIL_PRIVATE`, line 237; `DEFAULT_USER_VISIBILITY` resolves to the first allowed mode `public`, lines 270-276), [repository defaults](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/repository.go) (`ForcePrivate` false and `DefaultPrivate` last, lines 165-166; `DisableHTTPGit` false, line 170).

## 8. Govern Forgejo Actions: treat every runner as a code-execution host

Forgejo Actions is globally enabled by default: the `Actions` settings struct initializes `Enabled: true`. Enabled is not the same as executing, though. No runner ships or auto-registers, so no workflow runs until an operator installs an `act_runner` and registers it with a registration token from the admin, organization or repository settings. The security point is what a registered runner is: a runner executing a workflow runs arbitrary code from that workflow on the runner host or container, not on the Forgejo host. If you do not use Actions, disable it; if you do, isolate runners and never attach a privileged runner to repositories that accept contributions from untrusted accounts. In `app.ini`:

```ini
[actions]
ENABLED = false
```

Where Actions is used, run each runner as a dedicated, unprivileged account or in a throwaway container, scope its registration to the smallest trust boundary that needs it, and keep untrusted pull-request workflows off any runner that can reach secrets or internal networks. [Actions enabled by default](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/actions.go) (`Enabled: true`, line 33; `DefaultActionsURL` `defaultActionsURLForgejo`, line 35; the URL literal `https://data.forgejo.org`, line 57), [Forgejo Actions administrator guide](https://forgejo.org/docs/latest/admin/actions/).

## 9. Understand the SSH surface

SSH access to repositories is enabled, but the built-in SSH server is off by default: `DISABLE_SSH` is false and `START_SSH_SERVER` is false, so Forgejo uses the host's own `sshd` and an `authorized_keys` file unless you turn the built-in server on. When the built-in server is enabled, `SSH_PORT` and `SSH_LISTEN_PORT` default to 22. By default Forgejo manages the run account's `~/.ssh/authorized_keys` through a forced command, because `SSH_CREATE_AUTHORIZED_KEYS_FILE` is true, and the push path is hardened by `DISABLE_GIT_HOOKS` true and `ONLY_ALLOW_PUSH_IF_GITEA_ENVIRONMENT_SET` true. Keep those two push-path defaults, and bind the built-in server privately if you enable it. The official rootless container image is different: its setup script defaults `SSH_PORT` and `SSH_LISTEN_PORT` to 2222, so the in-container SSH server listens on 2222. Publish and firewall that port deliberately rather than by default. [SSH defaults](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/ssh.go) (`Disabled` false and `StartBuiltinServer` false, lines 55-56; `SSH_PORT`/`SSH_LISTEN_PORT` 22, lines 139-140; `SSH_CREATE_AUTHORIZED_KEYS_FILE` true, line 178), [example built-in-server default](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/custom/conf/app.example.ini) (`START_SSH_SERVER = false`, line 146). [push-path hardening](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/security.go) (`DISABLE_GIT_HOOKS` true, line 461; `ONLY_ALLOW_PUSH_IF_GITEA_ENVIRONMENT_SET` true, line 463), [rootless container SSH port](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/docker/rootless/usr/local/bin/docker-setup.sh) (`SSH_PORT` and `SSH_LISTEN_PORT` default `2222`, lines 36-37).

## 10. Keep the webhook and migration SSRF guards at their fail-closed defaults

Two surfaces that are often open elsewhere are fail-closed here, and the honest guidance is to leave them that way. Webhook delivery is not an open server-side request forgery by default: when `webhook.ALLOWED_HOST_LIST` is empty it is set to the built-in `external` matcher, which excludes loopback (127.0.0.0/8, ::1) and private and LAN ranges (RFC 1918, RFC 4193 and RFC 6598), and `SKIP_TLS_VERIFY` is false, so a webhook cannot reach localhost or internal IPs unless an admin widens the list. Repository migration and mirroring are fail-closed too: `migrations.ALLOW_LOCALNETWORKS` defaults false, `SKIP_TLS_VERIFY` false and `ALLOW_UNENCRYPTED` false, and local-path import through `IMPORT_LOCAL_PATHS` defaults false. Do not widen `ALLOWED_HOST_LIST` or set `ALLOW_LOCALNETWORKS = true` without a specific reason, because either turns a safe default into an SSRF path into your own network. [Webhook allow-list default](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/services/webhook/deliver.go) (empty list becomes the built-in `external` matcher, lines 205-209), [built-in matcher ranges](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/hostmatcher/hostmatcher.go) (external excludes loopback and private and LAN ranges, lines 26-33), [migration SSRF defaults](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/migrations.go) (`ALLOW_LOCALNETWORKS`, `SKIP_TLS_VERIFY`, `ALLOW_UNENCRYPTED` all false, lines 32-36), [local-path import default](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/security.go) (`IMPORT_LOCAL_PATHS` false, line 460).

## 11. Run with least privilege, and know the registry surfaces

Run Forgejo under a dedicated, unprivileged operating-system account, protect `app.ini` and the data directory, and remember which registry surfaces are on by default. The package and container registry is enabled by default: `Packages.Enabled` is true and its `RegistryHost` is the `ROOT_URL` host, and it authenticates with the same user tokens, so its exposure rides the instance's authentication and registration posture. The Git LFS server is off by default, because `LFS_START_SERVER` is false; when it is enabled it authenticates with short-lived tokens whose `LFS_HTTP_AUTH_EXPIRY` defaults to 24 hours. The OAuth2 provider is enabled by default, since `OAuth2.Enabled` is true, and a leaked `JWT_SECRET`, which sits in plaintext in `app.ini`, undermines every OAuth2 token the instance has issued. Protect the data directory and any backups the same way as `app.ini`, since they carry repository contents and the state database. [Package registry on](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/packages.go) (`Enabled: true`, line 48; `RegistryHost` is the ROOT_URL host, line 70), [LFS server off](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/lfs.go) (`LFS_HTTP_AUTH_EXPIRY` 24h, line 74; `StartServer` gate, line 79), [example LFS default](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/custom/conf/app.example.ini) (`LFS_START_SERVER = false`, line 323), [OAuth2 provider on](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/oauth2.go) (`Enabled: true`, lines 97-110), [JWT secret write](https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/routers/install/install.go) (`JWT_SECRET` generated into `app.ini`, lines 496-500).

## Exposure rules

Before Forgejo is reachable beyond loopback, every one of these must hold:

- `INSTALL_LOCK = true`, confirmed after a completed install over a private channel; never open the port to an un-installed instance.
- `SECRET_KEY` and `INTERNAL_TOKEN` are strong and not the fallback, and `app.ini` is readable only by the run account.
- The listener is on a private address or loopback (`HTTP_ADDR`), `ROOT_URL` is the public origin, and trusted proxies are declared.
- TLS is on (`PROTOCOL = https`) or a TLS-terminating proxy is in front; no plain HTTP is reachable from the network.
- Registration is closed (`DISABLE_REGISTRATION = true`) and anonymous viewing is off (`REQUIRE_SIGNIN_VIEW = true`), unless a public forge is intended.
- A second factor is required (`GLOBAL_TWO_FACTOR_REQUIREMENT` is `all` or `admin`) and the password policy is raised.
- Repository and user visibility defaults are set deliberately (`FORCE_PRIVATE`, `DEFAULT_PRIVATE`, `DEFAULT_USER_VISIBILITY`).
- Actions is disabled if unused; otherwise every runner is unprivileged and isolated, and no privileged runner serves untrusted contributors.
- The built-in SSH server, if enabled, is bound privately, and the container's 2222 publication is deliberate and firewalled.
- The webhook and migration SSRF guards keep their fail-closed defaults; `ALLOWED_HOST_LIST` and `ALLOW_LOCALNETWORKS` are not widened without reason.
- Forgejo runs as a dedicated non-root account, and the data directory and backups are protected like `app.ini`.

## Verify

REASONED: Verification preparation. A live Forgejo stand-up opens a listener and, with an unlocked installer, would accept an unauthenticated admin-takeover POST; the authoring host forbids opening listeners without an isolated network namespace, and none was available. No Forgejo instance, container runtime or test deployment was exercised here, so every outcome below is REASONED from the cited source and documentation, not demonstrated. The guarded Bash blocks were written to pass `bash -n` and ShellCheck cleanly and to refuse on unsubstituted placeholders before they reach `curl`; the repository gate suite's `bash -n` and ShellCheck passes cover them. Service behaviour is REASONED, not demonstrated. Run each exposed-versus-fixed comparison only against an isolated test deployment you control, never by weakening production, and keep versions, paths and credentials constant while changing the control under test. A rejection counts only when the positive control succeeds.

### Inventory the listener and confirm the bind

REASONED: No Forgejo instance runs here. `ss` inventories local binds in this namespace only, not firewall or NAT, and a failed netlink inventory proves no absence. Expect Forgejo on `127.0.0.1:3000` when `HTTP_ADDR` is loopback, and treat a `0.0.0.0:3000` or `[::]:3000` listener as exposed to every interface, which is the shipped default. Confirm the actual external entry point separately.

```bash
# REASONED: no Forgejo instance runs in the authoring environment; local listener inventory only.
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
  match=$(printf '%s\n' "$listeners" | grep -E '[:.]3000([[:space:]]|$)')
  if [ -z "$match" ]; then
    echo "no listener on port 3000 in this namespace; Forgejo may be elsewhere, not running, or on another port"
    exit 0
  fi
  printf '%s\n' "$match"
  if printf '%s\n' "$match" | grep -Eq '0\.0\.0\.0:3000|\[::\]:3000'; then
    echo "FINDING (REASONED): Forgejo is bound to all interfaces; set HTTP_ADDR to a private address or front it with a proxy unless this exposure is intended"
  elif printf '%s\n' "$match" | grep -Eq '127\.0\.0\.1:3000|\[::1\]:3000'; then
    echo "expected fixed result: Forgejo is bound to loopback"
  else
    echo "a non-loopback host is bound; judge whether that interface is intended"
  fi
)
```

### Confirm the installer is locked and TLS is on

REASONED: No Forgejo instance runs here. An un-installed Forgejo serves the installer form at `/`, whose markup carries the installer-only `name="db_type"` field, and a single unauthenticated `POST /` would create a site admin; a locked instance serves the application instead. The probe fetches `/` over HTTPS, which also confirms TLS, and refuses placeholders before it calls `curl`; it sends no credential. Paste the whole block and substitute the two values inside the single quotes.

```bash
# REASONED: no Forgejo instance runs in the authoring environment; unauthenticated GET only, no POST.
(
  set +x
  set +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_FORGEJO_BASE_URL' 'REPLACE_WITH_CA_BUNDLE'
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
        "$base/") ;;
  esac
  printf '%s\n' "$body" | tail -n 1
  if printf '%s\n' "$body" | grep -q 'name="db_type"'; then
    echo "FINDING (REASONED): the installer is being served at / (INSTALL_LOCK is false); an unauthenticated POST / would create a site admin. Lock install before exposing"
  else
    echo "expected fixed result: the application is served, not the installer (INSTALL_LOCK is true); TLS succeeded because the HTTPS fetch returned a status above"
  fi
  echo "REASONED expectation: exposed answers the installer form (FINDING); fixed answers the app; exit!=0 in the status line means TLS or the connection failed (inconclusive)."
)
```

### Confirm anonymous browsing is blocked

REASONED: No Forgejo instance runs here. With `REQUIRE_SIGNIN_VIEW` true, an anonymous request to a browse page such as `/explore/repos` is redirected to `/user/login` with `303 See Other`; with it false, the page returns `200` to anonymous callers. The probe does not follow redirects, so the status code alone discriminates. Paste the whole block and substitute the two values inside the single quotes.

```bash
# REASONED: no Forgejo instance runs in the authoring environment; unauthenticated GET only.
(
  set +x
  set +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_FORGEJO_BASE_URL' 'REPLACE_WITH_CA_BUNDLE'
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
        -w 'anonymous /explore/repos -> http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "$base/explore/repos" ;;
  esac
  echo "REASONED expectation: fixed redirects to /user/login with 303 (REQUIRE_SIGNIN_VIEW is true); a 200 means anonymous browsing is open (FINDING); exit!=0 means TLS or the connection failed (inconclusive)."
)
```

### Confirm self-registration is closed

REASONED: No Forgejo instance runs here. Forgejo serves `/user/sign_up` with `200` either way, but when registration is disabled it sets a registration-disabled notice and suppresses the sign-up form, so the installer-style form field `name="user_name"` is present only when registration is open. The probe fetches the page over HTTPS and reports whether that field is present. Paste the whole block and substitute the two values inside the single quotes.

```bash
# REASONED: no Forgejo instance runs in the authoring environment; unauthenticated GET only.
(
  set +x
  set +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_FORGEJO_BASE_URL' 'REPLACE_WITH_CA_BUNDLE'
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
      body=$(curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert "$ca" \
        -w '\nHTTPSTATUS:%{http_code} exit=%{exitcode} err=%{errormsg}' \
        "$base/user/sign_up") ;;
  esac
  printf '%s\n' "$body" | tail -n 1
  if printf '%s\n' "$body" | grep -q 'name="user_name"'; then
    echo "FINDING (REASONED): the sign-up form is served (DISABLE_REGISTRATION is false); anyone reachable can self-register. Close registration before exposing"
  else
    echo "expected fixed result: the sign-up form is suppressed (DISABLE_REGISTRATION is true)"
  fi
  echo "REASONED expectation: exposed serves the sign-up form (FINDING); fixed suppresses it; exit!=0 in the status line means TLS or the connection failed (inconclusive)."
)
```

## Sources (checked November 2026)

Repository sources are the Forgejo repository at tag `v17.0.1` (commit `363f3dc30beef902b187af5a5244ff7af44901e6`); line numbers in the prose above are at that tag, and its upstream home is codeberg.org, not GitHub. Documentation pages under `https://forgejo.org/docs/` are the rolling, reader-facing administrator docs for the same product.

- Forgejo install-lock default and `HasInstallLock` (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/setting.go
- Forgejo security settings: install-lock load, secret-key fallback, two-factor and password defaults, trusted proxies, push-path hardening, local-path import (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/security.go
- Forgejo example configuration defaults (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/custom/conf/app.example.ini
- Forgejo serveInstall gate and installer route mounting (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/cmd/web.go
- Forgejo installer routes, GET and POST at the root (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/routers/install/routes.go
- Forgejo install handler: admin creation, secret writes and auto-login (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/routers/install/install.go
- Forgejo TOTP two-factor secret encryption (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/models/auth/twofactor.go
- Forgejo access-token hashing and constant-time compare (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/models/auth/access_token.go
- Forgejo server bind, port, ROOT_URL and TLS protocol defaults (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/server.go
- Forgejo service settings: registration, sign-in view, captcha, reverse-proxy auth and user visibility (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/service.go
- Forgejo SSH defaults: built-in server, ports and authorized_keys management (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/ssh.go
- Forgejo repository defaults: force-private, default-private and HTTP git (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/repository.go
- Forgejo Actions settings, enabled by default (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/actions.go
- Forgejo webhook delivery allow-list default (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/services/webhook/deliver.go
- Forgejo host-matcher built-in external, loopback and private ranges (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/hostmatcher/hostmatcher.go
- Forgejo migration SSRF defaults (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/migrations.go
- Forgejo package and container registry enabled by default (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/packages.go
- Forgejo Git LFS server default and auth expiry (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/lfs.go
- Forgejo OAuth2 provider enabled by default (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/oauth2.go
- Forgejo rootless container SSH port default (v17.0.1): https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/docker/rootless/usr/local/bin/docker-setup.sh
- Forgejo configuration cheat sheet (rolling documentation, checked November 2026): https://forgejo.org/docs/latest/admin/config-cheat-sheet/
- Forgejo Actions administrator guide (rolling documentation, checked November 2026): https://forgejo.org/docs/latest/admin/actions/

<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, and any earlier-form run it rests on, not a live demonstration of the shipped form. Unknown means no version recorded.

Components (recorded basis):

- forgejo: Forgejo (v17.0.1)
- forgejo-docs: Forgejo documentation (rolling) (unknown)

Claims (full source mapping in the JSON block below):

- install-lock-default (REASONED; forgejo, forgejo-docs): Forgejo's INSTALL_LOCK defaults to false: HasInstallLock returns Section("security").Key("INSTALL_LOCK").MustBool(false), the loader sets InstallLock from it, and app.example.ini ships INSTALL_LOCK = false.
- install-serves (REASONED; forgejo): While InstallLock is false the process runs the installer, not the app: cmd/web.go calls serveInstall when !setting.InstallLock, and install.Routes() mounts GET / to the install form and POST / to SubmitInstall at the site root.
- install-admin (REASONED; forgejo): The unauthenticated install POST creates a site admin with attacker input: SubmitInstall builds &amp;user_model.User{Name, Email, Passwd, IsAdmin: true} and calls CreateUser, so the first caller to an unlocked installer becomes an administrator.
- install-secrets (REASONED; forgejo): The same install POST writes secrets and locks install: it sets security.INSTALL_LOCK=true, generates INTERNAL_TOKEN and the OAuth2 JWT_SECRET and a SECRET_KEY when each is unset, then saves them to app.ini with cfg.SaveTo.
- install-autologin (REASONED; forgejo): The installer auto-logs-in the new admin: after CreateUser it calls ctx.SetLTACookie(u) and sets the session uid, so the caller leaves the request authenticated as the admin it just created.
- secret-fallback (REASONED; forgejo): If SECRET_KEY is unset Forgejo does not fail: it falls back to the hardcoded literal "!#@FDEWREWR&amp;*(", which a source comment keeps as the widely used default, so a deploy that never set the key runs on a world-known key.
- secret-encrypts (REASONED; forgejo): SECRET_KEY is the data-encryption key: the loader calls keying.Init([]byte(SecretKey)), and TOTP two-factor secrets are stored encrypted under it via keying.TOTP.Encrypt in SetSecret, so a default or leaked key makes 2FA secrets decryptable.
- secret-plaintext (REASONED; forgejo): SECRET_KEY, INTERNAL_TOKEN and the OAuth2 JWT_SECRET live as plaintext in app.ini; their only at-rest protection is filesystem permissions, because the installer writes them with SetValue and SaveTo and there is no secret-manager integration.
- token-hash (REASONED; forgejo): API access tokens are not stored in plaintext: a token row keeps a sha256 TokenHash, a TokenSalt and a TokenLastEight, the token is hashed on generation, and the lookup compares hashes in constant time.
- net-bind (REASONED; forgejo, forgejo-docs): The default HTTP listener binds every interface on port 3000 as plain HTTP: HTTP_ADDR MustString("0.0.0.0"), HTTP_PORT MustString("3000"), Protocol default HTTP and DOMAIN localhost.
- net-rooturl (REASONED; forgejo): ROOT_URL defaults to &lt;proto&gt;://&lt;domain&gt;:&lt;port&gt;, for example http://localhost:3000/; it drives absolute links, cookie scope and OAuth redirects, so a wrong ROOT_URL behind a proxy breaks or weakens those.
- net-tls (REASONED; forgejo, forgejo-docs): Native HTTPS is opt-in: TLS is active only when PROTOCOL=https, which then uses CERT_FILE and KEY_FILE or built-in ACME; the default PROTOCOL is http, so an out-of-the-box Forgejo serves plain HTTP on 3000.
- net-proxy (REASONED; forgejo): Reverse-proxy trust: REVERSE_PROXY_TRUSTED_PROXIES defaults to 127.0.0.0/8, ::1/128 and REVERSE_PROXY_LIMIT to 1; header authentication via ENABLE_REVERSE_PROXY_AUTHENTICATION (header X-WEBAUTH-USER) is off by default.
- reg-open (REASONED; forgejo, forgejo-docs): Open registration is on by default: DISABLE_REGISTRATION resolves through MustBool() to false and app.example.ini ships it false, so anyone who can reach the instance can self-register.
- reg-browse (REASONED; forgejo): The instance is browsable without a login by default: REQUIRE_SIGNIN_VIEW resolves through MustBool() to false and app.example.ini ships it false.
- reg-2fa (REASONED; forgejo): No global 2FA requirement by default: GLOBAL_TWO_FACTOR_REQUIREMENT is empty and resolves to none, ENABLE_CAPTCHA is false, MIN_PASSWORD_LENGTH is 8, PASSWORD_COMPLEXITY defaults to off, and PASSWORD_CHECK_PWN is false.
- reg-visibility (REASONED; forgejo): New accounts and repos lean public: DEFAULT_USER_VISIBILITY resolves to the first allowed mode public, DEFAULT_KEEP_EMAIL_PRIVATE is false, DEFAULT_PRIVATE is last with FORCE_PRIVATE false, and HTTP git is enabled with DISABLE_HTTP_GIT false.
- act-enabled (REASONED; forgejo, forgejo-docs): Forgejo Actions is globally enabled by default: the Actions settings struct initializes Enabled: true with DefaultActionsURL https://data.forgejo.org.
- act-runner (REASONED; forgejo, forgejo-docs): Enabled is not executing: no runner ships or auto-registers, so no workflow runs until an operator registers an act_runner with a token from the admin, org or repo settings; a registered runner running a workflow is arbitrary code execution on the runner host, not the Forgejo host.
- ssrf-webhook (REASONED; forgejo): Webhook delivery is not an open SSRF by default: when webhook.ALLOWED_HOST_LIST is empty it becomes the built-in external matcher, which excludes loopback (127.0.0.0/8, ::1) and private and LAN ranges (RFC 1918, 4193, 6598), and SKIP_TLS_VERIFY is false.
- ssrf-migration (REASONED; forgejo): Repo migration and mirror SSRF is fail-closed too: migrations.ALLOW_LOCALNETWORKS defaults false, SKIP_TLS_VERIFY false and ALLOW_UNENCRYPTED false, and local-path import via IMPORT_LOCAL_PATHS defaults false.
- ssh-builtin (REASONED; forgejo, forgejo-docs): SSH is enabled but the built-in SSH server is off by default: DISABLE_SSH false and START_SSH_SERVER false, so Forgejo uses the host sshd and authorized_keys unless the built-in server is turned on; when on, SSH_PORT and SSH_LISTEN_PORT default to 22.
- ssh-authkeys (REASONED; forgejo): By default Forgejo manages the run account's ~/.ssh/authorized_keys via a forced command (SSH_CREATE_AUTHORIZED_KEYS_FILE true), and the push path is hardened by DISABLE_GIT_HOOKS true and ONLY_ALLOW_PUSH_IF_GITEA_ENVIRONMENT_SET true.
- ssh-container (REASONED; forgejo): The official rootless container image defaults SSH_PORT and SSH_LISTEN_PORT to 2222 in its setup script, so the in-container built-in SSH server listens on 2222 rather than 22.
- pkg-registry (REASONED; forgejo): The package and container registry is on by default: Packages.Enabled is true and RegistryHost is the ROOT_URL host; it authenticates with the same user tokens, so its exposure rides the instance's auth and registration posture.
- lfs-server (REASONED; forgejo, forgejo-docs): The Git LFS server is off by default (LFS_START_SERVER false); when enabled it authenticates with short-lived tokens whose LFS_HTTP_AUTH_EXPIRY defaults to 24 hours.
- oauth-provider (REASONED; forgejo): The OAuth2 provider is enabled by default (OAuth2.Enabled true); a leaked JWT_SECRET, which the installer writes as plaintext into app.ini, undermines every OAuth2 token the instance has issued.
- verify-listeners (REASONED; forgejo): ss inventories local binds in this namespace only; expect 127.0.0.1:3000 for a loopback bind and treat 0.0.0.0:3000 or [::]:3000 as all-interfaces exposure, the shipped default; a failed inventory proves no absence.
- verify-install (REASONED; forgejo): An un-installed Forgejo serves the installer form at / carrying the installer-only name="db_type" field, where an unauthenticated POST / would create a site admin; a locked instance serves the app, so the probe's presence of that field is a takeover FINDING.
- verify-tls (REASONED; forgejo): The install probe fetches / over HTTPS with certificate validation on, so a completed fetch with a status line also confirms TLS, while a nonzero exit means the TLS handshake or connection failed and the result is inconclusive.
- verify-signin (REASONED; forgejo): With REQUIRE_SIGNIN_VIEW true an anonymous request to /explore/repos is redirected to /user/login with 303, and with it false the page returns 200; the probe does not follow redirects, so the status code discriminates.
- verify-registration (REASONED; forgejo): Forgejo serves /user/sign_up with 200 either way, but suppresses the sign-up form when registration is disabled, so the field name="user_name" is present only when DISABLE_REGISTRATION is false; its presence is a FINDING.

````json
{
  "schema": 1,
  "checked": "2026-11-10",
  "documentation_checked": "2026-11",
  "body_sha256": "af053bd6acf0fa7a84f1d8fb958379dd6c1651ef0c6f9d2f02b012c0daf78b5a",
  "components": {
    "forgejo": {
      "name": "Forgejo",
      "basis": "v17.0.1",
      "sources": {
        "s3f2ffe5a08d5": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/setting.go",
        "sf3ba5b6a7894": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/security.go",
        "s29d7d7200de4": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/custom/conf/app.example.ini",
        "sa20e0e37a0cf": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/cmd/web.go",
        "sff39524ba49f": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/routers/install/routes.go",
        "s824dd5d240ba": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/routers/install/install.go",
        "sf19bd5cde7ed": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/models/auth/twofactor.go",
        "s3879055a7879": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/models/auth/access_token.go",
        "sc9d8c80cb133": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/server.go",
        "sf2d6a425a0b4": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/service.go",
        "sa46cfd6747a9": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/ssh.go",
        "sfdd4142a2b6a": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/repository.go",
        "sfefa21c72676": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/actions.go",
        "s9f205aa9ed3c": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/services/webhook/deliver.go",
        "sa77a69b1c999": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/hostmatcher/hostmatcher.go",
        "se9943f8c2bf6": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/migrations.go",
        "s66a4c73c950f": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/packages.go",
        "sc87c932fe2c6": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/lfs.go",
        "sd83514a65420": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/modules/setting/oauth2.go",
        "sdeb88077f18a": "https://codeberg.org/forgejo/forgejo/src/tag/v17.0.1/docker/rootless/usr/local/bin/docker-setup.sh"
      }
    },
    "forgejo-docs": {
      "name": "Forgejo documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s1483cc6ab1d4": "https://forgejo.org/docs/latest/admin/config-cheat-sheet/",
        "s579b9b8dfc12": "https://forgejo.org/docs/latest/admin/actions/"
      }
    }
  },
  "claims": {
    "install-lock-default": {"text": "Forgejo's INSTALL_LOCK defaults to false: HasInstallLock returns Section(\"security\").Key(\"INSTALL_LOCK\").MustBool(false), the loader sets InstallLock from it, and app.example.ini ships INSTALL_LOCK = false.", "components": ["forgejo", "forgejo-docs"], "sources": ["forgejo:s3f2ffe5a08d5", "forgejo:sf3ba5b6a7894", "forgejo:s29d7d7200de4", "forgejo-docs:s1483cc6ab1d4"], "status": "REASONED"},
    "install-serves": {"text": "While InstallLock is false the process runs the installer, not the app: cmd/web.go calls serveInstall when !setting.InstallLock, and install.Routes() mounts GET / to the install form and POST / to SubmitInstall at the site root.", "components": ["forgejo"], "sources": ["forgejo:sa20e0e37a0cf", "forgejo:sff39524ba49f"], "status": "REASONED"},
    "install-admin": {"text": "The unauthenticated install POST creates a site admin with attacker input: SubmitInstall builds &user_model.User{Name, Email, Passwd, IsAdmin: true} and calls CreateUser, so the first caller to an unlocked installer becomes an administrator.", "components": ["forgejo"], "sources": ["forgejo:s824dd5d240ba"], "status": "REASONED"},
    "install-secrets": {"text": "The same install POST writes secrets and locks install: it sets security.INSTALL_LOCK=true, generates INTERNAL_TOKEN and the OAuth2 JWT_SECRET and a SECRET_KEY when each is unset, then saves them to app.ini with cfg.SaveTo.", "components": ["forgejo"], "sources": ["forgejo:s824dd5d240ba"], "status": "REASONED"},
    "install-autologin": {"text": "The installer auto-logs-in the new admin: after CreateUser it calls ctx.SetLTACookie(u) and sets the session uid, so the caller leaves the request authenticated as the admin it just created.", "components": ["forgejo"], "sources": ["forgejo:s824dd5d240ba"], "status": "REASONED"},
    "secret-fallback": {"text": "If SECRET_KEY is unset Forgejo does not fail: it falls back to the hardcoded literal \"!#@FDEWREWR&*(\", which a source comment keeps as the widely used default, so a deploy that never set the key runs on a world-known key.", "components": ["forgejo"], "sources": ["forgejo:sf3ba5b6a7894"], "status": "REASONED"},
    "secret-encrypts": {"text": "SECRET_KEY is the data-encryption key: the loader calls keying.Init([]byte(SecretKey)), and TOTP two-factor secrets are stored encrypted under it via keying.TOTP.Encrypt in SetSecret, so a default or leaked key makes 2FA secrets decryptable.", "components": ["forgejo"], "sources": ["forgejo:sf3ba5b6a7894", "forgejo:sf19bd5cde7ed"], "status": "REASONED"},
    "secret-plaintext": {"text": "SECRET_KEY, INTERNAL_TOKEN and the OAuth2 JWT_SECRET live as plaintext in app.ini; their only at-rest protection is filesystem permissions, because the installer writes them with SetValue and SaveTo and there is no secret-manager integration.", "components": ["forgejo"], "sources": ["forgejo:s824dd5d240ba"], "status": "REASONED"},
    "token-hash": {"text": "API access tokens are not stored in plaintext: a token row keeps a sha256 TokenHash, a TokenSalt and a TokenLastEight, the token is hashed on generation, and the lookup compares hashes in constant time.", "components": ["forgejo"], "sources": ["forgejo:s3879055a7879"], "status": "REASONED"},
    "net-bind": {"text": "The default HTTP listener binds every interface on port 3000 as plain HTTP: HTTP_ADDR MustString(\"0.0.0.0\"), HTTP_PORT MustString(\"3000\"), Protocol default HTTP and DOMAIN localhost.", "components": ["forgejo", "forgejo-docs"], "sources": ["forgejo:sc9d8c80cb133", "forgejo-docs:s1483cc6ab1d4"], "status": "REASONED"},
    "net-rooturl": {"text": "ROOT_URL defaults to <proto>://<domain>:<port>, for example http://localhost:3000/; it drives absolute links, cookie scope and OAuth redirects, so a wrong ROOT_URL behind a proxy breaks or weakens those.", "components": ["forgejo"], "sources": ["forgejo:sc9d8c80cb133"], "status": "REASONED"},
    "net-tls": {"text": "Native HTTPS is opt-in: TLS is active only when PROTOCOL=https, which then uses CERT_FILE and KEY_FILE or built-in ACME; the default PROTOCOL is http, so an out-of-the-box Forgejo serves plain HTTP on 3000.", "components": ["forgejo", "forgejo-docs"], "sources": ["forgejo:sc9d8c80cb133", "forgejo:s29d7d7200de4", "forgejo-docs:s1483cc6ab1d4"], "status": "REASONED"},
    "net-proxy": {"text": "Reverse-proxy trust: REVERSE_PROXY_TRUSTED_PROXIES defaults to 127.0.0.0/8, ::1/128 and REVERSE_PROXY_LIMIT to 1; header authentication via ENABLE_REVERSE_PROXY_AUTHENTICATION (header X-WEBAUTH-USER) is off by default.", "components": ["forgejo"], "sources": ["forgejo:sf3ba5b6a7894", "forgejo:sf2d6a425a0b4"], "status": "REASONED"},
    "reg-open": {"text": "Open registration is on by default: DISABLE_REGISTRATION resolves through MustBool() to false and app.example.ini ships it false, so anyone who can reach the instance can self-register.", "components": ["forgejo", "forgejo-docs"], "sources": ["forgejo:sf2d6a425a0b4", "forgejo:s29d7d7200de4", "forgejo-docs:s1483cc6ab1d4"], "status": "REASONED"},
    "reg-browse": {"text": "The instance is browsable without a login by default: REQUIRE_SIGNIN_VIEW resolves through MustBool() to false and app.example.ini ships it false.", "components": ["forgejo"], "sources": ["forgejo:sf2d6a425a0b4", "forgejo:s29d7d7200de4"], "status": "REASONED"},
    "reg-2fa": {"text": "No global 2FA requirement by default: GLOBAL_TWO_FACTOR_REQUIREMENT is empty and resolves to none, ENABLE_CAPTCHA is false, MIN_PASSWORD_LENGTH is 8, PASSWORD_COMPLEXITY defaults to off, and PASSWORD_CHECK_PWN is false.", "components": ["forgejo"], "sources": ["forgejo:sf3ba5b6a7894", "forgejo:sf2d6a425a0b4"], "status": "REASONED"},
    "reg-visibility": {"text": "New accounts and repos lean public: DEFAULT_USER_VISIBILITY resolves to the first allowed mode public, DEFAULT_KEEP_EMAIL_PRIVATE is false, DEFAULT_PRIVATE is last with FORCE_PRIVATE false, and HTTP git is enabled with DISABLE_HTTP_GIT false.", "components": ["forgejo"], "sources": ["forgejo:sf2d6a425a0b4", "forgejo:sfdd4142a2b6a"], "status": "REASONED"},
    "act-enabled": {"text": "Forgejo Actions is globally enabled by default: the Actions settings struct initializes Enabled: true with DefaultActionsURL https://data.forgejo.org.", "components": ["forgejo", "forgejo-docs"], "sources": ["forgejo:sfefa21c72676", "forgejo-docs:s579b9b8dfc12"], "status": "REASONED"},
    "act-runner": {"text": "Enabled is not executing: no runner ships or auto-registers, so no workflow runs until an operator registers an act_runner with a token from the admin, org or repo settings; a registered runner running a workflow is arbitrary code execution on the runner host, not the Forgejo host.", "components": ["forgejo", "forgejo-docs"], "sources": ["forgejo:sfefa21c72676", "forgejo-docs:s579b9b8dfc12"], "status": "REASONED"},
    "ssrf-webhook": {"text": "Webhook delivery is not an open SSRF by default: when webhook.ALLOWED_HOST_LIST is empty it becomes the built-in external matcher, which excludes loopback (127.0.0.0/8, ::1) and private and LAN ranges (RFC 1918, 4193, 6598), and SKIP_TLS_VERIFY is false.", "components": ["forgejo"], "sources": ["forgejo:s9f205aa9ed3c", "forgejo:sa77a69b1c999"], "status": "REASONED"},
    "ssrf-migration": {"text": "Repo migration and mirror SSRF is fail-closed too: migrations.ALLOW_LOCALNETWORKS defaults false, SKIP_TLS_VERIFY false and ALLOW_UNENCRYPTED false, and local-path import via IMPORT_LOCAL_PATHS defaults false.", "components": ["forgejo"], "sources": ["forgejo:se9943f8c2bf6", "forgejo:sf3ba5b6a7894"], "status": "REASONED"},
    "ssh-builtin": {"text": "SSH is enabled but the built-in SSH server is off by default: DISABLE_SSH false and START_SSH_SERVER false, so Forgejo uses the host sshd and authorized_keys unless the built-in server is turned on; when on, SSH_PORT and SSH_LISTEN_PORT default to 22.", "components": ["forgejo", "forgejo-docs"], "sources": ["forgejo:sa46cfd6747a9", "forgejo:s29d7d7200de4", "forgejo-docs:s1483cc6ab1d4"], "status": "REASONED"},
    "ssh-authkeys": {"text": "By default Forgejo manages the run account's ~/.ssh/authorized_keys via a forced command (SSH_CREATE_AUTHORIZED_KEYS_FILE true), and the push path is hardened by DISABLE_GIT_HOOKS true and ONLY_ALLOW_PUSH_IF_GITEA_ENVIRONMENT_SET true.", "components": ["forgejo"], "sources": ["forgejo:sa46cfd6747a9", "forgejo:sf3ba5b6a7894"], "status": "REASONED"},
    "ssh-container": {"text": "The official rootless container image defaults SSH_PORT and SSH_LISTEN_PORT to 2222 in its setup script, so the in-container built-in SSH server listens on 2222 rather than 22.", "components": ["forgejo"], "sources": ["forgejo:sdeb88077f18a"], "status": "REASONED"},
    "pkg-registry": {"text": "The package and container registry is on by default: Packages.Enabled is true and RegistryHost is the ROOT_URL host; it authenticates with the same user tokens, so its exposure rides the instance's auth and registration posture.", "components": ["forgejo"], "sources": ["forgejo:s66a4c73c950f"], "status": "REASONED"},
    "lfs-server": {"text": "The Git LFS server is off by default (LFS_START_SERVER false); when enabled it authenticates with short-lived tokens whose LFS_HTTP_AUTH_EXPIRY defaults to 24 hours.", "components": ["forgejo", "forgejo-docs"], "sources": ["forgejo:sc87c932fe2c6", "forgejo:s29d7d7200de4", "forgejo-docs:s1483cc6ab1d4"], "status": "REASONED"},
    "oauth-provider": {"text": "The OAuth2 provider is enabled by default (OAuth2.Enabled true); a leaked JWT_SECRET, which the installer writes as plaintext into app.ini, undermines every OAuth2 token the instance has issued.", "components": ["forgejo"], "sources": ["forgejo:sd83514a65420", "forgejo:s824dd5d240ba"], "status": "REASONED"},
    "verify-listeners": {"text": "ss inventories local binds in this namespace only; expect 127.0.0.1:3000 for a loopback bind and treat 0.0.0.0:3000 or [::]:3000 as all-interfaces exposure, the shipped default; a failed inventory proves no absence.", "components": ["forgejo"], "sources": ["forgejo:sc9d8c80cb133"], "status": "REASONED", "verify": [1]},
    "verify-install": {"text": "An un-installed Forgejo serves the installer form at / carrying the installer-only name=\"db_type\" field, where an unauthenticated POST / would create a site admin; a locked instance serves the app, so the probe's presence of that field is a takeover FINDING.", "components": ["forgejo"], "sources": ["forgejo:sa20e0e37a0cf", "forgejo:s824dd5d240ba"], "status": "REASONED", "verify": [2]},
    "verify-tls": {"text": "The install probe fetches / over HTTPS with certificate validation on, so a completed fetch with a status line also confirms TLS, while a nonzero exit means the TLS handshake or connection failed and the result is inconclusive.", "components": ["forgejo"], "sources": ["forgejo:sc9d8c80cb133"], "status": "REASONED", "verify": [2]},
    "verify-signin": {"text": "With REQUIRE_SIGNIN_VIEW true an anonymous request to /explore/repos is redirected to /user/login with 303, and with it false the page returns 200; the probe does not follow redirects, so the status code discriminates.", "components": ["forgejo"], "sources": ["forgejo:sf2d6a425a0b4"], "status": "REASONED", "verify": [3]},
    "verify-registration": {"text": "Forgejo serves /user/sign_up with 200 either way, but suppresses the sign-up form when registration is disabled, so the field name=\"user_name\" is present only when DISABLE_REGISTRATION is false; its presence is a FINDING.", "components": ["forgejo"], "sources": ["forgejo:sf2d6a425a0b4"], "status": "REASONED", "verify": [4]}
  }
}
````
<!-- version-basis:end -->
