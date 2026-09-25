# Security policy

secureconfig publishes deployment-exposure hardening guides, all dedicated to the public domain
under CC0 (the AIQT Guardrails material listed in `.aiqt/PIN` is Apache-2.0). The guides are
documentation; the code that ships is the Agent Plugin under `plugin/` and
the helper scripts under `tools/` and `scripts/`.

## Reporting a vulnerability

Report privately through GitHub's private vulnerability reporting: open the repository's **Security**
tab and choose **Report a vulnerability**, which opens a private advisory rather than a public issue.
GitHub adds you to that advisory as a collaborator, so the discussion stays between you and the
maintainers. Please do not open a public issue for a security report.

Private reporting has to be enabled on the repository for that button to appear. If it is not there,
open a regular issue asking only for a private security contact, with no vulnerability details, and
the maintainer will follow up.

Helpful things to include: the affected guide, script, or file; the exact commit; what a reader or a
running system would do wrong as a result; and how you confirmed it. A proof of concept helps, but a
clear description of the defect is enough.

## What is in scope

This policy covers defects in secureconfig's own guidance and code, not vulnerabilities in the
third-party products the guides document; report those to their respective vendors. Examples of
in-scope issues:

- A guide that instructs a reader to apply an insecure configuration, or a Verify step that passes
  while the exposure it is meant to catch is still live.
- A plugin or helper script that writes outside its intended path, executes untrusted input, or
  mishandles a secret.
- An invented flag, a stale default, or a broken command that a reader would copy onto an
  internet-facing system.

Documentation accuracy is a security property here, because a reader copies these configurations onto
systems that face the internet, so a factual defect that could lead a reader to deploy insecurely is
in scope. Ordinary editorial corrections are welcome as normal issues or pull requests instead.

## Handling and supported versions

Reports are triaged privately. A confirmed issue is fixed on `main` through the normal pull-request
and gate process, and the advisory names the affected and fixed commits; you are credited unless you
ask otherwise. Fixes target the current `main`, which is the published state, versioned as
`1.0.<pull request number>`. There is no separate release artifact, so an installed plugin bundle or
a copied guide must be refreshed against `main` to pick up a correction.
