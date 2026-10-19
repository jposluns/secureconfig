# Free publicly trusted certificates (ACME)

Written against Let's Encrypt documentation (no recorded version), Certbot reconfigure minimum 2.3.0, Certbot user guide and source v2.3.0, Certbot Cloudflare DNS plugin v2.3.0, Caddy automatic HTTPS v2.11.4, certmagic ACME implementation v0.25.3, and Traefik ACME documentation v3.5, plus 3 more recorded bases; 3 further sources carry no recorded version. Metadata reviewed 2026-10-17; documentation checked September 2026. The guide records 31 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

Publicly trusted certificates are free through ACME certificate authorities such as Let's Encrypt and ZeroSSL. Browsers and libraries accept them without any client-side configuration, which is why this guide assesses them as the correct choice for every service with a public DNS name. Use [self-signed.md](self-signed.md) only when no public domain exists; a host that cannot accept inbound connections can still get a publicly trusted certificate through the DNS-01 challenge (below), or serve behind [cloudflare.md](cloudflare.md).

## Prerequisites

- A public DNS record (`A`/`AAAA` or `CNAME`) pointing at the server, for the HTTP-01 and TLS-ALPN-01 challenges; the DNS-01 challenge instead needs only control of the challenge `TXT` record and can certify a host with no public address record or inbound port.
- For the HTTP-01 challenge: inbound port 80 reachable from the internet.
- For the TLS-ALPN-01 challenge: inbound port 443. Caddy's ACME issuer enables this challenge when DNS-01 is not configured and TLS-ALPN-01 is not disabled; Traefik also uses it. Caddy can use an alternate local port if port 443 forwards to it.
- For the DNS-01 challenge (required for wildcard certificates), automated issuance and renewal need an automated way to update the provider's TXT record; this guide advises using a DNS plugin and scoped API credentials, while Certbot also documents manual authentication hooks for automated challenges. Manual DNS-01 is also possible with `certbot certonly --manual --preferred-challenges dns`, creating the TXT record by hand; the Certbot v2.3.0 guide says certificates obtained this way do not auto-renew without an authentication hook (`--manual-auth-hook`) that automates the challenge.

If none of these is possible, use [cloudflare.md](cloudflare.md) instead.

## Certbot with Let's Encrypt

Certbot is the reference ACME client. Install it from your distribution or via snap:

```bash
# Debian/Ubuntu
sudo apt install certbot python3-certbot-nginx python3-certbot-apache

# Any distribution with snapd
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

Issue and install in one step when certbot supports your web server:

```bash
sudo certbot --nginx  -d example.com -d www.example.com
sudo certbot --apache -d example.com -d www.example.com
```

Issue only the certificate when you configure the server yourself, or when no web server is running yet:

```bash
# Standalone: certbot binds port 80 itself; stop anything using it first (and for a host whose web server will own :80, switch this certificate to --webroot or the server plugin, or add pre/post hooks that free the port, so unattended renewal can still bind)
sudo certbot certonly --standalone -d example.com

# Webroot: the existing web server keeps running and serves the challenge files
sudo certbot certonly --webroot -w /var/www/html -d example.com
```

Wildcard certificates require the DNS-01 challenge. For automated issuance and renewal, use a DNS plugin as this guide advises (for example `python3-certbot-dns-cloudflare`). Scope provider API credentials to least privilege: use a Cloudflare API token with `Zone:DNS:Edit` on only the required zones; never use the account-wide Global API Key. Keep the credentials file readable only by root (`chmod 600` the file in a `700` directory; Certbot warns when other users can read it):

```bash
sudo certbot certonly --dns-cloudflare \
  --dns-cloudflare-credentials /root/.secrets/cloudflare.ini \
  -d example.com -d "*.example.com"
