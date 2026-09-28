---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "7d647297dab9e9fef3508f7f6df980f890f3909ee349755d77f0aa1429302791",
  "components": {
    "portainer": {
      "name": "Portainer",
      "basis": "unknown",
      "sources": {
        "s3e163c7d3c38": "https://docs.portainer.io/start/install-ce/server/docker/linux",
        "s115489d2f86f": "https://docs.portainer.io/start/install-ce/server/setup",
        "s59297757a042": "https://docs.portainer.io/admin/settings/authentication",
        "s8901bbe7c3d3": "https://docs.portainer.io/admin/settings/authentication/oauth"
      }
    },
    "coolify": {
      "name": "Coolify",
      "basis": "unknown",
      "sources": {
        "s41e2d21202d9": "https://coolify.io/docs/start-with-self-hosted",
        "sf2ae62425b35": "https://coolify.io/docs/core/infrastructure/servers/firewall",
        "sf5d819d5d87d": "https://coolify.io/docs/core/networking/proxy/overview",
        "s90addf9d8d5d": "https://coolify.io/docs/core/networking/dns",
        "s683244a61c48": "https://coolify.io/docs/core/infrastructure/servers/openssh"
      }
    },
    "dokploy": {
      "name": "Dokploy",
      "basis": "unknown",
      "sources": {
        "sc2cc854c9b7e": "https://docs.dokploy.com/docs/core/installation"
      }
    },
    "npm": {
      "name": "Nginx Proxy Manager",
      "basis": "unknown",
      "sources": {
        "se553d384e783": "https://nginxproxymanager.com/setup/"
      }
    },
    "vaultwarden": {
      "name": "Vaultwarden docs",
      "basis": "unknown",
      "sources": {
        "s0bbe8ad856cd": "https://github.com/dani-garcia/vaultwarden/wiki/Enabling-admin-page",
        "s6d3d0d02dcc9": "https://github.com/dani-garcia/vaultwarden/wiki/Disable-registration-of-new-users",
        "s60d064cae50e": "https://github.com/dani-garcia/vaultwarden/wiki/Enabling-HTTPS"
      }
    },
    "vaultwarden-pin": {
      "name": "Vaultwarden config",
      "basis": "3347698712d3e99e652ad4394ef2fc0ce2800fdd",
      "sources": {
        "s31c5fc79f5a0": "https://github.com/dani-garcia/vaultwarden/blob/3347698712d3e99e652ad4394ef2fc0ce2800fdd/.env.template"
      }
    },
    "dashboard": {
      "name": "Dashboard docs",
      "basis": "unknown",
      "sources": {
        "s73a36a43f6b5": "https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/"
      }
    },
    "dashboard-old": {
      "name": "Dashboard arguments",
      "basis": "v2.7.0",
      "sources": {
        "sacea2944651e": "https://github.com/kubernetes-retired/dashboard/blob/v2.7.0/docs/common/dashboard-arguments.md"
      }
    },
    "jenkins": {
      "name": "Jenkins",
      "basis": "unknown",
      "sources": {
        "s524c8d5871f1": "https://www.jenkins.io/doc/book/security/managing-security/",
        "sdfee751aeeee": "https://www.jenkins.io/doc/book/security/access-control/",
        "s6f5287fd36d4": "https://www.jenkins.io/doc/book/security/csrf-protection/"
      }
    },
    "gitea": {
      "name": "Gitea docs",
      "basis": "unknown",
      "sources": {
        "s57933519c308": "https://docs.gitea.com/administration/config-cheat-sheet",
        "s3b7060d58383": "https://docs.gitea.com/usage/user-setting/multi-factor-authentication/"
      }
    },
    "gitlab": {
      "name": "GitLab CE",
      "basis": "unknown",
      "sources": {
        "s3b7ac561a92e": "https://docs.gitlab.com/install/docker/installation/",
        "s6e8d16cad2ef": "https://docs.gitlab.com/administration/settings/sign_up_restrictions/",
        "s6b8a68a77e17": "https://docs.gitlab.com/administration/settings/visibility_and_access_controls/",
        "s0347014ce554": "https://docs.gitlab.com/security/two_factor_authentication/"
      }
    },
    "kuma": {
      "name": "Uptime Kuma",
      "basis": "unknown",
      "sources": {
        "s05b853ba300b": "https://github.com/louislam/uptime-kuma",
        "sed52bfca4039": "https://github.com/louislam/uptime-kuma/wiki/Reverse-Proxy"
      }
    },
    "docker": {
      "name": "Docker Engine",
      "basis": "unknown",
      "sources": {
        "sfe15a8156c18": "https://docs.docker.com/engine/security/protect-access/",
        "s1b5ec54421b0": "https://docs.docker.com/engine/daemon/remote-access/"
      }
    },
    "dozzle": {
      "name": "Dozzle",
      "basis": "unknown",
      "sources": {
        "s45b3eab2515b": "https://dozzle.dev/guide/authentication"
      }
    },
    "filebrowser": {
      "name": "Filebrowser",
      "basis": "unknown",
      "sources": {
        "s6386c9e2356b": "https://github.com/filebrowser/filebrowser"
      }
    },
    "nodered": {
      "name": "Node-RED",
      "basis": "unknown",
      "sources": {
        "sa94f329023fe": "https://nodered.org/docs/user-guide/runtime/securing-node-red"
      }
    },
    "gitea-pin": {
      "name": "Gitea listener",
      "basis": "v1.27.3",
      "sources": {
        "s31dd622b1c12": "https://github.com/go-gitea/gitea/blob/v1.27.3/modules/setting/server.go#L121-L122"
      }
    },
    "gitea-mfa-min": {
      "name": "Gitea MFA minimum",
      "basis": "1.24",
      "sources": {
        "s57933519c308": "https://docs.gitea.com/administration/config-cheat-sheet"
      }
    },
    "registry-docs": {
      "name": "Docker Registry documentation (rolling)",
      "basis": "unknown",
      "sources": {
        "sa315b3f8bfa6": "https://distribution.github.io/distribution/about/deploying/"
      }
    }
  },
  "claims": {
    "private": {"text": "Keep panels private; public front doors need proxy TLS/auth and MFA. Complete first-run administration before exposure.", "components": ["portainer", "docker"], "sources": ["portainer:s3e163c7d3c38", "docker:sfe15a8156c18"], "status": "REASONED"},
    "portainer-ports": {"text": "UI HTTPS 9443 is self-signed by default; supply a certificate/proxy. Leave legacy HTTP 9000 unpublished; publish tunnel 8000 only for Edge Compute.", "components": ["portainer"], "sources": ["portainer:s3e163c7d3c38"], "status": "REASONED"},
    "portainer-setup": {"text": "Setup requires the logged setup_token; first user is admin with a password of at least 12 characters.", "components": ["portainer"], "sources": ["portainer:s115489d2f86f"], "status": "REASONED"},
    "portainer-auth": {"text": "Internal, LDAP, AD or OAuth login; no documented native second factor. Enforce MFA at the OAuth provider.", "components": ["portainer"], "sources": ["portainer:s59297757a042", "portainer:s8901bbe7c3d3"], "status": "REASONED"},
    "portainer-socket": {"text": "Mounted docker.sock grants host-root power; treat a Portainer admin accordingly.", "components": ["portainer", "docker"], "sources": ["portainer:s3e163c7d3c38", "docker:sfe15a8156c18"], "status": "REASONED"},
    "coolify-setup": {"text": "HTTP dashboard starts on 8000; first registration claims server control, so create admin immediately.", "components": ["coolify"], "sources": ["coolify:s41e2d21202d9"], "status": "REASONED"},
    "coolify-tls": {"text": "Custom domain in /settings lets Traefik/Caddy issue/renew TLS; dashboard ports 8000/6001/6002 can then close.", "components": ["coolify"], "sources": ["coolify:sf2ae62425b35", "coolify:sf5d819d5d87d", "coolify:s90addf9d8d5d"], "status": "REASONED"},
    "coolify-firewall": {"text": "Docker bypasses UFW; restrict dashboard ports at the cloud firewall.", "components": ["coolify"], "sources": ["coolify:sf2ae62425b35"], "status": "REASONED"},
    "coolify-ssh": {"text": "Server SSH keys require no passphrase; stored key material is the whole secret.", "components": ["coolify"], "sources": ["coolify:s683244a61c48"], "status": "REASONED"},
    "dokploy-ports": {"text": "UI is 3000, Traefik 80/443; first setup creates admin.", "components": ["dokploy"], "sources": ["dokploy:sc2cc854c9b7e"], "status": "REASONED"},
    "dokploy-tls": {"text": "Configure a panel domain and Let's Encrypt/custom certificate, then remove published 3000.", "components": ["dokploy"], "sources": ["dokploy:sc2cc854c9b7e"], "status": "REASONED"},
    "npm-ports": {"text": "Admin is 81, proxy 80/443; publish 127.0.0.1:81:81 and tunnel in.", "components": ["npm"], "sources": ["npm:se553d384e783"], "status": "REASONED"},
    "npm-admin": {"text": "Change default first-run admin credentials before other work.", "components": ["npm"], "sources": ["npm:se553d384e783"], "status": "REASONED"},
    "vaultwarden-tls": {"text": "Web-vault crypto needs HTTPS; prefer proxy TLS over ROCKET_TLS and set DOMAIN=https://vault.example.com.", "components": ["vaultwarden", "vaultwarden-pin"], "sources": ["vaultwarden:s60d064cae50e", "vaultwarden-pin:s31c5fc79f5a0"], "status": "REASONED"},
    "vaultwarden-signup": {"text": "SIGNUPS_ALLOWED defaults true; set false to close registration.", "components": ["vaultwarden", "vaultwarden-pin"], "sources": ["vaultwarden:s6d3d0d02dcc9", "vaultwarden-pin:s31c5fc79f5a0"], "status": "REASONED"},
    "vaultwarden-invites": {"text": "INVITATIONS_ALLOWED=true still permits owner/admin invitations; SIGNUPS_DOMAINS_WHITELIST admits selected domains.", "components": ["vaultwarden", "vaultwarden-pin"], "sources": ["vaultwarden:s6d3d0d02dcc9", "vaultwarden-pin:s31c5fc79f5a0"], "status": "REASONED"},
    "vaultwarden-admin": {"text": "ADMIN_TOKEN enables the disabled admin page; enable HTTPS first, use vaultwarden hash argon2id PHC, and escape Compose dollars as $$.", "components": ["vaultwarden", "vaultwarden-pin"], "sources": ["vaultwarden:s0bbe8ad856cd", "vaultwarden-pin:s31c5fc79f5a0"], "status": "REASONED"},
    "vaultwarden-session": {"text": "Admin sessions expire after 20 minutes by default.", "components": ["vaultwarden", "vaultwarden-pin"], "sources": ["vaultwarden:s0bbe8ad856cd", "vaultwarden-pin:s31c5fc79f5a0"], "status": "REASONED"},
    "vaultwarden-port": {"text": "Container port 80 or non-Docker 8000; publish only to loopback/proxy network.", "components": ["vaultwarden-pin"], "sources": ["vaultwarden-pin:s31c5fc79f5a0"], "status": "REASONED"},
    "dashboard-lifecycle": {"text": "Recorded September 2026: deprecated/unmaintained, archived January 2026; Kubernetes points new installs to Headlamp.", "components": ["dashboard"], "sources": ["dashboard:s73a36a43f6b5"], "status": "REASONED"},
    "dashboard-forward": {"text": "Avoid public LoadBalancer/Ingress; port-forward kong-proxy 8443:443 and use https://localhost:8443 on the operator machine.", "components": ["dashboard"], "sources": ["dashboard:s73a36a43f6b5"], "status": "REASONED"},
    "dashboard-token": {"text": "Use minimally privileged ServiceAccount bearer tokens; sample cluster-admin is demonstration-only.", "components": ["dashboard"], "sources": ["dashboard:s73a36a43f6b5"], "status": "REASONED"},
    "dashboard-old-flags": {"text": "Older 2.x enable-skip-login and enable-insecure-login default false; keep both false.", "components": ["dashboard-old"], "sources": ["dashboard-old:sacea2944651e"], "status": "REASONED"},
    "dashboard-mfa": {"text": "API-server OIDC gives ServiceAccount tokens no MFA; enforce human MFA on the access path or an IdP-aware UI.", "components": ["dashboard"], "sources": ["dashboard:s73a36a43f6b5"], "status": "REASONED"},
    "jenkins-auth": {"text": "Realm/authorization are separate; setup creates one local admin. Disable signup because strategy grants apply to new users too.", "components": ["jenkins"], "sources": ["jenkins:s524c8d5871f1", "jenkins:sdfee751aeeee"], "status": "REASONED"},
    "jenkins-matrix": {"text": "Use Matrix Authorization; grant nothing significant to anonymous/authenticated. Anonymous Overall/Administer is full control.", "components": ["jenkins"], "sources": ["jenkins:sdfee751aeeee"], "status": "REASONED"},
    "jenkins-csrf": {"text": "Keep CSRF enabled even privately; disabling uses hudson.security.csrf.GlobalCrumbIssuerConfiguration.DISABLE_CSRF_PROTECTION, not a UI switch.", "components": ["jenkins"], "sources": ["jenkins:s6f5287fd36d4"], "status": "REASONED"},
    "jenkins-agents": {"text": "Inbound agents use fixed/random TCP or WebSocket on HTTPS; prefer WebSocket or isolate the extra port.", "components": ["jenkins"], "sources": ["jenkins:s524c8d5871f1"], "status": "REASONED"},
    "jenkins-mfa": {"text": "No native second factor; enforce MFA through SSO/fronting identity.", "components": ["jenkins"], "sources": ["jenkins:s524c8d5871f1", "jenkins:sdfee751aeeee"], "status": "REASONED"},
    "gitea-bind": {"text": "HTTP_ADDR=0.0.0.0 and HTTP_PORT=3000 default; set 127.0.0.1 behind a proxy.", "components": ["gitea-pin"], "sources": ["gitea-pin:s31dd622b1c12"], "status": "REASONED"},
    "gitea-tls": {"text": "Native TLS uses PROTOCOL=https, CERT_FILE and KEY_FILE.", "components": ["gitea"], "sources": ["gitea:s57933519c308"], "status": "REASONED"},
    "gitea-registration": {"text": "Set service DISABLE_REGISTRATION=true; default false.", "components": ["gitea"], "sources": ["gitea:s57933519c308"], "status": "REASONED"},
    "gitea-private": {"text": "Set service REQUIRE_SIGNIN_VIEW=true for a private forge; default false.", "components": ["gitea"], "sources": ["gitea:s57933519c308"], "status": "REASONED"},
    "gitea-mfa": {"text": "Enrol TOTP/WebAuthn; security TWO_FACTOR_AUTH=enforced requires MFA in Gitea 1.24 and later.", "components": ["gitea", "gitea-mfa-min"], "sources": ["gitea:s57933519c308", "gitea:s3b7060d58383", "gitea-mfa-min:s57933519c308"], "status": "REASONED"},
    "gitea-tokens": {"text": "With MFA, Git HTTP uses tokens that bypass MFA; scope and revoke unused tokens.", "components": ["gitea"], "sources": ["gitea:s3b7060d58383"], "status": "REASONED"},
    "gitlab-root": {"text": "Rotate generated initial_root_password; file deletion is on first restart after 24 hours. Alternatively preset through gitlab.rb/OMNIBUS_CONFIG.", "components": ["gitlab"], "sources": ["gitlab:s3b7ac561a92e"], "status": "REASONED"},
    "gitlab-signup": {"text": "signup_enabled defaults true; disable for a private forge.", "components": ["gitlab"], "sources": ["gitlab:s6e8d16cad2ef"], "status": "REASONED"},
    "gitlab-approval": {"text": "New instances require admin approval after signup by default; do not rely on approval alone.", "components": ["gitlab"], "sources": ["gitlab:s6e8d16cad2ef"], "status": "REASONED"},
    "gitlab-visibility": {"text": "Project/group visibility default private; internal admits every signed-in non-external user, including allowed registrants.", "components": ["gitlab"], "sources": ["gitlab:s6b8a68a77e17"], "status": "REASONED"},
    "gitlab-mfa": {"text": "Enforce two-factor authentication for every user; available on all tiers.", "components": ["gitlab"], "sources": ["gitlab:s0347014ce554"], "status": "REASONED"},
    "kuma-proxy": {"text": "Port 3001 uses WebSockets; proxy Upgrade/Connection headers are required.", "components": ["kuma"], "sources": ["kuma:s05b853ba300b", "kuma:sed52bfca4039"], "status": "REASONED"},
    "kuma-admin": {"text": "Finish account setup before others, enable 2FA and keep dashboard private even if status pages are public.", "components": ["kuma"], "sources": ["kuma:s05b853ba300b"], "status": "REASONED"},
    "docker-root": {"text": "Docker socket grants host-root power; never expose unauthenticated 0.0.0.0:2375.", "components": ["docker"], "sources": ["docker:sfe15a8156c18", "docker:s1b5ec54421b0"], "status": "REASONED"},
    "docker-ssh": {"text": "DOCKER_HOST/context can select SSH to the Unix socket without a new listener.", "components": ["docker"], "sources": ["docker:sfe15a8156c18"], "status": "REASONED"},
    "docker-mtls": {"text": "2376 requires tlsverify, CA, server cert/key and client TLS settings. Without tlsverify clients are not authenticated; firewall source addresses too.", "components": ["docker"], "sources": ["docker:sfe15a8156c18"], "status": "REASONED"},
    "dozzle-socket": {"text": "Docker-socket access has host-level power; keep Dozzle private with fronting MFA.", "components": ["dozzle", "docker"], "sources": ["dozzle:s45b3eab2515b", "docker:sfe15a8156c18"], "status": "REASONED"},
    "dozzle-auth": {"text": "Auth defaults off; generate users.yml with stdin password prompt and set simple auth, or delegate with forward-proxy.", "components": ["dozzle"], "sources": ["dozzle:s45b3eab2515b"], "status": "REASONED"},
    "dozzle-actions": {"text": "Leave optional container actions/shell off unless needed; either enables remote command execution.", "components": ["dozzle"], "sources": ["dozzle:s45b3eab2515b"], "status": "REASONED"},
    "registry-auth": {"text": "registry:2 defaults to unauthenticated push/pull; configure TLS before htpasswd/token auth or use an authenticated distribution.", "components": ["registry-docs"], "sources": ["registry-docs:sa315b3f8bfa6"], "status": "REASONED"},
    "registry-bcrypt": {"text": "Native htpasswd accepts bcrypt only; use -B -C 12. Proxy hashing rules differ; OWASP cost minimum lacks a direct source here.", "components": ["registry-docs"], "sources": ["registry-docs:sa315b3f8bfa6"], "status": "REASONED"},
    "registry-private": {"text": "Use private networking and tunnels/Access with fronting MFA.", "components": ["registry-docs"], "sources": ["registry-docs:sa315b3f8bfa6"], "status": "REASONED"},
    "filebrowser-admin": {"text": "Change first-run admin credentials, historically admin/admin. Guide records September 1, 2026 archival and the warning against internet exposure.", "components": ["filebrowser"], "sources": ["filebrowser:s6386c9e2356b"], "status": "REASONED"},
    "filebrowser-private": {"text": "Keep Filebrowser private through tunnel/tailnet/Access with fronting MFA.", "components": ["filebrowser"], "sources": ["filebrowser:s6386c9e2356b"], "status": "REASONED"},
    "nodered-default": {"text": "Editor/admin API on 1880 defaults unauthenticated, permitting flow viewing/deployment/modification.", "components": ["nodered"], "sources": ["nodered:sa94f329023fe"], "status": "REASONED"},
    "nodered-auth": {"text": "Set adminAuth with bcrypt passwords from node-red admin hash-pw.", "components": ["nodered"], "sources": ["nodered:sa94f329023fe"], "status": "REASONED"},
    "nodered-secret": {"text": "Set credentialSecret yourself; otherwise generated, and stored credentials depend on it.", "components": ["nodered"], "sources": ["nodered:sa94f329023fe"], "status": "REASONED"},
    "nodered-private": {"text": "Keep editor private with fronting MFA; it has the power of its flows.", "components": ["nodered"], "sources": ["nodered:sa94f329023fe"], "status": "REASONED"},
    "verify-listeners": {"text": "Read every panel/API listener; expect loopback or absence, never wildcard exposure.", "components": ["portainer", "dokploy", "npm", "kuma", "docker"], "sources": ["portainer:s3e163c7d3c38", "dokploy:sc2cc854c9b7e", "npm:se553d384e783", "kuma:s05b853ba300b", "docker:s1b5ec54421b0"], "status": "REASONED", "verify": [1]},
    "verify-panel": {"text": "Expect denial/login redirect with valid TLS; anonymous host/container/repository data is a finding. No live panel outcome recorded.", "components": ["portainer", "jenkins", "gitea"], "sources": ["portainer:s3e163c7d3c38", "jenkins:sdfee751aeeee", "gitea:s57933519c308"], "status": "REASONED", "verify": [1]},
    "verify-docker-plain": {"text": "Public-IP 2375 must be refused/filtered by the remote host; local client failure is inconclusive.", "components": ["docker"], "sources": ["docker:s1b5ec54421b0"], "status": "REASONED", "verify": [1]},
    "verify-docker-mtls": {"text": "2376 /_ping without a client certificate must fail client-certificate authentication; correct certificate/key must return 200.", "components": ["docker"], "sources": ["docker:sfe15a8156c18"], "status": "REASONED", "verify": [1]},
    "verify-gitlab": {"text": "Present initial_root_password requires rotation; absence does not prove rotation. Failed/unexpected docker exec output is not a result.", "components": ["gitlab"], "sources": ["gitlab:s3b7ac561a92e"], "status": "REASONED", "verify": [1]}
  }
}
---
# DevOps panels: Portainer, Coolify, Dokploy, Nginx Proxy Manager, Vaultwarden, Kubernetes Dashboard, Jenkins, Gitea, Uptime Kuma, and the Docker API

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| private: Keep panels private; public front doors need proxy TLS/auth and MFA. Complete first-run administration before exposure. | Portainer unknown; Docker Engine unknown | REASONED |
| portainer-ports: UI HTTPS 9443 is self-signed by default; supply a certificate/proxy. Leave legacy HTTP 9000 unpublished; publish tunnel 8000 only for Edge Compute. | Portainer unknown | REASONED |
| portainer-setup: Setup requires the logged setup_token; first user is admin with a password of at least 12 characters. | Portainer unknown | REASONED |
| portainer-auth: Internal, LDAP, AD or OAuth login; no documented native second factor. Enforce MFA at the OAuth provider. | Portainer unknown | REASONED |
| portainer-socket: Mounted docker.sock grants host-root power; treat a Portainer admin accordingly. | Portainer unknown; Docker Engine unknown | REASONED |
| coolify-setup: HTTP dashboard starts on 8000; first registration claims server control, so create admin immediately. | Coolify unknown | REASONED |
| coolify-tls: Custom domain in /settings lets Traefik/Caddy issue/renew TLS; dashboard ports 8000/6001/6002 can then close. | Coolify unknown | REASONED |
| coolify-firewall: Docker bypasses UFW; restrict dashboard ports at the cloud firewall. | Coolify unknown | REASONED |
| coolify-ssh: Server SSH keys require no passphrase; stored key material is the whole secret. | Coolify unknown | REASONED |
| dokploy-ports: UI is 3000, Traefik 80/443; first setup creates admin. | Dokploy unknown | REASONED |
| dokploy-tls: Configure a panel domain and Let's Encrypt/custom certificate, then remove published 3000. | Dokploy unknown | REASONED |
| npm-ports: Admin is 81, proxy 80/443; publish 127.0.0.1:81:81 and tunnel in. | Nginx Proxy Manager unknown | REASONED |
| npm-admin: Change default first-run admin credentials before other work. | Nginx Proxy Manager unknown | REASONED |
| vaultwarden-tls: Web-vault crypto needs HTTPS; prefer proxy TLS over ROCKET_TLS and set DOMAIN=https://vault.example.com. | Vaultwarden docs unknown; Vaultwarden config 3347698712d3e99e652ad4394ef2fc0ce2800fdd | REASONED |
| vaultwarden-signup: SIGNUPS_ALLOWED defaults true; set false to close registration. | Vaultwarden docs unknown; Vaultwarden config 3347698712d3e99e652ad4394ef2fc0ce2800fdd | REASONED |
| vaultwarden-invites: INVITATIONS_ALLOWED=true still permits owner/admin invitations; SIGNUPS_DOMAINS_WHITELIST admits selected domains. | Vaultwarden docs unknown; Vaultwarden config 3347698712d3e99e652ad4394ef2fc0ce2800fdd | REASONED |
| vaultwarden-admin: ADMIN_TOKEN enables the disabled admin page; enable HTTPS first, use vaultwarden hash argon2id PHC, and escape Compose dollars as $$. | Vaultwarden docs unknown; Vaultwarden config 3347698712d3e99e652ad4394ef2fc0ce2800fdd | REASONED |
| vaultwarden-session: Admin sessions expire after 20 minutes by default. | Vaultwarden docs unknown; Vaultwarden config 3347698712d3e99e652ad4394ef2fc0ce2800fdd | REASONED |
| vaultwarden-port: Container port 80 or non-Docker 8000; publish only to loopback/proxy network. | Vaultwarden config 3347698712d3e99e652ad4394ef2fc0ce2800fdd | REASONED |
| dashboard-lifecycle: Recorded September 2026: deprecated/unmaintained, archived January 2026; Kubernetes points new installs to Headlamp. | Dashboard docs unknown | REASONED |
| dashboard-forward: Avoid public LoadBalancer/Ingress; port-forward kong-proxy 8443:443 and use https://localhost:8443 on the operator machine. | Dashboard docs unknown | REASONED |
| dashboard-token: Use minimally privileged ServiceAccount bearer tokens; sample cluster-admin is demonstration-only. | Dashboard docs unknown | REASONED |
| dashboard-old-flags: Older 2.x enable-skip-login and enable-insecure-login default false; keep both false. | Dashboard arguments v2.7.0 | REASONED |
| dashboard-mfa: API-server OIDC gives ServiceAccount tokens no MFA; enforce human MFA on the access path or an IdP-aware UI. | Dashboard docs unknown | REASONED |
| jenkins-auth: Realm/authorization are separate; setup creates one local admin. Disable signup because strategy grants apply to new users too. | Jenkins unknown | REASONED |
| jenkins-matrix: Use Matrix Authorization; grant nothing significant to anonymous/authenticated. Anonymous Overall/Administer is full control. | Jenkins unknown | REASONED |
| jenkins-csrf: Keep CSRF enabled even privately; disabling uses hudson.security.csrf.GlobalCrumbIssuerConfiguration.DISABLE_CSRF_PROTECTION, not a UI switch. | Jenkins unknown | REASONED |
| jenkins-agents: Inbound agents use fixed/random TCP or WebSocket on HTTPS; prefer WebSocket or isolate the extra port. | Jenkins unknown | REASONED |
| jenkins-mfa: No native second factor; enforce MFA through SSO/fronting identity. | Jenkins unknown | REASONED |
| gitea-bind: HTTP_ADDR=0.0.0.0 and HTTP_PORT=3000 default; set 127.0.0.1 behind a proxy. | Gitea listener v1.27.3 | REASONED |
| gitea-tls: Native TLS uses PROTOCOL=https, CERT_FILE and KEY_FILE. | Gitea docs unknown | REASONED |
| gitea-registration: Set service DISABLE_REGISTRATION=true; default false. | Gitea docs unknown | REASONED |
| gitea-private: Set service REQUIRE_SIGNIN_VIEW=true for a private forge; default false. | Gitea docs unknown | REASONED |
| gitea-mfa: Enrol TOTP/WebAuthn; security TWO_FACTOR_AUTH=enforced requires MFA in Gitea 1.24 and later. | Gitea docs unknown; Gitea MFA minimum 1.24 | REASONED |
| gitea-tokens: With MFA, Git HTTP uses tokens that bypass MFA; scope and revoke unused tokens. | Gitea docs unknown | REASONED |
| gitlab-root: Rotate generated initial_root_password; file deletion is on first restart after 24 hours. Alternatively preset through gitlab.rb/OMNIBUS_CONFIG. | GitLab CE unknown | REASONED |
| gitlab-signup: signup_enabled defaults true; disable for a private forge. | GitLab CE unknown | REASONED |
| gitlab-approval: New instances require admin approval after signup by default; do not rely on approval alone. | GitLab CE unknown | REASONED |
| gitlab-visibility: Project/group visibility default private; internal admits every signed-in non-external user, including allowed registrants. | GitLab CE unknown | REASONED |
| gitlab-mfa: Enforce two-factor authentication for every user; available on all tiers. | GitLab CE unknown | REASONED |
| kuma-proxy: Port 3001 uses WebSockets; proxy Upgrade/Connection headers are required. | Uptime Kuma unknown | REASONED |
| kuma-admin: Finish account setup before others, enable 2FA and keep dashboard private even if status pages are public. | Uptime Kuma unknown | REASONED |
| docker-root: Docker socket grants host-root power; never expose unauthenticated 0.0.0.0:2375. | Docker Engine unknown | REASONED |
| docker-ssh: DOCKER_HOST/context can select SSH to the Unix socket without a new listener. | Docker Engine unknown | REASONED |
| docker-mtls: 2376 requires tlsverify, CA, server cert/key and client TLS settings. Without tlsverify clients are not authenticated; firewall source addresses too. | Docker Engine unknown | REASONED |
| dozzle-socket: Docker-socket access has host-level power; keep Dozzle private with fronting MFA. | Dozzle unknown; Docker Engine unknown | REASONED |
| dozzle-auth: Auth defaults off; generate users.yml with stdin password prompt and set simple auth, or delegate with forward-proxy. | Dozzle unknown | REASONED |
| dozzle-actions: Leave optional container actions/shell off unless needed; either enables remote command execution. | Dozzle unknown | REASONED |
| registry-auth: registry:2 defaults to unauthenticated push/pull; configure TLS before htpasswd/token auth or use an authenticated distribution. | Docker Registry documentation (rolling) unknown | REASONED |
| registry-bcrypt: Native htpasswd accepts bcrypt only; use -B -C 12. Proxy hashing rules differ; OWASP cost minimum lacks a direct source here. | Docker Registry documentation (rolling) unknown | REASONED |
| registry-private: Use private networking and tunnels/Access with fronting MFA. | Docker Registry documentation (rolling) unknown | REASONED |
| filebrowser-admin: Change first-run admin credentials, historically admin/admin. Guide records September 1, 2026 archival and the warning against internet exposure. | Filebrowser unknown | REASONED |
| filebrowser-private: Keep Filebrowser private through tunnel/tailnet/Access with fronting MFA. | Filebrowser unknown | REASONED |
| nodered-default: Editor/admin API on 1880 defaults unauthenticated, permitting flow viewing/deployment/modification. | Node-RED unknown | REASONED |
| nodered-auth: Set adminAuth with bcrypt passwords from node-red admin hash-pw. | Node-RED unknown | REASONED |
| nodered-secret: Set credentialSecret yourself; otherwise generated, and stored credentials depend on it. | Node-RED unknown | REASONED |
| nodered-private: Keep editor private with fronting MFA; it has the power of its flows. | Node-RED unknown | REASONED |
| verify-listeners: Read every panel/API listener; expect loopback or absence, never wildcard exposure. | Portainer unknown; Dokploy unknown; Nginx Proxy Manager unknown; Uptime Kuma unknown; Docker Engine unknown | REASONED |
| verify-panel: Expect denial/login redirect with valid TLS; anonymous host/container/repository data is a finding. No live panel outcome recorded. | Portainer unknown; Jenkins unknown; Gitea docs unknown | REASONED |
| verify-docker-plain: Public-IP 2375 must be refused/filtered by the remote host; local client failure is inconclusive. | Docker Engine unknown | REASONED |
| verify-docker-mtls: 2376 /_ping without a client certificate must fail client-certificate authentication; correct certificate/key must return 200. | Docker Engine unknown | REASONED |
| verify-gitlab: Present initial_root_password requires rotation; absence does not prove rotation. Failed/unexpected docker exec output is not a result. | GitLab CE unknown | REASONED |
<!-- version-basis:end -->

