# CORS: allow your origins, not everyone's

CORS is how your API tells browsers which other websites' pages may read its responses. This guide helps your AI assistant configure it securely, including exact allowed origins for authenticated APIs, a wildcard only for public, unauthenticated, read-only resources and never with credentials, and endpoint authentication still required.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/cors.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against MDN CORS documentation (no recorded version); 3 further sources carry no recorded version. Metadata reviewed 2026-09-27; documentation checked September 2026. The guide records 13 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

CORS misconfiguration does not expose a port; it lets hostile websites use your users' browsers, cookies included, against your API. AI assistants reach for `Access-Control-Allow-Origin: *` the moment a browser console shows a CORS error; that is the wrong fix for any API that authenticates.

## Rules

1. **List exact origins.** `Access-Control-Allow-Origin` names the site(s) allowed to call the API from a browser:
   ```
   Access-Control-Allow-Origin: https://app.example.com
   ```
2. **Never combine `*` with credentials.** Browsers refuse `Access-Control-Allow-Origin: *` together with `Access-Control-Allow-Credentials: true`; configurations that "fix" this by reflecting whatever `Origin` header arrives recreate `*` for credentialed requests, which is worse. Reflect only origins checked against an explicit allow list.
3. **`*` is acceptable** only for genuinely public, unauthenticated, read-only resources.
4. **CORS is not authentication.** It controls browsers, not attackers with curl; every endpoint still authenticates per [authentication.md](authentication.md).

## Framework examples

Express (`cors` package):

```js
const cors = require('cors');
app.use(cors({ origin: ['https://app.example.com'], credentials: true }));
```

FastAPI:

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
```

Keep the origin list in configuration per environment rather than hardcoding localhost origins into production.

## Verify

**REASONED:** not demonstrated against a deployed API: no Express or FastAPI deployment or browser session is available here, so which origins real CORS middleware echoes rests on the Fetch Standard and MDN's CORS guide (Sources). An exposed API echoes `https://evil.example` in `Access-Control-Allow-Origin`; the fixed API omits it for that origin and returns only your listed origin, with `Access-Control-Allow-Credentials: true` only where the browser must send credentials. For an earlier change both pipelines ran with curl 8.18.0: against a loopback listener answering 200 with the listed origin's headers, each printed the status line with both Access-Control headers and exited 0. Both pipelines also ran for an earlier change with curl 8.18.0 against a closed loopback port, where each printed `curl: (7) Failed to connect ...` on stderr and its inconclusive line (the same pipelines without the pipefail subshell exited 1 with empty output, and silently under the old `-s`). Both pipelines also ran for an earlier change with curl 8.18.0 against a stub curl that printed `HTTP/1.1 200 OK`, wrote a transfer error to stderr and returned 18: the pipeline without pipefail exited 0 as if it had passed, while the `set -o pipefail` subshell (the convention litellm.md and search-engines.md use) exited 18, so its `|| echo` printed the inconclusive line. The runs against the loopback listener, the closed loopback port and the stub curl record the pipelines' behaviour, not any deployed middleware's CORS decisions. Those curl 8.18.0 runs covered the earlier form of both pipelines, which named api.example.com and an app.example.com origin directly; the pipelines now take the API host and your app's origin host on a guarded `set --` line that refuses example.com, example.net, example.org and their subdomains, and those curl 8.18.0 runs did not cover the guarded form. Those runs also used a form without the block's classified status: the block now exits with status 1 when `Access-Control-Allow-Origin` echoes the hostile origin, otherwise with status 3 when either probe is inconclusive or your own origin is not returned, and otherwise with status 0, leaving `Access-Control-Allow-Credentials` and any other origin value for you to judge. Stub runs on 2026-11-01 covered the current form under Bash 5.3.9, with curl replaced by a local stub that prints one line and exits 0, and no network, but reached only the block's status 2 and status 3 exits: no run reached its status 1 or status 0 arm. In those runs the block refused an unsubstituted placeholder, a scheme in either host value, a third value on the `set --` line and a paste without the `set --` line, with or without caller arguments, each with status 2, its own message and no curl call. It refused example.com, EXAMPLE.COM, Example.Org, example.NET, app.example.net, APP.EXAMPLE.NET, Api.Example.Com and deep.sub.EXAMPLE.org as the API host and, in separate runs, as the origin host, each with status 2, the reserved-name message and no curl call. EXAMPLE.COM and App.Example.ORG in either position were refused the same way with `tr` absent from PATH and under an inherited `nocasematch`, readonly and `declare -i` variables, or `set -e`, and an inherited `nocasematch` was still set after the block. The host names status.acme-widgets.io and app.acme-widgets.io, also with `tr` absent and under each of those preludes, and Status.Acme-Widgets.IO as the API host, were not refused: the block made its two curl calls, printed its inconclusive line for each probe against the stub's output and exited 3. Under dash 0.5.12 and BusyBox 1.37.0 sh, the block refused the eight reserved names in either position and a real-looking pair of host names with status 2 and its message that the block needs bash, with no curl call; the placeholder and the partial paste got their own messages instead. No other shell, including Bash 3.2, zsh or ksh, was run, and these stub runs record the block's refusals and its exit statuses 2 and 3, not any deployed middleware's CORS decisions.

