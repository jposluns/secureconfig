---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "4e0320534d6c0e20a0f7044b6dfe3cfdcdd3a35f15a4880858102fce5948fd5a",
  "components": {
    "apache": {
      "name": "Apache HTTP Server",
      "basis": "2.4",
      "sources": {
        "sde155f1667f3": "https://httpd.apache.org/docs/2.4/ssl/ssl_howto.html",
        "s99dcb49d86a4": "https://httpd.apache.org/docs/2.4/howto/auth.html",
        "sc07f97af99e3": "https://httpd.apache.org/docs/2.4/vhosts/name-based.html",
        "scf804f4940d7": "https://httpd.apache.org/docs/2.4/mod/mod_ssl.html#sslvhostsnipolicy",
        "s7c302c734a0d": "https://httpd.apache.org/docs/2.4/vhosts/details.html"
      }
    },
    "policy": {
      "name": "Mozilla TLS policy",
      "basis": "unknown",
      "sources": {
        "s529b0eabe2ed": "https://ssl-config.mozilla.org/"
      }
    },
    "tls-min": {
      "name": "Apache TLSv1.3 minimum",
      "basis": "2.4.36+",
      "sources": {
        "scf804f4940d7": "https://httpd.apache.org/docs/2.4/mod/mod_ssl.html#sslvhostsnipolicy"
      }
    },
    "sni-min": {
      "name": "Apache per-vhost protocol minimum",
      "basis": "2.4.42+",
      "sources": {
        "scf804f4940d7": "https://httpd.apache.org/docs/2.4/mod/mod_ssl.html#sslvhostsnipolicy"
      }
    },
    "openssl": {
      "name": "OpenSSL qualification",
      "basis": "1.1.1+",
      "sources": {
        "scf804f4940d7": "https://httpd.apache.org/docs/2.4/mod/mod_ssl.html#sslvhostsnipolicy"
      }
    },
    "chain-min": {
      "name": "Apache chain-file minimum",
      "basis": "2.4.8",
      "sources": {
        "scf804f4940d7": "https://httpd.apache.org/docs/2.4/mod/mod_ssl.html#sslvhostsnipolicy"
      }
    }
  },
  "claims": {
    "certbot": {"text": "The guide says certbot --apache installs certificates and redirects by default; --redirect is explicit and --hsts defaults off. Certbot is not in Sources.", "components": ["apache"], "sources": ["apache:sde155f1667f3"], "status": "REASONED"},
    "modules": {"text": "Enable ssl/headers and a 443 vhost on Debian/Ubuntu, or install mod_ssl/httpd-tools on RHEL/Fedora; package-command sources are absent.", "components": ["apache"], "sources": ["apache:sde155f1667f3"], "status": "REASONED"},
    "tls": {"text": "The 443 vhost enables TLS with a certificate chain and private key and TLSv1.2/TLSv1.3 only.", "components": ["apache"], "sources": ["apache:sde155f1667f3", "apache:scf804f4940d7"], "status": "REASONED"},
    "tls-version": {"text": "TLSv1.3 needs Apache 2.4.36+ with OpenSSL 1.1.1+; older builds use SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1.", "components": ["apache", "tls-min", "openssl"], "sources": ["apache:scf804f4940d7", "tls-min:scf804f4940d7", "openssl:scf804f4940d7"], "status": "REASONED"},
    "vhost-floor": {"text": "Independent per-vhost SSLProtocol needs Apache 2.4.42+, OpenSSL 1.1.1+ and client SNI; older builds also need the floor in global/base config.", "components": ["apache", "sni-min", "openssl"], "sources": ["apache:scf804f4940d7", "apache:s7c302c734a0d", "sni-min:scf804f4940d7", "openssl:scf804f4940d7"], "status": "REASONED"},
    "chain": {"text": "Apache 2.4.8+ permits the chain in SSLCertificateFile; SSLCertificateChainFile is deprecated.", "components": ["apache", "chain-min"], "sources": ["apache:scf804f4940d7", "chain-min:scf804f4940d7"], "status": "REASONED"},
    "hsts": {"text": "Header always sets HSTS after HTTPS works; includeSubDomains requires valid HTTPS everywhere. Sources omit mod_headers.", "components": ["apache"], "sources": ["apache:sde155f1667f3"], "status": "REASONED"},
    "cipher-policy": {"text": "Generate explicit cipher policy with Mozilla rather than copying old lists.", "components": ["policy"], "sources": ["policy:s529b0eabe2ed"], "status": "REASONED"},
    "redirect": {"text": "The 80 vhost sends a permanent redirect to the canonical HTTPS host; retain only redirects and needed ACME HTTP-01 paths.", "components": ["apache"], "sources": ["apache:sc07f97af99e3", "apache:sde155f1667f3"], "status": "REASONED"},
    "password-file": {"text": "Create a bcrypt htpasswd file with cost 12 and -c only for its first user; paths differ by distribution. Cost defaults and OWASP guidance are not directly cited.", "components": ["apache"], "sources": ["apache:s99dcb49d86a4"], "status": "REASONED"},
    "basic": {"text": "AuthType Basic, AuthName, AuthUserFile and Require valid-user protect the chosen site/path over TLS; enumerate every public path.", "components": ["apache"], "sources": ["apache:s99dcb49d86a4"], "status": "REASONED"},
    "mtls": {"text": "A separate machine-client 443 vhost requires a trusted certificate with SSLVerifyClient require and depth 2; SSLCACertificateFile is server/vhost scoped.", "components": ["apache"], "sources": ["apache:scf804f4940d7"], "status": "REASONED"},
    "mfa": {"text": "Basic is single-factor; the guide says Authelia does not support Apache and proposes mod_auth_openidc with IdP MFA or Cloudflare Access. Integration sources are absent.", "components": ["apache"], "sources": ["apache:s99dcb49d86a4"], "status": "REASONED"},
    "key-permissions": {"text": "Keep private keys root-owned and mode 0600.", "components": ["apache"], "sources": ["apache:sde155f1667f3"], "status": "REASONED"},
    "verify-config": {"text": "Run apachectl configtest before service reload; no outcome is recorded.", "components": ["apache"], "sources": ["apache:sde155f1667f3"], "status": "REASONED", "verify": [1]},
    "verify-redirect": {"text": "HTTP should return 301 with an HTTPS Location.", "components": ["apache"], "sources": ["apache:sc07f97af99e3"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "Read printed status: curl can exit 0 for 200 or 401; expect 200 before auth and 401 after it.", "components": ["apache"], "sources": ["apache:s99dcb49d86a4"], "status": "REASONED", "verify": [1]},
    "verify-listeners": {"text": "Inspect the entire listener table, without filtering away unexpected ports.", "components": ["apache"], "sources": ["apache:sc07f97af99e3"], "status": "REASONED", "verify": [1]},
    "verify-unmatched": {"text": "Use an unconfigured certificate-covered URL name for both SNI and Host; 401 passes, 200 exposes a protected resource through another vhost. Host-only probes can misleadingly give 401 or 421.", "components": ["apache"], "sources": ["apache:sc07f97af99e3", "apache:scf804f4940d7", "apache:s7c302c734a0d"], "status": "REASONED", "verify": [1]},
    "verify-vhost-review": {"text": "If no spare certificate-covered name exists, use apachectl -S and review that the first matching vhost cannot serve the protected DocumentRoot.", "components": ["apache"], "sources": ["apache:sc07f97af99e3", "apache:s7c302c734a0d"], "status": "REASONED", "verify": [2]}
  }
}
---
# Apache HTTP Server: TLS and authentication

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| certbot: The guide says certbot --apache installs certificates and redirects by default; --redirect is explicit and --hsts defaults off. Certbot is not in Sources. | Apache HTTP Server 2.4 | REASONED |
| modules: Enable ssl/headers and a 443 vhost on Debian/Ubuntu, or install mod_ssl/httpd-tools on RHEL/Fedora; package-command sources are absent. | Apache HTTP Server 2.4 | REASONED |
| tls: The 443 vhost enables TLS with a certificate chain and private key and TLSv1.2/TLSv1.3 only. | Apache HTTP Server 2.4 | REASONED |
| tls-version: TLSv1.3 needs Apache 2.4.36+ with OpenSSL 1.1.1+; older builds use SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1. | Apache HTTP Server 2.4; Apache TLSv1.3 minimum 2.4.36+; OpenSSL qualification 1.1.1+ | REASONED |
| vhost-floor: Independent per-vhost SSLProtocol needs Apache 2.4.42+, OpenSSL 1.1.1+ and client SNI; older builds also need the floor in global/base config. | Apache HTTP Server 2.4; Apache per-vhost protocol minimum 2.4.42+; OpenSSL qualification 1.1.1+ | REASONED |
| chain: Apache 2.4.8+ permits the chain in SSLCertificateFile; SSLCertificateChainFile is deprecated. | Apache HTTP Server 2.4; Apache chain-file minimum 2.4.8 | REASONED |
| hsts: Header always sets HSTS after HTTPS works; includeSubDomains requires valid HTTPS everywhere. Sources omit mod_headers. | Apache HTTP Server 2.4 | REASONED |
| cipher-policy: Generate explicit cipher policy with Mozilla rather than copying old lists. | Mozilla TLS policy unknown | REASONED |
| redirect: The 80 vhost sends a permanent redirect to the canonical HTTPS host; retain only redirects and needed ACME HTTP-01 paths. | Apache HTTP Server 2.4 | REASONED |
| password-file: Create a bcrypt htpasswd file with cost 12 and -c only for its first user; paths differ by distribution. Cost defaults and OWASP guidance are not directly cited. | Apache HTTP Server 2.4 | REASONED |
| basic: AuthType Basic, AuthName, AuthUserFile and Require valid-user protect the chosen site/path over TLS; enumerate every public path. | Apache HTTP Server 2.4 | REASONED |
| mtls: A separate machine-client 443 vhost requires a trusted certificate with SSLVerifyClient require and depth 2; SSLCACertificateFile is server/vhost scoped. | Apache HTTP Server 2.4 | REASONED |
| mfa: Basic is single-factor; the guide says Authelia does not support Apache and proposes mod_auth_openidc with IdP MFA or Cloudflare Access. Integration sources are absent. | Apache HTTP Server 2.4 | REASONED |
| key-permissions: Keep private keys root-owned and mode 0600. | Apache HTTP Server 2.4 | REASONED |
| verify-config: Run apachectl configtest before service reload; no outcome is recorded. | Apache HTTP Server 2.4 | REASONED |
| verify-redirect: HTTP should return 301 with an HTTPS Location. | Apache HTTP Server 2.4 | REASONED |
| verify-auth: Read printed status: curl can exit 0 for 200 or 401; expect 200 before auth and 401 after it. | Apache HTTP Server 2.4 | REASONED |
| verify-listeners: Inspect the entire listener table, without filtering away unexpected ports. | Apache HTTP Server 2.4 | REASONED |
| verify-unmatched: Use an unconfigured certificate-covered URL name for both SNI and Host; 401 passes, 200 exposes a protected resource through another vhost. Host-only probes can misleadingly give 401 or 421. | Apache HTTP Server 2.4 | REASONED |
| verify-vhost-review: If no spare certificate-covered name exists, use apachectl -S and review that the first matching vhost cannot serve the protected DocumentRoot. | Apache HTTP Server 2.4 | REASONED |
<!-- version-basis:end -->

