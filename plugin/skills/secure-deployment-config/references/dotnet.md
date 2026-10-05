---
version_basis: {
  "schema": 1,
  "checked": "2026-10-05",
  "documentation_checked": "2026-09",
  "body_sha256": "9d0e36ae7a3e5baed014b5e060adef6d2c09c78d38e8b31cf7320d856a4be63a",
  "components": {
    "docs": {
      "name": "ASP.NET Core documentation",
      "basis": ".NET 10",
      "sources": {
        "s8c762260991c": "https://learn.microsoft.com/en-us/aspnet/core/security/enforcing-ssl?view=aspnetcore-10.0",
        "s74dcd6a72d63": "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/kestrel/endpoints?view=aspnetcore-10.0",
        "s5701d26de241": "https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/proxy-load-balancer?view=aspnetcore-10.0",
        "s3790c49f70b9": "https://learn.microsoft.com/en-us/aspnet/core/security/authentication/identity?view=aspnetcore-10.0",
        "s9d10c561bb48": "https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.identity.passwordhasheroptions?view=aspnetcore-10.0",
        "sa3c22a38f4cb": "https://learn.microsoft.com/en-us/aspnet/core/security/authentication/cookie?view=aspnetcore-10.0",
        "sb6780977fa3f": "https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.http.cookiesecurepolicy?view=aspnetcore-10.0",
        "s592dc85bb71f": "https://learn.microsoft.com/en-us/aspnet/core/security/authentication/configure-oidc-web-authentication?view=aspnetcore-10.0",
        "s6afc0255098f": "https://learn.microsoft.com/en-us/dotnet/api/system.net.http.httpclienthandler.dangerousacceptanyservercertificatevalidator?view=net-10.0",
        "s2d5a930aac35": "https://learn.microsoft.com/en-us/aspnet/core/security/authentication/mfa?view=aspnetcore-10.0"
      }
    },
    "rate-min": {
      "name": "ASP.NET Core rate-limiter minimum",
      "basis": ".NET 7",
      "sources": {
        "sd3fef8f45066": "https://learn.microsoft.com/en-us/aspnet/core/performance/rate-limit"
      }
    },
    "net10": {
      "name": "ASP.NET Core",
      "basis": ".NET 10",
      "sources": {
        "s74dcd6a72d63": "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/kestrel/endpoints?view=aspnetcore-10.0",
        "s5701d26de241": "https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/proxy-load-balancer?view=aspnetcore-10.0",
        "s0d7c367ac06f": "https://learn.microsoft.com/en-us/aspnet/core/security/authentication/identity-configuration?view=aspnetcore-10.0",
        "sc0654e58fc4c": "https://learn.microsoft.com/en-us/aspnet/core/security/samesite?view=aspnetcore-10.0",
        "s837df4b1657f": "https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/cookie-authentication-api-endpoints?view=aspnetcore-10.0",
        "s2f7e6a8213f1": "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling?view=aspnetcore-10.0",
        "s61afb89034f8": "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/environments?view=aspnetcore-10.0",
        "s9d290374f4e8": "https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.builder.migrationsendpointextensions.usemigrationsendpoint?view=aspnetcore-10.0",
        "s1ce47370d948": "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/kestrel/options?view=aspnetcore-10.0",
        "s55f298bf0048": "https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.mvc.disablerequestsizelimitattribute?view=aspnetcore-10.0",
        "s792d3e8f3e42": "https://learn.microsoft.com/en-us/aspnet/core/mvc/models/file-uploads?view=aspnetcore-10.0",
        "s529a3d7cce08": "https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/iis/in-process-hosting?view=aspnetcore-10.0",
        "s6682926c8da7": "https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/configuration/overview?view=aspnetcore-10.0",
        "s66f1ab4555d6": "https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/configuration/default-settings?view=aspnetcore-10.0",
        "sd635cefc0a9f": "https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.dataprotection.dataprotectionbuilderextensions.protectkeyswithcertificate?view=aspnetcore-10.0",
        "s9463626a3d0e": "https://learn.microsoft.com/en-us/aspnet/core/security/cookie-sharing?view=aspnetcore-10.0",
        "s1d58219cedec": "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/aspnetcore-openapi?view=aspnetcore-10.0",
        "s1f9d4c5e975c": "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/using-openapi-documents?view=aspnetcore-10.0",
        "sc41b77cc06c8": "https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/health-checks?view=aspnetcore-10.0",
        "se101626c29d6": "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/kestrel/host-filtering?view=aspnetcore-10.0"
      }
    },
    "source": {
      "name": "ASP.NET Core source",
      "basis": "v10.0.0",
      "sources": {
        "sb62cff70e3b8": "https://raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/Middleware/HttpsPolicy/src/HstsOptions.cs",
        "sfc86e3f62243": "https://raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/Middleware/HttpOverrides/src/ForwardedHeadersOptions.cs",
        "s903da00d32b5": "https://raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/Servers/Kestrel/Core/src/KestrelServerLimits.cs",
        "sc00d8d67e93b": "https://raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/Servers/Kestrel/Core/src/Http2Limits.cs",
        "s67f347ba7947": "https://raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/Http/Http/src/Features/FormOptions.cs",
        "s18c44d6c2fb7": "https://raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/Servers/Kestrel/Core/src/KestrelServerOptions.cs"
      }
    },
    "proxy-fix": {
      "name": "ASP.NET Core proxy hardening",
      "basis": "8.0.17",
      "sources": {
        "s2864662bcd21": "https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/8/forwarded-headers-unknown-proxies?view=aspnetcore-10.0"
      }
    },
    "runtime": {
      "name": "NET runtime source",
      "basis": "v10.0.0",
      "sources": {
        "s29ee940c94b9": "https://raw.githubusercontent.com/dotnet/runtime/v10.0.0/src/native/libs/System.Security.Cryptography.Native/pal_x509_root.c"
      }
    },
    "openssl": {
      "name": "OpenSSL documentation",
      "basis": "3.0",
      "sources": {
        "scac6dada5f6a": "https://docs.openssl.org/3.0/man3/SSL_CTX_load_verify_locations/"
      }
    },
    "precedence": {
      "name": "WebApplicationBuilder precedence",
      "basis": ".NET 7",
      "sources": {
        "s10d46bc97fef": "https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/7/environment-variable-precedence?view=aspnetcore-10.0"
      }
    },
    "iis": {
      "name": "IIS documentation",
      "basis": "IIS 10",
      "sources": {
        "sb2eac755b583": "https://learn.microsoft.com/en-us/iis/configuration/system.webserver/security/requestfiltering/"
      }
    },
    "iis-rolling": {
      "name": "IIS documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s267eddd43502": "https://learn.microsoft.com/en-us/iis/configuration/system.webserver/httpprotocol/customheaders/"
      }
    },
    "dotnet-rolling": {
      "name": ".NET documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s640872a17a8a": "https://learn.microsoft.com/en-us/dotnet/standard/security/cross-platform-cryptography"
      }
    }
  },
  "claims": {
    "tls": {"text": "Kestrel serves wildcard HTTP 80 and HTTPS 443 with PKCS12 or PEM Path/KeyPath; supply certificate passwords from environment or a secret store.", "components": ["docs", "net10"], "sources": ["docs:s74dcd6a72d63", "net10:s74dcd6a72d63"], "status": "REASONED"},
    "tls-protocols": {"text": "Default SslProtocols.None delegates to the OS; example explicitly permits only TLS 1.2 and 1.3.", "components": ["net10"], "sources": ["net10:s74dcd6a72d63"], "status": "REASONED"},
    "hsts-age": {"text": "NET 10 HSTS defaults to 30 days; example selects 365 days outside Development.", "components": ["source"], "sources": ["source:sb62cff70e3b8"], "status": "REASONED"},
    "hsts-subdomains": {"text": "HSTS IncludeSubDomains defaults false; example enables it only when all affected subdomains support HTTPS.", "components": ["source"], "sources": ["source:sb62cff70e3b8"], "status": "REASONED"},
    "hsts-preload": {"text": "HSTS Preload defaults false.", "components": ["source"], "sources": ["source:sb62cff70e3b8"], "status": "REASONED"},
    "redirect": {"text": "UseHttpsRedirection needs an HTTPS port via ASPNETCORE_HTTPS_PORT=443 or HttpsPort.", "components": ["docs"], "sources": ["docs:s8c762260991c"], "status": "REASONED"},
    "proxy-bind": {"text": "ListenLocalhost(5000), or localhost:5000 URLs, binds behind a same-host proxy; process forwarded headers first.", "components": ["docs", "net10"], "sources": ["docs:s74dcd6a72d63", "net10:s5701d26de241"], "status": "REASONED"},
    "proxy-default": {"text": "NET 10 trusts ::1 and 127.0.0.0/8 by default; adding 127.0.0.1 does not narrow that list.", "components": ["net10", "source"], "sources": ["net10:s5701d26de241", "source:sfc86e3f62243"], "status": "REASONED"},
    "proxy-networks": {"text": "NET 10 replaces obsolete KnownNetworks with KnownIPNetworks/System.Net.IPNetwork; narrow both lists together and never leave both empty.", "components": ["net10", "source"], "sources": ["net10:s5701d26de241", "source:sfc86e3f62243"], "status": "REASONED"},
    "proxy-hardening": {"text": "Unknown-proxy headers are ignored in 8.0.17 and 9.0.6 and NET 10, even without X-Forwarded-For processing; register the real proxy.", "components": ["net10", "proxy-fix"], "sources": ["net10:s5701d26de241", "proxy-fix:s2864662bcd21"], "status": "REASONED"},
    "proxy-https": {"text": "When the proxy handles redirects/HSTS, omit the app middleware; missing forwarded-header handling can cause redirect loops.", "components": ["docs"], "sources": ["docs:s8c762260991c", "docs:s5701d26de241"], "status": "REASONED"},
    "password": {"text": "Identity uses PBKDF2 with default 100000 iterations; keep its password hasher.", "components": ["docs"], "sources": ["docs:s3790c49f70b9", "docs:s9d10c561bb48"], "status": "REASONED"},
    "lockout": {"text": "Configure five failures, five-minute lockout and allowance for new users; PasswordSignInAsync must use lockoutOnFailure=true, while the template uses false.", "components": ["net10"], "sources": ["net10:s0d7c367ac06f"], "status": "REASONED"},
    "cookies": {"text": "Configure HttpOnly, SecurePolicy.Always, SameSite=Lax and eight-hour expiry; cookie-only auth uses the same options.", "components": ["docs", "net10"], "sources": ["docs:sa3c22a38f4cb", "docs:sb6780977fa3f", "net10:s0d7c367ac06f"], "status": "REASONED"},
    "samesite": {"text": "NET 10 auth cookie defaults Lax; Strict can suppress cross-site app cookies without universally breaking OAuth/OIDC callbacks.", "components": ["net10"], "sources": ["net10:sc0654e58fc4c"], "status": "REASONED"},
    "remote-cookies": {"text": "Correlation and OIDC nonce cookies separately default None; preserve secure cross-site settings and avoid global rewriting.", "components": ["net10"], "sources": ["net10:sc0654e58fc4c"], "status": "REASONED"},
    "authorization": {"text": "Run authentication before authorization and Map calls; use an authenticated fallback policy and explicitly AllowAnonymous on public pages.", "components": ["docs"], "sources": ["docs:sa3c22a38f4cb"], "status": "REASONED"},
    "login-limit": {"text": "NET 7+ built-in rate limiting: login policy permits 20 per 15 minutes, no queue, 429 rejection; endpoint policies need UseRateLimiter after routing.", "components": ["rate-min"], "sources": ["rate-min:sd3fef8f45066"], "status": "REASONED"},
    "oidc": {"text": "Configure OpenIdConnect code flow with cookie DefaultScheme and OIDC DefaultChallengeScheme; keep client secrets outside appsettings.json.", "components": ["docs"], "sources": ["docs:s592dc85bb71f"], "status": "REASONED"},
    "mfa": {"text": "Enforce MFA at the provider or fronting identity layer per linked guides; provider MFA configuration lacks a direct listed source.", "components": ["docs"], "sources": ["docs:s592dc85bb71f", "docs:s2d5a930aac35"], "status": "REASONED"},
    "client-validation": {"text": "Never accept every certificate through DangerousAcceptAnyServerCertificateValidator or an always-true callback.", "components": ["docs"], "sources": ["docs:s6afc0255098f"], "status": "REASONED"},
    "client-ca": {"text": "On Linux NET 10 install internal roots or use SSL_CERT_FILE for a PEM file and SSL_CERT_DIR for a certificate directory; preserve needed public roots.", "components": ["runtime", "openssl", "dotnet-rolling"], "sources": ["dotnet-rolling:s640872a17a8a", "runtime:s29ee940c94b9", "openssl:scac6dada5f6a"], "status": "REASONED"},
    "developer-errors": {"text": "Development automatically enables the Developer Exception Page; production must exclude it and check the effective environment.", "components": ["net10"], "sources": ["net10:s2f7e6a8213f1", "net10:s61afb89034f8"], "status": "REASONED"},
    "error-handler": {"text": "Install UseExceptionHandler early after forwarding; provide a generic /Error route supporting failed methods/anonymous requests and preserve intentional 413 responses.", "components": ["net10"], "sources": ["net10:s2f7e6a8213f1"], "status": "REASONED"},
    "environment": {"text": "Production is default absent overrides; NET 7+ WebApplicationBuilder prioritizes command-line/DOTNET_ over ASPNETCORE_, while older WebHost differs.", "components": ["net10", "precedence"], "sources": ["net10:s61afb89034f8", "precedence:s10d46bc97fef"], "status": "REASONED"},
    "database-diagnostics": {"text": "Register database developer exception filters before Build and migrations middleware after Build only in Development; migrations execute database changes.", "components": ["net10"], "sources": ["net10:s2f7e6a8213f1", "net10:s9d290374f4e8"], "status": "REASONED"},
    "body-limit": {"text": "NET 10 Kestrel total body default is 30000000 bytes, null unlimited; example lowers it to 1048576 bytes.", "components": ["net10", "source"], "sources": ["net10:s1ce47370d948", "source:s903da00d32b5"], "status": "REASONED"},
    "body-override": {"text": "RequestSizeLimit overrides before body reading; DisableRequestSizeLimit removes the protection.", "components": ["net10"], "sources": ["net10:s1ce47370d948", "net10:s55f298bf0048"], "status": "REASONED"},
    "multipart": {"text": "MultipartBodyLengthLimit defaults 134217728 bytes per parsed section; example uses 1048576. Framing consumes total allowance and parsing failure need not return 413.", "components": ["source", "net10"], "sources": ["source:s67f347ba7947", "net10:s792d3e8f3e42"], "status": "REASONED"},
    "iis-body": {"text": "In-process IISServerOptions body default is 30000000, separately from IIS maxAllowedContentLength default 30000000; out-of-process IIS disables Kestrel body limiting.", "components": ["net10"], "sources": ["net10:s1ce47370d948", "net10:s792d3e8f3e42", "net10:s529a3d7cce08"], "status": "REASONED"},
    "keepalive": {"text": "Kestrel KeepAliveTimeout defaults to 130 seconds; it is not a total execution deadline.", "components": ["net10", "source"], "sources": ["net10:s1ce47370d948", "source:s903da00d32b5"], "status": "REASONED"},
    "header-timeout": {"text": "Kestrel RequestHeadersTimeout defaults to 30 seconds; it is not a total execution deadline.", "components": ["net10", "source"], "sources": ["net10:s1ce47370d948", "source:s903da00d32b5"], "status": "REASONED"},
    "connections": {"text": "MaxConcurrentConnections defaults null/unlimited; example caps ordinary connections at 100.", "components": ["source"], "sources": ["source:s903da00d32b5"], "status": "REASONED"},
    "upgraded": {"text": "Upgraded connections leave the ordinary count; MaxConcurrentUpgradedConnections separately defaults null.", "components": ["net10", "source"], "sources": ["net10:s1ce47370d948", "source:s903da00d32b5"], "status": "REASONED"},
    "header-count": {"text": "Kestrel MaxRequestHeaderCount defaults 100.", "components": ["source"], "sources": ["source:s903da00d32b5"], "status": "REASONED"},
    "header-size": {"text": "Kestrel MaxRequestHeadersTotalSize defaults 32768 bytes.", "components": ["source"], "sources": ["source:s903da00d32b5"], "status": "REASONED"},
    "request-rate": {"text": "MinRequestBodyDataRate defaults 240 bytes/second with five-second grace.", "components": ["source"], "sources": ["source:s903da00d32b5"], "status": "REASONED"},
    "response-rate": {"text": "MinResponseDataRate defaults 240 bytes/second with five-second grace.", "components": ["source"], "sources": ["source:s903da00d32b5"], "status": "REASONED"},
    "rate-scope": {"text": "HTTP/2 per-request rate adjustments differ from HTTP/1.x; several timeout/rate checks are disabled under a debugger.", "components": ["net10"], "sources": ["net10:s1ce47370d948"], "status": "REASONED"},
    "h2-streams": {"text": "NET 10 HTTP/2 MaxStreamsPerConnection defaults 100.", "components": ["source"], "sources": ["source:sc00d8d67e93b"], "status": "REASONED"},
    "h2-table": {"text": "NET 10 HTTP/2 HeaderTableSize defaults 4096 bytes.", "components": ["source"], "sources": ["source:sc00d8d67e93b"], "status": "REASONED"},
    "h2-frame": {"text": "NET 10 HTTP/2 MaxFrameSize defaults 16384 bytes.", "components": ["source"], "sources": ["source:sc00d8d67e93b"], "status": "REASONED"},
    "h2-header": {"text": "NET 10 HTTP/2 MaxRequestHeaderFieldSize defaults 32768 bytes, not the older 8192.", "components": ["source"], "sources": ["source:sc00d8d67e93b"], "status": "REASONED"},
    "h2-connection-window": {"text": "NET 10 HTTP/2 InitialConnectionWindowSize defaults 1048576 bytes, not the older 131072.", "components": ["source"], "sources": ["source:sc00d8d67e93b"], "status": "REASONED"},
    "h2-stream-window": {"text": "NET 10 HTTP/2 InitialStreamWindowSize defaults 786432 bytes, not the older 98304.", "components": ["source"], "sources": ["source:sc00d8d67e93b"], "status": "REASONED"},
    "h2-ping-delay": {"text": "NET 10 HTTP/2 KeepAlivePingDelay defaults TimeSpan.MaxValue, disabling pings.", "components": ["source"], "sources": ["source:sc00d8d67e93b"], "status": "REASONED"},
    "h2-ping-timeout": {"text": "NET 10 HTTP/2 KeepAlivePingTimeout defaults 20 seconds.", "components": ["source"], "sources": ["source:sc00d8d67e93b"], "status": "REASONED"},
    "h2-scope": {"text": "Flow-control windows bound outstanding buffered data, not total bodies; Http2Limits do not configure HTTP/3.", "components": ["net10", "source"], "sources": ["net10:s1ce47370d948", "source:sc00d8d67e93b"], "status": "REASONED"},
    "key-defaults": {"text": "Data Protection key persistence depends on hosting: user profiles, IIS or Azure may persist; process-only fallback and disposable container layers can lose keys.", "components": ["net10"], "sources": ["net10:s66f1ab4555d6"], "status": "REASONED"},
    "key-persistence": {"text": "Persist keys durably with restricted permissions; replicas share repository, application name and decryption certificates, not merely identical directory names.", "components": ["net10"], "sources": ["net10:s6682926c8da7", "net10:sd635cefc0a9f"], "status": "REASONED"},
    "key-encryption": {"text": "Choosing an explicit repository disables automatic at-rest encryption; configure ProtectKeysWithCertificate and retain needed keys/certificates.", "components": ["net10"], "sources": ["net10:s6682926c8da7", "net10:sd635cefc0a9f"], "status": "REASONED"},
    "key-isolation": {"text": "Separate repositories, permissions and certificate private keys for untrusted apps; SetApplicationName is not isolation from another holder of master keys.", "components": ["net10"], "sources": ["net10:s6682926c8da7"], "status": "REASONED"},
    "cookie-sharing": {"text": "Cookie continuity also needs compatible cookie names, schemes, stores and identity-validation configuration.", "components": ["net10"], "sources": ["net10:s9463626a3d0e"], "status": "REASONED"},
    "server-header": {"text": "NET 10 AddServerHeader defaults true; set false and check all hosting layers since header removal does not control access.", "components": ["source"], "sources": ["source:s18c44d6c2fb7"], "status": "REASONED"},
    "iis-headers": {"text": "Remove IIS X-Powered-By and set removeServerHeader; the latter requires IIS 10 with Windows Server/Windows 10 version 1709 or later.", "components": ["iis", "iis-rolling"], "sources": ["iis-rolling:s267eddd43502", "iis:sb2eac755b583"], "status": "REASONED"},
    "openapi": {"text": "NET 10 built-in OpenAPI requires AddOpenApi before Build; map only in Development or RequireAuthorization with an appropriate policy.", "components": ["net10"], "sources": ["net10:s1d58219cedec"], "status": "REASONED"},
    "swagger": {"text": "Built-in OpenAPI has no Swagger UI; keep separately added UseSwaggerUI in Development or protect it separately from the document.", "components": ["net10"], "sources": ["net10:s1f9d4c5e975c"], "status": "REASONED"},
    "health": {"text": "Register health checks and authorize /healthz; monitoring must authenticate or use a deliberately controlled minimal liveness route.", "components": ["net10"], "sources": ["net10:sc41b77cc06c8"], "status": "REASONED"},
    "health-host": {"text": "RequireHost checks a spoofable Host header and is not a network or authentication boundary.", "components": ["net10"], "sources": ["net10:sc41b77cc06c8"], "status": "REASONED"},
    "host-filter": {"text": "AllowedHosts uses semicolon-separated names without ports; wildcard permits all. It neither authenticates nor binds interfaces; forwarded-host allowlisting is separate.", "components": ["net10"], "sources": ["net10:s5701d26de241", "net10:se101626c29d6"], "status": "REASONED"},
    "verify-redirect": {"text": "HTTP should return 307/308 with HTTPS Location.", "components": ["docs"], "sources": ["docs:s8c762260991c"], "status": "REASONED", "verify": [1]},
    "verify-tls": {"text": "HTTPS must validate without -k and show HSTS.", "components": ["docs", "net10"], "sources": ["docs:s8c762260991c", "net10:s74dcd6a72d63"], "status": "REASONED", "verify": [1]},
    "verify-api": {"text": "Known protected NET 10 cookie API endpoints return 401 anonymous and 403 forbidden; pages/OIDC/custom handlers may redirect. Confirm authorized success first.", "components": ["net10"], "sources": ["net10:s837df4b1657f"], "status": "REASONED", "verify": [1]},
    "verify-bind": {"text": "Inspect every listener for 127.0.0.1 and ::1 behind the proxy.", "components": ["docs", "net10"], "sources": ["docs:s74dcd6a72d63", "net10:s74dcd6a72d63"], "status": "REASONED", "verify": [1]},
    "verify-errors": {"text": "Controlled exception should expose marker/detail under development and generic 500 under production; inspect plain/HTML bodies and correlate handler execution.", "components": ["net10"], "sources": ["net10:s2f7e6a8213f1"], "status": "REASONED", "verify": [2]},
    "verify-body": {"text": "Body-consuming test route returns 204 at 1048576 bytes, 413 at 1048577; raised limit permits both. Isolate other limits and distinguish upstream rejection.", "components": ["net10"], "sources": ["net10:s1ce47370d948"], "status": "REASONED", "verify": [3]},
    "verify-aux": {"text": "Probe actual diagnostic/OpenAPI/UI/health routes anonymously, then authorized; Development-only routes should be absent and retained routes protected. Status alone does not prove authorization.", "components": ["net10"], "sources": ["net10:s1d58219cedec", "net10:s1f9d4c5e975c", "net10:sc41b77cc06c8"], "status": "REASONED", "verify": [4]},
    "verify-migrations": {"text": "GET cannot prove migrations middleware absent; inspect registration and test actual behavior only in isolated database infrastructure.", "components": ["net10"], "sources": ["net10:s9d290374f4e8"], "status": "REASONED"},
    "verify-headers": {"text": "Inspect public success, redirect and error responses for absent Server/X-Powered-By after hosting-layer removal where supported.", "components": ["source", "iis", "iis-rolling"], "sources": ["source:s18c44d6c2fb7", "iis-rolling:s267eddd43502", "iis:sb2eac755b583"], "status": "REASONED", "verify": [5]},
    "verify-cookie": {"text": "Anonymous cookie API control returns 401; original cookie keeps the same identity with 200 before/after restart and across confirmed replicas, before expiry and without identity changes.", "components": ["net10"], "sources": ["net10:s837df4b1657f", "net10:s66f1ab4555d6", "net10:s9463626a3d0e"], "status": "REASONED", "verify": [6]},
    "verify-antiforgery": {"text": "Retain an antiforgery token and cookie across restart and submit without replacement; key loss can invalidate it independently of login recovery.", "components": ["net10"], "sources": ["net10:s6682926c8da7", "net10:s66f1ab4555d6"], "status": "REASONED"}
  }
}
---
# ASP.NET Core and Kestrel: TLS and authentication

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-05; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| tls: Kestrel serves wildcard HTTP 80 and HTTPS 443 with PKCS12 or PEM Path/KeyPath; supply certificate passwords from environment or a secret store. | ASP.NET Core documentation .NET 10; ASP.NET Core .NET 10 | REASONED |
| tls-protocols: Default SslProtocols.None delegates to the OS; example explicitly permits only TLS 1.2 and 1.3. | ASP.NET Core .NET 10 | REASONED |
| hsts-age: NET 10 HSTS defaults to 30 days; example selects 365 days outside Development. | ASP.NET Core source v10.0.0 | REASONED |
| hsts-subdomains: HSTS IncludeSubDomains defaults false; example enables it only when all affected subdomains support HTTPS. | ASP.NET Core source v10.0.0 | REASONED |
| hsts-preload: HSTS Preload defaults false. | ASP.NET Core source v10.0.0 | REASONED |
| redirect: UseHttpsRedirection needs an HTTPS port via ASPNETCORE_HTTPS_PORT=443 or HttpsPort. | ASP.NET Core documentation .NET 10 | REASONED |
| proxy-bind: ListenLocalhost(5000), or localhost:5000 URLs, binds behind a same-host proxy; process forwarded headers first. | ASP.NET Core documentation .NET 10; ASP.NET Core .NET 10 | REASONED |
| proxy-default: NET 10 trusts ::1 and 127.0.0.0/8 by default; adding 127.0.0.1 does not narrow that list. | ASP.NET Core .NET 10; ASP.NET Core source v10.0.0 | REASONED |
| proxy-networks: NET 10 replaces obsolete KnownNetworks with KnownIPNetworks/System.Net.IPNetwork; narrow both lists together and never leave both empty. | ASP.NET Core .NET 10; ASP.NET Core source v10.0.0 | REASONED |
| proxy-hardening: Unknown-proxy headers are ignored in 8.0.17 and 9.0.6 and NET 10, even without X-Forwarded-For processing; register the real proxy. | ASP.NET Core .NET 10; ASP.NET Core proxy hardening 8.0.17 | REASONED |
| proxy-https: When the proxy handles redirects/HSTS, omit the app middleware; missing forwarded-header handling can cause redirect loops. | ASP.NET Core documentation .NET 10 | REASONED |
| password: Identity uses PBKDF2 with default 100000 iterations; keep its password hasher. | ASP.NET Core documentation .NET 10 | REASONED |
| lockout: Configure five failures, five-minute lockout and allowance for new users; PasswordSignInAsync must use lockoutOnFailure=true, while the template uses false. | ASP.NET Core .NET 10 | REASONED |
| cookies: Configure HttpOnly, SecurePolicy.Always, SameSite=Lax and eight-hour expiry; cookie-only auth uses the same options. | ASP.NET Core documentation .NET 10; ASP.NET Core .NET 10 | REASONED |
| samesite: NET 10 auth cookie defaults Lax; Strict can suppress cross-site app cookies without universally breaking OAuth/OIDC callbacks. | ASP.NET Core .NET 10 | REASONED |
| remote-cookies: Correlation and OIDC nonce cookies separately default None; preserve secure cross-site settings and avoid global rewriting. | ASP.NET Core .NET 10 | REASONED |
| authorization: Run authentication before authorization and Map calls; use an authenticated fallback policy and explicitly AllowAnonymous on public pages. | ASP.NET Core documentation .NET 10 | REASONED |
| login-limit: NET 7+ built-in rate limiting: login policy permits 20 per 15 minutes, no queue, 429 rejection; endpoint policies need UseRateLimiter after routing. | ASP.NET Core rate-limiter minimum .NET 7 | REASONED |
| oidc: Configure OpenIdConnect code flow with cookie DefaultScheme and OIDC DefaultChallengeScheme; keep client secrets outside appsettings.json. | ASP.NET Core documentation .NET 10 | REASONED |
| mfa: Enforce MFA at the provider or fronting identity layer per linked guides; provider MFA configuration lacks a direct listed source. | ASP.NET Core documentation .NET 10 | REASONED |
| client-validation: Never accept every certificate through DangerousAcceptAnyServerCertificateValidator or an always-true callback. | ASP.NET Core documentation .NET 10 | REASONED |
| client-ca: On Linux NET 10 install internal roots or use SSL_CERT_FILE for a PEM file and SSL_CERT_DIR for a certificate directory; preserve needed public roots. | NET runtime source v10.0.0; OpenSSL documentation 3.0; .NET documentation (rolling) unknown | REASONED |
| developer-errors: Development automatically enables the Developer Exception Page; production must exclude it and check the effective environment. | ASP.NET Core .NET 10 | REASONED |
| error-handler: Install UseExceptionHandler early after forwarding; provide a generic /Error route supporting failed methods/anonymous requests and preserve intentional 413 responses. | ASP.NET Core .NET 10 | REASONED |
| environment: Production is default absent overrides; NET 7+ WebApplicationBuilder prioritizes command-line/DOTNET_ over ASPNETCORE_, while older WebHost differs. | ASP.NET Core .NET 10; WebApplicationBuilder precedence .NET 7 | REASONED |
| database-diagnostics: Register database developer exception filters before Build and migrations middleware after Build only in Development; migrations execute database changes. | ASP.NET Core .NET 10 | REASONED |
| body-limit: NET 10 Kestrel total body default is 30000000 bytes, null unlimited; example lowers it to 1048576 bytes. | ASP.NET Core .NET 10; ASP.NET Core source v10.0.0 | REASONED |
| body-override: RequestSizeLimit overrides before body reading; DisableRequestSizeLimit removes the protection. | ASP.NET Core .NET 10 | REASONED |
| multipart: MultipartBodyLengthLimit defaults 134217728 bytes per parsed section; example uses 1048576. Framing consumes total allowance and parsing failure need not return 413. | ASP.NET Core source v10.0.0; ASP.NET Core .NET 10 | REASONED |
| iis-body: In-process IISServerOptions body default is 30000000, separately from IIS maxAllowedContentLength default 30000000; out-of-process IIS disables Kestrel body limiting. | ASP.NET Core .NET 10 | REASONED |
| keepalive: Kestrel KeepAliveTimeout defaults to 130 seconds; it is not a total execution deadline. | ASP.NET Core .NET 10; ASP.NET Core source v10.0.0 | REASONED |
| header-timeout: Kestrel RequestHeadersTimeout defaults to 30 seconds; it is not a total execution deadline. | ASP.NET Core .NET 10; ASP.NET Core source v10.0.0 | REASONED |
| connections: MaxConcurrentConnections defaults null/unlimited; example caps ordinary connections at 100. | ASP.NET Core source v10.0.0 | REASONED |
| upgraded: Upgraded connections leave the ordinary count; MaxConcurrentUpgradedConnections separately defaults null. | ASP.NET Core .NET 10; ASP.NET Core source v10.0.0 | REASONED |
| header-count: Kestrel MaxRequestHeaderCount defaults 100. | ASP.NET Core source v10.0.0 | REASONED |
| header-size: Kestrel MaxRequestHeadersTotalSize defaults 32768 bytes. | ASP.NET Core source v10.0.0 | REASONED |
| request-rate: MinRequestBodyDataRate defaults 240 bytes/second with five-second grace. | ASP.NET Core source v10.0.0 | REASONED |
| response-rate: MinResponseDataRate defaults 240 bytes/second with five-second grace. | ASP.NET Core source v10.0.0 | REASONED |
| rate-scope: HTTP/2 per-request rate adjustments differ from HTTP/1.x; several timeout/rate checks are disabled under a debugger. | ASP.NET Core .NET 10 | REASONED |
| h2-streams: NET 10 HTTP/2 MaxStreamsPerConnection defaults 100. | ASP.NET Core source v10.0.0 | REASONED |
| h2-table: NET 10 HTTP/2 HeaderTableSize defaults 4096 bytes. | ASP.NET Core source v10.0.0 | REASONED |
| h2-frame: NET 10 HTTP/2 MaxFrameSize defaults 16384 bytes. | ASP.NET Core source v10.0.0 | REASONED |
| h2-header: NET 10 HTTP/2 MaxRequestHeaderFieldSize defaults 32768 bytes, not the older 8192. | ASP.NET Core source v10.0.0 | REASONED |
| h2-connection-window: NET 10 HTTP/2 InitialConnectionWindowSize defaults 1048576 bytes, not the older 131072. | ASP.NET Core source v10.0.0 | REASONED |
| h2-stream-window: NET 10 HTTP/2 InitialStreamWindowSize defaults 786432 bytes, not the older 98304. | ASP.NET Core source v10.0.0 | REASONED |
| h2-ping-delay: NET 10 HTTP/2 KeepAlivePingDelay defaults TimeSpan.MaxValue, disabling pings. | ASP.NET Core source v10.0.0 | REASONED |
| h2-ping-timeout: NET 10 HTTP/2 KeepAlivePingTimeout defaults 20 seconds. | ASP.NET Core source v10.0.0 | REASONED |
| h2-scope: Flow-control windows bound outstanding buffered data, not total bodies; Http2Limits do not configure HTTP/3. | ASP.NET Core .NET 10; ASP.NET Core source v10.0.0 | REASONED |
| key-defaults: Data Protection key persistence depends on hosting: user profiles, IIS or Azure may persist; process-only fallback and disposable container layers can lose keys. | ASP.NET Core .NET 10 | REASONED |
| key-persistence: Persist keys durably with restricted permissions; replicas share repository, application name and decryption certificates, not merely identical directory names. | ASP.NET Core .NET 10 | REASONED |
| key-encryption: Choosing an explicit repository disables automatic at-rest encryption; configure ProtectKeysWithCertificate and retain needed keys/certificates. | ASP.NET Core .NET 10 | REASONED |
| key-isolation: Separate repositories, permissions and certificate private keys for untrusted apps; SetApplicationName is not isolation from another holder of master keys. | ASP.NET Core .NET 10 | REASONED |
| cookie-sharing: Cookie continuity also needs compatible cookie names, schemes, stores and identity-validation configuration. | ASP.NET Core .NET 10 | REASONED |
| server-header: NET 10 AddServerHeader defaults true; set false and check all hosting layers since header removal does not control access. | ASP.NET Core source v10.0.0 | REASONED |
| iis-headers: Remove IIS X-Powered-By and set removeServerHeader; the latter requires IIS 10 with Windows Server/Windows 10 version 1709 or later. | IIS documentation IIS 10; IIS documentation (rolling) unknown | REASONED |
| openapi: NET 10 built-in OpenAPI requires AddOpenApi before Build; map only in Development or RequireAuthorization with an appropriate policy. | ASP.NET Core .NET 10 | REASONED |
| swagger: Built-in OpenAPI has no Swagger UI; keep separately added UseSwaggerUI in Development or protect it separately from the document. | ASP.NET Core .NET 10 | REASONED |
| health: Register health checks and authorize /healthz; monitoring must authenticate or use a deliberately controlled minimal liveness route. | ASP.NET Core .NET 10 | REASONED |
| health-host: RequireHost checks a spoofable Host header and is not a network or authentication boundary. | ASP.NET Core .NET 10 | REASONED |
| host-filter: AllowedHosts uses semicolon-separated names without ports; wildcard permits all. It neither authenticates nor binds interfaces; forwarded-host allowlisting is separate. | ASP.NET Core .NET 10 | REASONED |
| verify-redirect: HTTP should return 307/308 with HTTPS Location. | ASP.NET Core documentation .NET 10 | REASONED |
| verify-tls: HTTPS must validate without -k and show HSTS. | ASP.NET Core documentation .NET 10; ASP.NET Core .NET 10 | REASONED |
| verify-api: Known protected NET 10 cookie API endpoints return 401 anonymous and 403 forbidden; pages/OIDC/custom handlers may redirect. Confirm authorized success first. | ASP.NET Core .NET 10 | REASONED |
| verify-bind: Inspect every listener for 127.0.0.1 and ::1 behind the proxy. | ASP.NET Core documentation .NET 10; ASP.NET Core .NET 10 | REASONED |
| verify-errors: Controlled exception should expose marker/detail under development and generic 500 under production; inspect plain/HTML bodies and correlate handler execution. | ASP.NET Core .NET 10 | REASONED |
| verify-body: Body-consuming test route returns 204 at 1048576 bytes, 413 at 1048577; raised limit permits both. Isolate other limits and distinguish upstream rejection. | ASP.NET Core .NET 10 | REASONED |
| verify-aux: Probe actual diagnostic/OpenAPI/UI/health routes anonymously, then authorized; Development-only routes should be absent and retained routes protected. Status alone does not prove authorization. | ASP.NET Core .NET 10 | REASONED |
| verify-migrations: GET cannot prove migrations middleware absent; inspect registration and test actual behavior only in isolated database infrastructure. | ASP.NET Core .NET 10 | REASONED |
| verify-headers: Inspect public success, redirect and error responses for absent Server/X-Powered-By after hosting-layer removal where supported. | ASP.NET Core source v10.0.0; IIS documentation IIS 10; IIS documentation (rolling) unknown | REASONED |
| verify-cookie: Anonymous cookie API control returns 401; original cookie keeps the same identity with 200 before/after restart and across confirmed replicas, before expiry and without identity changes. | ASP.NET Core .NET 10 | REASONED |
| verify-antiforgery: Retain an antiforgery token and cookie across restart and submit without replacement; key loss can invalidate it independently of login recovery. | ASP.NET Core .NET 10 | REASONED |
<!-- version-basis:end -->