```bash
(                                       # a subshell, so your own script arguments are untouched
  set +e                                # errexit off here, so a command that ends nonzero is recorded below instead of ending the block
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_API_HOST' 'REPLACE_WITH_YOUR_APP_HOST'   # the API's public host name, then the host name of the https:// origin your app is served from, each with no scheme, user name, port, path, query, fragment, percent sign or trailing dot: replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit 2; }
  case "$1" in
    ""|*REPLACE_WITH_*|*/*|*:*|*.|*[@?%]*|*'#'*|*[[:space:][:cntrl:]]*) echo "substitute your API's public host name (no scheme, user name, port, path, query, fragment, percent sign or trailing dot) inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  shopt -s nocasematch || { echo "this block needs bash; run it in bash; not probing"; exit 2; }   # host names ignore letter case, so this case matches them in any case through a bash option, not an outside command that could fail
  case "$1" in
    example.com|example.net|example.org|*.example.com|*.example.net|*.example.org) echo "example.com, example.net, example.org and their subdomains are not your deployment: substitute your own host name on the set -- line above; not probing"; exit 2 ;;
  esac
  shopt -u nocasematch   # every match below compares letter case exactly again
  case "$2" in
    ""|*REPLACE_WITH_*|*/*|*:*|*.|*[@?%]*|*'#'*|*[[:space:][:cntrl:]]*) echo "substitute your app's origin host name (no scheme, user name, port, path, query, fragment, percent sign or trailing dot) inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  shopt -s nocasematch || { echo "this block needs bash; run it in bash; not probing"; exit 2; }   # host names ignore letter case, so this case matches them in any case through a bash option, not an outside command that could fail
  case "$2" in
    example.com|example.net|example.org|*.example.com|*.example.net|*.example.org) echo "example.com, example.net, example.org and their subdomains are not your deployment: substitute your own origin host name on the set -- line above; not probing"; exit 2 ;;
  esac
  shopt -u nocasematch   # every match below compares letter case exactly again
  # Both probes request /data: change that path to a route your app's browser code calls.
  # The hostile origin https://evil.example is deliberately foreign; keep it as written.
  set -- "$1" "$2" 0                    # the 3rd value is the block's status so far: 1 (a finding) outranks 3 (inconclusive), which outranks 0
  set -- "$1" "$2" "$3" "$(if curl -q -g -sS -o /dev/null -D - "https://$1/data" -H "Origin: https://evil.example"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "$3" "${4##*$'\n'}" "$(if printf '%s\n' "${4%$'\n'*}" | awk '{ sub(/\r$/, "") } tolower($0) ~ /http\/|access-control/ { print } /^HTTP\// { c = $2; v = "" } tolower(substr($0, 1, 28)) == "access-control-allow-origin:" { v = substr($0, 29); gsub(/^( |\t)+|( |\t)+$/, "", v) } END { printf "\n%s %s", c, v }'; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "$3" "$4" "${5##*$'\n'}" "${5%$'\n'*}"   # curl's exit status, awk's exit status, then awk's output
  printf '%s' "${6%$'\n'*}"             # the status and access-control header lines
  set -- "$1" "$2" "$3" "$4" "$5" "${6##*$'\n'}"
  set -- "$1" "$2" "$3" "$4" "$5" "${6%% *}" "${6#* }"     # curl's exit status, awk's exit status, the final HTTP status code, then the last Access-Control-Allow-Origin value
  if [ "$5" != 0 ]; then
    echo "awk could not read the response headers; inconclusive"; set -- "$1" "$2" 3 "$6"
  elif [ "$7" = https://evil.example ]; then
    echo "FINDING: Access-Control-Allow-Origin echoes the hostile origin https://evil.example"; set -- "$1" "$2" 1 "$6"
  elif [ "$4" != 0 ] || [ -z "$6" ]; then
    echo "inconclusive: the transfer failed or printed no status line; not a pass"; set -- "$1" "$2" 3 "$6"
  else
    set -- "$1" "$2" "$3" "$6"          # the 4th value is now this probe's HTTP status code
    case "$4" in 2??) ;; *) echo "HTTP $4 for the hostile origin is not a 2xx status; inconclusive"; set -- "$1" "$2" 3 "$4" ;; esac
  fi
  # expect: a 2xx status line matching the own-origin probe below, and no Access-Control-Allow-Origin echoing the hostile origin; any other status, a proxy's lone "HTTP/1.1 200 Connection established" line, the inconclusive line, or empty output is inconclusive, not a pass
  set -- "$1" "$2" "$3" "$4" "$(if curl -q -g -sS -o /dev/null -D - "https://$1/data" -H "Origin: https://$2"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "$3" "$4" "${5##*$'\n'}" "$(if printf '%s\n' "${5%$'\n'*}" | awk '{ sub(/\r$/, "") } tolower($0) ~ /http\/|access-control/ { print } /^HTTP\// { c = $2; v = "" } tolower(substr($0, 1, 28)) == "access-control-allow-origin:" { v = substr($0, 29); gsub(/^( |\t)+|( |\t)+$/, "", v) } END { printf "\n%s %s", c, v }'; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "$3" "$4" "$5" "${6##*$'\n'}" "${6%$'\n'*}"   # the hostile probe's HTTP status code, curl's exit status, awk's exit status, then awk's output
  printf '%s' "${7%$'\n'*}"             # the status and access-control header lines
  set -- "$1" "$2" "$3" "$4" "$5" "$6" "${7##*$'\n'}"
  set -- "$1" "$2" "$3" "$4" "$5" "$6" "${7%% *}" "${7#* }"   # then this probe's final HTTP status code and last Access-Control-Allow-Origin value
  if [ "$6" != 0 ]; then
    echo "awk could not read the response headers; inconclusive"; [ "$3" = 1 ] || set -- "$1" "$2" 3
  elif [ "$5" != 0 ] || [ -z "$7" ]; then
    echo "inconclusive: the transfer failed or printed no status line; not a pass"; [ "$3" = 1 ] || set -- "$1" "$2" 3
  elif [ "$8" != "https://$2" ]; then
    echo "Access-Control-Allow-Origin does not return your origin https://$2, so this positive control failed; inconclusive"; [ "$3" = 1 ] || set -- "$1" "$2" 3
  else
    case "$4:$7" in
      2??:2??) [ "$4" = "$7" ] || { echo "the hostile-origin probe answered HTTP $4 and yours HTTP $7, so the status lines do not match; inconclusive"; [ "$3" = 1 ] || set -- "$1" "$2" 3; } ;;
      *:2??) ;;
      *) echo "HTTP $7 for your origin is not a 2xx status; inconclusive"; [ "$3" = 1 ] || set -- "$1" "$2" 3 ;;
    esac
  fi
  # expect: a 2xx status line, your origin in Access-Control-Allow-Origin, and Allow-Credentials only if the browser must send credentials: cookies, HTTP authentication, or TLS client certificates
  # The block exits with status 1 if the hostile origin is echoed, otherwise 3 if either probe printed an inconclusive line, and otherwise 0.
  echo "block exit $3; Access-Control-Allow-Credentials and any Access-Control-Allow-Origin value other than the two origins, such as *, are not classified, so judge them yourself"
  exit "$3"
)
```

