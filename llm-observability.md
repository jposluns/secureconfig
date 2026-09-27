---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "93bfdc4f83c4b909a31cccd0267de7afb7e8c5fbf7a04b4ebd5c018ba2e41dd4",
  "components": {
    "langfuse": {
      "name": "Langfuse documentation",
      "basis": "unknown",
      "sources": {
        "s34b0fb076e86": "https://langfuse.com/self-hosting/security/authentication-and-sso",
        "sfdfc0ea9fdc1": "https://langfuse.com/docs/api-and-data-platform/features/public-api",
        "sb92c8a6aaad1": "https://langfuse.com/self-hosting/configuration",
        "scd1d81693f96": "https://langfuse.com/self-hosting/administration/headless-initialization"
      }
    },
    "lf-session": {
      "name": "Langfuse session source",
      "basis": "24c949d8dd5617219a8415f80e4c65ad611ff05c",
      "sources": {
        "s01522120437c": "https://github.com/langfuse/langfuse/blob/24c949d8dd5617219a8415f80e4c65ad611ff05c/web/src/env.mjs"
      }
    },
    "lf-compose": {
      "name": "Langfuse Compose",
      "basis": "0dd0a7fbe2feb300b8776f02b3684eeee3fbceab",
      "sources": {
        "s4d19a7b83526": "https://github.com/langfuse/langfuse/blob/0dd0a7fbe2feb300b8776f02b3684eeee3fbceab/docker-compose.yml"
      }
    },
    "phoenix": {
      "name": "Phoenix documentation",
      "basis": "unknown",
      "sources": {
        "s5a90699b7950": "https://arize.com/docs/phoenix/self-hosting/features/authentication"
      }
    },
    "phoenix-tls-min": {
      "name": "Phoenix TLS minimum",
      "basis": "8.29",
      "sources": {
        "s8af9d57a7636": "https://arize.com/docs/phoenix/release-notes/04-2025/04-28-2025-tls-support-for-phoenix-server"
      }
    },
    "phoenix-tls": {
      "name": "Phoenix TLS source",
      "basis": "080959576563900038688ddf01f3bee110005df5",
      "sources": {
        "s33e12a73fb58": "https://github.com/Arize-ai/phoenix/blob/080959576563900038688ddf01f3bee110005df5/src/phoenix/config.py"
      }
    },
    "helicone": {
      "name": "Helicone documentation",
      "basis": "unknown",
      "sources": {
        "s48d6e38bf1fa": "https://docs.helicone.ai/getting-started/self-host/manual",
        "sac4298a08e00": "https://docs.helicone.ai/getting-started/self-host/docker"
      }
    },
    "helicone-compose": {
      "name": "Helicone Compose",
      "basis": "b12ebaccb824ab9778757ca197ff302d97fda421",
      "sources": {
        "s05ca7cfb09fe": "https://github.com/Helicone/helicone/blob/b12ebaccb824ab9778757ca197ff302d97fda421/docker/docker-compose.yml"
      }
    },
    "otel": {
      "name": "OpenTelemetry Collector",
      "basis": "v0.161.0",
      "sources": {
        "s6eb17ad3eb47": "https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/receiver/otlpreceiver/factory.go#L41-L67",
        "s3252b8ba9775": "https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/CHANGELOG.md#L2058-L2070",
        "s5a13f52d7e6d": "https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/CHANGELOG.md#L1793-L1811",
        "sb419d6444c19": "https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/CHANGELOG.md#L1737-L1743",
        "s9780bf233e75": "https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/service/telemetry/otelconftelemetry/factory.go#L49-L64",
        "se93854d097ec": "https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/extension/zpagesextension/factory.go#L15-L29",
        "s6957342b0bf4": "https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/extension/zpagesextension/zpagesextension.go#L87-L105",
        "sdac173d533e6": "https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/config/confighttp/server.go#L352-L364"
      }
    },
    "otel-dist": {
      "name": "Collector distributions",
      "basis": "v0.161.0",
      "sources": {
        "s08ca284a6d6f": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/config.yaml#L1-L81",
        "s9d2ef3c6b75d": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/config.yaml#L1-L81",
        "s7a517873f7be": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/Dockerfile#L10-L15",
        "sc806e2cc23e6": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/Dockerfile#L10-L15",
        "s96832924ecbd": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/.goreleaser.yaml#L86-L118",
        "s3cf497a4401c": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/.goreleaser.yaml#L94-L126",
        "s532d68e28e68": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/otelcol.service#L5-L7",
        "saa59feb48156": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/otelcol-contrib.service#L5-L7",
        "s73f6337cd50e": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/otelcol.conf#L1-L5",
        "sff25af5f7a79": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/otelcol-contrib.conf#L1-L5",
        "sd829f5067d73": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/postinstall.sh#L6-L16",
        "secd03f9c13d6": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/postinstall.sh#L6-L16",
        "s353fc01c0b2c": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/postinstall-rpm.sh#L6-L9",
        "s72fc7a0602d1": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/postinstall-rpm.sh#L6-L9",
        "sb93573df35e2": "https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-k8s/Dockerfile#L1-L17"
      }
    },
    "otel-docs": {
      "name": "Collector security guidance",
      "basis": "unknown",
      "sources": {
        "s5fc11440844b": "https://opentelemetry.io/docs/security/config-best-practices/"
      }
    },
    "basicauth": {
      "name": "Collector Basic auth extension",
      "basis": "1c897ba9c67afc3c9e218b5cd05a6de49435f4de",
      "sources": {
        "s473397b3887e": "https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/basicauthextension"
      }
    },
    "phoenix-auth": {
      "name": "Phoenix gRPC auth source",
      "basis": "f11c885c063f1c9b6146693cda401c5d645d8294",
      "sources": {
        "sdbf548dbb448": "https://github.com/Arize-ai/phoenix/blob/f11c885c063f1c9b6146693cda401c5d645d8294/src/phoenix/server/bearer_auth.py"
      }
    },
    "pprof": {
      "name": "Collector pprof source",
      "basis": "443567a6a00d7cff8cae1432a6fef655d8698e94",
      "sources": {
        "s3f2efc571022": "https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/443567a6a00d7cff8cae1432a6fef655d8698e94/extension/pprofextension/README.md"
      }
    },
    "health": {
      "name": "Collector health source",
      "basis": "d922ffb299c6b9be026f97dd7d6a5f0f507efdeb",
      "sources": {
        "s6ac60517accc": "https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/d922ffb299c6b9be026f97dd7d6a5f0f507efdeb/extension/healthcheckextension/README.md"
      }
    },
    "curl": {
      "name": "curl minimum",
      "basis": "7.75.0",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    },
    "phoenix-bind": {
      "name": "Phoenix listener source",
      "basis": "arize-phoenix-v20.16.0",
      "sources": {
        "s19ffeb67866e": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.16.0/src/phoenix/config.py#L3111-L3117",
        "sfc104ed5254a": "https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.16.0/src/phoenix/server/grpc_server.py#L107-L109"
      }
    }
  },
  "claims": {
    "lf-signup": {"text": "Email/password and public signup default on; AUTH_DISABLE_SIGNUP=true also prevents invite acceptance by new users.", "components": ["langfuse"], "sources": ["langfuse:s34b0fb076e86"], "status": "REASONED"},
    "lf-bootstrap": {"text": "Create first account before closing signup, or initialize org before headless user/project with LANGFUSE_INIT_*.", "components": ["langfuse"], "sources": ["langfuse:scd1d81693f96", "langfuse:s34b0fb076e86"], "status": "REASONED"},
    "lf-sso": {"text": "AUTH_DISABLE_USERNAME_PASSWORD=true requires SSO; supported Auth.js providers need correct NEXTAUTH_URL beyond password login.", "components": ["langfuse"], "sources": ["langfuse:s34b0fb076e86"], "status": "REASONED"},
    "lf-session": {"text": "AUTH_SESSION_MAX_AGE must be integer >5 minutes; source default is 20160, while documentation says 43200; check pinned release.", "components": ["lf-session", "langfuse"], "sources": ["lf-session:s01522120437c", "langfuse:s34b0fb076e86"], "status": "REASONED"},
    "lf-api": {"text": "Ingestion/public API use project public-key username and secret-key password via Basic auth, separately from UI credentials.", "components": ["langfuse"], "sources": ["langfuse:sfdfc0ea9fdc1"], "status": "REASONED"},
    "lf-mfa": {"text": "Langfuse login has no native MFA; enforce it at the identity provider.", "components": ["langfuse"], "sources": ["langfuse:s34b0fb076e86"], "status": "REASONED"},
    "lf-session-secret": {"text": "Replace shipped NEXTAUTH_SECRET=mysecret before first start; known session protection secret permits forged sessions bypassing sign-in controls.", "components": ["langfuse", "lf-compose"], "sources": ["langfuse:sb92c8a6aaad1", "lf-compose:s4d19a7b83526"], "status": "REASONED"},
    "lf-salt": {"text": "Replace shipped SALT=mysalt used for API-key hashes with a separate random value.", "components": ["langfuse", "lf-compose"], "sources": ["langfuse:sb92c8a6aaad1", "lf-compose:s4d19a7b83526"], "status": "REASONED"},
    "lf-encryption": {"text": "Replace all-zero ENCRYPTION_KEY with 32 random hex bytes; later changes need re-encryption and exposed provider credentials need rotation.", "components": ["langfuse", "lf-compose"], "sources": ["langfuse:sb92c8a6aaad1", "lf-compose:s4d19a7b83526"], "status": "REASONED"},
    "lf-minio": {"text": "Rotate bundled minio/miniosecret and matching LANGFUSE_S3_* keys; MinIO S3 host 9090 is wildcard-published.", "components": ["lf-compose", "langfuse"], "sources": ["lf-compose:s4d19a7b83526", "langfuse:sb92c8a6aaad1"], "status": "REASONED"},
    "lf-ports": {"text": "langfuse-web host 3000 is wildcard-published; bundled Postgres, ClickHouse and Redis default loopback; keep all publications private.", "components": ["lf-compose"], "sources": ["lf-compose:s4d19a7b83526"], "status": "REASONED"},
    "lf-tls": {"text": "Container deployment needs proxy TLS; an HTTPS public URL does not establish native Langfuse TLS.", "components": ["langfuse"], "sources": ["langfuse:sb92c8a6aaad1"], "status": "REASONED"},
    "phoenix-enable": {"text": "Phoenix auth defaults disabled; enable PHOENIX_ENABLE_AUTH=True with random PHOENIX_SECRET.", "components": ["phoenix"], "sources": ["phoenix:s5a90699b7950"], "status": "REASONED"},
    "phoenix-admin": {"text": "Auth creates admin@localhost/admin unless first-account startup sets PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD; later environment changes are inert.", "components": ["phoenix"], "sources": ["phoenix:s5a90699b7950"], "status": "REASONED"},
    "phoenix-password": {"text": "Existing admin needs UI password replacement before exposure; remove the inert initial-password variable afterwards.", "components": ["phoenix"], "sources": ["phoenix:s5a90699b7950"], "status": "REASONED"},
    "phoenix-http": {"text": "HTTP UI/REST/OTLP defaults to 0.0.0.0:6006; restrict its bind/publication and backing database exposure.", "components": ["phoenix-bind", "phoenix"], "sources": ["phoenix-bind:s19ffeb67866e", "phoenix:s5a90699b7950"], "status": "REASONED"},
    "phoenix-grpc": {"text": "Separate OTLP gRPC defaults to [::]:4317 independently of PHOENIX_HOST; isolate namespace/publication/firewall separately.", "components": ["phoenix-bind"], "sources": ["phoenix-bind:s19ffeb67866e", "phoenix-bind:sfc104ed5254a"], "status": "REASONED"},
    "phoenix-keys": {"text": "Enabling auth blocks collection/API access until system or user API keys exist; PHOENIX_API_KEY is sent as Bearer.", "components": ["phoenix"], "sources": ["phoenix:s5a90699b7950"], "status": "REASONED"},
    "phoenix-mfa": {"text": "No native MFA; federate OAuth2/OIDC or use identity-aware ingress and enforce MFA there.", "components": ["phoenix"], "sources": ["phoenix:s5a90699b7950"], "status": "REASONED"},
    "phoenix-signup": {"text": "PHOENIX_OAUTH2_<IDP>_ALLOW_SIGN_UP defaults True; set False and restrict provider membership.", "components": ["phoenix"], "sources": ["phoenix:s5a90699b7950"], "status": "REASONED"},
    "phoenix-basic": {"text": "Local password login remains beside SSO; PHOENIX_DISABLE_BASIC_AUTH=True closes it after an approved IdP administrator is tested.", "components": ["phoenix"], "sources": ["phoenix:s5a90699b7950"], "status": "REASONED"},
    "phoenix-tls": {"text": "Native HTTP/gRPC TLS exists from 8.29, defaults off, uses certificate/key files; later per-protocol switches override PHOENIX_TLS_ENABLED.", "components": ["phoenix-tls-min", "phoenix-tls"], "sources": ["phoenix-tls-min:s8af9d57a7636", "phoenix-tls:s33e12a73fb58"], "status": "REASONED"},
    "helicone-login": {"text": "Better Auth uses signup and organizations; test@helicone.ai/password is a local manual trial, not the deployment security model.", "components": ["helicone"], "sources": ["helicone:s48d6e38bf1fa", "helicone:sac4298a08e00"], "status": "REASONED"},
    "helicone-secret": {"text": "Replace BETTER_AUTH_SECRET examples change-me-in-production and Compose your-secret-key before first start.", "components": ["helicone", "helicone-compose"], "sources": ["helicone:sac4298a08e00", "helicone-compose:s05ca7cfb09fe"], "status": "REASONED"},
    "helicone-ports": {"text": "Backing Postgres/ClickHouse/MinIO/Redis/MailHog publications bypass UI login, including 54388:5432 and 18123:8123; remove or loopback-scope them.", "components": ["helicone-compose"], "sources": ["helicone-compose:s05ca7cfb09fe"], "status": "REASONED"},
    "helicone-boundary": {"text": "Restrict signup, protect dashboard/Jawn/S3 and gateway separately with private networking or authenticated ingress and MFA; rotate example storage credentials.", "components": ["helicone", "helicone-compose"], "sources": ["helicone:sac4298a08e00", "helicone-compose:s05ca7cfb09fe"], "status": "REASONED"},
    "helicone-ingest": {"text": "AI Gateway ingestion and provider environment keys are separate from web sessions; protect those secrets.", "components": ["helicone"], "sources": ["helicone:sac4298a08e00"], "status": "REASONED"},
    "otel-default": {"text": "OTLP factory defaults localhost:4317 gRPC and localhost:4318 HTTP at v0.161.0; bind every enabled receiver explicitly.", "components": ["otel", "otel-docs"], "sources": ["otel:s6eb17ad3eb47", "otel-docs:s5fc11440844b"], "status": "REASONED"},
    "otel-history": {"text": "OTLP localhost transition was v0.104.0; UseLocalHostAsDefaultHost stabilized v0.110.0 and was removed v0.112.0.", "components": ["otel"], "sources": ["otel:s3252b8ba9775", "otel:s5a13f52d7e6d", "otel:sb419d6444c19"], "status": "REASONED"},
    "otel-shipped": {"text": "Both shipped configs override component defaults with unauthenticated IPv4 wildcard OTLP 4317/4318, Jaeger 14250/6832/6831/14268 and Zipkin 9411.", "components": ["otel-dist"], "sources": ["otel-dist:s08ca284a6d6f", "otel-dist:s9d2ef3c6b75d"], "status": "REASONED"},
    "otel-diagnostics": {"text": "Shipped pprof 1777 and zPages 55679 are wildcard and unauthenticated; remove from extensions/service.extensions or restrict separately.", "components": ["otel-dist", "otel", "pprof"], "sources": ["otel-dist:s08ca284a6d6f", "otel-dist:s9d2ef3c6b75d", "otel:se93854d097ec", "otel:s6957342b0bf4", "otel:sdac173d533e6", "pprof:s3f2efc571022"], "status": "REASONED"},
    "otel-images": {"text": "Dockerfiles COPY/select shipped config; EXPOSE 4317/4318/55679 is not host publication, but container peers may reach wildcard listeners.", "components": ["otel-dist"], "sources": ["otel-dist:s7a517873f7be", "otel-dist:sc806e2cc23e6"], "status": "REASONED"},
    "otel-packages": {"text": "Systemd reads distribution otelcol.conf; OTELCOL_OPTIONS selects config.yaml; config|noreplace installation can retain local config, and postinstall manages service.", "components": ["otel-dist"], "sources": ["otel-dist:s96832924ecbd", "otel-dist:s3cf497a4401c", "otel-dist:s532d68e28e68", "otel-dist:saa59feb48156", "otel-dist:s73f6337cd50e", "otel-dist:sff25af5f7a79", "otel-dist:sd829f5067d73", "otel-dist:secd03f9c13d6", "otel-dist:s353fc01c0b2c", "otel-dist:s72fc7a0602d1"], "status": "REASONED"},
    "otel-tls": {"text": "Require TLS on receivers/exporters and authentication on every receiver protocol accepting off-host data.", "components": ["otel-docs"], "sources": ["otel-docs:s5fc11440844b"], "status": "REASONED"},
    "otel-auth": {"text": "Declare authenticator, start it in service.extensions, and attach each receiver protocol with auth.authenticator; Basic supports htpasswd/client_auth.", "components": ["otel-docs", "basicauth"], "sources": ["otel-docs:s5fc11440844b", "basicauth:s473397b3887e"], "status": "REASONED"},
    "otel-bearer": {"text": "bearertokenauth accepts static or file-backed Authorization tokens; the guide cites general security guidance, not a pinned extension reference.", "components": ["otel-docs"], "sources": ["otel-docs:s5fc11440844b"], "status": "REASONED"},
    "otel-metrics": {"text": "Internal metrics factory defaults localhost:8888; shipped configs set 127.0.0.1:8888; 0.0.0.0:8888 scrape target is outbound.", "components": ["otel", "otel-dist"], "sources": ["otel:s9780bf233e75", "otel-dist:s08ca284a6d6f", "otel-dist:s9d2ef3c6b75d"], "status": "REASONED"},
    "otel-health": {"text": "Review enabled health-check 13133 independently of receiver authentication.", "components": ["health", "otel-dist"], "sources": ["health:s6ac60517accc", "otel-dist:s08ca284a6d6f", "otel-dist:s9d2ef3c6b75d"], "status": "REASONED"},
    "otel-k8s": {"text": "otelcol-k8s Dockerfile supplies no default config COPY/CMD; EXPOSE alone establishes no listener; Helm/operator are out of scope.", "components": ["otel-dist"], "sources": ["otel-dist:sb93573df35e2"], "status": "REASONED"},
    "otel-minimal": {"text": "Run only required components and use a non-root process.", "components": ["otel-docs"], "sources": ["otel-docs:s5fc11440844b"], "status": "REASONED"},
    "verify-inventory": {"text": "Inspect effective config, namespace TCP/UDP, publications and firewall; shipped wildcard listeners should become intended private listeners; outside failures need positive controls.", "components": ["otel-dist", "otel-docs", "phoenix-bind"], "sources": ["otel-dist:s08ca284a6d6f", "otel-dist:s9d2ef3c6b75d", "otel-docs:s5fc11440844b", "phoenix-bind:s19ffeb67866e", "phoenix-bind:sfc104ed5254a"], "status": "REASONED", "verify": [1]},
    "verify-dashboard": {"text": "Langfuse curl is reachability only; fresh unauthenticated browser must show login rather than project data.", "components": ["langfuse"], "sources": ["langfuse:s34b0fb076e86"], "status": "REASONED", "verify": [1]},
    "verify-lf-api": {"text": "Direct /api/public/projects pair should yield 401 without key and 200 with expected project ID; proxy-only results cannot prove native auth.", "components": ["langfuse"], "sources": ["langfuse:sfdfc0ea9fdc1"], "status": "REASONED", "verify": [1]},
    "verify-collector": {"text": "Direct OTLP/HTTP JSON /v1/traces should reject anonymous 401/403 and admit configured auth 2xx; wrong content type and failed connections are inconclusive.", "components": ["otel-docs", "basicauth"], "sources": ["otel-docs:s5fc11440844b", "basicauth:s473397b3887e"], "status": "REASONED", "verify": [1]},
    "verify-phoenix-admin": {"text": "Default admin/admin must fail with replacement password succeeding; with basic auth disabled, require local-login refusal and approved MFA IdP success.", "components": ["phoenix"], "sources": ["phoenix:s5a90699b7950"], "status": "REASONED"},
    "verify-phoenix-read": {"text": "Anonymous /v1/projects should reject 401/403, versus exposed project data 2xx; 404, redirect, 415 and transport errors are inconclusive.", "components": ["phoenix", "curl"], "sources": ["phoenix:s5a90699b7950", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [2]},
    "verify-phoenix-http": {"text": "Empty protobuf POST /v1/traces on 6006 tests admission, not persistence: anonymous rejects, write-authorized key admits, viewer key is not a positive control.", "components": ["phoenix", "phoenix-auth"], "sources": ["phoenix:s5a90699b7950", "phoenix-auth:sdbf548dbb448"], "status": "REASONED"},
    "verify-phoenix-grpc": {"text": "Separate empty gRPC TraceService/Export requires UNAUTHENTICATED without key, OK with write key; auth-off anonymous OK and viewer PERMISSION_DENIED remain source-reasoned.", "components": ["phoenix-auth", "phoenix-bind"], "sources": ["phoenix-auth:sdbf548dbb448", "phoenix-bind:sfc104ed5254a"], "status": "REASONED"}
  }
}
---
# LLM tracing and observability: Langfuse, Phoenix, Helicone, OpenTelemetry Collector

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| lf-signup: Email/password and public signup default on; AUTH_DISABLE_SIGNUP=true also prevents invite acceptance by new users. | Langfuse documentation unknown | REASONED |
| lf-bootstrap: Create first account before closing signup, or initialize org before headless user/project with LANGFUSE_INIT_*. | Langfuse documentation unknown | REASONED |
| lf-sso: AUTH_DISABLE_USERNAME_PASSWORD=true requires SSO; supported Auth.js providers need correct NEXTAUTH_URL beyond password login. | Langfuse documentation unknown | REASONED |
| lf-session: AUTH_SESSION_MAX_AGE must be integer &gt;5 minutes; source default is 20160, while documentation says 43200; check pinned release. | Langfuse session source 24c949d8dd5617219a8415f80e4c65ad611ff05c; Langfuse documentation unknown | REASONED |
| lf-api: Ingestion/public API use project public-key username and secret-key password via Basic auth, separately from UI credentials. | Langfuse documentation unknown | REASONED |
| lf-mfa: Langfuse login has no native MFA; enforce it at the identity provider. | Langfuse documentation unknown | REASONED |
| lf-session-secret: Replace shipped NEXTAUTH_SECRET=mysecret before first start; known session protection secret permits forged sessions bypassing sign-in controls. | Langfuse documentation unknown; Langfuse Compose 0dd0a7fbe2feb300b8776f02b3684eeee3fbceab | REASONED |
| lf-salt: Replace shipped SALT=mysalt used for API-key hashes with a separate random value. | Langfuse documentation unknown; Langfuse Compose 0dd0a7fbe2feb300b8776f02b3684eeee3fbceab | REASONED |
| lf-encryption: Replace all-zero ENCRYPTION_KEY with 32 random hex bytes; later changes need re-encryption and exposed provider credentials need rotation. | Langfuse documentation unknown; Langfuse Compose 0dd0a7fbe2feb300b8776f02b3684eeee3fbceab | REASONED |
| lf-minio: Rotate bundled minio/miniosecret and matching LANGFUSE_S3_* keys; MinIO S3 host 9090 is wildcard-published. | Langfuse Compose 0dd0a7fbe2feb300b8776f02b3684eeee3fbceab; Langfuse documentation unknown | REASONED |
| lf-ports: langfuse-web host 3000 is wildcard-published; bundled Postgres, ClickHouse and Redis default loopback; keep all publications private. | Langfuse Compose 0dd0a7fbe2feb300b8776f02b3684eeee3fbceab | REASONED |
| lf-tls: Container deployment needs proxy TLS; an HTTPS public URL does not establish native Langfuse TLS. | Langfuse documentation unknown | REASONED |
| phoenix-enable: Phoenix auth defaults disabled; enable PHOENIX_ENABLE_AUTH=True with random PHOENIX_SECRET. | Phoenix documentation unknown | REASONED |
| phoenix-admin: Auth creates admin@localhost/admin unless first-account startup sets PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD; later environment changes are inert. | Phoenix documentation unknown | REASONED |
| phoenix-password: Existing admin needs UI password replacement before exposure; remove the inert initial-password variable afterwards. | Phoenix documentation unknown | REASONED |
| phoenix-http: HTTP UI/REST/OTLP defaults to 0.0.0.0:6006; restrict its bind/publication and backing database exposure. | Phoenix listener source arize-phoenix-v20.16.0; Phoenix documentation unknown | REASONED |
| phoenix-grpc: Separate OTLP gRPC defaults to [::]:4317 independently of PHOENIX_HOST; isolate namespace/publication/firewall separately. | Phoenix listener source arize-phoenix-v20.16.0 | REASONED |
| phoenix-keys: Enabling auth blocks collection/API access until system or user API keys exist; PHOENIX_API_KEY is sent as Bearer. | Phoenix documentation unknown | REASONED |
| phoenix-mfa: No native MFA; federate OAuth2/OIDC or use identity-aware ingress and enforce MFA there. | Phoenix documentation unknown | REASONED |
| phoenix-signup: PHOENIX_OAUTH2_&lt;IDP&gt;_ALLOW_SIGN_UP defaults True; set False and restrict provider membership. | Phoenix documentation unknown | REASONED |
| phoenix-basic: Local password login remains beside SSO; PHOENIX_DISABLE_BASIC_AUTH=True closes it after an approved IdP administrator is tested. | Phoenix documentation unknown | REASONED |
| phoenix-tls: Native HTTP/gRPC TLS exists from 8.29, defaults off, uses certificate/key files; later per-protocol switches override PHOENIX_TLS_ENABLED. | Phoenix TLS minimum 8.29; Phoenix TLS source 080959576563900038688ddf01f3bee110005df5 | REASONED |
| helicone-login: Better Auth uses signup and organizations; test@helicone.ai/password is a local manual trial, not the deployment security model. | Helicone documentation unknown | REASONED |
| helicone-secret: Replace BETTER_AUTH_SECRET examples change-me-in-production and Compose your-secret-key before first start. | Helicone documentation unknown; Helicone Compose b12ebaccb824ab9778757ca197ff302d97fda421 | REASONED |
| helicone-ports: Backing Postgres/ClickHouse/MinIO/Redis/MailHog publications bypass UI login, including 54388:5432 and 18123:8123; remove or loopback-scope them. | Helicone Compose b12ebaccb824ab9778757ca197ff302d97fda421 | REASONED |
| helicone-boundary: Restrict signup, protect dashboard/Jawn/S3 and gateway separately with private networking or authenticated ingress and MFA; rotate example storage credentials. | Helicone documentation unknown; Helicone Compose b12ebaccb824ab9778757ca197ff302d97fda421 | REASONED |
| helicone-ingest: AI Gateway ingestion and provider environment keys are separate from web sessions; protect those secrets. | Helicone documentation unknown | REASONED |
| otel-default: OTLP factory defaults localhost:4317 gRPC and localhost:4318 HTTP at v0.161.0; bind every enabled receiver explicitly. | OpenTelemetry Collector v0.161.0; Collector security guidance unknown | REASONED |
| otel-history: OTLP localhost transition was v0.104.0; UseLocalHostAsDefaultHost stabilized v0.110.0 and was removed v0.112.0. | OpenTelemetry Collector v0.161.0 | REASONED |
| otel-shipped: Both shipped configs override component defaults with unauthenticated IPv4 wildcard OTLP 4317/4318, Jaeger 14250/6832/6831/14268 and Zipkin 9411. | Collector distributions v0.161.0 | REASONED |
| otel-diagnostics: Shipped pprof 1777 and zPages 55679 are wildcard and unauthenticated; remove from extensions/service.extensions or restrict separately. | Collector distributions v0.161.0; OpenTelemetry Collector v0.161.0; Collector pprof source 443567a6a00d7cff8cae1432a6fef655d8698e94 | REASONED |
| otel-images: Dockerfiles COPY/select shipped config; EXPOSE 4317/4318/55679 is not host publication, but container peers may reach wildcard listeners. | Collector distributions v0.161.0 | REASONED |
| otel-packages: Systemd reads distribution otelcol.conf; OTELCOL_OPTIONS selects config.yaml; config&#124;noreplace installation can retain local config, and postinstall manages service. | Collector distributions v0.161.0 | REASONED |
| otel-tls: Require TLS on receivers/exporters and authentication on every receiver protocol accepting off-host data. | Collector security guidance unknown | REASONED |
| otel-auth: Declare authenticator, start it in service.extensions, and attach each receiver protocol with auth.authenticator; Basic supports htpasswd/client_auth. | Collector security guidance unknown; Collector Basic auth extension 1c897ba9c67afc3c9e218b5cd05a6de49435f4de | REASONED |
| otel-bearer: bearertokenauth accepts static or file-backed Authorization tokens; the guide cites general security guidance, not a pinned extension reference. | Collector security guidance unknown | REASONED |
| otel-metrics: Internal metrics factory defaults localhost:8888; shipped configs set 127.0.0.1:8888; 0.0.0.0:8888 scrape target is outbound. | OpenTelemetry Collector v0.161.0; Collector distributions v0.161.0 | REASONED |
| otel-health: Review enabled health-check 13133 independently of receiver authentication. | Collector health source d922ffb299c6b9be026f97dd7d6a5f0f507efdeb; Collector distributions v0.161.0 | REASONED |
| otel-k8s: otelcol-k8s Dockerfile supplies no default config COPY/CMD; EXPOSE alone establishes no listener; Helm/operator are out of scope. | Collector distributions v0.161.0 | REASONED |
| otel-minimal: Run only required components and use a non-root process. | Collector security guidance unknown | REASONED |
| verify-inventory: Inspect effective config, namespace TCP/UDP, publications and firewall; shipped wildcard listeners should become intended private listeners; outside failures need positive controls. | Collector distributions v0.161.0; Collector security guidance unknown; Phoenix listener source arize-phoenix-v20.16.0 | REASONED |
| verify-dashboard: Langfuse curl is reachability only; fresh unauthenticated browser must show login rather than project data. | Langfuse documentation unknown | REASONED |
| verify-lf-api: Direct /api/public/projects pair should yield 401 without key and 200 with expected project ID; proxy-only results cannot prove native auth. | Langfuse documentation unknown | REASONED |
| verify-collector: Direct OTLP/HTTP JSON /v1/traces should reject anonymous 401/403 and admit configured auth 2xx; wrong content type and failed connections are inconclusive. | Collector security guidance unknown; Collector Basic auth extension 1c897ba9c67afc3c9e218b5cd05a6de49435f4de | REASONED |
| verify-phoenix-admin: Default admin/admin must fail with replacement password succeeding; with basic auth disabled, require local-login refusal and approved MFA IdP success. | Phoenix documentation unknown | REASONED |
| verify-phoenix-read: Anonymous /v1/projects should reject 401/403, versus exposed project data 2xx; 404, redirect, 415 and transport errors are inconclusive. | Phoenix documentation unknown; curl minimum 7.75.0 | REASONED |
| verify-phoenix-http: Empty protobuf POST /v1/traces on 6006 tests admission, not persistence: anonymous rejects, write-authorized key admits, viewer key is not a positive control. | Phoenix documentation unknown; Phoenix gRPC auth source f11c885c063f1c9b6146693cda401c5d645d8294 | REASONED |
| verify-phoenix-grpc: Separate empty gRPC TraceService/Export requires UNAUTHENTICATED without key, OK with write key; auth-off anonymous OK and viewer PERMISSION_DENIED remain source-reasoned. | Phoenix gRPC auth source f11c885c063f1c9b6146693cda401c5d645d8294; Phoenix listener source arize-phoenix-v20.16.0 | REASONED |
<!-- version-basis:end -->

