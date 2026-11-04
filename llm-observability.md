# LLM tracing and observability: Langfuse, Phoenix, Helicone, OpenTelemetry Collector

Langfuse, Phoenix and Helicone record an AI app's prompts and responses; the OpenTelemetry Collector relays trace data. This guide helps your AI assistant configure each securely, including open signup off, authentication enabled where it ships disabled, private listeners, and TLS on Collector receivers, plus authentication on those taking off-host data.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/llm-observability.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against Langfuse documentation (no recorded version), Phoenix listener source arize-phoenix-v21.0.0 and arize-phoenix-v20.27.0, OpenTelemetry Collector v0.161.0, Collector distributions v0.161.0, and Phoenix TLS source arize-phoenix-v21.0.0, plus 2 more recorded bases; 7 further sources are pinned to a commit and 4 carry no recorded version. Metadata reviewed 2026-11-04; documentation checked September 2026. The guide records 48 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

These tools store full prompts, completions, and often the provider API keys used to generate them, so an
exposed dashboard leaks your most sensitive data at once. Several ship with authentication off or with open
signup enabled, so the default install is not safe to expose.

## Langfuse (self-hosted)

Email/password authentication is enabled by default: anyone who can reach the URL can register their own
account unless you turn signup off. Set `AUTH_DISABLE_SIGNUP=true` to block new registrations, including a
user accepting a project invite without an existing account; set `AUTH_DISABLE_USERNAME_PASSWORD=true` to
require SSO instead of a password entirely. Create the first account BEFORE you disable signup (or provision
it headlessly with `LANGFUSE_INIT_ORG_ID`, `LANGFUSE_INIT_USER_EMAIL`, and `LANGFUSE_INIT_USER_PASSWORD` -
a user or project cannot be initialized without also initializing an organization), or you lock yourself
out; then confirm a fresh registration is actually refused. SSO runs through Auth.js against Google, GitHub, GitLab, Azure
AD/Entra ID, Okta, Auth0, Keycloak, or a custom OIDC provider; `NEXTAUTH_URL` must be set correctly for any
method other than email/password. `AUTH_SESSION_MAX_AGE` sets the session lifetime in minutes, and must be an integer greater than five. The current implementation defaults it to 20160 (14 days); the documentation still says 43200 (30 days), so pin your release and check the value you actually get. The ingestion and public API are authenticated
separately from the UI session: a project's public key (username) and secret key (password) are sent as HTTP
Basic Auth, issued from Project Settings, and unrelated to a user's login credentials. Put MFA at the
identity provider per [mfa.md](mfa.md); Langfuse's own login has none.

Those controls all sit on the sign-in flow, and the self-hosting `docker-compose.yml` sits under them: it
ships example secrets marked `# CHANGEME`. The `NEXTAUTH_SECRET` variable protects the session token, which NextAuth
encrypts and authenticates, so the shipped `mysecret` lets anyone mint a session for any existing account,
administrators included, without the login flow and the SSO or MFA that only guard it. Disabling signup and
enforcing SSO do not help, because they gate account creation and sign-in, not a forged cookie. Two related
secrets ship the same way: `SALT` (`mysalt`) salts the stored API-key hashes, so a known salt speeds offline
cracking of keys lifted from the database; and `ENCRYPTION_KEY`, shipped as 64 hex zeros, encrypts the LLM
provider keys and integration credentials Langfuse stores, so anyone holding that key and a copy of the data
reads them in clear. Generate a fresh random value for each before the first start (`openssl rand -base64 32`
for `NEXTAUTH_SECRET` and `SALT`, `openssl rand -hex 32` for `ENCRYPTION_KEY`) and keep them out of the
repository ([secrets.md](secrets.md)); changing `ENCRYPTION_KEY` later needs a planned re-encryption, and if
the shipped key was ever live, treat the stored provider credentials as exposed and rotate them. The same
compose bundles a MinIO with the well-known `minio`/`miniosecret` login and publishes its S3 API on host port
`9090` on every interface by default, as it does langfuse-web on `3000`. The same compose's bundled Postgres,
ClickHouse, and Redis default to loopback; change the MinIO login, update the matching `LANGFUSE_S3_*` access keys
Langfuse uses to reach MinIO, and keep every published port off untrusted networks ([minio.md](minio.md),
[object-storage.md](object-storage.md)).

## Arize Phoenix (self-hosted)

At Phoenix 20.27.0, the last 20.x release, authentication is disabled by default, "as you may be just trying Phoenix for the very first time or have
Phoenix deployed in a VPC" in the vendor's own words: anyone who reaches the UI has full read and write
access with no login at all. Set `PHOENIX_ENABLE_AUTH=True` and `PHOENIX_SECRET` (a long random value used to
sign session tokens) to turn it on; at 20.27.0, `phoenix serve` raises an error when auth is enabled without
`PHOENIX_SECRET`. At Phoenix 21.0.0, an unset `PHOENIX_ENABLE_AUTH` follows the bind address: authentication
is on for any `PHOENIX_HOST` that is not loopback, including `0.0.0.0`, `::` and any hostname other than
`localhost`, and off for a loopback address, while an explicit `True` or `False` overrides that. Since 21.0.0's
default bind is loopback, this guide reads its defaults as leaving authentication off on a listener only the
host itself reaches.
`PHOENIX_SECRET` is optional at 21.0.0, but its source says that without it "Saved credentials use a publicly
known encryption key and are readable by database readers", so set it there too, and set
`PHOENIX_ENABLE_AUTH=True` explicitly rather than relying on the host rule. The served documentation page
still says authentication is disabled by default and that both variables are needed, which this guide reads
as not reflecting 21.0.0's host rule or its optional `PHOENIX_SECRET`.

Turning auth on is not enough. Phoenix creates an administrator account `admin@localhost` with the password
`admin` at startup, whether or not auth is on, so the flip alone leaves a reachable instance with a known admin login. `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD`
sets that password when the startup creates the account: set it on a brand-new deployment,
before the first start. At 20.27.0 that is the only time it takes effect: on any instance that has started before, the variable is inert, and setting it and
restarting changes nothing and reports no error, so never read "I set it and restarted" as proof the password
changed. At 21.0.0 a later start also applies it while the account still needs a password reset and still has
the password `admin`: that start replaces the password, deletes the account's pending password-reset tokens,
ends its sessions and logs "Applied PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD to the default admin account, which
still had the default password, and ended its existing sessions". The 21.0.0 `MIGRATION.md` adds that the
account's API keys stay valid and that all replicas must be stopped first for old sessions to end at once.
Once the password is no longer `admin`, the variable is inert at 21.0.0 as well. Unless you are setting it on a
brand-new deployment's very first start, treat the account as already existing: log in at the UI as
`admin@localhost`, which prompts for a new password, then run the
default-credential check in Verify to prove `admin` is dead. At 20.27.0 a login with `admin` opens a session;
at 21.0.0 the server answers it with HTTP 403 and a password-reset token, and that token sets the admin
password for whoever sent `admin`. In both releases, until that change lands, `admin`/`admin` is a live
admin login, so keep the instance off any untrusted network in the window between the flip and the change.
Once the password has been changed, the variable only holds an admin password in plaintext for no effect; remove it from
your environment files.

Phoenix 20.27.0 binds broadly by default: `phoenix serve` gives the HTTP UI/REST/OTLP server on 6006 its
`--host` value or `PHOENIX_HOST`, otherwise `HOST = "0.0.0.0"`, and starts a SEPARATE gRPC OTLP server on
`[::]:4317` that does not follow the HTTP host setting. Phoenix 21.0.0 binds loopback by default, with
`HOST = "127.0.0.1"`, and its `phoenix serve` gives the same `PHOENIX_HOST` value to both servers, so by this
guide's reading the two listeners can no longer be bound to different addresses. The repository's 21.0.0
`Dockerfile` sets `ENV PHOENIX_HOST=::`, with the comment "Bind all IPv4 and IPv6 interfaces (dual-stack) for
HTTP, gRPC, and Prometheus", so by this guide's reading a container built from it listens on every interface
for both protocols with authentication on unless `PHOENIX_ENABLE_AUTH=false`. The 20.27.0 `Dockerfile` sets
no `PHOENIX_HOST`, which leaves the `0.0.0.0` default with authentication off. Whether the vendor's published
images carry these `Dockerfile` settings is not established here. The vendor Compose file, the same at both
releases, builds that `Dockerfile`, publishes `6006:6006` and `4317:4317`, and lists its PostgreSQL port
(`- 5432`, with user and password `postgres`) under `ports`, which this guide reads as also publishing the
database on a host port the file does not fix. Bind or publish both protocols deliberately and keep the
database off host interfaces.

Upgrading from 20.x to 21.0.0 changes what an unchanged deployment does, by this guide's reading of the
21.0.0 source and its `MIGRATION.md`. A deployment that set a non-loopback `PHOENIX_HOST` but never
`PHOENIX_ENABLE_AUTH`, including a container built from the 21.0.0 `Dockerfile`, comes up with
authentication on, so collectors and clients without an API key are refused until you create keys for them.
A deployment outside such a container that relied on the `0.0.0.0` default comes up on `127.0.0.1` only, and `MIGRATION.md` says
`phoenix serve --host` is removed in favour of `PHOENIX_HOST`. With `PHOENIX_SECRET` unset, 21.0.0 still
starts with authentication on, signing tokens with a key derived from a deployment seed, and anyone who can
read the database, including a Compose PostgreSQL published as above, can read the saved credentials, such
as provider API keys. `MIGRATION.md` also says that setting or changing `PHOENIX_SECRET` makes previously saved
credentials unreadable, so plan to enter them again when you set it.

Enabling auth on a running instance stops trace collection and blocks all API access until API keys exist, so
mint a key immediately after the flip: a system key (admin-created, acts for the whole instance) or a user key
authenticates API requests via `PHOENIX_API_KEY` sent as an `Authorization: Bearer` header, and collectors and
SDKs need one to keep sending traces. At 21.0.0 the same lockout follows from the bind rule alone on a
non-loopback `PHOENIX_HOST` when `PHOENIX_ENABLE_AUTH` is unset, and `MIGRATION.md` says unauthenticated requests are then rejected with HTTP
401 or gRPC unauthenticated errors. Phoenix's authentication documentation describes no native MFA, and none
appears in the 21.0.0 files read for this guide, though that Phoenix has none is not established; it can
federate to an OAuth2/OIDC
identity provider (its documentation works through Google, AWS Cognito, and Microsoft Entra ID); enforce MFA
there, or add an identity-aware proxy in front per [mfa.md](mfa.md). Two OAuth caveats:
`PHOENIX_OAUTH2_<IDP>_ALLOW_SIGN_UP` defaults to `True`, so any identity the provider will authenticate can
provision itself an account unless you set it `False` and restrict provider membership (test an unapproved
identity). The second caveat is that local email/password login stays available alongside SSO and bypasses the
provider's MFA, so set `PHOENIX_DISABLE_BASIC_AUTH=True` once the IdP is the intended path. Establish and test
an approved IdP administrator BEFORE you disable local login or provider signup: disabling basic auth also
disables the local admin password, so once `PHOENIX_DISABLE_BASIC_AUTH=True` the "replacement admin password
works" control in Verify no longer applies - instead require local password login to FAIL and an approved IdP
login with MFA to succeed.

## Helicone (self-hosted)