These panels control hosts, containers, clusters, deploy keys, and secrets; a login to one of them is a login to everything it manages. One rule dominates everything tool-specific below: **a DevOps panel is never reachable from the public internet.** Bind it to loopback or a private interface and reach it through SSH port forwarding, a tailnet ([tailscale.md](tailscale.md)), or Cloudflare Access ([cloudflare.md](cloudflare.md)); anything that must be public sits behind a TLS proxy with its own authentication ([nginx.md](nginx.md), [caddy.md](caddy.md)) and the admin login gets MFA ([mfa.md](mfa.md)). Several of these tools create their administrator on first visit, so whoever reaches a fresh install first owns it: create the account before the port is reachable by anyone else.

## Portainer

- Serves the UI over HTTPS on `9443` (self-signed by default; supply your own certificate or front it per [nginx.md](nginx.md)). `9000` is the legacy HTTP port and stays unpublished; `8000` is the Edge agent tunnel and is only published when Edge Compute is in use.
- New instances require a setup token to complete first-time setup; it is in the server logs on the `setup_token=` line. The first user is an administrator, and its password must be at least 12 characters.
- Authentication is internal, LDAP, Active Directory, or OAuth (Microsoft, Google, GitHub, or a custom provider). Portainer's own login has no second factor in its documentation; use OAuth against a provider that enforces MFA ([identity-providers.md](identity-providers.md)).
- The container mounts `/var/run/docker.sock`, which is root on the host; a Portainer admin is a host root user ([docker.md](docker.md)).

