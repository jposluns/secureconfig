---
version_basis: {
  "schema": 1,
  "checked": "2026-09-27",
  "documentation_checked": "2026-09",
  "body_sha256": "f0a5c38cca708ba4474566b366f8c9a89f4e265ed20e89cffdd87ccabe0713ab",
  "components": {
    "webui": {
      "name": "Open WebUI",
      "basis": "0a7c15832fb30b1903753e83f81dc7d27e5b0944",
      "sources": {
        "s94d055784840": "https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/config.py",
        "s9d6f5fb157de": "https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py",
        "s8952330d0246": "https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/main.py",
        "s241050fbe377": "https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/README.md",
        "s7d025cba5af9": "https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/env.py",
        "seb3e13955745": "https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/utils/auth.py",
        "s4fed797e27ab": "https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/start.sh",
        "s0a3440b8f305": "https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/Dockerfile",
        "s0b1139eccad8": "https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/ollama.py",
        "s416fdb7c65df": "https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/chats.py",
        "s377a6a5e9f43": "https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/files.py",
        "sbd0096118f9c": "https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/retrieval.py",
        "s26981e2dc6de": "https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/package.json"
      }
    },
    "docker": {
      "name": "Docker Engine localhost boundary",
      "basis": "28.0.0",
      "sources": {
        "s1e53417c513d": "https://docs.docker.com/engine/network/port-publishing/"
      }
    },
    "webui-docs": {
      "name": "Open WebUI documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "s991b1b357189": "https://docs.openwebui.com/reference/env-configuration",
        "s4618b483c060": "https://docs.openwebui.com/getting-started/advanced-topics/hardening/",
        "sddffd30a3b0f": "https://docs.openwebui.com/features/authentication-access/auth/sso/",
        "sf412328c22af": "https://docs.openwebui.com/features/extensibility/plugin/development/under-the-hood/",
        "seec6b2b9c299": "https://docs.openwebui.com/features/authentication-access/rbac/groups/",
        "sab6706f74917": "https://docs.openwebui.com/features/authentication-access/rbac/permissions/",
        "s724ec4249003": "https://docs.openwebui.com/reference/database-schema/",
        "s3d61ecad0833": "https://docs.openwebui.com/reference/api-endpoints/",
        "sf11ac1428acb": "https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/",
        "sbebbd1dda5c6": "https://docs.openwebui.com/features/chat-conversations/direct-connections/",
        "sb28825887b54": "https://docs.openwebui.com/features/authentication-access/api-keys/"
      }
    }
  },
  "claims": {
    "signup": {"text": "ENABLE_SIGNUP defaults true; disable ordinary registration after accounts exist.", "components": ["webui"], "sources": ["webui:s94d055784840", "webui:s9d6f5fb157de"], "status": "REASONED", "verify": [1]},
    "persistence": {"text": "ConfigVar database values override environment after first launch unless ENABLE_PERSISTENT_CONFIG=false; default is true.", "components": ["webui", "webui-docs"], "sources": ["webui-docs:s991b1b357189", "webui:s94d055784840"], "status": "REASONED"},
    "roles": {"text": "DEFAULT_USER_ROLE defaults pending; user auto-approves and admin grants administrative privileges to later registrations.", "components": ["webui"], "sources": ["webui:s94d055784840", "webui:s9d6f5fb157de"], "status": "REASONED"},
    "first-admin": {"text": "First account is admin regardless of DEFAULT_USER_ROLE; bootstrap privately or preset admin email/password.", "components": ["webui"], "sources": ["webui:s9d6f5fb157de", "webui:s8952330d0246"], "status": "REASONED"},
    "signup-auto-disable": {"text": "First normal registration and successful environment admin creation disable signup under normal persisted configuration.", "components": ["webui", "webui-docs"], "sources": ["webui:s9d6f5fb157de", "webui:s8952330d0246", "webui-docs:s4618b483c060"], "status": "REASONED"},
    "bootstrap-exception": {"text": "Empty-database signup bypasses ENABLE_SIGNUP with ENABLE_LOGIN_FORM=true, its default; disabled-form bootstrap needs ENABLE_INITIAL_ADMIN_SIGNUP=true, default false.", "components": ["webui"], "sources": ["webui:s9d6f5fb157de", "webui:s94d055784840"], "status": "REASONED", "verify": [3]},
    "password-auth": {"text": "ENABLE_PASSWORD_AUTH=false blocks password and trusted-header signin because its check runs first; use for OAuth/OIDC-only login.", "components": ["webui"], "sources": ["webui:s9d6f5fb157de"], "status": "REASONED", "verify": [3]},
    "sso-mfa": {"text": "OAuth/OIDC MFA belongs at the identity provider; ordinary signup refusal does not close alternative provisioning.", "components": ["webui-docs"], "sources": ["webui-docs:sddffd30a3b0f"], "status": "REASONED"},
    "publication": {"text": "Publish host 127.0.0.1:3000 to container 8080 with Engine 28.0+; inspect NAT and external reachability as well as ss.", "components": ["webui", "docker"], "sources": ["webui:s241050fbe377", "docker:s1e53417c513d"], "status": "REASONED", "verify": [1, 2]},
    "data-volume": {"text": "Retain /app/backend/data for accounts/config; lost data reopens first-admin bootstrap, so keep ingress closed until claimed.", "components": ["webui"], "sources": ["webui:s241050fbe377", "webui:s9d6f5fb157de"], "status": "REASONED"},
    "transport": {"text": "Open WebUI has no native TLS; use a TLS fronting layer and keep authentication enabled behind public access paths.", "components": ["webui-docs"], "sources": ["webui-docs:s991b1b357189", "webui-docs:s4618b483c060"], "status": "REASONED"},
    "session-cookie": {"text": "Set WEBUI_SESSION_COOKIE_SECURE=true before HTTPS publication; default is false.", "components": ["webui"], "sources": ["webui:s7d025cba5af9"], "status": "REASONED", "verify": [3]},
    "auth-cookie": {"text": "WEBUI_AUTH_COOKIE_SECURE inherits the session setting unless overridden; set it true explicitly, since TLS termination alone does not set Secure.", "components": ["webui"], "sources": ["webui:s7d025cba5af9", "webui:s9d6f5fb157de"], "status": "REASONED", "verify": [3]},
    "cookie-test": {"text": "Issued token and owui-session cookies need Secure/HttpOnly and intended SameSite, lax by default; no issued cookie is inconclusive.", "components": ["webui"], "sources": ["webui:s7d025cba5af9", "webui:s9d6f5fb157de", "webui:s8952330d0246"], "status": "REASONED", "verify": [3]},
    "auth": {"text": "WEBUI_AUTH defaults true; do not disable it to bypass empty signing-key startup refusal.", "components": ["webui"], "sources": ["webui:s7d025cba5af9"], "status": "REASONED"},
    "jwt-lifetime": {"text": "JWT_EXPIRES_IN defaults 4w; 24h is an example finite lifetime.", "components": ["webui"], "sources": ["webui:s94d055784840"], "status": "REASONED"},
    "signing-key": {"text": "Inject the same persistent WEBUI_SECRET_KEY into every replica; HS256 signing-key disclosure permits existing-user impersonation.", "components": ["webui"], "sources": ["webui:s7d025cba5af9", "webui:seb3e13955745"], "status": "REASONED"},
    "key-file": {"text": "Launcher generates .webui_secret_key only when absent; default /app/backend location is outside the data volume and can be lost on replacement.", "components": ["webui"], "sources": ["webui:s4fed797e27ab", "webui:s0a3440b8f305"], "status": "REASONED"},
    "revocation": {"text": "Without Redis signout does not revoke a copied JWT before expiry; shared revocation needs Redis across workers.", "components": ["webui"], "sources": ["webui:seb3e13955745"], "status": "REASONED", "verify": [3]},
    "rotation": {"text": "WEBUI_JWT_SECRET_KEY is deprecated; signing-key rotation invalidates tokens and affects default OAuth encryption keys.", "components": ["webui", "webui-docs"], "sources": ["webui:s7d025cba5af9", "webui-docs:sddffd30a3b0f"], "status": "REASONED"},
    "key-persistence-test": {"text": "Unexpired JWT should survive recreation with retained key/data and work across replicas; a changed key rejects it.", "components": ["webui"], "sources": ["webui:seb3e13955745", "webui:s4fed797e27ab"], "status": "REASONED", "verify": [3]},
    "oauth-signup": {"text": "ENABLE_OAUTH_SIGNUP defaults false and independently controls OAuth provisioning; test new and already-linked identities.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui-docs:sddffd30a3b0f"], "status": "REASONED", "verify": [3]},
    "oauth-domains": {"text": "OAUTH_ALLOWED_DOMAINS defaults *; set approved domains and test excluded-domain refusal.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui-docs:sddffd30a3b0f"], "status": "REASONED", "verify": [3]},
    "oauth-merge": {"text": "OAUTH_MERGE_ACCOUNTS_BY_EMAIL defaults false; retain it absent verified-email guarantees.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui-docs:sddffd30a3b0f"], "status": "REASONED"},
    "oauth-roles": {"text": "ENABLE_OAUTH_ROLE_MANAGEMENT defaults false; enable only after reviewing role claims.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui-docs:sddffd30a3b0f"], "status": "REASONED"},
    "oauth-persistence": {"text": "ENABLE_OAUTH_PERSISTENT_CONFIG defaults false with environment authority/read-only admin UI; enabling persistence permits stored precedence.", "components": ["webui-docs"], "sources": ["webui-docs:sddffd30a3b0f"], "status": "REASONED"},
    "trusted-headers": {"text": "Leave identity headers unset unless a sole trusted proxy strips client values and supplies authenticated identity; forged headers can impersonate/provision users.", "components": ["webui", "webui-docs"], "sources": ["webui:s7d025cba5af9", "webui:s9d6f5fb157de", "webui-docs:sddffd30a3b0f"], "status": "REASONED", "verify": [3]},
    "plugins": {"text": "ENABLE_PLUGINS defaults true; uploaded Tools/Functions execute server-side Python, including top-level code at load.", "components": ["webui", "webui-docs"], "sources": ["webui:s7d025cba5af9", "webui-docs:sf412328c22af"], "status": "REASONED"},
    "plugin-scope": {"text": "Disabling plugins blocks loading/execution, not every management endpoint, built-in tool, MCP/OpenAPI connection or terminal.", "components": ["webui-docs"], "sources": ["webui-docs:s991b1b357189", "webui-docs:sf412328c22af"], "status": "REASONED", "verify": [3]},
    "tools-access": {"text": "USER_PERMISSIONS_WORKSPACE_TOOLS_ACCESS defaults false; ordinary Tool creation depends on workspace.tools, Function creation is administrative.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui-docs:sf412328c22af"], "status": "REASONED", "verify": [3]},
    "tools-import": {"text": "USER_PERMISSIONS_WORKSPACE_TOOLS_IMPORT defaults false; remove unintended import grants from every group.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui-docs:seec6b2b9c299"], "status": "REASONED"},
    "code-execution": {"text": "ENABLE_CODE_EXECUTION defaults true with pyodide engine; disable unused legacy execution independently of server plugins.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui-docs:s991b1b357189"], "status": "REASONED", "verify": [3]},
    "code-interpreter": {"text": "ENABLE_CODE_INTERPRETER defaults true with pyodide engine; test its own request path separately.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui-docs:s991b1b357189"], "status": "REASONED", "verify": [3]},
    "groups": {"text": "Group permissions add grants; a false default or another false membership cannot cancel a true grant.", "components": ["webui-docs"], "sources": ["webui-docs:seec6b2b9c299"], "status": "REASONED", "verify": [3]},
    "model-bypass": {"text": "BYPASS_MODEL_ACCESS_CONTROL defaults false; keep bypass disabled.", "components": ["webui"], "sources": ["webui:s7d025cba5af9"], "status": "REASONED"},
    "model-workspace": {"text": "USER_PERMISSIONS_WORKSPACE_MODELS_ACCESS defaults false and controls creation/editing, not invocation of existing models.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui-docs:sab6706f74917"], "status": "REASONED", "verify": [3]},
    "model-grants": {"text": "Private models need user/group grants; current payloads use access_grants; permitted completion is the positive control for excluded-user refusal.", "components": ["webui-docs"], "sources": ["webui-docs:seec6b2b9c299", "webui-docs:s724ec4249003", "webui-docs:s3d61ecad0833"], "status": "REASONED", "verify": [3]},
    "ollama-admin": {"text": "Pull/create/copy/delete require admin role, not ENABLE_MODEL_* switches; test ordinary-user refusal, including DELETE /ollama/api/delete, against valid admin controls.", "components": ["webui"], "sources": ["webui:s0b1139eccad8"], "status": "REASONED", "verify": [3]},
    "connections": {"text": "Pin every backend; initial OpenAI destination is https://api.openai.com/v1, and connection URLs do not enforce network egress.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui-docs:sf11ac1428acb"], "status": "REASONED", "verify": [3]},
    "direct-connections": {"text": "ENABLE_DIRECT_CONNECTIONS defaults false; enabling it sends browser-to-provider inference, not server-side SSRF protection.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui-docs:sbebbd1dda5c6"], "status": "REASONED", "verify": [3]},
    "admin-chat": {"text": "ENABLE_ADMIN_CHAT_ACCESS defaults true; disable/restart and test admin list-user refusal while owner access works.", "components": ["webui"], "sources": ["webui:s7d025cba5af9", "webui:s416fdb7c65df"], "status": "REASONED", "verify": [3]},
    "admin-export": {"text": "ENABLE_ADMIN_EXPORT defaults true; disable separately and test /api/v1/chats/all/db refusal; operator/database access remains possible.", "components": ["webui"], "sources": ["webui:s7d025cba5af9", "webui:s416fdb7c65df"], "status": "REASONED", "verify": [3]},
    "community": {"text": "ENABLE_COMMUNITY_SHARING defaults true; false removes community UI, not all local sharing/export.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui-docs:s991b1b357189"], "status": "REASONED", "verify": [3]},
    "docs": {"text": "ENV defaults dev in backend and prod in official image; prod removes docs/schema registration, not APIs; inspect content rather than HTTP 200 alone.", "components": ["webui"], "sources": ["webui:s7d025cba5af9", "webui:s0a3440b8f305", "webui:s8952330d0246"], "status": "REASONED", "verify": [3]},
    "api-keys": {"text": "ENABLE_API_KEYS defaults false; disabling rejects existing keys without deleting them or disabling JWTs.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui:seb3e13955745", "webui-docs:sb28825887b54"], "status": "REASONED", "verify": [3]},
    "key-permission": {"text": "API-key permission defaults false; ordinary users need it and global enablement, admins need the global switch; keys inherit owner authority.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui:seb3e13955745", "webui-docs:sb28825887b54"], "status": "REASONED", "verify": [3]},
    "key-routes": {"text": "Endpoint restrictions default false; allowed exact paths also admit slash descendants and do not constrain methods or vary per key.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui:seb3e13955745", "webui-docs:sb28825887b54"], "status": "REASONED", "verify": [3]},
    "local-fetch": {"text": "ENABLE_LOCAL_WEB_FETCH defaults false; ENABLE_RAG_LOCAL_WEB_FETCH is its deprecated alias.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui-docs:s991b1b357189"], "status": "REASONED"},
    "redirects": {"text": "AIOHTTP_CLIENT_ALLOW_REDIRECTS defaults false; keep redirects disabled and enforce independent egress.", "components": ["webui", "webui-docs"], "sources": ["webui:s7d025cba5af9", "webui-docs:s4618b483c060"], "status": "REASONED"},
    "fetch-filter": {"text": "WEB_FETCH_FILTER_LIST uses comma-separated allow entries and ! deny entries extending the built-in blocklist.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui-docs:s991b1b357189"], "status": "REASONED", "verify": [3]},
    "web-search": {"text": "ENABLE_WEB_SEARCH defaults false; disabling should stop controlled search-provider calls.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui-docs:s4618b483c060"], "status": "REASONED", "verify": [3]},
    "file-size": {"text": "RAG_FILE_MAX_SIZE defaults unset; 10 MB is an example and handler checks after storage upload, so proxy body limits are also needed.", "components": ["webui"], "sources": ["webui:s94d055784840", "webui:s377a6a5e9f43"], "status": "REASONED", "verify": [3]},
    "file-count": {"text": "RAG_FILE_MAX_COUNT defaults unset; five is an example count, not aggregate storage/request quota.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui-docs:s991b1b357189"], "status": "REASONED", "verify": [3]},
    "file-permission": {"text": "Chat file-upload permission defaults true; false alone does not block verified-user POST /api/v1/files/, requiring proxy denial when prohibited.", "components": ["webui"], "sources": ["webui:s94d055784840", "webui:s377a6a5e9f43", "webui:seb3e13955745"], "status": "REASONED", "verify": [3]},
    "web-permission": {"text": "Chat web-upload permission defaults true; false alone does not block web/youtube/url handlers; test each proxy denial with a working fixture.", "components": ["webui"], "sources": ["webui:s94d055784840", "webui:sbd0096118f9c", "webui:seb3e13955745"], "status": "REASONED", "verify": [3]},
    "search-permission": {"text": "USER_PERMISSIONS_FEATURES_WEB_SEARCH defaults true; audit every group grant alongside global search disablement.", "components": ["webui", "webui-docs"], "sources": ["webui:s94d055784840", "webui-docs:seec6b2b9c299"], "status": "REASONED"},
    "signin-rate": {"text": "Password signin is limited to 15 attempts per 180 seconds per email; this is not an inference quota.", "components": ["webui"], "sources": ["webui:s9d6f5fb157de"], "status": "REASONED"},
    "inference-limits": {"text": "Apply proxy rate/concurrency and provider/gateway spend limits; under-limit requests work while excess work is refused without provider calls.", "components": ["webui-docs"], "sources": ["webui-docs:s4618b483c060"], "status": "REASONED", "verify": [3]},
    "verify-signup": {"text": "After bootstrap require disabled feature flag, absent signup option and actual registration refusal; enabled signup should yield pending, not access.", "components": ["webui"], "sources": ["webui:s9d6f5fb157de", "webui:s94d055784840"], "status": "REASONED", "verify": [1]},
    "verify-network": {"text": "Actual host port 3000 must not answer from a second LAN/VPC host while trusted HTTPS works; DNS/local errors do not prove isolation.", "components": ["docker"], "sources": ["docker:s1e53417c513d"], "status": "REASONED", "verify": [2]},
    "verify-ssrf": {"text": "Compare allowed public, controlled private, filter-denied and redirected destinations using contact/egress logs; failed fetch alone proves no boundary.", "components": ["webui", "webui-docs"], "sources": ["webui:sbd0096118f9c", "webui-docs:s4618b483c060"], "status": "REASONED", "verify": [3]},
    "recorded-version": {"text": "Pinned package identifies v0.11.3; the environment reference describes coverage through v0.11.1; introduction versions remain unverified.", "components": ["webui", "webui-docs"], "sources": ["webui:s26981e2dc6de", "webui-docs:s991b1b357189"], "status": "REASONED"}
  }
}
---
# Open WebUI: signup control, TLS, and MFA

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-27; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- webui: Open WebUI, 0a7c15832fb30b1903753e83f81dc7d27e5b0944
- docker: Docker Engine localhost boundary, 28.0.0
- webui-docs: Open WebUI documentation (rolling), unknown