## Sources (checked September 2026)

- MDN: Cross-Origin Resource Sharing, for the protocol itself: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS
- Fetch Standard, definition of credentials: https://fetch.spec.whatwg.org/#credentials
- Express `cors` middleware, for the `origin` and `credentials` options used above: https://expressjs.com/en/resources/middleware/cors/
- FastAPI CORS, for `CORSMiddleware` and its parameters: https://fastapi.tiangolo.com/tutorial/cors/


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- protocol: MDN CORS documentation (unknown)
- fetch: Fetch Standard credentials (unknown)
- express: Express cors middleware (unknown)
- fastapi: FastAPI CORSMiddleware (unknown)

Claims (full source mapping in the JSON block below):

- exact-origins (REASONED; protocol): Allow exact browser origins, illustrated by Access-Control-Allow-Origin: https://app.example.com; keep environment-specific lists in configuration instead of production localhost entries.
- wildcard-credentials (REASONED; protocol): Browsers refuse wildcard Access-Control-Allow-Origin with credentials; the guide restricts wildcard use to public, unauthenticated, read-only resources.
- origin-reflection (REASONED; protocol): Reflect only origins checked against an explicit allowlist; reflecting arbitrary Origin values permits hostile sites to read credentialed responses.
- authentication (REASONED; protocol, express): CORS controls browsers rather than curl or other attackers, does not expose a port and does not replace endpoint authentication.
- express-origins (REASONED; express): Express cors uses origin: ['https://app.example.com'] as the allowed origin list.
- express-credentials (REASONED; express): The Express example enables credentials with credentials: true.
- fastapi-origins (REASONED; fastapi): FastAPI adds CORSMiddleware with allow_origins restricted to https://app.example.com.
- fastapi-credentials (REASONED; fastapi): The FastAPI example enables allow_credentials=True.
- fastapi-methods (REASONED; fastapi): The FastAPI example allows only GET and POST through allow_methods.
- fastapi-headers (REASONED; fastapi): The FastAPI example allows Authorization and Content-Type through allow_headers.
- verify-hostile (REASONED; protocol, express, fastapi, fetch): The exposed API echoes https://evil.example in Access-Control-Allow-Origin; the fixed API omits that hostile origin. No deployed API or browser run is recorded.
- verify-allowed (REASONED; protocol, express, fastapi, fetch): The allowed-Origin probe should return the listed app origin, with Allow-Credentials only where the browser must send cookies, HTTP authentication or TLS client certificates; no actual response is recorded.
- credential-types (REASONED; fetch, protocol): Browser credentials include cookies, HTTP authentication and TLS client certificates; Access-Control-Allow-Credentials: true is needed only where the browser must send credentials.

