---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "7f657d93a2ca394df96639c25716f2a0e62decbd10eea393ba0a5c06f51f55f7",
  "components": {
    "nmap": {
      "name": "Nmap documentation",
      "basis": "unknown",
      "sources": {
        "sf8404f695ccd": "https://nmap.org/book/man-briefoptions.html",
        "sb7d0e7eb5141": "https://nmap.org/book/man-host-discovery.html"
      }
    },
    "shodan": {
      "name": "Shodan",
      "basis": "unknown",
      "sources": {
        "scf863db67f1e": "https://www.shodan.io/"
      }
    },
    "censys": {
      "name": "Censys",
      "basis": "unknown",
      "sources": {
        "s1e64a007a91f": "https://censys.com/"
      }
    },
    "vercel": {
      "name": "Vercel Deployment Protection",
      "basis": "unknown",
      "sources": {
        "se6089d5c4e96": "https://vercel.com/docs/deployment-protection",
        "s7836e043434a": "https://vercel.com/changelog/protect-production-deployments-for-free-on-every-plan"
      }
    },
    "access": {
      "name": "Cloudflare Access policies",
      "basis": "unknown",
      "sources": {
        "sc007294b64a0": "https://developers.cloudflare.com/cloudflare-one/access-controls/policies/"
      }
    },
    "dns": {
      "name": "BIND dig documentation",
      "basis": "unknown",
      "sources": {
        "se6d352e0a4fa": "https://bind9.readthedocs.io/en/latest/manpages.html"
      }
    }
  },
  "claims": {
    "outside": {"text": "Run exposure checks from a second network; host-local curl and ss do not establish outside reachability or platform firewall behaviour.", "components": ["nmap"], "sources": ["nmap:sf8404f695ccd", "nmap:sb7d0e7eb5141"], "status": "REASONED"},
    "tcp-scan": {"text": "Sweep authorized hosts with nmap -Pn -p-; the guide also gives an nc port loop. No nc reference is recorded in Sources.", "components": ["nmap"], "sources": ["nmap:sf8404f695ccd", "nmap:sb7d0e7eb5141"], "status": "REASONED"},
    "udp-scan": {"text": "The full port sweep is TCP only; inventory UDP services and probe their ports separately with nmap -sU.", "components": ["nmap"], "sources": ["nmap:sf8404f695ccd"], "status": "REASONED"},
    "all-addresses": {"text": "Check public IPv4, public IPv6 and platform URLs as well as the custom domain; one address cannot establish coverage of the others.", "components": ["nmap", "vercel"], "sources": ["nmap:sf8404f695ccd", "vercel:se6089d5c4e96"], "status": "REASONED"},
    "passive-index": {"text": "Cross-reference Shodan and Censys indexes for previously indexed exposure; indexed observations are not a fresh direct scan.", "components": ["shodan", "censys"], "sources": ["shodan:scf863db67f1e", "censys:s1e64a007a91f"], "status": "REASONED"},
    "initialize-secrets": {"text": "Create owner/admin credentials and signing secrets before opening access. Access-policy citation is context only; application bootstrap sources are not recorded.", "components": ["access"], "sources": ["access:sc007294b64a0"], "status": "REASONED"},
    "registration": {"text": "Disable open registration or restrict it to an allowlisted domain before exposure. Access-policy citation is context only; application registration sources are not recorded.", "components": ["access"], "sources": ["access:sc007294b64a0"], "status": "REASONED"},
    "fronting-order": {"text": "Install TLS and proxy authentication before opening network access. Access policies support the gate; TLS and deployment-order sources are not recorded.", "components": ["access"], "sources": ["access:sc007294b64a0"], "status": "REASONED"},
    "setup-route": {"text": "After initialization, restart and confirm the setup URL refuses a second admin. Access-policy citation is context only; setup-route behaviour is not sourced.", "components": ["access"], "sources": ["access:sc007294b64a0"], "status": "REASONED"},
    "preview-standard": {"text": "Vercel Standard Protection is available on every plan and gates previews and generated deployment URLs while leaving the production domain open.", "components": ["vercel"], "sources": ["vercel:se6089d5c4e96"], "status": "REASONED"},
    "preview-all": {"text": "All Deployments also protects production; pairing it with Vercel Authentication became free on every plan on 9 September 2026, with no paid add-on.", "components": ["vercel"], "sources": ["vercel:se6089d5c4e96", "vercel:s7836e043434a"], "status": "REASONED"},
    "preview-gate": {"text": "Apply a fronting gate such as a Cloudflare Access policy to preview hostnames the platform gate does not cover.", "components": ["access", "vercel"], "sources": ["access:sc007294b64a0", "vercel:se6089d5c4e96"], "status": "REASONED"},
    "clone-secrets": {"text": "Treat clone data like production and rotate inherited credentials if the clone is less trusted. Access-policy citation is context only; clone credential lifecycle is not sourced.", "components": ["access"], "sources": ["access:sc007294b64a0"], "status": "REASONED"},
    "dns-retirement": {"text": "Remove CNAME or A/AAAA records before releasing the resource; retain it through the old TTL and authoritative removal checks. dig supports DNS inspection; takeover and resource-retention guidance has no dedicated source.", "components": ["dns"], "sources": ["dns:se6d352e0a4fa"], "status": "REASONED"},
    "retire-credentials": {"text": "After DNS retirement revoke deployment access policies, API/service credentials and dedicated database users. Access-policy citation covers only the fronting context.", "components": ["access"], "sources": ["access:sc007294b64a0"], "status": "REASONED"},
    "reverify": {"text": "Repeat outside scans and negative auth tests after upgrades, restores or network/auth changes; restored defaults can reopen exposure. Nmap supports the scan, not application restore behaviour.", "components": ["nmap"], "sources": ["nmap:sf8404f695ccd", "nmap:sb7d0e7eb5141"], "status": "REASONED"},
    "certificate-monitor": {"text": "Monitor certificate expiry externally; a local certbot renewal dry run does not prove the last production renewal succeeded. Nmap is outside-check context only; OpenSSL and Certbot sources are not recorded.", "components": ["nmap"], "sources": ["nmap:sf8404f695ccd"], "status": "REASONED"},
    "offboarding": {"text": "Revoke identity membership, proxy/app sessions, personal tokens, API keys and second factors; account for cached-session expiry. Access-policy citation does not establish each layer or its revocation delay.", "components": ["access"], "sources": ["access:sc007294b64a0"], "status": "REASONED"},
    "verify-ipv4": {"text": "From another network, nmap -Pn -p- should find only intended TCP ports; unintended open ports fail, and errors or an unexecuted scan are inconclusive.", "components": ["nmap"], "sources": ["nmap:sf8404f695ccd", "nmap:sb7d0e7eb5141"], "status": "REASONED", "verify": [1]},
    "verify-ipv6": {"text": "Repeat the full TCP sweep over the public IPv6 address with -6; a scan that did not run is inconclusive.", "components": ["nmap"], "sources": ["nmap:sf8404f695ccd", "nmap:sb7d0e7eb5141"], "status": "REASONED", "verify": [1]},
    "verify-dns": {"text": "curl failure does not prove DNS removal; resolver A/AAAA/CNAME answers need investigation and empty output is inconclusive. Check every authoritative server with +norecurse for NXDOMAIN or NOERROR/NODATA without CNAME; SERVFAIL, referral and timeout are inconclusive.", "components": ["dns"], "sources": ["dns:se6d352e0a4fa"], "status": "REASONED", "verify": [1]},
    "verify-certificate": {"text": "The scheduled external s_client probe checks hostname and verification errors and pipes the certificate to x509 -enddate. No OpenSSL source or observed outcome is recorded; Nmap is outside-check context only.", "components": ["nmap"], "sources": ["nmap:sf8404f695ccd"], "status": "REASONED", "verify": [1]}
  }
}
---
# Deploying safely over time: verify from outside, safe order, previews, teardown

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| outside: Run exposure checks from a second network; host-local curl and ss do not establish outside reachability or platform firewall behaviour. | Nmap documentation unknown | REASONED |
| tcp-scan: Sweep authorized hosts with nmap -Pn -p-; the guide also gives an nc port loop. No nc reference is recorded in Sources. | Nmap documentation unknown | REASONED |
| udp-scan: The full port sweep is TCP only; inventory UDP services and probe their ports separately with nmap -sU. | Nmap documentation unknown | REASONED |
| all-addresses: Check public IPv4, public IPv6 and platform URLs as well as the custom domain; one address cannot establish coverage of the others. | Nmap documentation unknown; Vercel Deployment Protection unknown | REASONED |
| passive-index: Cross-reference Shodan and Censys indexes for previously indexed exposure; indexed observations are not a fresh direct scan. | Shodan unknown; Censys unknown | REASONED |
| initialize-secrets: Create owner/admin credentials and signing secrets before opening access. Access-policy citation is context only; application bootstrap sources are not recorded. | Cloudflare Access policies unknown | REASONED |
| registration: Disable open registration or restrict it to an allowlisted domain before exposure. Access-policy citation is context only; application registration sources are not recorded. | Cloudflare Access policies unknown | REASONED |
| fronting-order: Install TLS and proxy authentication before opening network access. Access policies support the gate; TLS and deployment-order sources are not recorded. | Cloudflare Access policies unknown | REASONED |
| setup-route: After initialization, restart and confirm the setup URL refuses a second admin. Access-policy citation is context only; setup-route behaviour is not sourced. | Cloudflare Access policies unknown | REASONED |
| preview-standard: Vercel Standard Protection is available on every plan and gates previews and generated deployment URLs while leaving the production domain open. | Vercel Deployment Protection unknown | REASONED |
| preview-all: All Deployments also protects production; pairing it with Vercel Authentication became free on every plan on 9 September 2026, with no paid add-on. | Vercel Deployment Protection unknown | REASONED |
| preview-gate: Apply a fronting gate such as a Cloudflare Access policy to preview hostnames the platform gate does not cover. | Cloudflare Access policies unknown; Vercel Deployment Protection unknown | REASONED |
| clone-secrets: Treat clone data like production and rotate inherited credentials if the clone is less trusted. Access-policy citation is context only; clone credential lifecycle is not sourced. | Cloudflare Access policies unknown | REASONED |
| dns-retirement: Remove CNAME or A/AAAA records before releasing the resource; retain it through the old TTL and authoritative removal checks. dig supports DNS inspection; takeover and resource-retention guidance has no dedicated source. | BIND dig documentation unknown | REASONED |
| retire-credentials: After DNS retirement revoke deployment access policies, API/service credentials and dedicated database users. Access-policy citation covers only the fronting context. | Cloudflare Access policies unknown | REASONED |
| reverify: Repeat outside scans and negative auth tests after upgrades, restores or network/auth changes; restored defaults can reopen exposure. Nmap supports the scan, not application restore behaviour. | Nmap documentation unknown | REASONED |
| certificate-monitor: Monitor certificate expiry externally; a local certbot renewal dry run does not prove the last production renewal succeeded. Nmap is outside-check context only; OpenSSL and Certbot sources are not recorded. | Nmap documentation unknown | REASONED |
| offboarding: Revoke identity membership, proxy/app sessions, personal tokens, API keys and second factors; account for cached-session expiry. Access-policy citation does not establish each layer or its revocation delay. | Cloudflare Access policies unknown | REASONED |
| verify-ipv4: From another network, nmap -Pn -p- should find only intended TCP ports; unintended open ports fail, and errors or an unexecuted scan are inconclusive. | Nmap documentation unknown | REASONED |
| verify-ipv6: Repeat the full TCP sweep over the public IPv6 address with -6; a scan that did not run is inconclusive. | Nmap documentation unknown | REASONED |
| verify-dns: curl failure does not prove DNS removal; resolver A/AAAA/CNAME answers need investigation and empty output is inconclusive. Check every authoritative server with +norecurse for NXDOMAIN or NOERROR/NODATA without CNAME; SERVFAIL, referral and timeout are inconclusive. | BIND dig documentation unknown | REASONED |
| verify-certificate: The scheduled external s_client probe checks hostname and verification errors and pipes the certificate to x509 -enddate. No OpenSSL source or observed outcome is recorded; Nmap is outside-check context only. | Nmap documentation unknown | REASONED |
<!-- version-basis:end -->

