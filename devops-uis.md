# DevOps panels: Portainer, Coolify, Dokploy, Nginx Proxy Manager, Vaultwarden, Kubernetes Dashboard, Jenkins, Gitea, Uptime Kuma, and the Docker API

Portainer, Coolify, Dokploy, Nginx Proxy Manager, Vaultwarden, Kubernetes Dashboard, Jenkins, Gitea, Uptime Kuma, Dozzle, Docker Registry, Filebrowser, Node-RED and Docker's API handle infrastructure, monitoring or secrets. This guide helps your AI assistant secure each, including private access, authentication, human MFA and any first-visit admin account claimed before exposure.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/devops-uis.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against Portainer (no recorded version), Dashboard arguments v2.7.0, Gitea source v28.3.0, Gitea 1.x source v1.27.3, Gitea MFA minimum 1.24, and Apache htpasswd 2.4; 2 further sources are pinned to a commit and 13 carry no recorded version. Metadata reviewed 2026-11-04; documentation checked September 2026. The guide records 57 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

These panels control hosts, containers, clusters, deploy keys, and secrets; a login to one of them is a login to everything it manages. One rule dominates everything tool-specific below: **a DevOps panel is never reachable from the public internet.** Bind it to loopback or a private interface and reach it through SSH port forwarding, a tailnet ([tailscale.md](tailscale.md)), or Cloudflare Access ([cloudflare.md](cloudflare.md)); anything that must be public sits behind a TLS proxy with its own authentication ([nginx.md](nginx.md), [caddy.md](caddy.md)) and the admin login gets MFA ([mfa.md](mfa.md)). Several of these tools create their administrator on first visit, so whoever reaches a fresh install first owns it: create the account before the port is reachable by anyone else.

## Portainer

- Serves the UI over HTTPS on `9443` (self-signed by default; supply your own certificate or front it per [nginx.md](nginx.md)). `9000` is the legacy HTTP port and stays unpublished; `8000` is the Edge agent tunnel and is only published when Edge Compute is in use.
- New instances require a setup token to complete first-time setup; it is in the server logs on the `setup_token=` line. The first user is an administrator, and its password must be at least 12 characters.
- Authentication is internal, LDAP, Active Directory, or OAuth (Microsoft, Google, GitHub, or a custom provider). Portainer's own login has no second factor in its documentation; use OAuth against a provider that enforces MFA ([identity-providers.md](identity-providers.md)).
- The container mounts `/var/run/docker.sock`, which is root on the host; a Portainer admin is a host root user ([docker.md](docker.md)).

## Coolify and Dokploy

Both are one-script installs that hold your servers' SSH private keys, Git provider credentials, and application secrets, and both create their administrator on first visit.

- Coolify's dashboard answers on `8000` over plain HTTP after install. Its documentation says to create the admin account immediately, because whoever reaches the registration page first can gain full control of the server. Set the instance a custom domain on the `/settings` page; the integrated proxy (Traefik by default, or Caddy) then issues and renews a Let's Encrypt certificate, and the firewall guide says ports `8000`, `6001`, and `6002` can be closed once the dashboard is reached through that domain. Docker's iptables rules bypass UFW, so restrict these ports with the cloud provider's firewall ([cloud-firewalls.md](cloud-firewalls.md)). Coolify requires the server SSH key to have no passphrase, so the key material inside Coolify is the whole secret.
- Dokploy's UI answers on `3000`; ports `80` and `443` belong to its Traefik. The first visit is the setup page that creates the admin account. Configure a domain with a Let's Encrypt or custom certificate for the panel under Domains, then remove the published `3000` binding so the panel is reachable only through the proxy.

## Nginx Proxy Manager

The admin UI is on port `81`; the proxy itself is on `80`/`443`. Port `81` is never published to the internet: bind it to `127.0.0.1` in the compose file (`'127.0.0.1:81:81'`) and reach it through a tunnel. A default admin user is created on the first run; change the initial admin credentials on first login, before anything else. Since it terminates TLS for every site behind it, treat its login like a root password.

## Vaultwarden

- The web vault needs HTTPS (browsers expose the crypto APIs it uses only in secure contexts). The wiki recommends a reverse proxy for TLS ([caddy.md](caddy.md), [nginx.md](nginx.md)) and rates the built-in `ROCKET_TLS` as not recommended. Set `DOMAIN=https://vault.example.com`.
- `SIGNUPS_ALLOWED=false` (the default is `true`, letting anyone who reaches the instance register). Organization owners and admins can still invite users while `INVITATIONS_ALLOWED=true`; `SIGNUPS_DOMAINS_WHITELIST` admits specific email domains.
- The admin page is disabled unless `ADMIN_TOKEN` is set. Store it as an argon2id PHC string generated with `vaultwarden hash` (or `docker run --rm -it vaultwarden/server /vaultwarden hash`), never plaintext; in a compose `environment:` block every `$` in the hash becomes `$$`. Enter the password at the tool's prompt; Sources has no reference for `vaultwarden hash` prompting (its Vaultwarden entry is described as covering the admin page and `ADMIN_TOKEN`, registration, HTTPS and the `.env.template`), so confirm that it does before relying on it. A prompt keeps the password out of the command text, shell history and shell tracing; the account owner and root can still read it in the `vaultwarden` process while it runs, and in the `docker run -it` form the `docker` client relays it, so anyone who can use the Docker daemon can read it too. Enable HTTPS before enabling the admin page. Admin sessions expire after 20 minutes by default.
- Inside a container it listens on `80` (`8000` outside Docker); publish it only to loopback or the proxy network.

## Kubernetes Dashboard

- As of September 2026 the Kubernetes documentation marks the Dashboard deprecated and unmaintained (the repository was archived in January 2026) and points new installs to Headlamp; the pattern below applies to any cluster UI.
- Do not expose it with a LoadBalancer or Ingress. Reach it from the operator's machine with `kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard-kong-proxy 8443:443` and open `https://localhost:8443`; the UI is then reachable only from that machine.
- Login is by bearer token of a ServiceAccount with a minimal RBAC role; the tutorial's sample user is cluster-admin and is for demonstration only. On the older 2.x releases, `--enable-skip-login` and `--enable-insecure-login` both default to `false`; never turn them on.
- A ServiceAccount token is a machine credential, so configuring OIDC on the API server puts no MFA on this login. Human MFA comes from the access path (a port-forward over SSH from a machine that already required it, a tailnet per [tailscale.md](tailscale.md), or Cloudflare Access per [cloudflare.md](cloudflare.md)) or from a UI that performs an identity-provider login itself; see [mfa.md](mfa.md).

## Jenkins