Claims (full source mapping in the front matter):

- signup (REASONED; webui): ENABLE_SIGNUP defaults true; disable ordinary registration after accounts exist.
- persistence (REASONED; webui, webui-docs): ConfigVar database values override environment after first launch unless ENABLE_PERSISTENT_CONFIG=false; default is true.
- roles (REASONED; webui): DEFAULT_USER_ROLE defaults pending; user auto-approves and admin grants administrative privileges to later registrations.
- first-admin (REASONED; webui): First account is admin regardless of DEFAULT_USER_ROLE; bootstrap privately or preset admin email/password.
- signup-auto-disable (REASONED; webui, webui-docs): First normal registration and successful environment admin creation disable signup under normal persisted configuration.
- bootstrap-exception (REASONED; webui): Empty-database signup bypasses ENABLE_SIGNUP with ENABLE_LOGIN_FORM=true, its default; disabled-form bootstrap needs ENABLE_INITIAL_ADMIN_SIGNUP=true, default false.
- password-auth (REASONED; webui): ENABLE_PASSWORD_AUTH=false blocks password and trusted-header signin because its check runs first; use for OAuth/OIDC-only login.
- sso-mfa (REASONED; webui-docs): OAuth/OIDC MFA belongs at the identity provider; ordinary signup refusal does not close alternative provisioning.
- publication (REASONED; webui, docker): Publish host 127.0.0.1:3000 to container 8080 with Engine 28.0+; inspect NAT and external reachability as well as ss.
- data-volume (REASONED; webui): Retain /app/backend/data for accounts/config; lost data reopens first-admin bootstrap, so keep ingress closed until claimed.
- transport (REASONED; webui-docs): Open WebUI has no native TLS; use a TLS fronting layer and keep authentication enabled behind public access paths.
- session-cookie (REASONED; webui): Set WEBUI_SESSION_COOKIE_SECURE=true before HTTPS publication; default is false.
- auth-cookie (REASONED; webui): WEBUI_AUTH_COOKIE_SECURE inherits the session setting unless overridden; set it true explicitly, since TLS termination alone does not set Secure.
- cookie-test (REASONED; webui): Issued token and owui-session cookies need Secure/HttpOnly and intended SameSite, lax by default; no issued cookie is inconclusive.
- auth (REASONED; webui): WEBUI_AUTH defaults true; do not disable it to bypass empty signing-key startup refusal.
- jwt-lifetime (REASONED; webui): JWT_EXPIRES_IN defaults 4w; 24h is an example finite lifetime.
- signing-key (REASONED; webui): Inject the same persistent WEBUI_SECRET_KEY into every replica; HS256 signing-key disclosure permits existing-user impersonation.
- key-file (REASONED; webui): Launcher generates .webui_secret_key only when absent; default /app/backend location is outside the data volume and can be lost on replacement.
- revocation (REASONED; webui): Without Redis signout does not revoke a copied JWT before expiry; shared revocation needs Redis across workers.
- rotation (REASONED; webui, webui-docs): WEBUI_JWT_SECRET_KEY is deprecated; signing-key rotation invalidates tokens and affects default OAuth encryption keys.
- key-persistence-test (REASONED; webui): Unexpired JWT should survive recreation with retained key/data and work across replicas; a changed key rejects it.
- oauth-signup (REASONED; webui, webui-docs): ENABLE_OAUTH_SIGNUP defaults false and independently controls OAuth provisioning; test new and already-linked identities.
- oauth-domains (REASONED; webui, webui-docs): OAUTH_ALLOWED_DOMAINS defaults *; set approved domains and test excluded-domain refusal.
- oauth-merge (REASONED; webui, webui-docs): OAUTH_MERGE_ACCOUNTS_BY_EMAIL defaults false; retain it absent verified-email guarantees.
- oauth-roles (REASONED; webui, webui-docs): ENABLE_OAUTH_ROLE_MANAGEMENT defaults false; enable only after reviewing role claims.
- oauth-persistence (REASONED; webui-docs): ENABLE_OAUTH_PERSISTENT_CONFIG defaults false with environment authority/read-only admin UI; enabling persistence permits stored precedence.
- trusted-headers (REASONED; webui, webui-docs): Leave identity headers unset unless a sole trusted proxy strips client values and supplies authenticated identity; forged headers can impersonate/provision users.
- plugins (REASONED; webui, webui-docs): ENABLE_PLUGINS defaults true; uploaded Tools/Functions execute server-side Python, including top-level code at load.
- plugin-scope (REASONED; webui-docs): Disabling plugins blocks loading/execution, not every management endpoint, built-in tool, MCP/OpenAPI connection or terminal.
- tools-access (REASONED; webui, webui-docs): USER_PERMISSIONS_WORKSPACE_TOOLS_ACCESS defaults false; ordinary Tool creation depends on workspace.tools, Function creation is administrative.
- tools-import (REASONED; webui, webui-docs): USER_PERMISSIONS_WORKSPACE_TOOLS_IMPORT defaults false; remove unintended import grants from every group.
- code-execution (REASONED; webui, webui-docs): ENABLE_CODE_EXECUTION defaults true with pyodide engine; disable unused legacy execution independently of server plugins.
- code-interpreter (REASONED; webui, webui-docs): ENABLE_CODE_INTERPRETER defaults true with pyodide engine; test its own request path separately.
- groups (REASONED; webui-docs): Group permissions add grants; a false default or another false membership cannot cancel a true grant.
- model-bypass (REASONED; webui): BYPASS_MODEL_ACCESS_CONTROL defaults false; keep bypass disabled.
- model-workspace (REASONED; webui, webui-docs): USER_PERMISSIONS_WORKSPACE_MODELS_ACCESS defaults false and controls creation/editing, not invocation of existing models.
- model-grants (REASONED; webui-docs): Private models need user/group grants; current payloads use access_grants; permitted completion is the positive control for excluded-user refusal.
- ollama-admin (REASONED; webui): Pull/create/copy/delete require admin role, not ENABLE_MODEL_* switches; test ordinary-user refusal, including DELETE /ollama/api/delete, against valid admin controls.
- connections (REASONED; webui, webui-docs): Pin every backend; initial OpenAI destination is https://api.openai.com/v1, and connection URLs do not enforce network egress.
- direct-connections (REASONED; webui, webui-docs): ENABLE_DIRECT_CONNECTIONS defaults false; enabling it sends browser-to-provider inference, not server-side SSRF protection.
- admin-chat (REASONED; webui): ENABLE_ADMIN_CHAT_ACCESS defaults true; disable/restart and test admin list-user refusal while owner access works.
- admin-export (REASONED; webui): ENABLE_ADMIN_EXPORT defaults true; disable separately and test /api/v1/chats/all/db refusal; operator/database access remains possible.
- community (REASONED; webui, webui-docs): ENABLE_COMMUNITY_SHARING defaults true; false removes community UI, not all local sharing/export.
- docs (REASONED; webui): ENV defaults dev in backend and prod in official image; prod removes docs/schema registration, not APIs; inspect content rather than HTTP 200 alone.
- api-keys (REASONED; webui, webui-docs): ENABLE_API_KEYS defaults false; disabling rejects existing keys without deleting them or disabling JWTs.
- key-permission (REASONED; webui, webui-docs): API-key permission defaults false; ordinary users need it and global enablement, admins need the global switch; keys inherit owner authority.
- key-routes (REASONED; webui, webui-docs): Endpoint restrictions default false; allowed exact paths also admit slash descendants and do not constrain methods or vary per key.
- local-fetch (REASONED; webui, webui-docs): ENABLE_LOCAL_WEB_FETCH defaults false; ENABLE_RAG_LOCAL_WEB_FETCH is its deprecated alias.
- redirects (REASONED; webui, webui-docs): AIOHTTP_CLIENT_ALLOW_REDIRECTS defaults false; keep redirects disabled and enforce independent egress.
- fetch-filter (REASONED; webui, webui-docs): WEB_FETCH_FILTER_LIST uses comma-separated allow entries and ! deny entries extending the built-in blocklist.
- web-search (REASONED; webui, webui-docs): ENABLE_WEB_SEARCH defaults false; disabling should stop controlled search-provider calls.
- file-size (REASONED; webui): RAG_FILE_MAX_SIZE defaults unset; 10 MB is an example and handler checks after storage upload, so proxy body limits are also needed.
- file-count (REASONED; webui, webui-docs): RAG_FILE_MAX_COUNT defaults unset; five is an example count, not aggregate storage/request quota.
- file-permission (REASONED; webui): Chat file-upload permission defaults true; false alone does not block verified-user POST /api/v1/files/, requiring proxy denial when prohibited.
- web-permission (REASONED; webui): Chat web-upload permission defaults true; false alone does not block web/youtube/url handlers; test each proxy denial with a working fixture.
- search-permission (REASONED; webui, webui-docs): USER_PERMISSIONS_FEATURES_WEB_SEARCH defaults true; audit every group grant alongside global search disablement.
- signin-rate (REASONED; webui): Password signin is limited to 15 attempts per 180 seconds per email; this is not an inference quota.
- inference-limits (REASONED; webui-docs): Apply proxy rate/concurrency and provider/gateway spend limits; under-limit requests work while excess work is refused without provider calls.
- verify-signup (REASONED; webui): After bootstrap require disabled feature flag, absent signup option and actual registration refusal; enabled signup should yield pending, not access.
- verify-network (REASONED; docker): Actual host port 3000 must not answer from a second LAN/VPC host while trusted HTTPS works; DNS/local errors do not prove isolation.
- verify-ssrf (REASONED; webui, webui-docs): Compare allowed public, controlled private, filter-denied and redirected destinations using contact/egress logs; failed fetch alone proves no boundary.
- recorded-version (REASONED; webui, webui-docs): Pinned package identifies v0.11.3; the environment reference describes coverage through v0.11.1; introduction versions remain unverified.
<!-- version-basis:end -->

