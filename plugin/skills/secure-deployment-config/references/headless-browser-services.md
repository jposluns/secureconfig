# Headless browser services: Chrome DevTools Protocol, Selenium Grid, browserless, and Playwright server

Agent and scraping stacks run these to drive a real browser, and that is exactly the exposure: whoever
reaches the endpoint gets JavaScript execution inside the pages the browser opens, the profile's cookie
jar, and a pivot from the service's own network position, including internal panels and the cloud
metadata endpoint ([egress-metadata.md](egress-metadata.md)). An exposed browser automation port is
usually unauthenticated code execution and credential theft, not just data. None of the four ships
real authentication that is on by default, and none binds to a documented loopback address you can rely
on without checking, so the headline mistake is letting the network reach the port at all. Restrict the
service's own egress as well as its inbound reach, front the listeners per
[fronting-auth.md](fronting-auth.md), [nginx.md](nginx.md) or [caddy.md](caddy.md), keep them private
per [docker.md](docker.md) and [tunnels.md](tunnels.md), and treat every connection URL as a secret
([secrets.md](secrets.md)).

## Chrome DevTools Protocol

A Chrome or Chromium started with `--remote-debugging-port=9222` speaks the DevTools Protocol, and that
endpoint has no authentication of any kind: the only control is not to let the network reach it. Recent
Chrome binds the debugging socket to loopback, so the exposure is not usually a single flag but a
listener put in front of it: a published container port, an SSH or socat forward, a reverse proxy, or a
modified image. Publishing a container port cannot reach a socket that is still loopback-bound inside
the container, so an image where `-p 9222:9222` "just works" has arranged a forward for you; read what
actually binds the port, not only the compose file. `GET /json` and `/json/version` hand out the
WebSocket debugger URL, and a client on that socket has `Runtime.evaluate` (arbitrary JavaScript in any
page), the Network domain (cookies and credentials), and full control of every tab. There is no flag
that adds a password, so keep the port on loopback and reach it over an SSH tunnel
([tunnels.md](tunnels.md)) or a private network, and never expose it through a forward or proxy without
an authenticating layer in front.

From Chrome 136 the `--remote-debugging-port` and `--remote-debugging-pipe` switches are ignored when
they would debug the default user data directory, so a deployment passes an explicit, non-default
`--user-data-dir`; Chrome for Testing, which automation commonly uses, is exempt and keeps the older
behaviour. That changes how you reproduce the exposure, not whether it exists.

## Selenium Grid

Selenium Grid ships with no authentication enabled: the Router's basic-auth credentials (`--username`
and `--password`, or the `SE_ROUTER_USERNAME` and `SE_ROUTER_PASSWORD` variables on the Docker images)
are unset by default. Its default bind is not a loopback guarantee: the docs describe `--host` as
"usually determined automatically", the Docker images leave `SE_BIND_HOST` unset, and Grid 3 binds
`0.0.0.0` outright, so treat any Grid whose bind you have not set and observed as reachable, and set an
explicit `--host` (with `--bind-host`) to a private interface. The Router, Hub, Standalone and the Grid
web UI share port `4444`; a Node listens on `5555`. Distributed deployments add more unauthenticated
listeners: the event bus on `4442` and `4443`, and the Distributor, Session Map, event bus HTTP, and
New Session Queue on `5553`, `5556`, `5557` and `5559`. Firewall all of them. The event bus is not
protected by the Router's basic auth; `--registration-secret` makes participants validate each other's
event messages, but it is carried in those messages rather than encrypting the transport, so it does
not make a reachable bus safe on its own: run the bus on a private, trusted network with matching
secrets on every component.

The Docker browser images add two more listeners: they start VNC by default (`SE_START_VNC` defaults to
`true`) on `5900` with noVNC on `7900`, and the vendor's own example connects with the password
`secret`; change it with `SE_VNC_PASSWORD`, disable the prompt deliberately only with
`SE_VNC_NO_PASSWORD`, or turn VNC off with `SE_START_VNC=false`. Selenium can terminate TLS itself with
`--https-certificate` and `--https-private-key`, but it is not enabled by default, and the Router's
basic auth travels in clear text without it; enabling native HTTPS or, more commonly, fronting the Grid
per [nginx.md](nginx.md), [caddy.md](caddy.md) and [fronting-auth.md](fronting-auth.md) is what protects
the credentials in transit.

## browserless

browserless listens on port `3000` and gates access with a `TOKEN`, but the token is optional and off
by default: with no `TOKEN` set, every endpoint is unauthenticated, including the routes that run
caller-supplied Puppeteer or Playwright code, which is full remote control of the browsers it manages.
Always set a long, randomized `TOKEN` (never a vendor sample, never committed), and publish the port to
loopback (`-p 127.0.0.1:3000:3000`) or keep it on an internal container network with no host mapping.
The token is presented in the connection URL, so proxy and access logs become credential stores; front
the service with TLS so it is unreadable in transit, and handle the token as [secrets.md](secrets.md)
describes. browserless blocks `file://` navigation by default (`ALLOW_FILE_PROTOCOL` is `false`), so
leave that off; it terminates no TLS of its own, so the fronting layer is where HTTPS lives.

## Playwright server

