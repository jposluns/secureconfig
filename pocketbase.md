# Self-hosted backends: PocketBase and Appwrite

PocketBase and Appwrite are self-hosted backends that give apps a database, user accounts and file storage through one API. This guide helps your AI assistant configure each securely, including private bootstrap, deliberate binding and TLS, access rules on every collection or resource, and server keys kept off clients.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/pocketbase.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against PocketBase v0.41.1, Appwrite 2.7.0, utopia-php/database 10.1.0, and curl curl-8_14_1; 2 further sources carry no recorded version. Metadata reviewed 2026-11-05; documentation checked November 2026. The guide records 91 claims: 2 demonstrated by a check that ran and 89 reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

Like Firebase and Supabase ([firebase-supabase.md](firebase-supabase.md)), these backends hand a
public API endpoint to your client code; the collection or resource rules you write gate access
to your data. Files and privileged server credentials need separate attention. Both also ship
an admin console, so complete bootstrap privately before exposing the instance. Appwrite's first
console registrant becomes its initial operator; PocketBase's installer requires a privileged
token from the startup log, not merely an ordinary user's registration.

The source checks below target **PocketBase v0.41.1** and **Appwrite 2.7.0**, with documentation
checked in November 2026: the Appwrite pages as served on 2026-11-04 and the PocketBase pages as
served on 2026-11-05. Defaults refer to those releases unless stated otherwise. Live behavior
has not been demonstrated in this authoring environment. Some pin-specific source checks remain
incomplete; the source-work table below records those. Live comparisons are REASONED from the
cited vendor documentation and the pinned sources that were available.

