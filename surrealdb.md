# SurrealDB: authentication and TLS

SurrealDB is a database server where apps store and query data. This guide helps your AI assistant configure it securely, including release 2.0 or later with authentication on and a root user, a private bind (its Docker images listen on every interface), scoped users, limited query capabilities, and TLS.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/surrealdb.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against SurrealDB server and image v4.0.0, SurrealDB 3.x server v3.3.5, SurrealDB native AUDIENCE minimum 3.3, SurrealDB SCOPE deprecation 2.x, SurrealDB SCOPE removal 3.0, GNU Bash reference manual bash-5.3, Linux procfs manual man-pages-6.19, and Linux ptrace manual man-pages-6.19; 3 further sources carry no recorded version. Metadata reviewed 2026-11-05; documentation checked September 2026. The guide records 45 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

Since SurrealDB 2.0.0, authentication is enabled by default and the CLI binds `127.0.0.1:8000` rather than
`0.0.0.0` (2.0.0 removed the old `--auth` flag, added `--unauthenticated`, and changed the bind default);
on older releases neither held, so pin your version. Even on a current version, a laptop demo becomes a real
exposure the moment the same command runs on a routable server with `--unauthenticated` or a widened bind
carried over.

This guide covers SurrealDB v4.0.0 and, where the two differ, v3.3.5, the last 3.x release (commit 5c3383fe).
Where a statement cites only v4.0.0 source, the v3.3.5 source read for this guide supports it too, unless the text
says otherwise. Statements that rest only on the rolling documentation, which as served on 2026-11-04 describes 4.0, are not
established at v3.3.5. The v3.3.5 release record's body is only "Release v3.3.5", so what v3.3.5 changed is not established either.

## 1. Root user and authenticated mode

At v4.0.0, two different programs answer to `surreal`. The database executable defines a `start` command and
no `db` command, so it takes `surreal start`. The Surreal CLI launcher, which the vendor's install script
installs as `surreal` with, by default, the database as a pinned component, takes `surreal db start` and passes everything
after the component name to the database unchanged. The launcher's pages document no bare `surreal start`, and
say "A name that is not a component, such as `surreal foo`, runs a `surreal-foo` from your `PATH` if one exists,
and reports an unknown component otherwise." As this guide's inference, under the launcher `surreal start`
does not start the database, and could pass the block's environment to a `surreal-start` found on `PATH`.
So the block below uses `surreal db start`, for the documented launcher install; where the standalone database
executable is installed as `surreal`, drop `db`. The container example in section 2 keeps `start`, because in the
`dev` and `prod` stages of the repository's `docker/Dockerfile` the `ENTRYPOINT` runs `/surreal`, by default
copied from `target/release/surreal`, which as this guide reads it is the database executable. The `dev-ci` and `prod-ci`
stages copy a prebuilt CI artifact instead, whose origin is not established at v4.0.0.
Which program the vendor's install script put on `PATH` as `surreal` for 3.x releases is not established, so
whether a v3.3.5 install takes `surreal start` or `surreal db start` is not established either.

`surreal db start` takes `--user`/`-u` and `--pass`/`-p` (also `SURREAL_USER`/`SURREAL_PASS`) for, in the
v4.0.0 help text, "the initial database root user. Only if no other root user exists": they initialize that
user when none exists, and do not disable authentication or rotate an existing root password. At v4.0.0 both
flags refuse an empty value (`value_parser = clap::builder::NonEmptyStringValueParser::new()`), and the server
core refuses an empty or whitespace-only username or password before it creates the user
(`!user.trim().is_empty() && !pass.trim().is_empty()`). Whether an empty `SURREAL_PASS` in the environment
reaches those checks or counts as unset is not established at v4.0.0; the block refuses an empty password itself.
At v3.3.5 neither check is in the cited code. Its `--user` and `--pass` arguments end with `requires = "password"`
and `requires = "username"`, with no `value_parser`, and its core `initialise_credentials` goes straight to
`Self::retry("Initialise credentials", || self.initialise_credentials_attempt(user, pass))` with no `ensure!`.
Whether v3.3.5 refuses an empty value elsewhere, in the user definition it then computes or in clap's handling of
an empty environment variable, is not established; the block's own check refuses an empty password on either release.
A root user can also come from the SurrealQL file that `--import-file` (`SURREAL_IMPORT_FILE`) runs at start:
the server runs that import first, "so that an import which supplies root users suppresses creation of the CLI
bootstrap user", so treat such a file as a credential.

At v4.0.0, `--help` no longer prints credential values: the password argument sets `hide_env_values = true`,
and the executable applies `arg.hide_env_values(true)` to every argument of every command. Before 4.0.0 it
could: GHSA-whfh-76h8-2r66, "CLI help output prints the values of SURREAL_PASS and SURREAL_TOKEN" (low;
affected `< 4.0.0`, patched `4.0.0`), names `surreal start` among the commands and was reproduced on v3.2.4.
At v3.3.5 the password argument sets no `hide_env_values` (its attributes are `env = "SURREAL_PASS"`, `short = 'p'`,
`long = "password"`, `visible_alias = "pass"` and `requires = "username"`), and no v3.3.5 file read for this guide
calls `hide_env_values`. v3.3.5 is inside that advisory's affected range, though the advisory's reproductions name
images up to `v3.3.4` and not v3.3.5. As this guide's advice, on v3.3.5 never run `--help` in a shell where
`SURREAL_PASS` or `SURREAL_TOKEN` is set.

Pass the password through the environment, never argv (which reaches `ps` and shell history). `surreal db start`
has no stdin input for it (none in the v4.0.0 server files read for this guide), so the block prompts for it and
hands it to that one command as a prefix assignment.
Bash 5.3 says that assignment affects only the command's environment; ensure the password is never exported from the shell:

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  { unset -n pw SURREAL_USER SURREAL_PASS && unset -v pw SURREAL_USER SURREAL_PASS; } 2>/dev/null ||
    { echo 'cannot clear pw, SURREAL_USER or SURREAL_PASS in this shell; not starting'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not starting'; exit 2; }
  set -- "${!SURREAL_@}"
  [ "$#" -eq 0 ] || { printf 'SURREAL_* variables set in this shell:'; printf ' %s' "$@"; printf '; unset them first; not starting\n'; exit 2; }
  IFS= read -r -s -p 'Initial root password: ' pw < /dev/tty || exit 2
  printf '\n'
  [ -n "$pw" ] || exit 2
  SURREAL_USER=root SURREAL_PASS="$pw" surreal db start surrealkv:/data/mydb.db --bind 127.0.0.1:8000
)
```

This moves the password out of argv, not out of reach: `/proc/<pid>/environ` contains the initial environment
set at `execve` and does not reflect later changes to the process environment. Reading it is governed by a
`PTRACE_MODE_READ_FSCREDS` check that depends on factors such as the credentials and capabilities of the two processes, dumpability and Linux Security Modules.
As this guide's assessment, the same account or root may read the initial value when that check permits, and a
process inheriting the environment may receive it and expose it the same way for as long as that process runs. Treat it as exposed to that account and to root while the server runs.
Under the launcher, Bash starts the launcher with that environment. Whether the launcher replaces itself with the
database or stays running as its parent, and whether it passes `SURREAL_PASS` on unchanged, is not established
at v4.0.0: its pages say variables that start with `SURREAL_` and not `SURREAL_CLI_` "belong to the database, and
the launcher never reads them", without saying how they reach it. As this guide's assessment, treat a resident
launcher as exposed the same way, and confirm that the root user was created by signing in with it.
Paste the password alone at the hidden prompt: a multi-line paste leaves every line after the first for
your shell to run.

The block clears `SURREAL_USER` and `SURREAL_PASS` itself, then refuses to start while any other `SURREAL_*` variable is set in the calling shell, naming each. The database reads many of its options from such variables, including `SURREAL_UNAUTHENTICATED` and `SURREAL_BIND`, so an inherited one would start the server differently from what the block shows. The check also refuses the launcher's own `SURREAL_CLI_*` variables, which its pages separate from the database's. Unset them, or start from a clean shell.

v4.0.0 removes the RocksDB engine. The start page as served says the `rocksdb://` and `indxdb://` schemes "are kept as deprecated spellings of `surrealkv://`", so the block names `surrealkv:/data/mydb.db`, which that page reads as an absolute path. The server's own path check is in a crate this guide has not read, so how v4.0.0 handles a `rocksdb:` path is not established here.

v3.3.5 differs. Its core's datastore factory comment gives `"memory",` and then `"rocksdb:...", "tikv:..."` as
examples of the connection strings an implementation may interpret, and the 3.3 release page says a 3.3 feature is
"Supported on every storage backend: in-memory, RocksDB, SurrealKV, IndexedDB and TiKV". Its core also documents
`Datastore::new("rocksdb://database.db")` as a usage example, and its server has a test, compiled only with the
`storage-rocksdb` feature (`#[cfg(feature = "storage-rocksdb")]`), that builds a `rocksdb:` path
(`format!("rocksdb:{}", dir.path().join("store").display())`). As this guide's inference from these, RocksDB is a
working engine at v3.3.5; they show code for it, not that a v3.3.5 release build includes it. How v3.3.5 parses a path scheme, and whether it reads the block's `surrealkv:/data/mydb.db` as an absolute path, is
not established: its path parser was not read, and the start page as served describes 4.0.

At v4.0.0 a directory a 3.x release wrote is refused unless the operator opts in. The error in the source says the in-place upgrade "is experimental and is refused by default", that "a 3.x release cannot open them afterwards", and to "take a backup and set SURREAL_EXPERIMENTAL_UPGRADE_FROM_3X=true to opt in to the experimental upgrade". This guide gives only that `true` value; which other values the server accepts is not established at v4.0.0.
The refusal is v4.0.0's: v3.3.5's `kvs-surrealkv/src/lib.rs` contains no `SURREAL_EXPERIMENTAL_UPGRADE_FROM_3X`
text, so as this guide's inference the opt-in does not apply to a v3.3.5 server.

The block cannot carry that opt-in: set in the calling shell, it is a `SURREAL_*` variable, and the block refuses to start. As this guide's advice, convert a 3.x directory as its own deliberate step after a backup, and run this block on a directory that v4.0.0 wrote or on a new one.

The `--unauthenticated` flag (`SURREAL_UNAUTHENTICATED`) allows unauthenticated access instead; a
guest connecting under it gets permissions equivalent to the `OWNER` role. Do not run it, or carry it
from a local demo, on anything reachable beyond your own machine.

## 2. Bind privately

`--bind`/`-b` (`SURREAL_BIND`) sets the listening address and defaults to `127.0.0.1:8000` (as of v4.0.0),
loopback only. The images built from the repository's `docker/Dockerfile` do not keep that default: each of its
runtime stages sets `SURREAL_BIND=0.0.0.0:8000` and none sets a `CMD`, so a container run with `start` and no
`--bind` or `SURREAL_BIND` of its own listens on every IPv4 interface inside the container. That is safe only while the host side
stays private: publish it on host loopback (`127.0.0.1:8000:8000`) or attach it to a private network only.
Whether the published images are built from that file is not established at v4.0.0. On a
host, widen the bind deliberately, and only to a private address, for example `--bind 10.0.0.5:8000`; never
bind an unauthenticated or root-only instance to `0.0.0.0`. SurrealDB's own security guidance says
that if the database should only be reachable by other internal services, "expose SurrealDB
exclusively to the internal network instead of deploying the service with a publicly addressable
network interface."

## 3. User levels and access control

