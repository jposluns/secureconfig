# SQLite in deployment: the file is the exposure (plus Turso and Litestream)

SQLite is a database engine built into your application that keeps its data in an ordinary file. This guide helps your AI assistant protect that file, including no copies in web roots or git, tight permissions, separate encryption at rest, and the network exposure libSQL, Turso, Litestream and LiteFS add.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/sqlite.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against SQLite documentation (rolling) (no recorded version), Litestream MCP minimum v0.5.0, LiteFS source v0.5.14, Git documentation v2.56.0, GNU Coreutils stat manual v9.7, GNU Bash reference manual bash-5.3, curl curl-8_14_1, and GNU grep documentation v3.12; 7 further sources carry no recorded version. Metadata reviewed 2026-10-17; documentation checked September 2026. The guide records 40 claims: 2 demonstrated by a check that ran and 38 reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

SQLite has no server process and no network listener: "there are no other processes, threads, machines, or other mechanisms (apart from host computer OS and filesystem) to help provide database services" ([SQLite: serverless](https://www.sqlite.org/serverless.html)), so there is no database-side authentication and the only access control is the filesystem's. Its security page warns that "any database file which might have ever been writable by an agent in a different security domain should be treated as suspect." So the deployment exposure is rarely a flaw in SQLite itself; it is wherever the database file ends up: under a web root, inside a git repository, readable by another local account, or replicated to a public bucket. Run the application with access only to the files it needs, since `ATTACH` opens further databases under the process's filesystem authority; keep extension loading disabled unless required (core SQLite disables it by default, though the SQLite CLI enables it) and load only trusted extension libraries. Application-level SQL-injection prevention is outside this guide's scope.

## 1. Keep the file out of anything that serves it

Keep the database, its sidecars, temporary files, exports, and backups outside every web-served directory, for example under `/var/lib/myapp/app.db` rather than `public/app.db` or `static/app.db`; a file under the web root is downloadable by URL like any other. Confirm that aliases, symlinks, application download routes, static-host uploads, and backup publishing do not expose them, and disable directory listing where appropriate rather than relying on hidden filenames. [web-exposure.md](web-exposure.md) explains the general pattern; its example deny rules must be extended for the actual SQLite filenames if you use them as a backstop.

## 2. Keep the file out of git

A committed `.db` file ships every row to anyone who clones the repository, permanently, even after a later commit deletes it. This warning is this guide's assessment based on Git's documented removal from the index alone or from the index and working tree and inspectable commit logs. Add `*.db`, `*.sqlite`, `*.sqlite3`, and their sidecar files to `.gitignore` before the first commit. The WAL, shared-memory, and rollback-journal files take the full database filename plus `-wal`, `-shm`, or `-journal`, so each extension needs its own trio (`*.db-wal`, `*.db-shm`, `*.db-journal`, `*.sqlite-wal`, `*.sqlite-shm`, `*.sqlite-journal`, `*.sqlite3-wal`, `*.sqlite3-shm`, `*.sqlite3-journal`). Ignore rules do not remove already-tracked files, so scan the index and history and handle a copy that already leaked per [secrets.md](secrets.md).

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

REASONED: the shell and HTTP mechanics of the download, bundle, listener and Turso checks rest on the GNU Bash bash-5.3, GNU grep v3.12 and curl curl-8_14_1 entries in Sources; this is source reasoning, not a new run. Bash documents `set --` and `shift`, quoted positional arguments and counts, unset-only expansion, prefix/suffix removal, conditional lists, loops, tests, patterns and subshells; these are the primitives used by this guide's marker, count, URL and directory checks. Bash documents `trap -`, `unset -n`/`-v`, readonly failure, `set +x +a +e`, `read -r -s -p`, `printf`, redirections and pipelines; the block's `< /dev/tty` is this guide's procedure and requires a usable controlling terminal at that path, whose operating-system availability these manuals do not establish. The token-handling conclusions below are this guide's assessment under these assumptions; hidden input is not itself history suppression. The clean-shell assumption in CONTRIBUTING rule 7 still applies; paste whole blocks, never a token as a shell command.

REASONED: following block; this overview and the download probe below. The probe needs a served application, and none was available during marking review (October 2026), which ran only local commands; per the guide's cited SQLite serverless architecture and SQLite temporary and sidecar file naming entries, the expected exposed outcome is `200` or `206` for `app.db` or a sidecar once the control answers, and the fixed outcome `404` or the application's catch-all. The probe block passed `bash -n` and ShellCheck 0.11.0 with no findings in that review. The probe block's guards were exercised during marking review (October 2026) under bash 5.3.9 with a Bash curl stub. The written placeholder, non-HTTPS scheme, missing host, empty or nondigit port, multiple port colons, origin path, query, fragment, userinfo or space, empty or placeholder prefix, relative prefix, double slash, prefix query, fragment or space, wrong value count and omitted initial `set --` each printed the corresponding refusal and exited 2 without calling curl. Valid root and `/static/` fixtures exited 0 and called the stub five and nine times respectively; its synthetic HTTP 200 output does not establish live-service behavior. The bundle scan, git inventory and `stat` re-runs from that review are recorded at their steps. The bundle scan and the git inventory were demonstrated on the authoring host in exposed and fixed states. The `stat` check is REASONED for ownership: the earlier plain-file marking review did not exercise a SQLite connection, but the 15 October 2026 local marking review re-observed WAL and rollback-journal modes on open connections with Python SQLite 3.46.1; ownership by a separate account remains unexercised. The paragraph after the `stat` step records these observations. The download probe, the LiteFS/Litestream listener check and the Turso check are REASONED, each marked at its step with the capability that was missing. Their expected outcomes are this guide's assessment using the cited service facts and shell, curl and grep primitives; the manuals do not establish deployed outcomes or exhaustive guard coverage. Use Bash and curl with the behaviour documented here at bash-5.3 and curl-8_14_1; the cited curl page dates `exitcode` and `errormsg` to 7.75.0 but does not establish compatibility of these complete checks with every release from that version onward; never add `-k`. Substitute inside the single quotes and paste each complete subshell.

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

REASONED: preceding block; the download probe above, which needs a served application that was not available, with its expected outcomes per the guide's cited SQLite serverless architecture and SQLite temporary and sidecar file naming entries and its local runs recorded in the opening paragraph of this section. The declaration's scope also covers this introduction to the bundle scan below, whose runs during marking review (October 2026) are recorded after that block. The download guards were exercised during marking review (October 2026) under bash 5.3.9 with a Bash curl stub, and the original block passed ShellCheck 0.11.0 with no findings. The placeholder, scheme, host, port, origin path and prefix refusal fixtures, wrong value count and omitted initial `set --` each exited 2 without calling curl; valid root and static-prefix fixtures exited 0 with synthetic HTTP 200 output, leaving live-service behavior REASONED. Keeping the token off argv and shell history rests on the block's hidden `read` prompt and the `printf` builtin feeding `grep -f -`, per CONTRIBUTING rule 7's `read` exception; no record of the arguments grep received was captured in that review, so the argv property was not observed there. Expected exposed outcome: `token-literal exit: 0`; fixed: `1`. Scan built client bundles for a leaked Turso/libSQL token, keeping the token off argv and shell history, though not out of your own account's view of the process:

REASONED: the paste-alone instruction for the block below, per CONTRIBUTING rule 7's `read` exception. Paste the token alone at the hidden prompt: a multi-line paste leaves every line after the first for your shell to run.

DEMONSTRATED: following block; the recorded authoring-host placeholder-token runs distinguish exposed and clean bundles and exercise the listed shell guards; no real token was used. On 2026-10-13 (UTC), after both scans were changed to print file names only (`-l`), a bundle carrying a JWT-shaped dummy printed `dist/app.js` before `token-literal exit: 0` and again before `jwt-shape exit: 0`, with no token in the output, and a clean bundle printed `1` for both; before the change each scan printed the line holding the token.

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
  printf '%s\n' "$tok" | grep -rlF -f - -- "$@"; echo "token-literal exit: $? (1 is the goal: not found; 0 means the token is in the bundle)"
  grep -rlE 'eyJ[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-]{10,}[.][ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-]{10,}' -- "$@"; echo "jwt-shape exit: $? (1 is the goal; 0 means a JWT-shaped string needs explaining)"
)
```

***

REASONED: the scan limits and token-format assertion are only partly demonstrated; no Sources entry as worded (Turso HTTP API quickstart (`TURSO_DATABASE_URL`, `TURSO_AUTH_TOKEN`), Turso CLI `db tokens create` (`--read-only`, `--expiration`), Turso SQL over HTTP (`/v2/pipeline`, bearer authentication)) states that Turso tokens are JWTs, and no real token was available. The bundle scan was re-run during marking review (October 2026) under bash 5.3.9 and GNU grep 3.12 on scratch fixtures, with a generated JWT-shaped placeholder, not a real token, written to the hidden prompt through a pseudo-terminal. A bundle carrying the placeholder printed `dist/app.js` before `token-literal exit: 0` and again before `jwt-shape exit: 0`, and a clean bundle printed `1` for both. With the placeholder stored base64-encoded, or only in an unnamed `out/` directory beside a clean `dist/`, both lines printed `1`, the same as the clean scan. The block refused, exiting 2, with no named directory present, an empty token, its `set --` line omitted, a readonly `tok` or `IFS` in the calling shell, or no controlling terminal; under an inherited `set -x` only `trap - DEBUG RETURN ERR` and `set +x +a +e` themselves were traced and no token was printed, and under an inherited `set -e` a clean scan still printed both lines. The nameref and lowercase cases are recorded in the list after the `stat` step. That real Turso and libSQL tokens are JWTs was not observed here. A clean result is evidence, not proof: neither pattern matched in the paths searched, not that the token cannot be present in some other form. A bundler can split, encode, or transform it, and a missing directory produces the same silence as a genuinely clean scan, so read the exit codes above and confirm the directories exist. The JWT-shape scan assumes, without a cited source, that Turso and libSQL tokens are JWTs; a JWT-shaped hit needs explaining either way.

REASONED: interpretation of the unchanged bundle commands, from the GNU grep v3.12 and Bash bash-5.3 entries in Sources. `grep -rlF -f - --` recursively searches the selected directories for fixed patterns read one per stdin line and prints matching file names; `grep -rlE` uses an extended regular expression instead, with the listed characters and repetitions chosen by this guide as a heuristic. Recursion follows command-line symlinks but skips symlinks encountered below them. The default binary-input heuristic can suppress output and change whether patterns match; the manual does not establish a complete binary-secret scan. GNU grep reports 0 for a match, 1 for no selected lines and 2 for an error in these invocations, which do not use `-q`. This guide requires both printed statuses to be 1, no diagnostic errors, and confirmation of the intended directories before treating the scan as clean within its stated limits; 2 or any other unexpected status is inconclusive, not clean. Bash makes the first printed `$?` a pipeline status: normally grep's status, but with inherited `pipefail` a failed `printf` can affect it too. The later `echo` status is not a substitute for reading both printed scan statuses.

DEMONSTRATED: re-run during marking review (October 2026) with git 2.53.0 in throwaway repositories outside any checkout. With `app.db` committed before an `app.db*` rule, `git check-ignore -v` listed only the three sidecars while `git ls-files` printed `app.db` and `git log` printed its commit; with the rule in place and `app.db` never committed, `git check-ignore -v` listed all four paths and the other two commands printed nothing. Confirm the database is not tracked in git, not only that a rule exists (ignore rules do not apply to already-tracked files):

DEMONSTRATED: following block; the recorded three throwaway repositories distinguish tracked, historical and never-committed database files.

```bash
git check-ignore -v app.db app.db-wal app.db-shm app.db-journal   # substitute the real repository paths
git ls-files -- app.db app.db-wal app.db-shm app.db-journal   # any output is a tracked database or sidecar
git log --all --oneline -- app.db app.db-wal app.db-shm app.db-journal | head   # any output is a copy in history; handle per secrets.md
```

REASONED: following block; the live-file and separate-account ownership check was only partly demonstrated; no application or second account was available. Reading the output rests on the guide's cited GNU Coreutils v9.7 `stat` manual entry (`-c` format, `%a`, `%U` and `%n`), and the expected private modes rest on the recorded umask runs in this paragraph and the `stat` item below, not on a source. The `stat` check this paragraph introduces was re-run during marking review (October 2026) with uutils coreutils 0.8.0 `stat`, not GNU stat. For a directory holding `app.db` and `-wal`, `-shm` and `-journal` files created as plain files under umask `022`, it printed `755` for the directory and `644` for each file; under umask `077` it printed `700` and `600`, and every path showed the one account that ran it. No application or SQLite connection ran in that earlier plain-file review, so which sidecars exist while the application runs was not exercised there. The 15 October 2026 local marking review re-observed WAL and rollback-journal modes on open connections with Python SQLite 3.46.1; ownership by a separate app user remains unexercised. Check the live file, its directory, and every existing sidecar while the application is running:

REASONED: following block; reading the mode and owner fields rests on the guide's cited GNU Coreutils v9.7 `stat` manual entry, and the expected modes rest on the recorded umask runs, not on a source. The recorded local WAL and rollback-journal runs compare umask 022 with 077, but no second account was available to exercise ownership by a separate application account. Expected exposed modes are 755/644 and fixed modes 700/600, with ownership by the app user; the recorded tests used one account.

```bash
stat -c '%a %U %n' /var/lib/myapp /var/lib/myapp/app.db*   # 700 on the directory, 600 on app.db and any -wal/-shm/-journal sidecars, each owned by the app user; an absent sidecar says nothing about its future mode
```

REASONED: preceding block; the `stat` check above and the combined account of the three checks below were only partly demonstrated in the earlier plain-file marking review: no SQLite connection or second account was available then. Reading the output rests on the guide's cited GNU Coreutils v9.7 `stat` manual entry; the expected exposed modes 755/644 and fixed modes 700/600 rest on the recorded umask runs in the `stat` item below rather than on a source, and the fixed state also expects ownership by the app user. The three checks were re-run during the earlier plain-file marking review (October 2026) using only bash, grep, git, `stat` and a pseudo-terminal for the bundle scan's hidden prompt, on local fixtures, as recorded in the paragraphs around those blocks above; each separated its exposed and fixed states. The earlier `stat` re-run read plain files created under each umask because the `sqlite3` command was refused in that marking environment. The 15 October 2026 local marking review re-observed WAL and rollback-journal modes on open connections with Python SQLite 3.46.1; ownership by a separate app user was not exercised in either review. On the authoring host, without opening any socket, these three checks ran in exposed and fixed states.

- DEMONSTRATED: re-run during marking review (October 2026) under bash 5.3.9 and GNU grep 3.12 with a generated JWT-shaped placeholder, not a real token, written to the hidden prompt through a pseudo-terminal; the exposed, clean and guard observations are in the items below. **Bundle scan.** It ran with a generated JWT-shaped placeholder, not a real token, typed at its hidden prompt.
  - DEMONSTRATED: exposed state, re-run during marking review (October 2026) with the placeholder in a fixture `dist/app.js`: it printed `dist/app.js` before `token-literal exit: 0` and again before `jwt-shape exit: 0`; the clean comparison is the next item. A bundle carrying the placeholder printed `token-literal exit: 0` and `jwt-shape exit: 0`.
  - DEMONSTRATED: fixed state, re-run during marking review (October 2026) with a fixture `dist/app.js` that lacks the placeholder: it printed `token-literal exit: 1` and `jwt-shape exit: 1`. A clean bundle printed `1` for both.
  - DEMONSTRATED: re-run during marking review (October 2026): with none of `build`, `dist` or `.next/static` present the block printed `none of the bundle directories exist here; not scanning` and exited 2 without prompting, while with `dist` present it prompted and scanned. With none of the named directories present, the block refused to scan.
  - DEMONSTRATED: re-run during marking review (October 2026) with `tok` readonly in the calling shell: the current block printed the refusal quoted here, without prompting, and exited 2, while the block before this change, taken from the guide's git history, prompted, reported `tok: readonly variable` and printed `token input failed; not scanning`. With `tok` readonly in the calling shell, the block refused before prompting: `a readonly tok is set in this shell; not scanning` (exit 2). The block before this change failed at the prompt instead ("token input failed").
  - DEMONSTRATED: re-run during marking review (October 2026) with `tok` a nameref to `PATH` in the calling shell: the current block found `grep` and printed `0` for both lines, while the block before this change, taken from the guide's git history, printed `grep: command not found` and `127` for both. With `tok` a nameref to `PATH` in the calling shell, the block scanned as in the placeholder run, printed `0` for both lines, and left `PATH` intact. The block before this change wrote the token into `PATH`, so `grep` was not found and both lines printed `127`.
  - DEMONSTRATED: re-run during marking review (October 2026) with `declare -l tok` in the calling shell and a mixed-case placeholder: the current block printed `0` for both lines, while the block before this change, taken from the guide's git history, printed `token-literal exit: 1` and `jwt-shape exit: 0`. With `declare -l tok` inherited, the block printed `0` for both lines. The block before this change lower-cased the token and printed `token-literal exit: 1`, a false clean result with the token in the bundle.
  - DEMONSTRATED: re-run during marking review (October 2026) with `IFS` readonly in the calling shell: the current block printed the refusal quoted here, without prompting, and exited 2, while the block before this change, taken from the guide's git history, reported `IFS: readonly variable`, prompted, and printed `0` for both lines. With `IFS` readonly in the calling shell, the block refused before prompting: `a readonly IFS is set in this shell; not scanning` (exit 2). The block before this change prompted and scanned with the readonly `IFS` in force.
- DEMONSTRATED: re-run during marking review (October 2026) with git 2.53.0 in three throwaway repositories outside any checkout, each holding `app.db` and its three sidecars as plain files; the exposed and fixed observations are in the items below. **Git inventory.** It was run in three throwaway repositories.
  - DEMONSTRATED: exposed state, re-run during marking review (October 2026): `git check-ignore -v` listed `app.db-wal`, `app.db-shm` and `app.db-journal` against `.gitignore:1:app.db*` but not `app.db`, `git ls-files` printed `app.db`, and `git log` printed its commit; the fixed comparison is the last item. With `app.db` committed before an `app.db*` ignore rule was added, `git check-ignore -v` listed the sidecars but not the tracked `app.db`. `git ls-files` printed `app.db`, and `git log` printed its commit.
  - DEMONSTRATED: exposed state, re-run during marking review (October 2026): after a commit of `git rm --cached app.db`, `git ls-files` printed nothing and `git log` printed both commits touching `app.db`; the fixed comparison is the last item. After `git rm --cached`, `git log` still printed both commits touching it.
  - DEMONSTRATED: fixed state, re-run during marking review (October 2026): `git check-ignore -v` listed all four paths against `.gitignore:1:app.db*`, and `git ls-files` and `git log` printed nothing. With the rule in place and the file never committed, only the rule matches printed.
- REASONED: this stat checklist as a whole; the first three child items' mode comparisons are DEMONSTRATED and ownership in the last is REASONED, per the guide's cited GNU Coreutils v9.7 `stat` manual (checked October 2026; GNU syntax) and SQLite temporary and sidecar file naming, -wal, -shm and -journal (rolling documentation, checked September 2026) entries. Local marking review (15 October 2026, Python SQLite 3.46.1, uutils coreutils 0.8.0 `stat`): `stat -c` on an open WAL connection and an open rollback-journal write transaction printed 755/644 under umask 022 and 700/600 under 077, with the one test account as owner and fixture paths in `%n`; the stat block passed `bash -n` and ShellCheck 0.11.0 with `-s bash`, both with no output. Expected exposed modes are 755/644; fixed modes are 700/600 with ownership by the application account. A separately owned live application file inventory was not exercised and its availability is unknown; no second authorized account was available, as the checklist records, so application ownership and future sidecar modes remain unobserved. **`stat` check.** A connection was held open while `stat` ran: in WAL mode, and separately with a write transaction in rollback-journal mode.
  - DEMONSTRATED: the WAL-mode exposed and fixed mode comparison, per the guide's cited GNU Coreutils v9.7 `stat` manual (checked October 2026; GNU syntax) and SQLite temporary and sidecar file naming, -wal, -shm and -journal (rolling documentation, checked September 2026) entries. Local marking review (15 October 2026, Python SQLite 3.46.1, uutils coreutils 0.8.0 `stat`): `stat -c` on an open WAL connection and an open rollback-journal write transaction printed 755/644 under umask 022 and 700/600 under 077, with the one test account as owner and fixture paths in `%n`; the stat block passed `bash -n` and ShellCheck 0.11.0 with `-s bash`, both with no output. Under umask 022 the directory printed 755 and app.db, -wal and -shm printed 644; under 077 they printed 700 and 600 respectively. Under umask `022` the directory was `755`, and `app.db`, `app.db-wal` and `app.db-shm` were `644`.
  - DEMONSTRATED: the WAL-mode exposed and fixed mode comparison, per the guide's cited GNU Coreutils v9.7 `stat` manual (checked October 2026; GNU syntax) and SQLite temporary and sidecar file naming, -wal, -shm and -journal (rolling documentation, checked September 2026) entries. Local marking review (15 October 2026, Python SQLite 3.46.1, uutils coreutils 0.8.0 `stat`): `stat -c` on an open WAL connection and an open rollback-journal write transaction printed 755/644 under umask 022 and 700/600 under 077, with the one test account as owner and fixture paths in `%n`; the stat block passed `bash -n` and ShellCheck 0.11.0 with `-s bash`, both with no output. Under umask 022 the directory printed 755 and app.db, -wal and -shm printed 644; under 077 they printed 700 and 600 respectively. Under umask `077` they were `700` and `600`.
  - DEMONSTRATED: the rollback-journal exposed and fixed mode comparison, per the guide's cited GNU Coreutils v9.7 `stat` manual (checked October 2026; GNU syntax) and SQLite temporary and sidecar file naming, -wal, -shm and -journal (rolling documentation, checked September 2026) entries. Local marking review (15 October 2026, Python SQLite 3.46.1, uutils coreutils 0.8.0 `stat`): `stat -c` on an open WAL connection and an open rollback-journal write transaction printed 755/644 under umask 022 and 700/600 under 077, with the one test account as owner and fixture paths in `%n`; the stat block passed `bash -n` and ShellCheck 0.11.0 with `-s bash`, both with no output. With the write transaction open, app.db-journal printed 644 under umask 022 and 600 under 077. With a write transaction held open in rollback-journal mode, `app.db-journal` was `644` under umask `022` and `600` under `077`, the same as `app.db`.
  - REASONED: ownership across security domains, per the guide's cited GNU Coreutils v9.7 `stat` manual (checked October 2026; GNU syntax) and SQLite temporary and sidecar file naming, -wal, -shm and -journal (rolling documentation, checked September 2026) entries. Local marking review (15 October 2026, Python SQLite 3.46.1, uutils coreutils 0.8.0 `stat`): `stat -c` on an open WAL connection and an open rollback-journal write transaction printed 755/644 under umask 022 and 700/600 under 077, with the one test account as owner and fixture paths in `%n`; the stat block passed `bash -n` and ShellCheck 0.11.0 with `-s bash`, both with no output. The one-account fixture printed the test account for every path; expected exposed ownership is an unintended account and fixed ownership is the application account, but a separately owned live application file was not exercised (availability unknown) and no second authorized account was available, as this item records. Each was owned by the one account that ran the test. Ownership by a separate app user was not exercised, because no second account was available.

REASONED: needs a running LiteFS, or Litestream with metrics or MCP enabled, plus an authorized peer and an untrusted network vantage, and none was available during marking review (October 2026). The declaration rests on the guide's cited LiteFS configuration (http.addr, lease.advertise-url, default port 20202), LiteFS listener and configuration (pinned tag v0.5.14) and Litestream configuration (metrics addr, MCP mcp-addr) (Litestream MCP listener in v0.5.0 and later) entries. Expected exposed outcome: an HTTP response at the untrusted vantage; fixed: the authorized peer's control answers and the untrusted vantage gets none, corroborated with the bind address, routing, proxy configuration and firewall. The probe block passed `bash -n` and ShellCheck 0.11.0 with no findings in that review. The probe block's guards were exercised during marking review (October 2026) under bash 5.3.9 with a Bash curl stub. The written placeholder printed `substitute the listener URL; not probing`, `ftp://example.test` and `https://` printed `HTTP or HTTPS URL required; not probing`, an extra value printed `exactly one URL required; not probing`, and omission of the initial `set --` printed `paste the whole block; not probing`, each exiting 2 without calling curl. A valid dummy HTTP URL reached the stub, printed its synthetic `http=200 exit=0 err=` line and exited 0; no listener or network isolation was exercised. For LiteFS (`20202`) or an enabled Litestream metrics/MCP listener (REASONED: needs a running LiteFS or Litestream, which opens listeners; the authoring host forbids that without an isolated network namespace, and none was available), prove network isolation from an untrusted vantage. Run it first from an authorized peer against the private URL (a response is the positive control), then from an untrusted network against the same public address and port:

REASONED: following block; LiteFS and Litestream listener isolation follows the cited API and configuration sources; no isolated network namespace was available to run listeners.

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

REASONED: preceding block; the listener probe above, this paragraph's reading of its result, and the Turso introduction, per the guide's cited LiteFS route dispatch and reads (pinned tag v0.5.14), Litestream configuration (metrics addr, MCP mcp-addr) (Litestream MCP listener in v0.5.0 and later) and Turso SQL over HTTP (`/v2/pipeline`, bearer authentication) entries. No LiteFS or Litestream listener, untrusted vantage, Turso database or token was available during marking review (October 2026). Expected exposed outcome: any HTTP response at the untrusted vantage; fixed: none there while the authorized control answers. The listener and Turso blocks passed `bash -n` and ShellCheck 0.11.0 with no findings in that review; their guards were exercised during marking review (October 2026) under bash 5.3.9 with a Bash curl stub: written placeholders, `ftp://example.test`, bare `https://`, extra values and omitted initial `set --` lines each produced the corresponding refusal and exited 2 without calling curl. The Turso block also refused readonly `turso_tok`, readonly `IFS`, an empty token, a placeholder token and a token containing a tab, each exiting 2 without calling curl. Through a pseudo-terminal its hidden prompt did not echo the supplied token; the valid dummy token reached the authorized curl stub on stdin as `Authorization: Bearer dummy.token.review` followed by a newline and was absent from both recorded curl argument lists. The valid listener and Turso cases exited 0 using synthetic HTTP 200 output; no live-service behavior, shell-history behavior or inherited tracing behavior was exercised by these runs. Any HTTP response from the untrusted vantage shows that an HTTP listener answered. Confirmed direct reachability to LiteFS exposes its unauthenticated endpoints, subject to their role and state conditions above; a fronting proxy can return its own denial or expose only selected paths, so its response alone does not establish reachability to the whole LiteFS API. A timeout, DNS, or TLS error, or a failed authorized control, is inconclusive, so corroborate with the bind address, routing, proxy configuration, and firewall. For Turso (REASONED: this outbound check needs a Turso database and token, and none was available to the authoring environment), prove the HTTP database rejects anonymous queries. Have a valid database token from the secret store ready to paste. The block uses Bash's terminal-only hidden input and tests the resulting value for control characters before constructing the header; Bash `read` ignores NUL and reads one line, so this is not a claim that every malformed paste is rejected. This guide's assessment, assuming the clean shell required by CONTRIBUTING rule 7 and a token pasted only at the prompt, is that clearing the token's attributes, disabling allexport and tracing, and feeding the builtin `printf` output to curl's `--header @-` keep that value out of curl's argv, the exported environment, shell-parser history and subsequent `set -x` output. These documented primitives do not prove that no secret can leak, and the running account remains outside this protection:

REASONED: following block; the cited Turso SQL-over-HTTP reference supplies the anonymous/authorized discriminator; no Turso database and token were available. Paste the token alone at the hidden prompt: a multi-line paste leaves every line after the first for your shell to run.

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

REASONED: preceding block; the Turso check above and the outcomes stated here, per the guide's cited Turso SQL over HTTP (`/v2/pipeline`, bearer authentication) entry. No Turso database and token was available during marking review (October 2026). Expected exposed outcome: the anonymous request returns a successful `SELECT 1` result; fixed: it is rejected and returns no successful result while the authorized request returns `1`. The block passed `bash -n` and ShellCheck 0.11.0 with no findings in that review. The block's guards were exercised during marking review (October 2026) under bash 5.3.9 with a Bash curl stub. The written URL placeholder, `ftp://example.test`, bare `https://`, an extra value, omission of the initial `set --`, readonly `turso_tok`, readonly `IFS`, an empty token, a placeholder token and a token containing a tab each printed the corresponding refusal and exited 2 without calling curl. A valid dummy token supplied through the hidden pseudo-terminal prompt was not echoed, reached the authorized stub on stdin as `Authorization: Bearer dummy.token.review` followed by a newline, and was absent from both recorded curl argument lists. That case printed synthetic `anonymous http=200 exit=0 err=` and `authorized http=200 exit=0 err=` lines and exited 0; the stub emitted no query result, so anonymous rejection and authorized query success remain REASONED. The authorized request must return a result containing `1`; the identical anonymous request must be rejected and return no successful query result. Anonymous query success is exposure, and an HTTP 200 alone is insufficient because the body can carry a statement error; transport failures are inconclusive.

## Sources (checked September 2026)

Applicability checked on 2026-09-18: SQLite 3.x documentation (local file tests on SQLite 3.46.1); LiteFS HTTP behavior traced to v0.5.14; Litestream MCP documented for v0.5.0 and later; Turso rolling CLI documentation and the SQL-over-HTTP `/v2/pipeline` protocol. Installed Turso, Litestream, and LiteFS versions were not available for runtime confirmation. The Verify commands require Bash, curl, GNU-compatible grep and stat, and Git; the shell, HTTP-client and scan behaviour is cited at bash-5.3, curl-8_14_1 and v3.12 respectively (checked October 2026), without asserting a minimum version for the complete checks.

- SQLite security (rolling documentation, checked September 2026): https://www.sqlite.org/security.html
- Turso HTTP API quickstart (`TURSO_DATABASE_URL`, `TURSO_AUTH_TOKEN`): https://docs.turso.tech/sdk/http/quickstart
- Turso CLI `db tokens create` (`--read-only`, `--expiration`): https://docs.turso.tech/cli/db/tokens/create
- Litestream guides (supported replica destinations): https://litestream.io/guides/
- Litestream S3 guide (credentials, scoped IAM policy): https://litestream.io/guides/s3/
- LiteFS overview (cluster replication, pre-1.0 status, backup recommendation): https://fly.io/docs/litefs/
- SQLite serverless architecture, no server process; OS and filesystem only (rolling documentation, checked September 2026): https://www.sqlite.org/serverless.html
- SQLite temporary and sidecar file naming, -wal, -shm and -journal (rolling documentation, checked September 2026): https://www.sqlite.org/tempfiles.html
- SQLite Encryption Extension (licensed; the public build cannot read an encrypted file): https://www.sqlite.org/see/doc/trunk/www/readme.wiki
- SQLCipher (third-party encrypted-SQLite build): https://www.zetetic.net/sqlcipher/
- SQLite extension loading, disabled by default and enabled in the CLI (rolling documentation, checked September 2026): https://sqlite.org/loadext.html
- LiteFS configuration (http.addr, lease.advertise-url, default port 20202): https://fly.io/docs/litefs/config/
- LiteFS listener and configuration (pinned tag v0.5.14): default address, plain TCP and h2c server, h2c-only client, mount flags, environment expansion, default config search and explicit path, and example API bind. LiteFS listener and configuration sources (pinned tag v0.5.14): https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L32-L35, https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/config.go#L57, https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L76-L99, https://github.com/superfly/litefs/blob/v0.5.14/http/client.go#L32-L43. More LiteFS listener and configuration sources (pinned tag v0.5.14): https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/mount_linux.go#L76-L110, https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/config.go#L219-L233, https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/config.go#L288-L333, https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/etc/litefs.yml#L54-L58
- LiteFS route dispatch and reads (pinned tag v0.5.14): no credential gate, export including WAL pages, primary-only HTTP/2 stream, database enumeration and filtering, snapshots, position-map decoding, info, events, and unconditional debug routes including rand. LiteFS route dispatch and reads sources (pinned tag v0.5.14): https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L134-L268, https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L320-L346, https://github.com/superfly/litefs/blob/v0.5.14/db.go#L2682-L2776, https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L495-L520. More LiteFS route dispatch and reads sources (pinned tag v0.5.14): https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L526-L585, https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L686-L699, https://github.com/superfly/litefs/blob/v0.5.14/http/http.go#L15-L43, https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L271-L292. More LiteFS route dispatch and reads sources (pinned tag v0.5.14): https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L779-L803, https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/mount_linux.go#L487-L488, https://github.com/superfly/litefs/blob/v0.5.14/store.go#L1661-L1713
- LiteFS mutations and role checks (pinned tag v0.5.14): import handler and database method, replica primary context, local tx application and validation, per-database halt acquisition and release, expiration defaults and enforcement, and replication write locks. LiteFS mutations and role checks sources (pinned tag v0.5.14): https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L294-L318, https://github.com/superfly/litefs/blob/v0.5.14/db.go#L2779-L2811, https://github.com/superfly/litefs/blob/v0.5.14/store.go#L139-L141, https://github.com/superfly/litefs/blob/v0.5.14/store.go#L444-L478. More LiteFS mutations and role checks sources (pinned tag v0.5.14): https://github.com/superfly/litefs/blob/v0.5.14/store.go#L1904-L1910, https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L461-L493, https://github.com/superfly/litefs/blob/v0.5.14/db.go#L2387-L2448, https://github.com/superfly/litefs/blob/v0.5.14/db.go#L2452-L2609. More LiteFS mutations and role checks sources (pinned tag v0.5.14): https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L348-L407, https://github.com/superfly/litefs/blob/v0.5.14/db.go#L215-L325, https://github.com/superfly/litefs/blob/v0.5.14/store.go#L39-L41, https://github.com/superfly/litefs/blob/v0.5.14/store.go#L1455-L1465. More LiteFS mutations and role checks sources (pinned tag v0.5.14): https://github.com/superfly/litefs/blob/v0.5.14/store.go#L1525-L1531
- LiteFS leasing and handoff (pinned tag v0.5.14): promote eligibility, primary and subscriber checks, Consul URL derivation, static configuration and primary URL on replicas, replication destination, and static handoff refusal. LiteFS leasing and handoff sources (pinned tag v0.5.14): https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L409-L459, https://github.com/superfly/litefs/blob/v0.5.14/store.go#L408-L432, https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/mount_linux.go#L329-L348, https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/mount_linux.go#L241-L244. More LiteFS leasing and handoff sources (pinned tag v0.5.14): https://github.com/superfly/litefs/blob/v0.5.14/lease.go#L99-L131, https://github.com/superfly/litefs/blob/v0.5.14/store.go#L1384-L1387, https://github.com/superfly/litefs/blob/v0.5.14/lease.go#L168-L170
- LiteFS optional proxy and image (pinned tag v0.5.14): proxy startup condition and required fields, example proxy address, and Dockerfile without configuration or EXPOSE. LiteFS optional proxy and image sources (pinned tag v0.5.14): https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/mount_linux.go#L519-L524, https://github.com/superfly/litefs/blob/v0.5.14/http/proxy_server.go#L131-L144, https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/etc/litefs.yml#L60-L68, https://github.com/superfly/litefs/blob/v0.5.14/Dockerfile
- Go standard library defaults the LiteFS listener and debug routes inherit (a host-less or empty address listens on every unicast address, with the port chosen automatically when empty; expvar serves `cmdline` and `memstats`; pprof's `cmdline` responds with the running program's command line): https://pkg.go.dev/net#Listen, https://pkg.go.dev/expvar and https://pkg.go.dev/net/http/pprof
- Go h2c handler (ordinary HTTP/1 requests pass to the underlying handler): [NewHandler documentation](https://pkg.go.dev/github.com/golang/net/http2/h2c#NewHandler).
- Docker container reachability: [bridge peers and publication](https://docs.docker.com/engine/network/drivers/bridge/), [host networking](https://docs.docker.com/engine/network/drivers/host/), and [shared container networking stacks](https://docs.docker.com/engine/network/#container-networks).
- Litestream configuration (metrics addr, MCP mcp-addr) (Litestream MCP listener in v0.5.0 and later): https://litestream.io/reference/config/
- Turso SQL over HTTP (`/v2/pipeline`, bearer authentication): https://docs.turso.tech/sdk/http/reference
- Git v2.56.0 `gitignore` documentation (checked October 2026; tracked files are unaffected): https://github.com/git/git/blob/v2.56.0/Documentation/gitignore.adoc#L15-L18
- Git v2.56.0 `git-rm` documentation (checked October 2026; removal from the index alone or from the index and working tree): https://github.com/git/git/blob/v2.56.0/Documentation/git-rm.adoc#L17-L28
- Git v2.56.0 `git-log` documentation (checked October 2026; shows commit logs): https://github.com/git/git/blob/v2.56.0/Documentation/git-log.adoc#L16-L16
- GNU Coreutils v9.7 `stat` manual (checked October 2026; GNU syntax): [`-c` format](https://github.com/coreutils/coreutils/blob/v9.7/doc/coreutils.texi#L12989-L12995), [`%a` octal permissions](https://github.com/coreutils/coreutils/blob/v9.7/doc/coreutils.texi#L13046), [`%n` file name](https://github.com/coreutils/coreutils/blob/v9.7/doc/coreutils.texi#L13062), and [`%U` owner name](https://github.com/coreutils/coreutils/blob/v9.7/doc/coreutils.texi#L13073).

- GNU Bash reference manual bash-5.3 (checked October 2026): [single and double quotes (450-487)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n450); [pipelines, status negation, sequential and conditional lists, while, for, if and case (769-1084)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n769); [subshell and brace groups (1397-1440)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n1397); [positional parameters, quoted "$@", "$#" and "$?" (1866-1948)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n1866); [unset-only default expansion (2288-2300)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n2288); [word splitting and null IFS (2993-3015)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n2993).
- GNU Bash reference manual bash-5.3 (checked October 2026): [literal, wildcard, bracket and character-class patterns (3131-3200)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n3131); [exit status and EXIT traps (4350-4358)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n4350); [shift and test arguments and status (4582-4616)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n4582); [echo output (5216-5234)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5216); [set -- positional assignment (6182-6185)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n6182); [directory, string and integer conditions (8232-8405)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n8232).
- GNU Bash reference manual bash-5.3 (checked October 2026): [shortest prefix and suffix removal (2580-2617)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n2580); [printf formatting, string arguments and status (5466-5546)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5466); [input/output redirection and open failures (3280-3414)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n3280); [command-prefix assignments (3872-3880)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n3872); [trap reset and DEBUG/RETURN/ERR conditions (4737-4808)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n4737); [unset -n/-v and readonly failure (4852-4876)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n4852).
- GNU Bash reference manual bash-5.3 (checked October 2026): [declare -l lowercase conversion (5156-5159)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5156); [nameref, readonly and export attributes (5161-5195)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5161); [read line assignment and IFS (5548-5569)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5548); [read -p terminal prompt (5625-5627)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5625); [read -r literal backslashes and -s terminal echo suppression (5629-5637)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5629); [read NUL handling and failure status (5659-5669)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5659).
- GNU Bash reference manual bash-5.3 (checked October 2026): [set -a export attribute (5917-5921)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5917); [set -e and its exceptions (5929-5944)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5929); [set -x expanded-command tracing (6122-6128)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n6122); [plus options disable settings (6194-6203)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n6194); [history records shell-parser input (7274-7295)](https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n7274).
- curl curl-8_14_1 (checked October 2026): [-q as the first parameter suppresses curlrc (4-20)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/disable.md#L4-L20); [-g disables curl URL globbing (4-22)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/globoff.md#L4-L22); [--noproxy and the all-hosts wildcard (18-28)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/noproxy.md#L18-L28); [connection timeout, including DNS and handshakes (19-28)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/connect-timeout.md#L19-L28); [per-transfer timeout (21-27)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/max-time.md#L21-L27); [-s suppresses progress and errors, not requested output (4-25)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/silent.md#L4-L25).
- curl curl-8_14_1 (checked October 2026): [-S restores error messages with -s (4-19)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/show-error.md#L4-L19); [-w output and format substitutions (4-33)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/write-out.md#L4-L33); [write-out is independent of transfer success (49-53)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/write-out.md#L49-L53); [errormsg and exitcode added in 7.75.0 (75-79)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/write-out.md#L75-L79); [http_code is the last retrieved response code (105-107)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/write-out.md#L105-L107); [TLS verification by default; -k skips it (4-30)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/insecure.md#L4-L30).
- curl curl-8_14_1 (checked October 2026): [HTTP response codes do not indicate failure by default (24-28)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/fail.md#L24-L28); [-o /dev/null suppresses response bodies (4-53)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/output.md#L4-L53); [--data sends POST data (4-49)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/data.md#L4-L49); [-H/--header overrides internal headers, passes control characters verbatim, and @- reads one header per stdin line (24-49)](https://raw.githubusercontent.com/curl/curl/curl-8_14_1/docs/cmdline-opts/header.md).
- GNU grep documentation v3.12 (checked October 2026): [-f reads one pattern per line; - means stdin (197-207)](https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n197); [-l prints matching file names and stops at the first match per file (342-351)](https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n342); [default binary handling, suppression and matching limits (621-668)](https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n621). More GNU grep documentation v3.12 sources (checked October 2026): [-r recurses, follows command-line symlinks and skips encountered symlinks (757-769)](https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n757); [-- terminates options (788-794)](https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n788); [exit 0 for a match, 1 for none, 2 for error, with the -q exception (1110-1115)](https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n1110).
- GNU grep documentation v3.12 (checked October 2026): [-E selects extended regular expressions (1142-1148)](https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n1142); [-F selects fixed strings (1150-1156)](https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n1150); [ordinary regexp characters (1274-1277)](https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n1274); [{n,} repeats at least n times (1316-1320)](https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n1316); [bracket expressions match one listed character (1363-1373)](https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n1363).
- curl curl-8_14_1 behaviour used by this guide's probes: the cited `-q`, `-g` and `--noproxy '*'` controls suppress curlrc, URL globbing and proxies; `--connect-timeout 5` bounds connection setup and `--max-time 20` bounds each transfer. The cited `-sS` combination hides progress while retaining errors, `-o /dev/null` suppresses bodies, and `-w` prints the response code, transfer exit code and error text even on failure. HTTP status is separate from transfer success. For Turso, the cited `--data` selects POST and `-H 'Content-Type: application/json'` replaces curl's default content type; the request payload and the required anonymous/authorized outcomes remain this guide's procedure using the Turso reference, not curl's guarantee. The cited default TLS checks support the requirement never to add `-k`.


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- sqlite-rolling: SQLite documentation (rolling) (unknown)
- mcp: Litestream MCP minimum (v0.5.0)
- see: SQLite Encryption Extension (unknown)
- turso: Turso documentation (unknown)
- litestream: Litestream documentation (unknown)
- cipher: SQLCipher (unknown)
- litefs: LiteFS source (v0.5.14)
- litefs-docs: LiteFS documentation (unknown)
- go: Go library documentation (unknown)
- docker: Docker documentation (unknown)
- git: Git documentation (v2.56.0)
- coreutils: GNU Coreutils stat manual (v9.7)
- bash: GNU Bash reference manual (bash-5.3)
- curl: curl (curl-8_14_1)
- grep-docs: GNU grep documentation (v3.12)

Claims (full source mapping in the JSON block below):

- filesystem (REASONED; sqlite-rolling): No server, network listener or database-side authentication; filesystem authority controls access, including ATTACH. Treat files writable across security domains as suspect.
- extensions (REASONED; sqlite-rolling): Core extension loading defaults off, while the CLI enables it; enable only when required and load trusted libraries.
- web-files (REASONED; sqlite-rolling): Keep databases, sidecars, temporary files, exports and backups outside web-served paths; inspect aliases, symlinks, download routes and publishing, and do not rely on hidden names.
- git-files (REASONED; sqlite-rolling, git): Ignore database extensions and each -wal, -shm and -journal suffix before committing; ignore rules do not remove tracked files or history. This guide assesses committed database rows as permanently available to anyone who clones, even after a later deletion commit.
- permissions (REASONED; sqlite-rolling): Dedicated account, directory 700, database and existing sidecars 600, and launch umask 077; same-account processes and privileged users remain outside this isolation.
- temporary (REASONED; sqlite-rolling): Protect temporary files and backups; Unix SQLITE_TMPDIR needs an existing private directory and may fall back elsewhere. Do not delete live sidecars to repair permissions.
- encryption (REASONED; see, cipher): Public-domain SQLite has no file encryption; SEE is licensed and SQLCipher is a third-party alternative, otherwise use filesystem or volume encryption.
- encryption-keys (REASONED; see, sqlite-rolling): Keep keys outside databases and backups; SEE TEMP tables can be unencrypted. Treat credential-bearing copies as secrets and rotate credentials after a leak.
- turso-http (REASONED; turso): Turso serves libSQL over HTTPS at the database/organization turso.io URL using bearer authentication; TURSO_DATABASE_URL and TURSO_AUTH_TOKEN belong in application configuration, never a client bundle or git.
- turso-scope (REASONED; turso): db tokens create --read-only scopes away writes; --expiration accepts never or durations such as 7d3h. Prefer scoped, expiring tokens.
- replicas (REASONED; litestream): Litestream replicates to supported object stores; scope AWS credentials and IAM to the required bucket/prefix, keep replicas private, and restore with scoped credentials.
- metrics (REASONED; litestream): Litestream addr metrics listener defaults disabled; leave off unless needed, otherwise bind loopback, for example 127.0.0.1:9090.
- mcp (REASONED; mcp): Litestream MCP mcp-addr is documented for v0.5.0 and later, defaults disabled and has no built-in authentication; protect information and restore access with an authenticated tunnel/proxy, for example at loopback:3001.
- litefs-backups (REASONED; litefs-docs): LiteFS replicates among cluster nodes; its pre-1.0 documentation recommends separate off-site backups with private destinations.
- litefs-transport (REASONED; litefs, go): LiteFS v0.5.14 routes have no credential gate; the server accepts cleartext HTTP/1 and h2c, and its client uses h2c. Litefs-Id comparisons reject self-connections, not unauthenticated callers.
- litefs-bind (REASONED; litefs, go): http.addr defaults to host-less :20202, including the example; an empty address still listens on all interfaces at a system-chosen port.
- litefs-config (REASONED; litefs): Set API bind in the config file; no direct address flag. Search working directory, available home directory, then /etc/litefs.yml; -config overrides and -no-expand-env disables ${VAR} expansion.
- import (REASONED; litefs): POST /import creates or replaces a named database on the primary only; replicas return 503 before creation without forwarding, and DB.Import also checks primary status.
- export (REASONED; litefs): GET /export returns the full existing local database, including applicable WAL pages, on either role; missing databases return 404.
- stream (REASONED; litefs): POST /stream requires primary, HTTP/2 and a valid position map; replicas return 503. Unfiltered streams cover every database, filters narrow them, and fresh positions receive snapshots.
- tx (REASONED; litefs): POST /tx applies a validated LTX file to an existing local database on either role without forwarding, primary or halt-owner checks; non-snapshots must match next transaction/checksum, missing databases return 404.
- halt (REASONED; litefs): POST /halt on either role creates the database if absent and acquires write locks with a nonzero id, stalling primary writes or replica updates; DELETE releases an existing lock for a matching id.
- halt-ttl (REASONED; litefs): LiteFS halt-lock TTL defaults to 30 seconds.
- promote (REASONED; litefs): POST /promote needs an eligible candidate, succeeds unchanged for an existing primary, and asks a known primary for handoff from a candidate replica; no database name is required.
- handoff (REASONED; litefs): POST /handoff requires primary, a connected target subscriber and a handoff-capable lease; static leases refuse it and no database name is required.
- information (REASONED; litefs): GET /info, /events and /metrics disclose node, cluster and database state on either role without a named database.
- debug (REASONED; litefs, go): Unconditional /debug/pprof/ exposes command line and live profiles; /debug/vars exposes command line, memory and store database/lock state on either role without a database name.
- debug-rand (REASONED; litefs): /debug/rand streams deterministic pseudo-random data; its minute timeout is checked between writes and no server write timeout bounds a slow or non-reading client.
- cluster-private (REASONED; litefs, litefs-docs): Bind each LiteFS API to its private node address and restrict reachability to cluster nodes; never publish 20202 through an internet-facing mapping or proxy.
- consul-url (REASONED; litefs): Consul lease.advertise-url names each node private API; when unset it derives http:// plus lease.hostname or OS hostname and the actual listening port.
- static-url (REASONED; litefs): Static leasing uses lease.advertise-url as configured: the primary points at itself and each replica at the primary private API.
- container (REASONED; litefs, docker): LiteFS image supplies no configuration or EXPOSE; default wildcard binding applies within its namespace. Peers, host/shared networking, routing, firewall and publication determine reachability.
- proxy (REASONED; litefs): LiteFS application proxy is separate: proxy.target enables attempted startup, proxy.db and proxy.addr must be nonempty, example :8080; application TLS and authentication remain necessary.
- verify-download (REASONED; sqlite-rolling, bash, curl): Probe actual database/sidecar paths only after a successful application control; timeouts, DNS and proxy failures do not establish non-publication. No served application was available.
- verify-bundle (DEMONSTRATED; turso, bash, grep-docs): Local placeholder-token scan distinguished exposed and clean bundles and refused absent directories; readonly, nameref, lowercase and IFS cases are recorded. A clean scan covers only the searched forms and paths.
- verify-git (DEMONSTRATED; sqlite-rolling): Local throwaway repositories showed tracked/history copies survive ignore rules and index removal; a never-committed ignored file produced only rule matches. Git version is unrecorded.
- verify-modes (REASONED; sqlite-rolling, coreutils): SQLite 3.46.1 local WAL and rollback-journal runs showed umask 022 versus 077 modes; every file belonged to the test account, and separate application-account ownership was not exercised.
- verify-listeners (REASONED; litefs, litestream, mcp, bash, curl): Compare authorized private control with untrusted reachability for LiteFS or enabled Litestream metrics/MCP; any HTTP response shows a listener, not every backend route. Transport errors and failed controls are inconclusive; no isolated listener environment was available.
- verify-turso (REASONED; turso, bash, curl): Turso /v2/pipeline must return SELECT 1 with a valid bearer token and no successful result anonymously; HTTP 200 alone is insufficient and transport failure inconclusive. No database/token was available.
- halt-expiration (REASONED; litefs): LiteFS checks halt-lock expiration every 5 seconds.

````json
{
  "schema": 1,
  "checked": "2026-10-17",
  "documentation_checked": "2026-09",
  "body_sha256": "41cf1a6483130a8cb3c88137675ef214919774d781c49e63e0d0c38947c792b9",
  "components": {
    "sqlite-rolling": {
      "name": "SQLite documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s2721da91f8d2": "https://www.sqlite.org/serverless.html",
        "sf3d7f8391994": "https://www.sqlite.org/tempfiles.html",
        "s742deb3338bb": "https://sqlite.org/loadext.html",
        "sadf0431c1271": "https://www.sqlite.org/security.html"
      }
    },
    "mcp": {
      "name": "Litestream MCP minimum",
      "basis": "v0.5.0",
      "sources": {
        "sa5dddf04652c": "https://litestream.io/reference/config/"
      }
    },
    "see": {
      "name": "SQLite Encryption Extension",
      "basis": "unknown",
      "sources": {
        "sda3d8876503d": "https://www.sqlite.org/see/doc/trunk/www/readme.wiki"
      }
    },
    "turso": {
      "name": "Turso documentation",
      "basis": "unknown",
      "sources": {
        "sb32fd9c679e1": "https://docs.turso.tech/sdk/http/quickstart",
        "sfec4e734f423": "https://docs.turso.tech/cli/db/tokens/create",
        "se409838a474a": "https://docs.turso.tech/sdk/http/reference"
      }
    },
    "litestream": {
      "name": "Litestream documentation",
      "basis": "unknown",
      "sources": {
        "sec3d72af1447": "https://litestream.io/guides/",
        "s87fa51accafc": "https://litestream.io/guides/s3/",
        "sa5dddf04652c": "https://litestream.io/reference/config/"
      }
    },
    "cipher": {
      "name": "SQLCipher",
      "basis": "unknown",
      "sources": {
        "s57d83a42a74a": "https://www.zetetic.net/sqlcipher/"
      }
    },
    "litefs": {
      "name": "LiteFS source",
      "basis": "v0.5.14",
      "sources": {
        "s694a6ba8eafa": "https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L134-L268",
        "s864cacb8e7cc": "https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L76-L99",
        "s16da1761d6cc": "https://github.com/superfly/litefs/blob/v0.5.14/http/client.go#L32-L43",
        "sf0e982d0e36a": "https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/config.go#L57",
        "s9389d639da6b": "https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/etc/litefs.yml#L54-L58",
        "s475c28fd949e": "https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/mount_linux.go#L76-L110",
        "s055e15e84ba5": "https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/config.go#L219-L233",
        "s0b0bac964067": "https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/config.go#L288-L333",
        "s326a1007e5c2": "https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L294-L318",
        "s4547cc32557d": "https://github.com/superfly/litefs/blob/v0.5.14/db.go#L2779-L2811",
        "s85ece0e83d43": "https://github.com/superfly/litefs/blob/v0.5.14/store.go#L1904-L1910",
        "sa467eeb47f34": "https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L320-L346",
        "s5ffa5c20fc78": "https://github.com/superfly/litefs/blob/v0.5.14/db.go#L2682-L2776",
        "s02908966756d": "https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L495-L520",
        "sd63fa776fbc1": "https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L526-L585",
        "s1c51b7efc42d": "https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L686-L699",
        "scd0168363c1a": "https://github.com/superfly/litefs/blob/v0.5.14/http/http.go#L15-L43",
        "s298808a10d50": "https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L461-L493",
        "s7269cca8b0ea": "https://github.com/superfly/litefs/blob/v0.5.14/db.go#L2387-L2448",
        "sbd59a1af784e": "https://github.com/superfly/litefs/blob/v0.5.14/db.go#L2452-L2609",
        "sa199174f541b": "https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L348-L407",
        "s750403129022": "https://github.com/superfly/litefs/blob/v0.5.14/db.go#L215-L325",
        "s5009045b97e1": "https://github.com/superfly/litefs/blob/v0.5.14/store.go#L1525-L1531",
        "se2add54cf935": "https://github.com/superfly/litefs/blob/v0.5.14/store.go#L39-L41",
        "s59a2dfccd853": "https://github.com/superfly/litefs/blob/v0.5.14/store.go#L1455-L1465",
        "s246e6ad0d330": "https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L409-L459",
        "sae4ece3fbc87": "https://github.com/superfly/litefs/blob/v0.5.14/store.go#L408-L432",
        "s7bcb006d6884": "https://github.com/superfly/litefs/blob/v0.5.14/lease.go#L168-L170",
        "se1a41376a98d": "https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L271-L292",
        "s93c0ad91a567": "https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L779-L803",
        "s36792457dd64": "https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/mount_linux.go#L487-L488",
        "s7234e34af9ef": "https://github.com/superfly/litefs/blob/v0.5.14/store.go#L1661-L1713",
        "s4cebe21e711d": "https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/mount_linux.go#L329-L348",
        "sb43f5d78723c": "https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/mount_linux.go#L241-L244",
        "s8dfa3f10f3d3": "https://github.com/superfly/litefs/blob/v0.5.14/lease.go#L99-L131",
        "s83d8bd834347": "https://github.com/superfly/litefs/blob/v0.5.14/store.go#L1384-L1387",
        "s3284d1a3ecad": "https://github.com/superfly/litefs/blob/v0.5.14/Dockerfile",
        "s2b80fdf8adbe": "https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/mount_linux.go#L519-L524",
        "sc0568fe7e0ee": "https://github.com/superfly/litefs/blob/v0.5.14/http/proxy_server.go#L131-L144",
        "sf0d31f900082": "https://github.com/superfly/litefs/blob/v0.5.14/cmd/litefs/etc/litefs.yml#L60-L68",
        "s82103ee03d64": "https://github.com/superfly/litefs/blob/v0.5.14/http/server.go#L32-L35"
      }
    },
    "litefs-docs": {
      "name": "LiteFS documentation",
      "basis": "unknown",
      "sources": {
        "s13b9e92d9996": "https://fly.io/docs/litefs/",
        "sd7c0ba136b25": "https://fly.io/docs/litefs/config/"
      }
    },
    "go": {
      "name": "Go library documentation",
      "basis": "unknown",
      "sources": {
        "s6c5be8454523": "https://pkg.go.dev/github.com/golang/net/http2/h2c#NewHandler",
        "s37204ff1b27c": "https://pkg.go.dev/net#Listen",
        "se49529035a0c": "https://pkg.go.dev/expvar",
        "s0246034dddd1": "https://pkg.go.dev/net/http/pprof"
      }
    },
    "docker": {
      "name": "Docker documentation",
      "basis": "unknown",
      "sources": {
        "s881082f899b2": "https://docs.docker.com/engine/network/drivers/bridge/",
        "s6732393fd414": "https://docs.docker.com/engine/network/drivers/host/",
        "s00095bd02553": "https://docs.docker.com/engine/network/#container-networks"
      }
    },
    "git": {
      "name": "Git documentation",
      "basis": "v2.56.0",
      "sources": {
        "s12aad6467212": "https://github.com/git/git/blob/v2.56.0/Documentation/gitignore.adoc#L15-L18",
        "s8054ab09dc74": "https://github.com/git/git/blob/v2.56.0/Documentation/git-rm.adoc#L17-L28",
        "s9a6802adec89": "https://github.com/git/git/blob/v2.56.0/Documentation/git-log.adoc#L16-L16"
      }
    },
    "coreutils": {
      "name": "GNU Coreutils stat manual",
      "basis": "v9.7",
      "sources": {
        "s247df4545dc0": "https://github.com/coreutils/coreutils/blob/v9.7/doc/coreutils.texi#L12989-L12995",
        "sfd49553ab6e5": "https://github.com/coreutils/coreutils/blob/v9.7/doc/coreutils.texi#L13046",
        "sbd6f7cad7bf4": "https://github.com/coreutils/coreutils/blob/v9.7/doc/coreutils.texi#L13062",
        "s3e55a7242c33": "https://github.com/coreutils/coreutils/blob/v9.7/doc/coreutils.texi#L13073"
      }
    },
    "bash": {
      "name": "GNU Bash reference manual",
      "basis": "bash-5.3",
      "sources": {
        "s3711969be580": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n450",
        "s7fec9b923488": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n769",
        "s77b19e384d70": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n1397",
        "se4f37e01a249": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n1866",
        "s07f77f16f9f5": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n2288",
        "sbed8cd562a35": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n2993",
        "s7c9e44003867": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n3131",
        "s223b5c4d9a28": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n4350",
        "se02ece9163d4": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n4582",
        "s6067b2b1f78a": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5216",
        "sa506f1abd6a1": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n6182",
        "s7d29125b4005": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n8232",
        "s8962e63cfb20": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n2580",
        "s8a27e686ddfb": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5466",
        "s213f6d8d1f07": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n3280",
        "sf9757e9fd6e8": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n3872",
        "s8cbc1b4709e2": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n4737",
        "s3255eca7e496": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n4852",
        "s252aa2e81179": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5156",
        "s8447036b2114": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5161",
        "s5cab49305f3d": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5548",
        "s6e8ae812c1c3": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5625",
        "sb38bf74a89b0": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5629",
        "s260459961fbc": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5659",
        "s8c59508bd4c8": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5917",
        "s8016d1aecfca": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n5929",
        "se62fd3ad4fc3": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n6122",
        "s2df39d2c9c1c": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n6194",
        "s80e3246e96d8": "https://git.savannah.gnu.org/cgit/bash.git/tree/doc/bashref.texi?h=bash-5.3#n7274"
      }
    },
    "curl": {
      "name": "curl",
      "basis": "curl-8_14_1",
      "sources": {
        "s5b71321b79ea": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/disable.md#L4-L20",
        "sc405a4bffc27": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/globoff.md#L4-L22",
        "s345ec65025b0": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/noproxy.md#L18-L28",
        "sc9973c4ceec1": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/connect-timeout.md#L19-L28",
        "s7b6dca376156": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/max-time.md#L21-L27",
        "s156481f6b726": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/silent.md#L4-L25",
        "s07916104bf60": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/show-error.md#L4-L19",
        "sa937dbe5dd4a": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/write-out.md#L4-L33",
        "s021603e35e68": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/write-out.md#L49-L53",
        "s5e1383feef7d": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/write-out.md#L75-L79",
        "s39402f9cb25c": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/write-out.md#L105-L107",
        "sf2dcd83157a6": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/insecure.md#L4-L30",
        "s13f463154cea": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/fail.md#L24-L28",
        "s2f1ff2f6cacd": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/output.md#L4-L53",
        "sd3b039bafbf6": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/data.md#L4-L49",
        "s3db522258e44": "https://raw.githubusercontent.com/curl/curl/curl-8_14_1/docs/cmdline-opts/header.md"
      }
    },
    "grep-docs": {
      "name": "GNU grep documentation",
      "basis": "v3.12",
      "sources": {
        "s1733b640052b": "https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n197",
        "s99f121f5426a": "https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n342",
        "sbc8d05ab659b": "https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n621",
        "sfdd7a73eab39": "https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n757",
        "s7f9dc35e81c5": "https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n788",
        "s5170317ddea8": "https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n1110",
        "sc08d6af4d642": "https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n1142",
        "scd528c854b46": "https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n1150",
        "sb8be8b716426": "https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n1274",
        "s5d5af9297df2": "https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n1316",
        "se99a83dba3c5": "https://git.savannah.gnu.org/cgit/grep.git/tree/doc/grep.texi?h=v3.12#n1363"
      }
    }
  },
  "claims": {
    "filesystem": {"text": "No server, network listener or database-side authentication; filesystem authority controls access, including ATTACH. Treat files writable across security domains as suspect.", "components": ["sqlite-rolling"], "sources": ["sqlite-rolling:s2721da91f8d2", "sqlite-rolling:sadf0431c1271"], "status": "REASONED"},
    "extensions": {"text": "Core extension loading defaults off, while the CLI enables it; enable only when required and load trusted libraries.", "components": ["sqlite-rolling"], "sources": ["sqlite-rolling:s742deb3338bb"], "status": "REASONED"},
    "web-files": {"text": "Keep databases, sidecars, temporary files, exports and backups outside web-served paths; inspect aliases, symlinks, download routes and publishing, and do not rely on hidden names.", "components": ["sqlite-rolling"], "sources": ["sqlite-rolling:s2721da91f8d2", "sqlite-rolling:sf3d7f8391994"], "status": "REASONED"},
    "git-files": {"text": "Ignore database extensions and each -wal, -shm and -journal suffix before committing; ignore rules do not remove tracked files or history. This guide assesses committed database rows as permanently available to anyone who clones, even after a later deletion commit.", "components": ["sqlite-rolling", "git"], "sources": ["sqlite-rolling:sf3d7f8391994", "git:s12aad6467212", "git:s8054ab09dc74", "git:s9a6802adec89"], "status": "REASONED"},
    "permissions": {"text": "Dedicated account, directory 700, database and existing sidecars 600, and launch umask 077; same-account processes and privileged users remain outside this isolation.", "components": ["sqlite-rolling"], "sources": ["sqlite-rolling:s2721da91f8d2", "sqlite-rolling:sf3d7f8391994"], "status": "REASONED"},
    "temporary": {"text": "Protect temporary files and backups; Unix SQLITE_TMPDIR needs an existing private directory and may fall back elsewhere. Do not delete live sidecars to repair permissions.", "components": ["sqlite-rolling"], "sources": ["sqlite-rolling:sf3d7f8391994"], "status": "REASONED"},
    "encryption": {"text": "Public-domain SQLite has no file encryption; SEE is licensed and SQLCipher is a third-party alternative, otherwise use filesystem or volume encryption.", "components": ["see", "cipher"], "sources": ["see:sda3d8876503d", "cipher:s57d83a42a74a"], "status": "REASONED"},
    "encryption-keys": {"text": "Keep keys outside databases and backups; SEE TEMP tables can be unencrypted. Treat credential-bearing copies as secrets and rotate credentials after a leak.", "components": ["see", "sqlite-rolling"], "sources": ["see:sda3d8876503d", "sqlite-rolling:sf3d7f8391994"], "status": "REASONED"},
    "turso-http": {"text": "Turso serves libSQL over HTTPS at the database/organization turso.io URL using bearer authentication; TURSO_DATABASE_URL and TURSO_AUTH_TOKEN belong in application configuration, never a client bundle or git.", "components": ["turso"], "sources": ["turso:sb32fd9c679e1"], "status": "REASONED"},
    "turso-scope": {"text": "db tokens create --read-only scopes away writes; --expiration accepts never or durations such as 7d3h. Prefer scoped, expiring tokens.", "components": ["turso"], "sources": ["turso:sfec4e734f423"], "status": "REASONED"},
    "replicas": {"text": "Litestream replicates to supported object stores; scope AWS credentials and IAM to the required bucket/prefix, keep replicas private, and restore with scoped credentials.", "components": ["litestream"], "sources": ["litestream:sec3d72af1447", "litestream:s87fa51accafc"], "status": "REASONED"},
    "metrics": {"text": "Litestream addr metrics listener defaults disabled; leave off unless needed, otherwise bind loopback, for example 127.0.0.1:9090.", "components": ["litestream"], "sources": ["litestream:sa5dddf04652c"], "status": "REASONED"},
    "mcp": {"text": "Litestream MCP mcp-addr is documented for v0.5.0 and later, defaults disabled and has no built-in authentication; protect information and restore access with an authenticated tunnel/proxy, for example at loopback:3001.", "components": ["mcp"], "sources": ["mcp:sa5dddf04652c"], "status": "REASONED"},
    "litefs-backups": {"text": "LiteFS replicates among cluster nodes; its pre-1.0 documentation recommends separate off-site backups with private destinations.", "components": ["litefs-docs"], "sources": ["litefs-docs:s13b9e92d9996"], "status": "REASONED"},
    "litefs-transport": {"text": "LiteFS v0.5.14 routes have no credential gate; the server accepts cleartext HTTP/1 and h2c, and its client uses h2c. Litefs-Id comparisons reject self-connections, not unauthenticated callers.", "components": ["litefs", "go"], "sources": ["litefs:s694a6ba8eafa", "litefs:s864cacb8e7cc", "litefs:s16da1761d6cc", "go:s6c5be8454523"], "status": "REASONED"},
    "litefs-bind": {"text": "http.addr defaults to host-less :20202, including the example; an empty address still listens on all interfaces at a system-chosen port.", "components": ["litefs", "go"], "sources": ["litefs:sf0e982d0e36a", "litefs:s9389d639da6b", "go:s37204ff1b27c", "litefs:s82103ee03d64"], "status": "REASONED"},
    "litefs-config": {"text": "Set API bind in the config file; no direct address flag. Search working directory, available home directory, then /etc/litefs.yml; -config overrides and -no-expand-env disables ${VAR} expansion.", "components": ["litefs"], "sources": ["litefs:s475c28fd949e", "litefs:s055e15e84ba5", "litefs:s0b0bac964067"], "status": "REASONED"},
    "import": {"text": "POST /import creates or replaces a named database on the primary only; replicas return 503 before creation without forwarding, and DB.Import also checks primary status.", "components": ["litefs"], "sources": ["litefs:s326a1007e5c2", "litefs:s4547cc32557d", "litefs:s85ece0e83d43"], "status": "REASONED"},
    "export": {"text": "GET /export returns the full existing local database, including applicable WAL pages, on either role; missing databases return 404.", "components": ["litefs"], "sources": ["litefs:sa467eeb47f34", "litefs:s5ffa5c20fc78"], "status": "REASONED"},
    "stream": {"text": "POST /stream requires primary, HTTP/2 and a valid position map; replicas return 503. Unfiltered streams cover every database, filters narrow them, and fresh positions receive snapshots.", "components": ["litefs"], "sources": ["litefs:s02908966756d", "litefs:sd63fa776fbc1", "litefs:s1c51b7efc42d", "litefs:scd0168363c1a"], "status": "REASONED"},
    "tx": {"text": "POST /tx applies a validated LTX file to an existing local database on either role without forwarding, primary or halt-owner checks; non-snapshots must match next transaction/checksum, missing databases return 404.", "components": ["litefs"], "sources": ["litefs:s298808a10d50", "litefs:s7269cca8b0ea", "litefs:sbd59a1af784e"], "status": "REASONED"},
    "halt": {"text": "POST /halt on either role creates the database if absent and acquires write locks with a nonzero id, stalling primary writes or replica updates; DELETE releases an existing lock for a matching id.", "components": ["litefs"], "sources": ["litefs:sa199174f541b", "litefs:s750403129022", "litefs:s5009045b97e1"], "status": "REASONED"},
    "halt-ttl": {"text": "LiteFS halt-lock TTL defaults to 30 seconds.", "components": ["litefs"], "sources": ["litefs:se2add54cf935", "litefs:s59a2dfccd853"], "status": "REASONED"},
    "promote": {"text": "POST /promote needs an eligible candidate, succeeds unchanged for an existing primary, and asks a known primary for handoff from a candidate replica; no database name is required.", "components": ["litefs"], "sources": ["litefs:s246e6ad0d330", "litefs:sae4ece3fbc87"], "status": "REASONED"},
    "handoff": {"text": "POST /handoff requires primary, a connected target subscriber and a handoff-capable lease; static leases refuse it and no database name is required.", "components": ["litefs"], "sources": ["litefs:s246e6ad0d330", "litefs:s7bcb006d6884"], "status": "REASONED"},
    "information": {"text": "GET /info, /events and /metrics disclose node, cluster and database state on either role without a named database.", "components": ["litefs"], "sources": ["litefs:s694a6ba8eafa", "litefs:se1a41376a98d", "litefs:s93c0ad91a567"], "status": "REASONED"},
    "debug": {"text": "Unconditional /debug/pprof/ exposes command line and live profiles; /debug/vars exposes command line, memory and store database/lock state on either role without a database name.", "components": ["litefs", "go"], "sources": ["litefs:s694a6ba8eafa", "litefs:s36792457dd64", "litefs:s7234e34af9ef", "go:se49529035a0c", "go:s0246034dddd1"], "status": "REASONED"},
    "debug-rand": {"text": "/debug/rand streams deterministic pseudo-random data; its minute timeout is checked between writes and no server write timeout bounds a slow or non-reading client.", "components": ["litefs"], "sources": ["litefs:s694a6ba8eafa", "litefs:s864cacb8e7cc"], "status": "REASONED"},
    "cluster-private": {"text": "Bind each LiteFS API to its private node address and restrict reachability to cluster nodes; never publish 20202 through an internet-facing mapping or proxy.", "components": ["litefs", "litefs-docs"], "sources": ["litefs:s694a6ba8eafa", "litefs-docs:sd7c0ba136b25"], "status": "REASONED"},
    "consul-url": {"text": "Consul lease.advertise-url names each node private API; when unset it derives http:// plus lease.hostname or OS hostname and the actual listening port.", "components": ["litefs"], "sources": ["litefs:s4cebe21e711d"], "status": "REASONED"},
    "static-url": {"text": "Static leasing uses lease.advertise-url as configured: the primary points at itself and each replica at the primary private API.", "components": ["litefs"], "sources": ["litefs:s8dfa3f10f3d3", "litefs:s83d8bd834347", "litefs:sb43f5d78723c"], "status": "REASONED"},
    "container": {"text": "LiteFS image supplies no configuration or EXPOSE; default wildcard binding applies within its namespace. Peers, host/shared networking, routing, firewall and publication determine reachability.", "components": ["litefs", "docker"], "sources": ["litefs:s3284d1a3ecad", "docker:s881082f899b2", "docker:s6732393fd414", "docker:s00095bd02553"], "status": "REASONED"},
    "proxy": {"text": "LiteFS application proxy is separate: proxy.target enables attempted startup, proxy.db and proxy.addr must be nonempty, example :8080; application TLS and authentication remain necessary.", "components": ["litefs"], "sources": ["litefs:s2b80fdf8adbe", "litefs:sc0568fe7e0ee", "litefs:sf0d31f900082"], "status": "REASONED"},
    "verify-download": {"text": "Probe actual database/sidecar paths only after a successful application control; timeouts, DNS and proxy failures do not establish non-publication. No served application was available.", "components": ["sqlite-rolling", "bash", "curl"], "sources": ["sqlite-rolling:s2721da91f8d2", "sqlite-rolling:sf3d7f8391994", "bash:s3711969be580", "bash:s7fec9b923488", "bash:s77b19e384d70", "bash:se4f37e01a249", "bash:s07f77f16f9f5", "bash:sbed8cd562a35", "bash:s7c9e44003867", "bash:s223b5c4d9a28", "bash:se02ece9163d4", "bash:s6067b2b1f78a", "bash:sa506f1abd6a1", "bash:s7d29125b4005", "bash:s8962e63cfb20", "bash:s8a27e686ddfb", "curl:s5b71321b79ea", "curl:sc405a4bffc27", "curl:s345ec65025b0", "curl:sc9973c4ceec1", "curl:s7b6dca376156", "curl:s156481f6b726", "curl:s07916104bf60", "curl:sa937dbe5dd4a", "curl:s021603e35e68", "curl:s5e1383feef7d", "curl:s39402f9cb25c", "curl:sf2dcd83157a6", "curl:s13f463154cea", "curl:s2f1ff2f6cacd"], "status": "REASONED", "verify": [1]},
    "verify-bundle": {"text": "Local placeholder-token scan distinguished exposed and clean bundles and refused absent directories; readonly, nameref, lowercase and IFS cases are recorded. A clean scan covers only the searched forms and paths.", "components": ["turso", "bash", "grep-docs"], "sources": ["turso:sb32fd9c679e1", "bash:s3711969be580", "bash:s7fec9b923488", "bash:s77b19e384d70", "bash:se4f37e01a249", "bash:s07f77f16f9f5", "bash:sbed8cd562a35", "bash:s7c9e44003867", "bash:s223b5c4d9a28", "bash:se02ece9163d4", "bash:s6067b2b1f78a", "bash:sa506f1abd6a1", "bash:s7d29125b4005", "bash:s8a27e686ddfb", "bash:s213f6d8d1f07", "bash:sf9757e9fd6e8", "bash:s8cbc1b4709e2", "bash:s3255eca7e496", "bash:s252aa2e81179", "bash:s8447036b2114", "bash:s5cab49305f3d", "bash:s6e8ae812c1c3", "bash:sb38bf74a89b0", "bash:s260459961fbc", "bash:s8c59508bd4c8", "bash:s8016d1aecfca", "bash:se62fd3ad4fc3", "bash:s2df39d2c9c1c", "bash:s80e3246e96d8", "grep-docs:s1733b640052b", "grep-docs:s99f121f5426a", "grep-docs:sbc8d05ab659b", "grep-docs:sfdd7a73eab39", "grep-docs:s7f9dc35e81c5", "grep-docs:s5170317ddea8", "grep-docs:sc08d6af4d642", "grep-docs:scd528c854b46", "grep-docs:sb8be8b716426", "grep-docs:s5d5af9297df2", "grep-docs:se99a83dba3c5"], "status": "DEMONSTRATED", "evidence": "A bundle carrying the placeholder printed `dist/app.js` before `token-literal exit: 0` and again before `jwt-shape exit: 0`, and a clean bundle printed `1` for both.", "verify": [2]},
    "verify-git": {"text": "Local throwaway repositories showed tracked/history copies survive ignore rules and index removal; a never-committed ignored file produced only rule matches. Git version is unrecorded.", "components": ["sqlite-rolling"], "sources": ["sqlite-rolling:sf3d7f8391994"], "status": "DEMONSTRATED", "evidence": "With `app.db` committed before an `app.db*` ignore rule was added, `git check-ignore -v` listed the sidecars but not the tracked `app.db`. `git ls-files` printed `app.db`, and `git log` printed its commit.", "verify": [3]},
    "verify-modes": {"text": "SQLite 3.46.1 local WAL and rollback-journal runs showed umask 022 versus 077 modes; every file belonged to the test account, and separate application-account ownership was not exercised.", "components": ["sqlite-rolling", "coreutils"], "sources": ["sqlite-rolling:sf3d7f8391994", "coreutils:s247df4545dc0", "coreutils:sfd49553ab6e5", "coreutils:sbd6f7cad7bf4", "coreutils:s3e55a7242c33"], "status": "REASONED", "verify": [4]},
    "verify-listeners": {"text": "Compare authorized private control with untrusted reachability for LiteFS or enabled Litestream metrics/MCP; any HTTP response shows a listener, not every backend route. Transport errors and failed controls are inconclusive; no isolated listener environment was available.", "components": ["litefs", "litestream", "mcp", "bash", "curl"], "sources": ["litefs:s694a6ba8eafa", "litestream:sa5dddf04652c", "mcp:sa5dddf04652c", "bash:s3711969be580", "bash:s7fec9b923488", "bash:s77b19e384d70", "bash:se4f37e01a249", "bash:s07f77f16f9f5", "bash:sbed8cd562a35", "bash:s7c9e44003867", "bash:s223b5c4d9a28", "bash:se02ece9163d4", "bash:s6067b2b1f78a", "bash:sa506f1abd6a1", "bash:s7d29125b4005", "curl:s5b71321b79ea", "curl:sc405a4bffc27", "curl:s345ec65025b0", "curl:sc9973c4ceec1", "curl:s7b6dca376156", "curl:s156481f6b726", "curl:s07916104bf60", "curl:sa937dbe5dd4a", "curl:s021603e35e68", "curl:s5e1383feef7d", "curl:s39402f9cb25c", "curl:sf2dcd83157a6", "curl:s13f463154cea", "curl:s2f1ff2f6cacd"], "status": "REASONED", "verify": [5]},
    "verify-turso": {"text": "Turso /v2/pipeline must return SELECT 1 with a valid bearer token and no successful result anonymously; HTTP 200 alone is insufficient and transport failure inconclusive. No database/token was available.", "components": ["turso", "bash", "curl"], "sources": ["turso:se409838a474a", "bash:s3711969be580", "bash:s7fec9b923488", "bash:s77b19e384d70", "bash:se4f37e01a249", "bash:s07f77f16f9f5", "bash:sbed8cd562a35", "bash:s7c9e44003867", "bash:s223b5c4d9a28", "bash:se02ece9163d4", "bash:s6067b2b1f78a", "bash:sa506f1abd6a1", "bash:s7d29125b4005", "bash:s8962e63cfb20", "bash:s8a27e686ddfb", "bash:s213f6d8d1f07", "bash:sf9757e9fd6e8", "bash:s8cbc1b4709e2", "bash:s3255eca7e496", "bash:s252aa2e81179", "bash:s8447036b2114", "bash:s5cab49305f3d", "bash:s6e8ae812c1c3", "bash:sb38bf74a89b0", "bash:s260459961fbc", "bash:s8c59508bd4c8", "bash:s8016d1aecfca", "bash:se62fd3ad4fc3", "bash:s2df39d2c9c1c", "bash:s80e3246e96d8", "curl:s5b71321b79ea", "curl:sc405a4bffc27", "curl:s345ec65025b0", "curl:sc9973c4ceec1", "curl:s7b6dca376156", "curl:s156481f6b726", "curl:s07916104bf60", "curl:sa937dbe5dd4a", "curl:s021603e35e68", "curl:s5e1383feef7d", "curl:s39402f9cb25c", "curl:sf2dcd83157a6", "curl:s13f463154cea", "curl:sd3b039bafbf6", "curl:s3db522258e44"], "status": "REASONED", "verify": [6]},
    "halt-expiration": {"text": "LiteFS checks halt-lock expiration every 5 seconds.", "components": ["litefs"], "sources": ["litefs:se2add54cf935", "litefs:s59a2dfccd853"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
