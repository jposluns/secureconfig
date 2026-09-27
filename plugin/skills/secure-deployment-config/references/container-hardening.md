---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "cb43ffffcc50fcf02b7be97c0948ab13cc5e36e7d0f948f4f5ac458d73684563",
  "components": {
    "docker": {
      "name": "Docker documentation",
      "basis": "unknown",
      "sources": {
        "s6ca35cbd69e7": "https://docs.docker.com/reference/dockerfile/",
        "s8b7485a246e4": "https://docs.docker.com/reference/compose-file/",
        "s5d6294cf605e": "https://docs.docker.com/reference/cli/docker/container/run/"
      }
    },
    "kubernetes": {
      "name": "Kubernetes documentation",
      "basis": "unknown",
      "sources": {
        "sb78ea91d0308": "https://kubernetes.io/docs/tasks/configure-pod-container/security-context/",
        "s1a2d717974c7": "https://kubernetes.io/docs/concepts/security/pod-security-standards/",
        "s953450b4076f": "https://kubernetes.io/docs/concepts/services-networking/network-policies/"
      }
    }
  },
  "claims": {
    "docker-user": {"text": "Dockerfile USER sets build/runtime identity; set user and group, since no primary group uses root. Compose user overrides it; unset in both runs as root.", "components": ["docker"], "sources": ["docker:s6ca35cbd69e7", "docker:s8b7485a246e4"], "status": "REASONED"},
    "docker-rootfs": {"text": "Compose read_only makes the root filesystem read-only; provide tmpfs only for required writable paths.", "components": ["docker"], "sources": ["docker:s8b7485a246e4"], "status": "REASONED"},
    "docker-capabilities": {"text": "cap_drop: [ALL] removes capabilities; add back only specific required capabilities with cap_add.", "components": ["docker"], "sources": ["docker:s8b7485a246e4"], "status": "REASONED"},
    "docker-escalation": {"text": "no-new-privileges prevents setuid privilege gain; the guide lists bare, equals-true and colon-true spellings as equivalent.", "components": ["docker"], "sources": ["docker:s5d6294cf605e", "docker:s8b7485a246e4"], "status": "REASONED"},
    "docker-socket": {"text": "Do not mount /var/run/docker.sock: the guide treats access as host-root equivalent through privileged siblings; no direct socket-security source is listed.", "components": ["docker"], "sources": ["docker:s5d6294cf605e"], "status": "REASONED"},
    "kube-user": {"text": "runAsNonRoot rejects root; pin runAsUser and runAsGroup to 10001, with the guide noting runtime-default GID 0 if unset.", "components": ["kubernetes"], "sources": ["kubernetes:sb78ea91d0308"], "status": "REASONED"},
    "kube-rootfs": {"text": "Set readOnlyRootFilesystem per container; this is a separate recommendation, not a restricted Pod Security requirement.", "components": ["kubernetes"], "sources": ["kubernetes:sb78ea91d0308", "kubernetes:s1a2d717974c7"], "status": "REASONED"},
    "kube-escalation": {"text": "Set allowPrivilegeEscalation: false in the container securityContext.", "components": ["kubernetes"], "sources": ["kubernetes:sb78ea91d0308", "kubernetes:s1a2d717974c7"], "status": "REASONED"},
    "kube-capabilities": {"text": "Drop ALL capabilities in the container securityContext.", "components": ["kubernetes"], "sources": ["kubernetes:sb78ea91d0308", "kubernetes:s1a2d717974c7"], "status": "REASONED"},
    "kube-seccomp": {"text": "RuntimeDefault selects the runtime syscall filter instead of Unconfined.", "components": ["kubernetes"], "sources": ["kubernetes:sb78ea91d0308", "kubernetes:s1a2d717974c7"], "status": "REASONED"},
    "admission": {"text": "Namespace enforce: restricted rejects new violating Pods: privileged mode, host namespaces/ports, root, missing capability drops or Unconfined seccomp.", "components": ["kubernetes"], "sources": ["kubernetes:s1a2d717974c7"], "status": "REASONED"},
    "existing-pods": {"text": "Adding the namespace label warns about existing violating Pods without evicting them; recreate workloads. Admission transition details lack a direct Sources entry.", "components": ["kubernetes"], "sources": ["kubernetes:s1a2d717974c7"], "status": "REASONED"},
    "policy-semantics": {"text": "NetworkPolicies are additive and require an enforcing CNI; both source egress and destination ingress must allow a connection.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED"},
    "default-deny": {"text": "The empty podSelector with Ingress and Egress isolates all pods selected in the namespace before narrow allowances.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED"},
    "dns": {"text": "The app egress rule permits UDP/TCP 53 to all kube-system pods, not just CoreDNS; narrow it to the actual resolver.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED"},
    "database-path": {"text": "Allow app egress to role: db and db ingress from role: app on TCP 5432; other paths governed by these namespace policies are refused.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED"},
    "policy-limits": {"text": "hostNetwork and same-node traffic handling are implementation-dependent; database TLS/authentication remain separate controls.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED"},
    "verify-user": {"text": "Compose exec app id must report a nonzero UID; the service name is project-scoped, unlike docker exec container names.", "components": ["docker"], "sources": ["docker:s6ca35cbd69e7", "docker:s8b7485a246e4"], "status": "REASONED", "verify": [1]},
    "verify-rootfs": {"text": "touch must first print WRITABLE on an owned existing path with read_only false, then blocked after recreation with true; ENOENT/EACCES or exit 0 do not discriminate.", "components": ["docker"], "sources": ["docker:s8b7485a246e4"], "status": "REASONED", "verify": [1]},
    "verify-context": {"text": "kubectl get reads declared context; inspect the application process for nonzero UID, NoNewPrivs:1, Seccomp:2 and zero effective/bounding capabilities, avoiding pause PID 1 in shared namespaces.", "components": ["kubernetes"], "sources": ["kubernetes:sb78ea91d0308"], "status": "REASONED", "verify": [1]},
    "verify-probe": {"text": "Resolve the db ClusterIP once; busybox:1.36 probes use matching container names and restricted-compliant overrides. BusyBox nc flags and kubectl merge semantics lack direct sources here.", "components": ["kubernetes"], "sources": ["kubernetes:sb78ea91d0308", "kubernetes:s1a2d717974c7", "kubernetes:s953450b4076f"], "status": "REASONED", "verify": [1]},
    "verify-segmentation": {"text": "The role: app TCP probe must succeed first; role: other to the same IP must fail at TCP, not DNS. This tests combined segmentation, not either policy layer independently.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED", "verify": [1]}
  }
}
---
# Containers: non-root, dropped capabilities, read-only root, and network segmentation

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| docker-user: Dockerfile USER sets build/runtime identity; set user and group, since no primary group uses root. Compose user overrides it; unset in both runs as root. | Docker documentation unknown | REASONED |
| docker-rootfs: Compose read_only makes the root filesystem read-only; provide tmpfs only for required writable paths. | Docker documentation unknown | REASONED |
| docker-capabilities: cap_drop: [ALL] removes capabilities; add back only specific required capabilities with cap_add. | Docker documentation unknown | REASONED |
| docker-escalation: no-new-privileges prevents setuid privilege gain; the guide lists bare, equals-true and colon-true spellings as equivalent. | Docker documentation unknown | REASONED |
| docker-socket: Do not mount /var/run/docker.sock: the guide treats access as host-root equivalent through privileged siblings; no direct socket-security source is listed. | Docker documentation unknown | REASONED |
| kube-user: runAsNonRoot rejects root; pin runAsUser and runAsGroup to 10001, with the guide noting runtime-default GID 0 if unset. | Kubernetes documentation unknown | REASONED |
| kube-rootfs: Set readOnlyRootFilesystem per container; this is a separate recommendation, not a restricted Pod Security requirement. | Kubernetes documentation unknown | REASONED |
| kube-escalation: Set allowPrivilegeEscalation: false in the container securityContext. | Kubernetes documentation unknown | REASONED |
| kube-capabilities: Drop ALL capabilities in the container securityContext. | Kubernetes documentation unknown | REASONED |
| kube-seccomp: RuntimeDefault selects the runtime syscall filter instead of Unconfined. | Kubernetes documentation unknown | REASONED |
| admission: Namespace enforce: restricted rejects new violating Pods: privileged mode, host namespaces/ports, root, missing capability drops or Unconfined seccomp. | Kubernetes documentation unknown | REASONED |
| existing-pods: Adding the namespace label warns about existing violating Pods without evicting them; recreate workloads. Admission transition details lack a direct Sources entry. | Kubernetes documentation unknown | REASONED |
| policy-semantics: NetworkPolicies are additive and require an enforcing CNI; both source egress and destination ingress must allow a connection. | Kubernetes documentation unknown | REASONED |
| default-deny: The empty podSelector with Ingress and Egress isolates all pods selected in the namespace before narrow allowances. | Kubernetes documentation unknown | REASONED |
| dns: The app egress rule permits UDP/TCP 53 to all kube-system pods, not just CoreDNS; narrow it to the actual resolver. | Kubernetes documentation unknown | REASONED |
| database-path: Allow app egress to role: db and db ingress from role: app on TCP 5432; other paths governed by these namespace policies are refused. | Kubernetes documentation unknown | REASONED |
| policy-limits: hostNetwork and same-node traffic handling are implementation-dependent; database TLS/authentication remain separate controls. | Kubernetes documentation unknown | REASONED |
| verify-user: Compose exec app id must report a nonzero UID; the service name is project-scoped, unlike docker exec container names. | Docker documentation unknown | REASONED |
| verify-rootfs: touch must first print WRITABLE on an owned existing path with read_only false, then blocked after recreation with true; ENOENT/EACCES or exit 0 do not discriminate. | Docker documentation unknown | REASONED |
| verify-context: kubectl get reads declared context; inspect the application process for nonzero UID, NoNewPrivs:1, Seccomp:2 and zero effective/bounding capabilities, avoiding pause PID 1 in shared namespaces. | Kubernetes documentation unknown | REASONED |
| verify-probe: Resolve the db ClusterIP once; busybox:1.36 probes use matching container names and restricted-compliant overrides. BusyBox nc flags and kubectl merge semantics lack direct sources here. | Kubernetes documentation unknown | REASONED |
| verify-segmentation: The role: app TCP probe must succeed first; role: other to the same IP must fail at TCP, not DNS. This tests combined segmentation, not either policy layer independently. | Kubernetes documentation unknown | REASONED |
<!-- version-basis:end -->

