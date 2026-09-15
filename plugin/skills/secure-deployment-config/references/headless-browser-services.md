# Headless browser services: Chrome DevTools Protocol, Selenium Grid, browserless, and Playwright server

Agent and scraping stacks run these to drive a real browser, and that is exactly the exposure: whoever
reaches the endpoint gets JavaScript execution inside every page the browser opens, the profile's
cookie jar, navigation to `file://` and to internal addresses, and a pivot from the service's own
network position, including the cloud metadata endpoint ([egress-metadata.md](egress-metadata.md)). An
exposed browser automation port is usually unauthenticated code execution and credential theft, not
just data. Three of the four listen on loopback by default, so the headline mistake is publishing the
port; none of the four terminates TLS or ships real authentication that is on by default. Front them
per [fronting-auth.md](fronting-auth.md), [nginx.md](nginx.md) or [caddy.md](caddy.md), keep their
listeners private per [docker.md](docker.md) and [tunnels.md](tunnels.md), and treat every connection
URL as a secret ([secrets.md](secrets.md)).

## Chrome DevTools Protocol

A Chrome or Chromium started with `--remote-debugging-port=9222` speaks the DevTools Protocol, and that
endpoint has no authentication of any kind: the only control is not to let the network reach it. By
default it binds to loopback only. It becomes reachable when someone adds `--remote-debugging-address`
(for example `0.0.0.0`) or publishes the container port; `GET /json` and `/json/version` then hand out
the WebSocket debugger URL, and a client on that socket has `Runtime.evaluate` (arbitrary JavaScript in
any page), the Network domain (cookies and credentials), `Page.navigate` including `file://` URLs, and
full control of every tab. There is no flag that adds a password, so keep the flag off when you are not
debugging, keep the port on loopback and reach it over an SSH tunnel ([tunnels.md](tunnels.md)) or a
private network, and in a container publish it only to the host loopback (`127.0.0.1:9222:9222`) if at
all. Publishing a container port cannot expose a listener that is still loopback-bound inside the
container, so an image where `-p 9222:9222` "just works" has already widened the bind for you; check
the launch flags, not only the compose file.

From Chrome 136 the `--remote-debugging-port` and `--remote-debugging-pipe` switches are ignored when
they would debug the default user data directory, so an automation deployment passes an explicit
`--user-data-dir`; that changes how you reproduce the exposure, not whether it exists, since automation
always runs with a custom profile.

## Selenium Grid

Selenium Grid ships with no authentication enabled: the Router's basic-auth credentials
(`--username` and `--password`, or the `SE_ROUTER_USERNAME` and `SE_ROUTER_PASSWORD` variables on the
Docker images) are unset by default. The default bind is version-dependent, and the difference is the
whole exposure: Grid 4 binds to `localhost` by default, while Grid 3 binds to `0.0.0.0`, every
interface. Treat any Grid 3 or inherited deployment as open until proven otherwise. In Grid 4 the
common exposure routes are the Docker images, an explicit `--host 0.0.0.0`, and a published `4444`. The
Router, Hub, Standalone and the Grid web UI share port `4444`; a Node listens on `5555`; in distributed
mode the event bus uses `4442` and `4443`, which the Router's basic auth does not cover, so set
`--registration-secret` so a reachable bus does not accept rogue Nodes. An exposed Grid hands unauthenticated control of the browsers it drives to anyone who reaches it.

The Docker browser images add two more listeners: they start VNC by default (`SE_START_VNC` defaults to
`true`) on `5900` with noVNC on `7900`, and the vendor's own example connects with the password
`secret`; change it with `SE_VNC_PASSWORD`, disable the password prompt deliberately only with
`SE_VNC_NO_PASSWORD`, or turn VNC off with `SE_START_VNC=false`. Keep the default `localhost` bind on
Grid 4 or bind to a private interface, never `--host 0.0.0.0` on a public one; firewall `4444`, `5555`,
`4442`, `4443`, `5900` and `7900`; and put basic auth plus TLS in front per [nginx.md](nginx.md),
[caddy.md](caddy.md) and [fronting-auth.md](fronting-auth.md), since the Router's basic auth travels in
clear text without it.

## browserless

browserless listens on port `3000` and gates access with a `TOKEN`, but the token is optional and off
by default: with no `TOKEN` set, every endpoint is unauthenticated, which is full remote control of the
browsers it manages. Always set a long, randomized `TOKEN` (never a vendor sample, never committed),
and publish the port to loopback (`-p 127.0.0.1:3000:3000`) or keep it on an internal container network
with no host mapping. The token is presented in the connection URL, so proxy and access logs become
credential stores; front the service with TLS so it is unreadable in transit, and handle the token as
[secrets.md](secrets.md) describes. browserless terminates no TLS of its own, so the fronting layer is
also where HTTPS lives.

## Playwright server

