---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "489d1984f670d6e5ed97838391a5bbe836fab48b9d1fcfc6620ae44d9abe67db",
  "components": {
    "sentry": {
      "name": "Sentry and self-hosted distribution",
      "basis": "26.8.0",
      "sources": {
        "sd29b3662378f": "https://github.com/getsentry/self-hosted/blob/26.8.0/docker-compose.yml",
        "s82b919d5116e": "https://github.com/getsentry/self-hosted/blob/26.8.0/.env",
        "sd576440e137e": "https://github.com/getsentry/sentry/blob/26.8.0/src/sentry/options/defaults.py",
        "s667e27476aba": "https://github.com/getsentry/sentry/blob/26.8.0/src/sentry/runner/commands/createuser.py",
        "sf2294c9468b9": "https://github.com/getsentry/self-hosted/blob/26.8.0/sentry/sentry.conf.example.py"
      }
    },
    "sentry-docs": {
      "name": "Sentry documentation",
      "basis": "unknown",
      "sources": {
        "see399d43779f": "https://docs.sentry.io/api/organizations/update-an-organization/",
        "s5e15f3959620": "https://docs.sentry.io/concepts/key-terms/dsn-explainer/"
      }
    },
    "glitchtip": {
      "name": "GlitchTip documentation",
      "basis": "unknown",
      "sources": {
        "seb7debbdfdf4": "https://glitchtip.com/documentation/install"
      }
    },
    "glitchtip-mfa": {
      "name": "GlitchTip MFA announcement",
      "basis": "unknown",
      "sources": {
        "sb4f6be6e6b48": "https://glitchtip.com/blog/2021-09-17-glitchtip-1-8/"
      }
    }
  },
  "claims": {
    "dsn": {"text": "Client DSNs authorize event submission, not reading tracker data.", "components": ["sentry-docs"], "sources": ["sentry-docs:s5e15f3959620"], "status": "REASONED"},
    "sentry-bind": {"text": "SENTRY_BIND=9000 publishes nginx on all interfaces; set 127.0.0.1:9000 behind a TLS proxy.", "components": ["sentry"], "sources": ["sentry:sd29b3662378f", "sentry:s82b919d5116e"], "status": "REASONED"},
    "sentry-stores": {"text": "Leave web, relay and backing stores unpublished; their internal credentials are not a public boundary.", "components": ["sentry"], "sources": ["sentry:sd29b3662378f"], "status": "REASONED"},
    "sentry-registration": {"text": "auth.allow-registration defaults False; keep it false on an internet-facing tracker.", "components": ["sentry"], "sources": ["sentry:sd576440e137e"], "status": "REASONED"},
    "sentry-admin": {"text": "createuser --superuser explicitly creates an administrator; plain createuser defaults its superuser prompt to no.", "components": ["sentry"], "sources": ["sentry:s667e27476aba"], "status": "REASONED"},
    "sentry-url": {"text": "Set system.url-prefix to the public HTTPS origin.", "components": ["sentry"], "sources": ["sentry:sf2294c9468b9", "sentry:sd576440e137e"], "status": "REASONED"},
    "sentry-secret": {"text": "Generate system.secret-key once and keep it out of version control; the generator command lacks a direct Sources citation.", "components": ["sentry"], "sources": ["sentry:sd576440e137e", "sentry:sf2294c9468b9"], "status": "REASONED"},
    "sentry-cookies": {"text": "Enable forwarded scheme/host recognition and secure session/CSRF cookies; bundled settings are commented out.", "components": ["sentry"], "sources": ["sentry:sf2294c9468b9"], "status": "REASONED"},
    "sentry-nginx": {"text": "Bundled nginx overwrites X-Forwarded-Proto with its scheme; terminate TLS there or propagate the real scheme. Its nginx config is not cited.", "components": ["sentry"], "sources": ["sentry:sd29b3662378f", "sentry:sf2294c9468b9"], "status": "REASONED"},
    "sentry-mfa": {"text": "Enforce organization member MFA with require2FA.", "components": ["sentry-docs"], "sources": ["sentry-docs:see399d43779f"], "status": "REASONED"},
    "sentry-scrubbing": {"text": "Use dataScrubber, dataScrubberDefaults and scrubIPAddresses to reduce sensitive intake.", "components": ["sentry-docs"], "sources": ["sentry-docs:see399d43779f"], "status": "REASONED"},
    "sentry-precedence": {"text": "auth.allow-registration prioritizes config.yml over the database; verify SSO provisioning and effective scrubbing separately.", "components": ["sentry", "sentry-docs"], "sources": ["sentry:sd576440e137e", "sentry-docs:see399d43779f"], "status": "REASONED"},
    "glitchtip-port": {"text": "GlitchTip Compose publishes 8000; bind privately behind TLS and verify the actual sample host bind.", "components": ["glitchtip"], "sources": ["glitchtip:seb7debbdfdf4"], "status": "REASONED"},
    "glitchtip-registration": {"text": "ENABLE_USER_REGISTRATION defaults True; False disables self-signup after the first user exists.", "components": ["glitchtip"], "sources": ["glitchtip:seb7debbdfdf4"], "status": "REASONED"},
    "glitchtip-secret": {"text": "Use a unique SECRET_KEY for Django signing and keep it out of version control.", "components": ["glitchtip"], "sources": ["glitchtip:seb7debbdfdf4"], "status": "REASONED"},
    "glitchtip-mfa": {"text": "Two-factor authentication is available since v1.8; confirm enforcement and SSO registration paths in the deployed version.", "components": ["glitchtip-mfa"], "sources": ["glitchtip-mfa:sb4f6be6e6b48"], "status": "REASONED"},
    "glitchtip-stores": {"text": "Keep PostgreSQL and optional Valkey or Redis internal.", "components": ["glitchtip"], "sources": ["glitchtip:seb7debbdfdf4"], "status": "REASONED"},
    "membership": {"text": "Sentry single-organization signups join the default organization; GlitchTip accounts and membership differ. Membership implementations are not cited.", "components": ["sentry", "glitchtip"], "sources": ["sentry:sf2294c9468b9", "glitchtip:seb7debbdfdf4"], "status": "REASONED"},
    "verify-listeners": {"text": "Inventory private 9000/8000 and backing ports; Docker forwarding can expose ports without host sockets.", "components": ["sentry", "glitchtip"], "sources": ["sentry:sd29b3662378f", "glitchtip:seb7debbdfdf4"], "status": "REASONED", "verify": [1]},
    "verify-sentry": {"text": "Follow the single-organization login redirect and inspect the create-account path; HTTP 200 alone cannot distinguish registration.", "components": ["sentry"], "sources": ["sentry:sd576440e137e", "sentry:sf2294c9468b9"], "status": "REASONED", "verify": [2]},
    "verify-glitchtip": {"text": "On an operator-controlled fixture, signup succeeds with registration True and is refused with False after the first user.", "components": ["glitchtip"], "sources": ["glitchtip:seb7debbdfdf4"], "status": "REASONED", "verify": [2]},
    "verify-stores": {"text": "Off-host backing-port probes judge TCP connection outcomes, not HTTP codes; distinguish the public HTTPS proxy and backend ports.", "components": ["sentry", "glitchtip"], "sources": ["sentry:sd29b3662378f", "glitchtip:seb7debbdfdf4"], "status": "REASONED", "verify": [2]},
    "verify-https": {"text": "Confirm plaintext web requests redirect to the HTTPS proxy; login pages, 404s and TLS errors do not prove controls.", "components": ["sentry", "glitchtip"], "sources": ["sentry:sf2294c9468b9", "glitchtip:seb7debbdfdf4"], "status": "REASONED", "verify": [2]}
  }
}
---
# Self-hosted error trackers: Sentry and GlitchTip

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| dsn: Client DSNs authorize event submission, not reading tracker data. | Sentry documentation unknown | REASONED |
| sentry-bind: SENTRY_BIND=9000 publishes nginx on all interfaces; set 127.0.0.1:9000 behind a TLS proxy. | Sentry and self-hosted distribution 26.8.0 | REASONED |
| sentry-stores: Leave web, relay and backing stores unpublished; their internal credentials are not a public boundary. | Sentry and self-hosted distribution 26.8.0 | REASONED |
| sentry-registration: auth.allow-registration defaults False; keep it false on an internet-facing tracker. | Sentry and self-hosted distribution 26.8.0 | REASONED |
| sentry-admin: createuser --superuser explicitly creates an administrator; plain createuser defaults its superuser prompt to no. | Sentry and self-hosted distribution 26.8.0 | REASONED |
| sentry-url: Set system.url-prefix to the public HTTPS origin. | Sentry and self-hosted distribution 26.8.0 | REASONED |
| sentry-secret: Generate system.secret-key once and keep it out of version control; the generator command lacks a direct Sources citation. | Sentry and self-hosted distribution 26.8.0 | REASONED |
| sentry-cookies: Enable forwarded scheme/host recognition and secure session/CSRF cookies; bundled settings are commented out. | Sentry and self-hosted distribution 26.8.0 | REASONED |
| sentry-nginx: Bundled nginx overwrites X-Forwarded-Proto with its scheme; terminate TLS there or propagate the real scheme. Its nginx config is not cited. | Sentry and self-hosted distribution 26.8.0 | REASONED |
| sentry-mfa: Enforce organization member MFA with require2FA. | Sentry documentation unknown | REASONED |
| sentry-scrubbing: Use dataScrubber, dataScrubberDefaults and scrubIPAddresses to reduce sensitive intake. | Sentry documentation unknown | REASONED |
| sentry-precedence: auth.allow-registration prioritizes config.yml over the database; verify SSO provisioning and effective scrubbing separately. | Sentry and self-hosted distribution 26.8.0; Sentry documentation unknown | REASONED |
| glitchtip-port: GlitchTip Compose publishes 8000; bind privately behind TLS and verify the actual sample host bind. | GlitchTip documentation unknown | REASONED |
| glitchtip-registration: ENABLE_USER_REGISTRATION defaults True; False disables self-signup after the first user exists. | GlitchTip documentation unknown | REASONED |
| glitchtip-secret: Use a unique SECRET_KEY for Django signing and keep it out of version control. | GlitchTip documentation unknown | REASONED |
| glitchtip-mfa: Two-factor authentication is available since v1.8; confirm enforcement and SSO registration paths in the deployed version. | GlitchTip MFA announcement unknown | REASONED |
| glitchtip-stores: Keep PostgreSQL and optional Valkey or Redis internal. | GlitchTip documentation unknown | REASONED |
| membership: Sentry single-organization signups join the default organization; GlitchTip accounts and membership differ. Membership implementations are not cited. | Sentry and self-hosted distribution 26.8.0; GlitchTip documentation unknown | REASONED |
| verify-listeners: Inventory private 9000/8000 and backing ports; Docker forwarding can expose ports without host sockets. | Sentry and self-hosted distribution 26.8.0; GlitchTip documentation unknown | REASONED |
| verify-sentry: Follow the single-organization login redirect and inspect the create-account path; HTTP 200 alone cannot distinguish registration. | Sentry and self-hosted distribution 26.8.0 | REASONED |
| verify-glitchtip: On an operator-controlled fixture, signup succeeds with registration True and is refused with False after the first user. | GlitchTip documentation unknown | REASONED |
| verify-stores: Off-host backing-port probes judge TCP connection outcomes, not HTTP codes; distinguish the public HTTPS proxy and backend ports. | Sentry and self-hosted distribution 26.8.0; GlitchTip documentation unknown | REASONED |
| verify-https: Confirm plaintext web requests redirect to the HTTPS proxy; login pages, 404s and TLS errors do not prove controls. | Sentry and self-hosted distribution 26.8.0; GlitchTip documentation unknown | REASONED |
<!-- version-basis:end -->

