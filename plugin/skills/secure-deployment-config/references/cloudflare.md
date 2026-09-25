# Cloudflare Tunnel and Zero Trust Access

This is the recommended path when the host cannot or should not accept inbound connections: home labs, NATed machines, cloud VMs you want to keep closed, and any project without its own TLS setup. `cloudflared` opens an outbound-only tunnel to Cloudflare's edge, the edge serves your hostname over HTTPS with a Cloudflare-managed certificate, and Cloudflare Access places authentication (SSO or emailed one-time PIN) in front of the app without any application changes. No inbound firewall ports are opened at all.

## 1. Prerequisites

- A domain added to Cloudflare (the free plan is sufficient), with Cloudflare as its DNS.
- A Zero Trust organization on the account. At the time of writing the free tier covers up to 50 users; verify current limits at https://www.cloudflare.com/plans/zero-trust-services/
- `cloudflared` installed on the host that can reach the service (packages for Linux, macOS, and Windows: https://github.com/cloudflare/cloudflared).

## 2. Create the tunnel (dashboard-managed, recommended)

Per the Cloudflare docs as of June 2026 (menu locations change; the sources below are authoritative):

1. In the Cloudflare dashboard go to **Networking > Tunnels** and create a tunnel (connector type `cloudflared`).
2. Copy the installation command the dashboard shows for your OS and run it on the host. It embeds a tunnel token and installs `cloudflared` as a service (`cloudflared service install <TOKEN>` on Linux).
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
  # Feed the service-token headers to curl on stdin (curl --header @-), never in
  # argv: the Client-Secret in -H is readable in ps / /proc/<pid>/cmdline.
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_CLIENT_ID' 'REPLACE_WITH_CLIENT_SECRET'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the Client-Id on the set -- line above; not probing"; exit ;; esac
  case "$2" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the Client-Secret on the set -- line above; not probing"; exit ;; esac
  printf 'CF-Access-Client-Id: %s\nCF-Access-Client-Secret: %s\n' "$1" "$2" | curl -q -H @- https://app.example.com/api
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
- With a service token, a GET returns your application content, not the login: `curl -q -s -H 'CF-Access-Client-Id: REPLACE_WITH_CLIENT_ID' -H 'CF-Access-Client-Secret: REPLACE_WITH_CLIENT_SECRET' https://app.example.com/`.
- `ss -tlnp` shows the app on `127.0.0.1` only for a same-host tunnel. Do not settle for "no inbound rule added": confirm the port's effective inbound policy, since a default-accept policy, a pre-existing broad allow, or a container publishing through its own NAT can leave it open. The policy differs by topology: a same-host tunnel app is on loopback, a remote tunnel origin accepts only the `cloudflared` host, and a no-tunnel HTTPS origin accepts only Cloudflare's IP ranges (plus AOP).
- The load-bearing check: from another host, confirm the origin is not reachable directly on the app's own port (`3000` in this example; substitute yours). For a tunnel there is no public inbound, so this must refuse or time out.

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
