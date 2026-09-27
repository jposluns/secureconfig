---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "154f92e013afc74a7aacee2575d1f0bf23b860edea5e709d36040d3def594d70",
  "components": {
    "runpod": {
      "name": "RunPod documentation",
      "basis": "unknown",
      "sources": {
        "s817198f039ee": "https://docs.runpod.io/pods/configuration/expose-ports",
        "s13c43b856d4f": "https://docs.runpod.io/pods/configuration/use-ssh"
      }
    },
    "vast": {
      "name": "Vast.ai documentation",
      "basis": "unknown",
      "sources": {
        "sc25989a1613e": "https://docs.vast.ai/guides/instances/connect/networking",
        "s0bdbda534723": "https://docs.vast.ai/guides/instances/connect/instance-portal",
        "s6e0303ef19fe": "https://docs.vast.ai/guides/instances/connect/ssh"
      }
    },
    "vast-image": {
      "name": "Vast.ai base image",
      "basis": "00064421641881c1f83ff58c55f13cbc10cbea4d",
      "sources": {
        "sf75c3c07819e": "https://github.com/vast-ai/base-image/blob/00064421641881c1f83ff58c55f13cbc10cbea4d/README.md"
      }
    },
    "lambda": {
      "name": "Lambda Public Cloud documentation",
      "basis": "unknown",
      "sources": {
        "se22064748974": "https://docs.lambda.ai/public-cloud/firewalls/",
        "sb12b4a953833": "https://docs.lambda.ai/public-cloud/on-demand/connecting-instance/"
      }
    },
    "modal": {
      "name": "Modal proxy authentication",
      "basis": "unknown",
      "sources": {
        "s7d083f819a21": "https://modal.com/docs/guide/webhook-proxy-auth"
      }
    },
    "jupyter": {
      "name": "Jupyter Server security",
      "basis": "unknown",
      "sources": {
        "sc703a8030c8f": "https://jupyter-server.readthedocs.io/en/latest/operators/security.html"
      }
    }
  },
  "claims": {
    "publication": {"text": "Raw port publication or a firewall allowance adds no listener authentication; platform proxies authenticate only the routes they actually cover.", "components": ["runpod", "vast", "lambda", "modal"], "sources": ["runpod:s817198f039ee", "vast:sc25989a1613e", "vast:s0bdbda534723", "lambda:se22064748974", "modal:s7d083f819a21"], "status": "REASONED"},
    "runpod-http": {"text": "Expose HTTP Ports publishes https://[POD_ID]-[INTERNAL_PORT].proxy.runpod.net with automatic HTTPS; anyone with the URL can reach it, so the application still needs authentication.", "components": ["runpod"], "sources": ["runpod:s817198f039ee"], "status": "REASONED"},
    "runpod-tcp": {"text": "Exposed TCP ports forward directly on a public IP without automatic TLS; secure template listeners before exposure and implement application TLS for sensitive TCP data.", "components": ["runpod"], "sources": ["runpod:s817198f039ee"], "status": "REASONED"},
    "runpod-symmetry": {"text": "TCP configuration values above 70000 request symmetrical mapping rather than naming valid ports; read the assigned mapping from the pod environment, such as RUNPOD_TCP_PORT_70000. Mapping remains public.", "components": ["runpod"], "sources": ["runpod:s817198f039ee"], "status": "REASONED"},
    "vast-ssh-port": {"text": "Vast.ai SSH launch mode opens internal port 22 by default.", "components": ["vast"], "sources": ["vast:sc25989a1613e"], "status": "REASONED"},
    "vast-jupyter-port": {"text": "Vast.ai Jupyter launch mode opens internal 8080 as well as SSH port 22 by default.", "components": ["vast"], "sources": ["vast:sc25989a1613e"], "status": "REASONED"},
    "vast-mapping": {"text": "Each open Vast.ai internal port maps to a random external port on a usually shared public IP; the networking docs describe no additional firewall step.", "components": ["vast"], "sources": ["vast:sc25989a1613e"], "status": "REASONED"},
    "vast-proxy": {"text": "Instance Portal uses local Caddy proxying when external and internal ports differ; forwarded apps can stay on loopback and PORTAL_CONFIG describes routing and presentation.", "components": ["vast"], "sources": ["vast:s0bdbda534723"], "status": "REASONED"},
    "vast-token": {"text": "Portal links carry a credential token; protect the URL, test access without it and confirm the selected route actually authenticates.", "components": ["vast"], "sources": ["vast:s0bdbda534723"], "status": "REASONED"},
    "vast-auth-controls": {"text": "The pinned base image exposes OPEN_BUTTON_TOKEN, WEB_PASSWORD and ENABLE_AUTH/AUTH_EXCLUDE; PORTAL_CONFIG is not the credential.", "components": ["vast-image", "vast"], "sources": ["vast-image:sf75c3c07819e", "vast:s0bdbda534723"], "status": "REASONED"},
    "lambda-default": {"text": "Lambda inbound firewall denies by default except ICMP and TCP 22; other listeners require explicit global/workspace rules or a per-instance ruleset attached at launch.", "components": ["lambda"], "sources": ["lambda:se22064748974"], "status": "REASONED"},
    "lambda-rule": {"text": "An allow rule admits the specified source range without authenticating callers; pair it with listener or proxy authentication. Removing an allow rule closes access.", "components": ["lambda"], "sources": ["lambda:se22064748974"], "status": "REASONED"},
    "modal-web": {"text": "Web endpoints using modal.fastapi_endpoint, the replacement for @web_endpoint, are public by default; requires_proxy_auth=True enables proxy authentication.", "components": ["modal"], "sources": ["modal:s7d083f819a21"], "status": "REASONED"},
    "modal-dedicated": {"text": "Dedicated Endpoints require proxy authentication by default; --unauthenticated makes them public.", "components": ["modal"], "sources": ["modal:s7d083f819a21"], "status": "REASONED"},
    "modal-server": {"text": "Servers require proxy authentication by default; @app.server(unauthenticated=True) makes them public.", "components": ["modal"], "sources": ["modal:s7d083f819a21"], "status": "REASONED"},
    "modal-shared": {"text": "Shared Endpoints always require a Proxy Token and cannot be made public with the Dedicated Endpoint flag; the cited proxy-auth page does not explicitly document this exception.", "components": ["modal"], "sources": ["modal:s7d083f819a21"], "status": "REASONED"},
    "modal-credentials": {"text": "Proxy authentication accepts Modal-Key and Modal-Secret or Authorization: Bearer <token_id>.<token_secret>; missing credentials on a protected endpoint return 401.", "components": ["modal"], "sources": ["modal:s7d083f819a21"], "status": "REASONED"},
    "runpod-bind": {"text": "RunPod HTTP proxy needs the exposed pod interface: bind the exposed service to 0.0.0.0 inside the pod, not localhost.", "components": ["runpod"], "sources": ["runpod:s817198f039ee"], "status": "REASONED"},
    "listener-auth": {"text": "Add listener authentication where supported; otherwise expose an authenticating gateway and keep the bare backend private. The guide cites Ollama locally, but records no Ollama vendor source here.", "components": ["runpod", "vast", "jupyter"], "sources": ["runpod:s817198f039ee", "vast:s0bdbda534723", "jupyter:sc703a8030c8f"], "status": "REASONED"},
    "mfa": {"text": "Platform-account MFA and workload authentication are separate; the guide recommends account MFA and says no platform adds workload MFA. Account-MFA sources are not recorded here.", "components": ["modal", "jupyter"], "sources": ["modal:s7d083f819a21", "jupyter:sc703a8030c8f"], "status": "REASONED"},
    "lambda-ssh": {"text": "Lambda requires an SSH key at launch; keep the private key off the instance.", "components": ["lambda"], "sources": ["lambda:sb12b4a953833"], "status": "REASONED"},
    "vast-ssh": {"text": "Vast.ai disables SSH password authentication and uses the registered public key; keep the private key off the instance.", "components": ["vast"], "sources": ["vast:s6e0303ef19fe"], "status": "REASONED"},
    "runpod-ssh": {"text": "RunPod recommends SSH keys and offers an optional password; use the key and skip the password.", "components": ["runpod"], "sources": ["runpod:s13c43b856d4f"], "status": "REASONED"},
    "verify-inventory": {"text": "ss inventories TCP listeners in the current network namespace only, not UDP, firewall state or platform publication; cross-check mappings and probe each from outside. No ss source is recorded.", "components": ["runpod", "vast"], "sources": ["runpod:s817198f039ee", "vast:sc25989a1613e"], "status": "REASONED", "verify": [1]},
    "verify-jupyter": {"text": "Probe loopback :8888/api/contents directly: the guide expects 403 without the Jupyter token and 200 with it; any anonymous data response is a finding. The cited security page documents token auth but not this exact endpoint/status pair.", "components": ["jupyter"], "sources": ["jupyter:sc703a8030c8f"], "status": "REASONED", "verify": [1]},
    "verify-mapping": {"text": "Repeat credential-free and authenticated requests per exposed mapping; anonymous app data fails, while a proxy 401 alone does not prove native listener auth and needs the direct positive control.", "components": ["runpod", "vast", "modal", "jupyter"], "sources": ["runpod:s817198f039ee", "vast:sc25989a1613e", "vast:s0bdbda534723", "modal:s7d083f819a21", "jupyter:sc703a8030c8f"], "status": "REASONED", "verify": [1]},
    "remote-desktop": {"text": "Inventory template noVNC ports such as 6080 and VNC ports such as 5900/5901; check weak or empty passwords, require a strong password plus encrypted tunnel for direct VNC, or remove its public mapping. Test with a VNC client; no noVNC/VNC source is recorded here.", "components": ["runpod", "vast"], "sources": ["runpod:s817198f039ee", "vast:sc25989a1613e"], "status": "REASONED"}
  }
}
---
# Rented GPUs: RunPod, Vast.ai, Lambda, Modal

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| publication: Raw port publication or a firewall allowance adds no listener authentication; platform proxies authenticate only the routes they actually cover. | RunPod documentation unknown; Vast.ai documentation unknown; Lambda Public Cloud documentation unknown; Modal proxy authentication unknown | REASONED |
| runpod-http: Expose HTTP Ports publishes https://[POD_ID]-[INTERNAL_PORT].proxy.runpod.net with automatic HTTPS; anyone with the URL can reach it, so the application still needs authentication. | RunPod documentation unknown | REASONED |
| runpod-tcp: Exposed TCP ports forward directly on a public IP without automatic TLS; secure template listeners before exposure and implement application TLS for sensitive TCP data. | RunPod documentation unknown | REASONED |
| runpod-symmetry: TCP configuration values above 70000 request symmetrical mapping rather than naming valid ports; read the assigned mapping from the pod environment, such as RUNPOD_TCP_PORT_70000. Mapping remains public. | RunPod documentation unknown | REASONED |
| vast-ssh-port: Vast.ai SSH launch mode opens internal port 22 by default. | Vast.ai documentation unknown | REASONED |
| vast-jupyter-port: Vast.ai Jupyter launch mode opens internal 8080 as well as SSH port 22 by default. | Vast.ai documentation unknown | REASONED |
| vast-mapping: Each open Vast.ai internal port maps to a random external port on a usually shared public IP; the networking docs describe no additional firewall step. | Vast.ai documentation unknown | REASONED |
| vast-proxy: Instance Portal uses local Caddy proxying when external and internal ports differ; forwarded apps can stay on loopback and PORTAL_CONFIG describes routing and presentation. | Vast.ai documentation unknown | REASONED |
| vast-token: Portal links carry a credential token; protect the URL, test access without it and confirm the selected route actually authenticates. | Vast.ai documentation unknown | REASONED |
| vast-auth-controls: The pinned base image exposes OPEN_BUTTON_TOKEN, WEB_PASSWORD and ENABLE_AUTH/AUTH_EXCLUDE; PORTAL_CONFIG is not the credential. | Vast.ai base image 00064421641881c1f83ff58c55f13cbc10cbea4d; Vast.ai documentation unknown | REASONED |
| lambda-default: Lambda inbound firewall denies by default except ICMP and TCP 22; other listeners require explicit global/workspace rules or a per-instance ruleset attached at launch. | Lambda Public Cloud documentation unknown | REASONED |
| lambda-rule: An allow rule admits the specified source range without authenticating callers; pair it with listener or proxy authentication. Removing an allow rule closes access. | Lambda Public Cloud documentation unknown | REASONED |
| modal-web: Web endpoints using modal.fastapi_endpoint, the replacement for @web_endpoint, are public by default; requires_proxy_auth=True enables proxy authentication. | Modal proxy authentication unknown | REASONED |
| modal-dedicated: Dedicated Endpoints require proxy authentication by default; --unauthenticated makes them public. | Modal proxy authentication unknown | REASONED |
| modal-server: Servers require proxy authentication by default; @app.server(unauthenticated=True) makes them public. | Modal proxy authentication unknown | REASONED |
| modal-shared: Shared Endpoints always require a Proxy Token and cannot be made public with the Dedicated Endpoint flag; the cited proxy-auth page does not explicitly document this exception. | Modal proxy authentication unknown | REASONED |
| modal-credentials: Proxy authentication accepts Modal-Key and Modal-Secret or Authorization: Bearer &lt;token_id&gt;.&lt;token_secret&gt;; missing credentials on a protected endpoint return 401. | Modal proxy authentication unknown | REASONED |
| runpod-bind: RunPod HTTP proxy needs the exposed pod interface: bind the exposed service to 0.0.0.0 inside the pod, not localhost. | RunPod documentation unknown | REASONED |
| listener-auth: Add listener authentication where supported; otherwise expose an authenticating gateway and keep the bare backend private. The guide cites Ollama locally, but records no Ollama vendor source here. | RunPod documentation unknown; Vast.ai documentation unknown; Jupyter Server security unknown | REASONED |
| mfa: Platform-account MFA and workload authentication are separate; the guide recommends account MFA and says no platform adds workload MFA. Account-MFA sources are not recorded here. | Modal proxy authentication unknown; Jupyter Server security unknown | REASONED |
| lambda-ssh: Lambda requires an SSH key at launch; keep the private key off the instance. | Lambda Public Cloud documentation unknown | REASONED |
| vast-ssh: Vast.ai disables SSH password authentication and uses the registered public key; keep the private key off the instance. | Vast.ai documentation unknown | REASONED |
| runpod-ssh: RunPod recommends SSH keys and offers an optional password; use the key and skip the password. | RunPod documentation unknown | REASONED |
| verify-inventory: ss inventories TCP listeners in the current network namespace only, not UDP, firewall state or platform publication; cross-check mappings and probe each from outside. No ss source is recorded. | RunPod documentation unknown; Vast.ai documentation unknown | REASONED |
| verify-jupyter: Probe loopback :8888/api/contents directly: the guide expects 403 without the Jupyter token and 200 with it; any anonymous data response is a finding. The cited security page documents token auth but not this exact endpoint/status pair. | Jupyter Server security unknown | REASONED |
| verify-mapping: Repeat credential-free and authenticated requests per exposed mapping; anonymous app data fails, while a proxy 401 alone does not prove native listener auth and needs the direct positive control. | RunPod documentation unknown; Vast.ai documentation unknown; Modal proxy authentication unknown; Jupyter Server security unknown | REASONED |
| remote-desktop: Inventory template noVNC ports such as 6080 and VNC ports such as 5900/5901; check weak or empty passwords, require a strong password plus encrypted tunnel for direct VNC, or remove its public mapping. Test with a VNC client; no noVNC/VNC source is recorded here. | RunPod documentation unknown; Vast.ai documentation unknown | REASONED |
<!-- version-basis:end -->

