---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "89dde97e67eda034ee23de23b210ec41af96694e16c262a44669c16d87752a8e",
  "components": {
    "argo": {
      "name": "Argo CD v3.5.3 source",
      "basis": "c9c369efcc5b2a0bd720803f8d14a1c3eaddf579",
      "sources": {
        "sddf4853ad503": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/server/argocd-server-service.yaml#L9-L20",
        "s6e8c96d23e05": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd-server/commands/argocd_server.go#L307-L323",
        "s96065cc09776": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L512-L535",
        "s7cc690d1bf69": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L668-L677",
        "s028a4769d6c3": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/metrics/metrics.go#L74-L100",
        "sc52bbd14bff4": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/profile/profile.go#L11-L30",
        "s98b27313f615": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd-repo-server/commands/argocd_repo_server.go#L180-L212",
        "sb0648e746fb9": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/server/argocd-server-deployment.yaml#L406-L408",
        "s2f5af86c62d1": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/server/argocd-server-deployment.yaml#L475-L481",
        "s9bca471ac6d9": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd-repo-server/commands/argocd_repo_server.go#L257-L280",
        "s4bbc848d9923": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/repo-server/argocd-repo-server-deployment.yaml#L367-L384",
        "sf98b6bc4f5dc": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/application-controller/argocd-application-controller-statefulset.yaml#L360-L365",
        "sf4dd846c82c4": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/common/common.go#L75-L92",
        "s49a7c83d9371": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd-applicationset-controller/commands/applicationset_controller.go#L294-L296",
        "s97a588d8a83f": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/applicationset-controller/argocd-applicationset-controller-service.yaml#L9-L20",
        "s0a85b38dfca8": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd-notification/commands/argocd_notification.go#L149-L154",
        "s5e141e32ed9c": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/notification/argocd-notifications-controller-metrics-service.yaml#L9-L16",
        "s8efcc66f9cb4": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd-dex/commands/argocd_dex.go#L82-L119",
        "s30c391d9dc23": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd-dex/commands/argocd_dex.go#L143-L146",
        "se477de2fdfa0": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/dex/config.go#L16-L152",
        "s56c41c02ba8b": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/dex/argocd-dex-server-service.yaml#L9-L25",
        "s996c72c5db28": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/redis/argocd-redis-deployment.yaml#L18-L58",
        "s34909d7a1932": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/cache/cache.go#L233-L238",
        "s1a13cc06db6d": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/repo-server/argocd-repo-server-network-policy.yaml#L9-L35",
        "s4bbf38e83770": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/redis/argocd-redis-network-policy.yaml#L9-L28",
        "sadccbbcffcd8": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/dex/argocd-dex-server-network-policy.yaml#L9-L29",
        "s743c8187cbd7": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/server/argocd-server-network-policy.yaml#L9-L16",
        "s49f63c21c3cd": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/application-controller/argocd-application-controller-network-policy.yaml#L9-L19",
        "sa258c4109d24": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/applicationset-controller/argocd-applicationset-controller-network-policy.yaml#L9-L22",
        "sa49c30e332ed": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/notification/argocd-notifications-controller-network-policy.yaml#L9-L20",
        "s68b67007da6b": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/settings/settings.go#L1631-L1638",
        "s01a52daf078f": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/server/argocd-server-deployment.yaml#L121-L126",
        "s210b24f04535": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/config/argocd-cmd-params-cm.yaml#L1-L7",
        "s0f7f1b3404d9": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/config/argocd-rbac-cm.yaml#L1-L7"
      }
    },
    "argo-docs": {
      "name": "Argo CD documentation",
      "basis": "unknown",
      "sources": {
        "s51e21b74ece6": "https://argo-cd.readthedocs.io/en/stable/operator-manual/security/",
        "s02463a4fb268": "https://argo-cd.readthedocs.io/en/stable/operator-manual/secret-management/",
        "s2efb9ee633af": "https://argo-cd.readthedocs.io/en/stable/getting_started/",
        "sc2590df86f4e": "https://argo-cd.readthedocs.io/en/stable/operator-manual/user-management/",
        "sf5f1c41f89bd": "https://argo-cd.readthedocs.io/en/stable/operator-manual/rbac/",
        "s3767d400e364": "https://argo-cd.readthedocs.io/en/stable/operator-manual/ingress/",
        "sdac90731b97d": "https://argo-cd.readthedocs.io/en/stable/operator-manual/webhook/",
        "s9357e3b59e84": "https://argo-cd.readthedocs.io/en/stable/user-guide/projects/"
      }
    },
    "flux": {
      "name": "Flux documentation",
      "basis": "unknown",
      "sources": {
        "s493859f3b848": "https://fluxcd.io/flux/security/best-practices/",
        "s4dcd744a2444": "https://fluxcd.io/flux/guides/mozilla-sops/",
        "sd8618bbbc628": "https://fluxcd.io/flux/components/source/ocirepositories/#secret-reference",
        "sf3f80d9941c8": "https://fluxcd.io/flux/installation/configuration/multitenancy/",
        "s0669b973542c": "https://fluxcd.io/flux/security/#controller-permissions",
        "s13bd7f0204b0": "https://fluxcd.io/flux/installation/bootstrap/github/",
        "s8759854c1bdf": "https://fluxcd.io/flux/components/image/imageupdateautomations/",
        "s0acf42beed45": "https://fluxcd.io/flux/guides/webhook-receivers/",
        "s35bb9a844dcf": "https://fluxcd.io/flux/components/notification/receivers/"
      }
    },
    "flux-oidc": {
      "name": "Flux OIDC introduction",
      "basis": "v2.9",
      "sources": {
        "s1ea193b2b3cc": "https://fluxcd.io/blog/2026/06/flux-v2.9.0/"
      }
    },
    "python": {
      "name": "Python documentation",
      "basis": "unknown",
      "sources": {
        "s7a54556e5dac": "https://docs.python.org/3/library/hmac.html",
        "s31fccd7d50e5": "https://docs.python.org/3/library/sys.html#sys.stdin"
      }
    }
  },
  "claims": {
    "git-boundary": {"text": "Repository writers exercise reconciliation permissions; review platform changes, separate tenants and scope credentials.", "components": ["argo-docs", "flux"], "sources": ["argo-docs:s51e21b74ece6", "flux:s493859f3b848"], "status": "REASONED"},
    "secret-storage": {"text": "Protect bootstrap, registry, cluster, webhook and decryption credentials; commit only encrypted secrets and keep SOPS/age keys out of Git.", "components": ["argo-docs", "flux"], "sources": ["argo-docs:s02463a4fb268", "flux:s4dcd744a2444", "flux:sd8618bbbc628"], "status": "REASONED"},
    "egress": {"text": "Restrict fetch, API, identity and notification egress; Argo repository allowlists do not constrain remote bases or Helm dependencies.", "components": ["argo-docs", "flux"], "sources": ["argo-docs:s51e21b74ece6", "flux:sf3f80d9941c8"], "status": "REASONED"},
    "argo-bootstrap": {"text": "Rotate the initial admin password before deleting argocd-initial-admin-secret; deletion alone does not rotate it.", "components": ["argo-docs"], "sources": ["argo-docs:s2efb9ee633af", "argo-docs:sc2590df86f4e"], "status": "REASONED"},
    "argo-sso": {"text": "The built-in admin is unrestricted; configure named SSO roles and IdP MFA, then set admin.enabled=false.", "components": ["argo-docs"], "sources": ["argo-docs:sc2590df86f4e", "argo-docs:sf5f1c41f89bd"], "status": "REASONED"},
    "argo-origin": {"text": "Keep the ClusterIP origin private behind authenticated TLS and protect both REST/browser and CLI/gRPC routes.", "components": ["argo-docs", "argo"], "sources": ["argo-docs:s2efb9ee633af", "argo-docs:s3767d400e364", "argo:sddf4853ad503"], "status": "REASONED"},
    "argo-server": {"text": "Server defaults to 0.0.0.0:8080; the Service maps 80 and 443 to it.", "components": ["argo"], "sources": ["argo:s6e8c96d23e05", "argo:sddf4853ad503", "argo:sf4dd846c82c4"], "status": "REASONED"},
    "argo-tls": {"text": "Server --insecure/server.insecure defaults false and disables backend TLS, not authentication; use only behind protected TLS termination.", "components": ["argo", "argo-docs"], "sources": ["argo:s6e8c96d23e05", "argo-docs:s3767d400e364"], "status": "REASONED"},
    "argo-client-tls": {"text": "argocd login --insecure skips client certificate verification; the server initially uses a self-signed certificate.", "components": ["argo-docs"], "sources": ["argo-docs:s2efb9ee633af", "argo-docs:s3767d400e364"], "status": "REASONED"},
    "argo-metrics": {"text": "Server HTTP metrics on 8083 are unauthenticated and bind to --address, not --metrics-address.", "components": ["argo"], "sources": ["argo:s96065cc09776", "argo:s7cc690d1bf69", "argo:s028a4769d6c3", "argo:sf4dd846c82c4", "argo:s6e8c96d23e05"], "status": "REASONED"},
    "argo-profiler": {"text": "Server and repo-server pprof paths return 401 unless the profiler file contains exactly true with no newline; enabled profiling has no caller authentication.", "components": ["argo"], "sources": ["argo:sc52bbd14bff4", "argo:s028a4769d6c3", "argo:s98b27313f615"], "status": "REASONED"},
    "argo-profiler-file": {"text": "ARGOCD_ENABLE_PROFILER_FILE_PATH defaults to /home/argocd/params/profiler.enabled; the server mounts ConfigMap key server.profile.enabled there.", "components": ["argo"], "sources": ["argo:sc52bbd14bff4", "argo:sb0648e746fb9", "argo:s2f5af86c62d1"], "status": "REASONED"},
    "repo-grpc": {"text": "Repo-server gRPC binds 0.0.0.0:8081 with TLS by default; mTLS is skipped without the client CA, separate from the serving certificate.", "components": ["argo"], "sources": ["argo:s9bca471ac6d9", "argo:s4bbc848d9923", "argo:sf4dd846c82c4"], "status": "REASONED"},
    "repo-http": {"text": "Repo-server HTTP metrics and health bind 0.0.0.0:8084 without an authentication wrapper.", "components": ["argo"], "sources": ["argo:s98b27313f615", "argo:s9bca471ac6d9", "argo:sf4dd846c82c4"], "status": "REASONED"},
    "repo-limits": {"text": "Repo-server RPC authorization and certificate fallback implementations were absent from the inspected subset; isolate cached manifests and operations.", "components": ["argo", "argo-docs"], "sources": ["argo:s9bca471ac6d9", "argo-docs:s02463a4fb268"], "status": "REASONED"},
    "controller-metrics": {"text": "Application-controller metrics and health use 8082; the inspected subset does not establish the bind address.", "components": ["argo"], "sources": ["argo:sf98b6bc4f5dc", "argo:sf4dd846c82c4"], "status": "REASONED"},
    "applicationset-webhook": {"text": "ApplicationSet webhook binds :7000; its container and Service declare 7000.", "components": ["argo"], "sources": ["argo:s49a7c83d9371", "argo:s97a588d8a83f"], "status": "REASONED"},
    "applicationset-metrics": {"text": "ApplicationSet metrics bind :8080; its container and Service declare 8080.", "components": ["argo"], "sources": ["argo:s49a7c83d9371", "argo:s97a588d8a83f"], "status": "REASONED"},
    "applicationset-health": {"text": "ApplicationSet health probes bind :8081 without a container or Service port declaration; missing declarations do not close sockets.", "components": ["argo"], "sources": ["argo:s49a7c83d9371"], "status": "REASONED"},
    "notifications": {"text": "Notifications HTTP metrics bind 0.0.0.0:9001 without authentication; a metrics Service and TCP liveness probe exist without containerPort.", "components": ["argo"], "sources": ["argo:s0a85b38dfca8", "argo:s5e141e32ed9c"], "status": "REASONED"},
    "dex-http": {"text": "Dex starts only with nonempty generated configuration; HTTP defaults to TLS on 0.0.0.0:5556 using /tmp/tls.crt and /tmp/tls.key.", "components": ["argo"], "sources": ["argo:s8efcc66f9cb4", "argo:s30c391d9dc23", "argo:se477de2fdfa0"], "status": "REASONED"},
    "dex-grpc": {"text": "Generated Dex gRPC uses 0.0.0.0:5557 with no TLS or client-auth settings; runtime authentication and authorization remain unverified.", "components": ["argo"], "sources": ["argo:se477de2fdfa0", "argo:s56c41c02ba8b"], "status": "REASONED"},
    "dex-telemetry": {"text": "Dex telemetry uses HTTP on 0.0.0.0:5558; all three Dex ports have Services.", "components": ["argo"], "sources": ["argo:se477de2fdfa0", "argo:s56c41c02ba8b"], "status": "REASONED"},
    "redis-password": {"text": "Redis 6379 receives --requirepass from argocd-redis/auth, initialized by secret-init; image bind and initializer implementation were not inspected.", "components": ["argo"], "sources": ["argo:s996c72c5db28"], "status": "REASONED"},
    "redis-tls": {"text": "Base manifests configure no Redis TLS and the Argo Redis client defaults --redis-use-tls=false; protect traffic, Secret and cache.", "components": ["argo"], "sources": ["argo:s996c72c5db28", "argo:s34909d7a1932"], "status": "REASONED"},
    "component-policies": {"text": "Base policies restrict repo gRPC, Redis and Dex callers by component; enforcement needs a supporting CNI.", "components": ["argo"], "sources": ["argo:s1a13cc06db6d", "argo:s4bbf38e83770", "argo:sadccbbcffcd8"], "status": "REASONED"},
    "broad-policies": {"text": "Server policy allows all ingress; other metrics and ApplicationSet webhook allowances admit every namespace. Narrow existing additive allowances and egress separately.", "components": ["argo"], "sources": ["argo:s743c8187cbd7", "argo:s49f63c21c3cd", "argo:sa258c4109d24", "argo:sa49c30e332ed"], "status": "REASONED"},
    "argo-anonymous": {"text": "users.anonymous.enabled defaults off; anonymous callers otherwise inherit policy.default.", "components": ["argo", "argo-docs"], "sources": ["argo:s68b67007da6b", "argo-docs:sf5f1c41f89bd"], "status": "REASONED"},
    "argo-disable-auth": {"text": "server.disable.auth defaults false; inspect effective args and environment because anonymous-off does not compensate for disabled authentication.", "components": ["argo"], "sources": ["argo:s6e8c96d23e05", "argo:s01a52daf078f", "argo:s210b24f04535"], "status": "REASONED"},
    "argo-default-role": {"text": "Base RBAC ConfigMap omits policy.default; keep it empty and grant explicit policy.csv roles/groups. Default-role grants cannot be revoked by later subject rules; fallback was not traced.", "components": ["argo", "argo-docs"], "sources": ["argo:s0f7f1b3404d9", "argo-docs:sf5f1c41f89bd"], "status": "REASONED"},
    "argo-webhook": {"text": "/api/webhook accepts unauthenticated refresh events without a shared secret; configure one to limit spoofed reconciliation and resource exhaustion.", "components": ["argo-docs"], "sources": ["argo-docs:sdac90731b97d"], "status": "REASONED"},
    "argo-projects": {"text": "Restrict AppProjects including the built-in default project; project constraints do not reduce a compromised controller's Kubernetes credentials.", "components": ["argo-docs"], "sources": ["argo-docs:s9357e3b59e84", "argo-docs:s51e21b74ece6"], "status": "REASONED"},
    "argo-cluster-rbac": {"text": "Reduce controller and registered-cluster argocd-manager write permissions to needed namespaces/resources while retaining required read access.", "components": ["argo-docs"], "sources": ["argo-docs:s51e21b74ece6"], "status": "REASONED"},
    "flux-api": {"text": "Flux has no standalone management login/API; Kubernetes authenticates its custom-resource operations, while separate dashboards need their own controls.", "components": ["flux"], "sources": ["flux:s493859f3b848", "flux:s0669b973542c"], "status": "REASONED"},
    "flux-bootstrap": {"text": "GitHub bootstrap --token-auth retains a PAT in flux-system; --token-auth=false creates a read-only SSH deploy key by default. Protect bootstrap input and Secrets.", "components": ["flux"], "sources": ["flux:s13bd7f0204b0"], "status": "REASONED"},
    "flux-writeback": {"text": "Image automation needs Git write access, including --read-write-key=true for the bootstrap key; scope the repository and protect update branches and objects.", "components": ["flux"], "sources": ["flux:s13bd7f0204b0", "flux:s8759854c1bdf"], "status": "REASONED"},
    "flux-artifacts": {"text": "Source-controller serves fetched artifacts over internal HTTP; enforced NetworkPolicy, not ClusterIP alone, isolates them.", "components": ["flux"], "sources": ["flux:s493859f3b848"], "status": "REASONED"},
    "flux-receiver-port": {"text": "Webhook receiver listens on 9292 behind Service port 80; external exposure needs a route and TLS termination.", "components": ["flux"], "sources": ["flux:s0acf42beed45"], "status": "REASONED"},
    "flux-receiver-types": {"text": "generic validates nothing; generic-hmac, GitHub, Bitbucket and Nexus use HMAC, while gitlab compares X-Gitlab-Token.", "components": ["flux"], "sources": ["flux:s35bb9a844dcf"], "status": "REASONED"},
    "flux-oidc": {"text": "generic-oidc, introduced in Flux 2.9, rejects secretRef and validates bearer tokens; constrain issuer validations and audience, whose default is notification-controller.", "components": ["flux", "flux-oidc"], "sources": ["flux:s35bb9a844dcf", "flux-oidc:s1ea193b2b3cc"], "status": "REASONED"},
    "flux-rbac": {"text": "Only kustomize-controller and helm-controller hold cluster-admin; other controllers still have meaningful permissions including Secret access.", "components": ["flux"], "sources": ["flux:s0669b973542c"], "status": "REASONED"},
    "flux-lockdown": {"text": "Use scoped reconciliation ServiceAccounts, --no-cross-namespace-refs and --no-remote-bases; --default-service-account fills an omission, not an explicit serviceAccountName.", "components": ["flux"], "sources": ["flux:sf3f80d9941c8"], "status": "REASONED"},
    "verify-argo": {"text": "Anonymous application listing should fail with 401 while a valid token lists the expected application; repeat at origin and CLI/gRPC and inspect effective RBAC.", "components": ["argo-docs", "argo"], "sources": ["argo-docs:sf5f1c41f89bd", "argo:s6e8c96d23e05"], "status": "REASONED", "verify": [1]},
    "verify-bootstrap": {"text": "Absence of the bootstrap Secret proves removal of that material, not password rotation.", "components": ["argo-docs"], "sources": ["argo-docs:s2efb9ee633af"], "status": "REASONED", "verify": [1]},
    "verify-inventory": {"text": "Inventory Services, routes, host ports, policies and component sockets; node-local ss and policy objects alone do not establish cluster isolation.", "components": ["argo", "flux"], "sources": ["argo:s743c8187cbd7", "flux:s493859f3b848"], "status": "REASONED", "verify": [1]},
    "verify-repo-metrics": {"text": "Base policy permits HTTP 200 metrics to monitoring and unrelated pods; narrowed policy should admit only monitoring, with a successful positive control.", "components": ["argo"], "sources": ["argo:s98b27313f615", "argo:s1a13cc06db6d"], "status": "REASONED", "verify": [2]},
    "verify-server-metrics": {"text": "Repeat on server 8083: only authorized monitoring should receive metrics after narrowing ingress; a failed control is inconclusive.", "components": ["argo"], "sources": ["argo:s028a4769d6c3", "argo:s743c8187cbd7"], "status": "REASONED"},
    "verify-profiler": {"text": "From an allowed pod, pprof cmdline should return 401 disabled, 200 for exact true, then 401 for true plus newline; keep metrics as control.", "components": ["argo"], "sources": ["argo:sc52bbd14bff4", "argo:s028a4769d6c3"], "status": "REASONED"},
    "verify-flux": {"text": "Identical generic-hmac bodies without and with X-Signature should be rejected and accepted with reconciliation; status is type/version dependent.", "components": ["flux", "python"], "sources": ["flux:s35bb9a844dcf", "python:s7a54556e5dac", "python:s31fccd7d50e5"], "status": "REASONED", "verify": [3]},
    "verify-receiver-status": {"text": "Read receiver name and Ready condition without exposing webhookPath or condition messages; origin checks distinguish receiver rejection from proxy rejection.", "components": ["flux"], "sources": ["flux:s35bb9a844dcf"], "status": "REASONED"}
  }
}
---
# GitOps controllers: Argo CD and Flux

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| git-boundary: Repository writers exercise reconciliation permissions; review platform changes, separate tenants and scope credentials. | Argo CD documentation unknown; Flux documentation unknown | REASONED |
| secret-storage: Protect bootstrap, registry, cluster, webhook and decryption credentials; commit only encrypted secrets and keep SOPS/age keys out of Git. | Argo CD documentation unknown; Flux documentation unknown | REASONED |
| egress: Restrict fetch, API, identity and notification egress; Argo repository allowlists do not constrain remote bases or Helm dependencies. | Argo CD documentation unknown; Flux documentation unknown | REASONED |
| argo-bootstrap: Rotate the initial admin password before deleting argocd-initial-admin-secret; deletion alone does not rotate it. | Argo CD documentation unknown | REASONED |
| argo-sso: The built-in admin is unrestricted; configure named SSO roles and IdP MFA, then set admin.enabled=false. | Argo CD documentation unknown | REASONED |
| argo-origin: Keep the ClusterIP origin private behind authenticated TLS and protect both REST/browser and CLI/gRPC routes. | Argo CD documentation unknown; Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| argo-server: Server defaults to 0.0.0.0:8080; the Service maps 80 and 443 to it. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| argo-tls: Server --insecure/server.insecure defaults false and disables backend TLS, not authentication; use only behind protected TLS termination. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579; Argo CD documentation unknown | REASONED |
| argo-client-tls: argocd login --insecure skips client certificate verification; the server initially uses a self-signed certificate. | Argo CD documentation unknown | REASONED |
| argo-metrics: Server HTTP metrics on 8083 are unauthenticated and bind to --address, not --metrics-address. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| argo-profiler: Server and repo-server pprof paths return 401 unless the profiler file contains exactly true with no newline; enabled profiling has no caller authentication. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| argo-profiler-file: ARGOCD_ENABLE_PROFILER_FILE_PATH defaults to /home/argocd/params/profiler.enabled; the server mounts ConfigMap key server.profile.enabled there. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| repo-grpc: Repo-server gRPC binds 0.0.0.0:8081 with TLS by default; mTLS is skipped without the client CA, separate from the serving certificate. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| repo-http: Repo-server HTTP metrics and health bind 0.0.0.0:8084 without an authentication wrapper. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| repo-limits: Repo-server RPC authorization and certificate fallback implementations were absent from the inspected subset; isolate cached manifests and operations. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579; Argo CD documentation unknown | REASONED |
| controller-metrics: Application-controller metrics and health use 8082; the inspected subset does not establish the bind address. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| applicationset-webhook: ApplicationSet webhook binds :7000; its container and Service declare 7000. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| applicationset-metrics: ApplicationSet metrics bind :8080; its container and Service declare 8080. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| applicationset-health: ApplicationSet health probes bind :8081 without a container or Service port declaration; missing declarations do not close sockets. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| notifications: Notifications HTTP metrics bind 0.0.0.0:9001 without authentication; a metrics Service and TCP liveness probe exist without containerPort. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| dex-http: Dex starts only with nonempty generated configuration; HTTP defaults to TLS on 0.0.0.0:5556 using /tmp/tls.crt and /tmp/tls.key. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| dex-grpc: Generated Dex gRPC uses 0.0.0.0:5557 with no TLS or client-auth settings; runtime authentication and authorization remain unverified. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| dex-telemetry: Dex telemetry uses HTTP on 0.0.0.0:5558; all three Dex ports have Services. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| redis-password: Redis 6379 receives --requirepass from argocd-redis/auth, initialized by secret-init; image bind and initializer implementation were not inspected. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| redis-tls: Base manifests configure no Redis TLS and the Argo Redis client defaults --redis-use-tls=false; protect traffic, Secret and cache. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| component-policies: Base policies restrict repo gRPC, Redis and Dex callers by component; enforcement needs a supporting CNI. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| broad-policies: Server policy allows all ingress; other metrics and ApplicationSet webhook allowances admit every namespace. Narrow existing additive allowances and egress separately. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| argo-anonymous: users.anonymous.enabled defaults off; anonymous callers otherwise inherit policy.default. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579; Argo CD documentation unknown | REASONED |
| argo-disable-auth: server.disable.auth defaults false; inspect effective args and environment because anonymous-off does not compensate for disabled authentication. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| argo-default-role: Base RBAC ConfigMap omits policy.default; keep it empty and grant explicit policy.csv roles/groups. Default-role grants cannot be revoked by later subject rules; fallback was not traced. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579; Argo CD documentation unknown | REASONED |
| argo-webhook: /api/webhook accepts unauthenticated refresh events without a shared secret; configure one to limit spoofed reconciliation and resource exhaustion. | Argo CD documentation unknown | REASONED |
| argo-projects: Restrict AppProjects including the built-in default project; project constraints do not reduce a compromised controller's Kubernetes credentials. | Argo CD documentation unknown | REASONED |
| argo-cluster-rbac: Reduce controller and registered-cluster argocd-manager write permissions to needed namespaces/resources while retaining required read access. | Argo CD documentation unknown | REASONED |
| flux-api: Flux has no standalone management login/API; Kubernetes authenticates its custom-resource operations, while separate dashboards need their own controls. | Flux documentation unknown | REASONED |
| flux-bootstrap: GitHub bootstrap --token-auth retains a PAT in flux-system; --token-auth=false creates a read-only SSH deploy key by default. Protect bootstrap input and Secrets. | Flux documentation unknown | REASONED |
| flux-writeback: Image automation needs Git write access, including --read-write-key=true for the bootstrap key; scope the repository and protect update branches and objects. | Flux documentation unknown | REASONED |
| flux-artifacts: Source-controller serves fetched artifacts over internal HTTP; enforced NetworkPolicy, not ClusterIP alone, isolates them. | Flux documentation unknown | REASONED |
| flux-receiver-port: Webhook receiver listens on 9292 behind Service port 80; external exposure needs a route and TLS termination. | Flux documentation unknown | REASONED |
| flux-receiver-types: generic validates nothing; generic-hmac, GitHub, Bitbucket and Nexus use HMAC, while gitlab compares X-Gitlab-Token. | Flux documentation unknown | REASONED |
| flux-oidc: generic-oidc, introduced in Flux 2.9, rejects secretRef and validates bearer tokens; constrain issuer validations and audience, whose default is notification-controller. | Flux documentation unknown; Flux OIDC introduction v2.9 | REASONED |
| flux-rbac: Only kustomize-controller and helm-controller hold cluster-admin; other controllers still have meaningful permissions including Secret access. | Flux documentation unknown | REASONED |
| flux-lockdown: Use scoped reconciliation ServiceAccounts, --no-cross-namespace-refs and --no-remote-bases; --default-service-account fills an omission, not an explicit serviceAccountName. | Flux documentation unknown | REASONED |
| verify-argo: Anonymous application listing should fail with 401 while a valid token lists the expected application; repeat at origin and CLI/gRPC and inspect effective RBAC. | Argo CD documentation unknown; Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| verify-bootstrap: Absence of the bootstrap Secret proves removal of that material, not password rotation. | Argo CD documentation unknown | REASONED |
| verify-inventory: Inventory Services, routes, host ports, policies and component sockets; node-local ss and policy objects alone do not establish cluster isolation. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579; Flux documentation unknown | REASONED |
| verify-repo-metrics: Base policy permits HTTP 200 metrics to monitoring and unrelated pods; narrowed policy should admit only monitoring, with a successful positive control. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| verify-server-metrics: Repeat on server 8083: only authorized monitoring should receive metrics after narrowing ingress; a failed control is inconclusive. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| verify-profiler: From an allowed pod, pprof cmdline should return 401 disabled, 200 for exact true, then 401 for true plus newline; keep metrics as control. | Argo CD v3.5.3 source c9c369efcc5b2a0bd720803f8d14a1c3eaddf579 | REASONED |
| verify-flux: Identical generic-hmac bodies without and with X-Signature should be rejected and accepted with reconciliation; status is type/version dependent. | Flux documentation unknown; Python documentation unknown | REASONED |
| verify-receiver-status: Read receiver name and Ready condition without exposing webhookPath or condition messages; origin checks distinguish receiver rejection from proxy rejection. | Flux documentation unknown | REASONED |
<!-- version-basis:end -->

