---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "b0cc3b842addeb734609d02f9a1dd4f917b95484fec0be92623b9f4a9bd126dd",
  "components": {
    "nocodb": {
      "name": "NocoDB",
      "basis": "2026.09.0",
      "sources": {
        "sa19c6557b712": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/Noco.ts",
        "s635b35ce4689": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/trustProxy.ts",
        "sd74ca4df55b0": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/run/dockerEntry.ts",
        "s5ea55dc5f0d9": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/services/users/users.service.ts",
        "sd0e9f451673f": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/interface/AppSettings.ts",
        "s8a1de0bc97b0": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/helpers/initAdminFromEnv.ts",
        "sca40040b40cc": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/encryptDecrypt.ts",
        "saf056bb4ff37": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/helpers/initDataSourceEncryption.ts",
        "sbfbf630008e1": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/docker/start.sh",
        "se5da9707c684": "https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/docker/start-litestream.sh",
        "s536899ecd4a5": "https://github.com/nocodb/nocodb/blob/2026.09.0/README.md",
        "se81c30b3f43b": "https://github.com/nocodb/nocodb/blob/2026.09.0/docker-compose/examples/external-postgres-and-redis/docker.env"
      }
    },
    "docker": {
      "name": "Docker docs",
      "basis": "unknown",
      "sources": {
        "sd34e76a09f6c": "https://docs.docker.com/reference/cli/docker/container/exec/",
        "s2fecb6db5480": "https://docs.docker.com/engine/network/firewall-iptables/"
      }
    },
    "docker-new": {
      "name": "Docker CLI",
      "basis": "v27.2.0",
      "sources": {
        "sca9a0e1e4b6a": "https://github.com/docker/cli/blob/v27.2.0/cli/command/formatter/container.go"
      }
    },
    "docker-old": {
      "name": "Docker CLI",
      "basis": "v27.1.2",
      "sources": {
        "sa202ad11d4ed": "https://github.com/docker/cli/blob/v27.1.2/cli/command/formatter/container.go"
      }
    },
    "node": {
      "name": "Node.js",
      "basis": "v22.22.1",
      "sources": {
        "sfb3e306c102d": "https://github.com/nodejs/node/blob/v22.22.1/doc/api/net.md"
      }
    },
    "baserow": {
      "name": "Baserow",
      "basis": "2.3.4",
      "sources": {
        "s1b31314982f4": "https://github.com/baserow/baserow/blob/2.3.4/docker-compose.yml",
        "s3f61036aca03": "https://github.com/baserow/baserow/blob/2.3.4/docs/installation/install-with-docker.md",
        "s34b87f60dcc6": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/core/user/handler.py",
        "s4588448964a2": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/core/models.py",
        "sd858f9ee45e0": "https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/core/apps.py",
        "s1a472d828699": "https://github.com/baserow/baserow/blob/2.3.4/.env.example"
      }
    },
    "appsmith": {
      "name": "Appsmith",
      "basis": "v2.4.1",
      "sources": {
        "s2650629933a1": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/resources/application-ce.properties",
        "sd1c55be91e30": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/solutions/ce/UserSignupCEImpl.java",
        "se3cd894dc579": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/exceptions/AppsmithError.java",
        "sa68daf87cde7": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/deploy/docker/fs/opt/appsmith/entrypoint.sh",
        "s9fdcff5a28a4": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/deploy/docker/docker-compose.yml",
        "sfa551c344e8b": "https://github.com/appsmithorg/appsmith/blob/v2.4.1/deploy/aws_ami/docker-compose.yml"
      }
    },
    "budibase": {
      "name": "Budibase",
      "basis": "v3.46.0",
      "sources": {
        "s735ead81ce9c": "https://github.com/Budibase/budibase/blob/v3.46.0/hosting/.env",
        "s74d858053d12": "https://github.com/Budibase/budibase/blob/v3.46.0/hosting/docker-compose.yaml",
        "s7fbf706a4c8f": "https://github.com/Budibase/budibase/blob/v3.46.0/hosting/proxy/nginx.prod.conf",
        "s45379b35a980": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/index.ts",
        "sc0a3ac85466f": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/controllers/global/users.ts",
        "s4902d93986c7": "https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/routes/global/users.ts"
      }
    },
    "couchdb": {
      "name": "CouchDB",
      "basis": "3.5.2",
      "sources": {
        "s34292991c4ec": "https://github.com/apache/couchdb/blob/3.5.2/src/docs/src/api/server/authn.rst"
      }
    },
    "windmill": {
      "name": "Windmill",
      "basis": "v1.817.0",
      "sources": {
        "s91439e21d4ac": "https://github.com/windmill-labs/windmill/blob/v1.817.0/README.md",
        "s8e4bbba271f2": "https://github.com/windmill-labs/windmill/blob/v1.817.0/backend/src/main.rs",
        "sd775b7c95872": "https://github.com/windmill-labs/windmill/blob/v1.817.0/backend/windmill-worker/src/worker.rs",
        "sfcc72cf06c9e": "https://github.com/windmill-labs/windmill/blob/v1.817.0/docker-compose.yml",
        "s345ca635c837": "https://github.com/windmill-labs/windmill/blob/v1.817.0/backend/migrations/20220123221903_first.up.sql",
        "s03c33b490c08": "https://github.com/windmill-labs/windmill/blob/v1.817.0/backend/migrations/20220816185849_remove_non_admin_users.up.sql"
      }
    }
  },
  "claims": {
    "private": {"text": "Keep builders private with fronting auth, claim admin early and protect databases storing connected-system credentials.", "components": ["nocodb", "baserow", "appsmith", "budibase", "windmill"], "sources": ["nocodb:sd74ca4df55b0", "baserow:s1b31314982f4", "appsmith:s9fdcff5a28a4", "budibase:s74d858053d12", "windmill:sfcc72cf06c9e"], "status": "REASONED"},
    "nocodb-bind": {"text": "PORT defaults 8080; listen omits host, so Node binds unspecified IPv6/IPv4. No application bind setting; restrict publication/firewall.", "components": ["nocodb", "node"], "sources": ["nocodb:sa19c6557b712", "nocodb:sd74ca4df55b0", "node:sfb3e306c102d"], "status": "REASONED"},
    "nocodb-first": {"text": "First signup becomes super-admin; claim first or seed NC_ADMIN_EMAIL/NC_ADMIN_PASSWORD.", "components": ["nocodb"], "sources": ["nocodb:s5ea55dc5f0d9", "nocodb:s8a1de0bc97b0"], "status": "REASONED"},
    "nocodb-signup": {"text": "invite_only_signup defaults false; enable to stop later self-signups.", "components": ["nocodb"], "sources": ["nocodb:s5ea55dc5f0d9", "nocodb:sd0e9f451673f"], "status": "REASONED"},
    "nocodb-encryption": {"text": "Unset NC_CONNECTION_ENCRYPT_KEY stores external DB credentials unchanged; set before adding sources, or startup encrypts existing sources when added later.", "components": ["nocodb"], "sources": ["nocodb:sca40040b40cc", "nocodb:saf056bb4ff37"], "status": "REASONED"},
    "nocodb-jwt": {"text": "Unset NC_AUTH_JWT_SECRET generates/stores a UUID as nc_auth_jwt_secret; replace README sample 569a1821-0a93-45e8-87ab-eb857f20a010.", "components": ["nocodb"], "sources": ["nocodb:sa19c6557b712", "nocodb:s536899ecd4a5"], "status": "REASONED"},
    "nocodb-cors": {"text": "Entry file allows every CORS origin.", "components": ["nocodb"], "sources": ["nocodb:sd74ca4df55b0"], "status": "REASONED"},
    "nocodb-proxy": {"text": "Startup resets trust proxy from NC_TRUST_PROXY, default no trust; restrict hops/subnets, never true with direct client access.", "components": ["nocodb"], "sources": ["nocodb:sa19c6557b712", "nocodb:s635b35ce4689", "nocodb:sd74ca4df55b0"], "status": "REASONED"},
    "nocodb-packaging": {"text": "README binaries are for local quick tests; guide records no 2026.09.0 release binaries and image/install-script production paths.", "components": ["nocodb"], "sources": ["nocodb:s536899ecd4a5"], "status": "REASONED"},
    "baserow-bind": {"text": "Caddy publishes 80/443 on HOST_PUBLISH_IP default 0.0.0.0; set it or publish loopback. Docker wildcard publication bypasses UFW.", "components": ["baserow"], "sources": ["baserow:s1b31314982f4", "baserow:s3f61036aca03"], "status": "REASONED"},
    "baserow-first": {"text": "First signup becomes staff; claim before exposure.", "components": ["baserow"], "sources": ["baserow:s34b87f60dcc6"], "status": "REASONED"},
    "baserow-signup": {"text": "allow_new_signups defaults True; disable in admin settings, yielding Sign up is disabled.", "components": ["baserow"], "sources": ["baserow:s34b87f60dcc6", "baserow:s4588448964a2"], "status": "REASONED"},
    "baserow-secrets": {"text": "Compose requires SECRET_KEY/DATABASE_PASSWORD/REDIS_PASSWORD; .env.example leaves them empty. Generate your own.", "components": ["baserow"], "sources": ["baserow:s1b31314982f4", "baserow:s1a472d828699"], "status": "REASONED"},
    "baserow-mfa": {"text": "Core registers a TOTP provider.", "components": ["baserow"], "sources": ["baserow:sd858f9ee45e0"], "status": "REASONED"},
    "appsmith-bind": {"text": "Java defaults APPSMITH_SERVER_ADDRESS=127.0.0.1 and port 8080 inside the container.", "components": ["appsmith"], "sources": ["appsmith:s2650629933a1"], "status": "REASONED"},
    "appsmith-publish": {"text": "Bundled Caddy fronts port 80; development Compose publishes host 8080, AWS example 80/443.", "components": ["appsmith"], "sources": ["appsmith:sa68daf87cde7", "appsmith:s9fdcff5a28a4", "appsmith:sfa551c344e8b"], "status": "REASONED"},
    "appsmith-first": {"text": "First signup claims super-user while no users exist; claim before exposure.", "components": ["appsmith"], "sources": ["appsmith:sd1c55be91e30"], "status": "REASONED"},
    "appsmith-signup": {"text": "APPSMITH_SIGNUP_DISABLED defaults false; set true or restrict APPSMITH_SIGNUP_ALLOWED_DOMAINS. Refusal is SIGNUP_DISABLED.", "components": ["appsmith"], "sources": ["appsmith:s2650629933a1", "appsmith:sd1c55be91e30", "appsmith:se3cd894dc579"], "status": "REASONED"},
    "appsmith-encryption": {"text": "Entrypoint generates 13-character encryption password/salt; external values override them. Development Compose sets both abcd; replace before first start.", "components": ["appsmith"], "sources": ["appsmith:sa68daf87cde7", "appsmith:s9fdcff5a28a4"], "status": "REASONED"},
    "appsmith-rotation": {"text": "Changing an existing abcd encryption pair presumably makes stored credentials unreadable; plan re-entry. Inferred, not tested.", "components": ["appsmith"], "sources": ["appsmith:sa68daf87cde7", "appsmith:s9fdcff5a28a4"], "status": "REASONED"},
    "budibase-publish": {"text": "Proxy publishes MAIN_PORT, sample 10000; LiteLLM publishes LITELLM_PORT default 4000.", "components": ["budibase"], "sources": ["budibase:s735ead81ce9c", "budibase:s74d858053d12"], "status": "REASONED"},
    "budibase-couchdb": {"text": "Proxy /db/ reaches CouchDB, exposing sample budibase/budibase login to anyone reaching it.", "components": ["budibase"], "sources": ["budibase:s735ead81ce9c", "budibase:s7fbf706a4c8f"], "status": "REASONED"},
    "budibase-secrets": {"text": "Sample JWT_SECRET/API_ENCRYPTION_KEY are testsecret; service passwords, INTERNAL_API_KEY and LITELLM_MASTER_KEY are budibase. Replace all.", "components": ["budibase"], "sources": ["budibase:s735ead81ce9c", "budibase:s74d858053d12"], "status": "REASONED"},
    "budibase-sample-check": {"text": "Recorded source search found no production rejection of testsecret; source reasoning, not a live safeguard test.", "components": ["budibase"], "sources": ["budibase:s735ead81ce9c"], "status": "REASONED"},
    "budibase-init": {"text": "Unauthenticated POST /api/global/users/init creates first admin until a user exists; validation runs first, so no read-only claimed-state probe.", "components": ["budibase"], "sources": ["budibase:s45379b35a980", "budibase:sc0a3ac85466f", "budibase:s4902d93986c7"], "status": "REASONED"},
    "budibase-seed": {"text": "Claim admin before exposure or seed BB_ADMIN_USER_EMAIL/BB_ADMIN_USER_PASSWORD.", "components": ["budibase"], "sources": ["budibase:sc0a3ac85466f"], "status": "REASONED"},
    "windmill-code": {"text": "Workers execute user scripts; a login enables code execution on worker hosts.", "components": ["windmill"], "sources": ["windmill:s91439e21d4ac", "windmill:sd775b7c95872"], "status": "REASONED"},
    "windmill-bind": {"text": "Default 0.0.0.0:8000; SERVER_BIND_ADDR changes binary binding. Default wildcard bind was not observed.", "components": ["windmill"], "sources": ["windmill:s8e4bbba271f2"], "status": "REASONED"},
    "windmill-compose": {"text": "Compose exposes server 8000 internally; Caddy publishes 80/25 on all host interfaces. Bind publications privately; container loopback cutting Caddy off is inferred.", "components": ["windmill"], "sources": ["windmill:sfcc72cf06c9e"], "status": "REASONED"},
    "windmill-sandbox": {"text": "DISABLE_NSJAIL defaults true; sandboxing is not enabled by default.", "components": ["windmill"], "sources": ["windmill:sd775b7c95872"], "status": "REASONED"},
    "windmill-privileged": {"text": "Shipped worker uses privileged=true.", "components": ["windmill"], "sources": ["windmill:sfcc72cf06c9e"], "status": "REASONED"},
    "windmill-smtp": {"text": "Port 25 serves email triggers; do not publish unless used.", "components": ["windmill"], "sources": ["windmill:sfcc72cf06c9e"], "status": "REASONED"},
    "windmill-debugger": {"text": "Vendor warns REQUIRE_SIGNED_DEBUG_REQUESTS=false exposes an unauthenticated code-execution debugger on reachable deployments.", "components": ["windmill"], "sources": ["windmill:sfcc72cf06c9e"], "status": "REASONED"},
    "verify-nocodb-signup": {"text": "Controlled signup creation is exposed; invite-only refusal is fixed. Hidden links prove nothing; inspect backend setting and confirm admin login.", "components": ["nocodb"], "sources": ["nocodb:s5ea55dc5f0d9", "nocodb:sd0e9f451673f"], "status": "REASONED"},
    "verify-baserow-signup": {"text": "Controlled signup creation is exposed; Sign up is disabled is fixed. Inspect allow_new_signups and confirm admin login.", "components": ["baserow"], "sources": ["baserow:s34b87f60dcc6", "baserow:s4588448964a2"], "status": "REASONED"},
    "verify-appsmith-signup": {"text": "Controlled signup creation is exposed; SIGNUP_DISABLED is fixed. Inspect backend settings, confirm admin login and delete test accounts.", "components": ["appsmith"], "sources": ["appsmith:s2650629933a1", "appsmith:sd1c55be91e30", "appsmith:se3cd894dc579"], "status": "REASONED"},
    "verify-external": {"text": "Probe each public IP; control proves only its port, refusal/timeout may be local filtering, and unexpected connections need host confirmation.", "components": ["baserow", "budibase", "windmill"], "sources": ["baserow:s1b31314982f4", "budibase:s74d858053d12", "windmill:sfcc72cf06c9e"], "status": "REASONED"},
    "windmill-default-login": {"text": "Fresh loopback DB had only admin@windmill.dev as a password user/super-admin; changeme returned 200/token, then 400 after rotation while the new password returned 200.", "components": ["windmill"], "sources": ["windmill:s91439e21d4ac", "windmill:s345ca635c837", "windmill:s03c33b490c08"], "status": "DEMONSTRATED", "evidence": "After the password was changed, `changeme` got `400` and the new password `200`.", "verify": [4]},
    "windmill-loopback": {"text": "SERVER_BIND_ADDR=127.0.0.1 produced only a loopback listener on the test port.", "components": ["windmill"], "sources": ["windmill:s8e4bbba271f2"], "status": "DEMONSTRATED", "evidence": "The server's only listener was on 127.0.0.1, at the test port the run set."},
    "windmill-sandbox-run": {"text": "Loopback worker without nsjail logged sandboxing unavailable; this does not demonstrate isolation.", "components": ["windmill"], "sources": ["windmill:sd775b7c95872"], "status": "DEMONSTRATED", "evidence": "on the loopback run, without nsjail installed, the worker logged \"Nsjail sandboxing will NOT be available\"."},
    "verify-inventory": {"text": "Inventory host sockets and Docker publications; NAT may have no socket, so absent ss entries do not establish isolation.", "components": ["docker", "baserow", "appsmith", "budibase", "windmill"], "sources": ["docker:s2fecb6db5480", "baserow:s1b31314982f4", "appsmith:s9fdcff5a28a4", "budibase:s74d858053d12", "windmill:sfcc72cf06c9e"], "status": "REASONED", "verify": [1]},
    "verify-port-display": {"text": "IPv6 wildcard displays [::]: from v27.2.0 versus ::: through v27.1.2; both mean all host addresses unless filtered.", "components": ["docker", "docker-new", "docker-old"], "sources": ["docker:s2fecb6db5480", "docker-new:sca9a0e1e4b6a", "docker-old:sa202ad11d4ed"], "status": "REASONED", "verify": [1]},
    "verify-sample-tokens": {"text": "Whole-token search found sample secrets/variants, clean replaced copies and unreadable paths; harmless matches and external environment values limit scope.", "components": ["nocodb", "appsmith", "budibase", "windmill"], "sources": ["nocodb:s536899ecd4a5", "appsmith:s9fdcff5a28a4", "budibase:s735ead81ce9c", "windmill:sfcc72cf06c9e"], "status": "DEMONSTRATED", "evidence": "On copies with the values replaced it printed \"no vendor sample tokens found\", and on an unreadable path it reported that it did not check.", "verify": [2]},
    "verify-nocodb-key": {"text": "docker exec tests configured key presence without printing it or passing its value in argv; no real container run. Startup selection/process value remain unverified.", "components": ["nocodb", "docker"], "sources": ["nocodb:sbfbf630008e1", "nocodb:se5da9707c684", "docker:sd34e76a09f6c"], "status": "REASONED", "verify": [3]},
    "nocodb-key-limits": {"text": "Trusted shells/startup assumed; environment remains readable to same-account/root or Docker-socket holders. Presence does not prove encryption; do not inject a replacement key.", "components": ["nocodb", "docker"], "sources": ["nocodb:sca40040b40cc", "nocodb:sbfbf630008e1", "nocodb:se5da9707c684", "docker:sd34e76a09f6c"], "status": "REASONED", "verify": [3]},
    "nocodb-key-logic": {"text": "A docker exec stand-in exercised set/empty/unset/missing-container branches only; no NocoDB deployment demonstrated.", "components": ["docker"], "sources": ["docker:sd34e76a09f6c"], "status": "DEMONSTRATED", "evidence": "With a stand-in for `docker exec`, the block printed \"non-empty\" for a set key, \"EMPTY or unset\" for an empty and an unset one, and \"not checked\" when the container was missing;"},
    "verify-windmill-control": {"text": "Before trusting default-login 400, confirm real credentials work so a dead service is not treated as fixed.", "components": ["windmill"], "sources": ["windmill:s91439e21d4ac"], "status": "REASONED"},
    "verify-couchdb": {"text": "Sample login at /db/_session?basic=true should return 200 exposed and 401 after replacement; real credentials are the positive control.", "components": ["budibase", "couchdb"], "sources": ["budibase:s735ead81ce9c", "budibase:s7fbf706a4c8f", "couchdb:s34292991c4ec"], "status": "REASONED", "verify": [5]},
    "verify-litellm": {"text": "Sample Bearer budibase at /v1/models should return 200 exposed/401 fixed; confirm real credentials. Endpoint discrimination is cross-referenced to litellm.md, not directly sourced here.", "components": ["budibase"], "sources": ["budibase:s735ead81ce9c", "budibase:s74d858053d12"], "status": "REASONED", "verify": [5]},
    "verify-tcp-outcomes": {"text": "Loopback observed connected/open, timeout/full accept queue, refused/closed and failed-control stopping; no real firewall demonstrated.", "components": ["baserow", "budibase", "windmill"], "sources": ["baserow:s1b31314982f4", "budibase:s74d858053d12", "windmill:sfcc72cf06c9e"], "status": "DEMONSTRATED", "evidence": "On loopback it printed \"connected\" for the control and an open port, \"timed out\" for a port whose accept queue was full (standing in for a filtered one) and \"refused\" for a closed port, and it stopped when the control was closed.", "verify": [6]},
    "verify-tcp-inputs": {"text": "Guard tests reject named hosts, malformed IPv4, zero/dotted IPv6, invalid ports and absent timeout; loopback/hex-mapped IPv6 pass. Invalid hex may fail at control.", "components": ["baserow", "budibase", "windmill"], "sources": ["baserow:s1b31314982f4", "budibase:s74d858053d12", "windmill:sfcc72cf06c9e"], "status": "DEMONSTRATED", "evidence": "`::ffff:0:0` and `::ffff:7f00:1` passed and connected to a listener bound to 127.0.0.1", "verify": [6]}
  }
}
---
# Low-code internal-tool builders: NocoDB, Baserow, Appsmith, Budibase, and Windmill

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| private: Keep builders private with fronting auth, claim admin early and protect databases storing connected-system credentials. | NocoDB 2026.09.0; Baserow 2.3.4; Appsmith v2.4.1; Budibase v3.46.0; Windmill v1.817.0 | REASONED |
| nocodb-bind: PORT defaults 8080; listen omits host, so Node binds unspecified IPv6/IPv4. No application bind setting; restrict publication/firewall. | NocoDB 2026.09.0; Node.js v22.22.1 | REASONED |
| nocodb-first: First signup becomes super-admin; claim first or seed NC_ADMIN_EMAIL/NC_ADMIN_PASSWORD. | NocoDB 2026.09.0 | REASONED |
| nocodb-signup: invite_only_signup defaults false; enable to stop later self-signups. | NocoDB 2026.09.0 | REASONED |
| nocodb-encryption: Unset NC_CONNECTION_ENCRYPT_KEY stores external DB credentials unchanged; set before adding sources, or startup encrypts existing sources when added later. | NocoDB 2026.09.0 | REASONED |
| nocodb-jwt: Unset NC_AUTH_JWT_SECRET generates/stores a UUID as nc_auth_jwt_secret; replace README sample 569a1821-0a93-45e8-87ab-eb857f20a010. | NocoDB 2026.09.0 | REASONED |
| nocodb-cors: Entry file allows every CORS origin. | NocoDB 2026.09.0 | REASONED |
| nocodb-proxy: Startup resets trust proxy from NC_TRUST_PROXY, default no trust; restrict hops/subnets, never true with direct client access. | NocoDB 2026.09.0 | REASONED |
| nocodb-packaging: README binaries are for local quick tests; guide records no 2026.09.0 release binaries and image/install-script production paths. | NocoDB 2026.09.0 | REASONED |
| baserow-bind: Caddy publishes 80/443 on HOST_PUBLISH_IP default 0.0.0.0; set it or publish loopback. Docker wildcard publication bypasses UFW. | Baserow 2.3.4 | REASONED |
| baserow-first: First signup becomes staff; claim before exposure. | Baserow 2.3.4 | REASONED |
| baserow-signup: allow_new_signups defaults True; disable in admin settings, yielding Sign up is disabled. | Baserow 2.3.4 | REASONED |
| baserow-secrets: Compose requires SECRET_KEY/DATABASE_PASSWORD/REDIS_PASSWORD; .env.example leaves them empty. Generate your own. | Baserow 2.3.4 | REASONED |
| baserow-mfa: Core registers a TOTP provider. | Baserow 2.3.4 | REASONED |
| appsmith-bind: Java defaults APPSMITH_SERVER_ADDRESS=127.0.0.1 and port 8080 inside the container. | Appsmith v2.4.1 | REASONED |
| appsmith-publish: Bundled Caddy fronts port 80; development Compose publishes host 8080, AWS example 80/443. | Appsmith v2.4.1 | REASONED |
| appsmith-first: First signup claims super-user while no users exist; claim before exposure. | Appsmith v2.4.1 | REASONED |
| appsmith-signup: APPSMITH_SIGNUP_DISABLED defaults false; set true or restrict APPSMITH_SIGNUP_ALLOWED_DOMAINS. Refusal is SIGNUP_DISABLED. | Appsmith v2.4.1 | REASONED |
| appsmith-encryption: Entrypoint generates 13-character encryption password/salt; external values override them. Development Compose sets both abcd; replace before first start. | Appsmith v2.4.1 | REASONED |
| appsmith-rotation: Changing an existing abcd encryption pair presumably makes stored credentials unreadable; plan re-entry. Inferred, not tested. | Appsmith v2.4.1 | REASONED |
| budibase-publish: Proxy publishes MAIN_PORT, sample 10000; LiteLLM publishes LITELLM_PORT default 4000. | Budibase v3.46.0 | REASONED |
| budibase-couchdb: Proxy /db/ reaches CouchDB, exposing sample budibase/budibase login to anyone reaching it. | Budibase v3.46.0 | REASONED |
| budibase-secrets: Sample JWT_SECRET/API_ENCRYPTION_KEY are testsecret; service passwords, INTERNAL_API_KEY and LITELLM_MASTER_KEY are budibase. Replace all. | Budibase v3.46.0 | REASONED |
| budibase-sample-check: Recorded source search found no production rejection of testsecret; source reasoning, not a live safeguard test. | Budibase v3.46.0 | REASONED |
| budibase-init: Unauthenticated POST /api/global/users/init creates first admin until a user exists; validation runs first, so no read-only claimed-state probe. | Budibase v3.46.0 | REASONED |
| budibase-seed: Claim admin before exposure or seed BB_ADMIN_USER_EMAIL/BB_ADMIN_USER_PASSWORD. | Budibase v3.46.0 | REASONED |
| windmill-code: Workers execute user scripts; a login enables code execution on worker hosts. | Windmill v1.817.0 | REASONED |
| windmill-bind: Default 0.0.0.0:8000; SERVER_BIND_ADDR changes binary binding. Default wildcard bind was not observed. | Windmill v1.817.0 | REASONED |
| windmill-compose: Compose exposes server 8000 internally; Caddy publishes 80/25 on all host interfaces. Bind publications privately; container loopback cutting Caddy off is inferred. | Windmill v1.817.0 | REASONED |
| windmill-sandbox: DISABLE_NSJAIL defaults true; sandboxing is not enabled by default. | Windmill v1.817.0 | REASONED |
| windmill-privileged: Shipped worker uses privileged=true. | Windmill v1.817.0 | REASONED |
| windmill-smtp: Port 25 serves email triggers; do not publish unless used. | Windmill v1.817.0 | REASONED |
| windmill-debugger: Vendor warns REQUIRE_SIGNED_DEBUG_REQUESTS=false exposes an unauthenticated code-execution debugger on reachable deployments. | Windmill v1.817.0 | REASONED |
| verify-nocodb-signup: Controlled signup creation is exposed; invite-only refusal is fixed. Hidden links prove nothing; inspect backend setting and confirm admin login. | NocoDB 2026.09.0 | REASONED |
| verify-baserow-signup: Controlled signup creation is exposed; Sign up is disabled is fixed. Inspect allow_new_signups and confirm admin login. | Baserow 2.3.4 | REASONED |
| verify-appsmith-signup: Controlled signup creation is exposed; SIGNUP_DISABLED is fixed. Inspect backend settings, confirm admin login and delete test accounts. | Appsmith v2.4.1 | REASONED |
| verify-external: Probe each public IP; control proves only its port, refusal/timeout may be local filtering, and unexpected connections need host confirmation. | Baserow 2.3.4; Budibase v3.46.0; Windmill v1.817.0 | REASONED |
| windmill-default-login: Fresh loopback DB had only admin@windmill.dev as a password user/super-admin; changeme returned 200/token, then 400 after rotation while the new password returned 200. | Windmill v1.817.0 | DEMONSTRATED |
| windmill-loopback: SERVER_BIND_ADDR=127.0.0.1 produced only a loopback listener on the test port. | Windmill v1.817.0 | DEMONSTRATED |
| windmill-sandbox-run: Loopback worker without nsjail logged sandboxing unavailable; this does not demonstrate isolation. | Windmill v1.817.0 | DEMONSTRATED |
| verify-inventory: Inventory host sockets and Docker publications; NAT may have no socket, so absent ss entries do not establish isolation. | Docker docs unknown; Baserow 2.3.4; Appsmith v2.4.1; Budibase v3.46.0; Windmill v1.817.0 | REASONED |
| verify-port-display: IPv6 wildcard displays [::]: from v27.2.0 versus ::: through v27.1.2; both mean all host addresses unless filtered. | Docker docs unknown; Docker CLI v27.2.0; Docker CLI v27.1.2 | REASONED |
| verify-sample-tokens: Whole-token search found sample secrets/variants, clean replaced copies and unreadable paths; harmless matches and external environment values limit scope. | NocoDB 2026.09.0; Appsmith v2.4.1; Budibase v3.46.0; Windmill v1.817.0 | DEMONSTRATED |
| verify-nocodb-key: docker exec tests configured key presence without printing it or passing its value in argv; no real container run. Startup selection/process value remain unverified. | NocoDB 2026.09.0; Docker docs unknown | REASONED |
| nocodb-key-limits: Trusted shells/startup assumed; environment remains readable to same-account/root or Docker-socket holders. Presence does not prove encryption; do not inject a replacement key. | NocoDB 2026.09.0; Docker docs unknown | REASONED |
| nocodb-key-logic: A docker exec stand-in exercised set/empty/unset/missing-container branches only; no NocoDB deployment demonstrated. | Docker docs unknown | DEMONSTRATED |
| verify-windmill-control: Before trusting default-login 400, confirm real credentials work so a dead service is not treated as fixed. | Windmill v1.817.0 | REASONED |
| verify-couchdb: Sample login at /db/_session?basic=true should return 200 exposed and 401 after replacement; real credentials are the positive control. | Budibase v3.46.0; CouchDB 3.5.2 | REASONED |
| verify-litellm: Sample Bearer budibase at /v1/models should return 200 exposed/401 fixed; confirm real credentials. Endpoint discrimination is cross-referenced to litellm.md, not directly sourced here. | Budibase v3.46.0 | REASONED |
| verify-tcp-outcomes: Loopback observed connected/open, timeout/full accept queue, refused/closed and failed-control stopping; no real firewall demonstrated. | Baserow 2.3.4; Budibase v3.46.0; Windmill v1.817.0 | DEMONSTRATED |
| verify-tcp-inputs: Guard tests reject named hosts, malformed IPv4, zero/dotted IPv6, invalid ports and absent timeout; loopback/hex-mapped IPv6 pass. Invalid hex may fail at control. | Baserow 2.3.4; Budibase v3.46.0; Windmill v1.817.0 | DEMONSTRATED |
<!-- version-basis:end -->

