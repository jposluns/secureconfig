# Cloudflare Tunnel and Zero Trust Access

Cloudflare Tunnel publishes a self-hosted app through Cloudflare, and Cloudflare Access decides who may sign in. This guide helps your AI assistant set both up securely, including Access policies, MFA for sensitive apps, and the app bound to loopback on the `cloudflared` host.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/cloudflare.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against cloudflared token-file minimum 2025.4.0, cloudflared service installer 2026.9.3, cloudflared README 2026.9.3, and curl command-line options curl-8_23_0; 1 further source is pinned to a commit and 2 carry no recorded version. Metadata reviewed 2026-10-18; documentation checked September 2026. The guide records 30 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

This is the recommended path when the host cannot or should not accept inbound connections: home labs, NATed machines, cloud VMs you want to keep closed, and any project without its own TLS setup. `cloudflared` opens an outbound-only tunnel to Cloudflare's edge, the edge serves your hostname over HTTPS with a Cloudflare-managed certificate, and Cloudflare Access places authentication (SSO or emailed one-time PIN) in front of the app without any application changes. No inbound firewall ports are opened at all.

## 1. Prerequisites

- A domain added to Cloudflare (the free plan is sufficient), with Cloudflare as its DNS.
- A Zero Trust organization on the account. Check current plan limits, including the free plan's, with Cloudflare; the fetched [plans page](https://www.cloudflare.com/plans/zero-trust-services/) did not state a user limit, and this guide does not establish one.
- `cloudflared` installed on the host that can reach the service (packages for Linux, macOS, and Windows: https://github.com/cloudflare/cloudflared).

## 2. Create the tunnel (dashboard-managed, recommended)

Per the Cloudflare docs as of June 2026 (menu locations change; the sources below are authoritative):

1. In the Cloudflare dashboard go to **Networking > Tunnels** and create a tunnel (connector type `cloudflared`).
2. Copy only the tunnel token from the dashboard into a file readable only by the account running `cloudflared` (mode `0600` on Linux/macOS; a restricted ACL on Windows). With `cloudflared` **2025.4.0 or later**, configure your OS service to run `cloudflared tunnel run --token-file /absolute/path/to/token`, substituting your token-file path ([run parameters](https://developers.cloudflare.com/tunnel/reference/run-parameters/#token-file)). Do not run the dashboard's `cloudflared service install <TOKEN>` command: it exposes the token in the installer's command line.
3. Last, and only after step 4 below: add a route: **Routes > Add route > Published application**, choose the subdomain (for example `app.example.com`), and set the service URL to the local service, for example `http://localhost:3000`.

The moment that route exists the app is reachable at `https://app.example.com`, by anyone, with no login in front of it. Access is what adds the login and it is step 4, so doing these steps in the order they are numbered leaves a window in which the application is published and unauthenticated, however short you make it. Close it rather than racing it. Either complete step 4 first and add the route afterwards, which works if Cloudflare accepts an Access application for a hostname you have not routed yet; or leave the local service stopped until Access is in place, which always works. With the route created and the service stopped the hostname still resolves, because the route is a proxied DNS record, and a visitor gets an error page from Cloudflare's edge rather than your application: the point is that nothing of yours is being served, not that the name is invisible. [deployment-lifecycle.md](deployment-lifecycle.md) makes the same point about previews and first deployments.

Once routed, the app is served over TLS terminated at Cloudflare's edge. Traffic between `cloudflared` and Cloudflare travels inside the encrypted tunnel; the `http://localhost:3000` hop stays on the host itself.

## 3. CLI alternative (locally-managed tunnel)

```bash
cloudflared tunnel login
cloudflared tunnel create myapp
# `route dns` is what publishes the hostname, so it has the same problem as the dashboard's
# routing step: run it after the Access application and policy of step 4 exist, not before.
cloudflared tunnel route dns myapp app.example.com
```

`~/.cloudflared/config.yml`:

```yaml
tunnel: <TUNNEL-UUID>
credentials-file: /home/user/.cloudflared/<TUNNEL-UUID>.json
ingress:
  - hostname: app.example.com
    service: http://localhost:3000
  - service: http_status:404
```

Run with `cloudflared tunnel run myapp`, or install it as a service with `sudo cloudflared --config /home/user/.cloudflared/config.yml service install` (substitute your own home path) (pass `--config` explicitly: under `sudo`, `$HOME` is `/root`, so a bare `cloudflared service install` misses the config you wrote under your own home). The credentials JSON and the tunnel token are secrets: they let anyone publish services on your hostname, so keep them out of repositories.

## 4. Add authentication with Access

A tunnel publishes the app; Access is what makes it authenticated. In the Zero Trust dashboard:

1. Go to the **Access > Applications** section and add a **self-hosted** application for `app.example.com`.
2. Create an **Allow** policy. Sensible starting rules: `Emails` listing specific addresses, or `Emails ending in` your domain.
3. Choose login methods. The built-in **One-time PIN** (a code emailed to the allowed address) works with zero identity-provider setup; connect Google, GitHub, Microsoft Entra ID, or another IdP for SSO and MFA.

Every request to the hostname now hits a Cloudflare login page first; only identities matching the policy reach the app.

MFA: the emailed one-time PIN proves control of a mailbox only. For anything sensitive, connect an identity provider and enforce MFA there; Access then inherits it. If both One-time PIN and the IdP are enabled on the same application a user may pick either, so OTP becomes a bypass of the IdP's MFA: remove One-time PIN from a sensitive application's login methods, leaving only the MFA-enforcing IdP, or enforce Access's own MFA requirement across the allowed methods. Broader options: [mfa.md](mfa.md).

For APIs and machine clients, create a **service token** in the Zero Trust dashboard (Access service authentication section), add a **Service Auth** policy to the application, and send the token with each request. Paste the client secret alone at the hidden prompt: a multi-line paste leaves every line after the first for your shell to run.

```bash
(
  # Use Bash in a fresh, trusted shell. Replace the URL and client ID inside
  # the quotes; paste only the secret at the hidden prompt, never into the command.
  # The prompted secret reaches curl on stdin, outside argv and shell history;
  # stdin does not hide it from set -x tracing (the block turns tracing off),
  # and it remains accessible to the account owner or root.
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  { unset -n HDR && unset -v HDR; } 2>/dev/null ||
    { echo 'cannot clear HDR in this shell; not probing'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not probing'; exit 2; }
  set -- PASTE_WHOLE_BLOCK 'https://app.example.com/api' 'REPLACE_WITH_CLIENT_ID'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not probing'; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo 'the set -- line needs a URL and client ID; not probing'; exit 2; }
  case "$1" in
    ''|*REPLACE_WITH_*|*example.com*|*example.net*|*example.org*|*[[:cntrl:]]*)
      echo 'substitute your own application URL inside the quotes; not probing'; exit 2 ;;
    https://*) ;;
    *) echo 'use an https:// URL; not probing'; exit 2 ;;
  esac
  case "$2" in
    ''|*REPLACE_WITH_*|*[[:cntrl:]]*) echo 'supply the client ID without control characters; not probing'; exit 2 ;;
  esac
  IFS= read -r -s -p 'Client secret (input hidden): ' HDR ||
    { echo 'secret input failed; not probing'; exit 2; }
  printf '\n'
  case "$HDR" in
    ''|*REPLACE_WITH_*|*[[:cntrl:]]*) echo 'supply the secret without control characters; not probing'; exit 2 ;;
  esac
  HDR="CF-Access-Client-Secret: $HDR"
  printf '%s\n' "CF-Access-Client-Id: $2" "$HDR" |
    curl -q -g -sS --connect-timeout 5 --max-time 20 --header @- "$1" || exit 2
  unset -v HDR
)
```

## 5. Close the side doors

- Bind the application to `127.0.0.1` so the tunnel is the only path to it. If the app also listens publicly, Access is decorative.
- Defense in depth: where the app can read a header, validate the `Cf-Access-Jwt-Assertion` that Access sends against your team's certificates (checking the `aud` tag and the issuer), per [cloud-identity-proxies.md](cloud-identity-proxies.md) section 5. It is the control that still holds when an origin is left reachable, an SSRF reaches `localhost`, or a second route is added to the same tunnel, which is unprotected unless an Access application and policy already cover its hostname and path (a per-hostname application, or a wildcard one).
- Do not use quick tunnels (`cloudflared tunnel --url http://localhost:3000`, the random `trycloudflare.com` URLs) for anything real: without `--allowed-mail`, anyone with the URL can access the service. Cloudflare describes these URLs as temporary and for testing and development, not production; the URL stops working when `cloudflared` stops.
- If the origin must sit on a different machine from `cloudflared`, TLS on that hop (`service: https://...`; see [self-signed.md](self-signed.md)) only encrypts it, it does not restrict who may connect, so the origin machine must also accept connections *only* from the `cloudflared` host (a host or cloud firewall source-restriction), or the app is reachable directly with no Access, just as in the next bullet. Better, run `cloudflared` on the origin machine itself and bind the app to loopback there. For a self-signed origin certificate, configure its issuing CA with `originRequest.caPool`, keeping certificate and hostname verification, rather than `originRequest.noTLSVerify: true`, which discards the server authentication the TLS hop was meant to add.
- Related but distinct: for a directly-exposed origin behind Cloudflare's proxy (no tunnel), Full (strict) with a Cloudflare **origin certificate** encrypts and authenticates the origin *to* Cloudflare. Full (strict) with that origin certificate still does not stop a client that discovers the IP of that directly-exposed origin (through DNS history, certificate-transparency scans, or a grey-clouded or MX record on the same host) from connecting straight to the origin and bypassing Access. Lock the origin down with **Authenticated Origin Pulls** and a firewall: enabling AOP in the dashboard alone enforces nothing at the origin, so the origin must require the client certificate (for nginx, `ssl_verify_client on` with `ssl_client_certificate` set to the CA the presented client certificate chains to). With **global** AOP that CA is Cloudflare's shared origin-pull CA, which only proves the request came from Cloudflare's network (any account); prefer a **zone-level** certificate you upload, trust that certificate's issuing CA at the origin and remove the shared-CA trust, so only your zone is accepted. Because AOP is mutual TLS it cannot authenticate plaintext HTTP, so close origin port 80 (or make it redirect only to the canonical HTTPS host, never serve the app) and restrict inbound 443 to Cloudflare's published IP ranges (https://www.cloudflare.com/ips/), per [cloud-firewalls.md](cloud-firewalls.md). Origin certificates are trusted only by Cloudflare's edge, never by browsers directly.

## 6. Verify

- REASONED: private-browsing Access check; local marking review (October 2026, Bash 5.3.9) did not run a browser comparison. A live Cloudflare origin stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; a Cloudflare account and Access application on a proxied hostname were not available to this marking review. For the visit to https://app.example.com, an exposed route is expected to serve app content anonymously; a fixed route is expected to show Access login, then serve the app after an allowed sign-in, per the guide's cited Cloudflare Zero Trust documentation and Cloudflare Access One-time PIN (login methods coexist with an IdP). A private-browsing visit to `https://app.example.com` shows the Access login page, not the app.
- REASONED: anonymous HEAD check; local marking review (October 2026, Bash 5.3.9) ran the stated curl command against a curl stub, which printed 'stub curl args=-q -sI https://app.example.com/' (exit 0), not an HTTP response. A live Cloudflare origin stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; a Cloudflare account and Access application on a proxied hostname were not available to this marking review. An exposed route is expected to return the application's own status and headers, potentially HTTP 200; a fixed anonymous route is expected to return 302 with a team cloudflareaccess.com login location, while an allowed session reaches the app, per the guide's cited Cloudflare Zero Trust documentation and Cloudflare Access One-time PIN (login methods coexist with an IdP). HEAD prints status and headers, not content. `curl -q -sI https://app.example.com/` returns a 302 whose `location` is your team's `*.cloudflareaccess.com` login, never a 200 or your application's own content.
- REASONED: service-token GET and anonymous comparison; local marking review (October 2026, Bash 5.3.9) passed the following block through bash -n and ShellCheck 0.11.0 with no output. Five of the fourteen Bash fixtures with a curl stub printed: placeholder and empty URL, 'substitute your own application URL inside the quotes; not probing' (each exit 2); wrong sentinel, 'paste the whole block, including its set -- line; not probing' (exit 2); and one and three values, 'the set -- line needs a URL and client ID; not probing' (each exit 2). Five more of the fourteen fixtures printed: HTTP URL, 'use an https:// URL; not probing' (exit 2); placeholder ID, 'supply the client ID without control characters; not probing' (exit 2); EOF secret input, 'secret input failed; not probing' (exit 2); and empty and placeholder secrets, 'supply the secret without control characters; not probing' (each exit 2). The remaining four fixtures printed: readonly HDR, 'cannot clear HDR in this shell; not probing' (exit 2); readonly IFS, 'a readonly IFS is set in this shell; not probing' (exit 2); valid input, 'stub curl' (exit 0); and curl stub exit 7, 'stub curl' (block exit 2). No HTTP status was observed. A live Cloudflare origin stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; a provisioned Cloudflare account, Access application and service token were not available to this marking review. On a route known to return application HTTP 200, exposed anonymous and token requests are expected to reach the app, per the guide's cited Cloudflare Access service tokens (request headers and Service Auth policy) and curl manual (stdin headers, output, redirect reporting and write-out variables). Fixed anonymous requests on that route are expected to show Access login or denial, while the valid token is expected to yield http=200 location= on that route, per the guide's cited Cloudflare Access service tokens (request headers and Service Auth policy) and curl manual (stdin headers, output, redirect reporting and write-out variables). The block discards the body, so the printed status cannot identify content. With a service token, a GET returns your application content, not the Access login. Use a route known to serve your application's content with HTTP 200. Expect `http=200 location=`; an Access login redirect, denial or transport error is not a pass. Compare with the anonymous check above: an exposed app serves the route anonymously too, so token success alone does not prove Access is enforced.

REASONED: the usage and secret-handling notes for the service-token block below, per the guide's cited Cloudflare Access service tokens and curl manual entries and the block's own text, with the paste-alone warning per CONTRIBUTING rule 7's `read` exception. No Cloudflare account, Access application or service token is available, so no status or redirect destination was observed. During marking review (October 2026) the block passed bash -n under bash 5.3.9 and ShellCheck 0.11.0 without diagnostics. In a scratch-local review, the block ran from a file with a stub curl, no network and a pseudo-terminal: unchanged placeholders printed 'substitute your own application URL inside the quotes; not probing' (exit 2); substituted dummy inputs printed 'stub curl' (exit 0); and an empty secret printed 'supply the secret without control characters; not probing' (exit 2). The same scratch-local review, with the same stub curl, no network and pseudo-terminal, also ran the readonly cases: readonly HDR printed 'cannot clear HDR in this shell; not probing' (exit 2), and readonly IFS printed 'a readonly IFS is set in this shell; not probing' (exit 2). The stub output is not a Cloudflare response; the expected live comparison remains anonymous denial or Access login versus application content with a valid service token. Use Bash in a fresh, trusted shell and replace the URL and client ID inside the quotes. Paste the secret alone at the hidden prompt, never into the command: a multi-line paste leaves every line after the first for your shell to run. The block discards the body and prints only the status and redirect destination; a 200 alone cannot identify the content. The secret stays in an unexported subshell variable and reaches curl on stdin, which keeps it out of argv and shell history but does not hide it from `set -x` tracing (the block turns tracing off) or the account owner or root.

```bash
# REASONED: no live Cloudflare account is available; not demonstrated against exposed and protected apps. The cited Cloudflare service-token documentation specifies the two headers and Service Auth policy.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  { unset -n HDR && unset -v HDR; } 2>/dev/null ||
    { echo 'cannot clear HDR in this shell; not probing'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not probing'; exit 2; }
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HTTPS_APP_URL' 'REPLACE_WITH_CLIENT_ID'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not probing'; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo 'the set -- line needs a URL and client ID; not probing'; exit 2; }
  case "$1" in
    ''|*REPLACE_WITH_*|*example.com*|*example.net*|*example.org*|*[[:cntrl:]]*)
      echo 'substitute your own application URL inside the quotes; not probing'; exit 2 ;;
    https://*) ;;
    *) echo 'use an https:// URL; not probing'; exit 2 ;;
  esac
  case "$2" in
    ''|*REPLACE_WITH_*|*[[:cntrl:]]*) echo 'supply the client ID without control characters; not probing'; exit 2 ;;
  esac
  IFS= read -r -s -p 'Client secret (input hidden): ' HDR ||
    { echo 'secret input failed; not probing'; exit 2; }
  printf '\n'
  case "$HDR" in
    ''|*REPLACE_WITH_*|*[[:cntrl:]]*) echo 'supply the secret without control characters; not probing'; exit 2 ;;
  esac
  HDR="CF-Access-Client-Secret: $HDR"
  printf '%s\n' "CF-Access-Client-Id: $2" "$HDR" |
    curl -q -g -sS --connect-timeout 5 --max-time 20 --output /dev/null \
      --write-out 'http=%{http_code} location=%{redirect_url}\n' --header @- "$1" || exit 2
  unset -v HDR
)
```

- REASONED: binding and effective policy for each topology; local marking review (October 2026, Bash 5.3.9) ran ss -tlnp with an ss stub, which printed 'stub ss args=-tlnp' (exit 0), not host socket state. A live origin stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; no deployed origin with a firewall and container-publication inventory, remote cloudflared host, AOP client certificate or external probe host was available to this marking review. Exposed same-host binding is expected to show a wildcard (0.0.0.0, [::] or *) or non-loopback address and answer directly, while fixed binding is expected to show 127.0.0.1 and answer only locally. Exposed remote-origin policy is expected to admit callers besides the cloudflared host; fixed policy is expected to admit that host and deny or filter others. Exposed no-tunnel 443 is expected to admit non-Cloudflare callers or lack enforced client certificates. Fixed no-tunnel 443 policy is expected to admit Cloudflare IP ranges with AOP and deny or filter others. Both no-tunnel 443 expectations follow the guide's cited Create a remotely-managed tunnel, Authenticated Origin Pulls (the origin must validate the client certificate; shared vs zone-level cert), and Cloudflare IP ranges (origin firewall allowlist). `ss -tlnp` shows the app on `127.0.0.1` only for a same-host tunnel. Do not settle for "no inbound rule added": confirm the port's effective inbound policy, since a default-accept policy, a pre-existing broad allow, or a container publishing through its own NAT can leave it open. The policy differs by topology: a same-host tunnel app is on loopback, a remote tunnel origin accepts only the `cloudflared` host, and a no-tunnel HTTPS origin accepts only Cloudflare's IP ranges (plus AOP).
- REASONED: external direct-origin probe on port 3000; local marking review (October 2026, Bash 5.3.9) passed the following block through bash -n and ShellCheck 0.11.0 without output. With a curl stub, placeholder and empty values each printed "substitute your origin's public IP on the set -- line above; not probing" (exit 2), and zero and two values each printed "the set -- line needs exactly 1 value; not probing" (exit 2). The same curl stub fixtures included a wrong marker, which printed "paste the whole block, including its set -- line; not probing" (exit 2), and a valid fixture, which printed 'stub curl args=-q -g -s -o /dev/null --noproxy * --connect-timeout 5 --max-time 20 -w http=%{http_code} exit=%{exitcode} err=%{errormsg}\n http://203.0.113.10:3000/' (exit 0). A live origin stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; no external probe host, deployed origin or allowed-vantage tunnel host control was available to this marking review. On 2026-10-17 the HTTP block passed `bash -n` and ShellCheck 0.11.0 with `-s bash`; a curl stub simulated transfer exits 0, 7 and 28, while its placeholder guard exited 2. The three remote HTTPS allowed-vantage controls ran with a curl stub; with distinct certificate and HTTP Host names, the differing-name form sent `-H` and `--connect-to` separately. As this guide's assessment, an exposed origin is expected to give an HTTP reply directly; the fixed outcome requires an explicit refusal from the independently confirmed origin address, a successful allowed-vantage control and the effective inbound-policy check; no reply is inconclusive, per the guide's cited Create a remotely-managed tunnel. From another host, confirm the origin is not reachable directly on the app's own port (3000 over HTTP in this same-host example; substitute yours). For a remote origin with `service: https://...`, use the HTTPS block below on that service URL's port. As this guide's assessment, a refusal supports isolation only after independently confirming that the public address being probed belongs to this origin; neither allowed-vantage control establishes that address mapping. On the tunnel host, the allowed-vantage control `curl -q -g -s -o /dev/null --noproxy '*' -w '%{http_code}\n' http://127.0.0.1:3000/` must return the app's status (not 000). A remote origin needs the matching HTTPS control: run that control from the `cloudflared` host and require the app's status (not 000), using `curl -q -g -s -o /dev/null --noproxy '*' -H 'Host: REPLACE_WITH_EFFECTIVE_HTTP_HOST' -w '%{http_code}\n' 'REPLACE_WITH_SERVICE_URL'` with system trust. The remote-origin control from the `cloudflared` host must instead be `curl -q -g -s -o /dev/null --noproxy '*' -H 'Host: REPLACE_WITH_EFFECTIVE_HTTP_HOST' --cacert 'REPLACE_WITH_COMBINED_CA_BUNDLE' -w '%{http_code}\n' 'REPLACE_WITH_SERVICE_URL'` when `caPool` is set, with the same required app status (not 000). The combined bundle must contain the default trusted roots used by `cloudflared` and the configured `caPool` certificates. When the effective certificate name is not the service URL host, use `curl -q -g -s -o /dev/null --noproxy '*' -H 'Host: REPLACE_WITH_EFFECTIVE_HTTP_HOST' --cacert 'REPLACE_WITH_COMBINED_CA_BUNDLE' --connect-to 'REPLACE_WITH_CERT_HOSTNAME:REPLACE_WITH_HTTPS_PORT:REPLACE_WITH_SERVICE_HOST:REPLACE_WITH_HTTPS_PORT' -w '%{http_code}\n' 'https://REPLACE_WITH_CERT_HOSTNAME:REPLACE_WITH_HTTPS_PORT/'`. The differing-name form may omit `--cacert` only when system trust reproduces tunnel trust. Choose the effective HTTP Host separately: use the configured HTTP Host Header when set, otherwise the request Host sent to the origin. Substitute it in the `-H` argument, including when it differs from the certificate name. Apply the `matchSNItoHost` override described below when choosing the certificate name. The pinned HTTP Host Header setting and curl `--header` option support this request header. As this guide's assessment, this control shows origin availability, not that the public address in the external probe belongs to it.

REASONED: following block; direct-origin isolation follows the cited Create a remotely-managed tunnel. The authoring environment cannot provision a Cloudflare origin and external probe host; no live outcome is recorded. Expected refusal, exposure and inconclusive outcomes are stated below.

```bash
(                                             # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_ORIGIN_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_ORIGIN_IP*|"") echo "substitute your origin's public IP on the set -- line above; not probing"; exit 2 ;;
    *) curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
         -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:3000/" ;;   # the app's own port
  esac
)
```

REASONED: following block; remote-origin HTTPS direct probe; on 2026-10-17 the changed block passed `bash -n` and ShellCheck 0.11.0 with `-s bash`. A curl stub in that 2026-10-17 review exercised the placeholders and invalid HTTP Host and port guards (exit 2), including ports 0 and above 65535 (exit 2), ports 443 and 65535 (exit 0) and bracketed IPv6 (exit 0), and simulated transfer exits 0, 7, 28 and 60 under both SYSTEM_TRUST and combined-CA branches. With distinct certificate and HTTP Host names, the stub received `--connect-to` for the certificate name and `-H` for the HTTP Host in both branches; no live response was observed. No live remote origin or external probe host was available. Use the `https://` service URL port and its certificate hostname. Set the third value to the effective HTTP Host sent to the origin: the configured HTTP Host Header when set, otherwise the request Host. Guard and send it separately from the certificate name, including when the values differ. Set the fourth value to `SYSTEM_TRUST` when `originRequest.caPool` is unset and the issuing CA is trusted by the probe host; otherwise supply a PEM bundle containing both the default trusted roots used by `cloudflared` and the certificates in `originRequest.caPool`. Build that bundle from the relevant default root store and the configured `caPool` PEM; a `caPool` file alone does not reproduce the combined trust pool. If the effective trust roots cannot be reproduced, treat a TLS trust failure as inconclusive. Use the service URL host as the certificate hostname unless `originServerName` sets a different one. When `matchSNItoHost` is true, it overrides `originServerName`: use the request `Host` value sent to the origin, or the configured HTTP Host Header value, as the effective SNI/certificate name for that request. As this guide's assessment, if this value varies or cannot be established, the hostname probe is inconclusive. As this guide's assessment, for an IPv6 origin address, put brackets around the address inside the first quoted value for `--connect-to`. The pinned Cloudflare origin parameters define that name, the SNI override, the HTTP Host Header and the additive CA pool; the pinned curl `--cacert`, `--connect-to` and `--header` entries define the trust file, destination override and HTTP header. As this guide's assessment, a TLS trust or hostname error is inconclusive, especially when the combined trust pool cannot be reproduced; after confirming the address mapping, an HTTP reply directly on the origin port shows exposure; a refusal supports isolation only with the effective inbound policy check and a successful allowed-vantage control. As this guide's assessment, the allowed-vantage control above shows that the origin answers but does not confirm the probed public address.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_ORIGIN_IP' 'REPLACE_WITH_CERT_HOSTNAME' 'REPLACE_WITH_EFFECTIVE_HTTP_HOST' 'REPLACE_WITH_COMBINED_CA_BUNDLE_OR_SYSTEM_TRUST' 'REPLACE_WITH_ORIGIN_HTTPS_PORT'  # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not probing'; exit 2; }
  shift
  [ "$#" -eq 5 ] || { echo 'the set -- line needs an origin IP, certificate hostname, HTTP Host, CA choice and port; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*|-*|*[[:space:]]*) echo 'substitute your origin public IP; not probing'; exit 2 ;; esac
  case "$2" in ''|*REPLACE_WITH_*|-*|*[[:space:]]*) echo 'substitute the certificate hostname; not probing'; exit 2 ;; esac
  case "$3" in ''|*REPLACE_WITH_*|-*|*[[:space:][:cntrl:]]*) echo 'substitute the effective HTTP Host; not probing'; exit 2 ;; esac
  case "$4" in ''|*REPLACE_WITH_*|-*|*[[:space:]]*) echo 'supply SYSTEM_TRUST or the combined CA bundle path; not probing'; exit 2 ;; esac
  case "$5" in ''|*[!0123456789]*) echo 'supply an HTTPS port from 1 to 65535; not probing'; exit 2 ;; esac
  if [ "${#5}" -gt 5 ] || [ "$5" -lt 1 ] || [ "$5" -gt 65535 ]; then
    echo 'supply an HTTPS port from 1 to 65535; not probing'; exit 2
  fi
  if [ "$4" = SYSTEM_TRUST ]; then
    curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
      -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' -H "Host: $3" --connect-to "$2:$5:$1:$5" "https://$2:$5/"
  else
    curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
      --cacert "$4" -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
      -H "Host: $3" --connect-to "$2:$5:$1:$5" "https://$2:$5/"
  fi
)
```

REASONED: external direct-origin outcome; local marking review (October 2026, Bash 5.3.9) used the curl stub above, not a live origin. A live origin stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; an external probe host, deployed origin and tunnel-host control were unavailable. As this guide's assessment, read err, not the number: `err` text reporting a refused connection to your confirmed origin address supports the fixed state only with the effective inbound-policy check and a successful allowed-vantage control. The successful allowed-vantage control, as this guide's assessment, is the tunnel-host loopback control `curl -q -g -s -o /dev/null --noproxy '*' -w '%{http_code}\n' http://127.0.0.1:3000/` returning the app's status (not 000). A remote origin's successful allowed-vantage control, as this guide's assessment, is instead one of the matching HTTPS controls above from the `cloudflared` host returning the app's status (not 000), using the combined CA bundle when `originRequest.caPool` is set. This guide's assessment is that any HTTP status (http= not 000) from that confirmed origin address means something answered directly on the app's port and Access is bypassed. As this guide's assessment, an HTTP reply from an unconfirmed address means something answers there; confirm the mapping before calling it this origin's exposure, and never treat that reply as fixed. As this guide's assessment, a timeout, no reply, resolver failure, TLS trust or hostname failure, or error whose destination is uncertain is inconclusive. As this guide's assessment, neither allowed-vantage control proves that the probed public address belongs to this origin; confirm it independently before calling a refusal fixed. Use curl 7.75.0 or newer for `%{exitcode}` and `%{errormsg}` write-out. These expectations follow the cited Create a remotely-managed tunnel; the cited curl manual (stdin headers, output, redirect reporting and write-out variables) explains the printed transfer status and error.

