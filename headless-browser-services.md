---
version_basis: {
  "schema": 1,
  "checked": "2026-09-27",
  "documentation_checked": "2026-09",
  "body_sha256": "6be7d8b96c82119f53878c6986aa97d5134eded2c815c4c095f456504a81736e",
  "components": {
    "chromium": {
      "name": "Chromium",
      "basis": "154.0.8037.57",
      "sources": {
        "s087ba883abe3": "https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/chrome/browser/devtools/remote_debugging_server.cc#L69-L158",
        "s65073710f8bd": "https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/chrome/browser/devtools/remote_debugging_server.cc#L160-L282",
        "sc62d44c2dee6": "https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/chrome/browser/devtools/remote_debugging_server.cc#L325-L417",
        "s6e1b34a120d1": "https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/headless/lib/browser/headless_devtools.cc#L31-L145",
        "sdf5f61d9b325": "https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/headless/lib/browser/command_line_handler.cc#L199-L206",
        "s005d90d4912a": "https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/content/public/common/content_switches.cc#L596-L607",
        "s804c1266fb81": "https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/content/browser/devtools/devtools_http_handler.cc#L267-L312",
        "s66b210123ff8": "https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/content/browser/devtools/devtools_http_handler.cc#L459-L630",
        "s1044899c624a": "https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/content/browser/devtools/devtools_http_handler.cc#L811-L880",
        "s1ca85f782546": "https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/content/browser/devtools/devtools_http_handler.cc#L1032-L1055",
        "s0a2a5fec4975": "https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/chrome/browser/devtools/remote_debugging_server.h#L26"
      }
    },
    "cdp": {
      "name": "Chrome DevTools Protocol",
      "basis": "unknown",
      "sources": {
        "se77e8fd82ffd": "https://developer.chrome.com/docs/devtools/remote-debugging/",
        "s523649d3b233": "https://chromedevtools.github.io/devtools-protocol/"
      }
    },
    "chrome-change": {
      "name": "Chrome remote-debugging announcement",
      "basis": "unknown",
      "sources": {
        "s643c9edab288": "https://developer.chrome.com/blog/remote-debugging-port"
      }
    },
    "selenium": {
      "name": "Selenium Grid",
      "basis": "unknown",
      "sources": {
        "sb304923778ab": "https://www.selenium.dev/documentation/grid/configuration/cli_options/",
        "s0a0129b8dd37": "https://www.selenium.dev/documentation/grid/getting_started/"
      }
    },
    "selenium-docker": {
      "name": "Selenium Docker images",
      "basis": "aafe4d6136f3bb5afcd9b7cb691c624516d06e1b",
      "sources": {
        "s992336986b07": "https://github.com/SeleniumHQ/docker-selenium/blob/aafe4d6136f3bb5afcd9b7cb691c624516d06e1b/ENV_VARIABLES.md"
      }
    },
    "browserless": {
      "name": "browserless",
      "basis": "unknown",
      "sources": {
        "sc0a7a8f6c093": "https://docs.browserless.io/enterprise/docker/config"
      }
    },
    "playwright": {
      "name": "Playwright",
      "basis": "unknown",
      "sources": {
        "sc13c2e85f08c": "https://playwright.dev/docs/api/class-browsertype",
        "s94dfef953286": "https://playwright.dev/docs/docker"
      }
    },
    "browserless-token-default": {
      "name": "browserless (open source)",
      "basis": "2.56.7",
      "sources": {
        "s87c144d59098": "https://github.com/browserless/browserless/blob/v2.56.7/src/config.ts#L250",
        "sdf3b808e8920": "https://github.com/browserless/browserless/blob/v2.56.7/src/server.ts#L103-L117",
        "se8b696d56eda": "https://github.com/browserless/browserless/blob/v2.56.7/src/server.ts#L264-L271",
        "sc7973e3e21df": "https://github.com/browserless/browserless/blob/v2.56.7/src/server.ts#L445-L454"
      }
    },
    "browserless-file-fix": {
      "name": "browserless Playwright file-protocol fix",
      "basis": "2.51.0",
      "sources": {
        "s94f1d485c2b7": "https://raw.githubusercontent.com/browserless/browserless/v2.51.0/CHANGELOG.md",
        "s90a20f6566c9": "https://github.com/browserless/browserless/commit/a18a1231ead2ecc4114347d5d1fafd69bffeb735",
        "sf2642da1de49": "https://raw.githubusercontent.com/browserless/browserless/v2.51.0/src/browsers/browsers.playwright.ts",
        "s7ee912fa0a9a": "https://github.com/browserless/browserless/blob/v2.51.0/src/http.ts#L91-L103"
      }
    },
    "browserless-docs": {
      "name": "browserless documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "sa189d41ee219": "https://docs.browserless.io/enterprise/open-source",
        "sf1ec52c41f54": "https://docs.browserless.io/enterprise/utility-functions/pressure"
      }
    },
    "cve-record": {
      "name": "CVE-2026-92811 record",
      "basis": "unknown",
      "sources": {
        "sba82c9b5f230": "https://raw.githubusercontent.com/CVEProject/cvelistV5/b0b0976792a7c9d6d66ee553050c21cb088a0659/cves/2026/92xxx/CVE-2026-92811.json"
      }
    }
  },
  "claims": {
    "cdp-bind": {"text": "Command-line DevTools binds 127.0.0.1, falling back to ::1; stock browser and headless shell have no remote-debugging-address switch.", "components": ["chromium"], "sources": ["chromium:s087ba883abe3", "chromium:s6e1b34a120d1", "chromium:s005d90d4912a"], "status": "REASONED"},
    "cdp-port": {"text": "Explicit nonzero DevTools ports do not fall back to another port; port 0 requests an ephemeral port.", "components": ["chromium"], "sources": ["chromium:s087ba883abe3", "chromium:s6e1b34a120d1"], "status": "REASONED"},
    "cdp-approval": {"text": "Feature-gated approval mode uses DevToolsActivePort or 9222, with requested/ephemeral IPv4 then IPv6 fallback; command-line modes take precedence.", "components": ["chromium"], "sources": ["chromium:s087ba883abe3", "chromium:s65073710f8bd", "chromium:sc62d44c2dee6", "chromium:s0a2a5fec4975"], "status": "REASONED"},
    "cdp-discovery": {"text": "Command-line /json and /json/version disclose debugger URLs; approval-mode 404 does not establish isolation.", "components": ["chromium"], "sources": ["chromium:s66b210123ff8", "chromium:s1ca85f782546"], "status": "REASONED", "verify": [2]},
    "cdp-auth": {"text": "Command-line CDP has no client authentication or password flag; Host and Origin checks do not authenticate clients.", "components": ["chromium"], "sources": ["chromium:s66b210123ff8", "chromium:s1044899c624a"], "status": "REASONED"},
    "cdp-capabilities": {"text": "CDP grants page JavaScript, cookie/credential and tab control; restrict ingress, browser egress and local-file reach.", "components": ["cdp"], "sources": ["cdp:s523649d3b233"], "status": "REASONED"},
    "cdp-private": {"text": "Keep DevTools loopback/private behind authenticated access; inspect forwarders and container namespaces, since publishing cannot reach container loopback.", "components": ["chromium"], "sources": ["chromium:s087ba883abe3", "chromium:s6e1b34a120d1", "chromium:s804c1266fb81"], "status": "REASONED"},
    "cdp-profile": {"text": "Chrome 136 requires non-default user data; pinned desktop branding check excludes normal Chromium, and Chrome for Testing exemption rests on the announcement.", "components": ["chrome-change", "chromium"], "sources": ["chrome-change:s643c9edab288", "chromium:s65073710f8bd"], "status": "REASONED"},
    "cdp-policy": {"text": "RemoteDebuggingAllowed gates browser command-line and approval modes; headless-shell startup lacks the corresponding profile/policy check.", "components": ["chromium"], "sources": ["chromium:s65073710f8bd", "chromium:sc62d44c2dee6", "chromium:s6e1b34a120d1"], "status": "REASONED"},
    "cdp-pipe": {"text": "Pipe mode alone opens no TCP port; supplying a port too can start an independent listener, and pipe access still grants browser control.", "components": ["chromium"], "sources": ["chromium:sc62d44c2dee6", "chromium:s6e1b34a120d1", "chromium:sdf5f61d9b325"], "status": "REASONED"},
    "grid-auth": {"text": "Router username/password are unset by default, including Docker SE_ROUTER_USERNAME and SE_ROUTER_PASSWORD.", "components": ["selenium", "selenium-docker"], "sources": ["selenium:sb304923778ab", "selenium-docker:s992336986b07"], "status": "REASONED"},
    "grid-bind": {"text": "Grid host is usually autodetected; Docker SE_BIND_HOST is unset and historical Grid 3 binds 0.0.0.0. Set and observe a private host with bind-host.", "components": ["selenium", "selenium-docker"], "sources": ["selenium:sb304923778ab", "selenium-docker:s992336986b07"], "status": "REASONED"},
    "grid-ports": {"text": "Router, Hub, Standalone and UI use 4444; Nodes use 5555. Keep all private.", "components": ["selenium"], "sources": ["selenium:s0a0129b8dd37"], "status": "REASONED"},
    "grid-distributed": {"text": "Distributed event bus uses 4442/4443; Distributor, Session Map, bus HTTP and New Session Queue add 5553/5556/5557/5559.", "components": ["selenium"], "sources": ["selenium:sb304923778ab", "selenium:s0a0129b8dd37"], "status": "REASONED"},
    "grid-bus": {"text": "Router Basic auth does not protect the bus; registration-secret validates event messages without encrypting transport, so isolate every participant.", "components": ["selenium"], "sources": ["selenium:sb304923778ab", "selenium:s0a0129b8dd37"], "status": "REASONED"},
    "grid-vnc": {"text": "Docker enables VNC by default on 5900 and noVNC on 7900; replace the example secret password or disable VNC, and avoid passwordless mode.", "components": ["selenium-docker"], "sources": ["selenium-docker:s992336986b07"], "status": "REASONED"},
    "grid-tls": {"text": "Native https-certificate/https-private-key or a TLS proxy protects Router Basic credentials; TLS is not on by default.", "components": ["selenium"], "sources": ["selenium:sb304923778ab"], "status": "REASONED"},
    "browserless-auth": {"text": "Open-source 2.56.7 reads an unset or empty TOKEN as null; no token is generated and endpoints are unauthenticated by default.", "components": ["browserless-token-default", "browserless-docs"], "sources": ["browserless-token-default:s87c144d59098", "browserless-docs:sa189d41ee219"], "status": "REASONED"},
    "browserless-bind": {"text": "browserless uses 3000; publish 127.0.0.1:3000:3000 or keep an internal network with no host mapping.", "components": ["browserless"], "sources": ["browserless:sc0a7a8f6c093"], "status": "REASONED"},
    "browserless-token": {"text": "Use a randomized TOKEN, protect token-bearing connection URLs and logs, and terminate TLS at the fronting layer.", "components": ["browserless"], "sources": ["browserless:sc0a7a8f6c093"], "status": "REASONED"},
    "browserless-file": {"text": "Require browserless 2.51.0 or later containing the pinned Playwright fix, keep ALLOW_FILE_PROTOCOL=false, and run the file-protocol check.", "components": ["browserless", "browserless-file-fix"], "sources": ["browserless:sc0a7a8f6c093", "browserless-file-fix:s94f1d485c2b7", "browserless-file-fix:s90a20f6566c9"], "status": "REASONED"},
    "playwright-auth": {"text": "Playwright server has no password/user model; reachable endpoints grant OS-user control, so bind 127.0.0.1 and protect endpoint URLs.", "components": ["playwright"], "sources": ["playwright:sc13c2e85f08c", "playwright:s94dfef953286"], "status": "REASONED"},
    "playwright-discovery": {"text": "Guide records run-server path / and launchServer random paths discoverable through GET /json; a secret path is not an access boundary.", "components": ["playwright"], "sources": ["playwright:sc13c2e85f08c", "playwright:s94dfef953286"], "status": "REASONED"},
    "playwright-tls": {"text": "Authenticate WebSocket upgrades and discovery at a wss proxy; connect accepts custom headers and the server supplies no native TLS.", "components": ["playwright"], "sources": ["playwright:sc13c2e85f08c", "playwright:s94dfef953286"], "status": "REASONED"},
    "debug-bypass": {"text": "A separately forwarded Chromium debug endpoint bypasses front-tool authentication; keep 9222 unpublished and restrict browser egress.", "components": ["cdp", "selenium", "browserless", "playwright"], "sources": ["cdp:s523649d3b233", "selenium:s0a0129b8dd37", "browserless:sc0a7a8f6c093", "playwright:sc13c2e85f08c"], "status": "REASONED"},
    "verify-listeners": {"text": "Inventory every listener, including distributed Grid and configured Playwright ports, and require intended loopback/private addresses.", "components": ["chromium", "selenium", "selenium-docker", "browserless", "playwright"], "sources": ["chromium:s087ba883abe3", "chromium:s6e1b34a120d1", "selenium:sb304923778ab", "selenium:s0a0129b8dd37", "selenium-docker:s992336986b07", "browserless:sc0a7a8f6c093", "playwright:sc13c2e85f08c"], "status": "REASONED", "verify": [1]},
    "verify-cdp": {"text": "External command-line CDP returns 200 with webSocketDebuggerUrl when forwarded; fixed isolation retains a working local control. Approval-mode 404 is inconclusive.", "components": ["chromium"], "sources": ["chromium:s804c1266fb81", "chromium:s66b210123ff8"], "status": "REASONED", "verify": [2]},
    "verify-grid": {"text": "Grid /status returns ready/node JSON when exposed; Router 401 with Basic challenge shows auth but still proves reachability. Probe Nodes separately.", "components": ["selenium"], "sources": ["selenium:sb304923778ab", "selenium:s0a0129b8dd37"], "status": "REASONED", "verify": [2]},
    "verify-browserless": {"text": "For open-source 2.56.7, expect /pressure load JSON without a configured TOKEN; with a nonempty TOKEN, expect 401 for missing/wrong tokens and JSON for a correct-token control.", "components": ["browserless-token-default", "browserless-docs"], "sources": ["browserless-token-default:s87c144d59098", "browserless-token-default:sdf3b808e8920", "browserless-token-default:se8b696d56eda", "browserless-token-default:sc7973e3e21df", "browserless-docs:sa189d41ee219", "browserless-docs:sf1ec52c41f54"], "status": "REASONED", "verify": [2]},
    "verify-playwright": {"text": "Any HTTP answer proves Playwright reachability; launchServer uses an ephemeral port unless set, while run-server takes --port.", "components": ["playwright"], "sources": ["playwright:sc13c2e85f08c", "playwright:s94dfef953286"], "status": "REASONED", "verify": [2]},
    "browserless-file-cve": {"text": "CVE-2026-92811 describes authenticated Playwright file reads despite ALLOW_FILE_PROTOCOL=false; its affected range 1.44.0 through 2.56.7 conflicts with the vendor 2.51.0 fix.", "components": ["browserless-file-fix", "cve-record"], "sources": ["cve-record:sba82c9b5f230", "browserless-file-fix:s94f1d485c2b7", "browserless-file-fix:s90a20f6566c9"], "status": "REASONED"},
    "verify-browserless-file": {"text": "With a valid token on every enabled Playwright WebSocket route, confirm HTTP navigation first, then attempt a readable container canary: exposed returns contents; fixed refuses with a blocked-URL policy reason.", "components": ["browserless-file-fix", "cve-record"], "sources": ["cve-record:sba82c9b5f230", "browserless-file-fix:sf2642da1de49", "browserless-file-fix:s7ee912fa0a9a"], "status": "REASONED"}
  }
}
---
# Headless browser services: Chrome DevTools Protocol, Selenium Grid, browserless, and Playwright server

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-27; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| cdp-bind: Command-line DevTools binds 127.0.0.1, falling back to ::1; stock browser and headless shell have no remote-debugging-address switch. | Chromium 154.0.8037.57 | REASONED |
| cdp-port: Explicit nonzero DevTools ports do not fall back to another port; port 0 requests an ephemeral port. | Chromium 154.0.8037.57 | REASONED |
| cdp-approval: Feature-gated approval mode uses DevToolsActivePort or 9222, with requested/ephemeral IPv4 then IPv6 fallback; command-line modes take precedence. | Chromium 154.0.8037.57 | REASONED |
| cdp-discovery: Command-line /json and /json/version disclose debugger URLs; approval-mode 404 does not establish isolation. | Chromium 154.0.8037.57 | REASONED |
| cdp-auth: Command-line CDP has no client authentication or password flag; Host and Origin checks do not authenticate clients. | Chromium 154.0.8037.57 | REASONED |
| cdp-capabilities: CDP grants page JavaScript, cookie/credential and tab control; restrict ingress, browser egress and local-file reach. | Chrome DevTools Protocol unknown | REASONED |
| cdp-private: Keep DevTools loopback/private behind authenticated access; inspect forwarders and container namespaces, since publishing cannot reach container loopback. | Chromium 154.0.8037.57 | REASONED |
| cdp-profile: Chrome 136 requires non-default user data; pinned desktop branding check excludes normal Chromium, and Chrome for Testing exemption rests on the announcement. | Chrome remote-debugging announcement unknown; Chromium 154.0.8037.57 | REASONED |
| cdp-policy: RemoteDebuggingAllowed gates browser command-line and approval modes; headless-shell startup lacks the corresponding profile/policy check. | Chromium 154.0.8037.57 | REASONED |
| cdp-pipe: Pipe mode alone opens no TCP port; supplying a port too can start an independent listener, and pipe access still grants browser control. | Chromium 154.0.8037.57 | REASONED |
| grid-auth: Router username/password are unset by default, including Docker SE_ROUTER_USERNAME and SE_ROUTER_PASSWORD. | Selenium Grid unknown; Selenium Docker images aafe4d6136f3bb5afcd9b7cb691c624516d06e1b | REASONED |
| grid-bind: Grid host is usually autodetected; Docker SE_BIND_HOST is unset and historical Grid 3 binds 0.0.0.0. Set and observe a private host with bind-host. | Selenium Grid unknown; Selenium Docker images aafe4d6136f3bb5afcd9b7cb691c624516d06e1b | REASONED |
| grid-ports: Router, Hub, Standalone and UI use 4444; Nodes use 5555. Keep all private. | Selenium Grid unknown | REASONED |
| grid-distributed: Distributed event bus uses 4442/4443; Distributor, Session Map, bus HTTP and New Session Queue add 5553/5556/5557/5559. | Selenium Grid unknown | REASONED |
| grid-bus: Router Basic auth does not protect the bus; registration-secret validates event messages without encrypting transport, so isolate every participant. | Selenium Grid unknown | REASONED |
| grid-vnc: Docker enables VNC by default on 5900 and noVNC on 7900; replace the example secret password or disable VNC, and avoid passwordless mode. | Selenium Docker images aafe4d6136f3bb5afcd9b7cb691c624516d06e1b | REASONED |
| grid-tls: Native https-certificate/https-private-key or a TLS proxy protects Router Basic credentials; TLS is not on by default. | Selenium Grid unknown | REASONED |
| browserless-auth: Open-source 2.56.7 reads an unset or empty TOKEN as null; no token is generated and endpoints are unauthenticated by default. | browserless (open source) 2.56.7; browserless documentation (rolling) unknown | REASONED |
| browserless-bind: browserless uses 3000; publish 127.0.0.1:3000:3000 or keep an internal network with no host mapping. | browserless unknown | REASONED |
| browserless-token: Use a randomized TOKEN, protect token-bearing connection URLs and logs, and terminate TLS at the fronting layer. | browserless unknown | REASONED |
| browserless-file: Require browserless 2.51.0 or later containing the pinned Playwright fix, keep ALLOW_FILE_PROTOCOL=false, and run the file-protocol check. | browserless unknown; browserless Playwright file-protocol fix 2.51.0 | REASONED |
| playwright-auth: Playwright server has no password/user model; reachable endpoints grant OS-user control, so bind 127.0.0.1 and protect endpoint URLs. | Playwright unknown | REASONED |
| playwright-discovery: Guide records run-server path / and launchServer random paths discoverable through GET /json; a secret path is not an access boundary. | Playwright unknown | REASONED |
| playwright-tls: Authenticate WebSocket upgrades and discovery at a wss proxy; connect accepts custom headers and the server supplies no native TLS. | Playwright unknown | REASONED |
| debug-bypass: A separately forwarded Chromium debug endpoint bypasses front-tool authentication; keep 9222 unpublished and restrict browser egress. | Chrome DevTools Protocol unknown; Selenium Grid unknown; browserless unknown; Playwright unknown | REASONED |
| verify-listeners: Inventory every listener, including distributed Grid and configured Playwright ports, and require intended loopback/private addresses. | Chromium 154.0.8037.57; Selenium Grid unknown; Selenium Docker images aafe4d6136f3bb5afcd9b7cb691c624516d06e1b; browserless unknown; Playwright unknown | REASONED |
| verify-cdp: External command-line CDP returns 200 with webSocketDebuggerUrl when forwarded; fixed isolation retains a working local control. Approval-mode 404 is inconclusive. | Chromium 154.0.8037.57 | REASONED |
| verify-grid: Grid /status returns ready/node JSON when exposed; Router 401 with Basic challenge shows auth but still proves reachability. Probe Nodes separately. | Selenium Grid unknown | REASONED |
| verify-browserless: For open-source 2.56.7, expect /pressure load JSON without a configured TOKEN; with a nonempty TOKEN, expect 401 for missing/wrong tokens and JSON for a correct-token control. | browserless (open source) 2.56.7; browserless documentation (rolling) unknown | REASONED |
| verify-playwright: Any HTTP answer proves Playwright reachability; launchServer uses an ephemeral port unless set, while run-server takes --port. | Playwright unknown | REASONED |
| browserless-file-cve: CVE-2026-92811 describes authenticated Playwright file reads despite ALLOW_FILE_PROTOCOL=false; its affected range 1.44.0 through 2.56.7 conflicts with the vendor 2.51.0 fix. | browserless Playwright file-protocol fix 2.51.0; CVE-2026-92811 record unknown | REASONED |
| verify-browserless-file: With a valid token on every enabled Playwright WebSocket route, confirm HTTP navigation first, then attempt a readable container canary: exposed returns contents; fixed refuses with a blocked-URL policy reason. | browserless Playwright file-protocol fix 2.51.0; CVE-2026-92811 record unknown | REASONED |
<!-- version-basis:end -->

