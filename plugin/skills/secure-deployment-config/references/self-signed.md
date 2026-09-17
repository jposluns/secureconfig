# Self-signed certificates

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

```bash
openssl x509 -in server.crt -noout -subject -dates -ext subjectAltName,basicConstraints
openssl s_client -connect app.internal:443 -servername app.internal -verify_hostname app.internal -verify_return_error -CAfile server.crt </dev/null
```

A pass prints `Verification: OK`, `Verified peername: app.internal`, and `Verify return code: 0 (ok)`, and the command exits 0. Without `-verify_hostname` the check ignores the name, and without `-verify_return_error` `s_client` reports a failure yet still completes the handshake and exits 0; with both, a name mismatch or an untrusted chain closes the connection and exits non-zero (`Verify return code: 62 (hostname mismatch)` for the wrong name). Read the first command's output rather than its exit status (it exits 0 even with no SAN): confirm a `subjectAltName` covering every name and IP clients use and `basicConstraints` marked `CA:FALSE`, and use `-verify_ip <addr>` to check an IP identity, since `-verify_hostname` falls back to the Common Name whenever the certificate carries no DNS-name SAN entry (even if it has an IP SAN), so a CN-only or IP-only certificate can still pass a hostname check. The `s_client` check supplies trust explicitly with `-CAfile`, so it proves the certificate and name but not that the section-4 trust-store install took effect; confirm that separately from each client with its normal configuration (for the system store, a plain `curl https://app.internal/` with no `--cacert` should fail before `update-ca-certificates` and succeed after).

## Limits to plan around

Self-signed certificates have no revocation and no third-party accountability, and trust distribution is manual. When the audience grows beyond a small internal group, move to [free-certificates.md](free-certificates.md) or put the service behind [cloudflare.md](cloudflare.md). Authentication is still required either way: see [authentication.md](authentication.md).

## Sources (checked September 2026)

- OpenSSL documentation: https://docs.openssl.org/ ; `openssl s_client` (`-servername`, `-verify_return_error`): https://docs.openssl.org/master/man1/openssl-s_client/ ; verification options (`-verify_hostname`): https://docs.openssl.org/master/man1/openssl-verification-options/
- mkcert: https://github.com/FiloSottile/mkcert