Argo CD and Flux reconcile a git repository into a Kubernetes cluster, so both hold
cluster-admin-equivalent power: whoever can drive the controller, or change what it reconciles, can
deploy anything it can reach, across the clusters it is registered against and to the extent the controller's Kubernetes RBAC, its registered-cluster credentials, and project restrictions allow. Three exposures follow
from that and apply to both. The blast radius is the cluster (or clusters), so administrative access
deserves the same care as the Kubernetes API itself ([kubernetes.md](kubernetes.md)). Git is an
authorization boundary: whoever can merge to a reconciled repository, or redirect a source, exercises
the controller's permissions, so platform repositories need reviewed changes and separation from
tenant repositories. And the credentials the controllers hold (git deploy keys, cluster Secrets)
should be read-only and narrowly scoped where the work allows. Handle every credential class per
[secrets.md](secrets.md): bootstrap tokens, git and registry credentials (Flux `OCIRepository`/`HelmRepository`
`.spec.secretRef`), cluster credentials, webhook secrets, and decryption keys. Never commit plaintext
credentials or base64-only Secret manifests; encrypted SOPS files and SealedSecret resources may be
committed, but Sealed Secrets is a separate controller and SOPS/age decryption keys (Flux references them
from the Kustomization) must be protected and never committed. For Argo CD, prefer destination-cluster
secret operators, because config-management plugins can surface decrypted values through Redis and the
repo-server. The tools differ in one way that shapes
the rest: Argo CD runs a network-facing API and UI with its own accounts, while Flux has no standalone
management UI or user-login API of its own, and is driven through Kubernetes custom resources under the
API server's authentication and RBAC (its controllers still expose in-cluster HTTP endpoints, and a
separately installed Flux dashboard brings its own login and exposure to harden). Control-plane exposure itself, the API server and etcd, stays in
[kubernetes.md](kubernetes.md). Egress is a surface too: both controllers fetch from Git, container and
chart registries, the Kubernetes API, identity/KMS, and notification targets, and Argo CD's repository
allowlist does not constrain remote bases or Helm chart dependencies while its webhook path has an SSRF
consideration, so restrict controller egress to the destinations each deployment needs and apply the
metadata protections in [egress-metadata.md](egress-metadata.md), keeping only the metadata access the
identity mechanism requires (for Flux tenant reconciliation, `--no-remote-bases=true` where applicable).