`browserType.launchServer()` and `playwright run-server` expose a `ws://` endpoint, and there is no
password or user model: the endpoint's path is the only secret. `launchServer()` binds to `localhost`
by default and generates an unguessable path, and Playwright's documentation warns that a process that
knows the path "can take control of the OS user", so treat the full `wsEndpoint` URL as a credential.
The exposure is binding it outward, which the Docker documentation's own `run-server --host 0.0.0.0`
example does; once the port is reachable, the only thing between an attacker and the browser is whether
they can learn or guess the path, so do not rely on path secrecy alone. Bind the server to `127.0.0.1`
explicitly, leave the generated path in place, never log or commit the `wsEndpoint` URL or bake it into
an image, and front it with `wss://` and header-based authentication (Playwright's `connect()` accepts
custom `headers`, which a reverse proxy can require) per [fronting-auth.md](fronting-auth.md). Rotate
the endpoint by restarting the server. Playwright serves no TLS itself.

## Shared exposures

Every one of these drives a real browser, so an exposed endpoint is typically unauthenticated code
execution plus session theft plus a pivot: the browser can reach internal panels, unauthenticated
internal APIs, and the cloud metadata endpoint from inside your network
([egress-metadata.md](egress-metadata.md)), and read local files through `file://`. Restrict the
service's own egress as well as its inbound reach. One more path ties them together: Selenium,
Playwright and browserless all drive Chromium over the DevTools Protocol in the common case, so a debug
port opened "just to inspect" a Node or a browserless container (a stray `-p 9222:9222`) bypasses
whatever authentication the front tool has. Keep 9222 unpublished wherever these run.

## Verify

Every probe below is reasoned, not demonstrated: the authoring environment has no container runtime, so
none was stood up in its exposed and fixed states. Each names its expected exposed and fixed result so
it discriminates when run against a live instance; backlog row 2.26 tracks demonstrating them. Run each
probe's positive control (the same request from the service host's own loopback) so a dead service is
not misread as fixed, and treat an empty result, an HTML page, an unrelated error, or a transport
failure as inconclusive, never as the fixed state.

```bash
# On the host: these listeners should be bound to loopback or an internal interface, not a wildcard.
ss -tlnp | grep -E ':(9222|4442|4443|4444|5555|3000|5900|7900) '   # loopback or internal only
# browserless with no TOKEN answers /pressure unauthenticated; with a TOKEN set it rejects the request.
curl -q -g -s --noproxy '*' -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
  'https://browser.example.com/pressure'
```

An exposed browserless returns the load JSON (CPU, memory, sessions, queue depth) with no token; once a
`TOKEN` is set the same request is rejected (confirm the exact status against your image, and repeat
with a deliberately wrong token expecting the same rejection). Because Docker publishes ports through
NAT rules that a host socket listing can miss, also inspect the Compose published ports and probe each
host port from an external vantage, over IPv4 and IPv6. Playwright's server port is whatever you
configured (ephemeral by default), so add it to both checks.

For the DevTools, Grid and Playwright ports, the fixed state answers nothing from outside, so guard the
address in the block below and read the `exit` field: a refusal or timeout (`exit=7` or `exit=28`) is
the fixed state, and an HTTP answer is the exposure. Substitute an IP literal, not a name, for the
DevTools probe, because the endpoint rejects a forwarded `Host` that is not an address.

```bash
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
    *) curl -q -g -s --noproxy '*' --connect-timeout 5 --max-time 20 \
         -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:9222/json/version" ;;
  esac
)
```

Exposed, the DevTools probe returns a `200` JSON body containing `webSocketDebuggerUrl`, which is the
whole compromise. To check the other services, change the URL in the block's `curl` line, leaving the
guard lines intact, to each port in turn: `http://$1:4444/status` for a Selenium Grid Router, Hub or
Standalone (a `200` JSON `ready` and node inventory is exposure; a `401` carrying `WWW-Authenticate:
Basic` means the Router auth is on but the port is still reachable, which is not the fixed state),
`http://$1:5555/status` for a Node, and the Playwright server on the port you configured (`launchServer`
uses an ephemeral port unless you set one; `run-server` takes `--port`), where any HTTP answer means the
port is reachable and, since the path is the only gate, is already the finding. The distinguishing
behaviour for each is in the cited vendor pages.

## Sources (checked September 2026)

- Chrome DevTools Protocol remote debugging: https://developer.chrome.com/docs/devtools/remote-debugging/
- Chrome DevTools Protocol domains (Runtime, Network, Page): https://chromedevtools.github.io/devtools-protocol/
- Chrome 136 remote-debugging user-data-dir change: https://developer.chrome.com/blog/remote-debugging-port
- Selenium Grid CLI options (host, bind-host, username, password): https://www.selenium.dev/documentation/grid/configuration/cli_options/
- Selenium Grid getting started (default localhost bind, ports): https://www.selenium.dev/documentation/grid/getting_started/
- Selenium Docker images env vars (SE_START_VNC, SE_VNC_PASSWORD, SE_ROUTER_USERNAME): https://github.com/SeleniumHQ/docker-selenium/blob/trunk/ENV_VARIABLES.md
- browserless Docker configuration (TOKEN, port 3000): https://docs.browserless.io/baas/docker/config
- Playwright BrowserType.launchServer and connect: https://playwright.dev/docs/api/class-browsertype
- Playwright Docker (run-server remote connection): https://playwright.dev/docs/docker