- REASONED: no-tunnel AOP origin and its port-80 sentence; local marking review (October 2026, Bash 5.3.9) reviewed the cited Authenticated Origin Pulls (the origin must validate the client certificate; shared vs zone-level cert) and Cloudflare IP ranges (origin firewall allowlist) guidance. The same local marking review (October 2026, Bash 5.3.9) ran the port-80 block below through bash -n, ShellCheck 0.11.0 and curl-stub guard fixtures, not against a live origin. A live origin stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; an external probe host, deployed no-tunnel origin, Origin CA and allowed-vantage service-token control were unavailable. The no-tunnel AOP origin needs a different check, because the direct request goes to the origin's HTTPS port and its Origin CA certificate is not trusted by an ordinary client. Independently confirm that the public address supplied to `--resolve` belongs to this origin; the service-token GET shows that the app answers through Cloudflare but does not establish that address mapping. Trust the origin's server CA so a server-certificate error does not mask the result, and read the response: `curl -q -g -s --noproxy '*' --cacert REPLACE_WITH_ORIGIN_SERVER_CA --resolve app.example.com:443:REPLACE_WITH_YOUR_ORIGIN_IP -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' https://app.example.com/`. As this guide's assessment, AOP is working when the independently confirmed origin address refuses the missing client certificate (a TLS alert, or nginx's `400 No required SSL certificate was sent`); a failure is your application's content coming back from that confirmed address. As this guide's assessment, a refusal or reply from an unconfirmed address shows only that something answers there; confirm the mapping before calling this origin fixed or exposed. Distinguish the layers, since all three withhold content for different reasons: a firewall drop is inconclusive in this probe even when the service-token GET answers; confirm isolation with the effective inbound-policy check above. As this guide's assessment, a client-certificate refusal from the confirmed origin address indicates AOP, and a `401`/`403` from that address indicates the app's own authorization. These outcome interpretations are this guide's assessment, per the cited Authenticated Origin Pulls (the origin must validate the client certificate; shared vs zone-level cert), Cloudflare Authenticated Origin Pulls and tunnel incompatibility, and Cloudflare Origin CA certificates and direct browser trust entries. This guide's assessment of these outcomes also rests on the cited curl manual (stdin headers, output, redirect reporting and write-out variables), curl noproxy and curl globoff entries. Confirm separately that port 80 does not serve the app.

