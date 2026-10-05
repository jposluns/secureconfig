---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "46f3a1b83b88df28c1c163b25a13c70a1ba4c2422f9d1a8abd4a940f6287fb8c",
  "components": {
    "ray": {
      "name": "Ray pinned source",
      "basis": "ray-2.58.0",
      "sources": {
        "sed3f197cc1ef": "https://github.com/ray-project/ray/blob/ray-2.58.0/doc/source/ray-security/token-auth.md",
        "s08d31327265a": "https://raw.githubusercontent.com/ray-project/ray/ray-2.58.0/docker/base-deps/Dockerfile",
        "s2740a1880e2b": "https://github.com/ray-project/ray/blob/ray-2.58.0/src/ray/rpc/grpc_server.cc#L67-L68",
        "s958054ab801b": "https://github.com/ray-project/ray/blob/ray-2.58.0/src/ray/util/network_util.h#L111-L113",
        "sa3d2966f536b": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/scripts/scripts.py#L601-L617",
        "s050b349f5bbd": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/ray_constants.py#L185",
        "sd7d2d0d963d0": "https://github.com/ray-project/ray/blob/ray-2.58.0/src/ray/util/network_util.cc#L257-L278",
        "s329ab4e0ed63": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/serve/_private/replica.py#L1778",
        "s3eb2c2cb2cbb": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/util/client/server/server.py#L799-L801",
        "sae1bb5af6e35": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/util/client/server/proxier.py#L929-L931",
        "s207ba00c4e86": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/node.py#L1572-L1575",
        "s3efda42d7913": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/services.py#L2464-L2471",
        "s9a060fe08a53": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/ray_constants.py#L189",
        "sb1935b32e677": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/scripts/scripts.py#L618-L635",
        "se9af8ec90932": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/scripts/scripts.py#L687-L692",
        "s17bc66b5543e": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/http_server_agent.py#L20-L23",
        "s7df4fce455ca": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/http_server_agent.py#L54-L66",
        "sc96f32b8a459": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/http_server_agent.py#L107-L113",
        "sbca5ef4de0bb": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/authentication/http_token_authentication.py#L28-L80",
        "scdfff3ba79f6": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/optional_utils.py#L132-L209",
        "s528944bdec23": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/job/job_agent.py#L32-L196",
        "s4796e2ca38da": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/job/job_head.py#L123-L144",
        "s1d86b2f31870": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/job/job_head.py#L267-L280",
        "s9976ecf5b1f1": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/log/log_agent.py#L245-L249",
        "sa542601368d1": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/log/log_agent.py#L264-L307",
        "sd12bacfbc3c7": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/log/log_agent.py#L345-L414",
        "s7ef1edbcda5c": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/reporter/reporter_agent.py#L570-L638",
        "s6f5310eb313d": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/agent.py#L144-L169",
        "s8f508c7e2c94": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/agent.py#L182-L187",
        "s48b3469099a3": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/agent.py#L100-L117",
        "s532a98227d6d": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/node.py#L372-L377",
        "s33a5ff7c987b": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/node.py#L1660-L1669",
        "s1a19fd793b8f": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/node.py#L1768",
        "s8f1ebe4bd911": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/services.py#L1381-L1387",
        "s7682a13e83a2": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/services.py#L1862-L1883",
        "s9237e74ea054": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/services.py#L1918-L1929",
        "s4ce6fe077ba9": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/services.py#L2022-L2031",
        "s7f27125f73b7": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/reporter/reporter_agent.py#L504-L516",
        "sf921a5d6a898": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/prometheus_exporter.py#L326-L334",
        "s434c7b4364dc": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/runtime_env/agent/main.py#L218-L224",
        "s08aa128e5d70": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/runtime_env/agent/main.py#L243-L248",
        "sdd8960062a9c": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/includes/network_util.pxi#L103-L110",
        "s51476b743c19": "https://github.com/ray-project/ray/blob/ray-2.58.0/src/ray/util/network_util.cc#L280-L289",
        "s7451c8e00be3": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/scripts/scripts.py#L850-L854",
        "s6c7faadf88a4": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/services.py#L786-L821",
        "s3625ec280c5e": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/worker.py#L1835-L1836",
        "sd3a18ab2a112": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/ray_constants.py#L507-L514",
        "sba3f67581471": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/parameter.py#L165-L167",
        "s994d0ddb6a7d": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/worker.py#L1884-L1912",
        "sd4d44da36278": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/utils.py#L1128-L1142",
        "s5a9d9c171f49": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/services.py#L1909-L1913",
        "s9cd95d66d32a": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/utils.py#L322-L351",
        "s762672f680e9": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/reporter/reporter_agent.py#L2099-L2101",
        "s28e3a1076d01": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/runtime_env/agent/main.py#L23-L33",
        "s883e3e00e4df": "https://github.com/ray-project/ray/blob/ray-2.58.0/src/ray/common/ray_config_def.h#L618-L619",
        "sdb1c4564137b": "https://github.com/ray-project/ray/blob/ray-2.58.0/src/ray/raylet/node_manager.cc#L3527-L3530",
        "sa7d4f677aadb": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/job/job_agent.py#L198-L203",
        "sa5873642c8a2": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/job/job_manager.py#L421-L463",
        "s2d562f0e7567": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/modules/job/job_manager.py#L565-L609",
        "s3a079f7e3d82": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/_private/prometheus_exporter.py#L10",
        "sefae1a66c0dd": "https://github.com/ray-project/ray/blob/ray-2.58.0/python/ray/dashboard/http_server_agent.py#L102-L114"
      }
    },
    "docs": {
      "name": "Ray documentation",
      "basis": "unknown",
      "sources": {
        "sa5e2c2d58c12": "https://docs.ray.io/en/latest/ray-security/index.html",
        "s6f0aa11f549a": "https://docs.ray.io/en/latest/ray-security/token-auth.html",
        "s56c7c98ab722": "https://docs.ray.io/en/latest/cluster/cli.html",
        "s261570b2672b": "https://docs.ray.io/en/latest/ray-core/configure.html",
        "sc375ff2ca01f": "https://docs.ray.io/en/latest/ray-core/handling-dependencies.html",
        "sb7a1d0b7dfb3": "https://docs.ray.io/en/latest/ray-core/api/doc/ray.runtime_env.RuntimeEnv.html",
        "scd3f7d8a9b02": "https://docs.ray.io/en/latest/serve/api/doc/ray.serve.config.HTTPOptions.html",
        "s15aa6ec80fb8": "https://docs.ray.io/en/latest/serve/api/doc/ray.serve.schema.HTTPOptionsSchema.html",
        "s045d75fbdecc": "https://docs.ray.io/en/latest/serve/api/doc/ray.serve.schema.ServeDeploySchema.html",
        "sc98a37c2b157": "https://docs.ray.io/en/latest/serve/http-guide.html",
        "s54ed4b890b65": "https://docs.ray.io/en/latest/cluster/kubernetes/user-guides/kuberay-gcs-ft.html"
      }
    },
    "token-min": {
      "name": "Ray token authentication introduction",
      "basis": "2.52.0",
      "sources": {
        "sa5e2c2d58c12": "https://docs.ray.io/en/latest/ray-security/index.html"
      }
    },
    "redis-history": {
      "name": "Ray Redis history announcement",
      "basis": "unknown",
      "sources": {
        "sb5afda59324d": "https://www.anyscale.com/blog/redis-in-ray-past-and-future"
      }
    },
    "docker": {
      "name": "Docker publishing documentation",
      "basis": "unknown",
      "sources": {
        "s1e53417c513d": "https://docs.docker.com/engine/network/port-publishing/"
      }
    },
    "kuberay-auth": {
      "name": "KubeRay authentication documentation",
      "basis": "unknown",
      "sources": {
        "saf5247262bc7": "https://docs.ray.io/en/latest/cluster/kubernetes/user-guides/kuberay-auth.html"
      }
    },
    "kuberay": {
      "name": "KubeRay chart",
      "basis": "v1.7.0",
      "sources": {
        "s76e45858aa01": "https://github.com/ray-project/kuberay/blob/v1.7.0/helm-chart/ray-cluster/values.yaml"
      }
    },
    "kubernetes": {
      "name": "Kubernetes security contexts",
      "basis": "unknown",
      "sources": {
        "sb78ea91d0308": "https://kubernetes.io/docs/tasks/configure-pod-container/security-context/"
      }
    },
    "python": {
      "name": "CPython WSGI server",
      "basis": "v3.11.0",
      "sources": {
        "sdd5a8e2ab59c": "https://github.com/python/cpython/blob/v3.11.0/Lib/wsgiref/simple_server.py#L1-L160",
        "se4933ce3da65": "https://github.com/python/cpython/blob/v3.11.0/Lib/http/server.py#L120-L145",
        "s0020052d7267": "https://github.com/python/cpython/blob/v3.11.0/Lib/socketserver.py#L400-L480"
      }
    },
    "curl": {
      "name": "curl minimum write-out version",
      "basis": "7.75.0",
      "sources": {
        "s2b2686afaf41": "https://curl.se/docs/manpage.html"
      }
    }
  },
  "claims": {
    "boundary": {"text": "Dashboard, Jobs and Client access permits arbitrary code execution; use an isolated cluster network and separate clusters for mutually untrusted jobs.", "components": ["docs"], "sources": ["docs:sa5e2c2d58c12"], "status": "REASONED"},
    "dashboard": {"text": "Dashboard defaults to resolved localhost, IPv4 before IPv6 then 127.0.0.1, on port 8265; state loopback explicitly.", "components": ["ray"], "sources": ["ray:sa3d2966f536b", "ray:s050b349f5bbd", "ray:sd7d2d0d963d0"], "status": "REASONED"},
    "docker": {"text": "Bridge publishing uses host loopback and container-interface bind; loopback isolation assumes Docker 28.0.0+ and normal NAT. The Sources entry does not record that minimum.", "components": ["docker"], "sources": ["docker:s1e53417c513d"], "status": "REASONED"},
    "access": {"text": "Reach Dashboard/Jobs through loopback SSH forwarding, launcher forwarding, KubeRay forwarding or a private tailnet; public browser access needs an authenticating TLS proxy.", "components": ["docs", "kuberay-auth"], "sources": ["docs:sa5e2c2d58c12", "docs:s56c7c98ab722", "kuberay-auth:saf5247262bc7"], "status": "REASONED"},
    "head-ports": {"text": "Head GCS uses 6379 and Client 10001; worker ports default 10002-19999 plus randomized listeners.", "components": ["docs"], "sources": ["docs:s56c7c98ab722", "docs:s261570b2672b"], "status": "REASONED"},
    "core-bind": {"text": "Core gRPC source binds all interfaces unless node address is exactly 127.0.0.1, ::1 or localhost; private node IP does not imply private bind.", "components": ["ray"], "sources": ["ray:s2740a1880e2b", "ray:s958054ab801b"], "status": "REASONED"},
    "gcs-observation": {"text": "Four attempted Ray 2.58.0 loopback starts still showed GCS *:6379; the cause was not established and the watcher stopped the runs.", "components": ["ray"], "sources": ["ray:s2740a1880e2b", "ray:s958054ab801b"], "status": "DEMONSTRATED", "evidence": "in each of four runs using `ray start --head --node-ip-address=127.0.0.1 --port=6379 --dashboard-host=127.0.0.1`, `ss` still showed the GCS listener as `*:6379`."},
    "client-bind": {"text": "Ray Client server/proxier listen on the supplied node address plus loopback; restrict access and prefer Jobs over publishing Client.", "components": ["ray"], "sources": ["ray:s3eb2c2cb2cbb", "ray:sae1bb5af6e35", "ray:s207ba00c4e86", "ray:s3efda42d7913"], "status": "REASONED"},
    "serve-replica": {"text": "Serve inter-deployment gRPC binds [::] on an OS-chosen port; this is source reasoning, not a run.", "components": ["ray"], "sources": ["ray:s329ab4e0ed63"], "status": "REASONED"},
    "agents": {"text": "--include-dashboard=false does not stop dashboard/runtime-env agents; head dashboard itself is reduced to usage stats.", "components": ["ray"], "sources": ["ray:s33a5ff7c987b", "ray:s1a19fd793b8f", "ray:s8f1ebe4bd911", "ray:s7682a13e83a2", "ray:s9237e74ea054", "ray:s4ce6fe077ba9"], "status": "REASONED"},
    "minimal": {"text": "Missing optional imports select minimal mode: no agent HTTP/gRPC or metrics reporter; runtime-env HTTP remains. Base installs may have full dependencies.", "components": ["ray"], "sources": ["ray:s48b3469099a3", "ray:sd4d44da36278", "ray:s5a9d9c171f49", "ray:s9cd95d66d32a", "ray:s762672f680e9", "ray:s28e3a1076d01"], "status": "REASONED"},
    "agent-http": {"text": "Non-minimal agent HTTP defaults 52365, including ray.init; --dashboard-agent-listen-port changes it, with node-IP plus conditional localhost binds.", "components": ["ray"], "sources": ["ray:s9a060fe08a53", "ray:sb1935b32e677", "ray:s7df4fce455ca", "ray:sba3f67581471", "ray:s994d0ddb6a7d"], "status": "REASONED"},
    "agent-jobs": {"text": "Direct /api/job_agent/jobs/ submission and stop/delete/log routes bypass a proxy on 8265; head forwarding reaches its agent job manager.", "components": ["ray"], "sources": ["ray:s528944bdec23", "ray:s4796e2ca38da", "ray:s1d86b2f31870"], "status": "REASONED"},
    "agent-placement": {"text": "Worker agents accept cluster submissions with their own managers; drivers normally use the head unless resources, labels or worker-placement override permit workers.", "components": ["ray"], "sources": ["ray:sa7d4f677aadb", "ray:sa5873642c8a2", "ray:s2d562f0e7567"], "status": "REASONED"},
    "agent-logs": {"text": "Agent static /logs exposes the node log directory and index.", "components": ["ray"], "sources": ["ray:s9976ecf5b1f1"], "status": "REASONED"},
    "agent-http-auth": {"text": "Without token mode a browser heuristic is the only filter; token mode guards all agent HTTP paths except two health endpoints.", "components": ["ray"], "sources": ["ray:s17bc66b5543e", "ray:sc96f32b8a459", "ray:sbca5ef4de0bb", "ray:scdfff3ba79f6"], "status": "REASONED"},
    "agent-grpc": {"text": "Agent gRPC defaults OS-assigned with --dashboard-agent-grpc-port override; localhost or wildcard bind serves log/profiling RPCs with optional token interception.", "components": ["ray"], "sources": ["ray:sb1935b32e677", "ray:sa542601368d1", "ray:sd12bacfbc3c7", "ray:s7ef1edbcda5c", "ray:s6f5310eb313d", "ray:s8f508c7e2c94", "ray:s532a98227d6d"], "status": "REASONED"},
    "runtime-agent": {"text": "Runtime-env HTTP defaults OS-assigned on node IP with --runtime-env-agent-port override; create/delete installs packages, and token middleware exempts no route.", "components": ["ray"], "sources": ["ray:s532a98227d6d", "ray:s434c7b4364dc", "ray:s08aa128e5d70", "ray:sb1935b32e677"], "status": "REASONED"},
    "metrics-agent": {"text": "Metrics default enabled; non-minimal reporter uses an OS-assigned port or --metrics-export-port, outside all token middleware.", "components": ["ray"], "sources": ["ray:s532a98227d6d", "ray:s7f27125f73b7", "ray:sf921a5d6a898", "ray:s883e3e00e4df", "ray:sdb1c4564137b", "ray:se9af8ec90932"], "status": "REASONED"},
    "metrics-ipv4": {"text": "WSGI metrics uses AF_INET: empty address is IPv4 wildcard, localhost is used for local node addresses, and resolved ::1 cannot bind this socket.", "components": ["ray", "python"], "sources": ["ray:s7f27125f73b7", "ray:sf921a5d6a898", "ray:s3a079f7e3d82", "python:sdd5a8e2ab59c", "python:se4933ce3da65", "python:s0020052d7267"], "status": "REASONED"},
    "node-normalization": {"text": "Both CLI and ray.init normalize localhost node arguments to a discovered address; cluster-mode setting changes whole-node selection, not independent agent binds.", "components": ["ray"], "sources": ["ray:s7451c8e00be3", "ray:s6c7faadf88a4", "ray:s3625ec280c5e", "ray:sd3a18ab2a112"], "status": "REASONED"},
    "agent-family": {"text": "Agent gRPC wildcard selection is 0.0.0.0 or :: based on resolved localhost, independently of node address family.", "components": ["ray"], "sources": ["ray:sdd8960062a9c", "ray:s51476b743c19"], "status": "REASONED"},
    "gcs-not-redis": {"text": "6379 is GCS, not Redis; Redis stopped being launched by default in 1.11.", "components": ["redis-history", "docs"], "sources": ["redis-history:sb5afda59324d", "docs:s56c7c98ab722"], "status": "REASONED"},
    "redis-backend": {"text": "External Redis is opt-in GCS fault-tolerance storage; Redis credentials do not authenticate GCS clients and RAY_REDIS_PASSWORD is not a head flag substitute.", "components": ["docs"], "sources": ["docs:s56c7c98ab722", "docs:s54ed4b890b65"], "status": "REASONED"},
    "token-default": {"text": "Shared token authentication exists since 2.52.0 but is disabled by default as of 2.58.0; it supplements network isolation and does not protect Serve apps.", "components": ["token-min", "ray"], "sources": ["token-min:sa5e2c2d58c12", "ray:sed3f197cc1ef"], "status": "REASONED"},
    "token-input": {"text": "Enable RAY_AUTH_MODE=token; precedence is RAY_AUTH_TOKEN, RAY_AUTH_TOKEN_PATH then ~/.ray/auth_token, shared by every node/client.", "components": ["ray"], "sources": ["ray:sed3f197cc1ef"], "status": "REASONED"},
    "token-storage": {"text": "Generate/protect token files and copy before startup; tokens are plaintext, do not expire and must never be committed.", "components": ["ray"], "sources": ["ray:sed3f197cc1ef"], "status": "REASONED"},
    "token-transport": {"text": "Token HTTP headers require a trusted tunnel or TLS; plaintext HTTP exposes them on the network.", "components": ["docs", "ray"], "sources": ["docs:s6f0aa11f549a", "ray:sed3f197cc1ef"], "status": "REASONED"},
    "kuberay-token": {"text": "KubeRay authOptions provisions a Secret and Ray-container token variables; the body states v1.6.0+, absent from its Sources entry.", "components": ["kuberay-auth"], "sources": ["kuberay-auth:saf5247262bc7"], "status": "REASONED"},
    "mfa": {"text": "Ray has no user accounts; MFA belongs on SSH, tailnet or identity-aware proxy access.", "components": ["docs"], "sources": ["docs:sa5e2c2d58c12"], "status": "REASONED"},
    "grpc-tls": {"text": "RAY_USE_TLS defaults 0; export it and server certificate/key/CA variables on every node before startup for internal gRPC mutual TLS.", "components": ["docs"], "sources": ["docs:s261570b2672b"], "status": "REASONED"},
    "tls-scope": {"text": "gRPC TLS can cost performance and does not replace isolation or the dashboard/Jobs HTTP TLS proxy.", "components": ["docs"], "sources": ["docs:sa5e2c2d58c12", "docs:s261570b2672b"], "status": "REASONED"},
    "runtime-code": {"text": "Job runtime_env installs before entrypoint; ray.init environments apply to child tasks/actors. Packages, archives, py_executable and setup hooks execute submitted code.", "components": ["docs"], "sources": ["docs:sc375ff2ca01f"], "status": "REASONED"},
    "runtime-policy": {"text": "No built-in package/URI/hook admission policy; eager_install and setup_timeout_seconds control timing, not trust. Prebuild reviewed dependencies.", "components": ["docs"], "sources": ["docs:sc375ff2ca01f", "docs:sb7a1d0b7dfb3"], "status": "REASONED"},
    "serve-bind": {"text": "Serve HTTP defaults port 8000, Python host 127.0.0.1 but config-file host 0.0.0.0; EveryNode puts proxies on nodes with replicas.", "components": ["docs"], "sources": ["docs:scd3f7d8a9b02", "docs:s15aa6ec80fb8", "docs:s045d75fbdecc"], "status": "REASONED"},
    "serve-auth": {"text": "Serve apps have no built-in application auth and are outside cluster token mode; restrict origins and add proxy or FastAPI authentication.", "components": ["docs"], "sources": ["docs:sa5e2c2d58c12", "docs:sc98a37c2b157"], "status": "REASONED"},
    "serve-tls": {"text": "Serve ssl_keyfile/ssl_certfile/ssl_ca_certs default None; supplying a CA does not itself require client certificates.", "components": ["docs"], "sources": ["docs:scd3f7d8a9b02"], "status": "REASONED"},
    "serve-grpc": {"text": "Optional Serve gRPC uses 9000 only with configured servicer functions; its dedicated gRPC option reference is not cited.", "components": ["docs"], "sources": ["docs:s045d75fbdecc"], "status": "REASONED"},
    "image-privilege": {"text": "Official image ray UID 1000/GID 100 has passwordless sudo; non-root startup alone does not prevent root escalation.", "components": ["ray"], "sources": ["ray:s08d31327265a"], "status": "REASONED"},
    "pod-security": {"text": "KubeRay v1.7.0 head/worker pod/container contexts default empty; enforce non-root UID/GID, no privilege escalation, dropped capabilities and RuntimeDefault seccomp.", "components": ["kuberay", "kubernetes"], "sources": ["kuberay:s76e45858aa01", "kubernetes:sb78ea91d0308"], "status": "REASONED"},
    "verify-inventory": {"text": "Inventory every head/worker and actual randomized agent ports after restarts; expected missing listeners need explanation. No isolated multi-node cluster was available.", "components": ["ray"], "sources": ["ray:s9a060fe08a53", "ray:s6f5310eb313d", "ray:s532a98227d6d", "ray:s7f27125f73b7", "ray:s434c7b4364dc"], "status": "REASONED", "verify": [1]},
    "verify-external": {"text": "Probe every routed IPv4/IPv6 origin and inventoried port; completed TCP, even HTTP 401 or non-HTTP, proves exposure. Resolver/local errors are inconclusive.", "components": ["docs", "curl"], "sources": ["docs:sa5e2c2d58c12", "docs:s261570b2672b", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [1]},
    "verify-jobs": {"text": "Through the trusted tunnel valid-token submission must succeed and token-free submission must fail authentication with 401, not a connection error.", "components": ["ray", "kuberay-auth"], "sources": ["ray:sed3f197cc1ef", "kuberay-auth:saf5247262bc7"], "status": "REASONED", "verify": [1]},
    "verify-grpc-tls": {"text": "ray health-check must pass with the correct CA and fail certificate verification with a wrong CA/name; local config errors are inconclusive.", "components": ["docs"], "sources": ["docs:s261570b2672b"], "status": "REASONED", "verify": [1]},
    "verify-agent": {"text": "Direct non-browser /logs/ must expose an index with token mode off, allow a valid token with it on and reject absent tokens with 401; health exemptions cannot discriminate.", "components": ["ray"], "sources": ["ray:s9976ecf5b1f1", "ray:s17bc66b5543e", "ray:sbca5ef4de0bb", "ray:sefae1a66c0dd"], "status": "REASONED", "verify": [2]},
    "verify-token-secret": {"text": "Trusted-path hidden prompt and stdin header avoid new token argv/history exposure; account owner/root can still read memory.", "components": ["ray", "curl"], "sources": ["ray:sed3f197cc1ef", "curl:s2b2686afaf41"], "status": "REASONED", "verify": [2]}
  }
}
---
# Ray: dashboard, Jobs, and Client ports execute code

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| boundary: Dashboard, Jobs and Client access permits arbitrary code execution; use an isolated cluster network and separate clusters for mutually untrusted jobs. | Ray documentation unknown | REASONED |
| dashboard: Dashboard defaults to resolved localhost, IPv4 before IPv6 then 127.0.0.1, on port 8265; state loopback explicitly. | Ray pinned source ray-2.58.0 | REASONED |
| docker: Bridge publishing uses host loopback and container-interface bind; loopback isolation assumes Docker 28.0.0+ and normal NAT. The Sources entry does not record that minimum. | Docker publishing documentation unknown | REASONED |
| access: Reach Dashboard/Jobs through loopback SSH forwarding, launcher forwarding, KubeRay forwarding or a private tailnet; public browser access needs an authenticating TLS proxy. | Ray documentation unknown; KubeRay authentication documentation unknown | REASONED |
| head-ports: Head GCS uses 6379 and Client 10001; worker ports default 10002-19999 plus randomized listeners. | Ray documentation unknown | REASONED |
| core-bind: Core gRPC source binds all interfaces unless node address is exactly 127.0.0.1, ::1 or localhost; private node IP does not imply private bind. | Ray pinned source ray-2.58.0 | REASONED |
| gcs-observation: Four attempted Ray 2.58.0 loopback starts still showed GCS *:6379; the cause was not established and the watcher stopped the runs. | Ray pinned source ray-2.58.0 | DEMONSTRATED |
| client-bind: Ray Client server/proxier listen on the supplied node address plus loopback; restrict access and prefer Jobs over publishing Client. | Ray pinned source ray-2.58.0 | REASONED |
| serve-replica: Serve inter-deployment gRPC binds [::] on an OS-chosen port; this is source reasoning, not a run. | Ray pinned source ray-2.58.0 | REASONED |
| agents: --include-dashboard=false does not stop dashboard/runtime-env agents; head dashboard itself is reduced to usage stats. | Ray pinned source ray-2.58.0 | REASONED |
| minimal: Missing optional imports select minimal mode: no agent HTTP/gRPC or metrics reporter; runtime-env HTTP remains. Base installs may have full dependencies. | Ray pinned source ray-2.58.0 | REASONED |
| agent-http: Non-minimal agent HTTP defaults 52365, including ray.init; --dashboard-agent-listen-port changes it, with node-IP plus conditional localhost binds. | Ray pinned source ray-2.58.0 | REASONED |
| agent-jobs: Direct /api/job_agent/jobs/ submission and stop/delete/log routes bypass a proxy on 8265; head forwarding reaches its agent job manager. | Ray pinned source ray-2.58.0 | REASONED |
| agent-placement: Worker agents accept cluster submissions with their own managers; drivers normally use the head unless resources, labels or worker-placement override permit workers. | Ray pinned source ray-2.58.0 | REASONED |
| agent-logs: Agent static /logs exposes the node log directory and index. | Ray pinned source ray-2.58.0 | REASONED |
| agent-http-auth: Without token mode a browser heuristic is the only filter; token mode guards all agent HTTP paths except two health endpoints. | Ray pinned source ray-2.58.0 | REASONED |
| agent-grpc: Agent gRPC defaults OS-assigned with --dashboard-agent-grpc-port override; localhost or wildcard bind serves log/profiling RPCs with optional token interception. | Ray pinned source ray-2.58.0 | REASONED |
| runtime-agent: Runtime-env HTTP defaults OS-assigned on node IP with --runtime-env-agent-port override; create/delete installs packages, and token middleware exempts no route. | Ray pinned source ray-2.58.0 | REASONED |
| metrics-agent: Metrics default enabled; non-minimal reporter uses an OS-assigned port or --metrics-export-port, outside all token middleware. | Ray pinned source ray-2.58.0 | REASONED |
| metrics-ipv4: WSGI metrics uses AF_INET: empty address is IPv4 wildcard, localhost is used for local node addresses, and resolved ::1 cannot bind this socket. | Ray pinned source ray-2.58.0; CPython WSGI server v3.11.0 | REASONED |
| node-normalization: Both CLI and ray.init normalize localhost node arguments to a discovered address; cluster-mode setting changes whole-node selection, not independent agent binds. | Ray pinned source ray-2.58.0 | REASONED |
| agent-family: Agent gRPC wildcard selection is 0.0.0.0 or :: based on resolved localhost, independently of node address family. | Ray pinned source ray-2.58.0 | REASONED |
| gcs-not-redis: 6379 is GCS, not Redis; Redis stopped being launched by default in 1.11. | Ray Redis history announcement unknown; Ray documentation unknown | REASONED |
| redis-backend: External Redis is opt-in GCS fault-tolerance storage; Redis credentials do not authenticate GCS clients and RAY_REDIS_PASSWORD is not a head flag substitute. | Ray documentation unknown | REASONED |
| token-default: Shared token authentication exists since 2.52.0 but is disabled by default as of 2.58.0; it supplements network isolation and does not protect Serve apps. | Ray token authentication introduction 2.52.0; Ray pinned source ray-2.58.0 | REASONED |
| token-input: Enable RAY_AUTH_MODE=token; precedence is RAY_AUTH_TOKEN, RAY_AUTH_TOKEN_PATH then ~/.ray/auth_token, shared by every node/client. | Ray pinned source ray-2.58.0 | REASONED |
| token-storage: Generate/protect token files and copy before startup; tokens are plaintext, do not expire and must never be committed. | Ray pinned source ray-2.58.0 | REASONED |
| token-transport: Token HTTP headers require a trusted tunnel or TLS; plaintext HTTP exposes them on the network. | Ray documentation unknown; Ray pinned source ray-2.58.0 | REASONED |
| kuberay-token: KubeRay authOptions provisions a Secret and Ray-container token variables; the body states v1.6.0+, absent from its Sources entry. | KubeRay authentication documentation unknown | REASONED |
| mfa: Ray has no user accounts; MFA belongs on SSH, tailnet or identity-aware proxy access. | Ray documentation unknown | REASONED |
| grpc-tls: RAY_USE_TLS defaults 0; export it and server certificate/key/CA variables on every node before startup for internal gRPC mutual TLS. | Ray documentation unknown | REASONED |
| tls-scope: gRPC TLS can cost performance and does not replace isolation or the dashboard/Jobs HTTP TLS proxy. | Ray documentation unknown | REASONED |
| runtime-code: Job runtime_env installs before entrypoint; ray.init environments apply to child tasks/actors. Packages, archives, py_executable and setup hooks execute submitted code. | Ray documentation unknown | REASONED |
| runtime-policy: No built-in package/URI/hook admission policy; eager_install and setup_timeout_seconds control timing, not trust. Prebuild reviewed dependencies. | Ray documentation unknown | REASONED |
| serve-bind: Serve HTTP defaults port 8000, Python host 127.0.0.1 but config-file host 0.0.0.0; EveryNode puts proxies on nodes with replicas. | Ray documentation unknown | REASONED |
| serve-auth: Serve apps have no built-in application auth and are outside cluster token mode; restrict origins and add proxy or FastAPI authentication. | Ray documentation unknown | REASONED |
| serve-tls: Serve ssl_keyfile/ssl_certfile/ssl_ca_certs default None; supplying a CA does not itself require client certificates. | Ray documentation unknown | REASONED |
| serve-grpc: Optional Serve gRPC uses 9000 only with configured servicer functions; its dedicated gRPC option reference is not cited. | Ray documentation unknown | REASONED |
| image-privilege: Official image ray UID 1000/GID 100 has passwordless sudo; non-root startup alone does not prevent root escalation. | Ray pinned source ray-2.58.0 | REASONED |
| pod-security: KubeRay v1.7.0 head/worker pod/container contexts default empty; enforce non-root UID/GID, no privilege escalation, dropped capabilities and RuntimeDefault seccomp. | KubeRay chart v1.7.0; Kubernetes security contexts unknown | REASONED |
| verify-inventory: Inventory every head/worker and actual randomized agent ports after restarts; expected missing listeners need explanation. No isolated multi-node cluster was available. | Ray pinned source ray-2.58.0 | REASONED |
| verify-external: Probe every routed IPv4/IPv6 origin and inventoried port; completed TCP, even HTTP 401 or non-HTTP, proves exposure. Resolver/local errors are inconclusive. | Ray documentation unknown; curl minimum write-out version 7.75.0 | REASONED |
| verify-jobs: Through the trusted tunnel valid-token submission must succeed and token-free submission must fail authentication with 401, not a connection error. | Ray pinned source ray-2.58.0; KubeRay authentication documentation unknown | REASONED |
| verify-grpc-tls: ray health-check must pass with the correct CA and fail certificate verification with a wrong CA/name; local config errors are inconclusive. | Ray documentation unknown | REASONED |
| verify-agent: Direct non-browser /logs/ must expose an index with token mode off, allow a valid token with it on and reject absent tokens with 401; health exemptions cannot discriminate. | Ray pinned source ray-2.58.0 | REASONED |
| verify-token-secret: Trusted-path hidden prompt and stdin header avoid new token argv/history exposure; account owner/root can still read memory. | Ray pinned source ray-2.58.0; curl minimum write-out version 7.75.0 | REASONED |
<!-- version-basis:end -->

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

