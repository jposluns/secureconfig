# Firebase and Supabase: the rules are the security

These platforms handle TLS for you; the exposure works differently. Client SDKs talk to the backend using keys that ship in your frontend code and are **public by design** (the Firebase API key, the Supabase `anon` key). The only server-side gate between the internet and your data is the rules layer: Firebase security rules, or Postgres row-level security (RLS) on Supabase. AI-generated apps repeatedly ship with that layer open because "it worked in testing". On Supabase the gate also depends on how exposed views and functions execute, not only on the table policies.

## Firebase

- Every Firestore, Realtime Database, and Storage instance needs explicit security rules. Never deploy the all-open rule (`allow read, write: if true;` or `".read": true, ".write": true`); it exposes the entire datastore to anyone with your public config.
- Require authentication and scope by user:

```
// Firestore example
match /users/{userId}/{document=**} {
  allow read, write: if request.auth != null && request.auth.uid == userId;
}
```

- New projects start in locked mode; keep production locked-by-default and open specific paths deliberately. Test with the Rules Playground and emulator before deploying.
- Server-side credentials (service accounts for the Admin SDK) bypass rules entirely; they stay on servers only, handled per [secrets.md](secrets.md).

## Supabase

- Enable RLS on **every** table exposed through the API, then write policies; a table without RLS is readable and writable with the public `anon` key:

```sql
alter table profiles enable row level security;

create policy "own rows"
on profiles for select
using ( auth.uid() = user_id );
```

Write separate policies per operation (`select`, `insert`, `update`, `delete`); no policy means no access once RLS is on, which is the correct starting point.
- The `service_role` key bypasses RLS; it is a server-only secret that must never reach the client bundle or the repository.
- A view runs with **its owner's** privileges by default, and applies the owner's row-level security policies rather than the caller's. On Supabase a view is typically created by the `postgres` user, so a view over an RLS-protected table serves that table's rows to anyone holding the `anon` key. On PostgreSQL 15 and later, make every API-exposed view apply the caller's policies instead:

```sql
alter view public.REPLACE_WITH_VIEW_NAME set (security_invoker = true);
```

  On PostgreSQL 14 and earlier there is no `security_invoker`: revoke the view from `anon` and `authenticated`, or keep it in a schema the API does not expose.

- A `SECURITY DEFINER` function likewise runs as its owner and can return rows RLS would hide. Keep such functions out of API-exposed schemas unless they enforce their own authorization, and revoke execution by default:

```sql
revoke execute on function public.REPLACE_WITH_FUNCTION_NAME from public, anon, authenticated;
```

Include the argument types where the function name is overloaded.
- Supabase Auth supports MFA (TOTP on every plan). Enrolment alone changes nothing: enforce it in your policies by requiring the `aal2` assurance level, so a session that has not completed the second factor cannot read protected rows ([mfa.md](mfa.md) for the general rules):

```sql
create policy "mfa required"
on profiles as restrictive
to authenticated
using ((select auth.jwt()->>'aal') = 'aal2');
```

## Verify

- With only the public key (no signed-in user), API reads and writes against protected tables/paths fail.
- Signed in as user A, reading user B's rows fails.
- Reads through every API-exposed view fail the same way as reads of the table behind it: request `/rest/v1/REPLACE_WITH_VIEW_NAME` with only the public key, then, signed in as user A, request user B's rows. A view that returns them is serving rows the table's policies withhold; check whether it runs with its owner's rights or whether a policy is simply too broad.
- Every API-exposed function is checked the same way, because the view check cannot see it: call `/rest/v1/rpc/REPLACE_WITH_FUNCTION_NAME` with only the public key, and again signed in as user A for user B's rows. A `SECURITY DEFINER` function returns rows while the table and view checks both look clean, so this is the only step that catches it. Repeat for every overload.
- Search the client bundle for `service_role` and private keys; the result must be empty.

## Sources (checked September 2026)

- Firebase security rules: https://firebase.google.com/docs/rules
- Supabase row level security: https://supabase.com/docs/guides/database/postgres/row-level-security
- Supabase multi-factor authentication (aal1, aal2, enforcement policy): https://supabase.com/docs/guides/auth/auth-mfa
- PostgreSQL `CREATE VIEW` (base relations checked against the view owner's permissions by default; the view owner's RLS policies applied by default; `security_invoker`): https://www.postgresql.org/docs/current/sql-createview.html
- PostgreSQL `ALTER VIEW` (`SET ( security_invoker = ... )` on an existing view): https://www.postgresql.org/docs/current/sql-alterview.html
- PostgreSQL `REVOKE`: https://www.postgresql.org/docs/current/sql-revoke.html
- Supabase RLS and views (`security_invoker = true` on PostgreSQL 15 and above; revoke or unexpose on older versions; views are typically created by the `postgres` user): https://supabase.com/docs/guides/database/postgres/row-level-security
- PostgreSQL 15 release notes (view accesses "were always treated as being done by the view's owner. That's still the default."): https://www.postgresql.org/docs/release/15.0/
