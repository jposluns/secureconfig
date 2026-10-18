---
version_basis: {
  "schema": 1,
  "checked": "2026-10-18",
  "documentation_checked": "2026-09",
  "body_sha256": "9a8092c4ccf44cfe39dab7d3a43fcb2fa0b0be1a5e61a4b07b3d2575860bca57",
  "components": {
    "aws": {
      "name": "AWS security groups and CLI",
      "basis": "unknown",
      "sources": {
        "s0c459e0aa7a1": "https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-security-group-rules.html",
        "s5594f61a25d6": "https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html",
        "sf8813f7c4057": "https://docs.aws.amazon.com/vpc/latest/userguide/managed-prefix-lists.html",
        "s06a2a8e07062": "https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-getting-started-enable-ssh-connections.html#session-manager-getting-started-enable-ssh-connections",
        "s0f77b30546ee": "https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-prerequisites.html#session-manager-prerequisites"
      }
    },
    "gcp": {
      "name": "Google Cloud firewall and CLI",
      "basis": "unknown",
      "sources": {
        "s1c06c98a99c9": "https://docs.cloud.google.com/firewall/docs/using-firewalls",
        "s3a90bf10d4eb": "https://docs.cloud.google.com/sdk/gcloud/reference/topic/formats",
        "s68e82eab648c": "https://docs.cloud.google.com/firewall/docs/firewall-policies-overview#regional_network_firewall_policies",
        "s633352524069": "https://docs.cloud.google.com/firewall/docs/firewall-policies#resource_hierarchy",
        "sbfb2e25c9059": "https://docs.cloud.google.com/sdk/gcloud/reference/compute/firewall-policies/list",
        "s12d2856bf552": "https://docs.cloud.google.com/sdk/gcloud/reference/compute/firewall-policies/describe",
        "sef4965908f7b": "https://docs.cloud.google.com/sdk/gcloud/reference/compute/network-firewall-policies/list",
        "s652edf39de2a": "https://docs.cloud.google.com/sdk/gcloud/reference/compute/network-firewall-policies/describe",
        "s57189bff8b8f": "https://docs.cloud.google.com/sdk/gcloud/reference/compute/firewall-rules/list",
        "sd9ee642a0bff": "https://docs.cloud.google.com/firewall/docs/firewall-policies-rule-eval-order",
        "s7e6eda97f950": "https://docs.cloud.google.com/iap/docs/using-tcp-forwarding#create-firewall-rule"
      }
    },
    "docker-docs": {
      "name": "Docker Engine networking documentation",
      "basis": "4e9a5751518ed8223a8dcde53693badddd72604f",
      "sources": {
        "sb5ca9f87b1f3": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/packet-filtering-firewalls.md#L90-L102"
      }
    },
    "azure": {
      "name": "Azure NSG and CLI",
      "basis": "unknown",
      "sources": {
        "se217f16ce4c1": "https://learn.microsoft.com/en-us/cli/azure/network/nsg/rule",
        "scde5b083d938": "https://learn.microsoft.com/en-us/rest/api/virtualnetwork/network-security-groups/get"
      }
    },
    "azure-docs": {
      "name": "Azure documentation snapshot",
      "basis": "8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f",
      "sources": {
        "s6d46120d991b": "https://github.com/MicrosoftDocs/azure-docs/blob/8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f/articles/bastion/bastion-nsg.md#L77-L84",
        "s03ca867c4276": "https://github.com/MicrosoftDocs/azure-docs/blob/8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f/articles/virtual-network-manager/concept-security-admins.md#L50-L67",
        "s382379ec555c": "https://github.com/MicrosoftDocs/azure-docs/blob/8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f/articles/virtual-network-manager/how-to-view-applied-configurations.md#L70-L100"
      }
    },
    "tailscale-docs": {
      "name": "Tailscale documentation",
      "basis": "unknown",
      "sources": {
        "scf48029376f6": "https://tailscale.com/docs/reference/faq/firewall-ports",
        "s44f0b2a0a8ba": "https://tailscale.com/docs/features/tailscale-ssh#why-it-matters"
      }
    }
  },
  "claims": {
    "public-front": {"text": "Allow internet sources only to the front TLS layer on 80 for redirects and 443; private sources alone reach databases/internal services, with TLS/authentication still required.", "components": ["aws", "gcp", "azure"], "sources": ["aws:s5594f61a25d6", "gcp:s1c06c98a99c9", "azure:scde5b083d938"], "status": "REASONED"},
    "ssh": {"text": "Restrict 22 to named administrative addresses or documented broker sources, never unrestricted internet ranges.", "components": ["aws", "gcp", "azure"], "sources": ["aws:s5594f61a25d6", "gcp:s1c06c98a99c9", "azure:scde5b083d938"], "status": "REASONED"},
    "ssm": {"text": "SSM SSH uses the agent's outbound TLS connection and needs no inbound port on the managed node; allow outbound HTTPS 443 to the documented Systems Manager endpoints.", "components": ["aws"], "sources": ["aws:s5594f61a25d6", "aws:s06a2a8e07062", "aws:s0f77b30546ee"], "status": "REASONED"},
    "iap": {"text": "IAP requires cloud ingress from 35.235.240.0/20, or 2600:2d00:1:7::/64 for IPv6 VMs, to SSH's default port 22 or its configured port.", "components": ["gcp"], "sources": ["gcp:s1c06c98a99c9", "gcp:s7e6eda97f950"], "status": "REASONED"},
    "bastion": {"text": "Where an NSG is applied to the target VM subnet, Bastion requires an inbound SSH rule on default port 22 or a custom port with Standard or Premium SKU. Microsoft's best practice scopes that rule's source to the AzureBastionSubnet IP range. A tailnet ordinarily needs no inbound internet firewall port, and Tailscale SSH accepts tailnet traffic on port 22. As this guide's advice, check the host firewall for these broker paths; the fetched IAP, Bastion and Tailscale pages do not specify which UFW or firewalld rules, if any, are needed.", "components": ["azure", "azure-docs", "tailscale-docs", "gcp"], "sources": ["azure:scde5b083d938", "azure-docs:s6d46120d991b", "tailscale-docs:scf48029376f6", "tailscale-docs:s44f0b2a0a8ba", "gcp:s7e6eda97f950"], "status": "REASONED"},
    "least-access": {"text": "Start default-deny, add minimum allowances and retire obsolete rules; use security-group references where supported to survive app IP changes.", "components": ["aws", "gcp", "azure"], "sources": ["aws:s5594f61a25d6", "gcp:s1c06c98a99c9", "azure:scde5b083d938"], "status": "REASONED"},
    "docker": {"text": "On VMs running Docker, use both cloud and host firewall layers as this guide's advice; Docker documents that published container traffic bypasses UFW settings, as the linked Docker guide explains.", "components": ["docker-docs"], "sources": ["docker-docs:sb5ca9f87b1f3"], "status": "REASONED"},
    "verify-aws": {"text": "Per region inspect all inbound rules, protocol/port ranges, IPv4/IPv6 CIDRs, resolved prefix lists and group references; combinations of narrower ranges can still expose the internet.", "components": ["aws"], "sources": ["aws:s0c459e0aa7a1", "aws:s5594f61a25d6", "aws:sf8813f7c4057"], "status": "REASONED", "verify": [1]},
    "verify-gcp": {"text": "Per project read JSON classic VPC rules, including direction, disabled state, allowed/denied and source ranges; a table can hide whether enforcement is disabled.", "components": ["gcp"], "sources": ["gcp:s1c06c98a99c9", "gcp:s3a90bf10d4eb"], "status": "REASONED", "verify": [1]},
    "gcp-policies": {"text": "Also list/describe hierarchical and global/regional network policies and read their effective order. Hierarchical policy rules can override or delegate to global network and VPC rules. The VPC network's networkFirewallPolicyEnforcementOrder defaults to AFTER_CLASSIC_FIREWALL: hierarchical and regional system policies, VPC rules, then global and regional network policies; BEFORE_CLASSIC_FIREWALL puts global and regional network policies after hierarchical and regional system policies but before VPC rules. A matching allow or deny stops evaluation; goto_next continues it. As this guide's reasoning, a policy allow with an internet source can expose a port even when the VPC list is clean, unless an earlier rule denies it.", "components": ["gcp"], "sources": ["gcp:s1c06c98a99c9", "gcp:s68e82eab648c", "gcp:s633352524069", "gcp:sbfb2e25c9059", "gcp:s12d2856bf552", "gcp:sef4965908f7b", "gcp:s652edf39de2a", "gcp:s57189bff8b8f", "gcp:sd9ee642a0bff"], "status": "REASONED", "verify": [1]},
    "verify-azure": {"text": "Per NSG include default rules and read JSON direction/access plus singular/plural source prefixes; tables omit arrays and can conceal exposure.", "components": ["azure"], "sources": ["azure:se217f16ce4c1", "azure:scde5b083d938"], "status": "REASONED", "verify": [1]},
    "azure-admin": {"text": "Azure Virtual Network Manager security admin rules run before NSG rules: Allow continues to NSG evaluation, Always Allow bypasses NSG evaluation, and Deny stops traffic. For a target VM whose virtual network has a Virtual Network Manager configuration applied, review its applied rules in the Azure portal; as this guide's advice, when none is applied, the NSG review alone covers that VM. As this guide's reasoning, this check passes when no applied Always Allow from an unauthorized or internet source reaches a restricted port, including SSH's default port 22 or its configured port; any such rule fails even if the NSG list looks safe. This guide has no sourced CLI command to list applied rules.", "components": ["azure", "azure-docs"], "sources": ["azure:scde5b083d938", "azure-docs:s03ca867c4276", "azure-docs:s382379ec555c"], "status": "REASONED", "verify": [1]},
    "verify-ports": {"text": "Outside the admin range, spot-check 22, 3306, 5432, 6379 and 27017; refusal/timeout is expected, while netcat usage errors or silent local failure are inconclusive.", "components": ["aws", "gcp", "azure"], "sources": ["aws:s5594f61a25d6", "gcp:s1c06c98a99c9", "azure:scde5b083d938"], "status": "REASONED", "verify": [2]},
    "verify-complete": {"text": "The spot-check omits RDP 3389 and apps such as 8080/9200; scan all public IPv4/IPv6 ports, distinguish open/closed/filtered, and correlate allowed/disallowed controls with effective rules.", "components": ["aws", "gcp", "azure"], "sources": ["aws:s5594f61a25d6", "gcp:s1c06c98a99c9", "azure:scde5b083d938"], "status": "REASONED", "verify": [2]}
  }
}
---
# Cloud firewalls: security groups and network rules

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-18; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| public-front: Allow internet sources only to the front TLS layer on 80 for redirects and 443; private sources alone reach databases/internal services, with TLS/authentication still required. | AWS security groups and CLI unknown; Google Cloud firewall and CLI unknown; Azure NSG and CLI unknown | REASONED |
| ssh: Restrict 22 to named administrative addresses or documented broker sources, never unrestricted internet ranges. | AWS security groups and CLI unknown; Google Cloud firewall and CLI unknown; Azure NSG and CLI unknown | REASONED |
| ssm: SSM SSH uses the agent's outbound TLS connection and needs no inbound port on the managed node; allow outbound HTTPS 443 to the documented Systems Manager endpoints. | AWS security groups and CLI unknown | REASONED |
| iap: IAP requires cloud ingress from 35.235.240.0/20, or 2600:2d00:1:7::/64 for IPv6 VMs, to SSH's default port 22 or its configured port. | Google Cloud firewall and CLI unknown | REASONED |
| bastion: Where an NSG is applied to the target VM subnet, Bastion requires an inbound SSH rule on default port 22 or a custom port with Standard or Premium SKU. Microsoft's best practice scopes that rule's source to the AzureBastionSubnet IP range. A tailnet ordinarily needs no inbound internet firewall port, and Tailscale SSH accepts tailnet traffic on port 22. As this guide's advice, check the host firewall for these broker paths; the fetched IAP, Bastion and Tailscale pages do not specify which UFW or firewalld rules, if any, are needed. | Azure NSG and CLI unknown; Azure documentation snapshot 8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f; Tailscale documentation unknown; Google Cloud firewall and CLI unknown | REASONED |
| least-access: Start default-deny, add minimum allowances and retire obsolete rules; use security-group references where supported to survive app IP changes. | AWS security groups and CLI unknown; Google Cloud firewall and CLI unknown; Azure NSG and CLI unknown | REASONED |
| docker: On VMs running Docker, use both cloud and host firewall layers as this guide's advice; Docker documents that published container traffic bypasses UFW settings, as the linked Docker guide explains. | Docker Engine networking documentation 4e9a5751518ed8223a8dcde53693badddd72604f | REASONED |
| verify-aws: Per region inspect all inbound rules, protocol/port ranges, IPv4/IPv6 CIDRs, resolved prefix lists and group references; combinations of narrower ranges can still expose the internet. | AWS security groups and CLI unknown | REASONED |
| verify-gcp: Per project read JSON classic VPC rules, including direction, disabled state, allowed/denied and source ranges; a table can hide whether enforcement is disabled. | Google Cloud firewall and CLI unknown | REASONED |
| gcp-policies: Also list/describe hierarchical and global/regional network policies and read their effective order. Hierarchical policy rules can override or delegate to global network and VPC rules. The VPC network's networkFirewallPolicyEnforcementOrder defaults to AFTER_CLASSIC_FIREWALL: hierarchical and regional system policies, VPC rules, then global and regional network policies; BEFORE_CLASSIC_FIREWALL puts global and regional network policies after hierarchical and regional system policies but before VPC rules. A matching allow or deny stops evaluation; goto_next continues it. As this guide's reasoning, a policy allow with an internet source can expose a port even when the VPC list is clean, unless an earlier rule denies it. | Google Cloud firewall and CLI unknown | REASONED |
| verify-azure: Per NSG include default rules and read JSON direction/access plus singular/plural source prefixes; tables omit arrays and can conceal exposure. | Azure NSG and CLI unknown | REASONED |
| azure-admin: Azure Virtual Network Manager security admin rules run before NSG rules: Allow continues to NSG evaluation, Always Allow bypasses NSG evaluation, and Deny stops traffic. For a target VM whose virtual network has a Virtual Network Manager configuration applied, review its applied rules in the Azure portal; as this guide's advice, when none is applied, the NSG review alone covers that VM. As this guide's reasoning, this check passes when no applied Always Allow from an unauthorized or internet source reaches a restricted port, including SSH's default port 22 or its configured port; any such rule fails even if the NSG list looks safe. This guide has no sourced CLI command to list applied rules. | Azure NSG and CLI unknown; Azure documentation snapshot 8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f | REASONED |
| verify-ports: Outside the admin range, spot-check 22, 3306, 5432, 6379 and 27017; refusal/timeout is expected, while netcat usage errors or silent local failure are inconclusive. | AWS security groups and CLI unknown; Google Cloud firewall and CLI unknown; Azure NSG and CLI unknown | REASONED |
| verify-complete: The spot-check omits RDP 3389 and apps such as 8080/9200; scan all public IPv4/IPv6 ports, distinguish open/closed/filtered, and correlate allowed/disallowed controls with effective rules. | AWS security groups and CLI unknown; Google Cloud firewall and CLI unknown; Azure NSG and CLI unknown | REASONED |
<!-- version-basis:end -->