Agent and scraping stacks run these to drive a real browser, and that is exactly the exposure: whoever
reaches the endpoint gets JavaScript execution inside the pages the browser opens, the profile's cookie
jar, and a pivot from the service's own network position, including internal panels and the cloud
metadata endpoint ([egress-metadata.md](egress-metadata.md)). An exposed browser automation port is
usually unauthenticated code execution and credential theft, not just data. None of these command-line
automation endpoints requires authentication by default. Inspect the actual listeners and any
forwarders: the headline mistake is letting the network reach the port at all. Restrict the
service's own egress as well as its inbound reach, front the listeners per
[fronting-auth.md](fronting-auth.md), [nginx.md](nginx.md) or [caddy.md](caddy.md), keep them private
per [docker.md](docker.md) and [tunnels.md](tunnels.md), and treat every connection URL as a secret
([secrets.md](secrets.md)).

## Chrome DevTools Protocol

A Chrome or Chromium started with `--remote-debugging-port=9222` speaks the DevTools Protocol without
client authentication. At `154.0.8037.57` (commit
`73c14f6228d7cd537c855007e8f88678969cc0eb`), the full browser, including `--headless`, and
`chrome-headless-shell` bind that TCP listener only to `127.0.0.1`, trying `::1` if the IPv4 bind
fails. Neither has a `--remote-debugging-address` switch at this version. A non-loopback DevTools
listener therefore means a forwarder or a modified build, not an address flag on either stock binary.
Publishing a container port cannot reach a socket that is still loopback-bound inside the container;
inspect the process that actually binds the published port, not only the compose file.