System users (`DEFINE USER`) exist at three levels: root, namespace, and database. The `DEFINE USER` page says
"Note that even a root-level user can be given a limited role such as `VIEWER`. This can be useful for automated
services that need to monitor each namespace and database, or for colleagues in non-technical roles." The JWT page
says, of root tokens, "Root tokens can be used to select, create,
update, and delete on all tables in all databases of all namespaces, as well as to define and remove namespaces and
databases from the SurrealDB instance." As this guide's inference from those sentences, a root system user reaches
every namespace and database, within what its role allows. The best-practices page says system users may be assigned "roles that will
limit the actions they can perform inside the level where they are defined", with `ROLES VIEWER` and
`ROLES EDITOR` examples, and the start page says the start credentials "define a new root user with the `OWNER`
role". The `DEFINE USER` page says "Currently, only the built-in roles OWNER, EDITOR and VIEWER are available."
Whether every system user holds one is not established by the pages read for this guide. The docs warn plainly that "a root system user is not
restricted by permissions at all, so it is the wrong
credential to put in an application"; give trusted backend administration a narrowly scoped system user. But
system users at EVERY level are governed by RBAC and bypass table and field `PERMISSIONS` entirely, so a
namespace- or database-level system user is not a substitute for record-level isolation: when application
users need database-enforced row or field permissions, use record users (below), not a system user.

Record users are different: they are rows in your own tables, authenticated through
`DEFINE ACCESS ... TYPE RECORD` with custom `SIGNUP` and `SIGNIN` logic. Record users get no access
beyond what a `PERMISSIONS` clause on a table or field grants them, the same
rules-are-the-security model as Firebase and Supabase ([firebase-supabase.md](firebase-supabase.md)):
the permissions page says "omitting `PERMISSIONS` results in a `PERMISSIONS NONE`", so a table with no
`PERMISSIONS` clause grants a record user nothing by default. Fields default the other way: "A field without an
explicit clause is stored as `PERMISSIONS FULL`", which follows the table's rules, so give a sensitive field,
such as a password hash, its own clause. The `/signup` and `/signin`
HTTP endpoints accept unauthenticated credentials by design. At v4.0.0 so do `/signup/cookie` and
`/signin/cookie`, which `--cookie-auth` with an explicit `--allow-origin` list enables, and scoped paths such as
`/ns/{ns}/db/{db}/ac/{ac}/signup`, which the server rewrites to the unscoped route before any layer sees them.
At v3.3.5 the sign-in and sign-up routers register only `.route("/signin", options(|| async {}).post(handler))`
and `.route("/signup", options(|| async {}).post(handler))`, and there is no `ntw/scope.rs`, so the cookie routes
and scoped paths are not in the v3.3.5 files read. Whether another v3.3.5 file registers them is not established.
A `SIGNUP` clause can permit public self-registration that root credentials do not restrict, so omit `SIGNUP`
when self-registration is unwanted and test that it is refused while a provisioned account still signs in.
At v4.0.0 every HTTP signup form calls the same core function, which refuses an access method with no `SIGNUP`
(`bail!(AuthError::AccessRecordNoSignup)`). The v3.3.5 `/signup` handler calls the same core function
(`surrealdb_core::iam::signup::signup(kvs, &mut session, vars.into())`), whose check is the same at both releases.
Whether RPC `signup` reaches that check was not traced at v4.0.0 or v3.3.5,
so where `/rpc` is allowed, test the refusal there too.

At v4.0.0 the per-address limit on sign-in and sign-up requests, and on requests carrying Basic credentials, is
off by default: `lazy_env_parse!("SURREAL_HTTP_AUTH_RATE_LIMIT_ENABLED", bool, false)`. The 4.0 release page
says "Basic authentication is rate-limited", which as this guide reads the source holds only once the limiter is
enabled. Its burst and per-minute rate then default to 60, and a request with no client address the server can
work out is not limited. Which values enable it is not established at v4.0.0.
At v3.3.5 the setting and its defaults are the same, but the limiter covers less: it admits any request that is not
`POST` untouched (`if request.method() != Method::POST {`) and limits only `"/signin"` and `"/signup"`, whatever
headers they carry, with no cookie, refresh or sign-out path. It lacks v4.0.0's header case, which also limits any
other request that carries Basic credentials (`} else if has_basic_auth(request) {`). As this guide's reading of the
v3.3.5 source, with the limiter enabled a `POST` to `/signin` or `/signup` with a client address the server can work
out is limited whether or not it carries Basic credentials, and any other request that carries them is not. A request
with no such address is not limited (`let Some(key) = request_key(request) else {`).

v4.0.0 fixes these advisories on table, field and role controls, each affecting versions below 4.0.0 and
patched in 4.0.0, so do not rely on those controls on an earlier release:

- GHSA-5xcv-fm6g-4hf3 (high): "Quoted Computed-Field Formatter Bypasses Field-Level SELECT Permissions".
- GHSA-fh2q-8f75-m4h6 (high): "REFERENCE ON DELETE CASCADE/UNSET/CUSTOM bypasses target table PERMISSIONS FOR delete/update".
- GHSA-qh3v-rr48-x3cq (medium): "Authenticated Export Permission Bypass".
- GHSA-ffvm-mqh3-7986 (medium): "SurrealDB 3.2.4 allows FOR loop variables named $access, $auth, and $token to shadow the authenticated session values used by table permission expressions." Its advisory record gives the severity as "medium", while the 4.0 release page lists it as "High".
- GHSA-wjh3-m4pv-q6cp (medium): "Cross-field array-index drift in wildcard field-permission filtering".
- GHSA-cff7-q66j-4hc8 (medium): "UNIQUE-Index Conflict Errors Disclose SELECT-Restricted Field Values and Record Ids in SurrealDB".
- GHSA-3rcm-c653-wgmr (medium): "Re-RELATE on an Existing Edge Echoes Stored in/out Endpoints Despite SELECT Restrictions in SurrealDB".
- GHSA-ff2q-h4x7-cpj4 (medium): "ON DELETE REJECT Errors Disclose SELECT-Hidden Referencing Record Ids in SurrealDB".
- GHSA-pvv9-h693-m8r4 (medium): "SurrealDB LIVE query notification expressions allow write side effects that bypass the write-blocking guard"; its description says write side effects in the WHERE clause that reference document fields "can exfiltrate data even after the subscriber's SELECT permission is revoked".
- GHSA-m887-2246-mgw3 (low): "VIEWER role can define tables implicitly via CREATE on a non-STRICT database".
- GHSA-3287-hpm5-3f8r (medium): "SurrealDB DDL statements bypass namespace/database implicit-creation authorization added by GHSA-wp87-mgvq-5j93 fix".