On AWS (security groups), Google Cloud (VPC firewall rules), and Azure (network security groups), the recurring hole is one rule wide open to the world: `0.0.0.0/0` (or `::/0`) on a database, admin, or SSH port, added once to unblock a remote connection and never removed.

## Rules

1. **Public means 80/443 on the TLS layer, nothing else.** Only the load balancer, reverse proxy, or tunnel endpoint accepts traffic from `0.0.0.0/0`, and only on 80 (redirect) and 443.
2. **Databases and internal services accept traffic from private sources only**: the application's security group, subnet, or VPC, never the internet. The per-database guides' TLS and auth still apply on top; the firewall is a layer, not the control.
3. **SSH is not public.** Restrict port 22 to your addresses, or remove the public rule and use brokered access. AWS SSM Session Manager SSH uses the SSM Agent's outbound TLS connection to Session Manager endpoints and needs no inbound port on the managed node; allow outbound HTTPS 443 to the documented endpoints. GCP IAP TCP forwarding requires a cloud ingress allow from `35.235.240.0/20` (`2600:2d00:1:7::/64` for IPv6 VMs) to SSH's default port 22 or its configured port; where an NSG is applied to the target VM subnet, Azure Bastion requires an inbound SSH rule on default port 22 or a custom port with Standard or Premium SKU. Microsoft's best practice scopes that rule's source to the `AzureBastionSubnet` IP address range. Or use a tailnet ([tailscale.md](tailscale.md)): Tailscale ordinarily needs no inbound internet firewall port, and Tailscale SSH accepts traffic from the tailnet on port 22. As this guide's reasoning, these broker paths avoid a public SSH rule. As this guide's advice, check the host firewall separately; the fetched IAP, Bastion and Tailscale pages do not specify which UFW or firewalld rules, if any, are needed. Then harden the host per [host.md](host.md).
4. **Default deny, explicit allow.** Start from no inbound rules and add the minimum; review rules whenever a service is retired. Reference security-group IDs rather than IP ranges where the provider supports it, so app-to-database access survives IP changes without widening.
5. **Both layers matter on VMs running Docker**: as this guide's advice, use both the cloud firewall and the host's rules, remembering that Docker documents published container traffic bypassing host UFW settings ([docker.md](docker.md)).

