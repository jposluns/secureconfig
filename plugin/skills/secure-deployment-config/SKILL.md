---
name: secure-deployment-config
description: Configure TLS, authentication, MFA, secrets and network exposure for a service you are deploying, or review one that is already running. Use when setting up or changing nginx, Apache, Caddy, HAProxy, Traefik, Docker, Kubernetes, PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, MinIO, Kafka, RabbitMQ, Ollama, vLLM, Jupyter, Gradio, Streamlit, n8n, Supabase, Firebase, a model server, a vector database, an MCP server, an agent builder, a chat or image UI, a dashboard, or any service that will listen on a port. Also use when asked to make something "production ready", to expose a local service, to add a login, to put a domain in front of an app, or to check whether a deployment is safe.
license: CC0-1.0
compatibility: Reference material only. No network access required; every guide is bundled. Commands in the guides are run by you against the user's own systems.
metadata:
  source: https://github.com/jposluns/secureconfig
  version: "1.0.38"
---

# Secure deployment configuration

Publicly reachable services built with AI assistance are routinely deployed on plain HTTP with no
authentication. This skill carries 85 short guides that close that gap, one per service or
control, each line traced to the vendor page it came from.

**A reader copies these configurations onto a system that faces the internet. An invented flag or
a stale default is a security defect, not a typo. Every guide's Sources section is dated; if a
default matters to the decision you are making, check it against the linked vendor page rather
than trusting the bundled copy.**

## Rules that apply to every deployment

Apply these whether or not a specific guide is open:

1. Treat every service as internet-reachable until you have confirmed otherwise. Bind to
   `127.0.0.1` by default and expose only through a TLS-terminating layer you configured.
2. Choose the certificate and access path before configuring exposure. Public DNS name with
   reachable 80 and 443: `references/free-certificates.md`. Behind NAT or no public ports:
   `references/cloudflare.md` or `references/tunnels.md`. Internal or local only:
   `references/self-signed.md`.
3. Apply every guide that fits, not just one. A deployment usually needs the service guide, its
   host or platform, containers where used, plus identity, secrets and the operational guides.
4. Redirect HTTP to HTTPS, or do not listen on HTTP at all.
5. Require authentication on every non-public endpoint. Never ship default or hardcoded
   credentials. Add MFA to human logins where viable (`references/mfa.md`). Where a tool has no
   native authentication, say so and put a fronting layer in front of it rather than inventing
   an option it does not have.
6. **A successful login is not authorization.** Check the returned identity against an allowlist
   (tenant, hosted domain, group, or explicit users) before granting access.
7. Keep secrets out of the repository and out of command lines. Load them from the environment or
   a secret manager (`references/secrets.md`), and give each service its own scoped credential.
8. Contain what an exposed or compromised service can reach: block unneeded outbound access and
   lock down cloud metadata (`references/egress-metadata.md`), and never serve dotfiles, dumps or
   `.git` (`references/web-exposure.md`).
9. AI and data tools vary wildly in their defaults and many need authentication added in front
   rather than configured within.
10. **Run the Verify steps before reporting the work as complete, and report what you could not
    test rather than asserting it passed.**

## Verify steps are the point, not the configuration

Every guide ends with a Verify section, and those steps are written to a specific standard: a
Verify step must FAIL while the service is still exposed. A check that passes in both the broken
and the fixed state is worse than no check, because it manufactures confidence.

So when you finish configuring something:

- Run the guide's Verify block and show the user the actual output.
- Probe from OUTSIDE the host where the guide says to. A check run on the box proves the service
  is listening, not that a firewall or a published container port is doing what you think.
- If a step cannot be run in the user's environment, say which one and why. Do not substitute a
  weaker check and report success.
- Never disable certificate verification to make a check pass. No guide here does, and a probe
  with verification off is not evidence about a deployment with it on.

## Choosing guides

Take every route that applies.

| Situation | Start with |
| --- | --- |
| Public web app with its own domain | `free-certificates.md`, then your web server or proxy, then `authentication.md` |
| Home server or behind NAT, domain on Cloudflare | `cloudflare.md`; with no domain at all, `tailscale.md` or `tunnels.md` |
| Internal tool, staging, local development | `self-signed.md`, with authentication still enabled |
| Human login or SSO | `identity-providers.md` to choose, `self-hosted-idp.md` if you run it, `oidc-integration.md` to integrate |
| Service-to-service or agent access | `machine-auth.md`, `secrets.md` |
| AI or agent deployment | the matching model-server, MCP, agent-builder, vector-database or UI guide, plus `egress-metadata.md` |
| Containers and clusters | `docker.md`, `container-hardening.md`, `kubernetes.md`, then the host or cloud guide |
| Databases, storage, messaging | the service guide; keep them off public interfaces entirely where possible |
| A pooler or proxy in front of a database | `connection-poolers.md`: it moves the client-facing TLS and host rules off the database |
| Web application exposure | `web-exposure.md`, `headers.md`, `cors.md`, `realtime-webhooks.md` |
| First deployment, preview, teardown | `deployment-lifecycle.md`, then `common-mistakes.md` |

Two references answer questions rather than covering a tool:

- `references/exposure-index.md` maps an open port to the guides worth reading. A port never
  identifies a service on its own; use the owning process from `ss`.
- `references/common-mistakes.md` is the recurring findings, each linked to its fix. Worth
  reading before a review.

`references/README.md` carries the full index of all 85 guides by category, and the verification
checklist to run at the end of a deployment.

## What this skill does not do

It does not cover application-layer vulnerabilities, dependency scanning, or compliance regimes.
It covers deployment exposure: how a service is reached, who is allowed to reach it, and what it
can reach in turn. Where a tool genuinely has no native control, the guide says so plainly and
gives the fronting-layer pattern instead of inventing an option.