Open WebUI has account-based authentication built in; the risks are open signup on an exposed instance and running it on plain HTTP. It provides no TLS of its own, so encryption comes from a fronting layer.

At the time of writing, the pinned source identifies release **v0.11.3** at commit `0a7c15832fb30b1903753e83f81dc7d27e5b0944`; the environment reference labels itself current through **v0.11.1**. The controls below were checked against that commit and the linked vendor documentation in September 2026. Introduction versions are unverified unless stated. See the [release version](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/package.json) and [environment reference](https://docs.openwebui.com/reference/env-configuration/).

## 1. Control who can register

Environment variables (defaults per the Open WebUI reference):

```
ENABLE_SIGNUP=false          # default true; disable once your accounts exist (persisted, see below)
DEFAULT_USER_ROLE=pending    # the default; new accounts wait for admin approval
                             # other values: user, admin
```

`ENABLE_SIGNUP` is a persisted setting: the reference marks it a `ConfigVar`, which means the value is written to the database on first launch and on later starts the stored value wins over the environment, unless `ENABLE_PERSISTENT_CONFIG=false` (default `true`). On an instance that has already started, change signup in the Admin panel rather than in the environment, then confirm the change took effect (Verify below).

With signup left on, keep `DEFAULT_USER_ROLE=pending` so a stranger who registers gets no access until approved. An admin account can also be created at startup by setting `WEBUI_ADMIN_EMAIL` together with `WEBUI_ADMIN_PASSWORD` (supply the password via the environment, not a compose file in git; see [secrets.md](secrets.md)).

With normal persisted configuration, the first normal registration automatically disables signup; successful environment-based admin creation does too. On an existing installation, "signup left on" means signup has been explicitly re-enabled. `DEFAULT_USER_ROLE=user` automatically approves subsequent registrations; `admin` gives those registrations administrative privileges. Keep `pending`. See [registration and bootstrap behavior](https://docs.openwebui.com/getting-started/advanced-topics/hardening/).

The first account created becomes the administrator, whatever `DEFAULT_USER_ROLE` is set to; that role governs only the accounts that follow. Claim the admin account yourself while the instance is still bound to loopback, before anyone else can reach it, or preset it with `WEBUI_ADMIN_EMAIL` and `WEBUI_ADMIN_PASSWORD`. On an exposed instance with signup on, whoever registers first is the administrator.

**An empty database is exposed even with `ENABLE_SIGNUP=false` when the login form is enabled.** `/api/v1/auths/signup` does not apply that switch to the first account. `ENABLE_LOGIN_FORM` defaults to `true`. With the form disabled, `ENABLE_INITIAL_ADMIN_SIGNUP=true` permits first-admin bootstrap; its default is `false`, and it should remain off outside private bootstrap. See the [signup handler](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py).

For SSO, the reference documents OAuth/OIDC settings plus `ENABLE_PASSWORD_AUTH=false` to turn off password login once SSO works; enforcing MFA then happens at the identity provider ([mfa.md](mfa.md)).

That recommendation applies to **OAuth/OIDC-only login**. `/signin` checks `ENABLE_PASSWORD_AUTH` before trusted-header authentication, so setting it to `false` also blocks trusted-header signin. Ordinary signup refusal does not close OAuth or trusted-header provisioning; configure those separately in step 4. See the [signin handler](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py).

The database-over-environment rule also matters for the other `ConfigVar` settings below. On an existing installation, inspect and change their effective values in the Admin panel, or deliberately manage configuration through the environment with persistence disabled. Restarting with a different environment value alone is not proof that a persisted control changed.

## 2. Bind privately and add TLS in front

```bash
docker run -d -p 127.0.0.1:3000:8080 \
  -v open-webui:/app/backend/data \
  ghcr.io/open-webui/open-webui:main
```

The `-v open-webui:/app/backend/data` volume holds the accounts and the persisted config; the vendor requires it. Reuse the same volume whenever you replace the container (an upgrade starts a fresh one), or the database resets and, by the first-account rule above, the next account to register becomes the administrator. When you do start on an empty database, keep the public proxy route disabled until your admin account exists and signup is confirmed off.

Publish it through [caddy.md](caddy.md)/[nginx.md](nginx.md) with a certificate from [free-certificates.md](free-certificates.md), through a [Cloudflare Tunnel with Access](cloudflare.md) in front, or over a [tailnet with Tailscale Serve](tailscale.md) (restricted by tailnet policy). Tailscale Funnel is public and adds no login of its own, so keep Open WebUI's own authentication on behind it. Never expose port 8080 directly: login forms over plain HTTP send passwords in cleartext.

Before publishing over HTTPS, set both `WEBUI_SESSION_COOKIE_SECURE=true` and `WEBUI_AUTH_COOKIE_SECURE=true` in the Open WebUI environment and restart. At this pin, the session setting defaults to `false`; the auth setting inherits it unless explicitly overridden. TLS termination alone does not set the cookies' `Secure` attribute, so an HTTP request can send a cookie before a redirect. See the [cookie defaults](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/env.py) and [signin cookie creation](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py).

The command above establishes the original private binding and data mount. Before publishing, inject the authentication, secret, and applicable controls below through the deployment configuration. For repeatable deployments, replace the mutable `:main` image reference with the release or digest you have tested.

## 3. Keep authentication on and persist the signing key

```
WEBUI_AUTH=true              # default true
JWT_EXPIRES_IN=24h           # example shorter lifetime; default 4w
```

Generate a strong `WEBUI_SECRET_KEY` with `openssl rand -hex 32`, store it in your secret manager, and inject the same persistent value into every replica. Do not commit it or put its value in command arguments. See [secrets.md](secrets.md), the [authentication defaults](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/env.py), and [token lifetime configuration](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/config.py).

The container launcher otherwise generates `.webui_secret_key` **once when the file is absent**, then reads it on subsequent starts. It does not generate a new key on every restart. Its default location is `/app/backend/.webui_secret_key`, outside `/app/backend/data`, so replacing the container can lose it despite retaining the data volume. See the [launcher](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/start.sh) and [container working directory](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/Dockerfile).

`WEBUI_SECRET_KEY` signs HS256 login tokens. Disclosure enables token forgery for existing users, including administrators. Without Redis, signout clears the browser session but does not revoke a copied JWT; it remains usable until expiry. Choose a finite lifetime suited to the deployment and use shared Redis when revocation must propagate across workers and replicas. See the [token signing and revocation implementation](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/utils/auth.py).

Direct backend startup rejects an empty signing key when authentication is enabled. Do not work around that refusal by disabling authentication. `WEBUI_JWT_SECRET_KEY` is the deprecated alias; use `WEBUI_SECRET_KEY`. Plan rotation deliberately: it invalidates existing login tokens, and the key also supplies defaults for OAuth encryption keys. See the [startup requirement](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/env.py) and [OAuth key configuration](https://docs.openwebui.com/features/authentication-access/auth/sso/).

## 4. Close alternative registration paths and protect trusted headers

For OAuth deployments that should not provision new users:

```
ENABLE_OAUTH_SIGNUP=false            # default false
OAUTH_ALLOWED_DOMAINS=example.com     # example approved email domain; default *
OAUTH_MERGE_ACCOUNTS_BY_EMAIL=false   # default false
ENABLE_OAUTH_ROLE_MANAGEMENT=false   # default false
```

Replace `example.com` with your approved email domain or comma-separated domains. OAuth account creation checks its own `ENABLE_OAUTH_SIGNUP` switch, independently of `ENABLE_SIGNUP`. Keep email-based account merging off unless the provider's verified-email guarantees have been established, and leave role management off unless you have deliberately reviewed the claims that assign user and admin roles. See [OAuth configuration](https://docs.openwebui.com/features/authentication-access/auth/sso/) and the [pinned defaults](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/config.py).

`ENABLE_OAUTH_PERSISTENT_CONFIG` defaults to `false`: OAuth settings remain environment-authoritative, unlike ordinary persisted settings. With that default, the OAuth Admin panel is read-only. Enabling OAuth persistence allows database values to take precedence when general persistence is enabled. See [OAuth persistence](https://docs.openwebui.com/features/authentication-access/auth/sso/).

Leave `WEBUI_AUTH_TRUSTED_EMAIL_HEADER` unset unless a trusted authentication proxy supplies identity. If configured, the proxy **must strip client-supplied identity headers**, inject only authenticated values, and be the only route to the backend. Apply the same rule to configured name, role, and group headers. A forged email header can impersonate an existing administrator; trusted-header signin can also provision accounts independently of ordinary signup. See [trusted-header authentication](https://docs.openwebui.com/features/authentication-access/auth/sso/) and the [signin implementation](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py).

For trusted-header deployments, retain `ENABLE_PASSWORD_AUTH=true` because of the `/signin` ordering described in step 1. Enforce MFA and admission at the authenticating proxy, and prevent direct backend access.

## 5. Restrict Tools, Functions, and code execution

If server-side Python plugins are unused:

```
ENABLE_PLUGINS=false                         # default true
USER_PERMISSIONS_WORKSPACE_TOOLS_ACCESS=false # default false
USER_PERMISSIONS_WORKSPACE_TOOLS_IMPORT=false # default false
ENABLE_CODE_EXECUTION=false                  # default true
ENABLE_CODE_INTERPRETER=false                # default true
```

Creating or importing Tools and Functions loads submitted Python through `exec`. Top-level code runs during loading, with the Open WebUI process's access to secrets, files, database, and network. Treat permission to submit that code as server access, not as an ordinary chat feature. Function creation is administrative; workspace Tool creation is controlled by `workspace.tools`. See the vendor's [plugin-loader explanation](https://docs.openwebui.com/features/extensibility/plugin/development/under-the-hood/).

`ENABLE_PLUGINS=false` stops uploaded plugins loading and running. It is not a blanket authorization switch for every plugin-management endpoint, and it does **not** disable built-in tools, MCP/OpenAPI connections, or terminals. Review those connections and their access separately. The two code-execution switches are separate controls; their engines default to `pyodide`, and the code-execution reference describes the legacy execution path. Browser Pyodide execution is distinct from server-side Python plugins. See [plugin and code-execution controls](https://docs.openwebui.com/reference/env-configuration/).

Audit **every group**, including all memberships of each ordinary user. Group permissions are additive: a false default or a false permission in one group cannot cancel a true grant from another group. Remove unintended Tools Access and Import grants as well as setting the defaults above. Apply this audit to model-workspace access and API-key permissions too. See [group permission merging](https://docs.openwebui.com/features/authentication-access/rbac/groups/) and the [permission defaults](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/config.py).

## 6. Constrain models, connections, and administrative data access

```
BYPASS_MODEL_ACCESS_CONTROL=false             # default false
USER_PERMISSIONS_WORKSPACE_MODELS_ACCESS=false # default false
ENABLE_DIRECT_CONNECTIONS=false               # default false
ENABLE_ADMIN_CHAT_ACCESS=false                # default true
ENABLE_ADMIN_EXPORT=false                     # default true
ENABLE_COMMUNITY_SHARING=false                # default true
ENV=prod                                     # backend default dev; official Docker default prod
```

Set each restricted model's **Access Control to Private**, then grant only the intended users or groups access. Workspace Models Access governs creation and editing, not which existing models a user may invoke. Inspect existing grants after changing visibility. Current resource payloads use `access_grants`; do not copy an older `access_control` JSON example into current configuration. See [resource access](https://docs.openwebui.com/features/authentication-access/rbac/groups/), [workspace permissions](https://docs.openwebui.com/features/authentication-access/rbac/permissions/), and the [access-grant schema](https://docs.openwebui.com/reference/database-schema/).

Ollama pull, create, copy, and delete routes already require an administrator. There is no `ENABLE_MODEL_*` switch for those operations: the boundary is the caller's role. Restrict admin membership and keep the Ollama service itself private so callers cannot bypass Open WebUI. See the [Ollama route dependencies](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/ollama.py).

Pin the intended backend destinations in **Settings > Admin > Connections**. The initial OpenAI-compatible destination defaults to `https://api.openai.com/v1`; inspect every configured connection on an existing installation. These URLs specify where Open WebUI sends requests; they are **not an egress firewall**. Independently restrict outbound destinations, including metadata services and unintended internal networks, as described in [egress-metadata.md](egress-metadata.md). See [connection configuration](https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/) and the [URL defaults](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/config.py).

Keep Direct Connections disabled unless required. They send inference requests **from the browser to the provider**, bypassing the backend inference proxy; this setting is not a server-side SSRF defense. See [Direct Connections](https://docs.openwebui.com/features/chat-conversations/direct-connections/).

For chat confidentiality, disable **both** administrative chat access and administrative export, then restart. Otherwise export can expose conversations through a second surface. These controls restrict the application's admin features; they do not conceal data from an operator with database or deployment access. See the [admin control reference](https://docs.openwebui.com/reference/env-configuration/) and [chat-list and export enforcement](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/chats.py).

`ENABLE_COMMUNITY_SHARING=false` removes community sharing buttons and discovery UI. It does not disable every local sharing or export operation. Review the separate sharing permissions and existing shares where confidentiality requires them. See the [community-sharing reference](https://docs.openwebui.com/reference/env-configuration/).

Interactive API documentation is controlled by `ENV`: `/docs` and `/openapi.json` are registered only in `dev`. The backend defaults to `dev`; the official Docker image sets `prod`. Keep `ENV=prod` in production rather than relying on an unverified `ENABLE_SWAGGER_UI` variable. This removes documentation, not the APIs. See [application initialization](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/main.py), [backend defaults](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/env.py), and the [Dockerfile](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/Dockerfile).

## 7. Keep API keys off unless needed

```
ENABLE_API_KEYS=false                    # default false
USER_PERMISSIONS_FEATURES_API_KEYS=false # default false
```

If API clients are required, enable the global switch and grant `features.api_keys` only to selected groups under **Admin Panel > Users > Groups**. Keep the default permission false. Administrators can create keys whenever the global switch is enabled; ordinary users need the feature permission too. Keys inherit the owner's authority, so use an ordinary account for an ordinary application. See [API-key setup and permissions](https://docs.openwebui.com/features/authentication-access/api-keys/).

For an enabled deployment, restrict the routes:

```
ENABLE_API_KEYS=true
ENABLE_API_KEYS_ENDPOINT_RESTRICTIONS=true # default false
API_KEYS_ALLOWED_ENDPOINTS=/api/chat/completions,/api/models
```

The endpoint list is an example for inference and model discovery; remove anything the client does not need. It matches an exact path **and its slash-separated descendants**, not HTTP methods. For example, allowing `/api/models` also allows `/api/models/anything` through this particular check. Enforce narrower path-and-method rules at the proxy when required. The restrictions apply to API keys across the instance, not separately per key. See [API-key configuration](https://docs.openwebui.com/features/authentication-access/api-keys/) and [endpoint matching](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/utils/auth.py).

Disabling the global switch rejects existing API keys as well as preventing creation; it does not delete those keys, and it does **not** disable JWT-authenticated APIs. See the [separate API-key and JWT authentication paths](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/utils/auth.py).

`ENABLE_API_KEY`, `ENABLE_API_KEY_ENDPOINT_RESTRICTIONS`, and `API_KEY_ALLOWED_ENDPOINTS` are deprecated names. Use the plural names shown above; do not assume every deprecated name is still honored by every release. See the [environment reference](https://docs.openwebui.com/reference/env-configuration/).

## 8. Bound retrieval, network access, and resource use

```
ENABLE_LOCAL_WEB_FETCH=false          # default false
AIOHTTP_CLIENT_ALLOW_REDIRECTS=false  # default false
WEB_FETCH_FILTER_LIST=docs.example.com,!internal.example.com
ENABLE_WEB_SEARCH=false              # default false; keep off if unused
RAG_FILE_MAX_SIZE=10                  # example limit in MB; default unset
RAG_FILE_MAX_COUNT=5                  # example file count; default unset
USER_PERMISSIONS_CHAT_FILE_UPLOAD=false # default true
USER_PERMISSIONS_CHAT_WEB_UPLOAD=false  # default true
USER_PERMISSIONS_FEATURES_WEB_SEARCH=false # default true
```

Replace the filter domains with your intended policy. `WEB_FETCH_FILTER_LIST` is comma-separated: entries without `!` form an allowlist, while `!` entries deny destinations. Custom entries extend the built-in blocklist. Keep local fetch and redirects disabled to reduce SSRF paths into private networks and cloud metadata services; enforce network egress separately. `ENABLE_RAG_LOCAL_WEB_FETCH` is the deprecated alias of `ENABLE_LOCAL_WEB_FETCH`. See [web-fetch configuration](https://docs.openwebui.com/reference/env-configuration/), the [filter and alias definitions](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/config.py), and the [redirect default](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/env.py).

Choose finite positive file limits for the available storage and processing capacity. They are not an aggregate storage quota or a general request quota. In the upload handler, the size check occurs after the storage upload has read the file, so also bound request bodies at the proxy. See the [upload handler](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/files.py).

**The feature permissions above are not sufficient to prohibit direct ingestion requests.** `POST /api/v1/files/` and `POST /api/v1/retrieval/process/web` require a verified user, but their handlers do not check the corresponding file-upload or web-upload feature permission. A verified user means an authenticated `user` or `admin`, not a pending account. If uploads must be unavailable, deny `/api/v1/files/` and applicable ingestion routes at the proxy. If URL ingestion must be unavailable, deny `/api/v1/retrieval/process/web`, `/api/v1/retrieval/process/youtube` (the same handler), and `/api/v1/retrieval/process/url` (which fetches URLs and can invoke web processing or file ingestion). Audit group grants and prevent access around the proxy. See [file uploads](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/files.py), [URL ingestion](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/retrieval.py), and [verified-user roles](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/utils/auth.py).

The native password-signin limiter is **15 attempts per 180 seconds per email address**. It is not an inference quota. Add proxy rate and concurrency limits, plus provider or gateway spend limits, for authenticated requests as well as anonymous traffic. See the [signin limiter](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py), [nginx.md](nginx.md), and [litellm.md](litellm.md).

## 9. Verify

**REASONED:** whole Verify section; every service comparison below rests on the Sources entries cited at that comparison. During marking review (October 2026), the three then-current bash blocks ran from files under Bash 5.3.9(1)-release with a Python 3.14.4 harness and scratch-confined command stubs; each passed `bash -n` and ShellCheck 0.11.0 with exit 0 and no output. The refusal and substituted-input results are recorded at each block's declaration. Earlier declarations elsewhere in this section describe historical authoring runs, which were not independently reproduced in this review. No live Open WebUI, TLS ingress, second-host fixture, identity provider or provider test credentials were supplied for this review. No service response was observed, and the exposed and fixed service comparisons remain REASONED from the pinned source and linked vendor documentation. During marking review (2026-10-14), the block 2 and 3 stub cases were repeated after adding credential refusals; those results are recorded at their declarations. During marking review (2026-10-14), all three current Verify bash blocks were extracted to files and each passed Bash 5.3.9(1)-release `bash -n` and ShellCheck 0.11.0 with exit 0 and no output. These syntax and lint checks did not execute the blocks or repeat the stub cases.

**REASONED:** operating guidance for every comparison below; no live Open WebUI or ordinary and administrator test accounts in the authoring environment; it carries no command of its own, so nothing in it ran locally, and it rests on the verified-user roles in the guide's cited Open WebUI authentication helpers entry and the additive grants in the guide's cited Open WebUI groups entry: an administrator can pass a check that an ordinary user must fail, so an administrator's success alone cannot separate the exposed state from the fixed one. Run exposed comparisons only on a private, disposable installation. Keep production bootstrap private. Use ordinary users as well as administrators: an administrator's successful request does not demonstrate an ordinary user's boundary.

### Private binding, TLS, and ordinary signup

**REASONED:** This needs a deployed container, TLS ingress, and a second LAN/VPC host, unavailable here. The original listener, TLS, feature-flag, and browser checks are retained below with guarded URL substitution. Substitute your actual HTTPS origin inside the quotes on the `set --` line. Paste the whole block; do not put credentials in URLs. Values containing a literal apostrophe require proper shell quoting rather than direct substitution.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'https://chat.example.com'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "provide exactly one HTTPS origin; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[[:cntrl:]]*)
      echo "substitute your HTTPS origin inside the quotes; not probing"; exit 1 ;;
    https://*@*)
      echo "use an HTTPS origin without credentials; not probing"; exit 1 ;;
    https://*)
      ss -tlnp   # read every listener; the published mapping should be 127.0.0.1:3000 only, never 0.0.0.0 or ::.
                 # ss shows host listeners, not Docker's NAT: use Docker Engine 28.0+ for loopback publishing
                 # (older engines let a same-L2 host reach a localhost-published port), confirm the mapping is
                 # 127.0.0.1:3000->8080/tcp, and from another LAN/VPC host confirm nothing answers on port 3000.
      curl -q -g -sSI --noproxy '*' --connect-timeout 5 --max-time 20 \
        -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "${1%/}/"
                                           # serves over TLS without -k; --noproxy so a client proxy cannot answer
      # Signup state, programmatically: Open WebUI serves its feature flags at /api/config.
      curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 "${1%/}/api/config"
                                           # JSON feature flags; confirm signup is disabled there (features.enable_signup: false)
      # In a private browser window, AFTER your admin account exists: the sign-up option is absent AND an actual
      # registration attempt is REFUSED (a missing button alone is not proof). With signup on, registering a new
      # account yields a pending/unapproved user, not access.
      ;;
    *) echo "use an HTTPS origin without credentials; not probing"; exit 1 ;;
  esac
)
```

**REASONED:** preceding block; covers the listener read, certificate-validated HTTPS request, `/api/config` signup flag and browser registration attempt. No live Open WebUI, TLS ingress or second LAN/VPC host was supplied for marking review; publication expectations rest on the cited Docker port publishing entry and signup expectations on the cited Open WebUI auth routes and configuration defaults. During marking review (October 2026), the current block ran from files under Bash 5.3.9(1)-release with stub ss and curl: the written placeholder, empty value, literal LF and angle-bracket value printed the substitution refusal; zero or two values printed the exactly-one-origin refusal; omitting the initial `set --` line with a caller argument printed the whole-block refusal; HTTP, the three userinfo forms `https://user:pw@chat.internal`, `https://user@chat.internal` and `https://@chat.internal`, and an @ in a path, query or fragment printed the HTTPS-without-credentials refusal; each exited 1 without calling a stub. Valid `https://chat.internal`, its trailing-slash form, an explicit port and a bracketed IPv6 origin reached `ss -tlnp` and both curl stubs and exited 0; the valid origin also exited 0 under `bash -u`. Static reasoning: an HTTPS authority containing userinfo has a literal @ and matches the refusal arm, whereas a valid HTTPS origin has no @. Inputs with a path, query or fragment are URLs rather than origins. The guard is not a complete origin validator. No listener, TLS, feature-flag or browser result was observed. Expected exposed signup reports `features.enable_signup: true` and admits pending registration; fixed signup reports `false` and refuses registration. Expected exposed publication is reachable externally or lacks working certificate-validated HTTPS; the fixed deployment serves HTTPS and publishes only the intended loopback mapping. A certificate error, local socket error or DNS failure does not prove private ingress. See [Docker port publishing](https://docs.docker.com/engine/network/port-publishing/).

**REASONED:** following block; from the separate LAN/VPC host, probe the actual Open WebUI host address, per the cited Docker port publishing entry. This second host is unavailable here. During marking review (October 2026), the then-current block ran from files under Bash 5.3.9(1)-release with a curl stub: the written placeholder, empty value, literal LF and angle-bracket value printed the substitution refusal, zero or two host values printed the exactly-one-host refusal, and omitting the initial `set --` line with a caller argument printed the whole-block refusal, each exiting 1 without calling curl; `127.0.0.1` and `[::1]` each reached only the curl stub with the corresponding HTTP URL on port 3000 and exited 0. These runs observed no network boundary. For IPv6, put the literal address in square brackets inside the quotes. A privately isolated exposed fixture should answer on port 3000; the fixed publication must not. Confirm that the intended HTTPS service still works and inspect the reported error before attributing a failure to the network boundary. During marking review (2026-10-14), the updated block ran from a file under Bash 5.3.9(1)-release with a scratch-confined curl stub: all cases recorded above repeated with the same messages and exit statuses; `user:pw@host`, `user@host`, `@host`, `host/path@tail`, `host?q=@tail` and `host#@tail` each printed "use a host address without credentials; not probing", exited 1 and called no stub. No network boundary was observed.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_OPENWEBUI_HOST_IP'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 1 ] || { echo "provide exactly one host address; not probing"; exit 1; }
  case "$1" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[[:cntrl:]]*)
      echo "substitute the actual host address inside the quotes; not probing"; exit 1 ;;
    *@*)
      echo "use a host address without credentials; not probing"; exit 1 ;;
    *)
      curl -q -g -sS -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 20 \
        -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:3000/"
      ;;
  esac
)
```

### Protected requests for the comparisons below

**REASONED:** preparation for the protected request block below; the Bearer header and API-key use rest on the Sources entries [Open WebUI API endpoints: model discovery, chat requests, ingestion, and development documentation (rolling documentation, checked September 2026)](https://docs.openwebui.com/reference/api-endpoints/) and [Open WebUI API keys: global enablement, group permissions, and inherited authority (rolling documentation, checked September 2026)](https://docs.openwebui.com/features/authentication-access/api-keys/); with no live Open WebUI or test identity in the authoring environment only the file handling ran locally: a mode-0600 header file in a mode-0700 directory, an empty header file and an empty body file were created, and with `curl` stubbed the block accepted the empty header file as an anonymous request and passed each file to curl only as an `@` path (`-H`, `--data-binary`, or `-F file=` for `UPLOAD`), so no file content reached the command line. Prepare a mode-0600 header file in a private directory containing `Authorization: Bearer ` followed by the disposable test JWT or API key. Use an empty file for anonymous requests. Put JSON request bodies, including signup passwords, in a separate protected file; use an empty body file for GET. For `UPLOAD`, the body file is the harmless file to upload.

**REASONED:** endpoint and response guidance for the protected request block below; signin, signup and API-key responses rest on the Sources entry [Open WebUI auth routes: first-admin signup, auto-disable, password-auth ordering, trusted-header provisioning, signin limiter, and API-key creation](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py), and export responses on [Open WebUI chat router: administrative chat access and export checks](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/chats.py); with no live Open WebUI in the authoring environment only the guard and response directory ran locally, against a stub `curl`: the block accepted `https://chat.internal/api/models` and `http://127.0.0.1:3000/docs`, refused `http://chat.internal/api/models` and `http://127.0.0.1:8080/api/models` with "use HTTPS or the loopback backend; not probing", refused an unsubstituted `REPLACE_WITH_TEST_USER_ID` path with "substitute every placeholder inside the quotes; not probing", and created each private response directory with mode 0700. No response content was observed. Use the actual HTTPS endpoint, or `http://127.0.0.1:3000/...` on the backend host. Replace placeholders inside the quoted arguments. Responses are captured privately because signin, signup, API-key, and export responses can contain credentials or private data.

**REASONED:** following block; protected requests support the comparisons below from the cited Open WebUI handlers; no live deployment or test identities are available.

```bash
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ENDPOINT_URL' 'GET' 'REPLACE_WITH_HEADER_FILE' 'REPLACE_WITH_BODY_FILE'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block; not probing"; exit 1; }
  shift
  [ "$#" -eq 4 ] || { echo "provide endpoint, method, header file and body file; not probing"; exit 1; }
  case "|$1|$2|$3|$4|" in
    *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|*'||'*|*[[:cntrl:]]*)
      echo "substitute every placeholder inside the quotes; not probing"; exit 1 ;;
  esac
  case "$1" in
    https://*@*|http://127.0.0.1:3000/*@*)
      echo "use an endpoint without credentials; not probing"; exit 1 ;;
    https://*|http://127.0.0.1:3000/*)
      [ -r "$3" ] || { echo "header file is unreadable"; exit 1; }
      [ -r "$4" ] || { echo "body file is unreadable"; exit 1; }
      case "$2" in
        GET|POST|DELETE|UPLOAD) ;;
        *) echo "use GET, POST, DELETE or UPLOAD; not probing"; exit 1 ;;
      esac
      umask 077
      set -- "$@" "$(mktemp -d)" || exit 1
      [ -d "$5" ] || { echo "cannot create private results directory"; exit 1; }
      printf 'Private response directory: %s\n' "$5"
      case "$2" in
        GET)
          curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 60 \
            -H "@$3" -o "$5/body" -D "$5/headers" \
            -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
          ;;
        POST)
          curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 60 \
            -H "@$3" -H 'Content-Type: application/json' --data-binary "@$4" \
            -o "$5/body" -D "$5/headers" \
            -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
          ;;
        DELETE)
          curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 60 \
            --request DELETE \
            -H "@$3" -H 'Content-Type: application/json' --data-binary "@$4" \
            -o "$5/body" -D "$5/headers" \
            -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
          ;;
        UPLOAD)
          curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 60 \
            -H "@$3" -F "file=@$4" -o "$5/body" -D "$5/headers" \
            -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
          ;;
      esac
      ;;
    *) echo "use HTTPS or the loopback backend; not probing"; exit 1 ;;
  esac
)
```

**REASONED:** preceding block; covers its guard and all four request modes. No live Open WebUI or test identities were supplied for marking review; each service comparison states its expected exposed and fixed outcomes where it uses the block, per the Sources entries cited there. During marking review (October 2026), the then-current block ran from files under Bash 5.3.9(1)-release with scratch-confined curl and mktemp stubs: the written placeholders and a placeholder, empty value or literal LF in each of the four argument positions printed the substitution refusal; three or five values printed the four-argument refusal; omitting the initial `set --` line with a caller argument printed the whole-block refusal; `http://chat.internal/api/models` and `http://127.0.0.1:8080/api/models` printed the HTTPS-or-loopback refusal; nonexistent header and body paths separately printed the corresponding unreadable-file message; PATCH printed the supported-method refusal; each exited 1 without calling curl or mktemp or creating a results directory. GET, POST, DELETE and UPLOAD at `https://chat.internal/api/models`, and GET at `http://127.0.0.1:3000/docs`, each exited 0 with empty readable header and body fixtures, called the mktemp stub's scratch-only directory helper, created one mode-0700 results directory and reached the curl stub. Each passed the header file as an `@` path; POST and DELETE supplied JSON content type and body-file `@` paths, DELETE added `--request DELETE`, and UPLOAD supplied `file=@` with the body-file path. Static reasoning: the outer method case admits only these four methods and the intervening `set --` appends a directory without changing the method, so no inner default arm is needed. No response content was observed. The guard checks arguments, not file contents. Inspect request files before sending them, especially registration bodies and requests captured from administrative actions. Do not use a production credential for an exposed comparison. Remove test accounts, keys, uploads, and private response files after recording redacted evidence. During marking review (2026-10-14), the updated block ran from a file under Bash 5.3.9(1)-release with scratch-confined curl and mktemp stubs: all cases recorded above repeated with the same messages and exit statuses; an embedded `REPLACE_WITH_TEST_USER_ID` endpoint also printed the substitution refusal and exited 1 without calling a stub. HTTPS endpoints with `user:pw@`, `user@` or empty userinfo, and HTTPS or allowed loopback endpoints containing @ in a path, query or fragment, each printed "use an endpoint without credentials; not probing", exited 1 and called neither stub nor created a results directory. Accepted runs again created mode-0700 response directories and passed request files as @ paths. No service response was observed.

### Authentication and provisioning

**REASONED:** Cookie attributes need a running Open WebUI, HTTPS ingress, disposable login, and configured OAuth provider; no container runtime or live fixture is available here. With password signin enabled on the private fixture, use the protected helper to POST `/api/v1/auths/signin` with valid `email` and `password` fields; inspect the saved `headers` file for the `token` cookie. In a fresh browser, visit `/oauth/REPLACE_WITH_CONFIGURED_PROVIDER/login` with the provider substituted, complete login, and inspect `Set-Cookie` headers throughout the flow for `owui-session`. With both Secure settings false and no proxy cookie rewriting, issued cookies should lack `Secure`. After setting both true and restarting, repeat through public HTTPS: require `Secure` and `HttpOnly` on both cookies and check `SameSite` against the intended configuration (`lax` by default). A response that issues no relevant cookie is inconclusive; record unused flows as not applicable. Redact cookie values. See [auth cookie creation](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py), [session middleware](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/main.py), and [cookie defaults](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/env.py).

**REASONED:** These comparisons require a running disposable Open WebUI, controlled accounts, a trusted proxy, an identity provider, and optional shared Redis, unavailable here. Use the protected request block and the specified browser flows.

| Control | Concrete comparison and expected outcomes |
| --- | --- |
| Ordinary signup and first-admin exception | **REASONED:** whole row; no container runtime or live Open WebUI with an empty and a bootstrapped database in the authoring environment, per the guide's cited Open WebUI auth routes and Open WebUI configuration defaults entries. Locally, the protected request block in POST mode for `https://chat.internal/api/v1/auths/signup`, with an empty header file and a JSON body that jq parsed, reached only a stub curl with those arguments. Expected: on an empty database with the login form enabled, signup bootstraps an administrator even with `ENABLE_SIGNUP=false`; after bootstrap, explicitly enabled signup admits a pending account (exposed) and disabled signup returns 403 (fixed). POST `/api/v1/auths/signup` anonymously with valid `name`, `email`, and `password` fields in the protected body. On an empty fixture with the login form enabled, even `ENABLE_SIGNUP=false` permits bootstrap. After bootstrap, explicitly enabled signup admits a pending account; disabled signup returns 403. See the [signup handler](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py). |
| OAuth provisioning | **REASONED:** whole row; no identity provider, browser session or live Open WebUI in the authoring environment, per the guide's cited Open WebUI SSO and Open WebUI configuration defaults entries. The row is a browser flow with no command or literal configuration, so nothing in it ran locally. Expected: with OAuth signup enabled a new approved-domain identity is provisioned despite ordinary signup being off (exposed); with it disabled the new identity is not provisioned while an already-linked permitted account still signs in (fixed). In a fresh browser, visit `/oauth/REPLACE_WITH_CONFIGURED_PROVIDER/login`, substituting the configured provider, and complete login with a new approved-domain identity. With OAuth signup enabled, provisioning can occur despite ordinary signup being off; with it disabled, the new identity must not be provisioned. An already-linked permitted account should still sign in. Separately try an excluded domain. See [OAuth signup and domain controls](https://docs.openwebui.com/features/authentication-access/auth/sso/). |
| Trusted identity and password-auth ordering | **REASONED:** whole row; no trusted proxy, controlled accounts or live Open WebUI in the authoring environment, per the guide's cited Open WebUI auth routes and Open WebUI SSO entries. Locally, the protected request block in POST mode for `http://127.0.0.1:3000/api/v1/auths/signin`, with a header file holding a forged identity header and a signin body that jq parsed, reached only a stub curl, which received the header file as an `@` path. Expected: an unstripped forged administrator header impersonates that administrator (exposed); fixed ingress rejects it or replaces it with the authenticated identity (fixed); with `ENABLE_PASSWORD_AUTH=false`, `/signin` returns 403. POST `/api/v1/auths/signin` with the fixture's configured identity header in the protected header file and a valid signin-shaped JSON body. An unstripped forged admin header can impersonate that admin; fixed ingress must reject it or replace it with the authenticated identity. Separately, `ENABLE_PASSWORD_AUTH=false` makes `/signin` return 403 before trusted-header handling. See the [signin handler](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py). |
| Key persistence and token lifecycle | **REASONED:** whole row; no container runtime, replicas, shared Redis or live Open WebUI in the authoring environment, per the guide's cited Open WebUI authentication helpers, Open WebUI launcher and Open WebUI environment defaults entries. Locally, the protected request block in GET mode for `https://chat.internal/api/models` and in POST mode for `https://chat.internal/api/v1/auths/signout` with an empty body reached only a stub curl. Expected: with the same injected key the unexpired token keeps working across recreation and replicas, and a changed key rejects it; after signout the token stays usable until expiry without Redis (exposed) and is refused on every worker with working shared revocation (fixed). Sign in and save the JWT privately. GET `/api/models` before and after recreating the disposable container with the same data volume and injected key, then against each replica: the unexpired token should continue working. A changed signing key rejects it. POST `/api/v1/auths/signout`, then repeat GET using the saved token: without Redis it remains usable until expiry; with working shared revocation it is refused on every worker. Check expiry separately. See [token validation and revocation](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/utils/auth.py). |

### Execution, models, connections, and data

**REASONED:** These comparisons need a running UI, disposable users and groups, reviewed harmless plugins, a working model backend, and controlled connection targets, unavailable here. Save any browser-generated request used for replay into protected files; do not put its credentials in command arguments.

| Control | Concrete comparison and expected outcomes |
| --- | --- |
| Plugin execution | **REASONED:** whole row; no live Open WebUI, model backend or reviewed canary plugin in the authoring environment, per the guide's cited Open WebUI plugin loader and Open WebUI environment configuration reference entries. Locally, the protected request block in GET mode for `https://chat.internal/api/v1/functions/` and `https://chat.internal/api/v1/tools/` reached only a stub curl. Expected: the canary marker appears with plugins enabled (exposed) and the plugin no longer executes after disabling and restarting (fixed), when local plugins also disappear from both lists while external tool servers may remain. With a reviewed canary Tool or Function enabled on the private fixture, submit a chat that invokes it and record its harmless marker. Disable plugins, restart, and repeat the same chat request: the plugin must no longer execute. GET `/api/v1/functions/` and `/api/v1/tools/` too; local plugins disappear, while external tool servers may remain. A management request being accepted does not by itself mean execution is enabled. See [plugin loading](https://docs.openwebui.com/features/extensibility/plugin/development/under-the-hood/) and [the switch's scope](https://docs.openwebui.com/reference/env-configuration/). |
| Additive group permissions | **REASONED:** whole row; no live Open WebUI, test users or groups in the authoring environment, per the guide's cited Open WebUI groups entry. The creation request is replayed from the browser through the protected request block, whose POST mode, run with other endpoints, reached only a stub curl locally; nothing else in the row can run here. Expected: with a group Tools Access grant the ordinary user saves the reviewed Tool (exposed); with the grant removed from every membership the same valid request is refused (fixed), and a false grant in a second group is not a deny. With plugins enabled only on the private fixture, give a test user a group Tools Access grant while the default remains false. Save a reviewed harmless Tool through the workspace. Remove the grant from every membership and repeat the same valid creation request: ordinary-user authorization must refuse it. A false grant in a second group must not be mistaken for a deny. See [permission merging](https://docs.openwebui.com/features/authentication-access/rbac/groups/). |
| Code execution | **REASONED:** whole row; no live Open WebUI or configured code-execution engine in the authoring environment, per the guide's cited Open WebUI hardening and Open WebUI configuration defaults entries. Locally, the harmless payload ran under the authoring Python 3: `print(1 + 1)` printed `2`, the marker an enabled execution path should show. Expected: the chat code block and the code-interpreter request execute before their switches are disabled (exposed) and those paths are unavailable afterwards (fixed). On the private fixture, compare execution of a harmless `print(1 + 1)` chat code block and a code-interpreter request before and after disabling their respective switches. Record browser and configured-engine activity separately; after disabling, those execution paths should be unavailable. This does not test terminals or server-side plugins. See [code-execution controls](https://docs.openwebui.com/getting-started/advanced-topics/hardening/). |
| Model access | **REASONED:** whole row; no live Open WebUI, configured test model or test users in the authoring environment, per the guide's cited Open WebUI groups and Open WebUI API endpoints entries. Locally, the protected request block in GET mode for `https://chat.internal/api/models` and in POST mode for `https://chat.internal/api/chat/completions` with a chat body that jq parsed reached only a stub curl. Expected: an excluded user who can still invoke the model is the exposed outcome; after the model is made Private the user with a read grant still obtains a completion while the excluded user cannot invoke it or create workspace models (fixed). GET `/api/models`, then POST a minimal valid chat to `/api/chat/completions` using a configured test model. Compare a user with a read grant and one without it after making the model Private. The authorized user must still obtain a completion; the excluded user must not invoke that model. Also confirm the excluded user cannot create workspace models. See [model access grants](https://docs.openwebui.com/features/authentication-access/rbac/groups/) and [API request examples](https://docs.openwebui.com/reference/api-endpoints/). |
| Ollama administration | **REASONED:** whole row; no isolated Ollama backend, test administrator and ordinary accounts or live Open WebUI in the authoring environment, per the guide's cited Open WebUI Ollama router entry. Locally, the protected request block in DELETE mode for `https://chat.internal/ollama/api/delete` and `http://127.0.0.1:3000/ollama/api/delete/0`, with a body holding a `model` field that jq parsed, reached only a stub curl as `--request DELETE` with the JSON content type and the body file. Expected: an ordinary user completing the operation is the exposed outcome; ordinary users receive authorization refusal before the backend operation while the matched administrator request succeeds (fixed). On an isolated backend, capture valid pull, create, copy, and delete requests for disposable model resources. Use `DELETE /ollama/api/delete` for deletion (or `/ollama/api/delete/{url_idx}` with the actual backend index), selecting `DELETE` in the protected helper and putting the disposable model's `model` field in the protected JSON body. Replay each with an ordinary user's JWT, then an administrator's JWT. Ordinary users must receive authorization refusal before the backend operation; matched admin requests establish that the payload and backend work. Never test deletion against a production model. See [Ollama administrative routes](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/ollama.py). |
| Connection destinations | **REASONED:** whole row; no approved backend connection, controlled excluded destination, egress records or live Open WebUI in the authoring environment, per the guide's cited Open WebUI OpenAI-compatible connections and Open WebUI Direct Connections entries; the exclusion itself is the network policy from egress-metadata.md, not an Open WebUI control. A canary chat can use the protected request block, whose POST mode for `https://chat.internal/api/chat/completions` reached only a stub curl locally; the egress and browser records cannot be produced here. Expected: a request reaching the excluded destination is the exposed outcome; the approved destination works while the excluded one receives no request (fixed); browser-to-provider inference appears with Direct Connections enabled and is absent when disabled. Send a canary chat through each approved backend connection and inspect backend egress records. In a private fixture with disposable credentials, compare an approved destination with a controlled destination excluded by the network policy. The latter must receive no request while the approved destination works. If testing Direct Connections, browser network records should show browser-to-provider inference when enabled and its absence when disabled. See [Direct Connections](https://docs.openwebui.com/features/chat-conversations/direct-connections/) and [egress-metadata.md](egress-metadata.md). |
| Administrative chat access and export | **REASONED:** whole row; no live Open WebUI, test administrator and user accounts or canary chats in the authoring environment, per the guide's cited Open WebUI chat router and Open WebUI environment defaults entries. Locally, the protected request block refused the unsubstituted `REPLACE_WITH_TEST_USER_ID` path with "substitute every placeholder inside the quotes; not probing", and in GET mode with a substituted ID and for `/api/v1/chats/all/db` reached only a stub curl. Expected: with the controls enabled both requests expose the canary chats (exposed); after disabling both and restarting both are refused while the chat owner keeps normal access (fixed). As an admin, GET `/api/v1/chats/list/user/REPLACE_WITH_TEST_USER_ID` and `/api/v1/chats/all/db`, substituting the test user ID. With the controls enabled, the fixture exposes its canary chats. After disabling both controls and restarting, both requests must be refused; the chat owner must retain normal access. See [chat-list and export enforcement](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/chats.py). |
| Documentation and community UI | **REASONED:** whole row; no isolated `ENV=dev` and `ENV=prod` fixtures or live Open WebUI in the authoring environment, per the guide's cited Open WebUI application initialization, Open WebUI environment defaults and Open WebUI environment configuration reference entries. Locally, the protected request block in GET mode for `http://127.0.0.1:3000/docs` and `https://chat.internal/openapi.json` with an empty header file reached only a stub curl. Expected: Swagger and the OpenAPI schema are served under `ENV=dev` (exposed) and disappear under `ENV=prod` (fixed); with community sharing disabled the discovery sections and share buttons disappear. GET `/docs` and `/openapi.json` on the backend and public origin. Compare an isolated `ENV=dev` fixture with `ENV=prod`: Swagger and the OpenAPI schema must disappear. Inspect content, since a 200 response containing the application shell is not API documentation. With community sharing disabled, inspect the workspace discovery sections and community-share buttons; their disappearance does not demonstrate that local export or sharing is disabled. See [documentation registration](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/main.py) and [community UI scope](https://docs.openwebui.com/reference/env-configuration/). |

### API keys, ingestion, and resource limits

**REASONED:** These comparisons require a live deployment, disposable API keys, controlled web destinations, proxy logs, and an approved bounded provider allowance, unavailable here.

| Control | Concrete comparison and expected outcomes |
| --- | --- |
| API-key enablement and scope | **REASONED:** whole row; no live Open WebUI, ordinary-user API key or JWT in the authoring environment, per the guide's cited Open WebUI API keys and Open WebUI authentication helpers entries. Locally, the protected request block in GET mode for `https://chat.internal/api/models` and `https://chat.internal/api/v1/auths/` with a dummy key header file reached only a stub curl. Expected: an existing key that still works after the global switch is disabled is the exposed outcome; disabled, the key is refused while a valid JWT works; with the step 7 allowlist `/api/models` is permitted and `/api/v1/auths/` refused for the key; with the API-key permission removed from every group the permitted request fails (fixed). With a selected ordinary user's working key, GET `/api/models`. Disable the global key switch and repeat: the existing key must be refused while a valid JWT still works. Re-enable keys with the step 7 allowlist: `/api/models` remains permitted, while GET `/api/v1/auths/` is refused for the key. Remove the user's API-key permission from every group and repeat the permitted request: it must now fail. Use real existing routes when testing descendants and methods; a nonexistent route's 404 proves no scope boundary. See [key permissions](https://docs.openwebui.com/features/authentication-access/api-keys/) and [endpoint enforcement](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/utils/auth.py). |
| Upload permission limitation and body limits | **REASONED:** whole row; no live Open WebUI, verified ordinary user or restricting proxy in the authoring environment, per the guide's cited Open WebUI file router entry. Locally, the protected request block in UPLOAD mode for `https://chat.internal/api/v1/files/` reached only a stub curl, which received the harmless file as `file=`. Expected: with the UI feature permission false and no proxy route block the handler still accepts the upload (exposed); with the proxy restriction it is refused (fixed); where uploads are allowed, the smaller file works and the larger one is refused. Use `UPLOAD` with `/api/v1/files/` and a small harmless document as a verified ordinary user. With the UI feature permission false but no proxy route block, the direct handler can still accept it. With the intended proxy restriction, it must be refused. Where uploads are allowed, compare files just below and above the chosen size limit, including multipart overhead in the proxy limit. Confirm the smaller upload works. Test the configured file count separately; it does not establish an aggregate quota. See [upload enforcement](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/files.py). |
| URL ingestion and SSRF | **REASONED:** whole row; no live Open WebUI, controlled test pages, proxy or egress logs in the authoring environment, per the guide's cited Open WebUI retrieval router, Open WebUI hardening, Open WebUI configuration defaults and Open WebUI environment defaults entries. Locally, the protected request block in POST mode for each of the three routes with `?process=false`, and a body holding `url` that jq parsed, reached only a stub curl with the query string intact. Expected: without proxy denial each route can fetch the page despite the disabled UI permission (exposed); with proxy denial each is refused before its handler with no destination contact, and fixed controls prevent forbidden contact while the allowed page succeeds (fixed). POST `/api/v1/retrieval/process/web?process=false` with a JSON body containing `url` set to your controlled test page. Compare an allowed public destination, a controlled private destination, a filter-denied destination, and a redirect to the controlled private destination. Inspect destination and egress logs. Fixed controls must prevent forbidden contact while the allowed page succeeds. Where URL ingestion is prohibited, directly POST to each of `/api/v1/retrieval/process/web?process=false`, `/api/v1/retrieval/process/youtube?process=false`, and `/api/v1/retrieval/process/url?process=false` using a verified ordinary user's JWT and the protected JSON body containing the controlled public page's `url`. On the private fixture without proxy denial, establish that each request can fetch the page despite the disabled UI permission. With proxy denial, each must be refused before reaching its handler, with no destination contact; confirm this in proxy and destination logs. A malformed request or failed fetch does not demonstrate prohibition. Never probe real metadata services. See [URL ingestion](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/retrieval.py) and [outbound fetch protections](https://docs.openwebui.com/getting-started/advanced-topics/hardening/). |
| Search, rate, and spend | **REASONED:** whole row; no live Open WebUI, controlled search provider, proxy rate limit or bounded provider allowance in the authoring environment, per the guide's cited Open WebUI hardening and Open WebUI configuration defaults entries. Locally, the protected request block in POST mode for `https://chat.internal/api/chat/completions` reached only a stub curl; no series was sent. Expected: excess requests that still reach the provider are the exposed outcome; under-limit requests work and excess requests are refused by the configured limiting layer without further provider work (fixed); disabling web search stops calls to the controlled search provider. Compare a harmless search-enabled chat on the private fixture before and after disabling web search; check the controlled search provider for calls. Separately submit a bounded series of valid `/api/chat/completions` requests across the chosen proxy rate threshold and provider/gateway spend threshold. Under-limit controls must work; excess requests must be refused by the configured limiting layer without further provider work. The signin limiter is not evidence for either result. See [network-layer limits](https://docs.openwebui.com/getting-started/advanced-topics/hardening/), [nginx.md](nginx.md), and [litellm.md](litellm.md). |

### Verification scope

**REASONED:** whole Verify section, summarizing the units above; no container runtime, network access or live Open WebUI in the authoring environment, per the Sources entries cited at each comparison; the only local runs are the shell, guard, stub, jq and Python checks recorded at the start of this section and at the units above that record them, which observed no service response. The original probes and the new controls are REASONED from the pinned source and linked vendor documentation. Configuration inspection alone does not demonstrate service behavior. Deployment checks must explicitly record the DELETE model comparison, individual proxy refusal for all three URL-ingestion routes, and exposed/fixed authentication and session `Set-Cookie` attributes.

| Check scope | Deployment comparison and prerequisites | Status |
| --- | --- | --- |
| Service comparisons | Demonstrate every REASONED comparison above on a recorded Open WebUI release and image digest, with disposable data, a second-host IPv4/IPv6 ingress fixture, controlled users/groups, OAuth and trusted-header fixtures, shared Redis and multiple workers, reviewed canary plugins, an Ollama test backend, controlled web destinations, and bounded provider credentials. Include first-admin signup with an empty database and signup disabled; bootstrap with the login form disabled; signup auto-disable and persistence; password-auth ordering; forged-header rejection; OAuth signup/domain boundaries; signing-key persistence across recreation and replicas; expiry and signout revocation; additive permissions; plugin and code-execution separation; model access and administrative operations; destination controls; admin chat/export refusal; documentation and community UI scope; API-key disablement and endpoint matching; direct ingestion despite UI permissions; file limits, SSRF and redirects; and proxy/provider rate and spend enforcement. Record commands, response content, positive controls, versions, propagation timing, costs, and cleanup. | **REASONED:** every comparison listed in this row; none ran, because the authoring environment has no container runtime, network access or live Open WebUI and none of the fixtures listed, per the Sources entries cited at each comparison above; only the local shell, guard, stub, jq and Python checks recorded at the start of this section and at the units above that record them ran, and each comparison above states its expected exposed and fixed outcomes. REASONED from the pinned source and linked vendor documentation; service behavior is not demonstrated. |

## Sources (checked September 2026)

- Open WebUI environment configuration reference (rolling documentation, checked September 2026): https://docs.openwebui.com/reference/env-configuration
- Open WebUI FAQ (the first account created becomes the administrator): https://docs.openwebui.com/faq
- Open WebUI repository (the Docker Quick Start `-v open-webui:/app/backend/data` data volume): https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/README.md
- Docker port publishing (localhost publishing; releases older than 28.0.0 let a same-L2 host reach a localhost-published port): https://docs.docker.com/engine/network/port-publishing/
- [Open WebUI pinned release version](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/package.json).
- [Open WebUI configuration defaults: signup, permissions, OAuth, code execution, API keys, connections, retrieval limits, and web-fetch filters](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/config.py).
- [Open WebUI environment defaults: authentication, signing-key requirement, trusted headers, plugins, model bypass, admin chat access, redirects, and ENV](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/env.py).
- [Open WebUI launcher: persistent key-file generation and loading](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/start.sh).
- [Open WebUI Dockerfile: backend working directory and production environment](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/Dockerfile).
- [Open WebUI auth routes: first-admin signup, auto-disable, password-auth ordering, trusted-header provisioning, signin limiter, and API-key creation](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/auths.py).
- [Open WebUI authentication helpers: HS256 signing, Redis revocation, API-key enforcement, path matching, and verified-user roles](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/utils/auth.py).
- [Open WebUI application initialization: environment-based admin creation, API documentation, and OAuth routes](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/main.py).
- [Open WebUI Ollama router: model access and administrator-only management operations](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/ollama.py).
- [Open WebUI chat router: administrative chat access and export checks](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/chats.py).
- [Open WebUI file router: verified-user upload dependency and size enforcement](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/files.py).
- [Open WebUI retrieval router: web and URL ingestion handlers](https://raw.githubusercontent.com/open-webui/open-webui/0a7c15832fb30b1903753e83f81dc7d27e5b0944/backend/open_webui/routers/retrieval.py).
- [Open WebUI hardening: registration lifecycle, execution controls, network limits, and outbound protections (rolling documentation, checked September 2026)](https://docs.openwebui.com/getting-started/advanced-topics/hardening/).
- [Open WebUI SSO: OAuth/OIDC, trusted headers, and OAuth persistence (rolling documentation, checked September 2026)](https://docs.openwebui.com/features/authentication-access/auth/sso/).
- [Open WebUI plugin loader: exec and server-process authority (rolling documentation, checked September 2026)](https://docs.openwebui.com/features/extensibility/plugin/development/under-the-hood/).
- [Open WebUI groups: additive permissions and private resource grants (rolling documentation, checked September 2026)](https://docs.openwebui.com/features/authentication-access/rbac/groups/).
- [Open WebUI permissions: workspace and sharing controls (rolling documentation, checked September 2026)](https://docs.openwebui.com/features/authentication-access/rbac/permissions/).
- [Open WebUI database schema: normalized access grants (rolling documentation, checked September 2026)](https://docs.openwebui.com/reference/database-schema/).
- [Open WebUI API keys: global enablement, group permissions, and inherited authority (rolling documentation, checked September 2026)](https://docs.openwebui.com/features/authentication-access/api-keys/).
- [Open WebUI Direct Connections: browser-to-provider inference (rolling documentation, checked September 2026)](https://docs.openwebui.com/features/chat-conversations/direct-connections/).
- [Open WebUI OpenAI-compatible connections: administrative provider configuration (rolling documentation, checked September 2026)](https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/starting-with-openai-compatible/).
- [Open WebUI API endpoints: model discovery, chat requests, ingestion, and development documentation (rolling documentation, checked September 2026)](https://docs.openwebui.com/reference/api-endpoints/).
