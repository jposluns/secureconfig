# Egress control and cloud metadata: keeping an agent from exfiltrating credentials

Cloud metadata services are built-in addresses where a cloud server reads its settings and temporary credentials. This guide helps your AI assistant make misdirected requests to them fail, including IMDSv2 with a hop limit of 1 on AWS, the addresses blocked inside workloads not needing them, and default-deny egress.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/egress-metadata.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against AWS metadata and networking (no recorded version), Azure IMDS API 2025-04-07, iptables owner match v1.8.13, and nftables packet filtering v1.1.7; 1 further source is pinned to a commit and 5 carry no recorded version. Metadata reviewed 2026-10-18; documentation checked September 2026. The guide records 27 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

An AI agent, RAG fetcher, or webhook handler that retrieves URLs can be steered by a prompt injection into requesting the cloud metadata endpoint or an internal service instead of the URL it was meant to fetch. Making the fetcher refuse that request is application security; this guide covers the deployment-side backstop, metadata hardening so the endpoint rejects an unqualified request, plus default-deny egress so the request never leaves the workload at all.

## AWS: require IMDSv2 and cap the hop limit

The instance metadata service listens on `169.254.169.254`, and on Nitro instances in an IPv6-enabled subnet also on `[fd00:ec2::254]` (IMDSv2-compatible); block or verify-disabled BOTH, since an IPv4-only control misses the IPv6 path. IMDSv2 requires a session token obtained with a
`PUT` before any `GET` succeeds. The response to that `PUT`, the token itself, has a hop limit at the IP
protocol level (1 on many launches, but launch parameters, account/Region settings, and the IMDSv2-only
`ImdsSupport: v2.0` AMI setting can make it 2, so set it explicitly below rather than assuming). The token
cannot travel more than one network hop back to the requester at hop limit 1 (per
the AWS instance metadata service documentation). A containerized application sitting one hop from the
host, for example behind the container network's own routing, will not receive the token and so cannot
complete an IMDSv2 request; this is a limit on the token response reaching that far, not a guarantee that no
proxy anywhere can reach the metadata service itself. Enforce IMDSv2 and keep the hop limit at 1:

```bash
aws ec2 modify-instance-metadata-options \
  --instance-id i-0123456789abcdef0 \
  --http-tokens required \
  --http-put-response-hop-limit 1 \
  --http-endpoint enabled
```

This command does not touch `--http-protocol-ipv6`, so it stays at its current value; AWS keeps IPv6 IMDS disabled unless you enable it explicitly, so the safest stance is to leave it off (one fewer endpoint to defend). If a workload needs IPv6 IMDS, enable it deliberately and then block and probe `[fd00:ec2::254]` alongside the IPv4 address; `describe-instances` reports the state as `HttpProtocolIpv6`.

With `--http-tokens required`, a request without a valid token receives a 401 from the service itself.

## GCP and Azure: a required header, but block the address anyway

GCP's metadata server answers at `metadata.google.internal` or `169.254.169.254` and requires a `Metadata-Flavor: Google` header on every request; Google states the request and response never leave the physical host. Azure's Instance Metadata Service listens at the same non-routable address, `169.254.169.254`, reachable only from within the VM, and requires a `Metadata: true` header, rejecting any request that also carries an `X-Forwarded-For` header. Both header checks stop a naive `curl`, but neither stops a fetch that has been steered into adding the header, so block `169.254.169.254` (and the IPv6 metadata addresses where enabled: AWS `[fd00:ec2::254]`, GCP `[fd20:ce::254]` on IPv6-only instances) from workloads that have no legitimate reason to reach it, the same as any other internal address. Note this must be a workload/guest control (host firewall, CNI, or an egress proxy): like AWS security groups, GCP VPC and hierarchical firewall rules do not filter traffic to the metadata server, so a cloud-firewall rule alone will not block it. Scope any guest block carefully, since this address can also serve DNS.

## Default-deny egress

- **Cloud firewall / security group egress rules** (the inbound side of the same tools is in
  [cloud-firewalls.md](cloud-firewalls.md)): AWS security groups and Google Cloud VPC firewalls
  start with broad outbound allowances; Azure NSGs include outbound allow rules. At the time of
  writing, the fetched Azure page says subnets in new virtual networks created with API versions
  released after March 31, 2026, and through the portal default to private; existing virtual networks
  are unchanged. Those private subnets need explicit outbound connectivity to public endpoints.
  As this guide recommends, permit only DNS and the specific
  provider APIs the application calls. On AWS a security group is
  allow-only (it has no deny rules), so you must REMOVE its default allow-all egress rule and add narrow
  allows, and account for every other security group attached to the instance; a network ACL, which does
  support deny rules, is the subnet-level complement; its rules are stateless. AWS security groups do not
  filter traffic to or from
  the instance metadata address `169.254.169.254` (per the security groups documentation); they are not a
  backstop for metadata access.
  Keep egress rules for every other destination, and rely on IMDSv2, the hop limit, and disabling the
  metadata endpoint where it is unused to control reachability of the metadata service itself.
- **Kubernetes NetworkPolicy egress**: a pod is unrestricted for egress until a `NetworkPolicy` with `Egress`
  in its `policyTypes` selects it, after which only listed destinations are reachable. Policies are ADDITIVE,
  so a second policy selecting the same pod can re-permit the metadata address; audit every policy that
  selects the workload, not just this one. Behaviour for `hostNetwork` pods is undefined, and it has no
  effect at all unless the cluster's network plugin (CNI) implements `NetworkPolicy`; confirm enforcement
  before relying on it.

  ```yaml
  apiVersion: networking.k8s.io/v1
  kind: NetworkPolicy
  metadata:
    name: agent-egress
  spec:
    podSelector: {matchLabels: {app: agent}}
    policyTypes: [Egress]
    egress:
      # DNS, or every hostname-based egress in the pod fails once this policy selects it:
      - to: [{namespaceSelector: {matchLabels: {kubernetes.io/metadata.name: kube-system}}, podSelector: {matchLabels: {k8s-app: kube-dns}}}]
        ports: [{protocol: UDP, port: 53}, {protocol: TCP, port: 53}]
      # the API destinations the app actually needs (203.0.113.0/24 is a placeholder - replace it):
      - to: [{ipBlock: {cidr: 203.0.113.0/24}}]
        ports: [{protocol: TCP, port: 443}]
  ```
