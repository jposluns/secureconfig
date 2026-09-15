# GitOps controllers: Argo CD and Flux

Argo CD and Flux reconcile a git repository into a Kubernetes cluster, so both hold
cluster-admin-equivalent power: whoever can drive the controller, or change what it reconciles, can
deploy anything it can reach, across every cluster it is registered against. Three exposures follow
from that and apply to both. The blast radius is the cluster (or clusters), so administrative access
deserves the same care as the Kubernetes API itself ([kubernetes.md](kubernetes.md)). Git is an
authorization boundary: whoever can merge to a reconciled repository, or redirect a source, exercises
the controller's permissions, so platform repositories need reviewed changes and separation from
tenant repositories. And the credentials the controllers hold (git deploy keys, cluster Secrets)
should be read-only and narrowly scoped where the work allows. The tools differ in one way that shapes
the rest: Argo CD runs a network-facing API and UI with its own accounts, while Flux has no login
surface at all. Control-plane exposure itself, the API server and etcd, stays in
[kubernetes.md](kubernetes.md).

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
[fronting-auth.md](fronting-auth.md).

Two settings decide who reaches the API without an account. Anonymous access is disabled by default
(`users.anonymous.enabled`); keep it off, because an anonymous caller is granted whatever role
`policy.default` names. Leave `policy.default` empty, which is its safe default in the
`argocd-rbac-cm` ConfigMap: an authenticated user who matches no role then gets no access, and access
is granted through explicit roles and group mappings instead. Argo CD RBAC grants through the default
role are additive and cannot be revoked by a later subject rule, so a permissive default is
especially hard to walk back. Separately, `argocd-server` serves an inbound git-webhook handler at
`/api/webhook` that accepts events without authentication unless you configure a webhook shared
secret; it triggers application refreshes and reconciliations rather than deploying attacker-supplied
manifests, but leaving it open to spoofed events is a reconciliation and resource-exhaustion vector
once the server is routed externally, so set the secret whenever it is reachable.

Finally, the `argocd-manager` ServiceAccount that Argo CD installs on a registered cluster is bound to
an admin-level ClusterRole, so driving Argo CD is deployment power over every cluster it manages;
scope who can act through project roles, move applications into restricted `AppProject`s, and tighten
the permissive built-in `default` project itself rather than only moving applications out of it, since
it still governs any new application placed there. Argo CD's Redis cache and repo-server can also hold
generated manifests, which matter when a config-management plugin injects secrets into them; restrict
access to them with enforced NetworkPolicies, the same isolation Flux's artifacts need. Treat Argo
CD access as cluster-admin
access.

## Flux

Flux has no built-in UI, API, dashboard, or default external network listener: it is a set of
in-cluster controllers that reconcile git into the cluster. There is no login surface to harden. Its
controllers do expose in-cluster listeners (the webhook receiver, the source-controller's artifact
server, metrics, health), so an `ss` inside a controller's own network namespace still shows sockets;
that is expected, not a finding. The surfaces that matter are three. Git repository credentials,
referenced as Secrets by the sources, are the primary one: use read-only deploy credentials for
pull-only reconciliation, keep tenant repositories separate from platform repositories, and narrow
the RBAC on the Secrets that hold them. The source-controller then serves the fetched artifacts to the
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
OIDC providers rather than a secret, so constrain it with an audience and token validations, since a
public issuer can otherwise mint valid tokens for unrelated callers. Choose a validating type,
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
# Argo CD API without a credential: exposed (anonymous on + a permissive default) returns application
# JSON; fixed answers 401. Use your real CA, never -k, which would accept any certificate.
curl -q -g -s --noproxy '*' --cacert REPLACE_WITH_YOUR_CA_FILE \
  -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' \
  'https://argocd.example.com/api/v1/applications'
# The bootstrap admin Secret should be gone once the password was rotated (its presence proves retained
# bootstrap material; its absence alone does not prove the password changed). This prints no secret.
kubectl -n argocd get secret argocd-initial-admin-secret -o name
# Network inventory: management access should have no external route. List Services, Ingresses, and
# Gateway routes, not only the named Service, since another Service, a NodePort, or an HTTPRoute can
# reach the same pods.
kubectl -n argocd get svc -o wide
kubectl -n flux-system get svc -o wide
kubectl get ingress,httproute -A
sudo ss -tlnp    # speaks only for the node and network namespace it runs in, not the whole cluster
```

A bare `401` proves less than it looks: a fronting authentication proxy can return it while the
underlying `users.anonymous.enabled` is still on, so pair the probe with an authenticated request
through the same route that should succeed, and read the anonymous and `policy.default` settings from
`argocd-cm`/`argocd-rbac-cm` directly. For Flux, test the webhook with an **unauthenticated** request,
not merely an unsigned body, since a valid `X-Gitlab-Token` or OIDC token authenticates without a
signature: POST to the receiver's path with no credential and expect a `generic` receiver to accept it
(and trigger a reconciliation) while a validating receiver rejects it, then send a correctly
authenticated request of that receiver's type as the positive control. Read the receiver's status
without printing its `.status.webhookPath`, which is itself a capability for a `generic` receiver. The
rejection status is type- and version-dependent, so read it as rejected rather than a fixed code.
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
- Flux webhook receivers guide (port 9292, webhook-receiver Service): https://fluxcd.io/flux/guides/webhook-receivers/
- Flux multitenancy configuration (cross-namespace and service-account lockdown): https://fluxcd.io/flux/installation/configuration/multitenancy/
