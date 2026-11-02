# Self-hosted CI runners: GitHub Actions and GitLab Runner

GitHub Actions self-hosted runners and GitLab Runner run CI jobs on machines you manage. This guide helps your AI assistant configure runners securely, including limits on whose code can start jobs, untrusted jobs on isolated disposable workers apart from deployment runners, narrow credentials, and egress enforced outside the job.

<a id="ai-assistant-prompt"></a>

If an AI assistant is helping you secure a deployment, give it the prompt below:

```text
Read the secureconfig guide at
https://raw.githubusercontent.com/jposluns/secureconfig/main/self-hosted-ci-runners.md
in full, including the section for AI assistants at the end. Then, for my
deployment: state which of its recommendations apply and the exact changes
to make; compare the versions the guide was written against with the
releases I am running and with the vendor's current releases, and flag any
guidance a newer release may have changed; and run or adapt the guide's
Verify steps where you can. List separately every item you could not
verify instead of reporting it as passed.
```

Written against GitHub Actions documentation (no recorded version), GitHub REST API 2026-03-10, GitLab Runner source v19.5.0, and Python tomllib minimum 3.11; 3 further sources carry no recorded version. Metadata reviewed 2026-10-21; documentation checked September 2026. The guide records 37 claims: 1 demonstrated by a check that ran and 36 reasoned from cited sources.

A newer release of any of this software can make version-specific details here outdated. To prioritize an update, open a GitHub issue, send a pull request, add a request under [requests/](requests/README.md), or reach the maintainer as [CONTRIBUTING.md](CONTRIBUTING.md) describes. The machine-readable version basis and claim list are in [the section for AI assistants](#about-the-ai-assistant-section-below) at the end of this guide.

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
separate management service, since it outranks anything the runner holds. The permission and lifetime rule for that admin-scoped
credential is to use the endpoint's documented minimum (organization registration or JIT endpoints need
`Self-hosted runners: write`, repository endpoints need `Administration: write`) and to expire or revoke that
admin-scoped credential when no longer needed. A JIT
configuration (the `encoded_jit_config` the generate-jitconfig API returns) provisions a runner that
executes at most one job; protect the whole response. Once configured, the runner stores its own
authentication credential locally, so protect the install directory and any backups. `GITHUB_TOKEN` is
a per-job token scoped to the workflow's repository; set the default workflow permissions to read-only
and grant more only to the trusted job with an explicit `permissions:` key. Treat OIDC as another job
credential: grant `id-token: write` only to the deployment job that needs it, keep it out of the default
permissions, and configure the cloud provider to validate the issuer, audience and a narrowly scoped subject
for the intended repository and trusted branch or protected environment ([machine-auth.md](machine-auth.md)).
Those OIDC controls matter because any code in an authorized job can mint the OIDC token and use the cloud
credentials it buys. Run the runner
service as a dedicated unprivileged user, never root and never in the `docker` group (membership is
root-equivalent), because a job executes with that account's authority ([docker.md](docker.md)). Prefer ephemeral or JIT
runners so one job cannot poison the next, run untrusted CI on a pool kept separate from deployment and
signing runners, and remember that deregistering an ephemeral runner does not destroy its disk: tearing
down the machine is your job. Labels only route jobs to runners; they do not authorize, so never treat
a label as a security boundary.

## GitLab Runner

The executor decides how much of the host a job controls, and it is the first thing to get right. The
shell executor runs the job directly as the runner's user with no isolation. The Docker executor is a
real boundary only when it is unprivileged: GitLab warns that with `privileged = true` "you are effectively
disabling all the container's security mechanisms", exposing the host to privilege escalation and container
breakout. Mounting `/var/run/docker.sock` (or reaching a rootful daemon over TCP)
hands over the daemon's host even with `privileged = false`. For untrusted work use an unprivileged Docker or a hardened Kubernetes executor on isolated disposable workers,
never shell on a shared host, never the socket, and never `services_privileged`; build images without the host
daemon rather than mounting it. Deny job access to the host Docker daemon, sensitive host mounts, host
PID/network namespaces, unnecessary devices and elevated capabilities. The Kubernetes executor needs the following
controls: enforce non-privileged
containers, disable privilege escalation, restrict the service-account RBAC, and disable automatic
service-account-token mounting where jobs do not need it, and prevent job configuration from overriding those
restrictions. Containers share the host kernel, so use separate disposable VMs or nodes where that boundary is
insufficient. Make workers disposable, one job each, with an autoscaling executor, since a persistent worker
lets one job poison the next.

The tokens are distinct credentials. The legacy registration token was disabled by default in GitLab 17.0; removal is currently scheduled for GitLab 20.0. Use
the runner authentication token, which lives in `config.toml`, so protect that file and its backups and rotate
the token on any exposure, because a cloned runner using the same token silently steals the jobs meant for the
original. The access token that creates a runner (through `POST /user/runners`, needing the `create_runner`
scope) is a separate, more powerful credential: keep it off the worker, and set runner scope and protection at
creation rather than assuming legacy registration arguments still configure them. `CI_JOB_TOKEN` carries the triggering user's access to the resources it
supports for the job's
lifetime, and it is also `CI_REGISTRY_PASSWORD` and is embedded in `CI_REPOSITORY_URL`, so restrict inbound
job-token access on each target project that holds sensitive resources. That inbound job-token allowlist controls whose job
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

REASONED: Both runners are outbound-only job pollers, so most checks are posture and REST audits, not reachability
probes. Every check that needs a live registered runner or worker is reasoned, not demonstrated: the authoring
environment has no container runtime, registered test runner, or cloud test infrastructure, so those outcomes
are derived from the cited vendor pages rather than observed. Offline outcomes are recorded below: `tomllib` fixtures,
jq filters on synthetic REST-shaped JSON, a PyYAML parse of the probe workflow, a stub `glab` run, the canary commands, plain ss -tln without sudo listing this host's listeners, the guarded listener block with stub `sudo` and `curl`, and bash -n and ShellCheck syntax checks.
Those records say which form each run covered; the current blocks are covered by the repository gate suite's bash -n and ShellCheck 0.11.0 passes over every block and by the October 2026 stub runs recorded at each block.
Require successful, complete listings; authentication errors, unavailable endpoints, and incomplete pagination
are inconclusive. Run the REST and config checks from an administrator workstation using stored CLI credentials.

REASONED: eligibility semantics per the guide's cited GitHub self-hosted runner groups REST API and runner groups and access entries; no GitHub organization or registered test runner is available in the authoring environment, so no listing was read. At marking time the three jq filters in the block below, run with jq 1.8.1 on synthetic REST-shaped JSON, printed the named fields, including allows_public_repositories true for an exposed group and false for a fixed one; the gh client's own --jq handling was not exercised. GitHub eligibility: `visibility: all` does not by itself mean public access, and `allows_public_repositories`
is a separate control, so list every runner group, then each selected group's repositories, then every public
repository's own runners (a repository-level runner belongs to no group). Those filter runs predate the
block's guarded values and exit status, though its three filters are unchanged.

REASONED: following block; GitHub eligibility audit follows the cited runner-group and runner REST documentation; no registered test runner or cloud test infrastructure was available. The block takes your organization's login, a runner group ID and a public repository's owner and name on a guarded `set --` line. It records a finding (1) when any runner group shows `allows_public_repositories` true, the exposed reading above, and 3 when a listing fails or the group listing shows no such value; the groups' other fields, the group's repositories and the repository's own runners are left for you to judge. This form is covered by the repository gate suite's bash -n and ShellCheck 0.11.0 passes over every block, and by October 2026 stub runs with gh stubbed: a group listing showing only false exited 0, one group showing true exited 1 (also when a later listing failed), a failed listing or a listing without the field exited 3, and each `set --` refusal exited 2 before any gh call.

