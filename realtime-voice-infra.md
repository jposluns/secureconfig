---
version_basis: {
  "schema": 1,
  "checked": "2026-10-05",
  "documentation_checked": "2026-09",
  "body_sha256": "ad4662f4006cf6b50037f7eff13c3e900a1a6bb122631372b6d7f12e14e1723e",
  "components": {
    "livekit": {
      "name": "LiveKit",
      "basis": "v1.13.7",
      "sources": {
        "s15a5a2b0b78b": "https://raw.githubusercontent.com/livekit/livekit/v1.13.7/pkg/config/config.go",
        "s75f8e517e920": "https://raw.githubusercontent.com/livekit/livekit/v1.13.7/cmd/server/main.go",
        "sc52b46730181": "https://raw.githubusercontent.com/livekit/livekit/v1.13.7/config-sample.yaml",
        "s022153e2a982": "https://github.com/livekit/livekit/blob/v1.13.7/pkg/service/server.go#L319",
        "s81618482f092": "https://github.com/livekit/livekit/blob/v1.13.7/pkg/service/server.go#L165-L170",
        "sdbaff31c14ce": "https://github.com/livekit/livekit/blob/v1.13.7/pkg/service/server.go#L181-L193",
        "s48a6c1203218": "https://github.com/livekit/livekit/blob/v1.13.7/pkg/service/server.go#L261-L266",
        "s646f86dd5bd7": "https://github.com/livekit/livekit/blob/v1.13.7/pkg/service/turn.go#L315-L325",
        "sdd5650ac94ff": "https://github.com/livekit/livekit/blob/v1.13.7/pkg/service/rtcservice.go#L147-L149"
      }
    },
    "livekit-docs": {
      "name": "LiveKit documentation",
      "basis": "unknown",
      "sources": {
        "s66f19d919eb5": "https://docs.livekit.io/transport/self-hosting/ports-firewall/",
        "sb6a31fba4f62": "https://docs.livekit.io/frontends/reference/tokens-grants/",
        "s38432c6e3577": "https://docs.livekit.io/transport/self-hosting/deployment/"
      }
    },
    "lk": {
      "name": "livekit-cli",
      "basis": "v2.18.2",
      "sources": {
        "sa42f9b5ed5d4": "https://raw.githubusercontent.com/livekit/livekit-cli/v2.18.2/cmd/lk/utils.go",
        "s6a98a324f01b": "https://raw.githubusercontent.com/livekit/livekit-cli/v2.18.2/cmd/lk/token.go",
        "sf8b161b60423": "https://raw.githubusercontent.com/livekit/livekit-cli/v2.18.2/pkg/config/config.go"
      }
    },
    "coturn": {
      "name": "coturn",
      "basis": "4.18.0",
      "sources": {
        "sc4178412962b": "https://raw.githubusercontent.com/coturn/coturn/4.18.0/examples/etc/turnserver.conf",
        "s5ec265938c96": "https://raw.githubusercontent.com/coturn/coturn/4.18.0/README.turnserver",
        "s0728ef023209": "https://github.com/coturn/coturn/releases/tag/4.18.0",
        "s7eb31b944cf1": "https://raw.githubusercontent.com/coturn/coturn/4.18.0/src/server/ns_turn_server.c",
        "se7856434c3d0": "https://raw.githubusercontent.com/coturn/coturn/4.18.0/src/apps/uclient/mainuclient.c",
        "s1942d0158590": "https://github.com/coturn/coturn/blob/4.18.0/src/apps/uclient/uclient.h#L132",
        "s0e40b57274d6": "https://github.com/coturn/coturn/blob/4.18.0/src/apps/uclient/mainuclient.c#L553-L554",
        "sdd3c00ef7290": "https://github.com/coturn/coturn/blob/4.18.0/src/apps/uclient/uclient.c#L3109",
        "s414c246eed7f": "https://github.com/coturn/coturn/blob/4.18.0/src/apps/uclient/uclient.c#L3132",
        "s6ba3cc5d04ea": "https://github.com/coturn/coturn/blob/4.18.0/src/apps/uclient/mainuclient.c#L381",
        "sed853e8fb3e3": "https://github.com/coturn/coturn/blob/4.18.0/src/apps/uclient/startuclient.c",
        "se9819d0c6412": "https://github.com/coturn/coturn/blob/4.18.0/src/apps/uclient/startuclient.h",
        "s51a288a4b86e": "https://github.com/coturn/coturn/blob/4.18.0/src/apps/uclient/session.h",
        "s790c96d8eed7": "https://github.com/coturn/coturn/blob/4.18.0/src/apps/uclient/CMakeLists.txt",
        "s0c57f0580b5c": "https://raw.githubusercontent.com/coturn/coturn/4.18.0/README.turnutils",
        "s3a76feb6f5e4": "https://github.com/coturn/coturn/blob/4.18.0/docker/coturn/turnserver.conf#L184"
      }
    },
    "dtls": {
      "name": "coturn DTLS opt-in introduction",
      "basis": "4.17.0",
      "sources": {
        "s24abe2486071": "https://github.com/coturn/coturn/releases/tag/4.17.0"
      }
    },
    "curl": {
      "name": "curl minimum write-out version",
      "basis": "7.75.0",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    },
    "openssl-cli": {
      "name": "OpenSSL CLI",
      "basis": "3.0",
      "sources": {
        "s00aaf106164f": "https://docs.openssl.org/3.0/man1/openssl-s_client/"
      }
    }
  },
  "claims": {
    "livekit-ports": {"text": "Signaling/API use 7880, RTC TCP 7881 and normal UDP media 50000-60000; development uses UDP mux 7882.", "components": ["livekit", "livekit-docs"], "sources": ["livekit:s15a5a2b0b78b", "livekit-docs:s66f19d919eb5"], "status": "REASONED"},
    "livekit-bind": {"text": "Unset signaling/RTC TCP binds are wildcard; UDP uses eligible interfaces independently of signaling restrictions.", "components": ["livekit", "livekit-docs"], "sources": ["livekit:s15a5a2b0b78b", "livekit-docs:s66f19d919eb5"], "status": "REASONED"},
    "livekit-turn": {"text": "Embedded TURN defaults off and needs explicit ports when enabled.", "components": ["livekit", "livekit-docs"], "sources": ["livekit:sc52b46730181", "livekit-docs:s66f19d919eb5"], "status": "REASONED"},
    "livekit-keys": {"text": "Normal mode refuses an empty key map; API secrets sign HS256 room and administrative JWT grants.", "components": ["livekit", "livekit-docs"], "sources": ["livekit:s15a5a2b0b78b", "livekit-docs:sb6a31fba4f62"], "status": "REASONED"},
    "livekit-dev": {"text": "Development mode supplies devkey/secret when keys are empty and defaults signaling to loopback only when no bind is supplied.", "components": ["livekit"], "sources": ["livekit:s75f8e517e920"], "status": "REASONED"},
    "livekit-samples": {"text": "Remove the sample key1/secret1 and key2/secret2 pairs from every effective key set.", "components": ["livekit"], "sources": ["livekit:sc52b46730181"], "status": "REASONED"},
    "livekit-length": {"text": "Outside development, secrets shorter than 32 characters only log an error; generate long random secrets.", "components": ["livekit"], "sources": ["livekit:s15a5a2b0b78b"], "status": "REASONED"},
    "livekit-grants": {"text": "canPublish and canSubscribe default true; signing secrets mint any grant, so deliberately scope issued tokens.", "components": ["livekit-docs"], "sources": ["livekit-docs:sb6a31fba4f62"], "status": "REASONED"},
    "livekit-keyfile": {"text": "Use key_file with service-owned mode 0600; world permissions reject startup, but group-readable 0640 passes the server check.", "components": ["livekit"], "sources": ["livekit:s15a5a2b0b78b"], "status": "REASONED"},
    "livekit-tls": {"text": "Front signaling with TLS/WSS; the guide describes no native signaling TLS and calls Serve, but the server implementation is not cited.", "components": ["livekit-docs", "livekit"], "sources": ["livekit-docs:s38432c6e3577", "livekit:s022153e2a982"], "status": "REASONED"},
    "livekit-metrics": {"text": "Enabled metrics are unauthenticated unless prometheus.username/password are set.", "components": ["livekit"], "sources": ["livekit:s15a5a2b0b78b", "livekit:sc52b46730181", "livekit:s81618482f092"], "status": "REASONED"},
    "livekit-debug": {"text": "Debug/pprof, goroutine and room routes lack grant checks and can use debug_handler.port; route implementations are not cited.", "components": ["livekit"], "sources": ["livekit:s15a5a2b0b78b", "livekit:sc52b46730181", "livekit:sdbaff31c14ce", "livekit:s48a6c1203218"], "status": "REASONED"},
    "livekit-turn-secret": {"text": "Embedded TURN derives credentials from the API secret; the derivation implementation is not cited.", "components": ["livekit"], "sources": ["livekit:sc52b46730181", "livekit:s646f86dd5bd7"], "status": "REASONED"},
    "livekit-webhook": {"text": "Webhook receivers must verify the signing token and SHA-256 body hash; the webhook verifier is not cited.", "components": ["livekit-docs"], "sources": ["livekit-docs:sb6a31fba4f62"], "status": "REASONED"},
    "coturn-listeners": {"text": "STUN/TURN use UDP/TCP 3478 and TLS 5349; enabled interfaces are enumerated, not loopback-only.", "components": ["coturn"], "sources": ["coturn:sc4178412962b", "coturn:s5ec265938c96"], "status": "REASONED"},
    "coturn-dtls": {"text": "DTLS on 5349 is opt-in since 4.17.0 and requires dtls.", "components": ["dtls"], "sources": ["dtls:s24abe2486071"], "status": "REASONED"},
    "coturn-relays": {"text": "On-demand relay endpoints use min-port/max-port 49152-65535.", "components": ["coturn"], "sources": ["coturn:s5ec265938c96"], "status": "REASONED"},
    "coturn-cli": {"text": "CLI 5766 defaults off and uses loopback plus cli-password when enabled; use cli=false, since --no-cli retired in 4.18.0.", "components": ["coturn"], "sources": ["coturn:sc4178412962b", "coturn:s5ec265938c96", "coturn:s0728ef023209"], "status": "REASONED"},
    "coturn-admin": {"text": "Web admin 8080 defaults off/loopback and uses separate admin accounts; keep web-admin-listen-on-workers off.", "components": ["coturn"], "sources": ["coturn:sc4178412962b", "coturn:s5ec265938c96"], "status": "REASONED"},
    "coturn-metrics": {"text": "Prometheus 9641 defaults off but binds wildcard without authentication when enabled; set prometheus-address=127.0.0.1.", "components": ["coturn"], "sources": ["coturn:s5ec265938c96"], "status": "REASONED"},
    "coturn-anonymous": {"text": "Stock example with no users and no credential mechanism permits anonymous allocation; static users imply long-term auth. The Docker exception lacks its own citation.", "components": ["coturn"], "sources": ["coturn:sc4178412962b", "coturn:s5ec265938c96", "coturn:s3a76feb6f5e4"], "status": "REASONED"},
    "coturn-longterm": {"text": "Enable lt-cred-mech, a stable realm and generated user credentials; set certificate/key paths for TLS.", "components": ["coturn"], "sources": ["coturn:sc4178412962b", "coturn:s5ec265938c96"], "status": "REASONED"},
    "coturn-secret": {"text": "For timed application credentials use use-auth-secret/static-auth-secret instead of static user lines; never distribute the shared secret.", "components": ["coturn"], "sources": ["coturn:s5ec265938c96"], "status": "REASONED"},
    "coturn-realm": {"text": "Missing realm warns rather than preventing startup; set it explicitly for either credential mode.", "components": ["coturn"], "sources": ["coturn:s5ec265938c96"], "status": "REASONED"},
    "coturn-encryption": {"text": "TLS availability does not require encryption: plaintext can use 3478 or 5349. no-tcp/no-udp remove plaintext; enable dtls for encrypted UDP clients.", "components": ["coturn", "dtls"], "sources": ["coturn:sc4178412962b", "coturn:s5ec265938c96", "dtls:s24abe2486071"], "status": "REASONED"},
    "coturn-loopback": {"text": "Loopback peers are blocked unless allow-loopback-peers is set; leave it off.", "components": ["coturn"], "sources": ["coturn:sc4178412962b", "coturn:s7eb31b944cf1"], "status": "REASONED"},
    "coturn-private": {"text": "RFC 1918 peers are not denied by default; explicitly deny all private ranges and enforce network controls.", "components": ["coturn"], "sources": ["coturn:sc4178412962b", "coturn:s7eb31b944cf1"], "status": "REASONED"},
    "coturn-linklocal": {"text": "4.18.0 scope checks reject IPv4 link-local and IPv6 link-local/ULA; explicit denies remain defense in depth across older/modified builds.", "components": ["coturn"], "sources": ["coturn:s7eb31b944cf1"], "status": "REASONED"},
    "coturn-multicast": {"text": "Multicast is permitted unless no-multicast-peers is set.", "components": ["coturn"], "sources": ["coturn:sc4178412962b", "coturn:s7eb31b944cf1"], "status": "REASONED"},
    "coturn-exceptions": {"text": "allowed-peer-ip adds exceptions rather than establishing a default-deny allowlist.", "components": ["coturn"], "sources": ["coturn:s5ec265938c96", "coturn:s7eb31b944cf1"], "status": "REASONED"},
    "coturn-binding": {"text": "STUN Binding stays anonymous with TURN auth; secure-stun requests authenticated Binding.", "components": ["coturn"], "sources": ["coturn:s5ec265938c96"], "status": "REASONED"},
    "coturn-reflection": {"text": "Anonymous 401 challenges still reflect traffic; unauthorized-ratelimit defaults off and bounds it when enabled.", "components": ["coturn"], "sources": ["coturn:s5ec265938c96"], "status": "REASONED"},
    "coturn-rfc5780": {"text": "RFC 5780 is disabled by default; leave this response-enlarging feature off.", "components": ["coturn"], "sources": ["coturn:s5ec265938c96"], "status": "REASONED"},
    "coturn-permissions": {"text": "Do not enable server-relay, which removes relay permission checks.", "components": ["coturn"], "sources": ["coturn:s5ec265938c96"], "status": "REASONED"},
    "turn-plaintext": {"text": "Plain TURN hides the long-term password itself but exposes usernames/metadata and enables offline guesses against weak passwords.", "components": ["coturn"], "sources": ["coturn:s5ec265938c96"], "status": "REASONED"},
    "verify-listeners": {"text": "Inventory TCP/UDP and actual allocations: media/TURN may be public, signaling/admin/metrics must be restricted; separately test off-host reachability.", "components": ["livekit-docs", "livekit", "coturn"], "sources": ["livekit-docs:s66f19d919eb5", "livekit:sc52b46730181", "coturn:s5ec265938c96"], "status": "REASONED", "verify": [1]},
    "verify-livekit": {"text": "Unauthenticated rtc/validate 401 only tests token requirement, not removal of a known signing key; its handler is not cited.", "components": ["livekit-docs", "curl", "livekit"], "sources": ["livekit-docs:sb6a31fba4f62", "curl:s2b2686afaf41", "livekit:sdd5650ac94ff"], "status": "REASONED", "verify": [2]},
    "verify-rotation": {"text": "Accept an old-key token on an isolated fixture, reject that same unexpired correctly scoped token after rotation, and accept a new-key token.", "components": ["livekit-docs", "lk"], "sources": ["livekit-docs:sb6a31fba4f62", "lk:s6a98a324f01b"], "status": "REASONED", "verify": [4]},
    "verify-extra": {"text": "Separately probe metrics, debug routes/port and embedded TURN from untrusted networks; a healthy root path proves no protection.", "components": ["livekit", "livekit-docs"], "sources": ["livekit:sc52b46730181", "livekit-docs:s66f19d919eb5"], "status": "REASONED"},
    "verify-allocation": {"text": "Anonymous Allocate must challenge with no relay address; valid throwaway credentials on a private plaintext fixture must allocate. Read output, not exit status.", "components": ["coturn"], "sources": ["coturn:s5ec265938c96", "coturn:s0c57f0580b5c"], "status": "REASONED", "verify": [3]},
    "verify-peers": {"text": "Authenticated CreatePermission/ChannelBind to owned denied peers must return 403 with no traffic; cover denied ranges and both families.", "components": ["coturn"], "sources": ["coturn:s7eb31b944cf1", "coturn:s0c57f0580b5c"], "status": "REASONED", "verify": [3]},
    "uclient-argv": {"text": "turnutils_uclient has only argv password inputs -w/-W at 4.18.0; use a prompted throwaway user, never a production password or -W shared secret.", "components": ["coturn"], "sources": ["coturn:se7856434c3d0", "coturn:s1942d0158590", "coturn:s0e40b57274d6", "coturn:sdd3c00ef7290", "coturn:s414c246eed7f", "coturn:s6ba3cc5d04ea", "coturn:sed853e8fb3e3", "coturn:se9819d0c6412", "coturn:s51a288a4b86e", "coturn:s790c96d8eed7"], "status": "REASONED", "verify": [3]},
    "uclient-lifetime": {"text": "Run on a trusted host, remove the test user afterwards and omit -h, which keeps the password-bearing process alive indefinitely.", "components": ["coturn"], "sources": ["coturn:s0c57f0580b5c"], "status": "REASONED", "verify": [3]},
    "lk-inputs": {"text": "lk reads argv or environment credentials, not stdin; explicit project/subdomain outrank environment, which outranks local/default projects.", "components": ["lk"], "sources": ["lk:sa42f9b5ed5d4"], "status": "REASONED"},
    "lk-storage": {"text": "Saved projects retain plaintext api_secret in ~/.livekit/cli-config.yaml, written 0600.", "components": ["lk"], "sources": ["lk:sf8b161b60423"], "status": "REASONED"},
    "lk-mint": {"text": "Prompt and prefix environment assignments keep secrets out of argv/history but expose them to same-account/root environment readers; printed short-lived tokens are secrets.", "components": ["lk"], "sources": ["lk:sa42f9b5ed5d4", "lk:s6a98a324f01b"], "status": "REASONED", "verify": [4]},
    "verify-tls": {"text": "Fatal hostname/CA verification tests only TURN certificate/handshake; separately test plaintext rejection on 3478 and 5349. OpenSSL syntax is not cited.", "components": ["coturn", "openssl-cli"], "sources": ["coturn:sc4178412962b", "openssl-cli:s00aaf106164f"], "status": "REASONED", "verify": [5]}
  }
}
---
# Realtime voice and video infrastructure: LiveKit and coturn

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-05; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| livekit-ports: Signaling/API use 7880, RTC TCP 7881 and normal UDP media 50000-60000; development uses UDP mux 7882. | LiveKit v1.13.7; LiveKit documentation unknown | REASONED |
| livekit-bind: Unset signaling/RTC TCP binds are wildcard; UDP uses eligible interfaces independently of signaling restrictions. | LiveKit v1.13.7; LiveKit documentation unknown | REASONED |
| livekit-turn: Embedded TURN defaults off and needs explicit ports when enabled. | LiveKit v1.13.7; LiveKit documentation unknown | REASONED |
| livekit-keys: Normal mode refuses an empty key map; API secrets sign HS256 room and administrative JWT grants. | LiveKit v1.13.7; LiveKit documentation unknown | REASONED |
| livekit-dev: Development mode supplies devkey/secret when keys are empty and defaults signaling to loopback only when no bind is supplied. | LiveKit v1.13.7 | REASONED |
| livekit-samples: Remove the sample key1/secret1 and key2/secret2 pairs from every effective key set. | LiveKit v1.13.7 | REASONED |
| livekit-length: Outside development, secrets shorter than 32 characters only log an error; generate long random secrets. | LiveKit v1.13.7 | REASONED |
| livekit-grants: canPublish and canSubscribe default true; signing secrets mint any grant, so deliberately scope issued tokens. | LiveKit documentation unknown | REASONED |
| livekit-keyfile: Use key_file with service-owned mode 0600; world permissions reject startup, but group-readable 0640 passes the server check. | LiveKit v1.13.7 | REASONED |
| livekit-tls: Front signaling with TLS/WSS; the guide describes no native signaling TLS and calls Serve, but the server implementation is not cited. | LiveKit documentation unknown; LiveKit v1.13.7 | REASONED |
| livekit-metrics: Enabled metrics are unauthenticated unless prometheus.username/password are set. | LiveKit v1.13.7 | REASONED |
| livekit-debug: Debug/pprof, goroutine and room routes lack grant checks and can use debug_handler.port; route implementations are not cited. | LiveKit v1.13.7 | REASONED |
| livekit-turn-secret: Embedded TURN derives credentials from the API secret; the derivation implementation is not cited. | LiveKit v1.13.7 | REASONED |
| livekit-webhook: Webhook receivers must verify the signing token and SHA-256 body hash; the webhook verifier is not cited. | LiveKit documentation unknown | REASONED |
| coturn-listeners: STUN/TURN use UDP/TCP 3478 and TLS 5349; enabled interfaces are enumerated, not loopback-only. | coturn 4.18.0 | REASONED |
| coturn-dtls: DTLS on 5349 is opt-in since 4.17.0 and requires dtls. | coturn DTLS opt-in introduction 4.17.0 | REASONED |
| coturn-relays: On-demand relay endpoints use min-port/max-port 49152-65535. | coturn 4.18.0 | REASONED |
| coturn-cli: CLI 5766 defaults off and uses loopback plus cli-password when enabled; use cli=false, since --no-cli retired in 4.18.0. | coturn 4.18.0 | REASONED |
| coturn-admin: Web admin 8080 defaults off/loopback and uses separate admin accounts; keep web-admin-listen-on-workers off. | coturn 4.18.0 | REASONED |
| coturn-metrics: Prometheus 9641 defaults off but binds wildcard without authentication when enabled; set prometheus-address=127.0.0.1. | coturn 4.18.0 | REASONED |
| coturn-anonymous: Stock example with no users and no credential mechanism permits anonymous allocation; static users imply long-term auth. The Docker exception lacks its own citation. | coturn 4.18.0 | REASONED |
| coturn-longterm: Enable lt-cred-mech, a stable realm and generated user credentials; set certificate/key paths for TLS. | coturn 4.18.0 | REASONED |
| coturn-secret: For timed application credentials use use-auth-secret/static-auth-secret instead of static user lines; never distribute the shared secret. | coturn 4.18.0 | REASONED |
| coturn-realm: Missing realm warns rather than preventing startup; set it explicitly for either credential mode. | coturn 4.18.0 | REASONED |
| coturn-encryption: TLS availability does not require encryption: plaintext can use 3478 or 5349. no-tcp/no-udp remove plaintext; enable dtls for encrypted UDP clients. | coturn 4.18.0; coturn DTLS opt-in introduction 4.17.0 | REASONED |
| coturn-loopback: Loopback peers are blocked unless allow-loopback-peers is set; leave it off. | coturn 4.18.0 | REASONED |
| coturn-private: RFC 1918 peers are not denied by default; explicitly deny all private ranges and enforce network controls. | coturn 4.18.0 | REASONED |
| coturn-linklocal: 4.18.0 scope checks reject IPv4 link-local and IPv6 link-local/ULA; explicit denies remain defense in depth across older/modified builds. | coturn 4.18.0 | REASONED |
| coturn-multicast: Multicast is permitted unless no-multicast-peers is set. | coturn 4.18.0 | REASONED |
| coturn-exceptions: allowed-peer-ip adds exceptions rather than establishing a default-deny allowlist. | coturn 4.18.0 | REASONED |
| coturn-binding: STUN Binding stays anonymous with TURN auth; secure-stun requests authenticated Binding. | coturn 4.18.0 | REASONED |
| coturn-reflection: Anonymous 401 challenges still reflect traffic; unauthorized-ratelimit defaults off and bounds it when enabled. | coturn 4.18.0 | REASONED |
| coturn-rfc5780: RFC 5780 is disabled by default; leave this response-enlarging feature off. | coturn 4.18.0 | REASONED |
| coturn-permissions: Do not enable server-relay, which removes relay permission checks. | coturn 4.18.0 | REASONED |
| turn-plaintext: Plain TURN hides the long-term password itself but exposes usernames/metadata and enables offline guesses against weak passwords. | coturn 4.18.0 | REASONED |
| verify-listeners: Inventory TCP/UDP and actual allocations: media/TURN may be public, signaling/admin/metrics must be restricted; separately test off-host reachability. | LiveKit documentation unknown; LiveKit v1.13.7; coturn 4.18.0 | REASONED |
| verify-livekit: Unauthenticated rtc/validate 401 only tests token requirement, not removal of a known signing key; its handler is not cited. | LiveKit documentation unknown; curl minimum write-out version 7.75.0; LiveKit v1.13.7 | REASONED |
| verify-rotation: Accept an old-key token on an isolated fixture, reject that same unexpired correctly scoped token after rotation, and accept a new-key token. | LiveKit documentation unknown; livekit-cli v2.18.2 | REASONED |
| verify-extra: Separately probe metrics, debug routes/port and embedded TURN from untrusted networks; a healthy root path proves no protection. | LiveKit v1.13.7; LiveKit documentation unknown | REASONED |
| verify-allocation: Anonymous Allocate must challenge with no relay address; valid throwaway credentials on a private plaintext fixture must allocate. Read output, not exit status. | coturn 4.18.0 | REASONED |
| verify-peers: Authenticated CreatePermission/ChannelBind to owned denied peers must return 403 with no traffic; cover denied ranges and both families. | coturn 4.18.0 | REASONED |
| uclient-argv: turnutils_uclient has only argv password inputs -w/-W at 4.18.0; use a prompted throwaway user, never a production password or -W shared secret. | coturn 4.18.0 | REASONED |
| uclient-lifetime: Run on a trusted host, remove the test user afterwards and omit -h, which keeps the password-bearing process alive indefinitely. | coturn 4.18.0 | REASONED |
| lk-inputs: lk reads argv or environment credentials, not stdin; explicit project/subdomain outrank environment, which outranks local/default projects. | livekit-cli v2.18.2 | REASONED |
| lk-storage: Saved projects retain plaintext api_secret in ~/.livekit/cli-config.yaml, written 0600. | livekit-cli v2.18.2 | REASONED |
| lk-mint: Prompt and prefix environment assignments keep secrets out of argv/history but expose them to same-account/root environment readers; printed short-lived tokens are secrets. | livekit-cli v2.18.2 | REASONED |
| verify-tls: Fatal hostname/CA verification tests only TURN certificate/handshake; separately test plaintext rejection on 3478 and 5349. OpenSSL syntax is not cited. | coturn 4.18.0; OpenSSL CLI 3.0 | REASONED |
<!-- version-basis:end -->

