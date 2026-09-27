---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "d7d88bbf754652ad64cd1044824c2cc41633732451a815523e2adabc25c7a2a4",
  "components": {
    "puma-readme": {
      "name": "Puma README",
      "basis": "aef89221e4d729c3133c723844382331ba3bbbd9",
      "sources": {
        "se5323687b58f": "https://github.com/puma/puma/blob/aef89221e4d729c3133c723844382331ba3bbbd9/README.md"
      }
    },
    "puma-dsl": {
      "name": "Puma DSL",
      "basis": "d70de8b4e926f1f5fa0269dc46cdfadf52562628",
      "sources": {
        "s8d510226544c": "https://github.com/puma/puma/blob/d70de8b4e926f1f5fa0269dc46cdfadf52562628/lib/puma/dsl.rb"
      }
    },
    "puma": {
      "name": "Puma defaults",
      "basis": "v8.0.2",
      "sources": {
        "s9687194339f3": "https://github.com/puma/puma/blob/v8.0.2/lib/puma/configuration.rb#L369-L384",
        "s8e2a34b121ba": "https://github.com/puma/puma/blob/v8.0.2/lib/puma/configuration.rb#L174",
        "s1d9011be835b": "https://github.com/puma/puma/blob/v8.0.2/lib/puma/const.rb#L214-L215"
      }
    },
    "rails": {
      "name": "Rails documentation",
      "basis": "unknown",
      "sources": {
        "s0e5c35fd756d": "https://api.rubyonrails.org/classes/ActionController/RateLimiting/ClassMethods.html",
        "s22fb0dcbb6e1": "https://api.rubyonrails.org/classes/ActionDispatch/RemoteIp.html",
        "sba5f72c7a627": "https://api.rubyonrails.org/classes/ActionDispatch/Session/CookieStore.html",
        "sae7bf5d75809": "https://api.rubyonrails.org/classes/ActiveModel/SecurePassword/ClassMethods.html",
        "s574629d873e4": "https://guides.rubyonrails.org/configuring.html",
        "s2abb8f0ec8d2": "https://guides.rubyonrails.org/security.html"
      }
    },
    "assume": {
      "name": "Action Pack",
      "basis": "7.1",
      "sources": {
        "sf720dd92b2e7": "https://github.com/rails/rails/blob/ffcbf6f205363f8c2fb3e9834bc86690dd59f1cb/actionpack/CHANGELOG.md"
      }
    },
    "credentials": {
      "name": "Rails credentials source",
      "basis": "e4cd6ae6f1f0a847958b3aa846c9fd8a3014922a",
      "sources": {
        "saab0a90edc0c": "https://github.com/rails/rails/blob/e4cd6ae6f1f0a847958b3aa846c9fd8a3014922a/railties/lib/rails/commands/credentials/USAGE"
      }
    },
    "rack": {
      "name": "Rack::Attack",
      "basis": "unknown",
      "sources": {
        "s1e5ca83efb79": "https://github.com/rack/rack-attack"
      }
    },
    "sidekiq": {
      "name": "Sidekiq Web",
      "basis": "unknown",
      "sources": {
        "s106d0b1ced6e": "https://github.com/sidekiq/sidekiq/wiki/Monitoring"
      }
    },
    "net-http": {
      "name": "Net::HTTP source",
      "basis": "39cf5f648a9e5e25312909a2dc26681edaa2402c",
      "sources": {
        "sbcafa3e06a73": "https://github.com/ruby/net-http/blob/39cf5f648a9e5e25312909a2dc26681edaa2402c/lib/net/http.rb"
      }
    },
    "openssl-ruby": {
      "name": "Ruby OpenSSL source",
      "basis": "a77ed4b9908e179cea8f018f7e245535301746a8",
      "sources": {
        "sf0192683941c": "https://github.com/ruby/openssl/blob/a77ed4b9908e179cea8f018f7e245535301746a8/lib/openssl/ssl.rb"
      }
    },
    "openssl": {
      "name": "OpenSSL documentation",
      "basis": "unknown",
      "sources": {
        "se3858048f9d6": "https://docs.openssl.org/master/man7/openssl-env/"
      }
    }
  },
  "claims": {
    "puma-default": {"text": "Puma v8.0.2 defaults plaintext 9292 on :: when non-loopback IPv6 exists, otherwise 0.0.0.0.", "components": ["puma"], "sources": ["puma:s9687194339f3", "puma:s8e2a34b121ba", "puma:s1d9011be835b"], "status": "REASONED"},
    "puma-private": {"text": "Bind loopback TCP 3000 or Unix socket with proxy TLS; bind accepts tcp, unix and ssl URIs only.", "components": ["puma-readme", "puma-dsl"], "sources": ["puma-readme:se5323687b58f", "puma-dsl:s8d510226544c"], "status": "REASONED"},
    "puma-tls": {"text": "Native ssl bind example uses 8443 with key/cert; ca and verify_mode configure client certificates.", "components": ["puma-dsl"], "sources": ["puma-dsl:s8d510226544c"], "status": "REASONED"},
    "force-ssl": {"text": "force_ssl enables HTTPS redirect and HSTS; ssl_options defaults hsts subdomains true. Encrypted cookies still need HTTPS.", "components": ["rails"], "sources": ["rails:s574629d873e4", "rails:sba5f72c7a627"], "status": "REASONED"},
    "assume-ssl": {"text": "Rails 7.1+ assume_ssl says the proxy terminated TLS before forwarding HTTP.", "components": ["rails", "assume"], "sources": ["rails:s574629d873e4", "assume:sf720dd92b2e7"], "status": "REASONED"},
    "hosts": {"text": "Add the application hostname to config.hosts for Host allowlisting.", "components": ["rails"], "sources": ["rails:s574629d873e4"], "status": "REASONED"},
    "session": {"text": "CookieStore example selects Secure, HttpOnly, SameSite=Lax and 14-day expiry.", "components": ["rails"], "sources": ["rails:sba5f72c7a627", "rails:s574629d873e4"], "status": "REASONED"},
    "trusted-proxies": {"text": "Defaults include loopback/private/link-local; public proxies require an enumerable. Without a proxy, client-controlled X-Forwarded-For makes remote_ip unsuitable for allowlists/rate limits.", "components": ["rails"], "sources": ["rails:s22fb0dcbb6e1"], "status": "REASONED"},
    "same-site-default": {"text": "cookies_same_site_protection defaults lax from load_defaults 6.1.", "components": ["rails"], "sources": ["rails:s574629d873e4"], "status": "REASONED"},
    "auth-generator": {"text": "Rails 8.0+ authentication generator supplies users, sessions and password reset using has_secure_password.", "components": ["rails"], "sources": ["rails:s2abb8f0ec8d2"], "status": "REASONED"},
    "passwords": {"text": "has_secure_password needs bcrypt ~> 3.1.7 and password_digest; authenticate returns user/false, validates presence and 72-byte limit, and needs an app minimum length.", "components": ["rails"], "sources": ["rails:sae7bf5d75809"], "status": "REASONED"},
    "rate-limit": {"text": "Controller rate_limit allows ten attempts per three minutes for create; needs ActiveSupport::Cache, defaulting to action_controller.cache_store.", "components": ["rails"], "sources": ["rails:s0e5c35fd756d"], "status": "REASONED"},
    "rack-attack": {"text": "Rack::Attack supplies path throttles/blocklists; configure its initializer and Rails railtie installs middleware.", "components": ["rack"], "sources": ["rack:s1e5ca83efb79"], "status": "REASONED"},
    "credentials": {"text": "Edit encrypted credentials with credentials:edit; RAILS_MASTER_KEY overrides master.key, which Rails gitignores.", "components": ["credentials", "rails"], "sources": ["credentials:saab0a90edc0c", "rails:s2abb8f0ec8d2"], "status": "REASONED"},
    "require-key": {"text": "require_master_key=true refuses boot without the decryption key.", "components": ["rails"], "sources": ["rails:s574629d873e4"], "status": "REASONED"},
    "mfa": {"text": "Rails has no built-in second factor; add TOTP or an identity layer and use linked MFA/OIDC guidance.", "components": ["rails"], "sources": ["rails:s2abb8f0ec8d2"], "status": "REASONED"},
    "sidekiq-open": {"text": "Bare /sidekiq mount has no auth; reachable users can read job arguments and retry, kill or clear queues.", "components": ["sidekiq"], "sources": ["sidekiq:s106d0b1ced6e"], "status": "REASONED"},
    "sidekiq-devise": {"text": "Devise authenticate constraint requires a signed-in admin; keep Sidekiq off the public internet even with auth.", "components": ["sidekiq"], "sources": ["sidekiq:s106d0b1ced6e"], "status": "REASONED"},
    "sidekiq-basic": {"text": "Otherwise add Rack Basic auth with credentials outside source, equal-length SHA256 secure_compare inputs and non-short-circuit &.", "components": ["sidekiq"], "sources": ["sidekiq:s106d0b1ced6e"], "status": "REASONED"},
    "client-tls": {"text": "Net::HTTP.start use_ssl defaults VERIFY_PEER; supply ca_file before handshake, not inside the opened block. Never use VERIFY_NONE.", "components": ["net-http"], "sources": ["net-http:sbcafa3e06a73"], "status": "REASONED"},
    "client-store": {"text": "Ruby SSLContext loads system trust through set_default_paths; SSL_CERT_FILE and SSL_CERT_DIR select an internal CA store.", "components": ["openssl-ruby", "openssl"], "sources": ["openssl-ruby:sf0192683941c", "openssl:se3858048f9d6"], "status": "REASONED"},
    "verify-bind": {"text": "Inventory every listener; Puma should bind only 127.0.0.1:3000.", "components": ["puma-readme", "puma-dsl"], "sources": ["puma-readme:se5323687b58f", "puma-dsl:s8d510226544c"], "status": "REASONED", "verify": [1]},
    "verify-https": {"text": "HTTP should redirect 301 to HTTPS; inspect HSTS and Secure/HttpOnly/SameSite=Lax cookies.", "components": ["rails"], "sources": ["rails:s574629d873e4", "rails:sba5f72c7a627"], "status": "REASONED", "verify": [1]},
    "verify-dashboard": {"text": "Anonymous dashboard request should return login 302 or 401.", "components": ["rails"], "sources": ["rails:s2abb8f0ec8d2"], "status": "REASONED", "verify": [1]},
    "verify-sidekiq": {"text": "Basic needs 401 plus WWW-Authenticate, Devise login 302; bare 404 is inconclusive, dashboard 200 is exposure. Require authorized success.", "components": ["sidekiq"], "sources": ["sidekiq:s106d0b1ced6e"], "status": "REASONED", "verify": [1]},
    "verify-key": {"text": "git ls-files config/master.key should print nothing.", "components": ["credentials"], "sources": ["credentials:saab0a90edc0c"], "status": "REASONED", "verify": [1]}
  }
}
---
# Ruby on Rails and Puma: TLS and authentication

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| puma-default: Puma v8.0.2 defaults plaintext 9292 on :: when non-loopback IPv6 exists, otherwise 0.0.0.0. | Puma defaults v8.0.2 | REASONED |
| puma-private: Bind loopback TCP 3000 or Unix socket with proxy TLS; bind accepts tcp, unix and ssl URIs only. | Puma README aef89221e4d729c3133c723844382331ba3bbbd9; Puma DSL d70de8b4e926f1f5fa0269dc46cdfadf52562628 | REASONED |
| puma-tls: Native ssl bind example uses 8443 with key/cert; ca and verify_mode configure client certificates. | Puma DSL d70de8b4e926f1f5fa0269dc46cdfadf52562628 | REASONED |
| force-ssl: force_ssl enables HTTPS redirect and HSTS; ssl_options defaults hsts subdomains true. Encrypted cookies still need HTTPS. | Rails documentation unknown | REASONED |
| assume-ssl: Rails 7.1+ assume_ssl says the proxy terminated TLS before forwarding HTTP. | Rails documentation unknown; Action Pack 7.1 | REASONED |
| hosts: Add the application hostname to config.hosts for Host allowlisting. | Rails documentation unknown | REASONED |
| session: CookieStore example selects Secure, HttpOnly, SameSite=Lax and 14-day expiry. | Rails documentation unknown | REASONED |
| trusted-proxies: Defaults include loopback/private/link-local; public proxies require an enumerable. Without a proxy, client-controlled X-Forwarded-For makes remote_ip unsuitable for allowlists/rate limits. | Rails documentation unknown | REASONED |
| same-site-default: cookies_same_site_protection defaults lax from load_defaults 6.1. | Rails documentation unknown | REASONED |
| auth-generator: Rails 8.0+ authentication generator supplies users, sessions and password reset using has_secure_password. | Rails documentation unknown | REASONED |
| passwords: has_secure_password needs bcrypt ~&gt; 3.1.7 and password_digest; authenticate returns user/false, validates presence and 72-byte limit, and needs an app minimum length. | Rails documentation unknown | REASONED |
| rate-limit: Controller rate_limit allows ten attempts per three minutes for create; needs ActiveSupport::Cache, defaulting to action_controller.cache_store. | Rails documentation unknown | REASONED |
| rack-attack: Rack::Attack supplies path throttles/blocklists; configure its initializer and Rails railtie installs middleware. | Rack::Attack unknown | REASONED |
| credentials: Edit encrypted credentials with credentials:edit; RAILS_MASTER_KEY overrides master.key, which Rails gitignores. | Rails credentials source e4cd6ae6f1f0a847958b3aa846c9fd8a3014922a; Rails documentation unknown | REASONED |
| require-key: require_master_key=true refuses boot without the decryption key. | Rails documentation unknown | REASONED |
| mfa: Rails has no built-in second factor; add TOTP or an identity layer and use linked MFA/OIDC guidance. | Rails documentation unknown | REASONED |
| sidekiq-open: Bare /sidekiq mount has no auth; reachable users can read job arguments and retry, kill or clear queues. | Sidekiq Web unknown | REASONED |
| sidekiq-devise: Devise authenticate constraint requires a signed-in admin; keep Sidekiq off the public internet even with auth. | Sidekiq Web unknown | REASONED |
| sidekiq-basic: Otherwise add Rack Basic auth with credentials outside source, equal-length SHA256 secure_compare inputs and non-short-circuit &amp;. | Sidekiq Web unknown | REASONED |
| client-tls: Net::HTTP.start use_ssl defaults VERIFY_PEER; supply ca_file before handshake, not inside the opened block. Never use VERIFY_NONE. | Net::HTTP source 39cf5f648a9e5e25312909a2dc26681edaa2402c | REASONED |
| client-store: Ruby SSLContext loads system trust through set_default_paths; SSL_CERT_FILE and SSL_CERT_DIR select an internal CA store. | Ruby OpenSSL source a77ed4b9908e179cea8f018f7e245535301746a8; OpenSSL documentation unknown | REASONED |
| verify-bind: Inventory every listener; Puma should bind only 127.0.0.1:3000. | Puma README aef89221e4d729c3133c723844382331ba3bbbd9; Puma DSL d70de8b4e926f1f5fa0269dc46cdfadf52562628 | REASONED |
| verify-https: HTTP should redirect 301 to HTTPS; inspect HSTS and Secure/HttpOnly/SameSite=Lax cookies. | Rails documentation unknown | REASONED |
| verify-dashboard: Anonymous dashboard request should return login 302 or 401. | Rails documentation unknown | REASONED |
| verify-sidekiq: Basic needs 401 plus WWW-Authenticate, Devise login 302; bare 404 is inconclusive, dashboard 200 is exposure. Require authorized success. | Sidekiq Web unknown | REASONED |
| verify-key: git ls-files config/master.key should print nothing. | Rails credentials source e4cd6ae6f1f0a847958b3aa846c9fd8a3014922a | REASONED |
<!-- version-basis:end -->