Unlike the major clouds, most rented-GPU platforms put no default-deny firewall in front of the box. How a bound port becomes public differs by platform: on RunPod you expose a port (HTTP or TCP), on Vast.ai a launch mode or an added port maps it to a public port, on Lambda you open a firewall rule (its inbound firewall is deny-by-default), and on Modal it depends on the serverless construct. Raw port publication and a firewall allowance add NO authentication of their own, so a listener exposed that way is reachable with only whatever auth it has itself; an authenticating platform proxy is the exception (Modal's Endpoints and Servers require proxy auth by default and Shared Endpoints always do, only a public Web endpoint does not, and Vast.ai's Instance Portal gates the routes it proxies), but do not assume one is in front of a given port. Treat every listener the same way you would on your own hardware: bind it privately or authenticate it, per [ollama.md](ollama.md) and [model-servers.md](model-servers.md).

## RunPod

Exposed HTTP ports (the "Expose HTTP Ports" pod setting) go through RunPod's proxy at `https://[POD_ID]-[INTERNAL_PORT].proxy.runpod.net`; the proxy terminates HTTPS automatically, "All connections are secured with HTTPS, even if your internal service uses HTTP," but the resulting URL is publicly reachable by anyone who has it, so a bare Jupyter server or model API on an exposed HTTP port still needs its own authentication.