REASONED: no-tunnel port-80 policy; AOP authenticates HTTPS client certificates, so an HTTP origin route must not serve app content, per the cited Authenticated Origin Pulls (the origin must validate the client certificate; shared vs zone-level cert). Check a known app route from an external host with the following block, replacing the origin IP, app hostname and route inside the quotes. On the same route, the service-token GET in the service-token block above is the allowed-vantage control and must return its success status. As this guide's assessment, a fixed origin gives an explicit refusal or only a redirect to the canonical HTTPS host from the independently confirmed origin address (the listed Sources do not prescribe a code), without app content; either fixed outcome requires that control to answer. As this guide's assessment, a timeout or no reply alone is inconclusive; app route content served over HTTP from that confirmed origin address is the exposed outcome. As this guide's assessment, app content from an unconfirmed address shows only that something answers there; confirm the mapping before calling this origin exposed. As this guide's assessment, the service-token GET proves that the application route answers through Cloudflare, but does not confirm that the public address probed on port 80 belongs to this origin; check that mapping independently before treating a refusal as fixed. Use curl 7.75.0 or newer for `%{exitcode}` and `%{errormsg}` write-out; the cited curl manual (stdin headers, output, redirect reporting and write-out variables) supports the printed status and error.

REASONED: following block; port-80 HTTP virtual-host route probe; local marking review (October 2026, Bash 5.3.9) passed bash -n and ShellCheck 0.11.0 without output. With a curl stub, a wrong marker printed "paste the whole block, including its set -- line; not probing" (exit 2); zero, two and four values each printed "the set -- line needs an origin IP, app hostname and app route; not probing" (exit 2); address placeholder, empty, option-like and spaced values each printed "substitute your origin's public IP on the set -- line above; not probing" (exit 2). The same curl stub fixtures had the default placeholders and hostname placeholder, empty, option-like and spaced values each print "substitute your app hostname on the set -- line above; not probing" (exit 2), and route placeholder, empty, option-like and spaced values each print "substitute your app route on the set -- line above; not probing" (exit 2). The same curl stub fixtures also included a route without a leading slash, which printed "use a route starting with /; not probing" (exit 2). The valid curl stub fixture printed 'stub curl args=-q -g -s -D - -o - --noproxy * --connect-timeout 5 --max-time 20 -w http=%{http_code} exit=%{exitcode} err=%{errormsg} location=%{redirect_url}\n --resolve app.example.com:80:203.0.113.10 http://app.example.com/health' (exit 0). A live origin stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; an external probe host, deployed no-tunnel origin, Origin CA and allowed-vantage service-token control were unavailable. On 2026-10-17 this unchanged port-80 block passed `bash -n` and ShellCheck with `-s bash`; a curl stub produced HTTP 200 (exit 0), canonical HTTPS redirect (exit 0), explicit refusal (exit 7) and timeout (exit 28) outputs, while its placeholder guard exited 2. No live refusal, redirect or app response was observed; expected outcomes are stated above, per the cited Authenticated Origin Pulls (the origin must validate the client certificate; shared vs zone-level cert) and curl manual (stdin headers, output, redirect reporting and write-out variables).