These tools store full prompts, completions, and often the provider API keys used to generate them, so an
exposed dashboard leaks your most sensitive data at once. Several ship with authentication off or with open
signup enabled, so the default install is not safe to expose.

## Langfuse (self-hosted)

Email/password authentication is enabled by default: anyone who can reach the URL can register their own
account unless you turn signup off. Set `AUTH_DISABLE_SIGNUP=true` to block new registrations, including a
user accepting a project invite without an existing account; set `AUTH_DISABLE_USERNAME_PASSWORD=true` to
require SSO instead of a password entirely. Create the first account BEFORE you disable signup (or provision
it headlessly with `LANGFUSE_INIT_ORG_ID`, `LANGFUSE_INIT_USER_EMAIL`, and `LANGFUSE_INIT_USER_PASSWORD` -
a user or project cannot be initialized without also initializing an organization), or you lock yourself
out; then confirm a fresh registration is actually refused. SSO runs through Auth.js against Google, GitHub, GitLab, Azure
AD/Entra ID, Okta, Auth0, Keycloak, or a custom OIDC provider; `NEXTAUTH_URL` must be set correctly for any
method other than email/password. `AUTH_SESSION_MAX_AGE` sets the session lifetime in minutes, and must be an integer greater than five. The current implementation defaults it to 20160 (14 days); the documentation still says 43200 (30 days), so pin your release and check the value you actually get. The ingestion and public API are authenticated
separately from the UI session: a project's public key (username) and secret key (password) are sent as HTTP
Basic Auth, issued from Project Settings, and unrelated to a user's login credentials. Put MFA at the
identity provider per [mfa.md](mfa.md); Langfuse's own login has none.