```

Certificates land in stable paths that server configuration should reference directly:

```
/etc/letsencrypt/live/example.com/fullchain.pem   # certificate plus chain
/etc/letsencrypt/live/example.com/privkey.pem     # private key
```

## Renewal

Let's Encrypt certificates are valid for 90 days at the time of writing, so renewal must be automated. The Certbot v2.3.0 guide says most installations come with a scheduled `certbot renew` task and says that, on Linux and BSD, you can check cron or systemd timers if unsure. Confirm that your installation (package and snap installs included) has a working scheduled `certbot renew` task, and reload the server after each renewal:

```bash
sudo systemctl list-timers | grep -i certbot       # a certbot timer must be listed; for cron, /etc/crontab or /etc/cron.*/* must contain certbot renew
sudo certbot renew --dry-run --run-deploy-hooks    # test renewal and the reload hook together
```

Install the reload hook durably: pass `--deploy-hook "systemctl reload nginx"` on the initial `certonly`/`run` (Certbot saves it to the renewal config only when a certificate is actually obtained or renewed), drop an executable script into `/etc/letsencrypt/renewal-hooks/deploy/` (it runs after every successful renewal), or add it later with `certbot reconfigure` (Certbot 2.3.0 and later). In Certbot v2.3.0, a bare `certbot renew --deploy-hook ...` skips renewal when no certificate is due and does not save that hook to a renewal configuration; use one of the durable methods above. This guide assesses a certificate that issues once and then expires in production as the most common ACME failure, so monitor the served certificate's expiry and alert on renewal failure rather than relying on CA reminder emails; the dry run belongs in your deployment checklist.

Lifetimes are getting shorter. Per Let's Encrypt as of September 2026: 6-day short-lived certificates are available now to every subscriber; the default `classic` profile moves to 64-day certificates on 2027-02-10 and to 45-day certificates on 2028-02-16; and industry rules cap publicly trusted certificates at 47 days from 2029-03-15. This guide assesses that any renewal step involving a person will fail at those lifetimes and that the automation above is the only viable path. Let's Encrypt also switched off its OCSP service on 2025-08-06 and publishes revocation only through CRLs, so do not add OCSP stapling directives for Let's Encrypt certificates.

## Rate limits

Let's Encrypt enforces per-domain issuance limits. Test against the staging environment (`certbot --staging` or `--test-cert`) until the configuration works, then issue the real certificate. Current limits: https://letsencrypt.org/docs/rate-limits/

## CAA records

A CAA DNS record restricts which certificate authorities may issue for your domain, limiting mis-issuance. Set it to the CA you use, for example `example.com. CAA 0 issue "letsencrypt.org"` for Let's Encrypt. Certificate-transparency monitoring detects mis-issuance after the fact; CAA constrains it beforehand, so treat the two as complementary, not as alternatives.

## Alternatives

- **ZeroSSL**: free certificates over ACME. Some clients need External Account Binding (EAB) credentials from the ZeroSSL dashboard; the acme.sh client registers with ZeroSSL by default.
- **acme.sh**: a dependency-light shell ACME client supporting many DNS providers, useful where certbot is unavailable. Install from the repository release rather than piping a downloaded script straight into a shell. https://github.com/acmesh-official/acme.sh
- **Caddy and Traefik**: obtain and renew certificates themselves with no external client; see [caddy.md](caddy.md) and [traefik.md](traefik.md). This guide assesses it as the lowest-effort correct option for new deployments.
- **Cloudflare origin certificates**: available on Cloudflare's Free plan; Cloudflare's page refers to long-lived origin CA certificates and says the validity period is chosen at creation. Cloudflare says they only encrypt traffic between Cloudflare and the origin server, not traffic from client browsers to the origin, and that visitors may see untrusted certificate errors if Cloudflare is paused or proxying is disabled; use them only for origins that receive traffic only through Cloudflare-proxied records; see [cloudflare.md](cloudflare.md).

## Verify

REASONED: certificate inventory and HTTPS/certificate inspection follow the cited Certbot and Let's Encrypt guidance and the cited curl and OpenSSL documentation. No deployment hostname or issued certificate was supplied for live checks, and this guide records no run.

```bash
sudo certbot certificates                       # what is issued and when it expires
host=REPLACE_WITH_YOUR_HOSTNAME                    # your deployment's public hostname, not example.com (which serves a live page and would pass spuriously)
curl -q -sI "https://$host/"                        # succeeds without -k
openssl s_client -connect "$host:443" -servername "$host" \
  -verify_hostname "$host" -verify_return_error </dev/null \
  | openssl x509 -noout -issuer -dates
