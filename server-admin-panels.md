# Server administration panels: Cockpit, Webmin, and Proxmox VE

A server administration panel is root on the host behind a login form. Cockpit gives any user who can
escalate with sudo or polkit an administrative session and a terminal. Webmin's packages make the host's
root password a Webmin login with every module, including a root shell. Proxmox VE's web interface is the
whole cluster API, and its `root@pam` user can always log in. All three listen on every interface by
default, none turns on a second factor by default, and none locks out an account after repeated wrong
passwords. Keep them off the public internet: bind them to a management address, allow only management
networks ([cloud-firewalls.md](cloud-firewalls.md), [host.md](host.md)), reach them over a VPN or tunnel
([tunnels.md](tunnels.md)), and turn on each panel's second factor. Versions checked: Cockpit 368, Webmin
2.670 (Usermin 2.570), and Proxmox VE 9.2 (pve-manager 9.2.20, pve-docs 9.2.12).

## Cockpit

Cockpit's socket unit listens on a bare port, `ListenStream=9090`. The systemd reference reads a bare
number as a port "to listen on via IPv6", "available via both IPv6 and IPv4 (default)", so it is
reachable on every address. The port cannot be changed in `cockpit.conf`; restrict it with a socket
drop-in, `/etc/systemd/system/cockpit.socket.d/listen.conf`, whose empty `ListenStream=` line resets the
default before the new one:

```ini
[Socket]
ListenStream=
ListenStream=10.0.0.5:9090
FreeBind=yes
```

Apply it with `sudo systemctl daemon-reload` and `sudo systemctl restart cockpit.socket`. The vendor
calls `FreeBind` "highly recommended when defining specific IP addresses".

Cockpit serves HTTP and HTTPS on the same port and redirects HTTP to HTTPS, except from localhost;
`AllowUnencrypted` defaults to false. Without a certificate in `/etc/cockpit/ws-certs.d`, it creates a
self-signed one. Any local account can log in through the `cockpit` PAM stack. Root is refused by a
deny list, `/etc/cockpit/disallowed-users`, which the upstream packages write only on a first install,
and the PAM line uses `onerr=succeed`, so a missing or unreadable file lets root in. A logged-in user
has "exactly the same privileges as if they logged in via SSH", including the terminal, and Cockpit
escalates the session to root "immediately upon login" when the user can already escalate with sudo or
polkit. There is no built-in second factor; use the PAM stack, Kerberos, or client certificates. There
is no lockout either: `MaxStartups` (default 10) limits concurrent login attempts, not attempts over
time. If Cockpit can also reach a private network, the vendor recommends `LoginTo=false`, which "prevents
unauthenticated remote attackers from scanning the internal network".

## Webmin and Usermin

Webmin listens on TCP 10000 and Usermin on 20000. The installer writes no `bind=` line, and without one
miniserv listens on all IPv4 and IPv6 addresses ("Listening on all IPs"). It also writes `listen=10000`
(Usermin `listen=20000`), which opens a UDP socket on every IPv4 address so other Webmin servers can find
this one. The vendor says Webmin "will accept connections from any IP address" by default and advises
limiting access "so that an attacker from outside your network cannot even attempt to login". In
`/etc/webmin/miniserv.conf`, set `bind=` to a management address, delete the `listen=` line if you do
not use server discovery, add `allow=` with your management networks, then run `/etc/webmin/restart`.

On a loopback run of Webmin 2.670's miniserv with `bind=127.0.0.1` and no `listen=` line, its only
socket was TCP `127.0.0.1` on the test port, with no UDP socket.

The deb and RPM packages turn on HTTPS (`ssl=1`) with a self-signed certificate, and create the Webmin
user `root` with `crypt=x`, which means Unix authentication: the host's root password logs in to Webmin
with every module. They also add `sudo=1`, which lets any Unix user whom sudo permits log in "effectively
as root". The Command Shell module runs commands as root by default. Two-factor authentication (TOTP or
Authy) exists but is not configured on install; turn it on and enroll every user. Vendor advisories
record a two-factor bypass through basic authentication (CVE-2026-42210, CVE-2026-56022) in releases
listed under "Webmin prior to 2.641", so run a current release.

The installer sets `blockhost_failures=5` and `blockhost_time=60`, so a host is blocked for 60 seconds
after five failed logins; per-user blocking is not set. That is a rate limit, not a lockout. Failed
HTTP basic-authentication logins are counted only when `passdelay` is set, which the installer also
writes (`passdelay=1`). On the loopback run with those settings, the fifth wrong password was delayed
past a five-second client timeout by miniserv's growing failure delay, and the right password was then
refused with `403` "Access denied for 127.0.0.1". Keep the network allow list as the real control.