## Argo CD

The install generates an initial `admin` password and stores it in cleartext in a Secret named
`argocd-initial-admin-secret`, in the `password` field. Rotate it and then delete the Secret:
`argocd account update-password` changes the password, and the vendor says the Secret "can safely be
deleted" afterward since it only holds the bootstrap value. Deleting the Secret does not by itself
rotate the credential, so change the password first. `admin` is the only built-in user and a
superuser with unrestricted access; once you have configured SSO (OIDC or Dex) and granted named
roles, disable it with `admin.enabled: "false"` in the `argocd-cm` ConfigMap, and pair Argo CD logins
with your identity provider's MFA ([mfa.md](mfa.md)).

The quickstart does not expose the API and UI outside the cluster; `argocd-server` is a ClusterIP
Service, and reaching it is a deliberate act through a LoadBalancer, an Ingress, a Gateway route, or
`kubectl port-forward`. When you do route to it, give it real TLS. The server ships a self-signed
certificate, and its `--insecure` flag runs the server with no TLS of its own; that is meant for a
setup where an ingress terminates trusted TLS in front and reaches the backend over a protected
network, not for anything a client reaches directly. The client flag `argocd login --insecure` is a
separate setting that skips certificate verification on the client side, and is unsafe against any
real deployment. At Argo CD v3.5.3 (commit `c9c369efcc5b2a0bd720803f8d14a1c3eaddf579`), the server defaults to
`0.0.0.0:8080` in the pod (its Service maps `80` and `443` to it), with separate metrics on
`0.0.0.0:8083`; front it per [nginx.md](nginx.md), [caddy.md](caddy.md) and
[fronting-auth.md](fronting-auth.md). Keep `argocd-server` as a ClusterIP and do not publish the origin through a public LoadBalancer, NodePort, or alternate route; reach it only through a restricted, authenticated TLS ingress (or private administrative access), and protect the CLI/gRPC path as well as the browser/REST one, since the Service carries both on `443`. `server.insecure` in `argocd-cmd-params-cm` is the ConfigMap form of `--insecure` and defaults to `"false"`; it disables the backend's TLS, not authentication, so allow it only behind trusted TLS termination on a protected network.