```

REASONED: preceding block; certificate inventory, HTTPS access and served-certificate hostname, trust, issuer and date inspection follow the cited Certbot and Let's Encrypt guidance and the cited curl and OpenSSL documentation; no deployment hostname or issued certificate was supplied, and no live result is recorded. A certificate alone does not protect anything: continue with the server guide for your stack and with [authentication.md](authentication.md).

## Sources (checked September 2026)

- Let's Encrypt documentation: https://letsencrypt.org/docs/
- Certbot instructions (rolling documentation, checked September 2026): https://certbot.eff.org/
- Certbot reconfigure (2.3.0 and later; v2.3.0 user guide): https://raw.githubusercontent.com/certbot/certbot/v2.3.0/certbot/docs/using.rst
- Certbot manual DNS-01 and renewal hooks: https://eff-certbot.readthedocs.io/en/stable/using.html#manual
- Certbot DNS plugins: https://eff-certbot.readthedocs.io/en/stable/using.html#dns-plugins
- ZeroSSL: https://zerossl.com/
- acme.sh: https://github.com/acmesh-official/acme.sh
- Let's Encrypt certificate lifetimes: https://letsencrypt.org/docs/cert-lifetimes/
- Let's Encrypt lifetime reduction schedule: https://letsencrypt.org/2025/12/02/from-90-to-45
- Let's Encrypt OCSP end of life: https://letsencrypt.org/2025/08/06/ocsp-service-has-reached-end-of-life
- Let's Encrypt CAA requirements: https://letsencrypt.org/docs/caa/
- Caddy v2.11.4 automatic certificate acquisition and renewal (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/autohttps.go#L62-L63
- Caddy v2.11.4 ACME TLS-ALPN challenge settings (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddytls/acmeissuer.go#L280-L296
- Caddy v2.11.4 builds its ACME issuer template at provisioning (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddytls/acmeissuer.go#L245-L249
- Caddy v2.11.4 passes its ACME issuer template to certmagic (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddytls/acmeissuer.go#L321-L328
- Caddy v2.11.4 pins certmagic v0.25.3 (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/go.mod#L12-L12
- certmagic v0.25.3 TLS-ALPN-01 solver selection (checked October 2026): https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeclient.go#L188-L226
- certmagic v0.25.3 TLS-ALPN challenge listener port (checked October 2026): https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeclient.go#L304-L313
- certmagic v0.25.3 alternate TLS-ALPN port forwarding (checked October 2026): https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeissuer.go#L116-L120
- certmagic v0.25.3 issuer defaults for the DNS-01 solver and TLS-ALPN setting (checked October 2026): https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeissuer.go#L222-L236
- certmagic v0.25.3 TLS-ALPN challenge port 443 (checked October 2026): https://github.com/caddyserver/certmagic/blob/v0.25.3/certmagic.go#L473-L475
- certmagic v0.25.3 `DefaultACME` values (checked October 2026): https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeissuer.go#L647-L654
- Traefik v3.5 ACME renewal and challenges (checked October 2026): https://doc.traefik.io/traefik/v3.5/reference/install-configuration/tls/certificate-resolvers/acme/
- OpenSSL 3.0 `s_client` connection and certificate verification (checked October 2026): https://docs.openssl.org/3.0/man1/openssl-s_client/
- OpenSSL 3.0 `x509` issuer and validity dates (checked October 2026): https://docs.openssl.org/3.0/man1/openssl-x509/
- curl curl-8_12_1 HEAD requests (checked October 2026): https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/head.md#L21-L22
- curl curl-8_12_1 normal certificate verification and `--insecure` (checked October 2026): https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/insecure.md#L21-L28
- Certbot v2.3.0 scheduled renewal guidance (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L808-L825
- Certbot v2.3.0 renew selection (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L632-L640
- Certbot v2.3.0 renewal option persistence (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L704-L710
- Certbot v2.3.0 deploy hooks (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L659-L684
- Certbot v2.3.0 DNS plugins (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L194-L220
- Certbot v2.3.0 manual DNS-01 and renewal (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L222-L265
- Certbot v2.3.0 deploy-hook argument storage (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/cli/cli_utils.py#L227-L231
- Certbot v2.3.0 renewal option list (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/renewal.py#L40-L53
- Certbot v2.3.0 due-renewal branch (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/renewal.py#L509-L534
- Certbot v2.3.0 relevant saved values (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L295-L312
- Certbot v2.3.0 initial renewal configuration (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L1120-L1128
- Certbot v2.3.0 renewed configuration (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L1243-L1249
- Certbot v2.3.0 Cloudflare DNS credentials (checked October 2026): <https://github.com/certbot/certbot/blob/v2.3.0/certbot-dns-cloudflare/certbot_dns_cloudflare/__init__.py#L24-L39>
- Certbot v2.3.0 Cloudflare DNS credential permissions (checked October 2026): <https://github.com/certbot/certbot/blob/v2.3.0/certbot-dns-cloudflare/certbot_dns_cloudflare/__init__.py#L61-L78>
- Cloudflare Origin CA (checked October 2026): https://developers.cloudflare.com/ssl/origin-configuration/origin-ca/


<!-- version-basis:start -->
## About the AI assistant section below

The rest of this file is generated by the repository's tooling and written for AI assistants rather than for people. It records the versions this guide was written against, the guide's claims with a status for each (demonstrated by a check that ran, or reasoned from the cited sources), and the mapping from each claim to its sources. You are welcome to read it, but it is dense and can be hard to take in.

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/free-certificates.md
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

- le: Let's Encrypt documentation (unknown)
- zerossl: ZeroSSL (unknown)
- certbot: Certbot documentation (unknown)
- reconfigure: Certbot reconfigure minimum (2.3.0)
- acme: acme.sh (unknown)
- certbot-v230: Certbot user guide and source (v2.3.0)
- certbot-dns-cloudflare-v230: Certbot Cloudflare DNS plugin (v2.3.0)
- caddy: Caddy automatic HTTPS (v2.11.4)
- certmagic: certmagic ACME implementation (v0.25.3)
- traefik: Traefik ACME documentation (v3.5)
- cloudflare-origin-ca: Cloudflare Origin CA documentation (checked October 2026)
- openssl-cli: OpenSSL certificate commands (3.0)
- curl-source: curl command documentation (curl-8_12_1)

Claims (full source mapping in the JSON block below):

- public-trust (REASONED; le, zerossl): ACME CAs such as Let's Encrypt and ZeroSSL issue free publicly trusted certificates; this guide advises preferring them for public DNS names, including private hosts using DNS-01.
- http-challenge (REASONED; le): HTTP-01 needs a public A/AAAA or CNAME pointing to the server and inbound internet access to port 80.
- alpn-challenge (REASONED; le, caddy, certmagic, traefik): TLS-ALPN-01 needs a public DNS record and inbound port 443; Caddy's ACME issuer enables the TLS-ALPN-01 solver when DNS-01 is not configured and TLS-ALPN-01 is not disabled, and can use an alternate local port if port 443 forwards to it; Traefik also uses TLS-ALPN-01.
- dns-challenge (REASONED; le, certbot, certbot-v230): DNS-01 needs control of the challenge TXT record, no public address record or inbound port, and supports wildcards; automated issuance and renewal need an automated way to update TXT records, and this guide advises a provider DNS plugin and scoped API credentials, while Certbot also supports manual DNS-01 and an authentication hook for automatic renewal.
- certbot-install (REASONED; certbot): Install Certbot and nginx/Apache plugins from the distribution, or the classic snap with /usr/bin/certbot pointing to /snap/bin/certbot.
- server-plugins (REASONED; certbot): certbot --nginx or --apache issues and installs certificates for the supplied domain names when the server is supported.
- standalone (REASONED; certbot): certonly --standalone binds port 80; stop its current owner and arrange webroot, a server plugin or port-freeing hooks for unattended renewal.
- webroot (REASONED; certbot): certonly --webroot uses /var/www/html to serve challenge files while the existing web server keeps running.
- dns-credentials (REASONED; certbot, certbot-dns-cloudflare-v230): The Cloudflare DNS plugin uses a credentials file and a Zone:DNS:Edit token limited to required zones; this guide requires never using the Global API Key and protecting the file with mode 600 in a 700 directory.
- certificate-paths (REASONED; certbot): Configure servers against stable /etc/letsencrypt/live/example.com/fullchain.pem and privkey.pem paths for the chain and private key.
- renewal-schedule (REASONED; certbot, certbot-v230): The Certbot v2.3.0 user guide says most installations have a scheduled task running certbot renew and says that, on Linux and BSD, you can check cron or systemd timers if unsure; this guide requires confirming the task and testing renewal plus reload with --dry-run --run-deploy-hooks, including package and snap installations.
- deploy-hook (REASONED; certbot, certbot-v230): This guide requires persisting a reload hook during successful initial issuance or successful renewal, or installing an executable in renewal-hooks/deploy; Certbot v2.3.0 saves the renewal-relevant options set on the command line to a lineage after successful renewal, and a renew --deploy-hook invocation with no renewal due does not save that hook.
- reconfigure (REASONED; reconfigure): certbot reconfigure can add the reload hook later on Certbot 2.3.0 and later.
- expiry-monitoring (REASONED; le, certbot): Monitor the served certificate's expiry and renewal failures instead of relying on CA reminder emails; include a dry run in the deployment checklist. This guide assesses that any renewal step involving a person will fail at those scheduled shorter certificate lifetimes and that unattended automation is the only viable path.
- default-lifetime (REASONED; le): At the guide's September 2026 documentation check, Let's Encrypt's default certificate lifetime is 90 days.
- short-lifetime (REASONED; le): Optional 6-day short-lived certificates are available to every subscriber as of the guide's September 2026 check.
- lifetime-schedule (REASONED; le): The classic profile moves to 64 days on 2027-02-10 and 45 days on 2028-02-16; industry rules cap publicly trusted certificates at 47 days from 2029-03-15.
- revocation (REASONED; le): Let's Encrypt ended OCSP on 2025-08-06 and publishes revocation through CRLs only; do not add OCSP stapling directives for its certificates.
- staging (REASONED; le, certbot): Let's Encrypt limits per-domain issuance; test with certbot --staging or --test-cert before real issuance.
- caa (REASONED; le): CAA restricts issuing CAs, using issue letsencrypt.org for Let's Encrypt; certificate-transparency monitoring detects mis-issuance afterwards and complements CAA.
- zerossl-eab (REASONED; zerossl): ZeroSSL offers free ACME certificates; some clients need dashboard EAB credentials.
- acme-default (REASONED; acme): acme.sh registers with ZeroSSL by default.
- acme-install (REASONED; acme): acme.sh is a shell ACME client supporting many DNS providers; the guide recommends installation from a repository release instead of piping a download into a shell.
- server-automation (REASONED; le, caddy, traefik): This guide advises Caddy or Traefik for built-in issuance and renewal without an external client; it assesses them as the lowest-effort correct option for new deployments.
- origin-certificates (REASONED; le, cloudflare-origin-ca): Cloudflare lists Origin CA certificates on its Free plan, refers to long-lived origin CA certificates and says the validity period is chosen at creation, says they only encrypt traffic between Cloudflare and the origin, and warns that visitors may see untrusted certificate errors when Cloudflare is paused or proxying is disabled; this guide requires using them only for origins that receive traffic only through Cloudflare-proxied records.
- verify-inventory (REASONED; certbot): certbot certificates lists issued certificates and their expiry dates.
- verify-https (REASONED; le, curl-source): Use the deployment's public hostname rather than example.com; curl HTTPS should succeed without -k.
- verify-certificate (REASONED; le, openssl-cli): The OpenSSL probe targets the hostname on port 443 with SNI, hostname verification and verification errors enabled, then displays issuer and dates.
- authentication (REASONED; le): A certificate alone is insufficient protection; continue with server controls and authentication.
- dns-automation (REASONED; certbot, certbot-v230): For automated DNS-01 issuance and renewal, this guide advises using a provider DNS plugin and least-privilege API credentials; Certbot also documents manual TXT entry and authentication hooks that automate the challenge.
- dns-manual (REASONED; certbot, certbot-v230): certbot certonly --manual --preferred-challenges dns permits hand-created TXT records; the Certbot v2.3.0 guide says certificates created with --manual do not support automatic renewal without a --manual-auth-hook that automates the challenge.

````json
{
  "schema": 1,
  "checked": "2026-10-17",
  "documentation_checked": "2026-09",
  "body_sha256": "1f578874874b2d4b757f649adda8745f4d241949ddc0c71bfffb7315a7158257",
  "components": {
    "le": {
      "name": "Let's Encrypt documentation",
      "basis": "unknown",
      "sources": {
        "s9ff2d787c618": "https://letsencrypt.org/docs/",
        "s01388c85c5d6": "https://letsencrypt.org/docs/cert-lifetimes/",
        "s4406ef210fff": "https://letsencrypt.org/2025/12/02/from-90-to-45",
        "s21efa5995c48": "https://letsencrypt.org/2025/08/06/ocsp-service-has-reached-end-of-life",
        "saf908bcd2143": "https://letsencrypt.org/docs/caa/"
      }
    },
    "zerossl": {
      "name": "ZeroSSL",
      "basis": "unknown",
      "sources": {
        "sddca28a3381b": "https://zerossl.com/"
      }
    },
    "certbot": {
      "name": "Certbot documentation",
      "basis": "unknown",
      "sources": {
        "s44faaf4eb7d7": "https://certbot.eff.org/",
        "s7b60a00cadf3": "https://eff-certbot.readthedocs.io/en/stable/using.html#manual",
        "s875be163b4c1": "https://eff-certbot.readthedocs.io/en/stable/using.html#dns-plugins"
      }
    },
    "reconfigure": {
      "name": "Certbot reconfigure minimum",
      "basis": "2.3.0",
      "sources": {
        "s0dee7d6d65ba": "https://raw.githubusercontent.com/certbot/certbot/v2.3.0/certbot/docs/using.rst"
      }
    },
    "acme": {
      "name": "acme.sh",
      "basis": "unknown",
      "sources": {
        "sa635c50fc1f9": "https://github.com/acmesh-official/acme.sh"
      }
    },
    "certbot-v230": {
      "name": "Certbot user guide and source",
      "basis": "v2.3.0",
      "sources": {
        "s725109195132": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L808-L825",
        "s2f25bc233392": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L632-L640",
        "s11c7994242fc": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L704-L710",
        "sbb0c60d635ee": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L659-L684",
        "s55ec19f37395": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L194-L220",
        "s5bf4ff9fbe76": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L222-L265",
        "s7a053488f705": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/cli/cli_utils.py#L227-L231",
        "sa18c858c4e49": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/renewal.py#L40-L53",
        "s2e4bd79a7795": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/renewal.py#L509-L534",
        "s1910987bfd8c": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L295-L312",
        "s9c6118b72e0a": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L1120-L1128",
        "s3e22e32a2862": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L1243-L1249"
      }
    },
    "certbot-dns-cloudflare-v230": {
      "name": "Certbot Cloudflare DNS plugin",
      "basis": "v2.3.0",
      "sources": {
        "s3f07ef3d544d": "https://github.com/certbot/certbot/blob/v2.3.0/certbot-dns-cloudflare/certbot_dns_cloudflare/__init__.py#L24-L39",
        "sc3b33fa2c90f": "https://github.com/certbot/certbot/blob/v2.3.0/certbot-dns-cloudflare/certbot_dns_cloudflare/__init__.py#L61-L78"
      }
    },
    "caddy": {
      "name": "Caddy automatic HTTPS",
      "basis": "v2.11.4",
      "sources": {
        "s9683cb8d689f": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/autohttps.go#L62-L63",
        "s409f9221aec2": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddytls/acmeissuer.go#L280-L296",
        "s80dbf0751153": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddytls/acmeissuer.go#L245-L249",
        "s5216789c9341": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddytls/acmeissuer.go#L321-L328"
      }
    },
    "certmagic": {
      "name": "certmagic ACME implementation",
      "basis": "v0.25.3",
      "sources": {
        "s61e3cba719df": "https://github.com/caddyserver/caddy/blob/v2.11.4/go.mod#L12-L12",
        "s8782e006523b": "https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeclient.go#L188-L226",
        "s465c4ddcc92f": "https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeclient.go#L304-L313",
        "sc1e2ddefe5ed": "https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeissuer.go#L116-L120",
        "sd423f53faa1a": "https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeissuer.go#L222-L236",
        "sf2fbc79f6542": "https://github.com/caddyserver/certmagic/blob/v0.25.3/certmagic.go#L473-L475",
        "s1c3236df58b9": "https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeissuer.go#L647-L654"
      }
    },
    "traefik": {
      "name": "Traefik ACME documentation",
      "basis": "v3.5",
      "sources": {
        "s418a6b1ad09b": "https://doc.traefik.io/traefik/v3.5/reference/install-configuration/tls/certificate-resolvers/acme/"
      }
    },
    "cloudflare-origin-ca": {
      "name": "Cloudflare Origin CA documentation",
      "basis": "checked October 2026",
      "sources": {
        "s1e15de5c9f36": "https://developers.cloudflare.com/ssl/origin-configuration/origin-ca/"
      }
    },
    "openssl-cli": {
      "name": "OpenSSL certificate commands",
      "basis": "3.0",
      "sources": {
        "s00aaf106164f": "https://docs.openssl.org/3.0/man1/openssl-s_client/",
        "s0856f4a58574": "https://docs.openssl.org/3.0/man1/openssl-x509/"
      }
    },
    "curl-source": {
      "name": "curl command documentation",
      "basis": "curl-8_12_1",
      "sources": {
        "s76f69702c9d5": "https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/head.md#L21-L22",
        "s60820cd231e1": "https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/insecure.md#L21-L28"
      }
    }
  },
  "claims": {
    "public-trust": {"text": "ACME CAs such as Let's Encrypt and ZeroSSL issue free publicly trusted certificates; this guide advises preferring them for public DNS names, including private hosts using DNS-01.", "components": ["le", "zerossl"], "sources": ["le:s9ff2d787c618", "zerossl:sddca28a3381b"], "status": "REASONED"},
    "http-challenge": {"text": "HTTP-01 needs a public A/AAAA or CNAME pointing to the server and inbound internet access to port 80.", "components": ["le"], "sources": ["le:s9ff2d787c618"], "status": "REASONED"},
    "alpn-challenge": {"text": "TLS-ALPN-01 needs a public DNS record and inbound port 443; Caddy's ACME issuer enables the TLS-ALPN-01 solver when DNS-01 is not configured and TLS-ALPN-01 is not disabled, and can use an alternate local port if port 443 forwards to it; Traefik also uses TLS-ALPN-01.", "components": ["le", "caddy", "certmagic", "traefik"], "sources": ["le:s9ff2d787c618", "caddy:s409f9221aec2", "caddy:s80dbf0751153", "caddy:s5216789c9341", "certmagic:s61e3cba719df", "certmagic:s8782e006523b", "certmagic:s465c4ddcc92f", "certmagic:sc1e2ddefe5ed", "certmagic:sd423f53faa1a", "certmagic:sf2fbc79f6542", "certmagic:s1c3236df58b9", "traefik:s418a6b1ad09b"], "status": "REASONED"},
    "dns-challenge": {"text": "DNS-01 needs control of the challenge TXT record, no public address record or inbound port, and supports wildcards; automated issuance and renewal need an automated way to update TXT records, and this guide advises a provider DNS plugin and scoped API credentials, while Certbot also supports manual DNS-01 and an authentication hook for automatic renewal.", "components": ["le", "certbot", "certbot-v230"], "sources": ["le:s9ff2d787c618", "certbot:s7b60a00cadf3", "certbot:s875be163b4c1", "certbot-v230:s55ec19f37395", "certbot-v230:s5bf4ff9fbe76"], "status": "REASONED"},
    "certbot-install": {"text": "Install Certbot and nginx/Apache plugins from the distribution, or the classic snap with /usr/bin/certbot pointing to /snap/bin/certbot.", "components": ["certbot"], "sources": ["certbot:s44faaf4eb7d7"], "status": "REASONED"},
    "server-plugins": {"text": "certbot --nginx or --apache issues and installs certificates for the supplied domain names when the server is supported.", "components": ["certbot"], "sources": ["certbot:s44faaf4eb7d7"], "status": "REASONED"},
    "standalone": {"text": "certonly --standalone binds port 80; stop its current owner and arrange webroot, a server plugin or port-freeing hooks for unattended renewal.", "components": ["certbot"], "sources": ["certbot:s44faaf4eb7d7"], "status": "REASONED"},
    "webroot": {"text": "certonly --webroot uses /var/www/html to serve challenge files while the existing web server keeps running.", "components": ["certbot"], "sources": ["certbot:s44faaf4eb7d7"], "status": "REASONED"},
    "dns-credentials": {"text": "The Cloudflare DNS plugin uses a credentials file and a Zone:DNS:Edit token limited to required zones; this guide requires never using the Global API Key and protecting the file with mode 600 in a 700 directory.", "components": ["certbot", "certbot-dns-cloudflare-v230"], "sources": ["certbot:s44faaf4eb7d7", "certbot-dns-cloudflare-v230:s3f07ef3d544d", "certbot-dns-cloudflare-v230:sc3b33fa2c90f"], "status": "REASONED"},
    "certificate-paths": {"text": "Configure servers against stable /etc/letsencrypt/live/example.com/fullchain.pem and privkey.pem paths for the chain and private key.", "components": ["certbot"], "sources": ["certbot:s44faaf4eb7d7"], "status": "REASONED"},
    "renewal-schedule": {"text": "The Certbot v2.3.0 user guide says most installations have a scheduled task running certbot renew and says that, on Linux and BSD, you can check cron or systemd timers if unsure; this guide requires confirming the task and testing renewal plus reload with --dry-run --run-deploy-hooks, including package and snap installations.", "components": ["certbot", "certbot-v230"], "sources": ["certbot:s44faaf4eb7d7", "certbot-v230:s725109195132"], "status": "REASONED"},
    "deploy-hook": {"text": "This guide requires persisting a reload hook during successful initial issuance or successful renewal, or installing an executable in renewal-hooks/deploy; Certbot v2.3.0 saves the renewal-relevant options set on the command line to a lineage after successful renewal, and a renew --deploy-hook invocation with no renewal due does not save that hook.", "components": ["certbot", "certbot-v230"], "sources": ["certbot:s44faaf4eb7d7", "certbot-v230:s2f25bc233392", "certbot-v230:s11c7994242fc", "certbot-v230:sbb0c60d635ee", "certbot-v230:s7a053488f705", "certbot-v230:sa18c858c4e49", "certbot-v230:s2e4bd79a7795", "certbot-v230:s1910987bfd8c", "certbot-v230:s9c6118b72e0a", "certbot-v230:s3e22e32a2862"], "status": "REASONED"},
    "reconfigure": {"text": "certbot reconfigure can add the reload hook later on Certbot 2.3.0 and later.", "components": ["reconfigure"], "sources": ["reconfigure:s0dee7d6d65ba"], "status": "REASONED"},
    "expiry-monitoring": {"text": "Monitor the served certificate's expiry and renewal failures instead of relying on CA reminder emails; include a dry run in the deployment checklist. This guide assesses that any renewal step involving a person will fail at those scheduled shorter certificate lifetimes and that unattended automation is the only viable path.", "components": ["le", "certbot"], "sources": ["le:s4406ef210fff", "certbot:s44faaf4eb7d7"], "status": "REASONED"},
    "default-lifetime": {"text": "At the guide's September 2026 documentation check, Let's Encrypt's default certificate lifetime is 90 days.", "components": ["le"], "sources": ["le:s01388c85c5d6"], "status": "REASONED"},
    "short-lifetime": {"text": "Optional 6-day short-lived certificates are available to every subscriber as of the guide's September 2026 check.", "components": ["le"], "sources": ["le:s01388c85c5d6"], "status": "REASONED"},
    "lifetime-schedule": {"text": "The classic profile moves to 64 days on 2027-02-10 and 45 days on 2028-02-16; industry rules cap publicly trusted certificates at 47 days from 2029-03-15.", "components": ["le"], "sources": ["le:s01388c85c5d6", "le:s4406ef210fff"], "status": "REASONED"},
    "revocation": {"text": "Let's Encrypt ended OCSP on 2025-08-06 and publishes revocation through CRLs only; do not add OCSP stapling directives for its certificates.", "components": ["le"], "sources": ["le:s21efa5995c48"], "status": "REASONED"},
    "staging": {"text": "Let's Encrypt limits per-domain issuance; test with certbot --staging or --test-cert before real issuance.", "components": ["le", "certbot"], "sources": ["le:s9ff2d787c618", "certbot:s44faaf4eb7d7"], "status": "REASONED"},
    "caa": {"text": "CAA restricts issuing CAs, using issue letsencrypt.org for Let's Encrypt; certificate-transparency monitoring detects mis-issuance afterwards and complements CAA.", "components": ["le"], "sources": ["le:saf908bcd2143", "le:s9ff2d787c618"], "status": "REASONED"},
    "zerossl-eab": {"text": "ZeroSSL offers free ACME certificates; some clients need dashboard EAB credentials.", "components": ["zerossl"], "sources": ["zerossl:sddca28a3381b"], "status": "REASONED"},
    "acme-default": {"text": "acme.sh registers with ZeroSSL by default.", "components": ["acme"], "sources": ["acme:sa635c50fc1f9"], "status": "REASONED"},
    "acme-install": {"text": "acme.sh is a shell ACME client supporting many DNS providers; the guide recommends installation from a repository release instead of piping a download into a shell.", "components": ["acme"], "sources": ["acme:sa635c50fc1f9"], "status": "REASONED"},
    "server-automation": {"text": "This guide advises Caddy or Traefik for built-in issuance and renewal without an external client; it assesses them as the lowest-effort correct option for new deployments.", "components": ["le", "caddy", "traefik"], "sources": ["le:s9ff2d787c618", "caddy:s9683cb8d689f", "traefik:s418a6b1ad09b"], "status": "REASONED"},
    "origin-certificates": {"text": "Cloudflare lists Origin CA certificates on its Free plan, refers to long-lived origin CA certificates and says the validity period is chosen at creation, says they only encrypt traffic between Cloudflare and the origin, and warns that visitors may see untrusted certificate errors when Cloudflare is paused or proxying is disabled; this guide requires using them only for origins that receive traffic only through Cloudflare-proxied records.", "components": ["le", "cloudflare-origin-ca"], "sources": ["le:s9ff2d787c618", "cloudflare-origin-ca:s1e15de5c9f36"], "status": "REASONED"},
    "verify-inventory": {"text": "certbot certificates lists issued certificates and their expiry dates.", "components": ["certbot"], "sources": ["certbot:s44faaf4eb7d7"], "status": "REASONED", "verify": [1]},
    "verify-https": {"text": "Use the deployment's public hostname rather than example.com; curl HTTPS should succeed without -k.", "components": ["le", "curl-source"], "sources": ["le:s9ff2d787c618", "curl-source:s76f69702c9d5", "curl-source:s60820cd231e1"], "status": "REASONED", "verify": [1]},
    "verify-certificate": {"text": "The OpenSSL probe targets the hostname on port 443 with SNI, hostname verification and verification errors enabled, then displays issuer and dates.", "components": ["le", "openssl-cli"], "sources": ["le:s9ff2d787c618", "openssl-cli:s00aaf106164f", "openssl-cli:s0856f4a58574"], "status": "REASONED", "verify": [1]},
    "authentication": {"text": "A certificate alone is insufficient protection; continue with server controls and authentication.", "components": ["le"], "sources": ["le:s9ff2d787c618"], "status": "REASONED"},
    "dns-automation": {"text": "For automated DNS-01 issuance and renewal, this guide advises using a provider DNS plugin and least-privilege API credentials; Certbot also documents manual TXT entry and authentication hooks that automate the challenge.", "components": ["certbot", "certbot-v230"], "sources": ["certbot:s875be163b4c1", "certbot:s7b60a00cadf3", "certbot-v230:s55ec19f37395", "certbot-v230:s5bf4ff9fbe76"], "status": "REASONED"},
    "dns-manual": {"text": "certbot certonly --manual --preferred-challenges dns permits hand-created TXT records; the Certbot v2.3.0 guide says certificates created with --manual do not support automatic renewal without a --manual-auth-hook that automates the challenge.", "components": ["certbot", "certbot-v230"], "sources": ["certbot:s7b60a00cadf3", "certbot-v230:s5bf4ff9fbe76"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
