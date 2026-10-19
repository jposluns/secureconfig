# Search engines for RAG: Meilisearch and Typesense

Written against Meilisearch release reference v1.53.2, Typesense 30.2, Caddy v2.11.4, curl minimum 7.75.0, Git grep manual 2.55.0, Git rev-list manual 2.56.0, and Git manual 2.56.0; 4 further sources carry no recorded version. Metadata reviewed 2026-10-12; documentation checked October 2026. The guide records 30 claims: 10 demonstrated by a check that ran and 20 reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

Both back RAG pipelines and site search. Meilisearch ships a keyless development mode meant for a laptop and answers unauthenticated until you set a master key; Typesense requires an operator-supplied bootstrap key from the moment it starts, with no keyless mode. Meilisearch's default admin key is full access except key management, and Typesense's bootstrap key is admin over all endpoints and data; ship an unprotected dev-mode instance, or leak either engine's privileged key, and the whole corpus, every document your RAG pipeline embedded, is readable and writable by whoever has it.

## Meilisearch

Meilisearch runs in two modes. In development mode it answers without a key by default, but development mode can still be protected by launching with `MEILI_MASTER_KEY` set; production mode requires it, together with `--env production`. Either way the master key (at least 16 bytes) is the credential everything else derives from. For a binary running beside its reverse proxy, set `MEILI_HTTP_ADDR=127.0.0.1:7700`; the binary's default is `localhost:7700` (as of v1.53.2, unless a `config.toml` in its working directory, which it reads without being asked, sets `http_addr`), but the official Docker image sets `MEILI_HTTP_ADDR=0.0.0.0:7700`, so with a host-side proxy publish the container port only on host loopback (`127.0.0.1:7700:7700`), and with a containerized proxy use a private container network without publishing the engine port.

At the time of writing, Meilisearch's master-key documentation describes four default API keys (a Default Search API Key, a Default Admin API Key with full access except key management, a Default Read-Only Admin API Key, and a Default Chat API Key); the inventory and permissions are version-dependent, so check `GET /keys` on your deployed release. It also supports scoped API keys you create yourself and tenant tokens: server-generated JWTs derived from an API key for per-end-user search restrictions, so set a short `exp` explicitly (no later than the parent key's expiry) rather than assuming they are short-lived. Expose the Default Search API Key only when every searchable index and document it permits is public; for confidential data, issue an index-restricted search key or a server-generated tenant token with enforced search rules, and keep the token's signing key server-side. Never put an admin key, the read-only admin key, or the master key in front-end code.

Meilisearch supports native HTTPS with `--ssl-cert-path` and `--ssl-key-path`; this guide uses a same-host TLS reverse proxy ([nginx.md](nginx.md), [caddy.md](caddy.md), [cloudflare.md](cloudflare.md)) and keeps the plaintext backend connection on loopback or an isolated local container network. If the proxy connects across machines, protect that hop with verified TLS as well, and restrict engine ingress to the proxy ([cloud-firewalls.md](cloud-firewalls.md)).

## Typesense

Typesense requires a bootstrap key at startup, set with the `--api-key` server parameter (a required parameter; the server will not start without it); that key has "admin permissions on all endpoints and data." Use the bootstrap key to create a separately revocable operational key through the `/keys` API, then use that operational key for routine administration; rotate the operational key through the API, while the bootstrap key remains a startup credential supplied through `TYPESENSE_API_KEY` or a protected configuration file rather than command-line arguments. Typesense listens on `0.0.0.0:8108` by default (as of v30.2; `--api-address`/`--api-port`), so for a same-host proxy set `--api-address=127.0.0.1 --api-port=8108`; its separate peering service defaults to port `8107`, so select a private peering address and restrict it to cluster members ([cloud-firewalls.md](cloud-firewalls.md)).

Create a parent search-only key through the same `/keys` endpoint:

```json
{
  "description": "Search products",
  "actions": ["documents:search"],
  "collections": ["products"]
}
```

For document or field restrictions, keep this parent key server-side and use a Typesense SDK there to derive a Scoped Search API Key containing the required `filter_by`, `include_fields`, or `exclude_fields`; send only the derived key to the browser, with an explicit `expires_at` no later than the parent key's expiry.

Narrow `collections` to a name or regex to limit a key to specific collections, embed a `filter_by` clause in a scoped key to restrict it to specific documents (Typesense: "Users will not be able to override the filter embedded inside the scoped API Key"), and use `include_fields`/`exclude_fields` to hide sensitive fields such as billing data from a given key. Typesense's own guidance is direct: "Never expose your Admin API Key or Bootstrap API Key to your frontend application as anyone with access to it will be able to write data into your collection." Set `expires_at` on browser-facing keys so a leaked one has a shelf life. Collection scoping does not by itself isolate data reachable through JOINs: review referenced collections and joined fields, enforce the intended restrictions in the key, and test joined queries with the browser credential.

Typesense's cloud offering terminates TLS for you. A self-managed cluster can also terminate TLS natively with the `--ssl-certificate` and `--ssl-certificate-key` server parameters; Typesense's production guidance still calls for restricting the public port and the private peering listener, and this guide defaults to the same reverse-proxy or platform TLS pattern as Meilisearch above because a proxy already handles certificate renewal, though native termination is a documented, supported alternative.

## The pattern, either engine

The credential that goes into a browser must be search-only, and for confidential or multi-tenant data must enforce the caller's index or collection and document restrictions in the credential itself (a tenant token in Meilisearch, a scoped key with `filter_by` in Typesense); browser-supplied filters are not authorization, and the parent key used to generate tenant tokens or scoped search keys must never be exposed. The admin or bootstrap key stays server-side, in the platform's secret store, never in client bundles or repository history ([secrets.md](secrets.md)).

Treat administration and backup as separate surfaces. Keep any dashboard or management UI private or behind an identity-aware proxy that enforces MFA, since an engine API key is a bearer credential and not a second factor; Meilisearch's development search preview is disabled in production mode. Protect dumps, snapshots, data volumes, and off-host backups independently of search authorization: restrict filesystem and object-store access, prohibit public downloads, and encrypt them, because a Meilisearch dump or a Typesense snapshot contains documents across every index. For Typesense, back up the directory its snapshot API produces rather than copying the live data directory, and restore into an isolated instance with authentication configured before exposing a listener.

Review outbound requests too. Meilisearch v1.8 through v1.34.0 need upgrading for an authenticated blind SSRF fixed in v1.34.1; on current releases do not set `MEILI_EXPERIMENTAL_ALLOWED_IP_NETWORKS=any`, restrict webhook and remote-service configuration to trusted administrators, protect webhook credentials, and constrain egress to approved destinations ([egress-metadata.md](egress-metadata.md)). Typesense's remote embedding configurations also make outbound requests carrying provider credentials, so apply the same destination and secret controls. Leave Meilisearch's experimental document-editing functions disabled unless needed; they run Rhai transformations that belong to trusted server-side workloads, not arbitrary operating-system command execution.

## Verify

