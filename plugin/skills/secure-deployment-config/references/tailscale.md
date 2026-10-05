---
version_basis: {
  "schema": 1,
  "checked": "2026-10-05",
  "documentation_checked": "2026-09",
  "body_sha256": "5da935be3e16ec5c813b70304fd06153ce263de13728955a9222f13988d07bdd",
  "components": {
    "ts": {
      "name": "Tailscale documentation",
      "basis": "unknown",
      "sources": {
        "s8a8000573b13": "https://tailscale.com/kb/1242/tailscale-serve",
        "sbe30f8121245": "https://tailscale.com/kb/1223/funnel",
        "s42e5680f0b20": "https://tailscale.com/docs/reference/examples/acls",
        "se0f0c1dd6af5": "https://tailscale.com/kb/1312/serve",
        "se137a82d9873": "https://tailscale.com/docs/reference/syntax/policy-file#tests"
      }
    },
    "cli": {
      "name": "Tailscale CLI change",
      "basis": "v1.52",
      "sources": {
        "s8a8000573b13": "https://tailscale.com/kb/1242/tailscale-serve"
      }
    },
    "ss": {
      "name": "ss",
      "basis": "unknown",
      "sources": {
        "s8ff688d5d940": "https://manpages.ubuntu.com/manpages/noble/en/man8/ss.8.html"
      }
    },
    "curl": {
      "name": "curl option documentation",
      "basis": "7.75.0",
      "sources": {
        "sc2888bc2b75b": "https://github.com/curl/curl/blob/curl-7_75_0/docs/cmdline-opts/write-out.d#L32-L36",
        "sc6f836c27ed8": "https://github.com/curl/curl/blob/curl-7_75_0/docs/cmdline-opts/write-out.d#L48-L51",
        "sc4ff20756ddd": "https://github.com/curl/curl/blob/curl-7_75_0/docs/cmdline-opts/write-out.d#L147-L149",
        "see8bc6e3acb6": "https://github.com/curl/curl/blob/curl-7_75_0/docs/cmdline-opts/head.d#L7-L9",
        "sb0b300176c5d": "https://github.com/curl/curl/blob/curl-7_75_0/docs/cmdline-opts/disable.d#L6-L8",
        "s72e21eeff9a4": "https://github.com/curl/curl/blob/curl-7_75_0/docs/cmdline-opts/connect-timeout.d#L7-L10",
        "s3b94eb9a9c12": "https://github.com/curl/curl/blob/curl-7_75_0/docs/cmdline-opts/max-time.d#L8-L12"
      }
    }
  },
  "claims": {
    "serve": {"text": "tailscale serve --bg localhost:3000 proxies to the app for tailnet devices, subject to identity and tailnet policy.", "components": ["ts"], "sources": ["ts:s8a8000573b13"], "status": "REASONED"},
    "policy-default": {"text": "New tailnets allow all devices, plus node-share recipients; remove allow-all before granting intended users, groups or tags access to the Serve port.", "components": ["ts"], "sources": ["ts:s42e5680f0b20"], "status": "REASONED"},
    "policy-additive": {"text": "Rules are additive accepts; a narrower rule cannot revoke allow-all. Grants are preferred and ACLs remain supported.", "components": ["ts"], "sources": ["ts:s42e5680f0b20"], "status": "REASONED"},
    "app-auth": {"text": "Tailnet reach is not app authorization; the app needs login or deliberate use of Serve identity headers.", "components": ["ts"], "sources": ["ts:se0f0c1dd6af5"], "status": "REASONED"},
    "header-trust": {"text": "Loopback limits identity-header spoofing to local processes; trusting Serve headers requires trusting every process on that host.", "components": ["ts"], "sources": ["ts:se0f0c1dd6af5"], "status": "REASONED"},
    "tagged": {"text": "Tagged devices carry no user identity; reject them or supply another authentication method.", "components": ["ts"], "sources": ["ts:se0f0c1dd6af5"], "status": "REASONED"},
    "bind": {"text": "Serve does not change the app bind; use 127.0.0.1:3000 because a wildcard app still answers directly on LAN/VPC addresses.", "components": ["ts"], "sources": ["ts:s8a8000573b13", "ts:se0f0c1dd6af5"], "status": "REASONED"},
    "serve-tls": {"text": "Serve automatically provisions HTTPS certificates for the machine's tailnet name.", "components": ["ts"], "sources": ["ts:s8a8000573b13"], "status": "REASONED"},
    "background": {"text": "--bg persists Serve in the background; without it the share ends with the session.", "components": ["ts"], "sources": ["ts:s8a8000573b13"], "status": "REASONED"},
    "funnel": {"text": "tailscale funnel 3000 publishes the service to the internet at its ts.net hostname with TLS.", "components": ["ts"], "sources": ["ts:sbe30f8121245"], "status": "REASONED"},
    "funnel-auth": {"text": "Funnel adds no per-request authentication and its relay does not decrypt traffic; the app needs login and human MFA.", "components": ["ts"], "sources": ["ts:sbe30f8121245"], "status": "REASONED"},
    "funnel-prerequisites": {"text": "Funnel requires tailnet HTTPS certificates, a funnel node attribute and MagicDNS.", "components": ["ts"], "sources": ["ts:sbe30f8121245"], "status": "REASONED"},
    "syntax": {"text": "Serve/Funnel command syntax changed in v1.52; older clients need their own --help.", "components": ["cli"], "sources": ["cli:s8a8000573b13"], "status": "REASONED"},
    "verify-bind": {"text": "ss sport=:3000 must show 127.0.0.1:3000, not IPv4 or IPv6 wildcard.", "components": ["ss", "ts"], "sources": ["ss:s8ff688d5d940", "ts:se0f0c1dd6af5"], "status": "REASONED", "verify": [1]},
    "verify-direct": {"text": "Probe from outside the host on the LAN/VPC: any HTTP reply proves bypass; failure alone does not prove loopback binding.", "components": ["ts", "curl"], "sources": ["ts:s8a8000573b13", "ts:se0f0c1dd6af5", "curl:sc2888bc2b75b", "curl:sc6f836c27ed8", "curl:sc4ff20756ddd", "curl:see8bc6e3acb6", "curl:sb0b300176c5d", "curl:s72e21eeff9a4", "curl:s3b94eb9a9c12"], "status": "REASONED", "verify": [2]},
    "verify-allowed": {"text": "Serve status and an allowed-device request check the intended path; success occurs under both allow-all and scoped policy.", "components": ["ts", "curl"], "sources": ["ts:s8a8000573b13", "ts:s42e5680f0b20", "curl:see8bc6e3acb6", "curl:sb0b300176c5d"], "status": "REASONED", "verify": [3]},
    "verify-policy": {"text": "Policy tests must accept the intended identity and deny an excluded one; failed assertions reject the policy file.", "components": ["ts"], "sources": ["ts:se137a82d9873"], "status": "REASONED"},
    "verify-public": {"text": "From a non-tailnet network Serve is unreachable and Funnel reachable; the funneled app must authenticate every request.", "components": ["ts"], "sources": ["ts:s8a8000573b13", "ts:sbe30f8121245"], "status": "REASONED"}
  }
}
---
# Tailscale: serve and funnel

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-05; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| serve: tailscale serve --bg localhost:3000 proxies to the app for tailnet devices, subject to identity and tailnet policy. | Tailscale documentation unknown | REASONED |
| policy-default: New tailnets allow all devices, plus node-share recipients; remove allow-all before granting intended users, groups or tags access to the Serve port. | Tailscale documentation unknown | REASONED |
| policy-additive: Rules are additive accepts; a narrower rule cannot revoke allow-all. Grants are preferred and ACLs remain supported. | Tailscale documentation unknown | REASONED |
| app-auth: Tailnet reach is not app authorization; the app needs login or deliberate use of Serve identity headers. | Tailscale documentation unknown | REASONED |
| header-trust: Loopback limits identity-header spoofing to local processes; trusting Serve headers requires trusting every process on that host. | Tailscale documentation unknown | REASONED |
| tagged: Tagged devices carry no user identity; reject them or supply another authentication method. | Tailscale documentation unknown | REASONED |
| bind: Serve does not change the app bind; use 127.0.0.1:3000 because a wildcard app still answers directly on LAN/VPC addresses. | Tailscale documentation unknown | REASONED |
| serve-tls: Serve automatically provisions HTTPS certificates for the machine's tailnet name. | Tailscale documentation unknown | REASONED |
| background: --bg persists Serve in the background; without it the share ends with the session. | Tailscale documentation unknown | REASONED |
| funnel: tailscale funnel 3000 publishes the service to the internet at its ts.net hostname with TLS. | Tailscale documentation unknown | REASONED |
| funnel-auth: Funnel adds no per-request authentication and its relay does not decrypt traffic; the app needs login and human MFA. | Tailscale documentation unknown | REASONED |
| funnel-prerequisites: Funnel requires tailnet HTTPS certificates, a funnel node attribute and MagicDNS. | Tailscale documentation unknown | REASONED |
| syntax: Serve/Funnel command syntax changed in v1.52; older clients need their own --help. | Tailscale CLI change v1.52 | REASONED |
| verify-bind: ss sport=:3000 must show 127.0.0.1:3000, not IPv4 or IPv6 wildcard. | ss unknown; Tailscale documentation unknown | REASONED |
| verify-direct: Probe from outside the host on the LAN/VPC: any HTTP reply proves bypass; failure alone does not prove loopback binding. | Tailscale documentation unknown; curl option documentation 7.75.0 | REASONED |
| verify-allowed: Serve status and an allowed-device request check the intended path; success occurs under both allow-all and scoped policy. | Tailscale documentation unknown; curl option documentation 7.75.0 | REASONED |
| verify-policy: Policy tests must accept the intended identity and deny an excluded one; failed assertions reject the policy file. | Tailscale documentation unknown | REASONED |
| verify-public: From a non-tailnet network Serve is unreachable and Funnel reachable; the funneled app must authenticate every request. | Tailscale documentation unknown | REASONED |
<!-- version-basis:end -->