ClusterIP is not a pod-network access control. The v3.5.3 component inventory also includes:

| Component | Listener and bind evidence | Base manifest exposure |
| --- | --- | --- |
| Repo-server | gRPC `0.0.0.0:8081`; HTTP metrics and health `0.0.0.0:8084` | Both container ports and Service ports |
| Application controller | Metrics and health on port `8082`; the supplied source subset lacks the bind implementation | Container port and `argocd-metrics` Service |
| ApplicationSet controller | Webhook `:7000`, metrics `:8080`, health probes `:8081`; empty hosts are wildcard binds | Container and Service ports `7000` and `8080`; probe port `8081` has neither declaration |
| Notifications controller | HTTP metrics `0.0.0.0:9001` | Metrics Service and TCP liveness probe; no `containerPort` declaration |
| Dex | Generated `web.https` (or `web.http` with TLS disabled) `0.0.0.0:5556`, `grpc.addr` `0.0.0.0:5557` and telemetry `http` `0.0.0.0:5558` | All three container and Service ports; the wrapper starts Dex only with a nonempty generated configuration |
| Redis | Port `6379`; no bind override in the Deployment, so the address is inherited from the Redis image and not established by this source subset | Container port and Service |

Repo-server's metrics/health mux and notifications' metrics handler have no authentication wrapper
and use HTTP, so a reachable pod-network peer can request them without an Argo CD login. Repo-server
gRPC defaults to TLS (`--disable-tls=false`), but the command documents skipping mTLS when
`/app/config/reposerver/mtls/client-ca.crt` is absent. The base Deployment optionally mounts
`argocd-repo-server-mtls` for that client CA, separately from `argocd-repo-server-tls` for the serving
certificate. A serving certificate alone does not require a client identity. The RPC implementation
and certificate fallback helper are absent from this source subset, so method-level authorization
and certificate fallback are not verified here. Isolate repository operations and cached manifests
from unrelated pods.

