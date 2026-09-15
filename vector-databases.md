# Vector databases: Qdrant, Weaviate, Milvus, Chroma, pgvector

A RAG store holds every document the application was given, often including private data, and it answers similarity queries that reconstruct that text. Several of these servers ship with no authentication enabled and none of them serves TLS out of the box, so an exposed default install is a searchable copy of your corpus. Keep the store on a private interface, turn on the native key or account control where one exists, and put TLS in front or on the server before any client crosses a network.

## 1. Bind privately

Each server listens on plain TCP; publish only a reverse proxy ([nginx.md](nginx.md), [caddy.md](caddy.md)), a tunnel ([cloudflare.md](cloudflare.md)), or a tailnet ([tailscale.md](tailscale.md)). In Docker, map to loopback (`-p 127.0.0.1:6333:6333`), not `-p 6333:6333`, which binds every interface ([docker.md](docker.md)). Default ports, from the vendor pages in Sources:

| Server | Default ports |
|---|---|
| Qdrant | 6333 (REST), 6334 (gRPC), 6335 (internal cluster gRPC, distributed mode only) |
| Weaviate | 8080 (HTTP), 50051 (gRPC) |
| Milvus | 19530 (gRPC), 9091 (WebUI) |
| Chroma | 8000 |
| pgvector | 5432 (it is PostgreSQL) |

## 2. Qdrant: API key and TLS

Per the Qdrant security page, "all self-deployed Qdrant instances are not secure" by default and connections are unencrypted. Set an API key in the config file or through the environment, and add a read-only key for query-only clients:

```yaml
service:
  api_key: REPLACE_WITH_LONG_RANDOM_VALUE
  read_only_api_key: REPLACE_WITH_ANOTHER_LONG_RANDOM_VALUE
  enable_tls: true

tls:
  cert: ./tls/cert.pem
  key: ./tls/key.pem
```

Environment equivalents: `QDRANT__SERVICE__API_KEY` and `QDRANT__SERVICE__READ_ONLY_API_KEY`. Clients send the key in the `api-key` header (or `Authorization: Bearer`); the two are interchangeable for the client REST and gRPC API. Qdrant's own docs say that enabling the key without TLS is insecure; terminate TLS either in Qdrant as above or at a proxy in front.

An API key protects the client API. It does not protect the internal cluster port, 6335. The security page states, exactly: "Internal communication channels are *never* protected by an API key nor bearer tokens. Internal gRPC uses port 6335 by default if running in distributed mode. You must ensure that this port is not publicly reachable and can only be used for node communication." Through v1.17.x this is not a gap a key can close. Qdrant v1.18.0 added `service.enforce_internal_auth`: with it set, the receiving peer verifies the forwarded `api_key` on internal p2p requests, so a key can gate 6335 on v1.18.0 and later. It is off by default, and the vendor recommends leaving it off through a rolling upgrade until every node is on the new version, so do not rely on it in place of the network restriction below. `read_only_api_key` does not cover 6335 either, and confirming that 6333 returns 401 without a key tells you nothing about 6335: in distributed mode 6335 answers a peer with no API key or bearer token (peer TLS, when enabled, authenticates the channel by certificate; a key applies to the internal channel only where `enforce_internal_auth` is set, on v1.18.0 and later), so a reader who sets a key, sees 6333 return 401, and concludes the deployment is authenticated is wrong about 6335.

Restrict 6335 to your cluster peers at the network layer, with a host firewall, a cloud security group, or by simply not publishing the container port to any address a non-peer can reach. Allow inbound 6335 only from your other peers' addresses and deny every other source, including other machines on the same private network. A node not running in cluster mode does not open 6335 at all; note that a single initial node started WITH cluster mode enabled does open the internal listener, so "single host" is not by itself a guarantee that 6335 is absent, which is why V1 and the 6335 probe still apply. In a cluster you cannot bind it to `127.0.0.1`, because peers on other hosts must reach it, so bind it to the private cluster interface and firewall it to peers. TLS on the peer channel does not remove this requirement; turn it on as well, but it authenticates and encrypts the channel rather than making an exposed port safe to reach:

```yaml
cluster:
  p2p:
    enable_tls: true
```

