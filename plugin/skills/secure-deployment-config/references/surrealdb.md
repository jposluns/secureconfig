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

Written against SurrealDB server and image v4.0.0, SurrealDB native AUDIENCE minimum 3.3, SurrealDB SCOPE deprecation 2.x, SurrealDB SCOPE removal 3.0, GNU Bash reference manual bash-5.3, Linux procfs manual man-pages-6.19, and Linux ptrace manual man-pages-6.19; 3 further sources carry no recorded version. Metadata reviewed 2026-11-04; documentation checked September 2026. The guide records 34 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

Since SurrealDB 2.0.0, authentication is enabled by default and the CLI binds `127.0.0.1:8000` rather than
`0.0.0.0` (2.0.0 removed the old `--auth` flag, added `--unauthenticated`, and changed the bind default);
on older releases neither held, so pin your version. Even on a current version, a laptop demo becomes a real
exposure the moment the same command runs on a routable server with `--unauthenticated` or a widened bind
carried over.

## 1. Root user and authenticated mode

At v4.0.0, two different programs answer to `surreal`. The database executable defines a `start` command and
no `db` command, so it takes `surreal start`. The Surreal CLI launcher, which the vendor's install script
installs as `surreal` with, by default, the database as a pinned component, takes `surreal db start` and passes everything
after the component name to the database unchanged. The launcher's pages document no bare `surreal start`, and
say "A name that is not a component, such as `surreal foo`, runs a `surreal-foo` from your `PATH` if one exists,
and reports an unknown component otherwise." As this guide's inference, under the launcher `surreal start`
does not start the database, and could pass the block's environment to a `surreal-start` found on `PATH`.
So the block below uses `surreal db start`, for the documented launcher install; where the standalone database
executable is installed as `surreal`, drop `db`. The container example in section 2 keeps `start`, because each
image stage's `ENTRYPOINT` is the database executable itself.

`surreal db start` takes `--user`/`-u` and `--pass`/`-p` (also `SURREAL_USER`/`SURREAL_PASS`) for, in the
v4.0.0 help text, "the initial database root user. Only if no other root user exists": they initialize that
user when none exists, and do not disable authentication or rotate an existing root password. At v4.0.0 both
flags refuse an empty value (`value_parser = clap::builder::NonEmptyStringValueParser::new()`), and the server
core refuses an empty or whitespace-only username or password before it creates the user
(`!user.trim().is_empty() && !pass.trim().is_empty()`). Whether an empty `SURREAL_PASS` in the environment
reaches those checks or counts as unset is not established at v4.0.0; the block refuses an empty password itself.
A root user can also come from the SurrealQL file that `--import-file` (`SURREAL_IMPORT_FILE`) runs at start:
the server runs that import first, "so that an import which supplies root users suppresses creation of the CLI
bootstrap user", so treat such a file as a credential.

At v4.0.0, `--help` no longer prints credential values: the password argument sets `hide_env_values = true`,
and the executable applies `arg.hide_env_values(true)` to every argument of every command. Before 4.0.0 it
could: GHSA-whfh-76h8-2r66, "CLI help output prints the values of SURREAL_PASS and SURREAL_TOKEN" (low;
affected `< 4.0.0`, patched `4.0.0`), names `surreal start` among the commands and was reproduced on v3.2.4.

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

At v4.0.0 a directory a 3.x release wrote is refused unless the operator opts in. The error in the source says the in-place upgrade "is experimental and is refused by default", that "a 3.x release cannot open them afterwards", and to "take a backup and set SURREAL_EXPERIMENTAL_UPGRADE_FROM_3X=true to opt in to the experimental upgrade". This guide gives only that `true` value; which other values the server accepts is not established at v4.0.0.

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

System users (`DEFINE USER`) exist at three levels: root (visibility across every namespace and
database), namespace, and database, each assigned a role of `OWNER`, `EDITOR`, or `VIEWER`. The docs
warn plainly that "a root system user is not restricted by permissions at all, so it is the wrong
credential to put in an application"; give trusted backend administration a narrowly scoped system user. But
system users at EVERY level are governed by RBAC and bypass table and field `PERMISSIONS` entirely, so a
namespace- or database-level system user is not a substitute for record-level isolation: when application
users need database-enforced row or field permissions, use record users (below), not a system user.

Record users are different: they are rows in your own tables, authenticated through
`DEFINE ACCESS ... TYPE RECORD` with custom `SIGNUP` and `SIGNIN` logic. Record users get no access
beyond what a `PERMISSIONS` clause on a table or field grants them, the same
rules-are-the-security model as Firebase and Supabase ([firebase-supabase.md](firebase-supabase.md)):
the permissions page says "omitting `PERMISSIONS` results in a `PERMISSIONS NONE`", so a table with no
`PERMISSIONS` clause grants a record user nothing by default. The `/signup` and `/signin`
HTTP endpoints accept unauthenticated credentials by design. At v4.0.0 so do `/signup/cookie` and
`/signin/cookie`, which `--cookie-auth` with an explicit `--allow-origin` list enables, and scoped paths such as
`/ns/{ns}/db/{db}/ac/{ac}/signup`, which the server rewrites to the unscoped route before any layer sees them.
A `SIGNUP` clause can permit public self-registration that root credentials do not restrict, so omit `SIGNUP`
when self-registration is unwanted and test that it is refused while a provisioned account still signs in.
At v4.0.0 every HTTP signup form calls the same core function, which refuses an access method with no `SIGNUP`
(`bail!(AuthError::AccessRecordNoSignup)`). Whether RPC `signup` reaches that check was not traced at v4.0.0,
so where `/rpc` is allowed, test the refusal there too.