Redis is not passwordless in these base manifests: the `secret-init` init container runs
`argocd admin redis-initial-password`, and Redis receives `--requirepass` from the `auth` key of the
`argocd-redis` Secret. This is an init container, not a separate Job. No Redis TLS is configured by
these manifests, and Argo CD's Redis client defaults to `--redis-use-tls=false`; protect that traffic
and Secret as well as the cached data. The password initializer's implementation and the Redis
image's bind configuration are absent from this source subset.

Dex's wrapper defaults to TLS for its HTTP endpoint. The generator replaces the `web`, `grpc` and
`telemetry` mappings: `web.https` uses `/tmp/tls.crt` and `/tmp/tls.key`, or `web.http` is used with
`--disable-tls`; `grpc` contains only `addr: 0.0.0.0:5557`, with no TLS or client-authentication
settings, and telemetry uses HTTP on `0.0.0.0:5558`. HTTP TLS does not secure the gRPC listener.
Dex's own server and handler implementations are absent from this source subset, so gRPC runtime
authentication and method-level authorization remain unverified; the generated configuration
provides neither TLS nor client-authentication settings for them.

Server metrics on `8083` use a plain HTTP server whose `/metrics` handler is registered through
`promhttp` with no authentication wrapper. The socket binds to `server.ListenHost`, following
`--address` (default `0.0.0.0`), not the separate metrics host; setting `--metrics-address` does not
restrict this socket in v3.5.3. The same mux registers `/debug/pprof/`, `/debug/pprof/cmdline`,
`/debug/pprof/profile`, `/debug/pprof/symbol` and `/debug/pprof/trace`. Each returns `401` unless
the file selected by `ARGOCD_ENABLE_PROFILER_FILE_PATH` (default
`/home/argocd/params/profiler.enabled`) contains exactly `true`, with no newline. The base server
Deployment mounts the `server.profile.enabled` key from `argocd-cmd-params-cm` at that path;
`profiler.enabled` is the filename, not the ConfigMap key. When enabled, these pprof endpoints
require no caller authentication: anyone who can reach `8083` can use them. This is an enable
switch, not an identity check. Repo-server's `8084` mux also registers the same file-gated pprof
handlers. Keep profiling disabled except during controlled diagnostics, and restrict both metrics
listeners to authorized monitoring and diagnostic callers. API authentication protects neither.

