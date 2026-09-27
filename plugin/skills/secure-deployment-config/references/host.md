---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "7ec61a3b662fc5b4bc804bea03d70b2907837b5d7382ece647096b00e5012adb",
  "components": {
    "ssh": {
      "name": "OpenSSH documentation",
      "basis": "unknown",
      "sources": {
        "s44f73ffcb41e": "https://man.openbsd.org/sshd_config"
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
    }
  },
  "claims": {
    "safe-transition": {"text": "Confirm non-root key login and sudo in a fresh session before disabling password/root access; retain the working session while testing.", "components": ["ssh"], "sources": ["ssh:s44f73ffcb41e"], "status": "REASONED"},
    "keys-only": {"text": "Disable PasswordAuthentication and KbdInteractiveAuthentication; enable PubkeyAuthentication and prohibit root login.", "components": ["ssh"], "sources": ["ssh:s44f73ffcb41e"], "status": "REASONED"},
    "include-order": {"text": "First-read values and lexical includes motivate 00-hardening.conf; the OpenSSH 8.2, Ubuntu 20.04 and cloud-init distribution history lacks a direct source here.", "components": ["ssh"], "sources": ["ssh:s44f73ffcb41e"], "status": "REASONED"},
    "effective-config": {"text": "Validate with sshd -t before reload; inspect sshd -T global values and -T -C for Match-specific settings. Service names differ by distribution.", "components": ["ssh"], "sources": ["ssh:s44f73ffcb41e"], "status": "REASONED"},
    "totp": {"text": "SSH TOTP uses google-authenticator-libpam through PAM keyboard-interactive; keys-only configuration must change before adding this factor.", "components": ["ssh", "totp"], "sources": ["ssh:s44f73ffcb41e", "totp:s6f787f7b4f18"], "status": "REASONED"},
    "duo": {"text": "Duo pam_duo provides the alternative push factor through PAM keyboard-interactive.", "components": ["ssh", "duo"], "sources": ["ssh:s44f73ffcb41e", "duo:s18b76ce18df1"], "status": "REASONED"},
    "mfa-methods": {"text": "UsePAM yes and AuthenticationMethods publickey,keyboard-interactive require both methods; keep password/root login disabled and public keys enabled.", "components": ["ssh", "duo"], "sources": ["ssh:s44f73ffcb41e", "duo:s18b76ce18df1"], "status": "REASONED"},
    "legacy-name": {"text": "Older configurations use ChallengeResponseAuthentication for KbdInteractiveAuthentication; enable the spelling present when configuring PAM MFA.", "components": ["ssh", "duo"], "sources": ["ssh:s44f73ffcb41e", "duo:s18b76ce18df1"], "status": "REASONED"},
    "ufw-default": {"text": "Set deny incoming and allow outgoing, then enable UFW; permit TCP 80 and 443 for the TLS layer.", "components": ["ufw"], "sources": ["ufw:scff3a017f30b"], "status": "REASONED"},
    "ufw-ssh": {"text": "Remove any broad OpenSSH allow before adding an admin-source TCP 22 rule; adding a narrower rule does not replace the old allowance.", "components": ["ufw"], "sources": ["ufw:scff3a017f30b"], "status": "REASONED"},
    "brokered-ssh": {"text": "SSM/tailnet avoid public inbound SSH; IAP uses 35.235.240.0/20 and Bastion its subnet on 22 in both layers. Broker details have no direct source here.", "components": ["ufw"], "sources": ["ufw:scff3a017f30b"], "status": "REASONED"},
    "firewalld-zone": {"text": "Find the public interface zone explicitly; remove its broad ssh service, add the IPv4 admin rich rule permanently, then reload to activate it.", "components": ["firewalld"], "sources": ["firewalld:sa1a1385129f1", "firewalld:sc1cb4d135f3b"], "status": "REASONED"},
    "firewalld-audit": {"text": "Inspect applicable zones for other services, port ranges, protocol/source allowances or ACCEPT targets that reopen 22; the narrow rich rule does not supersede them.", "components": ["firewalld"], "sources": ["firewalld:sa1a1385129f1", "firewalld:sc1cb4d135f3b"], "status": "REASONED"},
    "docker-bypass": {"text": "Published Docker ports bypass UFW; consult docker.md before relying on the host firewall. This guide has no direct Docker citation.", "components": ["ufw"], "sources": ["ufw:scff3a017f30b"], "status": "REASONED"},
    "fail2ban": {"text": "Use fail2ban to ban repeated authentication failures against SSH/login services.", "components": ["fail2ban"], "sources": ["fail2ban:s7a37ae416e85"], "status": "REASONED"},
    "crowdsec": {"text": "CrowdSec is the alternative protection for repeated authentication failures.", "components": ["crowdsec"], "sources": ["crowdsec:s4efe4c22c69b"], "status": "REASONED"},
    "updates": {"text": "Automate patches with unattended-upgrades on Debian/Ubuntu or dnf-automatic on RHEL-family systems; no update-tool source is listed.", "components": ["ssh"], "sources": ["ssh:s44f73ffcb41e"], "status": "REASONED"},
    "verify-listeners": {"text": "Inventory intended TCP/UDP listeners and addresses in both IP families; no ss manual is listed.", "components": ["ufw"], "sources": ["ufw:scff3a017f30b"], "status": "REASONED", "verify": [1]},
    "verify-firewall": {"text": "UFW status should show default-deny ingress and admin-scoped SSH allowances; also inspect show raw because status omits /etc/ufw rules.", "components": ["ufw"], "sources": ["ufw:scff3a017f30b"], "status": "REASONED", "verify": [1]},
    "verify-external": {"text": "Disallowed-source TCP 22 must fail while allowed SSH works; correlate effective rules. Refusal alone, local errors and unsupported netcat options are inconclusive.", "components": ["ufw", "firewalld"], "sources": ["ufw:scff3a017f30b", "firewalld:sa1a1385129f1"], "status": "REASONED", "verify": [1]},
    "verify-password": {"text": "A password-only SSH attempt must fail immediately without a password prompt; a prompt means password authentication remains enabled.", "components": ["ssh"], "sources": ["ssh:s44f73ffcb41e"], "status": "REASONED", "verify": [1]},
    "verify-mfa": {"text": "After key acceptance require a code, reject wrong/omitted codes and unenrolled users without nullok, and use Duo failmode=secure; test before closing the working session.", "components": ["ssh", "totp", "duo"], "sources": ["ssh:s44f73ffcb41e", "totp:s6f787f7b4f18", "duo:s18b76ce18df1"], "status": "REASONED", "verify": [1]}
  }
}
---
# Host baseline: SSH, firewall, updates

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| safe-transition: Confirm non-root key login and sudo in a fresh session before disabling password/root access; retain the working session while testing. | OpenSSH documentation unknown | REASONED |
| keys-only: Disable PasswordAuthentication and KbdInteractiveAuthentication; enable PubkeyAuthentication and prohibit root login. | OpenSSH documentation unknown | REASONED |
| include-order: First-read values and lexical includes motivate 00-hardening.conf; the OpenSSH 8.2, Ubuntu 20.04 and cloud-init distribution history lacks a direct source here. | OpenSSH documentation unknown | REASONED |
| effective-config: Validate with sshd -t before reload; inspect sshd -T global values and -T -C for Match-specific settings. Service names differ by distribution. | OpenSSH documentation unknown | REASONED |
| totp: SSH TOTP uses google-authenticator-libpam through PAM keyboard-interactive; keys-only configuration must change before adding this factor. | OpenSSH documentation unknown; google-authenticator-libpam unknown | REASONED |
| duo: Duo pam_duo provides the alternative push factor through PAM keyboard-interactive. | OpenSSH documentation unknown; Duo Unix unknown | REASONED |
| mfa-methods: UsePAM yes and AuthenticationMethods publickey,keyboard-interactive require both methods; keep password/root login disabled and public keys enabled. | OpenSSH documentation unknown; Duo Unix unknown | REASONED |
| legacy-name: Older configurations use ChallengeResponseAuthentication for KbdInteractiveAuthentication; enable the spelling present when configuring PAM MFA. | OpenSSH documentation unknown; Duo Unix unknown | REASONED |
| ufw-default: Set deny incoming and allow outgoing, then enable UFW; permit TCP 80 and 443 for the TLS layer. | UFW documentation unknown | REASONED |
| ufw-ssh: Remove any broad OpenSSH allow before adding an admin-source TCP 22 rule; adding a narrower rule does not replace the old allowance. | UFW documentation unknown | REASONED |
| brokered-ssh: SSM/tailnet avoid public inbound SSH; IAP uses 35.235.240.0/20 and Bastion its subnet on 22 in both layers. Broker details have no direct source here. | UFW documentation unknown | REASONED |
| firewalld-zone: Find the public interface zone explicitly; remove its broad ssh service, add the IPv4 admin rich rule permanently, then reload to activate it. | firewalld documentation unknown | REASONED |
| firewalld-audit: Inspect applicable zones for other services, port ranges, protocol/source allowances or ACCEPT targets that reopen 22; the narrow rich rule does not supersede them. | firewalld documentation unknown | REASONED |
| docker-bypass: Published Docker ports bypass UFW; consult docker.md before relying on the host firewall. This guide has no direct Docker citation. | UFW documentation unknown | REASONED |
| fail2ban: Use fail2ban to ban repeated authentication failures against SSH/login services. | fail2ban unknown | REASONED |
| crowdsec: CrowdSec is the alternative protection for repeated authentication failures. | CrowdSec unknown | REASONED |
| updates: Automate patches with unattended-upgrades on Debian/Ubuntu or dnf-automatic on RHEL-family systems; no update-tool source is listed. | OpenSSH documentation unknown | REASONED |
| verify-listeners: Inventory intended TCP/UDP listeners and addresses in both IP families; no ss manual is listed. | UFW documentation unknown | REASONED |
| verify-firewall: UFW status should show default-deny ingress and admin-scoped SSH allowances; also inspect show raw because status omits /etc/ufw rules. | UFW documentation unknown | REASONED |
| verify-external: Disallowed-source TCP 22 must fail while allowed SSH works; correlate effective rules. Refusal alone, local errors and unsupported netcat options are inconclusive. | UFW documentation unknown; firewalld documentation unknown | REASONED |
| verify-password: A password-only SSH attempt must fail immediately without a password prompt; a prompt means password authentication remains enabled. | OpenSSH documentation unknown | REASONED |
| verify-mfa: After key acceptance require a code, reject wrong/omitted codes and unenrolled users without nullok, and use Duo failmode=secure; test before closing the working session. | OpenSSH documentation unknown; google-authenticator-libpam unknown; Duo Unix unknown | REASONED |
<!-- version-basis:end -->

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

