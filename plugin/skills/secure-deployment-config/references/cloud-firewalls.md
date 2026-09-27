---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "e0b311b40e6ea58d7a06f881ad51b260ad36e741b08f3b27c387ebb78e6fb2b3",
  "components": {
    "aws": {
      "name": "AWS security groups and CLI",
      "basis": "unknown",
      "sources": {
        "s0c459e0aa7a1": "https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-security-group-rules.html",
        "s5594f61a25d6": "https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html",
        "sf8813f7c4057": "https://docs.aws.amazon.com/vpc/latest/userguide/managed-prefix-lists.html"
      }
    },
    "gcp": {
      "name": "Google Cloud firewall and CLI",
      "basis": "unknown",
      "sources": {
        "s1c06c98a99c9": "https://docs.cloud.google.com/firewall/docs/using-firewalls",
        "s3a90bf10d4eb": "https://docs.cloud.google.com/sdk/gcloud/reference/topic/formats"
      }
    },
    "azure": {
      "name": "Azure NSG and CLI",
      "basis": "unknown",
      "sources": {
        "se217f16ce4c1": "https://learn.microsoft.com/en-us/cli/azure/network/nsg/rule",
        "scde5b083d938": "https://learn.microsoft.com/en-us/rest/api/virtualnetwork/network-security-groups/get"
      }
    }
  },
  "claims": {
    "public-front": {"text": "Allow internet sources only to the front TLS layer on 80 for redirects and 443; private sources alone reach databases/internal services, with TLS/authentication still required.", "components": ["aws", "gcp", "azure"], "sources": ["aws:s5594f61a25d6", "gcp:s1c06c98a99c9", "azure:scde5b083d938"], "status": "REASONED"},
    "ssh": {"text": "Restrict 22 to named administrative addresses or documented broker sources, never unrestricted internet ranges.", "components": ["aws", "gcp", "azure"], "sources": ["aws:s5594f61a25d6", "gcp:s1c06c98a99c9", "azure:scde5b083d938"], "status": "REASONED"},
    "ssm": {"text": "SSM Agent dials out and requires no inbound rule; no Session Manager source is listed.", "components": ["aws"], "sources": ["aws:s5594f61a25d6"], "status": "REASONED"},
    "iap": {"text": "IAP needs TCP 22 ingress from 35.235.240.0/20; no IAP source is listed.", "components": ["gcp"], "sources": ["gcp:s1c06c98a99c9"], "status": "REASONED"},
    "bastion": {"text": "Bastion needs target-VM ingress from AzureBastionSubnet; tailnet is another linked alternative. Direct broker sources are absent.", "components": ["azure"], "sources": ["azure:scde5b083d938"], "status": "REASONED"},
    "least-access": {"text": "Start default-deny, add minimum allowances and retire obsolete rules; use security-group references where supported to survive app IP changes.", "components": ["aws", "gcp", "azure"], "sources": ["aws:s5594f61a25d6", "gcp:s1c06c98a99c9", "azure:scde5b083d938"], "status": "REASONED"},
    "docker": {"text": "Cloud and host firewall layers both matter for Docker VMs; the linked Docker guide explains UFW bypass, with no Docker source in this Sources section.", "components": ["aws"], "sources": ["aws:s5594f61a25d6"], "status": "REASONED"},
    "verify-aws": {"text": "Per region inspect all inbound rules, protocol/port ranges, IPv4/IPv6 CIDRs, resolved prefix lists and group references; combinations of narrower ranges can still expose the internet.", "components": ["aws"], "sources": ["aws:s0c459e0aa7a1", "aws:s5594f61a25d6", "aws:sf8813f7c4057"], "status": "REASONED", "verify": [1]},
    "verify-gcp": {"text": "Per project read JSON classic VPC rules, including direction, disabled state, allowed/denied and source ranges; a table can hide whether enforcement is disabled.", "components": ["gcp"], "sources": ["gcp:s1c06c98a99c9", "gcp:s3a90bf10d4eb"], "status": "REASONED", "verify": [1]},
    "gcp-policies": {"text": "Also list/describe hierarchical and network policies and their effective order; the guide says hierarchy precedes VPC and network policies follow by default. Policy-specific sources are absent.", "components": ["gcp"], "sources": ["gcp:s1c06c98a99c9"], "status": "REASONED", "verify": [1]},
    "verify-azure": {"text": "Per NSG include default rules and read JSON direction/access plus singular/plural source prefixes; tables omit arrays and can conceal exposure.", "components": ["azure"], "sources": ["azure:se217f16ce4c1", "azure:scde5b083d938"], "status": "REASONED", "verify": [1]},
    "azure-admin": {"text": "Review Virtual Network Manager security admin rules; the guide says Always allow bypasses NSGs. No security-admin-rule source is listed.", "components": ["azure"], "sources": ["azure:scde5b083d938"], "status": "REASONED", "verify": [1]},
    "verify-ports": {"text": "Outside the admin range, spot-check 22, 3306, 5432, 6379 and 27017; refusal/timeout is expected, while netcat usage errors or silent local failure are inconclusive.", "components": ["aws", "gcp", "azure"], "sources": ["aws:s5594f61a25d6", "gcp:s1c06c98a99c9", "azure:scde5b083d938"], "status": "REASONED", "verify": [2]},
    "verify-complete": {"text": "The spot-check omits RDP 3389 and apps such as 8080/9200; scan all public IPv4/IPv6 ports, distinguish open/closed/filtered, and correlate allowed/disallowed controls with effective rules.", "components": ["aws", "gcp", "azure"], "sources": ["aws:s5594f61a25d6", "gcp:s1c06c98a99c9", "azure:scde5b083d938"], "status": "REASONED", "verify": [2]}
  }
}
---
# Cloud firewalls: security groups and network rules

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| public-front: Allow internet sources only to the front TLS layer on 80 for redirects and 443; private sources alone reach databases/internal services, with TLS/authentication still required. | AWS security groups and CLI unknown; Google Cloud firewall and CLI unknown; Azure NSG and CLI unknown | REASONED |
| ssh: Restrict 22 to named administrative addresses or documented broker sources, never unrestricted internet ranges. | AWS security groups and CLI unknown; Google Cloud firewall and CLI unknown; Azure NSG and CLI unknown | REASONED |
| ssm: SSM Agent dials out and requires no inbound rule; no Session Manager source is listed. | AWS security groups and CLI unknown | REASONED |
| iap: IAP needs TCP 22 ingress from 35.235.240.0/20; no IAP source is listed. | Google Cloud firewall and CLI unknown | REASONED |
| bastion: Bastion needs target-VM ingress from AzureBastionSubnet; tailnet is another linked alternative. Direct broker sources are absent. | Azure NSG and CLI unknown | REASONED |
| least-access: Start default-deny, add minimum allowances and retire obsolete rules; use security-group references where supported to survive app IP changes. | AWS security groups and CLI unknown; Google Cloud firewall and CLI unknown; Azure NSG and CLI unknown | REASONED |
| docker: Cloud and host firewall layers both matter for Docker VMs; the linked Docker guide explains UFW bypass, with no Docker source in this Sources section. | AWS security groups and CLI unknown | REASONED |
| verify-aws: Per region inspect all inbound rules, protocol/port ranges, IPv4/IPv6 CIDRs, resolved prefix lists and group references; combinations of narrower ranges can still expose the internet. | AWS security groups and CLI unknown | REASONED |
| verify-gcp: Per project read JSON classic VPC rules, including direction, disabled state, allowed/denied and source ranges; a table can hide whether enforcement is disabled. | Google Cloud firewall and CLI unknown | REASONED |
| gcp-policies: Also list/describe hierarchical and network policies and their effective order; the guide says hierarchy precedes VPC and network policies follow by default. Policy-specific sources are absent. | Google Cloud firewall and CLI unknown | REASONED |
| verify-azure: Per NSG include default rules and read JSON direction/access plus singular/plural source prefixes; tables omit arrays and can conceal exposure. | Azure NSG and CLI unknown | REASONED |
| azure-admin: Review Virtual Network Manager security admin rules; the guide says Always allow bypasses NSGs. No security-admin-rule source is listed. | Azure NSG and CLI unknown | REASONED |
| verify-ports: Outside the admin range, spot-check 22, 3306, 5432, 6379 and 27017; refusal/timeout is expected, while netcat usage errors or silent local failure are inconclusive. | AWS security groups and CLI unknown; Google Cloud firewall and CLI unknown; Azure NSG and CLI unknown | REASONED |
| verify-complete: The spot-check omits RDP 3389 and apps such as 8080/9200; scan all public IPv4/IPv6 ports, distinguish open/closed/filtered, and correlate allowed/disallowed controls with effective rules. | AWS security groups and CLI unknown; Google Cloud firewall and CLI unknown; Azure NSG and CLI unknown | REASONED |
<!-- version-basis:end -->

