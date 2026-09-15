# Security policy

secureconfig publishes deployment-exposure hardening guides, all dedicated to the public domain
under CC0. The guides are documentation; the code that ships is the Agent Plugin under `plugin/` and
the helper scripts under `tools/` and `scripts/`.

## Reporting a vulnerability

Report privately through GitHub's private vulnerability reporting: open the repository's **Security**
tab and choose **Report a vulnerability**. That opens a private advisory visible only to the
maintainers. Please do not open a public issue for a security report.

Helpful things to include: the affected guide, script, or file; the exact commit; what a reader or a
running system would do wrong as a result; and how you confirmed it. A proof of concept helps, but a
clear description of the defect is enough.

## What is in scope

- A guide that instructs a reader to apply an insecure configuration, or a Verify step that passes
  while the exposure it is meant to catch is still live.
- A plugin or helper script that writes outside its intended path, executes untrusted input, or
  mishandles a secret.
- An invented flag, a stale default, or a broken command that a reader would copy onto an
  internet-facing system.

Documentation accuracy is a security property here, because a reader copies these configurations onto
systems that face the internet. A factual defect in a guide is in scope, not merely a typo.

## Handling

Reports are triaged privately. A confirmed issue is fixed on `main` through the normal pull-request
and gate process, and the reporter is credited in the advisory unless they ask otherwise. There is no
release artifact to patch separately: `main` is the published state, versioned as `1.0.<pull request
number>`.