This repository's per-service guides check TLS, binding, and authentication from inside the host and at the moment you set them up. Real exposure is judged from outside the host, and it drifts: a preview URL, a restored backup, or an upgrade can reopen something already closed. This guide is the lifecycle layer around the per-service checks.

## 1. Verify from outside, not just from the host

A `curl` or `ss -tlnp` run on the host itself cannot see a firewall the host does not know about, or a platform-level bypass like Docker's iptables rules ([docker.md](docker.md)). Verify from a second network: a phone hotspot, a cloud shell, or a second VM.

- Port-by-port: `for p in 22 80 443 3000 5432 6379 27017; do nc -vz -w 3 REPLACE_WITH_YOUR_PUBLIC_IP "$p"; done`, or a full sweep, `nmap -Pn -p- REPLACE_WITH_YOUR_PUBLIC_IP` (per the nmap reference, which documents `-p-` and `-p 1-65535` as equivalent port-range syntax; this sweeps TCP only, so inventory and separately probe any UDP service with `nmap -sU` on its ports; only scan hosts you own or are authorized to test).
- Check every address the service actually has, not just the one you remember configuring: the public IPv4 address, the public IPv6 address if the host has one, and any platform-assigned URL alongside your custom domain (a PaaS default subdomain, per [paas.md](paas.md), often stays reachable even when the custom domain is fronted). A scan of one address that misses the others is not a clean result, it is an incomplete one.
- Cross-reference what is already indexed about your IP with a passive internet-wide scanner such as Shodan or Censys; both build a continuously updated index of internet-connected hosts and services, so a stale exposure can show up there before you find it yourself ([cloud-firewalls.md](cloud-firewalls.md) covers the firewall rules this is checking).

