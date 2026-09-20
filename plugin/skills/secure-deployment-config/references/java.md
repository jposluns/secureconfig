# Spring Boot: TLS and authentication

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

The `issuer-uri` drives OpenID Connect discovery, and the `openid` scope is what makes the registration an OpenID Connect login that returns an ID token; without it the login is plain OAuth2. Allowlist and token checks are in [oidc-integration.md](oidc-integration.md), providers in [identity-providers.md](identity-providers.md). MFA: enforce it at the identity provider, or front the app per [mfa.md](mfa.md).

Do not disable CSRF protection merely because an API is "stateless". Browsers can automatically attach authentication cookies or HTTP Basic credentials, so those requests remain vulnerable to CSRF. Decide from how clients supply credentials, not from whether the application stores a session. See Spring Security's [stateless-browser qualification](https://docs.spring.io/spring-security/reference/features/exploits/csrf.html#csrf-and-stateless-browser-applications).

Spring Security's default session fixation protection uses `changeSessionId` on Servlet 3.1 and newer containers: an existing session receives a new ID on authentication. Keep this protection enabled. See [session fixation protection](https://docs.spring.io/spring-security/reference/servlet/authentication/session-management.html#understanding-session-fixation-attack-protection).

## 4. Client-side TLS discipline

- Never install a trust-all `TrustManager` or hostname verifier, and never copy one from an answer that "fixes" a certificate error; it disables validation for the whole JVM client.
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

## 8. Verify

```bash
curl -q -g -sI --noproxy '*' https://example.com/        # succeeds without -k; shows Strict-Transport-Security
curl -q -g -sS --noproxy '*' -o /dev/null -w '%{http_code}\n' https://example.com/api   # 401, or 302 to the login page, without credentials
ss -tlnp   # read every listener; java: behind a proxy: 127.0.0.1 only
grep -c "Using generated security password" app.log   # a positive count records password generation; zero does not prove the default user is absent
```

