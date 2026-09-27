# TODO

Forward-looking backlog for secureconfig. Closed items move to `DONE.md`; nothing is deleted.

This file is not a guide. It carries no configuration and is excluded from the guide-shape and
site-wiring gates for that reason; see `not_a_guide()` in `tools/run_all_checks.sh`.

## How items are numbered

Every open item is one index row in the band below that fits it. **Ids are permanent and never
reused**, including when an item is dropped, superseded, or its work reverted, and they are
decoupled from the band so an item can move band without changing identity.

Series: **1.x** an existing guide, whether the row is an error or a deepening, **2.x** missing
content, **3.x** tooling and process, **4.x** the site and adopter-facing surfaces. A row moves
band without changing its id, which is the point of decoupling the two.

Each row carries `(severity, effort)`. Severity is what a reader loses: **H** a wrong or missing
control on something commonly exposed, **M** a real gap with a workaround, **L** cosmetic or
internal. Effort is **XS** minutes, **S** under an hour, **M** a session, **L** several sessions,
**XL** a project.

Next ids: **1.181**, **2.48**, **3.36**, **4.12**.

Retired without ever naming an item, and never to be issued: **2.21** to **2.23** and **4.3** to **4.4**, assigned in error on 2026-09-13 when the band number was used in place of the series.

## Queueing

**AIQT: fix issues first.** Band 1 is worked to empty before anything else is picked, whatever
the severity of what is waiting in the other bands. After band 1 is clear, take the highest
severity across bands 2 and 3 together rather than finishing a band.

Maintainer direction supersedes the order at any time. Items blocked on another project are not
picked, they are waited on.

## Priority 1: Errors

A guide that asserts something false, or a Verify step that cannot discriminate. These are worked
first and to empty, because a reader acting on a wrong guide is worse off than a reader with no
guide. Found by the 2026-09-13 coverage audit; `[N families]` means raised independently by that
many.

| ID | Item | Tags |
| --- | --- | --- |
| 1.143 | `image-gen-uis.md`: confirm on a live AUTOMATIC1111 v1.10.1 instance what the guide states as read from the code, not run, on the maintainer's 2026-09-25 "Disclose + row" ruling: that `GET /internal/sysinfo` and `/internal/sysinfo-download` (`modules/ui.py:1223-1232`) answer without a login while the Gradio login is on, and return `COMMANDLINE_ARGS` unredacted (`modules/sysinfo.py:33`, `:130-131`) and a `--gradio-auth=user:pass` argv element unhidden (`get_argv()`, `:134-148`). Use dummy credentials and a loopback bind; record the unauthenticated request and response, and the proxy refusal of `/internal/sysinfo*` as the fixed state. Also confirm the unhidden `--api-auth=user:pass` argv form under the same conditions (`modules/sysinfo.py:142-148`, v1.10.1). Also confirm that `GET /sdapi/v1/cmd-flags` returns the `--gradio-auth` and `--api-auth` values (`modules/api/api.py:689-690`, `modules/api/models.py:221-231`), with no credential when `--api-auth` is unset and with any API user's credential when it is set. Then replace the "read from the code, not run" wording with the observation, or correct the disclosure. (H, S) | `[gap]` |
| 1.177 | F-MONGODB-AUDIT-SCOPE: `mongodb.md:579` says auditing logs only authorization failures. The MongoDB 8.0 parameter reference for `auditAuthorizationSuccess` scopes the failures-only default to `authCheck` events. Verify at a pinned version and correct the guide's scope. (M, S) | `[gap]` |
| 1.178 | F-BROWSERLESS-TOKEN: `headless-browser-services.md:86` records Browserless's token as optional by default. The vendor documentation disagrees with itself: the older quickstart (https://docs.browserless.io/enterprise/docker/quickstart) says an omitted token is generated, while the current configuration reference (https://docs.browserless.io/enterprise/docker/config) says endpoints remain unauthenticated. Pin a Browserless release and verify its default before deciding which guide wording to change. (M, S) | `[gap]` |

## Priority 2: Deepen existing guides

A real surface the guide never covers. Correct as far as it goes, and not far enough.

