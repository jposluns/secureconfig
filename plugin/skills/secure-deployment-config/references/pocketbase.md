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

Written against PocketBase v0.40.4, Appwrite 2.2.0, utopia-php/database 7.3.9, and curl curl-8_14_1; 2 further sources carry no recorded version. Metadata reviewed 2026-10-19; documentation checked September 2026. The guide records 75 claims: 2 demonstrated by a check that ran and 73 reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

Like Firebase and Supabase ([firebase-supabase.md](firebase-supabase.md)), these backends hand a
public API endpoint to your client code; the collection or resource rules you write gate access
to your data. Files and privileged server credentials need separate attention. Both also ship
an admin console, so complete bootstrap privately before exposing the instance. Appwrite's first
console registrant becomes its initial operator; PocketBase's installer requires a privileged
token from the startup log, not merely an ordinary user's registration.

The source checks below target **PocketBase v0.40.4** and **Appwrite 2.2.0**, with documentation
checked in September 2026. Defaults refer to those releases unless stated otherwise. Live behavior
has not been demonstrated in this authoring environment. Some pin-specific source checks remain
incomplete; the source-work table below records those. Live comparisons are REASONED from the
cited vendor documentation and the pinned sources that were available.

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
In the pinned CLI wrapper, `Start()` registers the `serve` and `superuser` commands on the root
command, and the `--dev` flag default is the configured value. `New()` sets it to true exactly
when `os.Args[0]` starts with a nonempty `os.TempDir()` or `cacheDir()` prefix, and false otherwise.
In dev mode the pinned code logs executed SQL statements and lowers the logger
threshold so practically all logs print. Avoid unnecessary production diagnostics and protect
their output. See the
[development-mode behavior](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/base.go),
[command wiring](https://github.com/pocketbase/pocketbase/blob/v0.40.4/pocketbase.go#L165-L173),
[dev default selection](https://github.com/pocketbase/pocketbase/blob/v0.40.4/pocketbase.go#L73-L79),
[go run detection](https://github.com/pocketbase/pocketbase/blob/v0.40.4/tools/osutils/run.go#L10-L19),
[flag-to-app wiring](https://github.com/pocketbase/pocketbase/blob/v0.40.4/pocketbase.go#L129-L139),
[dev SQL logging](https://github.com/pocketbase/pocketbase/blob/v0.40.4/core/base.go#L1277-L1286), and
[dev logger level](https://github.com/pocketbase/pocketbase/blob/v0.40.4/core/base.go#L1489-L1499).

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
off. Configure a schedule and retention deliberately. Archives contain the main and logs
databases plus the rest of `pb_data`, excluding the backups directory and tracked exclusions.
The source says uploaded collection files on S3 are outside `pb_data` and need manual backup;
protect that storage separately. See [backup archive implementation](https://github.com/pocketbase/pocketbase/blob/v0.40.4/core/backup_create.go#L36-L60) and
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

Set collection and document `permissions` deliberately. In Appwrite 2.2.0,
`documentSecurity` defaults to `false`; enable it for document-level grants. Access granted at
**either collection or document level** is sufficient. A broad collection grant therefore
defeats an intended document restriction. See [legacy database permissions](https://appwrite.io/docs/products/databases/tablesdb/legacy/permissions).
The [collection create parameter](https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Create.php#L82-L84) states the requirement for one of the two permission levels.

For a document with null or omitted `permissions`, the Appwrite 2.2.0 create handler
calls `Permission::aggregate` first. The pinned helper returns null for null input, so
`permissions` remains null and reaches the handler's default branch. The handler assigns
read/update/delete user grants when the requester has a user ID and is not privileged;
otherwise it assigns an empty list. API-key requests skip subsequent role validation, but
the key check alone does not set that default list. Use specific user identities or team
roles, such as `Role.user(...)` or `Role.team(..., ...)`, rather than `Role.any()` for private
data. See [document create parameter](https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Create.php#L129-L134),
[requester classification](https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Create.php#L211-L212),
[null-permissions handling](https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Create.php#L237-L287),
[pinned dependency](https://github.com/appwrite/appwrite/blob/2.2.0/composer.lock#L3461-L3471),
[pinned aggregate helper](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Helpers/Permission.php#L151-L155), and
[permission roles](https://appwrite.io/docs/advanced/security/permissions).

For a 2.2.0 document GET, the pinned handler reads the requester class from the request's
authorization roles: the `keys` role marks an API-key request, and the `owner`, `developer`, or
`admin` role marks a privileged one. A disabled database or collection is reported as not found,
except to API-key or privileged requesters, and the document itself is then fetched through the
database layer. With an API key, the request's role and scopes come from the key; a standard or
ephemeral project key for the same project disables the database layer's default authorization
status, as do admin-mode console sessions outside the console project routes, while route scope
validation still applies to every requester. Collection `permissions` and `documentSecurity` are
handed to utopia-php/database when the collection is created. The dependency's read checks and
remaining adapter gap are described below; relating these checks to server-key permission bypass
is this guide's source-based reasoning alongside the cited documentation, not a live demonstration.
See the
[document read handler](https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Get.php#L80-L95),
[document fetch](https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Get.php#L103-L120),
[role classification](https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Utopia/Database/Documents/User.php#L75-L109),
[API-key role and authorization status](https://github.com/appwrite/appwrite/blob/2.2.0/app/controllers/shared/api.php#L144-L161),
[admin-mode authorization status](https://github.com/appwrite/appwrite/blob/2.2.0/app/controllers/shared/api.php#L312-L339),
[request role assignment](https://github.com/appwrite/appwrite/blob/2.2.0/app/controllers/shared/api.php#L357-L361),
[route scope validation](https://github.com/appwrite/appwrite/blob/2.2.0/app/controllers/shared/api.php#L503-L507),
[collection permission handoff](https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Create.php#L221-L227), and the
[pinned dependency](https://github.com/appwrite/appwrite/blob/2.2.0/composer.lock#L3461-L3471).

At the pinned utopia-php/database 7.3.9 commit, `getRead()` obtains read permissions from
`$permissions`; `getPermissionsByType()` selects entries starting with the requested action and
strips the action wrapper, quotes and spaces to yield distinct role strings. `Authorization`
stores added roles as keys. With its status enabled, it accepts a permission string matching any
role key and rejects an empty permission list or one with no match. See
[read accessors](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Document.php#L101-L112),
[role extraction](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Document.php#L153-L165), and
[role matching](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Validator/Authorization.php#L52-L90).

For non-metadata collections, `getDocument` checks collection read roles, adding document read roles
only when `documentSecurity` is true, both for a cached document and after an adapter fetch;
a failed check returns an empty document. This guide's reasoning is that the shown Database-level
checks are additive: a matching collection grant suffices for those checks, provided the adapter
returns the document on a fetch. Enabling document security adds grants to these checks rather
than restricting a collection grant. See the
[cached read check](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Database.php#L4943-L4993) and
[fetched read check](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Database.php#L5006-L5049).

`find` defaults to the read action and checks the collection's roles for that action. If that
check fails and `documentSecurity` is false, it throws an authorization exception, except for the
metadata collection. When a query reaches the adapter, a successful collection check runs
`adapter->find` inside the authorization instance's `skip`; otherwise it calls the adapter without that wrapper.
The database passes the same authorization instance to the adapter. See the
[find collection check](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Database.php#L8622-L8657),
[adapter dispatch](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Database.php#L8739-L8760), and
[authorization handoff](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Database.php#L1143-L1148).

`setDefaultStatus` changes both the current and reset-default status; `setStatus` changes only the
current status, `getStatus` returns it, and `reset` restores the default. `disable` sets status
false, `enable` sets it true, and `skip` disables it for a callback then restores the prior status
in `finally`. For a valid `Input`, disabled status makes `isValid` return true before checking an
empty permission list or matching roles; invalid input is still refused. This guide's reasoning
is that disabled status therefore bypasses the shown `getDocument` permission denials and makes
`find` take its skip branch when it reaches the adapter; collection existence and query-type checks
still run, as does query validation when enabled, in the shown `find` entry path. See
[status controls](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Validator/Authorization.php#L135-L211),
[role matching](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Validator/Authorization.php#L52-L90), and the
[find collection check](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Database.php#L8622-L8657).

These excerpts do not show what the adapter's `getDocument` and `find` do with the shared
authorization instance: any document-permission filtering (with or without a collection grant,
including the non-skip `find` branch when `documentSecurity` is enabled), and what disabled
authorization status bypasses there.
Those internals remain open in SELFHOSTED-BACKEND-SOURCE-1; this guide does not claim complete
pinned-source verification or a live authorization demonstration.

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

REASONED: this historical environment account is not a new host inventory; a live PocketBase or Appwrite stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. All three Verify shell blocks passed bash -n and ShellCheck 0.11.0 with exit 0 and no output. With curl and grep stubbed, written and embedded placeholders, example.com, angle brackets, empty values, and omitted or shortened set -- lines printed their refusal messages without invoking either stub. Live public-to-restricted record comparisons remain unobserved: guests can read public records, while restricted records deny or filter unauthorized reads and preserve permitted access, per the guide’s cited PocketBase API rules and filters (rolling documentation, checked September 2026) and Appwrite legacy collection/document permissions (rolling documentation, checked October 2026). The following sentences record the earlier authoring environment: The live checks below are **reasoned, not demonstrated**. This authoring environment has no
PocketBase executable or container runtime, no writable service installation, and no supplied
deployment, accounts, SMTP service, or second-host ingress fixture. Shell network access also
failed. No available authorized environment could reproduce the live exposed and fixed states.

REASONED: disposable-fixture comparison procedure; a live PocketBase or Appwrite stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. The GET block passed bash -n and ShellCheck 0.11.0 with exit 0 and no output; under bash -u, written and embedded placeholders, example.com, angle brackets, empty values, omitted or shortened set -- lines, HTTP, query, fragment, userinfo, and a control character printed refusal messages without invoking the curl stub. A valid fixture printed CURL_STUB arguments including --header @- and STDIN Authorization: DUMMY_TOKEN; the dummy header did not occur in those arguments. The local stub does not establish application authorization: public records admit guests, while fixed rules deny or filter unauthorized access and retain authorized access, per the guide’s cited PocketBase API rules and filters (rolling documentation, checked September 2026) and Appwrite legacy collection/document permissions (rolling documentation, checked October 2026). Use disposable data on a private fixture to establish exposed behavior, then repeat through
the deployed endpoints after hardening. Record response bodies, authorization identities, and
positive controls. A timeout, malformed request, nonexistent resource, or unrelated proxy error
does not establish application authorization.

REASONED: console-origin and API selection; a live PocketBase or Appwrite stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. The signup JSON parsed as four expected string fields. The registration block passed bash -n and ShellCheck 0.11.0 with exit 0 and no output; under bash -u, written and embedded placeholders, example.com, angle brackets, empty values, omitted or shortened set -- lines, HTTP, query, fragment, userinfo, and a control character printed refusal messages without invoking the curl stub. A valid fixture printed CURL_STUB arguments ending in https://console.internal/v1/account and STDIN containing the JSON; the password field did not occur in those arguments. Expected bootstrap access is private operator creation, not proof from static dashboard assets; Appwrite console account creation must fail after root-only bootstrap, per the guide’s cited PocketBase v0.40.4 installer and bootstrap-token lifetime and Appwrite 2.2.0 Compose console path, persistent volumes, and Docker socket mounts and Appwrite 2.2.0 console registration handler. The former `curl -I` checks are insufficient: HEAD cannot inspect signup controls, PocketBase
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

REASONED: substitution and protected-header handling for the GET procedure; live backend fixtures and controlled accounts remain unavailable; a live PocketBase or Appwrite stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. The GET block passed bash -n and ShellCheck 0.11.0 with exit 0 and no output; under bash -u, written and embedded placeholders, example.com, angle brackets, empty values, omitted or shortened set -- lines, HTTP, query, fragment, userinfo, and a control character printed refusal messages without invoking the curl stub. A valid fixture printed CURL_STUB arguments including --header @- and STDIN Authorization: DUMMY_TOKEN; the dummy header did not occur in those arguments. Expected public guest reads become denied or filtered after restrictive rules, with authorized-user positive controls, per the guide’s cited PocketBase API rules and filters (rolling documentation, checked September 2026) and Appwrite legacy collection/document permissions (rolling documentation, checked October 2026) and curl curl-8_14_1 headers from stdin (checked October 2026). Substitute inside the single quotes and paste whole blocks. Do not paste literal apostrophes
inside those quotes. The guards assume ordinary shell builtins. The headers reach curl from a
file on its stdin and this block never expands their contents, so they stay out of curl's
arguments, shell history and `set -x` tracing. The file's permissions and how it was prepared
remain exposures, as does the same account or root reading the file or viewing the process.
Never place a token-bearing URL in this block.

REASONED: following block; resource and scope comparisons follow the cited vendor documentation and available pins; live backend fixtures and controlled accounts were unavailable.

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
| Appwrite document permissions | **REASONED:** Request `/v1/databases/REPLACE_WITH_DATABASE/collections/REPLACE_WITH_COLLECTION/documents/REPLACE_WITH_DOCUMENT`. With document security explicitly enabled, first demonstrate that a broad collection read grant allows an otherwise ungranted user. Remove that broad grant: the intended document grantee must still receive the fixture, while guests and an unrelated user receive no document data. Compare omitted permissions for client-created and server-created fixtures. See [additive permissions](https://appwrite.io/docs/products/databases/tablesdb/legacy/permissions) and [creation defaults](https://appwrite.io/docs/advanced/security/permissions). |
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

REASONED: preceding block; signup JSON structure and the protected-stdin request procedure in this paragraph. No disposable Appwrite installation with a first console account and controlled signup fixture is available; a live Appwrite stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. The signup JSON parsed as four expected string fields. The registration block passed bash -n and ShellCheck 0.11.0 with exit 0 and no output; under bash -u, written and embedded placeholders, example.com, angle brackets, empty values, omitted or shortened set -- lines, HTTP, query, fragment, userinfo, and a control character printed refusal messages without invoking the curl stub. A valid fixture printed CURL_STUB arguments ending in https://console.internal/v1/account and STDIN containing the JSON; the password field did not occur in those arguments. Expected exposed registration returns 201; root-only registration after bootstrap rejects an additional account, per the guide’s cited Appwrite 2.2.0 console registration handler. The request can create an account on a misconfigured instance. Run it only on the disposable
fixture or an explicitly designated registration-test deployment. Use the API origin serving
the console project, not a guessed `/console` UI path. The block feeds the signup JSON, test
password included, to curl on stdin from the protected file: no password is typed into the command
or held in a shell variable, so neither shell history nor `set -x` tracing records it, provided the
file is prepared with an editor, not a shell command containing the password, which would enter
shell history. Stdin closes the argv channel only; the account owner and root can still read the
file and curl's memory.

REASONED: following block; console registration comparisons follow the pinned Appwrite handler; no disposable Appwrite installation or controlled signup fixture was available.

```bash
(
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

REASONED: preceding block; the full registration request, guards, protected stdin, root-only and allowlist comparisons, and operator controls in this paragraph. No disposable Appwrite installation, controlled signup identities, source-IP fixture, or operator/invitation fixture is available; a live Appwrite stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. The signup JSON parsed as four expected string fields. The registration block passed bash -n and ShellCheck 0.11.0 with exit 0 and no output; under bash -u, written and embedded placeholders, example.com, angle brackets, empty values, omitted or shortened set -- lines, HTTP, query, fragment, userinfo, and a control character printed refusal messages without invoking the curl stub. A valid fixture printed CURL_STUB arguments ending in https://console.internal/v1/account and STDIN containing the JSON; the password field did not occur in those arguments. The exposed/fixed outcomes that follow are expectations, per the guide’s cited Appwrite 2.2.0 console registration handler. With root-only registration disabled and allowlists empty on the private fixture, a valid new
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

REASONED: safe fixture and credential-transport procedure for the remaining-control comparisons; a live PocketBase or Appwrite stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Controlled service accounts, protected request files, and SDK fixtures for these live mutations are unavailable. The GET block passed bash -n and ShellCheck 0.11.0 with exit 0 and no output; under bash -u, written and embedded placeholders, example.com, angle brackets, empty values, omitted or shortened set -- lines, HTTP, query, fragment, userinfo, and a control character printed refusal messages without invoking the curl stub. A valid fixture printed CURL_STUB arguments including --header @- and STDIN Authorization: DUMMY_TOKEN; the dummy header did not occur in those arguments. Public record actions should admit guests; locked or restrictive rules should reject unauthorized mutations while intended users succeed, per the guide’s cited PocketBase v0.40.4 record CRUD handlers and curl curl-8_14_1 headers from stdin (checked October 2026). Each comparison below requires the unavailable live fixture. Perform mutations only on disposable
records and functions. Send credentials and request bodies through protected files or the SDK,
never command arguments.

| Control | Required comparison |
| --- | --- |
| Appwrite console MFA | **REASONED:** Requires an unavailable live Appwrite console fixture and controlled operator account with a TOTP authenticator. Using the operator's session and `X-Appwrite-Project: console`, request `GET /v1/account` without an API key. With MFA disabled, password authentication permits this request. Enable MFA and verify the TOTP factor, then create a fresh password-only session: the same request must return `user_more_factors_required`. Complete the TOTP challenge in that session and repeat the request: expect 200 with the operator's account data. See [console MFA](https://appwrite.io/docs/advanced/security/mfa) and [MFA enforcement](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/shared/api.php). |
| PocketBase writes and management | **REASONED:** Exercise `POST /api/collections/REPLACE_WITH_COLLECTION/records`, then `PATCH` and `DELETE` on disposable record URLs, using valid bodies. Public rules expose the actions; locked or restrictive rules must deny unauthorized changes while intended users still succeed. Separately attempt changing another auth record's email, password, and `verified` field: locked `manageRule` must not grant privileged management; an explicitly authorized manager must succeed only where intended. Confirm collection configuration rejects `manageRule=""`. See [CRUD handlers](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/record_crud.go) and [management validation](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/collection_model_auth_options.go). |
| PocketBase protected files | **REASONED:** GET a known fixture file at `/api/files/REPLACE_WITH_COLLECTION/REPLACE_WITH_RECORD/REPLACE_WITH_FILENAME`. Before protection, its unsigned URL downloads despite locked record access. Enable Protected and a `viewRule` that permits the intended ordinary user but denies guests and an unrelated ordinary user. File-token issuance does not check access to a particular file: authenticated users can obtain tokens. Confirm the unrelated user's `pb.files.getToken()` succeeds, then GET the protected fixture using that user's token-bearing SDK URL: expect 404. The permitted user's `pb.files.getToken()` must also succeed, and GET with that user's token-bearing SDK URL must return the expected fixture bytes as a positive control. Separately, an unsigned guest GET of the same protected file must return 404. Use the SDK for signed URLs, or feed a protected curl configuration through stdin; that keeps the token-bearing URL out of curl's argv only. Prepare the file with an editor, not a shell command that contains the URL, which would put it in shell history and `set -x` tracing, and the account owner and root can still read the file and curl's memory. See [download checks](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/file.go). |
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

REASONED: exact-match scan procedure; no deployed client bundle or credential inventory is available, so deployed absence remains unobserved. The scan block passed bash -n and ShellCheck 0.11.0 with exit 0 and no output. Its guards printed refusal messages for written and embedded placeholders, example.com, angle brackets, empty values, and omitted or shortened set -- lines without invoking the grep stub. Stub exits 0, 1, and 2 printed respectively FAIL: credential matches in the files listed above; No exact matches; also inspect build inputs and source maps.; and Scan failed; no conclusion. Separately, real grep -r -F -l -f on a disposable marker fixture exited 0 and printed only the matching client.js filename; after marker removal it exited 1 with no output. Expected exposed bundles contain privileged credentials and fixed bundles do not, per the guide’s cited PocketBase authentication (rolling documentation, checked September 2026) and Appwrite project API keys (rolling documentation, checked September 2026); exact-match fixtures do not establish detection of encoded or split credentials. Grep the client bundle for the strings used by your admin credentials or API keys; they should
not appear. Prepare a protected, nonempty patterns file containing one exact credential per
line, outside the bundle directory. The command prints matching filenames, not secret-bearing
lines. Establish a positive control using a disposable dummy credential in a test bundle, then
remove it and repeat. Exact matching does not detect every encoded or split representation.

REASONED: following block; privileged-credential scanning follows the cited authentication/API-key documentation; no deployed client bundle or credential inventory was supplied.

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

### Verification status and source work

All three bash blocks passed ShellCheck 0.11.0 and `bash -n` during authoring. Local guard tests
refused embedded `REPLACE_WITH_` placeholders, `example.com`, angle brackets, empty arguments,
and omitted or shortened `set --` lines. These checks establish shell behavior only. No live
service result or deployed-bundle scan is claimed.

| Check scope or source-work ID | Procedure and prerequisites | Status |
| --- | --- | --- |
| Service comparisons | Demonstrate every REASONED comparison above on PocketBase v0.40.4 and Appwrite 2.2.0, recording binary/image identity, commands, response bodies, denied and allowed identities, disposable-data cleanup, and effective settings. Requires writable service fixtures, a container runtime, controlled accounts and mailboxes, S3 and backup fixtures, ClamAV, function execution, a second-host ingress fixture, and the actual client build. Include all five PocketBase actions, manageRule, file-token issuance versus protected downloads (unrelated-user and unsigned-guest denial, permitted-user bytes), realtime, bootstrap-token handling, MFA, verification, retained-token behavior, additive Appwrite permissions, server-key scopes, registration, console MFA (fresh password-only denial and successful TOTP completion), TLS, proxy trust, limits, encrypted recovery, uploads, and executor privacy. | REASONED: full service-comparison inventory; a live PocketBase or Appwrite stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. This comparison still requires the writable service, container, account, mailbox, S3, backup, scanner, function, second-host ingress, and actual-build prerequisites named in this row. All three Verify shell blocks passed bash -n and ShellCheck 0.11.0 with exit 0 and no output. With curl and grep stubbed, written and embedded placeholders, example.com, angle brackets, empty values, and omitted or shortened set -- lines printed their refusal messages without invoking either stub. The signup JSON parsed as four expected string fields; valid curl stubs printed arguments and protected input separately. The grep stub exercised match, no-match, and error branches; real grep on a disposable marker printed only client.js with exit 0 and, after removal, no output with exit 1. None establishes the listed live outcomes. Exposed public authorization should admit unintended access and fixed authorization should deny or filter it while retaining permitted controls; the other expected outcomes remain those in the individual comparisons, per the guide’s cited PocketBase API rules and filters (rolling documentation, checked September 2026); Appwrite legacy collection/document permissions (rolling documentation, checked October 2026); Appwrite 2.2.0 console registration handler; PocketBase v0.40.4 auth defaults, manageRule validation, and MFA; PocketBase v0.40.4 file-token and download authorization; PocketBase v0.40.4 realtime authorization; PocketBase v0.40.4 authentication and superuser IP middleware; PocketBase v0.40.4 settings, encryption, proxy trust, SMTP, backups, and rate defaults; PocketBase v0.40.4 backup download authorization; PocketBase v0.40.4 rate limiter and exemptions; PocketBase v0.40.4 listener and origin flags; Appwrite 2.2.0 API-key authorization, scopes, MFA enforcement, and abuse exemptions; Appwrite 2.2.0 hostname routing and HTTPS enforcement; Appwrite email delivery (rolling documentation, checked September 2026); Appwrite self-hosted backups and encryption-key preservation (rolling documentation, checked September 2026); Appwrite 2.2.0 bucket defaults and upload controls; Appwrite 2.2.0 function execute roles, execution-key scopes, and enablement; Appwrite 2.2.0 Compose console path, persistent volumes, and Docker socket mounts; PocketBase authentication (rolling documentation, checked September 2026); Appwrite project API keys (rolling documentation, checked September 2026); PocketBase v0.40.4 installer and bootstrap-token lifetime; PocketBase v0.40.4 record CRUD handlers; PocketBase v0.40.4 record authorization and token validation; PocketBase v0.40.4 native TLS and ACME listener; Appwrite console MFA enrollment and recovery codes (rolling documentation, checked September 2026); Appwrite rate limits (rolling documentation, checked September 2026); and Appwrite permissions, creation defaults, and server integrations (rolling documentation, checked September 2026). REASONED from the cited vendor documentation and available pinned sources; live behavior is not demonstrated. |
| SELFHOSTED-BACKEND-SOURCE-1 | Complete pin-specific tracing for the Appwrite document read-authorization internals. The PocketBase CLI wrapper, the `--dev` flag default, the Appwrite requester privileged/API-key classification, and the Appwrite-repository document-read call sites are now cited above, alongside the earlier collection default, document-create permission branch, and backup archive pins. The pinned dependency now cites permission-role extraction and matching, collection/document read checks in `getDocument`, collection checks and adapter dispatch in `find`, and authorization status/skip behavior. Still untraced: what the adapter's `getDocument` and `find` do with the shared authorization instance, including any document-permission filtering (with or without a collection grant, and the non-skip `find` branch when `documentSecurity` is enabled), and what disabled authorization status bypasses there. | REASONED: pinned-source reading of PocketBase v0.40.4, Appwrite 2.2.0 and the utopia-php/database 7.3.9 excerpts above; the adapter internals stay open, complete pinned-source verification is not claimed, and live authorization is not demonstrated. |

## Sources (checked September 2026)

- PocketBase going to production (rolling documentation, checked September 2026): https://pocketbase.io/docs/going-to-production/
- PocketBase API rules and filters (rolling documentation, checked September 2026): https://pocketbase.io/docs/api-rules-and-filters/
- Appwrite self-hosting production security (rolling documentation, checked September 2026): https://appwrite.io/docs/advanced/self-hosting/production/security
- Appwrite project API keys (rolling documentation, checked September 2026): https://appwrite.io/docs/partners/project/api-keys
- [PocketBase authentication (rolling documentation, checked September 2026)](https://pocketbase.io/docs/authentication/).
- [PocketBase files and protected downloads (rolling documentation, checked September 2026)](https://pocketbase.io/docs/files-handling/).
- [PocketBase Realtime API (rolling documentation, checked September 2026)](https://pocketbase.io/docs/api-realtime/).
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
- [PocketBase v0.40.4 backup archive implementation](https://github.com/pocketbase/pocketbase/blob/v0.40.4/core/backup_create.go#L36-L60).
- [PocketBase v0.40.4 rate limiter and exemptions](https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/middlewares_rate_limit.go).
- [Appwrite 2.2.0 collection create parameters](https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Create.php#L82-L84).
- [Appwrite 2.2.0 document create parameters](https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Create.php#L129-L134).
- [Appwrite 2.2.0 requester classification](https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Create.php#L211-L212).
- [Appwrite 2.2.0 document create permission handling](https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Create.php#L237-L287).
- [Appwrite 2.2.0 composer.lock pinned database dependency](https://github.com/appwrite/appwrite/blob/2.2.0/composer.lock#L3461-L3471).
- [utopia-php/database 7.3.9 pinned aggregate helper](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Helpers/Permission.php#L151-L155).
- [utopia-php/database 7.3.9 stored permissions and read accessor](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Document.php#L101-L112).
- [utopia-php/database 7.3.9 permission role extraction](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Document.php#L153-L165).
- [utopia-php/database 7.3.9 authorization role matching](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Validator/Authorization.php#L52-L90).
- [utopia-php/database 7.3.9 cached document read authorization](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Database.php#L4943-L4993).
- [utopia-php/database 7.3.9 fetched document read authorization](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Database.php#L5006-L5049).
- [utopia-php/database 7.3.9 find collection authorization](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Database.php#L8622-L8657).
- [utopia-php/database 7.3.9 find adapter dispatch](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Database.php#L8739-L8760).
- [utopia-php/database 7.3.9 shared authorization instance](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Database.php#L1143-L1148).
- [utopia-php/database 7.3.9 authorization status and skip](https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Validator/Authorization.php#L135-L211).
- [Appwrite permissions, creation defaults, and server integrations (rolling documentation, checked September 2026)](https://appwrite.io/docs/advanced/security/permissions).
- [Appwrite legacy collection/document permissions (rolling documentation, checked October 2026)](https://appwrite.io/docs/products/databases/tablesdb/legacy/permissions).
- [Appwrite environment reference and HTTPS deprecation wording (rolling documentation, checked September 2026)](https://appwrite.io/docs/advanced/self-hosting/configuration/environment-variables).
- [Appwrite rate limits (rolling documentation, checked September 2026)](https://appwrite.io/docs/advanced/security/rate-limits).
- [Appwrite email delivery (rolling documentation, checked September 2026)](https://appwrite.io/docs/advanced/self-hosting/configuration/email).
- [Appwrite self-hosted backups and encryption-key preservation (rolling documentation, checked September 2026)](https://appwrite.io/docs/advanced/self-hosting/production/backups).
- [Appwrite 2.2.0 configuration defaults](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/config/variables.php).
- [Appwrite 2.2.0 development environment and placeholder secrets](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/.env).
- [Appwrite 2.2.0 console registration handler](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/api/account.php).
- [Appwrite console MFA enrollment and recovery codes (rolling documentation, checked September 2026)](https://appwrite.io/docs/advanced/security/mfa).
- [Appwrite 2.2.0 API-key authorization, scopes, MFA enforcement, and abuse exemptions](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/shared/api.php).
- [Appwrite 2.2.0 hostname routing and HTTPS enforcement](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/general.php).
- [Appwrite 2.2.0 bucket defaults and upload controls](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/src/Appwrite/Platform/Modules/Storage/Http/Buckets/Create.php).
- [Appwrite 2.2.0 function execute roles, execution-key scopes, and enablement](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/src/Appwrite/Platform/Modules/Functions/Http/Functions/Create.php).
- [Appwrite 2.2.0 storage thresholds and release constant](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/init/constants.php).
- [Appwrite 2.2.0 Compose console path, persistent volumes, and Docker socket mounts](https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/docker-compose.yml).
- [PocketBase v0.40.4 CLI wrapper and development flag wiring (checked October 2026)](https://github.com/pocketbase/pocketbase/blob/v0.40.4/pocketbase.go#L234-L239).
- [PocketBase v0.40.4 dev default selection (checked October 2026)](https://github.com/pocketbase/pocketbase/blob/v0.40.4/pocketbase.go#L73-L79).
- [PocketBase v0.40.4 flag-to-app dev wiring (checked October 2026)](https://github.com/pocketbase/pocketbase/blob/v0.40.4/pocketbase.go#L129-L139).
- [PocketBase v0.40.4 root command wiring for serve and superuser (checked October 2026)](https://github.com/pocketbase/pocketbase/blob/v0.40.4/pocketbase.go#L165-L173).
- [PocketBase v0.40.4 go run detection (checked October 2026)](https://github.com/pocketbase/pocketbase/blob/v0.40.4/tools/osutils/run.go#L10-L19).
- [PocketBase v0.40.4 dev SQL logging (checked October 2026)](https://github.com/pocketbase/pocketbase/blob/v0.40.4/core/base.go#L1277-L1286).
- [PocketBase v0.40.4 dev logger level (checked October 2026)](https://github.com/pocketbase/pocketbase/blob/v0.40.4/core/base.go#L1489-L1499).
- [Appwrite 2.2.0 document read handler and requester checks (checked October 2026)](https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Get.php#L80-L95).
- [Appwrite 2.2.0 document fetch through the database layer (checked October 2026)](https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Get.php#L103-L120).
- [Appwrite 2.2.0 privileged and key role classification (checked October 2026)](https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Utopia/Database/Documents/User.php#L75-L109).
- [Appwrite 2.2.0 API-key role, scopes, and authorization status (checked October 2026)](https://github.com/appwrite/appwrite/blob/2.2.0/app/controllers/shared/api.php#L144-L161).
- [Appwrite 2.2.0 admin-mode roles and authorization status (checked October 2026)](https://github.com/appwrite/appwrite/blob/2.2.0/app/controllers/shared/api.php#L312-L339).
- [Appwrite 2.2.0 request role assignment (checked October 2026)](https://github.com/appwrite/appwrite/blob/2.2.0/app/controllers/shared/api.php#L357-L361).
- [Appwrite 2.2.0 route scope validation (checked October 2026)](https://github.com/appwrite/appwrite/blob/2.2.0/app/controllers/shared/api.php#L503-L507).
- [Appwrite 2.2.0 collection permission and documentSecurity handoff (checked October 2026)](https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Create.php#L221-L227).
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

- pb: PocketBase (v0.40.4)
- appwrite: Appwrite (2.2.0)
- pb-docs: PocketBase documentation (rolling) (unknown)
- appwrite-docs: Appwrite documentation (rolling) (unknown)
- utopia-php-database: utopia-php/database (7.3.9)
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
- pb-limiter (REASONED; pb, pb-docs): Native limits exist from v0.23.0 but default disabled at v0.40.4; enable rateLimits.enabled.
- pb-limit-rules (REASONED; pb): Seeded limits are *:auth 2/3s, *:create 20/5s, /api/batch 3/1s and /api/ 300/10s.
- pb-limit-bypass (REASONED; pb): Superusers and rateLimits.excludedIPs bypass limits; test ordinary non-excluded clients.
- pb-smtp (REASONED; pb): smtp.enabled and smtp.tls default false; disabled SMTP falls back to sendmail. Configure protected transport and test actual delivery.
- appwrite-https (REASONED; appwrite, appwrite-docs): API FORCE_HTTPS and function/site ROUTER_FORCE_HTTPS default disabled at 2.2.0; explicitly enable both despite conflicting rolling deprecation/default documentation.
- appwrite-hosts (REASONED; appwrite): ROUTER_PROTECTION defaults disabled; configure actual domains and enable rejection of unknown hostnames.
- appwrite-registration (REASONED; appwrite): Console root-only registration defaults enabled with empty email/IP allowlists; these restrict account creation, not dashboard reachability or login.
- appwrite-console (REASONED; appwrite, appwrite-docs): Claim the first operator privately and use a separate network/access boundary for a private dashboard.
- appwrite-mfa (REASONED; appwrite, appwrite-docs): Enroll and verify operator TOTP, protect recovery codes; at 2.2.0 enabled MFA with a verified factor requires a second session factor.
- appwrite-dev-env (REASONED; appwrite): Development env disables root-only registration, abuse and router protection and carries placeholders; do not inherit it for production.
- appwrite-recreate (REASONED; appwrite-docs): Apply env/Compose changes with docker compose up -d from the install directory, then check effective behavior.
- appwrite-permissions (REASONED; appwrite, appwrite-docs): Collection and document grants are additive according to legacy documentation; documentSecurity defaults false in Appwrite 2.2.0 and must be enabled for document grants. The pinned parameter description states the need for one permission level.
- appwrite-creation (REASONED; appwrite, appwrite-docs, utopia-php-database): For null or omitted document permissions, the pinned aggregate helper preserves null before the handler assigns read/update/delete user grants to a nonprivileged requester with a user ID, or an empty list otherwise. API-key classification skips role validation but does not itself determine the default list. Use specific users/teams for private data.
- appwrite-read-path (REASONED; appwrite): Document GET classifies the requester from authorization roles (keys; owner/developer/admin privileged), reports disabled databases/collections as not found except to those requesters, and fetches the document through the database layer; collection permissions and documentSecurity are passed to the database layer at collection creation.
- appwrite-requester (REASONED; appwrite): With an API key the request role and scopes come from the key; a standard or ephemeral project key for the same project disables the default authorization status, as do admin-mode console sessions outside console project routes, while route scope validation applies to every requester.
- appwrite-keys (REASONED; appwrite, appwrite-docs): Properly scoped server API keys bypass resource permissions but still obey operation scopes; keys.write is admin-equivalent and keys never belong in clients.
- appwrite-encryption (REASONED; appwrite, appwrite-docs): Replace _APP_OPENSSL_KEY_V1=your-secret-key before production data; preserve the exact key separately, since replacement/loss strands encrypted secrets.
- appwrite-backups (REASONED; appwrite-docs): Back up database, persistent storage and deployment configuration; restrict access and test restoration in a separate installation.
- appwrite-abuse (REASONED; appwrite, appwrite-docs): _APP_OPTIONS_ABUSE defaults enabled but dev env disables it; server API-key requests are exempt, so test with ordinary clients.
- appwrite-smtp (REASONED; appwrite, appwrite-docs): SMTP host/port/secure/username/password default empty and empty host disables sending; configure the provider and confirm message receipt/use.
- appwrite-storage (REASONED; appwrite): Storage defaults local, upload limit 30000000 and server antivirus disabled; enabling scanning requires configured reachable ClamAV.
- appwrite-bucket (REASONED; appwrite): New bucket permissions are empty and fileSecurity=false; enable per-file security deliberately, since bucket grants also permit access.
- appwrite-bucket-options (REASONED; appwrite): Bucket encryption and antivirus default true; bucket antivirus does not enable the server scanner.
- appwrite-size (REASONED; appwrite): Encryption/scanning skip files above 20000000 bytes; cap maximumFileSize at that threshold when either is mandatory and test the boundary.
- appwrite-functions (REASONED; appwrite): Function execute roles and execution-key scopes default empty; grant narrowly. Disabled functions still admit authorized Server SDK API keys.
- appwrite-executor (REASONED; appwrite, appwrite-docs): Keep executor/orchestrator private, protect Docker-socket authority and replace _APP_EXECUTOR_SECRET; container execution is not demonstrated hostile-tenant isolation.
- verify-pb-records (REASONED; pb-docs, curl): Public rules allow guest reads; locked rules deny with 403, unsatisfied list filters can return empty 200 and view rules 404. Retain owner and separate superuser controls.
- verify-appwrite-records (REASONED; appwrite-docs): Broad collection grants defeat document restrictions; removing them must deny unrelated users while document grantees succeed. Compare client/server creation defaults.
- verify-appwrite-keys (REASONED; appwrite): A correctly scoped server key reads despite empty permissions, while a key without scope fails; neither substitutes for an ordinary-user control.
- verify-registration (REASONED; appwrite): On disposable Appwrite fixtures compare open signup 201 with root-only account-limit failure and independent email/IP restrictions; retain login/invitation controls.
- verify-pb-bootstrap (REASONED; pb): Guest and ordinary-user _superusers record creation must fail while a valid installer token creates the private operator; static dashboard assets prove no admin access.
- verify-appwrite-mfa (REASONED; appwrite, appwrite-docs): Console account GET succeeds without MFA, fails with user_more_factors_required for a fresh password-only MFA session, and succeeds after TOTP completion.
- verify-pb-writes (REASONED; pb): Compare intended/unauthorized POST/PATCH/DELETE and privileged auth-record management; locked manageRule grants no management and empty-string configuration must fail.
- verify-pb-files (REASONED; pb, curl): Before protection unsigned file GET works; Protected plus private viewRule rejects guests/unrelated-user file tokens with 404 while permitted-user bytes still arrive.
- verify-pb-realtime (REASONED; pb, pb-docs): Mutate a fixture while comparing collection and record subscriptions; deny unauthorized event delivery, retaining authorized delivery. PB_CONNECT/acknowledgment alone is insufficient.
- verify-pb-mfa (REASONED; pb-docs): Compare password-only completion with password-plus-OTP MFA and verified/unverified authRule logins; clearing authStore must not revoke a retained valid token.
- verify-pb-ips (REASONED; pb): Compare allowed/excluded superuser sources and forged forwarded headers; excluded sources must get 403 and direct backend access must fail with a working proxy control.
- verify-transport (REASONED; pb, appwrite): Compare HTTP/HTTPS and certificates, Appwrite API/function/site domains and configured/unknown Host; compare browser origins separately from record authorization.
- verify-abuse (REASONED; pb, appwrite-docs): Cross each configured threshold with ordinary non-excluded clients and compare disabled/enabled controls; PocketBase limiting yields 429 with later successful recovery.
- verify-email (REASONED; pb, appwrite-docs): Request OTP, verification and recovery messages and confirm receipt and use; request success alone is not delivery evidence.
- verify-pb-recovery (REASONED; pb, pb-docs): Compare plaintext/encrypted persisted settings, restart with retained key and restore local/S3 data; only permitted superuser file tokens may download backups.
- verify-appwrite-recovery (REASONED; appwrite-docs): Restore encrypted fixtures with the original key; a separate wrong-key fixture must not recover encrypted values.
- verify-uploads (REASONED; appwrite): Compare permitted/unrelated uploads and size-boundary fixtures; mandatory processing requires rejecting over-limit files and confirming accepted-file encryption/scanning.
- verify-functions (REASONED; appwrite): Compare intended execute roles, unrelated users and privileged server keys, including disabled functions; confirm executor/orchestrator privacy from a second host.
- verify-bundle (REASONED; pb-docs, appwrite-docs): Search filenames using protected exact-secret patterns with a disposable marker control; client bundles must contain neither superuser tokens nor Appwrite API keys, and encoded/split forms can evade scanning.
- local-guards (DEMONSTRATED; pb-docs, appwrite-docs): Recorded guard tests rejected placeholders and omitted/shortened arguments; this demonstrates shell behavior only, not service access or deployed-bundle scanning.
- local-syntax (DEMONSTRATED; appwrite, pb-docs, appwrite-docs): All three bash fences have recorded local lint/syntax success, not live service evidence; ShellCheck version is recorded only in the body.
- source-limits (REASONED; appwrite-docs, pb-docs, appwrite, utopia-php-database): PocketBase CLI/--dev and Appwrite requester/call-site pins remain cited; utopia-php/database role matching, Database reads/dispatch and status/skip are cited. Adapter getDocument/find use of shared authorization, any document filtering with/without collection grants (including non-skip find with documentSecurity enabled), and disabled-status bypass remain untraced; live authorization is not demonstrated.

````json
{
  "schema": 1,
  "checked": "2026-10-19",
  "documentation_checked": "2026-09",
  "body_sha256": "fd9e0affef1fd7df9fb791f3226c4b9347ac2799eb585795afe7158cf43bbdc3",
  "components": {
    "pb": {
      "name": "PocketBase",
      "basis": "v0.40.4",
      "sources": {
        "saf684a26056b": "https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/installer.go",
        "s4b155ef30262": "https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/cmd/serve.go",
        "sb2129128b86c": "https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/serve.go",
        "s5b66ca69bf6d": "https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/middlewares.go",
        "s04ae861b5709": "https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/record_query.go",
        "s69aa223f52e4": "https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/record_crud.go",
        "sce114368c2ad": "https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/collection_model_auth_options.go",
        "s03dd7dd84c2a": "https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/settings_model.go",
        "seb56d3763223": "https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/core/base.go",
        "sa5e571f8d473": "https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/file.go",
        "sfd2f779e8e11": "https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/realtime.go",
        "s31a5adccd695": "https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/backup.go",
        "se74188862a55": "https://github.com/pocketbase/pocketbase/blob/v0.40.4/core/backup_create.go#L36-L60",
        "sf6ffdca4dd39": "https://raw.githubusercontent.com/pocketbase/pocketbase/v0.40.4/apis/middlewares_rate_limit.go",
        "s1b04c2cd16ec": "https://github.com/pocketbase/pocketbase/blob/v0.40.4/pocketbase.go#L234-L239",
        "sb63f49346abe": "https://github.com/pocketbase/pocketbase/blob/v0.40.4/pocketbase.go#L73-L79",
        "sd700e81880f2": "https://github.com/pocketbase/pocketbase/blob/v0.40.4/pocketbase.go#L129-L139",
        "s54430c83a38a": "https://github.com/pocketbase/pocketbase/blob/v0.40.4/pocketbase.go#L165-L173",
        "s2c8f78f2d5ac": "https://github.com/pocketbase/pocketbase/blob/v0.40.4/tools/osutils/run.go#L10-L19",
        "s5b0dd2fd7a6a": "https://github.com/pocketbase/pocketbase/blob/v0.40.4/core/base.go#L1277-L1286",
        "sf7c2fb5e78e7": "https://github.com/pocketbase/pocketbase/blob/v0.40.4/core/base.go#L1489-L1499"
      }
    },
    "appwrite": {
      "name": "Appwrite",
      "basis": "2.2.0",
      "sources": {
        "s9f5bd3b70f14": "https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/config/variables.php",
        "sadb8c6e7b00a": "https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/.env",
        "s2bb21218c5ee": "https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/api/account.php",
        "s193bfa5c6e22": "https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/shared/api.php",
        "s427bab3733b6": "https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/controllers/general.php",
        "se9480e5807b3": "https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/src/Appwrite/Platform/Modules/Storage/Http/Buckets/Create.php",
        "sf916851a0b10": "https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Create.php#L82-L84",
        "s5b4b3eb2271f": "https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Create.php#L129-L134",
        "s93647e16b966": "https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Create.php#L211-L212",
        "sda698c40fc34": "https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Create.php#L237-L287",
        "s655a0abb9ef0": "https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/src/Appwrite/Platform/Modules/Functions/Http/Functions/Create.php",
        "s4ab95ecbf6b5": "https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/app/init/constants.php",
        "s8e5272615f2e": "https://raw.githubusercontent.com/appwrite/appwrite/2.2.0/docker-compose.yml",
        "s7ba6f9c71972": "https://github.com/appwrite/appwrite/blob/2.2.0/composer.lock#L3461-L3471",
        "s5396e119c026": "https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Get.php#L80-L95",
        "s82988de645fa": "https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Get.php#L103-L120",
        "s224cc9d8a387": "https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Utopia/Database/Documents/User.php#L75-L109",
        "sc55465cf878d": "https://github.com/appwrite/appwrite/blob/2.2.0/app/controllers/shared/api.php#L144-L161",
        "sed1bf9453ecb": "https://github.com/appwrite/appwrite/blob/2.2.0/app/controllers/shared/api.php#L312-L339",
        "s8784d02c82c9": "https://github.com/appwrite/appwrite/blob/2.2.0/app/controllers/shared/api.php#L357-L361",
        "sf60a2b283b80": "https://github.com/appwrite/appwrite/blob/2.2.0/app/controllers/shared/api.php#L503-L507",
        "s1fe0e6185518": "https://github.com/appwrite/appwrite/blob/2.2.0/src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Create.php#L221-L227"
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
      "basis": "7.3.9",
      "sources": {
        "s847e0ded0300": "https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Helpers/Permission.php#L151-L155",
        "s44e735a78b9d": "https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Document.php#L101-L112",
        "sfda128d99ef9": "https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Document.php#L153-L165",
        "s610f3fb8fa73": "https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Validator/Authorization.php#L52-L90",
        "s4f7f3ed32a53": "https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Database.php#L4943-L4993",
        "sa3038716384d": "https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Database.php#L5006-L5049",
        "scf82badc07e5": "https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Database.php#L8622-L8657",
        "s7cf5a05cf798": "https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Database.php#L8739-L8760",
        "s3389fa5854d5": "https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Database.php#L1143-L1148",
        "s01a8ce8001e0": "https://github.com/utopia-php/database/blob/54364c687d6ddb3d976d7130b9001c0b29276933/src/Database/Validator/Authorization.php#L135-L211"
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
    "pb-bootstrap": {"text": "Privately bootstrap through the logged installer URL; superuser create EMAIL PASS exposes passwords in argv. Ordinary registration does not grant superuser rights.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:s9029ab974cf1", "pb:saf684a26056b"], "status": "REASONED"},
    "pb-installer": {"text": "Installer system-superuser token lasts about 30 minutes; protect its URL and startup logs as credentials.", "components": ["pb"], "sources": ["pb:saf684a26056b"], "status": "REASONED"},
    "pb-ips": {"text": "Superuser IP allowlists are available from v0.38.0; superuserIPs defaults empty and restricts authenticated requests, not /_/ static assets.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:s9029ab974cf1", "pb:s5b66ca69bf6d"], "status": "REASONED"},
    "pb-tls": {"text": "serve with a domain provides native HTTPS/ACME; alternatively terminate TLS at a reverse proxy.", "components": ["pb"], "sources": ["pb:sb2129128b86c"], "status": "REASONED"},
    "pb-bind": {"text": "Without a domain serve defaults to 127.0.0.1:8090; with a domain it uses 0.0.0.0:80/443. Behind a local proxy omit the domain and set --http loopback.", "components": ["pb"], "sources": ["pb:s4b155ef30262"], "status": "REASONED"},
    "pb-origins": {"text": "--origins defaults * and accepts comma-separated allowed origins; CORS does not authorize records.", "components": ["pb"], "sources": ["pb:s4b155ef30262"], "status": "REASONED"},
    "pb-proxy": {"text": "Trust only headers the proxy overwrites, review useLeftmostIP ordering and block direct backend access to protect IP/rate controls.", "components": ["pb"], "sources": ["pb:s03dd7dd84c2a"], "status": "REASONED"},
    "pb-dev": {"text": "--dev adds diagnostics including SQL on stderr, not an auth bypass; its configured default comes from New(): true if os.Args[0] starts with a nonempty os.TempDir() or cacheDir() prefix, false otherwise.", "components": ["pb"], "sources": ["pb:seb56d3763223", "pb:s1b04c2cd16ec", "pb:sb63f49346abe", "pb:s2c8f78f2d5ac", "pb:sd700e81880f2", "pb:s5b0dd2fd7a6a", "pb:sf7c2fb5e78e7"], "status": "REASONED"},
    "pb-cli": {"text": "In the pinned CLI wrapper, Start() registers the serve and superuser commands on the root command and executes it.", "components": ["pb"], "sources": ["pb:s54430c83a38a"], "status": "REASONED"},
    "pb-rules": {"text": "Each list/view/create/update/delete rule defaults null (superuser-only); empty opens to guests and nonempty filters. Superusers bypass rules.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:saedbdfbdfc48", "pb:s04ae861b5709"], "status": "REASONED"},
    "pb-manage": {"text": "Top-level manageRule defaults null and permits privileged auth-record changes alongside create/update rules; its validator rejects empty-string rules.", "components": ["pb"], "sources": ["pb:sce114368c2ad"], "status": "REASONED"},
    "pb-files": {"text": "File fields default unprotected despite locked record rules; Protected plus an authorized viewRule gates downloads, while a public viewRule still permits public access.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:sf711b6345643", "pb:sa5e571f8d473"], "status": "REASONED"},
    "pb-file-token": {"text": "Short-lived file tokens provide identity context, not file authorization; viewRule decides. Protect token-bearing file URLs.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:sf711b6345643", "pb:sa5e571f8d473"], "status": "REASONED"},
    "pb-realtime": {"text": "Collection subscriptions use listRule and individual-record subscriptions viewRule; SSE/subscription success does not prove event authorization.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:sb850a71fad4d", "pb:sfd2f779e8e11"], "status": "REASONED"},
    "pb-password": {"text": "Auth initialization enables password authentication with email as the identity field.", "components": ["pb"], "sources": ["pb:sce114368c2ad"], "status": "REASONED"},
    "pb-oauth": {"text": "OAuth2 defaults disabled and is unsupported for _superusers.", "components": ["pb", "pb-docs"], "sources": ["pb:sce114368c2ad", "pb-docs:s773e441dd51c"], "status": "REASONED"},
    "pb-mfa-default": {"text": "MFA defaults disabled with duration 600 seconds.", "components": ["pb"], "sources": ["pb:sce114368c2ad"], "status": "REASONED"},
    "pb-otp-default": {"text": "OTP defaults disabled with duration 180 seconds and length 8.", "components": ["pb"], "sources": ["pb:sce114368c2ad"], "status": "REASONED"},
    "pb-alerts": {"text": "Authentication alerts default enabled; retain alerts and provide working email.", "components": ["pb"], "sources": ["pb:sce114368c2ad"], "status": "REASONED"},
    "pb-auth-token": {"text": "Auth token duration defaults to 432000 seconds.", "components": ["pb"], "sources": ["pb:sce114368c2ad"], "status": "REASONED"},
    "pb-file-duration": {"text": "File token duration defaults to 180 seconds.", "components": ["pb"], "sources": ["pb:sce114368c2ad"], "status": "REASONED"},
    "pb-auth-rule": {"text": "authRule defaults empty; verified-only collections can require verified = true after email verification works.", "components": ["pb", "pb-docs"], "sources": ["pb:sce114368c2ad", "pb-docs:s773e441dd51c"], "status": "REASONED"},
    "pb-mfa": {"text": "For superusers retain password auth and enable both OTP and MFA; empty mfa.rule applies to everyone. OTP alone is not a second factor.", "components": ["pb", "pb-docs"], "sources": ["pb:sce114368c2ad", "pb-docs:s773e441dd51c"], "status": "REASONED"},
    "pb-logout": {"text": "Stateless authentication means clearing pb.authStore removes only the local copy, not a stolen token.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:s773e441dd51c", "pb:s04ae861b5709"], "status": "REASONED"},
    "pb-encryption": {"text": "Settings default to plaintext JSON; select a 32-character environment secret with --encryptionEnv. This encrypts settings, not the whole database or files.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:s9029ab974cf1", "pb:s03dd7dd84c2a"], "status": "REASONED"},
    "pb-backups": {"text": "Backups default local with empty cron (automatic backups off); archives contain main and logs databases plus remaining pb_data, excluding the backups directory and tracked exclusions; uploaded collection files on S3 require manual backup. Schedule/retain deliberately and protect archives.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:s9029ab974cf1", "pb:s03dd7dd84c2a", "pb:se74188862a55"], "status": "REASONED"},
    "pb-backup-auth": {"text": "Backup downloads require a superuser file token and obey superuser IP restrictions; ordinary auth/file tokens do not suffice.", "components": ["pb"], "sources": ["pb:s31a5adccd695"], "status": "REASONED"},
    "pb-limiter": {"text": "Native limits exist from v0.23.0 but default disabled at v0.40.4; enable rateLimits.enabled.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:s9029ab974cf1", "pb:s03dd7dd84c2a"], "status": "REASONED"},
    "pb-limit-rules": {"text": "Seeded limits are *:auth 2/3s, *:create 20/5s, /api/batch 3/1s and /api/ 300/10s.", "components": ["pb"], "sources": ["pb:s03dd7dd84c2a"], "status": "REASONED"},
    "pb-limit-bypass": {"text": "Superusers and rateLimits.excludedIPs bypass limits; test ordinary non-excluded clients.", "components": ["pb"], "sources": ["pb:sf6ffdca4dd39"], "status": "REASONED"},
    "pb-smtp": {"text": "smtp.enabled and smtp.tls default false; disabled SMTP falls back to sendmail. Configure protected transport and test actual delivery.", "components": ["pb"], "sources": ["pb:s03dd7dd84c2a", "pb:seb56d3763223"], "status": "REASONED"},
    "appwrite-https": {"text": "API FORCE_HTTPS and function/site ROUTER_FORCE_HTTPS default disabled at 2.2.0; explicitly enable both despite conflicting rolling deprecation/default documentation.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite:s9f5bd3b70f14", "appwrite:s427bab3733b6", "appwrite-docs:s2bf9a4746d28"], "status": "REASONED"},
    "appwrite-hosts": {"text": "ROUTER_PROTECTION defaults disabled; configure actual domains and enable rejection of unknown hostnames.", "components": ["appwrite"], "sources": ["appwrite:s9f5bd3b70f14", "appwrite:s427bab3733b6"], "status": "REASONED"},
    "appwrite-registration": {"text": "Console root-only registration defaults enabled with empty email/IP allowlists; these restrict account creation, not dashboard reachability or login.", "components": ["appwrite"], "sources": ["appwrite:s9f5bd3b70f14", "appwrite:s2bb21218c5ee"], "status": "REASONED"},
    "appwrite-console": {"text": "Claim the first operator privately and use a separate network/access boundary for a private dashboard.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite-docs:s4a965bdeeb98", "appwrite:s2bb21218c5ee"], "status": "REASONED"},
    "appwrite-mfa": {"text": "Enroll and verify operator TOTP, protect recovery codes; at 2.2.0 enabled MFA with a verified factor requires a second session factor.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite-docs:s221c6aaef8df", "appwrite:s193bfa5c6e22"], "status": "REASONED"},
    "appwrite-dev-env": {"text": "Development env disables root-only registration, abuse and router protection and carries placeholders; do not inherit it for production.", "components": ["appwrite"], "sources": ["appwrite:sadb8c6e7b00a"], "status": "REASONED"},
    "appwrite-recreate": {"text": "Apply env/Compose changes with docker compose up -d from the install directory, then check effective behavior.", "components": ["appwrite-docs"], "sources": ["appwrite-docs:s4a965bdeeb98"], "status": "REASONED"},
    "appwrite-permissions": {"text": "Collection and document grants are additive according to legacy documentation; documentSecurity defaults false in Appwrite 2.2.0 and must be enabled for document grants. The pinned parameter description states the need for one permission level.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite:sf916851a0b10", "appwrite-docs:s58ad28816c5d"], "status": "REASONED"},
    "appwrite-creation": {"text": "For null or omitted document permissions, the pinned aggregate helper preserves null before the handler assigns read/update/delete user grants to a nonprivileged requester with a user ID, or an empty list otherwise. API-key classification skips role validation but does not itself determine the default list. Use specific users/teams for private data.", "components": ["appwrite", "appwrite-docs", "utopia-php-database"], "sources": ["appwrite:s5b4b3eb2271f", "appwrite:s93647e16b966", "appwrite:sda698c40fc34", "appwrite-docs:sa0bd132f7968", "appwrite:s7ba6f9c71972", "utopia-php-database:s847e0ded0300"], "status": "REASONED"},
    "appwrite-read-path": {"text": "Document GET classifies the requester from authorization roles (keys; owner/developer/admin privileged), reports disabled databases/collections as not found except to those requesters, and fetches the document through the database layer; collection permissions and documentSecurity are passed to the database layer at collection creation.", "components": ["appwrite"], "sources": ["appwrite:s5396e119c026", "appwrite:s82988de645fa", "appwrite:s224cc9d8a387", "appwrite:s1fe0e6185518"], "status": "REASONED"},
    "appwrite-requester": {"text": "With an API key the request role and scopes come from the key; a standard or ephemeral project key for the same project disables the default authorization status, as do admin-mode console sessions outside console project routes, while route scope validation applies to every requester.", "components": ["appwrite"], "sources": ["appwrite:sc55465cf878d", "appwrite:sed1bf9453ecb", "appwrite:s8784d02c82c9", "appwrite:sf60a2b283b80"], "status": "REASONED"},
    "appwrite-keys": {"text": "Properly scoped server API keys bypass resource permissions but still obey operation scopes; keys.write is admin-equivalent and keys never belong in clients.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite:s193bfa5c6e22", "appwrite-docs:saa37bb5d4d7e"], "status": "REASONED"},
    "appwrite-encryption": {"text": "Replace _APP_OPENSSL_KEY_V1=your-secret-key before production data; preserve the exact key separately, since replacement/loss strands encrypted secrets.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite:s9f5bd3b70f14", "appwrite-docs:s256ef73f7b85"], "status": "REASONED"},
    "appwrite-backups": {"text": "Back up database, persistent storage and deployment configuration; restrict access and test restoration in a separate installation.", "components": ["appwrite-docs"], "sources": ["appwrite-docs:s256ef73f7b85"], "status": "REASONED"},
    "appwrite-abuse": {"text": "_APP_OPTIONS_ABUSE defaults enabled but dev env disables it; server API-key requests are exempt, so test with ordinary clients.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite:s9f5bd3b70f14", "appwrite:sadb8c6e7b00a", "appwrite:s193bfa5c6e22", "appwrite-docs:s000d05106450"], "status": "REASONED"},
    "appwrite-smtp": {"text": "SMTP host/port/secure/username/password default empty and empty host disables sending; configure the provider and confirm message receipt/use.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite:s9f5bd3b70f14", "appwrite-docs:s38a1efa0c7d2"], "status": "REASONED"},
    "appwrite-storage": {"text": "Storage defaults local, upload limit 30000000 and server antivirus disabled; enabling scanning requires configured reachable ClamAV.", "components": ["appwrite"], "sources": ["appwrite:s9f5bd3b70f14"], "status": "REASONED"},
    "appwrite-bucket": {"text": "New bucket permissions are empty and fileSecurity=false; enable per-file security deliberately, since bucket grants also permit access.", "components": ["appwrite"], "sources": ["appwrite:se9480e5807b3"], "status": "REASONED"},
    "appwrite-bucket-options": {"text": "Bucket encryption and antivirus default true; bucket antivirus does not enable the server scanner.", "components": ["appwrite"], "sources": ["appwrite:se9480e5807b3"], "status": "REASONED"},
    "appwrite-size": {"text": "Encryption/scanning skip files above 20000000 bytes; cap maximumFileSize at that threshold when either is mandatory and test the boundary.", "components": ["appwrite"], "sources": ["appwrite:se9480e5807b3", "appwrite:s4ab95ecbf6b5"], "status": "REASONED"},
    "appwrite-functions": {"text": "Function execute roles and execution-key scopes default empty; grant narrowly. Disabled functions still admit authorized Server SDK API keys.", "components": ["appwrite"], "sources": ["appwrite:s655a0abb9ef0"], "status": "REASONED"},
    "appwrite-executor": {"text": "Keep executor/orchestrator private, protect Docker-socket authority and replace _APP_EXECUTOR_SECRET; container execution is not demonstrated hostile-tenant isolation.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite:s8e5272615f2e", "appwrite-docs:s2bf9a4746d28"], "status": "REASONED"},
    "verify-pb-records": {"text": "Public rules allow guest reads; locked rules deny with 403, unsatisfied list filters can return empty 200 and view rules 404. Retain owner and separate superuser controls.", "components": ["pb-docs", "curl"], "sources": ["pb-docs:saedbdfbdfc48", "curl:s5e1383feef7d", "curl:s3db522258e44"], "status": "REASONED", "verify": [1]},
    "verify-appwrite-records": {"text": "Broad collection grants defeat document restrictions; removing them must deny unrelated users while document grantees succeed. Compare client/server creation defaults.", "components": ["appwrite-docs"], "sources": ["appwrite-docs:s58ad28816c5d", "appwrite-docs:sa0bd132f7968"], "status": "REASONED", "verify": [1]},
    "verify-appwrite-keys": {"text": "A correctly scoped server key reads despite empty permissions, while a key without scope fails; neither substitutes for an ordinary-user control.", "components": ["appwrite"], "sources": ["appwrite:s193bfa5c6e22"], "status": "REASONED", "verify": [1]},
    "verify-registration": {"text": "On disposable Appwrite fixtures compare open signup 201 with root-only account-limit failure and independent email/IP restrictions; retain login/invitation controls.", "components": ["appwrite"], "sources": ["appwrite:s2bb21218c5ee"], "status": "REASONED", "verify": [2]},
    "verify-pb-bootstrap": {"text": "Guest and ordinary-user _superusers record creation must fail while a valid installer token creates the private operator; static dashboard assets prove no admin access.", "components": ["pb"], "sources": ["pb:saf684a26056b", "pb:s69aa223f52e4"], "status": "REASONED"},
    "verify-appwrite-mfa": {"text": "Console account GET succeeds without MFA, fails with user_more_factors_required for a fresh password-only MFA session, and succeeds after TOTP completion.", "components": ["appwrite", "appwrite-docs"], "sources": ["appwrite-docs:s221c6aaef8df", "appwrite:s193bfa5c6e22"], "status": "REASONED"},
    "verify-pb-writes": {"text": "Compare intended/unauthorized POST/PATCH/DELETE and privileged auth-record management; locked manageRule grants no management and empty-string configuration must fail.", "components": ["pb"], "sources": ["pb:s69aa223f52e4", "pb:sce114368c2ad"], "status": "REASONED"},
    "verify-pb-files": {"text": "Before protection unsigned file GET works; Protected plus private viewRule rejects guests/unrelated-user file tokens with 404 while permitted-user bytes still arrive.", "components": ["pb", "curl"], "sources": ["pb:sa5e571f8d473", "curl:s82a34ee18632"], "status": "REASONED"},
    "verify-pb-realtime": {"text": "Mutate a fixture while comparing collection and record subscriptions; deny unauthorized event delivery, retaining authorized delivery. PB_CONNECT/acknowledgment alone is insufficient.", "components": ["pb", "pb-docs"], "sources": ["pb-docs:sb850a71fad4d", "pb:sfd2f779e8e11"], "status": "REASONED"},
    "verify-pb-mfa": {"text": "Compare password-only completion with password-plus-OTP MFA and verified/unverified authRule logins; clearing authStore must not revoke a retained valid token.", "components": ["pb-docs"], "sources": ["pb-docs:s773e441dd51c"], "status": "REASONED"},
    "verify-pb-ips": {"text": "Compare allowed/excluded superuser sources and forged forwarded headers; excluded sources must get 403 and direct backend access must fail with a working proxy control.", "components": ["pb"], "sources": ["pb:s5b66ca69bf6d", "pb:s03dd7dd84c2a"], "status": "REASONED"},
    "verify-transport": {"text": "Compare HTTP/HTTPS and certificates, Appwrite API/function/site domains and configured/unknown Host; compare browser origins separately from record authorization.", "components": ["pb", "appwrite"], "sources": ["pb:s4b155ef30262", "appwrite:s427bab3733b6"], "status": "REASONED"},
    "verify-abuse": {"text": "Cross each configured threshold with ordinary non-excluded clients and compare disabled/enabled controls; PocketBase limiting yields 429 with later successful recovery.", "components": ["pb", "appwrite-docs"], "sources": ["pb:sf6ffdca4dd39", "appwrite-docs:s000d05106450"], "status": "REASONED"},
    "verify-email": {"text": "Request OTP, verification and recovery messages and confirm receipt and use; request success alone is not delivery evidence.", "components": ["pb", "appwrite-docs"], "sources": ["pb:seb56d3763223", "appwrite-docs:s38a1efa0c7d2"], "status": "REASONED"},
    "verify-pb-recovery": {"text": "Compare plaintext/encrypted persisted settings, restart with retained key and restore local/S3 data; only permitted superuser file tokens may download backups.", "components": ["pb", "pb-docs"], "sources": ["pb:s03dd7dd84c2a", "pb:s31a5adccd695", "pb-docs:s9029ab974cf1"], "status": "REASONED"},
    "verify-appwrite-recovery": {"text": "Restore encrypted fixtures with the original key; a separate wrong-key fixture must not recover encrypted values.", "components": ["appwrite-docs"], "sources": ["appwrite-docs:s256ef73f7b85"], "status": "REASONED"},
    "verify-uploads": {"text": "Compare permitted/unrelated uploads and size-boundary fixtures; mandatory processing requires rejecting over-limit files and confirming accepted-file encryption/scanning.", "components": ["appwrite"], "sources": ["appwrite:se9480e5807b3", "appwrite:s4ab95ecbf6b5"], "status": "REASONED"},
    "verify-functions": {"text": "Compare intended execute roles, unrelated users and privileged server keys, including disabled functions; confirm executor/orchestrator privacy from a second host.", "components": ["appwrite"], "sources": ["appwrite:s655a0abb9ef0", "appwrite:s8e5272615f2e"], "status": "REASONED"},
    "verify-bundle": {"text": "Search filenames using protected exact-secret patterns with a disposable marker control; client bundles must contain neither superuser tokens nor Appwrite API keys, and encoded/split forms can evade scanning.", "components": ["pb-docs", "appwrite-docs"], "sources": ["pb-docs:s773e441dd51c", "appwrite-docs:saa37bb5d4d7e"], "status": "REASONED", "verify": [3]},
    "local-guards": {"text": "Recorded guard tests rejected placeholders and omitted/shortened arguments; this demonstrates shell behavior only, not service access or deployed-bundle scanning.", "components": ["pb-docs", "appwrite-docs"], "sources": ["pb-docs:saedbdfbdfc48", "appwrite-docs:sa0bd132f7968", "appwrite-docs:saa37bb5d4d7e"], "status": "DEMONSTRATED", "evidence": "Local guard tests refused embedded `REPLACE_WITH_` placeholders, `example.com`, angle brackets, empty arguments, and omitted or shortened `set --` lines."},
    "local-syntax": {"text": "All three bash fences have recorded local lint/syntax success, not live service evidence; ShellCheck version is recorded only in the body.", "components": ["appwrite", "pb-docs", "appwrite-docs"], "sources": ["pb-docs:saedbdfbdfc48", "appwrite:s2bb21218c5ee", "appwrite-docs:saa37bb5d4d7e"], "status": "DEMONSTRATED", "evidence": "All three bash blocks passed ShellCheck 0.11.0 and `bash -n` during authoring."},
    "source-limits": {"text": "PocketBase CLI/--dev and Appwrite requester/call-site pins remain cited; utopia-php/database role matching, Database reads/dispatch and status/skip are cited. Adapter getDocument/find use of shared authorization, any document filtering with/without collection grants (including non-skip find with documentSecurity enabled), and disabled-status bypass remain untraced; live authorization is not demonstrated.", "components": ["appwrite-docs", "pb-docs", "appwrite", "utopia-php-database"], "sources": ["appwrite-docs:s58ad28816c5d", "pb-docs:s9029ab974cf1", "appwrite:s7ba6f9c71972", "utopia-php-database:s44e735a78b9d", "utopia-php-database:sfda128d99ef9", "utopia-php-database:s610f3fb8fa73", "utopia-php-database:s4f7f3ed32a53", "utopia-php-database:sa3038716384d", "utopia-php-database:scf82badc07e5", "utopia-php-database:s7cf5a05cf798", "utopia-php-database:s3389fa5854d5", "utopia-php-database:s01a8ce8001e0"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
