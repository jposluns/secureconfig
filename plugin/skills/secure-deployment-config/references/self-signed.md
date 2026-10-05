---
version_basis: {
  "schema": 1,
  "checked": "2026-10-05",
  "documentation_checked": "2026-09",
  "body_sha256": "dd01520941958a931b14adbf4f0ce2664b58693f02a68c1942574d02b30d09ed",
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
    }
  },
  "claims": {
    "trust-scope": {"text": "Self-signed TLS encrypts transit but needs explicit client trust and triggers browser warnings; the guide prefers publicly trusted certificates for browser users and external parties.", "components": ["openssl", "mkcert"], "sources": ["openssl:s211b1e6e4aa4", "mkcert:s41ae17dba4ce"], "status": "REASONED"},
    "rsa-certificate": {"text": "OpenSSL 3.0 or later generates an RSA 4096-bit self-signed certificate with SHA-256, 365-day validity, an unencrypted key and the shown subject and extensions.", "components": ["openssl"], "sources": ["openssl:s211b1e6e4aa4"], "status": "REASONED"},
    "ec-certificate": {"text": "Generate a prime256v1 EC key first, then a SHA-256 self-signed certificate with 365-day validity and the shown subject and extensions; the guide describes ECDSA as smaller and faster.", "components": ["openssl"], "sources": ["openssl:s211b1e6e4aa4"], "status": "REASONED"},
    "san": {"text": "SAN must cover every client DNS name and IP; replace the documentation IP or omit IP entries for name-only access. RFC 9525 clients reject a missing matching SAN; that RFC is named but not linked in Sources.", "components": ["openssl"], "sources": ["openssl:se5d70578564e"], "status": "REASONED"},
    "leaf-constraint": {"text": "Set basicConstraints=critical,CA:FALSE because the stated stock req -x509 configuration otherwise marks a trusted certificate CA:TRUE, allowing its unencrypted server key to sign for any name.", "components": ["openssl"], "sources": ["openssl:s211b1e6e4aa4"], "status": "REASONED"},
    "extension-history": {"text": "The command-line extension override relies on OpenSSL 3.0 or later; the guide says end-of-life 1.1.1 instead emits a duplicate invalid extension.", "components": ["openssl"], "sources": ["openssl:s211b1e6e4aa4"], "status": "REASONED"},
    "unencrypted-key": {"text": "-noenc leaves the key unencrypted for unattended startup; -nodes is the pre-3.0 spelling, still accepted but deprecated. Protect the key with permissions.", "components": ["openssl"], "sources": ["openssl:s211b1e6e4aa4"], "status": "REASONED"},
    "expiry": {"text": "Track the -days expiry with a calendar or monitoring; self-signed certificates do not renew themselves.", "components": ["openssl"], "sources": ["openssl:s211b1e6e4aa4"], "status": "REASONED"},
    "key-permissions": {"text": "chmod 600 and service-user ownership protect server.key; filesystem command sources and versions are not recorded.", "components": ["openssl"], "sources": ["openssl:s211b1e6e4aa4"], "status": "REASONED"},
    "key-compromise": {"text": "Never commit private keys; ignore *.key and *.pem before generation in a repository and regenerate keys committed or pasted into chat. Git-specific sources are not recorded.", "components": ["openssl", "git"], "sources": ["openssl:s211b1e6e4aa4", "git:sf961a2e5b8e1"], "status": "REASONED"},
    "mkcert": {"text": "mkcert -install creates and trusts a local CA; mkcert issues certificates for the listed development DNS names and IPs.", "components": ["mkcert"], "sources": ["mkcert:s41ae17dba4ce"], "status": "REASONED"},
    "mkcert-custody": {"text": "Use mkcert only for development; its CA key can sign for any name, must not leave the developer's machine and must not serve real users.", "components": ["mkcert"], "sources": ["mkcert:s41ae17dba4ce"], "status": "REASONED"},
    "debian-trust": {"text": "Install app-internal.crt under /usr/local/share/ca-certificates and run update-ca-certificates on Debian/Ubuntu; a platform-specific Sources entry is absent.", "components": ["mkcert"], "sources": ["mkcert:s41ae17dba4ce"], "status": "REASONED"},
    "rhel-trust": {"text": "Install app-internal.crt under /etc/pki/ca-trust/source/anchors and run update-ca-trust on RHEL/Fedora; a platform-specific Sources entry is absent.", "components": ["mkcert"], "sources": ["mkcert:s41ae17dba4ce"], "status": "REASONED"},
    "curl-trust": {"text": "curl --cacert server.crt supplies explicit trust for app.internal; a curl source and version are not recorded.", "components": ["openssl", "curl-source"], "sources": ["openssl:se5d70578564e", "curl-source:s19ed21fc98f8"], "status": "REASONED"},
    "requests-trust": {"text": "REQUESTS_CA_BUNDLE supplies the certificate path to Python requests; a requests Sources entry and version are absent.", "components": ["openssl", "requests"], "sources": ["openssl:se5d70578564e", "requests:s21c6be6f6df4"], "status": "REASONED"},
    "node-trust": {"text": "NODE_EXTRA_CA_CERTS supplies additional client trust to Node.js; its version is unrecorded.", "components": ["mkcert", "node"], "sources": ["mkcert:s41ae17dba4ce", "node:s402034f5dcea"], "status": "REASONED"},
    "verification-bypasses": {"text": "Do not commit curl -k, verify=False, rejectUnauthorized: false or NODE_TLS_REJECT_UNAUTHORIZED=0; the guide says they disable TLS validation, but tool-specific Sources entries are absent.", "components": ["openssl", "requests", "curl-source"], "sources": ["openssl:se5d70578564e", "requests:scff02f87cf30", "curl-source:s60820cd231e1"], "status": "REASONED"},
    "verify-extensions": {"text": "Inspect x509 output for SAN coverage and CA:FALSE, not its exit status: it can exit 0 with no SAN.", "components": ["openssl"], "sources": ["openssl:s211b1e6e4aa4"], "status": "DEMONSTRATED", "evidence": "On 2026-10-05 in private /dev/shm scratch, OpenSSL 3.5.5 ran the printed x509 command on three disposable one-day RSA certificates. Missing-SAN and CA:TRUE fixtures each exited 0 but lacked the required SAN or leaf constraint; the fixed fixture also exited 0 and printed DNS:app.internal, IP Address:127.0.0.1 and critical CA:FALSE. Subject and validity dates printed for all three.", "verify": [1]},
    "verify-tls": {"text": "The app.internal:443 s_client check supplies SNI, hostname checking, verification errors and CAfile; a pass prints Verification: OK, Verified peername: app.internal and return code 0, and exits 0.", "components": ["openssl"], "sources": ["openssl:s581d7ad32359", "openssl:se5d70578564e"], "status": "REASONED", "verify": [2]},
    "verify-failures": {"text": "Without -verify_hostname the name is ignored; without -verify_return_error a verification failure can still complete the handshake and exit 0. Both flags make name or trust failures exit nonzero; wrong name reports code 62.", "components": ["openssl"], "sources": ["openssl:s581d7ad32359", "openssl:se5d70578564e"], "status": "REASONED", "verify": [2]},
    "verify-identity": {"text": "Use -verify_ip for IP identities; -verify_hostname can fall back to CN without a DNS SAN, even with an IP SAN, so CN-only or IP-only certificates can pass hostname checks.", "components": ["openssl"], "sources": ["openssl:se5d70578564e"], "status": "REASONED", "verify": [2]},
    "verify-store": {"text": "Explicit -CAfile proves certificate and name, not the system-store installation; test each normally configured client separately, expecting plain curl without --cacert to fail before trust installation and succeed after.", "components": ["openssl", "mkcert", "curl-source"], "sources": ["openssl:s581d7ad32359", "mkcert:s41ae17dba4ce", "curl-source:s19ed21fc98f8", "curl-source:s60820cd231e1"], "status": "REASONED", "verify": [2]},
    "trust-limits": {"text": "Self-signed certificates have no revocation or third-party accountability and need manual trust distribution; move beyond them as the audience grows and retain authentication.", "components": ["openssl", "mkcert"], "sources": ["openssl:s211b1e6e4aa4", "mkcert:s41ae17dba4ce"], "status": "REASONED"}
  }
}
---
# Self-signed certificates

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-05; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| trust-scope: Self-signed TLS encrypts transit but needs explicit client trust and triggers browser warnings; the guide prefers publicly trusted certificates for browser users and external parties. | OpenSSL documentation (rolling) unknown; mkcert unknown | REASONED |
| rsa-certificate: OpenSSL 3.0 or later generates an RSA 4096-bit self-signed certificate with SHA-256, 365-day validity, an unencrypted key and the shown subject and extensions. | OpenSSL documentation (rolling) unknown | REASONED |
| ec-certificate: Generate a prime256v1 EC key first, then a SHA-256 self-signed certificate with 365-day validity and the shown subject and extensions; the guide describes ECDSA as smaller and faster. | OpenSSL documentation (rolling) unknown | REASONED |
| san: SAN must cover every client DNS name and IP; replace the documentation IP or omit IP entries for name-only access. RFC 9525 clients reject a missing matching SAN; that RFC is named but not linked in Sources. | OpenSSL documentation (rolling) unknown | REASONED |
| leaf-constraint: Set basicConstraints=critical,CA:FALSE because the stated stock req -x509 configuration otherwise marks a trusted certificate CA:TRUE, allowing its unencrypted server key to sign for any name. | OpenSSL documentation (rolling) unknown | REASONED |
| extension-history: The command-line extension override relies on OpenSSL 3.0 or later; the guide says end-of-life 1.1.1 instead emits a duplicate invalid extension. | OpenSSL documentation (rolling) unknown | REASONED |
| unencrypted-key: -noenc leaves the key unencrypted for unattended startup; -nodes is the pre-3.0 spelling, still accepted but deprecated. Protect the key with permissions. | OpenSSL documentation (rolling) unknown | REASONED |
| expiry: Track the -days expiry with a calendar or monitoring; self-signed certificates do not renew themselves. | OpenSSL documentation (rolling) unknown | REASONED |
| key-permissions: chmod 600 and service-user ownership protect server.key; filesystem command sources and versions are not recorded. | OpenSSL documentation (rolling) unknown | REASONED |
| key-compromise: Never commit private keys; ignore *.key and *.pem before generation in a repository and regenerate keys committed or pasted into chat. Git-specific sources are not recorded. | OpenSSL documentation (rolling) unknown; Git ignore documentation v2.43.0 | REASONED |
| mkcert: mkcert -install creates and trusts a local CA; mkcert issues certificates for the listed development DNS names and IPs. | mkcert unknown | REASONED |
| mkcert-custody: Use mkcert only for development; its CA key can sign for any name, must not leave the developer's machine and must not serve real users. | mkcert unknown | REASONED |
| debian-trust: Install app-internal.crt under /usr/local/share/ca-certificates and run update-ca-certificates on Debian/Ubuntu; a platform-specific Sources entry is absent. | mkcert unknown | REASONED |
| rhel-trust: Install app-internal.crt under /etc/pki/ca-trust/source/anchors and run update-ca-trust on RHEL/Fedora; a platform-specific Sources entry is absent. | mkcert unknown | REASONED |
| curl-trust: curl --cacert server.crt supplies explicit trust for app.internal; a curl source and version are not recorded. | OpenSSL documentation (rolling) unknown; curl command documentation curl-8_12_1 | REASONED |
| requests-trust: REQUESTS_CA_BUNDLE supplies the certificate path to Python requests; a requests Sources entry and version are absent. | OpenSSL documentation (rolling) unknown; Requests TLS documentation v2.32.3 | REASONED |
| node-trust: NODE_EXTRA_CA_CERTS supplies additional client trust to Node.js; its version is unrecorded. | mkcert unknown; Node.js extra CA certificates v22.19.0 | REASONED |
| verification-bypasses: Do not commit curl -k, verify=False, rejectUnauthorized: false or NODE_TLS_REJECT_UNAUTHORIZED=0; the guide says they disable TLS validation, but tool-specific Sources entries are absent. | OpenSSL documentation (rolling) unknown; Requests TLS documentation v2.32.3; curl command documentation curl-8_12_1 | REASONED |
| verify-extensions: Inspect x509 output for SAN coverage and CA:FALSE, not its exit status: it can exit 0 with no SAN. | OpenSSL documentation (rolling) unknown | DEMONSTRATED |
| verify-tls: The app.internal:443 s_client check supplies SNI, hostname checking, verification errors and CAfile; a pass prints Verification: OK, Verified peername: app.internal and return code 0, and exits 0. | OpenSSL documentation (rolling) unknown | REASONED |
| verify-failures: Without -verify_hostname the name is ignored; without -verify_return_error a verification failure can still complete the handshake and exit 0. Both flags make name or trust failures exit nonzero; wrong name reports code 62. | OpenSSL documentation (rolling) unknown | REASONED |
| verify-identity: Use -verify_ip for IP identities; -verify_hostname can fall back to CN without a DNS SAN, even with an IP SAN, so CN-only or IP-only certificates can pass hostname checks. | OpenSSL documentation (rolling) unknown | REASONED |
| verify-store: Explicit -CAfile proves certificate and name, not the system-store installation; test each normally configured client separately, expecting plain curl without --cacert to fail before trust installation and succeed after. | OpenSSL documentation (rolling) unknown; mkcert unknown; curl command documentation curl-8_12_1 | REASONED |
| trust-limits: Self-signed certificates have no revocation or third-party accountability and need manual trust distribution; move beyond them as the audience grows and retain authentication. | OpenSSL documentation (rolling) unknown; mkcert unknown | REASONED |
<!-- version-basis:end -->

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

