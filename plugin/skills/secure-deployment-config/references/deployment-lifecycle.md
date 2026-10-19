# Deploying safely over time: verify from outside, safe order, previews, teardown

Written against Nmap documentation (no recorded version), BIND dig documentation 9.18.39, OpenSSL command documentation 3.0, OpenBSD nc manual 7.6, OWASP Web Security Testing Guide v4.2, OAuth2 Proxy v7.15.4, Authelia v4.39.28, and NIST digital identity guidelines SP 800-63B-4, plus 2 more recorded bases; 9 further sources are pinned to a commit and 6 carry no recorded version. Metadata reviewed 2026-10-18; documentation checked September 2026. The guide records 22 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

This repository's per-service guides check TLS, binding, and authentication from inside the host and at the moment you set them up. Real exposure is judged from outside the host, and it drifts: a preview URL, a restored backup, or an upgrade can reopen something already closed. This guide is the lifecycle layer around the per-service checks.

## 1. Verify from outside, not just from the host

A `curl` or `ss -tlnp` run on the host itself cannot see a firewall the host does not know about, or a platform-level bypass like Docker's iptables rules ([docker.md](docker.md)). Verify from a second network: a phone hotspot, a cloud shell, or a second VM.

- Port-by-port: `for p in 22 80 443 3000 5432 6379 27017; do nc -vz -w 3 REPLACE_WITH_YOUR_PUBLIC_IP "$p"; done`, or a full sweep, `nmap -Pn -p- REPLACE_WITH_YOUR_PUBLIC_IP` (per the nmap reference, which documents `-p-` and `-p 1-65535` as equivalent port-range syntax; this sweeps TCP only, so inventory and separately probe any UDP service with `nmap -sU` on its ports; only scan hosts you own or are authorized to test). Before running either form, use the [guarded Verify block](#verify); for the loop, replace only its IPv4 arm's `nmap -Pn -p- "$1"` with `for p in 22 80 443 3000 5432 6379 27017; do nc -vz -w 3 "$1" "$p"; done`, keeping the whole guard and substituting inside the quotes on `set --`. Ubuntu noble netcat-openbsd documents `-v` as verbose output, `-z` as scanning without sending data and `-w` as a connection/idle timeout. BusyBox 1.36.1 small `nc` lacks `-v` and `-z`, and has `-w` only with `NC_EXTRA`; its `NC_110_COMPAT` applet lists `-v` and `-w`, with `-z` conditional on `NC_EXTRA`. CentOS Stream 9 packages Ncat 7.92 as an `nc` alternative; Ncat 7.92's option behaviour is not established here, nor is traditional or GNU netcat behaviour. Check the installed variant. As this guide's assessment, refusal or timeout shows only that this connection failed; an unsupported-option error, local error or silent exit is inconclusive.
- Check every address the service actually has, not just the one you remember configuring: the public IPv4 address, the public IPv6 address if the host has one, and any platform-assigned URL alongside your custom domain (a PaaS default subdomain, per [paas.md](paas.md), often stays reachable even when the custom domain is fronted). A scan of one address that misses the others is not a clean result, it is an incomplete one.
- Cross-reference what is already indexed about your IP with a passive internet-wide scanner such as Shodan or Censys; both build a continuously updated index of internet-connected hosts and services, so a stale exposure can show up there before you find it yourself ([cloud-firewalls.md](cloud-firewalls.md) covers the firewall rules this is checking).

## 2. Safe initialization order

This guide advises the following first-deployment order, keeping application access closed until initialization and the fronting gate are ready:

1. Create the owner or admin account's credentials and any signing secrets (session, JWT, or cookie-signing keys) per [authentication.md](authentication.md); the ordering is this guide's advice, and signing secrets follow that guide's recommendation.
2. Set the registration policy (disable open self-registration, or restrict it to an allowlisted domain) before opening application access, as this guide advises; [authentication.md](authentication.md) covers allowlisting after federated login.
3. Put the fronting gate in place, TLS and any proxy-level authentication, per [free-certificates.md](free-certificates.md) and the fronting-layer guides. For ACME, this guide advises DNS-01 issuance before opening inbound access, or opening only the challenge port during issuance while keeping application access blocked: HTTP-01 requires inbound port 80 and TLS-ALPN-01 requires inbound port 443, whereas DNS-01 needs no inbound port, per the [prerequisite list](free-certificates.md#prerequisites). These challenge requirements do not establish this deployment order. Cloudflare recommends creating the Access application before the tunnel route and warns that without it the published application is available to anyone on the Internet; an already publicly routable origin needs its IP protected by other methods, per the pinned self-hosted application instructions.
4. Only then open application network access, as this guide advises.

For applications that give admin to whoever completes first-run setup, an unclaimed setup wizard is a race to become admin, open to whoever completes it first. [Open WebUI](open-webui.md) at commit 0a7c15832fb30b1903753e83f81dc7d27e5b0944 is one example: its signup handler makes the first account admin; with authentication enabled, ENABLE_SIGNUP and ENABLE_LOGIN_FORM default to true, and an empty database bypasses ENABLE_SIGNUP when the login form is enabled. Once accounts exist, disabled signup refuses registration. These Open WebUI paths do not establish other applications' bootstrap, signing-secret, registration or domain-enforcement behaviour. After initialization, confirm the setup route itself is closed: restart the service and try hitting the initial-setup URL again; it must refuse to mint a second admin, not silently succeed (this guide's test expectation). The Open WebUI signup handler illustrates bootstrap and signup refusal, not every application's setup route or a deployed restart result.

## 3. Previews and clones get production posture

A preview deployment or a database clone is not lower stakes just because it is temporary. Vercel's Deployment Protection illustrates the gap: Standard Protection, available on every plan, gates preview and generated deployment URLs but leaves the production domain open by default; the All Deployments scope closes that gap too, and Vercel's September 9, 2026 change made pairing it with Vercel Authentication free on every plan rather than Pro and Enterprise only ([paas.md](paas.md); per Vercel's Deployment Protection changelog of 9 September 2026 and its current Deployment Protection reference, which states that Vercel Authentication for All Deployments does not require a paid add-on). Where the platform's own gate does not cover a hostname, front it the same way as production, for example a Cloudflare Access policy scoped to that preview hostname, per the pinned self-hosted application instructions. Those instructions establish the Access gate, not the platform's coverage of preview URLs. Either way, as this guide's advice, treat a clone's data the same as the original: rotate any credential a clone inherited if the clone is less trusted than the source. That a clone can inherit credentials is this guide's assessment; clone credential inheritance and rotation are not established by the Access citation, which supplies fronting context only.

## 4. Teardown: DNS before the app, then revoke the rest

Retiring a deployment in the wrong order can leave a dangling DNS record pointing at a resource someone else can claim (a subdomain takeover); OWASP's Subdomain Takeover Prevention Cheat Sheet describes this mechanism, and WSTG v4.2 identifies an inactive target and inadequate ownership verification as preconditions. Delete the DNS record (the `CNAME` or `A`/`AAAA`) before you delete or release the underlying app, load balancer, or IP, and wait at least the record's old TTL before decommissioning the resource, following OWASP's order; WSTG supports removing vulnerable records but does not specify that wait.

RFC 1034 section 3.6 and RFC 1035 section 3.2.1 describe resolver caching and TTL, with TTL bounds clarified by RFC 2181 section 8 and updated by RFC 8767 section 4. **TTL expiry is not a hard bound: RFC 8767 permits serving stale records when they cannot be authoritatively refreshed.** This guide infers that deleting a record does not flush cached answers, so immediately releasing a reclaimable IP or hostname can still send cached clients to its next owner. OWASP describes claimable CNAME targets and released IPs that an attacker obtains after reassignment; the cited files do not establish a particular platform's current reclaimability. This guide advises keeping the resource reserved through the old TTL and until removal is confirmed at every authoritative nameserver, and accounting for serve-stale before release; authoritative removal and elapsed TTL do not prove that every resolver has stopped returning the old mapping.

Then revoke what pointed at it: access policies (Cloudflare Access or equivalent), API tokens and service credentials scoped to that deployment ([machine-auth.md](machine-auth.md)), and database users created only for it. This remains the guide's retirement requirement: OWASP Secrets Management requires secure revocation of secrets that are no longer required or potentially compromised. The Access-policy citation covers fronting context only, and the cited files do not establish removal of an Access application or policy or dropping database users.

## 5. Re-verify after anything changes

Rerun the outside-in checks in section 1 and the negative auth tests from [authentication.md](authentication.md) after an upgrade, a backup restore (which, as this guide's assessment, can reintroduce a default account or reset a feature flag), or any change to network policy or auth configuration. Docker's pinned 28.x release notes give concrete change-related cases: 28.0.0 sets IPv6 `FORWARD` policy to `DROP` only when Docker enables forwarding itself, warning that hosts with forwarding already enabled that relied on Docker setting `DROP` may need configuration changes; 28.3.3 fixes direct local-network access to published container ports after a firewalld reload, even when intended for loopback-only access. Open WebUI's pinned configuration supplies an environment-derived signup default and enables persistence by default. As this guide's conditional inference for restores, if database values override the environment after first launch as described in [open-webui.md](open-webui.md), restoring earlier database values could reinstate earlier signup settings; the configuration this guide cites delegates to `models.config.Config`, whose implementation this guide does not cite, so these files do not establish that precedence or general restore behaviour. Nmap supports scanning, not application restore behaviour. Monitor certificate expiry from outside the host too: as this guide's assessment, a renewal cron can silently fail while the host's own view still looks fine, so this guide's advice is an external check (a scheduled `openssl s_client` from another machine, or a third-party uptime/certificate monitor). Certbot v2.3.0's `certbot renew --dry-run` uses the staging test server unless a custom server is set, obtains test certificates without saving them and does not run deploy hooks unless `--run-deploy-hooks` is supplied; applicable deploy hooks then run only after a successful dry run, using the current active certificate. The option documentation also warns that dry runs can temporarily change webserver configuration, reload webservers and run pre/post hooks; the user guide's dry-run example distinguishes it from a subsequent live renewal. From these documented limits, this guide infers that a dry run cannot show whether the last real renewal succeeded; Nmap is outside-check context only.

## 6. Offboarding

When a person leaves, revoke access at every layer they touched, not only their password: identity-provider membership (the SSO or directory account), proxy-level sessions (Cloudflare Access or equivalent), application-level sessions on each service, and any personal access tokens or API keys issued to them (this guide's recommendation, as in [authentication.md](authentication.md)).

Microsoft Entra documents blocking new sign-ins and revoking refresh tokens, but the application must revoke its own session; access-token lifetimes vary, and CAE critical-event enforcement can take up to 15 minutes for supported services. Cloudflare Access documents per-user session revocation, but an active IdP profile can start a new session; after user logout, previously issued tokens stop being accepted in 20-30 seconds. OAuth2 Proxy v7.15.4 documents cookie expiry and refresh, and Authelia v4.39.28 documents cookie expiry and session destruction, overridden by remember-me; these passages do not establish immediate per-user revocation for either proxy. RFC 7009 section 2.1 specifies immediate token invalidation with possible propagation delay and conditional access-token revocation support. OWASP requires secure revocation of unneeded or potentially compromised secrets. NIST SP 800-63B-4 section 4.5 requires CSPs to promptly invalidate authenticators when the CSP determines that the subscriber no longer meets its eligibility requirements.

Where a system cannot revoke immediately, such as a session cached until its own expiry, measure that system's maximum time-to-revoke and work to shrink it (this guide's recommendation, as in [authentication.md](authentication.md)). The cited files do not establish a provider-membership removal mechanism, a session-revocation mechanism for every application, or this deployment's measured maximum time-to-revoke. For delayed invalidation checks, follow the REASONED offboarding replay check in [authentication.md](authentication.md#quick-checks): matched requests must succeed before revocation, then each old credential must be refused and return no protected data within its configured maximum time-to-revoke; these are test expectations, not observed results. [mfa.md](mfa.md) covers revoking the second factor alongside the account.

## Common mistakes

- Verifying only the custom domain and forgetting the platform's own generated URL, which is often still reachable and unauthenticated.
- Deleting the app first and the DNS record later, leaving the dangling-CNAME window OWASP warns about when the target can be claimed; waiting only for TTL expiry also misses the serve-stale exception in RFC 8767.
- Trusting a local `certbot renew --dry-run` as proof that production certificates are actually renewing; Certbot v2.3.0 documents test certificates without saving them, staging unless a custom server is set, and deploy hooks only with `--run-deploy-hooks` after a successful dry run, using the active certificate. This guide infers that this test does not establish whether the last real renewal succeeded.

## Verify

REASONED: outside-network scans, DNS retirement and certificate inspection; no deployment, authoritative DNS zone or second-network probe host was supplied for this metadata review, and no run is recorded. The commands and expected readings below follow the cited Nmap, dig and OpenSSL 3.0 documentation and the guide's lifecycle reasoning; Sources has no curl reference. DNS response interpretations follow RFC 2308 section 2, and cache timing follows the cited DNS RFCs, including RFC 8767's serve-stale exception; the authoritative-removal checks are this guide's advice and do not establish that all recursive caches have refreshed.

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
- Cloudflare Access authentication layer (checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L14-L16
- Cloudflare Access policy gate, tunnel order and origin protection (checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L40-L54
- Open WebUI first-admin bootstrap and signup refusal (checked October 2026): https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py
- Let's Encrypt documentation (challenge requirements as cited in free-certificates.md): https://letsencrypt.org/docs/
- nmap host discovery (`-Pn` "skips the host discovery stage altogether"): https://nmap.org/book/man-host-discovery.html
- BIND 9.18.39 dig DNS lookup utility (querying a specific nameserver with `@server` and `+norecurse`): https://bind9.readthedocs.io/en/v9.18.39/manpages.html
- OpenSSL 3.0 `s_client` (checked October 2026; connection, hostname verification, and verification errors): https://docs.openssl.org/3.0/man1/openssl-s_client/
- OpenSSL 3.0 `x509` (checked October 2026; `-noout -enddate` certificate expiry inspection): https://docs.openssl.org/3.0/man1/openssl-x509/
- OpenBSD 7.6 `nc` (checked October 2026; OpenBSD netcat implementation of `-v`, `-z`, and `-w`): https://man.openbsd.org/OpenBSD-7.6/nc.1
- OWASP takeover mechanism (668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Subdomain_Takeover_Prevention_Cheat_Sheet.md#L5
- OWASP CNAME and released-IP risk (668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Subdomain_Takeover_Prevention_Cheat_Sheet.md#L43-L44
- OWASP retirement order and TTL wait (668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Subdomain_Takeover_Prevention_Cheat_Sheet.md#L98-L105
- WSTG takeover preconditions (v4.2, checked October 2026): https://github.com/OWASP/wstg/blob/v4.2/document/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/10-Test_for_Subdomain_Takeover.md#L9-L14
- WSTG removal of vulnerable DNS records (v4.2, checked October 2026): https://github.com/OWASP/wstg/blob/v4.2/document/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/10-Test_for_Subdomain_Takeover.md#L109
- RFC 1034 section 3.6 (TTL and cached records) (checked October 2026): https://www.rfc-editor.org/rfc/rfc1034#section-3.6
- RFC 1035 section 3.2.1 (TTL refresh semantics) (checked October 2026): https://www.rfc-editor.org/rfc/rfc1035#section-3.2.1
- RFC 2181 section 8 (TTL upper bounds, updated by RFC 8767) (checked October 2026): https://www.rfc-editor.org/rfc/rfc2181#section-8
- RFC 8767 section 4 (serve-stale updates to TTL) (checked October 2026): https://www.rfc-editor.org/rfc/rfc8767#section-4
- OWASP compromised credentials and secret revocation (pinned commit 668ba7db3d0da5868b8a0305c259f7f6914a6ecd, checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Secrets_Management_Cheat_Sheet.md#L214-L218
- Microsoft Entra application-session revocation (pinned commit 231747abc59ae3d50c74e215c1cdd592eb980723, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/users/users-revoke-access.md#L62
- Microsoft Entra account disablement and refresh-token revocation (pinned commit 231747abc59ae3d50c74e215c1cdd592eb980723, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/users/users-revoke-access.md#L96-L106
- Microsoft Entra access-token lifetime (pinned commit 231747abc59ae3d50c74e215c1cdd592eb980723, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity-platform/access-tokens.md#L54-L60
- Microsoft Entra continuous access evaluation delay (pinned commit 231747abc59ae3d50c74e215c1cdd592eb980723, checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/concept-continuous-access-evaluation.md#L21-L25
- Cloudflare Access session revocation (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/access-settings/session-management.mdx#L159-L186
- Cloudflare Access user logout delay (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/access-settings/session-management.mdx#L190-L195
- OAuth2 Proxy cookie expiry and refresh (v7.15.4, checked October 2026): https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/docs/docs/configuration/overview.md#L126-L130
- Authelia session expiration (v4.39.28, checked October 2026): https://github.com/authelia/authelia/blob/v4.39.28/docs/content/configuration/session/introduction.md#L220-L221
- OAuth 2.0 token revocation (RFC 7009) (checked October 2026): https://www.rfc-editor.org/rfc/rfc7009.html#section-2.1
- NIST SP 800-63B-4, section 4.5 (authenticator invalidation): https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63b-4.pdf
- RFC 2308 section 2 (NXDOMAIN, NODATA and referrals; checked October 2026): https://www.rfc-editor.org/rfc/rfc2308#section-2
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


<!-- version-basis:start -->
## About the AI assistant section below

The rest of this file is generated by the repository's tooling and written for AI assistants rather than for people. It records the versions this guide was written against, the guide's claims with a status for each (demonstrated by a check that ran, or reasoned from the cited sources), and the mapping from each claim to its sources. You are welcome to read it, but it is dense and can be hard to take in.

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/deployment-lifecycle.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- nmap: Nmap documentation (unknown)
- shodan: Shodan (unknown)
- censys: Censys (unknown)
- vercel: Vercel Deployment Protection (unknown)
- access: Cloudflare Access policies (c896795b8e8bab68d05ae78d64c9cbcda1fdb104)
- dns: BIND dig documentation (9.18.39)
- openssl: OpenSSL command documentation (3.0)
- openbsd-nc: OpenBSD nc manual (7.6)
- owasp-takeover: OWASP subdomain takeover prevention (668ba7db3d0da5868b8a0305c259f7f6914a6ecd)
- wstg: OWASP Web Security Testing Guide (v4.2)
- dns-rfcs: DNS caching RFCs (unknown)
- owasp-docs: OWASP security guidance (668ba7db3d0da5868b8a0305c259f7f6914a6ecd)
- entra-docs: Microsoft Entra revocation model (231747abc59ae3d50c74e215c1cdd592eb980723)
- cloudflare-access: Cloudflare Access and origin configuration (c896795b8e8bab68d05ae78d64c9cbcda1fdb104)
- oauth2-proxy: OAuth2 Proxy (v7.15.4)
- authelia: Authelia (v4.39.28)
- oauth-revocation: OAuth 2.0 Token Revocation RFC (unknown)
- nist: NIST digital identity guidelines (SP 800-63B-4)
- ubuntu-nc: Ubuntu noble netcat-openbsd source (c047f1a4572e796c8643fb7e5a719a9d960a677b)
- c9s-nmap: CentOS Stream 9 nmap packaging (17c2b7795d821cd7fbe311cf3f885be3ea1f122f)
- busybox: BusyBox 1.36.1 (1_36_1)
- docker-notes: Docker Engine release notes (4e9a5751518ed8223a8dcde53693badddd72604f)
- webui: Open WebUI (0a7c15832fb30b1903753e83f81dc7d27e5b0944)
- certbot-v230: Certbot user guide and source (v2.3.0)
- le: Let's Encrypt documentation (unknown)

Claims (full source mapping in the JSON block below):

- outside (REASONED; nmap): Run exposure checks from a second network; host-local curl and ss do not establish outside reachability or platform firewall behaviour.
- tcp-scan (REASONED; nmap, openbsd-nc, ubuntu-nc, c9s-nmap, busybox): Sweep authorized hosts with nmap -Pn -p-; the guide also gives an nc port loop. Use the house placeholder guard for both. Ubuntu noble netcat-openbsd documents -v verbosity, -z scanning and -w timeout; BusyBox 1.36.1 small nc lacks -v/-z and needs NC_EXTRA for -w, while its NC_110_COMPAT applet lists -v/-w and needs NC_EXTRA for -z. CentOS Stream 9 packages Ncat 7.92 as nc; its option behaviour and traditional/GNU netcat remain unestablished. As this guide's assessment, refusal or timeout shows only connection failure; unsupported-option errors, local errors and silent exits are inconclusive.
- udp-scan (REASONED; nmap): The full port sweep is TCP only; inventory UDP services and probe their ports separately with nmap -sU.
- all-addresses (REASONED; nmap, vercel): Check public IPv4, public IPv6 and platform URLs as well as the custom domain; one address cannot establish coverage of the others.
- passive-index (REASONED; shodan, censys): Cross-reference Shodan and Censys indexes for previously indexed exposure; indexed observations are not a fresh direct scan.
- initialize-secrets (REASONED; access, webui): As this guide's advice, create owner/admin credentials and any session, JWT or cookie-signing secrets before opening application access, following authentication.md's signing-secret recommendation. For applications that give admin to whoever completes first-run setup, an unclaimed setup wizard is a race to become admin; Open WebUI at the recorded pin is one example, with its first account becoming admin. Access is fronting context only; other applications' bootstrap and signing-secret behaviour are not established here.
- registration (REASONED; access, webui): As this guide's advice, disable open self-registration or restrict it to an allowlisted domain before opening application access; authentication.md covers allowlisting after federated login. Open WebUI at the recorded pin defaults ENABLE_SIGNUP and ENABLE_LOGIN_FORM to true with authentication enabled; an empty database bypasses ENABLE_SIGNUP when the login form is enabled, and after accounts exist disabled signup refuses registration. Access is fronting context only; other applications' registration controls and domain enforcement are not established here.
- fronting-order (REASONED; access, le): As this guide's advice, install TLS and any proxy authentication before opening application access: use DNS-01 before opening inbound access, or open only the challenge port during issuance while keeping application access blocked. Per free-certificates.md, HTTP-01 requires inbound port 80 and TLS-ALPN-01 requires inbound port 443; DNS-01 needs no inbound port. These challenge requirements do not establish this deployment order. Cloudflare recommends creating Access before the tunnel route and warns that without it the published app is public; publicly routable origins need separate IP protection. The general order remains this guide's advice.
- setup-route (REASONED; access, webui): After initialization, restart and retry the initial-setup URL; it must refuse to mint a second admin, not silently succeed (this guide's test expectation). Open WebUI's signup handler illustrates first-account bootstrap and refusal when accounts exist and signup is disabled; it does not establish every application's setup route or a deployed restart result. Access is fronting context only.
- preview-standard (REASONED; vercel): Vercel Standard Protection is available on every plan and gates previews and generated deployment URLs while leaving the production domain open.
- preview-all (REASONED; vercel): All Deployments also protects production; pairing it with Vercel Authentication became free on every plan on 9 September 2026, with no paid add-on.
- preview-gate (REASONED; access, vercel): Apply a fronting gate such as a Cloudflare Access policy to preview hostnames the platform gate does not cover. The pinned Cloudflare instructions establish the Access gate, not the platform's coverage of preview URLs.
- clone-secrets (REASONED; access): As this guide's advice, treat a clone's data the same as the original and rotate any inherited credential if the clone is less trusted than the source. That a clone can inherit credentials is this guide's assessment; clone credential inheritance and rotation are not established by the Access citation, which supplies fronting context only.
- dns-retirement (REASONED; dns, owasp-takeover, wstg, dns-rfcs): Remove CNAME or A/AAAA records before releasing the app, load balancer or IP, and wait at least the old TTL per OWASP; WSTG supports record removal, not that wait. TTL expiry is not a hard bound: RFC 8767 permits serve-stale when authoritative refresh fails. This guide advises retaining the resource through the old TTL and confirmation of removal at every authoritative nameserver, and accounting for serve-stale before release; these checks do not prove all caches have refreshed. By this guide's inference, deletion does not flush cached answers and cached clients can reach the next owner of a reclaimable target. Reclaimability is OWASP's account of claimable CNAME targets and reassigned released IPs, not established for a particular platform. dig supports DNS inspection.
- retire-credentials (REASONED; access, owasp-docs): After DNS retirement revoke deployment access policies, API/service credentials and dedicated database users (guide requirement). OWASP requires secure revocation of secrets that are no longer required or potentially compromised. The Access-policy citation covers fronting context only; the cited files do not establish removal of an Access application or policy or dropping database users.
- reverify (REASONED; nmap, docker-notes, webui): Repeat outside scans and negative auth tests after upgrades, backup restores or network/auth changes; a restore can reintroduce a default account or reset a feature flag as this guide's assessment, not a general vendor fact. Docker 28.0.0 warns that hosts with IPv6 forwarding already enabled that relied on Docker setting FORWARD to DROP may need configuration changes; 28.3.3 fixes local-network access to loopback-intended published ports after firewalld reload. Open WebUI enables persistence by default; as this guide's conditional inference, restoring database values that override the environment after first launch could reinstate earlier signup settings. The files this guide cites do not establish database precedence or general restore behaviour; Nmap supports scanning only.
- certificate-monitor (REASONED; nmap, openssl, certbot-v230): Monitor certificate expiry externally. As this guide's assessment, a renewal cron can silently fail while the host's view looks fine; its advice is a scheduled external openssl s_client or third-party monitor. Certbot v2.3.0 dry-run uses staging unless a custom server is set, saves no test certificates and runs applicable deploy hooks only with --run-deploy-hooks after success, using the active certificate. The user guide separates dry-run from live renewal; this guide infers that dry-run cannot establish the last real renewal's success. Nmap is outside-check context only.
- offboarding (REASONED; access, owasp-docs, entra-docs, cloudflare-access, oauth2-proxy, authelia, oauth-revocation, nist): When a person leaves, revoke every touched layer, not only the password: identity-provider membership, proxy/app sessions on each service, personal tokens and API keys (this guide's recommendation), and revoke the second factor alongside the account. Entra documents blocking sign-ins and revoking refresh tokens; application sessions require application revocation, access-token lifetimes vary, and supported-service CAE critical-event enforcement can take up to 15 minutes. Cloudflare documents per-user revocation, but an active IdP profile can start a new session; user logout stops acceptance of issued tokens in 20-30 seconds. OAuth2 Proxy documents cookie expiry/refresh; Authelia documents cookie expiry and session destruction, overridden by remember-me; neither passage establishes immediate per-user revocation. RFC 7009 specifies immediate invalidation with possible propagation delay and conditional access-token revocation support. OWASP requires secure revocation of unneeded or potentially compromised secrets. NIST requires CSPs to promptly invalidate authenticators when the CSP determines that the subscriber no longer meets its eligibility requirements. Where immediate revocation is unavailable, measure and shrink maximum time-to-revoke (this guide's recommendation). Provider-membership removal, every application's session-revocation mechanism and this deployment's measured maximum time-to-revoke remain unestablished. Follow authentication.md's REASONED replay check: matched requests must succeed before revocation, then old credentials must be refused without protected data within each configured maximum; these are test expectations, not observations.
- verify-ipv4 (REASONED; nmap): From another network, nmap -Pn -p- should find only intended TCP ports; unintended open ports fail, and errors or an unexecuted scan are inconclusive.
- verify-ipv6 (REASONED; nmap): Repeat the full TCP sweep over the public IPv6 address with -6; a scan that did not run is inconclusive.
- verify-dns (REASONED; dns, dns-rfcs): curl failure does not prove DNS removal; resolver A/AAAA/CNAME answers need investigation and empty output is inconclusive. Check every authoritative server with +norecurse for NXDOMAIN or NOERROR/NODATA without CNAME; SERVFAIL, referral and timeout are inconclusive.
- verify-certificate (REASONED; nmap, openssl): The scheduled external s_client probe checks hostname and verification errors and pipes the certificate to x509 -enddate. No observed outcome is recorded; Nmap is outside-check context only.

````json
{
  "schema": 1,
  "checked": "2026-10-18",
  "documentation_checked": "2026-09",
  "body_sha256": "2b1579a1516959fa861ec6c8982f8581b5cba283120096bc4a10bdcf25d10c1b",
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
      "basis": "c896795b8e8bab68d05ae78d64c9cbcda1fdb104",
      "sources": {
        "sfddb92e438ca": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L14-L16",
        "s7cafe1b17afd": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L40-L54"
      }
    },
    "dns": {
      "name": "BIND dig documentation",
      "basis": "9.18.39",
      "sources": {
        "s54cff06bb882": "https://bind9.readthedocs.io/en/v9.18.39/manpages.html"
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
    "owasp-takeover": {
      "name": "OWASP subdomain takeover prevention",
      "basis": "668ba7db3d0da5868b8a0305c259f7f6914a6ecd",
      "sources": {
        "s03e38fd5f89d": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Subdomain_Takeover_Prevention_Cheat_Sheet.md#L5",
        "sf5a4befe8112": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Subdomain_Takeover_Prevention_Cheat_Sheet.md#L43-L44",
        "s33c539162561": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Subdomain_Takeover_Prevention_Cheat_Sheet.md#L98-L105"
      }
    },
    "wstg": {
      "name": "OWASP Web Security Testing Guide",
      "basis": "v4.2",
      "sources": {
        "s62c309021e80": "https://github.com/OWASP/wstg/blob/v4.2/document/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/10-Test_for_Subdomain_Takeover.md#L9-L14",
        "s39a0e1d42b51": "https://github.com/OWASP/wstg/blob/v4.2/document/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/10-Test_for_Subdomain_Takeover.md#L109"
      }
    },
    "dns-rfcs": {
      "name": "DNS caching RFCs",
      "basis": "unknown",
      "sources": {
        "s0d5c3bb5aad8": "https://www.rfc-editor.org/rfc/rfc1034#section-3.6",
        "s8bc007a2299d": "https://www.rfc-editor.org/rfc/rfc1035#section-3.2.1",
        "s3b645146ca75": "https://www.rfc-editor.org/rfc/rfc2181#section-8",
        "s78f445a994d7": "https://www.rfc-editor.org/rfc/rfc8767#section-4",
        "s1d32db254435": "https://www.rfc-editor.org/rfc/rfc2308#section-2"
      }
    },
    "owasp-docs": {
      "name": "OWASP security guidance",
      "basis": "668ba7db3d0da5868b8a0305c259f7f6914a6ecd",
      "sources": {
        "seb866a1f94e9": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Secrets_Management_Cheat_Sheet.md#L214-L218"
      }
    },
    "entra-docs": {
      "name": "Microsoft Entra revocation model",
      "basis": "231747abc59ae3d50c74e215c1cdd592eb980723",
      "sources": {
        "s983f45259faa": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/users/users-revoke-access.md#L62",
        "scb38e683ae3f": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/users/users-revoke-access.md#L96-L106",
        "s9ff4d6ed4cfe": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity-platform/access-tokens.md#L54-L60",
        "sca6feea4b601": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/concept-continuous-access-evaluation.md#L21-L25"
      }
    },
    "cloudflare-access": {
      "name": "Cloudflare Access and origin configuration",
      "basis": "c896795b8e8bab68d05ae78d64c9cbcda1fdb104",
      "sources": {
        "sf2dbab0fc574": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/access-settings/session-management.mdx#L159-L186",
        "sa0e3eb928f4a": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/access-settings/session-management.mdx#L190-L195"
      }
    },
    "oauth2-proxy": {
      "name": "OAuth2 Proxy",
      "basis": "v7.15.4",
      "sources": {
        "s32cedbc14f60": "https://github.com/oauth2-proxy/oauth2-proxy/blob/v7.15.4/docs/docs/configuration/overview.md#L126-L130"
      }
    },
    "authelia": {
      "name": "Authelia",
      "basis": "v4.39.28",
      "sources": {
        "sc844fe82794f": "https://github.com/authelia/authelia/blob/v4.39.28/docs/content/configuration/session/introduction.md#L220-L221"
      }
    },
    "oauth-revocation": {
      "name": "OAuth 2.0 Token Revocation RFC",
      "basis": "unknown",
      "sources": {
        "s3383c9f41cc2": "https://www.rfc-editor.org/rfc/rfc7009.html#section-2.1"
      }
    },
    "nist": {
      "name": "NIST digital identity guidelines",
      "basis": "SP 800-63B-4",
      "sources": {
        "s2a689905c161": "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-63b-4.pdf"
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
        "s94d055784840": "https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/config.py",
        "s9d6f5fb157de": "https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py"
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
    },
    "le": {
      "name": "Let's Encrypt documentation",
      "basis": "unknown",
      "sources": {
        "s9ff2d787c618": "https://letsencrypt.org/docs/"
      }
    }
  },
  "claims": {
    "outside": {"text": "Run exposure checks from a second network; host-local curl and ss do not establish outside reachability or platform firewall behaviour.", "components": ["nmap"], "sources": ["nmap:sf8404f695ccd", "nmap:sb7d0e7eb5141"], "status": "REASONED"},
    "tcp-scan": {"text": "Sweep authorized hosts with nmap -Pn -p-; the guide also gives an nc port loop. Use the house placeholder guard for both. Ubuntu noble netcat-openbsd documents -v verbosity, -z scanning and -w timeout; BusyBox 1.36.1 small nc lacks -v/-z and needs NC_EXTRA for -w, while its NC_110_COMPAT applet lists -v/-w and needs NC_EXTRA for -z. CentOS Stream 9 packages Ncat 7.92 as nc; its option behaviour and traditional/GNU netcat remain unestablished. As this guide's assessment, refusal or timeout shows only connection failure; unsupported-option errors, local errors and silent exits are inconclusive.", "components": ["nmap", "openbsd-nc", "ubuntu-nc", "c9s-nmap", "busybox"], "sources": ["nmap:sf8404f695ccd", "nmap:sb7d0e7eb5141", "openbsd-nc:s0c8b1a738e7b", "ubuntu-nc:s478aaf9a8975", "ubuntu-nc:sd7b31d3bc579", "ubuntu-nc:scc48da80246b", "c9s-nmap:sd06e83963e39", "c9s-nmap:s3ab25d24e37a", "busybox:s34bdee292f79", "busybox:sd707e18625cc", "busybox:s14b89daa008d"], "status": "REASONED"},
    "udp-scan": {"text": "The full port sweep is TCP only; inventory UDP services and probe their ports separately with nmap -sU.", "components": ["nmap"], "sources": ["nmap:sf8404f695ccd"], "status": "REASONED"},
    "all-addresses": {"text": "Check public IPv4, public IPv6 and platform URLs as well as the custom domain; one address cannot establish coverage of the others.", "components": ["nmap", "vercel"], "sources": ["nmap:sf8404f695ccd", "vercel:se6089d5c4e96"], "status": "REASONED"},
    "passive-index": {"text": "Cross-reference Shodan and Censys indexes for previously indexed exposure; indexed observations are not a fresh direct scan.", "components": ["shodan", "censys"], "sources": ["shodan:scf863db67f1e", "censys:s1e64a007a91f"], "status": "REASONED"},
    "initialize-secrets": {"text": "As this guide's advice, create owner/admin credentials and any session, JWT or cookie-signing secrets before opening application access, following authentication.md's signing-secret recommendation. For applications that give admin to whoever completes first-run setup, an unclaimed setup wizard is a race to become admin; Open WebUI at the recorded pin is one example, with its first account becoming admin. Access is fronting context only; other applications' bootstrap and signing-secret behaviour are not established here.", "components": ["access", "webui"], "sources": ["access:s7cafe1b17afd", "webui:s94d055784840", "webui:s9d6f5fb157de"], "status": "REASONED"},
    "registration": {"text": "As this guide's advice, disable open self-registration or restrict it to an allowlisted domain before opening application access; authentication.md covers allowlisting after federated login. Open WebUI at the recorded pin defaults ENABLE_SIGNUP and ENABLE_LOGIN_FORM to true with authentication enabled; an empty database bypasses ENABLE_SIGNUP when the login form is enabled, and after accounts exist disabled signup refuses registration. Access is fronting context only; other applications' registration controls and domain enforcement are not established here.", "components": ["access", "webui"], "sources": ["access:s7cafe1b17afd", "webui:s94d055784840", "webui:s9d6f5fb157de"], "status": "REASONED"},
    "fronting-order": {"text": "As this guide's advice, install TLS and any proxy authentication before opening application access: use DNS-01 before opening inbound access, or open only the challenge port during issuance while keeping application access blocked. Per free-certificates.md, HTTP-01 requires inbound port 80 and TLS-ALPN-01 requires inbound port 443; DNS-01 needs no inbound port. These challenge requirements do not establish this deployment order. Cloudflare recommends creating Access before the tunnel route and warns that without it the published app is public; publicly routable origins need separate IP protection. The general order remains this guide's advice.", "components": ["access", "le"], "sources": ["access:s7cafe1b17afd", "access:sfddb92e438ca", "le:s9ff2d787c618"], "status": "REASONED"},
    "setup-route": {"text": "After initialization, restart and retry the initial-setup URL; it must refuse to mint a second admin, not silently succeed (this guide's test expectation). Open WebUI's signup handler illustrates first-account bootstrap and refusal when accounts exist and signup is disabled; it does not establish every application's setup route or a deployed restart result. Access is fronting context only.", "components": ["access", "webui"], "sources": ["access:s7cafe1b17afd", "webui:s9d6f5fb157de"], "status": "REASONED"},
    "preview-standard": {"text": "Vercel Standard Protection is available on every plan and gates previews and generated deployment URLs while leaving the production domain open.", "components": ["vercel"], "sources": ["vercel:se6089d5c4e96"], "status": "REASONED"},
    "preview-all": {"text": "All Deployments also protects production; pairing it with Vercel Authentication became free on every plan on 9 September 2026, with no paid add-on.", "components": ["vercel"], "sources": ["vercel:se6089d5c4e96", "vercel:s7836e043434a"], "status": "REASONED"},
    "preview-gate": {"text": "Apply a fronting gate such as a Cloudflare Access policy to preview hostnames the platform gate does not cover. The pinned Cloudflare instructions establish the Access gate, not the platform's coverage of preview URLs.", "components": ["access", "vercel"], "sources": ["access:s7cafe1b17afd", "vercel:se6089d5c4e96"], "status": "REASONED"},
    "clone-secrets": {"text": "As this guide's advice, treat a clone's data the same as the original and rotate any inherited credential if the clone is less trusted than the source. That a clone can inherit credentials is this guide's assessment; clone credential inheritance and rotation are not established by the Access citation, which supplies fronting context only.", "components": ["access"], "sources": ["access:s7cafe1b17afd"], "status": "REASONED"},
    "dns-retirement": {"text": "Remove CNAME or A/AAAA records before releasing the app, load balancer or IP, and wait at least the old TTL per OWASP; WSTG supports record removal, not that wait. TTL expiry is not a hard bound: RFC 8767 permits serve-stale when authoritative refresh fails. This guide advises retaining the resource through the old TTL and confirmation of removal at every authoritative nameserver, and accounting for serve-stale before release; these checks do not prove all caches have refreshed. By this guide's inference, deletion does not flush cached answers and cached clients can reach the next owner of a reclaimable target. Reclaimability is OWASP's account of claimable CNAME targets and reassigned released IPs, not established for a particular platform. dig supports DNS inspection.", "components": ["dns", "owasp-takeover", "wstg", "dns-rfcs"], "sources": ["dns:s54cff06bb882", "owasp-takeover:s03e38fd5f89d", "owasp-takeover:sf5a4befe8112", "owasp-takeover:s33c539162561", "wstg:s62c309021e80", "wstg:s39a0e1d42b51", "dns-rfcs:s0d5c3bb5aad8", "dns-rfcs:s8bc007a2299d", "dns-rfcs:s3b645146ca75", "dns-rfcs:s78f445a994d7"], "status": "REASONED"},
    "retire-credentials": {"text": "After DNS retirement revoke deployment access policies, API/service credentials and dedicated database users (guide requirement). OWASP requires secure revocation of secrets that are no longer required or potentially compromised. The Access-policy citation covers fronting context only; the cited files do not establish removal of an Access application or policy or dropping database users.", "components": ["access", "owasp-docs"], "sources": ["access:s7cafe1b17afd", "owasp-docs:seb866a1f94e9"], "status": "REASONED"},
    "reverify": {"text": "Repeat outside scans and negative auth tests after upgrades, backup restores or network/auth changes; a restore can reintroduce a default account or reset a feature flag as this guide's assessment, not a general vendor fact. Docker 28.0.0 warns that hosts with IPv6 forwarding already enabled that relied on Docker setting FORWARD to DROP may need configuration changes; 28.3.3 fixes local-network access to loopback-intended published ports after firewalld reload. Open WebUI enables persistence by default; as this guide's conditional inference, restoring database values that override the environment after first launch could reinstate earlier signup settings. The files this guide cites do not establish database precedence or general restore behaviour; Nmap supports scanning only.", "components": ["nmap", "docker-notes", "webui"], "sources": ["nmap:sf8404f695ccd", "nmap:sb7d0e7eb5141", "docker-notes:s182da2bdd442", "docker-notes:sfbe11311e8a4", "webui:s94d055784840"], "status": "REASONED"},
    "certificate-monitor": {"text": "Monitor certificate expiry externally. As this guide's assessment, a renewal cron can silently fail while the host's view looks fine; its advice is a scheduled external openssl s_client or third-party monitor. Certbot v2.3.0 dry-run uses staging unless a custom server is set, saves no test certificates and runs applicable deploy hooks only with --run-deploy-hooks after success, using the active certificate. The user guide separates dry-run from live renewal; this guide infers that dry-run cannot establish the last real renewal's success. Nmap is outside-check context only.", "components": ["nmap", "openssl", "certbot-v230"], "sources": ["nmap:sf8404f695ccd", "openssl:s00aaf106164f", "openssl:s0856f4a58574", "certbot-v230:s5def4225771f", "certbot-v230:se96df86ba351", "certbot-v230:sc37d1ffd6192", "certbot-v230:s77de4441a9e5"], "status": "REASONED"},
    "offboarding": {"text": "When a person leaves, revoke every touched layer, not only the password: identity-provider membership, proxy/app sessions on each service, personal tokens and API keys (this guide's recommendation), and revoke the second factor alongside the account. Entra documents blocking sign-ins and revoking refresh tokens; application sessions require application revocation, access-token lifetimes vary, and supported-service CAE critical-event enforcement can take up to 15 minutes. Cloudflare documents per-user revocation, but an active IdP profile can start a new session; user logout stops acceptance of issued tokens in 20-30 seconds. OAuth2 Proxy documents cookie expiry/refresh; Authelia documents cookie expiry and session destruction, overridden by remember-me; neither passage establishes immediate per-user revocation. RFC 7009 specifies immediate invalidation with possible propagation delay and conditional access-token revocation support. OWASP requires secure revocation of unneeded or potentially compromised secrets. NIST requires CSPs to promptly invalidate authenticators when the CSP determines that the subscriber no longer meets its eligibility requirements. Where immediate revocation is unavailable, measure and shrink maximum time-to-revoke (this guide's recommendation). Provider-membership removal, every application's session-revocation mechanism and this deployment's measured maximum time-to-revoke remain unestablished. Follow authentication.md's REASONED replay check: matched requests must succeed before revocation, then old credentials must be refused without protected data within each configured maximum; these are test expectations, not observations.", "components": ["access", "owasp-docs", "entra-docs", "cloudflare-access", "oauth2-proxy", "authelia", "oauth-revocation", "nist"], "sources": ["access:s7cafe1b17afd", "owasp-docs:seb866a1f94e9", "entra-docs:s983f45259faa", "entra-docs:scb38e683ae3f", "entra-docs:s9ff4d6ed4cfe", "entra-docs:sca6feea4b601", "cloudflare-access:sf2dbab0fc574", "cloudflare-access:sa0e3eb928f4a", "oauth2-proxy:s32cedbc14f60", "authelia:sc844fe82794f", "oauth-revocation:s3383c9f41cc2", "nist:s2a689905c161"], "status": "REASONED"},
    "verify-ipv4": {"text": "From another network, nmap -Pn -p- should find only intended TCP ports; unintended open ports fail, and errors or an unexecuted scan are inconclusive.", "components": ["nmap"], "sources": ["nmap:sf8404f695ccd", "nmap:sb7d0e7eb5141"], "status": "REASONED", "verify": [1]},
    "verify-ipv6": {"text": "Repeat the full TCP sweep over the public IPv6 address with -6; a scan that did not run is inconclusive.", "components": ["nmap"], "sources": ["nmap:sf8404f695ccd", "nmap:sb7d0e7eb5141"], "status": "REASONED", "verify": [1]},
    "verify-dns": {"text": "curl failure does not prove DNS removal; resolver A/AAAA/CNAME answers need investigation and empty output is inconclusive. Check every authoritative server with +norecurse for NXDOMAIN or NOERROR/NODATA without CNAME; SERVFAIL, referral and timeout are inconclusive.", "components": ["dns", "dns-rfcs"], "sources": ["dns:s54cff06bb882", "dns-rfcs:s1d32db254435"], "status": "REASONED", "verify": [1]},
    "verify-certificate": {"text": "The scheduled external s_client probe checks hostname and verification errors and pipes the certificate to x509 -enddate. No observed outcome is recorded; Nmap is outside-check context only.", "components": ["nmap", "openssl"], "sources": ["nmap:sf8404f695ccd", "openssl:s00aaf106164f", "openssl:s0856f4a58574"], "status": "REASONED", "verify": [1]}
  }
}
````
<!-- version-basis:end -->