````json
{
  "schema": 1,
  "checked": "2026-09-27",
  "documentation_checked": "2026-09",
  "body_sha256": "fbd626460a42276389a3b92e19db79c3f6b6e8e35270a5ac65dfe39d39872ee8",
  "components": {
    "protocol": {
      "name": "MDN CORS documentation",
      "basis": "unknown",
      "sources": {
        "s6265cf028385": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS"
      }
    },
    "fetch": {
      "name": "Fetch Standard credentials",
      "basis": "unknown",
      "sources": {
        "s028c38ebd452": "https://fetch.spec.whatwg.org/#credentials"
      }
    },
    "express": {
      "name": "Express cors middleware",
      "basis": "unknown",
      "sources": {
        "sb6448b9a443d": "https://expressjs.com/en/resources/middleware/cors/"
      }
    },
    "fastapi": {
      "name": "FastAPI CORSMiddleware",
      "basis": "unknown",
      "sources": {
        "s4f1cea92e7bc": "https://fastapi.tiangolo.com/tutorial/cors/"
      }
    }
  },
  "claims": {
    "exact-origins": {"text": "Allow exact browser origins, illustrated by Access-Control-Allow-Origin: https://app.example.com; keep environment-specific lists in configuration instead of production localhost entries.", "components": ["protocol"], "sources": ["protocol:s6265cf028385"], "status": "REASONED"},
    "wildcard-credentials": {"text": "Browsers refuse wildcard Access-Control-Allow-Origin with credentials; the guide restricts wildcard use to public, unauthenticated, read-only resources.", "components": ["protocol"], "sources": ["protocol:s6265cf028385"], "status": "REASONED"},
    "origin-reflection": {"text": "Reflect only origins checked against an explicit allowlist; reflecting arbitrary Origin values permits hostile sites to read credentialed responses.", "components": ["protocol"], "sources": ["protocol:s6265cf028385"], "status": "REASONED"},
    "authentication": {"text": "CORS controls browsers rather than curl or other attackers, does not expose a port and does not replace endpoint authentication.", "components": ["protocol", "express"], "sources": ["protocol:s6265cf028385", "express:sb6448b9a443d"], "status": "REASONED"},
    "express-origins": {"text": "Express cors uses origin: ['https://app.example.com'] as the allowed origin list.", "components": ["express"], "sources": ["express:sb6448b9a443d"], "status": "REASONED"},
    "express-credentials": {"text": "The Express example enables credentials with credentials: true.", "components": ["express"], "sources": ["express:sb6448b9a443d"], "status": "REASONED"},
    "fastapi-origins": {"text": "FastAPI adds CORSMiddleware with allow_origins restricted to https://app.example.com.", "components": ["fastapi"], "sources": ["fastapi:s4f1cea92e7bc"], "status": "REASONED"},
    "fastapi-credentials": {"text": "The FastAPI example enables allow_credentials=True.", "components": ["fastapi"], "sources": ["fastapi:s4f1cea92e7bc"], "status": "REASONED"},
    "fastapi-methods": {"text": "The FastAPI example allows only GET and POST through allow_methods.", "components": ["fastapi"], "sources": ["fastapi:s4f1cea92e7bc"], "status": "REASONED"},
    "fastapi-headers": {"text": "The FastAPI example allows Authorization and Content-Type through allow_headers.", "components": ["fastapi"], "sources": ["fastapi:s4f1cea92e7bc"], "status": "REASONED"},
    "verify-hostile": {"text": "The exposed API echoes https://evil.example in Access-Control-Allow-Origin; the fixed API omits that hostile origin. No deployed API or browser run is recorded.", "components": ["protocol", "express", "fastapi", "fetch"], "sources": ["protocol:s6265cf028385", "express:sb6448b9a443d", "fastapi:s4f1cea92e7bc", "fetch:s028c38ebd452"], "status": "REASONED", "verify": [1]},
    "verify-allowed": {"text": "The allowed-Origin probe should return the listed app origin, with Allow-Credentials only where the browser must send cookies, HTTP authentication or TLS client certificates; no actual response is recorded.", "components": ["protocol", "express", "fastapi", "fetch"], "sources": ["protocol:s6265cf028385", "express:sb6448b9a443d", "fastapi:s4f1cea92e7bc", "fetch:s028c38ebd452"], "status": "REASONED", "verify": [1]},
    "credential-types": {"text": "Browser credentials include cookies, HTTP authentication and TLS client certificates; Access-Control-Allow-Credentials: true is needed only where the browser must send credentials.", "components": ["fetch", "protocol"], "sources": ["fetch:s028c38ebd452", "protocol:s6265cf028385"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
