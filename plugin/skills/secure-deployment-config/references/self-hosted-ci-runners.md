# Self-hosted CI runners: GitHub Actions and GitLab Runner

A self-hosted runner exists to execute CI job commands on your own machine, so the trust question is
not a bind address but who can cause code to run on it. Both GitHub Actions runners and GitLab Runner
are outbound-only: they poll their service over HTTPS and open no inbound job-transport listener, so
no inbound opening is needed to receive jobs, and the controls are eligibility (whose code the runner
will run), credentials (what a job can reach), executor privilege (how isolated the job is from the
host), and lifecycle (what survives after a job). Get those wrong and an untrusted job is remote code
execution with the runner's permissions and network position: it can steal the credentials the job
legitimately receives, poison caches and tools that later trusted builds consume, and pivot from the
runner's place in your network, including the cloud metadata endpoint
([egress-metadata.md](egress-metadata.md)).
Isolate runners from production and from each other, and handle every token as [secrets.md](secrets.md)
describes.

## GitHub Actions self-hosted runner

GitHub's own guidance is to "only use self-hosted runners with private repositories", because a fork of
a public repository "can potentially run dangerous code on your self-hosted runner machine by creating
a pull request that executes the code in a workflow". Keep self-hosted runners off public repositories.
Runner groups are the control: only private repositories can use a runner group by default, and the
override that admits public repositories should stay off. An ordinary fork `pull_request` run receives a
read-only `GITHUB_TOKEN` and, on the default fork settings, none of your other secrets, but the code
still executes on your host, so it can already read host-resident credentials, files, and reachable
services; host persistence (a poisoned tool or harvested credential left for a later, more privileged
job on the same machine) only compounds it. The `pull_request_target` and `workflow_run` triggers can
run with repository secrets, so never run them on a runner that also handles untrusted code or persists
between jobs; keep them to trusted, ephemeral runners, and review the private-repository fork-workflow
settings, which can themselves grant write tokens and secrets.

Several credentials pass through a runner, and they are not interchangeable. The registration token is
a short-lived bootstrap value (documented one-hour lifetime); generate it on demand, never bake it into
an image, and note that its expiry does not deregister a runner already registered with it. A JIT
configuration (the `encoded_jit_config` the generate-jitconfig API returns) provisions a runner that
executes at most one job; protect the whole response. Once configured, the runner stores its own
authentication credential locally, so protect the install directory and any backups. `GITHUB_TOKEN` is
a per-job token scoped to the workflow's repository; set the default workflow permissions to read-only
and grant more only to the trusted job with an explicit `permissions:` key. Prefer ephemeral or JIT
runners so one job cannot poison the next, run untrusted CI on a pool kept separate from deployment and
signing runners, and remember that deregistering an ephemeral runner does not destroy its disk: tearing
down the machine is your job. Labels only route jobs to runners; they do not authorize, so never treat
a label as a security boundary.

## GitLab Runner

The executor decides how much of the host a job controls, and it is the first thing to get right. The
shell executor runs the job directly as the runner's user with no isolation. The Docker executor is a
real boundary only when it is unprivileged: `privileged = true` gives the job, in GitLab's words,
"disabling all the container's security mechanisms", which is root on the host through a container
breakout, and mounting `/var/run/docker.sock` (or reaching a rootful daemon over TCP) hands over the
daemon's host even with `privileged = false`. For untrusted work use an unprivileged Docker or a
Kubernetes executor, never shell, never the socket, and never `services_privileged`; build images
without the host daemon rather than mounting it. Make workers disposable, one job each, with an
autoscaling executor, since a persistent worker lets one job poison the next.

The tokens are distinct credentials. The legacy registration token is deprecated; migrate to the
runner authentication token, which lives in `config.toml`, so protect that file and its backups and
rotate the token on any exposure, because a cloned runner using the same token silently steals the jobs
meant for the original. `CI_JOB_TOKEN` carries the triggering user's access to the resources it
supports for the job's
lifetime, and it is also `CI_REGISTRY_PASSWORD` and is embedded in `CI_REPOSITORY_URL`, so keep the
project's job-token allowlist restrictive. A runner scoped to a single project limits the trust to that
project's contributors; any user with the Developer role there can compromise a non-ephemeral runner,
so use protected runners for protected refs and keep them separate from the pool that tests forked
merge requests. The runner opens no inbound listener unless you configure one: a Prometheus metrics
endpoint (the Prometheus-allocated port `9252`) is served "without any authorization" when a
`listen_address` is set, and the interactive session server (documented example `:8093`) is another;
enable neither unless needed, and firewall it to a monitoring network when you do.

## Verify

Both runners are outbound-only pollers, so there is usually no inbound listener to reach and these are
posture checks, not reachability probes. Every check that needs a live registered runner is reasoned,
not demonstrated: the authoring environment has no container runtime and no registered test runner, so
those outcomes are derived from the cited vendor pages rather than observed, and backlog row 2.29 tracks
demonstrating them. The `config.toml` inspection below needs neither a runner nor a
network, so run it, but read the result as TOML: a `grep` is only a first pass that surfaces the lines
to judge, since it does not separate a comment from an active setting, resolve which runner block a
value belongs to, or reach a config kept at a non-default path (root and user installs differ).

```bash
# GitHub eligibility: a self-hosted runner visible to a public repo, or an all-repositories group, is
# the exposed state; fixed is groups restricted to selected private repositories.
gh api -X GET /orgs/REPLACE_WITH_ORG/actions/runner-groups --jq '.runner_groups[] | {name, visibility, allows_public_repositories}'
# GitHub default token posture: the org/repo default workflow permission should be read, not write.
gh api /orgs/REPLACE_WITH_ORG/actions/permissions/workflow --jq '.default_workflow_permissions'
# GitLab config.toml: a privileged executor, the docker socket, or a persistent worker is the exposure.
grep -nE 'executor|privileged|services_privileged|/var/run/docker.sock|capacity_per_instance|max_use_count' /etc/gitlab-runner/config.toml
# Host listener inventory on the runner: no runner-owned inbound listener except a deliberately
# configured metrics (9252) or session server (8093), each of which must be justified and firewalled.
sudo ss -tlnp
```

For GitHub, an ephemeral or JIT runner is gone from `gh api /orgs/REPLACE_WITH_ORG/actions/runners`
after a harmless job, while a persistent runner still idling is the exposed state; deregistration is not
proof the machine was destroyed. For GitLab, `privileged = true`, a `docker.sock`
volume, or `services_privileged = true` present is the finding; but the one-job limits are the reverse,
for an Instance or Docker Autoscaler executor a worker with neither `capacity_per_instance` nor
`max_use_count` set reuses across jobs by default, so their absence is the finding and you confirm both
are present and set to `1`; a plain Docker or Kubernetes executor gives a fresh container or pod per job
but does not itself destroy the host or its storage, so check that executor's own disposal instead.
`gitlab-runner verify` only confirms that configured runners can
authenticate, nothing about isolation. Read the job-token allowlist and the runner's project scope in
the API, and confirm a release runner's `access_level` reads `ref_protected`. These checks discriminate on the
content of a listing or a file, so they take the plain form; only an optional nothing-answered probe of
an exposed metrics or session port from outside would need the guarded-subshell form, so an
unsubstituted address cannot time out and read as closed.

## Sources (checked September 2026)

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