Preferred production layout: bind Kestrel to loopback and terminate TLS in a reverse proxy ([caddy.md](caddy.md), [nginx.md](nginx.md)) or behind [cloudflare.md](cloudflare.md). Kestrel can also terminate TLS itself, shown below. Certificates: [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md).

## 1. HTTPS directly in Kestrel

`appsettings.json` with a PKCS12 file (for PEM files, `Path` is the certificate and `KeyPath` the private key; the docs warn against a plaintext `Password` here, so supply it from the environment or a secret store):

```json
{ "Kestrel": { "Endpoints": {
    "Http":  { "Url": "http://*:80" },
    "Https": { "Url": "https://*:443",
               "Certificate": { "Path": "/etc/ssl/private/server.pfx", "Password": "REPLACE_WITH_LONG_RANDOM_VALUE" } }
} } }
```

```csharp
builder.WebHost.ConfigureKestrel(serverOptions =>
    serverOptions.ConfigureHttpsDefaults(listenOptions =>
        listenOptions.SslProtocols = SslProtocols.Tls12 | SslProtocols.Tls13));   // default SslProtocols.None = OS defaults
builder.Services.AddHsts(options => { options.MaxAge = TimeSpan.FromDays(365); options.IncludeSubDomains = true; });
if (!app.Environment.IsDevelopment()) { app.UseHsts(); }   // browsers cache HSTS; keep it out of development
app.UseHttpsRedirection();                                  // needs the HTTPS port: ASPNETCORE_HTTPS_PORT=443 or options.HttpsPort
```

