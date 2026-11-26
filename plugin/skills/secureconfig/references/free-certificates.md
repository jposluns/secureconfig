# Free publicly trusted certificates (ACME)

ACME is the protocol Let's Encrypt and similar authorities use to issue TLS certificates automatically after a client proves domain control. This guide helps your AI assistant obtain them securely, including a suitable challenge, Certbot or a built-in ACME client, automated renewal, testing against staging first, and CAA records.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/free-certificates.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against Let's Encrypt documentation (no recorded version), Certbot reconfigure minimum 2.3.0, acme.sh 3.1.7, Certbot user guide and source v2.3.0, Certbot Cloudflare DNS plugin v2.3.0, Caddy automatic HTTPS v2.11.4, certmagic ACME implementation v0.25.3, and Traefik ACME documentation v3.5, plus 7 more recorded bases; 2 further sources carry no recorded version. Metadata reviewed 2026-11-25; documentation checked September 2026. The guide records 38 claims, all reasoned from cited sources and any earlier-form run, not a live demonstration of the shipped form.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

Publicly trusted certificates are free through ACME certificate authorities such as Let's Encrypt and ZeroSSL. Browsers and libraries accept them without any client-side configuration, which is why this guide assesses them as the correct choice for every service with a public DNS name. Use [self-signed.md](self-signed.md) only when no public domain exists; a host that cannot accept inbound connections can still get a publicly trusted certificate through the DNS-01 challenge (below), or serve behind [cloudflare.md](cloudflare.md).

## Prerequisites

- A public DNS record (`A`/`AAAA` or `CNAME`) pointing at the server, for the HTTP-01 and TLS-ALPN-01 challenges; the DNS-01 challenge instead needs only control of the challenge `TXT` record and can certify a host with no public address record or inbound port.
- For the HTTP-01 challenge: inbound port 80 reachable from the internet.
- For the TLS-ALPN-01 challenge: inbound port 443. Caddy's ACME issuer enables this challenge when DNS-01 is not configured and TLS-ALPN-01 is not disabled; Traefik also uses it. Caddy can use an alternate local port if port 443 forwards to it.
- For the DNS-01 challenge (required for wildcard certificates), automated issuance and renewal need an automated way to update the provider's TXT record; this guide advises using a DNS plugin and scoped API credentials, while Certbot also documents manual authentication hooks for automated challenges. Manual DNS-01 is also possible with `certbot certonly --manual --preferred-challenges dns`, creating the TXT record by hand; the Certbot v2.3.0 guide says certificates obtained this way do not auto-renew without an authentication hook (`--manual-auth-hook`) that automates the challenge.

If none of these is possible, use [cloudflare.md](cloudflare.md) instead.

## Certbot with Let's Encrypt

Certbot is the reference ACME client. Install it from your distribution or via snap:

```bash
# Debian/Ubuntu
sudo apt install certbot python3-certbot-nginx python3-certbot-apache

# Any distribution with snapd
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

Issue and install in one step when certbot supports your web server:

```bash
sudo certbot --nginx  -d example.com -d www.example.com
sudo certbot --apache -d example.com -d www.example.com
```

Issue only the certificate when you configure the server yourself, or when no web server is running yet:

```bash
# Standalone: certbot binds port 80 itself; stop anything using it first (and for a host whose web server will own :80, switch this certificate to --webroot or the server plugin, or add pre/post hooks that free the port, so unattended renewal can still bind)
sudo certbot certonly --standalone -d example.com

# Webroot: the existing web server keeps running and serves the challenge files
sudo certbot certonly --webroot -w /var/www/html -d example.com
```

Wildcard certificates require the DNS-01 challenge. For automated issuance and renewal, use a DNS plugin as this guide advises (for example `python3-certbot-dns-cloudflare`). Scope provider API credentials to least privilege: use a Cloudflare API token with `Zone:DNS:Edit` on only the required zones; never use the account-wide Global API Key. Keep the credentials file readable only by root (`chmod 600` the file in a `700` directory; Certbot warns when other users can read it):

```bash
sudo certbot certonly --dns-cloudflare \
  --dns-cloudflare-credentials /root/.secrets/cloudflare.ini \
  -d example.com -d "*.example.com"