An error tracker exists to collect what your application would otherwise hide: stack traces, the source lines around each frame, request bodies and headers, environment variables, release and server names, and whatever user context the SDK attaches. That makes an exposed tracker one of the richest leaks in a deployment, because it aggregates secrets, tokens, and personal data that were never meant to leave the app, and it does so in a searchable UI. The two common self-hosted choices behave differently at their most important default, so the guide takes them one at a time. [fronting-auth.md](fronting-auth.md) is the reverse-proxy pattern both rely on for TLS, [secrets.md](secrets.md) covers the signing keys, and [mfa.md](mfa.md) is the account layer. Values below are illustrative; replace them.

One thing both share: the DSN a client uses to send events is a public, client-side key by design, not a secret. It authorizes event submission and nothing else, so finding one in shipped JavaScript is expected and is not the exposure this guide is about. The exposure is the tracker's own web and API, and the data they hold.

## Sentry

The `getsentry/self-hosted` Docker Compose distribution fronts the web and API with a bundled nginx. Its published port comes from `SENTRY_BIND` in `.env`, which ships as `SENTRY_BIND=9000` (a bare port), so nginx binds `0.0.0.0:9000` and the instance answers on every interface. Bind it to loopback and let your own proxy terminate TLS in front:

```ini
# .env
SENTRY_BIND=127.0.0.1:9000
```