Version scope: ASP.NET Core on .NET 10 LTS. Kestrel's default `SslProtocols.None` delegates protocol selection to the operating system; it does not disable TLS. The explicit `Tls12 | Tls13` above intentionally restricts the permitted versions. In .NET 10, `HstsOptions` defaults to a 30-day `MaxAge`, `IncludeSubDomains = false`, and `Preload = false`. This guide intentionally chooses 365 days and subdomain coverage; enable that coverage only when every affected subdomain supports HTTPS.

## 2. Behind a proxy

```csharp
builder.WebHost.ConfigureKestrel(o => o.ListenLocalhost(5000));   // or ASPNETCORE_URLS=http://localhost:5000
builder.Services.Configure<ForwardedHeadersOptions>(o => {
    o.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto;
    o.KnownProxies.Add(IPAddress.Parse("127.0.0.1")); });   // adds to the default loopback trust entries
app.UseForwardedHeaders();   // first in the pipeline
```

In .NET 10, forwarded-header trust already includes IPv6 loopback `::1` and the IPv4 loopback network `127.0.0.0/8`; adding `127.0.0.1` does not make it the sole trusted address. `KnownNetworks` is obsolete in .NET 10: use `KnownIPNetworks`, whose entries are `System.Net.IPNetwork`, for trusted network ranges. If the deployment needs a narrower trust list, clear the default entries and populate the actual proxy addresses or networks together; never leave both lists empty, which permits any proxy.

