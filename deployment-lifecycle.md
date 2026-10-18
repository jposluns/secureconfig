---
version_basis: {
  "schema": 1,
  "checked": "2026-10-18",
  "documentation_checked": "2026-09",
  "body_sha256": "157e46f159f0f4457d43a1b311f18c8efdd97fdec15bec7065c1373ee5eb24ec",
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
    },
    "openssl": {
      "name": "OpenSSL command documentation",
      "basis": "3.0",
      "sources": {
        "s00aaf106164f": "https://docs.openssl.org/3.0/man1/openssl-s_client/",
        "s0856f4a58574": "https://docs.openssl.org/3.0/man1/openssl-x509/"
      }
    },
    "openbsd-nc": {
      "name": "OpenBSD nc manual",
      "basis": "7.6",
      "sources": {
        "s0c8b1a738e7b": "https://man.openbsd.org/OpenBSD-7.6/nc.1"
      }
    },
    "ubuntu-nc": {
      "name": "Ubuntu noble netcat-openbsd source",
      "basis": "c047f1a4572e796c8643fb7e5a719a9d960a677b",
      "sources": {
        "s478aaf9a8975": "https://git.launchpad.net/ubuntu/+source/netcat-openbsd/tree/nc.1?id=c047f1a4572e796c8643fb7e5a719a9d960a677b#n257",
        "sd7b31d3bc579": "https://git.launchpad.net/ubuntu/+source/netcat-openbsd/tree/nc.1?id=c047f1a4572e796c8643fb7e5a719a9d960a677b#n263",
        "scc48da80246b": "https://git.launchpad.net/ubuntu/+source/netcat-openbsd/tree/nc.1?id=c047f1a4572e796c8643fb7e5a719a9d960a677b#n308"
      }
    },
    "c9s-nmap": {
      "name": "CentOS Stream 9 nmap packaging",
      "basis": "17c2b7795d821cd7fbe311cf3f885be3ea1f122f",
      "sources": {
        "sd06e83963e39": "https://gitlab.com/redhat/centos-stream/rpms/nmap/-/blob/17c2b7795d821cd7fbe311cf3f885be3ea1f122f/nmap.spec#L133-L137",
        "s3ab25d24e37a": "https://gitlab.com/redhat/centos-stream/rpms/nmap/-/blob/17c2b7795d821cd7fbe311cf3f885be3ea1f122f/nmap.spec#L6-L8"
      }
    },
    "busybox": {
      "name": "BusyBox 1.36.1",
      "basis": "1_36_1",
      "sources": {
        "s34bdee292f79": "https://github.com/mirror/busybox/blob/1_36_1/networking/nc_bloaty.c#L61-L93",
        "sd707e18625cc": "https://github.com/mirror/busybox/blob/1_36_1/networking/nc.c#L136-L170",
        "s14b89daa008d": "https://github.com/mirror/busybox/blob/1_36_1/networking/nc.c#L30-L59"
      }
    },
    "docker-notes": {
      "name": "Docker Engine release notes",
      "basis": "4e9a5751518ed8223a8dcde53693badddd72604f",
      "sources": {
        "s182da2bdd442": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/release-notes/28.md#L771-L772",
        "sfbe11311e8a4": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/release-notes/28.md#L263-L263"
      }
    },
    "webui": {
      "name": "Open WebUI",
      "basis": "0a7c15832fb30b1903753e83f81dc7d27e5b0944",
      "sources": {
        "s94d055784840": "https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/config.py"
      }
    },
    "certbot-v230": {
      "name": "Certbot user guide and source",
      "basis": "v2.3.0",
      "sources": {
        "s5def4225771f": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/cli/__init__.py#L146-L170",
        "se96df86ba351": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/cli/helpful.py#L210-L211",
        "sc37d1ffd6192": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/cli/helpful.py#L237-L264",
        "s77de4441a9e5": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L786-L798"
      }
    }
  },
  "claims": {
    "outside": {"text": "Run exposure checks from a second network; host-local curl and ss do not establish outside reachability or platform firewall behaviour.", "components": ["nmap"], "sources": ["nmap:sf8404f695ccd", "nmap:sb7d0e7eb5141"], "status": "REASONED"},
    "tcp-scan": {"text": "Sweep authorized hosts with nmap -Pn -p-; the guide also gives an nc port loop. Use the house placeholder guard for both. Ubuntu noble netcat-openbsd documents -v verbosity, -z scanning and -w timeout; BusyBox 1.36.1 small nc lacks -v/-z and needs NC_EXTRA for -w, while its NC_110_COMPAT applet lists -v/-w and needs NC_EXTRA for -z. CentOS Stream 9 packages Ncat 7.92 as nc; its option behaviour and traditional/GNU netcat remain unestablished. As this guide's assessment, refusal or timeout shows only connection failure; unsupported-option errors, local errors and silent exits are inconclusive.", "components": ["nmap", "openbsd-nc", "ubuntu-nc", "c9s-nmap", "busybox"], "sources": ["nmap:sf8404f695ccd", "nmap:sb7d0e7eb5141", "openbsd-nc:s0c8b1a738e7b", "ubuntu-nc:s478aaf9a8975", "ubuntu-nc:sd7b31d3bc579", "ubuntu-nc:scc48da80246b", "c9s-nmap:sd06e83963e39", "c9s-nmap:s3ab25d24e37a", "busybox:s34bdee292f79", "busybox:sd707e18625cc", "busybox:s14b89daa008d"], "status": "REASONED"},
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
    "reverify": {"text": "Repeat outside scans and negative auth tests after upgrades, backup restores or network/auth changes; a restore can reintroduce a default account or reset a feature flag as this guide's assessment, not a general vendor fact. Docker 28.0.0 warns that hosts with IPv6 forwarding already enabled that relied on Docker setting FORWARD to DROP may need configuration changes; 28.3.3 fixes local-network access to loopback-intended published ports after firewalld reload. Open WebUI enables persistence by default; as this guide's conditional inference, restoring database values that override the environment after first launch could reinstate earlier signup settings. The files this guide cites do not establish database precedence or general restore behaviour; Nmap supports scanning only.", "components": ["nmap", "docker-notes", "webui"], "sources": ["nmap:sf8404f695ccd", "nmap:sb7d0e7eb5141", "docker-notes:s182da2bdd442", "docker-notes:sfbe11311e8a4", "webui:s94d055784840"], "status": "REASONED"},
    "certificate-monitor": {"text": "Monitor certificate expiry externally. As this guide's assessment, a renewal cron can silently fail while the host's view looks fine; its advice is a scheduled external openssl s_client or third-party monitor. Certbot v2.3.0 dry-run uses staging unless a custom server is set, saves no test certificates and runs applicable deploy hooks only with --run-deploy-hooks after success, using the active certificate. The user guide separates dry-run from live renewal; this guide infers that dry-run cannot establish the last real renewal's success. Nmap is outside-check context only.", "components": ["nmap", "openssl", "certbot-v230"], "sources": ["nmap:sf8404f695ccd", "openssl:s00aaf106164f", "openssl:s0856f4a58574", "certbot-v230:s5def4225771f", "certbot-v230:se96df86ba351", "certbot-v230:sc37d1ffd6192", "certbot-v230:s77de4441a9e5"], "status": "REASONED"},
    "offboarding": {"text": "Revoke identity membership, proxy/app sessions, personal tokens, API keys and second factors; account for cached-session expiry. Access-policy citation does not establish each layer or its revocation delay.", "components": ["access"], "sources": ["access:sc007294b64a0"], "status": "REASONED"},
    "verify-ipv4": {"text": "From another network, nmap -Pn -p- should find only intended TCP ports; unintended open ports fail, and errors or an unexecuted scan are inconclusive.", "components": ["nmap"], "sources": ["nmap:sf8404f695ccd", "nmap:sb7d0e7eb5141"], "status": "REASONED", "verify": [1]},
    "verify-ipv6": {"text": "Repeat the full TCP sweep over the public IPv6 address with -6; a scan that did not run is inconclusive.", "components": ["nmap"], "sources": ["nmap:sf8404f695ccd", "nmap:sb7d0e7eb5141"], "status": "REASONED", "verify": [1]},
    "verify-dns": {"text": "curl failure does not prove DNS removal; resolver A/AAAA/CNAME answers need investigation and empty output is inconclusive. Check every authoritative server with +norecurse for NXDOMAIN or NOERROR/NODATA without CNAME; SERVFAIL, referral and timeout are inconclusive.", "components": ["dns"], "sources": ["dns:se6d352e0a4fa"], "status": "REASONED", "verify": [1]},
    "verify-certificate": {"text": "The scheduled external s_client probe checks hostname and verification errors and pipes the certificate to x509 -enddate. No observed outcome is recorded; Nmap is outside-check context only.", "components": ["nmap", "openssl"], "sources": ["nmap:sf8404f695ccd", "openssl:s00aaf106164f", "openssl:s0856f4a58574"], "status": "REASONED", "verify": [1]}
  }
}
---
# Deploying safely over time: verify from outside, safe order, previews, teardown

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-18; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| outside: Run exposure checks from a second network; host-local curl and ss do not establish outside reachability or platform firewall behaviour. | Nmap documentation unknown | REASONED |
| tcp-scan: Sweep authorized hosts with nmap -Pn -p-; the guide also gives an nc port loop. Use the house placeholder guard for both. Ubuntu noble netcat-openbsd documents -v verbosity, -z scanning and -w timeout; BusyBox 1.36.1 small nc lacks -v/-z and needs NC_EXTRA for -w, while its NC_110_COMPAT applet lists -v/-w and needs NC_EXTRA for -z. CentOS Stream 9 packages Ncat 7.92 as nc; its option behaviour and traditional/GNU netcat remain unestablished. As this guide's assessment, refusal or timeout shows only connection failure; unsupported-option errors, local errors and silent exits are inconclusive. | Nmap documentation unknown; OpenBSD nc manual 7.6; Ubuntu noble netcat-openbsd source c047f1a4572e796c8643fb7e5a719a9d960a677b; CentOS Stream 9 nmap packaging 17c2b7795d821cd7fbe311cf3f885be3ea1f122f; BusyBox 1.36.1 1_36_1 | REASONED |
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
| reverify: Repeat outside scans and negative auth tests after upgrades, backup restores or network/auth changes; a restore can reintroduce a default account or reset a feature flag as this guide's assessment, not a general vendor fact. Docker 28.0.0 warns that hosts with IPv6 forwarding already enabled that relied on Docker setting FORWARD to DROP may need configuration changes; 28.3.3 fixes local-network access to loopback-intended published ports after firewalld reload. Open WebUI enables persistence by default; as this guide's conditional inference, restoring database values that override the environment after first launch could reinstate earlier signup settings. The files this guide cites do not establish database precedence or general restore behaviour; Nmap supports scanning only. | Nmap documentation unknown; Docker Engine release notes 4e9a5751518ed8223a8dcde53693badddd72604f; Open WebUI 0a7c15832fb30b1903753e83f81dc7d27e5b0944 | REASONED |
| certificate-monitor: Monitor certificate expiry externally. As this guide's assessment, a renewal cron can silently fail while the host's view looks fine; its advice is a scheduled external openssl s_client or third-party monitor. Certbot v2.3.0 dry-run uses staging unless a custom server is set, saves no test certificates and runs applicable deploy hooks only with --run-deploy-hooks after success, using the active certificate. The user guide separates dry-run from live renewal; this guide infers that dry-run cannot establish the last real renewal's success. Nmap is outside-check context only. | Nmap documentation unknown; OpenSSL command documentation 3.0; Certbot user guide and source v2.3.0 | REASONED |
| offboarding: Revoke identity membership, proxy/app sessions, personal tokens, API keys and second factors; account for cached-session expiry. Access-policy citation does not establish each layer or its revocation delay. | Cloudflare Access policies unknown | REASONED |
| verify-ipv4: From another network, nmap -Pn -p- should find only intended TCP ports; unintended open ports fail, and errors or an unexecuted scan are inconclusive. | Nmap documentation unknown | REASONED |
| verify-ipv6: Repeat the full TCP sweep over the public IPv6 address with -6; a scan that did not run is inconclusive. | Nmap documentation unknown | REASONED |
| verify-dns: curl failure does not prove DNS removal; resolver A/AAAA/CNAME answers need investigation and empty output is inconclusive. Check every authoritative server with +norecurse for NXDOMAIN or NOERROR/NODATA without CNAME; SERVFAIL, referral and timeout are inconclusive. | BIND dig documentation unknown | REASONED |
| verify-certificate: The scheduled external s_client probe checks hostname and verification errors and pipes the certificate to x509 -enddate. No observed outcome is recorded; Nmap is outside-check context only. | Nmap documentation unknown; OpenSSL command documentation 3.0 | REASONED |
<!-- version-basis:end -->

