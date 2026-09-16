# Self-hosted error trackers: Sentry and GlitchTip

An error tracker exists to collect what your application would otherwise hide: stack traces, the source lines around each frame, request bodies and headers, environment variables, release and server names, and whatever user context the SDK attaches. That makes an exposed tracker one of the richest leaks in a deployment, because it aggregates secrets, tokens, and personal data that were never meant to leave the app, and it does so in a searchable UI. The two common self-hosted choices behave differently at their most important default, so the guide takes them one at a time. [fronting-auth.md](fronting-auth.md) is the reverse-proxy pattern both rely on for TLS, [secrets.md](secrets.md) covers the signing keys, and [mfa.md](mfa.md) is the account layer. Values below are illustrative; replace them.

One thing both share: the DSN a client uses to send events is a public, client-side key by design, not a secret. It authorizes event submission and nothing else, so finding one in shipped JavaScript is expected and is not the exposure this guide is about. The exposure is the tracker's own web and API, and the data they hold.

## Sentry

The `getsentry/self-hosted` Docker Compose distribution fronts the web and API with a bundled nginx. Its published port comes from `SENTRY_BIND` in `.env`, which ships as `SENTRY_BIND=9000` (a bare port), so nginx binds `0.0.0.0:9000` and the instance answers on every interface. Bind it to loopback and let your own proxy terminate TLS in front:

```ini
# .env
SENTRY_BIND=127.0.0.1:9000
```

Everything else in the Compose file (the web and relay processes, PostgreSQL, Redis, Kafka, and the ClickHouse and Snuba services) is an internal service that the distribution does not publish; leave it that way, because those backing stores hold the same event data with no authentication of their own.

Registration is off by default: `auth.allow-registration` defaults to `False`, so an exposed instance does not by itself let a stranger create an account. Do not turn it on for an internet-facing tracker, and create the first administrator explicitly, since a plain `createuser` does not grant superuser:

```bash
docker compose run --rm web createuser --superuser
```

Set the rest in `sentry/config.yml`, and generate the signing key rather than copying one:

```yaml
system.url-prefix: "https://sentry.example.com"
auth.allow-registration: false
# system.secret-key: generate once with `sentry config generate-secret-key`, keep it out of version control
```

Enforce member MFA and data scrubbing at the organization level (an authenticated API call, or the same fields in the org settings UI): `require2FA`, `dataScrubber`, `dataScrubberDefaults`, and `scrubIPAddresses`. Scrubbing matters precisely because the tracker ingests request data, so redacting passwords, tokens, and IPs at intake reduces what a later exposure leaks.

Unverified until checked in your deployment: any registration or SSO setting already persisted in the database (which overrides the file default), the full list of auxiliary listeners your compose revision publishes, and the effective scrubbing rules.

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

- **The event data itself.** Both tools store stack traces with source context, request payloads, and user identifiers. An exposed tracker, or an exposed backing database, is a disclosure of every secret and every piece of personal data that ever rode into an event. Scrub at intake and keep the stores private.
- **Open registration.** GlitchTip ships it on; Sentry ships it off. On either, a self-registered stranger becomes a member who can read issues. Confirm the live setting rather than trusting the default, since a persisted value can differ.
- **The public DSN misread as a secret.** Rotating a DSN does not protect the tracker; authenticating its web and API does. Do not treat a leaked DSN as the incident.
- **Plaintext.** Neither serves TLS natively, so an instance reachable without a terminating proxy sends session cookies and the event UI in the clear.

## Verify

Every probe below is reasoned, not demonstrated: the authoring environment has no container runtime, so the outcomes are derived from the cited vendor sources rather than observed, and backlog row 2.33 tracks demonstrating them against live instances in the exposed and fixed states. A redirect to a login page, a 404, or a TLS error is inconclusive, never the fixed state.

```bash
sudo ss -tlnp    # the tracker's own port only, on a private address: 9000 for Sentry, 8000 for
                 # GlitchTip; and no PostgreSQL, Redis, Kafka, or ClickHouse port published beside it
```

```bash
# Registration discriminator against the plaintext listener. Substitute the registration URL on the
# set -- line and paste the whole block so the guard runs; read the body, since an open form and a
# closed one can both return 200.
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

Point that block at Sentry's `http://tracker.example.com:9000/auth/register/`: an open instance serves a working registration form, and a closed one (the default) does not offer signup. For GlitchTip's `http://tracker.example.com:8000/`, an instance with `ENABLE_USER_REGISTRATION=True` accepts a new account through its signup, and one set `False` refuses after the first user exists; confirm by attempting a throwaway registration in an operator-controlled test, never against a shared instance. Separately, confirm each backing store's port does not answer from off-host, and that reaching the web over plain HTTP redirects to your HTTPS proxy rather than serving the app. A reachable login page alone proves only that the port is open, not that registration or the backing stores are closed.

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
- GlitchTip installation (port `8000`, `ENABLE_USER_REGISTRATION` default and behavior): https://glitchtip.com/documentation/install
- GlitchTip two-factor authentication (available since v1.8): https://glitchtip.com/blog/2021-09-17-glitchtip-1-8/
