---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "0f9eff25a1850ccb008ceb6dfe028342a335a23d2ef93112e35e3caf8bdee585",
  "components": {
    "dify": {
      "name": "Dify documentation",
      "basis": "unknown",
      "sources": {
        "sc63a91c72255": "https://docs.dify.ai/en/self-host/deploy/quick-start/docker-compose",
        "s144cc3f563a1": "https://docs.dify.ai/en/self-host/deploy/configuration/environments",
        "sd5ae6b9492f0": "https://docs.dify.ai/en/api-reference/guides/get-started"
      }
    },
    "dify-console": {
      "name": "Dify console/config source",
      "basis": "d39d9ddb7430522e0c828c6953afdf773ba6e675",
      "sources": {
        "sb28809d177bf": "https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/docker/.env.example",
        "s1e4c822a36b1": "https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/docker/docker-compose.yaml#L573-L644",
        "s1cd4f464c880": "https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/controllers/console/workspace/plugin.py#L567-L585",
        "saa9ceb383427": "https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/controllers/console/workspace/__init__.py#L14-L61",
        "s3998f01569b8": "https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/controllers/common/wraps.py#L11-L32",
        "s39e0b615af71": "https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/configs/enterprise/__init__.py#L38-L41",
        "s5384bb9d1e75": "https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/controllers/console/wraps.py#L308-L321",
        "s7cdbcd9957ac": "https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/controllers/console/wraps.py#L113-L125",
        "s182d16f6e475": "https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/libs/login.py#L47-L59",
        "sf9235e345b51": "https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/libs/login.py#L152-L169",
        "s1edf3fa3d667": "https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/models/account.py#L402-L407",
        "s09ea6abe9b9c": "https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/controllers/console/workspace/plugin.py#L1086-L1106",
        "s662ba88445cd": "https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/controllers/console/workspace/plugin.py#L170-L172",
        "s4b8c82f515c6": "https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/services/plugin/plugin_permission_service.py#L14-L36"
      }
    },
    "dify-compose": {
      "name": "Dify Compose source",
      "basis": "8387590ace4a094de812b7847fc6a4c3a27cd52b",
      "sources": {
        "s517af9c43635": "https://github.com/langgenius/dify/blob/8387590ace4a094de812b7847fc6a4c3a27cd52b/docker/docker-compose.yaml"
      }
    },
    "docker": {
      "name": "Docker",
      "basis": "unknown",
      "sources": {
        "s351180c6678f": "https://docs.docker.com/engine/network/packet-filtering-firewalls/",
        "se716ad33db1f": "https://docs.docker.com/reference/compose-file/merge/",
        "s3e97c2c250b6": "https://docs.docker.com/reference/cli/docker/compose/ps/"
      }
    },
    "certbot": {
      "name": "Dify certbot source",
      "basis": "4c1ad40f8e8a6ee58a958330558f2178b7e47fa7",
      "sources": {
        "sba8e43d56b94": "https://github.com/langgenius/dify/blob/4c1ad40f8e8a6ee58a958330558f2178b7e47fa7/docker/certbot/README.md"
      }
    },
    "flowise": {
      "name": "Flowise documentation",
      "basis": "unknown",
      "sources": {
        "s546a18b65918": "https://docs.flowiseai.com/configuration/authorization/chatflow-level",
        "sfee1ae75d51a": "https://docs.flowiseai.com/configuration/environment-variables",
        "scabc8335d0c7": "https://docs.flowiseai.com/configuration/sso",
        "s23c31010d23d": "https://docs.flowiseai.com/api-reference/prediction",
        "s7b675aa70798": "https://docs.flowiseai.com/configuration/deployment/digital-ocean"
      }
    },
    "flowise-auth": {
      "name": "Flowise account minimum",
      "basis": "v3.0.1",
      "sources": {
        "s6fd9f4266a98": "https://docs.flowiseai.com/configuration/authorization/app-level"
      }
    },
    "flowise-compose": {
      "name": "Flowise Compose",
      "basis": "4ea391204a499fb6d19747104502362295b4dde3",
      "sources": {
        "s81474794a92d": "https://github.com/FlowiseAI/Flowise/blob/4ea391204a499fb6d19747104502362295b4dde3/docker/docker-compose.yml"
      }
    },
    "langflow-compose": {
      "name": "Langflow Compose",
      "basis": "c6dbca308dc85526d5cecb31211821ec4f5e1d05",
      "sources": {
        "s7f4564c949cb": "https://github.com/langflow-ai/langflow/blob/c6dbca308dc85526d5cecb31211821ec4f5e1d05/docker_example/docker-compose.yml"
      }
    },
    "librechat-compose": {
      "name": "LibreChat Compose",
      "basis": "1596df724a840f894831fc74f21de8d8df72fcb1",
      "sources": {
        "sb3cc671b90e3": "https://github.com/danny-avila/LibreChat/blob/1596df724a840f894831fc74f21de8d8df72fcb1/docker-compose.yml"
      }
    },
    "langflow": {
      "name": "Langflow documentation",
      "basis": "unknown",
      "sources": {
        "s5cfeeba4d9b3": "https://docs.langflow.org/api-keys-and-authentication",
        "s885461210e4e": "https://docs.langflow.org/environment-variables",
        "s5a55bdef1f33": "https://docs.langflow.org/deployment-prod-best-practices",
        "sca4ee617805d": "https://docs.langflow.org/security",
        "sec83eaf2b841": "https://docs.langflow.org/authentication-overview"
      }
    },
    "librechat": {
      "name": "LibreChat documentation",
      "basis": "unknown",
      "sources": {
        "s41811a0d442f": "https://www.librechat.ai/docs/configuration/dotenv",
        "s70ac8e7c9504": "https://www.librechat.ai/docs/configuration/authentication",
        "s7896961bc713": "https://www.librechat.ai/docs/configuration/authentication/OAuth2-OIDC",
        "s43fbe74e3c42": "https://www.librechat.ai/docs/configuration/authentication/OAuth2-OIDC/keycloak",
        "s3f1c594392bc": "https://www.librechat.ai/docs/local/docker",
        "s432d72870381": "https://www.librechat.ai/docs/remote/nginx",
        "s9f9e35619ce7": "https://www.librechat.ai/docs/configuration/librechat_yaml/object_structure/actions"
      }
    },
    "librechat-mfa": {
      "name": "LibreChat changelog",
      "basis": "v0.7.7",
      "sources": {
        "s3909883e4681": "https://www.librechat.ai/changelog/v0.7.7"
      }
    },
    "daemon": {
      "name": "Dify plugin daemon",
      "basis": "0.6.10",
      "sources": {
        "scb80ef9b341b": "https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/core/debugging_runtime/server.go#L109-L134",
        "sbb1558888c1a": "https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/core/debugging_runtime/codec.go#L14-L49",
        "s1d0863ded6ed": "https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/core/debugging_runtime/runtime_intialization_handlers.go#L18-L42",
        "sfabe22af22d6": "https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/core/debugging_runtime/hooks.go#L51-L90",
        "sbccc30db5bfe": "https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/core/debugging_runtime/hooks.go#L158-L240",
        "s6490d756c639": "https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/service/debugging_service/connection_key.go#L23-L123",
        "sa0aa7e953ee0": "https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/pkg/utils/cache/redis.go#L208-L230",
        "sa3ee5e4e8a84": "https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/service/install_service/controlpanel.go#L50-L85",
        "s14d062f60b1b": "https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/core/debugging_runtime/io.go#L18-L68",
        "sa3fa1b50ea09": "https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/pkg/entities/requests/tool.go#L27-L36",
        "s8e20b988ea0b": "https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/pkg/entities/requests/model.go#L9-L34",
        "s191317bdf3a7": "https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/types/app/config.go#L101-L106",
        "s32b7d021da01": "https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/core/control_panel/watch_dog.go#L32-L46",
        "sb19f8717ed1f": "https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/server/http_server.go#L130-L134",
        "s2efeb062db27": "https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/core/debugging_runtime/hooks.go#L132-L153"
      }
    },
    "daemon-source": {
      "name": "Dify plugin daemon source",
      "basis": "1310a18b2f6bc6f18768a0a6265484830891433c",
      "sources": {
        "s629f3bfbae72": "https://github.com/langgenius/dify-plugin-daemon/blob/1310a18b2f6bc6f18768a0a6265484830891433c/internal/core/debugging_runtime/hooks.go#L158-L237",
        "s07045a0003da": "https://github.com/langgenius/dify-plugin-daemon/blob/1310a18b2f6bc6f18768a0a6265484830891433c/internal/core/debugging_runtime/runtime_intialization_handlers.go#L44-L75",
        "s2b36558b0078": "https://github.com/langgenius/dify-plugin-daemon/blob/1310a18b2f6bc6f18768a0a6265484830891433c/internal/core/debugging_runtime/runtime_intialization_handlers.go#L139-L183"
      }
    }
  },
  "claims": {
    "flowise-port": {"text": "Flowise PORT defaults 3000; Compose publishes ${PORT}:${PORT}; replace with host-loopback mapping.", "components": ["flowise", "flowise-compose"], "sources": ["flowise:sfee1ae75d51a", "flowise-compose:s81474794a92d"], "status": "REASONED"},
    "langflow-port": {"text": "Langflow defaults port 7860; example Compose publishes 7860:7860 and Postgres 5432:5432; keep database unpublished or private.", "components": ["langflow", "langflow-compose"], "sources": ["langflow:s885461210e4e", "langflow-compose:s7f4564c949cb"], "status": "REASONED"},
    "librechat-port": {"text": "LibreChat defaults 3080; Compose publishes ${PORT}:${PORT} and admin-panel ${ADMIN_PANEL_PORT:-3000}:3000; restrict both.", "components": ["librechat", "librechat-compose"], "sources": ["librechat:s3f1c594392bc", "librechat-compose:sb3cc671b90e3"], "status": "REASONED"},
    "compose-merge": {"text": "Override ports lists merge; !override replaces and !reset clears. Body requires Compose 2.24.4+ for both; Sources does not record that version.", "components": ["docker"], "sources": ["docker:se716ad33db1f"], "status": "REASONED"},
    "docker-firewall": {"text": "Docker published traffic can bypass UFW; removing or narrowing publications is required.", "components": ["docker"], "sources": ["docker:s351180c6678f"], "status": "REASONED"},
    "dify-ports": {"text": "Dify publishes nginx 80/443 and plugin debugging 5003, with more vector-profile ports; EXPOSE_NGINX_SSL_PORT remains published when HTTPS serving is off.", "components": ["dify-console", "dify-compose"], "sources": ["dify-console:sb28809d177bf", "dify-compose:s517af9c43635", "dify-console:s1e4c822a36b1"], "status": "REASONED"},
    "dify-debug-bind": {"text": "Compose pins daemon 0.6.10-local, publishes 5003 on all host interfaces; EXPOSE_PLUGIN_DEBUGGING_HOST is client destination, not bind control.", "components": ["dify-console"], "sources": ["dify-console:s1e4c822a36b1", "dify-console:sb28809d177bf"], "status": "REASONED"},
    "daemon-listener": {"text": "Daemon 0.6.10 uses plaintext newline-delimited JSON TCP; PLUGIN_DEBUGGING_HOST/PORT map to remote-installing listener, default 0.0.0.0:5003.", "components": ["dify-console", "daemon"], "sources": ["dify-console:s1e4c822a36b1", "daemon:scb80ef9b341b", "daemon:sbb1558888c1a", "daemon:sbccc30db5bfe", "daemon:s2efeb062db27"], "status": "REASONED"},
    "daemon-key": {"text": "Per-tenant UUID debugging key has Redis bidirectional mappings with two-hour expiry; retrieval refreshes expiry, not key, and expiry leaves authenticated runtime connected.", "components": ["daemon"], "sources": ["daemon:s6490d756c639", "daemon:sa0aa7e953ee0", "daemon:sfabe22af22d6"], "status": "REASONED"},
    "daemon-rejection": {"text": "Wrong key yields handshake failed, invalid key and closes; lookup is Redis-based and TCP key guessing has no rate limiter.", "components": ["daemon"], "sources": ["daemon:s1d0863ded6ed", "daemon:sfabe22af22d6", "daemon:sbccc30db5bfe"], "status": "REASONED"},
    "daemon-preauth": {"text": "Non-handshake messages can parse/store declarations and buffer assets before authentication.", "components": ["daemon-source"], "sources": ["daemon-source:s629f3bfbae72", "daemon-source:s07045a0003da", "daemon-source:s2b36558b0078"], "status": "REASONED"},
    "daemon-assets": {"text": "Asset limit compares decoded buffered bytes plus incoming base64 string length against 50 MiB; accepted chunks increment decoded length.", "components": ["daemon-source"], "sources": ["daemon-source:s07045a0003da"], "status": "REASONED"},
    "daemon-authority": {"text": "Key holder registers tenant runtime receiving invocation parameters/prompts/credentials and returning results; this alone does not demonstrate host shell execution.", "components": ["daemon"], "sources": ["daemon:sa3ee5e4e8a84", "daemon:s14d062f60b1b", "daemon:sa3fa1b50ea09", "daemon:s8e20b988ea0b"], "status": "REASONED"},
    "debug-key-access": {"text": "Initialized authenticated member with active workspace after setup can GET current workspace debugging-key under documented default permissions.", "components": ["dify-console"], "sources": ["dify-console:s1cd4f464c880", "dify-console:s5384bb9d1e75", "dify-console:s7cdbcd9957ac", "dify-console:s182d16f6e475", "dify-console:sf9235e345b51", "dify-console:saa9ceb383427", "dify-console:s3998f01569b8", "dify-console:s39e0b615af71"], "status": "REASONED"},
    "rbac-default": {"text": "RBAC_ENABLED defaults false and skips enterprise RBAC checks.", "components": ["dify-console"], "sources": ["dify-console:s3998f01569b8", "dify-console:s39e0b615af71"], "status": "REASONED"},
    "plugin-permission": {"text": "No plugin-permission row allows every member; existing row default noone differs, and admins permits only admin/owner.", "components": ["dify-console"], "sources": ["dify-console:saa9ceb383427", "dify-console:s1edf3fa3d667"], "status": "REASONED"},
    "debug-remedy": {"text": "Admin/owner may POST permission/change with debug_permission admins; preserve install_permission, whose omitted value defaults everyone; UI availability unestablished.", "components": ["dify-console"], "sources": ["dify-console:s09ea6abe9b9c", "dify-console:s662ba88445cd", "dify-console:s4b8c82f515c6"], "status": "REASONED"},
    "debug-disable": {"text": "PLUGIN_REMOTE_INSTALLING_ENABLED defaults true; false prevents TCP startup and removes debugging-key route, while ports: !reset [] separately removes publication.", "components": ["daemon", "docker"], "sources": ["daemon:s191317bdf3a7", "daemon:s32b7d021da01", "daemon:sb19f8717ed1f", "docker:se716ad33db1f"], "status": "REASONED"},
    "verify-debug-config": {"text": "Merged Compose should change from published 5003/default-enabled to no publication and explicit false after override and recreation; no Docker/listener demonstration.", "components": ["dify-console", "daemon", "docker"], "sources": ["dify-console:s1e4c822a36b1", "daemon:s191317bdf3a7", "daemon:s32b7d021da01", "daemon:sb19f8717ed1f", "docker:se716ad33db1f"], "status": "REASONED"},
    "flowise-tls": {"text": "Flowise documented TLS uses nginx/certbot upstream localhost:3000; configure NUMBER_OF_PROXIES for real client addresses.", "components": ["flowise"], "sources": ["flowise:s7b675aa70798", "flowise:sfee1ae75d51a"], "status": "REASONED"},
    "librechat-tls": {"text": "LibreChat documented TLS uses nginx upstream localhost:3080; TRUST_PROXY defaults 1 and must match proxy hops.", "components": ["librechat"], "sources": ["librechat:s432d72870381", "librechat:s41811a0d442f"], "status": "REASONED"},
    "langflow-tls": {"text": "LANGFLOW_SSL_CERT_FILE/KEY_FILE enable native TLS; proxy remains a place for login/MFA.", "components": ["langflow"], "sources": ["langflow:s885461210e4e"], "status": "REASONED"},
    "langflow-cookies": {"text": "LANGFLOW_ACCESS_SECURE and LANGFLOW_REFRESH_SECURE default false; enable both behind HTTPS.", "components": ["langflow"], "sources": ["langflow:s885461210e4e"], "status": "REASONED"},
    "dify-tls": {"text": "Certbot challenge/domain/email and fullchain.pem/privkey.pem precede certificate update; enable HTTPS and recreate nginx; default HTTPS false, protocols TLSv1.2 TLSv1.3.", "components": ["certbot", "dify-console"], "sources": ["certbot:sba8e43d56b94", "dify-console:sb28809d177bf"], "status": "REASONED"},
    "dify-urls": {"text": "Set CONSOLE_API_URL, CONSOLE_WEB_URL and APP_WEB_URL to public HTTPS; CONSOLE_API_URL controls HTTPS-only cookies.", "components": ["dify"], "sources": ["dify:s144cc3f563a1"], "status": "REASONED"},
    "dify-bootstrap": {"text": "INIT_PASSWORD defaults empty; set it before first up to gate /install and claim admin privately.", "components": ["dify", "dify-console"], "sources": ["dify:s144cc3f563a1", "dify:sc63a91c72255", "dify-console:sb28809d177bf"], "status": "REASONED"},
    "dify-secret": {"text": "SECRET_KEY signs session/JWT and encrypts stored OAuth credentials; generate random value, or empty auto-generates in storage.", "components": ["dify", "dify-console"], "sources": ["dify:s144cc3f563a1", "dify-console:sb28809d177bf"], "status": "REASONED"},
    "dify-registration": {"text": "ALLOW_REGISTER=false default closes ordinary self-registration, but not invitations or /install bootstrap.", "components": ["dify-console"], "sources": ["dify-console:sb28809d177bf"], "status": "REASONED"},
    "dify-db-redis": {"text": "Replace DB_PASSWORD and REDIS_PASSWORD defaults difyai123456 and update embedded CELERY_BROKER_URL password.", "components": ["dify-console"], "sources": ["dify-console:sb28809d177bf"], "status": "REASONED"},
    "dify-sandbox": {"text": "Replace CODE_EXECUTION_API_KEY/SANDBOX_API_KEY default dify-sandbox together.", "components": ["dify-console"], "sources": ["dify-console:sb28809d177bf"], "status": "REASONED"},
    "dify-plugin-keys": {"text": "Replace PLUGIN_DAEMON_KEY and PLUGIN_DIFY_INNER_API_KEY example service credentials.", "components": ["dify-console"], "sources": ["dify-console:sb28809d177bf"], "status": "REASONED"},
    "dify-agent-keys": {"text": "Replace DIFY_AGENT_API_TOKEN and DIFY_AGENT_SERVER_SECRET_KEY; signing key needs unpadded base64url of 32 random bytes.", "components": ["dify-console"], "sources": ["dify-console:sb28809d177bf"], "status": "REASONED"},
    "dify-weaviate": {"text": "If enabled, rotate WEAVIATE_API_KEY and matching allowed keys; disable anonymous access.", "components": ["dify-console"], "sources": ["dify-console:sb28809d177bf"], "status": "REASONED"},
    "dify-api": {"text": "App Bearer keys are separate from console accounts; create per app and keep calls/keys on the backend.", "components": ["dify"], "sources": ["dify:sd5ae6b9492f0"], "status": "REASONED"},
    "flowise-accounts": {"text": "From v3.0.1, email/password accounts use JWT HTTP-only cookies; old FLOWISE_USERNAME/PASSWORD are deprecated migration settings; claim admin privately.", "components": ["flowise-auth"], "sources": ["flowise-auth:s6fd9f4266a98"], "status": "REASONED"},
    "flowise-secrets": {"text": "Randomize JWT_AUTH_TOKEN_SECRET, JWT_REFRESH_TOKEN_SECRET, EXPRESS_SESSION_SECRET default flowise, and TOKEN_HASH_SECRET; APP_URL defaults localhost:3000.", "components": ["flowise-auth", "flowise"], "sources": ["flowise-auth:s6fd9f4266a98", "flowise:sfee1ae75d51a"], "status": "REASONED"},
    "flowise-encryption": {"text": "FLOWISE_SECRETKEY_OVERWRITE supplies stored-credential encryption key; otherwise it lives under SECRETKEY_PATH.", "components": ["flowise"], "sources": ["flowise:sfee1ae75d51a"], "status": "REASONED"},
    "flowise-prediction": {"text": "Chatflow without assigned key is public by ID; assign per-chatflow API key (DefaultKey is precreated), Bearer requests reject missing key with 401.", "components": ["flowise"], "sources": ["flowise:s546a18b65918", "flowise:s23c31010d23d"], "status": "REASONED"},
    "langflow-auto": {"text": "Application AUTO_LOGIN defaults True, official images false; explicitly disable it, set superuser password other than legacy langflow; username defaults langflow.", "components": ["langflow"], "sources": ["langflow:s5cfeeba4d9b3", "langflow:s885461210e4e"], "status": "REASONED"},
    "langflow-secret": {"text": "Set permanent random LANGFLOW_SECRET_KEY; documented auto-generated key is unsuitable for production.", "components": ["langflow"], "sources": ["langflow:s5a55bdef1f33"], "status": "REASONED"},
    "langflow-signup": {"text": "NEW_USER_IS_ACTIVE defaults False but ENABLE_SIGNUP True; disable signup and keep activation requirement.", "components": ["langflow"], "sources": ["langflow:s885461210e4e"], "status": "REASONED"},
    "langflow-api": {"text": "With auto-login off, POST /api/v1/run/<flow-id> needs x-api-key; create via settings or CLI. SKIP_AUTH_AUTO_LOGIN defaults false, applies only with auto-login and is slated for removal.", "components": ["langflow"], "sources": ["langflow:s5cfeeba4d9b3", "langflow:s885461210e4e"], "status": "REASONED"},
    "langflow-host": {"text": "HOST defaults localhost; bridged containers need 0.0.0.0 plus host-loopback publication and injected env_file/environment. Body labels docs 1.12.x; Sources lacks that pin.", "components": ["langflow", "langflow-compose"], "sources": ["langflow:s885461210e4e", "langflow-compose:s7f4564c949cb"], "status": "REASONED"},
    "librechat-bootstrap": {"text": "First registered user becomes admin; close ALLOW_REGISTRATION after claiming it.", "components": ["librechat"], "sources": ["librechat:s3f1c594392bc", "librechat:s41811a0d442f"], "status": "REASONED"},
    "librechat-sso": {"text": "For SSO-only, disable email login and deliberately enable social registration/login; configure OPENID_* and optional required role with provider allowlist and MFA.", "components": ["librechat"], "sources": ["librechat:s41811a0d442f", "librechat:s70ac8e7c9504", "librechat:s7896961bc713", "librechat:s43fbe74e3c42"], "status": "REASONED"},
    "librechat-secrets": {"text": "CREDS_KEY is 32 bytes, CREDS_IV 16; JWT secrets at least 32 bytes. Blank values bootstrap keys with persistence caveats; retired JWT defaults are refused.", "components": ["librechat"], "sources": ["librechat:s41811a0d442f"], "status": "REASONED"},
    "librechat-urls": {"text": "DOMAIN_CLIENT and DOMAIN_SERVER must use public HTTPS URL.", "components": ["librechat"], "sources": ["librechat:s41811a0d442f", "librechat:s432d72870381"], "status": "REASONED"},
    "mfa": {"text": "Instance-wide native MFA enforcement is not documented; use provider/fronting MFA. Flowise SSO is Enterprise; Langflow offers external JWT/JWKS.", "components": ["flowise", "langflow", "librechat"], "sources": ["flowise:scabc8335d0c7", "langflow:sec83eaf2b841", "librechat:s70ac8e7c9504"], "status": "REASONED"},
    "librechat-mfa": {"text": "v0.7.7 changelog lists two-factor enrolment/backup codes, but checked authentication docs do not establish enforced MFA.", "components": ["librechat-mfa", "librechat"], "sources": ["librechat-mfa:s3909883e4681", "librechat:s70ac8e7c9504"], "status": "REASONED"},
    "containment": {"text": "Treat editor as code/SSRF authority; isolate runtime, limit mounts/privileges and default-deny egress including metadata; rotate exposed provider keys.", "components": ["langflow", "flowise", "librechat", "dify-console"], "sources": ["langflow:sca4ee617805d", "flowise:sfee1ae75d51a", "librechat:s9f9e35619ce7", "dify-console:sb28809d177bf"], "status": "REASONED"},
    "flowise-guards": {"text": "Keep HTTP_SECURITY_CHECK and CUSTOM_MCP_SECURITY_CHECK enabled; disabling MCP check permits arbitrary command execution.", "components": ["flowise"], "sources": ["flowise:sfee1ae75d51a"], "status": "REASONED"},
    "librechat-actions": {"text": "Unset actions.allowedDomains allows public domains with private-target SSRF checks; configured allowlist denies others, and listed private destination grants exception.", "components": ["librechat"], "sources": ["librechat:s9f9e35619ce7"], "status": "REASONED"},
    "dify-ssrf": {"text": "Keep Dify SSRF proxy for sandbox and HTTP-request nodes; HTTP allowlists do not contain arbitrary local tools.", "components": ["dify-console", "dify-compose"], "sources": ["dify-console:sb28809d177bf", "dify-compose:s517af9c43635"], "status": "REASONED"},
    "verify-network": {"text": "Inventory all listeners and actual Publishers; direct TCP 5003 success proves exposure, refusal/timeout needs same-host reachable control and merged-model evidence.", "components": ["dify-console", "daemon", "docker"], "sources": ["dify-console:s1e4c822a36b1", "daemon:s32b7d021da01", "docker:s3e97c2c250b6", "docker:s351180c6678f"], "status": "REASONED", "verify": [1]},
    "verify-editor": {"text": "Curl checks transport only; fresh unauthenticated browser must show login, and /install must be already claimed rather than open admin setup.", "components": ["dify", "flowise-auth", "langflow", "librechat"], "sources": ["dify:sc63a91c72255", "flowise-auth:s6fd9f4266a98", "langflow:s5cfeeba4d9b3", "librechat:s70ac8e7c9504"], "status": "REASONED", "verify": [1]},
    "verify-dify": {"text": "Direct /v1/parameters matched pair expects missing-Bearer 401 and valid-key parameters 200; app_unavailable 400 is inconclusive; bundled nginx is not strict api-service attribution.", "components": ["dify"], "sources": ["dify:sd5ae6b9492f0"], "status": "REASONED", "verify": [1]},
    "verify-flowise": {"text": "Assigned-key chatflow prediction must reject missing key and return real output with valid Bearer key; keyless flow is public.", "components": ["flowise"], "sources": ["flowise:s546a18b65918", "flowise:s23c31010d23d"], "status": "REASONED", "verify": [1]},
    "verify-langflow": {"text": "Run API must reject absent x-api-key and return real output with valid key; routing, transport or validation errors are inconclusive.", "components": ["langflow"], "sources": ["langflow:s5cfeeba4d9b3"], "status": "REASONED", "verify": [1]}
  }
}
---
# Agent and workflow builders: Dify, Flowise, Langflow, LibreChat

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| flowise-port: Flowise PORT defaults 3000; Compose publishes ${PORT}:${PORT}; replace with host-loopback mapping. | Flowise documentation unknown; Flowise Compose 4ea391204a499fb6d19747104502362295b4dde3 | REASONED |
| langflow-port: Langflow defaults port 7860; example Compose publishes 7860:7860 and Postgres 5432:5432; keep database unpublished or private. | Langflow documentation unknown; Langflow Compose c6dbca308dc85526d5cecb31211821ec4f5e1d05 | REASONED |
| librechat-port: LibreChat defaults 3080; Compose publishes ${PORT}:${PORT} and admin-panel ${ADMIN_PANEL_PORT:-3000}:3000; restrict both. | LibreChat documentation unknown; LibreChat Compose 1596df724a840f894831fc74f21de8d8df72fcb1 | REASONED |
| compose-merge: Override ports lists merge; !override replaces and !reset clears. Body requires Compose 2.24.4+ for both; Sources does not record that version. | Docker unknown | REASONED |
| docker-firewall: Docker published traffic can bypass UFW; removing or narrowing publications is required. | Docker unknown | REASONED |
| dify-ports: Dify publishes nginx 80/443 and plugin debugging 5003, with more vector-profile ports; EXPOSE_NGINX_SSL_PORT remains published when HTTPS serving is off. | Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675; Dify Compose source 8387590ace4a094de812b7847fc6a4c3a27cd52b | REASONED |
| dify-debug-bind: Compose pins daemon 0.6.10-local, publishes 5003 on all host interfaces; EXPOSE_PLUGIN_DEBUGGING_HOST is client destination, not bind control. | Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675 | REASONED |
| daemon-listener: Daemon 0.6.10 uses plaintext newline-delimited JSON TCP; PLUGIN_DEBUGGING_HOST/PORT map to remote-installing listener, default 0.0.0.0:5003. | Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675; Dify plugin daemon 0.6.10 | REASONED |
| daemon-key: Per-tenant UUID debugging key has Redis bidirectional mappings with two-hour expiry; retrieval refreshes expiry, not key, and expiry leaves authenticated runtime connected. | Dify plugin daemon 0.6.10 | REASONED |
| daemon-rejection: Wrong key yields handshake failed, invalid key and closes; lookup is Redis-based and TCP key guessing has no rate limiter. | Dify plugin daemon 0.6.10 | REASONED |
| daemon-preauth: Non-handshake messages can parse/store declarations and buffer assets before authentication. | Dify plugin daemon source 1310a18b2f6bc6f18768a0a6265484830891433c | REASONED |
| daemon-assets: Asset limit compares decoded buffered bytes plus incoming base64 string length against 50 MiB; accepted chunks increment decoded length. | Dify plugin daemon source 1310a18b2f6bc6f18768a0a6265484830891433c | REASONED |
| daemon-authority: Key holder registers tenant runtime receiving invocation parameters/prompts/credentials and returning results; this alone does not demonstrate host shell execution. | Dify plugin daemon 0.6.10 | REASONED |
| debug-key-access: Initialized authenticated member with active workspace after setup can GET current workspace debugging-key under documented default permissions. | Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675 | REASONED |
| rbac-default: RBAC_ENABLED defaults false and skips enterprise RBAC checks. | Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675 | REASONED |
| plugin-permission: No plugin-permission row allows every member; existing row default noone differs, and admins permits only admin/owner. | Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675 | REASONED |
| debug-remedy: Admin/owner may POST permission/change with debug_permission admins; preserve install_permission, whose omitted value defaults everyone; UI availability unestablished. | Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675 | REASONED |
| debug-disable: PLUGIN_REMOTE_INSTALLING_ENABLED defaults true; false prevents TCP startup and removes debugging-key route, while ports: !reset [] separately removes publication. | Dify plugin daemon 0.6.10; Docker unknown | REASONED |
| verify-debug-config: Merged Compose should change from published 5003/default-enabled to no publication and explicit false after override and recreation; no Docker/listener demonstration. | Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675; Dify plugin daemon 0.6.10; Docker unknown | REASONED |
| flowise-tls: Flowise documented TLS uses nginx/certbot upstream localhost:3000; configure NUMBER_OF_PROXIES for real client addresses. | Flowise documentation unknown | REASONED |
| librechat-tls: LibreChat documented TLS uses nginx upstream localhost:3080; TRUST_PROXY defaults 1 and must match proxy hops. | LibreChat documentation unknown | REASONED |
| langflow-tls: LANGFLOW_SSL_CERT_FILE/KEY_FILE enable native TLS; proxy remains a place for login/MFA. | Langflow documentation unknown | REASONED |
| langflow-cookies: LANGFLOW_ACCESS_SECURE and LANGFLOW_REFRESH_SECURE default false; enable both behind HTTPS. | Langflow documentation unknown | REASONED |
| dify-tls: Certbot challenge/domain/email and fullchain.pem/privkey.pem precede certificate update; enable HTTPS and recreate nginx; default HTTPS false, protocols TLSv1.2 TLSv1.3. | Dify certbot source 4c1ad40f8e8a6ee58a958330558f2178b7e47fa7; Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675 | REASONED |
| dify-urls: Set CONSOLE_API_URL, CONSOLE_WEB_URL and APP_WEB_URL to public HTTPS; CONSOLE_API_URL controls HTTPS-only cookies. | Dify documentation unknown | REASONED |
| dify-bootstrap: INIT_PASSWORD defaults empty; set it before first up to gate /install and claim admin privately. | Dify documentation unknown; Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675 | REASONED |
| dify-secret: SECRET_KEY signs session/JWT and encrypts stored OAuth credentials; generate random value, or empty auto-generates in storage. | Dify documentation unknown; Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675 | REASONED |
| dify-registration: ALLOW_REGISTER=false default closes ordinary self-registration, but not invitations or /install bootstrap. | Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675 | REASONED |
| dify-db-redis: Replace DB_PASSWORD and REDIS_PASSWORD defaults difyai123456 and update embedded CELERY_BROKER_URL password. | Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675 | REASONED |
| dify-sandbox: Replace CODE_EXECUTION_API_KEY/SANDBOX_API_KEY default dify-sandbox together. | Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675 | REASONED |
| dify-plugin-keys: Replace PLUGIN_DAEMON_KEY and PLUGIN_DIFY_INNER_API_KEY example service credentials. | Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675 | REASONED |
| dify-agent-keys: Replace DIFY_AGENT_API_TOKEN and DIFY_AGENT_SERVER_SECRET_KEY; signing key needs unpadded base64url of 32 random bytes. | Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675 | REASONED |
| dify-weaviate: If enabled, rotate WEAVIATE_API_KEY and matching allowed keys; disable anonymous access. | Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675 | REASONED |
| dify-api: App Bearer keys are separate from console accounts; create per app and keep calls/keys on the backend. | Dify documentation unknown | REASONED |
| flowise-accounts: From v3.0.1, email/password accounts use JWT HTTP-only cookies; old FLOWISE_USERNAME/PASSWORD are deprecated migration settings; claim admin privately. | Flowise account minimum v3.0.1 | REASONED |
| flowise-secrets: Randomize JWT_AUTH_TOKEN_SECRET, JWT_REFRESH_TOKEN_SECRET, EXPRESS_SESSION_SECRET default flowise, and TOKEN_HASH_SECRET; APP_URL defaults localhost:3000. | Flowise account minimum v3.0.1; Flowise documentation unknown | REASONED |
| flowise-encryption: FLOWISE_SECRETKEY_OVERWRITE supplies stored-credential encryption key; otherwise it lives under SECRETKEY_PATH. | Flowise documentation unknown | REASONED |
| flowise-prediction: Chatflow without assigned key is public by ID; assign per-chatflow API key (DefaultKey is precreated), Bearer requests reject missing key with 401. | Flowise documentation unknown | REASONED |
| langflow-auto: Application AUTO_LOGIN defaults True, official images false; explicitly disable it, set superuser password other than legacy langflow; username defaults langflow. | Langflow documentation unknown | REASONED |
| langflow-secret: Set permanent random LANGFLOW_SECRET_KEY; documented auto-generated key is unsuitable for production. | Langflow documentation unknown | REASONED |
| langflow-signup: NEW_USER_IS_ACTIVE defaults False but ENABLE_SIGNUP True; disable signup and keep activation requirement. | Langflow documentation unknown | REASONED |
| langflow-api: With auto-login off, POST /api/v1/run/&lt;flow-id&gt; needs x-api-key; create via settings or CLI. SKIP_AUTH_AUTO_LOGIN defaults false, applies only with auto-login and is slated for removal. | Langflow documentation unknown | REASONED |
| langflow-host: HOST defaults localhost; bridged containers need 0.0.0.0 plus host-loopback publication and injected env_file/environment. Body labels docs 1.12.x; Sources lacks that pin. | Langflow documentation unknown; Langflow Compose c6dbca308dc85526d5cecb31211821ec4f5e1d05 | REASONED |
| librechat-bootstrap: First registered user becomes admin; close ALLOW_REGISTRATION after claiming it. | LibreChat documentation unknown | REASONED |
| librechat-sso: For SSO-only, disable email login and deliberately enable social registration/login; configure OPENID_* and optional required role with provider allowlist and MFA. | LibreChat documentation unknown | REASONED |
| librechat-secrets: CREDS_KEY is 32 bytes, CREDS_IV 16; JWT secrets at least 32 bytes. Blank values bootstrap keys with persistence caveats; retired JWT defaults are refused. | LibreChat documentation unknown | REASONED |
| librechat-urls: DOMAIN_CLIENT and DOMAIN_SERVER must use public HTTPS URL. | LibreChat documentation unknown | REASONED |
| mfa: Instance-wide native MFA enforcement is not documented; use provider/fronting MFA. Flowise SSO is Enterprise; Langflow offers external JWT/JWKS. | Flowise documentation unknown; Langflow documentation unknown; LibreChat documentation unknown | REASONED |
| librechat-mfa: v0.7.7 changelog lists two-factor enrolment/backup codes, but checked authentication docs do not establish enforced MFA. | LibreChat changelog v0.7.7; LibreChat documentation unknown | REASONED |
| containment: Treat editor as code/SSRF authority; isolate runtime, limit mounts/privileges and default-deny egress including metadata; rotate exposed provider keys. | Langflow documentation unknown; Flowise documentation unknown; LibreChat documentation unknown; Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675 | REASONED |
| flowise-guards: Keep HTTP_SECURITY_CHECK and CUSTOM_MCP_SECURITY_CHECK enabled; disabling MCP check permits arbitrary command execution. | Flowise documentation unknown | REASONED |
| librechat-actions: Unset actions.allowedDomains allows public domains with private-target SSRF checks; configured allowlist denies others, and listed private destination grants exception. | LibreChat documentation unknown | REASONED |
| dify-ssrf: Keep Dify SSRF proxy for sandbox and HTTP-request nodes; HTTP allowlists do not contain arbitrary local tools. | Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675; Dify Compose source 8387590ace4a094de812b7847fc6a4c3a27cd52b | REASONED |
| verify-network: Inventory all listeners and actual Publishers; direct TCP 5003 success proves exposure, refusal/timeout needs same-host reachable control and merged-model evidence. | Dify console/config source d39d9ddb7430522e0c828c6953afdf773ba6e675; Dify plugin daemon 0.6.10; Docker unknown | REASONED |
| verify-editor: Curl checks transport only; fresh unauthenticated browser must show login, and /install must be already claimed rather than open admin setup. | Dify documentation unknown; Flowise account minimum v3.0.1; Langflow documentation unknown; LibreChat documentation unknown | REASONED |
| verify-dify: Direct /v1/parameters matched pair expects missing-Bearer 401 and valid-key parameters 200; app_unavailable 400 is inconclusive; bundled nginx is not strict api-service attribution. | Dify documentation unknown | REASONED |
| verify-flowise: Assigned-key chatflow prediction must reject missing key and return real output with valid Bearer key; keyless flow is public. | Flowise documentation unknown | REASONED |
| verify-langflow: Run API must reject absent x-api-key and return real output with valid key; routing, transport or validation errors are inconclusive. | Langflow documentation unknown | REASONED |
<!-- version-basis:end -->

