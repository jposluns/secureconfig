# Control patterns for applications not yet covered

secureconfig ships service-specific guides, but most deployments run at least one application
without one. This document is the bridge: it distils the control patterns that recur across the
whole corpus into a single reference, so a human or an AI assistant can run an alignment
assessment of any self-hosted application against them. Use it when your application is not in
the guides. Every entry states the control, why it matters, and how to check your own app against
it. Nothing here is product-specific; every example is a pattern, not a flag.

## 1. Network exposure and binding

- **Control:** Bind to loopback (`127.0.0.1`) or a private interface by default. Keep admin and
  data ports off the open internet entirely. A surface that is deliberately public goes through a
  TLS-terminating layer, with authentication enforced somewhere: the app's own login, or a
  fronting layer where the app has none. A service meant to be open to everyone, such as a public
  site, still terminates TLS but need not add a login. Reach admin surfaces over SSH forwarding, a
  tailnet, or an identity-aware proxy, not the open internet.
- **Why:** A port bound to `0.0.0.0` on an internet-facing host is found by routine scanning
  within minutes, and direct access to a backend bypasses whatever authentication a fronting layer
  adds.
- **Check:** Find the bind-address setting and its current value. Run `ss -tlnp`: any line showing
  `0.0.0.0` or `[::]` for this app is reachable from every network the host is on unless a firewall
  blocks it. From an outside network, connect to each port over IPv4 and IPv6: a port that should
  be private must be refused or filtered, and a port that is deliberately public must answer only
  over TLS and enforce whatever authentication that surface requires. Confirm the backend cannot be
  reached directly by IP, skipping the fronting layer.

## 2. Secondary and hidden listeners

- **Control:** Inventory every port the application opens, not just the one you configured.
  Metrics, admin APIs, debug endpoints, clustering, replication, and backing-store ports
  frequently bind separately, often on all interfaces even when the main port is locked down.
  Assess each listener independently.
- **Why:** A guarded front door means nothing if the backing store, debug console, or metrics
  endpoint is published beside it. These listeners are forgotten because they are not in the
  quickstart.