REASONED: from the shell behaviour of the hidden prompt (`read -s`) and of `set +x`, not from the loopback runs described next, which did not test it. What was run: on 2026-10-13 UTC a QA review ran the paired-request block under `bash -x` with its external commands stubbed and a dummy secret fed to the prompts on a pseudo-terminal; no trace line carried the dummy secret, and the same block with its `set +x` removed traced it. A second run the same day pasted the block into Bash 5.3.9 (`bash --noprofile --norc -i`) on a pseudo-terminal with history enabled, with stub commands that read stdin and slept four seconds, a dummy secret entered at the prompts, and the observing and inspected processes under the same account: the history file held the pasted block, with its literal `$audit_key` references, but no prompt response, and neither `/proc/<pid>/cmdline` nor `/proc/<pid>/environ` of the stubs, the block's subshell or its command-substitution shells contained the dummy secret. In that run the observer was an ancestor of the inspected processes. A third run the same day, on the QA review's evaluation host, repeated the observation with same-account observers that were siblings of the block's shells rather than ancestors: neither `/proc/<pid>/cmdline` nor `/proc/<pid>/environ` of any sampled process, including the recording stubs, the command-substitution shells, the block's subshell and the outer shell, contained the dummy secret. What was not run: the contents of process memory are unknown, because every attempt by those observers to open `/proc/<pid>/mem` was refused with EACCES (Permission denied) on the evaluation host, where `/proc/sys/kernel/yama/ptrace_scope` read `1`; root was not tested as the observer, because the evaluation host refused privilege elevation (`sudo -n id` failed because the no-new-privileges flag was set); and no real curl request to a live Meilisearch or Typesense service ran, because `meilisearch` and `typesense-server` were not on the evaluation host's PATH (every run used a recording curl stub). In the paired-request block below, the hidden prompts keep the keys out of shell history and the block's `set +x` keeps them out of `set -x` tracing, but stdin closes the argv channel only, so the keys stay visible to the account owner and root. Paste each key alone at its hidden prompt: a multi-line paste feeds every line after the first to the next prompt or to your shell, which runs it.