AI voice agents run on self-hosted realtime backends that carry live media, and two of them sit at the network edge: LiveKit, a WebRTC SFU that routes participants' audio, video, and data, and coturn, a TURN/STUN server that relays media when a direct peer path cannot be found. The relay is the sharp edge. A TURN server proxies traffic on a client's behalf, so an unauthenticated or misconfigured one is an *open relay*: an attacker uses it to launder traffic, to reach services on the host's own loopback and private network, and to reflect and amplify UDP toward a victim. LiveKit's edge is different: it will not start without API keys, so the danger is not an anonymous join but a *known or weak* signing secret, which lets anyone mint a token and enter any room to eavesdrop or inject media. LiveKit terminates no TLS on its signaling, so [fronting-auth.md](fronting-auth.md) is the reverse-proxy pattern it needs for `wss://`; coturn terminates TLS and DTLS natively from its own certificate. [secrets.md](secrets.md) covers generating and holding the signing material. Values below are illustrative; replace them.

## LiveKit

LiveKit's HTTP/WebSocket signaling and API listen on `7880`, and ICE media uses a separate TCP mux on `7881`; outside development mode the UDP media sockets are allocated from a range of `50000` to `60000` (development mode instead uses a single UDP mux port, `7882`). With no explicit `bind_addresses`, the signaling and RTC TCP listeners bind the wildcard address, and the UDP media sockets bind each eligible interface address; restricting the signaling bind does not restrict the RTC sockets, which is why a relay or media port can be reachable while signaling is on loopback. The embedded TURN service is off by default and, if enabled, needs its ports set explicitly.