Each of these tools stores your provider API keys (OpenAI, Anthropic, and the rest) and exposes both an editor UI and callable APIs, so an open instance is a secrets vault plus free compute for whoever finds it. All four ship with login of some kind; the exposure comes from skipping the first-run setup, leaving default secrets in place, and publishing the container port on every interface over plain HTTP. And because each one runs user-authored flows with custom-code and HTTP-request/tool nodes, the editor is effectively code-execution and server-side-request authority on the host, so authentication decides who gets in but does not contain what a flow can then run or reach (section 8, [egress-metadata.md](egress-metadata.md)). None of them offers a native second factor that this guide can rely on, so MFA comes from an OIDC provider (where the tool supports OIDC) or from the fronting layer ([mfa.md](mfa.md)).

## 1. Bind privately

Publish the container on loopback and let a proxy or tunnel be the only public listener ([docker.md](docker.md)). This belongs in the service's own Compose file. If you put it in an override file beside a vendor Compose file instead, it will not replace what that file publishes: an override `ports` list merges with the base list, so use the `!reset` form shown for Dify below.

```yaml
ports:
  - "127.0.0.1:3000:3000"    # Flowise (PORT defaults to 3000)
  - "127.0.0.1:7860:7860"    # Langflow (LANGFLOW_PORT defaults to 7860)
  - "127.0.0.1:3080:3080"    # LibreChat (PORT defaults to 3080)
```

