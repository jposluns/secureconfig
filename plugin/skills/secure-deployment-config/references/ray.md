# Ray: dashboard, Jobs, and Client ports execute code

Ray's own security page is blunt: if you expose the Ray Dashboard, Ray Jobs, or Ray Client services, "anybody who can access the associated ports can execute arbitrary code on your Ray Cluster", explicitly by submitting a Job or connecting a Client, indirectly through the Dashboard REST API, and implicitly because Ray deserializes arbitrary Python objects with cloudpickle. Ray "doesn't implement access controls for developers interacting with a given cluster"; security and isolation "must be enforced outside of the Ray Cluster". The head ports in question are the dashboard (and Jobs API) on `8265`, the Ray Client server on `10001`, and the head node port `6379`, all plain HTTP or gRPC with no login of their own unless you enable token authentication (step 3). The per-node agent listeners in step 2 add independent paths to job submission, logs, profiling, runtime environments and metrics.

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

Every node also runs two agent processes, the dashboard agent and the runtime env agent, and `--include-dashboard=false` stops neither: that flag only decides whether the head's dashboard process serves its API and UI (the process itself still starts, reduced to a usage-stats module), while normal head and worker startup supplies both agent commands to the raylet. Their four listeners, read from the Ray 2.58.0 source and not run, are the agent HTTP server with a default port below and three of the "several randomized ports" above. Minimal mode is selected when the optional dashboard dependencies cannot be imported, not by which install command was used: a base installation with those dependencies already present can run the full agent. In minimal mode the dashboard agent has no HTTP or gRPC server, and its reporter module and metrics exporter are absent; only the runtime env agent HTTP listener remains among these four. With the optional dependencies present, all four normally run, but disabling metrics collection skips the metrics exporter (collection is enabled by default).

- The dashboard agent serves HTTP on port `52365` by default on every non-minimal head and worker (`--dashboard-agent-listen-port` changes it); this default also applies to local clusters started by `ray.init()`. It binds the effective node IP and adds a listener on resolved localhost when `is_localhost(node_ip)` is false, meaning the address is not exactly `127.0.0.1`, `::1` or `localhost`. It serves the Jobs agent API, whose `POST /api/job_agent/jobs/` runs an arbitrary entrypoint command on the cluster, with stop, delete, logs and log-tail routes beside it, and it serves the node's whole Ray log directory as static files under `/logs`, directory index included. The head dashboard's Jobs API on `8265` forwards job submission to the head node's agent, so a request straight to the head node's agent reaches the same job manager while skipping anything placed in front of `8265`. Each worker agent has its own job manager and also accepts cluster job submissions; the driver normally runs on the head, but resource requests, a label selector or `RAY_JOB_ALLOW_DRIVER_ON_WORKER_NODES=1` can allow worker placement. A network-reachable agent therefore remains a code-execution path even while step 1 keeps `8265` on loopback; direct access does not bypass the agent's own token check when enabled. Without token authentication its only filter is a heuristic that turns away browser-looking requests (a `Mozilla` User-Agent or browser-typical headers); a plain HTTP client without those browser markers passes it. With `RAY_AUTH_MODE=token` (step 3), every route on it requires the token except `/api/healthz` and `/api/local_raylet_healthz`.
- The same agent opens a gRPC listener on an OS-assigned port by default (`--dashboard-agent-grpc-port` fixes it), on resolved localhost when the effective node address is exactly `127.0.0.1`, `::1` or `localhost`, and otherwise on the all-interfaces address, serving, among its registered services, log listing and streaming plus CPU, GPU and memory profiling services that attach profilers to processes on the node; token authentication, when enabled, adds an authentication interceptor here too.
- The runtime env agent serves HTTP on an OS-assigned port by default (`--runtime-env-agent-port` fixes it), bound to the effective node IP, with routes that create and delete runtime environments, which is package installation on the node (step 5); its token middleware exempts no path, and without token authentication it answers any caller.
- The non-minimal dashboard agent's reporter module, when metrics collection is enabled, serves Prometheus metrics on an OS-assigned port by default (`--metrics-export-port` fixes it). It passes resolved localhost when the effective node address is exactly `127.0.0.1`, `::1` or `localhost`, and otherwise an empty address, to a plain WSGI server with no authentication under any setting: the step 3 token never covers this endpoint, which is a separate server outside the agent's middleware. What it exposes is read-only cluster and host telemetry. Ray uses `wsgiref.simple_server.make_server` with its default `AF_INET` server: the empty address binds all IPv4 interfaces, and a resolved localhost of `::1` cannot bind that IPv4 socket. This IPv6 limitation is read from the source, not demonstrated with a Ray exporter.

