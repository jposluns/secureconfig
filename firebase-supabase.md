# Firebase and Supabase: the rules are the security

These platforms handle TLS for you on their hosted endpoints; the exposure works differently.
Client SDKs talk to the backend using keys that ship in your frontend code and are **public by
design**: the Firebase API key and Supabase publishable or legacy `anon` key. Client data access
needs Firebase Security Rules or Postgres row-level security (RLS) alongside grants, IAM,
endpoint authorization, and App Check where applicable. AI-generated apps repeatedly ship with
that layer open because "it worked in testing". On Supabase the gate also depends on how exposed
views and functions execute, not only on the table policies.

Documentation was checked in September 2026. Defaults below describe the documentation at the
time of writing; inspect the effective settings of each project. Live behavior has not been
demonstrated in this authoring environment. The Verify section records the missing prerequisites
and demonstration debt.

## Firebase

### 1. Set ownership rules in all three products

Every Firestore, Realtime Database, and Storage instance needs explicit security rules. Never
deploy the all-open rule (`allow read, write: if true;` or `".read": true, ".write": true`);
it exposes the entire datastore to anyone with your public config. Require authentication and
scope by user: `request.auth != null` establishes authentication, not authorization to another
user's data. See [Firebase Security Rules](https://firebase.google.com/docs/rules) and
[ownership examples](https://firebase.google.com/docs/rules/basics).

Do not assume a new instance denies access. Creating a Firestore database offers a **test mode**
that lets anyone read and overwrite your data alongside locked production mode. Firestore
production mode and RTDB locked mode deny client reads and writes. Test-mode templates grant
public access for about a month; their expiry ends that access, but does not protect data during
the trial. Inspect the actual expiry and replace the template before using sensitive data. See
[Firestore starting modes](https://firebase.google.com/docs/firestore/quickstart),
[RTDB starting modes](https://firebase.google.com/docs/database/web/start), and
[Firebase's test-rule expiry announcement](https://firebase.google.com/support/releases).

For Firestore, this is a complete ownership ruleset:

```text
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

Version 2 matters: the recursive wildcard matches zero or more path items, so this includes
`/users/{userId}` itself and its descendant documents. Under version 1, the same recursive match
excludes the user document itself. Unmatched paths remain denied. Remove overlapping permissive
rules; a matching denial does not override another matching grant. See
[Firestore rule structure](https://firebase.google.com/docs/firestore/security/rules-structure).

RTDB uses a separate JSON rules engine. Put ownership checks under `users.$uid`:

```json
{
  "rules": {
    ".read": false,
    ".write": false,
    "users": {
      "$uid": {
        ".read": "auth !== null && auth.uid === $uid",
        ".write": "auth !== null && auth.uid === $uid"
      }
    }
  }
}
```

Remove any root or ancestor `.read` or `.write` grant that would authorize everyone.
RTDB child rules cannot revoke a parent grant. Read individual authorized user paths; RTDB rules
do not filter a parent read into its permitted children. See
[RTDB rule syntax and cascading](https://firebase.google.com/docs/database/security/core-syntax).

Storage has its own rules; Firestore rules do **not** secure uploaded objects. Firebase's basic
rules documentation describes authenticated Storage access in its default-rules prose while
showing a deny-all Storage ruleset. Establish deny-all explicitly instead of relying on a
starting-mode label:

```text
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /{allPaths=**} {
      allow read, write: if false;
    }
  }
}
```

Then replace that ruleset with deliberate ownership access, for example:

```text
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /users/{userId}/{allPaths=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

This authorizes objects beneath the caller's UID path. Other paths remain denied unless another
rule grants access. See [basic rules](https://firebase.google.com/docs/rules/basics) and
[Storage rule structure](https://firebase.google.com/docs/storage/security/core-syntax).

A distributed Storage download URL is a bearer credential: it does not expire, and anyone
holding it can access the object. Tightening ownership Rules does not revoke that URL. For
sensitive objects, revoke previously distributed download tokens in the Firebase console and
use authenticated SDK direct downloads such as `getBlob()` or `getBytes()` so Rules govern
access. See [Admin shareable URLs](https://firebase.google.com/docs/storage/admin/start),
[download-token revocation](https://firebase.google.com/docs/reference/kotlin/com/google/firebase/storage/StorageReference),
and [SDK direct downloads](https://firebase.google.com/docs/storage/web/download-files).

Inspect the deployed rules for every Firestore database, bucket, and RTDB instance; keep
production locked-by-default, open specific paths deliberately, and test with the Rules
Playground and emulator before deploying. Keep local and deployed rule definitions in sync.
See [getting started with rules](https://firebase.google.com/docs/firestore/security/get-started)
and [Storage rule management](https://firebase.google.com/docs/storage/security/get-started).

### 2. Authorize Functions before privileged work

Server-side credentials, including service accounts for the Admin SDK, bypass client Security
Rules; they stay on servers only, handled per [secrets.md](secrets.md). IAM and the server's own
authorization checks therefore matter. A function using the Admin SDK must not treat successful
SDK access as evidence that its caller was entitled to the data. See
[Firestore server access](https://firebase.google.com/docs/firestore/security/rules-structure).

Callable authentication is optional: the callable protocol validates a supplied ID token, but
does not require the caller to supply one. In second-generation `onCall` handlers, reject missing
`request.auth` before privileged work and derive identity from `request.auth.uid`. Treat
`request.data` as untrusted input, including any UID, role, document path, or ownership claim.
First-generation handlers use `context.auth` instead. See the
[callable protocol](https://firebase.google.com/docs/functions/callable-reference),
[second-generation handlers](https://firebase.google.com/docs/functions/callable), and
[first-generation handlers](https://firebase.google.com/docs/functions/1st-gen/callable-1st).

This second-generation example identifies the authenticated caller and also enforces App Check:

```javascript
const { onCall, HttpsError } = require("firebase-functions/v2/https");

exports.whoAmI = onCall({ enforceAppCheck: true }, (request) => {
  if (!request.auth) {
    throw new HttpsError("unauthenticated", "Sign in first.");
  }
  return { uid: request.auth.uid };
});
```

Before extending it to read or change protected resources, authorize that UID for the requested
operation and validate the submitted data. App Check does not replace those checks.
The enforcement option requires `firebase-functions` 4.0.0 or newer. See
[callable App Check enforcement](https://firebase.google.com/docs/app-check/cloud-functions).

An `onRequest` HTTP handler does not inherit callable authentication. For end-user endpoints,
extract the bearer ID token, validate it with the Admin SDK's `verifyIdToken()`, reject missing or
invalid tokens, and authorize the verified UID. For IAM-controlled endpoints, restrict invocation
with `invoker: "private"` or an explicit invoker list and configure the intended principals.
Firebase user ID tokens and IAM invocation credentials serve different checks. See
[ID-token verification](https://firebase.google.com/docs/auth/admin/verify-id-tokens),
[HTTP handlers](https://firebase.google.com/docs/functions/http-events), and
[`HttpsOptions.invoker`](https://firebase.google.com/docs/reference/functions/2nd-gen/node/firebase-functions.https.httpsoptions).

### 3. Enforce App Check and restrict public API keys

Register each app with its appropriate App Check provider, deploy compatible clients, and inspect
request metrics before enabling enforcement. Registration alone does not enforce anything.
In the App Check console, enable enforcement separately for Firestore, Realtime Database, and
Storage; configure `enforceAppCheck: true` separately on each protected callable. See
[provider registration and client rollout](https://firebase.google.com/docs/app-check/web/recaptcha-enterprise-provider)
and [per-product enforcement](https://firebase.google.com/docs/app-check/enable-enforcement).

In Google Cloud Console > APIs & Services > Credentials, restrict the public Web API key to the
intended HTTP referrers. Use Android application restrictions for Android keys and iOS application
restrictions for iOS keys. A key supports one application-restriction type, so use separate keys
for different types. Apply API restrictions as well. See
[application and API restrictions](https://docs.cloud.google.com/api-keys/docs/add-restrictions-api-keys).

Build the API allowlist from Firebase's full product table. For example, Authentication uses
`identitytoolkit.googleapis.com` and `securetoken.googleapis.com`, while App Check uses
`firebaseappcheck.googleapis.com`; those three are not a complete list for every Firebase app.
Retest each product after changing restrictions. Keep unrelated, especially billable, APIs on
separate restricted keys. See
[Firebase API-key restrictions and the product table](https://firebase.google.com/docs/projects/api-keys).

The public Firebase config, including `databaseURL`, identifies resources; it grants no
authorization. Hiding or changing it does not repair open rules. See
[Firebase configuration objects](https://firebase.google.com/docs/web/learn-more).

### 4. Limit sign-in methods and keep emulators private

Disable unused sign-in providers in Firebase Authentication, including Anonymous when the app
does not need it. Anonymous authentication is opt-in, but an anonymous account still has an
authenticated UID and satisfies an authentication-only Rules check. See
[anonymous authentication](https://firebase.google.com/docs/auth/web/anonymous-auth).

Enable **Email enumeration protection** under Authentication Settings > User account management >
User actions. At the time of writing, it is enabled by default only for projects created on or
after September 15, 2023. It changes sign-in errors and account-discovery behavior; update clients
that rely on the old responses. Signup can still return `EMAIL_EXISTS`, so this is not complete
protection against discovering registered addresses. See
[email enumeration protection](https://docs.cloud.google.com/identity-platform/docs/admin/email-enumeration-protection).

Emulators listen on localhost by default. Keep their listeners, UI, and hub private: no public
ports, reverse-proxy routes, or public tunnels. A private listener is especially important because
Firestore, RTDB, and Storage emulators run with **open data security** when Rules configuration is
missing. Merge these entries into `firebase.json`, with the referenced files containing the
intended rules:

```json
{
  "firestore": {
    "rules": "firestore.rules"
  },
  "database": {
    "rules": "database.rules.json"
  },
  "storage": {
    "rules": "storage.rules"
  }
}
```

Inspect existing emulator host overrides and restore localhost-only binding where necessary.
See [emulator configuration](https://firebase.google.com/docs/emulator-suite/install_and_configure)
and [the documented localhost default](https://firebase.google.com/docs/emulator-suite/use_hosting).

## Supabase

For the hosted direct-Postgres endpoint and database pooler, restrict allowed client IP ranges
with Dashboard **Network Restrictions**, enable **Enforce SSL on incoming connections**, and
keep the `postgres` and other database-role passwords secret; see
[Network Restrictions](https://supabase.com/docs/guides/platform/network-restrictions),
[SSL enforcement](https://supabase.com/docs/guides/platform/ssl-enforcement), and
[database roles and passwords](https://supabase.com/docs/guides/database/postgres/roles).

### 1. Restrict the Data API, grants, and rows

Enable RLS on **every** table exposed through the API, then write policies for intended access.
An API-exposed table without RLS is readable or writable by a role only when that role also has
the corresponding grants. Projects retaining Supabase's automatic grants can therefore expose
new tables to the public `anon` key. At the time of writing, Supabase documents a transition
towards opt-in grants; do not assume identical defaults across projects. Review grants and RLS
separately. Dashboard Table Editor creation enables RLS; SQL-created tables require explicit
enablement. See [Data API security](https://supabase.com/docs/guides/api/securing-your-api).

For an existing `public.profiles` table whose `user_id` column contains the owner's Auth UUID,
this baseline permits authenticated owners to select their rows:

```sql
alter table public.profiles enable row level security;
revoke all privileges on table public.profiles from public, anon, authenticated;
grant select on table public.profiles to authenticated;

create policy "own rows"
on public.profiles for select
to authenticated
using ((select auth.uid()) = user_id);
```

Review existing policies and inherited or column-level grants as well; adding a narrow policy
does not cancel an existing broad permissive policy. See
[Supabase RLS](https://supabase.com/docs/guides/database/postgres/row-level-security) and
[PostgreSQL policy combination](https://www.postgresql.org/docs/current/sql-createpolicy.html).

Write separate policies per operation (`select`, `insert`, `update`, `delete`). No policy means
no row access once RLS is on for ordinary roles subject to RLS, which is the correct starting
point. Policies grant intended access; they are not required to make an RLS-enabled table closed.
Table owners normally bypass RLS, and superusers and `BYPASSRLS` roles bypass it. `TRUNCATE` is
outside RLS, so do not grant it to client roles. See
[PostgreSQL row security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html).

Install only the write policies and matching grants the app intentionally needs. For an app
that permits owners to create, update, and delete their profiles:

```sql
grant insert, update, delete on table public.profiles to authenticated;

create policy "insert own rows"
on public.profiles for insert
to authenticated
with check ((select auth.uid()) = user_id);

create policy "update own rows"
on public.profiles for update
to authenticated
using ((select auth.uid()) = user_id)
with check ((select auth.uid()) = user_id);

create policy "delete own rows"
on public.profiles for delete
to authenticated
using ((select auth.uid()) = user_id);
```

The UPDATE policy checks both the existing row and its proposed replacement, preventing a caller
from taking another user's row or changing ownership away from themselves. For roles subject
to RLS, UPDATE also needs applicable SELECT (or ALL) policies when it reads table columns,
for example in WHERE, RETURNING, or a SET expression. Data API updates that filter on existing
rows therefore need the SELECT policy too. See
[PostgreSQL CREATE POLICY](https://www.postgresql.org/docs/current/sql-createpolicy.html) and
[operation-specific RLS policies](https://supabase.com/docs/guides/database/postgres/row-level-security).

`public` is exposed by default. Restrict **Exposed schemas** to the schemas intended for client
access, or use a dedicated `api` schema and keep internal tables and helpers outside it. Grant
schema usage and object privileges deliberately; changing schemas is not a substitute for RLS.
See [custom API schemas](https://supabase.com/docs/guides/api/using-custom-schemas).

If the application does not use the Data API, turn **Enable Data API** off in the Dashboard's
Data API integration settings. This closes its generated REST endpoints regardless of table
policies. It does not disable every other Supabase service. See
[disabling the Data API](https://supabase.com/docs/guides/api/securing-your-api).

### 2. Separate client keys, server keys, and JWT signing keys

Use `sb_publishable_...` keys in clients. With no signed-in session, a publishable key uses the
`anon` role; with a signed-in user's session, requests use `authenticated`.
Keep `sb_secret_...` keys only in trusted backends: they resolve to `service_role`, which has
`BYPASSRLS`. The legacy `service_role` key likewise bypasses RLS; it is a server-only secret that
must never reach the client bundle or the repository. Browser rejection of a secret key does
not make a leaked key safe: another client can use it. See
[API keys](https://supabase.com/docs/guides/api/api-keys).

Creating replacement publishable and secret keys does **not** disable legacy keys. Migrate every
consumer, confirm it uses the replacement, then explicitly deactivate the legacy keys in
Settings > API Keys. For a compromised secret key, replace it in the trusted consumers and
delete the compromised key. Fix the exposure as well as retiring the credential. See
[key migration](https://supabase.com/docs/guides/getting-started/migrating-to-new-api-keys).

JWT signing keys have a separate lifecycle. **Rotate keys** changes the key used to sign new
JWTs; the previous key remains trusted until it is revoked. Plan revocation and verifier-cache
propagation explicitly. API-key replacement is not evidence that an old JWT signing key has
lost trust. See [JWT signing keys](https://supabase.com/docs/guides/auth/signing-keys).

### 3. Check views and privileged functions

A view checks underlying relations with **its owner's** privileges by default and applies the
owner's row-level security policies rather than the caller's. On Supabase a view is typically
created by the `postgres` user, so it can disclose rows hidden by the caller's table policies.
That requires a reachable schema, suitable grants, and a view query and owner privileges that
permit the disclosure; possession of an `anon` key alone does not guarantee it. See
[PostgreSQL view security](https://www.postgresql.org/docs/current/sql-createview.html) and
[Supabase RLS and views](https://supabase.com/docs/guides/database/postgres/row-level-security).

On PostgreSQL 15 and later, make every API-exposed view apply the caller's policies instead:

```sql
alter view public.REPLACE_WITH_VIEW_NAME set (security_invoker = true);
```

The caller also needs appropriate privileges on the underlying relations. See
[`ALTER VIEW`](https://www.postgresql.org/docs/current/sql-alterview.html) and the
[PostgreSQL 15 release notes](https://www.postgresql.org/docs/release/15.0/).

On PostgreSQL 14 and earlier there is no `security_invoker`: revoke ALL privileges on the view
from `public` as well as from `anon` and `authenticated`, or keep it in a schema the API does not
expose. A simple view is automatically updatable, so revoking only `select` can leave
`insert`/`update`/`delete` that write through the owner and bypass the table's RLS.
Revoking the two API roles alone leaves access they inherit from `PUBLIC`, so confirm with
`select has_table_privilege('anon', 'public.REPLACE_WITH_VIEW_NAME', 'select, insert, update, delete');`,
which must return `f`.

```sql
-- PostgreSQL 14 or earlier: revoke ALL privileges on an API-exposed view from all three, then confirm both API roles lost every one.
-- Run the REVOKE as the view's owner; a check still returning t means another grant or role provides access.
-- A simple view is automatically updatable, so revoking only SELECT can leave INSERT/UPDATE/DELETE that write through the owner.
revoke all privileges on table public.REPLACE_WITH_VIEW_NAME from public, anon, authenticated;
select has_table_privilege('anon', 'public.REPLACE_WITH_VIEW_NAME', 'select, insert, update, delete'),
       has_table_privilege('authenticated', 'public.REPLACE_WITH_VIEW_NAME', 'select, insert, update, delete');   -- both must be f
```

See [`REVOKE`](https://www.postgresql.org/docs/current/sql-revoke.html) and
[privilege inquiry functions](https://www.postgresql.org/docs/current/functions-info.html).
The comma-separated privilege check returns true if **any** listed privilege remains.

Prefer `SECURITY INVOKER` for functions. A `SECURITY DEFINER` function likewise runs as its owner
and can return rows RLS would hide. Keep such functions out of API-exposed schemas unless they
enforce their own authorization, and revoke execution by default:

```sql
revoke execute on function public.REPLACE_WITH_FUNCTION_NAME from public, anon, authenticated;
```

Include the argument types where the function name is overloaded. Where DEFINER is necessary,
set `SET search_path = ''`, schema-qualify every referenced relation and helper, and enforce caller
authorization inside the function, including MFA where required. An empty search path does not
supply authorization. See [database functions](https://supabase.com/docs/guides/database/functions).

For an existing function with one UUID argument, the settings and selective grant take this
shape. Substitute its actual signature; grant execution only after reviewing its body:

```sql
alter function public.REPLACE_WITH_FUNCTION_NAME(uuid) set search_path = '';
revoke execute on function public.REPLACE_WITH_FUNCTION_NAME(uuid)
  from public, anon, authenticated;
grant execute on function public.REPLACE_WITH_FUNCTION_NAME(uuid)
  to authenticated;
```

New PostgreSQL functions normally grant execution to `PUBLIC`. Create privileged functions and
set their privileges in the same transaction. To change future defaults for functions created
by `postgres`, remove the global PUBLIC grant and any schema-specific API-role defaults:

```sql
alter default privileges for role postgres
  revoke execute on functions from public;

alter default privileges for role postgres in schema public
  revoke execute on functions from anon, authenticated;
```

Repeat for the actual function-creating roles and relevant schemas. Defaults do not change
existing functions; a schema-scoped revocation cannot cancel a global default grant.
See [`CREATE FUNCTION`](https://www.postgresql.org/docs/current/sql-createfunction.html),
[`ALTER FUNCTION`](https://www.postgresql.org/docs/current/sql-alterfunction.html), and
[`ALTER DEFAULT PRIVILEGES`](https://www.postgresql.org/docs/current/sql-alterdefaultprivileges.html).

Audit API-callable wrappers around `http`, `net.http_get`, and `net.http_post`. Revoke execution
from `PUBLIC`, `anon`, and `authenticated` on unneeded entry points, using each installed
signature. Where needed, constrain callers, destinations, and transmitted data. The documented
ability to issue outbound requests implies a possible SSRF or data-exfiltration path if an
exposed wrapper accepts attacker-controlled destinations or forwards privileged data; enabling
an extension alone is not proof of an exploitable endpoint. See
[`http`](https://supabase.com/docs/guides/database/extensions/http) and
[`pg_net`](https://supabase.com/docs/guides/database/extensions/pg_net).

Restrict `vault.decrypted_secrets` and every DEFINER function that reads it:

```sql
revoke all privileges on table vault.decrypted_secrets from public, anon, authenticated;
```

Keep Vault outside exposed schemas and review indirect access through views and functions.
Vault decrypts values through this view; encryption at rest does not prevent an authorized
query or privileged wrapper from disclosing plaintext through an API. See
[Vault](https://supabase.com/docs/guides/database/vault).

### 4. Authorize Storage separately

Keep sensitive buckets **Private**. Private downloads require authorized access or a deliberately
issued, time-limited signed URL. A **Public** bucket bypasses retrieval checks for anyone with the
asset URL; upload, delete, move, and copy operations still undergo access checks. See
[bucket access models](https://supabase.com/docs/guides/storage/buckets/fundamentals).

Application-table policies do not secure Storage objects. Define policies on `storage.objects`,
constrained by both `bucket_id` and the caller's path or ownership. For a private bucket whose
object names begin with the owner's UUID:

```sql
create policy "read own files"
on storage.objects for select
to authenticated
using (
  bucket_id = 'REPLACE_WITH_PRIVATE_BUCKET'
  and (storage.foldername(name))[1] = (select auth.uid())::text
);

create policy "upload own files"
on storage.objects for insert
to authenticated
with check (
  bucket_id = 'REPLACE_WITH_PRIVATE_BUCKET'
  and (storage.foldername(name))[1] = (select auth.uid())::text
);
```

See [Storage helpers](https://supabase.com/docs/guides/storage/schema/helper-functions) and
[Storage access control](https://supabase.com/docs/guides/storage/security/access-control).

Upload needs INSERT. Upsert additionally needs SELECT and UPDATE policies. If overwrites are
intended, give UPDATE both `USING` and `WITH CHECK` with the same bucket and owner-path condition;
add DELETE only if intended. Remove broader existing policies that would admit other users.
The example above deliberately does not permit overwrites or deletion.

### 5. Require private Realtime channels

At the time of writing, **Allow public access to channels** is enabled by default. Disable it
in Realtime Settings to require private channels. Set `config.private` on clients as well; a
client's private flag alone does not disable public channels for the project. See
[Realtime settings](https://supabase.com/docs/guides/realtime/settings).

For channels named `user:` followed by the authenticated user's UUID:

```javascript
const channel = supabase.channel('user:REPLACE_WITH_AUTHENTICATED_USER_ID', {
  config: { private: true }
});
```

Authorize receiving and sending separately on `realtime.messages`, checking both the topic and
the message extension:

```sql
create policy "receive own channel"
on realtime.messages for select
to authenticated
using (
  (select realtime.topic()) = 'user:' || (select auth.uid())::text
  and extension in ('broadcast', 'presence')
);

create policy "send own channel"
on realtime.messages for insert
to authenticated
with check (
  (select realtime.topic()) = 'user:' || (select auth.uid())::text
  and extension in ('broadcast', 'presence')
);
```

These policies govern Broadcast and Presence; replace the ownership expression with an explicit
membership check for shared rooms. See
[Realtime authorization](https://supabase.com/docs/guides/realtime/authorization).

Postgres Changes uses source-table authorization. Private-channel policies are not a universal
Realtime filter. Test that subscription path separately; in particular, the documented DELETE
event limitations differ from normal row reads. See
[Postgres Changes security and limitations](https://supabase.com/docs/guides/realtime/postgres-changes).

### 6. Limit registration and enforce MFA

For invite-only projects, disable **Allow new users to sign up**. Disable **Allow anonymous
sign-ins** and unused providers unless the application deliberately needs them. Inspect the
hosted project's settings rather than assuming a universal hosted default. See
[Auth configuration](https://supabase.com/docs/guides/auth/general-configuration).

For CLI-managed local configuration in `supabase/config.toml`:

```toml
[auth]
enable_signup = false
enable_anonymous_sign_ins = false
```

At the time of writing, the CLI defaults are `true` and `false`, respectively. Editing this local
file is not evidence that hosted settings changed. See
[the CLI configuration reference](https://supabase.com/docs/guides/local-development/cli/config).

Supabase Auth supports MFA, with TOTP on every plan at the time of writing. Enrolment alone
changes nothing about table authorization: enforce it in your policies by requiring the `aal2`
assurance level, so a session that has not completed the second factor cannot read protected
rows. See [mfa.md](mfa.md),
[TOTP availability](https://supabase.com/docs/guides/auth/auth-mfa/totp), and
[MFA enforcement](https://supabase.com/docs/guides/auth/auth-mfa).

```sql
create policy "mfa required"
on public.profiles as restrictive
to authenticated
using ((select auth.jwt()->>'aal') = 'aal2')
with check ((select auth.jwt()->>'aal') = 'aal2');
```

Keep the applicable permissive ownership policies alongside this restrictive policy. It narrows
their permissions; it does not grant access itself. Repeat the assurance requirement on other
protected surfaces where needed. See
[restrictive policies](https://www.postgresql.org/docs/current/sql-createpolicy.html).

### 7. Authorize Edge Functions before privileged work

[Edge Functions](https://supabase.com/docs/guides/functions) expose server-side handlers.
At the time of writing, platform JWT verification is configured per function and enabled by
default (`verify_jwt = true`). Deploying with `supabase functions deploy --no-verify-jwt`
disables that check, as commonly needed for external webhooks. The handler MUST then
authenticate and authorize callers itself before protected work, for example by verifying
the provider's webhook signature. See the
[deployment CLI reference](https://supabase.com/docs/reference/cli/supabase-functions-deploy)
and [function authentication](https://supabase.com/docs/guides/functions/auth).

Even with JWT verification enabled, authorize the verified caller for the requested resource
and operation. Passing the platform check alone does not establish user authorization:
Supabase also documents API-key compatibility paths through that check. See
[authorization headers and JWT verification](https://supabase.com/docs/guides/functions/auth-headers).

The function environment carries privileged secrets, including the legacy
`SUPABASE_SERVICE_ROLE_KEY`, which bypasses RLS. Treat an unauthenticated function with access
to those credentials as a privileged surface. Keep secrets in managed environment variables,
exclude local secret files from source control, and never expose secret values in responses,
logs, or client bundles. Secret hygiene and in-function authorization are both required. See
[Edge Function secrets](https://supabase.com/docs/guides/functions/secrets).

## Verify

Use disposable projects and harmless fixtures for exposed/fixed comparisons. Do not temporarily
open production data. No disposable cloud project, controlled user accounts, deployed client
bundle, or authorized writable service-fixture environment was supplied here. The checks below
are **reasoned, not demonstrated**, and are tracked in the demonstration backlog.

### 1. Compare unauthenticated, owner, and unrelated-user access

**REASONED:** No Firebase/Supabase test project or controlled A/B sessions was supplied.
Seed a known row owned by user A and one owned by user B first, so an empty result is not mistaken
for enforcement. Seed equivalent Firebase documents, RTDB nodes, and Storage objects.

With only the public key/config and no signed-in user, reads and writes against protected
tables/paths must be refused or return no rows and change nothing. Signed in as user A, reading
and writing user B's rows must be refused. An authorized owner read on the same path MUST
succeed, so denial is attributable to access controls rather than a broken request or wrong
endpoint. Require owner-write success only for operations the app intentionally permits after
installing their grants and policies. The baseline Supabase policy above permits SELECT only.
With the MFA restriction installed, the positive authenticated test also needs `aal2`.

Compare the following requests against a disposable exposed fixture and its fixed counterpart:

| Surface | Concrete request and expected distinction |
| --- | --- |
| Firestore | **REASONED:** In the Rules Playground or client test harness, get and write `/users/REPLACE_WITH_USER_B_ID` and `/users/REPLACE_WITH_USER_B_ID/items/probe` without authentication, as A, and as B. Open rules admit the first two identities; the ownership rules deny them and admit B for these operations. Test the user document itself to catch a version-1 recursive-match mistake. See [Firestore rules](https://firebase.google.com/docs/firestore/security/rules-structure). |
| RTDB | **REASONED:** Read and write `/users/REPLACE_WITH_USER_B_ID/probe` with the same identities. An ancestor grant admits unauthorized requests; the fixed rules deny them and admit B. See [RTDB cascading](https://firebase.google.com/docs/database/security/core-syntax). |
| Firebase Storage | **REASONED:** Read and upload `users/REPLACE_WITH_USER_B_ID/probe.txt` through the Storage client. Open or authentication-only rules admit unauthorized access; ownership rules admit B and reject A and unsigned requests. See [Storage rules](https://firebase.google.com/docs/storage/security/core-syntax). |
| Firebase Storage download tokens | **REASONED:** No disposable object, existing download URL, token-revocation access, or owner session was supplied. Save an existing download URL for `users/REPLACE_WITH_USER_B_ID/probe.txt`. With caching disabled and no session, cookies, or Authorization header, send HTTP GET to that exact URL before and after tightening ownership Rules: both should return the object's bytes. Revoke its download token in the Firebase console, keep the object and Rules unchanged, and repeat GET to the same saved URL: require an HTTP denial with no object bytes. A network or CORS failure is inconclusive. Before and after revocation, B's authenticated `getBytes(ref(storage, 'users/REPLACE_WITH_USER_B_ID/probe.txt'))` must still return the bytes; configure browser CORS for the test origin. See [shareable URLs](https://firebase.google.com/docs/storage/admin/start), [token revocation](https://firebase.google.com/docs/reference/kotlin/com/google/firebase/storage/StorageReference), and [direct downloads](https://firebase.google.com/docs/storage/web/download-files). |
| Supabase tables | **REASONED:** Request `GET /rest/v1/profiles?select=user_id&user_id=eq.REPLACE_WITH_USER_B_ID`. With matching grants and RLS disabled, B's seeded row is exposed. With the fixed grants/policies, unsigned requests and A receive no B row; B at the required assurance level receives it. For intentionally enabled writes, use POST to create a disposable profile, PATCH to change it, and DELETE to remove it; inspect persisted state as well as response status. See [select requests](https://supabase.com/docs/reference/javascript/select) and [row-security semantics](https://www.postgresql.org/docs/current/ddl-rowsecurity.html). |

For the Supabase GET comparison, prepare protected header files privately, outside source control.
The unsigned file contains an `apikey` header with the publishable or legacy `anon` key; the
signed-in file also contains `Authorization: Bearer` with the test user's access token.
Do not use a secret or service-role key for an ordinary-user test.

Paste the whole block and substitute inside the single quotes. Use an unsigned HTTPS endpoint
URL, never a credential-bearing or signed URL. The response must contain only your harmless
fixture data. Credentials enter curl through stdin, not process arguments; that does not protect
a carelessly created header file, shell history, or tracing. The write-out fields require curl
7.75.0 or newer.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_REQUEST_URL' 'REPLACE_WITH_PROTECTED_HEADERS_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the request URL; not probing" ;;
    https://*)
      case "$2" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
          echo "substitute the protected headers file; not probing" ;;
        *)
          if [ -r "$2" ]; then
            curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
              --header @- --write-out '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
              --url "$1" < "$2"
          else
            echo "headers file is unreadable; no conclusion"
          fi ;;
      esac ;;
    *) echo "use the project's HTTPS endpoint; not probing" ;;
  esac
)
```

A timeout, DNS failure, malformed request, or missing fixture proves nothing about authorization.
Retain the positive owner control. Supply valid App Check tokens when testing Firebase ownership
so an unrelated App Check rejection does not hide an open rule.

### 2. Test views, functions, and indirect access

- **REASONED:** No deployed view inventory or A/B sessions was supplied. Reads through every
  API-exposed view must respect the intended table boundary: request
  `/rest/v1/REPLACE_WITH_VIEW_NAME` with only the public key, then, signed in as user A, request
  user B's rows using the view's actual ownership column. An exposed owner-privileged view can
  return those rows while the table denies them; an invoker view or revoked endpoint must not.
  If it returns them, check owner privileges and overly broad policies. Confirm intended owner
  reads still succeed, or confirm deliberate endpoint removal. See
  [view security](https://www.postgresql.org/docs/current/sql-createview.html).

- **REASONED:** No deployed function inventory or disposable RPC fixtures was supplied. Every
  API-exposed function is checked the same way, because the view check cannot see it: call
  `POST /rest/v1/rpc/REPLACE_WITH_FUNCTION_NAME` with its documented JSON arguments, first with
  only the public key, then as A requesting B's data. A `SECURITY DEFINER` function **can return
  rows** while the table and view checks both look clean; this separate check catches that path.
  Repeat for every overload and use valid, harmless arguments so argument errors do not masquerade
  as authorization. Fixed functions must deny unauthorized data or operations while permitting
  their intended caller. See [RPC calls](https://supabase.com/docs/reference/javascript/rpc)
  and [function privileges](https://supabase.com/docs/guides/database/functions).

- **REASONED:** No outbound-request collector or disposable Vault secret was supplied. For each
  HTTP wrapper, call its RPC with a controlled destination and harmless marker. An exposed
  wrapper may cause an outbound request; after revocation or caller checks, an unauthorized
  request must cause none. Commit an authorized `pg_net` fixture transaction before expecting
  its request. For each Vault-reading wrapper, use a disposable nonsecret canary: an exposed
  function may return it, while the fixed endpoint must withhold it from unauthorized callers.
  Check `has_function_privilege` for each signature and `has_table_privilege` on
  `vault.decrypted_secrets` for both API roles as supporting evidence. See
  [`pg_net`](https://supabase.com/docs/guides/database/extensions/pg_net),
  [Vault](https://supabase.com/docs/guides/database/vault), and
  [privilege checks](https://www.postgresql.org/docs/current/functions-info.html).

### 3. Test Storage and Realtime independently

| Surface | Required exposed/fixed comparison |
| --- | --- |
| Supabase Storage | **REASONED:** No bucket, file fixture, or A/B sessions was supplied. Download B's known file with `supabase.storage.from('REPLACE_WITH_PRIVATE_BUCKET').download('REPLACE_WITH_USER_B_ID/probe.txt')` as A and B; also request its public asset URL without a session. A public bucket serves the public URL; the private, restricted bucket must withhold unauthorized bytes while B's authorized download succeeds. Test fresh uploads and, only if intended, upserts using `{ upsert: true }`; A must not write B's path. See [downloads](https://supabase.com/docs/guides/storage/serving/downloads), [uploads](https://supabase.com/docs/guides/storage/uploads/standard-uploads), and [bucket access](https://supabase.com/docs/guides/storage/buckets/fundamentals). |
| Broadcast and Presence | **REASONED:** No Realtime project or connected A/B clients was supplied. Join `user:REPLACE_WITH_USER_B_ID` as A and B, attempt a Broadcast send and Presence tracking, and observe from B's client. Public channels admit unintended participation when allowed. After disabling public channels, a client without `private: true` must be rejected; the private policies must withhold B's channel operations from A while allowing B. A socket connection alone is not proof of authorized message delivery. See [settings](https://supabase.com/docs/guides/realtime/settings) and [authorization](https://supabase.com/docs/guides/realtime/authorization). |
| Postgres Changes | **REASONED:** No publication or live subscription fixture was supplied. Subscribe as A to INSERT/UPDATE changes on `public.profiles`, then change seeded A and B rows through the controlled fixture. An exposed source table can disclose B's changes; fixed source-table authorization must withhold them while A's intended events arrive. Evaluate DELETE separately against its documented limitations. See [Postgres Changes](https://supabase.com/docs/guides/realtime/postgres-changes). |

### 4. Test Functions, App Check, and emulator exposure

- **REASONED:** No deployed Supabase Edge Function, disposable operation fixture, or caller
  credentials was supplied. Send `POST /functions/v1/REPLACE_WITH_FUNCTION_NAME` to the
  disposable project's function with a valid fixture payload, first without `Authorization`
  or `apikey`, then with `Authorization: Bearer invalid-test-token` and no `apikey`.
  With JWT verification disabled and handler authorization absent, these requests can reach
  privileged work; the corrected handler must reject unauthorized requests before that work.
  With JWT verification enabled, both requests must receive HTTP 401 before the handler runs.
  Omit API keys in these two probes because API-key compatibility can pass the platform check.
  For a webhook, also compare missing/invalid provider signatures with a valid signed request.
  For a user endpoint, compare A attempting B's operation with the authorized owner's request.
  The authorized positive control must succeed; inspect persisted effects as well as response
  status, and check that responses and logs disclose no secrets. See
  [JWT verification](https://supabase.com/docs/guides/functions/auth-headers),
  [handler authentication](https://supabase.com/docs/guides/functions/auth), and
  [secret handling](https://supabase.com/docs/guides/functions/secrets).

- **REASONED:** No deployed callable, HTTP endpoint, or test credentials was supplied. Send
  `POST` with `{"data":{}}` to each callable, first with valid App Check but no user ID token.
  A handler lacking its own authentication check can enter privileged work; the fixed handler
  must reject it. Repeat with A attempting B's operation and with the intended owner. For each
  `onRequest` endpoint, send its valid application request without credentials, with invalid
  credentials, and with the intended verified user or IAM principal. Only the authorized
  request may perform the operation. See [callable protocol](https://firebase.google.com/docs/functions/callable-reference)
  and [ID-token verification](https://firebase.google.com/docs/auth/admin/verify-id-tokens).

- **REASONED:** No registered Firebase app, provider attestation, or deployed clients was supplied.
  Repeat the permitted owner read separately for Firestore, RTDB, and Storage, and the permitted
  callable invocation, with valid user authentication but no App Check token. Registration
  without enforcement allows otherwise permitted requests; enforcement must reject them.
  The compatible client with valid App Check must still succeed. Allow for documented
  enforcement propagation. Test each used Firebase product from the intended restricted app
  and an excluded app/referrer; intended traffic must work and applicable key restrictions
  must reject excluded traffic. See [App Check enforcement](https://firebase.google.com/docs/app-check/enable-enforcement)
  and [API-key restrictions](https://firebase.google.com/docs/projects/api-keys).

- **REASONED:** No writable emulator fixture or second-host network fixture was supplied.
  On the emulator host, inspect `ss -ltn` and request `GET /emulators` on the local Emulator Hub
  to enumerate actual listeners. In an isolated fixture with Rules configuration omitted,
  attempt an unsigned read/write of a seeded path; repeat after loading the ownership rules.
  Open emulators admit the operation; configured rules must deny the unauthorized operation
  and permit the owner. From another host, attempt connections to every enumerated port:
  listeners exposed on that interface can answer, while the fixed localhost-only deployment
  must not. Inspect proxy and tunnel routes as well. A failed connection without a working
  local positive control is inconclusive. See
  [emulator configuration and Hub API](https://firebase.google.com/docs/emulator-suite/install_and_configure)
  and [localhost binding](https://firebase.google.com/docs/emulator-suite/use_hosting).

### 5. Test account controls, MFA, and key retirement

- **REASONED:** No controlled signup accounts or mailboxes was supplied. Use a signed-out
  Firebase Auth context for EACH Anonymous-provider comparison: explicitly `await signOut(auth)`
  and confirm `auth.currentUser === null` before each `await signInAnonymously(auth)` call,
  including the retry after disabling Anonymous. With Anonymous enabled, require a successful
  result and `getAdditionalUserInfo(result)?.isNewUser === true` to confirm account creation.
  With Anonymous disabled, require rejection of new-account creation due to the disabled
  provider; a network failure is inconclusive. An already signed-in anonymous user can be
  returned without creating an account. This tests signup restrictions, not revocation of
  existing sessions. See the [Auth JS reference](https://firebase.google.com/docs/reference/js/auth),
  [new-user indicator](https://firebase.google.com/docs/reference/js/auth.additionaluserinfo), and
  [session revocation](https://firebase.google.com/docs/auth/admin/manage-sessions).
  Test each other disabled provider.
  For email enumeration protection, compare password-sign-in requests for a nonexistent
  address and a known account with a wrong password; protected sign-in responses must not
  reveal that distinction. Do not expect signup to stop returning `EMAIL_EXISTS`. See
  [anonymous authentication](https://firebase.google.com/docs/auth/web/anonymous-auth) and
  [email enumeration behavior](https://docs.cloud.google.com/identity-platform/docs/admin/email-enumeration-protection).

- **REASONED:** No Supabase signup fixture or invited account was supplied. Attempt
  `supabase.auth.signUp()` with a fresh controlled address and
  `supabase.auth.signInAnonymously()`. Enabled methods can create users; the invite-only and
  anonymous-disabled configuration must refuse those creations while an existing invited
  account can still sign in. See [Auth settings](https://supabase.com/docs/guides/auth/general-configuration),
  [password signup](https://supabase.com/docs/guides/auth/passwords), and
  [anonymous sign-ins](https://supabase.com/docs/guides/auth/auth-anonymous).

- **REASONED:** No MFA-enrolled account was supplied. Repeat the owner's
  `GET /rest/v1/profiles` request with fresh `aal1` and `aal2` sessions. Without the restrictive
  policy, ownership alone permits the read; with it, `aal1` must receive no protected rows and
  `aal2` must receive the owner's seeded row. See
  [MFA enforcement](https://supabase.com/docs/guides/auth/auth-mfa).

- **REASONED:** No API-key inventory, signing-key controls, or disposable backend was supplied.
  Repeat a known successful fixture request using the replaced and replacement API keys.
  Merely creating replacements leaves legacy keys valid; explicit deactivation must invalidate
  legacy-key use while replacement credentials still work. Separately test JWTs signed before
  and after signing-key rotation: rotation alone retains both trust relationships; revocation
  must remove trust in the old signing key after the documented propagation and verifier-cache
  behavior. Keep keys and JWTs in protected files or SDK memory. See
  [API-key migration](https://supabase.com/docs/guides/getting-started/migrating-to-new-api-keys)
  and [JWT signing-key lifecycle](https://supabase.com/docs/guides/auth/signing-keys).

- **REASONED:** No hosted Data API settings or schema fixture was supplied. Repeat a previously
  successful `GET /rest/v1/profiles` request after removing its schema from Exposed schemas,
  or after disabling the unused Data API. It must no longer return the fixture through that
  endpoint. Test retained API schemas separately with authorized positive requests. See
  [Data API controls](https://supabase.com/docs/guides/api/securing-your-api).

### 6. Review the client bundle for privileged credentials

**REASONED:** No deployed client bundle or credential inventory was supplied.
Search the client bundle for possible leaked secrets:
`grep -rlIE 'service_role|eyJ|sb_secret_' dist/` lists only files to inspect, so a full key never
lands in a shared terminal or CI log. Use the guarded form below for the actual bundle path.

Open each flagged file privately and interpret the match rather than expecting none.
A literal `service_role` reference, an `eyJ` substring, or an `sb_secret_` prefix is a **review
candidate**, not proof of a live credential. The public legacy `anon` key is itself a JWT that
legitimately ships in the frontend; new `sb_publishable_...` keys are also intended for clients.
For a complete JWT candidate, decode its payload locally and inspect `role`: `anon` is the
expected legacy public-key role, while a confirmed project `service_role` credential is a leak.
A prefix match alone does not establish that a string is a JWT or a valid key.

A confirmed `sb_secret_...` key, legacy service-role credential, or private key must not be there:
remove the exposure and rotate or revoke the confirmed credential, not just delete it from the
tree. Do not rotate credentials merely because a source-code word matched. See
[API-key handling](https://supabase.com/docs/guides/api/api-keys) and [secrets.md](secrets.md).

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_CLIENT_BUNDLE_DIRECTORY'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not scanning"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not scanning"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute the client bundle directory; not scanning" ;;
    *)
      if grep -rlIE 'service_role|eyJ|sb_secret_' -- "$1"; then
        echo "Review candidates in the files listed above; a match is not proof of a leak."
      else
        case "$?" in
          1) echo "No candidate strings found; encoded or split secrets can evade this scan." ;;
          *) echo "Scan failed; no conclusion." ;;
        esac
      fi ;;
  esac
)
```

For the demonstration, place a harmless marker containing a searched prefix in a disposable
bundle and confirm that its filename is reported; remove it and repeat. A clean result does not
prove the absence of encoded, split, binary, or differently shaped credentials. Inspect build
inputs, source maps, and private-key material separately.

### Demonstration backlog

Both bash blocks passed ShellCheck 0.11.0 and `bash -n` during authoring. Local guard tests refused
embedded `REPLACE_WITH_` placeholders, `example.com`, angle brackets, empty values, and omitted
or shortened `set --` lines. Both URL and header-file placeholder positions were checked.
A ShellCheck canary produced the expected SC2086 finding.

The RTDB JSON, `firebase.json` fragment, Auth TOML, and callable JavaScript passed local parsing
checks. These checks establish syntax and the stated shell behavior only; they do not compile
Firebase Rules, execute SQL policies, or demonstrate service authorization. The replacement
was not installed in the repository, and no whole-corpus gate result is claimed.

| ID | Required exposed/fixed demonstration | Status |
| --- | --- | --- |
| FIREBASE-SUPABASE-LIVE | Demonstrate every REASONED comparison above using disposable Firebase and Supabase projects, controlled A/B accounts and mailboxes, MFA sessions, registered App Check clients, a writable emulator/service fixture, a second host, Storage objects, Realtime clients, view/RPC inventories, an outbound-request collector, a Vault canary, key-lifecycle controls, and the actual client build. Record versions, effective rules/grants/settings, requests, responses, persisted write results, positive controls, propagation intervals, and cleanup. Include all three Firebase Rules engines, Firebase Functions, Supabase Edge Functions (using deployed operation fixtures and caller/webhook credentials to compare JWT verification enabled/disabled, handler authorization, positive controls, persisted effects, and secret hygiene), emulators, API restrictions, signup (including signed-out Anonymous-provider comparisons that confirm new-account creation when enabled and rejection when disabled), Data API removal, views, every function overload, HTTP wrappers, Vault, Storage (including sessionless GET of the same saved download URL before and after Rules tightening and token revocation, with an authorized SDK direct-download positive control), both Realtime authorization paths, MFA, API-key retirement, JWT-signing-key revocation, and bundle-scan controls. | Open; live behavior is reasoned, not demonstrated. |

## Sources (checked September 2026)

- Firebase security rules: https://firebase.google.com/docs/rules
- Supabase API keys (legacy `service_role` is a JWT starting `eyJ`; new `sb_publishable_` and `sb_secret_` keys are short strings): https://supabase.com/docs/guides/api/api-keys
- Supabase row level security: https://supabase.com/docs/guides/database/postgres/row-level-security
- Supabase multi-factor authentication (aal1, aal2, enforcement policy): https://supabase.com/docs/guides/auth/auth-mfa
- PostgreSQL `CREATE VIEW` (base relations checked against the view owner's permissions by default; the view owner's RLS policies applied by default; `security_invoker`): https://www.postgresql.org/docs/current/sql-createview.html
- PostgreSQL `ALTER VIEW` (`SET ( security_invoker = ... )` on an existing view): https://www.postgresql.org/docs/current/sql-alterview.html
- PostgreSQL `REVOKE`: https://www.postgresql.org/docs/current/sql-revoke.html
- Supabase RLS and views (`security_invoker = true` on PostgreSQL 15 and above; revoke or unexpose on older versions; views are typically created by the `postgres` user): https://supabase.com/docs/guides/database/postgres/row-level-security
- PostgreSQL 15 release notes (view accesses "were always treated as being done by the view's owner. That's still the default."): https://www.postgresql.org/docs/release/15.0/
- [Firebase basic rules, ownership examples, and conflicting Storage default prose/example](https://firebase.google.com/docs/rules/basics).
- [Firestore starting modes](https://firebase.google.com/docs/firestore/quickstart).
- [RTDB starting modes and test-rule expiry](https://firebase.google.com/docs/database/web/start).
- [Firebase release notes: month-long test-rule access](https://firebase.google.com/support/releases).
- [Firestore rule structure, recursive wildcards, overlapping grants, and server access](https://firebase.google.com/docs/firestore/security/rules-structure).
- [RTDB rule syntax and cascading](https://firebase.google.com/docs/database/security/core-syntax).
- [Storage rule syntax](https://firebase.google.com/docs/storage/security/core-syntax).
- [Firestore rule testing and deployment](https://firebase.google.com/docs/firestore/security/get-started).
- [Storage rule management](https://firebase.google.com/docs/storage/security/get-started).
- [Second-generation callable handlers](https://firebase.google.com/docs/functions/callable).
- [Callable protocol and optional authentication](https://firebase.google.com/docs/functions/callable-reference).
- [First-generation callable handlers](https://firebase.google.com/docs/functions/1st-gen/callable-1st).
- [Firebase ID-token verification](https://firebase.google.com/docs/auth/admin/verify-id-tokens).
- [Firebase HTTP handlers](https://firebase.google.com/docs/functions/http-events).
- [Second-generation HTTPS invoker options](https://firebase.google.com/docs/reference/functions/2nd-gen/node/firebase-functions.https.httpsoptions).
- [Callable App Check enforcement and SDK requirement](https://firebase.google.com/docs/app-check/cloud-functions).
- [App Check provider registration and client rollout](https://firebase.google.com/docs/app-check/web/recaptcha-enterprise-provider).
- [Per-product App Check enforcement](https://firebase.google.com/docs/app-check/enable-enforcement).
- [Firebase API-key restrictions and required API table](https://firebase.google.com/docs/projects/api-keys).
- [Google Cloud API-key application restrictions](https://docs.cloud.google.com/api-keys/docs/add-restrictions-api-keys).
- [Public Firebase configuration identifiers](https://firebase.google.com/docs/web/learn-more).
- [Firebase anonymous authentication](https://firebase.google.com/docs/auth/web/anonymous-auth).
- [Email enumeration protection, defaults, and remaining signup errors](https://docs.cloud.google.com/identity-platform/docs/admin/email-enumeration-protection).
- [Firebase Emulator Suite configuration, open-rule behavior, and Hub API](https://firebase.google.com/docs/emulator-suite/install_and_configure).
- [Emulator localhost default](https://firebase.google.com/docs/emulator-suite/use_hosting).
- [Supabase Data API security, grants transition, explicit RLS, and API disablement](https://supabase.com/docs/guides/api/securing-your-api).
- [Supabase exposed and custom schemas](https://supabase.com/docs/guides/api/using-custom-schemas).
- [PostgreSQL row-security bypasses and operations outside RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html).
- [PostgreSQL policy syntax and permissive/restrictive policy combination](https://www.postgresql.org/docs/current/sql-createpolicy.html).
- [Supabase API-key migration and legacy-key deactivation](https://supabase.com/docs/guides/getting-started/migrating-to-new-api-keys).
- [Supabase JWT signing-key rotation and revocation](https://supabase.com/docs/guides/auth/signing-keys).
- [Supabase function security and privileges](https://supabase.com/docs/guides/database/functions).
- [PostgreSQL function security and default PUBLIC execution](https://www.postgresql.org/docs/current/sql-createfunction.html).
- [PostgreSQL function settings](https://www.postgresql.org/docs/current/sql-alterfunction.html).
- [PostgreSQL default privileges and global versus schema-specific grants](https://www.postgresql.org/docs/current/sql-alterdefaultprivileges.html).
- [PostgreSQL privilege inquiry functions](https://www.postgresql.org/docs/current/functions-info.html).
- [Supabase HTTP extension](https://supabase.com/docs/guides/database/extensions/http).
- [Supabase pg_net signatures and transaction behavior](https://supabase.com/docs/guides/database/extensions/pg_net).
- [Supabase Vault and its decrypted view](https://supabase.com/docs/guides/database/vault).
- [Supabase Storage bucket access models](https://supabase.com/docs/guides/storage/buckets/fundamentals).
- [Supabase Storage policies and upsert requirements](https://supabase.com/docs/guides/storage/security/access-control).
- [Supabase Storage path helpers](https://supabase.com/docs/guides/storage/schema/helper-functions).
- [Supabase Storage downloads](https://supabase.com/docs/guides/storage/serving/downloads).
- [Supabase Storage uploads](https://supabase.com/docs/guides/storage/uploads/standard-uploads).
- [Supabase Realtime settings and public-channel default](https://supabase.com/docs/guides/realtime/settings).
- [Supabase Broadcast and Presence authorization](https://supabase.com/docs/guides/realtime/authorization).
- [Supabase Postgres Changes security and limitations](https://supabase.com/docs/guides/realtime/postgres-changes).
- [Supabase Auth signup and anonymous-access settings](https://supabase.com/docs/guides/auth/general-configuration).
- [Supabase CLI Auth configuration and defaults](https://supabase.com/docs/guides/local-development/cli/config).
- [Supabase password signup](https://supabase.com/docs/guides/auth/passwords).
- [Supabase anonymous sign-ins](https://supabase.com/docs/guides/auth/auth-anonymous).
- [Supabase TOTP availability and assurance-level transitions](https://supabase.com/docs/guides/auth/auth-mfa/totp).
- [Supabase JavaScript select requests](https://supabase.com/docs/reference/javascript/select).
- [Supabase JavaScript RPC requests](https://supabase.com/docs/reference/javascript/rpc).
- [Supabase Edge Functions overview](https://supabase.com/docs/guides/functions).
- [Supabase Edge Function deployment CLI and JWT-verification flag](https://supabase.com/docs/reference/cli/supabase-functions-deploy).
- [Supabase Edge Function authentication and webhook verification](https://supabase.com/docs/guides/functions/auth).
- [Supabase Edge Function authorization headers, per-function JWT verification, and API-key compatibility](https://supabase.com/docs/guides/functions/auth-headers).
- [Supabase Edge Function secrets and privileged environment credentials](https://supabase.com/docs/guides/functions/secrets).
- [Supabase database Network Restrictions](https://supabase.com/docs/guides/platform/network-restrictions).
- [Supabase Postgres SSL enforcement](https://supabase.com/docs/guides/platform/ssl-enforcement).
- [Supabase database roles and password handling](https://supabase.com/docs/guides/database/postgres/roles).