## Verify

REASONED: rule-enumeration scope and the one allowed public pattern, per the cited AWS security group rules, Google Cloud VPC firewall rules, Google firewall policy, evaluation-order and gcloud references, Azure network security group rule properties, the fetched Session Manager, IAP, Bastion and Tailscale pages, and the Azure security-admin rule and applied-rules pages; no authorized AWS, Google Cloud or Azure account is available in the authoring environment, so no rule inventory was read here, while the fenced commands below passed bash -n and ShellCheck 0.11.0 at marking time with no diagnostics. Enumerate every inbound rule, then, for each one whose source reaches the internet, confirm that the destination port is 80 or 443 on the front layer, nothing else. Rule 3's administrative SSH access is the one other source that may reach 22, and it is a named address or a documented broker source (an IAP `35.235.240.0/20` rule, its IPv6 range for IPv6 VMs, or an Azure Bastion inbound SSH rule on the target VM subnet where an NSG is applied, is expected; Microsoft recommends scoping the Bastion source to `AzureBastionSubnet`), never `0.0.0.0/0`. These commands list rather than select, because no filter catches the exposure class.

REASONED: cloud-rule inventory and external reachability checks; no exposed/fixed run is recorded in this guide. Expectations follow the cited provider rule documentation, Google firewall policy and evaluation-order references, and the Azure security-admin rule and applied-rules pages; this read-only review has no authorized cloud accounts or allowed/disallowed probe hosts.

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
# firewall-rules list displays Compute Engine firewall rules in this project; also enumerate the policy resources:
gcloud compute firewall-policies list --organization=REPLACE_WITH_ORG_ID   # repeat with --folder=REPLACE_WITH_FOLDER_ID for each relevant folder
gcloud compute network-firewall-policies list                              # no scope flag lists global and regional policies in this project
# inspect each hierarchical policy with `gcloud compute firewall-policies describe POLICY_ID --format=json`.
# inspect each global network policy with `gcloud compute network-firewall-policies describe POLICY_NAME --global --format=json`;
# for each regional policy, use `gcloud compute network-firewall-policies describe POLICY_NAME --region=REGION --format=json`.
# Hierarchical policy rules can override or delegate to global network and VPC rules. Read the effective order and matching
# rule: as this guide's reasoning, a policy allow with an internet source can expose the port even when the VPC list
# above is clean, unless an earlier rule denies it. Google documents the VPC network's networkFirewallPolicyEnforcementOrder:
# AFTER_CLASSIC_FIREWALL (default) evaluates hierarchical and regional system policies, VPC rules, then global and
# regional network policies; BEFORE_CLASSIC_FIREWALL puts global and regional network policies after hierarchical and
# regional system policies but before VPC rules.
# A matching allow or deny stops evaluation; goto_next continues it. See
# https://docs.cloud.google.com/firewall/docs/firewall-policies-rule-eval-order#determine-rule-evaluation
# and https://docs.cloud.google.com/firewall/docs/firewall-policies-rule-eval-order#default-rule-evaluation

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
# NSG rules are not the whole story: Azure Virtual Network Manager security admin rules run before NSG rules.
# Allow continues to NSG evaluation; Always Allow bypasses it; Deny stops traffic. For a target VM
# whose virtual network has a Virtual Network Manager configuration applied, use the Azure portal:
# Networking > network interface > Support + troubleshooting > Effective security rules, then select
# the Azure Virtual Network Manager to inspect its applied security admin rules.
# As this guide's advice, when none is applied, the NSG review above alone covers that VM.
# As this guide's reasoning, this check passes when no applied Always Allow from an unauthorized or
# internet source reaches a restricted port, including SSH's default port 22 or its configured port.
# Any such rule is a finding even if the NSG list above looks safe; inspect its source, destination,
# action and port.
# The fetched pages give a portal path for applied rules; this guide has no sourced CLI command to list them.
```

- REASONED: disallowed-source port probes and their failure interpretation, per the guide's cited AWS security group rules and Azure network security group rule properties. No authorized cloud endpoints or allowed/disallowed probe hosts are available. bash -n and ShellCheck 0.11.0 exited 0 without diagnostics; original, missing-assignment, short, empty and embedded-placeholder cases printed refusal messages without reaching nc, while a substituted address reached five nc stubs. Live exposed connections and fixed refusals/timeouts remain unobserved; local errors are inconclusive. From an address outside the range you administer from:

  REASONED: cloud-rule inventory and external reachability checks; no exposed/fixed run is recorded in this guide. Expectations follow the cited provider rule documentation and Google firewall policy and evaluation-order references; this read-only review has no authorized cloud accounts or allowed/disallowed probe hosts.

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
- REASONED: complete address/port coverage and allowed/disallowed controls, per the guide's cited AWS security group rules, Google Cloud VPC firewall rules and Azure network security group rule properties. No authorized cloud endpoints or separate source networks are available. The related shell blocks passed bash -n and ShellCheck 0.11.0 without diagnostics; rejected placeholder cases reached no nc stub and a substituted address reached five. No real scan ran. Exposed services answer disallowed sources; fixed services answer only allowed sources, corroborated by effective rules, with unused or failed services remaining inconclusive. The `nc` list above is a non-exhaustive spot-check (it omits RDP 3389 and application ports such as 8080 or 9200), and a refused or timed-out port only means nothing answered from here, not that the cloud firewall denies it (an allowed port with no listener refuses too). The strongest reachability test is a full-range external scan of every public IPv4 and IPv6 address (for example with nmap, against your own infrastructure only) from a disallowed source: distinguish open, closed, and filtered, since a closed or refused port is not proof the firewall denies it (a port with no listener also reads closed). For each restricted service, confirm it is reachable from its allowed source and unreachable from a disallowed one, and correlate that with the effective firewall rules before crediting the block to the cloud firewall.

## Sources (checked September 2026)

- AWS Session Manager SSH tunnel (rolling) (checked October 2026): https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-getting-started-enable-ssh-connections.html#session-manager-getting-started-enable-ssh-connections
- AWS Session Manager managed-node outbound HTTPS prerequisites (rolling) (checked October 2026): https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-prerequisites.html#session-manager-prerequisites
- Google Cloud IAP TCP forwarding firewall source and SSH port (rolling) (checked October 2026): https://docs.cloud.google.com/iap/docs/using-tcp-forwarding#create-firewall-rule
- Azure Bastion target VM subnet NSG rule, at 8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f (checked October 2026): https://github.com/MicrosoftDocs/azure-docs/blob/8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f/articles/bastion/bastion-nsg.md#L77-L84
- Azure security-admin actions and NSG evaluation order, at 8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f (checked October 2026): https://github.com/MicrosoftDocs/azure-docs/blob/8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f/articles/virtual-network-manager/concept-security-admins.md#L50-L67
- Azure portal view of applied VM security-admin rules, at 8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f (checked October 2026): https://github.com/MicrosoftDocs/azure-docs/blob/8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f/articles/virtual-network-manager/how-to-view-applied-configurations.md#L70-L100
- Tailscale firewall ports (rolling) (checked October 2026): https://tailscale.com/docs/reference/faq/firewall-ports
- Tailscale SSH tailnet port 22 (rolling) (checked October 2026): https://tailscale.com/docs/features/tailscale-ssh#why-it-matters
- AWS CLI `describe-security-group-rules` (the `IsEgress`, `CidrIpv4`, `CidrIpv6`, `FromPort` and `ToPort` fields): https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-security-group-rules.html
- AWS security group rules (`0.0.0.0/0` as every IPv4 address): https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html
- Google Cloud VPC firewall rules, including the `gcloud compute firewall-rules list --format` projection used above: https://docs.cloud.google.com/firewall/docs/using-firewalls
- Azure CLI `az network nsg rule list`: https://learn.microsoft.com/en-us/cli/azure/network/nsg/rule
- Azure network security group rule properties (`direction`, `access`, `sourceAddressPrefix`, `sourceAddressPrefixes`): https://learn.microsoft.com/en-us/rest/api/virtualnetwork/network-security-groups/get
- AWS managed prefix lists (a rule source that is neither a CIDR nor a security group): https://docs.aws.amazon.com/vpc/latest/userguide/managed-prefix-lists.html
- gcloud output formats, for the `json` format value used above: https://docs.cloud.google.com/sdk/gcloud/reference/topic/formats
- Docker and UFW published-port traffic, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/packet-filtering-firewalls.md#L90-L102
- Google Cloud regional network firewall policies (rolling) (checked October 2026): https://docs.cloud.google.com/firewall/docs/firewall-policies-overview#regional_network_firewall_policies
- Google Cloud hierarchical policy resource order and delegation to lower-level rules (rolling) (checked October 2026): https://docs.cloud.google.com/firewall/docs/firewall-policies#resource_hierarchy
- gcloud hierarchical policy list syntax (rolling) (checked October 2026): https://docs.cloud.google.com/sdk/gcloud/reference/compute/firewall-policies/list
- gcloud hierarchical policy describe syntax (rolling) (checked October 2026): https://docs.cloud.google.com/sdk/gcloud/reference/compute/firewall-policies/describe
- gcloud network policy list scope, including unflagged global and regional enumeration (rolling) (checked October 2026): https://docs.cloud.google.com/sdk/gcloud/reference/compute/network-firewall-policies/list
- gcloud network policy describe global/region syntax (rolling) (checked October 2026): https://docs.cloud.google.com/sdk/gcloud/reference/compute/network-firewall-policies/describe
- gcloud Compute Engine firewall-rule list project scope (rolling) (checked October 2026): https://docs.cloud.google.com/sdk/gcloud/reference/compute/firewall-rules/list
- Google Cloud firewall policy evaluation order and enforcement setting (rolling) (checked October 2026): https://docs.cloud.google.com/firewall/docs/firewall-policies-rule-eval-order