Those controls all sit on the sign-in flow, and the self-hosting `docker-compose.yml` sits under them: it
ships example secrets marked `# CHANGEME`, and `NEXTAUTH_SECRET` protects the session token, which NextAuth
encrypts and authenticates, so the shipped `mysecret` lets anyone mint a session for any existing account,
administrators included, without the login flow and the SSO or MFA that only guard it. Disabling signup and
enforcing SSO do not help, because they gate account creation and sign-in, not a forged cookie. Two related
secrets ship the same way: `SALT` (`mysalt`) salts the stored API-key hashes, so a known salt speeds offline
cracking of keys lifted from the database; and `ENCRYPTION_KEY`, shipped as 64 hex zeros, encrypts the LLM
provider keys and integration credentials Langfuse stores, so anyone holding that key and a copy of the data
reads them in clear. Generate a fresh random value for each before the first start (`openssl rand -base64 32`
for `NEXTAUTH_SECRET` and `SALT`, `openssl rand -hex 32` for `ENCRYPTION_KEY`) and keep them out of the
repository ([secrets.md](secrets.md)); changing `ENCRYPTION_KEY` later needs a planned re-encryption, and if
the shipped key was ever live, treat the stored provider credentials as exposed and rotate them. The same
compose bundles a MinIO with the well-known `minio`/`miniosecret` login and publishes its S3 API on host port
`9090` on every interface by default, as it does langfuse-web on `3000`, while the bundled Postgres,
ClickHouse, and Redis default to loopback; change that login, update the matching `LANGFUSE_S3_*` access keys
Langfuse uses to reach MinIO, and keep every published port off untrusted networks ([minio.md](minio.md),
[object-storage.md](object-storage.md)).