Authentication is by API key/secret pairs, and access tokens are HS256 JWTs that carry room grants (`roomJoin`, `room`, `canPublish`, `canSubscribe`, administrative grants such as `roomCreate`) and are signed with the secret. The critical default is that **a normal-mode server refuses to start with no keys configured** (`ValidateKeys()` returns an error), so an exposed instance is not an anonymous free-for-all. The real exposures are the ways a *usable* secret ends up known:

- **Development mode** (`--dev`) injects a hard-coded pair, `devkey` / `secret`, when the key map is empty, and (when no bind is supplied) defaults signaling to loopback. The local quickstart selects it deliberately. Never run it on an exposed host: anyone can sign a valid admin token.
- **The upstream `config-sample.yaml` ships uncommented `key1: secret1` and `key2: secret2` entries.** These are examples, not generated credentials; remove every one from the effective key set.
- **A short secret does not block startup.** Outside development mode a secret under 32 characters only logs an error; it still runs. Treat that log as a finding, and generate a long random secret.

Because a signing secret mints any grant, guard it like a root credential, and note that omitted grants are permissive: `canPublish` and `canSubscribe` default to true, so scope tokens deliberately. Generate a real pair and keep it in a key file rather than the main config:

```yaml
# livekit.yaml: front this with a proxy for wss:// (LiveKit terminates no TLS on signaling)
development: false
port: 7880
bind_addresses: ["127.0.0.1"]
key_file: /etc/livekit/keys.yaml

rtc:
  tcp_port: 7881
  port_range_start: 50000
  port_range_end: 60000
```