These tools sit on top of your databases and APIs and let people build internal apps, forms and
automations quickly. That is also the exposure. Each one stores credentials for the systems it connects
to, and Windmill runs arbitrary code by design. Three first-run patterns recur. On a fresh instance, the
first visitor becomes the administrator. Open signup is on by default. And the vendor's own sample
configuration ships fixed secrets that too many deployments keep. Keep every one of them private
([docker.md](docker.md), [cloud-firewalls.md](cloud-firewalls.md), [tunnels.md](tunnels.md)), claim the
admin account before the instance is reachable, and front the web UI per
[fronting-auth.md](fronting-auth.md), [nginx.md](nginx.md) or [caddy.md](caddy.md). Treat the database
behind each tool as a store of every connected system's credentials ([secrets.md](secrets.md)).
Versions checked: NocoDB 2026.09.0, Baserow 2.3.4, Appsmith v2.4.1, Budibase v3.46.0 and Windmill
v1.817.0.

## NocoDB

NocoDB listens on port 8080 (`process.env.PORT || '8080'`), and its entry point calls `listen` with no
host. For an omitted host, Node "will accept connections on the unspecified IPv6 address (`::`) when IPv6
is available, or the unspecified IPv4 address (`0.0.0.0`) otherwise", so the server listens on every
interface; its code passes no host, so NocoDB offers no bind setting. Restrict it with the container
publication or a firewall. The first account to sign up gets the super-admin role, and later self-signups are allowed
unless invite-only signup is on; `invite_only_signup` defaults to `false`. Claim the admin account first,
or seed it with `NC_ADMIN_EMAIL` and `NC_ADMIN_PASSWORD`, then turn on invite-only signup.

