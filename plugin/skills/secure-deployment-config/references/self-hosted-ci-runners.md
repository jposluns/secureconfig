# Self-hosted CI runners: GitHub Actions and GitLab Runner

A self-hosted runner exists to execute CI job commands on your own machine, so the trust question is
not a bind address but who can cause code to run on it. Both GitHub Actions runners and GitLab Runner
are outbound-only for job transport: they poll their service over HTTPS (configure GitLab Runner to verify the
certificate) and open no inbound job-polling port, so no inbound opening is needed to receive jobs. Autoscaled
GitLab workers can still take private management connections from their runner manager, and a custom GitHub
autoscaler can run a separate webhook receiver; restrict any such management listener to its manager and
validate webhook signatures before processing. The controls are eligibility (whose code the runner will run),
credentials (what a job can reach), executor privilege (how isolated the job is from the host), and lifecycle
(what survives after a job). Get those wrong and an untrusted job is remote code
execution with the runner's permissions and network position: it can steal the credentials the job
legitimately receives, poison caches and tools that later trusted builds consume, and pivot from the
runner's place in your network, including the cloud metadata endpoint
([egress-metadata.md](egress-metadata.md)).
Isolate runners from production and from each other, and handle every token as [secrets.md](secrets.md)
describes. Run the job-executing process under a dedicated account with the least OS privilege it needs, keep
administrator and provisioning credentials off the worker, and treat rootful Docker access (including `docker`
group membership) as host administration confined to a disposable VM. Enforce worker egress outside the job's
control: allow the CI, artifact, registry, DNS and dependency destinations it needs and deny production
networks, runner-management services, other workers, and unused metadata endpoints over IPv4 and IPv6. IMDSv2
and metadata headers do not stop arbitrary job code that can request its own token, so test egress from the
actual job environment, including connections that bypass any proxy ([egress-metadata.md](egress-metadata.md)).

## GitHub Actions self-hosted runner

GitHub's own guidance is to "only use self-hosted runners with private repositories", because a fork of
a public repository "can potentially run dangerous code on your self-hosted runner machine by creating
a pull request that executes the code in a workflow". Keep self-hosted runners off public repositories.
Runner groups are the control: only private repositories can use a runner group by default, and the
override that admits public repositories should stay off. An ordinary fork `pull_request` run receives a
read-only `GITHUB_TOKEN` and, on the default fork settings, none of your other secrets, but the code
still executes on your host, so it can already read host-resident credentials, files, and reachable
services; host persistence (a poisoned tool or harvested credential left for a later, more privileged
job on the same machine) only compounds it. The `pull_request_target` and `workflow_run` triggers can access secrets and a write token, so never check out
or execute untrusted pull-request code (or scripts from untrusted artifacts or caches) in those privileged
workflows; a fresh ephemeral runner does not protect credentials supplied to the same job. Keep privileged
workflows on separate, trusted, ephemeral workers, and review the private-repository fork-workflow settings,
which can themselves grant write tokens and secrets.

Several credentials pass through a runner, and they are not interchangeable. The registration token is
a short-lived bootstrap value (documented one-hour lifetime); generate it on demand, never bake it into
an image, and note that its expiry does not deregister a runner already registered with it. Keep the
admin-scoped credential that generates it (a GitHub App installation or a PAT) off the runner host and in a
separate management service, since it outranks anything the runner holds; use the endpoint's documented minimum
(organization registration or JIT endpoints need `Self-hosted runners: write`, repository endpoints need
`Administration: write`) and expire or revoke it when no longer needed. A JIT
configuration (the `encoded_jit_config` the generate-jitconfig API returns) provisions a runner that
executes at most one job; protect the whole response. Once configured, the runner stores its own
authentication credential locally, so protect the install directory and any backups. `GITHUB_TOKEN` is
a per-job token scoped to the workflow's repository; set the default workflow permissions to read-only
and grant more only to the trusted job with an explicit `permissions:` key. Treat OIDC as another job
credential: grant `id-token: write` only to the deployment job that needs it, keep it out of the default
permissions, and configure the cloud provider to validate the issuer, audience and a narrowly scoped subject
for the intended repository and trusted branch or protected environment ([machine-auth.md](machine-auth.md)),
since any code in an authorized job can mint that token and use the cloud credentials it buys. Run the runner
service as a dedicated unprivileged user, never root and never in the `docker` group (membership is
root-equivalent), because a job executes with that account's authority ([docker.md](docker.md)). Prefer ephemeral or JIT
runners so one job cannot poison the next, run untrusted CI on a pool kept separate from deployment and
signing runners, and remember that deregistering an ephemeral runner does not destroy its disk: tearing
down the machine is your job. Labels only route jobs to runners; they do not authorize, so never treat
a label as a security boundary.

