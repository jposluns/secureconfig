# Self-signed certificates

A self-signed certificate is one signed with its own key rather than by a certificate authority browsers already trust. This guide helps your AI assistant use one securely, including creating it with OpenSSL, mkcert only on development machines, a protected private key, and clients that trust it without disabling verification.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/self-signed.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against OpenSSL documentation (rolling) (no recorded version), Requests TLS documentation v2.32.3, Git ignore documentation v2.43.0, curl command documentation curl-8_12_1, Node.js extra CA certificates v22.19.0, and Service identity RFC 9525, plus 5 more recorded bases; 9 further sources are pinned to a commit and 1 carries no recorded version. Metadata reviewed 2026-10-21; documentation checked September 2026. The guide records 25 claims: 1 demonstrated by a check that ran and 24 reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

Use a self-signed certificate when the service has no public DNS name, when an ACME CA cannot reach it, and when [cloudflare.md](cloudflare.md) is not an option: internal tools, lab and development environments, and machine-to-machine links on private networks. For anything a browser user or external party reaches, prefer [free-certificates.md](free-certificates.md); self-signed certificates trigger browser warnings and every client must be configured to trust them.

Self-signed TLS still matters. It encrypts credentials and data in transit; without it, authentication tokens cross the network in cleartext.

## 1. Generate a certificate with OpenSSL

RSA, single command (OpenSSL 3.0 or later):

```bash
openssl req -x509 -newkey rsa:4096 -sha256 -days 365 -noenc \
  -keyout server.key -out server.crt \
  -subj "/CN=app.internal" \
  -addext "basicConstraints=critical,CA:FALSE" \
  -addext "subjectAltName=DNS:app.internal,DNS:localhost,IP:127.0.0.1,IP:203.0.113.10"
```

ECDSA (smaller and faster; generate the key first, then the certificate):

```bash
openssl ecparam -name prime256v1 -genkey -noout -out server.key
openssl req -x509 -key server.key -sha256 -days 365 -out server.crt \
  -subj "/CN=app.internal" \
  -addext "basicConstraints=critical,CA:FALSE" \
  -addext "subjectAltName=DNS:app.internal,IP:203.0.113.10"
```

Rules that make the certificate actually work:

