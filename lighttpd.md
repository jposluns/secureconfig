---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "1af8ee3401d7827e532ae96a905cf473eb5726da3f950e6ab9e6791a20736f67",
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
    }
  },
  "claims": {
    "tls-defaults": {"text": "lighttpd 1.4.56 and later disables SSLv2, SSLv3, TLS 1.0 and TLS 1.1 by default.", "components": ["tls"], "sources": ["tls:sbff3cb2e01a8"], "status": "REASONED"},
    "tls-listeners": {"text": "Load mod_openssl and enable TLS on both :443 and [::]:443 with ssl.pemfile and ssl.privkey; omitting the IPv6 socket leaves IPv6 clients on plain HTTP.", "components": ["tls"], "sources": ["tls:sbff3cb2e01a8"], "status": "REASONED"},
    "certificate-chain": {"text": "ssl.pemfile uses fullchain.pem rather than a certificate without its chain.", "components": ["tls"], "sources": ["tls:sbff3cb2e01a8"], "status": "REASONED"},
    "separate-key": {"text": "ssl.privkey exists from 1.4.53; older versions need certificate and key concatenated into ssl.pemfile.", "components": ["key"], "sources": ["key:sbff3cb2e01a8"], "status": "REASONED"},
    "protocol-floor": {"text": "ssl.openssl.ssl-conf-cmd sets MinProtocol to TLSv1.2 explicitly; recent versions already default to TLS 1.2.", "components": ["tls"], "sources": ["tls:sbff3cb2e01a8"], "status": "REASONED"},
    "module-defaults": {"text": "Only mod_indexfile, mod_dirlisting and mod_staticfile load without server.modules entries; load mod_redirect explicitly.", "components": ["docs"], "sources": ["docs:s6d5666b862a0"], "status": "REASONED"},
    "http-redirect": {"text": "For the http scheme, redirect to HTTPS preserving authority, path and query; port 80 must redirect rather than serve content.", "components": ["docs"], "sources": ["docs:s6de629323c64"], "status": "REASONED"},
    "redirect-code": {"text": "Set url.redirect-code to 308 explicitly on versions before 1.4.75.", "components": ["redirect"], "sources": ["redirect:s6de629323c64"], "status": "REASONED"},
    "basic-auth": {"text": "Load mod_auth and mod_authn_file, select the htpasswd file backend and require valid-user Basic authentication on / over TLS; application login is preferable.", "components": ["docs"], "sources": ["docs:s1dbd1ce27da5"], "status": "REASONED"},
    "password-file": {"text": "Create the user file with Apache htpasswd; the backend reads user:crypt()-hashed-password entries and accepted hashes depend on the build.", "components": ["docs"], "sources": ["docs:s1dbd1ce27da5"], "status": "REASONED"},
    "mfa": {"text": "Basic authentication is single-factor; use an MFA-capable front proxy. The stated Authelia support-list exclusion and Cloudflare Access option lack direct Sources entries.", "components": ["docs"], "sources": ["docs:s1dbd1ce27da5"], "status": "REASONED"},
    "verify-config": {"text": "lighttpd -tt checks /etc/lighttpd/lighttpd.conf before systemctl reload; command-specific and service-manager sources are not recorded.", "components": ["docs"], "sources": ["docs:s6d5666b862a0"], "status": "REASONED", "verify": [1]},
    "verify-redirect": {"text": "The HTTP header request should show a redirect to HTTPS; these are read-and-judge status checks.", "components": ["docs"], "sources": ["docs:s6de629323c64"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "An HTTPS request without credentials should return 401 once authentication is enabled.", "components": ["docs"], "sources": ["docs:s1dbd1ce27da5"], "status": "REASONED", "verify": [1]},
    "verify-listeners": {"text": "Read every listener with ss -tlnp: front-door authentication does not establish that no other listener serves content. The ss version is unrecorded.", "components": ["tls"], "sources": ["tls:sbff3cb2e01a8"], "status": "REASONED", "verify": [1]},
    "verify-host": {"text": "A Host header outside a conditional auth.require falls back to global configuration; on a protected path, 401 passes and 200 exposes an authentication bypass. The Apache SNI comparison lacks a Sources entry.", "components": ["docs"], "sources": ["docs:s1dbd1ce27da5"], "status": "REASONED", "verify": [1]}
  }
}
---
# lighttpd: TLS and authentication

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| tls-defaults: lighttpd 1.4.56 and later disables SSLv2, SSLv3, TLS 1.0 and TLS 1.1 by default. | lighttpd TLS minimum 1.4.56 | REASONED |
| tls-listeners: Load mod_openssl and enable TLS on both :443 and [::]:443 with ssl.pemfile and ssl.privkey; omitting the IPv6 socket leaves IPv6 clients on plain HTTP. | lighttpd TLS minimum 1.4.56 | REASONED |
| certificate-chain: ssl.pemfile uses fullchain.pem rather than a certificate without its chain. | lighttpd TLS minimum 1.4.56 | REASONED |
| separate-key: ssl.privkey exists from 1.4.53; older versions need certificate and key concatenated into ssl.pemfile. | lighttpd separate-key minimum 1.4.53 | REASONED |
| protocol-floor: ssl.openssl.ssl-conf-cmd sets MinProtocol to TLSv1.2 explicitly; recent versions already default to TLS 1.2. | lighttpd TLS minimum 1.4.56 | REASONED |
| module-defaults: Only mod_indexfile, mod_dirlisting and mod_staticfile load without server.modules entries; load mod_redirect explicitly. | lighttpd documentation unknown | REASONED |
| http-redirect: For the http scheme, redirect to HTTPS preserving authority, path and query; port 80 must redirect rather than serve content. | lighttpd documentation unknown | REASONED |
| redirect-code: Set url.redirect-code to 308 explicitly on versions before 1.4.75. | lighttpd redirect default transition 1.4.75 | REASONED |
| basic-auth: Load mod_auth and mod_authn_file, select the htpasswd file backend and require valid-user Basic authentication on / over TLS; application login is preferable. | lighttpd documentation unknown | REASONED |
| password-file: Create the user file with Apache htpasswd; the backend reads user:crypt()-hashed-password entries and accepted hashes depend on the build. | lighttpd documentation unknown | REASONED |
| mfa: Basic authentication is single-factor; use an MFA-capable front proxy. The stated Authelia support-list exclusion and Cloudflare Access option lack direct Sources entries. | lighttpd documentation unknown | REASONED |
| verify-config: lighttpd -tt checks /etc/lighttpd/lighttpd.conf before systemctl reload; command-specific and service-manager sources are not recorded. | lighttpd documentation unknown | REASONED |
| verify-redirect: The HTTP header request should show a redirect to HTTPS; these are read-and-judge status checks. | lighttpd documentation unknown | REASONED |
| verify-auth: An HTTPS request without credentials should return 401 once authentication is enabled. | lighttpd documentation unknown | REASONED |
| verify-listeners: Read every listener with ss -tlnp: front-door authentication does not establish that no other listener serves content. The ss version is unrecorded. | lighttpd TLS minimum 1.4.56 | REASONED |
| verify-host: A Host header outside a conditional auth.require falls back to global configuration; on a protected path, 401 passes and 200 exposes an authentication bypass. The Apache SNI comparison lacks a Sources entry. | lighttpd documentation unknown | REASONED |
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

