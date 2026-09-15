# HashiCorp Vault

Vault's own defaults are careful: the listener binds loopback, TLS is assumed (`tls_disable` is
`false`), and the web UI is off. The exposures are the deployment decisions you make on top of that,
and the corpus points you here from [machine-auth.md](machine-auth.md)
without saying how to stand one up safely. Five decisions decide it: not running dev mode, keeping TLS
on the listener you expose, choosing and guarding the seal, enabling an audit device, and retiring the
initial root token. OpenBao is the Linux Foundation open-source fork after Vault's move to the BUSL
licence; the controls below are written for Vault, and OpenBao shares the model but differs in some
commands, so check its own docs if you run it.

## 1. Never run dev mode in production

`vault server -dev` runs entirely in memory, initializes and unseals itself with a single key, serves
plain HTTP, and prints a known root token to the console; the `-dev-tls` variant adds a throwaway
certificate but is still a development server: it binds loopback rather than the world, but it stores
nothing durably, writes its printed root token into your token helper, and has none of the protections
below. Run a real server from a config file under your service manager
(`vault server -config=/etc/vault.d/vault.hcl`), and audit the systemd unit and its environment so no
`-dev` flag or dev-token override slips into production.

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
}
```

## 4. Choose the seal, and initialize once

A fresh server starts sealed: the storage is encrypted and Vault cannot read it until it is unsealed,
and the seal you pick decides who or what does that. Shamir splits the unseal capability into key
shares (`vault operator init -key-shares=5 -key-threshold=3`), and a threshold of custodians must each
supply a share at the hidden prompt to unseal; never pass a share on the command line. Auto-unseal
(`seal "awskms" { ... }`, or a `transit` seal against another Vault) unseals automatically from a KMS
key and instead emits recovery keys for privileged operations. Initialize a cluster exactly once and
join the other nodes to it; Vault emits the unseal or recovery material and the initial root token only
at that moment and never again, so capture them under split custody. The trade cuts both ways: a
threshold of shares plus a copy of the storage is an offline path to your data, while losing the
shares, or the KMS key behind an auto-unseal, makes the ciphertext, backups included, permanently
unreadable.

## 5. Enable an audit device

A new cluster has no audit device, so requests are served with no durable record; server logs are not
a substitute. Enable one (`vault audit enable file file_path=/var/log/vault/audit.log`), and add a
second, independent one (`vault audit enable syslog`), because auditing is fail-closed: when Vault
cannot write to at least one enabled device it "refuses to service the corresponding API request", so a
full disk on your only device is an outage. Monitor the disk and rotate the file by reopening it rather
than truncating it. Vault writes a keyed HMAC-SHA256 of most string values by default, so a
leaked string value is hashed rather than exposed; leave that on and never set `log_raw`, but non-string
values are not hashed, so still restrict who can read the log and treat it as sensitive. A handful of endpoints,
including `sys/health` and `sys/seal-status`, are exempt from auditing, which matters when you verify
delivery below.

## 6. Revoke the initial root token

The initial root token has unlimited access and no expiry, so it is a bootstrap credential, not an
operating one. Retire it in order: enable an audit device, configure an auth method and write scoped
admin policies, then actually log in as a non-root admin and confirm that identity works, and only then
revoke the root token from its own session with `vault token revoke -self`. Confirm the revocation (the
Verify section does), and delete any token-helper copy left in `~/.vault-token`. Keep no live root
token afterward; if you genuinely need root again, `vault operator generate-root` issues a new
one through the unseal quorum, or the recovery-key quorum under auto-unseal, which is the point of not
leaving one lying around.

## 7. Scope policies and tokens

The root policy bypasses every rule; every other identity gets only the capabilities its policies
grant, on a deny-by-default basis. Write narrow policies with `vault policy write`, prefer logins
through an auth method over long-lived tokens, and give tokens bounded TTLs so a leaked one expires.
Do not try to "block all `sys/`": some system paths answer without authentication by design, both the
`sys/seal-status` and `sys/health` monitors need and the `sys/init` and `sys/leader` bootstrap paths,
and policy cannot close a bootstrap path, so keep an uninitialized or unsealed Vault off untrusted
networks (whoever reaches `sys/init` first can initialize it and take the root token). Other
authenticated system
operations are policy-gated, while recovery paths such as `sys/unseal` carry their own authorization, so
the control is correct policies plus network isolation, not blanket denial.

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

## Verify

Every probe below is reasoned, not demonstrated: the authoring environment has no Vault instance to run
them against, so the outcomes are derived from the cited vendor pages rather than observed; backlog row
2.30 tracks demonstrating them; the `-w` fields need curl 7.75.0 or newer. For the on-host probes a
transport failure or a TLS error is inconclusive, never the fixed state.

```bash
sudo ss -tlnp                          # read the whole table: 8200 on the intended private address and
                                       # 8201 only between nodes, nothing unexpected beside them
vault status -format=json              # initialized true, sealed false; exit code 2 means sealed (a standby is 0)
curl -q -g -s -o /dev/null -w 'http=%{http_code}\n' --cacert /etc/vault.d/tls/ca.pem \
  https://vault-1.internal:8200/v1/sys/health   # 200 active, 429 standby, 501 uninitialized, 503 sealed
vault audit list -detailed             # a non-empty list; an empty one means requests are served unlogged
vault token lookup                     # run once after a scoped-admin login (succeeds, the control) and
                                       # once with the revoked initial root credential still selected,
                                       # which must return Vault's permission-denied or invalid-token error
```

Confirm the audit device actually records by correlating a non-root `vault token lookup` with an entry
in the log by request id; do not use `sys/health` for that, since it is on the audit exemption list. The
revocation check proves that one token is dead, not that no root token exists, so do not keep a live
root credential for testing. The last probe is the reverse of the ones above: run it from a machine
outside your trusted network, where the fixed state is that nothing answers. Guard the address so the
probe cannot run unsubstituted and time out as if the port were closed:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
    *) curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
         -w 'http=%{http_code} time_connect=%{time_connect} exit=%{exitcode} err=%{errormsg}\n' "https://$1:8200/v1/sys/seal-status" ;;
  esac
)
```

For this probe the discriminator is whether the TCP connection forms, not the HTTP reply: the fixed
state is `time_connect` at `0.000000` with `err` naming a refusal, no route, or a filtered-port timeout,
and any non-zero `time_connect`, even when the TLS handshake then fails against an internal CA, means
the port is reachable and is the finding. Run the same check against `8201` and every externally
reachable address. A name-resolution or local-socket error is inconclusive.

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
