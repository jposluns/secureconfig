# Cloud firewalls: security groups and network rules

On AWS (security groups), Google Cloud (VPC firewall rules), and Azure (network security groups), the recurring hole is one rule wide open to the world: `0.0.0.0/0` (or `::/0`) on a database, admin, or SSH port, added once to unblock a remote connection and never removed.

## Rules

1. **Public means 80/443 on the TLS layer, nothing else.** Only the load balancer, reverse proxy, or tunnel endpoint accepts traffic from `0.0.0.0/0`, and only on 80 (redirect) and 443.
2. **Databases and internal services accept traffic from private sources only**: the application's security group, subnet, or VPC, never the internet. The per-database guides' TLS and auth still apply on top; the firewall is a layer, not the control.
3. **SSH is not public.** Restrict port 22 to your addresses, or remove the inbound rule entirely and use the provider's brokered access (AWS SSM Session Manager, GCP Identity-Aware Proxy, Azure Bastion) or a tailnet ([tailscale.md](tailscale.md)). Then harden the host per [host.md](host.md).
4. **Default deny, explicit allow.** Start from no inbound rules and add the minimum; review rules whenever a service is retired. Reference security-group IDs rather than IP ranges where the provider supports it, so app-to-database access survives IP changes without widening.
5. **Both layers matter on VMs running Docker**: the cloud firewall and the host's rules, remembering that published container ports bypass host UFW ([docker.md](docker.md)).

## Verify

Enumerate every inbound rule, then confirm that any whose source reaches the internet is 80 or 443 on the front layer, nothing else. These commands list rather than select, because no filter catches the exposure class.

```bash
# AWS, once per region. Every rule, not a selection: no filter catches the exposure class, because
# 0.0.0.0/1 together with 128.0.0.0/1 admits every IPv4 address while matching neither literal, and
# a source can be a prefix list or another security group instead of a CIDR.
aws ec2 describe-security-group-rules \
  --query "SecurityGroupRules[].{Group:GroupId,Egress:IsEgress,Proto:IpProtocol,From:FromPort,To:ToPort,V4:CidrIpv4,V6:CidrIpv6,Prefix:PrefixListId,SG:ReferencedGroupInfo.GroupId}" \
  --output table
# read every row whose Egress column reads False. Its source must be 80 or 443 on the front layer,
# a private CIDR, a security group, or a prefix list you have resolved and trust. Rows reading True
# are outbound, a separate question.

# Google Cloud, once per project. Whole records, because a table projection drops the enforcement
# state: an enforced world-open rule and the same rule with "disabled": true project identically.
gcloud compute firewall-rules list --format=json
# for each entry with "direction": "INGRESS" and "disabled": false, "sourceRanges" must not hold
# 0.0.0.0/0 or ::/0 except where "allowed" is only tcp:80 and tcp:443 on the front layer

# Azure, once per network security group. JSON, not a table: the table formatter omits array-valued
# columns, so a rule carrying sourceAddressPrefixes rather than sourceAddressPrefix would print an
# empty cell in the exposed state and the safe state alike.
az network nsg rule list \
  --resource-group REPLACE_WITH_RESOURCE_GROUP --nsg-name REPLACE_WITH_NSG_NAME --output json
# for each rule with "direction": "Inbound" and "access": "Allow", neither "sourceAddressPrefix" nor
# any entry in "sourceAddressPrefixes" may be "*", "Internet", "0.0.0.0/0" or "::/0" except on 80 and 443
```

- From an address outside the range you administer from: `for p in 22 3306 5432 6379 27017; do nc -vz -w 3 203.0.113.10 "$p"; done   # every line must fail to connect`. Each port must report a refused or timed-out connection; a usage error from `nc` (some netcat variants take one port or a range per invocation) is not a passing result.
- An external scan of the public IP (for example with nmap, against your own infrastructure only) shows only the intended ports.

## Sources (checked September 2026)

- AWS CLI `describe-security-group-rules` (the `IsEgress`, `CidrIpv4`, `CidrIpv6`, `FromPort` and `ToPort` fields): https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-security-group-rules.html
- AWS security group rules (`0.0.0.0/0` as every IPv4 address): https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html
- Google Cloud VPC firewall rules, including the `gcloud compute firewall-rules list --format` projection used above: https://docs.cloud.google.com/firewall/docs/using-firewalls
- Azure CLI `az network nsg rule list`: https://learn.microsoft.com/en-us/cli/azure/network/nsg/rule
- Azure network security group rule properties (`direction`, `access`, `sourceAddressPrefix`, `sourceAddressPrefixes`): https://learn.microsoft.com/en-us/rest/api/virtualnetwork/network-security-groups/get
- AWS managed prefix lists (a rule source that is neither a CIDR nor a security group): https://docs.aws.amazon.com/vpc/latest/userguide/managed-prefix-lists.html
