# Host baseline: SSH, firewall, updates

Every guide in this repository secures a service; this one secures the machine under them. Apply it once per host before exposing anything.

## 1. SSH: keys only, no root login

Add your public key to `~/.ssh/authorized_keys` and confirm that key login works **before** disabling passwords. Keep the current session open while testing changes.

Put this in a drop-in that sorts first, `/etc/ssh/sshd_config.d/00-hardening.conf`, not only in the main `/etc/ssh/sshd_config`:

```
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
```

sshd uses the *first* value it reads for each option, and current Debian, Ubuntu, and RHEL-family systems ship a main `sshd_config` that includes `/etc/ssh/sshd_config.d/*.conf` near the top, before its own settings (the `Include` keyword is a distribution default, added in OpenSSH 8.2). Cloud images commonly carry a `50-cloud-init.conf` there, written by cloud-init when password login is requested, that sets `PasswordAuthentication yes`; read before a later main-file line or a higher-numbered drop-in, it wins and password login stays on. Name the hardening file `00-hardening.conf` so it is read first, and confirm with `sshd -T` (below) that the value took effect, in case an upgraded main file lacks the include or an earlier drop-in already set it.

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

SSH stays closed to the world here for the same reason rule 3 in [cloud-firewalls.md](cloud-firewalls.md) keeps it off the cloud firewall: `ufw allow OpenSSH` opens port 22 to every address on the internet. Restrict it to the range you administer from, or add no SSH rule at all and reach the host through brokered access or a tailnet ([tailscale.md](tailscale.md)).

RHEL-family systems use firewalld (`firewall-cmd --permanent --add-service=https` and so on) with the same posture, and that includes SSH: `--add-service=ssh` opens port 22 to every address exactly as `ufw allow OpenSSH` does. Open only the ports the TLS-terminating layer needs; databases and app servers stay unreachable from outside per their guides. Docker-published ports bypass ufw entirely; see [docker.md](docker.md) before relying on the firewall.

```bash
# firewalld, where an earlier run enabled the ssh service: a rich rule does not supersede it.
# Every command below names the zone: without --zone they act on the default zone, which is not
# necessarily the one holding the internet-facing interface.
sudo firewall-cmd --get-active-zones            # find the zone your public interface is in
sudo firewall-cmd --permanent --zone=REPLACE_WITH_PUBLIC_ZONE --remove-service=ssh
sudo firewall-cmd --permanent --zone=REPLACE_WITH_PUBLIC_ZONE --add-rich-rule='rule family="ipv4" source address="REPLACE_WITH_ADMIN_RANGE" service name="ssh" accept'
sudo firewall-cmd --reload                      # --permanent writes the stored config only; nothing changes until this
sudo firewall-cmd --zone=REPLACE_WITH_PUBLIC_ZONE --list-all   # confirm: no ssh under services, and the rich rule present
```

## 3. Brute-force protection and updates

- fail2ban ([github.com/fail2ban/fail2ban](https://github.com/fail2ban/fail2ban)) or CrowdSec ([crowdsec.net](https://www.crowdsec.net/)) bans repeated authentication failures against SSH and login panels.
- Automate security patches: `unattended-upgrades` on Debian/Ubuntu, `dnf-automatic` on RHEL-family systems.

## 4. Verify

```bash
ss -tlnp                          # only intended listeners, on intended addresses
sudo ufw status verbose           # default deny incoming; port 22 shows your admin range, never Anywhere
(                                 # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
    *) nc -vz -w 3 "$1" 22 ;;   # from an address outside the admin range: must fail to connect
    # a refusal or a timeout from YOUR address is the pass. A local error, an unsupported option (BusyBox
    # netcat rejects -v), or exit 1 with no output at all is inconclusive: nothing reached the network
  esac
)
ssh -o PreferredAuthentications=password user@host   # expect: Permission denied
ssh user@host                     # with PAM MFA: the key is accepted, then the code prompt appears before a shell
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