- **Docker network isolation**: an internal network has no default route out, and Docker's own firewall
  rules drop traffic leaving it, while containers on the network still reach each other:
  `docker network create --internal agent-net`.
- **Host-process restriction**: IMDSv2 with hop limit 1 still lets a process ON the host obtain its own
  token, so on a host that runs the agent directly (not in a container one hop away) restrict the metadata
  address by user, as this guide recommends, with an `iptables` `OUTPUT` owner match, e.g. `iptables -A OUTPUT -d 169.254.169.254 -m owner ! --uid-owner aws -j DROP` (adapt the allowed uid). The `iptables` `OUTPUT` owner match does not cover traffic forwarded from a container, an nftables equivalent must be in a base chain hooked at the output path, or in a regular chain reached from that base chain by a jump, and you need the matching `ip6tables` rule for `[fd00:ec2::254]` where IPv6 IMDS is enabled. A forward proxy with a destination allowlist only enforces on traffic that actually passes through it, so it is not a substitute for a network block: pair it with a rule that stops the workload reaching metadata directly, or the workload just bypasses the proxy, and test the proxy path separately.

## Scope boundary

Steering a fetcher into requesting the metadata address or an internal host is server-side request forgery,
an application-security defect belonging to the code doing the fetching, not to this guide. IMDSv2, the
header requirements above, and egress rules are deployment-side controls: they do not prevent the request
from being attempted, they make the attempt fail.

## Verify

REASONED: exit statuses and run locations, from the blocks below as written; no exposed/fixed run is recorded in this guide. Each block below is pasted whole and runs in one subshell, so one exit status covers every check in it: 0 for a pass, or for an observation the block cannot classify and says so; 1 for a finding; 2 when a guard refuses the block's input; and 3 for a failed or inconclusive check, a finding outranking an inconclusive result. Run the metadata blocks for your own cloud on the workload, the egress controls on the same workload, and the metadata-options check wherever your AWS CLI has credentials.

REASONED: metadata headers, token flow, network blocks, egress controls and applied options; no exposed/fixed run is recorded in this guide. Expectations follow the cited cloud, NetworkPolicy and curl sources; the authoring environment has no authorized cloud VM or workload enforcement point.

```bash
# --noproxy so an ambient http(s)_proxy/ALL_PROXY cannot answer in place of the metadata service (Azure
# documents that IMDS queries must bypass proxies); timeouts so a blocked address does not hang.
# AWS, on the workload. This tests the header requirement, which is not the control this guide
# recommends; the next block tests the network block itself.
(                                       # a subshell, so the exits below end only this check
  set +e                                # errexit off here, so a request that fails is classified below instead of ending the block
  # AWS, no token supplied: with --http-tokens required this returns 401
  set -- "$(if curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "${1##*$'\n'}" "${1%%$'\n'*}"  # curl's exit status, then the HTTP code
  printf '%s\n' "$2"
  case "$1:$2" in
    0:401) echo "block exit 0; the tokenless request got 401, so tokens are required"; exit 0 ;;
    0:2??) echo "FINDING: the tokenless request got $2, so the instance answers without an IMDSv2 token"; exit 1 ;;
    0:*) echo "HTTP $2 is neither the 401 pass nor a 2xx finding; inconclusive"; exit 3 ;;
    7:*|28:*) echo "block exit 0; curl exit $1, no answer, so the header requirement was not tested from here: the next block classifies reachability"; exit 0 ;;
    *) echo "curl exit $1: the tokenless request failed; inconclusive"; exit 3 ;;
  esac
)
```

REASONED: following block; metadata reachability and what each provider's probed path returns, per the cited AWS instance metadata, GCP metadata and Azure Instance Metadata Service documentation; no exposed/fixed run is recorded. In the network blocks below, a 200, or any HTTP response including a 401, means the metadata endpoint is reachable from the workload, whatever the header checks returned. Reachability is the finding. GCP's probed path returns a live access token (credential issuance). AWS's `/latest/meta-data/iam/security-credentials/` lists the attached role NAMES (append a role name to fetch the actual credentials), and the token PUT issues an IMDS session token, not IAM credentials, so treat the AWS checks as metadata reachability, not credential issuance. Azure's `/metadata/instance` likewise proves reachability only, its managed-identity token being a separate `/metadata/identity/oauth2/token` request.

REASONED: following block; reading a failed probe and running the positive control, per the cited curl manual and AWS VPC Flow Logs limitations page; no exposed/fixed run is recorded. `http=000` on its own is not proof of a block: an endpoint that accepts the connection and then stalls produces it too. Read `time_connect`, which stays 0.000000 only when no connection completed, and corroborate with an enforcement-point deny record for THIS flow: a CNI NetworkPolicy drop counter or log, a host iptables or nftables DROP counter, or a packet capture. AWS VPC Flow Logs EXCLUDE traffic to and from 169.254.169.254, so they cannot corroborate a metadata block (they are fine for the other egress destinations in the negative control below). Run the network blocks BEFORE applying the block too (the positive control): they should reach metadata then, so a later refusal is the block working, not the endpoint being down.