For an explicit nonzero port, both try the same port on IPv6 and fail to start the listener if both
binds fail. They do not silently choose another port when `9222` is busy. Explicit
`--remote-debugging-port=0` requests an ephemeral port. The full browser also has a separate,
feature-gated approval mode enabled through `chrome://inspect`: it reads the previous port from
`DevToolsActivePort` or starts with `9222`. For a nonzero requested port, it tries IPv4 at that port,
IPv4 at port `0`, IPv6 at the requested port, and IPv6 at port `0`, stopping at the first success.
This mode asks for user approval; the command-line port and pipe modes take precedence over it. Inspect the actual listening address and port in
`ss -tlnp` and the `DevTools listening on` stderr message, plus `DevToolsActivePort` when written,
rather than assuming every debugging session uses `9222`.

In command-line port mode, `GET /json` lists target WebSocket debugger URLs and `/json/version`
returns the browser WebSocket debugger URL. A client on that socket has `Runtime.evaluate`
(arbitrary JavaScript in pages), the Network domain (cookies and credentials), and control of tabs.
The Host and WebSocket Origin checks are not client authentication. There is no password flag for this
mode, so keep the port on loopback and reach it over an SSH tunnel ([tunnels.md](tunnels.md)), or use
an authenticating proxy on a private network. Never expose an unauthenticated forward or proxy.
Approval mode rejects the JSON discovery routes with `404`, so that status is not proof of isolation.