- Authentication (the security realm: Jenkins' own user database, LDAP, and others) and authorization (the strategy) are configured separately. The setup wizard leaves a single admin in the local database; do not enable account signup for that database, since new accounts inherit whatever the strategy grants to authenticated users.
- Use the Matrix Authorization Strategy (global or project-based) and grant nothing significant to `anonymous` or to `authenticated`; granting Overall/Administer to anonymous is the same as "Anyone can do anything".
- Leave CSRF protection on. It has no UI switch and is only disabled by the `hudson.security.csrf.GlobalCrumbIssuerConfiguration.DISABLE_CSRF_PROTECTION` system property; the documentation says to keep it enabled even on private networks.
- Inbound agents use a fixed or random TCP port, or WebSocket over the same HTTPS port with no extra listener; prefer WebSocket or keep the agent port on the private network.
- Jenkins has no native second factor; put the web UI behind SSO with MFA at the provider or behind an identity layer ([mfa.md](mfa.md)).

## Gitea

- It listens on `HTTP_ADDR = 0.0.0.0` and `HTTP_PORT = 3000` by default (both as of v28.3.0, and the same at v1.27.3); set `HTTP_ADDR = 127.0.0.1` behind a proxy, or `PROTOCOL = https` with `CERT_FILE` and `KEY_FILE` to terminate TLS itself.
- In `[service]`, set `DISABLE_REGISTRATION = true` and, for a private forge, `REQUIRE_SIGNIN_VIEW = true` (default `false`). The code default of `DISABLE_REGISTRATION` differs between the two releases this guide covers. At v28.3.0 Gitea reads it with `sec.Key("DISABLE_REGISTRATION").MustBool(true)`, a default of `true`, although that release's `app.example.ini` still shows `;DISABLE_REGISTRATION = false`. At v1.27.3 it reads `sec.Key("DISABLE_REGISTRATION").MustBool()`, which this guide reads as a default of `false`, the value that release's `app.example.ini` shows. Which release after v1.27.3 first defaults to `true` is not established.
- At both releases the install wizard starts its registration checkbox from the loaded setting (`form.DisableRegistration = setting.Service.DisableRegistration`) and writes the submitted value to `app.ini` as an explicit setting (`cfg.Section("service").Key("DISABLE_REGISTRATION").SetValue(strconv.FormatBool(form.DisableRegistration))`); it handles `REQUIRE_SIGNIN_VIEW` the same way. At both releases the wizard then applies the environment settings to the configuration again before saving it, which a v28.3.0 code comment says must override the install form, so by that comment an environment setting for `DISABLE_REGISTRATION` overrides the submitted value. As this guide's inference, a wizard install that leaves the checkbox as first shown writes `false` at v1.27.3 and `true` at v28.3.0, unless an existing setting changed what it showed or an environment setting overrides the submitted value, so read `DISABLE_REGISTRATION` in `app.ini` after installing instead of relying on either default.
- Users enrol TOTP or a WebAuthn key under Settings > Security; `TWO_FACTOR_AUTH = enforced` in `[security]` (Gitea 1.24 and later) requires it. Gitea's source reads `TWO_FACTOR_AUTH` at v1.24.0 and v28.3.0 and not at v1.23.8; whether a later 1.23.x release added it is not established. With MFA on, Git over HTTP uses an access token instead of the password, and tokens bypass MFA, so scope them and revoke unused ones ([machine-auth.md](machine-auth.md)).
- At v28.3.0, with the same token-first order and the same 2FA checks at v1.27.3, Gitea's Basic authentication method, which its code comment describes as for API requests only, first tries the credential as an OAuth2, personal access or Actions task token, a path with no 2FA check. Only after that, and only while `ENABLE_BASIC_AUTHENTICATION` (default `true`) is on, does it try a password. Unless the user's sign-in source skips 2FA, it then refuses the password while a WebAuthn key is enrolled and, with TOTP enrolled, requires a valid code in an `X-Gitea-OTP` header. Whether Git over HTTP uses this method is not established, and neither is whether `TWO_FACTOR_AUTH = enforced` refuses the tokens of users who have not enrolled; the v28.3.0 `app.example.ini` says users without 2FA "have no access to repositories via API or web".

## GitLab CE

GitLab CE has its own guide now: [gitlab.md](gitlab.md). It covers the forced-random root password and the Omnibus `/etc/gitlab/initial_root_password` file, the plain-HTTP `external_url` listener, TLS, registration and admin approval, 2FA and the password policy, private visibility, the CI/CD runner as a code-execution host, the container registry, the SSH surface, the webhook and system-hook SSRF defaults, and the secrets at rest.

## Uptime Kuma

Listens on `3001` and is WebSocket-based, so a reverse proxy in front needs the `Upgrade` and `Connection` headers. Open it right after the first start and finish the account setup before anyone else can; then enable the 2FA the project lists as a feature for that account. Status pages can be public; the dashboard is not.

## The Docker API

The daemon socket is root on the host: anyone who can talk to it can run a privileged container. Never start `dockerd` with `-H tcp://0.0.0.0:2375`; Docker's documentation calls remote access without TLS not recommended, and scanners find open 2375 within minutes. Two acceptable remote paths:

```bash
# 1. SSH to the Unix socket (nothing new listens on the network)
export DOCKER_HOST=ssh://docker-user@host1.example.com
docker context create remote --docker host=ssh://docker-user@host1.example.com

# 2. TLS with client certificates on 2376, all four flags set
dockerd --tlsverify --tlscacert=ca.pem --tlscert=server-cert.pem --tlskey=server-key.pem -H=0.0.0.0:2376
export DOCKER_HOST=tcp://$HOST:2376 DOCKER_TLS_VERIFY=1 DOCKER_CERT_PATH=~/.docker/zone1/
```

Without `--tlsverify` the daemon does not check client certificates. Firewall 2376 to the operator addresses even with TLS ([docker.md](docker.md)).

## Dozzle

- Dozzle reads the Docker socket to show logs, the same host-level access the Docker API section above describes ([docker.md](docker.md)); a Dozzle login is a login to the host.
- Authentication is off unless configured. Generate a `users.yml` with `docker run -it --rm amir20/dozzle generate admin > users.yml`, mount that file into the container, and set `DOZZLE_AUTH_PROVIDER=simple`; or set `DOZZLE_AUTH_PROVIDER=forward-proxy` to delegate login to a fronting proxy such as Authelia, Authentik, or Cloudflare Access. The `users.yml` generation step is to omit `--password`, and Dozzle then prompts for the password on stdin, so the password never lands in shell history or `set -x` tracing. Stdin closes the argv channel only, so the password stays visible to your own account and root while the `docker` client relays it, and to anyone who can use the Docker daemon.
- Container actions (start, stop, recreate) and shell access into a running container can be turned on; leave both off unless a specific workflow needs them, since either turns a log viewer into remote command execution on the host.
- Bind it to loopback or a private interface and reach it through SSH port forwarding, a tailnet, or Access, with MFA at the fronting layer, like every panel above.

## Docker Registry (`registry:2`)

- The reference registry image ships with no authentication at all: anyone who reaches the port can push and pull every image, and TLS must be configured before any authentication scheme works, since credentials would otherwise cross the wire in clear text.
- Restrict access with htpasswd basic authentication, a token server, or a registry distribution that has its own authentication built in. If using the registry's own native htpasswd auth provider (set directly in the registry's `config.yml`), credentials must be bcrypt-hashed at a strong cost (bare `-B` is cost 5, below the OWASP minimum of 10); the registry rejects any non-bcrypt hash format. Generate each entry with `htpasswd -B -C 12`, using its interactive password prompt and the intended password-file path and username, never `-b`, which takes the password as an argument. The prompt keeps the password out of the command text, shell history and shell tracing; the account owner and root can still read it in the `htpasswd` process while it runs. If instead a reverse proxy sits in front and does its own basic authentication from its own htpasswd file, that proxy's own hashing rules apply, not the registry's.
- Bind it to loopback or a private interface and reach it through SSH port forwarding, a tailnet, or Access, with MFA at the fronting layer.

## Filebrowser

- Ships with a default administrator account created on first run (historically `admin`/`admin`). Change it immediately, before the instance is reachable by anyone else. The project's own repository (archived on September 1, 2026) says not to expose it directly to the internet.
- Bind it to loopback or a private interface and reach it through SSH port forwarding, a tailnet, or Access, with MFA at the fronting layer; never publish a file-serving admin panel.

## Node-RED

- The editor and admin API on `1880` have no authentication at all by default; anyone who reaches the port can view, deploy, and modify flows.
- Set `adminAuth` in `settings.js` with bcrypt-hashed user passwords (`node-red admin hash-pw` generates the hash), and set `credentialSecret` to a value you control, since Node-RED otherwise generates one for you and stored credentials are only as protected as that secret. Give `hash-pw` the password at the tool's prompt, not as an argument; Sources has no reference for `hash-pw` prompting (its Node-RED entry is described as covering `adminAuth` and `credentialSecret`), so confirm that it does before relying on it. A prompt keeps the password out of the command text, shell history and shell tracing; the account owner and root can still read it in the `node-red` process while it runs.
- Bind it to loopback or a private interface and reach it through SSH port forwarding, a tailnet, or Access, with MFA at the fronting layer; the editor is equivalent to a shell on whatever the flows can reach.

## Verify

REASONED: following block; listener check, per the panel and Docker daemon sources below, which also support the panel-login and 2375/2376 checks in the two blocks after it; each of the three blocks carries its own marker and exit status. No deployed panels, certificate fixture or external test network is available here. Comments give expected outcomes and limits; no live run is recorded. The panel-login curl takes one panel's host name on a guarded `set --` line that refuses example.com, example.net, example.org and their subdomains; that guard and the Docker block's address and certificate-file guards have been run only under stubs, without network access.

