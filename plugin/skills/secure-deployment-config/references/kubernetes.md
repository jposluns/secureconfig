---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "7e9c37235c767ce4c97180557f7fc13cbc1a6ae20c76c63b13e8575c55ffab75",
  "components": {
    "kubernetes": {
      "name": "Kubernetes documentation",
      "basis": "unknown",
      "sources": {
        "s0f11d6ed39b7": "https://kubernetes.io/blog/2026/01/29/ingress-nginx-statement/",
        "sca23283c5a9b": "https://kubernetes.io/docs/concepts/services-networking/gateway/",
        "sd8c8df3b9ddc": "https://kubernetes.io/docs/concepts/services-networking/ingress/",
        "se41a53ea6778": "https://kubernetes.io/docs/reference/config-api/kubeconfig.v1/",
        "sae633285120e": "https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/",
        "sd59fb2f35cd7": "https://kubernetes.io/docs/reference/networking/ports-and-protocols/",
        "s01f081fed0ff": "https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/",
        "s49a29258961b": "https://kubernetes.io/docs/reference/access-authn-authz/kubelet-authn-authz/",
        "s04f0c3099fd7": "https://kubernetes.io/docs/reference/kubectl/jsonpath/"
      }
    },
    "kubelet": {
      "name": "Kubernetes kubelet/kubeadm source",
      "basis": "v1.37.1",
      "sources": {
        "sc6056d6413a0": "https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/cmd/kubelet/app/options/options.go#L196-L224",
        "s227d2a259fd3": "https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/cmd/kubelet/app/options/options.go#L373-L398",
        "s568cd52cc674": "https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/pkg/kubelet/apis/config/v1beta1/defaults.go#L85-L102",
        "s2daf96dabbdf": "https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/cmd/kubelet/app/options/options.go#L281",
        "s24ba323c3dab": "https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/cmd/kubelet/app/options/options.go#L282",
        "sd81692a1876f": "https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/cmd/kubeadm/app/componentconfigs/kubelet.go#L33-L48",
        "s0eb30acf2f46": "https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/cmd/kubeadm/app/componentconfigs/kubelet.go#L95-L100",
        "s1c86aaef7307": "https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/cmd/kubeadm/app/componentconfigs/kubelet.go#L144-L188",
        "sb98bd327db92": "https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/cmd/kubeadm/app/componentconfigs/utils.go#L66-L71",
        "s3fc405855b4a": "https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/staging/src/k8s.io/kubelet/config/v1beta1/types.go#L160-L176",
        "s98cf98130201": "https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/pkg/kubelet/server/server.go#L181-L250",
        "s8bea69523ed9": "https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/pkg/kubelet/server/server.go#L339-L375",
        "sa02a895a475c": "https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/pkg/cluster/ports/ports.go#L32-L37",
        "s6b753b247f8a": "https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/pkg/kubelet/server/server.go#L477-L572",
        "sd00d4cdb9276": "https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/pkg/kubelet/server/stats/handler.go#L109-L133",
        "s02441dcae3cf": "https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/pkg/kubelet/server/server.go#L577-L610"
      }
    },
    "envoy": {
      "name": "Envoy Gateway",
      "basis": "v1.9.1",
      "sources": {
        "s49ae1b1ab1b5": "https://gateway.envoyproxy.io/docs/install/install-helm/",
        "s6412abbdfdbd": "https://github.com/envoyproxy/gateway/releases/download/v1.9.1/quickstart.yaml",
        "se833317feea7": "https://gateway.envoyproxy.io/docs/tasks/security/secure-gateways/",
        "s9b1d646cb718": "https://gateway.envoyproxy.io/docs/tasks/traffic/http-redirect/",
        "sb5fa4f4ffa1a": "https://gateway.envoyproxy.io/docs/tasks/security/basic-auth/",
        "s7fdd76c5d549": "https://gateway.envoyproxy.io/docs/tasks/security/oidc/",
        "s100049c74adf": "https://gateway.envoyproxy.io/docs/tasks/security/ext-auth/",
        "s45e142abcd62": "https://gateway.envoyproxy.io/docs/tasks/quickstart/"
      }
    },
    "gateway": {
      "name": "Gateway API documentation",
      "basis": "unknown",
      "sources": {
        "se0e45c61dc65": "https://gateway-api.sigs.k8s.io/guides/getting-started/introduction/",
        "se1f28d98d168": "https://gateway-api.sigs.k8s.io/guides/user-guides/tls/",
        "s4a971425e1d1": "https://gateway-api.sigs.k8s.io/guides/user-guides/http-routing/",
        "s8d02fbc742ba": "https://gateway-api.sigs.k8s.io/guides/user-guides/http-redirect-rewrite/"
      }
    },
    "cert-manager": {
      "name": "cert-manager Gateway support minimum",
      "basis": "1.15",
      "sources": {
        "s72bdb97928a8": "https://cert-manager.io/docs/usage/gateway/",
        "s8d82244c2d6d": "https://cert-manager.io/docs/configuration/acme/http01/"
      }
    },
    "apache": {
      "name": "Apache htpasswd documentation",
      "basis": "unknown",
      "sources": {
        "scde9004bb967": "https://httpd.apache.org/docs/2.4/programs/htpasswd.html"
      }
    },
    "authelia": {
      "name": "Authelia documentation",
      "basis": "unknown",
      "sources": {
        "s0cb4f49871b5": "https://www.authelia.com/integration/proxies/introduction/",
        "scfa9e2cc2ef5": "https://www.authelia.com/integration/kubernetes/envoy/gateway/"
      }
    },
    "eks": {
      "name": "Amazon EKS documentation",
      "basis": "unknown",
      "sources": {
        "s9724ce882930": "https://docs.aws.amazon.com/eks/latest/userguide/cluster-endpoint.html"
      }
    },
    "eks-ami": {
      "name": "Amazon EKS AMI bootstrap",
      "basis": "6caf8311a3c6a8da71ac7e5e83f9c2e06287039a",
      "sources": {
        "sbe1fce93c7b2": "https://github.com/awslabs/amazon-eks-ami/blob/6caf8311a3c6a8da71ac7e5e83f9c2e06287039a/nodeadm/internal/kubelet/config.go"
      }
    },
    "gke": {
      "name": "GKE documentation",
      "basis": "unknown",
      "sources": {
        "s0f44d89575ed": "https://docs.cloud.google.com/kubernetes-engine/docs/concepts/network-isolation#how_authorized_networks_work"
      }
    },
    "gke-min": {
      "name": "GKE new-cluster read-only-port boundary",
      "basis": "1.32",
      "sources": {
        "s4c7be4adcab4": "https://docs.cloud.google.com/kubernetes-engine/docs/how-to/disable-kubelet-readonly-port"
      }
    },
    "aks": {
      "name": "AKS documentation",
      "basis": "unknown",
      "sources": {
        "s897dd27ab9a1": "https://learn.microsoft.com/en-us/azure/aks/api-server-authorized-ip-ranges"
      }
    },
    "curl": {
      "name": "curl documentation",
      "basis": "unknown",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html",
        "s7d4a6e627b1b": "https://curl.se/libcurl/c/libcurl-errors.html"
      }
    },
    "nmap": {
      "name": "Nmap documentation",
      "basis": "unknown",
      "sources": {
        "sb7d0e7eb5141": "https://nmap.org/book/man-host-discovery.html",
        "s1818abeb3f92": "https://nmap.org/book/man-port-specification.html",
        "s79c95712dd8d": "https://nmap.org/book/man-misc-options.html"
      }
    },
    "traefik": {
      "name": "Traefik documentation",
      "basis": "unknown",
      "sources": {
        "s06f2ee45331e": "https://doc.traefik.io/traefik/reference/install-configuration/providers/kubernetes/kubernetes-gateway/"
      }
    },
    "cilium": {
      "name": "Cilium documentation",
      "basis": "unknown",
      "sources": {
        "sacaa7a78461d": "https://docs.cilium.io/en/stable/network/servicemesh/gateway-api/gateway-api/"
      }
    }
  },
  "claims": {
    "ingress-migration": {"text": "ingress-nginx retired in March 2026 with no subsequent updates; detect its labeled pods and migrate. Gateway API is recommended and Ingress API is frozen.", "components": ["kubernetes"], "sources": ["kubernetes:s0f11d6ed39b7", "kubernetes:sca23283c5a9b", "kubernetes:sd8c8df3b9ddc"], "status": "REASONED"},
    "gateway-install": {"text": "Install Envoy Gateway chart v1.9.1 and its default Gateway CRDs; separately create GatewayClass eg with the documented controllerName and confirm Accepted=True.", "components": ["envoy", "gateway"], "sources": ["envoy:s49ae1b1ab1b5", "envoy:s6412abbdfdbd", "gateway:se0e45c61dc65"], "status": "REASONED"},
    "gateway-alternatives": {"text": "Traefik uses providers.kubernetesGateway; Cilium uses gatewayAPI.enabled=true and requires kube-proxy replacement.", "components": ["traefik", "cilium"], "sources": ["traefik:s06f2ee45331e", "cilium:sacaa7a78461d"], "status": "REASONED"},
    "gateway-tls": {"text": "Gateway HTTPS listener 443 terminates TLS using app-tls for app.example.com; HTTP 80 is for redirect and ACME challenges.", "components": ["gateway", "envoy"], "sources": ["gateway:se1f28d98d168", "envoy:se833317feea7"], "status": "REASONED"},
    "gateway-route": {"text": "HTTPRoute app attaches only to the HTTPS listener via sectionName and forwards to the ClusterIP app Service on port 80.", "components": ["gateway"], "sources": ["gateway:s4a971425e1d1"], "status": "REASONED"},
    "gateway-redirect": {"text": "The HTTP route uses RequestRedirect with scheme https and statusCode 301.", "components": ["gateway", "envoy"], "sources": ["gateway:s8d02fbc742ba", "envoy:s9b1d646cb718"], "status": "REASONED"},
    "cert-manager-enable": {"text": "From cert-manager 1.15, enable config.gatewayAPI.enabled; install Gateway CRDs before startup or restart cert-manager afterwards.", "components": ["cert-manager"], "sources": ["cert-manager:s72bdb97928a8"], "status": "REASONED"},
    "cert-manager-issue": {"text": "Gateway issuer annotations produce Certificates per HTTPS-listener Secret using listener hostnames; ACME gatewayHTTPRoute parentRefs selects the challenge Gateway.", "components": ["cert-manager"], "sources": ["cert-manager:s72bdb97928a8", "cert-manager:s8d82244c2d6d"], "status": "REASONED"},
    "basic-auth-policy": {"text": "Gateway API has no standard auth filter; Envoy SecurityPolicy attaches Basic auth to Gateway/HTTPRoute/GRPCRoute using an htpasswd Secret.", "components": ["gateway", "envoy"], "sources": ["gateway:s4a971425e1d1", "envoy:sb5fa4f4ffa1a"], "status": "REASONED"},
    "basic-auth-hash": {"text": "Envoy supports SHA hashes only; htpasswd -s is weak SHA-1, so use long random passwords over TLS and keep application login.", "components": ["envoy", "apache"], "sources": ["envoy:sb5fa4f4ffa1a", "apache:scde9004bb967"], "status": "REASONED"},
    "basic-auth-input": {"text": "htpasswd -i reads stdin, unlike argv-exposing -b; confirm twice, create with -cis, verify with -vi and only then create the Kubernetes Secret.", "components": ["apache", "envoy"], "sources": ["apache:scde9004bb967", "envoy:sb5fa4f4ffa1a"], "status": "REASONED"},
    "oidc": {"text": "Envoy SecurityPolicy oidc uses issuer, clientID, clientSecret and redirectURL; enforce MFA at the identity provider.", "components": ["envoy"], "sources": ["envoy:s7fdd76c5d549"], "status": "REASONED"},
    "external-auth": {"text": "Authelia is an authorization endpoint, not a traffic proxy; Envoy extAuth.http targets its Service and /api/authz/ext-authz/.", "components": ["authelia", "envoy"], "sources": ["authelia:s0cb4f49871b5", "authelia:scfa9e2cc2ef5", "envoy:s100049c74adf"], "status": "REASONED"},
    "workload-exposure": {"text": "Expose workloads only through the Gateway LoadBalancer; keep databases on ClusterIP without routes and enforce pod access with NetworkPolicies plus database TLS/auth.", "components": ["envoy", "kubernetes"], "sources": ["envoy:s45e142abcd62", "kubernetes:sca23283c5a9b"], "status": "REASONED"},
    "secrets": {"text": "Store credentials in Secrets or an external operator, not committed ConfigMaps or environment literals; kubeconfigs containing credentials also need secret handling.", "components": ["kubernetes"], "sources": ["kubernetes:se41a53ea6778", "kubernetes:sae633285120e"], "status": "REASONED"},
    "eks-endpoint": {"text": "EKS API defaults public; restrict public CIDRs or use private access. Private-only endpoints can resolve publicly to private VPC addresses.", "components": ["eks"], "sources": ["eks:s9724ce882930"], "status": "REASONED"},
    "gke-endpoints": {"text": "GKE authorized networks constrain IP-based access, not its separately IAM-gated DNS endpoint; inspect both and disable unused DNS access.", "components": ["gke"], "sources": ["gke:s0f44d89575ed"], "status": "REASONED"},
    "aks-endpoint": {"text": "Restrict AKS API access with authorized IP ranges; workload Gateway protection does not secure the control plane.", "components": ["aks"], "sources": ["aks:s897dd27ab9a1"], "status": "REASONED"},
    "kubeconfig": {"text": "Embedded tokens or client keys confer their RBAC access without another factor; exec-plugin configs may be only pointers, but args/env can themselves hold credentials.", "components": ["kubernetes"], "sources": ["kubernetes:se41a53ea6778"], "status": "REASONED"},
    "api-port": {"text": "API server commonly uses 6443, but providers may use 443; use the complete kubeconfig endpoint and its actual port.", "components": ["kubernetes", "eks"], "sources": ["kubernetes:sd59fb2f35cd7", "eks:s9724ce882930"], "status": "REASONED"},
    "etcd-ports": {"text": "etcd client/peer defaults are 2379/2380; require certificates, restrict holders and private access, and retain loopback listeners used by the local API server.", "components": ["kubernetes"], "sources": ["kubernetes:sd59fb2f35cd7", "kubernetes:s01f081fed0ff"], "status": "REASONED"},
    "etcd-storage": {"text": "API resources default to plaintext storage in etcd; valid client certificates are the boundary and etcd access is equivalent to cluster root.", "components": ["kubernetes"], "sources": ["kubernetes:sae633285120e", "kubernetes:s01f081fed0ff"], "status": "REASONED"},
    "scheduler-port": {"text": "Scheduler default 10259 must remain restricted to cluster clients.", "components": ["kubernetes"], "sources": ["kubernetes:sd59fb2f35cd7"], "status": "REASONED"},
    "controller-port": {"text": "Controller-manager default 10257 must remain restricted to cluster clients.", "components": ["kubernetes"], "sources": ["kubernetes:sd59fb2f35cd7"], "status": "REASONED"},
    "proxy-port": {"text": "Worker kube-proxy health default 10256 needs separate node exposure checks.", "components": ["kubernetes"], "sources": ["kubernetes:sd59fb2f35cd7"], "status": "REASONED"},
    "nodeports": {"text": "NodePort defaults span 30000 to 32767 TCP/UDP; Service listings do not actively probe that range.", "components": ["kubernetes"], "sources": ["kubernetes:sd59fb2f35cd7"], "status": "REASONED"},
    "kubelet-legacy-anonymous": {"text": "Legacy kubelet flags default anonymous-auth=true; explicitly disable it where flags control authentication.", "components": ["kubelet"], "sources": ["kubelet:sc6056d6413a0", "kubelet:s227d2a259fd3"], "status": "REASONED"},
    "kubelet-legacy-webhook": {"text": "Legacy authentication-token-webhook defaults false; explicitly enable it where flags configure authentication.", "components": ["kubelet"], "sources": ["kubelet:sc6056d6413a0"], "status": "REASONED"},
    "kubelet-legacy-authz": {"text": "Legacy authorization-mode defaults AlwaysAllow; set Webhook where flags configure authorization.", "components": ["kubelet", "kubernetes"], "sources": ["kubelet:sc6056d6413a0", "kubernetes:s49a29258961b"], "status": "REASONED"},
    "kubelet-file-anonymous": {"text": "v1beta1 KubeletConfiguration instead defaults authentication.anonymous.enabled=false.", "components": ["kubelet"], "sources": ["kubelet:s568cd52cc674"], "status": "REASONED"},
    "kubelet-file-webhook": {"text": "v1beta1 KubeletConfiguration defaults authentication.webhook.enabled=true.", "components": ["kubelet"], "sources": ["kubelet:s568cd52cc674"], "status": "REASONED"},
    "kubelet-file-authz": {"text": "v1beta1 KubeletConfiguration defaults authorization.mode=Webhook.", "components": ["kubelet"], "sources": ["kubelet:s568cd52cc674"], "status": "REASONED"},
    "kubelet-precedence": {"text": "Explicit flags override --config; --config-dir drop-ins override defaults and the file. Inspect all effective settings together.", "components": ["kubelet"], "sources": ["kubelet:s2daf96dabbdf", "kubelet:s24ba323c3dab"], "status": "REASONED"},
    "kubeadm": {"text": "kubeadm sets anonymous false, token webhook true, Webhook authorization and readOnlyPort 0; user overrides are preserved with warnings.", "components": ["kubelet"], "sources": ["kubelet:sd81692a1876f", "kubelet:s0eb30acf2f46", "kubelet:s1c86aaef7307", "kubelet:sb98bd327db92"], "status": "REASONED"},
    "eks-bootstrap": {"text": "The pinned EKS AMI bootstrap writes Anonymous.Enabled=false, Mode=Webhook and ReadOnlyPort=0; do not generalize to all managed nodes.", "components": ["eks-ami"], "sources": ["eks-ami:sbe1fce93c7b2"], "status": "REASONED"},
    "kubelet-bind": {"text": "Secured kubelet defaults to address 0.0.0.0 on 10250; wildcard help includes both families. Bind private addresses and restrict authorized callers.", "components": ["kubelet"], "sources": ["kubelet:s568cd52cc674", "kubelet:s3fc405855b4a", "kubelet:s227d2a259fd3", "kubelet:s98cf98130201"], "status": "REASONED"},
    "kubelet-exec": {"text": "10250 debugging handlers can execute in containers; authentication does not justify public reachability.", "components": ["kubelet"], "sources": ["kubelet:s8bea69523ed9", "kubelet:s3fc405855b4a", "kubelet:s98cf98130201", "kubelet:s02441dcae3cf"], "status": "REASONED"},
    "readonly-default": {"text": "Legacy read-only port defaults 10255, while v1beta1 readOnlyPort defaults 0; explicitly disable it and remove enabling overrides.", "components": ["kubelet"], "sources": ["kubelet:sc6056d6413a0", "kubelet:sa02a895a475c", "kubelet:s3fc405855b4a"], "status": "REASONED"},
    "readonly-auth": {"text": "Read-only server uses plain HTTP with no authentication or authorization filter; its caller-supplied bind wiring was outside the inspected source subset.", "components": ["kubelet"], "sources": ["kubelet:s98cf98130201", "kubelet:s8bea69523ed9"], "status": "REASONED"},
    "readonly-paths": {"text": "Read-only handlers expose /pods, /stats/summary, metrics variants and health; v1.37.1 has no /spec handler. Securing 10250 does not secure 10255.", "components": ["kubelet"], "sources": ["kubelet:s6b753b247f8a", "kubelet:sd00d4cdb9276"], "status": "REASONED"},
    "gke-readonly": {"text": "GKE disables the read-only port by default only for new clusters running 1.32+; inspect effective configuration on older or upgraded clusters.", "components": ["gke-min"], "sources": ["gke-min:s4c7be4adcab4"], "status": "REASONED"},
    "verify-services": {"text": "Only the Gateway should have NodePort/LoadBalancer exposure; verify its public address/DNS and Certificate Ready=True.", "components": ["kubernetes", "envoy", "cert-manager"], "sources": ["kubernetes:s04f0c3099fd7", "envoy:s45e142abcd62", "cert-manager:s72bdb97928a8"], "status": "REASONED", "verify": [1]},
    "verify-redirect": {"text": "HTTP should return 301 to the HTTPS application URL.", "components": ["gateway"], "sources": ["gateway:s8d02fbc742ba"], "status": "REASONED", "verify": [1]},
    "verify-basic": {"text": "Anonymous Basic-protected access should return 401; require SecurityPolicy Accepted=True and a valid credential reaching the app without the gateway Basic challenge.", "components": ["envoy", "curl"], "sources": ["envoy:sb5fa4f4ffa1a", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-api-target": {"text": "Use the whole kubeconfig endpoint, preserving IPv6 and inferring a schemeless endpoint from both cluster and user TLS settings, not a hardcoded 6443.", "components": ["kubernetes"], "sources": ["kubernetes:se41a53ea6778", "kubernetes:sd59fb2f35cd7"], "status": "REASONED", "verify": [1]},
    "verify-proxies": {"text": "Disable curl config and configured proxies for direct probes; a transparent TLS middlebox can still answer for an unreachable target.", "components": ["curl"], "sources": ["curl:s2b2686afaf41", "curl:s7d4a6e627b1b"], "status": "REASONED", "verify": [1]},
    "verify-api-tcp": {"text": "Outside allowed ranges, nc success proves something accepted TCP; corroborate failed probes with provider ranges and multiple vantage points.", "components": ["kubernetes", "eks"], "sources": ["kubernetes:sd59fb2f35cd7", "eks:s9724ce882930"], "status": "REASONED", "verify": [1]},
    "verify-api-http": {"text": "Any HTTP status with curl exit 0 means answered; exit 60 means a TLS peer answered, 7 failed connect, 28 is ambiguous timeout and 6 is DNS failure, not privacy proof.", "components": ["curl", "eks"], "sources": ["curl:s7d4a6e627b1b", "eks:s9724ce882930"], "status": "REASONED", "verify": [1]},
    "verify-node-scan": {"text": "Scan control-plane hosts first and every public node address in both families; workers alone miss API/etcd and separate etcd hosts are absent from kubectl nodes.", "components": ["kubernetes", "nmap"], "sources": ["kubernetes:sd59fb2f35cd7", "kubernetes:s01f081fed0ff", "nmap:sb7d0e7eb5141", "nmap:s1818abeb3f92", "nmap:s79c95712dd8d"], "status": "REASONED", "verify": [1]},
    "verify-kubelet": {"text": "Untrusted clients should reach neither kubelet port after isolation, while authorized clients still reach 10250; readOnlyPort=0 should leave no 10255 listener even for authorized clients.", "components": ["kubelet"], "sources": ["kubelet:s98cf98130201", "kubelet:s3fc405855b4a"], "status": "REASONED", "verify": [1]}
  }
}
---
# Kubernetes: Gateway API TLS and authentication

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| ingress-migration: ingress-nginx retired in March 2026 with no subsequent updates; detect its labeled pods and migrate. Gateway API is recommended and Ingress API is frozen. | Kubernetes documentation unknown | REASONED |
| gateway-install: Install Envoy Gateway chart v1.9.1 and its default Gateway CRDs; separately create GatewayClass eg with the documented controllerName and confirm Accepted=True. | Envoy Gateway v1.9.1; Gateway API documentation unknown | REASONED |
| gateway-alternatives: Traefik uses providers.kubernetesGateway; Cilium uses gatewayAPI.enabled=true and requires kube-proxy replacement. | Traefik documentation unknown; Cilium documentation unknown | REASONED |
| gateway-tls: Gateway HTTPS listener 443 terminates TLS using app-tls for app.example.com; HTTP 80 is for redirect and ACME challenges. | Gateway API documentation unknown; Envoy Gateway v1.9.1 | REASONED |
| gateway-route: HTTPRoute app attaches only to the HTTPS listener via sectionName and forwards to the ClusterIP app Service on port 80. | Gateway API documentation unknown | REASONED |
| gateway-redirect: The HTTP route uses RequestRedirect with scheme https and statusCode 301. | Gateway API documentation unknown; Envoy Gateway v1.9.1 | REASONED |
| cert-manager-enable: From cert-manager 1.15, enable config.gatewayAPI.enabled; install Gateway CRDs before startup or restart cert-manager afterwards. | cert-manager Gateway support minimum 1.15 | REASONED |
| cert-manager-issue: Gateway issuer annotations produce Certificates per HTTPS-listener Secret using listener hostnames; ACME gatewayHTTPRoute parentRefs selects the challenge Gateway. | cert-manager Gateway support minimum 1.15 | REASONED |
| basic-auth-policy: Gateway API has no standard auth filter; Envoy SecurityPolicy attaches Basic auth to Gateway/HTTPRoute/GRPCRoute using an htpasswd Secret. | Gateway API documentation unknown; Envoy Gateway v1.9.1 | REASONED |
| basic-auth-hash: Envoy supports SHA hashes only; htpasswd -s is weak SHA-1, so use long random passwords over TLS and keep application login. | Envoy Gateway v1.9.1; Apache htpasswd documentation unknown | REASONED |
| basic-auth-input: htpasswd -i reads stdin, unlike argv-exposing -b; confirm twice, create with -cis, verify with -vi and only then create the Kubernetes Secret. | Apache htpasswd documentation unknown; Envoy Gateway v1.9.1 | REASONED |
| oidc: Envoy SecurityPolicy oidc uses issuer, clientID, clientSecret and redirectURL; enforce MFA at the identity provider. | Envoy Gateway v1.9.1 | REASONED |
| external-auth: Authelia is an authorization endpoint, not a traffic proxy; Envoy extAuth.http targets its Service and /api/authz/ext-authz/. | Authelia documentation unknown; Envoy Gateway v1.9.1 | REASONED |
| workload-exposure: Expose workloads only through the Gateway LoadBalancer; keep databases on ClusterIP without routes and enforce pod access with NetworkPolicies plus database TLS/auth. | Envoy Gateway v1.9.1; Kubernetes documentation unknown | REASONED |
| secrets: Store credentials in Secrets or an external operator, not committed ConfigMaps or environment literals; kubeconfigs containing credentials also need secret handling. | Kubernetes documentation unknown | REASONED |
| eks-endpoint: EKS API defaults public; restrict public CIDRs or use private access. Private-only endpoints can resolve publicly to private VPC addresses. | Amazon EKS documentation unknown | REASONED |
| gke-endpoints: GKE authorized networks constrain IP-based access, not its separately IAM-gated DNS endpoint; inspect both and disable unused DNS access. | GKE documentation unknown | REASONED |
| aks-endpoint: Restrict AKS API access with authorized IP ranges; workload Gateway protection does not secure the control plane. | AKS documentation unknown | REASONED |
| kubeconfig: Embedded tokens or client keys confer their RBAC access without another factor; exec-plugin configs may be only pointers, but args/env can themselves hold credentials. | Kubernetes documentation unknown | REASONED |
| api-port: API server commonly uses 6443, but providers may use 443; use the complete kubeconfig endpoint and its actual port. | Kubernetes documentation unknown; Amazon EKS documentation unknown | REASONED |
| etcd-ports: etcd client/peer defaults are 2379/2380; require certificates, restrict holders and private access, and retain loopback listeners used by the local API server. | Kubernetes documentation unknown | REASONED |
| etcd-storage: API resources default to plaintext storage in etcd; valid client certificates are the boundary and etcd access is equivalent to cluster root. | Kubernetes documentation unknown | REASONED |
| scheduler-port: Scheduler default 10259 must remain restricted to cluster clients. | Kubernetes documentation unknown | REASONED |
| controller-port: Controller-manager default 10257 must remain restricted to cluster clients. | Kubernetes documentation unknown | REASONED |
| proxy-port: Worker kube-proxy health default 10256 needs separate node exposure checks. | Kubernetes documentation unknown | REASONED |
| nodeports: NodePort defaults span 30000 to 32767 TCP/UDP; Service listings do not actively probe that range. | Kubernetes documentation unknown | REASONED |
| kubelet-legacy-anonymous: Legacy kubelet flags default anonymous-auth=true; explicitly disable it where flags control authentication. | Kubernetes kubelet/kubeadm source v1.37.1 | REASONED |
| kubelet-legacy-webhook: Legacy authentication-token-webhook defaults false; explicitly enable it where flags configure authentication. | Kubernetes kubelet/kubeadm source v1.37.1 | REASONED |
| kubelet-legacy-authz: Legacy authorization-mode defaults AlwaysAllow; set Webhook where flags configure authorization. | Kubernetes kubelet/kubeadm source v1.37.1; Kubernetes documentation unknown | REASONED |
| kubelet-file-anonymous: v1beta1 KubeletConfiguration instead defaults authentication.anonymous.enabled=false. | Kubernetes kubelet/kubeadm source v1.37.1 | REASONED |
| kubelet-file-webhook: v1beta1 KubeletConfiguration defaults authentication.webhook.enabled=true. | Kubernetes kubelet/kubeadm source v1.37.1 | REASONED |
| kubelet-file-authz: v1beta1 KubeletConfiguration defaults authorization.mode=Webhook. | Kubernetes kubelet/kubeadm source v1.37.1 | REASONED |
| kubelet-precedence: Explicit flags override --config; --config-dir drop-ins override defaults and the file. Inspect all effective settings together. | Kubernetes kubelet/kubeadm source v1.37.1 | REASONED |
| kubeadm: kubeadm sets anonymous false, token webhook true, Webhook authorization and readOnlyPort 0; user overrides are preserved with warnings. | Kubernetes kubelet/kubeadm source v1.37.1 | REASONED |
| eks-bootstrap: The pinned EKS AMI bootstrap writes Anonymous.Enabled=false, Mode=Webhook and ReadOnlyPort=0; do not generalize to all managed nodes. | Amazon EKS AMI bootstrap 6caf8311a3c6a8da71ac7e5e83f9c2e06287039a | REASONED |
| kubelet-bind: Secured kubelet defaults to address 0.0.0.0 on 10250; wildcard help includes both families. Bind private addresses and restrict authorized callers. | Kubernetes kubelet/kubeadm source v1.37.1 | REASONED |
| kubelet-exec: 10250 debugging handlers can execute in containers; authentication does not justify public reachability. | Kubernetes kubelet/kubeadm source v1.37.1 | REASONED |
| readonly-default: Legacy read-only port defaults 10255, while v1beta1 readOnlyPort defaults 0; explicitly disable it and remove enabling overrides. | Kubernetes kubelet/kubeadm source v1.37.1 | REASONED |
| readonly-auth: Read-only server uses plain HTTP with no authentication or authorization filter; its caller-supplied bind wiring was outside the inspected source subset. | Kubernetes kubelet/kubeadm source v1.37.1 | REASONED |
| readonly-paths: Read-only handlers expose /pods, /stats/summary, metrics variants and health; v1.37.1 has no /spec handler. Securing 10250 does not secure 10255. | Kubernetes kubelet/kubeadm source v1.37.1 | REASONED |
| gke-readonly: GKE disables the read-only port by default only for new clusters running 1.32+; inspect effective configuration on older or upgraded clusters. | GKE new-cluster read-only-port boundary 1.32 | REASONED |
| verify-services: Only the Gateway should have NodePort/LoadBalancer exposure; verify its public address/DNS and Certificate Ready=True. | Kubernetes documentation unknown; Envoy Gateway v1.9.1; cert-manager Gateway support minimum 1.15 | REASONED |
| verify-redirect: HTTP should return 301 to the HTTPS application URL. | Gateway API documentation unknown | REASONED |
| verify-basic: Anonymous Basic-protected access should return 401; require SecurityPolicy Accepted=True and a valid credential reaching the app without the gateway Basic challenge. | Envoy Gateway v1.9.1; curl documentation unknown | REASONED |
| verify-api-target: Use the whole kubeconfig endpoint, preserving IPv6 and inferring a schemeless endpoint from both cluster and user TLS settings, not a hardcoded 6443. | Kubernetes documentation unknown | REASONED |
| verify-proxies: Disable curl config and configured proxies for direct probes; a transparent TLS middlebox can still answer for an unreachable target. | curl documentation unknown | REASONED |
| verify-api-tcp: Outside allowed ranges, nc success proves something accepted TCP; corroborate failed probes with provider ranges and multiple vantage points. | Kubernetes documentation unknown; Amazon EKS documentation unknown | REASONED |
| verify-api-http: Any HTTP status with curl exit 0 means answered; exit 60 means a TLS peer answered, 7 failed connect, 28 is ambiguous timeout and 6 is DNS failure, not privacy proof. | curl documentation unknown; Amazon EKS documentation unknown | REASONED |
| verify-node-scan: Scan control-plane hosts first and every public node address in both families; workers alone miss API/etcd and separate etcd hosts are absent from kubectl nodes. | Kubernetes documentation unknown; Nmap documentation unknown | REASONED |
| verify-kubelet: Untrusted clients should reach neither kubelet port after isolation, while authorized clients still reach 10250; readOnlyPort=0 should leave no 10255 listener even for authorized clients. | Kubernetes kubelet/kubeadm source v1.37.1 | REASONED |
<!-- version-basis:end -->

The cluster equivalents of this repository's rules: nothing reaches a workload except through the TLS-terminating entry point (a Gateway API `Gateway`), and no Service becomes public through a casual `type: LoadBalancer` or `NodePort`; the entry point's own Service is the only exception.

**If you run ingress-nginx today, migrate.** Earlier versions of this guide built on ingress-nginx. The Kubernetes project retired it in March 2026: per the Kubernetes Steering and Security Response Committees, "there will be no more releases for bug fixes, security patches, or any updates of any kind after the project is retired", and "choosing to remain with Ingress NGINX after its retirement leaves you and your users vulnerable to attack" (as of September 2026; statement linked in Sources). Detect it with cluster-admin permissions: `kubectl get pods --all-namespaces --selector app.kubernetes.io/name=ingress-nginx`. Any pod returned means migration is required; the `nginx.ingress.kubernetes.io/*` annotations die with the controller. Kubernetes recommends Gateway API over Ingress (whose API is now frozen) and links a migration guide from its Gateway API page. The rest of this guide is the Gateway API form of the old rules.

## 1. Gateway API with a maintained implementation

Gateway API is a set of CRDs, not part of core Kubernetes; a controller you install implements them. This guide uses [Envoy Gateway](https://gateway.envoyproxy.io/): `helm install eg oci://docker.io/envoyproxy/gateway-helm --version v1.9.1 -n envoy-gateway-system --create-namespace` (version current at the time of writing; the default chart also installs the Gateway API CRDs). The chart does not create a `GatewayClass`; the quickstart applies one separately, and the `Gateway` below refers to it by name, so apply it first and confirm that the controller accepted it:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: eg
spec:
  controllerName: gateway.envoyproxy.io/gatewayclass-controller
```

```bash
kubectl get gatewayclass eg -o jsonpath='{.status.conditions[?(@.type=="Accepted")].status}'   # True
```

Traefik's Gateway API provider (`providers.kubernetesGateway`) and Cilium (`gatewayAPI.enabled=true`, requires kube-proxy replacement) are maintained alternatives, linked in Sources. The `Gateway` is the entry point; keep its HTTP listener only for redirects and ACME challenges:

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: eg
  annotations: { cert-manager.io/cluster-issuer: letsencrypt }   # section 2
spec:
  gatewayClassName: eg
  listeners:
    - { name: http, protocol: HTTP, port: 80 }
    - name: https
      protocol: HTTPS
      port: 443
      hostname: app.example.com
      tls: { mode: Terminate, certificateRefs: [{ kind: Secret, name: app-tls }] }
```

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata: { name: app }
spec:
  parentRefs: [{ name: eg, sectionName: https }]        # sectionName binds the route to one listener
  hostnames: [app.example.com]
  rules: [{ backendRefs: [{ name: app, port: 80 }] }]   # a ClusterIP Service
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata: { name: app-redirect }
spec:
  parentRefs: [{ name: eg, sectionName: http }]
  hostnames: [app.example.com]
  rules: [{ filters: [{ type: RequestRedirect, requestRedirect: { scheme: https, statusCode: 301 } }] }]
```

## 2. Automatic certificates with cert-manager

Install [cert-manager](https://cert-manager.io/docs/) with Gateway API support turned on: `--set config.gatewayAPI.enabled=true` on its Helm chart (cert-manager 1.15 and later per its docs; the Gateway API CRDs must exist before cert-manager starts, or restart its Deployment afterwards). Define an ACME issuer once, with the HTTP-01 solver pointed at the Gateway (adjust `namespace` to where the Gateway lives). The `cert-manager.io/cluster-issuer` (or `cert-manager.io/issuer`) annotation goes on the Gateway, not on routes: cert-manager creates one Certificate per Secret named in the HTTPS listeners, with `dnsNames` taken from each listener's `hostname`, issues into `app-tls`, and renews it.

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata: { name: letsencrypt }
spec:
  acme:
    email: admin@example.com
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef: { name: letsencrypt-account }
    solvers:
      - http01:
          gatewayHTTPRoute: { parentRefs: [{ name: eg, namespace: default, kind: Gateway }] }
```

## 3. Authentication at the entry point

Gateway API defines no authentication filter; each implementation adds its own. Envoy Gateway's `SecurityPolicy` attaches basic auth to a Gateway, HTTPRoute, or GRPCRoute from a Secret holding an htpasswd file. Its docs state that only SHA hashes are supported, which falls short of the bcrypt rule in [authentication.md](authentication.md): treat it as a gate over TLS with long random passwords, and keep the application's own login in place.

```bash
# -b would take the password from the command line, where `ps` and your shell history can
# read it. Apache's own page says of it: "This option should be used with extreme care,
# since the password is clearly visible on the command line. For script use see the -i
# option." -i reads it from stdin instead. Envoy Gateway's example uses -b; this does not.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell (CONTRIBUTING rule 7): no inherited DEBUG trap, extdebug, function or alias
  set +x +a +e
  { unset -n PASSWORD confirm && unset -v PASSWORD confirm; } 2>/dev/null ||
    { echo 'cannot clear PASSWORD or confirm in this shell; not creating the secret'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not creating the secret'; exit 2; }
  IFS= read -r -s -p 'basic auth password: ' PASSWORD < /dev/tty || exit 2
  echo
  IFS= read -r -s -p 'again, to confirm: ' confirm < /dev/tty || exit 2
  echo
  [ -n "$PASSWORD" ] || { echo 'no password supplied; not creating the secret'; exit 2; }
  [ "$PASSWORD" = "$confirm" ] || { echo 'the two entries differ; not creating the secret'; exit 2; }
  set -o pipefail  # so a failure anywhere in a pipeline below, not only in htpasswd, fails it
  printf '%s' "$PASSWORD" | htpasswd -cis .htpasswd admin ||
    { echo 'password-file creation failed; not creating the secret'; exit 2; }
  # -i does no verification, so the block asks twice and refuses a mismatch; `-vi` below then
  # confirms the file holds that value, and the secret is created only if it does. Paste the block by
  # itself: the shell reads the whole subshell before either `read` runs. Without bracketed paste,
  # lines pasted after the closing `)` feed the two prompts instead, and the block refuses unless both
  # are identical; with bracketed paste, they run as commands once the block finishes.
  printf '%s' "$PASSWORD" | htpasswd -vi .htpasswd admin ||
    { echo 'htpasswd could not verify the file; not creating the secret'; exit 2; }
  kubectl create secret generic app-basic-auth --from-file=.htpasswd
)
```

`-s` is SHA-1, which Apache describes as "insecure by today's standards", and it is not a
choice here: Envoy Gateway's basic auth documentation says "only SHA hash algorithm is
supported for now", so `-B` for bcrypt produces a file it cannot read. Treat this credential
accordingly. It is a single shared secret protecting an entry point, it is only as strong as
its own length, and a long random value is doing all of the work. Where that is not enough,
the `oidc` block below moves the decision to an identity provider instead.

```yaml
apiVersion: gateway.envoyproxy.io/v1alpha1
kind: SecurityPolicy
metadata: { name: app-basic-auth }
spec:
  targetRefs: [{ group: gateway.networking.k8s.io, kind: HTTPRoute, name: app }]
  basicAuth: { users: { name: app-basic-auth } }
```

For SSO, the same `SecurityPolicy` takes an `oidc` block (`provider.issuer`, `clientID`, a `clientSecret` Secret, `redirectURL`) so Envoy Gateway sends users to an OpenID Connect provider; enforce MFA at that provider ([mfa.md](mfa.md), [identity-providers.md](identity-providers.md)). The portable alternative for any Gateway implementation is oauth2-proxy deployed in the cluster as the route's backend in front of the app, per [mfa.md](mfa.md). Authelia does not proxy traffic; the proxy calls its authorization endpoint, so it needs an implementation with external authorization. On Envoy Gateway the same `SecurityPolicy` takes an `extAuth.http` block whose `backendRefs` point at the Authelia Service and whose `path` is `/api/authz/ext-authz/`, per Authelia's Envoy Gateway page. Publishing through [cloudflare.md](cloudflare.md) is the other option.

## 4. Cluster posture

- Expose workloads through the Gateway only; the Service Envoy Gateway creates for it in `envoy-gateway-system` is the one `LoadBalancer` in the cluster.
- Databases stay `type: ClusterIP` (the default) and never get a route; NetworkPolicies limit which pods reach them, and their guides' TLS and auth still apply inside the cluster ([postgresql.md](postgresql.md), [mysql.md](mysql.md), [redis.md](redis.md), [mongodb.md](mongodb.md)).
- Store credentials in Secrets (or an external secrets operator), not ConfigMaps or env literals in manifests committed to git ([secrets.md](secrets.md)).

## 5. The control plane is a separate exposure

Sections 1 to 4 cover how traffic reaches your workloads. None of it touches the cluster's own
management surface, and a reader can apply every one of them while the API server answers the whole
internet.

**Managed clusters start public.** AWS documents that "[b]y default, this API server endpoint is public
to the internet" for EKS. Restrict it: EKS supports private endpoint access and CIDR restrictions on the
public one, GKE calls the same control "authorized networks", and AKS calls it authorized IP ranges.
Whichever you run, the question to answer is which addresses can reach the API server, and the default
answer is everyone. GKE needs a second look, because it has two control-plane endpoints and authorized
networks only govern one. The vendor says authorized networks "provide an IP-based firewall that
controls access to the GKE control plane", and that reaching the DNS-based endpoint is a different
question entirely: "To access the control plane endpoint, you need to configure IAM roles and policies,
and authentication tokens." So a GKE reader who restricts authorized networks exactly as this section
says, and then probes the address in their kubeconfig, can still have a DNS-based endpoint answering
from anywhere, gated by IAM alone. Check both, and if you do not use the DNS-based endpoint, disable it
rather than leaving it to IAM.

**A kubeconfig may be a credential, or only a pointer to one.** A file with an embedded token, or with
a client certificate and its key, is the credential: anyone holding it has whatever it is bound to, with
no second factor. A file that names an exec credential plugin is usually not, because the plugin fetches
a fresh token when it runs, which is how EKS works with `aws eks get-token`, and copying it without the
provider credentials the plugin depends on confers nothing. Usually, not always: the exec block carries
`args` and `env`, and Kubernetes documents `env` as defining "additional environment variables to expose
to the process", so a plugin can be handed its own credentials right there in the file. Read the whole
block before you decide it is only a pointer. Open yours and find out which kind it is before you decide
how to handle it. Treat the credential-bearing kind as a secret ([secrets.md](secrets.md)), scope every
kubeconfig with RBAC rather than handing out cluster-admin, and prefer the plugin form.

**Self-managed clusters expose more ports.** Kubernetes documents the control plane's inbound ports as
6443 for the API server, 2379 and 2380 for etcd, 10250 for the kubelet API, 10259 for the scheduler and
10257 for the controller manager. Worker nodes have their own inbound list on the same page: 10250
again for the kubelet API, 10256 for kube-proxy health, and the NodePort range 30000 to 32767 over
TCP and UDP. These are defaults, not fixtures. The same page notes that "One common
example is API server port that is sometimes switched to 443", which is the port the managed providers
serve on, so read the port out of your own kubeconfig rather than assuming 6443. Only the API server has
any business being reachable beyond the cluster, and only from addresses you list. Kubernetes states that
"By default, the API server stores plain-text representations of resources into etcd, with no at-rest
encryption", so what is on that disk is every Secret in the cluster in the clear. Reaching 2379 is not
the same as reading it, because Kubernetes' operating-etcd guide says "Once etcd is configured
correctly, only clients with valid certificates can access it"; the point is that the certificate is
the entire boundary, and there is no second one behind it. Kubernetes puts the consequence plainly:
"Access to etcd is equivalent to root permission in the cluster so ideally only the API server should
have access to it." Require client certificates on both the client and peer ports, and keep the client
listener off any public interface. Do not simply move it to the private address: kubeadm points the
API server at loopback, `127.0.0.1:2379` or `::1` depending on the address family it advertises, and
configures etcd to listen there as well as on the advertised address, so dropping the loopback
listener breaks the API server on that node. Keep whichever one your cluster configured rather than
the literal written here. Keep issuance narrow rather than absolute, because kubeadm issues an
`etcd-healthcheck-client` certificate of its own and backups need one too; the rule is that you should
be able to name every holder. A firewall rule in front of an etcd still listening on `0.0.0.0` is one
misconfiguration away from the same outcome.

**The kubelet's defaults depend on how it is configured.** At Kubernetes v1.37.1
(commit `f78e722310e50bcaca9276be22276d9e91d91308`), the legacy command-line defaults are
`--anonymous-auth=true`, `--authentication-token-webhook=false` and
`--authorization-mode=AlwaysAllow`. The v1beta1 `KubeletConfiguration` defaults instead are
`authentication.anonymous.enabled: false`, `authentication.webhook.enabled: true` and
`authorization.mode: Webhook`. These are defaults for omitted settings, not enforced policy.
An explicitly supplied command-line flag overrides the configuration file, as the pinned `--config`
help states, and drop-in files in a `--config-dir` directory override both the defaults and the `--config` file, as the pinned `--config-dir` help states. Read the configuration file, any drop-in directory and the node's actual startup arguments together. Where flags
configure these controls, set `--anonymous-auth=false`, `--authentication-token-webhook=true` and
`--authorization-mode=Webhook`. The authentication documentation in Sources explains the resulting
anonymous identity and webhook checks.

kubeadm's v1.37.1 `KubeletConfiguration` sets anonymous authentication to false, token webhook
authentication to true and authorization to `Webhook`, and leaves `readOnlyPort` at 0. Its source
warns when a user supplies different values for these controls; it preserves those overrides rather
than forcing the recommended values. A default kubeadm configuration therefore disables anonymous
access and the read-only service, but kubeadm's involvement alone does not prove a node is safe.
The separately pinned EKS AMI bootstrap cited below writes `Anonymous.Enabled: false`,
`Mode: "Webhook"` and `ReadOnlyPort: 0`; do not generalize that snapshot to every managed distribution.

**Both ports need a bind and network boundary.** The v1.37.1 default `address` is `0.0.0.0`,
with the secured API on port 10250. The read-only server takes a bind address from its caller;
that caller is outside the offline source subset, so its wiring to `address` was not verified here. The pinned `--address` help describes both `0.0.0.0` and `::` as listening on all interfaces
and IP address families. Do not interpret `0.0.0.0` as an IPv4-only restriction: IPv6 can be included
where the host supports dual-stack wildcard sockets. Bind `address` (or `--address`) to the node's
intended private address and restrict access to the control plane and other authorized cluster
clients. Check both address families. Port 10250 can expose container execution through its
debugging handlers, so authentication does not make public reachability appropriate.

**Disable the separate read-only service.** The command-line reference gives `--read-only-port`
a default of 10255; the pinned legacy-default code assigns `ports.KubeletReadOnlyPort`, which `pkg/cluster/ports/ports.go:37` sets to 10255. The v1beta1
`readOnlyPort` field defaults to 0 (disabled). Set `readOnlyPort: 0` in the configuration file or
`--read-only-port=0`, and remove any overriding startup flag that enables it. In v1.37.1 the
read-only server uses plain HTTP and installs no authentication or authorization filter.
It exposes `/pods` (pod specifications), `/stats/summary`, `/metrics`, `/metrics/cadvisor`,
`/metrics/resource`, `/metrics/probes` and health checks. This version has no `/spec` handler;
do not rely on historical endpoint lists. Securing 10250 does not secure 10255.

GKE's cited documentation says the read-only port is disabled by default in **new clusters running
1.32 or later**. That is not proof that every older cluster still has it enabled, or that an upgraded
cluster has it disabled. Check the provider's effective node configuration. The provider citations
are retained context; this offline source audit did not recheck their current contents.

## Verify

**REASONED, not demonstrated:** the live checks below need a cluster, which is unavailable;
the authoring host forbids opening listeners without an isolated network namespace, and has none.
The existing commands state the expected workload and API outcomes. For the node scans, an exposed
kubelet is expected to show 10250 open and, when enabled, 10255 open; after private binding and
network restrictions, neither should be reachable from an untrusted network, while an authorized
cluster client must still reach 10250. With `readOnlyPort: 0`, 10255 should have no kubelet listener
even from that authorized client. Check every configured address family and retain an authorized
positive control so an unavailable node is not mistaken for successful isolation. The pinned
listener/default sources below support these expectations; no live result is claimed.

```bash
# REASONED: workload, API and kubelet exposure checks follow the cited documentation and pinned listener sources;
# no Kubernetes cluster or isolated network namespace is available.
kubectl get svc -A | grep -E 'NodePort|LoadBalancer'                 # only the Gateway's Service
kubectl get gateway/eg -o jsonpath='{.status.addresses[0].value}'    # the public address; DNS points here
kubectl get certificate -A                                           # Ready=True
# App checks, run directly with client proxies disabled (the unset below only affects LATER commands).
curl -q --noproxy '*' -sI http://app.example.com/                       # 301 with Location: https://app.example.com/
curl -q --noproxy '*' -sS -o /dev/null -w 'http=%{http_code}\n' https://app.example.com/
                                                                        # no credentials: 401 where basic auth is set
# Positive control: confirm the SecurityPolicy attached, and that a valid basic-auth credential (from a
# mode-0600 ~/.netrc-style file, never argv) is ACCEPTED by the gateway - it reaches the app rather than
# drawing the gateway's basic-auth 401. The app's own login may then answer, so the test is that you NO
# LONGER get the gateway's 401 with `WWW-Authenticate: Basic`, not that `/` returns 2xx.
kubectl get securitypolicy app-basic-auth -o yaml   # an Accepted "True" condition under .status.ancestors (PolicyStatus)
curl -q --noproxy '*' -sS --netrc-file "$HOME/.secureconfig-app.netrc" -D - -o /dev/null https://app.example.com/

# The API server endpoint, taken WHOLE. Do not rebuild it with :6443. Managed providers
# serve the API on 443, and a probe of 6443 times out against a cluster that is answering
# the internet on 443, which reads as a pass.
API=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')
# Whether a schemeless server means HTTP or HTTPS is decided by the TLS settings in the
# same kubeconfig, on the cluster entry and the user entry both, so read those rather
# than guessing.
TLS=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.certificate-authority}{.clusters[0].cluster.certificate-authority-data}{.clusters[0].cluster.insecure-skip-tls-verify}{.users[0].user.client-certificate}{.users[0].user.client-certificate-data}')

# From a machine OUTSIDE any allowed range, against a cluster you are authorized to test.
# Neutralize the proxy settings, all of them. curl reads ALL_PROXY and all_proxy as well as
# the per-scheme variables, and it reads ~/.curlrc, which can also turn verification off.
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy ALL_PROXY all_proxy NO_PROXY no_proxy

# First at the TCP layer, because this is the only part with a clean answer. Did anything
# accept a connection?
PARSED=$(python3 - "$API" "$TLS" <<'PY'
import sys, urllib.parse
raw, tls = sys.argv[1].strip(), sys.argv[2].strip()
if "://" not in raw:
    # Kubernetes starts at http:// and moves to https:// only when the config carries a
    # CA or insecure-skip-tls-verify on the cluster entry, or a client certificate on the
    # user entry. Guessing https here sent the probe to 443 against a cluster the client
    # would reach on 80.
    raw = ("https://" if tls else "http://") + raw
p = urllib.parse.urlsplit(raw)
if not p.hostname:
    sys.exit("cannot parse an API server out of: " + sys.argv[1])
print(p.hostname, p.port or (80 if p.scheme == "http" else 443),
      p.scheme + "://" + p.netloc)
PY
) || { echo "could not read the API server endpoint; skipping the probe" >&2; PARSED=; }
if [ -n "$PARSED" ]; then
  read -r HOST PORT URL <<<"$PARSED"
  echo "$URL"
  nc -vz -w 3 "$HOST" "$PORT"
fi
# Parsed with python3 rather than cut with sed. A bracketed IPv6 address breaks on the
# colons, and the failure looks exactly like the clean drop you were hoping for.
# A bare host with no scheme is also legal in a kubeconfig, and the scheme it implies depends
# on the TLS settings beside it rather than on a convention, so those are read and the URL the
# probe uses is the normalized one. Getting that wrong sends both layers of this check at a
# port the cluster was never using, where a refusal proves nothing.
# A context with no user entry would make the TLS jsonpath error out; every real one names
# a user, and kubectl says so if yours does not.
# This step needs python3, nc and nmap on the machine you run it from, none of which the
# cluster provides for you.
# "succeeded" means something is listening and reachable from here, whatever it does next.

# Then at the HTTP layer, with verification left ON.
curl -q --noproxy '*' -sS -o /dev/null --connect-timeout 3 -m 10 \
  -w '%{http_code}\n' "$URL/version"; echo "curl exit $?"
# Exit 0 with ANY status, 200, 401, 403 and 404 alike, means it answered.
# So does exit 60: curl reached a TLS peer, received a certificate and refused to trust it.
# That is not necessarily a completed handshake, and it does not need to be: something on
# that address answered in TLS, and the 000 printed beside it is not a pass.
# Exit 7 is "failed to connect", which is the outcome you want. Exit 28 is a TIMEOUT and it
# is NOT clean evidence either way: a dropped packet and an endpoint that accepted the
# connection and then stalled both produce it. If you get 28, the nc line above is what
# tells you which one you had.
# Any other exit is neither, and two are worth naming.
# Exit 6 is a name that did not resolve. Do not read that as proof of a private cluster:
# EKS documents that a private-only endpoint is still "resolved by public DNS servers to a
# private IP address from the VPC", so a correctly private cluster usually resolves fine
# and simply refuses the connection. Exit 6 means your resolver had no answer, which is
# worth understanding before you call it anything.
# And a TLS-intercepting middlebox on your own network answers every outbound 443 with its own
# certificate, so it prints exit 60 whether or not the cluster is reachable. Exit 60 means
# SOMETHING answered, and on a network like that it may not be the thing you aimed at; the
# unset above defeats a configured proxy and nothing defeats a transparent one except
# testing from somewhere else.

# Scan the control-plane nodes FIRST, because a worker shows 6443 and 2379 closed while
# the control-plane host serves both, and a scan of a worker alone therefore passes on an
# exposed control plane. Then scan every node that has a public address, worker nodes
# included: 10250 and 10256 are worker ports, 10250 runs commands in containers, and a
# kubeadm or k3s cluster built on cloud instances commonly gives every node a public
# address. A managed cluster hides the control-plane nodes from you, but not its workers,
# and the kubectl line below tells you which nodes have a public address. Scan the ones
# that do.
kubectl get nodes -o wide          # control-plane nodes and workers alike, but see below
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.addresses[*].address}{"\n"}{end}'
                                   # -o wide prints only the FIRST external address per node
nmap -Pn -p 6443,2379,2380,10250,10255,10256,10257,10259 REPLACE_WITH_ONE_NODE_ADDRESS
nmap -6 -Pn -p 6443,2379,2380,10250,10255,10256,10257,10259 REPLACE_WITH_ITS_IPV6_ADDRESS
                                                                     # every one closed or filtered from
                                                                     # outside. 10250 runs commands in
                                                                     # containers; 2379 is the whole of etcd
```

One name is not one address and one node is not the cluster. Repeat the scan for every node that has a
public address, worker nodes included, and every address each one answers on, in both families: a host
filtered on IPv4 while it answers on IPv6 passes every check above and is still reachable. The
`kubectl get svc` line catches NodePort Services that exist, but nothing here probes the 30000 to 32767
NodePort range itself, over TCP or UDP, so scan that too if you run self-managed nodes with
public addresses. And a cluster whose etcd runs on its own machines has hosts that `kubectl get nodes`
never lists, because they carry no kubelet; take their client and peer addresses from wherever you
configured them and scan those too.

Be clear about what a pass here is worth. It says that this host, at this moment, over this address
family, could not reach that endpoint. It does not say the cluster is restricted, because your own
egress, a stale kubeconfig context, a resolver, a tunnel that is down, or a transient failure at the far
end all produce the same result, and because an allowlist that admits one network you forgot about is
still an allowlist that admits it. Run it from more than one place before you believe it, and read the
allowed ranges out of the provider's own configuration rather than inferring them from a probe.

## Sources (checked September 2026)

- Ingress NGINX: Statement from the Kubernetes Steering and Security Response Committees (retirement, detection command): https://kubernetes.io/blog/2026/01/29/ingress-nginx-statement/ ; Kubernetes docs, Gateway API (migration guide from Ingress): https://kubernetes.io/docs/concepts/services-networking/gateway/ ; Kubernetes docs, Ingress (the project recommends Gateway; the Ingress API is frozen): https://kubernetes.io/docs/concepts/services-networking/ingress/
- Gateway API getting started (CRD install): https://gateway-api.sigs.k8s.io/guides/getting-started/introduction/ ; TLS: https://gateway-api.sigs.k8s.io/guides/user-guides/tls/ ; HTTP routing: https://gateway-api.sigs.k8s.io/guides/user-guides/http-routing/ ; redirects: https://gateway-api.sigs.k8s.io/guides/user-guides/http-redirect-rewrite/
- Envoy Gateway: https://gateway.envoyproxy.io/ ; Helm install: https://gateway.envoyproxy.io/docs/install/install-helm/ ; quickstart and its manifest (GatewayClass `controllerName`): https://gateway.envoyproxy.io/docs/tasks/quickstart/ , https://github.com/envoyproxy/gateway/releases/download/v1.9.1/quickstart.yaml
- Envoy Gateway v1.9.1 tasks, secure gateways (TLS listener): https://gateway.envoyproxy.io/docs/tasks/security/secure-gateways/ ; basic auth: https://gateway.envoyproxy.io/docs/tasks/security/basic-auth/ ; OIDC: https://gateway.envoyproxy.io/docs/tasks/security/oidc/ ; external authorization (`extAuth`): https://gateway.envoyproxy.io/docs/tasks/security/ext-auth/ ; HTTP redirect: https://gateway.envoyproxy.io/docs/tasks/traffic/http-redirect/
- htpasswd, for `-i` rather than `-b` and what SHA-1 costs: https://httpd.apache.org/docs/2.4/programs/htpasswd.html
- Authelia: proxy integration (the proxy calls the authorization endpoint): https://www.authelia.com/integration/proxies/introduction/ ; Envoy Gateway `SecurityPolicy` example: https://www.authelia.com/integration/kubernetes/envoy/gateway/
- kubectl JSONPath filter syntax: https://kubernetes.io/docs/reference/kubectl/jsonpath/
- curl exit codes, used to read the API server probe (6 could not resolve, 7 failed to connect, 28 timed out, 60 peer certificate not trusted): https://curl.se/libcurl/c/libcurl-errors.html
- curl manual (`--noproxy '*'` disables proxies; `--netrc-file` reads credentials from a file): https://curl.se/docs/manpage.html
- Nmap host discovery (`-Pn`): https://nmap.org/book/man-host-discovery.html ; port specification (`-p`): https://nmap.org/book/man-port-specification.html ; IPv6 scanning (`-6`): https://nmap.org/book/man-misc-options.html
- Kubernetes ports and protocols (6443 API server, 2379 and 2380 etcd, 10250 kubelet, 10259 scheduler, 10257 controller manager): https://kubernetes.io/docs/reference/networking/ports-and-protocols/
- Kubernetes kubelet authentication and authorization (unrejected requests treated as anonymous, `--anonymous-auth`, `--authorization-mode=Webhook`): https://kubernetes.io/docs/reference/access-authn-authz/kubelet-authn-authz/
- Kubernetes v1.37.1 source, legacy flag defaults (anonymous true, webhook false, AlwaysAllow, read-only port constant): https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/cmd/kubelet/app/options/options.go#L196-L224 ; explicit flags override the file (`--config` help): https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/cmd/kubelet/app/options/options.go#L281 ; drop-in `--config-dir` files override defaults and the file (`--config-dir` help): https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/cmd/kubelet/app/options/options.go#L282 ; wildcard address families and read-only flag semantics: https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/cmd/kubelet/app/options/options.go#L373-L398 ; read-only port constant 10255: https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/pkg/cluster/ports/ports.go#L32-L37
- Kubernetes v1.37.1 source, v1beta1 defaults (`address`, secured port, anonymous false, webhook true, Webhook authorization): https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/pkg/kubelet/apis/config/v1beta1/defaults.go#L85-L102 ; field contract (`0.0.0.0`, 10250, `readOnlyPort: 0`): https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/staging/src/k8s.io/kubelet/config/v1beta1/types.go#L160-L176
- Kubernetes v1.37.1 kubeadm configuration (read-only port 0, anonymous false, webhook true): https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/cmd/kubeadm/app/componentconfigs/kubelet.go#L33-L48 ; serialization: https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/cmd/kubeadm/app/componentconfigs/kubelet.go#L95-L100 ; authentication/authorization defaults and override warnings: https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/cmd/kubeadm/app/componentconfigs/kubelet.go#L144-L188 ; warning text: https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/cmd/kubeadm/app/componentconfigs/utils.go#L66-L71
- Kubernetes v1.37.1 server (secured address/port, read-only HTTP with nil auth): https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/pkg/kubelet/server/server.go#L181-L250 ; conditional auth filter and debugging handlers: https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/pkg/kubelet/server/server.go#L339-L375 ; auth-required container run and exec handlers: https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/pkg/kubelet/server/server.go#L577-L610 ; read-only handlers, with no `/spec` registration: https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/pkg/kubelet/server/server.go#L477-L572 ; `/stats/summary`: https://github.com/kubernetes/kubernetes/blob/f78e722310e50bcaca9276be22276d9e91d91308/pkg/kubelet/server/stats/handler.go#L109-L133
- Kubernetes command-line and configuration references (usage context; the legacy port constant 10255 is pinned above in pkg/cluster/ports/ports.go): https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/ ; https://kubernetes.io/docs/reference/config-api/kubelet-config.v1beta1/
- Amazon EKS AMI node bootstrap, the default `KubeletConfiguration` it writes (`Anonymous.Enabled: false`, `Mode: "Webhook"`, `ReadOnlyPort: 0`): https://github.com/awslabs/amazon-eks-ami/blob/6caf8311a3c6a8da71ac7e5e83f9c2e06287039a/nodeadm/internal/kubelet/config.go
- Kubernetes kubeconfig API reference (`ExecConfig`, whose `env` "defines additional environment variables to expose to the process"): https://kubernetes.io/docs/reference/config-api/kubeconfig.v1/
- Kubernetes encrypting confidential data at rest ("By default, the API server stores plain-text representations of resources into etcd, with no at-rest encryption"): https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/
- Kubernetes, operating etcd clusters, including securing communication and limiting access ("Access to etcd is equivalent to root permission in the cluster"): https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/
- GKE, disable the kubelet read-only port (disabled by default only in new clusters running 1.32 or later): https://docs.cloud.google.com/kubernetes-engine/docs/how-to/disable-kubelet-readonly-port
- Amazon EKS cluster endpoint access ("[b]y default, this API server endpoint is public to the internet"; private endpoint DNS, "resolved by public DNS servers to a private IP address from the VPC"): https://docs.aws.amazon.com/eks/latest/userguide/cluster-endpoint.html
- GKE control plane network isolation, including how authorized networks work: https://docs.cloud.google.com/kubernetes-engine/docs/concepts/network-isolation#how_authorized_networks_work
- AKS API server authorized IP ranges: https://learn.microsoft.com/en-us/azure/aks/api-server-authorized-ip-ranges
- cert-manager Gateway API usage (enabling support, annotations) (cert-manager 1.15 and later): https://cert-manager.io/docs/usage/gateway/ ; ACME HTTP-01 `gatewayHTTPRoute` solver: https://cert-manager.io/docs/configuration/acme/http01/
- Traefik Kubernetes Gateway API provider: https://doc.traefik.io/traefik/reference/install-configuration/providers/kubernetes/kubernetes-gateway/ ; Cilium Gateway API support: https://docs.cilium.io/en/stable/network/servicemesh/gateway-api/gateway-api/