Tailscale gives the same no-open-inbound-ports posture as [cloudflare.md](cloudflare.md), built on WireGuard with device identity as the access control. Two commands matter, and they differ in exactly one thing: who can reach the service.

## 1. tailscale serve: tailnet-only (authenticated by membership)

```bash
tailscale serve --bg localhost:3000
```

- Traffic **through this proxy** is reachable only by devices in your tailnet, so that path is authenticated by device identity and your tailnet ACLs. `serve` does not change how the application binds, though: an application still listening on `0.0.0.0:3000` keeps answering its LAN or VPC address directly, past the tailnet.
- That reach is only as tight as your tailnet policy. A new tailnet's default policy lets every device in the tailnet (`action` accept, `src` `*`, `dst` `*:*`), plus anyone you have shared the node with, connect to this service. Restrict it by removing the default allow-all rule and granting only the intended users, groups, or tags to this host and the port `serve` listens on (a grant is preferred; ACLs remain supported); adding a narrower rule alongside allow-all does not revoke it, because Tailscale rules are additive accepts.
- Tailnet reach is network access, not application authorization: an admin panel behind `serve` must still authenticate and authorize its own users, through its own login or by deliberately consuming the identity headers `serve` forwards. Trusting those headers is safe only where you trust every process on the Serve host: binding the app to loopback (next bullet) stops other machines, but any local process can still reach `127.0.0.1:3000` and forge them (Tailscale notes that binding to localhost limits tampering to other services on the Serve device, it does not eliminate it). Requests from tagged devices carry no user identity, so give those another method or reject them.
- Bind the fronted application to `127.0.0.1:3000` so no other machine can reach it directly; local processes on the host still can, per the identity-header caveat above.
- HTTPS uses an automatically provisioned TLS certificate for the machine's tailnet name.
- `--bg` keeps it running in the background; without it, the share stops with the session.