```bash
(                                       # the whole block in one subshell, so one exit status covers all three listings
  set +e                                # errexit off here, so a listing that ends nonzero is folded into the status below instead of ending the block
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ORG' 'REPLACE_WITH_GROUP_ID' 'REPLACE_WITH_OWNER' 'REPLACE_WITH_REPO'   # your organization's login, a runner group ID (the first listing prints them), then the owner and name of a public repository: replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 4 ] || { echo "the set -- line needs exactly 4 values; not probing"; exit 2; }
  case "$1" in
    ""|*REPLACE_WITH_*|*[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-]*) echo "substitute your organization's login (letters, digits and hyphens) inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  case "$2" in
    ""|*REPLACE_WITH_*|*[!0123456789]*) echo "substitute a runner group ID (digits) inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  case "$3" in
    ""|*REPLACE_WITH_*|*[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-]*) echo "substitute the repository owner's login (letters, digits and hyphens) inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  case "$4" in
    ""|.|..|*REPLACE_WITH_*|*[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-]*) echo "substitute the repository name (letters, digits, dots, underscores and hyphens) inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  set -- "$1" "$2" "$3" "$4" 0          # the 5th value is the block's status so far: 1 (a finding) outranks 3 (inconclusive), which outranks 0
  set -- "$1" "$2" "$3" "$4" "$5" "$(if gh api -X GET --paginate -H 'X-GitHub-Api-Version: 2026-03-10' "/orgs/$1/actions/runner-groups" --jq '.runner_groups[] | {id, name, visibility, allows_public_repositories, inherited, restricted_to_workflows, selected_workflows}'; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "$3" "$4" "$5" "${6##*$'\n'}" "${6%$'\n'*}"   # gh's exit status, then the group listing
  printf '%s\n' "$7"
  case "$6:$7" in
    0:*'"allows_public_repositories":true'*|0:*'"allows_public_repositories": true'*) echo "FINDING: a runner group allows public repositories"; set -- "$1" "$2" "$3" "$4" 1 ;;
    0:*'"allows_public_repositories":false'*|0:*'"allows_public_repositories": false'*) ;;
    0:*) echo "the group listing showed no allows_public_repositories value; inconclusive"; set -- "$1" "$2" "$3" "$4" 3 ;;
    *) echo "gh exit $6: the runner-group listing failed; inconclusive"; set -- "$1" "$2" "$3" "$4" 3 ;;
  esac
  gh api -X GET --paginate -H 'X-GitHub-Api-Version: 2026-03-10' "/orgs/$1/actions/runner-groups/$2/repositories" --jq '.repositories[] | {id, full_name, visibility}' ||
    { echo "gh exit $?: the group's repository listing failed; inconclusive"; [ "$5" = 1 ] || set -- "$1" "$2" "$3" "$4" 3; }
  gh api -X GET --paginate -H 'X-GitHub-Api-Version: 2026-03-10' "/repos/$3/$4/actions/runners" --jq '.runners[] | {id, name, status}' ||
    { echo "gh exit $?: the repository's runner listing failed; inconclusive"; [ "$5" = 1 ] || set -- "$1" "$2" "$3" "$4" 3; }
  echo "block exit $5; each group's other fields, the group's repositories and the repository's own runners are not classified, so judge them yourself"
  exit "$5"
)
```

REASONED: following block; the repository review in this paragraph and the organization and repository workflow-permission reads in the block below, per the guide's cited GitHub GITHUB_TOKEN permissions and GitHub self-hosted runner groups and access entries; no GitHub organization or repository is available in the authoring environment, so no setting was read. At marking time the block passed bash -n and ShellCheck 0.11.0, and its jq filter on synthetic JSON printed write and true for an exposed posture and read and false for a fixed one. Those runs covered the block's earlier form. The current form takes your organization's login and a repository's owner and name on a guarded `set --` line, records a finding (1) when either read shows write or true and 3 when a read fails or shows neither value, and exits 0 for read and false in both. It reports `can_approve_pull_request_reviews` true as a finding (a finding unless your workflows require it), so where they do, the block exits 1 and that FINDING line is the expected setting for you to judge. It is covered by the repository gate suite's bash -n and ShellCheck 0.11.0 passes over every block, and by October 2026 stub runs with gh stubbed: read and false in both exited 0, write or true in either exited 1, a failed read or unrecognized output exited 3, and each `set --` refusal exited 2. Check every selected repository's visibility and trust level, including inherited groups: a public repository
must have neither a repository-level self-hosted runner nor access through a group, and private or internal
repositories still need review of who can submit executable workflow code. Then confirm the default token
posture and that workflow approval of pull requests is off unless required (a workflow can still raise its own
permissions with an explicit `permissions:` key, and OIDC `id-token` is separate):

```bash
(                                       # the whole block in one subshell, so one exit status covers both reads
  set +e                                # errexit off here, so a read that ends nonzero is folded into the status below instead of ending the block
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_ORG' 'REPLACE_WITH_OWNER' 'REPLACE_WITH_REPO'   # your organization's login, then the owner and name of a repository: replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 3 ] || { echo "the set -- line needs exactly 3 values; not probing"; exit 2; }
  case "$1" in
    ""|*REPLACE_WITH_*|*[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-]*) echo "substitute your organization's login (letters, digits and hyphens) inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  case "$2" in
    ""|*REPLACE_WITH_*|*[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-]*) echo "substitute the repository owner's login (letters, digits and hyphens) inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  case "$3" in
    ""|.|..|*REPLACE_WITH_*|*[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-]*) echo "substitute the repository name (letters, digits, dots, underscores and hyphens) inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  set -- "$1" "$2" "$3" 0               # the 4th value is the block's status so far: 1 (a finding) outranks 3 (inconclusive), which outranks 0
  set -- "$1" "$2" "$3" "$4" "$(if gh api -H 'X-GitHub-Api-Version: 2026-03-10' "/orgs/$1/actions/permissions/workflow" --jq '{default_workflow_permissions, can_approve_pull_request_reviews}'; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "$3" "$4" "${5##*$'\n'}" "${5%$'\n'*}"   # gh's exit status, then the organization's settings
  printf '%s\n' "$6"
  case "$5:$6" in
    0:*'"default_workflow_permissions":"write"'*|0:*'"default_workflow_permissions": "write"'*|0:*'"can_approve_pull_request_reviews":true'*|0:*'"can_approve_pull_request_reviews": true'*)
      echo "FINDING: the organization's default token can write or workflows can approve pull requests"; set -- "$1" "$2" "$3" 1 ;;
    0:*'"default_workflow_permissions":"read"'*|0:*'"default_workflow_permissions": "read"'*)
      case "$6" in
        *'"can_approve_pull_request_reviews":false'*|*'"can_approve_pull_request_reviews": false'*) ;;
        *) echo "the organization's settings showed no can_approve_pull_request_reviews value; inconclusive"; set -- "$1" "$2" "$3" 3 ;;
      esac ;;
    0:*) echo "the organization's settings showed no default_workflow_permissions value; inconclusive"; set -- "$1" "$2" "$3" 3 ;;
    *) echo "gh exit $5: the organization's workflow-permission read failed; inconclusive"; set -- "$1" "$2" "$3" 3 ;;
  esac
  set -- "$1" "$2" "$3" "$4" "$(if gh api -H 'X-GitHub-Api-Version: 2026-03-10' "/repos/$2/$3/actions/permissions/workflow" --jq '{default_workflow_permissions, can_approve_pull_request_reviews}'; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "$3" "$4" "${5##*$'\n'}" "${5%$'\n'*}"   # gh's exit status, then the repository's settings
  printf '%s\n' "$6"
  case "$5:$6" in
    0:*'"default_workflow_permissions":"write"'*|0:*'"default_workflow_permissions": "write"'*|0:*'"can_approve_pull_request_reviews":true'*|0:*'"can_approve_pull_request_reviews": true'*)
      echo "FINDING: the repository's default token can write or workflows can approve pull requests"; set -- "$1" "$2" "$3" 1 ;;
    0:*'"default_workflow_permissions":"read"'*|0:*'"default_workflow_permissions": "read"'*)
      case "$6" in
        *'"can_approve_pull_request_reviews":false'*|*'"can_approve_pull_request_reviews": false'*) ;;
        *) echo "the repository's settings showed no can_approve_pull_request_reviews value; inconclusive"; [ "$4" = 1 ] || set -- "$1" "$2" "$3" 3 ;;
      esac ;;
    0:*) echo "the repository's settings showed no default_workflow_permissions value; inconclusive"; [ "$4" = 1 ] || set -- "$1" "$2" "$3" 3 ;;
    *) echo "gh exit $5: the repository's workflow-permission read failed; inconclusive"; [ "$4" = 1 ] || set -- "$1" "$2" "$3" 3 ;;
  esac
  echo "block exit $4; each workflow's own permissions: key and its id-token grant are not shown here, so review them yourself"
  exit "$4"
)
```