Exposed TCP ports get "direct TCP forwarding with a public IP address" instead, and TLS is not automatic there: RunPod's own docs say to "implement TLS in your application when handling sensitive data over TCP." Secure every template listener, including notebooks, before exposing its port; a notebook exposed as raw TCP with no application-level password is fully open.

A "symmetrical port mapping" option lets a template ask for matching internal and external port numbers by specifying a value above 70000 in its TCP configuration. That value is not a port: RunPod's documentation says such numbers are not valid ports and serve only to signal the request, and the real assignment arrives in the pod's environment (for example `$RUNPOD_TCP_PORT_70000`). It is a convenience for the pod's own scripts, not a security boundary, and the port is still public once mapped.

## Vast.ai

Rented instances open ports per launch mode (port 22 for SSH mode, port 22 plus 8080 for Jupyter mode by default); each internal port maps to a random external port on a shared public IP, and once a port is mapped it is reachable from the internet with no firewall step described in Vast.ai's docs.

The Instance Portal fronts web apps on the instance with a reverse proxy (Caddy) when the external and internal ports differ, and secures access with a token rather than a login: "a secure token is appended to the link to prevent unauthorised access to your applications." The token is `OPEN_BUTTON_TOKEN` (the base image also exposes `WEB_PASSWORD` and an `ENABLE_AUTH`/`AUTH_EXCLUDE` pair that decide which routes are actually protected); `PORTAL_CONFIG` only configures the portal's routing and presentation, not the credential. A token-bearing link IS the credential: anyone who has that URL is authenticated, so treat it as a secret and share it only with intended recipients (stripping the token is useful for testing that anonymous access is refused). Do not assume an app is private just because it sits behind the portal's port remapping, and confirm the route is one the portal actually authenticates.