```yaml
# /etc/livekit/keys.yaml: generate the pair (e.g. `livekit-server generate-keys`); replace both
REPLACE_WITH_GENERATED_API_KEY: "REPLACE_WITH_GENERATED_RANDOM_SECRET"
```

LiveKit refuses a key file that grants any permission to others (it checks the world/other bits), so a world-readable `0644` file stops the server from starting; a group-readable `0640` passes that check, so create the file `0600` owned by the service account to keep the group out as well. Signaling TLS terminates at a reverse proxy or load balancer: the core server calls `Serve`, not `ServeTLS`, and there is no top-level signaling TLS flag, so front it with the [fronting-auth.md](fronting-auth.md) pattern and connect over `wss://`. A few surfaces are easy to leave open beside the main port: Prometheus metrics, when enabled, serve unauthenticated unless you set `prometheus.username`/`password`; the debug and profiling routes (`/debug/pprof/`, `/debug/goroutine`, `/debug/rooms`) carry no grant check and, with `debug_handler.port` set, listen on their own port; and the embedded TURN service derives its credentials from the same API secret, so a leaked secret also undermines TURN. Webhook receivers must verify both the signing token and the SHA-256 body hash, not merely accept TLS.

Unverified until checked in your deployment: whether a Helm chart or package generator creates or overrides keys and binds, the effective bind of a distribution's sample config, and the JWT-library version your build pins.

