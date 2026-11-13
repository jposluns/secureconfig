# OpenClaw: gateway binding, authentication, TLS, and tool execution

OpenClaw is a self-hosted, MIT-licensed AI assistant. Its "Gateway" is the local control plane that wires chat channels (WhatsApp, Telegram, Discord, Slack, Signal, iMessage and more) to a model-agnostic agent, and that agent runs shell commands and reads and writes files as tools on the host. This guide helps your AI assistant configure a deployment securely: bind the Gateway to loopback, keep its single shared-secret authentication on, enable TLS, and hold the tool-execution surface and sandbox to their hardened settings.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/openclaw.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against OpenClaw v2026.11.2; 1 further source carries no recorded version. Metadata reviewed 2026-11-09; documentation checked November 2026. The guide records 31 claims, all reasoned from cited sources and any earlier-form run, not a live demonstration of the shipped form.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

An exposed, authenticated Gateway is remote code execution on the host. OpenClaw's own threat model says the authenticated caller is a trusted operator, the Control UI and HTTP surfaces are "intended for local use only", and public internet exposure is "out of scope and not hardened". A valid Gateway token or password is, in the vendor's words, to be treated like an owner or operator credential: the always-enabled `POST /tools/invoke` endpoint runs host tools for anyone holding it. Binding, authentication, TLS, and the tool and sandbox limits are therefore the whole game. OpenClaw is calendar-versioned and releases often, so pin the tag you tested and re-verify before relying on a default. The configuration file is `~/.openclaw/openclaw.json` (JSON5: comments and trailing commas are allowed), and the Gateway's default port is `18789`. [Gateway security and network exposure](https://docs.openclaw.ai/gateway/security/network-exposure), [tool-invoke HTTP API](https://docs.openclaw.ai/gateway/tools-invoke-http-api), [config overview](https://docs.openclaw.ai/gateway/configuration), [default port constant](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/config/paths.ts) (`DEFAULT_GATEWAY_PORT = 18789`, line 283; `CONFIG_FILENAME = "openclaw.json"`, line 35).

## 1. Bind the Gateway to loopback, and never trust `auto` in a container

`gateway.bind` selects a bind mode, not an address: `auto`, `loopback`, `lan` (all interfaces, `0.0.0.0`), `tailnet`, or `custom` (one IPv4 in `gateway.customBindHost`). On a normal host the default is `loopback` (127.0.0.1), local clients only. Keep it there. In `~/.openclaw/openclaw.json`:

```json5
{
  gateway: {
    bind: "loopback", // 127.0.0.1 only; set this explicitly, especially in a container
    port: 18789,
  },
}
```