This is the right default for admin panels, dashboards, Jupyter, and internal tools: no certificate work, no public exposure at all.

## 2. tailscale funnel: public internet (bring your own auth)

```bash
tailscale funnel 3000
```

- Publishes the service to the entire internet at your `*.ts.net` hostname, TLS included.
- Funnel itself adds **no per-request authentication**; the relay does not even decrypt your traffic. Anything funneled needs application-level login per [authentication.md](authentication.md) and, for human logins, [mfa.md](mfa.md), exactly as if it sat behind any public proxy.
- Prerequisites per the docs: HTTPS certificates enabled for the tailnet, a `funnel` node attribute in the tailnet policy file, and MagicDNS.

## 3. Choosing between them

Serve for anything private (most things). Funnel or [cloudflare.md](cloudflare.md) for genuinely public services; Cloudflare Access adds managed login in front, which funnel does not, so prefer Access when the public service is for a defined set of people. Command syntax changed in Tailscale v1.52; on older clients consult `tailscale serve --help`.

## 4. Verify

REASONED: following block; the cited ss filter reference and Serve backend-isolation guidance define the loopback check. This read-only review cannot configure a Serve host; the guide records no listener observation.

```bash
ss -tlnp 'sport = :3000'                          # ss's own filter, not a grep: the address column
                                                  # must read 127.0.0.1:3000, never 0.0.0.0:3000 or [::]:3000
```