- The `subjectAltName` list must contain every DNS name and IP address clients will use to reach the service. Modern clients validate SAN entries; a certificate with no matching SAN is rejected by clients that follow RFC 9525, so the SAN is mandatory (some verifiers, including OpenSSL's default, still fall back to the CN, which is why the Verify below confirms the SAN exists rather than trusting a CN). Replace the example `203.0.113.10` (a documentation address from RFC 5737) with your service's real IP, or drop the `IP:` entries if clients reach it only by name.
- `basicConstraints=critical,CA:FALSE` marks the certificate a leaf, not a CA. It matters because section 4 installs the certificate into client trust stores: OpenSSL's stock configuration marks a bare `req -x509` certificate `CA:TRUE`, which in a trust store is a signer for any name, using the unencrypted key that `-noenc` leaves on the server. This override relies on OpenSSL 3.0 or later, where a command-line extension replaces the configuration default; the end-of-life 1.1.1 would instead emit a duplicate, invalid extension.
- `-noenc` (spelled `-nodes` before OpenSSL 3.0, still accepted but deprecated) leaves the key unencrypted so services can start unattended; protect it with file permissions instead.
- Track the `-days` expiry. Nothing renews a self-signed certificate for you; put the date in your calendar or monitoring.

## 2. Protect the private key

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

```bash
# Debian/Ubuntu system trust store
sudo cp server.crt /usr/local/share/ca-certificates/app-internal.crt
sudo update-ca-certificates

# RHEL/Fedora system trust store
sudo cp server.crt /etc/pki/ca-trust/source/anchors/app-internal.crt
sudo update-ca-trust

# Per-tool
curl -q --cacert server.crt https://app.internal/
export REQUESTS_CA_BUNDLE=/path/to/server.crt      # Python requests
export NODE_EXTRA_CA_CERTS=/path/to/server.crt     # Node.js
```

Do not ship `curl -k`, `verify=False`, `rejectUnauthorized: false`, or `NODE_TLS_REJECT_UNAUTHORIZED=0` in committed code. Each of these disables TLS validation entirely, for attacker-controlled certificates as much as for your own, and they reliably survive into production.

## 5. Verify

DEMONSTRATED: following block; local certificate-output inspection only. On 2026-10-05 in private /dev/shm scratch, OpenSSL 3.5.5 ran the printed x509 command on three disposable one-day RSA certificates. Missing-SAN and CA:TRUE fixtures each exited 0 but lacked the required SAN or leaf constraint; the fixed fixture also exited 0 and printed DNS:app.internal, IP Address:127.0.0.1 and critical CA:FALSE. Subject and validity dates printed for all three.

```bash
openssl x509 -in server.crt -noout -subject -dates -ext subjectAltName,basicConstraints
```

REASONED: following block; live TLS identity, failure handling and client-trust checks follow the cited OpenSSL and mkcert documentation. No app.internal service or client trust-store installation was supplied for these checks. The local x509 run above does not demonstrate a handshake or installed trust; expected outcomes and limitations are stated below.

```bash
openssl s_client -connect app.internal:443 -servername app.internal -verify_hostname app.internal -verify_return_error -CAfile server.crt </dev/null
```

A pass prints `Verification: OK`, `Verified peername: app.internal`, and `Verify return code: 0 (ok)`, and the command exits 0. Without `-verify_hostname` the check ignores the name, and without `-verify_return_error` `s_client` reports a failure yet still completes the handshake and exits 0; with both, a name mismatch or an untrusted chain closes the connection and exits non-zero (`Verify return code: 62 (hostname mismatch)` for the wrong name). Read the first command's output rather than its exit status (it exits 0 even with no SAN): confirm a `subjectAltName` covering every name and IP clients use and `basicConstraints` marked `CA:FALSE`, and use `-verify_ip <addr>` to check an IP identity, since `-verify_hostname` falls back to the Common Name whenever the certificate carries no DNS-name SAN entry (even if it has an IP SAN), so a CN-only or IP-only certificate can still pass a hostname check. The `s_client` check supplies trust explicitly with `-CAfile`, so it proves the certificate and name but not that the section-4 trust-store install took effect; confirm that separately from each client with its normal configuration (for the system store, a plain `curl https://app.internal/` with no `--cacert` should fail before `update-ca-certificates` and succeed after).

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
