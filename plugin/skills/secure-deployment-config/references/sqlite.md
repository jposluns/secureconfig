# SQLite in deployment: the file is the exposure (plus Turso and Litestream)

SQLite has no server process and no network listener: "there are no other processes, threads, machines, or other mechanisms (apart from host computer OS and filesystem) to help provide database services" ([SQLite: serverless](https://www.sqlite.org/serverless.html)), so there is no database-side authentication and the only access control is the filesystem's. Its security page warns that "any database file which might have ever been writable by an agent in a different security domain should be treated as suspect." So the deployment exposure is rarely a flaw in SQLite itself; it is wherever the database file ends up: under a web root, inside a git repository, readable by another local account, or replicated to a public bucket. Run the application with access only to the files it needs, since `ATTACH` opens further databases under the process's filesystem authority; keep extension loading disabled unless required (core SQLite disables it by default, though the SQLite CLI enables it) and load only trusted extension libraries. Application-level SQL-injection prevention is outside this guide's scope.

## 1. Keep the file out of anything that serves it

Keep the database, its sidecars, temporary files, exports, and backups outside every web-served directory, for example under `/var/lib/myapp/app.db` rather than `public/app.db` or `static/app.db`; a file under the web root is downloadable by URL like any other. Confirm that aliases, symlinks, application download routes, static-host uploads, and backup publishing do not expose them, and disable directory listing where appropriate rather than relying on hidden filenames. [web-exposure.md](web-exposure.md) explains the general pattern; its example deny rules must be extended for the actual SQLite filenames if you use them as a backstop.

## 2. Keep the file out of git

A committed `.db` file ships every row to anyone who clones the repository, permanently, even after a later commit deletes it. Add `*.db`, `*.sqlite`, `*.sqlite3`, and their sidecar files to `.gitignore` before the first commit: the WAL, shared-memory, and rollback-journal files take the full database filename plus `-wal`, `-shm`, or `-journal`, so each extension needs its own trio (`*.db-wal`, `*.db-shm`, `*.db-journal`, `*.sqlite-wal`, `*.sqlite-shm`, `*.sqlite-journal`, `*.sqlite3-wal`, `*.sqlite3-shm`, `*.sqlite3-journal`). Ignore rules do not remove already-tracked files, so scan the index and history and handle a copy that already leaked per [secrets.md](secrets.md).

## 3. File permissions

Use a dedicated application account. Restrict its database directory to that account (`700`) and the database and any existing journal, WAL, and SHM sidecar files to that account (`600`), and set `umask 077` in the launch environment before those files are created; any other local account or process can otherwise open the file directly, since there is no SQLite-side access control. Verify existing sidecars separately rather than deleting live ones to repair exposure, and protect temporary files and backups too: with the Unix VFS, `SQLITE_TMPDIR` can point at an existing private temporary directory (SQLite may fall back to other locations, so confirm it exists). These permissions do not isolate processes that share the account or privileged host users.

## 4. Encryption at rest is not built in

Public-domain SQLite does not encrypt database files; whoever obtains the file reads every row, which is what makes steps 1 to 3 load-bearing. The [SQLite Encryption Extension (SEE)](https://www.sqlite.org/see/doc/trunk/www/readme.wiki) is licensed software ("the public version of SQLite will not be able to read or write an encrypted database file"), and [SQLCipher](https://www.zetetic.net/sqlcipher/) is a third-party build with the same goal; unless the deployment has adopted one of those, rely on filesystem or volume encryption. Keep encryption keys outside the database and its backups and load them through the application's secret mechanism, and note that SEE documents unencrypted TEMP tables, so do not assume temporary files are encrypted. Rows that hold credentials make every database, journal, export, and backup copy a secret-bearing artefact; if one leaks, rotate those credentials rather than assuming deletion contains it ([secrets.md](secrets.md)).

## 5. libSQL and Turso: the file becomes an HTTP endpoint

Turso serves libSQL databases over HTTP, replacing the local file with a network service authenticated by a bearer token against a URL of the form `https://[databaseName]-[organizationSlug].turso.io`. Applications read `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN` from the environment; the token is a secret exactly like an API key, never in the client bundle, never committed ([secrets.md](secrets.md)).

```bash
turso db tokens create example-db --read-only --expiration 7d
```

`turso db tokens create` supports `-r`/`--read-only` to scope a token away from writes, and `-e`/`--expiration` to give it a lifetime (`never`, or a duration such as `7d3h`); issue a scoped, expiring token for anything that does not need full write access rather than reusing one long-lived full-access token everywhere.

## 6. Litestream and LiteFS: the replica destination is now part of the exposure

Litestream continuously replicates the SQLite file to S3, Google Cloud Storage, Azure Blob Storage, and other supported destinations, authenticating to S3 the same way any AWS client does, with `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in the environment. Litestream's own S3 guide scopes the IAM policy to the one bucket and prefix it needs rather than granting broad S3 access, which limits the damage if the credential leaks. The replica bucket needs the same private-by-default posture as any other bucket: see [object-storage.md](object-storage.md) for keeping it non-public and restoring through scoped credentials rather than a public URL. Litestream's metrics listener (`addr`) and, in v0.5.0 and later, its MCP listener (`mcp-addr`) are disabled by default; leave them off unless needed, and when local access is required bind explicitly to loopback (for example `addr: "127.0.0.1:9090"`, `mcp-addr: "127.0.0.1:3001"`). The MCP server has no built-in authentication and exposes database information and restore capabilities, so reach it only through an authenticated tunnel or protected proxy, never a directly published port.

LiteFS replicates a SQLite file across a cluster's nodes rather than to object storage directly; its docs note the project is pre-1.0 and recommend regular off-site backups as a separate measure, and that backup destination should get the same bucket-privacy treatment as a Litestream replica. LiteFS also runs an HTTP API for replication and administration. At v0.5.14 no route on it checks any credential: the server accepts cleartext HTTP/1 and h2c (HTTP/2 without TLS), and LiteFS's own client uses h2c only. Network reachability therefore exposes unauthenticated operations, subject to the role and database conditions below.

The default `http.addr` is `:20202`, which names no host and so listens on every interface, and the example configuration in the LiteFS repository ships the same host-less value. Set the address in the configuration file; no command-line flag sets it directly. The default search order is `litefs.yml` in the working directory, then the current user's home directory when available, then `/etc/litefs.yml`; `-config PATH` instead reads the specified path. `${VAR}` environment expansion applies unless `-no-expand-env` is passed. An explicitly empty `addr` still listens on every interface, on a system-chosen port; it does not disable the API.

| Route | Role and database conditions at v0.5.14 |
| --- | --- |
| POST `/import` | Primary only: creates a named database if absent or replaces its contents from the request body. A named request on a replica returns 503 before database creation; it is not forwarded. `DB.Import` also rejects a non-primary. |
| GET `/export` | Primary or replica: exports an existing named local database in full, including applicable WAL pages. A missing database returns 404. |
| POST `/stream` | Primary only, over HTTP/2 with a valid position-map body. An otherwise valid request on a replica returns 503. Without a `filter`, it can stream every database on the primary; a caller-supplied filter narrows the set, and a fresh position receives a snapshot. |
| POST `/tx` | Primary or replica: applies a valid LTX file to an existing named local database, without forwarding or checking primary status or the caller's halt-lock ownership. Non-snapshot input must match the next transaction id and current checksum, and the file undergoes LTX validation. A missing database returns 404. |
| POST `/halt`, DELETE `/halt` | Primary or replica: POST creates the named local database if absent and acquires its write locks with a nonzero lock id. On the primary this stalls that database's writes; on a replica it can block replication applying that database's updates. The default lock TTL is 30 seconds, with expiration checked every 5 seconds. DELETE releases the existing database's lock when its id matches. |
| POST `/promote` | Requires an eligible candidate. An already-primary candidate returns success without a change; a candidate replica with a known primary requests handoff from it, subject to the handoff conditions below. No database name is required. |
| POST `/handoff` | Primary only, with a connected target subscriber and a lease that supports handoff; static leases refuse it. No database name is required. |
| GET `/info`, `/events`, `/metrics` | Primary or replica, without a named database: disclose node, cluster, and database state through information, events, and metrics. |

The debug routes are also unconditional on either role and need no named database: Go's `/debug/pprof/` exposes profiling (`cmdline` returns the process command line; `profile` and `trace` run live profiles), and `/debug/vars` exposes the command line, memory statistics, and a `store` variable carrying primary status and each database's name, transaction id, and lock states. The third route, `/debug/rand`, streams deterministic pseudo-random data and checks a one-minute timeout only between writes, so a slow or non-reading client can hold a request open longer, since the server sets no write timeout. The optional `Litefs-Id` comparisons in the API reject self-connections; they do not authenticate callers.

Keep each node's API reachable only by the cluster's own nodes over a private network: set `http.addr` to that node's private address and never publish port 20202 through an internet-facing port mapping or proxy. Under Consul leasing, set each node's `lease.advertise-url` to its own private API URL; if unset, it is derived as `http://` plus `lease.hostname` (falling back to the OS hostname) and the actual listening port. Under static leasing, the configured value is used as given: the primary advertises its own private API URL, while every replica's `lease.advertise-url` must point to the primary's private API URL.

The upstream image bakes in no configuration file and declares no `EXPOSE`. With the default bind, LiteFS listens on every interface of its network namespace. Container reachability depends on the configured bind, network mode, connected peers, routing, firewall, and port publication: same-network peers can reach the listener without a published port, host networking uses the host's network namespace, and containers sharing a network namespace can reach its listeners. The optional application proxy (`proxy.addr`, `:8080` in the example configuration) is a separate listener: startup is attempted only when `proxy.target` is set, and `proxy.db` and `proxy.addr` must also be nonempty. It forwards requests to the application and needs the application's own TLS and authentication controls.

## Verify

The bundle scan, the git inventory and the `stat` check were demonstrated on the authoring host in exposed and fixed states; the paragraph after the `stat` step records what was observed. The download probe, the LiteFS/Litestream listener check and the Turso check are REASONED, each marked at its step with the capability that was missing. Their outcomes are derived from the cited vendor pages, and backlog row 2.37 tracks demonstrating them. Use Bash and curl 7.75.0 or newer; never add `-k`. Substitute inside the single quotes and paste each complete subshell.

```bash
# REASONED: needs a served application, which opens a listener; the authoring host forbids that without an isolated network namespace, and none was available.
# The database and its sidecars must not be downloadable. The positive control must answer first, or the 404s
# are inconclusive (a timeout, NXDOMAIN, or an environment proxy otherwise reads like a false pass).
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_APP_ORIGIN' '/'   # the second value is a static path prefix to probe as well, such as '/static'; '/' probes the root only
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo "exactly one origin and one path prefix required; not probing"; exit 2; }
  case "$1" in ""|*REPLACE_WITH_*) echo "substitute the HTTPS application origin; not probing"; exit 2 ;; esac
  case "$1" in https://*) ;; *) echo "HTTPS origin required; not probing"; exit 2 ;; esac
  case "${1#https://}" in ""|/*|:*) echo "the origin needs a host after https://; not probing"; exit 2 ;; esac
  set -- "${1%/}" "$2"   # one trailing / is tolerated and dropped
  case "${1#https://}" in */*|*'?'*|*'#'*|*@*|*[[:space:][:cntrl:]]*) echo "the origin must be https://host or https://host:port, with no path, query, fragment, userinfo or whitespace; not probing"; exit 2 ;; esac
  case "${1#https://}" in *:|*:*[!0123456789]*) echo "the origin port must be digits after a single colon; not probing"; exit 2 ;; esac
  case "$2" in ""|*REPLACE_WITH_*) echo "substitute the static path prefix, or '/' for the root only; not probing"; exit 2 ;; esac
  case "$2" in /*) ;; *) echo "the path prefix must start with /; not probing"; exit 2 ;; esac
  case "$2" in *//*) echo "the path prefix must not contain //; not probing"; exit 2 ;; esac
  case "$2" in *'?'*|*'#'*|*[[:space:][:cntrl:]]*) echo "the path prefix must not contain ?, # or whitespace; not probing"; exit 2 ;; esac
  case "${2%/}" in "") set -- "$1" ;; *) set -- "$1" "$1${2%/}" ;; esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 -o /dev/null \
    -w 'control http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1/"
  while [ "$#" -gt 0 ]; do
    printf 'under %s/\n' "$1"
    (
      set -- "$1" app.db "$1" app.db-wal "$1" app.db-shm "$1" app.db-journal   # base and file in pairs, so no named loop variable is read
      while [ "$#" -gt 0 ]; do
        curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 -o /dev/null \
          -w "$2 http=%{http_code} exit=%{exitcode} err=%{errormsg}\n" "$1/$2"
        shift 2
      done   # 404 or the app's catch-all, never 200/206; repeat for any further prefix your app serves
    )
    shift
  done
)
```

Scan built client bundles for a leaked Turso/libSQL token, keeping the token off argv and shell history:

```bash
(                                       # a subshell, so your own script arguments are untouched
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e                          # never trace or export the token read below
  { unset -n tok && unset -v tok; } 2>/dev/null ||
    { echo 'a readonly tok is set in this shell; not scanning'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not scanning'; exit 2; }
  set -- PASTE_WHOLE_BLOCK build dist .next/static
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not scanning'; exit 2; }
  shift
  for d in "$@"; do shift; [ -d "$d" ] && set -- "$@" "$d"; done   # keep only the directories that exist
  [ "$#" -ge 1 ] || { echo 'none of the bundle directories exist here; not scanning'; exit 2; }
  if ! IFS= read -r -s -p 'paste the token value from the secret store (input hidden): ' tok < /dev/tty; then
    echo 'token input failed; not scanning'
    exit 2
  fi
  echo
  [ -n "$tok" ] || { echo 'no token supplied; not scanning'; exit 2; }
  printf '%s\n' "$tok" | grep -rnF -f - -- "$@"; echo "token-literal exit: $? (1 is the goal: not found; 0 means the token is in the bundle)"
  grep -rnE 'eyJ[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-]{10,}[.][ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-]{10,}' -- "$@"; echo "jwt-shape exit: $? (1 is the goal; 0 means a JWT-shaped string needs explaining)"
)
```

A clean result is evidence, not proof: neither pattern matched in the paths searched, not that the token cannot be present in some other form. A bundler can split, encode, or transform it, and a missing directory produces the same silence as a genuinely clean scan, so read the exit codes above and confirm the directories exist. Turso and libSQL tokens are JWTs, so a JWT-shaped hit needs explaining.

Confirm the database is not tracked in git, not only that a rule exists (ignore rules do not apply to already-tracked files):

```bash
git check-ignore -v app.db app.db-wal app.db-shm app.db-journal   # substitute the real repository paths
git ls-files -- app.db app.db-wal app.db-shm app.db-journal   # any output is a tracked database or sidecar
git log --all --oneline -- app.db app.db-wal app.db-shm app.db-journal | head   # any output is a copy in history; handle per secrets.md
```

Check the live file, its directory, and every existing sidecar while the application is running:

```bash
stat -c '%a %U %n' /var/lib/myapp /var/lib/myapp/app.db*   # 700 on the directory, 600 on app.db and any -wal/-shm/-journal sidecars, each owned by the app user; an absent sidecar says nothing about its future mode
```

On the authoring host, without opening any socket, these three checks ran in exposed and fixed states.

- **Bundle scan.** It ran with a generated JWT-shaped placeholder, not a real token, typed at its hidden prompt.
  - A bundle carrying the placeholder printed `token-literal exit: 0` and `jwt-shape exit: 0`.
  - A clean bundle printed `1` for both.
  - With none of the named directories present, the block refused to scan.
  - With `tok` readonly in the calling shell, the block refused before prompting: `a readonly tok is set in this shell; not scanning` (exit 2). The block before this change failed at the prompt instead ("token input failed").
  - With `tok` a nameref to `PATH` in the calling shell, the block scanned as in the placeholder run, printed `0` for both lines, and left `PATH` intact. The block before this change wrote the token into `PATH`, so `grep` was not found and both lines printed `127`.
  - With `declare -l tok` inherited, the block printed `0` for both lines. The block before this change lower-cased the token and printed `token-literal exit: 1`, a false clean result with the token in the bundle.
  - With `IFS` readonly in the calling shell, the block refused before prompting: `a readonly IFS is set in this shell; not scanning` (exit 2). The block before this change prompted and scanned with the readonly `IFS` in force.
- **Git inventory.** It was run in three throwaway repositories.
  - With `app.db` committed before an `app.db*` ignore rule was added, `git check-ignore -v` listed the sidecars but not the tracked `app.db`. `git ls-files` printed `app.db`, and `git log` printed its commit.
  - After `git rm --cached`, `git log` still printed both commits touching it.
  - With the rule in place and the file never committed, only the rule matches printed.
- **`stat` check.** A connection was held open while `stat` ran: in WAL mode, and separately with a write transaction in rollback-journal mode.
  - Under umask `022` the directory was `755`, and `app.db`, `app.db-wal` and `app.db-shm` were `644`.
  - Under umask `077` they were `700` and `600`.
  - With a write transaction held open in rollback-journal mode, `app.db-journal` was `644` under umask `022` and `600` under `077`, the same as `app.db`.
  - Each was owned by the one account that ran the test. Ownership by a separate app user was not exercised, because no second account was available.

For LiteFS (`20202`) or an enabled Litestream metrics/MCP listener (REASONED: needs a running LiteFS or Litestream, which opens listeners; the authoring host forbids that without an isolated network namespace, and none was available), prove network isolation from an untrusted vantage. Run it first from an authorized peer against the private URL (a response is the positive control), then from an untrusted network against the same public address and port:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_LISTENER_PROBE_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "exactly one URL required; not probing"; exit 2; }
  case "$1" in ""|*REPLACE_WITH_*) echo "substitute the listener URL; not probing"; exit 2 ;; esac
  case "$1" in http://?*|https://?*) ;; *) echo "HTTP or HTTPS URL required; not probing"; exit 2 ;; esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -o /dev/null -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
)
```

Any HTTP response from the untrusted vantage shows that an HTTP listener answered. Confirmed direct reachability to LiteFS exposes its unauthenticated endpoints, subject to their role and state conditions above; a fronting proxy can return its own denial or expose only selected paths, so its response alone does not establish reachability to the whole LiteFS API. A timeout, DNS, or TLS error, or a failed authorized control, is inconclusive, so corroborate with the bind address, routing, proxy configuration, and firewall. For Turso (REASONED: this outbound check needs a Turso database and token, and none was available to the authoring environment), prove the HTTP database rejects anonymous queries. Have a valid database token from the secret store ready to paste. The block prompts for it with input hidden, never exports it, and refuses a control character, so a pasted token cannot inject a second header. This keeps the token out of curl's argv, not out of reach of the account that runs the block:

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  { unset -n turso_tok && unset -v turso_tok; } 2>/dev/null ||
    { echo "a readonly turso_tok is set in this shell; not probing"; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo "a readonly IFS is set in this shell; not probing"; exit 2; }
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_DATABASE_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "exactly one URL required; not probing"; exit 2; }
  case "$1" in ""|*REPLACE_WITH_*) echo "substitute the HTTPS database URL; not probing"; exit 2 ;; esac
  case "$1" in https://?*) ;; *) echo "HTTPS required; not probing"; exit 2 ;; esac
  IFS= read -r -s -p 'Turso database token (input hidden): ' turso_tok < /dev/tty ||
    { echo "token input failed; not probing"; exit 2; }
  printf '\n'
  case "$turso_tok" in ""|*REPLACE_WITH_*|*[[:cntrl:]]*) echo "paste a valid database token, with no control characters; not probing"; exit 2 ;; esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -H 'Content-Type: application/json' \
    --data '{"requests":[{"type":"execute","stmt":{"sql":"SELECT 1"}},{"type":"close"}]}' \
    -w '\nanonymous http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "${1%/}/v2/pipeline"
  printf 'Authorization: Bearer %s\n' "$turso_tok" |
    curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 --header @- \
      -H 'Content-Type: application/json' \
      --data '{"requests":[{"type":"execute","stmt":{"sql":"SELECT 1"}},{"type":"close"}]}' \
      -w '\nauthorized http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "${1%/}/v2/pipeline"
)
```