The base kustomizations include NetworkPolicies. Repo-server gRPC admits the server, application
controller, notifications controller and ApplicationSet controller in the same namespace; Redis
admits the server, repo-server and application controller; Dex HTTP/gRPC admits the server. These
restrictions need an enforcing CNI. They are not a blanket isolation policy: the server policy
allows all ingress, while the other metrics policies admit pods from every namespace, and the
ApplicationSet policy also admits its webhook from every namespace. Replace or narrow those
allowances to the required ingress, component and monitoring callers, per [kubernetes.md](kubernetes.md).
NetworkPolicy allows are additive, so an additional restrictive policy does not cancel an existing
allow-all rule. Restrict egress separately. A container-port declaration is metadata, not a firewall;
its absence does not close a pod socket.

For v3.5.3, the base command-parameters ConfigMap omits both server switches; their CLI defaults
are false. The base RBAC ConfigMap omits `policy.default` rather than declaring a role.
The RBAC fallback implementation is absent from this source subset; the empty-default-role advice
below retains the vendor RBAC guidance, rather than claiming that fallback was traced here.
Two settings decide who reaches the API without an account. Anonymous access is disabled by default
(`users.anonymous.enabled`); keep it off, because an anonymous caller is granted whatever role
`policy.default` names. Leave `policy.default` empty, which is its safe default in the
`argocd-rbac-cm` ConfigMap: an authenticated user who matches no role then gets no access, and access
is granted through explicit roles and group mappings instead. Anonymous access is not the only client-auth switch: keep `server.disable.auth: "false"` in the `argocd-cmd-params-cm` ConfigMap (its default), and inspect the running server's effective arguments and environment for any override that turns client authentication off, because disabling anonymous access does not compensate for authentication being disabled outright. Argo CD RBAC grants through the default
role are additive and cannot be revoked by a later subject rule, so a permissive default is
especially hard to walk back. Define the actual permissions in `policy.csv` in `argocd-rbac-cm`: a `p` rule such as `p, role:team, applications, get, team-project/*, allow` and a `g` rule mapping the intended IdP group to that role, then confirm the group reaches its project and not an unrelated one. Separately, `argocd-server` serves an inbound git-webhook handler at
`/api/webhook` that accepts events without authentication unless you configure a webhook shared
secret; it triggers application refreshes and reconciliations rather than deploying attacker-supplied
manifests, but leaving it open to spoofed events is a reconciliation and resource-exhaustion vector
once the server is routed externally, so set the secret whenever it is reachable.

Finally, the `argocd-manager` ServiceAccount that Argo CD installs on a registered cluster is bound to
an admin-level ClusterRole, so driving Argo CD is deployment power over every cluster it manages;
scope who can act through project roles, move applications into restricted `AppProject`s, and tighten
the permissive built-in `default` project itself rather than only moving applications out of it, since
it still governs any new application placed there. AppProjects constrain actions through Argo CD but do not shrink the Kubernetes credentials a compromised controller holds, so also reduce the controller and each registered cluster's `argocd-manager` service-account write permissions to the namespaces and resource kinds actually needed (keeping the read access the install mode requires); a repository writer exercises whatever its reconciliation can do, not inherently every registered cluster. Argo CD's Redis cache and repo-server can also hold
generated manifests, which matter when a config-management plugin injects secrets into them; restrict
access to them with enforced NetworkPolicies, the same isolation Flux's artifacts need. Treat Argo
CD access as cluster-admin
access.

## Flux

Flux has no standalone user-login or management API of its own: it is a set of in-cluster controllers
that reconcile git into the cluster, driven through Kubernetes custom resources under the API server's
authentication and RBAC. There is no login surface of its own to harden, but its controllers still expose
in-cluster HTTP endpoints (below), and a separately installed Flux dashboard brings its own login and exposure. Its
controllers do expose in-cluster listeners (the webhook receiver, the source-controller's artifact
server, metrics, health), so an `ss` inside a controller's own network namespace still shows sockets;
that is expected, not a finding. The surfaces that matter are three. Git repository credentials,
referenced as Secrets by the sources, are the primary one: use read-only deploy credentials for
pull-only reconciliation, keep tenant repositories separate from platform repositories, and narrow
the RBAC on the Secrets that hold them. Bootstrap credentials are separate from reconciliation ones:
`flux bootstrap github --token-auth` leaves the PAT in the cluster as the `flux-system` Secret in the
`flux-system` namespace, while `--token-auth=false` provisions an SSH deploy key that is read-only by
default; prefer the narrowly scoped key, restrict access to that Secret, and pass any bootstrap token
through stdin or the prompt, never Git or logs. Image automation is the exception to read-only: the
image-automation-controller commits manifest changes back to Git and needs write access (`--read-write-key=true`
when it uses the bootstrap deploy key), so scope that credential to the one repository, protect the
deployment branch, use a dedicated update branch, and restrict who may edit `ImageUpdateAutomation` objects. The source-controller then serves the fetched artifacts to the
other controllers over an internal HTTP listener, and Flux relies on Kubernetes NetworkPolicies, not a
ClusterIP alone, to keep that access to Flux components; apply them, since a CNI that enforces
NetworkPolicy is what actually isolates the artifacts.

The notification-controller webhook receiver is the deliberate network surface. The controller handles
webhook requests on port `9292`, and its `webhook-receiver` Service exposes them on port `80`,
forwarding to `9292`; it is reachable from outside only if you put a LoadBalancer, Ingress, or Gateway
route in front of it. When you do, the receiver type is what authenticates the request, not merely the
presence of a `secretRef`: a `generic` receiver validates nothing, `generic-hmac` and the GitHub,
Bitbucket and Nexus types verify an HMAC signature against the referenced secret, `gitlab` compares
the `X-Gitlab-Token` header against it, and `generic-oidc` validates a bearer token against configured
OIDC providers rather than a secret (new in Flux 2.9, and it rejects `.spec.secretRef`), so
constrain it with `.spec.oidcProviders[].validations` and a specific `.audience` (which otherwise
defaults to `notification-controller`), since a public issuer can otherwise mint valid tokens for
unrelated callers. Choose a validating type,
terminate TLS at the ingress, and
confine what a webhook can trigger with cross-namespace reference policies.

The third surface is Kubernetes RBAC. Only the kustomize-controller and helm-controller are bound to
`cluster-admin`, because they apply resources, though every controller holds meaningful permissions
including Secret access. Restrict tenant reconciliation to scoped ServiceAccounts: Flux offers
`--no-cross-namespace-refs` to stop a tenant referencing another namespace's sources,
`--default-service-account` to fall back to a named account when a reconciliation omits its own
`spec.serviceAccountName` (it does not override an explicit one), and related lockdown settings;
enable the ones your tenancy needs, and protect the
platform git sources that feed the privileged controllers.

