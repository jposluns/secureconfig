# Memcached: bind privately; authentication and TLS are optional builds

Memcached has no authentication by default, and its `-l` option defaults to `INADDR_ANY`, so a stock start listens on every interface on TCP 11211 and serves any client that connects. The project's own wording: memcached "does not spend much, if any, effort in ensuring its defensibility from random internet connections", so it "must not" be exposed to the internet or to untrusted users. The practical control is network isolation; SASL and TLS exist, but each needs a build compiled with that feature. SASL adds no encryption; SASL PLAIN credentials need TLS. See the [server configuration documentation](https://docs.memcached.org/serverguide/configuring/) and [SASL documentation](https://docs.memcached.org/protocols/binarysasl/).

Use a maintained package carrying current security fixes. Feature introduction dates below describe availability, not a recommended deployment version. At the time of writing, [upstream lists 1.6.45 as current stable](https://memcached.org/). [1.6.42](https://github.com/memcached/memcached/wiki/ReleaseNotes1642) was explicitly security-focused and included SASL, authentication, and protocol fixes; [1.6.45](https://github.com/memcached/memcached/wiki/ReleaseNotes1645) contains further security and crash fixes. Review distribution backports and test upgrades on a canary before rollout.

The startup examples build on one another; apply the chosen arguments to one service instance, rather than starting every example concurrently. Distribution service accounts and configuration files vary.

## 1. Bind to loopback or a private interface, UDP off

```bash
memcached -l 127.0.0.1 -p 11211 -U 0
```

`-l` accepts an address or `host:port`; the man page calls it "an important option to consider as there is no other way to secure the installation". Put the same flags in your distribution's service configuration, and firewall 11211 per [cloud-firewalls.md](cloud-firewalls.md) or [host.md](host.md). For clients on other hosts, prefer a private network or a tailnet ([tailscale.md](tailscale.md)) over a public listener.

Use `-l 127.0.0.1` for local clients, or the actual private interface address for remote clients. Avoid wildcard listeners such as `0.0.0.0` and `::`. Permit only intended clients through the firewall. Repeated `-l` options and address-specific ports can create additional listeners; inspect every listener. See the [network configuration documentation](https://github.com/memcached/memcached/wiki/ConfiguringServer#networking).

Set both transport ports explicitly: `-p 11211 -U 0`. Changing the TCP port does not provide access control. `-p 0` disables TCP; `-U 0` disables UDP. These meanings are documented in the [1.6.45 man page](https://raw.githubusercontent.com/memcached/memcached/1.6.45/doc/memcached.1).

UDP defaults to disabled since 1.5.6. Retain explicit `-U 0` to override inherited package settings: public UDP enables reflection and amplification attacks. The older configuration wiki's illustrative `udpport 11211` output is not the desired state. See the [vendor DDoS advisory](https://docs.memcached.org/advisories/ddos/).

## 2. Run under a dedicated unprivileged account

Limit the host privileges available to a compromised cache process. Run the service as its dedicated account. If the launcher starts as root, add `-u memcache`, substituting the existing service account:

```bash
memcached -l 127.0.0.1 -p 11211 -U 0 -u memcache
```

`-u` changes identity only when started as root; it does not create the account. If the service manager already starts memcached as its dedicated unprivileged account, configure that identity there. Distribution account names vary. See the [1.6.45 man page](https://raw.githubusercontent.com/memcached/memcached/1.6.45/doc/memcached.1).

Supported builds also offer `-o drop_privileges` for additional syscall restrictions. This is separate from `-u`, and the [1.6.45 CLI help](https://raw.githubusercontent.com/memcached/memcached/1.6.45/memcached.c) documents it as disabled by default. Treat it as a follow-up control until tested with the deployed platform, build, and required operations.

## 3. Bound connections and item memory

Set a connection budget and an item-storage budget:

```bash
memcached -l 127.0.0.1 -p 11211 -U 0 -u memcache -c 256 -m 256
```

These are example capacities. Calculate the connection limit from application pools and leave operational headroom. Allow memory for connections, threads, and other overhead beyond `-m`. `-m` is not a total process-memory limit, and `-c` is not a request-rate limit. Network isolation remains necessary.

The documented upstream defaults are 1024 connections and 64 MB of item storage. Verify the service's effective configuration because package overrides can differ. See the [man page](https://raw.githubusercontent.com/memcached/memcached/1.6.45/doc/memcached.1) and [memory and connection guidance](https://github.com/memcached/memcached/wiki/ConfiguringServer).

Optionally, `-o idle_timeout=60` retires idle connections. Choose a timeout compatible with connection pools. The 1.6.45 default is zero, meaning no timeout; binary-protocol handling was fixed in 1.5.15. See the [CLI implementation](https://raw.githubusercontent.com/memcached/memcached/1.6.45/memcached.c) and [1.5.15 release notes](https://github.com/memcached/memcached/wiki/ReleaseNotes1515).

## 4. SASL authentication (binary protocol only)

For clients that require binary SASL, use a build configured with `--enable-sasl`; add `--enable-tls` when building the encrypted deployment:

```bash
./configure --enable-sasl --enable-tls
```

SASL support dates to 1.4.3 and requires a compatible client and build. Confirm the installed binary advertises `-S`, then retain `-S` in the service arguments. Install the Cyrus SASL mechanism required by the client. See the [SASL how-to](https://github.com/memcached/memcached/wiki/SASLHowto) and [TLS build documentation](https://docs.memcached.org/features/tls/).

Credentials come from the Cyrus SASL password database. The password command prompts interactively:

```bash
saslpasswd2 -a memcached -c cacheuser
memcached -l 10.0.0.5 -p 11211 -U 0 -u memcache -c 256 -m 256 -S
```

This demonstrates SASL enablement; add TLS as in step 5 before sending PLAIN credentials. The password database must be owned by, and readable only by, the account running memcached. SASL provides authentication without encrypting cache traffic and is intended to protect against neighbours and accidents inside a mostly trusted network, not to justify internet exposure. See the [SASL documentation](https://docs.memcached.org/protocols/binarysasl/).

`-S` enables SASL commands and requires the binary protocol. Protected operations such as GET require successful authentication. Binary VERSION and SASL negotiation commands are permitted before authentication, so a VERSION response does not demonstrate an authentication bypass. See the [1.6.45 binary dispatcher](https://raw.githubusercontent.com/memcached/memcached/1.6.45/proto_bin.c). Because SASL protects only the binary protocol, keep every listener on the binary protocol. memcached supports per-listener protocol overrides, and an ASCII connection, including one that selects ASCII on a negotiating listener, bypasses SASL even with `-S`, so such a listener would accept commands without credentials; a negotiated binary connection still undergoes the SASL check. Probe each listener with an unauthenticated ASCII GET as well as the binary no-credentials check, so an ASCII bypass on any listener is caught.

The binary protocol is [deprecated upstream](https://docs.memcached.org/protocols/). For new text/meta clients, use private networking and an appropriate authenticated TLS deployment. ASCII has no SASL authentication, but optional ASCII token authentication exists: `-Y /etc/memcached/authfile`.

Provision that file with one `username:password` pair per line, readable only by the service account. Configure a client that implements the token exchange: a fake `set` command carries `username password` as its value. Carry that exchange over TLS and keep passwords out of startup arguments. See the [authentication wire format](https://raw.githubusercontent.com/memcached/memcached/7278bdee96329915bbc87731ba005095453f5c2f/doc/protocol.txt).

`-Y` arrived in 1.5.15, is built in without SASL dependencies, and provides no per-user authorization after login. Choose it as an alternative to binary SASL. See the [1.5.15 release notes](https://github.com/memcached/memcached/wiki/ReleaseNotes1515). It remains experimental in 1.6.45. Binary operation is excluded; a nonzero UDP configuration is rejected at startup, rather than silently overridden, so retain `-U 0`. See the [1.6.45 option handling](https://raw.githubusercontent.com/memcached/memcached/1.6.45/memcached.c).

## 5. TLS (1.5.13 and later, build with `--enable-tls`)

The TLS documentation specifies a build configured with `--enable-tls` against OpenSSL 1.1.1 or later, and a client library that speaks TLS. TLS is off by default. This example combines the preceding controls with the command restrictions in steps 6 and 7:

```bash
memcached -l 10.0.0.5 -p 11211 -U 0 -u memcache -c 256 -m 256 -S -Z -F -X -W \
  -o ssl_chain_cert=/etc/memcached/tls/fullchain.pem,ssl_key=/etc/memcached/tls/privkey.pem
```

`--enable-tls` is the build option; `-Z` (`--enable-ssl`) enables TLS at runtime. `ssl_chain_cert` and `ssl_key` point at the PEM certificate chain and key ([free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md)). `-o` accepts comma-separated extended options.

`-o ssl_verify_mode=2` with `-o ssl_ca_cert=/path/ca.pem`, substituting the actual CA file, requires client certificates. This provides mutual TLS and a possession factor for machine clients ([machine-auth.md](machine-auth.md)). The default verification mode is `0`, which does not require client certificates. See the [TLS documentation](https://docs.memcached.org/features/tls/).

A `-l notls:127.0.0.1:11211` listener explicitly bypasses TLS for local tooling. It does not remove `-S`'s binary-protocol requirement. Keep this exception restricted to loopback if an existing deployment requires it; do not add a plaintext listener merely to obtain text administration commands.

On a text-capable listener, `refresh_certs` reloads certificates without a restart, and `stats settings` shows active `ssl_` values. Those text requests cannot simply be sent to the demonstrated `-S` listener. In 1.6.45, use the service manager to send SIGHUP to the verified memcached process for certificate reload, and use an authenticated binary client's STAT request with key `settings` for settings inspection. Retain the configured certificate paths; check reload errors and inspect the certificate on a new connection. Existing connections retain their established sessions. See the [TLS reload design](https://raw.githubusercontent.com/memcached/memcached/4b9e6198fc44c9eb3ae80802a1b0dcbaf9602969/doc/tls.txt), [1.6.45 signal handling](https://raw.githubusercontent.com/memcached/memcached/1.6.45/memcached.c), and [binary statistics implementation](https://raw.githubusercontent.com/memcached/memcached/1.6.45/proto_bin.c).

MFA: there is no login for a person, so no second factor applies; human access to the host goes behind MFA per [mfa.md](mfa.md).

## 6. Disable unnecessary cache-wide invalidation and keep shutdown disabled

If the application does not require cache-wide invalidation, add `-F`. This disables `flush_all`, reducing the risk of accidental or malicious cache eviction followed by a backend load spike. It does not prevent ordinary writes or individual deletions.

Leave `-A` absent so the ASCII `shutdown` command remains disabled. Check inherited service arguments as well as the configuration you edited.

Both controls are documented in the [1.6.45 man page](https://raw.githubusercontent.com/memcached/memcached/1.6.45/doc/memcached.1). A rejected flush still increments `cmd_flush`; that counter alone does not establish that flushing succeeded. Verify the command response and a previously readable test item. The [protocol reference](https://raw.githubusercontent.com/memcached/memcached/7278bdee96329915bbc87731ba005095453f5c2f/doc/protocol.txt) describes invalidation and shutdown; its general flush success description must be read with the `-F` restriction.

## 7. Disable key enumeration and live watch access

Cache keys and activity logs can disclose application identifiers and usage. Add `-X -W` when operations do not require key dumps or live watchers.

In 1.6.45, `-X` blocks `stats cachedump`, `stats detail`, `lru_crawler metadump`, and `lru_crawler mgdump`. The man page lists fewer commands than the implementation; do not generalize this coverage to older releases. `-W` blocks `watch`. These controls leave ordinary `stats`, `stats settings`, and reads of known keys available within the applicable protocol and authentication rules. Keep those capabilities behind the same network and authentication boundary. See the [1.6.45 command enforcement](https://raw.githubusercontent.com/memcached/memcached/1.6.45/proto_text.c).

`-W` was introduced in [1.5.21](https://github.com/memcached/memcached/wiki/ReleaseNotes1521). The flags are listed in the [1.6.45 CLI help](https://raw.githubusercontent.com/memcached/memcached/1.6.45/memcached.c).

Do not substitute `-o no_lru_crawler` for `-X`. It disables the background crawler, and protocol commands can enable the crawler again. It is a maintenance setting, not an authorization boundary. See the [crawler protocol](https://raw.githubusercontent.com/memcached/memcached/7278bdee96329915bbc87731ba005095453f5c2f/doc/protocol.txt).

## Verify

Service-level verification below is **REASONED, not demonstrated**. The authoring environment has no memcached binary, Docker, or Podman, and no available authorized service environment for reproducing these states. TLS and authentication fixtures and separate network observers are also unavailable. Expected outcomes come from the linked vendor sources; no live outcome is claimed.

Local validation ran in memory: all 11 shell blocks passed `bash -n`, ShellCheck 0.11.0, and the repository's strict guard scanner. Each of the five guarded blocks rejected six invalid values and two incomplete-assignment cases under `bash -u`; valid inputs reached instrumented probes. This tests the guards, not memcached. Memcached startup/configuration parsing remains undemonstrated.

Paste each complete block, including its parentheses, marker, and count checks. Substitute inside the single quotes on the `set --` line. Do not insert a literal apostrophe there without shell escaping. The guards assume normal shell builtins; fragments pasted below the guards are not protected.

### V1. Inspect the release, process identity, arguments, and every listener

**REASONED:** no memcached executable or service process is available here. On the service host, first ensure `memcached` resolves to the same installed executable used by the service. Supply its actual PID. Run listener inspection with enough privilege to identify the process and in its network namespace; also inspect host-side published ports for container deployments.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_MEMCACHED_PID'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "supply exactly one PID; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "replace the PID; not probing"; exit 1 ;;
    *)
      case "$1" in
        *[!0-9]*|0) echo "supply a positive numeric PID; not probing"; exit 1 ;;
        *)
          memcached -V
          memcached -h
          ps -o pid=,user=,group=,args= -p "$1"
          ss -tlnup
          ;;
      esac
      ;;
  esac
)
```

Confirm the package's security-fix status, including distribution backports; a version string alone is insufficient. Confirm `-S` and `-Z` are advertised for the SASL/TLS deployment. The running process must use the intended dedicated account.

Read every listener: TCP 11211 on loopback or the intended private address only, no memcached UDP socket, and no unexpected address-specific port or published listener. An exposed comparison has a wildcard/unintended listener or UDP enabled; a fixed comparison has only the intended listeners while an allowed client's protected operation still succeeds. Use V2 and V6 as the positive controls. The [man page](https://raw.githubusercontent.com/memcached/memcached/1.6.45/doc/memcached.1) and [DDoS advisory](https://docs.memcached.org/advisories/ddos/) define the expected configuration.

For capacity, request `stats settings` through V3's applicable text configuration, or authenticated binary STAT with key `settings` for `-S`. For the example budgets, expect `maxconns` of `256` and `maxbytes` of `268435456`; unchanged upstream defaults would report `1024` and `67108864`. Compare the actual selected budgets, not these numbers if you chose different capacities. Also inspect `tcpport`, `udpport`, `inter`, `shutdown_command`, `flush_enabled`, and `dump_enabled`. Expected restrictions are UDP `0`, shutdown `no`, flush `no`, and dumping `no`. See the [effective-settings implementation](https://raw.githubusercontent.com/memcached/memcached/1.6.45/memcached.c).

A successful application SET/GET after applying the budgets is the matched positive control. These observations establish effective settings and basic operation, not workload capacity or a total process-memory ceiling.

### V2. Pair outside denial with allowed-client success

**REASONED:** separate allowed and disallowed observers and a deployed cache are unavailable. Use the real address from the deployment inventory, not a documentation address. Run this block from both observers and record their locations and targets.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_REAL_TARGET_IP'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "supply exactly one address; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|-*|*[[:space:]]*)
      echo "replace the address; not probing"; exit 1 ;;
    *)
      if nc -vz -w 5 "$1" 11211; then
        echo "TCP connection succeeded; compare the observer and expected policy"
      else
        echo "TCP connection failed; inspect the error and matched positive control"
      fi
      ;;
  esac
)
```

On an isolated test network, the exposed comparison allows the otherwise disallowed observer to connect. After fixing the bind/firewall, that observer must receive refusal or timeout while the allowed observer can still connect and complete V6's application request. Do not create public exposure to obtain a baseline.

For loopback-only service, the positive control runs on the service host against `127.0.0.1`; the outside probe targets the host's actual non-loopback address. For a private remote-client deployment, test the actual private endpoint from both relevant network positions, and any public address or port mapping separately.

A timeout alone proves nothing about isolation: a wrong target, unavailable service, or broken route can produce it. Correlate the pair with V1's process/listener evidence and the effective firewall rules. This follows the vendor's [network isolation guidance](https://docs.memcached.org/serverguide/configuring/).

### V3. Retain the loopback text probe for its applicable configuration

**REASONED:** no loopback memcached service is available. This probe is only for the no-authentication, no-TLS loopback configuration in step 1, or an isolated test instance with that transport.

```bash
(
  set -- PASTE_WHOLE_BLOCK '127.0.0.1'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "supply exactly one address; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "replace the address; not probing"; exit 1 ;;
    *)
      [ "$1" = 127.0.0.1 ] || { echo "this probe is only for loopback; not probing"; exit 1; }
      printf 'stats\r\nquit\r\n' | nc -w 5 "$1" 11211
      printf 'stats settings\r\nquit\r\n' | nc -w 5 "$1" 11211
      ;;
  esac
)
```

Expect statistics terminated by `END` on the applicable text listener. On the combined private-address SASL/TLS deployment, this probe fails for independent reasons: nothing need listen on loopback, `-S` rejects text `stats`, and `-Z` requires TLS. That failure proves none of those controls individually. Pair it with V1's listener evidence and V6's successful authenticated request. See the [text protocol](https://raw.githubusercontent.com/memcached/memcached/7278bdee96329915bbc87731ba005095453f5c2f/doc/protocol.txt) and [binary dispatcher](https://raw.githubusercontent.com/memcached/memcached/1.6.45/proto_bin.c).

### V4. Verify TLS, certificate identity, and the existing mutual-TLS option

**REASONED:** no TLS-enabled memcached service, certificate fixture, or compatible application client is available. Provide the trusted CA as `ca.pem` and the actual server IPv4 address:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_SERVER_IPV4'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "supply exactly one address; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|-*|*[[:space:]]*)
      echo "replace the address; not probing"; exit 1 ;;
    *)
      [ -r ca.pem ] || { echo "provide the trusted CA file ca.pem; not probing"; exit 1; }
      timeout 10 openssl s_client -connect "$1:11211" -CAfile ca.pem -verify_ip "$1" \
        -verify_return_error </dev/null
      ;;
  esac
)
```

For the original `10.0.0.5` example, the certificate needs an iPAddress SAN for `10.0.0.5`. `-verify_ip` binds trust to that address. For a DNS SAN, adapt the guarded block to the actual name and use `-verify_hostname` with that name instead. Chain checks alone accept other identities signed by the same CA.

Omit `-CAfile` only for a publicly trusted certificate whose issuer is already in the system store. On that path, use `-verify_hostname` with the certificate's DNS name rather than expecting an iPAddress SAN.

A reachable plaintext comparison cannot complete this TLS handshake; the fixed TLS endpoint must complete certificate and identity verification and then support V6's application request. A bare handshake without the proper trust and identity checks establishes only that TLS is present. A timeout or missing certificate file is inconclusive.

The example matches the default server behavior, which does not require client certificates. With `-o ssl_verify_mode=2`, add `-cert` and `-key` pointing to the approved client certificate and key files. Compare a valid client certificate with an omitted certificate against the same service. Only the valid client must complete an application request. `Verification: OK` describes server-certificate verification and can still print when the server subsequently refuses the client.

For certificate reload, replace the certificate material at the configured paths, send SIGHUP through the service manager to the verified process, and repeat on a new connection. Expect the new certificate and a successful application request; retaining the old certificate or reporting a reload error is not success. See the [TLS documentation](https://docs.memcached.org/features/tls/) and [reload design](https://raw.githubusercontent.com/memcached/memcached/4b9e6198fc44c9eb3ae80802a1b0dcbaf9602969/doc/tls.txt).

### V5. Exercise flush, dump, watch, and shutdown restrictions

**REASONED:** no disposable memcached runtime is available. This block deliberately sends `flush_all` and `shutdown`. Run it only against an otherwise empty disposable loopback instance, never a live application cache.

Use the same 1.6.45 build for both comparisons, with ordinary text transport, no authentication, no TLS, default slab geometry, and the crawler running. Keep automatic service restart disabled so it cannot conceal shutdown. The exposed comparison omits `-F -X -W` and enables `-A`; the fixed comparison adds `-F -X -W` and omits `-A`. Keep network isolation and the dedicated account in both.

Replace the address with `127.0.0.1` only after confirming that this port belongs to the disposable instance:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_DISPOSABLE_LOOPBACK_IP'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "supply exactly one address; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "replace the disposable cache address; not probing"; exit 1 ;;
    *)
      [ "$1" = 127.0.0.1 ] || { echo "use the disposable loopback cache; not probing"; exit 1; }
      printf 'set sc:probe 0 300 2\r\nok\r\nget sc:probe\r\nquit\r\n' | nc -w 5 "$1" 11211
      sleep 2
      printf 'flush_all\r\nget sc:probe\r\nquit\r\n' | nc -w 5 "$1" 11211
      printf 'set sc:probe 0 300 2\r\nok\r\nstats items\r\nquit\r\n' | nc -w 5 "$1" 11211
      for request in 'stats cachedump 1 10' 'stats detail dump' \
        'lru_crawler metadump all' 'lru_crawler mgdump all' 'watch'; do
        printf 'request: %s\n' "$request"
        printf '%s\r\n' "$request" | timeout 5 nc -w 3 "$1" 11211
      done
      printf 'get sc:probe\r\ndelete sc:probe\r\nstats\r\nstats settings\r\nquit\r\n' | nc -w 5 "$1" 11211
      printf 'shutdown\r\n' | nc -w 5 "$1" 11211
      printf 'stats\r\nquit\r\n' | nc -w 5 "$1" 11211
      ;;
  esac
)
```

Read the responses, not just the block's final exit status:

| Request | Exposed comparison | Fixed comparison and positive control |
| --- | --- | --- |
| Initial SET/GET | Stores and returns `ok` | Also stores and returns `ok`; otherwise subsequent results are inconclusive |
| `flush_all`, then GET | Flush succeeds; the previously readable item is absent | Explicit flush refusal; GET still returns `ok` |
| `stats cachedump 1 10` | Command accepted, with a normal dump terminator; an empty dump alone is not denial | Explicit dumping refusal; known-key GET still works |
| `stats detail dump` | Detail dump accepted, possibly empty | Explicit detail refusal |
| `lru_crawler metadump all` and `lru_crawler mgdump all` | Successful dumps from the populated fixture | Explicit dump refusal |
| `watch` | Watcher accepted | Explicit watch refusal |
| GET, DELETE, ordinary statistics | Ordinary operations succeed | Ordinary operations still succeed |
| `shutdown`, then fresh statistics request | Process stops; subsequent connection fails | Explicit shutdown refusal; the same process still answers statistics |

The short item uses slab class 1 with the stated default geometry; inspect `stats items` before interpreting that dump. A disabled or busy crawler, malformed request, connection failure, or protocol mismatch does not prove `-X`. A watcher timeout does not prove `-W`; inspect whether the watcher was accepted or explicitly refused. The two-second pause separates item creation from immediate flush timing.

These comparisons follow the [basic command semantics](https://docs.memcached.org/protocols/basic/), [1.6.45 restrictions](https://raw.githubusercontent.com/memcached/memcached/1.6.45/proto_text.c), and [shutdown protocol](https://raw.githubusercontent.com/memcached/memcached/7278bdee96329915bbc87731ba005095453f5c2f/doc/protocol.txt). The disposable text fixture isolates these flags; it does not demonstrate the production authentication or TLS configuration.

For a binary SASL deployment, also repeat SET, GET, FLUSH, and GET through the authenticated TLS client on a disposable equivalent. Without `-F`, FLUSH invalidates the item; with `-F`, FLUSH is refused and the item remains readable. See the [binary flush implementation](https://raw.githubusercontent.com/memcached/memcached/1.6.45/proto_bin.c).

### V6. Test authentication with a protected operation

**REASONED:** no memcached service, configured authentication database, or compatible client is available. Use the deployed application's client, with credentials obtained interactively or from its protected secret configuration, never password arguments.

Seed `sc:auth-probe` with a short-lived known value through an authorized client. Use fresh connections for the following requests:

| Mode | Concrete request and exposed comparison | Fixed outcome and matched positive control |
| --- | --- | --- |
| Binary SASL | Binary GET, opcode `0x00`, key `sc:auth-probe`, without SASL authentication. A service without `-S` returns the item | With `-S`, the unauthenticated GET receives authentication-required/error status `0x20`. On a fresh connection, successful SASL authentication followed by the same GET returns the known value |
| ASCII token authentication | Text `get sc:auth-probe` without token exchange. A service without `-Y` returns the item | With `-Y`, it cannot retrieve the item before authentication. On a fresh connection, the client's fake SET token exchange succeeds, then the same GET returns the known value |

Also test an intentionally incorrect password on a fresh connection and confirm it cannot retrieve the item; retain the successful correct-credential request against the same endpoint. Keep the same TLS and client-certificate conditions across each authentication comparison so a TLS failure cannot masquerade as authentication enforcement.

Binary VERSION and SASL negotiation success are not substitutes for GET. A missing key, closed connection, or unavailable server without the matched successful request is inconclusive. See the [binary protocol](https://docs.memcached.org/protocols/binary/), [SASL status codes](https://docs.memcached.org/protocols/binarysasl/), [binary enforcement](https://raw.githubusercontent.com/memcached/memcached/1.6.45/proto_bin.c), and [ASCII token exchange](https://raw.githubusercontent.com/memcached/memcached/7278bdee96329915bbc87731ba005095453f5c2f/doc/protocol.txt).

| Backlog ID | Status | Required demonstration |
| --- | --- | --- |
| MEMCACHED-LIVE-1 | Open; REASONED, not demonstrated | Obtain an authorized memcached runtime, SASL/TLS client and certificate fixtures, and allowed/disallowed network observers. Run V1-V6 against matched exposed and fixed states; record package/build identity, service arguments, process ownership, listeners, effective budgets, requests, responses, and positive controls. Validate startup parsing and certificate reload. If optional idle timeout or privilege dropping is adopted, include its platform and application checks before claiming it effective. |

## Common mistakes

- A container or package that starts memcached without `-l`, so it listens on `INADDR_ANY` while a firewall rule is assumed but absent.
- `-S` on a distribution package built without SASL: the option is documented as meaningful only with SASL compiled in, so confirm it took effect rather than assuming.
- SASL without TLS across a shared network; the documentation is explicit that SASL adds no encryption, and PLAIN credentials need TLS.
- Changing `-p` and treating the new port as access control, or inheriting a nonzero UDP setting.
- Treating `-m` as a total process-memory limit or `-c` as a request-rate limit.
- Assuming a rejected text request proves authentication on a binary/TLS listener, or treating VERSION as a protected operation.
- Reading `cmd_flush` as proof that invalidation succeeded.
- Substituting `-o no_lru_crawler` for `-X`, or assuming `-X -W` disables ordinary statistics and known-key access.
- Adding a plaintext listener just to send text administration commands to a service configured for binary SASL.
- Calling an outside timeout a pass without confirming the real target and a successful allowed-client request.

## Sources (checked September 2026)

- memcached documentation, binary protocol SASL authentication: https://docs.memcached.org/protocols/binarysasl/
- memcached documentation, TLS: https://docs.memcached.org/features/tls/
- memcached documentation, configuring the server (`-l`, `-U`, exposure warning): https://docs.memcached.org/serverguide/configuring/
- memcached man page (`-l` default `INADDR_ANY`, `-U` default 0, `-S`): https://raw.githubusercontent.com/memcached/memcached/5d17f8f4bb068a0bdd4809e80e3ed5d378ef2fad/doc/memcached.1
- memcached protocol reference (`-Y` text protocol authentication): https://raw.githubusercontent.com/memcached/memcached/7278bdee96329915bbc87731ba005095453f5c2f/doc/protocol.txt
- memcached current stable release: https://memcached.org/
- memcached 1.6.42 security release notes: https://github.com/memcached/memcached/wiki/ReleaseNotes1642
- memcached 1.6.45 security and crash fixes: https://github.com/memcached/memcached/wiki/ReleaseNotes1645
- memcached 1.6.45 man page, network, account, resource, flush, and shutdown options: https://raw.githubusercontent.com/memcached/memcached/1.6.45/doc/memcached.1
- memcached configuration wiki, networking and resource budgets: https://github.com/memcached/memcached/wiki/ConfiguringServer
- memcached UDP reflection and amplification advisory: https://docs.memcached.org/advisories/ddos/
- memcached SASL build and setup how-to: https://github.com/memcached/memcached/wiki/SASLHowto
- memcached protocol status and binary deprecation: https://docs.memcached.org/protocols/
- memcached 1.5.15 release notes, ASCII authentication and binary idle timeout fix: https://github.com/memcached/memcached/wiki/ReleaseNotes1515
- memcached 1.5.21 release notes, watch disabling: https://github.com/memcached/memcached/wiki/ReleaseNotes1521
- memcached 1.6.45 CLI help, defaults, effective settings, and signal handling: https://raw.githubusercontent.com/memcached/memcached/1.6.45/memcached.c
- memcached 1.6.45 text command enforcement: https://raw.githubusercontent.com/memcached/memcached/1.6.45/proto_text.c
- memcached 1.6.45 binary authentication, statistics, and flush enforcement: https://raw.githubusercontent.com/memcached/memcached/1.6.45/proto_bin.c
- memcached TLS design and certificate reload: https://raw.githubusercontent.com/memcached/memcached/4b9e6198fc44c9eb3ae80802a1b0dcbaf9602969/doc/tls.txt
- memcached basic text command semantics: https://docs.memcached.org/protocols/basic/
- memcached binary requests and responses: https://docs.memcached.org/protocols/binary/
