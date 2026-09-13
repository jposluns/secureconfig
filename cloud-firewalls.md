# Cloud firewalls: security groups and network rules

On AWS (security groups), Google Cloud (VPC firewall rules), and Azure (network security groups), the recurring hole is one rule wide open to the world: `0.0.0.0/0` (or `::/0`) on a database, admin, or SSH port, added once to unblock a remote connection and never removed.

## Rules

1. **Public means 80/443 on the TLS layer, nothing else.** Only the load balancer, reverse proxy, or tunnel endpoint accepts traffic from `0.0.0.0/0`, and only on 80 (redirect) and 443.
2. **Databases and internal services accept traffic from private sources only**: the application's security group, subnet, or VPC, never the internet. The per-database guides' TLS and auth still apply on top; the firewall is a layer, not the control.
3. **SSH is not public.** Restrict port 22 to your addresses, or remove the inbound rule entirely and use the provider's brokered access (AWS SSM Session Manager, GCP Identity-Aware Proxy, Azure Bastion) or a tailnet ([tailscale.md](tailscale.md)). Then harden the host per [host.md](host.md).
4. **Default deny, explicit allow.** Start from no inbound rules and add the minimum; review rules whenever a service is retired. Reference security-group IDs rather than IP ranges where the provider supports it, so app-to-database access survives IP changes without widening.
5. **Both layers matter on VMs running Docker**: the cloud firewall and the host's rules, remembering that published container ports bypass host UFW ([docker.md](docker.md)).

## Verify

Enumerate every inbound rule whose source is the whole internet, and confirm that each one is 80 or 443 on the front layer, nothing else.

```bash
# AWS, once per region. A world-open rule always carries 0.0.0.0/0 or ::/0, so this hides none of them.
aws ec2 describe-security-group-rules \
  --query 'SecurityGroupRules[?IsEgress==`false` && (CidrIpv4==`0.0.0.0/0` || CidrIpv6==`::/0`)].{Group:GroupId,Proto:IpProtocol,From:FromPort,To:ToPort,V4:CidrIpv4,V6:CidrIpv6}' \
  --output table

# Google Cloud, once per project. No filter, so no rule can be hidden by one.
gcloud compute firewall-rules list --sort-by priority \
  --format="table(name, network, direction, priority, sourceRanges.list():label=SRC_RANGES, allowed[].map().firewall_rule().list():label=ALLOW)"
# every INGRESS row whose SRC_RANGES holds 0.0.0.0/0 or ::/0 must allow only tcp:80 and tcp:443

# Azure, once per network security group. Lists every inbound allow, not only the open ones.
az network nsg rule list \
  --resource-group REPLACE_WITH_RESOURCE_GROUP --nsg-name REPLACE_WITH_NSG_NAME \
  --query "[?direction=='Inbound' && access=='Allow'].{Name:name,Prio:priority,Proto:protocol,Src:sourceAddressPrefix,Ports:destinationPortRange}" \
  --output table
# a rule may instead carry sourceAddressPrefixes and destinationPortRanges (plural); re-run with
# those names where Src or Ports comes back empty. No source may be '*', 'Internet', 0.0.0.0/0 or
# ::/0 except on 80 and 443.
```

- From an outside network: `for p in 22 3306 5432 6379 27017; do nc -vz -w 3 203.0.113.10 "$p"; done   # every line must fail to connect`. Each port must report a refused or timed-out connection; a usage error from `nc` (some netcat variants take one port or a range per invocation) is not a passing result.
- An external scan of the public IP (for example with nmap, against your own infrastructure only) shows only the intended ports.

## Sources (checked September 2026)

- AWS CLI `describe-security-group-rules` (the `IsEgress`, `CidrIpv4`, `CidrIpv6`, `FromPort` and `ToPort` fields): https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-security-group-rules.html
- AWS security group rules (`0.0.0.0/0` as every IPv4 address): https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html
- Google Cloud VPC firewall rules, including the `gcloud compute firewall-rules list --format` projection used above: https://docs.cloud.google.com/firewall/docs/using-firewalls
- Azure CLI `az network nsg rule list`: https://learn.microsoft.com/en-us/cli/azure/network/nsg/rule
- Azure network security group rule properties (`direction`, `access`, `sourceAddressPrefix`, `sourceAddressPrefixes`): https://learn.microsoft.com/en-us/rest/api/virtualnetwork/network-security-groups/get