## GitLab Runner

The executor decides how much of the host a job controls, and it is the first thing to get right. The
shell executor runs the job directly as the runner's user with no isolation. The Docker executor is a
real boundary only when it is unprivileged: GitLab warns that with `privileged = true` "you are practically
disabling all of the security mechanisms of containers and exposing your host to privilege escalation, which
can lead to container breakout", and mounting `/var/run/docker.sock` (or reaching a rootful daemon over TCP)
hands over the daemon's host even with `privileged = false`. For untrusted work use an unprivileged Docker or a hardened Kubernetes executor on isolated disposable workers,
never shell on a shared host, never the socket, and never `services_privileged`; build images without the host
daemon rather than mounting it. Deny job access to the host Docker daemon, sensitive host mounts, host
PID/network namespaces, unnecessary devices and elevated capabilities; for Kubernetes enforce non-privileged
containers, disable privilege escalation, restrict the service-account RBAC, and disable automatic
service-account-token mounting where jobs do not need it, and prevent job configuration from overriding those
restrictions. Containers share the host kernel, so use separate disposable VMs or nodes where that boundary is
insufficient. Make workers disposable, one job each, with an autoscaling executor, since a persistent worker
lets one job poison the next.

The tokens are distinct credentials. The legacy registration token was disabled by default in GitLab 17.0 and removed in 18.0; registration now uses
the runner authentication token, which lives in `config.toml`, so protect that file and its backups and rotate
the token on any exposure, because a cloned runner using the same token silently steals the jobs meant for the
original. The access token that creates a runner (through `POST /user/runners`, needing the `create_runner`
scope) is a separate, more powerful credential: keep it off the worker, and set runner scope and protection at
creation rather than assuming legacy registration arguments still configure them. `CI_JOB_TOKEN` carries the triggering user's access to the resources it
supports for the job's
lifetime, and it is also `CI_REGISTRY_PASSWORD` and is embedded in `CI_REPOSITORY_URL`, so restrict inbound
job-token access on each target project that holds sensitive resources: that allowlist controls whose job
tokens may reach the target, not where this job's token may go, and some resources stay reachable outside it
unless you also restrict their feature visibility. An instance-wide runner on an installation with public
projects accepts strangers' code just as a public-repository GitHub runner does. A project-scoped runner limits
which project can assign it, not the provenance of the code it runs: a parent-project member can launch a fork
merge-request pipeline using the fork's configuration with parent-project resources, so review that code before
launching it or disable `ci_allow_fork_pipelines_to_run_in_parent_project`. Any user with the Developer role can
compromise a non-ephemeral runner, so use protected runners with `access_level: ref_protected` for protected
refs and keep them separate from the pool that tests forked merge requests. The runner opens no inbound listener unless you configure one. The Prometheus metrics endpoint (set through
`listen_address` or `gitlab-runner run --listen-address`, and also via Helm/Operator config) has no built-in
authorization and also exposes profiling endpoints; `9252` is the allocated port, not proof of the configured
one. The optional `[session_server]` listener uses TLS and must be reachable by GitLab at its configured
address (`8093` is an example), so restrict it to the required GitLab traffic rather than only to monitoring
clients. Enable neither unless needed, and firewall each to the clients that need it when you do.

## Verify

Both runners are outbound-only job pollers, so most checks are posture and REST audits, not reachability
probes. Every check that needs a live registered runner or worker is reasoned, not demonstrated: the authoring
environment has no container runtime, registered test runner, or cloud test infrastructure, so those outcomes
are derived from the cited vendor pages rather than observed, and backlog row 2.29 tracks demonstrating them.
Require successful, complete listings; authentication errors, unavailable endpoints, and incomplete pagination
are inconclusive. Run the REST and config checks from an administrator workstation using stored CLI credentials.

GitHub eligibility: `visibility: all` does not by itself mean public access, and `allows_public_repositories`
is a separate control, so list every runner group, then each selected group's repositories, then every public
repository's own runners (a repository-level runner belongs to no group).

```bash
gh api -X GET --paginate -H 'X-GitHub-Api-Version: 2026-03-10' /orgs/REPLACE_WITH_ORG/actions/runner-groups --jq '.runner_groups[] | {id, name, visibility, allows_public_repositories, inherited, restricted_to_workflows, selected_workflows}'
gh api -X GET --paginate -H 'X-GitHub-Api-Version: 2026-03-10' /orgs/REPLACE_WITH_ORG/actions/runner-groups/REPLACE_WITH_GROUP_ID/repositories --jq '.repositories[] | {id, full_name, visibility}'
gh api -X GET --paginate -H 'X-GitHub-Api-Version: 2026-03-10' /repos/REPLACE_WITH_OWNER/REPLACE_WITH_REPO/actions/runners --jq '.runners[] | {id, name, status}'
```

