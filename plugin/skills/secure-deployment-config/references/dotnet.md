# ASP.NET Core and Kestrel: TLS and authentication

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

## 9. Verify

```bash
curl -q -g --noproxy '*' -sI http://example.com/         # expect 307 or 308 with a https:// Location
curl -q -g --noproxy '*' -sI https://example.com/        # succeeds without -k; shows Strict-Transport-Security
curl -q -g --noproxy '*' -sS -o /dev/null -w '%{http_code}\n' https://example.com/api   # protected [ApiController] API using the cookie scheme: 401 without a cookie
ss -tlnp   # read every listener; dotnet: behind a proxy: 127.0.0.1 and ::1 only
```

For the `/api` check, the route must exist, require authorization, and use the app's cookie authentication scheme for challenge and forbid. With the default .NET 10 cookie handler, known API endpoints, including `[ApiController]` endpoints, return `401` for unauthenticated requests and `403` for authenticated users denied access. This changed in .NET 10; ordinary browser-page challenges can still redirect. An OIDC challenge scheme or customized cookie events can also change the response. Confirm that an authorized request reaches the expected API before interpreting a denial.

### Additional deployment checks

**REASONED, .NET 10 LTS:** The following checks have not been demonstrated: the authoring environment has no .NET runtime or container runtime, and no deployed application or replica infrastructure. `DOTNET-VERIFY` in [TODO.md](TODO.md) tracks demonstration against exposed and corrected deployments. Shell checks do not establish server behavior.

Paste each complete guarded block. Substitute the entire URL inside its single quotes; a literal apostrophe requires proper shell escaping. Run public-exposure checks from outside the application host and its trusted proxy network. Supply trusted CA configuration where needed; do not use `-k`. A DNS error, TLS failure, timeout, or HTTP `000` is not proof of an application-level rejection. The final `|| true` protects an enclosing shell from termination; it does not mean the check passed.

#### Production error disclosure

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

#### Oversized-request rejection

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

#### Diagnostic, OpenAPI, and health access

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

#### Public response headers

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

#### Cookie continuity across restart and replicas

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

- Enforce HTTPS (UseHttpsRedirection, UseHsts, HttpsPort): https://learn.microsoft.com/en-us/aspnet/core/security/enforcing-ssl ; Kestrel endpoints (certificate config, ListenLocalhost, SslProtocols): https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/kestrel/endpoints ; proxy servers (ForwardedHeadersOptions, KnownProxies): https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/proxy-load-balancer
- Introduction to Identity (lockout, ConfigureApplicationCookie): https://learn.microsoft.com/en-us/aspnet/core/security/authentication/identity ; PasswordHasherOptions: https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.identity.passwordhasheroptions
- Cookie authentication without Identity: https://learn.microsoft.com/en-us/aspnet/core/security/authentication/cookie ; CookieSecurePolicy: https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.http.cookiesecurepolicy
- Rate limiting middleware: https://learn.microsoft.com/en-us/aspnet/core/performance/rate-limit ; OpenID Connect web authentication: https://learn.microsoft.com/en-us/aspnet/core/security/authentication/configure-oidc-web-authentication
- DangerousAcceptAnyServerCertificateValidator: https://learn.microsoft.com/en-us/dotnet/api/system.net.http.httpclienthandler.dangerousacceptanyservercertificatevalidator ; trusted roots on Linux: https://learn.microsoft.com/en-us/dotnet/standard/security/cross-platform-cryptography
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
- Kestrel request-size enforcement, per-request overrides, IIS exception, and debugger behavior: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/kestrel/options?view=aspnetcore-10.0
- .NET 10 KestrelServerLimits defaults: https://raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/Servers/Kestrel/Core/src/KestrelServerLimits.cs
- .NET 10 Http2Limits defaults: https://raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/Servers/Kestrel/Core/src/Http2Limits.cs
- .NET 10 FormOptions multipart limits: https://raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/Http/Http/src/Features/FormOptions.cs
- .NET 10 DisableRequestSizeLimitAttribute: https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.mvc.disablerequestsizelimitattribute?view=aspnetcore-10.0
- .NET 10 upload limits and IIS request filtering: https://learn.microsoft.com/en-us/aspnet/core/mvc/models/file-uploads?view=aspnetcore-10.0
- IIS in-process hosting and IISServerOptions.MaxRequestBodySize: https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/iis/in-process-hosting?view=aspnetcore-10.0
- .NET 10 Data Protection persistence, application names, encryption, and isolation: https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/configuration/overview?view=aspnetcore-10.0
- .NET 10 environment-dependent key storage and key lifetime: https://learn.microsoft.com/en-us/aspnet/core/security/data-protection/configuration/default-settings?view=aspnetcore-10.0
- .NET 10 ProtectKeysWithCertificate overloads: https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.dataprotection.dataprotectionbuilderextensions.protectkeyswithcertificate?view=aspnetcore-10.0
- Cookie sharing requirements for key rings, application names, and authentication schemes: https://learn.microsoft.com/en-us/aspnet/core/security/cookie-sharing?view=aspnetcore-10.0
- .NET 10 KestrelServerOptions.AddServerHeader default: https://raw.githubusercontent.com/dotnet/aspnetcore/v10.0.0/src/Servers/Kestrel/Core/src/KestrelServerOptions.cs
- IIS custom response headers and X-Powered-By: https://learn.microsoft.com/en-us/iis/configuration/system.webserver/httpprotocol/customheaders/
- IIS removeServerHeader requirements and request filtering: https://learn.microsoft.com/en-us/iis/configuration/system.webserver/security/requestfiltering/
- .NET 10 OpenAPI document generation and endpoint authorization: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/aspnetcore-openapi?view=aspnetcore-10.0
- .NET 10 OpenAPI documents with Development-only Swagger UI: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/using-openapi-documents?view=aspnetcore-10.0
- .NET 10 health-check authorization and Host-header spoofing: https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/health-checks?view=aspnetcore-10.0
- .NET 10 host filtering and AllowedHosts: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/kestrel/host-filtering?view=aspnetcore-10.0