Everything else in the Compose file (the web and relay processes, PostgreSQL, Redis, Kafka, and the ClickHouse and Snuba services) is an internal service that the distribution does not publish; leave it that way, because those backing stores hold the same event data with no authentication of their own.

Registration is off by default: `auth.allow-registration` defaults to `False`, so an exposed instance does not by itself let a stranger create an account. Do not turn it on for an internet-facing tracker, and create the first administrator with the superuser flag set explicitly (a plain `createuser` prompts for superuser and defaults to no):

```bash
docker compose run --rm web createuser --superuser
```

Set the rest in `sentry/config.yml`, and generate the signing key rather than copying one:

```yaml
system.url-prefix: "https://sentry.example.com"
auth.allow-registration: false
# system.secret-key: generate once with `sentry config generate-secret-key`, keep it out of version control
```

Because your proxy terminates TLS, Sentry has to be told it is behind HTTPS, or its session and CSRF cookies are never marked secure. The bundled `sentry/sentry.conf.example.py` ships the relevant settings commented out; enable them in `sentry/sentry.conf.py`:

```python
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

One catch is specific to the bundled stack: its own nginx sets `proxy_set_header X-Forwarded-Proto $scheme`, which overwrites whatever an outer proxy sent, so if you add a TLS proxy in front of nginx on `9000` it forwards `http` and Sentry still sees plaintext. Either terminate TLS at the bundled nginx itself, or propagate the real scheme through it, and verify the scheme Sentry actually receives rather than assuming the header setting alone took effect.

Enforce member MFA and data scrubbing at the organization level (an authenticated API call, or the same fields in the org settings UI): `require2FA`, `dataScrubber`, `dataScrubberDefaults`, and `scrubIPAddresses`. Scrubbing matters precisely because the tracker ingests request data, so redacting passwords, tokens, and IPs at intake reduces what a later exposure leaks.

The file setting is authoritative for this option: `auth.allow-registration` is a prioritize-disk option, so the value in `config.yml` wins over any value stored in the database, not the other way around. Unverified until checked in your deployment: any SSO path that provisions accounts around registration, the full list of auxiliary listeners your compose revision publishes, and the effective scrubbing rules.

## GlitchTip

GlitchTip is a single Django application, and its Compose distribution publishes it on port `8000`. Its default is the opposite of Sentry's on the setting that matters most: `ENABLE_USER_REGISTRATION` defaults to `True`, which means an exposed instance offers open self-signup to anyone who reaches it. Close it, and remember the value's own nuance:

```ini
# When True (the default), anyone may self-register; when False, self-signup is disabled
# after the first user exists. Set it False once your accounts are provisioned.
ENABLE_USER_REGISTRATION=False
```

Bind the app to loopback or a private interface and terminate TLS at a reverse proxy, since GlitchTip serves no TLS of its own. Give it a unique `SECRET_KEY` (Django's session and CSRF signing key) and keep it out of version control. GlitchTip has supported two-factor authentication since v1.8; enable it and require it for your users. PostgreSQL and the optional Valkey or Redis are internal services; do not publish them.

Unverified until checked: the exact host bind in your Compose sample, whether MFA is enforced rather than merely available in your version, and whether any single-sign-on you add carries its own registration path around `ENABLE_USER_REGISTRATION`.

## Shared exposures

- **The event data itself.** Both tools store stack traces with source context, request payloads, and user identifiers. An exposed backing store is reachable with the credentials the compose ships and expects on its internal network, so publishing it is a direct disclosure of every event it holds; an exposed web or API discloses to the degree an attacker can authenticate to it, which is why the registration default and the intake scrubbing both matter. Scrub at intake and keep the stores private.
- **Open registration.** GlitchTip ships it on; Sentry ships it off. What a self-registered stranger then reaches differs by tool: Sentry's single-organization mode adds new sign-ups to the default organization, while a GlitchTip account is separate from organization membership, so confirm your own membership and project permissions rather than assuming either extreme. Confirm the live setting rather than trusting the default.
- **The public DSN misread as a secret.** Rotating a DSN does not protect the tracker; authenticating its web and API does. Do not treat a leaked DSN as the incident.
- **Plaintext.** Neither serves TLS natively, so an instance reachable without a terminating proxy sends session cookies and the event UI in the clear.

## Verify

Every probe below is reasoned, not demonstrated: the authoring environment has no container runtime, so the outcomes are derived from the cited vendor sources rather than observed. A redirect to a login page, a 404, or a TLS error is inconclusive, never the fixed state.

```bash
# REASONED: listener expectations follow the cited vendor sources; no container runtime is available.
sudo ss -tlnp    # the tracker's own port only, on a private address: 9000 for Sentry, 8000 for
                 # GlitchTip; and no PostgreSQL, Redis, Kafka, or ClickHouse port published beside it
