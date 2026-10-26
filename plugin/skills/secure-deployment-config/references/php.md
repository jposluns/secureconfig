# PHP and Laravel: TLS and authentication

PHP is a scripting language for building websites and web apps, and Laravel is a framework written in it. This guide helps your AI assistant configure them securely, including a private php-fpm listener, hardened session cookies, password hashing with login rate limiting, production php.ini settings, and debug mode off.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/php.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against PHP native configuration 8.x, PHP production template 8.4 and 8.3, Laravel 12.x, fail2ban 1.1.1, and curl manual 7.75.0; 2 further sources carry no recorded version. Metadata reviewed 2026-10-18; documentation checked September 2026. The guide records 65 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

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

Hash with `password_hash($password, PASSWORD_DEFAULT)` (bcrypt at the time of writing; `PASSWORD_ARGON2ID` needs PHP built with Argon2), check with `password_verify()`, and upgrade old hashes when `password_needs_rehash()` says so. `PASSWORD_DEFAULT` is designed to change over time, so store the hash in a column that can grow past 60 bytes (the manual suggests 255).

Guide assessment: the PHP password and session functions cited here provide no login-attempt throttling; this is not a claim about every PHP extension or application.

Guide advice: apply a proxy limiter or a fail2ban jail over a failure log written by the application or proxy, following the authentication-endpoint requirements in [authentication.md](authentication.md). Among the linked proxy guides, [nginx.md, section 4](nginx.md#4-bound-the-expensive-endpoints) documents `limit_req`; [caddy.md, section 4](caddy.md#4-bound-the-expensive-endpoints) states that stock Caddy has no rate limiter, and [apache.md](apache.md) gives no limiter configuration. fail2ban 1.1.1 documents [`filter` and `logpath`](https://github.com/fail2ban/fail2ban/blob/1.1.1/man/jail.conf.5#L187-L200); its [`nginx-limit-req` jail](https://github.com/fail2ban/fail2ban/blob/1.1.1/config/jail.conf#L378-L384) reads the nginx error log and its [filter](https://github.com/fail2ban/fail2ban/blob/1.1.1/config/filter.d/nginx-limit-req.conf#L48-L49) matches limiting or delaying entries. These sources do not establish a filter for this PHP application's login form or its log format.

Guide advice: for plain-PHP MFA, use a TOTP library or an identity layer in front whose policy requires MFA; [mfa.md](mfa.md#identity-layers-and-auth-proxies-open-source) covers identity-layer options and enforcement requirements, but its library list has no PHP TOTP library. No PHP TOTP library is pinned here.

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

**REASONED: deployment checks have not been demonstrated.** The authoring environment has no PHP or PHP-FPM runtime, no Docker or Podman, and no supplied PHP/Laravel deployment. The listener, TLS, cookie, authentication, banner, and error-disclosure checks require a real deployment. Expected outcomes are REASONED from the cited PHP, Laravel, curl manual, and fronting-server documentation.

REASONED: paste and probe guidance. A live PHP deployment stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. The listener, TLS and cookie comparisons also need a deployed FPM listener and HTTPS application, which were unavailable. Exposed listener: `ss -tlnp` shows a wildcard FPM TCP bind; fixed listener: `ss -xlnp` shows a Unix socket or `ss -tlnp` shows `127.0.0.1:9000`, per the guide's cited PHP FPM configuration (`listen`, `listen.allowed_clients`, `listen.owner`) (PHP 8.x). Exposed TLS: the listener block first prints no headers and `exit=60`, the cited certificate failure marker; the backend-dependent `err=` wording names the certificate failure. Fixed TLS: the first request prints response headers and `exit=0` without `-k`; that success marker is REASONED, not stated in the cited exit-code passages. The exit-code distinction follows the curl manual, exit codes 6, 7, 28 and 60 and the `exitcode` and `errormsg` write-out variables (added in curl 7.75.0) (checked October 2026) entry. The Laravel 12.x deployment (nginx example, `APP_DEBUG`) and PHP cURL constants (`CURLOPT_SSL_VERIFYPEER`, `CURLOPT_SSL_VERIFYHOST`, `CURLOPT_CAINFO`) entries back the settings in sections 3 and 4; they do not establish this probe's outcomes. A lack of headers also appears on a DNS failure (`exit=6`), a refused connection (`exit=7`), a timeout (`exit=28`) or plain HTTP on 443, so on its own it does not show a certificate failure. Exposed cookie: `Set-Cookie` omits one of Secure, HttpOnly or SameSite; fixed cookie: `Set-Cookie` includes all three, per the guide's cited PHP session runtime configuration (PHP 8.x) and Laravel 12.x `config/session.php` defaults entries. All five Verify Bash blocks passed `bash -n` and ShellCheck 0.11.0 with no output. Stubbed URL blocks printed `substitute the full HTTPS URL inside the quotes above; not probing` or `substitute the full HTTPS fixture URL inside the quotes above; not probing` for their placeholders; dummy HTTPS URLs reached `curl-stub`. With `bash -u`, empty and extra values and a missing `set --` line printed `substitute the full HTTPS URL inside the quotes above; not probing` or `substitute the full HTTPS fixture URL inside the quotes above; not probing`, `the set -- line needs exactly 1 value; not probing`, and `paste the whole block, including its set -- line; not probing`, respectively. Local marking review (October 2026, Bash 5.3.9, ShellCheck 0.11.0): the listener block passed `bash -n` and ShellCheck with empty stdout/stderr and status 0. Each Bash -u trial used scratch `ss`, `curl` and `grep` stubs; all had empty stderr and real process status 0. Exact stdout follows, with `\n` denoting each printed line feed.  placeholder: `ss-stub:-xlnp\nsubstitute the full HTTPS URL inside the quotes above; not probing\n` (no curl calls).  empty: `ss-stub:-xlnp\nsubstitute the full HTTPS URL inside the quotes above; not probing\n` (no curl calls).  missing set line: `ss-stub:-xlnp\npaste the whole block, including its set -- line; not probing\n` (no curl calls).  wrong marker: `ss-stub:-xlnp\npaste the whole block, including its set -- line; not probing\n` (no curl calls).  extra value: `ss-stub:-xlnp\nthe set -- line needs exactly 1 value; not probing\n` (no curl calls).  option-like value: `ss-stub:-xlnp\nuse a URL, not an option; not probing\n` (no curl calls).  spaced URL: `ss-stub:-xlnp\nremove whitespace from the URL; not probing\n` (no curl calls).  http:// URL: `ss-stub:-xlnp\nuse an https:// URL; not probing\n` (no curl calls).  bare host: `ss-stub:-xlnp\nuse an https:// URL; not probing\n` (no curl calls).  certificate with cookie present: `ss-stub:-xlnp\nhttp=000 exit=60 err=SSL certificate problem: unable to get local issuer certificate\nSet-Cookie: session=x; Secure; HttpOnly; SameSite=Lax\n`.  certificate with cookie missing: `ss-stub:-xlnp\nhttp=000 exit=60 err=SSL certificate problem: unable to get local issuer certificate\n`.  DNS with cookie present: `ss-stub:-xlnp\nhttp=000 exit=6 err=Could not resolve host\nSet-Cookie: session=x; Secure; HttpOnly; SameSite=Lax\n`.  DNS with cookie missing: `ss-stub:-xlnp\nhttp=000 exit=6 err=Could not resolve host\n`.  refusal with cookie present: `ss-stub:-xlnp\nhttp=000 exit=7 err=Failed to connect\nSet-Cookie: session=x; Secure; HttpOnly; SameSite=Lax\n`.  refusal with cookie missing: `ss-stub:-xlnp\nhttp=000 exit=7 err=Failed to connect\n`.  timeout with cookie present: `ss-stub:-xlnp\nhttp=000 exit=28 err=Operation timed out\nSet-Cookie: session=x; Secure; HttpOnly; SameSite=Lax\n`.  timeout with cookie missing: `ss-stub:-xlnp\nhttp=000 exit=28 err=Operation timed out\n`.  success with cookie present: `ss-stub:-xlnp\nHTTP/2 200\nhttp=200 exit=0 err=\nSet-Cookie: session=x; Secure; HttpOnly; SameSite=Lax\n`.  success with cookie missing: `ss-stub:-xlnp\nHTTP/2 200\nhttp=200 exit=0 err=\n`.  Success with a trailing slash and cookie present: `ss-stub:-xlnp\nHTTP/2 200\nhttp=200 exit=0 err=\nSet-Cookie: session=x; Secure; HttpOnly; SameSite=Lax\n`. In each curl-stub trial, the two calls were to `https://example.test/base` and `https://example.test/base/login`; the trailing-slash trial used `https://example.test/base/` then `https://example.test/base/login`. No request reached a network. No live outcome was observed. Paste each guarded block whole. Substitute a full HTTPS URL inside the single quotes on its `set --` line; use a URL without a literal apostrophe or embedded credentials. Supply the application's base URL; the cookie request appends `/login`, and no output from it is inconclusive. The `exitcode` and `errormsg` write-out variables require curl 7.75.0 or later per the curl manual, exit codes 6, 7, 28 and 60 and the `exitcode` and `errormsg` write-out variables (added in curl 7.75.0) (checked October 2026) entry. The trailing `|| true` keeps a failed probe from ending the shell; it does not indicate success.

REASONED: protected-route comparison. A live PHP deployment stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; no protected route or authorized session was available. Exposed: the same route returns protected content anonymously; fixed: it returns that content only to an authorized session and denies or redirects an anonymous request to login. Per the guide's cited Laravel 12.x Fortify and Laravel 12.x starter kits (Fortify, two-factor, rate limiting) entries. The route block passed `bash -n` and ShellCheck 0.11.0 with no output. Its scratch `bash` curl-stub run printed the placeholder guard; a dummy HTTPS URL reached `curl-stub`; `bash -u` empty, extra and missing-`set --` trials printed the substitute, exactly-one-value and paste-whole-block messages. No route response was observed. For the protected-route check, confirm the same route returns the expected protected content to an authorized session. In an isolated exposed-state test, removing the authentication requirement must make that content accessible anonymously; restoring it must produce the documented denial or login redirect. A missing route or an unrelated error is not evidence of authentication.

REASONED: following block; FPM listener, HTTPS and cookie inspection. The guide records no PHP/PHP-FPM runtime, container runtime or supplied deployment; expectations follow its cited PHP and Laravel documentation and, for the TLS status, the curl manual entry, not a recorded run.

```bash
ss -xlnp   # read every listener; php-fpm: Unix socket; with TCP, ss -tlnp shows 127.0.0.1:9000 only
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the full HTTPS URL inside the quotes above; not probing" ;;
    -*) echo "use a URL, not an option; not probing" ;;
    *[[:space:]]*) echo "remove whitespace from the URL; not probing" ;;
    https://*)
      curl -q -g --noproxy '*' -sSI --connect-timeout 5 --max-time 20 \
        -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' -- "$1" || true
      curl -q -g --noproxy '*' -sI --connect-timeout 5 --max-time 20 -- "${1%/}/login" | grep -i set-cookie   # secure; httponly; samesite=lax
      ;;
    *) echo "use an https:// URL; not probing" ;;
  esac
) || true
```

REASONED: following block; anonymous protected-route discrimination. The guide records no PHP/PHP-FPM runtime, container runtime or supplied deployment; expectations follow its cited PHP and Laravel documentation, not a recorded run.

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

REASONED: following block; loaded CLI configuration inspection. The guide records no PHP/PHP-FPM runtime, container runtime or supplied deployment; expectations follow its cited PHP and Laravel documentation, not a recorded run.

```bash
php --ini
php -i | grep -E '^(display_errors|display_startup_errors|log_errors|error_log|error_reporting|expose_php) =>'
php -r 'echo "E_ALL=", E_ALL, PHP_EOL;'
```

REASONED: preceding block; loaded CLI configuration inspection and expected error settings. In the authoring environment, `php -v` exited 127 and printed `/usr/bin/bash: line 1: php: command not found`; `php` was not on the command path, and neither network package installation nor an authorized offline PHP package source was available. The block passed `bash -n` and ShellCheck 0.11.0 with no output; its scratch stubs printed `php-stub:--ini`, `grep-stub:-E ^(display_errors|display_startup_errors|log_errors|error_log|error_reporting|expose_php) =>` and `php-stub:-r echo "E_ALL=", E_ALL, PHP_EOL;`. Exposed settings show display or startup errors On, logging Off or `expose_php` On where misconfigured; fixed settings show display and startup errors Off, logging On, a protected log, `expose_php` Off and reporting matched to the installed `E_ALL`. Per the guide's cited PHP command-line inspection (`--ini`, `-i`, `-r`), PHP 8.x error configuration (`display_errors`, `display_startup_errors`, `log_errors`, `error_log`, `error_reporting`) and PHP hiding and `expose_php` entries. An effective FPM or Apache comparison still needs that deployed SAPI; a live PHP deployment stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available. No actual CLI or FPM values were observed. Expect `display_errors=Off`, `display_startup_errors=Off`, `log_errors=On`, the intended protected `error_log`, `expose_php=Off`, and `error_reporting` equal to the installed version's `E_ALL`. PHP's diagnostic values can change between versions, so compare against the printed constant rather than a copied integer. CLI inspection does not establish FPM or Apache's effective configuration: inspect that SAPI's loaded files and overrides separately, including the FPM pool settings. Do not publish a `phpinfo()` endpoint.

**REASONED: banner and native PHP error disclosure.** No web SAPI or deployment was available. In an isolated deployment matching production, temporarily serve this controlled fixture through the intended PHP handler and proxy. Use PHP's built-in error handler, without framework bootstrapping or application error-handler overrides. Restrict access to the test operator and remove the fixture afterwards. The fixed warning text contains no secret. [PHP `trigger_error()`](https://www.php.net/manual/en/function.trigger-error.php).

REASONED: following block; controlled native PHP warning fixture. The guide records no PHP/PHP-FPM runtime, container runtime or supplied deployment; expectations follow its cited PHP and Laravel documentation, not a recorded run.

```php
<?php
trigger_error('SECURECONFIG_PHP_ERROR_CANARY', E_USER_WARNING);
echo "SECURECONFIG_PHP_REACHED\n";
```

REASONED: preceding block; controlled native PHP warning fixture and header-probe lead-in. In the authoring environment, `php -v` exited 127 and printed `/usr/bin/bash: line 1: php: command not found`; `php` was not on the command path, and neither network package installation nor an authorized offline PHP package source was available, so `php -l` and the CLI fixture runs could not be performed. A live PHP deployment stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; no protected worker log was available. Exposed with display errors On, the fixture HTTP 200 response should include `SECURECONFIG_PHP_ERROR_CANARY` and `SECURECONFIG_PHP_REACHED`; fixed with display errors Off and logging On, HTTP 200 should include only `SECURECONFIG_PHP_REACHED` and the protected log should contain `SECURECONFIG_PHP_ERROR_CANARY`. Per the guide's cited PHP controlled warning fixture (`trigger_error`) and PHP 8.x error configuration (`display_errors`, `display_startup_errors`, `log_errors`, `error_log`, `error_reporting`) entries. No PHP response or log was observed. First inspect the fixture's response headers:

REASONED: following block; PHP response-banner discrimination. The guide records no PHP/PHP-FPM runtime, container runtime or supplied deployment; expectations follow its cited PHP and Laravel documentation, not a recorded run.

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

REASONED: preceding block; fixture-header curl probe and PHP banner interpretation. A live PHP deployment stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; no proxy response or active SAPI inventory was available. Exposed with `expose_php=On`: successful fixture HTTP 200 with `X-Powered-By: PHP/...` unless a proxy strips it; fixed with Off: successful HTTP 200 without PHP's header. Per the guide's cited PHP hiding and `expose_php` and PHP 8.x error configuration (`display_errors`, `display_startup_errors`, `log_errors`, `error_log`, `error_reporting`) entries. The banner block passed `bash -n` and ShellCheck 0.11.0 with no output; scratch `bash` printed its placeholder guard, a dummy HTTPS URL reached `curl-stub`, and `bash -u` empty, extra and missing-`set --` trials printed the matching guard messages. No response header was observed. With `expose_php=On`, the exposed-state response is expected to contain `X-Powered-By: PHP/...` unless another layer strips it. With `expose_php=Off`, it must be absent. Require a successful transfer and the fixture's expected HTTP 200 response. If the proxy strips the header in both states, this checks the externally visible response only; attribute the PHP setting through the active SAPI configuration. [PHP banner behavior](https://www.php.net/manual/en/security.hiding.php).

REASONED: fixture-body inspection instruction. A live PHP deployment stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; no protected worker log was available. Exposed with display errors On: the fixture HTTP 200 body includes `SECURECONFIG_PHP_ERROR_CANARY`; fixed with display errors Off and logging On: HTTP 200 body includes `SECURECONFIG_PHP_REACHED` without the warning, while the protected log receives `SECURECONFIG_PHP_ERROR_CANARY`. Per the guide's cited PHP controlled warning fixture (`trigger_error`) and PHP 8.x error configuration (`display_errors`, `display_startup_errors`, `log_errors`, `error_log`, `error_reporting`) entries. The following body block passed `bash -n` and ShellCheck 0.11.0 with no output; scratch `bash` printed `substitute the full HTTPS fixture URL inside the quotes above; not probing`, a dummy HTTPS URL reached `curl-stub`, and `bash -u` empty, extra and missing-`set --` trials printed `substitute the full HTTPS fixture URL inside the quotes above; not probing`, `the set -- line needs exactly 1 value; not probing`, and `paste the whole block, including its set -- line; not probing`, respectively. No body or log was observed. Then inspect the body from the same fixture URL:

REASONED: following block; native PHP and Laravel error-disclosure discrimination. The guide records no PHP/PHP-FPM runtime, container runtime or supplied deployment; expectations follow its cited PHP and Laravel documentation, not a recorded run.

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

REASONED: preceding block; native PHP body curl probe, response and log comparison. A live PHP deployment stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; no worker log was available. Exposed with display errors On: HTTP 200 contains the warning marker; fixed with display errors Off and logging On: HTTP 200 contains the reached marker without diagnostics and the protected log contains the warning marker. Per the guide's cited PHP controlled warning fixture (`trigger_error`) and PHP 8.x error configuration (`display_errors`, `display_startup_errors`, `log_errors`, `error_log`, `error_reporting`) entries. The body block passed `bash -n` and ShellCheck 0.11.0 with no output; scratch `bash` printed its placeholder guard, a dummy HTTPS URL reached `curl-stub`, and `bash -u` empty, extra and missing-`set --` trials printed the matching guard messages. No HTTP or log outcome was observed. In the isolated exposed state, `display_errors=On` with `error_reporting=E_ALL` should disclose `SECURECONFIG_PHP_ERROR_CANARY` in the response. After applying section 5, the HTTP 200 body must contain `SECURECONFIG_PHP_REACHED` without the warning marker or PHP diagnostics, while the protected log receives the warning marker for that request. A blank response, redirect, 404, failed transfer, or missing log entry does not satisfy this check. This fixture tests a runtime warning; it does not exercise startup or parse errors. [PHP error configuration](https://www.php.net/manual/en/errorfunc.configuration.php).

REASONED: Laravel exception-route comparison. A live Laravel deployment stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; no controlled route, authorized session or application log was available. Exposed with `APP_DEBUG=true`: the route's response shows the distinctive exception, trace or configuration values; fixed with `APP_DEBUG=false` after rebuilding cached configuration: a generic error response omits those details and the protected application log records the exception. Per the guide's cited Laravel 12.x deployment (nginx example, `APP_DEBUG`) and Laravel 12.x configuration and environment-file security entries. The related body curl block passed `bash -n` and ShellCheck 0.11.0 with no output; scratch `bash` printed its placeholder guard, a dummy HTTPS URL reached `curl-stub`, and `bash -u` empty, extra and missing-`set --` trials printed the matching guard messages. No Laravel response or log was observed. For Laravel 12.x, repeat the body probe against a controlled route that raises an exception with a distinctive, non-secret message. In an isolated deployment, compare `APP_DEBUG=true` with `APP_DEBUG=false`, rebuilding cached configuration after each change. The protected state must show a generic error response without the exception message, trace, or configuration values; confirm the matching exception in the protected application log. The native PHP fixture alone does not establish Laravel's framework error behavior. [Laravel debug mode](https://laravel.com/framework/docs/12.x/deployment#debug-mode).

## Sources (checked September 2026)

- PHP FPM configuration (`listen`, `listen.allowed_clients`, `listen.owner`) (PHP 8.x): https://www.php.net/manual/en/install.fpm.configuration.php
- PHP session runtime configuration (PHP 8.x): https://www.php.net/manual/en/session.configuration.php
- PHP `session_regenerate_id()`: https://www.php.net/manual/en/function.session-regenerate-id.php
- fail2ban 1.1.1 jail filter and logpath options (checked October 2026): https://github.com/fail2ban/fail2ban/blob/1.1.1/man/jail.conf.5#L187-L200
- fail2ban 1.1.1 nginx-limit-req jail and nginx limiter prerequisite (checked October 2026): https://github.com/fail2ban/fail2ban/blob/1.1.1/config/jail.conf#L378-L384
- fail2ban 1.1.1 nginx-limit-req filter expression (checked October 2026): https://github.com/fail2ban/fail2ban/blob/1.1.1/config/filter.d/nginx-limit-req.conf#L48-L49
- PHP `password_hash()`: https://www.php.net/manual/en/function.password-hash.php
- PHP cURL constants (`CURLOPT_SSL_VERIFYPEER`, `CURLOPT_SSL_VERIFYHOST`, `CURLOPT_CAINFO`): https://www.php.net/manual/en/curl.constants.php
- curl manual, exit codes 6, 7, 28 and 60 and the `exitcode` and `errormsg` write-out variables (added in curl 7.75.0) (checked October 2026): https://curl.se/docs/manpage.html
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
- PHP core directives (`disable_functions`, `open_basedir`, memory and upload limits) (PHP 8.x): https://www.php.net/manual/en/ini.core.php
- PHP hiding and `expose_php`: https://www.php.net/manual/en/security.hiding.php
- PHP 8.4 bundled production template: https://raw.githubusercontent.com/php/php-src/d313ad6098430f4e61f0121a9e7ab392d195e4e4/php.ini-production
- PHP 8.3 bundled production template (older session ID overrides): https://raw.githubusercontent.com/php/php-src/b94f9f68a610e0fca5f2fea5bfa7c7d6d3d5a847/php.ini-production
- PHP filesystem and streams configuration (`allow_url_fopen`, `allow_url_include`): https://www.php.net/manual/en/filesystem.configuration.php
- PHP execution and input limits (`max_execution_time`, `max_input_time`, `max_input_vars`) (PHP 8.x): https://www.php.net/manual/en/info.configuration.php
- PHP upload-limit interactions and pitfalls: https://www.php.net/manual/en/features.file-upload.common-pitfalls.php
- PHP session security and lifetime management: https://www.php.net/manual/en/session.security.ini.php
- PHP command-line inspection (`--ini`, `-i`, `-r`): https://www.php.net/manual/en/features.commandline.options.php
- PHP controlled warning fixture (`trigger_error`): https://www.php.net/manual/en/function.trigger-error.php
- Laravel 12.x configuration and environment-file security: https://laravel.com/framework/docs/12.x/configuration
- Laravel 12.x file storage (private local disk and public storage link): https://laravel.com/framework/docs/12.x/filesystem
- Laravel 12.x Telescope local-only installation: https://laravel.com/framework/docs/12.x/telescope
- Laravel Debugbar production-installation guidance: https://github.com/fruitcake/laravel-debugbar


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- php8: PHP native configuration (8.x)
- template84: PHP production template (8.4)
- template83: PHP production template (8.3)
- laravel: Laravel (12.x)
- php: PHP documentation (unknown)
- debugbar: Laravel Debugbar (unknown)
- fail2ban: fail2ban (1.1.1)
- curl: curl manual (7.75.0)

Claims (full source mapping in the JSON block below):

- fpm-private (REASONED; php8): FPM requires listen per pool; exposed FastCGI permits code execution. Use a Unix socket or loopback TCP 9000; never publish container FPM.
- fpm-clients (REASONED; php8): listen.allowed_clients defaults unset, accepting any address; explicitly allow loopback for TCP.
- fpm-socket (REASONED; php8): Unix socket access uses listen.owner, listen.group and listen.mode, default 0660.
- cookie-secure (REASONED; php8): Native session.cookie_secure defaults 0; enable it.
- cookie-httponly (REASONED; php8): Native session.cookie_httponly defaults 0; enable it.
- cookie-samesite (REASONED; php8): Native session.cookie_samesite defaults empty; choose Lax or Strict.
- session-strict (REASONED; php8): session.use_strict_mode defaults 0; enable it.
- session-regenerate (REASONED; php): Regenerate IDs after login/privilege changes; delete_old_session defaults false. Timestamp expiry avoids immediate deletion.
- passwords (REASONED; php): PASSWORD_DEFAULT currently uses bcrypt; Argon2id needs an Argon2 build. Verify/rehash passwords and allow growing hashes, suggested 255 bytes.
- plain-auth (REASONED; php, fail2ban): Guide assessment: the cited PHP password and session functions lack login throttling (no claim about every PHP extension or application). Guide advice: a proxy limiter or fail2ban jail over app/proxy failure logs (cited sources establish no filter for this login form or log format) and for plain-PHP MFA a TOTP library or an MFA-requiring identity layer in front; no PHP TOTP library is pinned here.
- laravel-debug (REASONED; laravel): Set APP_ENV=production, APP_DEBUG=false and HTTPS APP_URL; debug mode exposes configuration values.
- laravel-key (REASONED; laravel): Generate APP_KEY with artisan key:generate; list old keys in APP_PREVIOUS_KEYS during rotation.
- laravel-secure (REASONED; laravel): Set SESSION_SECURE_COOKIE=true; the session secure configuration has no default.
- laravel-httponly (REASONED; laravel): SESSION_HTTP_ONLY defaults true; retain it.
- laravel-samesite (REASONED; laravel): SESSION_SAME_SITE defaults lax; strict suits admin-only apps.
- laravel-proxy (REASONED; laravel): Laravel 12.x trustProxies names proxies in bootstrap/app.php; wildcard trust requires exclusive proxy reachability.
- laravel-urls (REASONED; laravel): URL::forceHttps() or forceScheme(https) in a provider boot method forces generated HTTPS URLs.
- laravel-hashes (REASONED; laravel): Hash::make/check default to bcrypt; HASH_DRIVER=argon2id switches it and needsRehash detects upgrades. HASH_VERIFY=false disables rejection of other algorithms.
- laravel-limiter (REASONED; laravel): Define a five-per-minute login limiter keyed by email plus IP; attach throttle:login to the real route.
- fortify-login (REASONED; laravel): 12.x starter kits use Fortify, which throttles username plus IP and regenerates session IDs on login; standalone Fortify omits views.
- fortify-mfa (REASONED; laravel): Fortify twoFactorAuthentication with confirm and confirmPassword supplies TOTP and recovery codes.
- socialite (REASONED; laravel): Socialite supplies OAuth providers; community packages supply OIDC. Use HTTPS callbacks and linked allowlist/token checks.
- laravel-cache (REASONED; laravel): Keep plaintext .env untracked; build config/route caches after production inputs and rebuild on changes. Cached config does not load .env; use env only in config files.
- laravel-hosts (REASONED; laravel): Laravel accepts arbitrary Host headers by default; restrict hosts at the server and add anchored TrustHosts with subdomains:false.
- debug-tools (REASONED; laravel, debugbar): Omit Telescope and Debugbar from production; Telescope local-only installation includes conditional provider registration.
- curl-peer (REASONED; php): CURLOPT_SSL_VERIFYPEER defaults true; retain certificate verification.
- curl-host (REASONED; php): CURLOPT_SSL_VERIFYHOST defaults 2; retain hostname checks and use CURLOPT_CAINFO for an internal CA.
- display-errors (REASONED; php8): PHP 8.x display_errors defaults On; set Off before execution. ini_set cannot hide a fatal error preventing it from running.
- startup-errors (REASONED; php8): display_startup_errors defaults On since PHP 8.0.0, previously Off; set Off.
- log-errors (REASONED; php8): log_errors defaults Off; enable it with a protected, pre-created, worker-writable log outside the document root and rotation. Unset error_log uses the SAPI logger.
- error-reporting (REASONED; php8): error_reporting defaults E_ALL since PHP 8.0.0; retain reporting into logs. Package/template/deployment overrides can differ.
- php-banner (REASONED; php8, php): expose_php defaults On; Off suppresses PHP own X-Powered-By header, not other layers or all application identification.
- production-template (REASONED; template84): PHP 8.4 production template disables display and enables logging, but uses E_ALL &amp; ~E_DEPRECATED and leaves expose_php enabled.
- disable-functions (REASONED; php8): disable_functions defaults empty; test the listed process-function restrictions. Since PHP 8.0 definitions disappear and userland can redefine them; internal functions only, not a security boundary.
- url-fopen (REASONED; php): allow_url_fopen defaults On; disable unnecessary URL wrappers after compatibility tests, not as a general egress policy.
- url-include (REASONED; php): allow_url_include defaults Off, deprecated since PHP 7.4; retain Off. URL includes also require allow_url_fopen.
- basedir (REASONED; php8): open_basedir defaults NULL; allow required paths, retain OS isolation and account for disabled realpath caching. PHP 8.3 rejects runtime .. components.
- fpm-extensions (REASONED; php8): PHP 8.x FPM security.limit_extensions defaults .php .phar; restrict to .php, which still permits uploaded PHP dispatched by the server.
- upload-execution (REASONED; php8, laravel): Separate writable uploads from code, preferably outside the document root; server mappings must forbid PHP execution, including aliases/symlinks.
- laravel-storage (REASONED; laravel): Laravel 12.x local disk defaults storage/app/private; public disk uses storage/app/public via public/storage, which does not itself prevent PHP execution.
- upload-size (REASONED; php8): upload_max_filesize defaults 2M per file; post_max_size must allow multipart overhead.
- post-size (REASONED; php8): post_max_size defaults 8M; excess leaves POST and FILES empty and must be rejected by the app.
- upload-count (REASONED; php8, php): max_file_uploads defaults 20; twenty maximum-sized files need not fit the POST limit.
- memory-limit (REASONED; php8): memory_limit defaults 128M, should generally exceed post_max_size, and -1 removes the bound.
- input-vars (REASONED; php8): max_input_vars defaults 1000 separately for GET, POST and COOKIE; excess is warned/truncated, not a general JSON limit.
- execution-time (REASONED; php8): max_execution_time defaults 30 for web and 0 for CLI; platform/build accounting can exclude I/O, not a portable wall-clock deadline.
- input-time (REASONED; php8, template84): max_input_time defaults -1, using max_execution_time; 0 is unlimited. Example and production template select 60 seconds.
- upload-time (REASONED; php): Test slow/multiple uploads and coordinate server size/time limits. Per-request bounds do not replace capacity controls or rate limiting.
- fpm-timeout (REASONED; php8): request_terminate_timeout defaults 0, disabled; example selects 60s as app policy and kills overlong workers.
- fpm-finished (REASONED; php8): request_terminate_timeout_track_finished defaults no; yes extends the limit past fastcgi_finish_request and into shutdown work.
- session-gc (REASONED; php8, php): Native gc_maxlifetime defaults 1440 seconds; probabilistic collection is not auth expiry. Use timestamp expiry/cleanup; shared paths can inherit shorter lifetimes.
- session-lifetime (REASONED; php8, laravel): Native cookie_lifetime defaults 0, a browser-session cookie; Laravel uses config/session.php rather than native storage/lifetime directives.
- session-only-cookies (REASONED; php8): session.use_only_cookies defaults 1; retain it to exclude GET/POST IDs. Disabling it is deprecated from PHP 8.4.
- session-storage (REASONED; php8): Default files handler needs a private worker-writable directory outside the document root; dedicated-account mode 0700, default file mode 0600, separate untrusted-app identities.
- session-sid-length (REASONED; php8, template83): PHP 8.x session.sid_length defaults 32; changes are deprecated from 8.4. PHP 8.3 production template sets 26.
- session-sid-bits (REASONED; php8, template83): PHP 8.x session.sid_bits_per_character defaults 4; changes are deprecated from 8.4. PHP 8.3 production template sets 5.
- verify-listener (REASONED; php8): Inventory all FPM listeners: Unix socket or loopback TCP 9000 only.
- verify-tls (REASONED; curl): The TLS probe distinguishes cited exit=60 certificate failure from reasoned exit=0 success without -k; linked fronting-server guides supply TLS configuration.
- verify-cookies (REASONED; php8, laravel): Inspect login Set-Cookie for Secure, HttpOnly and SameSite=Lax.
- verify-auth (REASONED; laravel): Anonymous protected routes must deny or redirect to login without protected content; require authorized success and isolated auth-removal control. Unrelated redirects/errors and anonymous Set-Cookie do not establish authentication.
- verify-config (REASONED; php, php8): Inspect CLI ini/settings against installed E_ALL; CLI does not establish web SAPI/FPM settings. Do not publish phpinfo.
- verify-banner (REASONED; php): Fixture should give HTTP 200; expose_php On should show PHP header unless stripped, Off must hide it. Proxy stripping in both states needs SAPI inspection.
- verify-error (REASONED; php8, php): Native warning fixture must disclose canary with display_errors On, then return reached marker without diagnostics and log the warning after hardening. Errors/missing logs/blank bodies are inconclusive; startup/parse errors untested.
- verify-laravel-error (REASONED; laravel): Repeat body probe with controlled Laravel exception, rebuild config cache after APP_DEBUG changes, and require generic response plus protected log; native fixture does not test framework errors.
- verify-curl-version (REASONED; curl): The exitcode and errormsg write-out variables require curl 7.75.0 or later per the curl manual.

````json
{
  "schema": 1,
  "checked": "2026-10-18",
  "documentation_checked": "2026-09",
  "body_sha256": "d49ada5c2cc5685214e052a66bea20b47fa0581969ca950c56b537fbff4f4c88",
  "components": {
    "php8": {
      "name": "PHP native configuration",
      "basis": "8.x",
      "sources": {
        "s89c799077b82": "https://www.php.net/manual/en/errorfunc.configuration.php",
        "s5a3f7bde8338": "https://www.php.net/manual/en/info.configuration.php",
        "sc9e417e2ad6f": "https://www.php.net/manual/en/ini.core.php",
        "s2e692b7c86a6": "https://www.php.net/manual/en/install.fpm.configuration.php",
        "s000e155a7b25": "https://www.php.net/manual/en/session.configuration.php"
      }
    },
    "template84": {
      "name": "PHP production template",
      "basis": "8.4",
      "sources": {
        "sd72e3d69551f": "https://raw.githubusercontent.com/php/php-src/d313ad6098430f4e61f0121a9e7ab392d195e4e4/php.ini-production"
      }
    },
    "template83": {
      "name": "PHP production template",
      "basis": "8.3",
      "sources": {
        "sea3d3a4ea486": "https://raw.githubusercontent.com/php/php-src/b94f9f68a610e0fca5f2fea5bfa7c7d6d3d5a847/php.ini-production"
      }
    },
    "laravel": {
      "name": "Laravel",
      "basis": "12.x",
      "sources": {
        "sf0448f3d4665": "https://api.laravel.com/docs/12.x/Illuminate/Routing/UrlGenerator.html",
        "s98db3429151c": "https://github.com/laravel/laravel/blob/f6b2e79bdbfc5bf4a37ad16466cc06ad79cc9e8f/config/session.php",
        "s4e846bd588a8": "https://laravel.com/framework/docs/12.x/configuration",
        "s6510c1aa8d96": "https://laravel.com/framework/docs/12.x/deployment",
        "sb3e2d08bd07d": "https://laravel.com/framework/docs/12.x/encryption",
        "s879d69d64852": "https://laravel.com/framework/docs/12.x/filesystem",
        "sc58ba221e3cd": "https://laravel.com/framework/docs/12.x/fortify",
        "sdf4ba04ddcda": "https://laravel.com/framework/docs/12.x/hashing",
        "s517839d232ec": "https://laravel.com/framework/docs/12.x/requests",
        "s248fef722141": "https://laravel.com/framework/docs/12.x/routing",
        "s003198079bdd": "https://laravel.com/framework/docs/12.x/socialite",
        "sb3e846095c54": "https://laravel.com/framework/docs/12.x/starter-kits",
        "sd7d2287b5d35": "https://laravel.com/framework/docs/12.x/telescope"
      }
    },
    "php": {
      "name": "PHP documentation",
      "basis": "unknown",
      "sources": {
        "s09fdbeba0867": "https://www.php.net/manual/en/curl.constants.php",
        "s5840a5a0a848": "https://www.php.net/manual/en/features.commandline.options.php",
        "s3cbc65590d52": "https://www.php.net/manual/en/features.file-upload.common-pitfalls.php",
        "s6f3e55d536e7": "https://www.php.net/manual/en/filesystem.configuration.php",
        "s50f85ff4fbd1": "https://www.php.net/manual/en/function.password-hash.php",
        "s625cd1d40655": "https://www.php.net/manual/en/function.session-regenerate-id.php",
        "s2f1c806d037c": "https://www.php.net/manual/en/function.trigger-error.php",
        "s7b2c2c19835d": "https://www.php.net/manual/en/security.hiding.php",
        "s8664dc56a028": "https://www.php.net/manual/en/session.security.ini.php"
      }
    },
    "debugbar": {
      "name": "Laravel Debugbar",
      "basis": "unknown",
      "sources": {
        "s7099781fdf4a": "https://github.com/fruitcake/laravel-debugbar"
      }
    },
    "fail2ban": {
      "name": "fail2ban",
      "basis": "1.1.1",
      "sources": {
        "s0470655e109b": "https://github.com/fail2ban/fail2ban/blob/1.1.1/man/jail.conf.5#L187-L200",
        "s9b3b926fe020": "https://github.com/fail2ban/fail2ban/blob/1.1.1/config/jail.conf#L378-L384",
        "sdb5f6f355db6": "https://github.com/fail2ban/fail2ban/blob/1.1.1/config/filter.d/nginx-limit-req.conf#L48-L49"
      }
    },
    "curl": {
      "name": "curl manual",
      "basis": "7.75.0",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    }
  },
  "claims": {
    "fpm-private": {"text": "FPM requires listen per pool; exposed FastCGI permits code execution. Use a Unix socket or loopback TCP 9000; never publish container FPM.", "components": ["php8"], "sources": ["php8:s2e692b7c86a6"], "status": "REASONED"},
    "fpm-clients": {"text": "listen.allowed_clients defaults unset, accepting any address; explicitly allow loopback for TCP.", "components": ["php8"], "sources": ["php8:s2e692b7c86a6"], "status": "REASONED"},
    "fpm-socket": {"text": "Unix socket access uses listen.owner, listen.group and listen.mode, default 0660.", "components": ["php8"], "sources": ["php8:s2e692b7c86a6"], "status": "REASONED"},
    "cookie-secure": {"text": "Native session.cookie_secure defaults 0; enable it.", "components": ["php8"], "sources": ["php8:s000e155a7b25"], "status": "REASONED"},
    "cookie-httponly": {"text": "Native session.cookie_httponly defaults 0; enable it.", "components": ["php8"], "sources": ["php8:s000e155a7b25"], "status": "REASONED"},
    "cookie-samesite": {"text": "Native session.cookie_samesite defaults empty; choose Lax or Strict.", "components": ["php8"], "sources": ["php8:s000e155a7b25"], "status": "REASONED"},
    "session-strict": {"text": "session.use_strict_mode defaults 0; enable it.", "components": ["php8"], "sources": ["php8:s000e155a7b25"], "status": "REASONED"},
    "session-regenerate": {"text": "Regenerate IDs after login/privilege changes; delete_old_session defaults false. Timestamp expiry avoids immediate deletion.", "components": ["php"], "sources": ["php:s625cd1d40655"], "status": "REASONED"},
    "passwords": {"text": "PASSWORD_DEFAULT currently uses bcrypt; Argon2id needs an Argon2 build. Verify/rehash passwords and allow growing hashes, suggested 255 bytes.", "components": ["php"], "sources": ["php:s50f85ff4fbd1"], "status": "REASONED"},
    "plain-auth": {"text": "Guide assessment: the cited PHP password and session functions lack login throttling (no claim about every PHP extension or application). Guide advice: a proxy limiter or fail2ban jail over app/proxy failure logs (cited sources establish no filter for this login form or log format) and for plain-PHP MFA a TOTP library or an MFA-requiring identity layer in front; no PHP TOTP library is pinned here.", "components": ["php", "fail2ban"], "sources": ["php:s50f85ff4fbd1", "php:s8664dc56a028", "fail2ban:s0470655e109b", "fail2ban:s9b3b926fe020", "fail2ban:sdb5f6f355db6"], "status": "REASONED"},
    "laravel-debug": {"text": "Set APP_ENV=production, APP_DEBUG=false and HTTPS APP_URL; debug mode exposes configuration values.", "components": ["laravel"], "sources": ["laravel:s4e846bd588a8", "laravel:s6510c1aa8d96"], "status": "REASONED"},
    "laravel-key": {"text": "Generate APP_KEY with artisan key:generate; list old keys in APP_PREVIOUS_KEYS during rotation.", "components": ["laravel"], "sources": ["laravel:sb3e2d08bd07d"], "status": "REASONED"},
    "laravel-secure": {"text": "Set SESSION_SECURE_COOKIE=true; the session secure configuration has no default.", "components": ["laravel"], "sources": ["laravel:s98db3429151c"], "status": "REASONED"},
    "laravel-httponly": {"text": "SESSION_HTTP_ONLY defaults true; retain it.", "components": ["laravel"], "sources": ["laravel:s98db3429151c"], "status": "REASONED"},
    "laravel-samesite": {"text": "SESSION_SAME_SITE defaults lax; strict suits admin-only apps.", "components": ["laravel"], "sources": ["laravel:s98db3429151c"], "status": "REASONED"},
    "laravel-proxy": {"text": "Laravel 12.x trustProxies names proxies in bootstrap/app.php; wildcard trust requires exclusive proxy reachability.", "components": ["laravel"], "sources": ["laravel:s517839d232ec"], "status": "REASONED"},
    "laravel-urls": {"text": "URL::forceHttps() or forceScheme(https) in a provider boot method forces generated HTTPS URLs.", "components": ["laravel"], "sources": ["laravel:sf0448f3d4665"], "status": "REASONED"},
    "laravel-hashes": {"text": "Hash::make/check default to bcrypt; HASH_DRIVER=argon2id switches it and needsRehash detects upgrades. HASH_VERIFY=false disables rejection of other algorithms.", "components": ["laravel"], "sources": ["laravel:sdf4ba04ddcda"], "status": "REASONED"},
    "laravel-limiter": {"text": "Define a five-per-minute login limiter keyed by email plus IP; attach throttle:login to the real route.", "components": ["laravel"], "sources": ["laravel:s248fef722141"], "status": "REASONED"},
    "fortify-login": {"text": "12.x starter kits use Fortify, which throttles username plus IP and regenerates session IDs on login; standalone Fortify omits views.", "components": ["laravel"], "sources": ["laravel:sc58ba221e3cd", "laravel:sb3e846095c54"], "status": "REASONED"},
    "fortify-mfa": {"text": "Fortify twoFactorAuthentication with confirm and confirmPassword supplies TOTP and recovery codes.", "components": ["laravel"], "sources": ["laravel:sc58ba221e3cd", "laravel:sb3e846095c54"], "status": "REASONED"},
    "socialite": {"text": "Socialite supplies OAuth providers; community packages supply OIDC. Use HTTPS callbacks and linked allowlist/token checks.", "components": ["laravel"], "sources": ["laravel:s003198079bdd"], "status": "REASONED"},
    "laravel-cache": {"text": "Keep plaintext .env untracked; build config/route caches after production inputs and rebuild on changes. Cached config does not load .env; use env only in config files.", "components": ["laravel"], "sources": ["laravel:s4e846bd588a8", "laravel:s6510c1aa8d96"], "status": "REASONED"},
    "laravel-hosts": {"text": "Laravel accepts arbitrary Host headers by default; restrict hosts at the server and add anchored TrustHosts with subdomains:false.", "components": ["laravel"], "sources": ["laravel:s517839d232ec"], "status": "REASONED"},
    "debug-tools": {"text": "Omit Telescope and Debugbar from production; Telescope local-only installation includes conditional provider registration.", "components": ["laravel", "debugbar"], "sources": ["laravel:sd7d2287b5d35", "debugbar:s7099781fdf4a"], "status": "REASONED"},
    "curl-peer": {"text": "CURLOPT_SSL_VERIFYPEER defaults true; retain certificate verification.", "components": ["php"], "sources": ["php:s09fdbeba0867"], "status": "REASONED"},
    "curl-host": {"text": "CURLOPT_SSL_VERIFYHOST defaults 2; retain hostname checks and use CURLOPT_CAINFO for an internal CA.", "components": ["php"], "sources": ["php:s09fdbeba0867"], "status": "REASONED"},
    "display-errors": {"text": "PHP 8.x display_errors defaults On; set Off before execution. ini_set cannot hide a fatal error preventing it from running.", "components": ["php8"], "sources": ["php8:s89c799077b82"], "status": "REASONED"},
    "startup-errors": {"text": "display_startup_errors defaults On since PHP 8.0.0, previously Off; set Off.", "components": ["php8"], "sources": ["php8:s89c799077b82"], "status": "REASONED"},
    "log-errors": {"text": "log_errors defaults Off; enable it with a protected, pre-created, worker-writable log outside the document root and rotation. Unset error_log uses the SAPI logger.", "components": ["php8"], "sources": ["php8:s89c799077b82"], "status": "REASONED"},
    "error-reporting": {"text": "error_reporting defaults E_ALL since PHP 8.0.0; retain reporting into logs. Package/template/deployment overrides can differ.", "components": ["php8"], "sources": ["php8:s89c799077b82"], "status": "REASONED"},
    "php-banner": {"text": "expose_php defaults On; Off suppresses PHP own X-Powered-By header, not other layers or all application identification.", "components": ["php8", "php"], "sources": ["php8:sc9e417e2ad6f", "php:s7b2c2c19835d"], "status": "REASONED"},
    "production-template": {"text": "PHP 8.4 production template disables display and enables logging, but uses E_ALL & ~E_DEPRECATED and leaves expose_php enabled.", "components": ["template84"], "sources": ["template84:sd72e3d69551f"], "status": "REASONED"},
    "disable-functions": {"text": "disable_functions defaults empty; test the listed process-function restrictions. Since PHP 8.0 definitions disappear and userland can redefine them; internal functions only, not a security boundary.", "components": ["php8"], "sources": ["php8:sc9e417e2ad6f"], "status": "REASONED"},
    "url-fopen": {"text": "allow_url_fopen defaults On; disable unnecessary URL wrappers after compatibility tests, not as a general egress policy.", "components": ["php"], "sources": ["php:s6f3e55d536e7"], "status": "REASONED"},
    "url-include": {"text": "allow_url_include defaults Off, deprecated since PHP 7.4; retain Off. URL includes also require allow_url_fopen.", "components": ["php"], "sources": ["php:s6f3e55d536e7"], "status": "REASONED"},
    "basedir": {"text": "open_basedir defaults NULL; allow required paths, retain OS isolation and account for disabled realpath caching. PHP 8.3 rejects runtime .. components.", "components": ["php8"], "sources": ["php8:sc9e417e2ad6f"], "status": "REASONED"},
    "fpm-extensions": {"text": "PHP 8.x FPM security.limit_extensions defaults .php .phar; restrict to .php, which still permits uploaded PHP dispatched by the server.", "components": ["php8"], "sources": ["php8:s2e692b7c86a6"], "status": "REASONED"},
    "upload-execution": {"text": "Separate writable uploads from code, preferably outside the document root; server mappings must forbid PHP execution, including aliases/symlinks.", "components": ["php8", "laravel"], "sources": ["php8:s2e692b7c86a6", "laravel:s879d69d64852"], "status": "REASONED"},
    "laravel-storage": {"text": "Laravel 12.x local disk defaults storage/app/private; public disk uses storage/app/public via public/storage, which does not itself prevent PHP execution.", "components": ["laravel"], "sources": ["laravel:s879d69d64852"], "status": "REASONED"},
    "upload-size": {"text": "upload_max_filesize defaults 2M per file; post_max_size must allow multipart overhead.", "components": ["php8"], "sources": ["php8:sc9e417e2ad6f"], "status": "REASONED"},
    "post-size": {"text": "post_max_size defaults 8M; excess leaves POST and FILES empty and must be rejected by the app.", "components": ["php8"], "sources": ["php8:sc9e417e2ad6f"], "status": "REASONED"},
    "upload-count": {"text": "max_file_uploads defaults 20; twenty maximum-sized files need not fit the POST limit.", "components": ["php8", "php"], "sources": ["php8:sc9e417e2ad6f", "php:s3cbc65590d52"], "status": "REASONED"},
    "memory-limit": {"text": "memory_limit defaults 128M, should generally exceed post_max_size, and -1 removes the bound.", "components": ["php8"], "sources": ["php8:sc9e417e2ad6f"], "status": "REASONED"},
    "input-vars": {"text": "max_input_vars defaults 1000 separately for GET, POST and COOKIE; excess is warned/truncated, not a general JSON limit.", "components": ["php8"], "sources": ["php8:s5a3f7bde8338"], "status": "REASONED"},
    "execution-time": {"text": "max_execution_time defaults 30 for web and 0 for CLI; platform/build accounting can exclude I/O, not a portable wall-clock deadline.", "components": ["php8"], "sources": ["php8:s5a3f7bde8338"], "status": "REASONED"},
    "input-time": {"text": "max_input_time defaults -1, using max_execution_time; 0 is unlimited. Example and production template select 60 seconds.", "components": ["php8", "template84"], "sources": ["php8:s5a3f7bde8338", "template84:sd72e3d69551f"], "status": "REASONED"},
    "upload-time": {"text": "Test slow/multiple uploads and coordinate server size/time limits. Per-request bounds do not replace capacity controls or rate limiting.", "components": ["php"], "sources": ["php:s3cbc65590d52"], "status": "REASONED"},
    "fpm-timeout": {"text": "request_terminate_timeout defaults 0, disabled; example selects 60s as app policy and kills overlong workers.", "components": ["php8"], "sources": ["php8:s2e692b7c86a6"], "status": "REASONED"},
    "fpm-finished": {"text": "request_terminate_timeout_track_finished defaults no; yes extends the limit past fastcgi_finish_request and into shutdown work.", "components": ["php8"], "sources": ["php8:s2e692b7c86a6"], "status": "REASONED"},
    "session-gc": {"text": "Native gc_maxlifetime defaults 1440 seconds; probabilistic collection is not auth expiry. Use timestamp expiry/cleanup; shared paths can inherit shorter lifetimes.", "components": ["php8", "php"], "sources": ["php8:s000e155a7b25", "php:s8664dc56a028"], "status": "REASONED"},
    "session-lifetime": {"text": "Native cookie_lifetime defaults 0, a browser-session cookie; Laravel uses config/session.php rather than native storage/lifetime directives.", "components": ["php8", "laravel"], "sources": ["php8:s000e155a7b25", "laravel:s98db3429151c"], "status": "REASONED"},
    "session-only-cookies": {"text": "session.use_only_cookies defaults 1; retain it to exclude GET/POST IDs. Disabling it is deprecated from PHP 8.4.", "components": ["php8"], "sources": ["php8:s000e155a7b25"], "status": "REASONED"},
    "session-storage": {"text": "Default files handler needs a private worker-writable directory outside the document root; dedicated-account mode 0700, default file mode 0600, separate untrusted-app identities.", "components": ["php8"], "sources": ["php8:s000e155a7b25"], "status": "REASONED"},
    "session-sid-length": {"text": "PHP 8.x session.sid_length defaults 32; changes are deprecated from 8.4. PHP 8.3 production template sets 26.", "components": ["php8", "template83"], "sources": ["php8:s000e155a7b25", "template83:sea3d3a4ea486"], "status": "REASONED"},
    "session-sid-bits": {"text": "PHP 8.x session.sid_bits_per_character defaults 4; changes are deprecated from 8.4. PHP 8.3 production template sets 5.", "components": ["php8", "template83"], "sources": ["php8:s000e155a7b25", "template83:sea3d3a4ea486"], "status": "REASONED"},
    "verify-listener": {"text": "Inventory all FPM listeners: Unix socket or loopback TCP 9000 only.", "components": ["php8"], "sources": ["php8:s2e692b7c86a6"], "status": "REASONED", "verify": [1]},
    "verify-tls": {"text": "The TLS probe distinguishes cited exit=60 certificate failure from reasoned exit=0 success without -k; linked fronting-server guides supply TLS configuration.", "components": ["curl"], "sources": ["curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-cookies": {"text": "Inspect login Set-Cookie for Secure, HttpOnly and SameSite=Lax.", "components": ["php8", "laravel"], "sources": ["php8:s000e155a7b25", "laravel:s98db3429151c"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "Anonymous protected routes must deny or redirect to login without protected content; require authorized success and isolated auth-removal control. Unrelated redirects/errors and anonymous Set-Cookie do not establish authentication.", "components": ["laravel"], "sources": ["laravel:sc58ba221e3cd"], "status": "REASONED", "verify": [2]},
    "verify-config": {"text": "Inspect CLI ini/settings against installed E_ALL; CLI does not establish web SAPI/FPM settings. Do not publish phpinfo.", "components": ["php", "php8"], "sources": ["php:s5840a5a0a848", "php8:s89c799077b82", "php8:s2e692b7c86a6"], "status": "REASONED", "verify": [3]},
    "verify-banner": {"text": "Fixture should give HTTP 200; expose_php On should show PHP header unless stripped, Off must hide it. Proxy stripping in both states needs SAPI inspection.", "components": ["php"], "sources": ["php:s7b2c2c19835d", "php:s2f1c806d037c"], "status": "REASONED", "verify": [4]},
    "verify-error": {"text": "Native warning fixture must disclose canary with display_errors On, then return reached marker without diagnostics and log the warning after hardening. Errors/missing logs/blank bodies are inconclusive; startup/parse errors untested.", "components": ["php8", "php"], "sources": ["php8:s89c799077b82", "php:s2f1c806d037c"], "status": "REASONED", "verify": [5]},
    "verify-laravel-error": {"text": "Repeat body probe with controlled Laravel exception, rebuild config cache after APP_DEBUG changes, and require generic response plus protected log; native fixture does not test framework errors.", "components": ["laravel"], "sources": ["laravel:s4e846bd588a8", "laravel:s6510c1aa8d96"], "status": "REASONED", "verify": [5]},
    "verify-curl-version": {"text": "The exitcode and errormsg write-out variables require curl 7.75.0 or later per the curl manual.", "components": ["curl"], "sources": ["curl:s2b2686afaf41"], "status": "REASONED", "verify": [1, 2, 4, 5]}
  }
}
````
<!-- version-basis:end -->
