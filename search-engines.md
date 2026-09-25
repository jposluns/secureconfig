# Search engines for RAG: Meilisearch and Typesense

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

Verification status: the checks below were demonstrated on loopback against the Meilisearch v1.53.2 release binary (its SHA-256 matched the digest GitHub publishes for the asset) and the Typesense 30.2 server (its MD5 matched the one in the release tarball), each with native TLS on 127.0.0.1, or behind a Caddy TLS proxy for the proxy checks, with certificates from a private test CA that curl trusted through `CURL_CA_BUNDLE`, and every address set before start. The blocks ran as printed with only their `set --` values substituted, and keys were fed to the prompts on stdin. What those runs do not show is marked **REASONED** where it occurs, with its reason; backlog row 1.117 tracks it. Use Bash and curl 7.75.0 or later; never add `-k`. Substitute your actual HTTPS origin inside the single quotes, without a trailing slash. Run each row of the matrix below through this paired-request block, changing the method, path, JSON body, header prefix, and expected statuses on its `set --` line, and enter credentials at the prompts rather than in the command. Both requests use exactly the same origin, method, path, and body; inspect the engine JSON as well as the status, since a proxy login page, redirect, missing resource, or transport failure does not establish engine authorization.

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a
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

| Test | Method and path | JSON body | Negative credential/status | Positive credential/status |
|---|---|---|---|---|
| Meilisearch authentication | `POST /indexes/movies/search` | `{"q":"ninja"}` | Empty / `401` | Valid search key / `200`, containing the known fixture |
| Typesense authentication | `GET /collections/products/documents/search?q=stark&query_by=company_name` | empty string | Empty / `401` | Valid search key / `200`, containing the known fixture |
| Meilisearch write restriction | `POST /indexes` | `{"uid":"acl_probe"}` | Search-only key / `403` | Authorized admin key / `202` |
| Typesense write restriction | `POST /collections` | `{"name":"acl_probe","fields":[{"name":"title","type":"string"}]}` | Search-only key / `401` | Authorized admin key / `201` |

Use `Authorization: Bearer ` for Meilisearch and `X-TYPESENSE-API-KEY: ` for Typesense. Prepare the search fixtures first, and for the creation tests confirm `acl_probe` does not already exist, using a disposable resource and removing it afterward. A Meilisearch `202` only acknowledges a queued task, so confirm task success before crediting the positive control. In an isolated exposed-state test, keyless Meilisearch must return the fixture anonymously and the protected instance must reject that request; Typesense's exposed-state discriminator is a known disclosed bootstrap or operational key (it has no keyless mode), which after rotation must fail while its replacement succeeds against the same request. Do not invent a universal default password. Test tenant restrictions with known allowed and forbidden documents: the restricted credential must find the allowed fixture and omit the forbidden one, while an authorized control finds the forbidden fixture on the same query and origin; attempt to override filters and field selection, and test referenced collections where JOINs are used, since an empty result alone proves nothing.

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

**The same-host TLS proxy demonstrated; container mappings, IPv6, firewalls and a wildcard bind REASONED
(one host with no container runtime, no second network, and no root or `sudo` to read the rulesets, and
the host forbids binding every interface):** proxy authentication does not prove the engine or
peering ports are private. On the engine host inspect `ss -ltnp`, container port mappings, and the effective IPv4 and IPv6 firewall rules, and confirm the engine answers from its intended private client while running. From an external disallowed source, test every public address and actual published port; the block below covers the default ports with OpenBSD-compatible netcat and numeric addresses:

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

