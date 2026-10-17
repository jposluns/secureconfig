---
version_basis: {
  "schema": 1,
  "checked": "2026-10-17",
  "documentation_checked": "2026-09",
  "body_sha256": "6786216fb9350d025fc8d689cfac0f3e0ac5723a0b2aef9aefc11995aa871562",
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
    },
    "curl-opts": {
      "name": "curl command-line options",
      "basis": "curl-8_23_0",
      "sources": {
        "s528fcc47043d": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/cacert.md#L19-L24",
        "sce3838e7adf1": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/connect-to.md#L17-L22",
        "s508454c45cf1": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/noproxy.md#L18-L23",
        "s511177850f9e": "https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/globoff.md#L17-L22"
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
        "s78f4d7c15ff5": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/ssl/origin-configuration/authenticated-origin-pull/index.mdx#L16-L26"
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
    "jwt": {"text": "Validate Cf-Access-Jwt-Assertion signature, issuer and application audience; origin reachability, SSRF and another route can bypass the front door.", "components": ["cf", "cf-docs"], "sources": ["cf:s536e61cfd1d0", "cf-docs:sc4628a1320d3"], "status": "REASONED"},
    "route-coverage": {"text": "Every added tunnel hostname/path needs an Access application and policy, including coverage by a wildcard application.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0"], "status": "REASONED"},
    "quick": {"text": "Quick trycloudflare.com tunnels are unauthenticated and intended only for short-lived tests.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0", "cf:s58da5534d71a"], "status": "REASONED"},
    "remote-origin": {"text": "A remote origin needs HTTPS and a firewall allowing only the cloudflared host; TLS alone does not restrict callers.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0", "cf:s160a7accb558"], "status": "REASONED"},
    "origin-ca": {"text": "Use originRequest.caPool for a self-signed origin; noTLSVerify discards server authentication.", "components": ["cf", "cf-docs"], "sources": ["cf:s536e61cfd1d0", "cf-docs:sa102d58fd878"], "status": "REASONED"},
    "full-strict": {"text": "Full (strict) with an Origin CA certificate authenticates the origin to Cloudflare, not callers; browsers do not trust that certificate directly.", "components": ["cf", "cf-docs"], "sources": ["cf:sbe2ecd154061", "cf-docs:sf8ae935ddb55", "cf-docs:s4a635dc9bd32"], "status": "REASONED"},
    "aop": {"text": "AOP requires origin-side client-certificate enforcement; nginx uses ssl_verify_client on and ssl_client_certificate.", "components": ["cf"], "sources": ["cf:sbe2ecd154061"], "status": "REASONED"},
    "aop-zone": {"text": "Global AOP proves only Cloudflare network membership; prefer a zone certificate and its issuing CA, removing shared-CA trust.", "components": ["cf"], "sources": ["cf:sbe2ecd154061"], "status": "REASONED"},
    "origin-ports": {"text": "For a no-tunnel origin, restrict 443 to Cloudflare IP ranges and close 80 or redirect only to the canonical HTTPS host without app content; the listed Sources do not prescribe a redirect code, and mTLS cannot authenticate plaintext HTTP.", "components": ["cf"], "sources": ["cf:sbe2ecd154061", "cf:s9f78b2ad819b"], "status": "REASONED"},
    "verify-login": {"text": "Private browsing must show Access login; anonymous HEAD must redirect to the team's cloudflareaccess.com login, never app content.", "components": ["cf"], "sources": ["cf:s536e61cfd1d0", "cf:s5bd93ae868e6"], "status": "REASONED"},
    "verify-token": {"text": "On a route known to serve application content with HTTP 200, send the hidden-prompt service token through curl --header @- and expect http=200 location=. Login redirects, denials and transport errors fail; compare anonymous denial because token success alone does not prove Access enforcement. The probe discards the body, so 200 alone cannot identify content.", "components": ["cf", "curl"], "sources": ["cf:s15ab6de85740", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-policy": {"text": "Inspect loopback binding and effective inbound policy, including existing allows and container NAT; permitted sources depend on topology.", "components": ["cf"], "sources": ["cf:s160a7accb558", "cf:sbe2ecd154061", "cf:s9f78b2ad819b"], "status": "REASONED"},
    "verify-origin": {"text": "From another host, probe the actual origin port (HTTP 3000 in the same-host example or HTTPS for a remote origin): an explicit refusal from the confirmed origin address while the allowed-vantage control (tunnel-host loopback, or the `cloudflared` host to a remote origin) returns the app's status, not 000, together with an effective inbound-policy check supports isolation; those controls do not confirm the probed public address; no reply and TLS trust or hostname errors are inconclusive (including when combined trust cannot be reproduced), and any HTTP reply from the confirmed origin address directly on the app's port exposes bypass; an HTTP reply from an unconfirmed address only shows something answers there and requires address-mapping confirmation before calling this origin exposed, never fixed (this guide's assessment of probe outcomes).", "components": ["cf", "curl", "cf-docs", "curl-opts"], "sources": ["cf:s160a7accb558", "curl:s2b2686afaf41", "cf-docs:s253af0f0386c", "curl-opts:s528fcc47043d", "curl-opts:sce3838e7adf1", "cf-docs:sa102d58fd878"], "status": "REASONED", "verify": [2, 3]},
    "verify-aop": {"text": "Trust the origin server CA when probing 443 directly: missing-client-certificate refusal proves AOP; a firewall drop is inconclusive in this probe, even if the service-token GET answers; the effective inbound policy establishes isolation, while app 401/403 shows app authorization (this guide's assessment of probe outcomes).", "components": ["cf", "cf-docs", "curl", "curl-opts"], "sources": ["cf:sbe2ecd154061", "curl:s2b2686afaf41", "cf-docs:s4a635dc9bd32", "curl-opts:s508454c45cf1", "curl-opts:s511177850f9e", "cf-docs:s78f4d7c15ff5"], "status": "REASONED"},
    "verify-http": {"text": "Probe a known app route and virtual host on no-tunnel origin port 80 from outside: either an explicit refusal from the confirmed origin address or only a redirect from that confirmed address to the canonical HTTPS host without app content supports the fixed state when the service-token GET on that route answers with its success status; that GET does not confirm the probed public address; app content from that confirmed address over HTTP shows exposure and no reply is inconclusive. The listed Sources do not prescribe a redirect code (this guide's assessment of probe outcomes).", "components": ["cf", "curl"], "sources": ["cf:sbe2ecd154061", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [4]},
    "token-file": {"text": "cloudflared 2025.4.0 or later supports tunnel run --token-file /absolute/path/to/token; restrict the file to the service account with mode 0600 on Linux/macOS or a restricted Windows ACL.", "components": ["token-file", "cf"], "sources": ["token-file:sde222f01d112", "cf:sd043afad3d8a"], "status": "REASONED"},
    "token-install-argv": {"text": "Avoid cloudflared service install <TOKEN>: the token is exposed on the installer argv, even though the cited 2026.9.3 installer runs the service with --token-file.", "components": ["installer", "token-file"], "sources": ["installer:sbe50314c5b92", "token-file:sde222f01d112"], "status": "REASONED"}
  }
}
---
# Cloudflare Tunnel and Zero Trust Access

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-17; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

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
| jwt: Validate Cf-Access-Jwt-Assertion signature, issuer and application audience; origin reachability, SSRF and another route can bypass the front door. | Cloudflare Zero Trust unknown; Cloudflare documentation c896795b8e8bab68d05ae78d64c9cbcda1fdb104 | REASONED |
| route-coverage: Every added tunnel hostname/path needs an Access application and policy, including coverage by a wildcard application. | Cloudflare Zero Trust unknown | REASONED |
| quick: Quick trycloudflare.com tunnels are unauthenticated and intended only for short-lived tests. | Cloudflare Zero Trust unknown | REASONED |
| remote-origin: A remote origin needs HTTPS and a firewall allowing only the cloudflared host; TLS alone does not restrict callers. | Cloudflare Zero Trust unknown | REASONED |
| origin-ca: Use originRequest.caPool for a self-signed origin; noTLSVerify discards server authentication. | Cloudflare Zero Trust unknown; Cloudflare documentation c896795b8e8bab68d05ae78d64c9cbcda1fdb104 | REASONED |
| full-strict: Full (strict) with an Origin CA certificate authenticates the origin to Cloudflare, not callers; browsers do not trust that certificate directly. | Cloudflare Zero Trust unknown; Cloudflare documentation c896795b8e8bab68d05ae78d64c9cbcda1fdb104 | REASONED |
| aop: AOP requires origin-side client-certificate enforcement; nginx uses ssl_verify_client on and ssl_client_certificate. | Cloudflare Zero Trust unknown | REASONED |
| aop-zone: Global AOP proves only Cloudflare network membership; prefer a zone certificate and its issuing CA, removing shared-CA trust. | Cloudflare Zero Trust unknown | REASONED |
| origin-ports: For a no-tunnel origin, restrict 443 to Cloudflare IP ranges and close 80 or redirect only to the canonical HTTPS host without app content; the listed Sources do not prescribe a redirect code, and mTLS cannot authenticate plaintext HTTP. | Cloudflare Zero Trust unknown | REASONED |
| verify-login: Private browsing must show Access login; anonymous HEAD must redirect to the team's cloudflareaccess.com login, never app content. | Cloudflare Zero Trust unknown | REASONED |
| verify-token: On a route known to serve application content with HTTP 200, send the hidden-prompt service token through curl --header @- and expect http=200 location=. Login redirects, denials and transport errors fail; compare anonymous denial because token success alone does not prove Access enforcement. The probe discards the body, so 200 alone cannot identify content. | Cloudflare Zero Trust unknown; curl manual unknown | REASONED |
| verify-policy: Inspect loopback binding and effective inbound policy, including existing allows and container NAT; permitted sources depend on topology. | Cloudflare Zero Trust unknown | REASONED |
| verify-origin: From another host, probe the actual origin port (HTTP 3000 in the same-host example or HTTPS for a remote origin): an explicit refusal from the confirmed origin address while the allowed-vantage control (tunnel-host loopback, or the &#96;cloudflared&#96; host to a remote origin) returns the app's status, not 000, together with an effective inbound-policy check supports isolation; those controls do not confirm the probed public address; no reply and TLS trust or hostname errors are inconclusive (including when combined trust cannot be reproduced), and any HTTP reply from the confirmed origin address directly on the app's port exposes bypass; an HTTP reply from an unconfirmed address only shows something answers there and requires address-mapping confirmation before calling this origin exposed, never fixed (this guide's assessment of probe outcomes). | Cloudflare Zero Trust unknown; curl manual unknown; Cloudflare documentation c896795b8e8bab68d05ae78d64c9cbcda1fdb104; curl command-line options curl-8_23_0 | REASONED |
| verify-aop: Trust the origin server CA when probing 443 directly: missing-client-certificate refusal proves AOP; a firewall drop is inconclusive in this probe, even if the service-token GET answers; the effective inbound policy establishes isolation, while app 401/403 shows app authorization (this guide's assessment of probe outcomes). | Cloudflare Zero Trust unknown; Cloudflare documentation c896795b8e8bab68d05ae78d64c9cbcda1fdb104; curl manual unknown; curl command-line options curl-8_23_0 | REASONED |
| verify-http: Probe a known app route and virtual host on no-tunnel origin port 80 from outside: either an explicit refusal from the confirmed origin address or only a redirect from that confirmed address to the canonical HTTPS host without app content supports the fixed state when the service-token GET on that route answers with its success status; that GET does not confirm the probed public address; app content from that confirmed address over HTTP shows exposure and no reply is inconclusive. The listed Sources do not prescribe a redirect code (this guide's assessment of probe outcomes). | Cloudflare Zero Trust unknown; curl manual unknown | REASONED |
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
- Do not use quick tunnels (`cloudflared tunnel --url http://localhost:3000`, the random `trycloudflare.com` URLs) for anything real: they are unauthenticated and intended for short-lived testing.
- If the origin must sit on a different machine from `cloudflared`, TLS on that hop (`service: https://...`; see [self-signed.md](self-signed.md)) only encrypts it, it does not restrict who may connect, so the origin machine must also accept connections *only* from the `cloudflared` host (a host or cloud firewall source-restriction), or the app is reachable directly with no Access, just as in the next bullet. Better, run `cloudflared` on the origin machine itself and bind the app to loopback there. For a self-signed origin certificate, configure its issuing CA with `originRequest.caPool`, keeping certificate and hostname verification, rather than `originRequest.noTLSVerify: true`, which discards the server authentication the TLS hop was meant to add.
- Related but distinct: for a directly-exposed origin behind Cloudflare's proxy (no tunnel), Full (strict) with a Cloudflare **origin certificate** encrypts and authenticates the origin *to* Cloudflare, but it does not stop a client that discovers the origin IP (through DNS history, certificate-transparency scans, or a grey-clouded or MX record on the same host) from connecting straight to it and bypassing Access. Lock the origin down with **Authenticated Origin Pulls** and a firewall: enabling AOP in the dashboard alone enforces nothing at the origin, so the origin must require the client certificate (for nginx, `ssl_verify_client on` with `ssl_client_certificate` set to the CA the presented client certificate chains to). With **global** AOP that CA is Cloudflare's shared origin-pull CA, which only proves the request came from Cloudflare's network (any account); prefer a **zone-level** certificate you upload, trust that certificate's issuing CA at the origin and remove the shared-CA trust, so only your zone is accepted. Because AOP is mutual TLS it cannot authenticate plaintext HTTP, so close origin port 80 (or make it redirect only to the canonical HTTPS host, never serve the app) and restrict inbound 443 to Cloudflare's published IP ranges (https://www.cloudflare.com/ips/), per [cloud-firewalls.md](cloud-firewalls.md). Origin certificates are trusted only by Cloudflare's edge, never by browsers directly.

## 6. Verify

- REASONED: private-browsing Access check; local marking review (October 2026, Bash 5.3.9) did not run a browser comparison. A live Cloudflare origin stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; a Cloudflare account and Access application on a proxied hostname were not available to this marking review. For the visit to https://app.example.com, an exposed route is expected to serve app content anonymously; a fixed route is expected to show Access login, then serve the app after an allowed sign-in, per the guide's cited Cloudflare Zero Trust documentation and Cloudflare Access One-time PIN (login methods coexist with an IdP). A private-browsing visit to `https://app.example.com` shows the Access login page, not the app.
- REASONED: anonymous HEAD check; local marking review (October 2026, Bash 5.3.9) ran the stated curl command against a curl stub, which printed 'stub curl args=-q -sI https://app.example.com/' (exit 0), not an HTTP response. A live Cloudflare origin stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; a Cloudflare account and Access application on a proxied hostname were not available to this marking review. An exposed route is expected to return the application's own status and headers, potentially HTTP 200; a fixed anonymous route is expected to return 302 with a team cloudflareaccess.com login location, while an allowed session reaches the app, per the guide's cited Cloudflare Zero Trust documentation and Cloudflare Access One-time PIN (login methods coexist with an IdP). HEAD prints status and headers, not content. `curl -q -sI https://app.example.com/` returns a 302 whose `location` is your team's `*.cloudflareaccess.com` login, never a 200 or your application's own content.
- REASONED: service-token GET and anonymous comparison; local marking review (October 2026, Bash 5.3.9) passed the following block through bash -n and ShellCheck 0.11.0 with no output. Fourteen Bash fixtures with a curl stub printed: placeholder and empty URL, 'substitute your own application URL inside the quotes; not probing' (each exit 2); wrong sentinel, 'paste the whole block, including its set -- line; not probing' (exit 2); one and three values, 'the set -- line needs a URL and client ID; not probing' (each exit 2); HTTP URL, 'use an https:// URL; not probing' (exit 2); placeholder ID, 'supply the client ID without control characters; not probing' (exit 2); EOF secret input, 'secret input failed; not probing' (exit 2); empty and placeholder secrets, 'supply the secret without control characters; not probing' (each exit 2); readonly HDR, 'cannot clear HDR in this shell; not probing' (exit 2); readonly IFS, 'a readonly IFS is set in this shell; not probing' (exit 2); valid input, 'stub curl' (exit 0); and curl stub exit 7, 'stub curl' (block exit 2). No HTTP status was observed. A live Cloudflare origin stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; a provisioned Cloudflare account, Access application and service token were not available to this marking review. On a route known to return application HTTP 200, exposed anonymous and token requests are expected to reach the app; fixed anonymous requests are expected to show Access login or denial, while the valid token is expected to yield http=200 location= on that route, per the guide's cited Cloudflare Access service tokens (request headers and Service Auth policy) and curl manual (stdin headers, output, redirect reporting and write-out variables). The block discards the body, so the printed status cannot identify content. With a service token, a GET returns your application content, not the Access login. Use a route known to serve your application's content with HTTP 200. Expect `http=200 location=`; an Access login redirect, denial or transport error is not a pass. Compare with the anonymous check above: an exposed app serves the route anonymously too, so token success alone does not prove Access is enforced.

REASONED: the usage and secret-handling notes for the service-token block below, per the guide's cited Cloudflare Access service tokens and curl manual entries and the block's own text, with the paste-alone warning per CONTRIBUTING rule 7's `read` exception. No Cloudflare account, Access application or service token is available, so no status or redirect destination was observed. During marking review (October 2026) the block passed bash -n under bash 5.3.9 and ShellCheck 0.11.0 without diagnostics. In a scratch-local review, the block ran from a file with a stub curl, no network and a pseudo-terminal: unchanged placeholders printed 'substitute your own application URL inside the quotes; not probing' (exit 2); substituted dummy inputs printed 'stub curl' (exit 0); an empty secret printed 'supply the secret without control characters; not probing' (exit 2); readonly HDR printed 'cannot clear HDR in this shell; not probing' (exit 2); and readonly IFS printed 'a readonly IFS is set in this shell; not probing' (exit 2). The stub output is not a Cloudflare response; the expected live comparison remains anonymous denial or Access login versus application content with a valid service token. Use Bash in a fresh, trusted shell and replace the URL and client ID inside the quotes. Paste the secret alone at the hidden prompt, never into the command: a multi-line paste leaves every line after the first for your shell to run. The block discards the body and prints only the status and redirect destination; a 200 alone cannot identify the content. The secret stays in an unexported subshell variable and reaches curl on stdin, which keeps it out of argv and shell history but does not hide it from `set -x` tracing (the block turns tracing off) or the account owner or root.

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

- REASONED: binding and effective policy for each topology; local marking review (October 2026, Bash 5.3.9) ran ss -tlnp with an ss stub, which printed 'stub ss args=-tlnp' (exit 0), not host socket state. A live origin stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; no deployed origin with a firewall and container-publication inventory, remote cloudflared host, AOP client certificate or external probe host was available to this marking review. Exposed same-host binding is expected to show a wildcard (0.0.0.0, [::] or *) or non-loopback address and answer directly, while fixed binding is expected to show 127.0.0.1 and answer only locally. Exposed remote-origin policy is expected to admit callers besides the cloudflared host; fixed policy is expected to admit that host and deny or filter others. Exposed no-tunnel 443 is expected to admit non-Cloudflare callers or lack enforced client certificates; fixed policy is expected to admit Cloudflare IP ranges with AOP and deny or filter others, per the guide's cited Create a remotely-managed tunnel, Authenticated Origin Pulls (the origin must validate the client certificate; shared vs zone-level cert), and Cloudflare IP ranges (origin firewall allowlist). `ss -tlnp` shows the app on `127.0.0.1` only for a same-host tunnel. Do not settle for "no inbound rule added": confirm the port's effective inbound policy, since a default-accept policy, a pre-existing broad allow, or a container publishing through its own NAT can leave it open. The policy differs by topology: a same-host tunnel app is on loopback, a remote tunnel origin accepts only the `cloudflared` host, and a no-tunnel HTTPS origin accepts only Cloudflare's IP ranges (plus AOP).
- REASONED: external direct-origin probe on port 3000; local marking review (October 2026, Bash 5.3.9) passed the following block through bash -n and ShellCheck 0.11.0 without output. With a curl stub, placeholder and empty values each printed "substitute your origin's public IP on the set -- line above; not probing" (exit 2); zero and two values each printed "the set -- line needs exactly 1 value; not probing" (exit 2); a wrong marker printed "paste the whole block, including its set -- line; not probing" (exit 2); a valid fixture printed 'stub curl args=-q -g -s -o /dev/null --noproxy * --connect-timeout 5 --max-time 20 -w http=%{http_code} exit=%{exitcode} err=%{errormsg}\n http://203.0.113.10:3000/' (exit 0). A live origin stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; no external probe host, deployed origin or allowed-vantage tunnel host control was available to this marking review. On 2026-10-17 the unchanged HTTP block passed `bash -n` and ShellCheck with `-s bash`; a curl stub produced HTTP 200 (exit 0), explicit refusal (exit 7) and timeout (exit 28) outputs, while its placeholder guard exited 2. Exposed origin is expected to give an HTTP reply directly; the fixed outcome is an explicit refusal from that address while an allowed-vantage control answers; no reply is inconclusive, per the guide's cited Create a remotely-managed tunnel. From another host, confirm the origin is not reachable directly on the app's own port (3000 over HTTP in this same-host example; substitute yours). For a remote origin with `service: https://...`, use the HTTPS block below on that service URL's port. As this guide's assessment, a refusal supports isolation only after independently confirming that the public address being probed belongs to this origin; neither allowed-vantage control establishes that address mapping. On the tunnel host, the allowed-vantage control `curl -q -g -s -o /dev/null --noproxy '*' -w '%{http_code}\n' http://127.0.0.1:3000/` must return the app's status (not 000); for a remote origin, run the matching HTTPS control from the `cloudflared` host and require the app's status (not 000): `curl -q -g -s -o /dev/null --noproxy '*' -w '%{http_code}\n' 'REPLACE_WITH_SERVICE_URL'` with system trust, or `curl -q -g -s -o /dev/null --noproxy '*' --cacert 'REPLACE_WITH_COMBINED_CA_BUNDLE' -w '%{http_code}\n' 'REPLACE_WITH_SERVICE_URL'` when `caPool` is set. The combined bundle must contain the default trusted roots used by `cloudflared` and the configured `caPool` certificates. When the effective certificate name differs from the service URL host, use `curl -q -g -s -o /dev/null --noproxy '*' --cacert 'REPLACE_WITH_COMBINED_CA_BUNDLE' --connect-to 'REPLACE_WITH_CERT_HOSTNAME:REPLACE_WITH_HTTPS_PORT:REPLACE_WITH_SERVICE_HOST:REPLACE_WITH_HTTPS_PORT' -w '%{http_code}\n' 'https://REPLACE_WITH_CERT_HOSTNAME:REPLACE_WITH_HTTPS_PORT/'`; omit `--cacert` in this form only when system trust reproduces tunnel trust. Apply the `matchSNItoHost` override described below when choosing that name. As this guide's assessment, this control shows origin availability, not that the public address in the external probe belongs to it.

REASONED: following block; direct-origin isolation follows the cited Create a remotely-managed tunnel. This read-only review cannot provision a Cloudflare origin and external probe host; no live outcome is recorded. Expected refusal, exposure and inconclusive outcomes are stated below.

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

REASONED: following block; remote-origin HTTPS direct probe; on 2026-10-17 this block passed `bash -n` and ShellCheck with `-s bash`; a curl stub exercised the placeholder and invalid-port guards (exit 2), ports 0 and above 65535 (exit 2), ports 443 and 65535 (exit 0), IPv6 brackets (exit 0), and HTTP 200 (exit 0), explicit refusal (exit 7), timeout (exit 28) and TLS error (exit 60) under both SYSTEM_TRUST and combined-CA branches; no live response was observed. No live remote origin or external probe host was available. Use the `https://` service URL port and its certificate hostname. Set the third value to `SYSTEM_TRUST` when `originRequest.caPool` is unset and the issuing CA is trusted by the probe host; otherwise supply a PEM bundle containing both the default trusted roots used by `cloudflared` and the certificates in `originRequest.caPool`. Build that bundle from the relevant default root store and the configured `caPool` PEM; a `caPool` file alone does not reproduce the combined trust pool. If the effective trust roots cannot be reproduced, treat a TLS trust failure as inconclusive. Use the service URL host as the certificate hostname unless `originServerName` sets a different one. When `matchSNItoHost` is true, it overrides `originServerName`: use the request `Host` value sent to the origin, or the configured HTTP Host Header value, as the effective SNI/certificate name for that request. If this value varies or cannot be established, the hostname probe is inconclusive. For an IPv6 origin address, put brackets around the address inside the first quoted value for `--connect-to`. The pinned Cloudflare origin parameters define that name, the SNI override and the additive CA pool; the pinned curl `--cacert` and `--connect-to` entries define the trust file and destination override. As this guide's assessment, a TLS trust or hostname error is inconclusive, especially when the combined trust pool cannot be reproduced; after confirming the address mapping, an HTTP reply directly on the origin port shows exposure; a refusal supports isolation only with the effective inbound policy check and a successful allowed-vantage control. The allowed-vantage control above shows that the origin answers but does not confirm the probed public address.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_ORIGIN_IP' 'REPLACE_WITH_CERT_HOSTNAME' 'REPLACE_WITH_ORIGIN_SERVER_CA_OR_SYSTEM_TRUST' 'REPLACE_WITH_ORIGIN_HTTPS_PORT'  # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block, including its set -- line; not probing'; exit 2; }
  shift
  [ "$#" -eq 4 ] || { echo 'the set -- line needs an origin IP, certificate hostname, CA choice and port; not probing'; exit 2; }
  case "$1" in ''|*REPLACE_WITH_*|-*|*[[:space:]]*) echo 'substitute your origin public IP; not probing'; exit 2 ;; esac
  case "$2" in ''|*REPLACE_WITH_*|-*|*[[:space:]]*) echo 'substitute the certificate hostname; not probing'; exit 2 ;; esac
  case "$3" in ''|*REPLACE_WITH_*|-*|*[[:space:]]*) echo 'supply SYSTEM_TRUST or the origin CA PEM path; not probing'; exit 2 ;; esac
  case "$4" in ''|*[!0123456789]*) echo 'supply an HTTPS port from 1 to 65535; not probing'; exit 2 ;; esac
  if [ "${#4}" -gt 5 ] || [ "$4" -lt 1 ] || [ "$4" -gt 65535 ]; then
    echo 'supply an HTTPS port from 1 to 65535; not probing'; exit 2
  fi
  if [ "$3" = SYSTEM_TRUST ]; then
    curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
      -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' --connect-to "$2:$4:$1:$4" "https://$2:$4/"
  else
    curl -q -g -s -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
      --cacert "$3" -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
      --connect-to "$2:$4:$1:$4" "https://$2:$4/"
  fi
)
```

REASONED: external direct-origin outcome; local marking review (October 2026, Bash 5.3.9) used the curl stub above, not a live origin. A live origin stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; an external probe host, deployed origin and tunnel-host control were unavailable. Read err, not the number: `err` text reporting a refused connection to your confirmed origin address supports the fixed state only with the effective inbound-policy check and when the tunnel-host loopback control `curl -q -g -s -o /dev/null --noproxy '*' -w '%{http_code}\n' http://127.0.0.1:3000/` returns the app's status (not 000), or, for a remote origin, one of the matching HTTPS controls above from the `cloudflared` host returns the app's status (not 000), using the combined CA bundle when `originRequest.caPool` is set; as this guide's assessment, any HTTP status (http= not 000) from that confirmed origin address means something answered directly on the app's port and Access is bypassed. An HTTP reply from an unconfirmed address means something answers there; confirm the mapping before calling it this origin's exposure, and never treat that reply as fixed. A timeout, no reply, resolver failure, TLS trust or hostname failure, or error whose destination is uncertain is inconclusive. As this guide's assessment, neither allowed-vantage control proves that the probed public address belongs to this origin; confirm it independently before calling a refusal fixed. Use curl 7.75.0 or newer for `%{exitcode}` and `%{errormsg}` write-out. These expectations follow the cited Create a remotely-managed tunnel; the cited curl manual (stdin headers, output, redirect reporting and write-out variables) explains the printed transfer status and error.