The unknown-proxy hardening introduced in ASP.NET Core 8.0.17 and 9.0.6 also applies in .NET 10: forwarded headers from unknown proxies are ignored, including when `X-Forwarded-For` processing is not enabled. Register the real proxy rather than disabling these checks.

When the proxy already redirects to HTTPS and sends HSTS, leave `UseHttpsRedirection` and `UseHsts` out of the app; per the docs, redirect middleware behind a proxy without forwarded headers loops. Set the remaining security headers at the proxy per [headers.md](headers.md).

## 3. Authentication

Follow [authentication.md](authentication.md). ASP.NET Core Identity hashes passwords with PBKDF2 (`PasswordHasherOptions.IterationCount`, default 100,000); keep its hasher rather than writing one. Lockout and cookie settings:

```csharp
builder.Services.AddDefaultIdentity<IdentityUser>(options => {
    options.Lockout.MaxFailedAccessAttempts = 5;
    options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(5);
    options.Lockout.AllowedForNewUsers = true; }).AddEntityFrameworkStores<ApplicationDbContext>();
builder.Services.ConfigureApplicationCookie(options => {
    options.Cookie.HttpOnly = true;
    options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
    options.Cookie.SameSite = SameSiteMode.Lax;   // app cookie; test cross-site sign-in flows before choosing Strict
    options.ExpireTimeSpan = TimeSpan.FromHours(8); });
```