Two secrets need your attention:

- **`NC_CONNECTION_ENCRYPT_KEY`.** When it is unset, the encryption helper returns the value unchanged,
  so the credentials of every external database you connect are stored in plaintext in NocoDB's meta
  database. Set it before connecting a data source; when it is set later, NocoDB encrypts the existing
  sources on startup.
- **`NC_AUTH_JWT_SECRET`.** When it is unset, NocoDB generates a UUID, stores it in the meta database
  as `nc_auth_jwt_secret` and uses it, which is fine. The README's Docker example hard-codes one literal
  value (`569a1821-0a93-45e8-87ab-eb857f20a010`), so everyone who copies that example signs sessions
  with the same key. Generate your own.

The entry file allows every CORS origin. It also enables Express's `trust proxy`, but startup then
resets that from `NC_TRUST_PROXY`, which trusts no proxy unless you set it; once a proxy is in front,
set it to that proxy's hop count or subnet, and never to `true` on a server clients can reach directly. The README says the release binaries "are only for quick testing
locally", and the 2026.09.0 GitHub release publishes no binaries; production installs use the
container image or the vendor's install script.

## Baserow

Baserow's default Compose file publishes the bundled Caddy on 80 and 443 at
`${HOST_PUBLISH_IP:-0.0.0.0}`, so every interface unless you set `HOST_PUBLISH_IP`. The vendor's install
guide warns that "docker when exposing ports on 0.0.0.0 will bypass any ufw firewall rules", and
suggests `-p 127.0.0.1:80:80 -p 127.0.0.1:443:443` if public exposure is not intended. The first user
to sign up is made staff (`is_staff=not User.objects.exists()`), and new signups are allowed by default
(`allow_new_signups` defaults to `True`). Sign up first, then turn off new signups in the admin
settings; a refused signup then fails with "Sign up is disabled."