## Lambda

Lambda's Public Cloud firewall is deny-by-default for inbound traffic with two exceptions: "By default, Lambda allows only incoming ICMP traffic or TCP traffic on port 22 (SSH)." Everything else, a Jupyter notebook, a model server port, needs an explicit firewall rule (global, workspace-wide rules, or a per-instance ruleset attached at launch); Lambda's own guidance is blunt about the tradeoff: "Each port you open increases the attack surface of your instances."

Opening a rule makes the port reachable from whatever source range you allow, with no authentication of its own, so pair the rule with the listener's native auth or a proxy in front, not the firewall rule alone.

## Modal

Modal's serverless constructs default differently by shape, and the control differs too. Web endpoints (the current decorator is `modal.fastapi_endpoint`, which replaced `@web_endpoint`) are "publicly available by default" and stay public until the function sets `requires_proxy_auth=True`. A Dedicated Endpoint is made public with the `--unauthenticated` flag; a Server sets `unauthenticated=True` on `@app.server(...)` instead of that flag; and a Shared Endpoint always requires a Proxy Token and cannot be made public that way. Name the construct you are deploying and check its actual control rather than assuming one flag covers all of them.

Where proxy auth is enabled, callers authenticate with a Token ID and Token Secret pair, either as separate `Modal-Key` and `Modal-Secret` headers or combined as `Authorization: Bearer <token_id>.<token_secret>` (Modal notes this mirrors "the same scheme the OpenAI API uses"). A protected endpoint called without credentials returns 401 with "missing credentials for proxy authorization." Check which default your construct uses before deploying; do not assume a Web Function is private.