In .NET 10, the authentication cookie defaults to `SameSite=Lax`. Choosing `Strict` can prevent an existing app cookie from accompanying a cross-site request, but it does not universally break OAuth2 or OIDC callbacks. Remote authentication correlation cookies and OIDC nonce cookies are separate cookies that default to `SameSite=None`; retain their secure cross-site settings and avoid a global cookie policy that rewrites them to `Lax` or `Strict`.

Lockout counts a failure only when the sign-in call asks for it: pass `lockoutOnFailure: true` to `_signInManager.PasswordSignInAsync(email, password, rememberMe, lockoutOnFailure: true)`. The template passes `false`, so password failures through that call do not count toward lockout.

Without Identity, the same `Cookie.*` options go on `AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme).AddCookie(options => ...)`; call `app.UseAuthentication()` then `app.UseAuthorization()` before the `Map*` calls. Deny by default with `AddAuthorizationBuilder().SetFallbackPolicy(new AuthorizationPolicyBuilder().RequireAuthenticatedUser().Build())` and mark public pages `[AllowAnonymous]`.

Rate-limit the login route with the built-in middleware (`Microsoft.AspNetCore.RateLimiting`, .NET 7 and later):

```csharp
builder.Services.AddRateLimiter(options => {
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    options.AddFixedWindowLimiter("login", o => { o.PermitLimit = 20; o.Window = TimeSpan.FromMinutes(15); o.QueueLimit = 0; }); });
app.UseRateLimiter();   // after UseRouting when policies are per endpoint
app.MapPost("/login", LoginHandler).RequireRateLimiting("login");
```

