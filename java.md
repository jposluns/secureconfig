# Spring Boot: TLS and authentication

Spring Boot is a Java framework for building web apps that run on a built-in web server. This guide helps your AI assistant deploy it securely, including TLS directly or behind a reverse proxy, authentication, Actuator endpoints limited and bound to a private management port, and production error responses.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/java.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against Spring Boot 4.1.1, Spring Boot starter migration 4.0, Spring Security HSTS 6.5, JDK keytool documentation 21, Tomcat HTTP connector 10.1, curl minimum diagnostics version 7.75.0, OpenJDK jdk21u javax.net.ssl sources jdk-21.0.12.1-ga, and Authelia source v4.39.28; 2 further sources are pinned to a commit and 4 carry no recorded version. Metadata reviewed 2026-10-19; documentation checked September 2026. The guide records 57 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

Preferred production layout: bind the embedded server to `127.0.0.1` and terminate TLS in a reverse proxy ([caddy.md](caddy.md), [nginx.md](nginx.md)) or behind [cloudflare.md](cloudflare.md). Spring Boot can also terminate TLS itself, shown below. Certificates: [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md).

## 1. HTTPS directly in Spring Boot

PEM certificate and key, or a PKCS12 keystore (the PEM properties are in the current Spring Boot how-to; on an older release, confirm your version's reference lists `server.ssl.certificate` before relying on it):

```properties
server.port=8443
server.ssl.certificate=file:/etc/ssl/certs/server.crt
server.ssl.certificate-private-key=file:/etc/ssl/private/server.key
server.ssl.enabled-protocols=TLSv1.2,TLSv1.3
# PKCS12 keystore instead of the two PEM lines:
# server.ssl.key-store=file:/etc/ssl/private/server.p12
# server.ssl.key-store-password=REPLACE_WITH_LONG_RANDOM_VALUE
# server.ssl.key-store-type=PKCS12
```

Spring Boot configures one connector from properties, HTTP or HTTPS, not both; the how-to recommends HTTPS in properties and an HTTP connector added in code if a port 80 redirect is needed. With Spring Security 6.5 or later, `http.redirectToHttps(withDefaults())` in the `SecurityFilterChain` sends requests that arrive over HTTP to HTTPS, and Spring Security's default writer emits `Strict-Transport-Security` only when the request's `isSecure()` returns `true`. The HSTS defaults are one year (`max-age=31536000`), `includeSubDomains=true`, and `preload=false`. Behind TLS termination, trusted forwarded-header handling matters because it determines whether the application sees the request as secure. In the proxy layout, let the proxy do the redirect and skip the second connector.

## 2. Behind a proxy

```properties
server.address=127.0.0.1
server.port=8080
server.forward-headers-strategy=NATIVE
```

`NATIVE` lets the embedded server (Tomcat by default) honour `X-Forwarded-For` and `X-Forwarded-Proto`; `FRAMEWORK` uses Spring's `ForwardedHeaderFilter` instead; the default outside supported cloud platforms is `NONE`. With Tomcat, `server.tomcat.remoteip.internal-proxies` restricts which proxy addresses those headers are accepted from, and `server.tomcat.redirect-context-root=false` keeps redirects on HTTPS when TLS ends at the proxy.

The edge proxy must strip inbound `Forwarded` and `X-Forwarded-*` headers before setting trusted values. Restrict direct access to the application listener so clients cannot bypass that boundary. Spring's [forwarded-header documentation](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/filter/ForwardedHeaderFilter.html) explicitly requires removing externally supplied forwarded headers at the trust boundary.

For code that imports server configuration, `ServerProperties` is `org.springframework.boot.autoconfigure.web.ServerProperties` in Boot 3.5 and `org.springframework.boot.web.server.autoconfigure.ServerProperties` in Boot 4. See the [3.5.16 API](https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/autoconfigure/web/ServerProperties.html) and [4.1.1 API](https://docs.spring.io/spring-boot/4.1/api/java/org/springframework/boot/web/server/autoconfigure/ServerProperties.html).

## 3. Authentication

Follow [authentication.md](authentication.md). With `spring-boot-starter-security` on the classpath and Boot's default web security configuration active, application endpoints require authentication, except that Actuator health is permitted when Actuator is present; form login and HTTP Basic are on, and CSRF protection and security headers are on. Defining any custom `SecurityFilterChain` makes Boot's default web security configuration back off, including its Actuator rules. The separate default-user auto-configuration, when applicable, creates a single user `user` with a generated password normally logged at startup; a custom filter chain alone does not remove that user. That user is for development only; `spring.security.user.name` and `spring.security.user.password` replace it for local use. Production needs deliberately configured authentication: OAuth2/OIDC does not require a local `UserDetailsService`; for locally stored accounts, configure a real `UserDetailsService` with this encoder:

```java
@Bean
PasswordEncoder passwordEncoder() {
    return PasswordEncoderFactories.createDelegatingPasswordEncoder();   // bcrypt by default, stored as {bcrypt}...
}
```

`BCryptPasswordEncoder(strength)` defaults to strength 10; the docs say to tune it to about 1 second per verification. `Argon2PasswordEncoder.defaultsForSpringSecurity_v5_8()` is the alternative.

Session cookie flags and lifetime:

```properties
server.servlet.session.cookie.secure=true
server.servlet.session.cookie.http-only=true
server.servlet.session.cookie.same-site=lax
server.servlet.session.timeout=30m
```

The Spring Security reference pages checked document no built-in login rate limiter: limit `/login` at the reverse proxy ([nginx.md](nginx.md), [caddy.md](caddy.md)), or count failures and lock the account in your own `UserDetailsService`.

SSO: use `spring-boot-starter-oauth2-client` for Boot 3.5 or `spring-boot-starter-security-oauth2-client` for Boot 4, plus properties and `http.oauth2Login(withDefaults())`. Boot 4 deprecates the old starter name; see the [Boot 4.0 starter reference](https://docs.spring.io/spring-boot/4.0/reference/using/build-systems.html) and [4.0 migration guide](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide):

```properties
spring.security.oauth2.client.registration.sso.client-id=REPLACE_WITH_CLIENT_ID
spring.security.oauth2.client.registration.sso.client-secret=${SSO_CLIENT_SECRET}
spring.security.oauth2.client.registration.sso.provider=sso
spring.security.oauth2.client.registration.sso.scope=openid,profile,email
spring.security.oauth2.client.provider.sso.issuer-uri=https://idp.example.com/
```

The `issuer-uri` drives OpenID Connect discovery, and the `openid` scope is what makes the registration an OpenID Connect login that returns an ID token; without it the login is plain OAuth2. Allowlist and token checks are in [oidc-integration.md](oidc-integration.md), providers in [identity-providers.md](identity-providers.md). MFA: enforce it at the identity provider, or front the app per [mfa.md](mfa.md). Examples of layers that can require MFA, cited at the pins in Sources: a Microsoft Entra Conditional Access policy can grant access only with the built-in Multifactor authentication strength; Cloudflare Access independent MFA lets Access enforce MFA requirements without relying on the identity provider, prompting for an additional authentication method before granting access to the application; and Authelia supports configuring TOTP, WebAuthn security keys and Duo mobile push as second factors. None of those pages says a layer enforces MFA by default, and none establishes that this deployment's provider or fronting layer requires MFA; checking the effective policy and testing a login without the second factor are this guide's requirements.

Do not disable CSRF protection merely because an API is "stateless". Browsers can automatically attach authentication cookies or HTTP Basic credentials, so those requests remain vulnerable to CSRF. Decide from how clients supply credentials, not from whether the application stores a session. See Spring Security's [stateless-browser qualification](https://docs.spring.io/spring-security/reference/features/exploits/csrf.html#csrf-and-stateless-browser-applications).

Spring Security's default session fixation protection uses `changeSessionId` on Servlet 3.1 and newer containers: an existing session receives a new ID on authentication. Keep this protection enabled. See [session fixation protection](https://docs.spring.io/spring-security/reference/servlet/authentication/session-management.html#understanding-session-fixation-attack-protection).

## 4. Client-side TLS discipline

- Never install a trust-all `TrustManager` or hostname verifier, and never copy one from an answer that "fixes" a certificate error. The pinned jdk21u sources document what such code switches off: `X509TrustManager` instances manage which X509 certificates may be used to authenticate the remote side of a secure socket, and its `checkClientTrusted` and `checkServerTrusted` methods throw `CertificateException` when a chain is not trusted; `HostnameVerifier.verify` decides whether a connection is allowed when the URL hostname and the server's identification hostname mismatch; `SSLContext.init` takes trust managers as that context's sources of peer authentication trust decisions. The scope depends on where the trust-all code lands: `HttpsURLConnection.setDefaultSSLSocketFactory` and `setDefaultHostnameVerifier` set the defaults inherited by `HttpsURLConnection` instances created afterwards, a process-wide default, while the per-instance `setSSLSocketFactory` and `setHostnameVerifier` replace only that one object's factory or verifier. That a trust-all pair disables certificate and hostname validation for every client built from the affected `SSLContext` or default, and any reading as broad as "the whole JVM client", are this guide's assessment of those documented contracts rather than statements on the cited lines; the prohibition applies at every scope.
- For an internal CA, either import it into the JDK truststore, `keytool -importcert -cacerts -alias internal-ca -file /path/ca.crt` (the `cacerts` password defaults to `changeit`; change it), or declare an SSL bundle, `spring.ssl.bundle.pem.internal.truststore.certificate=file:/path/ca.crt`, and apply it to the client: `restClientBuilder.apply(ssl.fromBundle("internal"))` with an injected `RestClientSsl` (`WebClientSsl` for `WebClient`). See [self-signed.md](self-signed.md).

The client SSL helper imports differ between [Boot 3.5.16](https://docs.spring.io/spring-boot/3.5/reference/io/rest-client.html) and [Boot 4.1.1](https://docs.spring.io/spring-boot/4.1/reference/io/rest-client.html):

| Helper | Boot 3.5 | Boot 4 |
| --- | --- | --- |
| `RestClientSsl` | `org.springframework.boot.autoconfigure.web.client.RestClientSsl` | `org.springframework.boot.restclient.autoconfigure.RestClientSsl` |
| `WebClientSsl` | `org.springframework.boot.autoconfigure.web.reactive.function.client.WebClientSsl` | `org.springframework.boot.webclient.autoconfigure.WebClientSsl` |

## 5. Actuator: expose only what you need, bind management privately, authorize administrators

Actuator can disclose application internals and provide administrative operations. In Boot 3.5.16 and 4.1.1, `management.endpoints.web.exposure.include` defaults to `health`. Keep an explicit allowlist instead of exposing `*`. Exposure, endpoint access, and HTTP authorization are separate controls. See the [3.5 endpoint reference](https://docs.spring.io/spring-boot/3.5/reference/actuator/endpoints.html) and [4.1 endpoint reference](https://docs.spring.io/spring-boot/4.1/reference/actuator/endpoints.html).

```properties
management.endpoints.web.exposure.include=health
management.server.port=8081
management.server.address=127.0.0.1
management.endpoint.shutdown.access=none
management.endpoint.heapdump.access=none
```

Use a management port different from the main application's port: `management.server.address` can bind a different address only with a separate port. Keep the listener private and do not forward the public proxy to it. To disable management HTTP endpoints entirely, use `management.server.port=-1` instead of `8081`; this does not disable JMX exposure. These settings are documented for [Boot 3.5](https://docs.spring.io/spring-boot/3.5/reference/actuator/monitoring.html) and [Boot 4.1](https://docs.spring.io/spring-boot/4.1/reference/actuator/monitoring.html).

Treat individual endpoints according to what they reveal or change:

- `env` and `configprops` sanitize values by default; their `show-values` settings default to `never`. Sanitization does not justify exposing configuration metadata publicly.
- `beans`, `mappings`, and `threaddump` disclose application components, request routes, and thread stacks.
- `heapdump` can expose secrets held in process memory and consume substantial resources. Keep it unavailable outside a controlled diagnostic procedure.
- `loggers` can read and change logging levels. Administrative writes can increase logging volume and expose information through logs.
- `shutdown` stops the application. Its access defaults to `none`; `heapdump` also defaults to `none` in the specifically checked 3.5.16 and 4.1.1 releases. Do not assume defaults from an older patch release.

The endpoint descriptions and sanitization behaviour are documented in the [Boot 3.5 Actuator reference](https://docs.spring.io/spring-boot/3.5/reference/actuator/endpoints.html#actuator.endpoints.sanitization) and [Boot 4.1 Actuator reference](https://docs.spring.io/spring-boot/4.1/reference/actuator/endpoints.html#actuator.endpoints.sanitization).

Authorize administrators explicitly. For a servlet application, this example requires `ROLE_ENDPOINT_ADMIN` for every exposed Actuator endpoint, including health. It also supplies a fallback chain for application requests:

```java
import org.springframework.boot.actuate.autoconfigure.security.servlet.EndpointRequest;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.annotation.Order;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;

import static org.springframework.security.config.Customizer.withDefaults;

@Configuration(proxyBeanMethods = false)
public class DeploymentSecurityConfiguration {

    @Bean
    @Order(1)
    SecurityFilterChain managementSecurity(HttpSecurity http) throws Exception {
        http.securityMatcher(EndpointRequest.toAnyEndpoint());
        http.authorizeHttpRequests(requests ->
                requests.anyRequest().hasRole("ENDPOINT_ADMIN"));
        http.httpBasic(withDefaults());
        return http.build();
    }

    @Bean
    @Order(2)
    SecurityFilterChain applicationSecurity(HttpSecurity http) throws Exception {
        http.authorizeHttpRequests(requests ->
                requests.anyRequest().authenticated());
        http.formLogin(withDefaults());
        http.httpBasic(withDefaults());
        return http.build();
    }
}
```

The example imports Boot 3.5's `org.springframework.boot.actuate.autoconfigure.security.servlet.EndpointRequest`. For Boot 4, replace that import with `org.springframework.boot.security.autoconfigure.actuate.web.servlet.EndpointRequest`. Both versions document `EndpointRequest.toAnyEndpoint()` with `securityMatcher`. See the [3.5 example](https://docs.spring.io/spring-boot/3.5/reference/actuator/endpoints.html#actuator.endpoints.security) and [4.1 example](https://docs.spring.io/spring-boot/4.1/reference/actuator/endpoints.html#actuator.endpoints.security).

**Any custom `SecurityFilterChain` makes Boot's default web security back off. An Actuator-only chain is therefore insufficient: requests outside its matcher need another chain.** Spring Security does not protect requests that match no chain. Integrate these rules into existing chains rather than adding competing configurations, and retain the application's authentication method and route permissions. For the OIDC setup in section 3, use `http.oauth2Login(withDefaults())` in the application chain instead of its local form login. Provision the administrator authority through the configured authentication system; this example does not create an administrator. See [multiple filter chains](https://docs.spring.io/spring-security/reference/servlet/configuration/java.html#_multiple_httpsecurity_instances).

## 6. Production error responses and development surfaces

Keep exception details out of client responses. The following are the defaults checked in Boot 3.5.16 and 4.1.1; declaring them explicitly helps prevent development configuration from becoming production configuration.

Boot 3.5:

```properties
server.error.include-message=never
server.error.include-stacktrace=never
server.error.include-binding-errors=never
server.error.include-exception=false
```

Boot 4:

```properties
spring.web.error.include-message=never
spring.web.error.include-stacktrace=never
spring.web.error.include-binding-errors=never
spring.web.error.include-exception=false
```

Use the property family for the deployed major version. The prefix moved from `server.error` to `spring.web.error`; see the [3.5.16 properties](https://docs.spring.io/spring-boot/3.5/appendix/application-properties/index.html) and [4.1.1 properties](https://docs.spring.io/spring-boot/4.1/appendix/application-properties/index.html).

`on-param` is not a production security boundary: the requester can supply the parameter that requests the error attribute. Disabling the whitelabel page alone changes the HTML error presentation; it does not fix information disclosed through JSON responses, custom error handlers, or container error pages. Apply the same disclosure policy to application-defined error responses. See the [error-inclusion options](https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/autoconfigure/web/ErrorProperties.IncludeAttribute.html) and [servlet error handling](https://docs.spring.io/spring-boot/3.5/reference/web/servlet.html).

Keep the H2 console off in production. This property defaults to `false` in both checked releases:

```properties
spring.h2.console.enabled=false
```

Exclude `spring-boot-devtools` from production dependencies and deployed artifacts. When its development defaults are active, it sets error message, stack trace, and binding-error inclusion to `always`, using the version-appropriate prefix, and sets `spring.h2.console.enabled=true`. Console availability still depends on the required H2 components. Verify the production artifact and launch configuration rather than relying only on the normal packaged-application behaviour. See [Boot 3.5 devtools defaults](https://docs.spring.io/spring-boot/3.5/reference/using/devtools.html#using.devtools.property-defaults) and [Boot 4.1 devtools defaults](https://docs.spring.io/spring-boot/4.1/reference/using/devtools.html#using.devtools.property-defaults).

## 7. Bound uploads, forms, and headers

Set limits according to the requests the application needs to accept. These property names and defaults are the same in the checked Boot 3.5.16 and 4.1.1 releases:

```properties
spring.servlet.multipart.max-file-size=1MB
spring.servlet.multipart.max-request-size=10MB
server.tomcat.max-http-form-post-size=2MB
server.max-http-request-header-size=8KB
```

| Property | Scope |
| --- | --- |
| `spring.servlet.multipart.max-file-size` | Each uploaded file handled by servlet multipart support. |
| `spring.servlet.multipart.max-request-size` | The complete multipart request, including its parts and multipart overhead. |
| `server.tomcat.max-http-form-post-size` | Tomcat's processing of form request bodies into parameters; not arbitrary request bodies. |
| `server.max-http-request-header-size` | HTTP request headers, with details dependent on the embedded server. Tomcat counts the request line and all header names and values together. |

The defaults and header qualifications appear in the [3.5.16 property reference](https://docs.spring.io/spring-boot/3.5/appendix/application-properties/index.html) and [4.1.1 property reference](https://docs.spring.io/spring-boot/4.1/appendix/application-properties/index.html). Tomcat explicitly documents that its [form parsing limit](https://tomcat.apache.org/tomcat-10.1-doc/config/http.html) is not a general request-body limit.

None of these properties establishes a universal JSON body limit. Bound other request bodies at the reverse proxy and, where necessary, in the application's request processing. Test the actual content type and route; an authentication failure does not demonstrate a size limit.

## 8. Verify (REASONED: TLS, authentication, listener and generated-user checks follow the Spring Sources below; no deployment outcomes are recorded. The authoring environment limitations are recorded below: no runnable Spring Boot fixture, Maven, Gradle or container runtime.)

```bash
curl -q -g -sI --noproxy '*' https://example.com/        # succeeds without -k; shows Strict-Transport-Security
curl -q -g -sS --noproxy '*' -o /dev/null -w '%{http_code}\n' https://example.com/api   # 401, or 302 to the login page, without credentials
ss -tlnp   # read every listener; java: behind a proxy: 127.0.0.1 only
grep -c "Using generated security password" app.log   # a positive count records password generation; zero does not prove the default user is absent
```

A zero generated-password log count is inconclusive: logging may suppress the message, and setting `spring.security.user.password` avoids password generation while retaining the default account. Check the deployed authentication configuration and exercise the intended login method. A custom `SecurityFilterChain` alone does not remove default-user auto-configuration, and OAuth2/OIDC does not require introducing a local `UserDetailsService`. See [Boot's security auto-configuration rules](https://docs.spring.io/spring-boot/3.5/reference/web/spring-security.html).

The following deployment checks are **REASONED, not demonstrated**. The authoring environment has no runnable Spring Boot fixture, no Maven or Gradle executable, and no container runtime; its filesystem is read-only and network access is restricted. Shell syntax and negative placeholder-guard cases were checked locally. Expected deployment outcomes rest on the cited Spring Boot and vendor documentation.

Paste each guarded block whole and substitute inside the single quotes. Supply URLs without a trailing slash where the block appends a path, and without existing query parameters where it appends a query. These blocks require curl 7.75.0 or newer for `exitcode` and `errormsg`. A DNS error, TLS failure, or timeout is not proof that an endpoint is securely configured; inspect the error and confirm the intended service and network path.

For authenticated requests, prepare `./java-verify-auth.headers` as a private, mode `0600` file containing the actual request headers for a test identity, one header per line. Use the application's authentication method, such as its session cookie or an accepted authorization header. For uploads, include the matching session and valid CSRF header where required. The blocks pass that file to curl through stdin, keeping credential values out of command arguments. Protect and remove the file after testing. Curl documents [header input and transfer diagnostics](https://curl.se/docs/manpage.html).

### Management reachability and authorization (REASONED: public/private Actuator access and external-port checks follow the cited endpoint and management-listener references; no runnable Spring Boot fixture or external management test deployment is available, as recorded above.)

Reasoned check: run this HTTPS sweep from outside the trusted management network against the public application origin to verify that it does not serve Actuator responses to either identity. Include any configured context or management base path in the substituted URL. Use an administrator identity for the authenticated pass.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'https://REPLACE_WITH_PUBLIC_HOST/actuator'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the value inside the quotes on the set -- line; not probing" ;;
    *)
      for java_endpoint in health env configprops beans mappings threaddump loggers; do
        curl -q -g -sS --noproxy '*' --proto '=https' --connect-timeout 5 --max-time 20 \
          -o /dev/null -w 'anonymous %{url_effective}: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
          "$1/$java_endpoint" || true
        curl -q -g -sS --noproxy '*' --proto '=https' --connect-timeout 5 --max-time 20 \
          --header @- -o /dev/null \
          -w 'authorized %{url_effective}: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
          "$1/$java_endpoint" < ./java-verify-auth.headers || true
      done
      ;;
  esac
) || true
```

Reasoned check: run this separate management-authorization sweep on the application host against the HTTP listener at `http://127.0.0.1:8081/actuator`. Adjust the port and base path in both URLs to match your management configuration. Prepare `./java-verify-auth.headers` on that host with an administrator identity accepted by the management security chain.

```bash
(
  for java_endpoint in health env configprops beans mappings threaddump loggers; do
    curl -q -g -sS --noproxy '*' --proto '=http' --connect-timeout 5 --max-time 20 \
      -o /dev/null -w 'anonymous %{url_effective}: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
      "http://127.0.0.1:8081/actuator/$java_endpoint" || true
    curl -q -g -sS --noproxy '*' --proto '=http' --connect-timeout 5 --max-time 20 \
      --header @- -o /dev/null \
      -w 'authorized %{url_effective}: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
      "http://127.0.0.1:8081/actuator/$java_endpoint" < ./java-verify-auth.headers || true
  done
) || true
```

With the private-listener layout, the public origin must not serve Actuator responses to either identity. On the reachable management listener, the example security chain should reject anonymous health requests with `401`, reject an authenticated non-administrator with `403`, and allow an administrator to receive the health response. Health itself can report an unhealthy status, commonly `503`, so successful authorization is not synonymous with HTTP `200`.

With health-only exposure, the other listed endpoints should remain unavailable even to an administrator, normally returning `404` once authentication succeeds. An anonymous `2xx` from a sensitive endpoint needs investigation; `401` or `403` demonstrates access control, not absence. Confirm that responses come from the intended application rather than a proxy or generic frontend. Repeat the authenticated pass with a non-administrator to test the role boundary. These expectations follow the documented [endpoint exposure and security rules](https://docs.spring.io/spring-boot/4.1/reference/actuator/endpoints.html).

Also check the separate port directly from an external machine. This block assumes the HTTP management listener in the proxy layout above; use the actual port and protocol if different:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PUBLIC_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the value inside the quotes on the set -- line; not probing" ;;
    *)
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
        -o /dev/null -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "http://$1:8081/actuator/health" || true
      ;;
  esac
) || true
```

Any HTTP response, including `401`, demonstrates that an HTTP listener is reachable on that public port. The fixed loopback binding should prevent that connection. Corroborate external failure with the existing `ss -tlnp` check on the server and a successful connection from the intended management path; an external timeout alone is inconclusive. See [management address binding](https://docs.spring.io/spring-boot/3.5/reference/actuator/monitoring.html#actuator.monitoring.customizing-management-server-address).

The sweep deliberately omits heap-dump generation and shutdown. Verify their explicit `access=none` settings in the effective deployment configuration. Demonstrating their exposed behaviour belongs in an isolated fixture: a heap-dump request can allocate substantial resources, and a shutdown request can stop the process.

### Error-body leakage (REASONED: error disclosure checks follow the cited error-inclusion references; the recorded authoring environment has no runnable Spring Boot fixture.)

Reasoned check: use an isolated test deployment with a known route that triggers a controlled exception containing a recognizable, non-secret marker. Supply that route below, then repeat for a known binding-error case. Use credentials that allow the request to reach the handler. A missing URL alone does not exercise exception or binding-error disclosure.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'https://REPLACE_WITH_HOST/REPLACE_WITH_TEST_ERROR_PATH'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the value inside the quotes on the set -- line; not probing" ;;
    *)
      curl -q -g -sS -i --noproxy '*' --proto '=https' --connect-timeout 5 --max-time 20 \
        --header @- -H 'Accept: application/json' \
        -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "$1?trace=true&message=true&errors=true" < ./java-verify-auth.headers || true
      ;;
  esac
) || true
```

In the exposed fixture, `always` or `on-param` inclusion can reveal the controlled message, trace, or binding details. With the production settings, Boot's standard error response should omit those details and the exception class even with these parameters. Confirm the expected error status and inspect the body for the marker, stack frames, internal paths, and rejected values. An authentication response does not test error handling. Repeat with `Accept: text/html` and check custom error responses separately. See the [error-inclusion semantics](https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/autoconfigure/web/ErrorProperties.IncludeAttribute.html) and [versioned production defaults](https://docs.spring.io/spring-boot/4.1/appendix/application-properties/index.html).

### H2 console absence (REASONED: console absence checks follow the cited console properties and devtools defaults; the recorded authoring environment has no runnable Spring Boot fixture.)

Reasoned check: test both anonymously and with an identity allowed through application security. Substitute the configured console path if it differs from `/h2-console/`.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'https://REPLACE_WITH_HOST/h2-console/'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the value inside the quotes on the set -- line; not probing" ;;
    *)
      curl -q -g -sS -i --noproxy '*' --proto '=https' --connect-timeout 5 --max-time 20 \
        -w '\nanonymous: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1" || true
      curl -q -g -sS -i --noproxy '*' --proto '=https' --connect-timeout 5 --max-time 20 \
        --header @- -w '\nauthorized: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "$1" < ./java-verify-auth.headers || true
      ;;
  esac
) || true
```

An enabled, reachable console can return H2 content or a redirect into it. With the console disabled, a request that passes application security should reach normal missing-route handling, typically `404`, without H2 content. A login redirect, `401`, or `403` alone does not establish absence. Confirm the effective `spring.h2.console.enabled=false` setting and absence of production devtools as well. See the [console properties](https://docs.spring.io/spring-boot/4.1/appendix/application-properties/index.html) and [devtools overrides](https://docs.spring.io/spring-boot/4.1/reference/using/devtools.html#using.devtools.property-defaults).

### Over-limit upload (REASONED: multipart discrimination follows the cited multipart limits; the recorded authoring environment has no runnable Spring Boot upload fixture.)

Reasoned check: use a test upload route that accepts a multipart file field named `file`. Prepare `./below-limit.bin` with 1,024 bytes and `./over-limit.bin` with 1,048,577 bytes of non-secret test data. These sizes bracket the configured `1MB` file limit while remaining below the `10MB` request limit. Supply valid authentication and CSRF headers for both requests, and adapt the field name to the real handler.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'https://REPLACE_WITH_HOST/REPLACE_WITH_UPLOAD_PATH'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the value inside the quotes on the set -- line; not probing" ;;
    *)
      curl -q -g -sS -i --noproxy '*' --proto '=https' --connect-timeout 5 --max-time 30 \
        --header @- --form 'file=@./below-limit.bin' \
        -w '\nbelow limit: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "$1" < ./java-verify-auth.headers || true
      curl -q -g -sS -i --noproxy '*' --proto '=https' --connect-timeout 5 --max-time 30 \
        --header @- --form 'file=@./over-limit.bin' \
        -w '\nover limit: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "$1" < ./java-verify-auth.headers || true
      ;;
  esac
) || true
```

The small upload must reach and succeed at the intended handler. With a deliberately raised limit in an isolated exposed fixture, both files should succeed; with the production limit, the larger file must be rejected because of its size. Inspect the response and server logs for that specific cause. Authentication, CSRF, missing-route, content-validation, and transport failures are not evidence of the multipart limit. A proxy rejection demonstrates the proxy limit; testing Boot's limit also requires reaching the application through an authorized path. See the [multipart limits](https://docs.spring.io/spring-boot/3.5/appendix/application-properties/index.html).

## Sources (checked September 2026)

- Spring Boot how-to, embedded web servers (Configure SSL, forward headers, Tomcat proxy settings): https://docs.spring.io/spring-boot/how-to/webserver.html
- Spring Boot SSL bundles: https://docs.spring.io/spring-boot/reference/features/ssl.html ; REST clients (applying a bundle): https://docs.spring.io/spring-boot/reference/io/rest-client.html
- Spring Boot javadoc, Ssl (rolling documentation, checked September 2026): https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/web/server/Ssl.html
- Spring Boot javadoc, ServerProperties (address, forwardHeadersStrategy, servlet.session) (rolling documentation, checked September 2026): https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/autoconfigure/web/ServerProperties.html
- Spring Boot javadoc, ServerProperties (moved package) (rolling documentation, checked September 2026): https://docs.spring.io/spring-boot/4.1/api/java/org/springframework/boot/web/server/autoconfigure/ServerProperties.html
- Spring Boot javadoc, session Cookie: https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/web/server/Cookie.html ; Spring Boot and Spring Security defaults: https://docs.spring.io/spring-boot/reference/web/spring-security.html
- Spring Boot OAuth2 client properties: https://docs.spring.io/spring-boot/reference/security/oauth2.html ; Spring Security OAuth2 login: https://docs.spring.io/spring-security/reference/servlet/oauth2/login/core.html
- Spring Boot 4.0 starters and deprecated OAuth2 client starter name: https://docs.spring.io/spring-boot/4.0/reference/using/build-systems.html
- Spring Boot 4.0 migration guide, deprecated starters: https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide/e11f389f3671d1eb7fa346065410b5b1eab99c3c
- Spring Security getting started (Boot defaults): https://docs.spring.io/spring-security/reference/servlet/getting-started.html ; password storage: https://docs.spring.io/spring-security/reference/features/authentication/password-storage.html ; redirect to HTTPS and HSTS: https://docs.spring.io/spring-security/reference/servlet/exploits/http.html
- Microsoft Entra documentation `231747abc59ae3d50c74e215c1cdd592eb980723`, Conditional Access MFA authentication-strength requirement (checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/policy-all-users-mfa-strength.md#L56-L57
- Cloudflare documentation `c896795b8e8bab68d05ae78d64c9cbcda1fdb104`, independent MFA enforced in Access without relying on the IdP (checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/access-settings/independent-mfa.mdx#L15-L24
- Authelia source `v4.39.28`, TOTP, WebAuthn security keys and Duo push factors (checked October 2026): https://github.com/authelia/authelia/blob/v4.39.28/docs/content/configuration/second-factor/introduction.md#L21-L31
- keytool (importcert, cacerts): https://docs.oracle.com/en/java/javase/21/docs/specs/man/keytool.html
- OpenJDK jdk21u `jdk-21.0.12.1-ga`, X509TrustManager interface and check methods (checked October 2026): https://github.com/openjdk/jdk21u/blob/jdk-21.0.12.1-ga/src/java.base/share/classes/javax/net/ssl/X509TrustManager.java#L31-L85
- OpenJDK jdk21u `jdk-21.0.12.1-ga`, HostnameVerifier callback and verify method (checked October 2026): https://github.com/openjdk/jdk21u/blob/jdk-21.0.12.1-ga/src/java.base/share/classes/javax/net/ssl/HostnameVerifier.java#L29-L55
- OpenJDK jdk21u `jdk-21.0.12.1-ga`, SSLContext.init trust-manager parameter (checked October 2026): https://github.com/openjdk/jdk21u/blob/jdk-21.0.12.1-ga/src/java.base/share/classes/javax/net/ssl/SSLContext.java#L296-L315
- OpenJDK jdk21u `jdk-21.0.12.1-ga`, HttpsURLConnection default and per-instance hostname verifier (checked October 2026): https://github.com/openjdk/jdk21u/blob/jdk-21.0.12.1-ga/src/java.base/share/classes/javax/net/ssl/HttpsURLConnection.java#L212-L273
- OpenJDK jdk21u `jdk-21.0.12.1-ga`, HttpsURLConnection default and per-instance SSL socket factory (checked October 2026): https://github.com/openjdk/jdk21u/blob/jdk-21.0.12.1-ga/src/java.base/share/classes/javax/net/ssl/HttpsURLConnection.java#L295-L371
- Spring Boot application properties, Actuator access, error inclusion, H2, multipart, forms, and headers (rolling documentation, checked September 2026): https://docs.spring.io/spring-boot/3.5/appendix/application-properties/index.html
- Spring Boot application properties, including spring.web.error (rolling documentation, checked September 2026): https://docs.spring.io/spring-boot/4.1/appendix/application-properties/index.html
- Spring Boot Actuator endpoints, exposure, sanitization, and security (rolling documentation, checked September 2026): https://docs.spring.io/spring-boot/3.5/reference/actuator/endpoints.html
- Spring Boot Actuator endpoints, sanitization, and moved EndpointRequest import (rolling documentation, checked September 2026): https://docs.spring.io/spring-boot/4.1/reference/actuator/endpoints.html ; sanitization: https://docs.spring.io/spring-boot/4.1/reference/actuator/endpoints.html#actuator.endpoints.sanitization
- Spring Boot management listener configuration (rolling documentation, checked September 2026): https://docs.spring.io/spring-boot/3.5/reference/actuator/monitoring.html
- Spring Boot management listener configuration (rolling documentation, checked September 2026): https://docs.spring.io/spring-boot/4.1/reference/actuator/monitoring.html
- Spring Boot web security and default-user auto-configuration (rolling documentation, checked September 2026): https://docs.spring.io/spring-boot/3.5/reference/web/spring-security.html
- Spring Boot devtools and development property defaults (rolling documentation, checked September 2026): https://docs.spring.io/spring-boot/3.5/reference/using/devtools.html
- Spring Boot devtools and development property defaults (rolling documentation, checked September 2026): https://docs.spring.io/spring-boot/4.1/reference/using/devtools.html
- Spring Boot error-inclusion options, including ON_PARAM (rolling documentation, checked September 2026): https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/autoconfigure/web/ErrorProperties.IncludeAttribute.html
- Spring Boot servlet error handling (rolling documentation, checked September 2026): https://docs.spring.io/spring-boot/3.5/reference/web/servlet.html
- Spring Boot RestClientSsl API (rolling documentation, checked September 2026): https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/autoconfigure/web/client/RestClientSsl.html
- Spring Boot 4.1.1 RestClientSsl API, moved package: https://raw.githubusercontent.com/spring-projects/spring-boot/v4.1.1/module/spring-boot-restclient/src/main/java/org/springframework/boot/restclient/autoconfigure/RestClientSsl.java
- Spring Boot REST clients and SSL helper imports (rolling documentation, checked September 2026): https://docs.spring.io/spring-boot/3.5/reference/io/rest-client.html
- Spring Boot REST clients and moved SSL helper imports (rolling documentation, checked September 2026): https://docs.spring.io/spring-boot/4.1/reference/io/rest-client.html
- Spring Framework ForwardedHeaderFilter, proxy trust boundary: https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/filter/ForwardedHeaderFilter.html
- Spring Security 6.5 HstsHeaderWriter, secure-request condition and defaults: https://docs.spring.io/spring-security/reference/6.5/api/java/org/springframework/security/web/header/writers/HstsHeaderWriter.html
- Spring Security HstsHeaderWriter, secure-request condition and defaults (rolling documentation, checked September 2026): https://docs.spring.io/spring-security/reference/api/java/org/springframework/security/web/header/writers/HstsHeaderWriter.html
- Spring Security multiple filter chains and unmatched requests: https://docs.spring.io/spring-security/reference/servlet/configuration/java.html
- Spring Security CSRF and stateless browser applications: https://docs.spring.io/spring-security/reference/features/exploits/csrf.html
- Spring Security session fixation protection and changeSessionId: https://docs.spring.io/spring-security/reference/servlet/authentication/session-management.html
- Apache Tomcat HTTP connector, form parsing and request-header limits: https://tomcat.apache.org/tomcat-10.1-doc/config/http.html
- curl manual, header input, multipart files, protocol restrictions, and transfer diagnostics (curl 7.75.0 or newer for `exitcode` and `errormsg`): https://curl.se/docs/manpage.html


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- boot41: Spring Boot (4.1.1)
- boot40: Spring Boot starter migration (4.0)
- security65: Spring Security HSTS (6.5)
- boot: Spring Boot documentation (unknown)
- boot-docs: Spring Boot documentation (rolling) (unknown)
- security: Spring Security documentation (rolling) (unknown)
- framework: Spring Framework documentation (unknown)
- jdk: JDK keytool documentation (21)
- tomcat: Tomcat HTTP connector (10.1)
- curl: curl minimum diagnostics version (7.75.0)
- jdk21u: OpenJDK jdk21u javax.net.ssl sources (jdk-21.0.12.1-ga)
- entra-docs: Microsoft Entra documentation (231747abc59ae3d50c74e215c1cdd592eb980723)
- cf-docs: Cloudflare documentation (c896795b8e8bab68d05ae78d64c9cbcda1fdb104)
- authelia-source: Authelia source (v4.39.28)

Claims (full source mapping in the JSON block below):

- tls (REASONED; boot, boot-docs): Direct HTTPS on 8443 uses PEM certificate/key or PKCS12 and TLSv1.2/TLSv1.3; older releases must confirm PEM property support.
- connector (REASONED; boot): Properties configure one HTTP or HTTPS connector; add the port-80 redirect connector in code, or let the proxy redirect.
- https-redirect (REASONED; security, security65): Spring Security 6.5+ redirectToHttps redirects insecure requests; trusted forwarded headers determine secure status behind TLS termination.
- hsts (REASONED; security65, security): Default HSTS writer runs only for secure requests; defaults are one year, includeSubDomains=true and preload=false.
- proxy-bind (REASONED; boot, boot-docs): Bind 127.0.0.1:8080 behind the TLS proxy.
- forwarding (REASONED; boot): NATIVE delegates forwarded headers to the server, FRAMEWORK uses ForwardedHeaderFilter; outside supported cloud platforms the default is NONE.
- proxy-trust (REASONED; boot, framework): Restrict Tomcat internal-proxies, strip inbound Forwarded/X-Forwarded-* at the edge and prevent direct listener bypass.
- proxy-redirect (REASONED; boot): Tomcat redirect-context-root=false preserves HTTPS redirects behind TLS termination.
- server-import (REASONED; boot-docs): ServerProperties moves from boot.autoconfigure.web in Boot 3.5 to boot.web.server.autoconfigure in Boot 4.
- default-web-auth (REASONED; boot, security, boot-docs): With starter-security and default web configuration, require authentication except Actuator health; form login, Basic, CSRF and security headers are enabled.
- custom-chain (REASONED; boot-docs, security): Any custom SecurityFilterChain replaces Boot default web and Actuator rules; unmatched requests need a fallback chain or remain unprotected.
- default-user (REASONED; boot-docs): Separate default-user auto-configuration creates user with a normally logged generated password; a custom chain alone does not remove it. Production needs deliberate authentication.
- password (REASONED; security): Use DelegatingPasswordEncoder, bcrypt by default with {bcrypt}; BCrypt strength defaults to 10 and is tuned to about one second; Argon2 v5_8 defaults are an alternative.
- cookies (REASONED; boot, boot-docs): Set secure/http-only cookies, SameSite=lax and a 30m servlet session timeout.
- login-limit (REASONED; security): Checked references document no built-in login limiter; limit at the proxy or count failures and lock local accounts.
- oidc-starter (REASONED; boot40): Boot 3.5 uses starter-oauth2-client; Boot 4 uses starter-security-oauth2-client and deprecates the old name.
- oidc (REASONED; boot, security): Configure client ID, environment-supplied secret, issuer discovery and openid/profile/email scopes with oauth2Login; without openid the login is OAuth2, not OIDC.
- mfa (REASONED; security, entra-docs, cf-docs, authelia-source): Enforce MFA at the identity provider or a fronting layer per linked guides; for example, an Entra Conditional Access policy can require an MFA authentication strength, Cloudflare Access independent MFA can enforce MFA without relying on the IdP, and Authelia supports TOTP, WebAuthn and Duo second factors. The cited pages do not establish this deployment's enforcement.
- csrf (REASONED; security): Statelessness does not remove CSRF risk for automatically attached browser cookies or Basic credentials; retain appropriate protection.
- session-fixation (REASONED; security): Default fixation protection uses changeSessionId on Servlet 3.1+ containers; keep it enabled.
- client-validation (REASONED; boot, jdk, jdk21u): Do not install trust-all TrustManager or hostname verifiers; pinned jdk21u sources document X509TrustManager's check methods, HostnameVerifier.verify, SSLContext.init's trust-manager input, and HttpsURLConnection default setters reaching later instances while per-instance setters affect one object. The whole-JVM-client reading is this guide's assessment.
- client-ca (REASONED; boot, jdk): Import an internal CA with keytool into cacerts and change its default changeit password, or configure and apply a named SSL bundle to the client.
- client-import (REASONED; boot-docs, boot41): RestClientSsl and WebClientSsl imports differ between Boot 3.5.16 and 4.1.1; apply ssl.fromBundle to the selected client.
- actuator-exposure (REASONED; boot-docs): Boot 3.5.16/4.1.1 default web exposure is health; use an explicit allowlist. Exposure, access and authorization are separate.
- management-bind (REASONED; boot-docs): Management binds 127.0.0.1:8081 separately; a distinct management address requires a distinct port and no public proxy forwarding.
- management-disable (REASONED; boot-docs): management.server.port=-1 disables management HTTP, not JMX exposure.
- sanitize (REASONED; boot-docs): env/configprops show-values default to never; sanitization does not justify exposing metadata.
- metadata-endpoints (REASONED; boot-docs): beans, mappings and threaddump expose components, routes and thread stacks.
- heapdump (REASONED; boot-docs): heapdump may expose secrets and consume resources; access defaults to none in specifically checked 3.5.16/4.1.1, and is explicitly disabled.
- loggers (REASONED; boot-docs): loggers can read/change logging levels, increasing volume and possible information disclosure.
- shutdown (REASONED; boot-docs): shutdown stops the application; access defaults to none and is explicitly disabled.
- management-auth (REASONED; boot-docs, security): The first servlet chain requires ROLE_ENDPOINT_ADMIN for all exposed Actuator endpoints including health; the second authenticates application requests. Provision identities separately.
- endpoint-import (REASONED; boot-docs): EndpointRequest moves from boot.actuate.autoconfigure.security.servlet in Boot 3.5 to boot.security.autoconfigure.actuate.web.servlet in Boot 4.
- error-message (REASONED; boot-docs): Error message inclusion defaults to never in checked releases; use server.error in Boot 3.5 and spring.web.error in Boot 4.
- error-stack (REASONED; boot-docs): Stacktrace inclusion defaults to never in checked releases, using the version-appropriate error prefix.
- error-binding (REASONED; boot-docs): Binding-error inclusion defaults to never in checked releases, using the version-appropriate error prefix.
- error-exception (REASONED; boot-docs): Exception-class inclusion defaults to false in checked releases, using the version-appropriate error prefix.
- error-policy (REASONED; boot-docs): on-param lets requesters request details; disabling whitelabel HTML alone does not protect JSON/custom/container errors.
- h2 (REASONED; boot-docs): H2 console defaults disabled in checked releases; explicitly set spring.h2.console.enabled=false.
- devtools (REASONED; boot-docs): Exclude production devtools; active development defaults enable H2 when components exist and set message/trace/binding errors to always.
- multipart-file (REASONED; boot-docs): Servlet multipart max-file-size defaults to 1MB per file in checked releases.
- multipart-request (REASONED; boot-docs): Servlet multipart max-request-size defaults to 10MB including parts and overhead in checked releases.
- form-limit (REASONED; boot-docs, tomcat): Tomcat max-http-form-post-size defaults to 2MB for form-to-parameter processing, not arbitrary request bodies.
- header-limit (REASONED; boot-docs, tomcat): max-http-request-header-size defaults to 8KB; Tomcat counts request line and all header names/values together.
- json-limit (REASONED; boot-docs, tomcat): These properties do not establish a universal JSON body limit; bound other bodies at the proxy/application and test the actual route and content type.
- verify-tls (REASONED; boot, security65, security): HTTPS must succeed without -k and show HSTS.
- verify-auth (REASONED; boot-docs): Unauthenticated /api should return 401 or a 302 login redirect.
- verify-bind (REASONED; boot-docs): Inspect every listener for loopback-only Java binding behind the proxy.
- verify-user (REASONED; boot-docs): Positive generated-password log count records generation; zero is inconclusive because logging or a configured password can hide the default account.
- verify-public-management (REASONED; boot-docs): Public origin must serve no Actuator content to anonymous or administrator identities; health-only exposure leaves other endpoints unavailable even to administrators.
- verify-management-auth (REASONED; boot-docs): On private 8081, anonymous health should get 401, non-admin 403 and admin a health response that may be 503; sensitive routes normally 404 after successful authentication.
- verify-management-port (REASONED; boot-docs): Any HTTP response on external 8081 proves reachability; corroborate failure with socket inventory and successful intended-path access.
- verify-dangerous (REASONED; boot-docs): Inspect heapdump/shutdown access=none without invoking them; exposed behavior needs an isolated fixture.
- verify-errors (REASONED; boot-docs): Controlled exception/binding markers appear with always/on-param but should disappear with production settings, including parameter requests; check JSON, HTML and custom responses after auth.
- verify-h2 (REASONED; boot-docs): Enabled console can return content or redirect; disabled console normally yields 404 after app authorization. Login/401/403 alone do not prove absence.
- verify-upload (REASONED; boot-docs): 1024-byte file must succeed; 1048577-byte file must fail for size under the 1MB policy; both succeed with raised limits. Auth, CSRF, route and transport failures are inconclusive.
- verify-credentials (REASONED; curl): Use private mode-0600 header files via stdin, valid session/CSRF headers and curl 7.75.0+ diagnostics; transport errors do not prove secure configuration.

````json
{
  "schema": 1,
  "checked": "2026-10-19",
  "documentation_checked": "2026-09",
  "body_sha256": "7c56980f6445ca589e115eee4703a75536ecf5cb2b77f85c85087e918d26e411",
  "components": {
    "boot41": {
      "name": "Spring Boot",
      "basis": "4.1.1",
      "sources": {
        "s8e261bdcd27a": "https://raw.githubusercontent.com/spring-projects/spring-boot/v4.1.1/module/spring-boot-restclient/src/main/java/org/springframework/boot/restclient/autoconfigure/RestClientSsl.java"
      }
    },
    "boot40": {
      "name": "Spring Boot starter migration",
      "basis": "4.0",
      "sources": {
        "s08143a9162b2": "https://docs.spring.io/spring-boot/4.0/reference/using/build-systems.html",
        "s0486713aa731": "https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide/e11f389f3671d1eb7fa346065410b5b1eab99c3c"
      }
    },
    "security65": {
      "name": "Spring Security HSTS",
      "basis": "6.5",
      "sources": {
        "s527bf5b95139": "https://docs.spring.io/spring-security/reference/6.5/api/java/org/springframework/security/web/header/writers/HstsHeaderWriter.html"
      }
    },
    "boot": {
      "name": "Spring Boot documentation",
      "basis": "unknown",
      "sources": {
        "s4f6aa9df744a": "https://docs.spring.io/spring-boot/how-to/webserver.html",
        "s6d0dd8e90590": "https://docs.spring.io/spring-boot/reference/features/ssl.html",
        "s1b86cf7d45f1": "https://docs.spring.io/spring-boot/reference/io/rest-client.html",
        "s81ce68041084": "https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/web/server/Cookie.html",
        "s75be5256a326": "https://docs.spring.io/spring-boot/reference/web/spring-security.html",
        "sc88333e257f0": "https://docs.spring.io/spring-boot/reference/security/oauth2.html"
      }
    },
    "boot-docs": {
      "name": "Spring Boot documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "se7aed3f6650b": "https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/web/server/Ssl.html",
        "s34f52429c110": "https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/autoconfigure/web/ServerProperties.html",
        "s6198bce672f6": "https://docs.spring.io/spring-boot/3.5/appendix/application-properties/index.html",
        "s973cb5a333ac": "https://docs.spring.io/spring-boot/3.5/reference/actuator/endpoints.html",
        "s73890facf07c": "https://docs.spring.io/spring-boot/3.5/reference/actuator/monitoring.html",
        "s8cf61ca65ae4": "https://docs.spring.io/spring-boot/3.5/reference/web/spring-security.html",
        "se8918714c2c8": "https://docs.spring.io/spring-boot/3.5/reference/using/devtools.html",
        "saea08b7576f4": "https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/autoconfigure/web/ErrorProperties.IncludeAttribute.html",
        "s6ce5733455c4": "https://docs.spring.io/spring-boot/3.5/reference/web/servlet.html",
        "s3a681db376ce": "https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/autoconfigure/web/client/RestClientSsl.html",
        "s2845cade9c1d": "https://docs.spring.io/spring-boot/3.5/reference/io/rest-client.html",
        "s61bf6b20e945": "https://docs.spring.io/spring-boot/4.1/api/java/org/springframework/boot/web/server/autoconfigure/ServerProperties.html",
        "sc24ee7294b38": "https://docs.spring.io/spring-boot/4.1/appendix/application-properties/index.html",
        "s0511290ee7a9": "https://docs.spring.io/spring-boot/4.1/reference/actuator/endpoints.html",
        "s033f98a55ba1": "https://docs.spring.io/spring-boot/4.1/reference/actuator/endpoints.html#actuator.endpoints.sanitization",
        "s1246672710d1": "https://docs.spring.io/spring-boot/4.1/reference/actuator/monitoring.html",
        "s88d377c93f63": "https://docs.spring.io/spring-boot/4.1/reference/using/devtools.html",
        "s03b9d97c1a28": "https://docs.spring.io/spring-boot/4.1/reference/io/rest-client.html"
      }
    },
    "security": {
      "name": "Spring Security documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s55e8fcd2ff11": "https://docs.spring.io/spring-security/reference/servlet/oauth2/login/core.html",
        "sae4824b03001": "https://docs.spring.io/spring-security/reference/servlet/getting-started.html",
        "sd5aebfb9d1ed": "https://docs.spring.io/spring-security/reference/features/authentication/password-storage.html",
        "s23cf30cad42c": "https://docs.spring.io/spring-security/reference/servlet/exploits/http.html",
        "s9471b4cfe0f6": "https://docs.spring.io/spring-security/reference/servlet/configuration/java.html",
        "s8859c309d60a": "https://docs.spring.io/spring-security/reference/features/exploits/csrf.html",
        "sf301a3d0645a": "https://docs.spring.io/spring-security/reference/servlet/authentication/session-management.html",
        "s6fb344722a7c": "https://docs.spring.io/spring-security/reference/api/java/org/springframework/security/web/header/writers/HstsHeaderWriter.html"
      }
    },
    "framework": {
      "name": "Spring Framework documentation",
      "basis": "unknown",
      "sources": {
        "sc25b4ff29bc9": "https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/filter/ForwardedHeaderFilter.html"
      }
    },
    "jdk": {
      "name": "JDK keytool documentation",
      "basis": "21",
      "sources": {
        "s8a504e61bc07": "https://docs.oracle.com/en/java/javase/21/docs/specs/man/keytool.html"
      }
    },
    "tomcat": {
      "name": "Tomcat HTTP connector",
      "basis": "10.1",
      "sources": {
        "s20a557a45f7a": "https://tomcat.apache.org/tomcat-10.1-doc/config/http.html"
      }
    },
    "curl": {
      "name": "curl minimum diagnostics version",
      "basis": "7.75.0",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    },
    "jdk21u": {
      "name": "OpenJDK jdk21u javax.net.ssl sources",
      "basis": "jdk-21.0.12.1-ga",
      "sources": {
        "s1379fba0b5e6": "https://github.com/openjdk/jdk21u/blob/jdk-21.0.12.1-ga/src/java.base/share/classes/javax/net/ssl/X509TrustManager.java#L31-L85",
        "s0249b6cf0853": "https://github.com/openjdk/jdk21u/blob/jdk-21.0.12.1-ga/src/java.base/share/classes/javax/net/ssl/HostnameVerifier.java#L29-L55",
        "sef5d534061ca": "https://github.com/openjdk/jdk21u/blob/jdk-21.0.12.1-ga/src/java.base/share/classes/javax/net/ssl/SSLContext.java#L296-L315",
        "sd6ea702f8bb2": "https://github.com/openjdk/jdk21u/blob/jdk-21.0.12.1-ga/src/java.base/share/classes/javax/net/ssl/HttpsURLConnection.java#L212-L273",
        "se315608f569f": "https://github.com/openjdk/jdk21u/blob/jdk-21.0.12.1-ga/src/java.base/share/classes/javax/net/ssl/HttpsURLConnection.java#L295-L371"
      }
    },
    "entra-docs": {
      "name": "Microsoft Entra documentation",
      "basis": "231747abc59ae3d50c74e215c1cdd592eb980723",
      "sources": {
        "s2c2f323edbd0": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/policy-all-users-mfa-strength.md#L56-L57"
      }
    },
    "cf-docs": {
      "name": "Cloudflare documentation",
      "basis": "c896795b8e8bab68d05ae78d64c9cbcda1fdb104",
      "sources": {
        "s7e793d13cf31": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/access-settings/independent-mfa.mdx#L15-L24"
      }
    },
    "authelia-source": {
      "name": "Authelia source",
      "basis": "v4.39.28",
      "sources": {
        "sfeb54a05c30d": "https://github.com/authelia/authelia/blob/v4.39.28/docs/content/configuration/second-factor/introduction.md#L21-L31"
      }
    }
  },
  "claims": {
    "tls": {"text": "Direct HTTPS on 8443 uses PEM certificate/key or PKCS12 and TLSv1.2/TLSv1.3; older releases must confirm PEM property support.", "components": ["boot", "boot-docs"], "sources": ["boot:s4f6aa9df744a", "boot-docs:se7aed3f6650b"], "status": "REASONED"},
    "connector": {"text": "Properties configure one HTTP or HTTPS connector; add the port-80 redirect connector in code, or let the proxy redirect.", "components": ["boot"], "sources": ["boot:s4f6aa9df744a"], "status": "REASONED"},
    "https-redirect": {"text": "Spring Security 6.5+ redirectToHttps redirects insecure requests; trusted forwarded headers determine secure status behind TLS termination.", "components": ["security", "security65"], "sources": ["security:s23cf30cad42c", "security65:s527bf5b95139"], "status": "REASONED"},
    "hsts": {"text": "Default HSTS writer runs only for secure requests; defaults are one year, includeSubDomains=true and preload=false.", "components": ["security65", "security"], "sources": ["security65:s527bf5b95139", "security:s6fb344722a7c"], "status": "REASONED"},
    "proxy-bind": {"text": "Bind 127.0.0.1:8080 behind the TLS proxy.", "components": ["boot", "boot-docs"], "sources": ["boot:s4f6aa9df744a", "boot-docs:s34f52429c110", "boot-docs:s61bf6b20e945"], "status": "REASONED"},
    "forwarding": {"text": "NATIVE delegates forwarded headers to the server, FRAMEWORK uses ForwardedHeaderFilter; outside supported cloud platforms the default is NONE.", "components": ["boot"], "sources": ["boot:s4f6aa9df744a"], "status": "REASONED"},
    "proxy-trust": {"text": "Restrict Tomcat internal-proxies, strip inbound Forwarded/X-Forwarded-* at the edge and prevent direct listener bypass.", "components": ["boot", "framework"], "sources": ["boot:s4f6aa9df744a", "framework:sc25b4ff29bc9"], "status": "REASONED"},
    "proxy-redirect": {"text": "Tomcat redirect-context-root=false preserves HTTPS redirects behind TLS termination.", "components": ["boot"], "sources": ["boot:s4f6aa9df744a"], "status": "REASONED"},
    "server-import": {"text": "ServerProperties moves from boot.autoconfigure.web in Boot 3.5 to boot.web.server.autoconfigure in Boot 4.", "components": ["boot-docs"], "sources": ["boot-docs:s34f52429c110", "boot-docs:s61bf6b20e945"], "status": "REASONED"},
    "default-web-auth": {"text": "With starter-security and default web configuration, require authentication except Actuator health; form login, Basic, CSRF and security headers are enabled.", "components": ["boot", "security", "boot-docs"], "sources": ["boot:s75be5256a326", "security:sae4824b03001", "boot-docs:s8cf61ca65ae4"], "status": "REASONED"},
    "custom-chain": {"text": "Any custom SecurityFilterChain replaces Boot default web and Actuator rules; unmatched requests need a fallback chain or remain unprotected.", "components": ["boot-docs", "security"], "sources": ["boot-docs:s8cf61ca65ae4", "security:s9471b4cfe0f6"], "status": "REASONED"},
    "default-user": {"text": "Separate default-user auto-configuration creates user with a normally logged generated password; a custom chain alone does not remove it. Production needs deliberate authentication.", "components": ["boot-docs"], "sources": ["boot-docs:s8cf61ca65ae4"], "status": "REASONED"},
    "password": {"text": "Use DelegatingPasswordEncoder, bcrypt by default with {bcrypt}; BCrypt strength defaults to 10 and is tuned to about one second; Argon2 v5_8 defaults are an alternative.", "components": ["security"], "sources": ["security:sd5aebfb9d1ed"], "status": "REASONED"},
    "cookies": {"text": "Set secure/http-only cookies, SameSite=lax and a 30m servlet session timeout.", "components": ["boot", "boot-docs"], "sources": ["boot:s81ce68041084", "boot-docs:s6198bce672f6", "boot-docs:sc24ee7294b38"], "status": "REASONED"},
    "login-limit": {"text": "Checked references document no built-in login limiter; limit at the proxy or count failures and lock local accounts.", "components": ["security"], "sources": ["security:sae4824b03001", "security:sd5aebfb9d1ed"], "status": "REASONED"},
    "oidc-starter": {"text": "Boot 3.5 uses starter-oauth2-client; Boot 4 uses starter-security-oauth2-client and deprecates the old name.", "components": ["boot40"], "sources": ["boot40:s08143a9162b2", "boot40:s0486713aa731"], "status": "REASONED"},
    "oidc": {"text": "Configure client ID, environment-supplied secret, issuer discovery and openid/profile/email scopes with oauth2Login; without openid the login is OAuth2, not OIDC.", "components": ["boot", "security"], "sources": ["boot:sc88333e257f0", "security:s55e8fcd2ff11"], "status": "REASONED"},
    "mfa": {"text": "Enforce MFA at the identity provider or a fronting layer per linked guides; for example, an Entra Conditional Access policy can require an MFA authentication strength, Cloudflare Access independent MFA can enforce MFA without relying on the IdP, and Authelia supports TOTP, WebAuthn and Duo second factors. The cited pages do not establish this deployment's enforcement.", "components": ["security", "entra-docs", "cf-docs", "authelia-source"], "sources": ["security:s55e8fcd2ff11", "entra-docs:s2c2f323edbd0", "cf-docs:s7e793d13cf31", "authelia-source:sfeb54a05c30d"], "status": "REASONED"},
    "csrf": {"text": "Statelessness does not remove CSRF risk for automatically attached browser cookies or Basic credentials; retain appropriate protection.", "components": ["security"], "sources": ["security:s8859c309d60a"], "status": "REASONED"},
    "session-fixation": {"text": "Default fixation protection uses changeSessionId on Servlet 3.1+ containers; keep it enabled.", "components": ["security"], "sources": ["security:sf301a3d0645a"], "status": "REASONED"},
    "client-validation": {"text": "Do not install trust-all TrustManager or hostname verifiers; pinned jdk21u sources document X509TrustManager's check methods, HostnameVerifier.verify, SSLContext.init's trust-manager input, and HttpsURLConnection default setters reaching later instances while per-instance setters affect one object. The whole-JVM-client reading is this guide's assessment.", "components": ["boot", "jdk", "jdk21u"], "sources": ["boot:s6d0dd8e90590", "jdk:s8a504e61bc07", "jdk21u:s1379fba0b5e6", "jdk21u:s0249b6cf0853", "jdk21u:sef5d534061ca", "jdk21u:sd6ea702f8bb2", "jdk21u:se315608f569f"], "status": "REASONED"},
    "client-ca": {"text": "Import an internal CA with keytool into cacerts and change its default changeit password, or configure and apply a named SSL bundle to the client.", "components": ["boot", "jdk"], "sources": ["boot:s6d0dd8e90590", "boot:s1b86cf7d45f1", "jdk:s8a504e61bc07"], "status": "REASONED"},
    "client-import": {"text": "RestClientSsl and WebClientSsl imports differ between Boot 3.5.16 and 4.1.1; apply ssl.fromBundle to the selected client.", "components": ["boot-docs", "boot41"], "sources": ["boot-docs:s3a681db376ce", "boot41:s8e261bdcd27a", "boot-docs:s2845cade9c1d", "boot-docs:s03b9d97c1a28"], "status": "REASONED"},
    "actuator-exposure": {"text": "Boot 3.5.16/4.1.1 default web exposure is health; use an explicit allowlist. Exposure, access and authorization are separate.", "components": ["boot-docs"], "sources": ["boot-docs:s973cb5a333ac", "boot-docs:s0511290ee7a9"], "status": "REASONED"},
    "management-bind": {"text": "Management binds 127.0.0.1:8081 separately; a distinct management address requires a distinct port and no public proxy forwarding.", "components": ["boot-docs"], "sources": ["boot-docs:s73890facf07c", "boot-docs:s1246672710d1"], "status": "REASONED"},
    "management-disable": {"text": "management.server.port=-1 disables management HTTP, not JMX exposure.", "components": ["boot-docs"], "sources": ["boot-docs:s73890facf07c", "boot-docs:s1246672710d1"], "status": "REASONED"},
    "sanitize": {"text": "env/configprops show-values default to never; sanitization does not justify exposing metadata.", "components": ["boot-docs"], "sources": ["boot-docs:s973cb5a333ac", "boot-docs:s033f98a55ba1"], "status": "REASONED"},
    "metadata-endpoints": {"text": "beans, mappings and threaddump expose components, routes and thread stacks.", "components": ["boot-docs"], "sources": ["boot-docs:s973cb5a333ac", "boot-docs:s0511290ee7a9"], "status": "REASONED"},
    "heapdump": {"text": "heapdump may expose secrets and consume resources; access defaults to none in specifically checked 3.5.16/4.1.1, and is explicitly disabled.", "components": ["boot-docs"], "sources": ["boot-docs:s6198bce672f6", "boot-docs:sc24ee7294b38", "boot-docs:s973cb5a333ac", "boot-docs:s0511290ee7a9"], "status": "REASONED"},
    "loggers": {"text": "loggers can read/change logging levels, increasing volume and possible information disclosure.", "components": ["boot-docs"], "sources": ["boot-docs:s973cb5a333ac", "boot-docs:s0511290ee7a9"], "status": "REASONED"},
    "shutdown": {"text": "shutdown stops the application; access defaults to none and is explicitly disabled.", "components": ["boot-docs"], "sources": ["boot-docs:s6198bce672f6", "boot-docs:sc24ee7294b38", "boot-docs:s973cb5a333ac", "boot-docs:s0511290ee7a9"], "status": "REASONED"},
    "management-auth": {"text": "The first servlet chain requires ROLE_ENDPOINT_ADMIN for all exposed Actuator endpoints including health; the second authenticates application requests. Provision identities separately.", "components": ["boot-docs", "security"], "sources": ["boot-docs:s973cb5a333ac", "boot-docs:s0511290ee7a9", "security:s9471b4cfe0f6"], "status": "REASONED"},
    "endpoint-import": {"text": "EndpointRequest moves from boot.actuate.autoconfigure.security.servlet in Boot 3.5 to boot.security.autoconfigure.actuate.web.servlet in Boot 4.", "components": ["boot-docs"], "sources": ["boot-docs:s973cb5a333ac", "boot-docs:s0511290ee7a9"], "status": "REASONED"},
    "error-message": {"text": "Error message inclusion defaults to never in checked releases; use server.error in Boot 3.5 and spring.web.error in Boot 4.", "components": ["boot-docs"], "sources": ["boot-docs:s6198bce672f6", "boot-docs:sc24ee7294b38"], "status": "REASONED"},
    "error-stack": {"text": "Stacktrace inclusion defaults to never in checked releases, using the version-appropriate error prefix.", "components": ["boot-docs"], "sources": ["boot-docs:s6198bce672f6", "boot-docs:sc24ee7294b38"], "status": "REASONED"},
    "error-binding": {"text": "Binding-error inclusion defaults to never in checked releases, using the version-appropriate error prefix.", "components": ["boot-docs"], "sources": ["boot-docs:s6198bce672f6", "boot-docs:sc24ee7294b38"], "status": "REASONED"},
    "error-exception": {"text": "Exception-class inclusion defaults to false in checked releases, using the version-appropriate error prefix.", "components": ["boot-docs"], "sources": ["boot-docs:s6198bce672f6", "boot-docs:sc24ee7294b38"], "status": "REASONED"},
    "error-policy": {"text": "on-param lets requesters request details; disabling whitelabel HTML alone does not protect JSON/custom/container errors.", "components": ["boot-docs"], "sources": ["boot-docs:saea08b7576f4", "boot-docs:s6ce5733455c4"], "status": "REASONED"},
    "h2": {"text": "H2 console defaults disabled in checked releases; explicitly set spring.h2.console.enabled=false.", "components": ["boot-docs"], "sources": ["boot-docs:s6198bce672f6", "boot-docs:sc24ee7294b38"], "status": "REASONED"},
    "devtools": {"text": "Exclude production devtools; active development defaults enable H2 when components exist and set message/trace/binding errors to always.", "components": ["boot-docs"], "sources": ["boot-docs:se8918714c2c8", "boot-docs:s88d377c93f63"], "status": "REASONED"},
    "multipart-file": {"text": "Servlet multipart max-file-size defaults to 1MB per file in checked releases.", "components": ["boot-docs"], "sources": ["boot-docs:s6198bce672f6", "boot-docs:sc24ee7294b38"], "status": "REASONED"},
    "multipart-request": {"text": "Servlet multipart max-request-size defaults to 10MB including parts and overhead in checked releases.", "components": ["boot-docs"], "sources": ["boot-docs:s6198bce672f6", "boot-docs:sc24ee7294b38"], "status": "REASONED"},
    "form-limit": {"text": "Tomcat max-http-form-post-size defaults to 2MB for form-to-parameter processing, not arbitrary request bodies.", "components": ["boot-docs", "tomcat"], "sources": ["boot-docs:s6198bce672f6", "boot-docs:sc24ee7294b38", "tomcat:s20a557a45f7a"], "status": "REASONED"},
    "header-limit": {"text": "max-http-request-header-size defaults to 8KB; Tomcat counts request line and all header names/values together.", "components": ["boot-docs", "tomcat"], "sources": ["boot-docs:s6198bce672f6", "boot-docs:sc24ee7294b38", "tomcat:s20a557a45f7a"], "status": "REASONED"},
    "json-limit": {"text": "These properties do not establish a universal JSON body limit; bound other bodies at the proxy/application and test the actual route and content type.", "components": ["boot-docs", "tomcat"], "sources": ["boot-docs:s6198bce672f6", "boot-docs:sc24ee7294b38", "tomcat:s20a557a45f7a"], "status": "REASONED"},
    "verify-tls": {"text": "HTTPS must succeed without -k and show HSTS.", "components": ["boot", "security65", "security"], "sources": ["boot:s4f6aa9df744a", "security65:s527bf5b95139", "security:s6fb344722a7c"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "Unauthenticated /api should return 401 or a 302 login redirect.", "components": ["boot-docs"], "sources": ["boot-docs:s8cf61ca65ae4"], "status": "REASONED", "verify": [1]},
    "verify-bind": {"text": "Inspect every listener for loopback-only Java binding behind the proxy.", "components": ["boot-docs"], "sources": ["boot-docs:s34f52429c110", "boot-docs:s61bf6b20e945"], "status": "REASONED", "verify": [1]},
    "verify-user": {"text": "Positive generated-password log count records generation; zero is inconclusive because logging or a configured password can hide the default account.", "components": ["boot-docs"], "sources": ["boot-docs:s8cf61ca65ae4"], "status": "REASONED", "verify": [1]},
    "verify-public-management": {"text": "Public origin must serve no Actuator content to anonymous or administrator identities; health-only exposure leaves other endpoints unavailable even to administrators.", "components": ["boot-docs"], "sources": ["boot-docs:s973cb5a333ac", "boot-docs:s0511290ee7a9"], "status": "REASONED", "verify": [2]},
    "verify-management-auth": {"text": "On private 8081, anonymous health should get 401, non-admin 403 and admin a health response that may be 503; sensitive routes normally 404 after successful authentication.", "components": ["boot-docs"], "sources": ["boot-docs:s973cb5a333ac", "boot-docs:s0511290ee7a9"], "status": "REASONED", "verify": [3]},
    "verify-management-port": {"text": "Any HTTP response on external 8081 proves reachability; corroborate failure with socket inventory and successful intended-path access.", "components": ["boot-docs"], "sources": ["boot-docs:s73890facf07c", "boot-docs:s1246672710d1"], "status": "REASONED", "verify": [4]},
    "verify-dangerous": {"text": "Inspect heapdump/shutdown access=none without invoking them; exposed behavior needs an isolated fixture.", "components": ["boot-docs"], "sources": ["boot-docs:s6198bce672f6", "boot-docs:sc24ee7294b38", "boot-docs:s973cb5a333ac", "boot-docs:s0511290ee7a9"], "status": "REASONED"},
    "verify-errors": {"text": "Controlled exception/binding markers appear with always/on-param but should disappear with production settings, including parameter requests; check JSON, HTML and custom responses after auth.", "components": ["boot-docs"], "sources": ["boot-docs:s6198bce672f6", "boot-docs:sc24ee7294b38", "boot-docs:saea08b7576f4", "boot-docs:s6ce5733455c4"], "status": "REASONED", "verify": [5]},
    "verify-h2": {"text": "Enabled console can return content or redirect; disabled console normally yields 404 after app authorization. Login/401/403 alone do not prove absence.", "components": ["boot-docs"], "sources": ["boot-docs:s6198bce672f6", "boot-docs:sc24ee7294b38", "boot-docs:se8918714c2c8", "boot-docs:s88d377c93f63"], "status": "REASONED", "verify": [6]},
    "verify-upload": {"text": "1024-byte file must succeed; 1048577-byte file must fail for size under the 1MB policy; both succeed with raised limits. Auth, CSRF, route and transport failures are inconclusive.", "components": ["boot-docs"], "sources": ["boot-docs:s6198bce672f6", "boot-docs:sc24ee7294b38"], "status": "REASONED", "verify": [7]},
    "verify-credentials": {"text": "Use private mode-0600 header files via stdin, valid session/CSRF headers and curl 7.75.0+ diagnostics; transport errors do not prove secure configuration.", "components": ["curl"], "sources": ["curl:s2b2686afaf41"], "status": "REASONED", "verify": [2, 3, 4, 5, 6, 7]}
  }
}
````
<!-- version-basis:end -->
