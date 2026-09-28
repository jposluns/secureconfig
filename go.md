---
version_basis: {
  "schema": 1,
  "checked": "2026-09-27",
  "documentation_checked": "2026-09",
  "body_sha256": "a76b9f18469b8277f3832a03d038c405bf34164e766365e26afc108fc6d1ea35",
  "components": {
    "http": {
      "name": "Go net/http documentation",
      "basis": "unknown",
      "sources": {
        "s75405f80decc": "https://pkg.go.dev/net/http",
        "s6ab9e32b7795": "https://pkg.go.dev/net/http#Server"
      }
    },
    "tls": {
      "name": "Go crypto/tls documentation",
      "basis": "unknown",
      "sources": {
        "se2152a9c28fc": "https://pkg.go.dev/crypto/tls"
      }
    },
    "x509": {
      "name": "Go certificate-store qualification",
      "basis": "1.27",
      "sources": {
        "se65b937f9e1e": "https://pkg.go.dev/crypto/x509@go1.27.0"
      }
    },
    "bcrypt": {
      "name": "Go bcrypt documentation",
      "basis": "unknown",
      "sources": {
        "s99bb1157593c": "https://pkg.go.dev/golang.org/x/crypto/bcrypt"
      }
    },
    "argon": {
      "name": "Go Argon2 documentation",
      "basis": "unknown",
      "sources": {
        "s95fa46eac674": "https://pkg.go.dev/golang.org/x/crypto/argon2"
      }
    },
    "rate": {
      "name": "Go rate documentation",
      "basis": "unknown",
      "sources": {
        "s5c3fdae5a0af": "https://pkg.go.dev/golang.org/x/time/rate"
      }
    },
    "oidc": {
      "name": "go-oidc documentation",
      "basis": "v3",
      "sources": {
        "s60cc1d7a8fe6": "https://pkg.go.dev/github.com/coreos/go-oidc/v3/oidc"
      }
    },
    "pprof": {
      "name": "Go pprof documentation",
      "basis": "unknown",
      "sources": {
        "s0246034dddd1": "https://pkg.go.dev/net/http/pprof"
      }
    },
    "headers": {
      "name": "Go header-count qualification",
      "basis": "1.27",
      "sources": {
        "sa4a9473fc6f8": "https://pkg.go.dev/net/http@go1.27.0#MaxBytesReader"
      }
    },
    "deadlines": {
      "name": "Go per-request deadline minimum",
      "basis": "1.20+",
      "sources": {
        "s251e0db38b90": "https://pkg.go.dev/net/http#ResponseController"
      }
    },
    "expvar": {
      "name": "Go expvar documentation",
      "basis": "unknown",
      "sources": {
        "se49529035a0c": "https://pkg.go.dev/expvar"
      }
    },
    "linux": {
      "name": "Linux port-threshold documentation",
      "basis": "unknown",
      "sources": {
        "s12e5a0911ec2": "https://docs.kernel.org/networking/ip-sysctl.html#ip-unprivileged-port-start"
      }
    },
    "request": {
      "name": "Go Request.Host source",
      "basis": "1.27.0",
      "sources": {
        "sfdeabbeca746": "https://pkg.go.dev/net/http@go1.27.0#Request"
      }
    }
  },
  "claims": {
    "tls": {"text": "Direct TLS listens on :443 using the leaf-plus-intermediates certificate and private key; ReadHeaderTimeout is 10 seconds.", "components": ["http", "tls"], "sources": ["http:s75405f80decc", "tls:se2152a9c28fc"], "status": "REASONED"},
    "redirect": {"text": "Port :80 sends a 301 to https:// plus the fixed canonicalHost and an origin-form request path; empty or non-path RequestURI values fall back to /. Never build the destination from r.Host.", "components": ["http", "request"], "sources": ["http:s75405f80decc", "request:sfdeabbeca746"], "status": "REASONED"},
    "tls-min": {"text": "crypto/tls defaults to TLS 1.2 minimum as of September 2026; explicitly set MinVersion=VersionTLS12.", "components": ["tls"], "sources": ["tls:se2152a9c28fc"], "status": "REASONED"},
    "privilege": {"text": "Linux privileged-port threshold defaults to 1024 but is configurable per namespace; root or CAP_NET_BIND_SERVICE is needed below it in the usual configuration.", "components": ["linux"], "sources": ["linux:s12e5a0911ec2"], "status": "REASONED"},
    "proxy": {"text": "Bind 127.0.0.1:8080 behind a TLS proxy; net/http has no proxy trust setting, so accept forwarded headers only from the isolated, overwriting proxy.", "components": ["http"], "sources": ["http:s75405f80decc"], "status": "REASONED"},
    "proxy-headers": {"text": "Set HSTS and other security headers at the proxy per the linked headers guide.", "components": ["http"], "sources": ["http:s75405f80decc"], "status": "REASONED"},
    "bcrypt": {"text": "Use bcrypt cost 12; DefaultCost is 10, inputs over 72 bytes are rejected and CompareHashAndPassword returns nil on match.", "components": ["bcrypt"], "sources": ["bcrypt:s99bb1157593c"], "status": "REASONED"},
    "argon": {"text": "IDKey returns raw bytes; retain random salt and parameters. RFC 9106 choices are time=1/memory=2 GiB/threads=4 or time=3/memory=64 MiB/threads=4.", "components": ["argon"], "sources": ["argon:s95fa46eac674"], "status": "REASONED"},
    "cookies": {"text": "Set session cookie Path=/, Secure, HttpOnly and SameSite=Lax.", "components": ["http"], "sources": ["http:s75405f80decc"], "status": "REASONED"},
    "login-limit": {"text": "A limiter every three seconds with burst five allows about 20/minute; use separate limiters keyed by trusted client address for per-client limits.", "components": ["rate"], "sources": ["rate:s5c3fdae5a0af"], "status": "REASONED"},
    "tokens": {"text": "Load tokens from the environment and generate them per authentication.md; token generation and environment handling lack a listed source.", "components": ["oidc"], "sources": ["oidc:s60cc1d7a8fe6"], "status": "REASONED"},
    "oidc": {"text": "NewProvider discovers the issuer; Verifier with ClientID checks ID-token signature, issuer, audience and expiry; apply separate allowlists.", "components": ["oidc"], "sources": ["oidc:s60cc1d7a8fe6"], "status": "REASONED"},
    "mfa": {"text": "Use pquerna/otp or a fronting identity layer; TOTP and MFA lack a listed source.", "components": ["oidc"], "sources": ["oidc:s60cc1d7a8fe6"], "status": "REASONED"},
    "client-validation": {"text": "InsecureSkipVerify accepts any certificate and hostname unless custom VerifyConnection/VerifyPeerCertificate checks replace validation.", "components": ["tls"], "sources": ["tls:se2152a9c28fc"], "status": "REASONED"},
    "client-ca": {"text": "Use SystemCertPool plus a checked AppendCertsFromPEM result and RootCAs, or override CA locations with SSL_CERT_FILE/SSL_CERT_DIR.", "components": ["tls", "x509"], "sources": ["tls:se2152a9c28fc", "x509:se65b937f9e1e"], "status": "REASONED"},
    "platform-ca": {"text": "Go 1.27 certificate-file/directory overrides bypass macOS/Windows platform verification unless GODEBUG=x509sslcertoverrideplatform=0 is also set.", "components": ["x509"], "sources": ["x509:se65b937f9e1e"], "status": "REASONED"},
    "pprof": {"text": "Importing pprof registers /debug/pprof/ on DefaultServeMux; profiles, traces, cmdline and forced GC can disclose data or exhaust resources.", "components": ["pprof"], "sources": ["pprof:s0246034dddd1"], "status": "REASONED"},
    "expvar": {"text": "Importing expvar registers /debug/vars with cmdline and memstats on DefaultServeMux.", "components": ["expvar"], "sources": ["expvar:se49529035a0c"], "status": "REASONED"},
    "diag-bind": {"text": "Imports do not start listeners; nil handlers serve DefaultServeMux. Give the app its own mux and diagnostics a separate 127.0.0.1:6060 mux, never public proxy routing.", "components": ["http", "pprof", "expvar"], "sources": ["http:s75405f80decc", "pprof:s0246034dddd1", "expvar:se49529035a0c"], "status": "REASONED"},
    "body-limit": {"text": "Wrap the body with MaxBytesReader before decoding; the example 1 MiB policy requires explicit MaxBytesError handling to return 413.", "components": ["headers"], "sources": ["headers:sa4a9473fc6f8"], "status": "REASONED"},
    "header-size": {"text": "MaxHeaderBytes defaults to 1 MiB for request line and headers, independently of body limits.", "components": ["http"], "sources": ["http:s75405f80decc"], "status": "REASONED"},
    "header-count": {"text": "Go 1.27 adds MaxHeaderValueCount with default 500; this is separate from body limits.", "components": ["headers"], "sources": ["headers:sa4a9473fc6f8"], "status": "REASONED"},
    "read-timeout": {"text": "ReadTimeout bounds the whole request including body; example 30 seconds, zero or negative disables it.", "components": ["http"], "sources": ["http:s6ab9e32b7795"], "status": "REASONED"},
    "write-timeout": {"text": "WriteTimeout bounds writing; example 60 seconds, zero or negative disables it.", "components": ["http"], "sources": ["http:s6ab9e32b7795"], "status": "REASONED"},
    "header-timeout": {"text": "ReadHeaderTimeout bounds headers; example 10 seconds, zero falls back to ReadTimeout and negative disables it.", "components": ["http"], "sources": ["http:s6ab9e32b7795"], "status": "REASONED"},
    "idle-timeout": {"text": "IdleTimeout bounds keep-alive idle time; example 60 seconds, zero falls back to ReadTimeout and negative disables it.", "components": ["http"], "sources": ["http:s6ab9e32b7795"], "status": "REASONED"},
    "redirect-timeout": {"text": "Apply deadlines to the redirect server too; ListenAndServe sets none.", "components": ["http"], "sources": ["http:s75405f80decc", "http:s6ab9e32b7795"], "status": "REASONED"},
    "request-deadlines": {"text": "For long uploads/streaming, use generous server budgets and Go 1.20+ ResponseController read/write deadlines, handling unsupported operations.", "components": ["deadlines"], "sources": ["deadlines:s251e0db38b90"], "status": "REASONED"},
    "headers": {"text": "Install secure(mux) before response commit for nosniff and TLS-only HSTS max-age=63072000 with includeSubDomains.", "components": ["http"], "sources": ["http:s75405f80decc"], "status": "REASONED"},
    "http2": {"text": "HTTPS enables HTTP/2 automatically; Server.HTTP2 tunes it on current releases; retain maintained cipher/curve defaults.", "components": ["http", "tls"], "sources": ["http:s75405f80decc", "tls:se2152a9c28fc"], "status": "REASONED"},
    "verify-redirect": {"text": "HTTP should return 301 with an HTTPS Location.", "components": ["http"], "sources": ["http:s75405f80decc"], "status": "REASONED", "verify": [1]},
    "verify-tls": {"text": "HTTPS must succeed without -k.", "components": ["http", "tls"], "sources": ["http:s75405f80decc", "tls:se2152a9c28fc"], "status": "REASONED", "verify": [1]},
    "verify-auth": {"text": "The guide expects /api to return 401/403 without credentials; it records no valid-credential positive control.", "components": ["http"], "sources": ["http:s75405f80decc"], "status": "REASONED", "verify": [1]},
    "verify-bind": {"text": "Inspect every listener for loopback-only application binding behind the proxy.", "components": ["http"], "sources": ["http:s75405f80decc"], "status": "REASONED", "verify": [1]},
    "verify-diag-local": {"text": "A local 6060/debug/pprof/ response of 200 establishes local availability only.", "components": ["pprof"], "sources": ["pprof:s0246034dddd1"], "status": "REASONED", "verify": [1]},
    "verify-diag-route": {"text": "The public application /debug/pprof/ route should return 404, never 200.", "components": ["http", "pprof"], "sources": ["http:s75405f80decc", "pprof:s0246034dddd1"], "status": "REASONED", "verify": [1]},
    "verify-diag-external": {"text": "From outside the server network, the actual public IP on 6060 must be unreachable; the guide expects refusal or timeout, never 200.", "components": ["http", "pprof"], "sources": ["http:s75405f80decc", "pprof:s0246034dddd1"], "status": "REASONED", "verify": [2]},
    "request-host": {"text": "Go 1.27.0 Request.Host is supplied by the client; a fixed canonical hostname plus an origin-form path prevents forged Host or crafted request targets from selecting the redirect destination.", "components": ["request"], "sources": ["request:sfdeabbeca746"], "status": "REASONED"}
  }
}
---
# Go: TLS and authentication with net/http

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-27; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| tls: Direct TLS listens on :443 using the leaf-plus-intermediates certificate and private key; ReadHeaderTimeout is 10 seconds. | Go net/http documentation unknown; Go crypto/tls documentation unknown | REASONED |
| redirect: Port :80 sends a 301 to https:// plus the fixed canonicalHost and an origin-form request path; empty or non-path RequestURI values fall back to /. Never build the destination from r.Host. | Go net/http documentation unknown; Go Request.Host source 1.27.0 | REASONED |
| tls-min: crypto/tls defaults to TLS 1.2 minimum as of September 2026; explicitly set MinVersion=VersionTLS12. | Go crypto/tls documentation unknown | REASONED |
| privilege: Linux privileged-port threshold defaults to 1024 but is configurable per namespace; root or CAP_NET_BIND_SERVICE is needed below it in the usual configuration. | Linux port-threshold documentation unknown | REASONED |
| proxy: Bind 127.0.0.1:8080 behind a TLS proxy; net/http has no proxy trust setting, so accept forwarded headers only from the isolated, overwriting proxy. | Go net/http documentation unknown | REASONED |
| proxy-headers: Set HSTS and other security headers at the proxy per the linked headers guide. | Go net/http documentation unknown | REASONED |
| bcrypt: Use bcrypt cost 12; DefaultCost is 10, inputs over 72 bytes are rejected and CompareHashAndPassword returns nil on match. | Go bcrypt documentation unknown | REASONED |
| argon: IDKey returns raw bytes; retain random salt and parameters. RFC 9106 choices are time=1/memory=2 GiB/threads=4 or time=3/memory=64 MiB/threads=4. | Go Argon2 documentation unknown | REASONED |
| cookies: Set session cookie Path=/, Secure, HttpOnly and SameSite=Lax. | Go net/http documentation unknown | REASONED |
| login-limit: A limiter every three seconds with burst five allows about 20/minute; use separate limiters keyed by trusted client address for per-client limits. | Go rate documentation unknown | REASONED |
| tokens: Load tokens from the environment and generate them per authentication.md; token generation and environment handling lack a listed source. | go-oidc documentation v3 | REASONED |
| oidc: NewProvider discovers the issuer; Verifier with ClientID checks ID-token signature, issuer, audience and expiry; apply separate allowlists. | go-oidc documentation v3 | REASONED |
| mfa: Use pquerna/otp or a fronting identity layer; TOTP and MFA lack a listed source. | go-oidc documentation v3 | REASONED |
| client-validation: InsecureSkipVerify accepts any certificate and hostname unless custom VerifyConnection/VerifyPeerCertificate checks replace validation. | Go crypto/tls documentation unknown | REASONED |
| client-ca: Use SystemCertPool plus a checked AppendCertsFromPEM result and RootCAs, or override CA locations with SSL_CERT_FILE/SSL_CERT_DIR. | Go crypto/tls documentation unknown; Go certificate-store qualification 1.27 | REASONED |
| platform-ca: Go 1.27 certificate-file/directory overrides bypass macOS/Windows platform verification unless GODEBUG=x509sslcertoverrideplatform=0 is also set. | Go certificate-store qualification 1.27 | REASONED |
| pprof: Importing pprof registers /debug/pprof/ on DefaultServeMux; profiles, traces, cmdline and forced GC can disclose data or exhaust resources. | Go pprof documentation unknown | REASONED |
| expvar: Importing expvar registers /debug/vars with cmdline and memstats on DefaultServeMux. | Go expvar documentation unknown | REASONED |
| diag-bind: Imports do not start listeners; nil handlers serve DefaultServeMux. Give the app its own mux and diagnostics a separate 127.0.0.1:6060 mux, never public proxy routing. | Go net/http documentation unknown; Go pprof documentation unknown; Go expvar documentation unknown | REASONED |
| body-limit: Wrap the body with MaxBytesReader before decoding; the example 1 MiB policy requires explicit MaxBytesError handling to return 413. | Go header-count qualification 1.27 | REASONED |
| header-size: MaxHeaderBytes defaults to 1 MiB for request line and headers, independently of body limits. | Go net/http documentation unknown | REASONED |
| header-count: Go 1.27 adds MaxHeaderValueCount with default 500; this is separate from body limits. | Go header-count qualification 1.27 | REASONED |
| read-timeout: ReadTimeout bounds the whole request including body; example 30 seconds, zero or negative disables it. | Go net/http documentation unknown | REASONED |
| write-timeout: WriteTimeout bounds writing; example 60 seconds, zero or negative disables it. | Go net/http documentation unknown | REASONED |
| header-timeout: ReadHeaderTimeout bounds headers; example 10 seconds, zero falls back to ReadTimeout and negative disables it. | Go net/http documentation unknown | REASONED |
| idle-timeout: IdleTimeout bounds keep-alive idle time; example 60 seconds, zero falls back to ReadTimeout and negative disables it. | Go net/http documentation unknown | REASONED |
| redirect-timeout: Apply deadlines to the redirect server too; ListenAndServe sets none. | Go net/http documentation unknown | REASONED |
| request-deadlines: For long uploads/streaming, use generous server budgets and Go 1.20+ ResponseController read/write deadlines, handling unsupported operations. | Go per-request deadline minimum 1.20+ | REASONED |
| headers: Install secure(mux) before response commit for nosniff and TLS-only HSTS max-age=63072000 with includeSubDomains. | Go net/http documentation unknown | REASONED |
| http2: HTTPS enables HTTP/2 automatically; Server.HTTP2 tunes it on current releases; retain maintained cipher/curve defaults. | Go net/http documentation unknown; Go crypto/tls documentation unknown | REASONED |
| verify-redirect: HTTP should return 301 with an HTTPS Location. | Go net/http documentation unknown | REASONED |
| verify-tls: HTTPS must succeed without -k. | Go net/http documentation unknown; Go crypto/tls documentation unknown | REASONED |
| verify-auth: The guide expects /api to return 401/403 without credentials; it records no valid-credential positive control. | Go net/http documentation unknown | REASONED |
| verify-bind: Inspect every listener for loopback-only application binding behind the proxy. | Go net/http documentation unknown | REASONED |
| verify-diag-local: A local 6060/debug/pprof/ response of 200 establishes local availability only. | Go pprof documentation unknown | REASONED |
| verify-diag-route: The public application /debug/pprof/ route should return 404, never 200. | Go net/http documentation unknown; Go pprof documentation unknown | REASONED |
| verify-diag-external: From outside the server network, the actual public IP on 6060 must be unreachable; the guide expects refusal or timeout, never 200. | Go net/http documentation unknown; Go pprof documentation unknown | REASONED |
| request-host: Go 1.27.0 Request.Host is supplied by the client; a fixed canonical hostname plus an origin-form path prevents forged Host or crafted request targets from selecting the redirect destination. | Go Request.Host source 1.27.0 | REASONED |
<!-- version-basis:end -->