The Compose file refuses to start without `SECRET_KEY`, `DATABASE_PASSWORD` and `REDIS_PASSWORD`
(`${SECRET_KEY:?}`), and `.env.example` leaves them empty rather than shipping examples, so the secrets
are yours to generate. Baserow's core registers a TOTP two-factor authentication provider.

## Appsmith

Appsmith's Java server binds to `127.0.0.1` on 8080 by default (`APPSMITH_SERVER_ADDRESS`), inside a
container fronted by a bundled Caddy on port 80. The vendor's development Compose file publishes that
on host port 8080, and its AWS example on 80 and 443. Signup is enabled by default
(`APPSMITH_SIGNUP_DISABLED` defaults to `false`). On a fresh instance, the first user to sign up claims
the super-user slot while no users exist. Claim it before exposing the instance, then set
`APPSMITH_SIGNUP_DISABLED=true` or restrict signup with `APPSMITH_SIGNUP_ALLOWED_DOMAINS`; a refused
signup gets the `SIGNUP_DISABLED` error, "Signup is restricted on this instance of Appsmith".

Datasource credentials are encrypted with `APPSMITH_ENCRYPTION_PASSWORD` and
`APPSMITH_ENCRYPTION_SALT`. On first start, the image's entrypoint generates random 13-character values
for both. But the vendor's development Compose file sets both to `abcd`, and values passed from outside
override the generated ones. Anyone who copies that file encrypts every stored datasource credential
with a published key. Remove those two lines, or set long random values, before the first start. On an
instance that already stored credentials under `abcd`, changing the pair presumably leaves them
unreadable, so plan to re-enter them (inferred from the encryption design, not tested).

