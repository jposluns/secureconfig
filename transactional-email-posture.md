---
version_basis: {
  "schema": 1,
  "checked": "2026-10-05",
  "documentation_checked": "2026-09",
  "body_sha256": "e8ed589badae861c5523d3f00b9988f385be3eab8cde37fe6c02c2a1387c1aae",
  "components": {
    "spf": {
      "name": "SPF",
      "basis": "RFC 7208",
      "sources": {
        "sea6ac206b034": "https://www.rfc-editor.org/rfc/rfc7208.html"
      }
    },
    "dkim": {
      "name": "DKIM",
      "basis": "RFC 6376",
      "sources": {
        "s13ee1bc66dfc": "https://www.rfc-editor.org/rfc/rfc6376.html"
      }
    },
    "crypto": {
      "name": "DKIM cryptography",
      "basis": "RFC 8301",
      "sources": {
        "sb675e6772778": "https://www.rfc-editor.org/rfc/rfc8301.html"
      }
    },
    "dmarc": {
      "name": "DMARC",
      "basis": "RFC 9989",
      "sources": {
        "s5da292ff1b92": "https://www.rfc-editor.org/rfc/rfc9989.html"
      }
    },
    "aggregate": {
      "name": "DMARC aggregate reporting",
      "basis": "RFC 9990",
      "sources": {
        "s5e0e418f74dd": "https://www.rfc-editor.org/rfc/rfc9990.html"
      }
    },
    "failure": {
      "name": "DMARC failure reporting",
      "basis": "RFC 9991",
      "sources": {
        "s136bbcd8e31a": "https://www.rfc-editor.org/rfc/rfc9991.html"
      }
    },
    "submission": {
      "name": "Submission TLS",
      "basis": "RFC 8314",
      "sources": {
        "sd78efc15555c": "https://www.rfc-editor.org/rfc/rfc8314.html"
      }
    },
    "roles": {
      "name": "SMTP submission roles",
      "basis": "RFC 6409",
      "sources": {
        "s3f9972faf8ff": "https://www.rfc-editor.org/rfc/rfc6409.html"
      }
    },
    "relay": {
      "name": "SMTP relay controls",
      "basis": "RFC 2505",
      "sources": {
        "s1b9349dd99bc": "https://www.rfc-editor.org/rfc/rfc2505.html"
      }
    },
    "sts": {
      "name": "MTA-STS",
      "basis": "RFC 8461",
      "sources": {
        "s39819f3ea93a": "https://www.rfc-editor.org/rfc/rfc8461.html"
      }
    },
    "rpt": {
      "name": "TLS-RPT",
      "basis": "RFC 8460",
      "sources": {
        "se80da0f5e0c8": "https://www.rfc-editor.org/rfc/rfc8460.html"
      }
    },
    "results": {
      "name": "Authentication-Results",
      "basis": "RFC 8601",
      "sources": {
        "s46f8392d93fd": "https://www.rfc-editor.org/rfc/rfc8601.html"
      }
    },
    "bimi": {
      "name": "BIMI documentation",
      "basis": "unknown",
      "sources": {
        "sd18b1e0134bd": "https://bimigroup.org/how-and-why-to-implement-bimi-selectors/"
      }
    },
    "submission-update": {
      "name": "Submission TLS update",
      "basis": "RFC 8997",
      "sources": {
        "sb5ca35fe0d1b": "https://www.rfc-editor.org/rfc/rfc8997.html#section-3"
      }
    },
    "bind": {
      "name": "BIND dig manual",
      "basis": "9.18.39",
      "sources": {
        "s54cff06bb882": "https://bind9.readthedocs.io/en/v9.18.39/manpages.html"
      }
    },
    "openssl": {
      "name": "OpenSSL command documentation",
      "basis": "3.0",
      "sources": {
        "s00aaf106164f": "https://docs.openssl.org/3.0/man1/openssl-s_client/",
        "s2a2127a2c79b": "https://docs.openssl.org/3.0/man3/SSL_CONF_cmd/"
      }
    }
  },
  "claims": {
    "spf-identity": {"text": "SPF TXT authorizes connecting IPs for MAIL FROM, or HELO with a null return path; it does not authenticate visible From without DMARC alignment.", "components": ["spf", "dmarc"], "sources": ["spf:sea6ac206b034", "dmarc:s5da292ff1b92"], "status": "REASONED"},
    "spf-all": {"text": "-all fails unmatched senders, ~all softfails and may still be delivered, while +all or bare all passes everyone.", "components": ["spf"], "sources": ["spf:sea6ac206b034"], "status": "REASONED"},
    "spf-record": {"text": "Publish exactly one v=spf1 record per evaluated domain; multiple records produce permerror.", "components": ["spf"], "sources": ["spf:sea6ac206b034"], "status": "REASONED"},
    "spf-lookups": {"text": "Ten DNS-lookup terms across recursion include include/a/mx/ptr/exists/redirect but exclude ip4/ip6/all; exceeding the limit gives permerror. An earlier matching mechanism stops evaluation; permerror is no SPF pass.", "components": ["spf"], "sources": ["spf:sea6ac206b034"], "status": "REASONED"},
    "dkim-signing": {"text": "DKIM d= and s= select the _domainkey public key; signatures authenticate signed content for the signing domain, not encryption. Actual signing and verification are required for DMARC.", "components": ["dkim", "dmarc"], "sources": ["dkim:s13ee1bc66dfc", "dmarc:s5da292ff1b92"], "status": "REASONED"},
    "dkim-crypto": {"text": "Use rsa-sha256, never rsa-sha1; RFC 8301 sets a 1024-bit RSA floor and recommends at least 2048 bits, used here as the working minimum. Publish the full generated key, not the truncated example.", "components": ["crypto"], "sources": ["crypto:sb675e6772778"], "status": "REASONED"},
    "dkim-rotation": {"text": "Publish a new selector before switching signing, retire the old selector after in-flight mail clears, and revoke with empty p=; inspect actual selector, delegation and rotation ownership.", "components": ["dkim"], "sources": ["dkim:s13ee1bc66dfc"], "status": "REASONED"},
    "dmarc-alignment": {"text": "DMARC requires at least one passing and aligned SPF or DKIM result; relaxed adkim=r/aspf=r defaults to organizational-domain alignment, strict s requires exact domain matching.", "components": ["dmarc"], "sources": ["dmarc:s5da292ff1b92"], "status": "REASONED"},
    "dmarc-policy": {"text": "p=none requests monitoring only, quarantine suspicious handling, and reject SMTP-time rejection; receivers retain local policy, so missing enforcement does not guarantee delivery.", "components": ["dmarc"], "sources": ["dmarc:s5da292ff1b92"], "status": "REASONED"},
    "dmarc-subdomains": {"text": "sp covers existing subdomains and np non-existent ones, falling back np to sp to p; a subdomain-specific record can take precedence. Inventory explicit and inherited policies.", "components": ["dmarc"], "sources": ["dmarc:s5da292ff1b92"], "status": "REASONED"},
    "dmarc-discovery": {"text": "RFC 9989 DNS tree walk discovers policy and organizational domain, replacing the former public-suffix-list method.", "components": ["dmarc"], "sources": ["dmarc:s5da292ff1b92"], "status": "REASONED"},
    "dmarc-testing": {"text": "t=y weakens enforcement and t=n is the default; the illustrated enforcing record omits the tag.", "components": ["dmarc"], "sources": ["dmarc:s5da292ff1b92"], "status": "REASONED"},
    "dmarc-rollout": {"text": "Monitor aggregate reports under p=none until legitimate streams align before moving to p=reject, or legitimate mail can be rejected.", "components": ["dmarc", "aggregate"], "sources": ["dmarc:s5da292ff1b92", "aggregate:s5e0e418f74dd"], "status": "REASONED"},
    "dmarc-pct": {"text": "RFC 9989, May 2026, obsoletes RFC 7489 and removes pct; legacy p=reject;pct=25 was partial application, not a current rollout control.", "components": ["dmarc"], "sources": ["dmarc:s5da292ff1b92"], "status": "REASONED"},
    "aggregate": {"text": "Enable rua daily aggregate XML reporting to observe sending streams; an external reporting domain must authorize reports, and actual receipt/processing must be checked.", "components": ["aggregate"], "sources": ["aggregate:s5e0e418f74dd"], "status": "REASONED"},
    "failure-reports": {"text": "ruf forensic reports can expose content, recipients and reset tokens; omit initially, settle redaction/retention/access before enabling, and authorize external destinations.", "components": ["failure"], "sources": ["failure:s136bbcd8e31a"], "status": "REASONED"},
    "starttls": {"text": "587 submission upgrades with STARTTLS before authentication; an opportunistic fallback can expose credentials to stripping, so require successful validated TLS.", "components": ["submission"], "sources": ["submission:sd78efc15555c"], "status": "REASONED"},
    "implicit-tls": {"text": "465 submission starts with TLS and avoids STARTTLS stripping; RFC 8314 prefers implicit TLS going forward.", "components": ["submission"], "sources": ["submission:sd78efc15555c"], "status": "REASONED"},
    "tls-validation": {"text": "Validate certificate chain and hostname before credentials on either submission port; the guide states TLS 1.2 as the floor and attributes that update to RFC 8997, absent from its Sources list.", "components": ["submission", "submission-update"], "sources": ["submission:sd78efc15555c", "submission-update:sb5ca35fe0d1b"], "status": "REASONED"},
    "port-25": {"text": "25 is inter-server relay or provider submission; identify the endpoint role instead of assuming that port 25 implies no authentication.", "components": ["roles"], "sources": ["roles:s3f9972faf8ff"], "status": "REASONED"},
    "relay-policy": {"text": "Reject unauthenticated untrusted forwarding to non-local recipients while allowing ordinary inbound local delivery and explicitly authorized relay paths.", "components": ["relay"], "sources": ["relay:s1b9349dd99bc"], "status": "REASONED"},
    "submission-auth": {"text": "After TLS, unauthenticated or invalidly authenticated submission must fail while authorized submission succeeds.", "components": ["roles", "submission"], "sources": ["roles:s3f9972faf8ff", "submission:sd78efc15555c"], "status": "REASONED"},
    "sts-publication": {"text": "MTA-STS TXT advertises the HTTPS text/plain policy at /.well-known/mta-sts.txt on mta-sts.example.com; the example selects enforce, an MX host and max_age 604800.", "components": ["sts"], "sources": ["sts:s39819f3ea93a"], "status": "REASONED"},
    "sts-enforcement": {"text": "Only enforce constrains delivery; testing and none do not. MTA-STS protects mail arriving at the policy domain and depends on sending-server validation, not protection of the publishing domain outbound mail.", "components": ["sts"], "sources": ["sts:s39819f3ea93a"], "status": "REASONED"},
    "sts-refresh": {"text": "Update the MTA-STS TXT id whenever the policy changes.", "components": ["sts"], "sources": ["sts:s39819f3ea93a"], "status": "REASONED"},
    "tls-reports": {"text": "TLS-RPT _smtp._tls TXT with TLSRPTv1 and rua supplies reports, never enforcement.", "components": ["rpt"], "sources": ["rpt:se80da0f5e0c8"], "status": "REASONED"},
    "bimi": {"text": "BIMI is optional logo display metadata requiring DMARC enforcement, not authentication or guaranteed rendering; deploy it last.", "components": ["bimi"], "sources": ["bimi:sd18b1e0134bd"], "status": "REASONED"},
    "verify-dns": {"text": "Inspect SPF, DKIM TXT/CNAME, DMARC, MTA-STS, TLS-RPT and BIMI records using actual inventory; DNS inspection alone does not evaluate SPF/DMARC or prove a listener. No DNS control was available.", "components": ["spf", "dkim", "dmarc", "sts", "rpt", "bimi", "bind"], "sources": ["spf:sea6ac206b034", "dkim:s13ee1bc66dfc", "dmarc:s5da292ff1b92", "sts:s39819f3ea93a", "rpt:se80da0f5e0c8", "bimi:sd18b1e0134bd", "bind:s54cff06bb882"], "status": "REASONED", "verify": [1]},
    "verify-tls": {"text": "587 STARTTLS and 465 implicit-TLS probes require validated TLS 1.2 or newer; TLS availability does not establish AUTH gating. Plaintext or stripped-STARTTLS AUTH must be refused; transport/TLS failures are inconclusive. No SMTP endpoint or container runtime was available.", "components": ["submission", "submission-update", "openssl"], "sources": ["submission:sd78efc15555c", "submission-update:sb5ca35fe0d1b", "openssl:s00aaf106164f", "openssl:s2a2127a2c79b"], "status": "REASONED", "verify": [1]},
    "verify-alignment": {"text": "Send a benign message to a controlled recipient and inspect receiver-trusted Authentication-Results, not a supplied header; require passing aligned SPF or DKIM and p=reject with subdomain coverage and no testing or legacy sampling.", "components": ["results", "dmarc"], "sources": ["results:s46f8392d93fd", "dmarc:s5da292ff1b92"], "status": "REASONED"},
    "verify-relay": {"text": "In an operator-controlled environment, external MAIL FROM and non-local RCPT TO should receive 5xx; compare with authorized submission and ordinary local delivery. These expected outcomes remain unobserved.", "components": ["relay", "roles"], "sources": ["relay:s1b9349dd99bc", "roles:s3f9972faf8ff"], "status": "REASONED"}
  }
}
---
# Transactional email posture: authenticating the mail your deployment sends

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-05; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| spf-identity: SPF TXT authorizes connecting IPs for MAIL FROM, or HELO with a null return path; it does not authenticate visible From without DMARC alignment. | SPF RFC 7208; DMARC RFC 9989 | REASONED |
| spf-all: -all fails unmatched senders, ~all softfails and may still be delivered, while +all or bare all passes everyone. | SPF RFC 7208 | REASONED |
| spf-record: Publish exactly one v=spf1 record per evaluated domain; multiple records produce permerror. | SPF RFC 7208 | REASONED |
| spf-lookups: Ten DNS-lookup terms across recursion include include/a/mx/ptr/exists/redirect but exclude ip4/ip6/all; exceeding the limit gives permerror. An earlier matching mechanism stops evaluation; permerror is no SPF pass. | SPF RFC 7208 | REASONED |
| dkim-signing: DKIM d= and s= select the _domainkey public key; signatures authenticate signed content for the signing domain, not encryption. Actual signing and verification are required for DMARC. | DKIM RFC 6376; DMARC RFC 9989 | REASONED |
| dkim-crypto: Use rsa-sha256, never rsa-sha1; RFC 8301 sets a 1024-bit RSA floor and recommends at least 2048 bits, used here as the working minimum. Publish the full generated key, not the truncated example. | DKIM cryptography RFC 8301 | REASONED |
| dkim-rotation: Publish a new selector before switching signing, retire the old selector after in-flight mail clears, and revoke with empty p=; inspect actual selector, delegation and rotation ownership. | DKIM RFC 6376 | REASONED |
| dmarc-alignment: DMARC requires at least one passing and aligned SPF or DKIM result; relaxed adkim=r/aspf=r defaults to organizational-domain alignment, strict s requires exact domain matching. | DMARC RFC 9989 | REASONED |
| dmarc-policy: p=none requests monitoring only, quarantine suspicious handling, and reject SMTP-time rejection; receivers retain local policy, so missing enforcement does not guarantee delivery. | DMARC RFC 9989 | REASONED |
| dmarc-subdomains: sp covers existing subdomains and np non-existent ones, falling back np to sp to p; a subdomain-specific record can take precedence. Inventory explicit and inherited policies. | DMARC RFC 9989 | REASONED |
| dmarc-discovery: RFC 9989 DNS tree walk discovers policy and organizational domain, replacing the former public-suffix-list method. | DMARC RFC 9989 | REASONED |
| dmarc-testing: t=y weakens enforcement and t=n is the default; the illustrated enforcing record omits the tag. | DMARC RFC 9989 | REASONED |
| dmarc-rollout: Monitor aggregate reports under p=none until legitimate streams align before moving to p=reject, or legitimate mail can be rejected. | DMARC RFC 9989; DMARC aggregate reporting RFC 9990 | REASONED |
| dmarc-pct: RFC 9989, May 2026, obsoletes RFC 7489 and removes pct; legacy p=reject;pct=25 was partial application, not a current rollout control. | DMARC RFC 9989 | REASONED |
| aggregate: Enable rua daily aggregate XML reporting to observe sending streams; an external reporting domain must authorize reports, and actual receipt/processing must be checked. | DMARC aggregate reporting RFC 9990 | REASONED |
| failure-reports: ruf forensic reports can expose content, recipients and reset tokens; omit initially, settle redaction/retention/access before enabling, and authorize external destinations. | DMARC failure reporting RFC 9991 | REASONED |
| starttls: 587 submission upgrades with STARTTLS before authentication; an opportunistic fallback can expose credentials to stripping, so require successful validated TLS. | Submission TLS RFC 8314 | REASONED |
| implicit-tls: 465 submission starts with TLS and avoids STARTTLS stripping; RFC 8314 prefers implicit TLS going forward. | Submission TLS RFC 8314 | REASONED |
| tls-validation: Validate certificate chain and hostname before credentials on either submission port; the guide states TLS 1.2 as the floor and attributes that update to RFC 8997, absent from its Sources list. | Submission TLS RFC 8314; Submission TLS update RFC 8997 | REASONED |
| port-25: 25 is inter-server relay or provider submission; identify the endpoint role instead of assuming that port 25 implies no authentication. | SMTP submission roles RFC 6409 | REASONED |
| relay-policy: Reject unauthenticated untrusted forwarding to non-local recipients while allowing ordinary inbound local delivery and explicitly authorized relay paths. | SMTP relay controls RFC 2505 | REASONED |
| submission-auth: After TLS, unauthenticated or invalidly authenticated submission must fail while authorized submission succeeds. | SMTP submission roles RFC 6409; Submission TLS RFC 8314 | REASONED |
| sts-publication: MTA-STS TXT advertises the HTTPS text/plain policy at /.well-known/mta-sts.txt on mta-sts.example.com; the example selects enforce, an MX host and max_age 604800. | MTA-STS RFC 8461 | REASONED |
| sts-enforcement: Only enforce constrains delivery; testing and none do not. MTA-STS protects mail arriving at the policy domain and depends on sending-server validation, not protection of the publishing domain outbound mail. | MTA-STS RFC 8461 | REASONED |
| sts-refresh: Update the MTA-STS TXT id whenever the policy changes. | MTA-STS RFC 8461 | REASONED |
| tls-reports: TLS-RPT _smtp._tls TXT with TLSRPTv1 and rua supplies reports, never enforcement. | TLS-RPT RFC 8460 | REASONED |
| bimi: BIMI is optional logo display metadata requiring DMARC enforcement, not authentication or guaranteed rendering; deploy it last. | BIMI documentation unknown | REASONED |
| verify-dns: Inspect SPF, DKIM TXT/CNAME, DMARC, MTA-STS, TLS-RPT and BIMI records using actual inventory; DNS inspection alone does not evaluate SPF/DMARC or prove a listener. No DNS control was available. | SPF RFC 7208; DKIM RFC 6376; DMARC RFC 9989; MTA-STS RFC 8461; TLS-RPT RFC 8460; BIMI documentation unknown; BIND dig manual 9.18.39 | REASONED |
| verify-tls: 587 STARTTLS and 465 implicit-TLS probes require validated TLS 1.2 or newer; TLS availability does not establish AUTH gating. Plaintext or stripped-STARTTLS AUTH must be refused; transport/TLS failures are inconclusive. No SMTP endpoint or container runtime was available. | Submission TLS RFC 8314; Submission TLS update RFC 8997; OpenSSL command documentation 3.0 | REASONED |
| verify-alignment: Send a benign message to a controlled recipient and inspect receiver-trusted Authentication-Results, not a supplied header; require passing aligned SPF or DKIM and p=reject with subdomain coverage and no testing or legacy sampling. | Authentication-Results RFC 8601; DMARC RFC 9989 | REASONED |
| verify-relay: In an operator-controlled environment, external MAIL FROM and non-local RCPT TO should receive 5xx; compare with authorized submission and ordinary local delivery. These expected outcomes remain unobserved. | SMTP relay controls RFC 2505; SMTP submission roles RFC 6409 | REASONED |
<!-- version-basis:end -->

