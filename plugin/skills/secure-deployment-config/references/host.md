# Host baseline: SSH, firewall, updates

A host baseline is the hardening of a server: who can log in, which ports are open, and how it is patched. This guide helps your AI assistant apply it, including key-only SSH without root login, a default-deny inbound firewall, bans after repeated failed logins, and automatic security updates.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/host.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against OpenSSH documentation (no recorded version), OpenSSH 8.2 server manual V_8_2_P1, OpenSSH 8.1 server manual V_8_1_P1, OpenSSH 9.9 source V_9_9_P2, DNF 4.14.0, cloud-init 26.2 and 20.1, iproute2 ss manual v6.12.0, and BusyBox 1_36_1; 9 further sources are pinned to a commit and 9 carry no recorded version. Metadata reviewed 2026-10-18; documentation checked September 2026. The guide records 22 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

Every guide in this repository secures a service; this one secures the machine under them. Apply it once per host before exposing anything.

## 1. SSH: keys only, no root login

Add your public key to a **non-root** admin account's `~/.ssh/authorized_keys`, and from a fresh connection confirm that key login to that account works and that it can `sudo`, **before** disabling passwords or root login. Keep the current session open while testing changes, so a mistake is recoverable.

Put this in a drop-in that sorts first, `/etc/ssh/sshd_config.d/00-hardening.conf`, not only in the main `/etc/ssh/sshd_config`:

```
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
```

OpenSSH 9.9 documents that, unless noted otherwise, sshd uses the *first* value it reads for each keyword and processes `Include` wildcard matches in lexical order. The fetched Ubuntu focal OpenSSH 1:8.2p1-4 configuration and CentOS Stream 9 packaging place `Include /etc/ssh/sshd_config.d/*.conf` near the top, before main-file settings; OpenSSH 8.2 added `Include` to `sshd_config`. In cloud-init 26.2, `ssh_pwauth: true` sets `PasswordAuthentication yes` in `50-cloud-init.conf` when the main configuration includes that drop-in directory; cloud-init 20.1 instead updated the main file. Read before a later main-file line or a higher-numbered drop-in, that `yes` value wins and password login stays on. Name the hardening file `00-hardening.conf` so it is read first, and confirm with `sshd -T` (below) that the value took effect; as this guide's reasoning, an upgraded main file may lack the include or an earlier drop-in may already have set it. The fetched packaging does not establish current defaults for every Debian, Ubuntu and RHEL-family release, or how often cloud images contain this drop-in.

```bash
sudo sshd -t && sudo systemctl reload ssh    # sshd on RHEL-family systems
sudo sshd -T | grep -iE 'passwordauthentication|permitrootlogin|kbdinteractiveauthentication'
                                             # the EFFECTIVE global values after every include; confirm
                                             # they match what you set, not a drop-in read earlier. If you
                                             # use Match blocks, also check a connection with
                                             # `sudo sshd -T -C user=admin,addr=203.0.113.10`, since Match can override these
```