Check every selected repository's visibility and trust level, including inherited groups: a public repository
must have neither a repository-level self-hosted runner nor access through a group, and private or internal
repositories still need review of who can submit executable workflow code. Then confirm the default token
posture and that workflow approval of pull requests is off unless required (a workflow can still raise its own
permissions with an explicit `permissions:` key, and OIDC `id-token` is separate):

```bash
gh api -H 'X-GitHub-Api-Version: 2026-03-10' /orgs/REPLACE_WITH_ORG/actions/permissions/workflow --jq '{default_workflow_permissions, can_approve_pull_request_reviews}'
gh api -H 'X-GitHub-Api-Version: 2026-03-10' /repos/REPLACE_WITH_OWNER/REPLACE_WITH_REPO/actions/permissions/workflow --jq '{default_workflow_permissions, can_approve_pull_request_reviews}'
```

The eligibility listing shows configuration; the behavioral proof is reasoned, not demonstrated (backlog row
2.29): in an isolated test organization use a disposable runner with no sensitive credentials or internal
network access, install this workflow in a public test repository, and open a controlled fork pull request.

```yaml
name: runner-eligibility-probe
on: pull_request
permissions: {}
jobs:
  probe:
    runs-on: [self-hosted, ci-audit-probe]
    steps:
      - run: printf '%s\n' eligibility-probe
```

Assign `ci-audit-probe` to the test runner. With eligibility deliberately exposed the approved run must execute
on it; after applying the private-repository restriction an equivalent fork run must not be assigned to it, and
the same harmless job from an allowed private repository confirms the runner is still available. Inspect the
assignment, and treat a skipped workflow, pending approval, offline runner, or queue timeout as inconclusive:

```bash
gh api --paginate -H 'X-GitHub-Api-Version: 2026-03-10' /repos/REPLACE_WITH_OWNER/REPLACE_WITH_REPO/actions/runs/REPLACE_WITH_RUN_ID/jobs --jq '.jobs[] | {id, status, conclusion, runner_id, runner_group_id}'
```

For GitLab, inspect the configuration each runner service actually loads (custom paths and
deployment-generated config included). This Python 3.11+ inspection decodes TOML and preserves the runner block
without printing tokens; `null` means absent, and empty output, read errors, or parse errors are inconclusive.
A `privileged = true`, a `docker.sock` volume or a `host` pointing at a rootful daemon, `services_privileged`,
or an autoscaler with neither `capacity_per_instance` nor `max_use_count` set to `1` is the finding.

```bash
sudo python3 - /etc/gitlab-runner/config.toml <<'PYTOML'
import json, sys, tomllib
with open(sys.argv[1], "rb") as source:
    config = tomllib.load(source)
for index, runner in enumerate(config.get("runners", [])):
    fields = {
        "docker": ("privileged", "services_privileged", "host", "volumes", "volumes_from", "devices", "cap_add", "security_opt", "pid_mode", "network_mode"),
        "kubernetes": ("privileged", "allow_privilege_escalation", "automount_service_account_token", "service_account"),
        "autoscaler": ("capacity_per_instance", "max_use_count"),
    }
    report = {"runner_index": index, "executor": runner.get("executor")}
    for section, keys in fields.items():
        report[section] = {key: runner.get(section, {}).get(key) for key in keys}
    print(json.dumps(report))
PYTOML
```

Read the GitLab job-token allowlist and runner scope from the API and require a release runner's `access_level`
to be `ref_protected`, comparing against an isolated control with unrestricted inbound access or `not_protected`;
`gitlab-runner verify` only confirms authentication, nothing about isolation.

```bash
glab api --hostname REPLACE_WITH_GITLAB_HOST projects/REPLACE_WITH_PROJECT_ID/job_token_scope
glab api --hostname REPLACE_WITH_GITLAB_HOST --paginate projects/REPLACE_WITH_PROJECT_ID/job_token_scope/allowlist
glab api --hostname REPLACE_WITH_GITLAB_HOST --paginate projects/REPLACE_WITH_PROJECT_ID/job_token_scope/groups_allowlist
glab api --hostname REPLACE_WITH_GITLAB_HOST runners/REPLACE_WITH_RUNNER_ID
```