Under the private-backend pattern, any successful external TCP connection is a finding, even if HTTP authentication would reject the caller; a timeout is inconclusive, and a refusal shows only no connection from that source at that moment, so corroborate it with the live private positive control, the listener bindings, and the effective firewall policy. If native HTTPS is intentionally public, run the paired authorization tests against that engine endpoint too, using its certificate-valid hostname and actual port (preserve the hostname with curl's `--resolve` when testing an IP, keep the substituted address guarded, and retain certificate verification); engine API TLS does not establish protection of Typesense's separate peering listener.

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

**REASONED (no client bundle in this review):** grep the client bundle and repository history for the
admin/master/bootstrap key; it should never appear outside the server-side secret store.

## Common mistakes

- Shipping a Meilisearch instance without `MEILI_MASTER_KEY` and `--env production` because dev mode "worked fine" in testing.
- Putting the Typesense bootstrap key or Meilisearch admin key straight into front-end JavaScript instead of minting a scoped search key.
- A scoped key with no `filter_by` or `collections` restriction, which searches everything the admin key can see.

## Sources (checked September 2026)

Version scope: Typesense 30.2; Meilisearch current unversioned documentation checked 2026-09-18, with v1.53.2 as the release reference. The first release containing all four default keys and their exact permissions remains to be confirmed against the deployed release, so inspect `GET /keys`. The Verify commands require Bash, curl 7.75.0 or later, and OpenBSD-compatible netcat.

- Meilisearch master API keys (MEILI_MASTER_KEY, the four default API keys): https://www.meilisearch.com/docs/resources/self_hosting/security/master_api_keys
- Typesense data access control (bootstrap api-key, /keys, actions, collections, filter_by, include_fields/exclude_fields, expires_at): https://typesense.org/docs/guide/data-access-control.html
- Typesense 30.2 server configuration (api-key required, api-address default 0.0.0.0, api-port 8108, peering-port 8107, ssl-certificate): https://typesense.org/docs/30.2/api/server-configuration.html
- Typesense `api-address` default `0.0.0.0`, `api-port` default 8108 and `peering-port` default 8107 (pinned tag v30.2): https://github.com/typesense/typesense/blob/v30.2/src/typesense_server_utils.cpp#L81-L85
- Typesense 30.2 API keys (parent search-only key, scoped-key derivation, description): https://typesense.org/docs/30.2/api/api-keys.html
- Typesense 30.2 collections (collection creation and schema fields): https://typesense.org/docs/30.2/api/collections.html
- Typesense v30.2 authorization failure (401): https://raw.githubusercontent.com/typesense/typesense/v30.2/src/http_server.cpp
- Typesense v30.2 collection creation success (201): https://raw.githubusercontent.com/typesense/typesense/v30.2/src/core_api.cpp
- Typesense backups (snapshot API, not the live data directory): https://typesense.org/docs/guide/backups.html
- Typesense 30.2 remote embeddings (outbound requests with provider credentials): https://typesense.org/docs/30.2/api/vector-search.html
- Meilisearch configuration reference (MEILI_HTTP_ADDR default localhost:7700; MEILI_EXPERIMENTAL_ALLOWED_IP_NETWORKS): https://www.meilisearch.com/docs/resources/self_hosting/configuration/reference
- Meilisearch `DEFAULT_HTTP_ADDR` "localhost:7700" and the `--http-addr` / `MEILI_HTTP_ADDR` option that defaults to it, and the implicit `./config.toml` read whose values yield to the environment and the command line (pinned tag v1.53.2): https://github.com/meilisearch/meilisearch/blob/v1.53.2/crates/meilisearch/src/option.rs#L95-L97, https://github.com/meilisearch/meilisearch/blob/v1.53.2/crates/meilisearch/src/option.rs#L221-L223 and https://github.com/meilisearch/meilisearch/blob/v1.53.2/crates/meilisearch/src/option.rs#L534-L560
- Meilisearch v1.53.2 Dockerfile (image sets MEILI_HTTP_ADDR=0.0.0.0:7700): https://raw.githubusercontent.com/meilisearch/meilisearch/v1.53.2/Dockerfile
- Meilisearch native TLS (--ssl-cert-path, --ssl-key-path): https://www.meilisearch.com/docs/resources/self_hosting/security/http2_ssl
- Meilisearch tenant-token payload (exp is optional): https://www.meilisearch.com/docs/capabilities/security/advanced/tenant_token_payload
- Meilisearch backups and dumps (documents across every index): https://www.meilisearch.com/docs/resources/self_hosting/data_backup/overview
- Meilisearch SSRF advisory (authenticated blind SSRF fixed in v1.34.1): https://www.meilisearch.com/blog/CVE-update-Jan-2026
- Meilisearch document-editing functions (Rhai; disabled unless enabled): https://www.meilisearch.com/docs/capabilities/indexing/how_to/edit_documents_with_functions
- curl options (write-out variables require 7.75.0+): https://curl.se/docs/manpage.html
- OpenBSD netcat reference: https://man.openbsd.org/nc