```bash
(                                                   # a subshell, so the exits below end only this check
  command -v ss >/dev/null || { echo "ss is not installed here; not listing sockets"; exit 2; }
  set -- 0 "$(if ss -tlnp; then printf '\n0'; else printf '\n%s' "$?"; fi)"   # the block's status so far (1, a finding, outranks 3, inconclusive, which outranks 0; a missing ss has already exited 2 above), then the listeners
  set -- "$1" "${2%$'\n'*}" "${2##*$'\n'}"                                    # status, the listener table, then ss's exit status
  printf '%s' "$2"   # read every listener; 9443/9000/8000/3000/81/3001/2375/2376: 127.0.0.1 or absent, never 0.0.0.0
  [ "$3" = 0 ] || { echo "ss -tlnp failed; inconclusive"; set -- 3 "$2" "$3"; }
  if printf '%s' "$2" | awk 'NR > 1 && $4 ~ /:(9443|9000|8000|3000|81|3001|2375|2376)$/ && (index($4, "0.0.0.0:") == 1 || index($4, "*:") == 1 || index($4, "[::]:") == 1) { found = 1 } END { exit !found }'; then
    echo "FINDING: a listener on port 9443, 9000, 8000, 3000, 81, 3001, 2375 or 2376 is bound to a wildcard address"; set -- 1 "$2" "$3"
  else
    case "$?" in 1) ;; *) echo "awk could not read the listener list; inconclusive"; [ "$1" = 1 ] || set -- 3 "$2" "$3" ;; esac
  fi
  echo "block exit $1; a listener on those ports bound to a specific non-loopback address, and every listener on other ports, is not classified, so judge it yourself"
  exit "$1"
)
```

```bash
# REASONED: panel-login check from the cited Portainer, Jenkins and Gitea sources; no deployed panel or external test network is available, the guard has been run only under stubs, and no live result is recorded.
(                                                   # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PANEL_HOST'   # the public host name your proxy serves one panel on, no scheme, user name, port, path, query, fragment, percent sign or trailing dot: replace inside the quotes, keeping them, and run the block once per panel
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
  set -- "$1" "$(if curl -q -g -s -o /dev/null -w '%{http_code}\n' "https://$1/"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "${2##*$'\n'}" "${2%%$'\n'*}"                    # the host, curl's exit status, then the HTTP code
  printf '%s\n' "$3"
                                                                    # 401, 403, or a login redirect, never a dashboard. No -k:
                                                                    # this panel is behind a proxy holding a real certificate, so
                                                                    # a check that skips verification proves nothing about it
  case "$2:$3" in
    0:401|0:403) set -- "$1" 0 ;;
    0:3??) echo "HTTP $3, a redirect: unclassified observation; it passes only when it leads to the panel's login page, so follow it yourself"; set -- "$1" 0 ;;
    0:2??) echo "HTTP $3: unclassified observation; open the page yourself, because a dashboard, or host, container or repository data shown without a login, is a finding"; set -- "$1" 0 ;;
    0:*) echo "HTTP $3 is neither a 401 or 403 refusal, a redirect nor a page to judge; inconclusive"; set -- "$1" 3 ;;
    *) echo "curl exit $2: the request failed, a certificate that did not verify included, since this check keeps certificate verification on; inconclusive"; set -- "$1" 3 ;;
  esac
  echo "block exit $2; a redirect or a 2xx page is not classified, so judge it as the line above says"
  exit "$2"
)
```

```bash
# REASONED: Docker 2375 refusal and 2376 client-certificate comparisons from the cited Docker daemon sources; no daemon, certificate fixture or external test network is available, and no live result is recorded.
# clears a pre-set declare -i or -l attribute, and any stale
# value; copy this whole block, not just the command below
(                                                   # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'   # the address the daemon answers on, for both 2375 and 2376: replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing"; exit 2 ;;
  esac
  set -- "$1" 0                                     # the 2nd value is the block's status so far: 1 (a finding) outranks 3 (inconclusive), which outranks 2 (the 2376 part refused), which outranks 0
  if env -u DOCKER_HOST -u DOCKER_TLS_VERIFY -u DOCKER_CERT_PATH docker -H "tcp://$1:2375" info; then   # must fail: connection refused or filtered; env -u drops the TLS settings exported in the setup above
    echo "FINDING: the Docker API answered on 2375 without TLS"; set -- "$1" 1
  else
    set -- "$1" "$2" "$?"                           # the address, the status so far, then docker's exit status
    # that is, refused or filtered BY THE REMOTE HOST. A local error or a docker client failure that
    # never opened a connection is inconclusive, not a pass
    case "$3" in
      126|127) echo "docker exit $3: the docker client could not run, so no connection was opened; inconclusive"; set -- "$1" 3 ;;
      *) echo "docker exit $3: unclassified observation; it is the pass only if the error above shows the remote host refused or filtered the connection"; set -- "$1" "$2" ;;
    esac
  fi
  if [ -r ca.pem ] && [ -r client-cert.pem ] && [ -r client-key.pem ]; then
    set -- "$1" "$2" "$(if env -u DOCKER_HOST -u DOCKER_TLS_VERIFY -u DOCKER_CERT_PATH \
      curl -q -g -sS -o /dev/null -w '%{http_code}\n' --cacert ca.pem "https://$1:2376/_ping"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
    set -- "$1" "$2" "${3##*$'\n'}" "${3%%$'\n'*}"  # the address, the status so far, curl's exit status, then the HTTP code
    printf '%s\n' "$4"
                                                    # must fail the handshake on the CLIENT certificate. Do not use
                                                    # `docker ... info` here: without `--tlsverify` it fails for the
                                                    # wrong reason, and `DOCKER_CERT_PATH` exported in the setup above
                                                    # can silently supply the very certificate the check is meant to lack
    case "$3" in
      0) echo "FINDING: 2376 answered HTTP $4 without a client certificate, so the daemon does not require one"; set -- "$1" 1 ;;
      6|7|28) echo "curl exit $3: the request without a client certificate never reached the handshake; inconclusive"; [ "$2" = 1 ] || set -- "$1" 3 ;;
      *) echo "curl exit $3: unclassified observation; it is the pass only if curl's error above shows the handshake failed on the client certificate"; set -- "$1" "$2" ;;
    esac
    set -- "$1" "$2" "$(if curl -q -g -sS -o /dev/null -w '%{http_code}\n' --cacert ca.pem --cert client-cert.pem --key client-key.pem \
      "https://$1:2376/_ping"; then printf '\n0'; else printf '\n%s' "$?"; fi)"   # positive control: 200 with the right client certificate
    set -- "$1" "$2" "${3##*$'\n'}" "${3%%$'\n'*}"  # the address, the status so far, curl's exit status, then the HTTP code
    printf '%s\n' "$4"
    case "$3:$4" in
      0:200) ;;
      0:*) echo "HTTP $4 with the client certificate is not the 200 positive control; inconclusive"; [ "$2" = 1 ] || set -- "$1" 3 ;;
      *) echo "curl exit $3: the request with the client certificate failed, so the positive control failed; inconclusive"; [ "$2" = 1 ] || set -- "$1" 3 ;;
    esac
    set -- "$1" "$2"
  else                                              # a guard: the 2376 checks rely on the setup's certificate files in this directory
    echo "ca.pem, client-cert.pem and client-key.pem are not all readable in this directory, so the 2376 checks did not run; not probing 2376"
    [ "$2" = 0 ] && set -- "$1" 2
  fi
  echo "block exit $2; docker's error on 2375 and curl's error on 2376 without a client certificate are not classified, so read them as the lines above say"
  exit "$2"
)
```

REASONED: preceding blocks; the listener and panel-login checks, Docker 2375 refusal and 2376 client-certificate comparisons in the blocks above follow the cited panel and Docker daemon sources; no deployed panels, certificate fixture or external test network is available, and no live result is recorded. From outside the network, every panel URL is unreachable or shows a login; a page that renders host, container, or repository data without one is a finding. Each of the three blocks exits 1 for a finding, 3 for a failed or inconclusive check and otherwise 0, and a guard refusal exits 2, as the listener block does when ss is not installed; the Docker block also reports 2 when its certificate files are missing and nothing else in it was found or inconclusive. The last line of the listener, panel-login and Docker blocks names what each leaves for you to judge.

## Sources (checked September 2026)