Preferred production layout: bind the Go server to `127.0.0.1` and terminate TLS in a reverse proxy ([caddy.md](caddy.md), [nginx.md](nginx.md)) or behind [cloudflare.md](cloudflare.md). `net/http` can also terminate TLS itself, shown below. Certificates: [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md).

## 1. HTTPS directly in Go

```go
const canonicalHost = "app.example.com"   // r.Host comes from the client; never reflect it in the redirect.
go http.ListenAndServe(":80", http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {   // port 80 only redirects
    target := r.URL.RequestURI()
    // Opaque or absolute-form targets can yield non-path values; only append an origin-form path.
    if len(target) == 0 || target[0] != '/' {
        target = "/"
    }
    http.Redirect(w, r, "https://"+canonicalHost+target, http.StatusMovedPermanently)
}))
srv := &http.Server{
    Addr:              ":443",
    Handler:           mux,
    ReadHeaderTimeout: 10 * time.Second,
    TLSConfig:         &tls.Config{MinVersion: tls.VersionTLS12},
}
log.Fatal(srv.ListenAndServeTLS("/etc/ssl/certs/server.crt", "/etc/ssl/private/server.key"))   // cert file: leaf, then intermediates
```

Set `canonicalHost` to your canonical hostname (no scheme or path) and append only an origin-form path (falling back to `/` for non-path values from opaque or absolute-form targets), so neither a forged Host nor a crafted request target can turn this into an open redirect.

