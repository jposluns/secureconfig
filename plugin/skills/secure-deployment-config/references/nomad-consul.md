---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "fc7d1dae3a7aea0f0a6710547e7f882d435c1c85a650f90d3fcab196de1cba5c",
  "components": {
    "nomad": {
      "name": "Nomad Community Edition",
      "basis": "2.0.7",
      "sources": {
        "s52d80d2821ed": "https://github.com/hashicorp/nomad/blob/v2.0.7/command/agent/config.go",
        "sa1c2951d3ca6": "https://github.com/hashicorp/nomad/blob/v2.0.7/nomad/structs/config/ui.go",
        "s553448c7957c": "https://github.com/hashicorp/nomad/blob/v2.0.7/nomad/auth/auth.go",
        "s7496bcf129dc": "https://github.com/hashicorp/nomad/blob/v2.0.7/acl/acl.go",
        "sd665f15bc452": "https://github.com/hashicorp/nomad/blob/v2.0.7/drivers/exec/driver.go",
        "sd5c86223bdf5": "https://github.com/hashicorp/nomad/blob/v2.0.7/client/config/config.go",
        "sd5f2c389c6ae": "https://github.com/hashicorp/nomad/blob/v2.0.7/drivers/rawexec/driver.go",
        "se7ba8e4262dc": "https://github.com/hashicorp/nomad/blob/v2.0.7/nomad/structs/config/tls.go",
        "sc3e36e830b67": "https://github.com/hashicorp/nomad/blob/v2.0.7/nomad/acl_endpoint.go",
        "s754c582b7565": "https://github.com/hashicorp/nomad/blob/v2.0.7/command/agent/agent.go",
        "s8193264e48c2": "https://github.com/hashicorp/nomad/blob/v2.0.7/nomad/structs/acl.go",
        "sba39c1a9119a": "https://github.com/hashicorp/nomad/blob/v2.0.7/command/meta.go#L96",
        "sa04bf8c95cb6": "https://github.com/hashicorp/nomad/blob/v2.0.7/api/api.go#L388-L389"
      }
    },
    "consul": {
      "name": "Consul Community Edition",
      "basis": "2.0.4",
      "sources": {
        "s679a306e1b08": "https://github.com/hashicorp/consul/blob/v2.0.4/agent/config/default.go",
        "s8a0b5abac641": "https://github.com/hashicorp/consul/blob/v2.0.4/agent/config/builder.go",
        "sc4fb30ca3702": "https://github.com/hashicorp/consul/blob/v2.0.4/agent/consul/acl.go",
        "s35b783d75794": "https://github.com/hashicorp/consul/blob/v2.0.4/agent/acl_endpoint.go",
        "sa77598ec3695": "https://github.com/hashicorp/consul/blob/v2.0.4/agent/consul/acl_endpoint.go",
        "s00748de44382": "https://github.com/hashicorp/consul/blob/v2.0.4/acl/acl.go",
        "sab8a5866d9c9": "https://github.com/hashicorp/consul/blob/v2.0.4/agent/http.go",
        "sfeb50129fc10": "https://github.com/hashicorp/consul/blob/v2.0.4/agent/token/persistence.go"
      }
    }
  },
  "claims": {
    "nomad-bind": {"text": "Nomad defaults bind_addr=0.0.0.0 and all three listeners fall back to it; setting only addresses.http leaves RPC and gossip on bind_addr.", "components": ["nomad"], "sources": ["nomad:s52d80d2821ed"], "status": "REASONED"},
    "nomad-http": {"text": "Nomad HTTP API/UI uses 4646; UI defaults enabled at /ui/.", "components": ["nomad"], "sources": ["nomad:s52d80d2821ed", "nomad:sa1c2951d3ca6"], "status": "REASONED"},
    "nomad-rpc": {"text": "Nomad RPC uses 4647; keep it on private or management addresses.", "components": ["nomad"], "sources": ["nomad:s52d80d2821ed"], "status": "REASONED"},
    "nomad-gossip": {"text": "Nomad Serf uses 4648 TCP/UDP; gossip is unencrypted until encrypt is configured.", "components": ["nomad"], "sources": ["nomad:s52d80d2821ed"], "status": "REASONED"},
    "nomad-dev": {"text": "Linux -dev binds 127.0.0.1 except -dev-connect, which binds 0.0.0.0. Wildcard behavior was not observed.", "components": ["nomad"], "sources": ["nomad:s52d80d2821ed"], "status": "REASONED"},
    "nomad-acl-default": {"text": "ACLs default disabled; enable acl.enabled on every agent before exposing the API.", "components": ["nomad"], "sources": ["nomad:s52d80d2821ed", "nomad:s553448c7957c", "nomad:s7496bcf129dc"], "status": "REASONED"},
    "nomad-debug": {"text": "Debug endpoints still require enable_debug with ACLs off; -dev enables it.", "components": ["nomad"], "sources": ["nomad:s52d80d2821ed", "nomad:s7496bcf129dc"], "status": "REASONED"},
    "nomad-exec": {"text": "On a root Linux client, exec uses a chroot and task user, default nobody, with root refused by the default exec denylist; no client job was run.", "components": ["nomad"], "sources": ["nomad:sd665f15bc452", "nomad:sd5c86223bdf5"], "status": "REASONED"},
    "nomad-raw-exec": {"text": "raw_exec has no isolation and defaults off, but -dev enables it.", "components": ["nomad"], "sources": ["nomad:sd5f2c389c6ae", "nomad:s52d80d2821ed"], "status": "REASONED"},
    "nomad-remote-exec": {"text": "Remote task execution defaults enabled through disable_remote_exec=false.", "components": ["nomad"], "sources": ["nomad:s52d80d2821ed"], "status": "REASONED"},
    "nomad-tls": {"text": "HTTP/RPC TLS defaults off; enable both tls.http and tls.rpc.", "components": ["nomad"], "sources": ["nomad:se7ba8e4262dc"], "status": "REASONED"},
    "nomad-bootstrap-reset": {"text": "Unauthenticated PUT /v1/acl/bootstrap claims the first management token after ACL enablement; repeat is blocked until the operator reset file in data_dir/server.", "components": ["nomad"], "sources": ["nomad:sc3e36e830b67", "nomad:s754c582b7565"], "status": "REASONED"},
    "consul-client-bind": {"text": "Consul client_addr defaults 127.0.0.1; widening it or addresses.http makes the API reachable.", "components": ["consul"], "sources": ["consul:s679a306e1b08", "consul:s8a0b5abac641"], "status": "REASONED"},
    "consul-http": {"text": "Consul HTTP API is 8500; UI defaults off and -dev enables /ui/ on that port.", "components": ["consul"], "sources": ["consul:s679a306e1b08", "consul:s8a0b5abac641"], "status": "REASONED"},
    "consul-dns": {"text": "Consul DNS uses 8600 TCP/UDP on client_addr.", "components": ["consul"], "sources": ["consul:s679a306e1b08", "consul:s8a0b5abac641"], "status": "REASONED"},
    "consul-rpc": {"text": "Consul server RPC uses 8300 on bind_addr, default 0.0.0.0.", "components": ["consul"], "sources": ["consul:s679a306e1b08", "consul:s8a0b5abac641"], "status": "REASONED"},
    "consul-lan": {"text": "Consul LAN Serf uses 8301 TCP/UDP on bind_addr.", "components": ["consul"], "sources": ["consul:s679a306e1b08", "consul:s8a0b5abac641"], "status": "REASONED"},
    "consul-wan": {"text": "Consul WAN Serf uses 8302 TCP/UDP on bind_addr.", "components": ["consul"], "sources": ["consul:s679a306e1b08", "consul:s8a0b5abac641"], "status": "REASONED"},
    "consul-https": {"text": "Consul HTTPS defaults disabled.", "components": ["consul"], "sources": ["consul:s679a306e1b08", "consul:s8a0b5abac641"], "status": "REASONED"},
    "consul-grpc": {"text": "Plaintext gRPC defaults disabled; servers open TLS gRPC on 8503 on client_addr.", "components": ["consul"], "sources": ["consul:s679a306e1b08", "consul:s8a0b5abac641"], "status": "REASONED"},
    "consul-acl-default": {"text": "Consul ACLs default off and disabled ACL resolution grants management rights; with ACLs enabled default_policy still defaults allow.", "components": ["consul"], "sources": ["consul:s679a306e1b08", "consul:s8a0b5abac641", "consul:sc4fb30ca3702"], "status": "REASONED"},
    "consul-bootstrap-reset": {"text": "Bootstrap is unauthenticated and one-time until an operator writes acl-bootstrap-reset; bootstrap privately before exposing the API.", "components": ["consul"], "sources": ["consul:s35b783d75794", "consul:sa77598ec3695"], "status": "REASONED"},
    "consul-script": {"text": "enable_script_checks defaults off; enabling without ACLs or allow_write_http_from only warns. Prefer enable_local_script_checks if needed.", "components": ["consul"], "sources": ["consul:s8a0b5abac641"], "status": "REASONED"},
    "consul-remote-exec": {"text": "consul exec defaults disabled through disable_remote_exec=true.", "components": ["consul"], "sources": ["consul:s679a306e1b08"], "status": "REASONED"},
    "consul-tls-gossip": {"text": "TLS verification defaults off and gossip is unencrypted without encrypt.", "components": ["consul"], "sources": ["consul:s679a306e1b08", "consul:s8a0b5abac641"], "status": "REASONED"},
    "verify-inventory": {"text": "Inventory TCP/UDP on private or management addresses; wildcard exposed binds and actual external isolation remain reasoned.", "components": ["nomad", "consul"], "sources": ["nomad:s52d80d2821ed", "consul:s679a306e1b08"], "status": "REASONED", "verify": [1]},
    "loopback-listeners": {"text": "Loopback runs used substitute TCP/Serf UDP ports; Consul DNS, WAN and gRPC were disabled, so their live listeners were not demonstrated.", "components": ["nomad", "consul"], "sources": ["nomad:s52d80d2821ed", "consul:s679a306e1b08"], "status": "DEMONSTRATED", "evidence": "On the loopback run, the agents listened on TCP on test ports standing in for Nomad's 4646, 4647 and 4648 and Consul's 8500, 8300 and 8301 (the runs turned off Consul's DNS, Serf WAN and gRPC), and on UDP on the two Serf ports."},
    "nomad-acl-probe": {"text": "Loopback anonymous self/jobs/agent probes distinguished ACLs-off from ACLs-on; self remains 200 but changes AccessorID, while jobs and agent become 403.", "components": ["nomad"], "sources": ["nomad:s553448c7957c", "nomad:s7496bcf129dc", "nomad:s8193264e48c2"], "status": "DEMONSTRATED", "evidence": "All of these outcomes were observed with the curl probe block and these commands, on agents listening on test ports.", "verify": [2]},
    "nomad-agent-acl": {"text": "Server-handled paths can conceal a client with ACLs off; local /v1/agent/self exposed that client with 200 while the server returned 403.", "components": ["nomad"], "sources": ["nomad:s52d80d2821ed", "nomad:s7496bcf129dc"], "status": "DEMONSTRATED", "evidence": "In a cluster whose server had ACLs on and was bootstrapped, a client agent configured with `acl { enabled = false }` answered the first two paths with the ACLs-on results and `/v1/agent/self` with `200`, while the server answered it with `403`.", "verify": [2]},
    "nomad-bootstrap-run": {"text": "ACL probe rejection did not prove bootstrap complete; first bootstrap issued management credentials and the second returned already-done.", "components": ["nomad"], "sources": ["nomad:sc3e36e830b67"], "status": "DEMONSTRATED", "evidence": "Before bootstrap, the probe already printed the ACLs-on results; the first `nomad acl bootstrap` printed a management token and the second failed with `Unexpected response code: 400 (ACL bootstrap already done ...)`."},
    "nomad-anonymous-policy": {"text": "Anonymous rights come from the named anonymous policy; historical exported-token inspection found it absent, then present with submit-job despite unchanged probe results.", "components": ["nomad"], "sources": ["nomad:s8193264e48c2"], "status": "DEMONSTRATED", "evidence": "After an `anonymous` policy granting only `submit-job` was applied, the probe's results did not change, an anonymous job registration returned `200`, and `nomad acl policy info anonymous`, run in the same earlier form, showed the policy."},
    "nomad-job-registration": {"text": "Anonymous registration succeeded with ACLs off and failed with ACLs on and no anonymous policy; registration is not a demonstrated job execution.", "components": ["nomad"], "sources": ["nomad:s553448c7957c", "nomad:s7496bcf129dc"], "status": "DEMONSTRATED", "evidence": "With ACLs off, an anonymous job registration also returned `200`; with ACLs on and no `anonymous` policy, it returned `403`."},
    "nomad-token-input": {"text": "CLI accepts -token or NOMAD_TOKEN, not stdin; the current prompted one-command prefix avoids argv/history but retains same-user/root environment visibility. That form has no recorded run.", "components": ["nomad"], "sources": ["nomad:sba39c1a9119a", "nomad:sa04bf8c95cb6"], "status": "REASONED", "verify": [3]},
    "consul-acl-probe": {"text": "Loopback ACLs-off gave self 401/agent 200; enabled allow gave self 403/agent 200; enabled deny gave agent 403 with anonymous-permission text.", "components": ["consul"], "sources": ["consul:sc4fb30ca3702", "consul:s8a0b5abac641"], "status": "DEMONSTRATED", "evidence": "All of these outcomes were observed with this block and these commands, on agents listening on test ports.", "verify": [4]},
    "consul-agent-acl": {"text": "Each agent applies its own enabled/default_policy; mixed server/client configurations gave different results on their own APIs.", "components": ["consul"], "sources": ["consul:s8a0b5abac641", "consul:sc4fb30ca3702"], "status": "DEMONSTRATED", "evidence": "with the server on the `allow` policy and the client on `deny`, it printed `200` on `/v1/agent/self` against the server and the deny results against the client.", "verify": [4]},
    "consul-bootstrap-run": {"text": "Deny results appeared before bootstrap; first bootstrap issued a token and the second refused with bootstrap no longer allowed.", "components": ["consul"], "sources": ["consul:s35b783d75794", "consul:sa77598ec3695"], "status": "DEMONSTRATED", "evidence": "the first `consul acl bootstrap` printed a token and the second failed with `Unexpected response code: 403 (Permission denied: ACL bootstrap no longer allowed ...)`"},
    "consul-anonymous-token": {"text": "Inspect anonymous accessor 00000000-0000-0000-0000-000000000002 for policies, roles and identities; its recorded read listed none.", "components": ["consul"], "sources": ["consul:s00748de44382"], "status": "DEMONSTRATED", "evidence": "the anonymous token's read listed none of those sections."},
    "consul-default-token": {"text": "An agent default token substitutes for anonymous requests; recorded key-write default token yielded self 200 and agent 403 yet allowed an unauthenticated KV write.", "components": ["consul"], "sources": ["consul:sab8a5866d9c9", "consul:sfeb50129fc10"], "status": "DEMONSTRATED", "evidence": "On the loopback run, a default token holding key write, set through the agent's token API on a deny-policy agent, made the block print `200` on `/v1/acl/token/self` and a `403` on `/v1/agent/self` without the anonymous-token message, while a key-value write without a token succeeded.", "verify": [4]},
    "consul-kv": {"text": "Anonymous KV writes succeeded with ACLs off and allow policy, and were refused under deny.", "components": ["consul"], "sources": ["consul:sc4fb30ca3702", "consul:s679a306e1b08"], "status": "DEMONSTRATED", "evidence": "On the same runs an anonymous key-value write succeeded in both exposed states and was refused with `403` with the deny policy"},
    "consul-script-run": {"text": "With default script-check settings, remote script registration was refused.", "components": ["consul"], "sources": ["consul:s8a0b5abac641"], "status": "DEMONSTRATED", "evidence": "with script checks at their default, registering a script check through the API was refused with \"Scripts are disabled on this agent from remote calls\"."},
    "verify-tcp": {"text": "Probe each actual public IP with a known-open control; connected establishes reachability, refused/timeout only local nonreachability. This guide cross-references another guide's run; UDP is not tested.", "components": ["nomad", "consul"], "sources": ["nomad:s52d80d2821ed", "consul:s679a306e1b08"], "status": "REASONED", "verify": [5]},
    "verify-address-limits": {"text": "TCP guard refuses zero/dotted-IPv6 forms but permits loopback and some hex forms reaching the probing host; use public addresses and corroborate surprising connections with host sockets.", "components": ["nomad", "consul"], "sources": ["nomad:s52d80d2821ed", "consul:s679a306e1b08"], "status": "REASONED", "verify": [5]}
  }
}
---
# Nomad and Consul: the scheduler and service-mesh APIs

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| nomad-bind: Nomad defaults bind_addr=0.0.0.0 and all three listeners fall back to it; setting only addresses.http leaves RPC and gossip on bind_addr. | Nomad Community Edition 2.0.7 | REASONED |
| nomad-http: Nomad HTTP API/UI uses 4646; UI defaults enabled at /ui/. | Nomad Community Edition 2.0.7 | REASONED |
| nomad-rpc: Nomad RPC uses 4647; keep it on private or management addresses. | Nomad Community Edition 2.0.7 | REASONED |
| nomad-gossip: Nomad Serf uses 4648 TCP/UDP; gossip is unencrypted until encrypt is configured. | Nomad Community Edition 2.0.7 | REASONED |
| nomad-dev: Linux -dev binds 127.0.0.1 except -dev-connect, which binds 0.0.0.0. Wildcard behavior was not observed. | Nomad Community Edition 2.0.7 | REASONED |
| nomad-acl-default: ACLs default disabled; enable acl.enabled on every agent before exposing the API. | Nomad Community Edition 2.0.7 | REASONED |
| nomad-debug: Debug endpoints still require enable_debug with ACLs off; -dev enables it. | Nomad Community Edition 2.0.7 | REASONED |
| nomad-exec: On a root Linux client, exec uses a chroot and task user, default nobody, with root refused by the default exec denylist; no client job was run. | Nomad Community Edition 2.0.7 | REASONED |
| nomad-raw-exec: raw_exec has no isolation and defaults off, but -dev enables it. | Nomad Community Edition 2.0.7 | REASONED |
| nomad-remote-exec: Remote task execution defaults enabled through disable_remote_exec=false. | Nomad Community Edition 2.0.7 | REASONED |
| nomad-tls: HTTP/RPC TLS defaults off; enable both tls.http and tls.rpc. | Nomad Community Edition 2.0.7 | REASONED |
| nomad-bootstrap-reset: Unauthenticated PUT /v1/acl/bootstrap claims the first management token after ACL enablement; repeat is blocked until the operator reset file in data_dir/server. | Nomad Community Edition 2.0.7 | REASONED |
| consul-client-bind: Consul client_addr defaults 127.0.0.1; widening it or addresses.http makes the API reachable. | Consul Community Edition 2.0.4 | REASONED |
| consul-http: Consul HTTP API is 8500; UI defaults off and -dev enables /ui/ on that port. | Consul Community Edition 2.0.4 | REASONED |
| consul-dns: Consul DNS uses 8600 TCP/UDP on client_addr. | Consul Community Edition 2.0.4 | REASONED |
| consul-rpc: Consul server RPC uses 8300 on bind_addr, default 0.0.0.0. | Consul Community Edition 2.0.4 | REASONED |
| consul-lan: Consul LAN Serf uses 8301 TCP/UDP on bind_addr. | Consul Community Edition 2.0.4 | REASONED |
| consul-wan: Consul WAN Serf uses 8302 TCP/UDP on bind_addr. | Consul Community Edition 2.0.4 | REASONED |
| consul-https: Consul HTTPS defaults disabled. | Consul Community Edition 2.0.4 | REASONED |
| consul-grpc: Plaintext gRPC defaults disabled; servers open TLS gRPC on 8503 on client_addr. | Consul Community Edition 2.0.4 | REASONED |
| consul-acl-default: Consul ACLs default off and disabled ACL resolution grants management rights; with ACLs enabled default_policy still defaults allow. | Consul Community Edition 2.0.4 | REASONED |
| consul-bootstrap-reset: Bootstrap is unauthenticated and one-time until an operator writes acl-bootstrap-reset; bootstrap privately before exposing the API. | Consul Community Edition 2.0.4 | REASONED |
| consul-script: enable_script_checks defaults off; enabling without ACLs or allow_write_http_from only warns. Prefer enable_local_script_checks if needed. | Consul Community Edition 2.0.4 | REASONED |
| consul-remote-exec: consul exec defaults disabled through disable_remote_exec=true. | Consul Community Edition 2.0.4 | REASONED |
| consul-tls-gossip: TLS verification defaults off and gossip is unencrypted without encrypt. | Consul Community Edition 2.0.4 | REASONED |
| verify-inventory: Inventory TCP/UDP on private or management addresses; wildcard exposed binds and actual external isolation remain reasoned. | Nomad Community Edition 2.0.7; Consul Community Edition 2.0.4 | REASONED |
| loopback-listeners: Loopback runs used substitute TCP/Serf UDP ports; Consul DNS, WAN and gRPC were disabled, so their live listeners were not demonstrated. | Nomad Community Edition 2.0.7; Consul Community Edition 2.0.4 | DEMONSTRATED |
| nomad-acl-probe: Loopback anonymous self/jobs/agent probes distinguished ACLs-off from ACLs-on; self remains 200 but changes AccessorID, while jobs and agent become 403. | Nomad Community Edition 2.0.7 | DEMONSTRATED |
| nomad-agent-acl: Server-handled paths can conceal a client with ACLs off; local /v1/agent/self exposed that client with 200 while the server returned 403. | Nomad Community Edition 2.0.7 | DEMONSTRATED |
| nomad-bootstrap-run: ACL probe rejection did not prove bootstrap complete; first bootstrap issued management credentials and the second returned already-done. | Nomad Community Edition 2.0.7 | DEMONSTRATED |
| nomad-anonymous-policy: Anonymous rights come from the named anonymous policy; historical exported-token inspection found it absent, then present with submit-job despite unchanged probe results. | Nomad Community Edition 2.0.7 | DEMONSTRATED |
| nomad-job-registration: Anonymous registration succeeded with ACLs off and failed with ACLs on and no anonymous policy; registration is not a demonstrated job execution. | Nomad Community Edition 2.0.7 | DEMONSTRATED |
| nomad-token-input: CLI accepts -token or NOMAD_TOKEN, not stdin; the current prompted one-command prefix avoids argv/history but retains same-user/root environment visibility. That form has no recorded run. | Nomad Community Edition 2.0.7 | REASONED |
| consul-acl-probe: Loopback ACLs-off gave self 401/agent 200; enabled allow gave self 403/agent 200; enabled deny gave agent 403 with anonymous-permission text. | Consul Community Edition 2.0.4 | DEMONSTRATED |
| consul-agent-acl: Each agent applies its own enabled/default_policy; mixed server/client configurations gave different results on their own APIs. | Consul Community Edition 2.0.4 | DEMONSTRATED |
| consul-bootstrap-run: Deny results appeared before bootstrap; first bootstrap issued a token and the second refused with bootstrap no longer allowed. | Consul Community Edition 2.0.4 | DEMONSTRATED |
| consul-anonymous-token: Inspect anonymous accessor 00000000-0000-0000-0000-000000000002 for policies, roles and identities; its recorded read listed none. | Consul Community Edition 2.0.4 | DEMONSTRATED |
| consul-default-token: An agent default token substitutes for anonymous requests; recorded key-write default token yielded self 200 and agent 403 yet allowed an unauthenticated KV write. | Consul Community Edition 2.0.4 | DEMONSTRATED |
| consul-kv: Anonymous KV writes succeeded with ACLs off and allow policy, and were refused under deny. | Consul Community Edition 2.0.4 | DEMONSTRATED |
| consul-script-run: With default script-check settings, remote script registration was refused. | Consul Community Edition 2.0.4 | DEMONSTRATED |
| verify-tcp: Probe each actual public IP with a known-open control; connected establishes reachability, refused/timeout only local nonreachability. This guide cross-references another guide's run; UDP is not tested. | Nomad Community Edition 2.0.7; Consul Community Edition 2.0.4 | REASONED |
| verify-address-limits: TCP guard refuses zero/dotted-IPv6 forms but permits loopback and some hex forms reaching the probing host; use public addresses and corroborate surprising connections with host sockets. | Nomad Community Edition 2.0.7; Consul Community Edition 2.0.4 | REASONED |
<!-- version-basis:end -->