On AWS (security groups), Google Cloud (VPC firewall rules), and Azure (network security groups), the recurring hole is one rule wide open to the world: `0.0.0.0/0` (or `::/0`) on a database, admin, or SSH port, added once to unblock a remote connection and never removed.

## Rules

1. **Public means 80/443 on the TLS layer, nothing else.** Only the load balancer, reverse proxy, or tunnel endpoint accepts traffic from `0.0.0.0/0`, and only on 80 (redirect) and 443.
2. **Databases and internal services accept traffic from private sources only**: the application's security group, subnet, or VPC, never the internet. The per-database guides' TLS and auth still apply on top; the firewall is a layer, not the control.
3. **SSH is not public.** Restrict port 22 to your addresses, or remove the public rule and use brokered access. AWS SSM Session Manager needs no inbound rule at all (its SSM Agent dials out to the SSM service); GCP Identity-Aware Proxy still needs an ingress allow for TCP 22 from the IAP range `35.235.240.0/20`; Azure Bastion needs the target VM to allow inbound from the `AzureBastionSubnet`; or use a tailnet ([tailscale.md](tailscale.md)). Those broker sources are scoped ranges, not the internet. Then harden the host per [host.md](host.md).
4. **Default deny, explicit allow.** Start from no inbound rules and add the minimum; review rules whenever a service is retired. Reference security-group IDs rather than IP ranges where the provider supports it, so app-to-database access survives IP changes without widening.
5. **Both layers matter on VMs running Docker**: the cloud firewall and the host's rules, remembering that published container ports bypass host UFW ([docker.md](docker.md)).