## Budibase

Budibase's Compose file publishes its nginx proxy on `MAIN_PORT` (10000 in the sample `.env`) and its
LiteLLM service on `${LITELLM_PORT:-4000}`. The proxy forwards `/db/` to CouchDB. The sample
`hosting/.env` sets `JWT_SECRET` and `API_ENCRYPTION_KEY` to `testsecret`, and the CouchDB, MinIO and
Redis passwords, `INTERNAL_API_KEY` and `LITELLM_MASTER_KEY` to `budibase`, under a comment that says
"These should be updated". A search of the v3.46.0 source finds `testsecret` only in those sample files,
a DigitalOcean first-boot script, a test setup and a development script, and no code that checks for
it. With the sample file unchanged,
anyone who can reach the proxy can try `budibase`/`budibase` against CouchDB through `/db/`, and the
LiteLLM port answers to the master key `budibase`. Replace every one of those values before the first
start.

The first-run admin route `POST /api/global/users/init` needs no login and works until the first user
exists; after that it returns an error ("You cannot initialise once an global user has been created").
The route validates its request body before that check, so no read-only request shows whether an
instance is claimed. Create the admin first, or seed it with `BB_ADMIN_USER_EMAIL` and
`BB_ADMIN_USER_PASSWORD`.

## Windmill