```bash
# REASONED: the AWS IMDSv2 token flow and metadata reachability, per the cited AWS instance metadata
# documentation and curl manual; no exposed/fixed run is recorded.
# AWS, on a workload that has no legitimate reason to reach metadata. A tokenless 401 proves the
# header requirement, not a network block, so this does the real IMDSv2 two-step: PUT a token, then
# GET WITH it.
#   Assumes a clean Bash shell with trusted startup files.
#   Tokens stay in positional parameters and curl's stdin, not named variables, environment or argv.
#   The same account and root can still read process memory; this does not erase earlier exports.
#   Stdin closes the argv channel only. No token is typed, and each subshell turns set -x tracing off
#   before it fetches a token, so shell history and set -x tracing do not record it.
# This block cannot exit 0. A token issued over either address family is the finding (1). A failed
# PUT, which is what a working block produces, is inconclusive (3) until an enforcement-point deny
# record for this flow corroborates it.
(                                       # the whole block in one subshell, so one exit status covers every part of it
  set +e                                # errexit off here, so a part that ends nonzero is folded into the status below instead of ending the block
  set -- 0                              # the block's status so far: 1 (a finding) outranks 3 (inconclusive), which outranks 0
  (
    trap - DEBUG RETURN ERR
    set +x +a +e
    # Append curl's status after a newline, then split it from the response without a named variable.
    set -- "$(if curl -q -g -sf --noproxy '*' --connect-timeout 5 --max-time 5 -X PUT -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' http://169.254.169.254/latest/api/token; then printf '\n0'; else printf '\n%s' "$?"; fi)"
    set -- "${1%$'\n'*}" "${1##*$'\n'}"
    printf 'PUT exit: %s\n' "$2"
    [ "$2" = 0 ] || { echo 'no usable token: PUT failed; inconclusive without an enforcement-point deny record'; exit 3; }
    case "$1" in ''|*[[:cntrl:]]*) echo 'empty or malformed token; inconclusive'; exit 3 ;; esac
    printf 'X-aws-ec2-metadata-token: %s\n' "$1" | curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 -w 'aws=%{http_code} time_connect=%{time_connect}\n' -H @- http://169.254.169.254/latest/meta-data/iam/security-credentials/
    echo "FINDING: the metadata service issued a session token to this workload over IPv4, so it is reachable from here"
    exit 1
  )
  case "$?:$1" in 0:*) ;; 1:*) set -- 1 ;; *:1) ;; *) set -- 3 ;; esac   # fold that part's status into the block's, ranked as above
  # Where IPv6 IMDS is enabled, the WHOLE probe is repeated over IPv6 (do not reuse the IPv4 token:
  # acquire one over IPv6 too, since IPv4 may be blocked while IPv6 is not). Where it is disabled,
  # this PUT fails and reports inconclusive. The bracketed literal is quoted, -q first then -g.
  (
    trap - DEBUG RETURN ERR
    set +x +a +e
    set -- "$(if curl -q -g -sf --noproxy '*' --connect-timeout 5 --max-time 5 -X PUT -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' 'http://[fd00:ec2::254]/latest/api/token'; then printf '\n0'; else printf '\n%s' "$?"; fi)"
    set -- "${1%$'\n'*}" "${1##*$'\n'}"
    printf 'PUT6 exit: %s\n' "$2"
    [ "$2" = 0 ] || { echo 'no usable IPv6 token: PUT failed; inconclusive without an enforcement-point deny record'; exit 3; }
    case "$1" in ''|*[[:cntrl:]]*) echo 'empty or malformed IPv6 token; inconclusive'; exit 3 ;; esac
    printf 'X-aws-ec2-metadata-token: %s\n' "$1" | curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 -w 'aws6=%{http_code} time_connect=%{time_connect}\n' -H @- 'http://[fd00:ec2::254]/latest/meta-data/'
    echo "FINDING: the metadata service issued a session token to this workload over IPv6, so it is reachable from here"
    exit 1
  )
  case "$?:$1" in 0:*) ;; 1:*) set -- 1 ;; *:1) ;; *) set -- 3 ;; esac   # fold that part's status into the block's, ranked as above
  echo "block exit $1; the GET lines above are printed for reading, and a 3 needs the deny record before you read it as a block"
  exit "$1"
)
```

```bash
# REASONED: the GCP header requirement and metadata reachability, per the cited GCP metadata
# documentation and curl manual; no exposed/fixed run is recorded.
# GCP, on a workload that has no legitimate reason to reach metadata.
(                                       # the whole block in one subshell, so one exit status covers every part of it
  set +e                                # errexit off here, so a request that fails is classified below instead of ending the block
  set -- 0                              # the block's status so far: 1 (a finding) outranks 3 (inconclusive), which outranks 0
  # GCP, no Metadata-Flavor header: must fail, must not return metadata. This tests the header
  # requirement, which is not the control this guide recommends.
  set -- "$1" "$(if curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 -w '%{http_code}\n' http://169.254.169.254/computeMetadata/v1/instance/; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "${2##*$'\n'}" "${2%%$'\n'*}"   # status, curl's exit status, then the HTTP code
  printf '%s\n' "$3"
  case "$2:$3" in
    0:2??) echo "FINDING: the request without the header got $3, so it returned metadata"; set -- 1 ;;
    0:*|7:*|28:*) ;;                    # refused or unanswered: the request failed, as it must
    *) echo "curl exit $2: the request without the header failed for another reason; inconclusive"; [ "$1" = 1 ] || set -- 3 ;;
  esac
  # The network block itself, WITH the header the service requires (send the required header).
  set -- "$1" "$(if curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 \
    -w 'gcp=%{http_code} time_connect=%{time_connect}\n' -H 'Metadata-Flavor: Google' \
    http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "${2##*$'\n'}" "${2%%$'\n'*}"   # status, curl's exit status, then the gcp= line
  printf '%s\n' "$3"
  case "$2:$3" in
    0:*) echo "FINDING: the metadata endpoint answered the request with the header, so it is reachable from this workload"; set -- 1 ;;
    7:*time_connect=0.000000|28:*time_connect=0.000000) echo "curl exit $2 and no connection completed: consistent with a block; confirm it with an enforcement-point deny record for this flow" ;;
    *) echo "curl exit $2 is not proof of a block, because a connection completed or the request failed for another reason; inconclusive"; [ "$1" = 1 ] || set -- 3 ;;
  esac
  # IPv6-only GCP instances also answer at [fd20:ce::254]; elsewhere this request finds no route,
  # which reads the same as a block. The bracketed literal is quoted, -q first then -g.
  set -- "$1" "$(if curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 -w 'gcp6=%{http_code} time_connect=%{time_connect}\n' -H 'Metadata-Flavor: Google' 'http://[fd20:ce::254]/computeMetadata/v1/instance/'; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "${2##*$'\n'}" "${2%%$'\n'*}"   # status, curl's exit status, then the gcp6= line
  printf '%s\n' "$3"
  case "$2:$3" in
    0:*) echo "FINDING: the IPv6 metadata endpoint answered the request with the header, so it is reachable from this workload"; set -- 1 ;;
    7:*time_connect=0.000000|28:*time_connect=0.000000) echo "curl exit $2 and no connection completed over IPv6: consistent with a block or with no IPv6 metadata address; confirm which" ;;
    *) echo "curl exit $2 over IPv6 is not proof of a block, because a connection completed or the request failed for another reason; inconclusive"; [ "$1" = 1 ] || set -- 3 ;;
  esac
  echo "block exit $1; a 0 still needs the enforcement-point deny record described above before you read it as a block"
  exit "$1"
)
```