## Coolify and Dokploy

Both are one-script installs that hold your servers' SSH private keys, Git provider credentials, and application secrets, and both create their administrator on first visit.

- Coolify's dashboard answers on `8000` over plain HTTP after install. Its documentation says to create the admin account immediately, because whoever reaches the registration page first can gain full control of the server. Set the instance a custom domain on the `/settings` page; the integrated proxy (Traefik by default, or Caddy) then issues and renews a Let's Encrypt certificate, and the firewall guide says ports `8000`, `6001`, and `6002` can be closed once the dashboard is reached through that domain. Docker's iptables rules bypass UFW, so restrict these ports with the cloud provider's firewall ([cloud-firewalls.md](cloud-firewalls.md)). Coolify requires the server SSH key to have no passphrase, so the key material inside Coolify is the whole secret.
- Dokploy's UI answers on `3000`; ports `80` and `443` belong to its Traefik. The first visit is the setup page that creates the admin account. Configure a domain with a Let's Encrypt or custom certificate for the panel under Domains, then remove the published `3000` binding so the panel is reachable only through the proxy.

## Nginx Proxy Manager

The admin UI is on port `81`; the proxy itself is on `80`/`443`. Port `81` is never published to the internet: bind it to `127.0.0.1` in the compose file (`'127.0.0.1:81:81'`) and reach it through a tunnel. A default admin user is created on the first run; change the initial admin credentials on first login, before anything else. Since it terminates TLS for every site behind it, treat its login like a root password.