```bash
(                                             # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_ORIGIN_IP' 'REPLACE_WITH_APP_HOSTNAME' 'REPLACE_WITH_APP_ROUTE'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 3 ] || { echo "the set -- line needs an origin IP, app hostname and app route; not probing"; exit 2; }
  case "$2" in
    *REPLACE_WITH_*|""|-*|*[[:space:]]*) echo "substitute your app hostname on the set -- line above; not probing"; exit 2 ;;
  esac
  case "$3" in
    *REPLACE_WITH_*|""|-*|*[[:space:]]*) echo "substitute your app route on the set -- line above; not probing"; exit 2 ;;
    /*) ;;
    *) echo "use a route starting with /; not probing"; exit 2 ;;
  esac
  case "$1" in
    *REPLACE_WITH_*|*YOUR_ORIGIN_IP*|""|-*|*[[:space:]]*) echo "substitute your origin's public IP on the set -- line above; not probing"; exit 2 ;;
    *) curl -q -g -s -D - -o - --noproxy '*' --connect-timeout 5 --max-time 20 \
         -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg} location=%{redirect_url}\n' --resolve "$2:80:$1" "http://$2$3" ;;
  esac
)
```

## Sources (checked September 2026)

- Cloudflare Zero Trust documentation: https://developers.cloudflare.com/cloudflare-one/
- Create a remotely-managed tunnel: https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/get-started/create-remote-tunnel/
- cloudflared releases: https://github.com/cloudflare/cloudflared
- Cloudflare Zero Trust plans (rolling; fetched page did not state a user limit; check current plan limits, including the free plan's, with Cloudflare, checked October 2026): https://www.cloudflare.com/plans/zero-trust-services/
- Cloudflare Quick Tunnels (temporary URL, access by URL without allowed-mail, email PIN option and testing/development use; pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, lines 13-42, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/tunnel/get-started/quick-tunnels/index.mdx#L13-L42
- cloudflared TryCloudflare testing note (pinned tag 2026.9.3, lines 50-52, checked October 2026): https://github.com/cloudflare/cloudflared/blob/2026.9.3/README.md#L50-L52
- Authenticated Origin Pulls (the origin must validate the client certificate; shared vs zone-level cert): https://developers.cloudflare.com/ssl/origin-configuration/authenticated-origin-pull/
- Cloudflare IP ranges (origin firewall allowlist): https://www.cloudflare.com/ips/
- cloudflared as a Linux service (pass --config under sudo): https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/as-a-service/linux/
- Cloudflare Access One-time PIN (login methods coexist with an IdP): https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/one-time-pin/
- Cloudflare Access service tokens (request headers and Service Auth policy): https://developers.cloudflare.com/cloudflare-one/access-controls/service-credentials/service-tokens/
- curl manual (stdin headers, output, redirect reporting and write-out variables): https://curl.se/docs/manpage.html
- cloudflared run parameters (`--token-file`, requires 2025.4.0 or later): https://developers.cloudflare.com/tunnel/reference/run-parameters/#token-file
- Tunnel tokens (retrieving the token from the dashboard installation command without running it): https://developers.cloudflare.com/tunnel/reference/tunnel-tokens/
- cloudflared 2026.9.3 service installer (runs `tunnel run --token-file`): https://github.com/cloudflare/cloudflared/blob/2026.9.3/cmd/cloudflared/common_service.go
- Cloudflare Access JWT signature, issuer and application audience validation (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json.mdx#L154-L157
- Cloudflare Tunnel origin caPool trust and noTLSVerify behavior (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/cloudflare-one/tunnel/origin-parameters.mdx#L51-L67
- Cloudflare Full (strict) origin certificate requirements (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/ssl/origin-configuration/ssl-modes/full-strict.mdx#L29-L33
- Cloudflare Origin CA certificates and direct browser trust (pinned commit c896795b8e8bab68d05ae78d64c9cbcda1fdb104, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/ssl/origin-ca-pause-error.mdx#L8
- Cloudflare Tunnel origin server name and matchSNItoHost override (pinned, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/cloudflare-one/tunnel/origin-parameters.mdx#L31-L49
- curl cacert (pinned, checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/cacert.md#L19-L24
- curl connect-to (pinned, checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/connect-to.md#L17-L22
- curl header (pinned, checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/header.md#L23-L40
- Cloudflare Tunnel HTTP Host Header (pinned, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/cloudflare-one/tunnel/origin-parameters.mdx#L89-L95
- curl noproxy (pinned, checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/noproxy.md#L18-L23
- curl globoff (pinned, checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/globoff.md#L17-L22
- Cloudflare Authenticated Origin Pulls and tunnel incompatibility (pinned, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/ssl/origin-configuration/authenticated-origin-pull/index.mdx#L16-L26


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- token-file: cloudflared token-file minimum (2025.4.0)
- installer: cloudflared service installer (2026.9.3)
- cloudflared-readme: cloudflared README (2026.9.3)
- cf: Cloudflare Zero Trust (unknown)
- cf-docs: Cloudflare documentation (c896795b8e8bab68d05ae78d64c9cbcda1fdb104)
- curl: curl manual (unknown)
- curl-opts: curl command-line options (curl-8_23_0)

Claims (full source mapping in the JSON block below):

- outbound (REASONED; cf): cloudflared opens an outbound-only encrypted tunnel; edge HTTPS needs no inbound firewall ports.
- prerequisites (REASONED; cf): Cloudflare DNS domain and Zero Trust organization required; check current plan limits, including the free plan's, with Cloudflare; the fetched plans page did not state a user limit, and this guide does not establish one.
- remote (REASONED; cf, token-file): Copy the dashboard tunnel token to a protected file and configure the OS service to use it; publish the hostname route to http://localhost:3000 only after Access is in place.
- publish-order (REASONED; cf): Create Access before publishing the route, or keep the app stopped; routing alone exposes it without login and a stopped origin still has public DNS.
- tls-hops (REASONED; cf): Edge terminates TLS, the tunnel is encrypted, and HTTP to localhost:3000 stays on the host.
- local (REASONED; cf): Locally managed login/create/route dns, tunnel UUID and credentials-file configure app ingress followed by http_status:404.
- service (REASONED; cf): Run by tunnel name or install with an explicit --config under sudo, whose HOME is /root.
- secrets (REASONED; cf): Tunnel credentials JSON and tokens allow service publication on the hostname; keep them out of repositories.
- access (REASONED; cf): Self-hosted Access application plus Allow policy limits login to listed emails or domains.
- otp (REASONED; cf): One-time PIN proves mailbox control; SSO can inherit IdP MFA.
- mfa-bypass (REASONED; cf): When PIN and an IdP coexist, either can be chosen; remove PIN or enforce Access MFA across methods for sensitive apps.
- service-token (REASONED; cf, curl): Machine access needs a service token and Service Auth policy. Read the secret at a hidden prompt in a fresh trusted Bash shell, keep it unexported in a subshell, and pipe Client-Id and Client-Secret headers to curl --header @-; this avoids argv/history exposure but not access by the account owner or root.
- loopback (REASONED; cf): Bind the same-host app to 127.0.0.1 so direct public requests cannot bypass Access.
- jwt (REASONED; cf, cf-docs): Validate Cf-Access-Jwt-Assertion signature, issuer and application audience; origin reachability, SSRF and another route can bypass the front door.
- route-coverage (REASONED; cf): Every added tunnel hostname/path needs an Access application and policy, including coverage by a wildcard application.
- quick (REASONED; cf, cf-docs, cloudflared-readme): Quick trycloudflare.com tunnels without --allowed-mail let anyone with the URL access the service; Cloudflare describes them as temporary and for testing and development, not production.
- remote-origin (REASONED; cf): A remote origin needs HTTPS and a firewall allowing only the cloudflared host; TLS alone does not restrict callers.
- origin-ca (REASONED; cf, cf-docs): Use originRequest.caPool for a self-signed origin; noTLSVerify discards server authentication.
- full-strict (REASONED; cf, cf-docs): Full (strict) with an Origin CA certificate authenticates the origin to Cloudflare, not callers; browsers do not trust that certificate directly.
- aop (REASONED; cf): AOP requires origin-side client-certificate enforcement; nginx uses ssl_verify_client on and ssl_client_certificate.
- aop-zone (REASONED; cf): Global AOP proves only Cloudflare network membership; prefer a zone certificate and its issuing CA, removing shared-CA trust.
- origin-ports (REASONED; cf): For a no-tunnel origin, restrict 443 to Cloudflare IP ranges and close 80 or redirect only to the canonical HTTPS host without app content; the listed Sources do not prescribe a redirect code, and mTLS cannot authenticate plaintext HTTP.
- verify-login (REASONED; cf): Private browsing must show Access login; anonymous HEAD must redirect to the team's cloudflareaccess.com login, never app content.
- verify-token (REASONED; cf, curl): On a route known to serve application content with HTTP 200, send the hidden-prompt service token through curl --header @- and expect http=200 location=. Login redirects, denials and transport errors fail; compare anonymous denial because token success alone does not prove Access enforcement. The probe discards the body, so 200 alone cannot identify content.
- verify-policy (REASONED; cf): Inspect loopback binding and effective inbound policy, including existing allows and container NAT; permitted sources depend on topology.
- verify-origin (REASONED; cf, curl, cf-docs, curl-opts): Externally, the confirmed origin address explicitly refusing the app port, plus a passing allowed-vantage control and effective inbound-policy check, supports isolation; any HTTP reply from that address directly on the app's port exposes bypass. No reply is inconclusive; an unconfirmed address's HTTP reply is never fixed, nor exposure until mapped (this guide's assessment of probe outcomes).
- verify-aop (REASONED; cf, cf-docs, curl, curl-opts): On direct 443 with the origin server CA trusted, a missing-client-certificate refusal indicates AOP only from an independently confirmed origin address; an unconfirmed address's refusal or reply needs mapping confirmation before a fixed or exposed verdict. A firewall drop is inconclusive in this probe; effective inbound policy establishes isolation (this guide's assessment of probe outcomes).
- verify-http (REASONED; cf, curl): Externally, on no-tunnel port 80 for a known app route, an explicit refusal or a canonical HTTPS redirect without app content from the confirmed origin address supports the fixed state if the route's service-token GET succeeds; app content from that address is exposure. No reply is inconclusive; unconfirmed-address content is not exposure until mapped (this guide's assessment of probe outcomes).
- token-file (REASONED; token-file, cf): cloudflared 2025.4.0 or later supports tunnel run --token-file /absolute/path/to/token; restrict the file to the service account with mode 0600 on Linux/macOS or a restricted Windows ACL.
- token-install-argv (REASONED; installer, token-file): Avoid cloudflared service install &lt;TOKEN&gt;: the token is exposed on the installer argv, even though the cited 2026.9.3 installer runs the service with --token-file.

````json
{
  "schema": 1,
  "checked": "2026-10-18",
  "documentation_checked": "2026-09",
  "body_sha256": "ad4fcaa94847979d8d1430c3e49d3525025e2dc7e29fdb52914d90e32d8dcf8d",
  "components": {
    "token-file": {
      "name": "cloudflared token-file minimum",
      "basis": "2025.4.0",
      "sources": {
        "sde222f01d112": "https://developers.cloudflare.com/tunnel/reference/run-parameters/#token-file"
      }
    },
    "installer": {
      "name": "cloudflared service installer",
      "basis": "2026.9.3",
      "sources": {
        "sbe50314c5b92": "https://github.com/cloudflare/cloudflared/blob/2026.9.3/cmd/cloudflared/common_service.go"
      }
    },
    "cloudflared-readme": {
      "name": "cloudflared README",
      "basis": "2026.9.3",
      "sources": {
        "s64bea39fdaff": "https://github.com/cloudflare/cloudflared/blob/2026.9.3/README.md#L50-L52"
      }
    },
    "cf": {
      "name": "Cloudflare Zero Trust",
      "basis": "unknown",
      "sources": {
        "s536e61cfd1d0": "https://developers.cloudflare.com/cloudflare-one/",
        "s160a7accb558": "https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/get-started/create-remote-tunnel/",
        "s58da5534d71a": "https://github.com/cloudflare/cloudflared",
        "sbe2ecd154061": "https://developers.cloudflare.com/ssl/origin-configuration/authenticated-origin-pull/",
        "s9f78b2ad819b": "https://www.cloudflare.com/ips/",
        "sdb4569bc3e0d": "https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/as-a-service/linux/",
        "s5bd93ae868e6": "https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/one-time-pin/",
        "s15ab6de85740": "https://developers.cloudflare.com/cloudflare-one/access-controls/service-credentials/service-tokens/",
        "sd043afad3d8a": "https://developers.cloudflare.com/tunnel/reference/tunnel-tokens/",
        "s8d2f573a9d81": "https://www.cloudflare.com/plans/zero-trust-services/"
      }
    },
    "cf-docs": {
      "name": "Cloudflare documentation",
      "basis": "c896795b8e8bab68d05ae78d64c9cbcda1fdb104",
      "sources": {
        "sc4628a1320d3": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/applications/http-apps/authorization-cookie/validating-json.mdx#L154-L157",
        "sa102d58fd878": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/cloudflare-one/tunnel/origin-parameters.mdx#L51-L67",
        "sf8ae935ddb55": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/ssl/origin-configuration/ssl-modes/full-strict.mdx#L29-L33",
        "s4a635dc9bd32": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/ssl/origin-ca-pause-error.mdx#L8",
        "s253af0f0386c": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/cloudflare-one/tunnel/origin-parameters.mdx#L31-L49",
        "s64e79c014e9a": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/partials/cloudflare-one/tunnel/origin-parameters.mdx#L89-L95",
        "s78f4d7c15ff5": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/ssl/origin-configuration/authenticated-origin-pull/index.mdx#L16-L26",
        "sd114b2a04351": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/tunnel/get-started/quick-tunnels/index.mdx#L13-L42"
      }
    },
    "curl": {
      "name": "curl manual",
      "basis": "unknown",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    },
    "curl-opts": {
      "name": "curl command-line options",
      "basis": "curl-8_23_0",
      "sources": {
        "s528fcc47043d": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/cacert.md#L19-L24",
        "sce3838e7adf1": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/connect-to.md#L17-L22",
        "s9665b1ea8cc7": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/header.md#L23-L40",
        "s508454c45cf1": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/noproxy.md#L18-L23",
        "s511177850f9e": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/globoff.md#L17-L22"
      }
    }
  },
  "claims": {
    "outbound": {"text": "cloudflared opens an outbound-only encrypted tunnel; edge HTTPS needs no inbound firewall ports.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0", "cf:s160a7accb558"], "status": "REASONED"},
    "prerequisites": {"text": "Cloudflare DNS domain and Zero Trust organization required; check current plan limits, including the free plan's, with Cloudflare; the fetched plans page did not state a user limit, and this guide does not establish one.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0", "cf:s160a7accb558", "cf:s8d2f573a9d81"], "status": "REASONED"},
    "remote": {"text": "Copy the dashboard tunnel token to a protected file and configure the OS service to use it; publish the hostname route to http://localhost:3000 only after Access is in place.", "components": ["cf", "token-file"], "sources": ["cf:s160a7accb558", "cf:sd043afad3d8a", "token-file:sde222f01d112"], "status": "REASONED"},
    "publish-order": {"text": "Create Access before publishing the route, or keep the app stopped; routing alone exposes it without login and a stopped origin still has public DNS.", "components": ["cf"], "sources": ["cf:s160a7accb558", "cf:s536e61cfd1d0"], "status": "REASONED"},
    "tls-hops": {"text": "Edge terminates TLS, the tunnel is encrypted, and HTTP to localhost:3000 stays on the host.", "components": ["cf"], "sources": ["cf:s160a7accb558"], "status": "REASONED"},
    "local": {"text": "Locally managed login/create/route dns, tunnel UUID and credentials-file configure app ingress followed by http_status:404.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0", "cf:sdb4569bc3e0d"], "status": "REASONED"},
    "service": {"text": "Run by tunnel name or install with an explicit --config under sudo, whose HOME is /root.", "components": ["cf"], "sources": ["cf:sdb4569bc3e0d"], "status": "REASONED"},
    "secrets": {"text": "Tunnel credentials JSON and tokens allow service publication on the hostname; keep them out of repositories.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0", "cf:s160a7accb558", "cf:sdb4569bc3e0d"], "status": "REASONED"},
    "access": {"text": "Self-hosted Access application plus Allow policy limits login to listed emails or domains.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0", "cf:s5bd93ae868e6"], "status": "REASONED"},
    "otp": {"text": "One-time PIN proves mailbox control; SSO can inherit IdP MFA.", "components": ["cf"], "sources": ["cf:s5bd93ae868e6"], "status": "REASONED"},
    "mfa-bypass": {"text": "When PIN and an IdP coexist, either can be chosen; remove PIN or enforce Access MFA across methods for sensitive apps.", "components": ["cf"], "sources": ["cf:s5bd93ae868e6", "cf:s536e61cfd1d0"], "status": "REASONED"},
    "service-token": {"text": "Machine access needs a service token and Service Auth policy. Read the secret at a hidden prompt in a fresh trusted Bash shell, keep it unexported in a subshell, and pipe Client-Id and Client-Secret headers to curl --header @-; this avoids argv/history exposure but not access by the account owner or root.", "components": ["cf", "curl"], "sources": ["cf:s15ab6de85740", "curl:s2b2686afaf41"], "status": "REASONED"},
    "loopback": {"text": "Bind the same-host app to 127.0.0.1 so direct public requests cannot bypass Access.", "components": ["cf"], "sources": ["cf:s160a7accb558"], "status": "REASONED"},
    "jwt": {"text": "Validate Cf-Access-Jwt-Assertion signature, issuer and application audience; origin reachability, SSRF and another route can bypass the front door.", "components": ["cf", "cf-docs"], "sources": ["cf:s536e61cfd1d0", "cf-docs:sc4628a1320d3"], "status": "REASONED"},
    "route-coverage": {"text": "Every added tunnel hostname/path needs an Access application and policy, including coverage by a wildcard application.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0"], "status": "REASONED"},
    "quick": {"text": "Quick trycloudflare.com tunnels without --allowed-mail let anyone with the URL access the service; Cloudflare describes them as temporary and for testing and development, not production.", "components": ["cf", "cf-docs", "cloudflared-readme"], "sources": ["cf:s536e61cfd1d0", "cf:s58da5534d71a", "cf-docs:sd114b2a04351", "cloudflared-readme:s64bea39fdaff"], "status": "REASONED"},
    "remote-origin": {"text": "A remote origin needs HTTPS and a firewall allowing only the cloudflared host; TLS alone does not restrict callers.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0", "cf:s160a7accb558"], "status": "REASONED"},
    "origin-ca": {"text": "Use originRequest.caPool for a self-signed origin; noTLSVerify discards server authentication.", "components": ["cf", "cf-docs"], "sources": ["cf:s536e61cfd1d0", "cf-docs:sa102d58fd878"], "status": "REASONED"},
    "full-strict": {"text": "Full (strict) with an Origin CA certificate authenticates the origin to Cloudflare, not callers; browsers do not trust that certificate directly.", "components": ["cf", "cf-docs"], "sources": ["cf:sbe2ecd154061", "cf-docs:sf8ae935ddb55", "cf-docs:s4a635dc9bd32"], "status": "REASONED"},
    "aop": {"text": "AOP requires origin-side client-certificate enforcement; nginx uses ssl_verify_client on and ssl_client_certificate.", "components": ["cf"], "sources": ["cf:sbe2ecd154061"], "status": "REASONED"},
    "aop-zone": {"text": "Global AOP proves only Cloudflare network membership; prefer a zone certificate and its issuing CA, removing shared-CA trust.", "components": ["cf"], "sources": ["cf:sbe2ecd154061"], "status": "REASONED"},
    "origin-ports": {"text": "For a no-tunnel origin, restrict 443 to Cloudflare IP ranges and close 80 or redirect only to the canonical HTTPS host without app content; the listed Sources do not prescribe a redirect code, and mTLS cannot authenticate plaintext HTTP.", "components": ["cf"], "sources": ["cf:sbe2ecd154061", "cf:s9f78b2ad819b"], "status": "REASONED"},
    "verify-login": {"text": "Private browsing must show Access login; anonymous HEAD must redirect to the team's cloudflareaccess.com login, never app content.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0", "cf:s5bd93ae868e6"], "status": "REASONED"},
    "verify-token": {"text": "On a route known to serve application content with HTTP 200, send the hidden-prompt service token through curl --header @- and expect http=200 location=. Login redirects, denials and transport errors fail; compare anonymous denial because token success alone does not prove Access enforcement. The probe discards the body, so 200 alone cannot identify content.", "components": ["cf", "curl"], "sources": ["cf:s15ab6de85740", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-policy": {"text": "Inspect loopback binding and effective inbound policy, including existing allows and container NAT; permitted sources depend on topology.", "components": ["cf"], "sources": ["cf:s160a7accb558", "cf:sbe2ecd154061", "cf:s9f78b2ad819b"], "status": "REASONED"},
    "verify-origin": {"text": "Externally, the confirmed origin address explicitly refusing the app port, plus a passing allowed-vantage control and effective inbound-policy check, supports isolation; any HTTP reply from that address directly on the app's port exposes bypass. No reply is inconclusive; an unconfirmed address's HTTP reply is never fixed, nor exposure until mapped (this guide's assessment of probe outcomes).", "components": ["cf", "curl", "cf-docs", "curl-opts"], "sources": ["cf:s160a7accb558", "curl:s2b2686afaf41", "cf-docs:s253af0f0386c", "curl-opts:s528fcc47043d", "curl-opts:sce3838e7adf1", "cf-docs:sa102d58fd878", "curl-opts:s9665b1ea8cc7", "cf-docs:s64e79c014e9a"], "status": "REASONED", "verify": [2, 3]},
    "verify-aop": {"text": "On direct 443 with the origin server CA trusted, a missing-client-certificate refusal indicates AOP only from an independently confirmed origin address; an unconfirmed address's refusal or reply needs mapping confirmation before a fixed or exposed verdict. A firewall drop is inconclusive in this probe; effective inbound policy establishes isolation (this guide's assessment of probe outcomes).", "components": ["cf", "cf-docs", "curl", "curl-opts"], "sources": ["cf:sbe2ecd154061", "curl:s2b2686afaf41", "cf-docs:s4a635dc9bd32", "curl-opts:s508454c45cf1", "curl-opts:s511177850f9e", "cf-docs:s78f4d7c15ff5"], "status": "REASONED"},
    "verify-http": {"text": "Externally, on no-tunnel port 80 for a known app route, an explicit refusal or a canonical HTTPS redirect without app content from the confirmed origin address supports the fixed state if the route's service-token GET succeeds; app content from that address is exposure. No reply is inconclusive; unconfirmed-address content is not exposure until mapped (this guide's assessment of probe outcomes).", "components": ["cf", "curl"], "sources": ["cf:sbe2ecd154061", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [4]},
    "token-file": {"text": "cloudflared 2025.4.0 or later supports tunnel run --token-file /absolute/path/to/token; restrict the file to the service account with mode 0600 on Linux/macOS or a restricted Windows ACL.", "components": ["token-file", "cf"], "sources": ["token-file:sde222f01d112", "cf:sd043afad3d8a"], "status": "REASONED"},
    "token-install-argv": {"text": "Avoid cloudflared service install <TOKEN>: the token is exposed on the installer argv, even though the cited 2026.9.3 installer runs the service with --token-file.", "components": ["installer", "token-file"], "sources": ["installer:sbe50314c5b92", "token-file:sde222f01d112"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
