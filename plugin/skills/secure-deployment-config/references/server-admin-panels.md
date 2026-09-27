---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "ad4e678700a70620ed705a45b599224a166de38542c77e7cb3950eb3de417bd0",
  "components": {
    "cockpit": {
      "name": "Cockpit",
      "basis": "368",
      "sources": {
        "sc42ba09017c7": "https://github.com/cockpit-project/cockpit/blob/368/src/systemd/cockpit.socket.in",
        "s0c1e0db624a4": "https://github.com/cockpit-project/cockpit/blob/368/doc/modules/guide/pages/listen.adoc",
        "sd0cb4ea3db56": "https://github.com/cockpit-project/cockpit/blob/368/doc/modules/guide/pages/https.adoc",
        "sf157ab3a6f47": "https://github.com/cockpit-project/cockpit/blob/368/doc/modules/man/pages/cockpit.conf.5.adoc",
        "s48ebdec28e10": "https://github.com/cockpit-project/cockpit/blob/368/doc/modules/guide/pages/authentication.adoc",
        "s2432e599485f": "https://github.com/cockpit-project/cockpit/blob/368/doc/modules/guide/pages/privileges.adoc",
        "sbdcd6e74a0c7": "https://github.com/cockpit-project/cockpit/blob/368/tools/cockpit.pam",
        "sc20103cfb39b": "https://github.com/cockpit-project/cockpit/blob/368/tools/cockpit.spec"
      }
    },
    "systemd": {
      "name": "systemd",
      "basis": "v262",
      "sources": {
        "s0a96457c713e": "https://github.com/systemd/systemd/blob/v262/man/systemd.socket.xml"
      }
    },
    "webmin": {
      "name": "Webmin",
      "basis": "2.670",
      "sources": {
        "sa4f7ac343e85": "https://github.com/webmin/webmin/blob/2.670/setup.sh",
        "sb8fec2baa0f2": "https://github.com/webmin/webmin/blob/2.670/miniserv.pl",
        "sdd465cac1ff8": "https://github.com/webmin/webmin/blob/2.670/makedebian.pl",
        "s9ecba8f15014": "https://github.com/webmin/webmin/blob/2.670/makerpm.pl",
        "sdb2ef2bf9978": "https://github.com/webmin/webmin/blob/2.670/miniserv-lib.pl",
        "s1a1dbd21dddd": "https://github.com/webmin/webmin/blob/2.670/shell/defaultacl",
        "s2f3504ad1328": "https://github.com/webmin/webmin/blob/2.670/webmin/twofactor-funcs-lib.pl"
      }
    },
    "webmin-docs": {
      "name": "Webmin docs",
      "basis": "8ceae26c5a074053905cbcc6c0053be573633f3a",
      "sources": {
        "s7a91f9f23044": "https://github.com/webmin/webmin.com/blob/8ceae26c5a074053905cbcc6c0053be573633f3a/content/docs/Modules/webmin-configuration.md",
        "s8b072a3403d1": "https://github.com/webmin/webmin.com/blob/8ceae26c5a074053905cbcc6c0053be573633f3a/content/security.md"
      }
    },
    "usermin": {
      "name": "Usermin",
      "basis": "2.570",
      "sources": {
        "s7fe74c9a3138": "https://github.com/webmin/usermin/blob/2.570/setup.sh"
      }
    },
    "pve-docs": {
      "name": "Proxmox VE 9.2 docs",
      "basis": "9.2.12",
      "sources": {
        "s8538bab3d3fc": "https://git.proxmox.com/?p=pve-docs.git;a=blob_plain;hb=9370638116430c4b1ccb9707b5716eaad7c7c9d3;f=pveproxy.adoc",
        "sdbc681682e8f": "https://git.proxmox.com/?p=pve-docs.git;a=blob_plain;hb=9370638116430c4b1ccb9707b5716eaad7c7c9d3;f=pveum.adoc",
        "sc6bbbfe64d09": "https://git.proxmox.com/?p=pve-docs.git;a=blob_plain;hb=9370638116430c4b1ccb9707b5716eaad7c7c9d3;f=pve-firewall.adoc",
        "s31f242f10eaa": "https://git.proxmox.com/?p=pve-docs.git;a=blob_plain;hb=9370638116430c4b1ccb9707b5716eaad7c7c9d3;f=certificate-management.adoc"
      }
    },
    "pve-manager": {
      "name": "pve-manager",
      "basis": "9.2.20",
      "sources": {
        "se4c11b901cf8": "https://git.proxmox.com/?p=pve-manager.git;a=blob_plain;hb=49318c671b82f31e6b273b79447526161739b97a;f=PVE/API2/Nodes.pm"
      }
    },
    "pve-http": {
      "name": "Proxmox HTTP server",
      "basis": "5119ff9bec08c69584c0c98bea3edd0098179e5f",
      "sources": {
        "s753d88abe320": "https://git.proxmox.com/?p=pve-http-server.git;a=blob_plain;hb=5119ff9bec08c69584c0c98bea3edd0098179e5f;f=src/PVE/APIServer/AnyEvent.pm"
      }
    }
  },
  "claims": {
    "private": {"text": "Keep root-capable panels off the internet, bound/restricted to management networks with private access and a second factor.", "components": ["cockpit", "webmin-docs", "pve-docs"], "sources": ["cockpit:s0c1e0db624a4", "webmin-docs:s7a91f9f23044", "pve-docs:s8538bab3d3fc", "pve-docs:sc6bbbfe64d09"], "status": "REASONED"},
    "cockpit-bind": {"text": "Bare ListenStream=9090 binds IPv6 and, by default, IPv4 wildcard addresses.", "components": ["cockpit", "systemd"], "sources": ["cockpit:sc42ba09017c7", "systemd:s0a96457c713e"], "status": "REASONED"},
    "cockpit-dropin": {"text": "Use a socket drop-in, not cockpit.conf: reset ListenStream, set 10.0.0.5:9090 and FreeBind=yes, then daemon-reload/restart.", "components": ["cockpit"], "sources": ["cockpit:s0c1e0db624a4"], "status": "REASONED"},
    "cockpit-tls": {"text": "One port serves HTTP/HTTPS, redirecting HTTP except localhost; AllowUnencrypted defaults false and missing certificates cause self-signed creation.", "components": ["cockpit"], "sources": ["cockpit:sd0cb4ea3db56", "cockpit:sf157ab3a6f47"], "status": "REASONED"},
    "cockpit-pam": {"text": "Local accounts use Cockpit PAM with normal SSH-equivalent privileges.", "components": ["cockpit"], "sources": ["cockpit:s48ebdec28e10"], "status": "REASONED"},
    "cockpit-root": {"text": "First-install packages write root to disallowed-users; onerr=succeed permits root if that file is missing/unreadable.", "components": ["cockpit"], "sources": ["cockpit:sbdcd6e74a0c7", "cockpit:sc20103cfb39b"], "status": "REASONED"},
    "cockpit-escalation": {"text": "Users allowed sudo/polkit escalation get an immediately elevated session and terminal.", "components": ["cockpit"], "sources": ["cockpit:s2432e599485f"], "status": "REASONED"},
    "cockpit-mfa": {"text": "No built-in second factor; use PAM, Kerberos or client certificates.", "components": ["cockpit"], "sources": ["cockpit:s48ebdec28e10"], "status": "REASONED"},
    "cockpit-rate": {"text": "MaxStartups defaults to 10 concurrent attempts, not repeated-password lockout.", "components": ["cockpit"], "sources": ["cockpit:sf157ab3a6f47"], "status": "REASONED"},
    "cockpit-loginto": {"text": "Set LoginTo=false to prevent unauthenticated scanning of reachable private networks.", "components": ["cockpit"], "sources": ["cockpit:sf157ab3a6f47"], "status": "REASONED"},
    "webmin-bind": {"text": "Webmin/Usermin TCP ports are 10000/20000; omitted bind makes miniserv listen on all IPv4/IPv6 addresses.", "components": ["webmin", "usermin"], "sources": ["webmin:sa4f7ac343e85", "webmin:sb8fec2baa0f2", "usermin:s7fe74c9a3138"], "status": "REASONED"},
    "webmin-discovery": {"text": "Installed listen=10000/20000 opens discovery UDP on every IPv4 address; delete when unused.", "components": ["webmin", "usermin"], "sources": ["webmin:sa4f7ac343e85", "webmin:sb8fec2baa0f2", "usermin:s7fe74c9a3138"], "status": "REASONED"},
    "webmin-access": {"text": "Set management bind and allow networks, then restart; empty allow admits all except denied clients.", "components": ["webmin", "webmin-docs"], "sources": ["webmin:sb8fec2baa0f2", "webmin:sdb2ef2bf9978", "webmin-docs:s7a91f9f23044"], "status": "REASONED"},
    "webmin-tls": {"text": "Deb/RPM packages enable ssl=1 with a self-signed certificate.", "components": ["webmin"], "sources": ["webmin:sa4f7ac343e85", "webmin:sdd465cac1ff8", "webmin:s9ecba8f15014"], "status": "REASONED"},
    "webmin-root": {"text": "Installed root crypt=x accepts the Unix root password with all modules; Command Shell defaults to root.", "components": ["webmin"], "sources": ["webmin:sdd465cac1ff8", "webmin:s9ecba8f15014", "webmin:s1a1dbd21dddd"], "status": "REASONED"},
    "webmin-sudo": {"text": "Installed sudo=1 lets sudo-permitted Unix users log in effectively as root.", "components": ["webmin"], "sources": ["webmin:sdd465cac1ff8", "webmin:s9ecba8f15014", "webmin:sdb2ef2bf9978"], "status": "REASONED"},
    "webmin-mfa": {"text": "TOTP/Authy exists but is not configured at install; enable and enrol every user.", "components": ["webmin"], "sources": ["webmin:s2f3504ad1328"], "status": "REASONED"},
    "webmin-advisories": {"text": "Advisories list Basic-auth MFA bypasses CVE-2026-42210/CVE-2026-56022 under Webmin prior to 2.641; use a current release.", "components": ["webmin-docs"], "sources": ["webmin-docs:s8b072a3403d1"], "status": "REASONED"},
    "webmin-rate": {"text": "Defaults blockhost_failures=5/blockhost_time=60 block a host for 60 seconds, not a user lockout; Basic-auth failures count only with installed passdelay=1.", "components": ["webmin"], "sources": ["webmin:sa4f7ac343e85", "webmin:sdb2ef2bf9978"], "status": "REASONED"},
    "pve-bind": {"text": "pveproxy HTTPS API 8006 and spiceproxy 3128 default IPv4/IPv6 wildcard; both share LISTEN_IP in /etc/default/pveproxy.", "components": ["pve-docs"], "sources": ["pve-docs:s8538bab3d3fc"], "status": "REASONED"},
    "pve-cluster": {"text": "LISTEN_IP is not recommended on clusters needing peer pveproxy access; use ACLs/firewall.", "components": ["pve-docs"], "sources": ["pve-docs:s8538bab3d3fc"], "status": "REASONED"},
    "pve-acl": {"text": "Default allow policy admits unmatched clients; ALLOW_FROM needs DENY_FROM=all or POLICY=deny, not both because deny policy rejects dual matches.", "components": ["pve-docs"], "sources": ["pve-docs:s8538bab3d3fc"], "status": "REASONED"},
    "pve-firewall": {"text": "Firewall defaults disabled; enable and restrict 8006/22/3128 to management addresses.", "components": ["pve-docs"], "sources": ["pve-docs:sc6bbbfe64d09"], "status": "REASONED"},
    "pve-root": {"text": "root@pam can always log in as unconfined admin; installer sets the web-interface root password.", "components": ["pve-docs"], "sources": ["pve-docs:sdbc681682e8f"], "status": "REASONED"},
    "pve-shell": {"text": "Node shell opens /bin/login -f root without another password.", "components": ["pve-manager"], "sources": ["pve-manager:se4c11b901cf8"], "status": "REASONED"},
    "pve-mfa": {"text": "Configure TOTP, WebAuthn, recovery keys or realm-enforced TOTP/YubiKey OTP; no default second factor.", "components": ["pve-docs"], "sources": ["pve-docs:sdbc681682e8f"], "status": "REASONED"},
    "pve-lockout": {"text": "Eight TOTP failures disable TOTP; 100 WebAuthn/recovery-key failures block all factors for an hour. These are second-factor lockouts.", "components": ["pve-docs"], "sources": ["pve-docs:sdbc681682e8f"], "status": "REASONED"},
    "pve-password-delay": {"text": "Unauthorized API responses delay three seconds; this is not password lockout.", "components": ["pve-http"], "sources": ["pve-http:s753d88abe320"], "status": "REASONED"},
    "pve-certificates": {"text": "Each cluster creates its own self-signed CA.", "components": ["pve-docs"], "sources": ["pve-docs:s31f242f10eaa"], "status": "REASONED"},
    "pve-tokens": {"text": "API tokens default to separated privileges and cannot access VM/node consoles.", "components": ["pve-docs"], "sources": ["pve-docs:sdbc681682e8f"], "status": "REASONED"},
    "verify-cockpit": {"text": "Inspect effective socket reset/address and root deny file; bare port or missing deny file exposes documented defaults.", "components": ["cockpit"], "sources": ["cockpit:sc42ba09017c7", "cockpit:s0c1e0db624a4", "cockpit:sbdcd6e74a0c7", "cockpit:sc20103cfb39b"], "status": "REASONED"},
    "verify-pve": {"text": "Inspect LISTEN_IP/ACL policy, enabled/running firewall and management-only rules, and every admin's second factor including root@pam.", "components": ["pve-docs"], "sources": ["pve-docs:s8538bab3d3fc", "pve-docs:sdbc681682e8f", "pve-docs:sc6bbbfe64d09"], "status": "REASONED"},
    "verify-external": {"text": "Probe each public IP with a reachable control; refusal/timeout is only consistent with isolation. TCP does not test Webmin UDP.", "components": ["cockpit", "webmin", "usermin", "pve-docs"], "sources": ["cockpit:sc42ba09017c7", "webmin:sb8fec2baa0f2", "usermin:s7fe74c9a3138", "pve-docs:s8538bab3d3fc"], "status": "REASONED"},
    "webmin-loopback": {"text": "Loopback bind with no listen line produced one TCP socket and no UDP.", "components": ["webmin"], "sources": ["webmin:sb8fec2baa0f2"], "status": "DEMONSTRATED", "evidence": "its only socket was TCP `127.0.0.1` on the test port, with no UDP socket."},
    "webmin-rate-run": {"text": "Fifth wrong password exceeded a five-second timeout; then even the right password received host-block 403.", "components": ["webmin"], "sources": ["webmin:sa4f7ac343e85", "webmin:sdb2ef2bf9978"], "status": "DEMONSTRATED", "evidence": "the fifth wrong password was delayed past a five-second client timeout by miniserv's growing failure delay, and the right password was then refused with `403` \"Access denied for 127.0.0.1\"."},
    "verify-listeners": {"text": "Expect management TCP binds and no discovery UDP; clustered Proxmox may retain wildcards with ACL/firewall protection.", "components": ["cockpit", "webmin", "usermin", "pve-docs"], "sources": ["cockpit:sc42ba09017c7", "webmin:sb8fec2baa0f2", "usermin:s7fe74c9a3138", "pve-docs:s8538bab3d3fc"], "status": "REASONED", "verify": [1]},
    "verify-webmin-parser": {"text": "Thirty fixtures matched miniserv parsing and bind/sockets/discovery/ACL outputs; unreadable paths were not checked. File inspection is not running-state proof.", "components": ["webmin"], "sources": ["webmin:sb8fec2baa0f2", "webmin:sdb2ef2bf9978"], "status": "DEMONSTRATED", "evidence": "On each, the copy's parsed values matched Webmin 2.670's own `read_config_file` run on the same file, and the block printed the outcomes above; it reported an unreadable path as not checked.", "verify": [2]},
    "verify-tcp-loopback": {"text": "Copied probe has recorded loopback provenance, not live panel-isolation evidence; loopback and mapped hex addresses pass its guard.", "components": ["cockpit", "webmin", "usermin", "pve-docs"], "sources": ["cockpit:sc42ba09017c7", "webmin:sb8fec2baa0f2", "usermin:s7fe74c9a3138", "pve-docs:s8538bab3d3fc"], "status": "DEMONSTRATED", "evidence": "loopback addresses pass, and hex spellings such as `::ffff:0:0` connected to a listener bound to 127.0.0.1", "verify": [3]}
  }
}
---
# Server administration panels: Cockpit, Webmin, and Proxmox VE

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| private: Keep root-capable panels off the internet, bound/restricted to management networks with private access and a second factor. | Cockpit 368; Webmin docs 8ceae26c5a074053905cbcc6c0053be573633f3a; Proxmox VE 9.2 docs 9.2.12 | REASONED |
| cockpit-bind: Bare ListenStream=9090 binds IPv6 and, by default, IPv4 wildcard addresses. | Cockpit 368; systemd v262 | REASONED |
| cockpit-dropin: Use a socket drop-in, not cockpit.conf: reset ListenStream, set 10.0.0.5:9090 and FreeBind=yes, then daemon-reload/restart. | Cockpit 368 | REASONED |
| cockpit-tls: One port serves HTTP/HTTPS, redirecting HTTP except localhost; AllowUnencrypted defaults false and missing certificates cause self-signed creation. | Cockpit 368 | REASONED |
| cockpit-pam: Local accounts use Cockpit PAM with normal SSH-equivalent privileges. | Cockpit 368 | REASONED |
| cockpit-root: First-install packages write root to disallowed-users; onerr=succeed permits root if that file is missing/unreadable. | Cockpit 368 | REASONED |
| cockpit-escalation: Users allowed sudo/polkit escalation get an immediately elevated session and terminal. | Cockpit 368 | REASONED |
| cockpit-mfa: No built-in second factor; use PAM, Kerberos or client certificates. | Cockpit 368 | REASONED |
| cockpit-rate: MaxStartups defaults to 10 concurrent attempts, not repeated-password lockout. | Cockpit 368 | REASONED |
| cockpit-loginto: Set LoginTo=false to prevent unauthenticated scanning of reachable private networks. | Cockpit 368 | REASONED |
| webmin-bind: Webmin/Usermin TCP ports are 10000/20000; omitted bind makes miniserv listen on all IPv4/IPv6 addresses. | Webmin 2.670; Usermin 2.570 | REASONED |
| webmin-discovery: Installed listen=10000/20000 opens discovery UDP on every IPv4 address; delete when unused. | Webmin 2.670; Usermin 2.570 | REASONED |
| webmin-access: Set management bind and allow networks, then restart; empty allow admits all except denied clients. | Webmin 2.670; Webmin docs 8ceae26c5a074053905cbcc6c0053be573633f3a | REASONED |
| webmin-tls: Deb/RPM packages enable ssl=1 with a self-signed certificate. | Webmin 2.670 | REASONED |
| webmin-root: Installed root crypt=x accepts the Unix root password with all modules; Command Shell defaults to root. | Webmin 2.670 | REASONED |
| webmin-sudo: Installed sudo=1 lets sudo-permitted Unix users log in effectively as root. | Webmin 2.670 | REASONED |
| webmin-mfa: TOTP/Authy exists but is not configured at install; enable and enrol every user. | Webmin 2.670 | REASONED |
| webmin-advisories: Advisories list Basic-auth MFA bypasses CVE-2026-42210/CVE-2026-56022 under Webmin prior to 2.641; use a current release. | Webmin docs 8ceae26c5a074053905cbcc6c0053be573633f3a | REASONED |
| webmin-rate: Defaults blockhost_failures=5/blockhost_time=60 block a host for 60 seconds, not a user lockout; Basic-auth failures count only with installed passdelay=1. | Webmin 2.670 | REASONED |
| pve-bind: pveproxy HTTPS API 8006 and spiceproxy 3128 default IPv4/IPv6 wildcard; both share LISTEN_IP in /etc/default/pveproxy. | Proxmox VE 9.2 docs 9.2.12 | REASONED |
| pve-cluster: LISTEN_IP is not recommended on clusters needing peer pveproxy access; use ACLs/firewall. | Proxmox VE 9.2 docs 9.2.12 | REASONED |
| pve-acl: Default allow policy admits unmatched clients; ALLOW_FROM needs DENY_FROM=all or POLICY=deny, not both because deny policy rejects dual matches. | Proxmox VE 9.2 docs 9.2.12 | REASONED |
| pve-firewall: Firewall defaults disabled; enable and restrict 8006/22/3128 to management addresses. | Proxmox VE 9.2 docs 9.2.12 | REASONED |
| pve-root: root@pam can always log in as unconfined admin; installer sets the web-interface root password. | Proxmox VE 9.2 docs 9.2.12 | REASONED |
| pve-shell: Node shell opens /bin/login -f root without another password. | pve-manager 9.2.20 | REASONED |
| pve-mfa: Configure TOTP, WebAuthn, recovery keys or realm-enforced TOTP/YubiKey OTP; no default second factor. | Proxmox VE 9.2 docs 9.2.12 | REASONED |
| pve-lockout: Eight TOTP failures disable TOTP; 100 WebAuthn/recovery-key failures block all factors for an hour. These are second-factor lockouts. | Proxmox VE 9.2 docs 9.2.12 | REASONED |
| pve-password-delay: Unauthorized API responses delay three seconds; this is not password lockout. | Proxmox HTTP server 5119ff9bec08c69584c0c98bea3edd0098179e5f | REASONED |
| pve-certificates: Each cluster creates its own self-signed CA. | Proxmox VE 9.2 docs 9.2.12 | REASONED |
| pve-tokens: API tokens default to separated privileges and cannot access VM/node consoles. | Proxmox VE 9.2 docs 9.2.12 | REASONED |
| verify-cockpit: Inspect effective socket reset/address and root deny file; bare port or missing deny file exposes documented defaults. | Cockpit 368 | REASONED |
| verify-pve: Inspect LISTEN_IP/ACL policy, enabled/running firewall and management-only rules, and every admin's second factor including root@pam. | Proxmox VE 9.2 docs 9.2.12 | REASONED |
| verify-external: Probe each public IP with a reachable control; refusal/timeout is only consistent with isolation. TCP does not test Webmin UDP. | Cockpit 368; Webmin 2.670; Usermin 2.570; Proxmox VE 9.2 docs 9.2.12 | REASONED |
| webmin-loopback: Loopback bind with no listen line produced one TCP socket and no UDP. | Webmin 2.670 | DEMONSTRATED |
| webmin-rate-run: Fifth wrong password exceeded a five-second timeout; then even the right password received host-block 403. | Webmin 2.670 | DEMONSTRATED |
| verify-listeners: Expect management TCP binds and no discovery UDP; clustered Proxmox may retain wildcards with ACL/firewall protection. | Cockpit 368; Webmin 2.670; Usermin 2.570; Proxmox VE 9.2 docs 9.2.12 | REASONED |
| verify-webmin-parser: Thirty fixtures matched miniserv parsing and bind/sockets/discovery/ACL outputs; unreadable paths were not checked. File inspection is not running-state proof. | Webmin 2.670 | DEMONSTRATED |
| verify-tcp-loopback: Copied probe has recorded loopback provenance, not live panel-isolation evidence; loopback and mapped hex addresses pass its guard. | Cockpit 368; Webmin 2.670; Usermin 2.570; Proxmox VE 9.2 docs 9.2.12 | DEMONSTRATED |
<!-- version-basis:end -->

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
Those expected outcomes are REASONED from the cited vendor documentation and source.