DEMONSTRATED: following block; the checks below were demonstrated on loopback against the Meilisearch v1.53.2 release binary (its SHA-256 matched the digest GitHub publishes for the asset) and the Typesense 30.2 server (its MD5 matched the one in the release tarball), each with native TLS on 127.0.0.1, or behind a Caddy TLS proxy for the proxy checks, with certificates from a private test CA that curl trusted through `CURL_CA_BUNDLE`, and every address set before start. The blocks ran as printed with only their `set --` values substituted, and keys were fed to the prompts on stdin. What those runs do not show is marked **REASONED** where it occurs, with its reason. Backlog row 1.117 retains the real-client-build positive and negative controls for the credential scan below; its hand-built fixtures do not supply a real client bundle. Use Bash and curl 7.75.0 or later; never add `-k`. Substitute your actual HTTPS origin inside the single quotes, without a trailing slash. Run each row of the matrix below through this paired-request block, changing the method, path, JSON body, header prefix, and expected statuses on its `set --` line, and enter credentials at the prompts rather than in the command. Both requests use exactly the same origin, method, path, and body; inspect the engine JSON as well as the status, since a proxy login page, redirect, missing resource, or transport failure does not establish engine authorization.

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set -o pipefail
  { unset -n audit_role audit_key audit_expected audit_reply &&
    unset -v audit_role audit_key audit_expected audit_reply; } 2>/dev/null ||
    { echo 'A readonly audit_* variable is set in this shell'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'A readonly IFS is set in this shell'; exit 2; }
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_ORIGIN' \
    'POST' '/indexes/movies/search' '{"q":"ninja"}' \
    'Authorization: Bearer ' '401' '200'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'Paste the whole block'; exit 2; }
  shift
  [ "$#" -eq 7 ] || { echo 'Expected seven values'; exit 2; }
  case "$*" in
    *REPLACE_WITH_*) echo 'Substitute inside the single quotes'; exit 2 ;;
  esac
  case "$1" in
    https://?*) ;;
    *) echo 'Use your HTTPS origin, without a trailing slash'; exit 2 ;;
  esac
  case "$5" in
    'Authorization: Bearer '|'X-TYPESENSE-API-KEY: ') ;;
    *) echo 'Unknown authentication header'; exit 2 ;;
  esac
  for audit_role in negative positive; do
    printf '%s key (empty only for an anonymous negative): ' "$audit_role"
    IFS= read -r -s audit_key || exit 2
    printf '\n'
    case "$audit_key" in
      *REPLACE_WITH_*|*$'\r'*|*$'\n'*) echo 'Invalid key input'; exit 2 ;;
    esac
    if [ "$audit_role" = positive ]; then
      [ -n "$audit_key" ] || { echo 'Positive key required'; exit 2; }
      audit_expected=$7
    else
      audit_expected=$6
    fi
    if audit_reply=$(
      {
        if [ -n "$audit_key" ]; then
          printf '%s%s\n' "$5" "$audit_key"
        fi
      } | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        --request "$2" --header @- --header 'Content-Type: application/json' \
        --data-raw "$4" --write-out \
        '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n%{http_code}' \
        "$1$3"
    ); then
      printf '%s\n' "$audit_reply"
    else
      printf '%s\n' "${audit_reply-}" 'INCONCLUSIVE: transport failed'
      exit 2
    fi
    case "$audit_reply" in
      *$'\n'"$audit_expected") ;;
      *) echo 'FAIL: unexpected HTTP status'; exit 1 ;;
    esac
  done
  echo 'Statuses matched; inspect the response bodies before accepting the result.'
)
```

| Test | Method and path | JSON body | Negative credential/status | Positive credential/status | Marking |
|---|---|---|---|---|---|
| Meilisearch authentication | `POST /indexes/movies/search` | `{"q":"ninja"}` | Empty / `401` | Valid search key / `200`, containing the known fixture | REASONED: this row; a live Meilisearch or Typesense stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Anonymous keyless search is expected to return the fixture with 200; a protected search rejects anonymous access with 401 and permits the search key with 200, per the guide's cited Meilisearch master API keys (MEILI_MASTER_KEY, the four default API keys; rolling documentation, checked September 2026) entries. During marking review, the paired-request block passed bash -n and ShellCheck 0.11.0 without output; under bash -u with a recording curl stub, this row's status pair printed 'Statuses matched; inspect the response bodies before accepting the result.' (exit 0), a synthetic 999 printed 'FAIL: unexpected HTTP status' (exit 1), and a simulated transport failure printed 'INCONCLUSIVE: transport failed' (exit 2). Python json.loads accepted this row's JSON body. Stub responses establish only local control flow. |
| Typesense authentication | `GET /collections/products/documents/search?q=stark&query_by=company_name` | empty string | Empty / `401` | Valid search key / `200`, containing the known fixture | REASONED: this row; a live Meilisearch or Typesense stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. A disclosed operational key is expected to return the fixture with 200 before rotation; after rotation it is refused with 401 while its replacement returns 200, and anonymous access is refused with 401, per the guide's cited Typesense data access control (bootstrap api-key, /keys, actions, collections, filter_by, include_fields/exclude_fields, expires_at; rolling documentation, checked September 2026), Typesense 30.2 authorization failure (401) entries. During marking review, the paired-request block passed bash -n and ShellCheck 0.11.0 without output; under bash -u with a recording curl stub, this row's status pair printed 'Statuses matched; inspect the response bodies before accepting the result.' (exit 0), a synthetic 999 printed 'FAIL: unexpected HTTP status' (exit 1), and a simulated transport failure printed 'INCONCLUSIVE: transport failed' (exit 2). This row has an empty request body. Stub responses establish only local control flow. |
| Meilisearch write restriction | `POST /indexes` | `{"uid":"acl_probe"}` | Search-only key / `403` | Authorized admin key / `202` | REASONED: this row; a live Meilisearch or Typesense stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. An overprivileged browser key is expected to create an index with 202; the fixed search-only key is refused with 403 while an authorized admin key receives 202, which requires task-success confirmation, per the guide's cited Meilisearch master API keys (MEILI_MASTER_KEY, the four default API keys; rolling documentation, checked September 2026) entries. During marking review, the paired-request block passed bash -n and ShellCheck 0.11.0 without output; under bash -u with a recording curl stub, this row's status pair printed 'Statuses matched; inspect the response bodies before accepting the result.' (exit 0), a synthetic 999 printed 'FAIL: unexpected HTTP status' (exit 1), and a simulated transport failure printed 'INCONCLUSIVE: transport failed' (exit 2). Python json.loads accepted this row's JSON body. Stub responses establish only local control flow. |
| Typesense write restriction | `POST /collections` | `{"name":"acl_probe","fields":[{"name":"title","type":"string"}]}` | Search-only key / `401` | Authorized admin key / `201` | REASONED: this row; a live Meilisearch or Typesense stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. An overprivileged browser key is expected to create a collection with 201; the fixed search-only key is refused with 401 while the authorized admin key receives 201, per the guide's cited Typesense data access control (bootstrap api-key, /keys, actions, collections, filter_by, include_fields/exclude_fields, expires_at; rolling documentation, checked September 2026), Typesense 30.2 authorization failure (401), Typesense 30.2 collection creation success (201), Typesense 30.2 collections (collection creation and schema fields) entries. During marking review, the paired-request block passed bash -n and ShellCheck 0.11.0 without output; under bash -u with a recording curl stub, this row's status pair printed 'Statuses matched; inspect the response bodies before accepting the result.' (exit 0), a synthetic 999 printed 'FAIL: unexpected HTTP status' (exit 1), and a simulated transport failure printed 'INCONCLUSIVE: transport failed' (exit 2). Python json.loads accepted this row's JSON body. Stub responses establish only local control flow. |

REASONED: fixture preparation, task completion, rotation and tenant/JOIN comparisons; a live Meilisearch or Typesense stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. Keyless Meilisearch is expected to expose the fixture, while master-key protection refuses anonymous search; a disclosed Typesense key succeeds before rotation and fails afterwards while its replacement succeeds; an unrestricted parent returns the forbidden fixture and joined field, while the restricted credential returns the allowed fixture and omits the forbidden document and joined field even with filter and field-selection overrides, per the guide's cited Meilisearch master API keys (MEILI_MASTER_KEY, the four default API keys; rolling documentation, checked September 2026), Meilisearch tenant-token payload (exp is optional; rolling documentation, checked September 2026), Typesense data access control (bootstrap api-key, /keys, actions, collections, filter_by, include_fields/exclude_fields, expires_at; rolling documentation, checked September 2026) entries. During marking review, bash -n and ShellCheck 0.11.0 accepted the paired-request block without output and Python json.loads accepted all three matrix JSON bodies. Under bash -u with a curl stub, placeholder, HTTP or empty origin, unknown header, wrong marker, wrong value count and omitted assignment printed their guard refusals and exited 2 without calling curl; placeholder or carriage-return keys printed 'Invalid key input' (exit 2), and an empty positive key printed 'Positive key required' (exit 2) after the negative request. Each matrix row's synthetic status pair exited 0 with 'Statuses matched; inspect the response bodies before accepting the result.'; synthetic status 999 and transport failure printed 'FAIL: unexpected HTTP status' (exit 1) and 'INCONCLUSIVE: transport failed' (exit 2). These runs do not observe task success, rotation or tenant/JOIN enforcement. Use `Authorization: Bearer ` for Meilisearch and `X-TYPESENSE-API-KEY: ` for Typesense. Prepare the search fixtures first, and for the creation tests confirm `acl_probe` does not already exist, using a disposable resource and removing it afterward. A Meilisearch `202` only acknowledges a queued task, so confirm task success before crediting the positive control. In an isolated exposed-state test, keyless Meilisearch must return the fixture anonymously and the protected instance must reject that request; Typesense's exposed-state discriminator is a known disclosed bootstrap or operational key (it has no keyless mode), which after rotation must fail while its replacement succeeds against the same request. Do not invent a universal default password. Test tenant restrictions with known allowed and forbidden documents: the restricted credential must find the allowed fixture and omit the forbidden one, while an authorized control finds the forbidden fixture on the same query and origin; attempt to override filters and field selection, and test referenced collections where JOINs are used, since an empty result alone proves nothing.

The paired-request block turns off `allexport` and removes its own variables, namerefs included,
before it runs, because an earlier version printed `Statuses matched` and exited `0` without sending any
request when the calling shell held a readonly `audit_role`. On loopback, with a curl stand-in that
reported its environment, the block exited `2` with `A readonly audit_* variable is set in this shell` for
a readonly `audit_role` or `audit_expected`; kept both key roles for a nameref named `audit_role`; and kept
the prompted key out of curl's environment for an inherited `set -a`, an exported `audit_key`, a nameref
`audit_key` and `declare -i audit_key`. It still assumes an ordinary interactive shell: no alias on any word the block
uses, reserved words such as `if` included (an alias on `if` brought back the false pass with no request
sent, while the stock `ls`, `grep` and `ll` aliases left the result unchanged; `alias` lists what is
defined), no functions shadowing any builtin or command the block uses (including `unset`, `read`, `printf`
and `curl`), curl on `PATH` (with curl missing, a `command_not_found_handle` function that printed a newline
and the expected status brought back the false pass), no builtins disabled with `enable -n`, no `hash -p` entries, no hostile inherited
DEBUG trap (the block clears DEBUG, RETURN and ERR traps with `trap - DEBUG RETURN ERR`, but an inherited DEBUG trap under `set -T` still runs once before that line, and under `shopt -s extdebug` can skip it), and a paste at the prompt rather than inside a function. On the loopback runs, keyless Meilisearch returned the fixture to an anonymous search with `200`, so the
authentication row printed `FAIL: unexpected HTTP status`: the exposed state. With a master key set, the
same row got `401` `missing_authorization_header` anonymously and `200` with the fixture on the Default
Search API Key, and `GET /keys` listed the four default keys named above; the write row got `403`
`invalid_api_key` for the search key and `202` for the Default Admin API Key, whose task then reported
`succeeded`. Started with `--env production` and no master key, Meilisearch refused to start: "You must
provide a master key to secure your instance in a production environment". Typesense, with its
bootstrap key from `TYPESENSE_API_KEY`, answered the authentication row with `401` anonymously and `200`
on a collection-scoped search key, and the write row with `401` for that key and `201` for the
bootstrap key. A disclosed operational key got `200` before rotation, `401` after it was deleted, and
its replacement `200`. A Meilisearch tenant token filtered to one tenant returned only that tenant's
fixture, and a request adding a filter for the other tenant returned nothing, while the parent key
returned both; a Typesense scoped key embedding `filter_by` behaved the same way under an overriding
`filter_by`. For JOINs, a Typesense key scoped to collection `products` was refused a direct search of
`companies` with `401`, but a `products` search with `include_fields=$companies(billing)` returned the
joined company's billing field: collection scoping alone did not isolate joined data. A scoped key
embedding `exclude_fields=$companies(billing)` returned the same query without it.

REASONED: listener inventory, container publications, IPv4/IPv6 rules and external TCP reachability; a live Meilisearch or Typesense stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. No deployed container mappings, effective firewall rules or external disallowed vantage were available to this marking review. An exposed public API or peering listener is expected to accept an external TCP connection, while a fixed private backend gives no external answer and still answers its intended private client; refusal or timeout alone remains inconclusive, per the guide's cited Meilisearch v1.53.2 Dockerfile (image sets MEILI_HTTP_ADDR=0.0.0.0:7700), Typesense 30.2 server configuration (api-key required, api-address default 0.0.0.0, api-port 8108, peering-port 8107, ssl-certificate), OpenBSD netcat reference entries. During marking review, bash -n and ShellCheck 0.11.0 accepted the TCP block without output. Under bash -u with an nc stub, placeholder and empty addresses printed 'Substitute your address inside the quotes', a wrong marker printed 'Paste the whole block', and a missing address printed 'Expected one address'; each exited 2 without calling nc. Stub success printed 'FAIL: TCP 7700 is reachable' (exit 1); stub failure printed 'INCONCLUSIVE: inspect the connection error and firewall evidence' for all three ports (exit 2). A separate ss stub printed 'ss <-ltnp>'; this checks argument delivery, not listener state. For the retained same-host TLS comparison, exposed keyless Meilisearch or a disclosed Typesense key is expected to permit search through the proxy; fixed routes refuse anonymous or revoked credentials and permit an authorized key, per the guide's cited Caddy bind, certificate files, automatic HTTPS and admin options, and reverse-proxy configuration (pinned tag v2.11.4), Meilisearch master API keys (MEILI_MASTER_KEY, the four default API keys; rolling documentation, checked September 2026), Typesense data access control (bootstrap api-key, /keys, actions, collections, filter_by, include_fields/exclude_fields, expires_at; rolling documentation, checked September 2026) entries. The following historical authoring limitations remain unchanged. **The same-host TLS proxy demonstrated; container mappings, IPv6, firewalls and a wildcard bind REASONED
(one host with no container runtime, no second network, and no root or `sudo` to read the rulesets, and
the host forbids binding every interface):** proxy authentication does not prove the engine or
peering ports are private. On the engine host inspect `ss -ltnp`, container port mappings, and the effective IPv4 and IPv6 firewall rules, and confirm the engine answers from its intended private client while running. From an external disallowed source, test every public address and actual published port; the block below covers the default ports with OpenBSD-compatible netcat and numeric addresses:

REASONED: following block; external isolation follows the cited server configuration and OpenBSD netcat documentation; no second network, container runtime, or firewall-rule access was available. Recorded loopback outcomes do not establish external isolation.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PUBLIC_IP'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'Paste the whole block'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'Expected one address'; exit 2; }
  case "$1" in
    ''|*REPLACE_WITH_*) echo 'Substitute your address inside the quotes'; exit 2 ;;
  esac
  for audit_port in 7700 8108 8107; do
    if nc -nvz -w 5 "$1" "$audit_port"; then
      echo "FAIL: TCP $audit_port is reachable"
      exit 1
    else
      echo "INCONCLUSIVE: inspect the connection error and firewall evidence"
    fi
  done
  exit 2
)
```