Puma's default bind is `tcp://[::]:9292` when the host has a non-loopback IPv6 address, otherwise `tcp://0.0.0.0:9292` (as of v8.0.2): every interface, plain HTTP. Rails encrypts its session cookie but still sends it in clear unless HTTPS is enforced. Preferred layout: bind Puma to loopback and terminate TLS in a reverse proxy ([nginx.md](nginx.md), [caddy.md](caddy.md), [apache.md](apache.md)) or behind [cloudflare.md](cloudflare.md), with a certificate from [free-certificates.md](free-certificates.md). Puma can also terminate TLS itself, shown below.

## 1. Bind Puma privately

```ruby
# config/puma.rb
bind "tcp://127.0.0.1:3000"
# or: bind "unix:///var/run/puma.sock"
# Puma terminating TLS itself (only when no proxy is in front):
# bind "ssl://0.0.0.0:8443?key=/etc/ssl/private/server.key&cert=/etc/ssl/certs/server.crt"
```

`bind` accepts only `tcp://`, `unix://`, and `ssl://` URIs. The `ssl://` query string also takes `ca=` and `verify_mode=` for client certificates ([machine-auth.md](machine-auth.md)).

## 2. Rails behind the proxy

```ruby
# config/environments/production.rb
config.force_ssl = true      # ActionDispatch::SSL: HTTPS redirect, HSTS per config.ssl_options (default hsts: { subdomains: true })
config.assume_ssl = true     # Rails 7.1+: the proxy terminated TLS and forwards plain HTTP
config.hosts << "app.example.com"   # Host header allowlist (DNS rebinding)
config.session_store :cookie_store, key: "_app_session", secure: true, httponly: true, same_site: :lax, expire_after: 14.days
```

