---
version_basis: {
  "schema": 1,
  "checked": "2026-09-27",
  "documentation_checked": "2026-09",
  "body_sha256": "3331f12551f4183d56da19a358ce50af40b14b9292e739a1b266b432c9e1224c",
  "components": {
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
        "sd043afad3d8a": "https://developers.cloudflare.com/tunnel/reference/tunnel-tokens/"
      }
    },
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
    "curl": {
      "name": "curl manual",
      "basis": "unknown",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    }
  },
  "claims": {
    "outbound": {"text": "cloudflared opens an outbound-only encrypted tunnel; edge HTTPS needs no inbound firewall ports.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0", "cf:s160a7accb558"], "status": "REASONED"},
    "prerequisites": {"text": "Cloudflare DNS domain and Zero Trust organization required; the guide records a free tier of 50 users, subject to current limits.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0", "cf:s160a7accb558"], "status": "REASONED"},
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
    "jwt": {"text": "Validate Cf-Access-Jwt-Assertion signature, issuer and application audience; origin reachability, SSRF and another route can bypass the front door.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0"], "status": "REASONED"},
    "route-coverage": {"text": "Every added tunnel hostname/path needs an Access application and policy, including coverage by a wildcard application.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0"], "status": "REASONED"},
    "quick": {"text": "Quick trycloudflare.com tunnels are unauthenticated and intended only for short-lived tests.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0", "cf:s58da5534d71a"], "status": "REASONED"},
    "remote-origin": {"text": "A remote origin needs HTTPS and a firewall allowing only the cloudflared host; TLS alone does not restrict callers.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0", "cf:s160a7accb558"], "status": "REASONED"},
    "origin-ca": {"text": "Use originRequest.caPool for a self-signed origin; noTLSVerify discards server authentication.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0"], "status": "REASONED"},
    "full-strict": {"text": "Full (strict) with an Origin CA certificate authenticates the origin to Cloudflare, not callers; browsers do not trust that certificate directly.", "components": ["cf"], "sources": ["cf:sbe2ecd154061"], "status": "REASONED"},
    "aop": {"text": "AOP requires origin-side client-certificate enforcement; nginx uses ssl_verify_client on and ssl_client_certificate.", "components": ["cf"], "sources": ["cf:sbe2ecd154061"], "status": "REASONED"},
    "aop-zone": {"text": "Global AOP proves only Cloudflare network membership; prefer a zone certificate and its issuing CA, removing shared-CA trust.", "components": ["cf"], "sources": ["cf:sbe2ecd154061"], "status": "REASONED"},
    "origin-ports": {"text": "For a no-tunnel origin, restrict 443 to Cloudflare IP ranges and close 80 or redirect only; mTLS cannot authenticate plaintext HTTP.", "components": ["cf"], "sources": ["cf:sbe2ecd154061", "cf:s9f78b2ad819b"], "status": "REASONED"},
    "verify-login": {"text": "Private browsing must show Access login; anonymous HEAD must redirect to the team's cloudflareaccess.com login, never app content.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0", "cf:s5bd93ae868e6"], "status": "REASONED"},
    "verify-token": {"text": "On a route known to serve application content with HTTP 200, send the hidden-prompt service token through curl --header @- and expect http=200 location=. Login redirects, denials and transport errors fail; compare anonymous denial because token success alone does not prove Access enforcement. The probe discards the body, so 200 alone cannot identify content.", "components": ["cf", "curl"], "sources": ["cf:s15ab6de85740", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-policy": {"text": "Inspect loopback binding and effective inbound policy, including existing allows and container NAT; permitted sources depend on topology.", "components": ["cf"], "sources": ["cf:s160a7accb558", "cf:sbe2ecd154061", "cf:s9f78b2ad819b"], "status": "REASONED"},
    "verify-origin": {"text": "From another host, probe the actual origin port 3000: remote refusal/timeout is expected; any HTTP reply exposes bypass, resolver/local errors are inconclusive.", "components": ["cf"], "sources": ["cf:s160a7accb558", "cf:s9f78b2ad819b"], "status": "REASONED", "verify": [2]},
    "verify-aop": {"text": "Trust the origin server CA when probing 443 directly: missing-client-certificate refusal proves AOP; firewall drops and app 401/403 prove different layers.", "components": ["cf"], "sources": ["cf:sbe2ecd154061"], "status": "REASONED"},
    "verify-http": {"text": "Separately confirm the no-tunnel origin's port 80 never serves the app.", "components": ["cf"], "sources": ["cf:sbe2ecd154061", "cf:s9f78b2ad819b"], "status": "REASONED"},
    "token-file": {"text": "cloudflared 2025.4.0 or later supports tunnel run --token-file /absolute/path/to/token; restrict the file to the service account with mode 0600 on Linux/macOS or a restricted Windows ACL.", "components": ["token-file", "cf"], "sources": ["token-file:sde222f01d112", "cf:sd043afad3d8a"], "status": "REASONED"},
    "token-install-argv": {"text": "Avoid cloudflared service install <TOKEN>: the token is exposed on the installer argv, even though the cited 2026.9.3 installer runs the service with --token-file.", "components": ["installer", "token-file"], "sources": ["installer:sbe50314c5b92", "token-file:sde222f01d112"], "status": "REASONED"}
  }
}
---
# Cloudflare Tunnel and Zero Trust Access

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-27; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| outbound: cloudflared opens an outbound-only encrypted tunnel; edge HTTPS needs no inbound firewall ports. | Cloudflare Zero Trust unknown | REASONED |
| prerequisites: Cloudflare DNS domain and Zero Trust organization required; the guide records a free tier of 50 users, subject to current limits. | Cloudflare Zero Trust unknown | REASONED |
| remote: Copy the dashboard tunnel token to a protected file and configure the OS service to use it; publish the hostname route to http://localhost:3000 only after Access is in place. | Cloudflare Zero Trust unknown; cloudflared token-file minimum 2025.4.0 | REASONED |
| publish-order: Create Access before publishing the route, or keep the app stopped; routing alone exposes it without login and a stopped origin still has public DNS. | Cloudflare Zero Trust unknown | REASONED |
| tls-hops: Edge terminates TLS, the tunnel is encrypted, and HTTP to localhost:3000 stays on the host. | Cloudflare Zero Trust unknown | REASONED |
| local: Locally managed login/create/route dns, tunnel UUID and credentials-file configure app ingress followed by http_status:404. | Cloudflare Zero Trust unknown | REASONED |
| service: Run by tunnel name or install with an explicit --config under sudo, whose HOME is /root. | Cloudflare Zero Trust unknown | REASONED |
| secrets: Tunnel credentials JSON and tokens allow service publication on the hostname; keep them out of repositories. | Cloudflare Zero Trust unknown | REASONED |
| access: Self-hosted Access application plus Allow policy limits login to listed emails or domains. | Cloudflare Zero Trust unknown | REASONED |
| otp: One-time PIN proves mailbox control; SSO can inherit IdP MFA. | Cloudflare Zero Trust unknown | REASONED |
| mfa-bypass: When PIN and an IdP coexist, either can be chosen; remove PIN or enforce Access MFA across methods for sensitive apps. | Cloudflare Zero Trust unknown | REASONED |
| service-token: Machine access needs a service token and Service Auth policy. Read the secret at a hidden prompt in a fresh trusted Bash shell, keep it unexported in a subshell, and pipe Client-Id and Client-Secret headers to curl --header @-; this avoids argv/history exposure but not access by the account owner or root. | Cloudflare Zero Trust unknown; curl manual unknown | REASONED |
| loopback: Bind the same-host app to 127.0.0.1 so direct public requests cannot bypass Access. | Cloudflare Zero Trust unknown | REASONED |
| jwt: Validate Cf-Access-Jwt-Assertion signature, issuer and application audience; origin reachability, SSRF and another route can bypass the front door. | Cloudflare Zero Trust unknown | REASONED |
| route-coverage: Every added tunnel hostname/path needs an Access application and policy, including coverage by a wildcard application. | Cloudflare Zero Trust unknown | REASONED |
| quick: Quick trycloudflare.com tunnels are unauthenticated and intended only for short-lived tests. | Cloudflare Zero Trust unknown | REASONED |
| remote-origin: A remote origin needs HTTPS and a firewall allowing only the cloudflared host; TLS alone does not restrict callers. | Cloudflare Zero Trust unknown | REASONED |
| origin-ca: Use originRequest.caPool for a self-signed origin; noTLSVerify discards server authentication. | Cloudflare Zero Trust unknown | REASONED |
| full-strict: Full (strict) with an Origin CA certificate authenticates the origin to Cloudflare, not callers; browsers do not trust that certificate directly. | Cloudflare Zero Trust unknown | REASONED |
| aop: AOP requires origin-side client-certificate enforcement; nginx uses ssl_verify_client on and ssl_client_certificate. | Cloudflare Zero Trust unknown | REASONED |
| aop-zone: Global AOP proves only Cloudflare network membership; prefer a zone certificate and its issuing CA, removing shared-CA trust. | Cloudflare Zero Trust unknown | REASONED |
| origin-ports: For a no-tunnel origin, restrict 443 to Cloudflare IP ranges and close 80 or redirect only; mTLS cannot authenticate plaintext HTTP. | Cloudflare Zero Trust unknown | REASONED |
| verify-login: Private browsing must show Access login; anonymous HEAD must redirect to the team's cloudflareaccess.com login, never app content. | Cloudflare Zero Trust unknown | REASONED |
| verify-token: On a route known to serve application content with HTTP 200, send the hidden-prompt service token through curl --header @- and expect http=200 location=. Login redirects, denials and transport errors fail; compare anonymous denial because token success alone does not prove Access enforcement. The probe discards the body, so 200 alone cannot identify content. | Cloudflare Zero Trust unknown; curl manual unknown | REASONED |
| verify-policy: Inspect loopback binding and effective inbound policy, including existing allows and container NAT; permitted sources depend on topology. | Cloudflare Zero Trust unknown | REASONED |
| verify-origin: From another host, probe the actual origin port 3000: remote refusal/timeout is expected; any HTTP reply exposes bypass, resolver/local errors are inconclusive. | Cloudflare Zero Trust unknown | REASONED |
| verify-aop: Trust the origin server CA when probing 443 directly: missing-client-certificate refusal proves AOP; firewall drops and app 401/403 prove different layers. | Cloudflare Zero Trust unknown | REASONED |
| verify-http: Separately confirm the no-tunnel origin's port 80 never serves the app. | Cloudflare Zero Trust unknown | REASONED |
| token-file: cloudflared 2025.4.0 or later supports tunnel run --token-file /absolute/path/to/token; restrict the file to the service account with mode 0600 on Linux/macOS or a restricted Windows ACL. | cloudflared token-file minimum 2025.4.0; Cloudflare Zero Trust unknown | REASONED |
| token-install-argv: Avoid cloudflared service install &lt;TOKEN&gt;: the token is exposed on the installer argv, even though the cited 2026.9.3 installer runs the service with --token-file. | cloudflared service installer 2026.9.3; cloudflared token-file minimum 2025.4.0 | REASONED |
<!-- version-basis:end -->