Password resets, sign-in links, and invitations are part of your authentication path: a recipient who trusts a forged one hands an attacker the account. The controls that stop that forgery are not a single service's settings but three DNS-published standards (SPF, DKIM, and DMARC), the submission channel your application sends through, and the transport policy between mail servers. This guide covers that posture for a deployment that sends transactional mail. It is standards-based rather than product-based, so [authentication.md](authentication.md) covers the account side and [secrets.md](secrets.md) covers the SMTP credential and DKIM private key you will handle here.

The through-line: a spoofable sender undermines every message your users are trained to act on, an open relay burns your sending reputation and gets your mail blocked, and an authenticated but plaintext submission leaks the credential that lets an attacker send as you. All values below (domains, IPs, selectors, keys) are illustrative; replace them with your own deployment inventory.

## 1. SPF: authorize the sending IPs

SPF publishes, as a DNS TXT record, the IP addresses allowed to send for a domain. A receiver checks the record against the connecting IP and the envelope `MAIL FROM` domain (the `HELO` name for a null return path); it does not check the visible `From:` header, which is why SPF alone does not stop header spoofing and only becomes useful once DMARC ties it to `From:`.

```dns
bounce.example.com. 3600 IN TXT "v=spf1 ip4:192.0.2.10 include:_spf.provider.example -all"
```