Helicone self-hosts with Better Auth: account signup and organization membership, not a fixed shared login
(the `test@helicone.ai` / `password` credential is the manual guide's local trial only). Generate a real
`BETTER_AUTH_SECRET` before the first start: the all-in-one image documents the placeholder
`change-me-in-production` and the repository Compose file falls back to `your-secret-key`, and a known signing
secret weakens every session token it protects, so replace whichever example value your deployment uses. Then
restrict who may sign up, and do not expose the dashboard without your own layer in front. Helicone is several
services, not one: its Docker Compose publishes the backing stores - PostgreSQL, ClickHouse, MinIO/S3, Redis,
and MailHog - on host ports independent of the dashboard login (for example `54388:5432` and `18123:8123`). An
identity proxy on the Helicone UI therefore leaves those backing stores wide open; remove or loopback-scope
every backing publication and rotate the example storage credentials ([minio.md](minio.md),
[object-storage.md](object-storage.md)). Ingestion runs through the separate AI Gateway and the provider keys
in its environment, not the web session; store those per [secrets.md](secrets.md). The Jawn service and the S3
store also hold your data, so protect every service, not just the dashboard and gateway: keep them all on a
private network or behind an identity-aware fronting layer ([fronting-auth.md](fronting-auth.md),
[nginx.md](nginx.md), [caddy.md](caddy.md)) with MFA ([mfa.md](mfa.md)).

## OpenTelemetry Collector

The Collector is the pipe these tools (and others) receive traces through, and it ships with no security
applied until you configure it. Bind receivers to a specific interface or loopback (for example
`127.0.0.1:4317`). The OTLP receiver's default host became `localhost` in v0.104.0; the
`component.UseLocalHostAsDefaultHost` feature gate was stabilized in v0.110.0 and removed in v0.112.0.
At v0.161.0, the OTLP factory sets `localhost:4317` (gRPC) and `localhost:4318` (HTTP) directly.

**The official `otelcol` and `otelcol-contrib` images and deb/rpm packages ship a configuration that
overrides those localhost component defaults.** At v0.161.0, both enable wildcard IPv4 listeners on
`0.0.0.0`: OTLP `4317`/`4318`, Jaeger `14250`/`6832`/`6831`/`14268`, Zipkin `9411`, and
the diagnostic extensions pprof `1777` and zPages `55679`, with no authentication configured.
Their first-line comment tells users to narrow the endpoints, but the shipped values still bind every
IPv4 interface. Each Dockerfile copies that config and selects it in the default `CMD`; it declares
`EXPOSE 4317 4318 55679`. `EXPOSE` does not publish ports, and `docker run -p` publishes only the
mappings you request; the in-container wildcard listeners can still be reachable by container peers.
Inventory network paths as well as host publications.

For packages, the systemd unit reads `/etc/otelcol/otelcol.conf` or
`/etc/otelcol-contrib/otelcol-contrib.conf`; its `OTELCOL_OPTIONS` selects the matching
`/etc/otelcol/config.yaml` or `/etc/otelcol-contrib/config.yaml`. The package recipe installs the
same shipped config with `config|noreplace` handling; the postinstall scripts manage the service,
rather than copying the config. Existing local configuration can therefore differ.

Supply your own configuration with explicit endpoints for every enabled listener. Remove pprof and
zPages from both `extensions` and `service.extensions` unless needed; if retained, bind them privately
and control access separately from receiver authentication. Widen a receiver's bind only where the
intended clients, proxy, or mesh need it; require TLS on every receiver and exporter; and attach an authenticator
extension to any receiver that accepts data from outside the host. Examples of an authenticator extension are
`basicauth` (htpasswd-style credentials, or a static `client_auth` username/password for outgoing calls) and
`bearertokenauth` (a static `token` or file `filename`, with `filename` taking precedence). For `bearertokenauth`, each file line with a non-whitespace field supplies its first whitespace-delimited field as a token. The configurable header (default `Authorization`) and scheme (default `Bearer`) apply to outgoing HTTP and gRPC calls: HTTP sends the value as a header, and gRPC sends it as metadata under the lower-case configured header key. On incoming requests, `Authenticate` checks the canonical HTTP header or lower-case gRPC metadata key and compares its first value with each configured scheme-prefixed token and accepts any match; outgoing calls send only the first token. Declaring an authenticator extension is not enough to enforce it: list it under `service.extensions` so it
starts, then attach it to EACH receiver protocol with an `auth.authenticator` key naming the extension.
Inventory the other listeners too. At v0.161.0, the internal telemetry metrics factory defaults to
`localhost:8888`; the two shipped configs explicitly use `127.0.0.1:8888`. Their
`0.0.0.0:8888` Prometheus scrape target is an outbound destination, not a listener setting.
The enabled health-check extension (`13133`) also needs review independently of receiver authentication.
The `otelcol-k8s` Dockerfile at this tag copies no default config and supplies no default config
`CMD`; its `EXPOSE` list alone establishes no running listeners. Helm chart and operator configuration
are out of scope here.
Build or run only the receivers, processors, and exporters you use, since every enabled component is attack
surface, and run the process as a non-root user.

Langfuse's container deployment does not terminate TLS, so an `https://` URL in front of it is your proxy's,
not Langfuse's. Phoenix (8.29 and later) CAN terminate TLS natively for both HTTP and gRPC - set
`PHOENIX_TLS_ENABLED=True` (it defaults to `False`) with `PHOENIX_TLS_CERT_FILE` and `PHOENIX_TLS_KEY_FILE` -
so its default is TLS off, not TLS unsupported. Later versions add per-protocol overrides
(`PHOENIX_TLS_ENABLED_FOR_HTTP` and `PHOENIX_TLS_ENABLED_FOR_GRPC`, each overriding `PHOENIX_TLS_ENABLED` for
its protocol), which 20.27.0 and 21.0.0 both have; which release added them is not established, so check your release. Either way terminate TLS deliberately (natively, or at a reverse proxy or tunnel
per [nginx.md](nginx.md), [caddy.md](caddy.md)), and make sure any plaintext backend port a proxy forwards
to is not separately reachable. For Phoenix with an API key, the proxy or tunnel is itself a key-sending client: it
must reach Phoenix over loopback in Phoenix's own network namespace or over TLS with verification on (see Verify).

## Verify

REASONED: following block; the listener inventory, with the Langfuse checks and the Collector OTLP/HTTP probe in the two blocks after it, each marked in its own first line, per the guide's cited OpenTelemetry Collector releases v0.161.0 shipped configs, Langfuse public API authentication and OpenTelemetry Collector Contrib basicauthextension entries. No Langfuse, Phoenix, Helicone or Collector deployment and no isolated network namespace were available. During marking review (October 2026) an earlier form, which held all three checks in one block, passed bash -n under bash 5.3.9 and ran with stub curl and ss and no network. With the placeholders it printed the substitute-the-public-key refusal, a tab in the secret key drew the secret-key refusal, dummy keys reached curl only on stdin as an escaped user line, and the OTLP JSON body parsed as an empty resourceSpans list. That review covered the Langfuse checks before they took the Langfuse host on guarded `set --` lines that refuse example.com, example.net, example.org and their subdomains, and the Collector probe while it targeted a fixed illustrative host. The repository gate suite's bash -n and ShellCheck 0.11.0 passes over every block cover the current forms of the three blocks. Stub runs on 2026-10-31 with Bash 5.3.9, stub curl and ss and no network ran the guards and every exit status, on the inventory's current form and on the earlier form of the Langfuse and Collector blocks, which lowercased the host with `tr` before refusing reserved names. Those two blocks now refuse a reserved name under bash's `nocasematch` option instead of through `tr`, and each of their host parts refuses with 2, saying the block needs bash, when `shopt` fails, as it does in dash. That current form is covered by curl-stub runs on 2026-11-01 with no network. In bash, each host part refused example.com, example.net, example.org and their subdomains in lower, upper and mixed case with 2 and no curl call, also with `tr` absent from PATH or failing and under an inherited `nocasematch`, `readonly`, `declare -i` or `set -e`, and a host name outside the reserved names reached its probe. Under dash, stub runs of the current form refused every host name in each host part with 2 and the bash message before its probe, and both blocks exited 2. The inventory's command, run without sudo on the review host as ss -tlnp (iproute2 6.19.0), showed none of ports 3000, 6006, 4317 and 4318 listening, with an empty process column, so it tested no target. Without credentials, expect 401 from Langfuse and 401 or 403 from the Collector, and with them 200 or a 2xx; an anonymous 2xx is the exposed state. The Langfuse and Collector blocks exit 1 for an anonymous 2xx; the Langfuse block exits 3 for any other anonymous answer than 401 or a keyed answer other than a 2xx, and the Collector block exits 0 for 401 or 403 and 3 for any other answer. Each block exits 2 when a guard refuses and 3 when a command it attempts fails, and its last line names what it leaves for you to judge. The listener inventory refuses with status 2 when `ss` is not installed, and an `ss` that runs and fails gives 3. Collector live checks remain **REASONED**: the authoring host forbids opening listeners without an
isolated network namespace, and has none. Expected outcomes follow the cited pinned Collector configuration. Inspect the
effective config and inventory TCP and UDP sockets in the Collector's network namespace, together
with container publications and firewall rules. With the shipped config, expect the nine wildcard
endpoints listed above, including unauthenticated pprof and zPages. With your replacement config,
expect only the intended private binds and no pprof or zPages listener if removed. Test reachability
from an untrusted network and use an authorized client as a positive control; a failed connection
alone does not prove authentication. No exposed-versus-fixed Collector run was performed here.

```bash
# ss is a listener inventory in THIS namespace - not a firewall, NAT, or authentication check.
(                                       # a subshell, so the exits below end only the subshell
  set +e                                # errexit off here, so a failed ss is reported below instead of ending the block
  command -v ss >/dev/null || { echo "ss is not installed here; not listing sockets"; exit 2; }   # a missing ss is a guard refusal; an ss that runs and fails is 3 below
  ss -tlnp   # inventory 3000/6006/4317/4318 and identify each listener's namespace, host publication, and
             # permitted network paths. A wildcard bind is not itself exposure (Phoenix 20.27.0's gRPC 4317
             # binds [::] regardless of PHOENIX_HOST; 21.0.0's binds PHOENIX_HOST) and a port here can still be published by DNAT, so
             # confirm the actual container publications and firewall, and probe the public IPv4/IPv6 path
             # from another host - this list alone proves neither exposure nor authentication
  case "$?" in
    0) echo "unclassified observation: the listener table above is not classified, so judge it yourself against the namespace, publications and firewall"; exit 0 ;;
    *) echo "ss -tlnp exit $?: there is no listener table to judge; inconclusive"; exit 3 ;;
  esac
)
```

```bash
# REASONED: Langfuse dashboard reachability and public API authentication follow the cited Langfuse authentication and public API documentation; no Langfuse deployment is available.
# Langfuse dashboard: a bare GET of / cannot tell a login page from an exposed project view (both are 200
# and the body is discarded), so confirm it in a FRESH browser session - an unauthenticated visit must
# land on login, not a project. The curl below is only transport reachability.
(                                       # the whole block in one subshell, so one exit status covers every part of it
  set +e                                # errexit off here, so a part that ends nonzero is folded into the status below instead of ending the block
  set -- 0                              # the block's status so far: 1 (a finding) outranks 3 (inconclusive), which outranks 2 (a part refused its input), which outranks 0
  (                                     # a subshell, so your own script arguments are untouched
    set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_LANGFUSE_HOST'   # the public host name your proxy serves Langfuse on, no scheme, user name, port, path, query, fragment, percent sign or trailing dot: replace inside the quotes, keeping them
    [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
    shift
    [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 2; }
    case "$1" in
      ""|*REPLACE_WITH_*|*/*|*:*|*.|*[@?%]*|*'#'*|*[[:space:][:cntrl:]]*) echo "substitute your public host name (no scheme, user name, port, path, query, fragment, percent sign or trailing dot) inside the quotes on the set -- line above; not probing"; exit 2 ;;
    esac
    shopt -s nocasematch || { echo "this block needs bash; run it in bash; not probing"; exit 2; }   # host names ignore letter case, so this case matches them in any case through a bash option, not an outside command that could fail
    case "$1" in
      example.com|example.net|example.org|*.example.com|*.example.net|*.example.org) echo "example.com, example.net, example.org and their subdomains are not your deployment: substitute your own host name on the set -- line above; not probing"; exit 2 ;;
    esac
    shopt -u nocasematch   # every match below compares letter case exactly again
    curl -q -g -sS -L --proto-redir '=https' --noproxy '*' --connect-timeout 5 --max-time 15 \
      -o /dev/null -w 'dashboard final=%{http_code} url=%{url_effective} exit=%{exitcode}\n' "https://$1/"
    case "$?" in 0) exit 0 ;; *) echo "curl exit $?: the dashboard request failed; inconclusive"; exit 3 ;; esac
  )
  case "$?:$1" in 0:*) ;; 1:*) set -- 1 ;; 2:0) set -- 2 ;; 2:*|*:1) ;; *) set -- 3 ;; esac   # fold that part's status into the block's, ranked as above
  # Langfuse public API auth, matched pair: WITHOUT the key expect 401; WITH a valid project key (public:secret)
  # expect 200 whose JSON body carries the EXPECTED project id - the positive control. A 401/200 pair seen
  # THROUGH a reverse proxy does not prove Langfuse itself authenticated (a proxy can reject anonymous and
  # admit authenticated while its backend stays open), so repeat the pair DIRECTLY against the Langfuse
  # listener from an authorized network position, keeping any proxy credentials constant, and separately
  # confirm untrusted clients cannot reach that backend. The key reaches curl on stdin via a config file (curl --config -), so it stays out
  # of argv and /proc/<pid>/cmdline; still prefer a short-lived project key.
  (
    trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
    # The secret key you substitute on the set -- line enters shell history.
    # Use a short-lived project key or clear that history line afterward.
    # Stdin closes the argv channel only: it does not hide the keys from set -x
    # tracing or your own account's view of the process.
    set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_LANGFUSE_HOST' 'REPLACE_WITH_PUBLIC_KEY' 'REPLACE_WITH_SECRET_KEY'   # the same Langfuse host name as the dashboard check above, no scheme, user name, port, path, query, fragment, percent sign or trailing dot, then the project's public and secret keys: replace inside the quotes, keeping them
    [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
    shift
    [ "$#" -eq 3 ] || { echo "the set -- line needs exactly 3 values; not probing"; exit 2; }
    case "$1" in
      ""|*REPLACE_WITH_*|*/*|*:*|*.|*[@?%]*|*'#'*|*[[:space:][:cntrl:]]*) echo "substitute your public host name (no scheme, user name, port, path, query, fragment, percent sign or trailing dot) inside the quotes on the set -- line above; not probing"; exit 2 ;;
    esac
    shopt -s nocasematch || { echo "this block needs bash; run it in bash; not probing"; exit 2; }   # host names ignore letter case, so this case matches them in any case through a bash option, not an outside command that could fail
    case "$1" in
      example.com|example.net|example.org|*.example.com|*.example.net|*.example.org) echo "example.com, example.net, example.org and their subdomains are not your deployment: substitute your own host name on the set -- line above; not probing"; exit 2 ;;
    esac
    shopt -u nocasematch   # every match below compares letter case exactly again
    case "$2" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the public key on the set -- line above; not probing"; exit 2 ;; esac
    case "$3" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the secret key on the set -- line above; not probing"; exit 2 ;; esac
    set -- "$1" "${2//\\/\\\\}" "${3//\\/\\\\}"
    set -- "$1" "${2//\"/\\\"}" "${3//\"/\\\"}"
    set -- "$1" "$2" "$3" 0             # the 4th value is this part's status so far, ranked as above
    set -- "$1" "$2" "$3" "$4" "$(if curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 15 -o /dev/null \
      -w 'projects no-key=%{http_code} exit=%{exitcode}\n' "https://$1/api/public/projects"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
    set -- "$1" "$2" "$3" "$4" "${5##*$'\n'}" "${5%%$'\n'*}"   # curl's exit status, then its projects no-key= line
    printf '%s\n' "$6"
    case "$5:$6" in
      "0:projects no-key=401 "*) ;;
      "0:projects no-key=2"*) echo "FINDING: the public API answered without the key"; set -- "$1" "$2" "$3" 1 ;;
      0:*) echo "the request without the key got neither 401 nor a 2xx; inconclusive"; set -- "$1" "$2" "$3" 3 ;;
      *) echo "curl exit $5: the request without the key failed; inconclusive"; set -- "$1" "$2" "$3" 3 ;;
    esac
    set -- "$1" "$2" "$3" "$4" "$(if printf 'user = "%s:%s"\n' "$2" "$3" | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 15 \
      -w '\nprojects with-key=%{http_code} exit=%{exitcode}\n' --config - "https://$1/api/public/projects"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
    set -- "$1" "$2" "$3" "$4" "${5##*$'\n'}" "${5%$'\n'*}"   # curl's exit status, then the response body and its projects with-key= line
    printf '%s' "$6"
    set -- "$1" "$2" "$3" "$4" "$5" "${6%$'\n'}"   # the same, without the final line feed, so the last line is the projects with-key= line
    case "$5:${6##*$'\n'}" in
      "0:projects with-key=2"*) ;;
      0:*) echo "the request with the key did not get a 2xx, so the positive control failed; inconclusive"; [ "$4" = 1 ] || set -- "$1" "$2" "$3" 3 ;;
      *) echo "curl exit $5: the request with the key failed; inconclusive"; [ "$4" = 1 ] || set -- "$1" "$2" "$3" 3 ;;
    esac
    exit "$4"
  )
  case "$?:$1" in 0:*) ;; 1:*) set -- 1 ;; 2:0) set -- 2 ;; 2:*|*:1) ;; *) set -- 3 ;; esac   # fold that part's status into the block's, ranked as above
  echo "block exit $1; the dashboard's final URL, whether a fresh browser lands on login, and whether the keyed body carries the expected project id are not classified, so judge them yourself"
  exit "$1"
)
```

```bash
# REASONED: Collector OTLP/HTTP receiver authentication follows the cited Collector security guidance and basicauthextension entries; no Collector deployment is available.
# Collector OTLP/HTTP, matched pair: WITHOUT the configured auth header expect 401/403; then repeat the
# probe below WITH it, on curl's stdin as described next, and expect a 2xx - the positive
# control. Run the pair DIRECTLY against the receiver to establish RECEIVER authentication (a proxy can
# answer 401/2xx while the receiver is open), and test the public ingress separately. Keep the JSON content
# type (a wrong content type draws a 415 that is not an authentication result). This tests this OTLP/HTTP
# receiver only; test each enabled OTLP/gRPC receiver separately, and note the Phoenix check further below
# targets a DIFFERENT server, not this Collector.
# Never add the credential with -H or -u, which put it in curl's argv, where ps and /proc/<pid>/cmdline
# show it. For bearertokenauth, pipe printf 'Authorization: Bearer %s\n' "$2" into the probe and add
# --header @- to its options; for basicauth, pipe printf 'user = "%s"\n' "$2" into it, with "$2" as
# user:password, and add --config -. Keep -q as curl's first option in either case. Run that repeat in a
# subshell built like the Langfuse block above, in a fresh, clean shell (CONTRIBUTING rule 7):
# trap - DEBUG RETURN ERR first, the Collector host first and the credential second on its
# set -- line, a refusal of a placeholder, an empty value or a control character, and for basicauth a
# backslash and then a double quote escaped in "$2" before the printf. The credential on that set -- line
# enters shell history, so clear that line afterward. Stdin closes the argv channel only: it does not
# hide the credential from set -x tracing or your own account's view of the process.
(                                       # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_COLLECTOR_HOST'   # the host name of the Collector's OTLP/HTTP receiver on port 4318, no scheme, user name, port, path, query, fragment, percent sign or trailing dot: replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 2; }
  case "$1" in
    ""|*REPLACE_WITH_*|*/*|*:*|*.|*[@?%]*|*'#'*|*[[:space:][:cntrl:]]*) echo "substitute the Collector's host name (no scheme, user name, port, path, query, fragment, percent sign or trailing dot) inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  shopt -s nocasematch || { echo "this block needs bash; run it in bash; not probing"; exit 2; }   # host names ignore letter case, so this case matches them in any case through a bash option, not an outside command that could fail
  case "$1" in
    example.com|example.net|example.org|*.example.com|*.example.net|*.example.org) echo "example.com, example.net, example.org and their subdomains are not your deployment: substitute your own host name on the set -- line above; not probing"; exit 2 ;;
  esac
  shopt -u nocasematch   # every match below compares letter case exactly again
  set -- "$1" "$(if curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 15 -o /dev/null \
    -w 'otlp no-auth=%{http_code} exit=%{exitcode}\n' -H 'Content-Type: application/json' -d '{"resourceSpans":[]}' \
    "https://$1:4318/v1/traces"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "${2##*$'\n'}" "${2%%$'\n'*}"   # curl's exit status, then its otlp no-auth= line
  printf '%s\n' "$3"
  case "$2:$3" in
    "0:otlp no-auth=401 "*|"0:otlp no-auth=403 "*) set -- 0 ;;
    "0:otlp no-auth=2"*) echo "FINDING: the receiver accepted spans with no credential"; set -- 1 ;;
    0:*) echo "the anonymous request got neither 401/403 nor a 2xx (a 415 is a content-type answer, not an authentication result); inconclusive"; set -- 3 ;;
    *) echo "curl exit $2: the request failed, and a failed connection proves nothing about authentication; inconclusive"; set -- 3 ;;
  esac
  echo "block exit $1; the authenticated repeat described above and each OTLP/gRPC receiver are not run here, so run and judge them yourself"
  exit "$1"
)
```

REASONED: the Phoenix default-credential check and the anonymous read-API probe it introduces, per the guide's cited Arize Phoenix authentication entry (the default admin account and /v1/ REST permissions) and Arize Phoenix OAuth2 sign-up and basic-auth controls entry. No Phoenix instance is available in the authoring environment, so the manual login was not attempted; the expected exposed and fixed results are those stated here. For Phoenix specifically, prove the default admin credential is dead and that the read API does not answer an
anonymous request. **These checks are REASONED from the cited Phoenix documentation and source, not demonstrated** (no Phoenix instance in the authoring
environment). The credential
check is manual, because the vendor documents only the UI login flow and a scripted guess against the wrong
endpoint can read a `404` as a rejection: in a fresh browser session with no saved Phoenix cookies, try once
to log in as `admin@localhost` with the password `admin`. **Exposed:** it logs in or, at 21.0.0, is answered
with a demand to change the password: that release's server answers a login with `admin` with HTTP 403 and a
password-reset token that sets the admin password, so `admin` still controls the account. **Fixed:** it is rejected,
and your replacement admin password works in a second fresh session (or, if you set
`PHOENIX_DISABLE_BASIC_AUTH=True`, local password login is refused entirely and an approved IdP login with
MFA succeeds instead). Then, from a network position that
legitimately reaches Phoenix (a connection failure proves nothing about authentication), probe the read API
anonymously (the probe prints the `exitcode` and `errormsg` write-out variables, which need curl 7.75.0 or newer):

```bash
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PHOENIX_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the host on the set -- line above; not probing"; exit 2 ;;
  esac
  set -- "$1" "$(if curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 "https://$1/v1/projects" \
       -w '\n[unauth-read] http=%{http_code} exit=%{exitcode} err=%{errormsg}\n'; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "${2##*$'\n'}" "${2%$'\n'*}"     # curl's exit status, then the response and its unauth-read line
  printf '%s' "$3"
  set -- "$1" "$2" "${3%$'\n'}"                # the same, without the final line feed, so the last line is the unauth-read line
  case "$2:${3##*$'\n'}" in
    0:*" http=2"??" exit="*) echo "FINDING: /v1/projects answered the anonymous request with a 2xx"; set -- 1 ;;
    0:*" http=401 exit="*|0:*" http=403 exit="*) set -- 0 ;;
    0:*) echo "an answer other than a 2xx, 401 or 403 is inconclusive and does not prove authentication is on"; set -- 3 ;;
    *) echo "curl exit $2: a transport error is inconclusive and does not prove authentication is on"; set -- 3 ;;
  esac
  echo "block exit $1; the response body and the default-credential check above are not classified here, so judge them yourself"
  exit "$1"
)
```

REASONED: preceding block; the anonymous Phoenix read-API probe and these outcomes, per the guide's cited Arize Phoenix authentication entry (/v1/ REST permissions) and curl manual entry. No Phoenix instance is available. During marking review (October 2026) the block passed bash -n under bash 5.3.9 and ran with a stub curl and no network: unchanged, it printed its substitute-the-host refusal and exited 1; without its set -- line, the paste-the-whole-block refusal with exit 1; with phoenix.internal:6006 substituted, the stub received https://phoenix.internal:6006/v1/projects. The bash -n and stub runs recorded here covered an earlier form of this block, whose guard refusals exited with status 1 and whose answer was not classified. The current form is covered by the repository gate suite's bash -n and ShellCheck 0.11.0 passes over every block and by stub runs on 2026-10-31 with Bash 5.3.9, a stub curl and no network: it exits 2 when a guard refuses, 1 for a 2xx, 0 for 401 or 403 and 3 for anything else, and its last line names what it leaves for you to judge. **Exposed:** `/v1/projects` returns project data with no credential (a `2xx`). **Fixed:** the anonymous request
is rejected with `401` or `403`. Anything else (a `404`, a redirect to a login page, a `415`, or a transport
error) is inconclusive and does not prove authentication is on; fall back to the credential check above and to
the listener inventory. Substitute a bracketed literal for an IPv6 host in the URL, for example `[::1]:6006`.

REASONED: the OTLP/HTTP admission and OTLP gRPC Export checks, per the guide's cited Arize Phoenix authentication entry, Arize Phoenix gRPC OTLP Export authorization entry and pinned Phoenix gRPC bind entry. They need a running Phoenix and, for 4317, an OTLP gRPC client with the protobuf descriptor; the authoring environment has no Phoenix and no protobuf or gRPC Python package, so live HTTP admission, protobuf encoding and gRPC Export were not exercised. During marking review (October 2026), bash ran the HTTP recipe with a stub curl on PATH and no network, anonymously and with a dummy bearer header supplied through stdin using --header @-. In both calls the stub received --data-binary followed by an empty argument, -H followed by Content-Type: application/x-protobuf, and https://phoenix.internal:6006/v1/traces; the anonymous call had empty stdin and no authorization header, and the second received Authorization: Bearer dummy-write-key followed by a newline on stdin. Both stub calls exited 0. This checks local HTTP request construction only, not protobuf serialization, Phoenix admission or gRPC behaviour. The expected exposed and fixed results are those stated here. The OTLP/HTTP ingestion path CAN be probed without hand-encoding a span: an empty `ExportTraceServiceRequest`
is a zero-length protobuf body, so send `--data-binary ''` with `Content-Type: application/x-protobuf` to
`/v1/traces` on the HTTP port (6006) and read the status. The anonymous request must be rejected (401/403),
and the request with a WRITE-authorized `Authorization: Bearer` key (a system key, or a user key allowed to
write traces, NOT a viewer key) is admitted (a 2xx). This tests request ADMISSION, not span
persistence, and a valid VIEWER-role key is not a positive control here: Phoenix authenticates a viewer but
rejects a viewer token for OTLP writes, with HTTP `403` on `/v1/traces` and `PERMISSION_DENIED` on gRPC, so admit only with a system key or a
write-authorized user key. The gRPC OTLP receiver on 4317 is a SEPARATE server with its own
`ApiKeyInterceptor`, not the HTTP `/v1` router, so a protected HTTP path does not prove the gRPC path is
protected. The gRPC path therefore needs a separate test of 4317: invoke
`opentelemetry.proto.collector.trace.v1.TraceService/Export`
with an empty `ExportTraceServiceRequest`, first with no metadata (expect `UNAUTHENTICATED`) then with
`authorization: Bearer <write-authorized key>` (expect `OK`). That needs an OTLP gRPC client carrying the
protobuf descriptor (and the CA if TLS is on), so it ships REASONED: with authentication
disabled the same anonymous empty Export returns `OK` (the exposed outcome), because Phoenix then builds no
token store and adds no `ApiKeyInterceptor`, and at 21.0.0 authentication is disabled by default only on a
loopback `PHOENIX_HOST`. The authenticated,
viewer-rejected, and empty-request behaviours follow Phoenix's gRPC Export handler and `ApiKeyInterceptor`
(see Sources). At 20.27.0 Phoenix's gRPC listener binds `[::]` regardless of `PHOENIX_HOST`, so you cannot
move it to loopback by host setting; at 21.0.0 it binds `PHOENIX_HOST`, the same address as the HTTP server.
Either way, isolate it in a private container network, restrict or omit its host publication, and inspect its
namespace, publications, and firewall separately from the HTTP port. A wildcard listener inside an isolated
namespace is not by itself public exposure.

REASONED: transport for the Phoenix API key in the OTLP checks above. The requirement applies the bearer-key
rule in [machine-auth.md](machine-auth.md), and the Phoenix TLS entries in Sources describe only the server
settings named here. No Phoenix instance is available, so no plaintext-versus-TLS run was made and Phoenix
transport and authentication were not exercised. During review, only the key-handling pattern at the end of this
paragraph was run, in bash under `bash -x` with a stub curl and a dummy key: the subshell traced only its
`trap - DEBUG RETURN ERR` and `set +x` lines, none carrying the key. The same review run found that curl's argv
held no key and its stdin held the `Authorization: Bearer` line, and that a placeholder, an empty value, a line
feed, a carriage return or a tab was refused before any curl call. With `set +x` removed, the trace showed the
key on two lines, the `set --` line and the `printf` line, and an interactive run with history enabled kept
the key in the history entry. Outside the one plaintext exception below, send a Phoenix API key only over TLS:
use an `https://` URL for `/v1/traces` with certificate verification left on, and a TLS channel for the gRPC
Export on 4317. The TLS must be terminated by Phoenix itself (`PHOENIX_TLS_ENABLED=True` with
`PHOENIX_TLS_CERT_FILE` and `PHOENIX_TLS_KEY_FILE`, or the per-protocol `PHOENIX_TLS_ENABLED_FOR_HTTP` and
`PHOENIX_TLS_ENABLED_FOR_GRPC` where your release has them) or by a reverse proxy or tunnel in front of
Phoenix. Phoenix defaults to TLS off, so a plain `http://` URL or a plaintext gRPC channel puts the Bearer key
on the wire in cleartext, and a private network is not a substitute: anyone who can observe that network reads
the key. The plaintext exception, this guide's reasoning rather than machine-auth.md's rule, is a client on
the Phoenix host using loopback in Phoenix's own network namespace, for example a direct probe of a plaintext
listener behind a TLS-terminating proxy. A TLS-terminating proxy or tunnel that forwards the key to Phoenix is
itself a client that sends the key, so it must use that loopback or TLS with verification on. **Exposed:**
where any client sends the key other than over that loopback, the `https://` probe of the endpoint those
clients use (Phoenix's port when Phoenix terminates TLS, otherwise the proxy or tunnel) fails the TLS
handshake against a plaintext listener, or a client sends the key over an `http://` URL or a plaintext gRPC
channel other than loopback in Phoenix's own network namespace. **Fixed:** that probe, where it applies,
completes with verification on, and every client that sends the key, including each 4317 gRPC exporter, uses
TLS with verification on, other than one using loopback in Phoenix's own network namespace (Sources names no
gRPC client TLS option, so confirm it in that client's configuration). Sources has no Phoenix reference for an
API-key transport requirement or for an OTLP gRPC client's TLS or CA settings, so this guide names no client
option for them: for gRPC clients using TLS, trust the CA for the certificate presented by the endpoint your
client connects to, whether Phoenix or the TLS-terminating proxy or tunnel. When you script the HTTP probe,
keep the key out of argv and tracing. In a fresh, clean shell (CONTRIBUTING rule 7), build a subshell like the
Langfuse block above and add `set +x` straight after its `trap - DEBUG RETURN ERR` line, so tracing is off
before the key arrives on the `set --` line. That subshell must refuse a placeholder, an empty value or a
control character, then pipe `printf 'Authorization: Bearer %s\n' "$1"` into curl with `--header @-`, never
`-H` with the key and never the key in the URL. Require exactly one value, omit the Langfuse block's two
escaping lines (they apply only to `--config -`), send the empty `application/x-protobuf` POST described
above, and delete the history entry for the pasted block. The key on that `set --` line enters shell history,
and stdin keeps it out of argv only, not out of your own account's view of the process.

REASONED: a summary of the findings the checks above look for, per the guide's cited Langfuse authentication and SSO, Arize Phoenix authentication and OpenTelemetry Collector security best practices entries; it adds no probe of its own, and no deployment was available to show either finding. Exposed, a dashboard or OTLP port answers without a credential; fixed, both require one. A dashboard that renders traces, prompts, or provider keys without a login is a finding; so is an OTLP port
that accepts spans with no credential at all.

## Common mistakes

- Leaving Phoenix's or Helicone's auth off "because it's just internal" on a host with a public IP.
- Enabling `PHOENIX_ENABLE_AUTH` without creating an API key first, which locks out collectors mid-flight; at 21.0.0 a non-loopback `PHOENIX_HOST` with `PHOENIX_ENABLE_AUTH` unset does the same.
- Leaving Phoenix's default `admin@localhost` / `admin` in place after turning auth on, or trusting `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD` to have changed it on an instance whose admin account already existed, where at 20.27.0 the variable is silently inert and at 21.0.0 it is inert once the password is no longer `admin`.
- Running Phoenix 21.0.0 without `PHOENIX_SECRET`, which its source says leaves saved credentials readable by database readers.
- Publishing the OTLP gRPC/HTTP ports (4317/4318) to `0.0.0.0` because a docker-compose example did.
- Assuming an ingestion key protects the UI, or a UI login protects the ingestion endpoint; they are
  separate credentials in Langfuse and Phoenix alike.

## Sources (checked September 2026)

- Langfuse, authentication and SSO (signup default, `AUTH_DISABLE_SIGNUP`, `AUTH_DISABLE_USERNAME_PASSWORD`,
  SSO providers, `AUTH_SESSION_MAX_AGE`, `NEXTAUTH_URL`): https://langfuse.com/self-hosting/security/authentication-and-sso
- Langfuse, public API authentication (Basic Auth with project public/secret key): https://langfuse.com/docs/api-and-data-platform/features/public-api
- Langfuse, session-lifetime implementation (`AUTH_SESSION_MAX_AGE` validated as an integer greater than five, default `14 * 24 * 60` = 20160 minutes, vs the 43200 in the docs): https://github.com/langfuse/langfuse/blob/24c949d8dd5617219a8415f80e4c65ad611ff05c/web/src/env.mjs
- Langfuse, self-hosting configuration (`NEXTAUTH_SECRET`, `SALT`, `ENCRYPTION_KEY` and their generation, the bundled MinIO/Postgres/ClickHouse/Redis; checked 2026-09-14): https://langfuse.com/self-hosting/configuration
- Langfuse, self-hosting docker-compose.yml (the `# CHANGEME` example secrets `mysecret`/`mysalt`/all-zero `ENCRYPTION_KEY`, MinIO `minio`/`miniosecret` on host `9090`, langfuse-web on `3000`; checked 2026-09-14): https://github.com/langfuse/langfuse/blob/0dd0a7fbe2feb300b8776f02b3684eeee3fbceab/docker-compose.yml
- Arize Phoenix, authentication (`PHOENIX_ENABLE_AUTH`, `PHOENIX_SECRET`, system and user API keys, `PHOENIX_API_KEY`, the default `admin@localhost` / `admin` account, `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD`, `/v1/` REST permissions, OAuth2/OIDC identity providers, and no mention of native MFA; read 2026-09-13 and as served on 2026-11-04, checked November 2026). Its admin-password text matches 21.0.0, and its authentication-default text omits 21.0.0's host rule and optional `PHOENIX_SECRET`. Arize Phoenix authentication sources: https://arize.com/docs/phoenix/self-hosting/features/authentication
- Arize Phoenix, native HTTP and gRPC TLS introduced in 8.29 (2025-04-28): https://arize.com/docs/phoenix/release-notes/04-2025/04-28-2025-tls-support-for-phoenix-server
- Arize Phoenix, TLS configuration implementation at arize-phoenix-v21.0.0 (`PHOENIX_TLS_ENABLED` default `False`, `PHOENIX_TLS_CERT_FILE`/`PHOENIX_TLS_KEY_FILE`, and the per-protocol `PHOENIX_TLS_ENABLED_FOR_HTTP`/`PHOENIX_TLS_ENABLED_FOR_GRPC` overrides, with the same text at arize-phoenix-v20.27.0; checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/config.py#L853-L874 and https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/config.py#L1032-L1057
- Helicone, self-hosted deployment (default `test@helicone.ai` / `password` login): https://docs.helicone.ai/getting-started/self-host/manual
- Helicone, all-in-one Docker deployment (Better Auth, `BETTER_AUTH_SECRET` documented default `change-me-in-production`): https://docs.helicone.ai/getting-started/self-host/docker
- Helicone, repository Compose deployment (`BETTER_AUTH_SECRET` fallback `your-secret-key`; backing stores published on host ports `54388:5432`, `18123:8123`, `19000:9000`, `9000`/`9001`, `6379`, `1025`/`8025`): https://github.com/Helicone/helicone/blob/b12ebaccb824ab9778757ca197ff302d97fda421/docker/docker-compose.yml
- Langfuse, headless initialization (`LANGFUSE_INIT_ORG_ID`/`USER_EMAIL`/`USER_PASSWORD`, org-before-user ordering): https://langfuse.com/self-hosting/administration/headless-initialization
- Arize Phoenix, OAuth2 sign-up and basic-auth controls (`PHOENIX_OAUTH2_<IDP>_ALLOW_SIGN_UP` default True, `PHOENIX_DISABLE_BASIC_AUTH`): https://arize.com/docs/phoenix/self-hosting/features/authentication
- OpenTelemetry Collector v0.161.0, OTLP factory endpoints: https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/receiver/otlpreceiver/factory.go#L41-L67
- OpenTelemetry Collector v0.161.0 changelog, v0.104.0 OTLP localhost transition: https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/CHANGELOG.md#L2058-L2070
- OpenTelemetry Collector v0.161.0 changelog, gate stabilization in v0.110.0 and removal in v0.112.0: https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/CHANGELOG.md#L1793-L1811 and https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/CHANGELOG.md#L1737-L1743
- OpenTelemetry Collector releases v0.161.0, shipped configs (wildcard endpoints, explicit loopback metrics, enabled pipelines and extensions): https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/config.yaml#L1-L81 and https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/config.yaml#L1-L81
- OpenTelemetry Collector releases v0.161.0, Docker config COPY, CMD and EXPOSE: https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/Dockerfile#L10-L15 and https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/Dockerfile#L10-L15
- OpenTelemetry Collector releases v0.161.0, deb/rpm config installation and script selection: https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/.goreleaser.yaml#L86-L118 and https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/.goreleaser.yaml#L94-L126
- OpenTelemetry Collector releases v0.161.0, systemd environment and command: https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/otelcol.service#L5-L7 and https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/otelcol-contrib.service#L5-L7
- OpenTelemetry Collector releases v0.161.0, package config arguments: https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/otelcol.conf#L1-L5 and https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/otelcol-contrib.conf#L1-L5
- OpenTelemetry Collector releases v0.161.0, deb postinstall service management: https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/postinstall.sh#L6-L16 and https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/postinstall.sh#L6-L16
- OpenTelemetry Collector releases v0.161.0, rpm postinstall service management: https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/postinstall-rpm.sh#L6-L9 and https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/postinstall-rpm.sh#L6-L9
- OpenTelemetry Collector releases v0.161.0, otelcol-k8s Dockerfile (no config COPY or CMD): https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-k8s/Dockerfile#L1-L17
- OpenTelemetry, Collector security best practices (bind addresses, TLS, authenticator extensions, minimal
  components, non-root): https://opentelemetry.io/docs/security/config-best-practices/
- OpenTelemetry Collector Contrib, `basicauthextension` (htpasswd, `client_auth`, `auth.authenticator` wiring): https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/basicauthextension
- OpenTelemetry Collector Contrib, `bearertokenauthextension` README (`token`, `filename`, precedence, line parsing, header and scheme defaults, HTTP and gRPC transport; checked October 2026): https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/bearertokenauthextension/README.md#L21-L39
- OpenTelemetry Collector Contrib, `bearertokenauthextension` gRPC metadata and TLS requirement (checked October 2026): https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/bearertokenauthextension/bearertokenauth.go#L30-L43
- OpenTelemetry Collector Contrib, `bearertokenauthextension` token resolver handoff and `filename` warning (checked October 2026): https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/bearertokenauthextension/bearertokenauth.go#L73-L122
- OpenTelemetry Collector Contrib, `bearertokenauthextension` file token parsing and scheme assembly (checked October 2026): https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/bearertokenauthextension/bearertokenauth.go#L156-L189
- OpenTelemetry Collector Contrib, `bearertokenauthextension` first-token selection for outgoing calls (checked October 2026): https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/bearertokenauthextension/bearertokenauth.go#L197-L205
- OpenTelemetry Collector Contrib, `bearertokenauthextension` incoming `Authenticate` header and metadata checks (checked October 2026): https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/bearertokenauthextension/bearertokenauth.go#L234-L255
- OpenTelemetry Collector Contrib, `bearertokenauthextension` HTTP header assignment (checked October 2026): https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/bearertokenauthextension/bearertokenauth.go#L264-L272
- OpenTelemetry Collector Contrib, `bearertokenauthextension` header and scheme defaults (checked October 2026): https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/bearertokenauthextension/factory.go#L15-L18
- Arize Phoenix, gRPC OTLP Export authorization at arize-phoenix-v21.0.0 (`ApiKeyInterceptor`: `UNAUTHENTICATED` without a key, `PERMISSION_DENIED` for a viewer token, `OK` with a write-authorized key; `bearer_auth.py` is the same file at arize-phoenix-v20.27.0; checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/bearer_auth.py#L152-L190
- OpenTelemetry Collector v0.161.0, internal telemetry metrics default `localhost:8888`: https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/service/telemetry/otelconftelemetry/factory.go#L49-L64
- OpenTelemetry Collector v0.161.0, zPages default endpoint and HTTP server configuration: https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/extension/zpagesextension/factory.go#L15-L29
- OpenTelemetry Collector v0.161.0, zPages server wiring and optional HTTP authentication: https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/extension/zpagesextension/zpagesextension.go#L87-L105 and https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/config/confighttp/server.go#L352-L364
- OpenTelemetry Collector Contrib, pprof extension (default endpoint `localhost:1777`): https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/443567a6a00d7cff8cae1432a6fef655d8698e94/extension/pprofextension/README.md
- OpenTelemetry Collector Contrib, health-check extension (default endpoint `localhost:13133`): https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/d922ffb299c6b9be026f97dd7d6a5f0f507efdeb/extension/healthcheckextension/README.md
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0): https://curl.se/docs/manpage.html
- Phoenix defaults `HOST = "127.0.0.1"`, `PORT = 6006`, `GRPC_PORT = 4317` at arize-phoenix-v21.0.0, where `PHOENIX_HOST` is the bind address for HTTP, gRPC and Prometheus, `get_env_host()` canonicalizes it, and `is_loopback_host` counts `0.0.0.0`, `::` and hostnames other than `localhost` as not loopback (checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/config.py#L55-L59, https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/config.py#L3166-L3172 and https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/config.py#L3425-L3447
- Phoenix defaults `HOST = "0.0.0.0"`, `PORT = 6006`, `GRPC_PORT = 4317` at arize-phoenix-v20.27.0, and `get_env_host()` returns `PHOENIX_HOST` or that default (checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/config.py#L3131-L3137 and https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/config.py#L3364-L3365
- Phoenix gRPC OTLP server at arize-phoenix-v21.0.0, which binds the host it is given through `_bind_address` and adds `ApiKeyInterceptor` only when it has a token store (checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/grpc_server.py#L55-L82 and https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/grpc_server.py#L109-L131
- Phoenix gRPC OTLP server at arize-phoenix-v20.27.0, which binds `[::]` regardless of the HTTP host and adds `ApiKeyInterceptor` only when it has a token store (checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/server/grpc_server.py#L55-L80 and https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/server/grpc_server.py#L107-L109
- Phoenix `serve` command at arize-phoenix-v21.0.0 (bind host from `get_env_host()`, auth settings from `get_env_auth_settings()`, `grpc_host=host`, and the HTTP server's `host=None if host == "::" else host`; checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/cli/commands/serve.py#L238-L246 and https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/cli/commands/serve.py#L363-L393
- Phoenix `serve` command at arize-phoenix-v20.27.0 (a `--host` option with no default, then `get_env_host()`, `::` passed to the HTTP server as `None`, no gRPC host, and `secret=auth_settings.phoenix_secret`; checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/server/cli/commands/serve.py#L148-L160, https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/server/cli/commands/serve.py#L244-L253 and https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/server/cli/commands/serve.py#L383-L417
- Phoenix `create_app` at arize-phoenix-v21.0.0 (the gRPC host defaulting to `get_env_host()`, the admin bootstrap added on every start, the token store only with authentication enabled, and a deployment-seed signing key without `PHOENIX_SECRET`; checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/app.py#L1007-L1014, https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/app.py#L1060-L1069 and https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/app.py#L704-L739
- Phoenix `create_app` at arize-phoenix-v20.27.0 (`GrpcServer` built with no host, and the token store only with authentication enabled and a secret; checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/server/app.py#L694-L702 and https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/server/app.py#L1018-L1027
- Phoenix `Dockerfile`, `ENV PHOENIX_HOST=::` at arize-phoenix-v21.0.0 and no `PHOENIX_HOST` at arize-phoenix-v20.27.0, each with the `serve` command (checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/Dockerfile#L160-L174 and https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/Dockerfile#L160-L172
- Phoenix migration notes for v20.x to v21.0.0 at arize-phoenix-v21.0.0 (loopback default bind, authentication following the bind address, Docker authentication by default, `--host` removed, default-admin credentials, optional `PHOENIX_SECRET` and saved credentials; checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/MIGRATION.md#L3-L63
- Phoenix vendor Compose file at arize-phoenix-v21.0.0, the same file at arize-phoenix-v20.27.0 (`6006:6006`, `4317:4317`, and PostgreSQL `- 5432` with user and password `postgres`; checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/docker-compose.yml#L1-L23
- Phoenix authentication settings at arize-phoenix-v21.0.0 (`PHOENIX_ENABLE_AUTH` following a non-loopback `PHOENIX_HOST` when unset, optional `PHOENIX_SECRET` with saved credentials readable by database readers when unset, and `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD` applied while the default admin still has `admin`; checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/config.py#L415-L467, https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/config.py#L1274-L1278 and https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/config.py#L1509-L1534
- Phoenix authentication settings at arize-phoenix-v20.27.0 (`PHOENIX_ENABLE_AUTH` default `False`, `PHOENIX_SECRET` required when auth is enabled, and `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD` with no effect once the default admin record exists; checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/config.py#L403-L449, https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/config.py#L1256-L1260 and https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/config.py#L1491-L1501
- Phoenix default admin bootstrap at arize-phoenix-v21.0.0 (creates `admin@localhost` with `reset_password=True`, and on a later start replaces a still-default password with a custom initial password, deletes its reset tokens and ends its sessions; checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/db/facilitator.py#L115-L219
- Phoenix default admin bootstrap at arize-phoenix-v20.27.0 (creates `admin@localhost` only when no admin exists, as a step added to every start; checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/db/facilitator.py#L113-L160 and https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/server/app.py#L972
- Phoenix password login at arize-phoenix-v21.0.0 (`POST /auth/login` with the default password answers HTTP 403 with a password-reset token, and `POST /auth/password-reset` refuses `admin` as the new password; checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/api/routers/auth.py#L147-L198 and https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/api/routers/auth.py#L311-L341
- Phoenix password login at arize-phoenix-v20.27.0 (`POST /auth/login` issues tokens for any valid password, with no default-password check; checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/server/api/routers/auth.py#L144-L186
- Phoenix `/v1` REST authentication and viewer write refusal at arize-phoenix-v21.0.0, the same files at arize-phoenix-v20.27.0 (`is_authenticated` on the `/v1` router only with authentication enabled, 401 without a valid token, `restrict_access_by_viewers` answering a viewer's non-GET request with 403, and `GET /v1/projects` and `POST /v1/traces` under that router; checked November 2026): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/api/routers/v1/__init__.py#L35-L83, https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/bearer_auth.py#L213-L282, https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/authorization.py#L73-L84, https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/api/routers/v1/projects.py#L66-L67 and https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/api/routers/v1/traces.py#L431-L433


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- langfuse: Langfuse documentation (unknown)
- phoenix-bind: Phoenix listener source (arize-phoenix-v21.0.0)
- phoenix-bind-20: Phoenix listener source (arize-phoenix-v20.27.0)
- otel: OpenTelemetry Collector (v0.161.0)
- otel-dist: Collector distributions (v0.161.0)
- lf-session: Langfuse session source (24c949d8dd5617219a8415f80e4c65ad611ff05c)
- lf-compose: Langfuse Compose (0dd0a7fbe2feb300b8776f02b3684eeee3fbceab)
- phoenix: Phoenix documentation (unknown)
- phoenix-tls-min: Phoenix TLS announcement (unknown)
- phoenix-tls: Phoenix TLS source (arize-phoenix-v21.0.0)
- phoenix-auth: Phoenix auth source (arize-phoenix-v21.0.0)
- phoenix-auth-20: Phoenix auth source (arize-phoenix-v20.27.0)
- helicone: Helicone documentation (unknown)
- helicone-compose: Helicone Compose (b12ebaccb824ab9778757ca197ff302d97fda421)
- otel-docs: Collector security guidance (unknown)
- basicauth: Collector Basic auth extension (1c897ba9c67afc3c9e218b5cd05a6de49435f4de)
- bearertokenauth: Collector bearer token auth extension (1c897ba9c67afc3c9e218b5cd05a6de49435f4de)
- pprof: Collector pprof source (443567a6a00d7cff8cae1432a6fef655d8698e94)
- health: Collector health source (d922ffb299c6b9be026f97dd7d6a5f0f507efdeb)
- curl: curl minimum (7.75.0)

Claims (full source mapping in the JSON block below):

- lf-signup (REASONED; langfuse): Email/password and public signup default on; AUTH_DISABLE_SIGNUP=true also prevents invite acceptance by new users.
- lf-bootstrap (REASONED; langfuse): Create first account before closing signup, or initialize org before headless user/project with LANGFUSE_INIT_*.
- lf-sso (REASONED; langfuse): AUTH_DISABLE_USERNAME_PASSWORD=true requires SSO; supported Auth.js providers need correct NEXTAUTH_URL beyond password login.
- lf-session (REASONED; lf-session, langfuse): AUTH_SESSION_MAX_AGE must be integer &gt;5 minutes; source default is 20160, while documentation says 43200; check pinned release.
- lf-api (REASONED; langfuse): Ingestion/public API use project public-key username and secret-key password via Basic auth, separately from UI credentials.
- lf-mfa (REASONED; langfuse): Langfuse login has no native MFA; enforce it at the identity provider.
- lf-session-secret (REASONED; langfuse, lf-compose): Replace shipped NEXTAUTH_SECRET=mysecret before first start; known session protection secret permits forged sessions bypassing sign-in controls.
- lf-salt (REASONED; langfuse, lf-compose): Replace shipped SALT=mysalt used for API-key hashes with a separate random value.
- lf-encryption (REASONED; langfuse, lf-compose): Replace all-zero ENCRYPTION_KEY with 32 random hex bytes; later changes need re-encryption and exposed provider credentials need rotation.
- lf-minio (REASONED; lf-compose, langfuse): Rotate bundled minio/miniosecret and matching LANGFUSE_S3_* keys; MinIO S3 host 9090 is wildcard-published.
- lf-ports (REASONED; lf-compose): langfuse-web host 3000 is wildcard-published; bundled Postgres, ClickHouse and Redis default loopback; keep all publications private.
- lf-tls (REASONED; langfuse): Container deployment needs proxy TLS; an HTTPS public URL does not establish native Langfuse TLS.
- phoenix-enable (REASONED; phoenix, phoenix-auth, phoenix-auth-20): At 20.27.0 auth defaults off and needs PHOENIX_ENABLE_AUTH=True with PHOENIX_SECRET; at 21.0.0 an unset PHOENIX_ENABLE_AUTH turns auth on for any non-loopback PHOENIX_HOST, and PHOENIX_SECRET is optional, but without it saved credentials are readable by database readers; set both explicitly.
- phoenix-admin (REASONED; phoenix, phoenix-auth, phoenix-auth-20): Startup creates admin@localhost/admin unless PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD is set first; later changes are inert at 20.27.0, while 21.0.0 applies them only while the admin still has the default password, then ends its sessions.
- phoenix-password (REASONED; phoenix, phoenix-auth, phoenix-auth-20): Existing admin needs UI password replacement before exposure; admin/admin opens a session at 20.27.0 and gets a password-reset token at 21.0.0; remove the initial-password variable once the password is changed.
- phoenix-http (REASONED; phoenix-bind, phoenix-bind-20): HTTP UI/REST/OTLP binds PHOENIX_HOST, or --host at 20.27.0, defaulting to 0.0.0.0:6006 at 20.27.0 and 127.0.0.1:6006 at 21.0.0, whose Dockerfile sets PHOENIX_HOST=::; vendor Compose publishes 6006 and 4317 and lists PostgreSQL ports; restrict bind, publication and database exposure.
- phoenix-grpc (REASONED; phoenix-bind, phoenix-bind-20): Separate OTLP gRPC on 4317 binds [::] regardless of PHOENIX_HOST at 20.27.0 but binds PHOENIX_HOST, default 127.0.0.1, at 21.0.0; isolate namespace, publication and firewall separately.
- phoenix-keys (REASONED; phoenix, phoenix-bind, phoenix-auth): Enabling auth blocks collection/API access until system or user API keys exist; PHOENIX_API_KEY is sent as Bearer; at 21.0.0 a non-loopback PHOENIX_HOST with PHOENIX_ENABLE_AUTH unset enables auth on its own.
- phoenix-mfa (REASONED; phoenix): Documentation describes no native MFA and none was found in the 21.0.0 files read, though absence is not established; federate OAuth2/OIDC or use identity-aware ingress and enforce MFA there.
- phoenix-signup (REASONED; phoenix): PHOENIX_OAUTH2_&lt;IDP&gt;_ALLOW_SIGN_UP defaults True; set False and restrict provider membership.
- phoenix-basic (REASONED; phoenix): Local password login remains beside SSO; PHOENIX_DISABLE_BASIC_AUTH=True closes it after an approved IdP administrator is tested.
- phoenix-tls (REASONED; phoenix-tls-min, phoenix-tls): Native HTTP/gRPC TLS exists from 8.29, defaults off, uses certificate/key files; per-protocol switches overriding PHOENIX_TLS_ENABLED exist at 20.27.0 and 21.0.0, added in a release not established.
- helicone-login (REASONED; helicone): Better Auth uses signup and organizations; test@helicone.ai/password is a local manual trial, not the deployment security model.
- helicone-secret (REASONED; helicone, helicone-compose): Replace BETTER_AUTH_SECRET examples change-me-in-production and Compose your-secret-key before first start.
- helicone-ports (REASONED; helicone-compose): Backing Postgres/ClickHouse/MinIO/Redis/MailHog publications bypass UI login, including 54388:5432 and 18123:8123; remove or loopback-scope them.
- helicone-boundary (REASONED; helicone, helicone-compose): Restrict signup, protect dashboard/Jawn/S3 and gateway separately with private networking or authenticated ingress and MFA; rotate example storage credentials.
- helicone-ingest (REASONED; helicone): AI Gateway ingestion and provider environment keys are separate from web sessions; protect those secrets.
- otel-default (REASONED; otel, otel-docs): OTLP factory defaults localhost:4317 gRPC and localhost:4318 HTTP at v0.161.0; bind every enabled receiver explicitly.
- otel-history (REASONED; otel): OTLP localhost transition was v0.104.0; UseLocalHostAsDefaultHost stabilized v0.110.0 and was removed v0.112.0.
- otel-shipped (REASONED; otel-dist): Both shipped configs override component defaults with unauthenticated IPv4 wildcard OTLP 4317/4318, Jaeger 14250/6832/6831/14268 and Zipkin 9411.
- otel-diagnostics (REASONED; otel-dist, otel, pprof): Shipped pprof 1777 and zPages 55679 are wildcard and unauthenticated; remove from extensions/service.extensions or restrict separately.
- otel-images (REASONED; otel-dist): Dockerfiles COPY/select shipped config; EXPOSE 4317/4318/55679 is not host publication, but container peers may reach wildcard listeners.
- otel-packages (REASONED; otel-dist): Systemd reads distribution otelcol.conf; OTELCOL_OPTIONS selects config.yaml; config&#124;noreplace installation can retain local config, and postinstall manages service.
- otel-tls (REASONED; otel-docs): Require TLS on receivers/exporters and authentication on every receiver protocol accepting off-host data.
- otel-auth (REASONED; otel-docs, basicauth): Declare authenticator, start it in service.extensions, and attach each receiver protocol with auth.authenticator; Basic supports htpasswd/client_auth.
- otel-bearer (REASONED; otel-docs, bearertokenauth): bearertokenauth accepts a static token or token file; filename takes precedence over token, and each file line with a non-whitespace field contributes its first whitespace-delimited field. The configurable header (default Authorization) and scheme (default Bearer) apply to HTTP and gRPC outgoing calls; the header becomes the lower-case gRPC metadata key. On incoming requests, Authenticate checks the canonical HTTP header or lower-case gRPC metadata key and compares its first value with each configured scheme-prefixed token and accepts any match; outgoing calls send only the first token.
- otel-metrics (REASONED; otel, otel-dist): Internal metrics factory defaults localhost:8888; shipped configs set 127.0.0.1:8888; 0.0.0.0:8888 scrape target is outbound.
- otel-health (REASONED; health, otel-dist): Review enabled health-check 13133 independently of receiver authentication.
- otel-k8s (REASONED; otel-dist): otelcol-k8s Dockerfile supplies no default config COPY/CMD; EXPOSE alone establishes no listener; Helm/operator are out of scope.
- otel-minimal (REASONED; otel-docs): Run only required components and use a non-root process.
- verify-inventory (REASONED; otel-dist, otel-docs, phoenix-bind, phoenix-bind-20): Inspect effective config, namespace TCP/UDP, publications and firewall; shipped wildcard listeners should become intended private listeners; outside failures need positive controls.
- verify-dashboard (REASONED; langfuse): Langfuse curl is reachability only; fresh unauthenticated browser must show login rather than project data.
- verify-lf-api (REASONED; langfuse): Direct /api/public/projects pair should yield 401 without key and 200 with expected project ID; proxy-only results cannot prove native auth.
- verify-collector (REASONED; otel-docs, basicauth): Direct OTLP/HTTP JSON /v1/traces should reject anonymous 401/403 and admit configured auth 2xx; wrong content type and failed connections are inconclusive.
- verify-phoenix-admin (REASONED; phoenix, phoenix-auth, phoenix-auth-20): Default admin/admin must fail, with a 20.27.0 session or a 21.0.0 reset token both exposed, and the replacement password must succeed; with basic auth disabled, require local-login refusal and approved MFA IdP success.
- verify-phoenix-read (REASONED; phoenix, phoenix-auth, curl): Anonymous /v1/projects should reject 401/403, versus exposed project data 2xx; 404, redirect, 415 and transport errors are inconclusive.
- verify-phoenix-http (REASONED; phoenix, phoenix-auth): Empty protobuf POST /v1/traces on 6006 tests admission, not persistence: anonymous rejects, write-authorized key admits, viewer key gets 403 and is not a positive control.
- verify-phoenix-grpc (REASONED; phoenix-auth, phoenix-bind, phoenix-bind-20): Separate empty gRPC TraceService/Export requires UNAUTHENTICATED without key, OK with write key; auth-off anonymous OK and viewer PERMISSION_DENIED remain source-reasoned.

````json
{
  "schema": 1,
  "checked": "2026-11-04",
  "documentation_checked": "2026-09",
  "body_sha256": "91b2536cf14b254076554c6abc38baa1f56c92074e663cf234f1b22af68b5ae5",
  "components": {
    "langfuse": {
      "name": "Langfuse documentation",
      "basis": "unknown",
      "sources": {
        "s34b0fb076e86": "https://langfuse.com/self-hosting/security/authentication-and-sso",
        "sfdfc0ea9fdc1": "https://langfuse.com/docs/api-and-data-platform/features/public-api",
        "sb92c8a6aaad1": "https://langfuse.com/self-hosting/configuration",
        "scd1d81693f96": "https://langfuse.com/self-hosting/administration/headless-initialization"
      }
    },
    "phoenix-bind": {
      "name": "Phoenix listener source",
      "basis": "arize-phoenix-v21.0.0",
      "sources": {
        "s1e4c3ebd33de": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/config.py#L55-L59",
        "se0340e8cbaba": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/config.py#L3166-L3172",
        "s4618901856d4": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/config.py#L3425-L3447",
        "s74e11942206c": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/grpc_server.py#L55-L82",
        "s1b9b41c2b9da": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/grpc_server.py#L109-L131",
        "s9294363c778c": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/cli/commands/serve.py#L238-L246",
        "s4746650f1449": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/cli/commands/serve.py#L363-L393",
        "sfcdf7957ab53": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/app.py#L1007-L1014",
        "s22756c69d535": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/app.py#L1060-L1069",
        "s62273aeb92e3": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/app.py#L704-L739",
        "s93abe2c011ec": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/Dockerfile#L160-L174",
        "s8402a7dc0c90": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/MIGRATION.md#L3-L63",
        "s053ea1feac0e": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/docker-compose.yml#L1-L23"
      }
    },
    "phoenix-bind-20": {
      "name": "Phoenix listener source",
      "basis": "arize-phoenix-v20.27.0",
      "sources": {
        "scfb88225f2ad": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/config.py#L3131-L3137",
        "s68717d339677": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/config.py#L3364-L3365",
        "sab369cec4af9": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/server/grpc_server.py#L55-L80",
        "s78a38870f8ea": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/server/grpc_server.py#L107-L109",
        "s27bd68072127": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/server/cli/commands/serve.py#L148-L160",
        "s566f5ab791a7": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/server/cli/commands/serve.py#L244-L253",
        "s8fb8f6b9d2f3": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/server/cli/commands/serve.py#L383-L417",
        "sd9548a2295ae": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/server/app.py#L694-L702",
        "s5f40ca1e1785": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/server/app.py#L1018-L1027",
        "s6c614a43f382": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/Dockerfile#L160-L172"
      }
    },
    "otel": {
      "name": "OpenTelemetry Collector",
      "basis": "v0.161.0",
      "sources": {
        "s6eb17ad3eb47": "https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/receiver/otlpreceiver/factory.go#L41-L67",
        "s3252b8ba9775": "https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/CHANGELOG.md#L2058-L2070",
        "s5a13f52d7e6d": "https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/CHANGELOG.md#L1793-L1811",
        "sb419d6444c19": "https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/CHANGELOG.md#L1737-L1743",
        "s9780bf233e75": "https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/service/telemetry/otelconftelemetry/factory.go#L49-L64",
        "se93854d097ec": "https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/extension/zpagesextension/factory.go#L15-L29",
        "s6957342b0bf4": "https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/extension/zpagesextension/zpagesextension.go#L87-L105",
        "sdac173d533e6": "https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/config/confighttp/server.go#L352-L364"
      }
    },
    "otel-dist": {
      "name": "Collector distributions",
      "basis": "v0.161.0",
      "sources": {
        "s08ca284a6d6f": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/config.yaml#L1-L81",
        "s9d2ef3c6b75d": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/config.yaml#L1-L81",
        "s7a517873f7be": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/Dockerfile#L10-L15",
        "sc806e2cc23e6": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/Dockerfile#L10-L15",
        "s96832924ecbd": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/.goreleaser.yaml#L86-L118",
        "s3cf497a4401c": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/.goreleaser.yaml#L94-L126",
        "s532d68e28e68": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/otelcol.service#L5-L7",
        "saa59feb48156": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/otelcol-contrib.service#L5-L7",
        "s73f6337cd50e": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/otelcol.conf#L1-L5",
        "sff25af5f7a79": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/otelcol-contrib.conf#L1-L5",
        "sd829f5067d73": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/postinstall.sh#L6-L16",
        "secd03f9c13d6": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/postinstall.sh#L6-L16",
        "s353fc01c0b2c": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/postinstall-rpm.sh#L6-L9",
        "s72fc7a0602d1": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/postinstall-rpm.sh#L6-L9",
        "sb93573df35e2": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-k8s/Dockerfile#L1-L17"
      }
    },
    "lf-session": {
      "name": "Langfuse session source",
      "basis": "24c949d8dd5617219a8415f80e4c65ad611ff05c",
      "sources": {
        "s01522120437c": "https://github.com/langfuse/langfuse/blob/24c949d8dd5617219a8415f80e4c65ad611ff05c/web/src/env.mjs"
      }
    },
    "lf-compose": {
      "name": "Langfuse Compose",
      "basis": "0dd0a7fbe2feb300b8776f02b3684eeee3fbceab",
      "sources": {
        "s4d19a7b83526": "https://github.com/langfuse/langfuse/blob/0dd0a7fbe2feb300b8776f02b3684eeee3fbceab/docker-compose.yml"
      }
    },
    "phoenix": {
      "name": "Phoenix documentation",
      "basis": "unknown",
      "sources": {
        "s5a90699b7950": "https://arize.com/docs/phoenix/self-hosting/features/authentication"
      }
    },
    "phoenix-tls-min": {
      "name": "Phoenix TLS announcement",
      "basis": "unknown",
      "sources": {
        "s8af9d57a7636": "https://arize.com/docs/phoenix/release-notes/04-2025/04-28-2025-tls-support-for-phoenix-server"
      }
    },
    "phoenix-tls": {
      "name": "Phoenix TLS source",
      "basis": "arize-phoenix-v21.0.0",
      "sources": {
        "s8c5c46660f2a": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/config.py#L853-L874",
        "s3ed506b65674": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/config.py#L1032-L1057"
      }
    },
    "phoenix-auth": {
      "name": "Phoenix auth source",
      "basis": "arize-phoenix-v21.0.0",
      "sources": {
        "s253973703f36": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/bearer_auth.py#L152-L190",
        "s036fb8ea6f51": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/config.py#L415-L467",
        "sdbaa6371c568": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/config.py#L1274-L1278",
        "s438ca2a1d10a": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/config.py#L1509-L1534",
        "s921dc8bddc0a": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/db/facilitator.py#L115-L219",
        "s9b5694263627": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/api/routers/auth.py#L147-L198",
        "sb292bb2171aa": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/api/routers/auth.py#L311-L341",
        "se91e507879d3": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/api/routers/v1/__init__.py#L35-L83",
        "sc7c47b61ba20": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/bearer_auth.py#L213-L282",
        "sb802793835cd": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/authorization.py#L73-L84",
        "s00e9a72f392a": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/api/routers/v1/projects.py#L66-L67",
        "se7438e02fc6a": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v21.0.0/src/phoenix/server/api/routers/v1/traces.py#L431-L433"
      }
    },
    "phoenix-auth-20": {
      "name": "Phoenix auth source",
      "basis": "arize-phoenix-v20.27.0",
      "sources": {
        "s710acd292052": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/config.py#L403-L449",
        "sbb3f3e1ef927": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/config.py#L1256-L1260",
        "s530d72b9665c": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/config.py#L1491-L1501",
        "s048f854055c7": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/db/facilitator.py#L113-L160",
        "sabe5c0470bf0": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/server/app.py#L972",
        "s8a3e177589da": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.27.0/src/phoenix/server/api/routers/auth.py#L144-L186"
      }
    },
    "helicone": {
      "name": "Helicone documentation",
      "basis": "unknown",
      "sources": {
        "s48d6e38bf1fa": "https://docs.helicone.ai/getting-started/self-host/manual",
        "sac4298a08e00": "https://docs.helicone.ai/getting-started/self-host/docker"
      }
    },
    "helicone-compose": {
      "name": "Helicone Compose",
      "basis": "b12ebaccb824ab9778757ca197ff302d97fda421",
      "sources": {
        "s05ca7cfb09fe": "https://github.com/Helicone/helicone/blob/b12ebaccb824ab9778757ca197ff302d97fda421/docker/docker-compose.yml"
      }
    },
    "otel-docs": {
      "name": "Collector security guidance",
      "basis": "unknown",
      "sources": {
        "s5fc11440844b": "https://opentelemetry.io/docs/security/config-best-practices/"
      }
    },
    "basicauth": {
      "name": "Collector Basic auth extension",
      "basis": "1c897ba9c67afc3c9e218b5cd05a6de49435f4de",
      "sources": {
        "s473397b3887e": "https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/basicauthextension"
      }
    },
    "bearertokenauth": {
      "name": "Collector bearer token auth extension",
      "basis": "1c897ba9c67afc3c9e218b5cd05a6de49435f4de",
      "sources": {
        "sc102b008afb0": "https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/bearertokenauthextension/README.md#L21-L39",
        "s664ba81d1aa6": "https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/bearertokenauthextension/bearertokenauth.go#L30-L43",
        "saa550790364b": "https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/bearertokenauthextension/bearertokenauth.go#L73-L122",
        "s93d4733c051d": "https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/bearertokenauthextension/bearertokenauth.go#L156-L189",
        "s828ec6427328": "https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/bearertokenauthextension/bearertokenauth.go#L197-L205",
        "s48a3bfa9c99e": "https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/bearertokenauthextension/bearertokenauth.go#L234-L255",
        "s4326cb59f96e": "https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/bearertokenauthextension/bearertokenauth.go#L264-L272",
        "sa8d47408d195": "https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/bearertokenauthextension/factory.go#L15-L18"
      }
    },
    "pprof": {
      "name": "Collector pprof source",
      "basis": "443567a6a00d7cff8cae1432a6fef655d8698e94",
      "sources": {
        "s3f2efc571022": "https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/443567a6a00d7cff8cae1432a6fef655d8698e94/extension/pprofextension/README.md"
      }
    },
    "health": {
      "name": "Collector health source",
      "basis": "d922ffb299c6b9be026f97dd7d6a5f0f507efdeb",
      "sources": {
        "s6ac60517accc": "https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/d922ffb299c6b9be026f97dd7d6a5f0f507efdeb/extension/healthcheckextension/README.md"
      }
    },
    "curl": {
      "name": "curl minimum",
      "basis": "7.75.0",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    }
  },
  "claims": {
    "lf-signup": {"text": "Email/password and public signup default on; AUTH_DISABLE_SIGNUP=true also prevents invite acceptance by new users.", "components": ["langfuse"], "sources": ["langfuse:s34b0fb076e86"], "status": "REASONED"},
    "lf-bootstrap": {"text": "Create first account before closing signup, or initialize org before headless user/project with LANGFUSE_INIT_*.", "components": ["langfuse"], "sources": ["langfuse:scd1d81693f96", "langfuse:s34b0fb076e86"], "status": "REASONED"},
    "lf-sso": {"text": "AUTH_DISABLE_USERNAME_PASSWORD=true requires SSO; supported Auth.js providers need correct NEXTAUTH_URL beyond password login.", "components": ["langfuse"], "sources": ["langfuse:s34b0fb076e86"], "status": "REASONED"},
    "lf-session": {"text": "AUTH_SESSION_MAX_AGE must be integer >5 minutes; source default is 20160, while documentation says 43200; check pinned release.", "components": ["lf-session", "langfuse"], "sources": ["lf-session:s01522120437c", "langfuse:s34b0fb076e86"], "status": "REASONED"},
    "lf-api": {"text": "Ingestion/public API use project public-key username and secret-key password via Basic auth, separately from UI credentials.", "components": ["langfuse"], "sources": ["langfuse:sfdfc0ea9fdc1"], "status": "REASONED"},
    "lf-mfa": {"text": "Langfuse login has no native MFA; enforce it at the identity provider.", "components": ["langfuse"], "sources": ["langfuse:s34b0fb076e86"], "status": "REASONED"},
    "lf-session-secret": {"text": "Replace shipped NEXTAUTH_SECRET=mysecret before first start; known session protection secret permits forged sessions bypassing sign-in controls.", "components": ["langfuse", "lf-compose"], "sources": ["langfuse:sb92c8a6aaad1", "lf-compose:s4d19a7b83526"], "status": "REASONED"},
    "lf-salt": {"text": "Replace shipped SALT=mysalt used for API-key hashes with a separate random value.", "components": ["langfuse", "lf-compose"], "sources": ["langfuse:sb92c8a6aaad1", "lf-compose:s4d19a7b83526"], "status": "REASONED"},
    "lf-encryption": {"text": "Replace all-zero ENCRYPTION_KEY with 32 random hex bytes; later changes need re-encryption and exposed provider credentials need rotation.", "components": ["langfuse", "lf-compose"], "sources": ["langfuse:sb92c8a6aaad1", "lf-compose:s4d19a7b83526"], "status": "REASONED"},
    "lf-minio": {"text": "Rotate bundled minio/miniosecret and matching LANGFUSE_S3_* keys; MinIO S3 host 9090 is wildcard-published.", "components": ["lf-compose", "langfuse"], "sources": ["lf-compose:s4d19a7b83526", "langfuse:sb92c8a6aaad1"], "status": "REASONED"},
    "lf-ports": {"text": "langfuse-web host 3000 is wildcard-published; bundled Postgres, ClickHouse and Redis default loopback; keep all publications private.", "components": ["lf-compose"], "sources": ["lf-compose:s4d19a7b83526"], "status": "REASONED"},
    "lf-tls": {"text": "Container deployment needs proxy TLS; an HTTPS public URL does not establish native Langfuse TLS.", "components": ["langfuse"], "sources": ["langfuse:sb92c8a6aaad1"], "status": "REASONED"},
    "phoenix-enable": {"text": "At 20.27.0 auth defaults off and needs PHOENIX_ENABLE_AUTH=True with PHOENIX_SECRET; at 21.0.0 an unset PHOENIX_ENABLE_AUTH turns auth on for any non-loopback PHOENIX_HOST, and PHOENIX_SECRET is optional, but without it saved credentials are readable by database readers; set both explicitly.", "components": ["phoenix", "phoenix-auth", "phoenix-auth-20"], "sources": ["phoenix:s5a90699b7950", "phoenix-auth:s036fb8ea6f51", "phoenix-auth:sdbaa6371c568", "phoenix-auth:s438ca2a1d10a", "phoenix-auth-20:sbb3f3e1ef927", "phoenix-auth-20:s530d72b9665c"], "status": "REASONED"},
    "phoenix-admin": {"text": "Startup creates admin@localhost/admin unless PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD is set first; later changes are inert at 20.27.0, while 21.0.0 applies them only while the admin still has the default password, then ends its sessions.", "components": ["phoenix", "phoenix-auth", "phoenix-auth-20"], "sources": ["phoenix:s5a90699b7950", "phoenix-auth:s036fb8ea6f51", "phoenix-auth:s921dc8bddc0a", "phoenix-auth-20:s710acd292052", "phoenix-auth-20:s048f854055c7", "phoenix-auth-20:sabe5c0470bf0"], "status": "REASONED"},
    "phoenix-password": {"text": "Existing admin needs UI password replacement before exposure; admin/admin opens a session at 20.27.0 and gets a password-reset token at 21.0.0; remove the initial-password variable once the password is changed.", "components": ["phoenix", "phoenix-auth", "phoenix-auth-20"], "sources": ["phoenix:s5a90699b7950", "phoenix-auth:s9b5694263627", "phoenix-auth:sb292bb2171aa", "phoenix-auth-20:s8a3e177589da"], "status": "REASONED"},
    "phoenix-http": {"text": "HTTP UI/REST/OTLP binds PHOENIX_HOST, or --host at 20.27.0, defaulting to 0.0.0.0:6006 at 20.27.0 and 127.0.0.1:6006 at 21.0.0, whose Dockerfile sets PHOENIX_HOST=::; vendor Compose publishes 6006 and 4317 and lists PostgreSQL ports; restrict bind, publication and database exposure.", "components": ["phoenix-bind", "phoenix-bind-20"], "sources": ["phoenix-bind:s1e4c3ebd33de", "phoenix-bind:se0340e8cbaba", "phoenix-bind:s4618901856d4", "phoenix-bind:s9294363c778c", "phoenix-bind:s4746650f1449", "phoenix-bind:s93abe2c011ec", "phoenix-bind:s8402a7dc0c90", "phoenix-bind:s053ea1feac0e", "phoenix-bind-20:scfb88225f2ad", "phoenix-bind-20:s68717d339677", "phoenix-bind-20:s27bd68072127", "phoenix-bind-20:s566f5ab791a7", "phoenix-bind-20:s8fb8f6b9d2f3", "phoenix-bind-20:s6c614a43f382"], "status": "REASONED"},
    "phoenix-grpc": {"text": "Separate OTLP gRPC on 4317 binds [::] regardless of PHOENIX_HOST at 20.27.0 but binds PHOENIX_HOST, default 127.0.0.1, at 21.0.0; isolate namespace, publication and firewall separately.", "components": ["phoenix-bind", "phoenix-bind-20"], "sources": ["phoenix-bind:se0340e8cbaba", "phoenix-bind:s74e11942206c", "phoenix-bind:s1b9b41c2b9da", "phoenix-bind:sfcdf7957ab53", "phoenix-bind:s62273aeb92e3", "phoenix-bind:s4746650f1449", "phoenix-bind-20:s78a38870f8ea", "phoenix-bind-20:sd9548a2295ae"], "status": "REASONED"},
    "phoenix-keys": {"text": "Enabling auth blocks collection/API access until system or user API keys exist; PHOENIX_API_KEY is sent as Bearer; at 21.0.0 a non-loopback PHOENIX_HOST with PHOENIX_ENABLE_AUTH unset enables auth on its own.", "components": ["phoenix", "phoenix-bind", "phoenix-auth"], "sources": ["phoenix:s5a90699b7950", "phoenix-bind:s8402a7dc0c90", "phoenix-auth:sdbaa6371c568"], "status": "REASONED"},
    "phoenix-mfa": {"text": "Documentation describes no native MFA and none was found in the 21.0.0 files read, though absence is not established; federate OAuth2/OIDC or use identity-aware ingress and enforce MFA there.", "components": ["phoenix"], "sources": ["phoenix:s5a90699b7950"], "status": "REASONED"},
    "phoenix-signup": {"text": "PHOENIX_OAUTH2_<IDP>_ALLOW_SIGN_UP defaults True; set False and restrict provider membership.", "components": ["phoenix"], "sources": ["phoenix:s5a90699b7950"], "status": "REASONED"},
    "phoenix-basic": {"text": "Local password login remains beside SSO; PHOENIX_DISABLE_BASIC_AUTH=True closes it after an approved IdP administrator is tested.", "components": ["phoenix"], "sources": ["phoenix:s5a90699b7950"], "status": "REASONED"},
    "phoenix-tls": {"text": "Native HTTP/gRPC TLS exists from 8.29, defaults off, uses certificate/key files; per-protocol switches overriding PHOENIX_TLS_ENABLED exist at 20.27.0 and 21.0.0, added in a release not established.", "components": ["phoenix-tls-min", "phoenix-tls"], "sources": ["phoenix-tls-min:s8af9d57a7636", "phoenix-tls:s8c5c46660f2a", "phoenix-tls:s3ed506b65674"], "status": "REASONED"},
    "helicone-login": {"text": "Better Auth uses signup and organizations; test@helicone.ai/password is a local manual trial, not the deployment security model.", "components": ["helicone"], "sources": ["helicone:s48d6e38bf1fa", "helicone:sac4298a08e00"], "status": "REASONED"},
    "helicone-secret": {"text": "Replace BETTER_AUTH_SECRET examples change-me-in-production and Compose your-secret-key before first start.", "components": ["helicone", "helicone-compose"], "sources": ["helicone:sac4298a08e00", "helicone-compose:s05ca7cfb09fe"], "status": "REASONED"},
    "helicone-ports": {"text": "Backing Postgres/ClickHouse/MinIO/Redis/MailHog publications bypass UI login, including 54388:5432 and 18123:8123; remove or loopback-scope them.", "components": ["helicone-compose"], "sources": ["helicone-compose:s05ca7cfb09fe"], "status": "REASONED"},
    "helicone-boundary": {"text": "Restrict signup, protect dashboard/Jawn/S3 and gateway separately with private networking or authenticated ingress and MFA; rotate example storage credentials.", "components": ["helicone", "helicone-compose"], "sources": ["helicone:sac4298a08e00", "helicone-compose:s05ca7cfb09fe"], "status": "REASONED"},
    "helicone-ingest": {"text": "AI Gateway ingestion and provider environment keys are separate from web sessions; protect those secrets.", "components": ["helicone"], "sources": ["helicone:sac4298a08e00"], "status": "REASONED"},
    "otel-default": {"text": "OTLP factory defaults localhost:4317 gRPC and localhost:4318 HTTP at v0.161.0; bind every enabled receiver explicitly.", "components": ["otel", "otel-docs"], "sources": ["otel:s6eb17ad3eb47", "otel-docs:s5fc11440844b"], "status": "REASONED"},
    "otel-history": {"text": "OTLP localhost transition was v0.104.0; UseLocalHostAsDefaultHost stabilized v0.110.0 and was removed v0.112.0.", "components": ["otel"], "sources": ["otel:s3252b8ba9775", "otel:s5a13f52d7e6d", "otel:sb419d6444c19"], "status": "REASONED"},
    "otel-shipped": {"text": "Both shipped configs override component defaults with unauthenticated IPv4 wildcard OTLP 4317/4318, Jaeger 14250/6832/6831/14268 and Zipkin 9411.", "components": ["otel-dist"], "sources": ["otel-dist:s08ca284a6d6f", "otel-dist:s9d2ef3c6b75d"], "status": "REASONED"},
    "otel-diagnostics": {"text": "Shipped pprof 1777 and zPages 55679 are wildcard and unauthenticated; remove from extensions/service.extensions or restrict separately.", "components": ["otel-dist", "otel", "pprof"], "sources": ["otel-dist:s08ca284a6d6f", "otel-dist:s9d2ef3c6b75d", "otel:se93854d097ec", "otel:s6957342b0bf4", "otel:sdac173d533e6", "pprof:s3f2efc571022"], "status": "REASONED"},
    "otel-images": {"text": "Dockerfiles COPY/select shipped config; EXPOSE 4317/4318/55679 is not host publication, but container peers may reach wildcard listeners.", "components": ["otel-dist"], "sources": ["otel-dist:s7a517873f7be", "otel-dist:sc806e2cc23e6"], "status": "REASONED"},
    "otel-packages": {"text": "Systemd reads distribution otelcol.conf; OTELCOL_OPTIONS selects config.yaml; config|noreplace installation can retain local config, and postinstall manages service.", "components": ["otel-dist"], "sources": ["otel-dist:s96832924ecbd", "otel-dist:s3cf497a4401c", "otel-dist:s532d68e28e68", "otel-dist:saa59feb48156", "otel-dist:s73f6337cd50e", "otel-dist:sff25af5f7a79", "otel-dist:sd829f5067d73", "otel-dist:secd03f9c13d6", "otel-dist:s353fc01c0b2c", "otel-dist:s72fc7a0602d1"], "status": "REASONED"},
    "otel-tls": {"text": "Require TLS on receivers/exporters and authentication on every receiver protocol accepting off-host data.", "components": ["otel-docs"], "sources": ["otel-docs:s5fc11440844b"], "status": "REASONED"},
    "otel-auth": {"text": "Declare authenticator, start it in service.extensions, and attach each receiver protocol with auth.authenticator; Basic supports htpasswd/client_auth.", "components": ["otel-docs", "basicauth"], "sources": ["otel-docs:s5fc11440844b", "basicauth:s473397b3887e"], "status": "REASONED"},
    "otel-bearer": {"text": "bearertokenauth accepts a static token or token file; filename takes precedence over token, and each file line with a non-whitespace field contributes its first whitespace-delimited field. The configurable header (default Authorization) and scheme (default Bearer) apply to HTTP and gRPC outgoing calls; the header becomes the lower-case gRPC metadata key. On incoming requests, Authenticate checks the canonical HTTP header or lower-case gRPC metadata key and compares its first value with each configured scheme-prefixed token and accepts any match; outgoing calls send only the first token.", "components": ["otel-docs", "bearertokenauth"], "sources": ["otel-docs:s5fc11440844b", "bearertokenauth:sc102b008afb0", "bearertokenauth:s664ba81d1aa6", "bearertokenauth:saa550790364b", "bearertokenauth:s93d4733c051d", "bearertokenauth:s828ec6427328", "bearertokenauth:s48a3bfa9c99e", "bearertokenauth:s4326cb59f96e", "bearertokenauth:sa8d47408d195"], "status": "REASONED"},
    "otel-metrics": {"text": "Internal metrics factory defaults localhost:8888; shipped configs set 127.0.0.1:8888; 0.0.0.0:8888 scrape target is outbound.", "components": ["otel", "otel-dist"], "sources": ["otel:s9780bf233e75", "otel-dist:s08ca284a6d6f", "otel-dist:s9d2ef3c6b75d"], "status": "REASONED"},
    "otel-health": {"text": "Review enabled health-check 13133 independently of receiver authentication.", "components": ["health", "otel-dist"], "sources": ["health:s6ac60517accc", "otel-dist:s08ca284a6d6f", "otel-dist:s9d2ef3c6b75d"], "status": "REASONED"},
    "otel-k8s": {"text": "otelcol-k8s Dockerfile supplies no default config COPY/CMD; EXPOSE alone establishes no listener; Helm/operator are out of scope.", "components": ["otel-dist"], "sources": ["otel-dist:sb93573df35e2"], "status": "REASONED"},
    "otel-minimal": {"text": "Run only required components and use a non-root process.", "components": ["otel-docs"], "sources": ["otel-docs:s5fc11440844b"], "status": "REASONED"},
    "verify-inventory": {"text": "Inspect effective config, namespace TCP/UDP, publications and firewall; shipped wildcard listeners should become intended private listeners; outside failures need positive controls.", "components": ["otel-dist", "otel-docs", "phoenix-bind", "phoenix-bind-20"], "sources": ["otel-dist:s08ca284a6d6f", "otel-dist:s9d2ef3c6b75d", "otel-docs:s5fc11440844b", "phoenix-bind:se0340e8cbaba", "phoenix-bind:s1b9b41c2b9da", "phoenix-bind-20:scfb88225f2ad", "phoenix-bind-20:s78a38870f8ea"], "status": "REASONED", "verify": [1]},
    "verify-dashboard": {"text": "Langfuse curl is reachability only; fresh unauthenticated browser must show login rather than project data.", "components": ["langfuse"], "sources": ["langfuse:s34b0fb076e86"], "status": "REASONED", "verify": [2]},
    "verify-lf-api": {"text": "Direct /api/public/projects pair should yield 401 without key and 200 with expected project ID; proxy-only results cannot prove native auth.", "components": ["langfuse"], "sources": ["langfuse:sfdfc0ea9fdc1"], "status": "REASONED", "verify": [2]},
    "verify-collector": {"text": "Direct OTLP/HTTP JSON /v1/traces should reject anonymous 401/403 and admit configured auth 2xx; wrong content type and failed connections are inconclusive.", "components": ["otel-docs", "basicauth"], "sources": ["otel-docs:s5fc11440844b", "basicauth:s473397b3887e"], "status": "REASONED", "verify": [3]},
    "verify-phoenix-admin": {"text": "Default admin/admin must fail, with a 20.27.0 session or a 21.0.0 reset token both exposed, and the replacement password must succeed; with basic auth disabled, require local-login refusal and approved MFA IdP success.", "components": ["phoenix", "phoenix-auth", "phoenix-auth-20"], "sources": ["phoenix:s5a90699b7950", "phoenix-auth:s9b5694263627", "phoenix-auth-20:s8a3e177589da"], "status": "REASONED"},
    "verify-phoenix-read": {"text": "Anonymous /v1/projects should reject 401/403, versus exposed project data 2xx; 404, redirect, 415 and transport errors are inconclusive.", "components": ["phoenix", "phoenix-auth", "curl"], "sources": ["phoenix:s5a90699b7950", "phoenix-auth:se91e507879d3", "phoenix-auth:sc7c47b61ba20", "phoenix-auth:s00e9a72f392a", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [4]},
    "verify-phoenix-http": {"text": "Empty protobuf POST /v1/traces on 6006 tests admission, not persistence: anonymous rejects, write-authorized key admits, viewer key gets 403 and is not a positive control.", "components": ["phoenix", "phoenix-auth"], "sources": ["phoenix:s5a90699b7950", "phoenix-auth:se91e507879d3", "phoenix-auth:sc7c47b61ba20", "phoenix-auth:sb802793835cd", "phoenix-auth:se7438e02fc6a"], "status": "REASONED"},
    "verify-phoenix-grpc": {"text": "Separate empty gRPC TraceService/Export requires UNAUTHENTICATED without key, OK with write key; auth-off anonymous OK and viewer PERMISSION_DENIED remain source-reasoned.", "components": ["phoenix-auth", "phoenix-bind", "phoenix-bind-20"], "sources": ["phoenix-auth:s253973703f36", "phoenix-bind:s74e11942206c", "phoenix-bind:s1b9b41c2b9da", "phoenix-bind:s22756c69d535", "phoenix-bind-20:sab369cec4af9", "phoenix-bind-20:s78a38870f8ea", "phoenix-bind-20:s5f40ca1e1785"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