This is the recommended path when the host cannot or should not accept inbound connections: home labs, NATed machines, cloud VMs you want to keep closed, and any project without its own TLS setup. `cloudflared` opens an outbound-only tunnel to Cloudflare's edge, the edge serves your hostname over HTTPS with a Cloudflare-managed certificate, and Cloudflare Access places authentication (SSO or emailed one-time PIN) in front of the app without any application changes. No inbound firewall ports are opened at all.

## 1. Prerequisites

- A domain added to Cloudflare (the free plan is sufficient), with Cloudflare as its DNS.
- A Zero Trust organization on the account. At the time of writing the free tier covers up to 50 users; verify current limits at https://www.cloudflare.com/plans/zero-trust-services/
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

For APIs and machine clients, create a **service token** in the Zero Trust dashboard (Access service authentication section), add a **Service Auth** policy to the application, and send the token with each request:

```bash
(
  # Use Bash in a fresh, trusted shell. Replace the URL and client ID inside
  # the quotes; paste only the secret at the hidden prompt, never into the command.
  # The prompted secret reaches curl on stdin, outside argv and shell history;
  # it remains accessible to the account owner or root.
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
- Do not use quick tunnels (`cloudflared tunnel --url http://localhost:3000`, the random `trycloudflare.com` URLs) for anything real: they are unauthenticated and intended for short-lived testing.
- If the origin must sit on a different machine from `cloudflared`, TLS on that hop (`service: https://...`; see [self-signed.md](self-signed.md)) only encrypts it, it does not restrict who may connect, so the origin machine must also accept connections *only* from the `cloudflared` host (a host or cloud firewall source-restriction), or the app is reachable directly with no Access, just as in the next bullet. Better, run `cloudflared` on the origin machine itself and bind the app to loopback there. For a self-signed origin certificate, configure its issuing CA with `originRequest.caPool`, keeping certificate and hostname verification, rather than `originRequest.noTLSVerify: true`, which discards the server authentication the TLS hop was meant to add.
- Related but distinct: for a directly-exposed origin behind Cloudflare's proxy (no tunnel), Full (strict) with a Cloudflare **origin certificate** encrypts and authenticates the origin *to* Cloudflare, but it does not stop a client that discovers the origin IP (through DNS history, certificate-transparency scans, or a grey-clouded or MX record on the same host) from connecting straight to it and bypassing Access. Lock the origin down with **Authenticated Origin Pulls** and a firewall: enabling AOP in the dashboard alone enforces nothing at the origin, so the origin must require the client certificate (for nginx, `ssl_verify_client on` with `ssl_client_certificate` set to the CA the presented client certificate chains to). With **global** AOP that CA is Cloudflare's shared origin-pull CA, which only proves the request came from Cloudflare's network (any account); prefer a **zone-level** certificate you upload, trust that certificate's issuing CA at the origin and remove the shared-CA trust, so only your zone is accepted. Because AOP is mutual TLS it cannot authenticate plaintext HTTP, so close origin port 80 (or make it redirect only to the canonical HTTPS host, never serve the app) and restrict inbound 443 to Cloudflare's published IP ranges (https://www.cloudflare.com/ips/), per [cloud-firewalls.md](cloud-firewalls.md). Origin certificates are trusted only by Cloudflare's edge, never by browsers directly.