sshd uses the *first* value it reads for each option, and current Debian, Ubuntu, and RHEL-family systems ship a main `sshd_config` that includes `/etc/ssh/sshd_config.d/*.conf` near the top, before its own settings (`sshd_config` gained the `Include` keyword in OpenSSH 8.2, and distributions began shipping this drop-in include in the stock config around then, from Ubuntu 20.04). Cloud images commonly carry a `50-cloud-init.conf` there, written by cloud-init when password login is requested, that sets `PasswordAuthentication yes`; read before a later main-file line or a higher-numbered drop-in, it wins and password login stays on. Name the hardening file `00-hardening.conf` so it is read first, and confirm with `sshd -T` (below) that the value took effect, in case an upgraded main file lacks the include or an earlier drop-in already set it.

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

SSH stays closed to the world here for the same reason rule 3 in [cloud-firewalls.md](cloud-firewalls.md) keeps it off the cloud firewall: `ufw allow OpenSSH` opens port 22 to every address on the internet. Restrict it to the range you administer from. AWS SSM Session Manager (its agent dials out to the SSM service) or a tailnet ([tailscale.md](tailscale.md)) needs no inbound SSH rule at all; GCP IAP and Azure Bastion instead connect to port 22 and need an allow for their documented source range (IAP `35.235.240.0/20`, the Azure `AzureBastionSubnet`) in both firewall layers, per [cloud-firewalls.md](cloud-firewalls.md).