## coturn

coturn listens on `3478` for STUN/TURN over both UDP and TCP, and on `5349` for TLS; **DTLS on `5349` has been opt-in since 4.17.0** and is off unless you set `dtls`. Relay endpoints are allocated on demand from `49152` to `65535` (`min-port`/`max-port`). Three side surfaces are each off until enabled: the telnet CLI (`5766`) and web admin (`8080`) bind loopback when on, but **Prometheus (`9641`) binds a wildcard address when enabled and serves metrics with no authentication**; pin it with `prometheus-address=127.0.0.1` if you use it. The default listener is *not* loopback-only: coturn enumerates addresses on every interface that is up.

The default that matters most is authentication. **With the stock example configuration (no users, and both `lt-cred-mech` and `use-auth-secret` commented out), TURN allocation is anonymous**, which is an open relay. That is the out-of-box example, not every install (the upstream Docker image ships `lt-cred-mech` on, and defining static users implies long-term auth), so confirm the effective config rather than assuming either way. Enable one credential mode and a stable realm:

```ini
# turnserver.conf: long-term credentials
lt-cred-mech
realm=turn.example.com
user=REPLACE_WITH_USER:REPLACE_WITH_RANDOM_PASSWORD

listening-port=3478
tls-listening-port=5349
cert=/etc/coturn/fullchain.pem
pkey=/etc/coturn/private-key.pem

# Relay policy: a starting denylist, not a complete one. Deny the metadata address and every
# private range explicitly; do not rely on coturn's built-in scope checks alone across versions.
allow-loopback-peers=false
no-multicast-peers
denied-peer-ip=169.254.0.0-169.254.255.255
denied-peer-ip=10.0.0.0-10.255.255.255
denied-peer-ip=172.16.0.0-172.31.255.255
denied-peer-ip=192.168.0.0-192.168.255.255
denied-peer-ip=fc00::-fdff:ffff:ffff:ffff:ffff:ffff:ffff:ffff
denied-peer-ip=fe80::-febf:ffff:ffff:ffff:ffff:ffff:ffff:ffff

cli=false
web-admin=false
```

For application-generated time-limited credentials, replace the `lt-cred-mech`/`user` lines with `use-auth-secret` and a `static-auth-secret` (plus the same `realm`); keep that shared secret in the server config, never distribute it to clients. A realm is an operational requirement for both modes, not a hard startup gate: omitting it warns rather than refuses, so set it explicitly.

Two properties of that config are worth stating plainly. First, **enabling TLS is not the same as requiring it**: coturn autodetects protocols across ports and still accepts plaintext STUN/TURN on `3478` (and even on the TLS-numbered port). Opening `5349` proves TLS is *available*, not that encryption is *mandatory*. To require encrypted client transport, drop the plaintext client listeners with `no-tcp` and `no-udp`, keeping TLS; because that removes the plain-UDP path, enable `dtls` so UDP clients can still connect over DTLS, or accept that clients are TLS-over-TCP only. This affects client transport, not the UDP relay to peers. Second, the relay destination policy does not fully contain a relay by default:

