# Ray: dashboard, Jobs, and Client ports execute code

Ray's own security page is blunt: if you expose the Ray Dashboard, Ray Jobs, or Ray Client services, "anybody who can access the associated ports can execute arbitrary code on your Ray Cluster", explicitly by submitting a Job or connecting a Client, indirectly through the Dashboard REST API, and implicitly because Ray deserializes arbitrary Python objects with cloudpickle. Ray "doesn't implement access controls for developers interacting with a given cluster"; security and isolation "must be enforced outside of the Ray Cluster". The ports in question are the dashboard (and Jobs API) on `8265`, the Ray Client server on `10001`, and the head node port `6379`, all plain HTTP or gRPC with no login of their own unless you enable token authentication (step 3).

## 1. Keep the dashboard on loopback

`ray start --dashboard-host` defaults to localhost (as of Ray 2.58.0, the first address `localhost` resolves to, IPv4 before IPv6, else `127.0.0.1`), and `--dashboard-port` defaults to `8265`. Leave both alone and say so explicitly, because most tutorials and container entrypoints override the host to make the UI reachable:

```bash
ray start --head --dashboard-host 127.0.0.1 --dashboard-port 8265
```

Never pass `--dashboard-host 0.0.0.0` (or `::`) on a machine with a public interface. In Docker the two binds are different things: the host publishes on loopback only (`-p 127.0.0.1:8265:8265`, which Docker's port-publishing docs say only the Docker host can reach, assuming a normal bridge-network NAT setup and a Docker version at or after 28.0.0; earlier releases could let hosts on the same layer-2 network reach a loopback-published port), while inside the container the dashboard must listen on the container's own interface (`--dashboard-host 0.0.0.0` there, private to the Compose network and the host), because a dashboard bound to the container's `127.0.0.1` is not reachable through the published port at all. See [docker.md](docker.md).

Reach the dashboard and the Jobs API through a channel that already authenticates you:

```bash
ssh -o ExitOnForwardFailure=yes -L 127.0.0.1:8265:127.0.0.1:8265 user@203.0.113.10   # bind the LOCAL end to loopback explicitly (a bare -L 8265: follows your ssh GatewayPorts); then open http://127.0.0.1:8265
ray job submit --address http://127.0.0.1:8265 -- python script.py
ray dashboard cluster.yaml                             # cluster launcher: sets up the same SSH forwarding
kubectl port-forward svc/"$HEAD_SERVICE" 8265:8265    # KubeRay: the RayCluster head service
```

A tailnet ([tailscale.md](tailscale.md)) is the other clean option: the dashboard binds to the tailnet address, and only enrolled devices can route to it. If a browser-facing hostname is unavoidable, put an authenticating TLS proxy in front ([nginx.md](nginx.md), [caddy.md](caddy.md), or [cloudflare.md](cloudflare.md) with Access) and keep the origin on loopback; Ray's docs themselves list "deploy a TLS proxy in front of your Ray cluster" as the pattern.

## 2. Network isolation is the primary boundary

Ray expects "a controlled, isolated network" between all its components. Beyond `8265`, the head node listens on `6379` (the GCS cluster-metadata server), `10001` (Ray Client), and every node opens worker ports `10002` to `19999` by default plus several randomized ports. Do not rely on Ray's bind addresses to keep these private.
- In Ray 2.58.0's source, the core gRPC servers (the GCS, the raylet, the object manager and every worker) listen on every interface whenever the node's address is anything other than `127.0.0.1`, `::1` or `localhost` ([`grpc_server.cc`](https://github.com/ray-project/ray/blob/ray-2.58.0/src/ray/rpc/grpc_server.cc#L67-L68), [`network_util.h`](https://github.com/ray-project/ray/blob/ray-2.58.0/src/ray/util/network_util.h#L111-L113)). On an ordinary cluster with a private node address, `6379` therefore listens on all interfaces.
- Ray Serve replicas open an inter-deployment gRPC server on `[::]` with an OS-chosen port ([`replica.py`](https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/serve/_private/replica.py#L1778)).

Those two points are read from the source and were not run. In each of four loopback runs with `--node-ip-address=127.0.0.1`, the GCS still listened on `*:6379`, and the cause was not established. Put every node of a cluster in one private network or security group that admits only the cluster's own members ([cloud-firewalls.md](cloud-firewalls.md), [host.md](host.md), [kubernetes.md](kubernetes.md)), and expose nothing from that group to the internet. The Ray Client port in particular is a remote code execution endpoint by design; use Ray Jobs over the forwarded dashboard port instead of publishing `10001`.

Ray does not isolate jobs from each other. Workloads that must not see each other's data or credentials go on separate clusters.

The head's `6379` is the GCS (cluster-metadata) server, not a Redis instance: Ray stopped launching Redis by default in Ray 1.11. What guards it is the network boundary here plus token authentication (step 3) and the gRPC TLS of step 4, not a database password. External Redis is only an opt-in backend for GCS fault tolerance; if you configure it (`ray start --redis-password` / `--redis-username`, or KubeRay's `gcsFaultToleranceOptions.redisPassword` sourced from a Secret), that credential authenticates the separate Redis connection and does not authenticate GCS clients. Do not `export RAY_REDIS_PASSWORD` as a substitute for `--redis-password` on the head; Ray does not read it as one.

## 3. Token authentication (Ray 2.52.0 and later)

Starting in Ray 2.52.0 the cluster can require a shared-secret token on its control-plane API and internal connections. Per the Ray docs it is still disabled by default as of Ray 2.58.0 (September 2026; a plan to enable it by default remains for a future release) and is "not an alternative to deploying Ray clusters in a controlled network environment", only defence in depth. It authenticates Ray's own control plane, not requests to a Ray Serve application (step 6).

```bash
export RAY_AUTH_MODE=token
ray get-auth-token --generate           # writes ~/.ray/auth_token and prints it
RAY_AUTH_MODE=token ray start --head
```

Every node and every client needs the same token. Ray reads it from `RAY_AUTH_TOKEN`, then from the file named by `RAY_AUTH_TOKEN_PATH`, then from `~/.ray/auth_token`; the docs recommend the file paths over the environment variable so other code that reads the environment cannot see it. Copy the file to each node before `ray start`, keep its permissions tight, and never commit it: tokens do not expire and are stored in plaintext ([secrets.md](secrets.md)). The token travels as an HTTP header, so over plain HTTP it is visible to the network; only send it inside the SSH tunnel, tailnet, or TLS proxy from step 1.

On Kubernetes, KubeRay v1.6.0 and later enable this through the `authOptions` field of a `RayCluster`; the operator creates a Secret with a random token and sets `RAY_AUTH_MODE` and `RAY_AUTH_TOKEN` on every Ray container. Clients read it with `kubectl get secrets 'REPLACE_WITH_SECRET_NAME' --template='{{.data.auth_token}}' | base64 -d` (quote the name, or the shell reads the unquoted `<name>` as input redirection, and quote the template so its braces are not globbed). Without the token, `ray job submit` fails with `401 Unauthorized`.

MFA: Ray has no user accounts, so a second factor can only come from the path to the cluster: the SSH login, the tailnet, or an identity-aware proxy in front of the dashboard ([mfa.md](mfa.md)).

## 4. TLS for the gRPC traffic

Ray can encrypt and mutually authenticate its internal gRPC connections. Export these in the environment of every node, head and workers alike, before Ray starts there; Ray reads them at startup (`RAY_USE_TLS` defaults to `0`), so a plain assignment without `export`, or a variable set after the node started, never reaches the Ray processes:

```bash
export RAY_USE_TLS=1                                 # default 0
export RAY_TLS_SERVER_CERT=/etc/ray/tls/tls.crt      # presented to other endpoints
export RAY_TLS_SERVER_KEY=/etc/ray/tls/tls.key
export RAY_TLS_CA_CERT=/etc/ray/tls/ca.crt           # CA that signs every node's certificate
```

Ray warns that this costs performance (large for small workloads, smaller for large ones) and that it "is not a replacement for network isolation". The docs describe it for the gRPC traffic; for the dashboard and Jobs HTTP API they point to a TLS proxy in front, which is the fronting proxy in step 1.

## 5. Job dependencies and setup hooks run as code

For a job submitted through the Jobs API, Ray installs its `runtime_env` before the entrypoint runs (a `runtime_env` passed to `ray.init` instead applies to the child tasks and actors it spawns), so submitting a job, or connecting a Client, is permission to execute code on the cluster, not just to run a fixed program. `ray job submit --runtime-env env.yaml` (or `--runtime-env-json`) and the `runtime_env=` argument to `ray.init` accept `pip`/`conda` (which download and install packages, and package installation can run distribution-provided code), `working_dir`/`py_modules` (pulled from a local path or a remote archive URI), a `py_executable` command, and an experimental `worker_process_setup_hook` that runs on every worker before your tasks. Ray ships no built-in policy that disables runtime environments or allowlists their packages, URIs, or hooks: `RuntimeEnvConfig`'s `eager_install` and `setup_timeout_seconds` only change when and how long installation runs, never whether a dependency is trusted. So the boundary is the same token and network boundary as everything else here, plus the operational practice of prebuilding reviewed dependencies into the image ([docker.md](docker.md)) rather than resolving them from an untrusted submission at run time. Treat anyone who can submit a job or reach the Client port as able to run arbitrary code.

## 6. Keep Ray Serve application endpoints private

Ray Serve runs your Python deployment code behind an HTTP proxy on port `8000`, and its bind default depends on how you start it: `serve.start(http_options=...)` and `HTTPOptions` in Python default to `127.0.0.1`, but a Serve config file's `http_options` defaults to `0.0.0.0`, every interface. `proxy_location` defaults to `EveryNode`, a proxy on each node that holds a replica. Serve has no built-in application authentication: the cluster's `RAY_AUTH_MODE=token` protects Ray's own control plane, not requests to your Serve endpoints, so a reachable Serve proxy answers anyone. Keep the proxy origin on loopback or a private interface and put an authenticating TLS proxy in front (step 1), or add authentication inside the app through Serve's FastAPI integration. `HTTPOptions` does expose `ssl_keyfile`, `ssl_certfile`, and `ssl_ca_certs` (all `None` by default) if you terminate TLS at Serve itself, but presenting a CA there does not by itself require a client certificate. The optional gRPC proxy listens on `9000` only when you configure `grpc_options` with servicer functions; treat `9000` like the other ports only when you have configured it.

## 7. Run Ray processes with restricted privileges

The official `rayproject/ray` image already runs as the non-root user `ray` (UID 1000, GID 100), but its base image grants that user passwordless `sudo`, so a compromised worker can regain root inside the container: "starts non-root" is not "stays unprivileged". On Kubernetes, KubeRay's ray-cluster Helm chart (v1.7.0) exposes `podSecurityContext` and `securityContext` on both the head and every worker group (each defaults to `{}`); on a plain `RayCluster` manifest the same settings live on the pod template and container. Set an explicit container security context on the Ray containers:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 100
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
  seccompProfile:
    type: RuntimeDefault
```

For a plain `RayCluster`, the containers are at `spec.headGroupSpec.template.spec.containers[*]` and `spec.workerGroupSpecs[*].template.spec.containers[*]`; for a bare Docker run, apply the same non-root, dropped-capabilities, read-only-where-possible posture from [container-hardening.md](container-hardening.md) and [kubernetes.md](kubernetes.md). This only limits what already-executing code can reach; it does not stop the cloudpickle deserialization or job-submission paths above, so it is a layer on top of the network and token boundaries, never a replacement.

## Verify

```bash
ss -tlnp   # read every listener; 127.0.0.1:8265 (or the tailnet IP), never 0.0.0.0 or *
ss -tlnp   # read every listener; per the source, 10001 shows the node IP address (private in step 2's layout) plus a loopback listener, but 6379 can show every
           # interface (see step 2), so only the network boundary keeps it private
ss -tlnp   # if you run Ray Serve, keep 8000 (HTTP proxy) private too, and 9000 (gRPC) when configured
# from another network, checking that each externally facing Ray port (8265 dashboard, 6379 head, 10001
# Client, plus 8000 if Ray Serve is deployed) is unreachable from outside: the first three execute arbitrary code with no cluster authentication, and the Serve proxy answers any caller because token auth (step 3) does not cover it, so every one of these origins must stay off untrusted networks whatever else fronts them. The pass is that
# no TCP connection formed: time_connect stays 0.000000 and err names a connection-level failure (refused,
# no route, or a filtered-port connect timeout). A non-zero time_connect (even if the port then speaks gRPC
# not HTTP, so http is 000) means the handshake completed and the port answered, which is the finding. A
# name-resolution or local socket error is inconclusive.
(                                       # a subshell, so your own script arguments are untouched
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_THE_SERVER_PUBLIC_IP'   # replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "the set -- line needs exactly 1 value; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the server's public address on the set -- line above; not probing" ;;
    *) curl -q -g -sI -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 \
         -w 'port=8265 http=%{http_code} time_connect=%{time_connect} exit=%{exitcode} err=%{errormsg}\n' "http://$1:8265/" || true
       curl -q -g -sI -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 \
         -w 'port=6379 http=%{http_code} time_connect=%{time_connect} exit=%{exitcode} err=%{errormsg}\n' "http://$1:6379/" || true
       curl -q -g -sI -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 \
         -w 'port=10001 http=%{http_code} time_connect=%{time_connect} exit=%{exitcode} err=%{errormsg}\n' "http://$1:10001/" || true
       curl -q -g -sI -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 \
         -w 'port=8000 http=%{http_code} time_connect=%{time_connect} exit=%{exitcode} err=%{errormsg}\n' "http://$1:8000/" || true ;;   # Ray Serve, if deployed; 9000 too when its gRPC proxy is configured
  esac
)
# Through the SSH tunnel of step 1, with RAY_AUTH_MODE=token on the cluster.
# POSITIVE control first: WITH the token the submit succeeds, proving the endpoint is live and reachable:
RAY_AUTH_MODE=token RAY_AUTH_TOKEN="$(cat ~/.ray/auth_token)" ray job submit --address http://127.0.0.1:8265 -- python -c "print(1)"   # succeeds (RAY_AUTH_MODE=token on the CLIENT makes it send the token header)
# NEGATIVE: from a client with NO token available (no RAY_AUTH_TOKEN or RAY_AUTH_TOKEN_PATH set and no
# ~/.ray/auth_token file), the same submit must be refused for AUTHENTICATION (HTTP 401); a connection
# error (tunnel down, wrong address) is INCONCLUSIVE, not a pass:
ray job submit --address http://127.0.0.1:8265 -- python -c "print(1)"   # must fail with an auth rejection, e.g. "Unauthorized: Missing authentication token" (key on the auth reason, not a literal string)
# gRPC TLS (only if you set RAY_USE_TLS=1 in step 4): the socket checks above do not prove the gRPC layer is
# encrypted. Confirm it the way Ray's docs show, running `ray health-check` once with the correct
# RAY_TLS_CA_CERT (succeeds) and once with a MISMATCHED CA or server name (Ray demonstrates a
# certificate-name mismatch), which must fail verification; a local configuration error is inconclusive.
```

Service behaviour is not demonstrated here. A watcher stopped each of four loopback runs of Ray 2.58.0 on recording the GCS listening on every interface (`*:6379`), which the authoring host forbids. No isolated network namespace was available to contain the runs. The `ss` listener check runs locally, but the external-reachability probe, the token-authentication positive and negative controls, and the gRPC-TLS health-check are **REASONED**, written to be run against a live cluster in both the exposed and fixed states, tracked as RAY-LIVE-1 (`TODO.md` row 2.40).

## Common mistakes

- `--dashboard-host 0.0.0.0` copied from a quickstart so the UI "works" from a laptop; forward the port instead.
- Treating token authentication as permission to expose `8265` to the internet. Ray says the opposite.
- Publishing `10001` for Ray Client convenience. It is unauthenticated code execution unless the token and isolation above are both in place.
- Putting the head node in a security group that also hosts unrelated services; any compromise there reaches every Ray worker.
- Securing the head port `6379` with a "Redis password". It is the GCS metadata server, not Redis; isolate the network and enable token authentication (step 3) instead.
- Assuming `RAY_AUTH_MODE=token` also protects Ray Serve endpoints. It protects Ray's control plane, not your Serve app; put authentication in front of the Serve proxy (step 6).
- Trusting the official image because it "runs as non-root", while its `ray` user holds passwordless sudo (step 7).

## Sources (checked September 2026)

- Ray security guidelines (arbitrary code execution, network isolation, TLS is not a replacement, token auth from 2.52.0): https://docs.ray.io/en/latest/ray-security/index.html
- Ray token authentication (`RAY_AUTH_MODE`, `RAY_AUTH_TOKEN`, `RAY_AUTH_TOKEN_PATH`, `ray get-auth-token`, plaintext-header caveat): https://docs.ray.io/en/latest/ray-security/token-auth.html
- `ray start` CLI reference (`--dashboard-host` default, `--dashboard-port` 8265, `--port` 6379, `--ray-client-server-port` 10001): https://docs.ray.io/en/latest/cluster/cli.html
- Configuring Ray (TLS environment variables, ports opened by nodes): https://docs.ray.io/en/latest/ray-core/configure.html
- Configure Ray clusters to use token authentication (KubeRay `authOptions`, 401 without token): https://docs.ray.io/en/latest/cluster/kubernetes/user-guides/kuberay-auth.html
- Docker, port publishing (loopback publishing): https://docs.docker.com/engine/network/port-publishing/
- curl manual (`--connect-timeout` bounds the connection phase only; the `time_connect`, `exitcode`, and `errormsg` write-out variables, the last two added in curl 7.75.0): https://curl.se/docs/manpage.html
- Ray runtime environments (`runtime_env`, pip/conda/working_dir/py_modules/setup hook, no admission-control policy): https://docs.ray.io/en/latest/ray-core/handling-dependencies.html
- Ray RuntimeEnv and RuntimeEnvConfig API (`eager_install`, `setup_timeout_seconds`): https://docs.ray.io/en/latest/ray-core/api/doc/ray.runtime_env.RuntimeEnv.html
- Ray Serve HTTPOptions (Python host default 127.0.0.1, port 8000, ssl_keyfile/ssl_certfile/ssl_ca_certs): https://docs.ray.io/en/latest/serve/api/doc/ray.serve.config.HTTPOptions.html
- Ray Serve config schema HTTPOptionsSchema (config-file http_options 0.0.0.0 host default): https://docs.ray.io/en/latest/serve/api/doc/ray.serve.schema.HTTPOptionsSchema.html
- Ray Serve deploy schema (proxy_location EveryNode default): https://docs.ray.io/en/latest/serve/api/doc/ray.serve.schema.ServeDeploySchema.html
- Ray Serve HTTP guide (FastAPI integration for app-level auth): https://docs.ray.io/en/latest/serve/http-guide.html
- GCS fault tolerance with external Redis (KubeRay `gcsFaultToleranceOptions.redisPassword`): https://docs.ray.io/en/latest/cluster/kubernetes/user-guides/kuberay-gcs-ft.html
- Redis in Ray, past and future (Redis dropped as the default in Ray 1.11): https://www.anyscale.com/blog/redis-in-ray-past-and-future
- Ray base image user and passwordless sudo (pinned tag): https://raw.githubusercontent.com/ray-project/ray/ray-2.58.0/docker/base-deps/Dockerfile
- Ray core gRPC server bind address (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/src/ray/rpc/grpc_server.cc#L67-L68
- Ray `IsLocalhost` (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/src/ray/util/network_util.h#L111-L113
- Ray `ray start` `--dashboard-host` default `get_localhost_ip()` and `--dashboard-port` default `DEFAULT_DASHBOARD_PORT` (8265), with `GetLocalhostIP()` resolving `localhost` as IPv4 first, then IPv6, else `127.0.0.1` (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/scripts/scripts.py#L601-L617, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/ray_constants.py#L185 and https://github.com/ray-project/ray/blob/ray-2.58.0/src/ray/util/network_util.cc#L257-L278
- Ray Serve replica inter-deployment gRPC server (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/serve/_private/replica.py#L1778
- Ray Client server listeners, `--host` address plus loopback (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/util/client/server/server.py#L799-L801
- Ray Client proxier listeners, `--host` address plus loopback (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/util/client/server/proxier.py#L929-L931
- Ray Client server started with the node IP address (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/node.py#L1572-L1575
- Ray Client server `--host` set from that address (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/services.py#L2464-L2471
- Kubernetes security contexts (runAsNonRoot, drop capabilities, seccomp): https://kubernetes.io/docs/tasks/configure-pod-container/security-context/
- KubeRay ray-cluster Helm chart values (head/worker podSecurityContext and securityContext, default {}): https://github.com/ray-project/kuberay/blob/v1.7.0/helm-chart/ray-cluster/values.yaml
