# Self-hosted backends: PocketBase and Appwrite

Like Firebase and Supabase ([firebase-supabase.md](firebase-supabase.md)), these backends hand a
public API endpoint to your client code; the collection or resource rules you write gate access
to your data. Files and privileged server credentials need separate attention. Both also ship
an admin console, so complete bootstrap privately before exposing the instance. Appwrite's first
console registrant becomes its initial operator; PocketBase's installer requires a privileged
token from the startup log, not merely an ordinary user's registration.

The source checks below target **PocketBase v0.40.4** and **Appwrite 2.2.0**, with documentation
checked in September 2026. Defaults refer to those releases unless stated otherwise. Live behavior
has not been demonstrated in this authoring environment. Some pin-specific source checks remain
incomplete; the verification backlog records those separately from the live-test debt.

## PocketBase

### 1. Bootstrap privately and protect the operator

Create the superuser before opening access. The documented console syntax is
`./pocketbase superuser create EMAIL PASS`; the alternative is the web-based installer linked from
the server's own startup log. That CLI syntax puts the password in process arguments: do not
substitute a real password there. Use the installer over a private connection to avoid that
credential channel. Do not leave a fresh instance open to the network while bootstrap is
unfinished. See [production setup](https://pocketbase.io/docs/going-to-production/).

The installer URL contains a system-superuser authentication token valid for approximately
30 minutes. A visitor registering an ordinary application user does not thereby become a
superuser. Protect startup logs and the installer URL as credentials, and complete setup before
publishing the proxy route. See the
[pinned installer](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/installer.go).

PocketBase v0.38.0 and later can restrict superuser sessions by IP: set the allowed list under
Settings > Application > Superuser IPs, or use the documented console example
`./pocketbase superuser ips 127.0.0.1 10.0.0.0 --dir=/path/to/your/pb_data`, substituting your
addresses and data directory. The setting is `superuserIPs`; an empty list imposes no restriction.
See [production guidance](https://pocketbase.io/docs/going-to-production/) and the
[pinned IP check](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/middlewares.go).

This controls authenticated superuser requests, not public delivery of the dashboard's static
assets. If the UI must be private, also restrict `/_/` at the proxy or network boundary.
Superuser IP restrictions and MFA are both worth enabling beyond your own machine.

### 2. Bind privately, enable TLS, and constrain proxy trust

PocketBase **has a native HTTPS listener with ACME integration**:
`./pocketbase serve example.com` issues and renews a Let's Encrypt certificate for that domain.
Alternatively, put it behind your own reverse proxy per [nginx.md](nginx.md) or
[caddy.md](caddy.md) and terminate TLS there. See the
[pinned TLS listener](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/serve.go).

Without a domain, `serve` binds to `127.0.0.1:8090`. With a domain, its default listeners become
`0.0.0.0:80` and `0.0.0.0:443`. Behind a TLS proxy on the same host, keep
`--http=127.0.0.1:8090` and omit the domain argument. Set `--origins=https://app.example.com`,
replacing that origin with your real browser application origin; multiple origins are
comma-separated. The default is `*`. CORS controls browser access and does not authorize records.
See the [serve flags](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/cmd/serve.go).

Configure `trustedProxy.headers` only for headers your proxy strips and overwrites, such as
`X-Real-IP`. Block direct backend access. Otherwise, attacker-supplied client-IP headers can
undermine IP allowlists and rate limits. Review forwarded-header ordering before using
`trustedProxy.useLeftmostIP`. See the
[proxy settings](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/settings_model.go).

`--dev` enables diagnostic logging, including SQL, to stderr; it is not an authentication bypass.
Its flag default was not verified here. Avoid unnecessary production diagnostics and protect
their output. See the
[development-mode behavior](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/base.go).

### 3. Cover records, auth-record management, files, and realtime separately

None of the operator controls replaces collection authorization. Every collection's API rules
(`listRule`, `viewRule`, `createRule`, `updateRule`, `deleteRule`) decide what non-superusers can do.
Their default `null` is "locked": only a superuser can perform that action. An empty string opens
the action to everyone, including unauthenticated guests. A nonempty rule filters access.
Superusers bypass API rules entirely, so never hand a superuser account or token to a client
application; use collection rules and scoped authentication instead. See
[API rules](https://pocketbase.io/docs/api-rules-and-filters/) and the
[pinned access check](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/record_query.go).

Auth collections additionally have a **top-level `manageRule`**, default `null`. It grants
privileged management of another auth record, including changing its password without the old
password and directly changing its email or verification state. It operates alongside create
and update rules. Keep it locked unless that delegation is intentional. Its validator accepts
`null` or a nonempty rule, **not `""`**. See the
[pinned auth options and validator](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/collection_model_auth_options.go).

**File fields are unprotected by default.** Knowing a file's full URL is sufficient to download
it, even when the record's API rules are locked. For sensitive files, enable the field's
**Protected** option and require an authorized identity in the collection's `viewRule`.
A protected field with a public `viewRule` can still be downloaded publicly. See
[file handling](https://pocketbase.io/docs/files-handling/) and the
[pinned download authorization](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/file.go).

After authenticating as the intended ordinary user, obtain a short-lived file token with
`await pb.files.getToken()` and supply it to `pb.files.getURL(record, filename, { token })`.
Treat the resulting URL as a credential; do not put it in command arguments or public logs.
The token supplies authentication context, while `viewRule` decides access. See
[protected files](https://pocketbase.io/docs/files-handling/).

Realtime uses `listRule` for collection subscriptions and `viewRule` for individual-record
subscriptions. An established SSE connection, or a successful subscription request, does not
prove authorization to receive a particular record's events. Test actual event delivery with
different users. See the
[pinned realtime rule mapping](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/realtime.go)
and [Realtime API](https://pocketbase.io/docs/api-realtime/).

### 4. Enable MFA and review authentication lifetimes

These are the v0.40.4 auth-option initialization defaults, not a substitute for inspecting an
existing collection's effective settings. Durations are seconds. See the
[pinned defaults](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/collection_model_auth_options.go).

| Option | Default |
| --- | --- |
| `passwordAuth.enabled` | `true` |
| `passwordAuth.identityFields` | `["email"]` |
| `oauth2.enabled` | `false` |
| `mfa.enabled` / `mfa.duration` | `false` / `600` |
| `otp.enabled` / `otp.duration` / `otp.length` | `false` / `180` / `8` |
| `authAlert.enabled` | `true` |
| `authToken.duration` | `432000` |
| `fileToken.duration` | `180` |
| `authRule` | `""` |

Superuser MFA is a separate setting: open `_superusers`, retain password authentication, and
enable both OTP and MFA. Leave `mfa.rule` empty to apply MFA to everyone in that collection.
This requires the password plus an email-delivered one-time code. **Enabling OTP alone is not
MFA**; OTP can otherwise be a standalone login method. OAuth2 is unsupported for `_superusers`.
See [authentication](https://pocketbase.io/docs/authentication/) and the
[MFA configuration](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/collection_model_auth_options.go).

For an application-user collection that should admit only verified accounts, set
`authRule="verified = true"`. Provide working verification email before enforcing it. Keep
authentication alerts enabled and choose token lifetimes appropriate to the deployment.

PocketBase authentication is stateless. Clearing `pb.authStore` removes the client's copy; it
does not revoke a stolen copy. Do not treat browser logout as server-side token revocation.
See [authentication semantics](https://pocketbase.io/docs/authentication/) and
[token validation](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/record_query.go).

### 5. Protect persisted settings and backups

PocketBase stores settings, including SMTP passwords and S3 credentials, as plaintext JSON by
default. Inject a random **32-character** secret through the service environment and select its
name with `--encryptionEnv=PB_ENCRYPTION_KEY`:

```text
PB_ENCRYPTION_KEY=REPLACE_WITH_RANDOM_32_CHARACTER_SECRET
```

`PB_ENCRYPTION_KEY` is a selectable name, not an automatically recognized switch. Setting it
without `--encryptionEnv=PB_ENCRYPTION_KEY` is insufficient. This encrypts persisted settings,
**not the database as a whole or uploaded files**. Protect the data directory, restrict backup
access, and retain the encryption key separately. See
[settings encryption](https://pocketbase.io/docs/going-to-production/) and
[persistence code](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/settings_model.go).

Backups are local by default, and `backups.cron` defaults to empty, so automatic backups are
off. Configure a schedule and retention deliberately. Archives include local uploaded files
but **exclude files stored in S3**; protect and back up that storage separately. See
[backup contents](https://pocketbase.io/docs/going-to-production/) and
[backup settings](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/settings_model.go).

Backup downloads require a **superuser file token**, and the superuser IP restriction also
applies. Ordinary auth tokens and ordinary-user file tokens do not grant backup access. Keep
backup URLs private. See the
[pinned backup download handler](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/backup.go).

### 6. Enable rate limits and working authentication email

Set `rateLimits.enabled=true`. The native limiter exists from v0.23.0, but v0.40.4 defaults it
to **false**. Its seeded rules are:

| Label | Requests / interval |
| --- | --- |
| `*:auth` | 2 / 3 seconds |
| `*:create` | 20 / 5 seconds |
| `/api/batch` | 3 / 1 second |
| `/api/` | 300 / 10 seconds |

See [limiter availability](https://pocketbase.io/docs/going-to-production/) and
[pinned defaults](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/settings_model.go).
Superusers and addresses in `rateLimits.excludedIPs` bypass the limiter. Keep exclusions narrow
and test using an ordinary client from a non-excluded address. See the
[bypass checks](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/middlewares_rate_limit.go).

Configure SMTP before relying on OTP, alerts, verification, or recovery. `smtp.enabled` and
`smtp.tls` both default to `false`; set the connection details and enforce transport protection
appropriate to your mail service. With SMTP disabled, PocketBase falls back to system
`sendmail`, which is not proof of deliverability. Test receipt in the intended mailbox.
See [SMTP settings](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/settings_model.go)
and [mailer selection](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/base.go).

## Appwrite (self-hosted)

### 1. Enforce HTTPS and restrict hostnames

Enforce HTTPS in production with `_APP_OPTIONS_FORCE_HTTPS=enabled`; Appwrite's own docs say to
"always prefer HTTPS over HTTP in production environments." Front it per [nginx.md](nginx.md)
or [caddy.md](caddy.md) and [fronting-auth.md](fronting-auth.md) if you are not terminating TLS at
Appwrite itself. See [production security](https://appwrite.io/docs/advanced/self-hosting/production/security).

```text
_APP_OPTIONS_FORCE_HTTPS=enabled
_APP_OPTIONS_ROUTER_FORCE_HTTPS=enabled
_APP_OPTIONS_ROUTER_PROTECTION=enabled
```

The first setting controls the API; the second controls function and site domains. At 2.2.0,
both configuration defaults are `disabled`. Router protection also defaults to `disabled`;
enabling it rejects unknown hostnames. Configure your actual deployment domains before enabling
it. See the [pinned variables](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/config/variables.php)
and [router and HTTPS enforcement](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/general.php).

There is a documentation/source conflict: the current environment documentation calls
`_APP_OPTIONS_FORCE_HTTPS` deprecated since 1.7.0 and describes an enabled default, while
2.2.0 still implements it with a disabled default. Retain the explicit `enabled` value for
this release, including behind TLS termination. See the
[environment reference](https://appwrite.io/docs/advanced/self-hosting/configuration/environment-variables)
and [pinned enforcement](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/general.php).

### 2. Restrict console registration and protect the dashboard separately

By default only the first user can register through the console; every account after that has
to be invited. Keep root-only registration enabled and configure the email/IP allowlists for
your operators:

```text
_APP_CONSOLE_WHITELIST_ROOT=enabled
_APP_CONSOLE_WHITELIST_EMAILS=operator@example.com
_APP_CONSOLE_WHITELIST_IPS=203.0.113.10
```

Replace the example email and address. The pinned defaults are respectively `enabled`, empty,
and empty. These settings narrow who can **create a console account**, not who can reach or
log into the dashboard. The first restricts self-registration to that one first user; the
other two add registration allowlists. See the
[pinned configuration](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/config/variables.php)
and [registration checks](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/api/account.php).

If the dashboard itself needs to stay unreachable from the open internet, put a separate
network or access boundary in front of it, such as a firewall rule, VPN, or the reverse-proxy
controls in [caddy.md](caddy.md) or [fronting-auth.md](fronting-auth.md). Claim the first console
account while this boundary is private.

Enable console MFA for each operator under the account menu > Your account > Multi-factor
authentication. Add a TOTP authenticator, scan its QR code, and enter an authenticator code to
verify the factor. Store the recovery codes in protected storage accessible if the authenticator
is lost. MFA strengthens permitted operators' password authentication; registration allowlists
alone do not. At 2.2.0, MFA with a verified factor requires a second session factor for account
access. See [console MFA](https://appwrite.io/docs/advanced/security/mfa) and the
[pinned MFA middleware](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/shared/api.php).

Do not inherit the repository's development `.env`: it disables root-only console registration,
abuse protection, and router protection, and contains placeholder secrets. See the
[pinned development environment](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/.env).

Apply `.env` or Compose changes from the installation directory with `docker compose up -d`.
Check effective behavior after recreation. See
[applying changes](https://appwrite.io/docs/advanced/self-hosting/production/security).

### 3. Make permissions explicit and keep server keys off clients

Set collection and document `permissions` deliberately. Enable `documentSecurity` explicitly
when using document-level grants; **its default was not verified here**. Access granted at
**either collection or document level** is sufficient. A broad collection grant therefore
defeats an intended document restriction. The current database documentation describes this
additive model using table/row terminology; the legacy API uses collection/document names.
See [database permissions](https://appwrite.io/docs/products/databases/permissions/) and the
[legacy API reference](https://appwrite.io/docs/references/cloud/server-nodejs/databases).

Omitted permissions do not have one universal result: resources created through a Client SDK
can grant their creator read, update, and delete access; omitted permissions through a Server
SDK or Console grant nobody ordinary resource access. Use specific user identities or team
roles, such as `Role.user(...)` or `Role.team(..., ...)`, rather than `Role.any()` for private
data. See [permission defaults and roles](https://appwrite.io/docs/advanced/security/permissions).

Properly scoped server API keys **bypass resource permissions**. A successful server-key test
does not establish that an ordinary user is authorized. Scopes are selected per key and still
restrict which API operations that key can perform. See the
[pinned key and scope checks](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/shared/api.php).

Project API keys are scoped rather than all-or-nothing; grant only the scopes a given key needs,
and treat any key with `keys.write` as equivalent to an admin credential, since it can change or
delete other keys' scopes. Keys are meant for server SDKs and CLI use, never for client-side code;
store them the way [secrets.md](secrets.md) describes, not in the repository or the client bundle.
See [project API keys](https://appwrite.io/docs/partners/project/api-keys).

### 4. Replace encryption secrets and make recoverable backups

Set a unique `_APP_OPENSSL_KEY_V1` **before storing production data**. The 2.2.0 tag ships the
placeholder `your-secret-key`; replace it rather than treating it as an installation-generated
secret. Inject the real value from protected deployment configuration:

```text
_APP_OPENSSL_KEY_V1=REPLACE_WITH_UNIQUE_ENCRYPTION_SECRET
```

See the [pinned default](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/config/variables.php)
and [encryption guidance](https://appwrite.io/docs/advanced/self-hosting/production/security).

Back up the exact key separately from ordinary data backups and restrict access to both.
Changing or losing it strands previously encrypted secrets; replacing it is not transparent
key rotation. Back up the database, persistent storage, and deployment configuration, and test
restoration in a separate installation. See
[self-hosted backups](https://appwrite.io/docs/advanced/self-hosting/production/backups).

### 5. Keep abuse protection enabled and configure SMTP

Set `_APP_OPTIONS_ABUSE=enabled`. This is the configuration default, but the repository's
development `.env` overrides it to `disabled`. Server API-key requests are exempt, so test
client rate limiting without a server key. See the
[pinned abuse check](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/shared/api.php)
and [rate-limit documentation](https://appwrite.io/docs/advanced/security/rate-limits).

Configure the `_APP_SMTP_*` settings for an actual mail service:

```text
_APP_SMTP_HOST=smtp.example.com
_APP_SMTP_PORT=587
_APP_SMTP_SECURE=tls
_APP_SMTP_USERNAME=REPLACE_WITH_SMTP_USERNAME
_APP_SMTP_PASSWORD=REPLACE_WITH_SMTP_PASSWORD
```

These five settings default to empty; an empty `_APP_SMTP_HOST` disables sending. Match the
port and transport to your provider and protect the credentials. OTP, alerts, invitations,
and recovery cannot be relied upon until delivery works. See the
[pinned SMTP variables](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/config/variables.php)
and [email configuration](https://appwrite.io/docs/advanced/self-hosting/configuration/email).

### 6. Constrain uploads and function execution

The server storage defaults are `_APP_STORAGE_DEVICE=local`,
`_APP_STORAGE_LIMIT=30000000`, and `_APP_STORAGE_ANTIVIRUS=disabled`. Enabling antivirus with
`_APP_STORAGE_ANTIVIRUS=enabled` requires a reachable ClamAV service; configure its host and
port for the deployment. See the
[pinned storage variables](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/config/variables.php).

New buckets have empty permissions and `fileSecurity=false`. Enable file security when using
individual-file grants, and keep bucket permissions narrow: a bucket-level grant also permits
access. Bucket `encryption` and `antivirus` default to `true`, but that antivirus option does
not enable the server-wide scanner. See the
[bucket defaults](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/src/Appwrite/Platform/Modules/Storage/Http/Buckets/Create.php).

Encryption and antivirus are skipped for files **above 20,000,000 bytes**, even with their bucket
options enabled. If either is mandatory, set bucket `maximumFileSize` to no more than
`20000000`, enable the relevant controls, and test the boundary. The default server upload limit
is larger than this threshold. See the
[bucket option semantics](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/src/Appwrite/Platform/Modules/Storage/Http/Buckets/Create.php)
and [size constants](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/init/constants.php).

For functions, `execute` roles and the `scopes` for API keys generated for executions both
default to `[]`. Grant execution only to intended callers and grant the execution key only
the API scopes its code needs. Setting `enabled=false` blocks ordinary callers but does not
block authorized Server SDK API keys. See the
[function options](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/src/Appwrite/Platform/Modules/Functions/Http/Functions/Create.php).

Keep the executor and orchestrator private. The pinned Compose stack mounts the Docker socket
into these services, giving their control plane significant host authority. Replace the
`_APP_EXECUTOR_SECRET` placeholder with a unique protected value:

```text
_APP_EXECUTOR_SECRET=REPLACE_WITH_UNIQUE_EXECUTOR_SECRET
```

Container execution is not demonstrated isolation for mutually hostile tenants. Treat deployment
and execution-control credentials as privileged, and review workload isolation separately.
See the [Compose services](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/docker-compose.yml)
and [executor configuration](https://appwrite.io/docs/advanced/self-hosting/configuration/environment-variables).

## Verify

The live checks below are **reasoned, not demonstrated**. This authoring environment has no
PocketBase executable or container runtime, no writable service installation, and no supplied
deployment, accounts, SMTP service, or second-host ingress fixture. Shell network access also
failed. No available authorized environment could reproduce the live exposed and fixed states.

Use disposable data on a private fixture to establish exposed behavior, then repeat through
the deployed endpoints after hardening. Record response bodies, authorization identities, and
positive controls. A timeout, malformed request, nonexistent resource, or unrelated proxy error
does not establish application authorization.

The former `curl -I` checks are insufficient: HEAD cannot inspect signup controls, PocketBase
serves static `/_/` assets, and Appwrite 2.2.0 Compose sets `_APP_CONSOLE_URL_SCHEME=root`, making
`/console` deployment-dependent. Use the actual console origin and API endpoints below.
See the [PocketBase installer](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/installer.go)
and [Appwrite Compose configuration](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/docker-compose.yml).

### 1. Test resource authorization with denied and allowed identities

**REASONED:** Requires the unavailable live backend and controlled accounts described above.
Use this GET block for each resource comparison below. Put request headers in an owner-readable
file outside the client bundle; use an empty file for a PocketBase guest. PocketBase uses
`Authorization: REPLACE_WITH_USER_TOKEN`. Appwrite uses
`X-Appwrite-Project: REPLACE_WITH_PROJECT_ID` plus the intended end-user session header or cookie.
Use a separate protected header file for each identity, and confirm that identity works on an
allowed resource before accepting its denial elsewhere.

Substitute inside the single quotes and paste whole blocks. Do not paste literal apostrophes
inside those quotes. The guards assume ordinary shell builtins. Credentials are read through
stdin; this does not protect against shell tracing, unsafe file permissions, or the account
owner reading those files. Never place a token-bearing URL in this block.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'https://REPLACE_WITH_BACKEND/REPLACE_WITH_RESOURCE_PATH' 'REPLACE_WITH_PROTECTED_HEADERS_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[[:cntrl:]]*|*'@'*|*'?'*|*'#'*)
      echo "substitute an unsigned HTTPS resource URL; not probing" ;;
    https://*)
      case "$2" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[[:cntrl:]]*)
          echo "substitute the protected headers file path; not probing" ;;
        *)
          curl -q -g -sS --noproxy '*' --proto '=https' \
            --connect-timeout 5 --max-time 20 --header @- \
            -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
            "$1" < "$2" ;;
      esac ;;
    *) echo "use HTTPS; not probing" ;;
  esac
)
```

| Check | Exposed and fixed comparison |
| --- | --- |
| PocketBase record rules | **REASONED:** On the private fixture, request `/api/collections/REPLACE_WITH_COLLECTION/records` and `/api/collections/REPLACE_WITH_COLLECTION/records/REPLACE_WITH_RECORD`. Public empty rules allow guest reads. Locked rules return 403 to non-superusers. Restrictive rules must return only authorized records: an unsatisfied list filter can return 200 with empty `items`, while an unsatisfied view rule returns 404. Confirm the authorized ordinary user receives the known fixture record; separately confirm a superuser bypasses record rules. See [rule outcomes](https://pocketbase.io/docs/api-rules-and-filters/). |
| Appwrite document permissions | **REASONED:** Request `/v1/databases/REPLACE_WITH_DATABASE/collections/REPLACE_WITH_COLLECTION/documents/REPLACE_WITH_DOCUMENT`. With document security explicitly enabled, first demonstrate that a broad collection read grant allows an otherwise ungranted user. Remove that broad grant: the intended document grantee must still receive the fixture, while guests and an unrelated user receive no document data. Compare omitted permissions for client-created and server-created fixtures. See [additive permissions](https://appwrite.io/docs/products/databases/permissions/) and [creation defaults](https://appwrite.io/docs/advanced/security/permissions). |
| Appwrite server-key scope | **REASONED:** Repeat the same document request from a trusted server using a protected API-key header file. A key with the required read scope can read despite empty resource permissions; a key lacking that scope must be refused. This is a separate test, never the positive control for an ordinary user's permissions. See [key authorization](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/shared/api.php). |

### 2. Test bootstrap and registration through the actual APIs

**REASONED:** Requires an unavailable disposable Appwrite installation with its first console
account already created. Prepare an owner-readable JSON file containing the following structure,
then replace its placeholders with an unused controlled email and a test password satisfying
the deployment's password policy:

```json
{
  "userId": "unique()",
  "email": "REPLACE_WITH_TEST_EMAIL",
  "password": "REPLACE_WITH_TEST_PASSWORD",
  "name": "Registration probe"
}
```

The request can create an account on a misconfigured instance. Run it only on the disposable
fixture or an explicitly designated registration-test deployment. Use the API origin serving
the console project, not a guessed `/console` UI path.

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set -- PASTE_WHOLE_BLOCK 'https://REPLACE_WITH_CONSOLE_API_ORIGIN' 'REPLACE_WITH_PROTECTED_SIGNUP_JSON'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[[:cntrl:]]*|*'@'*|*'?'*|*'#'*)
      echo "substitute the console API HTTPS origin; not probing" ;;
    https://*)
      case "$2" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[[:cntrl:]]*)
          echo "substitute the protected signup JSON path; not probing" ;;
        *)
          curl -q -g -sS --noproxy '*' --proto '=https' \
            --connect-timeout 5 --max-time 20 \
            --header 'X-Appwrite-Project: console' \
            --header 'Content-Type: application/json' \
            --data-binary @- \
            -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
            "${1%/}/v1/account" < "$2" ;;
      esac ;;
    *) echo "use HTTPS; not probing" ;;
  esac
)
```

With root-only registration disabled and allowlists empty on the private fixture, a valid new
registration should return 201. After enabling root-only registration and recreating the stack,
an additional self-registration must fail with the console-account-limit error. A duplicate
email or password-validation error does not establish that restriction. Test email and IP
allowlists independently on a fresh private fixture: allowed bootstrap succeeds; an excluded
email or source IP receives its corresponding allowlist error. Existing operator login and
intended invitation acceptance must still work. See the
[registration handler](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/api/account.php).

**REASONED:** Requires an unavailable fresh PocketBase fixture. Submit a valid test-superuser
creation body to `POST /api/collections/_superusers/records`: a guest and an ordinary user's
token must not create a superuser. On the private bootstrap fixture, the valid installer token
must permit creating the operator. Confirm ordinary application-user registration never grants
that privilege. After bootstrap, use a clean browser to inspect the deployed dashboard and
exercise its API authorization; loading static assets is not evidence of administrative access.
See the [installer](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/installer.go)
and [record access checks](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/record_crud.go).

### 3. Exercise the remaining controls

Each comparison below requires the unavailable live fixture. Perform mutations only on disposable
records and functions. Send credentials and request bodies through protected files or the SDK,
never command arguments.

| Control | Required comparison |
| --- | --- |
| Appwrite console MFA | **REASONED:** Requires an unavailable live Appwrite console fixture and controlled operator account with a TOTP authenticator. Using the operator's session and `X-Appwrite-Project: console`, request `GET /v1/account` without an API key. With MFA disabled, password authentication permits this request. Enable MFA and verify the TOTP factor, then create a fresh password-only session: the same request must return `user_more_factors_required`. Complete the TOTP challenge in that session and repeat the request: expect 200 with the operator's account data. See [console MFA](https://appwrite.io/docs/advanced/security/mfa) and [MFA enforcement](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/shared/api.php). |
| PocketBase writes and management | **REASONED:** Exercise `POST /api/collections/REPLACE_WITH_COLLECTION/records`, then `PATCH` and `DELETE` on disposable record URLs, using valid bodies. Public rules expose the actions; locked or restrictive rules must deny unauthorized changes while intended users still succeed. Separately attempt changing another auth record's email, password, and `verified` field: locked `manageRule` must not grant privileged management; an explicitly authorized manager must succeed only where intended. Confirm collection configuration rejects `manageRule=""`. See [CRUD handlers](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/record_crud.go) and [management validation](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/collection_model_auth_options.go). |
| PocketBase protected files | **REASONED:** GET a known fixture file at `/api/files/REPLACE_WITH_COLLECTION/REPLACE_WITH_RECORD/REPLACE_WITH_FILENAME`. Before protection, its unsigned URL downloads despite locked record access. Enable Protected and a `viewRule` that permits the intended ordinary user but denies guests and an unrelated ordinary user. File-token issuance does not check access to a particular file: authenticated users can obtain tokens. Confirm the unrelated user's `pb.files.getToken()` succeeds, then GET the protected fixture using that user's token-bearing SDK URL: expect 404. The permitted user's `pb.files.getToken()` must also succeed, and GET with that user's token-bearing SDK URL must return the expected fixture bytes as a positive control. Separately, an unsigned guest GET of the same protected file must return 404. Use the SDK for signed URLs, or feed a protected curl configuration through stdin. See [download checks](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/file.go). |
| PocketBase realtime | **REASONED:** Establish `GET /api/realtime`, then `POST /api/realtime` subscriptions for both `REPLACE_WITH_COLLECTION/*` and a specific fixture record. Change that record through an authorized writer. Public rules expose events; restrictive list/view rules must suppress unauthorized delivery while an authorized subscriber receives the same mutation. A `PB_CONNECT` event or subscription acknowledgement is insufficient. See [Realtime API](https://pocketbase.io/docs/api-realtime/). |
| PocketBase MFA, verification, and tokens | **REASONED:** Use `POST /api/collections/_superusers/auth-with-password`, followed by the OTP flow through `/request-otp` and `/auth-with-otp`. Without MFA, password authentication completes; with password, OTP, and MFA enabled, the first factor must not complete authentication, while the correct second factor does. For application users, compare password login for otherwise valid verified and unverified accounts with `authRule="verified = true"`. Retain a test token privately, clear the SDK auth store, and retry an allowed record request with the retained token: clearing local state alone must not revoke it. See [authentication flows](https://pocketbase.io/docs/authentication/). |
| PocketBase IP and proxy boundary | **REASONED:** Repeat an authorized superuser resource GET from allowed and excluded source addresses. With no allowlist both can work; with the allowlist the excluded address must receive 403. Forged forwarded-IP headers must not change that result through the proxy. From a second host, test the actual backend address and port as well as the proxy: direct backend access must be blocked, while the permitted proxy route works. If the UI is private, separately test GET `/_/` from both networks. See [IP enforcement](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/middlewares.go) and [proxy settings](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/settings_model.go). |
| TLS, origins, and hostnames | **REASONED:** Request a known API resource over HTTP and HTTPS, and inspect the HTTPS certificate. Fixed deployments must redirect or reject HTTP while HTTPS remains usable. Test Appwrite function/site domains separately. Send the same Appwrite request with an unconfigured `Host`: disabled router protection can serve it; enabled protection must reject it while the configured host works. For PocketBase, compare browser requests from an allowed and disallowed origin; then repeat outside the browser to confirm CORS has not replaced record authorization. See [PocketBase serve flags](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/cmd/serve.go) and [Appwrite routing](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/general.php). |
| Abuse and email delivery | **REASONED:** From a non-excluded ordinary client, send a bounded sequence of valid PocketBase authentication requests across the configured `*:auth` threshold. Disabled limiting should not produce limiter denials; enabled limiting should produce 429, with normal requests succeeding after the window. For Appwrite, cross a documented client endpoint's threshold without an API key and compare disabled/enabled abuse protection. Separately request OTP, verification, and recovery messages and confirm receipt and successful use; a successful request alone does not prove delivery. See [PocketBase limiter](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/middlewares_rate_limit.go), [Appwrite limits](https://appwrite.io/docs/advanced/security/rate-limits), and [email delivery](https://appwrite.io/docs/advanced/self-hosting/configuration/email). |
| Settings encryption and recovery | **REASONED:** On a private PocketBase fixture, save a disposable SMTP credential and inspect persisted settings before and after selecting the encryption environment; plaintext settings must become encrypted, and a restart with the retained key must recover them. Create and restore a backup in a separate fixture, checking local uploads and separately restored S3 objects. Request `/api/backups/REPLACE_WITH_BACKUP_KEY` with no token, an ordinary-user file token, and a superuser file token: only the permitted superuser case should download. For Appwrite, restore disposable encrypted data with the original key; a separate wrong-key fixture must not recover those encrypted values. See [settings persistence](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/settings_model.go), [backup authorization](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/backup.go), and [Appwrite restoration](https://appwrite.io/docs/advanced/self-hosting/production/backups). |
| Appwrite uploads and functions | **REASONED:** Upload harmless fixtures through `POST /v1/storage/buckets/REPLACE_WITH_BUCKET/files`, comparing permitted and unrelated users. Test files at the chosen maximum and one byte above it. With a mandatory encryption/scanning policy capped at 20,000,000 bytes, larger uploads must be rejected; accepted fixtures must show the intended encryption and scanner processing. Invoke a harmless function through `POST /v1/functions/REPLACE_WITH_FUNCTION/executions`: intended execute roles succeed, unrelated users fail, and an authorized server key remains a separate privileged case even when the function is disabled. From the second host, confirm executor/orchestrator ports are inaccessible. See [bucket controls](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/src/Appwrite/Platform/Modules/Storage/Http/Buckets/Create.php), [function controls](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/src/Appwrite/Platform/Modules/Functions/Http/Functions/Create.php), and [service networks](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/docker-compose.yml). |

### 4. Check the client bundle for privileged credentials

**REASONED:** No deployed client bundle or credential inventory was supplied. Confirm that the
client carries only an end-user session or auth token, never a PocketBase superuser token or an
Appwrite API key of any scope. Appwrite API keys are server credentials regardless of scope;
client code should authenticate with an end-user session from the Client SDK instead. See
[PocketBase superusers](https://pocketbase.io/docs/authentication/) and
[Appwrite API keys](https://appwrite.io/docs/partners/project/api-keys).

Grep the client bundle for the strings used by your admin credentials or API keys; they should
not appear. Prepare a protected, nonempty patterns file containing one exact credential per
line, outside the bundle directory. The command prints matching filenames, not secret-bearing
lines. Establish a positive control using a disposable dummy credential in a test bundle, then
remove it and repeat. Exact matching does not detect every encoded or split representation.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PROTECTED_SECRET_PATTERNS_FILE' 'REPLACE_WITH_CLIENT_BUNDLE_DIRECTORY'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not scanning"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not scanning"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the protected patterns file path; not scanning" ;;
    *)
      case "$2" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
          echo "substitute the client bundle directory; not scanning" ;;
        *)
          if grep -r -F -l -f "$1" -- "$2"; then
            echo "FAIL: credential matches in the files listed above"
          else
            case "$?" in
              1) echo "No exact matches; also inspect build inputs and source maps." ;;
              *) echo "Scan failed; no conclusion." ;;
            esac
          fi ;;
      esac ;;
  esac
)
```

### Demonstration backlog

All three bash blocks passed ShellCheck 0.11.0 and `bash -n` during authoring. Local guard tests
refused embedded `REPLACE_WITH_` placeholders, `example.com`, angle brackets, empty arguments,
and omitted or shortened `set --` lines. These checks establish shell behavior only. No live
service result or deployed-bundle scan is claimed.

| ID | Required exposed/fixed demonstration | Status |
| --- | --- | --- |
| SELFHOSTED-BACKEND-LIVE-1 | Demonstrate every REASONED comparison above on PocketBase v0.40.4 and Appwrite 2.2.0, recording binary/image identity, commands, response bodies, denied and allowed identities, disposable-data cleanup, and effective settings. Requires writable service fixtures, a container runtime, controlled accounts and mailboxes, S3 and backup fixtures, ClamAV, function execution, a second-host ingress fixture, and the actual client build. Include all five PocketBase actions, manageRule, file-token issuance versus protected downloads (unrelated-user and unsigned-guest denial, permitted-user bytes), realtime, bootstrap-token handling, MFA, verification, retained-token behavior, additive Appwrite permissions, server-key scopes, registration, console MFA (fresh password-only denial and successful TOTP completion), TLS, proxy trust, limits, encrypted recovery, uploads, and executor privacy. | Open; live behavior is reasoned, not demonstrated. |
| SELFHOSTED-BACKEND-SOURCE-1 | Complete pin-specific tracing for the Appwrite legacy collection/document implementation and creator permission defaults, and the PocketBase CLI wrapper and backup archive implementation. Vendor documentation was opened for these controls, but the corresponding implementation files could not all be retrieved at the requested tags. Do not infer the documentSecurity or --dev flag default. | Open; complete pinned-source verification is not claimed. |

## Sources (checked September 2026)

- PocketBase going to production: https://pocketbase.io/docs/going-to-production/
- PocketBase API rules and filters: https://pocketbase.io/docs/api-rules-and-filters/
- Appwrite self-hosting production security: https://appwrite.io/docs/advanced/self-hosting/production/security
- Appwrite project API keys: https://appwrite.io/docs/partners/project/api-keys
- [PocketBase authentication](https://pocketbase.io/docs/authentication/).
- [PocketBase files and protected downloads](https://pocketbase.io/docs/files-handling/).
- [PocketBase Realtime API](https://pocketbase.io/docs/api-realtime/).
- [PocketBase v0.40.4 installer and bootstrap-token lifetime](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/installer.go).
- [PocketBase v0.40.4 listener and origin flags](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/cmd/serve.go).
- [PocketBase v0.40.4 native TLS and ACME listener](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/serve.go).
- [PocketBase v0.40.4 authentication and superuser IP middleware](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/middlewares.go).
- [PocketBase v0.40.4 record authorization and token validation](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/record_query.go).
- [PocketBase v0.40.4 record CRUD handlers](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/record_crud.go).
- [PocketBase v0.40.4 auth defaults, manageRule validation, and MFA](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/collection_model_auth_options.go).
- [PocketBase v0.40.4 settings, encryption, proxy trust, SMTP, backups, and rate defaults](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/settings_model.go).
- [PocketBase v0.40.4 development logging and mailer selection](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/base.go).
- [PocketBase v0.40.4 file-token and download authorization](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/file.go).
- [PocketBase v0.40.4 realtime authorization](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/realtime.go).
- [PocketBase v0.40.4 backup download authorization](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/backup.go).
- [PocketBase v0.40.4 rate limiter and exemptions](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/middlewares_rate_limit.go).
- [Appwrite permissions, creation defaults, and server integrations](https://appwrite.io/docs/advanced/security/permissions).
- [Appwrite additive database permissions](https://appwrite.io/docs/products/databases/permissions/).
- [Appwrite legacy Databases API](https://appwrite.io/docs/references/cloud/server-nodejs/databases).
- [Appwrite environment reference and HTTPS deprecation wording](https://appwrite.io/docs/advanced/self-hosting/configuration/environment-variables).
- [Appwrite rate limits](https://appwrite.io/docs/advanced/security/rate-limits).
- [Appwrite email delivery](https://appwrite.io/docs/advanced/self-hosting/configuration/email).
- [Appwrite self-hosted backups and encryption-key preservation](https://appwrite.io/docs/advanced/self-hosting/production/backups).
- [Appwrite 2.2.0 configuration defaults](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/config/variables.php).
- [Appwrite 2.2.0 development environment and placeholder secrets](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/.env).
- [Appwrite 2.2.0 console registration handler](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/api/account.php).
- [Appwrite console MFA enrollment and recovery codes](https://appwrite.io/docs/advanced/security/mfa).
- [Appwrite 2.2.0 API-key authorization, scopes, MFA enforcement, and abuse exemptions](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/shared/api.php).
- [Appwrite 2.2.0 hostname routing and HTTPS enforcement](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/general.php).
- [Appwrite 2.2.0 bucket defaults and upload controls](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/src/Appwrite/Platform/Modules/Storage/Http/Buckets/Create.php).
- [Appwrite 2.2.0 function execute roles, execution-key scopes, and enablement](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/src/Appwrite/Platform/Modules/Functions/Http/Functions/Create.php).
- [Appwrite 2.2.0 storage thresholds and release constant](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/init/constants.php).
- [Appwrite 2.2.0 Compose console path, persistent volumes, and Docker socket mounts](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/docker-compose.yml).