The authorized request must return a result containing `1`; the identical anonymous request must be rejected and return no successful query result. Anonymous query success is exposure, and an HTTP 200 alone is insufficient because the body can carry a statement error; transport failures are inconclusive.

## Sources (checked September 2026)

Applicability checked on 2026-09-18: SQLite 3.x documentation (local file tests on SQLite 3.46.1); LiteFS HTTP behavior traced to v0.5.14; Litestream MCP documented for v0.5.0 and later; Turso rolling CLI documentation and the SQL-over-HTTP `/v2/pipeline` protocol. Installed Turso, Litestream, and LiteFS versions were not available for runtime confirmation. The Verify commands require Bash, curl 7.75.0 or later, GNU-compatible grep and stat, and Git.

- SQLite security: https://www.sqlite.org/security.html
- Turso HTTP API quickstart (`TURSO_DATABASE_URL`, `TURSO_AUTH_TOKEN`): https://docs.turso.tech/sdk/http/quickstart
- Turso CLI `db tokens create` (`--read-only`, `--expiration`): https://docs.turso.tech/cli/db/tokens/create
- Litestream guides (supported replica destinations): https://litestream.io/guides/
- Litestream S3 guide (credentials, scoped IAM policy): https://litestream.io/guides/s3/
- LiteFS overview (cluster replication, pre-1.0 status, backup recommendation): https://fly.io/docs/litefs/
- SQLite serverless architecture (no server process; OS and filesystem only): https://www.sqlite.org/serverless.html
- SQLite temporary and sidecar file naming (-wal, -shm, -journal): https://www.sqlite.org/tempfiles.html
- SQLite Encryption Extension (licensed; the public build cannot read an encrypted file): https://www.sqlite.org/see/doc/trunk/www/readme.wiki
- SQLCipher (third-party encrypted-SQLite build): https://www.zetetic.net/sqlcipher/
- SQLite extension loading (disabled by default; enabled in the CLI): https://sqlite.org/loadext.html
- LiteFS configuration (http.addr, lease.advertise-url, default port 20202): https://fly.io/docs/litefs/config/
- LiteFS listener and configuration (pinned tag v0.5.14): default address, plain TCP and h2c server, h2c-only client, mount flags, environment expansion, default config search and explicit path, and example API bind: https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L32-L35, https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/config.go#L57, https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L76-L99, https://github.com/superfly/litefs/blob/v0.5.14/http/client.go#L32-L43, https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/mount_linux.go#L76-L110, https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/config.go#L219-L233, https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/config.go#L288-L333, https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/etc/litefs.yml#L54-L58
- LiteFS route dispatch and reads (pinned tag v0.5.14): no credential gate, export including WAL pages, primary-only HTTP/2 stream, database enumeration and filtering, snapshots, position-map decoding, info, events, and unconditional debug routes including rand: https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L134-L268, https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L320-L346, https://github.com/superfly/litefs/blob/v0.5.14/db.go#L2682-L2776, https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L495-L520, https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L526-L585, https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L686-L699, https://github.com/superfly/litefs/blob/v0.5.14/http/http.go#L15-L43, https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L271-L292, https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L779-L803, https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/mount_linux.go#L487-L488, https://github.com/superfly/litefs/blob/v0.5.14/store.go#L1661-L1713
- LiteFS mutations and role checks (pinned tag v0.5.14): import handler and database method, replica primary context, local tx application and validation, per-database halt acquisition and release, expiration defaults and enforcement, and replication write locks: https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L294-L318, https://github.com/superfly/litefs/blob/v0.5.14/db.go#L2779-L2811, https://github.com/superfly/litefs/blob/v0.5.14/store.go#L139-L141, https://github.com/superfly/litefs/blob/v0.5.14/store.go#L444-L478, https://github.com/superfly/litefs/blob/v0.5.14/store.go#L1904-L1910, https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L461-L493, https://github.com/superfly/litefs/blob/v0.5.14/db.go#L2387-L2448, https://github.com/superfly/litefs/blob/v0.5.14/db.go#L2452-L2609, https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L348-L407, https://github.com/superfly/litefs/blob/v0.5.14/db.go#L215-L325, https://github.com/superfly/litefs/blob/v0.5.14/store.go#L39-L41, https://github.com/superfly/litefs/blob/v0.5.14/store.go#L1455-L1465, https://github.com/superfly/litefs/blob/v0.5.14/store.go#L1525-L1531
- LiteFS leasing and handoff (pinned tag v0.5.14): promote eligibility, primary and subscriber checks, Consul URL derivation, static configuration and primary URL on replicas, replication destination, and static handoff refusal: https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L409-L459, https://github.com/superfly/litefs/blob/v0.5.14/store.go#L408-L432, https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/mount_linux.go#L329-L348, https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/mount_linux.go#L241-L244, https://github.com/superfly/litefs/blob/v0.5.14/lease.go#L99-L131, https://github.com/superfly/litefs/blob/v0.5.14/store.go#L1384-L1387, https://github.com/superfly/litefs/blob/v0.5.14/lease.go#L168-L170
- LiteFS optional proxy and image (pinned tag v0.5.14): proxy startup condition and required fields, example proxy address, and Dockerfile without configuration or EXPOSE: https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/mount_linux.go#L519-L524, https://github.com/superfly/litefs/blob/v0.5.14/http/proxy_server.go#L131-L144, https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/etc/litefs.yml#L60-L68, https://github.com/superfly/litefs/blob/v0.5.14/Dockerfile
- Go standard library defaults the LiteFS listener and debug routes inherit (a host-less or empty address listens on every unicast address, with the port chosen automatically when empty; expvar serves `cmdline` and `memstats`; pprof's `cmdline` responds with the running program's command line): https://pkg.go.dev/net#Listen, https://pkg.go.dev/expvar and https://pkg.go.dev/net/http/pprof
- Go h2c handler (ordinary HTTP/1 requests pass to the underlying handler): [NewHandler documentation](https://pkg.go.dev/github.com/golang/net/http2/h2c#NewHandler).
- Docker container reachability: [bridge peers and publication](https://docs.docker.com/engine/network/drivers/bridge/), [host networking](https://docs.docker.com/engine/network/drivers/host/), and [shared container networking stacks](https://docs.docker.com/engine/network/#container-networks).
- Litestream configuration (metrics addr, MCP mcp-addr): https://litestream.io/reference/config/
- Turso SQL over HTTP (`/v2/pipeline`, bearer authentication): https://docs.turso.tech/sdk/http/reference