| ID | Item | Tags |
| --- | --- | --- |
| 1.179 | F-SOURCES-GAPS: add pinned sources for body facts the guide's Sources do not substantiate; surfaced by the row 3.32 version-basis drafting. Recheck each unfetchable pin before claiming support. `mosquitto.md`: WebSockets, session expiry, takeover, bridge ingress; `kafka.md`, `rabbitmq.md`, `clickhouse.md`: series and minimums (RabbitMQ 4.3), listener-default, default-user and users pins; `vector-databases.md`: hosted MFA; `search-engines.md`: Caddy (:182), default keys (:199); `elasticsearch.md`: OpenSearch GCS/Azure encryption (:445); `object-storage.md`: bucket HTTP denial (:304); `streamlit.md`: proxy and IdP versions (:90), `hd` (:71); `n8n.md`: owner setup, cookie and Execute Command defaults, env-access flag, `/rest/login`, refusal codes; `headless-browser-services.md`: `ALLOW_FILE_PROTOCOL`, Playwright paths; `headless-cms-instant-api.md`: Strapi signup; `supabase-self-hosted.md`: `.env.example` pin; `firebase-supabase.md`: tool and SDK versions; `pocketbase.md`: implementation traces, `documentSecurity`, `--dev` (:572); `workflow-orchestrators.md`: Airflow settings, Prefect block secrets, Temporal Codec Server; `kubernetes.md`: kubelet read-only bind; `observability-components.md`: Loki traces; `self-hosted-error-trackers.md`: secret generator, nginx scheme, membership; `realtime-webhooks.md`: proxy capabilities (:35); `realtime-voice-infra.md`: LiveKit handlers, coturn, OpenSSL; `ray.md`: Docker and KubeRay minimums, Serve gRPC; `nginx.md`: certbot, HTTP/2, tickets, HSTS, htpasswd, MFA; `apache.md`: certbot, distro commands, mod_headers, MFA; `caddy.md`: systemd, Cloudflare, tag-map and Caddyfile pins; `traefik.md`: per-control pages, htpasswd; `haproxy.md`: certbot hooks, `openssl passwd`, Cloudflare; `lighttpd.md`: Apache, Authelia, Cloudflare, wiki pins; `free-certificates.md`: Caddy, Traefik, Cloudflare origin, OpenSSL, Certbot page; `self-signed.md`: trust stores, requests, Git, RFC 9525; `headers.md`: proxy middleware; `docker.md`: examples, auth, secrets, workload, persistence, proxy; `container-hardening.md`: socket, admission, BusyBox `nc`, kubectl, diagnostics; `host.md`: includes, brokered SSH, Docker bypass, tooling; `cloud-firewalls.md`: brokered access, Docker bypass, GCP order, Azure admin rules; `egress-metadata.md`: egress defaults, owner rules, STS; curl in the headless, Supabase, Firebase, PocketBase, observability, certificate, headers and CORS guides. F-MOSQUITTO-SOURCES is included; `gitops-controllers.md` is covered by row 2.28; row 1.178 tracks the Browserless default. (M, L) | `[gap]` |
| 1.173 | `self-hosted-idp.md` (#382), authentik `version/2026.8.3`: The server metrics handler and the bootstrap blueprint are pinned in source; the worker and outpost metrics handlers remain documentation-backed, so trace them at the tag if further source auditing is wanted. (H, M) | `[gap]` |
| 2.28 | `gitops-controllers.md`: Complete the missing-source audit of controller binds, repo-server RPC authorization and certificate fallback, Dex runtime authentication and authorization, the Redis image bind and password initializer, and the RBAC fallback before claiming those fully traced. (M, M) | `[gap]` |
| 2.29 | `self-hosted-ci-runners.md` (#130, reworked #213): run the `tomllib` config inspection (privileged/services_privileged/`host` tcp:// daemon/autoscaler one-job limits) offline against exposed and fixed fixtures. (M, M) | `[gap]` |
| 1.117 | `search-engines.md` Verify (#285): supply a concrete, credential-safe grep of a real client bundle and repository history for the admin, master or bootstrap key, with a disposable build containing a known dummy credential as the positive control. The loopback runs had no client bundle. (M, M) | `[gap]` |
| 1.138 | `realtime-voice-infra.md`: the key-rotation test never shows how the rotated token is presented, and the obvious forms put a live bearer token in argv. Show it sent as a header on stdin (`--header @-`) to the existing `/rtc/validate` probe, once LiveKit v1.13.7 is confirmed to accept the token that way on that route and to answer old and new tokens distinguishably (from the #353 plan, maintainer ruling 2026-09-25). (L, S) | `[gap]` |
| 1.139 | `realtime-voice-infra.md`: `turnserver.conf` holds the TURN password in plaintext. Document the hashed-key alternative and whether `turnadmin`'s key derivation takes the password in argv at coturn 4.18.0 (from the #353 plan, maintainer ruling 2026-09-25). (L, S) | `[gap]` |
| 1.140 | `realtime-voice-infra.md`: evaluate a TURN allocation client that takes the password outside argv (stdin, a file or the environment), verified at a pinned tag, to replace `turnutils_uclient -w` in the allocation test, as CONTRIBUTING rule 7's third exception asks (from #354, maintainer ruling 2026-09-25). (L, S) | `[gap]` |
| 1.141 | Create-once key writers (`model-servers.md`'s llama.cpp, SGLang, vLLM and text-generation-webui blocks, and the LobeChat and Stable Diffusion WebUI writers in `chat-uis.md` and `image-gen-uis.md`): a default ACL on the target directory is inherited by new files and defeats `umask 077`, so a key file can be group-readable while the guide says `0600`. Refuse a directory carrying a default ACL (`getfacl`) and assert the file's mode after the write, verifying setfacl/getfacl behaviour first (from the #355 review, maintainer ruling 2026-09-25). (L, S) | `[gap]` |
| 1.144 | CONTRIBUTING rule 7's `read` exception and every block that uses it (among them `search-engines.md`, which CONTRIBUTING names as the model block): `read -r` takes only the first line of a paste, so a secret pasted with a newline leaves every later line for the reader's shell to run. Add one warning sentence to the rule (paste the secret alone) and apply it to every read-exception block (from the #356 review, maintainer ruling 2026-09-25). (L, M) | `[gap]` |
| 1.147 | `model-servers.md` Verify: the vLLM `/invocations` probe's subshell opens with `set -- 'REPLACE_WITH_A_REAL_SERVED_MODEL'`, with neither rule 6's `PASTE_WHOLE_BLOCK` marker nor its value count, so a paste that drops the `set --` line probes with the calling shell's own first argument when it has one. Give it the marker line (`set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_A_REAL_SERVED_MODEL'`), the marker check, `shift` and `[ "$#" -eq 1 ]`, as the key probe above it has (maintainer ruling 2026-09-26T00:27Z). (M, XS) | `[gap]` |
| 1.149 | `vector-databases.md`: check how the Milvus Helm chart and the Operator expose 9091 (a Service, and on which type), at a pinned chart and Operator version. Found in #361 review. (M, S) | `[gap]` |

## Priority 3: Add missing content

Gaps from the same audit, one row per missing guide. A gap raised by more than one family is
marked, and those are the ones worth taking first.

| ID | Item | Tags |
| --- | --- | --- |

## Priority 4: Tooling and process

| ID | Item | Tags |
| --- | --- | --- |
| 3.27 | Migrate the grandfathered Verify fences guide by guide: attach canonical DEMONSTRATED or REASONED declarations with audited scope and provenance, and remove matching entries from tools/verify_marking_baseline.txt. Never invent evidence or a missing prerequisite to clear the gate. (M, L) | `[gap]` |
| 3.30 | Extend the fenced-block Verify-marking gate planned in #389 to list items, table rows and prose units, with the same baseline-and-ratchet mechanism (maintainer ruling, 2026-09-26). (M, L) | `[gap]` |
| 3.32 | Roll version-basis metadata out to every remaining guide in one generated PR (maintainer ruling 2026-09-26): generate candidate claims from pinned Sources, explicit versions, controls, endpoint mappings, Verify markers and recorded observations; review by guide family with a coverage matrix (claim, body passage, source, version qualification, evidence); never infer DEMONSTRATED from an unmarked fence; enrol each guide in tools/version_basis_guides.txt. Depends on #395. (M, L) | `[gap]` |

## Decisions

Maintainer rulings moved to `DECISIONS.md` on 2026-09-13, in preparation for the OPF operational-files migration (row 3.8). A row may cite a decision there; this file no longer carries them.

## Priority 5: Site and adopters

| ID | Item | Tags |
| --- | --- | --- |

## Blocked upstream

| ID | Item | Waiting on |
| --- | --- | --- |
| 3.6 | Activate the AIQT hooks: `.claude/settings.json` is classifier-gated and `tools/gen_aiqt_settings.py` merges rather than overwrites (L, S) | the guardrails versioning work |
| 3.7 | Re-pin `.aiqt/` to a tag: currently pinned to a `main` commit because the only tag predates the commits this repository depends on (L, XS) | guardrails publishing a tag |
| 3.8 | Adopt the DevProcess / OPF operational-files standard. Deferred by the maintainer on 2026-09-12; `TODO.md` stays at the repository root and the adoption script will ingest it. See the note below (L, M) | the OPF tooling release |

### On 3.8, so it is not re-derived

Read from `.aiqt/core/opf/OPF-SPEC.md` and `OPF-QUICKSTART.md` rather than from a summary:

- There is **no TODO.md to DONE.md migration** under OPF. Both are deterministic generated views
  rendered from one store of versioned TOML records. An item is a `backlog_item` record; closing
  it is a state transition (`open` to `active` to `done`, or to `dropped` when declined) plus one
  worklog entry. Nothing hand-edits a generated view. The two files in this repository today are
  hand-kept and will be imported, not converted in place.
- Ids are permanent and never reused, which is the convention this file already follows.
- A declined item stays a record in the terminal `dropped` state with its reason, which is why
  `DONE.md` carries dropped rows rather than deleting them.
- Default store location is `.working/`, with `CHANGELOG.md` and `VERSION` staying at the product
  root and `VERSION` becoming generated. The maintainer has directed that this file stay at the
  root meanwhile; guardrails has captured that as an adoption-tooling requirement.
- The tooling ships in a later pack release. Adopting by hand today would mean maintaining a TOML
  store **and** rendering its views by hand with no `opf doctor` to catch drift between them,
  which is two hand-kept copies of one truth and the defect class this repository already runs
  three freshness gates against.
