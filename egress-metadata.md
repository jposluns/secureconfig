---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "ec354e7856390374a23b7e1998f9d37152bc9d095115f14d5a0132d6bf29edee",
  "components": {
    "aws": {
      "name": "AWS metadata and networking",
      "basis": "unknown",
      "sources": {
        "s82aca706445c": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html",
        "s8e0b69b2747a": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-options.html",
        "s5de42a587ed0": "https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs-limitations.html",
        "s6761ddae28b8": "https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html",
        "sb843930c4944": "https://docs.aws.amazon.com/cli/latest/reference/ec2/modify-instance-metadata-options.html"
      }
    },
    "gcp": {
      "name": "Google Cloud metadata and firewall",
      "basis": "unknown",
      "sources": {
        "sdb98c49a5970": "https://docs.cloud.google.com/compute/docs/metadata/querying-metadata",
        "se75aedd46ef0": "https://docs.cloud.google.com/compute/docs/metadata/overview",
        "see9b515c5ffd": "https://docs.cloud.google.com/firewall/docs/firewalls#metadata-server"
      }
    },
    "azure": {
      "name": "Azure IMDS API",
      "basis": "2025-04-07",
      "sources": {
        "s5301638a3c81": "https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service"
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
    "cloud-egress": {"text": "Replace broadly allowed outbound access with DNS and required API destinations; the most-providers default generalization is not fully sourced here.", "components": ["aws"], "sources": ["aws:s6761ddae28b8"], "status": "REASONED"},
    "aws-groups": {"text": "Security groups are allow-only and additive across attached groups; remove default allow-all egress and add narrow rules. A subnet network ACL supplies deny rules.", "components": ["aws"], "sources": ["aws:s6761ddae28b8"], "status": "REASONED"},
    "aws-metadata-bypass": {"text": "AWS security groups do not filter 169.254.169.254; use IMDSv2/hop limit or disable unused metadata, keeping egress rules for other destinations.", "components": ["aws"], "sources": ["aws:s6761ddae28b8", "aws:s8e0b69b2747a"], "status": "REASONED"},
    "policy-default": {"text": "Pod egress is unrestricted until a selecting policy includes Egress; policies add allowances, so audit every selecting policy.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED"},
    "policy-limits": {"text": "NetworkPolicy needs an enforcing CNI and has undefined hostNetwork behaviour; confirm enforcement before relying on it.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED"},
    "policy-dns": {"text": "agent-egress selects app: agent and allows UDP/TCP 53 to kube-system pods labeled k8s-app: kube-dns.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED"},
    "policy-api": {"text": "The API allowance permits TCP 443 to 203.0.113.0/24 as a replaceable destination placeholder.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED"},
    "docker-internal": {"text": "An internal Docker network has no default route out and firewall rules drop external traffic while peer containers communicate.", "components": ["docker"], "sources": ["docker:sc308b8f1039c"], "status": "REASONED"},
    "host-owner": {"text": "Hop limit 1 still permits host processes; the guide recommends OUTPUT owner filtering and matching IPv6 rules, excluding forwarded containers. Netfilter syntax lacks a direct source here.", "components": ["aws"], "sources": ["aws:s82aca706445c"], "status": "REASONED"},
    "proxy-bypass": {"text": "A destination-allowlist proxy controls only traversing traffic; pair it with a direct metadata block and test its path separately.", "components": ["curl"], "sources": ["curl:s2b2686afaf41"], "status": "REASONED"},
    "verify-headers": {"text": "Tokenless AWS must return 401; headerless GCP/Azure must not return metadata. These header checks alone do not demonstrate network isolation.", "components": ["aws", "gcp", "azure"], "sources": ["aws:s82aca706445c", "gcp:sdb98c49a5970", "azure:s5301638a3c81"], "status": "REASONED", "verify": [1]},
    "verify-token": {"text": "AWS network checks acquire a token then GET with it, separately over IPv4/IPv6; failed PUT needs enforcement evidence. Token/session reachability is not IAM credential issuance.", "components": ["aws", "curl"], "sources": ["aws:s82aca706445c", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-provider-paths": {"text": "Required-header GCP token and Azure instance requests test reachability; any HTTP response means reachable. GCP returns credentials; Azure instance data is separate from managed-identity tokens.", "components": ["gcp", "azure"], "sources": ["gcp:sdb98c49a5970", "azure:s5301638a3c81"], "status": "REASONED", "verify": [1]},
    "verify-deny": {"text": "Run positive metadata controls before blocking; http=000 alone is inconclusive. Require no completed connection plus a matching enforcement deny record; metadata is excluded from AWS VPC Flow Logs.", "components": ["curl", "aws"], "sources": ["curl:s2b2686afaf41", "aws:s5de42a587ed0"], "status": "REASONED", "verify": [1]},
    "verify-allow": {"text": "The allowed STS destination must remain reachable; --noproxy tests direct egress, so proxy allowlists require separate probes. STS-specific behaviour has no direct source here.", "components": ["curl"], "sources": ["curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-negative": {"text": "Known-live disallowed egress must fail: curl success is failure, exit 6 is DNS-inconclusive, and 7/28 need zero time_connect plus correlated deny evidence.", "components": ["curl"], "sources": ["curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-options": {"text": "Read MetadataOptions for required tokens, hop limit 1, intended IPv6 state and State applied rather than pending, then repeat workload probes.", "components": ["aws"], "sources": ["aws:s8e0b69b2747a", "aws:sb843930c4944"], "status": "REASONED", "verify": [1]}
  }
}
---
# Egress control and cloud metadata: keeping an agent from exfiltrating credentials

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| aws-endpoints: IMDS uses 169.254.169.254 and, on Nitro in IPv6-enabled subnets, [fd00:ec2::254]; block or verify-disabled both paths. | AWS metadata and networking unknown | REASONED |
| aws-token: IMDSv2 requires a PUT-issued session token on subsequent GETs; required tokens make missing/invalid-token requests return 401. | AWS metadata and networking unknown | REASONED |
| hop-default: PUT response hop limit is often 1, but launch/account/Region options and ImdsSupport: v2.0 AMIs can make it 2; set it explicitly. | AWS metadata and networking unknown | REASONED |
| hop-control: Set required tokens, hop limit 1 and endpoint enabled; a container an extra routing hop away cannot receive the token, but this does not exclude every proxy path. | AWS metadata and networking unknown | REASONED |
| aws-ipv6: The modify command leaves HttpProtocolIpv6 unchanged; IPv6 IMDS defaults disabled. If deliberately enabled, block and probe it too. | AWS metadata and networking unknown | REASONED |
| gcp-header: GCP metadata uses metadata.google.internal or 169.254.169.254, requires Metadata-Flavor: Google and stays on the physical host. | Google Cloud metadata and firewall unknown | REASONED |
| gcp-ipv6: IPv6-only GCP instances also expose metadata at [fd20:ce::254]; include it in workload restrictions. | Google Cloud metadata and firewall unknown | REASONED |
| azure-header: Azure IMDS is VM-local at 169.254.169.254, requires Metadata: true and rejects X-Forwarded-For; the example instance API uses 2025-04-07. | Azure IMDS API 2025-04-07 | REASONED |
| guest-block: Headers do not stop a fetcher that can add them; use guest/workload metadata restrictions, accounting for DNS use of the address and all enabled IPv6 endpoints. | Google Cloud metadata and firewall unknown; Azure IMDS API 2025-04-07; AWS metadata and networking unknown | REASONED |
| gcp-firewall: GCP VPC and hierarchical firewall rules do not block metadata-server traffic; use a host firewall, CNI or enforced egress proxy path. | Google Cloud metadata and firewall unknown | REASONED |
| cloud-egress: Replace broadly allowed outbound access with DNS and required API destinations; the most-providers default generalization is not fully sourced here. | AWS metadata and networking unknown | REASONED |
| aws-groups: Security groups are allow-only and additive across attached groups; remove default allow-all egress and add narrow rules. A subnet network ACL supplies deny rules. | AWS metadata and networking unknown | REASONED |
| aws-metadata-bypass: AWS security groups do not filter 169.254.169.254; use IMDSv2/hop limit or disable unused metadata, keeping egress rules for other destinations. | AWS metadata and networking unknown | REASONED |
| policy-default: Pod egress is unrestricted until a selecting policy includes Egress; policies add allowances, so audit every selecting policy. | Kubernetes NetworkPolicy unknown | REASONED |
| policy-limits: NetworkPolicy needs an enforcing CNI and has undefined hostNetwork behaviour; confirm enforcement before relying on it. | Kubernetes NetworkPolicy unknown | REASONED |
| policy-dns: agent-egress selects app: agent and allows UDP/TCP 53 to kube-system pods labeled k8s-app: kube-dns. | Kubernetes NetworkPolicy unknown | REASONED |
| policy-api: The API allowance permits TCP 443 to 203.0.113.0/24 as a replaceable destination placeholder. | Kubernetes NetworkPolicy unknown | REASONED |
| docker-internal: An internal Docker network has no default route out and firewall rules drop external traffic while peer containers communicate. | Docker network create unknown | REASONED |
| host-owner: Hop limit 1 still permits host processes; the guide recommends OUTPUT owner filtering and matching IPv6 rules, excluding forwarded containers. Netfilter syntax lacks a direct source here. | AWS metadata and networking unknown | REASONED |
| proxy-bypass: A destination-allowlist proxy controls only traversing traffic; pair it with a direct metadata block and test its path separately. | curl documentation unknown | REASONED |
| verify-headers: Tokenless AWS must return 401; headerless GCP/Azure must not return metadata. These header checks alone do not demonstrate network isolation. | AWS metadata and networking unknown; Google Cloud metadata and firewall unknown; Azure IMDS API 2025-04-07 | REASONED |
| verify-token: AWS network checks acquire a token then GET with it, separately over IPv4/IPv6; failed PUT needs enforcement evidence. Token/session reachability is not IAM credential issuance. | AWS metadata and networking unknown; curl documentation unknown | REASONED |
| verify-provider-paths: Required-header GCP token and Azure instance requests test reachability; any HTTP response means reachable. GCP returns credentials; Azure instance data is separate from managed-identity tokens. | Google Cloud metadata and firewall unknown; Azure IMDS API 2025-04-07 | REASONED |
| verify-deny: Run positive metadata controls before blocking; http=000 alone is inconclusive. Require no completed connection plus a matching enforcement deny record; metadata is excluded from AWS VPC Flow Logs. | curl documentation unknown; AWS metadata and networking unknown | REASONED |
| verify-allow: The allowed STS destination must remain reachable; --noproxy tests direct egress, so proxy allowlists require separate probes. STS-specific behaviour has no direct source here. | curl documentation unknown | REASONED |
| verify-negative: Known-live disallowed egress must fail: curl success is failure, exit 6 is DNS-inconclusive, and 7/28 need zero time_connect plus correlated deny evidence. | curl documentation unknown | REASONED |
| verify-options: Read MetadataOptions for required tokens, hop limit 1, intended IPv6 state and State applied rather than pending, then repeat workload probes. | AWS metadata and networking unknown | REASONED |
<!-- version-basis:end -->

An AI agent, RAG fetcher, or webhook handler that retrieves URLs can be steered by a prompt injection into requesting the cloud metadata endpoint or an internal service instead of the URL it was meant to fetch. Making the fetcher refuse that request is application security; this guide covers the deployment-side backstop, metadata hardening so the endpoint rejects an unqualified request, plus default-deny egress so the request never leaves the workload at all.

## AWS: require IMDSv2 and cap the hop limit

The instance metadata service listens on `169.254.169.254`, and on Nitro instances in an IPv6-enabled subnet also on `[fd00:ec2::254]` (IMDSv2-compatible); block or verify-disabled BOTH, since an IPv4-only control misses the IPv6 path. IMDSv2 requires a session token obtained with a
`PUT` before any `GET` succeeds. The response to that `PUT`, the token itself, has a hop limit at the IP
protocol level (1 on many launches, but launch parameters, account/Region settings, and the IMDSv2-only
`ImdsSupport: v2.0` AMI setting can make it 2, so set it explicitly below rather than assuming): the token
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
  [cloud-firewalls.md](cloud-firewalls.md)): default outbound rules on most providers allow everything out.
  Permit only DNS and the specific provider APIs the application calls. On AWS a security group is
  allow-only (it has no deny rules), so you must REMOVE its default allow-all egress rule and add narrow
  allows, and account for every other security group attached to the instance; a network ACL, which does
  support deny rules, is the subnet-level complement. AWS security groups do not filter traffic to or from
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
  address by user with an `iptables` `OUTPUT` owner match, e.g. `iptables -A OUTPUT -d 169.254.169.254 -m owner ! --uid-owner aws -j DROP` (adapt the allowed uid); this does not cover traffic forwarded from a container, an nftables equivalent must attach to a hooked chain, and you need the matching `ip6tables` rule for `[fd00:ec2::254]` where IPv6 IMDS is enabled. A forward proxy with a destination allowlist only enforces on traffic that actually passes through it, so it is not a substitute for a network block: pair it with a rule that stops the workload reaching metadata directly, or the workload just bypasses the proxy, and test the proxy path separately.

## Scope boundary

Steering a fetcher into requesting the metadata address or an internal host is server-side request forgery,
an application-security defect belonging to the code doing the fetching, not to this guide. IMDSv2, the
header requirements above, and egress rules are deployment-side controls: they do not prevent the request
from being attempted, they make the attempt fail.

## Verify

REASONED: metadata headers, token flow, network blocks, egress controls and applied options; no exposed/fixed run is recorded in this guide. Expectations follow the cited cloud, NetworkPolicy and curl sources; this read-only review has no authorized cloud VM or workload enforcement point.

```bash
# --noproxy so an ambient http(s)_proxy/ALL_PROXY cannot answer in place of the metadata service (Azure
# documents that IMDS queries must bypass proxies); timeouts so a blocked address does not hang.
# Read this block manually and run it WITHOUT set -e: several probes below intentionally exit non-zero
# when a block is in place (a refused or timed-out connection), and set -e would stop the block on the first.
# AWS, no token supplied: with --http-tokens required this returns 401
curl -q -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 -w '%{http_code}\n' http://169.254.169.254/latest/meta-data/
# GCP, no Metadata-Flavor header: must fail, must not return metadata
curl -q -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 -w '%{http_code}\n' http://169.254.169.254/computeMetadata/v1/instance/
# Azure, no Metadata: true header: must fail, must not return metadata
curl -q -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 -w '%{http_code}\n' 'http://169.254.169.254/metadata/instance?api-version=2025-04-07'
# the three checks above test the header requirement, which is not the control this guide
# recommends. Test the network block itself, WITH the header the service requires, from a
# workload that has no legitimate reason to reach metadata:
# GCP (send the required header). For AWS, do the real IMDSv2 two-step - PUT a token then GET WITH it -
# because a tokenless 401 proves the header requirement, not a network block; for Azure send Metadata: true:
#   Assumes a clean Bash shell with trusted startup files. Uncomment each WHOLE subshell to run.
#   Tokens stay in positional parameters and curl's stdin, not named variables, environment or argv.
#   The same account and root can still read process memory; this does not erase earlier exports.
#   (
#     trap - DEBUG RETURN ERR
#     set +x +a +e
#     # Append curl's status after a newline, then split it from the response without a named variable.
#     set -- "$(curl -q -g -sf --noproxy '*' --connect-timeout 5 --max-time 5 -X PUT -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' http://169.254.169.254/latest/api/token; printf '\n%s' "$?")"
#     set -- "${1%$'\n'*}" "${1##*$'\n'}"
#     printf 'PUT exit: %s\n' "$2"
#     [ "$2" = 0 ] || { echo 'no usable token: PUT failed; inconclusive without an enforcement-point deny record'; exit 2; }
#     case "$1" in ''|*REPLACE_WITH_*|*[[:cntrl:]]*) echo 'empty or malformed token; inconclusive'; exit 2 ;; esac
#     printf 'X-aws-ec2-metadata-token: %s\n' "$1" | curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 -w 'aws=%{http_code} time_connect=%{time_connect}\n' -H @- http://169.254.169.254/latest/meta-data/iam/security-credentials/
#   )
#   Where IPv6 IMDS is enabled, repeat the WHOLE probe over IPv6 (do not reuse the IPv4 token - acquire
#   one over IPv6 too, since IPv4 may be blocked while IPv6 is not). Quote the bracketed literal, -q first
#   then -g. AWS, with the same clean-shell assumption:
#   (
#     trap - DEBUG RETURN ERR
#     set +x +a +e
#     set -- "$(curl -q -g -sf --noproxy '*' --connect-timeout 5 --max-time 5 -X PUT -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' 'http://[fd00:ec2::254]/latest/api/token'; printf '\n%s' "$?")"
#     set -- "${1%$'\n'*}" "${1##*$'\n'}"
#     printf 'PUT6 exit: %s\n' "$2"
#     [ "$2" = 0 ] || { echo 'no usable IPv6 token: PUT failed; inconclusive without an enforcement-point deny record'; exit 2; }
#     case "$1" in ''|*REPLACE_WITH_*|*[[:cntrl:]]*) echo 'empty or malformed IPv6 token; inconclusive'; exit 2 ;; esac
#     printf 'X-aws-ec2-metadata-token: %s\n' "$1" | curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 -w 'aws6=%{http_code} time_connect=%{time_connect}\n' -H @- 'http://[fd00:ec2::254]/latest/meta-data/'
#   )
#   GCP: curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 -w 'gcp6=%{http_code} time_connect=%{time_connect}\n' -H 'Metadata-Flavor: Google' 'http://[fd20:ce::254]/computeMetadata/v1/instance/'
#   Any HTTP response (including 401) means the IPv6 endpoint is reachable; read time_connect as below.
# Run these BEFORE applying the block too (the positive control): they should reach metadata then, so a
# later refusal is the block working, not the endpoint being down.
curl -q -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 \
  -w 'gcp=%{http_code} time_connect=%{time_connect}\n' -H 'Metadata-Flavor: Google' \
  http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token
curl -q -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 \
  -w 'azure=%{http_code} time_connect=%{time_connect}\n' -H 'Metadata: true' \
  'http://169.254.169.254/metadata/instance?api-version=2025-04-07'
# a 200 (or any HTTP response, including a 401) here means the metadata endpoint is reachable from the
# workload, whatever the header checks above returned. Reachability is the finding: GCP's probed path
# returns a live access token (credential issuance), while AWS's /latest/meta-data/iam/security-credentials/
# lists the attached role NAMES (append a role name to fetch the actual credentials) and the token PUT
# issues an IMDS session token, not IAM credentials, so treat the AWS checks as metadata reachability, not
# credential issuance; Azure's /metadata/instance likewise proves reachability only, its managed-identity
# token being a separate /metadata/identity/oauth2/token request. http=000 on its own is not proof of a
# block: an endpoint that accepts the
# connection and then stalls produces it too. Read time_connect, which stays 0.000000 only when no
# connection completed, and corroborate with an enforcement-point deny record for THIS flow: a CNI
# NetworkPolicy drop counter/log, a host iptables/nftables DROP counter, or a packet capture. Note AWS
# VPC Flow Logs EXCLUDE traffic to and from 169.254.169.254, so they cannot corroborate a metadata block
# (they are fine for the other egress destinations in the negative control below).
# positive control: a host on the egress allow list, for example the AWS STS endpoint used for role
# credentials, must succeed. --noproxy '*' on these two controls tests DIRECT egress (a network rule),
# not a forward proxy's allow list; where a proxy is the egress control, test through it separately.
curl -q -s -o /dev/null --noproxy '*' -w '%{http_code}\n' --max-time 5 https://sts.amazonaws.com/

# negative control: a known-live host outside the egress allow list, judged by curl's exit status,
# not by matching text in its output, since a successful connection also lacks the string
# "Could not resolve host" and so would otherwise be misreported as blocked
if curl -q -s --noproxy '*' --connect-timeout 5 --max-time 10 -o /dev/null -w 'time_connect=%{time_connect}\n' https://example.com/; then rc=0; else rc=$?; fi
if [ "$rc" -eq 0 ]; then
  echo "FAIL: connected to a host outside the allow list, egress is not enforced"
elif [ "$rc" -eq 6 ]; then
  echo "inconclusive: DNS resolution failed (curl exit 6), confirm this host still resolves before retrying"
elif [ "$rc" -eq 7 ] || [ "$rc" -eq 28 ]; then
  echo "request failed or timed out (curl exit $rc): inconclusive on its own. curl cannot say why it"
  echo "failed, and --max-time can expire after the connection already succeeded, in which case the"
  echo "time_connect printed above is non-zero. Treat this as blocked only when time_connect stayed"
  echo "0.000000 AND the enforcement point recorded the deny: a VPC Flow Logs REJECT for this flow,"
  echo "or the CNI's NetworkPolicy drop log or counter"
else
  echo "unexpected curl exit code $rc, investigate before treating this as a pass"
fi
# confirm the metadata options actually took effect
aws ec2 describe-instances --instance-ids i-0123456789abcdef0 \
  --query 'Reservations[].Instances[].MetadataOptions'
# expect HttpTokens: required, HttpPutResponseHopLimit: 1, HttpProtocolIpv6: disabled (the safe stance;
# if you deliberately enabled IPv6 IMDS it reads enabled, and you must then block and probe
# [fd00:ec2::254] as well), and State: applied (State: pending means the change is not yet in effect);
# then re-run the workload-side probes above to confirm the live behaviour.
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
- Azure Instance Metadata Service (2025-04-07): https://learn.microsoft.com/en-us/azure/virtual-machines/instance-metadata-service
- Kubernetes NetworkPolicy: https://kubernetes.io/docs/concepts/services-networking/network-policies/
- Docker network create (`--internal`): https://docs.docker.com/reference/cli/docker/network/create/
- curl manual (exit 7 "Failed to connect to host", exit 28 "Operation timeout", `--connect-timeout`, and the `time_connect` write-out variable): https://curl.se/docs/manpage.html