SSO: the `Microsoft.AspNetCore.Authentication.OpenIdConnect` package adds `.AddOpenIdConnect(options => { options.Authority = ...; options.ClientId = ...; options.ClientSecret = ...; options.ResponseType = OpenIdConnectResponseType.Code; })` next to `.AddCookie()`, with the cookie as `DefaultScheme` and OIDC as `DefaultChallengeScheme`; keep the secret out of `appsettings.json`. Validation and allowlist checks are in [oidc-integration.md](oidc-integration.md), providers in [identity-providers.md](identity-providers.md). MFA: enforce it at the identity provider, or front the app per [mfa.md](mfa.md).

## 4. Client-side TLS discipline

- Never assign `HttpClientHandler.DangerousAcceptAnyServerCertificateValidator` or a `ServerCertificateCustomValidationCallback` that returns `true`; both accept any certificate for every request through that handler.
- On Linux with .NET 10, install an internal CA in the distribution's trust store, or configure `SSL_CERT_FILE` to name a PEM certificate file and `SSL_CERT_DIR` to name a directory of certificates. `SSL_CERT_DIR` is not a file path; preserve the public roots the app also needs (see [self-signed.md](self-signed.md)).

## 5. Production errors and diagnostics

The following applies to .NET 10 LTS. Keep the Developer Exception Page out of production: it can disclose stack traces, request details, and other diagnostic information. `WebApplication.CreateBuilder` enables it automatically in Development, so check the effective environment as well as explicit `UseDeveloperExceptionPage` calls.

After creating `app`, install production exception handling early, after forwarded-header handling and before the middleware it must protect:

```csharp
if (!app.Environment.IsDevelopment())
    app.UseExceptionHandler("/Error");
```

Provide the `/Error` handler; it must return a generic error response without exception messages, stack traces, configuration values, or request secrets. Make it accessible when handling failures from anonymous requests, and do not restrict it to GET if other methods can fail. Preserve intentional request-rejection statuses such as `413` in the application's error handling.

Set `ASPNETCORE_ENVIRONMENT=Production` in deployment configuration and check `DOTNET_ENVIRONMENT` too. With default host configuration, Production is the default when neither variable nor another environment override is supplied. Since .NET 7, `WebApplicationBuilder` gives command-line host settings and `DOTNET_` variables precedence over `ASPNETCORE_` variables. Thus `DOTNET_ENVIRONMENT=Development` can override `ASPNETCORE_ENVIRONMENT=Production`. The older `WebHost` hosting model retains different precedence. Confirm the effective environment in startup logs.

For an EF Core application using `Microsoft.AspNetCore.Diagnostics.EntityFrameworkCore`, put the database developer filter registration before `builder.Build()`, inside the Development branch:

```csharp
if (builder.Environment.IsDevelopment())
{
    builder.Services.AddDatabaseDeveloperPageExceptionFilter();
}
```

After building the app, keep the migrations endpoint in the same environment boundary:

```csharp
if (app.Environment.IsDevelopment())
{
    app.UseMigrationsEndPoint();
}
```

Move any existing unconditional calls into these branches. The migrations middleware processes requests to execute migrations; production database changes belong in the deployment process.

## 6. Request and connection budgets

In .NET 10, `KestrelServerLimits.MaxRequestBodySize` defaults to `30_000_000` bytes; `null` removes that limit. Choose a finite budget appropriate to the routes. This example deliberately lowers the total body allowance to 1 MiB and caps ordinary connections at 100; these are example deployment choices, not framework defaults:

```csharp
using Microsoft.AspNetCore.Http.Features;

builder.WebHost.ConfigureKestrel(options =>
{
    options.Limits.MaxRequestBodySize = 1_048_576;
    options.Limits.MaxConcurrentConnections = 100;
});

builder.Services.Configure<FormOptions>(options =>
{
    options.MultipartBodyLengthLimit = 1_048_576;
});
```

For MVC actions, `[RequestSizeLimit(1_048_576)]` sets a per-request body limit. Apply overrides before the body is read. Avoid `[DisableRequestSizeLimit]`, which removes this protection rather than providing an upload-specific budget.

`FormOptions.MultipartBodyLengthLimit` defaults to `134_217_728` bytes in .NET 10 and limits each multipart section body when the form is parsed. It is separate from the server's total request-body limit; multipart framing also consumes the total allowance. A multipart parsing failure is not a guarantee of an HTTP `413` response.

IIS hosting changes which server enforces the body limit. In-process hosting uses `IISServerOptions.MaxRequestBodySize`, default `30_000_000`, rather than Kestrel. IIS request filtering independently applies `maxAllowedContentLength`, also default `30_000_000`, before the application limit. Changing one does not change the other. With out-of-process hosting behind the ASP.NET Core Module, IIS sets the body limit and Kestrel's body-size limit is disabled. Align the applicable IIS, proxy, application, and form limits.

The following are .NET 10 `KestrelServerLimits` defaults, not suggested overrides:

| Property | Default |
| --- | --- |
| `KeepAliveTimeout` | 130 seconds |
| `RequestHeadersTimeout` | 30 seconds |
| `MaxConcurrentConnections` | `null`, unlimited |
| `MaxRequestHeaderCount` | 100 |
| `MaxRequestHeadersTotalSize` | 32,768 bytes |
| `MinRequestBodyDataRate` | 240 bytes/second, 5-second grace period |
| `MinResponseDataRate` | 240 bytes/second, 5-second grace period |

Keep-alive and header timeouts are not total application execution deadlines. Upgraded connections leave the ordinary connection count; budget them separately with `MaxConcurrentUpgradedConnections`, whose default is also `null`. Minimum-rate enforcement has protocol-specific behavior; HTTP/2 does not support the same per-request rate adjustments as HTTP/1.x. Several Kestrel timeout and rate checks are disabled while a debugger is attached, so demonstrate them without one.

For HTTP/2, configure `options.Limits.Http2`. The .NET 10 `Http2Limits` defaults are:

| Property | Default |
| --- | --- |
| `MaxStreamsPerConnection` | 100 |
| `HeaderTableSize` | 4,096 bytes |
| `MaxFrameSize` | 16,384 bytes |
| `MaxRequestHeaderFieldSize` | 32,768 bytes |
| `InitialConnectionWindowSize` | 1,048,576 bytes |
| `InitialStreamWindowSize` | 786,432 bytes |
| `KeepAlivePingDelay` | `TimeSpan.MaxValue`, pings disabled |
| `KeepAlivePingTimeout` | 20 seconds |

The older `8_192`, `131_072`, and `98_304` header-field, connection-window, and stream-window values found in older examples are not .NET 10 defaults. Flow-control windows bound outstanding buffered data, not the total body size. These `Http2Limits` properties do not configure HTTP/3.

## 7. Persistent Data Protection keys

ASP.NET Core Data Protection protects authentication cookies and antiforgery tokens. Losing a key ring can invalidate those values after a restart or when a different replica handles the request; ephemeral storage does not weaken the cryptographic algorithm.

The .NET 10 defaults depend on the hosting environment. Available user-profile storage, IIS, and Azure App Service can provide persistence; process-only keys are a fallback, not the universal default. A container's writable layer can still disappear when the container is replaced.

Before `builder.Build()`, configure a durable key repository. Here, `keyEncryptionCertificate` is an `X509Certificate2` loaded through the deployment's certificate provisioning; its private key must be available to every replica that decrypts the stored keys:

```csharp
using Microsoft.AspNetCore.DataProtection;

builder.Services.AddDataProtection()
    .PersistKeysToFileSystem(new DirectoryInfo("/var/lib/myapp/data-protection"))
    .SetApplicationName("myapp-production")
    .ProtectKeysWithCertificate(keyEncryptionCertificate);
```

Provision that directory with permissions restricted to the application identity and mount durable storage there. Replicas need the same shared key repository, the same application name, and access to the required decryption certificates; identical directory names on separate local disks do not share keys. An external durable key repository is another option.

Explicitly choosing a key repository disables automatic key encryption at rest, so configure protection such as `ProtectKeysWithCertificate` as well as persistence. Retain the keys and decryption certificates needed for still-valid cookies and tokens.

Use separate repositories, access permissions, and certificate private keys for mutually untrusted applications. `SetApplicationName` separates cryptographic purposes, but a different name is not a security boundary against another application with access to the same master keys.

Cookie continuity also requires compatible authentication configuration across replicas, including the cookie name and authentication scheme. Shared keys alone do not reconcile different cookie settings, session stores, or identity-validation behavior.

## 8. Auxiliary exposure

In .NET 10, `KestrelServerOptions.AddServerHeader` defaults to `true`. Disable Kestrel's identifying header:

```csharp
builder.WebHost.ConfigureKestrel(options =>
{
    options.AddServerHeader = false;
});
```