A model server, chat UI, or proxy is the thing most likely to face untrusted input, so treat its container as compromised eventually and limit what that gets an attacker: not root, not the host's capabilities, not a writable filesystem, and not a route to the rest of the network.

## Docker and Compose

- **Run as non-root.** `USER <user>[:<group>]` in the Dockerfile sets the default user for later `RUN` instructions and for `ENTRYPOINT`/`CMD` at runtime (per the Dockerfile reference); a user with no primary group runs with the `root` group, so set both. Compose's `user:` overrides that per service; unset in both places, the container runs as root (per the Compose file reference).
- **Read-only root filesystem.** `read_only: true` on a Compose service creates it with a read-only root filesystem; mount a small `tmpfs` for any path the process must write to.
- **Drop capabilities.** `cap_drop: [ALL]` removes every Linux capability; add back only the specific one a service needs with `cap_add`.
- **No privilege escalation.** `security_opt: [no-new-privileges:true]` stops a `setuid` binary from gaining more privilege than the process already has (this maps to Docker's engine-level `--security-opt no-new-privileges`; the spellings `no-new-privileges`, `no-new-privileges=true`, and `no-new-privileges:true` are equivalent).
- **Never mount the Docker socket into a container.** `/var/run/docker.sock` is root-equivalent access to the host; a container holding it can start a privileged sibling and escape.

```yaml
services:
  app:
    build: .
    user: "10001:10001"
    read_only: true
    tmpfs: [/tmp]
    cap_drop: [ALL]
    security_opt: [no-new-privileges:true]
```

## Kubernetes securityContext

The same controls, per-Pod or per-container, in the Kubernetes securityContext documentation:

```yaml
spec:
  containers:
    - name: app
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
        runAsGroup: 10001
        readOnlyRootFilesystem: true
        allowPrivilegeEscalation: false
        capabilities:
          drop: [ALL]
        seccompProfile:
          type: RuntimeDefault
```

`runAsNonRoot: true` refuses to start the container if its effective user is root; pin `runAsUser` and `runAsGroup` too, since an unset primary group defaults to GID 0 (the runtime default). `seccompProfile.type: RuntimeDefault` applies the runtime's default syscall filter instead of running unconfined.

Enforce this with Pod Security Admission's `restricted` level, set as the namespace label
`pod-security.kubernetes.io/enforce: restricted` (per the Pod Security Standards documentation); the label
applies to that namespace only, not the whole cluster. `restricted` requires, among its controls: no
privileged containers, no host namespaces or host ports, non-root execution, all capabilities dropped, and a
seccomp profile that is not `Unconfined`. A Pod violating any of these is rejected at admission, not merely
flagged, for Pods created after the label is set; adding the label to a namespace that already runs violating Pods does not evict them (it only warns), so recreate those workloads. The `readOnlyRootFilesystem: true` setting above is a separate, per-container recommendation this
guide makes; it is good practice, but it is not one of the controls `restricted` itself requires.

## Network segmentation

A NetworkPolicy is additive and does nothing without an enforcing CNI (per the Kubernetes NetworkPolicy documentation; confirm yours enforces it before relying on this). Start default-deny, then allow only the specific path the app needs:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny-all }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-app-egress-to-db }
spec:
  podSelector: { matchLabels: { role: app } }
  policyTypes: [Egress]
  egress:
    - to: [{ namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: kube-system } } }]
      ports: [{ protocol: UDP, port: 53 }, { protocol: TCP, port: 53 }]
    - to: [{ podSelector: { matchLabels: { role: db } } }]
      ports: [{ protocol: TCP, port: 5432 }]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-db-ingress-from-app }