Windmill runs scripts in Python, TypeScript, Go, Bash and more on its workers, so a Windmill login is
code execution on your worker hosts. The server listens on port 8000 on every interface by default
(`DEFAULT_SERVER_BIND_ADDR` is `0.0.0.0`; `SERVER_BIND_ADDR` changes it when you run the binary). In the
vendor's Compose file the server only `expose`s 8000 to the Compose network, and the bundled Caddy
publishes `80:80` and `25:25` on every host interface, so port 80 is where the login page is reachable.
A fresh database has one password user, `admin@windmill.dev`, a super admin whose password is
`changeme`; the README gives them as the default credentials.

On a v1.817.0 loopback run of the release binary with `SERVER_BIND_ADDR=127.0.0.1`, that was the only
password user in the fresh database, and it was a super admin. Logging in with `changeme` returned `200`
and a token, and `whoami` confirmed super-admin rights. After the password was changed, `changeme` got
`400` and the new password `200`. The server's only listener was on 127.0.0.1, at the test port the run
set. Change the password before anything else can reach the server. In Compose, bind Caddy's `ports:`
entries to `127.0.0.1` or a private address ([docker.md](docker.md)); `SERVER_BIND_ADDR=127.0.0.1` inside the
server container would presumably cut Caddy off from it (inferred, not tested).

The worker sandbox is not on by default either. `DISABLE_NSJAIL` defaults to `true` in the worker, and
on the loopback run, without nsjail installed, the worker logged "Nsjail sandboxing will NOT be
available". The vendor's Compose file runs the worker with `privileged: true` and publishes port 25 for
email triggers. Its debugger setting carries the vendor's warning: `REQUIRE_SIGNED_DEBUG_REQUESTS`
"Do NOT set to false on any internet-reachable deployment: it exposes an unauthenticated code-execution
debugger". Do not publish 25 unless you use email triggers.

## Verify

Three checks here were demonstrated: the sample-token check, the Windmill default-login pair, and
the TCP reachability probe's outcomes on loopback; the NocoDB key check's logic was exercised with a
stand-in for `docker exec`. Everything else is reasoned. NocoDB 2026.09.0, Baserow,
Appsmith and Budibase ship for production as container images and the authoring host has no container
runtime. NocoDB also cannot run here outside a container: its server calls `listen` with no host, so it
can only bind every interface, which the host forbids; the same applies to Windmill's default bind.
The remaining checks are REASONED from the cited vendor documentation and pinned source readings.

On the host, list the listeners, then read Docker's own publications, because a port published through
Docker's NAT may have no host socket at all, so absence from `ss` is not proof of isolation:

REASONED: following block; pinned Compose and Docker sources support listener/publication inventory. The recorded host has no container runtime and forbids wildcard binds; exposed/fixed expectations follow.

```bash
sudo ss -tlnp   # 8080 (NocoDB; Appsmith dev Compose), 80/443 (Baserow, Windmill Caddy), 10000 and 4000 (Budibase), 8000 and 25 (Windmill): loopback or private only
docker ps --format '{{.Names}}\t{{.Ports}}'   # every "0.0.0.0:" or "[::]:" (":::" before Docker CLI 27.2) publication accepts connections on every host address: reachable from outside unless a firewall rule (for example in DOCKER-USER) filters it
```

Exposed, the reasoned expectation is a wildcard address, on the host or in a Docker publication, for any
of those ports; fixed means a loopback or private address only.

Check each environment and Compose file the deployment uses for the vendor sample values: run the block
once per file, including every file an `env_file:` line names and the `.env` Compose reads for
variable substitution. Substitute the file path inside the
single quotes (a path containing an apostrophe needs other quoting), and paste the whole block.

DEMONSTRATED: following block; recorded sample-token runs found vendor values and syntax variants, found none in replaced copies and refused an unreadable path, as detailed below. External environment values are outside this file check.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ENV_OR_COMPOSE_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not checking"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not checking"; exit; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute your file on the set -- line above; not checking"; exit ;; esac
  { [ -f "$1" ] && [ -r "$1" ]; } || { echo "cannot read $1 as a regular file; not checked"; exit; }
  grep -n -E '(^|[^ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_])(testsecret|budibase|abcd|changeme|569a1821-0a93-45e8-87ab-eb857f20a010)([^ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_]|$)' -- "$1"
  case "$?" in
    0) echo "FOUND vendor sample tokens: inspect each line above; replace every secret still set to one" ;;
    1) echo "no vendor sample tokens found" ;;
    *) echo "grep could not read $1; not checked" ;;
  esac
)
```

The search matches each sample value as a whole token wherever it appears, so it cannot report a file
clean while one of them is still in it; the cost is that it also reports harmless lines such as `image:
budibase/apps`, so inspect each hit. Values supplied from outside the files, such as the shell
environment Compose runs in, are beyond its reach. This was demonstrated. On Budibase's sample `hosting/.env` it
reported all eleven sample lines, on Appsmith's development Compose file the two `abcd` lines, and on
Windmill's Compose file its `changeme` Postgres password. It also reported Compose defaults
(`${JWT_SECRET:-testsecret}`), flow mappings and lists (`{COUCH_DB_PASSWORD: budibase, X: 1}`),
URL parameters (`&password=changeme&`) and trailing punctuation. On copies with the values replaced it printed "no
vendor sample tokens found", and on an unreadable path it reported that it did not check.

For NocoDB, check the encryption key in the container rather than in a file: Compose variable
substitution, `env_file:` precedence and YAML values all decide the value, and the container's
configured environment is their result. `docker exec` runs with that configured environment, not with
the server process's own, so the two differ if the image's startup changes the variable. NocoDB's
pinned start scripts, `docker/start.sh` and `docker/start-litestream.sh`, run `node docker/main.js`
without touching it, but the pinned tree has no Dockerfile, so which script the image runs was not
verified. The block reports only whether the key is non-empty and never prints it. Substitute the
container name inside the single quotes.

This check assumes a clean host Bash shell, trusted container image and startup files, and a
container shell whose `[` is a builtin. It intentionally tests an existing container environment
value: prompting for a key or supplying a file would test that replacement, not the deployed
configuration. Docker's documented `exec`
environment inheritance and the pinned NocoDB startup scripts cited below are the trace for this
assumption. The host sends only the literal variable name and test program, never the key, in argv.
The container shell's builtin `[` tests the value without starting a child process with it in argv.
The key remains in the container's configured environment and is inherited by this extra shell;
the same account and root may read it through `/proc/<pid>/environ` for those processes' lifetimes,
and Docker-socket holders can read the configured value with `docker inspect`. This presence check
does not remove that exposure, prove encryption is working, or establish what the server process
actually received. Do not use `docker exec -e` to inject a key for this check.

REASONED: following block; Docker exec inheritance and pinned NocoDB start scripts support key-presence checking. No real container ran because the recorded host has no container runtime; only stand-in logic outcomes below were observed.

```bash
(
  trap - DEBUG RETURN ERR
  set +x +a +e
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_NOCODB_CONTAINER_NAME'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not checking"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not checking"; exit; }
  case "$1" in *REPLACE_WITH_*|""|-*|*[[:cntrl:]]*) echo "substitute the container name on the set -- line above; not checking"; exit ;; esac
  # shellcheck disable=SC2016  # the single-quoted script is meant to expand inside the container
  docker exec "$1" sh -c 'set +x; if [ -n "${NC_CONNECTION_ENCRYPT_KEY-}" ]; then exit 0; else exit 3; fi'
  case "$?" in
    0) echo "NC_CONNECTION_ENCRYPT_KEY is non-empty in the container's configured environment" ;;
    3) echo "NC_CONNECTION_ENCRYPT_KEY is EMPTY or unset in the container's configured environment" ;;
    *) echo "could not run the check in container $1; not checked" ;;
  esac
)
```

Exposed: "EMPTY or unset". Fixed: "non-empty". Anything else means the check did not run. With a
stand-in for `docker exec`, the block printed "non-empty" for a set key, "EMPTY or unset" for an empty
and an unset one, and "not checked" when the container was missing; it was not run against a real
NocoDB container (no container runtime on the authoring host).

For Windmill, check whether the default login still works. The password below is the vendor's
published default, not a secret, so it is fine in the request body. Substitute the base URL (for
example the Caddy address on port 80) inside the single quotes.

DEMONSTRATED: following block; Windmill v1.817.0 loopback returned 200 for changeme before rotation, 400 afterwards and 200 for the replacement password. This does not demonstrate external isolation.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_WINDMILL_BASE_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the base URL on the set -- line above; not probing" ;;
    *) printf '%s' '{"email":"admin@windmill.dev","password":"changeme"}' |
         curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 15 \
           -H 'Content-Type: application/json' --data-binary @- \
           -w 'default login: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1/api/auth/login" ;;
  esac
)
```