On the host, list the listeners, TCP and UDP:

REASONED: following block; pinned Cockpit, Webmin/Usermin and Proxmox sources support this inventory. The recorded host lacks Cockpit systemd and Proxmox and forbids wildcard binds; exposed/fixed expectations follow.

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

DEMONSTRATED: following block; the parser matched Webmin 2.670 on thirty fixtures and printed the recorded outcomes below. This demonstrates file inspection, not running sockets or network isolation.

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

DEMONSTRATED: following block; recorded reuse of the low-code-builders.md loopback probe with these ports includes the mapped-address connection below. This is probe evidence only; live panel reachability and firewall isolation remain reasoned.

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
- Proxmox VE `pveproxy` (bind, `LISTEN_IP`, access lists) (Proxmox VE 9.2, pve-docs 9.2.12): https://git.proxmox.com/?p=pve-docs.git;a=blob_plain;hb=9370638116430c4b1ccb9707b5716eaad7c7c9d3;f=pveproxy.adoc
- Proxmox VE user management (root@pam, two-factor, lockout, API tokens): https://git.proxmox.com/?p=pve-docs.git;a=blob_plain;hb=9370638116430c4b1ccb9707b5716eaad7c7c9d3;f=pveum.adoc
- Proxmox VE firewall: https://git.proxmox.com/?p=pve-docs.git;a=blob_plain;hb=9370638116430c4b1ccb9707b5716eaad7c7c9d3;f=pve-firewall.adoc
- Proxmox VE certificates: https://git.proxmox.com/?p=pve-docs.git;a=blob_plain;hb=9370638116430c4b1ccb9707b5716eaad7c7c9d3;f=certificate-management.adoc
- Proxmox VE node shell (`/bin/login -f root`) (pve-manager 9.2.20): https://git.proxmox.com/?p=pve-manager.git;a=blob_plain;hb=49318c671b82f31e6b273b79447526161739b97a;f=PVE/API2/Nodes.pm
- Proxmox VE HTTP server (three-second delay on unauthorized responses): https://git.proxmox.com/?p=pve-http-server.git;a=blob_plain;hb=5119ff9bec08c69584c0c98bea3edd0098179e5f;f=src/PVE/APIServer/AnyEvent.pm