From another machine on the same LAN or VPC (run this from OUTSIDE the host), confirm the app does not answer its direct address:

REASONED: following block; direct-backend isolation follows the cited Serve identity-header guidance. This read-only review cannot provision a Serve host and separate LAN/VPC probe machine; HTTP replies expose bypass and failed requests remain inconclusive as described below.

```bash
(                                       # a subshell, so your own shell keeps its positional parameters and the guard's exit does not close it
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_THE_HOST_LAN_OR_VPC_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the host's LAN or VPC address on the set -- line above; not probing" ;;
    *) curl -q -g -sI -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 \
         -w 'http=%{http_code} time_connect=%{time_connect} exit=%{exitcode} err=%{errormsg}\n' "http://$1:3000/" ;;
  esac
)
# Any HTTP reply (including 4xx/5xx) proves the app is reachable past the tailnet at that address. A failed request does not by itself prove a loopback bind (a firewall, a wrong address, or a stalled response fails the same way), so read `err`/`exitcode` and rely on the `ss` line above for the actual bind address.
```

Then confirm the tailnet path works and that the section-1 restriction actually holds:

REASONED: following block; Serve status and allowed-device access follow the cited Serve CLI and policy-test documentation. This read-only review cannot configure a tailnet with allowed and excluded devices; success alone does not prove policy restriction.

```bash
tailscale serve status
curl -q -sI https://host.tailnet.ts.net/            # from an ALLOWED tailnet device: works
```

An allowed device connects under both the default allow-all policy and a correctly scoped one, so a request that works here does not prove the section-1 restriction took hold. Assert it in the tailnet policy file's `tests` (an `accept` from the intended identity to this host and port, and a `deny` from an excluded tailnet identity); Tailscale rejects a policy file whose `tests` fail. From a non-tailnet network the serve URL is unreachable while a funnel URL is reachable, so a funneled app must gate every request with its own login.

## Sources (checked September 2026)

- Tailscale serve (CLI syntax changed in v1.52): https://tailscale.com/kb/1242/tailscale-serve
- Tailscale funnel: https://tailscale.com/kb/1223/funnel
- Tailscale ACL policy examples, for the default allow-all policy (`action` accept, `src` `*`, `dst` `*:*`) and scoping access from a source to a destination: https://tailscale.com/docs/reference/examples/acls
- Tailscale serve identity headers, that binding the backend to localhost limits tampering to other services on the Serve device (it does not authenticate the calling process): https://tailscale.com/kb/1312/serve
- Tailscale policy-file `tests`, that a policy file whose assertions fail is rejected: https://tailscale.com/docs/reference/syntax/policy-file#tests
- ss(8), the `sport` filter expression used above: https://manpages.ubuntu.com/manpages/noble/en/man8/ss.8.html
- curl 7.75.0 write-out errormsg and exitcode (pinned tag curl-7_75_0, checked October 2026): https://github.com/curl/curl/blob/curl-7_75_0/docs/cmdline-opts/write-out.d#L32-L36
- curl 7.75.0 write-out http_code (pinned tag curl-7_75_0, checked October 2026): https://github.com/curl/curl/blob/curl-7_75_0/docs/cmdline-opts/write-out.d#L48-L51
- curl 7.75.0 write-out time_connect (pinned tag curl-7_75_0, checked October 2026): https://github.com/curl/curl/blob/curl-7_75_0/docs/cmdline-opts/write-out.d#L147-L149
- curl 7.75.0 HEAD requests (pinned tag curl-7_75_0, checked October 2026): https://github.com/curl/curl/blob/curl-7_75_0/docs/cmdline-opts/head.d#L7-L9
- curl 7.75.0 first-argument configuration disabling (pinned tag curl-7_75_0, checked October 2026): https://github.com/curl/curl/blob/curl-7_75_0/docs/cmdline-opts/disable.d#L6-L8
- curl 7.75.0 connection timeout (pinned tag curl-7_75_0, checked October 2026): https://github.com/curl/curl/blob/curl-7_75_0/docs/cmdline-opts/connect-timeout.d#L7-L10
- curl 7.75.0 total timeout (pinned tag curl-7_75_0, checked October 2026): https://github.com/curl/curl/blob/curl-7_75_0/docs/cmdline-opts/max-time.d#L8-L12