Exposed, the default login gets `200` with a token; fixed, it gets `400` (both observed with this block
on the loopback run). Before trusting a `400`, log in once with your real credentials, so that a dead
service is not read as fixed.

For Budibase, two reasoned requests use the published sample values, which are not secrets. Substitute
the proxy URL (`http://HOST:10000` in the sample setup) and the LiteLLM URL inside the single quotes.

REASONED: following block; Budibase samples, CouchDB session documentation and the litellm.md comparison support the 200/401 expectations below. No Budibase/LiteLLM containers ran; the recorded host has no container runtime.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_BUDIBASE_PROXY_URL' 'REPLACE_WITH_LITELLM_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1|$2" in
    *REPLACE_WITH_*|"|"*|*"|"|*[[:cntrl:]]*) echo "substitute both URLs on the set -- line above; not probing" ;;
    *) printf 'user = "budibase:budibase"\n' | curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 \
         --max-time 15 --config - -w 'couchdb sample login: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
         "$1/db/_session?basic=true"
       printf 'Authorization: Bearer budibase\n' | curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 \
         --max-time 15 -H @- -w 'litellm sample key: http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
         "$2/v1/models" ;;
  esac
)
```

Exposed, either line gets `200`, which means the sample secret is live. Fixed, the CouchDB sample login
gets `401` ("Username or password wasn't recognized", per CouchDB's `/_session` reference) and the
LiteLLM sample key gets `401` (the `/v1/models` comparison in [litellm.md](litellm.md)). Confirm each
service answers your real credentials as the positive control. Budibase's first-run admin route has no
equivalent probe: its request validation runs before the "already initialised" check, so a request
either fails validation in both states or, with a valid body on a fresh instance, creates the admin.
Claim the admin yourself before the proxy is reachable.

For NocoDB, Baserow and Appsmith, check signup by hand, reasoned from source. In a private browser
window, open the instance's sign-up page and try to create an account with an address you control.
Exposed: the account is created, or, on a fresh instance, you become its administrator. Fixed: the
signup is refused. The backends' refusal messages are NocoDB's "Not allowed to signup, contact super
admin.", Baserow's "Sign up is disabled." and Appsmith's `SIGNUP_DISABLED` error ("Signup is restricted
on this instance of Appsmith"); the web UIs may word them differently. A hidden sign-up link is
inconclusive, because the frontend does not enforce the setting: check the backend setting itself
(NocoDB's `invite_only_signup` app setting, Baserow's `allow_new_signups` admin setting, Appsmith's
`APPSMITH_SIGNUP_DISABLED`). Delete any test account the exposed state let you create, then sign in as your
admin as the positive control.

Finally, from a host that should not have access, try a TCP connection to each published port. The
block uses bash's `/dev/tcp`, so it works for SMTP on 25 as well as the web ports. It takes one IP
address rather than a host name, so that a name with both IPv4 and IPv6 addresses cannot hide one
behind a timeout on the other: run it once for each public address of the host. It also takes a port you know
is open on that address from this host (for example SSH on 22) as the positive control, and stops if
the control does not connect. Substitute both inside the single quotes.

DEMONSTRATED: following block; recorded loopback tests observed connected, refused, timeout/full accept queue, failed-control stopping and the input cases below. Public isolation remains reasoned; the timeout fixture was not a firewall.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ONE_IP_ADDRESS' 'REPLACE_WITH_A_KNOWN_OPEN_PORT'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|"") echo "substitute one IP address on the set -- line above; not probing"; exit ;; esac
  case "$1" in 0.0.0.0) echo "$1 reaches this host itself; give the public address of the service; not probing"; exit ;; esac
  ipv4='^((25[012345]|2[01234][0123456789]|1[0123456789][0123456789]|[123456789]?[0123456789])[.]){3}(25[012345]|2[01234][0123456789]|1[0123456789][0123456789]|[123456789]?[0123456789])$'
  case "$1" in
    *:*:*)
      case "$1" in *[!0123456789ABCDEFabcdef.:]*) echo "$1 is not an IPv6 address; not probing"; exit ;; esac
      case "$1" in *.*) echo "give the IPv4 address itself rather than $1; not probing"; exit ;; esac
      case "$1" in *[!0:]*) ;; *) echo "$1 is all zeros (this host itself, or not an address); give the public address of the service; not probing"; exit ;; esac ;;
    *) [[ $1 =~ $ipv4 ]] || { echo "give one IPv4 address (four numbers, 0 to 255, joined by dots) or one IPv6 address, with no host name, port or brackets; not probing"; exit; } ;;
  esac
  case "$2" in *[!0123456789]*|"") echo "substitute a known-open control port on the set -- line above; not probing"; exit ;; esac
  { [ "$2" -ge 1 ] && [ "$2" -le 65535 ]; } 2>/dev/null || { echo "the control port must be 1 to 65535; not probing"; exit; }
  command -v timeout >/dev/null || { echo "timeout is not installed here; not probing"; exit; }
  # shellcheck disable=SC2016  # the single-quoted script is meant to expand $1 and $2 in the child shell
  err=$(LC_ALL=C timeout 5 bash -c ': > "/dev/tcp/$1/$2"' probe "$1" "$2" 2>&1) ||
    { echo "control $1:$2 did not connect (${err:-timed out}); not probing"; exit; }
  echo "control $1:$2 connected"
  for p in 80 443 8080 10000 4000 8000 25; do
    # shellcheck disable=SC2016  # the single-quoted script is meant to expand $1 and $2 in the child shell
    err=$(LC_ALL=C timeout 5 bash -c ': > "/dev/tcp/$1/$2"' probe "$1" "$p" 2>&1)
    case "$?:$err" in
      0:*) echo "$1:$p connected: reachable from this host" ;;
      124:*) echo "$1:$p timed out from this host" ;;
      *"Connection refused"*) echo "$1:$p refused from this host" ;;
      *) echo "$1:$p inconclusive (not a connection, refusal or timeout): ${err:-no message}" ;;
    esac
  done
)
```