## Proxmox VE

`pveproxy` serves the whole Proxmox VE API over HTTPS on 8006, and `spiceproxy` listens on 3128. By
default both "listen on the wildcard address and accept connections from both IPv4 and IPv6 clients".
`LISTEN_IP` in `/etc/default/pveproxy` restricts the bind, but the vendor warns that it is "not
recommended" on clustered systems, whose nodes need each other's `pveproxy`. The same file takes
`ALLOW_FROM`, `DENY_FROM` and `POLICY`; the default policy is `allow`, under which a client that
matches neither list is allowed, so an `ALLOW_FROM` list restricts nothing until you also set
`DENY_FROM="all"` (the vendor's example) or `POLICY="deny"`. Set one or the other, not both: under
`POLICY="deny"` a client that matches both lists is denied, so adding `DENY_FROM="all"` refuses
everyone. `LISTEN_IP` binds `spiceproxy` as well as `pveproxy`. The Proxmox VE firewall "is
completely disabled by default"; when you enable it, allow 8006, 22 and 3128 from management addresses
only.

The system's `root` user "can always log in via the Linux PAM realm and is an unconfined administrator",
and the installer sets its password for the web interface. Its node shell opens with
`/bin/login -f root`, without a further password. Two-factor authentication (TOTP, WebAuthn, recovery
keys, and realm-enforced TOTP or YubiKey OTP) is available and must be configured. The only lockout is on
the second factor: eight failed TOTP attempts disable that user's TOTP, and after 100 failed WebAuthn or
recovery-key attempts all second factors are blocked for an hour. For passwords, the API delays every
unauthorized response by three seconds. Each cluster creates its own self-signed CA. API tokens have
separated privileges by default, and cannot reach the VM or node consoles.

## Verify

Two checks here were demonstrated: the Webmin configuration check, whose parser was compared with
Webmin 2.670's own on thirty test files, and the TCP reachability probe, which is the block demonstrated
on loopback in [low-code-builders.md](low-code-builders.md) with this guide's ports. Everything else
is reasoned: the authoring host runs neither Cockpit's
systemd socket nor Proxmox VE, and it forbids binding every interface, so no default bind was observed.
Backlog row 1.110 tracks demonstrating the rest.

On the host, list the listeners, TCP and UDP:

```bash
sudo ss -tlnp   # 9090 (Cockpit), 10000 (Webmin), 20000 (Usermin), 8006 and 3128 (Proxmox VE): a management address only
sudo ss -ulnp   # Webmin's discovery socket on UDP 10000 (Usermin 20000) should be gone
```

Exposed, the reasoned expectation is a wildcard address (`*:`, `0.0.0.0:` or `[::]:`) on those ports;
fixed means a management address only. On a Proxmox VE cluster, where the vendor advises against
`LISTEN_IP`, 8006 and 3128 keep their wildcard binds; there the fixed state is the access lists and
firewall below.

On a Webmin host, check the configuration miniserv reads when it starts. The block parses the file
with a copy of miniserv's own `read_config_file` (a line starting with `#` is a comment, spaces around
the name and the value are trimmed, and the last occurrence of a setting wins), then applies
miniserv's rules: `bind=*`, `bind=0`, `bind=0.0.0.0`, `bind=::`, or an empty or missing `bind=` means
every address. The block reads the value with the system's numeric address parser, `inet_pton`, which
never looks up a name: an all-zero IPv4 or IPv6 address is reported as every address, any other
IPv4 or IPv6 address the parser accepts is printed as it is, except an IPv4-mapped IPv6 address, and
every other value is flagged for checking with `ss`;
`sockets=` adds listeners; a `listen=` value other than empty or `0` opens the UDP discovery socket;
and an empty `allow=` lets every client address try to log in, except those a `deny=` list refuses. It describes the file, not the running process:
`ss` above is the authority for what is listening now, and a change takes effect at
`/etc/webmin/restart`. Substitute the file path inside the single quotes (the package default is
`/etc/webmin/miniserv.conf`), and paste the whole block.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_MINISERV_CONF'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not checking"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not checking"; exit; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute your file on the set -- line above; not checking"; exit ;; esac
  { [ -f "$1" ] && [ -r "$1" ]; } || { echo "cannot read $1 as a regular file (try sudo); not checked"; exit; }
  command -v perl >/dev/null || { echo "perl is not installed here; not checking"; exit; }
  # shellcheck disable=SC2016  # the single-quoted Perl program is meant to expand its own variables
  perl -MSocket -e '
    open(CONF, "<", $ARGV[0]) || exit 2;
    while (<CONF>) {
      s/\r|\n//g;
      if (/^#/ || !/\S/) { next; }
      /^([^=]+)=(.*)$/;
      $name = $1; $val = $2;
      $name =~ s/^\s+//g; $name =~ s/\s+$//g;
      $val =~ s/^\s+//g; $val =~ s/\s+$//g;
      $rv{$name} = $val;
    }
    close(CONF);
    $bind = $rv{"bind"}; $bind = "" if ($bind eq "*");
    $v4 = $bind eq "" ? undef : Socket::inet_pton(Socket::AF_INET(), $bind);
    $v6 = (defined($v4) || $bind !~ /:/) ? undef : Socket::inet_pton(Socket::AF_INET6(), $bind);
    if (!$bind || (defined($v4) && $v4 eq "\0" x 4) || (defined($v6) && $v6 eq "\0" x 16)) { print "NO effective bind=: every address\n"; }
    elsif (defined($v4) || (defined($v6) && substr($v6, 0, 12) ne ("\0" x 10) . "\xff\xff")) { print "bind=$bind\n"; }
    else { print "bind=$bind: not a plain IPv4 or IPv6 address; check with ss what miniserv binds\n"; }
    print "sockets=$rv{sockets}: extra listeners, possibly on every address; check ss\n" if ($rv{"sockets"} =~ /\S/);
    print $rv{"listen"} ? "listen=$rv{listen}: UDP discovery socket on every IPv4 address\n" : "no UDP discovery socket\n";
    @allow = split(/\s+/, $rv{"allow"});
    @deny = split(/\s+/, $rv{"deny"});
    print "deny=@deny\n" if (@deny);
    print @allow ? "allow=@allow\n" : @deny ? "NO allow=: any client address not on deny= may try to log in\n" : "NO allow=: any client address may try to log in\n";
    print "sudo=$rv{sudo}: Unix users whom sudo permits can log in as root\n" if ($rv{"sudo"});
    exit 0;
  ' "$1"
  case "$?" in 0) ;; *) echo "could not read $1; not checked" ;; esac
)
```

Exposed: "NO effective bind=", a `listen=` line and "NO allow=". Fixed: a management address on
`bind=`, "no UDP discovery socket" and only your management networks on `allow=`; the block prints
the lists as written, so check each entry. A `sockets=` line means more listeners; check each with
`ss`. This was demonstrated on thirty test files: the loopback run's configuration, its exposed
variant, a repeated `bind=` whose last value is `*`, `bind=0.0.0.0`, `bind=::`,
`bind=0:0:0:0:0:0:0:0`, four IPv6 addresses printed as they are (`2001:db8::5`,
`0:0:0:0:ffff:0:0:1`, `::ffff:0` and `64:ff9b::10.0.0.5`), and fourteen values flagged for `ss`
(`0x0`, `0x00000000`, `0x0a000005`, `010.0.0.5`, `cafe`, `0 10.0.0.5`, `::ffff:0:0`, `::ffff:10.0.0.5`,
`1::2::3`, `a:b:c`, `12345::1`, `1:2:3`, `:::1` and `2001:db8:5`), spaced settings, commented settings, `bind=0` with `listen=0` and an empty
`allow=`, an empty `allow=` with `deny=127.0.0.1`, CRLF line endings with `sockets=*:10001`, and a line
without `=`. On each, the copy's parsed values matched Webmin 2.670's own `read_config_file` run on
the same file, and the block printed the outcomes above; it reported an unreadable path as not
checked.

On a Cockpit host, reasoned: `systemctl cat cockpit.socket` shows the effective listeners; exposed is a
bare `ListenStream=9090`, fixed is the drop-in's empty `ListenStream=` followed by an address and port.
`sudo cat /etc/cockpit/disallowed-users` should list `root`; a missing file lets root log in.

On a Proxmox VE node, reasoned: `grep -E '^(LISTEN_IP|ALLOW_FROM|DENY_FROM|POLICY)=' /etc/default/pveproxy`
prints nothing on a default install (or reports that the file does not exist), which means the
wildcard bind and the `allow` policy. Fixed is `LISTEN_IP` set to a management address on a single
node, or `ALLOW_FROM` with your management networks together with `DENY_FROM="all"` or
`POLICY="deny"` (one of the two, not both); an `ALLOW_FROM` line alone is not fixed, because under the `allow` policy a client
that matches neither list is allowed (the access table in the vendor's `pveproxy` documentation).
`pve-firewall status` prints whether the firewall is enabled and running. Exposed is disabled, the
default; fixed is enabled and running, with rules that allow 8006, 22 and 3128 only from management
addresses, which you confirm in the datacenter and node firewall rules in the web interface. In the web interface, check
that every administrative user, `root@pam` included, has a second factor.

Finally, from a host that should not have access, try a TCP connection to each panel port. The block
takes one IP address rather than a host name, so that a name with both IPv4 and IPv6 addresses cannot
hide one behind a timeout on the other: run it once for each public address of the server. It also
takes a port you know is open on that address from this host (for example SSH on 22) as the positive
control, and stops if the control does not connect. Substitute both inside the single quotes.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ONE_IP_ADDRESS' 'REPLACE_WITH_A_KNOWN_OPEN_PORT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute one IP address on the set -- line above; not probing"; exit ;; esac
  case "$1" in 0.0.0.0) echo "$1 reaches this host itself; give the public address of the service; not probing"; exit ;; esac
  ipv4='^((25[012345]|2[01234][0123456789]|1[0123456789][0123456789]|[123456789]?[0123456789])[.]){3}(25[012345]|2[01234][0123456789]|1[0123456789][0123456789]|[123456789]?[0123456789])$'
  case "$1" in
    *:*:*)
      case "$1" in *[!0123456789ABCDEFabcdef.:]*) echo "$1 is not an IPv6 address; not probing"; exit ;; esac
      case "$1" in *.*) echo "give the IPv4 address itself rather than $1; not probing"; exit ;; esac
      case "$1" in *[!0:]*) ;; *) echo "$1 is all zeros (this host itself, or not an address); give the public address of the service; not probing"; exit ;; esac ;;
    *) [[ $1 =~ $ipv4 ]] || { echo "give one IPv4 address (four numbers, 0 to 255, joined by dots) or one IPv6 address, with no host name, port or brackets; not probing"; exit; } ;;
  esac
  case "$2" in *[!0123456789]*|"") echo "substitute a known-open control port on the set -- line above; not probing"; exit ;; esac
  { [ "$2" -ge 1 ] && [ "$2" -le 65535 ]; } 2>/dev/null || { echo "the control port must be 1 to 65535; not probing"; exit; }
  command -v timeout >/dev/null || { echo "timeout is not installed here; not probing"; exit; }
  # shellcheck disable=SC2016  # the single-quoted script is meant to expand $1 and $2 in the child shell
  err=$(LC_ALL=C timeout 5 bash -c ': > "/dev/tcp/$1/$2"' probe "$1" "$2" 2>&1) ||
    { echo "control $1:$2 did not connect (${err:-timed out}); not probing"; exit; }
  echo "control $1:$2 connected"
  for p in 9090 10000 20000 8006 3128; do
    # shellcheck disable=SC2016  # the single-quoted script is meant to expand $1 and $2 in the child shell
    err=$(LC_ALL=C timeout 5 bash -c ': > "/dev/tcp/$1/$2"' probe "$1" "$p" 2>&1)
    case "$?:$err" in
      0:*) echo "$1:$p connected: reachable from this host" ;;
      124:*) echo "$1:$p timed out from this host" ;;
      *"Connection refused"*) echo "$1:$p refused from this host" ;;
      *) echo "$1:$p inconclusive (not a connection, refusal or timeout): ${err:-no message}" ;;
    esac
  done
)
```

