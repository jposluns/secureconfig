# PHP and Laravel: TLS and authentication

PHP normally runs behind a web server (Apache with php-fpm or mod_php, nginx or Caddy with php-fpm), so TLS terminates there: follow [apache.md](apache.md), [nginx.md](nginx.md), or [caddy.md](caddy.md) with a certificate from [free-certificates.md](free-certificates.md). The PHP-specific exposures are the php-fpm FastCGI socket (the PHP manual: "An exposed FastCGI endpoint allows arbitrary code execution"), session cookies that PHP ships without `Secure`, `HttpOnly`, or `SameSite` (all three default off), `APP_DEBUG=true` left on in production, and cURL calls with certificate checks turned off.

## 1. Keep php-fpm private

`listen` is mandatory per pool. Prefer a Unix socket when the web server is on the same host; with TCP, list the allowed clients, because `listen.allowed_clients` is unset by default and then accepts any address. In containers, never publish the FPM port on the host.

```ini
; /etc/php/*/fpm/pool.d/www.conf
listen = /run/php/php-fpm.sock        ; access controlled by listen.owner, listen.group, listen.mode (default 0660)
; listen = 127.0.0.1:9000 plus listen.allowed_clients = 127.0.0.1 for the TCP alternative, loopback only
```

## 2. Plain PHP: sessions, passwords, rate limiting

```ini
session.cookie_secure = 1        ; default 0
session.cookie_httponly = 1      ; default 0
session.cookie_samesite = Lax    ; default "" (no attribute); Lax or Strict
session.use_strict_mode = 1      ; default 0; the manual calls enabling it "mandatory for general session security"
```

Call `session_regenerate_id()` after login and on privilege change. Its `delete_old_session` parameter defaults to `false`; the manual advises against destroying the old session immediately (unstable networks, hijack detection), so expire it with a timestamp instead.

Hash with `password_hash($password, PASSWORD_DEFAULT)` (bcrypt at the time of writing; `PASSWORD_ARGON2ID` needs PHP built with Argon2), check with `password_verify()`, and upgrade old hashes when `password_needs_rehash()` says so. `PASSWORD_DEFAULT` is designed to change over time, so store the hash in a column that can grow past 60 bytes (the manual suggests 255). Plain PHP has no login rate limiter; apply one at the proxy or with fail2ban per [authentication.md](authentication.md). MFA in plain PHP means a TOTP library or an identity layer in front, per [mfa.md](mfa.md).

## 3. Laravel

```ini
APP_ENV=production              # .env stays out of source control
APP_DEBUG=false                 # true in production exposes configuration values to end users
APP_URL=https://app.example.com
APP_KEY=                        # php artisan key:generate; list old keys in APP_PREVIOUS_KEYS when rotating
SESSION_SECURE_COOKIE=true      # config/session.php 'secure' has no default
SESSION_HTTP_ONLY=true          # default true
SESSION_SAME_SITE=lax           # default lax; strict for admin-only apps
```

Behind a proxy, name it in `bootstrap/app.php` (Laravel 12.x docs; check the docs for your version) so `url()`, `request()->secure()`, and secure cookies see HTTPS:

```php
->withMiddleware(function (Middleware $middleware): void {
    $middleware->trustProxies(at: ['127.0.0.1', '10.0.0.0/8']);   // '*' only when the app is unreachable except through the proxy
})
```

Force HTTPS in generated URLs with `URL::forceHttps()` (or `URL::forceScheme('https')`) in a service provider's `boot()` method. Passwords: `Hash::make()` and `Hash::check()` use bcrypt by default; `HASH_DRIVER=argon2id` switches the driver, `Hash::needsRehash()` indicates whether a hash needs rehashing, and `Hash::check()` rejects hashes made with a different algorithm unless `HASH_VERIFY=false`. Rate-limit the login route in `AppServiceProvider::boot()` and attach it with the `throttle` middleware:

```php
RateLimiter::for('login', fn (Request $request) => Limit::perMinute(5)->by($request->email.$request->ip()));
Route::post('/login', [AuthController::class, 'store'])->middleware('throttle:login');   // attach the limiter to your real login route and handler
```