Add a second factor for SSH per [mfa.md](mfa.md): TOTP via [google-authenticator-libpam](https://github.com/google/google-authenticator-libpam) or push approval via Duo's `pam_duo`.

Both run through PAM's keyboard-interactive path, which the block above turns off. When adding PAM MFA, change the block to:

```
PasswordAuthentication no
KbdInteractiveAuthentication yes
UsePAM yes
AuthenticationMethods publickey,keyboard-interactive
PermitRootLogin no
PubkeyAuthentication yes
```

`AuthenticationMethods` with a comma-separated list requires every method in it, so a key alone is no longer enough. `PasswordAuthentication no` stays: the code prompt is keyboard-interactive, not password. Older sshd_config files spell `KbdInteractiveAuthentication` as `ChallengeResponseAuthentication`; set that one to `yes` where it is the one present.

## 2. Firewall: default deny inbound

```bash
# Debian/Ubuntu (ufw)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw delete allow OpenSSH                # only if an earlier run of this guide added it: a new rule does not replace an old one
sudo ufw allow proto tcp from REPLACE_WITH_ADMIN_RANGE to any port 22
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

SSH stays closed to the world here for the same reason rule 3 in [cloud-firewalls.md](cloud-firewalls.md) keeps it off the cloud firewall: `ufw allow OpenSSH` opens port 22 to every address on the internet. Restrict it to the range you administer from. AWS SSM Session Manager SSH uses the SSM Agent's outbound TLS connection to Session Manager endpoints and needs no inbound port on the managed node; allow outbound HTTPS 443 to the documented endpoints. A tailnet ordinarily needs no inbound internet firewall port for Tailscale, and Tailscale SSH accepts traffic from the tailnet on port 22 ([tailscale.md](tailscale.md)). GCP IAP TCP forwarding requires a cloud ingress allow from `35.235.240.0/20` (`2600:2d00:1:7::/64` for IPv6 VMs) to SSH's default port 22 or its configured port; where an NSG is applied to the target VM subnet, Azure Bastion requires an inbound SSH rule on default port 22 or a custom port with Standard or Premium SKU. Microsoft's best practice scopes that rule's source to the `AzureBastionSubnet` IP address range. As this guide's advice, check the effective host firewall rules for the broker paths; the fetched IAP, Bastion and Tailscale pages do not specify which UFW or firewalld rules, if any, are needed. See [cloud-firewalls.md](cloud-firewalls.md).

RHEL-family systems use firewalld (`firewall-cmd --permanent --add-service=https` and so on) with the same posture, and that includes SSH: `--add-service=ssh` opens port 22 to every address exactly as `ufw allow OpenSSH` does. Open only the ports the TLS-terminating layer needs; databases and app servers stay unreachable from outside per their guides. With Docker Engine's default Linux bridge firewall rules, published container traffic is diverted before ufw's rules; see [docker.md](docker.md) before relying on the firewall. As this guide's assessment, other modes and paths, including the userland proxy, need separate review in that guide.

```bash
# firewalld, where an earlier run enabled the ssh service: a rich rule does not supersede it.
# Every command below names the zone: without --zone they act on the default zone, which is not
# necessarily the one holding the internet-facing interface.
sudo firewall-cmd --get-active-zones            # find the zone your public interface is in
sudo firewall-cmd --permanent --zone=REPLACE_WITH_PUBLIC_ZONE --remove-service=ssh
sudo firewall-cmd --permanent --zone=REPLACE_WITH_PUBLIC_ZONE --add-rich-rule='rule family="ipv4" source address="REPLACE_WITH_ADMIN_RANGE" service name="ssh" accept'   # confirm your current address is inside REPLACE_WITH_ADMIN_RANGE first
sudo firewall-cmd --reload                      # --permanent writes the stored config only; nothing changes until this
sudo firewall-cmd --zone=REPLACE_WITH_PUBLIC_ZONE --list-all   # confirm nothing reaches 22 from an unauthorized source: no `ssh` (or other 22/tcp) service, no `22/tcp` or a port range covering 22, no protocol-wide or broad-source rule, the zone target is not ACCEPT, only the admin rich rule matches; check other applicable zones too
```

## 3. Brute-force protection and updates

- fail2ban ([github.com/fail2ban/fail2ban](https://github.com/fail2ban/fail2ban)) or CrowdSec ([crowdsec.net](https://www.crowdsec.net/)) bans repeated authentication failures against SSH and login panels.
- Automate security patches: `unattended-upgrades` on Debian/Ubuntu, `dnf-automatic` on RHEL-family systems. Configure them to install updates: on Ubuntu noble, the unattended-upgrades post-install script writes `20auto-upgrades` when `enable_auto_updates` is true, and `apt-daily-upgrade.timer` runs `apt.systemd.daily install`, which invokes `unattended-upgrade` when its periodic interval permits. Its Ubuntu allowed origins include the release and security pockets; inspect local origins and periodic settings. On CentOS Stream 9, `dnf-automatic` is a packaged subpackage. Upstream DNF 4.14.0 ships the cited `automatic.conf` defaults (`apply_updates = no` and `upgrade_type = default`) and timers; with that configuration the generic timer does not install updates. CentOS Stream 9 applies downstream dnf-automatic patches this guide has not reviewed, so its packaged defaults remain unestablished. Enable `dnf-automatic-install.timer` to install updates, and set `upgrade_type = security` when only advisory-backed security upgrades are intended. Package defaults on other Debian and RHEL-family releases remain unestablished.

## 4. Verify

REASONED: listener, firewall, SSH key-only and PAM MFA checks; no exposed/fixed run is recorded in this guide. Expectations follow the cited SSH, firewall, MFA, iproute2, netcat and BusyBox sources; this read-only review has no authorized target host or external probe machine.

```bash
sudo ss -4 -tulnp                 # IPv4 TCP and UDP listeners: only intended ones, on intended addresses
sudo ss -6 -tulnp                 # IPv6 TCP and UDP listeners: only intended ones, on intended addresses
sudo ufw status verbose           # default deny incoming; then `sudo ufw show raw` (status verbose omits rules loaded from /etc/ufw): every allowance that can reach 22 (a port-22 rule OR a broader "from <range> to any" allow) is scoped to your admin range, never Anywhere
(                                 # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
    *) nc -vz -w 3 "$1" 22 ;;   # from an address outside the admin range: must fail to connect
    # as this guide's assessment, a refusal or timeout only means THIS connection failed, not that the host firewall denied it (a host with
    # no sshd listening refuses too): confirm SSH works from an allowed source and read `ufw status`/`--list-all`
    # for the effective rule. A local error, an unsupported option (BusyBox small nc lacks -v; its 1.10-compatible applet lists it), or exit 1 with no
    # output at all is inconclusive as this guide's assessment; it does not establish a remote firewall result
  esac
)
# guard-conventions: allow probe of an illustrative user@host; no reader-substituted placeholder in this probe's argv
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no user@host   # keys-only: require immediate failure with NO password prompt AND a Permission denied (...) method list naming neither password nor keyboard-interactive. As this guide's reasoning, the client prints the server's remaining methods in that list; "Permission denied (publickey)" is expected when only publickey remains; a password prompt or a method list naming either method means that path is still on
# guard-conventions: allow probe of an illustrative user@host; no reader-substituted placeholder in this probe's argv
ssh user@host                     # with PAM MFA: the key is accepted, then a code is required before a shell. Also confirm a wrong or omitted code is REJECTED, that unenrolled users are denied (drop `nullok`), and that Duo fails closed (`failmode=secure`), per mfa.md; otherwise the factor is optional, not mandatory
```

REASONED: preceding block; listener and firewall inventory, disallowed-source SSH reachability, key-only login and PAM MFA comparisons follow the cited SSH, firewall, MFA, iproute2, netcat and BusyBox sources; no authorized target host or external probe machine is available, and no exposed/fixed result is recorded. Run the SSH test from a second terminal before closing your working session. The `nc -vz -w 3` form is sourced for Ubuntu noble netcat-openbsd; CentOS Stream 9 packages Ncat 7.92 as an `nc` alternative, but the fetched Ncat source is a later master commit, so this guide has not established the packaged version's option behaviour. Check the installed `nc` variant before treating this probe as evidence.

## Sources (checked September 2026)

- OpenSSH sshd_config manual: https://man.openbsd.org/sshd_config
- CentOS Stream 9 OpenSSH patch identifier, at 0b69a3828606595828fc3b878a7c70652303ad67 (checked October 2026): https://gitlab.com/redhat/centos-stream/rpms/openssh/-/blob/0b69a3828606595828fc3b878a7c70652303ad67/openssh.spec#L135-L135
- cloud-init 20.1 default sshd_config path, at 20.1 (checked October 2026): https://github.com/canonical/cloud-init/blob/20.1/cloudinit/ssh_util.py#L17-L18
- OpenSSH 8.1 adjacent server keyword entries, at V_8_1_P1 (checked October 2026): https://github.com/openssh/openssh-portable/blob/V_8_1_P1/sshd_config.5#L793-L804
- OpenSSH server Include entry, at V_8_2_P1 (checked October 2026): https://github.com/openssh/openssh-portable/blob/V_8_2_P1/sshd_config.5#L805-L817
- OpenSSH first-obtained-value rule, at V_9_9_P2 (checked October 2026): https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sshd_config.5#L51-L51
- OpenSSH lexical Include order, at V_9_9_P2 (checked October 2026): https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sshd_config.5#L912-L918
- Ubuntu focal stock sshd_config include, at 1b842ea8f368b6c7a913ae9e3f253107fb0aa1cc (checked October 2026): https://git.launchpad.net/ubuntu/+source/openssh/tree/sshd_config?id=1b842ea8f368b6c7a913ae9e3f253107fb0aa1cc#n13
- Ubuntu focal source version, at 1b842ea8f368b6c7a913ae9e3f253107fb0aa1cc (checked October 2026): https://git.launchpad.net/ubuntu/+source/openssh/tree/debian/changelog?id=1b842ea8f368b6c7a913ae9e3f253107fb0aa1cc#n1
- Ubuntu focal source changelog for drop-in packaging, at 1b842ea8f368b6c7a913ae9e3f253107fb0aa1cc (checked October 2026): https://git.launchpad.net/ubuntu/+source/openssh/tree/debian/changelog?id=1b842ea8f368b6c7a913ae9e3f253107fb0aa1cc#n4
- CentOS Stream 9 sshd_config include patch, at 0b69a3828606595828fc3b878a7c70652303ad67 (checked October 2026): https://gitlab.com/redhat/centos-stream/rpms/openssh/-/blob/0b69a3828606595828fc3b878a7c70652303ad67/openssh-7.7p1-redhat.patch#L69-L71
- CentOS Stream 9 OpenSSH patch application, at 0b69a3828606595828fc3b878a7c70652303ad67 (checked October 2026): https://gitlab.com/redhat/centos-stream/rpms/openssh/-/blob/0b69a3828606595828fc3b878a7c70652303ad67/openssh.spec#L444-L444
- cloud-init drop-in selection and writing, at 26.2 (checked October 2026): https://github.com/canonical/cloud-init/blob/26.2/cloudinit/ssh_util.py#L548-L586
- cloud-init ssh_pwauth value handling, at 26.2 (checked October 2026): https://github.com/canonical/cloud-init/blob/26.2/cloudinit/config/cc_set_passwords.py#L60-L90
- cloud-init ssh_pwauth call site, at 26.2 (checked October 2026): https://github.com/canonical/cloud-init/blob/26.2/cloudinit/config/cc_set_passwords.py#L255-L255
- cloud-init 20.1 main-file update, at 20.1 (checked October 2026): https://github.com/canonical/cloud-init/blob/20.1/cloudinit/ssh_util.py#L338-L348
- cloud-init 20.1 ssh_pwauth value handling, at 20.1 (checked October 2026): https://github.com/canonical/cloud-init/blob/20.1/cloudinit/config/cc_set_passwords.py#L97-L122
- cloud-init 20.1 ssh_pwauth call site, at 20.1 (checked October 2026): https://github.com/canonical/cloud-init/blob/20.1/cloudinit/config/cc_set_passwords.py#L230-L232
- Docker default Linux firewall integration, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/packet-filtering-firewalls.md#L11-L32
- Docker and ufw published-port behaviour, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/packet-filtering-firewalls.md#L90-L102
- AWS Session Manager SSH tunnel (rolling) (checked October 2026): https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-getting-started-enable-ssh-connections.html#session-manager-getting-started-enable-ssh-connections
- AWS Session Manager managed-node outbound HTTPS prerequisites (rolling) (checked October 2026): https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-prerequisites.html#session-manager-prerequisites
- Google Cloud IAP TCP forwarding firewall source and SSH port (rolling) (checked October 2026): https://docs.cloud.google.com/iap/docs/using-tcp-forwarding#create-firewall-rule
- Azure Bastion target VM subnet NSG rule, at 8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f (checked October 2026): https://github.com/MicrosoftDocs/azure-docs/blob/8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f/articles/bastion/bastion-nsg.md#L77-L84
- Tailscale firewall ports (rolling) (checked October 2026): https://tailscale.com/docs/reference/faq/firewall-ports
- Tailscale SSH tailnet port 22 (rolling) (checked October 2026): https://tailscale.com/docs/features/tailscale-ssh#why-it-matters
- ufw(8), for `default deny incoming`, `allow` and `status verbose`: https://manpages.ubuntu.com/manpages/noble/man8/ufw.8.html
- firewall-cmd(1), for `--permanent --add-service` and `--add-rich-rule`: https://firewalld.org/documentation/man-pages/firewall-cmd.html
- firewalld.richlanguage(5), for the `source address` / `service name` / `accept` rule form: https://firewalld.org/documentation/man-pages/firewalld.richlanguage.html
- fail2ban: https://github.com/fail2ban/fail2ban
- CrowdSec: https://www.crowdsec.net/
- google-authenticator-libpam: https://github.com/google/google-authenticator-libpam
- Duo Unix (`UsePAM`, `KbdInteractiveAuthentication`, `AuthenticationMethods publickey,keyboard-interactive`): https://duo.com/docs/duounix
- Ubuntu noble conditional automatic-update configuration, lines 47 to 58, at 0570be65234e2392d420308470d26920fa4cd21a (checked October 2026): https://git.launchpad.net/ubuntu/+source/unattended-upgrades/tree/debian/postinst?id=0570be65234e2392d420308470d26920fa4cd21a#n47
- Ubuntu noble allowed origins, lines 6 to 18, at 0570be65234e2392d420308470d26920fa4cd21a (checked October 2026): https://git.launchpad.net/ubuntu/+source/unattended-upgrades/tree/data/50unattended-upgrades.Ubuntu?id=0570be65234e2392d420308470d26920fa4cd21a#n6
- Ubuntu noble apt upgrade timer, lines 5 to 11, at 835f914ef5657b923fbb8b357f134b00de24c6fd (checked October 2026): https://git.launchpad.net/ubuntu/+source/apt/tree/debian/apt-daily-upgrade.timer?id=835f914ef5657b923fbb8b357f134b00de24c6fd#n5
- Ubuntu noble apt upgrade service, lines 7 to 12, at 835f914ef5657b923fbb8b357f134b00de24c6fd (checked October 2026): https://git.launchpad.net/ubuntu/+source/apt/tree/debian/apt-daily-upgrade.service?id=835f914ef5657b923fbb8b357f134b00de24c6fd#n7
- Ubuntu noble periodic unattended-upgrade invocation, lines 491 to 503, at 835f914ef5657b923fbb8b357f134b00de24c6fd (checked October 2026): https://git.launchpad.net/ubuntu/+source/apt/tree/debian/apt.systemd.daily?id=835f914ef5657b923fbb8b357f134b00de24c6fd#n491
- CentOS Stream 9 dnf-automatic subpackage, at 3d5ca2af8635e0ef77219625f734d503b9900208 (checked October 2026): https://gitlab.com/redhat/centos-stream/rpms/dnf/-/blob/3d5ca2af8635e0ef77219625f734d503b9900208/dnf.spec#L260-L267
- CentOS Stream 9 DNF package version, line 75, at 3d5ca2af8635e0ef77219625f734d503b9900208 (checked October 2026): https://gitlab.com/redhat/centos-stream/rpms/dnf/-/blob/3d5ca2af8635e0ef77219625f734d503b9900208/dnf.spec#L75-L75
- CentOS Stream 9 downstream DNF patch list, lines 82 to 158, at 3d5ca2af8635e0ef77219625f734d503b9900208 (checked October 2026): https://gitlab.com/redhat/centos-stream/rpms/dnf/-/blob/3d5ca2af8635e0ef77219625f734d503b9900208/dnf.spec#L82-L158
- CentOS Stream 9 downstream DNF patch application, lines 281 to 282, at 3d5ca2af8635e0ef77219625f734d503b9900208 (checked October 2026): https://gitlab.com/redhat/centos-stream/rpms/dnf/-/blob/3d5ca2af8635e0ef77219625f734d503b9900208/dnf.spec#L281-L282
- DNF 4.14.0 automatic configuration defaults, at 4.14.0 (checked October 2026): https://github.com/rpm-software-management/dnf/blob/4.14.0/etc/dnf/automatic.conf#L1-L22
- DNF 4.14.0 automatic timer behaviour, at 4.14.0 (checked October 2026): https://github.com/rpm-software-management/dnf/blob/4.14.0/doc/automatic.rst#L38-L50
- DNF 4.14.0 security upgrade type, at 4.14.0 (checked October 2026): https://github.com/rpm-software-management/dnf/blob/4.14.0/doc/automatic.rst#L86-L91
- DNF 4.14.0 automatic install timer, at 4.14.0 (checked October 2026): https://github.com/rpm-software-management/dnf/blob/4.14.0/etc/systemd/dnf-automatic-install.timer#L7-L13
- DNF 4.14.0 automatic install service, at 4.14.0 (checked October 2026): https://github.com/rpm-software-management/dnf/blob/4.14.0/etc/systemd/dnf-automatic-install.service#L7-L13
- iproute2 ss numeric output, at v6.12.0 (checked October 2026): https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L33-L34
- iproute2 ss listening sockets, at v6.12.0 (checked October 2026): https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L43-L44
- iproute2 ss process display, at v6.12.0 (checked October 2026): https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L162-L163
- iproute2 ss TCP sockets, at v6.12.0 (checked October 2026): https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L374-L375
- iproute2 ss UDP sockets, at v6.12.0 (checked October 2026): https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L377-L378
- iproute2 ss explicit IPv4 and IPv6 selection, at v6.12.0 (checked October 2026): https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L365-L369
- Ubuntu noble nc verbose flag, lines 257 to 258, at c047f1a4572e796c8643fb7e5a719a9d960a677b (checked October 2026): https://git.launchpad.net/ubuntu/+source/netcat-openbsd/tree/nc.1?id=c047f1a4572e796c8643fb7e5a719a9d960a677b#n257
- Ubuntu noble nc timeout flag, lines 263 to 266, at c047f1a4572e796c8643fb7e5a719a9d960a677b (checked October 2026): https://git.launchpad.net/ubuntu/+source/netcat-openbsd/tree/nc.1?id=c047f1a4572e796c8643fb7e5a719a9d960a677b#n263
- Ubuntu noble nc zero-I/O scan, lines 308 to 311, at c047f1a4572e796c8643fb7e5a719a9d960a677b (checked October 2026): https://git.launchpad.net/ubuntu/+source/netcat-openbsd/tree/nc.1?id=c047f1a4572e796c8643fb7e5a719a9d960a677b#n308
- Ubuntu noble nc connection and exit path, lines 899 to 953, at c047f1a4572e796c8643fb7e5a719a9d960a677b (checked October 2026): https://git.launchpad.net/ubuntu/+source/netcat-openbsd/tree/netcat.c?id=c047f1a4572e796c8643fb7e5a719a9d960a677b#n899
- CentOS Stream 9 ncat nc alternative, at 17c2b7795d821cd7fbe311cf3f885be3ea1f122f (checked October 2026): https://gitlab.com/redhat/centos-stream/rpms/nmap/-/blob/17c2b7795d821cd7fbe311cf3f885be3ea1f122f/nmap.spec#L133-L137
- OpenSSH 9.9 client PreferredAuthentications, at V_9_9_P2 (checked October 2026): https://github.com/openssh/openssh-portable/blob/V_9_9_P2/ssh_config.5#L1536-L1546
- OpenSSH 9.9 client PubkeyAuthentication, at V_9_9_P2 (checked October 2026): https://github.com/openssh/openssh-portable/blob/V_9_9_P2/ssh_config.5#L1661-L1674
- OpenSSH 9.9 client authentication failure message and method list, at V_9_9_P2 (checked October 2026): https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sshconnect2.c#L540-L543
- BusyBox 1.36.1 small nc option parser, at 1_36_1 (checked October 2026): https://github.com/mirror/busybox/blob/1_36_1/networking/nc.c#L136-L170
- BusyBox 1.36.1 compatible nc options, at 1_36_1 (checked October 2026): https://github.com/mirror/busybox/blob/1_36_1/networking/nc_bloaty.c#L61-L93
- BusyBox 1.36.1 nc compatibility build selection, at 1_36_1 (checked October 2026): https://github.com/mirror/busybox/blob/1_36_1/networking/nc.c#L30-L59
- CentOS Stream 9 nmap package version, at 17c2b7795d821cd7fbe311cf3f885be3ea1f122f (checked October 2026): https://gitlab.com/redhat/centos-stream/rpms/nmap/-/blob/17c2b7795d821cd7fbe311cf3f885be3ea1f122f/nmap.spec#L6-L8


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- ssh: OpenSSH documentation (unknown)
- openssh82: OpenSSH 8.2 server manual (V_8_2_P1)
- openssh81: OpenSSH 8.1 server manual (V_8_1_P1)
- openssh99: OpenSSH 9.9 source (V_9_9_P2)
- ubuntu-focal: Ubuntu focal OpenSSH source (1b842ea8f368b6c7a913ae9e3f253107fb0aa1cc)
- rhel-c9s: CentOS Stream 9 OpenSSH packaging (0b69a3828606595828fc3b878a7c70652303ad67)
- ufw: UFW documentation (unknown)
- firewalld: firewalld documentation (unknown)
- ubuntu-uu: Ubuntu noble unattended-upgrades source (0570be65234e2392d420308470d26920fa4cd21a)
- ubuntu-apt: Ubuntu noble-updates apt source (835f914ef5657b923fbb8b357f134b00de24c6fd)
- c9s-dnf: CentOS Stream 9 dnf packaging (3d5ca2af8635e0ef77219625f734d503b9900208)
- dnf4: DNF (4.14.0)
- aws-ssm: AWS Session Manager (unknown)
- gcp-iap: Google Cloud IAP (unknown)
- azure-docs: Azure documentation snapshot (8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f)
- tailscale-docs: Tailscale documentation (unknown)
- fail2ban: fail2ban (unknown)
- crowdsec: CrowdSec (unknown)
- totp: google-authenticator-libpam (unknown)
- duo: Duo Unix (unknown)
- cloudinit26: cloud-init (26.2)
- cloudinit20: cloud-init (20.1)
- docker: Docker Engine networking (4e9a5751518ed8223a8dcde53693badddd72604f)
- iproute2: iproute2 ss manual (v6.12.0)
- ubuntu-nc: Ubuntu noble netcat-openbsd source (c047f1a4572e796c8643fb7e5a719a9d960a677b)
- c9s-nmap: CentOS Stream 9 nmap packaging (17c2b7795d821cd7fbe311cf3f885be3ea1f122f)
- busybox: BusyBox (1_36_1)

Claims (full source mapping in the JSON block below):

- safe-transition (REASONED; ssh): Confirm non-root key login and sudo in a fresh session before disabling password/root access; retain the working session while testing.
- keys-only (REASONED; ssh): Disable PasswordAuthentication and KbdInteractiveAuthentication; enable PubkeyAuthentication and prohibit root login.
- include-order (REASONED; ssh, openssh81, openssh82, openssh99, ubuntu-focal, rhel-c9s, cloudinit26, cloudinit20): OpenSSH 8.2 added server Include; OpenSSH 9.9 documents that, unless noted otherwise, each keyword uses its first obtained value, and documents lexical wildcard order supporting 00-hardening.conf. The fetched Ubuntu focal OpenSSH 1:8.2p1-4 configuration and CentOS Stream 9 packaging place the drop-in Include near the top, before main-file settings. With ssh_pwauth: true, cloud-init 26.2 writes PasswordAuthentication yes to 50-cloud-init.conf when the main configuration includes that directory; cloud-init 20.1 instead updated the main file. Current distribution defaults and cloud-image prevalence remain unestablished.
- effective-config (REASONED; ssh): Validate with sshd -t before reload; inspect sshd -T global values and -T -C for Match-specific settings. Service names differ by distribution.
- totp (REASONED; ssh, totp): SSH TOTP uses google-authenticator-libpam through PAM keyboard-interactive; keys-only configuration must change before adding this factor.
- duo (REASONED; ssh, duo): Duo pam_duo provides the alternative push factor through PAM keyboard-interactive.
- mfa-methods (REASONED; ssh, duo): UsePAM yes and AuthenticationMethods publickey,keyboard-interactive require both methods; keep password/root login disabled and public keys enabled.
- legacy-name (REASONED; ssh, duo): Older configurations use ChallengeResponseAuthentication for KbdInteractiveAuthentication; enable the spelling present when configuring PAM MFA.
- ufw-default (REASONED; ufw): Set deny incoming and allow outgoing, then enable UFW; permit TCP 80 and 443 for the TLS layer.
- ufw-ssh (REASONED; ufw): Remove any broad OpenSSH allow before adding an admin-source TCP 22 rule; adding a narrower rule does not replace the old allowance.
- brokered-ssh (REASONED; ufw, aws-ssm, gcp-iap, azure-docs, tailscale-docs): SSM SSH uses the agent's outbound TLS connection and needs no inbound port on the managed node; allow outbound HTTPS 443 to the documented Systems Manager endpoints. A tailnet ordinarily needs no inbound internet firewall port, and Tailscale SSH accepts tailnet traffic on port 22. IAP requires cloud ingress from 35.235.240.0/20, or 2600:2d00:1:7::/64 for IPv6 VMs, to SSH's default port 22 or its configured port; where an NSG is applied to the target VM subnet, Bastion requires an inbound SSH rule on default port 22 or a custom port with Standard or Premium SKU. Microsoft's best practice scopes that rule's source to the AzureBastionSubnet IP range. As this guide's advice, check the host firewall for these broker paths; the fetched IAP, Bastion and Tailscale pages do not specify which UFW or firewalld rules, if any, are needed.
- firewalld-zone (REASONED; firewalld): Find the public interface zone explicitly; remove its broad ssh service, add the IPv4 admin rich rule permanently, then reload to activate it.
- firewalld-audit (REASONED; firewalld): Inspect applicable zones for other services, port ranges, protocol/source allowances or ACCEPT targets that reopen 22; the narrow rich rule does not supersede them.
- docker-bypass (REASONED; ufw, docker): With Docker Engine default Linux bridge firewall rules, published container traffic is diverted before UFW settings; consult docker.md before relying on the host firewall. As this guide's assessment, other modes and paths, including the userland proxy, need separate review in that guide.
- fail2ban (REASONED; fail2ban): Use fail2ban to ban repeated authentication failures against SSH/login services.
- crowdsec (REASONED; crowdsec): CrowdSec is the alternative protection for repeated authentication failures.
- updates (REASONED; ssh, ubuntu-uu, ubuntu-apt, c9s-dnf, dnf4): Automate security patches with unattended-upgrades on Debian/Ubuntu or dnf-automatic on RHEL-family systems, configured to install them. Ubuntu noble's postinst conditionally writes 20auto-upgrades, and apt-daily-upgrade invokes unattended-upgrade when its periodic interval permits; its allowed origins include the release and security pockets. CentOS Stream 9 packages dnf-automatic. Upstream DNF 4.14.0 ships the cited automatic.conf defaults apply_updates=no and upgrade_type=default and the cited timers; enable dnf-automatic-install.timer and select upgrade_type=security for security-only installation. CentOS Stream 9 applies downstream dnf-automatic patches this guide has not reviewed, so its packaged defaults remain unestablished. Other Debian and RHEL-family package defaults remain unestablished.
- verify-listeners (REASONED; ufw, iproute2, ubuntu-nc, c9s-nmap, busybox, openssh99): Inventory intended TCP/UDP listeners and addresses in both IP families with explicit ss -4 and -6 runs. Ubuntu noble netcat-openbsd supports -v, -z and -w; CentOS Stream 9 packages Ncat as an nc alternative, but behaviour of packaged 7.92 remains unestablished. BusyBox 1.36.1 small nc lacks -v while its 1.10-compatible applet lists -v. As this guide's assessment, refusal or timeout proves only that this connection failed; local errors, unsupported options and exit 1 without output are inconclusive. The OpenSSH 9.9 client options select password and disable public key; the literal Permission denied (publickey) is this guide's reasoned expectation dependent on server-advertised methods, while immediate failure with NO password prompt and a Permission denied (...) method list naming neither password nor keyboard-interactive are required. As this guide's reasoning, the client prints the server's remaining methods in that list.
- verify-firewall (REASONED; ufw): UFW status should show default-deny ingress and admin-scoped SSH allowances; also inspect show raw because status omits /etc/ufw rules.
- verify-external (REASONED; ufw, firewalld): Disallowed-source TCP 22 must fail while allowed SSH works; correlate effective rules. As this guide's assessment, refusal alone, local errors and unsupported netcat options are inconclusive.
- verify-password (REASONED; ssh, openssh99): A password-only SSH attempt must fail immediately without a password prompt and show a Permission denied (...) method list naming neither password nor keyboard-interactive. As this guide's reasoning, the client prints the server's remaining methods in that list; a prompt or a list naming either method means that path is still on.
- verify-mfa (REASONED; ssh, totp, duo): After key acceptance require a code, reject wrong/omitted codes and unenrolled users without nullok, and use Duo failmode=secure; test before closing the working session.

````json
{
  "schema": 1,
  "checked": "2026-10-18",
  "documentation_checked": "2026-09",
  "body_sha256": "140e5bbbf557bda32e09d1ae1270b599f1b7eb98bc38f954e6201a34b5d6b5a9",
  "components": {
    "ssh": {
      "name": "OpenSSH documentation",
      "basis": "unknown",
      "sources": {
        "s44f73ffcb41e": "https://man.openbsd.org/sshd_config"
      }
    },
    "openssh82": {
      "name": "OpenSSH 8.2 server manual",
      "basis": "V_8_2_P1",
      "sources": {
        "s74206a9a30dd": "https://github.com/openssh/openssh-portable/blob/V_8_2_P1/sshd_config.5#L805-L817"
      }
    },
    "openssh81": {
      "name": "OpenSSH 8.1 server manual",
      "basis": "V_8_1_P1",
      "sources": {
        "s76bfb1ff5934": "https://github.com/openssh/openssh-portable/blob/V_8_1_P1/sshd_config.5#L793-L804"
      }
    },
    "openssh99": {
      "name": "OpenSSH 9.9 source",
      "basis": "V_9_9_P2",
      "sources": {
        "sb409a9bcefc5": "https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sshd_config.5#L51-L51",
        "s447d8f1b88bd": "https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sshd_config.5#L912-L918",
        "saa71f4024a44": "https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sshconnect2.c#L540-L543",
        "sd768a096f236": "https://github.com/openssh/openssh-portable/blob/V_9_9_P2/ssh_config.5#L1536-L1546",
        "s711f7f9ad562": "https://github.com/openssh/openssh-portable/blob/V_9_9_P2/ssh_config.5#L1661-L1674"
      }
    },
    "ubuntu-focal": {
      "name": "Ubuntu focal OpenSSH source",
      "basis": "1b842ea8f368b6c7a913ae9e3f253107fb0aa1cc",
      "sources": {
        "sbc9404fbd678": "https://git.launchpad.net/ubuntu/+source/openssh/tree/sshd_config?id=1b842ea8f368b6c7a913ae9e3f253107fb0aa1cc#n13",
        "s8681449a40db": "https://git.launchpad.net/ubuntu/+source/openssh/tree/debian/changelog?id=1b842ea8f368b6c7a913ae9e3f253107fb0aa1cc#n1",
        "sc389a883f3ae": "https://git.launchpad.net/ubuntu/+source/openssh/tree/debian/changelog?id=1b842ea8f368b6c7a913ae9e3f253107fb0aa1cc#n4"
      }
    },
    "rhel-c9s": {
      "name": "CentOS Stream 9 OpenSSH packaging",
      "basis": "0b69a3828606595828fc3b878a7c70652303ad67",
      "sources": {
        "sd34862bbf569": "https://gitlab.com/redhat/centos-stream/rpms/openssh/-/blob/0b69a3828606595828fc3b878a7c70652303ad67/openssh-7.7p1-redhat.patch#L69-L71",
        "s87a3827a045e": "https://gitlab.com/redhat/centos-stream/rpms/openssh/-/blob/0b69a3828606595828fc3b878a7c70652303ad67/openssh.spec#L444-L444",
        "s0a2ed08d7a83": "https://gitlab.com/redhat/centos-stream/rpms/openssh/-/blob/0b69a3828606595828fc3b878a7c70652303ad67/openssh.spec#L135-L135"
      }
    },
    "ufw": {
      "name": "UFW documentation",
      "basis": "unknown",
      "sources": {
        "scff3a017f30b": "https://manpages.ubuntu.com/manpages/noble/man8/ufw.8.html"
      }
    },
    "firewalld": {
      "name": "firewalld documentation",
      "basis": "unknown",
      "sources": {
        "sa1a1385129f1": "https://firewalld.org/documentation/man-pages/firewall-cmd.html",
        "sc1cb4d135f3b": "https://firewalld.org/documentation/man-pages/firewalld.richlanguage.html"
      }
    },
    "ubuntu-uu": {
      "name": "Ubuntu noble unattended-upgrades source",
      "basis": "0570be65234e2392d420308470d26920fa4cd21a",
      "sources": {
        "sf087d7bd33d0": "https://git.launchpad.net/ubuntu/+source/unattended-upgrades/tree/debian/postinst?id=0570be65234e2392d420308470d26920fa4cd21a#n47",
        "s665816188e55": "https://git.launchpad.net/ubuntu/+source/unattended-upgrades/tree/data/50unattended-upgrades.Ubuntu?id=0570be65234e2392d420308470d26920fa4cd21a#n6"
      }
    },
    "ubuntu-apt": {
      "name": "Ubuntu noble-updates apt source",
      "basis": "835f914ef5657b923fbb8b357f134b00de24c6fd",
      "sources": {
        "sca779f690beb": "https://git.launchpad.net/ubuntu/+source/apt/tree/debian/apt-daily-upgrade.timer?id=835f914ef5657b923fbb8b357f134b00de24c6fd#n5",
        "sfd64eba4bd67": "https://git.launchpad.net/ubuntu/+source/apt/tree/debian/apt-daily-upgrade.service?id=835f914ef5657b923fbb8b357f134b00de24c6fd#n7",
        "s11bc9e19894d": "https://git.launchpad.net/ubuntu/+source/apt/tree/debian/apt.systemd.daily?id=835f914ef5657b923fbb8b357f134b00de24c6fd#n491"
      }
    },
    "c9s-dnf": {
      "name": "CentOS Stream 9 dnf packaging",
      "basis": "3d5ca2af8635e0ef77219625f734d503b9900208",
      "sources": {
        "s9b090e2053b2": "https://gitlab.com/redhat/centos-stream/rpms/dnf/-/blob/3d5ca2af8635e0ef77219625f734d503b9900208/dnf.spec#L260-L267",
        "s32a269377ebb": "https://gitlab.com/redhat/centos-stream/rpms/dnf/-/blob/3d5ca2af8635e0ef77219625f734d503b9900208/dnf.spec#L75-L75",
        "s006862fe84d1": "https://gitlab.com/redhat/centos-stream/rpms/dnf/-/blob/3d5ca2af8635e0ef77219625f734d503b9900208/dnf.spec#L82-L158",
        "s50216e5989bf": "https://gitlab.com/redhat/centos-stream/rpms/dnf/-/blob/3d5ca2af8635e0ef77219625f734d503b9900208/dnf.spec#L281-L282"
      }
    },
    "dnf4": {
      "name": "DNF",
      "basis": "4.14.0",
      "sources": {
        "s97934a4740a2": "https://github.com/rpm-software-management/dnf/blob/4.14.0/etc/dnf/automatic.conf#L1-L22",
        "sbd65ffa4b83c": "https://github.com/rpm-software-management/dnf/blob/4.14.0/doc/automatic.rst#L38-L50",
        "s5619c2b76401": "https://github.com/rpm-software-management/dnf/blob/4.14.0/doc/automatic.rst#L86-L91",
        "sb4ab6d87f528": "https://github.com/rpm-software-management/dnf/blob/4.14.0/etc/systemd/dnf-automatic-install.timer#L7-L13",
        "s189a68fdfaad": "https://github.com/rpm-software-management/dnf/blob/4.14.0/etc/systemd/dnf-automatic-install.service#L7-L13"
      }
    },
    "aws-ssm": {
      "name": "AWS Session Manager",
      "basis": "unknown",
      "sources": {
        "s06a2a8e07062": "https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-getting-started-enable-ssh-connections.html#session-manager-getting-started-enable-ssh-connections",
        "s0f77b30546ee": "https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-prerequisites.html#session-manager-prerequisites"
      }
    },
    "gcp-iap": {
      "name": "Google Cloud IAP",
      "basis": "unknown",
      "sources": {
        "s7e6eda97f950": "https://docs.cloud.google.com/iap/docs/using-tcp-forwarding#create-firewall-rule"
      }
    },
    "azure-docs": {
      "name": "Azure documentation snapshot",
      "basis": "8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f",
      "sources": {
        "s6d46120d991b": "https://github.com/MicrosoftDocs/azure-docs/blob/8ef1ae8a3759ddb2ed2e437bf38083aa2268c39f/articles/bastion/bastion-nsg.md#L77-L84"
      }
    },
    "tailscale-docs": {
      "name": "Tailscale documentation",
      "basis": "unknown",
      "sources": {
        "scf48029376f6": "https://tailscale.com/docs/reference/faq/firewall-ports",
        "s44f0b2a0a8ba": "https://tailscale.com/docs/features/tailscale-ssh#why-it-matters"
      }
    },
    "fail2ban": {
      "name": "fail2ban",
      "basis": "unknown",
      "sources": {
        "s7a37ae416e85": "https://github.com/fail2ban/fail2ban"
      }
    },
    "crowdsec": {
      "name": "CrowdSec",
      "basis": "unknown",
      "sources": {
        "s4efe4c22c69b": "https://www.crowdsec.net/"
      }
    },
    "totp": {
      "name": "google-authenticator-libpam",
      "basis": "unknown",
      "sources": {
        "s6f787f7b4f18": "https://github.com/google/google-authenticator-libpam"
      }
    },
    "duo": {
      "name": "Duo Unix",
      "basis": "unknown",
      "sources": {
        "s18b76ce18df1": "https://duo.com/docs/duounix"
      }
    },
    "cloudinit26": {
      "name": "cloud-init",
      "basis": "26.2",
      "sources": {
        "sad4ec0d2acc5": "https://github.com/canonical/cloud-init/blob/26.2/cloudinit/ssh_util.py#L548-L586",
        "s8de0318d9aa5": "https://github.com/canonical/cloud-init/blob/26.2/cloudinit/config/cc_set_passwords.py#L60-L90",
        "s368c8162762a": "https://github.com/canonical/cloud-init/blob/26.2/cloudinit/config/cc_set_passwords.py#L255-L255"
      }
    },
    "cloudinit20": {
      "name": "cloud-init",
      "basis": "20.1",
      "sources": {
        "s471abb6d2123": "https://github.com/canonical/cloud-init/blob/20.1/cloudinit/ssh_util.py#L338-L348",
        "sa8d2f85a5876": "https://github.com/canonical/cloud-init/blob/20.1/cloudinit/ssh_util.py#L17-L18",
        "s872ab5dff723": "https://github.com/canonical/cloud-init/blob/20.1/cloudinit/config/cc_set_passwords.py#L97-L122",
        "s7e40e982cb9f": "https://github.com/canonical/cloud-init/blob/20.1/cloudinit/config/cc_set_passwords.py#L230-L232"
      }
    },
    "docker": {
      "name": "Docker Engine networking",
      "basis": "4e9a5751518ed8223a8dcde53693badddd72604f",
      "sources": {
        "sc920c6946fcf": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/packet-filtering-firewalls.md#L11-L32",
        "sb5ca9f87b1f3": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/network/packet-filtering-firewalls.md#L90-L102"
      }
    },
    "iproute2": {
      "name": "iproute2 ss manual",
      "basis": "v6.12.0",
      "sources": {
        "s2afc4764d5bb": "https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L33-L34",
        "sfaa932c2ca13": "https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L43-L44",
        "sd295f82d643f": "https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L162-L163",
        "s65278ee45850": "https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L374-L375",
        "s8ecdaf9e9ea7": "https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L377-L378",
        "s4e1c28d5adad": "https://github.com/iproute2/iproute2/blob/v6.12.0/man/man8/ss.8#L365-L369"
      }
    },
    "ubuntu-nc": {
      "name": "Ubuntu noble netcat-openbsd source",
      "basis": "c047f1a4572e796c8643fb7e5a719a9d960a677b",
      "sources": {
        "s478aaf9a8975": "https://git.launchpad.net/ubuntu/+source/netcat-openbsd/tree/nc.1?id=c047f1a4572e796c8643fb7e5a719a9d960a677b#n257",
        "sd7b31d3bc579": "https://git.launchpad.net/ubuntu/+source/netcat-openbsd/tree/nc.1?id=c047f1a4572e796c8643fb7e5a719a9d960a677b#n263",
        "scc48da80246b": "https://git.launchpad.net/ubuntu/+source/netcat-openbsd/tree/nc.1?id=c047f1a4572e796c8643fb7e5a719a9d960a677b#n308",
        "s5e260ceab82c": "https://git.launchpad.net/ubuntu/+source/netcat-openbsd/tree/netcat.c?id=c047f1a4572e796c8643fb7e5a719a9d960a677b#n899"
      }
    },
    "c9s-nmap": {
      "name": "CentOS Stream 9 nmap packaging",
      "basis": "17c2b7795d821cd7fbe311cf3f885be3ea1f122f",
      "sources": {
        "sd06e83963e39": "https://gitlab.com/redhat/centos-stream/rpms/nmap/-/blob/17c2b7795d821cd7fbe311cf3f885be3ea1f122f/nmap.spec#L133-L137",
        "s3ab25d24e37a": "https://gitlab.com/redhat/centos-stream/rpms/nmap/-/blob/17c2b7795d821cd7fbe311cf3f885be3ea1f122f/nmap.spec#L6-L8"
      }
    },
    "busybox": {
      "name": "BusyBox",
      "basis": "1_36_1",
      "sources": {
        "s34bdee292f79": "https://github.com/mirror/busybox/blob/1_36_1/networking/nc_bloaty.c#L61-L93",
        "sd707e18625cc": "https://github.com/mirror/busybox/blob/1_36_1/networking/nc.c#L136-L170",
        "s14b89daa008d": "https://github.com/mirror/busybox/blob/1_36_1/networking/nc.c#L30-L59"
      }
    }
  },
  "claims": {
    "safe-transition": {"text": "Confirm non-root key login and sudo in a fresh session before disabling password/root access; retain the working session while testing.", "components": ["ssh"], "sources": ["ssh:s44f73ffcb41e"], "status": "REASONED"},
    "keys-only": {"text": "Disable PasswordAuthentication and KbdInteractiveAuthentication; enable PubkeyAuthentication and prohibit root login.", "components": ["ssh"], "sources": ["ssh:s44f73ffcb41e"], "status": "REASONED"},
    "include-order": {"text": "OpenSSH 8.2 added server Include; OpenSSH 9.9 documents that, unless noted otherwise, each keyword uses its first obtained value, and documents lexical wildcard order supporting 00-hardening.conf. The fetched Ubuntu focal OpenSSH 1:8.2p1-4 configuration and CentOS Stream 9 packaging place the drop-in Include near the top, before main-file settings. With ssh_pwauth: true, cloud-init 26.2 writes PasswordAuthentication yes to 50-cloud-init.conf when the main configuration includes that directory; cloud-init 20.1 instead updated the main file. Current distribution defaults and cloud-image prevalence remain unestablished.", "components": ["ssh", "openssh81", "openssh82", "openssh99", "ubuntu-focal", "rhel-c9s", "cloudinit26", "cloudinit20"], "sources": ["ssh:s44f73ffcb41e", "openssh82:s74206a9a30dd", "openssh99:sb409a9bcefc5", "openssh99:s447d8f1b88bd", "ubuntu-focal:sbc9404fbd678", "ubuntu-focal:s8681449a40db", "rhel-c9s:sd34862bbf569", "rhel-c9s:s87a3827a045e", "cloudinit26:sad4ec0d2acc5", "cloudinit26:s8de0318d9aa5", "cloudinit20:s471abb6d2123", "cloudinit20:sa8d2f85a5876", "rhel-c9s:s0a2ed08d7a83", "openssh81:s76bfb1ff5934", "ubuntu-focal:sc389a883f3ae", "cloudinit26:s368c8162762a", "cloudinit20:s872ab5dff723", "cloudinit20:s7e40e982cb9f"], "status": "REASONED"},
    "effective-config": {"text": "Validate with sshd -t before reload; inspect sshd -T global values and -T -C for Match-specific settings. Service names differ by distribution.", "components": ["ssh"], "sources": ["ssh:s44f73ffcb41e"], "status": "REASONED"},
    "totp": {"text": "SSH TOTP uses google-authenticator-libpam through PAM keyboard-interactive; keys-only configuration must change before adding this factor.", "components": ["ssh", "totp"], "sources": ["ssh:s44f73ffcb41e", "totp:s6f787f7b4f18"], "status": "REASONED"},
    "duo": {"text": "Duo pam_duo provides the alternative push factor through PAM keyboard-interactive.", "components": ["ssh", "duo"], "sources": ["ssh:s44f73ffcb41e", "duo:s18b76ce18df1"], "status": "REASONED"},
    "mfa-methods": {"text": "UsePAM yes and AuthenticationMethods publickey,keyboard-interactive require both methods; keep password/root login disabled and public keys enabled.", "components": ["ssh", "duo"], "sources": ["ssh:s44f73ffcb41e", "duo:s18b76ce18df1"], "status": "REASONED"},
    "legacy-name": {"text": "Older configurations use ChallengeResponseAuthentication for KbdInteractiveAuthentication; enable the spelling present when configuring PAM MFA.", "components": ["ssh", "duo"], "sources": ["ssh:s44f73ffcb41e", "duo:s18b76ce18df1"], "status": "REASONED"},
    "ufw-default": {"text": "Set deny incoming and allow outgoing, then enable UFW; permit TCP 80 and 443 for the TLS layer.", "components": ["ufw"], "sources": ["ufw:scff3a017f30b"], "status": "REASONED"},
    "ufw-ssh": {"text": "Remove any broad OpenSSH allow before adding an admin-source TCP 22 rule; adding a narrower rule does not replace the old allowance.", "components": ["ufw"], "sources": ["ufw:scff3a017f30b"], "status": "REASONED"},
    "brokered-ssh": {"text": "SSM SSH uses the agent's outbound TLS connection and needs no inbound port on the managed node; allow outbound HTTPS 443 to the documented Systems Manager endpoints. A tailnet ordinarily needs no inbound internet firewall port, and Tailscale SSH accepts tailnet traffic on port 22. IAP requires cloud ingress from 35.235.240.0/20, or 2600:2d00:1:7::/64 for IPv6 VMs, to SSH's default port 22 or its configured port; where an NSG is applied to the target VM subnet, Bastion requires an inbound SSH rule on default port 22 or a custom port with Standard or Premium SKU. Microsoft's best practice scopes that rule's source to the AzureBastionSubnet IP range. As this guide's advice, check the host firewall for these broker paths; the fetched IAP, Bastion and Tailscale pages do not specify which UFW or firewalld rules, if any, are needed.", "components": ["ufw", "aws-ssm", "gcp-iap", "azure-docs", "tailscale-docs"], "sources": ["ufw:scff3a017f30b", "aws-ssm:s06a2a8e07062", "aws-ssm:s0f77b30546ee", "gcp-iap:s7e6eda97f950", "azure-docs:s6d46120d991b", "tailscale-docs:scf48029376f6", "tailscale-docs:s44f0b2a0a8ba"], "status": "REASONED"},
    "firewalld-zone": {"text": "Find the public interface zone explicitly; remove its broad ssh service, add the IPv4 admin rich rule permanently, then reload to activate it.", "components": ["firewalld"], "sources": ["firewalld:sa1a1385129f1", "firewalld:sc1cb4d135f3b"], "status": "REASONED"},
    "firewalld-audit": {"text": "Inspect applicable zones for other services, port ranges, protocol/source allowances or ACCEPT targets that reopen 22; the narrow rich rule does not supersede them.", "components": ["firewalld"], "sources": ["firewalld:sa1a1385129f1", "firewalld:sc1cb4d135f3b"], "status": "REASONED"},
    "docker-bypass": {"text": "With Docker Engine default Linux bridge firewall rules, published container traffic is diverted before UFW settings; consult docker.md before relying on the host firewall. As this guide's assessment, other modes and paths, including the userland proxy, need separate review in that guide.", "components": ["ufw", "docker"], "sources": ["ufw:scff3a017f30b", "docker:sc920c6946fcf", "docker:sb5ca9f87b1f3"], "status": "REASONED"},
    "fail2ban": {"text": "Use fail2ban to ban repeated authentication failures against SSH/login services.", "components": ["fail2ban"], "sources": ["fail2ban:s7a37ae416e85"], "status": "REASONED"},
    "crowdsec": {"text": "CrowdSec is the alternative protection for repeated authentication failures.", "components": ["crowdsec"], "sources": ["crowdsec:s4efe4c22c69b"], "status": "REASONED"},
    "updates": {"text": "Automate security patches with unattended-upgrades on Debian/Ubuntu or dnf-automatic on RHEL-family systems, configured to install them. Ubuntu noble's postinst conditionally writes 20auto-upgrades, and apt-daily-upgrade invokes unattended-upgrade when its periodic interval permits; its allowed origins include the release and security pockets. CentOS Stream 9 packages dnf-automatic. Upstream DNF 4.14.0 ships the cited automatic.conf defaults apply_updates=no and upgrade_type=default and the cited timers; enable dnf-automatic-install.timer and select upgrade_type=security for security-only installation. CentOS Stream 9 applies downstream dnf-automatic patches this guide has not reviewed, so its packaged defaults remain unestablished. Other Debian and RHEL-family package defaults remain unestablished.", "components": ["ssh", "ubuntu-uu", "ubuntu-apt", "c9s-dnf", "dnf4"], "sources": ["ssh:s44f73ffcb41e", "ubuntu-uu:sf087d7bd33d0", "ubuntu-uu:s665816188e55", "ubuntu-apt:sca779f690beb", "ubuntu-apt:sfd64eba4bd67", "ubuntu-apt:s11bc9e19894d", "c9s-dnf:s9b090e2053b2", "c9s-dnf:s32a269377ebb", "c9s-dnf:s006862fe84d1", "c9s-dnf:s50216e5989bf", "dnf4:s97934a4740a2", "dnf4:sbd65ffa4b83c", "dnf4:s5619c2b76401", "dnf4:sb4ab6d87f528", "dnf4:s189a68fdfaad"], "status": "REASONED"},
    "verify-listeners": {"text": "Inventory intended TCP/UDP listeners and addresses in both IP families with explicit ss -4 and -6 runs. Ubuntu noble netcat-openbsd supports -v, -z and -w; CentOS Stream 9 packages Ncat as an nc alternative, but behaviour of packaged 7.92 remains unestablished. BusyBox 1.36.1 small nc lacks -v while its 1.10-compatible applet lists -v. As this guide's assessment, refusal or timeout proves only that this connection failed; local errors, unsupported options and exit 1 without output are inconclusive. The OpenSSH 9.9 client options select password and disable public key; the literal Permission denied (publickey) is this guide's reasoned expectation dependent on server-advertised methods, while immediate failure with NO password prompt and a Permission denied (...) method list naming neither password nor keyboard-interactive are required. As this guide's reasoning, the client prints the server's remaining methods in that list.", "components": ["ufw", "iproute2", "ubuntu-nc", "c9s-nmap", "busybox", "openssh99"], "sources": ["ufw:scff3a017f30b", "iproute2:s2afc4764d5bb", "iproute2:sfaa932c2ca13", "iproute2:sd295f82d643f", "iproute2:s65278ee45850", "iproute2:s8ecdaf9e9ea7", "iproute2:s4e1c28d5adad", "ubuntu-nc:s478aaf9a8975", "ubuntu-nc:sd7b31d3bc579", "ubuntu-nc:scc48da80246b", "c9s-nmap:sd06e83963e39", "busybox:sd707e18625cc", "busybox:s34bdee292f79", "busybox:s14b89daa008d", "c9s-nmap:s3ab25d24e37a", "ubuntu-nc:s5e260ceab82c", "openssh99:sd768a096f236", "openssh99:s711f7f9ad562", "openssh99:saa71f4024a44"], "status": "REASONED", "verify": [1]},
    "verify-firewall": {"text": "UFW status should show default-deny ingress and admin-scoped SSH allowances; also inspect show raw because status omits /etc/ufw rules.", "components": ["ufw"], "sources": ["ufw:scff3a017f30b"], "status": "REASONED", "verify": [1]},
    "verify-external": {"text": "Disallowed-source TCP 22 must fail while allowed SSH works; correlate effective rules. As this guide's assessment, refusal alone, local errors and unsupported netcat options are inconclusive.", "components": ["ufw", "firewalld"], "sources": ["ufw:scff3a017f30b", "firewalld:sa1a1385129f1"], "status": "REASONED", "verify": [1]},
    "verify-password": {"text": "A password-only SSH attempt must fail immediately without a password prompt and show a Permission denied (...) method list naming neither password nor keyboard-interactive. As this guide's reasoning, the client prints the server's remaining methods in that list; a prompt or a list naming either method means that path is still on.", "components": ["ssh", "openssh99"], "sources": ["ssh:s44f73ffcb41e", "openssh99:saa71f4024a44", "openssh99:sd768a096f236", "openssh99:s711f7f9ad562"], "status": "REASONED", "verify": [1]},
    "verify-mfa": {"text": "After key acceptance require a code, reject wrong/omitted codes and unenrolled users without nullok, and use Duo failmode=secure; test before closing the working session.", "components": ["ssh", "totp", "duo"], "sources": ["ssh:s44f73ffcb41e", "totp:s6f787f7b4f18", "duo:s18b76ce18df1"], "status": "REASONED", "verify": [1]}
  }
}
````
<!-- version-basis:end -->