Those two points are read from the source and were not run.

**Observed on 2026-09-24 with Ray 2.58.0:** in each of four runs using `ray start --head --node-ip-address=127.0.0.1 --port=6379 --dashboard-host=127.0.0.1`, `ss` still showed the GCS listener as `*:6379`. The cause was not established. Do not rely on `--node-ip-address` alone to keep the GCS off other interfaces; restrict access with a host firewall or network namespace, and verify the listeners with `ss`.

Put every node of a cluster in one private network or security group that admits only the cluster's own members ([cloud-firewalls.md](cloud-firewalls.md), [host.md](host.md), [kubernetes.md](kubernetes.md)), and expose nothing from that group to the internet. The Ray Client port in particular is a remote code execution endpoint by design; use Ray Jobs over the forwarded dashboard port instead of publishing `10001`.

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

**Per-node listener inventory, REASONED:** no isolated multi-node Ray cluster in the authoring environment; expected outcomes follow the cited Ray 2.58.0 sources. Inventory listeners on **every head and worker**, in the network namespace where Ray runs. Use `sudo ss -tlnp` if needed to see their owning processes. Record the dashboard agent HTTP port (default 52365, or the configured `--dashboard-agent-listen-port`) and the actual dashboard agent gRPC, runtime env agent HTTP and metrics export ports from that inventory. The last three are OS-assigned by default, so repeat the inventory after a restart. Attribute each port to its agent process; do not guess from the worker-port range. In minimal mode only runtime env HTTP remains among these four; with metrics collection disabled the metrics exporter is absent. An expected listener missing without an established reason is inconclusive.