spec:
  podSelector: { matchLabels: { role: db } }
  policyTypes: [Ingress]
  ingress:
    - from: [{ podSelector: { matchLabels: { role: app } } }]
      ports: [{ protocol: TCP, port: 5432 }]
```

A connection needs both sides to allow it: the egress policy on the source pod and the ingress policy on
the destination pod (per the Kubernetes NetworkPolicy documentation). With all three policies applied, an
`app` pod can resolve names through the cluster's DNS and reach the `db` pod on port 5432; the `db` pod
accepts connections only from pods labeled `role: app` on port 5432; every other path the namespace's own policies govern is refused. (NetworkPolicy handling of `hostNetwork` pods and of traffic on a pod's own node is implementation-dependent, and the DNS rule above allows port 53 to every pod in `kube-system`, not only CoreDNS, so narrow the DNS peer selector to your resolver where you can.) Databases
still need their own TLS and auth on top ([postgresql.md](postgresql.md), [mysql.md](mysql.md),
[mongodb.md](mongodb.md), [redis.md](redis.md)); a NetworkPolicy is a layer, not a substitute.

## Verify

REASONED: identity, filesystem, runtime security context and segmentation checks; no exposed/fixed run is recorded in this guide. Expectations follow the cited Docker and Kubernetes sources; this read-only review has no authorized Docker workload or Kubernetes cluster.

```bash
docker compose exec app id                          # uid is not 0 (run from the Compose project; a bare `docker exec` needs the real container name, not the `app` service name)
docker compose exec app sh -c 'touch /app/probe && echo WRITABLE || echo blocked'
                                                    # with read_only: true this prints "blocked" (EROFS). But `touch` also
                                                    # fails on a MISSING or non-writable /app (ENOENT/EACCES), which prints
                                                    # "blocked" on a WRITABLE fs too, and this line exits 0 either way (read the
                                                    # printed word, it is not an exit-status test), so prove the discrimination:
                                                    # set read_only: false and recreate (docker compose up -d --force-recreate
                                                    # app), run the same line, confirm it prints WRITABLE (the path exists and
                                                    # the user owns it), then restore read_only, recreate again, and confirm
                                                    # "blocked". Probe a path the container user owns, not `/` (a non-root
                                                    # user cannot write `/` on a writable fs either) and not a tmpfs you
                                                    # mounted (writable by design)