`config.action_dispatch.trusted_proxies` already covers loopback, private, and link-local ranges, so a same-host proxy needs nothing more. A proxy on a public address must be listed as an enumerable, for example `config.action_dispatch.trusted_proxies = [IPAddr.new("203.0.113.10")]`; a single value is not supported. Without any proxy, `X-Forwarded-For` is client-controlled, so do not trust `request.remote_ip` for rate limits or allowlists. `config.action_dispatch.cookies_same_site_protection` defaults to `:lax` from `load_defaults 6.1`.

## 3. Authentication

Follow [authentication.md](authentication.md). Rails specifics:

- Rails 8.0 and later: `bin/rails generate authentication` "Generates a basic authentication system with users, sessions, and password reset", built on `has_secure_password`. Prefer it to hand-rolled login code.
- `has_secure_password` needs `gem "bcrypt", "~> 3.1.7"` and a `password_digest` column; `user.authenticate(password)` returns the user or `false`. It validates presence and the 72-byte bcrypt limit; add your own minimum length.
- Rate-limit login in the controller (needs an `ActiveSupport::Cache` store; defaults to `config.action_controller.cache_store`):

```ruby
class SessionsController < ApplicationController
  rate_limit to: 10, within: 3.minutes, only: :create
end
```

- For path-level throttles and blocklists, [Rack::Attack](https://github.com/rack/rack-attack) (`gem "rack-attack"`, configured in `config/initializers/rack_attack.rb`; its railtie adds the middleware in Rails).
- Secrets live in `config/credentials.yml.enc`, edited with `bin/rails credentials:edit`; the decryption key is `config/master.key` (Rails adds it to `.gitignore`) or `ENV["RAILS_MASTER_KEY"]`, which takes precedence. Set `config.require_master_key = true` so a deployment without the key refuses to boot instead of running half-configured.
- MFA: Rails has no built-in second factor. Add TOTP in the app or front it with an identity layer; options in [mfa.md](mfa.md). OIDC login follows [oidc-integration.md](oidc-integration.md).

Sidekiq's Web UI is a common blind spot. Mounted the usual way it has no authentication of its own:

```ruby
# config/routes.rb -- unsafe as written
require "sidekiq/web"
mount Sidekiq::Web => "/sidekiq"
```

Anyone who reaches `/sidekiq` can read the arguments of the jobs it lists, which routinely carry tokens, email addresses, and record IDs, and can retry, kill, or clear queues. Gate the mount; these route snippets go inside your `Rails.application.routes.draw` block. With Devise, wrap it in an `authenticate` constraint so only a signed-in admin reaches it:

```ruby
authenticate :user, ->(u) { u.admin? } do
  mount Sidekiq::Web => "/sidekiq"
end
```

Without Devise, put HTTP Basic Auth in front of the Rack app, a separate credential kept out of source and compared in constant time (the SHA256 digests give `secure_compare` equal-length inputs, and `&` avoids a short-circuit that would leak which half matched):

```ruby
# config/initializers/sidekiq.rb
require "sidekiq/web"
Sidekiq::Web.use(Rack::Auth::Basic) do |user, password|
  ActiveSupport::SecurityUtils.secure_compare(
    ::Digest::SHA256.hexdigest(user), ::Digest::SHA256.hexdigest(ENV.fetch("SIDEKIQ_USER"))) &
    ActiveSupport::SecurityUtils.secure_compare(
      ::Digest::SHA256.hexdigest(password), ::Digest::SHA256.hexdigest(ENV.fetch("SIDEKIQ_PASSWORD")))
end
```

Never mount it bare, and keep it off the public internet even behind auth.

## 4. Client-side TLS discipline

```ruby
Net::HTTP.start("api.example.com", 443,
                use_ssl: true,                                  # verify_mode defaults to OpenSSL::SSL::VERIFY_PEER
                ca_file: "/etc/ssl/certs/internal-ca.pem") do |http|   # internal CA; or set SSL_CERT_FILE in the environment
  http.request(Net::HTTP::Get.new("/"))
end
```

`Net::HTTP.start` takes `use_ssl`, `ca_file`, `verify_mode`, and the other SSL settings in its options hash and applies them when it opens the connection. Assigning `http.ca_file` inside the block comes after the handshake and does not affect it; to set attributes on an instance, use `Net::HTTP.new` and set them before calling `start`.

Never set `verify_mode = OpenSSL::SSL::VERIFY_NONE`. Ruby's default SSL context loads the system store through `set_default_paths`, and OpenSSL reads `SSL_CERT_FILE` and `SSL_CERT_DIR` to locate that store, so an internal CA goes there (see [self-signed.md](self-signed.md)) rather than into a disabled check.

## Verify

REASONED: following block; Puma binds, Rails HTTPS/cookies/login, Sidekiq denial and master-key tracking. No application deployment or run outcome is recorded here; these checks are reasoned from the cited Puma, Rails and Sidekiq sources.

```bash
ss -tlnp   # read every listener; puma/ruby: 127.0.0.1:3000 only
curl -q -sI http://app.example.com/                                 # 301 to https:// (force_ssl)
curl -q -sI https://app.example.com/ | grep -iE 'strict-transport|set-cookie'   # HSTS; secure; httponly; samesite=lax
curl -q -s -o /dev/null -w '%{http_code}\n' https://app.example.com/dashboard    # 302 to login, or 401
curl -q -sS -i https://app.example.com/sidekiq
# if you run Sidekiq Web, read the headers, not just the code: Basic Auth answers 401 with a
# WWW-Authenticate: Basic header; the Devise constraint answers 302 with a Location pointing at your
# login path (a bare 404 is inconclusive, it also means nothing is mounted there). A 200 that returns
# the Sidekiq dashboard is the exposure. Then confirm an authorized request does reach it
git ls-files config/master.key                                   # prints nothing
```

## Sources (checked September 2026)

- Puma README (binding): https://github.com/puma/puma/blob/aef89221e4d729c3133c723844382331ba3bbbd9/README.md
- Puma DSL (`bind`, `ssl_bind`, default bind): https://github.com/puma/puma/blob/d70de8b4e926f1f5fa0269dc46cdfadf52562628/lib/puma/dsl.rb
- Puma default TCP port `9292` (`tcp_port: 9292`, L174) and default bind host (L369-L384): `::` when a non-loopback IPv6 interface exists, else `0.0.0.0` (pinned tag v8.0.2): https://github.com/puma/puma/blob/v8.0.2/lib/puma/configuration.rb#L369-L384 and https://github.com/puma/puma/blob/v8.0.2/lib/puma/configuration.rb#L174
- Puma `UNSPECIFIED_IPV4 = "0.0.0.0"` and `UNSPECIFIED_IPV6 = "::"` (pinned tag v8.0.2): https://github.com/puma/puma/blob/v8.0.2/lib/puma/const.rb#L214-L215
- Rails configuring guide (`force_ssl`, `assume_ssl`, `ssl_options`, `hosts`, `session_store`, `cookies_same_site_protection`, `require_master_key`): https://guides.rubyonrails.org/configuring.html
- Action Pack 7.1 changelog (`ActionDispatch::AssumeSSL`): https://github.com/rails/rails/blob/ffcbf6f205363f8c2fb3e9834bc86690dd59f1cb/actionpack/CHANGELOG.md
- `ActionDispatch::RemoteIp` (trusted proxies, spoofing warning): https://api.rubyonrails.org/classes/ActionDispatch/RemoteIp.html
- `ActionDispatch::Session::CookieStore` options: https://api.rubyonrails.org/classes/ActionDispatch/Session/CookieStore.html
- Rails security guide (authentication generator, `has_secure_password`, `rate_limit`, credentials): https://guides.rubyonrails.org/security.html
- `has_secure_password`: https://api.rubyonrails.org/classes/ActiveModel/SecurePassword/ClassMethods.html
- `ActionController::RateLimiting`: https://api.rubyonrails.org/classes/ActionController/RateLimiting/ClassMethods.html
- `bin/rails credentials:help` text (`master.key`, `RAILS_MASTER_KEY`): https://github.com/rails/rails/blob/e4cd6ae6f1f0a847958b3aa846c9fd8a3014922a/railties/lib/rails/commands/credentials/USAGE
- Rack::Attack README: https://github.com/rack/rack-attack
- Sidekiq Web UI security (the mount, the Devise `authenticate` constraint, and `Rack::Auth::Basic`): https://github.com/sidekiq/sidekiq/wiki/Monitoring
- Net::HTTP source (`verify_mode`, `ca_file`, `VERIFY_PEER` default): https://github.com/ruby/net-http/blob/39cf5f648a9e5e25312909a2dc26681edaa2402c/lib/net/http.rb
- Ruby OpenSSL `SSLContext` defaults (`DEFAULT_CERT_STORE.set_default_paths`, `VERIFY_PEER`): https://github.com/ruby/openssl/blob/a77ed4b9908e179cea8f018f7e245535301746a8/lib/openssl/ssl.rb
- OpenSSL environment variables (`SSL_CERT_FILE`, `SSL_CERT_DIR`): https://docs.openssl.org/master/man7/openssl-env/