```bash
# REASONED: Ray listener, job and TLS checks follow the cited 2.58.0 sources; no isolated cluster is available. Earlier ss observations are recorded below.
ss -tlnp   # 8265: 127.0.0.1 (or the tailnet IP), never wildcard; agent gRPC and metrics can show wildcard binds (step 2)
ss -tlnp   # read every listener; per the source, 10001 shows the node IP address (private in step 2's layout) plus a loopback listener, but 6379 can show every
           # interface (see step 2), so only the network boundary keeps it private
ss -tlnp   # if you run Ray Serve, keep 8000 (HTTP proxy) private too, and 9000 (gRPC) when configured
# REASONED: no isolated multi-node Ray cluster in the authoring environment; expected outcomes follow the cited Ray 2.58.0 sources.
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
# REASONED: no isolated multi-node Ray cluster in the authoring environment; expected outcomes follow the cited Ray 2.58.0 sources.
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
# Assumes a clean Bash shell with trusted startup files, and a token file owned by this account
# under ~/.ray in directories no other account can write to or replace. Ray reads the file itself.
(
  trap - DEBUG RETURN ERR
  set +x +a +e
  { unset -n RAY_AUTH_TOKEN RAY_AUTH_TOKEN_PATH RAY_AUTH_MODE &&
    unset -v RAY_AUTH_TOKEN RAY_AUTH_TOKEN_PATH RAY_AUTH_MODE; } 2>/dev/null ||
    { echo 'cannot clear Ray authentication variables; not submitting'; exit 2; }
  if [ ! -f "$HOME/.ray/auth_token" ] || [ -L "$HOME/.ray/auth_token" ] ||
     [ ! -r "$HOME/.ray/auth_token" ] || [ ! -s "$HOME/.ray/auth_token" ]; then
    echo 'need a readable, non-empty regular token file, not a symlink; not submitting'; exit 2
  fi
  chmod 600 -- "$HOME/.ray/auth_token" ||
    { echo 'cannot protect the token file; not submitting'; exit 2; }
  RAY_AUTH_MODE=token RAY_AUTH_TOKEN_PATH="$HOME/.ray/auth_token" \
    ray job submit --address http://127.0.0.1:8265 -- python -c "print(1)"
)
# Only the path is in the environment; the token stays in the file and Ray's memory, readable by
# this account and root. Clearing variables does not erase a token previously exported or logged.
# NEGATIVE: from a client with NO token available (no RAY_AUTH_TOKEN or RAY_AUTH_TOKEN_PATH set and no
# ~/.ray/auth_token file), the same submit must be refused for AUTHENTICATION (HTTP 401); a connection
# error (tunnel down, wrong address) is INCONCLUSIVE, not a pass:
ray job submit --address http://127.0.0.1:8265 -- python -c "print(1)"   # must fail with an auth rejection, e.g. "Unauthorized: Missing authentication token" (key on the auth reason, not a literal string)
# gRPC TLS (only if you set RAY_USE_TLS=1 in step 4): the socket checks above do not prove the gRPC layer is
# encrypted. Confirm it the way Ray's docs show, running `ray health-check` once with the correct
# RAY_TLS_CA_CERT (succeeds) and once with a MISMATCHED CA or server name (Ray demonstrates a
# certificate-name mismatch), which must fail verification; a local configuration error is inconclusive.
```