```bash
# REASONED: the Azure header requirement and metadata reachability, per the cited Azure Instance
# Metadata Service documentation and curl manual; no exposed/fixed run is recorded.
# Azure, on a workload that has no legitimate reason to reach metadata.
(                                       # the whole block in one subshell, so one exit status covers every part of it
  set +e                                # errexit off here, so a request that fails is classified below instead of ending the block
  set -- 0                              # the block's status so far: 1 (a finding) outranks 3 (inconclusive), which outranks 0
  # Azure, no Metadata: true header: must fail, must not return metadata. This tests the header
  # requirement, which is not the control this guide recommends.
  set -- "$1" "$(if curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 -w '%{http_code}\n' 'http://169.254.169.254/metadata/instance?api-version=2025-04-07'; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "${2##*$'\n'}" "${2%%$'\n'*}"   # status, curl's exit status, then the HTTP code
  printf '%s\n' "$3"
  case "$2:$3" in
    0:2??) echo "FINDING: the request without the header got $3, so it returned metadata"; set -- 1 ;;
    0:*|7:*|28:*) ;;                    # refused or unanswered: the request failed, as it must
    *) echo "curl exit $2: the request without the header failed for another reason; inconclusive"; [ "$1" = 1 ] || set -- 3 ;;
  esac
  # The network block itself, WITH the header the service requires (send Metadata: true).
  set -- "$1" "$(if curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 \
    -w 'azure=%{http_code} time_connect=%{time_connect}\n' -H 'Metadata: true' \
    'http://169.254.169.254/metadata/instance?api-version=2025-04-07'; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "${2##*$'\n'}" "${2%%$'\n'*}"   # status, curl's exit status, then the azure= line
  printf '%s\n' "$3"
  case "$2:$3" in
    0:*) echo "FINDING: the metadata endpoint answered the request with the header, so it is reachable from this workload"; set -- 1 ;;
    7:*time_connect=0.000000|28:*time_connect=0.000000) echo "curl exit $2 and no connection completed: consistent with a block; confirm it with an enforcement-point deny record for this flow" ;;
    *) echo "curl exit $2 is not proof of a block, because a connection completed or the request failed for another reason; inconclusive"; [ "$1" = 1 ] || set -- 3 ;;
  esac
  echo "block exit $1; a 0 still needs the enforcement-point deny record described above before you read it as a block"
  exit "$1"
)
```

```bash
# REASONED: the egress allow and deny controls, per the cited curl manual and AWS STS pages; no
# exposed/fixed run is recorded.
# positive control: use any host on this workload's egress allow list; the AWS STS global endpoint
# is one example when allowed. If it is not allowed, substitute an allowed URL, such as a Regional
# STS endpoint, inside the single quotes on the set -- line.
# The fetched STS pages document the global endpoint and authentication errors, but do not state
# the response to this bare unauthenticated GET. Receiving an HTTP response is this guide's REASONED
# expectation; the exact status and body of the bare unauthenticated GET are unknown. A 000 response
# fails this control. --noproxy '*' on these two controls tests DIRECT egress (a network rule),
# not a forward proxy's allow list; where a proxy is the egress control, test through it separately.
(                                       # the whole block in one subshell, so one exit status covers every part of it
  set +e                                # errexit off here, so a part that ends nonzero is folded into the status below instead of ending the block
  set -- 0                              # the block's status so far: 1 (a finding) outranks 3 (inconclusive), which outranks 2 (a part refused its input), which outranks 0
  (
    set -- SECURECONFIG_EGRESS_ALLOW_URL 'https://sts.amazonaws.com/'
    [ "${1-}" = SECURECONFIG_EGRESS_ALLOW_URL ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
    shift
    [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 URL; not probing"; exit 2; }
    [ -n "${1-}" ] || { echo "substitute a URL on this workload's egress allow list; not probing"; exit 2; }
    set -- "$1" "$(if curl -q -g -s -o /dev/null --noproxy '*' -w '%{http_code}\n' --max-time 5 "$1"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
    set -- "$1" "${2##*$'\n'}" "${2%%$'\n'*}"   # the URL, curl's exit status, then the HTTP code
    printf '%s\n' "$3"
    case "$2:$3" in
      0:000) echo "no HTTP response from the allowed URL, so this positive control failed and the negative control below proves nothing; inconclusive"; exit 3 ;;
      0:*) exit 0 ;;                    # an HTTP response, whatever its code: the control passed
      *) echo "curl exit $2: no HTTP response from the allowed URL, so this positive control failed and the negative control below proves nothing; inconclusive"; exit 3 ;;
    esac
  )
  case "$?:$1" in 0:*) ;; 1:*) set -- 1 ;; 2:0) set -- 2 ;; 2:*|*:1) ;; *) set -- 3 ;; esac   # fold that part's status into the block's, ranked as above

  # negative control: a known-live host outside the egress allow list, judged by curl's exit status,
  # not by matching text in its output, since a successful connection also lacks the string
  # "Could not resolve host" and so would otherwise be misreported as blocked.
  # Status: 1 when the connection succeeded, 3 for curl exit 6 or an unexpected code, and 0 for exit 7
  # or 28, which still needs the time_connect and deny-record evidence it prints
  (                                                 # a subshell, so the exit below ends only this check
    # guard-conventions: allow C4-EXAMPLE-HOST egress negative control: example.com, served by IANA, is a known-live host outside the egress allow list, and this probe must fail when egress is enforced
    if curl -q -g -s --noproxy '*' --connect-timeout 5 --max-time 10 -o /dev/null -w 'time_connect=%{time_connect}\n' https://example.com/; then set -- 0; else set -- "$?"; fi
    case "$1" in
      0)
        echo "FAIL: connected to a host outside the allow list, egress is not enforced"
        exit 1 ;;
      6)
        echo "inconclusive: DNS resolution failed (curl exit 6), confirm this host still resolves before retrying"
        exit 3 ;;
      7|28)
        echo "request failed or timed out (curl exit $1): inconclusive on its own. curl cannot say why it"
        echo "failed, and --max-time can expire after the connection already succeeded, in which case the"
        echo "time_connect printed above is non-zero. Treat this as blocked only when time_connect stayed"
        echo "0.000000 AND the enforcement point recorded the deny: a VPC Flow Logs REJECT for this flow,"
        echo "or the CNI's NetworkPolicy drop log or counter"
        exit 0 ;;
      *)
        echo "unexpected curl exit code $1, investigate before treating this as a pass"
        exit 3 ;;
    esac
  )
  case "$?:$1" in 0:*) ;; 1:*) set -- 1 ;; 2:0) set -- 2 ;; 2:*|*:1) ;; *) set -- 3 ;; esac   # fold that part's status into the block's, ranked as above
  echo "block exit $1; the positive control's HTTP code, and a negative-control 0 for curl exit 7 or 28, are not classified further, so read them as above"
  exit "$1"
)
```

