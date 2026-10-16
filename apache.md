---
version_basis: {
  "schema": 1,
  "checked": "2026-10-05",
  "documentation_checked": "2026-09",
  "body_sha256": "4a5a82ed689907196d2cc574f58cbbf538d83a57da33f9f0018046b1f10da8ba",
  "components": {
    "apache": {
      "name": "Apache HTTP Server",
      "basis": "2.4",
      "sources": {
        "sde155f1667f3": "https://httpd.apache.org/docs/2.4/ssl/ssl_howto.html",
        "s99dcb49d86a4": "https://httpd.apache.org/docs/2.4/howto/auth.html",
        "sc07f97af99e3": "https://httpd.apache.org/docs/2.4/vhosts/name-based.html",
        "scf804f4940d7": "https://httpd.apache.org/docs/2.4/mod/mod_ssl.html#sslvhostsnipolicy",
        "s7c302c734a0d": "https://httpd.apache.org/docs/2.4/vhosts/details.html",
        "s1dbb2636d050": "https://httpd.apache.org/docs/2.4/mod/mod_headers.html"
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
    },
    "certbot": {
      "name": "Certbot Apache installation",
      "basis": "v2.3.0",
      "sources": {
        "sc74fcd0167d8": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L104-L106",
        "sa453a66e4130": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/client.py#L646",
        "sacf90ffa5a6d": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/client.py#L674-L677",
        "s74412ad87016": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/constants.py#L66-L68"
      }
    },
    "debian-packaging": {
      "name": "Debian apache2 packaging",
      "basis": "2.4.69-1",
      "sources": {
        "s1c05297f1ef0": "https://salsa.debian.org/apache-team/apache2/-/blob/fc6e58fa5248fc058591097c94ac8fde34283519/debian/apache2.install#L1-7",
        "s32bd234fb40a": "https://salsa.debian.org/apache-team/apache2/-/blob/fc6e58fa5248fc058591097c94ac8fde34283519/debian/config-dir/sites-available/default-ssl.conf#L1-4",
        "sc9b152b1a444": "https://salsa.debian.org/apache-team/apache2/-/blob/fc6e58fa5248fc058591097c94ac8fde34283519/debian/apache2.links#L7",
        "sd1c9de6b39aa": "https://salsa.debian.org/apache-team/apache2/-/blob/fc6e58fa5248fc058591097c94ac8fde34283519/debian/control#L92-102"
      }
    },
    "fedora-packaging": {
      "name": "Fedora f44 httpd packaging",
      "basis": "commit 6df70d39",
      "sources": {
        "s7d73f140a3fe": "https://src.fedoraproject.org/rpms/httpd/blob/6df70d392dace11a7c01ceffc5d8a929de0b7a35/f/httpd.spec#_204-212",
        "s4479577a2e6a": "https://src.fedoraproject.org/rpms/httpd/blob/6df70d392dace11a7c01ceffc5d8a929de0b7a35/f/httpd.spec#_819-824"
      }
    },
    "htpasswd": {
      "name": "httpd htpasswd",
      "basis": "2.4.69",
      "sources": {
        "s309ecdd34379": "https://github.com/apache/httpd/blob/2.4.69/support/htpasswd.c#L100-L128",
        "s7850e1e9dfa1": "https://github.com/apache/httpd/blob/2.4.69/support/passwd_common.h#L43-L45",
        "s1c1a101a70e7": "https://github.com/apache/httpd/blob/2.4.69/support/passwd_common.c#L290-L295"
      }
    },
    "owasp": {
      "name": "OWASP password storage cheat sheet",
      "basis": "commit 72865b1e",
      "sources": {
        "s4531e65b6502": "https://github.com/OWASP/CheatSheetSeries/blob/72865b1e3b5754246a101778dc00b37f9c233373/cheatsheets/Password_Storage_Cheat_Sheet.md#L13"
      }
    },
    "authelia": {
      "name": "Authelia proxy support",
      "basis": "v4.39.28",
      "sources": {
        "s1de7fe72d011": "https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/support.md#L112-L115"
      }
    },
    "openidc": {
      "name": "mod_auth_openidc",
      "basis": "v2.4.20.3",
      "sources": {
        "s01e183d16f03": "https://github.com/OpenIDC/mod_auth_openidc/blob/v2.4.20.3/README.md#L11-L20"
      }
    }
  },
  "claims": {
    "certbot": {"text": "The guide says certbot --apache installs certificates and redirects by default; --redirect is explicit and --hsts defaults off.", "components": ["apache", "certbot"], "sources": ["apache:sde155f1667f3", "certbot:sc74fcd0167d8", "certbot:sa453a66e4130", "certbot:sacf90ffa5a6d", "certbot:s74412ad87016"], "status": "REASONED"},
    "modules": {"text": "Enable ssl/headers and a 443 vhost on Debian/Ubuntu, or install mod_ssl/httpd-tools on RHEL/Fedora; fetched packaging supports a2enmod, a2ensite (a link to a2enmod), default-ssl, and Fedora package names.", "components": ["apache", "debian-packaging", "fedora-packaging"], "sources": ["apache:sde155f1667f3", "debian-packaging:s1c05297f1ef0", "debian-packaging:sc9b152b1a444", "debian-packaging:s32bd234fb40a", "fedora-packaging:s7d73f140a3fe"], "status": "REASONED"},
    "tls": {"text": "The 443 vhost enables TLS with a certificate chain and private key and TLSv1.2/TLSv1.3 only.", "components": ["apache"], "sources": ["apache:sde155f1667f3", "apache:scf804f4940d7"], "status": "REASONED"},
    "tls-version": {"text": "TLSv1.3 needs Apache 2.4.36+ with OpenSSL 1.1.1+; older builds use SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1.", "components": ["apache", "tls-min", "openssl"], "sources": ["apache:scf804f4940d7", "tls-min:scf804f4940d7", "openssl:scf804f4940d7"], "status": "REASONED"},
    "vhost-floor": {"text": "Independent per-vhost SSLProtocol needs Apache 2.4.42+, OpenSSL 1.1.1+ and client SNI; older builds also need the floor in global/base config.", "components": ["apache", "sni-min", "openssl"], "sources": ["apache:scf804f4940d7", "apache:s7c302c734a0d", "sni-min:scf804f4940d7", "openssl:scf804f4940d7"], "status": "REASONED"},
    "chain": {"text": "Apache 2.4.8+ permits the chain in SSLCertificateFile; SSLCertificateChainFile is deprecated.", "components": ["apache", "chain-min"], "sources": ["apache:scf804f4940d7", "chain-min:scf804f4940d7"], "status": "REASONED"},
    "hsts": {"text": "Header always sets HSTS after HTTPS works; includeSubDomains requires valid HTTPS everywhere.", "components": ["apache"], "sources": ["apache:sde155f1667f3", "apache:s1dbb2636d050"], "status": "REASONED"},
    "cipher-policy": {"text": "Generate explicit cipher policy with Mozilla rather than copying old lists.", "components": ["policy"], "sources": ["policy:s529b0eabe2ed"], "status": "REASONED"},
    "redirect": {"text": "The 80 vhost sends a permanent redirect to the canonical HTTPS host; retain only redirects and needed ACME HTTP-01 paths.", "components": ["apache"], "sources": ["apache:sc07f97af99e3", "apache:sde155f1667f3"], "status": "REASONED"},
    "password-file": {"text": "Create a bcrypt htpasswd file with cost 12 and -c only for its first user; httpd 2.4.69 defaults bcrypt cost to 5 and OWASP recommends at least 10 for legacy bcrypt. The RHEL/Fedora password-file path is a guide choice.", "components": ["apache", "debian-packaging", "fedora-packaging", "htpasswd", "owasp"], "sources": ["apache:s99dcb49d86a4", "debian-packaging:sd1c9de6b39aa", "fedora-packaging:s4479577a2e6a", "htpasswd:s309ecdd34379", "htpasswd:s7850e1e9dfa1", "htpasswd:s1c1a101a70e7", "owasp:s4531e65b6502"], "status": "REASONED"},
    "basic": {"text": "AuthType Basic, AuthName, AuthUserFile and Require valid-user protect the chosen site/path over TLS; enumerate every public path.", "components": ["apache"], "sources": ["apache:s99dcb49d86a4"], "status": "REASONED"},
    "mtls": {"text": "A separate machine-client 443 vhost requires a trusted certificate with SSLVerifyClient require and depth 2; SSLCACertificateFile is server/vhost scoped.", "components": ["apache"], "sources": ["apache:scf804f4940d7"], "status": "REASONED"},
    "mfa": {"text": "Basic is single-factor; Authelia v4.39.28 says Apache is unsupported for its proxy integration, and mod_auth_openidc v2.4.20.3 is an OIDC relying party. Provider MFA is guide advice; Cloudflare Access is unsourced here.", "components": ["apache", "authelia", "openidc"], "sources": ["apache:s99dcb49d86a4", "authelia:s1de7fe72d011", "openidc:s01e183d16f03"], "status": "REASONED"},
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

Metadata reviewed 2026-10-05; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| certbot: The guide says certbot --apache installs certificates and redirects by default; --redirect is explicit and --hsts defaults off. | Apache HTTP Server 2.4; Certbot Apache installation v2.3.0 | REASONED |
| modules: Enable ssl/headers and a 443 vhost on Debian/Ubuntu, or install mod_ssl/httpd-tools on RHEL/Fedora; fetched packaging supports a2enmod, a2ensite (a link to a2enmod), default-ssl, and Fedora package names. | Apache HTTP Server 2.4; Debian apache2 packaging 2.4.69-1; Fedora f44 httpd packaging commit 6df70d39 | REASONED |
| tls: The 443 vhost enables TLS with a certificate chain and private key and TLSv1.2/TLSv1.3 only. | Apache HTTP Server 2.4 | REASONED |
| tls-version: TLSv1.3 needs Apache 2.4.36+ with OpenSSL 1.1.1+; older builds use SSLProtocol all -SSLv3 -TLSv1 -TLSv1.1. | Apache HTTP Server 2.4; Apache TLSv1.3 minimum 2.4.36+; OpenSSL qualification 1.1.1+ | REASONED |
| vhost-floor: Independent per-vhost SSLProtocol needs Apache 2.4.42+, OpenSSL 1.1.1+ and client SNI; older builds also need the floor in global/base config. | Apache HTTP Server 2.4; Apache per-vhost protocol minimum 2.4.42+; OpenSSL qualification 1.1.1+ | REASONED |
| chain: Apache 2.4.8+ permits the chain in SSLCertificateFile; SSLCertificateChainFile is deprecated. | Apache HTTP Server 2.4; Apache chain-file minimum 2.4.8 | REASONED |
| hsts: Header always sets HSTS after HTTPS works; includeSubDomains requires valid HTTPS everywhere. | Apache HTTP Server 2.4 | REASONED |
| cipher-policy: Generate explicit cipher policy with Mozilla rather than copying old lists. | Mozilla TLS policy unknown | REASONED |
| redirect: The 80 vhost sends a permanent redirect to the canonical HTTPS host; retain only redirects and needed ACME HTTP-01 paths. | Apache HTTP Server 2.4 | REASONED |
| password-file: Create a bcrypt htpasswd file with cost 12 and -c only for its first user; httpd 2.4.69 defaults bcrypt cost to 5 and OWASP recommends at least 10 for legacy bcrypt. The RHEL/Fedora password-file path is a guide choice. | Apache HTTP Server 2.4; Debian apache2 packaging 2.4.69-1; Fedora f44 httpd packaging commit 6df70d39; httpd htpasswd 2.4.69; OWASP password storage cheat sheet commit 72865b1e | REASONED |
| basic: AuthType Basic, AuthName, AuthUserFile and Require valid-user protect the chosen site/path over TLS; enumerate every public path. | Apache HTTP Server 2.4 | REASONED |
| mtls: A separate machine-client 443 vhost requires a trusted certificate with SSLVerifyClient require and depth 2; SSLCACertificateFile is server/vhost scoped. | Apache HTTP Server 2.4 | REASONED |
| mfa: Basic is single-factor; Authelia v4.39.28 says Apache is unsupported for its proxy integration, and mod_auth_openidc v2.4.20.3 is an OIDC relying party. Provider MFA is guide advice; Cloudflare Access is unsourced here. | Apache HTTP Server 2.4; Authelia proxy support v4.39.28; mod_auth_openidc v2.4.20.3 | REASONED |
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

Debian apache2 2.4.69-1 installs `a2enmod`, links `a2ensite` to it, and ships the `default-ssl` configuration. Fedora f44 httpd packaging at commit 6df70d39 defines the `mod_ssl` and `httpd-tools` packages. These packaging citations do not establish every Debian/Ubuntu or RHEL release. (https://salsa.debian.org/apache-team/apache2/-/blob/fc6e58fa5248fc058591097c94ac8fde34283519/debian/apache2.install#L1-7; https://salsa.debian.org/apache-team/apache2/-/blob/fc6e58fa5248fc058591097c94ac8fde34283519/debian/apache2.links#L7; https://salsa.debian.org/apache-team/apache2/-/blob/fc6e58fa5248fc058591097c94ac8fde34283519/debian/config-dir/sites-available/default-ssl.conf#L1-4; https://src.fedoraproject.org/rpms/httpd/blob/6df70d392dace11a7c01ceffc5d8a929de0b7a35/f/httpd.spec#_204-212)

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
sudo htpasswd -B -C 12 -c /etc/apache2/.htpasswd admin     # Debian/Ubuntu path; /etc/httpd/conf/.htpasswd is the suggested RHEL/Fedora choice. -C 12 sets bcrypt cost; -c creates the file only for the first user
```

Debian apache2 2.4.69-1 provides `htpasswd` in `apache2-utils`; Fedora f44 httpd packaging at commit 6df70d39 puts it in `httpd-tools`. In httpd 2.4.69, `-B` selects bcrypt, `-C` sets its cost, and the default bcrypt cost is 5. The OWASP cheat sheet at commit 72865b1e recommends a work factor of at least 10 for legacy bcrypt; 12 is this guide's choice. The RHEL/Fedora password-file path above is also a guide choice. (https://salsa.debian.org/apache-team/apache2/-/blob/fc6e58fa5248fc058591097c94ac8fde34283519/debian/control#L92-102; https://src.fedoraproject.org/rpms/httpd/blob/6df70d392dace11a7c01ceffc5d8a929de0b7a35/f/httpd.spec#_819-824; https://github.com/apache/httpd/blob/2.4.69/support/htpasswd.c#L100-L128; https://github.com/apache/httpd/blob/2.4.69/support/passwd_common.h#L43-L45; https://github.com/apache/httpd/blob/2.4.69/support/passwd_common.c#L290-L295; https://github.com/OWASP/CheatSheetSeries/blob/72865b1e3b5754246a101778dc00b37f9c233373/cheatsheets/Password_Storage_Cheat_Sheet.md#L13)

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

Basic authentication is single-factor. Authelia v4.39.28 says Apache is unsupported for its proxy integration (https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/support.md#L112-L115). For human-facing sites, use [mod_auth_openidc](https://github.com/OpenIDC/mod_auth_openidc) v2.4.20.3 to make Apache an OIDC relying party (https://github.com/OpenIDC/mod_auth_openidc/blob/v2.4.20.3/README.md#L11-L20), and configure MFA at the identity provider as this guide advises. Cloudflare Access is another suggested option, but it is unsourced here; see [mfa.md](mfa.md).

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
- Certbot v2.3.0 Apache installation (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L104-L106
- Certbot v2.3.0 redirect default and enhancement application (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/client.py#L646 ; https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/client.py#L674-L677
- Certbot v2.3.0 redirect and opt-in HSTS defaults (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/constants.py#L66-L68
- Apache 2.4 `Header always set` response-header handling (checked October 2026): https://httpd.apache.org/docs/2.4/mod/mod_headers.html
- Debian apache2 2.4.69-1 helper, `a2ensite` link and default SSL configuration: https://salsa.debian.org/apache-team/apache2/-/blob/fc6e58fa5248fc058591097c94ac8fde34283519/debian/apache2.install#L1-7 ; https://salsa.debian.org/apache-team/apache2/-/blob/fc6e58fa5248fc058591097c94ac8fde34283519/debian/apache2.links#L7 ; https://salsa.debian.org/apache-team/apache2/-/blob/fc6e58fa5248fc058591097c94ac8fde34283519/debian/config-dir/sites-available/default-ssl.conf#L1-4
- Debian apache2 2.4.69-1 `apache2-utils` package: https://salsa.debian.org/apache-team/apache2/-/blob/fc6e58fa5248fc058591097c94ac8fde34283519/debian/control#L92-102
- Fedora f44 httpd packaging at commit 6df70d39 package definitions and `htpasswd` file list: https://src.fedoraproject.org/rpms/httpd/blob/6df70d392dace11a7c01ceffc5d8a929de0b7a35/f/httpd.spec#_204-212 ; https://src.fedoraproject.org/rpms/httpd/blob/6df70d392dace11a7c01ceffc5d8a929de0b7a35/f/httpd.spec#_819-824
- httpd 2.4.69 `htpasswd` options and bcrypt default: https://github.com/apache/httpd/blob/2.4.69/support/htpasswd.c#L100-L128 ; https://github.com/apache/httpd/blob/2.4.69/support/passwd_common.h#L43-L45 ; https://github.com/apache/httpd/blob/2.4.69/support/passwd_common.c#L290-L295
- OWASP cheat sheet at commit 72865b1e legacy bcrypt guidance: https://github.com/OWASP/CheatSheetSeries/blob/72865b1e3b5754246a101778dc00b37f9c233373/cheatsheets/Password_Storage_Cheat_Sheet.md#L13
- Authelia v4.39.28 Apache proxy support: https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/support.md#L112-L115
- mod_auth_openidc v2.4.20.3 relying-party description: https://github.com/OpenIDC/mod_auth_openidc/blob/v2.4.20.3/README.md#L11-L20