REASONED: the eligibility workflow's expected behavior follows the cited vendor pages and is not demonstrated; the paragraph after the workflow below declares the workflow. The eligibility listing shows configuration; in an isolated test organization use a disposable runner with no sensitive credentials or internal
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

REASONED: preceding block; the eligibility-probe workflow above and the assignment comparison in this paragraph, per the guide's cited GitHub self-hosted runner groups and access, workflow-jobs REST API and events that trigger workflows entries. No isolated test organization, public test repository or disposable runner is available in the authoring environment, so no fork run was assigned or refused. At marking time PyYAML 6.0.3 parsed the workflow with empty permissions and the self-hosted and ci-audit-probe labels, reading its on key as boolean true under YAML 1.1, so this checked structure only, and the job-listing jq filter below printed a runner_id for an assigned synthetic job and null for an unassigned one. That filter run predates the listing block's guarded owner, repository and run ID values; that block now exits 3 when the listing fails and otherwise 0 with every job left for you to read, and it is covered by the repository gate suite's bash -n and ShellCheck 0.11.0 passes over every block and by October 2026 stub runs (a listing exited 0, a failed listing 3, each refusal 2). Assign `ci-audit-probe` to the test runner. With eligibility deliberately exposed the approved run must execute
on it; after applying the private-repository restriction an equivalent fork run must not be assigned to it, and
the same harmless job from an allowed private repository confirms the runner is still available. Inspect the
assignment, and treat a skipped workflow, pending approval, offline runner, or queue timeout as inconclusive:

```bash
(                                       # a subshell, so the exits below end only the subshell
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_OWNER' 'REPLACE_WITH_REPO' 'REPLACE_WITH_RUN_ID'   # the owner and name of the repository the probe ran in, then the run's numeric ID: replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 3 ] || { echo "the set -- line needs exactly 3 values; not probing"; exit 2; }
  case "$1" in
    ""|*REPLACE_WITH_*|*[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-]*) echo "substitute the repository owner's login (letters, digits and hyphens) inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  case "$2" in
    ""|.|..|*REPLACE_WITH_*|*[!ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-]*) echo "substitute the repository name (letters, digits, dots, underscores and hyphens) inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  case "$3" in
    ""|*REPLACE_WITH_*|*[!0123456789]*) echo "substitute the run's numeric ID inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  gh api --paginate -H 'X-GitHub-Api-Version: 2026-03-10' "/repos/$1/$2/actions/runs/$3/jobs" --jq '.jobs[] | {id, status, conclusion, runner_id, runner_group_id}' ||
    { echo "gh exit $?: the job listing failed; inconclusive"; exit 3; }
  echo "block exit 0; each job's status, conclusion and runner assignment are not classified, so judge them yourself"
)
```

REASONED: preceding block; assignment discrimination in the job listing above follows the cited workflow-jobs API and runner-group documentation, and no registered test runner or cloud test infrastructure was available. Following the cited GitLab and Docker documentation, inspect the configuration each runner service actually loads (custom paths and
deployment-generated config included); no live runner or daemon was tested. The inspection omits the runner `token` key, but reported fields are not redacted.
`null` means absent from the inspected table only, not a secure default. Unexpected types are inconclusive until corrected, except for the two autoscaler keys, where anything other than integer `1` is flagged. Empty output, read/parse/structure errors and partial output before an error are inconclusive; exit 0 alone is not a safety verdict.
`privileged = true`, `services_privileged = true`, or a host Docker socket mounted into a job is a finding. Unset `services_privileged` inherits `privileged`, so its `null` does not mean unprivileged services. The
reported `docker.host` selects the runner manager's Docker endpoint; resolve an absent value through the
service's `DOCKER_HOST` environment or the default Unix socket. Inspect the daemon's privilege, authentication
and network controls, and compare access from the actual job environment with an authorized management client.
Flag job access to a rootful daemon; a `tcp://` value alone does not establish that access. For an Instance or
Docker Autoscaler executor, flag either `capacity_per_instance` or `max_use_count` being absent or not integer
`1`; require both explicitly set to integer `1`, not a boolean, float or string.
For Kubernetes, flag `privileged = true`; require `allow_privilege_escalation`, and where jobs do not need tokens `automount_service_account_token`, explicitly set to boolean `false` (a printed `null` means the key is unset, so the requirement is not met); check the `service_account` name against the intended RBAC restrictions.

DEMONSTRATED: following block; the extracted Python program ran without sudo on 20 synthetic config.toml cases using Python 3.14.4. Docker fixtures printed true/true, a socket mount and a TCP host versus false/false, empty volumes and a null host; both exited 0. Autoscaler limits printed null/null, 1/2 and 2/1 versus 1/1, all exit 0. Kubernetes fixtures printed true versus false for the three booleans and the supplied service_account. Wrong-type strings, booleans and floats retained their JSON types; misplaced privileged printed docker.privileged null. Empty and runner-less files printed nothing and exited 0. Missing files, malformed TOML and wrong section types exited 1; the second-runner structure error followed one printed runner. Two valid runners printed indices 0 and 1. The runner token key was omitted; a dummy token copied into service_account was printed. These observations cover file inspection only. Those runs covered the block's earlier form, whose program printed these lines, ended with a traceback on any read, parse or structure error, and left the block's status to Python. The current program prints the same lines, then a FINDING line for each docker privileged or services_privileged true, docker.sock volume, Kubernetes runner with privileged true or without allow_privilege_escalation false, and Instance or Docker Autoscaler limit other than integer 1. It prints an inconclusive line for a wrong type in a classified Docker or Kubernetes key, an error or an empty runner list; the block exits 1 for any finding, otherwise 3 for any inconclusive line or when sudo or python3 does not run the program, otherwise 0. In October 2026 the current program ran without sudo on 21 synthetic config.toml cases using Python 3.14.4. The Docker privileged and socket-mount cases, the Kubernetes privileged and unset-escalation cases, the autoscaler null, 1/2, true and 1.0 cases, and a privileged runner followed by a structure error printed FINDING lines and exited 10. The fixed Docker, Kubernetes and autoscaler 1/1 cases, two fixed runners and a misplaced privileged key exited 0. Wrong-type strings, empty and runner-less files, a missing file, malformed TOML and a wrong section type printed inconclusive lines and exited 13, and no case printed the runner token. With sudo and python3 stubbed, the whole block turned 10, 13 and 0 into 1, 3 and 0, and exited 3 when sudo or python3 failed. The current form is covered by the repository gate suite's bash -n and ShellCheck 0.11.0 passes over every block and by these October 2026 fixture and stub runs, which, like the earlier runs, demonstrate synthetic file inspection only.