`cluster.p2p.enable_tls` is separate from `service.enable_tls`: the first secures peer-to-peer traffic, the second the client API. Enabling `cluster.p2p.enable_tls` also requires a `ca_cert` in the `tls:` block, the CA that validates peer certificates; the security page marks `ca_cert: ./tls/cacert.pem` as required for peer TLS. Provision that CA and set the field before you enable peer TLS. Qdrant carries a compiled default path (`./tls/cacert.pem`), so a missing entry does not always fail at startup, but relying on an unprovisioned default is fragile and the vendor marks it required. Set both TLS settings in distributed mode, apply the configuration on every peer, and restart the peers one at a time. To rotate the client API key without downtime, set the new key as `service.alt_api_key` on each peer and restart one at a time; `alt_api_key` (available as of Qdrant v1.17.0) is an additional accepted client key and, like `api_key`, gates the client API; it reaches the internal channel only where `enforce_internal_auth` is set, on v1.18.0 and later. The peer-channel and rotation settings can be version-dependent, so confirm them against the security page for the Qdrant version you run.

## 3. Weaviate: disable anonymous access, then authorize

`AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED` defaults to `true`, which the Weaviate docs describe as strongly discouraged outside development. The secured Docker example:

```yaml
environment:
  AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'false'
  AUTHENTICATION_APIKEY_ENABLED: 'true'
  AUTHENTICATION_APIKEY_ALLOWED_KEYS: 'REPLACE_WITH_ADMIN_KEY,REPLACE_WITH_APP_KEY'
  AUTHENTICATION_APIKEY_USERS: 'admin-user,app-user'
  AUTHORIZATION_RBAC_ENABLED: 'true'
  AUTHORIZATION_RBAC_ROOT_USERS: 'admin-user'
```