```

REASONED: following block; registration and backing-port checks follow the cited Sentry and GlitchTip sources; no container runtime is available.

```bash
# Registration discriminator against the plaintext listener. Substitute the URL inside the single
# quotes on the set -- line and paste the whole block so the guard runs; read the body, since an
# open form and a closed one can both return 200.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_REGISTER_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute a full URL on the set -- line above; not probing"; exit 2 ;;
    http://*|https://*) : ;;
    *) echo "expected an http:// or https:// URL; not probing"; exit 2 ;;
  esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
)
```

Point that block at Sentry's `http://tracker.example.com:9000/`: because the bundled config sets `SENTRY_SINGLE_ORGANIZATION`, `/auth/register/` redirects to the organization login, so follow the redirect (add `-L`) to the served login page, where an instance with registration on presents a create-account path and a closed one (the default) does not. For GlitchTip's `http://tracker.example.com:8000/`, an instance with `ENABLE_USER_REGISTRATION=True` accepts a new account through its signup, and one set `False` refuses after the first user exists; confirm by attempting a throwaway registration in an operator-controlled test, never against a shared instance. For each backing store, run the same guarded block against its port from off-host: those ports speak their own protocols, not HTTP, so read the connection outcome in the `exit` and `err` fields (a refused connection is the closed, fixed state; an accepted one is reachable) rather than any HTTP status. The `ss` inventory shows what Docker has published on the host, but a container port can be reachable through Docker's forwarding without a matching host socket, so the off-host probe is what proves it closed. Distinguish the public HTTPS proxy from the direct backend ports, and confirm plain HTTP to the web redirects to that proxy rather than serving the app. A reachable login page alone proves only that the port is open, not that registration or the backing stores are closed.

