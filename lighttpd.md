---
version_basis: {
  "schema": 1,
  "checked": "2026-10-18",
  "documentation_checked": "2026-09",
  "body_sha256": "8ac6945eb9dabb0c177108c32378b1379c627fa5611c8a20c32ce366bf650aff",
  "components": {
    "tls": {
      "name": "lighttpd TLS minimum",
      "basis": "1.4.56",
      "sources": {
        "sbff3cb2e01a8": "https://redmine.lighttpd.net/projects/lighttpd/wiki/Docs_SSL"
      }
    },
    "key": {
      "name": "lighttpd separate-key minimum",
      "basis": "1.4.53",
      "sources": {
        "sbff3cb2e01a8": "https://redmine.lighttpd.net/projects/lighttpd/wiki/Docs_SSL"
      }
    },
    "redirect": {
      "name": "lighttpd redirect default transition",
      "basis": "1.4.75",
      "sources": {
        "s6de629323c64": "https://redmine.lighttpd.net/projects/lighttpd/wiki/HowToRedirectHttpToHttps"
      }
    },
    "docs": {
      "name": "lighttpd documentation",
      "basis": "unknown",
      "sources": {
        "s1dbd1ce27da5": "https://redmine.lighttpd.net/projects/lighttpd/wiki/Mod_auth",
        "s6d5666b862a0": "https://redmine.lighttpd.net/projects/lighttpd/wiki/Docs_ConfigurationOptions",
        "s6de629323c64": "https://redmine.lighttpd.net/projects/lighttpd/wiki/HowToRedirectHttpToHttps"
      }
    },
    "modules-source": {
      "name": "lighttpd module loader source",
      "basis": "1.4.75",
      "sources": {
        "s8680e561bed2": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/configfile.c#L395-L544",
        "s8e9688979427": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/configfile.c#L270-L290",
        "s9bd716d27e8d": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/configfile.c#L382-L393",
        "s21288573041a": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/configfile.c#L662-L945",
        "s67bb3733d81c": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/configfile.c#L1684-L1711"
      }
    },
    "authn-source": {
      "name": "lighttpd file authentication source",
      "basis": "1.4.75",
      "sources": {
        "s2c11c0fbc0ca": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/mod_authn_file.c#L340-L397",
        "se971effb489f": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/mod_authn_file.c#L613-L740"
      }
    },
    "htpasswd-tool": {
      "name": "Apache htpasswd manual",
      "basis": "2.4",
      "sources": {
        "scde9004bb967": "https://httpd.apache.org/docs/2.4/programs/htpasswd.html"
      }
    },
    "debian-package": {
      "name": "Debian apache2-utils package",
      "basis": "trixie",
      "sources": {
        "s436bdf5f1fb9": "https://packages.debian.org/trixie/apache2-utils"
      }
    },
    "authelia": {
      "name": "Authelia proxy support",
      "basis": "v4.39.28",
      "sources": {
        "s77083bc8faa2": "https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/support.md#L24-L36"
      }
    },
    "cloudflare-access": {
      "name": "Cloudflare Access documentation",
      "basis": "commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104",
      "sources": {
        "sfddb92e438ca": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L14-L16",
        "s7cafe1b17afd": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L40-L54",
        "sdcac732541da": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/policies/mfa-requirements.mdx#L35-L81"
      }
    },
    "fedora-package": {
      "name": "Fedora httpd-tools package",
      "basis": "unknown",
      "sources": {
        "s919088d03a5e": "https://packages.fedoraproject.org/pkgs/httpd/httpd-tools/"
      }
    },
    "lighttpd-verify-source": {
      "name": "lighttpd verify source",
      "basis": "1.4.75",
      "sources": {
        "s0bbb4c861d5e": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/doc/lighttpd.8#L22-L23",
        "sca076bcd18dc": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/doc/lighttpd.8#L33-L37",
        "s9e69235fbbc7": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/server.c#L1439-L1451",
        "s87104d328493": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/server.c#L1466-L1467",
        "sba72bab46867": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/server.c#L1510-L1523",
        "s2faa9b3149ac": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/server.c#L1942-L1953",
        "s87b4b266bb0e": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/server.c#L2320-L2384",
        "sa989ef425f1d": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/server.c#L229-L235",
        "sf9d56b052c61": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/doc/systemd/lighttpd.service#L5-L11",
        "s6a29b290d83a": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/request.c#L423-L430",
        "s2fc4cf82abd9": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/request.c#L1235-L1247",
        "s3f692a48bd01": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/configfile-glue.c#L504-L508",
        "sbb09703388c3": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/configfile.c#L213-L223",
        "s8bb6bd7774f9": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/mod_openssl.c#L1025-L1034",
        "s95b975ea9cd2": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/mod_openssl.c#L1295-L1330"
      }
    },
    "systemd-reload": {
      "name": "systemd reload manual",
      "basis": "v262",
      "sources": {
        "sb3f5069cd250": "https://github.com/systemd/systemd/blob/v262/man/systemctl.xml#L462-L474",
        "s441757b7048f": "https://github.com/systemd/systemd/blob/v262/man/systemd.service.xml#L498-L519"
      }
    },
    "apache-vhosts": {
      "name": "Apache virtual-host source",
      "basis": "2.4.69",
      "sources": {
        "s558db45d4d61": "https://github.com/apache/httpd/blob/2.4.69/docs/manual/vhosts/details.xml#L217-L231"
      }
    }
  },
  "claims": {
    "tls-defaults": {"text": "lighttpd 1.4.56 and later disables SSLv2, SSLv3, TLS 1.0 and TLS 1.1 by default.", "components": ["tls"], "sources": ["tls:sbff3cb2e01a8"], "status": "REASONED"},
    "tls-listeners": {"text": "Load mod_openssl and enable TLS on both :443 and [::]:443 with ssl.pemfile and ssl.privkey; omitting the IPv6 socket leaves IPv6 clients on plain HTTP.", "components": ["tls"], "sources": ["tls:sbff3cb2e01a8"], "status": "REASONED"},
    "certificate-chain": {"text": "ssl.pemfile uses fullchain.pem rather than a certificate without its chain.", "components": ["tls"], "sources": ["tls:sbff3cb2e01a8"], "status": "REASONED"},
    "separate-key": {"text": "ssl.privkey exists from 1.4.53; older versions need certificate and key concatenated into ssl.pemfile.", "components": ["key"], "sources": ["key:sbff3cb2e01a8"], "status": "REASONED"},
    "protocol-floor": {"text": "ssl.openssl.ssl-conf-cmd sets MinProtocol to TLSv1.2 explicitly; recent versions already default to TLS 1.2.", "components": ["tls"], "sources": ["tls:sbff3cb2e01a8"], "status": "REASONED"},
    "module-defaults": {"text": "In lighttpd 1.4.75, mod_h2 is inserted unless server.feature-flags disables server.h2proto (enabled by default); when server.compat-module-load is enabled (the default), mod_indexfile and mod_dirlisting are conditionally added when enabled, mod_staticfile is added when absent, and compatibility handling can also add other modules, including authentication and TLS modules under their respective conditions. Load mod_redirect explicitly.", "components": ["docs", "modules-source"], "sources": ["docs:s6d5666b862a0", "modules-source:s8680e561bed2", "modules-source:s8e9688979427", "modules-source:s9bd716d27e8d", "modules-source:s21288573041a", "modules-source:s67bb3733d81c"], "status": "REASONED"},
    "http-redirect": {"text": "For the http scheme, redirect to HTTPS preserving authority, path and query; port 80 must redirect rather than serve content.", "components": ["docs"], "sources": ["docs:s6de629323c64"], "status": "REASONED"},
    "redirect-code": {"text": "Set url.redirect-code to 308 explicitly on versions before 1.4.75.", "components": ["redirect"], "sources": ["redirect:s6de629323c64"], "status": "REASONED"},
    "basic-auth": {"text": "Load mod_auth and mod_authn_file, select the htpasswd file backend and require valid-user Basic authentication on / over TLS; application login is preferable.", "components": ["docs"], "sources": ["docs:s1dbd1ce27da5"], "status": "REASONED"},
    "password-file": {"text": "Create the user file with Apache htpasswd (Debian apache2-utils; Fedora httpd-tools is this guide's package assessment); lighttpd 1.4.75 reads username:stored-hash entries and checks {SHA} SHA-1 and $apr1$ internally, with other hashes of at least 13 characters checked through crypt() when built with crypt support; under USE_LIB_CRYPTO_MD4, the $1+ntlm$ path derives an NTLM hash and calls crypt() with that derived value and a $1$ salt. Check the build and platform's accepted hashes before choosing a flag; this check is this guide's compatibility advice.", "components": ["docs", "authn-source", "htpasswd-tool", "debian-package", "fedora-package"], "sources": ["docs:s1dbd1ce27da5", "authn-source:s2c11c0fbc0ca", "authn-source:se971effb489f", "htpasswd-tool:scde9004bb967", "debian-package:s436bdf5f1fb9", "fedora-package:s919088d03a5e"], "status": "REASONED"},
    "mfa": {"text": "Basic authentication is single-factor; add MFA by fronting this service with Cloudflare Access or an MFA-capable proxy (this guide's requirement). Authelia v4.39.28's complete supported-proxy list has no lighttpd entry (this guide's inference from the table); Cloudflare Access documents self-hosted application and MFA policy controls; applying them to lighttpd is this guide's assessment.", "components": ["docs", "authelia", "cloudflare-access"], "sources": ["docs:s1dbd1ce27da5", "authelia:s77083bc8faa2", "cloudflare-access:sfddb92e438ca", "cloudflare-access:s7cafe1b17afd", "cloudflare-access:sdcac732541da"], "status": "REASONED"},
    "verify-config": {"text": "lighttpd 1.4.75 -tt -f /etc/lighttpd/lighttpd.conf tests the named file for syntax errors and initializes modules; configuration failures prevent the && reload (this guide's inference from the nonzero process result and shell chaining). The cited upstream unit starts from that file and defines a USR1 reload through ExecReload; systemctl reload triggers the service action, whose signal does not establish completion. Confirm the installed unit uses that file and defines reload (this guide's advice).", "components": ["docs", "lighttpd-verify-source", "systemd-reload"], "sources": ["docs:s6d5666b862a0", "lighttpd-verify-source:s0bbb4c861d5e", "lighttpd-verify-source:sca076bcd18dc", "lighttpd-verify-source:s9e69235fbbc7", "lighttpd-verify-source:s87104d328493", "lighttpd-verify-source:sba72bab46867", "lighttpd-verify-source:s2faa9b3149ac", "lighttpd-verify-source:s87b4b266bb0e", "lighttpd-verify-source:sa989ef425f1d", "lighttpd-verify-source:sf9d56b052c61", "systemd-reload:sb3f5069cd250", "systemd-reload:s441757b7048f"], "status": "REASONED", "verify": [1]},
    "verify-redirect": {"text": "The HTTP header request should show a redirect to HTTPS; these are read-and-judge status checks.", "components": ["docs"], "sources": ["docs:s6de629323c64"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "An HTTPS request without credentials should return 401 once authentication is enabled.", "components": ["docs"], "sources": ["docs:s1dbd1ce27da5"], "status": "REASONED", "verify": [1]},
    "verify-listeners": {"text": "Read every listener with ss -tlnp: front-door authentication does not establish that no other listener serves content. The ss version is unrecorded.", "components": ["tls"], "sources": ["tls:sbff3cb2e01a8"], "status": "REASONED", "verify": [1]},
    "verify-host": {"text": "In lighttpd 1.4.75, request-time $HTTP[\"host\"] matching uses the HTTP Host value, while TLS SNI can select mod_openssl settings before request headers; a Host outside a conditional auth.require falls back to global configuration for that rule (this guide's inference from conditional merging and mod_auth documentation). On a protected path, this guide expects 401 to pass and interprets 200 as an authentication bypass for the tested TLS connection. Apache 2.4.69 uses SNI for TLS virtual-host selection when supplied; varying Host while keeping URL and SNI fixed is this guide's auth-check advice.", "components": ["docs", "lighttpd-verify-source", "apache-vhosts"], "sources": ["docs:s1dbd1ce27da5", "lighttpd-verify-source:s6a29b290d83a", "lighttpd-verify-source:s2fc4cf82abd9", "lighttpd-verify-source:s3f692a48bd01", "lighttpd-verify-source:sbb09703388c3", "lighttpd-verify-source:s8bb6bd7774f9", "lighttpd-verify-source:s95b975ea9cd2", "apache-vhosts:s558db45d4d61"], "status": "REASONED", "verify": [1]}
  }
}
---
# lighttpd: TLS and authentication

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-18; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| tls-defaults: lighttpd 1.4.56 and later disables SSLv2, SSLv3, TLS 1.0 and TLS 1.1 by default. | lighttpd TLS minimum 1.4.56 | REASONED |
| tls-listeners: Load mod_openssl and enable TLS on both :443 and [::]:443 with ssl.pemfile and ssl.privkey; omitting the IPv6 socket leaves IPv6 clients on plain HTTP. | lighttpd TLS minimum 1.4.56 | REASONED |
| certificate-chain: ssl.pemfile uses fullchain.pem rather than a certificate without its chain. | lighttpd TLS minimum 1.4.56 | REASONED |
| separate-key: ssl.privkey exists from 1.4.53; older versions need certificate and key concatenated into ssl.pemfile. | lighttpd separate-key minimum 1.4.53 | REASONED |
| protocol-floor: ssl.openssl.ssl-conf-cmd sets MinProtocol to TLSv1.2 explicitly; recent versions already default to TLS 1.2. | lighttpd TLS minimum 1.4.56 | REASONED |
| module-defaults: In lighttpd 1.4.75, mod_h2 is inserted unless server.feature-flags disables server.h2proto (enabled by default); when server.compat-module-load is enabled (the default), mod_indexfile and mod_dirlisting are conditionally added when enabled, mod_staticfile is added when absent, and compatibility handling can also add other modules, including authentication and TLS modules under their respective conditions. Load mod_redirect explicitly. | lighttpd documentation unknown; lighttpd module loader source 1.4.75 | REASONED |
| http-redirect: For the http scheme, redirect to HTTPS preserving authority, path and query; port 80 must redirect rather than serve content. | lighttpd documentation unknown | REASONED |
| redirect-code: Set url.redirect-code to 308 explicitly on versions before 1.4.75. | lighttpd redirect default transition 1.4.75 | REASONED |
| basic-auth: Load mod_auth and mod_authn_file, select the htpasswd file backend and require valid-user Basic authentication on / over TLS; application login is preferable. | lighttpd documentation unknown | REASONED |
| password-file: Create the user file with Apache htpasswd (Debian apache2-utils; Fedora httpd-tools is this guide's package assessment); lighttpd 1.4.75 reads username:stored-hash entries and checks {SHA} SHA-1 and $apr1$ internally, with other hashes of at least 13 characters checked through crypt() when built with crypt support; under USE_LIB_CRYPTO_MD4, the $1+ntlm$ path derives an NTLM hash and calls crypt() with that derived value and a $1$ salt. Check the build and platform's accepted hashes before choosing a flag; this check is this guide's compatibility advice. | lighttpd documentation unknown; lighttpd file authentication source 1.4.75; Apache htpasswd manual 2.4; Debian apache2-utils package trixie; Fedora httpd-tools package unknown | REASONED |
| mfa: Basic authentication is single-factor; add MFA by fronting this service with Cloudflare Access or an MFA-capable proxy (this guide's requirement). Authelia v4.39.28's complete supported-proxy list has no lighttpd entry (this guide's inference from the table); Cloudflare Access documents self-hosted application and MFA policy controls; applying them to lighttpd is this guide's assessment. | lighttpd documentation unknown; Authelia proxy support v4.39.28; Cloudflare Access documentation commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104 | REASONED |
| verify-config: lighttpd 1.4.75 -tt -f /etc/lighttpd/lighttpd.conf tests the named file for syntax errors and initializes modules; configuration failures prevent the &amp;&amp; reload (this guide's inference from the nonzero process result and shell chaining). The cited upstream unit starts from that file and defines a USR1 reload through ExecReload; systemctl reload triggers the service action, whose signal does not establish completion. Confirm the installed unit uses that file and defines reload (this guide's advice). | lighttpd documentation unknown; lighttpd verify source 1.4.75; systemd reload manual v262 | REASONED |
| verify-redirect: The HTTP header request should show a redirect to HTTPS; these are read-and-judge status checks. | lighttpd documentation unknown | REASONED |
| verify-auth: An HTTPS request without credentials should return 401 once authentication is enabled. | lighttpd documentation unknown | REASONED |
| verify-listeners: Read every listener with ss -tlnp: front-door authentication does not establish that no other listener serves content. The ss version is unrecorded. | lighttpd TLS minimum 1.4.56 | REASONED |
| verify-host: In lighttpd 1.4.75, request-time $HTTP["host"] matching uses the HTTP Host value, while TLS SNI can select mod_openssl settings before request headers; a Host outside a conditional auth.require falls back to global configuration for that rule (this guide's inference from conditional merging and mod_auth documentation). On a protected path, this guide expects 401 to pass and interprets 200 as an authentication bypass for the tested TLS connection. Apache 2.4.69 uses SNI for TLS virtual-host selection when supplied; varying Host while keeping URL and SNI fixed is this guide's auth-check advice. | lighttpd documentation unknown; lighttpd verify source 1.4.75; Apache virtual-host source 2.4.69 | REASONED |
<!-- version-basis:end -->

Applies to lighttpd 1.4.56 and later, which disables SSLv2/SSLv3/TLS 1.0/TLS 1.1 by default. Get a certificate first: [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md).

## 1. Enable TLS

```
server.modules += ( "mod_openssl" )

$SERVER["socket"] == ":443" {
    ssl.engine  = "enable"
    ssl.pemfile = "/etc/letsencrypt/live/example.com/fullchain.pem"
    ssl.privkey = "/etc/letsencrypt/live/example.com/privkey.pem"
}

$SERVER["socket"] == "[::]:443" {
    ssl.engine  = "enable"
    ssl.pemfile = "/etc/letsencrypt/live/example.com/fullchain.pem"
    ssl.privkey = "/etc/letsencrypt/live/example.com/privkey.pem"
}
```

Version notes:

- `ssl.privkey` exists from lighttpd 1.4.53. On older versions, concatenate certificate and key into one file and point `ssl.pemfile` at it.
- To set the protocol floor explicitly (recent versions already default to TLS 1.2):

```
ssl.openssl.ssl-conf-cmd = ( "MinProtocol" => "TLSv1.2" )
```

## 2. Redirect HTTP to HTTPS

Load `mod_redirect` explicitly. In lighttpd 1.4.75, `configfile.c` inserts `mod_h2` unless `server.feature-flags` disables `server.h2proto` (enabled by default); when `server.compat-module-load` is enabled (the default), it adds `mod_indexfile` when index files are enabled, `mod_dirlisting` when directory listing is enabled, and `mod_staticfile` when it is absent from `server.modules`; compatibility handling can also add other modules, including authentication and TLS modules under their respective conditions. For other versions, check the module-loading behaviour. Per the lighttpd wiki:

```
server.modules += ( "mod_redirect" )

$HTTP["scheme"] == "http" {
    url.redirect = ("" => "https://${url.authority}${url.path}${qsa}")
    url.redirect-code = 308        # explicit on versions before 1.4.75
}
```

## 3. Require authentication

Application-level login is preferable ([authentication.md](authentication.md)). Basic authentication at the server, over TLS only:

```
server.modules += ( "mod_auth", "mod_authn_file" )

auth.backend = "htpasswd"
auth.backend.htpasswd.userfile = "/etc/lighttpd/lighttpd.user"

auth.require = ( "/" =>
  (
    "method"  => "basic",
    "realm"   => "Restricted",
    "require" => "valid-user"
  )
)
```

Create the user file with Apache's `htpasswd` (Debian `apache2-utils`; for Fedora, use `httpd-tools` as this guide's package assessment). In lighttpd 1.4.75, the htpasswd backend reads `username:stored-hash` entries; it checks `{SHA}` SHA-1 and `$apr1$` hashes internally and, when built with `crypt()` support, checks other stored hashes of at least 13 characters through the platform's `crypt()`, except that, when built with MD4 support, the `$1+ntlm$` path derives an NTLM hash and calls `crypt()` with the derived value and a `$1$` salt. Check the build and platform's accepted hash formats before choosing an `htpasswd` flag; this is the guide's compatibility advice. Check the lighttpd mod_auth documentation and Apache `htpasswd` manual in Sources for the supported hash formats.

Basic authentication is single-factor, and this guide finds no lighttpd entry in Authelia v4.39.28's complete supported-proxy list (https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/support.md#L24-L36). Add MFA by fronting the service with Cloudflare Access ([cloudflare.md](cloudflare.md)) or an MFA-capable proxy; options in [mfa.md](mfa.md). Cloudflare documents an Access application as an authentication layer between users and a self-hosted origin (https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L14-L16; https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L40-L54) and an Access policy that can require MFA (https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/policies/mfa-requirements.mdx#L35-L81). Applying these controls to a lighttpd origin is this guide's assessment.

## 4. Verify

REASONED: interpretation procedure from the status-output commands and expected outcomes below; no deployment or protected path was supplied. These are read-and-judge checks: the status code is printed and you compare it.

REASONED: configuration, redirect, authentication, listener inventory and alternate-Host checks follow the cited lighttpd TLS, mod_auth, redirect and configuration documentation and the pinned command, unit, systemd, host-condition and Apache virtual-host sources below. No deployment or protected path was supplied for live checks, and this guide records no run; expected outcomes are stated in the following block. The reload line is this guide's advice for an installed unit that reads `/etc/lighttpd/lighttpd.conf` and defines reload; confirm both before using it. The cited upstream 1.4.75 unit does so, but its signal-based reload is asynchronous.
```bash
sudo lighttpd -tt -f /etc/lighttpd/lighttpd.conf && sudo systemctl reload lighttpd
curl -q -sI http://example.com/        # expect a redirect to https://
curl -q -s -o /dev/null -w '%{http_code}\n' https://example.com/
                                    # expect 401 without credentials once auth is on

# Read every listener rather than filtering to the ports you expect. The checks above prove
# the front door asks for credentials; they do not prove it is the only door, and a filtered
# list cannot show you a port you did not think of.
ss -tlnp

# `auth.require` can sit at the top level or inside a `$HTTP["host"]` conditional, and a
# conditional one applies only to the hosts it names. If yours is conditional, a request
# carrying a host it does not name is served by the global configuration instead. That
# conditional uses the request Host for auth after headers are read. In lighttpd 1.4.75,
# TLS SNI first selects mod_openssl settings; Apache 2.4.69 uses SNI for TLS virtual-host
# selection when supplied. This guide's advice is to vary Host while keeping the URL and
# SNI fixed for this auth check:
curl -q -s -o /dev/null -w '%{http_code}\n' -H 'Host: not-configured.example' \
  https://example.com/REPLACE_WITH_A_PROTECTED_PATH
                                    # 401 is the pass. 200 means the protected path is served
                                    # without authentication to anyone who sends another host
```

## Common mistakes

- Loading `mod_openssl` but leaving the `:80` socket serving content instead of only the redirect.
- Forgetting the `[::]:443` socket, leaving IPv6 clients on plain HTTP.
- Pointing `ssl.pemfile` at a certificate without its chain; use `fullchain.pem`.

## Sources (checked September 2026)

- lighttpd 1.4.75 -f option (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/doc/lighttpd.8#L22-L23
- lighttpd 1.4.75 -tt option (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/doc/lighttpd.8#L33-L37
- lighttpd 1.4.75 configuration-read error exit (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/server.c#L1439-L1451
- lighttpd 1.4.75 -tt option parsing (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/server.c#L1466-L1467
- lighttpd 1.4.75 preflight test path (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/server.c#L1510-L1523
- lighttpd 1.4.75 module and configuration-finalization error exits (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/server.c#L1942-L1953
- lighttpd 1.4.75 process exit result (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/server.c#L2320-L2384
- lighttpd 1.4.75 USR1 graceful restart handler (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/server.c#L229-L235
- lighttpd 1.4.75 upstream systemd unit (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/doc/systemd/lighttpd.service#L5-L11
- lighttpd 1.4.75 Host header parsing (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/request.c#L423-L430
- lighttpd 1.4.75 request authority from Host (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/request.c#L1235-L1247
- lighttpd 1.4.75 host-condition value (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/configfile-glue.c#L504-L508
- lighttpd 1.4.75 conditional configuration merge (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/configfile.c#L213-L223
- lighttpd 1.4.75 OpenSSL conditional settings (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/mod_openssl.c#L1025-L1034
- lighttpd 1.4.75 SNI callback and Host-condition reset (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/mod_openssl.c#L1295-L1330
- systemd v262 systemctl reload semantics (checked October 2026): https://github.com/systemd/systemd/blob/v262/man/systemctl.xml#L462-L474
- systemd v262 ExecReload and asynchronous signal semantics (checked October 2026): https://github.com/systemd/systemd/blob/v262/man/systemd.service.xml#L498-L519
- Apache 2.4.69 TLS virtual-host SNI selection (checked October 2026): https://github.com/apache/httpd/blob/2.4.69/docs/manual/vhosts/details.xml#L217-L231
- lighttpd TLS documentation (1.4.56 and later; ssl.privkey from 1.4.53): https://redmine.lighttpd.net/projects/lighttpd/wiki/Docs_SSL
- lighttpd mod_auth documentation, including `auth.require` inside a `$HTTP["host"]` conditional: https://redmine.lighttpd.net/projects/lighttpd/wiki/Mod_auth
- lighttpd HTTP-to-HTTPS redirect how-to (308 explicit before 1.4.75): https://redmine.lighttpd.net/projects/lighttpd/wiki/HowToRedirectHttpToHttps
- lighttpd configuration options (`server.modules` and default modules): https://redmine.lighttpd.net/projects/lighttpd/wiki/Docs_ConfigurationOptions
- lighttpd 1.4.75 compatibility loader and conditional modules source (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/configfile.c#L395-L544
- lighttpd 1.4.75 TLS module helper source (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/configfile.c#L270-L290
- lighttpd 1.4.75 authentication module helper source (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/configfile.c#L382-L393
- lighttpd 1.4.75 directive binding, feature flag and compatibility gate source (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/configfile.c#L662-L945
- lighttpd 1.4.75 compatibility loader default source (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/configfile.c#L1684-L1711
- lighttpd 1.4.75 htpasswd parsing source (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/mod_authn_file.c#L340-L397
- lighttpd 1.4.75 htpasswd password check source (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/mod_authn_file.c#L613-L740
- Apache HTTP Server 2.4 `htpasswd` manual (checked October 2026): https://httpd.apache.org/docs/2.4/programs/htpasswd.html
- Debian trixie `apache2-utils` package (checked October 2026): https://packages.debian.org/trixie/apache2-utils
- Authelia v4.39.28 supported-proxy list, complete table (checked October 2026): https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/support.md#L24-L36
- Cloudflare Access self-hosted application at commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104 (checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L14-L16 ; https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L40-L54
- Cloudflare Access MFA policy controls at commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104 (checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/policies/mfa-requirements.mdx#L35-L81
- Fedora `httpd-tools` package (checked October 2026): https://packages.fedoraproject.org/pkgs/httpd/httpd-tools/