## 2. Safe initialization order

Sequence a first deployment so nothing is reachable before it is safe to reach:

1. Create the owner or admin account's credentials and any signing secrets (session, JWT, or cookie-signing keys) per [authentication.md](authentication.md).
2. Set the registration policy (disable open self-registration, or restrict it to an allowlisted domain) before the service is reachable.
3. Put the fronting gate in place, TLS and any proxy-level authentication, per [free-certificates.md](free-certificates.md) and the fronting-layer guides.
4. Only then open network access.

The common failure this order prevents: an unclaimed setup wizard is a race to become admin, open to whoever reaches it first. After that, confirm the setup route itself is closed: restart the service and try hitting the initial-setup URL again; it must refuse to mint a second admin, not silently succeed.

## 3. Previews and clones get production posture

A preview deployment or a database clone is not lower stakes just because it is temporary. Vercel's Deployment Protection illustrates the gap: Standard Protection, available on every plan, gates preview and generated deployment URLs but leaves the production domain open by default; the All Deployments scope closes that gap too, and Vercel's September 9, 2026 change made pairing it with Vercel Authentication free on every plan rather than Pro and Enterprise only ([paas.md](paas.md); per Vercel's Deployment Protection changelog of 9 September 2026 and its current Deployment Protection reference, which states that Vercel Authentication for All Deployments does not require a paid add-on). Where the platform's own gate does not cover a hostname, front it the same way as production, for example a Cloudflare Access policy scoped to that preview hostname. Either way, treat a clone's data the same as the original: rotate any credential a clone inherited if the clone is less trusted than the source.

## 4. Teardown: DNS before the app, then revoke the rest

Retiring a deployment in the wrong order leaves a dangling DNS record pointing at a resource someone else can now claim (a subdomain takeover). Delete the DNS record (the `CNAME` or `A`/`AAAA`) before you delete or release the underlying app, load balancer, or IP, and keep that resource reserved until the record's old TTL has drained and its removal is confirmed at the authoritative nameservers: deleting a record does not flush answers already cached by resolvers, so releasing a reclaimable IP or hostname immediately can still send cached clients to whoever claims it next. Then revoke what pointed at it: access policies (Cloudflare Access or equivalent), API tokens and service credentials scoped to that deployment ([machine-auth.md](machine-auth.md)), and database users created only for it.

## 5. Re-verify after anything changes

Rerun the outside-in checks in section 1 and the negative auth tests from [authentication.md](authentication.md) after an upgrade, a backup restore (which can reintroduce a default account or reset a feature flag), or any change to network policy or auth configuration. Monitor certificate expiry from outside the host too: a renewal cron can silently fail while the host's own view still looks fine, so an external check (a scheduled `openssl s_client` from another machine, or a third-party uptime/certificate monitor) catches what a local `certbot renew --dry-run` cannot.

## 6. Offboarding

When a person leaves, revoke access at every layer they touched, not only their password: identity-provider membership (the SSO or directory account), proxy-level sessions (Cloudflare Access or equivalent), application-level sessions on each service, and any personal access tokens or API keys issued to them. Where a system cannot revoke immediately, such as a session cached until its own expiry, know that system's maximum time-to-revoke and treat the number as something to shrink, not accept. [mfa.md](mfa.md) covers revoking the second factor alongside the account.

## Common mistakes

- Verifying only the custom domain and forgetting the platform's own generated URL, which is often still reachable and unauthenticated.
- Deleting the app first and the DNS record later, leaving exactly the dangling-CNAME window a takeover needs.
- Trusting a local `certbot renew --dry-run` as proof that production certificates are actually renewing; it proves the client works, not that the last real renewal succeeded.

## Verify

REASONED: outside-network scans, DNS retirement and certificate inspection; no deployment, authoritative DNS zone or second-network probe host was supplied for this metadata review, and no run is recorded. The commands and expected readings below follow the cited Nmap and dig documentation and the guide's lifecycle reasoning; an OpenSSL source is not recorded.

```bash
# From a second network, not the host itself:
(                                                      # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
    *) nmap -Pn -p- "$1" ;;                        # TCP only: only the intended ports answer here; probe any UDP service separately (nmap -sU)
    # and the scan actually ran: nmap reporting a host down, a permission error, or no output at all is
    # inconclusive, not a clean result
  esac
)
(                                                      # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IPV6'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
    *) nmap -Pn -6 -p- "$1" ;;                      # same, over the public IPv6 address (TCP only)
                                                    # same reading: a scan that did not run is not a clean scan
  esac
)
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -sI https://retired-preview.example.com/          # a connection/DNS/TLS failure here is NOT proof the record is gone (a dangling record to a released target fails the same way); use the dig check below, and confirm at the authoritative nameservers, to establish removal
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
for t in A AAAA CNAME; do echo "$t:"; dig +short retired-preview.example.com "$t"; done   # checks your configured resolver only, so it is not authoritative: any A/AAAA/CNAME answer means that resolver still returns a mapping (investigate before release; an answer alone does not prove the target is dangling), and empty output is inconclusive. Confirm removal against each authoritative nameserver directly (dig @AUTH_NS name TYPE +norecurse), requiring NXDOMAIN or NOERROR/NODATA with no CNAME; treat SERVFAIL/referral/timeout as inconclusive
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
openssl s_client -connect app.example.com:443 -servername app.example.com \
  -verify_hostname app.example.com -verify_return_error </dev/null \
  | openssl x509 -noout -enddate                        # run from outside on a schedule
```

## Sources (checked September 2026)

- nmap reference guide (port scanning syntax, and `-Pn`): https://nmap.org/book/man-briefoptions.html
- Shodan: https://www.shodan.io/
- Censys: https://censys.com/
- Vercel Deployment Protection (Standard Protection versus All Deployments scope; Vercel Authentication for All Deployments does not require a paid add-on): https://vercel.com/docs/deployment-protection
- Vercel changelog, protect production deployments for free on every plan (9 September 2026): https://vercel.com/changelog/protect-production-deployments-for-free-on-every-plan
- Cloudflare Access policies: https://developers.cloudflare.com/cloudflare-one/access-controls/policies/
- nmap host discovery (`-Pn` "skips the host discovery stage altogether"): https://nmap.org/book/man-host-discovery.html
- dig DNS lookup utility (querying a specific authoritative nameserver with `@server` and `+norecurse`; NXDOMAIN vs NODATA): https://bind9.readthedocs.io/en/latest/manpages.html