```bash
(                                       # a subshell, so the exits below end only the subshell
  if sudo python3 - /etc/gitlab-runner/config.toml <<'PYTOML'
import json, sys, tomllib
findings, doubts, count = list(), list(), 0
try:
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
        count += 1
        docker, kubernetes, autoscaler = report.get("docker"), report.get("kubernetes"), report.get("autoscaler")
        for key in ("privileged", "services_privileged"):
            if docker.get(key) is True:
                findings.append(f"runner {index}: docker.{key} is true")
            elif docker.get(key) is not None and docker.get(key) is not False:
                doubts.append(f"runner {index}: docker.{key} is not a boolean")
        volumes = docker.get("volumes")
        if volumes is not None and not (isinstance(volumes, list) and all(isinstance(volume, str) for volume in volumes)):
            doubts.append(f"runner {index}: docker.volumes is not a list of strings")
        elif any("docker.sock" in volume for volume in volumes or ()):
            findings.append(f"runner {index}: a docker.volumes entry mounts docker.sock")
        if report.get("executor") == "kubernetes":
            if kubernetes.get("privileged") is True:
                findings.append(f"runner {index}: kubernetes.privileged is true")
            elif kubernetes.get("privileged") is not None and kubernetes.get("privileged") is not False:
                doubts.append(f"runner {index}: kubernetes.privileged is not a boolean")
            if kubernetes.get("allow_privilege_escalation") is None or kubernetes.get("allow_privilege_escalation") is True:
                findings.append(f"runner {index}: kubernetes.allow_privilege_escalation is not explicitly false")
            elif kubernetes.get("allow_privilege_escalation") is not False:
                doubts.append(f"runner {index}: kubernetes.allow_privilege_escalation is not a boolean")
        if report.get("executor") in ("instance", "docker-autoscaler"):
            for key in ("capacity_per_instance", "max_use_count"):
                if type(autoscaler.get(key)) is not int or autoscaler.get(key) != 1:
                    findings.append(f"runner {index}: autoscaler.{key} is {json.dumps(autoscaler.get(key))}, not integer 1")
except Exception as error:
    doubts.append(f"read, parse or structure error: {type(error).__name__}: {error}")
if count == 0 and not doubts:
    doubts.append("no [[runners]] entry was read")
for line in findings:
    print("FINDING: " + line)
for line in doubts:
    print("inconclusive: " + line)
sys.exit(10 if findings else 13 if doubts else 0)
PYTOML
  then set -- 0; else set -- "$?"; fi    # Python exits 10 for a finding and 13 for an inconclusive result; any other nonzero status means sudo or python3 did not run the program
  case "$1" in
    0) echo "block exit 0; no classified finding, and the host, volumes_from, devices, cap_add, security_opt, pid_mode, network_mode, automount_service_account_token and service_account values are not classified, so judge them yourself"; exit 0 ;;
    10) echo "block exit 1; the values this check does not classify are left for you to judge as well"; exit 1 ;;
    13) echo "block exit 3; inconclusive, and the values this check does not classify are left for you to judge"; exit 3 ;;
    *) echo "sudo python3 exit $1: the configuration was not inspected; inconclusive"; exit 3 ;;
  esac
)
```

REASONED: the ref_protected requirement in this paragraph and the run records of the job-token scope, allowlist and runner reads in the block below, per the guide's cited GitLab project job-token scopes API and GitLab Runner security entries; no GitLab instance, project or registered runner is available in the authoring environment, so nothing was read. The paragraph after that block declares the block. At marking time the block's earlier form, which had no guard, passed bash -n and ShellCheck 0.11.0 and, against a stub glab, made four calls with its placeholders passed through unchanged. The current form takes the GitLab host, the project ID and a release runner's ID on a guarded `set --` line, records a finding (1) when the runner read shows not_protected and 3 when a read fails or the runner read shows neither value, and leaves the job-token scope and allowlists for you to judge. It is covered by the repository gate suite's bash -n and ShellCheck 0.11.0 passes over every block, and by October 2026 stub runs with glab stubbed: ref_protected exited 0, not_protected exited 1 (also when an earlier read failed), a failed read or a runner without access_level exited 3, and each `set --` refusal exited 2 before any glab call. A release runner at not_protected is the exposed state and ref_protected the fixed one. Read the GitLab job-token allowlist and runner scope from the API and require a release runner's `access_level`
to be `ref_protected`, comparing against an isolated control with unrestricted inbound access or `not_protected`;
`gitlab-runner verify` only confirms authentication, nothing about isolation.

```bash
(                                       # the whole block in one subshell, so one exit status covers all four reads
  set +e                                # errexit off here, so a read that ends nonzero is folded into the status below instead of ending the block
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_GITLAB_HOST' 'REPLACE_WITH_PROJECT_ID' 'REPLACE_WITH_RUNNER_ID'   # your GitLab host name, no scheme, user name, port, path, query, fragment, percent sign or trailing dot, then the numeric project ID, then a release runner's numeric ID: replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste the whole block, including its set -- line; not probing"; exit 2; }
  shift
  [ "$#" -eq 3 ] || { echo "the set -- line needs exactly 3 values; not probing"; exit 2; }
  case "$1" in
    ""|*REPLACE_WITH_*|*/*|*:*|*.|*[@?%]*|*'#'*|*[[:space:][:cntrl:]]*) echo "substitute your GitLab host name (no scheme, user name, port, path, query, fragment, percent sign or trailing dot) inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  case "$(printf '%s' "$1" | tr 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' 'abcdefghijklmnopqrstuvwxyz')" in   # host names ignore letter case; no named variable, so a declare -u in your shell cannot alter it
    example.com|example.net|example.org|*.example.com|*.example.net|*.example.org) echo "example.com, example.net, example.org and their subdomains are not your deployment: substitute your own host name on the set -- line above; not probing"; exit 2 ;;
  esac
  case "$2" in
    ""|*REPLACE_WITH_*|*[!0123456789]*) echo "substitute the numeric project ID inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  case "$3" in
    ""|*REPLACE_WITH_*|*[!0123456789]*) echo "substitute the release runner's numeric ID inside the quotes on the set -- line above; not probing"; exit 2 ;;
  esac
  set -- "$1" "$2" "$3" 0               # the 4th value is the block's status so far: 1 (a finding) outranks 3 (inconclusive), which outranks 0
  glab api --hostname "$1" "projects/$2/job_token_scope" ||
    { echo "glab exit $?: the job-token scope read failed; inconclusive"; set -- "$1" "$2" "$3" 3; }
  glab api --hostname "$1" --paginate "projects/$2/job_token_scope/allowlist" ||
    { echo "glab exit $?: the project allowlist read failed; inconclusive"; set -- "$1" "$2" "$3" 3; }
  glab api --hostname "$1" --paginate "projects/$2/job_token_scope/groups_allowlist" ||
    { echo "glab exit $?: the group allowlist read failed; inconclusive"; set -- "$1" "$2" "$3" 3; }
  set -- "$1" "$2" "$3" "$4" "$(if glab api --hostname "$1" "runners/$3"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "$3" "$4" "${5##*$'\n'}" "${5%$'\n'*}"   # glab's exit status, then the runner
  printf '%s\n' "$6"
  case "$5:$6" in
    0:*'"access_level":"not_protected"'*|0:*'"access_level": "not_protected"'*) echo "FINDING: the release runner's access_level is not_protected"; set -- "$1" "$2" "$3" 1 ;;
    0:*'"access_level":"ref_protected"'*|0:*'"access_level": "ref_protected"'*) ;;
    0:*) echo "the runner read showed neither ref_protected nor not_protected; inconclusive"; set -- "$1" "$2" "$3" 3 ;;
    *) echo "glab exit $5: the runner read failed; inconclusive"; set -- "$1" "$2" "$3" 3 ;;
  esac
  echo "block exit $4; the job-token scope and both allowlists are not classified, so judge them yourself"
  exit "$4"
)
```

REASONED: preceding block; the GitLab reads in the block above, per the guide's cited GitLab project job-token scopes API and GitLab Runner security entries, and the lifecycle and contamination checks in this paragraph, per the cited GitHub self-hosted runners REST API, GitLab Instance and Docker Autoscaler executors, and GitHub Actions security hardening entries. No registered runner, worker infrastructure or GitLab instance is available in the authoring environment. At marking time both canary commands passed bash -n and ShellCheck 0.11.0, and with job A and job B sharing one home directory job B printed its FAIL line and exited 1, while in a fresh home directory it printed the canary-absent line and exited 0; this exercises the marker logic only, not worker reuse or destruction. Lifecycle and contamination are REASONED from the cited vendor pages: an ephemeral or JIT GitHub runner should be gone
from a fully paginated `gh api /orgs/REPLACE_WITH_ORG/actions/runners` after a harmless job, but deregistration
is not proof the machine was destroyed, and a GitLab runner manager can stay registered while its workers are
replaced. The check those reasons call for is to verify termination and storage disposal through the infrastructure provider. Test reuse with two
sequential harmless jobs: job A runs `printf '%s\n' ci-isolation-canary > "$HOME/.ci-isolation-canary"`, and job
B runs `if test -e "$HOME/.ci-isolation-canary"; then echo 'FAIL: previous job state survived'; exit 1; else echo 'canary absent; corroborate worker destruction'; fi`. A deliberately persistent worker must find the marker;
the hardened case uses a newly provisioned worker with disposal records and no marker. Marker absence alone is
insufficient, and worker destruction does not remove shared caches or artifacts, so review those separately.