Applies to Apache 2.4. Get a certificate first: [free-certificates.md](free-certificates.md) for a public host (note that `certbot --apache` obtains and installs the certificate and, at the time of writing, enables the HTTP-to-HTTPS redirect by default (`--redirect` requests it explicitly), but review its generated TLS config against steps 1 to 3 and add HSTS yourself, since certbot's `--hsts` is off by default), or [self-signed.md](self-signed.md) for internal use.

## 1. Enable the modules

```bash
# Debian/Ubuntu
sudo a2enmod ssl headers
sudo a2ensite default-ssl        # or your own :443 vhost file

# RHEL/Fedora
sudo dnf install mod_ssl httpd-tools
```

## 2. Configure the HTTPS virtual host

```apache
<VirtualHost *:443>
    ServerName example.com
    DocumentRoot /var/www/html

    SSLEngine on
    SSLCertificateFile      /etc/letsencrypt/live/example.com/fullchain.pem
    SSLCertificateKeyFile   /etc/letsencrypt/live/example.com/privkey.pem

    # TLS 1.2 minimum. The TLSv1.3 keyword needs Apache 2.4.36+ with OpenSSL 1.1.1+;
    # on older builds use: SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1
    # A per-vhost SSLProtocol takes effect independently only on Apache 2.4.42+ (with OpenSSL
    # 1.1.1+ and client SNI); on older builds the base or first-listed :443 vhost sets the floor,
    # so set the same SSLProtocol in the global/base config as well.
    SSLProtocol -all +TLSv1.2 +TLSv1.3

    # Send HSTS only once HTTPS is confirmed working. Add `includeSubDomains` ONLY after every
    # subdomain also serves valid HTTPS: it forces them all onto HTTPS and blocks any HTTP-only one.
    Header always set Strict-Transport-Security "max-age=31536000"
</VirtualHost>
```

On Apache 2.4.8 and later, `SSLCertificateFile` may contain the certificate plus its chain (certbot's `fullchain.pem`), and `SSLCertificateChainFile` is deprecated. For cipher suites beyond the protocol floor, generate a current list with the [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/) rather than copying one from an old tutorial.

## 3. Redirect HTTP to HTTPS

```apache
<VirtualHost *:80>
    ServerName example.com
    Redirect permanent / https://example.com/
</VirtualHost>
```

Keep port 80 serving only this redirect (and ACME HTTP-01 challenges if certbot uses the webroot method).

## 4. Require authentication

Application-level login is preferable ([authentication.md](authentication.md)). To gate a whole site or path at the server, use basic authentication over TLS with bcrypt-hashed entries:

```bash
sudo htpasswd -B -C 12 -c /etc/apache2/.htpasswd admin     # Debian/Ubuntu path; on RHEL/Fedora use /etc/httpd/conf/.htpasswd. -C 12 sets bcrypt cost (bare -B is 5, below the OWASP minimum of 10); -c only for the first user
```

```apache
<Location "/">
    AuthType Basic
    AuthName "Restricted"
    # Debian/Ubuntu path; on RHEL/Fedora use /etc/httpd/conf/.htpasswd (match the htpasswd -c path above)
    AuthUserFile /etc/apache2/.htpasswd
    Require valid-user
</Location>
```

For machine-to-machine links, mutual TLS is stronger than passwords. Put it in a SEPARATE `:443` vhost dedicated to machine clients, not the human-facing one: vhost-level `SSLVerifyClient require` makes every client present a trusted certificate, so a browser user with no client certificate is rejected during the TLS handshake before basic auth can apply. `SSLCACertificateFile` belongs at server or vhost level, not inside `<Location>`:

```apache
SSLCACertificateFile /etc/ssl/certs/internal-ca.crt
SSLVerifyClient require
SSLVerifyDepth 2
```

Basic authentication is single-factor, and Authelia documents Apache as unsupported for its portal. For human-facing sites, add MFA by making Apache an OIDC client with [mod_auth_openidc](https://github.com/OpenIDC/mod_auth_openidc), with MFA enforced at the identity provider, or by fronting the site with Cloudflare Access; options in [mfa.md](mfa.md).

## 5. Verify (REASONED: all Verify scenarios follow the cited Apache documentation; this guide records no exposed/fixed deployment run. This metadata-only review has no authorized Apache deployment fixture.)

These are read-and-judge checks. `curl` exits 0 for a 401 as readily as for a 200, so the
status code is printed and you compare it; nothing here fails on its own.

```bash
sudo apachectl configtest && sudo systemctl reload apache2   # httpd on RHEL
curl -q -sSI --noproxy '*' http://example.com/            # expect 301 with a https:// Location
curl -q -sS -o /dev/null --noproxy '*' -w '%{http_code}\n' https://example.com/
                                        # 200 before section 4, 401 after it. Once
                                        # authentication is on, a 200 here is the finding

# Read every listener. Do not filter to the ports you expect: a filter cannot show you a port
# you did not think of, which is the whole question, and `grep ':(80|443)'` also matches an
# address such as [2001:db8:80::1]:9000.
ss -tlnp

# A request whose name matches no ServerName or ServerAlias does not fail. Apache falls through
# to "the first listed virtual host that matches" the address and port, so a vhost listed
# before yours over the same DocumentRoot answers without your authentication.
#
# Over TLS the name that selects the vhost is the SNI one, not the Host header: Apache says
# that when the handshake carries it, "that hostname is used below just like the Host: header
# would be used on a non-SSL connection". So setting only the header tests nothing. It leaves
# SNI saying example.com, which selects YOUR vhost and answers 401, or makes mod_ssl reject the
# mismatched pair with 421; both look like a pass and neither is the request an attacker sends.
# The URL hostname supplies SNI and the Host header; --connect-to changes only the connection destination (your address):
curl -q -sS -o /dev/null --noproxy '*' -w '%{http_code}\n' \
  --connect-to REPLACE_WITH_AN_UNCONFIGURED_NAME:443:example.com:443 \
  https://REPLACE_WITH_AN_UNCONFIGURED_NAME/REPLACE_WITH_A_PROTECTED_PATH
                                        # 401 is the pass. 200 means another vhost served the
                                        # protected resource with no authentication at all
```

That name has to be one your certificate already covers, typically a spare label under a
wildcard SAN, because the guide will not tell you to disable certificate verification to run a
test. If the certificate covers no name you can spare, this check is a configuration review
instead: list the vhosts for that address and port, and confirm the first one Apache would
choose does not serve the protected `DocumentRoot`.

```bash
sudo apachectl -S                       # the vhost list, in Apache's own matching order
```

## Common mistakes

- Serving the application on port 80 next to the HTTPS vhost instead of only redirecting.
- Enabling `mod_ssl` without `Header`/HSTS, leaving downgrade open on repeat visits.
- World-readable private keys; keep them `0600` and root-owned.
- Protecting `/admin` but leaving `/api` open; `Require` rules apply per path, so enumerate what is public.

## Sources (checked September 2026)

- Apache SSL/TLS how-to: https://httpd.apache.org/docs/2.4/ssl/ssl_howto.html
- Apache authentication how-to: https://httpd.apache.org/docs/2.4/howto/auth.html
- Apache name-based virtual hosts, for which vhost answers an unmatched Host header: https://httpd.apache.org/docs/2.4/vhosts/name-based.html
- Apache mod_ssl `SSLVHostSNIPolicy`, for the 421 a mismatched SNI and Host pairing can produce (TLSv1.3: Apache 2.4.36+ with OpenSSL 1.1.1+; per-vhost SSLProtocol: Apache 2.4.42+ with OpenSSL 1.1.1+ and client SNI; chain in SSLCertificateFile: Apache 2.4.8+): https://httpd.apache.org/docs/2.4/mod/mod_ssl.html#sslvhostsnipolicy
- Apache virtual host matching in detail, for SNI selecting the vhost on a TLS connection: https://httpd.apache.org/docs/2.4/vhosts/details.html
- Mozilla SSL Configuration Generator: https://ssl-config.mozilla.org/
