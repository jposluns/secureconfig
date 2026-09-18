# ClickHouse: listen address, the default user, and TLS ports

ClickHouse listens on localhost only until you set `listen_host`, but the upstream base configuration ships a `default` user that has an empty password, may connect from any address (`<ip>::/0</ip>`), and holds `access_management`, so widening `listen_host` to `::` or `0.0.0.0` publishes a passwordless administrator on plaintext HTTP 8123 and native TCP 9000. Packaging, container initialization, and configuration overrides can change these defaults (the official Docker image, for one, disables the `default` user's network access when none of `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD`, or `CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT` is set), so inspect the effective configuration of the version you run rather than assuming either behaviour. Widen only after steps 2 and 3.

## 1. Keep `listen_host` narrow

The shipped `config.xml` comments out every `listen_host` example and says the default is to "try listen localhost on IPv4 and IPv6". For remote clients, name the one private address rather than `::`. The listed client listeners then bind there: `http_port` 8123, `tcp_port` 9000, `mysql_port` 9004, `postgresql_port` 9005, and `interserver_http_port` 9009 (replica traffic). Replica communication follows `interserver_listen_host`, which defaults to `listen_host` but can be set separately, so inspect both settings and every effective listener before you write firewall rules per [cloud-firewalls.md](cloud-firewalls.md) or [host.md](host.md).

```xml
<listen_host>127.0.0.1</listen_host>
<listen_host>REPLACE_WITH_PRIVATE_IP</listen_host>
```

## 2. Put a password on `default`, and create real users

In `users.xml` the `default` user is `<password></password>`. Replace that with a hash (the shipped file documents `echo -n "$PASSWORD" | sha256sum | tr -d '-'`) and restrict where it may connect from. `password_double_sha1_hex` exists for MySQL-protocol clients; plain `<password>` is documented but stores the secret in clear.

```xml
<users>
  <default>
    <password_sha256_hex>REPLACE_WITH_THE_SHA256_HEX_OF_A_LONG_RANDOM_PASSWORD</password_sha256_hex>
    <networks>
      <ip>::1</ip>
      <ip>127.0.0.1</ip>
    </networks>
    <profile>default</profile>
    <quota>default</quota>
    <access_management>1</access_management>
  </default>
</users>
```

Because `default` holds `access_management`, use it once to create per-application users with SQL, each limited to its source network and its database ([authentication.md](authentication.md)). `IDENTIFIED WITH bcrypt_password BY '...'` (72-character maximum) is also available and stores a slower hash. The access-control documentation recommends disabling `default` in production once a SQL admin user exists and inter-node credentials are configured, since `default` is what nodes use to talk to each other; until then, the loopback-only `<networks>` above keeps it off the network.

```sql
CREATE USER app HOST IP '10.0.0.0/8' IDENTIFIED WITH sha256_password BY 'REPLACE_WITH_LONG_RANDOM_VALUE';
GRANT SELECT, INSERT ON appdb.* TO app;
```

Keep external-source privileges out of application accounts unless they are needed. ClickHouse can fetch URLs from SQL through the `url()` table function and HTTP dictionaries, read local files with `file()` (relative to `user_files_path`, not an HTTP fetcher), and reach other servers with `remote()`, so review URL, S3, REMOTE, and FILE access, dictionary creation, and any existing externally backed tables and dictionaries (the `SOURCES` grants; separate READ and WRITE forms are available since 25.7 only when `access_control_improvements.enable_read_write_grants` is set, otherwise use the legacy source privileges such as `URL`, `S3`, `REMOTE`, and `FILE`). Set `remote_url_allow_hosts` to the specific URL destinations you need; the shipped configuration notes that omitting the section allows all hosts. That check matches the host name before DNS resolution and on every redirect, so it does not replace network egress controls on link-local metadata and internal addresses; enforce those per [egress-metadata.md](egress-metadata.md).

## 3. TLS listeners, plaintext ports off

Get a certificate ([free-certificates.md](free-certificates.md) or [self-signed.md](self-signed.md)), enable the secure ports, and comment out the plaintext ones, as the vendor's TLS guide does. Treat `mysql_port`, `postgresql_port`, and `interserver_http_port` the same way: remove them or keep them on a private address (`interserver_https_port` 9010 is the TLS variant). Replication has its own authentication that a SQL-user password and TLS do not provide: if you keep a replication listener, set matching `interserver_http_credentials` (`user` and `password`) on every replica and keep `allow_empty` false, because omitting that section leaves replication unauthenticated. Users can also be identified by client certificate (`IDENTIFIED WITH ssl_certificate CN 'name'`), the possession factor for machine clients ([machine-auth.md](machine-auth.md)). MFA: ClickHouse 26.2 introduced native TOTP for users defined in XML (`time_based_one_time_password` alongside a password, with `secret`, `period`, `digits`, and `algorithm`); it is not available for SQL-driven users, so configure it for the human XML accounts that support it and route every unsupported human path (to the host, and to any dashboard in front) behind an MFA-enforcing layer per [mfa.md](mfa.md). Keep machine authentication separate.

```xml
<https_port>8443</https_port>
<tcp_port_secure>9440</tcp_port_secure>
<!-- <http_port>8123</http_port> -->
<!-- <tcp_port>9000</tcp_port> -->
<openSSL>
  <server>
    <certificateFile>/etc/clickhouse-server/certs/server.crt</certificateFile>
    <privateKeyFile>/etc/clickhouse-server/certs/server.key</privateKeyFile>
    <disableProtocols>sslv2,sslv3</disableProtocols>
    <preferServerCiphers>true</preferServerCiphers>
  </server>
</openSSL>
```

These snippets edit children of the `<clickhouse>` root; state whether you are editing the base files or installing overrides under `config.d`/`users.d`, and remember that in an override, commenting an element out does not remove the inherited setting. To close inherited plaintext listeners from a `config.d/hardening.xml` override, remove them explicitly with `<http_port remove="remove"/>` and `<tcp_port remove="remove"/>`; to replace the `default` user's access from a `users.d` override, use `<password remove="remove"/>` and a `<networks replace="replace">` subtree. Inspect the effective merged configuration before widening access.

## Verify

Clients use `clickhouse-client --secure` on 9440, or HTTPS on 8443 with HTTP basic auth or the `X-ClickHouse-User` and `X-ClickHouse-Key` headers; the documentation discourages `user` and `password` URL parameters because proxies log them.

```bash
# REASONED, not demonstrated here: the authoring environment has no running ClickHouse (no server binary or
# container runtime), so the shell syntax and the guards were checked locally but the exposed-vs-fixed
# responses were not. Backlog row 1.77 tracks running these against a live server in both states.
# ss is a listener inventory in THIS network namespace - not a firewall, NAT, publication, or auth check.
ss -tlnp   # expect 8443 and 9440, plus only the private listeners you deliberately kept (e.g. replication
           # HTTPS 9010); inspect host/container publications and firewall separately, and probe external
           # reachability from the client networks - this list alone proves neither exposure nor auth
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_CLICKHOUSE_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 2; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute the host on the set -- line above; not probing"; exit 2 ;; esac
  host=$1
  set +e   # inspect each probe's outcome from its write-out below, not via an inherited set -e
  # Private CA or self-signed: keep verification ON and point curl at the CA. Never -k. For a public CA,
  # remove the two --cacert arguments from the array below.
  common=(-sS --noproxy '*' --connect-timeout 5 --max-time 20 --cacert /etc/clickhouse-server/certs/ca.crt)
  fmt='\nhttp=%{http_code} exit=%{exitcode} remote=%{remote_ip} err=%{errormsg}\n'
  # 1) Disabled plaintext HTTP 8123 on the SAME origin. Read the HTTP status independently of curl's exit:
  #    ANY received status (even if a later transfer error follows, e.g. curl exit 18) proves the port answered.
  code=$(curl -q -g "${common[@]}" -o /dev/null -w '%{http_code}' "http://$host:8123/?query=SELECT%201"); rc=$?
  printf 'plaintext http=%s exit=%s\n' "$code" "$rc"
  if [ "$code" != 000 ]; then
    echo 'FAIL: plaintext HTTP 8123 answered (any status here means the plaintext port is still serving)'
  else
    echo "plaintext probe: transport error (curl exit $rc); this alone does not prove the port is disabled"
  fi
  # 2) HTTPS origin as `app`, a matched triple against the SAME origin. Read the password once with no echo
  #    and pass both credential headers on stdin, so the secret never enters argv or history.
  IFS= read -r -s -p 'app password: ' apppw || {
    echo 'password input failed; not probing authentication'; exit 2;
  }
  echo
  [ -n "$apppw" ] || {
    echo 'supply the configured nonempty password; not probing authentication'; exit 2;
  }
  for label in empty wrong correct; do
    case $label in
      empty)   pw='' ;;
      wrong)   pw='definitely-not-the-password' ;;
      correct) pw=$apppw ;;
    esac
    printf 'X-ClickHouse-User: app\nX-ClickHouse-Key: %s\n' "$pw" \
      | { echo "[$label]"; curl -q -g "${common[@]}" -w "$fmt" -H @- "https://$host:8443/?query=SELECT%201"; }
  done
  unset apppw pw
  # Native 9440 is a SEPARATE authenticator: SELECT 1 as `app` at each prompt, the wrong password then the
  # correct one. For a private CA, configure the client's openSSL.client.caConfig; keep --secure. Fixed:
  # `wrong` gives a native auth error and a nonzero exit, `correct` returns 1 and exits 0. A transport or
  # certificate error is inconclusive. Test the `default` account separately.
  for label in wrong correct; do
    printf '\n[native %s] enter the %s password at the prompt.\n' "$label" "$label"
    clickhouse-client --host "$host" --port 9440 --secure --user app --query 'SELECT 1' --password
    printf 'native_exit=%s\n' "$?"
  done
)
```

Exposed HTTPS origin: `empty` and `wrong` return an HTTP 200 data body (auth not enforced). Fixed origin: both
return a ClickHouse authentication error and `correct` returns the `SELECT` result. A DNS, proxy, certificate,
or connection error is inconclusive, not a pass: fix the trust or path and retry.

## Common mistakes

- `<listen_host>::</listen_host>` uncommented to reach the server from a laptop, with `default` still passwordless.
- A password set on `default` while `<networks>` still says `::/0`, so the one administrator account is guessable from anywhere.
- `https_port` added while `http_port` 8123 stays open beside it.

## Sources (checked September 2026)

- Server settings: [`listen_host`](https://clickhouse.com/docs/reference/settings/server-settings/settings/listen#listen_host), [`openSSL`](https://clickhouse.com/docs/reference/settings/server-settings/settings/other#openSSL), [`interserver_listen_host`](https://clickhouse.com/docs/reference/settings/server-settings/settings/interserver#interserver_listen_host), [`interserver_http_credentials`](https://clickhouse.com/docs/reference/settings/server-settings/settings/interserver-http#interserver_http_credentials)
- Shipped `config.xml` (`listen_host` default comment, `openSSL` block): https://raw.githubusercontent.com/ClickHouse/ClickHouse/master/programs/server/config.xml
- User settings (`password_sha256_hex`, `networks`, `access_management`): https://clickhouse.com/docs/concepts/features/configuration/settings/settings-users
- Shipped `users.xml` (default user, empty password, `::/0`): https://raw.githubusercontent.com/ClickHouse/ClickHouse/master/programs/server/users.xml
- Access control and account management: https://clickhouse.com/docs/concepts/features/security/access-rights
- CREATE USER: https://clickhouse.com/docs/reference/statements/create/user
- GRANT: https://clickhouse.com/docs/reference/statements/grant
- Configuring SSL-TLS: https://clickhouse.com/docs/concepts/features/security/tls/configuring-tls
- HTTP interface (ports, authentication): https://clickhouse.com/docs/concepts/features/interfaces/http
- `remote_url_allow_hosts` (host allow-list checked before DNS and on redirects; omitting the section allows all hosts): https://clickhouse.com/docs/reference/settings/server-settings/settings/remote#remote_url_allow_hosts
- External-source privileges (`GRANT`, `SOURCES`; READ/WRITE forms require version 25.7 or later and `access_control_improvements.enable_read_write_grants`): https://clickhouse.com/docs/reference/statements/grant#sources
- External sources: [`url()`](https://clickhouse.com/docs/reference/functions/table-functions/url), [`file()` and `user_files_path`](https://clickhouse.com/docs/reference/functions/table-functions/file), [`remote()`/`remoteSecure()`](https://clickhouse.com/docs/reference/functions/table-functions/remote), and [HTTP(S) dictionary sources](https://clickhouse.com/docs/reference/statements/create/dictionary/sources/http)
- Native TOTP for XML users (`time_based_one_time_password`; not in SQL-driven access control): https://clickhouse.com/docs/concepts/features/configuration/settings/settings-users#totp-authentication-configuration
- ClickHouse 26.2 release (native TOTP): https://clickhouse.com/blog/clickhouse-release-26-02
- Configuration files (`config.d`/`users.d` merging, `remove` and `replace` attributes, `<clickhouse>` root): https://clickhouse.com/docs/concepts/features/configuration/server-config/configuration-files
- Install with Docker (default-user network access when no `CLICKHOUSE_*` env is set): https://clickhouse.com/docs/get-started/setup/self-managed/docker#managing-default-user
- ClickHouse client (`--secure`, native port 9440, `openSSL.client.caConfig`): https://clickhouse.com/docs/concepts/features/interfaces/client