REASONED: preceding block; external TCP interpretation and intentionally public native-HTTPS authorization; a live Meilisearch or Typesense stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. No external disallowed vantage, deployed listener inventory, effective firewall rules or certificate-valid public engine endpoint was available to this marking review. An exposed private-backend deployment permits external TCP connections; the fixed backend gives no external answer while its private positive control answers, per the guide's cited Meilisearch v1.53.2 Dockerfile (image sets MEILI_HTTP_ADDR=0.0.0.0:7700), Typesense 30.2 server configuration (api-key required, api-address default 0.0.0.0, api-port 8108, peering-port 8107, ssl-certificate), OpenBSD netcat reference entries. For intentionally public HTTPS, exposed keyless Meilisearch or a disclosed Typesense key returns data; fixed authorization denies anonymous or revoked credentials and permits the authorized control, per the guide's cited Meilisearch master API keys (MEILI_MASTER_KEY, the four default API keys; rolling documentation, checked September 2026), Typesense data access control (bootstrap api-key, /keys, actions, collections, filter_by, include_fields/exclude_fields, expires_at; rolling documentation, checked September 2026), Typesense 30.2 authorization failure (401), curl options (write-out variables require 7.75.0+) entries. During marking review, bash -n and ShellCheck 0.11.0 accepted the TCP block without output. Under bash -u with an nc stub, placeholder and empty addresses printed 'Substitute your address inside the quotes', a wrong marker printed 'Paste the whole block', and a missing address printed 'Expected one address'; each exited 2 without calling nc. Stub success printed 'FAIL: TCP 7700 is reachable' (exit 1); stub failure printed 'INCONCLUSIVE: inspect the connection error and firewall evidence' for all three ports (exit 2). The paired-request block also passed bash -n and ShellCheck 0.11.0 without output; under bash -u with a curl stub, both authentication rows printed 'Statuses matched; inspect the response bodies before accepting the result.' (exit 0), synthetic 999 printed 'FAIL: unexpected HTTP status' (exit 1), and simulated transport failure printed 'INCONCLUSIVE: transport failed' (exit 2). Stubs do not establish TLS, authorization or network isolation. Under the private-backend pattern, any successful external TCP connection is a finding, even if HTTP authentication would reject the caller; a timeout is inconclusive, and a refusal shows only no connection from that source at that moment, so corroborate it with the live private positive control, the listener bindings, and the effective firewall policy. If native HTTPS is intentionally public, run the paired authorization tests against that engine endpoint too, using its certificate-valid hostname and actual port (preserve the hostname with curl's `--resolve` when testing an IP, keep the substituted address guarded, and retain certificate verification); engine API TLS does not establish protection of Typesense's separate peering listener.

On loopback, the harness's `ss -tulnp` listener check, run at every engine start, showed Typesense
only on `127.0.0.1:8108` and `127.0.0.1:8107`; the exposed half, a wildcard bind such as Typesense's
default `0.0.0.0:8108`, was not observed. The block against
127.0.0.1, where the engines listened, printed `FAIL: TCP 7700 is reachable` (exit `1`), the reachable
shape; against 127.0.0.2, where nothing listens, each port's `Connection refused` printed `INCONCLUSIVE`
and the block ended with exit `2`, the refused shape. A real external vantage is REASONED for the same
reason. Behind Caddy v2.11.4 (the release tarball, its SHA-256 equal to GitHub's published digest) on `127.0.0.1:8443` with `bind 127.0.0.1`, `auto_https off`, the admin API off and TLS files from the test CA,
terminating TLS in front of Meilisearch's plaintext backend on `127.0.0.1:7700`, the paired block's
authentication row got `401` anonymously and `200` on the search key through the proxy. Behind the same
proxy, keyless Meilisearch made the block print `FAIL: unexpected HTTP status` on an anonymous `200`, the
exposed state, and Typesense with its plaintext backend on `127.0.0.1:8108` gave `401` anonymously then `200` on a collection-scoped search key.

REASONED: search each admin, master or bootstrap key before deploying a client build, using the repository's `tools/scan_credential.sh` credential scanner. The cited Git manuals define the literal file and commit-tree searches; the engine references require privileged keys to stay server-side. The scanner is part of the [secureconfig repository](https://github.com/jposluns/secureconfig) itself, at `tools/scan_credential.sh`, from the merge of [PR #450](https://github.com/jposluns/secureconfig/pull/450) onward; it is not included in the published site or the plugin. Use a full clone of the repository, record the commit you ran, and read the script before giving it a real key.

DEMONSTRATED: `tools/test_scan_credential.py` is the regression evidence for the repository tool, run with Bash 5.3.9 and Git 2.55.0 on disposable repositories: literal output and historical matches returned FOUND/1; absence and the named omission fixtures returned NOT FOUND/0; invalid inputs, unsafe output entries, Git diagnostics and incomplete searches returned INCONCLUSIVE/2. These are fixture observations, not real application builds; bounded sampling of the scanner's and its children's argv and environment during live scans found no key, and such sampling is no proof against exposure between samples or through process memory.

REASONED: following block; no real application build is available in the authoring environment. From a trusted fresh shell with BASH_ENV unset, substitute the two checkout paths and the relative build directory, then enter one key alone on a line at the silent read; repeat for each key. Bash 4.3+, trusted Bash/Git executables and Git configuration, a finished build and a quiet repository are prerequisites. In a disposable real build, seed a dummy key and require FOUND/1, remove it and rebuild and require NOT FOUND/0; retain a separate old-commit positive control. Those real-build controls remain unobserved under row 1.117.

```bash
(cd /path/to/project && bash /path/to/secureconfig/tools/scan_credential.sh ./dist)
```

REASONED: the tool's three outcomes are FOUND/1 (remove and rotate the credential), NOT FOUND/0 (only the scope below) and INCONCLUSIVE/2 (a refusal or incomplete search, taking precedence over earlier matches). It prints matching names, which can themselves contain a key, but never matching content or Git diagnostics. To identify the first failed prerequisite without entering a key, add `--explain` before the output argument; its categories disclose no paths. A READY result checks prerequisites only, not content. Interrupted runs without a final outcome remain inconclusive.

- REASONED: Git grep searches raw output bytes and regular-file blobs in commits from `git rev-list --all --reflog`; it neither decodes gzip/Brotli nor reconstructs encoded, escaped, split or runtime-injected keys.
- REASONED: Git tree searches omit committed symlink targets, submodule contents and LFS payloads; the output walk refuses symlinks, special/unreadable entries, empty output and any ASCII-case `.git` component.
- REASONED: Git's commit enumeration omits unreachable objects, expired reflogs, omitted shallow/unfetched history, other-worktree private refs and objects present in no commit tree, including tags directly pointing at blobs; keys present only in commit or tag messages, author, committer or tagger identities, reflog messages, ref names or path names are not searched.
- REASONED: Git replacement refs and grafts can hide original content or ancestry; only the resulting Git view is searched.
- REASONED: a concurrent file change can evade the walk; commit lists consume memory and each commit needs a separate Git search, so resource exhaustion can interrupt completion.
- REASONED: stdin avoids key-bearing child arguments and files; it does not protect process memory or pipes from the same account/root, or compensate for hostile shell startup files or executables.

## Common mistakes

- Shipping a Meilisearch instance without `MEILI_MASTER_KEY` and `--env production` because dev mode "worked fine" in testing.
- Putting the Typesense bootstrap key or Meilisearch admin key straight into front-end JavaScript instead of minting a scoped search key.
- A scoped key with no `filter_by` or `collections` restriction, which searches everything the admin key can see.

## Sources (checked October 2026)

Version scope: Typesense 30.2; Meilisearch current unversioned documentation checked 2026-09-18, with v1.53.2 as the release reference. The first release containing all four default keys and their exact permissions remains to be confirmed against the deployed release, so inspect `GET /keys`. The Verify commands require Bash, curl 7.75.0 or later, OpenBSD-compatible netcat and Git; the credential scan was exercised with Bash 5.3.9 and Git 2.55.0.

- Meilisearch master API keys (MEILI_MASTER_KEY, the four default API keys; rolling documentation, checked September 2026): https://www.meilisearch.com/docs/resources/self_hosting/security/master_api_keys
- Typesense data access control (bootstrap api-key, /keys, actions, collections, filter_by, include_fields/exclude_fields, expires_at; rolling documentation, checked September 2026): https://typesense.org/docs/guide/data-access-control.html
- Typesense 30.2 server configuration (api-key required, api-address default 0.0.0.0, api-port 8108, peering-port 8107, ssl-certificate): https://typesense.org/docs/30.2/api/server-configuration.html
- Typesense `api-address` default `0.0.0.0`, `api-port` default 8108 and `peering-port` default 8107 (pinned tag v30.2): https://github.com/typesense/typesense/blob/v30.2/src/typesense_server_utils.cpp#L81-L85
- Typesense 30.2 API keys (parent search-only key, scoped-key derivation, description): https://typesense.org/docs/30.2/api/api-keys.html
- Typesense 30.2 collections (collection creation and schema fields): https://typesense.org/docs/30.2/api/collections.html
- Typesense 30.2 authorization failure (401): https://raw.githubusercontent.com/typesense/typesense/v30.2/src/http_server.cpp
- Typesense 30.2 collection creation success (201): https://raw.githubusercontent.com/typesense/typesense/v30.2/src/core_api.cpp
- Typesense backups (snapshot API, not the live data directory; rolling documentation, checked September 2026): https://typesense.org/docs/guide/backups.html
- Typesense 30.2 remote embeddings (outbound requests with provider credentials): https://typesense.org/docs/30.2/api/vector-search.html
- Meilisearch configuration reference (MEILI_HTTP_ADDR default localhost:7700; MEILI_EXPERIMENTAL_ALLOWED_IP_NETWORKS; rolling documentation, checked September 2026): https://www.meilisearch.com/docs/resources/self_hosting/configuration/reference
- Meilisearch `DEFAULT_HTTP_ADDR` "localhost:7700" and the `--http-addr` / `MEILI_HTTP_ADDR` option that defaults to it, and the implicit `./config.toml` read whose values yield to the environment and the command line (pinned tag v1.53.2): https://github.com/meilisearch/meilisearch/blob/v1.53.2/crates/meilisearch/src/option.rs#L95-L97, https://github.com/meilisearch/meilisearch/blob/v1.53.2/crates/meilisearch/src/option.rs#L221-L223 and https://github.com/meilisearch/meilisearch/blob/v1.53.2/crates/meilisearch/src/option.rs#L534-L560
- Meilisearch v1.53.2 Dockerfile (image sets MEILI_HTTP_ADDR=0.0.0.0:7700): https://raw.githubusercontent.com/meilisearch/meilisearch/v1.53.2/Dockerfile
- Meilisearch native TLS (--ssl-cert-path, --ssl-key-path; rolling documentation, checked September 2026): https://www.meilisearch.com/docs/resources/self_hosting/security/http2_ssl
- Meilisearch tenant-token payload (exp is optional; rolling documentation, checked September 2026): https://www.meilisearch.com/docs/capabilities/security/advanced/tenant_token_payload
- Meilisearch backups and dumps (documents across every index; rolling documentation, checked September 2026): https://www.meilisearch.com/docs/resources/self_hosting/data_backup/overview
- Meilisearch SSRF advisory (authenticated blind SSRF fixed in v1.34.1): https://www.meilisearch.com/blog/CVE-update-Jan-2026
- Meilisearch document-editing functions (Rhai; disabled unless enabled; rolling documentation, checked September 2026): https://www.meilisearch.com/docs/capabilities/indexing/how_to/edit_documents_with_functions
- curl options (write-out variables require 7.75.0+): https://curl.se/docs/manpage.html
- OpenBSD netcat reference: https://man.openbsd.org/nc
- Caddy bind, certificate files, automatic HTTPS and admin options, and reverse-proxy configuration (pinned tag v2.11.4): https://github.com/caddyserver/caddy/blob/v2.11.4/caddyconfig/httpcaddyfile/builtins.go#L58-L88, https://github.com/caddyserver/caddy/blob/v2.11.4/caddyconfig/httpcaddyfile/options.go#L347-L381, https://github.com/caddyserver/caddy/blob/v2.11.4/caddyconfig/httpcaddyfile/options.go#L459-L476, https://raw.githubusercontent.com/caddyserver/caddy/v2.11.4/modules/caddyhttp/reverseproxy/caddyfile.go

- Git grep manual (page last updated in 2.55.0; fixed strings, pattern files, binary text, names only, no-index and tree operands; supplied excerpts checked October 2026): https://git-scm.com/docs/git-grep
- Git rev-list manual (page last updated in 2.56.0; all refs, HEAD and reflogs; supplied excerpts checked October 2026): https://git-scm.com/docs/git-rev-list
- Git manual (page last updated in 2.56.0; --no-pager disables paging; supplied excerpt checked October 2026): https://git-scm.com/docs/git


<!-- version-basis:start -->
## About the AI assistant section below

The rest of this file is generated by the repository's tooling and written for AI assistants rather than for people. It records the versions this guide was written against, the guide's claims with a status for each (demonstrated by a check that ran, or reasoned from the cited sources), and the mapping from each claim to its sources. You are welcome to read it, but it is dense and can be hard to take in.

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/search-engines.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- meili: Meilisearch release reference (v1.53.2)
- typesense: Typesense (30.2)
- meili-docs: Meilisearch documentation (rolling) (unknown)
- meili-advisory: Meilisearch SSRF advisory (unknown)
- typesense-docs: Typesense documentation (rolling) (unknown)
- caddy: Caddy (v2.11.4)
- curl: curl minimum (7.75.0)
- nc: OpenBSD-compatible netcat (unknown)
- git-grep: Git grep manual (2.55.0)
- git-rev-list: Git rev-list manual (2.56.0)
- git: Git manual (2.56.0)

Claims (full source mapping in the JSON block below):

- meili-mode (REASONED; meili-docs): Development is keyless unless MEILI_MASTER_KEY is set; production requires a master key of at least 16 bytes.
- meili-bind (REASONED; meili): Binary defaults localhost:7700 unless implicit config.toml overrides it; environment and CLI override the file.
- meili-image (REASONED; meili): Official image sets MEILI_HTTP_ADDR=0.0.0.0:7700; publish only host loopback or use an unpublished private proxy network.
- meili-keys (REASONED; meili-docs): Four default keys and their permissions are version-dependent; inspect GET /keys and keep admin, read-only admin and master keys server-side.
- meili-tenant (REASONED; meili-docs): For confidential search, restrict indexes or issue tenant JWTs with enforced rules; keep the signing key server-side and set exp no later than parent expiry.
- meili-tls (REASONED; meili-docs): Native HTTPS uses ssl-cert-path and ssl-key-path; the proxy pattern confines plaintext locally and verifies TLS across machines.
- typesense-bootstrap (REASONED; typesense, typesense-docs): Bootstrap api-key is required and controls all endpoints/data; supply it through TYPESENSE_API_KEY or a protected file and use a revocable operational key routinely.
- typesense-api (REASONED; typesense): API defaults 0.0.0.0:8108; set api-address=127.0.0.1 and api-port=8108 for a same-host proxy.
- typesense-peer (REASONED; typesense): Separate peering defaults to 8107; select a private address and admit only cluster members.
- typesense-scope (REASONED; typesense, typesense-docs): Parent search key uses documents:search and named/regex collections; derive browser keys with filter_by and field restrictions, keeping the parent server-side.
- typesense-expiry (REASONED; typesense-docs): Set expires_at on browser keys no later than parent expiry; collection scope alone does not isolate JOIN data.
- typesense-tls (REASONED; typesense): Self-managed native TLS uses ssl-certificate and ssl-certificate-key; cloud terminates TLS; restrict API and peering access independently.
- admin-surface (REASONED; meili-docs, typesense-docs): Keep management UIs private or behind MFA; engine bearer keys are not a second factor and Meilisearch production disables the development preview.
- backup (REASONED; meili-docs, typesense-docs): Protect and encrypt dumps, snapshots, volumes and backups; Typesense backs up snapshot output rather than the live directory and restores privately with auth.
- meili-egress (REASONED; meili-docs, meili-advisory): Upgrade Meilisearch v1.8 through v1.34.0 for SSRF fixed in v1.34.1; avoid allowed-IP-networks=any and restrict remote/webhook administration and egress.
- typesense-egress (REASONED; typesense): Remote embeddings send provider credentials outbound; restrict destinations and protect those secrets.
- meili-functions (REASONED; meili-docs): Leave experimental document-editing functions disabled unless needed; Rhai transformations belong to trusted workloads, not arbitrary OS execution.
- verify-meili-auth (DEMONSTRATED; meili-docs): Loopback keyless search returned 200; protected search returned anonymous 401 and keyed 200 with the fixture.
- verify-meili-write (DEMONSTRATED; meili-docs): Search key was refused index creation with 403; Default Admin received 202 and the task succeeded.
- verify-meili-production (DEMONSTRATED; meili-docs): Production startup without a master key was refused in the recorded run.
- verify-typesense-auth (DEMONSTRATED; typesense, typesense-docs): Loopback Typesense refused anonymous search with 401 and returned the fixture with a collection-scoped key and 200.
- verify-typesense-write (DEMONSTRATED; typesense): Search-key collection creation returned 401; bootstrap creation returned 201.
- verify-rotation (DEMONSTRATED; typesense): Disclosed Typesense operational key succeeded before deletion, failed after deletion, and its replacement succeeded.
- verify-tenant (DEMONSTRATED; meili-docs, typesense-docs): Tenant token and scoped-key filters resisted other-tenant overrides while parent controls returned both fixtures.
- verify-join (DEMONSTRATED; typesense-docs): Collection-scoped key leaked a joined billing field; an embedded exclude_fields restriction removed it.
- verify-proxy (DEMONSTRATED; meili-docs, typesense-docs, caddy): Recorded same-host Caddy TLS proxy preserved anonymous/keyed auth distinctions for both engines; no external isolation is established.
- verify-request (REASONED; curl, meili-docs, typesense-docs): Paired requests require Bash, curl 7.75.0+, verified HTTPS and identical origin/method/path/body; inspect engine JSON, not status alone.
- verify-external (REASONED; meili, typesense, nc): Inventory actual listeners, publications and IPv4/IPv6 rules; external TCP success fails, while refusal/timeout needs live private controls and policy evidence.
- verify-local-tcp (DEMONSTRATED; nc): Recorded netcat loopback reachable/refused shapes returned FAIL/exit 1 and INCONCLUSIVE/exit 2 respectively; external reachability remains unobserved.
- verify-bundle (REASONED; meili-docs, typesense-docs, git-grep, git-rev-list, git): Repository credential scanner searches literal output and local commit-tree content; regression fixtures ran, while real-client-build controls remain unobserved.

````json
{
  "schema": 1,
  "checked": "2026-10-12",
  "documentation_checked": "2026-10",
  "body_sha256": "98bf2bbbb774a4c7e71ec7f07b9035b6127771baa4c953d0b35d251f59f0b34c",
  "components": {
    "meili": {
      "name": "Meilisearch release reference",
      "basis": "v1.53.2",
      "sources": {
        "sbed426856353": "https://github.com/meilisearch/meilisearch/blob/v1.53.2/crates/meilisearch/src/option.rs#L95-L97",
        "sa5636634c0e5": "https://github.com/meilisearch/meilisearch/blob/v1.53.2/crates/meilisearch/src/option.rs#L534-L560",
        "sb9cb7736ecb6": "https://raw.githubusercontent.com/meilisearch/meilisearch/v1.53.2/Dockerfile"
      }
    },
    "typesense": {
      "name": "Typesense",
      "basis": "30.2",
      "sources": {
        "s9671c6e07c7f": "https://typesense.org/docs/30.2/api/server-configuration.html",
        "s2c4b6bcfaf53": "https://typesense.org/docs/30.2/api/api-keys.html",
        "sa9d1feeb6147": "https://typesense.org/docs/30.2/api/vector-search.html",
        "s4a43ef5aa4f9": "https://raw.githubusercontent.com/typesense/typesense/v30.2/src/http_server.cpp",
        "s29b60ad510db": "https://raw.githubusercontent.com/typesense/typesense/v30.2/src/core_api.cpp"
      }
    },
    "meili-docs": {
      "name": "Meilisearch documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "sb0775887509a": "https://www.meilisearch.com/docs/resources/self_hosting/security/master_api_keys",
        "s9ea7561d005d": "https://www.meilisearch.com/docs/capabilities/security/advanced/tenant_token_payload",
        "s26bf028aa235": "https://www.meilisearch.com/docs/resources/self_hosting/security/http2_ssl",
        "s5a14ae3a4b54": "https://www.meilisearch.com/docs/resources/self_hosting/configuration/reference",
        "s733eae6c1299": "https://www.meilisearch.com/docs/resources/self_hosting/data_backup/overview",
        "s034b9614262f": "https://www.meilisearch.com/docs/capabilities/indexing/how_to/edit_documents_with_functions"
      }
    },
    "meili-advisory": {
      "name": "Meilisearch SSRF advisory",
      "basis": "unknown",
      "sources": {
        "sb8b81d3f76ff": "https://www.meilisearch.com/blog/CVE-update-Jan-2026"
      }
    },
    "typesense-docs": {
      "name": "Typesense documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s6fb918104d58": "https://typesense.org/docs/guide/data-access-control.html",
        "s02ce5458d664": "https://typesense.org/docs/guide/backups.html"
      }
    },
    "caddy": {
      "name": "Caddy",
      "basis": "v2.11.4",
      "sources": {
        "sb0b62262df7b": "https://github.com/caddyserver/caddy/blob/v2.11.4/caddyconfig/httpcaddyfile/builtins.go#L58-L88",
        "sb4be8e0cfe75": "https://github.com/caddyserver/caddy/blob/v2.11.4/caddyconfig/httpcaddyfile/options.go#L347-L381",
        "sd11645c28457": "https://github.com/caddyserver/caddy/blob/v2.11.4/caddyconfig/httpcaddyfile/options.go#L459-L476",
        "s9702adeb8c11": "https://raw.githubusercontent.com/caddyserver/caddy/v2.11.4/modules/caddyhttp/reverseproxy/caddyfile.go"
      }
    },
    "curl": {
      "name": "curl minimum",
      "basis": "7.75.0",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    },
    "nc": {
      "name": "OpenBSD-compatible netcat",
      "basis": "unknown",
      "sources": {
        "s096a08149c92": "https://man.openbsd.org/nc"
      }
    },
    "git-grep": {
      "name": "Git grep manual",
      "basis": "2.55.0",
      "sources": {
        "se138ed3614b1": "https://git-scm.com/docs/git-grep"
      }
    },
    "git-rev-list": {
      "name": "Git rev-list manual",
      "basis": "2.56.0",
      "sources": {
        "sa551f03eb541": "https://git-scm.com/docs/git-rev-list"
      }
    },
    "git": {
      "name": "Git manual",
      "basis": "2.56.0",
      "sources": {
        "s1d8fe6ad85ac": "https://git-scm.com/docs/git"
      }
    }
  },
  "claims": {
    "meili-mode": {"text": "Development is keyless unless MEILI_MASTER_KEY is set; production requires a master key of at least 16 bytes.", "components": ["meili-docs"], "sources": ["meili-docs:sb0775887509a"], "status": "REASONED"},
    "meili-bind": {"text": "Binary defaults localhost:7700 unless implicit config.toml overrides it; environment and CLI override the file.", "components": ["meili"], "sources": ["meili:sbed426856353", "meili:sa5636634c0e5"], "status": "REASONED"},
    "meili-image": {"text": "Official image sets MEILI_HTTP_ADDR=0.0.0.0:7700; publish only host loopback or use an unpublished private proxy network.", "components": ["meili"], "sources": ["meili:sb9cb7736ecb6"], "status": "REASONED"},
    "meili-keys": {"text": "Four default keys and their permissions are version-dependent; inspect GET /keys and keep admin, read-only admin and master keys server-side.", "components": ["meili-docs"], "sources": ["meili-docs:sb0775887509a"], "status": "REASONED"},
    "meili-tenant": {"text": "For confidential search, restrict indexes or issue tenant JWTs with enforced rules; keep the signing key server-side and set exp no later than parent expiry.", "components": ["meili-docs"], "sources": ["meili-docs:s9ea7561d005d", "meili-docs:sb0775887509a"], "status": "REASONED"},
    "meili-tls": {"text": "Native HTTPS uses ssl-cert-path and ssl-key-path; the proxy pattern confines plaintext locally and verifies TLS across machines.", "components": ["meili-docs"], "sources": ["meili-docs:s26bf028aa235"], "status": "REASONED"},
    "typesense-bootstrap": {"text": "Bootstrap api-key is required and controls all endpoints/data; supply it through TYPESENSE_API_KEY or a protected file and use a revocable operational key routinely.", "components": ["typesense", "typesense-docs"], "sources": ["typesense:s9671c6e07c7f", "typesense-docs:s6fb918104d58"], "status": "REASONED"},
    "typesense-api": {"text": "API defaults 0.0.0.0:8108; set api-address=127.0.0.1 and api-port=8108 for a same-host proxy.", "components": ["typesense"], "sources": ["typesense:s9671c6e07c7f"], "status": "REASONED"},
    "typesense-peer": {"text": "Separate peering defaults to 8107; select a private address and admit only cluster members.", "components": ["typesense"], "sources": ["typesense:s9671c6e07c7f"], "status": "REASONED"},
    "typesense-scope": {"text": "Parent search key uses documents:search and named/regex collections; derive browser keys with filter_by and field restrictions, keeping the parent server-side.", "components": ["typesense", "typesense-docs"], "sources": ["typesense:s2c4b6bcfaf53", "typesense-docs:s6fb918104d58"], "status": "REASONED"},
    "typesense-expiry": {"text": "Set expires_at on browser keys no later than parent expiry; collection scope alone does not isolate JOIN data.", "components": ["typesense-docs"], "sources": ["typesense-docs:s6fb918104d58"], "status": "REASONED"},
    "typesense-tls": {"text": "Self-managed native TLS uses ssl-certificate and ssl-certificate-key; cloud terminates TLS; restrict API and peering access independently.", "components": ["typesense"], "sources": ["typesense:s9671c6e07c7f"], "status": "REASONED"},
    "admin-surface": {"text": "Keep management UIs private or behind MFA; engine bearer keys are not a second factor and Meilisearch production disables the development preview.", "components": ["meili-docs", "typesense-docs"], "sources": ["meili-docs:s5a14ae3a4b54", "typesense-docs:s6fb918104d58"], "status": "REASONED"},
    "backup": {"text": "Protect and encrypt dumps, snapshots, volumes and backups; Typesense backs up snapshot output rather than the live directory and restores privately with auth.", "components": ["meili-docs", "typesense-docs"], "sources": ["meili-docs:s733eae6c1299", "typesense-docs:s02ce5458d664"], "status": "REASONED"},
    "meili-egress": {"text": "Upgrade Meilisearch v1.8 through v1.34.0 for SSRF fixed in v1.34.1; avoid allowed-IP-networks=any and restrict remote/webhook administration and egress.", "components": ["meili-docs", "meili-advisory"], "sources": ["meili-advisory:sb8b81d3f76ff", "meili-docs:s5a14ae3a4b54"], "status": "REASONED"},
    "typesense-egress": {"text": "Remote embeddings send provider credentials outbound; restrict destinations and protect those secrets.", "components": ["typesense"], "sources": ["typesense:sa9d1feeb6147"], "status": "REASONED"},
    "meili-functions": {"text": "Leave experimental document-editing functions disabled unless needed; Rhai transformations belong to trusted workloads, not arbitrary OS execution.", "components": ["meili-docs"], "sources": ["meili-docs:s034b9614262f"], "status": "REASONED"},
    "verify-meili-auth": {"text": "Loopback keyless search returned 200; protected search returned anonymous 401 and keyed 200 with the fixture.", "components": ["meili-docs"], "sources": ["meili-docs:sb0775887509a"], "status": "DEMONSTRATED", "evidence": "keyless Meilisearch returned the fixture to an anonymous search with `200`, so the authentication row printed `FAIL: unexpected HTTP status`: the exposed state.", "verify": [1]},
    "verify-meili-write": {"text": "Search key was refused index creation with 403; Default Admin received 202 and the task succeeded.", "components": ["meili-docs"], "sources": ["meili-docs:sb0775887509a"], "status": "DEMONSTRATED", "evidence": "the write row got `403` `invalid_api_key` for the search key and `202` for the Default Admin API Key, whose task then reported `succeeded`. Started with", "verify": [1]},
    "verify-meili-production": {"text": "Production startup without a master key was refused in the recorded run.", "components": ["meili-docs"], "sources": ["meili-docs:sb0775887509a"], "status": "DEMONSTRATED", "evidence": "Meilisearch refused to start: \"You must provide a master key to secure your instance in a production environment\"."},
    "verify-typesense-auth": {"text": "Loopback Typesense refused anonymous search with 401 and returned the fixture with a collection-scoped key and 200.", "components": ["typesense", "typesense-docs"], "sources": ["typesense-docs:s6fb918104d58", "typesense:s4a43ef5aa4f9"], "status": "DEMONSTRATED", "evidence": "answered the authentication row with `401` anonymously and `200` on a collection-scoped search key", "verify": [1]},
    "verify-typesense-write": {"text": "Search-key collection creation returned 401; bootstrap creation returned 201.", "components": ["typesense"], "sources": ["typesense:s4a43ef5aa4f9", "typesense:s29b60ad510db"], "status": "DEMONSTRATED", "evidence": "the write row with `401` for that key and `201` for the bootstrap key.", "verify": [1]},
    "verify-rotation": {"text": "Disclosed Typesense operational key succeeded before deletion, failed after deletion, and its replacement succeeded.", "components": ["typesense"], "sources": ["typesense:s2c4b6bcfaf53"], "status": "DEMONSTRATED", "evidence": "A disclosed operational key got `200` before rotation, `401` after it was deleted, and its replacement `200`. A Meilisearch tenant token", "verify": [1]},
    "verify-tenant": {"text": "Tenant token and scoped-key filters resisted other-tenant overrides while parent controls returned both fixtures.", "components": ["meili-docs", "typesense-docs"], "sources": ["meili-docs:s9ea7561d005d", "typesense-docs:s6fb918104d58"], "status": "DEMONSTRATED", "evidence": "A Meilisearch tenant token filtered to one tenant returned only that tenant's fixture, and a request adding a filter for the other tenant returned nothing, while the parent key returned both; a Typesense scoped key embedding `filter_by` behaved the same way under an overriding `filter_by`. For JOINs,", "verify": [1]},
    "verify-join": {"text": "Collection-scoped key leaked a joined billing field; an embedded exclude_fields restriction removed it.", "components": ["typesense-docs"], "sources": ["typesense-docs:s6fb918104d58"], "status": "DEMONSTRATED", "evidence": "For JOINs, a Typesense key scoped to collection `products` was refused a direct search of `companies` with `401`, but a `products` search with `include_fields=$companies(billing)` returned the joined company's billing field: collection scoping alone did not isolate joined data. A scoped key embedding `exclude_fields=$companies(billing)` returned the same query without it.", "verify": [1]},
    "verify-proxy": {"text": "Recorded same-host Caddy TLS proxy preserved anonymous/keyed auth distinctions for both engines; no external isolation is established.", "components": ["meili-docs", "typesense-docs", "caddy"], "sources": ["meili-docs:sb0775887509a", "typesense-docs:s6fb918104d58", "caddy:sb0b62262df7b", "caddy:sb4be8e0cfe75", "caddy:sd11645c28457", "caddy:s9702adeb8c11"], "status": "DEMONSTRATED", "evidence": "Behind the same proxy, keyless Meilisearch made the block print `FAIL: unexpected HTTP status` on an anonymous `200`, the exposed state, and Typesense with its plaintext backend on `127.0.0.1:8108` gave `401` anonymously then `200` on a collection-scoped search key.", "verify": [1]},
    "verify-request": {"text": "Paired requests require Bash, curl 7.75.0+, verified HTTPS and identical origin/method/path/body; inspect engine JSON, not status alone.", "components": ["curl", "meili-docs", "typesense-docs"], "sources": ["curl:s2b2686afaf41", "meili-docs:sb0775887509a", "typesense-docs:s6fb918104d58"], "status": "REASONED"},
    "verify-external": {"text": "Inventory actual listeners, publications and IPv4/IPv6 rules; external TCP success fails, while refusal/timeout needs live private controls and policy evidence.", "components": ["meili", "typesense", "nc"], "sources": ["meili:sb9cb7736ecb6", "typesense:s9671c6e07c7f", "nc:s096a08149c92"], "status": "REASONED", "verify": [2]},
    "verify-local-tcp": {"text": "Recorded netcat loopback reachable/refused shapes returned FAIL/exit 1 and INCONCLUSIVE/exit 2 respectively; external reachability remains unobserved.", "components": ["nc"], "sources": ["nc:s096a08149c92"], "status": "DEMONSTRATED", "evidence": "The block against 127.0.0.1, where the engines listened, printed `FAIL: TCP 7700 is reachable` (exit `1`), the reachable shape; against 127.0.0.2, where nothing listens, each port's `Connection refused` printed `INCONCLUSIVE` and the block ended with exit `2`, the refused shape."},
    "verify-bundle": {"text": "Repository credential scanner searches literal output and local commit-tree content; regression fixtures ran, while real-client-build controls remain unobserved.", "components": ["meili-docs", "typesense-docs", "git-grep", "git-rev-list", "git"], "sources": ["meili-docs:sb0775887509a", "typesense-docs:s6fb918104d58", "git-grep:se138ed3614b1", "git-rev-list:sa551f03eb541", "git:s1d8fe6ad85ac"], "status": "REASONED", "verify": [3]}
  }
}
````
<!-- version-basis:end -->