## Verify

Every probe below is REASONED, not demonstrated: the authoring environment has no container runtime;
also, the authoring host forbids opening listeners without an isolated network namespace, and has none;
there is no Kubernetes cluster. None was stood up in its exposed and fixed states. Each names its expected exposed and fixed result
so it discriminates against a live install, based on the cited vendor documentation and pinned source readings. A login page, a
redirect, a `404`, an HTML body, a TLS error, a `kubectl` `Forbidden`, or a missing-CRD error is
inconclusive, never the fixed state.

Backlog row 2.28 retains only the missing-source audits: controller binds, repo-server RPC authorization
and certificate fallback, Dex runtime authentication and authorization, the Redis image bind and
password initializer, and the RBAC fallback. Those implementations are not fully traced here.

```bash
# REASONED: Argo CD API and cluster inventory checks follow the cited documentation and pinned sources;
# no container runtime, isolated network namespace or Kubernetes cluster is available.
# Argo CD API auth, matched pair against the SAME endpoint. Use your real CA, never -k. Anonymous (no
# token) must answer 401 fixed (application JSON exposed); with a valid bearer token it must return JSON
# listing the expected application - the positive control a fronting proxy's 401 cannot fake. Repeat both
# against the ORIGIN from an authorized location (keep the TLS hostname), and test the gRPC/CLI path too.
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 --cacert REPLACE_WITH_YOUR_CA_FILE \
  -w '\nanon http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
  'https://argocd.example.com/api/v1/applications'
# token from `argocd account generate-token` (or a login session); read it without echo, pass via stdin.
# Run in a subshell with tracing, allexport and errexit OFF, so an inherited `set -x` cannot echo the token,
# an inherited `set -a` cannot export it (read -s and the stdin header prevent neither), and an inherited
# `set -e` cannot end the block early.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  { unset -n tok && unset -v tok; } 2>/dev/null ||
    { echo 'a readonly tok is set in this shell; not probing'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not probing'; exit 2; }
  IFS= read -r -s -p 'Argo CD bearer token: ' tok < /dev/tty || exit 2; echo
  case "$tok" in ''|*[[:cntrl:]]*) echo 'supply the token; not probing'; exit 2 ;; esac
  printf 'Authorization: Bearer %s\n' "$tok" \
    | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 --cacert REPLACE_WITH_YOUR_CA_FILE \
        -H @- -w '\nauth http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
        'https://argocd.example.com/api/v1/applications'
)
# The bootstrap admin Secret should be gone once the password was rotated (its presence proves retained
# bootstrap material; its absence alone does not prove the password changed). This prints no secret.
kubectl -n argocd get secret argocd-initial-admin-secret -o name
# Network inventory: management access should have no external route. List Services, Ingresses, and
# Gateway routes, not only the named Service, since another Service, a NodePort, or an HTTPRoute can
# reach the same pods.
kubectl -n argocd get svc -o wide
kubectl -n argocd get networkpolicy -o yaml
kubectl -n argocd get pods -o wide
kubectl -n flux-system get svc -o wide
kubectl get ingress,httproute,grpcroute,tlsroute -A   # also check NodePort Services and host-network/hostPort pods
sudo ss -tlnp    # speaks only for the node and network namespace it runs in, not the whole cluster
```

For internal isolation, inventory actual sockets in each component's network namespace with
`ss -tlnp`, including ports absent from container declarations. Review rendered policies and CNI
enforcement; a NetworkPolicy object's presence alone proves neither reachability nor denial.
The following probe is REASONED for the same missing isolation and cluster capabilities above. Run it inside an authorized monitoring pod and an unrelated pod in another
namespace, against the same actual repo-server pod IP. With the base metrics allowance, expect HTTP
200 and Prometheus metrics from both. After narrowing the allowance, expect no HTTP response from
the unrelated pod while the monitoring pod still receives those metrics. A timeout alone, a missing
curl binary, or a failed positive control is inconclusive. The pinned repo-server mux and
NetworkPolicy below supply the exposed-state basis.

```bash
# REASONED: repo-server metrics isolation follows the cited pinned mux and NetworkPolicy;
# no isolated network namespace or Kubernetes cluster is available.
(
  set -- secureconfig-probe REPLACE_WITH_REPO_SERVER_POD_IP
  [ "${1-}" = secureconfig-probe ] && [ "$#" -eq 2 ] || { echo 'incomplete probe; not probing'; exit 2; }
  shift
  case "${1-}" in
    ''|*REPLACE_WITH*|*[!0123456789.]*) echo 'supply the actual IPv4 pod address; not probing'; exit 2 ;;
  esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "http://$1:8084/metrics"
)
```

For server metrics, repeat the guarded pod-IP probe above with the actual server pod IP and
port `8083`, keeping `/metrics`. This check is also REASONED for the missing isolated network
namespace and Kubernetes cluster. Before narrowing the server's allow-all policy,
expect HTTP 200 and Prometheus metrics without credentials from both pods; afterwards only the
authorized monitoring pod should receive them. From that allowed pod, repeat with
`/debug/pprof/cmdline`: expect `401` with profiling disabled, then HTTP 200 and the process command
line when the mounted file contains exactly `true`. In an isolated demonstration, confirm that
`true` followed by a newline returns `401` again. Keep `/metrics` as the positive control throughout;
a failed control is inconclusive. Return profiling to disabled after the demonstration. The pinned
metrics mux, profiler wrapper and server NetworkPolicy below distinguish these states.

A bare `401` proves less than it looks: a fronting authentication proxy can return it while the
underlying `users.anonymous.enabled` is still on, so pair the probe with an authenticated request
through the same route that should succeed, and read the anonymous and `policy.default` settings from
`argocd-cm`/`argocd-rbac-cm` directly. For Flux, test the webhook with an **unauthenticated** request, not merely an unsigned body, since a valid
`X-Gitlab-Token` or OIDC token authenticates without a signature. For a `generic-hmac` receiver the
signature is `X-Signature: sha256=<hex HMAC of the exact body under the receiver's secret>`; send identical
bytes without it (must be rejected) and then with it (must be accepted and trigger the reconciliation):

```bash
# REASONED: Flux webhook checks follow the cited receiver documentation; no live Flux is available.
# Read the HMAC key without echo.
# Python's hmac reads the key from stdin; only the non-secret request body is passed in argv.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  { unset -n hmac sig && unset -v hmac sig; } 2>/dev/null ||
    { echo 'a readonly hmac or sig is set in this shell; not probing'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not probing'; exit 2; }
  IFS= read -r -s -p 'receiver HMAC secret: ' hmac < /dev/tty || exit 2; echo
  [ -n "$hmac" ] || { echo 'supply the HMAC secret; not probing'; exit 2; }
  body='{"ref":"refs/heads/main"}'
  sig=$(set -o pipefail; printf '%s' "$hmac" | python3 -c \
    'import hmac, sys; print(hmac.new(sys.stdin.buffer.read(), sys.argv[1].encode(), "sha256").hexdigest())' "$body") ||
    { echo 'signature generation failed; not probing'; exit 2; }
  [ -n "$sig" ] || { echo 'signature generation failed; not probing'; exit 2; }
  url='https://flux-webhook.example.com/hook/REPLACE_WITH_PATH'
  printf '%s' "$body" | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -X POST --data-binary @- -w '\nno-sig http=%{http_code}\n' "$url"          # expect rejected
  printf '%s' "$body" | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -X POST --data-binary @- -H "X-Signature: sha256=$sig" -w '\nsigned http=%{http_code}\n' "$url"  # expect accepted
)
```