## Common mistakes

- Publishing Sentry with the shipped `SENTRY_BIND=9000`, which binds every interface, instead of a loopback address behind a proxy.
- Leaving GlitchTip's `ENABLE_USER_REGISTRATION` at its default `True` on an internet-facing instance, so anyone can self-register.
- Treating a leaked client DSN as the exposure while the tracker's own web and API stay unauthenticated.
- Publishing a backing service (PostgreSQL, Redis, Kafka, ClickHouse) beside the tracker, which holds the same event data with no auth of its own.
- Skipping data scrubbing, so secrets and personal data captured in events sit in the tracker in the clear.

## Sources (checked September 2026)

- Sentry self-hosted Docker Compose (`SENTRY_BIND`, the bundled nginx publication): https://github.com/getsentry/self-hosted/blob/26.8.0/docker-compose.yml
- Sentry self-hosted `.env` (`SENTRY_BIND=9000` default): https://github.com/getsentry/self-hosted/blob/26.8.0/.env
- Sentry `auth.allow-registration` default `False`: https://github.com/getsentry/sentry/blob/26.8.0/src/sentry/options/defaults.py
- Sentry `createuser` (explicit `--superuser`): https://github.com/getsentry/sentry/blob/26.8.0/src/sentry/runner/commands/createuser.py
- Sentry organization update API (`require2FA`, data scrubbing fields): https://docs.sentry.io/api/organizations/update-an-organization/
- Sentry bundled configuration (`SENTRY_SINGLE_ORGANIZATION`, the commented-out `SECURE_PROXY_SSL_HEADER`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`): https://github.com/getsentry/self-hosted/blob/26.8.0/sentry/sentry.conf.example.py
- Sentry DSN explainer (a DSN is public and allows only event submission, not read access): https://docs.sentry.io/concepts/key-terms/dsn-explainer/
- GlitchTip installation (port `8000`, `ENABLE_USER_REGISTRATION` default and behavior): https://glitchtip.com/documentation/install
- GlitchTip two-factor authentication (available since v1.8): https://glitchtip.com/blog/2021-09-17-glitchtip-1-8/
