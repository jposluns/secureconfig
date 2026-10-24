# Containers: non-root, dropped capabilities, read-only root, and network segmentation

Container hardening means running each container with as few rights as possible, so an attacker inside one gains little. This guide helps your AI assistant apply it, including non-root users, dropped capabilities and read-only root filesystems in Docker, Compose and Kubernetes, plus NetworkPolicy where the cluster's network plugin enforces it.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/container-hardening.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against Docker documentation (no recorded version), Docker Compose source and reference v2.32.4, Kubernetes Pod Security Admission 1.34, kubectl source v1.34.0, Linux process status and capabilities manuals man-pages-6.19, JSON Merge Patch RFC 7396, and BusyBox source 1_36_1; 4 further sources are pinned to a commit and 1 carries no recorded version. Metadata reviewed 2026-10-21; documentation checked September 2026. The guide records 23 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

A model server, chat UI, or proxy is the thing most likely to face untrusted input, so treat its container as compromised eventually and limit what that gets an attacker: not root, not the host's capabilities, not a writable filesystem, and not a route to the rest of the network.

## Docker and Compose

- **Run as non-root.** `USER <user>[:<group>]` in the Dockerfile sets the default user for later `RUN` instructions and for `ENTRYPOINT`/`CMD` at runtime (per the Dockerfile reference); a user with no primary group runs with the `root` group, so set both. Compose's `user:` overrides that per service; unset in both places, the container runs as root (per the Compose file reference).
- **Read-only root filesystem.** `read_only: true` on a Compose service creates it with a read-only root filesystem; mount a small `tmpfs` for any path the process must write to.
- **Drop capabilities.** `cap_drop: [ALL]` removes every Linux capability; add back only the specific one a service needs with `cap_add`.
- **No privilege escalation.** `security_opt: [no-new-privileges:true]` stops a `setuid` binary from gaining more privilege than the process already has (this maps to Docker's engine-level `--security-opt no-new-privileges`; the spellings `no-new-privileges`, `no-new-privileges=true`, and `no-new-privileges:true` are equivalent).
- **Never mount the Docker socket into a container.** In Docker's default rootful configuration, control of the daemon lets a user start a container that can alter the host filesystem without restriction; membership of the `docker` group grants root-level privileges. Rootless mode runs the daemon and containers without root privileges. Docker documents that a container with the mounted `/var/run/docker.sock` and a Docker client can control the host daemon, and documents the `--privileged` and host bind-mount options. This guide's assessment: a container holding the socket can start a privileged sibling or bind-mount host `/` and escape to the host; Rootless mode narrows the host privilege available through this path but does not make the mount safe.

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

REASONED: identity, filesystem, runtime security context and segmentation checks; no exposed/fixed run is recorded in this guide. Expectations follow the cited Docker, Kubernetes and Linux man-pages sources; the authoring environment has no authorized Docker workload or Kubernetes cluster. This guide's assessment: the Compose `app` service's image must supply id, sh and touch, and the Pod's container image must supply id, sh and grep -E for these commands; the exact touch error depends on the Compose `app` service's image and probe path.

```bash
docker compose exec app id                          # uid is not 0 (run from the Compose project; this guide advises using the actual container name with bare `docker exec` rather than the `app` service name)
docker compose exec app sh -c 'touch /app/probe && echo WRITABLE || echo blocked'
                                                    # with read_only: true expect "blocked" (typically EROFS; the exact error is image-dependent). But `touch` also
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
kubectl exec app -- sh -c 'id; grep -E "NoNewPrivs|Seccomp|CapEff|CapBnd" /proc/1/status'   # expect uid!=0, NoNewPrivs:1, Seccomp:2 (a filter is active, not 0=unconfined), and CapEff+CapBnd 0000000000000000 (this guide's expected runtime state under drop:[ALL] is zero effective AND bounding sets; CapEff alone is not enough). Assumes the container's own PID namespace; with shareProcessNamespace PID 1 is the pod sandbox (shown as /pause in the cited example), so pick the app PID and inspect its /proc/<pid>/status

# resolve the db Service's ClusterIP once and probe that same IP from both pods below; the
# role: other pod has no DNS egress under the policies above, so a probe by hostname would fail on
# name resolution rather than on the NetworkPolicy, and access by IP could still work even if
# the policy were not enforcing anything
DBIP=$(kubectl get svc db -o jsonpath='{.spec.clusterIP}')

# A probe pod needs its own admission-compliant securityContext under the restricted PSA level (Pod Security
# Standards). This guide's advice: make a real TCP connect to the db's actual port (a Postgres port does not
# speak HTTP, so wget cannot test it).
# This guide's advice: quote the address into the JSON: unquoted, `10.96.0.5` is a bare token and the array is not valid
# JSON, so kubectl rejects the override and neither probe below runs. Keep the override's container name
# matching the pod name (this guide's advice): kubectl v1.34.0 `kubectl run --overrides` uses an RFC 7396 JSON
# merge patch by default (`--override-type=merge`), which replaces the whole `containers` array with the one in your override, so the
# override's container name is the one that remains (RFC 7396).
# kubectl run passes the pod name to its generator, generates the Pod, then applies the override; run.go
# does not show the generator's container-naming rule. Keep the names matching to avoid confusion (this guide's advice).
# BusyBox 1.36.1 source offers -z (zero-I/O scanning) in the 1.10-compatible nc applet with NC_EXTRA, and -w sets
# a connect timeout. At official-images d6d62c71, the amd64 busybox:1.36 image is the glibc variant published
# (imported, `Builder: oci-import`) from artefacts committed at docker-library/busybox c1375496, and its root
# filesystem has bin/nc as a link to the BusyBox binary. That commit's Dockerfile.builder applies one patch before
# `make defconfig` (no-cbq.patch, which changes only networking/tc.c and no nc file or NC option), and its config
# step changes no NC option. This guide's inference: that build produced the image's root filesystem. Tags move, so
# this tag-to-commit mapping holds as of that official-images commit, and only amd64's mapping was examined.
# Binary reading, not run: on 2026-10-24 Docker Hub served busybox:1.36 as the index
# busybox@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662, which lists nine linux images
# (armv6 musl, the others glibc); in each, bin/nc links to a BusyBox v1.36.1 binary that carries the nc getopt32
# option string `^np:s:ubvw:+lki:o:z` and not the small nc's `lp:w:i:f:e:`.
# Source reading of 1.36.1, matched against that binary reading: the string is nc_bloaty.c's, built with
# NC_110_COMPAT, NC_SERVER and NC_EXTRA. This guide's inference: each image's nc option parser accepts -z and a
# nonnegative integer -w. That is an inference because a matched string literal does not show which function
# references it, no disassembly was done, and the source clone that was read checks out only the networking,
# include, libbb and scripts directories, so whether the string occurs elsewhere in BusyBox was not checked.
# The usage text each binary carries also lists -z and -w SEC, but BusyBox generates usage text from the build
# configuration, so it corroborates those options without showing the parser.
# This guide's assessment: the index's amd64 entry names docker-library/busybox revision c1375496 and version
# 1.36.1-glibc, which agrees with the mapping above but does not prove that build made the image.
# This guide's advice: neither reading shows run-time behaviour, and tags move, so confirm that the image you pull
# accepts `nc -z -w 3` and makes a TCP connect before relying on the probe.
# Build the override per pod:
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
- Docker daemon control-socket access and host filesystem control, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/security/_index.md#L84-L112
- Docker group root-level privileges, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/install/linux-postinstall.md#L29-L39
- Docker Rootless mode daemon and container privileges, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/security/rootless/_index.md#L8-L21
- Docker run `--privileged` host control, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/data/cli/engine/docker_container_run.yaml#L1330-L1350
- Docker run mounted socket and client access to the host daemon, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/data/cli/engine/docker_container_run.yaml#L1460-L1467
- Docker run `--mount` host-directory bind mounts, at 4e9a5751518ed8223a8dcde53693badddd72604f (checked October 2026): https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/data/cli/engine/docker_container_run.yaml#L1495-L1515
- Kubernetes: Configure a security context for a Pod or Container: https://kubernetes.io/docs/tasks/configure-pod-container/security-context/
- Kubernetes: Pod Security Standards (`restricted` level, Pod Security Admission labels): https://kubernetes.io/docs/concepts/security/pod-security-standards/
- Kubernetes: Network Policies: https://kubernetes.io/docs/concepts/services-networking/network-policies/
- Kubernetes 1.34 Pod Security Admission enforcement (checked October 2026): https://v1-34.docs.kubernetes.io/docs/concepts/security/pod-security-admission/
- Kubernetes 1.34 namespace labels and warnings for existing Pods (checked October 2026): https://v1-34.docs.kubernetes.io/docs/tasks/configure-pod-container/enforce-standards-namespace-labels/
- kubectl 1.34.0 source, run name parameter (checked October 2026): https://github.com/kubernetes/kubernetes/blob/v1.34.0/staging/src/k8s.io/kubectl/pkg/cmd/run/run.go#L293-L310
- kubectl 1.34.0 source, kubectl run registers the override flags (checked October 2026): https://github.com/kubernetes/kubernetes/blob/v1.34.0/staging/src/k8s.io/kubectl/pkg/cmd/run/run.go#L103-L194
- kubectl 1.34.0 source, generation before override (checked October 2026): https://github.com/kubernetes/kubernetes/blob/v1.34.0/staging/src/k8s.io/kubectl/pkg/cmd/run/run.go#L591-L622
- kubectl 1.34.0 source, default override method (checked October 2026): https://github.com/kubernetes/kubernetes/blob/v1.34.0/staging/src/k8s.io/kubectl/pkg/cmd/util/override_options.go#L29-L90
- RFC 7396, JSON Merge Patch section 2 (checked October 2026): https://www.rfc-editor.org/rfc/rfc7396#section-2
- BusyBox 1.36.1 source, nc configuration and compatibility path (checked October 2026): https://github.com/mirror/busybox/blob/1_36_1/networking/nc.c#L30-L59
- BusyBox 1.36.1 source, compatible nc options (checked October 2026): https://github.com/mirror/busybox/blob/1_36_1/networking/nc_bloaty.c#L61-L93
- BusyBox 1.36.1 source, compatible nc connect and exit behaviour (checked October 2026): https://github.com/mirror/busybox/blob/1_36_1/networking/nc_bloaty.c#L888-L922
- BusyBox 1.36.1 source, nc getopt32 option string that the BusyBox binary in each of the nine linux images of busybox@sha256:73aaf090f3d85aa34ee199857f03fa3a95c8ede2ffd4cc2cdb5b94e566b11662 (busybox:1.36 as Docker Hub served it on 2026-10-24) carries, read without running it (checked October 2026): https://github.com/mirror/busybox/blob/1_36_1/networking/nc_bloaty.c#L793-L801
- BusyBox 1.36.1 source, small nc option string, which none of those nine binaries carries (checked October 2026): https://github.com/mirror/busybox/blob/1_36_1/networking/nc.c#L133-L138
- BusyBox 1.36.1 source, getopt32 `o:+` option parameter, a nonnegative integer processed with `xatoi_positive()`, as in nc's `w:+` (checked October 2026): https://github.com/mirror/busybox/blob/1_36_1/libbb/getopt32.c#L67-L69
- Docker Official Images busybox library at d6d62c71a83290283aa58c5041a156415cfd37d9, image repository and amd64 commit (checked October 2026): https://github.com/docker-library/official-images/blob/d6d62c71a83290283aa58c5041a156415cfd37d9/library/busybox#L5-L11
- Docker Official Images busybox library at d6d62c71a83290283aa58c5041a156415cfd37d9, 1.36 tags and amd64 glibc directory (checked October 2026): https://github.com/docker-library/official-images/blob/d6d62c71a83290283aa58c5041a156415cfd37d9/library/busybox#L111-L113
- docker-library/busybox at c1375496373e76f680b1ef5f713500e98921a45c, glibc build patch step before `make defconfig` (checked October 2026): https://github.com/docker-library/busybox/blob/c1375496373e76f680b1ef5f713500e98921a45c/latest-1/glibc/Dockerfile.builder#L51-L59
- docker-library/busybox at c1375496373e76f680b1ef5f713500e98921a45c, no-cbq patch, which changes only `networking/tc.c` (checked October 2026): https://github.com/docker-library/busybox/blob/c1375496373e76f680b1ef5f713500e98921a45c/.patches/no-cbq.patch
- docker-library/busybox at c1375496373e76f680b1ef5f713500e98921a45c, glibc build configuration (checked October 2026): https://github.com/docker-library/busybox/blob/c1375496373e76f680b1ef5f713500e98921a45c/latest-1/glibc/Dockerfile.builder#L68-L113
- docker-library/busybox at c1375496373e76f680b1ef5f713500e98921a45c, amd64 glibc root filesystem archive with `bin/nc` (checked October 2026): https://github.com/docker-library/busybox/blob/c1375496373e76f680b1ef5f713500e98921a45c/latest-1/glibc/amd64/rootfs.tar.gz
- Docker Compose v2.32.4 exec service target (checked October 2026): https://github.com/docker/compose/blob/v2.32.4/docs/reference/compose_exec.md#L1-L7
- Docker Compose v2.32.4 exec project and service options (checked October 2026): https://github.com/docker/compose/blob/v2.32.4/cmd/compose/exec.go#L84-L110
- Docker Compose v2.32.4 up detach and force-recreate flags (checked October 2026): https://github.com/docker/compose/blob/v2.32.4/cmd/compose/up.go#L145-L155
- Linux man-pages man-pages-6.19 process status fields (checked October 2026): https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/tree/man/man5/proc_pid_status.5?h=man-pages-6.19#n315
- Linux man-pages man-pages-6.19 capability bounding set (checked October 2026): https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/tree/man/man7/capabilities.7?h=man-pages-6.19#n1367
- kubectl v1.34.0 exec Pod and container examples (checked October 2026): https://github.com/kubernetes/kubernetes/blob/v1.34.0/staging/src/k8s.io/kubectl/pkg/cmd/exec/exec.go#L52-L56
- Kubernetes website 47132eb5367cfdcba0a3b33a0b3ffc81185bd7e8 shared process namespace and pod sandbox (checked October 2026): https://github.com/kubernetes/website/blob/47132eb5367cfdcba0a3b33a0b3ffc81185bd7e8/content/en/docs/tasks/configure-pod-container/share-process-namespace.md#L115-L119


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- docker: Docker documentation (unknown)
- docker-daemon: Docker daemon security documentation (4e9a5751518ed8223a8dcde53693badddd72604f)
- compose-2324: Docker Compose source and reference (v2.32.4)
- kubernetes-website: Kubernetes process namespace documentation (47132eb5367cfdcba0a3b33a0b3ffc81185bd7e8)
- kubernetes: Kubernetes documentation (unknown)
- kubernetes-134: Kubernetes Pod Security Admission (1.34)
- kubectl-134: kubectl source (v1.34.0)
- procfs-619: Linux process status and capabilities manuals (man-pages-6.19)
- rfc7396: JSON Merge Patch (RFC 7396)
- busybox-1361: BusyBox source (1_36_1)
- busybox-library: Docker Official Images busybox library (d6d62c71a83290283aa58c5041a156415cfd37d9)
- busybox-image: Docker busybox image build files (c1375496373e76f680b1ef5f713500e98921a45c)

Claims (full source mapping in the JSON block below):

- docker-user (REASONED; docker): Dockerfile USER sets build/runtime identity; set user and group, since no primary group uses root. Compose user overrides it; unset in both runs as root.
- docker-rootfs (REASONED; docker): Compose read_only makes the root filesystem read-only; provide tmpfs only for required writable paths.
- docker-capabilities (REASONED; docker): cap_drop: [ALL] removes capabilities; add back only specific required capabilities with cap_add.
- docker-escalation (REASONED; docker): no-new-privileges prevents setuid privilege gain; the guide lists bare, equals-true and colon-true spellings as equivalent.
- docker-socket (REASONED; docker, docker-daemon): Never mount /var/run/docker.sock. In Docker's default rootful configuration, daemon control lets a user start a container that can alter the host filesystem without restriction, and docker-group membership grants root-level privileges; Rootless mode runs the daemon and containers without root privileges. Docker documents mounted-socket daemon control with a Docker client, and documents --privileged and host bind mounts; a socket-holding container starting a privileged sibling or bind-mounting host / to escape is this guide's assessment. Rootless mode narrowing the available host privilege but not making the mount safe is this guide's assessment.
- kube-user (REASONED; kubernetes): runAsNonRoot rejects root; pin runAsUser and runAsGroup to 10001, with the guide noting runtime-default GID 0 if unset.
- kube-rootfs (REASONED; kubernetes): Set readOnlyRootFilesystem per container; this is a separate recommendation, not a restricted Pod Security requirement.
- kube-escalation (REASONED; kubernetes): Set allowPrivilegeEscalation: false in the container securityContext.
- kube-capabilities (REASONED; kubernetes): Drop ALL capabilities in the container securityContext.
- kube-seccomp (REASONED; kubernetes): RuntimeDefault selects the runtime syscall filter instead of Unconfined.
- admission (REASONED; kubernetes, kubernetes-134): Namespace enforce: restricted rejects new violating Pods: privileged mode, host namespaces/ports, root, missing capability drops or Unconfined seccomp.
- existing-pods (REASONED; kubernetes, kubernetes-134): Adding the namespace label warns about existing violating Pods without evicting them; recreate workloads.
- policy-semantics (REASONED; kubernetes): NetworkPolicies are additive and require an enforcing CNI; both source egress and destination ingress must allow a connection.
- default-deny (REASONED; kubernetes): The empty podSelector with Ingress and Egress isolates all pods selected in the namespace before narrow allowances.
- dns (REASONED; kubernetes): The app egress rule permits UDP/TCP 53 to all kube-system pods, not just CoreDNS; narrow it to the actual resolver.
- database-path (REASONED; kubernetes): Allow app egress to role: db and db ingress from role: app on TCP 5432; other paths governed by these namespace policies are refused.
- policy-limits (REASONED; kubernetes): hostNetwork and same-node traffic handling are implementation-dependent; database TLS/authentication remain separate controls.
- verify-user (REASONED; docker, compose-2324): Compose exec targets the app service in the resolved project and id must report a nonzero UID; using the actual container name for bare docker exec is this guide's advice.
- verify-rootfs (REASONED; docker, compose-2324): With read_only false, touch on an existing owned path must print WRITABLE; after docker compose up -d --force-recreate with read_only true, it must print blocked. ENOENT or EACCES can also print blocked on a writable filesystem, so blocked alone is not proof of a read-only root. This guide's assessment: the errno, including typical EROFS, depends on the image and path; the probe's exit 0 does not discriminate.
- verify-context (REASONED; kubernetes, kubectl-134, procfs-619, kubernetes-website): kubectl get reads the declared context; kubectl exec inspects the application process for nonzero UID, NoNewPrivs:1, Seccomp:2 and zero effective/bounding capabilities. Clearing CapBnd under drop:[ALL] is this guide's expected runtime state; with shareProcessNamespace, PID 1 belongs to the pod sandbox, so select the application PID.
- verify-probe (REASONED; kubernetes, kubectl-134, rfc7396, busybox-1361): Resolve the db ClusterIP once; keep matching container names and restricted-compliant overrides for busybox:1.36 probes. Pinned kubectl and BusyBox sources explain merge and nc flags; no probe run is recorded, so this guide advises confirming that the image accepts nc -z -w 3 and makes a TCP connect before relying on it.
- probe-image (REASONED; busybox-1361, busybox-library, busybox-image): As of official-images d6d62c71 (tags move), amd64 busybox:1.36 is the glibc variant imported from docker-library/busybox c1375496 artefacts; this guide infers that commit's build made it. Binary reading, not run: each of the nine linux images in the index served on 2026-10-24 has a BusyBox whose nc option string is nc_bloaty.c's with NC_EXTRA; this guide infers that its parser accepts -z and -w.
- verify-segmentation (REASONED; kubernetes): The role: app TCP probe must succeed first; role: other to the same IP must fail at TCP, not DNS. This tests combined segmentation, not either policy layer independently.

````json
{
  "schema": 1,
  "checked": "2026-10-21",
  "documentation_checked": "2026-09",
  "body_sha256": "29e83bf457d9e8d8d3e44f2c3d66ac3c162301aac6d95ea9ea28ada47e7bb59c",
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
    "docker-daemon": {
      "name": "Docker daemon security documentation",
      "basis": "4e9a5751518ed8223a8dcde53693badddd72604f",
      "sources": {
        "secebea1a69ab": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/security/_index.md#L84-L112",
        "s79490cd2f3b2": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/install/linux-postinstall.md#L29-L39",
        "s8eab393a61c6": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/content/manuals/engine/security/rootless/_index.md#L8-L21",
        "s94d57fcbfafe": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/data/cli/engine/docker_container_run.yaml#L1330-L1350",
        "s372ddf9da1f0": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/data/cli/engine/docker_container_run.yaml#L1460-L1467",
        "see4d326cd914": "https://github.com/docker/docs/blob/4e9a5751518ed8223a8dcde53693badddd72604f/data/cli/engine/docker_container_run.yaml#L1495-L1515"
      }
    },
    "compose-2324": {
      "name": "Docker Compose source and reference",
      "basis": "v2.32.4",
      "sources": {
        "s906b5822e9c4": "https://github.com/docker/compose/blob/v2.32.4/docs/reference/compose_exec.md#L1-L7",
        "sfe4c568a9887": "https://github.com/docker/compose/blob/v2.32.4/cmd/compose/exec.go#L84-L110",
        "s1bf114813e47": "https://github.com/docker/compose/blob/v2.32.4/cmd/compose/up.go#L145-L155"
      }
    },
    "kubernetes-website": {
      "name": "Kubernetes process namespace documentation",
      "basis": "47132eb5367cfdcba0a3b33a0b3ffc81185bd7e8",
      "sources": {
        "s3df8336a2aa8": "https://github.com/kubernetes/website/blob/47132eb5367cfdcba0a3b33a0b3ffc81185bd7e8/content/en/docs/tasks/configure-pod-container/share-process-namespace.md#L115-L119"
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
    },
    "kubernetes-134": {
      "name": "Kubernetes Pod Security Admission",
      "basis": "1.34",
      "sources": {
        "s9b9aaf5067e2": "https://v1-34.docs.kubernetes.io/docs/concepts/security/pod-security-admission/",
        "sa25682f200f0": "https://v1-34.docs.kubernetes.io/docs/tasks/configure-pod-container/enforce-standards-namespace-labels/"
      }
    },
    "kubectl-134": {
      "name": "kubectl source",
      "basis": "v1.34.0",
      "sources": {
        "s0906dc78482b": "https://github.com/kubernetes/kubernetes/blob/v1.34.0/staging/src/k8s.io/kubectl/pkg/cmd/run/run.go#L293-L310",
        "s1adb8cde69c0": "https://github.com/kubernetes/kubernetes/blob/v1.34.0/staging/src/k8s.io/kubectl/pkg/cmd/run/run.go#L103-L194",
        "sc98b92ba3ebf": "https://github.com/kubernetes/kubernetes/blob/v1.34.0/staging/src/k8s.io/kubectl/pkg/cmd/run/run.go#L591-L622",
        "s2ffc04de1d63": "https://github.com/kubernetes/kubernetes/blob/v1.34.0/staging/src/k8s.io/kubectl/pkg/cmd/util/override_options.go#L29-L90",
        "sf5417ce59241": "https://github.com/kubernetes/kubernetes/blob/v1.34.0/staging/src/k8s.io/kubectl/pkg/cmd/exec/exec.go#L52-L56"
      }
    },
    "procfs-619": {
      "name": "Linux process status and capabilities manuals",
      "basis": "man-pages-6.19",
      "sources": {
        "sa94440d59945": "https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/tree/man/man5/proc_pid_status.5?h=man-pages-6.19#n315",
        "s74035196d5f7": "https://git.kernel.org/pub/scm/docs/man-pages/man-pages.git/tree/man/man7/capabilities.7?h=man-pages-6.19#n1367"
      }
    },
    "rfc7396": {
      "name": "JSON Merge Patch",
      "basis": "RFC 7396",
      "sources": {
        "sda39f95d0890": "https://www.rfc-editor.org/rfc/rfc7396#section-2"
      }
    },
    "busybox-1361": {
      "name": "BusyBox source",
      "basis": "1_36_1",
      "sources": {
        "s14b89daa008d": "https://github.com/mirror/busybox/blob/1_36_1/networking/nc.c#L30-L59",
        "s34bdee292f79": "https://github.com/mirror/busybox/blob/1_36_1/networking/nc_bloaty.c#L61-L93",
        "s8a53fb647996": "https://github.com/mirror/busybox/blob/1_36_1/networking/nc_bloaty.c#L888-L922",
        "s77dbf800f462": "https://github.com/mirror/busybox/blob/1_36_1/networking/nc_bloaty.c#L793-L801",
        "s7333a3b4590b": "https://github.com/mirror/busybox/blob/1_36_1/networking/nc.c#L133-L138",
        "s43d921981bf2": "https://github.com/mirror/busybox/blob/1_36_1/libbb/getopt32.c#L67-L69"
      }
    },
    "busybox-library": {
      "name": "Docker Official Images busybox library",
      "basis": "d6d62c71a83290283aa58c5041a156415cfd37d9",
      "sources": {
        "s080d20eae28c": "https://github.com/docker-library/official-images/blob/d6d62c71a83290283aa58c5041a156415cfd37d9/library/busybox#L5-L11",
        "s72f8958126e8": "https://github.com/docker-library/official-images/blob/d6d62c71a83290283aa58c5041a156415cfd37d9/library/busybox#L111-L113"
      }
    },
    "busybox-image": {
      "name": "Docker busybox image build files",
      "basis": "c1375496373e76f680b1ef5f713500e98921a45c",
      "sources": {
        "s0844cb594c98": "https://github.com/docker-library/busybox/blob/c1375496373e76f680b1ef5f713500e98921a45c/latest-1/glibc/Dockerfile.builder#L51-L59",
        "s58988a470c6b": "https://github.com/docker-library/busybox/blob/c1375496373e76f680b1ef5f713500e98921a45c/.patches/no-cbq.patch",
        "s26842ca97d63": "https://github.com/docker-library/busybox/blob/c1375496373e76f680b1ef5f713500e98921a45c/latest-1/glibc/Dockerfile.builder#L68-L113",
        "s6fd2add44b43": "https://github.com/docker-library/busybox/blob/c1375496373e76f680b1ef5f713500e98921a45c/latest-1/glibc/amd64/rootfs.tar.gz"
      }
    }
  },
  "claims": {
    "docker-user": {"text": "Dockerfile USER sets build/runtime identity; set user and group, since no primary group uses root. Compose user overrides it; unset in both runs as root.", "components": ["docker"], "sources": ["docker:s6ca35cbd69e7", "docker:s8b7485a246e4"], "status": "REASONED"},
    "docker-rootfs": {"text": "Compose read_only makes the root filesystem read-only; provide tmpfs only for required writable paths.", "components": ["docker"], "sources": ["docker:s8b7485a246e4"], "status": "REASONED"},
    "docker-capabilities": {"text": "cap_drop: [ALL] removes capabilities; add back only specific required capabilities with cap_add.", "components": ["docker"], "sources": ["docker:s8b7485a246e4"], "status": "REASONED"},
    "docker-escalation": {"text": "no-new-privileges prevents setuid privilege gain; the guide lists bare, equals-true and colon-true spellings as equivalent.", "components": ["docker"], "sources": ["docker:s5d6294cf605e", "docker:s8b7485a246e4"], "status": "REASONED"},
    "docker-socket": {"text": "Never mount /var/run/docker.sock. In Docker's default rootful configuration, daemon control lets a user start a container that can alter the host filesystem without restriction, and docker-group membership grants root-level privileges; Rootless mode runs the daemon and containers without root privileges. Docker documents mounted-socket daemon control with a Docker client, and documents --privileged and host bind mounts; a socket-holding container starting a privileged sibling or bind-mounting host / to escape is this guide's assessment. Rootless mode narrowing the available host privilege but not making the mount safe is this guide's assessment.", "components": ["docker", "docker-daemon"], "sources": ["docker:s5d6294cf605e", "docker-daemon:secebea1a69ab", "docker-daemon:s79490cd2f3b2", "docker-daemon:s8eab393a61c6", "docker-daemon:s94d57fcbfafe", "docker-daemon:s372ddf9da1f0", "docker-daemon:see4d326cd914"], "status": "REASONED"},
    "kube-user": {"text": "runAsNonRoot rejects root; pin runAsUser and runAsGroup to 10001, with the guide noting runtime-default GID 0 if unset.", "components": ["kubernetes"], "sources": ["kubernetes:sb78ea91d0308"], "status": "REASONED"},
    "kube-rootfs": {"text": "Set readOnlyRootFilesystem per container; this is a separate recommendation, not a restricted Pod Security requirement.", "components": ["kubernetes"], "sources": ["kubernetes:sb78ea91d0308", "kubernetes:s1a2d717974c7"], "status": "REASONED"},
    "kube-escalation": {"text": "Set allowPrivilegeEscalation: false in the container securityContext.", "components": ["kubernetes"], "sources": ["kubernetes:sb78ea91d0308", "kubernetes:s1a2d717974c7"], "status": "REASONED"},
    "kube-capabilities": {"text": "Drop ALL capabilities in the container securityContext.", "components": ["kubernetes"], "sources": ["kubernetes:sb78ea91d0308", "kubernetes:s1a2d717974c7"], "status": "REASONED"},
    "kube-seccomp": {"text": "RuntimeDefault selects the runtime syscall filter instead of Unconfined.", "components": ["kubernetes"], "sources": ["kubernetes:sb78ea91d0308", "kubernetes:s1a2d717974c7"], "status": "REASONED"},
    "admission": {"text": "Namespace enforce: restricted rejects new violating Pods: privileged mode, host namespaces/ports, root, missing capability drops or Unconfined seccomp.", "components": ["kubernetes", "kubernetes-134"], "sources": ["kubernetes:s1a2d717974c7", "kubernetes-134:s9b9aaf5067e2"], "status": "REASONED"},
    "existing-pods": {"text": "Adding the namespace label warns about existing violating Pods without evicting them; recreate workloads.", "components": ["kubernetes", "kubernetes-134"], "sources": ["kubernetes:s1a2d717974c7", "kubernetes-134:sa25682f200f0"], "status": "REASONED"},
    "policy-semantics": {"text": "NetworkPolicies are additive and require an enforcing CNI; both source egress and destination ingress must allow a connection.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED"},
    "default-deny": {"text": "The empty podSelector with Ingress and Egress isolates all pods selected in the namespace before narrow allowances.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED"},
    "dns": {"text": "The app egress rule permits UDP/TCP 53 to all kube-system pods, not just CoreDNS; narrow it to the actual resolver.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED"},
    "database-path": {"text": "Allow app egress to role: db and db ingress from role: app on TCP 5432; other paths governed by these namespace policies are refused.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED"},
    "policy-limits": {"text": "hostNetwork and same-node traffic handling are implementation-dependent; database TLS/authentication remain separate controls.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED"},
    "verify-user": {"text": "Compose exec targets the app service in the resolved project and id must report a nonzero UID; using the actual container name for bare docker exec is this guide's advice.", "components": ["docker", "compose-2324"], "sources": ["docker:s6ca35cbd69e7", "docker:s8b7485a246e4", "compose-2324:s906b5822e9c4", "compose-2324:sfe4c568a9887"], "status": "REASONED", "verify": [1]},
    "verify-rootfs": {"text": "With read_only false, touch on an existing owned path must print WRITABLE; after docker compose up -d --force-recreate with read_only true, it must print blocked. ENOENT or EACCES can also print blocked on a writable filesystem, so blocked alone is not proof of a read-only root. This guide's assessment: the errno, including typical EROFS, depends on the image and path; the probe's exit 0 does not discriminate.", "components": ["docker", "compose-2324"], "sources": ["docker:s8b7485a246e4", "compose-2324:s1bf114813e47"], "status": "REASONED", "verify": [1]},
    "verify-context": {"text": "kubectl get reads the declared context; kubectl exec inspects the application process for nonzero UID, NoNewPrivs:1, Seccomp:2 and zero effective/bounding capabilities. Clearing CapBnd under drop:[ALL] is this guide's expected runtime state; with shareProcessNamespace, PID 1 belongs to the pod sandbox, so select the application PID.", "components": ["kubernetes", "kubectl-134", "procfs-619", "kubernetes-website"], "sources": ["kubernetes:sb78ea91d0308", "kubectl-134:sf5417ce59241", "procfs-619:sa94440d59945", "procfs-619:s74035196d5f7", "kubernetes-website:s3df8336a2aa8"], "status": "REASONED", "verify": [1]},
    "verify-probe": {"text": "Resolve the db ClusterIP once; keep matching container names and restricted-compliant overrides for busybox:1.36 probes. Pinned kubectl and BusyBox sources explain merge and nc flags; no probe run is recorded, so this guide advises confirming that the image accepts nc -z -w 3 and makes a TCP connect before relying on it.", "components": ["kubernetes", "kubectl-134", "rfc7396", "busybox-1361"], "sources": ["kubernetes:sb78ea91d0308", "kubernetes:s1a2d717974c7", "kubernetes:s953450b4076f", "kubectl-134:s0906dc78482b", "kubectl-134:s1adb8cde69c0", "kubectl-134:sc98b92ba3ebf", "kubectl-134:s2ffc04de1d63", "rfc7396:sda39f95d0890", "busybox-1361:s14b89daa008d", "busybox-1361:s34bdee292f79", "busybox-1361:s8a53fb647996"], "status": "REASONED", "verify": [1]},
    "probe-image": {"text": "As of official-images d6d62c71 (tags move), amd64 busybox:1.36 is the glibc variant imported from docker-library/busybox c1375496 artefacts; this guide infers that commit's build made it. Binary reading, not run: each of the nine linux images in the index served on 2026-10-24 has a BusyBox whose nc option string is nc_bloaty.c's with NC_EXTRA; this guide infers that its parser accepts -z and -w.", "components": ["busybox-1361", "busybox-library", "busybox-image"], "sources": ["busybox-1361:s14b89daa008d", "busybox-1361:s34bdee292f79", "busybox-1361:s77dbf800f462", "busybox-1361:s7333a3b4590b", "busybox-1361:s43d921981bf2", "busybox-library:s080d20eae28c", "busybox-library:s72f8958126e8", "busybox-image:s0844cb594c98", "busybox-image:s58988a470c6b", "busybox-image:s26842ca97d63", "busybox-image:s6fd2add44b43"], "status": "REASONED", "verify": [1]},
    "verify-segmentation": {"text": "The role: app TCP probe must succeed first; role: other to the same IP must fail at TCP, not DNS. This tests combined segmentation, not either policy layer independently.", "components": ["kubernetes"], "sources": ["kubernetes:s953450b4076f"], "status": "REASONED", "verify": [1]}
  }
}
````
<!-- version-basis:end -->
