---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "82ea4d4ff14f58e99013eba2c60fae44f17f8a66a78fc4d15bdf49e8818cb149",
  "components": {
    "docs": {
      "name": "SurrealDB documentation",
      "basis": "unknown",
      "sources": {
        "s36c00a9caa98": "https://surrealdb.com/docs/reference/cli/surrealdb-cli/commands/start",
        "sa4cee13a8dd9": "https://surrealdb.com/docs/reference/cli/surrealdb-cli/commands/sql",
        "s38b5f5aad1d4": "https://surrealdb.com/docs/learn/security",
        "sdaa9a636537a": "https://surrealdb.com/docs/learn/security/authentication/overview",
        "sae73137661aa": "https://surrealdb.com/docs/learn/security/best-practices/security-best-practices",
        "sc798cc43c457": "https://surrealdb.com/docs/learn/security/authorization/capabilities",
        "sb9c3a17a2998": "https://surrealdb.com/docs/learn/security/authorization/permissions-and-row-level-security",
        "sfdfa4e63cdd5": "https://surrealdb.com/docs/reference/query-language/statements/define/access/record",
        "scc00d3d3618d": "https://surrealdb.com/docs/reference/rest-api/http-protocol",
        "s51100e115b41": "https://surrealdb.com/docs/reference/query-language/statements/info",
        "s048fd6bd1f3e": "https://surrealdb.com/docs/reference/query-language/statements/define/access/jwt"
      }
    },
    "pinned": {
      "name": "SurrealDB CLI and image",
      "basis": "v3.2.4",
      "sources": {
        "sac8662d10d16": "https://github.com/surrealdb/surrealdb/blob/v3.2.4/surrealdb/server/src/cli/start.rs#L148-L162",
        "s91a7bdf0a6e8": "https://github.com/surrealdb/surrealdb/blob/v3.2.4/surrealdb/server/src/dbs/mod.rs#L47-L50",
        "s21f5e29c7e44": "https://github.com/surrealdb/surrealdb/blob/v3.2.4/surrealdb/server/src/cli/start.rs#L177-L180",
        "s6794599ae101": "https://github.com/surrealdb/surrealdb/blob/v3.2.4/docker/Dockerfile#L104"
      }
    },
    "defaults": {
      "name": "SurrealDB default transition",
      "basis": "2.0.0",
      "sources": {
        "se73fa9c93548": "https://surrealdb.com/releases/2.0"
      }
    },
    "authenticate-compat": {
      "name": "SurrealDB AUTHENTICATE qualification",
      "basis": "3.2.x",
      "sources": {
        "s048fd6bd1f3e": "https://surrealdb.com/docs/reference/query-language/statements/define/access/jwt"
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
    }
  },
  "claims": {
    "auth-default": {"text": "Since 2.0.0 authentication defaults on, --auth was removed and --unauthenticated added; older releases do not share this default.", "components": ["defaults"], "sources": ["defaults:se73fa9c93548"], "status": "REASONED"},
    "bind-default": {"text": "Since 2.0.0 the CLI defaults to 127.0.0.1:8000; v3.2.4 --bind/-b and SURREAL_BIND retain that loopback default.", "components": ["defaults", "pinned"], "sources": ["defaults:se73fa9c93548", "pinned:s21f5e29c7e44"], "status": "REASONED"},
    "root-bootstrap": {"text": "User/password flags or SURREAL_USER/PASS initialize a root only when none exists; they neither disable authentication nor rotate an existing password.", "components": ["docs", "pinned"], "sources": ["docs:s36c00a9caa98", "pinned:sac8662d10d16"], "status": "REASONED"},
    "root-input": {"text": "v3.2.4 start has no stdin password form; prompt and supply a command-local environment assignment, avoiding argv but exposing the server environment to same-user/root inspection.", "components": ["pinned"], "sources": ["pinned:sac8662d10d16"], "status": "REASONED"},
    "environment": {"text": "The clean-Bash block clears user/password variables and rejects other inherited SURREAL_* options, including auth and bind overrides.", "components": ["docs", "pinned"], "sources": ["docs:s36c00a9caa98", "pinned:s91a7bdf0a6e8", "pinned:s21f5e29c7e44"], "status": "REASONED"},
    "unauthenticated": {"text": "--unauthenticated/SURREAL_UNAUTHENTICATED gives guests OWNER-equivalent access; never carry it onto a remotely reachable deployment.", "components": ["docs", "pinned"], "sources": ["docs:s36c00a9caa98", "docs:s38b5f5aad1d4", "docs:sdaa9a636537a", "pinned:s91a7bdf0a6e8"], "status": "REASONED"},
    "docker-bind": {"text": "Pinned image stages set SURREAL_BIND=0.0.0.0:8000 without CMD; start without an override listens on all container IPv4 interfaces, requiring private network or loopback publication.", "components": ["pinned"], "sources": ["pinned:s6794599ae101"], "status": "REASONED"},
    "private-network": {"text": "Widen host binds only deliberately to private addresses; internal-service databases should have no public interface.", "components": ["docs"], "sources": ["docs:sae73137661aa"], "status": "REASONED"},
    "system-users": {"text": "Root, namespace and database system users use OWNER/EDITOR/VIEWER RBAC; all bypass table/field PERMISSIONS, so scoped system users do not supply record isolation.", "components": ["docs"], "sources": ["docs:sdaa9a636537a", "docs:sb9c3a17a2998"], "status": "REASONED"},
    "record-users": {"text": "Record users authenticate through DEFINE ACCESS TYPE RECORD SIGNUP/SIGNIN logic and receive only explicit table/field permissions; absent permissions grant nothing.", "components": ["docs"], "sources": ["docs:sb9c3a17a2998", "docs:sfdfa4e63cdd5"], "status": "REASONED"},
    "signup": {"text": "Unauthenticated /signup and /signin are intentional; omit SIGNUP to prevent public registration and test refusal alongside a provisioned-account sign-in control.", "components": ["docs"], "sources": ["docs:sfdfa4e63cdd5", "docs:scc00d3d3618d"], "status": "REASONED"},
    "scope-history": {"text": "Use DEFINE ACCESS TYPE RECORD; legacy DEFINE SCOPE was deprecated in 2.x and removed in 3.0.", "components": ["scope-old", "scope-removed"], "sources": ["scope-old:s5a6f3aad8f24", "scope-removed:s5a6f3aad8f24"], "status": "REASONED"},
    "access-types": {"text": "DEFINE ACCESS also supports JWT and per-client BEARER keys; standalone JWT creates system-level sessions, while RECORD WITH JWT retains record permissions.", "components": ["docs"], "sources": ["docs:sdaa9a636537a", "docs:sfdfa4e63cdd5", "docs:s048fd6bd1f3e"], "status": "REASONED"},
    "jwt-checks": {"text": "Verify token algorithm/key or JWKS, issuer and audience; native AUDIENCE is a 3.3 feature and 3.2.x uses AUTHENTICATE. Compare invalid tokens against a valid control.", "components": ["docs", "audience", "authenticate-compat"], "sources": ["docs:s048fd6bd1f3e", "audience:s048fd6bd1f3e", "authenticate-compat:s048fd6bd1f3e"], "status": "REASONED"},
    "capability-all": {"text": "allow-all and deny-all default off; prefer deny-all with narrow route, RPC-method and function allowances.", "components": ["docs"], "sources": ["docs:sc798cc43c457"], "status": "REASONED"},
    "capability-net": {"text": "Network access is denied by default; restrict http::* and JWKS destinations and retain external egress protections against SSRF.", "components": ["docs"], "sources": ["docs:sc798cc43c457"], "status": "REASONED"},
    "capability-functions": {"text": "Functions are allowed by default; a bare allow-funcs broadens access beyond narrow named allowances.", "components": ["docs"], "sources": ["docs:sc798cc43c457"], "status": "REASONED"},
    "capability-scripting": {"text": "Embedded scripting defaults off; enable it only when required.", "components": ["docs"], "sources": ["docs:sc798cc43c457"], "status": "REASONED"},
    "capability-guests": {"text": "Guest access defaults off; capabilities govern what an authorized query may do independently of authentication.", "components": ["docs"], "sources": ["docs:sc798cc43c457"], "status": "REASONED"},
    "capability-precedence": {"text": "More-specific capability rules override broader ones; deny wins at equal specificity.", "components": ["docs"], "sources": ["docs:sc798cc43c457"], "status": "REASONED"},
    "tls": {"text": "web-crt and web-key provide native HTTPS; a TLS proxy or private tailnet is another documented access pattern.", "components": ["docs"], "sources": ["docs:s36c00a9caa98", "docs:sae73137661aa"], "status": "REASONED"},
    "mfa": {"text": "No native second factor is provided; require IdP or administrative-gateway MFA and prevent direct-origin bypass.", "components": ["docs"], "sources": ["docs:sdaa9a636537a", "docs:sae73137661aa"], "status": "REASONED"},
    "verify-inventory": {"text": "Inventory 8000 on loopback/private addresses; /health establishes process availability, not authentication.", "components": ["docs"], "sources": ["docs:s36c00a9caa98", "docs:scc00d3d3618d"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "Compare INFO FOR DB without credentials and with a system-user JWT on the same NS/DB: exposed auth-off returns info; fixed denies anonymous access and returns authenticated OK data.", "components": ["docs"], "sources": ["docs:scc00d3d3618d", "docs:s51100e115b41"], "status": "REASONED", "verify": [1]},
    "verify-auth-limits": {"text": "Test direct origin and HTTPS; HTTP 200, missing database, disabled route, proxy rejection or transport failure alone proves no authorization control or record permissions.", "components": ["docs"], "sources": ["docs:scc00d3d3618d", "docs:s51100e115b41"], "status": "REASONED", "verify": [1]},
    "verify-origin": {"text": "Any HTTP answer from an untrusted-network origin probe proves reachability; a gateway result alone does not establish origin isolation.", "components": ["docs"], "sources": ["docs:sae73137661aa"], "status": "REASONED", "verify": [1]},
    "verify-tls": {"text": "Validate the certificate chain at every TLS termination using normal trust checks, never -k.", "components": ["docs"], "sources": ["docs:sae73137661aa"], "status": "REASONED", "verify": [1]}
  }
}
---
# SurrealDB: authentication and TLS

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| auth-default: Since 2.0.0 authentication defaults on, --auth was removed and --unauthenticated added; older releases do not share this default. | SurrealDB default transition 2.0.0 | REASONED |
| bind-default: Since 2.0.0 the CLI defaults to 127.0.0.1:8000; v3.2.4 --bind/-b and SURREAL_BIND retain that loopback default. | SurrealDB default transition 2.0.0; SurrealDB CLI and image v3.2.4 | REASONED |
| root-bootstrap: User/password flags or SURREAL_USER/PASS initialize a root only when none exists; they neither disable authentication nor rotate an existing password. | SurrealDB documentation unknown; SurrealDB CLI and image v3.2.4 | REASONED |
| root-input: v3.2.4 start has no stdin password form; prompt and supply a command-local environment assignment, avoiding argv but exposing the server environment to same-user/root inspection. | SurrealDB CLI and image v3.2.4 | REASONED |
| environment: The clean-Bash block clears user/password variables and rejects other inherited SURREAL_* options, including auth and bind overrides. | SurrealDB documentation unknown; SurrealDB CLI and image v3.2.4 | REASONED |
| unauthenticated: --unauthenticated/SURREAL_UNAUTHENTICATED gives guests OWNER-equivalent access; never carry it onto a remotely reachable deployment. | SurrealDB documentation unknown; SurrealDB CLI and image v3.2.4 | REASONED |
| docker-bind: Pinned image stages set SURREAL_BIND=0.0.0.0:8000 without CMD; start without an override listens on all container IPv4 interfaces, requiring private network or loopback publication. | SurrealDB CLI and image v3.2.4 | REASONED |
| private-network: Widen host binds only deliberately to private addresses; internal-service databases should have no public interface. | SurrealDB documentation unknown | REASONED |
| system-users: Root, namespace and database system users use OWNER/EDITOR/VIEWER RBAC; all bypass table/field PERMISSIONS, so scoped system users do not supply record isolation. | SurrealDB documentation unknown | REASONED |
| record-users: Record users authenticate through DEFINE ACCESS TYPE RECORD SIGNUP/SIGNIN logic and receive only explicit table/field permissions; absent permissions grant nothing. | SurrealDB documentation unknown | REASONED |
| signup: Unauthenticated /signup and /signin are intentional; omit SIGNUP to prevent public registration and test refusal alongside a provisioned-account sign-in control. | SurrealDB documentation unknown | REASONED |
| scope-history: Use DEFINE ACCESS TYPE RECORD; legacy DEFINE SCOPE was deprecated in 2.x and removed in 3.0. | SurrealDB SCOPE deprecation 2.x; SurrealDB SCOPE removal 3.0 | REASONED |
| access-types: DEFINE ACCESS also supports JWT and per-client BEARER keys; standalone JWT creates system-level sessions, while RECORD WITH JWT retains record permissions. | SurrealDB documentation unknown | REASONED |
| jwt-checks: Verify token algorithm/key or JWKS, issuer and audience; native AUDIENCE is a 3.3 feature and 3.2.x uses AUTHENTICATE. Compare invalid tokens against a valid control. | SurrealDB documentation unknown; SurrealDB native AUDIENCE minimum 3.3; SurrealDB AUTHENTICATE qualification 3.2.x | REASONED |
| capability-all: allow-all and deny-all default off; prefer deny-all with narrow route, RPC-method and function allowances. | SurrealDB documentation unknown | REASONED |
| capability-net: Network access is denied by default; restrict http::* and JWKS destinations and retain external egress protections against SSRF. | SurrealDB documentation unknown | REASONED |
| capability-functions: Functions are allowed by default; a bare allow-funcs broadens access beyond narrow named allowances. | SurrealDB documentation unknown | REASONED |
| capability-scripting: Embedded scripting defaults off; enable it only when required. | SurrealDB documentation unknown | REASONED |
| capability-guests: Guest access defaults off; capabilities govern what an authorized query may do independently of authentication. | SurrealDB documentation unknown | REASONED |
| capability-precedence: More-specific capability rules override broader ones; deny wins at equal specificity. | SurrealDB documentation unknown | REASONED |
| tls: web-crt and web-key provide native HTTPS; a TLS proxy or private tailnet is another documented access pattern. | SurrealDB documentation unknown | REASONED |
| mfa: No native second factor is provided; require IdP or administrative-gateway MFA and prevent direct-origin bypass. | SurrealDB documentation unknown | REASONED |
| verify-inventory: Inventory 8000 on loopback/private addresses; /health establishes process availability, not authentication. | SurrealDB documentation unknown | REASONED |
| verify-auth: Compare INFO FOR DB without credentials and with a system-user JWT on the same NS/DB: exposed auth-off returns info; fixed denies anonymous access and returns authenticated OK data. | SurrealDB documentation unknown | REASONED |
| verify-auth-limits: Test direct origin and HTTPS; HTTP 200, missing database, disabled route, proxy rejection or transport failure alone proves no authorization control or record permissions. | SurrealDB documentation unknown | REASONED |
| verify-origin: Any HTTP answer from an untrusted-network origin probe proves reachability; a gateway result alone does not establish origin isolation. | SurrealDB documentation unknown | REASONED |
| verify-tls: Validate the certificate chain at every TLS termination using normal trust checks, never -k. | SurrealDB documentation unknown | REASONED |
<!-- version-basis:end -->

Since SurrealDB 2.0.0, authentication is enabled by default and the CLI binds `127.0.0.1:8000` rather than
`0.0.0.0` (2.0.0 removed the old `--auth` flag, added `--unauthenticated`, and changed the bind default);
on older releases neither held, so pin your version. Even on a current version, a laptop demo becomes a real
exposure the moment the same command runs on a routable server with `--unauthenticated` or a widened bind
carried over.

## 1. Root user and authenticated mode

`surreal start` takes `--user`/`-u` and `--pass`/`-p` (also `SURREAL_USER`/`SURREAL_PASS`) to set
"the initial database root user, applied only if no other root user exists": they initialize that user when
none exists, and do not disable authentication or rotate an existing root password. Pass the password through
the environment, never argv (which reaches `ps` and shell history). `surreal start` has no stdin input for it
(checked at v3.2.4), so the block prompts for it and hands it to that one command as a prefix assignment,
never exported:

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
  SURREAL_USER=root SURREAL_PASS="$pw" surreal start rocksdb:/data/mydb.db --bind 127.0.0.1:8000
)
```

This moves the password out of argv, not out of reach: it stays readable through `/proc/<pid>/environ` by
the same user and by root for the server's whole lifetime, as it does through the environment of any
process that inherits it. Treat it as exposed to that account and to root while the server runs.

The block clears `SURREAL_USER` and `SURREAL_PASS` itself, then refuses to start while any other `SURREAL_*` variable is set in the calling shell, naming each. `surreal start` reads many of its options from such variables, including `SURREAL_UNAUTHENTICATED` and `SURREAL_BIND`, so an inherited one would start the server differently from what the block shows. Unset them, or start from a clean shell.

The `--unauthenticated` flag (`SURREAL_UNAUTHENTICATED`) allows unauthenticated access instead; a
guest connecting under it gets permissions equivalent to the `OWNER` role. Do not run it, or carry it
from a local demo, on anything reachable beyond your own machine.

## 2. Bind privately

`--bind`/`-b` (`SURREAL_BIND`) sets the listening address and defaults to `127.0.0.1:8000` (as of v3.2.4),
loopback only. The images built from the repository's `docker/Dockerfile` do not keep that default: each of its
runtime stages sets `SURREAL_BIND=0.0.0.0:8000` and none sets a `CMD`, so a container run with `start` and no
`--bind` or `SURREAL_BIND` of its own listens on every IPv4 interface inside the container. That is safe only while the host side
stays private: publish it on host loopback (`127.0.0.1:8000:8000`) or attach it to a private network only. On a
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
`DEFINE ACCESS ... TYPE RECORD` with custom `SIGNUP` and `SIGNIN` logic, and they "have no
permissions" beyond what a `PERMISSIONS` clause on a table or field grants them, the same
rules-are-the-security model as Firebase and Supabase ([firebase-supabase.md](firebase-supabase.md)):
a table with no `PERMISSIONS` clause for a record user grants nothing by default. The `/signup` and `/signin`
HTTP endpoints accept unauthenticated credentials by design, and a `SIGNUP` clause can permit public
self-registration that root credentials do not restrict, so omit `SIGNUP` when self-registration is unwanted
and test that it is refused while a provisioned account still signs in. Use `DEFINE ACCESS ... TYPE RECORD`;
the legacy `DEFINE SCOPE` is deprecated in 2.x and removed in 3.0. `DEFINE ACCESS`
also supports `TYPE JWT` and `TYPE BEARER` (per-client keys). Mind the authorization boundary: a standalone
`TYPE JWT` access grants SYSTEM-level sessions governed by its scope and roles, above table and field
permissions, whereas application users who need those permissions want `DEFINE ACCESS ... ON DATABASE TYPE
RECORD WITH JWT`. Trusting an IdP's tokens is more than a valid signature: enforce the expected issuer and
audience (native `AUDIENCE` is a 3.3 feature; on 3.2.x enforce them in an `AUTHENTICATE` clause), set the
verification algorithm and key or JWKS URL, and test expired, wrong-issuer, and wrong-audience tokens against
a valid-token control.

## 4. Capabilities: what an authorized query may do

Authentication decides who connects; capabilities decide what a query may then reach, and it is a separate
control. `--allow-all` and `--deny-all` default off; network access is denied by default, functions are
allowed by default, and scripting (`--allow-scripting`) and guest access (`--allow-guests`) default off. More
specific settings override broader ones, and at equal specificity a deny wins. Prefer `--deny-all` with narrow
explicit allowances for the routes, RPC methods, and functions you need rather than a bare `--allow-funcs` or
`--allow-net`, keep embedded scripting off unless required, and confirm each default against your pinned
version. Functions such as `http::*` and JWKS retrieval make outbound requests, so restrict destinations and
apply the metadata and internal-network protections in [egress-metadata.md](egress-metadata.md); authentication
alone does not prevent SSRF.

## 5. TLS

`--web-crt` and `--web-key` serve SurrealDB's own interfaces over HTTPS directly. SurrealDB's own
guidance also endorses delegating TLS termination to a load balancer or reverse proxy, per
[nginx.md](nginx.md) or [caddy.md](caddy.md), or reaching the instance only over a tailnet
([tailscale.md](tailscale.md)). SurrealDB has no native second factor, so require MFA at the identity provider
(for JWT access) or at an administrative access gateway per [mfa.md](mfa.md), and make sure direct-origin
access cannot bypass that gateway.

## Verify

```bash
# REASONED: expected server outcomes follow the cited SurrealDB documentation; no SurrealDB runtime is
# available in the authoring environment. A redirect, missing database, disabled route, proxy rejection, TLS or transport failure is
# inconclusive, never a pass.
ss -tlnp   # inventory, on the host: 8000 on loopback or a private address, never 0.0.0.0
# guard-conventions: allow fixed loopback health URL http://127.0.0.1:8000/health; no reader-substituted target
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 10 -o /dev/null -w 'health=%{http_code}\n' http://127.0.0.1:8000/health   # process up (not an auth check)
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
  set -- -sS --noproxy '*' --connect-timeout 5 --max-time 20 --header 'Accept: application/json' \
    --header "Surreal-NS: $2" --header "Surreal-DB: $3" --data-binary 'INFO FOR DB;' --url "${1%/}/sql" \
    --write-out '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n'
  echo UNAUTHENTICATED
  curl -q -g "$@" </dev/null || exit 1
  IFS= read -r -s -p 'Short-lived system-user JWT: ' probe_jwt || exit 2
  printf '\n'
  [[ "$probe_jwt" =~ ^[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-]+$ ]] || { echo 'missing or malformed JWT; not probing'; exit 2; }
  echo AUTHENTICATED
  printf 'Authorization: Bearer %s\n' "$probe_jwt" | curl -q -g "$@" --header @- || exit 1
)
# Exposed (auth disabled + /sql enabled): the unauthenticated query returns DB info. Fixed: unauthenticated is
# rejected with an identifiable authorization error and the authenticated request returns an OK result with DB
# info. Both failing, only a proxy tested, an unrelated response, or a TLS/transport failure is inconclusive;
# HTTP 200 alone is insufficient. This tests unauthorized DB-info access, not record permissions.
# Origin reachability from an UNTRUSTED network - ANY HTTP answer proves the origin is reachable (a finding):
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PUBLIC_ORIGIN_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'one URL required; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*) echo 'substitute the origin URL; not probing'; exit 2 ;; esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 -o /dev/null \
    -w 'origin http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' --url "$1"
)
```

These server outcomes are reasoned, not demonstrated here (no SurrealDB runtime in the authoring environment);
the expected exposed and fixed outcomes follow the cited SurrealDB documentation. Confirm the TLS certificate chain wherever
TLS terminates with normal validation (a trusted CA for private PKI); never use `-k`.

## Sources (checked September 2026)

- SurrealDB CLI, `surreal start`: https://surrealdb.com/docs/reference/cli/surrealdb-cli/commands/start
- SurrealDB 3.2.4 `surreal start` root password: `--password`/`--pass`/`-p` or `SURREAL_PASS`, with no stdin form (pinned tag v3.2.4): https://github.com/surrealdb/surrealdb/blob/v3.2.4/surrealdb/server/src/cli/start.rs#L148-L162
- SurrealDB 3.2.4 `--unauthenticated` flag, bound to `SURREAL_UNAUTHENTICATED` (pinned tag v3.2.4): https://github.com/surrealdb/surrealdb/blob/v3.2.4/surrealdb/server/src/dbs/mod.rs#L47-L50
- SurrealDB 3.2.4 `--bind`/`-b` (`SURREAL_BIND`) default `127.0.0.1:8000` (pinned tag v3.2.4): https://github.com/surrealdb/surrealdb/blob/v3.2.4/surrealdb/server/src/cli/start.rs#L177-L180
- SurrealDB `docker/Dockerfile` sets `ENV SURREAL_BIND="0.0.0.0:8000"` in each runtime stage (L78, L104, L139, L165), each followed by `ENTRYPOINT ["/surreal"]` with no `CMD`, shown here for the `prod-ci` stage (pinned tag v3.2.4): https://github.com/surrealdb/surrealdb/blob/v3.2.4/docker/Dockerfile#L104
- SurrealDB CLI, `surreal sql`: https://surrealdb.com/docs/reference/cli/surrealdb-cli/commands/sql
- SurrealDB security overview: https://surrealdb.com/docs/learn/security
- SurrealDB authentication overview: https://surrealdb.com/docs/learn/security/authentication/overview
- SurrealDB security best practices: https://surrealdb.com/docs/learn/security/best-practices/security-best-practices
- SurrealDB capabilities (`--allow-all`/`--deny-all`, net denied, functions allowed, scripting/guests off, specificity + deny-wins): https://surrealdb.com/docs/learn/security/authorization/capabilities
- SurrealDB permissions and row-level security (system users bypass table/field PERMISSIONS): https://surrealdb.com/docs/learn/security/authorization/permissions-and-row-level-security
- SurrealDB DEFINE ACCESS (RECORD, JWT, BEARER): https://surrealdb.com/docs/reference/query-language/statements/define/access/record
- SurrealDB 2.0.0 release (auth on by default, `--unauthenticated`, bind default 127.0.0.1): https://surrealdb.com/releases/2.0
- SurrealDB HTTP protocol (`/signup`, `/signin`, `POST /sql`, `/health`): https://surrealdb.com/docs/reference/rest-api/http-protocol
- SurrealDB INFO statement (database information requires a system user): https://surrealdb.com/docs/reference/query-language/statements/info
- SurrealDB DEFINE ACCESS TYPE JWT (native `AUDIENCE` since 3.3, issuer/audience checks via `AUTHENTICATE`) (AUTHENTICATE on 3.2.x): https://surrealdb.com/docs/reference/query-language/statements/define/access/jwt
- SurrealDB DEFINE SCOPE (deprecated in 2.x, removed in 3.0): https://surrealdb.com/docs/reference/query-language/statements/define/scope
