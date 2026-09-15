# Changelog

secureconfig is published continuously and versions as `1.0.<pull request number>`, where the number is
that of the most recently merged pull request. The current value is in the `VERSION` file at the
repository root. There is no release artifact, so the version names a state of `main` rather than a
downloadable build, and each guide remains dated by its own "Sources (checked <month year>)" section.
Entries here are grouped by the date the change landed on `main`. Note that nothing in the gate suite
can check `VERSION` against GitHub: the suite is deliberately offline so that no outside service can
turn the build red, and a pull request number is only knowable from outside. Keeping `VERSION` in step
with the merged pull request is therefore an authoring obligation, not an enforced one.

## 2026-09-15
- Clarified the tailnet access boundary in tailscale.md (#117, row 1.39): the guide said `serve` traffic is "reachable only by devices in your tailnet, authenticated by device identity and your tailnet ACLs", without noting that a new tailnet is allow-all by default (`src` `*`, `dst` `*:*`; an empty `acls` means allow-all, not deny-all), so every device and user in the tailnet reaches the service until the policy is narrowed with a grant or ACL from a specific source to this host and port. It adds that tailnet access is network reachability, not user authorization: a panel behind `serve` still needs its own login. Verified at Tailscale's access-control docs (added to Sources).
- Added the DOCKER-USER chain and a Docker 28.0 caveat to docker.md (#116, row 1.6): the guide offered only loopback publishing for a host-reachable port. It now notes that the host-IP restriction in a publish string (including `127.0.0.1`) is reliable only on Docker Engine 28.0 and later, since before 28.0 a neighbour host could reach a loopback-mapped port, a remote host could reach a port bound to a specific host IP, and an unpublished container port was reachable by direct routing (all three fixed in 28.0). For a port that must be published on a routable interface, it adds the `DOCKER-USER` iptables chain (evaluated before Docker's own accept rules) with a source-IP filter, and the caveat that after DNAT those rules match a container's internal address, not the published port. The DOCKER-USER documentation has moved off the packet-filtering page the guide cited; the correct Docker "with iptables" page and the 28.0 release notes were added to Sources.
- Added an Adminer section to admin-uis.md (#115, row 1.32): Adminer is database management in a single PHP file at a predictable path (`adminer.php`) that scanners probe constantly, and it keeps no accounts of its own; its login form takes the database server's own address, username, and password, so an internet-reachable Adminer is a public login form onto the database and a perennial exploit target. The section applies the guide's never-public rule (private, proxy-level TLS and authentication, source-IP restriction) and says to delete the file from the docroot when it is not in use. Verified at adminer.org.
- Named credential-bearing config files as secrets in secrets.md (#114, row 1.33): a new rule 9 says a Terraform state file (`terraform.tfstate`, plaintext, holding any secret in the configuration), a kubeconfig (a base64 client private key in `client-key-data`), and `~/.docker/config.json` (registry logins base64-encoded without a credential helper) belong in `.gitignore` beside `.env` and `*.pem`, and that the rule-4 scanners flag one that slips in. Verified at the Terraform, Kubernetes, and Docker docs (added to Sources).
- Stopped the ollama.md and memcached.md Verify steps filtering ss output by port (#113, rows 1.28 and 1.29): both piped `ss` through `grep <port>`, which the repo's own rule (apache.md, traefik.md) forbids because a port filter hides an unexpected listener and can match the port's digits inside an address such as an IPv6 literal. They now run the unfiltered `ss -tlnp` (ollama) and `ss -tlnup` (memcached, which also confirms no UDP line), so the reader reads the whole listener table and confirms the service is on the intended address with nothing unexpected beside it.
- Generalized the CSP-hash gate to cover site/404.html (#112, row 3.12): `tools/check_csp_hashes.py` hard-coded site/index.html and modeled one `<style>` and one `<script>`, so 404.html (added in #102, its style hash pinned in the shared `/*` CSP) was never verified; editing it left the gate green while a browser refused the style. The gate now checks a declared per-page list, refuses any unlisted `site/**/*.html`, and requires exactly one CSP under `/*` with no other rule setting or detaching one. The mutation harness grew from 43 to 68 cases, including an edited-but-unrepinned 404 style that must fail. Orphan-pin exactness is deferred to row 3.15. Tier Sensitive: tri-family seeds combined by Fable, premises re-verified at source, adversarial self-checks confirmed the fail-open is closed and the harness catches a single-page regression.
- Added a homepage copy-paste prompt for confidential business rules (#111, row 4.11): secrets.md rule 8 treats a confidential pricing formula, allocation rule, or customer-specific process as a secret that belongs out of public repositories, client bundles, and public LLM prompts, but no homepage task surfaced them. A new "Audit for exposed business rules" prompt card directs an assistant to secrets.md and web-exposure.md, has it search the public repository and git history, anything shipped to the browser (a NEXT_PUBLIC_ or VITE_ value, client-shipped code, or a source map), and any prompt sent to a public LLM, and apply the per-guide fix only after approval. It matches the five existing prompt cards and adds no inline script or style, so the CSP hashes are unchanged. Completes a second external review (item 6).
- Named the OWASP Top 10 for LLM Applications in the scope statements (#110, row 4.10): README.md and CONTRIBUTING.md already said general application security (injection, deserialization, business logic) is out of scope and pointed to OWASP resources; each now also points to the OWASP Top 10 for LLM Applications (https://genai.owasp.org/llm-top-10/) for LLM-specific application risks such as prompt injection, so a reader of these AI-deployment guides knows where the application-layer LLM risks are catalogued. One link per file, no new guide; the repo's own scope stays deployment exposure. Found in a second external review (item 5).
- Added cross-user isolation Verify steps to vector-databases.md and chat-uis.md (#109, row 1.70): the guides configured tenant row-level security and per-workspace access but had no step proving one user's RAG or chat query does not return another user's data. vector-databases.md now has a cross-tenant check (as tenant B, query, confirm only B's rows; an RLS-bypassing role returns both, so the difference is the policy working, not an empty table); chat-uis.md now says to ask, as user B, a question whose answer lives only in user A's documents and confirm nothing of A's returns. Found in a second external review.
- Added two secret-handling principles to secrets.md (#108, row 1.69): keys and customer data stay out of AI-model prompts, including the system prompt and any internal role map (a system prompt is not a secret store, and prompt injection can make a model repeat it); and unpublished business rules (pricing, allocation, a customer-specific process) are treated like secrets, kept out of public repositories, client bundles, and public LLMs. Found in a second external review.
- Added browser-side cache guidance to headers.md (#107, row 1.68): the guide covered a shared cache serving user A's authenticated response to user B, but not the browser's own cache. It now explains that `private` still lets the browser store a page (so the Back button can redisplay an authenticated view after logout), that `no-store` is needed on authenticated or session-cookie responses, and that logout should send `Clear-Site-Data` to clear the browser and back/forward cache; the Verify adds a back-button-after-logout check. Verified at MDN. Found in a second external review.
- Brought the legacy probe guards to the rule-6 template (#106, row 1.44): eleven guides carried the pre-hardening guard, an unquoted placeholder on the `set --` line, no `PASTE_WHOLE_BLOCK` sentinel or arity check, and no `-g` on the curl probe. Each guard now uses the full CONTRIBUTING rule-6 shape: a single-quoted placeholder with the substitute-inside-the-quotes note, the sentinel-and-shift check, an `[ "$#" -eq 1 ]` arity check, `case "$1"`, and `-g` on every probe curl. shellcheck and the guard-conventions gate (#105) verify them. From the guard-conventions review.
- Gated the curl guard conventions in tools/check_guard_conventions.py (#105, row 3.11): a stdlib shell-lexer gate (not line-regex) that flags a fenced-block curl whose first argument is not `-q`/`--disable` (curl only skips `~/.curlrc` when `-q` leads) and an unglobbed `[...]` or `{...}` in a scheme-bearing URL without `-g`. Registered in run_all_checks.sh with `--no-c2` (the probe-outside-guard rule mis-flags the corpus's legitimate exit-guard-then-probe-after-esac idiom, deferred to row 3.14) and `--min-curls 176` as a scope-regression tripwire; a 60-case self-test guards the gate itself. Enablement on main is clean (181 curls, 0 findings). From the guard-conventions review.
- Added a leading `-q` to a devops-uis.md TLS probe (#104, row 1.67): one curl in the Docker-over-TLS Verify block (the missing-client-certificate handshake check) did not lead with `-q`, so a reader's `~/.curlrc` could silently alter it, while the next curl in the same block already did. Prepended `-q`. This is the surviving genuine defect from the guard-conventions-gate review; the two files it originally named were fixed in later pull requests.
- Synced the plugin manifest version to VERSION (#103, row 3.13): `plugin/plugin.json` had been frozen at `1.0.38` since the plugin was first packaged (#39) while the repository moved to `1.0.102`, so an adopter's updater keyed on the plugin version saw no reason to re-fetch corrected guides. `scripts/build-plugin.sh` now rewrites the manifest version from VERSION on every build, and the existing whole-corpus staleness gate (which rebuilds the bundle and diffs) enforces it, so no separate version gate is needed. Found in an external pre-launch review.
- Added a site 404 page in site/404.html (#102, row 4.9): unknown URLs were served the homepage with a 200; Cloudflare Pages serves 404.html for an unmatched path when the file exists. The page matches the site (brand, accent, theme-aware) and is self-contained with one inline stylesheet, whose sha256 is pinned in site/_headers so the site CSP allows it. The CSP gate still covers only index.html; extending it to 404.html is tracked as row 3.12. Found in an external pre-launch review.
- Added a security policy in SECURITY.md (#101, row 4.8): the repository had none. It routes reports to GitHub private vulnerability reporting (with a fallback if that is not enabled), scopes reports to secureconfig's own guidance and code rather than to vulnerabilities in the products the guides document, and notes that fixes land on main so an installed plugin bundle or a copied guide must be refreshed to get them. SECURITY.md is added to the gate suite's not_a_guide exclusions so a meta file is not held to guide shape. Found in an external pre-launch review.

## 2026-09-14
- Guarded the external-reachability probes in ray.md and mlflow.md (#100, row 1.66): each probe used an unguarded `http://REPLACE_WITH_THE_SERVER_PUBLIC_IP:PORT/` with a pass of `http=000` and `time_connect=0.000000`, but an unsubstituted placeholder fails DNS to exactly that result, a false pass indistinguishable from a filtered port (CONTRIBUTING rule 6). Both probes now use the corpus's guarded subshell idiom (a `case` on `*REPLACE_WITH_*` refuses to run unsubstituted, `--noproxy '*'` so a proxy cannot answer, and the `exitcode`/`errormsg` write-out naming why the connection failed), the same pattern already in chat-uis.md and others; the curl Sources bullets now cite the exitcode/errormsg variables (curl 7.75.0). Verified with shellcheck. Found in an external pre-launch review.
- Corrected vLLM's default bind in model-servers.md (#99, row 1.65): the intro listed only TGI and Triton as `0.0.0.0` binders, implying vLLM defaults local, but `vllm serve` leaves `--host` unset, which binds every interface (the startup log shows `http://0.0.0.0:8000`). The guide now lists vLLM among the all-interfaces binders and tells readers to pass `--host 127.0.0.1`, with the launcher source. Verified at the vLLM launcher source. Found in an external pre-launch review.
- Noted the Ollama Docker image's all-interfaces default in ollama.md (#98, row 1.64): the guide said Ollama binds `127.0.0.1` by default, true for the standalone binary, but the official `ollama/ollama` Docker image sets `ENV OLLAMA_HOST=0.0.0.0:11434`, so a containerized Ollama listens on every interface and a bare `-p 11434:11434` republishes it to every host interface. The guide now adds that in Docker the control is the published address (`-p 127.0.0.1:11434:11434`), not `OLLAMA_HOST`, because the container must listen broadly for a proxy to reach it. Verified at the ollama/ollama Dockerfile. Found in an external pre-launch review.
- Warned about the OpenSearch demo internal_users.yml accounts in elasticsearch.md (#97, row 1.63): the demo security configuration seeds seven built-in accounts (`admin`, `anomalyadmin`, `kibanaserver`, `kibanaro`, `logstash`, `readall`, `snapshotrestore`), and `OPENSEARCH_INITIAL_ADMIN_PASSWORD` sets only the `admin` password, so the other six keep the credentials shipped in the demo file. The guide now says to replace `internal_users.yml` or remove the demo accounts before any real deployment and to confirm each demo login is refused. Verified at the opensearch-project/security internal_users.yml. Found in an external pre-launch review.
- Warned against the Airflow docker-compose defaults in workflow-orchestrators.md (#96, row 1.62): the official `docker-compose.yaml` selects the FAB auth manager but seeds it with a known admin (`_AIRFLOW_WWW_USER_USERNAME` and `_AIRFLOW_WWW_USER_PASSWORD` both `airflow`) and signs API tokens with a fallback `AIRFLOW__API_AUTH__JWT_SECRET` of `airflow_jwt_secret` (used when the variable is unset), and it publishes port 8080 on all interfaces; its own header calls it local-development only. A reader who runs it unchanged gets an `airflow`/`airflow` login exposed wherever 8080 is reachable and can forge API tokens to impersonate existing users. The guide now names all three, says to set your own values before the container is reachable, and to publish 8080 only behind the fronting layer. Verified at the apache/airflow docker-compose.yaml. Found in an external pre-launch review.
- Warned against the Langfuse self-hosting compose defaults in llm-observability.md (#95, row 1.61): the official `docker-compose.yml` ships example secrets marked `# CHANGEME`, and `NEXTAUTH_SECRET` protects the session token, so the shipped `mysecret` lets anyone mint a session for any existing account (admins included), skipping the sign-in flow and its SSO and MFA; `SALT` and an all-zero `ENCRYPTION_KEY` (which encrypts stored provider keys and integration secrets) ship the same way, and the compose bundles a MinIO with `minio`/`miniosecret` published on host port 9090 plus langfuse-web on 3000. The guide now names these, tells the reader to generate a fresh random value for each before first start, and to keep the bundled stores off untrusted networks. Verified at the langfuse/langfuse docker-compose.yml. Found in an external pre-launch review.
- Enabled mongo-express basic auth across 1.x in admin-uis.md (#94, row 1.60): the guide set ME_CONFIG_BASICAUTH_USERNAME and ME_CONFIG_BASICAUTH_PASSWORD, but 1.x has basic auth off by default and credentials alone do not enable it, so a reader ran the panel with no login. Which variable enables it also changed within 1.x: 1.0.x reads ME_CONFIG_BASICAUTH, 1.1.0 and later read ME_CONFIG_BASICAUTH_ENABLED, so the block now sets both, and the intro notes that admin:pass is the credential fallback if you skip the username and password. Verified at the mongo-express v1.0.2 and v1.1.0 config source. Found in an external pre-launch review.
- Flagged the KRaft controller port overlap in kafka.md (#93, row 1.59): the guide puts the SASL_SSL broker listener on 9093, which is the port Kafka's default `server.properties` assigns to the KRaft controller listener, so on a combined broker-and-controller node the two try to bind 9093 and the broker fails to start. Section 1 now warns to give the controller a different port. Verified against Kafka's default config. Found in an external pre-launch review.
- Bound the LiteLLM proxy to loopback explicitly in litellm.md (#92, row 1.58): the guide said to run the proxy on loopback but the proxy's `--host` defaults to `0.0.0.0`, so a reader who ran it without the flag bound every interface. The guide now shows `litellm --host 127.0.0.1 --port 4000 --config config.yaml` and adds the LiteLLM CLI source. Verified at docs.litellm.ai. Found in an external pre-launch review.
- Broadened the leaked-key search in firebase-supabase.md (#91, row 1.57): the Verify step searched the client bundle for the word `service_role`, but a leaked key is a value, not that word, so the search missed it. A Supabase secret is a legacy JWT starting `eyJ` or a new `sb_secret_` string; the step now greps for `service_role|eyJ|sb_secret_` and notes a hit must be rotated. Verified at supabase.com API keys docs. Found in an external pre-launch review.
- Hardened the sshd config ordering guidance in host.md (#90, row 1.56): sshd uses the first value it reads for each option and includes `/etc/ssh/sshd_config.d/*.conf` at the top of the main file, so a cloud image's `50-cloud-init.conf` (`PasswordAuthentication yes`) silently overrides a setting placed later, leaving password login on. The guide now puts the hardening in a first-sorting `00-hardening.conf` drop-in, explains the override, and verifies the EFFECTIVE config with `sudo sshd -T` rather than only the `sshd -t` syntax check. Found in an external pre-launch review.
- Validated manifest file names in the plugin updater (#89, row 4.7): scripts/update-guides.sh looped over the fetched MANIFEST.sha256 and wrote each entry to `$work/$name` with no name check, so a manifest entry such as `../x.md` escaped the temporary directory and the subsequent digest check still passed. The loop now rejects any name outside `[A-Za-z0-9._-]`, containing `..`, or beginning with a dot, refusing the whole update so a malicious manifest cannot write outside its temp directory. Found in an external pre-launch review.
- Warned that Open WebUI's first account is the administrator in open-webui.md (#88, row 1.55): the guide covered ENABLE_SIGNUP and DEFAULT_USER_ROLE=pending, which governs only later accounts, but not that the first account created is made admin regardless. On an exposed instance with signup on, whoever registers first owns it, so claim the admin account on loopback first (or preset WEBUI_ADMIN_EMAIL/WEBUI_ADMIN_PASSWORD). Verified at the Open WebUI FAQ. Found in an external pre-launch review.
- Completed the nginx Authelia identity headers in fronting-auth.md (#87, row 1.54): the protected-location snippet called `auth_request` but omitted the `auth_request_set`/`proxy_set_header Remote-User` (and Groups/Name/Email) pairs from Authelia's `authelia-authrequest.conf`. Since nginx forwards client request headers to the upstream by default, without them a client that reached the app could send its own `Remote-User: admin`; the pairs set the identity from Authelia's response and overwrite the client's. Verified against Authelia's nginx integration guide. Found in an external pre-launch review.
- Marked the self-signed leaf certificate CA:FALSE in self-signed.md (#86, row 1.53): the `openssl req -x509` commands set no `basicConstraints`, so on configurations where OpenSSL marks the leaf `CA:TRUE` the certificate, once installed into a client trust store in section 4, becomes a trusted signer for any name using the unencrypted key `-nodes` leaves on disk. Both commands now pass `-addext "basicConstraints=critical,CA:FALSE"`, with a bullet explaining why. Found in an external pre-launch review.
- Fixed a literal placeholder password in rabbitmq.md (#85, row 1.52): the account block created the `ops` administrator with the literal password `...`, which a reader copying the block would deploy. It now uses a `REPLACE_WITH_A_DIFFERENT_LONG_RANDOM_PASSWORD` placeholder like the `app` user above it. Found in an external pre-launch review.
- Added Webhook-node authentication to n8n.md (#84, row 1.24): a private Webhook node left on the default None answers anyone who reaches its URL, and this is separate from the instance login and the `X-N8N-API-KEY` public API, so the existing api/v1 check does not establish it. The guide now sets the node Authentication to Basic, Header, or JWT auth, notes it is per-node, points to signature validation for third-party callers, and adds a Verify probe that a known production webhook (`/webhook/<path>`) rejects an unauthenticated request.
- Bound Express `trust proxy` to the proxy topology in nodejs.md (#83, row 1.23): the guide set it to a bare hop count of 1; a blanket `true` or an over-large hop count lets a client forge X-Forwarded-For/Host/Proto (faking the client IP, hostname, or HTTPS status) unless the last trusted proxy overwrites them. It now trusts `loopback` for a same-host proxy, with the exact IP or subnet shown for a remote one, explains the affected req.* properties and the shorter-path risk, and adds a Verify probe that a forged X-Forwarded-For is not reflected in req.ip.
- Added a generic controls reference and a guide-request path (#82): controls-reference.md distils the control patterns that recur across the corpus (network binding, hidden listeners, default credentials, registration, MFA, TLS, file access, secrets, API surfaces, container posture, and the Verify discipline) into an alignment checklist for applications with no guide of their own, and a new requests/ directory with a README and template lets anyone, including an AI assistant, request a guide by pull request. README point 3 points assistants at both. The reference is excluded from the guide-shape gate as a cross-service document rather than a service guide.
- Added a GitLab CE section to devops-uis.md (#81, row 1.13): the root password auto-generates into /etc/gitlab/initial_root_password and is deleted on the first container restart after 24 hours, so sign in and rotate it; signup_enabled defaults true (clear "Allow new user accounts" for a private forge); default_project_visibility and default_group_visibility both default private, and "internal" means any signed-in non-external user; admin-enforced 2FA. Adds a Verify check for the initial_root_password file and three docs.gitlab.com sources.
- Removed the dated section headings from DECISIONS.md and added an intro paragraph (#80): the rulings now read as one standing set rather than a dated log, and the intro records the DECISIONS.md convention across the maintainer's projects, so an assistant can predict how he decides and a settled question is not asked twice.
- Simplified the GRC Library entry in the site's related-resources note (#79): a single "GRC Library" link to grclibrary.ai, in the same style as the AIQT link, replacing the repository link and the separate URL. The repository is still reachable from the GRC gap-assessment prompt.
- Corrected the frp OIDC directionality note in tunnels.md (#78, row 1.51): auth.method = "oidc" has frpc obtain a token from an OIDC provider through the Client Credentials Grant and frps validate it by issuer and audience, authenticating frpc to frps rather than "both sides" as the line previously read. Found by codex during the #77 QA.
- Covered ssh -R remote forwarding in tunnels.md (#77, row 1.30): the server's sshd_config GatewayPorts governs the forwarded port's bind (default no keeps it on loopback and overrides a client's public-bind request; yes forces a wildcard bind; clientspecified honours the client's requested address), and SSH authenticates the tunnel session but not callers to the forwarded port, so a widened GatewayPorts in front of an app with no login of its own publishes it unauthenticated.
- Covered Caddy's admin API in caddy.md (#76, row 1.27): it listens on localhost:2019 with no auth and can replace the whole config or stop the server, so it must never be published; the guide adds the permissioned-unix-socket pattern for shared hosts and a Verify check for the 2019 listener.
- Warned against quick-sharing files with python -m http.server in python.md (#75, row 1.31): it binds every interface by default and serves the current directory (source, .env, keys, dumps), follows symlinks, and is not for production; the guide shows the loopback-bound alternative.
- Added MySQL's X Plugin listener to mysql.md (#74, row 1.21): MySQL 8.4 enables the X Plugin by default on port 33060 with mysqlx_bind_address defaulting to every interface, independent of the classic bind_address; the guide now sets mysqlx_bind_address (or mysqlx = OFF) and checks 33060.
- Covered Sidekiq Web UI authentication in ruby.md (#73, row 1.20): the usual mount exposes job arguments and queue controls to anyone who reaches /sidekiq; added the Devise authenticate constraint and the Rack::Auth::Basic pattern, plus a Verify probe of the path.
- Covered directory listing in web-exposure.md (#72, row 1.19): Debian and Ubuntu ship apache2.conf with Options Indexes on /var/www, so a directory without an index.html is served as a browsable listing that defeats the name-based deny rules; added an Options -Indexes block, a Verify probe against a directory URL, and the mod_autoindex and nginx autoindex sources.
- Added RabbitMQ's epmd (default 4369) and Erlang distribution (default 25672) ports to rabbitmq.md (#71, row 1.17): the shared Erlang cookie is the only default credential on the distribution port and grants full control of the node, so a weak or leaked cookie on a published port is a remote compromise; the ss check and exposure-index.md now cover both ports.
- Named MinIO's web console listener and checked its port (#70, row 1.16): the embedded console is a second listener (--console-address / MINIO_CONSOLE_ADDRESS) that binds all interfaces when host-less, even with the S3 API on loopback; the guide now advises --console-address 127.0.0.1:9001, checks 9000 and 9001, probes the console, and adds a 9001 exposure-index row.
- Added a text-generation-webui section to model-servers.md (#69, row 1.8): its two independently keyed surfaces (Gradio UI and the OpenAI-compatible API), the --listen-widens-both trap, the --share/--public-api tunnels, per-surface auth, the validate_host_header 400, and a reasoned /v1/models probe (demonstration tracked by row 1.50). Flags verified at source.
- Added the curl 7.75.0 version note to the Verify probes in llm-observability.md and vector-databases.md (#68, rows 1.48/1.49); both print the exitcode and errormsg write-out variables that curl added in 7.75.0.
- Prepended `-q` to two Verify probes (#66) in `fronting-auth.md` and `image-gen-uis.md` so the reader's `~/.curlrc` cannot silently alter them; surfaced by the row 3.11 guard-conventions gate work.
- Rotated row 1.12 into `DONE.md` (#65) after #64 merged, and opened three follow-up rows: 1.47 (live exposed/fixed reproduction of the Traefik canary probes) and 1.48/1.49 (the curl 7.75.0 note that `llm-observability.md` and `vector-databases.md` still lack for their `exitcode`/`errormsg` write-out variables, found while applying #64).
- Disabled Traefik's Docker-provider default exposure (`traefik.md`, #64): added the `providers.docker` block with `exposedByDefault: false`, the read-only socket mount with its root-equivalence note, the opt-in/opt-out and daemon-wide-discovery prose, an unlabelled-canary front-door probe with an app baseline, a widened whole-table `ss` check, and the Swarm-scope note. Closes backlog row 1.12.

### Added

- The Phoenix administrator bootstrap in `llm-observability.md` (#62). Enabling Phoenix authentication as the guide previously advised left the default `admin@localhost` / `admin` login live; the guide now sets `PHOENIX_DEFAULT_ADMIN_INITIAL_PASSWORD` (read only on the startup that first creates the account, and silently inert afterward), changes the password at the UI before the instance is reachable and proves the default is dead, adds an unauthenticated read (`/v1/projects`) Verify probe in the hardened guard idiom and a manual default-credential check, governs the OTLP write path through the listener inventory rather than a curl probe, and records that Phoenix has no native MFA but federates to an OAuth2/OIDC provider. Closes backlog row 1.11.
- Qdrant's internal cluster port 6335 in `vector-databases.md` (#63). An API key does not protect 6335 (the vendor states internal channels are never protected by a key), and the guide had listed 6335 in its port table but omitted it from the Verify grep. The guide now annotates 6335 as distributed-mode-only, states that a key and `read_only_api_key` do not cover it, restricts it at the network layer with `cluster.p2p.enable_tls`, replaces the forbidden `ss` grep with a whole-table inventory, and probes 6333/6334/6335 from outside the peer allowlist with exit/err discrimination. The probes are marked reasoned (no distributed cluster in the authoring environment), tracked by row 1.46. Closes row 1.9.

## 2026-09-13

### Added

- A required gate on the changelog's own pull-request coverage (#53). It compares every `(#N)`
  squash-merge suffix in the local history against the `#N` references here, so it reads the
  repository and nothing else and keeps the suite offline. It found two unreferenced pull requests
  on its first run against this branch. It exempts exactly one, the highest-numbered merged pull
  request, because a pull request cannot reference its own number before it is opened; let a second
  merge without its entry and the gate goes red. It fails on a shallow clone rather than skipping,
  because with one commit it would find nothing missing and report a pass.
- The pack's `cntdef` rule, "Continue by default", vendored verbatim at
  `.aiqt/core/rules/trust-continue-by-default.md`, with `CLAUDE.md` and `AGENTS.md` pointing at it
  (#55). An earlier attempt paraphrased the rule into those two files instead and the permission
  classifier refused it three times, including a read-only check: prose that narrows when an agent
  pauses for its maintainer, authored by that agent into the file that configures it, is the shape
  it screens for whatever its provenance. Vendoring the upstream file is both permitted and the
  correct architecture. The file is byte-identical at this repository's pinned commit and at
  upstream main, so it needs no pin bump.
- `ai-infra-services.md`, the 86th guide (#60). One guide covering SearxNG, LocalAI, Text Embeddings
  Inference, LangServe, Mem0 and Onyx, closing six backlog rows. Three of those rows had premises
  that were wrong at source: LangServe is deprecated, and Mem0 and Onyx both ship authentication on.
  What the six share is not a missing password but that the run form decides what the network sees,
  and it publishes more than the authentication covers. Two shapes are named: authentication absent
  or unset, and a guarded front door with the backing store published beside it. Text Embeddings
  Inference was reclassified during review: it does have a native control, `--api-key` with the
  environment variable `API_KEY`, off by default, and a Prometheus listener on port 9000 that the
  quick tour never mentions and the key does not cover. Mem0 and Onyx both hand administrator rights
  to whoever registers first, so the bootstrap has to happen before the deployment is reachable from
  anywhere but its own host.

### Fixed

- A sixth way past the copy-paste guard, found while testing the fifth (#60). The five earlier
  designs each constrained what happened after the guard ran; this one lands before it exists. The
  placeholder sat unquoted at its substitution site, so a reader pasting a URL with a query string
  had the ampersand background the `set --` itself, leaving the parameters empty while the rest of
  the line ran as its own command, and a value containing `$(...)` or a backtick simply executed.
  Every substitution site is now a single-quoted literal, which a guard cannot achieve because the
  shell evaluates the value first. Demonstrated three ways in bash; the fix is verified against
  bash, dash and BusyBox ash, with and without `set -u`, with the caller's own arguments intact.
- The six guards in the new guide, which the corpus-wide sweep had missed (#60). The sweep keyed on
  the variable name the other twelve files used, and this guide uses its own, so it shipped the form
  a `readonly` variable in the reader's shell defeats. Three `curl` invocations went the same way,
  sitting on indented continuation lines the sweep's line-anchored pattern never matched, and have
  gained the `-q` the rest of the corpus carries.
- The guard's seventh bypass, found by round-2 review after the sixth was fixed in the same change
  (#60). A block pasted without its `set --` line inherits whatever positional parameters the
  reader's shell already held, and a stale pair from an earlier experiment satisfies every check the
  guard makes, so the probe fires at the old target and its refusal is read as this target's
  evidence. Counting the values does not close it, because a shell holding the expected number
  passes the count; that was measured against the first fix, which is why the fix that shipped is a
  sentinel the block sets and shifts away. The whole historical bypass set was re-run against the
  sentinel rather than reasoned about: unsubstituted placeholder, stale-positional partial paste,
  `readonly`, `declare -i`, an exported value, `IFS`, caller arguments present, and a placeholder
  embedded in a longer value, across bash, dash and BusyBox ash under `set -u`. Two limits are now
  stated rather than papered over: a shell whose `set` has been shadowed defeats every guard at
  once, and a value containing an apostrophe cannot be carried inside the quotes.
- The Onyx development-form port inventory, which was short by two published ports (#60).
  `docker-compose.dev.yml` is an override, and its own header gives the launch form as
  `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --wait`, so the effective
  configuration includes the base file, which publishes nginx on `${HOST_PORT_80:-80}:80` and
  `${HOST_PORT:-3000}:80`. A reader probing exactly the ports this guide enumerated would have read
  "Fixed" with two ports still published. The same file settles a question this guide had recorded
  as unverified: host 3000 reaches nginx's container port 80, and `web_server` carries no host
  publication of its own.
- Eight band-1 errors across eight guides (#45), closing `TODO.md` band 1 to empty. Each was a
  guide asserting something false or a Verify step that could not discriminate: a missing
  `--cacert` that made an Elasticsearch check die on TLS rather than answer; a Tailscale claim that
  ignored how the fronted application binds; `ufw allow OpenSSH`, which admits the whole internet
  while `cloud-firewalls.md` rule 3 says SSH is not public; a PostgreSQL Verify step that could not
  tell a refused password from a refused connection; a Dify paragraph that implied a setting could
  unpublish a port the vendor Compose file publishes unconditionally; a cloud-firewall Verify step
  with no runnable command for any provider; curl -q exit 7 or 28 treated as proof of egress
  enforcement; and a Supabase section that never warned that views and `SECURITY DEFINER`
  functions run with their owner's rights, past RLS.
- Five QA rounds across three families produced the shipped text. Rounds 1 and 3 rejected, round 4
  accepted with changes, and round 5's single finding rested on a premise the guide did not state.
  Every finding was checked at its vendor source before it was applied, and two were rejected on
  evidence: a recollection that Dify's Compose file binds the plugin daemon to localhost, and a
  report that injecting `curl -k` survives the gate suite. Neither held.
- Three of the fixes had to be fixed again during review, all the same shape: removing a narrow
  allowance and leaving the broad one. A ufw rule added beside the old `allow OpenSSH`; a firewalld
  rich rule added beside an existing `--add-service=ssh`; and a Supabase view revoked from `anon`
  and `authenticated` while `PUBLIC` still granted it. The last was demonstrated on a live
  PostgreSQL: `has_table_privilege` stayed true and the view kept returning rows.
- The gate suite caught no semantic defect in any round, which is what the tri-family tier exists
  for. It did catch one defect in the original draft: SC2016 on a JMESPath backtick literal, which
  inside a shell command is a command substitution waiting to happen.
- `mlflow.md` and `ray.md` stopped reading a bare `--max-time` timeout as proof that a connection
  was blocked (#49), which `egress-metadata.md` had just said plainly it is not. Demonstrated with
  curl 8.18.0: a blackholed address and a listener that accepts TCP then stalls both return
  `http=000` and exit 28, so only `time_connect` separates a blocked port from a reachable one.
- Verify probes that targeted a literal reserved example address now reject an unsubstituted value
  locally (#50). Of 27 occurrences, 17 lines were probes whose pass signal is "nothing answered",
  where an unreplaced address times out exactly like a blocked port; the rest are configuration,
  certificate SANs, an ssh target and prose, where a wrong value fails visibly. Five QA rounds, and
  rounds 1, 3 and 4 each found a defect in the fix rather than in the original row: the placeholder
  alone traded one silent false pass for another, the guard warned and then ran the probe anyway,
  and under `set -u` a partial paste crashed in a way these steps call a refusal. `README.md`'s own
  checklist had the defect in its worst form, targeting `example.com`, which resolves and serves
  HTTPS, so its TLS check passed for every reader whatever state their deployment was in.
- Placeholder guards now unset their variable before assigning it, and five guides classify a local
  failure as inconclusive rather than a pass (#57). A pre-existing `declare -i` made the assignment
  arithmetic and silently set `0`, so the probe ran against nothing; `declare -l` lowercased the
  placeholder past the rejection pattern; and a stale exported value survived a paste that dropped
  the assignment. Separately, OpenBSD netcat returns exit 1 with no output at all when socket
  creation is denied, and BusyBox netcat rejects `-v` the same way, so "must fail to connect"
  accepted a check that never reached the network.

### Changed

- `VERSION` to 1.0.45.
- Maintainer rulings moved out of `TODO.md` into `DECISIONS.md`, and `PENDING-DECISIONS.md` added
  for questions awaiting a ruling during unattended operation (#51), in preparation for the OPF
  operational-files migration. Each ruling records the reasoning behind it, and a profile
  generalizes across them so fewer questions need asking; the profile is the orchestrator's
  inference, is marked fallible, and records where it has already been wrong. That change also
  corrected six rows whose ids used the priority band instead of the subject series, and restored
  the TLS-bypass gate's scope after a consistency edit had wrongly excluded the records files
  from it.
- `CONTRIBUTING.md` gains a "Shipping a change" section (#55): open the pull request, write its
  number into `VERSION`, push, then merge; merge in numeric order, and where that is not possible
  the later pull request sets the value; and record the change in `CHANGELOG.md` in the same pull
  request rather than a later one. The ordering rule exists because `VERSION` read literally makes
  the number go backwards when an older pull request merges last, which #50 did against a `main`
  already at 1.0.51.
- `CONTRIBUTING.md` rules 1, 5 and 6 (#60). Rule 1 gains a source-authority clause: for whether a
  control exists at all, the vendor's reference or CLI page is the authority, and absence from a
  quickstart is not evidence of absence. This repository had recorded Text Embeddings Inference as
  having no documented inbound authentication on the strength of its quick tour. Rule 5 gains an
  allowance for a check that cannot practically be run against the exposed state, which must then be
  marked at the step as reasoned rather than demonstrated; an unmarked step still claims a
  demonstration, so omitting the mark is itself a breach. Rule 6's prose had contradicted its own
  example ever since the guard became positional, and now gives the real reason for that form.
- Rule 5's reasoned-check allowance, narrowed the same day it was added (#60). Two review families
  independently reported that the first wording let an author mark anything reasoned. A reasoned
  step must now name the specific prerequisite that was unavailable, give the concrete command,
  state the expected exposed and fixed outcomes, and cite the vendor passage that distinguishes
  them; every locally feasible part is still run; a container on ordinary hardware is not
  impractical to stand up; and each reasoned mark opens a backlog row, because reasoned is a debt,
  not a destination.

### Records

- Backlog rotation and version bookkeeping: #46 moved the eight closed band 1 rows into `DONE.md`
  and opened three new band 1 rows and three new band 2 rows; #47 pinned `VERSION` to its own pull
  request number, correcting the stale value #46 shipped. #48 completed the pull-request references
  across every dated section and set `VERSION` to its own number, which is the authoring step row
  3.9 names.
- Backlog judgement and a second `VERSION` gap (#52). Row 1.38 asked for a per-guide judgement of
  46 filtered listener checks; all 46 were judged against the maintainer's ruling and none changed,
  because none claims that anything else is unexposed, 45 carry a trailing expectation comment, and
  the one without states its expectation in the prose below its block. Row 3.9 gained a second gap
  found while merging out of numeric order: the scheme names the most recently merged pull request,
  so when pull requests merge out of order the value goes backwards and no gate enforces
  monotonicity.
- Row 3.10 rotated to `DONE.md` (#54) now that the changelog-coverage gate it asked for is merged
  and green on `main`.
- The maintainer's four rulings of 2026-09-13 recorded in `DECISIONS.md`, and the two `.aiqt` local
  patches marked upstreamed in the PIN (#56). Guardrails accepted the `AIQT_SITE_HOST` change and is
  applying it as their own rather than taking a cross-repo pull request; preparing the details
  surfaced two problems in our own patches, an accidental lowercasing inconsistency between the two
  and an empty-value case that would make every dotted host resolve internal, and both were adopted.
  The patches drop when we re-pin to their first digest-verifiable release, which is the release row
  3.7 waits on.
- Four more rulings recorded, and two backlog rows corrected against their sources (#58). Row 2.15
  said Onyx has "complex default exposure"; the vendor documents authentication on by default since
  v4.4.0, `AUTH_TYPE` inert, and the real exposure being which compose file is run, since the
  production one publishes only nginx while the development one publishes seven services past the
  login page. That is the third of six row premises this verification pass overturned, after
  LangServe's deprecation and Mem0 shipping authentication on. Row 1.8 loses LocalAI to the new
  guide and records why, and row 1.43 opens for the published-backing-store pattern now seen in
  Dify, Mem0 and Onyx alike.
- Four more rulings recorded, and a second correction to the decision profile (#59). The
  permission-rule ruling is reversed on my own report that the evidence weakened; the
  AI-infrastructure guide gets two independent drafts rather than direct authoring; untested Verify
  checks ship marked as reasoned rather than demonstrated; and bands 2 and 3 stay ordered by the
  severity already recorded on each row. The profile now records two occasions in one day where a
  recommendation was overruled toward more rigour, so that pattern is evidenced rather than
  inferred.
- Row 3.9 rotated to `DONE.md` (#61). Its work shipped in #55 and has been live on `main` since; only
  the row was outstanding, and it was pulled out of a larger pending change at the maintainer's
  request so the backlog stops showing it as open.

## 2026-09-12

### Added

- `TODO.md` and `DONE.md` at the repository root (#38, #41). The backlog lived only in a private
  working store, so a question about it could not be answered without a summary, and writing it
  down exposed that the September audit's eighteen ranked coverage gaps were never recorded: five
  had shipped and thirteen are unrecoverable. A three-family audit replaced them, with codex and
  claude reading all 85 guides and gemini 16, producing sixteen gap rows and thirty enhancement
  rows, each naming what specifically to do. `DONE.md` records two terminal states, done and
  dropped, because a declined item that simply disappears gets proposed again.
- An Agent Plugin package (#39). `plugin.json` and one skill validated against the Agent Plugins
  and Agent Skills specifications, with the 86 guides bundled as `references/` so an adopter with
  no egress still has them, and `scripts/update-guides.sh` to refresh them and re-pin the version
  when there is network. The updater verifies every fetched guide against a published digest and
  replaces the bundle only once all of them match, so an interrupted run leaves the working bundle
  intact. Recording the bundle exposed two defects in the generated-file record gate: `kind` sat
  unused so a generated directory could not be recorded at all, and the build script did not
  declare the script it calls.
- `connection-poolers.md`, covering PgBouncer and pgpool-II (#30). A pooler becomes the thing
  clients connect to, so the database's own `hostssl` rules and TLS settings stop governing the
  client and start governing the pooler. Two PgBouncer defaults fail open: `client_tls_sslmode`
  is documented as "TLS connections are disabled by default", so a carefully TLS'd database
  gains nothing once a pooler fronts it, and `server_tls_sslmode` defaults to `prefer`, which
  "If refused, the connection will be established over plain TCP" and validates no certificate;
  `require` and `verify-ca` each close only half of that. A forced `user=` in a `[databases]`
  entry makes every client the same PostgreSQL role, so every `GRANT` and every per-user
  `pg_hba.conf` line stops discriminating. `exposure-index.md` gained 6432, 9898 and 9999.
- A shell-block gate (#27). Every fenced bash block is linted by shellcheck and parsed by
  `bash -n`, with the version reported rather than pinned, and a canary block whose finding has
  to come back: a reviewer silenced the real shellcheck through an environment variable so that
  it exited 1 with empty output, and the gate had read that as 156 blocks passing. It found five
  real defects in the corpus on its first run. A placeholder check shipped alongside it was
  deleted after five successive rules were each beaten by legal shell, the last by an ordinary
  `sed` substitution; CONTRIBUTING rule 6 now names that hazard as a review obligation and says
  plainly that no gate catches it reliably.
- A category gate covering `site/llms.txt` (#36). The README's guide index, the site menu and
  `llms.txt` are three hand-maintained copies of one category list, and nothing compared the
  third: it carried ten sections of its own against the README's twelve. The gate now checks all
  three, and checks `llms.txt`'s guide membership per category as well as its headings.
- A control-plane section in `kubernetes.md` (#23). A managed cluster's API server is reachable from
  the internet the moment the cluster is created, so a control plane nobody exposed on purpose is
  exposed; a kubeconfig may be a credential in itself or only a pointer to one, which decides what
  its disclosure costs; a self-managed control plane answers on 6443, 2379, 2380, 10250, 10255,
  10256, 10257 and 10259; the kubelet's flag and file defaults are opposites, so a reader who checks
  one learns nothing about the other; and GKE's DNS-based endpoint is not governed by authorized
  networks, so an allowlist that looks complete does not cover it. `exposure-index.md` gained rows
  for those ports.
- `self-hosted-idp.md`, covering Keycloak and authentik (#24). `hostname-admin` does not restrict
  the Administration REST API, so an operator who sets it can believe the administrative surface is
  closed while it answers; the administrative realm's login paths have to be restricted by source
  rather than refused; authentik's Compose install has a first-boot window in which whoever loads
  the page first becomes the administrator; and the management and metrics ports answer without
  asking who you are.
- `tools/check_gensrc.py` and `tools/test_gensrc_gate.py`, which gate `.aiqt/gensrc.json` against
  the build script it describes (#25). A new guide touches five wiring surfaces, and this was the
  fifth and the only one nothing checked, so the record of what generates `site/llms-full.txt`
  could fall out of step with the script that generates it while every other surface stayed green.


### Changed

- The backlog is banded and ordered by AIQT (#41, #42). Errors are band 1 and worked to empty
  before anything else, because a reader acting on a wrong guide is worse off than a reader with
  no guide; eight of the thirty rows against existing guides turned out to be errors rather than
  gaps. Band ids are decoupled from bands, so the reordering changed no identities.
- `site/_headers` pins the inline stylesheet by hash and drops `'unsafe-inline'` from
  `style-src`, with a gate that keeps the pin honest (#28). The gate refuses what it cannot
  model rather than modelling HTML: exactly one bare `<style>` and one bare `<script>`, every
  literal opener accounted for, no script-data escape states, no NUL byte, and one declared
  charset. Four review rounds of parser detail preceded that decision, and the round that
  settled it found the gate handing an author the hash of the empty string for a self-closing
  `<style/>` and going green once it was pinned.
- The weekly citation sweep reports where a cited page has moved, and fails the run when it has
  (#29). The link sweep accepts 301 and 302, so a moved citation passes it forever; #16 and #17
  were spent on that drift once it had spread across 82 citations. A green scheduled run
  notifies nobody, so a host or path move now reds the weekly workflow, which is not a required
  check and blocks no merge.
- `site/llms.txt` uses the README guide index's twelve categories, in the same order, with the
  same guides in each (#36). Seventeen entries that carried no description now have one, and two
  guides that were listed twice are listed once.

### Fixed

- `cors.md` and `host.md` cite the tools whose syntax they show (#35). `cors.md` demonstrated
  Express and FastAPI middleware while citing only MDN's protocol guide, and `host.md` showed five
  `ufw` and `firewall-cmd` invocations and cited neither tool, so rule 1 could not be exercised on
  either. A sweep for the same shape found ten more candidates, all false positives: this corpus's
  convention is for a source line to name the settings it covers, and they do.
- The DevProcess / OPF adoption is deferred and the reason recorded (#40). Its tooling ships in a
  later release, so adopting by hand would mean maintaining a TOML store and rendering its views
  by hand with no validator to catch drift between them, which is the defect class this repository
  already runs three freshness gates against.
- `chat-uis.md` no longer reproduces Chainlit's own login example (#31). The vendor's snippet
  compares a literal `"admin"` against a literal `"admin"`; the guide had swapped the literal
  for a house placeholder and kept both real defects underneath, a credential in application
  source compared with `==`. It reads both values from the environment and compares them with
  `hmac.compare_digest`, and the paragraph beside it no longer claims constant time the function
  does not promise, nor that rotating the password ends existing sessions, which
  `CHAINLIT_AUTH_SECRET` does.
- `kubernetes.md` no longer passes a password as a command-line argument (#33). Apache's own
  page says of `htpasswd -b` that "the password is clearly visible on the command line. For
  script use see the -i option", and the guide had copied Envoy Gateway's example. `-s` stays,
  because Envoy Gateway's basic auth documentation says "only SHA hash algorithm is supported
  for now", and the guide now says that rather than leaving SHA-1 looking like a free choice.
  `secrets.md` gained the rule that was missing, with the reason a probe for it is not offered:
  `grep` for the words password, token and secret finds only commands that spell them out, and
  a check that reads clean while the exposure is running is worse than none.
- `cloudflare.md` no longer publishes an application before authenticating it (#34). The guide
  said "The app is now reachable" at the end of step 2 and added Access in step 4, so a reader
  following the numbered order had a public, unauthenticated application in between, which
  `deployment-lifecycle.md` already warns against.
- `apache.md` and `lighttpd.md` probe more than the front door (#32). Four of the six
  fronting-proxy guides had been fixed and these two were missed, because neither proxies to an
  origin so the check the others use did not transfer. Apache's bypass is documented: an
  unmatched name falls through to "the first listed virtual host that matches" the address and
  port. Over TLS that name is the SNI one, so the probe sets both it and the Host header.
- `cors.md` and `host.md` cite the tools whose syntax they show (#35). `cors.md` showed Express
  and FastAPI middleware while citing only MDN's protocol guide, and `host.md` showed five
  `ufw` and `firewall-cmd` invocations and cited neither tool, so rule 1 could not be exercised
  on either.
- `kubernetes.md` and `memcached.md` gained Verify steps that discriminate (#26), and the
  changelog was brought up to date through #25.

### Records

- Changelog and version bookkeeping: #37 recorded #26 through #36 and set the version to match;
  #43 did the same for #35 and #38 through #42; #44 rotated rows 3.4 and 3.5 into `DONE.md`.

## 2026-09-11

### Added

- Two gates for conventions this repository stated and never checked (#21).
  `tools/check_verify_safety.py` fails when a command inside a Verify block skips TLS certificate
  verification, a rule stated in `common-mistakes.md`, `self-signed.md` and `README.sources.md` and
  broken in three Verify blocks before anything checked. `tools/check_prose_conventions.py` fails on
  British `-ise` spellings and on placeholders outside the house set. Both found defects live on `main`
  the first time they ran: `ray.md` carried `randomised`, which the corpus-wide conversion in #18 missed
  because its word list omitted that stem, and `pocketbase.md` carried `yourdomain.com`, a real
  registered domain that an audit had identified and no change had fixed.
- Three Verify steps that asserted a certificate check they did not perform (#21). `kafka.md`,
  `neo4j.md` and `memcached.md` each ran a bare `openssl s_client -connect` in a Verify block, two of
  them commented "TLS handshake with your certificate". Without `-CAfile`, `-verify_hostname` or
  `-verify_return_error` the handshake succeeds against any certificate, so the comment asserted what
  the command did not check, and `self-signed.md` and `rabbitmq.md` already carried the correct form.
  These surfaced only because the first version of the new gate got the openssl case backwards: it
  matched `-verify_return_error 0`, a syntax OpenSSL does not have, for a flag whose presence is the
  safe state. Cross-family review found the dead pattern, and fixing it exposed the guides behind it.
  The exemption for certificate inspection was removed after review showed it was a laundering pipe,
  since appending `| openssl x509` to an unverified handshake made the line pass, and the two guides
  that inspect a publicly trusted certificate, `deployment-lifecycle.md` and `free-certificates.md`,
  now pass because their commands carry `-verify_hostname` and `-verify_return_error`, not because an
  exemption covers them.
- `tools/test_convention_gates.py`, the regression suite for the two new gates (#21). It records one case
  per input a reviewer demonstrated against them, so every way past a gate that review found is a
  standing check rather than a one-off fix, and the inputs the gates still get wrong are asserted as the
  gates' current answer rather than dropped: quote state is per physical line, so a quotation spanning a
  line break hides what follows it, and inside a fence only a shell-style trailing comment is read as
  prose, so a hash inside a Python triple-quoted string is read as one. Both limits are named in the
  gates' docstrings as well.
- A "Bound the expensive endpoints" section in each of the four proxy guides (#20).
  `realtime-webhooks.md` and `authentication.md` both require request-size, concurrency and timeout
  limits on inference, upload and job-submission endpoints, naming denial of wallet as the failure
  mode, and `realtime-webhooks.md` recorded that the proxy guides did not carry those directives.
  They do now, and that sentence is rewritten to state what each proxy actually enforces rather than
  implying parity: nginx carries all four controls, Traefik body size, concurrency and rate but no
  timeout, HAProxy timeouts with an aggregate connection cap and a Content-Length body check, and
  Caddy body size only, with no rate limiting in its standard build. Two of those are CONTRIBUTING
  rule 3 statements rather than directives, since the control does not exist to configure. The change
  took four cross-family review rounds, three of them returning DO NOT SHIP from both families: the
  directives were correct throughout, while the snippets and the verification claims were not. Two
  snippets would have dropped a security directive if pasted over an existing block, so every snippet
  is now an explicit fragment, and the Verify steps report what they observe rather than asserting
  which limiter fired, because a backend returning the same status explains the result with no proxy
  limit present.
- `exposure-index.md`, a lookup from an observed listening port to the guides worth reading (#19). The
  corpus routes from a known mistake to its fix in `common-mistakes.md`; this routes from an observed
  symptom, which is the direction a reader arrives from. It claims deliberately little. A port does not
  identify a service here: 23 guides mention 3000, 21 mention 443, and six mention 8443, so the table says
  what may be listening and sends the reader to the owning process. Its Verify section is stated as a
  baseline inventory that cannot establish completeness, because a container on a bridge network
  publishes no host port and one on routed IPv6 answers on its own address whatever the host publishes.
  It took four cross-family review rounds: the first two returned DO NOT SHIP from both families, one
  for the false premise and one for a Verify section that certified an exposed application through an
  outbound tunnel and through endpoints no linked guide enumerates.
- A gate, `tools/check_guide_shape.py`, requiring every guide to carry a Verify section with a
  non-empty body and a `Sources (checked <month year>)` heading whose date names a real month, is not
  in the future, and cites at least one absolute URL with a hostname. It is deterministic and offline
  like the rest of the suite, and monotonic in time: its only date comparison can turn a failing guide
  into a passing one as the clock advances, never the reverse, so no build can go red from the
  calendar alone. The gate covers only the structural floor of `CONTRIBUTING.md` rule 5: it cannot
  prove that a Verify body holds a runnable command, that a Verify step fails while the service is
  still exposed, or that a cited page contains the line it is cited for, and it says so rather than
  implying wider coverage. `common-mistakes.md` is the one documented exemption. (#9)
- `README.sources.md`, holding the citations for the README verification checklist. The checklist
  names tools, status codes and services without citing them inline, so the sources now sit in a
  companion file and the front page stays readable. `README.md` is held to the same Verify and Sources
  contract as any guide, resolving its Sources through that file. Nothing mechanically ties a numbered
  check to its citation, so that correspondence is kept by reading. (#9)
- A fifth copy-ready prompt on the site that audits the AI and agent stack. (#6)
- A gate in `tools/run_all_checks.sh` that fails if the README guide-index category headings and the
  site menu category headings drift apart. (#6)

### Changed

- CONTRIBUTING rule 2 now states the Oxford `-ize` convention and the RFC 2606 placeholder set
  (#21). `tools/check_prose_conventions.py` enforces both, and rule 2 stated neither, so the gate
  was citing a rule as its source for something that rule did not say.

- Prose now uses Oxford `-ize` spellings throughout (#18). The corpus mixed British `-ise` and Oxford
  `-ize`, with the `-ise` forms holding the recurring line "login is not authorisation" in `README.md`,
  `authentication.md`, the `oidc-integration.md` heading and the site's front page. 27 instances were
  converted across 12 files. Technical identifiers were already `-ize` and are untouched: the
  `Authorization` header, `authorization_endpoint`, `authorizationEnabled`, AWS `authorizer`, and the
  term of art "authorization code flow". The case worth naming is `oidc-integration.md` lines 24 and 35,
  where prose `organisation` sat on the same line as the Microsoft Entra authority name `organizations`
  in backticks; both lines now carry the converted prose word and the identifier unchanged.

- The project was renamed from `sslconfig` to `secureconfig`. The GitHub repository is now
  `jposluns/secureconfig` and the site is served at `secureconfig.ai`; GitHub redirects the old
  repository path. Every
  absolute repository and site URL in `site/index.html`, `site/llms.txt`, `site/robots.txt`,
  `README.md` and `scripts/build-llms-full.sh` was updated, along with the `AIQT_SITE_HOST` gate
  variable in `tools/run_all_checks.sh` and the patch notes in `.aiqt/PIN`; `site/llms-full.txt` was
  regenerated. Earlier entries in this changelog keep the old name: they record what shipped under
  it. (#8)

- The `sslconfig.ai` domain was retired. Its DNS record was removed on 2026-09-11, so the old
  hostname no longer resolves and `secureconfig.ai` is now the only site hostname. GitHub continues
  to redirect the old `jposluns/sslconfig` repository path, but there is no redirect for the old
  domain: URLs in the wild that point at `sslconfig.ai` fail to resolve rather than forwarding. (#9)

- Three items in the README verification checklist were rewritten so that they discriminate. Each
  could previously be recorded as verified while the exposure it exists to catch was still standing.
  Item 4 now asks the reader to establish whether a failed `openssl s_client -tls1_1` came from the
  server or from a local client that never offered TLS 1.1, since the two are indistinguishable from
  the error alone. Item 7 now requires confirming that something is scheduled to invoke
  `certbot renew`, because a passing dry run proves the command works and nothing about whether it
  will ever be run. Item 10 no longer accepts a Shodan or Censys lookup in place of a live probe from
  a second host, because those services report what they last observed rather than what is listening
  now. (#10)

- The "Jump to" line was removed from the top of `site/index.html`. The left-hand menu and the
  in-page anchors it pointed at are unchanged. (#9)

- The README and the site front page (`site/index.html`) were realigned with the current corpus.
  One canonical description now appears in the README title, the site tagline, and both the meta and
  Open Graph descriptions. The AI-assistant rules, the decision guide, and the verification checklist
  were rewritten to cover identity and the allowlist, machine credentials, secrets, egress and
  metadata, exposed files, and the AI stack, and the README and site rule lists were reconciled. The
  flat guide index and the site menu were regrouped into the same twelve categories. No guide content
  changed. (#6)

### Fixed

- Seven accuracy defects, each re-checked against the vendor's own page or source before the edit, found
  by a tri-family QA scan of the whole corpus (#12). `model-servers.md` recommended a vLLM API key and
  verified only `/v1/models`; vLLM authenticates only the `/v1`, `/v2` and `/inference` prefixes and
  leaves `/invocations` open to the same inference capability, so a reader whose Verify step passed still
  had an unauthenticated inference endpoint. `workflow-orchestrators.md` named `[fab] auth_backends` to
  select Airflow's auth manager, which is `[core] auth_manager`; the FAB setting selects API
  authentication backends and is independent of it. `llm-observability.md` called the all-interfaces
  listener the OpenTelemetry Collector default, which has been `localhost` since v0.110.0.
  `nextjs.md` and `paas.md` still required Pro or Enterprise to protect a Vercel production domain,
  contradicting `cloud-identity-proxies.md`, which already carried the 9 September 2026 change making it
  free on every plan.
- Four Verify steps that could not discriminate (#12). The Prefect check expected a 401 on `/api/health`,
  which the server exempts on GET so container probes keep working, so it would have failed a correctly
  configured server; it now probes `POST /api/flows/filter`. The Langfuse check treated
  `/api/public/health` as an access-control test although it returns health status by design. The MinIO
  check tested the service root, which does not prove any bucket is private, because anonymous policies
  are set per bucket. The OTLP probe sent `{}` with curl's default form encoding, which the Collector
  rejects with 415 on content type before reaching authentication, so the rejection proved nothing.
- Nine Verify steps that could pass, or fail, for reasons unrelated to what they claim to prove (#13).
  `container-hardening.md` spliced the database address into a `kubectl --overrides` JSON array unquoted,
  so the override was not valid JSON, kubectl rejected it, and the guide's only proof that the default-deny
  NetworkPolicy blocks anything never ran; the same override named its container `probe` while `kubectl
  run` names the container after the pod, so a strategic merge would have added a container rather than
  replaced the command. Its read-only filesystem probe wrote to `/x`, which the configured non-root user
  cannot create on a writable filesystem either. `web-exposure.md` sent grep's errors to `/dev/null` and
  read empty output as clean, although grep exits 2 and prints nothing against a directory that does not
  exist, so a reader whose framework built elsewhere was told an unscanned bundle was clean; its ACME
  check also forbade a 404 on a challenge token it never created, which a correctly exempted directory
  returns anyway. `devops-uis.md` tested Docker client certificates with a command that does not enable
  TLS and could inherit a certificate from an export earlier in the same guide. `n8n.md` and `php.md`
  inferred route protection from a HEAD response and from cookie flags.
- `egress-metadata.md` verified the metadata services' header requirement rather than the network block
  the guide itself recommends as the control (#13). Added a probe of the block, sending the header the
  service requires, which must time out or be refused.
- Three Verify steps that disabled TLS certificate verification, which the corpus forbids in
  `common-mistakes.md`, `self-signed.md` and `README.sources.md` (#14). `elasticsearch.md` sent
  credentials over a connection whose certificate was never checked, and claimed in a comment that
  plaintext does not answer while making no plaintext request; `jupyter.md` and `devops-uis.md` probed
  with `curl -skI`. A `-k` probe passes against a substituted certificate as readily as against the real
  one, so the TLS half of each check proved nothing. All three now verify, and the plaintext refusal is
  its own check.
- A citation in `elasticsearch.md` that still returned 200 but redirected to a generic install page
  carrying no security configuration (#14). The weekly link sweep treats a redirect as passing, so a
  stale citation of this shape stays green indefinitely. Replaced with the current documentation home,
  and the page documenting the generated `http_ca.crt` is now cited beside it.
- The four fronting-proxy guides never checked the backend's bind address (#15).
  `common-mistakes.md` opens the corpus-wide list with "Binding to `0.0.0.0` to fix a connection
  problem and never binding back", and `nginx.md` repeats it as its own first common mistake, yet
  the Verify blocks in `nginx.md`, `caddy.md`, `haproxy.md` and `traefik.md` probed only the front
  door. All of those checks pass while the application also answers directly on port 3000, bypassing
  the proxy's TLS and authentication, so a reader in exactly the state this project ranks first
  collected four passes. Each Verify block now ends with the `ss -tlnp` check already used in
  `model-servers.md`, `vector-databases.md`, `docker.md` and the database guides; `traefik.md` also
  checks published container ports. `apache.md` and `lighttpd.md` serve content directly and front
  no backend, so the check does not apply to them and they were left alone.
- 82 citations that had silently moved (#16). An audit of all 767 URLs cited in the corpus found no
  broken links and 84 redirects to a different path. The weekly link sweep counts a redirect as
  passing, so a citation whose vendor reorganized its documentation stays green while pointing away
  from the syntax it supports. ClickHouse, Coolify, NATS, the GitHub Actions OIDC pages, Gateway API
  and Google Cloud all restructured; `encode/uvicorn` moved to `Kludex/uvicorn` and
  `kubernetes/dashboard` to `kubernetes-retired/dashboard`. Every replacement target was fetched and
  confirmed to resolve to itself, and where a redirect collapsed to a bare documentation root the
  real successor page was found instead. Two of the refreshed citations had been added earlier the
  same day, in #12 and #13. This also settles the disagreement between `README.md` and
  `README.sources.md` over the testssl.sh URL.
- Two URLs were deliberately left pointing at what looks like a stale target, because neither is a
  citation (#16). `cloud-identity-proxies.md` keeps `https://cloud.google.com/iap` as the JWT `iss`
  claim a reader validates Google IAP tokens against, and `egress-metadata.md` keeps
  `https://sts.amazonaws.com/` as the positive-control probe in its Verify block, which is the
  endpoint a workload calls for role credentials rather than a page to read.
- Four citations from #16 whose refreshed target stopped matching its own description (#17).
  `machine-auth.md` promised RFC 6749 section 4.4 while the new URL dropped the `#section-4.4` fragment,
  and now cites the IETF datatracker copy, which serves anchors. `python.md` promised a settings
  reference while the new URL landed on Gunicorn's home page; Gunicorn restructured its documentation and
  the reference is now at `/reference/settings/`, confirmed to carry `bind`, `certfile`, `keyfile` and
  `ca_certs`. Helicone and NATS each merged two pages into one, so `llm-observability.md` cited the same
  URL twice in a single bullet and `nats.md` cited one page from two bullets; both are now cited once.
  The detection gap worth recording: the audit flagged redirects that lost path depth, which catches a
  page collapsing to a documentation root, but not `docs.gunicorn.org/` redirecting to `gunicorn.org/`,
  where the depth is unchanged and only the host differs.
- The `rabbitmq.md` Verify step could not complete the mutually authenticated connection the guide's own
  configuration requires (#21). `ssl_options.fail_if_no_peer_cert = true` makes the broker demand a
  client certificate and the command supplied neither `-cert` nor `-key`, so the run that failed to
  connect still printed "Verification: OK", which reports the server certificate rather than the
  client's, and the comment named that line as the pass condition. It is now a pair: one invocation
  carrying client credentials that must reach a session, one without them that the broker must refuse,
  with the pass condition stated as the shape of the outcome rather than a message to match on. The
  negative run holds stdin open with `sleep 2` rather than closing it with `</dev/null`, because on TLS
  1.3 the server can only refuse an empty client certificate after the client's flight and s_client
  otherwise reaches end of input and exits before the rejection arrives; measured against a server
  requiring a client certificate, the `</dev/null` form exited 0 and printed a full session block in four
  trials of five, indistinguishable from the positive run.
- `deserialises` in `ray.md`, a second `-ise` spelling in the same file (#21). It sits in the opening
  risk statement, describing what cloudpickle does to arbitrary Python objects, and now reads
  `deserializes`.
- `kafka.md` named the unprefixed `ssl.client.auth=required` as the way to require client certificates
  (#21). The guide configures a SASL_SSL listener, and its own section 5 already states that the
  unprefixed setting applies to SSL listeners only and that Kafka logs a warning when it is set without
  the prefix on a SASL_SSL broker, so the advice was inert: a reader who followed it would have believed
  client certificates were required while they were not. It now names
  `listener.name.sasl_ssl.ssl.client.auth=required`, which is what the rest of the guide already says.
  The clause was added earlier in this branch and corrected within it.
- `ollama.md`'s bearer-token variant silently dropped two directives its `location /` variant
  carries (#22). `proxy_set_header Host localhost:11434` and `proxy_read_timeout 300s` are restored,
  so a reader who chose the authenticated variant gets the same upstream settings as the other one.
  The RunPod port wording in `gpu-clouds.md` was corrected in the same change.

### Records

- Changelog and version bookkeeping: #7 recorded the front-door realignment; #11 set the project
  version and completed the changelog for #9 and #10.

## 2026-09-10

### Added

- Nineteen guides from a three-family forward-looking gap review: `fronting-auth.md` (oauth2-proxy,
  Authelia, Pomerium wiring, which six existing guides already referenced), `web-exposure.md`,
  `egress-metadata.md`, `realtime-webhooks.md`, `container-hardening.md`, `deployment-lifecycle.md`,
  `image-gen-uis.md`, `chat-uis.md`, `llm-observability.md`, `workflow-orchestrators.md`,
  `gpu-clouds.md`, `nats.md`, `search-engines.md`, `bi-dashboards.md`, `pocketbase.md`,
  `frontend-frameworks.md`, `sqlite.md`, `tunnels.md`, and `surrealdb.md` (#5). Each cites vendor pages
  fetched in September 2026; unconfirmable details were left out.
- Sections folded into existing guides: a shared-cache disclosure section in `headers.md`, a
  fail-closed rule in `cloud-identity-proxies.md`, CAA records in `free-certificates.md`, an
  expensive-endpoint limit note and an offboarding rule in `authentication.md`, an offboarding check
  in `mfa.md`, Dozzle, Docker Registry, Filebrowser, and Node-RED in `devops-uis.md`, Hugging Face
  Spaces in `paas.md`, a Redpanda note in `kafka.md`, and a Valkey note in `redis.md` (#5).
- README gained an outside-in verification checklist item, a fronting-auth pointer in the
  authentication rule and decision guide, and index rows for every new guide; the site menu,
  `site/llms.txt`, the build script, and `.aiqt/gensrc.json` were updated to match (#5).
- Twenty-one guides: `identity-providers.md`, `oidc-integration.md`, `cloud-identity-proxies.md`,
  `machine-auth.md`, `nextjs.md`, `go.md`, `dotnet.md`, `java.md`, `php.md`, `ruby.md`, `kafka.md`,
  `clickhouse.md`, `neo4j.md`, `memcached.md`, `object-storage.md`, `vector-databases.md`,
  `mcp-servers.md`, `ray.md`, `mlflow.md`, `agent-builders.md`, and `devops-uis.md` (#4). Configuration
  syntax in each was checked against vendor documentation fetched in September 2026, and each
  guide's Sources section lists the pages. A three-family review (Claude, Codex, Gemini) of the
  whole branch then found and corrected further defects, listed under Fixed; details that no page
  confirmed were left out.
- `authentication.md` rules 11 to 15: federated login is not authorization, OIDC and OAuth hygiene,
  MFA enforced where access is granted, control-plane MFA, and authentication on every transport;
  plus a negative-test quick check (#4).
- `mfa.md`: a phishing-resistant factor for administrators, enrolment is not enforcement, a pointer
  to hosted providers, and a section on passkeys and hardware keys (#4).
- `common-mistakes.md` items 15 to 19, including federated login treated as authorization and MCP
  servers bound to all interfaces (#4).
- `model-servers.md` now covers Text Generation Inference, SGLang, Triton, and LM Studio (#4).
- README: an AI-assistant rule on federated login and a decision-guide entry for team and customer
  login (#4). Site: menu entries for every new guide, the same rule, and a fourth copy-ready prompt,
  "Add single sign-on and MFA".
- The wiring gate now also fails when a guide is missing from `README.md` or the site menu.

### Changed

- `kubernetes.md` rewritten on the Gateway API (Envoy Gateway, cert-manager Gateway support,
  SecurityPolicy for basic auth and OIDC) because the Kubernetes project retired ingress-nginx in
  March 2026 with no further releases or security patches. The guide tells readers how to detect
  ingress-nginx and that migration is required.
- `free-certificates.md` carries Let's Encrypt's announced lifetime schedule (64-day certificates
  from 2027-02-10, 45-day from 2028-02-16, an industry cap of 47 days from 2029-03-15) and notes
  that Let's Encrypt ended OCSP on 2025-08-06, so no stapling directives for its certificates.
- `paas.md` distinguishes platform deployment protection (Vercel) from application user
  authentication instead of saying the platform authenticates nobody.
- `redis.md` describes mutual TLS as a possession factor for machine clients, not MFA for a person.
- `linkcheck.yml` documents why 403, 429, and 999 are accepted: a green sweep proves every URL
  answered, not that every page was readable.

### Fixed

- `tools/check_site.py` reads the site host from `AIQT_SITE_HOST`, so absolute `sslconfig.ai`
  self-links in `site/index.html` are resolved rather than skipped as external. Recorded as a local
  patch in `.aiqt/PIN`.
- `CLAUDE.md` and `AGENTS.md` now describe the wiring gate's real coverage, and `.aiqt/gensrc.json`
  lists every source of `site/llms-full.txt`.
- Pre-existing guide defects found by the review: Redis inline comments that its parser rejects;
  PostgreSQL `listen_addresses` needing a restart rather than a reload; MongoDB client examples
  lacking the certificate the server configuration demanded; Caddy `/admin/*` not matching
  `/admin`; lighttpd `mod_redirect` not loaded; SSH MFA advice that conflicted with
  `KbdInteractiveAuthentication no`; Open WebUI's persisted `ENABLE_SIGNUP`; the Streamlit login
  example admitting any Google account; the multi-port `nc` check in `cloud-firewalls.md`; and
  several inline comments inside properties and INI values in the new guides.
- A gate that recomputes the sha256 of every inline script in `site/index.html` and requires it in
  the effective CSP line of `site/_headers`; the wiring gate now matches real index rows and menu
  links rather than any text; same-page anchors are validated.

## 2026-09-09

### Added

- An offline gate suite, `tools/run_all_checks.sh`, run on every pull request and on every push to
  `main` as the check `gates`. Four checks to start: `site/llms-full.txt` matches a fresh build,
  every guide is listed in the build script and linked from `site/llms.txt`, every local link target
  and heading anchor resolves, and no private keys or provider tokens appear in tracked files. Every
  check is deterministic and offline, so nothing outside this repository can turn the build red.
  (#1)
- An AIQT Guardrails baseline, vendored and pinned to guardrails
  `8ab5b9ae37cdf4f8bcdb0a73934cb5a58b2aea87`. `CLAUDE.md` and a byte-identical `AGENTS.md` carry the
  AIQT priority ordering and the five rules. The pack's hooks are vendored under `.aiqt/` but are
  deliberately not activated. Three upstream gates joined the suite: `check_site`, `check_no_dashes`,
  and `check_newtab`. The pin and the local patches to re-apply on upgrade are recorded in
  `.aiqt/PIN`. (#2)

### Changed

- Every external link in `site/index.html` now opens in a new tab with `rel="noopener noreferrer"`.
  Fifty-five links changed; the four `sslconfig.ai` links are internal and were left alone. (#2)

### Fixed

- The weekly link check had failed since 2026-09-07 because lychee cannot resolve the root-relative
  `/favicon.svg` in `site/index.html` without a root directory. Passing `--root-dir` fixes it, and
  the sweep now reports 555 of 555 links good. (#1)

### Repository settings

- `main` is protected: a pull request is required, force-push and deletion are blocked, and the
  `gates` check must pass before a merge.
- Issues and pull requests were both disabled on the repository and are now enabled. Pull requests
  being disabled is why the API rejected every attempt to open one, reporting it misleadingly as a
  personal-access-token permission error.

### Records

- #3 added this changelog and exempted it from the guide-coverage gate.