**Direct agent token control, REASONED:** no isolated multi-node Ray cluster in the authoring environment; expected outcomes follow the cited Ray 2.58.0 sources. On every non-minimal head and worker, use a trusted path directly to that node's agent HTTP port, not the head dashboard or its proxy. Run on the node against its resolved localhost, or use a dedicated SSH forward to that agent; the step 1 forward for 8265 does not forward 52365. Substitute an origin such as `http://127.0.0.1:52365` (or its actual address and configured port), without a trailing slash. Send a token only over the trusted path.

In an isolated exposed state with token mode off, select `anonymous`: a non-browser GET to `/logs/` should return 200 and the log directory index. With token mode on, first select `token` and supply the valid cluster token: expect the same access. Then select `anonymous` against that same live agent: expect 401. A connection error, 404, redirect, unexpected body or failed positive control is inconclusive; 403 is not the expected missing-token result. `/api/healthz` and `/api/local_raylet_healthz` are exempt and cannot discriminate token enforcement. These expectations follow the pinned static route and app-wide token middleware cited in Sources.

This block assumes a clean Bash shell with trusted startup files. The hidden prompt and stdin header keep the token out of curl's argv and the pasted command history; they do not hide it from the account owner or root. Do not put the token in the pasted text.

```bash
# REASONED: direct agent token controls follow the cited Ray 2.58.0 sources; no isolated multi-node cluster is available.
(
  trap - DEBUG RETURN ERR
  set +x +a +e
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

Service behaviour is not demonstrated here. A watcher stopped each of four loopback runs of Ray 2.58.0 on recording the GCS listening on every interface (`*:6379`), which the authoring host forbids. No isolated network namespace was available to contain the runs, and no isolated multi-node Ray cluster is available in the authoring environment. The `ss` command was run locally in the earlier attempts; the per-node agent inventory, external-reachability probes (including all four agent listeners), direct `/logs/` token controls, dashboard job-submission controls and gRPC-TLS health-check are **REASONED**, with expected exposed and fixed outcomes derived from the cited Ray 2.58.0 sources and vendor documentation.

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
- Ray 2.58.0 token input precedence and file-based job submission: https://github.com/ray-project/ray/blob/ray-2.58.0/doc/source/ray-security/token-auth.md
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