- **Loopback** (`127.0.0.0/8`, `::1`) is blocked unless you set `allow-loopback-peers`; leave it off.
- **RFC 1918 private ranges are *not* blocked by default and must be denied explicitly**, as in the block above (`10/8`, `172.16/12`, `192.168/16`); without those lines an authenticated user, or on the stock config an anonymous one, relays into your internal network. Stock coturn 4.18.0 *does* reject IPv4 link-local (`169.254.0.0/16`, the `169.254.169.254` metadata address) and IPv6 link-local/ULA through built-in scope checks, but older or modified builds have not, so the explicit link-local and IPv6 denies above are defense in depth rather than the only barrier to the metadata endpoint.
- **Multicast** is allowed unless `no-multicast-peers` is set.
- `allowed-peer-ip` is an exception list, not a default-deny allowlist: an address it does not name can still be permitted.

STUN Binding stays anonymous even when TURN allocation requires credentials, and closing anonymous allocation does not close reflection: an unauthenticated request still draws a `401` challenge response that can itself reflect and amplify toward a spoofed source. `unauthorized-ratelimit` (off by default) bounds that, `secure-stun` requests authenticated Binding, and RFC 5780 (a reflection amplifier) is off by default, so leave it off. The two admin surfaces authenticate separately from TURN users and from each other: the CLI uses `cli-password`, while the web admin uses its own provisioned admin accounts, so setting `cli-password` does not secure the web admin. Disable both (`cli=false`, `web-admin=false`) or keep them on loopback, keep `web-admin-listen-on-workers` off, and do not enable `server-relay`, which drops permission checks on relayed traffic. `--no-cli` is retired in 4.18.0, so use `cli=false`.

Unverified until checked in your deployment: the default service state and effective configuration of any specific distro or container image, the build's TLS/feature availability, and real reflection/amplification factors.

## Shared exposures

- **An open TURN relay reaches your internal network and amplifies UDP.** An anonymous (or abusive authenticated) allocator originates traffic through the relay to any permitted, reachable peer, which is an SSRF-like path into your private network and the cloud-metadata endpoint, plus a UDP amplification vector. Authentication closes anonymous allocation; explicit `denied-peer-ip` policy and network controls are still needed against authenticated abuse.
- **A weak or development LiveKit secret forges room admission.** A known signing secret lets an attacker choose identities and grants, so publishing, subscribing, or administering rooms all become available. Application end-to-end encryption is a separate content boundary, not a substitute for protecting the secret.
- **Plaintext signaling or relay.** Public HTTP/WS exposes signaling and bearer tokens in transit. Plaintext TURN does not send the long-term password itself (the protocol proves knowledge of it through a challenge and message integrity), but it exposes usernames and protocol metadata and permits offline guessing against a weak password, so terminate TLS and require it. Media transport encryption is a separate layer again.
- **STUN reflection and amplification.** Binding and `401`-challenge responses are unauthenticated regardless of TURN auth, so a spoofed source can reflect UDP toward a victim; rate limiting and disabling response-enlarging features reduce it, but authenticating allocation does not remove it.

## Verify

Every probe below is reasoned, not demonstrated: the authoring environment has no container runtime, so the outcomes are derived from the cited vendor sources rather than observed. A redirect, a `404`, a timeout, or a TLS error is inconclusive, never proof of the fixed state; every negative check needs a working positive control.

```bash
# REASONED: listener expectations follow the cited vendor sources; no container runtime is available.
sudo ss -tlnp    # Read the bind address per port, do not just confirm the port. LiveKit signaling 7880
sudo ss -aunp    # should be on loopback (behind the proxy); RTC 7881 and coturn 3478/5349 are expected
                 # PUBLIC (a relay and media are useless if unreachable), so their public bind is normal,
                 # not the finding. The findings are: a wildcard-bound 7880, or any exposed CLI 5766,
                 # web-admin 8080, or metrics 9641/6789. coturn 3478 is a persistent listener; the LiveKit
                 # 50000-60000 media range and coturn 49152-65535 relay range appear only during active
                 # calls/allocations. A private bind is not external isolation: confirm reachability from
                 # off-host separately, since NAT or Docker forwarding can publish a loopback-bound port.
```

REASONED: following block; LiveKit token expectations follow the cited token guidance; no container runtime is available.

```bash
# LiveKit reachability/auth diagnostic against the direct listener. This ONLY shows the endpoint requires
# a token; it does NOT prove the dev/known secret is gone (see the rotation test below). Substitute the
# base URL inside the single quotes on the set -- line and paste the whole block so the guard runs.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_LIVEKIT_BASE_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the LiveKit base URL on the set -- line above; not probing"; exit 2 ;;
    http://*|https://*) : ;;
    *) echo "expected an http:// or https:// URL; not probing"; exit 2 ;;
  esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1/rtc/validate"
)
```

The **decisive** LiveKit check is a key-rotation test that discriminates the exposed state, because an unauthenticated `/rtc/validate` returns `401` whether or not the dev key is still in use. Mint a correctly scoped token signed with the old (`devkey`/`secret`, or a retired real) secret with `livekit-cli` (the guarded block below) or a JWT tool that takes the signing secret from stdin, an owner-only file or its environment, never from its command line, confirm it is *accepted* on an isolated development fixture, then confirm the *same token is rejected* against the deployment after its key is rotated, while a token signed with the new key is accepted. An expired or wrong-room token is an invalid rotation test, and the isolated fixture is what keeps the dev secret off the public instance. Separately probe the metrics and debug routes (and any `debug_handler.port`) and the embedded TURN sockets from an untrusted network; a healthy `/` proves none of them protected.

For coturn, the discriminator is a TURN **Allocate** exchange, not an HTTP request. Send a well-formed Allocate requesting UDP relay with no credentials: an allocation containing a relayed address means anonymous allocation is open, while an authentication challenge with no allocation means it is closed (the required positive control is a valid-credential allocation, because the initial `401` also occurs during a successful authenticated exchange). Closing anonymous allocation is not the whole fix: authenticated, request `CreatePermission`/`ChannelBind` for an owned RFC 1918 or `169.254.169.254` test peer and confirm a `403` with no traffic reaching it, across the denied ranges and both address families (a plain allocation failure or timeout is not evidence of peer policy). coturn ships `turnutils_uclient` for the allocation test; run it against an isolated, plaintext-enabled authentication fixture (the hardened deployment may set `no-udp`, and you must never re-open public plaintext to get a positive control). It needs a peer address via `-e`: point it at an owned permitted peer here, or at a denied internal address to test peer policy (expect refusal).