```bash
# REASONED: the applied metadata options, per the cited AWS instance metadata options and
# modify-instance-metadata-options pages; no exposed/fixed run is recorded.
# confirm the metadata options actually took effect: run this wherever your AWS CLI has credentials
# for the account, not on the workload. It prints HttpTokens, HttpPutResponseHopLimit,
# HttpProtocolIpv6 and State, in that order, separated by tabs.
(                                       # a subshell, so your own script arguments are untouched
  set +e                                # errexit off here, so a command that fails is classified below instead of ending the block
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_INSTANCE_ID'   # the instance ID, such as i-0123456789abcdef0: replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 2; }
  case "$1" in
    ""|*REPLACE_WITH_*|-*|*[[:space:][:cntrl:]]*) echo "substitute your instance ID inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  set -- "$(if aws ec2 describe-instances --instance-ids "$1" \
    --query 'Reservations[].Instances[].MetadataOptions.[HttpTokens,HttpPutResponseHopLimit,HttpProtocolIpv6,State]' \
    --output text; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "${1##*$'\n'}" "${1%$'\n'*}"   # the CLI's exit status, then its output
  set -- "$1" "${2%$'\n'}"              # the exit status, then the four values without the output's final newline
  printf '%s\n' "$2"
  # expect HttpTokens: required, HttpPutResponseHopLimit: 1, HttpProtocolIpv6: disabled (the safe stance;
  # if you deliberately enabled IPv6 IMDS it reads enabled, and you must then block and probe
  # [fd00:ec2::254] as well), and State: applied (State: pending means the change is not yet in effect);
  # then re-run the workload-side probes above to confirm the live behaviour.
  case "$1:$2" in
    0:optional$'\t'*) echo "FINDING: HttpTokens is optional, so the instance answers metadata requests without an IMDSv2 token"; exit 1 ;;
    0:required$'\t'1$'\t'*$'\t'applied) echo "block exit 0; HttpProtocolIpv6 is not classified, so read it as above" ;;
    0:required$'\t'1$'\t'*) echo "State is not applied (pending means the change is not yet in effect); inconclusive"; exit 3 ;;
    0:required$'\t'[0123456789]*) echo "FINDING: HttpPutResponseHopLimit is above 1, so a token response can reach a container an extra hop away"; exit 1 ;;
    0:*) echo "the metadata options above are not one instance's four values in the expected form; inconclusive"; exit 3 ;;
    *) echo "aws ec2 describe-instances exit $1: could not read the metadata options; inconclusive"; exit 3 ;;
  esac
)
```

## Sources (checked September 2026)

- AWS EC2 instance metadata service configuration (IMDSv2, hop limit, the `[fd00:ec2::254]` IPv6 endpoint): https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- AWS instance metadata options (hop-limit defaults incl. `ImdsSupport: v2.0`, IPv6): https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-options.html
- AWS VPC Flow Logs limitations (metadata `169.254.169.254` traffic is not logged): https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-limitations.html
- GCP querying metadata (required header, IPv6 `[fd20:ce::254]`): https://docs.cloud.google.com/compute/docs/metadata/querying-metadata
- AWS VPC security groups (traffic security groups do not filter, including instance metadata): https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html
- AWS CLI `modify-instance-metadata-options`: https://docs.aws.amazon.com/cli/latest/reference/ec2/modify-instance-metadata-options.html
- GCP metadata server overview: https://docs.cloud.google.com/compute/docs/metadata/overview
- GCP VPC firewall (a VM reaches metadata regardless of firewall rules): https://docs.cloud.google.com/firewall/docs/firewalls#metadata-server
- Azure Instance Metadata Service (API version 2025-04-07): https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service
- Kubernetes NetworkPolicy: https://kubernetes.io/docs/concepts/services-networking/network-policies/
- Docker network create (`--internal`): https://docs.docker.com/reference/cli/docker/network/create/
- curl manual (exit 7 "Failed to connect to host", exit 28 "Operation timeout", `--connect-timeout`, and the `time_connect` write-out variable): https://curl.se/docs/manpage.html
- AWS security-group rules (allow-only, default egress, combined groups; checked October 2026): https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html#security-group-rule-characteristics
- AWS network ACL basics (subnet deny, stateless; checked October 2026): https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html#nacl-basics
- GCP egress cases (implied allow egress to any destination; checked October 2026): https://docs.cloud.google.com/firewall/docs/firewalls#egress_cases
- Azure NSG default outbound rules (8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f, lines 67-85; checked October 2026): https://github.com/MicrosoftDocs/azure-docs/blob/8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f/articles/virtual-network/network-security-groups-overview.md#L67-L85
- Azure private subnet outbound access (checked October 2026): https://learn.microsoft.com/en-us/azure/virtual-network/ip-services/default-outbound-access#retirement-of-default-outbound-access-scope-and-impact
- iptables owner match (v1.8.13, lines 1-10; checked October 2026): https://git.netfilter.org/iptables/tree/extensions/libxt_owner.man?h=v1.8.13#n1
- iptables and ip6tables commands (v1.8.13, lines 28-32, 76-77, 99-102, 152-155, 293-304, 306-315; checked October 2026): https://git.netfilter.org/iptables/tree/iptables/iptables.8.in?h=v1.8.13#n28
- nftables output hook (v1.1.7, lines 230-234; checked October 2026): https://git.netfilter.org/nftables/tree/doc/nft.txt?h=v1.1.7#n230
- nftables chains and hooks (v1.1.7, lines 387-419; checked October 2026): https://git.netfilter.org/nftables/tree/doc/nft.txt?h=v1.1.7#n387
- nftables socket UID (v1.1.7, lines 92-94; checked October 2026): https://git.netfilter.org/nftables/tree/doc/primary-expression.txt?h=v1.1.7#n92
- AWS STS MissingAuthenticationToken (checked October 2026): https://docs.aws.amazon.com/STS/latest/APIReference/CommonErrors.html#CommonErrors-MissingAuthenticationToken
- AWS STS global endpoint (checked October 2026): https://docs.aws.amazon.com/general/latest/gr/sts.html#sts_region


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- aws: AWS metadata and networking (unknown)
- gcp: Google Cloud metadata and firewall (unknown)
- azure: Azure IMDS API (2025-04-07)
- azure-nsg: Azure network security groups (8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f)
- azure-outbound: Azure outbound access (unknown)
- kubernetes: Kubernetes NetworkPolicy (unknown)
- docker: Docker network create (unknown)
- iptables: iptables owner match (v1.8.13)
- nftables: nftables packet filtering (v1.1.7)
- curl: curl documentation (unknown)

