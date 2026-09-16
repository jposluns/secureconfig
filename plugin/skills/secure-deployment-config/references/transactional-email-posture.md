# Transactional email posture: authenticating the mail your deployment sends

Password resets, sign-in links, and invitations are part of your authentication path: a recipient who trusts a forged one hands an attacker the account. The controls that stop that forgery are not a single service's settings but three DNS-published standards (SPF, DKIM, and DMARC), the submission channel your application sends through, and the transport policy between mail servers. This guide covers that posture for a deployment that sends transactional mail. It is standards-based rather than product-based, so [authentication.md](authentication.md) covers the account side and [secrets.md](secrets.md) covers the SMTP credential and DKIM private key you will handle here.

The through-line: a spoofable sender undermines every message your users are trained to act on, an open relay burns your sending reputation and gets your mail blocked, and an authenticated but plaintext submission leaks the credential that lets an attacker send as you. All values below (domains, IPs, selectors, keys) are illustrative; replace them with your own deployment inventory.

## 1. SPF: authorize the sending IPs

SPF publishes, as a DNS TXT record, the IP addresses allowed to send for a domain. A receiver checks the record against the connecting IP and the envelope `MAIL FROM` domain (the `HELO` name for a null return path); it does not check the visible `From:` header, which is why SPF alone does not stop header spoofing and only becomes useful once DMARC ties it to `From:`.

```dns
bounce.example.com. 3600 IN TXT "v=spf1 ip4:192.0.2.10 include:_spf.provider.example -all"
```

The final mechanism decides unmatched senders: `-all` fails them, `~all` softfails (many receivers still deliver a softfail), and `+all` or a bare `all` passes everyone, which destroys the record's meaning. Publish exactly one SPF record per evaluated domain; a domain with two `v=spf1` records is a `permerror`. SPF also caps the terms that trigger DNS lookups (`include`, `a`, `mx`, `ptr`, `exists`, and the `redirect` modifier) at ten across the whole recursion, and exceeding that is a `permerror` that voids the result; `ip4`, `ip6`, and `all` do not count against the ten (RFC 7208 sections 4.5 and 4.6.4). A long chain of provider `include`s is the usual way a domain silently blows the budget and becomes spoofable.

What remains unverified until you inspect your own zone: the real envelope domain, the provider `include` targets, the live recursive lookup count, and whether a second SPF record was left behind by an earlier vendor.

## 2. DKIM: sign with a rotatable key

DKIM attaches a cryptographic signature to each message and publishes the matching public key at a selector under the signing domain. The signature names its domain as `d=` and its selector as `s=`; the receiver fetches the key from the selector record under `_domainkey` (here `tx202609._domainkey.example.com`) to verify it. DKIM proves the signed headers and body were not altered and were authorized by the `d=` domain; it does not encrypt the message.

```dns
tx202609._domainkey.example.com. 3600 IN TXT "v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA..."
```

The `p=` value above is a truncated illustrative key; publish the full base64 your signer generates. Sign with `rsa-sha256`: RFC 8301 prohibits `rsa-sha1` outright, sets a hard floor of 1024-bit RSA keys, and recommends 2048-bit or larger, so treat 2048-bit as the working minimum rather than the 1024-bit floor. Rotate by publishing a new selector's public key first, switching signing to it, and only then retiring the old selector once mail signed with it has cleared the network; an empty `p=` revokes a key. Publishing a key is not enough on its own: the sending service must actually sign, and a receiver must actually verify, before DKIM contributes to a DMARC pass.

Unverified until checked in your deployment: whether signing is enabled, the live `d=` and selector, the key length, whether the key is a TXT record or a provider CNAME delegation, and who owns rotation.

## 3. DMARC: align authentication to the visible From and enforce

DMARC is the record that finally protects the `From:` your users see. A message passes DMARC when at least one of SPF or DKIM both passes and is aligned: SPF alignment compares the envelope domain, DKIM alignment compares the verified signature's `d=`, each against the visible `From:` domain. Relaxed alignment (`adkim=r`, `aspf=r`, the default) accepts the same organizational domain; strict (`s`) requires an exact match.

```dns
_dmarc.example.com. 3600 IN TXT "v=DMARC1; p=reject; sp=reject; np=reject; adkim=r; aspf=r; rua=mailto:dmarc-agg@example.com"
```