At v4.0.0 the per-address limit on sign-in and sign-up requests, and on requests carrying Basic credentials, is
off by default: `lazy_env_parse!("SURREAL_HTTP_AUTH_RATE_LIMIT_ENABLED", bool, false)`. The 4.0 release page
says "Basic authentication is rate-limited", which as this guide reads the source holds only once the limiter is
enabled. Its burst and per-minute rate then default to 60, and a request with no client address the server can
work out is not limited. Which values enable it is not established at v4.0.0.

v4.0.0 fixes these advisories on table, field and role controls, each affecting versions below 4.0.0 and
patched in 4.0.0, so do not rely on those controls on an earlier release:

- GHSA-5xcv-fm6g-4hf3 (high): "Quoted Computed-Field Formatter Bypasses Field-Level SELECT Permissions".
- GHSA-fh2q-8f75-m4h6 (high): "REFERENCE ON DELETE CASCADE/UNSET/CUSTOM bypasses target table PERMISSIONS FOR delete/update".
- GHSA-qh3v-rr48-x3cq (medium): "Authenticated Export Permission Bypass".
- GHSA-ffvm-mqh3-7986 (medium): "SurrealDB 3.2.4 allows FOR loop variables named $access, $auth, and $token to shadow the authenticated session values used by table permission expressions."
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
allowed by default, and scripting (`--allow-scripting`) and guest access (`--allow-guests`) default off. The
capabilities page says "the more specific capabilities prevail over the less specific" and that at the same level
of specificity denies prevail. As this guide's reading of the v4.0.0 source, that holds between layers: a
category's allow list overrides `--deny-all` or a bare category deny. It does not hold between list entries: a
function is allowed only when an allow entry matches it and no deny entry does
(`self.allow_funcs.matches(target) && !self.deny_funcs.matches(target)`), so allowing `http::get` while denying
`http` refuses `http::get`. The capabilities page's own example agrees: under `--deny-funcs crypto
--allow-funcs crypto::md5`, "all four are denied, because a specific deny wins over any allow."

Prefer `--deny-all` with narrow explicit allowances for the routes, RPC methods, and functions you need rather
than a bare `--allow-funcs` or `--allow-net`, keep embedded scripting off unless required, and confirm each
default against your pinned version. What `--deny-all` alone does to HTTP routes is not established at v4.0.0.
Under `--deny-all` the route getter allows only what `--allow-http` lists, but `--allow-http` has a default
value that its parser reads as every route, and no run showed which applies. So list the routes you use with
`--allow-http`, `/health`, `/signin`, `/signup` and `/sql` included where needed. The HTTP protocol page says a
denied `health` route answers `403`, which the Verify block's health check reports as inconclusive.

v4.0.0 also fixes these capability bypasses, each affecting versions below 4.0.0 and patched in 4.0.0:

- GHSA-5w6j-qm42-4rc2 (high): "JavaScript Built-in Bridge Bypasses Function Capability Enforcement".
- GHSA-fq69-wr4w-v3gm (high): "JavaScript Query Bridge Bypasses Arbitrary-Query Subject Gate".
- GHSA-q83r-f38r-rwvj (high): "Surrealism WASI socket allowlist ignores deny_net, enabling SSRF via hostname resolving to a private IP".

The 4.0 release page lists 23 advisories; this guide names the 10 that bear on its statements and counts the
other 13 only.

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
engaged or the storage backend fails its health check, so a `200` shows neither authentication nor finished
startup. `/status` is the process and listener liveness check, and `/ready` returns `200` only once startup,
import and credentials included, has finished. Confirm the TLS certificate chain wherever
TLS terminates with normal validation (a trusted CA for private PKI); never use `-k`.
Paste the JWT alone at the first block's hidden prompt: a multi-line paste leaves every line after the first for your
shell to run.

## Sources (checked September 2026)

- SurrealDB CLI, `surreal db start` (checked November 2026): https://surrealdb.com/docs/reference/cli/db/commands/start
- Surreal CLI launcher: `surreal <component> <command>` passes everything after the component name on unchanged, and the install script installs `surreal` with the database as a pinned component (checked November 2026): https://surrealdb.com/docs/explore/cli
- Surreal CLI components: a name that is not a component runs a `surreal-<name>` from `PATH`, and `SURREAL_*` variables other than `SURREAL_CLI_*` belong to the database (checked November 2026): https://surrealdb.com/docs/explore/cli/components
- SurrealDB 4.0 release notes (the `db` component, RocksDB removal, the 3.x upgrade opt-in, cookie endpoints, "Basic authentication is rate-limited" and 23 advisories) (checked November 2026): https://surrealdb.com/releases/4.0
- GNU Bash reference manual, bash-5.3 (checked October 2026), prefix assignments 3872-3878: https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n3872
- Linux man-pages `proc_pid_environ(5)`, tag man-pages-6.19 (file header says "unreleased"; version identity rests on the tag) (checked October 2026): initial environment 12-15 https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/tree/man/man5/proc_pid_environ.5?h=man-pages-6.19#n12. The same `proc_pid_environ(5)` page, tag man-pages-6.19 (file header says "unreleased"; version identity rests on the tag) (checked October 2026): later modifications 26-36 https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/tree/man/man5/proc_pid_environ.5?h=man-pages-6.19#n26. The same `proc_pid_environ(5)` page, tag man-pages-6.19 (file header says "unreleased"; version identity rests on the tag) (checked October 2026): procfs access check 43-47 https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/tree/man/man5/proc_pid_environ.5?h=man-pages-6.19#n43
- Linux man-pages `ptrace(2)`, tag man-pages-6.19 (file header says "unreleased"; version identity rests on the tag) (checked October 2026): ptrace access factors 2519-2533 https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/tree/man/man2/ptrace.2?h=man-pages-6.19#n2519
- SurrealDB v4.0.0 `start` root user and password: `--username`/`--user`/`-u` or `SURREAL_USER` and `--password`/`--pass`/`-p` or `SURREAL_PASS`, each refusing an empty value, the password's value hidden from `--help`, no stdin form in the files read (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cli/start.rs#L178-L205
- SurrealDB v4.0.0 `--unauthenticated` flag, bound to `SURREAL_UNAUTHENTICATED` (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L56-L59
- SurrealDB v4.0.0 `--bind`/`-b` (`SURREAL_BIND`) default `127.0.0.1:8000` (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cli/start.rs#L220-L223
- SurrealDB `docker/Dockerfile` sets `ENV SURREAL_BIND="0.0.0.0:8000"` in each runtime stage (L78, L106, L141, L169), each followed by `ENTRYPOINT ["/surreal"]` with no `CMD`, shown here for the `prod-ci` stage (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/docker/Dockerfile#L88-L111
- SurrealDB v4.0.0 database executable: the `start` command, with no `db` command (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cli/mod.rs#L144-L146
- SurrealDB v4.0.0 help: no argument's environment value shown, in any command (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cli/mod.rs#L427-L431
- SurrealDB v4.0.0 SurrealKV refusal of a directory a 3.x release wrote, unless `SURREAL_EXPERIMENTAL_UPGRADE_FROM_3X=true` (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/kvs-surrealkv/src/lib.rs#L336-L348
- SurrealDB v4.0.0 core root credentials: empty or whitespace-only values refused, and a root user created only when none exists (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/core/src/kvs/ds.rs#L3543-L3589
- SurrealDB v4.0.0 `--import-file` (`SURREAL_IMPORT_FILE`) (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L67-L70 and the import running before credentials: https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L1326-L1332
- SurrealDB v4.0.0 capability getters: HTTP routes under `--deny-all` (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L498-L535 and specific function denies applied on top of allows: https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L597-L607
- SurrealDB v4.0.0 capability checks: function target matching (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/rpc/src/capabilities/mod.rs#L43-L55 and allow-and-not-deny: https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/rpc/src/capabilities/mod.rs#L1158-L1160
- SurrealDB v4.0.0 `/health`, and `/ready` (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/health.rs#L10-L36 and https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/ready.rs#L15-L23
- SurrealDB v4.0.0 `/signup` and `/signup/cookie` handlers calling core signup (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/signup.rs#L43-L75 and https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/signup.rs#L133-L148
- SurrealDB v4.0.0 `/signin` and `/signin/cookie` routes (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/signin.rs#L45-L54
- SurrealDB v4.0.0 scoped `/ns/.../db/.../ac/...` paths rewritten before the router (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/scope.rs#L1-L35
- SurrealDB v4.0.0 core signup refusing an access method with no `SIGNUP` (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/core/src/iam/signup.rs#L213-L215
- SurrealDB v4.0.0 HTTP authentication rate limit, off by default, burst and per-minute rate 60 (pinned tag v4.0.0) (checked November 2026): https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cnf/mod.rs#L290-L304 and the requests it covers: https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/rate_limit.rs#L244-L280
- SurrealDB CLI, `surreal db sql` (checked November 2026): https://surrealdb.com/docs/reference/cli/db/commands/sql
- SurrealDB security overview (checked November 2026): https://surrealdb.com/docs/learn/security
- SurrealDB authentication overview (checked November 2026): https://surrealdb.com/docs/learn/security/authentication/overview
- SurrealDB security best practices (checked November 2026): https://surrealdb.com/docs/learn/security/best-practices/security-best-practices
- SurrealDB capabilities (`--allow-all`/`--deny-all`, net denied, functions allowed, scripting/guests off, specificity + deny-wins, a specific deny winning over any allow) (checked November 2026): https://surrealdb.com/docs/learn/security/authorization/capabilities
- SurrealDB permissions and row-level security (system users bypass table/field PERMISSIONS; omitting `PERMISSIONS` results in `PERMISSIONS NONE`) (checked November 2026): https://surrealdb.com/docs/learn/security/authorization/permissions-and-row-level-security
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
- SurrealDB advisory GHSA-ffvm-mqh3-7986, FOR loop variables named `$access`, `$auth` and `$token` shadowing the session values that table permission expressions use (medium; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-ffvm-mqh3-7986
- SurrealDB advisory GHSA-m887-2246-mgw3, "VIEWER role can define tables implicitly via CREATE on a non-STRICT database" (low; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-m887-2246-mgw3
- SurrealDB advisory GHSA-3287-hpm5-3f8r, DDL statements bypassing namespace and database implicit-creation authorization (medium; affected `< 4.0.0`, patched `4.0.0`) (checked November 2026): https://github.com/surrealdb/surrealdb/security/advisories/GHSA-3287-hpm5-3f8r


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- pinned: SurrealDB server and image (v4.0.0)
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
- bind-default (REASONED; defaults, pinned): Since 2.0.0 the CLI defaults to 127.0.0.1:8000; v4.0.0 --bind/-b and SURREAL_BIND retain that loopback default.
- command-form (REASONED; pinned, docs): At v4.0.0 the database executable takes start and defines no db command; the Surreal CLI launcher runs it as surreal db start, passing the rest unchanged. As this guide's inference, under the launcher surreal start does not start the database, so the host block uses surreal db start and the image keeps start.
- root-bootstrap (REASONED; docs, pinned): User/password flags or SURREAL_USER/PASS initialize a root only when none exists; they neither disable authentication nor rotate an existing password. At v4.0.0 the flags refuse empty values, core also refuses whitespace-only ones, and an import file that supplies root users suppresses the flag user.
- root-input (REASONED; pinned, bash, procfs, ptrace): No v4.0.0 server file read has a stdin password form; prompt and use a Bash command-local environment assignment, not argv. As this guide's assessment, the initial server environment may be exposed to the same account and root when the procfs ptrace check permits; an inheriting process may expose it the same way while it runs; treat it as exposed to that account and root while the server runs.
- help-values (REASONED; pinned, advisories): Before 4.0.0 --help could print SURREAL_PASS and SURREAL_TOKEN values (GHSA-whfh-76h8-2r66, low, affecting versions below 4.0.0, patched in 4.0.0); at v4.0.0 the start password sets hide_env_values and the executable hides every argument's environment value in help.
- environment (REASONED; docs, pinned): The clean-Bash block clears user/password variables and rejects other inherited SURREAL_* options, including auth and bind overrides, the 3.x upgrade opt-in and the launcher's SURREAL_CLI_* variables.
- launcher-unknowns (REASONED; docs): Whether the Surreal CLI launcher stays running as the server's parent, or passes SURREAL_PASS on unchanged, is not established at v4.0.0; as this guide's assessment, treat a resident launcher as exposed like the server and confirm the root user by signing in.
- storage-upgrade (REASONED; pinned, docs): v4.0.0 removes the RocksDB engine; the docs read rocksdb:// as a deprecated spelling of surrealkv://, and the block names surrealkv:/data/mydb.db. A 3.x directory is refused unless SURREAL_EXPERIMENTAL_UPGRADE_FROM_3X=true, which the block cannot carry; convert it as a separate step after a backup. The server path check was not read.
- unauthenticated (REASONED; docs, pinned): --unauthenticated/SURREAL_UNAUTHENTICATED gives guests OWNER-equivalent access; never carry it onto a remotely reachable deployment.
- docker-bind (REASONED; pinned): v4.0.0 image stages set SURREAL_BIND=0.0.0.0:8000 without CMD; start without an override listens on all container IPv4 interfaces, requiring private network or loopback publication. Whether published images use that file is not established.
- private-network (REASONED; docs): Widen host binds only deliberately to private addresses; internal-service databases should have no public interface.
- system-users (REASONED; docs): Root, namespace and database system users use OWNER/EDITOR/VIEWER RBAC; all bypass table/field PERMISSIONS, so scoped system users do not supply record isolation.
- record-users (REASONED; docs): Record users authenticate through DEFINE ACCESS TYPE RECORD SIGNUP/SIGNIN logic and receive only explicit table/field permissions; omitting PERMISSIONS results in PERMISSIONS NONE.
- signup (REASONED; docs, pinned): Unauthenticated /signup and /signin, their v4.0.0 cookie forms and scoped /ns/.../ac/... paths are intentional; every HTTP signup form reaches the core check that refuses an access method with no SIGNUP, so omit SIGNUP to prevent public registration and test refusal beside a provisioned sign-in. RPC signup was not traced.
- rate-limit (REASONED; pinned, docs): At v4.0.0 the per-address HTTP limit on sign-in, sign-up and Basic-auth requests is off by default (SURREAL_HTTP_AUTH_RATE_LIMIT_ENABLED false; burst and per-minute 60 once on), so the release page's Basic-auth rate limit applies only when enabled; a request with no derivable client address is not limited.
- permission-advisories (REASONED; advisories): v4.0.0 fixes advisories affecting versions below 4.0.0 on table, field and role controls: GHSA-5xcv-fm6g-4hf3, GHSA-fh2q-8f75-m4h6, GHSA-qh3v-rr48-x3cq, GHSA-ffvm-mqh3-7986, GHSA-m887-2246-mgw3 and GHSA-3287-hpm5-3f8r; do not rely on those controls on an earlier release.
- scope-history (REASONED; scope-old, scope-removed): Use DEFINE ACCESS TYPE RECORD; legacy DEFINE SCOPE was deprecated in 2.x and removed in 3.0.
- access-types (REASONED; docs): DEFINE ACCESS also supports JWT and per-client BEARER keys; standalone JWT creates system-level sessions, while RECORD WITH JWT retains record permissions.
- jwt-checks (REASONED; docs, audience): Verify token algorithm/key or JWKS, issuer and audience; native AUDIENCE is available since 3.3.0, so set it at the v4.0.0 basis, and check the issuer in AUTHENTICATE as the JWT page's example does. Compare invalid tokens against a valid control.
- capability-all (REASONED; docs, pinned): allow-all and deny-all default off; prefer deny-all with narrow route, RPC-method and function allowances. What deny-all alone does to HTTP routes is not established at v4.0.0, because allow-http has a default, so list needed routes, /health included.
- capability-net (REASONED; docs): Network access is denied by default; restrict http::* and JWKS destinations and retain external egress protections against SSRF.
- capability-functions (REASONED; docs): Functions are allowed by default; a bare allow-funcs broadens access beyond narrow named allowances.
- capability-scripting (REASONED; docs): Embedded scripting defaults off; enable it only when required.
- capability-guests (REASONED; docs): Guest access defaults off; capabilities govern what an authorized query may do independently of authentication.
- capability-precedence (REASONED; docs, pinned): A category allow list overrides deny-all or a bare category deny, and deny wins at equal specificity; between list entries a deny entry wins over any allow entry, so a narrower allow does not override a broader deny, as the capabilities page's own example and this guide's reading of v4.0.0 source agree.
- capability-advisories (REASONED; advisories, docs): v4.0.0 fixes capability bypasses affecting versions below 4.0.0: GHSA-5w6j-qm42-4rc2, GHSA-fq69-wr4w-v3gm and GHSA-q83r-f38r-rwvj; the 4.0 release page lists 23 advisories, of which this guide names 10 and counts 13.
- tls (REASONED; docs): web-crt and web-key provide native HTTPS; SurrealDB documents TLS termination at a load balancer or reverse proxy, and reaching the instance only over a tailnet is this guide's own suggestion.
- mfa (REASONED; docs): Whether SurrealDB v4.0.0 has a native second factor is not established, as no page read addresses one; require IdP or administrative-gateway MFA and prevent direct-origin bypass.
- verify-inventory (REASONED; docs, pinned): Inventory 8000 on loopback/private addresses; at v4.0.0 a /health 200 means the route is allowed, the memory guard is not engaged and storage answers, not authentication or finished startup; /status is liveness and /ready follows startup.
- verify-auth (REASONED; docs): Compare INFO FOR DB without credentials and with a system-user JWT on the same NS/DB: exposed auth-off returns info; fixed denies anonymous access and returns authenticated OK data.
- verify-auth-limits (REASONED; docs): Test direct origin and HTTPS; HTTP 200, missing database, disabled route, proxy rejection or transport failure alone proves no authorization control or record permissions.
- verify-origin (REASONED; docs): Any HTTP answer from an untrusted-network origin probe proves reachability; a gateway result alone does not establish origin isolation.
- verify-tls (REASONED; docs): Validate the certificate chain at every TLS termination using normal trust checks, never -k.

````json
{
  "schema": 1,
  "checked": "2026-11-04",
  "documentation_checked": "2026-09",
  "body_sha256": "87ee6929c82067d815236edd2b99f5be74dac089ff7a884a8ee4a6b32fe6863c",
  "components": {
    "pinned": {
      "name": "SurrealDB server and image",
      "basis": "v4.0.0",
      "sources": {
        "s325ec1bdaeca": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cli/start.rs#L178-L205",
        "s025b59b3dab9": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L56-L59",
        "sd341f6f1f6cb": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cli/start.rs#L220-L223",
        "sa4c7bc20d655": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/docker/Dockerfile#L88-L111",
        "s29933d0b75dd": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cli/mod.rs#L144-L146",
        "sc48298a83d5b": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cli/mod.rs#L427-L431",
        "s315fd2b3211f": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/kvs-surrealkv/src/lib.rs#L336-L348",
        "s68c349d06271": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/core/src/kvs/ds.rs#L3543-L3589",
        "s85b6558fdf7d": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L67-L70",
        "se2b9738f37cc": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L1326-L1332",
        "sc07a54a13543": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L498-L535",
        "sd1dcb148f996": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/dbs/mod.rs#L597-L607",
        "s6a13d5749f9a": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/rpc/src/capabilities/mod.rs#L43-L55",
        "s6f5b41199da6": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/rpc/src/capabilities/mod.rs#L1158-L1160",
        "sf3cc586861b8": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/health.rs#L10-L36",
        "s67ee52a23e57": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/ready.rs#L15-L23",
        "s6ddbe030cea1": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/signup.rs#L43-L75",
        "s1c21ede08712": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/signup.rs#L133-L148",
        "s0a950c71cc01": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/signin.rs#L45-L54",
        "saa6be90fd793": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/scope.rs#L1-L35",
        "se50982814d76": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/core/src/iam/signup.rs#L213-L215",
        "s57c8f0d7c045": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/cnf/mod.rs#L290-L304",
        "s0d453e52834e": "https://github.com/surrealdb/surrealdb/blob/v4.0.0/surrealdb/server/src/ntw/rate_limit.rs#L244-L280"
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
        "sae73137661aa": "https://surrealdb.com/docs/learn/security/best-practices/security-best-practices",
        "sc798cc43c457": "https://surrealdb.com/docs/learn/security/authorization/capabilities",
        "sb9c3a17a2998": "https://surrealdb.com/docs/learn/security/authorization/permissions-and-row-level-security",
        "sfdfa4e63cdd5": "https://surrealdb.com/docs/reference/query-language/statements/define/access/record",
        "scc00d3d3618d": "https://surrealdb.com/docs/reference/rest-api/http-protocol",
        "s51100e115b41": "https://surrealdb.com/docs/reference/query-language/statements/info",
        "s048fd6bd1f3e": "https://surrealdb.com/docs/reference/query-language/statements/define/access/jwt",
        "se2dbccd34348": "https://surrealdb.com/docs/explore/cli",
        "s80d3b718d95d": "https://surrealdb.com/docs/explore/cli/components",
        "sac0752ff1726": "https://surrealdb.com/releases/4.0"
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
        "s6363f9220ffe": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-m887-2246-mgw3",
        "s1f98319f76ae": "https://github.com/surrealdb/surrealdb/security/advisories/GHSA-3287-hpm5-3f8r"
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
    "bind-default": {"text": "Since 2.0.0 the CLI defaults to 127.0.0.1:8000; v4.0.0 --bind/-b and SURREAL_BIND retain that loopback default.", "components": ["defaults", "pinned"], "sources": ["defaults:se73fa9c93548", "pinned:sd341f6f1f6cb"], "status": "REASONED"},
    "command-form": {"text": "At v4.0.0 the database executable takes start and defines no db command; the Surreal CLI launcher runs it as surreal db start, passing the rest unchanged. As this guide's inference, under the launcher surreal start does not start the database, so the host block uses surreal db start and the image keeps start.", "components": ["pinned", "docs"], "sources": ["pinned:s29933d0b75dd", "pinned:sa4c7bc20d655", "docs:se2dbccd34348", "docs:s80d3b718d95d", "docs:sac0752ff1726"], "status": "REASONED"},
    "root-bootstrap": {"text": "User/password flags or SURREAL_USER/PASS initialize a root only when none exists; they neither disable authentication nor rotate an existing password. At v4.0.0 the flags refuse empty values, core also refuses whitespace-only ones, and an import file that supplies root users suppresses the flag user.", "components": ["docs", "pinned"], "sources": ["docs:s2eb33a763ea4", "pinned:s325ec1bdaeca", "pinned:s68c349d06271", "pinned:s85b6558fdf7d", "pinned:se2b9738f37cc"], "status": "REASONED"},
    "root-input": {"text": "No v4.0.0 server file read has a stdin password form; prompt and use a Bash command-local environment assignment, not argv. As this guide's assessment, the initial server environment may be exposed to the same account and root when the procfs ptrace check permits; an inheriting process may expose it the same way while it runs; treat it as exposed to that account and root while the server runs.", "components": ["pinned", "bash", "procfs", "ptrace"], "sources": ["pinned:s325ec1bdaeca", "bash:sf9757e9fd6e8", "procfs:s56aa3e840419", "procfs:s9aae2a8587f2", "procfs:sd64e43d1515a", "ptrace:sfe9fe6919d33"], "status": "REASONED"},
    "help-values": {"text": "Before 4.0.0 --help could print SURREAL_PASS and SURREAL_TOKEN values (GHSA-whfh-76h8-2r66, low, affecting versions below 4.0.0, patched in 4.0.0); at v4.0.0 the start password sets hide_env_values and the executable hides every argument's environment value in help.", "components": ["pinned", "advisories"], "sources": ["pinned:s325ec1bdaeca", "pinned:sc48298a83d5b", "advisories:sd74a20d357b6"], "status": "REASONED"},
    "environment": {"text": "The clean-Bash block clears user/password variables and rejects other inherited SURREAL_* options, including auth and bind overrides, the 3.x upgrade opt-in and the launcher's SURREAL_CLI_* variables.", "components": ["docs", "pinned"], "sources": ["docs:s2eb33a763ea4", "docs:s80d3b718d95d", "pinned:s025b59b3dab9", "pinned:sd341f6f1f6cb", "pinned:s315fd2b3211f"], "status": "REASONED"},
    "launcher-unknowns": {"text": "Whether the Surreal CLI launcher stays running as the server's parent, or passes SURREAL_PASS on unchanged, is not established at v4.0.0; as this guide's assessment, treat a resident launcher as exposed like the server and confirm the root user by signing in.", "components": ["docs"], "sources": ["docs:se2dbccd34348", "docs:s80d3b718d95d"], "status": "REASONED"},
    "storage-upgrade": {"text": "v4.0.0 removes the RocksDB engine; the docs read rocksdb:// as a deprecated spelling of surrealkv://, and the block names surrealkv:/data/mydb.db. A 3.x directory is refused unless SURREAL_EXPERIMENTAL_UPGRADE_FROM_3X=true, which the block cannot carry; convert it as a separate step after a backup. The server path check was not read.", "components": ["pinned", "docs"], "sources": ["pinned:s315fd2b3211f", "docs:s2eb33a763ea4", "docs:sac0752ff1726"], "status": "REASONED"},
    "unauthenticated": {"text": "--unauthenticated/SURREAL_UNAUTHENTICATED gives guests OWNER-equivalent access; never carry it onto a remotely reachable deployment.", "components": ["docs", "pinned"], "sources": ["docs:s2eb33a763ea4", "pinned:s025b59b3dab9"], "status": "REASONED"},
    "docker-bind": {"text": "v4.0.0 image stages set SURREAL_BIND=0.0.0.0:8000 without CMD; start without an override listens on all container IPv4 interfaces, requiring private network or loopback publication. Whether published images use that file is not established.", "components": ["pinned"], "sources": ["pinned:sa4c7bc20d655"], "status": "REASONED"},
    "private-network": {"text": "Widen host binds only deliberately to private addresses; internal-service databases should have no public interface.", "components": ["docs"], "sources": ["docs:sae73137661aa"], "status": "REASONED"},
    "system-users": {"text": "Root, namespace and database system users use OWNER/EDITOR/VIEWER RBAC; all bypass table/field PERMISSIONS, so scoped system users do not supply record isolation.", "components": ["docs"], "sources": ["docs:sdaa9a636537a", "docs:sb9c3a17a2998"], "status": "REASONED"},
    "record-users": {"text": "Record users authenticate through DEFINE ACCESS TYPE RECORD SIGNUP/SIGNIN logic and receive only explicit table/field permissions; omitting PERMISSIONS results in PERMISSIONS NONE.", "components": ["docs"], "sources": ["docs:sb9c3a17a2998", "docs:sfdfa4e63cdd5"], "status": "REASONED"},
    "signup": {"text": "Unauthenticated /signup and /signin, their v4.0.0 cookie forms and scoped /ns/.../ac/... paths are intentional; every HTTP signup form reaches the core check that refuses an access method with no SIGNUP, so omit SIGNUP to prevent public registration and test refusal beside a provisioned sign-in. RPC signup was not traced.", "components": ["docs", "pinned"], "sources": ["docs:sfdfa4e63cdd5", "docs:scc00d3d3618d", "docs:sac0752ff1726", "pinned:s6ddbe030cea1", "pinned:s1c21ede08712", "pinned:s0a950c71cc01", "pinned:saa6be90fd793", "pinned:se50982814d76"], "status": "REASONED"},
    "rate-limit": {"text": "At v4.0.0 the per-address HTTP limit on sign-in, sign-up and Basic-auth requests is off by default (SURREAL_HTTP_AUTH_RATE_LIMIT_ENABLED false; burst and per-minute 60 once on), so the release page's Basic-auth rate limit applies only when enabled; a request with no derivable client address is not limited.", "components": ["pinned", "docs"], "sources": ["pinned:s57c8f0d7c045", "pinned:s0d453e52834e", "docs:sac0752ff1726"], "status": "REASONED"},
    "permission-advisories": {"text": "v4.0.0 fixes advisories affecting versions below 4.0.0 on table, field and role controls: GHSA-5xcv-fm6g-4hf3, GHSA-fh2q-8f75-m4h6, GHSA-qh3v-rr48-x3cq, GHSA-ffvm-mqh3-7986, GHSA-m887-2246-mgw3 and GHSA-3287-hpm5-3f8r; do not rely on those controls on an earlier release.", "components": ["advisories"], "sources": ["advisories:s1b98c24eb665", "advisories:sb541fcd902da", "advisories:s2da32614f366", "advisories:s8064745de0e0", "advisories:s6363f9220ffe", "advisories:s1f98319f76ae"], "status": "REASONED"},
    "scope-history": {"text": "Use DEFINE ACCESS TYPE RECORD; legacy DEFINE SCOPE was deprecated in 2.x and removed in 3.0.", "components": ["scope-old", "scope-removed"], "sources": ["scope-old:s5a6f3aad8f24", "scope-removed:s5a6f3aad8f24"], "status": "REASONED"},
    "access-types": {"text": "DEFINE ACCESS also supports JWT and per-client BEARER keys; standalone JWT creates system-level sessions, while RECORD WITH JWT retains record permissions.", "components": ["docs"], "sources": ["docs:sdaa9a636537a", "docs:sfdfa4e63cdd5", "docs:s048fd6bd1f3e"], "status": "REASONED"},
    "jwt-checks": {"text": "Verify token algorithm/key or JWKS, issuer and audience; native AUDIENCE is available since 3.3.0, so set it at the v4.0.0 basis, and check the issuer in AUTHENTICATE as the JWT page's example does. Compare invalid tokens against a valid control.", "components": ["docs", "audience"], "sources": ["docs:s048fd6bd1f3e", "audience:s048fd6bd1f3e"], "status": "REASONED"},
    "capability-all": {"text": "allow-all and deny-all default off; prefer deny-all with narrow route, RPC-method and function allowances. What deny-all alone does to HTTP routes is not established at v4.0.0, because allow-http has a default, so list needed routes, /health included.", "components": ["docs", "pinned"], "sources": ["docs:sc798cc43c457", "docs:scc00d3d3618d", "pinned:sc07a54a13543"], "status": "REASONED"},
    "capability-net": {"text": "Network access is denied by default; restrict http::* and JWKS destinations and retain external egress protections against SSRF.", "components": ["docs"], "sources": ["docs:sc798cc43c457"], "status": "REASONED"},
    "capability-functions": {"text": "Functions are allowed by default; a bare allow-funcs broadens access beyond narrow named allowances.", "components": ["docs"], "sources": ["docs:sc798cc43c457"], "status": "REASONED"},
    "capability-scripting": {"text": "Embedded scripting defaults off; enable it only when required.", "components": ["docs"], "sources": ["docs:sc798cc43c457"], "status": "REASONED"},
    "capability-guests": {"text": "Guest access defaults off; capabilities govern what an authorized query may do independently of authentication.", "components": ["docs"], "sources": ["docs:sc798cc43c457"], "status": "REASONED"},
    "capability-precedence": {"text": "A category allow list overrides deny-all or a bare category deny, and deny wins at equal specificity; between list entries a deny entry wins over any allow entry, so a narrower allow does not override a broader deny, as the capabilities page's own example and this guide's reading of v4.0.0 source agree.", "components": ["docs", "pinned"], "sources": ["docs:sc798cc43c457", "pinned:sd1dcb148f996", "pinned:s6a13d5749f9a", "pinned:s6f5b41199da6"], "status": "REASONED"},
    "capability-advisories": {"text": "v4.0.0 fixes capability bypasses affecting versions below 4.0.0: GHSA-5w6j-qm42-4rc2, GHSA-fq69-wr4w-v3gm and GHSA-q83r-f38r-rwvj; the 4.0 release page lists 23 advisories, of which this guide names 10 and counts 13.", "components": ["advisories", "docs"], "sources": ["advisories:s28cd26dc0103", "advisories:sad31e9ec665b", "advisories:s9c8e76544223", "docs:sac0752ff1726"], "status": "REASONED"},
    "tls": {"text": "web-crt and web-key provide native HTTPS; SurrealDB documents TLS termination at a load balancer or reverse proxy, and reaching the instance only over a tailnet is this guide's own suggestion.", "components": ["docs"], "sources": ["docs:s2eb33a763ea4", "docs:sae73137661aa"], "status": "REASONED"},
    "mfa": {"text": "Whether SurrealDB v4.0.0 has a native second factor is not established, as no page read addresses one; require IdP or administrative-gateway MFA and prevent direct-origin bypass.", "components": ["docs"], "sources": ["docs:sdaa9a636537a", "docs:sae73137661aa"], "status": "REASONED"},
    "verify-inventory": {"text": "Inventory 8000 on loopback/private addresses; at v4.0.0 a /health 200 means the route is allowed, the memory guard is not engaged and storage answers, not authentication or finished startup; /status is liveness and /ready follows startup.", "components": ["docs", "pinned"], "sources": ["docs:s2eb33a763ea4", "docs:scc00d3d3618d", "pinned:sf3cc586861b8", "pinned:s67ee52a23e57"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "Compare INFO FOR DB without credentials and with a system-user JWT on the same NS/DB: exposed auth-off returns info; fixed denies anonymous access and returns authenticated OK data.", "components": ["docs"], "sources": ["docs:scc00d3d3618d", "docs:s51100e115b41"], "status": "REASONED", "verify": [1]},
    "verify-auth-limits": {"text": "Test direct origin and HTTPS; HTTP 200, missing database, disabled route, proxy rejection or transport failure alone proves no authorization control or record permissions.", "components": ["docs"], "sources": ["docs:scc00d3d3618d", "docs:s51100e115b41"], "status": "REASONED", "verify": [1]},
    "verify-origin": {"text": "Any HTTP answer from an untrusted-network origin probe proves reachability; a gateway result alone does not establish origin isolation.", "components": ["docs"], "sources": ["docs:sae73137661aa"], "status": "REASONED", "verify": [2]},
    "verify-tls": {"text": "Validate the certificate chain at every TLS termination using normal trust checks, never -k.", "components": ["docs"], "sources": ["docs:sae73137661aa"], "status": "REASONED", "verify": [1, 2]}
  }
}
````
<!-- version-basis:end -->