Those three also ship an official Compose file that publishes the app port on all interfaces by default (`${PORT}:${PORT}` for Flowise and LibreChat, `7860:7860` for Langflow), and LibreChat's is meant to be extended through a `docker-compose.override.yaml` rather than edited; LibreChat's file also publishes an `admin-panel` on `${ADMIN_PANEL_PORT:-3000}:3000`, so treat that mapping the same way. An override `ports` list merges with the base list, so a loopback entry added beside a base `${PORT}:${PORT}` leaves the base publication in place; move a port to loopback by replacing the list with `ports: !override ["127.0.0.1:3000:3000"]` (using the tool's own port), which supersedes the base (`!override` needs Docker Compose 2.24.4 or newer and `!reset` a little earlier, so treat 2.24.4+ as the prerequisite for both; check `docker compose version`). The `!reset []` form used for Dify below does a different job: it clears a publication a service should not have at all, rather than moving one to loopback. Langflow's example Compose also publishes PostgreSQL on `5432:5432` beside the app; leave that backing store unpublished on the Compose network or loopback-scope it, as shown in [ai-infra-services.md](ai-infra-services.md).

Dify is different: its Compose file publishes nginx on `EXPOSE_NGINX_PORT=80` and `EXPOSE_NGINX_SSL_PORT=443` from `docker/.env`, plus the plugin daemon's `EXPOSE_PLUGIN_DEBUGGING_PORT=5003` (optional vector store profiles publish more). Do not hide a published port with the host firewall: Docker's NAT rules divert the traffic before it reaches the chains UFW uses, so a UFW deny on a published port does nothing ([docker.md](docker.md)). The plugin daemon's debugging port is only needed for remote plugin debugging. The checked Compose file pins `langgenius/dify-plugin-daemon:0.6.10-local` and unconditionally publishes `${EXPOSE_PLUGIN_DEBUGGING_PORT:-5003}:${PLUGIN_DEBUGGING_PORT:-5003}`, with no host address by default, so Docker publishes port 5003 on every host interface. `EXPOSE_PLUGIN_DEBUGGING_HOST=localhost` does not restrict that bind; it only tells the plugin client where to connect. Remove the publication with an override file (see below). Leave the backend services unpublished on the Compose network, and make Dify's nginx the only service with a public port: either as the TLS edge (section 2) or on loopback (`EXPOSE_NGINX_PORT=127.0.0.1:8080`) behind your own proxy. The Compose file publishes `EXPOSE_NGINX_SSL_PORT` as well, and unconditionally, so give that the same host address too. Turning `NGINX_HTTPS_ENABLED` off does not help: it stops nginx serving TLS, it does not remove Docker's publication, which is the same trap as the plugin daemon's port above. The same shape appears in other AI-infrastructure deployments, where an authenticated front door sits beside a published backing store; [ai-infra-services.md](ai-infra-services.md) documents it.


At daemon 0.6.10, this is a plain TCP channel carrying newline-delimited JSON, with no TLS. Compose maps `PLUGIN_DEBUGGING_HOST` (default `0.0.0.0`) and `PLUGIN_DEBUGGING_PORT` (default `5003`) to the daemon's `PLUGIN_REMOTE_INSTALLING_HOST` and `PLUGIN_REMOTE_INSTALLING_PORT`; these control the listener inside the container. Its handshake authenticates a per-tenant debugging key, generated with `uuid.New().String()` and stored in Redis as tenant-to-key and key-to-tenant mappings. Both mappings expire after two hours; retrieving an existing key returns the same key and refreshes both expiries, rather than rotating it. Expiry does not disconnect an already authenticated runtime. A wrong key gets `handshake failed, invalid key` and the connection closes. The key is checked by Redis lookup, not a constant-time secret comparison, and this TCP path has no rate limiter for key guesses. However, `onMessage` does not require a successful handshake before dispatching non-handshake messages: an unauthenticated connection can have plugin declarations parsed and stored in its runtime, and asset chunks buffered. The per-connection asset check rejects buffered decoded bytes plus the incoming chunk's base64 string length above `50 * 1024 * 1024` bytes (50 MiB); accepted chunks add their decoded length to the counter. The key gates registration into its tenant, not message processing on this listener, so an exposed port 5003 is not inert to a keyless client.

A key holder can register a remote plugin runtime into the key's tenant by supplying its declarations and assets. When Dify invokes that runtime, it receives the tool parameters or model prompts and any credentials included in those requests, and supplies the results. Treat the key as authority to supply remotely executed plugin code to the tenant's workflows; the plugin code runs at the connector, and this channel alone does not demonstrate shell execution on the Dify host. Keep the channel private even though its handshake uses a key.

Who can obtain a key: after instance setup, any initialized member with an active workspace and a valid console session can retrieve the current workspace's key, with the debugging host and port, through `GET /console/api/workspaces/current/plugin/debugging-key` at Dify commit `d39d9ddb7430522e0c828c6953afdf773ba6e675` under the defaults below. Enterprise RBAC (`RBAC_ENABLED`) defaults to false, which skips its check. The plugin-permission check then allows every member when the workspace has no plugin-permission record, and refuses only when the workspace's debug permission is set to nobody, or to admins for an account that is neither admin nor owner. The model's default `debug_permission` is `noone`, but it applies only once a row exists; with no row, everyone is allowed. By default, therefore, a member meeting those session and workspace prerequisites can retrieve the key and register a remote runtime. Where plugin debugging is needed, an admin or owner can set `debug_permission` to `admins` through the API `POST /console/api/workspaces/current/plugin/permission/change`, preserving the current `install_permission` in the request as well (omitting it defaults it to `everyone`). This is an API remedy; UI availability was not established. Otherwise disable the listener as described below.

Set `PLUGIN_REMOTE_INSTALLING_ENABLED=false` in the `plugin_daemon` container environment when debugging is unused. This setting defaults to `true`; `false` prevents the TCP debugging server from starting and removes the daemon's debugging-key API route. It does not remove Docker's port publication. The override below disables the server and removes the publication together.

```yaml
# docker-compose.override.yaml, beside docker-compose.yaml; plain `docker compose up -d` picks it up
services:
  plugin_daemon:
    environment:
      PLUGIN_REMOTE_INSTALLING_ENABLED: "false"
    ports: !reset []   # an ordinary ports list would merge with the base file's list, not replace it
```

**REASONED, not demonstrated:** the authoring host forbids opening listeners without an isolated network namespace, and has none; Docker is unavailable. Confirm the result against the merged model with `docker compose config`: without the override, expect the base host publication on port 5003 and no `PLUGIN_REMOTE_INSTALLING_ENABLED` entry (the daemon defaults it to `true`); with the override, expect `PLUGIN_REMOTE_INSTALLING_ENABLED: "false"` and no published port for `plugin_daemon`. Recreate the service with `docker compose up -d --force-recreate plugin_daemon`: the default starts the TCP listener, whereas `false` prevents its startup and removes the daemon debugging-key route. The switch alone leaves the Compose publication in place. These expectations follow the pinned Compose file, daemon startup and route conditions, and Docker [reset semantics](https://docs.docker.com/reference/compose-file/merge/#reset-value), cited in Sources.

## 2. TLS

Flowise and LibreChat document no TLS of their own; their deployment guides put nginx with certbot in front (`proxy_pass http://localhost:3000` and `http://localhost:3080` respectively). Use [caddy.md](caddy.md) or [nginx.md](nginx.md) with a certificate from [free-certificates.md](free-certificates.md), or [cloudflare.md](cloudflare.md) / [tailscale.md](tailscale.md) with no public port at all. Set `NUMBER_OF_PROXIES` (Flowise) and `TRUST_PROXY` (LibreChat, default `1`) to the number of proxy hops so rate limiting sees client addresses.

Langflow can terminate TLS itself with `LANGFLOW_SSL_CERT_FILE` and `LANGFLOW_SSL_KEY_FILE`; a fronting proxy remains the simpler place to add login and MFA. Behind HTTPS, also set `LANGFLOW_ACCESS_SECURE=true` and `LANGFLOW_REFRESH_SECURE=true`: both default to `false`, so the access and refresh session cookies are issued without the `Secure` flag until you do.

Dify's bundled nginx can terminate TLS. In `docker/.env`, per the certbot README in the Dify repository: set `NGINX_ENABLE_CERTBOT_CHALLENGE=true`, `CERTBOT_DOMAIN`, `CERTBOT_EMAIL`, `NGINX_SSL_CERT_FILENAME=fullchain.pem`, `NGINX_SSL_CERT_KEY_FILENAME=privkey.pem`; run `docker compose --profile certbot up --force-recreate -d` and `docker compose exec -it certbot /bin/sh /update-cert.sh`; then set `NGINX_HTTPS_ENABLED=true` (default `false`) and recreate nginx with `docker compose --profile certbot up -d --no-deps --force-recreate nginx`. `NGINX_SSL_PROTOCOLS` defaults to `TLSv1.2 TLSv1.3`. Set `CONSOLE_API_URL`, `CONSOLE_WEB_URL`, and `APP_WEB_URL` to the public `https://` URLs; per the Dify reference, `CONSOLE_API_URL` decides whether cookies are marked HTTPS-only.

## 3. Dify

```bash
cd dify/docker && cp .env.example .env
# edit .env now: INIT_PASSWORD, SECRET_KEY, the default service credentials (next bullet), the EXPOSE_* bindings (section 1), the public URLs (section 2)
docker compose up -d
```

- `INIT_PASSWORD=REPLACE_WITH_LONG_RANDOM_VALUE` goes into `.env` before the first `up`. It is empty by default; when set, the `/install` page demands it before anyone can create the admin account. Once the stack is up, open `https://dify.example.com/install` yourself, immediately.
- Set `SECRET_KEY` from `openssl rand -base64 42`. It signs session cookies and JWTs and encrypts stored OAuth credentials (left empty, Dify auto-generates one in its storage directory, per `.env.example`).
- Console self-registration is off by default (`ALLOW_REGISTER=false`); leave it false for an invite-only console and add members by invitation. This governs ordinary self-registration AFTER setup: workspace invitations and the `/install` setup wizard always work regardless, so the protection for an unclaimed install is still `INIT_PASSWORD` plus claiming `/install` privately (above), not this switch.
- Replace the shipped SERVICE credentials in `.env`, not just `SECRET_KEY`: `docker/.env.example` ships working defaults that authenticate Dify's internal services, and `SECRET_KEY` (empty, auto-generated) does not cover them. Change `DB_PASSWORD` and `REDIS_PASSWORD` (both `difyai123456`; `CELERY_BROKER_URL` embeds the Redis password, so update it in lockstep), the sandbox pair `CODE_EXECUTION_API_KEY`/`SANDBOX_API_KEY` (both `dify-sandbox`, keep them equal), `PLUGIN_DAEMON_KEY` and `PLUGIN_DIFY_INNER_API_KEY`, and the agent keys `DIFY_AGENT_API_TOKEN` and `DIFY_AGENT_SERVER_SECRET_KEY` (the last one's known default lets anyone forge agent tokens; replace it with unpadded base64url of 32 random bytes). If you enable the Weaviate vector store, also rotate `WEAVIATE_API_KEY` together with `WEAVIATE_AUTHENTICATION_APIKEY_ALLOWED_KEYS` and turn off `WEAVIATE_AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED`.
- App API keys are created inside each app and sent as `Authorization: Bearer <key>` to the service API. They are not console accounts, so tightening console login does nothing for a leaked key. Dify's guidance: call the API from your backend only; a key in frontend code can be extracted.

## 4. Flowise

- From v3.0.1 onwards Flowise uses email-and-password accounts with JWTs in HTTP-only cookies. `FLOWISE_USERNAME` / `FLOWISE_PASSWORD` are documented as deprecated; the docs use them only to migrate an older instance into a new admin account. Register the admin account before exposing the instance.
- Set random values for `JWT_AUTH_TOKEN_SECRET`, `JWT_REFRESH_TOKEN_SECRET`, `EXPRESS_SESSION_SECRET` (default `flowise`), and `TOKEN_HASH_SECRET`; set `APP_URL` to the public URL (default `http://localhost:3000`). `FLOWISE_SECRETKEY_OVERWRITE` sets the key that encrypts stored credentials; without it the key lives in a file under `SECRETKEY_PATH`.
- Prediction endpoints: a chatflow with no API key assigned is public to anyone who knows the chatflow ID. Create keys under **API Keys** (a `DefaultKey` is pre-created), assign one per chatflow, and clients send `Authorization: Bearer <key>`; the prediction API answers `401` without it.

## 5. Langflow

```
LANGFLOW_AUTO_LOGIN=false
LANGFLOW_SUPERUSER=REPLACE_WITH_ADMIN_USERNAME
LANGFLOW_SUPERUSER_PASSWORD=REPLACE_WITH_LONG_RANDOM_VALUE
LANGFLOW_SECRET_KEY=REPLACE_WITH_LONG_RANDOM_VALUE
```

- `LANGFLOW_AUTO_LOGIN` defaults to `True` in the application (the official Docker images set it to `false`), which means no login at all; set it to `false` explicitly. The password is then required and cannot be the legacy default `langflow`; the username defaults to `langflow`.
- Generate the key with `python3 -c "from secrets import token_urlsafe; print(f'LANGFLOW_SECRET_KEY={token_urlsafe(32)}')"`. An auto-generated key is documented as unsuitable for production.
- `LANGFLOW_NEW_USER_IS_ACTIVE` defaults to `False`, so a new account waits for superuser activation, but public signup is still OPEN by default (`ENABLE_SIGNUP` is `True`), letting inactive accounts accumulate; set `LANGFLOW_ENABLE_SIGNUP=false` to close registration outright and keep `LANGFLOW_NEW_USER_IS_ACTIVE=False` as the backstop.
- With auto-login off, API calls (`POST /api/v1/run/<flow-id>`) need a Langflow API key in the `x-api-key` header, created under **Settings > Langflow API Keys** or with `langflow api-key`. `LANGFLOW_SKIP_AUTH_AUTO_LOGIN` (default `false`) only applies when auto-login is on and is slated for removal; leave it alone.
- `LANGFLOW_HOST` defaults to `localhost`, which is right only when Langflow runs directly on the host behind a same-host proxy; INSIDE a bridged Docker container `localhost` binds the container's own loopback, so a host proxy hitting the published port reaches nothing. In a container set `LANGFLOW_HOST=0.0.0.0` and publish to host loopback (`127.0.0.1:7860:7860`, section 1). These `LANGFLOW_*` settings must also be injected into the container through Compose (`env_file:` or `environment:`), not merely written to a `.env` the app never reads. Version note: checked against the 1.12.x docs.

## 6. LibreChat

- The first registered account becomes the admin. Register it, then set `ALLOW_REGISTRATION=false` so nobody else can create an email account. For SSO-only operation, also set `ALLOW_EMAIL_LOGIN=false` and enable `ALLOW_SOCIAL_REGISTRATION=true` deliberately, with the provider's allowlist deciding who may exist.
- `ALLOW_SOCIAL_LOGIN=true` enables the OAuth2 providers (Apple, Discord, Facebook, GitHub, Google) and OIDC through `OPENID_ISSUER`, `OPENID_CLIENT_ID`, `OPENID_CLIENT_SECRET`, `OPENID_SESSION_SECRET`, `OPENID_SCOPE="openid profile email"`, `OPENID_CALLBACK_URL=/oauth/openid/callback`, optionally `OPENID_REQUIRED_ROLE`. The docs cover Keycloak, Authentik, Authelia, Auth0, Cognito, and Entra; with OIDC in place, set `ALLOW_EMAIL_LOGIN=false` and enforce MFA at the provider ([identity-providers.md](identity-providers.md), [oidc-integration.md](oidc-integration.md)).
- `CREDS_KEY` is a 32-byte key (64 hexadecimal characters) and `CREDS_IV` a 16-byte IV (32 hexadecimal characters); `JWT_SECRET` and `JWT_REFRESH_SECRET` are unique random values of at least 32 bytes each. The docs point to the Credentials Generator. The current `.env.example` leaves these blank (a missing value makes LibreChat bootstrap a random key, persisted only if it can write and keep its credentials file, otherwise process-local and lost on restart), and it refuses to start if you paste a retired published `JWT_SECRET`/`JWT_REFRESH_SECRET` default; set your own permanent production values so the secrets are known, backed up, and stable across restarts.
- Set `DOMAIN_CLIENT` and `DOMAIN_SERVER` to the public `https://` URL. TLS comes from the fronting proxy (section 2).
- The v0.7.7 changelog lists two-factor authentication with backup codes and QR enrolment, but the authentication documentation we checked does not describe it, so do not count on it as the enforced control; MFA at the OIDC provider is the documented path.

## 7. MFA and stored secrets

None of the four documents instance-wide MFA enforcement. Where OIDC exists (LibreChat), enforce MFA at the provider; for Dify, Flowise, and Langflow put the editor behind Cloudflare Access or an identity layer per [mfa.md](mfa.md). Flowise's native SSO is Enterprise-plan only and Langflow documents external JWT/JWKS identity integration, but on the open-source editions the fronting layer is the dependable path. Every provider key pasted into these tools is a secret held by the tool; rotate any key that lived on an instance that was ever open ([secrets.md](secrets.md)).

## 8. Contain what the builder can execute and reach

Authentication decides who gets in; it does not limit what a flow does once inside. All four run
custom code and outbound HTTP from the flow itself, so treat the editor as code-execution and SSRF
authority and contain it at the infrastructure layer, not with login alone:

- **Isolate the runtime**: one container or VM per builder, a non-root user, a read-only root
  filesystem where the tool supports it, and no host mount it does not need ([docker.md](docker.md)).
- **Default-deny egress**: permit only DNS and the provider APIs the flows actually call, and block
  the cloud metadata address so a flow cannot mint the instance's cloud credentials
  ([egress-metadata.md](egress-metadata.md)).
- **Keep each tool's own guards on**: Flowise's `HTTP_SECURITY_CHECK` and `CUSTOM_MCP_SECURITY_CHECK`
  (the docs warn that disabling the MCP check "allows arbitrary command execution"); LibreChat
  Actions' domain allowlist, which you must CONFIGURE (`actions.allowedDomains` in `librechat.yaml`): left unset its built-in SSRF checks block private targets but every other domain is allowed, and only once you set the allowlist are unlisted domains denied (listing a private destination grants it an exception); Dify's
  SSRF proxy in front of the code-sandbox and HTTP-request nodes. An HTTP allowlist is not containment
  of an arbitrary local tool, so pair it with the egress and isolation controls above.

## Verify

**REASONED Dify publication and port 5003 checks, not demonstrated:** the authoring host forbids opening listeners without an isolated network namespace, and has none; Docker is unavailable. With the default listener enabled and published, expect a successful outside TCP connection; after the section 1 override and recreation, expect no host publication and a refusal or timeout, with a successful same-host positive control as described below. These outcomes follow the pinned Compose publication and daemon startup condition, Docker [reset semantics](https://docs.docker.com/reference/compose-file/merge/#reset-value), and the [Publishers fields](https://docs.docker.com/reference/cli/docker/compose/ps/). The port 5003 probe tests TCP reachability, not debugging-key authentication. A successful connection proves exposure even if a later handshake would reject a key. Disabling the listener alone also cannot prove that Docker's publication was removed; check the merged Compose model and Publishers entries as well.

```bash
# REASONED: listener inventory, Dify publication and TCP checks follow the cited pinned Compose,
# daemon startup and Docker sources; no isolated network namespace or Docker is available here.
ss -tlnp                                        # read the whole list: app ports on 127.0.0.1; 80/443
                                                # public only where Dify's own nginx is the TLS edge.
                                                # A container port published by DNAT need not appear
                                                # here at all, so this list cannot clear 5003 by itself
# REASONED Dify publication check: the authoring host forbids opening listeners without an isolated
# network namespace, and has none; Docker is unavailable. Base: expect PublishedPort 5003 on
# plugin_daemon; after !reset and recreation: no host mapping. See the Compose and ps sources.
docker compose ps --format json                 # run in dify/docker: no Publishers entry on the
                                                # plugin_daemon service may map it to a host port.
                                                # Read the entries rather than the array's length:
                                                # a merely exposed container port can appear too. A grep for
                                                # "published" cannot say which service published it
# REASONED Dify TCP check: the authoring host forbids opening listeners without an isolated network
# namespace, and has none; Docker is unavailable. Default enabled/published: expect connection success;
# section 1 override and recreation: refusal/timeout with the positive control succeeding.
# See the pinned Compose publication and daemon startup sources.
(                                               # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
    *) nc -vz -w 3 "$1" 5003 ;;                # from an outside network, and the authority here:
  esac
)
                                                # EXPOSE_PLUGIN_DEBUGGING_PORT can move it, so the ps output above is the authority on which port to probe
# a refusal or timeout from YOUR address is the pass ONLY if your packets reach the host at all: as a
# positive control, nc -vz -w 3 the same address on a port you know is open (your TLS edge, 443) and
# confirm THAT succeeds; if the control also times out the path is filtered and the 5003 result is
# inconclusive (the port could still be open from another network). A local error, an unsupported
# option (BusyBox netcat rejects -v), or exit 1 with no output is inconclusive: nothing reached the network
# The curls below observe TRANSPORT and status; they cannot by themselves prove APPLICATION auth,
# because a reverse proxy in front of the app can return the same codes (or forward to an
# unauthenticated backend once its own check passes), and curl follows HTTP redirects but does not run a
# SPA's client-side login routing. Attribute an app-layer result by probing the BACKEND directly on its
# loopback address (section 1; the separate fronting proxy is out of the path, but see the Dify nginx caveat below) and confirm the editor/setup state in a browser.
# Each curl disables client proxies (--noproxy '*'), is bounded, -g-guards substituted values, and
# prints the exit code. Run each before and after locking down.
#
# Editor/console and Dify /install: confirm in a FRESH, UNAUTHENTICATED BROWSER SESSION, not by status
# code - all four are SPAs serving the same 200 + HTML shell logged in or not, so a curl of / cannot
# tell an open editor from a login page and it discards the /install form you must read. In the browser,
# an unauthenticated editor visit must land on a login route, and https://dify.example.com/install must
# show "already set up" or redirect to login, NEVER an open create-admin form (an open form means the
# first visitor owns the instance). The curl below is only a transport-reachability note:
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -g -sS -L --proto-redir '=https' --noproxy '*' --connect-timeout 5 --max-time 15 \
  -o /dev/null -w 'builder final=%{http_code} url=%{url_effective} exit=%{exitcode}\n' https://builder.example.com/
#
# App API auth, tested against the app on its LOOPBACK address so your fronting reverse proxy (section 2)
# is out of the path, one MATCHED pair per app: WITHOUT the key expect that app's OWN rejection, WITH a
# valid key expect a 2xx returning real output (the positive control). Note for Dify: 127.0.0.1:8080 is
# Dify's OWN bundled nginx, which forwards /v1 to the api service - part of Dify, not a separate fronting
# proxy, but to attribute a result strictly to the api service, probe it on the Compose network instead
# (docker compose exec api curl http://localhost:5001/v1/parameters ...). The pair below shows the body
# so you can read the evidence, and the guard refuses while a placeholder remains. WITHOUT the key Dify
# returns 401 with a message like "Authorization header must be provided and start with 'Bearer'"; a 400
# app_unavailable instead means the app is unavailable or misconfigured (the token identifies the app),
# not that the endpoint is open. WITH a valid app key, 200 returning the app's parameters JSON.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  # The app key you substitute on the set -- line enters shell history.
  # Use a short-lived key or clear that history line afterward.
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_DIFY_APP_KEY'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo "substitute the Dify app key on the set -- line above; not probing"; exit ;; esac
  curl -q -g -sS -w '\ndify no-key=%{http_code} exit=%{exitcode}\n' --noproxy '*' --connect-timeout 5 --max-time 15 http://127.0.0.1:8080/v1/parameters
  printf 'Authorization: Bearer %s\n' "$1" | curl -q -g -sS -w '\ndify with-key=%{http_code} exit=%{exitcode}\n' --noproxy '*' --connect-timeout 5 --max-time 15 -H @- http://127.0.0.1:8080/v1/parameters
)
# Repeat the same guarded, paired pattern for Flowise (POST http://127.0.0.1:3000/api/v1/prediction/<id>
# on a chatflow you ASSIGNED a key to - a keyless chatflow is public by design - key in an
# 'Authorization: Bearer' header) and Langflow (POST http://127.0.0.1:7860/api/v1/run/<id>, key in the
# 'x-api-key' header), each with a JSON body, expecting the app's own rejection without the key and a
# real 2xx with it. A transport error (exit != 0), a validation error, or a redirect is inconclusive,
# never a pass.
```

## Common mistakes

- Starting Dify without `INIT_PASSWORD` on a reachable host: the first visitor to `/install` owns the instance.
- Running Langflow with the default `LANGFLOW_AUTO_LOGIN=True`, which is no login.
- A Flowise chatflow with no API key assigned: the prediction API is public to anyone with the ID.
- Leaving LibreChat registration open after the admin exists, or running with unset or placeholder `CREDS_KEY`/`JWT_SECRET` instead of your own permanent values.

## Sources (checked September 2026)

- Dify Docker Compose deployment (setup at `/install`): https://docs.dify.ai/en/self-host/deploy/quick-start/docker-compose
- Dify environment variables (`SECRET_KEY`, `INIT_PASSWORD`, `CONSOLE_API_URL`, `CONSOLE_WEB_URL`, `APP_WEB_URL`): https://docs.dify.ai/en/self-host/deploy/configuration/environments
- Dify `docker/.env.example` (`EXPOSE_NGINX_PORT`, `NGINX_HTTPS_ENABLED`, certificate variables): https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/docker/.env.example ; `docker-compose.yaml` (which services publish ports): https://github.com/langgenius/dify/blob/8387590ace4a094de812b7847fc6a4c3a27cd52b/docker/docker-compose.yaml
- Docker packet filtering and firewalls (published ports bypass UFW): https://docs.docker.com/engine/network/packet-filtering-firewalls/
- Dify certbot README (HTTPS steps): https://github.com/langgenius/dify/blob/4c1ad40f8e8a6ee58a958330558f2178b7e47fa7/docker/certbot/README.md
- Dify API keys (Bearer, backend-only): https://docs.dify.ai/en/api-reference/guides/get-started
- Flowise app-level authentication (v3.0.1 accounts, deprecated username/password, JWT secrets): https://docs.flowiseai.com/configuration/authorization/app-level
- Flowise chatflow-level API keys: https://docs.flowiseai.com/configuration/authorization/chatflow-level
- Flowise environment variables (`PORT`, `NUMBER_OF_PROXIES`, `FLOWISE_SECRETKEY_OVERWRITE`): https://docs.flowiseai.com/configuration/environment-variables
- Flowise SSO (Enterprise-plan only): https://docs.flowiseai.com/configuration/sso
- Flowise prediction API (401 without key): https://docs.flowiseai.com/api-reference/prediction
- Flowise deployment with nginx and certbot: https://docs.flowiseai.com/configuration/deployment/digital-ocean
- Flowise Compose (publishes `${PORT}:${PORT}`): https://github.com/FlowiseAI/Flowise/blob/4ea391204a499fb6d19747104502362295b4dde3/docker/docker-compose.yml
- Langflow example Compose (publishes `7860:7860` and PostgreSQL `5432:5432`): https://github.com/langflow-ai/langflow/blob/c6dbca308dc85526d5cecb31211821ec4f5e1d05/docker_example/docker-compose.yml
- LibreChat Compose (publishes `${PORT}:${PORT}`; extended via a docker-compose.override.yaml): https://github.com/danny-avila/LibreChat/blob/1596df724a840f894831fc74f21de8d8df72fcb1/docker-compose.yml
- Langflow API keys and authentication: https://docs.langflow.org/api-keys-and-authentication
- Langflow environment variables (`LANGFLOW_HOST`, `LANGFLOW_PORT`, SSL files): https://docs.langflow.org/environment-variables
- Langflow production best practices (`LANGFLOW_SECRET_KEY` preflight): https://docs.langflow.org/deployment-prod-best-practices
- Langflow security model (the editor runs arbitrary Python with host/filesystem/network access): https://docs.langflow.org/security
- Langflow authentication overview (external identity, JWT/JWKS validation): https://docs.langflow.org/authentication-overview
- LibreChat `.env` reference: https://www.librechat.ai/docs/configuration/dotenv
- LibreChat authentication system: https://www.librechat.ai/docs/configuration/authentication
- LibreChat OAuth2 and OIDC overview: https://www.librechat.ai/docs/configuration/authentication/OAuth2-OIDC
- LibreChat Keycloak setup (`OPENID_*` variables): https://www.librechat.ai/docs/configuration/authentication/OAuth2-OIDC/keycloak
- LibreChat Docker install (port 3080, first account is admin): https://www.librechat.ai/docs/local/docker
- LibreChat nginx and TLS: https://www.librechat.ai/docs/remote/nginx
- LibreChat Actions (domain allowlist, built-in SSRF checks): https://www.librechat.ai/docs/configuration/librechat_yaml/object_structure/actions
- LibreChat v0.7.7 changelog (two-factor authentication): https://www.librechat.ai/changelog/v0.7.7
- Docker Compose merge rules (sequences merge rather than replace; the `!reset` tag): https://docs.docker.com/reference/compose-file/merge/
- Dify Compose at d39d9ddb7430522e0c828c6953afdf773ba6e675 (daemon image, container bind and host publication): https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/docker/docker-compose.yaml#L573-L644
- Dify plugin daemon 0.6.10, commit 1310a18b2f6bc6f18768a0a6265484830891433c (TCP listener and newline framing): https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/core/debugging_runtime/server.go#L109-L134 ; https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/core/debugging_runtime/codec.go#L14-L49 ; each decoded line passed to the message handler: https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/core/debugging_runtime/hooks.go#L132-L153
- Dify plugin daemon 0.6.10 (handshake lookup, invalid-key rejection and connection handling): https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/core/debugging_runtime/runtime_intialization_handlers.go#L18-L42 ; https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/core/debugging_runtime/hooks.go#L51-L90 ; https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/core/debugging_runtime/hooks.go#L158-L240
- Dify plugin daemon 0.6.10 (pre-handshake dispatch, declaration storage and exact asset accounting): https://github.com/langgenius/dify-plugin-daemon/blob/1310a18b2f6bc6f18768a0a6265484830891433c/internal/core/debugging_runtime/hooks.go#L158-L237 ; https://github.com/langgenius/dify-plugin-daemon/blob/1310a18b2f6bc6f18768a0a6265484830891433c/internal/core/debugging_runtime/runtime_intialization_handlers.go#L44-L75 ; https://github.com/langgenius/dify-plugin-daemon/blob/1310a18b2f6bc6f18768a0a6265484830891433c/internal/core/debugging_runtime/runtime_intialization_handlers.go#L139-L183
- Dify plugin daemon 0.6.10 (key generation, Redis mappings, expiry refresh and lookup): https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/service/debugging_service/connection_key.go#L23-L123 ; https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/pkg/utils/cache/redis.go#L208-L230
- Dify plugin daemon 0.6.10 (remote installation, invocation transport and request data): https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/service/install_service/controlpanel.go#L50-L85 ; https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/core/debugging_runtime/io.go#L18-L68 ; https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/pkg/entities/requests/tool.go#L27-L36 ; https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/pkg/entities/requests/model.go#L9-L34
- Dify plugin daemon 0.6.10 (enable switch, server startup and debugging-key route): https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/types/app/config.go#L101-L106 ; https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/core/control_panel/watch_dog.go#L32-L46 ; https://github.com/langgenius/dify-plugin-daemon/blob/0.6.10/internal/server/http_server.go#L130-L134
- Dify console at d39d9ddb7430522e0c828c6953afdf773ba6e675 (debugging-key route and its decorators; plugin-permission default; RBAC check and its default): https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/controllers/console/workspace/plugin.py#L567-L585 ; https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/controllers/console/workspace/__init__.py#L14-L61 ; https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/controllers/common/wraps.py#L11-L32 ; https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/configs/enterprise/__init__.py#L38-L41
- Dify console prerequisites (instance setup, account initialization, active workspace and authenticated session): https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/controllers/console/wraps.py#L308-L321 ; https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/controllers/console/wraps.py#L113-L125 ; https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/libs/login.py#L47-L59 ; https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/libs/login.py#L152-L169
- Dify plugin permission model (row default `noone`, unlike the no-row allowance above): https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/models/account.py#L402-L407
- Dify permission-change API (admin or owner only, request defaults, create or update the permission row): https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/controllers/console/workspace/plugin.py#L1086-L1106 ; https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/controllers/console/workspace/plugin.py#L170-L172 ; https://github.com/langgenius/dify/blob/d39d9ddb7430522e0c828c6953afdf773ba6e675/api/services/plugin/plugin_permission_service.py#L14-L36
- `docker compose ps` output fields (`Service`, `Publishers`, `PublishedPort`): https://docs.docker.com/reference/cli/docker/compose/ps/