The Chrome 136 change ignores `--remote-debugging-port` and `--remote-debugging-pipe` when they
would debug the default user data directory. At the pinned source this check applies to
`GOOGLE_CHROME_BRANDING` desktop builds on Windows, macOS and Linux, not normal Chromium builds
(a test-only hook can enable it there). Use an explicit, non-default `--user-data-dir`.
The `RemoteDebuggingAllowed` enterprise policy can disable remote debugging: the browser checks
`prefs::kDevToolsRemoteDebuggingAllowed` before starting either command-line mode or approval mode.
The separate headless-shell startup path has no corresponding profile or policy check.
The existing Chrome vendor announcement says Chrome for Testing retains the older behaviour; the
source subset reviewed here does not establish its build branding, so that exemption rests on the
vendor announcement, not an inferred branding equivalence.

`--remote-debugging-pipe` uses pipes, not a TCP listener. Supplying it alone opens no DevTools TCP
port; supplying `--remote-debugging-port` as well can still start the independent TCP listener in
both the browser and headless shell. Pipe access still grants browser control.

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

Open-source browserless `2.56.7` listens on port `3000` and reads `TOKEN` as
`process.env.TOKEN || null`: an unset or empty value becomes `null`, with no generated token.
Its default is unauthenticated endpoints, including routes that run caller-supplied browser code.
The current Docker configuration reference agrees; the older quickstart's generated-token claim
does not match this release. The current reference documents the same default for Enterprise,
but its private image was not inspected or run here, so equivalence is not source-verified.
Always set a long, randomized `TOKEN` (never a vendor sample, never committed), and publish the port to
loopback (`-p 127.0.0.1:3000:3000`) or keep it on an internal container network with no host mapping.
The token is presented in the connection URL, so proxy and access logs become credential stores; front
the service with TLS so it is unreadable in transit, and handle the token as [secrets.md](secrets.md)
describes.