There is no independent bind-host setting for these listeners; their bind decisions use Ray's effective node address. `ray start` passes a supplied `--node-ip-address` through `resolve_ip_for_localhost`, which replaces `127.0.0.1`, `::1` and `localhost` with `get_node_ip_address()`; with cluster mode enabled this normally discovers a network address. Passing `--node-ip-address=127.0.0.1` therefore does not, by itself, give loopback agent binds. The `ray.init()` startup path performs the same normalization. `RAY_ENABLE_WINDOWS_OR_OSX_CLUSTER` controls whole-node address selection (disabled cluster mode selects resolved localhost), not an independent agent bind. These source paths do not establish the cause of the earlier GCS observations. Keep the network boundary and the step 3 token even when the dashboard is on loopback. For the agent gRPC listener, `GetAllInterfacesIP` selects `0.0.0.0`, or `::` when resolved localhost is IPv6, independently of the node address's family; the metrics server remains IPv4 as described above.

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

**Per-node listener inventory, REASONED:** no isolated multi-node Ray cluster in the authoring environment (RAY-LIVE-1). Inventory listeners on **every head and worker**, in the network namespace where Ray runs. Use `sudo ss -tlnp` if needed to see their owning processes. Record the dashboard agent HTTP port (default 52365, or the configured `--dashboard-agent-listen-port`) and the actual dashboard agent gRPC, runtime env agent HTTP and metrics export ports from that inventory. The last three are OS-assigned by default, so repeat the inventory after a restart. Attribute each port to its agent process; do not guess from the worker-port range. In minimal mode only runtime env HTTP remains among these four; with metrics collection disabled the metrics exporter is absent. An expected listener missing without an established reason is inconclusive.

```bash
ss -tlnp   # 8265: 127.0.0.1 (or the tailnet IP), never wildcard; agent gRPC and metrics can show wildcard binds (step 2)
ss -tlnp   # read every listener; per the source, 10001 shows the node IP address (private in step 2's layout) plus a loopback listener, but 6379 can show every
           # interface (see step 2), so only the network boundary keeps it private
ss -tlnp   # if you run Ray Serve, keep 8000 (HTTP proxy) private too, and 9000 (gRPC) when configured
# REASONED: no isolated multi-node Ray cluster in the authoring environment (RAY-LIVE-1).
# From another network, repeat against every public IPv4 and IPv6 address of every head and worker
# (enclose an IPv6 literal in square brackets). Check 8265 dashboard, 6379 head, 10001 Client and
# 8000 if Ray Serve is deployed. The separate block below adds all four agent listeners.
# Keep all these origins off untrusted networks, including when token authentication is enabled;
# it does not cover Serve or metrics. The pass is that
# no TCP connection formed: time_connect stays 0.000000 and err names a connection-level failure (refused,
# no route, or a filtered-port connect timeout). A non-zero time_connect (even if the port then speaks gRPC
# not HTTP, so http is 000, or HTTP returns 401 or 403) means exposure, regardless of authentication. A
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
# REASONED: no isolated multi-node Ray cluster in the authoring environment (RAY-LIVE-1).
# On EVERY head and worker, probe the default 52365 or its configured replacement first. Then run
# this whole block again for EACH of the three actual agent ports recorded from ss above, where
# present. Also repeat it for other inventoried listeners, including worker and Serve replica ports.
# Use every externally routed node/container address, IPv4 and IPv6. Apply the reading rules above:
# exposed means a completed TCP connection (even 401/403); fixed means no TCP connection formed.
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_THE_NODE_PUBLIC_IP' '52365'   # replace inside the quotes
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the node's public address; not probing" ;;
    *) case "$2" in
         *REPLACE_WITH_*|""|*[!0123456789]*) echo "supply the actual numeric listener port; not probing" ;;
         *) if [ "${#2}" -gt 5 ] || [ "$2" -lt 1 ] || [ "$2" -gt 65535 ]; then
              echo "port must be 1 to 65535; not probing"
            else
              curl -q -g -sI -o /dev/null --noproxy '*' --connect-timeout 5 --max-time 10 \
                -w "port=$2 http=%{http_code} time_connect=%{time_connect} exit=%{exitcode} err=%{errormsg}\n" "http://$1:$2/" || true
            fi ;;
       esac ;;
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

**Direct agent token control, REASONED:** no isolated multi-node Ray cluster in the authoring environment; tracked in RAY-LIVE-1. On every non-minimal head and worker, use a trusted path directly to that node's agent HTTP port, not the head dashboard or its proxy. Run on the node against its resolved localhost, or use a dedicated SSH forward to that agent; the step 1 forward for 8265 does not forward 52365. Substitute an origin such as `http://127.0.0.1:52365` (or its actual address and configured port), without a trailing slash. Send a token only over the trusted path.