Nomad schedules and runs workloads, and Consul holds a cluster's service catalog, health checks and
key-value store. Both are controlled through an HTTP API that also serves a web UI, and both ship
with access control lists (ACLs) turned off. With ACLs off, anyone who reaches Nomad's API can
register a job, which is code the cluster runs, and anyone who reaches Consul's API can read and
write the catalog and the key-value store. Keep both APIs on private or management addresses
([cloud-firewalls.md](cloud-firewalls.md), [host.md](host.md), [tunnels.md](tunnels.md)), turn ACLs
on with a deny default, and bootstrap them before the API is reachable. Versions checked: Nomad
2.0.7 and Consul 2.0.4, Community Edition; Consul Enterprise namespaces and admin partitions are not covered.

## Nomad

A Nomad agent serves its HTTP API and web UI on 4646, RPC on 4647 and Serf gossip on 4648. The
default `bind_addr` is `0.0.0.0`, and each of the three listeners falls back to it, so a stock agent
listens on every address. The UI is enabled by default, at `/ui/` on the API port. `nomad agent -dev`
binds 127.0.0.1 on Linux, except `-dev-connect`, which binds `0.0.0.0`.

ACLs are disabled by default, and with ACLs off requests are allowed without a token, including job
registration; the agent's debug endpoints still need `enable_debug`, which `-dev` turns on.
A job is code: on a Linux client running as root, the `exec` driver runs a job's commands in a chroot
as the task's `user`, `nobody` when the task sets none (by default the client refuses `root` for
`exec`), and `raw_exec`, which runs commands with no isolation, is off by default but turned on by
`-dev`. Remote exec into running tasks is enabled by default (`disable_remote_exec = false`). TLS for
HTTP and RPC is off by default, and gossip is unencrypted until you set `encrypt`.