## Arize Phoenix (self-hosted)

Authentication is disabled by default, "as you may be just trying Phoenix for the very first time or have
Phoenix deployed in a VPC" in the vendor's own words: anyone who reaches the UI has full read and write
access with no login at all. Set `PHOENIX_ENABLE_AUTH=True` and `PHOENIX_SECRET` (a long random value used to
sign session tokens) to turn it on.

Turning auth on is not enough. Phoenix creates an administrator account `admin@localhost` with the password
`admin`, so the flip alone leaves a reachable instance with a known admin login. `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD`
sets that password, but only on the startup that first creates the account: set it on a brand-new deployment,
before the first start. On any instance that has started before, the variable is inert, and setting it and
restarting changes nothing and reports no error, so never read "I set it and restarted" as proof the password
changed. It is read only on the first startup that creates the admin account; unless you are setting it on a
brand-new deployment's very first start, treat the account as already existing: log in at the UI as
`admin@localhost`, which prompts for a new password, then run the
default-credential check in Verify to prove `admin` is dead. Until that change lands, `admin`/`admin` is a live
admin login, so keep the instance off any untrusted network in the window between the flip and the change.
Once the account exists the variable only holds an admin password in plaintext for no effect; remove it from
your environment files.

Phoenix binds broadly by default: the HTTP UI/REST/OTLP server on `0.0.0.0:6006` and a SEPARATE gRPC OTLP
server on `[::]:4317` that does not follow the HTTP host setting (both as of Phoenix 20.16.0), and the vendor Compose also publishes its
PostgreSQL, so bind or publish both protocols deliberately and keep the database off host interfaces.