## Vaultwarden

- The web vault needs HTTPS (browsers expose the crypto APIs it uses only in secure contexts). The wiki recommends a reverse proxy for TLS ([caddy.md](caddy.md), [nginx.md](nginx.md)) and rates the built-in `ROCKET_TLS` as not recommended. Set `DOMAIN=https://vault.example.com`.
- `SIGNUPS_ALLOWED=false` (the default is `true`, letting anyone who reaches the instance register). Organization owners and admins can still invite users while `INVITATIONS_ALLOWED=true`; `SIGNUPS_DOMAINS_WHITELIST` admits specific email domains.
- The admin page is disabled unless `ADMIN_TOKEN` is set. Store it as an argon2id PHC string generated with `vaultwarden hash` (or `docker run --rm -it vaultwarden/server /vaultwarden hash`), never plaintext; in a compose `environment:` block every `$` in the hash becomes `$$`. Enable HTTPS before enabling the admin page. Admin sessions expire after 20 minutes by default.
- Inside a container it listens on `80` (`8000` outside Docker); publish it only to loopback or the proxy network.

## Kubernetes Dashboard

- As of September 2026 the Kubernetes documentation marks the Dashboard deprecated and unmaintained (the repository was archived in January 2026) and points new installs to Headlamp; the pattern below applies to any cluster UI.
- Do not expose it with a LoadBalancer or Ingress. Reach it from the operator's machine with `kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard-kong-proxy 8443:443` and open `https://localhost:8443`; the UI is then reachable only from that machine.
- Login is by bearer token of a ServiceAccount with a minimal RBAC role; the tutorial's sample user is cluster-admin and is for demonstration only. On the older 2.x releases, `--enable-skip-login` and `--enable-insecure-login` both default to `false`; never turn them on.
- A ServiceAccount token is a machine credential, so configuring OIDC on the API server puts no MFA on this login. Human MFA comes from the access path (a port-forward over SSH from a machine that already required it, a tailnet per [tailscale.md](tailscale.md), or Cloudflare Access per [cloudflare.md](cloudflare.md)) or from a UI that performs an identity-provider login itself; see [mfa.md](mfa.md).