Set `bind_addr` to a private or management address (setting only `addresses.http` leaves RPC and
Serf on `bind_addr`), and turn ACLs on in every agent's configuration:

```hcl
acl {
  enabled = true
}
```

Then run `nomad acl bootstrap` at once, before the API is reachable. `PUT /v1/acl/bootstrap` needs no
token and works once, until an operator writes the `acl-bootstrap-reset` file in `<data_dir>/server`:
the first caller after ACLs are enabled receives the global management token.
Turn on TLS for HTTP and RPC (the `tls` block's `http` and `rpc` settings) and set a gossip `encrypt`
key.

## Consul

Consul's HTTP API listens on 8500 and its DNS interface on 8600 (TCP and UDP), both on `client_addr`,
which defaults to 127.0.0.1. Server RPC on 8300 and Serf gossip on 8301 (LAN) and 8302 (WAN) use
`bind_addr`, which defaults to `0.0.0.0`. HTTPS and plaintext gRPC are off by default; servers open
gRPC with TLS on 8503, also on `client_addr`. The web UI is off by default and on in `-dev`, at `/ui/` on the HTTP port. So a
stock Consul API is loopback-only, and it becomes reachable when `client_addr` or `addresses.http` is
widened.

ACLs are disabled by default, and with ACLs off every request has management rights: the key-value
store, the catalog and the agent endpoints. Enabling ACLs is not enough on its own: `default_policy`
defaults to `allow`, so an anonymous request can still read and write everything except ACL
management until you set `default_policy = "deny"`:

```hcl
acl {
  enabled        = true
  default_policy = "deny"
}
```

Put the same block on every agent, servers and clients: each agent applies its own `acl` block
(observed for `enabled` and `default_policy`).
Then run `consul acl bootstrap`; `PUT /v1/acl/bootstrap` needs no token and works once, until an
operator writes the `acl-bootstrap-reset` file. Script checks
run commands on the agent. `enable_script_checks` is off by default, and Consul's own startup warning
calls enabling it without ACLs and without `allow_write_http_from` "DANGEROUS"; it only warns. Use
`enable_local_script_checks` instead if you need them. `consul exec` is off by default
(`disable_remote_exec = true`). TLS verification is off by default, and gossip is unencrypted until you
set `encrypt`.

## Verify

These checks were demonstrated on loopback, against Nomad 2.0.7 and Consul 2.0.4 agents whose every
listener was bound to 127.0.0.1: the Nomad and Consul probes in each ACL state, the bootstrap and anonymous-policy checks, and the
listener list.
The exposed listener state is REASONED from source: the authoring host forbids binding every
interface, so the default wildcard bind was not observed, and no Nomad client ran a job.
The TCP reachability probe is the block demonstrated on loopback in
[low-code-builders.md](low-code-builders.md) with this guide's ports.

On each host, list the listeners, TCP and UDP:

REASONED: following block; default and external listener expectations follow the pinned Nomad and Consul sources; only the reduced loopback inventory below was observed, and wildcard binding was forbidden.

```bash
sudo ss -tlnp   # 4646, 4647, 4648 (Nomad); 8500, 8600, 8300, 8301, 8302, 8503 (Consul): private or management addresses only
sudo ss -ulnp   # Serf gossip on UDP 4648 (Nomad) and 8301, 8302 (Consul); Consul DNS on UDP 8600
```

Exposed, the reasoned expectation is a wildcard address (`*:`, `0.0.0.0:` or `[::]:`) on the API
ports, 4646 and 8500; fixed means a private or management address. On the loopback run, the agents
listened on TCP on test ports standing in for Nomad's 4646, 4647 and 4648 and Consul's 8500, 8300
and 8301 (the runs turned off Consul's DNS, Serf WAN and gRPC), and on UDP on the two Serf ports.

For Nomad, send three requests without a token, to every agent's API, servers and clients. Substitute the API URL (for example
`http://10.0.0.5:4646`) inside the single quotes, and paste the whole block.

DEMONSTRATED: following block; the recorded Nomad 2.0.7 loopback runs observed the ACL-off/on and per-agent HTTP results below on test ports, without running a client job.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NOMAD_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the Nomad URL on the set -- line above; not probing" ;;
    *) for path in /v1/acl/token/self /v1/jobs /v1/agent/self; do
         out=$(curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 15 -w '\n%{http_code} %{exitcode}' -- "$1$path" 2>&1)
         status=${out##*$'\n'}
         echo "GET $path (no token): http/exit=$status $(printf '%s' "${out%$'\n'*}" | grep -o -E '"AccessorID":"[^"]*"|^Permission denied$|^curl: .*' | head -n 1)"
       done ;;
  esac
)
```

Exposed (ACLs off): `/v1/acl/token/self` returns `200` with `"AccessorID":"acls-disabled"`, and
`/v1/jobs` and `/v1/agent/self` return `200`. With ACLs on, `/v1/acl/token/self` returns `200` with
`"AccessorID":"anonymous"`, and `/v1/jobs` and `/v1/agent/self` return `403` `Permission denied`.
The first two paths are answered by the servers, so of these three paths only `/v1/agent/self` shows
an agent whose own
`acl.enabled` is off; any agent that answers it with `200` is exposed. Those `403`s cover listing jobs
in the default namespace and reading the agent only, and they look the same before bootstrap, so
fixed needs two more checks on a server. First, `nomad acl bootstrap` must fail with an error that includes "ACL
bootstrap already done"; if it prints a management token instead, the cluster was claimable until
that moment, so keep the token as your own. Second, with a management token,
`nomad acl policy info anonymous` must report `404 (ACL policy not found)`: the anonymous token takes
its rights from the policy named `anonymous`. The block after the next paragraph runs it. A connection failure prints curl's error and exit code, and says nothing about ACLs. Any other
status or message is inconclusive: a redirect (for example from a trailing slash, or from HTTP to
HTTPS), a proxy's own response, or a certificate error once TLS is on says nothing about the
server's ACLs; run the curl block above from a host that trusts the cluster's CA.

`nomad` takes the token from `-token`, which puts it in argv, or from `NOMAD_TOKEN`, and has no stdin
input for it (checked at v2.0.7). The block prompts for the token, so it stays out of shell history,
and hands it to the one `nomad` command as a prefix assignment, never exported. That moves the token
out of argv, not out of reach: while `nomad` runs, it can be read from `/proc/<pid>/environ` by the
same account and by root.

REASONED: following block; token input follows the pinned Nomad 2.0.7 CLI source; the recorded policy inspection used the earlier exported-token form, not this prompt and prefix assignment.

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  { unset -n tok NOMAD_TOKEN && unset -v tok NOMAD_TOKEN; } 2>/dev/null ||
    { echo 'cannot clear tok or NOMAD_TOKEN in this shell; not probing'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not probing'; exit 2; }
  IFS= read -r -s -p 'Nomad management token (input hidden): ' tok < /dev/tty ||
    { echo 'token input failed; not probing'; exit 2; }
  printf '\n'
  [ -n "$tok" ] || { echo 'no token supplied; not probing'; exit 2; }
  NOMAD_TOKEN="$tok" nomad acl policy info anonymous
)
```

All of these outcomes were observed with the curl probe block and these commands, on agents listening on test
ports. In a cluster whose server had ACLs on and was bootstrapped, a client agent configured with
`acl { enabled = false }` answered the first two paths with the ACLs-on results and `/v1/agent/self`
with `200`, while the server answered it with `403`. Before bootstrap, the probe already printed the
ACLs-on results; the first `nomad acl bootstrap`
printed a management token and the second failed with `Unexpected response code: 400 (ACL bootstrap
already done ...)`. `nomad acl policy info anonymous` reported `404 (ACL policy not found)`, observed
with the token exported in a subshell, the form this guide used before #306. After an
`anonymous` policy granting only `submit-job` was applied, the probe's results did not change, an
anonymous job registration returned `200`, and `nomad acl policy info anonymous`, run in the same earlier form, showed the policy.
With ACLs off, an anonymous job registration also returned `200`; with ACLs on and no `anonymous`
policy, it returned `403`.

For Consul, send two requests without a token, to every agent's HTTP API, servers and clients; probe
an agent whose `client_addr` is loopback, the default, from its own host (for example
`http://127.0.0.1:8500`). Substitute the HTTP API URL (for example
`http://10.0.0.5:8500`) inside the single quotes, and paste the whole block.

DEMONSTRATED: following block; the recorded Consul 2.0.4 loopback runs observed disabled, allow, deny and per-agent/default-token HTTP outcomes below on test ports.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_CONSUL_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the Consul URL on the set -- line above; not probing" ;;
    *) for path in /v1/acl/token/self /v1/agent/self; do
         out=$(curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 15 -w '\n%{http_code} %{exitcode}' -- "$1$path" 2>&1)
         status=${out##*$'\n'}
         echo "GET $path (no token): http/exit=$status $(printf '%s' "${out%$'\n'*}" | grep -o -E '^ACL support disabled$|^token does not exist: ACL not found$|^Permission denied: anonymous token lacks permission|^curl: .*' | head -n 1)"
       done ;;
  esac
)
```

Exposed with ACLs off: `/v1/acl/token/self` returns `401` `ACL support disabled`, and
`/v1/agent/self` returns `200`. Exposed with ACLs on and the default `allow` policy:
`/v1/acl/token/self` returns `403` `token does not exist: ACL not found`, and `/v1/agent/self` still
returns `200`. Each agent applies its own `acl` block (observed for `enabled` and `default_policy`),
so any agent that answers `/v1/agent/self`
with `200` is exposed. With ACLs on and `default_policy = "deny"`, `/v1/agent/self` returns `403`
`Permission denied: anonymous token lacks permission`, but that `403` covers `agent:read` only, and it
looks the same before bootstrap, so fixed needs two more checks. First, `consul acl bootstrap` must
fail with an error that includes "ACL bootstrap no longer allowed"; if it prints a token instead,
keep it as your own. Second, with a management token in `CONSUL_HTTP_TOKEN`, `consul acl token read
-accessor-id 00000000-0000-0000-0000-000000000002` (the anonymous token; set `CONSUL_HTTP_TOKEN`
the same way, in a subshell around this command) must list no policies,
roles, or service, node or templated identities, and no agent may have a default token, set in
`acl.tokens.default` or through the agent's token API: a request without a token uses it instead of
the anonymous token. On the loopback run, a default token holding key write, set through the
agent's token API on a deny-policy agent, made the block print `200` on `/v1/acl/token/self` and a
`403` on `/v1/agent/self` without the anonymous-token message, while a key-value write without a
token succeeded. A `200` on `/v1/acl/token/self` without a token is how the block shows such a default
token. A connection failure prints curl's error and exit code, and says nothing about ACLs. Any other
status or message is inconclusive: a redirect (for example from a trailing slash, or from HTTP to
HTTPS), a proxy's own response, or a certificate error once TLS is on says nothing about the
server's ACLs; run the block from a host that trusts the cluster's CA.

All of these outcomes were observed with this block and these commands, on agents listening on test
ports. With a bootstrapped server on the deny policy and a client agent with ACLs off, the block
printed the deny results against the server, and `401` `ACL support disabled` and `200` against the
client; with the server on the `allow` policy and the client on `deny`, it printed `200` on
`/v1/agent/self` against the server and the deny results against the client. Before bootstrap, the
probe already printed the deny-policy results; the first `consul acl
bootstrap` printed a token and the second failed with `Unexpected response code: 403 (Permission
denied: ACL bootstrap no longer allowed ...)`; the anonymous token's read listed none of those
sections. On the same runs an anonymous key-value write succeeded in both exposed states and was
refused with `403` with the deny policy, and with script checks at their default, registering a script
check through the API was refused with "Scripts are disabled on this agent from remote calls".

Finally, from a host that should not have access, try a TCP connection to each port. The block takes
one IP address rather than a host name, so that a name with both IPv4 and IPv6 addresses cannot hide
one behind a timeout on the other: run it once for each public address of the host. It also takes a
port you know is open on that address from this host (for example SSH on 22) as the positive control,
and stops if the control does not connect. Substitute both inside the single quotes.

REASONED: following block; port targets follow the pinned Nomad and Consul defaults; the guide cross-references a loopback demonstration elsewhere, while external isolation was not demonstrated here.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ONE_IP_ADDRESS' 'REPLACE_WITH_A_KNOWN_OPEN_PORT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute one IP address on the set -- line above; not probing"; exit ;; esac
  case "$1" in 0.0.0.0) echo "$1 reaches this host itself; give the public address of the service; not probing"; exit ;; esac
  ipv4='^((25[012345]|2[01234][0123456789]|1[0123456789][0123456789]|[123456789]?[0123456789])[.]){3}(25[012345]|2[01234][0123456789]|1[0123456789][0123456789]|[123456789]?[0123456789])$'
  case "$1" in
    *:*:*)
      case "$1" in *[!0123456789ABCDEFabcdef.:]*) echo "$1 is not an IPv6 address; not probing"; exit ;; esac
      case "$1" in *.*) echo "give the IPv4 address itself rather than $1; not probing"; exit ;; esac
      case "$1" in *[!0:]*) ;; *) echo "$1 is all zeros (this host itself, or not an address); give the public address of the service; not probing"; exit ;; esac ;;
    *) [[ $1 =~ $ipv4 ]] || { echo "give one IPv4 address (four numbers, 0 to 255, joined by dots) or one IPv6 address, with no host name, port or brackets; not probing"; exit; } ;;
  esac
  case "$2" in *[!0123456789]*|"") echo "substitute a known-open control port on the set -- line above; not probing"; exit ;; esac
  { [ "$2" -ge 1 ] && [ "$2" -le 65535 ]; } 2>/dev/null || { echo "the control port must be 1 to 65535; not probing"; exit; }
  command -v timeout >/dev/null || { echo "timeout is not installed here; not probing"; exit; }
  # shellcheck disable=SC2016  # the single-quoted script is meant to expand $1 and $2 in the child shell
  err=$(LC_ALL=C timeout 5 bash -c ': > "/dev/tcp/$1/$2"' probe "$1" "$2" 2>&1) ||
    { echo "control $1:$2 did not connect (${err:-timed out}); not probing"; exit; }
  echo "control $1:$2 connected"
  for p in 4646 4647 4648 8500 8600 8300 8301 8302 8503; do
    # shellcheck disable=SC2016  # the single-quoted script is meant to expand $1 and $2 in the child shell
    err=$(LC_ALL=C timeout 5 bash -c ': > "/dev/tcp/$1/$2"' probe "$1" "$p" 2>&1)
    case "$?:$err" in
      0:*) echo "$1:$p connected: reachable from this host" ;;
      124:*) echo "$1:$p timed out from this host" ;;
      *"Connection refused"*) echo "$1:$p refused from this host" ;;
      *) echo "$1:$p inconclusive (not a connection, refusal or timeout): ${err:-no message}" ;;
    esac
  done
)
```