IIS and reverse proxies can add their own headers. For IIS, merge these settings into the existing `web.config`, preserving its other hosting configuration:

```xml
<configuration>
  <system.webServer>
    <httpProtocol>
      <customHeaders>
        <remove name="X-Powered-By" />
      </customHeaders>
    </httpProtocol>
    <security>
      <requestFiltering removeServerHeader="true" />
    </security>
  </system.webServer>
</configuration>
```

`removeServerHeader` is an IIS 10 feature and requires Windows Server version 1709 or Windows 10 version 1709 or later. Check the public response because the fronting server can supply a different header. Header removal reduces disclosure; it does not control access.

For .NET 10 built-in OpenAPI generation, use the `Microsoft.AspNetCore.OpenApi` package and register `builder.Services.AddOpenApi()` before building the app. Keep document mapping in Development unless production access is deliberately authorized:

```csharp
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}
```

If production clients need the document, replace that conditional mapping with an authorized mapping:

```csharp
app.MapOpenApi().RequireAuthorization();
```

This requires the authentication and authorization setup from section 3. Use a dedicated authorization policy when only operators should see the document.

Built-in OpenAPI generation does not include Swagger UI. If the app adds Swagger UI, keep its `UseSwaggerUI` registration inside a Development branch too. Protecting the document endpoint does not automatically protect separately registered UI middleware.

Register health checks before building the app, then require authorization on their endpoint:

```csharp
builder.Services.AddHealthChecks();
```

```csharp
app.MapHealthChecks("/healthz").RequireAuthorization();
```

Configure the monitoring client to authenticate, or deliberately expose a minimal liveness response through a separately controlled route. `RequireHost` matches a client-supplied Host header, which can be spoofed; it is not a network or authentication boundary.

For default ASP.NET Core hosting, merge an explicit host allowlist into `appsettings.json`:

```json
{
  "AllowedHosts": "example.com;www.example.com"
}
```

Use semicolon-separated hostnames without ports. `*` permits all hosts. Host filtering validates the request host; it does not authenticate the caller or restrict listening interfaces. `ForwardedHeadersOptions.AllowedHosts` is a separate setting for forwarded host values when the proxy replaces the original Host header.

## 9. Verify (REASONED: redirect, TLS, cookie-API and listener expectations follow the Sources below; no deployment outcomes are recorded. The authoring environment has no .NET runtime, container runtime or deployed application, as recorded below.)

```bash
curl -q -g --noproxy '*' -sI http://example.com/         # expect 307 or 308 with a https:// Location
curl -q -g --noproxy '*' -sI https://example.com/        # succeeds without -k; shows Strict-Transport-Security
curl -q -g --noproxy '*' -sS -o /dev/null -w '%{http_code}\n' https://example.com/api   # protected [ApiController] API using the cookie scheme: 401 without a cookie
ss -tlnp   # read every listener; dotnet: behind a proxy: 127.0.0.1 and ::1 only
```

For the `/api` check, the route must exist, require authorization, and use the app's cookie authentication scheme for challenge and forbid. With the default .NET 10 cookie handler, known API endpoints, including `[ApiController]` endpoints, return `401` for unauthenticated requests and `403` for authenticated users denied access. This changed in .NET 10; ordinary browser-page challenges can still redirect. An OIDC challenge scheme or customized cookie events can also change the response. Confirm that an authorized request reaches the expected API before interpreting a denial.

### Additional deployment checks

**REASONED, .NET 10 LTS:** The following checks have not been demonstrated: the authoring environment has no .NET runtime or container runtime, and no deployed application or replica infrastructure. Expected exposed and corrected outcomes rest on the cited .NET 10 documentation. Shell checks do not establish server behavior.

Paste each complete guarded block. Substitute the entire URL inside its single quotes; a literal apostrophe requires proper shell escaping. Run public-exposure checks from outside the application host and its trusted proxy network. Supply trusted CA configuration where needed; do not use `-k`. A DNS error, TLS failure, timeout, or HTTP `000` is not proof of an application-level rejection. The final `|| true` protects an enclosing shell from termination; it does not mean the check passed.

#### Production error disclosure (REASONED: the following block tests error representations against the cited error-handling documentation; no .NET runtime or deployed test application, as recorded below.)

**REASONED: no .NET runtime or deployed test application.** In an isolated deployment, provide a controlled route that throws an exception containing the harmless marker `DOTNET_VERIFY_CANARY`. Confirm that the route is reached, rather than stopped by authentication or routing. Use the public URL of that route below.

With the Developer Exception Page exposed, expect a `500` response containing diagnostic detail and the marker. With the production handler, expect the intended generic `500` response, with neither the marker nor stack traces, source paths, cookies, or configuration values. Inspect both representations and correlate the request with server logs; an empty body or a proxy-generated error alone does not establish that the application's handler ran. The distinguishing vendor behavior is documented under Developer Exception Page and Exception Handler Middleware in the error-handling source.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_ERROR_TEST_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the value inside the single quotes; not probing" ;;
    *)
      curl -q -g --noproxy '*' -sS -i --connect-timeout 5 --max-time 20 \
        -H 'Accept: text/plain' "$1"
      curl -q -g --noproxy '*' -sS -i --connect-timeout 5 --max-time 20 \
        -H 'Accept: text/html' "$1"
      ;;
  esac
) || true
```

#### Oversized-request rejection (REASONED: the following block compares body sizes against the cited Kestrel limit; no .NET runtime or deployed body-reading endpoint, as recorded below.)

**REASONED: no .NET runtime or deployed body-reading endpoint.** For the section-6 example, use an isolated deployment with a POST test endpoint that accepts `application/octet-stream`, consumes the entire body before returning `204`, and preserves body-limit failures as `413`. It must be reachable without an authentication challenge for these requests. Do not point this test at a business operation or an endpoint that ignores the body.

The fixed expectation is `204` at 1,048,576 bytes and `413` at 1,048,577 bytes. For the permissive comparison, raise only the tested limit above both sizes in the isolated deployment: both requests should return `204`. Keep other limits above the tested threshold when attributing the rejection to Kestrel. An upstream `413` demonstrates public enforcement, but does not prove which inner limit rejected the body. An authentication denial, parser error, `500`, or connection failure is inconclusive. The Kestrel request-body documentation describes the limit and its IIS hosting exception.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_BODY_TEST_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the value inside the single quotes; not probing" ;;
    *)
      head -c 1048576 /dev/zero | curl -q -g --noproxy '*' -sS \
        --http1.1 --connect-timeout 5 --max-time 30 \
        -H 'Content-Type: application/octet-stream' -H 'Expect:' \
        --data-binary @- -o /dev/null -w 'at-limit http=%{http_code}\n' "$1"
      head -c 1048577 /dev/zero | curl -q -g --noproxy '*' -sS \
        --http1.1 --connect-timeout 5 --max-time 30 \
        -H 'Content-Type: application/octet-stream' -H 'Expect:' \
        --data-binary @- -o /dev/null -w 'over-limit http=%{http_code}\n' "$1"
      ;;
  esac
) || true
```

#### Diagnostic, OpenAPI, and health access (REASONED: the following block checks endpoint exposure against the cited OpenAPI and health documentation; no deployed endpoints or external test vantage, as recorded below.)

**REASONED: no deployed endpoints or external test vantage.** The error probe above checks Developer Exception Page exposure. Inventory additional diagnostic routes and repeat the following GET probe for each applicable route, the OpenAPI document, any Swagger UI and its document route, and health checks. Common configured paths include `/openapi/v1.json`, `/swagger/index.html`, `/swagger/v1/swagger.json`, and `/healthz`; use the paths actually registered by the application.

In the exposed comparison, the request returns the diagnostic content, API description, UI, or health output without credentials. In the corrected deployment, Development-only routes are absent, while intentionally retained routes deny anonymous access according to their authentication scheme. An absent route normally returns `404`; fallback routing or authorization can change that response. Cookie or OIDC challenges can redirect on endpoints that are not treated as APIs. Do not follow redirects and mistake a login page for protected content.

For retained routes, pair the anonymous request with an authorized request through the normal client and confirm the expected content. A health endpoint can disclose its result with `200` or `503`; neither status by itself proves authorization. A GET to a migrations path cannot prove that `UseMigrationsEndPoint` is absent: inspect its Development-only registration and test its actual behavior in an isolated database deployment. The OpenAPI and health-check sources document the mapping and authorization controls.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_AUXILIARY_ENDPOINT_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the value inside the single quotes; not probing" ;;
    *)
      curl -q -g --noproxy '*' -sS -i --connect-timeout 5 --max-time 20 "$1"
      ;;
  esac
) || true
```

#### Public response headers (REASONED: the following block checks header removal against the cited Kestrel and IIS controls; no deployed Kestrel, IIS or proxy response, as recorded below.)

**REASONED: no deployed Kestrel, IIS, or proxy response.** Probe a known working public route and repeat for representative redirects and errors. Before removal, direct Kestrel responses normally include `Server: Kestrel`; IIS or the proxy can supply their own identifiers. After the relevant hosting-layer changes, expect no public `Server` or `X-Powered-By` header where removal is supported and configured. Inspect all returned headers, not just the application's normal success response. The Kestrel option and IIS sources distinguish which layer controls each header.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_PUBLIC_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the value inside the single quotes; not probing" ;;
    *)
      curl -q -g --noproxy '*' -sS -D - -o /dev/null \
        --connect-timeout 5 --max-time 20 "$1"
      ;;
  esac
) || true
```