Lifecycle and contamination are reasoned (backlog row 2.29): an ephemeral or JIT GitHub runner should be gone
from a fully paginated `gh api /orgs/REPLACE_WITH_ORG/actions/runners` after a harmless job, but deregistration
is not proof the machine was destroyed, and a GitLab runner manager can stay registered while its workers are
replaced, so verify termination and storage disposal through the infrastructure provider. Test reuse with two
sequential harmless jobs: job A runs `printf '%s\n' ci-isolation-canary > "$HOME/.ci-isolation-canary"`, and job
B runs `if test -e "$HOME/.ci-isolation-canary"; then echo 'FAIL: previous job state survived'; exit 1; else echo 'canary absent; corroborate worker destruction'; fi`. A deliberately persistent worker must find the marker;
the hardened case uses a newly provisioned worker with disposal records and no marker. Marker absence alone is
insufficient, and worker destruction does not remove shared caches or artifacts, so review those separately.

Finally, `ss` is an inventory only; inspect the relevant container and pod namespaces and published ports too.
If a metrics or session-server listener is enabled, run the guarded block against the exact configured URL from
an allowed monitoring client (the positive control must return the expected response) and from a disallowed
network; any HTTP response from the disallowed network proves reachability, while a timeout, DNS error, or
connection failure is inconclusive without a matching firewall deny record. This reachability comparison is
reasoned, since no deployed endpoint or external vantage was available. Substitute the URL inside the single
quotes and paste the whole block; do not bypass TLS certificate verification.

```bash
sudo ss -tlnp
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_METRICS_URL'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 1 ] || { echo 'exactly one URL required; not probing'; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|'') echo 'substitute the URL inside the quotes; not probing'; exit 2 ;;
  esac
  case "$1" in
    http://*|https://*) ;;
    *) echo 'HTTP or HTTPS URL required; not probing'; exit 2 ;;
  esac
  curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -o /dev/null -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"
)
```

## Sources (checked September 2026)

Version boundary: GitHub.com documentation checked 18 September 2026, with REST examples pinned to API version `2026-03-10`; GitLab documentation is rolling, checked that date. The legacy GitLab registration token was disabled by default in Runner 17.0 and removed in 18.0, and the Instance and Docker Autoscaler executors became generally available in Runner 17.1; run a currently supported patched release. No live product-version compatibility matrix was exercised.

- GitHub Actions security hardening and secure use: https://docs.github.com/en/actions/reference/security/secure-use
- GitHub self-hosted runner groups and access (private-only default): https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/manage-access
- GitHub self-hosted runners REST API (generate-jitconfig, listings): https://docs.github.com/en/rest/actions/self-hosted-runners
- GitHub GITHUB_TOKEN permissions: https://docs.github.com/en/actions/concepts/security/github_token
- GitHub events that trigger workflows (pull_request_target, workflow_run): https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- GitLab Runner security (privileged executor, tokens): https://docs.gitlab.com/runner/security/
- GitLab Runner Docker executor: https://docs.gitlab.com/runner/executors/docker/
- GitLab CI_JOB_TOKEN and the job-token allowlist: https://docs.gitlab.com/ci/jobs/ci_job_token/
- GitLab runner authentication tokens and the creation workflow: https://docs.gitlab.com/ci/runners/new_creation_workflow/
- GitLab Runner monitoring (metrics port 9252, no built-in authorization): https://docs.gitlab.com/runner/monitoring/
- GitLab Runner advanced configuration (session_server): https://docs.gitlab.com/runner/configuration/advanced-configuration/
- GitHub self-hosted runner groups REST API (group visibility, allows_public_repositories, group repositories): https://docs.github.com/en/rest/actions/self-hosted-runner-groups
- GitHub Actions OIDC (id-token permission, issuer/audience/subject claims): https://docs.github.com/en/actions/reference/security/oidc
- GitHub workflow-jobs REST API (runner assignment: runner_id, runner_group_id): https://docs.github.com/en/rest/actions/workflow-jobs
- GitLab ID token authentication (id_tokens, aud): https://docs.gitlab.com/ci/secrets/id_token_authentication/
- GitLab Users API, create a runner (create_runner scope): https://docs.gitlab.com/api/users/#create-a-runner-linked-to-a-user
- GitLab Kubernetes executor (privileged, privilege escalation, service-account RBAC and token mounting): https://docs.gitlab.com/runner/executors/kubernetes/
- GitLab Instance and Docker Autoscaler executors (capacity_per_instance, max_use_count): https://docs.gitlab.com/runner/executors/docker_autoscaler/
- GitLab project job-token scopes API (inbound allowlist): https://docs.gitlab.com/api/project_job_token_scopes/
- Docker Engine security (rootful daemon, docker group as host administration): https://docs.docker.com/engine/security/
- AWS EC2 instance metadata service (IMDSv2 does not stop authorized in-job requests): https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- Python tomllib (offline config.toml inspection, Python 3.11+): https://docs.python.org/3.11/library/tomllib.html