Exposed, a panel port reports "connected"; a transparent proxy on the probing host's network can
also complete the handshake, so confirm a surprising "connected" with `ss` on the server. "refused"
and "timed out" show only that this host could not reach the port: a firewall in front of the server
produces either, but so can filtering on the probing host's own network, and the control proves only
its own port. Treat them as consistent with fixed, and take `ss` on the server as the authority; the
probe does not test Webmin's UDP discovery socket, which only `ss -ulnp` shows. "inconclusive" is any
other result and says nothing about the port. The block is the one demonstrated in
[low-code-builders.md](low-code-builders.md) with only the port list changed; that guide lists the
values it was measured to refuse. It refuses `0.0.0.0`, IPv6 values made only of zeros and colons,
and IPv6 values containing a dot, but not every value that reaches the probing host: loopback
addresses pass, and hex spellings such as `::ffff:0:0` connected to a listener bound to 127.0.0.1, so
give the server's public address. A "connected" on a port you did not mean to expose is the finding.

## Sources (checked September 2026)

- Cockpit 368 socket unit: https://github.com/cockpit-project/cockpit/blob/368/src/systemd/cockpit.socket.in
- Cockpit 368 listening address and port: https://github.com/cockpit-project/cockpit/blob/368/doc/modules/guide/pages/listen.adoc
- Cockpit 368 HTTPS and certificates: https://github.com/cockpit-project/cockpit/blob/368/doc/modules/guide/pages/https.adoc
- Cockpit 368 `cockpit.conf` reference (`AllowUnencrypted`, `MaxStartups`, `LoginTo`): https://github.com/cockpit-project/cockpit/blob/368/doc/modules/man/pages/cockpit.conf.5.adoc
- Cockpit 368 authentication: https://github.com/cockpit-project/cockpit/blob/368/doc/modules/guide/pages/authentication.adoc
- Cockpit 368 privileges: https://github.com/cockpit-project/cockpit/blob/368/doc/modules/guide/pages/privileges.adoc
- Cockpit 368 PAM stack and root deny list: https://github.com/cockpit-project/cockpit/blob/368/tools/cockpit.pam and https://github.com/cockpit-project/cockpit/blob/368/tools/cockpit.spec
- systemd v262 socket unit reference (bare port): https://github.com/systemd/systemd/blob/v262/man/systemd.socket.xml
- Webmin 2.670 installer (`listen=`, `blockhost_*`, `passdelay=1`, certificate): https://github.com/webmin/webmin/blob/2.670/setup.sh
- Webmin 2.670 miniserv (`bind`, `sockets` and the discovery socket): https://github.com/webmin/webmin/blob/2.670/miniserv.pl
- Webmin 2.670 deb and RPM package builders (`crypt=x`, `ssl=1`, `sudo=1`): https://github.com/webmin/webmin/blob/2.670/makedebian.pl and https://github.com/webmin/webmin/blob/2.670/makerpm.pl
- Webmin 2.670 sudo login, configuration parser (`read_config_file`), allow and deny lists, and basic-authentication failure counting (`passdelay`): https://github.com/webmin/webmin/blob/2.670/miniserv-lib.pl
- Webmin 2.670 Command Shell default ACL: https://github.com/webmin/webmin/blob/2.670/shell/defaultacl
- Webmin 2.670 two-factor providers: https://github.com/webmin/webmin/blob/2.670/webmin/twofactor-funcs-lib.pl
- Webmin documentation (configuration, security advisories): https://github.com/webmin/webmin.com/blob/8ceae26c5a074053905cbcc6c0053be573633f3a/content/docs/Modules/webmin-configuration.md and https://github.com/webmin/webmin.com/blob/8ceae26c5a074053905cbcc6c0053be573633f3a/content/security.md
- Usermin 2.570 installer: https://github.com/webmin/usermin/blob/2.570/setup.sh
- Proxmox VE `pveproxy` (bind, `LISTEN_IP`, access lists): https://git.proxmox.com/?p=pve-docs.git;a=blob_plain;hb=9370638116430c4b1ccb9707b5716eaad7c7c9d3;f=pveproxy.adoc
- Proxmox VE user management (root@pam, two-factor, lockout, API tokens): https://git.proxmox.com/?p=pve-docs.git;a=blob_plain;hb=9370638116430c4b1ccb9707b5716eaad7c7c9d3;f=pveum.adoc
- Proxmox VE firewall: https://git.proxmox.com/?p=pve-docs.git;a=blob_plain;hb=9370638116430c4b1ccb9707b5716eaad7c7c9d3;f=pve-firewall.adoc
- Proxmox VE certificates: https://git.proxmox.com/?p=pve-docs.git;a=blob_plain;hb=9370638116430c4b1ccb9707b5716eaad7c7c9d3;f=certificate-management.adoc
- Proxmox VE node shell (`/bin/login -f root`): https://git.proxmox.com/?p=pve-manager.git;a=blob_plain;hb=49318c671b82f31e6b273b79447526161739b97a;f=PVE/API2/Nodes.pm
- Proxmox VE HTTP server (three-second delay on unauthorized responses): https://git.proxmox.com/?p=pve-http-server.git;a=blob_plain;hb=5119ff9bec08c69584c0c98bea3edd0098179e5f;f=src/PVE/APIServer/AnyEvent.pm