Read the receiver's status without printing the default table, full status, condition messages, or
`.status.webhookPath` (status messages can carry the generated path, itself a capability for a `generic`
receiver): select the name and the Ready condition explicitly. The rejection status is type- and
version-dependent, so read it as rejected rather than a fixed code. A malformed-payload error or a
proxy-only rejection is inconclusive; repeat against the receiver origin from an authorized location.
Because these checks discriminate on a response rather than on silence, they take the plain form above;
a bare reachability probe of your own public address, whose pass is nothing answering, would instead
need the guarded-subshell form so an unsubstituted address cannot time out and read as closed.

## Sources (checked September 2026)

- Python HMAC calculation and binary stdin: https://docs.python.org/3/library/hmac.html and https://docs.python.org/3/library/sys.html#sys.stdin

Argo CD source claims below were checked offline at v3.5.3, commit
`c9c369efcc5b2a0bd720803f8d14a1c3eaddf579`. Retained readthedocs links provide operational guidance;
they were not rechecked online. Missing source implementations are identified above.

- Argo CD Listener constants: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/common/common.go#L75-L92
- Argo CD Server CLI bind, TLS and authentication defaults: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd-server/commands/argocd_server.go#L307-L323
- Argo CD Server main and metrics socket binding: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L512-L535
- Argo CD Server metrics served separately: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L668-L677
- Argo CD Server unauthenticated HTTP metrics mux and profiler registration: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/metrics/metrics.go#L74-L100
- Argo CD Profiler paths and exact file-content gate: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/profile/profile.go#L11-L30
- Argo CD Server command-parameters mount: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/server/argocd-server-deployment.yaml#L406-L408
- Argo CD Server profiler ConfigMap key and filename: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/server/argocd-server-deployment.yaml#L475-L481
- Argo CD Anonymous access setting: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/settings/settings.go#L1631-L1638
- Argo CD Base command-parameters ConfigMap: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/config/argocd-cmd-params-cm.yaml#L1-L7
- Argo CD Base RBAC ConfigMap with no default role: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/config/argocd-rbac-cm.yaml#L1-L7
- Argo CD Server authentication ConfigMap wiring: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/server/argocd-server-deployment.yaml#L121-L126
- Argo CD Server Service mapping: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/server/argocd-server-service.yaml#L9-L20
- Argo CD Repo-server HTTP metrics and health mux: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd-repo-server/commands/argocd_repo_server.go#L180-L212
- Argo CD Repo-server addresses and TLS/client-CA defaults: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd-repo-server/commands/argocd_repo_server.go#L257-L280
- Argo CD Separate optional repo-server TLS and mTLS Secrets: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/repo-server/argocd-repo-server-deployment.yaml#L367-L384
- Argo CD Application-controller metrics port and health probe: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/application-controller/argocd-application-controller-statefulset.yaml#L360-L365
- Argo CD ApplicationSet wildcard listeners: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd-applicationset-controller/commands/applicationset_controller.go#L294-L296
- Argo CD ApplicationSet Service ports: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/applicationset-controller/argocd-applicationset-controller-service.yaml#L9-L20
- Argo CD Notifications HTTP metrics bind and handler: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd-notification/commands/argocd_notification.go#L149-L154
- Argo CD Notifications metrics Service: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/notification/argocd-notifications-controller-metrics-service.yaml#L9-L16
- Argo CD Dex TLS setup and conditional startup: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd-dex/commands/argocd_dex.go#L82-L119
- Argo CD Dex HTTP TLS default: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd-dex/commands/argocd_dex.go#L143-L146
- Argo CD Dex configuration generation, including wildcard binds and gRPC without TLS/client-auth settings: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/dex/config.go#L16-L152
- Argo CD Dex declared Service ports: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/dex/argocd-dex-server-service.yaml#L9-L25
- Argo CD Redis password initialization and required Secret: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/redis/argocd-redis-deployment.yaml#L18-L58
- Argo CD Redis client TLS is opt-in: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/cache/cache.go#L233-L238
- Argo CD Server allow-all ingress policy: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/server/argocd-server-network-policy.yaml#L9-L16
- Argo CD Repo-server component selectors and metrics allowance: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/repo-server/argocd-repo-server-network-policy.yaml#L9-L35
- Argo CD Redis component selectors: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/redis/argocd-redis-network-policy.yaml#L9-L28
- Argo CD Dex component selectors and metrics allowance: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/dex/argocd-dex-server-network-policy.yaml#L9-L29
- Argo CD Application-controller metrics allowance: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/application-controller/argocd-application-controller-network-policy.yaml#L9-L19
- Argo CD ApplicationSet webhook and metrics allowance: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/applicationset-controller/argocd-applicationset-controller-network-policy.yaml#L9-L22
- Argo CD Notifications metrics allowance: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/notification/argocd-notifications-controller-network-policy.yaml#L9-L20
- Argo CD getting started (initial admin secret, server exposure): https://argo-cd.readthedocs.io/en/stable/getting_started/
- Argo CD user management (disable admin, change password): https://argo-cd.readthedocs.io/en/stable/operator-manual/user-management/
- Argo CD RBAC (anonymous access, policy.default in argocd-rbac-cm): https://argo-cd.readthedocs.io/en/stable/operator-manual/rbac/
- Argo CD ingress and TLS termination: https://argo-cd.readthedocs.io/en/stable/operator-manual/ingress/
- Argo CD git webhook configuration (/api/webhook, shared secret): https://argo-cd.readthedocs.io/en/stable/operator-manual/webhook/
- Argo CD AppProjects: https://argo-cd.readthedocs.io/en/stable/user-guide/projects/
- Flux security model and best practices (NetworkPolicy artifact isolation, controller permissions): https://fluxcd.io/flux/security/best-practices/
- Flux notification Receivers (types and payload validation): https://fluxcd.io/flux/components/notification/receivers/
- Flux v2.9 release (generic-oidc receiver introduced): https://fluxcd.io/blog/2026/06/flux-v2.9.0/
- Flux webhook receivers guide (port 9292, webhook-receiver Service): https://fluxcd.io/flux/guides/webhook-receivers/
- Flux multitenancy configuration (cross-namespace and service-account lockdown): https://fluxcd.io/flux/installation/configuration/multitenancy/
- Argo CD cluster RBAC and security (narrowing `argocd-manager` privileges, remote-bases/SSRF): https://argo-cd.readthedocs.io/en/stable/operator-manual/security/
- Argo CD secret management (destination-cluster operators, repo-server/Redis exposure): https://argo-cd.readthedocs.io/en/stable/operator-manual/secret-management/
- Flux GitHub bootstrap (`--token-auth` PAT Secret, `--read-write-key` for image automation): https://fluxcd.io/flux/installation/bootstrap/github/
- Flux image update automations (Git write-back): https://fluxcd.io/flux/components/image/imageupdateautomations/
- Flux SOPS/age decryption: https://fluxcd.io/flux/guides/mozilla-sops/
- Flux OCIRepository and HelmRepository credential references (`.spec.secretRef`): https://fluxcd.io/flux/components/source/ocirepositories/#secret-reference
- Flux controller permissions (which controllers hold cluster-admin, Secret access): https://fluxcd.io/flux/security/#controller-permissions