`mod_redirect` must be loaded: only `mod_indexfile`, `mod_dirlisting`, and `mod_staticfile` load without being listed in `server.modules`. Per the lighttpd wiki:

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

Create the user file with Apache's `htpasswd` (package `apache2-utils` or `httpd-tools`). The lighttpd htpasswd backend reads `user:crypt()-hashed-password` entries; check the mod_auth documentation below for the hash algorithms your lighttpd build accepts before choosing an `htpasswd` flag.

Basic authentication is single-factor, and lighttpd is absent from Authelia's supported-proxy list. Add MFA by fronting the service with Cloudflare Access ([cloudflare.md](cloudflare.md)) or an MFA-capable proxy; options in [mfa.md](mfa.md).

## 4. Verify

These are read-and-judge checks: the status code is printed and you compare it.

REASONED: configuration, redirect, authentication, listener inventory and alternate-Host checks follow the cited lighttpd TLS, mod_auth, redirect and configuration documentation. No deployment or protected path was supplied for live checks, and this guide records no run; expected outcomes are stated in the following block.

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
# conditional reads the Host HEADER, so setting the header is the right test here, unlike
# Apache, which selects its virtual host by the SNI name when the connection is TLS:
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

- lighttpd TLS documentation (1.4.56 and later; ssl.privkey from 1.4.53): https://redmine.lighttpd.net/projects/lighttpd/wiki/Docs_SSL
- lighttpd mod_auth documentation, including `auth.require` inside a `$HTTP["host"]` conditional: https://redmine.lighttpd.net/projects/lighttpd/wiki/Mod_auth
- lighttpd HTTP-to-HTTPS redirect how-to (308 explicit before 1.4.75): https://redmine.lighttpd.net/projects/lighttpd/wiki/HowToRedirectHttpToHttps
- lighttpd configuration options (`server.modules`, the three modules loaded by default): https://redmine.lighttpd.net/projects/lighttpd/wiki/Docs_ConfigurationOptions