## Verify

Enumerate every inbound rule, then, for each one whose source reaches the internet, confirm that the destination port is 80 or 443 on the front layer, nothing else. Rule 3's administrative SSH access is the one other source that may reach 22, and it is a named address or a documented broker range (an IAP `35.235.240.0/20` rule, or an Azure Bastion subnet rule, is expected), never `0.0.0.0/0`. These commands list rather than select, because no filter catches the exposure class.

REASONED: cloud-rule inventory and external reachability checks; no exposed/fixed run is recorded in this guide. Expectations follow the cited provider rule documentation; this read-only review has no authorized cloud accounts or allowed/disallowed probe hosts.

```bash
# AWS, once per region. Every rule, not a selection: no filter catches the exposure class, because
# 0.0.0.0/1 together with 128.0.0.0/1 admits every IPv4 address while matching neither literal, and
# a source can be a prefix list or another security group instead of a CIDR.
aws ec2 describe-security-group-rules \
  --query "SecurityGroupRules[].{Group:GroupId,Egress:IsEgress,Proto:IpProtocol,From:FromPort,To:ToPort,V4:CidrIpv4,V6:CidrIpv6,Prefix:PrefixListId,SG:ReferencedGroupInfo.GroupId}" \
  --output table
# read every row whose Egress column reads False. Its source must be a private CIDR, a security
# group, a prefix list you have resolved and trust, or, where the destination port is 80 or 443,
# the internet. A public source on any other port is a finding, except the single administrative
# address rule 3 allows on 22. Rows reading True
# are outbound, a separate question.

# Google Cloud, once per project. Whole records, because a table projection drops the enforcement
# state: an enforced world-open rule and the same rule with "disabled": true project identically.
gcloud compute firewall-rules list --format=json
# for each entry with "direction": "INGRESS", "disabled": false and an "allowed" list, work out what
# its "sourceRanges" actually reach, by the same reasoning as the AWS command above: 0.0.0.0/0 and
# ::/0 are the obvious cases, and so is any set of ranges that together cover the internet. An entry
# with "denied" restricts rather than exposes.
# firewall-rules list returns ONLY classic VPC rules; GCP also enforces firewall policies, which this misses:
gcloud compute firewall-policies list --organization=REPLACE_WITH_ORG_ID   # or --folder=...; hierarchical policies
gcloud compute network-firewall-policies list                              # global and regional network policies in this project
# inspect each policy's rules with its `describe` subcommand (--format=json). Hierarchical policies are evaluated
# before VPC rules and network policies after them by default, so read the effective order and the matching rule:
# a policy allow with an internet source can expose the port even when the VPC list above is clean, unless an earlier rule denies it.

# Azure, once per network security group. JSON, not a table: the table formatter omits array-valued
# columns, so a rule carrying sourceAddressPrefixes rather than sourceAddressPrefix would print an
# empty cell in the exposed state and the safe state alike. --include-default because the platform's
# own rules are inbound rules too, and this step claims to enumerate every one.
az network nsg rule list \
  --resource-group REPLACE_WITH_RESOURCE_GROUP --nsg-name REPLACE_WITH_NSG_NAME \
  --include-default --output json
# for each rule with "direction": "Inbound" and "access": "Allow", work out what its
# "sourceAddressPrefix" and "sourceAddressPrefixes" actually reach: "*", "Internet", "0.0.0.0/0" and
# "::/0" are the obvious cases, and so is any set of ranges that together cover the internet.
# NSG rules are not the whole story: Azure Virtual Network Manager security admin rules are evaluated BEFORE the
# NSG, and an "Always allow" admin rule sends traffic straight to the resource, bypassing the NSG. If your tenant
# uses a network manager, also review its security admin rules (they do not appear in `nsg rule list`), or an NSG
# that reads safe here can still be overridden into exposure.
```