## 6. Verify

- A private-browsing visit to `https://app.example.com` shows the Access login page, not the app.
- `curl -q -sI https://app.example.com/` returns a 302 whose `location` is your team's `*.cloudflareaccess.com` login, never a 200 or your application's own content.
- With a service token, a GET returns your application content, not the Access login. Use a route known to serve your application's content with HTTP 200. Expect `http=200 location=`; an Access login redirect, denial or transport error is not a pass. Compare with the anonymous check above: an exposed app serves the route anonymously too, so token success alone does not prove Access is enforced.

Use Bash in a fresh, trusted shell and replace the URL and client ID inside the quotes. Paste only the secret at the hidden prompt, never into the command. The block discards the body and prints only the status and redirect destination; a 200 alone cannot identify the content. The secret stays in an unexported subshell variable and reaches curl on stdin, which does not hide it from the account owner or root.

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

- `ss -tlnp` shows the app on `127.0.0.1` only for a same-host tunnel. Do not settle for "no inbound rule added": confirm the port's effective inbound policy, since a default-accept policy, a pre-existing broad allow, or a container publishing through its own NAT can leave it open. The policy differs by topology: a same-host tunnel app is on loopback, a remote tunnel origin accepts only the `cloudflared` host, and a no-tunnel HTTPS origin accepts only Cloudflare's IP ranges (plus AOP).
- The load-bearing check: from another host, confirm the origin is not reachable directly on the app's own port (`3000` in this example; substitute yours). For a tunnel there is no public inbound, so this must refuse or time out.