The container case is the headline exposure gotcha. When `gateway.bind` is unset inside a detected container, the effective default mode is `auto`, and `auto` resolves to `0.0.0.0` (all interfaces) inside a container so host port-forwarding works. On bare metal or a VM the unset default is `loopback`. Container detection keys on `/.dockerenv`, `/run/.containerenv`, `/var/run/.containerenv`, Fly environment variables, and a `/proc/1/cgroup` match for docker, containerd, kubepods or lxc. So a Gateway you believe is private can be listening on every interface the moment it runs under Docker; set `bind: "loopback"` explicitly and do not publish the port with `docker run -p 18789:18789` unless you intend to expose it. [Bind-host resolution](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/gateway/net.ts) (`resolveGatewayBindHost` returns `127.0.0.1` for `loopback` at lines 253-254 and `0.0.0.0` for container `auto` at line 276; `defaultGatewayBindMode` returns `auto` in a container and `loopback` otherwise at lines 293-298), [container detection](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/infra/container-environment.ts) (lines 15-27), [config keys and bind default](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/config/zod-schema.gateway.ts) (`bind` enum and "Default: loopback (127.0.0.1)" at lines 140-155), [config-gateway reference](https://docs.openclaw.ai/gateway/config-gateway).

If `bind: "loopback"` ever resolves to a non-loopback host, startup throws rather than falling back to a network bind ("gateway bind=loopback resolved to non-loopback host ...; refusing fallback to a network bind"). [Loopback-resolution guard](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/gateway/server-runtime-config.ts) (line 155).

## 2. Rely on the non-loopback fail-closed guard as a safety net, not a substitute

Before it binds, the Gateway refuses to start on a non-loopback host with no shared secret unless it is in `trusted-proxy` mode. The guard is verbatim:

```ts
if (!isLoopbackHost(bindHost) && !hasSharedSecret && authMode !== "trusted-proxy") {
  throw new GatewayEffectiveConfigConflictError(
    `refusing to bind gateway to ${bindHost}:${params.port} without auth (...)`,
  );
}
```

`hasSharedSecret` is true only when mode is `token` with a non-empty token, or `password` with a non-empty password. The thrown `GatewayEffectiveConfigConflictError` is classified like a persisted-config validation failure, not a restart-eligible transient error, so a supervisor cannot loop past it. The same function also refuses a non-loopback Control UI with no `allowedOrigins`/`publicOrigin` (and no Host-header fallback), and refuses `trusted-proxy` mode with no `gateway.trustedProxies`. Treat all of this as a backstop: it stops the worst accident, but it does not configure authentication, TLS, origins, or the sandbox for you. Do the steps below. [Fail-closed guards](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/gateway/server-runtime-config.ts) (`hasSharedSecret` at lines 82-84, the no-auth refusal at lines 108-110, the Control UI origin refusal at lines 115-121, the trusted-proxy refusal at lines 124-126), [network-exposure docs](https://docs.openclaw.ai/gateway/security/network-exposure).

## 3. Keep Gateway authentication on and set a strong token

Authentication is on by default, including on loopback. With nothing configured and no ambient credential, the resolved `gateway.auth.mode` is `token` (a shared secret), not open. A Gateway in token mode with no token configured refuses to start ("gateway auth mode is token, but no token was configured"), so a fresh install does not silently run unauthenticated; the setup wizard (`openclaw setup`) provisions a token, generated as 24 random bytes (192 bits) rendered as hex. [Resolved default mode](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/gateway/auth-resolve.ts) (`mode ?? (password ? "password" : "token")`, line 64), [token-required guard](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/gateway/auth.ts) (lines 140-152), [token generator](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/commands/random-token.ts) (lines 4-6).

Set a strong secret and choose the mode explicitly. The keys are `gateway.auth.mode` (`none | token | password | trusted-proxy`), `gateway.auth.token`, and `gateway.auth.password`; the environment overrides are `OPENCLAW_GATEWAY_TOKEN` and `OPENCLAW_GATEWAY_PASSWORD`. If both a token and a password are set, the mode must be explicit or startup fails.

```json5
{
  gateway: {
    auth: {
      mode: "token", // explicit; "none" is tokenless and assumes a fully trusted local host
      token: "${OPENCLAW_GATEWAY_TOKEN}", // or a long random literal; keep it out of the config if you can
    },
  },
}
```

Generate a token with `openclaw doctor --fix --generate-gateway-token`, and read the configured token back with `openclaw gateway auth-token --show`, which refuses to print outside an interactive terminal on the Gateway host. The Control UI login field is labelled "Gateway secret" and takes the token or password. [Generate-token flag](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/cli/program/register.maintenance.ts) (`--generate-gateway-token`, line 67), [auth-token --show](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/commands/gateway-auth-token.ts) (interactive-terminal refusal at line 23), [auth config keys](https://docs.openclaw.ai/gateway/config-gateway), [dashboard login](https://docs.openclaw.ai/web/dashboard).

There is no native multi-factor authentication. Gateway auth is a single shared secret (or a trusted-proxy or Tailscale identity); a "second factor" exists only if an upstream identity-aware proxy enforces one. For MFA or SSO, keep the Gateway on loopback and front it with an identity proxy using `trusted-proxy` mode, and see [cloud-identity-proxies.md](cloud-identity-proxies.md). Keep `mode: "none"` (tokenless) only for a fully trusted local loopback host; the onboarding wizard never offers it. [MFA and trusted-proxy model](https://docs.openclaw.ai/gateway/trusted-proxy-auth), [remote access](https://docs.openclaw.ai/gateway/remote).

Password and token attempts are rate limited. The defaults are `maxAttempts` 10, `windowMs` 60000, `lockoutMs` 300000, and `exemptLoopback` true; blocked attempts return `429` with `Retry-After`. The loopback exemption means local processes are not throttled, which is one more reason the token must be strong even on a single-user host. [Rate-limit defaults](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/gateway/auth-rate-limit.ts) (lines 136-139).

## 4. Enable TLS

`gateway.tls.enabled` defaults to `false`, so an out-of-the-box Gateway serves plain HTTP and WebSocket on port 18789. Enable it, or terminate TLS at a reverse proxy. In source, TLS is active only when `enabled` is explicitly `true`, and `autoGenerate` is treated as `true` unless explicitly `false`:

```ts
if (!cfg || cfg.enabled !== true) {
  return { enabled: false, required: false };
}
const autoGenerate = cfg.autoGenerate !== false;
```

```json5
{
  gateway: {
    tls: {
      enabled: true,       // default is false
      autoGenerate: true,  // default; generates a self-signed cert/key only when both are missing
      // certPath: "/absolute/path/to/cert.pem", // or supply your own material
      // keyPath:  "/absolute/path/to/key.pem",
    },
  },
}
```

With `autoGenerate` on and no cert and key present, startup writes a self-signed pair under `~/.openclaw/gateway/tls/`, and the listener negotiates TLS 1.3 as its minimum version. Alternatively, terminate TLS at a reverse proxy in front of a loopback-bound Gateway. Without TLS, a non-loopback bind sends the shared secret in clear text to any on-path observer; the vendor allows plain `ws://` only for loopback, private/LAN, link-local, CGNAT, `.local` and `*.ts.net` hosts, and requires `wss://` for public remote hosts. The Control UI, the HTTP APIs, and the WebSocket all share the one port 18789, so this one TLS setting (or one terminating proxy) covers every surface. [TLS runtime defaults](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/infra/tls/gateway.ts) (`enabled` and `autoGenerate` at lines 210-214, self-signed generation and TLS 1.3 minimum below), [TLS schema](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/config/zod-schema.gateway.ts) (lines 485-502), [plaintext and wss rules](https://docs.openclaw.ai/gateway/security/network-exposure).

## 5. Lock down tool execution (the `/tools/invoke` surface)

`POST /tools/invoke` on the Gateway port is always enabled and invokes a single named host tool directly (default maximum body 2 MB). Its authentication is the Gateway's own: a shared-secret `Authorization: Bearer <token-or-password>`, trusted-proxy identity headers, or no header in `mode: "none"`. The vendor is blunt that this is a full operator surface: "Treat this endpoint as a full operator-access surface for the gateway instance," and a valid token or password "should be treated like an owner/operator credential." Under a shared-secret bearer the endpoint restores full operator scopes and ignores narrower `x-openclaw-scopes`, and there is no per-call approval prompt on this endpoint; exec approvals are "operator guardrails, not a separate authorization boundary for this HTTP endpoint." [Tool-invoke HTTP API](https://docs.openclaw.ai/gateway/tools-invoke-http-api).

A default hard deny list blocks the most dangerous tools over this HTTP surface even when a session policy would allow them. `DEFAULT_GATEWAY_HTTP_TOOL_DENY` denies 21 tools: `exec` ("Direct command execution - immediate RCE surface"), `spawn`, `shell`, `fs_write`, `fs_delete`, `fs_move`, `apply_patch`, `terminal`, `portal`, and `sessions_spawn`. The rest are `sessions_send`, `conversations_list`, `conversations_send`, `conversations_turn`, `automations`, `gateway`, `plugins`, `nodes`, `computer`, `mobile_ui`, and `openclaw`. [Default deny list](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/security/dangerous-tools.ts) (`DEFAULT_GATEWAY_HTTP_TOOL_DENY`, lines 10-49).

`gateway.tools.allow` removes tools from that default deny for owner and admin callers, and `gateway.tools.deny` adds more. Do not add `exec` (or `spawn`/`shell`) to `allow` on any exposed Gateway: with `exec` reachable here, an authenticated caller has arbitrary shell on the host, and denying write or patch tools "does not make shell execution read-only." Keep the deny list intact:

```json5
{
  gateway: {
    tools: {
      // allow: [],       // do NOT re-enable exec/spawn/shell on an exposed gateway
      deny: ["intent"],   // optional: extend the default deny; never shrink it on an exposed host
    },
  },
}
```

The core framing to carry into every other decision: a token holder is a host operator. Even with the default deny list intact, that holder has full operator access to every non-denied tool, and `/v1/chat/completions` and `/v1/responses` carry the same owner-sender semantics. [Tools schema](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/config/zod-schema.gateway.ts) (`tools.allow`/`tools.deny` at lines 458-464), [tool-invoke semantics](https://docs.openclaw.ai/gateway/tools-invoke-http-api).

## 6. Sandbox the agent

Sandboxing is off by default: `agents.defaults.sandbox.mode` resolves to `"off"`, so for the main session the agent runs its tools directly in the Gateway process's host context. Turn it on for any deployment where the model can receive untrusted input (an inbound channel message or a prompt-injection payload that reaches an allowed tool):

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",       // default "off"; "non-main" sandboxes every session except the agent's main
        backend: "docker", // default "docker"; also podman, ssh, openshell, crabbox
      },
    },
  },
}
```

The session-sandbox backends are `docker`, `podman`, `ssh`, `openshell`, and `crabbox` (default `docker` once the sandbox is enabled). The Docker sandbox schema blocks `network: "host"` and `network: "container:*"`, and blocks `seccomp`/`apparmor` set to `"unconfined"`, unless a `dangerouslyAllow...` escape hatch is set; leave those escape hatches off. A per-role `sandbox: "required"` forces a sandbox for that role regardless of agent mode and blocks execution if the backend is unavailable. [Sandbox resolved defaults](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/agents/sandbox/config.ts) (`mode ?? "off"` at line 221, backend `?? "docker"` at line 222), [sandbox mode enum](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/config/zod-schema.agent-runtime.ts) (line 516), [Docker sandbox hardening](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/config/zod-schema.sandbox.ts) (network and profile blocks at lines 79-118), [sandboxing modes/scope/backend](https://docs.openclaw.ai/gateway/sandboxing/modes-scope-and-backend).

Do not mistake the default "Code Mode" executor for a sandbox. Node's `node:vm` executor is explicitly "not a security boundary": the worker "shares the Gateway process's operating-system privileges," so "Treat Node Code Mode as trusted host execution." It is a separate feature from session sandboxing; a sandboxed session's Code Mode cell still runs in the Gateway process under the Node executor. The QuickJS (WASI) executor is the hardened-guest option. [Code Mode executors](https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/tools/code-mode/executors.md) (the "not a security boundary" warning, lines 26-30).

## 7. Restrict the Control UI origins

The browser Control UI is an admin surface (chat, config, exec approvals) served at `/` on port 18789, and the vendor says plainly: "Do not expose it publicly." For any non-loopback Control UI, set an explicit cross-origin allowlist. `gateway.controlUi.allowedOrigins` is the browser-origin allowlist used for CSRF and cross-origin protection; when it is omitted the Gateway falls back to `gateway.publicOrigin`, and a non-loopback Control UI with neither configured refuses to start (unless `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback` is set, which the docs call a dangerous security downgrade):

```json5
{
  gateway: {
    controlUi: {
      allowedOrigins: ["https://openclaw.internal.example"], // explicit; an empty [] replaces the publicOrigin default
    },
  },
}
```

Do not set `allowedOrigins: ["*"]` outside tightly controlled local testing, and do not enable `dangerouslyAllowHostHeaderOriginFallback`. The Control UI token is kept in per-tab `sessionStorage` (not `localStorage`), passwords stay in memory, and auth is enforced at the WebSocket handshake. [Control UI origin schema](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/config/zod-schema.gateway.ts) (`allowedOrigins` at line 257, `dangerouslyAllowHostHeaderOriginFallback` at line 262), [Control UI exposure warning](https://docs.openclaw.ai/web/dashboard), [origin requirement](https://docs.openclaw.ai/web).

## 8. For remote access, prefer loopback plus Tailscale Serve or a trusted reverse proxy

Keep the bind on loopback and reach the Gateway over Tailscale Serve or an authenticating reverse proxy rather than binding to the LAN or the internet. Tailscale Serve is the vendor's preferred path for the Control UI: it keeps the Gateway on loopback and provides TLS and identity (and Tailscale Funnel additionally requires `gateway.auth.mode: "password"`). An SSH tunnel (`ssh -N -L 18789:127.0.0.1:18789 user@gateway-host`) is the universal fallback, but note that a headerless SSH forward looks like a local process, so SSH access to the host is local-machine authority over the Gateway. [Remote access model](https://docs.openclaw.ai/gateway/remote).

If you must use `trusted-proxy` mode, these are its foot-guns and the safe defaults to keep:

- `gateway.auth.trustedProxy.allowLoopback` defaults to `false`. Enabling it lets any local process impersonate the proxy by sending identity headers; keep it off unless a same-host proxy is the deliberate trust boundary.
- `gateway.auth.trustedProxy.deviceAutoApprove.enabled` defaults to `false`. If you enable it, never list `operator.admin` in its `scopes`: that lets every proxy-authenticated user request a full-admin device. The default scopes are `operator.read`, `operator.write`, `operator.approvals`, `operator.questions`.
- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback` is off by default; keep it off.
- `gateway.allowRealIpFallback` defaults to `false` ("safer fail-closed"); keep it off unless the proxy strips a client-supplied `X-Real-IP` and sets its own.
- `gateway.nodes.pairing.autoApproveLocal` defaults to **`true`** - it silently approves trusted local device pairing. Call this one out and set it to `false` to require explicit approval if local pairing is a concern on your host.

The proxy must overwrite (not append) the client `x-forwarded-*` headers, firewall the Gateway port to the proxy only, and `gateway.auth.trustedProxy.requiredHeaders` checks only presence, not authenticity. [Trusted-proxy foot-gun defaults](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/config/zod-schema.gateway.ts) (`allowLoopback` default false at lines 352-357, `deviceAutoApprove` default-false and scopes at lines 378-391, `allowRealIpFallback` default false at lines 451-455, `nodes.pairing.autoApproveLocal` default true at lines 567-575), [trusted-proxy hardening](https://docs.openclaw.ai/gateway/trusted-proxy-auth).

## 9. Know which channels open inbound listeners

Each channel connects through the Gateway, but channels differ in direction, and only inbound ones expose a URL you must protect. Inbound webhook channels register a route on the single Gateway port (default 18789) and need an externally reachable URL:

- **Twilio / SMS** - inbound webhook, default path `/webhooks/sms`; Twilio request-signature validation is on by default. [sms channel](https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/sms.md) (webhook route and signature validation at line 9, path at line 110).
- **Synology Chat** - inbound outgoing-webhook POSTs to `https://gateway-host/webhook/synology` (or `channels.synology-chat.webhookPath`); needs a reachable HTTPS URL. [synology-chat channel](https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/synology-chat.md) (lines 34-35).
- **Slack in HTTP Request URLs mode** - the default transport is Socket Mode (outbound); only HTTP mode opens an inbound endpoint. [slack channel](https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/slack.md) (default Socket Mode, line 8).
- **Telegram in webhook mode** - the default transport is long polling (outbound); only webhook mode opens an inbound endpoint. [telegram channel](https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/telegram.md) (long polling default, line 10).

Outbound-only or local channels open no inbound listener: **Discord** (outbound bot connection over the Discord gateway), **WhatsApp** (WhatsApp Web via Baileys, QR-paired, more on-disk state), **Signal** (the Gateway talks to a signal-cli daemon on loopback `127.0.0.1:8080`), and **iMessage** (JSON-RPC over stdio to `imsg rpc` - no daemon or port). **WebChat** rides the Gateway's own WebSocket port, so its exposure is governed by `gateway.bind`, Gateway auth, and `controlUi.allowedOrigins`, not a dedicated channel port. Protect each channel's own secret and any inbound webhook URL. [discord](https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/discord.md) (line 8), [whatsapp](https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/whatsapp.md) (line 8), [signal](https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/signal.md) (loopback daemon default `127.0.0.1:8080`, line 42), [imessage](https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/imessage.md) (JSON-RPC over stdio, line 19), [channels overview](https://docs.openclaw.ai/channels).

## 10. Protect secrets at rest

OpenClaw has no OS-keychain integration by default; where secrets live depends on how you store them, and the defaults are unencrypted-at-rest files protected only by filesystem permissions.

- **Inline in config.** `gateway.auth.token`/`password`, channel credentials, and provider keys may sit as plaintext directly in `~/.openclaw/openclaw.json` (and the docs warn plaintext can remain in `.env` and generated `agents/*/agent/models.json` too).
- **Shared state SQLite.** The shared secret store, and the Gateway token when `OPENCLAW_GATEWAY_TOKEN` is not exported, live in `~/.openclaw/state/openclaw.sqlite` - stored unencrypted at rest. [State SQLite path](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/state/openclaw-state-db.paths.ts) (`openclaw.sqlite`, lines 34-35).
- **Agent SQLite.** Provider and model OAuth and API keys live in the auth-profile store, either the state DB or `~/.openclaw/agents/<name>/agent/openclaw-agent.sqlite`. [Shared auth store path](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/agents/auth-profiles/path-resolve.ts) (`openclaw-agent.sqlite`, lines 173-177).

The state code enforces directory mode `0700` and file mode `0600` for the state store, and chmod failures throw so credential-adjacent hardening stays loud. For stronger isolation than on-disk filesystem permissions, use opt-in exec SecretRefs (for example the 1Password or Vault plugin), where the config holds only a reference and the value is fetched at runtime. Keep the state directory and any backups protected, since the secret store is not encrypted. [State permissions](https://github.com/openclaw/openclaw/blob/v2026.11.2/src/state/openclaw-state-db-permissions.ts) (`0o700`/`0o600`, lines 13-14), [secret store and egress](https://docs.openclaw.ai/gateway/secrets/secret-store-and-egress).

## 11. Run with least privilege

Run the Gateway under a dedicated, unprivileged operating-system account, one Gateway per trust boundary (one host or OS user per person). A token holder already has host-operator authority through the agent's tools, so the account the Gateway runs as bounds the blast radius of a leaked secret or a successful prompt injection. In a container, run as the non-root `node` user with `--read-only` and `--cap-drop=ALL`, and see [container-hardening.md](container-hardening.md) and [docker.md](docker.md); under systemd, apply the usual service hardening. Grant the account only the filesystem and network access the agent genuinely needs, and remember that loopback binding limits inbound reach, not the agent's outbound access from its tools. [Threat model and least privilege](https://docs.openclaw.ai/gateway/security/network-exposure).

## Exposure rules

Before the Gateway is reachable beyond loopback, every one of these must hold:

- A Gateway auth token or password is set, strong, and random (`gateway.auth.mode` is `token`, `password`, or `trusted-proxy`, never `none`).
- TLS is on (`gateway.tls.enabled: true`) or a TLS-terminating authenticating proxy is in front; public hosts use `wss://`/`https://`.
- `gateway.controlUi.allowedOrigins` is set to explicit origins, and `dangerouslyAllowHostHeaderOriginFallback` is off.
- The sandbox is on (`agents.defaults.sandbox.mode` is `non-main` or `all`) with a container backend for any untrusted input.
- `exec`, `spawn`, and `shell` are not in `gateway.tools.allow`; the default HTTP deny list is intact.
- The auth rate limit is in force, and for `trusted-proxy` mode `allowLoopback`, `deviceAutoApprove` (never `operator.admin`), `allowRealIpFallback`, and `nodes.pairing.autoApproveLocal` are set as in section 8.
- Secrets at rest are protected: the state directory is `0700`, files `0600`, and backups are protected; prefer exec SecretRefs over inline plaintext.
- The Gateway runs as a dedicated non-root account, one Gateway per trust boundary.

## Verify

REASONED: Verification preparation. A live OpenClaw Gateway stand-up opens a listener and would run host tools; the authoring host forbids that without an isolated network namespace, and none was available. No Gateway, container runtime, or test deployment was exercised here, so every outcome below is REASONED from the cited source and documentation, not demonstrated. The guarded Bash blocks were written to pass `bash -n` and ShellCheck cleanly and to refuse on unsubstituted placeholders before they reach `curl`; the repository gate suite's `bash -n` and ShellCheck passes cover them. Service behaviour is REASONED, not demonstrated. Run each exposed-versus-fixed comparison only against an isolated test deployment you control, never by weakening production, and keep versions, paths, and credentials constant while changing the control under test. A rejection counts only when the positive control succeeds.

### Inventory the listener and confirm the loopback bind

REASONED: No OpenClaw Gateway runs here. `ss` inventories local binds in this namespace only, not firewall or NAT; a failed netlink inventory proves no absence. Expect the Gateway on `127.0.0.1:18789` when `gateway.bind` is `loopback`, and treat a `0.0.0.0:18789` (or `[::]:18789`) listener as exposed to every interface, which is the container `auto` default. Confirm the actual external entry point separately.

```bash
(
  set +e
  if ! command -v ss > /dev/null 2>&1; then
    echo "ss is not installed; install iproute2 (or use lsof -iTCP -sTCP:LISTEN); not probing"
    exit 2
  fi
  listeners=$(ss -H -tlnp 2>/dev/null)
  rc=$?
  if [ "$rc" -ne 0 ]; then
    echo "ss exited $rc; the listener inventory is inconclusive"
    exit 3
  fi
  match=$(printf '%s\n' "$listeners" | grep -E '[:.]18789([[:space:]]|$)')
  if [ -z "$match" ]; then
    echo "no listener on port 18789 in this namespace; the Gateway may be elsewhere, not running, or on another port"
    exit 0
  fi
  printf '%s\n' "$match"
  if printf '%s\n' "$match" | grep -Eq '0\.0\.0\.0:18789|\[::\]:18789'; then
    echo "FINDING (REASONED): the Gateway is bound to all interfaces; set gateway.bind=\"loopback\" unless this exposure is intended"
  elif printf '%s\n' "$match" | grep -Eq '127\.0\.0\.1:18789|\[::1\]:18789'; then
    echo "expected fixed result: the Gateway is bound to loopback"
  else
    echo "a non-loopback host is bound; judge whether that interface is intended"
  fi
)
```

### Confirm TLS and that `/tools/invoke` refuses anonymous callers

REASONED: No OpenClaw Gateway runs here. The first probe checks TLS and the always-enabled tool-invoke surface together: an exposed, unauthenticated Gateway answers an anonymous `exec` invoke with a `2xx` (a FINDING), while a fixed Gateway answers `401`/`403`. Paste the whole block and substitute the two values inside the single quotes; the block refuses placeholders before it calls `curl`, and it sends no credential.

```bash
(
  set +x
  set +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_GATEWAY_BASE_URL' 'REPLACE_WITH_CA_BUNDLE'
  if [ "${1-}" != PASTE_WHOLE_BLOCK ]; then
    echo "paste the whole block, including its set -- line; not probing"; exit 2
  fi
  shift
  if [ "$#" -ne 2 ]; then
    echo "the set -- line needs exactly 2 values; not probing"; exit 2
  fi
  for arg in "$@"; do
    case "$arg" in
      *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
        echo "substitute every placeholder inside the quotes; not probing"; exit 2 ;;
      *[[:cntrl:]]*)
        echo "control character in input; not probing"; exit 2 ;;
    esac
  done
  base=$1
  ca=$2
  case "$base" in
    https://*) ;;
    *) echo "an https:// base URL is required so no secret is sent in plaintext; not probing"; exit 2 ;;
  esac
  case "$base" in
    *'@'*|*'?'*|*'#'*|*' '*)
      echo "use a base URL without credentials, query, fragment or spaces; not probing"; exit 2 ;;
  esac
  case "$ca" in
    /*) ;;
    *) echo "an absolute CA bundle path is required; not probing"; exit 2 ;;
  esac
  if [ ! -f "$ca" ] || [ ! -r "$ca" ]; then
    echo "the CA bundle is not a readable file; not probing"; exit 2
  fi
  base=${base%/}
  # REASONED: no OpenClaw gateway or test deployment in the authoring environment.
  # Certificate validation stays on; a failed TLS handshake ends with a nonzero exit.
  case "$base" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute every placeholder inside the quotes; not probing"; exit 2 ;;
    *)
      curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert "$ca" \
        -H 'Content-Type: application/json' \
        --data '{"tool":"exec","args":{"command":"id"}}' \
        -w 'anonymous /tools/invoke -> http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "$base/tools/invoke" ;;
  esac
  echo "REASONED expectation: exposed+unauthenticated answers 2xx (FINDING); fixed answers 401 or 403; exit!=0 means TLS or the connection failed (inconclusive)."
)
```

### Confirm the default deny list refuses `exec` even with a valid token

REASONED: No OpenClaw Gateway runs here. Export `OPENCLAW_GATEWAY_TOKEN` in this shell first so the secret is read from the environment, not from `argv`; the block feeds the bearer header to `curl` on stdin. A fixed Gateway refuses `exec` with a `4xx` because `exec` is on `DEFAULT_GATEWAY_HTTP_TOOL_DENY`, even for the owner token; a `2xx` means `gateway.tools.allow` re-enabled `exec` (a FINDING).

```bash
(
  set +x
  set +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_GATEWAY_BASE_URL' 'REPLACE_WITH_CA_BUNDLE'
  if [ "${1-}" != PASTE_WHOLE_BLOCK ]; then
    echo "paste the whole block, including its set -- line; not probing"; exit 2
  fi
  shift
  if [ "$#" -ne 2 ]; then
    echo "the set -- line needs exactly 2 values; not probing"; exit 2
  fi
  for arg in "$@"; do
    case "$arg" in
      *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
        echo "substitute every placeholder inside the quotes; not probing"; exit 2 ;;
      *[[:cntrl:]]*)
        echo "control character in input; not probing"; exit 2 ;;
    esac
  done
  base=$1
  ca=$2
  case "$base" in
    https://*) ;;
    *) echo "an https:// base URL is required; not probing"; exit 2 ;;
  esac
  case "$ca" in
    /*) ;;
    *) echo "an absolute CA bundle path is required; not probing"; exit 2 ;;
  esac
  if [ ! -f "$ca" ] || [ ! -r "$ca" ]; then
    echo "the CA bundle is not a readable file; not probing"; exit 2
  fi
  if [ -z "${OPENCLAW_GATEWAY_TOKEN:-}" ]; then
    echo "export OPENCLAW_GATEWAY_TOKEN in this shell first; it is read from the environment, not argv; not probing"; exit 2
  fi
  case "$OPENCLAW_GATEWAY_TOKEN" in
    *[[:cntrl:]]*) echo "the token contains a control character; not probing"; exit 2 ;;
  esac
  base=${base%/}
  # REASONED: no OpenClaw gateway or test deployment in the authoring environment.
  case "$base" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute every placeholder inside the quotes; not probing"; exit 2 ;;
    *)
      printf 'Authorization: Bearer %s\n' "$OPENCLAW_GATEWAY_TOKEN" | \
        curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
          --cacert "$ca" --header @- \
          -H 'Content-Type: application/json' \
          --data '{"tool":"exec","args":{"command":"id"}}' \
          -w 'authenticated exec invoke -> http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
          "$base/tools/invoke" ;;
  esac
  echo "REASONED expectation: fixed answers a 4xx deny (exec is on the default HTTP deny list); a 2xx means exec was re-enabled via gateway.tools.allow (FINDING)."
)
```

### Confirm a foreign Origin is rejected and a non-loopback no-auth bind fails closed

REASONED: No OpenClaw Gateway runs here. For the origin check, a fixed non-loopback Control UI (with `allowedOrigins` set) rejects a browser request carrying a foreign `Origin`, while a misconfigured one with a Host-header fallback or `allowedOrigins: ["*"]` would accept it; `curl` does not enforce browser CORS, so also confirm with a real cookie-authenticated browser request. For fail-closed, do not probe production: in an isolated fixture, set `gateway.bind` to `lan` with no `gateway.auth.token`/`password` and start the Gateway - it must refuse to start with "refusing to bind gateway to ...:18789 without auth"; adding a token (or switching to `loopback`) lets it start. That refusal is a startup behaviour, observed from the fixture's logs, not a request.

```bash
(
  set +x
  set +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_GATEWAY_BASE_URL' 'REPLACE_WITH_CA_BUNDLE'
  if [ "${1-}" != PASTE_WHOLE_BLOCK ]; then
    echo "paste the whole block, including its set -- line; not probing"; exit 2
  fi
  shift
  if [ "$#" -ne 2 ]; then
    echo "the set -- line needs exactly 2 values; not probing"; exit 2
  fi
  for arg in "$@"; do
    case "$arg" in
      *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
        echo "substitute every placeholder inside the quotes; not probing"; exit 2 ;;
      *[[:cntrl:]]*)
        echo "control character in input; not probing"; exit 2 ;;
    esac
  done
  base=$1
  ca=$2
  case "$base" in
    https://*) ;;
    *) echo "an https:// base URL is required; not probing"; exit 2 ;;
  esac
  case "$ca" in
    /*) ;;
    *) echo "an absolute CA bundle path is required; not probing"; exit 2 ;;
  esac
  if [ ! -f "$ca" ] || [ ! -r "$ca" ]; then
    echo "the CA bundle is not a readable file; not probing"; exit 2
  fi
  base=${base%/}
  # REASONED: no OpenClaw gateway or test deployment in the authoring environment.
  # The foreign Origin below is a non-secret test value, not a destination.
  case "$base" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|"")
      echo "substitute every placeholder inside the quotes; not probing"; exit 2 ;;
    *)
      curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
        --cacert "$ca" \
        -H 'Origin: https://cross-origin.invalid' \
        -w 'foreign-origin control UI -> http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        "$base/" ;;
  esac
  echo "REASONED expectation: fixed rejects the foreign Origin; an accepted 2xx with cross-origin access is a FINDING; curl does not enforce CORS, so confirm in a browser too."
)
```

## Sources (checked November 2026)

Repository sources are the OpenClaw repository at annotated tag `v2026.11.2` (commit `b556fdf457b026574bf0f1e7b4914b15f3f179ce`); line numbers in the prose above are at that tag. Documentation pages under `https://docs.openclaw.ai/` are the rolling, reader-facing docs for the same product.

- OpenClaw default port and config filename constants (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/config/paths.ts
- OpenClaw gateway bind-host resolution and default bind mode (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/gateway/net.ts
- OpenClaw container-environment detection (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/infra/container-environment.ts
- OpenClaw gateway runtime-config guards (non-loopback fail-closed, Control UI origin, trusted-proxy, loopback resolution) (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/gateway/server-runtime-config.ts
- OpenClaw gateway auth resolved default mode (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/gateway/auth-resolve.ts
- OpenClaw gateway token-required guard (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/gateway/auth.ts
- OpenClaw gateway auth rate-limit defaults (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/gateway/auth-rate-limit.ts
- OpenClaw default HTTP tool deny list (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/security/dangerous-tools.ts
- OpenClaw gateway TLS runtime defaults and self-signed generation (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/infra/tls/gateway.ts
- OpenClaw sandbox resolved defaults (mode off, backend docker) (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/agents/sandbox/config.ts
- OpenClaw gateway config schema (bind, auth, TLS, tools, Control UI origins, trusted-proxy and pairing defaults) (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/config/zod-schema.gateway.ts
- OpenClaw agent-runtime sandbox mode enum (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/config/zod-schema.agent-runtime.ts
- OpenClaw Docker-sandbox hardening schema (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/config/zod-schema.sandbox.ts
- OpenClaw state-database file and directory permission modes (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/state/openclaw-state-db-permissions.ts
- OpenClaw state-database SQLite path (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/state/openclaw-state-db.paths.ts
- OpenClaw auth-profile store path (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/agents/auth-profiles/path-resolve.ts
- OpenClaw gateway auth-token show command (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/commands/gateway-auth-token.ts
- OpenClaw maintenance CLI generate-gateway-token flag (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/cli/program/register.maintenance.ts
- OpenClaw random-token generator (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/src/commands/random-token.ts
- OpenClaw Code Mode executors ("node:vm is not a security boundary") (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/tools/code-mode/executors.md
- OpenClaw SMS/Twilio channel (inbound webhook and signature validation) (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/sms.md
- OpenClaw Synology Chat channel (inbound webhook) (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/synology-chat.md
- OpenClaw Slack channel (default Socket Mode) (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/slack.md
- OpenClaw Telegram channel (default long polling) (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/telegram.md
- OpenClaw Discord channel (outbound bot connection) (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/discord.md
- OpenClaw WhatsApp channel (WhatsApp Web via Baileys) (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/whatsapp.md
- OpenClaw Signal channel (loopback signal-cli daemon) (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/signal.md
- OpenClaw iMessage channel (JSON-RPC over stdio) (v2026.11.2): https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/imessage.md
- OpenClaw gateway configuration reference (rolling documentation, checked November 2026): https://docs.openclaw.ai/gateway/config-gateway
- OpenClaw gateway network-exposure and security guidance (rolling documentation, checked November 2026): https://docs.openclaw.ai/gateway/security/network-exposure
- OpenClaw remote-access model (rolling documentation, checked November 2026): https://docs.openclaw.ai/gateway/remote
- OpenClaw trusted-proxy authentication (rolling documentation, checked November 2026): https://docs.openclaw.ai/gateway/trusted-proxy-auth
- OpenClaw tool-invoke HTTP API (rolling documentation, checked November 2026): https://docs.openclaw.ai/gateway/tools-invoke-http-api
- OpenClaw web dashboard and Control UI login (rolling documentation, checked November 2026): https://docs.openclaw.ai/web/dashboard
- OpenClaw Control UI (web) overview (rolling documentation, checked November 2026): https://docs.openclaw.ai/web
- OpenClaw channels overview (rolling documentation, checked November 2026): https://docs.openclaw.ai/channels
- OpenClaw sandboxing modes, scope and backend (rolling documentation, checked November 2026): https://docs.openclaw.ai/gateway/sandboxing/modes-scope-and-backend
- OpenClaw secret store and egress (rolling documentation, checked November 2026): https://docs.openclaw.ai/gateway/secrets/secret-store-and-egress
- OpenClaw configuration overview (rolling documentation, checked November 2026): https://docs.openclaw.ai/gateway/configuration


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, and any earlier-form run it rests on, not a live demonstration of the shipped form. Unknown means no version recorded.

Components (recorded basis):

- openclaw: OpenClaw (v2026.11.2)
- openclaw-docs: OpenClaw documentation (rolling) (unknown)

Claims (full source mapping in the JSON block below):

- product (REASONED; openclaw, openclaw-docs): OpenClaw is a self-hosted MIT AI assistant whose Gateway runs host tools; an exposed authenticated Gateway is host RCE; config is ~/.openclaw/openclaw.json (JSON5) and the default port is 18789.
- bind (REASONED; openclaw, openclaw-docs): gateway.bind modes are auto&#124;loopback&#124;lan&#124;tailnet&#124;custom, default loopback on a host, but unset auto resolves to 0.0.0.0 inside a detected container; set bind:"loopback" explicitly.
- port (REASONED; openclaw): The Gateway default port is 18789 (DEFAULT_GATEWAY_PORT) and the config filename is openclaw.json.
- fail-closed (REASONED; openclaw, openclaw-docs): A non-loopback bind with no shared secret and not trusted-proxy refuses to start; the error is classified non-restartable, and related guards cover Control UI origins and trusted-proxy.
- auth-default (REASONED; openclaw, openclaw-docs): Auth is on by default; the resolved mode is token; a token-mode Gateway with no token refuses to start even on loopback; the wizard provisions a 192-bit token.
- auth-keys (REASONED; openclaw, openclaw-docs): Keys gateway.auth.mode/token/password and env OPENCLAW_GATEWAY_TOKEN/PASSWORD; generate via doctor --fix --generate-gateway-token; show via gateway auth-token --show; mode:"none" assumes a trusted host.
- rate-limit (REASONED; openclaw): gateway.auth.rateLimit defaults maxAttempts 10, windowMs 60000, lockoutMs 300000, exemptLoopback true; blocked attempts return 429.
- mfa (REASONED; openclaw-docs): There is no native MFA; the shared secret is single-factor; for MFA/SSO front the loopback Gateway with an identity proxy in trusted-proxy mode.
- tls (REASONED; openclaw, openclaw-docs): gateway.tls.enabled defaults false; enable it; autoGenerate effective default true (self-signed under ~/.openclaw/gateway/tls, TLS 1.3 minimum) or terminate TLS at a proxy; public hosts need wss://.
- one-port (REASONED; openclaw, openclaw-docs): The Control UI, HTTP APIs and WebSocket share the single port 18789, so one TLS setting or terminating proxy covers every surface.
- tools-invoke (REASONED; openclaw-docs): POST /tools/invoke is always enabled and is a full operator-access surface; a token/password is an owner credential; it ignores narrower scopes and has no per-call approval.
- tools-deny (REASONED; openclaw): DEFAULT_GATEWAY_HTTP_TOOL_DENY denies 21 tools over HTTP by default, including exec/spawn/shell/fs_write/apply_patch/gateway/plugins/nodes/computer.
- tools-allow (REASONED; openclaw, openclaw-docs): gateway.tools.allow removes tools from the default deny for owner/admin callers; do not allow exec/spawn/shell on an exposed Gateway; denying write tools does not make shell read-only.
- sandbox (REASONED; openclaw, openclaw-docs): agents.defaults.sandbox.mode defaults off; backends docker/podman/ssh/openshell/crabbox (default docker); enable non-main or all with a container backend for untrusted input; Docker sandbox blocks host network and unconfined profiles by default.
- code-mode (REASONED; openclaw): The default node:vm Code Mode executor is explicitly not a security boundary and shares the Gateway's OS privileges; it is not a sandbox backend; QuickJS is the hardened option.
- control-ui-origins (REASONED; openclaw, openclaw-docs): The Control UI is an admin surface not to be exposed publicly; set gateway.controlUi.allowedOrigins for any non-loopback UI; dangerouslyAllowHostHeaderOriginFallback is a dangerous downgrade.
- remote (REASONED; openclaw-docs): Prefer loopback plus Tailscale Serve or an authenticating reverse proxy; Funnel needs password mode; an SSH forward grants local-machine authority over the Gateway.
- trusted-proxy (REASONED; openclaw, openclaw-docs): trustedProxy.allowLoopback (false), deviceAutoApprove.enabled (false; never list operator.admin), dangerouslyAllowHostHeaderOriginFallback (off) and allowRealIpFallback (false) are the safe defaults; the proxy must overwrite forwarded headers.
- pairing-autoapprove (REASONED; openclaw): gateway.nodes.pairing.autoApproveLocal defaults true and silently approves trusted local device pairing; set false to require explicit approval.
- channels-inbound (REASONED; openclaw, openclaw-docs): Twilio/SMS (/webhooks/sms, signatures on), Synology Chat (/webhook/synology), Slack in HTTP mode and Telegram in webhook mode open inbound listeners on the Gateway port that must be protected.
- channels-outbound (REASONED; openclaw, openclaw-docs): Discord, WhatsApp (Baileys), Signal (loopback signal-cli 127.0.0.1:8080) and iMessage (stdio) are outbound or local; WebChat rides the Gateway WebSocket port; default Slack is Socket Mode and default Telegram is long polling, both outbound.
- secrets-config (REASONED; openclaw-docs): Secrets may sit as inline plaintext in ~/.openclaw/openclaw.json, .env and generated models.json; there is no default OS keychain.
- secrets-store (REASONED; openclaw, openclaw-docs): The shared secret store and the Gateway token (when not exported) live in the unencrypted SQLite ~/.openclaw/state/openclaw.sqlite; state dir is 0700 and files 0600 and chmod failures throw.
- secrets-agent (REASONED; openclaw): Provider and model OAuth/API keys live in the auth-profile store, the state DB or a per-agent openclaw-agent.sqlite under ~/.openclaw/agents.
- secrets-refs (REASONED; openclaw-docs): For stronger isolation than filesystem permissions use opt-in exec SecretRefs (1Password/Vault); the config then holds only a reference; protect the state dir and backups.
- least-privilege (REASONED; openclaw-docs): Run the Gateway as a dedicated non-root account, one Gateway per trust boundary; loopback limits inbound reach, not the agent's outbound tool access; harden the container/systemd unit.
- verify-listeners (REASONED; openclaw): ss inventories local binds in this namespace only; expect 127.0.0.1:18789 for a loopback bind and treat 0.0.0.0:18789 as all-interfaces exposure; a failed inventory proves no absence.
- verify-tls-anon (REASONED; openclaw, openclaw-docs): Validated HTTPS must complete with exit=0; anonymous POST /tools/invoke must return 401/403 on a fixed Gateway and a 2xx on an exposed one.
- verify-exec-deny (REASONED; openclaw): An authenticated exec invoke must be refused with a 4xx because exec is on the default HTTP deny list; a 2xx means gateway.tools.allow re-enabled exec.
- verify-origin (REASONED; openclaw, openclaw-docs): A fixed non-loopback Control UI rejects a foreign Origin while the same-origin browser session loads; curl does not enforce CORS, so confirm in a browser.
- verify-fail-closed (REASONED; openclaw): In an isolated fixture, a non-loopback bind with no shared secret refuses to start with the verbatim refusal; adding a token or returning to loopback lets it start.

````json
{
  "schema": 1,
  "checked": "2026-11-09",
  "documentation_checked": "2026-11",
  "body_sha256": "3815828c34fddbe3481c810f921965b3f1674da163f7c8be62897a3f0559c203",
  "components": {
    "openclaw": {
      "name": "OpenClaw",
      "basis": "v2026.11.2",
      "sources": {
        "s6dd72b6a5226": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/config/paths.ts",
        "s19fa57e613dd": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/gateway/net.ts",
        "s7d682527d730": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/infra/container-environment.ts",
        "s7f909bc2f9ef": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/gateway/server-runtime-config.ts",
        "sf7afb92c7157": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/gateway/auth-resolve.ts",
        "s1e841487f8ae": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/gateway/auth.ts",
        "sf014616af61c": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/gateway/auth-rate-limit.ts",
        "s04b0bb697adb": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/security/dangerous-tools.ts",
        "sd85cbe517038": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/infra/tls/gateway.ts",
        "sff476340465b": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/agents/sandbox/config.ts",
        "s0ad6a13b229d": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/config/zod-schema.gateway.ts",
        "s683523927f66": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/config/zod-schema.agent-runtime.ts",
        "sd517a3611689": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/config/zod-schema.sandbox.ts",
        "s93afaf65e6e5": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/state/openclaw-state-db-permissions.ts",
        "s50f6fcb0cdbf": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/state/openclaw-state-db.paths.ts",
        "s117ed23e1616": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/agents/auth-profiles/path-resolve.ts",
        "s99d2ca6c335d": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/commands/gateway-auth-token.ts",
        "s570175db1450": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/cli/program/register.maintenance.ts",
        "saa90e718188e": "https://github.com/openclaw/openclaw/blob/v2026.11.2/src/commands/random-token.ts",
        "sbf5e8f744c73": "https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/tools/code-mode/executors.md",
        "s6c0945fe18c1": "https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/sms.md",
        "s1e093326443f": "https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/synology-chat.md",
        "s648e23668290": "https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/slack.md",
        "s2408eeadc229": "https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/telegram.md",
        "sc484f9208dc6": "https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/discord.md",
        "sf9ae91fb4925": "https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/whatsapp.md",
        "saf2ebd9d8abd": "https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/signal.md",
        "s0c92dbd75cbe": "https://github.com/openclaw/openclaw/blob/v2026.11.2/docs/channels/imessage.md"
      }
    },
    "openclaw-docs": {
      "name": "OpenClaw documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "sfd021eada97d": "https://docs.openclaw.ai/gateway/config-gateway",
        "sabc5c1fcbcc1": "https://docs.openclaw.ai/gateway/security/network-exposure",
        "sb089ccf1e235": "https://docs.openclaw.ai/gateway/remote",
        "s090654569dd4": "https://docs.openclaw.ai/gateway/trusted-proxy-auth",
        "s9e649e9bbd24": "https://docs.openclaw.ai/gateway/tools-invoke-http-api",
        "s1e50b1691d19": "https://docs.openclaw.ai/web/dashboard",
        "s3280e646dc58": "https://docs.openclaw.ai/web",
        "s6569d3b4860a": "https://docs.openclaw.ai/channels",
        "sc8f82dbf287a": "https://docs.openclaw.ai/gateway/sandboxing/modes-scope-and-backend",
        "sbb76d16c68a5": "https://docs.openclaw.ai/gateway/secrets/secret-store-and-egress",
        "s4ddc0690c335": "https://docs.openclaw.ai/gateway/configuration"
      }
    }
  },
  "claims": {
    "product": {"text": "OpenClaw is a self-hosted MIT AI assistant whose Gateway runs host tools; an exposed authenticated Gateway is host RCE; config is ~/.openclaw/openclaw.json (JSON5) and the default port is 18789.", "components": ["openclaw", "openclaw-docs"], "sources": ["openclaw:s6dd72b6a5226", "openclaw-docs:sabc5c1fcbcc1", "openclaw-docs:s9e649e9bbd24", "openclaw-docs:s4ddc0690c335"], "status": "REASONED"},
    "bind": {"text": "gateway.bind modes are auto|loopback|lan|tailnet|custom, default loopback on a host, but unset auto resolves to 0.0.0.0 inside a detected container; set bind:\"loopback\" explicitly.", "components": ["openclaw", "openclaw-docs"], "sources": ["openclaw:s19fa57e613dd", "openclaw:s7d682527d730", "openclaw:s0ad6a13b229d", "openclaw:s7f909bc2f9ef", "openclaw-docs:sfd021eada97d"], "status": "REASONED"},
    "port": {"text": "The Gateway default port is 18789 (DEFAULT_GATEWAY_PORT) and the config filename is openclaw.json.", "components": ["openclaw"], "sources": ["openclaw:s6dd72b6a5226"], "status": "REASONED"},
    "fail-closed": {"text": "A non-loopback bind with no shared secret and not trusted-proxy refuses to start; the error is classified non-restartable, and related guards cover Control UI origins and trusted-proxy.", "components": ["openclaw", "openclaw-docs"], "sources": ["openclaw:s7f909bc2f9ef", "openclaw-docs:sabc5c1fcbcc1"], "status": "REASONED"},
    "auth-default": {"text": "Auth is on by default; the resolved mode is token; a token-mode Gateway with no token refuses to start even on loopback; the wizard provisions a 192-bit token.", "components": ["openclaw", "openclaw-docs"], "sources": ["openclaw:sf7afb92c7157", "openclaw:s1e841487f8ae", "openclaw:saa90e718188e", "openclaw-docs:sfd021eada97d"], "status": "REASONED"},
    "auth-keys": {"text": "Keys gateway.auth.mode/token/password and env OPENCLAW_GATEWAY_TOKEN/PASSWORD; generate via doctor --fix --generate-gateway-token; show via gateway auth-token --show; mode:\"none\" assumes a trusted host.", "components": ["openclaw", "openclaw-docs"], "sources": ["openclaw:s570175db1450", "openclaw:s99d2ca6c335d", "openclaw:s0ad6a13b229d", "openclaw-docs:sfd021eada97d", "openclaw-docs:s1e50b1691d19"], "status": "REASONED"},
    "rate-limit": {"text": "gateway.auth.rateLimit defaults maxAttempts 10, windowMs 60000, lockoutMs 300000, exemptLoopback true; blocked attempts return 429.", "components": ["openclaw"], "sources": ["openclaw:sf014616af61c"], "status": "REASONED"},
    "mfa": {"text": "There is no native MFA; the shared secret is single-factor; for MFA/SSO front the loopback Gateway with an identity proxy in trusted-proxy mode.", "components": ["openclaw-docs"], "sources": ["openclaw-docs:s090654569dd4", "openclaw-docs:sb089ccf1e235"], "status": "REASONED"},
    "tls": {"text": "gateway.tls.enabled defaults false; enable it; autoGenerate effective default true (self-signed under ~/.openclaw/gateway/tls, TLS 1.3 minimum) or terminate TLS at a proxy; public hosts need wss://.", "components": ["openclaw", "openclaw-docs"], "sources": ["openclaw:sd85cbe517038", "openclaw:s0ad6a13b229d", "openclaw-docs:sabc5c1fcbcc1"], "status": "REASONED"},
    "one-port": {"text": "The Control UI, HTTP APIs and WebSocket share the single port 18789, so one TLS setting or terminating proxy covers every surface.", "components": ["openclaw", "openclaw-docs"], "sources": ["openclaw:s6dd72b6a5226", "openclaw-docs:s3280e646dc58"], "status": "REASONED"},
    "tools-invoke": {"text": "POST /tools/invoke is always enabled and is a full operator-access surface; a token/password is an owner credential; it ignores narrower scopes and has no per-call approval.", "components": ["openclaw-docs"], "sources": ["openclaw-docs:s9e649e9bbd24"], "status": "REASONED"},
    "tools-deny": {"text": "DEFAULT_GATEWAY_HTTP_TOOL_DENY denies 21 tools over HTTP by default, including exec/spawn/shell/fs_write/apply_patch/gateway/plugins/nodes/computer.", "components": ["openclaw"], "sources": ["openclaw:s04b0bb697adb"], "status": "REASONED"},
    "tools-allow": {"text": "gateway.tools.allow removes tools from the default deny for owner/admin callers; do not allow exec/spawn/shell on an exposed Gateway; denying write tools does not make shell read-only.", "components": ["openclaw", "openclaw-docs"], "sources": ["openclaw:s0ad6a13b229d", "openclaw-docs:s9e649e9bbd24"], "status": "REASONED"},
    "sandbox": {"text": "agents.defaults.sandbox.mode defaults off; backends docker/podman/ssh/openshell/crabbox (default docker); enable non-main or all with a container backend for untrusted input; Docker sandbox blocks host network and unconfined profiles by default.", "components": ["openclaw", "openclaw-docs"], "sources": ["openclaw:sff476340465b", "openclaw:s683523927f66", "openclaw:sd517a3611689", "openclaw-docs:sc8f82dbf287a"], "status": "REASONED"},
    "code-mode": {"text": "The default node:vm Code Mode executor is explicitly not a security boundary and shares the Gateway's OS privileges; it is not a sandbox backend; QuickJS is the hardened option.", "components": ["openclaw"], "sources": ["openclaw:sbf5e8f744c73"], "status": "REASONED"},
    "control-ui-origins": {"text": "The Control UI is an admin surface not to be exposed publicly; set gateway.controlUi.allowedOrigins for any non-loopback UI; dangerouslyAllowHostHeaderOriginFallback is a dangerous downgrade.", "components": ["openclaw", "openclaw-docs"], "sources": ["openclaw:s0ad6a13b229d", "openclaw-docs:s1e50b1691d19", "openclaw-docs:s3280e646dc58"], "status": "REASONED"},
    "remote": {"text": "Prefer loopback plus Tailscale Serve or an authenticating reverse proxy; Funnel needs password mode; an SSH forward grants local-machine authority over the Gateway.", "components": ["openclaw-docs"], "sources": ["openclaw-docs:sb089ccf1e235"], "status": "REASONED"},
    "trusted-proxy": {"text": "trustedProxy.allowLoopback (false), deviceAutoApprove.enabled (false; never list operator.admin), dangerouslyAllowHostHeaderOriginFallback (off) and allowRealIpFallback (false) are the safe defaults; the proxy must overwrite forwarded headers.", "components": ["openclaw", "openclaw-docs"], "sources": ["openclaw:s0ad6a13b229d", "openclaw-docs:s090654569dd4"], "status": "REASONED"},
    "pairing-autoapprove": {"text": "gateway.nodes.pairing.autoApproveLocal defaults true and silently approves trusted local device pairing; set false to require explicit approval.", "components": ["openclaw"], "sources": ["openclaw:s0ad6a13b229d"], "status": "REASONED"},
    "channels-inbound": {"text": "Twilio/SMS (/webhooks/sms, signatures on), Synology Chat (/webhook/synology), Slack in HTTP mode and Telegram in webhook mode open inbound listeners on the Gateway port that must be protected.", "components": ["openclaw", "openclaw-docs"], "sources": ["openclaw:s6c0945fe18c1", "openclaw:s1e093326443f", "openclaw:s648e23668290", "openclaw:s2408eeadc229", "openclaw-docs:s6569d3b4860a"], "status": "REASONED"},
    "channels-outbound": {"text": "Discord, WhatsApp (Baileys), Signal (loopback signal-cli 127.0.0.1:8080) and iMessage (stdio) are outbound or local; WebChat rides the Gateway WebSocket port; default Slack is Socket Mode and default Telegram is long polling, both outbound.", "components": ["openclaw", "openclaw-docs"], "sources": ["openclaw:sc484f9208dc6", "openclaw:sf9ae91fb4925", "openclaw:saf2ebd9d8abd", "openclaw:s0c92dbd75cbe", "openclaw:s648e23668290", "openclaw:s2408eeadc229", "openclaw-docs:s6569d3b4860a"], "status": "REASONED"},
    "secrets-config": {"text": "Secrets may sit as inline plaintext in ~/.openclaw/openclaw.json, .env and generated models.json; there is no default OS keychain.", "components": ["openclaw-docs"], "sources": ["openclaw-docs:sbb76d16c68a5"], "status": "REASONED"},
    "secrets-store": {"text": "The shared secret store and the Gateway token (when not exported) live in the unencrypted SQLite ~/.openclaw/state/openclaw.sqlite; state dir is 0700 and files 0600 and chmod failures throw.", "components": ["openclaw", "openclaw-docs"], "sources": ["openclaw:s50f6fcb0cdbf", "openclaw:s93afaf65e6e5", "openclaw-docs:sbb76d16c68a5"], "status": "REASONED"},
    "secrets-agent": {"text": "Provider and model OAuth/API keys live in the auth-profile store, the state DB or a per-agent openclaw-agent.sqlite under ~/.openclaw/agents.", "components": ["openclaw"], "sources": ["openclaw:s117ed23e1616"], "status": "REASONED"},
    "secrets-refs": {"text": "For stronger isolation than filesystem permissions use opt-in exec SecretRefs (1Password/Vault); the config then holds only a reference; protect the state dir and backups.", "components": ["openclaw-docs"], "sources": ["openclaw-docs:sbb76d16c68a5"], "status": "REASONED"},
    "least-privilege": {"text": "Run the Gateway as a dedicated non-root account, one Gateway per trust boundary; loopback limits inbound reach, not the agent's outbound tool access; harden the container/systemd unit.", "components": ["openclaw-docs"], "sources": ["openclaw-docs:sabc5c1fcbcc1"], "status": "REASONED"},
    "verify-listeners": {"text": "ss inventories local binds in this namespace only; expect 127.0.0.1:18789 for a loopback bind and treat 0.0.0.0:18789 as all-interfaces exposure; a failed inventory proves no absence.", "components": ["openclaw"], "sources": ["openclaw:s19fa57e613dd", "openclaw:s6dd72b6a5226"], "status": "REASONED", "verify": [1]},
    "verify-tls-anon": {"text": "Validated HTTPS must complete with exit=0; anonymous POST /tools/invoke must return 401/403 on a fixed Gateway and a 2xx on an exposed one.", "components": ["openclaw", "openclaw-docs"], "sources": ["openclaw:sd85cbe517038", "openclaw-docs:s9e649e9bbd24"], "status": "REASONED", "verify": [2]},
    "verify-exec-deny": {"text": "An authenticated exec invoke must be refused with a 4xx because exec is on the default HTTP deny list; a 2xx means gateway.tools.allow re-enabled exec.", "components": ["openclaw"], "sources": ["openclaw:s04b0bb697adb"], "status": "REASONED", "verify": [3]},
    "verify-origin": {"text": "A fixed non-loopback Control UI rejects a foreign Origin while the same-origin browser session loads; curl does not enforce CORS, so confirm in a browser.", "components": ["openclaw", "openclaw-docs"], "sources": ["openclaw:s0ad6a13b229d", "openclaw-docs:s3280e646dc58"], "status": "REASONED", "verify": [4]},
    "verify-fail-closed": {"text": "In an isolated fixture, a non-loopback bind with no shared secret refuses to start with the verbatim refusal; adding a token or returning to loopback lets it start.", "components": ["openclaw"], "sources": ["openclaw:s7f909bc2f9ef"], "status": "REASONED", "verify": [4]}
  }
}
````
<!-- version-basis:end -->