Exposed, a port reports "connected"; a transparent proxy on the probing host's network can also
complete the handshake, so confirm a surprising "connected" with `ss` on the host. "refused" and
"timed out" show only that this host could not reach the port: a firewall in front of the host
produces either, but so can filtering on the probing host's own network, and the control proves only
its own port. Treat them as consistent with fixed, and take `ss` on the host as the authority; the
probe does not test the UDP gossip or DNS sockets, which only `ss -ulnp` shows. "inconclusive" is any
other result and says nothing about the port. The block is the one demonstrated in
[low-code-builders.md](low-code-builders.md) with only the port list changed; that guide lists the
values it was measured to refuse. It refuses `0.0.0.0`, IPv6 values made only of zeros and colons,
and IPv6 values containing a dot, but not every value that reaches the probing host: loopback
addresses pass, and hex spellings such as `::ffff:0:0` connected to a listener bound to 127.0.0.1, so
give the host's public address. A "connected" on a port you did not mean to expose is the finding.

## Sources (checked September 2026)

- Nomad 2.0.7 agent defaults (`bind_addr`, ports, ACLs, `disable_remote_exec`, `-dev` binds, `raw_exec` and `enable_debug`): https://github.com/hashicorp/nomad/blob/v2.0.7/command/agent/config.go
- Nomad 2.0.7 UI default: https://github.com/hashicorp/nomad/blob/v2.0.7/nomad/structs/config/ui.go
- Nomad 2.0.7 TLS settings: https://github.com/hashicorp/nomad/blob/v2.0.7/nomad/structs/config/tls.go
- Nomad 2.0.7 `raw_exec` driver (default off, no isolation): https://github.com/hashicorp/nomad/blob/v2.0.7/drivers/rawexec/driver.go
- Nomad 2.0.7 `exec` driver (root on Linux, `nobody` when the task sets no user, chroot): https://github.com/hashicorp/nomad/blob/v2.0.7/drivers/exec/driver.go
- Nomad 2.0.7 client user denylist (`root` refused for `exec`): https://github.com/hashicorp/nomad/blob/v2.0.7/client/config/config.go
- Nomad 2.0.7 server data directory (`<data_dir>/server`, for the bootstrap reset file): https://github.com/hashicorp/nomad/blob/v2.0.7/command/agent/agent.go
- Nomad 2.0.7 ACL resolution when disabled: https://github.com/hashicorp/nomad/blob/v2.0.7/nomad/auth/auth.go and https://github.com/hashicorp/nomad/blob/v2.0.7/acl/acl.go
- Nomad 2.0.7 anonymous token (its rights come from the policy named `anonymous`): https://github.com/hashicorp/nomad/blob/v2.0.7/nomad/structs/acl.go
- Nomad 2.0.7 ACL bootstrap: https://github.com/hashicorp/nomad/blob/v2.0.7/nomad/acl_endpoint.go
- Nomad 2.0.7 CLI token input: `-token` (`command/meta.go` L96, L170-L171) or `NOMAD_TOKEN` (`api/api.go` L388-L389), with no stdin form: https://github.com/hashicorp/nomad/blob/v2.0.7/command/meta.go#L96 and https://github.com/hashicorp/nomad/blob/v2.0.7/api/api.go#L388-L389
- Consul 2.0.4 agent defaults (`bind_addr`, `client_addr`, ports, `default_policy`, `disable_remote_exec`, `-dev`): https://github.com/hashicorp/consul/blob/v2.0.4/agent/config/default.go
- Consul 2.0.4 configuration builder (listener addresses, ACL default, script checks and their warning, UI): https://github.com/hashicorp/consul/blob/v2.0.4/agent/config/builder.go
- Consul 2.0.4 ACL resolution when disabled: https://github.com/hashicorp/consul/blob/v2.0.4/agent/consul/acl.go
- Consul 2.0.4 anonymous token accessor ID: https://github.com/hashicorp/consul/blob/v2.0.4/acl/acl.go
- Consul 2.0.4 default token for requests without one (`acl.tokens.default`, agent token API): https://github.com/hashicorp/consul/blob/v2.0.4/agent/http.go and https://github.com/hashicorp/consul/blob/v2.0.4/agent/token/persistence.go
- Nomad 2.0.7 agent debug endpoints when ACLs are disabled (`enable_debug`): https://github.com/hashicorp/nomad/blob/v2.0.7/acl/acl.go
- Consul 2.0.4 ACL bootstrap: https://github.com/hashicorp/consul/blob/v2.0.4/agent/acl_endpoint.go and https://github.com/hashicorp/consul/blob/v2.0.4/agent/consul/acl_endpoint.go