Exposed, a port reports "connected"; a transparent proxy on the probing host's network can also
complete the handshake, so confirm a surprising "connected" with `ss` on the host. "refused" and
"timed out" show only that this host could not reach the port: a firewall in front of the service
produces either, but so can filtering on the probing host's own network (many providers block outbound
SMTP on 25), and the control proves only its own port. Treat them as consistent with fixed, and take
the `ss` and `docker ps` check on the host as the authority. "inconclusive" is any other result and
says nothing about the port. The block runs the probe in the C locale so that bash's refusal message
is matched in English. On loopback it printed "connected" for the control and an open port, "timed
out" for a port whose accept queue was full (standing in for a filtered one) and "refused" for a
closed port, and it stopped when the control was closed. It refused to run for the host names
`localhost`, `cafe.be`, `fe01`, `db1` and `face`, for `1.2.3.4.5`, `999.1.1.1`, `01.2.3.4` and
`1.2.3`, for `1.2.3.4:22`, `[::1]` and `[::1]:22`, for a leading space, for control ports `0` and
`65536`, and on a machine without `timeout`. It refuses `0.0.0.0` and any IPv6 value made only of
zeros and colons (measured: `::`, `::0`, `0::`, `0000::`, `0:0:0:0:0:0:0:0`), because those reach
the probing host itself or are not addresses, and any IPv6 value containing a dot (measured:
`::ffff:0.0.0.0`, `::ffff:127.0.0.1`, `::0.0.0.0`), asking for the IPv4 address instead. It does not
refuse every value that reaches the probing host: loopback addresses pass, and hex spellings such as
`::ffff:0:0` and `::ffff:7f00:1` passed and connected to a listener bound to 127.0.0.1, so give the
service's public address. Any other value with two or
more colons, made only of hex digits and colons, is passed on as IPv6, so a port appended without brackets changes the address: `2001:db8::1:22` is still a valid
address and was probed as that different address, while `2001:db8::1:10000` and `dead::beef::` are
not, and each failed the name lookup at the control and stopped. A "connected" on a port you did not
mean to publish is the finding.

## Sources (checked September 2026)

- NocoDB 2026.09.0 port default, JWT secret generation and proxy-trust reset: https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/Noco.ts
- NocoDB 2026.09.0 proxy trust default (`NC_TRUST_PROXY`): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/trustProxy.ts
- NocoDB 2026.09.0 entry point (listen with no host, CORS): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/run/dockerEntry.ts
- NocoDB 2026.09.0 first user, signup and its refusal message: https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/services/users/users.service.ts
- NocoDB 2026.09.0 app settings (`invite_only_signup`): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/interface/AppSettings.ts
- NocoDB 2026.09.0 admin from environment (`NC_ADMIN_EMAIL`, `NC_ADMIN_PASSWORD`): https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/helpers/initAdminFromEnv.ts
- NocoDB 2026.09.0 credential encryption: https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/utils/encryptDecrypt.ts and https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/src/helpers/initDataSourceEncryption.ts
- NocoDB 2026.09.0 container start scripts: https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/docker/start.sh and https://github.com/nocodb/nocodb/blob/2026.09.0/packages/nocodb/docker/start-litestream.sh
- Docker `docker exec` environment: https://docs.docker.com/reference/cli/docker/container/exec/
- Docker packet filtering (`DOCKER-USER`): https://docs.docker.com/engine/network/firewall-iptables/
- Docker CLI port display (`[::]:` from v27.2.0, `:::` through v27.1.2): https://github.com/docker/cli/blob/v27.2.0/cli/command/formatter/container.go and https://github.com/docker/cli/blob/v27.1.2/cli/command/formatter/container.go
- NocoDB 2026.09.0 README (Docker example JWT secret, binaries note): https://github.com/nocodb/nocodb/blob/2026.09.0/README.md
- NocoDB 2026.09.0 sample environment without an encryption key: https://github.com/nocodb/nocodb/blob/2026.09.0/docker-compose/examples/external-postgres-and-redis/docker.env
- Node.js v22 `server.listen` with an omitted host: https://github.com/nodejs/node/blob/v22.22.1/doc/api/net.md
- Baserow 2.3.4 Compose file: https://github.com/baserow/baserow/blob/2.3.4/docker-compose.yml
- Baserow 2.3.4 install with Docker (ufw warning): https://github.com/baserow/baserow/blob/2.3.4/docs/installation/install-with-docker.md
- Baserow 2.3.4 first user, signup and its refusal message: https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/core/user/handler.py
- Baserow 2.3.4 settings model (`allow_new_signups`): https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/core/models.py
- Baserow 2.3.4 TOTP provider registration: https://github.com/baserow/baserow/blob/2.3.4/backend/src/baserow/core/apps.py
- Baserow 2.3.4 sample environment: https://github.com/baserow/baserow/blob/2.3.4/.env.example
- Appsmith v2.4.1 server properties (bind address, signup): https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/resources/application-ce.properties
- Appsmith v2.4.1 first super user: https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/solutions/ce/UserSignupCEImpl.java
- Appsmith v2.4.1 `SIGNUP_DISABLED` error: https://github.com/appsmithorg/appsmith/blob/v2.4.1/app/server/appsmith-server/src/main/java/com/appsmith/server/exceptions/AppsmithError.java
- Appsmith v2.4.1 image entrypoint (generated encryption values): https://github.com/appsmithorg/appsmith/blob/v2.4.1/deploy/docker/fs/opt/appsmith/entrypoint.sh
- Appsmith v2.4.1 development Compose file: https://github.com/appsmithorg/appsmith/blob/v2.4.1/deploy/docker/docker-compose.yml
- Appsmith v2.4.1 AWS Compose example: https://github.com/appsmithorg/appsmith/blob/v2.4.1/deploy/aws_ami/docker-compose.yml
- Budibase v3.46.0 sample environment: https://github.com/Budibase/budibase/blob/v3.46.0/hosting/.env
- Budibase v3.46.0 Compose file: https://github.com/Budibase/budibase/blob/v3.46.0/hosting/docker-compose.yaml
- Budibase v3.46.0 proxy configuration (`/db/`): https://github.com/Budibase/budibase/blob/v3.46.0/hosting/proxy/nginx.prod.conf
- Budibase v3.46.0 public worker routes: https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/index.ts
- Budibase v3.46.0 admin init: https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/controllers/global/users.ts
- Budibase v3.46.0 admin init route and its validation: https://github.com/Budibase/budibase/blob/v3.46.0/packages/worker/src/api/routes/global/users.ts
- Apache CouchDB 3.5.2 `/_session` reference: https://github.com/apache/couchdb/blob/3.5.2/src/docs/src/api/server/authn.rst
- Windmill v1.817.0 README (default credentials): https://github.com/windmill-labs/windmill/blob/v1.817.0/README.md
- Windmill v1.817.0 server defaults: https://github.com/windmill-labs/windmill/blob/v1.817.0/backend/src/main.rs
- Windmill v1.817.0 worker (`DISABLE_NSJAIL`): https://github.com/windmill-labs/windmill/blob/v1.817.0/backend/windmill-worker/src/worker.rs
- Windmill v1.817.0 Compose file: https://github.com/windmill-labs/windmill/blob/v1.817.0/docker-compose.yml
- Windmill v1.817.0 seeded-user migrations: https://github.com/windmill-labs/windmill/blob/v1.817.0/backend/migrations/20220123221903_first.up.sql and https://github.com/windmill-labs/windmill/blob/v1.817.0/backend/migrations/20220816185849_remove_non_admin_users.up.sql
