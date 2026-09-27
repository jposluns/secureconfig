---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "0cd50f8008842262c1ad8033701c13325472154ad3203105e744b5db00446520",
  "components": {
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
    "debugbar": {
      "name": "Laravel Debugbar",
      "basis": "unknown",
      "sources": {
        "s7099781fdf4a": "https://github.com/fruitcake/laravel-debugbar"
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
    "plain-auth": {"text": "Plain PHP rate limiting and MFA need application/proxy/identity controls; direct references are the linked guides, not PHP Sources.", "components": ["php"], "sources": ["php:s50f85ff4fbd1", "php:s8664dc56a028"], "status": "REASONED"},
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
    "verify-tls": {"text": "HTTPS should succeed without -k; linked fronting-server guides supply TLS configuration.", "components": ["php", "laravel"], "sources": ["php:s09fdbeba0867", "laravel:s6510c1aa8d96"], "status": "REASONED", "verify": [1]},
    "verify-cookies": {"text": "Inspect login Set-Cookie for Secure, HttpOnly and SameSite=Lax.", "components": ["php8", "laravel"], "sources": ["php8:s000e155a7b25", "laravel:s98db3429151c"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "Anonymous protected routes must deny or redirect to login without protected content; require authorized success and isolated auth-removal control. Unrelated redirects/errors and anonymous Set-Cookie do not establish authentication.", "components": ["laravel"], "sources": ["laravel:sc58ba221e3cd"], "status": "REASONED", "verify": [2]},
    "verify-config": {"text": "Inspect CLI ini/settings against installed E_ALL; CLI does not establish web SAPI/FPM settings. Do not publish phpinfo.", "components": ["php", "php8"], "sources": ["php:s5840a5a0a848", "php8:s89c799077b82", "php8:s2e692b7c86a6"], "status": "REASONED", "verify": [3]},
    "verify-banner": {"text": "Fixture should give HTTP 200; expose_php On should show PHP header unless stripped, Off must hide it. Proxy stripping in both states needs SAPI inspection.", "components": ["php"], "sources": ["php:s7b2c2c19835d", "php:s2f1c806d037c"], "status": "REASONED", "verify": [4]},
    "verify-error": {"text": "Native warning fixture must disclose canary with display_errors On, then return reached marker without diagnostics and log the warning after hardening. Errors/missing logs/blank bodies are inconclusive; startup/parse errors untested.", "components": ["php8", "php"], "sources": ["php8:s89c799077b82", "php:s2f1c806d037c"], "status": "REASONED", "verify": [5]},
    "verify-laravel-error": {"text": "Repeat body probe with controlled Laravel exception, rebuild config cache after APP_DEBUG changes, and require generic response plus protected log; native fixture does not test framework errors.", "components": ["laravel"], "sources": ["laravel:s4e846bd588a8", "laravel:s6510c1aa8d96"], "status": "REASONED", "verify": [5]},
    "verify-curl-version": {"text": "Write-out fields require curl 7.75.0 or later; Sources cite PHP cURL constants, not the curl CLI minimum.", "components": ["php"], "sources": ["php:s09fdbeba0867"], "status": "REASONED", "verify": [2, 4, 5]}
  }
}
---
# PHP and Laravel: TLS and authentication

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| fpm-private: FPM requires listen per pool; exposed FastCGI permits code execution. Use a Unix socket or loopback TCP 9000; never publish container FPM. | PHP native configuration 8.x | REASONED |
| fpm-clients: listen.allowed_clients defaults unset, accepting any address; explicitly allow loopback for TCP. | PHP native configuration 8.x | REASONED |
| fpm-socket: Unix socket access uses listen.owner, listen.group and listen.mode, default 0660. | PHP native configuration 8.x | REASONED |
| cookie-secure: Native session.cookie_secure defaults 0; enable it. | PHP native configuration 8.x | REASONED |
| cookie-httponly: Native session.cookie_httponly defaults 0; enable it. | PHP native configuration 8.x | REASONED |
| cookie-samesite: Native session.cookie_samesite defaults empty; choose Lax or Strict. | PHP native configuration 8.x | REASONED |
| session-strict: session.use_strict_mode defaults 0; enable it. | PHP native configuration 8.x | REASONED |
| session-regenerate: Regenerate IDs after login/privilege changes; delete_old_session defaults false. Timestamp expiry avoids immediate deletion. | PHP documentation unknown | REASONED |
| passwords: PASSWORD_DEFAULT currently uses bcrypt; Argon2id needs an Argon2 build. Verify/rehash passwords and allow growing hashes, suggested 255 bytes. | PHP documentation unknown | REASONED |
| plain-auth: Plain PHP rate limiting and MFA need application/proxy/identity controls; direct references are the linked guides, not PHP Sources. | PHP documentation unknown | REASONED |
| laravel-debug: Set APP_ENV=production, APP_DEBUG=false and HTTPS APP_URL; debug mode exposes configuration values. | Laravel 12.x | REASONED |
| laravel-key: Generate APP_KEY with artisan key:generate; list old keys in APP_PREVIOUS_KEYS during rotation. | Laravel 12.x | REASONED |
| laravel-secure: Set SESSION_SECURE_COOKIE=true; the session secure configuration has no default. | Laravel 12.x | REASONED |
| laravel-httponly: SESSION_HTTP_ONLY defaults true; retain it. | Laravel 12.x | REASONED |
| laravel-samesite: SESSION_SAME_SITE defaults lax; strict suits admin-only apps. | Laravel 12.x | REASONED |
| laravel-proxy: Laravel 12.x trustProxies names proxies in bootstrap/app.php; wildcard trust requires exclusive proxy reachability. | Laravel 12.x | REASONED |
| laravel-urls: URL::forceHttps() or forceScheme(https) in a provider boot method forces generated HTTPS URLs. | Laravel 12.x | REASONED |
| laravel-hashes: Hash::make/check default to bcrypt; HASH_DRIVER=argon2id switches it and needsRehash detects upgrades. HASH_VERIFY=false disables rejection of other algorithms. | Laravel 12.x | REASONED |
| laravel-limiter: Define a five-per-minute login limiter keyed by email plus IP; attach throttle:login to the real route. | Laravel 12.x | REASONED |
| fortify-login: 12.x starter kits use Fortify, which throttles username plus IP and regenerates session IDs on login; standalone Fortify omits views. | Laravel 12.x | REASONED |
| fortify-mfa: Fortify twoFactorAuthentication with confirm and confirmPassword supplies TOTP and recovery codes. | Laravel 12.x | REASONED |
| socialite: Socialite supplies OAuth providers; community packages supply OIDC. Use HTTPS callbacks and linked allowlist/token checks. | Laravel 12.x | REASONED |
| laravel-cache: Keep plaintext .env untracked; build config/route caches after production inputs and rebuild on changes. Cached config does not load .env; use env only in config files. | Laravel 12.x | REASONED |
| laravel-hosts: Laravel accepts arbitrary Host headers by default; restrict hosts at the server and add anchored TrustHosts with subdomains:false. | Laravel 12.x | REASONED |
| debug-tools: Omit Telescope and Debugbar from production; Telescope local-only installation includes conditional provider registration. | Laravel 12.x; Laravel Debugbar unknown | REASONED |
| curl-peer: CURLOPT_SSL_VERIFYPEER defaults true; retain certificate verification. | PHP documentation unknown | REASONED |
| curl-host: CURLOPT_SSL_VERIFYHOST defaults 2; retain hostname checks and use CURLOPT_CAINFO for an internal CA. | PHP documentation unknown | REASONED |
| display-errors: PHP 8.x display_errors defaults On; set Off before execution. ini_set cannot hide a fatal error preventing it from running. | PHP native configuration 8.x | REASONED |
| startup-errors: display_startup_errors defaults On since PHP 8.0.0, previously Off; set Off. | PHP native configuration 8.x | REASONED |
| log-errors: log_errors defaults Off; enable it with a protected, pre-created, worker-writable log outside the document root and rotation. Unset error_log uses the SAPI logger. | PHP native configuration 8.x | REASONED |
| error-reporting: error_reporting defaults E_ALL since PHP 8.0.0; retain reporting into logs. Package/template/deployment overrides can differ. | PHP native configuration 8.x | REASONED |
| php-banner: expose_php defaults On; Off suppresses PHP own X-Powered-By header, not other layers or all application identification. | PHP native configuration 8.x; PHP documentation unknown | REASONED |
| production-template: PHP 8.4 production template disables display and enables logging, but uses E_ALL &amp; ~E_DEPRECATED and leaves expose_php enabled. | PHP production template 8.4 | REASONED |
| disable-functions: disable_functions defaults empty; test the listed process-function restrictions. Since PHP 8.0 definitions disappear and userland can redefine them; internal functions only, not a security boundary. | PHP native configuration 8.x | REASONED |
| url-fopen: allow_url_fopen defaults On; disable unnecessary URL wrappers after compatibility tests, not as a general egress policy. | PHP documentation unknown | REASONED |
| url-include: allow_url_include defaults Off, deprecated since PHP 7.4; retain Off. URL includes also require allow_url_fopen. | PHP documentation unknown | REASONED |
| basedir: open_basedir defaults NULL; allow required paths, retain OS isolation and account for disabled realpath caching. PHP 8.3 rejects runtime .. components. | PHP native configuration 8.x | REASONED |
| fpm-extensions: PHP 8.x FPM security.limit_extensions defaults .php .phar; restrict to .php, which still permits uploaded PHP dispatched by the server. | PHP native configuration 8.x | REASONED |
| upload-execution: Separate writable uploads from code, preferably outside the document root; server mappings must forbid PHP execution, including aliases/symlinks. | PHP native configuration 8.x; Laravel 12.x | REASONED |
| laravel-storage: Laravel 12.x local disk defaults storage/app/private; public disk uses storage/app/public via public/storage, which does not itself prevent PHP execution. | Laravel 12.x | REASONED |
| upload-size: upload_max_filesize defaults 2M per file; post_max_size must allow multipart overhead. | PHP native configuration 8.x | REASONED |
| post-size: post_max_size defaults 8M; excess leaves POST and FILES empty and must be rejected by the app. | PHP native configuration 8.x | REASONED |
| upload-count: max_file_uploads defaults 20; twenty maximum-sized files need not fit the POST limit. | PHP native configuration 8.x; PHP documentation unknown | REASONED |
| memory-limit: memory_limit defaults 128M, should generally exceed post_max_size, and -1 removes the bound. | PHP native configuration 8.x | REASONED |
| input-vars: max_input_vars defaults 1000 separately for GET, POST and COOKIE; excess is warned/truncated, not a general JSON limit. | PHP native configuration 8.x | REASONED |
| execution-time: max_execution_time defaults 30 for web and 0 for CLI; platform/build accounting can exclude I/O, not a portable wall-clock deadline. | PHP native configuration 8.x | REASONED |
| input-time: max_input_time defaults -1, using max_execution_time; 0 is unlimited. Example and production template select 60 seconds. | PHP native configuration 8.x; PHP production template 8.4 | REASONED |
| upload-time: Test slow/multiple uploads and coordinate server size/time limits. Per-request bounds do not replace capacity controls or rate limiting. | PHP documentation unknown | REASONED |
| fpm-timeout: request_terminate_timeout defaults 0, disabled; example selects 60s as app policy and kills overlong workers. | PHP native configuration 8.x | REASONED |
| fpm-finished: request_terminate_timeout_track_finished defaults no; yes extends the limit past fastcgi_finish_request and into shutdown work. | PHP native configuration 8.x | REASONED |
| session-gc: Native gc_maxlifetime defaults 1440 seconds; probabilistic collection is not auth expiry. Use timestamp expiry/cleanup; shared paths can inherit shorter lifetimes. | PHP native configuration 8.x; PHP documentation unknown | REASONED |
| session-lifetime: Native cookie_lifetime defaults 0, a browser-session cookie; Laravel uses config/session.php rather than native storage/lifetime directives. | PHP native configuration 8.x; Laravel 12.x | REASONED |
| session-only-cookies: session.use_only_cookies defaults 1; retain it to exclude GET/POST IDs. Disabling it is deprecated from PHP 8.4. | PHP native configuration 8.x | REASONED |
| session-storage: Default files handler needs a private worker-writable directory outside the document root; dedicated-account mode 0700, default file mode 0600, separate untrusted-app identities. | PHP native configuration 8.x | REASONED |
| session-sid-length: PHP 8.x session.sid_length defaults 32; changes are deprecated from 8.4. PHP 8.3 production template sets 26. | PHP native configuration 8.x; PHP production template 8.3 | REASONED |
| session-sid-bits: PHP 8.x session.sid_bits_per_character defaults 4; changes are deprecated from 8.4. PHP 8.3 production template sets 5. | PHP native configuration 8.x; PHP production template 8.3 | REASONED |
| verify-listener: Inventory all FPM listeners: Unix socket or loopback TCP 9000 only. | PHP native configuration 8.x | REASONED |
| verify-tls: HTTPS should succeed without -k; linked fronting-server guides supply TLS configuration. | PHP documentation unknown; Laravel 12.x | REASONED |
| verify-cookies: Inspect login Set-Cookie for Secure, HttpOnly and SameSite=Lax. | PHP native configuration 8.x; Laravel 12.x | REASONED |
| verify-auth: Anonymous protected routes must deny or redirect to login without protected content; require authorized success and isolated auth-removal control. Unrelated redirects/errors and anonymous Set-Cookie do not establish authentication. | Laravel 12.x | REASONED |
| verify-config: Inspect CLI ini/settings against installed E_ALL; CLI does not establish web SAPI/FPM settings. Do not publish phpinfo. | PHP documentation unknown; PHP native configuration 8.x | REASONED |
| verify-banner: Fixture should give HTTP 200; expose_php On should show PHP header unless stripped, Off must hide it. Proxy stripping in both states needs SAPI inspection. | PHP documentation unknown | REASONED |
| verify-error: Native warning fixture must disclose canary with display_errors On, then return reached marker without diagnostics and log the warning after hardening. Errors/missing logs/blank bodies are inconclusive; startup/parse errors untested. | PHP native configuration 8.x; PHP documentation unknown | REASONED |
| verify-laravel-error: Repeat body probe with controlled Laravel exception, rebuild config cache after APP_DEBUG changes, and require generic response plus protected log; native fixture does not test framework errors. | Laravel 12.x | REASONED |
| verify-curl-version: Write-out fields require curl 7.75.0 or later; Sources cite PHP cURL constants, not the curl CLI minimum. | PHP documentation unknown | REASONED |
<!-- version-basis:end -->

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

**REASONED: deployment checks have not been demonstrated.** The authoring environment has no PHP or PHP-FPM runtime, no Docker or Podman, and no supplied PHP/Laravel deployment. The listener, TLS, cookie, authentication, banner, and error-disclosure checks require a real deployment. Expected outcomes are REASONED from the cited PHP, Laravel, and fronting-server documentation.

Paste each guarded block whole. Substitute a full HTTPS URL inside the single quotes on its `set --` line; use a URL without a literal apostrophe or embedded credentials. The fixed `app.example.com` examples are illustrations. For deployment requests, use the guarded blocks with the application's actual URL. Curl's `http`, `exit`, and `err` write-out fields require curl 7.75.0 or later. The trailing `|| true` keeps a failed probe from ending the shell; it does not indicate success.

For the protected-route check, confirm the same route returns the expected protected content to an authorized session. In an isolated exposed-state test, removing the authentication requirement must make that content accessible anonymously; restoring it must produce the documented denial or login redirect. A missing route or an unrelated error is not evidence of authentication.

REASONED: following block; FPM listener, HTTPS and cookie inspection. The guide records no PHP/PHP-FPM runtime, container runtime or supplied deployment; expectations follow its cited PHP and Laravel documentation, not a recorded run.

```bash
ss -xlnp   # read every listener; php-fpm: Unix socket; with TCP, ss -tlnp shows 127.0.0.1:9000 only
curl -q -g --noproxy '*' -sI https://app.example.com/                             # succeeds without -k
curl -q -g --noproxy '*' -sI https://app.example.com/login | grep -i set-cookie   # secure; httponly; samesite=lax
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

Expect `display_errors=Off`, `display_startup_errors=Off`, `log_errors=On`, the intended protected `error_log`, `expose_php=Off`, and `error_reporting` equal to the installed version's `E_ALL`. PHP's diagnostic values can change between versions, so compare against the printed constant rather than a copied integer. CLI inspection does not establish FPM or Apache's effective configuration: inspect that SAPI's loaded files and overrides separately, including the FPM pool settings. Do not publish a `phpinfo()` endpoint.

**REASONED: banner and native PHP error disclosure.** No web SAPI or deployment was available. In an isolated deployment matching production, temporarily serve this controlled fixture through the intended PHP handler and proxy. Use PHP's built-in error handler, without framework bootstrapping or application error-handler overrides. Restrict access to the test operator and remove the fixture afterwards. The fixed warning text contains no secret. [PHP `trigger_error()`](https://www.php.net/manual/en/function.trigger-error.php).

REASONED: following block; controlled native PHP warning fixture. The guide records no PHP/PHP-FPM runtime, container runtime or supplied deployment; expectations follow its cited PHP and Laravel documentation, not a recorded run.

```php
<?php
trigger_error('SECURECONFIG_PHP_ERROR_CANARY', E_USER_WARNING);
echo "SECURECONFIG_PHP_REACHED\n";
```

First inspect the fixture's response headers:

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

With `expose_php=On`, the exposed-state response is expected to contain `X-Powered-By: PHP/...` unless another layer strips it. With `expose_php=Off`, it must be absent. Require a successful transfer and the fixture's expected HTTP 200 response. If the proxy strips the header in both states, this checks the externally visible response only; attribute the PHP setting through the active SAPI configuration. [PHP banner behavior](https://www.php.net/manual/en/security.hiding.php).

Then inspect the body from the same fixture URL:

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

In the isolated exposed state, `display_errors=On` with `error_reporting=E_ALL` should disclose `SECURECONFIG_PHP_ERROR_CANARY` in the response. After applying section 5, the HTTP 200 body must contain `SECURECONFIG_PHP_REACHED` without the warning marker or PHP diagnostics, while the protected log receives the warning marker for that request. A blank response, redirect, 404, failed transfer, or missing log entry does not satisfy this check. This fixture tests a runtime warning; it does not exercise startup or parse errors. [PHP error configuration](https://www.php.net/manual/en/errorfunc.configuration.php).

For Laravel 12.x, repeat the body probe against a controlled route that raises an exception with a distinctive, non-secret message. In an isolated deployment, compare `APP_DEBUG=true` with `APP_DEBUG=false`, rebuilding cached configuration after each change. The protected state must show a generic error response without the exception message, trace, or configuration values; confirm the matching exception in the protected application log. The native PHP fixture alone does not establish Laravel's framework error behavior. [Laravel debug mode](https://laravel.com/framework/docs/12.x/deployment#debug-mode).

## Sources (checked September 2026)

- PHP FPM configuration (`listen`, `listen.allowed_clients`, `listen.owner`) (PHP 8.x): https://www.php.net/manual/en/install.fpm.configuration.php
- PHP session runtime configuration (PHP 8.x): https://www.php.net/manual/en/session.configuration.php
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