A zero generated-password log count is inconclusive: logging may suppress the message, and setting `spring.security.user.password` avoids password generation while retaining the default account. Check the deployed authentication configuration and exercise the intended login method. A custom `SecurityFilterChain` alone does not remove default-user auto-configuration, and OAuth2/OIDC does not require introducing a local `UserDetailsService`. See [Boot's security auto-configuration rules](https://docs.spring.io/spring-boot/3.5/reference/web/spring-security.html).

The following deployment checks are **reasoned, not demonstrated**. The authoring environment has no runnable Spring Boot fixture, no Maven or Gradle executable, and no container runtime; its filesystem is read-only and network access is restricted. Shell syntax and negative placeholder-guard cases were checked locally. These deployment demonstrations are tracked in the project backlog (`TODO.md`).

Paste each guarded block whole and substitute inside the single quotes. Supply URLs without a trailing slash where the block appends a path, and without existing query parameters where it appends a query. These blocks require curl 7.75.0 or newer for `exitcode` and `errormsg`. A DNS error, TLS failure, or timeout is not proof that an endpoint is securely configured; inspect the error and confirm the intended service and network path.

For authenticated requests, prepare `./java-verify-auth.headers` as a private, mode `0600` file containing the actual request headers for a test identity, one header per line. Use the application's authentication method, such as its session cookie or an accepted authorization header. For uploads, include the matching session and valid CSRF header where required. The blocks pass that file to curl through stdin, keeping credential values out of command arguments. Protect and remove the file after testing. Curl documents [header input and transfer diagnostics](https://curl.se/docs/manpage.html).

### Management reachability and authorization

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

### Error-body leakage

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

### H2 console absence

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

### Over-limit upload

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
- Spring Boot 3.5.16 javadoc, Ssl: https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/web/server/Ssl.html
- Spring Boot 3.5.16 javadoc, ServerProperties (address, forwardHeadersStrategy, servlet.session): https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/autoconfigure/web/ServerProperties.html
- Spring Boot 4.1.1 javadoc, ServerProperties (moved package): https://docs.spring.io/spring-boot/4.1/api/java/org/springframework/boot/web/server/autoconfigure/ServerProperties.html
- Spring Boot javadoc, session Cookie: https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/web/server/Cookie.html ; Spring Boot and Spring Security defaults: https://docs.spring.io/spring-boot/reference/web/spring-security.html
- Spring Boot OAuth2 client properties: https://docs.spring.io/spring-boot/reference/security/oauth2.html ; Spring Security OAuth2 login: https://docs.spring.io/spring-security/reference/servlet/oauth2/login/core.html
- Spring Boot 4.0 starters and deprecated OAuth2 client starter name: https://docs.spring.io/spring-boot/4.0/reference/using/build-systems.html
- Spring Boot 4.0 migration guide, deprecated starters: https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide
- Spring Security getting started (Boot defaults): https://docs.spring.io/spring-security/reference/servlet/getting-started.html ; password storage: https://docs.spring.io/spring-security/reference/features/authentication/password-storage.html ; redirect to HTTPS and HSTS: https://docs.spring.io/spring-security/reference/servlet/exploits/http.html
- keytool (importcert, cacerts): https://docs.oracle.com/en/java/javase/21/docs/specs/man/keytool.html
- Spring Boot 3.5.16 application properties, Actuator access, error inclusion, H2, multipart, forms, and headers: https://docs.spring.io/spring-boot/3.5/appendix/application-properties/index.html
- Spring Boot 4.1.1 application properties, including spring.web.error: https://docs.spring.io/spring-boot/4.1/appendix/application-properties/index.html
- Spring Boot 3.5.16 Actuator endpoints, exposure, sanitization, and security: https://docs.spring.io/spring-boot/3.5/reference/actuator/endpoints.html
- Spring Boot 4.1.1 Actuator endpoints, sanitization, and moved EndpointRequest import: https://docs.spring.io/spring-boot/4.1/reference/actuator/endpoints.html ; sanitization: https://docs.spring.io/spring-boot/4.1/reference/actuator/endpoints.html#actuator.endpoints.sanitization
- Spring Boot 3.5.16 management listener configuration: https://docs.spring.io/spring-boot/3.5/reference/actuator/monitoring.html
- Spring Boot 4.1.1 management listener configuration: https://docs.spring.io/spring-boot/4.1/reference/actuator/monitoring.html
- Spring Boot 3.5.16 web security and default-user auto-configuration: https://docs.spring.io/spring-boot/3.5/reference/web/spring-security.html
- Spring Boot 3.5.16 devtools and development property defaults: https://docs.spring.io/spring-boot/3.5/reference/using/devtools.html
- Spring Boot 4.1.1 devtools and development property defaults: https://docs.spring.io/spring-boot/4.1/reference/using/devtools.html
- Spring Boot 3.5.16 error-inclusion options, including ON_PARAM: https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/autoconfigure/web/ErrorProperties.IncludeAttribute.html
- Spring Boot 3.5.16 servlet error handling: https://docs.spring.io/spring-boot/3.5/reference/web/servlet.html
- Spring Boot 3.5.16 RestClientSsl API: https://docs.spring.io/spring-boot/3.5/api/java/org/springframework/boot/autoconfigure/web/client/RestClientSsl.html
- Spring Boot 4.1.1 RestClientSsl API, moved package: https://docs.spring.io/spring-boot/api/java/org/springframework/boot/restclient/autoconfigure/RestClientSsl.html
- Spring Boot 3.5.16 REST clients and SSL helper imports: https://docs.spring.io/spring-boot/3.5/reference/io/rest-client.html
- Spring Boot 4.1.1 REST clients and moved SSL helper imports: https://docs.spring.io/spring-boot/4.1/reference/io/rest-client.html
- Spring Framework ForwardedHeaderFilter, proxy trust boundary: https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/web/filter/ForwardedHeaderFilter.html
- Spring Security 6.5 HstsHeaderWriter, secure-request condition and defaults: https://docs.spring.io/spring-security/reference/6.5/api/java/org/springframework/security/web/header/writers/HstsHeaderWriter.html
- Spring Security 7.1 HstsHeaderWriter, secure-request condition and defaults: https://docs.spring.io/spring-security/reference/api/java/org/springframework/security/web/header/writers/HstsHeaderWriter.html
- Spring Security multiple filter chains and unmatched requests: https://docs.spring.io/spring-security/reference/servlet/configuration/java.html
- Spring Security CSRF and stateless browser applications: https://docs.spring.io/spring-security/reference/features/exploits/csrf.html
- Spring Security session fixation protection and changeSessionId: https://docs.spring.io/spring-security/reference/servlet/authentication/session-management.html
- Apache Tomcat HTTP connector, form parsing and request-header limits: https://tomcat.apache.org/tomcat-10.1-doc/config/http.html
- curl manual, header input, multipart files, protocol restrictions, and transfer diagnostics: https://curl.se/docs/manpage.html