## The pattern, whatever the platform

The platform's own controls (RunPod's proxy TLS, Vast.ai's portal token, Lambda's firewall rules, Modal's proxy auth) are necessary but not sufficient on their own. How to bind the model server depends on which kind of proxy is in front of it. RunPod's HTTP proxy reaches the pod over its exposed network interface rather than through a local backend, so the service must bind `0.0.0.0` inside the pod; RunPod's own troubleshooting guidance is explicit that binding to `localhost` only will keep the proxy from reaching it. Vast.ai's Instance Portal is the opposite case: it is a local reverse proxy (Caddy) running on the instance itself, so the app it forwards to can stay on loopback behind it, the same pattern as an authenticating proxy on your own hardware. Whichever binding the platform's proxy needs, add the listener's OWN authentication where it supports one; where it does not (Ollama's API, for example, has no native authentication), keep the unauthenticated backend private and put an authenticating gateway in front, so the gateway and not the bare listener is what the platform exposes, exactly as [ollama.md](ollama.md) and [model-servers.md](model-servers.md) describe. A platform-level control that changes later, a firewall rule widened to a broader source range, a template rebuilt without a flag, should not be the only thing standing between the listener and the internet (deleting a Lambda allow rule, by contrast, closes the port rather than opening it).

MFA: none of these platforms add a second factor to the workload itself. The account you log into RunPod, Vast.ai, Lambda, or Modal with should have MFA enabled ([mfa.md](mfa.md)); an API key or proxy-auth token secures a machine client, and is a separate control from your platform login.

SSH: authenticate with your own key, not a password. Lambda requires an SSH key at launch; Vast.ai disables password authentication and uses the key you register; RunPod recommends key auth and offers an optional password you should skip. Keep the private key off the instance, and treat SSH access as a control separate from the platform login above.

## Verify

REASONED: listener inventory and direct/proxied authentication pairs; no GPU-platform deployment, workload credentials or outside probe host was supplied for this metadata review, and no run is recorded. Expected readings below follow the cited platform and Jupyter documentation; the exact Jupyter endpoint/status pair and ss semantics lack direct citations.

```bash
ss -tlnp   # TCP listening sockets in THIS network namespace only - not UDP, not a firewall, and not
           # the platform's NAT/proxy publication. A port here may be private OR public (once exposed/
           # mapped), and a port published by the platform need not appear here at all, so cross-check
           # against the platform's port mappings and probe each MAPPED port from outside (below).
# Does the LISTENER itself demand auth? Test it DIRECTLY on loopback, with no platform proxy in the path,
# as a matched pair. Jupyter uses an 'Authorization: token <token>' (or ?token=) scheme; without it
# /api/contents returns 403, with a valid token 200. Substitute the real token.
(
  # Feed the token to curl on stdin (curl --header @-), never in argv:
  # -H "Authorization: token TOKEN" is readable in ps / /proc/<pid>/cmdline.
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  # The Jupyter token you substitute on the set -- line enters shell history.
  # Clear that history line afterward.
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_JUPYTER_TOKEN'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the Jupyter token on the set -- line above; not probing"; exit ;; esac
  curl -q -g -sS -o /dev/null -w 'jupyter no-token=%{http_code} exit=%{exitcode}\n' --noproxy '*' \
    --connect-timeout 5 --max-time 10 http://127.0.0.1:8888/api/contents
  printf 'Authorization: token %s\n' "$1" | curl -q -g -sS -o /dev/null -w 'jupyter with-token=%{http_code} exit=%{exitcode}\n' --noproxy '*' \
    --connect-timeout 5 --max-time 10 -H @- http://127.0.0.1:8888/api/contents
)
# Then confirm the SAME listener is authenticated FROM OUTSIDE, once PER exposed port/mapping. A probe of
# the platform proxy hostname shows reachability and that something gates the URL, but a 401/200 there can
# be the PLATFORM proxy rather than the listener, so read it with the direct-loopback pair above: a no-
# credential 200 returning app data is a finding; a 401 is only conclusive alongside a direct 200. The
# guard refuses while a placeholder remains; repeat for each mapped port.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  # The token you substitute on the set -- line enters shell history.
  # Use a short-lived token or clear that history line afterward.
  set -- PASTE_WHOLE_BLOCK 'https://REPLACE_WITH_POD_ID-REPLACE_WITH_PORT.proxy.runpod.net/REPLACE_WITH_PROTECTED_PATH' 'REPLACE_WITH_TOKEN'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute the URL on the set -- line above; not probing"; exit ;; esac
  case "$2" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the token on the set -- line above; not probing"; exit ;; esac
  curl -q -g -sS -o /dev/null -w 'no-cred=%{http_code} exit=%{exitcode}\n' --noproxy '*' --connect-timeout 5 --max-time 10 "$1"
  printf 'Authorization: Bearer %s\n' "$2" | curl -q -g -sS -o /dev/null -w 'with-cred=%{http_code} exit=%{exitcode}\n' --noproxy '*' --connect-timeout 5 --max-time 10 -H @- "$1"
)
```

Every port `ss` shows listening should be either closed (not exposed at the platform layer) or authenticated (the listener itself demands a key, token, or login). A Jupyter server that answers without its token is a finding, whichever of these platforms it runs on.

## Common mistakes

- Assuming a rented box has a default-deny firewall like a major cloud's security group; most rented-GPU platforms do not.
- Treating a template's HTTPS proxy URL as proof the underlying service is authenticated; the proxy secures transport, not access.
- Overlooking a template's remote desktop: a ComfyUI or Linux-desktop image may include a noVNC web interface served on a port like 6080, backed by a VNC server on a port such as 5900 or 5901, either of which may default to a weak or empty password and be published like any other listener. Check both listeners and their public mappings for missing or weak authentication: the browser page's HTTPS does not protect a separately reachable VNC connection, so a direct VNC mapping needs its own strong password and an encrypted tunnel, or should be kept off the public mapping. Test a direct VNC mapping with a VNC client, since the browser access controls and the HTTP status checks above may not cover it.
- Leaving a Modal Web Function without `requires_proxy_auth=True` because Endpoints and Servers are private by default and it is easy to assume Web Functions are too.
- Reusing a rented box's platform login (RunPod/Vast.ai/Lambda/Modal account) as if it were the same thing as the workload's own authentication; they are separate controls.

## Sources (checked September 2026)

- RunPod expose ports (proxy HTTPS, TCP forwarding): https://docs.runpod.io/pods/configuration/expose-ports
- Vast.ai networking and ports (default ports, port mapping): https://docs.vast.ai/guides/instances/connect/networking
- Vast.ai Instance Portal (PORTAL_CONFIG, Caddy reverse proxy, secure-token links): https://docs.vast.ai/guides/instances/connect/instance-portal
- Lambda Cloud firewalls (default-deny inbound, SSH/ICMP exception, rule types): https://docs.lambda.ai/public-cloud/firewalls/
- Modal proxy auth for web endpoints (Endpoints/Servers vs Web Functions defaults, headers): https://modal.com/docs/guide/webhook-proxy-auth
- Vast.ai base image (portal auth: `OPEN_BUTTON_TOKEN`, `WEB_PASSWORD`, `ENABLE_AUTH`/`AUTH_EXCLUDE`): https://github.com/vast-ai/base-image/blob/00064421641881c1f83ff58c55f13cbc10cbea4d/README.md
- Jupyter Server security (token authentication; a missing token is refused with 403): https://jupyter-server.readthedocs.io/en/latest/operators/security.html
- Lambda SSH (an SSH key is required at launch): https://docs.lambda.ai/public-cloud/on-demand/connecting-instance/
- Vast.ai SSH (password authentication is disabled; register a key): https://docs.vast.ai/guides/instances/connect/ssh
- RunPod SSH (key authentication recommended, optional password): https://docs.runpod.io/pods/configuration/use-ssh
