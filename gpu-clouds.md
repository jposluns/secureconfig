# Rented GPUs: RunPod, Vast.ai, Lambda, Modal

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
  set -- PASTE_WHOLE_BLOCK 'https://REPLACE_WITH_POD_ID-REPLACE_WITH_PORT.proxy.runpod.net/REPLACE_WITH_PROTECTED_PATH' 'REPLACE_WITH_TOKEN'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute the URL on the set -- line above; not probing"; exit ;; esac
  case "$2" in *REPLACE_WITH_*|"") echo "substitute the token on the set -- line above; not probing"; exit ;; esac
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
- Vast.ai base image (portal auth: `OPEN_BUTTON_TOKEN`, `WEB_PASSWORD`, `ENABLE_AUTH`/`AUTH_EXCLUDE`): https://github.com/vast-ai/base-image/blob/main/README.md
- Jupyter Server security (token authentication; a missing token is refused with 403): https://jupyter-server.readthedocs.io/en/latest/operators/security.html
- Lambda SSH (an SSH key is required at launch): https://docs.lambda.ai/public-cloud/on-demand/connecting-instance/
- Vast.ai SSH (password authentication is disabled; register a key): https://docs.vast.ai/guides/instances/connect/ssh
- RunPod SSH (key authentication recommended, optional password): https://docs.runpod.io/pods/configuration/use-ssh