This repository's per-service guides check TLS, binding, and authentication from inside the host and at the moment you set them up. Real exposure is judged from outside the host, and it drifts: a preview URL, a restored backup, or an upgrade can reopen something already closed. This guide is the lifecycle layer around the per-service checks.

## 1. Verify from outside, not just from the host

A `curl` or `ss -tlnp` run on the host itself cannot see a firewall the host does not know about, or a platform-level bypass like Docker's iptables rules ([docker.md](docker.md)). Verify from a second network: a phone hotspot, a cloud shell, or a second VM.

- Port-by-port: `for p in 22 80 443 3000 5432 6379 27017; do nc -vz -w 3 REPLACE_WITH_YOUR_PUBLIC_IP "$p"; done`, or a full sweep, `nmap -Pn -p- REPLACE_WITH_YOUR_PUBLIC_IP` (per the nmap reference, which documents `-p-` and `-p 1-65535` as equivalent port-range syntax; this sweeps TCP only, so inventory and separately probe any UDP service with `nmap -sU` on its ports; only scan hosts you own or are authorized to test). Before running either form, use the [guarded Verify block](#verify); for the loop, replace only its IPv4 arm's `nmap -Pn -p- "$1"` with `for p in 22 80 443 3000 5432 6379 27017; do nc -vz -w 3 "$1" "$p"; done`, keeping the whole guard and substituting inside the quotes on `set --`. Ubuntu noble netcat-openbsd documents `-v` as verbose output, `-z` as scanning without sending data and `-w` as a connection/idle timeout. BusyBox 1.36.1 small `nc` lacks `-v` and `-z`, and has `-w` only with `NC_EXTRA`; its `NC_110_COMPAT` applet lists `-v` and `-w`, with `-z` conditional on `NC_EXTRA`. CentOS Stream 9 packages Ncat 7.92 as an `nc` alternative, but the Ncat implementation this guide cites is from a later master commit, so Ncat 7.92's option behaviour remains unestablished here, as does traditional or GNU netcat behaviour. Check the installed variant. As this guide's assessment, refusal or timeout shows only that this connection failed; an unsupported-option error, local error or silent exit is inconclusive.
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

Rerun the outside-in checks in section 1 and the negative auth tests from [authentication.md](authentication.md) after an upgrade, a backup restore (which, as this guide's assessment, can reintroduce a default account or reset a feature flag), or any change to network policy or auth configuration. Docker's pinned 28.x release notes give concrete change-related cases: 28.0.0 sets IPv6 `FORWARD` policy to `DROP` only when Docker enables forwarding itself, warning that hosts with forwarding already enabled that relied on Docker setting `DROP` may need configuration changes; 28.3.3 fixes direct local-network access to published container ports after a firewalld reload, even when intended for loopback-only access. Open WebUI's pinned configuration supplies an environment-derived signup default and enables persistence by default. As this guide's conditional inference for restores, if database values override the environment after first launch as described in [open-webui.md](open-webui.md), restoring earlier database values could reinstate earlier signup settings; the configuration this guide cites delegates to `models.config.Config`, whose implementation this guide does not cite, so these files do not establish that precedence or general restore behaviour. Nmap supports scanning, not application restore behaviour. Monitor certificate expiry from outside the host too: as this guide's assessment, a renewal cron can silently fail while the host's own view still looks fine, so this guide's advice is an external check (a scheduled `openssl s_client` from another machine, or a third-party uptime/certificate monitor). Certbot v2.3.0's `certbot renew --dry-run` uses the staging test server unless a custom server is set, obtains test certificates without saving them and does not run deploy hooks unless `--run-deploy-hooks` is supplied; applicable deploy hooks then run only after a successful dry run, using the current active certificate. The option documentation also warns that dry runs can temporarily change webserver configuration, reload webservers and run pre/post hooks; the user guide's dry-run example distinguishes it from a subsequent live renewal. From these documented limits, this guide infers that a dry run cannot show whether the last real renewal succeeded; Nmap is outside-check context only.

## 6. Offboarding

When a person leaves, revoke access at every layer they touched, not only their password: identity-provider membership (the SSO or directory account), proxy-level sessions (Cloudflare Access or equivalent), application-level sessions on each service, and any personal access tokens or API keys issued to them. Where a system cannot revoke immediately, such as a session cached until its own expiry, know that system's maximum time-to-revoke and treat the number as something to shrink, not accept. [mfa.md](mfa.md) covers revoking the second factor alongside the account.

## Common mistakes

- Verifying only the custom domain and forgetting the platform's own generated URL, which is often still reachable and unauthenticated.
- Deleting the app first and the DNS record later, leaving exactly the dangling-CNAME window a takeover needs.
- Trusting a local `certbot renew --dry-run` as proof that production certificates are actually renewing; Certbot v2.3.0 documents test certificates without saving them, staging unless a custom server is set, and deploy hooks only with `--run-deploy-hooks` after a successful dry run, using the active certificate. This guide infers that this test does not establish whether the last real renewal succeeded.

## Verify

REASONED: outside-network scans, DNS retirement and certificate inspection; no deployment, authoritative DNS zone or second-network probe host was supplied for this metadata review, and no run is recorded. The commands and expected readings below follow the cited Nmap, dig and OpenSSL 3.0 documentation and the guide's lifecycle reasoning; Sources has no curl reference.

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
- OpenSSL 3.0 `s_client` (checked October 2026; connection, hostname verification, and verification errors): https://docs.openssl.org/3.0/man1/openssl-s_client/
- OpenSSL 3.0 `x509` (checked October 2026; `-noout -enddate` certificate expiry inspection): https://docs.openssl.org/3.0/man1/openssl-x509/
- OpenBSD 7.6 `nc` (checked October 2026; OpenBSD netcat implementation of `-v`, `-z`, and `-w`): https://man.openbsd.org/OpenBSD-7.6/nc.1
- Ubuntu noble nc verbose flag, lines 257 to 258, at c047f1a4572e796c8643fb7e5a719a9d960a677b (checked October 2026): https://git.launchpad.net/ubuntu/+source/netcat-openbsd/tree/nc.1?id=c047f1a4572e796c8643fb7e5a719a9d960a677b#n257
- Ubuntu noble nc timeout flag, lines 263 to 266, at c047f1a4572e796c8643fb7e5a719a9d960a677b (checked October 2026): https://git.launchpad.net/ubuntu/+source/netcat-openbsd/tree/nc.1?id=c047f1a4572e796c8643fb7e5a719a9d960a677b#n263
- Ubuntu noble nc zero-I/O scan, lines 308 to 311, at c047f1a4572e796c8643fb7e5a719a9d960a677b (checked October 2026): https://git.launchpad.net/ubuntu/+source/netcat-openbsd/tree/nc.1?id=c047f1a4572e796c8643fb7e5a719a9d960a677b#n308
- CentOS Stream 9 ncat nc alternative, at 17c2b7795d821cd7fbe311cf3f885be3ea1f122f (checked October 2026): https://gitlab.com/redhat/centos-stream/rpms/nmap/-/blob/17c2b7795d821cd7fbe311cf3f885be3ea1f122f/nmap.spec#L133-L137
- CentOS Stream 9 nmap package version, at 17c2b7795d821cd7fbe311cf3f885be3ea1f122f (checked October 2026): https://gitlab.com/redhat/centos-stream/rpms/nmap/-/blob/17c2b7795d821cd7fbe311cf3f885be3ea1f122f/nmap.spec#L6-L8
- BusyBox 1.36.1 compatible nc options, at 1_36_1 (checked October 2026): https://github.com/mirror/busybox/blob/1_36_1/networking/nc_bloaty.c#L61-L93
- BusyBox 1.36.1 small nc option parser, at 1_36_1 (checked October 2026): https://github.com/mirror/busybox/blob/1_36_1/networking/nc.c#L136-L170
- BusyBox 1.36.1 nc compatibility build selection, at 1_36_1 (checked October 2026): https://github.com/mirror/busybox/blob/1_36_1/networking/nc.c#L30-L59
- Docker Engine 28.0.0 IPv6 forwarding-policy change and warning, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/release-notes/28.md#L771-L772
- Docker Engine 28.3.3 firewalld-reload exposure fix, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/release-notes/28.md#L263-L263
- Open WebUI signup default and persistence configuration (lines 1649, 3091 and 3237 to 3244; Config implementation not cited), at 0a7c15832fb30b1903753e83f81dc7d27e5b0944 (checked October 2026): https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/config.py
- Certbot dry-run and deploy-hook option documentation, at v2.3.0 (checked October 2026): <https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/cli/__init__.py#L146-L170>
- Certbot dry-run test-server dispatch, at v2.3.0 (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/cli/helpful.py#L210-L211
- Certbot staging-server selection and custom-server exception, at v2.3.0 (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/cli/helpful.py#L237-L264
- Certbot user-guide dry-run and subsequent live-renewal example, at v2.3.0 (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L786-L798
