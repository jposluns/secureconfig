---
version_basis: {
  "schema": 1,
  "checked": "2026-10-17",
  "documentation_checked": "2026-09",
  "body_sha256": "01448c4f9ba0d99dbcaf3c68b1ed70e39986556e4bc9b641b2f0dfda5f50a71d",
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
    "zerossl": {
      "name": "ZeroSSL",
      "basis": "unknown",
      "sources": {
        "sddca28a3381b": "https://zerossl.com/"
      }
    },
    "acme": {
      "name": "acme.sh",
      "basis": "unknown",
      "sources": {
        "sa635c50fc1f9": "https://github.com/acmesh-official/acme.sh"
      }
    },
    "caddy": {
      "name": "Caddy automatic HTTPS",
      "basis": "v2.11.4",
      "sources": {
        "s9683cb8d689f": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/autohttps.go#L62-L63",
        "s409f9221aec2": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddytls/acmeissuer.go#L280-L296",
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
        "sf2fbc79f6542": "https://github.com/caddyserver/certmagic/blob/v0.25.3/certmagic.go#L473-L475"
      }
    },
    "traefik": {
      "name": "Traefik ACME documentation",
      "basis": "v3.5",
      "sources": {
        "s418a6b1ad09b": "https://doc.traefik.io/traefik/v3.5/reference/install-configuration/tls/certificate-resolvers/acme/"
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
    "cloudflare-origin-ca": {
      "name": "Cloudflare Origin CA documentation",
      "basis": "checked October 2026",
      "sources": {
        "s1e15de5c9f36": "https://developers.cloudflare.com/ssl/origin-configuration/origin-ca/"
      }
    }
  },
  "claims": {
    "public-trust": {"text": "ACME CAs such as Let's Encrypt and ZeroSSL issue free publicly trusted certificates; this guide advises preferring them for public DNS names, including private hosts using DNS-01.", "components": ["le", "zerossl"], "sources": ["le:s9ff2d787c618", "zerossl:sddca28a3381b"], "status": "REASONED"},
    "http-challenge": {"text": "HTTP-01 needs a public A/AAAA or CNAME pointing to the server and inbound internet access to port 80.", "components": ["le"], "sources": ["le:s9ff2d787c618"], "status": "REASONED"},
    "alpn-challenge": {"text": "TLS-ALPN-01 needs a public DNS record and inbound port 443; Caddy's ACME issuer enables the TLS-ALPN-01 solver when DNS-01 is not configured and TLS-ALPN-01 is not disabled, and can use an alternate local port if port 443 forwards to it; Traefik also uses TLS-ALPN-01.", "components": ["le", "caddy", "certmagic", "traefik"], "sources": ["le:s9ff2d787c618", "caddy:s409f9221aec2", "caddy:s5216789c9341", "certmagic:s61e3cba719df", "certmagic:s8782e006523b", "certmagic:s465c4ddcc92f", "certmagic:sc1e2ddefe5ed", "certmagic:sd423f53faa1a", "certmagic:sf2fbc79f6542", "traefik:s418a6b1ad09b"], "status": "REASONED"},
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
---
# Free publicly trusted certificates (ACME)

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-17; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| public-trust: ACME CAs such as Let's Encrypt and ZeroSSL issue free publicly trusted certificates; this guide advises preferring them for public DNS names, including private hosts using DNS-01. | Let's Encrypt documentation unknown; ZeroSSL unknown | REASONED |
| http-challenge: HTTP-01 needs a public A/AAAA or CNAME pointing to the server and inbound internet access to port 80. | Let's Encrypt documentation unknown | REASONED |
| alpn-challenge: TLS-ALPN-01 needs a public DNS record and inbound port 443; Caddy's ACME issuer enables the TLS-ALPN-01 solver when DNS-01 is not configured and TLS-ALPN-01 is not disabled, and can use an alternate local port if port 443 forwards to it; Traefik also uses TLS-ALPN-01. | Let's Encrypt documentation unknown; Caddy automatic HTTPS v2.11.4; certmagic ACME implementation v0.25.3; Traefik ACME documentation v3.5 | REASONED |
| dns-challenge: DNS-01 needs control of the challenge TXT record, no public address record or inbound port, and supports wildcards; automated issuance and renewal need an automated way to update TXT records, and this guide advises a provider DNS plugin and scoped API credentials, while Certbot also supports manual DNS-01 and an authentication hook for automatic renewal. | Let's Encrypt documentation unknown; Certbot documentation unknown; Certbot user guide and source v2.3.0 | REASONED |
| certbot-install: Install Certbot and nginx/Apache plugins from the distribution, or the classic snap with /usr/bin/certbot pointing to /snap/bin/certbot. | Certbot documentation unknown | REASONED |
| server-plugins: certbot --nginx or --apache issues and installs certificates for the supplied domain names when the server is supported. | Certbot documentation unknown | REASONED |
| standalone: certonly --standalone binds port 80; stop its current owner and arrange webroot, a server plugin or port-freeing hooks for unattended renewal. | Certbot documentation unknown | REASONED |
| webroot: certonly --webroot uses /var/www/html to serve challenge files while the existing web server keeps running. | Certbot documentation unknown | REASONED |
| dns-credentials: The Cloudflare DNS plugin uses a credentials file and a Zone:DNS:Edit token limited to required zones; this guide requires never using the Global API Key and protecting the file with mode 600 in a 700 directory. | Certbot documentation unknown; Certbot Cloudflare DNS plugin v2.3.0 | REASONED |
| certificate-paths: Configure servers against stable /etc/letsencrypt/live/example.com/fullchain.pem and privkey.pem paths for the chain and private key. | Certbot documentation unknown | REASONED |
| renewal-schedule: The Certbot v2.3.0 user guide says most installations have a scheduled task running certbot renew and says that, on Linux and BSD, you can check cron or systemd timers if unsure; this guide requires confirming the task and testing renewal plus reload with --dry-run --run-deploy-hooks, including package and snap installations. | Certbot documentation unknown; Certbot user guide and source v2.3.0 | REASONED |
| deploy-hook: This guide requires persisting a reload hook during successful initial issuance or successful renewal, or installing an executable in renewal-hooks/deploy; Certbot v2.3.0 saves the renewal-relevant options set on the command line to a lineage after successful renewal, and a renew --deploy-hook invocation with no renewal due does not save that hook. | Certbot documentation unknown; Certbot user guide and source v2.3.0 | REASONED |
| reconfigure: certbot reconfigure can add the reload hook later on Certbot 2.3.0 and later. | Certbot reconfigure minimum 2.3.0 | REASONED |
| expiry-monitoring: Monitor the served certificate's expiry and renewal failures instead of relying on CA reminder emails; include a dry run in the deployment checklist. This guide assesses that any renewal step involving a person will fail at those scheduled shorter certificate lifetimes and that unattended automation is the only viable path. | Let's Encrypt documentation unknown; Certbot documentation unknown | REASONED |
| default-lifetime: At the guide's September 2026 documentation check, Let's Encrypt's default certificate lifetime is 90 days. | Let's Encrypt documentation unknown | REASONED |
| short-lifetime: Optional 6-day short-lived certificates are available to every subscriber as of the guide's September 2026 check. | Let's Encrypt documentation unknown | REASONED |
| lifetime-schedule: The classic profile moves to 64 days on 2027-02-10 and 45 days on 2028-02-16; industry rules cap publicly trusted certificates at 47 days from 2029-03-15. | Let's Encrypt documentation unknown | REASONED |
| revocation: Let's Encrypt ended OCSP on 2025-08-06 and publishes revocation through CRLs only; do not add OCSP stapling directives for its certificates. | Let's Encrypt documentation unknown | REASONED |
| staging: Let's Encrypt limits per-domain issuance; test with certbot --staging or --test-cert before real issuance. | Let's Encrypt documentation unknown; Certbot documentation unknown | REASONED |
| caa: CAA restricts issuing CAs, using issue letsencrypt.org for Let's Encrypt; certificate-transparency monitoring detects mis-issuance afterwards and complements CAA. | Let's Encrypt documentation unknown | REASONED |
| zerossl-eab: ZeroSSL offers free ACME certificates; some clients need dashboard EAB credentials. | ZeroSSL unknown | REASONED |
| acme-default: acme.sh registers with ZeroSSL by default. | acme.sh unknown | REASONED |
| acme-install: acme.sh is a shell ACME client supporting many DNS providers; the guide recommends installation from a repository release instead of piping a download into a shell. | acme.sh unknown | REASONED |
| server-automation: This guide advises Caddy or Traefik for built-in issuance and renewal without an external client; it assesses them as the lowest-effort correct option for new deployments. | Let's Encrypt documentation unknown; Caddy automatic HTTPS v2.11.4; Traefik ACME documentation v3.5 | REASONED |
| origin-certificates: Cloudflare lists Origin CA certificates on its Free plan, refers to long-lived origin CA certificates and says the validity period is chosen at creation, says they only encrypt traffic between Cloudflare and the origin, and warns that visitors may see untrusted certificate errors when Cloudflare is paused or proxying is disabled; this guide requires using them only for origins that receive traffic only through Cloudflare-proxied records. | Let's Encrypt documentation unknown; Cloudflare Origin CA documentation checked October 2026 | REASONED |
| verify-inventory: certbot certificates lists issued certificates and their expiry dates. | Certbot documentation unknown | REASONED |
| verify-https: Use the deployment's public hostname rather than example.com; curl HTTPS should succeed without -k. | Let's Encrypt documentation unknown; curl command documentation curl-8_12_1 | REASONED |
| verify-certificate: The OpenSSL probe targets the hostname on port 443 with SNI, hostname verification and verification errors enabled, then displays issuer and dates. | Let's Encrypt documentation unknown; OpenSSL certificate commands 3.0 | REASONED |
| authentication: A certificate alone is insufficient protection; continue with server controls and authentication. | Let's Encrypt documentation unknown | REASONED |
| dns-automation: For automated DNS-01 issuance and renewal, this guide advises using a provider DNS plugin and least-privilege API credentials; Certbot also documents manual TXT entry and authentication hooks that automate the challenge. | Certbot documentation unknown; Certbot user guide and source v2.3.0 | REASONED |
| dns-manual: certbot certonly --manual --preferred-challenges dns permits hand-created TXT records; the Certbot v2.3.0 guide says certificates created with --manual do not support automatic renewal without a --manual-auth-hook that automates the challenge. | Certbot documentation unknown; Certbot user guide and source v2.3.0 | REASONED |
<!-- version-basis:end -->

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
- Caddy v2.11.4 passes its ACME issuer template to certmagic (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddytls/acmeissuer.go#L321-L328
- Caddy v2.11.4 pins certmagic v0.25.3 (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/go.mod#L12-L12
- certmagic v0.25.3 TLS-ALPN-01 solver selection (checked October 2026): https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeclient.go#L188-L226
- certmagic v0.25.3 TLS-ALPN challenge listener port (checked October 2026): https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeclient.go#L304-L313
- certmagic v0.25.3 alternate TLS-ALPN port forwarding (checked October 2026): https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeissuer.go#L116-L120
- certmagic v0.25.3 issuer defaults for the DNS-01 solver and TLS-ALPN setting (checked October 2026): https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeissuer.go#L222-L236
- certmagic v0.25.3 TLS-ALPN challenge port 443 (checked October 2026): https://github.com/caddyserver/certmagic/blob/v0.25.3/certmagic.go#L473-L475
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
- Certbot v2.3.0 Cloudflare DNS credentials (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot-dns-cloudflare/certbot_dns_cloudflare/__init__.py#L24-L39
- Certbot v2.3.0 Cloudflare DNS credential permissions (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot-dns-cloudflare/certbot_dns_cloudflare/__init__.py#L61-L78
- Cloudflare Origin CA (checked October 2026): https://developers.cloudflare.com/ssl/origin-configuration/origin-ca/