Claims (full source mapping in the JSON block below):

- aws-endpoints (REASONED; aws): IMDS uses 169.254.169.254 and, on Nitro in IPv6-enabled subnets, [fd00:ec2::254]; block or verify-disabled both paths.
- aws-token (REASONED; aws): IMDSv2 requires a PUT-issued session token on subsequent GETs; required tokens make missing/invalid-token requests return 401.
- hop-default (REASONED; aws): PUT response hop limit is often 1, but launch/account/Region options and ImdsSupport: v2.0 AMIs can make it 2; set it explicitly.
- hop-control (REASONED; aws): Set required tokens, hop limit 1 and endpoint enabled; a container an extra routing hop away cannot receive the token, but this does not exclude every proxy path.
- aws-ipv6 (REASONED; aws): The modify command leaves HttpProtocolIpv6 unchanged; IPv6 IMDS defaults disabled. If deliberately enabled, block and probe it too.
- gcp-header (REASONED; gcp): GCP metadata uses metadata.google.internal or 169.254.169.254, requires Metadata-Flavor: Google and stays on the physical host.
- gcp-ipv6 (REASONED; gcp): IPv6-only GCP instances also expose metadata at [fd20:ce::254]; include it in workload restrictions.
- azure-header (REASONED; azure): Azure IMDS is VM-local at 169.254.169.254, requires Metadata: true and rejects X-Forwarded-For; the example instance API uses 2025-04-07.
- guest-block (REASONED; gcp, azure, aws): Headers do not stop a fetcher that can add them; use guest/workload metadata restrictions, accounting for DNS use of the address and all enabled IPv6 endpoints.
- gcp-firewall (REASONED; gcp): GCP VPC and hierarchical firewall rules do not block metadata-server traffic; use a host firewall, CNI or enforced egress proxy path.
- cloud-egress (REASONED; aws, gcp, azure-nsg, azure-outbound): AWS security groups and Google Cloud VPC firewalls start with broad outbound allowances; Azure NSGs include outbound allow rules. At the time of writing, the fetched Azure page says subnets in new virtual networks created with API versions released after March 31, 2026, and through the portal default to private; existing virtual networks are unchanged. Those private subnets need explicit outbound connectivity to public endpoints. This guide recommends permitting only DNS and required provider APIs.
- aws-groups (REASONED; aws): Security groups are allow-only and additive across attached groups; remove default allow-all egress and add narrow rules. A subnet network ACL supplies deny rules but is stateless.
- aws-metadata-bypass (REASONED; aws): AWS security groups do not filter 169.254.169.254; use IMDSv2/hop limit or disable unused metadata, keeping egress rules for other destinations.
- policy-default (REASONED; kubernetes): Pod egress is unrestricted until a selecting policy includes Egress; policies add allowances, so audit every selecting policy.
- policy-limits (REASONED; kubernetes): NetworkPolicy needs an enforcing CNI and has undefined hostNetwork behaviour; confirm enforcement before relying on it.
- policy-dns (REASONED; kubernetes): agent-egress selects app: agent and allows UDP/TCP 53 to kube-system pods labeled k8s-app: kube-dns.
- policy-api (REASONED; kubernetes): The API allowance permits TCP 443 to 203.0.113.0/24 as a replaceable destination placeholder.
- docker-internal (REASONED; docker): An internal Docker network has no default route out and firewall rules drop external traffic while peer containers communicate.
- host-owner (REASONED; aws, iptables, nftables): Hop limit 1 still permits host processes; this guide recommends OUTPUT owner filtering and matching IPv6 rules. The owner match applies to locally generated packets, not forwarded containers; an nftables equivalent must be in a base chain hooked at the output path, or in a regular chain reached from that base chain by a jump.
- proxy-bypass (REASONED; curl): A destination-allowlist proxy controls only traversing traffic; pair it with a direct metadata block and test its path separately.
- verify-headers (REASONED; aws, gcp, azure): Tokenless AWS must return 401; headerless GCP/Azure must not return metadata. These header checks alone do not demonstrate network isolation.
- verify-token (REASONED; aws, curl): AWS network checks acquire a token then GET with it, separately over IPv4/IPv6; failed PUT needs enforcement evidence. Token/session reachability is not IAM credential issuance.
- verify-provider-paths (REASONED; gcp, azure): Required-header GCP token and Azure instance requests test reachability; any HTTP response means reachable. GCP returns credentials; Azure instance data is separate from managed-identity tokens.
- verify-deny (REASONED; curl, aws): Run positive metadata controls before blocking; http=000 alone is inconclusive. Require no completed connection plus a matching enforcement deny record; metadata is excluded from AWS VPC Flow Logs.
- verify-allow (REASONED; curl, aws): A positive-control bare unauthenticated GET can target any host on this workload's egress allow list; the fetched STS pages document the global endpoint and authentication errors, and that endpoint is one example when allowed. Receiving an HTTP response is this guide's REASONED expectation; the exact status and body of the bare unauthenticated GET are unknown. --noproxy tests direct egress, so proxy allowlists require separate probes.
- verify-negative (REASONED; curl): Known-live disallowed egress must fail: curl success is a finding (block status 1), exit 6 is DNS-inconclusive (block status 3), and 7/28 need zero time_connect plus correlated deny evidence.
- verify-options (REASONED; aws): Read MetadataOptions for required tokens, hop limit 1, intended IPv6 state and State applied rather than pending, then repeat workload probes.