The final mechanism decides unmatched senders: `-all` fails them, `~all` softfails (many receivers still deliver a softfail), and `+all` or a bare `all` passes everyone, which destroys the record's meaning. Publish exactly one SPF record per evaluated domain; a domain with two `v=spf1` records is a `permerror`. SPF also caps the terms that trigger DNS lookups (`include`, `a`, `mx`, `ptr`, `exists`, and the `redirect` modifier) at ten across the whole recursion, and exceeding that is a `permerror` that voids the result; `ip4`, `ip6`, and `all` do not count against the ten (RFC 7208 sections 4.5 and 4.6.4). A long chain of provider `include`s is the usual way a domain silently blows the budget: any evaluation that has to walk the whole chain returns `permerror`, though a sender matched by an earlier mechanism such as a listed `ip4` still passes, because evaluation stops at the first match. A `permerror` is not an SPF pass, so legitimate mail that reached it and relied on SPF alignment fails your own DMARC. It breaks your authentication, not an attacker's.

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

`p=` sets the requested handling of failures: `none` asks for no change (monitor only, and still spoofable), `quarantine` asks receivers to treat failures as suspicious, and `reject` asks them to reject at SMTP time. `sp=` sets the policy for existing subdomains and `np=` for non-existent ones; where a tag is absent, policy falls back `np` to `sp` to `p`, so a `p=reject` domain already rejects for its own subdomains without them. Publish `sp` and `np` when you want subdomains held to a policy of their own, whether it repeats or differs from `p`, and inventory any subdomain that publishes its own DMARC record, since a receiver's tree walk finds that record first. DMARC discovers the applicable policy and organizational domain by a DNS tree walk (RFC 9989 section 4.10), which replaced the old public-suffix-list method. `t=y` weakens enforcement for testing and `t=n` is the default; the enforcement record above omits it.

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