In an isolated exposed state with token mode off, select `anonymous`: a non-browser GET to `/logs/` should return 200 and the log directory index. With token mode on, first select `token` and supply the valid cluster token: expect the same access. Then select `anonymous` against that same live agent: expect 401. A connection error, 404, redirect, unexpected body or failed positive control is inconclusive; 403 is not the expected missing-token result. `/api/healthz` and `/api/local_raylet_healthz` are exempt and cannot discriminate token enforcement. These expectations follow the pinned static route and app-wide token middleware cited in Sources.

This block assumes a clean Bash shell with trusted startup files. The hidden prompt and stdin header keep the token out of curl's argv and the pasted command history; they do not hide it from the account owner or root. Do not put the token in the pasted text.

```bash
(
  trap - DEBUG RETURN ERR
  set +x +a
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_TRUSTED_AGENT_ORIGIN' 'anonymous'   # replace inside the quotes; mode: anonymous or token
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit; }
  shift
  [ "$#" -eq 2 ] || { echo "the set -- line needs exactly 2 values; not probing"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute the trusted agent origin; not probing" ;;
    *) case "$2" in
         anonymous)
           curl -q -g -s --noproxy '*' --connect-timeout 5 --max-time 10 \
             -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1/logs/" || true ;;
         token)
           { unset -n RAY_AGENT_PROBE_TOKEN && unset -v RAY_AGENT_PROBE_TOKEN; } 2>/dev/null || { echo 'cannot clear token variable; not probing'; exit 2; }
           { unset -n IFS; } 2>/dev/null || { echo 'cannot clear IFS attributes; not probing'; exit 2; }
           IFS= read -r -s -p 'Cluster token: ' RAY_AGENT_PROBE_TOKEN || { echo 'token read failed; not probing'; exit 2; }
           printf '\n'
           case "$RAY_AGENT_PROBE_TOKEN" in
             *REPLACE_WITH_*|""|*[[:cntrl:]]*) echo 'empty, placeholder or control character in token; not probing' ;;
             *) printf 'Authorization: Bearer %s\n' "$RAY_AGENT_PROBE_TOKEN" |
                  curl -q -g -s --noproxy '*' --connect-timeout 5 --max-time 10 --header @- \
                    -w '\nhttp=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1/logs/" || true ;;
           esac ;;
         *) echo 'mode must be anonymous or token; not probing' ;;
       esac ;;
  esac
)
```