Enabling auth on a running instance stops trace collection and blocks all API access until API keys exist, so
mint a key immediately after the flip: a system key (admin-created, acts for the whole instance) or a user key
authenticates API requests via `PHOENIX_API_KEY` sent as an `Authorization: Bearer` header, and collectors and
SDKs need one to keep sending traces. Phoenix has no native MFA, but it can federate to an OAuth2/OIDC identity
provider (its documentation works through Google, AWS Cognito, and Microsoft Entra ID); enforce MFA there, or
add an identity-aware proxy in front per [mfa.md](mfa.md). Two OAuth caveats: `PHOENIX_OAUTH2_<IDP>_ALLOW_SIGN_UP`
defaults to `True`, so any identity the provider will authenticate can provision itself an account unless you
set it `False` and restrict provider membership (test an unapproved identity); and local email/password login
stays available alongside SSO and bypasses the provider's MFA, so set `PHOENIX_DISABLE_BASIC_AUTH=True` once
the IdP is the intended path. Establish and test an approved IdP administrator BEFORE you disable local login
or provider signup: disabling basic auth also disables the local admin password, so once
`PHOENIX_DISABLE_BASIC_AUTH=True` the "replacement admin password works" control in Verify no longer applies -
instead require local password login to FAIL and an approved IdP login with MFA to succeed.