Keys map to users by position, so the first key belongs to `admin-user` and the second to `app-user`. Only `admin-user` is a root user with full access; give `app-user` a custom role limited to its collections, created with the admin key through the RBAC API as the [RBAC configuration page](https://docs.weaviate.io/deploy/configuration/configuring-rbac) describes, and keep the admin key off the application host. Authentication alone lets any key holder do anything; add authorization with either RBAC (above, generally available from v1.29 per the authorization page) or the simpler admin list (`AUTHORIZATION_ADMINLIST_ENABLED`, `AUTHORIZATION_ADMINLIST_USERS`, `AUTHORIZATION_ADMINLIST_READONLY_USERS`; it cannot be combined with RBAC). For human logins, `AUTHENTICATION_OIDC_ENABLED` with `AUTHENTICATION_OIDC_ISSUER` and `AUTHENTICATION_OIDC_CLIENT_ID` delegates to an identity provider, where MFA is enforced ([mfa.md](mfa.md)). The documented deployment starts Weaviate with `--scheme http` and points to a reverse proxy for domain access, forwarding both 8080 and 50051; give the proxy the certificate ([free-certificates.md](free-certificates.md)) and do not expose the plain ports.

## 4. Milvus: enable authentication, change root, add TLS

Authentication is enabled by setting `common.security.authorizationEnabled: true` in `milvus.yaml` (or through the Helm `extraConfigFiles` / Operator `spec.config` equivalents). Once on, the built-in `root` user exists with the password `Milvus`; change it before exposure, since a documented default is a public credential ([authentication.md](authentication.md)):

```python
client = MilvusClient(uri="https://milvus.example.com:19530", token="root:Milvus")
client.update_password(user_name="root", old_password="Milvus", new_password="REPLACE_WITH_LONG_RANDOM_VALUE")
```

Create a per-application user rather than handing `root` to the app. TLS is configured in the same file, with certificates mounted into the container (Docker Compose: a volume such as `./tls:/milvus/tls`):

```yaml
tls:
  serverPemPath: /milvus/tls/server.pem
  serverKeyPath: /milvus/tls/server.key
  caPemPath: /milvus/tls/ca.pem
common:
  security:
    tlsMode: 1      # 1 = server certificate only; 2 = mutual TLS, clients present a certificate too
```

Clients then connect with `secure=True` and the server certificate path. TLS and authentication are independent in Milvus; enable both.

## 5. Chroma: no native authentication since 1.0

Chroma's migration notes for v1.0.0 state that "Chroma no longer provides built-in authentication implementations". A self-hosted `chroma run --path /db_path` server (port 8000) therefore accepts every request, and the older `CHROMA_SERVER_AUTHN_PROVIDER` / `CHROMA_SERVER_AUTHN_CREDENTIALS` variables from the 2024 auth overhaul no longer do anything; do not paste them from old tutorials and assume protection. Keep Chroma on loopback and expose it only through an authenticated TLS proxy (bearer-token or basic-auth block per [nginx.md](nginx.md) / [caddy.md](caddy.md)), a Cloudflare Tunnel with Access ([cloudflare.md](cloudflare.md)), or a tailnet ([tailscale.md](tailscale.md)).

## 6. pgvector: it is PostgreSQL

pgvector is an extension (`CREATE EXTENSION vector;`, PostgreSQL 13 and later), so [postgresql.md](postgresql.md) applies unchanged: `ssl = on`, `hostssl` lines with `scram-sha-256`, a least-privilege role per application, and `sslmode=verify-full` in every connection string. When several tenants share one embeddings table, add row-level security keyed on the tenant column so a query can only match rows the connected role may see.

## 7. Hosted services and MFA

Pinecone, Qdrant Cloud, Weaviate Cloud, and Zilliz authenticate with API keys: those are secrets under [secrets.md](secrets.md), one per environment, never committed, rotated on leak. The vendor terminates TLS, so the client-side check is that the SDK is pointed at the `https://` endpoint the console gives you. None of the self-hosted servers has a human login with a second factor; MFA exists only on the vendor console for the hosted tiers, at the identity provider when Weaviate uses OIDC, or on the fronting layer (Access policy, Authelia-style portal) for everything else ([mfa.md](mfa.md)).

## Verify

Inventory every listener without grep, because filtering for the ports you expect hides the listener you did not (a grep for `6333` also matches a port `63330` or a PID). Read the whole table:

```bash
sudo ss -tulnp                       # read every row; any 6333/6334/6335 on a wildcard
                                     # (0.0.0.0, *, [::]) or public address fails bind-privately.
                                     # In a container, also run it in the container netns and check
                                     # published ports; the host table alone does not show -p 6335:6335.
```

Then probe each Qdrant backend port from a host **outside** the peer allowlist, against the node's real address, running the block three times with `6333`, `6334`, then `6335` on the `set --` line. **These probes are reasoned, not demonstrated** (no distributed Qdrant cluster in the authoring environment; backlog row 1.46 tracks demonstrating the exposed and fixed states against a live cluster). Bracket an IPv6 literal, for example `'[2001:db8::1]'`; `-g` keeps curl from globbing the brackets. The block prints the `exitcode` and `errormsg` write-out variables, which need curl 7.75.0 or newer:

```bash
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HOST_ADDRESS' 'REPLACE_WITH_PORT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  if [ -z "$1" ] || [ -z "$2" ]; then echo "substitute the values on the set -- line above; not probing"; exit; fi
  case "$1:$2" in
    *REPLACE_WITH_*) echo "substitute the values on the set -- line above; not probing"; exit ;;
  esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:$2/"
)
```

Read the exit code and the elapsed time together (curl's exit strings vary by version, so key on the code, not the message). A non-peer probe of a restricted 6335 should FAIL TO CONNECT: curl reports `exit=7` (the TCP connection did not complete, whether refused or reset), or `exit=28` at about 5 seconds (the connect timeout, consistent with a firewall that drops the packet). Neither proves the port is closed on its own, so corroborate with the inventory and the filtering point's own deny evidence. Two other exits are your own input error, not a result: `exit=6` (could not resolve host) means you mistyped the address, and `exit=3` (a malformed URL) means the target string is wrong; fix the value and re-run. Any sign the connection COMPLETED is a reachability fail for a backend port from a non-peer: a non-zero `http=` status, `exit=52` (empty reply) or `exit=56` (receive failure), or `exit=28` at about 20 seconds (the max-time, the connection opened and then stalled). Do not judge on `http=` alone: curl prints `http=000` both when nothing connected and when a connection completed with no HTTP response, so pair it with the exit code, since a `52` or `56` alongside `000` is still a completed connection and a fail. A key check or a TLS rejection after the connection opens does not un-expose the port. Plaintext `http://` is deliberate: the question is only whether the TCP connection completed, and a plaintext probe that reaches a TLS-only peer port still completes the TCP connection and surfaces as one of the reachable signals above.

For 6335 specifically, in distributed mode, require two results. From a non-peer: a failure to connect, `exit=7` or a 5-second `exit=28`, corroborated by the inventory and firewall evidence (a `exit=6` or `exit=3` is a mistyped target, not a result). From an allowed peer: POSITIVE evidence that the connection completed, a non-zero `http=` status (not `http=000`, which curl prints when nothing was received), or a post-connect exit (`52`, `56`, or the 20-second `exit=28`), not merely the absence of a refusal, because a mistyped target also avoids `exit=7`. The pair separates "restricted to peers, cluster works" from both "exposed to everyone" and "blocked for everyone". 6335 absent from the inventory is consistent with single-node but does not prove it can never appear, so probe it anyway.

Keep the existing client-API key check, hardened, against the frontend hostname over TLS (never a backend IP, never `curl -k`, which a gate rejects). It confirms the key is enforced, but it **cannot** distinguish a keyed single-node deployment from a keyed distributed one with 6335 exposed, because both answer 401 then 200; only the port probes above catch an exposed 6335:

```bash
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_FRONTEND_HOSTNAME' 'REPLACE_WITH_LONG_RANDOM_VALUE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  if [ -z "$1" ] || [ -z "$2" ]; then echo "substitute the values on the set -- line above; not probing"; exit; fi
  case "$1:$2" in
    *REPLACE_WITH_*) echo "substitute the values on the set -- line above; not probing"; exit ;;
  esac
  echo "without key (expect http=401 or 403):"
  curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
    -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "https://$1/collections"
  echo "with key (expect http=200):"
  curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
    -H "api-key: $2" \
    -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "https://$1/collections"
)
```

**Exposed:** without-key returns `http=200` (no key, or a proxy that does not enforce it), or a backend port is reachable from a non-peer. **Fixed:** without-key returns `401`/`403` and with-key returns `200`, and 6335 is refused from a non-peer while a peer connects.

For Weaviate and Chroma, the fronted client checks still apply:

```bash
curl -q -si https://weaviate.example.com/v1/schema | head -1   # 401 without a key
curl -q -si https://chroma.example.com/ | head -1              # 401 from the proxy, never a Chroma response
```

For Milvus, a `MilvusClient(uri=...)` call with no `token` must fail once `authorizationEnabled` is on, and the same call with the application user's credentials must succeed.

None of the checks above tests isolation between tenants. Where one embeddings table serves several users or tenants under the row-level security above, prove the boundary as well as the ports: connect as the role for tenant B, run the similarity search tenant A would run, and confirm only tenant B's rows come back. Run the same query as a role that bypasses that policy (a superuser, or the table owner) and confirm it returns both tenants' rows, so the difference is the policy filtering and not an empty table. A query that returns another tenant's vectors is a live cross-user leak, whatever the network posture.

## Sources (checked September 2026)

- Qdrant security (API key, read-only key, `api-key` header, TLS keys, ports, default insecurity): https://qdrant.tech/documentation/security/
- Weaviate authentication (anonymous access, API key, OIDC variables): https://docs.weaviate.io/deploy/configuration/authentication
- Weaviate authorization (admin list, RBAC availability): https://docs.weaviate.io/deploy/configuration/authorization and RBAC configuration (`AUTHORIZATION_RBAC_ENABLED`, `AUTHORIZATION_RBAC_ROOT_USERS`): https://docs.weaviate.io/deploy/configuration/configuring-rbac
- Weaviate environment variables (`AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED` default, `GRPC_PORT` default): https://docs.weaviate.io/deploy/configuration/env-vars
- Weaviate Docker installation (ports 8080/50051, `--scheme http`, reverse proxy layout): https://docs.weaviate.io/deploy/installation-guides/docker-installation
- Milvus authentication (`common.security.authorizationEnabled`, default `root`/`Milvus`, `update_password`): https://milvus.io/docs/authenticate.md
- Milvus TLS (`tls.*` paths, `common.security.tlsMode`, RESTful port note): https://milvus.io/docs/tls.md ; standalone install (ports 19530 and 9091): https://milvus.io/docs/install_standalone-docker.md
- Chroma migration notes (v1.0.0 removal of built-in authentication; 2024 auth overhaul variables): https://docs.trychroma.com/docs/overview/migration ; client-server mode (`chroma run --path`, port 8000): https://docs.trychroma.com/docs/run-chroma/client-server
- pgvector (`CREATE EXTENSION vector`, PostgreSQL 13 and later): https://github.com/pgvector/pgvector
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0): https://curl.se/docs/manpage.html
