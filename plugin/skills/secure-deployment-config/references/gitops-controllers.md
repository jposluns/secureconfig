# GitOps controllers: Argo CD and Flux

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
real deployment. The server listens on port `8080` in the pod (its Service maps `80` and `443` to it)
with metrics on `8083`; front it per [nginx.md](nginx.md), [caddy.md](caddy.md) and
[fronting-auth.md](fronting-auth.md). Keep `argocd-server` as a ClusterIP and do not publish the origin through a public LoadBalancer, NodePort, or alternate route; reach it only through a restricted, authenticated TLS ingress (or private administrative access), and protect the CLI/gRPC path as well as the browser/REST one, since the Service carries both on `443`. `server.insecure` in `argocd-cmd-params-cm` is the ConfigMap form of `--insecure` and defaults to `"false"`; it disables the backend's TLS, not authentication, so allow it only behind trusted TLS termination on a protected network.

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

Every probe below is reasoned, not demonstrated: the authoring environment has no container runtime,
so none was stood up in its exposed and fixed states. Each names its expected exposed and fixed result
so it discriminates against a live install; backlog row 2.28 tracks demonstrating them. A login page, a
redirect, a `404`, an HTML body, a TLS error, a `kubectl` `Forbidden`, or a missing-CRD error is
inconclusive, never the fixed state.

```bash
# Argo CD API auth, matched pair against the SAME endpoint. Use your real CA, never -k. Anonymous (no
# token) must answer 401 fixed (application JSON exposed); with a valid bearer token it must return JSON
# listing the expected application - the positive control a fronting proxy's 401 cannot fake. Repeat both
# against the ORIGIN from an authorized location (keep the TLS hostname), and test the gRPC/CLI path too.
curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 --cacert REPLACE_WITH_YOUR_CA_FILE \
  -w '\nanon http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
  'https://argocd.example.com/api/v1/applications'
# token from `argocd account generate-token` (or a login session); read it without echo, pass via stdin.
# Run in a subshell with tracing and allexport OFF, so an inherited `set -x` cannot echo the token and an
# inherited `set -a` cannot export it (read -s and the stdin header prevent neither).
(
  trap - DEBUG RETURN ERR  # assumes a clean shell: no inherited DEBUG trap or extdebug, no function named like a command below
  set +x +a
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
kubectl -n flux-system get svc -o wide
kubectl get ingress,httproute,grpcroute,tlsroute -A   # also check NodePort Services and host-network/hostPort pods
sudo ss -tlnp    # speaks only for the node and network namespace it runs in, not the whole cluster
```

A bare `401` proves less than it looks: a fronting authentication proxy can return it while the
underlying `users.anonymous.enabled` is still on, so pair the probe with an authenticated request
through the same route that should succeed, and read the anonymous and `policy.default` settings from
`argocd-cm`/`argocd-rbac-cm` directly. For Flux, test the webhook with an **unauthenticated** request, not merely an unsigned body, since a valid
`X-Gitlab-Token` or OIDC token authenticates without a signature. For a `generic-hmac` receiver the
signature is `X-Signature: sha256=<hex HMAC of the exact body under the receiver's secret>`; send identical
bytes without it (must be rejected) and then with it (must be accepted and trigger the reconciliation):

```bash
# Reasoned, not demonstrated (no live Flux; backlog row 2.28). Read the HMAC key without echo. openssl takes
# the key as an argument, so keep tracing off; on a shared host compute the HMAC from a language binding.
(
  trap - DEBUG RETURN ERR  # assumes a clean shell: no inherited DEBUG trap or extdebug, no function named like a command below
  set +x +a
  { unset -n hmac sig && unset -v hmac sig; } 2>/dev/null ||
    { echo 'a readonly hmac or sig is set in this shell; not probing'; exit 2; }
  { unset -n IFS; } 2>/dev/null || { echo 'a readonly IFS is set in this shell; not probing'; exit 2; }
  IFS= read -r -s -p 'receiver HMAC secret: ' hmac < /dev/tty || exit 2; echo
  [ -n "$hmac" ] || { echo 'supply the HMAC secret; not probing'; exit 2; }
  body='{"ref":"refs/heads/main"}'
  sig=$(printf '%s' "$body" | openssl dgst -sha256 -hmac "$hmac" -r | cut -d' ' -f1)
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

- Argo CD getting started (initial admin secret, server exposure): https://argo-cd.readthedocs.io/en/stable/getting_started/
- Argo CD user management (disable admin, change password): https://argo-cd.readthedocs.io/en/stable/operator-manual/user-management/
- Argo CD RBAC (anonymous access, policy.default in argocd-rbac-cm): https://argo-cd.readthedocs.io/en/stable/operator-manual/rbac/
- Argo CD server command (ports 8080/8083, --insecure): https://argo-cd.readthedocs.io/en/stable/operator-manual/server-commands/argocd-server/
- Argo CD ingress and TLS termination: https://argo-cd.readthedocs.io/en/stable/operator-manual/ingress/
- Argo CD git webhook configuration (/api/webhook, shared secret): https://argo-cd.readthedocs.io/en/stable/operator-manual/webhook/
- Argo CD AppProjects: https://argo-cd.readthedocs.io/en/stable/user-guide/projects/
- Flux security model and best practices (NetworkPolicy artifact isolation, controller permissions): https://fluxcd.io/flux/security/best-practices/
- Flux notification Receivers (types and payload validation): https://fluxcd.io/flux/components/notification/receivers/
- Flux v2.9 release (generic-oidc receiver introduced): https://fluxcd.io/blog/2026/06/flux-v2.9.0/
- Flux webhook receivers guide (port 9292, webhook-receiver Service): https://fluxcd.io/flux/guides/webhook-receivers/
- Flux multitenancy configuration (cross-namespace and service-account lockdown): https://fluxcd.io/flux/installation/configuration/multitenancy/
- Argo CD server command parameters (`server.disable.auth`, `server.insecure` defaults in argocd-cmd-params-cm): https://argo-cd.readthedocs.io/en/stable/operator-manual/argocd-cmd-params-cm-yaml/
- Argo CD RBAC ConfigMap (`policy.csv` `p`/`g` rules, empty `policy.default`): https://argo-cd.readthedocs.io/en/stable/operator-manual/argocd-rbac-cm-yaml/
- Argo CD cluster RBAC and security (narrowing `argocd-manager` privileges, remote-bases/SSRF): https://argo-cd.readthedocs.io/en/stable/operator-manual/security/
- Argo CD secret management (destination-cluster operators, repo-server/Redis exposure): https://argo-cd.readthedocs.io/en/stable/operator-manual/secret-management/
- Flux GitHub bootstrap (`--token-auth` PAT Secret, `--read-write-key` for image automation): https://fluxcd.io/flux/installation/bootstrap/github/
- Flux image update automations (Git write-back): https://fluxcd.io/flux/components/image/imageupdateautomations/
- Flux SOPS/age decryption: https://fluxcd.io/flux/guides/mozilla-sops/
- Flux OCIRepository and HelmRepository credential references (`.spec.secretRef`): https://fluxcd.io/flux/components/source/ocirepositories/#secret-reference
- Flux controller permissions (which controllers hold cluster-admin, Secret access): https://fluxcd.io/flux/security/#controller-permissions
