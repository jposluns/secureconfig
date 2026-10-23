# GitOps controllers: Argo CD and Flux

Argo CD and Flux are GitOps tools: they watch a Git repository and keep a Kubernetes cluster matching it, using whatever permissions they are granted. This guide helps your AI assistant configure each securely, including guarded admin access, reviewed changes to the repositories they deploy, narrow credentials, and restricted egress.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/gitops-controllers.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against Argo CD v3.5.3 source (pinned to a commit), Flux OIDC introduction v2.9, Dex source v2.45.1, Redis source 8.2.3, curl curl-8_14_1, go-grpc-middleware source v2.3.3, and go-grpc-middleware providers/prometheus source v1.1.0; 4 further sources are pinned to a commit and 3 carry no recorded version. Metadata reviewed 2026-10-19; documentation checked September 2026. The guide records 57 claims, all reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

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
rotate the credential, so change the password first. Give `argocd account update-password` the current
and new passwords at the tool's prompt, not as arguments: `--current-password` and `--new-password`
would put them in its argv. Sources has no reference for the command prompting (its Argo CD user
management entry is described as covering disabling admin and changing the password), so confirm
that it does before relying on it. A prompt keeps the passwords out of the command text, shell
history and shell tracing; the account owner and root can still read them in the `argocd` process
while it runs. `admin` is the only built-in user and a
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
| Application controller | Plain-HTTP metrics, health and file-gated pprof on `0.0.0.0:8082`; the host is hardcoded and only `--metrics-port` (default `8082`) sets the port | Container port and `argocd-metrics` Service |
| ApplicationSet controller | Webhook `:7000`, metrics `:8080`, health probes `:8081`; empty hosts are wildcard binds | Container and Service ports `7000` and `8080`; probe port `8081` has neither declaration |
| Notifications controller | HTTP metrics `0.0.0.0:9001` | Metrics Service and TCP liveness probe; no `containerPort` declaration |
| Dex | Generated `web.https` (or `web.http` with TLS disabled) `0.0.0.0:5556`, `grpc.addr` `0.0.0.0:5557` and telemetry `http` `0.0.0.0:5558` | All three container and Service ports; the wrapper starts Dex only with a nonempty generated configuration |
| Redis | Port `6379`; the Deployment has no bind override, and the `redis:8.2.3-alpine` tag, taken as built from docker-library-redis bcbc6921 (tag v8.2.3), uses Redis defaults of IPv4 wildcard (`*`) and optional IPv6 wildcard (`-::*`), with protected mode patched off; this holds for the deployed `public.ecr.aws/docker/library/redis:8.2.3-alpine` image only if that registry tag was built from that recipe (recipe NOT ESTABLISHED) | Container port and Service |

Repo-server's metrics/health mux and notifications' metrics handler have no authentication wrapper
and use HTTP, so a reachable pod-network peer can request them without an Argo CD login. Repo-server
gRPC defaults to TLS (`--disable-tls=false`), but the command documents skipping mTLS when
`/app/config/reposerver/mtls/client-ca.crt` is absent. The base Deployment optionally mounts
`argocd-repo-server-mtls` for that client CA, separately from `argocd-repo-server-tls` for the serving
certificate. A serving certificate alone does not require a client identity. The server requires and verifies client certificates when a client CA is loaded; without that CA it uses TLS without client-certificate authentication. If either serving certificate file is missing or cannot be stat'ed, the helper generates a session self-signed certificate; a present but invalid pair fails loading. The gRPC interceptor chain shows logging, metrics, recovery and unary error sanitization, with no authorization interceptor. The registered repository service's struct has no authenticator or enforcer field, and its handlers read no caller identity: `ListRefs`, for example, discards its call context, and a search of the non-test `reposerver/` code finds no peer, incoming-metadata, `AuthInfo`, claims or `Enforce` reads, including in handlers such as `GenerateManifest` that pass the context on. So, from this source reading, any client that completes the transport handshake can call every method; its one `PermissionDenied` reports Helm repositories that the request's own project source list does not permit. The server also registers gRPC reflection, health and version services. Isolate repository operations and cached manifests
from unrelated pods.

Redis is not passwordless in these base manifests: the `secret-init` init container runs
`argocd admin redis-initial-password`, and Redis receives `--requirepass` from the `auth` key of the
`argocd-redis` Secret. This is an init container, not a separate Job. Holding the password in a
Secret does not keep it off the command line: as an argument, it is in the Redis process's argv from
its start until the process overwrites its arguments, if it does, readable through `ps` and
`/proc/<pid>/cmdline` by other local accounts on the node as well as by the same account and root, and command-line auditing on the node
can record it beyond that. Where a process overwrites its own arguments, they stay readable until
the overwrite runs. Redis 8.2.3 has no password-specific redaction of its start-up arguments. On Linux it copies its arguments to the heap at start-up and, with `set-proc-title` at its default `yes`, its first title update zeroes the original argument area and writes the process title there; that runs before Redis opens its listeners. From this source reading, the password stays in `/proc/<pid>/cmdline` until then and in the process's heap copies afterwards. This is not a live observation. Treat
every account that can read the node's processes as able to read the Redis password. The base
Deployment does pass the value through the `REDIS_PASSWORD` container environment variable, which the `--requirepass $(REDIS_PASSWORD)` argument references, so it is also readable through
`/proc/<pid>/environ` by the same account and root. From this source reading, Redis 8.2.3's title initialization extends the range that its first title update zeroes over any environment strings laid out contiguously after the argument strings, and, before that update, rebuilds the environment through `setenv()` from the original strings (after `clearenv()` where glibc is detected, otherwise after pointing `environ` at a new empty array), so the variable stays set in the process while an original `REDIS_PASSWORD=` string inside that range is zeroed with the arguments. Whether the environment strings lie directly after the arguments, and what `/proc/<pid>/environ` returns after the overwrite, are NOT ESTABLISHED; this is not a live observation. No Redis TLS
is configured by these manifests, and Argo CD's Redis client defaults to `--redis-use-tls=false`;
protect that traffic and Secret as well as the cached data. The initializer generates a 16-character random password, creates the Secret if absent, then checks that its password key exists. The base Redis kustomization renames the `redis` image to `public.ecr.aws/docker/library/redis`, keeping the tag, and the rendered `install.yaml` names `public.ecr.aws/docker/library/redis:8.2.3-alpine`; the pinned sources do not establish which build recipe that registry tag comes from (NOT ESTABLISHED), so the reading that follows holds for that deployed image only if the registry tag was built from docker-library-redis bcbc6921. Docker Official Images' `library/redis` file, at the official-images commit that added the tag, lists `8.2.3-alpine` with `GitRepo` redis/docker-library-redis, `GitCommit` bcbc6921, `GitFetch` `refs/tags/v8.2.3` and `Directory` `alpine`, and its last revision listing the tag keeps the same `GitCommit`. The official-images README says Bashbrew fetches each entry's `GitRepo` at its `GitCommit`, tags the built image with the library file's name, and also rebuilds listed tags when their base image is updated. That identifies the recipe for Docker Hub's `redis:8.2.3-alpine`, not a fixed image: the file records no digests, and a base-image rebuild keeps the tag. It does not establish that the ECR registry tag, or any pull of either tag, is that build (NOT ESTABLISHED). The `redis:8.2.3-alpine` tag, taken as built from docker-library-redis bcbc6921 (tag v8.2.3), starts Redis without a config file; Redis 8.2.3 defines `CONFIG_DEFAULT_BINDADDR` as `*` and `-::*` and initializes its bind list from it. The `-` makes an unavailable IPv6 address optional, and the image build patches protected mode off. This is a source-derived default, not a live socket observation.

