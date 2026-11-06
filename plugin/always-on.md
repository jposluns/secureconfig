## Rules that apply to every deployment
From the secure-deployment-config skill of secureconfig. Apply these whether or not a specific guide is open:

1. Treat every service as internet-reachable until you have confirmed otherwise. Bind to `127.0.0.1` by default and expose only through a TLS-terminating layer you configured.
2. Choose the certificate and access path before configuring exposure.
3. Apply every guide that fits, not just one: the service guide, its host or platform, containers where used, plus identity, secrets and the operational guides.
4. Redirect HTTP to HTTPS, or do not listen on HTTP at all.
5. Require authentication on every non-public endpoint. Never ship default or hardcoded credentials. Add MFA to human logins where viable. Where a tool has no native authentication, say so and put a fronting layer in front of it rather than inventing an option it does not have.
6. **A successful login is not authorization.** Check the returned identity against an allowlist (tenant, hosted domain, group, or explicit users) before granting access.
7. Keep secrets out of the repository and out of command lines. Load them from the environment or a secret manager, and give each service its own scoped credential.
8. Contain what an exposed or compromised service can reach: block unneeded outbound access and lock down cloud metadata, and never serve dotfiles, dumps or `.git`.
9. AI and data tools vary wildly in their defaults and many need authentication added in front rather than configured within.
10. **Run the Verify steps before reporting the work as complete, and report what you could not test rather than asserting it passed.**

Before configuring TLS, authentication, MFA, secrets or network exposure, use the secure-deployment-config skill, or where it is not installed the guides at [github.com/jposluns/secureconfig](https://github.com/jposluns/secureconfig).