From v0.41.0, PocketBase publishes its source and releases on its author's forge at
`https://ganigeorgiev.com` instead of GitHub, so the PocketBase source citations below point to
that forge at the v0.41.1 tag, with any line range given in the link text. The
[v0.41.0 release notes](https://ganigeorgiev.com/pocketbase/pocketbase/releases?expr=tag%3D%22v0.41.0%22)
flag one change with a warning sign, the Go module's move from GitHub to the new host. No
statement in this guide depends on the module path.

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
[pinned installer](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/installer.go?rev=v0.41.1).

PocketBase v0.38.0 and later can restrict superuser sessions by IP: set the allowed list under
Settings > Application > Superuser IPs, or use the documented console example
`./pocketbase superuser ips 127.0.0.1 10.0.0.0 --dir=/path/to/your/pb_data`, substituting your
addresses and data directory. The setting is `superuserIPs`; an empty list imposes no restriction.
See [production guidance](https://pocketbase.io/docs/going-to-production/) and the
[pinned IP check](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/middlewares.go?rev=v0.41.1).

This controls authenticated superuser requests, not public delivery of the dashboard's static
assets. If the UI must be private, also restrict `/_/` at the proxy or network boundary.
Superuser IP restrictions and MFA are both worth enabling beyond your own machine.

### 2. Bind privately, enable TLS, and constrain proxy trust

PocketBase **has a native HTTPS listener with ACME integration**:
`./pocketbase serve example.com` issues and renews a Let's Encrypt certificate for that domain.
Alternatively, put it behind your own reverse proxy per [nginx.md](nginx.md) or
[caddy.md](caddy.md) and terminate TLS there. See the
[pinned TLS listener](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/serve.go?rev=v0.41.1).

Without a domain, `serve` binds to `127.0.0.1:8090`. With a domain, its default listeners become
`0.0.0.0:80` and `0.0.0.0:443`. Behind a TLS proxy on the same host, keep
`--http=127.0.0.1:8090` and omit the domain argument. Set `--origins=https://app.example.com`,
replacing that origin with your real browser application origin; multiple origins are
comma-separated. The default is `*`. CORS controls browser access and does not authorize records.
See the [serve flags](https://ganigeorgiev.com/pocketbase/pocketbase/files/cmd/serve.go?rev=v0.41.1).

Configure `trustedProxy.headers` only for headers your proxy strips and overwrites, such as
`X-Real-IP`. Block direct backend access. Otherwise, attacker-supplied client-IP headers can
undermine IP allowlists and rate limits. Review forwarded-header ordering before using
`trustedProxy.useLeftmostIP`. See the
[proxy settings](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/settings_model.go?rev=v0.41.1).

`--dev` enables diagnostic logging, including SQL, to stderr; it is not an authentication bypass.
In the pinned CLI wrapper, `Start()` registers the `serve` and `superuser` commands on the root
command, and the `--dev` flag default is the configured value. `New()` sets it to true exactly
when `os.Args[0]` starts with a nonempty `os.TempDir()` or `cacheDir()` prefix, and false otherwise.
In dev mode the pinned code logs executed SQL statements and lowers the logger
threshold so practically all logs print. Avoid unnecessary production diagnostics and protect
their output. See the
[development-mode behavior](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/base.go?rev=v0.41.1),
[command wiring, lines 165 to 173](https://ganigeorgiev.com/pocketbase/pocketbase/files/pocketbase.go?rev=v0.41.1),
[dev default selection, lines 73 to 79](https://ganigeorgiev.com/pocketbase/pocketbase/files/pocketbase.go?rev=v0.41.1),
[go run detection, lines 10 to 19](https://ganigeorgiev.com/pocketbase/pocketbase/files/tools/osutils/run.go?rev=v0.41.1),
[flag-to-app wiring, lines 129 to 139](https://ganigeorgiev.com/pocketbase/pocketbase/files/pocketbase.go?rev=v0.41.1),
[dev SQL logging, lines 1277 to 1286](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/base.go?rev=v0.41.1), and
[dev logger level, lines 1489 to 1499](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/base.go?rev=v0.41.1).

### 3. Cover records, auth-record management, files, and realtime separately

None of the operator controls replaces collection authorization. Every collection's API rules
(`listRule`, `viewRule`, `createRule`, `updateRule`, `deleteRule`) decide what non-superusers can do.
Their default `null` is "locked": only a superuser can perform that action. An empty string opens
the action to everyone, including unauthenticated guests. A nonempty rule filters access.
Superusers bypass API rules entirely, so never hand a superuser account or token to a client
application; use collection rules and scoped authentication instead. See
[API rules](https://pocketbase.io/docs/api-rules-and-filters/) and the
[pinned access check](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/record_query.go?rev=v0.41.1).

Auth collections additionally have a **top-level `manageRule`**, default `null`. It grants
privileged management of another auth record, including changing its password without the old
password and directly changing its email or verification state. It operates alongside create
and update rules. Keep it locked unless that delegation is intentional. Its validator accepts
`null` or a nonempty rule, **not `""`**. See the
[pinned auth options and validator](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/collection_model_auth_options.go?rev=v0.41.1).

**File fields are unprotected by default.** Knowing a file's full URL is sufficient to download
it, even when the record's API rules are locked. For sensitive files, enable the field's
**Protected** option and require an authorized identity in the collection's `viewRule`.
A protected field with a public `viewRule` can still be downloaded publicly. See
[file handling](https://pocketbase.io/docs/files-handling/) and the
[pinned download authorization](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/file.go?rev=v0.41.1).

After authenticating as the intended ordinary user, obtain a short-lived file token with
`await pb.files.getToken()` and supply it to `pb.files.getURL(record, filename, { token })`.
Treat the resulting URL as a credential; do not put it in command arguments or public logs.
The token supplies authentication context, while `viewRule` decides access. See
[protected files](https://pocketbase.io/docs/files-handling/).

Realtime uses `listRule` for collection subscriptions and `viewRule` for individual-record
subscriptions. An established SSE connection, or a successful subscription request, does not
prove authorization to receive a particular record's events. Test actual event delivery with
different users. See the
[pinned realtime rule mapping](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/realtime.go?rev=v0.41.1)
and [Realtime API](https://pocketbase.io/docs/api-realtime/).

### 4. Enable MFA and review authentication lifetimes

These are the v0.41.1 auth-option initialization defaults, not a substitute for inspecting an
existing collection's effective settings. Durations are seconds. See the
[pinned defaults](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/collection_model_auth_options.go?rev=v0.41.1).

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
[MFA configuration](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/collection_model_auth_options.go?rev=v0.41.1).

For an application-user collection that should admit only verified accounts, set
`authRule="verified = true"`. Provide working verification email before enforcing it. Keep
authentication alerts enabled and choose token lifetimes appropriate to the deployment.

PocketBase authentication is stateless. Clearing `pb.authStore` removes the client's copy; it
does not revoke a stolen copy. Do not treat browser logout as server-side token revocation.
See [authentication semantics](https://pocketbase.io/docs/authentication/) and
[token validation](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/record_query.go?rev=v0.41.1).

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
[persistence code](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/settings_model.go?rev=v0.41.1).

Backups are local by default, and `backups.cron` defaults to empty, so automatic backups are
off. Configure a schedule and retention deliberately. Archives contain the main and logs
databases plus the rest of `pb_data`, excluding the backups directory and tracked exclusions.
The source says uploaded collection files on S3 are outside `pb_data` and need manual backup;
protect that storage separately. See [backup archive implementation, lines 36 to 60](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/backup_create.go?rev=v0.41.1) and
[backup settings](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/settings_model.go?rev=v0.41.1).

Backup downloads require a **superuser file token**, and the superuser IP restriction also
applies. Ordinary auth tokens and ordinary-user file tokens do not grant backup access. Keep
backup URLs private. See the
[pinned backup download handler](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/backup.go?rev=v0.41.1).

### 6. Enable rate limits and working authentication email

Set `rateLimits.enabled=true`. The native limiter exists from v0.23.0, but v0.41.1 defaults it
to **false**. Its seeded rules are:

| Label | Requests / interval |
| --- | --- |
| `*:auth` | 2 / 3 seconds |
| `*:create` | 20 / 5 seconds |
| `/api/batch` | 3 / 1 second |
| `/api/` | 300 / 10 seconds |

See [limiter availability](https://pocketbase.io/docs/going-to-production/) and
[pinned defaults](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/settings_model.go?rev=v0.41.1).
Superusers and addresses in `rateLimits.excludedIPs` bypass the limiter. Keep exclusions narrow
and test using an ordinary client from a non-excluded address. See the
[bypass checks](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/middlewares_rate_limit.go?rev=v0.41.1).

Configure SMTP before relying on OTP, alerts, verification, or recovery. `smtp.enabled` and
`smtp.tls` both default to `false`; set the connection details and enforce transport protection
appropriate to your mail service. With SMTP disabled, PocketBase falls back to system
`sendmail`, which is not proof of deliverability. Test receipt in the intended mailbox.
See [SMTP settings](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/settings_model.go?rev=v0.41.1)
and [mailer selection](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/base.go?rev=v0.41.1).

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

The first setting controls the API; the second controls function and site domains. At 2.7.0,
both configuration defaults are `disabled`. Router protection also defaults to `disabled`;
enabling it rejects unknown hostnames. Configure your actual deployment domains before enabling
it. See the [pinned variables](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/config/variables.php)
and [router and HTTPS enforcement](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/controllers/general.php).

There is a documentation/source conflict: the environment documentation as served on 2026-11-04
calls `_APP_OPTIONS_FORCE_HTTPS` deprecated since 1.7.0 and describes an enabled default, while
2.7.0 still implements it with a disabled default. Retain the explicit `enabled` value for
this release, including behind TLS termination. See the
[environment reference](https://appwrite.io/docs/advanced/self-hosting/configuration/environment-variables)
and [pinned enforcement](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/controllers/general.php).

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
other two add registration allowlists. At 2.7.0 these checks are in the Account module's
account-create handler, since 2.7.0 has no `app/controllers/api/account.php`. See the
[pinned configuration](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/config/variables.php)
and [registration checks](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Account/Http/Account/Create.php#L109-L134).

If the dashboard itself needs to stay unreachable from the open internet, put a separate
network or access boundary in front of it, such as a firewall rule, VPN, or the reverse-proxy
controls in [caddy.md](caddy.md) or [fronting-auth.md](fronting-auth.md). Claim the first console
account while this boundary is private.

Appwrite 2.3.0 changed how the console's location is configured. Its release notes say
"`_APP_CONSOLE_URL` is the origin every console link is built from" and "`_APP_CONSOLE_URL_SCHEME`
and the legacy `/console/...` link shapes are gone". Their upgrade section says "Remove
`_APP_CONSOLE_URL_SCHEME` from your `.env`, and set `_APP_CONSOLE_URL` if your console is served
from a different host than the API." The served environment reference marks `_APP_CONSOLE_URL` as
`version >= 2.3.0` and says it "Replaces `_APP_CONSOLE_URL_SCHEME`, which is removed." At 2.7.0
the variable defaults to empty, and the root Compose file passes `_APP_CONSOLE_URL` to the
`appwrite` service without a value. Set it to the console origin your boundary serves when that
differs from the API host. See the
[2.3.0 release notes](https://github.com/appwrite/appwrite/releases/tag/2.3.0),
[pinned configuration](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/config/variables.php),
[pinned Compose file](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/docker-compose.yml) and
[environment reference](https://appwrite.io/docs/advanced/self-hosting/configuration/environment-variables).

Enable console MFA for each operator under the account menu > Your account > Multi-factor
authentication. Add a TOTP authenticator, scan its QR code, and enter an authenticator code to
verify the factor. Store the recovery codes in protected storage accessible if the authenticator
is lost. MFA strengthens permitted operators' password authentication; registration allowlists
alone do not. At 2.7.0, MFA with a verified factor requires a second session factor for account
access; the middleware now takes the required count from the user's `getMinimumFactors()`. See
[console MFA](https://appwrite.io/docs/advanced/security/mfa), the
[pinned MFA middleware](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/controllers/shared/api.php)
and the [minimum factors](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Utopia/Database/Documents/User.php#L211-L218).

Appwrite 2.7.0 also tightens two MFA steps that the served MFA page does not reflect as of
2026-11-04. Its release notes say "Make TOTP codes single-use, so one code can't complete a
challenge on a second session; the enrolment code can't be reused either" and "Require an MFA
challenge from the last few minutes to turn MFA off, as deleting an authenticator already does".
As source reading of 2.7.0, a TOTP challenge records the code's time step as spent and refuses
that step or an earlier one afterwards. Turning MFA off while it is in force needs a session
challenge completed within `MFA_RECENT_DURATION`, 1800 seconds. Expect both when you test MFA.
See the [2.7.0 release notes](https://github.com/appwrite/appwrite/releases/tag/2.7.0),
[single-use TOTP steps](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Auth/MFA/Challenge/TOTP.php#L30-L88),
[challenge spend](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Account/Http/Account/MFA/Challenges/Update.php#L165-L177),
[MFA turn-off check](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Account/Http/Account/MFA/Update.php#L81-L84),
[recent-challenge window](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Utopia/Database/Documents/User.php#L230-L244) and
[window length](https://github.com/appwrite/appwrite/blob/2.7.0/app/init/constants.php#L266).

Do not inherit the repository's development `.env`: it disables root-only console registration,
abuse protection, and router protection, and contains placeholder secrets. See the
[pinned development environment](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/.env).

Apply `.env` or Compose changes from the installation directory with `docker compose up -d`.
Check effective behavior after recreation. See
[applying changes](https://appwrite.io/docs/advanced/self-hosting/production/security).

### 3. Make permissions explicit and keep server keys off clients

Set collection and document `permissions` deliberately. In Appwrite 2.7.0,
`documentSecurity` defaults to `false`; enable it for document-level grants. Access granted at
**either collection or document level** is sufficient. A broad collection grant therefore
defeats an intended document restriction. See [legacy database permissions](https://appwrite.io/docs/products/databases/tablesdb/legacy/permissions).
The [collection create parameter](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Create.php#L88-L90) states the requirement for one of the two permission levels.

For a document with null or omitted `permissions`, the Appwrite 2.7.0 create handler
calls `Permission::aggregate` first. The pinned helper returns null for null input, so
`permissions` remains null and reaches the handler's default branch. The handler assigns
read/update/delete user grants when the requester has a user ID and is not privileged;
otherwise it assigns an empty list. API-key requests skip subsequent role validation, but
the key check alone does not set that default list. Use specific user identities or team
roles, such as `Role.user(...)` or `Role.team(..., ...)`, rather than `Role.any()` for private
data. See [document create parameter](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Create.php#L134-L139),
[requester classification](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Create.php#L217-L218),
[null-permissions handling](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Create.php#L238-L288),
[pinned dependency](https://github.com/appwrite/appwrite/blob/2.7.0/composer.lock#L4429-L4439),
[pinned aggregate helper](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Permission.php#L176-L180), and
[permission roles](https://appwrite.io/docs/advanced/security/permissions).

For a 2.7.0 document GET, the pinned handler reads the requester class from the request's
authorization roles: the `keys` role marks an API-key request, and the `owner`, `developer`, or
`admin` role marks a privileged one. A disabled database or collection is reported as not found,
except to API-key or privileged requesters, and, for a request without a transaction ID, the
document itself is then fetched through the database layer. With an API key, the request's role
and scopes come from the key, and at 2.7.0 every key also holds the `public` scope; a standard,
ephemeral or `dynamic` project key for the same project sets the current authorization status to
disabled. So do admin-mode console sessions, except on the console project's `/v1/projects` and
`/v1/projects/:projectId` routes and GET requests to the `/v1/organization/projects` routes, which
enable it. An OAuth2 key with the `owner` role on an admin-mode request by a user to a project
other than the console also sets it to disabled. Route scope validation still applies to every requester. At 2.7.0 a request with an
`x-appwrite-key` header that resolves to no key is refused. Collection `permissions` and
`documentSecurity` are handed to utopia-php/database when the collection is created. The
dependency's read checks and remaining deployment, installer and transaction-state gaps are
described below; relating these checks to server-key permission bypass is this guide's
source-based reasoning alongside the cited documentation, not a live demonstration.
See the
[document read handler](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Get.php#L82-L97),
[document fetch](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Get.php#L105-L132),
[role classification](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Utopia/Database/Documents/User.php#L82-L116),
[API-key role and authorization status](https://github.com/appwrite/appwrite/blob/2.7.0/app/controllers/shared/api.php#L146-L167),
[admin-mode authorization status](https://github.com/appwrite/appwrite/blob/2.7.0/app/controllers/shared/api.php#L328-L361),
[OAuth2 owner key status](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/controllers/shared/api.php),
[request role assignment](https://github.com/appwrite/appwrite/blob/2.7.0/app/controllers/shared/api.php#L396-L400),
[route scope validation](https://github.com/appwrite/appwrite/blob/2.7.0/app/controllers/shared/api.php#L557-L561),
[collection permission handoff](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Create.php#L230-L236), and the
[pinned dependency](https://github.com/appwrite/appwrite/blob/2.7.0/composer.lock#L4429-L4439).

Appwrite 2.7.0's `composer.lock` pins utopia-php/database 10.1.0 at commit 950a4907. At that
commit, `getPermissionsByType()` splits each stored permission at its first `(`, skipping one
with no `(`, keys it on the action name with surrounding whitespace trimmed and strips `)`, double
quotes and spaces to yield distinct role strings. Missing or null permissions yield no roles
rather than throwing, since `getAttribute` returns its `[]` default for an unset or null value; a
non-null value that is not an array, or an entry that is not a string, throws. The 7.3.9
`getRead()` accessor no longer exists. `Authorization` stores added roles as keys. With its status enabled, it accepts a
permission string matching any role key and rejects an empty permission list or one with no
match. See [role extraction](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Document.php#L273-L334),
[attribute default](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Document.php#L405-L416) and
[role matching](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Validator/Authorization.php#L59-L102).

At 10.1.0, `Database` takes its document methods from the `Trait\Documents` trait, whose code
was not read for this guide. So the Database-level read checks in `getDocument` and `find`, and
the `find` dispatch through `skip` after a successful collection check, are not established at
10.1.0. The 7.3.9 reading found those checks additive, a collection grant sufficing; this guide
does not assert that for 2.7.0. The database still passes its authorization instance to the
adapter. See the
[trait use](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Database.php#L52-L61) and
[authorization handoff](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Database.php#L1033-L1039).

At 10.1.0 `Authorization` has no `setDefaultStatus`. `setStatus`, `enable` and `disable` change
the current status, `getStatus` returns it, and `reset` restores the status the instance was
constructed with, `true` by default. `skip` runs a callback with status false through a value that
the class comment scopes to "the calling coroutine and the coroutines it starts"; how that value
restores the prior status was not read. For a valid `Input`, disabled status makes `isValid`
return true before checking an empty permission list or matching roles; invalid input is still
refused. Appwrite 2.2.0 called `setDefaultStatus(false)` for keys and admin mode, and 2.7.0 calls
`setStatus(false)`. This guide infers that the 2.7.0 calls change only the current status, so a
later `reset()` would restore `true`; the 2.7.0 files read here never call `reset()` on an
`Authorization` instance.
See [status controls](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Validator/Authorization.php#L148-L208),
[shared status and constructor default](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Validator/Authorization.php#L10-L41), and
[role matching](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Validator/Authorization.php#L59-L102).

At 10.1.0, `SQL.php` supplies `getDocument` and `find` for MariaDB, Postgres and SQLite, and
through MariaDB for MySQL. SQLite now extends `SQL` directly, no longer through MariaDB, and its
own `find` refuses queries using aggregates it does not support before calling the parent's.
See the
[MariaDB](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/MariaDB.php#L46),
[Postgres](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Postgres.php#L53),
[MySQL](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/MySQL.php#L25), and
[SQLite](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQLite.php#L71) class declarations and the
[SQLite find wrapper](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQLite.php#L249-L259).
Without selections or join queries, SQL `getDocument` selects by ID with a bound parameter, adds a
tenant clause itself under shared tables and returns the row as a document. Neither that path nor
the builder path it uses for selections without joins adds a shared-authorization status check or
permission predicate. With join queries, it reads the
requester roles and builds its query through `configureFindBuilder`, which adds the permission
hooks under the same conditions as `find` below. See the
[complete SQL document fetch](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L650-L779).

SQL `find` reads roles from the shared authorization instance and defaults to the read action.
As source reading of 10.1.0, it adds the main collection's document-permission hook only when that
instance's status is enabled and the collection has `documentSecurity` enabled or is the metadata
collection. With joins, and on its bounded-page path, it also skips that hook for a collection
whose `Database::COLLECTION_GRANTED` attribute is true; where that attribute is set was not read.
Separately, while the status is enabled, it wraps a permission hook for each joined table in a
`Permission\Join` hook, whatever the main collection's `documentSecurity` or grant. It omits one
only when the collection's `Database::JOIN_DOCUMENT_SECURITY` map gives that table a value that
casts to false; an empty map, or one with no entry for the table, keeps it. Where that map is set
was not read.
On a join that keeps unmatched rows, it also adds a `Permission\OuterJoin` hook once any of these
permission hooks is added. At 7.3.9 the predicate depended on the status alone, whatever the
`documentSecurity` setting. See the
[SQL find entry](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L1566-L1572),
[SQL find permission gate](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L5063-L5079),
[joined-table permission hooks](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L5081-L5112),
[per-document filtering test](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L5179-L5183),
[joined-table security test](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L5185-L5213), and
[bounded-page gate](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L6080-L6086).
The base permission hook selects document IDs from the collection's permissions side table where
a permission matches a requester role and the requested action, with bound parameters and, under
shared tables, a tenant filter on that table; it returns `1 = 0` for an empty role list. Postgres
overrides it with OR-ed JSONB containment tests for action-wrapped roles on each row's permissions
column, also returning `1 = 0` for an empty role list. The side table's name comes from
`Storage::permissionsTable()`, which was not read; code comments call it the `_perms` side table.
See the
[permission hook construction](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L3658-L3678),
[base permission filter](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL/Hook/Permission/Filter.php#L72-L116), and
[Postgres override](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Postgres.php#L1909-L1958).

This guide's reasoning from the cited 10.1.0 SQL code is that, with authorization enabled, SQL
`find` filters the main collection's rows by document permissions only for a collection with
`documentSecurity` enabled or the metadata collection, and not for a granted collection on a join
or bounded-page path. It also filters each joined table unless the collection's join
document-security map disables that table. Disabled authorization omits those filters, while
query conditions, ordering and pagination remain.
Whether a collection grant still makes Database-level `find` run with authorization disabled, as at
7.3.9, is not established at 10.1.0, since the dispatch was not read.
These are source-based conclusions, not a live authorization demonstration.

At 10.1.0, Mongo, Memory, Redis and Pool also extend `Adapter`; see the
[Mongo](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Mongo.php#L57),
[Memory](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Memory.php#L36-L48), and
[Redis](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Redis.php#L41-L57) class declarations and the
[Pool class and delegation](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Pool.php#L36-L138).
Memory and Redis are declared in the `Utopia\Database\Adapter` namespace and import
`Utopia\Database\Adapter`, so both extend `Utopia\Database\Adapter`; see the
[Memory namespace and import](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Memory.php#L3-L5) and
[Redis namespace and import](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Redis.php#L5-L8).
Mongo `getDocument` filters on `_uid`, applies its tenant hook and returns the first match; its
method contains no shared-authorization status check or permission filter. Mongo `find` builds
query filters and passes them through its tenant hook and then a `Hook\Mongo\Permission` hook built
on the shared authorization instance. That hook's code was not read, so at 10.1.0 its status gate
and the permission strings it matches are not established. See the
[Mongo document fetch](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Mongo.php#L1561-L1603),
[Mongo find filters](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Mongo.php#L2402-L2413), and
[Mongo read hooks](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Mongo.php#L249-L282).

Memory's class comment calls it an "In-process drop-in for the SQL adapters" and says it is
"Intended for tests, fixtures, and ephemeral workloads"; Redis's calls it an adapter "mirroring
the Memory adapter's surface". Neither `getDocument` method contains a shared-authorization status
check or permission filter; Redis `getDocument` also returns an empty document when a
shared-tables row belongs to another tenant. In `find`, only while the shared authorization status
is enabled, Memory keeps documents whose indexed permissions for the requested action name a
requester role, and Redis keeps IDs found in its per-action sets for the requester's roles,
keeping none for an empty role list. Unlike SQL `find`, neither permission step tests
`documentSecurity`. See the
[Memory document fetch](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Memory.php#L1204-L1227),
[Memory find](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Memory.php#L1807-L1836),
[Memory find filter](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Memory.php#L2397-L2452),
[Memory permission allow set](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Memory.php#L3108-L3141),
[Redis document fetch](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Redis.php#L882-L916),
[Redis find](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Redis.php#L1482-L1519),
[Redis find permission step](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Redis.php#L2809-L2823), and
[Redis permission filter](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Redis.php#L1938-L1973).

Pool `getDocument` and `find` delegate to a pooled adapter. Before each delegated call, including
calls on the adapter it pins for a transaction, Pool sets that adapter's database, namespace,
shared-tables mode, tenant, tenant-per-document mode, authorization and locks from its own state.
Pool's `setAuthorization` stores the instance it receives, and `withTransaction` sets the same
state on an adapter before pinning it for the transaction's calls. See the
[Pool state sync](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Pool.php#L178-L186),
[Pool document read delegation](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Pool.php#L802-L807),
[Pool find delegation](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Pool.php#L884-L889),
[Pool authorization setter](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Pool.php#L1101-L1106), and
[Pool transaction pinning](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Pool.php#L517-L541).
This guide's reasoning from these lines and the cited authorization handoff is that a Pool-wrapped
adapter runs its own `getDocument` and `find` code above with the authorization instance the
database set. It also reasons that Memory and Redis `getDocument` add no document-permission
filter, and that disabled status omits their `find` permission filters as it omits the SQL one.
Whether a collection grant omits them, and the Mongo `find` filter, are not established at 10.1.0.
These are source-based conclusions, not a live authorization demonstration.

In Appwrite 2.7.0, `_APP_DB_ADAPTER` selects the main database: the pinned variables give it
introduction version 1.9.0, default `postgresql`, the description "Must be one of: PostgreSQL,
MariaDB, or MongoDB" and the question choices `postgresql|mariadb|mongodb`. The pool registration
falls back to `postgresql` when the variable is unset, accepts the `mariadb`, `mongodb`, `mysql`
and `postgresql` schemes for its `console` and `database` connections, and maps them to the
MariaDB, Mongo, MySQL and Postgres adapters; DocumentsDB connections accept only `mongodb`, and
the mapping names no Memory, Redis or SQLite adapter. See the
[pinned variables](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/config/variables.php),
[pool DSN fallbacks and connections](https://github.com/appwrite/appwrite/blob/2.7.0/app/init/registers.php#L45-L99), and
[adapter mapping](https://github.com/appwrite/appwrite/blob/2.7.0/app/init/registers.php#L239-L252).
The 2.7.0 database factory imports utopia-php's `Utopia\Database\Adapter\Pool` as `DatabasePool`
and wraps the connection pool named by a DSN host in it; its `tenant` method sets the shared
authorization instance on the database it builds and turns on `setCheckGrants(true)`. The 10.1.0
docblock says that setting makes a related document given as a document to the write methods it
lists, while authorization is enabled, "only add permissions for roles the caller holds", that
`updateDocuments()` then refuses such a document, and that `createDocuments()` and the upsert
methods read its existing permissions without a lock. Without a transaction ID, the
document GET handler cited above fetches through `getDatabasesDB`, which builds its database with
that `tenant` method from the database document's DSN, or the project's when that is empty; at
2.7.0 it also adds `Metadata` and `Joins` hooks, whose effect is not traced here. With a
transaction ID, the 2.7.0 handler first reads the `transactions` document, inside `skip` for
API-key or privileged requesters and under the requester's authorization otherwise, and reports a
key or privileged requester's empty result as not found. It then calls the transaction state's
`getDocument`; the request resources build that state from the project database, the request's
`authorization` resource, the same `getDatabasesDB` and the request's user, and give the database
factory that `authorization` resource too. As source reading of 2.7.0 without a run, the state is
replayed from the transaction's `transactionLogs` entries, plus any pending operations, only when
its `transactions` document exists with status `pending`. The state reads that document inside
`skip` only for API-key or privileged requesters and reads the logs inside `skip`; its code comment
says "Staged operations are only visible to the transaction owner, API keys and privileged users."
Whether a `transactions` document's permissions limit an ordinary requester to its creator is not
established here. A document staged for deletion yields an empty document, which the handler
reports as not found, and one staged for creation is returned from the staged state itself. For a
staged update or upsert, the committed document is fetched through the database layer and the
staged state is merged over it; if that fetch is empty, an upsert returns the staged document,
while an update falls through to a second committed fetch, as does a document with no staged
state. This guide's reasoning from these lines is that staged creates bypass database-layer
retrieval, and that when a committed fetch returns empty, the upsert branch returns the staged
document without another database-layer read. The 2.7.0 handler no longer calls
`processDocument`; its parent class's `stampTransactionRead` and `isTransactionTypeMismatch`
helpers and any other layer are not traced. See the
[factory Pool import](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Database/Factory.php#L12),
[factory Pool wrapping](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Database/Factory.php#L208-L211),
[tenant database construction](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Database/Factory.php#L123-L201),
[grant checking](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Database.php#L1162-L1183),
[getDatabasesDB resource](https://github.com/appwrite/appwrite/blob/2.7.0/app/init/resources/request.php#L1112-L1159),
[document GET transaction branch](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Get.php#L109-L124),
[document GET not-found response](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Get.php#L134-L136),
[transaction-state staged creation](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Databases/TransactionState.php#L92-L94),
[transaction-state document branches](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Databases/TransactionState.php#L70-L108),
[transaction and log reads](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Databases/TransactionState.php#L675-L706),
[transaction-state resource](https://github.com/appwrite/appwrite/blob/2.7.0/app/init/resources/request.php#L1161-L1165), and
[factory authorization resource](https://github.com/appwrite/appwrite/blob/2.7.0/app/init/resources/request.php#L234-L238).

The repository's development `.env` (`_APP_ENV=development`) sets `_APP_DB_ADAPTER=postgresql`;
that is a development default, not a production default. The repository's root Compose file,
which the 2.7.0 install task reads as its Compose template, passes `_APP_DB_ADAPTER` to the
`appwrite` service without a value and defines `mariadb`, `mongodb` and `postgresql` services.
The 2.7.0 upgrade task keeps an installation's existing engine and, when neither its Compose
services nor its `.env` set `_APP_DB_ADAPTER`, assumes MariaDB, commenting "Pre-1.9.0
installations only supported MariaDB". It then passes that engine to the install task, whose own
detection, described below, runs as well and can replace the assumed MariaDB with a `mongodb` or
`postgresql` service name, or an `_APP_DB_HOST` value naming one, found in the Compose file. See the
[pinned development environment](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/.env),
[pinned root Compose file](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/docker-compose.yml),
[install task Compose template](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L563-L568),
[install task Compose rendering](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L664-L671),
[upgrade engine detection](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Upgrade.php#L73-L98), and
[upgrade hand-off to the install task](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Upgrade.php#L108-L110).

As source reading of 2.7.0 without an Appwrite run, the console variables endpoint reports
`_APP_DB_ADAPTER` with its own fallback, `mariadb`, through a response model whose rule for the
field also defaults to `mariadb` and describes it as "Database adapter in use", while the pool
registration, cited above as the pool DSN fallbacks and connections, falls back to `postgresql`. A
deployment that leaves the variable unset therefore gets Postgres `console` and `database` pools
while that endpoint reports `mariadb`; where the variable is set, the endpoint and the pool
registration read the same value, so for a value that registration accepts, the endpoint reports
the scheme those pools use. At 2.7.0, `packages/system/src/System.php` in the Appwrite tree
declares `Utopia\System\System`, whose `getEnv` returns `getenv($name) ?: $default`. The 2.3.0
release notes list `system` among Utopia libraries that "now live in `packages/` and load
directly", and the 2.7.0 `composer.lock` has no utopia-php/system package entry. This guide infers
that this in-tree class is the one 2.7.0 loads, so an empty value takes the same fallback as an
unset one in the endpoint's and the pool registration's `System::getEnv` calls; Appwrite's
`composer.json` was not read. What the filters for an older response format do to the field is
not traced here. As source reading of 2.7.0, the install task starts the
web installer and returns when its `interactive` parameter is `Y`, the console is interactive and
no command-line argument starts with `--`; otherwise it takes its command-line path. In that path
it sets the variable from an interactive answer, a question it skips when it finds an existing
Compose file, or else from the database it selects, which is the `database` parameter (default
`postgresql`) unless an existing installation's detected database replaces it, and writes it to
`.env` unless it reuses an existing configuration. It detects that database from the first Compose
service setting `_APP_DB_ADAPTER`, then from `.env`, then from a `mariadb`, `mongodb` or
`postgresql` service name, checked in that order, then from a service's `_APP_DB_HOST` naming one of
those. Unless its `no-start` parameter is set, it then runs `docker compose` with `--env-file`
naming its environment file, assigning each nonempty prepared value, this variable included, in
the command's environment unless it reuses an existing configuration. The web installer and the
Compose generator are traced below, but how Compose resolves the template's value-less
`_APP_DB_ADAPTER` entry from that `--env-file` and environment, or in a later `docker compose up -d`
run by hand, is not established here, so whether a given installation passes the value to its
`appwrite` service is still not established. This guide's assessment: do not
rely on the `_APP_DB_ADAPTER` value the console reports to identify which adapter a 2.7.0
deployment uses, because a reported `mariadb` can be that fallback over Postgres pools; check
whether the variable is set in the `appwrite` service's environment, and to what, instead. See the
[console variables adapter fallback](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Console/Http/Variables/Get.php#L118),
[console variables response model adapter rule](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Utopia/Response/Model/ConsoleVariables.php#L130-L138),
[install task database parameter](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L81),
[install task detected-database override](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L234-L239),
[install task interactive database answer](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L299-L307),
[install task adapter assignment](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L318-L319),
[install task existing-configuration check](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L550-L555),
[install task Compose and environment writes](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L708-L721), and
[install environment template](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/views/install/env.phtml).
For the empty-value fallback, see the
[packages/system getEnv fallback](https://github.com/appwrite/appwrite/blob/2.7.0/packages/system/src/System.php#L703-L706) and the
[2.3.0 release notes](https://github.com/appwrite/appwrite/releases/tag/2.3.0).
For the web-installer branch, existing-database detection and container start, see the
[install task web-installer branch](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L253-L262),
[install task explicit-parameter check](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L1694-L1703),
[install task existing-database detection order](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L214-L233),
[install task database service and host detection](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L1709-L1728),
[install task container start condition](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L767-L773), and
[install task Compose start](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L1316-L1377).

As source reading of the 2.7.0 web installer without a run, its first step offers PostgreSQL,
MariaDB and MongoDB, each only when enabled, as radio choices. It preselects a locked database or
else the `_APP_DB_ADAPTER` variable's default as the install task passes it, which is `postgresql`
unless the task replaced it for an existing installation, and disables the other choices when one
is locked. The page's script posts the choice as `database`, falling back to `postgresql`. The
install handler accepts only those three values, requires an unlocked choice to be a supported and
enabled database, and sets `_APP_DB_ADAPTER` to the locked database or else the choice. For a
request without a retry step whose installation already has progress steps recorded, the handler
deletes the progress file of an earlier run that ended in error or completed every step, so the
request starts fresh, and otherwise sets the installer lock to an error status and answers
"Installation already started" (409, or an error event on a stream) before any comparison. When a
resumed installation has a saved payload and the earlier run recorded no error, the handler
compares the stored fields with the request and refuses a mismatch, such as a nonempty posted
`database` that differs from a stored `database`, by setting the installer lock to an error status
and answering "Installation payload mismatch". If every check passes, the handler sets
`_APP_DB_ADAPTER` to the locked database, else the stored `database` if present, else the value
the handler set before the comparison; after an earlier error, or with no saved payload, the
handler skips the comparison and keeps that earlier value. The install task's environment
preparation keeps the handler's nonempty
`_APP_DB_ADAPTER` value and sets the database host and port to match it, and the
installation then passes it to the Compose generator and to the environment template as described
above. When the installer server finds an existing Compose or environment file and has no locked
database, it locks one detected from database service or container names in the Compose file's
text, then from `_APP_DB_ADAPTER` or `_APP_DB_HOST` in the environment file. See the
[web installer database default and lock](https://github.com/appwrite/appwrite/blob/2.7.0/app/views/install/installer/templates/steps/step-1.phtml#L11-L20),
[web installer database choices](https://github.com/appwrite/appwrite/blob/2.7.0/app/views/install/installer/templates/steps/step-1.phtml#L66-L108),
[web installer default database variable](https://github.com/appwrite/appwrite/blob/2.7.0/app/views/install/installer.phtml#L12),
[web installer view database settings](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/View.php#L42-L48), and
[web installer posted database fallback](https://github.com/appwrite/appwrite/blob/2.7.0/app/views/install/installer/js/modules/progress.js#L408).
For the install handler, see the
[web installer database parameter](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L46),
[web installer database validation](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L150-L161),
[web installer supported database values](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Runtime/State.php#L204-L206),
[web installer database adapter input](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L238-L246),
[web installer resumed progress check](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L202-L225),
[web installer resumed payload comparison](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L248-L285),
[web installer resumed database input](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L313),
[web installer environment preparation](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L320-L322), and
[web installer installation call](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L380-L394).
For the install task and installer server, see the
[install task web installer configuration](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L337-L374),
[install task existing-installation defaults](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L156-L191),
[install task user input and database host](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L440-L473),
[installer server upgrade and database lock detection](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Server.php#L225-L257), and
[installer server database detection from files](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Server.php#L277-L315).

As source reading of 2.7.0, the Compose generator replaces a `database` value other than
`postgresql`, `mariadb` or `mongodb` with `postgresql`, removes the other two database services and
their volumes, and replaces dependencies on any database service or on `${_APP_DB_HOST:-postgresql}`
with one dependency on the selected service, under the condition `service_healthy`. Its code never
refers to a service's `environment` or to `_APP_DB_ADAPTER`, so this guide reasons that the
rendered Compose file keeps the template's value-less `_APP_DB_ADAPTER` entry; no rendered file was
observed. When the install task reads an existing Compose file, `Appwrite\Docker\Compose` wraps each
service in a `Service`, which joins its `environment` list with newlines and parses the result with
`Env`, and `Env` skips a line that has no `=`. A value-less `_APP_DB_ADAPTER` entry therefore yields
no key, so the install task's first detection step, which tests `isset` on that key, does not match
it, and detection moves on to `.env`. See the
[Compose generator](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/src/Appwrite/Docker/Compose/Generator.php),
[generator selectable database services and volumes](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose/Generator.php#L9-L26),
[generator database dependency selector](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose/Generator.php#L71-L81),
[generator parameter normalization](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose/Generator.php#L145-L153),
[generator service filter](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose/Generator.php#L188-L210),
[generator volume filter](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose/Generator.php#L263-L278),
[generator dependency rewrite](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose/Generator.php#L283-L333),
[Compose services](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose.php#L16-L27),
[Compose service environment parsing](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose/Service.php#L32-L33), and
[environment parser lines without an assignment](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Env.php#L37-L42).

There is a documentation/source conflict: the environment documentation as served on 2026-11-04
says "Appwrite supports MariaDB and MongoDB as database backends" and gives
`_APP_DB_ADAPTER` the default `mongodb` with possible values `mongodb` and `mariadb`, while
2.7.0 defaults to `postgresql`, which that page does not list. See the
[environment reference](https://appwrite.io/docs/advanced/self-hosting/configuration/environment-variables).

This guide's reasoning from these Appwrite and utopia-php lines is that, on its non-transaction
retrieval path, the cited 2.7.0 document GET reads through Pool over whichever MariaDB, MySQL,
Postgres or Mongo adapter its connection's DSN scheme selects. Its transaction-state path, traced
above, by the same reasoning makes its committed fetches the same way and returns staged documents
from the transaction's logs. Which adapter a given deployment uses depends on its own environment,
DSNs and installation history and is not established here, and neither is how Compose resolves the
value-less `_APP_DB_ADAPTER` entry. Those deployment and Compose gaps, and the transaction-state
layers left untraced above, stay open in SELFHOSTED-BACKEND-SOURCE-1; this guide does not claim complete
pinned-source verification or a live authorization demonstration.

Properly scoped server API keys **bypass resource permissions**. A successful server-key test
does not establish that an ordinary user is authorized. Scopes are selected per key and still
restrict which API operations that key can perform. At 2.7.0 every key also holds the `public`
scope, which the 2.7.0 release notes describe as letting "API keys call `public` scope endpoints".
See the
[pinned key and scope checks](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/controllers/shared/api.php).

Project API keys are scoped rather than all-or-nothing; grant only the scopes a given key needs,
and treat any key with `keys.write` as equivalent to an admin credential. The served API keys
page says "An API key with `keys.write` can change the scopes of existing keys and delete them." Keys are
meant for server SDKs and CLI use, never for client-side code; store them the way
[secrets.md](secrets.md) describes, not in the repository or the client bundle.
See [project API keys](https://appwrite.io/docs/partners/project/api-keys).

The same page, as served on 2026-11-04, says "Creating API keys with the Project API is deprecated
as of 17 August 2026. Create long-lived keys in the Appwrite Console. The Project API can list,
update, and delete existing keys, and can issue ephemeral keys for short-lived access." The 2.3.0
to 2.7.0 release notes do not mention that date; the page links a changelog entry for 2026-08-17,
which was not read here.

Releases since 2.6.2 also limit what a key can grant, which the served API keys page does not
reflect as of 2026-11-04. The 2.6.2 release notes say "A key can no longer create or change a key
with scopes it doesn't hold or an expiry later than its own". The 2.7.0 release notes say "a key
that configures a function or site can only add scopes it holds itself", and the 2.7.0 function
create handler refuses such a key with "An API key cannot grant scopes it does not hold." This
guide reads these sources as meaning that a key with `keys.write` cannot give another key a scope
it lacks; the 2.7.0 key handlers themselves were not read, so their scope and expiry checks are
not established at 2.7.0, and this guide still treats such a key as equivalent to an admin
credential. See the
[2.6.2 release notes](https://github.com/appwrite/appwrite/releases/tag/2.6.2),
[2.7.0 release notes](https://github.com/appwrite/appwrite/releases/tag/2.7.0) and
[function options](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/src/Appwrite/Platform/Modules/Functions/Http/Functions/Create.php).

### 4. Replace encryption secrets and make recoverable backups

Set a unique `_APP_OPENSSL_KEY_V1` **before storing production data**. At 2.7.0 its configuration
default is empty, and a fresh install generates it: the install task passes every `token` variable
except `_APP_JOBS_SECRET` through `EncryptionKey::resolve`, which replaces an empty or
`your-secret-key` value only when secrets are generated, which is for neither an existing
installation nor an upgrade. It passes `_APP_JOBS_SECRET`, also a `token` variable, through
`JobsSecret::resolve`, which takes no generation flag and replaces such a value whether or not
secrets are generated. The 2.4.0
release notes say "Fresh installs generate `_APP_OPENSSL_KEY_V1` instead of using
`your-secret-key`. Upgrades keep the existing key." An upgraded installation can therefore still
hold the placeholder, and the repository's development `.env` still ships it, so replace a
placeholder wherever you find it. The 2.7.0 variable description says "Production refuses to start
when this is empty"; where that is enforced was not traced here. As of 2026-11-04 the served
environment reference still says the variable "is not set by default" and does not mention the
generated value. The served security page, as of 2026-11-04, says "Appwrite does not generate a
unique encryption key during a default setup.", which contradicts the key that a fresh 2.7.0
install generates. Inject the real value from protected deployment configuration:

```text
_APP_OPENSSL_KEY_V1=REPLACE_WITH_UNIQUE_ENCRYPTION_SECRET
```

See the [pinned default](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/config/variables.php),
[key resolution](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Auth/EncryptionKey.php#L11-L69),
[jobs secret resolution](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Auth/JobsSecret.php#L20-L32),
[install task secret generation](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L440-L473),
[generation condition](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L331),
[2.4.0 release notes](https://github.com/appwrite/appwrite/releases/tag/2.4.0)
and [encryption guidance](https://appwrite.io/docs/advanced/self-hosting/production/security).

Back up the exact key separately from ordinary data backups and restrict access to both.
Changing or losing it strands previously encrypted secrets. Back up the database, persistent
storage, and deployment configuration, and test restoration in a separate installation. See
[self-hosted backups](https://appwrite.io/docs/advanced/self-hosting/production/backups).

Appwrite 2.7.0 adds server key rotation, which the served security and backups pages do not
reflect as of 2026-11-04; both name only `_APP_OPENSSL_KEY_V1`. The 2.7.0 release notes say
"`_APP_OPENSSL_KEY_CURRENT` picks the `_APP_OPENSSL_KEY_V{n}` that signs new tokens and encrypts
new data", that "Stored values keep decrypting with the version they record", and that "The new
`encryption` task re-encrypts stored data under the current version". Their upgrade notes add
"Files already encrypted in storage are not re-encrypted, so keep `_APP_OPENSSL_KEY_V1`
configured." Rotate only by that procedure, and back up every key version that still decrypts
stored data or files. The served environment reference does list the 2.7.0 key-version variables.
See the [2.7.0 release notes](https://github.com/appwrite/appwrite/releases/tag/2.7.0),
[key resolution](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Auth/EncryptionKey.php#L11-L69)
and [pinned variables](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/config/variables.php).

### 5. Keep abuse protection enabled and configure SMTP

Set `_APP_OPTIONS_ABUSE=enabled`. This is the configuration default, but the repository's
development `.env` overrides it to `disabled`. Server API-key requests and requests with the
`owner`, `developer` or `admin` role are exempt, so test client rate limiting as an ordinary client
without a server key. See the
[pinned abuse check](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/controllers/shared/api.php)
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
[pinned SMTP variables](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/config/variables.php)
and [email configuration](https://appwrite.io/docs/advanced/self-hosting/configuration/email).

### 6. Constrain uploads and function execution

The server storage defaults are `_APP_STORAGE_DEVICE=local`,
`_APP_STORAGE_LIMIT=30000000`, and `_APP_STORAGE_ANTIVIRUS=disabled`. Enabling antivirus with
`_APP_STORAGE_ANTIVIRUS=enabled` requires a reachable ClamAV service; configure its host and
port for the deployment. See the
[pinned storage variables](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/config/variables.php).

New buckets have empty permissions and `fileSecurity=false`. Enable file security when using
individual-file grants, and keep bucket permissions narrow: a bucket-level grant also permits
access. Bucket `encryption` and `antivirus` default to `true`, but that antivirus option does
not enable the server-wide scanner. See the
[bucket defaults](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/src/Appwrite/Platform/Modules/Storage/Http/Buckets/Create.php).

Encryption and antivirus are skipped for files **above 20,000,000 bytes**, even with their bucket
options enabled. If either is mandatory, set bucket `maximumFileSize` to no more than
`20000000`, enable the relevant controls, and test the boundary. The default server upload limit
is larger than this threshold. See the
[bucket option semantics](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/src/Appwrite/Platform/Modules/Storage/Http/Buckets/Create.php)
and [size constants](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/init/constants.php).

For functions, `execute` roles and the `scopes` for API keys generated for executions both
default to `[]`. Grant execution only to intended callers and grant the execution key only
the API scopes its code needs. Setting `enabled=false` blocks ordinary callers but does not
block authorized Server SDK API keys. See the
[function options](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/src/Appwrite/Platform/Modules/Functions/Http/Functions/Create.php).

Keep the executor and orchestrator private. The pinned Compose stack mounts the Docker socket
into these services, giving their control plane significant host authority. It also mounts the
socket into the `traefik` service, which publishes the HTTP and HTTPS ports. At 2.7.0
`_APP_EXECUTOR_SECRET` keeps the default `your-secret-key` but is a `token` variable, so by the
same `EncryptionKey::resolve` call as the encryption key a fresh install replaces that placeholder with a
generated value, while an existing or upgraded installation keeps its stored value. The 2.6.2
release notes say "Install generates the executor secret". As of 2026-11-04 the served environment
reference still says "Make sure to change this!" and does not mention the generated value. Replace
any remaining `_APP_EXECUTOR_SECRET` placeholder with a unique protected value:

```text
_APP_EXECUTOR_SECRET=REPLACE_WITH_UNIQUE_EXECUTOR_SECRET
```

Container execution is not demonstrated isolation for mutually hostile tenants. Treat deployment
and execution-control credentials as privileged, and review workload isolation separately.
See the [Compose services](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/docker-compose.yml),
[pinned variables](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/config/variables.php),
[install task secret generation](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L440-L473),
[2.6.2 release notes](https://github.com/appwrite/appwrite/releases/tag/2.6.2)
and [executor configuration](https://appwrite.io/docs/advanced/self-hosting/configuration/environment-variables).

## Verify

REASONED: this historical environment account is not a new host inventory; a live PocketBase or Appwrite stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. All three Verify shell blocks passed bash -n and ShellCheck 0.11.0 with exit 0 and no output. With curl and grep stubbed, written and embedded placeholders, example.com, angle brackets, empty values, and omitted or shortened set -- lines printed their refusal messages without invoking either stub. The bash -n, ShellCheck and stub runs recorded here covered all three Verify shell blocks in an earlier form, whose guard refusals left the subshell with status 0 and whose scan block result arms ended with status 0, and the stub runs were not repeated on the current forms. In the current forms guard refusals leave the subshell with status 2, the GET and registration blocks exit 3 when curl fails, the registration block exits 1 when the registration returns 201, the scan block's FAIL and scan-failure arms exit 1 and 3, and the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover all three blocks. Live public-to-restricted record comparisons remain unobserved: guests can read public records, while restricted records deny or filter unauthorized reads and preserve permitted access, per the guide’s cited PocketBase API rules and filters (rolling documentation, checked November 2026) and Appwrite legacy collection/document permissions (rolling documentation, checked November 2026). The following sentences record the earlier authoring environment: The live checks below are **reasoned, not demonstrated**. This authoring environment has no
PocketBase executable or container runtime, no writable service installation, and no supplied
deployment, accounts, SMTP service, or second-host ingress fixture. Shell network access also
failed. No available authorized environment could reproduce the live exposed and fixed states.

REASONED: disposable-fixture comparison procedure; a live PocketBase or Appwrite stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. The GET block passed bash -n and ShellCheck 0.11.0 with exit 0 and no output; under bash -u, written and embedded placeholders, example.com, angle brackets, empty values, omitted or shortened set -- lines, HTTP, query, fragment, userinfo, and a control character printed refusal messages without invoking the curl stub. A valid fixture printed CURL_STUB arguments including --header @- and STDIN Authorization: DUMMY_TOKEN; the dummy header did not occur in those arguments. The bash -n, ShellCheck and stub runs recorded here covered the GET block in an earlier form, whose guard refusals left the subshell with status 0, and the stub runs were not repeated on the current form, whose guard refusals leave the subshell with status 2 and which exits 3 when curl fails; the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover it. The local stub does not establish application authorization: public records admit guests, while fixed rules deny or filter unauthorized access and retain authorized access, per the guide’s cited PocketBase API rules and filters (rolling documentation, checked November 2026) and Appwrite legacy collection/document permissions (rolling documentation, checked November 2026). Use disposable data on a private fixture to establish exposed behavior, then repeat through
the deployed endpoints after hardening. Record response bodies, authorization identities, and
positive controls. A timeout, malformed request, nonexistent resource, or unrelated proxy error
does not establish application authorization.

REASONED: console-origin and API selection; a live PocketBase or Appwrite stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. The signup JSON parsed as four expected string fields. The registration block passed bash -n and ShellCheck 0.11.0 with exit 0 and no output; under bash -u, written and embedded placeholders, example.com, angle brackets, empty values, omitted or shortened set -- lines, HTTP, query, fragment, userinfo, and a control character printed refusal messages without invoking the curl stub. A valid fixture printed CURL_STUB arguments ending in https://console.internal/v1/account and STDIN containing the JSON; the password field did not occur in those arguments. The bash -n, ShellCheck and stub runs recorded here covered the registration block in an earlier form, whose guard refusals left the subshell with status 0, and the stub runs were not repeated on the current form, whose guard refusals leave the subshell with status 2 and which exits 1 for a 201 and 3 when curl fails; the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover it. Expected bootstrap access is private operator creation, not proof from static dashboard assets; Appwrite console account creation must fail after root-only bootstrap, per the guide’s cited PocketBase v0.41.1 installer and bootstrap-token lifetime and Appwrite 2.7.0 Compose console URL, persistent volumes, and Docker socket mounts and Appwrite 2.7.0 console registration handler. The former `curl -I` checks are insufficient: HEAD cannot inspect signup controls, PocketBase
serves static `/_/` assets, and since 2.3.0 Appwrite builds console links from `_APP_CONSOLE_URL`,
which 2.7.0 Compose passes without a value, and has dropped the legacy `/console/...` link shapes, so
a `/console` path is deployment-dependent. Use the actual console origin and API endpoints below.
See the [PocketBase installer](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/installer.go?rev=v0.41.1),
[Appwrite Compose configuration](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/docker-compose.yml)
and [Appwrite 2.3.0 release notes](https://github.com/appwrite/appwrite/releases/tag/2.3.0).

### 1. Test resource authorization with denied and allowed identities

**REASONED:** Requires the unavailable live backend and controlled accounts described above.
Use this GET block for each resource comparison below. Put request headers in an owner-readable
file outside the client bundle; use an empty file for a PocketBase guest. PocketBase uses
`Authorization: REPLACE_WITH_USER_TOKEN`. Appwrite uses
`X-Appwrite-Project: REPLACE_WITH_PROJECT_ID` plus the intended end-user session header or cookie.
Use a separate protected header file for each identity, and confirm that identity works on an
allowed resource before accepting its denial elsewhere.

REASONED: substitution and protected-header handling for the GET procedure; live backend fixtures and controlled accounts remain unavailable; a live PocketBase or Appwrite stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. The GET block passed bash -n and ShellCheck 0.11.0 with exit 0 and no output; under bash -u, written and embedded placeholders, example.com, angle brackets, empty values, omitted or shortened set -- lines, HTTP, query, fragment, userinfo, and a control character printed refusal messages without invoking the curl stub. A valid fixture printed CURL_STUB arguments including --header @- and STDIN Authorization: DUMMY_TOKEN; the dummy header did not occur in those arguments. The bash -n, ShellCheck and stub runs recorded here covered the GET block in an earlier form, whose guard refusals left the subshell with status 0, and the stub runs were not repeated on the current form, whose guard refusals leave the subshell with status 2 and which exits 3 when curl fails; the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover it. Expected public guest reads become denied or filtered after restrictive rules, with authorized-user positive controls, per the guide’s cited PocketBase API rules and filters (rolling documentation, checked November 2026) and Appwrite legacy collection/document permissions (rolling documentation, checked November 2026) and curl curl-8_14_1 headers from stdin (checked October 2026). Substitute inside the single quotes and paste whole blocks. Do not paste literal apostrophes
inside those quotes. The guards assume ordinary shell builtins. The headers reach curl from a
file on its stdin and this block never expands their contents, so they stay out of curl's
arguments, shell history and `set -x` tracing. The file's permissions and how it was prepared
remain exposures, as does the same account or root reading the file or viewing the process.
Never place a token-bearing URL in this block.

REASONED: following block; resource and scope comparisons follow the cited vendor documentation and available pins; live backend fixtures and controlled accounts were unavailable.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'https://REPLACE_WITH_BACKEND/REPLACE_WITH_RESOURCE_PATH' 'REPLACE_WITH_PROTECTED_HEADERS_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[[:cntrl:]]*|*'@'*|*'?'*|*'#'*)
      echo "substitute an unsigned HTTPS resource URL; not probing"; exit 2 ;;
    https://*)
      case "$2" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[[:cntrl:]]*)
          echo "substitute the protected headers file path; not probing"; exit 2 ;;
        *)
          [ -f "$2" ] || { echo "the protected headers file is not a readable file; not probing"; exit 2; }
          [ -r "$2" ] || { echo "the protected headers file is not a readable file; not probing"; exit 2; }
          if curl -q -g -sS --noproxy '*' --proto '=https' \
            --connect-timeout 5 --max-time 20 --header @- \
            -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
            "$1" < "$2"; then
            echo "unclassified observation: judge the status and body above against the comparison you are running, for the identity in this headers file"
          else
            echo "curl exit $?: the request failed; inconclusive"; exit 3
          fi ;;
      esac ;;
    *) echo "use HTTPS; not probing"; exit 2 ;;
  esac
)
```

| Check | Exposed and fixed comparison |
| --- | --- |
| PocketBase record rules | **REASONED:** On the private fixture, request `/api/collections/REPLACE_WITH_COLLECTION/records` and `/api/collections/REPLACE_WITH_COLLECTION/records/REPLACE_WITH_RECORD`. Public empty rules allow guest reads. Locked rules return 403 to non-superusers. Restrictive rules must return only authorized records: an unsatisfied list filter can return 200 with empty `items`, while an unsatisfied view rule returns 404. Confirm the authorized ordinary user receives the known fixture record; separately confirm a superuser bypasses record rules. See [rule outcomes](https://pocketbase.io/docs/api-rules-and-filters/). |
| Appwrite document permissions | **REASONED:** Request `/v1/databases/REPLACE_WITH_DATABASE/collections/REPLACE_WITH_COLLECTION/documents/REPLACE_WITH_DOCUMENT`. With document security explicitly enabled, first demonstrate that a broad collection read grant allows an otherwise ungranted user. Remove that broad grant: the intended document grantee must still receive the fixture, while guests and an unrelated user receive no document data. Compare omitted permissions for client-created and server-created fixtures. See [additive permissions](https://appwrite.io/docs/products/databases/tablesdb/legacy/permissions) and [creation defaults](https://appwrite.io/docs/advanced/security/permissions). |
| Appwrite server-key scope | **REASONED:** Repeat the same document request from a trusted server using a protected API-key header file. A key with the required read scope can read despite empty resource permissions; a key lacking that scope must be refused. This is a separate test, never the positive control for an ordinary user's permissions. See [key authorization](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/controllers/shared/api.php). |

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

REASONED: the signup JSON structure in the block above, whose declaration is the paragraph before that block, and the protected-stdin request procedure in this paragraph for the following registration block, whose declaration is the paragraph after that block. No disposable Appwrite installation with a first console account and controlled signup fixture is available; a live Appwrite stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. The signup JSON parsed as four expected string fields. The registration block passed bash -n and ShellCheck 0.11.0 with exit 0 and no output; under bash -u, written and embedded placeholders, example.com, angle brackets, empty values, omitted or shortened set -- lines, HTTP, query, fragment, userinfo, and a control character printed refusal messages without invoking the curl stub. A valid fixture printed CURL_STUB arguments ending in https://console.internal/v1/account and STDIN containing the JSON; the password field did not occur in those arguments. The bash -n, ShellCheck and stub runs recorded here covered the registration block in an earlier form, whose guard refusals left the subshell with status 0, and the stub runs were not repeated on the current form, whose guard refusals leave the subshell with status 2 and which exits 1 for a 201 and 3 when curl fails; the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover it. Expected exposed registration returns 201; root-only registration after bootstrap rejects an additional account, per the guide’s cited Appwrite 2.7.0 console registration handler. The request can create an account on a misconfigured instance. Run it only on the disposable
fixture or an explicitly designated registration-test deployment. Use the API origin serving
the console project, not a guessed `/console` UI path. The block feeds the signup JSON, test
password included, to curl on stdin from the protected file: no password is typed into the command
or held in a shell variable, so neither shell history nor `set -x` tracing records it, provided the
file is prepared with an editor, not a shell command containing the password, which would enter
shell history. Stdin closes the argv channel only; the account owner and root can still read the
file and curl's memory. Console registration comparisons follow the pinned Appwrite handler; no disposable Appwrite installation or controlled signup fixture was available.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'https://REPLACE_WITH_CONSOLE_API_ORIGIN' 'REPLACE_WITH_PROTECTED_SIGNUP_JSON'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[[:cntrl:]]*|*'@'*|*'?'*|*'#'*)
      echo "substitute the console API HTTPS origin; not probing"; exit 2 ;;
    https://*)
      case "$2" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[[:cntrl:]]*)
          echo "substitute the protected signup JSON path; not probing"; exit 2 ;;
        *)
          [ -f "$2" ] || { echo "the protected signup JSON is not a readable file; not probing"; exit 2; }
          [ -r "$2" ] || { echo "the protected signup JSON is not a readable file; not probing"; exit 2; }
          set -- "$1" "$2" "$(if curl -q -g -sS --noproxy '*' --proto '=https' \
            --connect-timeout 5 --max-time 20 \
            --header 'X-Appwrite-Project: console' \
            --header 'Content-Type: application/json' \
            --data-binary @- \
            -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
            "${1%/}/v1/account" < "$2"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
          set -- "$1" "$2" "${3##*$'\n'}" "${3%$'\n'*}"   # curl's exit status, then its output
          printf '%s' "$4"
          case "$3:$4" in
            0:*'http=201 '*) echo "FINDING: the registration returned 201 and created an account, which is the finding once root-only registration is on"; exit 1 ;;
            0:*) echo "unclassified observation: read the error above; only the console-account-limit error shows the restriction, and a duplicate email or password-validation error does not" ;;
            *) echo "curl exit $3: the registration request failed; inconclusive"; exit 3 ;;
          esac ;;
      esac ;;
    *) echo "use HTTPS; not probing"; exit 2 ;;
  esac
)
```

REASONED: preceding block; the full registration request, guards, protected stdin, root-only and allowlist comparisons, and operator controls in this paragraph. No disposable Appwrite installation, controlled signup identities, source-IP fixture, or operator/invitation fixture is available; a live Appwrite stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. The signup JSON parsed as four expected string fields. The registration block passed bash -n and ShellCheck 0.11.0 with exit 0 and no output; under bash -u, written and embedded placeholders, example.com, angle brackets, empty values, omitted or shortened set -- lines, HTTP, query, fragment, userinfo, and a control character printed refusal messages without invoking the curl stub. A valid fixture printed CURL_STUB arguments ending in https://console.internal/v1/account and STDIN containing the JSON; the password field did not occur in those arguments. The bash -n, ShellCheck and stub runs recorded here covered the registration block in an earlier form, whose guard refusals left the subshell with status 0, and the stub runs were not repeated on the current form, whose guard refusals leave the subshell with status 2 and which exits 1 for a 201 and 3 when curl fails; the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover it. The exposed/fixed outcomes that follow are expectations, per the guide’s cited Appwrite 2.7.0 console registration handler. With root-only registration disabled and allowlists empty on the private fixture, a valid new
registration should return 201. After enabling root-only registration and recreating the stack,
an additional self-registration must fail with the console-account-limit error. A duplicate
email or password-validation error does not establish that restriction. Test email and IP
allowlists independently on a fresh private fixture: allowed bootstrap succeeds; an excluded
email or source IP receives its corresponding allowlist error. The registration block's exit status
classifies only the root-only comparison: in the allowlist comparison an allowed bootstrap's 201 is
the positive control, so there its FINDING line and status 1 show that control succeeding. Existing
operator login and intended invitation acceptance must still work. See the
[registration handler](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Account/Http/Account/Create.php#L109-L134).

**REASONED:** Requires an unavailable fresh PocketBase fixture. Submit a valid test-superuser
creation body to `POST /api/collections/_superusers/records`: a guest and an ordinary user's
token must not create a superuser. On the private bootstrap fixture, the valid installer token
must permit creating the operator. Confirm ordinary application-user registration never grants
that privilege. After bootstrap, use a clean browser to inspect the deployed dashboard and
exercise its API authorization; loading static assets is not evidence of administrative access.
See the [installer](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/installer.go?rev=v0.41.1)
and [record access checks](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/record_crud.go?rev=v0.41.1).

### 3. Exercise the remaining controls

REASONED: safe fixture and credential-transport procedure for the remaining-control comparisons; a live PocketBase or Appwrite stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Controlled service accounts, protected request files, and SDK fixtures for these live mutations are unavailable. The GET block passed bash -n and ShellCheck 0.11.0 with exit 0 and no output; under bash -u, written and embedded placeholders, example.com, angle brackets, empty values, omitted or shortened set -- lines, HTTP, query, fragment, userinfo, and a control character printed refusal messages without invoking the curl stub. A valid fixture printed CURL_STUB arguments including --header @- and STDIN Authorization: DUMMY_TOKEN; the dummy header did not occur in those arguments. The bash -n, ShellCheck and stub runs recorded here covered the GET block in an earlier form, whose guard refusals left the subshell with status 0, and the stub runs were not repeated on the current form, whose guard refusals leave the subshell with status 2 and which exits 3 when curl fails; the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover it. Public record actions should admit guests; locked or restrictive rules should reject unauthorized mutations while intended users succeed, per the guide’s cited PocketBase v0.41.1 record CRUD handlers and curl curl-8_14_1 headers from stdin (checked October 2026). Each comparison below requires the unavailable live fixture. Perform mutations only on disposable
records and functions. Send credentials and request bodies through protected files or the SDK,
never command arguments.

| Control | Required comparison |
| --- | --- |
| Appwrite console MFA | **REASONED:** Requires an unavailable live Appwrite console fixture and controlled operator account with a TOTP authenticator. Using the operator's session and `X-Appwrite-Project: console`, request `GET /v1/account` without an API key. With MFA disabled, password authentication permits this request. Enable MFA and verify the TOTP factor, then create a fresh password-only session: the same request must fail. As source reading of 2.7.0, the middleware throws `Exception::USER_MORE_FACTORS_REQUIRED` when a session holds fewer factors than the user's minimum, on routes outside its `mfa` group, and `GET /v1/account` is in the `api` and `account` groups. The error type string and status this produces are not established at 2.7.0, so record what the response returns. Complete the TOTP challenge in that session with a code not already redeemed, since 2.7.0 TOTP codes are single-use, and repeat the request: expect 200 with the operator's account data. See [console MFA](https://appwrite.io/docs/advanced/security/mfa), [MFA enforcement](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/controllers/shared/api.php), [account GET route groups](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Account/Http/Account/Get.php#L27-L30) and [single-use TOTP steps](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Auth/MFA/Challenge/TOTP.php#L30-L88). |
| PocketBase writes and management | **REASONED:** Exercise `POST /api/collections/REPLACE_WITH_COLLECTION/records`, then `PATCH` and `DELETE` on disposable record URLs, using valid bodies. Public rules expose the actions; locked or restrictive rules must deny unauthorized changes while intended users still succeed. Separately attempt changing another auth record's email, password, and `verified` field: locked `manageRule` must not grant privileged management; an explicitly authorized manager must succeed only where intended. Confirm collection configuration rejects `manageRule=""`. See [CRUD handlers](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/record_crud.go?rev=v0.41.1) and [management validation](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/collection_model_auth_options.go?rev=v0.41.1). |
| PocketBase protected files | **REASONED:** GET a known fixture file at `/api/files/REPLACE_WITH_COLLECTION/REPLACE_WITH_RECORD/REPLACE_WITH_FILENAME`. Before protection, its unsigned URL downloads despite locked record access. Enable Protected and a `viewRule` that permits the intended ordinary user but denies guests and an unrelated ordinary user. File-token issuance does not check access to a particular file: authenticated users can obtain tokens. Confirm the unrelated user's `pb.files.getToken()` succeeds, then GET the protected fixture using that user's token-bearing SDK URL: expect 404. The permitted user's `pb.files.getToken()` must also succeed, and GET with that user's token-bearing SDK URL must return the expected fixture bytes as a positive control. Separately, an unsigned guest GET of the same protected file must return 404. Use the SDK for signed URLs, or feed a protected curl configuration through stdin; that keeps the token-bearing URL out of curl's argv only. Prepare the file with an editor, not a shell command that contains the URL, which would put it in shell history and `set -x` tracing, and the account owner and root can still read the file and curl's memory. See [download checks](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/file.go?rev=v0.41.1). |
| PocketBase realtime | **REASONED:** Establish `GET /api/realtime`, then `POST /api/realtime` subscriptions for both `REPLACE_WITH_COLLECTION/*` and a specific fixture record. Change that record through an authorized writer. Public rules expose events; restrictive list/view rules must suppress unauthorized delivery while an authorized subscriber receives the same mutation. A `PB_CONNECT` event or subscription acknowledgement is insufficient. See [Realtime API](https://pocketbase.io/docs/api-realtime/). |
| PocketBase MFA, verification, and tokens | **REASONED:** Use `POST /api/collections/_superusers/auth-with-password`, followed by the OTP flow through `/request-otp` and `/auth-with-otp`. Without MFA, password authentication completes; with password, OTP, and MFA enabled, the first factor must not complete authentication, while the correct second factor does. For application users, compare password login for otherwise valid verified and unverified accounts with `authRule="verified = true"`. Retain a test token privately, clear the SDK auth store, and retry an allowed record request with the retained token: clearing local state alone must not revoke it. See [authentication flows](https://pocketbase.io/docs/authentication/) and [authRule option](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/collection_model_auth_options.go?rev=v0.41.1). |
| PocketBase IP and proxy boundary | **REASONED:** Repeat an authorized superuser resource GET from allowed and excluded source addresses. With no allowlist both can work; with the allowlist the excluded address must receive 403. Forged forwarded-IP headers must not change that result through the proxy. From a second host, test the actual backend address and port as well as the proxy: direct backend access must be blocked, while the permitted proxy route works. If the UI is private, separately test GET `/_/` from both networks. See [IP enforcement](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/middlewares.go?rev=v0.41.1) and [proxy settings](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/settings_model.go?rev=v0.41.1). |
| TLS, origins, and hostnames | **REASONED:** Request a known API resource over HTTP and HTTPS, and inspect the HTTPS certificate. Fixed deployments must redirect or reject HTTP while HTTPS remains usable. Test Appwrite function/site domains separately. Send the same Appwrite request with an unconfigured `Host`: disabled router protection can serve it; enabled protection must reject it while the configured host works. For PocketBase, compare browser requests from an allowed and disallowed origin; then repeat outside the browser to confirm CORS has not replaced record authorization. See [PocketBase serve flags](https://ganigeorgiev.com/pocketbase/pocketbase/files/cmd/serve.go?rev=v0.41.1) and [Appwrite routing](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/controllers/general.php). |
| Abuse and email delivery | **REASONED:** From a non-excluded ordinary client, send a bounded sequence of valid PocketBase authentication requests across the configured `*:auth` threshold. Disabled limiting should not produce limiter denials; enabled limiting should produce 429, with normal requests succeeding after the window. For Appwrite, cross a documented client endpoint's threshold without an API key or privileged session and compare disabled/enabled abuse protection. Separately request OTP, verification, and recovery messages and confirm receipt and successful use; a successful request alone does not prove delivery. See [PocketBase limiter](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/middlewares_rate_limit.go?rev=v0.41.1), [Appwrite limits](https://appwrite.io/docs/advanced/security/rate-limits), and [email delivery](https://appwrite.io/docs/advanced/self-hosting/configuration/email). |
| Settings encryption and recovery | **REASONED:** On a private PocketBase fixture, save a disposable SMTP credential and inspect persisted settings before and after selecting the encryption environment; plaintext settings must become encrypted, and a restart with the retained key must recover them. Create and restore a backup in a separate fixture, checking local uploads and separately restored S3 objects. Request `/api/backups/REPLACE_WITH_BACKUP_KEY` with no token, an ordinary-user file token, and a superuser file token: only the permitted superuser case should download. For Appwrite, restore disposable encrypted data with the original key; a separate wrong-key fixture must not recover those encrypted values. See [settings persistence](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/settings_model.go?rev=v0.41.1), [backup authorization](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/backup.go?rev=v0.41.1), and [Appwrite restoration](https://appwrite.io/docs/advanced/self-hosting/production/backups). |
| Appwrite uploads and functions | **REASONED:** Upload harmless fixtures through `POST /v1/storage/buckets/REPLACE_WITH_BUCKET/files`, comparing permitted and unrelated users. Test files at the chosen maximum and one byte above it. With a mandatory encryption/scanning policy capped at 20,000,000 bytes, larger uploads must be rejected; accepted fixtures must show the intended encryption and scanner processing. Invoke a harmless function through `POST /v1/functions/REPLACE_WITH_FUNCTION/executions`: intended execute roles succeed, unrelated users fail, and an authorized server key remains a separate privileged case even when the function is disabled. From the second host, confirm executor/orchestrator ports are inaccessible. See [bucket controls](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/src/Appwrite/Platform/Modules/Storage/Http/Buckets/Create.php), [function controls](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/src/Appwrite/Platform/Modules/Functions/Http/Functions/Create.php), and [service networks](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/docker-compose.yml). |

### 4. Check the client bundle for privileged credentials

**REASONED:** No deployed client bundle or credential inventory was supplied. Confirm that the
client carries only an end-user session or auth token, never a PocketBase superuser token or an
Appwrite API key of any scope. Appwrite API keys are server credentials regardless of scope;
client code should authenticate with an end-user session from the Client SDK instead. See
[PocketBase superusers](https://pocketbase.io/docs/authentication/) and
[Appwrite API keys](https://appwrite.io/docs/partners/project/api-keys).

REASONED: exact-match scan procedure; no deployed client bundle or credential inventory is available, so deployed absence remains unobserved. The scan block passed bash -n and ShellCheck 0.11.0 with exit 0 and no output. Its guards printed refusal messages for written and embedded placeholders, example.com, angle brackets, empty values, and omitted or shortened set -- lines without invoking the grep stub. Stub exits 0, 1, and 2 printed respectively FAIL: credential matches in the files listed above; No exact matches; also inspect build inputs and source maps.; and Scan failed; no conclusion. The bash -n, ShellCheck and stub runs recorded here covered the scan block in an earlier form, whose guard refusals left the subshell with status 0 and whose result arms ended with status 0; none was re-run on the current form, whose guard refusals leave the subshell with status 2, whose FAIL arm exits 1 and whose scan-failure arm exits 3. Separately, real grep -r -F -l -f on a disposable marker fixture exited 0 and printed only the matching client.js filename; after marker removal it exited 1 with no output. Expected exposed bundles contain privileged credentials and fixed bundles do not, per the guide’s cited PocketBase authentication (rolling documentation, checked November 2026) and Appwrite project API keys (rolling documentation, checked November 2026); exact-match fixtures do not establish detection of encoded or split credentials. Grep the client bundle for the strings used by your admin credentials or API keys; they should
not appear. Prepare a protected, nonempty patterns file containing one exact credential per
line, outside the bundle directory. The command prints matching filenames, not secret-bearing
lines. Establish a positive control using a disposable dummy credential in a test bundle, then
remove it and repeat. Exact matching does not detect every encoded or split representation.

REASONED: following block; privileged-credential scanning follows the cited authentication/API-key documentation; no deployed client bundle or credential inventory was supplied.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PROTECTED_SECRET_PATTERNS_FILE' 'REPLACE_WITH_CLIENT_BUNDLE_DIRECTORY'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not scanning"; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not scanning"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the protected patterns file path; not scanning"; exit 2 ;;
    *)
      case "$2" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
          echo "substitute the client bundle directory; not scanning"; exit 2 ;;
        *)
          if grep -r -F -l -f "$1" -- "$2"; then
            echo "FAIL: credential matches in the files listed above"; exit 1
          else
            case "$?" in
              1) echo "No exact matches; also inspect build inputs and source maps." ;;
              *) echo "Scan failed; no conclusion."; exit 3 ;;
            esac
          fi ;;
      esac ;;
  esac
)
```

### Verification status and source work

REASONED: authoring-time shell checks of an earlier form of the three bash blocks; no live service or deployed bundle was available, and the current forms, in which the GET and registration blocks also set their exit status from their request, are covered by the repository gate suite's bash -n and ShellCheck 0.11.0 passes. All three bash blocks passed ShellCheck 0.11.0 and `bash -n` during authoring. Local guard tests
refused embedded `REPLACE_WITH_` placeholders, `example.com`, angle brackets, empty arguments,
and omitted or shortened `set --` lines. These checks establish shell behavior only. No live
service result or deployed-bundle scan is claimed.

| Check scope or source-work ID | Procedure and prerequisites | Status |
| --- | --- | --- |
| Service comparisons | Demonstrate every REASONED comparison above on PocketBase v0.41.1 and Appwrite 2.7.0, recording binary/image identity, commands, response bodies, denied and allowed identities, disposable-data cleanup, and effective settings. Requires writable service fixtures, a container runtime, controlled accounts and mailboxes, S3 and backup fixtures, ClamAV, function execution, a second-host ingress fixture, and the actual client build. Include all five PocketBase actions, manageRule, file-token issuance versus protected downloads (unrelated-user and unsigned-guest denial, permitted-user bytes), realtime, bootstrap-token handling, MFA, verification, retained-token behavior, additive Appwrite permissions (items, part 1 of 2). The service-comparison items (part 2 of 2): server-key scopes, registration, console MFA (fresh password-only denial and successful TOTP completion), TLS, proxy trust, limits, encrypted recovery, uploads, and executor privacy. | REASONED: full service-comparison inventory; a live PocketBase or Appwrite stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. This comparison still requires the writable service, container, account, mailbox, S3, backup, scanner, function, second-host ingress, and actual-build prerequisites named in this row. All three Verify shell blocks passed bash -n and ShellCheck 0.11.0 with exit 0 and no output. With curl and grep stubbed, written and embedded placeholders, example.com, angle brackets, empty values, and omitted or shortened set -- lines printed their refusal messages without invoking either stub. The signup JSON parsed as four expected string fields; valid curl stubs printed arguments and protected input separately. The grep stub exercised match, no-match, and error branches; real grep on a disposable marker printed only client.js with exit 0 and, after removal, no output with exit 1. None establishes the listed live outcomes. The bash -n, ShellCheck and stub runs recorded here covered all three Verify shell blocks in an earlier form, whose guard refusals left the subshell with status 0 and whose scan block result arms ended with status 0, and the stub runs were not repeated on the current forms. In the current forms guard refusals leave the subshell with status 2, the GET and registration blocks exit 3 when curl fails, the registration block exits 1 when the registration returns 201, the scan block's FAIL and scan-failure arms exit 1 and 3, and the repository gate suite's bash -n and ShellCheck 0.11.0 passes cover all three blocks. Exposed public authorization should admit unintended access and fixed authorization should deny or filter it while retaining permitted controls; the other expected outcomes remain those in the individual comparisons, per the guide’s cited sources, which this cell lists in six parts. The guide’s cited sources (1 of 6): PocketBase API rules and filters (rolling documentation, checked November 2026); Appwrite legacy collection/document permissions (rolling documentation, checked November 2026); Appwrite 2.7.0 console registration handler; PocketBase v0.41.1 auth defaults, manageRule validation, and MFA. The guide’s cited sources (2 of 6): PocketBase v0.41.1 file-token and download authorization; PocketBase v0.41.1 realtime authorization; PocketBase v0.41.1 authentication and superuser IP middleware; PocketBase v0.41.1 settings, encryption, proxy trust, SMTP, backups, and rate defaults; PocketBase v0.41.1 backup download authorization. The guide’s cited sources (3 of 6): PocketBase v0.41.1 rate limiter and exemptions; PocketBase v0.41.1 listener and origin flags; Appwrite 2.7.0 API-key authorization, scopes, MFA enforcement, and abuse exemptions; Appwrite 2.7.0 hostname routing and HTTPS enforcement; Appwrite email delivery (rolling documentation, checked November 2026). The guide’s cited sources (4 of 6): Appwrite self-hosted backups and encryption-key preservation (rolling documentation, checked November 2026); Appwrite 2.7.0 bucket defaults and upload controls; Appwrite 2.7.0 function execute roles, execution-key scopes, and enablement; Appwrite 2.7.0 Compose console URL, persistent volumes, and Docker socket mounts. The guide’s cited sources (5 of 6): PocketBase authentication (rolling documentation, checked November 2026); Appwrite project API keys (rolling documentation, checked November 2026); PocketBase v0.41.1 installer and bootstrap-token lifetime; PocketBase v0.41.1 record CRUD handlers; PocketBase v0.41.1 record authorization and token validation. The guide’s cited sources (6 of 6): PocketBase v0.41.1 native TLS and ACME listener; Appwrite console MFA enrollment and recovery codes (rolling documentation, checked November 2026); Appwrite rate limits (rolling documentation, checked November 2026); and Appwrite permissions, creation defaults, and server integrations (rolling documentation, checked November 2026). REASONED from the cited vendor documentation and available pinned sources; live behavior is not demonstrated. |
| SELFHOSTED-BACKEND-SOURCE-1 | Complete pin-specific tracing for the Appwrite document read-authorization internals. The PocketBase CLI wrapper, the `--dev` flag default, the Appwrite requester privileged/API-key classification, and the Appwrite-repository document-read call sites are now cited above, alongside the earlier collection default, document-create permission branch, and backup archive pins. With the move to Appwrite 2.7.0 and utopia-php/database 10.1.0, the pinned dependency cites permission-role extraction and matching and authorization status/skip behavior. The SQL base used by MariaDB, MySQL, Postgres and SQLite is traced: without joins `getDocument` adds no permission filter, while `find` adds the main collection's document-permission hook only with authorization enabled and `documentSecurity` on, or for the metadata collection, unless a join or bounded-page path finds the collection granted; the Postgres override is described above. With authorization enabled, `find` also adds a `Permission\Join` hook for each joined table that the collection's join document-security map does not disable. Memory, Redis and Pool `getDocument`/`find` and Mongo `getDocument` are traced as described above, as are Appwrite 2.7.0's `_APP_DB_ADAPTER` default, pool scheme mapping, factory Pool wrapping on the document GET's non-transaction retrieval path and upgrade engine detection. The 2.7.0 install task's command-line selection, existing-database detection and container start, the document GET's transaction-state branches, the web installer's database selection, the Compose generator's database handling, the `Appwrite\Docker\Compose` and `Env` representation of a value-less entry and the in-tree `System::getEnv` empty-value reading are traced as described above too. Still open at 10.1.0: the Database-level `getDocument` and `find` read checks and `skip` dispatch in `Trait\Documents`, the Mongo `find` permission hook, `Storage::permissionsTable()` and where `Database::COLLECTION_GRANTED` and `Database::JOIN_DOCUMENT_SECURITY` are set. Still open at 2.7.0: which adapter a given deployment uses, how Compose resolves the value-less `_APP_DB_ADAPTER` entry, whether a `transactions` document's permissions limit an ordinary requester to its creator, the handler's `stampTransactionRead` and `isTransactionTypeMismatch` helpers, the `Metadata` and `Joins` hooks, and whether 2.7.0 loads the in-tree `Utopia\System\System`. | REASONED: pinned-source reading of PocketBase v0.41.1, Appwrite 2.7.0 and the utopia-php/database 10.1.0 excerpts above, with the Appwrite 2.3.0 to 2.7.0 release notes; the Database-level, Mongo find, deployment-adapter, Compose-resolution and remaining transaction-state gaps stay open, complete pinned-source verification is not claimed, and live authorization is not demonstrated. |

## Sources (checked November 2026)

The November 2026 date in this heading is the guide-wide documentation check, which covers every rolling documentation item: the 9 Appwrite rolling documentation items were rechecked as served on 2026-11-04 and the 5 PocketBase pages as served on 2026-11-05. Items pinned to a release or commit carry no check date, except those marked "checked October 2026" or "checked November 2026", which were checked individually, and some pinned items were first cited in October or November 2026.

The PocketBase source items cite its author's forge at the v0.41.1 tag, because PocketBase moved its source and releases off GitHub at v0.41.0. The forge's line-anchor format is not established, so line ranges are in the link text. The cited files and line ranges were read in the v0.41.1 Go module, whose recorded origin is the forge's v0.41.1 tag at commit f70b24e1; the forge pages themselves were not opened, so that they serve the same text is not established.

- PocketBase going to production (rolling documentation, checked November 2026): https://pocketbase.io/docs/going-to-production/
- PocketBase API rules and filters (rolling documentation, checked November 2026): https://pocketbase.io/docs/api-rules-and-filters/
- Appwrite self-hosting production security (rolling documentation, checked November 2026): https://appwrite.io/docs/advanced/self-hosting/production/security
- Appwrite project API keys (rolling documentation, checked November 2026): https://appwrite.io/docs/partners/project/api-keys
- [PocketBase authentication (rolling documentation, checked November 2026)](https://pocketbase.io/docs/authentication/).
- [PocketBase files and protected downloads (rolling documentation, checked November 2026)](https://pocketbase.io/docs/files-handling/).
- [PocketBase Realtime API (rolling documentation, checked November 2026)](https://pocketbase.io/docs/api-realtime/).
- [PocketBase v0.41.1 installer and bootstrap-token lifetime (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/installer.go?rev=v0.41.1).
- [PocketBase v0.41.1 listener and origin flags (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/cmd/serve.go?rev=v0.41.1).
- [PocketBase v0.41.1 native TLS and ACME listener (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/serve.go?rev=v0.41.1).
- [PocketBase v0.41.1 authentication and superuser IP middleware (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/middlewares.go?rev=v0.41.1).
- [PocketBase v0.41.1 record authorization and token validation (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/record_query.go?rev=v0.41.1).
- [PocketBase v0.41.1 record CRUD handlers (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/record_crud.go?rev=v0.41.1).
- [PocketBase v0.41.1 auth defaults, manageRule validation, and MFA (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/collection_model_auth_options.go?rev=v0.41.1).
- [PocketBase v0.41.1 settings, encryption, proxy trust, SMTP, backups, and rate defaults (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/settings_model.go?rev=v0.41.1).
- [PocketBase v0.41.1 development logging and mailer selection (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/base.go?rev=v0.41.1).
- [PocketBase v0.41.1 file-token and download authorization (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/file.go?rev=v0.41.1).
- [PocketBase v0.41.1 realtime authorization (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/realtime.go?rev=v0.41.1).
- [PocketBase v0.41.1 backup download authorization (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/backup.go?rev=v0.41.1).
- [PocketBase v0.41.1 backup archive implementation, lines 36 to 60 (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/backup_create.go?rev=v0.41.1).
- [PocketBase v0.41.1 rate limiter and exemptions (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/middlewares_rate_limit.go?rev=v0.41.1).
- [PocketBase v0.41.0 release notes on the move to the new host, read for the v0.41.1 basis (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/releases?expr=tag%3D%22v0.41.0%22).
- [Appwrite 2.7.0 collection create parameters (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Create.php#L88-L90).
- [Appwrite 2.7.0 document create parameters (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Create.php#L134-L139).
- [Appwrite 2.7.0 requester classification (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Create.php#L217-L218).
- [Appwrite 2.7.0 document create permission handling (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Create.php#L238-L288).
- [Appwrite 2.7.0 composer.lock pinned database dependency, utopia-php/database 10.1.0 (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/composer.lock#L4429-L4439).
- [utopia-php/database 10.1.0 aggregate helper (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Permission.php#L176-L180).
- [utopia-php/database 10.1.0 permission role extraction (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Document.php#L273-L334).
- [utopia-php/database 10.1.0 document attribute default (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Document.php#L405-L416).
- [utopia-php/database 10.1.0 authorization role matching (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Validator/Authorization.php#L59-L102).
- [utopia-php/database 10.1.0 Database traits, including the unread Documents trait (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Database.php#L52-L61).
- [utopia-php/database 10.1.0 shared authorization instance (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Database.php#L1033-L1039).
- [utopia-php/database 10.1.0 related-document grant checking (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Database.php#L1162-L1183).
- [utopia-php/database 10.1.0 authorization status and skip (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Validator/Authorization.php#L148-L208).
- [utopia-php/database 10.1.0 shared status scope and constructor default (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Validator/Authorization.php#L10-L41).
- [utopia-php/database 10.1.0 SQL document fetch (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L650-L779).
- [utopia-php/database 10.1.0 SQL find roles and read default (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L1566-L1572).
- [utopia-php/database 10.1.0 SQL find permission gate on status, grant and documentSecurity (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L5063-L5079).
- [utopia-php/database 10.1.0 SQL joined-table permission hooks (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L5081-L5112).
- [utopia-php/database 10.1.0 SQL per-document filtering test (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L5179-L5183).
- [utopia-php/database 10.1.0 SQL joined-table document-security test (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L5185-L5213).
- [utopia-php/database 10.1.0 SQL bounded-page permission gate (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L6080-L6086).
- [utopia-php/database 10.1.0 SQL permission hook construction (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L3658-L3678).
- [utopia-php/database 10.1.0 SQL base permission filter (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL/Hook/Permission/Filter.php#L72-L116).
- [utopia-php/database 10.1.0 Postgres permission filter (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Postgres.php#L1909-L1958).
- [utopia-php/database 10.1.0 MariaDB SQL inheritance (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/MariaDB.php#L46).
- [utopia-php/database 10.1.0 MySQL MariaDB inheritance (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/MySQL.php#L25).
- [utopia-php/database 10.1.0 Postgres SQL inheritance (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Postgres.php#L53).
- [utopia-php/database 10.1.0 SQLite SQL inheritance (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQLite.php#L71).
- [utopia-php/database 10.1.0 SQLite find wrapper (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQLite.php#L249-L259).
- [utopia-php/database 10.1.0 Mongo adapter declaration (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Mongo.php#L57).
- [utopia-php/database 10.1.0 Mongo document fetch (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Mongo.php#L1561-L1603).
- [utopia-php/database 10.1.0 Mongo tenant and permission read hooks (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Mongo.php#L249-L282).
- [utopia-php/database 10.1.0 Mongo find filters (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Mongo.php#L2402-L2413).
- [utopia-php/database 10.1.0 Pool adapter declaration and delegation (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Pool.php#L36-L138).
- [utopia-php/database 10.1.0 Pool state sync (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Pool.php#L178-L186).
- [utopia-php/database 10.1.0 Pool transaction pinning (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Pool.php#L517-L541).
- [utopia-php/database 10.1.0 Pool document read delegation (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Pool.php#L802-L807).
- [utopia-php/database 10.1.0 Pool find delegation (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Pool.php#L884-L889).
- [utopia-php/database 10.1.0 Pool authorization setter (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Pool.php#L1101-L1106).
- [utopia-php/database 10.1.0 Memory namespace and Adapter import (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Memory.php#L3-L5).
- [utopia-php/database 10.1.0 Memory adapter purpose and declaration (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Memory.php#L36-L48).
- [utopia-php/database 10.1.0 Memory document fetch (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Memory.php#L1204-L1227).
- [utopia-php/database 10.1.0 Memory find (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Memory.php#L1807-L1836).
- [utopia-php/database 10.1.0 Memory find tenant and permission filter (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Memory.php#L2397-L2452).
- [utopia-php/database 10.1.0 Memory permission allow set (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Memory.php#L3108-L3141).
- [utopia-php/database 10.1.0 Redis namespace and Adapter import (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Redis.php#L5-L8).
- [utopia-php/database 10.1.0 Redis adapter purpose and declaration (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Redis.php#L41-L57).
- [utopia-php/database 10.1.0 Redis permission filter (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Redis.php#L1938-L1973).
- [utopia-php/database 10.1.0 Redis document fetch and tenant check (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Redis.php#L882-L916).
- [utopia-php/database 10.1.0 Redis find (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Redis.php#L1482-L1519).
- [utopia-php/database 10.1.0 Redis find permission step (checked November 2026)](https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Redis.php#L2809-L2823).
- [Appwrite permissions, creation defaults, and server integrations (rolling documentation, checked November 2026)](https://appwrite.io/docs/advanced/security/permissions).
- [Appwrite legacy collection/document permissions (rolling documentation, checked November 2026)](https://appwrite.io/docs/products/databases/tablesdb/legacy/permissions).
- [Appwrite environment reference, HTTPS deprecation, database selector, console URL and key variables (rolling documentation, checked November 2026)](https://appwrite.io/docs/advanced/self-hosting/configuration/environment-variables).
- [Appwrite rate limits (rolling documentation, checked November 2026)](https://appwrite.io/docs/advanced/security/rate-limits).
- [Appwrite email delivery (rolling documentation, checked November 2026)](https://appwrite.io/docs/advanced/self-hosting/configuration/email).
- [Appwrite self-hosted backups and encryption-key preservation (rolling documentation, checked November 2026)](https://appwrite.io/docs/advanced/self-hosting/production/backups).
- [Appwrite 2.7.0 configuration defaults, console URL, key versions and executor secret (checked November 2026)](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/config/variables.php).
- [Appwrite 2.7.0 development environment and placeholder secrets (checked November 2026)](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/.env).
- [Appwrite 2.7.0 console registration handler (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Account/Http/Account/Create.php#L109-L134).
- [Appwrite console MFA enrollment and recovery codes (rolling documentation, checked November 2026)](https://appwrite.io/docs/advanced/security/mfa).
- [Appwrite 2.7.0 API-key authorization, scopes, MFA enforcement, and abuse exemptions (checked November 2026)](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/controllers/shared/api.php).
- [Appwrite 2.7.0 MFA minimum factors (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Utopia/Database/Documents/User.php#L211-L218).
- [Appwrite 2.7.0 account GET route groups (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Account/Http/Account/Get.php#L27-L30).
- [Appwrite 2.7.0 recent MFA challenge window (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Utopia/Database/Documents/User.php#L230-L244).
- [Appwrite 2.7.0 MFA_RECENT_DURATION constant (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/app/init/constants.php#L266).
- [Appwrite 2.7.0 MFA turn-off challenge check (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Account/Http/Account/MFA/Update.php#L81-L84).
- [Appwrite 2.7.0 MFA challenge TOTP spend (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Account/Http/Account/MFA/Challenges/Update.php#L165-L177).
- [Appwrite 2.7.0 single-use TOTP steps (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Auth/MFA/Challenge/TOTP.php#L30-L88).
- [Appwrite 2.7.0 encryption key resolution and versions (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Auth/EncryptionKey.php#L11-L69).
- [Appwrite 2.7.0 jobs secret resolution (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Auth/JobsSecret.php#L20-L32).
- [Appwrite 2.7.0 install task secret generation condition (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L331).
- [Appwrite 2.3.0 release notes on the console URL and packages, read for the 2.7.0 basis (checked November 2026)](https://github.com/appwrite/appwrite/releases/tag/2.3.0).
- [Appwrite 2.4.0 release notes on the generated encryption key, read for the 2.7.0 basis (checked November 2026)](https://github.com/appwrite/appwrite/releases/tag/2.4.0).
- [Appwrite 2.6.2 release notes on key scope limits and the generated executor secret, read for the 2.7.0 basis (checked November 2026)](https://github.com/appwrite/appwrite/releases/tag/2.6.2).
- [Appwrite 2.7.0 release notes on key rotation, MFA, public scope and function scopes (checked November 2026)](https://github.com/appwrite/appwrite/releases/tag/2.7.0).
- [Appwrite 2.7.0 hostname routing and HTTPS enforcement (checked November 2026)](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/controllers/general.php).
- [Appwrite 2.7.0 bucket defaults and upload controls (checked November 2026)](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/src/Appwrite/Platform/Modules/Storage/Http/Buckets/Create.php).
- [Appwrite 2.7.0 function execute roles, execution-key scopes, enablement and scope grants (checked November 2026)](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/src/Appwrite/Platform/Modules/Functions/Http/Functions/Create.php).
- [Appwrite 2.7.0 storage thresholds and release constant (checked November 2026)](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/init/constants.php).
- [Appwrite 2.7.0 Compose console URL, persistent volumes, and Docker socket mounts (checked November 2026)](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/docker-compose.yml).
- [PocketBase v0.41.1 CLI wrapper and development flag wiring, lines 234 to 239 (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/pocketbase.go?rev=v0.41.1).
- [PocketBase v0.41.1 dev default selection, lines 73 to 79 (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/pocketbase.go?rev=v0.41.1).
- [PocketBase v0.41.1 flag-to-app dev wiring, lines 129 to 139 (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/pocketbase.go?rev=v0.41.1).
- [PocketBase v0.41.1 root command wiring for serve and superuser, lines 165 to 173 (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/pocketbase.go?rev=v0.41.1).
- [PocketBase v0.41.1 go run detection, lines 10 to 19 (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/tools/osutils/run.go?rev=v0.41.1).
- [PocketBase v0.41.1 dev SQL logging, lines 1277 to 1286 (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/base.go?rev=v0.41.1).
- [PocketBase v0.41.1 dev logger level, lines 1489 to 1499 (checked November 2026)](https://ganigeorgiev.com/pocketbase/pocketbase/files/core/base.go?rev=v0.41.1).
- [Appwrite 2.7.0 document read handler and requester checks (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Get.php#L82-L97).
- [Appwrite 2.7.0 document fetch, through the database layer without a transaction ID and through transaction state with one (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Get.php#L105-L132).
- [Appwrite 2.7.0 privileged and key role classification (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Utopia/Database/Documents/User.php#L82-L116).
- [Appwrite 2.7.0 API-key role, scopes, and authorization status (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/app/controllers/shared/api.php#L146-L167).
- [Appwrite 2.7.0 admin-mode roles and authorization status (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/app/controllers/shared/api.php#L328-L361).
- [Appwrite 2.7.0 request role assignment (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/app/controllers/shared/api.php#L396-L400).
- [Appwrite 2.7.0 route scope validation (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/app/controllers/shared/api.php#L557-L561).
- [Appwrite 2.7.0 collection permission and documentSecurity handoff (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Create.php#L230-L236).
- [Appwrite 2.7.0 database pool DSN fallbacks and connections (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/app/init/registers.php#L45-L99).
- [Appwrite 2.7.0 database adapter mapping (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/app/init/registers.php#L239-L252).
- [Appwrite 2.7.0 tenant database construction, authorization and grant checking (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Database/Factory.php#L123-L201).
- [Appwrite 2.7.0 database factory Pool wrapping (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Database/Factory.php#L208-L211).
- [Appwrite 2.7.0 database factory Pool import (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Database/Factory.php#L12).
- [Appwrite 2.7.0 getDatabasesDB request resource (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/app/init/resources/request.php#L1112-L1159).
- [Appwrite 2.7.0 document GET transaction branch (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Get.php#L109-L124).
- [Appwrite 2.7.0 document GET not-found response for an empty document (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Get.php#L134-L136).
- [Appwrite 2.7.0 transaction-state staged creation return (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Databases/TransactionState.php#L92-L94).
- [Appwrite 2.7.0 upgrade database engine detection (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Upgrade.php#L73-L98).
- [Appwrite 2.7.0 install task Compose template read (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L563-L568).
- [Appwrite 2.7.0 install task Compose template rendering (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L664-L671).
- [Appwrite 2.7.0 console variables database adapter fallback (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Console/Http/Variables/Get.php#L118).
- [Appwrite 2.7.0 console variables response model database adapter rule (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Utopia/Response/Model/ConsoleVariables.php#L130-L138).
- [Appwrite 2.7.0 install task database parameter default (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L81).
- [Appwrite 2.7.0 install task detected existing database override (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L234-L239).
- [Appwrite 2.7.0 install task interactive database answer (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L299-L307).
- [Appwrite 2.7.0 install task database adapter assignment (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L318-L319).
- [Appwrite 2.7.0 install task existing-configuration check (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L550-L555).
- [Appwrite 2.7.0 install task Compose and environment file writes (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L708-L721).
- [Appwrite 2.7.0 install environment file template (checked November 2026)](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/views/install/env.phtml).
- [Appwrite 2.7.0 transaction-state document branches (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Databases/TransactionState.php#L70-L108).
- [Appwrite 2.7.0 transaction read by requester class and log reads under skip (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Databases/TransactionState.php#L675-L706).
- [Appwrite 2.7.0 transaction-state request resource (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/app/init/resources/request.php#L1161-L1165).
- [Appwrite 2.7.0 database factory authorization resource (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/app/init/resources/request.php#L234-L238).
- [Appwrite 2.7.0 upgrade hand-off to the install task (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Upgrade.php#L108-L110).
- [Appwrite 2.7.0 install task existing database detection order (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L214-L233).
- [Appwrite 2.7.0 install task database service and host detection (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L1709-L1728).
- [Appwrite 2.7.0 install task web-installer branch (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L253-L262).
- [Appwrite 2.7.0 install task explicit command-line parameter check (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L1694-L1703).
- [Appwrite 2.7.0 install task container start condition (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L767-L773).
- [Appwrite 2.7.0 install task Compose start (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L1316-L1377).
- [Appwrite 2.7.0 web installer database default and lock (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/app/views/install/installer/templates/steps/step-1.phtml#L11-L20).
- [Appwrite 2.7.0 web installer database choices (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/app/views/install/installer/templates/steps/step-1.phtml#L66-L108).
- [Appwrite 2.7.0 web installer default database variable (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/app/views/install/installer.phtml#L12).
- [Appwrite 2.7.0 web installer view database settings (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/View.php#L42-L48).
- [Appwrite 2.7.0 web installer posted database fallback (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/app/views/install/installer/js/modules/progress.js#L408).
- [Appwrite 2.7.0 web installer database parameter (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L46).
- [Appwrite 2.7.0 web installer database validation (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L150-L161).
- [Appwrite 2.7.0 web installer supported database values (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Runtime/State.php#L204-L206).
- [Appwrite 2.7.0 web installer database adapter input (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L238-L246).
- [Appwrite 2.7.0 web installer resumed progress check (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L202-L225).
- [Appwrite 2.7.0 web installer resumed payload comparison (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L248-L285).
- [Appwrite 2.7.0 web installer resumed database input (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L313).
- [Appwrite 2.7.0 web installer environment preparation (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L320-L322).
- [Appwrite 2.7.0 web installer installation call (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L380-L394).
- [Appwrite 2.7.0 install task web installer configuration (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L337-L374).
- [Appwrite 2.7.0 install task existing-installation defaults (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L156-L191).
- [Appwrite 2.7.0 install task user input, generated secrets and database host (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L440-L473).
- [Appwrite 2.7.0 installer server upgrade and database lock detection (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Server.php#L225-L257).
- [Appwrite 2.7.0 installer server database detection from files (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Server.php#L277-L315).
- [Appwrite 2.7.0 Compose generator, read whole (checked November 2026)](https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/src/Appwrite/Docker/Compose/Generator.php).
- [Appwrite 2.7.0 Compose generator selectable database services and volumes (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose/Generator.php#L9-L26).
- [Appwrite 2.7.0 Compose generator database dependency selector (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose/Generator.php#L71-L81).
- [Appwrite 2.7.0 Compose generator parameter normalization (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose/Generator.php#L145-L153).
- [Appwrite 2.7.0 Compose generator service filter (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose/Generator.php#L188-L210).
- [Appwrite 2.7.0 Compose generator volume filter (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose/Generator.php#L263-L278).
- [Appwrite 2.7.0 Compose generator dependency rewrite (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose/Generator.php#L283-L333).
- [Appwrite 2.7.0 Compose services (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose.php#L16-L27).
- [Appwrite 2.7.0 Compose service environment parsing (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose/Service.php#L32-L33).
- [Appwrite 2.7.0 environment parser lines without an assignment (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Env.php#L37-L42).
- [Appwrite 2.7.0 in-tree packages/system getEnv empty-value fallback (checked November 2026)](https://github.com/appwrite/appwrite/blob/2.7.0/packages/system/src/System.php#L703-L706).
- [curl curl-8_14_1 write-out fields and version requirements (checked October 2026)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/write-out.md#L75-L79).
- [curl curl-8_14_1 headers from stdin (checked October 2026)](https://raw.githubusercontent.com/curl/curl/curl-8_14_1/docs/cmdline-opts/header.md).
- [curl curl-8_14_1 configuration from stdin (checked October 2026)](https://raw.githubusercontent.com/curl/curl/curl-8_14_1/docs/cmdline-opts/config.md).


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- pb: PocketBase (v0.41.1)
- appwrite: Appwrite (2.7.0)
- pb-docs: PocketBase documentation (rolling) (unknown)
- appwrite-docs: Appwrite documentation (rolling) (unknown)
- utopia-php-database: utopia-php/database (10.1.0)
- curl: curl (curl-8_14_1)

Claims (full source mapping in the JSON block below):

- pb-bootstrap (REASONED; pb, pb-docs): Privately bootstrap through the logged installer URL; superuser create EMAIL PASS exposes passwords in argv. Ordinary registration does not grant superuser rights.
- pb-installer (REASONED; pb): Installer system-superuser token lasts about 30 minutes; protect its URL and startup logs as credentials.
- pb-ips (REASONED; pb, pb-docs): Superuser IP allowlists are available from v0.38.0; superuserIPs defaults empty and restricts authenticated requests, not /_/ static assets.
- pb-tls (REASONED; pb): serve with a domain provides native HTTPS/ACME; alternatively terminate TLS at a reverse proxy.
- pb-bind (REASONED; pb): Without a domain serve defaults to 127.0.0.1:8090; with a domain it uses 0.0.0.0:80/443. Behind a local proxy omit the domain and set --http loopback.
- pb-origins (REASONED; pb): --origins defaults * and accepts comma-separated allowed origins; CORS does not authorize records.
- pb-proxy (REASONED; pb): Trust only headers the proxy overwrites, review useLeftmostIP ordering and block direct backend access to protect IP/rate controls.
- pb-dev (REASONED; pb): --dev adds diagnostics including SQL on stderr, not an auth bypass; its configured default comes from New(): true if os.Args[0] starts with a nonempty os.TempDir() or cacheDir() prefix, false otherwise.
- pb-cli (REASONED; pb): In the pinned CLI wrapper, Start() registers the serve and superuser commands on the root command and executes it.
- pb-rules (REASONED; pb, pb-docs): Each list/view/create/update/delete rule defaults null (superuser-only); empty opens to guests and nonempty filters. Superusers bypass rules.
- pb-manage (REASONED; pb): Top-level manageRule defaults null and permits privileged auth-record changes alongside create/update rules; its validator rejects empty-string rules.
- pb-files (REASONED; pb, pb-docs): File fields default unprotected despite locked record rules; Protected plus an authorized viewRule gates downloads, while a public viewRule still permits public access.
- pb-file-token (REASONED; pb, pb-docs): Short-lived file tokens provide identity context, not file authorization; viewRule decides. Protect token-bearing file URLs.
- pb-realtime (REASONED; pb, pb-docs): Collection subscriptions use listRule and individual-record subscriptions viewRule; SSE/subscription success does not prove event authorization.
- pb-password (REASONED; pb): Auth initialization enables password authentication with email as the identity field.
- pb-oauth (REASONED; pb, pb-docs): OAuth2 defaults disabled and is unsupported for _superusers.
- pb-mfa-default (REASONED; pb): MFA defaults disabled with duration 600 seconds.
- pb-otp-default (REASONED; pb): OTP defaults disabled with duration 180 seconds and length 8.
- pb-alerts (REASONED; pb): Authentication alerts default enabled; retain alerts and provide working email.
- pb-auth-token (REASONED; pb): Auth token duration defaults to 432000 seconds.
- pb-file-duration (REASONED; pb): File token duration defaults to 180 seconds.
- pb-auth-rule (REASONED; pb, pb-docs): authRule defaults empty; verified-only collections can require verified = true after email verification works.
- pb-mfa (REASONED; pb, pb-docs): For superusers retain password auth and enable both OTP and MFA; empty mfa.rule applies to everyone. OTP alone is not a second factor.
- pb-logout (REASONED; pb, pb-docs): Stateless authentication means clearing pb.authStore removes only the local copy, not a stolen token.
- pb-encryption (REASONED; pb, pb-docs): Settings default to plaintext JSON; select a 32-character environment secret with --encryptionEnv. This encrypts settings, not the whole database or files.
- pb-backups (REASONED; pb, pb-docs): Backups default local with empty cron (automatic backups off); archives contain main and logs databases plus remaining pb_data, excluding the backups directory and tracked exclusions; uploaded collection files on S3 require manual backup. Schedule/retain deliberately and protect archives.
- pb-backup-auth (REASONED; pb): Backup downloads require a superuser file token and obey superuser IP restrictions; ordinary auth/file tokens do not suffice.
- pb-limiter (REASONED; pb, pb-docs): Native limits exist from v0.23.0 but default disabled at v0.41.1; enable rateLimits.enabled.
- pb-limit-rules (REASONED; pb): Seeded limits are *:auth 2/3s, *:create 20/5s, /api/batch 3/1s and /api/ 300/10s.
- pb-limit-bypass (REASONED; pb): Superusers and rateLimits.excludedIPs bypass limits; test ordinary non-excluded clients.
- pb-smtp (REASONED; pb): smtp.enabled and smtp.tls default false; disabled SMTP falls back to sendmail. Configure protected transport and test actual delivery.
- pb-forge (REASONED; pb): From v0.41.0 PocketBase publishes its source and releases on its author's forge at ganigeorgiev.com, which this guide cites at v0.41.1; the v0.41.0 notes flag only the Go module's move to the new host, and no guide statement depends on the module path.
- appwrite-https (REASONED; appwrite, appwrite-docs): API FORCE_HTTPS and function/site ROUTER_FORCE_HTTPS default disabled at 2.7.0; explicitly enable both despite conflicting rolling deprecation/default documentation.
- appwrite-hosts (REASONED; appwrite): ROUTER_PROTECTION defaults disabled; configure actual domains and enable rejection of unknown hostnames.
- appwrite-registration (REASONED; appwrite): Console root-only registration defaults enabled with empty email/IP allowlists; these restrict account creation, not dashboard reachability or login.
- appwrite-console (REASONED; appwrite, appwrite-docs): Claim the first operator privately and use a separate network/access boundary for a private dashboard.
- appwrite-console-url (REASONED; appwrite, appwrite-docs): Since 2.3.0, _APP_CONSOLE_URL is the origin console links are built from and replaces the removed _APP_CONSOLE_URL_SCHEME; 2.7.0 defaults it to empty and its Compose file passes it to the appwrite service without a value, so set it when the console host differs from the API.
- appwrite-mfa (REASONED; appwrite, appwrite-docs): Enroll and verify operator TOTP, protect recovery codes; at 2.7.0 enabled MFA with a verified factor requires a second session factor, a spent TOTP time step cannot be reused, and turning MFA off needs a session challenge from the last 1800 seconds.
- appwrite-dev-env (REASONED; appwrite): Development env disables root-only registration, abuse and router protection and carries placeholders; do not inherit it for production.
- appwrite-recreate (REASONED; appwrite-docs): Apply env/Compose changes with docker compose up -d from the install directory, then check effective behavior.
- appwrite-permissions (REASONED; appwrite, appwrite-docs): Collection and document grants are additive according to legacy documentation; documentSecurity defaults false in Appwrite 2.7.0 and must be enabled for document grants. The pinned parameter description states the need for one permission level.
- appwrite-creation (REASONED; appwrite, appwrite-docs, utopia-php-database): For null or omitted document permissions, the pinned aggregate helper preserves null before the handler assigns read/update/delete user grants to a nonprivileged requester with a user ID, or an empty list otherwise. API-key classification skips role validation but does not itself determine the default list. Use specific users/teams for private data.
- appwrite-read-path (REASONED; appwrite): Document GET classifies requesters by authorization role (keys; owner/developer/admin privileged), reports disabled databases/collections as not found to others and, without a transaction ID, fetches through the database layer, which gets collection permissions and documentSecurity at collection creation. With one, staged creates come from the pending transaction's logs.
- appwrite-requester (REASONED; appwrite): With an API key the request role and scopes come from the key, plus public at 2.7.0; a standard, ephemeral or dynamic project key for the same project sets the current authorization status to disabled, as do admin-mode console sessions outside the console and organization project read routes, while route scope validation applies to every requester.
- appwrite-keys (REASONED; appwrite, appwrite-docs): Properly scoped server API keys bypass resource permissions but still obey operation scopes; treat keys.write as admin-equivalent: release notes since 2.6.2 say a key cannot grant scopes it does not hold, which the served page does not reflect, but the 2.7.0 key handlers were not read. Keys never belong in clients.
- appwrite-key-creation (REASONED; appwrite-docs): The served API keys page says creating API keys with the Project API is deprecated as of 17 August 2026 and long-lived keys are created in the Console, while the Project API can still list, update and delete keys and issue ephemeral keys.
- appwrite-encryption (REASONED; appwrite, appwrite-docs): Fresh 2.7.0 installs generate _APP_OPENSSL_KEY_V1 while existing and upgraded installs keep their stored value, so replace a remaining your-secret-key placeholder before production data; preserve every key version that still decrypts data, since loss strands encrypted secrets.
- appwrite-backups (REASONED; appwrite-docs): Back up database, persistent storage and deployment configuration; restrict access and test restoration in a separate installation.
- appwrite-abuse (REASONED; appwrite, appwrite-docs): _APP_OPTIONS_ABUSE defaults enabled but dev env disables it; server API-key and owner, developer or admin requests are exempt, so test with ordinary clients.
- appwrite-smtp (REASONED; appwrite, appwrite-docs): SMTP host/port/secure/username/password default empty and empty host disables sending; configure the provider and confirm message receipt/use.
- appwrite-storage (REASONED; appwrite): Storage defaults local, upload limit 30000000 and server antivirus disabled; enabling scanning requires configured reachable ClamAV.
- appwrite-bucket (REASONED; appwrite): New bucket permissions are empty and fileSecurity=false; enable per-file security deliberately, since bucket grants also permit access.
- appwrite-bucket-options (REASONED; appwrite): Bucket encryption and antivirus default true; bucket antivirus does not enable the server scanner.
- appwrite-size (REASONED; appwrite): Encryption/scanning skip files above 20000000 bytes; cap maximumFileSize at that threshold when either is mandatory and test the boundary.
- appwrite-functions (REASONED; appwrite): Function execute roles and execution-key scopes default empty; grant narrowly. Disabled functions still admit authorized Server SDK API keys.
- appwrite-executor (REASONED; appwrite, appwrite-docs): Keep executor/orchestrator private and protect Docker-socket authority; fresh 2.7.0 installs generate _APP_EXECUTOR_SECRET but existing and upgraded installs keep theirs, so replace a remaining placeholder. Container execution is not demonstrated hostile-tenant isolation.
- appwrite-docs-lag (REASONED; appwrite, appwrite-docs): As served on 2026-11-04, the MFA page omits 2.7.0's single-use TOTP codes and recent challenge to turn MFA off, the security and backups pages its key rotation, the environment page the generated encryption key and executor secret, the API keys page key scope limits, and the security page says no unique encryption key is generated; the guide states each from release notes and source.
- verify-pb-records (REASONED; pb-docs, curl): Public rules allow guest reads; locked rules deny with 403, unsatisfied list filters can return empty 200 and view rules 404. Retain owner and separate superuser controls.
- verify-appwrite-records (REASONED; appwrite-docs): Broad collection grants defeat document restrictions; removing them must deny unrelated users while document grantees succeed. Compare client/server creation defaults.
- verify-appwrite-keys (REASONED; appwrite): A correctly scoped server key reads despite empty permissions, while a key without scope fails; neither substitutes for an ordinary-user control.
- verify-registration (REASONED; appwrite): On disposable Appwrite fixtures compare open signup 201 with root-only account-limit failure and independent email/IP restrictions; retain login/invitation controls.
- verify-pb-bootstrap (REASONED; pb): Guest and ordinary-user _superusers record creation must fail while a valid installer token creates the private operator; static dashboard assets prove no admin access.
- verify-appwrite-mfa (REASONED; appwrite, appwrite-docs): Console account GET succeeds without MFA, fails for a fresh password-only MFA session, where 2.7.0 throws USER_MORE_FACTORS_REQUIRED with a response string not established here, and succeeds after TOTP completion with a code not already redeemed.
- verify-pb-writes (REASONED; pb): Compare intended/unauthorized POST/PATCH/DELETE and privileged auth-record management; locked manageRule grants no management and empty-string configuration must fail.
- verify-pb-files (REASONED; pb, curl): Before protection unsigned file GET works; Protected plus private viewRule rejects guests/unrelated-user file tokens with 404 while permitted-user bytes still arrive.
- verify-pb-realtime (REASONED; pb, pb-docs): Mutate a fixture while comparing collection and record subscriptions; deny unauthorized event delivery, retaining authorized delivery. PB_CONNECT/acknowledgment alone is insufficient.
- verify-pb-mfa (REASONED; pb, pb-docs): Compare password-only completion with password-plus-OTP MFA and verified/unverified authRule logins; clearing authStore must not revoke a retained valid token.
- verify-pb-ips (REASONED; pb): Compare allowed/excluded superuser sources and forged forwarded headers; excluded sources must get 403 and direct backend access must fail with a working proxy control.
- verify-transport (REASONED; pb, appwrite): Compare HTTP/HTTPS and certificates, Appwrite API/function/site domains and configured/unknown Host; compare browser origins separately from record authorization.
- verify-abuse (REASONED; pb, appwrite-docs): Cross each configured threshold with ordinary non-excluded clients and compare disabled/enabled controls; PocketBase limiting yields 429 with later successful recovery.
- verify-email (REASONED; pb, appwrite-docs): Request OTP, verification and recovery messages and confirm receipt and use; request success alone is not delivery evidence.
- verify-pb-recovery (REASONED; pb, pb-docs): Compare plaintext/encrypted persisted settings, restart with retained key and restore local/S3 data; only permitted superuser file tokens may download backups.
- verify-appwrite-recovery (REASONED; appwrite-docs): Restore encrypted fixtures with the original key; a separate wrong-key fixture must not recover encrypted values.
- verify-uploads (REASONED; appwrite): Compare permitted/unrelated uploads and size-boundary fixtures; mandatory processing requires rejecting over-limit files and confirming accepted-file encryption/scanning.
- verify-functions (REASONED; appwrite): Compare intended execute roles, unrelated users and privileged server keys, including disabled functions; confirm executor/orchestrator privacy from a second host.
- verify-bundle (REASONED; pb-docs, appwrite-docs): Search filenames using protected exact-secret patterns with a disposable marker control; client bundles must contain neither superuser tokens nor Appwrite API keys, and encoded/split forms can evade scanning.
- local-guards (DEMONSTRATED; pb-docs, appwrite-docs): Recorded guard tests rejected placeholders and omitted/shortened arguments; this demonstrates shell behavior only, not service access or deployed-bundle scanning. The tests covered earlier forms, whose guard refusals left the subshell with status 0 and whose scan block result arms ended with status 0; current forms were not re-run, and gate bash -n and ShellCheck passes cover them.
- local-syntax (DEMONSTRATED; appwrite, pb-docs, appwrite-docs): All three bash fences have recorded local lint/syntax success, not live service evidence; ShellCheck version is recorded only in the body. The runs covered earlier forms, whose guard refusals left the subshell with status 0 and whose scan block result arms ended with status 0; current forms were not re-run, and gate bash -n and ShellCheck passes cover them.
- source-limits (REASONED; appwrite-docs, pb-docs, appwrite, utopia-php-database): PocketBase CLI/--dev, Appwrite 2.7.0 requester/call-site and utopia-php/database 10.1.0 role matching and status/skip pins are cited; Database-level read checks and dispatch are not established at 10.1.0. SQL, Memory, Redis and Pool reads are traced; deployment adapters are unknown and live authorization is not demonstrated.
- source-limits-sql-get (REASONED; utopia-php-database): At 10.1.0 MariaDB, MySQL, Postgres and SQLite use SQL getDocument; without joins it selects by ID, adds a tenant clause under shared tables and has no adapter authorization check, while join queries add the find permission hooks under the same gates. Whether Database read checks accept collection roles as at 7.3.9 is not established.
- source-limits-sql-find (REASONED; utopia-php-database): At 10.1.0 SQL find defaults to read and takes shared authorization roles; with status enabled it adds the main collection's permission hook only for documentSecurity on or the metadata collection, skipping a granted collection on join or bounded-page paths, plus a hook per joined table unless the collection's join map disables it. Database-level grant skipping is not established.
- source-limits-sql-predicate (REASONED; utopia-php-database): At 10.1.0 the SQL permission hook matches requester roles and action in the collection's permissions side table with bound parameters and a shared-table tenant filter, returning 1 = 0 for no roles; Postgres overrides it with OR-ed JSONB containment tests on each row's permissions column, also 1 = 0 for no roles.
- source-limits-sql-disabled (REASONED; utopia-php-database): This guide reasons from the 10.1.0 SQL code that disabled authorization omits find permission filtering while query conditions, ordering and pagination remain, and that SQL getDocument without joins has no adapter authorization check to bypass; whether Database read checks are bypassed at 10.1.0 is not established.
- source-limits-mongo (REASONED; utopia-php-database): At 10.1.0 Mongo getDocument filters by _uid through a tenant hook with no adapter authorization check; Mongo find passes its filters through a Mongo permission read hook whose code was not read, so its status gate and permission strings are not established at 10.1.0, with no live authorization demonstration.
- source-limits-memory-redis (REASONED; utopia-php-database): At 10.1.0 Memory, intended for tests, fixtures and ephemeral workloads, and Redis, mirroring its surface, check no authorization in getDocument; their find paths keep only IDs matching requester roles for the action while authorization is enabled, without testing documentSecurity. This guide reasons that disabled status omits that filtering.
- source-limits-pool (REASONED; utopia-php-database): At 10.1.0 Pool delegates getDocument and find to a pooled or pinned adapter, first setting its database, namespace, shared tables, tenant, tenant-per-document mode, authorization and locks from Pool's own; withTransaction does this before pinning. This guide reasons that a Pool-wrapped adapter reads with the authorization instance the database set.
- source-limits-appwrite-adapter (REASONED; appwrite, utopia-php-database): Appwrite 2.7.0's _APP_DB_ADAPTER (since 1.9.0) defaults to postgresql; pool registration maps the mariadb, mongodb, mysql and postgresql schemes to the MariaDB, Mongo, MySQL and Postgres adapters, DocumentsDB accepts only mongodb, and the factory wraps pools in Pool, with tenant databases getting the shared authorization. Which adapter a given deployment uses is not established.
- source-limits-appwrite-dev (REASONED; appwrite): Appwrite 2.7.0's development .env sets _APP_DB_ADAPTER=postgresql, a development default, not a production default; the root Compose file, which the install task reads as its Compose template, passes the variable to the appwrite service without a value. The 2.7.0 upgrade task keeps an installation's engine, assuming MariaDB when neither Compose nor .env sets _APP_DB_ADAPTER.
- source-limits-appwrite-console (REASONED; appwrite): Appwrite 2.7.0's console variables endpoint reports _APP_DB_ADAPTER with a mariadb fallback while pool registration falls back to postgresql, so by source reading an unset variable, and by this guide's inference an empty one, gives Postgres pools and a reported mariadb. Both read a set variable; this guide advises not relying on the reported value to identify the adapter.
- source-limits-appwrite-install-env (REASONED; appwrite): Appwrite 2.7.0's install task writes _APP_DB_ADAPTER to .env, unless reusing a configuration, from a prompt answer, its database (default postgresql, or detected) or the web installer's choice (default postgresql). Its Compose generator keeps only the chosen database service and, this guide reasons, the value-less entry, which the first detection step skips; how Compose resolves it is unknown.
- source-limits-adapter-docs (REASONED; appwrite-docs, appwrite): As served on 2026-11-04, Appwrite's environment documentation lists MariaDB and MongoDB and gives _APP_DB_ADAPTER a mongodb default, conflicting with Appwrite 2.7.0, which defaults to postgresql, a value that page does not list.

````json
{
  "schema": 1,
  "checked": "2026-11-05",
  "documentation_checked": "2026-11",
  "body_sha256": "325ea5d1c0b70ba017390ef84fa6b7bbab896d136a28dc0e9869eb6253e80460",
  "components": {
    "pb": {
      "name": "PocketBase",
      "basis": "v0.41.1",
      "sources": {
        "sdac3a0528b21": "https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/installer.go?rev=v0.41.1",
        "s3e36d8dfb361": "https://ganigeorgiev.com/pocketbase/pocketbase/files/cmd/serve.go?rev=v0.41.1",
        "sc2185c0270bd": "https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/serve.go?rev=v0.41.1",
        "s6e16f42cec77": "https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/middlewares.go?rev=v0.41.1",
        "scbc7a105fefc": "https://ganigeorgiev.com/pocketbase/pocketbase/files/core/record_query.go?rev=v0.41.1",
        "s225b010fcdc5": "https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/record_crud.go?rev=v0.41.1",
        "s6c3b8a802406": "https://ganigeorgiev.com/pocketbase/pocketbase/files/core/collection_model_auth_options.go?rev=v0.41.1",
        "s30d6893c77b6": "https://ganigeorgiev.com/pocketbase/pocketbase/files/core/settings_model.go?rev=v0.41.1",
        "sc2c33a37ae40": "https://ganigeorgiev.com/pocketbase/pocketbase/files/core/base.go?rev=v0.41.1",
        "s64408cd7e99a": "https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/file.go?rev=v0.41.1",
        "s887df2263cf6": "https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/realtime.go?rev=v0.41.1",
        "s4013de5446a0": "https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/backup.go?rev=v0.41.1",
        "sc0c18faa3a10": "https://ganigeorgiev.com/pocketbase/pocketbase/files/core/backup_create.go?rev=v0.41.1",
        "s2ae84f3f32ec": "https://ganigeorgiev.com/pocketbase/pocketbase/files/apis/middlewares_rate_limit.go?rev=v0.41.1",
        "s38c247ab536b": "https://ganigeorgiev.com/pocketbase/pocketbase/files/pocketbase.go?rev=v0.41.1",
        "s1146d8d23620": "https://ganigeorgiev.com/pocketbase/pocketbase/files/tools/osutils/run.go?rev=v0.41.1",
        "s958702d638d0": "https://ganigeorgiev.com/pocketbase/pocketbase/releases?expr=tag%3D%22v0.41.0%22"
      }
    },
    "appwrite": {
      "name": "Appwrite",
      "basis": "2.7.0",
      "sources": {
        "s6bb4fe4aeed0": "https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/config/variables.php",
        "s2ce76c61491b": "https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/.env",
        "sd96c9b2ddc30": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Account/Http/Account/Create.php#L109-L134",
        "s535fef1a5540": "https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/controllers/shared/api.php",
        "s7a257b8fa05b": "https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/controllers/general.php",
        "seb281dd186ea": "https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/src/Appwrite/Platform/Modules/Storage/Http/Buckets/Create.php",
        "sd13079dcf7cd": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Create.php#L88-L90",
        "s389cba971534": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Create.php#L134-L139",
        "sababfed68086": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Create.php#L217-L218",
        "s1af8437dd494": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Create.php#L238-L288",
        "s77e2ce52136f": "https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/src/Appwrite/Platform/Modules/Functions/Http/Functions/Create.php",
        "s1c49e69946a1": "https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/init/constants.php",
        "s80913a396c73": "https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/docker-compose.yml",
        "s8222d84642bc": "https://github.com/appwrite/appwrite/blob/2.7.0/composer.lock#L4429-L4439",
        "sbf22f36f3eaf": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Get.php#L82-L97",
        "sfa704d5d52d2": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Get.php#L105-L132",
        "s4704dc36131d": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Utopia/Database/Documents/User.php#L82-L116",
        "s9c364b4988f9": "https://github.com/appwrite/appwrite/blob/2.7.0/app/controllers/shared/api.php#L146-L167",
        "sdc161a81e5f1": "https://github.com/appwrite/appwrite/blob/2.7.0/app/controllers/shared/api.php#L328-L361",
        "seae8fbd82294": "https://github.com/appwrite/appwrite/blob/2.7.0/app/controllers/shared/api.php#L396-L400",
        "s02d278fc618d": "https://github.com/appwrite/appwrite/blob/2.7.0/app/controllers/shared/api.php#L557-L561",
        "s4a5ab116894c": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Create.php#L230-L236",
        "s298b295bc4a2": "https://github.com/appwrite/appwrite/blob/2.7.0/app/init/registers.php#L45-L99",
        "s90d9a92f0ed4": "https://github.com/appwrite/appwrite/blob/2.7.0/app/init/registers.php#L239-L252",
        "s8ed5acf4fc13": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Database/Factory.php#L123-L201",
        "s495c0d1f4835": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Database/Factory.php#L208-L211",
        "s3e984f6f58a1": "https://github.com/appwrite/appwrite/blob/2.7.0/app/init/resources/request.php#L1112-L1159",
        "se35f39b4f087": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Upgrade.php#L73-L98",
        "s320dd52ad7ad": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L563-L568",
        "s34cf9f92e6fb": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L664-L671",
        "s781b997e5328": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Get.php#L109-L124",
        "s32cdcbef66a2": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Databases/TransactionState.php#L92-L94",
        "s7061d34674a8": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Database/Factory.php#L12",
        "s43512ed49a8b": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Console/Http/Variables/Get.php#L118",
        "sc7cb880ebc53": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Utopia/Response/Model/ConsoleVariables.php#L130-L138",
        "sbdd71fb0bdee": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L81",
        "s7c7d516c2e29": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L234-L239",
        "s354c70b426e9": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L299-L307",
        "s3f837fcdd474": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L318-L319",
        "sf0bdc23845a6": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L550-L555",
        "s8194e1cb510c": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L708-L721",
        "s7649c24d59ac": "https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/app/views/install/env.phtml",
        "sfe2ab69d5301": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Databases/TransactionState.php#L70-L108",
        "s20b34941cb2a": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Databases/TransactionState.php#L675-L706",
        "s39e9760a01ee": "https://github.com/appwrite/appwrite/blob/2.7.0/app/init/resources/request.php#L234-L238",
        "sa0f0758379af": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Upgrade.php#L108-L110",
        "s8bd7139f8949": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L214-L233",
        "s48b953e7a273": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L1709-L1728",
        "sade59f0be4d6": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L253-L262",
        "s3fc2bb20c0bb": "https://github.com/appwrite/appwrite/blob/2.7.0/app/views/install/installer/templates/steps/step-1.phtml#L11-L20",
        "s2ab6c91f62fd": "https://github.com/appwrite/appwrite/blob/2.7.0/app/views/install/installer/templates/steps/step-1.phtml#L66-L108",
        "s824989859386": "https://github.com/appwrite/appwrite/blob/2.7.0/app/views/install/installer.phtml#L12",
        "s5fb71939c4b6": "https://github.com/appwrite/appwrite/blob/2.7.0/app/views/install/installer/js/modules/progress.js#L408",
        "s254e58212ad0": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L150-L161",
        "s595b0f259c3a": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L238-L246",
        "s3a92a2e12968": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L202-L225",
        "s7e549280b454": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L248-L285",
        "s9cb7dec752e3": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L313",
        "s79502c89f0ed": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L320-L322",
        "s830783806300": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Installer/Http/Installer/Install.php#L380-L394",
        "s2851b656753a": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L440-L473",
        "s1141172bac7f": "https://raw.githubusercontent.com/appwrite/appwrite/2.7.0/src/Appwrite/Docker/Compose/Generator.php",
        "sa7170a7b4946": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose/Generator.php#L9-L26",
        "sc31ddc8f2659": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose/Generator.php#L145-L153",
        "se6ecc9107190": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose/Generator.php#L188-L210",
        "s2e99d3590696": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose.php#L16-L27",
        "s0ea4f620650f": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Compose/Service.php#L32-L33",
        "sdfd43737a7ac": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Docker/Env.php#L37-L42",
        "s2f6df67b8aea": "https://github.com/appwrite/appwrite/blob/2.7.0/packages/system/src/System.php#L703-L706",
        "sdbcf25c4f59a": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Utopia/Database/Documents/User.php#L211-L218",
        "sad0f2bc8be8f": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Account/Http/Account/Get.php#L27-L30",
        "sd0c2d9cf89f4": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Utopia/Database/Documents/User.php#L230-L244",
        "sec3eb7219b94": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Account/Http/Account/MFA/Update.php#L81-L84",
        "s3ea65093a0fb": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Modules/Account/Http/Account/MFA/Challenges/Update.php#L165-L177",
        "se24bc37a7000": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Auth/MFA/Challenge/TOTP.php#L30-L88",
        "s3d7f866403ab": "https://github.com/appwrite/appwrite/blob/2.7.0/app/init/constants.php#L266",
        "s8208896c2c22": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Auth/EncryptionKey.php#L11-L69",
        "sd987a4f33938": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Auth/JobsSecret.php#L20-L32",
        "s296ddae6efd8": "https://github.com/appwrite/appwrite/blob/2.7.0/src/Appwrite/Platform/Tasks/Install.php#L331",
        "s1da118060657": "https://github.com/appwrite/appwrite/releases/tag/2.3.0",
        "sf22fdc1ed786": "https://github.com/appwrite/appwrite/releases/tag/2.4.0",
        "s4d8a36b7651f": "https://github.com/appwrite/appwrite/releases/tag/2.6.2",
        "sc92fc6843e8a": "https://github.com/appwrite/appwrite/releases/tag/2.7.0"
      }
    },
    "pb-docs": {
      "name": "PocketBase documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s9029ab974cf1": "https://pocketbase.io/docs/going-to-production/",
        "saedbdfbdfc48": "https://pocketbase.io/docs/api-rules-and-filters/",
        "s773e441dd51c": "https://pocketbase.io/docs/authentication/",
        "sf711b6345643": "https://pocketbase.io/docs/files-handling/",
        "sb850a71fad4d": "https://pocketbase.io/docs/api-realtime/"
      }
    },
    "appwrite-docs": {
      "name": "Appwrite documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s4a965bdeeb98": "https://appwrite.io/docs/advanced/self-hosting/production/security",
        "saa37bb5d4d7e": "https://appwrite.io/docs/partners/project/api-keys",
        "sa0bd132f7968": "https://appwrite.io/docs/advanced/security/permissions",
        "s58ad28816c5d": "https://appwrite.io/docs/products/databases/tablesdb/legacy/permissions",
        "s2bf9a4746d28": "https://appwrite.io/docs/advanced/self-hosting/configuration/environment-variables",
        "s000d05106450": "https://appwrite.io/docs/advanced/security/rate-limits",
        "s38a1efa0c7d2": "https://appwrite.io/docs/advanced/self-hosting/configuration/email",
        "s256ef73f7b85": "https://appwrite.io/docs/advanced/self-hosting/production/backups",
        "s221c6aaef8df": "https://appwrite.io/docs/advanced/security/mfa"
      }
    },
    "utopia-php-database": {
      "name": "utopia-php/database",
      "basis": "10.1.0",
      "sources": {
        "s84fe9d3d1ab5": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Permission.php#L176-L180",
        "s275a3120b495": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Document.php#L273-L334",
        "s655e2f6c04a0": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Document.php#L405-L416",
        "s4a3f8adc3023": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Validator/Authorization.php#L59-L102",
        "s000a4b53503d": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Database.php#L52-L61",
        "sa8f4d7b8a48c": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Database.php#L1033-L1039",
        "safe798d5dd9c": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Database.php#L1162-L1183",
        "s2feb9534db52": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Validator/Authorization.php#L10-L41",
        "sc00b8981307b": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Validator/Authorization.php#L148-L208",
        "s41c5bffe6075": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L650-L779",
        "s1d79e9cf0e57": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L1566-L1572",
        "s7bf0e65d6cf0": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L5063-L5079",
        "s0ae9c48f1b01": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L5081-L5112",
        "sb95aa1aa9ed9": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L5179-L5183",
        "sc3379278f3f2": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L5185-L5213",
        "s9e70fd6370ea": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L6080-L6086",
        "s7c5f032eabba": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL.php#L3658-L3678",
        "s6a26dc1f9801": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQL/Hook/Permission/Filter.php#L72-L116",
        "sc9e144475031": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Postgres.php#L1909-L1958",
        "s361b4b790fbf": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/MariaDB.php#L46",
        "s699a2c766b74": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/MySQL.php#L25",
        "s07bdbc102182": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Postgres.php#L53",
        "s402631b77efa": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQLite.php#L71",
        "s97013afdaf6d": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/SQLite.php#L249-L259",
        "sda6b15e8a7f2": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Mongo.php#L57",
        "sf19fad9126ff": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Mongo.php#L1561-L1603",
        "s68e7d8672204": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Mongo.php#L249-L282",
        "s08b8af0098a5": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Mongo.php#L2402-L2413",
        "s915a0850c1bf": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Pool.php#L36-L138",
        "s8795cdff3377": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Pool.php#L178-L186",
        "sde36e9303448": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Pool.php#L517-L541",
        "sa151e5aefbf8": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Pool.php#L802-L807",
        "s7edf5f1161c1": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Pool.php#L884-L889",
        "s9613234b8f17": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Pool.php#L1101-L1106",
        "s70895d208fe4": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Memory.php#L3-L5",
        "s1a92600403ce": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Memory.php#L36-L48",
        "s604f86d30464": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Memory.php#L1204-L1227",
        "s4aec3fdda679": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Memory.php#L1807-L1836",
        "se488122e644f": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Memory.php#L2397-L2452",
        "sab16fda30b23": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Memory.php#L3108-L3141",
        "s970890cdc753": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Redis.php#L5-L8",
        "s91c17eccdca7": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Redis.php#L41-L57",
        "s784f964c7ba3": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Redis.php#L882-L916",
        "s2c28e6247d1d": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Redis.php#L1482-L1519",
        "sd26ea42ec217": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Redis.php#L1938-L1973",
        "s1336d62998d1": "https://github.com/utopia-php/database/blob/950a4907d5519efd7ac7d1aff8978e482f8e07ae/src/Database/Adapter/Redis.php#L2809-L2823"
      }
    },
    "curl": {
      "name": "curl",
      "basis": "curl-8_14_1",
      "sources": {
        "s5e1383feef7d": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/write-out.md#L75-L79",
        "s3db522258e44": "https://raw.githubusercontent.com/curl/curl/curl-8_14_1/docs/cmdline-opts/header.md",
        "s82a34ee18632": "https://raw.githubusercontent.com/curl/curl/curl-8_14_1/docs/cmdline-opts/config.md"
      }
    }
  },
  "claims": {
    "pb-bootstrap": {"text": "Privately bootstrap through the logged installer URL; superuser create EMAIL PASS exposes passwords in argv. Ordinary registration does not grant superuser rights.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:s9029ab974cf1", "pb:sdac3a0528b21"], "status": "REASONED"},
    "pb-installer": {"text": "Installer system-superuser token lasts about 30 minutes; protect its URL and startup logs as credentials.", "components": ["pb"], "sources": ["pb:sdac3a0528b21"], "status": "REASONED"},
    "pb-ips": {"text": "Superuser IP allowlists are available from v0.38.0; superuserIPs defaults empty and restricts authenticated requests, not /_/ static assets.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:s9029ab974cf1", "pb:s6e16f42cec77"], "status": "REASONED"},
    "pb-tls": {"text": "serve with a domain provides native HTTPS/ACME; alternatively terminate TLS at a reverse proxy.", "components": ["pb"], "sources": ["pb:sc2185c0270bd"], "status": "REASONED"},
    "pb-bind": {"text": "Without a domain serve defaults to 127.0.0.1:8090; with a domain it uses 0.0.0.0:80/443. Behind a local proxy omit the domain and set --http loopback.", "components": ["pb"], "sources": ["pb:s3e36d8dfb361"], "status": "REASONED"},
    "pb-origins": {"text": "--origins defaults * and accepts comma-separated allowed origins; CORS does not authorize records.", "components": ["pb"], "sources": ["pb:s3e36d8dfb361"], "status": "REASONED"},
    "pb-proxy": {"text": "Trust only headers the proxy overwrites, review useLeftmostIP ordering and block direct backend access to protect IP/rate controls.", "components": ["pb"], "sources": ["pb:s30d6893c77b6"], "status": "REASONED"},
    "pb-dev": {"text": "--dev adds diagnostics including SQL on stderr, not an auth bypass; its configured default comes from New(): true if os.Args[0] starts with a nonempty os.TempDir() or cacheDir() prefix, false otherwise.", "components": ["pb"], "sources": ["pb:sc2c33a37ae40", "pb:s38c247ab536b", "pb:s1146d8d23620"], "status": "REASONED"},
    "pb-cli": {"text": "In the pinned CLI wrapper, Start() registers the serve and superuser commands on the root command and executes it.", "components": ["pb"], "sources": ["pb:s38c247ab536b"], "status": "REASONED"},
    "pb-rules": {"text": "Each list/view/create/update/delete rule defaults null (superuser-only); empty opens to guests and nonempty filters. Superusers bypass rules.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:saedbdfbdfc48", "pb:scbc7a105fefc"], "status": "REASONED"},
    "pb-manage": {"text": "Top-level manageRule defaults null and permits privileged auth-record changes alongside create/update rules; its validator rejects empty-string rules.", "components": ["pb"], "sources": ["pb:s6c3b8a802406"], "status": "REASONED"},
    "pb-files": {"text": "File fields default unprotected despite locked record rules; Protected plus an authorized viewRule gates downloads, while a public viewRule still permits public access.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:sf711b6345643", "pb:s64408cd7e99a"], "status": "REASONED"},
    "pb-file-token": {"text": "Short-lived file tokens provide identity context, not file authorization; viewRule decides. Protect token-bearing file URLs.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:sf711b6345643", "pb:s64408cd7e99a"], "status": "REASONED"},
    "pb-realtime": {"text": "Collection subscriptions use listRule and individual-record subscriptions viewRule; SSE/subscription success does not prove event authorization.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:sb850a71fad4d", "pb:s887df2263cf6"], "status": "REASONED"},
    "pb-password": {"text": "Auth initialization enables password authentication with email as the identity field.", "components": ["pb"], "sources": ["pb:s6c3b8a802406"], "status": "REASONED"},
    "pb-oauth": {"text": "OAuth2 defaults disabled and is unsupported for _superusers.", "components": ["pb", "pb-docs"], "sources": ["pb:s6c3b8a802406", "pb-docs:s773e441dd51c"], "status": "REASONED"},
    "pb-mfa-default": {"text": "MFA defaults disabled with duration 600 seconds.", "components": ["pb"], "sources": ["pb:s6c3b8a802406"], "status": "REASONED"},
    "pb-otp-default": {"text": "OTP defaults disabled with duration 180 seconds and length 8.", "components": ["pb"], "sources": ["pb:s6c3b8a802406"], "status": "REASONED"},
    "pb-alerts": {"text": "Authentication alerts default enabled; retain alerts and provide working email.", "components": ["pb"], "sources": ["pb:s6c3b8a802406"], "status": "REASONED"},
    "pb-auth-token": {"text": "Auth token duration defaults to 432000 seconds.", "components": ["pb"], "sources": ["pb:s6c3b8a802406"], "status": "REASONED"},
    "pb-file-duration": {"text": "File token duration defaults to 180 seconds.", "components": ["pb"], "sources": ["pb:s6c3b8a802406"], "status": "REASONED"},
    "pb-auth-rule": {"text": "authRule defaults empty; verified-only collections can require verified = true after email verification works.", "components": ["pb", "pb-docs"], "sources": ["pb:s6c3b8a802406", "pb-docs:s773e441dd51c"], "status": "REASONED"},
    "pb-mfa": {"text": "For superusers retain password auth and enable both OTP and MFA; empty mfa.rule applies to everyone. OTP alone is not a second factor.", "components": ["pb", "pb-docs"], "sources": ["pb:s6c3b8a802406", "pb-docs:s773e441dd51c"], "status": "REASONED"},
    "pb-logout": {"text": "Stateless authentication means clearing pb.authStore removes only the local copy, not a stolen token.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:s773e441dd51c", "pb:scbc7a105fefc"], "status": "REASONED"},
    "pb-encryption": {"text": "Settings default to plaintext JSON; select a 32-character environment secret with --encryptionEnv. This encrypts settings, not the whole database or files.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:s9029ab974cf1", "pb:s30d6893c77b6"], "status": "REASONED"},
    "pb-backups": {"text": "Backups default local with empty cron (automatic backups off); archives contain main and logs databases plus remaining pb_data, excluding the backups directory and tracked exclusions; uploaded collection files on S3 require manual backup. Schedule/retain deliberately and protect archives.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:s9029ab974cf1", "pb:s30d6893c77b6", "pb:sc0c18faa3a10"], "status": "REASONED"},
    "pb-backup-auth": {"text": "Backup downloads require a superuser file token and obey superuser IP restrictions; ordinary auth/file tokens do not suffice.", "components": ["pb"], "sources": ["pb:s4013de5446a0"], "status": "REASONED"},
    "pb-limiter": {"text": "Native limits exist from v0.23.0 but default disabled at v0.41.1; enable rateLimits.enabled.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:s9029ab974cf1", "pb:s30d6893c77b6"], "status": "REASONED"},
    "pb-limit-rules": {"text": "Seeded limits are *:auth 2/3s, *:create 20/5s, /api/batch 3/1s and /api/ 300/10s.", "components": ["pb"], "sources": ["pb:s30d6893c77b6"], "status": "REASONED"},
    "pb-limit-bypass": {"text": "Superusers and rateLimits.excludedIPs bypass limits; test ordinary non-excluded clients.", "components": ["pb"], "sources": ["pb:s2ae84f3f32ec"], "status": "REASONED"},
    "pb-smtp": {"text": "smtp.enabled and smtp.tls default false; disabled SMTP falls back to sendmail. Configure protected transport and test actual delivery.", "components": ["pb"], "sources": ["pb:s30d6893c77b6", "pb:sc2c33a37ae40"], "status": "REASONED"},
    "pb-forge": {"text": "From v0.41.0 PocketBase publishes its source and releases on its author's forge at ganigeorgiev.com, which this guide cites at v0.41.1; the v0.41.0 notes flag only the Go module's move to the new host, and no guide statement depends on the module path.", "components": ["pb"], "sources": ["pb:s958702d638d0"], "status": "REASONED"},
    "appwrite-https": {"text": "API FORCE_HTTPS and function/site ROUTER_FORCE_HTTPS default disabled at 2.7.0; explicitly enable both despite conflicting rolling deprecation/default documentation.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite:s6bb4fe4aeed0", "appwrite:s7a257b8fa05b", "appwrite-docs:s2bf9a4746d28"], "status": "REASONED"},
    "appwrite-hosts": {"text": "ROUTER_PROTECTION defaults disabled; configure actual domains and enable rejection of unknown hostnames.", "components": ["appwrite"], "sources": ["appwrite:s6bb4fe4aeed0", "appwrite:s7a257b8fa05b"], "status": "REASONED"},
    "appwrite-registration": {"text": "Console root-only registration defaults enabled with empty email/IP allowlists; these restrict account creation, not dashboard reachability or login.", "components": ["appwrite"], "sources": ["appwrite:s6bb4fe4aeed0", "appwrite:sd96c9b2ddc30"], "status": "REASONED"},
    "appwrite-console": {"text": "Claim the first operator privately and use a separate network/access boundary for a private dashboard.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite-docs:s4a965bdeeb98", "appwrite:sd96c9b2ddc30"], "status": "REASONED"},
    "appwrite-console-url": {"text": "Since 2.3.0, _APP_CONSOLE_URL is the origin console links are built from and replaces the removed _APP_CONSOLE_URL_SCHEME; 2.7.0 defaults it to empty and its Compose file passes it to the appwrite service without a value, so set it when the console host differs from the API.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite:s1da118060657", "appwrite:s6bb4fe4aeed0", "appwrite:s80913a396c73", "appwrite-docs:s2bf9a4746d28"], "status": "REASONED"},
    "appwrite-mfa": {"text": "Enroll and verify operator TOTP, protect recovery codes; at 2.7.0 enabled MFA with a verified factor requires a second session factor, a spent TOTP time step cannot be reused, and turning MFA off needs a session challenge from the last 1800 seconds.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite-docs:s221c6aaef8df", "appwrite:s535fef1a5540", "appwrite:sdbcf25c4f59a", "appwrite:se24bc37a7000", "appwrite:s3ea65093a0fb", "appwrite:sec3eb7219b94", "appwrite:sd0c2d9cf89f4", "appwrite:s3d7f866403ab", "appwrite:sc92fc6843e8a"], "status": "REASONED"},
    "appwrite-dev-env": {"text": "Development env disables root-only registration, abuse and router protection and carries placeholders; do not inherit it for production.", "components": ["appwrite"], "sources": ["appwrite:s2ce76c61491b"], "status": "REASONED"},
    "appwrite-recreate": {"text": "Apply env/Compose changes with docker compose up -d from the install directory, then check effective behavior.", "components": ["appwrite-docs"], "sources": ["appwrite-docs:s4a965bdeeb98"], "status": "REASONED"},
    "appwrite-permissions": {"text": "Collection and document grants are additive according to legacy documentation; documentSecurity defaults false in Appwrite 2.7.0 and must be enabled for document grants. The pinned parameter description states the need for one permission level.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite:sd13079dcf7cd", "appwrite-docs:s58ad28816c5d"], "status": "REASONED"},
    "appwrite-creation": {"text": "For null or omitted document permissions, the pinned aggregate helper preserves null before the handler assigns read/update/delete user grants to a nonprivileged requester with a user ID, or an empty list otherwise. API-key classification skips role validation but does not itself determine the default list. Use specific users/teams for private data.", "components": ["appwrite", "appwrite-docs", "utopia-php-database"], "sources": ["appwrite:s389cba971534", "appwrite:sababfed68086", "appwrite:s1af8437dd494", "appwrite-docs:sa0bd132f7968", "appwrite:s8222d84642bc", "utopia-php-database:s84fe9d3d1ab5"], "status": "REASONED"},
    "appwrite-read-path": {"text": "Document GET classifies requesters by authorization role (keys; owner/developer/admin privileged), reports disabled databases/collections as not found to others and, without a transaction ID, fetches through the database layer, which gets collection permissions and documentSecurity at collection creation. With one, staged creates come from the pending transaction's logs.", "components": ["appwrite"], "sources": ["appwrite:sbf22f36f3eaf", "appwrite:sfa704d5d52d2", "appwrite:s781b997e5328", "appwrite:s4704dc36131d", "appwrite:s4a5ab116894c", "appwrite:s32cdcbef66a2", "appwrite:sfe2ab69d5301", "appwrite:s20b34941cb2a"], "status": "REASONED"},
    "appwrite-requester": {"text": "With an API key the request role and scopes come from the key, plus public at 2.7.0; a standard, ephemeral or dynamic project key for the same project sets the current authorization status to disabled, as do admin-mode console sessions outside the console and organization project read routes, while route scope validation applies to every requester.", "components": ["appwrite"], "sources": ["appwrite:s9c364b4988f9", "appwrite:sdc161a81e5f1", "appwrite:seae8fbd82294", "appwrite:s02d278fc618d"], "status": "REASONED"},
    "appwrite-keys": {"text": "Properly scoped server API keys bypass resource permissions but still obey operation scopes; treat keys.write as admin-equivalent: release notes since 2.6.2 say a key cannot grant scopes it does not hold, which the served page does not reflect, but the 2.7.0 key handlers were not read. Keys never belong in clients.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite:s535fef1a5540", "appwrite-docs:saa37bb5d4d7e", "appwrite:s4d8a36b7651f", "appwrite:sc92fc6843e8a", "appwrite:s77e2ce52136f"], "status": "REASONED"},
    "appwrite-key-creation": {"text": "The served API keys page says creating API keys with the Project API is deprecated as of 17 August 2026 and long-lived keys are created in the Console, while the Project API can still list, update and delete keys and issue ephemeral keys.", "components": ["appwrite-docs"], "sources": ["appwrite-docs:saa37bb5d4d7e"], "status": "REASONED"},
    "appwrite-encryption": {"text": "Fresh 2.7.0 installs generate _APP_OPENSSL_KEY_V1 while existing and upgraded installs keep their stored value, so replace a remaining your-secret-key placeholder before production data; preserve every key version that still decrypts data, since loss strands encrypted secrets.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite:s6bb4fe4aeed0", "appwrite:s8208896c2c22", "appwrite:s2851b656753a", "appwrite:s296ddae6efd8", "appwrite:sf22fdc1ed786", "appwrite:sc92fc6843e8a", "appwrite-docs:s256ef73f7b85"], "status": "REASONED"},
    "appwrite-backups": {"text": "Back up database, persistent storage and deployment configuration; restrict access and test restoration in a separate installation.", "components": ["appwrite-docs"], "sources": ["appwrite-docs:s256ef73f7b85"], "status": "REASONED"},
    "appwrite-abuse": {"text": "_APP_OPTIONS_ABUSE defaults enabled but dev env disables it; server API-key and owner, developer or admin requests are exempt, so test with ordinary clients.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite:s6bb4fe4aeed0", "appwrite:s2ce76c61491b", "appwrite:s535fef1a5540", "appwrite-docs:s000d05106450"], "status": "REASONED"},
    "appwrite-smtp": {"text": "SMTP host/port/secure/username/password default empty and empty host disables sending; configure the provider and confirm message receipt/use.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite:s6bb4fe4aeed0", "appwrite-docs:s38a1efa0c7d2"], "status": "REASONED"},
    "appwrite-storage": {"text": "Storage defaults local, upload limit 30000000 and server antivirus disabled; enabling scanning requires configured reachable ClamAV.", "components": ["appwrite"], "sources": ["appwrite:s6bb4fe4aeed0"], "status": "REASONED"},
    "appwrite-bucket": {"text": "New bucket permissions are empty and fileSecurity=false; enable per-file security deliberately, since bucket grants also permit access.", "components": ["appwrite"], "sources": ["appwrite:seb281dd186ea"], "status": "REASONED"},
    "appwrite-bucket-options": {"text": "Bucket encryption and antivirus default true; bucket antivirus does not enable the server scanner.", "components": ["appwrite"], "sources": ["appwrite:seb281dd186ea"], "status": "REASONED"},
    "appwrite-size": {"text": "Encryption/scanning skip files above 20000000 bytes; cap maximumFileSize at that threshold when either is mandatory and test the boundary.", "components": ["appwrite"], "sources": ["appwrite:seb281dd186ea", "appwrite:s1c49e69946a1"], "status": "REASONED"},
    "appwrite-functions": {"text": "Function execute roles and execution-key scopes default empty; grant narrowly. Disabled functions still admit authorized Server SDK API keys.", "components": ["appwrite"], "sources": ["appwrite:s77e2ce52136f"], "status": "REASONED"},
    "appwrite-executor": {"text": "Keep executor/orchestrator private and protect Docker-socket authority; fresh 2.7.0 installs generate _APP_EXECUTOR_SECRET but existing and upgraded installs keep theirs, so replace a remaining placeholder. Container execution is not demonstrated hostile-tenant isolation.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite:s80913a396c73", "appwrite:s6bb4fe4aeed0", "appwrite:s2851b656753a", "appwrite:s4d8a36b7651f", "appwrite-docs:s2bf9a4746d28"], "status": "REASONED"},
    "appwrite-docs-lag": {"text": "As served on 2026-11-04, the MFA page omits 2.7.0's single-use TOTP codes and recent challenge to turn MFA off, the security and backups pages its key rotation, the environment page the generated encryption key and executor secret, the API keys page key scope limits, and the security page says no unique encryption key is generated; the guide states each from release notes and source.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite-docs:s221c6aaef8df", "appwrite-docs:s4a965bdeeb98", "appwrite-docs:s256ef73f7b85", "appwrite-docs:s2bf9a4746d28", "appwrite-docs:saa37bb5d4d7e", "appwrite:sc92fc6843e8a", "appwrite:s4d8a36b7651f", "appwrite:sf22fdc1ed786", "appwrite:se24bc37a7000", "appwrite:sec3eb7219b94", "appwrite:s8208896c2c22", "appwrite:s2851b656753a"], "status": "REASONED"},
    "verify-pb-records": {"text": "Public rules allow guest reads; locked rules deny with 403, unsatisfied list filters can return empty 200 and view rules 404. Retain owner and separate superuser controls.", "components": ["pb-docs", "curl"], "sources": ["pb-docs:saedbdfbdfc48", "curl:s5e1383feef7d", "curl:s3db522258e44"], "status": "REASONED", "verify": [1]},
    "verify-appwrite-records": {"text": "Broad collection grants defeat document restrictions; removing them must deny unrelated users while document grantees succeed. Compare client/server creation defaults.", "components": ["appwrite-docs"], "sources": ["appwrite-docs:s58ad28816c5d", "appwrite-docs:sa0bd132f7968"], "status": "REASONED", "verify": [1]},
    "verify-appwrite-keys": {"text": "A correctly scoped server key reads despite empty permissions, while a key without scope fails; neither substitutes for an ordinary-user control.", "components": ["appwrite"], "sources": ["appwrite:s535fef1a5540"], "status": "REASONED", "verify": [1]},
    "verify-registration": {"text": "On disposable Appwrite fixtures compare open signup 201 with root-only account-limit failure and independent email/IP restrictions; retain login/invitation controls.", "components": ["appwrite"], "sources": ["appwrite:sd96c9b2ddc30"], "status": "REASONED", "verify": [2]},
    "verify-pb-bootstrap": {"text": "Guest and ordinary-user _superusers record creation must fail while a valid installer token creates the private operator; static dashboard assets prove no admin access.", "components": ["pb"], "sources": ["pb:sdac3a0528b21", "pb:s225b010fcdc5"], "status": "REASONED"},
    "verify-appwrite-mfa": {"text": "Console account GET succeeds without MFA, fails for a fresh password-only MFA session, where 2.7.0 throws USER_MORE_FACTORS_REQUIRED with a response string not established here, and succeeds after TOTP completion with a code not already redeemed.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite-docs:s221c6aaef8df", "appwrite:s535fef1a5540", "appwrite:sad0f2bc8be8f", "appwrite:se24bc37a7000"], "status": "REASONED"},
    "verify-pb-writes": {"text": "Compare intended/unauthorized POST/PATCH/DELETE and privileged auth-record management; locked manageRule grants no management and empty-string configuration must fail.", "components": ["pb"], "sources": ["pb:s225b010fcdc5", "pb:s6c3b8a802406"], "status": "REASONED"},
    "verify-pb-files": {"text": "Before protection unsigned file GET works; Protected plus private viewRule rejects guests/unrelated-user file tokens with 404 while permitted-user bytes still arrive.", "components": ["pb", "curl"], "sources": ["pb:s64408cd7e99a", "curl:s82a34ee18632"], "status": "REASONED"},
    "verify-pb-realtime": {"text": "Mutate a fixture while comparing collection and record subscriptions; deny unauthorized event delivery, retaining authorized delivery. PB_CONNECT/acknowledgment alone is insufficient.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:sb850a71fad4d", "pb:s887df2263cf6"], "status": "REASONED"},
    "verify-pb-mfa": {"text": "Compare password-only completion with password-plus-OTP MFA and verified/unverified authRule logins; clearing authStore must not revoke a retained valid token.", "components": ["pb", "pb-docs"], "sources": ["pb:s6c3b8a802406", "pb-docs:s773e441dd51c"], "status": "REASONED"},
    "verify-pb-ips": {"text": "Compare allowed/excluded superuser sources and forged forwarded headers; excluded sources must get 403 and direct backend access must fail with a working proxy control.", "components": ["pb"], "sources": ["pb:s6e16f42cec77", "pb:s30d6893c77b6"], "status": "REASONED"},
    "verify-transport": {"text": "Compare HTTP/HTTPS and certificates, Appwrite API/function/site domains and configured/unknown Host; compare browser origins separately from record authorization.", "components": ["pb", "appwrite"], "sources": ["pb:s3e36d8dfb361", "appwrite:s7a257b8fa05b"], "status": "REASONED"},
    "verify-abuse": {"text": "Cross each configured threshold with ordinary non-excluded clients and compare disabled/enabled controls; PocketBase limiting yields 429 with later successful recovery.", "components": ["pb", "appwrite-docs"], "sources": ["pb:s2ae84f3f32ec", "appwrite-docs:s000d05106450"], "status": "REASONED"},
    "verify-email": {"text": "Request OTP, verification and recovery messages and confirm receipt and use; request success alone is not delivery evidence.", "components": ["pb", "appwrite-docs"], "sources": ["pb:sc2c33a37ae40", "appwrite-docs:s38a1efa0c7d2"], "status": "REASONED"},
    "verify-pb-recovery": {"text": "Compare plaintext/encrypted persisted settings, restart with retained key and restore local/S3 data; only permitted superuser file tokens may download backups.", "components": ["pb", "pb-docs"], "sources": ["pb:s30d6893c77b6", "pb:s4013de5446a0", "pb-docs:s9029ab974cf1"], "status": "REASONED"},
    "verify-appwrite-recovery": {"text": "Restore encrypted fixtures with the original key; a separate wrong-key fixture must not recover encrypted values.", "components": ["appwrite-docs"], "sources": ["appwrite-docs:s256ef73f7b85"], "status": "REASONED"},
    "verify-uploads": {"text": "Compare permitted/unrelated uploads and size-boundary fixtures; mandatory processing requires rejecting over-limit files and confirming accepted-file encryption/scanning.", "components": ["appwrite"], "sources": ["appwrite:seb281dd186ea", "appwrite:s1c49e69946a1"], "status": "REASONED"},
    "verify-functions": {"text": "Compare intended execute roles, unrelated users and privileged server keys, including disabled functions; confirm executor/orchestrator privacy from a second host.", "components": ["appwrite"], "sources": ["appwrite:s77e2ce52136f", "appwrite:s80913a396c73"], "status": "REASONED"},
    "verify-bundle": {"text": "Search filenames using protected exact-secret patterns with a disposable marker control; client bundles must contain neither superuser tokens nor Appwrite API keys, and encoded/split forms can evade scanning.", "components": ["pb-docs", "appwrite-docs"], "sources": ["pb-docs:s773e441dd51c", "appwrite-docs:saa37bb5d4d7e"], "status": "REASONED", "verify": [3]},
    "local-guards": {"text": "Recorded guard tests rejected placeholders and omitted/shortened arguments; this demonstrates shell behavior only, not service access or deployed-bundle scanning. The tests covered earlier forms, whose guard refusals left the subshell with status 0 and whose scan block result arms ended with status 0; current forms were not re-run, and gate bash -n and ShellCheck passes cover them.", "components": ["pb-docs", "appwrite-docs"], "sources": ["pb-docs:saedbdfbdfc48", "appwrite-docs:sa0bd132f7968", "appwrite-docs:saa37bb5d4d7e"], "status": "DEMONSTRATED", "evidence": "Local guard tests refused embedded `REPLACE_WITH_` placeholders, `example.com`, angle brackets, empty arguments, and omitted or shortened `set --` lines."},
    "local-syntax": {"text": "All three bash fences have recorded local lint/syntax success, not live service evidence; ShellCheck version is recorded only in the body. The runs covered earlier forms, whose guard refusals left the subshell with status 0 and whose scan block result arms ended with status 0; current forms were not re-run, and gate bash -n and ShellCheck passes cover them.", "components": ["appwrite", "pb-docs", "appwrite-docs"], "sources": ["pb-docs:saedbdfbdfc48", "appwrite:sd96c9b2ddc30", "appwrite-docs:saa37bb5d4d7e"], "status": "DEMONSTRATED", "evidence": "All three bash blocks passed ShellCheck 0.11.0 and `bash -n` during authoring."},
    "source-limits": {"text": "PocketBase CLI/--dev, Appwrite 2.7.0 requester/call-site and utopia-php/database 10.1.0 role matching and status/skip pins are cited; Database-level read checks and dispatch are not established at 10.1.0. SQL, Memory, Redis and Pool reads are traced; deployment adapters are unknown and live authorization is not demonstrated.", "components": ["appwrite-docs", "pb-docs", "appwrite", "utopia-php-database"], "sources": ["appwrite-docs:s58ad28816c5d", "pb-docs:s9029ab974cf1", "appwrite:s8222d84642bc", "utopia-php-database:s275a3120b495", "utopia-php-database:s655e2f6c04a0", "utopia-php-database:s4a3f8adc3023", "utopia-php-database:s000a4b53503d", "utopia-php-database:sa8f4d7b8a48c", "utopia-php-database:s2feb9534db52", "utopia-php-database:sc00b8981307b", "utopia-php-database:s41c5bffe6075", "utopia-php-database:s1d79e9cf0e57", "utopia-php-database:s7bf0e65d6cf0", "utopia-php-database:sb95aa1aa9ed9", "utopia-php-database:s9e70fd6370ea", "utopia-php-database:s7c5f032eabba", "utopia-php-database:s6a26dc1f9801", "utopia-php-database:sc9e144475031", "utopia-php-database:s361b4b790fbf", "utopia-php-database:s699a2c766b74", "utopia-php-database:s07bdbc102182", "utopia-php-database:s402631b77efa", "utopia-php-database:s97013afdaf6d", "utopia-php-database:sda6b15e8a7f2", "utopia-php-database:sf19fad9126ff", "utopia-php-database:s68e7d8672204", "utopia-php-database:s08b8af0098a5", "utopia-php-database:s915a0850c1bf", "utopia-php-database:s8795cdff3377", "utopia-php-database:sde36e9303448", "utopia-php-database:sa151e5aefbf8", "utopia-php-database:s7edf5f1161c1", "utopia-php-database:s9613234b8f17", "utopia-php-database:s70895d208fe4", "utopia-php-database:s1a92600403ce", "utopia-php-database:s604f86d30464", "utopia-php-database:s4aec3fdda679", "utopia-php-database:se488122e644f", "utopia-php-database:sab16fda30b23", "utopia-php-database:s970890cdc753", "utopia-php-database:s91c17eccdca7", "utopia-php-database:s784f964c7ba3", "utopia-php-database:s2c28e6247d1d", "utopia-php-database:sd26ea42ec217", "utopia-php-database:s1336d62998d1"], "status": "REASONED"},
    "source-limits-sql-get": {"text": "At 10.1.0 MariaDB, MySQL, Postgres and SQLite use SQL getDocument; without joins it selects by ID, adds a tenant clause under shared tables and has no adapter authorization check, while join queries add the find permission hooks under the same gates. Whether Database read checks accept collection roles as at 7.3.9 is not established.", "components": ["utopia-php-database"], "sources": ["utopia-php-database:s41c5bffe6075", "utopia-php-database:s361b4b790fbf", "utopia-php-database:s699a2c766b74", "utopia-php-database:s07bdbc102182", "utopia-php-database:s402631b77efa", "utopia-php-database:s97013afdaf6d", "utopia-php-database:s000a4b53503d"], "status": "REASONED"},
    "source-limits-sql-find": {"text": "At 10.1.0 SQL find defaults to read and takes shared authorization roles; with status enabled it adds the main collection's permission hook only for documentSecurity on or the metadata collection, skipping a granted collection on join or bounded-page paths, plus a hook per joined table unless the collection's join map disables it. Database-level grant skipping is not established.", "components": ["utopia-php-database"], "sources": ["utopia-php-database:s1d79e9cf0e57", "utopia-php-database:s7bf0e65d6cf0", "utopia-php-database:s0ae9c48f1b01", "utopia-php-database:sb95aa1aa9ed9", "utopia-php-database:sc3379278f3f2", "utopia-php-database:s9e70fd6370ea", "utopia-php-database:s000a4b53503d", "utopia-php-database:sa8f4d7b8a48c", "utopia-php-database:sc00b8981307b"], "status": "REASONED"},
    "source-limits-sql-predicate": {"text": "At 10.1.0 the SQL permission hook matches requester roles and action in the collection's permissions side table with bound parameters and a shared-table tenant filter, returning 1 = 0 for no roles; Postgres overrides it with OR-ed JSONB containment tests on each row's permissions column, also 1 = 0 for no roles.", "components": ["utopia-php-database"], "sources": ["utopia-php-database:s7c5f032eabba", "utopia-php-database:s6a26dc1f9801", "utopia-php-database:sc9e144475031"], "status": "REASONED"},
    "source-limits-sql-disabled": {"text": "This guide reasons from the 10.1.0 SQL code that disabled authorization omits find permission filtering while query conditions, ordering and pagination remain, and that SQL getDocument without joins has no adapter authorization check to bypass; whether Database read checks are bypassed at 10.1.0 is not established.", "components": ["utopia-php-database"], "sources": ["utopia-php-database:s41c5bffe6075", "utopia-php-database:s7bf0e65d6cf0", "utopia-php-database:s4a3f8adc3023", "utopia-php-database:sc00b8981307b", "utopia-php-database:s2feb9534db52"], "status": "REASONED"},
    "source-limits-mongo": {"text": "At 10.1.0 Mongo getDocument filters by _uid through a tenant hook with no adapter authorization check; Mongo find passes its filters through a Mongo permission read hook whose code was not read, so its status gate and permission strings are not established at 10.1.0, with no live authorization demonstration.", "components": ["utopia-php-database"], "sources": ["utopia-php-database:sda6b15e8a7f2", "utopia-php-database:sf19fad9126ff", "utopia-php-database:s68e7d8672204", "utopia-php-database:s08b8af0098a5"], "status": "REASONED"},
    "source-limits-memory-redis": {"text": "At 10.1.0 Memory, intended for tests, fixtures and ephemeral workloads, and Redis, mirroring its surface, check no authorization in getDocument; their find paths keep only IDs matching requester roles for the action while authorization is enabled, without testing documentSecurity. This guide reasons that disabled status omits that filtering.", "components": ["utopia-php-database"], "sources": ["utopia-php-database:s1a92600403ce", "utopia-php-database:s604f86d30464", "utopia-php-database:s4aec3fdda679", "utopia-php-database:se488122e644f", "utopia-php-database:sab16fda30b23", "utopia-php-database:s91c17eccdca7", "utopia-php-database:s784f964c7ba3", "utopia-php-database:s2c28e6247d1d", "utopia-php-database:s1336d62998d1", "utopia-php-database:sd26ea42ec217", "utopia-php-database:sc00b8981307b"], "status": "REASONED"},
    "source-limits-pool": {"text": "At 10.1.0 Pool delegates getDocument and find to a pooled or pinned adapter, first setting its database, namespace, shared tables, tenant, tenant-per-document mode, authorization and locks from Pool's own; withTransaction does this before pinning. This guide reasons that a Pool-wrapped adapter reads with the authorization instance the database set.", "components": ["utopia-php-database"], "sources": ["utopia-php-database:s915a0850c1bf", "utopia-php-database:s8795cdff3377", "utopia-php-database:sa151e5aefbf8", "utopia-php-database:s7edf5f1161c1", "utopia-php-database:s9613234b8f17", "utopia-php-database:sde36e9303448", "utopia-php-database:sa8f4d7b8a48c"], "status": "REASONED"},
    "source-limits-appwrite-adapter": {"text": "Appwrite 2.7.0's _APP_DB_ADAPTER (since 1.9.0) defaults to postgresql; pool registration maps the mariadb, mongodb, mysql and postgresql schemes to the MariaDB, Mongo, MySQL and Postgres adapters, DocumentsDB accepts only mongodb, and the factory wraps pools in Pool, with tenant databases getting the shared authorization. Which adapter a given deployment uses is not established.", "components": ["appwrite", "utopia-php-database"], "sources": ["appwrite:s6bb4fe4aeed0", "appwrite:s298b295bc4a2", "appwrite:s90d9a92f0ed4", "appwrite:s495c0d1f4835", "appwrite:s7061d34674a8", "appwrite:s8ed5acf4fc13", "appwrite:s3e984f6f58a1", "appwrite:s39e9760a01ee", "utopia-php-database:safe798d5dd9c"], "status": "REASONED"},
    "source-limits-appwrite-dev": {"text": "Appwrite 2.7.0's development .env sets _APP_DB_ADAPTER=postgresql, a development default, not a production default; the root Compose file, which the install task reads as its Compose template, passes the variable to the appwrite service without a value. The 2.7.0 upgrade task keeps an installation's engine, assuming MariaDB when neither Compose nor .env sets _APP_DB_ADAPTER.", "components": ["appwrite"], "sources": ["appwrite:s2ce76c61491b", "appwrite:s80913a396c73", "appwrite:s320dd52ad7ad", "appwrite:s34cf9f92e6fb", "appwrite:se35f39b4f087", "appwrite:sa0f0758379af"], "status": "REASONED"},
    "source-limits-appwrite-console": {"text": "Appwrite 2.7.0's console variables endpoint reports _APP_DB_ADAPTER with a mariadb fallback while pool registration falls back to postgresql, so by source reading an unset variable, and by this guide's inference an empty one, gives Postgres pools and a reported mariadb. Both read a set variable; this guide advises not relying on the reported value to identify the adapter.", "components": ["appwrite"], "sources": ["appwrite:s43512ed49a8b", "appwrite:sc7cb880ebc53", "appwrite:s298b295bc4a2", "appwrite:s90d9a92f0ed4", "appwrite:s2f6df67b8aea", "appwrite:s1da118060657"], "status": "REASONED"},
    "source-limits-appwrite-install-env": {"text": "Appwrite 2.7.0's install task writes _APP_DB_ADAPTER to .env, unless reusing a configuration, from a prompt answer, its database (default postgresql, or detected) or the web installer's choice (default postgresql). Its Compose generator keeps only the chosen database service and, this guide reasons, the value-less entry, which the first detection step skips; how Compose resolves it is unknown.", "components": ["appwrite"], "sources": ["appwrite:sbdd71fb0bdee", "appwrite:s7c7d516c2e29", "appwrite:s354c70b426e9", "appwrite:s3f837fcdd474", "appwrite:sf0bdc23845a6", "appwrite:s8194e1cb510c", "appwrite:s7649c24d59ac", "appwrite:sade59f0be4d6", "appwrite:s8bd7139f8949", "appwrite:s48b953e7a273", "appwrite:s34cf9f92e6fb", "appwrite:s2ab6c91f62fd", "appwrite:s824989859386", "appwrite:s5fb71939c4b6", "appwrite:s254e58212ad0", "appwrite:s595b0f259c3a", "appwrite:s830783806300", "appwrite:s2851b656753a", "appwrite:s1141172bac7f", "appwrite:sc31ddc8f2659", "appwrite:se6ecc9107190", "appwrite:s2e99d3590696", "appwrite:s0ea4f620650f", "appwrite:sdfd43737a7ac", "appwrite:s3fc2bb20c0bb", "appwrite:s9cb7dec752e3", "appwrite:s7e549280b454", "appwrite:s3a92a2e12968", "appwrite:s79502c89f0ed", "appwrite:sa7170a7b4946"], "status": "REASONED"},
    "source-limits-adapter-docs": {"text": "As served on 2026-11-04, Appwrite's environment documentation lists MariaDB and MongoDB and gives _APP_DB_ADAPTER a mongodb default, conflicting with Appwrite 2.7.0, which defaults to postgresql, a value that page does not list.", "components": ["appwrite-docs", "appwrite"], "sources": ["appwrite-docs:s2bf9a4746d28", "appwrite:s6bb4fe4aeed0", "appwrite:s298b295bc4a2"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