- REASONED: no-tunnel AOP origin and its port-80 sentence; local marking review (October 2026, Bash 5.3.9) reviewed the cited Authenticated Origin Pulls (the origin must validate the client certificate; shared vs zone-level cert) and Cloudflare IP ranges (origin firewall allowlist) guidance and ran the port-80 block below through bash -n, ShellCheck 0.11.0 and curl-stub guard fixtures, not against a live origin. A live origin stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; an external probe host, deployed no-tunnel origin, Origin CA and allowed-vantage service-token control were unavailable. The no-tunnel AOP origin needs a different check, because the direct request goes to the origin's HTTPS port and its Origin CA certificate is not trusted by an ordinary client. Trust the origin's server CA so a server-certificate error does not mask the result, and read the response: `curl -q -g -s --noproxy '*' --cacert REPLACE_WITH_ORIGIN_SERVER_CA --resolve app.example.com:443:REPLACE_WITH_YOUR_ORIGIN_IP -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' https://app.example.com/`. As this guide's assessment, AOP is working when the origin refuses the missing client certificate (a TLS alert, or nginx's `400 No required SSL certificate was sent`); a failure is your application's content coming back. Distinguish the layers, since all three withhold content for different reasons: a firewall drop is inconclusive in this probe even when the service-token GET answers; confirm isolation with the effective inbound-policy check above. As this guide's assessment, a client-certificate refusal indicates AOP, and a `401`/`403` indicates the app's own authorization. These outcome interpretations are this guide's assessment. Confirm separately that port 80 does not serve the app.