The 12.x starter kits (React, Vue, Svelte, Livewire) authenticate through Laravel Fortify, which throttles login by username plus IP, regenerates the session ID on login, and ships TOTP two-factor authentication with recovery codes: `Features::twoFactorAuthentication(['confirm' => true, 'confirmPassword' => true])` in `config/fortify.php`. Fortify alone (`composer require laravel/fortify`, `php artisan fortify:install`) gives the same backend without views. Laravel Socialite handles OAuth login for Google, GitHub, GitLab, Slack, and others; OpenID Connect providers come through the community Socialite Providers packages. After the callback, apply the allowlist and token checks in [oidc-integration.md](oidc-integration.md), and keep the `redirect` in `config/services.php` on `https://`.

For Laravel 12.x production deployments, never commit the plaintext `.env` file. After supplying the production configuration, build the configuration and route caches as part of deployment. Once configuration is cached, Laravel does not load `.env`; call `env()` only in configuration files and read application settings through `config()`. Rebuild the caches when their inputs change. [Configuration](https://laravel.com/framework/docs/12.x/configuration), [deployment](https://laravel.com/framework/docs/12.x/deployment).

```bash
php artisan config:cache
php artisan route:cache
```

Restrict accepted hostnames at the web server. Laravel accepts arbitrary `Host` headers by default; enable `TrustHosts` as an additional check. Add this statement inside the existing `withMiddleware` callback, alongside `trustProxies`, and substitute the application's hostname in the anchored regular expression. `subdomains: false` prevents automatic trust of subdomains of the application URL. [Trusted hosts](https://laravel.com/framework/docs/12.x/requests#configuring-trusted-hosts).

```php
$middleware->trustHosts(at: ['^app\.example\.com$'], subdomains: false);
```

Keep Telescope and Debugbar out of the production installation. Use Telescope's documented local-only installation, including conditional provider registration, so production does not attempt to load an omitted development dependency. Debugbar's maintainer also recommends omitting it from production. [Telescope local-only installation](https://laravel.com/framework/docs/12.x/telescope#local-only-installation), [Debugbar](https://github.com/fruitcake/laravel-debugbar).

## 4. Client-side TLS discipline

```php
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true);                     // the default; never set false
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 2);                        // the default; keep 2 in production
curl_setopt($ch, CURLOPT_CAINFO, '/etc/ssl/certs/internal-ca.pem'); // internal CA instead of disabling checks
```

## 5. php.ini production error and banner hardening

These settings target PHP 8.x. Defaults below mean PHP's built-in defaults; distribution packages, templates, and deployment overrides can differ. Configure the `php.ini` used by the web SAPI, then reload the relevant service. This is the plain-PHP counterpart to Laravel's `APP_DEBUG=false`.

```ini
display_errors = Off          ; built-in default On
display_startup_errors = Off  ; default On since PHP 8.0.0; previously Off
log_errors = On               ; built-in default Off
error_log = /var/log/php/app-error.log
error_reporting = E_ALL       ; built-in default since PHP 8.0.0
expose_php = Off              ; built-in default On
```

`error_reporting` selects which diagnostics PHP reports; it does not decide whether they reach the HTTP response. Keep reporting enabled while directing errors into protected logs. Pre-create the example log destination outside the document root, make it writable by the PHP worker identity, restrict access to that identity and authorized operators, and arrange rotation. An unset `error_log` uses the SAPI's logger. Configure error display before requests execute; an `ini_set()` inside a script cannot protect against a fatal error that prevents that statement from running. [PHP error configuration](https://www.php.net/manual/en/errorfunc.configuration.php).

Use the bundled `php.ini-production` as a starting point, then review its actual settings. For example, PHP 8.4's template disables both display settings and enables logging, but uses `E_ALL & ~E_DEPRECATED` and leaves `expose_php` enabled. The explicit settings above retain all diagnostic levels in logs and disable PHP's banner. [PHP 8.4 production template](https://raw.githubusercontent.com/php/php-src/d313ad6098430f4e61f0121a9e7ab392d195e4e4/php.ini-production).

`expose_php=Off` suppresses PHP's own `X-Powered-By: PHP/...` header. It does not remove headers added elsewhere or make the application unidentifiable. [Hiding PHP](https://www.php.net/manual/en/security.hiding.php).

## 6. Code execution, inclusion, and upload-directory surface

For PHP 8.x, consider an application-tested `disable_functions` list only where these process-launching functions are unnecessary. Its default is an empty list. It affects internal functions only; since PHP 8.0, disabling a function removes its definition and allows userland to redefine that name. This reduces available functionality but is not a security boundary. [PHP core directives](https://www.php.net/manual/en/ini.core.php#ini.disable-functions).

The first two settings below are conditional on application compatibility. Retain the third setting:

```ini
disable_functions = exec,system,passthru,shell_exec,proc_open,popen
allow_url_fopen = Off
allow_url_include = Off
```

`allow_url_fopen` defaults to On and enables URL-aware file wrappers; disable it where unnecessary. `allow_url_include` defaults to Off and has been deprecated since PHP 7.4. It governs URL-wrapper use by `include`, `include_once`, `require`, and `require_once`, and requires `allow_url_fopen` to be enabled. These switches are not a general network-egress policy. [Filesystem and streams configuration](https://www.php.net/manual/en/filesystem.configuration.php).

`open_basedir` defaults to NULL, with no directory restriction. If used, allow every required application, dependency, session, and temporary directory, and test the result. It disables the realpath cache and is an additional restriction, not filesystem isolation. PHP 8.3 additionally rejects `..` components when changing this setting at runtime. Retain operating-system permissions and application isolation. [PHP core directives](https://www.php.net/manual/en/ini.core.php#ini.open-basedir).

In the FPM pool configuration, restrict the main script extensions:

```ini
security.limit_extensions = .php
```

The PHP 8.x FPM default is `.php .phar`. Restricting it to `.php` still permits an uploaded `.php` file if the web server sends that file to FPM. [FPM configuration](https://www.php.net/manual/en/install.fpm.configuration.php).

Never execute PHP from upload or other writable data directories. Store such data outside the document root where possible, and enforce the exclusion in the actual web-server handler mappings. Any publicly served upload directory must serve permitted content without dispatching it to PHP; include aliases and symbolic links in that review. Keep executable application code separate from writable data. See [apache.md](apache.md), [nginx.md](nginx.md), and [caddy.md](caddy.md).

For Laravel 12.x, the default local disk uses `storage/app/private`; the public disk uses `storage/app/public` and can be exposed through `public/storage`. That public link does not itself prevent PHP execution: the web-server rules must cover it. [Laravel file storage](https://laravel.com/framework/docs/12.x/filesystem).

## 7. Upload and request limits

Set finite limits appropriate to the application and test legitimate requests near each limit. The following retains PHP 8.x's built-in size, count, memory, and execution defaults, while explicitly choosing 60 seconds for input parsing:

```ini
upload_max_filesize = 2M
post_max_size = 8M
max_file_uploads = 20
memory_limit = 128M
max_input_vars = 1000
max_execution_time = 30
max_input_time = 60
```

`upload_max_filesize` limits each uploaded file; `post_max_size` limits the complete POST body and must exceed it, allowing room for other fields and multipart overhead. A count limit of 20 does not mean twenty maximum-sized files fit into an 8M request. If POST data exceeds `post_max_size`, PHP leaves `$_POST` and `$_FILES` empty; handle that condition as a rejected request. `memory_limit` bounds a script's allocation and should generally exceed `post_max_size`; `-1` removes that memory limit. [PHP core directives](https://www.php.net/manual/en/ini.core.php).

`max_input_vars=1000` applies separately to GET, POST, and COOKIE input; excess variables generate a warning and are truncated. It is not a general JSON-body limit. `max_execution_time` defaults to 30 seconds for web execution and 0 for CLI. It is not a portable wall-clock deadline: accounting depends on the platform and build and can exclude I/O waits. The built-in `max_input_time` default is `-1`, meaning use `max_execution_time`; 0 permits unlimited input-parsing time. The production template sets it to 60. [PHP execution and input limits](https://www.php.net/manual/en/info.configuration.php), [production template](https://raw.githubusercontent.com/php/php-src/d313ad6098430f4e61f0121a9e7ab392d195e4e4/php.ini-production).

Uploads also consume input-processing time. Test slow and multiple-file uploads, and coordinate these values with the web server's request-size and timeout limits. These settings bound individual requests; they do not replace capacity limits or rate limiting. [PHP upload pitfalls](https://www.php.net/manual/en/features.file-upload.common-pitfalls.php).

For FPM, choose a finite request termination limit. This example uses 60 seconds as an application policy, not a vendor default:

```ini
; FPM pool configuration, not php.ini
request_terminate_timeout = 60s
request_terminate_timeout_track_finished = yes
```

`request_terminate_timeout` defaults to 0, disabled, and kills the worker when the request exceeds the limit. Ordinarily it stops applying after `fastcgi_finish_request()` or during shutdown processing; `request_terminate_timeout_track_finished=yes`, default no, extends it to those phases. Test applications that perform work after sending the response. [FPM configuration](https://www.php.net/manual/en/install.fpm.configuration.php).

## 8. Session storage and lifetime beyond cookie flags

These settings govern PHP 8.x native sessions. Laravel's session subsystem uses `config/session.php`; do not assume native PHP session directives configure Laravel's session storage or lifetime.

```ini
session.gc_maxlifetime = 1440
session.cookie_lifetime = 0
session.use_only_cookies = 1
session.save_path = "/var/lib/php/app-sessions"
```

The first three values retain PHP's built-in defaults. `session.gc_maxlifetime` makes session data eligible for collection after 1440 seconds, 24 minutes. `session.cookie_lifetime=0` creates a browser-session cookie. `session.use_only_cookies=1` keeps session IDs out of GET and POST parameters; retain it. Disabling it is deprecated from PHP 8.4. [Session configuration](https://www.php.net/manual/en/session.configuration.php).

Garbage collection is probabilistic by default and is not an authentication-expiry guarantee. Enforce idle and absolute expiry using application timestamps, and arrange reliable cleanup of expired storage. Applications sharing a save location can have their data removed according to another application's shorter collection lifetime. [Session security](https://www.php.net/manual/en/session.security.ini.php), [session configuration](https://www.php.net/manual/en/session.configuration.php).

For the default `files` save handler, pre-create a private directory outside the document root for each application, writable by its PHP identity. A directory mode of 0700 is appropriate for a dedicated runtime account; session files default to 0600. Separate untrusted applications by runtime identity as well as path. Avoid a shared, world-readable session directory. [Session configuration](https://www.php.net/manual/en/session.configuration.php#ini.session.save-path).

PHP 8.x's built-in `session.sid_length` and `session.sid_bits_per_character` defaults are 32 and 4. Changing either away from its default is deprecated from PHP 8.4. Do not add new tuning overrides on those versions. Older templates differ: PHP 8.3's production template sets 26 and 5, so review inherited configuration during upgrades. [Session configuration](https://www.php.net/manual/en/session.configuration.php), [PHP 8.3 production template](https://raw.githubusercontent.com/php/php-src/b94f9f68a610e0fca5f2fea5bfa7c7d6d3d5a847/php.ini-production).

## Verify

**REASONED: deployment checks have not been demonstrated.** The authoring environment has no PHP or PHP-FPM runtime, no Docker or Podman, and no supplied PHP/Laravel deployment. The listener, TLS, cookie, authentication, banner, and error-disclosure checks require a real deployment. Demonstration debt is tracked as `PHP-VERIFY` in `TODO.md`.

Paste each guarded block whole. Substitute a full HTTPS URL inside the single quotes on its `set --` line; use a URL without a literal apostrophe or embedded credentials. The fixed `app.example.com` examples are illustrations. For deployment requests, use the guarded blocks with the application's actual URL. Curl's `http`, `exit`, and `err` write-out fields require curl 7.75.0 or later. The trailing `|| true` keeps a failed probe from ending the shell; it does not indicate success.

For the protected-route check, confirm the same route returns the expected protected content to an authorized session. In an isolated exposed-state test, removing the authentication requirement must make that content accessible anonymously; restoring it must produce the documented denial or login redirect. A missing route or an unrelated error is not evidence of authentication.

```bash
ss -xlnp   # read every listener; php-fpm: Unix socket; with TCP, ss -tlnp shows 127.0.0.1:9000 only
curl -q -g --noproxy '*' -sI https://app.example.com/                             # succeeds without -k
curl -q -g --noproxy '*' -sI https://app.example.com/login | grep -i set-cookie   # secure; httponly; samesite=lax
```

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_PROTECTED_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the full HTTPS URL inside the quotes above; not probing" ;;
    *)
      curl -q -g --noproxy '*' -sS -i --connect-timeout 5 --max-time 20 \
        -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' -- "$1" || true
      # This request sends no session cookie. Expect 401 or 403, or a redirect whose Location is the login
      # page, and no protected content in the response; an anonymous session Set-Cookie in the response is
      # permitted (Laravel's StartSession issues one even for a denied request). An unrelated canonical
      # redirect (for example to a trailing slash) is not a login redirect; a 200 carrying protected content
      # is a failure. TLS and cookie flags say nothing about whether a route actually refuses an
      # unauthenticated request.
      ;;
  esac
) || true
```

**REASONED: inspect the loaded configuration locally.** No PHP executable was available in the authoring environment. On the deployment host, these commands identify CLI configuration and show the production error settings. [PHP command-line options](https://www.php.net/manual/en/features.commandline.options.php).

```bash
php --ini
php -i | grep -E '^(display_errors|display_startup_errors|log_errors|error_log|error_reporting|expose_php) =>'
php -r 'echo "E_ALL=", E_ALL, PHP_EOL;'
```

Expect `display_errors=Off`, `display_startup_errors=Off`, `log_errors=On`, the intended protected `error_log`, `expose_php=Off`, and `error_reporting` equal to the installed version's `E_ALL`. PHP's diagnostic values can change between versions, so compare against the printed constant rather than a copied integer. CLI inspection does not establish FPM or Apache's effective configuration: inspect that SAPI's loaded files and overrides separately, including the FPM pool settings. Do not publish a `phpinfo()` endpoint.

**REASONED: banner and native PHP error disclosure.** No web SAPI or deployment was available. In an isolated deployment matching production, temporarily serve this controlled fixture through the intended PHP handler and proxy. Use PHP's built-in error handler, without framework bootstrapping or application error-handler overrides. Restrict access to the test operator and remove the fixture afterwards. The fixed warning text contains no secret. [PHP `trigger_error()`](https://www.php.net/manual/en/function.trigger-error.php).

```php
<?php
trigger_error('SECURECONFIG_PHP_ERROR_CANARY', E_USER_WARNING);
echo "SECURECONFIG_PHP_REACHED\n";
```

First inspect the fixture's response headers:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_FIXTURE_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the full HTTPS fixture URL inside the quotes above; not probing" ;;
    *)
      curl -q -g --noproxy '*' -sS --connect-timeout 5 --max-time 20 \
        -D - -o /dev/null \
        -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' -- "$1" || true
      ;;
  esac
) || true
```

With `expose_php=On`, the exposed-state response is expected to contain `X-Powered-By: PHP/...` unless another layer strips it. With `expose_php=Off`, it must be absent. Require a successful transfer and the fixture's expected HTTP 200 response. If the proxy strips the header in both states, this checks the externally visible response only; attribute the PHP setting through the active SAPI configuration. [PHP banner behavior](https://www.php.net/manual/en/security.hiding.php).

Then inspect the body from the same fixture URL:

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_FIXTURE_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the full HTTPS fixture URL inside the quotes above; not probing" ;;
    *)
      curl -q -g --noproxy '*' -sS --connect-timeout 5 --max-time 20 \
        -i \
        -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' -- "$1" || true
      ;;
  esac
) || true
```

In the isolated exposed state, `display_errors=On` with `error_reporting=E_ALL` should disclose `SECURECONFIG_PHP_ERROR_CANARY` in the response. After applying section 5, the HTTP 200 body must contain `SECURECONFIG_PHP_REACHED` without the warning marker or PHP diagnostics, while the protected log receives the warning marker for that request. A blank response, redirect, 404, failed transfer, or missing log entry does not satisfy this check. This fixture tests a runtime warning; it does not exercise startup or parse errors. [PHP error configuration](https://www.php.net/manual/en/errorfunc.configuration.php).

For Laravel 12.x, repeat the body probe against a controlled route that raises an exception with a distinctive, non-secret message. In an isolated deployment, compare `APP_DEBUG=true` with `APP_DEBUG=false`, rebuilding cached configuration after each change. The protected state must show a generic error response without the exception message, trace, or configuration values; confirm the matching exception in the protected application log. The native PHP fixture alone does not establish Laravel's framework error behavior. [Laravel debug mode](https://laravel.com/framework/docs/12.x/deployment#debug-mode).

## Sources (checked September 2026)

- PHP FPM configuration (`listen`, `listen.allowed_clients`, `listen.owner`): https://www.php.net/manual/en/install.fpm.configuration.php
- PHP session runtime configuration: https://www.php.net/manual/en/session.configuration.php
- PHP `session_regenerate_id()`: https://www.php.net/manual/en/function.session-regenerate-id.php
- PHP `password_hash()`: https://www.php.net/manual/en/function.password-hash.php
- PHP cURL constants (`CURLOPT_SSL_VERIFYPEER`, `CURLOPT_SSL_VERIFYHOST`, `CURLOPT_CAINFO`): https://www.php.net/manual/en/curl.constants.php
- Laravel 12.x encryption (`APP_KEY`, `key:generate`, `APP_PREVIOUS_KEYS`): https://laravel.com/framework/docs/12.x/encryption
- Laravel 12.x requests (trusted proxies, trusted hosts): https://laravel.com/framework/docs/12.x/requests
- Laravel 12.x `config/session.php` defaults: https://github.com/laravel/laravel/blob/f6b2e79bdbfc5bf4a37ad16466cc06ad79cc9e8f/config/session.php
- Laravel 12.x `UrlGenerator::forceHttps()` and `forceScheme()`: https://api.laravel.com/docs/12.x/Illuminate/Routing/UrlGenerator.html
- Laravel 12.x hashing: https://laravel.com/framework/docs/12.x/hashing
- Laravel 12.x routing (rate limiting): https://laravel.com/framework/docs/12.x/routing
- Laravel 12.x starter kits (Fortify, two-factor, rate limiting): https://laravel.com/framework/docs/12.x/starter-kits
- Laravel 12.x Fortify: https://laravel.com/framework/docs/12.x/fortify
- Laravel 12.x Socialite: https://laravel.com/framework/docs/12.x/socialite
- Laravel 12.x deployment (nginx example, `APP_DEBUG`): https://laravel.com/framework/docs/12.x/deployment
- PHP 8.x error configuration (`display_errors`, `display_startup_errors`, `log_errors`, `error_log`, `error_reporting`): https://www.php.net/manual/en/errorfunc.configuration.php
- PHP core directives (`disable_functions`, `open_basedir`, memory and upload limits): https://www.php.net/manual/en/ini.core.php
- PHP hiding and `expose_php`: https://www.php.net/manual/en/security.hiding.php
- PHP 8.4 bundled production template: https://raw.githubusercontent.com/php/php-src/d313ad6098430f4e61f0121a9e7ab392d195e4e4/php.ini-production
- PHP 8.3 bundled production template (older session ID overrides): https://raw.githubusercontent.com/php/php-src/b94f9f68a610e0fca5f2fea5bfa7c7d6d3d5a847/php.ini-production
- PHP filesystem and streams configuration (`allow_url_fopen`, `allow_url_include`): https://www.php.net/manual/en/filesystem.configuration.php
- PHP execution and input limits (`max_execution_time`, `max_input_time`, `max_input_vars`): https://www.php.net/manual/en/info.configuration.php
- PHP upload-limit interactions and pitfalls: https://www.php.net/manual/en/features.file-upload.common-pitfalls.php
- PHP session security and lifetime management: https://www.php.net/manual/en/session.security.ini.php
- PHP command-line inspection (`--ini`, `-i`, `-r`): https://www.php.net/manual/en/features.commandline.options.php
- PHP controlled warning fixture (`trigger_error`): https://www.php.net/manual/en/function.trigger-error.php
- Laravel 12.x configuration and environment-file security: https://laravel.com/framework/docs/12.x/configuration
- Laravel 12.x file storage (private local disk and public storage link): https://laravel.com/framework/docs/12.x/filesystem
- Laravel 12.x Telescope local-only installation: https://laravel.com/framework/docs/12.x/telescope
- Laravel Debugbar production-installation guidance: https://github.com/fruitcake/laravel-debugbar