## Jenkins

- Authentication (the security realm: Jenkins' own user database, LDAP, and others) and authorization (the strategy) are configured separately. The setup wizard leaves a single admin in the local database; do not enable account signup for that database, since new accounts inherit whatever the strategy grants to authenticated users.
- Use the Matrix Authorization Strategy (global or project-based) and grant nothing significant to `anonymous` or to `authenticated`; granting Overall/Administer to anonymous is the same as "Anyone can do anything".
- Leave CSRF protection on. It has no UI switch and is only disabled by the `hudson.security.csrf.GlobalCrumbIssuerConfiguration.DISABLE_CSRF_PROTECTION` system property; the documentation says to keep it enabled even on private networks.
- Inbound agents use a fixed or random TCP port, or WebSocket over the same HTTPS port with no extra listener; prefer WebSocket or keep the agent port on the private network.
- Jenkins has no native second factor; put the web UI behind SSO with MFA at the provider or behind an identity layer ([mfa.md](mfa.md)).

## Gitea

- It listens on `HTTP_ADDR = 0.0.0.0` and `HTTP_PORT = 3000` by default (both as of v1.27.3); set `HTTP_ADDR = 127.0.0.1` behind a proxy, or `PROTOCOL = https` with `CERT_FILE` and `KEY_FILE` to terminate TLS itself.
- In `[service]`, `DISABLE_REGISTRATION = true` (default `false`) and, for a private forge, `REQUIRE_SIGNIN_VIEW = true` (default `false`).
- Users enrol TOTP or a WebAuthn key under Settings > Security; `TWO_FACTOR_AUTH = enforced` in `[security]` (Gitea 1.24 and later) requires it. With MFA on, Git over HTTP uses an access token instead of the password, and tokens bypass MFA, so scope them and revoke unused ones ([machine-auth.md](machine-auth.md)).

## GitLab CE

- First run auto-generates the root password into `/etc/gitlab/initial_root_password` (read it with `docker exec -it gitlab grep 'Password:' /etc/gitlab/initial_root_password`); GitLab deletes the file in the first container restart after 24 hours. Change it immediately on first sign-in, since until you do the generated password is the only thing guarding the root account; or preset it with `gitlab_rails['initial_root_password']` in `gitlab.rb` or `GITLAB_OMNIBUS_CONFIG`.
- `signup_enabled` defaults to `true`, so any visitor can register. New instances hold registrants pending approval (`require_admin_approval_after_user_signup` is on by default), but for a private forge clear "Allow new user accounts" under Admin > Settings > General > New user account restrictions (`signup_enabled = false`) rather than relying on approval discipline.
- `default_project_visibility` and `default_group_visibility` both default to `private`; keep them there. "Internal" means visible to every signed-in non-external user, so on an instance that allows sign-up, internal is not private.
- GitLab can enforce two-factor authentication for every user (all tiers) from Admin > Settings > General > Sign-in restrictions; turn it on so local accounts are not password-only.

## Uptime Kuma

Listens on `3001` and is WebSocket-based, so a reverse proxy in front needs the `Upgrade` and `Connection` headers. Open it right after the first start and finish the account setup before anyone else can; then enable the 2FA the project lists as a feature for that account. Status pages can be public; the dashboard is not.

## The Docker API

The daemon socket is root on the host: anyone who can talk to it can run a privileged container. Never start `dockerd` with `-H tcp://0.0.0.0:2375`; Docker's documentation calls remote access without TLS not recommended, and scanners find open 2375 within minutes. Two acceptable remote paths:

```bash
# 1. SSH to the Unix socket (nothing new listens on the network)
export DOCKER_HOST=ssh://docker-user@host1.example.com
docker context create remote --docker host=ssh://docker-user@host1.example.com

# 2. TLS with client certificates on 2376, all four flags set
dockerd --tlsverify --tlscacert=ca.pem --tlscert=server-cert.pem --tlskey=server-key.pem -H=0.0.0.0:2376
export DOCKER_HOST=tcp://$HOST:2376 DOCKER_TLS_VERIFY=1 DOCKER_CERT_PATH=~/.docker/zone1/
```

Without `--tlsverify` the daemon does not check client certificates. Firewall 2376 to the operator addresses even with TLS ([docker.md](docker.md)).

## Dozzle

- Dozzle reads the Docker socket to show logs, the same host-level access the Docker API section above describes ([docker.md](docker.md)); a Dozzle login is a login to the host.
- Authentication is off unless configured. Generate a `users.yml` with `docker run -it --rm amir20/dozzle generate admin > users.yml` (omit `--password` and Dozzle prompts for it on stdin, so it never lands in shell history), mount that file into the container, and set `DOZZLE_AUTH_PROVIDER=simple`; or set `DOZZLE_AUTH_PROVIDER=forward-proxy` to delegate login to a fronting proxy such as Authelia, Authentik, or Cloudflare Access.
- Container actions (start, stop, recreate) and shell access into a running container can be turned on; leave both off unless a specific workflow needs them, since either turns a log viewer into remote command execution on the host.
- Bind it to loopback or a private interface and reach it through SSH port forwarding, a tailnet, or Access, with MFA at the fronting layer, like every panel above.

## Docker Registry (`registry:2`)

- The reference registry image ships with no authentication at all: anyone who reaches the port can push and pull every image, and TLS must be configured before any authentication scheme works, since credentials would otherwise cross the wire in clear text.
- Restrict access with htpasswd basic authentication, a token server, or a registry distribution that has its own authentication built in. If using the registry's own native htpasswd auth provider (set directly in the registry's `config.yml`), credentials must be bcrypt-hashed at a strong cost (`htpasswd -B -C 12`; bare -B is cost 5, below the OWASP minimum of 10); the registry rejects any non-bcrypt hash format. If instead a reverse proxy sits in front and does its own basic authentication from its own htpasswd file, that proxy's own hashing rules apply, not the registry's.
- Bind it to loopback or a private interface and reach it through SSH port forwarding, a tailnet, or Access, with MFA at the fronting layer.

