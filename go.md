# Go: TLS and authentication with net/http

Preferred production layout: bind the Go server to `127.0.0.1` and terminate TLS in a reverse proxy ([caddy.md](caddy.md), [nginx.md](nginx.md)) or behind [cloudflare.md](cloudflare.md). `net/http` can also terminate TLS itself, shown below. Certificates: [free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md).

## 1. HTTPS directly in Go

```go
go http.ListenAndServe(":80", http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {   // port 80 only redirects
    http.Redirect(w, r, "https://"+r.Host+r.URL.RequestURI(), http.StatusMovedPermanently)
}))
srv := &http.Server{
    Addr:              ":443",
    Handler:           mux,
    ReadHeaderTimeout: 10 * time.Second,
    TLSConfig:         &tls.Config{MinVersion: tls.VersionTLS12},
}
log.Fatal(srv.ListenAndServeTLS("/etc/ssl/certs/server.crt", "/etc/ssl/private/server.key"))   // cert file: leaf, then intermediates
```

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

## 9. Verify

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
- crypto/tls (Config.MinVersion, InsecureSkipVerify, RootCAs): https://pkg.go.dev/crypto/tls
- crypto/x509 (SystemCertPool, SSL_CERT_FILE, AppendCertsFromPEM): https://pkg.go.dev/crypto/x509
- golang.org/x/crypto/bcrypt: https://pkg.go.dev/golang.org/x/crypto/bcrypt
- golang.org/x/crypto/argon2: https://pkg.go.dev/golang.org/x/crypto/argon2
- golang.org/x/time/rate: https://pkg.go.dev/golang.org/x/time/rate
- go-oidc: https://pkg.go.dev/github.com/coreos/go-oidc/v3/oidc
- net/http/pprof and expvar register on DefaultServeMux: https://pkg.go.dev/net/http/pprof
- net/http MaxBytesReader, MaxBytesError, Server.MaxHeaderBytes / MaxHeaderValueCount: https://pkg.go.dev/net/http#MaxBytesReader
- net/http Server timeouts (ReadTimeout, WriteTimeout, IdleTimeout, ReadHeaderTimeout): https://pkg.go.dev/net/http#Server
- net/http ResponseController (per-request deadlines): https://pkg.go.dev/net/http#ResponseController
- expvar (registers /debug/vars on the default mux): https://pkg.go.dev/expvar
- Linux ip-sysctl, ip_unprivileged_port_start (the privileged-port threshold is configurable): https://docs.kernel.org/networking/ip-sysctl.html#ip-unprivileged-port-start