Use `DEFINE ACCESS ... TYPE RECORD`;
the legacy `DEFINE SCOPE` is deprecated in 2.x and removed in 3.0. `DEFINE ACCESS`
also supports `TYPE JWT` and `TYPE BEARER` (per-client keys). Mind the authorization boundary: a standalone
`TYPE JWT` access grants SYSTEM-level sessions governed by its scope and roles, above table and field
permissions, whereas application users who need those permissions want `DEFINE ACCESS ... ON DATABASE TYPE
RECORD WITH JWT`. Trusting an IdP's tokens is more than a valid signature: enforce the expected issuer and
audience (native `AUDIENCE` is available since 3.3.0, so set it at this guide's v4.0.0 basis; check the issuer
in an `AUTHENTICATE` clause, as the JWT page's example does), set the
verification algorithm and key or JWKS URL, and test expired, wrong-issuer, and wrong-audience tokens against
a valid-token control.

## 4. Capabilities: what an authorized query may do

Authentication decides who connects; capabilities decide what a query may then reach, and it is a separate
control. `--allow-all` and `--deny-all` default off; network access is denied by default, functions are
allowed by default, and scripting (`--allow-scripting`) and guest access (`--allow-guests`) default off. These
defaults come from the capabilities page as served, which describes 4.0 ("Before 4.0, a target such as
`*.example.com` was read as an exact host name"), so at v3.3.5 they are not established. The
capabilities page says "the more specific capabilities prevail over the less specific" and that at the same level
of specificity denies prevail. As this guide's reading of the v4.0.0 source, that holds between layers: a
category's allow list overrides `--deny-all` or a bare category deny. It does not hold between list entries: a
function is allowed only when an allow entry matches it and no deny entry does
(`self.allow_funcs.matches(target) && !self.deny_funcs.matches(target)`), so allowing `http::get` while denying
`http` refuses `http::get`. The capabilities page's own example agrees: under `--deny-funcs crypto
--allow-funcs crypto::md5`, "all four are denied, because a specific deny wins over any allow."

Prefer `--deny-all` with narrow explicit allowances for the routes, RPC methods, and functions you need rather
than a bare `--allow-funcs` or `--allow-net`, keep embedded scripting off unless required, and confirm each
default against your pinned version. As this guide's reading of the v4.0.0 source, `--deny-all` alone leaves
every HTTP route, RPC method and MCP tool allowed by capabilities. `--allow-http`, `--allow-rpc` and `--allow-mcp`
each default to an empty value (`#[arg(default_value_os = "")]`), their parsers read it as every target
(`Ok(Targets::All)`), and under `--deny-all` each allow getter returns `Targets::All` for that list, while each
deny getter denies nothing unless you name targets in its list. That runtime result is not established by a
run. So pass explicit `--allow-http` and `--allow-rpc` lists of the routes and RPC
methods you use, giving routes by name without a slash, such as `health`, `signin`, `signup` and `sql`. The
HTTP protocol page says a denied `health` route answers `403`, which the Verify block's health check reports
as inconclusive. So when the Verify block's health check should pass, include `health` in the `--allow-http`
list. Under `--deny-all` the HTTP allow getter returns a named list as given (`return targets.clone();`),
the route parser reads the name as `"health" => Ok(RouteTarget::Health),`, and `/health` refuses a route that is not
allowed: `return Err(NetError::ForbiddenRoute(RouteTarget::Health.to_string()));`.

GHSA-cr79-9p8r-p5wx (high; affected `< 4.0.0`, patched `4.0.0`), "MCP Tool Identifier Validation Permits Statement
Injection via Escaped Backticks", bears on MCP tools staying allowed: its impact reads "Arbitrary SQL query execution
through MCP tool invocation, bypassing tool argument constraints." Its patch note says "Version 4.0.0 and later are
not affected by this issue."

The v3.3.5 capability files read for this guide, `server/src/dbs/mod.rs` and `rpc/src/capabilities/mod.rs`, have no
MCP-tool lists. v3.3.5's capability arguments define `allow_rpc` and `allow_http` with the same
`#[arg(default_value_os = "")]` default, and neither file defines an `allow_mcp` or `deny_mcp` argument. Their only
MCP capability target is the HTTP route, `"mcp" => Ok(RouteTarget::Mcp),`. v3.3.5 also defines a `surreal mcp`
command, `Mcp(McpCommandArguments)`, to "Start the MCP server over stdio for AI assistant integration", behind
`#[cfg(feature = "mcp")]`. Its arguments type, `McpCommandArguments`, is named through the `cli::mcp` module
(`use mcp::McpCommandArguments;` at `cli/mod.rs` line 38), whose file, `cli/mcp.rs` or `cli/mcp/mod.rs`, was not
read. Whether anything else gates MCP tools at v3.3.5 is not established, because neither that module nor its
MCP crate was read.

v4.0.0 also fixes these capability bypasses, each affecting versions below 4.0.0 and patched in 4.0.0:

- GHSA-5w6j-qm42-4rc2 (high): "JavaScript Built-in Bridge Bypasses Function Capability Enforcement".
- GHSA-fq69-wr4w-v3gm (high): "JavaScript Query Bridge Bypasses Arbitrary-Query Subject Gate".
- GHSA-q83r-f38r-rwvj (high): "Surrealism WASI socket allowlist ignores deny_net, enabling SSRF via hostname resolving to a private IP".

The 4.0 release page lists 23 advisories and says "Each affected `v3.3.5` and earlier, and each fix ships in
`v4.0.0` and is enabled by default." Each of the 23 advisory records gives the affected range `< 4.0.0` and the
patched version `4.0.0`, so v3.3.5 falls inside all 23 published affected ranges. Whether a given v3.3.5 server
is exposed to each depends on that advisory's own prerequisites, such as a feature, platform, route or privilege it
names. This guide names 16 above as bearing on its statements. The other 7 are GHSA-p3c2-wh5f-jwqm,
GHSA-cph5-pm57-9w9c, GHSA-7pqw-x84x-frxc, GHSA-6c37-x4jm-529x, GHSA-7r2m-g5wf-pj9j, GHSA-623g-mhxq-5hmf and
GHSA-m9qr-4rcq-3jhc, on GraphQL WebSockets, bucket storage paths, the model export route, events in interactive
transactions and a dependency. GHSA-q83r-f38r-rwvj gives its prerequisites: "the experimental `surrealism` capability
is enabled; the attacker is authenticated with enough privilege to upload a `.surli` module to a bucket and invoke it;
and the operator relies on `deny_net` (with a broad or attacker-influenceable `allow_net`) for egress control".
GHSA-m9qr-4rcq-3jhc says its reproduction exercises `reblessive`'s public API directly and "It is not remote/black-box
triggerable." GHSA-q83r-f38r-rwvj and GHSA-m9qr-4rcq-3jhc are filed against the `surrealdb-core`
crate and the other 21 against `surrealdb`; reading those crate versions as server releases is this guide's inference.

Functions such as `http::*` and JWKS retrieval make outbound requests, so restrict destinations and
apply the metadata and internal-network protections in [egress-metadata.md](egress-metadata.md); authentication
alone does not prevent SSRF.

## 5. TLS

`--web-crt` and `--web-key` serve SurrealDB's own interfaces over HTTPS directly. SurrealDB's own
guidance also endorses delegating TLS termination to a load balancer or reverse proxy, per
[nginx.md](nginx.md) or [caddy.md](caddy.md). Reaching the instance only over a tailnet
([tailscale.md](tailscale.md)) is this guide's own suggestion, not one on SurrealDB's pages. Whether SurrealDB
v4.0.0 has a native second factor is not established here, because none of the pages read for this guide
addresses one. Require MFA at the identity provider
(for JWT access) or at an administrative access gateway per [mfa.md](mfa.md), and make sure direct-origin
access cannot bypass that gateway.

## Verify

```bash
# REASONED: expected server outcomes follow the cited SurrealDB documentation; no SurrealDB runtime is
# available in the authoring environment. A redirect, missing database, disabled route, proxy rejection, TLS or transport failure is
# inconclusive, never a pass.
# Run this block on the SurrealDB host: its listener inventory and health check read that host. It exits 2 if a
# check refuses its input, 3 if the JWT prompt, ss, the health check or either query fails or the health check
# does not answer 200, otherwise 2 if ss is not installed, and otherwise 0; the listener list, when ss ran, and
# the two query responses stay for you to judge.
# Auth discrimination: INFO FOR DB; with no credentials vs with a valid system-user JWT, same NS/DB and
# endpoint. Substitute inside the quotes and paste the whole block; run first against the direct origin, then
# the actual HTTPS endpoint.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set -o pipefail
  { unset -n probe_jwt && unset -v probe_jwt; } 2>/dev/null ||
    { echo 'a readonly probe_jwt is set in this shell; not probing'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not probing'; exit 2; }
  set -- PASTE_WHOLE_BLOCK 'http://127.0.0.1:8000' 'REPLACE_WITH_NAMESPACE' 'REPLACE_WITH_DATABASE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 3 ] || { echo 'need endpoint, namespace and database; not probing'; exit 2; }
  case "$1|$2|$3" in *REPLACE_WITH_*) echo 'replace all placeholders; not probing'; exit 2 ;; esac
  { [ -n "$1" ] && [ -n "$2" ] && [ -n "$3" ]; } || { echo 'empty value; not probing'; exit 2; }
  case "$1" in http://127.0.0.1:8000|https://?*) ;; *) echo 'use local loopback HTTP or HTTPS; not probing'; exit 2 ;; esac
  if IFS= read -r -s -p 'Short-lived system-user JWT: ' probe_jwt; then
    printf '\n'
  else
    printf '\n'; echo 'secret input failed; not probing'; exit 3   # every check above passed, so the failed prompt is inconclusive
  fi
  [[ "$probe_jwt" =~ ^[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-]+$ ]] || { echo 'missing or malformed JWT; not probing'; exit 2; }
  set -- "$1" "$2" "$3" 0               # the 4th value is the block's status so far: 3 (inconclusive) outranks 2 (ss is not installed), which outranks 0
  if command -v ss >/dev/null; then
    ss -tlnp || { echo "ss -tlnp exit $?: the listener inventory failed; inconclusive"; set -- "$1" "$2" "$3" 3; }   # inventory, on the host: 8000 on loopback or a private address, never 0.0.0.0
    set -- "$1" "$2" "$3" "$4" listed   # the 5th value says whether ss ran, so the last line names the listener list only when it did
  else
    echo "ss is not installed here; not listing sockets"
    case "$4" in 0) set -- "$1" "$2" "$3" 2 ;; esac
    set -- "$1" "$2" "$3" "$4" unlisted
  fi
  # guard-conventions: allow fixed loopback health URL http://127.0.0.1:8000/health; no reader-substituted target
  set -- "$1" "$2" "$3" "$4" "$5" "$(if curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -o /dev/null -w 'health=%{http_code}\n' http://127.0.0.1:8000/health; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "$3" "$4" "$5" "${6##*$'\n'}" "${6%$'\n'*}"   # curl's exit status, then its health= line
  printf '%s' "$7"                      # /health answered (not an auth check)
  case "$6:$7" in
    0:health=200*) ;;
    0:*) echo "the health check did not answer 200; inconclusive"; set -- "$1" "$2" "$3" 3 "$5" ;;
    *) echo "curl exit $6: the health check failed; inconclusive"; set -- "$1" "$2" "$3" 3 "$5" ;;
  esac
  set -- "$4" "$5" -sS --noproxy '*' --connect-timeout 5 --max-time 20 --header 'Accept: application/json' \
    --header "Surreal-NS: $2" --header "Surreal-DB: $3" --data-binary 'INFO FOR DB;' --url "${1%/}/sql" \
    --write-out '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n'   # the block's status so far, whether ss ran, then curl's arguments
  echo UNAUTHENTICATED
  curl -q -g "${@:3}" </dev/null || { echo "curl exit $?: the unauthenticated query failed; inconclusive"; set -- 3 "${@:2}"; }
  echo AUTHENTICATED
  printf 'Authorization: Bearer %s\n' "$probe_jwt" | curl -q -g "${@:3}" --header @- || { echo "curl exit $?: the authenticated query failed; inconclusive"; set -- 3 "${@:2}"; }
  case "$2" in
    listed) echo "block exit $1; the listener list and the two INFO FOR DB responses are not classified, so judge them against the comments" ;;
    *) echo "block exit $1; the two INFO FOR DB responses are not classified, so judge them against the comments" ;;
  esac
  exit "$1"
)
# Exposed (auth disabled + /sql enabled): the unauthenticated query returns DB info. Fixed: unauthenticated is
# rejected with an identifiable authorization error and the authenticated request returns an OK result with DB
# info. Both failing, only a proxy tested, an unrelated response, or a TLS/transport failure is inconclusive;
# HTTP 200 alone is insufficient. This tests unauthorized DB-info access, not record permissions.
```

```bash
# Origin reachability from an UNTRUSTED network - ANY HTTP answer proves the origin is reachable (a finding):
# no other result passes, because a refusal, timeout, TLS or transport failure is inconclusive, so this block
# exits 1 or 3, never 0, and 2 if it refuses its input.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PUBLIC_ORIGIN_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'one URL required; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*) echo 'substitute the origin URL; not probing'; exit 2 ;; esac
  set -- "$1" "$(if curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 -o /dev/null \
    -w 'origin http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' --url "$1"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "${2##*$'\n'}" "${2%$'\n'*}"     # curl's exit status, then its origin line
  printf '%s' "$3"
  case "$3" in
    'origin http=000 '*) echo "no HTTP answer (curl exit $2): a refusal, timeout, TLS or transport failure is inconclusive, never a pass"; set -- 3 ;;
    'origin http='*) echo "FINDING: the origin gave an HTTP answer, so it is reachable from this network"; set -- 1 ;;
    *) echo "curl exit $2 printed no origin line; inconclusive"; set -- 3 ;;
  esac
  echo "block exit $1; this block classifies its one request and leaves nothing else to judge"
  exit "$1"
)
```

REASONED: preceding block; public-origin reachability and TLS interpretation follow the cited SurrealDB bind and TLS documentation; no external test path or deployment certificate is available in the authoring environment, so no reachability result is recorded.
The first block's listener inventory, health check and anonymous/authenticated database-info queries are declared by its own leading comment and follow the cited SurrealDB bind, health and SQL/authentication documentation; no running deployment or system-user JWT is available for them.
At v4.0.0 the source says `/health` returns `200` unless its route is denied, the memory guard has stayed
engaged for at least the configured `SURREAL_MEMORY_THRESHOLD_UNHEALTHY_AFTER` period, or the storage backend
fails its health check. So a `200` can come while the guard is engaged, for less than that period or with that
memory check disabled, and it shows neither authentication nor finished startup. `/status` is the process and
listener liveness check, and `/ready` returns `200` only once startup, import and credentials included, has
finished and, when a heartbeat budget is configured, the node's cluster heartbeat is fresh. Confirm the TLS certificate chain wherever
TLS terminates with normal validation (a trusted CA for private PKI); never use `-k`.
Paste the JWT alone at the first block's hidden prompt: a multi-line paste leaves every line after the first for your
shell to run.

## Sources (checked September 2026)

- SurrealDB CLI, `surreal db start` (start credentials define a new root user with the `OWNER` role) (checked November 2026): https://surrealdb.com/docs/reference/cli/db/commands/start
- Surreal CLI launcher: `surreal <component> <command>` passes everything after the component name on unchanged, and the install script installs `surreal` with the database as a pinned component (checked November 2026): https://surrealdb.com/docs/explore/cli
- Surreal CLI components: a name that is not a component runs a `surreal-<name>` from `PATH`, and `SURREAL_*` variables other than `SURREAL_CLI_*` belong to the database (checked November 2026): https://surrealdb.com/docs/explore/cli/components
- SurrealDB 4.0 release notes (the `db` component, RocksDB removal, the 3.x upgrade opt-in, cookie endpoints, "Basic authentication is rate-limited" and 23 advisories, each affecting `v3.3.5` and earlier) (checked November 2026): https://surrealdb.com/releases/4.0
- SurrealDB 3.3 release notes (a 3.3 feature "Supported on every storage backend: in-memory, RocksDB, SurrealKV, IndexedDB and TiKV") (checked November 2026): https://surrealdb.com/releases/3.3
- GNU Bash reference manual, bash-5.3 (checked October 2026), prefix assignments 3872-3878: https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n3872
- Linux man-pages `proc_pid_environ(5)`, tag man-pages-6.19 (file header says "unreleased"; version identity rests on the tag) (checked October 2026): initial environment 12-15 https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/tree/man/man5/proc_pid_environ.5?h=man-pages-6.19#n12. The same `proc_pid_environ(5)` page, tag man-pages-6.19 (file header says "unreleased"; version identity rests on the tag) (checked October 2026): later modifications 26-36 https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/tree/man/man5/proc_pid_environ.5?h=man-pages-6.19#n26. The same `proc_pid_environ(5)` page, tag man-pages-6.19 (file header says "unreleased"; version identity rests on the tag) (checked October 2026): procfs access check 43-47 https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/tree/man/man5/proc_pid_environ.5?h=man-pages-6.19#n43
- Linux man-pages `ptrace(2)`, tag man-pages-6.19 (file header says "unreleased"; version identity rests on the tag) (checked October 2026): ptrace access factors 2519-2533 https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/tree/man/man2/ptrace.2?h=man-pages-6.19#n2519
- SurrealDB v4.0.0 `start` root user and password: `--username`/`--user`/`-u` or `SURREAL_USER` and `--password`/`--pass`/`-p` or `SURREAL_PASS`, each refusing an empty value, the password's value hidden from `--help`, no stdin form in the files read (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cli/start.rs#L178-L205
- SurrealDB v4.0.0 `--unauthenticated` flag, bound to `SURREAL_UNAUTHENTICATED` (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L56-L59
- SurrealDB v4.0.0 `--bind`/`-b` (`SURREAL_BIND`) default `127.0.0.1:8000` (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cli/start.rs#L220-L223
- SurrealDB `docker/Dockerfile` sets `ENV SURREAL_BIND="0.0.0.0:8000"` in each runtime stage (L78, L106, L141, L169), each followed by `ENTRYPOINT ["/surreal"]` with no `CMD`; `dev` copies `/surreal` from `target/release/surreal` (L118-L120) and `dev-ci` from a prebuilt CI artifact (L59) (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/docker/Dockerfile#L47-L174
- SurrealDB v4.0.0 database executable: the whole `Commands` enum, with a `start` command and no `db` command (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cli/mod.rs#L144-L190
- SurrealDB v4.0.0 help: no argument's environment value shown, in any command (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cli/mod.rs#L427-L431
- SurrealDB v4.0.0 SurrealKV refusal of a directory a 3.x release wrote, unless `SURREAL_EXPERIMENTAL_UPGRADE_FROM_3X=true` (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/kvs-surrealkv/src/lib.rs#L336-L348
- SurrealDB v4.0.0 core root credentials: empty or whitespace-only values refused, and a root user created only when none exists (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/core/src/kvs/ds.rs#L3543-L3589
- SurrealDB v4.0.0 `--import-file` (`SURREAL_IMPORT_FILE`) (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L67-L70 and the import running before credentials: https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L1326-L1332
- SurrealDB v4.0.0 capabilities under `--deny-all`: `--allow-rpc`, `--allow-http` and `--allow-mcp` defaulting to an empty value (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L200-L231 and their parsers reading it as every target: https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cli/validator/mod.rs#L154-L185 and the RPC and HTTP allow getters: https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L459-L535 and the RPC deny, MCP and HTTP deny getters: https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L629-L696 and specific function denies applied on top of allows: https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L597-L607
- SurrealDB v4.0.0 capability checks: function target matching (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/rpc/src/capabilities/mod.rs#L43-L55 and allow-and-not-deny: https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/rpc/src/capabilities/mod.rs#L1158-L1160 and the same rule for RPC methods, MCP tools and HTTP routes: https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/rpc/src/capabilities/mod.rs#L1226-L1236
- SurrealDB v4.0.0 `/health` with its memory-guard condition, and `/ready` with its heartbeat condition (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/health.rs#L10-L71 and https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/ready.rs#L15-L23
- SurrealDB v4.0.0 `/signup` and `/signup/cookie` handlers calling core signup (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/signup.rs#L43-L75 and https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/signup.rs#L133-L148
- SurrealDB v4.0.0 `/signin` and `/signin/cookie` routes (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/signin.rs#L45-L54
- SurrealDB v4.0.0 scoped `/ns/.../db/.../ac/...` paths rewritten before the router (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/scope.rs#L1-L35
- SurrealDB v4.0.0 core signup refusing an access method with no `SIGNUP` (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/core/src/iam/signup.rs#L213-L215
- SurrealDB v4.0.0 HTTP authentication rate limit, off by default, burst and per-minute rate 60 (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cnf/mod.rs#L290-L304 and the requests it covers: https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/rate_limit.rs#L244-L280
- SurrealDB v4.0.0 HTTP route names that `--allow-http` accepts, `health` among them (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/rpc/src/capabilities/mod.rs#L548-L573
- SurrealDB v3.3.5 release record, whose body is only "Release v3.3.5" (pinned tag v3.3.5, commit 5c3383fe) (checked November 2026): https://github.com/surrealdb/surrealdb/releases/tag/v3.3.5
- SurrealDB v3.3.5 `start` root user and password, with no non-empty value parser and no `hide_env_values` (pinned tag v3.3.5, commit 5c3383fe) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/server/src/cli/start.rs#L178-L201
- SurrealDB v3.3.5 core root credentials, retried with no empty-value check (pinned tag v3.3.5, commit 5c3383fe) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/core/src/kvs/ds.rs#L1246-L1250
- SurrealDB v3.3.5 core datastore factory, whose comment names `rocksdb:` and `tikv:` connection strings (pinned tag v3.3.5, commit 5c3383fe) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/core/src/kvs/ds.rs#L453-L461
- SurrealDB v3.3.5 core `Datastore::new("rocksdb://database.db")` usage example (pinned tag v3.3.5, commit 5c3383fe) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/core/src/kvs/ds.rs#L4970-L4981
- SurrealDB v3.3.5 server test, compiled only with the `storage-rocksdb` feature, that builds a `rocksdb:` path (pinned tag v3.3.5, commit 5c3383fe) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/server/src/dbs/mod.rs#L2134-L2142
- SurrealDB v3.3.5 SurrealKV crate, with no `SURREAL_EXPERIMENTAL_UPGRADE_FROM_3X` text (pinned tag v3.3.5, commit 5c3383fe) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/kvs-surrealkv/src/lib.rs
- SurrealDB v3.3.5 `/signin` route and `/signup` route, whose handler calls core signup (pinned tag v3.3.5, commit 5c3383fe) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/server/src/ntw/signin.rs#L41-L49 and https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/server/src/ntw/signup.rs#L39-L75
- SurrealDB v3.3.5 HTTP authentication rate limit, covering only `POST` to `/signin` and `/signup` (pinned tag v3.3.5, commit 5c3383fe) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/server/src/ntw/rate_limit.rs#L243-L259
- SurrealDB v3.3.5 capabilities: `--allow-rpc` and `--allow-http` with no MCP-tool list (pinned tag v3.3.5, commit 5c3383fe) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/server/src/dbs/mod.rs#L105-L324 and the HTTP route names, with `mcp` as a route: https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/rpc/src/capabilities/mod.rs#L373-L397
- SurrealDB v3.3.5 `surreal mcp` command, behind `#[cfg(feature = "mcp")]`, whose arguments are named through the `cli::mcp` module (`cli/mcp.rs` or `cli/mcp/mod.rs`), which was not read (pinned tag v3.3.5, commit 5c3383fe) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/server/src/cli/mod.rs#L182-L184
- SurrealDB v3.3.5 `use mcp::McpCommandArguments;`, which names the `surreal mcp` arguments through the `cli::mcp` module (pinned tag v3.3.5, commit 5c3383fe) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/server/src/cli/mod.rs#L37-L38
- SurrealDB CLI, `surreal db sql` (checked November 2026): https://surrealdb.com/docs/reference/cli/db/commands/sql
- SurrealDB security overview (checked November 2026): https://surrealdb.com/docs/learn/security
- SurrealDB authentication overview (`DEFINE USER` at root, namespace or database level) (checked November 2026): https://surrealdb.com/docs/learn/security/authentication/overview
- SurrealDB DEFINE USER (a root-level user given a limited role such as `VIEWER`, for monitoring each namespace and database; only the built-in roles OWNER, EDITOR and VIEWER currently available) (checked November 2026): https://surrealdb.com/docs/surrealql/statements/define/user
- SurrealDB security best practices (system-user roles, with `ROLES VIEWER` and `ROLES EDITOR` examples) (checked November 2026): https://surrealdb.com/docs/learn/security/best-practices/security-best-practices
- SurrealDB capabilities (`--allow-all`/`--deny-all`, net denied, functions allowed, scripting/guests off, specificity + deny-wins, a specific deny winning over any allow) (checked November 2026): https://surrealdb.com/docs/learn/security/authorization/capabilities
- SurrealDB permissions and row-level security (system users bypass table/field PERMISSIONS; on a table, omitting `PERMISSIONS` results in `PERMISSIONS NONE`, while a field without a clause is stored as `PERMISSIONS FULL`) (checked November 2026): https://surrealdb.com/docs/learn/security/authorization/permissions-and-row-level-security
- SurrealDB DEFINE ACCESS (RECORD, JWT, BEARER) (checked November 2026): https://surrealdb.com/docs/reference/query-language/statements/define/access/record
- SurrealDB 2.0.0 release (auth on by default, `--unauthenticated`, bind default 127.0.0.1) (checked November 2026): https://surrealdb.com/releases/2.0
- SurrealDB HTTP protocol (`/signup`, `/signin`, `POST /sql`, `/health`, `/status`; a denied `health` route answers `403`) (checked November 2026): https://surrealdb.com/docs/reference/rest-api/http-protocol
- SurrealDB INFO statement (database information requires a system user) (checked November 2026): https://surrealdb.com/docs/reference/query-language/statements/info
- SurrealDB DEFINE ACCESS TYPE JWT (native `AUDIENCE` since 3.3, issuer check via `AUTHENTICATE`) (rolling documentation, checked November 2026): https://surrealdb.com/docs/reference/query-language/statements/define/access/jwt
- SurrealDB DEFINE SCOPE (deprecated in 2.x, removed in 3.0) (checked November 2026): https://surrealdb.com/docs/reference/query-language/statements/define/scope
- SurrealDB advisory GHSA-whfh-76h8-2r66, "CLI help output prints the values of SURREAL_PASS and SURREAL_TOKEN" (low; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-whfh-76h8-2r66
- SurrealDB advisory GHSA-5w6j-qm42-4rc2, "JavaScript Built-in Bridge Bypasses Function Capability Enforcement" (high; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-5w6j-qm42-4rc2
- SurrealDB advisory GHSA-fq69-wr4w-v3gm, "JavaScript Query Bridge Bypasses Arbitrary-Query Subject Gate" (high; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-fq69-wr4w-v3gm
- SurrealDB advisory GHSA-q83r-f38r-rwvj, "Surrealism WASI socket allowlist ignores deny_net, enabling SSRF via hostname resolving to a private IP" (high; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-q83r-f38r-rwvj
- SurrealDB advisory GHSA-5xcv-fm6g-4hf3, "Quoted Computed-Field Formatter Bypasses Field-Level SELECT Permissions" (high; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-5xcv-fm6g-4hf3
- SurrealDB advisory GHSA-fh2q-8f75-m4h6, "REFERENCE ON DELETE CASCADE/UNSET/CUSTOM bypasses target table PERMISSIONS FOR delete/update" (high; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-fh2q-8f75-m4h6
- SurrealDB advisory GHSA-qh3v-rr48-x3cq, "Authenticated Export Permission Bypass" (medium; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-qh3v-rr48-x3cq
- SurrealDB advisory GHSA-ffvm-mqh3-7986, FOR loop variables named `$access`, `$auth` and `$token` shadowing the session values that table permission expressions use ("medium" in the record, while the 4.0 release page lists it as "High"; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-ffvm-mqh3-7986
- SurrealDB advisory GHSA-wjh3-m4pv-q6cp, "Cross-field array-index drift in wildcard field-permission filtering" (medium; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-wjh3-m4pv-q6cp
- SurrealDB advisory GHSA-cff7-q66j-4hc8, "UNIQUE-Index Conflict Errors Disclose SELECT-Restricted Field Values and Record Ids in SurrealDB" (medium; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-cff7-q66j-4hc8
- SurrealDB advisory GHSA-3rcm-c653-wgmr, "Re-RELATE on an Existing Edge Echoes Stored in/out Endpoints Despite SELECT Restrictions in SurrealDB" (medium; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-3rcm-c653-wgmr
- SurrealDB advisory GHSA-ff2q-h4x7-cpj4, "ON DELETE REJECT Errors Disclose SELECT-Hidden Referencing Record Ids in SurrealDB" (medium; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-ff2q-h4x7-cpj4
- SurrealDB advisory GHSA-pvv9-h693-m8r4, "SurrealDB LIVE query notification expressions allow write side effects that bypass the write-blocking guard", including data exfiltration after a SELECT permission is revoked (medium; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-pvv9-h693-m8r4
- SurrealDB advisory GHSA-m887-2246-mgw3, "VIEWER role can define tables implicitly via CREATE on a non-STRICT database" (low; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-m887-2246-mgw3
- SurrealDB advisory GHSA-3287-hpm5-3f8r, DDL statements bypassing namespace and database implicit-creation authorization (medium; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-3287-hpm5-3f8r
- SurrealDB advisory GHSA-cr79-9p8r-p5wx, "MCP Tool Identifier Validation Permits Statement Injection via Escaped Backticks", with arbitrary SQL query execution through MCP tool invocation (high; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-cr79-9p8r-p5wx
- SurrealDB advisory GHSA-p3c2-wh5f-jwqm, "GraphQL WebSocket upgrade omits frame and message size limits enabling memory amplification" (high; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-p3c2-wh5f-jwqm
- SurrealDB advisory GHSA-cph5-pm57-9w9c, "Direct Filesystem Buckets Permit Path Traversal Across Key-Based ACL Boundaries" (high; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-cph5-pm57-9w9c
- SurrealDB advisory GHSA-7pqw-x84x-frxc, "Filesystem Bucket Containment Fails to Resolve Descendant Symlinks" (high; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-7pqw-x84x-frxc
- SurrealDB advisory GHSA-6c37-x4jm-529x, "Windows Backslashes Bypass Global Bucket Path Traversal Protection" (high; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-6c37-x4jm-529x
- SurrealDB advisory GHSA-7r2m-g5wf-pj9j, "Model Export Route joins Raw Name Permitting Authenticated Request Redirection" (high; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-7r2m-g5wf-pj9j
- SurrealDB advisory GHSA-623g-mhxq-5hmf, "Interactive transactions keep the writes of a statement refused by a THROWing event, and commit persists them" (medium; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-623g-mhxq-5hmf
- SurrealDB advisory GHSA-m9qr-4rcq-3jhc, a safe-code data race and double-free in `surrealdb-core` through `reblessive 0.4.3` (high; affected `< 4.0.0`, patched `4.0.0`, filed against `surrealdb-core`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-m9qr-4rcq-3jhc


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- pinned: SurrealDB server and image (v4.0.0)
- pinned-3x: SurrealDB 3.x server (v3.3.5)
- audience: SurrealDB native AUDIENCE minimum (3.3)
- scope-old: SurrealDB SCOPE deprecation (2.x)
- scope-removed: SurrealDB SCOPE removal (3.0)
- docs: SurrealDB documentation (rolling) (unknown)
- defaults: SurrealDB 2.0 release announcement (unknown)
- advisories: SurrealDB security advisories (unknown)
- bash: GNU Bash reference manual (bash-5.3)
- procfs: Linux procfs manual (man-pages-6.19)
- ptrace: Linux ptrace manual (man-pages-6.19)

Claims (full source mapping in the JSON block below):

- auth-default (REASONED; defaults): Since 2.0.0 authentication defaults on, --auth was removed and --unauthenticated added; older releases do not share this default.
- basis-3x (REASONED; pinned-3x, docs): The guide covers v4.0.0 and, where they differ, v3.3.5; the v3.3.5 source read supports each statement citing only v4.0.0 source unless stated. Not established at v3.3.5: statements resting only on rolling documentation, the capability defaults among them, what v3.3.5 changed, as its release record has no notes, and which command form a 3.x install takes.
- bind-default (REASONED; defaults, pinned): Since 2.0.0 the CLI defaults to 127.0.0.1:8000; v4.0.0 --bind/-b and SURREAL_BIND retain that loopback default.
- command-form (REASONED; pinned, docs): At v4.0.0 the database executable takes start and defines no db command; the Surreal CLI launcher runs it as surreal db start, passing the rest unchanged. As this guide's inference, under the launcher surreal start does not start the database, so the host block uses surreal db start and the image keeps start.
- root-bootstrap (REASONED; docs, pinned): User/password flags or SURREAL_USER/PASS initialize a root only when none exists; they neither disable authentication nor rotate an existing password. At v4.0.0 the flags refuse empty values, core also refuses whitespace-only ones, and an import file that supplies root users suppresses the flag user.
- root-bootstrap-3x (REASONED; pinned-3x): At v3.3.5 neither empty-credential check is in the cited code: the user and password flags have no non-empty value parser, and core credential setup has no empty-value check. Whether v3.3.5 refuses empty values elsewhere is not established; the block refuses an empty password itself.
- root-input (REASONED; pinned, bash, procfs, ptrace): No v4.0.0 server file read has a stdin password form; prompt and use a Bash command-local environment assignment, not argv. As this guide's assessment, the initial server environment may be exposed to the same account and root when the procfs ptrace check permits; an inheriting process may expose it the same way while it runs; treat it as exposed to that account and root while the server runs.
- help-values (REASONED; pinned, advisories): Before 4.0.0 --help could print SURREAL_PASS and SURREAL_TOKEN values (GHSA-whfh-76h8-2r66, low, affecting versions below 4.0.0, patched in 4.0.0); at v4.0.0 the start password sets hide_env_values and the executable hides every argument's environment value in help.
- help-values-3x (REASONED; pinned-3x, advisories): At v3.3.5 the start password sets no hide_env_values and no v3.3.5 file read calls it, so v3.3.5 lies inside the affected range of GHSA-whfh-76h8-2r66, below 4.0.0, though its reproductions name images up to v3.3.4. As this guide's advice, never run --help on v3.3.5 with SURREAL_PASS or SURREAL_TOKEN set.
- environment (REASONED; docs, pinned): The clean-Bash block clears user/password variables and rejects other inherited SURREAL_* options, including auth and bind overrides, the 3.x upgrade opt-in and the launcher's SURREAL_CLI_* variables.
- launcher-unknowns (REASONED; docs): Whether the Surreal CLI launcher stays running as the server's parent, or passes SURREAL_PASS on unchanged, is not established at v4.0.0; as this guide's assessment, treat a resident launcher as exposed like the server and confirm the root user by signing in.
- storage-upgrade (REASONED; pinned, docs): v4.0.0 removes the RocksDB engine; the docs read rocksdb:// as a deprecated spelling of surrealkv://, and the block names surrealkv:/data/mydb.db. A 3.x directory is refused unless SURREAL_EXPERIMENTAL_UPGRADE_FROM_3X=true, which the block cannot carry; convert it as a separate step after a backup. The server path check was not read.
- storage-3x (REASONED; pinned-3x, docs): As this guide's inference from the v3.3.5 datastore factory comment, a rocksdb:// usage example in core, a rocksdb: test behind the storage-rocksdb feature and the 3.3 release page, RocksDB is a working engine at v3.3.5; the v4.0.0 refusal of a 3.x directory does not apply there, as its SurrealKV crate has no upgrade opt-in text. How v3.3.5 parses storage paths is not established.
- unauthenticated (REASONED; docs, pinned): --unauthenticated/SURREAL_UNAUTHENTICATED gives guests OWNER-equivalent access; never carry it onto a remotely reachable deployment.
- docker-bind (REASONED; pinned): v4.0.0 image stages set SURREAL_BIND=0.0.0.0:8000 without CMD; start without an override listens on all container IPv4 interfaces, requiring private network or loopback publication. Whether published images use that file is not established.
- private-network (REASONED; docs): Widen host binds only deliberately to private addresses; internal-service databases should have no public interface.
- system-users (REASONED; docs): System users exist at root, namespace and database level; the DEFINE USER page says only the built-in roles OWNER, EDITOR and VIEWER are currently available, but no page read says every user holds one. All bypass table/field PERMISSIONS, using roles instead, so scoped system users do not supply record isolation.
- root-visibility (REASONED; docs): The DEFINE USER page says even a root-level user can be given a limited role such as VIEWER, useful for automated services that need to monitor each namespace and database; the JWT page says root tokens can act on all tables in all databases of all namespaces. As this guide's inference, a root system user reaches every namespace and database, within what its role allows.
- record-users (REASONED; docs): Record users authenticate through DEFINE ACCESS TYPE RECORD SIGNUP/SIGNIN logic and are bound by table and field PERMISSIONS: omitting PERMISSIONS on a table results in PERMISSIONS NONE, while a field without a clause is stored as PERMISSIONS FULL and follows the table's rules.
- signup (REASONED; docs, pinned): Unauthenticated /signup and /signin, their v4.0.0 cookie forms and scoped /ns/.../ac/... paths are intentional; every HTTP signup form reaches the core check that refuses an access method with no SIGNUP, so omit SIGNUP to prevent public registration and test refusal beside a provisioned sign-in. RPC signup was not traced.
- signup-3x (REASONED; pinned-3x, pinned): At v3.3.5 the files read register only the /signin and /signup routes, with no cookie routes and no scoped-path rewrite, and the /signup handler calls the same core signup check as v4.0.0. Whether another v3.3.5 file registers cookie or scoped routes, and whether RPC signup reaches the check, is not established.
- rate-limit (REASONED; pinned, docs): At v4.0.0 the per-address HTTP limit on sign-in, sign-up and Basic-auth requests is off by default (SURREAL_HTTP_AUTH_RATE_LIMIT_ENABLED false; burst and per-minute 60 once on), so the release page's Basic-auth rate limit applies only when enabled; a request with no derivable client address is not limited.
- rate-limit-3x (REASONED; pinned-3x, pinned): At v3.3.5 the HTTP authentication limiter has the same setting and defaults but limits only POST requests to /signin and /signup with a derivable client address, whatever headers they carry; it has no cookie, refresh or sign-out path. It lacks v4.0.0's case for other requests carrying Basic credentials, so as this guide's reading of v3.3.5 source those are not rate-limited even when it is enabled.
- permission-advisories (REASONED; advisories): v4.0.0 fixes advisories affecting versions below 4.0.0 on table, field and role controls: GHSA-5xcv-fm6g-4hf3, GHSA-fh2q-8f75-m4h6, GHSA-qh3v-rr48-x3cq, GHSA-ffvm-mqh3-7986, GHSA-wjh3-m4pv-q6cp, GHSA-cff7-q66j-4hc8, GHSA-3rcm-c653-wgmr, GHSA-ff2q-h4x7-cpj4, GHSA-pvv9-h693-m8r4, GHSA-m887-2246-mgw3 and GHSA-3287-hpm5-3f8r; do not rely on those controls on an earlier release.
- scope-history (REASONED; scope-old, scope-removed): Use DEFINE ACCESS TYPE RECORD; legacy DEFINE SCOPE was deprecated in 2.x and removed in 3.0.
- access-types (REASONED; docs): DEFINE ACCESS also supports JWT and per-client BEARER keys; standalone JWT creates system-level sessions, while RECORD WITH JWT retains record permissions.
- jwt-checks (REASONED; docs, audience): Verify token algorithm/key or JWKS, issuer and audience; native AUDIENCE is available since 3.3.0, so set it at the v4.0.0 basis, and check the issuer in AUTHENTICATE as the JWT page's example does. Compare invalid tokens against a valid control.
- capability-all (REASONED; docs, pinned): allow-all and deny-all default off; prefer deny-all with narrow route, RPC-method and function allowances. As this guide's reading of v4.0.0 source, deny-all alone leaves every HTTP route, RPC method and MCP tool allowed, as allow-http, allow-rpc and allow-mcp default to all targets; no run confirmed it, so pass explicit allow-http and allow-rpc lists.
- capability-health (REASONED; pinned, docs): When the Verify block's health check should pass under deny-all, include health in the allow-http list: the HTTP allow getter returns a named list as given, the route parser reads health as the health route, and /health refuses a route that is not allowed, which the HTTP protocol page says answers 403.
- mcp-advisory (REASONED; advisories): GHSA-cr79-9p8r-p5wx (high; affecting versions below 4.0.0, patched in 4.0.0) reports MCP tool identifier validation permitting statement injection, with arbitrary SQL query execution through MCP tool invocation; it bears on MCP tools staying allowed under deny-all.
- capability-mcp-3x (REASONED; pinned-3x): The v3.3.5 capability files read define allow-rpc and allow-http with the same empty default but no allow-mcp or deny-mcp list; their only MCP target is the mcp HTTP route. surreal mcp is behind the mcp feature; its arguments are named through the cli::mcp module (use mcp::McpCommandArguments;), which was not read, nor was its MCP crate, so whether anything else gates MCP tools is not established.
- capability-net (REASONED; docs): Network access is denied by default; restrict http::* and JWKS destinations and retain external egress protections against SSRF.
- capability-functions (REASONED; docs): Functions are allowed by default; a bare allow-funcs broadens access beyond narrow named allowances.
- capability-scripting (REASONED; docs): Embedded scripting defaults off; enable it only when required.
- capability-guests (REASONED; docs): Guest access defaults off; capabilities govern what an authorized query may do independently of authentication.
- capability-precedence (REASONED; docs, pinned): A category allow list overrides deny-all or a bare category deny, and deny wins at equal specificity; between list entries a deny entry wins over any allow entry, so a narrower allow does not override a broader deny, as the capabilities page's own example and this guide's reading of v4.0.0 source agree.
- capability-advisories (REASONED; advisories, docs): v4.0.0 fixes capability bypasses affecting versions below 4.0.0: GHSA-5w6j-qm42-4rc2, GHSA-fq69-wr4w-v3gm and GHSA-q83r-f38r-rwvj; the 4.0 release page lists 23 advisories, of which this guide names 16 and lists 7 more.
- advisories-3x (REASONED; advisories, docs): v3.3.5 is in all 23 affected ranges of the 4.0 advisories; exposure depends on prerequisites. GHSA-q83r-f38r-rwvj needs experimental Surrealism, authenticated module upload and invoke rights, and that the operator relies on deny_net (with a broad or attacker-influenceable allow_net) for egress control. GHSA-m9qr-4rcq-3jhc is "not remote/black-box triggerable." Crate-to-server mapping is inference.
- tls (REASONED; docs): web-crt and web-key provide native HTTPS; SurrealDB documents TLS termination at a load balancer or reverse proxy, and reaching the instance only over a tailnet is this guide's own suggestion.
- mfa (REASONED; docs): Whether SurrealDB v4.0.0 has a native second factor is not established, as no page read addresses one; require IdP or administrative-gateway MFA and prevent direct-origin bypass.
- verify-inventory (REASONED; docs, pinned): Inventory 8000 on loopback/private addresses; at v4.0.0 a /health 200 means the route is allowed, the memory-health failure condition was not met (the check is disabled, or the guard has not stayed engaged for its configured period) and storage answers, not authentication or finished startup; /status is liveness and /ready follows startup and any configured heartbeat budget.
- verify-auth (REASONED; docs): Compare INFO FOR DB without credentials and with a system-user JWT on the same NS/DB: exposed auth-off returns info; fixed denies anonymous access and returns authenticated OK data.
- verify-auth-limits (REASONED; docs): Test direct origin and HTTPS; HTTP 200, missing database, disabled route, proxy rejection or transport failure alone proves no authorization control or record permissions.
- verify-origin (REASONED; docs): Any HTTP answer from an untrusted-network origin probe proves reachability; a gateway result alone does not establish origin isolation.
- verify-tls (REASONED; docs): Validate the certificate chain at every TLS termination using normal trust checks, never -k.

````json
{
  "schema": 1,
  "checked": "2026-11-05",
  "documentation_checked": "2026-09",
  "body_sha256": "e955c8567ffc256dc05bbd2c57e3e72f1a758599118df2ac18ef43472a6ee4e5",
  "components": {
    "pinned": {
      "name": "SurrealDB server and image",
      "basis": "v4.0.0",
      "sources": {
        "s325ec1bdaeca": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cli/start.rs#L178-L205",
        "s025b59b3dab9": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L56-L59",
        "sd341f6f1f6cb": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cli/start.rs#L220-L223",
        "s439e9f7b6e75": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/docker/Dockerfile#L47-L174",
        "s02c05ba6cc1a": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cli/mod.rs#L144-L190",
        "sc48298a83d5b": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cli/mod.rs#L427-L431",
        "s315fd2b3211f": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/kvs-surrealkv/src/lib.rs#L336-L348",
        "s68c349d06271": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/core/src/kvs/ds.rs#L3543-L3589",
        "s85b6558fdf7d": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L67-L70",
        "se2b9738f37cc": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L1326-L1332",
        "scce5b37cc67e": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L200-L231",
        "sb983f262eea6": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cli/validator/mod.rs#L154-L185",
        "s41f93c8f1044": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L459-L535",
        "s10eff64ec263": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L629-L696",
        "sd1dcb148f996": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L597-L607",
        "s6a13d5749f9a": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/rpc/src/capabilities/mod.rs#L43-L55",
        "s6f5b41199da6": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/rpc/src/capabilities/mod.rs#L1158-L1160",
        "sc2c677a2fedc": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/rpc/src/capabilities/mod.rs#L1226-L1236",
        "s538897c5bacc": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/health.rs#L10-L71",
        "s67ee52a23e57": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/ready.rs#L15-L23",
        "s6ddbe030cea1": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/signup.rs#L43-L75",
        "s1c21ede08712": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/signup.rs#L133-L148",
        "s0a950c71cc01": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/signin.rs#L45-L54",
        "saa6be90fd793": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/scope.rs#L1-L35",
        "se50982814d76": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/core/src/iam/signup.rs#L213-L215",
        "s57c8f0d7c045": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cnf/mod.rs#L290-L304",
        "s0d453e52834e": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/rate_limit.rs#L244-L280",
        "s02c701807dae": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/rpc/src/capabilities/mod.rs#L548-L573"
      }
    },
    "pinned-3x": {
      "name": "SurrealDB 3.x server",
      "basis": "v3.3.5",
      "sources": {
        "s7374afb961a9": "https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/server/src/cli/start.rs#L178-L201",
        "s38f06f165ec4": "https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/core/src/kvs/ds.rs#L1246-L1250",
        "s77f37f03f1ee": "https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/core/src/kvs/ds.rs#L453-L461",
        "s12582dd057b1": "https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/core/src/kvs/ds.rs#L4970-L4981",
        "sfc310c15b039": "https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/server/src/dbs/mod.rs#L2134-L2142",
        "s73099ef5068f": "https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/kvs-surrealkv/src/lib.rs",
        "sc840084091cd": "https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/server/src/ntw/signin.rs#L41-L49",
        "s65828a4dd9ea": "https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/server/src/ntw/signup.rs#L39-L75",
        "s10ad47f37dcd": "https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/server/src/ntw/rate_limit.rs#L243-L259",
        "s7144f593a339": "https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/server/src/dbs/mod.rs#L105-L324",
        "sb555f9745ad7": "https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/rpc/src/capabilities/mod.rs#L373-L397",
        "sd82d608cc2e1": "https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/server/src/cli/mod.rs#L182-L184",
        "s5ef899492471": "https://github.com/surrealdb/surrealdb/blob/v3.3.5/surrealdb/server/src/cli/mod.rs#L37-L38",
        "s905871ed201e": "https://github.com/surrealdb/surrealdb/releases/tag/v3.3.5"
      }
    },
    "audience": {
      "name": "SurrealDB native AUDIENCE minimum",
      "basis": "3.3",
      "sources": {
        "s048fd6bd1f3e": "https://surrealdb.com/docs/reference/query-language/statements/define/access/jwt"
      }
    },
    "scope-old": {
      "name": "SurrealDB SCOPE deprecation",
      "basis": "2.x",
      "sources": {
        "s5a6f3aad8f24": "https://surrealdb.com/docs/reference/query-language/statements/define/scope"
      }
    },
    "scope-removed": {
      "name": "SurrealDB SCOPE removal",
      "basis": "3.0",
      "sources": {
        "s5a6f3aad8f24": "https://surrealdb.com/docs/reference/query-language/statements/define/scope"
      }
    },
    "docs": {
      "name": "SurrealDB documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s2eb33a763ea4": "https://surrealdb.com/docs/reference/cli/db/commands/start",
        "s38b5f5aad1d4": "https://surrealdb.com/docs/learn/security",
        "sdaa9a636537a": "https://surrealdb.com/docs/learn/security/authentication/overview",
        "s39d3475ac024": "https://surrealdb.com/docs/surrealql/statements/define/user",
        "sae73137661aa": "https://surrealdb.com/docs/learn/security/best-practices/security-best-practices",
        "sc798cc43c457": "https://surrealdb.com/docs/learn/security/authorization/capabilities",
        "sb9c3a17a2998": "https://surrealdb.com/docs/learn/security/authorization/permissions-and-row-level-security",
        "sfdfa4e63cdd5": "https://surrealdb.com/docs/reference/query-language/statements/define/access/record",
        "scc00d3d3618d": "https://surrealdb.com/docs/reference/rest-api/http-protocol",
        "s51100e115b41": "https://surrealdb.com/docs/reference/query-language/statements/info",
        "s048fd6bd1f3e": "https://surrealdb.com/docs/reference/query-language/statements/define/access/jwt",
        "se2dbccd34348": "https://surrealdb.com/docs/explore/cli",
        "s80d3b718d95d": "https://surrealdb.com/docs/explore/cli/components",
        "sac0752ff1726": "https://surrealdb.com/releases/4.0",
        "s23996eedc4c4": "https://surrealdb.com/releases/3.3"
      }
    },
    "defaults": {
      "name": "SurrealDB 2.0 release announcement",
      "basis": "unknown",
      "sources": {
        "se73fa9c93548": "https://surrealdb.com/releases/2.0"
      }
    },
    "advisories": {
      "name": "SurrealDB security advisories",
      "basis": "unknown",
      "sources": {
        "sd74a20d357b6": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-whfh-76h8-2r66",
        "s28cd26dc0103": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-5w6j-qm42-4rc2",
        "sad31e9ec665b": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-fq69-wr4w-v3gm",
        "s9c8e76544223": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-q83r-f38r-rwvj",
        "s1b98c24eb665": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-5xcv-fm6g-4hf3",
        "sb541fcd902da": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-fh2q-8f75-m4h6",
        "s2da32614f366": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-qh3v-rr48-x3cq",
        "s8064745de0e0": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-ffvm-mqh3-7986",
        "s2f3b208498de": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-wjh3-m4pv-q6cp",
        "se50ef588388b": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-cff7-q66j-4hc8",
        "se5f6e6699691": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-3rcm-c653-wgmr",
        "s29b6dab1b6dd": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-ff2q-h4x7-cpj4",
        "sb7209bfe440d": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-pvv9-h693-m8r4",
        "s6363f9220ffe": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-m887-2246-mgw3",
        "s1f98319f76ae": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-3287-hpm5-3f8r",
        "s390dd974a89c": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-cr79-9p8r-p5wx",
        "sd6a62a692fe6": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-p3c2-wh5f-jwqm",
        "se028de7b3f26": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-cph5-pm57-9w9c",
        "s4846cdc74b47": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-7pqw-x84x-frxc",
        "s7b253e6289d7": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-6c37-x4jm-529x",
        "s3a93dc5e0a90": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-7r2m-g5wf-pj9j",
        "s03e87b1aeb09": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-623g-mhxq-5hmf",
        "sc475ce490938": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-m9qr-4rcq-3jhc"
      }
    },
    "bash": {
      "name": "GNU Bash reference manual",
      "basis": "bash-5.3",
      "sources": {
        "sf9757e9fd6e8": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n3872"
      }
    },
    "procfs": {
      "name": "Linux procfs manual",
      "basis": "man-pages-6.19",
      "sources": {
        "s56aa3e840419": "https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/tree/man/man5/proc_pid_environ.5?h=man-pages-6.19#n12",
        "s9aae2a8587f2": "https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/tree/man/man5/proc_pid_environ.5?h=man-pages-6.19#n26",
        "sd64e43d1515a": "https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/tree/man/man5/proc_pid_environ.5?h=man-pages-6.19#n43"
      }
    },
    "ptrace": {
      "name": "Linux ptrace manual",
      "basis": "man-pages-6.19",
      "sources": {
        "sfe9fe6919d33": "https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/tree/man/man2/ptrace.2?h=man-pages-6.19#n2519"
      }
    }
  },
  "claims": {
    "auth-default": {"text": "Since 2.0.0 authentication defaults on, --auth was removed and --unauthenticated added; older releases do not share this default.", "components": ["defaults"], "sources": ["defaults:se73fa9c93548"], "status": "REASONED"},
    "basis-3x": {"text": "The guide covers v4.0.0 and, where they differ, v3.3.5; the v3.3.5 source read supports each statement citing only v4.0.0 source unless stated. Not established at v3.3.5: statements resting only on rolling documentation, the capability defaults among them, what v3.3.5 changed, as its release record has no notes, and which command form a 3.x install takes.", "components": ["pinned-3x", "docs"], "sources": ["pinned-3x:s905871ed201e", "docs:sc798cc43c457", "docs:se2dbccd34348"], "status": "REASONED"},
    "bind-default": {"text": "Since 2.0.0 the CLI defaults to 127.0.0.1:8000; v4.0.0 --bind/-b and SURREAL_BIND retain that loopback default.", "components": ["defaults", "pinned"], "sources": ["defaults:se73fa9c93548", "pinned:sd341f6f1f6cb"], "status": "REASONED"},
    "command-form": {"text": "At v4.0.0 the database executable takes start and defines no db command; the Surreal CLI launcher runs it as surreal db start, passing the rest unchanged. As this guide's inference, under the launcher surreal start does not start the database, so the host block uses surreal db start and the image keeps start.", "components": ["pinned", "docs"], "sources": ["pinned:s02c05ba6cc1a", "pinned:s439e9f7b6e75", "docs:se2dbccd34348", "docs:s80d3b718d95d", "docs:sac0752ff1726"], "status": "REASONED"},
    "root-bootstrap": {"text": "User/password flags or SURREAL_USER/PASS initialize a root only when none exists; they neither disable authentication nor rotate an existing password. At v4.0.0 the flags refuse empty values, core also refuses whitespace-only ones, and an import file that supplies root users suppresses the flag user.", "components": ["docs", "pinned"], "sources": ["docs:s2eb33a763ea4", "pinned:s325ec1bdaeca", "pinned:s68c349d06271", "pinned:s85b6558fdf7d", "pinned:se2b9738f37cc"], "status": "REASONED"},
    "root-bootstrap-3x": {"text": "At v3.3.5 neither empty-credential check is in the cited code: the user and password flags have no non-empty value parser, and core credential setup has no empty-value check. Whether v3.3.5 refuses empty values elsewhere is not established; the block refuses an empty password itself.", "components": ["pinned-3x"], "sources": ["pinned-3x:s7374afb961a9", "pinned-3x:s38f06f165ec4"], "status": "REASONED"},
    "root-input": {"text": "No v4.0.0 server file read has a stdin password form; prompt and use a Bash command-local environment assignment, not argv. As this guide's assessment, the initial server environment may be exposed to the same account and root when the procfs ptrace check permits; an inheriting process may expose it the same way while it runs; treat it as exposed to that account and root while the server runs.", "components": ["pinned", "bash", "procfs", "ptrace"], "sources": ["pinned:s325ec1bdaeca", "bash:sf9757e9fd6e8", "procfs:s56aa3e840419", "procfs:s9aae2a8587f2", "procfs:sd64e43d1515a", "ptrace:sfe9fe6919d33"], "status": "REASONED"},
    "help-values": {"text": "Before 4.0.0 --help could print SURREAL_PASS and SURREAL_TOKEN values (GHSA-whfh-76h8-2r66, low, affecting versions below 4.0.0, patched in 4.0.0); at v4.0.0 the start password sets hide_env_values and the executable hides every argument's environment value in help.", "components": ["pinned", "advisories"], "sources": ["pinned:s325ec1bdaeca", "pinned:sc48298a83d5b", "advisories:sd74a20d357b6"], "status": "REASONED"},
    "help-values-3x": {"text": "At v3.3.5 the start password sets no hide_env_values and no v3.3.5 file read calls it, so v3.3.5 lies inside the affected range of GHSA-whfh-76h8-2r66, below 4.0.0, though its reproductions name images up to v3.3.4. As this guide's advice, never run --help on v3.3.5 with SURREAL_PASS or SURREAL_TOKEN set.", "components": ["pinned-3x", "advisories"], "sources": ["pinned-3x:s7374afb961a9", "advisories:sd74a20d357b6"], "status": "REASONED"},
    "environment": {"text": "The clean-Bash block clears user/password variables and rejects other inherited SURREAL_* options, including auth and bind overrides, the 3.x upgrade opt-in and the launcher's SURREAL_CLI_* variables.", "components": ["docs", "pinned"], "sources": ["docs:s2eb33a763ea4", "docs:s80d3b718d95d", "pinned:s025b59b3dab9", "pinned:sd341f6f1f6cb", "pinned:s315fd2b3211f"], "status": "REASONED"},
    "launcher-unknowns": {"text": "Whether the Surreal CLI launcher stays running as the server's parent, or passes SURREAL_PASS on unchanged, is not established at v4.0.0; as this guide's assessment, treat a resident launcher as exposed like the server and confirm the root user by signing in.", "components": ["docs"], "sources": ["docs:se2dbccd34348", "docs:s80d3b718d95d"], "status": "REASONED"},
    "storage-upgrade": {"text": "v4.0.0 removes the RocksDB engine; the docs read rocksdb:// as a deprecated spelling of surrealkv://, and the block names surrealkv:/data/mydb.db. A 3.x directory is refused unless SURREAL_EXPERIMENTAL_UPGRADE_FROM_3X=true, which the block cannot carry; convert it as a separate step after a backup. The server path check was not read.", "components": ["pinned", "docs"], "sources": ["pinned:s315fd2b3211f", "docs:s2eb33a763ea4", "docs:sac0752ff1726"], "status": "REASONED"},
    "storage-3x": {"text": "As this guide's inference from the v3.3.5 datastore factory comment, a rocksdb:// usage example in core, a rocksdb: test behind the storage-rocksdb feature and the 3.3 release page, RocksDB is a working engine at v3.3.5; the v4.0.0 refusal of a 3.x directory does not apply there, as its SurrealKV crate has no upgrade opt-in text. How v3.3.5 parses storage paths is not established.", "components": ["pinned-3x", "docs"], "sources": ["pinned-3x:s77f37f03f1ee", "pinned-3x:s12582dd057b1", "pinned-3x:sfc310c15b039", "pinned-3x:s73099ef5068f", "docs:s23996eedc4c4"], "status": "REASONED"},
    "unauthenticated": {"text": "--unauthenticated/SURREAL_UNAUTHENTICATED gives guests OWNER-equivalent access; never carry it onto a remotely reachable deployment.", "components": ["docs", "pinned"], "sources": ["docs:s2eb33a763ea4", "pinned:s025b59b3dab9"], "status": "REASONED"},
    "docker-bind": {"text": "v4.0.0 image stages set SURREAL_BIND=0.0.0.0:8000 without CMD; start without an override listens on all container IPv4 interfaces, requiring private network or loopback publication. Whether published images use that file is not established.", "components": ["pinned"], "sources": ["pinned:s439e9f7b6e75"], "status": "REASONED"},
    "private-network": {"text": "Widen host binds only deliberately to private addresses; internal-service databases should have no public interface.", "components": ["docs"], "sources": ["docs:sae73137661aa"], "status": "REASONED"},
    "system-users": {"text": "System users exist at root, namespace and database level; the DEFINE USER page says only the built-in roles OWNER, EDITOR and VIEWER are currently available, but no page read says every user holds one. All bypass table/field PERMISSIONS, using roles instead, so scoped system users do not supply record isolation.", "components": ["docs"], "sources": ["docs:sdaa9a636537a", "docs:s39d3475ac024", "docs:sae73137661aa", "docs:s2eb33a763ea4", "docs:sb9c3a17a2998"], "status": "REASONED"},
    "root-visibility": {"text": "The DEFINE USER page says even a root-level user can be given a limited role such as VIEWER, useful for automated services that need to monitor each namespace and database; the JWT page says root tokens can act on all tables in all databases of all namespaces. As this guide's inference, a root system user reaches every namespace and database, within what its role allows.", "components": ["docs"], "sources": ["docs:s39d3475ac024", "docs:s048fd6bd1f3e", "docs:sdaa9a636537a"], "status": "REASONED"},
    "record-users": {"text": "Record users authenticate through DEFINE ACCESS TYPE RECORD SIGNUP/SIGNIN logic and are bound by table and field PERMISSIONS: omitting PERMISSIONS on a table results in PERMISSIONS NONE, while a field without a clause is stored as PERMISSIONS FULL and follows the table's rules.", "components": ["docs"], "sources": ["docs:sb9c3a17a2998", "docs:sfdfa4e63cdd5"], "status": "REASONED"},
    "signup": {"text": "Unauthenticated /signup and /signin, their v4.0.0 cookie forms and scoped /ns/.../ac/... paths are intentional; every HTTP signup form reaches the core check that refuses an access method with no SIGNUP, so omit SIGNUP to prevent public registration and test refusal beside a provisioned sign-in. RPC signup was not traced.", "components": ["docs", "pinned"], "sources": ["docs:sfdfa4e63cdd5", "docs:scc00d3d3618d", "docs:sac0752ff1726", "pinned:s6ddbe030cea1", "pinned:s1c21ede08712", "pinned:s0a950c71cc01", "pinned:saa6be90fd793", "pinned:se50982814d76"], "status": "REASONED"},
    "signup-3x": {"text": "At v3.3.5 the files read register only the /signin and /signup routes, with no cookie routes and no scoped-path rewrite, and the /signup handler calls the same core signup check as v4.0.0. Whether another v3.3.5 file registers cookie or scoped routes, and whether RPC signup reaches the check, is not established.", "components": ["pinned-3x", "pinned"], "sources": ["pinned-3x:sc840084091cd", "pinned-3x:s65828a4dd9ea", "pinned:se50982814d76"], "status": "REASONED"},
    "rate-limit": {"text": "At v4.0.0 the per-address HTTP limit on sign-in, sign-up and Basic-auth requests is off by default (SURREAL_HTTP_AUTH_RATE_LIMIT_ENABLED false; burst and per-minute 60 once on), so the release page's Basic-auth rate limit applies only when enabled; a request with no derivable client address is not limited.", "components": ["pinned", "docs"], "sources": ["pinned:s57c8f0d7c045", "pinned:s0d453e52834e", "docs:sac0752ff1726"], "status": "REASONED"},
    "rate-limit-3x": {"text": "At v3.3.5 the HTTP authentication limiter has the same setting and defaults but limits only POST requests to /signin and /signup with a derivable client address, whatever headers they carry; it has no cookie, refresh or sign-out path. It lacks v4.0.0's case for other requests carrying Basic credentials, so as this guide's reading of v3.3.5 source those are not rate-limited even when it is enabled.", "components": ["pinned-3x", "pinned"], "sources": ["pinned-3x:s10ad47f37dcd", "pinned:s57c8f0d7c045", "pinned:s0d453e52834e"], "status": "REASONED"},
    "permission-advisories": {"text": "v4.0.0 fixes advisories affecting versions below 4.0.0 on table, field and role controls: GHSA-5xcv-fm6g-4hf3, GHSA-fh2q-8f75-m4h6, GHSA-qh3v-rr48-x3cq, GHSA-ffvm-mqh3-7986, GHSA-wjh3-m4pv-q6cp, GHSA-cff7-q66j-4hc8, GHSA-3rcm-c653-wgmr, GHSA-ff2q-h4x7-cpj4, GHSA-pvv9-h693-m8r4, GHSA-m887-2246-mgw3 and GHSA-3287-hpm5-3f8r; do not rely on those controls on an earlier release.", "components": ["advisories"], "sources": ["advisories:s1b98c24eb665", "advisories:sb541fcd902da", "advisories:s2da32614f366", "advisories:s8064745de0e0", "advisories:s2f3b208498de", "advisories:se50ef588388b", "advisories:se5f6e6699691", "advisories:s29b6dab1b6dd", "advisories:sb7209bfe440d", "advisories:s6363f9220ffe", "advisories:s1f98319f76ae"], "status": "REASONED"},
    "scope-history": {"text": "Use DEFINE ACCESS TYPE RECORD; legacy DEFINE SCOPE was deprecated in 2.x and removed in 3.0.", "components": ["scope-old", "scope-removed"], "sources": ["scope-old:s5a6f3aad8f24", "scope-removed:s5a6f3aad8f24"], "status": "REASONED"},
    "access-types": {"text": "DEFINE ACCESS also supports JWT and per-client BEARER keys; standalone JWT creates system-level sessions, while RECORD WITH JWT retains record permissions.", "components": ["docs"], "sources": ["docs:sdaa9a636537a", "docs:sfdfa4e63cdd5", "docs:s048fd6bd1f3e"], "status": "REASONED"},
    "jwt-checks": {"text": "Verify token algorithm/key or JWKS, issuer and audience; native AUDIENCE is available since 3.3.0, so set it at the v4.0.0 basis, and check the issuer in AUTHENTICATE as the JWT page's example does. Compare invalid tokens against a valid control.", "components": ["docs", "audience"], "sources": ["docs:s048fd6bd1f3e", "audience:s048fd6bd1f3e"], "status": "REASONED"},
    "capability-all": {"text": "allow-all and deny-all default off; prefer deny-all with narrow route, RPC-method and function allowances. As this guide's reading of v4.0.0 source, deny-all alone leaves every HTTP route, RPC method and MCP tool allowed, as allow-http, allow-rpc and allow-mcp default to all targets; no run confirmed it, so pass explicit allow-http and allow-rpc lists.", "components": ["docs", "pinned"], "sources": ["docs:sc798cc43c457", "docs:scc00d3d3618d", "pinned:scce5b37cc67e", "pinned:sb983f262eea6", "pinned:s41f93c8f1044", "pinned:s10eff64ec263", "pinned:sc2c677a2fedc"], "status": "REASONED"},
    "capability-health": {"text": "When the Verify block's health check should pass under deny-all, include health in the allow-http list: the HTTP allow getter returns a named list as given, the route parser reads health as the health route, and /health refuses a route that is not allowed, which the HTTP protocol page says answers 403.", "components": ["pinned", "docs"], "sources": ["pinned:s41f93c8f1044", "pinned:s02c701807dae", "pinned:s538897c5bacc", "docs:scc00d3d3618d"], "status": "REASONED"},
    "mcp-advisory": {"text": "GHSA-cr79-9p8r-p5wx (high; affecting versions below 4.0.0, patched in 4.0.0) reports MCP tool identifier validation permitting statement injection, with arbitrary SQL query execution through MCP tool invocation; it bears on MCP tools staying allowed under deny-all.", "components": ["advisories"], "sources": ["advisories:s390dd974a89c"], "status": "REASONED"},
    "capability-mcp-3x": {"text": "The v3.3.5 capability files read define allow-rpc and allow-http with the same empty default but no allow-mcp or deny-mcp list; their only MCP target is the mcp HTTP route. surreal mcp is behind the mcp feature; its arguments are named through the cli::mcp module (use mcp::McpCommandArguments;), which was not read, nor was its MCP crate, so whether anything else gates MCP tools is not established.", "components": ["pinned-3x"], "sources": ["pinned-3x:s7144f593a339", "pinned-3x:sb555f9745ad7", "pinned-3x:sd82d608cc2e1", "pinned-3x:s5ef899492471"], "status": "REASONED"},
    "capability-net": {"text": "Network access is denied by default; restrict http::* and JWKS destinations and retain external egress protections against SSRF.", "components": ["docs"], "sources": ["docs:sc798cc43c457"], "status": "REASONED"},
    "capability-functions": {"text": "Functions are allowed by default; a bare allow-funcs broadens access beyond narrow named allowances.", "components": ["docs"], "sources": ["docs:sc798cc43c457"], "status": "REASONED"},
    "capability-scripting": {"text": "Embedded scripting defaults off; enable it only when required.", "components": ["docs"], "sources": ["docs:sc798cc43c457"], "status": "REASONED"},
    "capability-guests": {"text": "Guest access defaults off; capabilities govern what an authorized query may do independently of authentication.", "components": ["docs"], "sources": ["docs:sc798cc43c457"], "status": "REASONED"},
    "capability-precedence": {"text": "A category allow list overrides deny-all or a bare category deny, and deny wins at equal specificity; between list entries a deny entry wins over any allow entry, so a narrower allow does not override a broader deny, as the capabilities page's own example and this guide's reading of v4.0.0 source agree.", "components": ["docs", "pinned"], "sources": ["docs:sc798cc43c457", "pinned:sd1dcb148f996", "pinned:s6a13d5749f9a", "pinned:s6f5b41199da6"], "status": "REASONED"},
    "capability-advisories": {"text": "v4.0.0 fixes capability bypasses affecting versions below 4.0.0: GHSA-5w6j-qm42-4rc2, GHSA-fq69-wr4w-v3gm and GHSA-q83r-f38r-rwvj; the 4.0 release page lists 23 advisories, of which this guide names 16 and lists 7 more.", "components": ["advisories", "docs"], "sources": ["advisories:s28cd26dc0103", "advisories:sad31e9ec665b", "advisories:s9c8e76544223", "docs:sac0752ff1726"], "status": "REASONED"},
    "advisories-3x": {"text": "v3.3.5 is in all 23 affected ranges of the 4.0 advisories; exposure depends on prerequisites. GHSA-q83r-f38r-rwvj needs experimental Surrealism, authenticated module upload and invoke rights, and that the operator relies on deny_net (with a broad or attacker-influenceable allow_net) for egress control. GHSA-m9qr-4rcq-3jhc is \"not remote/black-box triggerable.\" Crate-to-server mapping is inference.", "components": ["advisories", "docs"], "sources": ["advisories:sd74a20d357b6", "advisories:s28cd26dc0103", "advisories:sad31e9ec665b", "advisories:s9c8e76544223", "advisories:s1b98c24eb665", "advisories:sb541fcd902da", "advisories:s2da32614f366", "advisories:s8064745de0e0", "advisories:s2f3b208498de", "advisories:se50ef588388b", "advisories:se5f6e6699691", "advisories:s29b6dab1b6dd", "advisories:sb7209bfe440d", "advisories:s6363f9220ffe", "advisories:s1f98319f76ae", "advisories:s390dd974a89c", "advisories:sd6a62a692fe6", "advisories:se028de7b3f26", "advisories:s4846cdc74b47", "advisories:s7b253e6289d7", "advisories:s3a93dc5e0a90", "advisories:s03e87b1aeb09", "advisories:sc475ce490938", "docs:sac0752ff1726"], "status": "REASONED"},
    "tls": {"text": "web-crt and web-key provide native HTTPS; SurrealDB documents TLS termination at a load balancer or reverse proxy, and reaching the instance only over a tailnet is this guide's own suggestion.", "components": ["docs"], "sources": ["docs:s2eb33a763ea4", "docs:sae73137661aa"], "status": "REASONED"},
    "mfa": {"text": "Whether SurrealDB v4.0.0 has a native second factor is not established, as no page read addresses one; require IdP or administrative-gateway MFA and prevent direct-origin bypass.", "components": ["docs"], "sources": ["docs:sdaa9a636537a", "docs:sae73137661aa"], "status": "REASONED"},
    "verify-inventory": {"text": "Inventory 8000 on loopback/private addresses; at v4.0.0 a /health 200 means the route is allowed, the memory-health failure condition was not met (the check is disabled, or the guard has not stayed engaged for its configured period) and storage answers, not authentication or finished startup; /status is liveness and /ready follows startup and any configured heartbeat budget.", "components": ["docs", "pinned"], "sources": ["docs:s2eb33a763ea4", "docs:scc00d3d3618d", "pinned:s538897c5bacc", "pinned:s67ee52a23e57"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "Compare INFO FOR DB without credentials and with a system-user JWT on the same NS/DB: exposed auth-off returns info; fixed denies anonymous access and returns authenticated OK data.", "components": ["docs"], "sources": ["docs:scc00d3d3618d", "docs:s51100e115b41"], "status": "REASONED", "verify": [1]},
    "verify-auth-limits": {"text": "Test direct origin and HTTPS; HTTP 200, missing database, disabled route, proxy rejection or transport failure alone proves no authorization control or record permissions.", "components": ["docs"], "sources": ["docs:scc00d3d3618d", "docs:s51100e115b41"], "status": "REASONED", "verify": [1]},
    "verify-origin": {"text": "Any HTTP answer from an untrusted-network origin probe proves reachability; a gateway result alone does not establish origin isolation.", "components": ["docs"], "sources": ["docs:sae73137661aa"], "status": "REASONED", "verify": [2]},
    "verify-tls": {"text": "Validate the certificate chain at every TLS termination using normal trust checks, never -k.", "components": ["docs"], "sources": ["docs:sae73137661aa"], "status": "REASONED", "verify": [1, 2]}
  }
}
````
<!-- version-basis:end -->