`p=` sets the requested handling of failures: `none` asks for no change (monitor only, and still spoofable), `quarantine` asks receivers to treat failures as suspicious, and `reject` asks them to reject at SMTP time. `sp=` sets the policy for existing subdomains and `np=` for non-existent ones; where a tag is absent, policy falls back `np` to `sp` to `p`, so publishing `sp=reject; np=reject` closes the subdomains an attacker would otherwise spoof. DMARC discovers the applicable policy and organizational domain by a DNS tree walk (RFC 9989 section 4.10), which replaced the old public-suffix-list method. `t=y` weakens enforcement for testing and `t=n` is the default; the enforcement record above omits it.

Reach `p=reject` only after a monitoring period under `p=none` with aggregate reports confirms every legitimate stream aligns, or you will reject your own mail. Missing DMARC or `p=none` means no enforcement is requested, not that mail is guaranteed to arrive; receivers keep their own local policy. One legacy note: RFC 9989 (May 2026), which now defines DMARC and obsoletes RFC 7489, removed the `pct` tag, so a `pct` value is not a current rollout control, and a legacy `p=reject; pct=25` was partial application rather than full enforcement.

Unverified until checked: which streams actually align, the inherited and explicit subdomain policies, and whether your receivers implement the current specification.

## 4. DMARC reporting: aggregate now, failure reports later

Aggregate reporting (`rua=`, RFC 9990) sends a daily XML summary of authentication results and is how you see what is sending as your domain before you enforce; turn it on first. A destination in another domain must authorize the reports, or receivers will not send them:

```dns
example.com._report._dmarc.collector.example.net. IN TXT "v=DMARC1"
```

Failure reporting (`ruf=`, RFC 9991) sends per-message forensic copies that can include message content and recipient data, which for password-reset mail can mean leaking a live reset token to whatever inbox collects the reports. Omit `ruf` at first, and enable it only after you have settled collection, redaction, retention, and access, and authorized any external destination the same way. Publication alone is not evidence reports arrive: verify the mailbox actually receives and processes them.

## 5. SMTP submission and relay: TLS before AUTH, and never an open relay

Where your application hands mail to a mail server, three ports carry different contracts. Port 587 is submission with STARTTLS: the client upgrades to TLS and then authenticates, but the STARTTLS offer alone does not force encryption, so an opportunistic client that falls back to plaintext is exposed to a STARTTLS-stripping downgrade that captures the credential. Port 465 is submission with implicit TLS: the connection is encrypted from the first byte and is immune to stripping, which is why RFC 8314 prefers it going forward. Require successful TLS with certificate chain and hostname validation before any credential is sent on either, and treat TLS 1.2 as the floor (RFC 8997). Port 25 is inter-server relay or, at some providers, submission; "port 25 means no authentication" is wrong (RFC 6409 section 3.1), so identify which role your endpoint plays rather than assuming.

An open relay forwards mail from an unauthenticated, untrusted client to a destination the server is not responsible for; it will be found and abused, and your domain blocked. Reject that forwarding while still allowing the two legitimate cases: ordinary unauthenticated inbound delivery to your own local recipients, and explicitly authorized relay paths (RFC 2505 section 2.1). After TLS, an unauthenticated or invalidly authenticated submission must fail and an authorized one succeed.

Unverified until checked: the live endpoints and ports, whether the client enforces TLS rather than merely offering it, the authentication mechanism, and the relay access rules.

## 6. Transport and display: MTA-STS, TLS-RPT, and BIMI

MTA-STS (RFC 8461) lets a receiving domain demand TLS for mail sent to it. A TXT record points to an HTTPS-hosted policy:

```dns
_mta-sts.example.com. IN TXT "v=STSv1; id=2026091501"
```

The policy is served as `text/plain` at `https://mta-sts.example.com/.well-known/mta-sts.txt`:

```text
version: STSv1
mode: enforce
mx: mx1.example.com
max_age: 604800
```

Only `mode: enforce` constrains delivery (`testing` and `none` do not), and the crucial caveat is direction: MTA-STS protects mail arriving at the policy domain, so publishing it does not secure your own outbound mail to other domains, and it depends on your sending server validating recipients' policies. Update the `id` whenever the policy changes. TLS-RPT (RFC 8460) is reporting only, never enforcement:

```dns
_smtp._tls.example.com. IN TXT "v=TLSRPTv1; rua=mailto:tls-rpt@example.com"
```

BIMI is optional display metadata that shows a brand logo in supporting clients; it depends on DMARC enforcement already being in place and is not an authentication mechanism or a guarantee the logo renders. Keep it last, after the records above are enforcing.

