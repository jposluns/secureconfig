# DONE

Closed backlog items, newest first. One line each, in the same shape as `TODO.md`: the permanent
id, what it was, and how it ended. Ids are never reused, so an id here never reappears there.

An item reaches this file in one of two states. **Done** means the work shipped. **Dropped** means
it was considered and declined, and the row says why, because a declined item that simply vanishes
gets proposed again six months later.

| ID | Item | Ended |
| --- | --- | --- |
| 1.36 | Literal example addresses in runnable Verify probes read as a pass when the reader has not substituted them: an unreplaced reserved address times out exactly like a blocked port | Done, #50. 17 of 27 occurrences changed after per-guide judgement; the other 10 are configuration, certificate SANs, an ssh target and prose, where a wrong value fails visibly. Five QA rounds, each of rounds 1, 3 and 4 finding a defect in the fix rather than the row. Residual gaps recorded as 1.42 |
| 1.37 | `mlflow.md` and `ray.md` treated a bare `--max-time` timeout as proof that a connection was blocked, contradicting `egress-metadata.md` | Done, #49. Demonstrated with curl 8.18.0 that a blackholed address and a listener that accepts TCP then stalls both return `http=000` and exit 28, so only `time_connect` separates them |
| 1.38 | Judge each of the 46 `ss ... \| grep <port>` checks against the maintainer's ruling that a filter asking whether one service is bound to loopback is correct for what it claims | Done, no guide changed. All 46 judged: none claims that anything else is unexposed, 45 carry a trailing expectation comment, and the one without states its expectation in the prose below its block. Converting them anyway would be the corpus-wide sweep the ruling rejected. `elasticsearch.md`, `postgresql.md` and `tailscale.md` use ss's native `sport = :N` filter because rows 1.14, 1.22 and 1.15 changed those checks for other reasons, not because of this row |
| 3.3 | Complete the `(#N)` pull-request references in `CHANGELOG.md`. The row's premise was wrong twice: it named PRs 4 and 5, which were already referenced, and the real gap was the eight records-maintenance pull requests, which is systematic rather than scattered | Done, #48 |
| 1.7 | `firebase-supabase.md` never warned that a Supabase view or a `SECURITY DEFINER` function runs with its owner's rights and serves rows past RLS | Done, #45 |
| 1.10 | `agent-builders.md` implied that disabling Dify's debugging feature unpublishes port 5003; the vendor Compose file publishes it unconditionally with no host address | Done, #45 |
| 1.14 | `elasticsearch.md` Verify line 1 had no `--cacert`, so it died on TLS verification and could certify nothing | Done, #45 |
| 1.15 | `tailscale.md` asserted tailnet-only reach without an `ss` bind check; `serve` does not change how the fronted app binds | Done, #45 |
| 1.18 | `cloud-firewalls.md` Verify step 1 named no runnable command for any provider, and all three sources were documentation roots | Done, #45 |
| 1.22 | `postgresql.md` could not tell a refused password from a refused connection, so an earlier `trust` record was invisible | Done, #45 |
| 1.25 | `egress-metadata.md` declared curl exit 7 or 28 proof that egress policy blocked the host | Done, #45 |
| 1.34 | `host.md` used `ufw allow OpenSSH`, which admits the whole internet, contradicting rule 3 of `cloud-firewalls.md` | Done, #45 |
| 3.4 | Changelog close-out for #35 and #38 to #42, and re-pin `VERSION` from a stale 1.0.37 | Done, #43 |
| 3.5 | Dispatch cross-family QA against a throwaway copy, and re-verify every finding against the current file before applying it | Done: adopted 2026-09-13, carried in the /flow skill's project mapping and its closing section |
| 2.1 | Package the corpus as an Agent Plugin, bundled for offline adopters with a digest-verified updater | Done, #39 |
| 3.1 | Put the backlog in the repository rather than a private working store | Done, #38 |
| 1.1 | Cite the tools whose syntax `cors.md` and `host.md` show | Done, #35 |
| 1.2 | Close the window where `cloudflare.md` publishes an app before authenticating it | Done, #34 |
| 1.3 | Stop passing a password on the command line in `kubernetes.md`, and add the missing `secrets.md` rule | Done, #33 |
| 1.4 | Probe more than the front door in `apache.md` and `lighttpd.md` | Done, #32 |
| 1.5 | Stop reproducing Chainlit's own insecure login example in `chat-uis.md` | Done, #31 |
| 2.2 | Cover connection poolers (PgBouncer, pgpool-II) | Done, #30 |
| 3.2 | Give `site/llms.txt` the README's categories, and gate the three against each other | Done, #36 |
| 4.1 | Add a skip link to `site/index.html` | Dropped: SC 2.4.1 governs content repeated across multiple pages and this is one page, and the sufficient technique ARIA11 is already satisfied by `<nav aria-label>` plus `<main>` |