kubectl get pod app -o jsonpath='{.spec.containers[0].securityContext}'   # the DECLARED context, not runtime proof; also inspect the running process:
kubectl exec app -- sh -c 'id; grep -E "NoNewPrivs|Seccomp|CapEff|CapBnd" /proc/1/status'   # expect uid!=0, NoNewPrivs:1, Seccomp:2 (a filter is active, not 0=unconfined), and CapEff+CapBnd 0000000000000000 (drop:[ALL] clears the effective AND bounding sets; CapEff alone is not enough). Assumes the container's own PID namespace; with shareProcessNamespace PID 1 is the pause container, so pick the app PID

# resolve the db Service's ClusterIP once and probe that same IP from both pods below; the
# role: other pod has no DNS egress under the policies above, so a probe by hostname would fail on
# name resolution rather than on the NetworkPolicy, and access by IP could still work even if
# the policy were not enforcing anything
DBIP=$(kubectl get svc db -o jsonpath='{.spec.clusterIP}')

# a probe pod needs its own admission-compliant securityContext under the restricted PSA level, and a
# real TCP connect to the db's actual port (a Postgres port does not speak HTTP, so wget cannot test it)
# Quote the address into the JSON: unquoted, `10.96.0.5` is a bare token and the array is not valid
# JSON, so kubectl rejects the override and neither probe below runs. Keep the override's container name
# matching the pod name: kubectl run's `--overrides` use a JSON merge patch (the default
# `--override-type=merge`), which replaces the whole `containers` array with the one in your override.
# kubectl assigns the container name (the pod name) BEFORE applying the override and the override's name
# then survives, so keep them matching to avoid confusion. Build the override per pod:
probe_override() {
  printf '%s' '{"spec":{"securityContext":{"runAsNonRoot":true,"runAsUser":10001,"runAsGroup":10001,"seccompProfile":{"type":"RuntimeDefault"}},"containers":[{"name":"'"$1"'","image":"busybox:1.36","securityContext":{"allowPrivilegeEscalation":false,"capabilities":{"drop":["ALL"]}},"command":["nc","-z","-w","3","'"$DBIP"'","5432"]}]}}'
}

