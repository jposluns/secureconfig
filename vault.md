# HashiCorp Vault

Vault's own defaults are careful: the listener binds loopback, TLS is assumed (`tls_disable` is
`false`), and the web UI is off. The exposures are the deployment decisions you make on top of that,
and the corpus points you here from [machine-auth.md](machine-auth.md)
without saying how to stand one up safely. Five decisions decide it: not running dev mode, keeping TLS
on the listener you expose, choosing and guarding the seal, enabling an audit device, and retiring the
initial root token. OpenBao is the Linux Foundation open-source fork after Vault's move to the BUSL
licence; the controls below are written for Vault, and OpenBao shares the model but differs in some
commands, so check its own docs if you run it.

At the time of writing, the defaults and configuration below follow the current
[Vault configuration reference](https://developer.hashicorp.com/vault/docs/configuration) and
[TCP listener reference](https://developer.hashicorp.com/vault/docs/configuration/listener/tcp).
The application ACL, AppRole, response-wrapping, and authenticated-monitoring controls below are
available in Vault Community. Edition and version qualifications appear where they matter.

## 1. Never run dev mode in production

`vault server -dev` runs entirely in memory, initializes and unseals itself with a single key, serves
plain HTTP, and prints a root token to the console; the `-dev-tls` variant adds a throwaway
certificate but is still a development server: by default it binds loopback rather than the world,
stores nothing durably, and writes its printed root token into your token helper unless
`-dev-no-store-token` is set. It does not provide the production protections below.
Run a real server from a config file under your service manager
(`vault server -config=/etc/vault.d/vault.hcl`), and audit the systemd unit and its environment so no
`-dev` flag or dev-token override slips into production.
See [dev mode](https://developer.hashicorp.com/vault/docs/concepts/dev-server) and
[server flags](https://developer.hashicorp.com/vault/docs/commands/server).

## 2. Bind and front the listeners deliberately

The API listener answers on `8200` (and serves the UI at `/ui` on that same listener when `ui = true`),
and cluster peers forward requests and run Raft over `8201`. Bind the API to the private address that
clients actually use rather than a wildcard, keep `8201` reachable only by the other Vault nodes, and
put a default-deny firewall around both. `api_addr` and `cluster_addr` only advertise where peers and
redirects should point; they do not restrict what the listener binds, so set the `address` explicitly.
Expose the API to anything wider than a trusted network only behind the corpus's fronting controls
([fronting-auth.md](fronting-auth.md), [nginx.md](nginx.md), [caddy.md](caddy.md)), and enforce
Vault's Login MFA on the
human auth methods, not only at a UI proxy, since the token method cannot use it ([mfa.md](mfa.md));
the cluster port must keep Vault's own end-to-end TLS regardless of any proxy.
Other listeners exist only if you configure them (a KMIP listener on Enterprise, a Vault Agent or Proxy
listener), and an external storage backend is an outbound connection to a separate service with its own
listeners, so add each to your own network-surface inventory.
See [HA communication](https://developer.hashicorp.com/vault/docs/concepts/ha) and
[Login MFA](https://developer.hashicorp.com/vault/docs/auth/login-mfa).

Monitoring endpoints expose operational information. Keep anonymous metrics and profiling access
disabled on every API listener. The listener in section 3 explicitly sets
`unauthenticated_metrics_access = false` and `unauthenticated_pprof_access = false`;
both default to false in the current reference at the time of writing. Enabling monitoring is not a
reason to change them.
See [listener telemetry and profiling parameters](https://developer.hashicorp.com/vault/docs/configuration/listener/tcp#telemetry-parameters).

Give the metrics collector a separate identity with this policy:

```hcl
path "sys/metrics" {
  capabilities = ["read"]
}
```

The collector requests `GET /v1/sys/metrics`; its token should have no application-secret access.
Keep monitoring traffic on the permitted network. The metrics and profiling APIs must be called
from the root namespace, including on Enterprise deployments that use namespaces. The metrics
policy does not grant profiling access.
See the [metrics API](https://developer.hashicorp.com/vault/api-docs/system/metrics),
[profiling API](https://developer.hashicorp.com/vault/api-docs/system/pprof), and
[policy capabilities](https://developer.hashicorp.com/vault/docs/concepts/policies#capabilities).

## 3. Keep TLS on the listener

Vault assumes TLS, so `tls_disable = true` is an explicit choice to put every token and secret on the
wire in plaintext; never set it on a listener anything reaches. Give the listener a real certificate
and key with `tls_cert_file` and `tls_key_file`, keep the key `0400` and owned by the vault user, and
set `tls_min_version = "tls12"` or higher. Certificates come from [free-certificates.md](free-certificates.md)
or, for an internal CA, [self-signed.md](self-signed.md). A minimal Raft node configuration:

```hcl
ui            = false
disable_mlock = true            # Raft memory-maps its data; disable swap at the OS instead (section 8)
api_addr      = "https://vault-1.internal:8200"
cluster_addr  = "https://vault-1.internal:8201"   # Raft requires this, distinct from the listener

storage "raft" {
  path    = "/var/lib/vault/raft"
  node_id = "vault-1"
}

listener "tcp" {
  address         = "10.20.0.11:8200"
  cluster_address = "10.20.0.11:8201"
  tls_cert_file   = "/etc/vault.d/tls/server-fullchain.pem"
  tls_key_file    = "/etc/vault.d/tls/server.key"
  tls_min_version = "tls12"

  telemetry {
    unauthenticated_metrics_access = false
  }

  profiling {
    unauthenticated_pprof_access = false
  }
}
```

Substitute the node's actual addresses and certificate paths.
See the [TCP listener reference](https://developer.hashicorp.com/vault/docs/configuration/listener/tcp)
and [Integrated Storage configuration](https://developer.hashicorp.com/vault/docs/configuration/storage/raft).

## 4. Choose the seal, and initialize once

A fresh server starts sealed: the storage is encrypted and Vault cannot read it until it is unsealed,
and the seal you pick decides who or what does that. Shamir splits the unseal capability into key
shares (`vault operator init -key-shares=5 -key-threshold=3`), and a threshold of custodians must each
supply a share at the hidden prompt to unseal; never pass a share on the command line. Auto-unseal
uses the configured external seal service, such as AWS KMS (`seal "awskms" { ... }`) or another
Vault's Transit secrets engine, and instead emits recovery keys for privileged operations.
Transit auto-unseal is available in Community; seal wrapping requires Enterprise.
See [initialization](https://developer.hashicorp.com/vault/docs/commands/operator/init),
[the unseal prompt](https://developer.hashicorp.com/vault/docs/commands/operator/unseal),
[AWS KMS seals](https://developer.hashicorp.com/vault/docs/configuration/seal/awskms), and
[Transit seals](https://developer.hashicorp.com/vault/docs/configuration/seal/transit).

Initialize a cluster exactly once and join the other nodes to it. Capture initialization output
securely, including the unseal or recovery material and initial root token, and preserve split
custody of the shares. Later quorum-authorized rekey operations can replace unseal or recovery
shares. The trade cuts both ways: a threshold of unseal shares plus a copy of the storage is an
offline path to your data, while losing the required shares, or permanently losing the external
seal mechanism and its keys, can make the ciphertext, backups included, permanently unreadable.
See [operator rekey](https://developer.hashicorp.com/vault/docs/commands/operator/rekey).

Recovery keys authorize recovery operations but cannot decrypt the root key when the auto-unseal
mechanism is unavailable. A temporary outage prevents recovery until the mechanism returns;
permanent loss can make the cluster and backups unrecoverable. Enterprise seal HA is a separate
feature, not a Community fallback.
See [seal and recovery behavior](https://developer.hashicorp.com/vault/docs/concepts/seal).

## 5. Enable an audit device

A new cluster has no audit device, so requests are served with no durable record; server logs are not
a substitute. Enable one (`vault audit enable file file_path=/var/log/vault/audit.log`), and add a
second, independent one (`vault audit enable syslog` shipping to a SEPARATE host or failure domain: a local
syslog agent that writes the same disk is not independent), because auditing is fail-closed: when Vault
cannot write to at least one enabled device it "refuses to service the corresponding API request", so a
full disk on your only device is an outage. Collect both devices: either device alone can have gaps
when it was unavailable. The syslog device sends to the local syslog agent; configure that agent's
remote delivery and monitor it.
See [audit-device availability](https://developer.hashicorp.com/vault/docs/audit#availability-of-audit-devices)
and the [syslog device](https://developer.hashicorp.com/vault/docs/audit/syslog).

Monitor the disk and rotate the file: rename the audit file and send the Vault process `SIGHUP`
to reopen it, rather than truncating it.
See [file audit rotation](https://developer.hashicorp.com/vault/docs/audit/file#log-file-rotation).

Vault writes a keyed HMAC-SHA256 of most string values by default, so a
leaked string value is hashed rather than exposed; leave that on and never enable `log_raw`, but non-string
values are not hashed, so still restrict who can read the log and treat it as sensitive. A handful of endpoints,
including `sys/health` and `sys/seal-status`, are exempt from auditing, which matters when you verify
delivery below.
See [audit hashing and exemptions](https://developer.hashicorp.com/vault/docs/audit) and
[audit-device options](https://developer.hashicorp.com/vault/api-docs/system/audit).

## 6. Revoke the initial root token

The initial root token has unlimited access and no expiry, so it is a bootstrap credential, not an
operating one. Retire it in order: enable an audit device, configure an auth method and write scoped
admin policies, then actually log in as a non-root admin and confirm that identity works, and only then
revoke the root token from its own session with `vault token revoke -self`. Log in through the auth method, not with a token made by
`vault token create` while the root token is selected: that token is the root token's child and is
revoked with it (observed on the loopback run in Verify). Confirm the revocation (the
Verify section does), and delete any token-helper copy left in `~/.vault-token`. Keep no live root
token afterward; if you genuinely need root again, `vault operator generate-root` issues a new
one through the unseal quorum, or the recovery-key quorum under auto-unseal, which is the point of not
leaving one lying around.
See [token behavior](https://developer.hashicorp.com/vault/docs/concepts/tokens),
[self-revocation](https://developer.hashicorp.com/vault/docs/commands/token/revoke), and
[root generation](https://developer.hashicorp.com/vault/docs/commands/operator/generate-root).

For CLI authentication, select tokens through a securely injected `VAULT_TOKEN` environment variable
or a token helper. Enter interactive login credentials and unseal shares at the prompt.
Never put credentials in command arguments, URLs, shell history, or build logs.
See [CLI authentication](https://developer.hashicorp.com/vault/docs/commands) and
[login prompts](https://developer.hashicorp.com/vault/docs/commands/login).

## 7. Scope policies and tokens

The root policy bypasses every rule; every other identity gets only the capabilities its policies
grant, on a deny-by-default basis. Write narrow policies with `vault policy write`, prefer logins
through an auth method over long-lived tokens, and give tokens bounded TTLs so a leaked one expires.

An application that can read another application's secrets can turn one compromise into several.
For an existing KV v2 mount at `kv/`, grant only the required data path:

```bash
vault policy write payments-read - <<'HCL'
path "kv/data/payments/config" {
  capabilities = ["read"]
}
HCL
```

KV v2 policies use the API's `data/` path. This example grants neither writes nor metadata listing.
Give applications no `root` policy or `sudo` capability, and review every policy attached through
tokens and identities; one narrow policy does not cancel broader grants elsewhere. This Community
example is specifically for KV v2; do not copy its path unchanged for KV v1.
See [KV v2 API paths](https://developer.hashicorp.com/vault/api-docs/secret/kv/kv-v2),
[ACL policy semantics](https://developer.hashicorp.com/vault/docs/concepts/policies), and
[policy write](https://developer.hashicorp.com/vault/docs/commands/policy/write).

A short-lived Vault token does not help if its login credential can mint replacements indefinitely.
For a bounded batch job using AppRole, limit both the SecretID and the resulting token. Enable the
mount only if it does not already exist; substitute the application's actual source network for the
example CIDR.

```bash
# Enable only if approle/ does not already exist.
vault auth enable approle
vault write auth/approle/role/payments \
  bind_secret_id=true \
  secret_id_ttl=10m \
  secret_id_num_uses=1 \
  secret_id_bound_cidrs=10.20.30.0/24 \
  token_policies=payments-read \
  token_no_default_policy=true \
  token_type=service \
  token_ttl=5m \
  token_max_ttl=15m \
  token_explicit_max_ttl=15m \
  token_period=0 \
  token_num_uses=100 \
  token_bound_cidrs=10.20.30.0/24
```

SecretID limits govern login; token limits govern subsequent requests. An expired SecretID can still
log in until AppRole's once-a-minute tidy deletes it (observed in Verify). Zero use limits mean
unlimited use. `token_explicit_max_ttl` supplies a hard lifetime ceiling. This role excludes the
default policy, so clients must not assume its self-service permissions. The values are an example
workload budget, not Vault defaults; server and mount limits can shorten issued token lifetimes.
These are current Community role parameters, not a universal Vault Agent configuration.
See [AppRole configuration](https://developer.hashicorp.com/vault/docs/auth/approle),
[exact role parameters](https://developer.hashicorp.com/vault/api-docs/auth/approle), and
[token lifetime rules](https://developer.hashicorp.com/vault/docs/concepts/tokens).

A one-use SecretID requires fresh delivery for another login. Count the client's actual requests
before choosing a token use limit; limited-use tokens cannot create child tokens. HashiCorp generally
recommends batch tokens for AppRole, but service tokens are intentional here for use limiting and
individual revocation. Batch tokens have different renewal and revocation behavior.
See [AppRole constraints](https://developer.hashicorp.com/vault/docs/auth/approle) and
[token types](https://developer.hashicorp.com/vault/docs/concepts/tokens).

Passing a SecretID through deployment systems exposes it to every intermediary. Deliver a
short-lived, single-use wrapping token instead, and require wrapping in the delivery identity's
policy:

```bash
vault policy write payments-delivery - <<'HCL'
path "auth/approle/role/payments/secret-id" {
  capabilities = ["create", "update"]
  min_wrapping_ttl = "1s"
  max_wrapping_ttl = "60s"
}
HCL
```

Attach this policy to the deployment identity, not the application. A positive minimum wrapping
TTL requires wrapping on this path. Review the delivery identity's other policies as well; the
effective permissions and wrapping limits must preserve this restriction.
See [required response-wrapping TTLs](https://developer.hashicorp.com/vault/docs/concepts/policies#required-response-wrapping-ttls).

As that deployment identity:

```bash
vault write -wrap-ttl=60s -f auth/approle/role/payments/secret-id
```

Treat the returned wrapping token as a credential. Keep it out of build logs and transfer it
through the protected delivery channel. Before unwrapping, the recipient must use wrapping lookup
to validate its lifetime and exact `creation_path`, here
`auth/approle/role/payments/secret-id`. Unexpected, expired, or already-consumed tokens require
investigation. Wrapping-token expiry does not replace the SecretID's own TTL.
See [response wrapping and validation](https://developer.hashicorp.com/vault/docs/concepts/response-wrapping).

For an explicit lookup request, have the protected delivery mechanism populate an owner-readable
JSON file at `/run/secrets/payments-wrapping-lookup.json` with the wrapping token in its `token`
field. Pass that request on stdin:

```bash
vault write -format=json sys/wrapping/lookup - \
  < /run/secrets/payments-wrapping-lookup.json
```

Check `data.creation_path`, `data.creation_time`, and `data.creation_ttl`; the latter is the
original TTL, not the remaining lifetime. Confirm the token is still within that lifetime before
proceeding. Protect and remove the request file when finished.
See the [wrapping lookup API](https://developer.hashicorp.com/vault/api-docs/system/wrapping-lookup)
and [JSON input to write](https://developer.hashicorp.com/vault/docs/commands/write).

With that same wrapping token selected through securely injected `VAULT_TOKEN`, unwrap without a
token argument:

```bash
vault unwrap
```

Protect the output, which contains the SecretID. Response wrapping is available in Community;
this example targets current behavior. The conceptual reference notes that some wrapping-token
features date from Vault 0.8 and may be unavailable before that version.
See [unwrap](https://developer.hashicorp.com/vault/docs/commands/unwrap) and
[response wrapping](https://developer.hashicorp.com/vault/docs/concepts/response-wrapping).

Where workload identity already exists, use Kubernetes or JWT authentication instead of distributing
AppRole credentials. Kubernetes roles should bind explicit service-account names and namespaces.
JWT roles should constrain the intended identity and audience; since Vault 1.17, a JWT containing
`aud` requires an exact match with at least one configured `bound_audiences` value. These are
alternative integrations, not additional prerequisites for this example.
See [AppRole integration guidance](https://developer.hashicorp.com/vault/docs/auth/approle/approle-pattern),
[Kubernetes role bindings](https://developer.hashicorp.com/vault/api-docs/auth/kubernetes), and
[JWT authentication](https://developer.hashicorp.com/vault/docs/auth/jwt).

Do not try to "block all `sys/`": some system paths answer without authentication by design, both the
`sys/seal-status` and `sys/health` monitors need and the `sys/init` and `sys/leader` bootstrap paths,
and policy cannot close a bootstrap path, so keep an uninitialized or unsealed Vault off untrusted
networks (whoever reaches `sys/init` first can initialize it and take the root token). Other
authenticated system
operations are policy-gated, while recovery paths such as `sys/unseal` carry their own authorization, so
the control is correct policies plus network isolation, not blanket denial.
See [initialization](https://developer.hashicorp.com/vault/api-docs/system/init),
[leader status](https://developer.hashicorp.com/vault/api-docs/system/leader), and
[seal status](https://developer.hashicorp.com/vault/api-docs/system/seal-status).

## 8. Protect storage, memory, and backups

Encryption at rest protects confidentiality, not availability: whoever can reach the storage can still
delete or corrupt it, and a backup carries exactly the sensitivity of the live data. Run Vault as a
dedicated unprivileged user that cannot overwrite its own binary or configuration, keep the Raft
directory owned by that user and mode-restricted, take snapshots with
`vault operator raft snapshot save /var/backups/vault.snap` and guard them like the unseal material,
and give an external
backend its own TLS and access controls. Two memory paths leak live key material regardless of the
storage: swap and core dumps. Disable swap on the host so the OS cannot page secrets to disk (the Raft
configuration above disables `mlock` because Raft memory-maps its data, and disabling swap is the
compensating control), and disable core dumps for the service (`LimitCORE=0` in the systemd unit).
See [production hardening](https://developer.hashicorp.com/vault/docs/concepts/production-hardening)
and [Raft snapshots](https://developer.hashicorp.com/vault/docs/commands/operator/raft#snapshot-save).

Deployments using other storage backends should not generalize the Raft recommendation:
HashiCorp discourages disabling `mlock` outside Integrated Storage.
See [memory-locking configuration](https://developer.hashicorp.com/vault/docs/configuration#disable_mlock).

## Verify

Most checks below were **demonstrated on loopback** against Vault 2.1.1, the release binary with its
checksum verified against HashiCorp's published SHA256SUMS: a single Raft node running the section 3
configuration unchanged apart from addresses and paths, with the API on 127.0.0.1:8200, the cluster
listener on 127.0.0.1:8201, a private test CA, a file audit device, and the section 2 and section 7
policies and AppRole role with `127.0.0.1/32` as the CIDR. Each block ran as printed, with only its
placeholders substituted. What that setup cannot show is marked **REASONED** where it occurs: HA
standbys, a second independent audit device, renewal up to the explicit ceiling, the recipient's own
validation, and real network paths and firewalls; backlog row 1.114 and VAULT-LIVE-1 below track
them. The authoring host has no `sudo`, so the first block's `sudo ss -tlnp` ran through a stand-in
that runs `ss` without it; as the same account, `ss` still showed the Vault process.

The curl `exitcode` and `errormsg` write-out fields require curl 7.75.0 or newer.
For authenticated and on-host checks, transport failure, TLS failure, an unexpected redirect, or a
missing positive control is inconclusive, never the fixed state.
See [curl write-out fields](https://curl.se/docs/manpage.html#-w).

Paste whole blocks and substitute inside the single quotes. Use the base HTTPS URL without a
trailing slash where a block appends an API path. Never embed credentials in a URL. These guards
assume ordinary shell builtins; do not insert a literal apostrophe into a single-quoted placeholder.
Use a clean shell without inherited HTTP proxy settings or Vault proxy overrides for direct CLI
checks. Select each CLI identity through securely injected `VAULT_TOKEN` or its token helper;
do not paste token values into commands. Keep credential-bearing CLI output out of recordings and
build logs.

**Listener, health, audit, root revocation, and role inspection (demonstrated on loopback):** run
this on the Vault host as a non-root admin authorized to inspect audit devices, look up its own token,
and read the example AppRole:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_VAULT_HTTPS_URL' \
    'REPLACE_WITH_CA_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute value 1; not probing"; exit 1 ;;
    *)
      case "$2" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute value 2; not probing"; exit 1 ;;
        *)
          case "$1" in https://*) ;; *) echo "use an HTTPS URL"; exit 1 ;; esac
          [ -r "$2" ] || { echo "CA file is not readable"; exit 1; }
          unset VAULT_SKIP_VERIFY VAULT_AGENT_ADDR VAULT_NAMESPACE VAULT_WRAP_TTL || exit 1
          export VAULT_ADDR="$1" VAULT_CACERT="$2" || exit 1
          sudo ss -tlnp
          vault status -format=json
          curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
            --cacert "$2" -w 'http=%{http_code}\n' "$1/v1/sys/health"
          vault audit list -detailed
          vault token lookup
          vault token lookup -format=json
          vault read -format=json auth/approle/role/payments
          ;;
      esac
      ;;
  esac
)
```

Interpret the checks separately; the block's final exit status does not summarize them:

- **Bind and TLS (demonstrated on one node; the firewall REASONED):** read the whole socket table. Confirm `8200` is bound to the intended
  private address and `8201` to the cluster address, with nothing unexpected. A wildcard or unintended
  listener is a finding. The TLS health request must reach the intended server with certificate
  verification enabled. `ss` shows the bind, not the firewall; "only between nodes" is a firewall
  property. Confirm it with firewall rules and the permitted/forbidden-source probes below.
  See the [listener reference](https://developer.hashicorp.com/vault/docs/configuration/listener/tcp).
- **Server state (demonstrated for `501`, `503` and `200`):** status should report `initialized: true` and `sealed: false`.
  Status exit code `2` means sealed; an unsealed standby returns `0`; `1` means an error.
  Health codes `200` active, `429` standby, `501` uninitialized, and `503` sealed are common
  examples, not an exhaustive list. Current documentation also includes `474` for an unhealthy
  standby unable to reach the active node and `530` for a removed node. Codes `472` and `473`
  concern Enterprise disaster-recovery and performance-standby roles. Query parameters can change
  returned codes. A healthy response is a connectivity control, not proof of hardening.
  See [status](https://developer.hashicorp.com/vault/docs/commands/status) and the
  [health API](https://developer.hashicorp.com/vault/api-docs/system/health).
- **Audit configuration and delivery (demonstrated for one file device; two independent devices
  REASONED):** an empty audit list means requests are served
  unlogged. The fixed configuration lists the intended independent devices. Correlate the successful
  non-root JSON token lookup's `request_id` with `request.id` in the collected audit entries;
  the default table output omits the request ID. Check delivery to both destinations while both are
  healthy and retain both streams, since either can have gaps during an outage. A listed device
  without delivered records is not a successful delivery check. Do not use health requests for
  correlation because they are exempt from auditing.
  See [audit availability and exemptions](https://developer.hashicorp.com/vault/docs/audit),
  [audit listing](https://developer.hashicorp.com/vault/docs/commands/audit/list), and the
  [audit schema](https://developer.hashicorp.com/vault/docs/audit/schema).
- **Root revocation (demonstrated):** the scoped-admin token lookup is the positive control. Log that
  admin in through an auth method: a token made with `vault token create` while the root token is
  selected is the root token's child and is revoked with it.
  Repeat the guarded block with the revoked initial root credential still selected and judge its
  token-lookup results: Vault must return permission-denied or invalid-token errors. Other
  authenticated commands in that repeat will also fail. A successful root-token lookup is the
  exposed state. This proves that one token is dead, not that no root token exists; do not retain
  or generate a live root credential for testing.
  See [token lookup](https://developer.hashicorp.com/vault/docs/commands/token/lookup) and
  [self-revocation](https://developer.hashicorp.com/vault/docs/commands/token/revoke).
- **AppRole configuration (demonstrated):** compare the role read with every parameter in section 7,
  including both CIDR restrictions, SecretID TTL/use limits, service-token type, token TTL/max TTL/
  explicit max TTL, zero period, use limit, and exclusion of the default policy. Durations may be
  returned in seconds. A missing role or denied inspection is inconclusive; zero use limits,
  missing bounds, or broader attached policies do not satisfy this example. This read establishes
  configuration, not runtime enforcement.
  See the [AppRole role API](https://developer.hashicorp.com/vault/api-docs/auth/approle).

On the loopback run, `ss` showed only `127.0.0.1:8200` and `127.0.0.1:8201` for the Vault process.
Health returned `501` before initialization, `503` while sealed (status exit code `2`) and `200` once
unsealed (exit code `0`); a plaintext request got `400` "Client sent an HTTP request to an HTTPS
server", and a request without the CA failed certificate verification. The audit list showed the file
device, and the JSON token lookup's `request_id` matched two audit entries, the request and its
response. The role read returned every section 7 value, with durations in seconds. After `vault token
revoke -self`, the block with the revoked root token selected got `403` `invalid token` for the audit
list, both token lookups and the role read. A scoped admin created as a child of the root token lost
access with it, while an orphan token and a userpass login kept working.

**Application ACLs and authenticated monitoring (demonstrated on loopback):** for API authentication, provision an
owner-readable header file containing the selected identity's `X-Vault-Token` header through a
protected mechanism. The file must contain the actual header, not a shell variable reference.
Use only the intended authentication header, and remove the file when finished.

Run this block for each full endpoint URL and identity described below. It reports an anonymous
request followed by the same request with the selected credential; response bodies are discarded
to avoid printing secrets or profiles.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_FULL_HTTPS_API_URL' \
    'REPLACE_WITH_CA_FILE' \
    'REPLACE_WITH_TOKEN_HEADER_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 3 ] || { echo "the set -- line needs exactly 3 values; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute value 1; not probing"; exit 1 ;;
    *)
      case "$2" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute value 2; not probing"; exit 1 ;;
        *)
          case "$3" in
            *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute value 3; not probing"; exit 1 ;;
            *)
              case "$1" in https://*) ;; *) echo "use an HTTPS URL"; exit 1 ;; esac
              [ -r "$2" ] || { echo "CA file is not readable"; exit 1; }
              [ -r "$3" ] || { echo "header file is not readable"; exit 1; }
              curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
                --cacert "$2" -w 'anonymous http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
              curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
                --cacert "$2" --header "@$3" \
                -w 'authenticated http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
              ;;
          esac
          ;;
      esac
      ;;
  esac
)
```

| Check | Request and identity | Fixed outcome and matched positive control | Exposed outcome |
| --- | --- | --- | --- |
| Application's own secret | `GET /v1/kv/data/payments/config`, payments application token | Authenticated `200` for an existing, readable test fixture | Failure makes the cross-application denial inconclusive |
| Another application's secret | `GET /v1/kv/data/inventory/config`, payments application token | Application receives `403`; repeat the same URL with a fixture-reader identity authorized for that existing path and require `200` | Application receives `200` |
| Metrics | `GET /v1/sys/metrics`, metrics collector token, directly on the active node | Anonymous `403`, collector `200`, on each API listener of the active node | Anonymous `200` |
| Profiling | `GET /v1/sys/pprof/`, separate operator with `read` on `sys/pprof/*`, directly on the active node | Anonymous `403`, authorized operator `200`, on each API listener of the active node | Anonymous `200` |
| Collector isolation | `GET /v1/kv/data/payments/config`, metrics collector token | Collector receives `403`; payments application receives `200` for the same existing fixture | Collector receives `200` |

Use non-sensitive fixtures in an isolated test deployment. A `404` is not proof of an ACL denial.
For metrics, use the default JSON representation so the positive control does not depend on enabling
Prometheus output. For both monitoring checks, target the active node directly, or the sole server
in a single-node deployment. Confirm its role with the guarded status/health check above before
running the paired requests. Do not use a load balancer that can select a standby.

On the loopback run, every row gave its fixed outcome: anonymous `403` throughout; the payments token
`200` on its own secret and `403` on the inventory secret, where the fixture reader got `200`; the
collector `200` on `sys/metrics` and `403` on `sys/pprof/` and on the payments secret; the profiling
operator `200` on `sys/pprof/`.

**REASONED (no HA cluster here):** authenticated metrics and profiling use local-only HTTP handlers. An ordinary HA standby returns
`307` to the active node's advertised API address when a leader is available; that redirect is not
an authentication result. Performance standbys can serve local requests, but the local-only handler
rejects requests that require forwarding with `400` in the inspected implementation. Do not follow
redirects with the token or count redirects, forwarding errors, or missing positive controls as
passes; reconfirm the active node and repeat the pair. See the
[HTTP route and standby redirect implementation](https://raw.githubusercontent.com/hashicorp/vault/v1.21.0/http/handler.go)
and [local-only forwarding handling](https://raw.githubusercontent.com/hashicorp/vault/v1.20.0/http/logical.go).
Keep both anonymous-access settings disabled on every node's API listeners. Inspect each listener's
configuration and repeat the paired checks on each node when it is active during an authorized HA
test; a pair on the current active node does not verify other nodes' listener settings.

A collector's metrics-only policy is not a positive control for profiling; use the separately
authorized operator. HashiCorp's [debug permissions](https://developer.hashicorp.com/vault/docs/commands/debug#permissions)
grant `read` on `sys/pprof/*`, covering the trailing-slash index and profiling subpaths without
`sudo`. Leave the collector's policy unchanged. These checks follow the
[KV v2 API](https://developer.hashicorp.com/vault/api-docs/secret/kv/kv-v2),
[ACL capabilities](https://developer.hashicorp.com/vault/docs/concepts/policies#capabilities),
[listener authentication settings](https://developer.hashicorp.com/vault/docs/configuration/listener/tcp#telemetry-parameters),
[metrics API](https://developer.hashicorp.com/vault/api-docs/system/metrics), and
[profiling API](https://developer.hashicorp.com/vault/api-docs/system/pprof).

**Bounded credentials and tokens (demonstrated on loopback):** prepare an owner-readable
JSON request file containing `role_id` and `secret_id` through protected delivery. The following
login request reads the credentials from stdin, not argv. Its successful output contains a token;
handle it only in a protected session.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_VAULT_HTTPS_URL' \
    'REPLACE_WITH_CA_FILE' \
    'REPLACE_WITH_LOGIN_JSON_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 3 ] || { echo "the set -- line needs exactly 3 values; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute value 1; not probing"; exit 1 ;;
    *)
      case "$2" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute value 2; not probing"; exit 1 ;;
        *)
          case "$3" in
            *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute value 3; not probing"; exit 1 ;;
            *)
              case "$1" in https://*) ;; *) echo "use an HTTPS URL"; exit 1 ;; esac
              [ -r "$2" ] || { echo "CA file is not readable"; exit 1; }
              unset VAULT_SKIP_VERIFY VAULT_AGENT_ADDR VAULT_NAMESPACE VAULT_WRAP_TTL || exit 1
              export VAULT_ADDR="$1" VAULT_CACERT="$2" || exit 1
              [ -r "$3" ] || { echo "login request file is not readable"; exit 1; }
              vault write -format=json auth/approle/login - < "$3"
              ;;
          esac
          ;;
      esac
      ;;
  esac
)
```

Use separate credentials for independent cases so consuming a SecretID or token does not confound
another test:

- **SecretID use limit (demonstrated):** a fresh SecretID succeeds once from an allowed source.
  An immediate repeat with the same request file must fail with a Vault authentication error;
  another freshly delivered SecretID must succeed. Successful reuse is the exposed state.
- **SecretID expiry (demonstrated):** leave a separate SecretID unused for more than a minute beyond
  its ten-minute lifetime, then submit its login request. It must fail while a fresh SecretID succeeds
  from the same source. AppRole deletes expired SecretIDs in a tidy that runs once a minute, and until
  then an expired SecretID still logs in: on the loopback run, SecretIDs 10 seconds past their TTL
  logged in, while one 70 seconds past it was refused with `invalid role or secret ID`. Successful
  login more than a minute after expiry is the exposed state.
- **Source bounds (demonstrated with a second loopback address):** try a fresh SecretID from outside the configured CIDR but within
  a test network that can reach Vault. Require authentication rejection, paired with successful
  login using fresh credentials from the allowed CIDR. Test the resulting token's payments read
  with the guarded GET block from both sources: allowed source `200`, disallowed source `403`.
  Network refusal alone does not demonstrate either CIDR control. On the loopback run, with
  `127.0.0.1/32` as the CIDR, a login sent from 127.0.0.2 (the same JSON request through
  `curl --interface`, because the block's CLI cannot choose its source address) was refused with
  `source address "127.0.0.2" unauthorized by CIDR restrictions on the role`, a login from 127.0.0.1
  succeeded, and its token read the payments secret with `200` from 127.0.0.1 and `403` from 127.0.0.2.
- **Token lifetime and use budget (demonstrated; the renewal ceiling REASONED):** the login response
  must show the intended `token_policies` and a `lease_duration` of at most 300 seconds, and its token
  must begin `hvs.`, the service-token prefix (the CLI's JSON output has no token-type field). Using the guarded payments
  GET, require success before expiry and `403` after the issued lease expires, paired with `200`
  using a fresh token. Separately exhaust the 100-request budget before expiry, counting all token
  uses, and require subsequent denial while a fresh token succeeds. Continued access after expiry
  or exhaustion is the exposed state. The role read checks the fifteen-minute explicit ceiling;
  an expiry test without renewal does not independently demonstrate that renewal ceiling.
  Do not use token self-lookup as the application's validity test: this example excludes the
  default policy and does not grant that permission. On the loopback run, the login returned
  `token_policies` `payments-read` and `lease_duration` `300` with an `hvs.` token; a read returned
  `200` before the TTL and `403` ten seconds after it, while a fresh token got `200`; and 100 reads
  returned `200` before read 101 got `403`.

The discriminators come from the
[AppRole credential and role parameters](https://developer.hashicorp.com/vault/api-docs/auth/approle),
[AppRole constraints](https://developer.hashicorp.com/vault/docs/auth/approle), and
[token lifetime rules](https://developer.hashicorp.com/vault/docs/concepts/tokens).

**Mandatory wrapping (demonstrated on loopback):** select the deployment identity, not an administrator or root token. In an isolated test deployment,
the first two requests below must be rejected for their wrapping settings; inspect Vault's errors
rather than interpreting every nonzero exit as success. The sixty-second request is the matched
positive control and must return wrapping information. Unexpectedly successful negative requests
are findings; their credential-bearing output is discarded.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_VAULT_HTTPS_URL' \
    'REPLACE_WITH_CA_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute value 1; not probing"; exit 1 ;;
    *)
      case "$2" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute value 2; not probing"; exit 1 ;;
        *)
          case "$1" in https://*) ;; *) echo "use an HTTPS URL"; exit 1 ;; esac
          [ -r "$2" ] || { echo "CA file is not readable"; exit 1; }
          unset VAULT_SKIP_VERIFY VAULT_AGENT_ADDR VAULT_NAMESPACE VAULT_WRAP_TTL || exit 1
          export VAULT_ADDR="$1" VAULT_CACERT="$2" || exit 1
          if vault write -f auth/approle/role/payments/secret-id > /dev/null; then
            echo "FINDING: unwrapped issuance succeeded"
          else
            echo "Check that Vault rejected missing wrapping; other failures are inconclusive"
          fi
          if vault write -wrap-ttl=61s -f auth/approle/role/payments/secret-id > /dev/null; then
            echo "FINDING: issuance above the wrapping TTL ceiling succeeded"
          else
            echo "Check that Vault rejected the wrapping TTL; other failures are inconclusive"
          fi
          vault write -wrap-ttl=60s -f auth/approle/role/payments/secret-id
          ;;
      esac
      ;;
  esac
)
```

Without the policy restrictions, otherwise authorized issuance can succeed without wrapping or
with a longer wrapping TTL. That is the exposed comparison. A failure of the sixty-second positive
control leaves the result inconclusive. On the loopback run, both negative requests were refused
with `403` `permission denied`, which does not name the wrapping setting, so the positive control is
what separates a wrapping refusal from a missing permission; the sixty-second request returned
`wrapping_token_ttl` `1m` and `wrapping_token_creation_path` `auth/approle/role/payments/secret-id`.
See [required wrapping TTLs](https://developer.hashicorp.com/vault/docs/concepts/policies#required-response-wrapping-ttls)
and [wrapping requests](https://developer.hashicorp.com/vault/docs/concepts/response-wrapping).

**Recipient validation (the lookup demonstrated; the recipient's own check REASONED):** prepare the
protected JSON lookup request described in section 7, and select the received
wrapping token through securely injected `VAULT_TOKEN`. Lookup must succeed before unwrapping:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_VAULT_HTTPS_URL' \
    'REPLACE_WITH_CA_FILE' \
    'REPLACE_WITH_WRAPPING_LOOKUP_JSON_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 3 ] || { echo "the set -- line needs exactly 3 values; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute value 1; not probing"; exit 1 ;;
    *)
      case "$2" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute value 2; not probing"; exit 1 ;;
        *)
          case "$3" in
            *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute value 3; not probing"; exit 1 ;;
            *)
              case "$1" in https://*) ;; *) echo "use an HTTPS URL"; exit 1 ;; esac
              [ -r "$2" ] || { echo "CA file is not readable"; exit 1; }
              unset VAULT_SKIP_VERIFY VAULT_AGENT_ADDR VAULT_NAMESPACE VAULT_WRAP_TTL || exit 1
              export VAULT_ADDR="$1" VAULT_CACERT="$2" || exit 1
              [ -r "$3" ] || { echo "lookup request file is not readable"; exit 1; }
              vault write -format=json sys/wrapping/lookup - < "$3"
              ;;
          esac
          ;;
      esac
      ;;
  esac
)
```

Require the exact creation path, an original TTL from one through sixty seconds, and an unexpired
creation time plus TTL. An expired or consumed token must fail lookup; a fresh token from the same
delivery path is the positive control. In an isolated recipient test, a valid wrapping token from
an unexpected creation path must be rejected by the recipient before unwrapping; accepting it
is a recipient-validation finding even though Vault itself recognizes the token. On the loopback run,
the lookup returned `creation_path` `auth/approle/role/payments/secret-id`, `creation_ttl` `60` and the
creation time, and a lookup of the consumed token failed with `wrapping token is not valid or does
not exist`.
See [wrapping lookup fields](https://developer.hashicorp.com/vault/api-docs/system/wrapping-lookup)
and [recipient validation](https://developer.hashicorp.com/vault/docs/concepts/response-wrapping).

**Single-use unwrap (demonstrated on loopback):** only after the preceding
validation, run this block with that same wrapping token selected. The first unwrap must succeed;
repeat with the consumed token still selected and require a Vault invalid-token or
already-unwrapped error. A separate fresh, validated token must still unwrap successfully.
Protect the successful output, which contains the SecretID.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_VAULT_HTTPS_URL' \
    'REPLACE_WITH_CA_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute value 1; not probing"; exit 1 ;;
    *)
      case "$2" in
        *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute value 2; not probing"; exit 1 ;;
        *)
          case "$1" in https://*) ;; *) echo "use an HTTPS URL"; exit 1 ;; esac
          [ -r "$2" ] || { echo "CA file is not readable"; exit 1; }
          unset VAULT_SKIP_VERIFY VAULT_AGENT_ADDR VAULT_NAMESPACE VAULT_WRAP_TTL || exit 1
          export VAULT_ADDR="$1" VAULT_CACERT="$2" || exit 1
          vault unwrap
          ;;
      esac
      ;;
  esac
)
```

Successful reuse would violate the expected single-use behavior. Do not mistake selecting a new
token between requests for successful reuse of the original. On the loopback run, the first unwrap
returned the SecretID fields, the second failed with `wrapping token is not valid or does not exist`,
and a fresh wrapping token unwrapped.
See [unwrap](https://developer.hashicorp.com/vault/docs/commands/unwrap) and
[wrapping-token behavior](https://developer.hashicorp.com/vault/docs/concepts/response-wrapping).

**External isolation (both connection outcomes demonstrated on loopback; the real network
REASONED):** this last probe is the reverse of the on-host checks:
run it from a machine outside your trusted network, where the fixed state is that nothing answers.
Guard the address so the probe cannot run unsubstituted and time out as if the port were closed:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"") echo "substitute value 1; not probing"; exit 1 ;;
    *)
      curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
        -w 'http=%{http_code} time_connect=%{time_connect} exit=%{exitcode} err=%{errormsg}\n' \
        "https://$1:8200/v1/sys/seal-status"
      ;;
  esac
)
```

For this probe the discriminator is whether the TCP connection forms, not the HTTP reply: the fixed
state is `time_connect` at `0.000000` with `err` naming a refusal, no route, or a filtered-port timeout,
and any non-zero `time_connect`, even when the TLS handshake then fails against an internal CA, means
the port is reachable and is the finding. Run the same check against `8201` and every externally
reachable address. A name-resolution or local-socket error is inconclusive. This proves only that the
ADDRESS you tested is unreachable, not that Vault is: a mistyped or misrouted address also yields
`time_connect=0`, so confirm `$1` is the real external address (or public NAT) of the listener the on-host
`ss` showed bound to `8200`, so a typo does not read as isolation. On loopback, the probe against the listening address printed a
non-zero `time_connect` and curl's certificate-verification error (exit `60`), the reachable shape,
and against 127.0.0.2, where nothing listens, `time_connect=0.000000` and `Could not connect to
server` (exit `7`), the refused shape.

Pair the forbidden-source check with the same destination and port from a permitted host:
the positive control must establish a TCP connection. For `8201`, use a permitted Vault node.
If the permitted source cannot route to that destination, the matched control is unavailable;
record the limitation instead of claiming this probe demonstrates isolation. Confirm the firewall
rules as well; a single external probe only establishes reachability from that source.
See [production firewall guidance](https://developer.hashicorp.com/vault/docs/concepts/production-hardening),
[cluster communication](https://developer.hashicorp.com/vault/docs/concepts/ha), and
[seal-status API behavior](https://developer.hashicorp.com/vault/api-docs/system/seal-status).

| Backlog ID | Status | Required demonstration |
| --- | --- | --- |
| VAULT-LIVE-1 | OPEN - REASONED parts only; backlog row 1.114 | In an authorized isolated Vault deployment, demonstrate what a single loopback node cannot: HA standby behavior for the monitoring checks (redirects and local-only handlers), a second independent audit device and delivery to both destinations, renewal through the explicit token lifetime ceiling, recipient-side rejection of an unexpected creation path, and the external isolation probe from real permitted and forbidden sources against 8200 and 8201. Record the Vault version and edition, effective settings, requests, errors, and matched positive controls without credentials. |

## Sources (checked September 2026)

- Vault dev server (in-memory, insecure, not for production): https://developer.hashicorp.com/vault/docs/concepts/dev-server
- Vault TCP listener (address defaults, tls_disable, cluster_address): https://developer.hashicorp.com/vault/docs/configuration/listener/tcp
- Vault Integrated Storage (Raft) backend (path, node_id, cluster_addr): https://developer.hashicorp.com/vault/docs/configuration/storage/raft
- Vault seal concepts (sealed state, Shamir vs auto-unseal, recovery keys): https://developer.hashicorp.com/vault/docs/concepts/seal
- Vault operator init: https://developer.hashicorp.com/vault/docs/commands/operator/init
- Vault audit devices (fail-closed, HMAC default, exempt endpoints): https://developer.hashicorp.com/vault/docs/audit
- Vault production hardening (root token, swap, core dumps): https://developer.hashicorp.com/vault/docs/concepts/production-hardening
- Vault sys/health status codes: https://developer.hashicorp.com/vault/api-docs/system/health
- Vault policies and tokens: https://developer.hashicorp.com/vault/docs/concepts/policies
- Vault Login MFA (enforced on auth-method logins; the token auth method cannot use it): https://developer.hashicorp.com/vault/docs/auth/login-mfa
- Vault server flags (config, dev TLS, dev token-helper storage): https://developer.hashicorp.com/vault/docs/commands/server
- Vault configuration (UI default, advertised addresses, disable_mlock): https://developer.hashicorp.com/vault/docs/configuration
- Vault HA communication (advertised addresses and cluster TLS): https://developer.hashicorp.com/vault/docs/concepts/ha
- Vault KMIP secrets engine (Enterprise requirement and separate listener): https://developer.hashicorp.com/vault/docs/secrets/kmip
- Vault Agent configuration and listeners: https://developer.hashicorp.com/vault/docs/agent-and-proxy/agent
- Vault Proxy configuration and listeners: https://developer.hashicorp.com/vault/docs/agent-and-proxy/proxy
- Vault AWS KMS seal (auto-unseal and Enterprise seal wrapping): https://developer.hashicorp.com/vault/docs/configuration/seal/awskms
- Vault Transit seal (Community auto-unseal and Enterprise seal wrapping): https://developer.hashicorp.com/vault/docs/configuration/seal/transit
- Vault operator unseal (hidden prompt): https://developer.hashicorp.com/vault/docs/commands/operator/unseal
- Vault operator rekey (unseal and recovery shares): https://developer.hashicorp.com/vault/docs/commands/operator/rekey
- Vault file audit device and SIGHUP rotation: https://developer.hashicorp.com/vault/docs/audit/file
- Vault syslog audit device (local agent and remote-delivery responsibility): https://developer.hashicorp.com/vault/docs/audit/syslog
- Vault audit API (device options, log_raw, and inspection permissions): https://developer.hashicorp.com/vault/api-docs/system/audit
- Vault audit entry schema (request IDs and token-use fields): https://developer.hashicorp.com/vault/docs/audit/schema
- Vault audit list command: https://developer.hashicorp.com/vault/docs/commands/audit/list
- Vault token concepts (token prefixes, parent and child revocation, root tokens, TTLs, service and batch behavior): https://developer.hashicorp.com/vault/docs/concepts/tokens
- Vault token revoke command (self-revocation): https://developer.hashicorp.com/vault/docs/commands/token/revoke
- Vault root-token generation: https://developer.hashicorp.com/vault/docs/commands/operator/generate-root
- Vault CLI (environment variables, token helper, TLS, and wrapping options): https://developer.hashicorp.com/vault/docs/commands
- Vault login command (credential prompts): https://developer.hashicorp.com/vault/docs/commands/login
- Vault policy write command (HCL from stdin): https://developer.hashicorp.com/vault/docs/commands/policy/write
- Vault KV v2 API (data paths and read operations): https://developer.hashicorp.com/vault/api-docs/secret/kv/kv-v2
- Vault AppRole authentication (setup, token choice, and child-token constraints): https://developer.hashicorp.com/vault/docs/auth/approle
- Vault AppRole API (role parameters, SecretID generation, and login): https://developer.hashicorp.com/vault/api-docs/auth/approle
- Vault AppRole integration guidance (prefer existing workload identity): https://developer.hashicorp.com/vault/docs/auth/approle/approle-pattern
- Vault auth enable command: https://developer.hashicorp.com/vault/docs/commands/auth/enable
- Vault Kubernetes API (service-account and namespace bindings): https://developer.hashicorp.com/vault/api-docs/auth/kubernetes
- Vault JWT authentication (identity constraints and Vault 1.17 audience requirement): https://developer.hashicorp.com/vault/docs/auth/jwt
- Vault response wrapping (single use, delivery, validation, and historical version note): https://developer.hashicorp.com/vault/docs/concepts/response-wrapping
- Vault wrapping lookup API (creation path, time, and original TTL): https://developer.hashicorp.com/vault/api-docs/system/wrapping-lookup
- Vault write command (JSON stdin, format, and force flags): https://developer.hashicorp.com/vault/docs/commands/write
- Vault unwrap command (use the selected token without a token argument): https://developer.hashicorp.com/vault/docs/commands/unwrap
- Vault metrics API (GET, JSON format, and root namespace): https://developer.hashicorp.com/vault/api-docs/system/metrics
- Vault profiling API (index path and root namespace): https://developer.hashicorp.com/vault/api-docs/system/pprof
- Vault initialization API: https://developer.hashicorp.com/vault/api-docs/system/init
- Vault leader-status API: https://developer.hashicorp.com/vault/api-docs/system/leader
- Vault seal-status API (unauthenticated status): https://developer.hashicorp.com/vault/api-docs/system/seal-status
- Vault Raft operator commands (snapshot save): https://developer.hashicorp.com/vault/docs/commands/operator/raft
- Vault status command (JSON output and exit codes): https://developer.hashicorp.com/vault/docs/commands/status
- Vault 2.1.1 AppRole expired-SecretID tidy (once a minute; a SecretID may live up to a minute past expiry): https://github.com/hashicorp/vault/blob/v2.1.1/builtin/credential/approle/backend.go
- Vault token lookup command (selected-token lookup and JSON output): https://developer.hashicorp.com/vault/docs/commands/token/lookup
- curl options (header files, TLS verification, direct connections, and write-out fields): https://curl.se/docs/manpage.html