- The `subjectAltName` list must contain every DNS name and IP address clients will use to reach the service (this guide's requirement, based on the RFC 9525 matching rules that follow). RFC 9525 requires DNS identity matching by comparing labels ('Each label MUST match', except under its wildcard rule) and says an IP-ID reference identifier 'MUST exactly match the value of an iPAddress entry in subjectAltName'. It says the subject Common Name 'MUST NOT be used to identify a service'. If no presented identifier matches, RFC 9525 says an automated client 'SHOULD terminate' and permits a configured exception that 'MUST NOT' disable this security control by default, while a human-facing client 'SHOULD' warn and terminate but may offer advanced users an override. Its ad hoc pinning provision says such pinning 'SHOULD NOT' restrict future connections to only the pinned certificate. Some verifiers, including OpenSSL's default, still fall back to the CN, so confirm in Verify below that the SAN exists rather than trusting a CN. Replace the example `203.0.113.10` (a documentation address from RFC 5737) with your service's real IP, or drop the `IP:` entries if clients reach it only by name.
- `basicConstraints=critical,CA:FALSE` marks the certificate a leaf, not a CA. It matters because section 4 installs the certificate into client trust stores: OpenSSL's stock configuration marks a bare `req -x509` certificate `CA:TRUE`, which in a trust store is a signer for any name, using the unencrypted key that `-noenc` leaves on the server. This override relies on OpenSSL 3.0 or later, where a command-line extension replaces the configuration default; the end-of-life 1.1.1 would instead emit a duplicate, invalid extension.
- `-noenc` (spelled `-nodes` before OpenSSL 3.0, still accepted but deprecated) leaves the key unencrypted so services can start unattended; protect it with file permissions instead.
- Track the `-days` expiry. Nothing renews a self-signed certificate for you; put the date in your calendar or monitoring.

## 2. Protect the private key

This guide advises protecting `server.key` with mode `600` and ownership by the account and group your service runs as; `app:app` below is this guide's example, to replace with that account and group. GNU coreutils v9.7 documents `chmod` changing file access permissions and taking new mode bits, and `chown owner:group` changing both owner and group (see Sources); it does not recommend a service account or select one for this key. This guide's reading of `600` is owner read/write and no group or other permissions, based on GNU coreutils v9.7's Numeric Modes definition in `doc/perm.texi` (see Sources).

```bash
chmod 600 server.key
chown app:app server.key      # whichever user your service runs as
```

Never commit a private key to version control. Add `*.key` and `*.pem` to `.gitignore` before generating anything inside a repository, and treat any key that has ever been committed or pasted into a chat as compromised: regenerate it.

## 3. mkcert for local development

[mkcert](https://github.com/FiloSottile/mkcert) creates a local CA, installs it into your OS and browser trust stores, and issues certificates that your own machine trusts with no warnings:

```bash
mkcert -install
mkcert app.test localhost 127.0.0.1 ::1
```

This is for development machines only. The generated CA can sign for any name, so its key must never leave the developer's machine, and mkcert certificates must never serve real users.

## 4. Make clients trust the certificate; never disable verification

Distribute the certificate (or your internal CA certificate) to clients instead of turning verification off:

Debian trixie and Ubuntu noble remain cited; the Debian bookworm and bullseye and Ubuntu jammy and focal manpages also document `update-ca-certificates` including `.crt` certificates under `/usr/local/share/ca-certificates` as implicitly trusted (see Sources). The Ubuntu resolute manpage words this slightly differently, saying that such certificates "are also included and implicitly trusted", and tells the reader to copy PEM certificates with the `.crt` extension to `/usr/local/share/ca-certificates` and then run `update-ca-certificates` (see Sources). Use on other Debian and Ubuntu releases remains this guide's assessment, with release-specific citations absent.

Documentation reading on 2026-10-24: Debian's releases page gives bullseye's End of LTS as 2026-08-31, now past, although its Status cell still says LTS support (see Sources). Documentation reading on 2026-10-24: Ubuntu's release-cycle page gives focal's standard security maintenance as ending May 2025, now past, with coverage after that only through Ubuntu Pro (see Sources). Both the bullseye and focal manpage citations remain because they still document those releases' commands.

RHEL 9 remains cited, and the RHEL 8 shared system certificates page also says to copy a certificate in the simple PEM or DER file formats to `/usr/share/pki/ca-trust-source/anchors/` or `/etc/pki/ca-trust/source/anchors/` and run `update-ca-trust extract` (see Sources). The CentOS Stream 8, 9 and 10 package manuals and the Fedora rawhide, 41, 42, 43, 44 and 45 branch dist-git manuals instruct adding a simple PEM or DER certificate to `/etc/pki/ca-trust/source/anchors/` and running `update-ca-trust extract` (see Sources). The Fedora 41, 42 and 43 branch manuals, at the pinned commits, give this instruction on the same lines 97 to 99 as the cited rawhide manual, with no difference from the rawhide citation there. The CentOS Stream 9 and Fedora 44 and 45 branch manuals, at the pinned commits, also give it on lines 97 to 99. CentOS Stream is not RHEL, rawhide is Fedora's development branch, not a released Fedora, and this guide does not establish whether Fedora 45 has been released; use on other RHEL releases (including 10), other Fedora releases and other CentOS Stream releases remains this guide's assessment, with release-specific citations absent.

```bash
# Debian trixie/bookworm/bullseye and Ubuntu resolute/noble/jammy/focal system trust store; other releases: this guide's assessment
# Documentation reading, 2026-10-24 (see Sources): bullseye past Debian LTS (End of LTS 2026-08-31; Status still says LTS support).
# Focal past standard security maintenance (ended May 2025); coverage after that only through Ubuntu Pro.
# Both manpage citations still document those releases' commands.
sudo cp server.crt /usr/local/share/ca-certificates/app-internal.crt
sudo update-ca-certificates

# RHEL 8/9 system trust store; CentOS Stream 8/9/10 (not RHEL); Fedora 41/42/43/44; Fedora 45 branch (release status not established); Fedora rawhide (development, not a release)
# Other RHEL (including 10), other Fedora and other CentOS Stream: this guide's assessment
sudo cp server.crt /etc/pki/ca-trust/source/anchors/app-internal.crt
sudo update-ca-trust extract

# Per-tool
curl -q --cacert server.crt https://app.internal/
export REQUESTS_CA_BUNDLE=/path/to/server.crt      # Python requests
export NODE_EXTRA_CA_CERTS=/path/to/server.crt     # Node.js
```

Do not ship `curl -k`, `verify=False`, `rejectUnauthorized: false`, or `NODE_TLS_REJECT_UNAUTHORIZED=0` in committed code. For curl and Requests, `-k` and `verify=False` disable certificate verification (see their existing Sources entries). Node.js v24.22.0 documents `NODE_TLS_REJECT_UNAUTHORIZED=0` as an environment variable disabling certificate validation for TLS connections in the Node.js process and strongly discourages its use. In `tls.connect`, `rejectUnauthorized: false` disables verification of the server certificate against supplied CAs for that client connection. In `tls.createServer`, it disables rejection of connections unauthorized by supplied CAs; the option only has an effect when `requestCert` is `true`. These Node.js passages establish the documented settings and their scope, not their use in a particular deployment. This guide's assessment is that these bypasses accept attacker-controlled certificates as readily as your own and reliably survive into production.

## 5. Verify

DEMONSTRATED: following block; local certificate-output inspection only. On 2026-10-05 in private /dev/shm scratch, OpenSSL 3.5.5 ran the printed x509 command on three disposable one-day RSA certificates. Missing-SAN and CA:TRUE fixtures each exited 0 but lacked the required SAN or leaf constraint; the fixed fixture also exited 0 and printed DNS:app.internal, IP Address:127.0.0.1 and critical CA:FALSE. Subject and validity dates printed for all three.

```bash
openssl x509 -in server.crt -noout -subject -dates -ext subjectAltName,basicConstraints
```

REASONED: following block; live TLS identity, failure handling and client-trust checks follow the cited OpenSSL and mkcert documentation. No app.internal service or client trust-store installation was supplied for these checks. The local x509 run above does not demonstrate a handshake or installed trust; expected outcomes and limitations are stated below.

```bash
openssl s_client -connect app.internal:443 -servername app.internal -verify_hostname app.internal -verify_return_error -CAfile server.crt </dev/null
```

REASONED: preceding block; live TLS identity, failure handling and installed client trust, per the guide's cited OpenSSL documentation and curl curl-8_12_1 normal certificate verification and --insecure. No app.internal service or writable system trust store is available, and local listeners are denied. bash -n and ShellCheck 0.11.0 exited 0 without diagnostics. OpenSSL 3.5.5 generated RSA and ECDSA certificates; offline x509 inspection exited 0 for missing-SAN, IP-only, CA:TRUE and fixed fixtures, displaying their differing extensions. Offline verify accepted the matching hostname even without a DNS SAN, rejected wrong names with error 62 and distinguished IP identities with error 64. Handshake and installed-trust outcomes below remain unobserved. A pass prints `Verification: OK`, `Verified peername: app.internal`, and `Verify return code: 0 (ok)`, and the command exits 0. Without `-verify_hostname` the check ignores the name, and without `-verify_return_error` `s_client` reports a failure yet still completes the handshake and exits 0; with both, a name mismatch or an untrusted chain closes the connection and exits non-zero (`Verify return code: 62 (hostname mismatch)` for the wrong name). Read the first command's output rather than its exit status (it exits 0 even with no SAN): confirm a `subjectAltName` covering every name and IP clients use and `basicConstraints` marked `CA:FALSE`, and use `-verify_ip <addr>` to check an IP identity, since `-verify_hostname` falls back to the Common Name whenever the certificate carries no DNS-name SAN entry (even if it has an IP SAN), so a CN-only or IP-only certificate can still pass a hostname check. The `s_client` check supplies trust explicitly with `-CAfile`, so it proves the certificate and name but not that the section-4 trust-store install took effect; confirm that separately from each client with its normal configuration (for the system store, a plain `curl https://app.internal/` with no `--cacert` should fail before `update-ca-certificates` and succeed after).

## Limits to plan around

Self-signed certificates have no revocation and no third-party accountability, and trust distribution is manual. When the audience grows beyond a small internal group, move to [free-certificates.md](free-certificates.md) or put the service behind [cloudflare.md](cloudflare.md). Authentication is still required either way: see [authentication.md](authentication.md).

## Sources (checked September 2026)

- OpenSSL documentation (rolling documentation, checked September 2026): https://docs.openssl.org/ ; `openssl s_client` (`-servername`, `-verify_return_error`): https://docs.openssl.org/master/man1/openssl-s_client/ ; verification options (`-verify_hostname`): https://docs.openssl.org/master/man1/openssl-verification-options/
- mkcert: https://github.com/FiloSottile/mkcert
- Requests v2.32.3 CA-bundle environment variables (checked October 2026): https://github.com/psf/requests/blob/v2.32.3/docs/user/advanced.rst#L238-L239
- Requests v2.32.3 disabled certificate verification (checked October 2026): https://github.com/psf/requests/blob/v2.32.3/docs/user/advanced.rst#L246-L250
- Git v2.43.0 ignore rules and already tracked files (checked October 2026): https://github.com/git/git/blob/v2.43.0/Documentation/gitignore.txt#L15-L18
- curl curl-8_12_1 explicit CA trust (checked October 2026): https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/cacert.md#L21-L24
- curl curl-8_12_1 normal certificate verification and `--insecure` (checked October 2026): https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/insecure.md#L21-L28
- Node.js v22.19.0 extra trusted CA certificates (checked October 2026): https://github.com/nodejs/node/blob/v22.19.0/doc/api/cli.md#L3234-L3238
- RFC 9525 subject Common Name (checked October 2026): https://www.rfc-editor.org/rfc/rfc9525.html#section-2
- RFC 9525 reference identifiers and IP-ID matching (checked October 2026): https://www.rfc-editor.org/rfc/rfc9525.html#section-6.2
- RFC 9525 DNS identity matching (checked October 2026): https://www.rfc-editor.org/rfc/rfc9525.html#section-6.3
- RFC 9525 IP identity matching (checked October 2026): https://www.rfc-editor.org/rfc/rfc9525.html#section-6.4
- RFC 9525 identity mismatch outcome (checked October 2026): https://www.rfc-editor.org/rfc/rfc9525.html#section-6.6
- Debian trixie update-ca-certificates (checked October 2026): https://manpages.debian.org/trixie/ca-certificates/update-ca-certificates.8.en.html#DESCRIPTION
- Ubuntu noble update-ca-certificates (checked October 2026): https://manpages.ubuntu.com/manpages/noble/man8/update-ca-certificates.8.html#description
- RHEL 9 shared system certificates (checked October 2026): https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/securing_networks/using-shared-system-certificates_securing-networks#adding-new-certificates_using-shared-system-certificates
- Debian bookworm update-ca-certificates (checked October 2026): https://manpages.debian.org/bookworm/ca-certificates/update-ca-certificates.8.en.html ; "Furthermore all certificates with a .crt extension found below /usr/local/share/ca-certificates are also included as implicitly trusted."
- Ubuntu jammy update-ca-certificates (checked October 2026): https://manpages.ubuntu.com/manpages/jammy/man8/update-ca-certificates.8.html ; "Furthermore all certificates with a .crt extension found below /usr/local/share/ca-certificates are also included as implicitly trusted."
- CentOS Stream 8, not RHEL, ca-certificates commit ad398898923bddb3953d2aa4c8d9d17c901ef3a4, update-ca-trust.8.txt lines 97 to 99 (checked October 2026): https://gitlab.com/redhat/centos-stream/rpms/ca-certificates/-/blob/ad398898923bddb3953d2aa4c8d9d17c901ef3a4/update-ca-trust.8.txt#L97-L99 ; QUICK HELP 1 specifies a simple PEM or DER certificate, /etc/pki/ca-trust/source/anchors/ and update-ca-trust extract.
- CentOS Stream 10, not RHEL, ca-certificates commit 1ab579df1508321342e9ab244fd4ed397ea89b80, update-ca-trust.8.txt lines 97 to 99 (checked October 2026): https://gitlab.com/redhat/centos-stream/rpms/ca-certificates/-/blob/1ab579df1508321342e9ab244fd4ed397ea89b80/update-ca-trust.8.txt#L97-L99 ; QUICK HELP 1 specifies a simple PEM or DER certificate, /etc/pki/ca-trust/source/anchors/ and update-ca-trust extract.
- Fedora rawhide development branch, not a released Fedora, ca-certificates commit 725690846ee1ae1cd46e62c3a336c84820390d27, update-ca-trust.8.txt lines 97 to 99 (checked October 2026): https://src.fedoraproject.org/rpms/ca-certificates/blob/725690846ee1ae1cd46e62c3a336c84820390d27/f/update-ca-trust.8.txt#_97 ; QUICK HELP 1 specifies a simple PEM or DER certificate, /etc/pki/ca-trust/source/anchors/ and update-ca-trust extract.
- Debian bullseye update-ca-certificates (checked October 2026): https://manpages.debian.org/bullseye/ca-certificates/update-ca-certificates.8.en.html ; "Furthermore all certificates with a .crt extension found below /usr/local/share/ca-certificates are also included as implicitly trusted."
- Ubuntu focal update-ca-certificates (checked October 2026): https://manpages.ubuntu.com/manpages/focal/man8/update-ca-certificates.8.html ; "Furthermore all certificates with a .crt extension found below /usr/local/share/ca-certificates are also included as implicitly trusted."
- Debian releases, Index of releases, bullseye row (checked October 2026): https://www.debian.org/releases/ ; read 2026-10-24, End of LTS and Status columns.
- Ubuntu release cycle, Selected product coverage details, Ubuntu 20.04 LTS row (checked October 2026): https://ubuntu.com/about/release-cycle ; read 2026-10-24, Standard security maintenance and Ubuntu Pro columns.
- Fedora 41 branch ca-certificates commit ea529bea8d6f00da8edfa62c87d115bc023b4b67, update-ca-trust.8.txt lines 97 to 99 (checked October 2026): https://src.fedoraproject.org/rpms/ca-certificates/blob/ea529bea8d6f00da8edfa62c87d115bc023b4b67/f/update-ca-trust.8.txt#_97 ; QUICK HELP 1 specifies a simple PEM or DER certificate, /etc/pki/ca-trust/source/anchors/ and update-ca-trust extract, as the cited rawhide lines do.
- Fedora 42 branch ca-certificates commit f00d2386f44d6dbcabc18becf7843c789584cfbc, update-ca-trust.8.txt lines 97 to 99 (checked October 2026): https://src.fedoraproject.org/rpms/ca-certificates/blob/f00d2386f44d6dbcabc18becf7843c789584cfbc/f/update-ca-trust.8.txt#_97 ; QUICK HELP 1 specifies a simple PEM or DER certificate, /etc/pki/ca-trust/source/anchors/ and update-ca-trust extract, as the cited rawhide lines do.
- Fedora 43 branch ca-certificates commit e73db0bb0458f65d530ae5901de2be73f7d7fb80, update-ca-trust.8.txt lines 97 to 99 (checked October 2026): https://src.fedoraproject.org/rpms/ca-certificates/blob/e73db0bb0458f65d530ae5901de2be73f7d7fb80/f/update-ca-trust.8.txt#_97 ; QUICK HELP 1 specifies a simple PEM or DER certificate, /etc/pki/ca-trust/source/anchors/ and update-ca-trust extract, as the cited rawhide lines do.
- Ubuntu resolute update-ca-certificates (checked October 2026): https://manpages.ubuntu.com/manpages/resolute/man8/update-ca-certificates.8.html ; "Furthermore, all certificates with a .crt extension found below /usr/local/share/ca-certificates are also included and implicitly trusted." and "Then run update-ca-certificates to merge the new certificates into the existing machine store at /etc/ssl/certs."
- RHEL 8 shared system certificates, section 3.2 "Adding new certificates to the system-wide truststore" (checked October 2026): https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html/securing_networks/using-shared-system-certificates_securing-networks#adding-new-certificates_using-shared-system-certificates ; "copy the certificate file to the /usr/share/pki/ca-trust-source/anchors/ or /etc/pki/ca-trust/source/anchors/ directory" and then "use the update-ca-trust command", shown as update-ca-trust extract.
- CentOS Stream 9, not RHEL, ca-certificates commit 848a7831862d78a087c8f5d2284ce603f20ed42f, update-ca-trust.8.txt lines 97 to 99 (checked October 2026): https://gitlab.com/redhat/centos-stream/rpms/ca-certificates/-/blob/848a7831862d78a087c8f5d2284ce603f20ed42f/update-ca-trust.8.txt#L97-L99 ; QUICK HELP 1 specifies a simple PEM or DER certificate, /etc/pki/ca-trust/source/anchors/ and update-ca-trust extract.
- Fedora 44 branch ca-certificates commit 1ccf8e36dcf991db7ae4a4220c1612d1f43d96ec, update-ca-trust.8.txt lines 97 to 99 (checked October 2026): https://src.fedoraproject.org/rpms/ca-certificates/blob/1ccf8e36dcf991db7ae4a4220c1612d1f43d96ec/f/update-ca-trust.8.txt#_97 ; QUICK HELP 1 specifies a simple PEM or DER certificate, /etc/pki/ca-trust/source/anchors/ and update-ca-trust extract.
- Fedora 45 branch, release status not established by this guide, ca-certificates commit 3e42eeb6c71e1dd7c126a90a4811ccbe5f79fed7, update-ca-trust.8.txt lines 97 to 99 (checked October 2026): https://src.fedoraproject.org/rpms/ca-certificates/blob/3e42eeb6c71e1dd7c126a90a4811ccbe5f79fed7/f/update-ca-trust.8.txt#_97 ; QUICK HELP 1 specifies a simple PEM or DER certificate, /etc/pki/ca-trust/source/anchors/ and update-ca-trust extract.
- GNU coreutils v9.7 `chmod` syntax (checked October 2026): https://github.com/coreutils/coreutils/blob/v9.7/doc/coreutils.texi#L11937-L11942
- GNU coreutils v9.7 mode argument (checked October 2026): https://github.com/coreutils/coreutils/blob/v9.7/doc/coreutils.texi#L11967-L11968
- GNU coreutils v9.7 `chown` owner and group (checked October 2026): https://github.com/coreutils/coreutils/blob/v9.7/doc/coreutils.texi#L11614-L11622
- GNU coreutils v9.7 numeric mode definition (checked October 2026): https://github.com/coreutils/coreutils/blob/v9.7/doc/perm.texi#L492-L535
- Node.js v24.22.0 `NODE_TLS_REJECT_UNAUTHORIZED` (checked October 2026): https://github.com/nodejs/node/blob/v24.22.0/doc/api/cli.md#L3940-L3944
- Node.js v24.22.0 `tls.connect` client `rejectUnauthorized` (checked October 2026): https://github.com/nodejs/node/blob/v24.22.0/doc/api/tls.md#L1786-L1789
- Node.js v24.22.0 `tls.createServer` `rejectUnauthorized` and `requestCert` (checked October 2026): https://github.com/nodejs/node/blob/v24.22.0/doc/api/tls.md#L2250-L2255


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- openssl: OpenSSL documentation (rolling) (unknown)
- mkcert: mkcert (unknown)
- requests: Requests TLS documentation (v2.32.3)
- git: Git ignore documentation (v2.43.0)
- curl-source: curl command documentation (curl-8_12_1)
- node: Node.js extra CA certificates (v22.19.0)
- rfc9525: Service identity (RFC 9525)
- debian-ca: Debian ca-certificates (trixie)
- ubuntu-ca: Ubuntu ca-certificates (noble)
- rhel-ca: RHEL shared system certificates (RHEL 9)
- coreutils: GNU coreutils file permissions (v9.7)
- node-v24: Node.js API documentation (v24.22.0)
- debian-bookworm: Debian ca-certificates (bookworm)
- ubuntu-jammy: Ubuntu ca-certificates (jammy)
- centos-stream-8: CentOS Stream 8 ca-certificates (ad398898923bddb3953d2aa4c8d9d17c901ef3a4)
- centos-stream-10: CentOS Stream 10 ca-certificates (1ab579df1508321342e9ab244fd4ed397ea89b80)
- fedora-rawhide: Fedora rawhide ca-certificates (development branch) (725690846ee1ae1cd46e62c3a336c84820390d27)
- debian-bullseye: Debian ca-certificates (bullseye)
- ubuntu-focal: Ubuntu ca-certificates (focal)
- fedora-41: Fedora 41 ca-certificates (ea529bea8d6f00da8edfa62c87d115bc023b4b67)
- fedora-42: Fedora 42 ca-certificates (f00d2386f44d6dbcabc18becf7843c789584cfbc)
- fedora-43: Fedora 43 ca-certificates (e73db0bb0458f65d530ae5901de2be73f7d7fb80)
- ubuntu-resolute: Ubuntu ca-certificates (resolute)
- rhel-8: RHEL shared system certificates (RHEL 8)
- centos-stream-9: CentOS Stream 9 ca-certificates (848a7831862d78a087c8f5d2284ce603f20ed42f)
- fedora-44: Fedora 44 ca-certificates (1ccf8e36dcf991db7ae4a4220c1612d1f43d96ec)
- fedora-45: Fedora 45 ca-certificates (branch) (3e42eeb6c71e1dd7c126a90a4811ccbe5f79fed7)

Claims (full source mapping in the JSON block below):

- trust-scope (REASONED; openssl, mkcert): Self-signed TLS encrypts transit but needs explicit client trust and triggers browser warnings; the guide prefers publicly trusted certificates for browser users and external parties.
- rsa-certificate (REASONED; openssl): OpenSSL 3.0 or later generates an RSA 4096-bit self-signed certificate with SHA-256, 365-day validity, an unencrypted key and the shown subject and extensions.
- ec-certificate (REASONED; openssl): Generate a prime256v1 EC key first, then a SHA-256 self-signed certificate with 365-day validity and the shown subject and extensions; the guide describes ECDSA as smaller and faster.
- san (REASONED; openssl, rfc9525): SAN must cover every client DNS name and IP (this guide's requirement, based on RFC 9525's matching rules); replace the documentation IP or omit IP entries for name-only access. RFC 9525 requires each DNS label to match except under its wildcard rule; an IP-ID reference identifier MUST exactly match an iPAddress subjectAltName entry. It forbids the subject Common Name as a service identifier.
- san-mismatch (REASONED; rfc9525): When no presented identifier matches, RFC 9525 says an automated client SHOULD terminate; a configured exception MUST NOT disable this control by default. A human-facing client SHOULD warn and terminate but MAY offer advanced users an override. RFC 9525's ad hoc pinning provision says such pinning SHOULD NOT restrict future connections to only the pinned certificate.
- leaf-constraint (REASONED; openssl): Set basicConstraints=critical,CA:FALSE because the stated stock req -x509 configuration otherwise marks a trusted certificate CA:TRUE, allowing its unencrypted server key to sign for any name.
- extension-history (REASONED; openssl): The command-line extension override relies on OpenSSL 3.0 or later; the guide says end-of-life 1.1.1 instead emits a duplicate invalid extension.
- unencrypted-key (REASONED; openssl): -noenc leaves the key unencrypted for unattended startup; -nodes is the pre-3.0 spelling, still accepted but deprecated. Protect the key with permissions.
- expiry (REASONED; openssl): Track the -days expiry with a calendar or monitoring; self-signed certificates do not renew themselves.
- key-permissions (REASONED; openssl, coreutils): This guide advises chmod 600 and service-user ownership for server.key; GNU coreutils v9.7 documents chmod's mode changes and chown's owner/group changes, not that advice. Mode 600's owner read/write and no group/other permissions are this guide's reading of GNU coreutils v9.7's Numeric Modes definition in doc/perm.texi.
- key-compromise (REASONED; openssl, git): Never commit private keys; ignore *.key and *.pem before generation in a repository and regenerate keys committed or pasted into chat.
- mkcert (REASONED; mkcert): mkcert -install creates and trusts a local CA; mkcert issues certificates for the listed development DNS names and IPs.
- mkcert-custody (REASONED; mkcert): Use mkcert only for development; its CA key can sign for any name, must not leave the developer's machine and must not serve real users.
- debian-trust (REASONED; mkcert, debian-ca, ubuntu-ca, debian-bookworm, ubuntu-jammy, debian-bullseye, ubuntu-focal, ubuntu-resolute): Install app-internal.crt under /usr/local/share/ca-certificates and run update-ca-certificates on Debian trixie/bookworm/bullseye and Ubuntu resolute/noble/jammy/focal; other Debian/Ubuntu releases remain this guide's assessment without release-specific citations.
- rhel-trust (REASONED; mkcert, rhel-ca, centos-stream-8, centos-stream-10, fedora-rawhide, fedora-41, fedora-42, fedora-43, rhel-8, centos-stream-9, fedora-44, fedora-45): Install app-internal.crt under /etc/pki/ca-trust/source/anchors and run update-ca-trust extract: RHEL 8/9 are cited; the CentOS Stream 8/9/10 (not RHEL), Fedora 41/42/43/44, Fedora 45 branch (release unestablished) and rawhide (development, not a release) manuals give this for simple PEM/DER certificates. Other RHEL (including 10), Fedora and CentOS Stream releases remain this guide's assessment.
- curl-trust (REASONED; openssl, curl-source): curl --cacert server.crt supplies explicit trust for app.internal.
- requests-trust (REASONED; openssl, requests): REQUESTS_CA_BUNDLE supplies the certificate path to Python requests.
- node-trust (REASONED; mkcert, node): NODE_EXTRA_CA_CERTS supplies additional client trust to Node.js.
- verification-bypasses (REASONED; openssl, requests, curl-source, node-v24): Do not commit curl -k, verify=False, rejectUnauthorized: false or NODE_TLS_REJECT_UNAUTHORIZED=0. Node.js v24.22.0 scopes the bypasses to process-environment TLS validation, client-connection server verification or server rejection with requestCert=true; accepting attacker certificates and persistence into production are this guide's assessment.
- verify-extensions (DEMONSTRATED; openssl): Inspect x509 output for SAN coverage and CA:FALSE, not its exit status: it can exit 0 with no SAN.
- verify-tls (REASONED; openssl): The app.internal:443 s_client check supplies SNI, hostname checking, verification errors and CAfile; a pass prints Verification: OK, Verified peername: app.internal and return code 0, and exits 0.
- verify-failures (REASONED; openssl): Without -verify_hostname the name is ignored; without -verify_return_error a verification failure can still complete the handshake and exit 0. Both flags make name or trust failures exit nonzero; wrong name reports code 62.
- verify-identity (REASONED; openssl): Use -verify_ip for IP identities; -verify_hostname can fall back to CN without a DNS SAN, even with an IP SAN, so CN-only or IP-only certificates can pass hostname checks.
- verify-store (REASONED; openssl, mkcert, curl-source): Explicit -CAfile proves certificate and name, not the system-store installation; test each normally configured client separately, expecting plain curl without --cacert to fail before trust installation and succeed after.
- trust-limits (REASONED; openssl, mkcert): Self-signed certificates have no revocation or third-party accountability and need manual trust distribution; move beyond them as the audience grows and retain authentication.

````json
{
  "schema": 1,
  "checked": "2026-10-21",
  "documentation_checked": "2026-09",
  "body_sha256": "101fa481026d71d13f0fcebbfd457d2978252b690e8344173cf40375c2a88869",
  "components": {
    "openssl": {
      "name": "OpenSSL documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s211b1e6e4aa4": "https://docs.openssl.org/",
        "s581d7ad32359": "https://docs.openssl.org/master/man1/openssl-s_client/",
        "se5d70578564e": "https://docs.openssl.org/master/man1/openssl-verification-options/"
      }
    },
    "mkcert": {
      "name": "mkcert",
      "basis": "unknown",
      "sources": {
        "s41ae17dba4ce": "https://github.com/FiloSottile/mkcert"
      }
    },
    "requests": {
      "name": "Requests TLS documentation",
      "basis": "v2.32.3",
      "sources": {
        "s21c6be6f6df4": "https://github.com/psf/requests/blob/v2.32.3/docs/user/advanced.rst#L238-L239",
        "scff02f87cf30": "https://github.com/psf/requests/blob/v2.32.3/docs/user/advanced.rst#L246-L250"
      }
    },
    "git": {
      "name": "Git ignore documentation",
      "basis": "v2.43.0",
      "sources": {
        "sf961a2e5b8e1": "https://github.com/git/git/blob/v2.43.0/Documentation/gitignore.txt#L15-L18"
      }
    },
    "curl-source": {
      "name": "curl command documentation",
      "basis": "curl-8_12_1",
      "sources": {
        "s19ed21fc98f8": "https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/cacert.md#L21-L24",
        "s60820cd231e1": "https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/insecure.md#L21-L28"
      }
    },
    "node": {
      "name": "Node.js extra CA certificates",
      "basis": "v22.19.0",
      "sources": {
        "s402034f5dcea": "https://github.com/nodejs/node/blob/v22.19.0/doc/api/cli.md#L3234-L3238"
      }
    },
    "rfc9525": {
      "name": "Service identity",
      "basis": "RFC 9525",
      "sources": {
        "s8dcb5fcc7802": "https://www.rfc-editor.org/rfc/rfc9525.html#section-2",
        "s4afb46847ce6": "https://www.rfc-editor.org/rfc/rfc9525.html#section-6.2",
        "s31c00ddbdfa5": "https://www.rfc-editor.org/rfc/rfc9525.html#section-6.3",
        "s416ff7327342": "https://www.rfc-editor.org/rfc/rfc9525.html#section-6.4",
        "s8bb6a7aa9400": "https://www.rfc-editor.org/rfc/rfc9525.html#section-6.6"
      }
    },
    "debian-ca": {
      "name": "Debian ca-certificates",
      "basis": "trixie",
      "sources": {
        "s99e100121493": "https://manpages.debian.org/trixie/ca-certificates/update-ca-certificates.8.en.html#DESCRIPTION"
      }
    },
    "ubuntu-ca": {
      "name": "Ubuntu ca-certificates",
      "basis": "noble",
      "sources": {
        "s4c3728cc6c12": "https://manpages.ubuntu.com/manpages/noble/man8/update-ca-certificates.8.html#description"
      }
    },
    "rhel-ca": {
      "name": "RHEL shared system certificates",
      "basis": "RHEL 9",
      "sources": {
        "s876e668e7116": "https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/securing_networks/using-shared-system-certificates_securing-networks#adding-new-certificates_using-shared-system-certificates"
      }
    },
    "coreutils": {
      "name": "GNU coreutils file permissions",
      "basis": "v9.7",
      "sources": {
        "s876896563d01": "https://github.com/coreutils/coreutils/blob/v9.7/doc/coreutils.texi#L11937-L11942",
        "s881033f651b3": "https://github.com/coreutils/coreutils/blob/v9.7/doc/coreutils.texi#L11967-L11968",
        "s9ab719f6189b": "https://github.com/coreutils/coreutils/blob/v9.7/doc/coreutils.texi#L11614-L11622",
        "s0ef955010eb3": "https://github.com/coreutils/coreutils/blob/v9.7/doc/perm.texi#L492-L535"
      }
    },
    "node-v24": {
      "name": "Node.js API documentation",
      "basis": "v24.22.0",
      "sources": {
        "sbfee17929443": "https://github.com/nodejs/node/blob/v24.22.0/doc/api/cli.md#L3940-L3944",
        "s684a71cf8b6e": "https://github.com/nodejs/node/blob/v24.22.0/doc/api/tls.md#L1786-L1789",
        "s025a5157269c": "https://github.com/nodejs/node/blob/v24.22.0/doc/api/tls.md#L2250-L2255"
      }
    },
    "debian-bookworm": {
      "name": "Debian ca-certificates",
      "basis": "bookworm",
      "sources": {
        "sa5e706846110": "https://manpages.debian.org/bookworm/ca-certificates/update-ca-certificates.8.en.html"
      }
    },
    "ubuntu-jammy": {
      "name": "Ubuntu ca-certificates",
      "basis": "jammy",
      "sources": {
        "s73a246e6ccfa": "https://manpages.ubuntu.com/manpages/jammy/man8/update-ca-certificates.8.html"
      }
    },
    "centos-stream-8": {
      "name": "CentOS Stream 8 ca-certificates",
      "basis": "ad398898923bddb3953d2aa4c8d9d17c901ef3a4",
      "sources": {
        "s448b09073b79": "https://gitlab.com/redhat/centos-stream/rpms/ca-certificates/-/blob/ad398898923bddb3953d2aa4c8d9d17c901ef3a4/update-ca-trust.8.txt#L97-L99"
      }
    },
    "centos-stream-10": {
      "name": "CentOS Stream 10 ca-certificates",
      "basis": "1ab579df1508321342e9ab244fd4ed397ea89b80",
      "sources": {
        "s2862e6522c85": "https://gitlab.com/redhat/centos-stream/rpms/ca-certificates/-/blob/1ab579df1508321342e9ab244fd4ed397ea89b80/update-ca-trust.8.txt#L97-L99"
      }
    },
    "fedora-rawhide": {
      "name": "Fedora rawhide ca-certificates (development branch)",
      "basis": "725690846ee1ae1cd46e62c3a336c84820390d27",
      "sources": {
        "s70fd69620a8b": "https://src.fedoraproject.org/rpms/ca-certificates/blob/725690846ee1ae1cd46e62c3a336c84820390d27/f/update-ca-trust.8.txt#_97"
      }
    },
    "debian-bullseye": {
      "name": "Debian ca-certificates",
      "basis": "bullseye",
      "sources": {
        "s2eedd95a8996": "https://manpages.debian.org/bullseye/ca-certificates/update-ca-certificates.8.en.html"
      }
    },
    "ubuntu-focal": {
      "name": "Ubuntu ca-certificates",
      "basis": "focal",
      "sources": {
        "s4ddde36c49dc": "https://manpages.ubuntu.com/manpages/focal/man8/update-ca-certificates.8.html"
      }
    },
    "fedora-41": {
      "name": "Fedora 41 ca-certificates",
      "basis": "ea529bea8d6f00da8edfa62c87d115bc023b4b67",
      "sources": {
        "s15529d5b4f48": "https://src.fedoraproject.org/rpms/ca-certificates/blob/ea529bea8d6f00da8edfa62c87d115bc023b4b67/f/update-ca-trust.8.txt#_97"
      }
    },
    "fedora-42": {
      "name": "Fedora 42 ca-certificates",
      "basis": "f00d2386f44d6dbcabc18becf7843c789584cfbc",
      "sources": {
        "sedab1dd6dee7": "https://src.fedoraproject.org/rpms/ca-certificates/blob/f00d2386f44d6dbcabc18becf7843c789584cfbc/f/update-ca-trust.8.txt#_97"
      }
    },
    "fedora-43": {
      "name": "Fedora 43 ca-certificates",
      "basis": "e73db0bb0458f65d530ae5901de2be73f7d7fb80",
      "sources": {
        "sf4a64ff0a939": "https://src.fedoraproject.org/rpms/ca-certificates/blob/e73db0bb0458f65d530ae5901de2be73f7d7fb80/f/update-ca-trust.8.txt#_97"
      }
    },
    "ubuntu-resolute": {
      "name": "Ubuntu ca-certificates",
      "basis": "resolute",
      "sources": {
        "sec84181fd9fa": "https://manpages.ubuntu.com/manpages/resolute/man8/update-ca-certificates.8.html"
      }
    },
    "rhel-8": {
      "name": "RHEL shared system certificates",
      "basis": "RHEL 8",
      "sources": {
        "s9f44bb7b2935": "https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html/securing_networks/using-shared-system-certificates_securing-networks#adding-new-certificates_using-shared-system-certificates"
      }
    },
    "centos-stream-9": {
      "name": "CentOS Stream 9 ca-certificates",
      "basis": "848a7831862d78a087c8f5d2284ce603f20ed42f",
      "sources": {
        "s6289706376f0": "https://gitlab.com/redhat/centos-stream/rpms/ca-certificates/-/blob/848a7831862d78a087c8f5d2284ce603f20ed42f/update-ca-trust.8.txt#L97-L99"
      }
    },
    "fedora-44": {
      "name": "Fedora 44 ca-certificates",
      "basis": "1ccf8e36dcf991db7ae4a4220c1612d1f43d96ec",
      "sources": {
        "sd111db8cd76e": "https://src.fedoraproject.org/rpms/ca-certificates/blob/1ccf8e36dcf991db7ae4a4220c1612d1f43d96ec/f/update-ca-trust.8.txt#_97"
      }
    },
    "fedora-45": {
      "name": "Fedora 45 ca-certificates (branch)",
      "basis": "3e42eeb6c71e1dd7c126a90a4811ccbe5f79fed7",
      "sources": {
        "s28e014a1e5b3": "https://src.fedoraproject.org/rpms/ca-certificates/blob/3e42eeb6c71e1dd7c126a90a4811ccbe5f79fed7/f/update-ca-trust.8.txt#_97"
      }
    }
  },
  "claims": {
    "trust-scope": {"text": "Self-signed TLS encrypts transit but needs explicit client trust and triggers browser warnings; the guide prefers publicly trusted certificates for browser users and external parties.", "components": ["openssl", "mkcert"], "sources": ["openssl:s211b1e6e4aa4", "mkcert:s41ae17dba4ce"], "status": "REASONED"},
    "rsa-certificate": {"text": "OpenSSL 3.0 or later generates an RSA 4096-bit self-signed certificate with SHA-256, 365-day validity, an unencrypted key and the shown subject and extensions.", "components": ["openssl"], "sources": ["openssl:s211b1e6e4aa4"], "status": "REASONED"},
    "ec-certificate": {"text": "Generate a prime256v1 EC key first, then a SHA-256 self-signed certificate with 365-day validity and the shown subject and extensions; the guide describes ECDSA as smaller and faster.", "components": ["openssl"], "sources": ["openssl:s211b1e6e4aa4"], "status": "REASONED"},
    "san": {"text": "SAN must cover every client DNS name and IP (this guide's requirement, based on RFC 9525's matching rules); replace the documentation IP or omit IP entries for name-only access. RFC 9525 requires each DNS label to match except under its wildcard rule; an IP-ID reference identifier MUST exactly match an iPAddress subjectAltName entry. It forbids the subject Common Name as a service identifier.", "components": ["openssl", "rfc9525"], "sources": ["openssl:se5d70578564e", "rfc9525:s8dcb5fcc7802", "rfc9525:s4afb46847ce6", "rfc9525:s31c00ddbdfa5", "rfc9525:s416ff7327342"], "status": "REASONED"},
    "san-mismatch": {"text": "When no presented identifier matches, RFC 9525 says an automated client SHOULD terminate; a configured exception MUST NOT disable this control by default. A human-facing client SHOULD warn and terminate but MAY offer advanced users an override. RFC 9525's ad hoc pinning provision says such pinning SHOULD NOT restrict future connections to only the pinned certificate.", "components": ["rfc9525"], "sources": ["rfc9525:s8bb6a7aa9400"], "status": "REASONED"},
    "leaf-constraint": {"text": "Set basicConstraints=critical,CA:FALSE because the stated stock req -x509 configuration otherwise marks a trusted certificate CA:TRUE, allowing its unencrypted server key to sign for any name.", "components": ["openssl"], "sources": ["openssl:s211b1e6e4aa4"], "status": "REASONED"},
    "extension-history": {"text": "The command-line extension override relies on OpenSSL 3.0 or later; the guide says end-of-life 1.1.1 instead emits a duplicate invalid extension.", "components": ["openssl"], "sources": ["openssl:s211b1e6e4aa4"], "status": "REASONED"},
    "unencrypted-key": {"text": "-noenc leaves the key unencrypted for unattended startup; -nodes is the pre-3.0 spelling, still accepted but deprecated. Protect the key with permissions.", "components": ["openssl"], "sources": ["openssl:s211b1e6e4aa4"], "status": "REASONED"},
    "expiry": {"text": "Track the -days expiry with a calendar or monitoring; self-signed certificates do not renew themselves.", "components": ["openssl"], "sources": ["openssl:s211b1e6e4aa4"], "status": "REASONED"},
    "key-permissions": {"text": "This guide advises chmod 600 and service-user ownership for server.key; GNU coreutils v9.7 documents chmod's mode changes and chown's owner/group changes, not that advice. Mode 600's owner read/write and no group/other permissions are this guide's reading of GNU coreutils v9.7's Numeric Modes definition in doc/perm.texi.", "components": ["openssl", "coreutils"], "sources": ["openssl:s211b1e6e4aa4", "coreutils:s876896563d01", "coreutils:s881033f651b3", "coreutils:s9ab719f6189b", "coreutils:s0ef955010eb3"], "status": "REASONED"},
    "key-compromise": {"text": "Never commit private keys; ignore *.key and *.pem before generation in a repository and regenerate keys committed or pasted into chat.", "components": ["openssl", "git"], "sources": ["openssl:s211b1e6e4aa4", "git:sf961a2e5b8e1"], "status": "REASONED"},
    "mkcert": {"text": "mkcert -install creates and trusts a local CA; mkcert issues certificates for the listed development DNS names and IPs.", "components": ["mkcert"], "sources": ["mkcert:s41ae17dba4ce"], "status": "REASONED"},
    "mkcert-custody": {"text": "Use mkcert only for development; its CA key can sign for any name, must not leave the developer's machine and must not serve real users.", "components": ["mkcert"], "sources": ["mkcert:s41ae17dba4ce"], "status": "REASONED"},
    "debian-trust": {"text": "Install app-internal.crt under /usr/local/share/ca-certificates and run update-ca-certificates on Debian trixie/bookworm/bullseye and Ubuntu resolute/noble/jammy/focal; other Debian/Ubuntu releases remain this guide's assessment without release-specific citations.", "components": ["mkcert", "debian-ca", "ubuntu-ca", "debian-bookworm", "ubuntu-jammy", "debian-bullseye", "ubuntu-focal", "ubuntu-resolute"], "sources": ["mkcert:s41ae17dba4ce", "debian-ca:s99e100121493", "ubuntu-ca:s4c3728cc6c12", "debian-bookworm:sa5e706846110", "ubuntu-jammy:s73a246e6ccfa", "debian-bullseye:s2eedd95a8996", "ubuntu-focal:s4ddde36c49dc", "ubuntu-resolute:sec84181fd9fa"], "status": "REASONED"},
    "rhel-trust": {"text": "Install app-internal.crt under /etc/pki/ca-trust/source/anchors and run update-ca-trust extract: RHEL 8/9 are cited; the CentOS Stream 8/9/10 (not RHEL), Fedora 41/42/43/44, Fedora 45 branch (release unestablished) and rawhide (development, not a release) manuals give this for simple PEM/DER certificates. Other RHEL (including 10), Fedora and CentOS Stream releases remain this guide's assessment.", "components": ["mkcert", "rhel-ca", "centos-stream-8", "centos-stream-10", "fedora-rawhide", "fedora-41", "fedora-42", "fedora-43", "rhel-8", "centos-stream-9", "fedora-44", "fedora-45"], "sources": ["mkcert:s41ae17dba4ce", "rhel-ca:s876e668e7116", "centos-stream-8:s448b09073b79", "centos-stream-10:s2862e6522c85", "fedora-rawhide:s70fd69620a8b", "fedora-41:s15529d5b4f48", "fedora-42:sedab1dd6dee7", "fedora-43:sf4a64ff0a939", "rhel-8:s9f44bb7b2935", "centos-stream-9:s6289706376f0", "fedora-44:sd111db8cd76e", "fedora-45:s28e014a1e5b3"], "status": "REASONED"},
    "curl-trust": {"text": "curl --cacert server.crt supplies explicit trust for app.internal.", "components": ["openssl", "curl-source"], "sources": ["openssl:se5d70578564e", "curl-source:s19ed21fc98f8"], "status": "REASONED"},
    "requests-trust": {"text": "REQUESTS_CA_BUNDLE supplies the certificate path to Python requests.", "components": ["openssl", "requests"], "sources": ["openssl:se5d70578564e", "requests:s21c6be6f6df4"], "status": "REASONED"},
    "node-trust": {"text": "NODE_EXTRA_CA_CERTS supplies additional client trust to Node.js.", "components": ["mkcert", "node"], "sources": ["mkcert:s41ae17dba4ce", "node:s402034f5dcea"], "status": "REASONED"},
    "verification-bypasses": {"text": "Do not commit curl -k, verify=False, rejectUnauthorized: false or NODE_TLS_REJECT_UNAUTHORIZED=0. Node.js v24.22.0 scopes the bypasses to process-environment TLS validation, client-connection server verification or server rejection with requestCert=true; accepting attacker certificates and persistence into production are this guide's assessment.", "components": ["openssl", "requests", "curl-source", "node-v24"], "sources": ["openssl:se5d70578564e", "requests:scff02f87cf30", "curl-source:s60820cd231e1", "node-v24:sbfee17929443", "node-v24:s684a71cf8b6e", "node-v24:s025a5157269c"], "status": "REASONED"},
    "verify-extensions": {"text": "Inspect x509 output for SAN coverage and CA:FALSE, not its exit status: it can exit 0 with no SAN.", "components": ["openssl"], "sources": ["openssl:s211b1e6e4aa4"], "status": "DEMONSTRATED", "evidence": "On 2026-10-05 in private /dev/shm scratch, OpenSSL 3.5.5 ran the printed x509 command on three disposable one-day RSA certificates. Missing-SAN and CA:TRUE fixtures each exited 0 but lacked the required SAN or leaf constraint; the fixed fixture also exited 0 and printed DNS:app.internal, IP Address:127.0.0.1 and critical CA:FALSE. Subject and validity dates printed for all three.", "verify": [1]},
    "verify-tls": {"text": "The app.internal:443 s_client check supplies SNI, hostname checking, verification errors and CAfile; a pass prints Verification: OK, Verified peername: app.internal and return code 0, and exits 0.", "components": ["openssl"], "sources": ["openssl:s581d7ad32359", "openssl:se5d70578564e"], "status": "REASONED", "verify": [2]},
    "verify-failures": {"text": "Without -verify_hostname the name is ignored; without -verify_return_error a verification failure can still complete the handshake and exit 0. Both flags make name or trust failures exit nonzero; wrong name reports code 62.", "components": ["openssl"], "sources": ["openssl:s581d7ad32359", "openssl:se5d70578564e"], "status": "REASONED", "verify": [2]},
    "verify-identity": {"text": "Use -verify_ip for IP identities; -verify_hostname can fall back to CN without a DNS SAN, even with an IP SAN, so CN-only or IP-only certificates can pass hostname checks.", "components": ["openssl"], "sources": ["openssl:se5d70578564e"], "status": "REASONED", "verify": [2]},
    "verify-store": {"text": "Explicit -CAfile proves certificate and name, not the system-store installation; test each normally configured client separately, expecting plain curl without --cacert to fail before trust installation and succeed after.", "components": ["openssl", "mkcert", "curl-source"], "sources": ["openssl:s581d7ad32359", "mkcert:s41ae17dba4ce", "curl-source:s19ed21fc98f8", "curl-source:s60820cd231e1"], "status": "REASONED", "verify": [2]},
    "trust-limits": {"text": "Self-signed certificates have no revocation or third-party accountability and need manual trust distribution; move beyond them as the audience grows and retain authentication.", "components": ["openssl", "mkcert"], "sources": ["openssl:s211b1e6e4aa4", "mkcert:s41ae17dba4ce"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