REASONED: following block; direct-origin isolation follows the cited Cloudflare tunnel and origin-firewall documentation. This read-only review cannot provision a Cloudflare origin and external probe host; no live outcome is recorded. Expected refusal, exposure and inconclusive outcomes are stated below.

```bash
(                                             # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_ORIGIN_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_ORIGIN_IP*|"") echo "substitute your origin's public IP on the set -- line above; not probing" ;;
    *) curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
         -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:3000/" ;;   # the app's own port
  esac
)
```

Read err, not the number: for a tunnel a refusal or timeout naming your own address is the pass, and any HTTP code means the app answered directly and Access is bypassed. A resolver failure, or a timeout that did not come from your address, is inconclusive, never a pass.

- The no-tunnel AOP origin needs a different check, because the direct request goes to the origin's HTTPS port and its Origin CA certificate is not trusted by an ordinary client. Trust the origin's server CA so a server-certificate error does not mask the result, and read the response: `curl -q -s --cacert REPLACE_WITH_ORIGIN_SERVER_CA --resolve app.example.com:443:REPLACE_WITH_YOUR_ORIGIN_IP -w 'http=%{http_code} err=%{errormsg}\n' https://app.example.com/`. AOP is working when the origin refuses the missing client certificate (a TLS alert, or nginx's `400 No required SSL certificate was sent`); a failure is your application's content coming back. Distinguish the layers, since all three withhold content for different reasons: a firewall drop is network isolation, a client-certificate refusal is AOP, and a `401`/`403` is the app's own authorization. Confirm separately that port 80 does not serve the app.

## Sources (checked September 2026)

- Cloudflare Zero Trust documentation: https://developers.cloudflare.com/cloudflare-one/
- Create a remotely-managed tunnel: https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/get-started/create-remote-tunnel/
- cloudflared releases: https://github.com/cloudflare/cloudflared
- Authenticated Origin Pulls (the origin must validate the client certificate; shared vs zone-level cert): https://developers.cloudflare.com/ssl/origin-configuration/authenticated-origin-pull/
- Cloudflare IP ranges (origin firewall allowlist): https://www.cloudflare.com/ips/
- cloudflared as a Linux service (pass --config under sudo): https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/local-management/as-a-service/linux/
- Cloudflare Access One-time PIN (login methods coexist with an IdP): https://developers.cloudflare.com/cloudflare-one/integrations/identity-providers/one-time-pin/
- Cloudflare Access service tokens (request headers and Service Auth policy): https://developers.cloudflare.com/cloudflare-one/access-controls/service-credentials/service-tokens/
- curl manual (stdin headers, output and redirect reporting): https://curl.se/docs/manpage.html
- cloudflared run parameters (`--token-file`, requires 2025.4.0 or later): https://developers.cloudflare.com/tunnel/reference/run-parameters/#token-file
- Tunnel tokens (retrieving the token from the dashboard installation command without running it): https://developers.cloudflare.com/tunnel/reference/tunnel-tokens/
- cloudflared 2026.9.3 service installer (runs `tunnel run --token-file`): https://github.com/cloudflare/cloudflared/blob/2026.9.3/cmd/cloudflared/common_service.go