Service behaviour is not demonstrated here. A watcher stopped each of four loopback runs of Ray 2.58.0 on recording the GCS listening on every interface (`*:6379`), which the authoring host forbids. No isolated network namespace was available to contain the runs, and no isolated multi-node Ray cluster is available in the authoring environment. The `ss` command was run locally in the earlier attempts; the per-node agent inventory, external-reachability probes (including all four agent listeners), direct `/logs/` token controls, dashboard job-submission controls and gRPC-TLS health-check are **REASONED**, written to be run against a live cluster in both the exposed and fixed states, tracked as RAY-LIVE-1 (`TODO.md` row 2.40).

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
- Ray dashboard agent HTTP listener (pinned tag): default `52365`, the `ray start` flags for the four agent ports, the node-IP-plus-loopback bind, the token middleware with its two exempt health paths and its no-op without token auth, and the browser-request heuristic: https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/ray_constants.py#L189, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/scripts/scripts.py#L618-L635, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/scripts/scripts.py#L687-L692, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/http_server_agent.py#L20-L23, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/http_server_agent.py#L54-L66, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/http_server_agent.py#L107-L113, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/authentication/http_token_authentication.py#L28-L80 and https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/optional_utils.py#L132-L209
- Ray Jobs agent routes and the head's forwarding to them (pinned tag): submit, stop, delete, logs and log tail on the agent; the head's submission client, its head-node agent resolution and its token header: https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/job/job_agent.py#L32-L196, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/job/job_head.py#L123-L144 and https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/job/job_head.py#L267-L280
- Ray log directory served by the agent, and its log and profiling gRPC services (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/log/log_agent.py#L245-L249, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/log/log_agent.py#L264-L307, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/log/log_agent.py#L345-L414 and https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/reporter/reporter_agent.py#L570-L638
- Ray dashboard agent gRPC bind and token interceptor, and the minimal-install case (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/agent.py#L144-L169, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/agent.py#L182-L187 and https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/agent.py#L100-L117
- Ray agent ports defaulting to OS-assigned, and both agents launched by the raylet regardless of `--include-dashboard` (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/node.py#L372-L377, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/node.py#L1660-L1669, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/node.py#L1768, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/services.py#L1381-L1387, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/services.py#L1862-L1883, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/services.py#L1918-L1929 and https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/services.py#L2022-L2031
- Ray Prometheus metrics endpoint bind and its authentication-free WSGI server (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/reporter/reporter_agent.py#L504-L516 and https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/prometheus_exporter.py#L326-L334
- Ray runtime env agent bind, routes and token middleware (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/runtime_env/agent/main.py#L218-L224 and https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/runtime_env/agent/main.py#L243-L248
- Ray all-interfaces address (pinned tag): `get_all_interfaces_ip()` calls `GetAllInterfacesIP`, which returns `0.0.0.0`, or `::` for an IPv6 localhost: https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/includes/network_util.pxi#L103-L110 and https://github.com/ray-project/ray/blob/ray-2.58.0/src/ray/util/network_util.cc#L280-L289
- Ray effective node address, CLI and Python localhost normalization, and whole-node cluster-mode setting (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/scripts/scripts.py#L850-L854, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/services.py#L786-L821, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/worker.py#L1835-L1836 and https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/ray_constants.py#L507-L514
- Ray local `ray.init()` cluster agent HTTP default, inherited from `RayParams` (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/parameter.py#L165-L167 and https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/worker.py#L1884-L1912
- Ray minimal mode dependency test, module filtering, absent reporter/exporter and runtime env agent's vendored aiohttp (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/utils.py#L1128-L1142, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/services.py#L1909-L1913, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/utils.py#L322-L351, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/agent.py#L100-L117, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/reporter/reporter_agent.py#L2099-L2101 and https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/runtime_env/agent/main.py#L23-L33
- Ray metrics collection enabled by default and raylet propagation of its disable option (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/src/ray/common/ray_config_def.h#L618-L619 and https://github.com/ray-project/ray/blob/ray-2.58.0/src/ray/raylet/node_manager.cc#L3527-L3530
- Ray agent-local job managers and default head placement, with resource, label-selector and worker-placement overrides (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/job/job_agent.py#L198-L203, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/job/job_manager.py#L421-L463 and https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/job/job_manager.py#L565-L609
- Ray metrics imports the standard WSGI server (pinned tag), whose default server inherits `AF_INET` (CPython v3.11.0); this is the source basis for the IPv4-only bind and `::1` limitation: https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/prometheus_exporter.py#L10, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/prometheus_exporter.py#L326-L334, https://github.com/python/cpython/blob/v3.11.0/Lib/wsgiref/simple_server.py#L1-L160, https://github.com/python/cpython/blob/v3.11.0/Lib/http/server.py#L120-L145 and https://github.com/python/cpython/blob/v3.11.0/Lib/socketserver.py#L400-L480
- Ray direct `/logs/` Verify discriminator: static directory index inside the agent middleware, disabled token bypass, 401 for missing credentials, valid-token access and exact health exemptions (pinned tag): https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/log/log_agent.py#L245-L249, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/http_server_agent.py#L20-L23, https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/http_server_agent.py#L102-L114 and https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/authentication/http_token_authentication.py#L28-L80
- Kubernetes security contexts (runAsNonRoot, drop capabilities, seccomp): https://kubernetes.io/docs/tasks/configure-pod-container/security-context/
- KubeRay ray-cluster Helm chart values (head/worker podSecurityContext and securityContext, default {}): https://github.com/ray-project/kuberay/blob/v1.7.0/helm-chart/ray-cluster/values.yaml
