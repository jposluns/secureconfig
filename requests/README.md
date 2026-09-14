# Requests: ask for a guide that does not exist yet

secureconfig covers many self-hosted services, but not every one. If the application you are
securing has no guide here, you can request one, and in the meantime secure it yourself against
[controls-reference.md](../controls-reference.md).

## Who this is for

Anyone, including an AI development assistant working on a project. If your assistant reaches a
service with no guide, it can open a request here as part of its work, then fall back to the
control patterns in [controls-reference.md](../controls-reference.md) for the deployment at hand.

## How to request a guide

1. Copy [TEMPLATE.md](TEMPLATE.md) to a new file in this directory named after the application, in
   lower case with hyphens, ending in `.md` (for example `requests/some-app.md`).
2. Fill in every field you can. The more of the default exposure, the default authentication, and
   the vendor documentation you supply, the faster the guide can be written and verified.
3. Open a pull request adding that one file. One application per file, one file per pull request.

## What happens next

A maintainer reviews the request and writes a guide when able, verifying every fact against the
vendor's documentation before it ships. A request records that an application is wanted; it is not
a commitment to a date, and it is not itself a guide. Do not wait on it to secure a live
deployment: run the alignment assessment in [controls-reference.md](../controls-reference.md) now,
and let the guide, when it lands, replace your private assessment with a verified one.

## While you wait

Use the existing guides as worked references for the kinds of controls that apply, and
[controls-reference.md](../controls-reference.md) as the generic checklist. Most services share the
same exposure patterns: a listener that should be private, an admin surface that needs
authentication and MFA, secondary ports that bind wide, and secrets that must stay out of images
and state. The reference walks each one and tells you how to check it against your application.