## Filebrowser

- Ships with a default administrator account created on first run (historically `admin`/`admin`). Change it immediately, before the instance is reachable by anyone else. The project's own repository (archived on September 1, 2026) says not to expose it directly to the internet.
- Bind it to loopback or a private interface and reach it through SSH port forwarding, a tailnet, or Access, with MFA at the fronting layer; never publish a file-serving admin panel.

## Node-RED

- The editor and admin API on `1880` have no authentication at all by default; anyone who reaches the port can view, deploy, and modify flows.
- Set `adminAuth` in `settings.js` with bcrypt-hashed user passwords (`node-red admin hash-pw` generates the hash), and set `credentialSecret` to a value you control, since Node-RED otherwise generates one for you and stored credentials are only as protected as that secret.
- Bind it to loopback or a private interface and reach it through SSH port forwarding, a tailnet, or Access, with MFA at the fronting layer; the editor is equivalent to a shell on whatever the flows can reach.

## Verify

REASONED: following block; panel, Docker daemon and GitLab sources below support these listener/login, 2375/2376 and password-file checks. No deployed panels, certificate fixture or external test network is available here. Comments give expected outcomes and limits; no live run is recorded.

```bash
ss -tlnp   # read every listener; 9443/9000/8000/3000/81/3001/2375/2376: 127.0.0.1 or absent, never 0.0.0.0
# guard-conventions: allow probe of an illustrative example host; no reader-substituted placeholder in this probe's argv
curl -q -s -o /dev/null -w '%{http_code}\n' https://panel.example.com/
                                                                  # 401, 403, or a login redirect, never a dashboard. No -k:
                                                                  # this panel is behind a proxy holding a real certificate, so
                                                                  # a check that skips verification proves nothing about it
# clears a pre-set declare -i or -l attribute, and any stale
# value; copy this whole block, not just the command below
(                                                   # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_YOUR_PUBLIC_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|*YOUR_PUBLIC_IP*|"") echo "substitute your own address on the set -- line above; not probing" ;;
    *) docker -H "tcp://$1:2375" info ;;       # must fail: connection refused or filtered
    # that is, refused or filtered BY THE REMOTE HOST. A local error or a docker client failure that
    # never opened a connection is inconclusive, not a pass
  esac
)
env -u DOCKER_HOST -u DOCKER_TLS_VERIFY -u DOCKER_CERT_PATH \
  curl -q -sS -o /dev/null -w '%{http_code}\n' --cacert ca.pem https://203.0.113.10:2376/_ping
                                                                  # must fail the handshake on the CLIENT certificate. Do not use
                                                                  # `docker ... info` here: without `--tlsverify` it fails for the
                                                                  # wrong reason, and `DOCKER_CERT_PATH` exported in the setup above
                                                                  # can silently supply the very certificate the check is meant to lack
# guard-conventions: allow probe of a fixed illustrative target; no reader-substituted placeholder in this probe's argv
curl -q -sS -o /dev/null -w '%{http_code}\n' --cacert ca.pem --cert client-cert.pem --key client-key.pem \
  https://203.0.113.10:2376/_ping                                 # positive control: 200 with the right client certificate

# GitLab CE: initial root password file check (needs Docker access; the container is named gitlab)
# absence does not prove the password was rotated; presence means rotate root now
if state=$(docker exec gitlab sh -c 'test -f /etc/gitlab/initial_root_password && echo PRESENT || echo ABSENT' 2>/dev/null); then
  case "$state" in
    PRESENT) echo 'initial_root_password present: rotate root and remove it' ;;
    ABSENT)  echo 'initial_root_password absent' ;;
    *)       echo 'the check did not run (unexpected reply from the gitlab container): not a result' ;;
  esac
else
  echo 'the check did not run (docker exec failed for the gitlab container): fix the container, this is not a result'
fi
```