crypto/tls already defaults to a TLS 1.2 minimum (as of September 2026); setting `MinVersion` keeps that true when a config is copied or a default shifts. Binding ports below 1024 needs root or `CAP_NET_BIND_SERVICE` on Linux's usual configuration (the per-namespace `net.ipv4.ip_unprivileged_port_start` defaults to 1024 but is configurable), one more reason to prefer the proxy layout.

## 2. Behind a proxy

```go
srv := &http.Server{Addr: "127.0.0.1:8080", Handler: mux, ReadHeaderTimeout: 10 * time.Second}
log.Fatal(srv.ListenAndServe())
```

`http.Server` has no trusted-proxy setting: `r.RemoteAddr` is the proxy, and `X-Forwarded-For` and `X-Forwarded-Proto` are ordinary request headers that anyone who can reach the port could set. Read them only when the listener is loopback-only and the proxy overwrites them, and set `Strict-Transport-Security` and the other headers at the proxy per [headers.md](headers.md).

## 3. Authentication

Follow [authentication.md](authentication.md). Password hashing with `golang.org/x/crypto/bcrypt`:

```go
hash, err := bcrypt.GenerateFromPassword([]byte(password), 12)   // DefaultCost is 10; input above 72 bytes is rejected
err = bcrypt.CompareHashAndPassword(hash, []byte(password))     // nil on match
```

