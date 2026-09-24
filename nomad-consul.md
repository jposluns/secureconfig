# Nomad and Consul: the scheduler and service-mesh APIs

Nomad schedules and runs workloads, and Consul holds a cluster's service catalog, health checks and
key-value store. Both are controlled through an HTTP API that also serves a web UI, and both ship
with access control lists (ACLs) turned off. With ACLs off, anyone who reaches Nomad's API can
register a job, which is code the cluster runs, and anyone who reaches Consul's API can read and
write the catalog and the key-value store. Keep both APIs on private or management addresses
([cloud-firewalls.md](cloud-firewalls.md), [host.md](host.md), [tunnels.md](tunnels.md)), turn ACLs
on with a deny default, and bootstrap them before the API is reachable. Versions checked: Nomad
2.0.7 and Consul 2.0.4.

## Nomad

A Nomad agent serves its HTTP API and web UI on 4646, RPC on 4647 and Serf gossip on 4648. The
default `bind_addr` is `0.0.0.0`, and each of the three listeners falls back to it, so a stock agent
listens on every address. The UI is enabled by default, at `/ui/` on the API port. `nomad agent -dev`
binds 127.0.0.1 on Linux, except `-dev-connect`, which binds `0.0.0.0`.

ACLs are disabled by default, and with ACLs off every request is allowed, including job registration.
A job is code: on a Linux client running as root, the `exec` driver runs a job's commands as `nobody`
in a chroot, and `raw_exec`, which runs commands with no isolation, is off by default but turned on by
`-dev`. Remote exec into running tasks is enabled by default (`disable_remote_exec = false`). TLS for
HTTP and RPC is off by default, and gossip is unencrypted until you set `encrypt`.

Set `bind_addr` (or `addresses.http`) to a private or management address, and turn ACLs on in every
agent's configuration:

```hcl
acl {
  enabled = true
}
```

Then run `nomad acl bootstrap` at once, before the API is reachable. `PUT /v1/acl/bootstrap` needs no
token and works once: the first caller after ACLs are enabled receives the global management token.
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

Then run `consul acl bootstrap`; `PUT /v1/acl/bootstrap` needs no token and works once. Script checks
run commands on the agent. `enable_script_checks` is off by default, and Consul's own startup warning
calls enabling it without ACLs and without `allow_write_http_from` "DANGEROUS"; it only warns. Use
`enable_local_script_checks` instead if you need them. `consul exec` is off by default
(`disable_remote_exec = true`). TLS verification is off by default, and gossip is unencrypted until you
set `encrypt`.

## Verify

These checks were demonstrated on loopback, against Nomad 2.0.7 and Consul 2.0.4 agents whose every
listener was bound to 127.0.0.1: the Nomad and Consul probes in each ACL state and the listener list.
The exposed listener state is reasoned from source: the authoring host forbids binding every
interface, so the default wildcard bind was not observed, and no Nomad client ran a job. Backlog row
1.112 tracks demonstrating both.
The TCP reachability probe is the block demonstrated on loopback in
[low-code-builders.md](low-code-builders.md) with this guide's ports.

On each host, list the listeners, TCP and UDP:

```bash
sudo ss -tlnp   # 4646, 4647, 4648 (Nomad); 8500, 8600, 8300, 8301, 8302, 8503 (Consul): private or management addresses only
sudo ss -ulnp   # Serf gossip on UDP 4648 (Nomad) and 8301, 8302 (Consul); Consul DNS on UDP 8600
```

Exposed, the reasoned expectation is a wildcard address (`*:`, `0.0.0.0:` or `[::]:`) on the API
ports, 4646 and 8500; fixed means a private or management address. On the loopback run, the agents
listened on TCP for all three Nomad ports and all three enabled Consul ports, and on UDP for the Serf
ports.

