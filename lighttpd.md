# lighttpd: TLS and authentication

lighttpd is a web server used to serve websites and web applications. This guide helps your AI assistant make sure it is configured securely: enabling TLS, redirecting HTTP to HTTPS, and requiring authentication.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/lighttpd.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against lighttpd TLS minimum 1.4.56, lighttpd separate-key minimum 1.4.53, lighttpd redirect default transition 1.4.75, lighttpd module loader source 1.4.75, lighttpd file authentication source 1.4.75, lighttpd verify source 1.4.75, Apache htpasswd manual 2.4, and Debian apache2-utils package trixie, plus 5 more recorded bases; 2 further sources carry no recorded version. Metadata reviewed 2026-10-19; documentation checked September 2026. The guide records 16 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

Applies to lighttpd 1.4.56 and later. NEWS records the `mod_openssl` `MinProtocol TLSv1.2` default in its 1.4.56 release section (https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/NEWS#L1660-L1660; https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/NEWS#L1927-L1927). Disabling SSLv2/SSLv3/TLS 1.0/TLS 1.1 is this guide's reading of that floor; NEWS does not establish defaults for every later release. Get a certificate first: [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md).

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

- NEWS records the optional `mod_openssl` `ssl.privkey` directive in its 1.4.53 release section (https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/NEWS#L2465-L2465; https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/NEWS#L2505-L2505). On older versions, concatenate certificate and key into one file and point `ssl.pemfile` at it (this guide's compatibility advice; the entry does not establish that procedure).
- To set the protocol floor explicitly (this guide's advice; NEWS records the `mod_openssl` TLS 1.2 minimum default in 1.4.56, not every later release):

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

NEWS records `url.redirect-code = 308` as the new default in its 1.4.75 release section (https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/NEWS#L6-L7). Setting 308 explicitly before 1.4.75 is this guide's advice; the entry does not specify each earlier default.

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

Create the user file with Apache's `htpasswd` (Debian `apache2-utils`; for Fedora, use `httpd-tools` as this guide's package assessment). In lighttpd 1.4.75, the htpasswd backend reads `username:stored-hash` entries; it checks `{SHA}` SHA-1 and `$apr1$` hashes internally and, when built with `crypt()` support, checks other stored hashes of at least 13 characters through the platform's `crypt()`, except that, when built with MD4 support, the `$1+ntlm$` path derives an NTLM hash and calls `crypt()` with the derived value and a `$1$` salt. The `$1+ntlm$` path is conditional on `USE_LIB_CRYPTO_MD4` in the 1.4.75 source (https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/mod_authn_file.c#L340-L397; https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/mod_authn_file.c#L613-L740). Check the build and platform's accepted hash formats before choosing an `htpasswd` flag; this is the guide's compatibility advice. Check the lighttpd mod_auth documentation and Apache `htpasswd` manual in Sources for the supported hash formats.

Basic authentication is single-factor, and this guide finds no lighttpd entry in Authelia v4.39.28's complete supported-proxy list (https://github.com/authelia/authelia/blob/v4.39.28/docs/content/integration/proxies/support.md#L24-L36). Add MFA by fronting the service with Cloudflare Access ([cloudflare.md](cloudflare.md)) or an MFA-capable proxy; options in [mfa.md](mfa.md). Cloudflare documents an Access application as an authentication layer between users and a self-hosted origin (https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L14-L16; https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L40-L54) and an Access policy that can require MFA (https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/policies/mfa-requirements.mdx#L35-L81). Applying these controls to a lighttpd origin is this guide's assessment. This guide assesses that a lighttpd origin reachable without passing through Access is not protected by it (https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L45-L45; https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L48-L48).

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
# carrying a host it does not name is served by the global configuration instead (this
# guide's inference from conditional merging and the mod_auth documentation). That
# conditional uses the request Host for auth after headers are read. In lighttpd 1.4.75,
# TLS SNI, when the client sends it, first selects mod_openssl settings; Apache
# 2.4.69 uses the SNI hostname, when the client sends it and the server supports SNI,
# for name-based TLS virtual-host
# selection. This guide's advice is to vary Host while keeping the URL and SNI fixed for
# this auth check:
curl -q -s -o /dev/null -w '%{http_code}\n' -H 'Host: not-configured.example' \
  https://example.com/REPLACE_WITH_A_PROTECTED_PATH
                                    # This guide interprets 401 as the pass and 200 as the protected
                                    # path served without authentication on this TLS connection to a
                                    # client that sends another host
```

## Common mistakes

- Loading `mod_openssl` but leaving the `:80` socket serving content instead of only the redirect.
- Forgetting the `[::]:443` socket, leaving IPv6 clients on plain HTTP.
- Pointing `ssl.pemfile` at a certificate without its chain; use `fullchain.pem`.

## Sources (checked September 2026)

- lighttpd 1.4.75 NEWS, 1.4.56 release heading (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/NEWS#L1660-L1660
- lighttpd 1.4.75 NEWS, 1.4.56 mod_openssl protocol default (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/NEWS#L1927-L1927
- lighttpd 1.4.75 NEWS, 1.4.53 release heading (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/NEWS#L2465-L2465
- lighttpd 1.4.75 NEWS, 1.4.53 optional separate-key directive (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/NEWS#L2505-L2505
- lighttpd 1.4.75 NEWS, 1.4.75 redirect-code default (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/NEWS#L6-L7

- lighttpd 1.4.75 -f option (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/doc/lighttpd.8#L22-L23
- lighttpd 1.4.75 -t and -tt options (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/doc/lighttpd.8#L33-L37
- lighttpd 1.4.75 configuration-read error exit (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/server.c#L1439-L1451
- lighttpd 1.4.75 -p and -t option parsing (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/server.c#L1466-L1467
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
- lighttpd 1.4.75 SNI callback and deferred Host-condition reset note (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/mod_openssl.c#L1294-L1330
- lighttpd 1.4.75 post-header condition-cache reset and configuration merge (checked October 2026): https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/response.c#L227-L228
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
- Cloudflare Access origin reachability at commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104 (checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L45-L45 ; https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L48-L48
- Cloudflare Access MFA policy controls at commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104 (checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/policies/mfa-requirements.mdx#L35-L81
- Fedora `httpd-tools` package (checked October 2026): https://packages.fedoraproject.org/pkgs/httpd/httpd-tools/


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- tls: lighttpd TLS minimum (1.4.56)
- key: lighttpd separate-key minimum (1.4.53)
- redirect: lighttpd redirect default transition (1.4.75)
- modules-source: lighttpd module loader source (1.4.75)
- authn-source: lighttpd file authentication source (1.4.75)
- lighttpd-verify-source: lighttpd verify source (1.4.75)
- docs: lighttpd documentation (unknown)
- htpasswd-tool: Apache htpasswd manual (2.4)
- debian-package: Debian apache2-utils package (trixie)
- authelia: Authelia proxy support (v4.39.28)
- cloudflare-access: Cloudflare Access documentation (commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104)
- fedora-package: Fedora httpd-tools package (unknown)
- apache-vhosts: Apache virtual-host source (2.4.69)
- systemd-reload: systemd reload manual (v262)
- release-news: lighttpd release NEWS (1.4.75)

Claims (full source mapping in the JSON block below):

- tls-defaults (REASONED; tls, release-news): For this guide's 1.4.56-and-later scope, NEWS records the mod_openssl MinProtocol TLSv1.2 default in 1.4.56. Disabling SSLv2, SSLv3, TLS 1.0 and TLS 1.1 is this guide's reading of that floor; NEWS does not establish defaults for every later release.
- tls-listeners (REASONED; tls): Load mod_openssl and enable TLS on both :443 and [::]:443 with ssl.pemfile and ssl.privkey; omitting the IPv6 socket leaves IPv6 clients on plain HTTP.
- certificate-chain (REASONED; tls): ssl.pemfile uses fullchain.pem rather than a certificate without its chain.
- separate-key (REASONED; key, release-news): NEWS records optional mod_openssl ssl.privkey in 1.4.53. On older versions, concatenate certificate and key into ssl.pemfile (this guide's compatibility advice; the entry does not establish that procedure).
- protocol-floor (REASONED; tls, release-news): Set MinProtocol to TLSv1.2 with ssl.openssl.ssl-conf-cmd explicitly (this guide's advice); NEWS records that default for mod_openssl in 1.4.56, not every later release.
- module-defaults (REASONED; docs, modules-source): In lighttpd 1.4.75, mod_h2 is inserted unless server.feature-flags disables server.h2proto (enabled by default); when server.compat-module-load is enabled (the default), compatibility handling can add other modules, including authentication and TLS modules under their respective conditions. Load mod_redirect explicitly.
- http-redirect (REASONED; docs): For the http scheme, redirect to HTTPS preserving authority, path and query; port 80 must redirect rather than serve content.
- redirect-code (REASONED; redirect, release-news): NEWS records url.redirect-code = 308 as the new default in 1.4.75. Set 308 explicitly before 1.4.75 (this guide's advice; the entry does not specify each earlier default).
- basic-auth (REASONED; docs): Load mod_auth and mod_authn_file, select the htpasswd file backend and require valid-user Basic authentication on / over TLS; application login is preferable.
- password-file (REASONED; docs, authn-source, htpasswd-tool, debian-package, fedora-package): Create the user file with Apache htpasswd (Debian apache2-utils; Fedora httpd-tools is this guide's package assessment); lighttpd 1.4.75 reads username:stored-hash entries and checks {SHA} SHA-1 and $apr1$ internally. Check the build and platform's accepted hashes before choosing a flag; this check is this guide's compatibility advice.
- mfa (REASONED; docs, authelia, cloudflare-access): Basic authentication is single-factor; add MFA by fronting this service with Cloudflare Access or an MFA-capable proxy (this guide's requirement). Authelia v4.39.28's complete supported-proxy list has no lighttpd entry (this guide's inference from the table); Cloudflare Access documents self-hosted application and MFA policy controls; applying them to lighttpd is this guide's assessment. This guide assesses that a lighttpd origin reachable without passing through Access is not protected by it.
- verify-config (REASONED; docs, lighttpd-verify-source, systemd-reload): lighttpd 1.4.75 -tt -f /etc/lighttpd/lighttpd.conf tests the named file for syntax errors and initializes modules; configuration failures prevent the &amp;&amp; reload (this guide's inference from the nonzero process result and shell chaining). The cited upstream unit starts from that file and defines a USR1 reload through ExecReload; systemctl reload triggers the service action, whose signal does not establish completion. Confirm the installed unit uses that file and defines reload (this guide's advice).
- verify-redirect (REASONED; docs): The HTTP header request should show a redirect to HTTPS; these are read-and-judge status checks.
- verify-auth (REASONED; docs): An HTTPS request without credentials should return 401 once authentication is enabled.
- verify-listeners (REASONED; tls): Read every listener with ss -tlnp: front-door authentication does not establish that no other listener serves content. The ss version is unrecorded.
- verify-host (REASONED; docs, lighttpd-verify-source, apache-vhosts): In lighttpd 1.4.75, request-time $HTTP["host"] matching uses the HTTP Host value, while TLS SNI can select mod_openssl settings before request headers; a Host outside a conditional auth.require falls back to global configuration for that rule (this guide's inference from conditional merging and mod_auth documentation). On a protected path, this guide interprets 401 as the pass and 200 as the protected path served without authentication on this TLS connection to a client that sends another host. Apache 2.4.69 uses the SNI hostname, when the client sends it and the server supports SNI, for name-based TLS virtual-host selection; varying Host while keeping URL and SNI fixed is this guide's auth-check advice.

````json
{
  "schema": 1,
  "checked": "2026-10-19",
  "documentation_checked": "2026-09",
  "body_sha256": "7bfc855c138546c2ecee38aba490f33a37fc0d0737f40a6c8cafb18c357d5ead",
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
        "sb4c43fa1a807": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/mod_openssl.c#L1294-L1330",
        "s9e49b928cc81": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/src/response.c#L227-L228"
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
        "s603bdb6b24ab": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L45-L45",
        "s863803bd9a1f": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app.mdx#L48-L48",
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
    "apache-vhosts": {
      "name": "Apache virtual-host source",
      "basis": "2.4.69",
      "sources": {
        "s558db45d4d61": "https://github.com/apache/httpd/blob/2.4.69/docs/manual/vhosts/details.xml#L217-L231"
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
    "release-news": {
      "name": "lighttpd release NEWS",
      "basis": "1.4.75",
      "sources": {
        "s4e990a9e5ec1": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/NEWS#L1660-L1660",
        "se97c93bf64a8": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/NEWS#L1927-L1927",
        "s1658d22c71f9": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/NEWS#L2465-L2465",
        "s95dd525fe4ac": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/NEWS#L2505-L2505",
        "sc0d0162991d5": "https://git.lighttpd.net/lighttpd/lighttpd1.4/src/tag/lighttpd-1.4.75/NEWS#L6-L7"
      }
    }
  },
  "claims": {
    "tls-defaults": {"text": "For this guide's 1.4.56-and-later scope, NEWS records the mod_openssl MinProtocol TLSv1.2 default in 1.4.56. Disabling SSLv2, SSLv3, TLS 1.0 and TLS 1.1 is this guide's reading of that floor; NEWS does not establish defaults for every later release.", "components": ["tls", "release-news"], "sources": ["tls:sbff3cb2e01a8", "release-news:s4e990a9e5ec1", "release-news:se97c93bf64a8"], "status": "REASONED"},
    "tls-listeners": {"text": "Load mod_openssl and enable TLS on both :443 and [::]:443 with ssl.pemfile and ssl.privkey; omitting the IPv6 socket leaves IPv6 clients on plain HTTP.", "components": ["tls"], "sources": ["tls:sbff3cb2e01a8"], "status": "REASONED"},
    "certificate-chain": {"text": "ssl.pemfile uses fullchain.pem rather than a certificate without its chain.", "components": ["tls"], "sources": ["tls:sbff3cb2e01a8"], "status": "REASONED"},
    "separate-key": {"text": "NEWS records optional mod_openssl ssl.privkey in 1.4.53. On older versions, concatenate certificate and key into ssl.pemfile (this guide's compatibility advice; the entry does not establish that procedure).", "components": ["key", "release-news"], "sources": ["key:sbff3cb2e01a8", "release-news:s1658d22c71f9", "release-news:s95dd525fe4ac"], "status": "REASONED"},
    "protocol-floor": {"text": "Set MinProtocol to TLSv1.2 with ssl.openssl.ssl-conf-cmd explicitly (this guide's advice); NEWS records that default for mod_openssl in 1.4.56, not every later release.", "components": ["tls", "release-news"], "sources": ["tls:sbff3cb2e01a8", "release-news:s4e990a9e5ec1", "release-news:se97c93bf64a8"], "status": "REASONED"},
    "module-defaults": {"text": "In lighttpd 1.4.75, mod_h2 is inserted unless server.feature-flags disables server.h2proto (enabled by default); when server.compat-module-load is enabled (the default), compatibility handling can add other modules, including authentication and TLS modules under their respective conditions. Load mod_redirect explicitly.", "components": ["docs", "modules-source"], "sources": ["docs:s6d5666b862a0", "modules-source:s8680e561bed2", "modules-source:s8e9688979427", "modules-source:s9bd716d27e8d", "modules-source:s21288573041a", "modules-source:s67bb3733d81c"], "status": "REASONED"},
    "http-redirect": {"text": "For the http scheme, redirect to HTTPS preserving authority, path and query; port 80 must redirect rather than serve content.", "components": ["docs"], "sources": ["docs:s6de629323c64"], "status": "REASONED"},
    "redirect-code": {"text": "NEWS records url.redirect-code = 308 as the new default in 1.4.75. Set 308 explicitly before 1.4.75 (this guide's advice; the entry does not specify each earlier default).", "components": ["redirect", "release-news"], "sources": ["redirect:s6de629323c64", "release-news:sc0d0162991d5"], "status": "REASONED"},
    "basic-auth": {"text": "Load mod_auth and mod_authn_file, select the htpasswd file backend and require valid-user Basic authentication on / over TLS; application login is preferable.", "components": ["docs"], "sources": ["docs:s1dbd1ce27da5"], "status": "REASONED"},
    "password-file": {"text": "Create the user file with Apache htpasswd (Debian apache2-utils; Fedora httpd-tools is this guide's package assessment); lighttpd 1.4.75 reads username:stored-hash entries and checks {SHA} SHA-1 and $apr1$ internally. Check the build and platform's accepted hashes before choosing a flag; this check is this guide's compatibility advice.", "components": ["docs", "authn-source", "htpasswd-tool", "debian-package", "fedora-package"], "sources": ["docs:s1dbd1ce27da5", "authn-source:s2c11c0fbc0ca", "authn-source:se971effb489f", "htpasswd-tool:scde9004bb967", "debian-package:s436bdf5f1fb9", "fedora-package:s919088d03a5e"], "status": "REASONED"},
    "mfa": {"text": "Basic authentication is single-factor; add MFA by fronting this service with Cloudflare Access or an MFA-capable proxy (this guide's requirement). Authelia v4.39.28's complete supported-proxy list has no lighttpd entry (this guide's inference from the table); Cloudflare Access documents self-hosted application and MFA policy controls; applying them to lighttpd is this guide's assessment. This guide assesses that a lighttpd origin reachable without passing through Access is not protected by it.", "components": ["docs", "authelia", "cloudflare-access"], "sources": ["docs:s1dbd1ce27da5", "authelia:s77083bc8faa2", "cloudflare-access:sfddb92e438ca", "cloudflare-access:s7cafe1b17afd", "cloudflare-access:sdcac732541da", "cloudflare-access:s603bdb6b24ab", "cloudflare-access:s863803bd9a1f"], "status": "REASONED"},
    "verify-config": {"text": "lighttpd 1.4.75 -tt -f /etc/lighttpd/lighttpd.conf tests the named file for syntax errors and initializes modules; configuration failures prevent the && reload (this guide's inference from the nonzero process result and shell chaining). The cited upstream unit starts from that file and defines a USR1 reload through ExecReload; systemctl reload triggers the service action, whose signal does not establish completion. Confirm the installed unit uses that file and defines reload (this guide's advice).", "components": ["docs", "lighttpd-verify-source", "systemd-reload"], "sources": ["docs:s6d5666b862a0", "lighttpd-verify-source:s0bbb4c861d5e", "lighttpd-verify-source:sca076bcd18dc", "lighttpd-verify-source:s9e69235fbbc7", "lighttpd-verify-source:s87104d328493", "lighttpd-verify-source:sba72bab46867", "lighttpd-verify-source:s2faa9b3149ac", "lighttpd-verify-source:s87b4b266bb0e", "lighttpd-verify-source:sa989ef425f1d", "lighttpd-verify-source:sf9d56b052c61", "systemd-reload:sb3f5069cd250", "systemd-reload:s441757b7048f"], "status": "REASONED", "verify": [1]},
    "verify-redirect": {"text": "The HTTP header request should show a redirect to HTTPS; these are read-and-judge status checks.", "components": ["docs"], "sources": ["docs:s6de629323c64"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "An HTTPS request without credentials should return 401 once authentication is enabled.", "components": ["docs"], "sources": ["docs:s1dbd1ce27da5"], "status": "REASONED", "verify": [1]},
    "verify-listeners": {"text": "Read every listener with ss -tlnp: front-door authentication does not establish that no other listener serves content. The ss version is unrecorded.", "components": ["tls"], "sources": ["tls:sbff3cb2e01a8"], "status": "REASONED", "verify": [1]},
    "verify-host": {"text": "In lighttpd 1.4.75, request-time $HTTP[\"host\"] matching uses the HTTP Host value, while TLS SNI can select mod_openssl settings before request headers; a Host outside a conditional auth.require falls back to global configuration for that rule (this guide's inference from conditional merging and mod_auth documentation). On a protected path, this guide interprets 401 as the pass and 200 as the protected path served without authentication on this TLS connection to a client that sends another host. Apache 2.4.69 uses the SNI hostname, when the client sends it and the server supports SNI, for name-based TLS virtual-host selection; varying Host while keeping URL and SNI fixed is this guide's auth-check advice.", "components": ["docs", "lighttpd-verify-source", "apache-vhosts"], "sources": ["docs:s1dbd1ce27da5", "lighttpd-verify-source:s6a29b290d83a", "lighttpd-verify-source:s2fc4cf82abd9", "lighttpd-verify-source:s3f692a48bd01", "lighttpd-verify-source:sbb09703388c3", "lighttpd-verify-source:s8bb6bd7774f9", "lighttpd-verify-source:sb4c43fa1a807", "lighttpd-verify-source:s9e49b928cc81", "apache-vhosts:s558db45d4d61"], "status": "REASONED", "verify": [1]}
  }
}
````
<!-- version-basis:end -->