REASONED: listener inventory and reachability comparison per the guide's cited GitLab Runner monitoring and advanced configuration entries; no deployed metrics or session-server endpoint and no external vantage are available in the authoring environment, so no probe was sent. At marking time plain ss -tln without sudo listed this host's listeners, and the guarded probe's earlier form passed bash -n and ShellCheck 0.11.0 and, run with stub sudo and curl under bash and bash -u, refused the unsubstituted, empty, embedded-placeholder, ftp, two-value and missing set -- line cases with its not-probing messages and exit 2, and passed http and https URLs to the stub curl. In that form the inventory and the probe shared one block and the probe took no network value; they are now two blocks, each covered by the repository gate suite's bash -n and ShellCheck 0.11.0 passes over every block and by the October 2026 stub runs recorded with it. Finally, `ss` is an inventory only; inspect the relevant container and pod namespaces and published ports too.
If a metrics or session-server listener is enabled, run the guarded block against the exact configured URL from
its permitted client network: monitoring for metrics, GitLab for the session server. Configure trusted
certificate verification for HTTPS, including the runner-generated session-server certificate. Require the
expected positive-control response, then repeat from a disallowed
network; any HTTP response from the disallowed network proves reachability, while a timeout, DNS error, or
connection failure is inconclusive without a matching firewall deny record. This reachability comparison is
reasoned, since no deployed endpoint or external vantage was available. Substitute the URL, and permitted
or disallowed for the network you run it from, inside the single quotes and paste the whole block; do not
bypass TLS certificate verification.

REASONED: following block; the listener inventory follows the cited GitLab monitoring and session-server documentation; no deployed endpoint was available. Run it on the runner host: it refuses with status 2 when `ss` is missing, exits 3 when `sudo ss -tlnp` fails, and otherwise exits 0 with the whole table left for you to read. October 2026 stub runs with sudo and ss stubbed gave those three statuses.

```bash
(                                       # a subshell, so the exits below end only the subshell
  command -v ss > /dev/null || { echo "ss is not installed here; not listing sockets"; exit 2; }
  sudo ss -tlnp || { echo "sudo ss -tlnp exit $?: the listener inventory failed; inconclusive"; exit 3; }
  echo "block exit 0; the listener table is not classified, so judge it yourself"
)
```

REASONED: following block; the reachability comparison follows the cited GitLab monitoring and session-server documentation; no deployed endpoint or external vantage was available. From the permitted network it exits 0 for any HTTP response, whose code you compare with the expected one, and 3 for none. From a disallowed network it exits 1 for any HTTP response and 3 for none, never 0 there, because a failure is inconclusive without a matching firewall deny record. October 2026 stub runs with curl stubbed gave each of those four outcomes, and each `set --` refusal exited 2 before any curl call.

```bash
(                                       # a subshell, so the exits below end only the subshell
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_METRICS_URL' 'REPLACE_WITH_permitted_OR_disallowed'   # the exact configured URL, then permitted or disallowed for the network you run this from: replace inside the quotes, keeping them
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo 'paste the whole block; not probing'; exit 2; }
  shift
  [ "$#" -eq 2 ] || { echo 'exactly one URL and one network required; not probing'; exit 2; }
  case "$1" in
    *REPLACE_WITH_*|'') echo 'substitute the URL inside the quotes; not probing'; exit 2 ;;
  esac
  case "$1" in
    http://*|https://*) ;;
    *) echo 'HTTP or HTTPS URL required; not probing'; exit 2 ;;
  esac
  case "$2" in
    permitted|disallowed) ;;
    *) echo 'substitute permitted or disallowed inside the quotes; not probing'; exit 2 ;;
  esac
  set -- "$1" "$2" "$(if curl -q -g -sS --noproxy '*' --connect-timeout 5 --max-time 20 \
    -o /dev/null -w 'http=%{http_code} exit=%{exitcode} err=%{errormsg}\n' "$1"; then printf '\n0'; else printf '\n%s' "$?"; fi)"
  set -- "$1" "$2" "${3##*$'\n'}" "${3%$'\n'*}"   # curl's exit status, then its http= line
  printf '%s' "$4"
  case "$2:$3" in
    permitted:0) echo "the permitted network received an HTTP response; compare it with the expected positive-control response"; set -- 0 ;;
    permitted:*) echo "curl exit $3: the permitted network received no HTTP response, so the positive control failed; inconclusive"; set -- 3 ;;
    disallowed:0) echo "FINDING: the disallowed network received an HTTP response, so the listener is reachable from it"; set -- 1 ;;
    *) echo "curl exit $3: no HTTP response from the disallowed network, which is inconclusive without a matching firewall deny record, so this network never exits 0 here"; set -- 3 ;;
  esac
  echo "block exit $1; the HTTP code against the expected response and any firewall deny record are not classified, so judge them yourself"
  exit "$1"
)
```

## Sources (checked September 2026)

Version boundary: GitHub.com documentation checked 18 September 2026, with REST examples pinned to API version `2026-03-10`; GitLab documentation is rolling, checked that date. GitLab Runner source for the `pid_mode` key is pinned to tag v19.5.0, checked October 2026. The legacy GitLab registration token was disabled by default in GitLab 17.0 and is currently scheduled for removal in GitLab 20.0, and the Instance and Docker Autoscaler executors became generally available in Runner 17.1; run a currently supported patched release. No live product-version compatibility matrix was exercised.

- GitHub Actions security hardening and secure use: https://docs.github.com/en/actions/reference/security/secure-use
- GitHub self-hosted runner groups and access (private-only default): https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/manage-access
- GitHub self-hosted runners REST API (generate-jitconfig, listings) (GitHub REST API 2026-03-10): https://docs.github.com/en/rest/actions/self-hosted-runners
- GitHub GITHUB_TOKEN permissions: https://docs.github.com/en/actions/concepts/security/github_token
- GitHub events that trigger workflows (pull_request_target, workflow_run): https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- GitLab Runner security (privileged executor, tokens): https://docs.gitlab.com/runner/security/
- GitLab Runner Docker executor: https://docs.gitlab.com/runner/executors/docker/
- GitLab CI_JOB_TOKEN and the job-token allowlist: https://docs.gitlab.com/ci/jobs/ci_job_token/
- GitLab runner authentication tokens and the creation workflow: https://docs.gitlab.com/ci/runners/new_creation_workflow/
- GitLab Runner monitoring (metrics port 9252, no built-in authorization): https://docs.gitlab.com/runner/monitoring/
- GitLab Runner advanced configuration (session_server, Docker controls and autoscaler limits). The GitLab Runner advanced configuration sources: https://docs.gitlab.com/runner/configuration/advanced-configuration/. A partial automated page read dated 2026-10-12, not a recheck of this September 2026 list, corroborated the inspected Docker and autoscaler keys except `pid_mode`, which was reported only from rolling GitLab Runner `common/config.go` on `main`; the next item cites `pid_mode` from GitLab Runner source pinned at tag v19.5.0.
- GitLab Runner `common/config.go` DockerConfig `PidMode` field (toml `pid_mode`, "Run the container in a specific PID space"), tag v19.5.0 at 70f5c12dad80bfd8ab426843f38cae72fddc4e75 (checked October 2026). The GitLab Runner v19.5.0 `common/config.go` sources: https://gitlab.com/gitlab-org/gitlab-runner/-/blob/70f5c12dad80bfd8ab426843f38cae72fddc4e75/common/config.go#L330. The same field is at L310 at tag v19.1.0 (5eb085abb18b9c9614ba6e12951ece859d092272). It is absent at tags v18.11.4 (5b1ba4d9a0dec0a0a67ba4b88fa88e7f21b1060f), v19.0.0 (d4bac16c639ce0e7a778f1e88ca05b6d18dde57a), v19.0.1 (c2831b75a3ff0782dca8f64498cbc6f71c76819e), v19.0.2 (02fcb2d71c5d50f2f0ab92f9fd685706d3729b94) and v19.0.3 (e951e4926504fcfce3399542ff56029f77798c5a). No other tag before v19.1.0 was checked, so the tag that introduced the key is not established.
- GitHub self-hosted runner groups REST API (group visibility, allows_public_repositories, group repositories) (GitHub REST API 2026-03-10): https://docs.github.com/en/rest/actions/self-hosted-runner-groups
- GitHub Actions OIDC (id-token permission, issuer/audience/subject claims): https://docs.github.com/en/actions/reference/security/oidc
- GitHub workflow-jobs REST API (runner assignment: runner_id, runner_group_id) (GitHub REST API 2026-03-10): https://docs.github.com/en/rest/actions/workflow-jobs
- GitLab ID token authentication (id_tokens, aud): https://docs.gitlab.com/ci/secrets/id_token_authentication/
- GitLab Users API, create a runner (create_runner scope): https://docs.gitlab.com/api/users/#create-a-runner-linked-to-a-user
- GitLab Kubernetes executor (privileged, privilege escalation, service-account RBAC and token mounting): https://docs.gitlab.com/runner/executors/kubernetes/
- GitLab Instance and Docker Autoscaler executors (capacity_per_instance, max_use_count): https://docs.gitlab.com/runner/executors/docker_autoscaler/
- GitLab project job-token scopes API (inbound allowlist): https://docs.gitlab.com/api/project_job_token_scopes/
- Docker Engine security (rootful daemon, docker group as host administration): https://docs.docker.com/engine/security/
- AWS EC2 instance metadata service (IMDSv2 does not stop authorized in-job requests): https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- Python tomllib (offline config.toml inspection, Python 3.11+): https://docs.python.org/3.11/library/tomllib.html