- From an address outside the range you administer from:

  REASONED: cloud-rule inventory and external reachability checks; no exposed/fixed run is recorded in this guide. Expectations follow the cited provider rule documentation; this read-only review has no authorized cloud accounts or allowed/disallowed probe hosts.

  ```bash
  (                                       # a subshell, so your own script arguments are untouched
    set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'   # replace inside the quotes, keeping them
    [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
    shift
    [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
    case "$1" in
      *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
      *) for p in 22 3306 5432 6379 27017; do nc -vz -w 3 "$1" "$p"; done ;;
    esac
  )
  ```

  Each port must report a refused or timed-out connection; a usage error from `nc` (some netcat variants take one port or a range per invocation) is not a passing result, and neither is exit 1 with no output at all, which is what a denied local socket looks like: in both cases nothing reached the network, so the check is inconclusive rather than passed.
- The `nc` list above is a non-exhaustive spot-check (it omits RDP 3389 and application ports such as 8080 or 9200), and a refused or timed-out port only means nothing answered from here, not that the cloud firewall denies it (an allowed port with no listener refuses too). The strongest reachability test is a full-range external scan of every public IPv4 and IPv6 address (for example with nmap, against your own infrastructure only) from a disallowed source: distinguish open, closed, and filtered, since a closed or refused port is not proof the firewall denies it (a port with no listener also reads closed). For each restricted service, confirm it is reachable from its allowed source and unreachable from a disallowed one, and correlate that with the effective firewall rules before crediting the block to the cloud firewall.

## Sources (checked September 2026)

- AWS CLI `describe-security-group-rules` (the `IsEgress`, `CidrIpv4`, `CidrIpv6`, `FromPort` and `ToPort` fields): https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-security-group-rules.html
- AWS security group rules (`0.0.0.0/0` as every IPv4 address): https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html
- Google Cloud VPC firewall rules, including the `gcloud compute firewall-rules list --format` projection used above: https://docs.cloud.google.com/firewall/docs/using-firewalls
- Azure CLI `az network nsg rule list`: https://learn.microsoft.com/en-us/cli/azure/network/nsg/rule
- Azure network security group rule properties (`direction`, `access`, `sourceAddressPrefix`, `sourceAddressPrefixes`): https://learn.microsoft.com/en-us/rest/api/virtualnetwork/network-security-groups/get
- AWS managed prefix lists (a rule source that is neither a CIDR nor a security group): https://docs.aws.amazon.com/vpc/latest/userguide/managed-prefix-lists.html
- gcloud output formats, for the `json` format value used above: https://docs.cloud.google.com/sdk/gcloud/reference/topic/formats