`browserType.launchServer()` and `playwright run-server` expose a `ws://` endpoint, and there is no
password or user model. Do not rely on the endpoint path as a secret: `run-server` defaults its
`--path` to `/`, so the CLI form has no secret path at all, and while `launchServer()` generates an
unguessable path, the server answers `GET /json` with its own endpoint path, so a client that can reach
the port can discover it. Treat a reachable Playwright port as the finding. The exposure is binding it
outward, which the Docker documentation's own `run-server --host 0.0.0.0` example does; Playwright's
documentation warns that a process that reaches the endpoint "can take control of the OS user". Bind the
server to `127.0.0.1` explicitly, never log or commit the `wsEndpoint` URL or bake it into an image, and
put a reverse proxy in front that authenticates both the WebSocket upgrade and the discovery routes and
terminates `wss://` (`connect()` accepts custom `headers` a proxy can require) per
[fronting-auth.md](fronting-auth.md) and [nginx.md](nginx.md). Playwright serves no TLS itself.

## Shared exposures

Every one of these drives a real browser, so an exposed endpoint is typically unauthenticated code
execution plus session theft plus a pivot: the browser can reach internal panels, unauthenticated
internal APIs, and the cloud metadata endpoint from inside your network
([egress-metadata.md](egress-metadata.md)), which is why restricting the service's egress matters as
much as its inbound reach. Local-file reads through `file://` are part of that reach for a raw CDP,
Selenium, or Playwright browser, though a fronting tool may block them (browserless does by default).
One path ties the four together: Selenium, Playwright and browserless all drive Chromium over the
DevTools Protocol in the common case, so a debug port opened "just to inspect" a Node or a browserless
container (a stray `-p 9222:9222`) bypasses whatever authentication the front tool has. Keep 9222
unpublished wherever these run.

## Verify

Every probe below is reasoned, not demonstrated: the authoring environment has no container runtime, so
none was stood up in its exposed and fixed states. Each names its expected exposed and fixed result so
it discriminates when run against a live instance; backlog row 2.26 tracks demonstrating them. Run each
probe from an external vantage, not the service host, and run its positive control (for a token-gated
service, an authorized request that succeeds) so a dead service or a blocked local socket is not
misread as fixed. A transport failure is inconclusive on its own: read the `err` field and confirm the
failure happened while connecting to the target (a connection refusal from that vantage), not because a
local policy blocked the probe or a slow response outlasted `--max-time`. These write-out fields need
curl 7.75.0 or newer, and an IPv6 literal needs brackets in the URL.

```bash
# On the host: these listeners should be bound to loopback or an internal interface, not a wildcard.
# Add the distributed Grid ports (5553, 5556, 5557, 5559) and your Playwright port if you run them.
ss -tlnp | grep -E ':(9222|4442|4443|4444|5555|3000|5900|7900) '   # loopback or internal only
```

For the DevTools, Grid, browserless and Playwright ports, guard the address in the block below so it
forces a real substitution, and read the write-out. Substitute an IP literal, not a name, for the
DevTools probe, because the endpoint rejects a forwarded `Host` that is not an address.

```bash
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
    *) curl -q -g -sS -i --noproxy '*' --connect-timeout 5 --max-time 20 \
         -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:9222/json/version" ;;
  esac
)
```

Exposed, the DevTools probe returns a `200` JSON body containing `webSocketDebuggerUrl`, which is the
whole compromise; a connection refused or a timeout that happened during the connect is consistent with
isolation from that vantage, not proof of the configuration. To check the other services, change the
URL in the block's `curl` line, leaving the guard lines intact, to each port in turn:
`http://$1:4444/status` for a Selenium Grid Router, Hub or Standalone (a `200` JSON `ready` and node
inventory is exposure; the `-i` prints the headers, so a `401` with `WWW-Authenticate: Basic` means the
Router auth is on but the port is still reachable, which is not the fixed state), `http://$1:5555/status`
for a Node, `http://$1:3000/pressure` for browserless (exposed returns a `200` with the load JSON of
CPU, memory, sessions and queue depth; with a `TOKEN` set the same request is rejected, so confirm the
status against your image, repeat with a deliberately wrong token, and confirm a correct token, passed in the query
string as `?token=` followed by your token, returns the JSON), and the Playwright server on the port you configured (`launchServer` uses an ephemeral port
unless you set one; `run-server` takes `--port`), where any HTTP answer means the port is reachable and
is already the finding. The distinguishing behaviour for each is in the cited vendor pages.

## Sources (checked September 2026)

- Chrome DevTools Protocol remote debugging: https://developer.chrome.com/docs/devtools/remote-debugging/
- Chrome DevTools Protocol domains (Runtime, Network, Page): https://chromedevtools.github.io/devtools-protocol/
- Chrome 136 remote-debugging user-data-dir change: https://developer.chrome.com/blog/remote-debugging-port
- Selenium Grid CLI options (host, bind-host, username, password, https-certificate): https://www.selenium.dev/documentation/grid/configuration/cli_options/
- Selenium Grid getting started (components, ports, distributed topology): https://www.selenium.dev/documentation/grid/getting_started/
- Selenium Docker images env vars (SE_START_VNC, SE_VNC_PASSWORD, SE_BIND_HOST, SE_ROUTER_USERNAME): https://github.com/SeleniumHQ/docker-selenium/blob/trunk/ENV_VARIABLES.md
- browserless Docker configuration (TOKEN, ALLOW_FILE_PROTOCOL, port 3000): https://docs.browserless.io/baas/docker/config
- Playwright BrowserType.launchServer and connect: https://playwright.dev/docs/api/class-browsertype
- Playwright Docker (run-server remote connection): https://playwright.dev/docs/docker