## Verify

```bash
# Inspect the published records (replace names; take the DKIM selector from a real signature).
# These read DNS and TLS state; they do not evaluate SPF or DMARC or prove a service listener.
dig +noall +answer TXT bounce.example.com
dig +noall +answer TXT tx202609._domainkey.example.com
dig +noall +answer CNAME tx202609._domainkey.example.com
dig +noall +answer TXT _dmarc.example.com
dig +noall +answer TXT _mta-sts.example.com
dig +noall +answer TXT _smtp._tls.example.com
dig +noall +answer TXT default._bimi.example.com

# Submission must complete TLS with a validated certificate before AUTH. -verify_return_error
# matters because s_client otherwise continues past a verification failure.
openssl s_client -connect smtp.example.com:587 -starttls smtp \
  -servername smtp.example.com -verify_hostname smtp.example.com \
  -verify_return_error -min_protocol TLSv1.2 </dev/null

openssl s_client -connect smtp.example.com:465 \
  -servername smtp.example.com -verify_hostname smtp.example.com \
  -verify_return_error -min_protocol TLSv1.2 </dev/null
```

Prove alignment by sending one benign message to a controlled recipient and reading the receiving system's trusted `Authentication-Results` header (RFC 8601), never a header the message itself supplied: require a passing, aligned SPF or DKIM result. Confirm the enforcement target is really `p=reject` with subdomain coverage and no testing or legacy sampling. Test open-relay rejection only in an operator-controlled environment (an external `MAIL FROM` and a non-local `RCPT TO` should draw a 5xx), and compare it against an authorized submission and ordinary local delivery. These checks inspect DNS, TLS, and message authentication, not an application listener; running them against live deployments in both the exposed and fixed states is tracked as `[gap]` 2.31.

## Common mistakes

- Stopping at `p=none`: monitoring is the first step, not the posture, and it stops no spoofing.
- Leaving subdomains open by omitting `sp=` and `np=` while enforcing only the top domain.
- Blowing the SPF ten-lookup budget through nested provider `include`s, which turns a strict record into a `permerror` and makes the domain spoofable.
- Enabling `ruf=` on password-reset mail without redaction, which can ship a live reset token to the report inbox.
- Trusting STARTTLS on 587 without enforcing it, so a stripped connection sends the credential in plaintext.
- Assuming MTA-STS on your own domain protects your outbound mail; it protects mail sent to you.

## Sources (checked September 2026)

- RFC 9989: Domain-based Message Authentication, Reporting, and Conformance (DMARC), obsoletes RFC 7489, removes `pct`, adds `np`, DNS tree walk: https://www.rfc-editor.org/rfc/rfc9989.html
- RFC 9990: DMARC Aggregate Reporting (`rua`): https://www.rfc-editor.org/rfc/rfc9990.html
- RFC 9991: DMARC Failure Reporting (`ruf`, privacy): https://www.rfc-editor.org/rfc/rfc9991.html
- RFC 7208: Sender Policy Framework (terminators, ten-lookup limit, multiple-record permerror): https://www.rfc-editor.org/rfc/rfc7208.html
- RFC 6376: DomainKeys Identified Mail (DKIM) Signatures: https://www.rfc-editor.org/rfc/rfc6376.html
- RFC 8301: DKIM cryptographic update (rsa-sha256 required, rsa-sha1 prohibited, key sizes): https://www.rfc-editor.org/rfc/rfc8301.html
- RFC 8314: Cleartext Considered Obsolete (implicit TLS on 465, STARTTLS on 587): https://www.rfc-editor.org/rfc/rfc8314.html
- RFC 6409: Message Submission for Mail (submission vs relay, port 25): https://www.rfc-editor.org/rfc/rfc6409.html
- RFC 2505: Anti-Spam Recommendations for SMTP MTAs (open relay): https://www.rfc-editor.org/rfc/rfc2505.html
- RFC 8461: SMTP MTA Strict Transport Security (MTA-STS): https://www.rfc-editor.org/rfc/rfc8461.html
- RFC 8460: SMTP TLS Reporting (TLS-RPT): https://www.rfc-editor.org/rfc/rfc8460.html
- RFC 8601: Message Header Field for Indicating Message Authentication Status (`Authentication-Results`): https://www.rfc-editor.org/rfc/rfc8601.html
- BIMI Group: implementation and sender requirements: https://bimigroup.org/how-and-why-to-implement-bimi-selectors/