- Portainer CE install on Docker (ports 9443, 9000, 8000): https://docs.portainer.io/start/install-ce/server/docker/linux
- Portainer initial setup (setup token, first admin, 12-character password): https://docs.portainer.io/start/install-ce/server/setup
- Portainer authentication and OAuth providers: https://docs.portainer.io/admin/settings/authentication and https://docs.portainer.io/admin/settings/authentication/oauth
- Coolify installation, firewall, proxy, and DNS pages: https://coolify.io/docs/start-with-self-hosted , https://coolify.io/docs/core/infrastructure/servers/firewall , https://coolify.io/docs/core/networking/proxy/overview , https://coolify.io/docs/core/networking/dns , https://coolify.io/docs/core/infrastructure/servers/openssh
- Dokploy installation (ports 80, 443, 3000; admin setup; panel domain): https://docs.dokploy.com/docs/core/installation
- Nginx Proxy Manager setup (port 81, default admin user): https://nginxproxymanager.com/setup/
- Vaultwarden wiki: admin page and ADMIN_TOKEN https://github.com/dani-garcia/vaultwarden/wiki/Enabling-admin-page , registration https://github.com/dani-garcia/vaultwarden/wiki/Disable-registration-of-new-users , and HTTPS https://github.com/dani-garcia/vaultwarden/wiki/Enabling-HTTPS. The Vaultwarden `.env.template`: https://github.com/dani-garcia/vaultwarden/blob/3347698712d3e99e652ad4394ef2fc0ce2800fdd/.env.template
- Kubernetes Dashboard (deprecation, port-forward, token login): https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/ ; 2.x arguments: https://github.com/kubernetes-retired/dashboard/blob/v2.7.0/docs/common/dashboard-arguments.md
- Jenkins security: https://www.jenkins.io/doc/book/security/managing-security/ , https://www.jenkins.io/doc/book/security/access-control/ , https://www.jenkins.io/doc/book/security/csrf-protection/
- Gitea config cheat sheet and MFA (`TWO_FACTOR_AUTH=enforced` requires Gitea 1.24 or later): https://docs.gitea.com/administration/config-cheat-sheet/ and https://docs.gitea.com/usage/user-setting/multi-factor-authentication/
- Uptime Kuma README and reverse proxy wiki: https://github.com/louislam/uptime-kuma and https://github.com/louislam/uptime-kuma/wiki/Reverse-Proxy
- Docker: protect the daemon socket https://docs.docker.com/engine/security/protect-access/ and remote access https://docs.docker.com/engine/daemon/remote-access/
- Dozzle authentication (DOZZLE_AUTH_PROVIDER, users.yml, actions and shell): https://dozzle.dev/guide/authentication
- Docker Registry deployment (default authentication, TLS requirement; rolling documentation, checked September 2026): https://distribution.github.io/distribution/about/deploying/
- Filebrowser: https://github.com/filebrowser/filebrowser
- Node-RED securing the runtime (adminAuth, credentialSecret): https://nodered.org/docs/user-guide/runtime/securing-node-red
- Gitea listener at pinned tag v28.3.0 (checked November 2026): `HTTP_ADDR` default `0.0.0.0` and `HTTP_PORT` default `3000` https://github.com/go-gitea/gitea/blob/v28.3.0/modules/setting/server.go#L151-L152 and `PROTOCOL`, `CERT_FILE` and `KEY_FILE` https://github.com/go-gitea/gitea/blob/v28.3.0/modules/setting/server.go#L163-L203
- Gitea `[service]` settings at pinned tag v28.3.0 (checked November 2026): `DISABLE_REGISTRATION` default https://github.com/go-gitea/gitea/blob/v28.3.0/modules/setting/service.go#L148 , `REQUIRE_SIGNIN_VIEW` and `ENABLE_BASIC_AUTHENTICATION` https://github.com/go-gitea/gitea/blob/v28.3.0/modules/setting/service.go#L168-L179 , and the example config's `TWO_FACTOR_AUTH` and `DISABLE_REGISTRATION` entries https://github.com/go-gitea/gitea/blob/v28.3.0/custom/conf/app.example.ini#L524-L526 and https://github.com/go-gitea/gitea/blob/v28.3.0/custom/conf/app.example.ini#L841-L842
- Gitea install wizard at pinned tag v28.3.0 (checked November 2026): checkbox prefill https://github.com/go-gitea/gitea/blob/v28.3.0/routers/install/install.go#L106-L108 and explicit writes https://github.com/go-gitea/gitea/blob/v28.3.0/routers/install/install.go#L363-L365
- Gitea install wizard environment settings applied after the form at pinned tags v28.3.0 and v1.27.3 (checked November 2026): https://github.com/go-gitea/gitea/blob/v28.3.0/routers/install/install.go#L305-L306 , https://github.com/go-gitea/gitea/blob/v28.3.0/routers/install/install.go#L402 and https://github.com/go-gitea/gitea/blob/v1.27.3/routers/install/install.go#L452
- Gitea `TWO_FACTOR_AUTH` and Basic authentication at pinned tag v28.3.0 (checked November 2026): https://github.com/go-gitea/gitea/blob/v28.3.0/modules/setting/security.go#L197-L204 and https://github.com/go-gitea/gitea/blob/v28.3.0/services/auth/basic.go#L37-L195
- Gitea 1.x source at pinned tag v1.27.3 (checked November 2026): `DISABLE_REGISTRATION` read https://github.com/go-gitea/gitea/blob/v1.27.3/modules/setting/service.go#L151 , example value https://github.com/go-gitea/gitea/blob/v1.27.3/custom/conf/app.example.ini#L809-L810 , and install wizard prefill and explicit writes https://github.com/go-gitea/gitea/blob/v1.27.3/routers/install/install.go#L109-L112 and https://github.com/go-gitea/gitea/blob/v1.27.3/routers/install/install.go#L384-L387
- Gitea listener and Basic method at pinned tag v1.27.3 (checked November 2026): listener defaults https://github.com/go-gitea/gitea/blob/v1.27.3/modules/setting/server.go#L121-L122 , Basic method https://github.com/go-gitea/gitea/blob/v1.27.3/services/auth/basic.go#L34-L187 and `ENABLE_BASIC_AUTHENTICATION` https://github.com/go-gitea/gitea/blob/v1.27.3/modules/setting/service.go#L182
- Gitea MFA minimum 1.24, `TWO_FACTOR_AUTH` read at tag v1.24.0 and absent from tag v1.23.8 (checked November 2026): https://github.com/go-gitea/gitea/blob/v1.24.0/modules/setting/security.go#L146-L153 and https://github.com/go-gitea/gitea/blob/v1.23.8/modules/setting/security.go
- Apache 2.4 `htpasswd` bcrypt default cost and `-C` override (checked October 2026): https://httpd.apache.org/docs/2.4/programs/htpasswd.html
- OWASP password storage at commit 1a3f58ed2714f258a1d713966457f1a0f426e841 (bcrypt minimum work factor 10) (checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/1a3f58ed2714f258a1d713966457f1a0f426e841/cheatsheets/Password_Storage_Cheat_Sheet.md#L139


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, and any earlier-form run it rests on, not a live demonstration of the shipped form. Unknown means no version recorded.

Components (recorded basis):

- portainer: Portainer (unknown)
- dashboard-old: Dashboard arguments (v2.7.0)
- gitea-pin: Gitea source (v28.3.0)
- gitea-1: Gitea 1.x source (v1.27.3)
- gitea-mfa-min: Gitea MFA minimum (1.24)
- coolify: Coolify (unknown)
- dokploy: Dokploy (unknown)
- npm: Nginx Proxy Manager (unknown)
- vaultwarden: Vaultwarden docs (unknown)
- vaultwarden-pin: Vaultwarden config (3347698712d3e99e652ad4394ef2fc0ce2800fdd)
- dashboard: Dashboard docs (unknown)
- jenkins: Jenkins (unknown)
- gitea: Gitea docs (unknown)
- kuma: Uptime Kuma (unknown)
- docker: Docker Engine (unknown)
- dozzle: Dozzle (unknown)
- filebrowser: Filebrowser (unknown)
- nodered: Node-RED (unknown)
- registry-docs: Docker Registry documentation (rolling) (unknown)
- htpasswd: Apache htpasswd (2.4)
- owasp-passwords: OWASP password storage (1a3f58ed2714f258a1d713966457f1a0f426e841)

Claims (full source mapping in the JSON block below):

- private (REASONED; portainer, docker): Keep panels private; public front doors need proxy TLS/auth and MFA. Complete first-run administration before exposure.
- portainer-ports (REASONED; portainer): UI HTTPS 9443 is self-signed by default; supply a certificate/proxy. Leave legacy HTTP 9000 unpublished; publish tunnel 8000 only for Edge Compute.
- portainer-setup (REASONED; portainer): Setup requires the logged setup_token; first user is admin with a password of at least 12 characters.
- portainer-auth (REASONED; portainer): Internal, LDAP, AD or OAuth login; no documented native second factor. Enforce MFA at the OAuth provider.
- portainer-socket (REASONED; portainer, docker): Mounted docker.sock grants host-root power; treat a Portainer admin accordingly.
- coolify-setup (REASONED; coolify): HTTP dashboard starts on 8000; first registration claims server control, so create admin immediately.
- coolify-tls (REASONED; coolify): Custom domain in /settings lets Traefik/Caddy issue/renew TLS; dashboard ports 8000/6001/6002 can then close.
- coolify-firewall (REASONED; coolify): Docker bypasses UFW; restrict dashboard ports at the cloud firewall.
- coolify-ssh (REASONED; coolify): Server SSH keys require no passphrase; stored key material is the whole secret.
- dokploy-ports (REASONED; dokploy): UI is 3000, Traefik 80/443; first setup creates admin.
- dokploy-tls (REASONED; dokploy): Configure a panel domain and Let's Encrypt/custom certificate, then remove published 3000.
- npm-ports (REASONED; npm): Admin is 81, proxy 80/443; publish 127.0.0.1:81:81 and tunnel in.
- npm-admin (REASONED; npm): Change default first-run admin credentials before other work.
- vaultwarden-tls (REASONED; vaultwarden, vaultwarden-pin): Web-vault crypto needs HTTPS; prefer proxy TLS over ROCKET_TLS and set DOMAIN=https://vault.example.com.
- vaultwarden-signup (REASONED; vaultwarden, vaultwarden-pin): SIGNUPS_ALLOWED defaults true; set false to close registration.
- vaultwarden-invites (REASONED; vaultwarden, vaultwarden-pin): INVITATIONS_ALLOWED=true still permits owner/admin invitations; SIGNUPS_DOMAINS_WHITELIST admits selected domains.
- vaultwarden-admin (REASONED; vaultwarden, vaultwarden-pin): ADMIN_TOKEN enables the disabled admin page; enable HTTPS first, use vaultwarden hash argon2id PHC, and escape Compose dollars as $$.
- vaultwarden-session (REASONED; vaultwarden, vaultwarden-pin): Admin sessions expire after 20 minutes by default.
- vaultwarden-port (REASONED; vaultwarden-pin): Container port 80 or non-Docker 8000; publish only to loopback/proxy network.
- dashboard-lifecycle (REASONED; dashboard): Recorded September 2026: deprecated/unmaintained, archived January 2026; Kubernetes points new installs to Headlamp.
- dashboard-forward (REASONED; dashboard): Avoid public LoadBalancer/Ingress; port-forward kong-proxy 8443:443 and use https://localhost:8443 on the operator machine.
- dashboard-token (REASONED; dashboard): Use minimally privileged ServiceAccount bearer tokens; sample cluster-admin is demonstration-only.
- dashboard-old-flags (REASONED; dashboard-old): Older 2.x enable-skip-login and enable-insecure-login default false; keep both false.
- dashboard-mfa (REASONED; dashboard): API-server OIDC gives ServiceAccount tokens no MFA; enforce human MFA on the access path or an IdP-aware UI.
- jenkins-auth (REASONED; jenkins): Realm/authorization are separate; setup creates one local admin. Disable signup because strategy grants apply to new users too.
- jenkins-matrix (REASONED; jenkins): Use Matrix Authorization; grant nothing significant to anonymous/authenticated. Anonymous Overall/Administer is full control.
- jenkins-csrf (REASONED; jenkins): Keep CSRF enabled even privately; disabling uses hudson.security.csrf.GlobalCrumbIssuerConfiguration.DISABLE_CSRF_PROTECTION, not a UI switch.
- jenkins-agents (REASONED; jenkins): Inbound agents use fixed/random TCP or WebSocket on HTTPS; prefer WebSocket or isolate the extra port.
- jenkins-mfa (REASONED; jenkins): No native second factor; enforce MFA through SSO/fronting identity.
- gitea-bind (REASONED; gitea-pin, gitea-1): HTTP_ADDR=0.0.0.0 and HTTP_PORT=3000 default at v28.3.0, the same at v1.27.3; set 127.0.0.1 behind a proxy.
- gitea-tls (REASONED; gitea, gitea-pin): Native TLS uses PROTOCOL=https, CERT_FILE and KEY_FILE.
- gitea-registration (REASONED; gitea, gitea-pin, gitea-1): Set service DISABLE_REGISTRATION=true. Code default is true at v28.3.0, whose example ini still shows false, and false at v1.27.3; which release changed it is not established. Both install wizards write an explicit value, which an environment setting overrides, so read it in app.ini.
- gitea-private (REASONED; gitea, gitea-pin): Set service REQUIRE_SIGNIN_VIEW=true for a private forge; default false. The install wizard writes an explicit value.
- gitea-mfa (REASONED; gitea, gitea-mfa-min, gitea-pin): Enrol TOTP/WebAuthn; security TWO_FACTOR_AUTH=enforced requires MFA in Gitea 1.24 and later. Source reads it at v1.24.0 and v28.3.0, not at v1.23.8; a later 1.23.x is not established.
- gitea-tokens (REASONED; gitea): With MFA, Git HTTP uses tokens that bypass MFA; scope and revoke unused tokens.
- gitea-basic-auth (REASONED; gitea-pin, gitea-1): At v28.3.0, and the same at v1.27.3, Basic auth tries tokens first, with no 2FA check; a password needs ENABLE_BASIC_AUTHENTICATION and, unless its sign-in source skips 2FA, is refused with WebAuthn enrolled and needs a valid X-Gitea-OTP with TOTP. Git HTTP use and enforced-2FA token refusal are not established.
- kuma-proxy (REASONED; kuma): Port 3001 uses WebSockets; proxy Upgrade/Connection headers are required.
- kuma-admin (REASONED; kuma): Finish account setup before others, enable 2FA and keep dashboard private even if status pages are public.
- docker-root (REASONED; docker): Docker socket grants host-root power; never expose unauthenticated 0.0.0.0:2375.
- docker-ssh (REASONED; docker): DOCKER_HOST/context can select SSH to the Unix socket without a new listener.
- docker-mtls (REASONED; docker): 2376 requires tlsverify, CA, server cert/key and client TLS settings. Without tlsverify clients are not authenticated; firewall source addresses too.
- dozzle-socket (REASONED; dozzle, docker): Docker-socket access has host-level power; keep Dozzle private with fronting MFA.
- dozzle-auth (REASONED; dozzle): Auth defaults off; generate users.yml with stdin password prompt and set simple auth, or delegate with forward-proxy.
- dozzle-actions (REASONED; dozzle): Leave optional container actions/shell off unless needed; either enables remote command execution.
- registry-auth (REASONED; registry-docs): registry:2 defaults to unauthenticated push/pull; configure TLS before htpasswd/token auth or use an authenticated distribution.
- registry-bcrypt (REASONED; registry-docs, htpasswd, owasp-passwords): Native htpasswd accepts bcrypt only; use -B -C 12. Proxy hashing rules differ.
- registry-private (REASONED; registry-docs): Use private networking and tunnels/Access with fronting MFA.
- filebrowser-admin (REASONED; filebrowser): Change first-run admin credentials, historically admin/admin. Guide records September 1, 2026 archival and the warning against internet exposure.
- filebrowser-private (REASONED; filebrowser): Keep Filebrowser private through tunnel/tailnet/Access with fronting MFA.
- nodered-default (REASONED; nodered): Editor/admin API on 1880 defaults unauthenticated, permitting flow viewing/deployment/modification.
- nodered-auth (REASONED; nodered): Set adminAuth with bcrypt passwords from node-red admin hash-pw.
- nodered-secret (REASONED; nodered): Set credentialSecret yourself; otherwise generated, and stored credentials depend on it.
- nodered-private (REASONED; nodered): Keep editor private with fronting MFA; it has the power of its flows.
- verify-listeners (REASONED; portainer, dokploy, npm, kuma, docker): Read every panel/API listener; expect loopback or absence, never wildcard exposure.
- verify-panel (REASONED; portainer, jenkins, gitea): Expect denial/login redirect with valid TLS; anonymous host/container/repository data is a finding. No live panel outcome recorded.
- verify-docker-plain (REASONED; docker): Public-IP 2375 must be refused/filtered by the remote host; local client failure is inconclusive.
- verify-docker-mtls (REASONED; docker): 2376 /_ping without a client certificate must fail client-certificate authentication; correct certificate/key must return 200.

````json
{
  "schema": 1,
  "checked": "2026-11-04",
  "documentation_checked": "2026-09",
  "body_sha256": "9d3fc3d3fd27a2f52538bf4e3cd4b88eb9b7ee738c9656611fd4dd0e76966079",
  "components": {
    "portainer": {
      "name": "Portainer",
      "basis": "unknown",
      "sources": {
        "s3e163c7d3c38": "https://docs.portainer.io/start/install-ce/server/docker/linux",
        "s115489d2f86f": "https://docs.portainer.io/start/install-ce/server/setup",
        "s59297757a042": "https://docs.portainer.io/admin/settings/authentication",
        "s8901bbe7c3d3": "https://docs.portainer.io/admin/settings/authentication/oauth"
      }
    },
    "dashboard-old": {
      "name": "Dashboard arguments",
      "basis": "v2.7.0",
      "sources": {
        "sacea2944651e": "https://github.com/kubernetes-retired/dashboard/blob/v2.7.0/docs/common/dashboard-arguments.md"
      }
    },
    "gitea-pin": {
      "name": "Gitea source",
      "basis": "v28.3.0",
      "sources": {
        "s01438ea0392a": "https://github.com/go-gitea/gitea/blob/v28.3.0/modules/setting/server.go#L151-L152",
        "s94fcc58b53a7": "https://github.com/go-gitea/gitea/blob/v28.3.0/modules/setting/server.go#L163-L203",
        "s5f900af6c58a": "https://github.com/go-gitea/gitea/blob/v28.3.0/modules/setting/service.go#L148",
        "sa1a585c22f58": "https://github.com/go-gitea/gitea/blob/v28.3.0/modules/setting/service.go#L168-L179",
        "s57a09b15fc30": "https://github.com/go-gitea/gitea/blob/v28.3.0/custom/conf/app.example.ini#L524-L526",
        "sb47c6c0b545b": "https://github.com/go-gitea/gitea/blob/v28.3.0/custom/conf/app.example.ini#L841-L842",
        "s4b700228467a": "https://github.com/go-gitea/gitea/blob/v28.3.0/routers/install/install.go#L106-L108",
        "s2029804191d3": "https://github.com/go-gitea/gitea/blob/v28.3.0/routers/install/install.go#L363-L365",
        "s25f54cf927cd": "https://github.com/go-gitea/gitea/blob/v28.3.0/routers/install/install.go#L305-L306",
        "s94cf9187cdb6": "https://github.com/go-gitea/gitea/blob/v28.3.0/routers/install/install.go#L402",
        "s17f07be814d4": "https://github.com/go-gitea/gitea/blob/v28.3.0/modules/setting/security.go#L197-L204",
        "s11c58c9a7056": "https://github.com/go-gitea/gitea/blob/v28.3.0/services/auth/basic.go#L37-L195"
      }
    },
    "gitea-1": {
      "name": "Gitea 1.x source",
      "basis": "v1.27.3",
      "sources": {
        "scc62ce4e5d4b": "https://github.com/go-gitea/gitea/blob/v1.27.3/modules/setting/service.go#L151",
        "s99677826f27f": "https://github.com/go-gitea/gitea/blob/v1.27.3/custom/conf/app.example.ini#L809-L810",
        "s9c7fa227cc6c": "https://github.com/go-gitea/gitea/blob/v1.27.3/routers/install/install.go#L109-L112",
        "s0ecc49b4eb51": "https://github.com/go-gitea/gitea/blob/v1.27.3/routers/install/install.go#L384-L387",
        "s9e03e5dfe7ae": "https://github.com/go-gitea/gitea/blob/v1.27.3/routers/install/install.go#L452",
        "s31dd622b1c12": "https://github.com/go-gitea/gitea/blob/v1.27.3/modules/setting/server.go#L121-L122",
        "s44ea7417ec5a": "https://github.com/go-gitea/gitea/blob/v1.27.3/services/auth/basic.go#L34-L187",
        "saed8434d7dff": "https://github.com/go-gitea/gitea/blob/v1.27.3/modules/setting/service.go#L182"
      }
    },
    "gitea-mfa-min": {
      "name": "Gitea MFA minimum",
      "basis": "1.24",
      "sources": {
        "sfec17fde7bb0": "https://docs.gitea.com/administration/config-cheat-sheet/",
        "sa5869c041fc5": "https://github.com/go-gitea/gitea/blob/v1.24.0/modules/setting/security.go#L146-L153",
        "s023053a8ef10": "https://github.com/go-gitea/gitea/blob/v1.23.8/modules/setting/security.go"
      }
    },
    "coolify": {
      "name": "Coolify",
      "basis": "unknown",
      "sources": {
        "s41e2d21202d9": "https://coolify.io/docs/start-with-self-hosted",
        "sf2ae62425b35": "https://coolify.io/docs/core/infrastructure/servers/firewall",
        "sf5d819d5d87d": "https://coolify.io/docs/core/networking/proxy/overview",
        "s90addf9d8d5d": "https://coolify.io/docs/core/networking/dns",
        "s683244a61c48": "https://coolify.io/docs/core/infrastructure/servers/openssh"
      }
    },
    "dokploy": {
      "name": "Dokploy",
      "basis": "unknown",
      "sources": {
        "sc2cc854c9b7e": "https://docs.dokploy.com/docs/core/installation"
      }
    },
    "npm": {
      "name": "Nginx Proxy Manager",
      "basis": "unknown",
      "sources": {
        "se553d384e783": "https://nginxproxymanager.com/setup/"
      }
    },
    "vaultwarden": {
      "name": "Vaultwarden docs",
      "basis": "unknown",
      "sources": {
        "s0bbe8ad856cd": "https://github.com/dani-garcia/vaultwarden/wiki/Enabling-admin-page",
        "s6d3d0d02dcc9": "https://github.com/dani-garcia/vaultwarden/wiki/Disable-registration-of-new-users",
        "s60d064cae50e": "https://github.com/dani-garcia/vaultwarden/wiki/Enabling-HTTPS"
      }
    },
    "vaultwarden-pin": {
      "name": "Vaultwarden config",
      "basis": "3347698712d3e99e652ad4394ef2fc0ce2800fdd",
      "sources": {
        "s31c5fc79f5a0": "https://github.com/dani-garcia/vaultwarden/blob/3347698712d3e99e652ad4394ef2fc0ce2800fdd/.env.template"
      }
    },
    "dashboard": {
      "name": "Dashboard docs",
      "basis": "unknown",
      "sources": {
        "s73a36a43f6b5": "https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/"
      }
    },
    "jenkins": {
      "name": "Jenkins",
      "basis": "unknown",
      "sources": {
        "s524c8d5871f1": "https://www.jenkins.io/doc/book/security/managing-security/",
        "sdfee751aeeee": "https://www.jenkins.io/doc/book/security/access-control/",
        "s6f5287fd36d4": "https://www.jenkins.io/doc/book/security/csrf-protection/"
      }
    },
    "gitea": {
      "name": "Gitea docs",
      "basis": "unknown",
      "sources": {
        "sfec17fde7bb0": "https://docs.gitea.com/administration/config-cheat-sheet/",
        "s3b7060d58383": "https://docs.gitea.com/usage/user-setting/multi-factor-authentication/"
      }
    },
    "kuma": {
      "name": "Uptime Kuma",
      "basis": "unknown",
      "sources": {
        "s05b853ba300b": "https://github.com/louislam/uptime-kuma",
        "sed52bfca4039": "https://github.com/louislam/uptime-kuma/wiki/Reverse-Proxy"
      }
    },
    "docker": {
      "name": "Docker Engine",
      "basis": "unknown",
      "sources": {
        "sfe15a8156c18": "https://docs.docker.com/engine/security/protect-access/",
        "s1b5ec54421b0": "https://docs.docker.com/engine/daemon/remote-access/"
      }
    },
    "dozzle": {
      "name": "Dozzle",
      "basis": "unknown",
      "sources": {
        "s45b3eab2515b": "https://dozzle.dev/guide/authentication"
      }
    },
    "filebrowser": {
      "name": "Filebrowser",
      "basis": "unknown",
      "sources": {
        "s6386c9e2356b": "https://github.com/filebrowser/filebrowser"
      }
    },
    "nodered": {
      "name": "Node-RED",
      "basis": "unknown",
      "sources": {
        "sa94f329023fe": "https://nodered.org/docs/user-guide/runtime/securing-node-red"
      }
    },
    "registry-docs": {
      "name": "Docker Registry documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "sa315b3f8bfa6": "https://distribution.github.io/distribution/about/deploying/"
      }
    },
    "htpasswd": {
      "name": "Apache htpasswd",
      "basis": "2.4",
      "sources": {
        "scde9004bb967": "https://httpd.apache.org/docs/2.4/programs/htpasswd.html"
      }
    },
    "owasp-passwords": {
      "name": "OWASP password storage",
      "basis": "1a3f58ed2714f258a1d713966457f1a0f426e841",
      "sources": {
        "s0f70ec4aa271": "https://github.com/OWASP/CheatSheetSeries/blob/1a3f58ed2714f258a1d713966457f1a0f426e841/cheatsheets/Password_Storage_Cheat_Sheet.md#L139"
      }
    }
  },
  "claims": {
    "private": {"text": "Keep panels private; public front doors need proxy TLS/auth and MFA. Complete first-run administration before exposure.", "components": ["portainer", "docker"], "sources": ["portainer:s3e163c7d3c38", "docker:sfe15a8156c18"], "status": "REASONED"},
    "portainer-ports": {"text": "UI HTTPS 9443 is self-signed by default; supply a certificate/proxy. Leave legacy HTTP 9000 unpublished; publish tunnel 8000 only for Edge Compute.", "components": ["portainer"], "sources": ["portainer:s3e163c7d3c38"], "status": "REASONED"},
    "portainer-setup": {"text": "Setup requires the logged setup_token; first user is admin with a password of at least 12 characters.", "components": ["portainer"], "sources": ["portainer:s115489d2f86f"], "status": "REASONED"},
    "portainer-auth": {"text": "Internal, LDAP, AD or OAuth login; no documented native second factor. Enforce MFA at the OAuth provider.", "components": ["portainer"], "sources": ["portainer:s59297757a042", "portainer:s8901bbe7c3d3"], "status": "REASONED"},
    "portainer-socket": {"text": "Mounted docker.sock grants host-root power; treat a Portainer admin accordingly.", "components": ["portainer", "docker"], "sources": ["portainer:s3e163c7d3c38", "docker:sfe15a8156c18"], "status": "REASONED"},
    "coolify-setup": {"text": "HTTP dashboard starts on 8000; first registration claims server control, so create admin immediately.", "components": ["coolify"], "sources": ["coolify:s41e2d21202d9"], "status": "REASONED"},
    "coolify-tls": {"text": "Custom domain in /settings lets Traefik/Caddy issue/renew TLS; dashboard ports 8000/6001/6002 can then close.", "components": ["coolify"], "sources": ["coolify:sf2ae62425b35", "coolify:sf5d819d5d87d", "coolify:s90addf9d8d5d"], "status": "REASONED"},
    "coolify-firewall": {"text": "Docker bypasses UFW; restrict dashboard ports at the cloud firewall.", "components": ["coolify"], "sources": ["coolify:sf2ae62425b35"], "status": "REASONED"},
    "coolify-ssh": {"text": "Server SSH keys require no passphrase; stored key material is the whole secret.", "components": ["coolify"], "sources": ["coolify:s683244a61c48"], "status": "REASONED"},
    "dokploy-ports": {"text": "UI is 3000, Traefik 80/443; first setup creates admin.", "components": ["dokploy"], "sources": ["dokploy:sc2cc854c9b7e"], "status": "REASONED"},
    "dokploy-tls": {"text": "Configure a panel domain and Let's Encrypt/custom certificate, then remove published 3000.", "components": ["dokploy"], "sources": ["dokploy:sc2cc854c9b7e"], "status": "REASONED"},
    "npm-ports": {"text": "Admin is 81, proxy 80/443; publish 127.0.0.1:81:81 and tunnel in.", "components": ["npm"], "sources": ["npm:se553d384e783"], "status": "REASONED"},
    "npm-admin": {"text": "Change default first-run admin credentials before other work.", "components": ["npm"], "sources": ["npm:se553d384e783"], "status": "REASONED"},
    "vaultwarden-tls": {"text": "Web-vault crypto needs HTTPS; prefer proxy TLS over ROCKET_TLS and set DOMAIN=https://vault.example.com.", "components": ["vaultwarden", "vaultwarden-pin"], "sources": ["vaultwarden:s60d064cae50e", "vaultwarden-pin:s31c5fc79f5a0"], "status": "REASONED"},
    "vaultwarden-signup": {"text": "SIGNUPS_ALLOWED defaults true; set false to close registration.", "components": ["vaultwarden", "vaultwarden-pin"], "sources": ["vaultwarden:s6d3d0d02dcc9", "vaultwarden-pin:s31c5fc79f5a0"], "status": "REASONED"},
    "vaultwarden-invites": {"text": "INVITATIONS_ALLOWED=true still permits owner/admin invitations; SIGNUPS_DOMAINS_WHITELIST admits selected domains.", "components": ["vaultwarden", "vaultwarden-pin"], "sources": ["vaultwarden:s6d3d0d02dcc9", "vaultwarden-pin:s31c5fc79f5a0"], "status": "REASONED"},
    "vaultwarden-admin": {"text": "ADMIN_TOKEN enables the disabled admin page; enable HTTPS first, use vaultwarden hash argon2id PHC, and escape Compose dollars as $$.", "components": ["vaultwarden", "vaultwarden-pin"], "sources": ["vaultwarden:s0bbe8ad856cd", "vaultwarden-pin:s31c5fc79f5a0"], "status": "REASONED"},
    "vaultwarden-session": {"text": "Admin sessions expire after 20 minutes by default.", "components": ["vaultwarden", "vaultwarden-pin"], "sources": ["vaultwarden:s0bbe8ad856cd", "vaultwarden-pin:s31c5fc79f5a0"], "status": "REASONED"},
    "vaultwarden-port": {"text": "Container port 80 or non-Docker 8000; publish only to loopback/proxy network.", "components": ["vaultwarden-pin"], "sources": ["vaultwarden-pin:s31c5fc79f5a0"], "status": "REASONED"},
    "dashboard-lifecycle": {"text": "Recorded September 2026: deprecated/unmaintained, archived January 2026; Kubernetes points new installs to Headlamp.", "components": ["dashboard"], "sources": ["dashboard:s73a36a43f6b5"], "status": "REASONED"},
    "dashboard-forward": {"text": "Avoid public LoadBalancer/Ingress; port-forward kong-proxy 8443:443 and use https://localhost:8443 on the operator machine.", "components": ["dashboard"], "sources": ["dashboard:s73a36a43f6b5"], "status": "REASONED"},
    "dashboard-token": {"text": "Use minimally privileged ServiceAccount bearer tokens; sample cluster-admin is demonstration-only.", "components": ["dashboard"], "sources": ["dashboard:s73a36a43f6b5"], "status": "REASONED"},
    "dashboard-old-flags": {"text": "Older 2.x enable-skip-login and enable-insecure-login default false; keep both false.", "components": ["dashboard-old"], "sources": ["dashboard-old:sacea2944651e"], "status": "REASONED"},
    "dashboard-mfa": {"text": "API-server OIDC gives ServiceAccount tokens no MFA; enforce human MFA on the access path or an IdP-aware UI.", "components": ["dashboard"], "sources": ["dashboard:s73a36a43f6b5"], "status": "REASONED"},
    "jenkins-auth": {"text": "Realm/authorization are separate; setup creates one local admin. Disable signup because strategy grants apply to new users too.", "components": ["jenkins"], "sources": ["jenkins:s524c8d5871f1", "jenkins:sdfee751aeeee"], "status": "REASONED"},
    "jenkins-matrix": {"text": "Use Matrix Authorization; grant nothing significant to anonymous/authenticated. Anonymous Overall/Administer is full control.", "components": ["jenkins"], "sources": ["jenkins:sdfee751aeeee"], "status": "REASONED"},
    "jenkins-csrf": {"text": "Keep CSRF enabled even privately; disabling uses hudson.security.csrf.GlobalCrumbIssuerConfiguration.DISABLE_CSRF_PROTECTION, not a UI switch.", "components": ["jenkins"], "sources": ["jenkins:s6f5287fd36d4"], "status": "REASONED"},
    "jenkins-agents": {"text": "Inbound agents use fixed/random TCP or WebSocket on HTTPS; prefer WebSocket or isolate the extra port.", "components": ["jenkins"], "sources": ["jenkins:s524c8d5871f1"], "status": "REASONED"},
    "jenkins-mfa": {"text": "No native second factor; enforce MFA through SSO/fronting identity.", "components": ["jenkins"], "sources": ["jenkins:s524c8d5871f1", "jenkins:sdfee751aeeee"], "status": "REASONED"},
    "gitea-bind": {"text": "HTTP_ADDR=0.0.0.0 and HTTP_PORT=3000 default at v28.3.0, the same at v1.27.3; set 127.0.0.1 behind a proxy.", "components": ["gitea-pin", "gitea-1"], "sources": ["gitea-pin:s01438ea0392a", "gitea-1:s31dd622b1c12"], "status": "REASONED"},
    "gitea-tls": {"text": "Native TLS uses PROTOCOL=https, CERT_FILE and KEY_FILE.", "components": ["gitea", "gitea-pin"], "sources": ["gitea:sfec17fde7bb0", "gitea-pin:s94fcc58b53a7"], "status": "REASONED"},
    "gitea-registration": {"text": "Set service DISABLE_REGISTRATION=true. Code default is true at v28.3.0, whose example ini still shows false, and false at v1.27.3; which release changed it is not established. Both install wizards write an explicit value, which an environment setting overrides, so read it in app.ini.", "components": ["gitea", "gitea-pin", "gitea-1"], "sources": ["gitea:sfec17fde7bb0", "gitea-pin:s5f900af6c58a", "gitea-pin:sb47c6c0b545b", "gitea-pin:s4b700228467a", "gitea-pin:s2029804191d3", "gitea-pin:s25f54cf927cd", "gitea-pin:s94cf9187cdb6", "gitea-1:scc62ce4e5d4b", "gitea-1:s99677826f27f", "gitea-1:s9c7fa227cc6c", "gitea-1:s0ecc49b4eb51", "gitea-1:s9e03e5dfe7ae"], "status": "REASONED"},
    "gitea-private": {"text": "Set service REQUIRE_SIGNIN_VIEW=true for a private forge; default false. The install wizard writes an explicit value.", "components": ["gitea", "gitea-pin"], "sources": ["gitea:sfec17fde7bb0", "gitea-pin:sa1a585c22f58", "gitea-pin:s4b700228467a", "gitea-pin:s2029804191d3"], "status": "REASONED"},
    "gitea-mfa": {"text": "Enrol TOTP/WebAuthn; security TWO_FACTOR_AUTH=enforced requires MFA in Gitea 1.24 and later. Source reads it at v1.24.0 and v28.3.0, not at v1.23.8; a later 1.23.x is not established.", "components": ["gitea", "gitea-mfa-min", "gitea-pin"], "sources": ["gitea:sfec17fde7bb0", "gitea:s3b7060d58383", "gitea-mfa-min:sfec17fde7bb0", "gitea-mfa-min:sa5869c041fc5", "gitea-mfa-min:s023053a8ef10", "gitea-pin:s17f07be814d4"], "status": "REASONED"},
    "gitea-tokens": {"text": "With MFA, Git HTTP uses tokens that bypass MFA; scope and revoke unused tokens.", "components": ["gitea"], "sources": ["gitea:s3b7060d58383"], "status": "REASONED"},
    "gitea-basic-auth": {"text": "At v28.3.0, and the same at v1.27.3, Basic auth tries tokens first, with no 2FA check; a password needs ENABLE_BASIC_AUTHENTICATION and, unless its sign-in source skips 2FA, is refused with WebAuthn enrolled and needs a valid X-Gitea-OTP with TOTP. Git HTTP use and enforced-2FA token refusal are not established.", "components": ["gitea-pin", "gitea-1"], "sources": ["gitea-pin:s11c58c9a7056", "gitea-pin:sa1a585c22f58", "gitea-pin:s57a09b15fc30", "gitea-1:s44ea7417ec5a", "gitea-1:saed8434d7dff"], "status": "REASONED"},
    "kuma-proxy": {"text": "Port 3001 uses WebSockets; proxy Upgrade/Connection headers are required.", "components": ["kuma"], "sources": ["kuma:s05b853ba300b", "kuma:sed52bfca4039"], "status": "REASONED"},
    "kuma-admin": {"text": "Finish account setup before others, enable 2FA and keep dashboard private even if status pages are public.", "components": ["kuma"], "sources": ["kuma:s05b853ba300b"], "status": "REASONED"},
    "docker-root": {"text": "Docker socket grants host-root power; never expose unauthenticated 0.0.0.0:2375.", "components": ["docker"], "sources": ["docker:sfe15a8156c18", "docker:s1b5ec54421b0"], "status": "REASONED"},
    "docker-ssh": {"text": "DOCKER_HOST/context can select SSH to the Unix socket without a new listener.", "components": ["docker"], "sources": ["docker:sfe15a8156c18"], "status": "REASONED"},
    "docker-mtls": {"text": "2376 requires tlsverify, CA, server cert/key and client TLS settings. Without tlsverify clients are not authenticated; firewall source addresses too.", "components": ["docker"], "sources": ["docker:sfe15a8156c18"], "status": "REASONED"},
    "dozzle-socket": {"text": "Docker-socket access has host-level power; keep Dozzle private with fronting MFA.", "components": ["dozzle", "docker"], "sources": ["dozzle:s45b3eab2515b", "docker:sfe15a8156c18"], "status": "REASONED"},
    "dozzle-auth": {"text": "Auth defaults off; generate users.yml with stdin password prompt and set simple auth, or delegate with forward-proxy.", "components": ["dozzle"], "sources": ["dozzle:s45b3eab2515b"], "status": "REASONED"},
    "dozzle-actions": {"text": "Leave optional container actions/shell off unless needed; either enables remote command execution.", "components": ["dozzle"], "sources": ["dozzle:s45b3eab2515b"], "status": "REASONED"},
    "registry-auth": {"text": "registry:2 defaults to unauthenticated push/pull; configure TLS before htpasswd/token auth or use an authenticated distribution.", "components": ["registry-docs"], "sources": ["registry-docs:sa315b3f8bfa6"], "status": "REASONED"},
    "registry-bcrypt": {"text": "Native htpasswd accepts bcrypt only; use -B -C 12. Proxy hashing rules differ.", "components": ["registry-docs", "htpasswd", "owasp-passwords"], "sources": ["registry-docs:sa315b3f8bfa6", "htpasswd:scde9004bb967", "owasp-passwords:s0f70ec4aa271"], "status": "REASONED"},
    "registry-private": {"text": "Use private networking and tunnels/Access with fronting MFA.", "components": ["registry-docs"], "sources": ["registry-docs:sa315b3f8bfa6"], "status": "REASONED"},
    "filebrowser-admin": {"text": "Change first-run admin credentials, historically admin/admin. Guide records September 1, 2026 archival and the warning against internet exposure.", "components": ["filebrowser"], "sources": ["filebrowser:s6386c9e2356b"], "status": "REASONED"},
    "filebrowser-private": {"text": "Keep Filebrowser private through tunnel/tailnet/Access with fronting MFA.", "components": ["filebrowser"], "sources": ["filebrowser:s6386c9e2356b"], "status": "REASONED"},
    "nodered-default": {"text": "Editor/admin API on 1880 defaults unauthenticated, permitting flow viewing/deployment/modification.", "components": ["nodered"], "sources": ["nodered:sa94f329023fe"], "status": "REASONED"},
    "nodered-auth": {"text": "Set adminAuth with bcrypt passwords from node-red admin hash-pw.", "components": ["nodered"], "sources": ["nodered:sa94f329023fe"], "status": "REASONED"},
    "nodered-secret": {"text": "Set credentialSecret yourself; otherwise generated, and stored credentials depend on it.", "components": ["nodered"], "sources": ["nodered:sa94f329023fe"], "status": "REASONED"},
    "nodered-private": {"text": "Keep editor private with fronting MFA; it has the power of its flows.", "components": ["nodered"], "sources": ["nodered:sa94f329023fe"], "status": "REASONED"},
    "verify-listeners": {"text": "Read every panel/API listener; expect loopback or absence, never wildcard exposure.", "components": ["portainer", "dokploy", "npm", "kuma", "docker"], "sources": ["portainer:s3e163c7d3c38", "dokploy:sc2cc854c9b7e", "npm:se553d384e783", "kuma:s05b853ba300b", "docker:s1b5ec54421b0"], "status": "REASONED", "verify": [1]},
    "verify-panel": {"text": "Expect denial/login redirect with valid TLS; anonymous host/container/repository data is a finding. No live panel outcome recorded.", "components": ["portainer", "jenkins", "gitea"], "sources": ["portainer:s3e163c7d3c38", "jenkins:sdfee751aeeee", "gitea:sfec17fde7bb0"], "status": "REASONED", "verify": [2]},
    "verify-docker-plain": {"text": "Public-IP 2375 must be refused/filtered by the remote host; local client failure is inconclusive.", "components": ["docker"], "sources": ["docker:s1b5ec54421b0"], "status": "REASONED", "verify": [3]},
    "verify-docker-mtls": {"text": "2376 /_ping without a client certificate must fail client-certificate authentication; correct certificate/key must return 200.", "components": ["docker"], "sources": ["docker:sfe15a8156c18"], "status": "REASONED", "verify": [3]}
  }
}
````
<!-- version-basis:end -->