## Helicone (self-hosted)

Helicone self-hosts with Better Auth: account signup and organization membership, not a fixed shared login
(the `test@helicone.ai` / `password` credential is the manual guide's local trial only). Generate a real
`BETTER_AUTH_SECRET` before the first start: the all-in-one image documents the placeholder
`change-me-in-production` and the repository Compose file falls back to `your-secret-key`, and a known
signing secret weakens every session token it protects, so replace whichever example value your deployment
uses. Then restrict who may sign up, and do not expose the dashboard without
your own layer in front. Helicone is several services, not one: its Docker Compose publishes the backing
stores - PostgreSQL, ClickHouse, MinIO/S3, Redis, and MailHog - on host ports independent of the dashboard
login (for example `54388:5432` and `18123:8123`), so an identity proxy on the UI leaves those wide open;
remove or loopback-scope every backing publication and rotate the example storage credentials
([minio.md](minio.md), [object-storage.md](object-storage.md)). Ingestion runs through the separate AI Gateway
and the provider keys in its environment, not the web session; store those per [secrets.md](secrets.md). The
Jawn service and the S3 store also hold your data, so protect every service, not just the dashboard and
gateway: keep them all on a private network or behind an identity-aware fronting layer
([fronting-auth.md](fronting-auth.md), [nginx.md](nginx.md), [caddy.md](caddy.md)) with MFA ([mfa.md](mfa.md)).

## OpenTelemetry Collector

The Collector is the pipe these tools (and others) receive traces through, and it ships with no security
applied until you configure it. Bind receivers to a specific interface or loopback (for example
`127.0.0.1:4317`). The OTLP receiver's default host became `localhost` in v0.104.0; the
`component.UseLocalHostAsDefaultHost` feature gate was stabilized in v0.110.0 and removed in v0.112.0.
At v0.161.0, the OTLP factory sets `localhost:4317` (gRPC) and `localhost:4318` (HTTP) directly.

**The official `otelcol` and `otelcol-contrib` images and deb/rpm packages ship a configuration that
overrides those localhost component defaults.** At v0.161.0, both enable wildcard IPv4 listeners on
`0.0.0.0`: OTLP `4317`/`4318`, Jaeger `14250`/`6832`/`6831`/`14268`, Zipkin `9411`, and
the diagnostic extensions pprof `1777` and zPages `55679`, with no authentication configured.
Their first-line comment tells users to narrow the endpoints, but the shipped values still bind every
IPv4 interface. Each Dockerfile copies that config and selects it in the default `CMD`; it declares
`EXPOSE 4317 4318 55679`. `EXPOSE` does not publish ports, and `docker run -p` publishes only the
mappings you request; the in-container wildcard listeners can still be reachable by container peers.
Inventory network paths as well as host publications.

For packages, the systemd unit reads `/etc/otelcol/otelcol.conf` or
`/etc/otelcol-contrib/otelcol-contrib.conf`; its `OTELCOL_OPTIONS` selects the matching
`/etc/otelcol/config.yaml` or `/etc/otelcol-contrib/config.yaml`. The package recipe installs the
same shipped config with `config|noreplace` handling; the postinstall scripts manage the service,
rather than copying the config. Existing local configuration can therefore differ.

Supply your own configuration with explicit endpoints for every enabled listener. Remove pprof and
zPages from both `extensions` and `service.extensions` unless needed; if retained, bind them privately
and control access separately from receiver authentication. Widen a receiver's bind only where the
intended clients, proxy, or mesh need it; require TLS on every receiver and exporter; and attach an authenticator
extension, such as `basicauth` (htpasswd-style credentials, or a static `client_auth` username/password for
outgoing calls) or `bearertokenauth` (a static or file-backed token sent as an `Authorization` header), to any
receiver that accepts data from outside the host. Declaring an authenticator extension is not enough to enforce it: list it under `service.extensions` so it
starts, then attach it to EACH receiver protocol with an `auth.authenticator` key naming the extension.
Inventory the other listeners too. At v0.161.0, the internal telemetry metrics factory defaults to
`localhost:8888`; the two shipped configs explicitly use `127.0.0.1:8888`. Their
`0.0.0.0:8888` Prometheus scrape target is an outbound destination, not a listener setting.
The enabled health-check extension (`13133`) also needs review independently of receiver authentication.
The `otelcol-k8s` Dockerfile at this tag copies no default config and supplies no default config
`CMD`; its `EXPOSE` list alone establishes no running listeners. Helm chart and operator configuration
are out of scope here.
Build or run only the receivers, processors, and exporters you use, since every enabled component is attack
surface, and run the process as a non-root user.

Langfuse's container deployment does not terminate TLS, so an `https://` URL in front of it is your proxy's,
not Langfuse's. Phoenix (8.29 and later) CAN terminate TLS natively for both HTTP and gRPC - set
`PHOENIX_TLS_ENABLED=True` (it defaults to `False`) with `PHOENIX_TLS_CERT_FILE` and `PHOENIX_TLS_KEY_FILE` -
so its default is TLS off, not TLS unsupported. Later versions add per-protocol overrides
(`PHOENIX_TLS_ENABLED_FOR_HTTP` and `PHOENIX_TLS_ENABLED_FOR_GRPC`, each overriding `PHOENIX_TLS_ENABLED` for
its protocol); check your release. Either way terminate TLS deliberately (natively, or at a reverse proxy or tunnel
per [nginx.md](nginx.md), [caddy.md](caddy.md)), and make sure any plaintext backend port a proxy forwards
to is not separately reachable.

## Verify

Collector live checks remain **REASONED**: the authoring host forbids opening listeners without an
isolated network namespace, and has none. Expected outcomes follow the cited pinned Collector configuration. Inspect the
effective config and inventory TCP and UDP sockets in the Collector's network namespace, together
with container publications and firewall rules. With the shipped config, expect the nine wildcard
endpoints listed above, including unauthenticated pprof and zPages. With your replacement config,
expect only the intended private binds and no pprof or zPages listener if removed. Test reachability
from an untrusted network and use an authorized client as a positive control; a failed connection
alone does not prove authentication. No exposed-versus-fixed Collector run was performed here.

```bash
# REASONED: these checks follow the cited vendor documentation and source readings, not live results.
# The authoring environment has no running Langfuse,
# Phoenix, Helicone, or OpenTelemetry Collector deployment to probe, so the shell syntax and the guard
# branches were tested locally but the exposed-vs-fixed service responses were not.
# ss is a listener inventory in THIS namespace - not a firewall, NAT, or authentication check.
ss -tlnp   # inventory 3000/6006/4317/4318 and identify each listener's namespace, host publication, and
           # permitted network paths. A wildcard bind is not itself exposure (Phoenix's gRPC 4317 always
           # binds [::] regardless of PHOENIX_HOST) and a port here can still be published by DNAT, so
           # confirm the actual container publications and firewall, and probe the public IPv4/IPv6 path
           # from another host - this list alone proves neither exposure nor authentication
# Langfuse dashboard: a bare GET of / cannot tell a login page from an exposed project view (both are 200
# and the body is discarded), so confirm it in a FRESH browser session - an unauthenticated visit must
# land on login, not a project. The curl below is only transport reachability.
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -g -sS -L --proto-redir '=https' --noproxy '*' --connect-timeout 5 --max-time 15 \
  -o /dev/null -w 'dashboard final=%{http_code} url=%{url_effective} exit=%{exitcode}\n' https://langfuse.example.com/
# Langfuse public API auth, matched pair: WITHOUT the key expect 401; WITH a valid project key (public:secret)
# expect 200 whose JSON body carries the EXPECTED project id - the positive control. A 401/200 pair seen
# THROUGH a reverse proxy does not prove Langfuse itself authenticated (a proxy can reject anonymous and
# admit authenticated while its backend stays open), so repeat the pair DIRECTLY against the Langfuse
# listener from an authorized network position, keeping any proxy credentials constant, and separately
# confirm untrusted clients cannot reach that backend. The key reaches curl on stdin via a config file (curl --config -), so it stays out
# of argv and /proc/<pid>/cmdline; still prefer a short-lived project key.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  # The secret key you substitute on the set -- line enters shell history.
  # Use a short-lived project key or clear that history line afterward.
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_PUBLIC_KEY' 'REPLACE_WITH_SECRET_KEY'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the public key on the set -- line above; not probing"; exit ;; esac
  case "$2" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the secret key on the set -- line above; not probing"; exit ;; esac
  set -- "${1//\\/\\\\}" "${2//\\/\\\\}"
  set -- "${1//\"/\\\"}" "${2//\"/\\\"}"
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 15 -o /dev/null \
    -w 'projects no-key=%{http_code} exit=%{exitcode}\n' https://langfuse.example.com/api/public/projects
  printf 'user = "%s:%s"\n' "$1" "$2" | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 15 \
    -w '\nprojects with-key=%{http_code} exit=%{exitcode}\n' --config - https://langfuse.example.com/api/public/projects
)
# Collector OTLP/HTTP, matched pair: WITHOUT the configured auth header expect 401/403; then repeat WITH it
# (add -H 'Authorization: Bearer <token>', or -u user:pass for basicauth) and expect a 2xx - the positive
# control. Run the pair DIRECTLY against the receiver to establish RECEIVER authentication (a proxy can
# answer 401/2xx while the receiver is open), and test the public ingress separately. Keep the JSON content
# type (a wrong content type draws a 415 that is not an authentication result). This tests this OTLP/HTTP
# receiver only; test each enabled OTLP/gRPC receiver separately, and note the Phoenix check further below
# targets a DIFFERENT server, not this Collector.
# guard-conventions: allow probe of an illustrative internal host; no reader-substituted placeholder in this probe's argv
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 15 -o /dev/null \
  -w 'otlp no-auth=%{http_code} exit=%{exitcode}\n' -H 'Content-Type: application/json' -d '{"resourceSpans":[]}' \
  https://otel-collector.internal:4318/v1/traces
```

For Phoenix specifically, prove the default admin credential is dead and that the read API does not answer an
anonymous request. **These checks are REASONED from the cited Phoenix documentation and source, not demonstrated** (no Phoenix instance in the authoring
environment). The credential
check is manual, because the vendor documents only the UI login flow and a scripted guess against the wrong
endpoint can read a `404` as a rejection: in a fresh browser session with no saved Phoenix cookies, try once
to log in as `admin@localhost` with the password `admin`. **Exposed:** it logs in. **Fixed:** it is rejected,
and your replacement admin password works in a second fresh session (or, if you set
`PHOENIX_DISABLE_BASIC_AUTH=True`, local password login is refused entirely and an approved IdP login with
MFA succeeds instead). Then, from a network position that
legitimately reaches Phoenix (a connection failure proves nothing about authentication), probe the read API
anonymously (the probe prints the `exitcode` and `errormsg` write-out variables, which need curl 7.75.0 or newer):

```bash
# REASONED: Phoenix read-API authentication follows the cited documentation and source; no Phoenix instance is available.
(                              # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PHOENIX_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the host on the set -- line above; not probing"; exit 1 ;;
    *) curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 "https://$1/v1/projects" \
         -w '\n[unauth-read] http=%{http_code} exit=%{exitcode} err=%{errormsg}\n'
       ;;
  esac
)
```

**Exposed:** `/v1/projects` returns project data with no credential (a `2xx`). **Fixed:** the anonymous request
is rejected with `401` or `403`. Anything else (a `404`, a redirect to a login page, a `415`, or a transport
error) is inconclusive and does not prove authentication is on; fall back to the credential check above and to
the listener inventory. Substitute a bracketed literal for an IPv6 host in the URL, for example `[::1]:6006`.

The OTLP/HTTP ingestion path CAN be probed without hand-encoding a span: an empty `ExportTraceServiceRequest`
is a zero-length protobuf body, so send `--data-binary ''` with `Content-Type: application/x-protobuf` to
`/v1/traces` on the HTTP port (6006) and read the status - anonymously it must be rejected (401/403), and
with a WRITE-authorized `Authorization: Bearer` key (a system key, or a user key allowed to write traces,
NOT a viewer key) it is admitted (a 2xx). This tests request ADMISSION, not span
persistence, and a valid VIEWER-role key is not a positive control here: Phoenix authenticates a viewer but
rejects a viewer token for OTLP writes with `PERMISSION_DENIED`, so admit only with a system key or a
write-authorized user key. The gRPC OTLP receiver on 4317 is a SEPARATE server with its own
`ApiKeyInterceptor`, not the HTTP `/v1` router, so a protected HTTP path does not prove the gRPC path is
protected: test 4317 separately by invoking `opentelemetry.proto.collector.trace.v1.TraceService/Export`
with an empty `ExportTraceServiceRequest`, first with no metadata (expect `UNAUTHENTICATED`) then with
`authorization: Bearer <write-authorized key>` (expect `OK`). That needs an OTLP gRPC client carrying the
protobuf descriptor (and the CA if TLS is on), so it ships REASONED: with authentication
disabled the same anonymous empty Export returns `OK` (the exposed outcome), and the authenticated,
viewer-rejected, and empty-request behaviours follow Phoenix's gRPC Export handler and `ApiKeyInterceptor`
(see Sources). Because Phoenix's gRPC listener always binds `[::]` regardless of `PHOENIX_HOST`, you cannot
move it to loopback by host
setting: isolate it in a private container network, restrict or omit its host publication, and inspect its
namespace, publications, and firewall separately from the HTTP port. A wildcard listener inside an isolated
namespace is not by itself public exposure.

A dashboard that renders traces, prompts, or provider keys without a login is a finding; so is an OTLP port
that accepts spans with no credential at all.

## Common mistakes

- Leaving Phoenix's or Helicone's auth off "because it's just internal" on a host with a public IP.
- Enabling `PHOENIX_ENABLE_AUTH` without creating an API key first, which locks out collectors mid-flight.
- Leaving Phoenix's default `admin@localhost` / `admin` in place after turning auth on, or trusting `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD` to have changed it on an instance whose admin account already existed, where the variable is silently inert.
- Publishing the OTLP gRPC/HTTP ports (4317/4318) to `0.0.0.0` because a docker-compose example did.
- Assuming an ingestion key protects the UI, or a UI login protects the ingestion endpoint; they are
  separate credentials in Langfuse and Phoenix alike.

## Sources (checked September 2026)

- Langfuse, authentication and SSO (signup default, `AUTH_DISABLE_SIGNUP`, `AUTH_DISABLE_USERNAME_PASSWORD`,
  SSO providers, `AUTH_SESSION_MAX_AGE`, `NEXTAUTH_URL`): https://langfuse.com/self-hosting/security/authentication-and-sso
- Langfuse, public API authentication (Basic Auth with project public/secret key): https://langfuse.com/docs/api-and-data-platform/features/public-api
- Langfuse, session-lifetime implementation (`AUTH_SESSION_MAX_AGE` validated as an integer greater than five, default `14 * 24 * 60` = 20160 minutes, vs the 43200 in the docs): https://github.com/langfuse/langfuse/blob/24c949d8dd5617219a8415f80e4c65ad611ff05c/web/src/env.mjs
- Langfuse, self-hosting configuration (`NEXTAUTH_SECRET`, `SALT`, `ENCRYPTION_KEY` and their generation, the bundled MinIO/Postgres/ClickHouse/Redis; checked 2026-09-14): https://langfuse.com/self-hosting/configuration
- Langfuse, self-hosting docker-compose.yml (the `# CHANGEME` example secrets `mysecret`/`mysalt`/all-zero `ENCRYPTION_KEY`, MinIO `minio`/`miniosecret` on host `9090`, langfuse-web on `3000`; checked 2026-09-14): https://github.com/langfuse/langfuse/blob/0dd0a7fbe2feb300b8776f02b3684eeee3fbceab/docker-compose.yml
- Arize Phoenix, authentication (`PHOENIX_ENABLE_AUTH`, `PHOENIX_SECRET`, system and user API keys, `PHOENIX_API_KEY`, the default `admin@localhost` / `admin` account, `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD` read only at first-account creation, `/v1/` REST permissions, OAuth2/OIDC identity providers, and the absence of native MFA; read 2026-09-13): https://arize.com/docs/phoenix/self-hosting/features/authentication
- Arize Phoenix, native HTTP and gRPC TLS introduced in 8.29 (2025-04-28): https://arize.com/docs/phoenix/release-notes/04-2025/04-28-2025-tls-support-for-phoenix-server
- Arize Phoenix, TLS configuration implementation (`PHOENIX_TLS_ENABLED` default `False`, `PHOENIX_TLS_CERT_FILE`/`PHOENIX_TLS_KEY_FILE`, and the per-protocol `PHOENIX_TLS_ENABLED_FOR_HTTP`/`PHOENIX_TLS_ENABLED_FOR_GRPC` overrides): https://github.com/Arize-ai/phoenix/blob/080959576563900038688ddf01f3bee110005df5/src/phoenix/config.py
- Helicone, self-hosted deployment (default `test@helicone.ai` / `password` login): https://docs.helicone.ai/getting-started/self-host/manual
- Helicone, all-in-one Docker deployment (Better Auth, `BETTER_AUTH_SECRET` documented default `change-me-in-production`): https://docs.helicone.ai/getting-started/self-host/docker
- Helicone, repository Compose deployment (`BETTER_AUTH_SECRET` fallback `your-secret-key`; backing stores published on host ports `54388:5432`, `18123:8123`, `19000:9000`, `9000`/`9001`, `6379`, `1025`/`8025`): https://github.com/Helicone/helicone/blob/b12ebaccb824ab9778757ca197ff302d97fda421/docker/docker-compose.yml
- Langfuse, headless initialization (`LANGFUSE_INIT_ORG_ID`/`USER_EMAIL`/`USER_PASSWORD`, org-before-user ordering): https://langfuse.com/self-hosting/administration/headless-initialization
- Arize Phoenix, OAuth2 sign-up and basic-auth controls (`PHOENIX_OAUTH2_<IDP>_ALLOW_SIGN_UP` default True, `PHOENIX_DISABLE_BASIC_AUTH`): https://arize.com/docs/phoenix/self-hosting/features/authentication
- OpenTelemetry Collector v0.161.0, OTLP factory endpoints: https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/receiver/otlpreceiver/factory.go#L41-L67
- OpenTelemetry Collector v0.161.0 changelog, v0.104.0 OTLP localhost transition: https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/CHANGELOG.md#L2058-L2070
- OpenTelemetry Collector v0.161.0 changelog, gate stabilization in v0.110.0 and removal in v0.112.0: https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/CHANGELOG.md#L1793-L1811 and https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/CHANGELOG.md#L1737-L1743
- OpenTelemetry Collector releases v0.161.0, shipped configs (wildcard endpoints, explicit loopback metrics, enabled pipelines and extensions): https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/config.yaml#L1-L81 and https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/config.yaml#L1-L81
- OpenTelemetry Collector releases v0.161.0, Docker config COPY, CMD and EXPOSE: https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/Dockerfile#L10-L15 and https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/Dockerfile#L10-L15
- OpenTelemetry Collector releases v0.161.0, deb/rpm config installation and script selection: https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/.goreleaser.yaml#L86-L118 and https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/.goreleaser.yaml#L94-L126
- OpenTelemetry Collector releases v0.161.0, systemd environment and command: https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/otelcol.service#L5-L7 and https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/otelcol-contrib.service#L5-L7
- OpenTelemetry Collector releases v0.161.0, package config arguments: https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/otelcol.conf#L1-L5 and https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/otelcol-contrib.conf#L1-L5
- OpenTelemetry Collector releases v0.161.0, deb postinstall service management: https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/postinstall.sh#L6-L16 and https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/postinstall.sh#L6-L16
- OpenTelemetry Collector releases v0.161.0, rpm postinstall service management: https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol/postinstall-rpm.sh#L6-L9 and https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-contrib/postinstall-rpm.sh#L6-L9
- OpenTelemetry Collector releases v0.161.0, otelcol-k8s Dockerfile (no config COPY or CMD): https://github.com/open-telemetry/opentelemetry-collector-releases/blob/v0.161.0/distributions/otelcol-k8s/Dockerfile#L1-L17
- OpenTelemetry, Collector security best practices (bind addresses, TLS, authenticator extensions, minimal
  components, non-root): https://opentelemetry.io/docs/security/config-best-practices/
- OpenTelemetry Collector Contrib, `basicauthextension` (htpasswd, `client_auth`, `auth.authenticator` wiring): https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/1c897ba9c67afc3c9e218b5cd05a6de49435f4de/extension/basicauthextension
- Arize Phoenix, gRPC OTLP Export authorization (`ApiKeyInterceptor`: `UNAUTHENTICATED` without a key, `PERMISSION_DENIED` for a viewer token, `OK` with a write-authorized key or when auth is disabled): https://github.com/Arize-ai/phoenix/blob/f11c885c063f1c9b6146693cda401c5d645d8294/src/phoenix/server/bearer_auth.py
- OpenTelemetry Collector v0.161.0, internal telemetry metrics default `localhost:8888`: https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/service/telemetry/otelconftelemetry/factory.go#L49-L64
- OpenTelemetry Collector v0.161.0, zPages default endpoint and HTTP server configuration: https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/extension/zpagesextension/factory.go#L15-L29
- OpenTelemetry Collector v0.161.0, zPages server wiring and optional HTTP authentication: https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/extension/zpagesextension/zpagesextension.go#L87-L105 and https://github.com/open-telemetry/opentelemetry-collector/blob/v0.161.0/config/confighttp/server.go#L352-L364
- OpenTelemetry Collector Contrib, pprof extension (default endpoint `localhost:1777`): https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/443567a6a00d7cff8cae1432a6fef655d8698e94/extension/pprofextension/README.md
- OpenTelemetry Collector Contrib, health-check extension (default endpoint `localhost:13133`): https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/d922ffb299c6b9be026f97dd7d6a5f0f507efdeb/extension/healthcheckextension/README.md
- curl manual (the `exitcode` and `errormsg` write-out variables, both added in curl 7.75.0): https://curl.se/docs/manpage.html
- Phoenix defaults `HOST = "0.0.0.0"`, `PORT = 6006`, `GRPC_PORT = 4317` (pinned tag arize-phoenix-v20.16.0): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.16.0/src/phoenix/config.py#L3111-L3117
- Phoenix gRPC OTLP server binds `[::]` regardless of the HTTP host (pinned tag arize-phoenix-v20.16.0): https://github.com/Arize-ai/phoenix/blob/arize-phoenix-v20.16.0/src/phoenix/server/grpc_server.py#L107-L109