kubectl run probe-permitted --rm -it --restart=Never --image=busybox:1.36 --labels=role=app \
  --overrides="$(probe_override probe-permitted)" -- true
                                                     # from a pod labeled role=app, by IP: must succeed FIRST. This is the
                                                     # positive control. If it fails, the policy, the override, or this
                                                     # image's `nc` is the problem, and the forbidden probe below proves
                                                     # nothing: a refusal you cannot distinguish from a broken probe is
                                                     # not evidence

kubectl run probe-forbidden --rm -it --restart=Never --image=busybox:1.36 --labels=role=other \
  --overrides="$(probe_override probe-forbidden)" -- true
                                                     # from a pod without that label, same IP: must time out or be refused
                                                     # at TCP, not fail on DNS. Read this as an END-TO-END denial: role=other
                                                     # cannot reach the db, but the refusal could be its own default-deny
                                                     # egress OR the db's ingress (either alone would refuse it), so it
                                                     # proves the combined segmentation, not either layer in isolation.
                                                     # Isolating which layer blocks (e.g. that the db ingress admits ONLY
                                                     # role=app) needs more elaborate per-layer probes, each with its own
                                                     # positive control, and is CNI-dependent, so validate the whole policy
                                                     # set on your CNI rather than reasoning rule by rule
```

## Sources (checked September 2026)

- Docker Dockerfile reference (`USER`): https://docs.docker.com/reference/dockerfile/
- Docker Compose file reference (`user`, `read_only`, `cap_add`, `cap_drop`, `security_opt`): https://docs.docker.com/reference/compose-file/
- Docker run security options (`--security-opt no-new-privileges` and its engine behaviour): https://docs.docker.com/reference/cli/docker/container/run/
- Kubernetes: Configure a security context for a Pod or Container: https://kubernetes.io/docs/tasks/configure-pod-container/security-context/
- Kubernetes: Pod Security Standards (`restricted` level, Pod Security Admission labels): https://kubernetes.io/docs/concepts/security/pod-security-standards/
- Kubernetes: Network Policies: https://kubernetes.io/docs/concepts/services-networking/network-policies/