REASONED: no-tunnel port-80 policy; AOP authenticates HTTPS client certificates, so an HTTP origin route must not serve app content, per the cited Authenticated Origin Pulls (the origin must validate the client certificate; shared vs zone-level cert). Check a known app route from an external host with the following block, replacing the origin IP, app hostname and route inside the quotes. On the same route, the service-token GET in the service-token block above is the allowed-vantage control and must return its success status. As this guide's assessment, a fixed origin gives an explicit refusal or only a redirect to the canonical HTTPS host from the independently confirmed origin address (the listed Sources do not prescribe a code), without app content; either fixed outcome requires that control to answer. A timeout or no reply alone is inconclusive; app route content served over HTTP from that confirmed origin address is the exposed outcome. As this guide's assessment, the service-token GET proves that the application route answers through Cloudflare, but does not confirm that the public address probed on port 80 belongs to this origin; check that mapping independently before treating a refusal as fixed. Use curl 7.75.0 or newer for `%{exitcode}` and `%{errormsg}` write-out; the cited curl manual (stdin headers, output, redirect reporting and write-out variables) supports the printed status and error.

REASONED: following block; port-80 HTTP virtual-host route probe; local marking review (October 2026, Bash 5.3.9) passed bash -n and ShellCheck 0.11.0 without output. With a curl stub, a wrong marker printed "paste the whole block, including its set -- line; not probing" (exit 2); zero, two and four values each printed "the set -- line needs an origin IP, app hostname and app route; not probing" (exit 2); address placeholder, empty, option-like and spaced values each printed "substitute your origin's public IP on the set -- line above; not probing" (exit 2); the default placeholders and hostname placeholder, empty, option-like and spaced values each printed "substitute your app hostname on the set -- line above; not probing" (exit 2); route placeholder, empty, option-like and spaced values each printed "substitute your app route on the set -- line above; not probing" (exit 2); a route without a leading slash printed "use a route starting with /; not probing" (exit 2); a valid fixture printed 'stub curl args=-q -g -s -D - -o - --noproxy * --connect-timeout 5 --max-time 20 -w http=%{http_code} exit=%{exitcode} err=%{errormsg} location=%{redirect_url}\n --resolve app.example.com:80:203.0.113.10 http://app.example.com/health' (exit 0). A live origin stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; an external probe host, deployed no-tunnel origin, Origin CA and allowed-vantage service-token control were unavailable. On 2026-10-17 this unchanged port-80 block passed `bash -n` and ShellCheck with `-s bash`; a curl stub produced HTTP 200 (exit 0), canonical HTTPS redirect (exit 0), explicit refusal (exit 7) and timeout (exit 28) outputs, while its placeholder guard exited 2. No live refusal, redirect or app response was observed; expected outcomes are stated above, per the cited Authenticated Origin Pulls (the origin must validate the client certificate; shared vs zone-level cert) and curl manual (stdin headers, output, redirect reporting and write-out variables).

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
- curl noproxy (pinned, checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/noproxy.md#L18-L23
- curl globoff (pinned, checked October 2026): https://github.com/curl/curl/blob/curl-8_23_0/docs/cmdline-opts/globoff.md#L17-L22
- Cloudflare Authenticated Origin Pulls and tunnel incompatibility (pinned, checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/ssl/origin-configuration/authenticated-origin-pull/index.mdx#L16-L26