From outside the network, every panel URL is unreachable or shows a login; a page that renders host, container, or repository data without one is a finding.

## Sources (checked September 2026)

- Portainer CE install on Docker (ports 9443, 9000, 8000): https://docs.portainer.io/start/install-ce/server/docker/linux
- Portainer initial setup (setup token, first admin, 12-character password): https://docs.portainer.io/start/install-ce/server/setup
- Portainer authentication and OAuth providers: https://docs.portainer.io/admin/settings/authentication and https://docs.portainer.io/admin/settings/authentication/oauth
- Coolify installation, firewall, proxy, and DNS pages: https://coolify.io/docs/start-with-self-hosted , https://coolify.io/docs/core/infrastructure/servers/firewall , https://coolify.io/docs/core/networking/proxy/overview , https://coolify.io/docs/core/networking/dns , https://coolify.io/docs/core/infrastructure/servers/openssh
- Dokploy installation (ports 80, 443, 3000; admin setup; panel domain): https://docs.dokploy.com/docs/core/installation
- Nginx Proxy Manager setup (port 81, default admin user): https://nginxproxymanager.com/setup/
- Vaultwarden wiki: admin page and ADMIN_TOKEN https://github.com/dani-garcia/vaultwarden/wiki/Enabling-admin-page , registration https://github.com/dani-garcia/vaultwarden/wiki/Disable-registration-of-new-users , HTTPS https://github.com/dani-garcia/vaultwarden/wiki/Enabling-HTTPS , and the `.env.template` https://github.com/dani-garcia/vaultwarden/blob/3347698712d3e99e652ad4394ef2fc0ce2800fdd/.env.template
- Kubernetes Dashboard (deprecation, port-forward, token login): https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/ ; 2.x arguments: https://github.com/kubernetes-retired/dashboard/blob/v2.7.0/docs/common/dashboard-arguments.md
- Jenkins security: https://www.jenkins.io/doc/book/security/managing-security/ , https://www.jenkins.io/doc/book/security/access-control/ , https://www.jenkins.io/doc/book/security/csrf-protection/
- Gitea config cheat sheet and MFA (Gitea 1.24 and later): https://docs.gitea.com/administration/config-cheat-sheet and https://docs.gitea.com/usage/user-setting/multi-factor-authentication/
- GitLab CE initial root password (Docker install): https://docs.gitlab.com/install/docker/installation/
- GitLab CE sign-up restrictions: https://docs.gitlab.com/administration/settings/sign_up_restrictions/
- GitLab CE default visibility and access controls: https://docs.gitlab.com/administration/settings/visibility_and_access_controls/
- GitLab CE enforce two-factor authentication for all users: https://docs.gitlab.com/security/two_factor_authentication/
- Uptime Kuma README and reverse proxy wiki: https://github.com/louislam/uptime-kuma and https://github.com/louislam/uptime-kuma/wiki/Reverse-Proxy
- Docker: protect the daemon socket https://docs.docker.com/engine/security/protect-access/ and remote access https://docs.docker.com/engine/daemon/remote-access/
- Dozzle authentication (DOZZLE_AUTH_PROVIDER, users.yml, actions and shell): https://dozzle.dev/guide/authentication
- Docker Registry deployment (default authentication, TLS requirement; rolling documentation, checked September 2026): https://distribution.github.io/distribution/about/deploying/
- Filebrowser: https://github.com/filebrowser/filebrowser
- Node-RED securing the runtime (adminAuth, credentialSecret): https://nodered.org/docs/user-guide/runtime/securing-node-red
- Gitea `HTTP_ADDR` default `0.0.0.0` and `HTTP_PORT` default `3000` (pinned tag v1.27.3): https://github.com/go-gitea/gitea/blob/v1.27.3/modules/setting/server.go#L121-L122