Dex's wrapper defaults to TLS for its HTTP endpoint. The generator replaces the `web`, `grpc` and
`telemetry` mappings: `web.https` uses `/tmp/tls.crt` and `/tmp/tls.key`, or `web.http` is used with
`--disable-tls`; `grpc` contains only `addr: 0.0.0.0:5557`, with no TLS or client-authentication
settings, and telemetry uses HTTP on `0.0.0.0:5558`. HTTP TLS does not secure the gRPC listener.
The `ghcr.io/dexidp/dex:v2.45.1` tag, taken as built from Dex v2.45.1, has a `GRPC` struct that maps `TLSCert` to the `tlsCert` configuration key; its server creates gRPC transport credentials only when that field is set. Argo CD's generated `grpc` mapping contains only `addr`. Its gRPC options therefore show no TLS or authentication interceptor for this configuration. The wrapper runs `dex serve /tmp/dex.yaml` inside that container. Dex v2.45.1's release workflow runs on pushed tags matching `v[0-9]+.[0-9]+.[0-9]+` and builds the checked-out tree, tagging the alpine variant of `ghcr.io/` plus the repository name through a `type=semver,pattern={{raw}}` rule. Its release job calls that workflow with `publish: true`, under which the workflow pushes the image, signs `ghcr.io/` plus the repository name at the pushed digest with `cosign sign` using the GitHub OIDC token, and pushes a build provenance attestation for that digest; this gives a verification path, but no fetched page shows the `v2.45.1` digest and no signature or attestation was verified here, so whether the published `v2.45.1` image came from that run is NOT ESTABLISHED. The registered Dex API handlers read no caller identity; `GetClient` returns a client's secret and `CreateClient` stores a new client. Argo CD's generator adds its static client with the Dex OAuth2 client secret, and Dex serves static clients from the storage that API reads, so, from this source reading, any caller that reaches `5557` can read that secret and create clients. The Dex NetworkPolicy, which admits only the server to `5557`, is the remaining barrier where a CNI enforces it.

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
The fetched RBAC loader passes the ConfigMap `policy.default` value to the enforcer; an omitted key yields an empty string, so this enforcer skips its additive default-role check. In `argocd-server`, the enforcer is built for `argocd-rbac-cm` with the built-in policy and a claims enforcer, and its `EnableEnforce` switch receives the inverse of the server's disable-auth option. The server starts the ConfigMap policy loader. By default, its gRPC interceptor chains authenticate each call with the server's `Authenticate` function unless authentication is disabled, storing the caller's claims (an empty claims value for an anonymous caller when anonymous access is enabled). From this source reading, three services override that authentication function for every method: the session and version services accept unauthenticated callers, and the settings service accepts them only for `Get`, returning any `Authenticate` error for its other methods. For the calls they accept unauthenticated, each attempts authentication to populate claims and ignores its error; the session service's comment says the server's authentication would run without its override. The server imports its authentication interceptors from `go-grpc-middleware/v2`, which Argo CD's `go.mod` pins at v2.3.3; Argo CD's `go.sum` lines for it match the `Sum` and `GoModSum` hashes a `go mod download` run for this guide on 23 October 2026 (go1.26.5, GOPROXY `proxy.golang.org`, GOSUMDB `sum.golang.org`) recorded over the downloaded module zip, which ties `go.sum` to that zip and the tree extracted from it, not to the v2.3.3 git tag tree the cited links point at. In v2.3.3, the unary and stream server auth interceptors each call a service's `AuthFuncOverride`, with the full method name, in place of the default authentication function when the service value they receive implements it, and return its error before the handler runs. From this source reading of grpc-go v1.81.1, the version Argo CD's `go.mod` requires (its `go.sum` lines match the same run's hashes for its downloaded zip), `grpc.NewServer` combines the `ChainUnaryInterceptor` interceptors into one, registration stores each service's implementation, each unary call passes that implementation and the combined interceptor to the generated method handler, and the chain hands every interceptor the same `UnaryServerInfo`, whose `Server` field grpc-go documents as the read-only service implementation the user provides. Argo CD's generated session, version and settings handlers put the value they receive in `Server`, those three services have no streaming methods, and `argocd-server` registers its `*session.Server`, `*version.Server` and `*settings.Server` values, the types that define the overrides. Argo CD's own bug21955 workaround interceptor, first in its unary chain, was read and discards its `*grpc.UnaryServerInfo` parameter. Between that workaround and the auth interceptor the chain runs v2.3.3's logging interceptor, then the metrics interceptor of `go-grpc-middleware/providers/prometheus` v1.1.0, the version `go.mod` pins (its `go.sum` lines also match that run's hashes). Read in the module trees extracted from those zips, both wrap one shared v2.3.3 interceptor that reads only `info.FullMethod`, builds its call metadata from that string and calls the handler with the context its reportable returns, writing nothing to `UnaryServerInfo` or its `Server` field. So the auth interceptor receives those values; whether each linked tag's git tree matches its downloaded zip was not compared. The API services receive the enforcer: for example, application `List` keeps only applications that pass a `get` check, and `Create` checks `create`. Per-handler coverage and effective runtime overrides were not traced or tested.
Two settings decide who reaches the API without an account. Anonymous access is disabled by default
(`users.anonymous.enabled`); keep it off, because an anonymous caller is granted whatever role
`policy.default` names. Leave `policy.default` empty, as in the base
`argocd-rbac-cm` ConfigMap: the inspected enforcer grants no default-role permissions to a user who matches no role, and access
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
through stdin or the prompt, never Git or logs. Typed at the prompt, the token stays out of shell
history and `set -x` tracing. Piped in, a token typed literally into the feeding command enters
shell history, and with `set -x` on also the trace; a token the feeding command expands from a
variable reaches the trace with `set -x` on, but history records only the variable's name, which
does not carry its value (a command that assigned the value literally is in history itself). Either
way stdin closes the argv channel only: the account owner and root can still read the token in the
`flux` process. Image automation is the exception to read-only: the
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

REASONED: section scope and authoring provenance; local marking review (October 2026, Bash 5.3.9) ran bash -n and ShellCheck 0.11.0 -s bash on the three Verify shell blocks, each with exit 0 and no diagnostics; the stub outcomes and expected exposed and fixed results are recorded at their individual checks, per the guide's cited Argo CD RBAC (anonymous access, policy.default in argocd-rbac-cm), Argo CD Repo-server component selectors and metrics allowance, Argo CD Server allow-all ingress policy, Argo CD Profiler paths and exact file-content gate, and Flux notification Receivers (types and payload validation) entries. A live Argo CD or Flux stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; a Kubernetes cluster is also required. The authoring prerequisites and inconclusive outcomes are described in the unchanged note. Every probe below is REASONED, not demonstrated: the authoring environment has no container runtime;
also, the authoring host forbids opening listeners without an isolated network namespace, and has none;
there is no Kubernetes cluster. None was stood up in its exposed and fixed states. Each names its expected exposed and fixed result
so it discriminates against a live install, based on the cited vendor documentation and pinned source readings. A login page, a
redirect, a `404`, an HTML body, a TLS error, a `kubectl` `Forbidden`, or a missing-CRD error is
inconclusive, never the fixed state.

REASONED: the backlog scope note and the token-paste instruction for the Argo CD block below; the scope
note restates backlog row 2.28, and the paste-alone warning follows CONTRIBUTING rule 7's `read`
exception. No container runtime, isolated network namespace or Kubernetes cluster is available, so no
Argo CD response was observed. During marking review (October 2026) the block passed bash -n under
bash 5.3.9 and ShellCheck 0.11.0 without diagnostics.
In a scratch-local review, the block ran from a file with curl, kubectl, sudo and ss stubbed,
no network and a pseudo-terminal. Unchanged placeholders and substituted dummy inputs each printed
'stub curl' twice, 'stub kubectl' six times, 'stub sudo' and 'stub ss' (file exit 0).
An empty token printed 'supply the token; not probing'; readonly tok printed
'a readonly tok is set in this shell; not probing'; readonly IFS printed
'a readonly IFS is set in this shell; not probing'. Each refusal still printed the anonymous
'stub curl' and all inventory stub lines, and the file exited 0 after inventory continued.
These stub outputs do not verify Argo CD authorization; the live comparison remains anonymous
401 versus application JSON listing the expected application with a valid token.
Backlog row 2.28 retains the remaining limits: which build recipe produced the deployed Redis tag,
whether the published Dex image came from its release workflow, whether Redis's title overwrite
also clears the `REDIS_PASSWORD` environment copy, and per-handler RBAC coverage in `argocd-server`.
Those are not traced here, and the cited source readings are not live
observations.
In the block below, paste the Argo CD bearer token alone at the hidden prompt: a multi-line paste leaves
every line after the first for your shell to run.

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
# The hidden prompt keeps the token out of shell history; stdin closes the argv channel only, so the
# account owner and root can still read the token in the subshell and curl.
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

REASONED: following block; internal socket and policy inventory plus the repo-server metrics probe; local marking review (October 2026, Bash 5.3.9) ran bash -n and ShellCheck 0.11.0 -s bash with exit 0 and no diagnostics. With stubbed curl, placeholder, empty and invalid addresses printed 'supply the actual IPv4 pod address; not probing' (exit 2); shortened and wrong-marker assignments printed 'incomplete probe; not probing' (exit 2); with IFS=0 and 20 values (marker plus 19), the quoted count printed 'incomplete probe; not probing' (exit 2), while an unquoted-$# control reached the curl stub and printed 'stub curl' (exit 0); a valid fixture printed 'stub curl' (exit 0). A live repo-server stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; a Kubernetes cluster with a supporting CNI, actual component sockets and authorized and unrelated pod vantages is also required. The base policy should return HTTP 200 metrics at both vantages; narrowed policy should return no HTTP response at the unrelated pod while the monitoring pod still returns metrics, per the guide's cited Argo CD Repo-server HTTP metrics and health mux and Argo CD Repo-server component selectors and metrics allowance entries. For internal isolation, inventory actual sockets in each component's network namespace with
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

REASONED: preceding block; the preceding repo-server guard and this server metrics and profiler comparison; local marking review (October 2026, Bash 5.3.9) ran bash -n and ShellCheck 0.11.0 -s bash on the guard with exit 0 and no diagnostics, and its stubbed curl and rejection results are recorded in the preceding paragraph. A live Argo CD server stand-up opens a listener; the authoring host forbids that without an isolated network namespace, and none was available; a Kubernetes cluster with a supporting CNI, the mounted profiler file, and monitoring and unrelated pod vantages is also required. Base metrics should return HTTP 200 at both vantages; narrowed policy should yield no HTTP response at the unrelated pod while the monitoring pod still receives metrics. From the allowed pod the profiler should return 401 disabled, 200 for exact true, and 401 for true plus newline, with metrics still answering, per the guide's cited Argo CD Repo-server component selectors and metrics allowance, Argo CD Server unauthenticated HTTP metrics mux and profiler registration, Argo CD Server allow-all ingress policy, and Argo CD Profiler paths and exact file-content gate entries. For server metrics, repeat the guarded pod-IP probe above with the actual server pod IP and
port `8083`, keeping `/metrics`. This check is also REASONED for the missing isolated network
namespace and Kubernetes cluster. Before narrowing the server's allow-all policy,
expect HTTP 200 and Prometheus metrics without credentials from both pods; afterwards only the
authorized monitoring pod should receive them. From that allowed pod, repeat with
`/debug/pprof/cmdline`: expect `401` with profiling disabled, then HTTP 200 and the process command
line when the mounted file contains exactly `true`. In an isolated demonstration, confirm that
`true` followed by a newline returns `401` again. Keep `/metrics` as the positive control throughout;
a failed control is inconclusive. Return profiling to disabled after the demonstration. The pinned
metrics mux, profiler wrapper and server NetworkPolicy below distinguish these states.

REASONED: the paired Argo CD `401` reading for the Argo CD API block earlier in this section and the Flux receiver checks
for the block below, per the guide's cited Argo CD anonymous-access and RBAC entries, Flux notification
Receivers entry and Python HMAC entries, with the paste-alone warning per CONTRIBUTING rule 7's `read`
exception. No live Argo CD or Flux installation is available, so no receiver response or reconciliation
was observed. During marking review (October 2026) the Flux block passed bash -n under bash 5.3.9 and
ShellCheck 0.11.0 without diagnostics.
In a scratch-local review, the block ran from a file with curl and python3 stubbed, no network
and a pseudo-terminal. Unchanged placeholders and substituted dummy inputs each printed
'stub curl' twice (exit 0); an empty secret printed 'supply the HMAC secret; not probing'
(exit 2); readonly hmac and readonly sig each printed
'a readonly hmac or sig is set in this shell; not probing' (exit 2); readonly IFS printed
'a readonly IFS is set in this shell; not probing' (exit 2). The python3 stub supplied a fixed
signature, so the HMAC computation is not verified. In the local marking review, a python3 stub exiting 1 and one printing no output each printed 'signature generation failed; not probing' (exit 2). With no readable /dev/tty, stdout was empty and Bash printed `<fixture path>: line 16: /dev/tty: No such device or address` on stderr (exit 2). The stub outputs do not verify receiver
authorization or reconciliation; the live comparison remains rejection without a signature
versus acceptance and reconciliation with a valid signature over the same body.
A bare `401` proves less than it looks: a fronting authentication proxy can return it while the
underlying `users.anonymous.enabled` is still on, so pair the probe with an authenticated request
through the same route that should succeed, and read the anonymous and `policy.default` settings from
`argocd-cm`/`argocd-rbac-cm` directly. For Flux, test the webhook with an **unauthenticated** request, not merely an unsigned body, since a valid
`X-Gitlab-Token` or OIDC token authenticates without a signature. Paste the receiver's HMAC secret alone at the
block's hidden prompt: a multi-line paste leaves every line after the first for your shell to run.
For a `generic-hmac` receiver the
signature is `X-Signature: sha256=<hex HMAC of the exact body under the receiver's secret>`; send identical
bytes without it (must be rejected) and then with it (must be accepted and trigger the reconciliation):

```bash
# REASONED: Flux webhook checks follow the cited receiver documentation; no live Flux is available.
# Read the HMAC key without echo.
# Python's hmac reads the key from stdin; only the non-secret request body is passed in argv.
# The hidden prompt keeps the key out of shell history and set +x keeps it out of set -x tracing.
# Stdin closes the argv channel only: the account owner and root can still read the key in the
# subshell and python3.
# The signature, a replayable HMAC for that exact body, goes to curl on stdin as a header line (-H @-)
# and the fixed, non-secret body as an argument. Stdin closes the argv channel only: the account owner
# and root can still read the signature in the subshell and curl.
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
  printf 'X-Signature: sha256=%s\n' "$sig" | curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -X POST --data-binary "$body" -H @- -w '\nsigned http=%{http_code}\n' "$url"  # expect accepted
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
- [curl curl-8_14_1 custom headers (checked October 2026)](https://raw.githubusercontent.com/curl/curl/curl-8_14_1/docs/cmdline-opts/header.md).
- curl curl-8_14_1 (checked October 2026): [--data-binary posts data exactly as specified, with newlines and carriage returns preserved and @- reading stdin (4-32)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/data-binary.md#L4-L32); [--data sends a POST request and strips carriage returns and newlines from @file input (4-49)](https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/data.md#L4-L49).

Argo CD source claims below were checked offline at v3.5.3, commit
`c9c369efcc5b2a0bd720803f8d14a1c3eaddf579`. Dex v2.45.1, Redis 8.2.3, docker-library-redis v8.2.3 (commit `bcbc692165ce2241e194035041c5b5e01d2e1a5f`) and Docker Official Images' `library/redis` file (official-images commits `1ff8d41b352de957628be66246d3af2996948c75` and `f80a67f648fe5f70e6708772537c48237dfbe39b`) and README (commit `326d6f326e8ed6ea7b66fcc53c6b78dd22334a2d`) were checked offline in October 2026. So were go-grpc-middleware v2.3.3 (commit `390bcef25adebe4b0c7dbb365230c0a856737afe`), go-grpc-middleware providers/prometheus v1.1.0 (read in the module tree extracted from its downloaded zip; commit `53040665d19bab33e444905822557433511bb981`, to which its tag peeled in a clone made for this guide on 23 October 2026) and grpc-go v1.81.1 (commit `caf0772c2bcb8bc15d43eb53448e921f34f0b7e8`). The go-grpc-middleware, providers/prometheus and grpc-go versions are the ones Argo CD's `go.mod` pins; Argo CD's `go.sum` lines for all three match the `Sum` and `GoModSum` hashes a `go mod download` run for this guide on 23 October 2026 (go1.26.5, GOPROXY `proxy.golang.org`, GOSUMDB `sum.golang.org`) recorded over the downloaded module zips. On the same day, `diff -rq` reported no file whose contents differ between each module tree extracted from those zips and a clone of its tag at the commit above (for providers/prometheus, the clone's `providers/prometheus` module directory). In this guide's source reading, each path on one side only is, or holds only, a nested module directory with its own `go.mod`, which the go command leaves out of a module zip, or is the providers/prometheus zip's `LICENSE`, which the go command copies from the repository root into a subdirectory module with none (byte-identical to the root file in a comparison made for this change). That compares file contents per path; it does not recompute the `h1:` hashes from the git trees and says nothing about other tags or file modes. Retained readthedocs links provide operational guidance;
they were not rechecked online. Remaining source limits are identified above.

- Application-controller metrics port handoff: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd-application-controller/commands/argocd_application_controller.go#L192-L209
- Application-controller metrics flag: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd-application-controller/commands/argocd_application_controller.go#L272-L273
- Application-controller hardcoded metrics bind host: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/controller/appcontroller.go#L321-L323
- Application-controller metrics server start: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/controller/appcontroller.go#L996
- Application-controller metrics, file-gated pprof and health mux and HTTP server: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/controller/metrics/metrics.go#L187-L220
- Repo-server TLS and client CA setup: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/reposerver/server.go#L49-L85
- Repo-server gRPC interceptor chain and registration: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/reposerver/server.go#L94-L150
- Repo-server request-derived Helm repository PermissionDenied: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/reposerver/repository/repository.go#L1385-L1401
- Repo-server repository service fields, with no authenticator or enforcer: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/reposerver/repository/repository.go#L87-L106
- Repo-server ListRefs handler, which discards its call context: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/reposerver/repository/repository.go#L227-L247
- Repo-server GenerateManifest handler: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/reposerver/repository/repository.go#L631-L706
- Repo-server certificate fallback: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/tls/tls.go#L428-L506
- Dex image tag: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/dex/argocd-dex-server-deployment.yaml#L38-L42
- Dex gRPC configuration field and JSON tag: https://github.com/dexidp/dex/blob/v2.45.1/cmd/dex/config.go#L255-L265
- Dex gRPC TLS options: https://github.com/dexidp/dex/blob/v2.45.1/cmd/dex/serve.go#L151-L199
- Dex gRPC listener and registration: https://github.com/dexidp/dex/blob/v2.45.1/cmd/dex/serve.go#L553-L572
- Dex API GetClient secret response and CreateClient: https://github.com/dexidp/dex/blob/v2.45.1/server/api.go#L53-L104
- Dex static client loading and storage wrapper: https://github.com/dexidp/dex/blob/v2.45.1/cmd/dex/serve.go#L209-L235
- Dex server storage handoff: https://github.com/dexidp/dex/blob/v2.45.1/cmd/dex/serve.go#L363
- Dex static client lookup: https://github.com/dexidp/dex/blob/v2.45.1/storage/static.go#L25-L39
- Dex release workflow tag trigger: https://github.com/dexidp/dex/blob/v2.45.1/.github/workflows/release.yaml#L3-L15
- Dex image checkout, name and tag rules: https://github.com/dexidp/dex/blob/v2.45.1/.github/workflows/artifacts.yaml#L52-L91
- Dex image build from the checked-out tree: https://github.com/dexidp/dex/blob/v2.45.1/.github/workflows/artifacts.yaml#L126-L142
- Dex release job calling the artifacts workflow with `publish: true` and attestation, package and OIDC token write permissions: https://github.com/dexidp/dex/blob/v2.45.1/.github/workflows/release.yaml#L10-L24
- Dex image push only when publishing: https://github.com/dexidp/dex/blob/v2.45.1/.github/workflows/artifacts.yaml#L103-L109
- Dex `cosign sign` of the pushed `ghcr.io` image digest with the GitHub OIDC token: https://github.com/dexidp/dex/blob/v2.45.1/.github/workflows/artifacts.yaml#L145-L148
- Dex build provenance attestation pushed for the `ghcr.io` image digest: https://github.com/dexidp/dex/blob/v2.45.1/.github/workflows/artifacts.yaml#L206-L212
- Redis initial password implementation: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd/commands/admin/redis_initial_password.go#L22-L89
- Redis image protected-mode patch: https://github.com/redis/docker-library-redis/blob/bcbc692165ce2241e194035041c5b5e01d2e1a5f/alpine/Dockerfile#L81-L87
- Redis image entrypoint and command: https://github.com/redis/docker-library-redis/blob/bcbc692165ce2241e194035041c5b5e01d2e1a5f/alpine/Dockerfile#L151-L154
- Redis entrypoint argument handling: https://github.com/redis/docker-library-redis/blob/bcbc692165ce2241e194035041c5b5e01d2e1a5f/alpine/docker-entrypoint.sh#L93-L111
- Docker Official Images `redis:8.2.3-alpine` stanza and `GitRepo` (official-images commit 1ff8d41b352de957628be66246d3af2996948c75, which added the tag; checked October 2026): https://github.com/docker-library/official-images/blob/1ff8d41b352de957628be66246d3af2996948c75/library/redis#L7-L19
- Docker Official Images last revision listing `redis:8.2.3-alpine`, with the same `GitCommit` as at official-images commit 1ff8d41b352de957628be66246d3af2996948c75 (checked October 2026): https://github.com/docker-library/official-images/blob/f80a67f648fe5f70e6708772537c48237dfbe39b/library/redis#L39-L43
- Docker Official Images README (official-images commit 326d6f326e8ed6ea7b66fcc53c6b78dd22334a2d; checked October 2026) on library-file tags being built only through a library-file update or a base-image update, and removed tags staying on Docker Hub unmaintained: https://github.com/docker-library/official-images/blob/326d6f326e8ed6ea7b66fcc53c6b78dd22334a2d/README.md#L369
- Docker Official Images README (official-images commit 326d6f326e8ed6ea7b66fcc53c6b78dd22334a2d; checked October 2026) on Bashbrew fetching `GitRepo` at `GitCommit` and naming tags after the library file: https://github.com/docker-library/official-images/blob/326d6f326e8ed6ea7b66fcc53c6b78dd22334a2d/README.md#L413-L415
- Redis default bind addresses: https://github.com/redis/redis/blob/8.2.3/src/server.h#L142-L143
- Redis default bind initialization: https://github.com/redis/redis/blob/8.2.3/src/server.c#L2199-L2221
- Redis TCP listener bind handoff: https://github.com/redis/redis/blob/8.2.3/src/server.c#L2983-L2996
- Redis optional bind prefix handling: https://github.com/redis/redis/blob/8.2.3/src/server.c#L2638-L2673
- Redis argument copy and title initialization at start-up: https://github.com/redis/redis/blob/8.2.3/src/server.c#L7369-L7408
- Redis title update before listener initialization: https://github.com/redis/redis/blob/8.2.3/src/server.c#L7593-L7607
- Redis process title setter: https://github.com/redis/redis/blob/8.2.3/src/server.c#L7172-L7184
- Redis argument copy and argument-area overwrite: https://github.com/redis/redis/blob/8.2.3/src/setproctitle.c#L164-L316
- Redis environment clearing and rebuild through `setenv()` before the title overwrite: https://github.com/redis/redis/blob/8.2.3/src/setproctitle.c#L87-L161
- Redis glibc detection defining `HAVE_CLEARENV` for the environment rebuild: https://github.com/redis/redis/blob/8.2.3/src/setproctitle.c#L53-L55
- Redis Linux title replacement build switch: https://github.com/redis/redis/blob/8.2.3/src/config.h#L199-L204
- Redis set-proc-title default: https://github.com/redis/redis/blob/8.2.3/src/config.c#L3088
- RBAC default role storage and enforcement handoff: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/rbac/rbac.go#L314-L346
- RBAC policy ConfigMap key names (`policy.default`): https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/rbac/rbac.go#L35-L42
- RBAC ConfigMap loader: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/rbac/rbac.go#L454-L467
- RBAC default-role value: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/rbac/rbac.go#L539-L547
- RBAC default-role enforcement: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/rbac/rbac.go#L399-L425
- RBAC enforcer construction in argocd-server: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L350-L359
- RBAC policy loader start in argocd-server: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L674-L675
- RBAC policy loader callback in argocd-server: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L892-L907
- argocd-server gRPC authentication interceptors: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L961-L985
- argocd-server bug21955 workaround interceptor, first in the unary chain, discarding its `*grpc.UnaryServerInfo` parameter: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L1715 and https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L973-L974
- argocd-server API services receiving the enforcer: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L1029-L1091
- argocd-server gRPC service registration: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L992-L1004
- argocd-server service set types, including `*session.Server`, `*settings.Server` and `*version.Server`: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L1012-L1027
- argocd-server call authentication and claims context: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L1537-L1576
- argocd-server session service authentication override: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/session/session.go#L94-L102
- argocd-server version service authentication override: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/version/version.go#L75-L82
- argocd-server settings service authentication override for Get: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/settings/settings.go#L193-L202
- argocd-server import of the `go-grpc-middleware/v2` auth interceptors: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L37
- Argo CD `go.mod` pin of `go-grpc-middleware/v2` at v2.3.3 (its `go.sum` lines match the recorded download hashes): https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/go.mod#L69
- Argo CD `go.mod` pin of `go-grpc-middleware/providers/prometheus` at v1.1.0 (its `go.sum` lines match the recorded download hashes): https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/go.mod#L68
- Argo CD `go.sum` entries for go-grpc-middleware providers/prometheus v1.1.0 and go-grpc-middleware/v2 v2.3.3, matching the recorded download hashes: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/go.sum#L521-L524
- go-grpc-middleware v2.3.3 (commit 390bcef25adebe4b0c7dbb365230c0a856737afe; checked October 2026) override interface and unary auth interceptor calling a service's `AuthFuncOverride` in place of the default function: https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/interceptors/auth/auth.go#L26-L50
- go-grpc-middleware v2.3.3 (commit 390bcef25adebe4b0c7dbb365230c0a856737afe; checked October 2026) stream auth interceptor calling a service's `AuthFuncOverride` in place of the default function: https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/interceptors/auth/auth.go#L52-L70
- argocd-server unary interceptor chain order: the bug21955 workaround, then logging, then metrics, then auth: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L973-L985
- go-grpc-middleware v2.3.3 logging unary server interceptor built on the shared interceptor (read October 2026 in the module tree extracted from its `go.sum`-matched zip): https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/interceptors/logging/interceptors.go#L209-L212
- go-grpc-middleware v2.3.3 shared unary server interceptor, reading only `info.FullMethod` and calling the handler with the context its reportable returns, writing nothing to `UnaryServerInfo` (read October 2026 in that extraction): https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/interceptors/server.go#L16-L28
- go-grpc-middleware v2.3.3 server call metadata built from the full-method string (read October 2026 in that extraction): https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/interceptors/callmeta.go#L38-L45
- go-grpc-middleware providers/prometheus v1.1.0 metrics unary server interceptor built on the shared v2.3.3 interceptor (read October 2026 in the module tree extracted from its `go.sum`-matched zip): https://github.com/grpc-ecosystem/go-grpc-middleware/blob/providers/prometheus/v1.1.0/providers/prometheus/server_metrics.go#L150-L155
- Argo CD generated session service registration, unary handlers setting `UnaryServerInfo.Server`, and descriptor with no streams: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/pkg/apiclient/session/session.pb.go#L417-L494
- Argo CD generated version service registration, unary handler setting `UnaryServerInfo.Server`, and descriptor with no streams: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/pkg/apiclient/version/version.pb.go#L262-L295
- Argo CD generated settings service registration, unary handlers setting `UnaryServerInfo.Server`, and descriptor with no streams: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/pkg/apiclient/settings/settings.pb.go#L932-L987
- Argo CD `go.mod` requirement of grpc-go v1.81.1 (its `go.sum` lines match the recorded download hashes): https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/go.mod#L115
- Argo CD `go.sum` entries for grpc-go v1.81.1, matching the recorded download hashes: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/go.sum#L1259-L1260
- grpc-go v1.81.1 (commit caf0772c2bcb8bc15d43eb53448e921f34f0b7e8; checked October 2026) nested modules, each directory's own `go.mod`, accounting for the tag clone's git-only directories in the module zip comparison: https://github.com/grpc/grpc-go/blob/v1.81.1/cmd/protoc-gen-go-grpc/go.mod#L1, https://github.com/grpc/grpc-go/blob/v1.81.1/examples/go.mod#L1, https://github.com/grpc/grpc-go/blob/v1.81.1/gcp/observability/go.mod#L1, https://github.com/grpc/grpc-go/blob/v1.81.1/interop/observability/go.mod#L1, https://github.com/grpc/grpc-go/blob/v1.81.1/interop/xds/go.mod#L1, https://github.com/grpc/grpc-go/blob/v1.81.1/security/advancedtls/go.mod#L1, https://github.com/grpc/grpc-go/blob/v1.81.1/stats/opencensus/go.mod#L1 and https://github.com/grpc/grpc-go/blob/v1.81.1/test/tools/go.mod#L1
- go-grpc-middleware v2.3.3 (commit 390bcef25adebe4b0c7dbb365230c0a856737afe; checked October 2026) nested modules, each directory's own `go.mod`, accounting for the tag clone's git-only directories in the module zip comparison: https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/.bingo/go.mod#L1, https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/examples/go.mod#L1, https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/interceptors/logging/examples/go.mod#L1 and https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/providers/prometheus/go.mod#L1
- go-grpc-middleware providers/prometheus v1.1.0 (commit 53040665d19bab33e444905822557433511bb981; checked October 2026) repository-root `LICENSE`, the zip-only file in the module zip comparison, since the tag's `providers/prometheus` directory has none: https://github.com/grpc-ecosystem/go-grpc-middleware/blob/providers/prometheus/v1.1.0/LICENSE
- Go module zip construction at go1.26.5 (read October 2026 in a local go1.26.5 toolchain tree, not compared with upstream; the Go version the proxy built the module zips with is not recorded): [the go command adds the repository-root LICENSE to the zip of a subdirectory module that has none](https://github.com/golang/go/blob/go1.26.5/src/cmd/go/internal/modfetch/coderepo.go#L1170-L1175); [module zip creation omits files in any directory below the module root that holds its own go.mod](https://github.com/golang/go/blob/go1.26.5/src/cmd/vendor/golang.org/x/mod/zip/zip.go#L232-L298).
- grpc-go v1.81.1 (commit caf0772c2bcb8bc15d43eb53448e921f34f0b7e8; checked October 2026) `ChainUnaryInterceptor` server option: https://github.com/grpc/grpc-go/blob/v1.81.1/server.go#L481-L489
- grpc-go v1.81.1 (commit caf0772c2bcb8bc15d43eb53448e921f34f0b7e8; checked October 2026) `NewServer` combining the configured interceptors: https://github.com/grpc/grpc-go/blob/v1.81.1/server.go#L691-L710
- grpc-go v1.81.1 (commit caf0772c2bcb8bc15d43eb53448e921f34f0b7e8; checked October 2026) service registration storing the implementation: https://github.com/grpc/grpc-go/blob/v1.81.1/server.go#L757-L793
- grpc-go v1.81.1 (commit caf0772c2bcb8bc15d43eb53448e921f34f0b7e8; checked October 2026) unary interceptor chain passing one `UnaryServerInfo` to every interceptor: https://github.com/grpc/grpc-go/blob/v1.81.1/server.go#L1212-L1245
- grpc-go v1.81.1 (commit caf0772c2bcb8bc15d43eb53448e921f34f0b7e8; checked October 2026) unary call passing the stored implementation and the combined interceptor to the method handler: https://github.com/grpc/grpc-go/blob/v1.81.1/server.go#L1430
- grpc-go v1.81.1 (commit caf0772c2bcb8bc15d43eb53448e921f34f0b7e8; checked October 2026) dispatch of a registered service's unary method: https://github.com/grpc/grpc-go/blob/v1.81.1/server.go#L1853-L1857
- grpc-go v1.81.1 (commit caf0772c2bcb8bc15d43eb53448e921f34f0b7e8; checked October 2026) `UnaryServerInfo.Server` documented as the read-only service implementation the user provides: https://github.com/grpc/grpc-go/blob/v1.81.1/interceptor.go#L65-L72
- Application List RBAC filter: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/application/application.go#L288-L330
- Application Create RBAC check: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/application/application.go#L348-L356
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
- Argo CD Redis image rename in the base kustomization: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/redis/kustomization.yaml#L12-L14
- Argo CD Redis image in the rendered install manifest: https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/install.yaml#L32485
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
- Argo CD repo-server bind defaults (v3.5.3; commit c9c369efcc5b2a0bd720803f8d14a1c3eaddf579; checked October 2026): https://github.com/argoproj/argo-cd/blob/v3.5.3/common/common.go#L89-L90
- Argo CD repo-server listener flags and default wiring (v3.5.3; commit c9c369efcc5b2a0bd720803f8d14a1c3eaddf579; checked October 2026): https://github.com/argoproj/argo-cd/blob/v3.5.3/cmd/argocd-repo-server/commands/argocd_repo_server.go#L257-L260
- Argo CD Redis password initializer command (v3.5.3; commit c9c369efcc5b2a0bd720803f8d14a1c3eaddf579; checked October 2026): https://github.com/argoproj/argo-cd/blob/v3.5.3/cmd/argocd/commands/admin/redis_initial_password.go#L41-L42
- Argo CD additive default-role enforcement (v3.5.3; commit c9c369efcc5b2a0bd720803f8d14a1c3eaddf579; checked October 2026): https://github.com/argoproj/argo-cd/blob/v3.5.3/util/rbac/rbac.go#L401-L406
- Argo CD default-role ConfigMap loading (v3.5.3; commit c9c369efcc5b2a0bd720803f8d14a1c3eaddf579; checked October 2026): https://github.com/argoproj/argo-cd/blob/v3.5.3/util/rbac/rbac.go#L540-L541


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- argo: Argo CD v3.5.3 source (c9c369efcc5b2a0bd720803f8d14a1c3eaddf579)
- flux-oidc: Flux OIDC introduction (v2.9)
- argo-docs: Argo CD documentation (unknown)
- flux: Flux documentation (unknown)
- dex: Dex source (v2.45.1)
- redis-image: docker-library-redis v8.2.3 source (bcbc692165ce2241e194035041c5b5e01d2e1a5f)
- redis-source: Redis source (8.2.3)
- curl: curl (curl-8_14_1)
- python: Python documentation (unknown)
- grpc-middleware: go-grpc-middleware source (v2.3.3)
- grpc-middleware-prom: go-grpc-middleware providers/prometheus source (v1.1.0)
- grpc-go: grpc-go v1.81.1 source (caf0772c2bcb8bc15d43eb53448e921f34f0b7e8)
- official-images: Docker Official Images library definitions (1ff8d41b352de957628be66246d3af2996948c75)
- official-images-docs: Docker Official Images README (326d6f326e8ed6ea7b66fcc53c6b78dd22334a2d)

Claims (full source mapping in the JSON block below):

- git-boundary (REASONED; argo-docs, flux): Repository writers exercise reconciliation permissions; review platform changes, separate tenants and scope credentials.
- secret-storage (REASONED; argo-docs, flux): Protect bootstrap, registry, cluster, webhook and decryption credentials; commit only encrypted secrets and keep SOPS/age keys out of Git.
- egress (REASONED; argo-docs, flux): Restrict fetch, API, identity and notification egress; Argo repository allowlists do not constrain remote bases or Helm dependencies.
- argo-bootstrap (REASONED; argo-docs): Rotate the initial admin password before deleting argocd-initial-admin-secret; deletion alone does not rotate it.
- argo-sso (REASONED; argo-docs): The built-in admin is unrestricted; configure named SSO roles and IdP MFA, then set admin.enabled=false.
- argo-origin (REASONED; argo-docs, argo): Keep the ClusterIP origin private behind authenticated TLS and protect both REST/browser and CLI/gRPC routes.
- argo-server (REASONED; argo): Server defaults to 0.0.0.0:8080; the Service maps 80 and 443 to it.
- argo-tls (REASONED; argo, argo-docs): Server --insecure/server.insecure defaults false and disables backend TLS, not authentication; use only behind protected TLS termination.
- argo-client-tls (REASONED; argo-docs): argocd login --insecure skips client certificate verification; the server initially uses a self-signed certificate.
- argo-metrics (REASONED; argo): Server HTTP metrics on 8083 are unauthenticated and bind to --address, not --metrics-address.
- argo-profiler (REASONED; argo): Server and repo-server pprof paths return 401 unless the profiler file contains exactly true with no newline; enabled profiling has no caller authentication.
- argo-profiler-file (REASONED; argo): ARGOCD_ENABLE_PROFILER_FILE_PATH defaults to /home/argocd/params/profiler.enabled; the server mounts ConfigMap key server.profile.enabled there.
- repo-grpc (REASONED; argo): Repo-server gRPC binds 0.0.0.0:8081 with TLS by default; mTLS is skipped without the client CA, separate from the serving certificate.
- repo-http (REASONED; argo): Repo-server HTTP metrics and health bind 0.0.0.0:8084 without an authentication wrapper.
- repo-limits (REASONED; argo): Repo-server requires verified client certificates with a loaded client CA; missing or unstatable serving files trigger a session self-signed certificate, while an invalid present pair errors. No authorization interceptor appears, and the registered service handlers read no caller identity, so, from this source reading, any client completing the transport handshake can call its methods.
- controller-metrics (REASONED; argo): Application-controller metrics, health and file-gated pprof share one plain-HTTP mux on a hardcoded 0.0.0.0 host; --metrics-port (default 8082) sets only the port, and the command defines no bind-address flag.
- applicationset-webhook (REASONED; argo): ApplicationSet webhook binds :7000; its container and Service declare 7000.
- applicationset-metrics (REASONED; argo): ApplicationSet metrics bind :8080; its container and Service declare 8080.
- applicationset-health (REASONED; argo): ApplicationSet health probes bind :8081 without a container or Service port declaration; missing declarations do not close sockets.
- notifications (REASONED; argo): Notifications HTTP metrics bind 0.0.0.0:9001 without authentication; a metrics Service and TCP liveness probe exist without containerPort.
- dex-http (REASONED; argo): Dex starts only with nonempty generated configuration; HTTP defaults to TLS on 0.0.0.0:5556 using /tmp/tls.crt and /tmp/tls.key.
- dex-grpc (REASONED; argo, dex): Generated Dex gRPC uses 0.0.0.0:5557 without TLS or client-auth settings; Dex v2.45.1 source sets no transport credentials or authentication interceptor for this configuration, its API handlers read no caller identity, and GetClient returns client secrets, including Argo CD's static client; this assumes the deployed ghcr.io/dexidp/dex:v2.45.1 tag was built from Dex v2.45.1.
- dex-image (REASONED; argo, dex): Dex v2.45.1's release workflow builds pushed vX.Y.Z tags from the checked-out tree, tags the alpine variant through its semver rule, and, when publishing, cosign-signs and attests the pushed ghcr.io digest; Argo CD's base names ghcr.io/dexidp/dex:v2.45.1, no signature or attestation was verified, and whether that published image came from this workflow is not established.
- dex-telemetry (REASONED; argo): Dex telemetry uses HTTP on 0.0.0.0:5558; all three Dex ports have Services.
- redis-password (REASONED; argo, redis-image, redis-source): Redis receives --requirepass from argocd-redis/auth; secret-init generates and checks that Secret. The redis:8.2.3-alpine tag, taken as built from docker-library-redis v8.2.3, uses Redis wildcard bind defaults and patches protected mode off; this holds for the deployed public.ecr.aws image only if it was built from that recipe.
- redis-image-name (REASONED; argo, official-images, official-images-docs): The base Redis kustomization renames redis to public.ecr.aws/docker/library/redis, keeping 8.2.3-alpine, as the rendered install.yaml shows; Docker Official Images lists redis:8.2.3-alpine as built from docker-library-redis bcbc6921's alpine directory, but the pinned sources do not establish which recipe the ECR registry tag was built from.
- redis-argv (REASONED; argo, redis-source): Redis 8.2.3 has no password-specific redaction of its start-up arguments; on Linux, with set-proc-title at its default yes, its first title update zeroes the original argument area and any environment strings directly after it before listeners open, leaving heap and setenv() copies; whether that clears the REDIS_PASSWORD environment copy is not established.
- redis-tls (REASONED; argo): Base manifests configure no Redis TLS and the Argo Redis client defaults --redis-use-tls=false; protect traffic, Secret and cache.
- component-policies (REASONED; argo): Base policies restrict repo gRPC, Redis and Dex callers by component; enforcement needs a supporting CNI.
- broad-policies (REASONED; argo): Server policy allows all ingress; other metrics and ApplicationSet webhook allowances admit every namespace. Narrow existing additive allowances and egress separately.
- argo-anonymous (REASONED; argo, argo-docs): users.anonymous.enabled defaults off; anonymous callers otherwise inherit policy.default.
- argo-disable-auth (REASONED; argo): server.disable.auth defaults false; inspect effective args and environment because anonymous-off does not compensate for disabled authentication.
- argo-default-role (REASONED; argo, argo-docs): Base RBAC ConfigMap omits policy.default; the inspected loader supplies an empty role to the enforcer, which skips its additive default-role check. Default-role grants are additive and cannot be revoked by a later subject rule; define scoped policy.csv roles and group mappings.
- argo-rbac-wiring (REASONED; argo): argocd-server builds its enforcer for argocd-rbac-cm with the built-in policy and a claims enforcer, starts the ConfigMap loader, authenticates gRPC calls by default and stores claims, and passes the enforcer to API services; for example, application List filters on get and Create checks create. Per-handler coverage and runtime overrides remain unverified.
- argo-auth-overrides (REASONED; argo, grpc-middleware, grpc-go, grpc-middleware-prom): argocd-server's gRPC interceptors authenticate calls by default unless auth is disabled, but, from this source reading, the session, version and settings services override that function for every method and accept unauthenticated callers, settings only for Get; pinned go-grpc-middleware v2.3.3 calls an override on the service value grpc-go v1.81.1 passes. As read, the interceptors ahead keep it.
- argo-auth-chain-ahead (REASONED; argo, grpc-middleware, grpc-middleware-prom): Ahead of auth, argocd-server's unary chain runs the bug21955 workaround, v2.3.3 logging and providers/prometheus v1.1.0 metrics interceptors; read in the extracted modules, the two module interceptors wrap one shared v2.3.3 interceptor that reads only info.FullMethod and calls the handler with the context its reportable returns, and none of the three writes to UnaryServerInfo or its Server field.
- argo-grpc-middleware-pin (REASONED; argo, grpc-middleware, grpc-middleware-prom, grpc-go): Argo CD's go.sum lines for go-grpc-middleware/v2 v2.3.3, providers/prometheus v1.1.0 and grpc-go v1.81.1 match hashes a go mod download recorded over their zips on 2026-10-23. A diff -rq of each extracted zip against its tag's module directory reported no differing file; one-sided paths are or hold nested modules, or are the root LICENSE in the prometheus zip; no h1: hash was recomputed from git.
- argo-webhook (REASONED; argo-docs): /api/webhook accepts unauthenticated refresh events without a shared secret; configure one to limit spoofed reconciliation and resource exhaustion.
- argo-projects (REASONED; argo-docs): Restrict AppProjects including the built-in default project; project constraints do not reduce a compromised controller's Kubernetes credentials.
- argo-cluster-rbac (REASONED; argo-docs): Reduce controller and registered-cluster argocd-manager write permissions to needed namespaces/resources while retaining required read access.
- flux-api (REASONED; flux): Flux has no standalone management login/API; Kubernetes authenticates its custom-resource operations, while separate dashboards need their own controls.
- flux-bootstrap (REASONED; flux): GitHub bootstrap --token-auth retains a PAT in flux-system; --token-auth=false creates a read-only SSH deploy key by default. Protect bootstrap input and Secrets.
- flux-writeback (REASONED; flux): Image automation needs Git write access, including --read-write-key=true for the bootstrap key; scope the repository and protect update branches and objects.
- flux-artifacts (REASONED; flux): Source-controller serves fetched artifacts over internal HTTP; enforced NetworkPolicy, not ClusterIP alone, isolates them.
- flux-receiver-port (REASONED; flux): Webhook receiver listens on 9292 behind Service port 80; external exposure needs a route and TLS termination.
- flux-receiver-types (REASONED; flux): generic validates nothing; generic-hmac, GitHub, Bitbucket and Nexus use HMAC, while gitlab compares X-Gitlab-Token.
- flux-oidc (REASONED; flux, flux-oidc): generic-oidc, introduced in Flux 2.9, rejects secretRef and validates bearer tokens; constrain issuer validations and audience, whose default is notification-controller.
- flux-rbac (REASONED; flux): Only kustomize-controller and helm-controller hold cluster-admin; other controllers still have meaningful permissions including Secret access.
- flux-lockdown (REASONED; flux): Use scoped reconciliation ServiceAccounts, --no-cross-namespace-refs and --no-remote-bases; --default-service-account fills an omission, not an explicit serviceAccountName.
- verify-argo (REASONED; argo-docs, argo, curl): Anonymous application listing should fail with 401 while a valid token lists the expected application; repeat at origin and CLI/gRPC and inspect effective RBAC.
- verify-bootstrap (REASONED; argo-docs): Absence of the bootstrap Secret proves removal of that material, not password rotation.
- verify-inventory (REASONED; argo, flux): Inventory Services, routes, host ports, policies and component sockets; node-local ss and policy objects alone do not establish cluster isolation.
- verify-repo-metrics (REASONED; argo): Base policy permits HTTP 200 metrics to monitoring and unrelated pods; narrowed policy should admit only monitoring, with a successful positive control.
- verify-server-metrics (REASONED; argo): Repeat on server 8083: only authorized monitoring should receive metrics after narrowing ingress; a failed control is inconclusive.
- verify-profiler (REASONED; argo): From an allowed pod, pprof cmdline should return 401 disabled, 200 for exact true, then 401 for true plus newline; keep metrics as control.
- verify-flux (REASONED; flux, python, curl): Identical generic-hmac bodies without and with X-Signature should be rejected and accepted with reconciliation; status is type/version dependent. The cited curl curl-8_14_1 lines show --data-binary posting data exactly as specified, preserving newlines and carriage returns that --data strips from @file input, reading @- from stdin and @filename from a file, and posting like --data's POST request.
- verify-receiver-status (REASONED; flux): Read receiver name and Ready condition without exposing webhookPath or condition messages; origin checks distinguish receiver rejection from proxy rejection.

````json
{
  "schema": 1,
  "checked": "2026-10-19",
  "documentation_checked": "2026-09",
  "body_sha256": "40a6f5bd491fd5b2f26d1a1101eb0e50083b114c4352cdd97b033de2dc412f60",
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
        "s0f7f1b3404d9": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/config/argocd-rbac-cm.yaml#L1-L7",
        "s85445da68ce7": "https://github.com/argoproj/argo-cd/blob/v3.5.3/common/common.go#L89-L90",
        "s357d253fc789": "https://github.com/argoproj/argo-cd/blob/v3.5.3/cmd/argocd-repo-server/commands/argocd_repo_server.go#L257-L260",
        "s9df1243dde48": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd-application-controller/commands/argocd_application_controller.go#L192-L209",
        "s0abbc26d61e4": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd-application-controller/commands/argocd_application_controller.go#L272-L273",
        "sfcaf2e03154d": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/reposerver/server.go#L49-L85",
        "s25a5da2c5e7c": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/reposerver/server.go#L94-L150",
        "s73653423b85d": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/tls/tls.go#L428-L506",
        "s7c7bf274e3ef": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/dex/argocd-dex-server-deployment.yaml#L38-L42",
        "s08939ffb906f": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/cmd/argocd/commands/admin/redis_initial_password.go#L22-L89",
        "s3fcdf1601776": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/rbac/rbac.go#L454-L467",
        "se987196f20c7": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/rbac/rbac.go#L539-L547",
        "s3cb98aa5348d": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/rbac/rbac.go#L399-L425",
        "s9bfcf07a6bcc": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/rbac/rbac.go#L314-L346",
        "s32323471d785": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/util/rbac/rbac.go#L35-L42",
        "sb5104fa6ab35": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/controller/appcontroller.go#L321-L323",
        "sbe428a31febd": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/controller/appcontroller.go#L996",
        "s326dd2512e89": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/controller/metrics/metrics.go#L187-L220",
        "s5e687a6ecca2": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/reposerver/repository/repository.go#L1385-L1401",
        "s5a0cd7608f62": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/base/redis/kustomization.yaml#L12-L14",
        "s9a8d62f416f8": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/manifests/install.yaml#L32485",
        "s0cfce81f2017": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L350-L359",
        "s19cc383608d3": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L674-L675",
        "s44b42ce894fe": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L892-L907",
        "s751b24797922": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L961-L985",
        "s0a3fee6c3102": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L1029-L1091",
        "s2bf01b29602c": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L1537-L1576",
        "s11dddf48ac64": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/application/application.go#L288-L330",
        "sab95c8799d63": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/application/application.go#L348-L356",
        "s27142bd7b0a7": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/session/session.go#L94-L102",
        "sab27d21a6f4f": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/version/version.go#L75-L82",
        "sdb49a2a191ec": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/settings/settings.go#L193-L202",
        "sa198755acef1": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/reposerver/repository/repository.go#L87-L106",
        "sdc5ce38b60a4": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/reposerver/repository/repository.go#L227-L247",
        "s63b5417fbbd0": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/reposerver/repository/repository.go#L631-L706",
        "s19e9d1a1d4d2": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L37",
        "sd94bce49cbb4": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/go.mod#L69",
        "sde82351720c4": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L992-L1004",
        "s6b0b042ccc35": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L1012-L1027",
        "sabf68ca51b16": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/pkg/apiclient/session/session.pb.go#L417-L494",
        "s0f7c55b64e47": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/pkg/apiclient/version/version.pb.go#L262-L295",
        "s074e2945a0f4": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/pkg/apiclient/settings/settings.pb.go#L932-L987",
        "seed01984c64f": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/go.mod#L115",
        "s6d4515def993": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L1715",
        "sc491b902058a": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/go.mod#L68",
        "s774ef5b5febe": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/go.sum#L521-L524",
        "s984568b27d03": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/go.sum#L1259-L1260",
        "se1742d8dba7c": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L973-L985",
        "s73f95d35b6a3": "https://github.com/argoproj/argo-cd/blob/c9c369efcc5b2a0bd720803f8d14a1c3eaddf579/server/server.go#L973-L974"
      }
    },
    "flux-oidc": {
      "name": "Flux OIDC introduction",
      "basis": "v2.9",
      "sources": {
        "s1ea193b2b3cc": "https://fluxcd.io/blog/2026/06/flux-v2.9.0/"
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
    "dex": {
      "name": "Dex source",
      "basis": "v2.45.1",
      "sources": {
        "s3b9512b79dea": "https://github.com/dexidp/dex/blob/v2.45.1/cmd/dex/serve.go#L151-L199",
        "s46eb2feaa84f": "https://github.com/dexidp/dex/blob/v2.45.1/cmd/dex/serve.go#L553-L572",
        "s55b453f266f3": "https://github.com/dexidp/dex/blob/v2.45.1/cmd/dex/config.go#L255-L265",
        "s7cc71fede65a": "https://github.com/dexidp/dex/blob/v2.45.1/server/api.go#L53-L104",
        "s4da116cf17b5": "https://github.com/dexidp/dex/blob/v2.45.1/cmd/dex/serve.go#L209-L235",
        "s68762857b08b": "https://github.com/dexidp/dex/blob/v2.45.1/cmd/dex/serve.go#L363",
        "s397fba865163": "https://github.com/dexidp/dex/blob/v2.45.1/storage/static.go#L25-L39",
        "sb068439020cf": "https://github.com/dexidp/dex/blob/v2.45.1/.github/workflows/release.yaml#L3-L15",
        "s94b27f414052": "https://github.com/dexidp/dex/blob/v2.45.1/.github/workflows/artifacts.yaml#L52-L91",
        "sf5d6527e4e92": "https://github.com/dexidp/dex/blob/v2.45.1/.github/workflows/artifacts.yaml#L126-L142",
        "s1e1a36027f42": "https://github.com/dexidp/dex/blob/v2.45.1/.github/workflows/release.yaml#L10-L24",
        "s5b7f1f0efe07": "https://github.com/dexidp/dex/blob/v2.45.1/.github/workflows/artifacts.yaml#L103-L109",
        "s53fa204808c2": "https://github.com/dexidp/dex/blob/v2.45.1/.github/workflows/artifacts.yaml#L145-L148",
        "s5fca5a23981a": "https://github.com/dexidp/dex/blob/v2.45.1/.github/workflows/artifacts.yaml#L206-L212"
      }
    },
    "redis-image": {
      "name": "docker-library-redis v8.2.3 source",
      "basis": "bcbc692165ce2241e194035041c5b5e01d2e1a5f",
      "sources": {
        "s67a2f7553c9a": "https://github.com/redis/docker-library-redis/blob/bcbc692165ce2241e194035041c5b5e01d2e1a5f/alpine/Dockerfile#L81-L87",
        "s30643c91686d": "https://github.com/redis/docker-library-redis/blob/bcbc692165ce2241e194035041c5b5e01d2e1a5f/alpine/Dockerfile#L151-L154",
        "sd04db8453288": "https://github.com/redis/docker-library-redis/blob/bcbc692165ce2241e194035041c5b5e01d2e1a5f/alpine/docker-entrypoint.sh#L93-L111"
      }
    },
    "redis-source": {
      "name": "Redis source",
      "basis": "8.2.3",
      "sources": {
        "s667fc16bf18f": "https://github.com/redis/redis/blob/8.2.3/src/server.h#L142-L143",
        "saa497d27f72f": "https://github.com/redis/redis/blob/8.2.3/src/server.c#L2199-L2221",
        "s0f96763525b7": "https://github.com/redis/redis/blob/8.2.3/src/server.c#L2638-L2673",
        "s9b50a7c52721": "https://github.com/redis/redis/blob/8.2.3/src/server.c#L2983-L2996",
        "sfc4931194892": "https://github.com/redis/redis/blob/8.2.3/src/server.c#L7369-L7408",
        "sad31935cbfd5": "https://github.com/redis/redis/blob/8.2.3/src/server.c#L7593-L7607",
        "s798e4cb2e0da": "https://github.com/redis/redis/blob/8.2.3/src/server.c#L7172-L7184",
        "s514f74f25aeb": "https://github.com/redis/redis/blob/8.2.3/src/setproctitle.c#L164-L316",
        "sc2c8077e667c": "https://github.com/redis/redis/blob/8.2.3/src/config.h#L199-L204",
        "s41802d8e64f5": "https://github.com/redis/redis/blob/8.2.3/src/config.c#L3088",
        "s8623193029f8": "https://github.com/redis/redis/blob/8.2.3/src/setproctitle.c#L87-L161",
        "sa8561a476c47": "https://github.com/redis/redis/blob/8.2.3/src/setproctitle.c#L53-L55"
      }
    },
    "curl": {
      "name": "curl",
      "basis": "curl-8_14_1",
      "sources": {
        "s3db522258e44": "https://raw.githubusercontent.com/curl/curl/curl-8_14_1/docs/cmdline-opts/header.md",
        "s9537bb790553": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/data-binary.md#L4-L32",
        "sd3b039bafbf6": "https://github.com/curl/curl/blob/curl-8_14_1/docs/cmdline-opts/data.md#L4-L49"
      }
    },
    "python": {
      "name": "Python documentation",
      "basis": "unknown",
      "sources": {
        "s7a54556e5dac": "https://docs.python.org/3/library/hmac.html",
        "s31fccd7d50e5": "https://docs.python.org/3/library/sys.html#sys.stdin"
      }
    },
    "grpc-middleware": {
      "name": "go-grpc-middleware source",
      "basis": "v2.3.3",
      "sources": {
        "s9ec5783f5bab": "https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/interceptors/auth/auth.go#L26-L50",
        "s4413e7e06e93": "https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/interceptors/auth/auth.go#L52-L70",
        "s38deb43fcd65": "https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/interceptors/logging/interceptors.go#L209-L212",
        "se4ca59a60a0e": "https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/interceptors/server.go#L16-L28",
        "sf6f4e6a293d3": "https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/interceptors/callmeta.go#L38-L45",
        "s71c21e4cdbaf": "https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/.bingo/go.mod#L1",
        "sa4598ce2f73d": "https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/examples/go.mod#L1",
        "sf540911a60b0": "https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/interceptors/logging/examples/go.mod#L1",
        "s7225a1c63c9c": "https://github.com/grpc-ecosystem/go-grpc-middleware/blob/v2.3.3/providers/prometheus/go.mod#L1"
      }
    },
    "grpc-middleware-prom": {
      "name": "go-grpc-middleware providers/prometheus source",
      "basis": "v1.1.0",
      "sources": {
        "sbb37d9bfd450": "https://github.com/grpc-ecosystem/go-grpc-middleware/blob/providers/prometheus/v1.1.0/providers/prometheus/server_metrics.go#L150-L155",
        "s11f89487025a": "https://github.com/grpc-ecosystem/go-grpc-middleware/blob/providers/prometheus/v1.1.0/LICENSE"
      }
    },
    "grpc-go": {
      "name": "grpc-go v1.81.1 source",
      "basis": "caf0772c2bcb8bc15d43eb53448e921f34f0b7e8",
      "sources": {
        "sd6f265b97017": "https://github.com/grpc/grpc-go/blob/v1.81.1/server.go#L481-L489",
        "s7f712ff2fcd0": "https://github.com/grpc/grpc-go/blob/v1.81.1/server.go#L691-L710",
        "se04d5024dfba": "https://github.com/grpc/grpc-go/blob/v1.81.1/server.go#L757-L793",
        "s9b3b1bb96432": "https://github.com/grpc/grpc-go/blob/v1.81.1/server.go#L1212-L1245",
        "se661d06557fb": "https://github.com/grpc/grpc-go/blob/v1.81.1/server.go#L1430",
        "s9e56a9214565": "https://github.com/grpc/grpc-go/blob/v1.81.1/server.go#L1853-L1857",
        "sb4ab78a762fd": "https://github.com/grpc/grpc-go/blob/v1.81.1/interceptor.go#L65-L72",
        "s342208064b4f": "https://github.com/grpc/grpc-go/blob/v1.81.1/cmd/protoc-gen-go-grpc/go.mod#L1",
        "s90e76e9ef9cf": "https://github.com/grpc/grpc-go/blob/v1.81.1/examples/go.mod#L1",
        "sb410d3246985": "https://github.com/grpc/grpc-go/blob/v1.81.1/gcp/observability/go.mod#L1",
        "s5b23c5ca5576": "https://github.com/grpc/grpc-go/blob/v1.81.1/interop/observability/go.mod#L1",
        "s763fdf228f24": "https://github.com/grpc/grpc-go/blob/v1.81.1/interop/xds/go.mod#L1",
        "s53ec4d2497b4": "https://github.com/grpc/grpc-go/blob/v1.81.1/security/advancedtls/go.mod#L1",
        "s11e1ee6bc55c": "https://github.com/grpc/grpc-go/blob/v1.81.1/stats/opencensus/go.mod#L1",
        "s144519a15f3a": "https://github.com/grpc/grpc-go/blob/v1.81.1/test/tools/go.mod#L1"
      }
    },
    "official-images": {
      "name": "Docker Official Images library definitions",
      "basis": "1ff8d41b352de957628be66246d3af2996948c75",
      "sources": {
        "s385d77aa2bdf": "https://github.com/docker-library/official-images/blob/1ff8d41b352de957628be66246d3af2996948c75/library/redis#L7-L19",
        "s8ab40bf97d9f": "https://github.com/docker-library/official-images/blob/f80a67f648fe5f70e6708772537c48237dfbe39b/library/redis#L39-L43"
      }
    },
    "official-images-docs": {
      "name": "Docker Official Images README",
      "basis": "326d6f326e8ed6ea7b66fcc53c6b78dd22334a2d",
      "sources": {
        "s79cc3f715062": "https://github.com/docker-library/official-images/blob/326d6f326e8ed6ea7b66fcc53c6b78dd22334a2d/README.md#L369",
        "sb8f4661bdd1f": "https://github.com/docker-library/official-images/blob/326d6f326e8ed6ea7b66fcc53c6b78dd22334a2d/README.md#L413-L415"
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
    "repo-grpc": {"text": "Repo-server gRPC binds 0.0.0.0:8081 with TLS by default; mTLS is skipped without the client CA, separate from the serving certificate.", "components": ["argo"], "sources": ["argo:s9bca471ac6d9", "argo:s4bbc848d9923", "argo:sf4dd846c82c4", "argo:s85445da68ce7", "argo:s357d253fc789"], "status": "REASONED"},
    "repo-http": {"text": "Repo-server HTTP metrics and health bind 0.0.0.0:8084 without an authentication wrapper.", "components": ["argo"], "sources": ["argo:s98b27313f615", "argo:s9bca471ac6d9", "argo:sf4dd846c82c4", "argo:s85445da68ce7", "argo:s357d253fc789"], "status": "REASONED"},
    "repo-limits": {"text": "Repo-server requires verified client certificates with a loaded client CA; missing or unstatable serving files trigger a session self-signed certificate, while an invalid present pair errors. No authorization interceptor appears, and the registered service handlers read no caller identity, so, from this source reading, any client completing the transport handshake can call its methods.", "components": ["argo"], "sources": ["argo:sfcaf2e03154d", "argo:s25a5da2c5e7c", "argo:s73653423b85d", "argo:s5e687a6ecca2", "argo:sa198755acef1", "argo:sdc5ce38b60a4", "argo:s63b5417fbbd0"], "status": "REASONED"},
    "controller-metrics": {"text": "Application-controller metrics, health and file-gated pprof share one plain-HTTP mux on a hardcoded 0.0.0.0 host; --metrics-port (default 8082) sets only the port, and the command defines no bind-address flag.", "components": ["argo"], "sources": ["argo:sf98b6bc4f5dc", "argo:s9df1243dde48", "argo:s0abbc26d61e4", "argo:sf4dd846c82c4", "argo:sb5104fa6ab35", "argo:sbe428a31febd", "argo:s326dd2512e89", "argo:sc52bbd14bff4"], "status": "REASONED"},
    "applicationset-webhook": {"text": "ApplicationSet webhook binds :7000; its container and Service declare 7000.", "components": ["argo"], "sources": ["argo:s49a7c83d9371", "argo:s97a588d8a83f"], "status": "REASONED"},
    "applicationset-metrics": {"text": "ApplicationSet metrics bind :8080; its container and Service declare 8080.", "components": ["argo"], "sources": ["argo:s49a7c83d9371", "argo:s97a588d8a83f"], "status": "REASONED"},
    "applicationset-health": {"text": "ApplicationSet health probes bind :8081 without a container or Service port declaration; missing declarations do not close sockets.", "components": ["argo"], "sources": ["argo:s49a7c83d9371"], "status": "REASONED"},
    "notifications": {"text": "Notifications HTTP metrics bind 0.0.0.0:9001 without authentication; a metrics Service and TCP liveness probe exist without containerPort.", "components": ["argo"], "sources": ["argo:s0a85b38dfca8", "argo:s5e141e32ed9c"], "status": "REASONED"},
    "dex-http": {"text": "Dex starts only with nonempty generated configuration; HTTP defaults to TLS on 0.0.0.0:5556 using /tmp/tls.crt and /tmp/tls.key.", "components": ["argo"], "sources": ["argo:s8efcc66f9cb4", "argo:s30c391d9dc23", "argo:se477de2fdfa0"], "status": "REASONED"},
    "dex-grpc": {"text": "Generated Dex gRPC uses 0.0.0.0:5557 without TLS or client-auth settings; Dex v2.45.1 source sets no transport credentials or authentication interceptor for this configuration, its API handlers read no caller identity, and GetClient returns client secrets, including Argo CD's static client; this assumes the deployed ghcr.io/dexidp/dex:v2.45.1 tag was built from Dex v2.45.1.", "components": ["argo", "dex"], "sources": ["argo:se477de2fdfa0", "argo:s56c41c02ba8b", "argo:s7c7bf274e3ef", "dex:s3b9512b79dea", "dex:s46eb2feaa84f", "dex:s55b453f266f3", "dex:s7cc71fede65a", "dex:s4da116cf17b5", "dex:s68762857b08b", "dex:s397fba865163"], "status": "REASONED"},
    "dex-image": {"text": "Dex v2.45.1's release workflow builds pushed vX.Y.Z tags from the checked-out tree, tags the alpine variant through its semver rule, and, when publishing, cosign-signs and attests the pushed ghcr.io digest; Argo CD's base names ghcr.io/dexidp/dex:v2.45.1, no signature or attestation was verified, and whether that published image came from this workflow is not established.", "components": ["argo", "dex"], "sources": ["argo:s7c7bf274e3ef", "dex:sb068439020cf", "dex:s94b27f414052", "dex:sf5d6527e4e92", "dex:s1e1a36027f42", "dex:s5b7f1f0efe07", "dex:s53fa204808c2", "dex:s5fca5a23981a"], "status": "REASONED"},
    "dex-telemetry": {"text": "Dex telemetry uses HTTP on 0.0.0.0:5558; all three Dex ports have Services.", "components": ["argo"], "sources": ["argo:se477de2fdfa0", "argo:s56c41c02ba8b"], "status": "REASONED"},
    "redis-password": {"text": "Redis receives --requirepass from argocd-redis/auth; secret-init generates and checks that Secret. The redis:8.2.3-alpine tag, taken as built from docker-library-redis v8.2.3, uses Redis wildcard bind defaults and patches protected mode off; this holds for the deployed public.ecr.aws image only if it was built from that recipe.", "components": ["argo", "redis-image", "redis-source"], "sources": ["argo:s996c72c5db28", "argo:s08939ffb906f", "argo:s5a0cd7608f62", "argo:s9a8d62f416f8", "redis-image:s67a2f7553c9a", "redis-image:s30643c91686d", "redis-image:sd04db8453288", "redis-source:s667fc16bf18f", "redis-source:saa497d27f72f", "redis-source:s0f96763525b7", "redis-source:s9b50a7c52721"], "status": "REASONED"},
    "redis-image-name": {"text": "The base Redis kustomization renames redis to public.ecr.aws/docker/library/redis, keeping 8.2.3-alpine, as the rendered install.yaml shows; Docker Official Images lists redis:8.2.3-alpine as built from docker-library-redis bcbc6921's alpine directory, but the pinned sources do not establish which recipe the ECR registry tag was built from.", "components": ["argo", "official-images", "official-images-docs"], "sources": ["argo:s996c72c5db28", "argo:s5a0cd7608f62", "argo:s9a8d62f416f8", "official-images:s385d77aa2bdf", "official-images:s8ab40bf97d9f", "official-images-docs:sb8f4661bdd1f", "official-images-docs:s79cc3f715062"], "status": "REASONED"},
    "redis-argv": {"text": "Redis 8.2.3 has no password-specific redaction of its start-up arguments; on Linux, with set-proc-title at its default yes, its first title update zeroes the original argument area and any environment strings directly after it before listeners open, leaving heap and setenv() copies; whether that clears the REDIS_PASSWORD environment copy is not established.", "components": ["argo", "redis-source"], "sources": ["argo:s996c72c5db28", "redis-source:sfc4931194892", "redis-source:sad31935cbfd5", "redis-source:s798e4cb2e0da", "redis-source:s514f74f25aeb", "redis-source:sc2c8077e667c", "redis-source:s41802d8e64f5", "redis-source:s8623193029f8", "redis-source:sa8561a476c47"], "status": "REASONED"},
    "redis-tls": {"text": "Base manifests configure no Redis TLS and the Argo Redis client defaults --redis-use-tls=false; protect traffic, Secret and cache.", "components": ["argo"], "sources": ["argo:s996c72c5db28", "argo:s34909d7a1932"], "status": "REASONED"},
    "component-policies": {"text": "Base policies restrict repo gRPC, Redis and Dex callers by component; enforcement needs a supporting CNI.", "components": ["argo"], "sources": ["argo:s1a13cc06db6d", "argo:s4bbf38e83770", "argo:sadccbbcffcd8"], "status": "REASONED"},
    "broad-policies": {"text": "Server policy allows all ingress; other metrics and ApplicationSet webhook allowances admit every namespace. Narrow existing additive allowances and egress separately.", "components": ["argo"], "sources": ["argo:s743c8187cbd7", "argo:s49f63c21c3cd", "argo:sa258c4109d24", "argo:sa49c30e332ed"], "status": "REASONED"},
    "argo-anonymous": {"text": "users.anonymous.enabled defaults off; anonymous callers otherwise inherit policy.default.", "components": ["argo", "argo-docs"], "sources": ["argo:s68b67007da6b", "argo-docs:sf5f1c41f89bd"], "status": "REASONED"},
    "argo-disable-auth": {"text": "server.disable.auth defaults false; inspect effective args and environment because anonymous-off does not compensate for disabled authentication.", "components": ["argo"], "sources": ["argo:s6e8c96d23e05", "argo:s01a52daf078f", "argo:s210b24f04535"], "status": "REASONED"},
    "argo-default-role": {"text": "Base RBAC ConfigMap omits policy.default; the inspected loader supplies an empty role to the enforcer, which skips its additive default-role check. Default-role grants are additive and cannot be revoked by a later subject rule; define scoped policy.csv roles and group mappings.", "components": ["argo", "argo-docs"], "sources": ["argo:s0f7f1b3404d9", "argo:s3fcdf1601776", "argo:se987196f20c7", "argo:s3cb98aa5348d", "argo:s9bfcf07a6bcc", "argo:s32323471d785", "argo-docs:sf5f1c41f89bd"], "status": "REASONED"},
    "argo-rbac-wiring": {"text": "argocd-server builds its enforcer for argocd-rbac-cm with the built-in policy and a claims enforcer, starts the ConfigMap loader, authenticates gRPC calls by default and stores claims, and passes the enforcer to API services; for example, application List filters on get and Create checks create. Per-handler coverage and runtime overrides remain unverified.", "components": ["argo"], "sources": ["argo:s0cfce81f2017", "argo:s19cc383608d3", "argo:s44b42ce894fe", "argo:s751b24797922", "argo:s0a3fee6c3102", "argo:s2bf01b29602c", "argo:s11dddf48ac64", "argo:sab95c8799d63", "argo:s3fcdf1601776", "argo:se987196f20c7"], "status": "REASONED"},
    "argo-auth-overrides": {"text": "argocd-server's gRPC interceptors authenticate calls by default unless auth is disabled, but, from this source reading, the session, version and settings services override that function for every method and accept unauthenticated callers, settings only for Get; pinned go-grpc-middleware v2.3.3 calls an override on the service value grpc-go v1.81.1 passes. As read, the interceptors ahead keep it.", "components": ["argo", "grpc-middleware", "grpc-go", "grpc-middleware-prom"], "sources": ["argo:s751b24797922", "argo:s6d4515def993", "argo:s73f95d35b6a3", "argo:s2bf01b29602c", "argo:s27142bd7b0a7", "argo:sab27d21a6f4f", "argo:sdb49a2a191ec", "argo:s19e9d1a1d4d2", "argo:sd94bce49cbb4", "argo:sc491b902058a", "argo:se1742d8dba7c", "grpc-middleware:s9ec5783f5bab", "grpc-middleware:s4413e7e06e93", "grpc-middleware:s38deb43fcd65", "grpc-middleware:se4ca59a60a0e", "grpc-middleware:sf6f4e6a293d3", "grpc-middleware-prom:sbb37d9bfd450", "argo:sde82351720c4", "argo:s6b0b042ccc35", "argo:sabf68ca51b16", "argo:s0f7c55b64e47", "argo:s074e2945a0f4", "argo:seed01984c64f", "grpc-go:sd6f265b97017", "grpc-go:s7f712ff2fcd0", "grpc-go:se04d5024dfba", "grpc-go:s9b3b1bb96432", "grpc-go:se661d06557fb", "grpc-go:s9e56a9214565", "grpc-go:sb4ab78a762fd"], "status": "REASONED"},
    "argo-auth-chain-ahead": {"text": "Ahead of auth, argocd-server's unary chain runs the bug21955 workaround, v2.3.3 logging and providers/prometheus v1.1.0 metrics interceptors; read in the extracted modules, the two module interceptors wrap one shared v2.3.3 interceptor that reads only info.FullMethod and calls the handler with the context its reportable returns, and none of the three writes to UnaryServerInfo or its Server field.", "components": ["argo", "grpc-middleware", "grpc-middleware-prom"], "sources": ["argo:se1742d8dba7c", "argo:s6d4515def993", "argo:s73f95d35b6a3", "argo:sc491b902058a", "argo:sd94bce49cbb4", "grpc-middleware:s38deb43fcd65", "grpc-middleware:se4ca59a60a0e", "grpc-middleware:sf6f4e6a293d3", "grpc-middleware-prom:sbb37d9bfd450"], "status": "REASONED"},
    "argo-grpc-middleware-pin": {"text": "Argo CD's go.sum lines for go-grpc-middleware/v2 v2.3.3, providers/prometheus v1.1.0 and grpc-go v1.81.1 match hashes a go mod download recorded over their zips on 2026-10-23. A diff -rq of each extracted zip against its tag's module directory reported no differing file; one-sided paths are or hold nested modules, or are the root LICENSE in the prometheus zip; no h1: hash was recomputed from git.", "components": ["argo", "grpc-middleware", "grpc-middleware-prom", "grpc-go"], "sources": ["argo:sd94bce49cbb4", "argo:sc491b902058a", "argo:seed01984c64f", "argo:s774ef5b5febe", "argo:s984568b27d03", "grpc-middleware:s9ec5783f5bab", "grpc-middleware:s4413e7e06e93", "grpc-middleware-prom:sbb37d9bfd450", "grpc-go:sb4ab78a762fd", "grpc-go:s342208064b4f", "grpc-go:s90e76e9ef9cf", "grpc-go:sb410d3246985", "grpc-go:s5b23c5ca5576", "grpc-go:s763fdf228f24", "grpc-go:s53ec4d2497b4", "grpc-go:s11e1ee6bc55c", "grpc-go:s144519a15f3a", "grpc-middleware:s71c21e4cdbaf", "grpc-middleware:sa4598ce2f73d", "grpc-middleware:sf540911a60b0", "grpc-middleware:s7225a1c63c9c", "grpc-middleware-prom:s11f89487025a"], "status": "REASONED"},
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
    "verify-argo": {"text": "Anonymous application listing should fail with 401 while a valid token lists the expected application; repeat at origin and CLI/gRPC and inspect effective RBAC.", "components": ["argo-docs", "argo", "curl"], "sources": ["argo-docs:sf5f1c41f89bd", "argo:s6e8c96d23e05", "curl:s3db522258e44"], "status": "REASONED", "verify": [1]},
    "verify-bootstrap": {"text": "Absence of the bootstrap Secret proves removal of that material, not password rotation.", "components": ["argo-docs"], "sources": ["argo-docs:s2efb9ee633af"], "status": "REASONED", "verify": [1]},
    "verify-inventory": {"text": "Inventory Services, routes, host ports, policies and component sockets; node-local ss and policy objects alone do not establish cluster isolation.", "components": ["argo", "flux"], "sources": ["argo:s743c8187cbd7", "flux:s493859f3b848"], "status": "REASONED", "verify": [1]},
    "verify-repo-metrics": {"text": "Base policy permits HTTP 200 metrics to monitoring and unrelated pods; narrowed policy should admit only monitoring, with a successful positive control.", "components": ["argo"], "sources": ["argo:s98b27313f615", "argo:s1a13cc06db6d"], "status": "REASONED", "verify": [2]},
    "verify-server-metrics": {"text": "Repeat on server 8083: only authorized monitoring should receive metrics after narrowing ingress; a failed control is inconclusive.", "components": ["argo"], "sources": ["argo:s028a4769d6c3", "argo:s743c8187cbd7"], "status": "REASONED"},
    "verify-profiler": {"text": "From an allowed pod, pprof cmdline should return 401 disabled, 200 for exact true, then 401 for true plus newline; keep metrics as control.", "components": ["argo"], "sources": ["argo:sc52bbd14bff4", "argo:s028a4769d6c3"], "status": "REASONED"},
    "verify-flux": {"text": "Identical generic-hmac bodies without and with X-Signature should be rejected and accepted with reconciliation; status is type/version dependent. The cited curl curl-8_14_1 lines show --data-binary posting data exactly as specified, preserving newlines and carriage returns that --data strips from @file input, reading @- from stdin and @filename from a file, and posting like --data's POST request.", "components": ["flux", "python", "curl"], "sources": ["flux:s35bb9a844dcf", "python:s7a54556e5dac", "python:s31fccd7d50e5", "curl:s3db522258e44", "curl:s9537bb790553", "curl:sd3b039bafbf6"], "status": "REASONED", "verify": [3]},
    "verify-receiver-status": {"text": "Read receiver name and Ready condition without exposing webhookPath or condition messages; origin checks distinguish receiver rejection from proxy rejection.", "components": ["flux"], "sources": ["flux:s35bb9a844dcf"], "status": "REASONED"}
  }
}
````
<!-- version-basis:end -->