`turnutils_uclient` takes the TURN password only on its command line, as `-w`, and `-W`, which takes a REST-API shared secret instead, is also an argument. At coturn 4.18.0 the client's option parser copies both from `optarg`, and a trace of the password buffer across the six files its build target lists in `src/apps/uclient/CMakeLists.txt` (`mainuclient.c`, `uclient.c`, `startuclient.c`, `uclient.h`, `startuclient.h` and `session.h`) found no stdin, environment, file, argument-file or prompt input for it, and across the whole 4.18.0 source tree the buffer is written only from `-w` and from the password `-W` derives. No other TURN client that takes the password outside argv was evaluated for this guide (backlog row 1.140); prefer one if you have it. The block below prompts for the password, which keeps it out of shell history, the terminal's scrollback and the pasted text, but that is not an argv fix. While the credentialed run lasts, the password is in that process's argv, readable through `ps` and `/proc/<pid>/cmdline` by every local account, your own and root included, and command-line auditing on the host can record it beyond that; an observer can keep a copy. Bound the exposure instead:

- Create a throwaway user on the isolated fixture for this test only, with no more access than the test needs, and remove it afterwards. Never use a production credential.
- Never use `-W` in this test, whatever secret it would carry: it takes a long-lived TURN REST API shared secret, which never qualifies, and a deployment's `static-auth-secret` would put the secret that mints every credential into argv.
- Do not add `-h`, which makes the client hang on indefinitely after the last sent packet, and keeps the password in its argv for as long as it does.
- Run the block from a host with no untrusted local users.

Read the verbose output, not the exit status: the anonymous run must show a `401` challenge and no relayed address, and the credentialed run, the positive control, must show a relayed address. Substitute the test user, the peer and the TURN host inside the single quotes, and paste the whole block. It assumes a clean shell (CONTRIBUTING rule 7).

REASONED: following block; Allocate and peer-policy outcomes follow the cited coturn 4.18.0 sources; no container runtime is available.

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_TEST_USER' 'REPLACE_WITH_OWNED_PEER_IP' 'REPLACE_WITH_TURN_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 3 ] || { echo "the set -- line needs exactly 3 values; not probing"; exit 2; }
  case "|$1|$2|$3|" in
    *REPLACE_WITH_*|*'||'*|*'|-'*|*[[:cntrl:]]*)
      echo "substitute the test user, peer and TURN host on the set -- line above (no empty value, none starting with -); not probing"; exit 2 ;;
  esac
  { unset -n pw && unset -v pw; } 2>/dev/null || { echo 'cannot clear pw in this shell; not probing'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not probing'; exit 2; }
  echo '--- no credentials: expect a 401 challenge and NO relayed address'
  turnutils_uclient -v -e "$2" "$3"
  IFS= read -r -s -p 'Throwaway test password (input hidden; it WILL be in argv while the next command runs): ' pw < /dev/tty ||
    { echo 'password input failed; not probing'; exit 2; }
  printf '\n'
  case "$pw" in
    ""|*REPLACE_WITH_*|*[[:cntrl:]]*) echo 'empty password, placeholder or control character; not probing'; exit 2 ;;
  esac
  echo '--- throwaway credentials (the positive control): expect a relayed address'
  # guard-conventions: allow argv-only TURN password at coturn 4.18.0; prompted throwaway credential on a trusted host under the rule 7 restrictions above
  turnutils_uclient -v -u "$1" -w "$pw" -e "$2" "$3"
)
```

For the LiveKit rotation test, mint each token with `livekit-cli` (`lk`). `lk` takes the API key and secret from `--api-key` and `--api-secret`, which put them in argv, or from `LIVEKIT_API_KEY` and `LIVEKIT_API_SECRET`, and has no stdin input for them (checked at livekit-cli v2.18.2). A saved project (`lk project add`) is a file input, but it keeps a plaintext copy of the secret in `~/.livekit/cli-config.yaml` until removed, the opposite of what a rotation is for. `lk` uses the environment pair unless `--project` or `--subdomain` is given, ahead of a `livekit.toml` in the working directory and any saved default project, so run the block with neither flag.

The block prompts for the secret, so it stays out of shell history, and hands it and the key to the one `lk` command as a prefix assignment, never exported. That moves the secret out of argv, not out of reach: while `lk` runs, the same account and root can read it from `/proc/<pid>/environ`. Run the block once with the old key and once with the new. For the public development pair the key is `devkey` and the secret typed at the prompt is `secret`. Each printed token is a bearer credential for its grants until it expires, so keep `--valid-for` short and treat the terminal output as a secret. Keep the old-key token: the same token must be accepted on the isolated development fixture and rejected by the deployment after rotation, and the new-key token must be accepted. Substitute the key inside the single quotes, and paste the whole block. It assumes a clean shell (CONTRIBUTING rule 7).

REASONED: following block; token minting and rotation follow the cited LiveKit and livekit-cli sources; no container runtime is available.

```bash
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_API_KEY'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not minting"; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not minting"; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the old or the new API key on the set -- line above; not minting"; exit 2 ;;
  esac
  { unset -n sec LIVEKIT_API_KEY LIVEKIT_API_SECRET && unset -v sec LIVEKIT_API_KEY LIVEKIT_API_SECRET; } 2>/dev/null ||
    { echo 'cannot clear sec, LIVEKIT_API_KEY or LIVEKIT_API_SECRET in this shell; not minting'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not minting'; exit 2; }
  IFS= read -r -s -p 'API secret for that key (input hidden): ' sec < /dev/tty ||
    { echo 'secret input failed; not minting'; exit 2; }
  printf '\n'
  case "$sec" in
    ""|*REPLACE_WITH_*|*[[:cntrl:]]*) echo 'empty secret, placeholder or control character; not minting'; exit 2 ;;
  esac
  LIVEKIT_API_KEY="$1" LIVEKIT_API_SECRET="$sec" lk token create --join --room test --identity probe --valid-for 5m
)
```

Verify TLS separately, and require verification to be fatal so a diagnostic tool does not continue past a bad certificate:

REASONED: following block; TURN TLS expectations follow the cited coturn configuration; no container runtime is available.

```bash
openssl s_client -connect turn.example.com:5349 -servername turn.example.com \
  -verify_hostname turn.example.com -verify_return_error \
  -CAfile /etc/ssl/certs/ca-certificates.crt </dev/null