Require browserless **2.51.0 or later containing
[fix a18a1231ead2ecc4114347d5d1fafd69bffeb735](https://github.com/browserless/browserless/commit/a18a1231ead2ecc4114347d5d1fafd69bffeb735)**,
and keep `ALLOW_FILE_PROTOCOL=false`. Earlier builds can allow authenticated Playwright WebSocket
clients to read container files despite that setting (CVE-2026-92811). The
[v2.51.0 changelog](https://raw.githubusercontent.com/browserless/browserless/v2.51.0/CHANGELOG.md)
records the fix; the [CVE record](https://raw.githubusercontent.com/CVEProject/cvelistV5/b0b0976792a7c9d6d66ee553050c21cb088a0659/cves/2026/92xxx/CVE-2026-92811.json)
lists a conflicting affected range of 1.44.0 through 2.56.7 inclusive, so run the file-protocol check
below rather than rely on the version alone. browserless terminates no TLS of its own, so the
fronting layer is where HTTPS lives.

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
Selenium, or Playwright browser, though a fronting tool may block them (browserless requires the
fixed version and setting described above, plus the file-protocol check below).
One path ties the four together: Selenium, Playwright and browserless all drive Chromium over the
DevTools Protocol in the common case, so a debug port opened "just to inspect" a Node or a browserless
container (a stray `-p 9222:9222`) bypasses whatever authentication the front tool has. Keep 9222
unpublished wherever these run.

## Verify

Every live check below is **REASONED**, not demonstrated: the authoring host forbids opening listeners
without an isolated network namespace, and has none. No exposed or fixed service was run.
Each names its expected exposed and fixed result so
it discriminates when run against a live instance, based on the cited vendor documentation and pinned sources. Run each
probe from an external vantage, not the service host, and run its positive control (for a token-gated
service, an authorized request that succeeds) so a dead service or a blocked local socket is not
misread as fixed. A transport failure is inconclusive on its own: read the `err` field and confirm the
failure happened while connecting to the target (a connection refusal from that vantage), not because a
local policy blocked the probe or a slow response outlasted `--max-time`. These write-out fields need
curl 7.75.0 or newer, and an IPv6 literal needs brackets in the URL.

```bash
# REASONED: listener inventory follows the cited vendor documentation and pinned sources;
# the authoring host lacks an isolated network namespace for authorized live listeners.
# On the host: these listeners should be bound to loopback or an internal interface, not a wildcard.
# Add the distributed Grid ports (5553, 5556, 5557, 5559) and your Playwright port if you run them.
ss -tlnp   # read every listener; 9222/4442/4443/4444/5555/3000/5900/7900: loopback or internal only
```

**REASONED DevTools listener check:** for the pinned stock browser and headless shell, expect only
`127.0.0.1` or `::1` for the DevTools TCP listener. Inspect both address families and every actual
port, including ephemeral ports, plus forwarders in the host and container network namespaces.
Exposed, a forwarder supplies a reachable non-loopback listener; fixed, no unauthenticated external
path remains while the local browser endpoint still answers. The pinned socket factories and HTTP
handler below establish these expected results.

For the DevTools, Grid, browserless and Playwright ports, guard the address in the block below so it
forces a real substitution, and read the write-out. Replace `9222` in the curl URL with the actual
externally forwarded port if different. For the local positive control, run the same guarded block
inside the browser's network namespace with its actual loopback address and DevTools port.
Substitute an IP literal, not a name, for the DevTools probe, because the endpoint rejects a forwarded
`Host` that is not an address or localhost.

REASONED: following block; external discovery/authentication probes and local positive controls follow the cited vendor documentation and pinned sources; the authoring host has no isolated network namespace for authorized live listeners.

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

**REASONED command-line DevTools port probe:** exposed through an unauthenticated forwarder, it returns
a `200` JSON body containing `webSocketDebuggerUrl`. Fixed, the external request cannot reach that
endpoint while the local positive control still returns it. A `404` from approval mode is not a pass.
A connection refused or a timeout that happened during the connect is consistent with
isolation from that vantage, not proof of the configuration. To check the other services, change the
URL in the block's `curl` line, leaving the guard lines intact, to each port in turn:
`http://$1:4444/status` for a Selenium Grid Router, Hub or Standalone (a `200` JSON `ready` and node
inventory is exposure; the `-i` prints the headers, so a `401` with `WWW-Authenticate: Basic` means the
Router auth is on but the port is still reachable, which is not the fixed state), `http://$1:5555/status`
for a Node, `http://$1:3000/pressure` for open-source browserless `2.56.7` (with `TOKEN` unset or empty,
expect `200` with load JSON; with a nonempty `TOKEN`, expect `401` for both the tokenless request and
a deliberately wrong `?token=` value, then confirm the correct token returns the load JSON).
These are REASONED expectations from the cited configuration, API documentation and HTTP rejection
handler, not live observations; this authoring environment has no container runtime and cannot
fetch runtime dependencies. A `401` establishes authentication, not network isolation: the fixed
deployment must also deny the external path while an authorized internal control still succeeds.
Pass the correct token through curl's stdin configuration, not a literal URL in shell history or
argv. For the Playwright server on the port you configured (`launchServer` uses an ephemeral port
unless you set one; `run-server` takes `--port`), any HTTP answer means the port is reachable and
is already the finding. The distinguishing behaviour for each is in the cited vendor pages.

**REASONED browserless file-protocol check:** no live instance was tested: the authoring host forbids
opening listeners without an isolated network namespace, and has none. With
`ALLOW_FILE_PROTOCOL=false`, use a valid token and a compatible Playwright client on each enabled
Playwright WebSocket route. The v2.51.0
[route table](https://github.com/browserless/browserless/blob/v2.51.0/src/http.ts#L91-L103) defines
`/chromium/playwright`, `/chrome/playwright`, `/edge/playwright`, `/firefox/playwright` and
`/webkit/playwright`, plus the `/playwright/chromium`, `/playwright/chrome`, `/playwright/firefox` and
`/playwright/webkit` aliases; test every one that is enabled. First confirm ordinary HTTP navigation
succeeds. Then call `page.goto('file:///tmp/secureconfig-canary.txt')` against a harmless canary with
known contents already confirmed readable by the browser process inside the container. On an exposed
build, expect `page.evaluate(() => document.body.innerText)` to return the canary contents. The
[fixed implementation](https://raw.githubusercontent.com/browserless/browserless/v2.51.0/src/browsers/browsers.playwright.ts)
refuses the navigation and closes the session with a blocked-URL policy reason. Confirm that reason;
missing files, authentication failures, connection failures, and timeouts are inconclusive. Passing
`/pressure` or a CDP-only check does not establish Playwright enforcement.

## Sources (checked September 2026)

- Chromium 154.0.8037.57 browser loopback factories and approval-mode port fallback: https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/chrome/browser/devtools/remote_debugging_server.cc#L69-L158
- Chromium 154.0.8037.57 browser branding/profile and policy checks; approval-mode startup, with the `kDefaultDevToolsPort` 9222 fallback: https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/chrome/browser/devtools/remote_debugging_server.cc#L160-L282 and https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/chrome/browser/devtools/remote_debugging_server.h#L26
- Browser command-line pipe/port startup and precedence over approval mode (Chromium 154.0.8037.57): https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/chrome/browser/devtools/remote_debugging_server.cc#L325-L417
- Headless-shell loopback factory and pipe/port startup (Chromium 154.0.8037.57): https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/headless/lib/browser/headless_devtools.cc#L31-L145
- Headless-shell command-line port and pipe handling (Chromium 154.0.8037.57): https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/headless/lib/browser/command_line_handler.cc#L199-L206
- Content pipe and port switch definitions (Chromium 154.0.8037.57): https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/content/public/common/content_switches.cc#L596-L607
- Actual bound address, stderr endpoint and DevToolsActivePort output (Chromium 154.0.8037.57): https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/content/browser/devtools/devtools_http_handler.cc#L267-L312
- Host check, JSON discovery, approval-mode 404 and browser WebSocket URL (Chromium 154.0.8037.57): https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/content/browser/devtools/devtools_http_handler.cc#L459-L630
- WebSocket Origin check, approval mode and unauthenticated command-line mode (Chromium 154.0.8037.57): https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/content/browser/devtools/devtools_http_handler.cc#L811-L880
- Target WebSocket URL serialization (Chromium 154.0.8037.57): https://github.com/chromium/chromium/blob/73c14f6228d7cd537c855007e8f88678969cc0eb/content/browser/devtools/devtools_http_handler.cc#L1032-L1055
- Chrome DevTools Protocol remote debugging: https://developer.chrome.com/docs/devtools/remote-debugging/
- Chrome DevTools Protocol domains (Runtime, Network, Page): https://chromedevtools.github.io/devtools-protocol/
- Chrome 136 user-data-dir change and Chrome for Testing exemption: https://developer.chrome.com/blog/remote-debugging-port
- Selenium Grid CLI options (host, bind-host, username, password, https-certificate): https://www.selenium.dev/documentation/grid/configuration/cli_options/
- Selenium Grid getting started (components, ports, distributed topology): https://www.selenium.dev/documentation/grid/getting_started/
- Selenium Docker images env vars (SE_START_VNC, SE_VNC_PASSWORD, SE_BIND_HOST, SE_ROUTER_USERNAME): https://github.com/SeleniumHQ/docker-selenium/blob/aafe4d6136f3bb5afcd9b7cb691c624516d06e1b/ENV_VARIABLES.md
- browserless Docker configuration (TOKEN, ALLOW_FILE_PROTOCOL, port 3000): https://docs.browserless.io/enterprise/docker/config
- CVE-2026-92811 record (affected range 1.44.0 through 2.56.7 inclusive; conflicts with the vendor fix record): https://raw.githubusercontent.com/CVEProject/cvelistV5/b0b0976792a7c9d6d66ee553050c21cb088a0659/cves/2026/92xxx/CVE-2026-92811.json
- browserless 2.51.0 Playwright WebSocket route table: https://github.com/browserless/browserless/blob/v2.51.0/src/http.ts#L91-L103
- browserless 2.51.0 changelog (Playwright WebSocket file-protocol fix): https://raw.githubusercontent.com/browserless/browserless/v2.51.0/CHANGELOG.md
- browserless 2.51.0 pinned Playwright file-protocol fix a18a1231ead2ecc4114347d5d1fafd69bffeb735 (PR #5407): https://github.com/browserless/browserless/commit/a18a1231ead2ecc4114347d5d1fafd69bffeb735
- browserless 2.51.0 Playwright WebSocket enforcement and blocked-URL policy close: https://raw.githubusercontent.com/browserless/browserless/v2.51.0/src/browsers/browsers.playwright.ts
- browserless 2.56.7 TOKEN initialization: https://github.com/browserless/browserless/blob/v2.56.7/src/config.ts#L250
- browserless 2.56.7 HTTP and WebSocket authentication rejection: https://github.com/browserless/browserless/blob/v2.56.7/src/server.ts#L103-L117
- browserless 2.56.7 HTTP route authentication dispatch: https://github.com/browserless/browserless/blob/v2.56.7/src/server.ts#L264-L271
- browserless 2.56.7 WebSocket route authentication dispatch: https://github.com/browserless/browserless/blob/v2.56.7/src/server.ts#L445-L454
- browserless open-source Docker default and management endpoints (rolling documentation, checked September 2026): https://docs.browserless.io/enterprise/open-source
- browserless pressure API request and response (rolling documentation, checked September 2026): https://docs.browserless.io/enterprise/utility-functions/pressure
- Playwright BrowserType.launchServer and connect: https://playwright.dev/docs/api/class-browsertype
- Playwright Docker (run-server remote connection): https://playwright.dev/docs/docker