`golang.org/x/crypto/argon2` is the alternative: `argon2.IDKey(password, salt, time, memory, threads, keyLen)` returns raw bytes, so you store the random salt and the parameters next to the result. Its documentation carries the RFC 9106 parameter sets (`time=1, memory=2 GiB, threads=4`, or `time=3, memory=64 MiB, threads=4` where memory is short).

Session cookie with the flags set:

```go
http.SetCookie(w, &http.Cookie{
    Name: "session", Value: token, Path: "/",
    Secure: true, HttpOnly: true, SameSite: http.SameSiteLaxMode,
})
```

Rate-limit the login handler with `golang.org/x/time/rate` (one limiter here; key a map of limiters by the proxy-supplied client address for per-client limits):

```go
var loginLimiter = rate.NewLimiter(rate.Every(3*time.Second), 5)   // about 20 per minute, burst 5
if !loginLimiter.Allow() { http.Error(w, "too many requests", http.StatusTooManyRequests); return }
```

API keys and tokens come from the environment, never from literals in the source; generate them per [authentication.md](authentication.md). SSO: `github.com/coreos/go-oidc/v3/oidc` pairs with `golang.org/x/oauth2`; `oidc.NewProvider(ctx, issuer)` discovers the provider and `provider.Verifier(&oidc.Config{ClientID: clientID})` checks ID token signature, issuer, audience, and expiry. The allowlist checks that follow are in [oidc-integration.md](oidc-integration.md). MFA: app-level TOTP with [pquerna/otp](https://github.com/pquerna/otp), or a fronting identity layer; requirements in [mfa.md](mfa.md).

## 4. Client-side TLS discipline

Never set `InsecureSkipVerify: true`; the crypto/tls docs state it accepts any certificate and any host name, a machine-in-the-middle position unless you supply your own checks through `VerifyConnection` or `VerifyPeerCertificate` (which is not a deployment pattern to reach for casually). For an internal CA, trust the CA instead (see [self-signed.md](self-signed.md) for producing the file): `SSL_CERT_FILE=/path/ca.crt` (or `SSL_CERT_DIR`) overrides the system locations that `x509.SystemCertPool` reads, or add it in code:

```go
pool, err := x509.SystemCertPool()
if err != nil { log.Fatal(err) }
pem, err := os.ReadFile("/path/ca.crt")
if err != nil { log.Fatal(err) }
if !pool.AppendCertsFromPEM(pem) { log.Fatal("no certificate parsed from /path/ca.crt") }
client := &http.Client{Transport: &http.Transport{TLSClientConfig: &tls.Config{RootCAs: pool}}}
```

On Go 1.27, setting `SSL_CERT_FILE` or `SSL_CERT_DIR` bypasses the platform certificate-verification APIs on macOS and Windows unless you also set `GODEBUG=x509sslcertoverrideplatform=0`.

## 5. Keep diagnostic endpoints private

Importing `net/http/pprof` for its side effect registers `/debug/pprof/` (profiles, traces, `cmdline`, and requests that force a GC) on `http.DefaultServeMux`, and `expvar` registers `/debug/vars` (exposing `cmdline` and `memstats`) the same way; neither starts a listener by itself, but `http.ListenAndServe(addr, nil)`, or any server with a nil handler, serves the default mux, so a single stray import turns a public port into an information-disclosure and resource-exhaustion surface. Give the application its own mux and never mount diagnostics on it:

```go
mux := http.NewServeMux()          // the app mux; assign it to Server.Handler, not the default mux
// ... register application routes on mux ...
```

If you need pprof or expvar, register them on a separate mux and serve it on loopback only, never through the public proxy:

```go
diag := http.NewServeMux()
diag.HandleFunc("/debug/pprof/", pprof.Index)              // import "net/http/pprof"; Index serves the named runtime profiles but not profile/trace/cmdline/symbol
diag.HandleFunc("/debug/pprof/profile", pprof.Profile)
diag.HandleFunc("/debug/pprof/trace", pprof.Trace)
diag.HandleFunc("/debug/pprof/cmdline", pprof.Cmdline)
diag.HandleFunc("/debug/pprof/symbol", pprof.Symbol)
diag.Handle("/debug/vars", expvar.Handler())
go func() { log.Fatal((&http.Server{Addr: "127.0.0.1:6060", Handler: diag, ReadHeaderTimeout: 10 * time.Second}).ListenAndServe()) }()
```

## 6. Bound request resources

Cap request bodies per endpoint so a large or slow upload cannot exhaust memory. `http.MaxBytesReader` wraps the body and makes reads past the limit fail; it does not send the 413 for you, so handle the error:

```go
r.Body = http.MaxBytesReader(w, r.Body, 1<<20)   // 1 MiB example policy, choose per endpoint
dec := json.NewDecoder(r.Body)                   // build the decoder AFTER wrapping, or the cap is not applied
if err := dec.Decode(&v); err != nil {           // v is the endpoint's destination value
    var mbe *http.MaxBytesError
    if errors.As(err, &mbe) { http.Error(w, "request body too large", http.StatusRequestEntityTooLarge); return }
    http.Error(w, "bad request", http.StatusBadRequest); return
}
```

Header size is a separate control: `Server.MaxHeaderBytes` defaults to `1 << 20` (1 MiB, covering the request line and headers, not the body), and Go 1.27 adds `Server.MaxHeaderValueCount` (default 500) to bound the number of header values. Neither substitutes for the body limit above; set the body limit where you read untrusted input.

## 7. Set server deadlines

The `ReadHeaderTimeout` in the examples above bounds only header reading; add the rest of the `http.Server` deadlines so a slow body, a slow reader, or an idle keep-alive connection cannot hold a goroutine open:

```go
srv := &http.Server{
    Addr:              "127.0.0.1:8080",
    Handler:           mux,
    ReadHeaderTimeout: 10 * time.Second,   // slow-header / Slowloris
    ReadTimeout:       30 * time.Second,   // whole request incl. body
    WriteTimeout:      60 * time.Second,   // slow readers
    IdleTimeout:       60 * time.Second,   // keep-alive between requests
}
```

These are a starting policy for short, bounded requests, not Go defaults. For `ReadTimeout` and `WriteTimeout`, a zero or negative value disables that timeout; for `ReadHeaderTimeout` and `IdleTimeout`, zero instead falls back to `ReadTimeout`, so a negative value disables them, as does zero when `ReadTimeout` is itself zero or negative. Give the port-80 redirect server the same deadlines (the `http.ListenAndServe` helper sets none). For genuinely long uploads or streaming, keep the server defaults generous and set a per-request budget with `http.NewResponseController(w)` (`SetReadDeadline`/`SetWriteDeadline`, Go 1.20+), handling the unsupported-operation error.

## 8. Security headers when Go terminates TLS

Section 2 sets `Strict-Transport-Security` and the rest at the proxy. When Go terminates its own TLS instead, set them in a middleware wrapper that runs before the handler commits the response, and send HSTS only over TLS:

```go
func secure(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("X-Content-Type-Options", "nosniff")
        if r.TLS != nil { w.Header().Set("Strict-Transport-Security", "max-age=63072000; includeSubDomains") }
        next.ServeHTTP(w, r)
    })
}
```

Defer the full header catalogue and values to [headers.md](headers.md); do not send HSTS over plain HTTP. Install it with `srv.Handler = secure(mux)` (or wrap your router); defining the wrapper alone adds no headers. (Go enables HTTP/2 automatically for HTTPS servers, and a `Server.HTTP2` field (`HTTP2Config`) tunes it on current releases, but leave the maintained cipher and curve defaults and the TLS 1.2 minimum from section 1 alone unless you have a specific requirement.)

## 9. Verify (REASONED: TLS, authentication, listener and diagnostic expectations follow the Go Sources below; no deployment run or outcome is recorded in this guide. This metadata-only review has no deployed Go service, proxy or outside-network probe host.)

```bash
curl -q -sI http://example.com/         # expect 301 with a https:// Location
curl -q -sI https://example.com/        # succeeds without -k
curl -q -sS -o /dev/null -w '%{http_code}\n' https://example.com/api   # 401 or 403 without credentials
ss -tlnp   # read every listener; REPLACE_WITH_BINARY_NAME: behind a proxy: 127.0.0.1 only
curl -q -g -sS --noproxy '*' -o /dev/null -w '%{http_code}\n' http://127.0.0.1:6060/debug/pprof/   # local availability only: 200 here just means you enabled a diagnostic listener (section 5). What matters is off-host reachability, checked next.
curl -q -sS -o /dev/null -w '%{http_code}\n' https://example.com/debug/pprof/   # diagnostics must never be routed on your PUBLIC app: substitute your hostname, expect 404, never 200
```

```bash
(                                       # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_THE_SERVER_PUBLIC_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the server's public address on the set -- line above; not probing" ;;
    *) curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 \
         -w 'diag_6060 http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:6060/debug/pprof/" || true ;;   # run from a machine OUTSIDE the server's network: the diagnostic listener (section 5) must be UNREACHABLE (a refusal or timeout, never a 200)
  esac
)
```

## Sources (checked September 2026)

- net/http (Server, ListenAndServeTLS, Cookie, SameSite, Redirect, Transport.TLSClientConfig): https://pkg.go.dev/net/http
- net/http Request.Host (Go 1.27.0, supplied by the client): https://pkg.go.dev/net/http@go1.27.0#Request
- crypto/tls (Config.MinVersion, InsecureSkipVerify, RootCAs): https://pkg.go.dev/crypto/tls
- crypto/x509 (SystemCertPool, SSL_CERT_FILE, AppendCertsFromPEM) (Go 1.27): https://pkg.go.dev/crypto/x509@go1.27.0
- golang.org/x/crypto/bcrypt: https://pkg.go.dev/golang.org/x/crypto/bcrypt
- golang.org/x/crypto/argon2: https://pkg.go.dev/golang.org/x/crypto/argon2
- golang.org/x/time/rate: https://pkg.go.dev/golang.org/x/time/rate
- go-oidc: https://pkg.go.dev/github.com/coreos/go-oidc/v3/oidc
- net/http/pprof and expvar register on DefaultServeMux: https://pkg.go.dev/net/http/pprof
- net/http MaxBytesReader, MaxBytesError, Server.MaxHeaderBytes / MaxHeaderValueCount (Go 1.27): https://pkg.go.dev/net/http@go1.27.0#MaxBytesReader
- net/http Server timeouts (ReadTimeout, WriteTimeout, IdleTimeout, ReadHeaderTimeout): https://pkg.go.dev/net/http#Server
- net/http ResponseController (per-request deadlines) (Go 1.20+): https://pkg.go.dev/net/http#ResponseController
- expvar (registers /debug/vars on the default mux): https://pkg.go.dev/expvar
- Linux ip-sysctl, ip_unprivileged_port_start (the privileged-port threshold is configurable): https://docs.kernel.org/networking/ip-sysctl.html#ip-unprivileged-port-start