```

That proves the certificate and handshake only, not TURN authentication, peer policy, or that plaintext is refused; also send plain STUN/TURN to `3478` and to `5349` and confirm it is rejected once `no-tcp`/`no-udp` are set. A local socket binding proves neither public reachability nor TLS. Never add `-k`/`--insecure` to any of these.

## Common mistakes

- Running LiveKit in development mode, or leaving the sample `key1: secret1` or `key2: secret2` pairs in the key set, so a public secret mints valid admin tokens; check every retained development and sample pair, not just `devkey`.
- Treating a short signing secret as safe because the server started: the length check only logs and does not block startup.
- Creating a world-readable LiveKit key file, which blocks startup; a group-readable `0640` passes the permission check but still exposes the secret to the group, so use `0600` owned by the service account.
- Running coturn with the stock example config (no `lt-cred-mech`, no users), which relays anonymously, an open relay.
- Enabling authentication but forgetting relay policy, so an authenticated user reaches RFC 1918 hosts, which coturn does not block by default (current builds cover the `169.254.169.254` metadata address with a built-in check, but the explicit deny is the control that survives an older or reconfigured build).
- Opening the coturn TLS port but leaving plain `3478` (and TLS-port plaintext) accepted because `no-tcp`/`no-udp` were not set, so clients still connect unencrypted.
- Assuming TURN credentials protect STUN Binding, the CLI, or the web admin, or that `cli-password` secures the web admin; each is a separate surface, and coturn's Prometheus exporter binds a wildcard address unauthenticated.
- Restricting LiveKit's signaling bind and assuming the RTC and embedded-TURN sockets followed; they bind independently.

## Sources (checked September 2026)

- LiveKit ports and firewall reference (`7880`, `7881`, UDP media range, single-port mux): https://docs.livekit.io/transport/self-hosting/ports-firewall/
- LiveKit key validation (`ValidateKeys()` errors on an empty key map and on a key file readable by others; the sub-32-character secret log): https://raw.githubusercontent.com/livekit/livekit/v1.13.7/pkg/config/config.go
- LiveKit development-mode `devkey`/`secret` injection and conditional loopback bind: https://raw.githubusercontent.com/livekit/livekit/v1.13.7/cmd/server/main.go
- LiveKit sample config (uncommented `key1: secret1` / `key2: secret2`; embedded-TURN, metrics, and debug settings): https://raw.githubusercontent.com/livekit/livekit/v1.13.7/config-sample.yaml
- LiveKit tokens and grants (HS256 JWT, room and admin grants, permissive defaults): https://docs.livekit.io/frontends/reference/tokens-grants/
- LiveKit self-hosting deployment (TLS terminates at a proxy; `wss://`): https://docs.livekit.io/transport/self-hosting/deployment/
- livekit-cli v2.18.2 credential inputs (`--api-key`/`--api-secret` with `LIVEKIT_API_KEY`/`LIVEKIT_API_SECRET` as their environment sources, lines 124-133; `resolveProject` precedence, `--project` and `--subdomain` ahead of the environment pair, lines 328-434; no stdin input): https://raw.githubusercontent.com/livekit/livekit-cli/v2.18.2/cmd/lk/utils.go
- coturn example configuration (anonymous default, `allow-loopback-peers`, `no-multicast-peers`, `no-tcp`/`no-udp`, `cli`/`web-admin` defaults, `cert`/`pkey`, `tls-listening-port`): https://raw.githubusercontent.com/coturn/coturn/4.18.0/examples/etc/turnserver.conf
- coturn option reference (credential modes, `use-auth-secret`, `secure-stun`, `server-relay`, CLI and web-admin auth, `prometheus-address` and its wildcard default, `unauthorized-ratelimit`, relay port range): https://raw.githubusercontent.com/coturn/coturn/4.18.0/README.turnserver
- coturn 4.17.0 release notes (DTLS listeners now opt-in, started only with `--dtls`): https://github.com/coturn/coturn/releases/tag/4.17.0
- coturn 4.18.0 release notes (`--no-cli` retired): https://github.com/coturn/coturn/releases/tag/4.18.0
- coturn peer-address classification and policy (loopback, link-local, RFC 1918, multicast handling): https://raw.githubusercontent.com/coturn/coturn/4.18.0/src/server/ns_turn_server.c
- curl manual (the `exitcode` and `errormsg` write-out variables in the Verify probe, both added in curl 7.75.0): https://curl.se/docs/manpage.html
- livekit-cli v2.18.2 `lk token create` (`--join`, `--room`, `--identity`, `--valid-for`; resolves credentials without requiring a URL, line 410; no stdin read): https://raw.githubusercontent.com/livekit/livekit-cli/v2.18.2/cmd/lk/token.go
- livekit-cli v2.18.2 saved project credentials (`api_secret` in `~/.livekit/cli-config.yaml`, lines 42 and 206, written `0600`, line 192): https://raw.githubusercontent.com/livekit/livekit-cli/v2.18.2/pkg/config/config.go
- coturn 4.18.0 `turnutils_uclient` option parser (`-w` and `-W` copy `optarg`, lines 380-381 and 456-458; no stdin, file or environment input for the password): https://raw.githubusercontent.com/coturn/coturn/4.18.0/src/apps/uclient/mainuclient.c
- coturn 4.18.0 `turnutils_uclient` password-buffer trace (`g_upwd` is declared in `uclient.h` line 132, written only in `mainuclient.c` lines 381 and 553-554, and read only in `uclient.c` lines 3109 and 3132; `startuclient.c`, `startuclient.h` and `session.h` do not reference it; the build target's files are listed in `CMakeLists.txt`): https://github.com/coturn/coturn/blob/4.18.0/src/apps/uclient/uclient.h#L132 , https://github.com/coturn/coturn/blob/4.18.0/src/apps/uclient/mainuclient.c#L553-L554 , https://github.com/coturn/coturn/blob/4.18.0/src/apps/uclient/uclient.c#L3109 , https://github.com/coturn/coturn/blob/4.18.0/src/apps/uclient/uclient.c#L3132 , https://github.com/coturn/coturn/blob/4.18.0/src/apps/uclient/mainuclient.c#L381 , https://github.com/coturn/coturn/blob/4.18.0/src/apps/uclient/startuclient.c , https://github.com/coturn/coturn/blob/4.18.0/src/apps/uclient/startuclient.h , https://github.com/coturn/coturn/blob/4.18.0/src/apps/uclient/session.h and https://github.com/coturn/coturn/blob/4.18.0/src/apps/uclient/CMakeLists.txt
- coturn 4.18.0 `turnutils_uclient` options (`-h` hangs on indefinitely after the last sent packet, line 95): https://raw.githubusercontent.com/coturn/coturn/4.18.0/README.turnutils
- LiveKit v1.13.7 signaling HTTP Serve call (checked October 2026): https://github.com/livekit/livekit/blob/v1.13.7/pkg/service/server.go#L319
- LiveKit v1.13.7 metrics credential gate (checked October 2026): https://github.com/livekit/livekit/blob/v1.13.7/pkg/service/server.go#L165-L170
- LiveKit v1.13.7 debug routes, separate server and listener (checked October 2026): https://github.com/livekit/livekit/blob/v1.13.7/pkg/service/server.go#L181-L193, https://github.com/livekit/livekit/blob/v1.13.7/pkg/service/server.go#L261-L266
- LiveKit v1.13.7 embedded TURN password derivation from the API secret (checked October 2026): https://github.com/livekit/livekit/blob/v1.13.7/pkg/service/turn.go#L315-L325
- LiveKit v1.13.7 missing-grants HTTP 401 branch (checked October 2026): https://github.com/livekit/livekit/blob/v1.13.7/pkg/service/rtcservice.go#L147-L149
- coturn 4.18.0 Docker configuration enables lt-cred-mech (checked October 2026): https://github.com/coturn/coturn/blob/4.18.0/docker/coturn/turnserver.conf#L184
- OpenSSL 3.0 s_client hostname, CA and fatal verification options (checked October 2026): https://docs.openssl.org/3.0/man1/openssl-s_client/