- **Check:** Run `ss -tlnp` (and `ss -ulnp` for UDP) before and after starting the app, and diff.
  On the host this shows host-namespace and published ports only; for a containerized app also run
  `ss` inside the container's own network namespace (for example `docker exec <container> ss
  -tlnp`) and read its published-port list, since a port open only inside the container never
  appears on the host. For each listener, answer: what is it, does it authenticate, and what
  interface is it bound to? Search the app's docs for "metrics", "admin", "debug", "cluster", and
  "replication" ports. Treat any listener you cannot explain as exposed until proven otherwise.

## 3. Authentication and default credentials

- **Control:** Every surface requires a login. Never run with blank, well-known, or
  vendor-default credentials. Rotate any auto-generated initial secret immediately after first
  login. Complete first-run setup before the app is reachable by anyone else.
- **Why:** Default and blank credentials are tried by scanners at scale, and an unclaimed
  first-run installer belongs to whoever reaches it first.
- **Check:** Open the UI and API in a fresh session with no credentials: is anything readable or
  writable? Try the documented default account if the vendor ships one. Confirm the setup wizard
  has completed and cannot be re-triggered. Confirm the initial or generated credentials no
  longer work after rotation.

## 4. Registration, tenancy, and visibility

- **Control:** Disable self-service sign-up on private deployments. Default new resources to
  private, not "internal" or "public". Establish exactly what each visibility tier means,
  including tenant and organization boundaries, before relying on it.
- **Why:** Open registration turns "authenticated users only" into public access, and "internal"
  often means every registered account rather than the intended team.
- **Check:** Logged out, is there a working register path in the UI or the API? Create a resource
  with default settings, then fetch its URL from a logged-out session, from an unrelated
  low-privilege account, and from another tenant where applicable.

## 5. Multi-factor authentication

- **Control:** Enforce MFA on administrative accounts, and on all accounts where the app supports
  it. When authentication is delegated to SSO, enforce MFA at the identity provider and close
  alternative local login paths.
- **Why:** Credential stuffing and password reuse defeat single-factor login regardless of
  password policy, and an unprotected local login undermines the identity-provider policy.
- **Check:** Is MFA required, or merely available? Log in as an admin with password only and
  confirm a second factor is demanded. Confirm enforcement covers existing accounts, local login,
  and recovery paths. If SSO is in use, confirm the provider policy applies to this application.

## 6. Transport security

- **Control:** Serve every non-loopback connection over TLS with a valid certificate. Never
  disable certificate verification in clients, agents, or scripts to make an error go away.
  Terminate TLS at the reverse proxy or at the app, but somewhere. Protect backend hops that
  cross untrusted networks.
- **Why:** Plaintext transport exposes credentials and session tokens to anyone on the path, and
  disabled verification silently accepts any interceptor, which is worse than the error it hides.
- **Check:** Connect to each endpoint and confirm the certificate is valid for the hostname. Grep
  deployment configs and scripts for verification-off patterns such as `verify=false`,
  `insecure`, or `-k`, and justify or remove each hit. Confirm the plain-HTTP port redirects or
  is closed. Inspect proxy-to-app and app-to-dependency connections, not just the front door.

## 7. File and path access

- **Control:** Scope what the app serves or reads to the narrowest directory that works. Keep
  secret paths (key material, config with credentials, `.git`, home directories, backups) out of
  every served root entirely, since exclusion is the only control that does not depend on a deny
  rule. Treat shared caches or artifact stores served by URL as public to anyone who can guess the
  URL unless access control is verified.
- **Why:** Apps that serve files, render previews, or proxy paths will serve whatever lives inside
  their configured root, including a config file or dotfile, unless a specific deny rule stops
  them, and cross-user caches leak one user's content to another.
- **Check:** Enumerate every setting that names a directory the app serves or indexes, and confirm
  no secret material lives under those roots. Where the app relies on a deny rule for dotfiles or
  config, request such a path through the app and confirm refusal; where it does not, confirm the
  sensitive files are simply not under any served root. Use harmless test files to probe traversal
  and symlink behaviour. As user B, fetch an object created by user A and confirm access control
  applies, not just URL obscurity.

## 8. Secret handling

- **Control:** Keep secrets out of container images, repositories, and state artifacts (Terraform
  state, kubeconfigs, CI logs, shell history). Deliver them by environment variable, mounted
  file, or a secret manager, and restrict read access to the processes and people that need them.
  Treat unavoidable secret-bearing state as sensitive in its own right.
- **Why:** Images and repos are copied, cached, and shared far beyond their original audience. A
  secret that lands in one is effectively published, and rotation is the only fix.
- **Check:** Search the repo and image layers for credential patterns (keys, tokens, connection
  strings with passwords). List who and what can read the state files, kubeconfigs, and backups
  the deployment produces. Confirm mounted secret files are owner-only. If a secret was ever
  committed, confirm it was rotated, not just deleted from the tree.

## 9. API and automation surfaces

- **Control:** Treat API keys, webhook endpoints, machine tokens, and service accounts as a
  separate authentication surface from interactive login. Each authenticates independently, is
  scoped to least privilege, and is revocable. Webhook receivers verify a signature or shared
  secret, not just an unguessable URL. Note that auth behaviour on these surfaces often changes
  between versions.
- **Why:** MFA on the login page does not protect an API that accepts a static token, and
  automation surfaces often bypass MFA and session timeouts, providing persistent access.
- **Check:** Enumerate the non-interactive entry points: APIs, webhook receivers, agent
  registration. For a token-authenticated API, call it without credentials and confirm refusal,
  then with a valid but under-scoped credential and confirm the scope holds. For a webhook
  receiver, send a request with a missing or wrong signature and confirm it is rejected before any
  processing, since these validate a payload signature or shared secret rather than a scoped
  credential. Confirm revocation works for each. Record the deployed version and check the
  vendor's notes for auth changes affecting these surfaces.

## 10. Container and host posture

- **Control:** Never mount the container runtime socket into a container unless that container is
  explicitly trusted with control of the host. In the default rootful configuration, socket access
  is root-equivalent on the host; a rootless runtime narrows the blast radius to that user but does
  not make it safe. Avoid privileged mode, broad host mounts, and unneeded capabilities, and run as
  a non-root user. Filter published container ports at the host firewall, and verify the firewall
  actually applies to them.
- **Why:** Container port publishing can bypass or precede host firewall rules depending on the
  stack, silently exposing ports you believed were filtered. A runtime socket in a compromised
  container converts app compromise into host compromise.
- **Check:** Inspect the container spec for runtime socket mounts (a path ending in a runtime
  socket such as `docker.sock`), broad host mounts (a host path such as `/`, `/var`, or `/etc`
  bound into the container), privileged mode, and added capabilities (for example `SYS_ADMIN`).
  Confirm the app runs as a non-root UID. From an external host, scan the published ports over
  IPv4 and IPv6 and confirm the firewall behaves as intended for each.

## 11. Verify discipline

- **Control:** Every hardening claim ends with a check that proves it. Inventory listeners, probe
  each surface unauthenticated from an untrusted vantage point, confirm refusal, and pair every
  negative result with a positive control so a pass is attributable to the control, not to a
  broken probe. A check claims exactly what it demonstrates, no more.
- **Why:** Configuration states intent; only observation states fact. A probe that fails for the
  wrong reason (typo, wrong port, a filter in between) produces a false pass, and a login page
  proves nothing about the API beside it.
- **Check:** Reconcile every `ss -tlnp` line against your listener inventory. Probe each surface
  with a fresh client carrying no cookies, tokens, or inherited credentials, and judge refusal by
  response content, not status code alone. Pair each result with a positive control that fits the
  claim: for an access check, repeat with valid credentials and confirm success; for a
  network-isolation check, confirm the surface is reachable from its intended vantage point while
  refused from outside, so a failure there is the control working and not a broken probe. Record
  target, version, vantage point, expected result, and observed result for each check.

## How to use this

Go control by control. Decide whether each applies to your application; if it does not (no
file-serving path, no container, no API), record why and move on. An assessment is complete when
every control has one of three dispositions: applied and verified, not applicable with a stated
reason, or accepted risk with an owner. Missing evidence is not a pass. When a check fails, fix
and re-run it; the verified probe, not the config edit, closes the item. Retest after changes to
version, networking, or authentication.

If the application sees enough use to deserve its own service-specific guide, request one through
the requests directory (https://github.com/jposluns/secureconfig/tree/main/requests) rather than
maintaining a private assessment indefinitely.