For Nomad, send two requests without a token. Substitute the API URL (for example
`http://10.0.0.5:4646`) inside the single quotes, and paste the whole block.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NOMAD_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the Nomad URL on the set -- line above; not probing" ;;
    *) for path in /v1/acl/token/self /v1/jobs; do
         out=$(curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 15 -w '\n%{http_code} %{exitcode}' -- "$1$path" 2>&1)
         status=${out##*$'\n'}
         echo "GET $path (no token): http/exit=$status $(printf '%s' "${out%$'\n'*}" | grep -o -E '"AccessorID":"[^"]*"|^Permission denied$|^curl: .*' | head -n 1)"
       done ;;
  esac
)
```

Exposed (ACLs off): `/v1/acl/token/self` returns `200` with `"AccessorID":"acls-disabled"`, and
`/v1/jobs` returns `200`. Fixed (ACLs on): `/v1/acl/token/self` returns `200` with
`"AccessorID":"anonymous"`, and `/v1/jobs` returns `403` `Permission denied`. A connection failure
prints curl's error and exit code, and says nothing about ACLs. All three outcomes were observed with
this block; on the same runs, an anonymous job registration returned `200` with ACLs off and `403`
with ACLs on, and an anonymous `PUT /v1/acl/bootstrap` succeeded once and then returned `400` "ACL
bootstrap already done". A `403` on `/v1/jobs` also depends on no permissive `anonymous` policy
having been written.

For Consul, send two requests without a token. Substitute the HTTP API URL (for example
`http://10.0.0.5:8500`) inside the single quotes, and paste the whole block.

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
`/v1/acl/token/self` returns `403` `token does not exist: ACL not found`, and `/v1/agent/self`
still returns `200`. Fixed (ACLs on, `default_policy = "deny"`): `/v1/agent/self` returns `403`
`Permission denied: anonymous token lacks permission`. All of these were observed with this block,
and on the same runs an anonymous key-value write succeeded in both exposed states and was refused
with `403` in the fixed one, and an anonymous `PUT /v1/acl/bootstrap` succeeded once and was then
refused. With script checks at their default, registering a script check through the API was refused
with "Scripts are disabled on this agent from remote calls".

Finally, from a host that should not have access, try a TCP connection to each port. The block takes
one IP address rather than a host name, so that a name with both IPv4 and IPv6 addresses cannot hide
one behind a timeout on the other: run it once for each public address of the host. It also takes a
port you know is open on that address from this host (for example SSH on 22) as the positive control,
and stops if the control does not connect. Substitute both inside the single quotes.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ONE_IP_ADDRESS' 'REPLACE_WITH_A_KNOWN_OPEN_PORT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute one IP address on the set -- line above; not probing"; exit ;; esac
  case "$1" in 0.0.0.0) echo "$1 reaches this host itself; give the service's public address; not probing"; exit ;; esac
  ipv4='^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])[.]){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$'
  case "$1" in
    *:*:*)
      case "$1" in *[!0-9A-Fa-f.:]*) echo "$1 is not an IPv6 address; not probing"; exit ;; esac
      case "$1" in *.*) echo "give the IPv4 address itself rather than $1; not probing"; exit ;; esac
      case "$1" in *[!0:]*) ;; *) echo "$1 is all zeros (this host itself, or not an address); give the service's public address; not probing"; exit ;; esac ;;
    *) [[ $1 =~ $ipv4 ]] || { echo "give one IPv4 address (four numbers, 0 to 255, joined by dots) or one IPv6 address, with no host name, port or brackets; not probing"; exit; } ;;
  esac
  case "$2" in *[!0-9]*|"") echo "substitute a known-open control port on the set -- line above; not probing"; exit ;; esac
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

- Nomad 2.0.7 agent defaults (`bind_addr`, ports, ACLs, `disable_remote_exec`, `-dev` binds and `raw_exec`): https://github.com/hashicorp/nomad/blob/v2.0.7/command/agent/config.go
- Nomad 2.0.7 UI default: https://github.com/hashicorp/nomad/blob/v2.0.7/nomad/structs/config/ui.go
- Nomad 2.0.7 TLS settings: https://github.com/hashicorp/nomad/blob/v2.0.7/nomad/structs/config/tls.go
- Nomad 2.0.7 `raw_exec` driver (default off, no isolation): https://github.com/hashicorp/nomad/blob/v2.0.7/drivers/rawexec/driver.go
- Nomad 2.0.7 `exec` driver (root on Linux, `nobody`, chroot): https://github.com/hashicorp/nomad/blob/v2.0.7/drivers/exec/driver.go
- Nomad 2.0.7 ACL resolution when disabled: https://github.com/hashicorp/nomad/blob/v2.0.7/nomad/auth/auth.go and https://github.com/hashicorp/nomad/blob/v2.0.7/acl/acl.go
- Nomad 2.0.7 ACL bootstrap: https://github.com/hashicorp/nomad/blob/v2.0.7/nomad/acl_endpoint.go
- Consul 2.0.4 agent defaults (`bind_addr`, `client_addr`, ports, `default_policy`, `disable_remote_exec`, `-dev`): https://github.com/hashicorp/consul/blob/v2.0.4/agent/config/default.go
- Consul 2.0.4 configuration builder (listener addresses, ACL default, script checks and their warning, UI): https://github.com/hashicorp/consul/blob/v2.0.4/agent/config/builder.go
- Consul 2.0.4 ACL resolution when disabled: https://github.com/hashicorp/consul/blob/v2.0.4/agent/consul/acl.go
- Consul 2.0.4 ACL bootstrap: https://github.com/hashicorp/consul/blob/v2.0.4/agent/acl_endpoint.go and https://github.com/hashicorp/consul/blob/v2.0.4/agent/consul/acl_endpoint.go