RHEL-family systems use firewalld (`firewall-cmd --permanent --add-service=https` and so on) with the same posture, and that includes SSH: `--add-service=ssh` opens port 22 to every address exactly as `ufw allow OpenSSH` does. Open only the ports the TLS-terminating layer needs; databases and app servers stay unreachable from outside per their guides. Docker-published ports bypass ufw entirely; see [docker.md](docker.md) before relying on the firewall.

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
- Automate security patches: `unattended-upgrades` on Debian/Ubuntu, `dnf-automatic` on RHEL-family systems.

## 4. Verify

REASONED: listener, firewall, SSH key-only and PAM MFA checks; no exposed/fixed run is recorded in this guide. Expectations follow the cited SSH, firewall and MFA sources; this read-only review has no authorized target host or external probe machine.

```bash
sudo ss -tulnp                    # TCP and UDP listeners (IPv4 and IPv6): only intended ones, on intended addresses
sudo ufw status verbose           # default deny incoming; then `sudo ufw show raw` (status verbose omits rules loaded from /etc/ufw): every allowance that can reach 22 (a port-22 rule OR a broader "from <range> to any" allow) is scoped to your admin range, never Anywhere
(                                 # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
    *) nc -vz -w 3 "$1" 22 ;;   # from an address outside the admin range: must fail to connect
    # a refusal or timeout only means THIS connection failed, not that the host firewall denied it (a host with
    # no sshd listening refuses too): confirm SSH works from an allowed source and read `ufw status`/`--list-all`
    # for the effective rule. A local error, an unsupported option (BusyBox netcat rejects -v), or exit 1 with no
    # output at all is inconclusive: nothing reached the network
  esac
)
# guard-conventions: allow probe of an illustrative user@host; no reader-substituted placeholder in this probe's argv
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no user@host   # keys-only: expect an immediate "Permission denied (publickey)" with NO password prompt; a password prompt means password auth is still on
# guard-conventions: allow probe of an illustrative user@host; no reader-substituted placeholder in this probe's argv
ssh user@host                     # with PAM MFA: the key is accepted, then a code is required before a shell. Also confirm a wrong or omitted code is REJECTED, that unenrolled users are denied (drop `nullok`), and that Duo fails closed (`failmode=secure`), per mfa.md; otherwise the factor is optional, not mandatory
```

Run the SSH test from a second terminal before closing your working session.

## Sources (checked September 2026)

- OpenSSH sshd_config manual: https://man.openbsd.org/sshd_config
- ufw(8), for `default deny incoming`, `allow` and `status verbose`: https://manpages.ubuntu.com/manpages/noble/man8/ufw.8.html
- firewall-cmd(1), for `--permanent --add-service` and `--add-rich-rule`: https://firewalld.org/documentation/man-pages/firewall-cmd.html
- firewalld.richlanguage(5), for the `source address` / `service name` / `accept` rule form: https://firewalld.org/documentation/man-pages/firewalld.richlanguage.html
- fail2ban: https://github.com/fail2ban/fail2ban
- CrowdSec: https://www.crowdsec.net/
- google-authenticator-libpam: https://github.com/google/google-authenticator-libpam
- Duo Unix (`UsePAM`, `KbdInteractiveAuthentication`, `AuthenticationMethods publickey,keyboard-interactive`): https://duo.com/docs/duounix