```

Certificates land in stable paths that server configuration should reference directly:

```
/etc/letsencrypt/live/example.com/fullchain.pem   # certificate plus chain
/etc/letsencrypt/live/example.com/privkey.pem     # private key
```

This guide advises keeping the private key on the server: do not copy it into a repository, image or ticket, and give read access only to the account that runs the server or the deploy hook. Certbot v2.3.0 creates the `live`, `archive` and `renewal` directories with mode `0700` when they do not exist, and writes each new private key under `archive` with mode `0600`, linked from `live` ([Certbot v2.3.0 storage.py](https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L1064-L1105)). Its user guide says private keys for new certificates default to `0600` as of Certbot 0.29.0 and that changes to the key's group mode or group owner are kept on renewal; for a server that drops root before reading the key, it gives `chgrp` and `chmod 0640` ([Certbot v2.3.0 user guide](https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L891-L914)).

## Renewal

Let's Encrypt certificates are valid for 90 days at the time of writing, so renewal must be automated. The Certbot v2.3.0 guide says most installations come with a scheduled `certbot renew` task and says that, on Linux and BSD, you can check cron or systemd timers if unsure ([Certbot v2.3.0 user guide](https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L808-L825)). Confirm that your installation (package and snap installs included) has a working scheduled `certbot renew` task, and reload the server after each renewal:

```bash
sudo systemctl list-timers | grep -i certbot       # a certbot timer must be listed; for cron, /etc/crontab or /etc/cron.*/* must contain certbot renew
sudo certbot renew --dry-run --run-deploy-hooks    # test renewal and the reload hook together
```

Install the reload hook durably: pass `--deploy-hook "systemctl reload nginx"` on the initial `certonly`/`run` (Certbot saves it to the renewal config only when a certificate is actually obtained or renewed). Alternatively, drop an executable script into `/etc/letsencrypt/renewal-hooks/deploy/` (it runs after every successful renewal), or add it later with `certbot reconfigure` (Certbot 2.3.0 and later) ([Certbot v2.3.0 deploy hooks](https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L659-L684)). In Certbot v2.3.0, a bare `certbot renew --deploy-hook ...` skips renewal when no certificate is due and does not save that hook to a renewal configuration; use one of the durable methods above. This guide assesses a certificate that issues once and then expires in production as the most common ACME failure, so monitor the served certificate's expiry and alert on renewal failure rather than relying on CA reminder emails; the dry run belongs in your deployment checklist.

Lifetimes are getting shorter. Per Let's Encrypt as of September 2026: 6-day short-lived certificates are available now to every subscriber; the default `classic` profile moves to 64-day certificates on 2027-02-10 and to 45-day certificates on 2028-02-16; and industry rules cap publicly trusted certificates at 47 days from 2029-03-15. This guide assesses that any renewal step involving a person will fail at those lifetimes and that the automation above is the only viable path. Let's Encrypt also switched off its OCSP service on 2025-08-06 and publishes revocation only through CRLs, so do not add OCSP stapling directives for Let's Encrypt certificates.

## Rate limits

Let's Encrypt enforces per-domain issuance limits. Test against the staging environment (`certbot --staging` or `--test-cert`) until the configuration works, then issue the real certificate. Current limits: https://letsencrypt.org/docs/rate-limits/

## CAA records

A CAA DNS record restricts which certificate authorities may issue for your domain, limiting mis-issuance. Set it to the CA you use, for example `example.com. CAA 0 issue "letsencrypt.org"` for Let's Encrypt. Certificate-transparency monitoring detects mis-issuance after the fact; CAA constrains it beforehand, so treat the two as complementary, not as alternatives. A CA checks the closest CAA record set: it looks up the requested name, following any alias (CNAME), and climbs one label at a time toward, but not including, the DNS root until it finds a set, so a set on your registered domain also covers its subdomains unless a subdomain has its own. Properties tagged `issuewild`, when present, control wildcard issuance. The second block under Verify finds that set for your host name with `dig`.

## Alternatives

- **ZeroSSL**: free certificates over ACME. ZeroSSL's ACME documentation says its ACME service needs External Account Binding (EAB) credentials, created in the ZeroSSL dashboard or through its API, and that they are not stored in your account, are reusable, and all remain functional when you generate more ([ZeroSSL ACME documentation](https://zerossl.com/documentation/acme/)). Its API returns them as `eab_kid` and `eab_hmac_key` ([ZeroSSL EAB credentials API](https://zerossl.com/documentation/acme/generate-eab-credentials/)). This guide treats both values as secrets: keep them out of shell history, repositories and tickets, and store them where only the account that registers can read them. ZeroSSL's ACME page says each click on "Generate" creates a new set of EAB credentials and that "all of them will remain functional"; the three cited pages describe no way to disable a set (this guide's reading), so treat a leaked set as still usable (this guide's reading). acme.sh 3.1.7 lists ZeroSSL as its default CA ([acme.sh 3.1.7 README](https://github.com/acmesh-official/acme.sh/blob/3.1.7/README.md#L149-L153)). When you register with `--eab-kid` and `--eab-hmac-key`, it saves the values as `CA_EAB_KEY_ID` and `CA_EAB_HMAC_KEY` in its CA configuration file, which it creates with mode `600` ([acme.sh 3.1.7](https://github.com/acmesh-official/acme.sh/blob/3.1.7/acme.sh#L4542-L4612)).
- **acme.sh**: a dependency-light shell ACME client supporting many DNS providers, useful where certbot is unavailable ([acme.sh 3.1.7 README](https://github.com/acmesh-official/acme.sh/blob/3.1.7/README.md#L405-L411)). Install from the repository release rather than piping a downloaded script straight into a shell. This guide gives no acme.sh walk-through, because it has no verified acme.sh command for issuance, renewal or DNS credentials: follow the project's documentation for release 3.1.7, or use Certbot, Caddy or Traefik as this guide covers them.
- **Caddy and Traefik**: obtain and renew certificates themselves with no external client; see [caddy.md](caddy.md) and [traefik.md](traefik.md). This guide assesses it as the lowest-effort correct option for new deployments.
- **Cloudflare origin certificates**: at the time of writing, Cloudflare's Origin CA page (checked October 2026, cited in Sources) lists them as available on its Free plan, and plan features can change, so confirm there before relying on it; Cloudflare's page refers to long-lived origin CA certificates and says the validity period is chosen at creation. Cloudflare says they only encrypt traffic between Cloudflare and the origin server, not traffic from client browsers to the origin, and that visitors may see untrusted certificate errors if Cloudflare is paused or proxying is disabled; use them only for origins that receive traffic only through Cloudflare-proxied records; see [cloudflare.md](cloudflare.md).

## Verify

REASONED: certificate inventory, HTTPS access and served-certificate hostname, trust, issuer and date inspection follow the cited Certbot and Let's Encrypt guidance and the cited curl and OpenSSL documentation. A demonstration was not run because it needs a public host name with a publicly issued certificate; a local listener with a self-made certificate would test a private CA, not the public trust this block checks. To see the exposed state, point the block at a host serving a Let's Encrypt staging certificate: the staging page says its roots are not in browser or client trust stores ([Let's Encrypt staging environment](https://letsencrypt.org/docs/staging-environment/)). Run the whole block on the server host that holds `/etc/letsencrypt`: `certbot certificates` lists the certificates Certbot knows about on the host it runs on ([Certbot v2.3.0 user guide](https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L356-L361)), so a run on a workstation does not show the server's certificates. Fixed: `certbot certificates` lists the certificate with days remaining, `curl` and `s_client` exit 0, and `x509` prints a public CA as the issuer and a `notAfter` date in the future. Exposed: `curl` exits 60, which libcurl names CURLE_PEER_FAILED_VERIFICATION ([curl curl-8_12_1 error codes](https://github.com/curl/curl/blob/curl-8_12_1/docs/libcurl/libcurl-errors.md#L319-L323)), or `s_client` fails verification. OpenSSL names such verification errors X509_V_ERR_CERT_HAS_EXPIRED, X509_V_ERR_HOSTNAME_MISMATCH and X509_V_ERR_DEPTH_ZERO_SELF_SIGNED_CERT, among others ([OpenSSL 3.0 verify errors](https://docs.openssl.org/3.0/man3/X509_STORE_CTX_get_error/)). The block exits 1 with a FINDING when `curl` exits 60, which curl's OpenSSL backend returns for an untrusted chain, an expired certificate and a name mismatch alike ([curl curl-8_12_1 verification failure](https://github.com/curl/curl/blob/curl-8_12_1/lib/vtls/openssl.c#L4384-L4387), [name mismatch](https://github.com/curl/curl/blob/curl-8_12_1/lib/vtls/openssl.c#L2396-L2398)); `-S` keeps curl's error text, which says which ([curl curl-8_12_1 `--show-error`](https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/show-error.md#L19-L19)). Every other nonzero `curl` exit is inconclusive (3), including 51, which curl-8_12_1 lists as obsolete ([curl curl-8_12_1 obsolete errors](https://github.com/curl/curl/blob/curl-8_12_1/docs/libcurl/libcurl-errors.md#L282-L284)); without `-f`, `curl` exits 0 for an HTTP error status too ([curl curl-8_12_1 `--fail`](https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/fail.md#L21-L29)). `s_client` starts with status 1 ([OpenSSL 3.0.22 s_client.c](https://github.com/openssl/openssl/blob/openssl-3.0.22/apps/s_client.c#L903-L903)), and this guide takes its exit status to show only that it failed, not why (this guide's reading). On a failure the block therefore reads the `verify error:num=N:` line that OpenSSL prints on standard error ([OpenSSL 3.0.22 s_cb.c](https://github.com/openssl/openssl/blob/openssl-3.0.22/apps/lib/s_cb.c#L65-L67)) and exits 1 for N of 9, 10, 18, 19, 20, 21 or 62 ([OpenSSL 3.0.22 verify error numbers](https://github.com/openssl/openssl/blob/openssl-3.0.22/include/openssl/x509_vfy.h.in#L222-L281)), and 3 for any other failure. A finding outranks an inconclusive result. When `certbot certificates`, `curl`, `s_client` and `openssl x509` all exit 0 it prints PASS and exits 0, which means this host's trust store accepted the chain, the dates and the name; it does not show that the issuer is a public CA, so read the issuer line yourself (this guide's reading). If the name resolves to a CDN or proxy, such as a Cloudflare-proxied record, the block checks that edge's certificate, not the one Certbot holds (this guide's reasoning). On a name with several addresses, `curl` and `s_client` each test one, normally the first the name resolves to, so another address can still serve a bad certificate (this guide's reasoning). The block assumes a clean shell, with no function or alias named `curl`, `openssl`, `sudo` or `[`, and the host's default trust store, with `SSL_CERT_FILE`, `SSL_CERT_DIR` and `CURL_CA_BUNDLE` unset: a trust store those variables name can make `curl` and `s_client` accept a certificate that public clients reject (this guide's reasoning). Authoring records are in the Verification record below. The block takes your public host name on a guarded `set --` line that refuses example.com, example.net, example.org and their subdomains, exits 2 when a guard refuses, and otherwise exits once with one status for all of its checks. A certificate alone does not protect anything: continue with the server guide for your stack and with [authentication.md](authentication.md).

```bash
(                                       # the whole block in one subshell, so one exit status covers every part of it
  set +e                                # errexit off here, so a check that ends nonzero is recorded in the status below instead of ending the block
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_HOSTNAME'   # your deployment's public hostname, not example.com (which serves a live page and would pass spuriously), with no scheme, user name, port, path, query, fragment, percent sign or trailing dot: replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 2; }
  case "$1" in
    ""|*REPLACE_WITH_*|*/*|*:*|*.|*[@?%]*|*'#'*|*[[:space:][:cntrl:]]*) echo "substitute your public host name (no scheme, user name, port, path, query, fragment, percent sign or trailing dot) inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  shopt -s nocasematch || { echo "this block needs bash; run it in bash; not probing"; exit 2; }   # host names ignore letter case, so this case matches them in any case through a bash option, not an outside command that could fail
  case "$1" in
    example.com|example.net|example.org|*.example.com|*.example.net|*.example.org) echo "example.com, example.net, example.org and their subdomains are not your deployment: substitute your own host name on the set -- line above; not probing"; exit 2 ;;
  esac
  shopt -u nocasematch   # every match below compares letter case exactly again
  set -- "$1" 0                         # the 2nd value is the block's status so far: 1 (finding) outranks 3 (inconclusive), which outranks 0
  sudo certbot certificates ||          # what is issued and when it expires
    { echo "certbot certificates exit $?: the certificate list could not be read; inconclusive"; [ "$2" = 1 ] || set -- "$1" 3; }
  curl -q -g -sSI "https://$1/"         # -S prints curl's error text despite -s; with normal certificate verification
  set -- "$1" "$2" "$?"                 # the host, the status so far, then curl's exit status
  case "$3" in
    0) ;;                               # verified TLS and an HTTP reply of any status, since this probe has no -f
    60) echo "FINDING: curl exit 60: the served certificate failed verification (untrusted chain, expiry or name mismatch; the error text above says which)"; set -- "$1" 1 ;;
    *) echo "curl exit $3: the HTTPS request failed before a certificate verdict this block classifies; inconclusive"; [ "$2" = 1 ] || set -- "$1" 3 ;;
  esac
  set -- "$1" "$2" "$(if openssl s_client -connect "$1:443" -servername "$1" \
    -verify_hostname "$1" -verify_return_error </dev/null 2>&1; then printf '\n0'; else printf '\n%s' "$?"; fi)"   # s_client's own status, captured with its error text before x509 reads its output
  set -- "$1" "$2" "${3%$'\n'*}" "${3##*$'\n'}"   # the host, the status so far, s_client's output, then its exit status
  if [ "$4" = 0 ]; then
    printf '%s\n' "$3" \
      | openssl x509 -noout -issuer -dates ||
      { echo "openssl x509 exit $?: it could not read the served certificate; inconclusive"; [ "$2" = 1 ] || set -- "$1" 3; }
  else
    printf '%s\n' "$3"                  # s_client's output and error text, since its exit status alone does not say why it failed
    case "$3" in
      *'verify error:num=9:'*|*'verify error:num=10:'*|*'verify error:num=18:'*|*'verify error:num=19:'*|*'verify error:num=20:'*|*'verify error:num=21:'*|*'verify error:num=62:'*)
        echo "FINDING: s_client exit $4 with a verify error above (not yet valid, expired, self-signed, untrusted issuer or hostname mismatch)"; set -- "$1" 1 ;;
      *) echo "s_client exit $4 without a verify error this block classifies (a refused connection, a protocol error or another verify error); inconclusive"; [ "$2" = 1 ] || set -- "$1" 3 ;;
    esac
  fi
  [ "$2" = 0 ] && echo "PASS: curl and s_client verified the chain, dates and name of the certificate served for $1 against this host's trust store"
  echo "block exit $2; the certificate list and the issuer and dates are not classified, so judge them yourself"
  exit "$2"
)
```

REASONED: following block; the CAA check for the CAA records section above, per RFC 8659 sections 3, 4.1, 4.1.1, 4.2 and 4.3, the Let's Encrypt CAA page and the BIND v9.20.24 `dig` manual and source cited in Sources. No deployment was run, so no live result for a reader's deployment is recorded. Authoring records are in the Verification record below. Run it on any host whose resolver offers recursion and answers as public DNS does. It runs `dig -r +noall +comments +answer NAME. CAA` for your host name and then for each parent name up to the top-level domain, stopping at the first reply that holds CAA lines, which is the set a CA checks. With `-r`, `dig` reads no options from `~/.digrc`, so a setting there cannot change the output the block reads. The recursive resolver follows an alias (CNAME), so the block exits 3 for any reply whose flags lack `ra` (recursion available), before it classifies that reply or climbs past it. It also exits 3, before it climbs, for an answer line that is not a comment (a line whose first word is `;` or `;;`) or an `IN CAA`, `IN CNAME` or `IN DNAME` line, such as the generic form `TYPE257 \# ...`: BIND `dig` 9.20.24 printed CAA in that form when given `+unknownformat`, which the block does not pass; a `dig` without CAA support or a non-BIND `dig` may print it. The block never reads `+short` output, which is empty alike for no records, NXDOMAIN and SERVFAIL. Exposed: no name up to the top-level domain has a CAA set, or the set has no `issue` property and has either `issuewild` (a CA ignores `issuewild` for a name that is not a wildcard) or only `iodef`, so any public CA may issue for your host name; it prints FINDING and exits 1. Fixed: an `issue` property, its tag in any letter case, whose value names `letsencrypt.org`, alone or before well-formed `;` parameters, with any spaces around it; it prints PASS and exits 0. A parameter such as `accounturi=` or `validationmethods=` limits only the `issue` property it is on, and the issuer alone defines what a parameter means (RFC 8659 section 4.2 and the Let's Encrypt CAA page); authorizations add up, so another `issue` property naming `letsencrypt.org` without that parameter authorizes Let's Encrypt without the limit. The block does not check parameters against your account or challenge. The block compares the CA name itself exactly, so a value such as `LetsEncrypt.org` counts as another CA. BIND's CAA text form, cited in Sources, prints a tab, another control byte or a non-ASCII byte in a value as a `\` and three digits, such as `\009`, and prints a `"` or `\` after a `\`; the block does not read a value holding a `\`, so it exits 3. RFC 8659 section 4.2 treats an `issue` value that breaks its grammar as one with an empty issuer, which authorizes no CA. The block therefore counts the parameters after `letsencrypt.org;` as well formed only when each is a tag of letters and digits, with hyphens only between them, then `=` and a value of printable ASCII characters other than space and `;`, with optional spaces around each `=` and `;`, no empty parameter and no `;` after the last. Otherwise it counts the property as an empty issuer, as it does `issue ";"`. Under the same section authorizations add up, so an empty or malformed `issue` beside a well-formed one naming `letsencrypt.org` still gives PASS. A set that has `issue` properties but no well-formed one naming `letsencrypt.org` (they name other CAs, are empty or break the grammar) also exits 0, printed as NOT LET'S ENCRYPT and not classified: it is not the exposure, but it does not authorize Let's Encrypt, so issuance and renewal from Let's Encrypt fail; on another CA, check that the set names that CA. The wildcard line reports `issuewild`, which controls wildcard issuance when present, and is not classified; it does not check `issuewild` parameters, not even against the section 4.2 grammar, so when an `issuewild` value names `letsencrypt.org`, the line adds that its parameters are not checked. The block exits 3 when `dig` exits nonzero, when a reply has no single header, when the reply status is not NOERROR (the `dig` manual gives exit 0 for NXDOMAIN, and `dig` 9.20.24 exited 0 on SERVFAIL when observed on 2026-11-11), when a reply has no flags line or no `ra` flag, when an answer line is not a comment or an `IN CAA`, `IN CNAME` or `IN DNAME` line, when a CAA line's flags or value is in a form it does not read (including a value holding a `\`), when a critical property has a tag it does not classify, and when the set has no `issue` or `issuewild` property but has a tag other than `iodef` that it does not classify; it exits 2 when a guard refuses or `dig` is missing. It reads your own resolver, so a split-horizon or filtering resolver or a cached answer can make it differ from what a CA sees. It takes your host name on a guarded `set --` line that refuses example.com, example.net, example.org and their subdomains, needs no sudo, and assumes a clean shell.

```bash
(                                       # the whole block in one subshell, so one exit status covers it
  trap - DEBUG RETURN ERR               # assumes a clean shell (CONTRIBUTING rule 7)
  set +x +a +e                          # no tracing, no allexport, errexit off, so each lookup's result is classified below instead of ending the block
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_HOSTNAME'   # the public host name you request certificates for (for a wildcard *.name, the name after "*."), not example.com, with no scheme, user name, port, path, query, fragment, percent sign or trailing dot: replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 2; }
  case "$1" in
    ""|*REPLACE_WITH_*|*/*|*:*|*.|*[@?%]*|*'#'*|*[[:space:][:cntrl:]]*) echo "substitute your public host name (no scheme, user name, port, path, query, fragment, percent sign or trailing dot) inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  case "$1" in
    *[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-]*|.*|*..*|-*|*.-*) echo "use letters, digits, dots and hyphens only, with no empty label and no label that starts with a hyphen (dig would read it as an option); not probing"; exit 2 ;;
    *.*) ;;
    *) echo "a single-label name is not a public host name: substitute the full name; not probing"; exit 2 ;;
  esac
  shopt -s nocasematch || { echo "this block needs bash; run it in bash; not probing"; exit 2; }   # host names ignore letter case, so this case matches them in any case through a bash option, not an outside command that could fail
  case "$1" in
    example.com|example.net|example.org|*.example.com|*.example.net|*.example.org) echo "example.com, example.net, example.org and their subdomains are not your deployment: substitute your own host name on the set -- line above; not probing"; exit 2 ;;
  esac
  shopt -u nocasematch   # letter case counts again in every match below, except the CAA tag match, which turns this option on for its one case statement
  command -v dig >/dev/null 2>&1 || { echo "dig is not on PATH: install BIND's dig, or run this where it is installed; not probing"; exit 2; }
  { unset -n IFS o t c y f g v p q seen && unset -v IFS o t c y f g v p q seen; } 2>/dev/null || { echo "IFS or a name this block uses (o t c y f g v p q seen) is readonly in this shell: run the block in a fresh bash; not probing"; exit 2; }   # with IFS unset, read splits on any run of spaces and tabs, as dig's columns need
  set -- "$1" "$1" 0                    # the 2nd value is the name looked up now, starting at your host; the 3rd is the block's status
  while :; do
    set -- "$1" "$2" "$3" "$(if dig -r +noall +comments +answer "$2." CAA; then printf '\n0'; else printf '\n%s' "$?"; fi)"   # -r: dig reads no options from ~/.digrc, which its manual calls useful for scripts that need predictable behavior; dig's search list is off by default, and no option here turns it on
    set -- "$1" "$2" "$3" "${4%$'\n'*}" "${4##*$'\n'}"   # the host, the name, the status, dig's output, then dig's exit status
    printf '%s\n' "-- dig -r +noall +comments +answer $2. CAA, exit $5:" "$4"
    [ "$5" = 0 ] || { echo "dig exit $5 for $2. is not 0, the status dig's manual gives for a DNS response received, so this block reads no reply; inconclusive"; set -- "$1" "$2" 3; break; }
    seen=" "
    while read -r o t c y f g v; do     # dig's header and flags lines, then answer lines: name, TTL, class, type, CAA flags, tag, value
      case "$o $t $c $f" in
        ';; ->>HEADER<<- opcode: status:') seen="${seen}header:$g "; continue ;;   # g is the status and its comma, as dig prints the header
      esac
      case "$o $t" in
        ';; flags:'*)                   # the reply's flag words end at the first ";", and dig prints ra among them when the reply says recursion is available
          v=" $c $y $f $g $v"
          case "${v%%;*} " in *' ra '*) seen="${seen}ra " ;; *) seen="${seen}nora " ;; esac
          continue ;;
      esac
      case "$o" in ''|';'|';;') continue ;; esac   # blank lines and dig's other comment lines, whose first word is ; or ;; alone, are printed above, not classified; every other line, including one whose owner name starts with ;, is classified below
      case "$c $y" in
        'IN CAA') seen="${seen}caa " ;;
        'IN CNAME'|'IN DNAME') continue ;;   # alias lines are printed above, not classified
        *) seen="${seen}unread "; continue ;;   # any other answer line, such as a CAA record in the generic form (TYPE257), is a form this block does not read
      esac
      case "$f" in 0|128) ;; *) seen="${seen}badflags " ;; esac
      case "$v" in
        *\\*) seen="${seen}badvalue "; v="" ;;   # dig prints a control byte in a value as \ and three digits (a tab as \009), and a " or \ after a \; this block does not read a value holding a \
        '"'*'"') v="${v#?}"; v="${v%?}"; p="${v#"${v%%;*}"}"; p="${p#;}"; v="${v%%;*}"; read -r v <<< "$v" ;;   # v is the CA identifier: the quoted value up to any ";" parameters, without the spaces RFC 8659 section 4.2 allows around it, which read drops because IFS is unset (it would drop raw tabs too, which dig does not print); p is the text after the first ";"
        *) seen="${seen}badvalue "; v="" ;;
      esac
      shopt -s nocasematch              # RFC 8659 section 4.1: tags match in any letter case, so this case writes each tag it knows in lower case
      case "$g" in issue) g=issue ;; issuewild) g=issuewild ;; iodef) g=iodef ;; esac
      shopt -u nocasematch              # the CA identifier below is compared exactly, letter case included
      case "$g" in
        issue)
          if [ "$v" = letsencrypt.org ]; then   # RFC 8659 section 4.2: after the ";" come nothing or parameters, each tag *WSP "=" *WSP value, separated by *WSP ";" *WSP; an issue value that breaks this grammar counts as an empty issuer, which authorizes no CA, so v is emptied
            read -r p <<< "$p"          # the parameters, without the spaces around them
            while [ -n "$p" ]; do
              q="${p%%;*}"; p="${p#"$q"}"   # q is the next parameter; p keeps the rest, from its ";"
              read -r o t c <<< "${q/=/ = }"   # o, t and c are free once the line is classified: here they take the tag, the first "=" and the value
              case "$o" in ""|-*|*-|*[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-]*) v=""; break ;; esac   # a tag: letters and digits, with hyphens only between them
              [ "$t" = '=' ] || { v=""; break; }
              case "$c" in *[[:space:][:cntrl:]]*|*[![:ascii:]]*) v=""; break ;; esac   # a value: printable ASCII other than space and ";" (q holds no ";", and a \ was refused above), so it refuses a space, a control character or a non-ASCII character
              [ -z "$p" ] || { read -r p <<< "${p#;}"; [ -n "$p" ] || { v=""; break; }; }   # a ";" must be followed by another parameter
            done
          fi
          if [ "$v" = letsencrypt.org ]; then seen="${seen}issue-le "; else seen="${seen}issue-other "; fi ;;
        issuewild) if [ "$v" = letsencrypt.org ]; then seen="${seen}wild-le "; else seen="${seen}wild-other "; fi ;;
        iodef) ;;
        *) if [ "$f" = 128 ]; then seen="${seen}critical-other "; else seen="${seen}other "; fi ;;
      esac
    done <<< "$4"
    case "$seen" in
      *' header:'*' header:'*) echo "dig printed more than one reply header for $2.; this block reads a single reply only; inconclusive"; set -- "$1" "$2" 3; break ;;
      *' header:NOERROR, '*) ;;
      *' header:'*) echo "the reply status for $2. is not NOERROR, and this block does not classify any other status (dig's manual gives exit 0 for NXDOMAIN, and dig 9.20.24 exited 0 on SERVFAIL when observed on 2026-11-11); inconclusive"; set -- "$1" "$2" 3; break ;;
      *) echo "dig printed no reply header for $2., so this block cannot read the reply; inconclusive"; set -- "$1" "$2" 3; break ;;
    esac
    case "$seen" in
      *' nora '*) echo "the reply for $2. lacks the ra flag, so recursion was not available and an alias (CNAME) in it may come without its target's records; this block reads only a recursive resolver's reply; inconclusive"; set -- "$1" "$2" 3; break ;;
      *' ra '*) ;;
      *) echo "dig printed no flags line for $2., so whether recursion was available is unknown; inconclusive"; set -- "$1" "$2" 3; break ;;
    esac
    case "$seen" in
      *' unread '*) echo "an answer line in the reply for $2. is in a form this block does not read (it reads IN CAA lines and passes over comments and IN CNAME and IN DNAME alias lines); inconclusive"; set -- "$1" "$2" 3; break ;;
    esac
    case "$seen" in
      *' caa '*) ;;
      *) case "$2" in
           *.*) set -- "$1" "${2#*.}" "$3"; continue ;;   # no CAA set at this name: climb one label toward the root
           *) echo "FINDING: no CAA record set at $1. or at any parent name up to $2., so any public CA may issue for $1"; set -- "$1" "$2" 1; break ;;
         esac ;;
    esac
    echo "the relevant CAA set is the one in the reply for $2. (this block does not check the owner names of its CAA lines)"
    case "$seen" in
      *' badflags '*|*' badvalue '*) echo "a CAA line's flags or value is in a form this block does not read; inconclusive"; set -- "$1" "$2" 3 ;;
      *' critical-other '*) echo "a CAA property marked critical (flags 128) has a tag other than issue, issuewild or iodef; a CA that does not recognize it must not issue, and this block does not classify it; inconclusive"; set -- "$1" "$2" 3 ;;
      *' issue-le '*) echo "PASS: a well-formed issue property names letsencrypt.org, so the set restricts which CAs may issue and authorizes Let's Encrypt for $1; a parameter such as accounturi= (ACME account) or validationmethods= (validation methods) limits only the property it is on, and authorizations add up, so another issue property naming letsencrypt.org without that parameter lifts the limit; this block does not check parameters against your account or challenge"; set -- "$1" "$2" 0 ;;
      *' issue-other '*) echo "NOT LET'S ENCRYPT: the set restricts issuance, but no well-formed issue property names letsencrypt.org (RFC 8659 section 4.2 treats an issue value that breaks its grammar as an empty issuer, which authorizes no CA), so it does not authorize Let's Encrypt to issue or renew for $1; if you use another CA, check that the set names that CA; not classified"; set -- "$1" "$2" 0 ;;
      *' wild-'*) echo "FINDING: the set has issuewild but no issue property, and a CA ignores issuewild for a name that is not a wildcard, so CAA does not restrict issuance for $1"; set -- "$1" "$2" 1 ;;
      *' other '*) echo "the set has no issue or issuewild property, and it has a tag other than iodef that this block does not classify; inconclusive"; set -- "$1" "$2" 3 ;;
      *) echo "FINDING: the set has no issue or issuewild property (iodef only), so CAA does not restrict issuance for $1"; set -- "$1" "$2" 1 ;;
    esac
    case "$seen" in
      *' wild-le '*) echo "wildcard *.$1: an issuewild property names letsencrypt.org (its parameters are not checked)" ;;
      *' wild-other '*) echo "wildcard *.$1: the set has issuewild properties and none names letsencrypt.org, so it does not authorize Let's Encrypt for a wildcard" ;;
      *) echo "wildcard *.$1: no issuewild property, so the issue result above governs wildcard issuance too" ;;
    esac
    break
  done
  echo "block exit $3; the dig output and the wildcard line are not classified, so judge them yourself"
  exit "$3"
)
```

REASONED: following block; the credentials-file check for the DNS-01 step above, from the GNU coreutils `stat` manual (rolling documentation, checked November 2026) and the cited Certbot v2.3.0 source. Run it on the host that runs Certbot: under `sudo` it reads `stat -L -c '%a %U %n'` for `/root/.secrets` and `/root/.secrets/cloudflare.ini`, the octal permission bits, owner and name ([GNU coreutils stat](https://www.gnu.org/software/coreutils/manual/html_node/stat-invocation.html)), and `-L` reads what a link points to. It compares the bits as octal numbers, so `600` and `0600` read alike (this guide's reasoning). Exposed: the directory has a group or other bit, the file has a group or other bit, or either is not owned by root; it prints FINDING and exits 1. Certbot v2.3.0 warns only when other users have a permission bit on the credentials file ([Certbot v2.3.0 dns_common.py](https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/plugins/dns_common.py#L342-L348), [filesystem.py](https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/compat/filesystem.py#L444-L453)), so a FINDING for a group bit or for the directory is this guide's stricter rule, not Certbot's. Fixed: both are owned by root with no group or other bit, such as `700` and `600`; it prints PASS and exits 0. It exits 3 when `stat` fails, as it does for a file kept at another path, which this block does not search for, or prints a form it does not read, and 2 when a name it uses is readonly; for another path, change both paths in the block. It assumes a clean shell, with no function or alias named `sudo`, `stat` or `[`. It does not check the private key: Certbot keeps a key's changed group mode on renewal, and its user guide gives `chmod 0640` for a server that drops root, so a key check would have to accept `640` as well as `600`. Authoring records are in the Verification record below.

```bash
(                                       # the whole block in one subshell, so one exit status covers it
  set +e                                # errexit off, so a nonzero stat is classified below instead of ending the block
  { unset -n IFS dm du dn fm fu fn && unset -v IFS dm du dn fm fu fn; } 2>/dev/null || { echo "IFS or a name this block uses (dm du dn fm fu fn) is readonly in this shell: run the block in a fresh bash; not probing"; exit 2; }   # with IFS unset, read splits stat's line on spaces
  set -- 0 "$(if sudo stat -L -c '%a %U %n' /root/.secrets /root/.secrets/cloudflare.ini; then printf '\n0'; else printf '\n%s' "$?"; fi)"   # -L reads the mode of what a link points to, as Certbot's own check does
  set -- "$1" "${2%$'\n'*}" "${2##*$'\n'}"   # the status so far, stat's output, then stat's exit status
  printf '%s\n' "-- stat -L -c '%a %U %n', exit $3:" "$2"
  [ "$3" = 0 ] || { echo "stat exit $3: the mode of /root/.secrets or of its cloudflare.ini could not be read (missing, kept at another path, or sudo refused); inconclusive"; exit 3; }
  { read -r dm du dn && read -r fm fu fn; } <<< "$2"   # mode, owner and name of the directory, then of the file
  case "$dm $fm" in ' '*|*' ') echo "a mode is not in the octal form this block reads; inconclusive"; exit 3 ;; esac; case "${dm// }${fm// }" in *[!01234567]*) echo "a mode is not in the octal form this block reads; inconclusive"; exit 3 ;; esac
  [ "$dn" = /root/.secrets ] && [ "$fn" = /root/.secrets/cloudflare.ini ] && [ "${#dm}" -le 4 ] && [ "${#fm}" -le 4 ] || { echo "stat printed lines this block does not read; inconclusive"; exit 3; }
  [ "$du" = root ] || { echo "FINDING: /root/.secrets is owned by $du, not root"; set -- 1; }
  [ $((8#$dm & 8#077)) = 0 ] || { echo "FINDING: /root/.secrets has mode $dm, so its group or other users can list or enter it; this guide asks for 700 (Certbot does not check the directory)"; set -- 1; }
  [ "$fu" = root ] || { echo "FINDING: /root/.secrets/cloudflare.ini is owned by $fu, not root"; set -- 1; }
  [ $((8#$fm & 8#007)) = 0 ] || { echo "FINDING: /root/.secrets/cloudflare.ini has mode $fm, so other users can read or change it; Certbot warns about this too"; set -- 1; }
  [ $((8#$fm & 8#070)) = 0 ] || { echo "FINDING: /root/.secrets/cloudflare.ini has mode $fm, so its group can read or change it; this guide asks for 600, which is stricter than Certbot's warning on other users only"; set -- 1; }
  [ "$1" = 0 ] && echo "PASS: /root/.secrets is mode $dm and cloudflare.ini mode $fm, both owned by root, with no group or other bits"
  echo "block exit $1"
  exit "$1"
)
```

### Verification record

REASONED: what was run on the three blocks above, and on what. The first block's classification of `curl` exit 60 and of OpenSSL verify errors was not run against a real untrusted, expired or mismatched certificate: that needs a public host name with an issued certificate, and no listener may be started on the authoring host. No deployment hostname or issued certificate was supplied for live checks, no live result is recorded, and no run of this block is recorded. The first and third blocks passed `bash -n` and ShellCheck 0.11.0 on 2026-11-26. On 2026-11-26 the third ran in bash 5.3.9 with a stub `sudo` printing 12 `stat` outputs: `700` and `600`, `0700` and `0600`, and `1700` and `600`, owned by root, gave PASS; a file at `640` or `604`, a directory at `755` and a file owned by another user gave FINDING; a failed `stat` and four unread forms gave 3. It was not run against a real credentials directory.

REASONED: The next sentences record the second block, the CAA check, which was the final block of this section when they were written. The final block passed `bash -n` and ShellCheck 0.11.0, and on 2026-11-12 it ran with real `dig` 9.20.24 through the host's systemd-resolved resolver against public domains: two Let's Encrypt sets, a CNAME whose target has CAA lines and one that falls back to its parent, another CA only, no CAA set at two names, NXDOMAIN and SERVFAIL. The no-reply case did not use that resolver: it ran the real `dig` through a wrapper that added `+time=1 +tries=1` and sent the query to a closed port on 127.0.0.1. Each exited with its expected status, as did the reserved-name refusal. A fake `dig` supplied the iodef-only and issuewild-only cases, an `issuewild "letsencrypt.org; %%%"`-only set, which exited 1 with a FINDING and a wildcard line that names letsencrypt.org and says its parameters are not checked, two iodef-only sets at a child name under a parent whose set authorizes Let's Encrypt, one whose owner name starts with a raw `;` and one whose owner name starts with an escaped `\;`, each of which exited 1 with a FINDING, three replies without the `ra` flag (one holding only a CNAME) and one with `ra` and `ad`, `issue`, `issuewild` and `iodef` tags in upper and mixed case, spaces and parameters around the CA name, a CA name in mixed case, an `issue ";"` beside `issuewild`, `iodef` with an unknown tag and a critical unknown tag beside a Let's Encrypt `issue`, and, for exit 3, an `issue` value holding `\009` and one holding `\"`, a `TYPE257` generic line, in `IN` and in `CLASS1` form, at a child name under a parent whose set authorizes Let's Encrypt, and an RRSIG line beside a Let's Encrypt `issue`; for exit 0 with NOT LET'S ENCRYPT, `issue "letsencrypt.org; %%%"` in two reply forms, parameters that end in `;`, whose tag starts with a hyphen or whose value holds a space or a non-ASCII character, and a word after the CA name; for exit 0 with PASS, that malformed value beside a well-formed Let's Encrypt `issue`, well-formed parameters, among them an `accounturi=` parameter, punctuation-only parameters, nothing after the `;`, a DNAME and CNAME before the target's set, and a CNAME to a set with an upper-case tag; and, for exit 3, replies with no flags line, an empty flags line, two reply headers, an upper-case `RA` and a lower-case status. Each exited with its expected status and result.

## Sources (checked September 2026)

The month in this heading is the month of the whole-guide documentation pass, and an item that carries its own later "checked" month was rechecked individually after that pass, so the later month applies to that item only.

- Let's Encrypt documentation (rolling documentation, checked September 2026): https://letsencrypt.org/docs/
- Certbot instructions (rolling documentation, checked September 2026): https://certbot.eff.org/
- Certbot reconfigure (2.3.0 and later; v2.3.0 user guide): https://raw.githubusercontent.com/certbot/certbot/v2.3.0/certbot/docs/using.rst
- Certbot manual DNS-01 and renewal hooks (rolling documentation, checked September 2026): https://eff-certbot.readthedocs.io/en/stable/using.html#manual
- Certbot DNS plugins (rolling documentation, checked September 2026): https://eff-certbot.readthedocs.io/en/stable/using.html#dns-plugins
- ZeroSSL ACME documentation, EAB credentials required, not stored in the account and reusable (rolling documentation, checked November 2026): https://zerossl.com/documentation/acme/
- ZeroSSL EAB credentials API, `eab_kid` and `eab_hmac_key` fields (rolling documentation, checked November 2026): https://zerossl.com/documentation/acme/generate-eab-credentials/
- acme.sh 3.1.7 README, ZeroSSL as the default CA (checked November 2026): https://github.com/acmesh-official/acme.sh/blob/3.1.7/README.md#L149-L153
- acme.sh 3.1.7 README, DNS provider API support (checked November 2026): https://github.com/acmesh-official/acme.sh/blob/3.1.7/README.md#L405-L411
- acme.sh 3.1.7 account registration saves EAB credentials to the CA configuration (checked November 2026): https://github.com/acmesh-official/acme.sh/blob/3.1.7/acme.sh#L4542-L4612
- acme.sh 3.1.7 `_savecaconf` writes to the CA configuration file (checked November 2026): https://github.com/acmesh-official/acme.sh/blob/3.1.7/acme.sh#L3139-L3141
- acme.sh 3.1.7 `_save_conf` writes through `_setopt` (checked November 2026): https://github.com/acmesh-official/acme.sh/blob/3.1.7/acme.sh#L2963-L2985
- acme.sh 3.1.7 `_setopt` creates a missing configuration file with mode 600 (checked November 2026): https://github.com/acmesh-official/acme.sh/blob/3.1.7/acme.sh#L2900-L2914
- Let's Encrypt staging environment, roots not in trust stores (rolling documentation, checked November 2026): https://letsencrypt.org/docs/staging-environment/
- Let's Encrypt certificate lifetimes (rolling documentation, checked September 2026): https://letsencrypt.org/docs/cert-lifetimes/
- Let's Encrypt lifetime reduction schedule (announcement dated 2025-12-02, checked September 2026): https://letsencrypt.org/2025/12/02/from-90-to-45
- Let's Encrypt OCSP end of life (announcement dated 2025-08-06, checked September 2026): https://letsencrypt.org/2025/08/06/ocsp-service-has-reached-end-of-life
- Let's Encrypt CAA requirements (rolling documentation, checked November 2026): https://letsencrypt.org/docs/caa/
- RFC 8659 CAA relevant record set, its climb toward the root and alias chasing, section 3 (checked November 2026): https://www.rfc-editor.org/rfc/rfc8659#section-3
- RFC 8659 CAA tags match case-insensitively, section 4.1 (checked November 2026): https://www.rfc-editor.org/rfc/rfc8659#section-4.1
- RFC 8659 CAA canonical presentation format, section 4.1.1 (checked November 2026): https://www.rfc-editor.org/rfc/rfc8659#section-4.1.1
- RFC 8659 CAA issue value grammar, with optional whitespace (WSP) around the issuer domain name, section 4.2 (checked November 2026): https://www.rfc-editor.org/rfc/rfc8659#section-4.2
- RFC 8659 CAA issuewild ignored for a name that is not a wildcard, section 4.3 (checked November 2026): https://www.rfc-editor.org/rfc/rfc8659#section-4.3
- BIND v9.20.24 `dig` return codes, with exit 0 on NXDOMAIN (checked November 2026): https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/bin/dig/dig.rst#L788-L806
- BIND v9.20.24 `dig` `+noall` and `+answer` display options (checked November 2026): https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/bin/dig/dig.rst#L255-L262
- BIND v9.20.24 `dig` `+comments` header display (checked November 2026): https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/bin/dig/dig.rst#L308-L312
- BIND v9.20.24 `dig` search list off by default (checked November 2026): https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/bin/dig/dig.rst#L598-L606
- BIND v9.20.24 `dig` `-r` reads no options from `${HOME}/.digrc` (checked November 2026): https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/bin/dig/dig.rst#L160-L163
- BIND v9.20.24 `dig` reply header line format (checked November 2026): https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/bin/dig/dig.c#L864-L884
- BIND v9.20.24 `dig` reply flags line, including `ra`, and its recursion-not-available warning (checked November 2026): https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/bin/dig/dig.c#L885-L924
- BIND v9.20.24 `dig` `+short` prints every answer record, aliases included (checked November 2026): https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/bin/dig/dig.c#L586-L630
- BIND v9.20.24 CAA text form prints the value as a quoted string (checked November 2026): https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/lib/dns/rdata/generic/caa_257.c#L331-L362
- BIND v9.20.24 quoted-string text form escapes a byte below 0x20 or from 0x7f as a backslash and three decimal digits, and a double quote or backslash with a backslash (checked November 2026): https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/lib/dns/rdata.c#L1886-L1944
- Caddy v2.11.4 automatic certificate acquisition and renewal (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/autohttps.go#L62-L63
- Caddy v2.11.4 ACME TLS-ALPN challenge settings (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddytls/acmeissuer.go#L280-L296
- Caddy v2.11.4 builds its ACME issuer template at provisioning (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddytls/acmeissuer.go#L245-L249
- Caddy v2.11.4 passes its ACME issuer template to certmagic (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddytls/acmeissuer.go#L321-L328
- Caddy v2.11.4 pins certmagic v0.25.3 (checked October 2026): https://github.com/caddyserver/caddy/blob/v2.11.4/go.mod#L12-L12
- certmagic v0.25.3 TLS-ALPN-01 solver selection (checked October 2026): https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeclient.go#L188-L226
- certmagic v0.25.3 TLS-ALPN challenge listener port (checked October 2026): https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeclient.go#L304-L313
- certmagic v0.25.3 alternate TLS-ALPN port forwarding (checked October 2026): https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeissuer.go#L116-L120
- certmagic v0.25.3 issuer defaults for the DNS-01 solver and TLS-ALPN setting (checked October 2026): https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeissuer.go#L222-L236
- certmagic v0.25.3 TLS-ALPN challenge port 443 (checked October 2026): https://github.com/caddyserver/certmagic/blob/v0.25.3/certmagic.go#L473-L475
- certmagic v0.25.3 `DefaultACME` values (checked October 2026): https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeissuer.go#L647-L654
- Traefik v3.5 ACME renewal and challenges (checked October 2026): https://doc.traefik.io/traefik/v3.5/reference/install-configuration/tls/certificate-resolvers/acme/
- OpenSSL 3.0 `s_client` connection and certificate verification (checked October 2026): https://docs.openssl.org/3.0/man1/openssl-s_client/
- OpenSSL 3.0 `x509` issuer and validity dates (checked October 2026): https://docs.openssl.org/3.0/man1/openssl-x509/
- OpenSSL 3.0 certificate verification error names (rolling documentation, checked November 2026): https://docs.openssl.org/3.0/man3/X509_STORE_CTX_get_error/
- OpenSSL 3.0.22 `s_client` status starts at 1 (checked November 2026): https://github.com/openssl/openssl/blob/openssl-3.0.22/apps/s_client.c#L903-L903
- OpenSSL 3.0.22 verify callback prints `verify error:num=` on standard error (checked November 2026): https://github.com/openssl/openssl/blob/openssl-3.0.22/apps/lib/s_cb.c#L65-L67
- OpenSSL 3.0.22 verify error numbers (checked November 2026): https://github.com/openssl/openssl/blob/openssl-3.0.22/include/openssl/x509_vfy.h.in#L222-L281
- curl curl-8_12_1 HEAD requests (checked October 2026): https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/head.md#L21-L22
- curl curl-8_12_1 normal certificate verification and `--insecure` (checked October 2026): https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/insecure.md#L21-L28
- curl curl-8_12_1 exit code 60 (checked November 2026): https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/_EXITCODES.md#L125-L126
- curl curl-8_12_1 CURLE_PEER_FAILED_VERIFICATION (60) (checked November 2026): https://github.com/curl/curl/blob/curl-8_12_1/docs/libcurl/libcurl-errors.md#L319-L323
- curl curl-8_12_1 OpenSSL backend maps a failed chain or expiry check to CURLE_PEER_FAILED_VERIFICATION (checked November 2026): https://github.com/curl/curl/blob/curl-8_12_1/lib/vtls/openssl.c#L4384-L4387
- curl curl-8_12_1 OpenSSL backend maps a subject alternative name mismatch to CURLE_PEER_FAILED_VERIFICATION (checked November 2026): https://github.com/curl/curl/blob/curl-8_12_1/lib/vtls/openssl.c#L2396-L2398
- curl curl-8_12_1 `--show-error` with `--silent` (checked November 2026): https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/show-error.md#L19-L19
- curl curl-8_12_1 obsolete errors 50 and 51 (checked November 2026): https://github.com/curl/curl/blob/curl-8_12_1/docs/libcurl/libcurl-errors.md#L282-L284
- curl curl-8_12_1 `--fail`; HTTP status is not a failure by default (checked November 2026): https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/fail.md#L21-L29
- Certbot v2.3.0 scheduled renewal guidance (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L808-L825
- Certbot v2.3.0 renew selection (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L632-L640
- Certbot v2.3.0 renewal option persistence (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L704-L710
- Certbot v2.3.0 deploy hooks (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L659-L684
- Certbot v2.3.0 DNS plugins (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L194-L220
- Certbot v2.3.0 manual DNS-01 and renewal (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L222-L265
- Certbot v2.3.0 deploy-hook argument storage (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/cli/cli_utils.py#L227-L231
- Certbot v2.3.0 renewal option list (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/renewal.py#L40-L53
- Certbot v2.3.0 due-renewal branch (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/renewal.py#L509-L534
- Certbot v2.3.0 relevant saved values (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L295-L312
- Certbot v2.3.0 initial renewal configuration (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L1120-L1128
- Certbot v2.3.0 renewed configuration (checked October 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L1243-L1249
- Certbot v2.3.0 private key mode constant (checked November 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L48-L48
- Certbot v2.3.0 directory modes and first private key (checked November 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L1064-L1105
- Certbot v2.3.0 renewed private key mode (checked November 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L1222-L1230
- Certbot v2.3.0 key and directory permissions (checked November 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L891-L914
- Certbot v2.3.0 `certificates` subcommand (checked November 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L356-L361
- Certbot v2.3.0 Cloudflare DNS credentials (checked October 2026): <https://github.com/certbot/certbot/blob/v2.3.0/certbot-dns-cloudflare/certbot_dns_cloudflare/__init__.py#L24-L39>
- Certbot v2.3.0 Cloudflare DNS credential permissions (checked October 2026): <https://github.com/certbot/certbot/blob/v2.3.0/certbot-dns-cloudflare/certbot_dns_cloudflare/__init__.py#L61-L78>
- Certbot v2.3.0 credentials-file permission warning (checked November 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/plugins/dns_common.py#L342-L348
- Certbot v2.3.0 other-user permission test (checked November 2026): https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/compat/filesystem.py#L444-L453
- GNU coreutils `stat`: `%a`, `%U`, `%n` and `-L` (rolling documentation, checked November 2026): https://www.gnu.org/software/coreutils/manual/html_node/stat-invocation.html
- Cloudflare Origin CA (rolling documentation, checked October 2026): https://developers.cloudflare.com/ssl/origin-configuration/origin-ca/


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, and any earlier-form run it rests on, not a live demonstration of the shipped form. Unknown means no version recorded.

Components (recorded basis):

- le: Let's Encrypt documentation (unknown)
- zerossl: ZeroSSL (unknown)
- certbot: Certbot documentation (unknown)
- reconfigure: Certbot reconfigure minimum (2.3.0)
- acme: acme.sh (3.1.7)
- certbot-v230: Certbot user guide and source (v2.3.0)
- certbot-dns-cloudflare-v230: Certbot Cloudflare DNS plugin (v2.3.0)
- caddy: Caddy automatic HTTPS (v2.11.4)
- certmagic: certmagic ACME implementation (v0.25.3)
- traefik: Traefik ACME documentation (v3.5)
- cloudflare-origin-ca: Cloudflare Origin CA documentation (checked October 2026)
- openssl-cli: OpenSSL certificate commands (3.0)
- curl-source: curl command documentation (curl-8_12_1)
- openssl-source: OpenSSL source (openssl-3.0.22)
- coreutils-stat: GNU coreutils stat manual (checked November 2026)
- bind-dig: BIND dig manual and source (v9.20.24)
- rfc8659: CAA specification (RFC 8659)

Claims (full source mapping in the JSON block below):

- public-trust (REASONED; le, zerossl): ACME CAs such as Let's Encrypt and ZeroSSL issue free publicly trusted certificates; this guide advises preferring them for public DNS names, including private hosts using DNS-01.
- http-challenge (REASONED; le): HTTP-01 needs a public A/AAAA or CNAME pointing to the server and inbound internet access to port 80.
- alpn-challenge (REASONED; le, caddy, certmagic, traefik): TLS-ALPN-01 needs a public DNS record and inbound port 443; Caddy's ACME issuer enables the TLS-ALPN-01 solver when DNS-01 is not configured and TLS-ALPN-01 is not disabled, and can use an alternate local port if port 443 forwards to it; Traefik also uses TLS-ALPN-01.
- dns-challenge (REASONED; le, certbot, certbot-v230): DNS-01 needs control of the challenge TXT record, no public address record or inbound port, and supports wildcards. Automated issuance and renewal need an automated way to update TXT records, and this guide advises a provider DNS plugin and scoped API credentials, while Certbot also supports manual DNS-01 and an authentication hook for automatic renewal.
- certbot-install (REASONED; certbot): Install Certbot and nginx/Apache plugins from the distribution, or the classic snap with /usr/bin/certbot pointing to /snap/bin/certbot.
- server-plugins (REASONED; certbot): certbot --nginx or --apache issues and installs certificates for the supplied domain names when the server is supported.
- standalone (REASONED; certbot): certonly --standalone binds port 80; stop its current owner and arrange webroot, a server plugin or port-freeing hooks for unattended renewal.
- webroot (REASONED; certbot): certonly --webroot uses /var/www/html to serve challenge files while the existing web server keeps running.
- dns-credentials (REASONED; certbot, certbot-dns-cloudflare-v230): The Cloudflare DNS plugin uses a credentials file and a Zone:DNS:Edit token limited to required zones; this guide requires never using the Global API Key and protecting the file with mode 600 in a 700 directory.
- certificate-paths (REASONED; certbot): Configure servers against stable /etc/letsencrypt/live/example.com/fullchain.pem and privkey.pem paths for the chain and private key.
- renewal-schedule (REASONED; certbot, certbot-v230): The Certbot v2.3.0 user guide says most installations have a scheduled task running certbot renew and says that, on Linux and BSD, you can check cron or systemd timers if unsure; this guide requires confirming the task and testing renewal plus reload with --dry-run --run-deploy-hooks, including package and snap installations.
- deploy-hook (REASONED; certbot, certbot-v230): This guide requires persisting a reload hook during successful initial issuance or successful renewal, or installing an executable in renewal-hooks/deploy; Certbot v2.3.0 saves the renewal-relevant options set on the command line to a lineage after successful renewal, and a renew --deploy-hook invocation with no renewal due does not save that hook.
- reconfigure (REASONED; reconfigure): certbot reconfigure can add the reload hook later on Certbot 2.3.0 and later.
- expiry-monitoring (REASONED; le, certbot): Monitor the served certificate's expiry and renewal failures instead of relying on CA reminder emails; include a dry run in the deployment checklist. This guide assesses that any renewal step involving a person will fail at those scheduled shorter certificate lifetimes and that unattended automation is the only viable path.
- default-lifetime (REASONED; le): At the guide's September 2026 documentation check, Let's Encrypt's default certificate lifetime is 90 days.
- short-lifetime (REASONED; le): Optional 6-day short-lived certificates are available to every subscriber as of the guide's September 2026 check.
- lifetime-schedule (REASONED; le): The classic profile moves to 64 days on 2027-02-10 and 45 days on 2028-02-16; industry rules cap publicly trusted certificates at 47 days from 2029-03-15.
- revocation (REASONED; le): Let's Encrypt ended OCSP on 2025-08-06 and publishes revocation through CRLs only; do not add OCSP stapling directives for its certificates.
- staging (REASONED; le, certbot): Let's Encrypt limits per-domain issuance; test with certbot --staging or --test-cert before real issuance.
- caa (REASONED; le, rfc8659): CAA restricts issuing CAs, using issue letsencrypt.org for Let's Encrypt; certificate-transparency monitoring detects mis-issuance afterwards and complements CAA. A CA uses the closest CAA set, following aliases and climbing from the requested name toward the root, so a registered-domain set covers subdomains without their own; issuewild, when present, controls wildcard issuance.
- zerossl-eab (REASONED; zerossl): ZeroSSL offers free ACME certificates; its ACME service needs EAB credentials, eab_kid and eab_hmac_key, from the dashboard or its API, which ZeroSSL says are not stored in the account, are reusable and all stay functional; this guide treats them as secrets kept out of shell history and repositories.
- acme-default (REASONED; acme): acme.sh 3.1.7 lists ZeroSSL as its default CA.
- acme-install (REASONED; acme): acme.sh is a shell ACME client supporting many DNS providers; the guide recommends installation from a repository release instead of piping a download into a shell, and gives no acme.sh walk-through because it has no verified acme.sh command.
- acme-eab-storage (REASONED; acme): acme.sh 3.1.7 saves EAB credentials given at registration as CA_EAB_KEY_ID and CA_EAB_HMAC_KEY in its CA configuration file, which it creates with mode 600 when the file does not exist.
- server-automation (REASONED; le, caddy, traefik): This guide advises Caddy or Traefik for built-in issuance and renewal without an external client; it assesses them as the lowest-effort correct option for new deployments.
- origin-certificates (REASONED; le, cloudflare-origin-ca): At the guide's October 2026 check, Cloudflare listed Origin CA certificates on its Free plan, which can change; it says they only encrypt traffic between Cloudflare and the origin, and that visitors may see untrusted certificate errors when Cloudflare is paused or proxying is disabled. This guide restricts their use to origins that receive traffic only through Cloudflare-proxied records.
- verify-inventory (REASONED; certbot): certbot certificates lists issued certificates and their expiry dates.
- verify-https (REASONED; le, curl-source): Use the deployment's public hostname rather than example.com; curl HTTPS should succeed without -k.
- verify-certificate (REASONED; le, openssl-cli): The OpenSSL probe targets the hostname on port 443 with SNI, hostname verification and verification errors enabled, then displays issuer and dates.
- verify-caa (REASONED; le, bind-dig, rfc8659): dig -r +noall +comments +answer CAA for the host, then each parent to the TLD, until a reply has CAA lines. Exit 1 (exposed): no set, or only iodef or issuewild. Exit 0: a well-formed letsencrypt.org issue (fixed), or other issues only (not classified). Exit 3: dig exit not 0, no single NOERROR header, no ra flag, an unread form, a critical unknown tag, or an unknown tag and no issue or issuewild.
- authentication (REASONED; le): A certificate alone is insufficient protection; continue with server controls and authentication.
- dns-automation (REASONED; certbot, certbot-v230): For automated DNS-01 issuance and renewal, this guide advises using a provider DNS plugin and least-privilege API credentials; Certbot also documents manual TXT entry and authentication hooks that automate the challenge.
- dns-manual (REASONED; certbot, certbot-v230): certbot certonly --manual --preferred-challenges dns permits hand-created TXT records; the Certbot v2.3.0 guide says certificates created with --manual do not support automatic renewal without a --manual-auth-hook that automates the challenge.
- private-key-at-rest (REASONED; certbot-v230): This guide advises keeping the private key on the server, readable only by the account that runs the server or deploy hook; Certbot v2.3.0 creates the live, archive and renewal directories with mode 0700, writes each new private key with mode 0600, and keeps a changed key group mode or group owner on renewal.
- verify-outcomes (REASONED; certbot-v230, curl-source, openssl-cli, openssl-source): Run Verify block 1 on the Certbot host. Fixed: the certificate is listed, curl and s_client exit 0, and the issuer is a public CA with notAfter in the future. Exposed: curl exit 60 (CURLE_PEER_FAILED_VERIFICATION) or s_client verify error 9, 10, 18-21 or 62, such as X509_V_ERR_CERT_HAS_EXPIRED; it exits 1 for these, 3 for curl 51 or any other failure, 2 for a refused guard.
- verify-classification (REASONED; curl-source, openssl-source): Verify block 1 exits 1 when curl exits 60, which the OpenSSL backend returns for an untrusted chain, expiry or name mismatch, or when s_client fails with verify error 9, 10, 18, 19, 20, 21 or 62; 2 for a refused guard; 3 for any other failure, curl 51 included; 0 only when certbot, curl, s_client and x509 all exit 0, judged against the host trust store, which does not prove a public CA.
- verify-credential-mode (REASONED; certbot-dns-cloudflare-v230, certbot-v230, coreutils-stat): Verify block 3 runs sudo stat -L -c %a %U %n on /root/.secrets and cloudflare.ini on the Certbot host: exit 1 for a group or other bit or a non-root owner (the group and directory rules are this guide's, stricter than Certbot's other-users warning), 0 when clean, 3 when stat fails or prints an unread form, 2 when a name it uses is readonly.
- verify-demonstration (REASONED; le): Verify block 1 was not demonstrated: it needs a public host name with a publicly issued certificate; a Let's Encrypt staging certificate, whose roots are not in browser or client trust stores, gives a reader the exposed state.

````json
{
  "schema": 1,
  "checked": "2026-11-25",
  "documentation_checked": "2026-09",
  "body_sha256": "e4646e9c948f374956a7fcd640b232926c7e670c5cc087b3b18b2ae9266bc92b",
  "components": {
    "le": {
      "name": "Let's Encrypt documentation",
      "basis": "unknown",
      "sources": {
        "s9ff2d787c618": "https://letsencrypt.org/docs/",
        "s01388c85c5d6": "https://letsencrypt.org/docs/cert-lifetimes/",
        "s4406ef210fff": "https://letsencrypt.org/2025/12/02/from-90-to-45",
        "s21efa5995c48": "https://letsencrypt.org/2025/08/06/ocsp-service-has-reached-end-of-life",
        "saf908bcd2143": "https://letsencrypt.org/docs/caa/",
        "s82d02dd253fe": "https://letsencrypt.org/docs/staging-environment/"
      }
    },
    "zerossl": {
      "name": "ZeroSSL",
      "basis": "unknown",
      "sources": {
        "s0504194a1b2c": "https://zerossl.com/documentation/acme/",
        "s7a78f859618d": "https://zerossl.com/documentation/acme/generate-eab-credentials/"
      }
    },
    "certbot": {
      "name": "Certbot documentation",
      "basis": "unknown",
      "sources": {
        "s44faaf4eb7d7": "https://certbot.eff.org/",
        "s7b60a00cadf3": "https://eff-certbot.readthedocs.io/en/stable/using.html#manual",
        "s875be163b4c1": "https://eff-certbot.readthedocs.io/en/stable/using.html#dns-plugins"
      }
    },
    "reconfigure": {
      "name": "Certbot reconfigure minimum",
      "basis": "2.3.0",
      "sources": {
        "s0dee7d6d65ba": "https://raw.githubusercontent.com/certbot/certbot/v2.3.0/certbot/docs/using.rst"
      }
    },
    "acme": {
      "name": "acme.sh",
      "basis": "3.1.7",
      "sources": {
        "s30c55ec3e30b": "https://github.com/acmesh-official/acme.sh/blob/3.1.7/README.md#L149-L153",
        "s1a766f6ce9c9": "https://github.com/acmesh-official/acme.sh/blob/3.1.7/README.md#L405-L411",
        "sef7cd897299d": "https://github.com/acmesh-official/acme.sh/blob/3.1.7/acme.sh#L4542-L4612",
        "s9e548be3349d": "https://github.com/acmesh-official/acme.sh/blob/3.1.7/acme.sh#L3139-L3141",
        "s792201671284": "https://github.com/acmesh-official/acme.sh/blob/3.1.7/acme.sh#L2963-L2985",
        "s40949c7c89ce": "https://github.com/acmesh-official/acme.sh/blob/3.1.7/acme.sh#L2900-L2914"
      }
    },
    "certbot-v230": {
      "name": "Certbot user guide and source",
      "basis": "v2.3.0",
      "sources": {
        "s725109195132": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L808-L825",
        "s2f25bc233392": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L632-L640",
        "s11c7994242fc": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L704-L710",
        "sbb0c60d635ee": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L659-L684",
        "s55ec19f37395": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L194-L220",
        "s5bf4ff9fbe76": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L222-L265",
        "s7a053488f705": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/cli/cli_utils.py#L227-L231",
        "sa18c858c4e49": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/renewal.py#L40-L53",
        "s2e4bd79a7795": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/renewal.py#L509-L534",
        "s1910987bfd8c": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L295-L312",
        "s9c6118b72e0a": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L1120-L1128",
        "s3e22e32a2862": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L1243-L1249",
        "se50e0211aba4": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L48-L48",
        "s95e395883c80": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L1064-L1105",
        "sf782a33eadba": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/_internal/storage.py#L1222-L1230",
        "sad2cb7416c28": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L891-L914",
        "s2429d556b9d4": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/docs/using.rst#L356-L361",
        "s9ea105d375d0": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/plugins/dns_common.py#L342-L348",
        "s173b515dae09": "https://github.com/certbot/certbot/blob/v2.3.0/certbot/certbot/compat/filesystem.py#L444-L453"
      }
    },
    "certbot-dns-cloudflare-v230": {
      "name": "Certbot Cloudflare DNS plugin",
      "basis": "v2.3.0",
      "sources": {
        "s3f07ef3d544d": "https://github.com/certbot/certbot/blob/v2.3.0/certbot-dns-cloudflare/certbot_dns_cloudflare/__init__.py#L24-L39",
        "sc3b33fa2c90f": "https://github.com/certbot/certbot/blob/v2.3.0/certbot-dns-cloudflare/certbot_dns_cloudflare/__init__.py#L61-L78"
      }
    },
    "caddy": {
      "name": "Caddy automatic HTTPS",
      "basis": "v2.11.4",
      "sources": {
        "s9683cb8d689f": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddyhttp/autohttps.go#L62-L63",
        "s409f9221aec2": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddytls/acmeissuer.go#L280-L296",
        "s80dbf0751153": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddytls/acmeissuer.go#L245-L249",
        "s5216789c9341": "https://github.com/caddyserver/caddy/blob/v2.11.4/modules/caddytls/acmeissuer.go#L321-L328"
      }
    },
    "certmagic": {
      "name": "certmagic ACME implementation",
      "basis": "v0.25.3",
      "sources": {
        "s61e3cba719df": "https://github.com/caddyserver/caddy/blob/v2.11.4/go.mod#L12-L12",
        "s8782e006523b": "https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeclient.go#L188-L226",
        "s465c4ddcc92f": "https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeclient.go#L304-L313",
        "sc1e2ddefe5ed": "https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeissuer.go#L116-L120",
        "sd423f53faa1a": "https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeissuer.go#L222-L236",
        "sf2fbc79f6542": "https://github.com/caddyserver/certmagic/blob/v0.25.3/certmagic.go#L473-L475",
        "s1c3236df58b9": "https://github.com/caddyserver/certmagic/blob/v0.25.3/acmeissuer.go#L647-L654"
      }
    },
    "traefik": {
      "name": "Traefik ACME documentation",
      "basis": "v3.5",
      "sources": {
        "s418a6b1ad09b": "https://doc.traefik.io/traefik/v3.5/reference/install-configuration/tls/certificate-resolvers/acme/"
      }
    },
    "cloudflare-origin-ca": {
      "name": "Cloudflare Origin CA documentation",
      "basis": "checked October 2026",
      "sources": {
        "s1e15de5c9f36": "https://developers.cloudflare.com/ssl/origin-configuration/origin-ca/"
      }
    },
    "openssl-cli": {
      "name": "OpenSSL certificate commands",
      "basis": "3.0",
      "sources": {
        "s00aaf106164f": "https://docs.openssl.org/3.0/man1/openssl-s_client/",
        "s0856f4a58574": "https://docs.openssl.org/3.0/man1/openssl-x509/",
        "s0eaac3f2fb2c": "https://docs.openssl.org/3.0/man3/X509_STORE_CTX_get_error/"
      }
    },
    "curl-source": {
      "name": "curl command documentation",
      "basis": "curl-8_12_1",
      "sources": {
        "s76f69702c9d5": "https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/head.md#L21-L22",
        "s60820cd231e1": "https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/insecure.md#L21-L28",
        "sa86ef00fb94b": "https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/_EXITCODES.md#L125-L126",
        "s0ff92938550d": "https://github.com/curl/curl/blob/curl-8_12_1/docs/libcurl/libcurl-errors.md#L319-L323",
        "s4f54448c0d68": "https://github.com/curl/curl/blob/curl-8_12_1/lib/vtls/openssl.c#L4384-L4387",
        "sadc6ed03a840": "https://github.com/curl/curl/blob/curl-8_12_1/lib/vtls/openssl.c#L2396-L2398",
        "sccba490151c8": "https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/show-error.md#L19-L19",
        "s086004acd4e1": "https://github.com/curl/curl/blob/curl-8_12_1/docs/libcurl/libcurl-errors.md#L282-L284",
        "s76ab8431b16a": "https://github.com/curl/curl/blob/curl-8_12_1/docs/cmdline-opts/fail.md#L21-L29"
      }
    },
    "openssl-source": {
      "name": "OpenSSL source",
      "basis": "openssl-3.0.22",
      "sources": {
        "s437e0115caf7": "https://github.com/openssl/openssl/blob/openssl-3.0.22/apps/s_client.c#L903-L903",
        "sda1595fead89": "https://github.com/openssl/openssl/blob/openssl-3.0.22/apps/lib/s_cb.c#L65-L67",
        "s4518b246013f": "https://github.com/openssl/openssl/blob/openssl-3.0.22/include/openssl/x509_vfy.h.in#L222-L281"
      }
    },
    "coreutils-stat": {
      "name": "GNU coreutils stat manual",
      "basis": "checked November 2026",
      "sources": {
        "s49db2bb3c454": "https://www.gnu.org/software/coreutils/manual/html_node/stat-invocation.html"
      }
    },
    "bind-dig": {
      "name": "BIND dig manual and source",
      "basis": "v9.20.24",
      "sources": {
        "s4a49b2a8a61e": "https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/bin/dig/dig.rst#L788-L806",
        "s2d161ece08ff": "https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/bin/dig/dig.rst#L255-L262",
        "sda67db889c0e": "https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/bin/dig/dig.rst#L308-L312",
        "s9cd3fcf628fb": "https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/bin/dig/dig.rst#L598-L606",
        "s5d98e69756c9": "https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/bin/dig/dig.rst#L160-L163",
        "sac989d3132f5": "https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/bin/dig/dig.c#L864-L884",
        "sf70f634493d1": "https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/bin/dig/dig.c#L885-L924",
        "sfc53128fa456": "https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/bin/dig/dig.c#L586-L630",
        "s57229d0dad3c": "https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/lib/dns/rdata/generic/caa_257.c#L331-L362",
        "s05438cee29a6": "https://gitlab.isc.org/isc-projects/bind9/-/blob/v9.20.24/lib/dns/rdata.c#L1886-L1944"
      }
    },
    "rfc8659": {
      "name": "CAA specification",
      "basis": "RFC 8659",
      "sources": {
        "s8aedfb08aff2": "https://www.rfc-editor.org/rfc/rfc8659#section-3",
        "s25ad17065812": "https://www.rfc-editor.org/rfc/rfc8659#section-4.1",
        "se86efc2c3dd3": "https://www.rfc-editor.org/rfc/rfc8659#section-4.1.1",
        "s547d1c56334d": "https://www.rfc-editor.org/rfc/rfc8659#section-4.2",
        "s27775a13cb28": "https://www.rfc-editor.org/rfc/rfc8659#section-4.3"
      }
    }
  },
  "claims": {
    "public-trust": {"text": "ACME CAs such as Let's Encrypt and ZeroSSL issue free publicly trusted certificates; this guide advises preferring them for public DNS names, including private hosts using DNS-01.", "components": ["le", "zerossl"], "sources": ["le:s9ff2d787c618", "zerossl:s0504194a1b2c"], "status": "REASONED"},
    "http-challenge": {"text": "HTTP-01 needs a public A/AAAA or CNAME pointing to the server and inbound internet access to port 80.", "components": ["le"], "sources": ["le:s9ff2d787c618"], "status": "REASONED"},
    "alpn-challenge": {"text": "TLS-ALPN-01 needs a public DNS record and inbound port 443; Caddy's ACME issuer enables the TLS-ALPN-01 solver when DNS-01 is not configured and TLS-ALPN-01 is not disabled, and can use an alternate local port if port 443 forwards to it; Traefik also uses TLS-ALPN-01.", "components": ["le", "caddy", "certmagic", "traefik"], "sources": ["le:s9ff2d787c618", "caddy:s409f9221aec2", "caddy:s80dbf0751153", "caddy:s5216789c9341", "certmagic:s61e3cba719df", "certmagic:s8782e006523b", "certmagic:s465c4ddcc92f", "certmagic:sc1e2ddefe5ed", "certmagic:sd423f53faa1a", "certmagic:sf2fbc79f6542", "certmagic:s1c3236df58b9", "traefik:s418a6b1ad09b"], "status": "REASONED"},
    "dns-challenge": {"text": "DNS-01 needs control of the challenge TXT record, no public address record or inbound port, and supports wildcards. Automated issuance and renewal need an automated way to update TXT records, and this guide advises a provider DNS plugin and scoped API credentials, while Certbot also supports manual DNS-01 and an authentication hook for automatic renewal.", "components": ["le", "certbot", "certbot-v230"], "sources": ["le:s9ff2d787c618", "certbot:s7b60a00cadf3", "certbot:s875be163b4c1", "certbot-v230:s55ec19f37395", "certbot-v230:s5bf4ff9fbe76"], "status": "REASONED"},
    "certbot-install": {"text": "Install Certbot and nginx/Apache plugins from the distribution, or the classic snap with /usr/bin/certbot pointing to /snap/bin/certbot.", "components": ["certbot"], "sources": ["certbot:s44faaf4eb7d7"], "status": "REASONED"},
    "server-plugins": {"text": "certbot --nginx or --apache issues and installs certificates for the supplied domain names when the server is supported.", "components": ["certbot"], "sources": ["certbot:s44faaf4eb7d7"], "status": "REASONED"},
    "standalone": {"text": "certonly --standalone binds port 80; stop its current owner and arrange webroot, a server plugin or port-freeing hooks for unattended renewal.", "components": ["certbot"], "sources": ["certbot:s44faaf4eb7d7"], "status": "REASONED"},
    "webroot": {"text": "certonly --webroot uses /var/www/html to serve challenge files while the existing web server keeps running.", "components": ["certbot"], "sources": ["certbot:s44faaf4eb7d7"], "status": "REASONED"},
    "dns-credentials": {"text": "The Cloudflare DNS plugin uses a credentials file and a Zone:DNS:Edit token limited to required zones; this guide requires never using the Global API Key and protecting the file with mode 600 in a 700 directory.", "components": ["certbot", "certbot-dns-cloudflare-v230"], "sources": ["certbot:s44faaf4eb7d7", "certbot-dns-cloudflare-v230:s3f07ef3d544d", "certbot-dns-cloudflare-v230:sc3b33fa2c90f"], "status": "REASONED"},
    "certificate-paths": {"text": "Configure servers against stable /etc/letsencrypt/live/example.com/fullchain.pem and privkey.pem paths for the chain and private key.", "components": ["certbot"], "sources": ["certbot:s44faaf4eb7d7"], "status": "REASONED"},
    "renewal-schedule": {"text": "The Certbot v2.3.0 user guide says most installations have a scheduled task running certbot renew and says that, on Linux and BSD, you can check cron or systemd timers if unsure; this guide requires confirming the task and testing renewal plus reload with --dry-run --run-deploy-hooks, including package and snap installations.", "components": ["certbot", "certbot-v230"], "sources": ["certbot:s44faaf4eb7d7", "certbot-v230:s725109195132"], "status": "REASONED"},
    "deploy-hook": {"text": "This guide requires persisting a reload hook during successful initial issuance or successful renewal, or installing an executable in renewal-hooks/deploy; Certbot v2.3.0 saves the renewal-relevant options set on the command line to a lineage after successful renewal, and a renew --deploy-hook invocation with no renewal due does not save that hook.", "components": ["certbot", "certbot-v230"], "sources": ["certbot:s44faaf4eb7d7", "certbot-v230:s2f25bc233392", "certbot-v230:s11c7994242fc", "certbot-v230:sbb0c60d635ee", "certbot-v230:s7a053488f705", "certbot-v230:sa18c858c4e49", "certbot-v230:s2e4bd79a7795", "certbot-v230:s1910987bfd8c", "certbot-v230:s9c6118b72e0a", "certbot-v230:s3e22e32a2862"], "status": "REASONED"},
    "reconfigure": {"text": "certbot reconfigure can add the reload hook later on Certbot 2.3.0 and later.", "components": ["reconfigure"], "sources": ["reconfigure:s0dee7d6d65ba"], "status": "REASONED"},
    "expiry-monitoring": {"text": "Monitor the served certificate's expiry and renewal failures instead of relying on CA reminder emails; include a dry run in the deployment checklist. This guide assesses that any renewal step involving a person will fail at those scheduled shorter certificate lifetimes and that unattended automation is the only viable path.", "components": ["le", "certbot"], "sources": ["le:s4406ef210fff", "certbot:s44faaf4eb7d7"], "status": "REASONED"},
    "default-lifetime": {"text": "At the guide's September 2026 documentation check, Let's Encrypt's default certificate lifetime is 90 days.", "components": ["le"], "sources": ["le:s01388c85c5d6"], "status": "REASONED"},
    "short-lifetime": {"text": "Optional 6-day short-lived certificates are available to every subscriber as of the guide's September 2026 check.", "components": ["le"], "sources": ["le:s01388c85c5d6"], "status": "REASONED"},
    "lifetime-schedule": {"text": "The classic profile moves to 64 days on 2027-02-10 and 45 days on 2028-02-16; industry rules cap publicly trusted certificates at 47 days from 2029-03-15.", "components": ["le"], "sources": ["le:s01388c85c5d6", "le:s4406ef210fff"], "status": "REASONED"},
    "revocation": {"text": "Let's Encrypt ended OCSP on 2025-08-06 and publishes revocation through CRLs only; do not add OCSP stapling directives for its certificates.", "components": ["le"], "sources": ["le:s21efa5995c48"], "status": "REASONED"},
    "staging": {"text": "Let's Encrypt limits per-domain issuance; test with certbot --staging or --test-cert before real issuance.", "components": ["le", "certbot"], "sources": ["le:s9ff2d787c618", "certbot:s44faaf4eb7d7"], "status": "REASONED"},
    "caa": {"text": "CAA restricts issuing CAs, using issue letsencrypt.org for Let's Encrypt; certificate-transparency monitoring detects mis-issuance afterwards and complements CAA. A CA uses the closest CAA set, following aliases and climbing from the requested name toward the root, so a registered-domain set covers subdomains without their own; issuewild, when present, controls wildcard issuance.", "components": ["le", "rfc8659"], "sources": ["le:saf908bcd2143", "le:s9ff2d787c618", "rfc8659:s8aedfb08aff2"], "status": "REASONED"},
    "zerossl-eab": {"text": "ZeroSSL offers free ACME certificates; its ACME service needs EAB credentials, eab_kid and eab_hmac_key, from the dashboard or its API, which ZeroSSL says are not stored in the account, are reusable and all stay functional; this guide treats them as secrets kept out of shell history and repositories.", "components": ["zerossl"], "sources": ["zerossl:s0504194a1b2c", "zerossl:s7a78f859618d"], "status": "REASONED"},
    "acme-default": {"text": "acme.sh 3.1.7 lists ZeroSSL as its default CA.", "components": ["acme"], "sources": ["acme:s30c55ec3e30b"], "status": "REASONED"},
    "acme-install": {"text": "acme.sh is a shell ACME client supporting many DNS providers; the guide recommends installation from a repository release instead of piping a download into a shell, and gives no acme.sh walk-through because it has no verified acme.sh command.", "components": ["acme"], "sources": ["acme:s1a766f6ce9c9"], "status": "REASONED"},
    "acme-eab-storage": {"text": "acme.sh 3.1.7 saves EAB credentials given at registration as CA_EAB_KEY_ID and CA_EAB_HMAC_KEY in its CA configuration file, which it creates with mode 600 when the file does not exist.", "components": ["acme"], "sources": ["acme:sef7cd897299d", "acme:s9e548be3349d", "acme:s792201671284", "acme:s40949c7c89ce"], "status": "REASONED"},
    "server-automation": {"text": "This guide advises Caddy or Traefik for built-in issuance and renewal without an external client; it assesses them as the lowest-effort correct option for new deployments.", "components": ["le", "caddy", "traefik"], "sources": ["le:s9ff2d787c618", "caddy:s9683cb8d689f", "traefik:s418a6b1ad09b"], "status": "REASONED"},
    "origin-certificates": {"text": "At the guide's October 2026 check, Cloudflare listed Origin CA certificates on its Free plan, which can change; it says they only encrypt traffic between Cloudflare and the origin, and that visitors may see untrusted certificate errors when Cloudflare is paused or proxying is disabled. This guide restricts their use to origins that receive traffic only through Cloudflare-proxied records.", "components": ["le", "cloudflare-origin-ca"], "sources": ["le:s9ff2d787c618", "cloudflare-origin-ca:s1e15de5c9f36"], "status": "REASONED"},
    "verify-inventory": {"text": "certbot certificates lists issued certificates and their expiry dates.", "components": ["certbot"], "sources": ["certbot:s44faaf4eb7d7"], "status": "REASONED", "verify": [1]},
    "verify-https": {"text": "Use the deployment's public hostname rather than example.com; curl HTTPS should succeed without -k.", "components": ["le", "curl-source"], "sources": ["le:s9ff2d787c618", "curl-source:s76f69702c9d5", "curl-source:s60820cd231e1"], "status": "REASONED", "verify": [1]},
    "verify-certificate": {"text": "The OpenSSL probe targets the hostname on port 443 with SNI, hostname verification and verification errors enabled, then displays issuer and dates.", "components": ["le", "openssl-cli"], "sources": ["le:s9ff2d787c618", "openssl-cli:s00aaf106164f", "openssl-cli:s0856f4a58574"], "status": "REASONED", "verify": [1]},
    "verify-caa": {"text": "dig -r +noall +comments +answer CAA for the host, then each parent to the TLD, until a reply has CAA lines. Exit 1 (exposed): no set, or only iodef or issuewild. Exit 0: a well-formed letsencrypt.org issue (fixed), or other issues only (not classified). Exit 3: dig exit not 0, no single NOERROR header, no ra flag, an unread form, a critical unknown tag, or an unknown tag and no issue or issuewild.", "components": ["le", "bind-dig", "rfc8659"], "sources": ["le:saf908bcd2143", "bind-dig:s4a49b2a8a61e", "bind-dig:s2d161ece08ff", "bind-dig:sda67db889c0e", "bind-dig:s9cd3fcf628fb", "bind-dig:s5d98e69756c9", "bind-dig:sac989d3132f5", "bind-dig:sf70f634493d1", "bind-dig:sfc53128fa456", "bind-dig:s57229d0dad3c", "bind-dig:s05438cee29a6", "rfc8659:s8aedfb08aff2", "rfc8659:s25ad17065812", "rfc8659:se86efc2c3dd3", "rfc8659:s547d1c56334d", "rfc8659:s27775a13cb28"], "status": "REASONED", "verify": [2]},
    "authentication": {"text": "A certificate alone is insufficient protection; continue with server controls and authentication.", "components": ["le"], "sources": ["le:s9ff2d787c618"], "status": "REASONED"},
    "dns-automation": {"text": "For automated DNS-01 issuance and renewal, this guide advises using a provider DNS plugin and least-privilege API credentials; Certbot also documents manual TXT entry and authentication hooks that automate the challenge.", "components": ["certbot", "certbot-v230"], "sources": ["certbot:s875be163b4c1", "certbot:s7b60a00cadf3", "certbot-v230:s55ec19f37395", "certbot-v230:s5bf4ff9fbe76"], "status": "REASONED"},
    "dns-manual": {"text": "certbot certonly --manual --preferred-challenges dns permits hand-created TXT records; the Certbot v2.3.0 guide says certificates created with --manual do not support automatic renewal without a --manual-auth-hook that automates the challenge.", "components": ["certbot", "certbot-v230"], "sources": ["certbot:s7b60a00cadf3", "certbot-v230:s5bf4ff9fbe76"], "status": "REASONED"},
    "private-key-at-rest": {"text": "This guide advises keeping the private key on the server, readable only by the account that runs the server or deploy hook; Certbot v2.3.0 creates the live, archive and renewal directories with mode 0700, writes each new private key with mode 0600, and keeps a changed key group mode or group owner on renewal.", "components": ["certbot-v230"], "sources": ["certbot-v230:se50e0211aba4", "certbot-v230:s95e395883c80", "certbot-v230:sf782a33eadba", "certbot-v230:sad2cb7416c28"], "status": "REASONED"},
    "verify-outcomes": {"text": "Run Verify block 1 on the Certbot host. Fixed: the certificate is listed, curl and s_client exit 0, and the issuer is a public CA with notAfter in the future. Exposed: curl exit 60 (CURLE_PEER_FAILED_VERIFICATION) or s_client verify error 9, 10, 18-21 or 62, such as X509_V_ERR_CERT_HAS_EXPIRED; it exits 1 for these, 3 for curl 51 or any other failure, 2 for a refused guard.", "components": ["certbot-v230", "curl-source", "openssl-cli", "openssl-source"], "sources": ["certbot-v230:s2429d556b9d4", "curl-source:sa86ef00fb94b", "curl-source:s0ff92938550d", "openssl-cli:s0eaac3f2fb2c", "openssl-cli:s00aaf106164f", "openssl-cli:s0856f4a58574", "openssl-source:s4518b246013f"], "status": "REASONED", "verify": [1]},
    "verify-classification": {"text": "Verify block 1 exits 1 when curl exits 60, which the OpenSSL backend returns for an untrusted chain, expiry or name mismatch, or when s_client fails with verify error 9, 10, 18, 19, 20, 21 or 62; 2 for a refused guard; 3 for any other failure, curl 51 included; 0 only when certbot, curl, s_client and x509 all exit 0, judged against the host trust store, which does not prove a public CA.", "components": ["curl-source", "openssl-source"], "sources": ["curl-source:sa86ef00fb94b", "curl-source:s4f54448c0d68", "curl-source:sadc6ed03a840", "curl-source:sccba490151c8", "curl-source:s086004acd4e1", "curl-source:s76ab8431b16a", "openssl-source:s437e0115caf7", "openssl-source:sda1595fead89", "openssl-source:s4518b246013f"], "status": "REASONED", "verify": [1]},
    "verify-credential-mode": {"text": "Verify block 3 runs sudo stat -L -c %a %U %n on /root/.secrets and cloudflare.ini on the Certbot host: exit 1 for a group or other bit or a non-root owner (the group and directory rules are this guide's, stricter than Certbot's other-users warning), 0 when clean, 3 when stat fails or prints an unread form, 2 when a name it uses is readonly.", "components": ["certbot-dns-cloudflare-v230", "certbot-v230", "coreutils-stat"], "sources": ["certbot-dns-cloudflare-v230:sc3b33fa2c90f", "certbot-v230:s9ea105d375d0", "certbot-v230:s173b515dae09", "certbot-v230:sad2cb7416c28", "coreutils-stat:s49db2bb3c454"], "status": "REASONED", "verify": [3]},
    "verify-demonstration": {"text": "Verify block 1 was not demonstrated: it needs a public host name with a publicly issued certificate; a Let's Encrypt staging certificate, whose roots are not in browser or client trust stores, gives a reader the exposed state.", "components": ["le"], "sources": ["le:s82d02dd253fe"], "status": "REASONED", "verify": [1]}
  }
}
````
<!-- version-basis:end -->