<!-- version-basis:start -->
## About the AI assistant section below

This generated section holds the recorded versions, claim statuses and source mappings for AI assistants; use [the prompt at the top](#ai-assistant-prompt). This guide is guidance to verify against your own deployment, not a certification, an audit, or a guarantee of compliance with any standard.

**Version basis**

AI assistants must compare the versions listed below with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

Components (recorded basis):

- github: GitHub Actions documentation (unknown)
- github-api: GitHub REST API (2026-03-10)
- gitlab: GitLab rolling documentation (unknown)
- gitlab-runner: GitLab Runner source (v19.5.0)
- docker: Docker Engine documentation (unknown)
- python: Python tomllib minimum (3.11)
- aws: AWS EC2 documentation (unknown)

Claims (full source mapping in the JSON block below):

- job-transport (REASONED; github, gitlab): Both runners poll over HTTPS without an inbound job-polling port; verify GitLab TLS and restrict separate autoscaler management or webhook listeners.
- worker-account (REASONED; github, gitlab, docker): Use a dedicated least-privileged account, keep provisioning credentials off workers and confine rootful Docker access to disposable VMs.
- worker-egress (REASONED; github, gitlab, aws): Enforce job egress outside job control, isolate production and other workers, and deny unused metadata over both families; IMDSv2 does not stop arbitrary authorized job code.
- github-eligibility (REASONED; github): Keep self-hosted runners off public repositories; runner groups admit only private repositories by default and the public override should stay off.
- fork-token (REASONED; github): Ordinary fork pull_request jobs normally receive a read-only GITHUB_TOKEN and no other secrets, but can still read host credentials and reachable services.
- privileged-triggers (REASONED; github): pull_request_target and workflow_run can access secrets and write tokens; never execute untrusted PR code, artifacts or caches in these jobs.
- private-forks (REASONED; github): Review private-repository fork settings, which can grant write tokens and secrets; separate trusted privileged workers from untrusted CI.
- registration-token (REASONED; github-api): Registration tokens last one hour; generate on demand, never bake into images, and do not confuse expiry with runner deregistration.
- registration-manager (REASONED; github-api): Keep the App/PAT generating registration or JIT credentials off workers; organization endpoints need Self-hosted runners: write, repository endpoints Administration: write.
- jit (REASONED; github-api): Protect encoded_jit_config and the whole response; JIT runners execute at most one job.
- runner-credential (REASONED; github): Protect the installed runner authentication credential, directory and backups.
- github-job-token (REASONED; github): GITHUB_TOKEN is repository-scoped and per-job; set read-only defaults and grant only trusted jobs additional permissions.
- oidc (REASONED; github): Grant id-token: write only where needed; the cloud trust must restrict issuer, audience and repository/branch or protected-environment subject.
- github-lifecycle (REASONED; github, github-api): Prefer ephemeral/JIT workers and destroy their machines and storage; deregistration does not destroy disks, and labels route rather than authorize jobs.
- shell-executor (REASONED; gitlab): The GitLab shell executor runs as the runner user without isolation; avoid it for untrusted jobs on shared hosts.
- docker-executor (REASONED; gitlab, docker): Use unprivileged Docker; privileged=true or services_privileged and host Docker socket/TCP access can expose the host despite privileged=false.
- executor-host-access (REASONED; gitlab, gitlab-runner): Deny sensitive host mounts, host PID/network namespaces, unnecessary devices and capabilities; build without the host daemon.
- kubernetes-executor (REASONED; gitlab): Enforce nonprivileged containers, no privilege escalation, scoped ServiceAccounts and no unnecessary token mounting; prevent job overrides.
- gitlab-disposal (REASONED; gitlab): Containers share the kernel; use disposable separate VMs/nodes as needed and one-job autoscaling workers. Instance and Docker Autoscaler GA is recorded as Runner 17.1.
- gitlab-registration (REASONED; gitlab): Legacy registration tokens were disabled by default in GitLab 17.0, with removal scheduled for 20.0; use runner authentication tokens.
- gitlab-runner-token (REASONED; gitlab): Protect and rotate the runner authentication token in config.toml and backups; a cloned runner can steal assigned jobs.
- gitlab-creation (REASONED; gitlab): POST /user/runners needs create_runner scope; keep that access token off workers and set scope/protection at creation.
- gitlab-job-token (REASONED; gitlab): CI_JOB_TOKEN carries supported triggering-user access during the job and appears as CI_REGISTRY_PASSWORD and inside CI_REPOSITORY_URL.
- gitlab-allowlist (REASONED; gitlab): Target-project inbound job-token allowlists limit who may access that target, not job egress; also restrict resource feature visibility.
- gitlab-forks (REASONED; gitlab): Instance runners on public installations accept strangers; project scope does not establish code trust. Review parent-launched fork pipelines or disable ci_allow_fork_pipelines_to_run_in_parent_project.
- gitlab-protected (REASONED; gitlab): Developer access can compromise persistent runners; release runners need ref_protected and a pool separate from fork-merge-request testing.
- gitlab-metrics (REASONED; gitlab): Optional listen_address metrics and profiling have no built-in authorization; 9252 is allocated, not proof of the configured port.
- gitlab-session (REASONED; gitlab): Optional session_server uses TLS and must admit required GitLab traffic at its configured address; 8093 is an example, not an established default.
- verify-eligibility (REASONED; github-api): Fully paginate groups, selected repositories and public repositories' own runners; visibility=all alone is not public eligibility, and inherited access needs review.
- verify-permissions (REASONED; github): Inspect organization and repository workflow-token defaults and PR approval settings; explicit workflow permissions can raise grants and id-token is separate.
- verify-assignment (REASONED; github-api, github): A controlled fork workflow should run when exposed and lose assignment when restricted, while an allowed private job still runs; skipped/pending/offline/timeout is inconclusive.
- verify-config (DEMONSTRATED; python, gitlab, gitlab-runner): Python 3.14.4 synthetic fixtures reported exposed/fixed Docker, Kubernetes and autoscaler values; wrong types passed through, misplaced keys printed null, and empty/error cases differed in output and exit status. Those runs covered an earlier form; the current form's findings and exit statuses were also run on synthetic fixtures.
- verify-daemon (REASONED; gitlab, docker): Resolve docker.host through DOCKER_HOST or the default socket when absent; flag actual job access to a rootful daemon, not tcp:// alone.
- verify-autoscaler (REASONED; gitlab): For Instance/Docker Autoscaler require capacity_per_instance=1 and max_use_count=1 explicitly as integers; absent or other values are findings.
- verify-gitlab-api (REASONED; gitlab): Read inbound allowlists and require release-runner ref_protected against exposed controls; gitlab-runner verify proves authentication only.
- verify-lifecycle (REASONED; github-api, gitlab, github): Check complete deregistration listings and infrastructure disposal; persistent-worker canary must survive in the control, but absence alone does not prove destruction or clean shared caches.
- verify-listeners (REASONED; gitlab): Inventory namespaces and publications, require the permitted-client response, then test disallowed access; any HTTP response proves reachability, failure needs corroborating firewall denial.

````json
{
  "schema": 1,
  "checked": "2026-10-21",
  "documentation_checked": "2026-09",
  "body_sha256": "2cc98970efba9b419c804f38bf722b88e7fb41263ab7677c3c260e6734512247",
  "components": {
    "github": {
      "name": "GitHub Actions documentation",
      "basis": "unknown",
      "sources": {
        "s215dc07e3642": "https://docs.github.com/en/actions/reference/security/secure-use",
        "s92e8e4820392": "https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/manage-access",
        "sbbcb15f795a8": "https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows",
        "s4561d20e7042": "https://docs.github.com/en/actions/concepts/security/github_token",
        "s80fe11d8c90d": "https://docs.github.com/en/actions/reference/security/oidc"
      }
    },
    "github-api": {
      "name": "GitHub REST API",
      "basis": "2026-03-10",
      "sources": {
        "s8217448953a4": "https://docs.github.com/en/rest/actions/self-hosted-runners",
        "sd36db9ea1031": "https://docs.github.com/en/rest/actions/self-hosted-runner-groups",
        "sbeee4a47110c": "https://docs.github.com/en/rest/actions/workflow-jobs"
      }
    },
    "gitlab": {
      "name": "GitLab rolling documentation",
      "basis": "unknown",
      "sources": {
        "seb30e3937183": "https://docs.gitlab.com/runner/security/",
        "sde661ff4762e": "https://docs.gitlab.com/runner/executors/docker_autoscaler/",
        "s265254bc5592": "https://docs.gitlab.com/runner/executors/docker/",
        "s47b236d63dc4": "https://docs.gitlab.com/runner/configuration/advanced-configuration/",
        "s1579c499c75b": "https://docs.gitlab.com/runner/executors/kubernetes/",
        "sd2cbff5d5d6e": "https://docs.gitlab.com/ci/runners/new_creation_workflow/",
        "se430cbabc011": "https://docs.gitlab.com/api/users/#create-a-runner-linked-to-a-user",
        "saef0483b7be7": "https://docs.gitlab.com/ci/jobs/ci_job_token/",
        "s699c1c198119": "https://docs.gitlab.com/api/project_job_token_scopes/",
        "sbc009ff2866a": "https://docs.gitlab.com/runner/monitoring/"
      }
    },
    "gitlab-runner": {
      "name": "GitLab Runner source",
      "basis": "v19.5.0",
      "sources": {
        "s46d58158c809": "https://gitlab.com/gitlab-org/gitlab-runner/-/blob/70f5c12dad80bfd8ab426843f38cae72fddc4e75/common/config.go#L330"
      }
    },
    "docker": {
      "name": "Docker Engine documentation",
      "basis": "unknown",
      "sources": {
        "s18f59818e451": "https://docs.docker.com/engine/security/"
      }
    },
    "python": {
      "name": "Python tomllib minimum",
      "basis": "3.11",
      "sources": {
        "s37be9e98ea29": "https://docs.python.org/3.11/library/tomllib.html"
      }
    },
    "aws": {
      "name": "AWS EC2 documentation",
      "basis": "unknown",
      "sources": {
        "s82aca706445c": "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html"
      }
    }
  },
  "claims": {
    "job-transport": {"text": "Both runners poll over HTTPS without an inbound job-polling port; verify GitLab TLS and restrict separate autoscaler management or webhook listeners.", "components": ["github", "gitlab"], "sources": ["github:s215dc07e3642", "gitlab:seb30e3937183", "gitlab:sde661ff4762e"], "status": "REASONED"},
    "worker-account": {"text": "Use a dedicated least-privileged account, keep provisioning credentials off workers and confine rootful Docker access to disposable VMs.", "components": ["github", "gitlab", "docker"], "sources": ["github:s215dc07e3642", "gitlab:seb30e3937183", "docker:s18f59818e451"], "status": "REASONED"},
    "worker-egress": {"text": "Enforce job egress outside job control, isolate production and other workers, and deny unused metadata over both families; IMDSv2 does not stop arbitrary authorized job code.", "components": ["github", "gitlab", "aws"], "sources": ["github:s215dc07e3642", "gitlab:seb30e3937183", "aws:s82aca706445c"], "status": "REASONED"},
    "github-eligibility": {"text": "Keep self-hosted runners off public repositories; runner groups admit only private repositories by default and the public override should stay off.", "components": ["github"], "sources": ["github:s92e8e4820392", "github:s215dc07e3642"], "status": "REASONED"},
    "fork-token": {"text": "Ordinary fork pull_request jobs normally receive a read-only GITHUB_TOKEN and no other secrets, but can still read host credentials and reachable services.", "components": ["github"], "sources": ["github:s215dc07e3642", "github:sbbcb15f795a8"], "status": "REASONED"},
    "privileged-triggers": {"text": "pull_request_target and workflow_run can access secrets and write tokens; never execute untrusted PR code, artifacts or caches in these jobs.", "components": ["github"], "sources": ["github:sbbcb15f795a8", "github:s215dc07e3642"], "status": "REASONED"},
    "private-forks": {"text": "Review private-repository fork settings, which can grant write tokens and secrets; separate trusted privileged workers from untrusted CI.", "components": ["github"], "sources": ["github:s215dc07e3642"], "status": "REASONED"},
    "registration-token": {"text": "Registration tokens last one hour; generate on demand, never bake into images, and do not confuse expiry with runner deregistration.", "components": ["github-api"], "sources": ["github-api:s8217448953a4"], "status": "REASONED"},
    "registration-manager": {"text": "Keep the App/PAT generating registration or JIT credentials off workers; organization endpoints need Self-hosted runners: write, repository endpoints Administration: write.", "components": ["github-api"], "sources": ["github-api:s8217448953a4"], "status": "REASONED"},
    "jit": {"text": "Protect encoded_jit_config and the whole response; JIT runners execute at most one job.", "components": ["github-api"], "sources": ["github-api:s8217448953a4"], "status": "REASONED"},
    "runner-credential": {"text": "Protect the installed runner authentication credential, directory and backups.", "components": ["github"], "sources": ["github:s215dc07e3642"], "status": "REASONED"},
    "github-job-token": {"text": "GITHUB_TOKEN is repository-scoped and per-job; set read-only defaults and grant only trusted jobs additional permissions.", "components": ["github"], "sources": ["github:s4561d20e7042"], "status": "REASONED"},
    "oidc": {"text": "Grant id-token: write only where needed; the cloud trust must restrict issuer, audience and repository/branch or protected-environment subject.", "components": ["github"], "sources": ["github:s80fe11d8c90d"], "status": "REASONED"},
    "github-lifecycle": {"text": "Prefer ephemeral/JIT workers and destroy their machines and storage; deregistration does not destroy disks, and labels route rather than authorize jobs.", "components": ["github", "github-api"], "sources": ["github:s215dc07e3642", "github:s92e8e4820392", "github-api:s8217448953a4"], "status": "REASONED"},
    "shell-executor": {"text": "The GitLab shell executor runs as the runner user without isolation; avoid it for untrusted jobs on shared hosts.", "components": ["gitlab"], "sources": ["gitlab:seb30e3937183"], "status": "REASONED"},
    "docker-executor": {"text": "Use unprivileged Docker; privileged=true or services_privileged and host Docker socket/TCP access can expose the host despite privileged=false.", "components": ["gitlab", "docker"], "sources": ["gitlab:s265254bc5592", "gitlab:seb30e3937183", "docker:s18f59818e451"], "status": "REASONED"},
    "executor-host-access": {"text": "Deny sensitive host mounts, host PID/network namespaces, unnecessary devices and capabilities; build without the host daemon.", "components": ["gitlab", "gitlab-runner"], "sources": ["gitlab:s265254bc5592", "gitlab:s47b236d63dc4", "gitlab-runner:s46d58158c809"], "status": "REASONED"},
    "kubernetes-executor": {"text": "Enforce nonprivileged containers, no privilege escalation, scoped ServiceAccounts and no unnecessary token mounting; prevent job overrides.", "components": ["gitlab"], "sources": ["gitlab:s1579c499c75b"], "status": "REASONED"},
    "gitlab-disposal": {"text": "Containers share the kernel; use disposable separate VMs/nodes as needed and one-job autoscaling workers. Instance and Docker Autoscaler GA is recorded as Runner 17.1.", "components": ["gitlab"], "sources": ["gitlab:sde661ff4762e", "gitlab:seb30e3937183"], "status": "REASONED"},
    "gitlab-registration": {"text": "Legacy registration tokens were disabled by default in GitLab 17.0, with removal scheduled for 20.0; use runner authentication tokens.", "components": ["gitlab"], "sources": ["gitlab:sd2cbff5d5d6e"], "status": "REASONED"},
    "gitlab-runner-token": {"text": "Protect and rotate the runner authentication token in config.toml and backups; a cloned runner can steal assigned jobs.", "components": ["gitlab"], "sources": ["gitlab:seb30e3937183", "gitlab:sd2cbff5d5d6e"], "status": "REASONED"},
    "gitlab-creation": {"text": "POST /user/runners needs create_runner scope; keep that access token off workers and set scope/protection at creation.", "components": ["gitlab"], "sources": ["gitlab:se430cbabc011", "gitlab:sd2cbff5d5d6e"], "status": "REASONED"},
    "gitlab-job-token": {"text": "CI_JOB_TOKEN carries supported triggering-user access during the job and appears as CI_REGISTRY_PASSWORD and inside CI_REPOSITORY_URL.", "components": ["gitlab"], "sources": ["gitlab:saef0483b7be7"], "status": "REASONED"},
    "gitlab-allowlist": {"text": "Target-project inbound job-token allowlists limit who may access that target, not job egress; also restrict resource feature visibility.", "components": ["gitlab"], "sources": ["gitlab:saef0483b7be7", "gitlab:s699c1c198119"], "status": "REASONED"},
    "gitlab-forks": {"text": "Instance runners on public installations accept strangers; project scope does not establish code trust. Review parent-launched fork pipelines or disable ci_allow_fork_pipelines_to_run_in_parent_project.", "components": ["gitlab"], "sources": ["gitlab:seb30e3937183"], "status": "REASONED"},
    "gitlab-protected": {"text": "Developer access can compromise persistent runners; release runners need ref_protected and a pool separate from fork-merge-request testing.", "components": ["gitlab"], "sources": ["gitlab:seb30e3937183", "gitlab:sd2cbff5d5d6e"], "status": "REASONED"},
    "gitlab-metrics": {"text": "Optional listen_address metrics and profiling have no built-in authorization; 9252 is allocated, not proof of the configured port.", "components": ["gitlab"], "sources": ["gitlab:sbc009ff2866a"], "status": "REASONED"},
    "gitlab-session": {"text": "Optional session_server uses TLS and must admit required GitLab traffic at its configured address; 8093 is an example, not an established default.", "components": ["gitlab"], "sources": ["gitlab:s47b236d63dc4"], "status": "REASONED"},
    "verify-eligibility": {"text": "Fully paginate groups, selected repositories and public repositories' own runners; visibility=all alone is not public eligibility, and inherited access needs review.", "components": ["github-api"], "sources": ["github-api:sd36db9ea1031", "github-api:s8217448953a4"], "status": "REASONED", "verify": [1]},
    "verify-permissions": {"text": "Inspect organization and repository workflow-token defaults and PR approval settings; explicit workflow permissions can raise grants and id-token is separate.", "components": ["github"], "sources": ["github:s4561d20e7042", "github:s80fe11d8c90d"], "status": "REASONED", "verify": [2]},
    "verify-assignment": {"text": "A controlled fork workflow should run when exposed and lose assignment when restricted, while an allowed private job still runs; skipped/pending/offline/timeout is inconclusive.", "components": ["github-api", "github"], "sources": ["github-api:sbeee4a47110c", "github:s92e8e4820392"], "status": "REASONED", "verify": [3]},
    "verify-config": {"text": "Python 3.14.4 synthetic fixtures reported exposed/fixed Docker, Kubernetes and autoscaler values; wrong types passed through, misplaced keys printed null, and empty/error cases differed in output and exit status. Those runs covered an earlier form; the current form's findings and exit statuses were also run on synthetic fixtures.", "components": ["python", "gitlab", "gitlab-runner"], "sources": ["python:s37be9e98ea29", "gitlab:s47b236d63dc4", "gitlab:s1579c499c75b", "gitlab-runner:s46d58158c809"], "status": "DEMONSTRATED", "verify": [4], "evidence": "the extracted Python program ran without sudo on 20 synthetic config.toml cases using Python 3.14.4. Docker fixtures printed true/true, a socket mount and a TCP host versus false/false, empty volumes and a null host; both exited 0. Autoscaler limits printed null/null, 1/2 and 2/1 versus 1/1, all exit 0. Kubernetes fixtures printed true versus false for the three booleans and the supplied service_account. Wrong-type strings, booleans and floats retained their JSON types; misplaced privileged printed docker.privileged null. Empty and runner-less files printed nothing and exited 0. Missing files, malformed TOML and wrong section types exited 1; the second-runner structure error followed one printed runner. Two valid runners printed indices 0 and 1. The runner token key was omitted; a dummy token copied into service_account was printed. These observations cover file inspection only. Those runs covered the block's earlier form, whose program printed these lines, ended with a traceback on any read, parse or structure error, and left the block's status to Python. The current program prints the same lines, then a FINDING line for each docker privileged or services_privileged true, docker.sock volume, Kubernetes runner with privileged true or without allow_privilege_escalation false, and Instance or Docker Autoscaler limit other than integer 1. It prints an inconclusive line for a wrong type in a classified Docker or Kubernetes key, an error or an empty runner list; the block exits 1 for any finding, otherwise 3 for any inconclusive line or when sudo or python3 does not run the program, otherwise 0. In October 2026 the current program ran without sudo on 21 synthetic config.toml cases using Python 3.14.4. The Docker privileged and socket-mount cases, the Kubernetes privileged and unset-escalation cases, the autoscaler null, 1/2, true and 1.0 cases, and a privileged runner followed by a structure error printed FINDING lines and exited 10. The fixed Docker, Kubernetes and autoscaler 1/1 cases, two fixed runners and a misplaced privileged key exited 0. Wrong-type strings, empty and runner-less files, a missing file, malformed TOML and a wrong section type printed inconclusive lines and exited 13, and no case printed the runner token. With sudo and python3 stubbed, the whole block turned 10, 13 and 0 into 1, 3 and 0, and exited 3 when sudo or python3 failed. The current form is covered by the repository gate suite's bash -n and ShellCheck 0.11.0 passes over every block and by these October 2026 fixture and stub runs, which, like the earlier runs, demonstrate synthetic file inspection only."},
    "verify-daemon": {"text": "Resolve docker.host through DOCKER_HOST or the default socket when absent; flag actual job access to a rootful daemon, not tcp:// alone.", "components": ["gitlab", "docker"], "sources": ["gitlab:s265254bc5592", "docker:s18f59818e451"], "status": "REASONED"},
    "verify-autoscaler": {"text": "For Instance/Docker Autoscaler require capacity_per_instance=1 and max_use_count=1 explicitly as integers; absent or other values are findings.", "components": ["gitlab"], "sources": ["gitlab:sde661ff4762e"], "status": "REASONED"},
    "verify-gitlab-api": {"text": "Read inbound allowlists and require release-runner ref_protected against exposed controls; gitlab-runner verify proves authentication only.", "components": ["gitlab"], "sources": ["gitlab:s699c1c198119", "gitlab:seb30e3937183"], "status": "REASONED", "verify": [5]},
    "verify-lifecycle": {"text": "Check complete deregistration listings and infrastructure disposal; persistent-worker canary must survive in the control, but absence alone does not prove destruction or clean shared caches.", "components": ["github-api", "gitlab", "github"], "sources": ["github-api:s8217448953a4", "gitlab:sde661ff4762e", "github:s215dc07e3642"], "status": "REASONED"},
    "verify-listeners": {"text": "Inventory namespaces and publications, require the permitted-client response, then test disallowed access; any HTTP response proves reachability, failure needs corroborating firewall denial.", "components": ["gitlab"], "sources": ["gitlab:sbc009ff2866a", "gitlab:s47b236d63dc4"], "status": "REASONED", "verify": [6, 7]}
  }
}
````
<!-- version-basis:end -->