#### Cookie continuity across restart and replicas (REASONED: the following block checks continuity against the cited key-lifetime and cookie-sharing documentation; no running cookie-authenticated application or replicas, as recorded below.)

**REASONED: no running cookie-authenticated application or replicas.** Sign in with a test account through the application's actual login flow and save its cookies in a private Netscape-format curl cookie file named `dotnet-verify.cookies`. Use an existing protected `[ApiController]` endpoint that authenticates and challenges with the app's cookie scheme and returns the test user's identity.

Run the pair below before restart, after restart, and while routing the same public hostname to each replica in turn. Confirm the selected replica in backend logs or the load balancer's controls; sticky routing to one instance does not test shared keys. Keep the cookie file unchanged, complete the test before expiry, and avoid account or security-stamp changes.

The anonymous control should return `401`. The request using the original cookie should return `200` with the same authenticated identity throughout. In an isolated comparison with process-only or non-shared keys, the cookie becomes unreadable after key loss or on a replica lacking its key. Do not delete production keys to create that comparison. Cookie renewal, expiry, session-store loss, and identity validation can also cause failures, so correlate them with application logs. Data Protection key-lifetime and cookie-sharing documentation explains the key-ring and scheme requirements.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_PROTECTED_COOKIE_API_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the value inside the single quotes; not probing" ;;
    *)
      curl -q -g --noproxy '*' -sS -i --connect-timeout 5 --max-time 20 "$1"
      curl -q -g --noproxy '*' -sS -i --connect-timeout 5 --max-time 20 \
        -b ./dotnet-verify.cookies "$1"
      ;;
  esac
) || true
```

Also retain an antiforgery token and its accompanying cookie across a restart, then submit the application's normal protected form. Confirm success without fetching a replacement token first. A lost key ring can invalidate antiforgery tokens independently of whether another authentication mechanism signs the user back in.

## Sources (checked September 2026)

- Enforce HTTPS (UseHttpsRedirection, UseHsts, HttpsPort) (.NET 10): https://learn.microsoft.com/en-us/aspnet/core/security/enforcing-ssl?view=aspnetcore-10.0 ; Kestrel endpoints (certificate config, ListenLocalhost, SslProtocols): https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/kestrel/endpoints?view=aspnetcore-10.0 ; proxy servers (ForwardedHeadersOptions, KnownProxies): https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/proxy-load-balancer?view=aspnetcore-10.0
- Introduction to Identity (lockout, ConfigureApplicationCookie) (.NET 10): https://learn.microsoft.com/en-us/aspnet/core/security/authentication/identity?view=aspnetcore-10.0 ; PasswordHasherOptions: https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.identity.passwordhasheroptions?view=aspnetcore-10.0
- Cookie authentication without Identity (.NET 10): https://learn.microsoft.com/en-us/aspnet/core/security/authentication/cookie?view=aspnetcore-10.0 ; CookieSecurePolicy: https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.http.cookiesecurepolicy?view=aspnetcore-10.0
- Rate limiting middleware (rate-limiting middleware in .NET 7 and later; guide targets .NET 10 LTS): https://learn.microsoft.com/en-us/aspnet/core/performance/rate-limit ; OpenID Connect web authentication: https://learn.microsoft.com/en-us/aspnet/core/security/authentication/configure-oidc-web-authentication?view=aspnetcore-10.0
- DangerousAcceptAnyServerCertificateValidator (.NET 10): https://learn.microsoft.com/en-us/dotnet/api/system.net.http.httpclienthandler.dangerousacceptanyservercertificatevalidator?view=net-10.0 ; trusted roots on Linux (rolling documentation, checked September 2026): https://learn.microsoft.com/en-us/dotnet/standard/security/cross-platform-cryptography
- .NET 10 Kestrel TLS protocol selection: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/kestrel/endpoints?view=aspnetcore-10.0
- .NET 10 HstsOptions defaults: https://raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/Middleware/HttpsPolicy/src/HstsOptions.cs
- .NET 10 proxy trust configuration and loopback defaults: https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/proxy-load-balancer?view=aspnetcore-10.0
- .NET 10 ForwardedHeadersOptions and KnownIPNetworks: https://raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/Middleware/HttpOverrides/src/ForwardedHeadersOptions.cs
- Unknown-proxy hardening in ASP.NET Core 8.0.17 and 9.0.6: https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/8/forwarded-headers-unknown-proxies?view=aspnetcore-10.0
- .NET 10 Identity lockout and template sign-in call: https://learn.microsoft.com/en-us/aspnet/core/security/authentication/identity-configuration?view=aspnetcore-10.0
- .NET 10 SameSite defaults for authentication, correlation, and nonce cookies: https://learn.microsoft.com/en-us/aspnet/core/security/samesite?view=aspnetcore-10.0
- .NET 10 cookie authentication behavior for API endpoints: https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/10/cookie-authentication-api-endpoints?view=aspnetcore-10.0
- .NET 10 native OpenSSL root-store file and directory selection: https://raw.githubusercontent.com/dotnet/runtime/v10.0.0/src/native/libs/System.Security.Cryptography.Native/pal_x509_root.c
- OpenSSL CA file, directory, and environment-variable semantics: https://docs.openssl.org/3.0/man3/SSL_CTX_load_verify_locations/
- .NET 10 production exception handling and database developer diagnostics: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling?view=aspnetcore-10.0
- .NET 10 environment selection and Production default: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/environments?view=aspnetcore-10.0
- WebApplicationBuilder environment-variable precedence change in .NET 7: https://learn.microsoft.com/en-us/aspnet/core/breaking-changes/7/environment-variable-precedence?view=aspnetcore-10.0
- .NET 10 UseMigrationsEndPoint API: https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.builder.migrationsendpointextensions.usemigrationsendpoint?view=aspnetcore-10.0
- .NET 10 Kestrel request-size enforcement, per-request overrides, IIS exception, and debugger behavior: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/kestrel/options?view=aspnetcore-10.0
- .NET 10 KestrelServerLimits defaults: https://raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/Servers/Kestrel/Core/src/KestrelServerLimits.cs
- .NET 10 Http2Limits defaults: https://raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/Servers/Kestrel/Core/src/Http2Limits.cs
- .NET 10 FormOptions multipart limits: https://raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/Http/Http/src/Features/FormOptions.cs
- .NET 10 DisableRequestSizeLimitAttribute: https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.mvc.disablerequestsizelimitattribute?view=aspnetcore-10.0
- .NET 10 upload limits and IIS request filtering: https://learn.microsoft.com/en-us/aspnet/core/mvc/models/file-uploads?view=aspnetcore-10.0
- .NET 10 IIS in-process hosting and IISServerOptions.MaxRequestBodySize: https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/iis/in-process-hosting?view=aspnetcore-10.0
- .NET 10 Data Protection persistence, application names, encryption, and isolation: https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/configuration/overview?view=aspnetcore-10.0
- .NET 10 environment-dependent key storage and key lifetime: https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/configuration/default-settings?view=aspnetcore-10.0
- .NET 10 ProtectKeysWithCertificate overloads: https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.dataprotection.dataprotectionbuilderextensions.protectkeyswithcertificate?view=aspnetcore-10.0
- .NET 10 Cookie sharing requirements for key rings, application names, and authentication schemes: https://learn.microsoft.com/en-us/aspnet/core/security/cookie-sharing?view=aspnetcore-10.0
- .NET 10 KestrelServerOptions.AddServerHeader default: https://raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/Servers/Kestrel/Core/src/KestrelServerOptions.cs
- IIS custom response headers and X-Powered-By (rolling documentation, checked September 2026): https://learn.microsoft.com/en-us/iis/configuration/system.webserver/httpprotocol/customheaders/
- IIS removeServerHeader requirements and request filtering (IIS 10; Windows Server version 1709 or Windows 10 version 1709): https://learn.microsoft.com/en-us/iis/configuration/system.webserver/security/requestfiltering/
- .NET 10 OpenAPI document generation and endpoint authorization: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/aspnetcore-openapi?view=aspnetcore-10.0
- .NET 10 OpenAPI documents with Development-only Swagger UI: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/using-openapi-documents?view=aspnetcore-10.0
- .NET 10 health-check authorization and Host-header spoofing: https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/health-checks?view=aspnetcore-10.0
- .NET 10 host filtering and AllowedHosts: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/kestrel/host-filtering?view=aspnetcore-10.0
- .NET 10 provider-side MFA requirements (checked October 2026): https://learn.microsoft.com/en-us/aspnet/core/security/authentication/mfa?view=aspnetcore-10.0