Every probe below is reasoned, not demonstrated: the authoring environment has no DNS control, no SMTP endpoint, and no container runtime, so the outcomes are derived from the cited RFCs rather than observed. For the submission probes, a transport failure or a TLS error is inconclusive, never the fixed state.

```bash
# REASONED: DNS and TLS expectations follow the cited RFCs; no DNS control, SMTP endpoint, or container runtime is available.
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
# matters because s_client otherwise continues past a verification failure. This confirms TLS is
# available, not that AUTH is gated on it; the discriminating check, reasoned here, is the negative
# one: a plaintext or post-stripped-STARTTLS AUTH attempt must be refused, where the exposed state
# accepts it.
openssl s_client -connect smtp.example.com:587 -starttls smtp \
  -servername smtp.example.com -verify_hostname smtp.example.com \
  -verify_return_error -min_protocol TLSv1.2 </dev/null

openssl s_client -connect smtp.example.com:465 \
  -servername smtp.example.com -verify_hostname smtp.example.com \
  -verify_return_error -min_protocol TLSv1.2 </dev/null
```

Prove alignment by sending one benign message to a controlled recipient and reading the receiving system's trusted `Authentication-Results` header (RFC 8601), never a header the message itself supplied: require a passing, aligned SPF or DKIM result. Confirm the enforcement target is really `p=reject` with subdomain coverage and no testing or legacy sampling. Test open-relay rejection only in an operator-controlled environment (an external `MAIL FROM` and a non-local `RCPT TO` should draw a 5xx), and compare it against an authorized submission and ordinary local delivery. These checks inspect DNS, TLS, and message authentication, not an application listener; their expected exposed and fixed outcomes are REASONED from the cited RFCs.

## Common mistakes

- Stopping at `p=none`: monitoring is the first step, not the posture, and it stops no spoofing.
- Assuming the parent policy covers a subdomain that publishes its own weaker DMARC record; a receiver's tree walk uses the subdomain's own record first, so inventory those.
- Blowing the SPF ten-lookup budget through nested provider `include`s, so any evaluation that walks the whole chain returns a `permerror`, which is no pass and breaks authentication for your own mail rather than an attacker's.
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
- RFC 8997 section 3 (checked October 2026; TLS 1.2 floor for email submission and access): https://www.rfc-editor.org/rfc/rfc8997.html#section-3
- BIND 9.18.39 `dig` manual (checked October 2026; TXT/CNAME queries and `+noall +answer` display controls): https://bind9.readthedocs.io/en/v9.18.39/manpages.html
- OpenSSL 3.0 `s_client` (checked October 2026; SMTP STARTTLS, TLS connections, hostname verification, and verification errors): https://docs.openssl.org/3.0/man1/openssl-s_client/
- OpenSSL 3.0 protocol configuration (checked October 2026; `-min_protocol TLSv1.2`): https://docs.openssl.org/3.0/man3/SSL_CONF_cmd/