````json
{
  "schema": 1,
  "checked": "2026-10-18",
  "documentation_checked": "2026-09",
  "body_sha256": "812f8213d3e3f17620fbb5da007c69442bbc7361a669ef5672dbd8ab4f545f88",
  "components": {
    "aws": {
      "name": "AWS metadata and networking",
      "basis": "unknown",
      "sources": {
        "s82aca706445c": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html",
        "s8e0b69b2747a": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-options.html",
        "s5de42a587ed0": "https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-limitations.html",
        "s6761ddae28b8": "https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html",
        "sb843930c4944": "https://docs.aws.amazon.com/cli/latest/reference/ec2/modify-instance-metadata-options.html",
        "sba085af3d477": "https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html#security-group-rule-characteristics",
        "s0604de50506f": "https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html#nacl-basics",
        "s9e5244cd7271": "https://docs.aws.amazon.com/STS/latest/APIReference/CommonErrors.html#CommonErrors-MissingAuthenticationToken",
        "sb525b61fd496": "https://docs.aws.amazon.com/general/latest/gr/sts.html#sts_region"
      }
    },
    "gcp": {
      "name": "Google Cloud metadata and firewall",
      "basis": "unknown",
      "sources": {
        "sdb98c49a5970": "https://docs.cloud.google.com/compute/docs/metadata/querying-metadata",
        "se75aedd46ef0": "https://docs.cloud.google.com/compute/docs/metadata/overview",
        "see9b515c5ffd": "https://docs.cloud.google.com/firewall/docs/firewalls#metadata-server",
        "s0d0c82f83f1d": "https://docs.cloud.google.com/firewall/docs/firewalls#egress_cases"
      }
    },
    "azure": {
      "name": "Azure IMDS API",
      "basis": "2025-04-07",
      "sources": {
        "s5301638a3c81": "https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service"
      }
    },
    "azure-nsg": {
      "name": "Azure network security groups",
      "basis": "8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f",
      "sources": {
        "scd8e9e55f3b7": "https://github.com/MicrosoftDocs/azure-docs/blob/8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f/articles/virtual-network/network-security-groups-overview.md#L67-L85"
      }
    },
    "azure-outbound": {
      "name": "Azure outbound access",
      "basis": "unknown",
      "sources": {
        "sdf1b3f364763": "https://learn.microsoft.com/en-us/azure/virtual-network/ip-services/default-outbound-access#retirement-of-default-outbound-access-scope-and-impact"
      }
    },
    "kubernetes": {
      "name": "Kubernetes NetworkPolicy",
      "basis": "unknown",
      "sources": {
        "s953450b4076f": "https://kubernetes.io/docs/concepts/services-networking/network-policies/"
      }
    },
    "docker": {
      "name": "Docker network create",
      "basis": "unknown",
      "sources": {
        "sc308b8f1039c": "https://docs.docker.com/reference/cli/docker/network/create/"
      }
    },
    "iptables": {
      "name": "iptables owner match",
      "basis": "v1.8.13",
      "sources": {
        "s35430e42cc22": "https://git.netfilter.org/iptables/tree/extensions/libxt_owner.man?h=v1.8.13#n1",
        "s8033be9cc6c1": "https://git.netfilter.org/iptables/tree/iptables/iptables.8.in?h=v1.8.13#n28"
      }
    },
    "nftables": {
      "name": "nftables packet filtering",
      "basis": "v1.1.7",
      "sources": {
        "se1acebec90fb": "https://git.netfilter.org/nftables/tree/doc/nft.txt?h=v1.1.7#n230",
        "s85ee6e57ed0c": "https://git.netfilter.org/nftables/tree/doc/nft.txt?h=v1.1.7#n387",
        "s60417f1df3e4": "https://git.netfilter.org/nftables/tree/doc/primary-expression.txt?h=v1.1.7#n92"
      }
    },
    "curl": {
      "name": "curl documentation",
      "basis": "unknown",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    }
  },
  "claims": {
    "aws-endpoints": {"text": "IMDS uses 169.254.169.254 and, on Nitro in IPv6-enabled subnets, [fd00:ec2::254]; block or verify-disabled both paths.", "components": ["aws"], "sources": ["aws:s82aca706445c", "aws:s8e0b69b2747a"], "status": "REASONED"},
    "aws-token": {"text": "IMDSv2 requires a PUT-issued session token on subsequent GETs; required tokens make missing/invalid-token requests return 401.", "components": ["aws"], "sources": ["aws:s82aca706445c"], "status": "REASONED"},
    "hop-default": {"text": "PUT response hop limit is often 1, but launch/account/Region options and ImdsSupport: v2.0 AMIs can make it 2; set it explicitly.", "components": ["aws"], "sources": ["aws:s82aca706445c", "aws:s8e0b69b2747a"], "status": "REASONED"},
    "hop-control": {"text": "Set required tokens, hop limit 1 and endpoint enabled; a container an extra routing hop away cannot receive the token, but this does not exclude every proxy path.", "components": ["aws"], "sources": ["aws:s82aca706445c", "aws:sb843930c4944"], "status": "REASONED"},
    "aws-ipv6": {"text": "The modify command leaves HttpProtocolIpv6 unchanged; IPv6 IMDS defaults disabled. If deliberately enabled, block and probe it too.", "components": ["aws"], "sources": ["aws:s8e0b69b2747a", "aws:sb843930c4944"], "status": "REASONED"},
    "gcp-header": {"text": "GCP metadata uses metadata.google.internal or 169.254.169.254, requires Metadata-Flavor: Google and stays on the physical host.", "components": ["gcp"], "sources": ["gcp:sdb98c49a5970", "gcp:se75aedd46ef0"], "status": "REASONED"},
    "gcp-ipv6": {"text": "IPv6-only GCP instances also expose metadata at [fd20:ce::254]; include it in workload restrictions.", "components": ["gcp"], "sources": ["gcp:sdb98c49a5970"], "status": "REASONED"},
    "azure-header": {"text": "Azure IMDS is VM-local at 169.254.169.254, requires Metadata: true and rejects X-Forwarded-For; the example instance API uses 2025-04-07.", "components": ["azure"], "sources": ["azure:s5301638a3c81"], "status": "REASONED"},
    "guest-block": {"text": "Headers do not stop a fetcher that can add them; use guest/workload metadata restrictions, accounting for DNS use of the address and all enabled IPv6 endpoints.", "components": ["gcp", "azure", "aws"], "sources": ["gcp:sdb98c49a5970", "gcp:see9b515c5ffd", "azure:s5301638a3c81", "aws:s82aca706445c"], "status": "REASONED"},
    "gcp-firewall": {"text": "GCP VPC and hierarchical firewall rules do not block metadata-server traffic; use a host firewall, CNI or enforced egress proxy path.", "components": ["gcp"], "sources": ["gcp:see9b515c5ffd"], "status": "REASONED"},
    "cloud-egress": {"text": "AWS security groups and Google Cloud VPC firewalls start with broad outbound allowances; Azure NSGs include outbound allow rules. At the time of writing, the fetched Azure page says subnets in new virtual networks created with API versions released after March 31, 2026, and through the portal default to private; existing virtual networks are unchanged. Those private subnets need explicit outbound connectivity to public endpoints. This guide recommends permitting only DNS and required provider APIs.", "components": ["aws", "gcp", "azure-nsg", "azure-outbound"], "sources": ["aws:s6761ddae28b8", "aws:sba085af3d477", "gcp:s0d0c82f83f1d", "azure-nsg:scd8e9e55f3b7", "azure-outbound:sdf1b3f364763"], "status": "REASONED"},
    "aws-groups": {"text": "Security groups are allow-only and additive across attached groups; remove default allow-all egress and add narrow rules. A subnet network ACL supplies deny rules but is stateless.", "components": ["aws"], "sources": ["aws:s6761ddae28b8", "aws:sba085af3d477", "aws:s0604de50506f"], "status": "REASONED"},
    "aws-metadata-bypass": {"text": "AWS security groups do not filter 169.254.169.254; use IMDSv2/hop limit or disable unused metadata, keeping egress rules for other destinations.", "components": ["aws"], "sources": ["aws:s6761ddae28b8", "aws:s8e0b69b2747a"], "status": "REASONED"},
    "policy-default": {"text": "Pod egress is unrestricted until a selecting policy includes Egress; policies add allowances, so audit every selecting policy.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED"},
    "policy-limits": {"text": "NetworkPolicy needs an enforcing CNI and has undefined hostNetwork behaviour; confirm enforcement before relying on it.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED"},
    "policy-dns": {"text": "agent-egress selects app: agent and allows UDP/TCP 53 to kube-system pods labeled k8s-app: kube-dns.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED"},
    "policy-api": {"text": "The API allowance permits TCP 443 to 203.0.113.0/24 as a replaceable destination placeholder.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED"},
    "docker-internal": {"text": "An internal Docker network has no default route out and firewall rules drop external traffic while peer containers communicate.", "components": ["docker"], "sources": ["docker:sc308b8f1039c"], "status": "REASONED"},
    "host-owner": {"text": "Hop limit 1 still permits host processes; this guide recommends OUTPUT owner filtering and matching IPv6 rules. The owner match applies to locally generated packets, not forwarded containers; an nftables equivalent must be in a base chain hooked at the output path, or in a regular chain reached from that base chain by a jump.", "components": ["aws", "iptables", "nftables"], "sources": ["aws:s82aca706445c", "iptables:s35430e42cc22", "iptables:s8033be9cc6c1", "nftables:se1acebec90fb", "nftables:s85ee6e57ed0c", "nftables:s60417f1df3e4"], "status": "REASONED"},
    "proxy-bypass": {"text": "A destination-allowlist proxy controls only traversing traffic; pair it with a direct metadata block and test its path separately.", "components": ["curl"], "sources": ["curl:s2b2686afaf41"], "status": "REASONED"},
    "verify-headers": {"text": "Tokenless AWS must return 401; headerless GCP/Azure must not return metadata. These header checks alone do not demonstrate network isolation.", "components": ["aws", "gcp", "azure"], "sources": ["aws:s82aca706445c", "gcp:sdb98c49a5970", "azure:s5301638a3c81"], "status": "REASONED", "verify": [1, 3, 4]},
    "verify-token": {"text": "AWS network checks acquire a token then GET with it, separately over IPv4/IPv6; failed PUT needs enforcement evidence. Token/session reachability is not IAM credential issuance.", "components": ["aws", "curl"], "sources": ["aws:s82aca706445c", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [2]},
    "verify-provider-paths": {"text": "Required-header GCP token and Azure instance requests test reachability; any HTTP response means reachable. GCP returns credentials; Azure instance data is separate from managed-identity tokens.", "components": ["gcp", "azure"], "sources": ["gcp:sdb98c49a5970", "azure:s5301638a3c81"], "status": "REASONED", "verify": [3, 4]},
    "verify-deny": {"text": "Run positive metadata controls before blocking; http=000 alone is inconclusive. Require no completed connection plus a matching enforcement deny record; metadata is excluded from AWS VPC Flow Logs.", "components": ["curl", "aws"], "sources": ["curl:s2b2686afaf41", "aws:s5de42a587ed0"], "status": "REASONED", "verify": [2, 3, 4]},
    "verify-allow": {"text": "A positive-control bare unauthenticated GET can target any host on this workload's egress allow list; the fetched STS pages document the global endpoint and authentication errors, and that endpoint is one example when allowed. Receiving an HTTP response is this guide's REASONED expectation; the exact status and body of the bare unauthenticated GET are unknown. --noproxy tests direct egress, so proxy allowlists require separate probes.", "components": ["curl", "aws"], "sources": ["curl:s2b2686afaf41", "aws:s9e5244cd7271", "aws:sb525b61fd496"], "status": "REASONED", "verify": [5]},
    "verify-negative": {"text": "Known-live disallowed egress must fail: curl success is a finding (block status 1), exit 6 is DNS-inconclusive (block status 3), and 7/28 need zero time_connect plus correlated deny evidence.", "components": ["curl"], "sources": ["curl:s2b2686afaf41"], "status": "REASONED", "verify": [5]},
    "verify-options": {"text": "Read MetadataOptions for required tokens, hop limit 1, intended IPv6 state and State applied rather than pending, then repeat workload probes.", "components": ["aws"], "sources": ["aws:s8e0b69b2747a", "aws:sb843930c4944"], "status": "REASONED", "verify": [6]}
  }
}
````
<!-- version-basis:end -->
