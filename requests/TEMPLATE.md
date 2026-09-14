# Guide request: APPLICATION NAME

Copy this file to `requests/<application-name>.md`, fill in what you can, and open a pull request.
Leave a field blank rather than guessing; note where you are unsure. Facts you supply are re-verified
against the vendor's documentation before a guide ships, so a link to the exact page beats a
recollection.

## What it is

One or two lines: what the application does, and the project or vendor that maintains it.

## Why it needs a guide

What a reader is likely to get wrong, or the specific exposure that prompted this request. If a
public incident or a common misconfiguration motivates it, say so.

## How it is typically deployed

Container image, single binary, Compose or Helm, or a managed offering. Name the usual install path
and the version you are looking at.

## Default network exposure

- Ports it listens on, and the default bind address (loopback, a private interface, or all
  interfaces / `0.0.0.0`).
- Whether the quickstart publishes it to the internet.
- Any secondary listeners: metrics, admin API, debug, clustering, replication, or a backing store.

## Default authentication

- Is there a login out of the box, or is the app open until you configure one?
- Any default or blank credentials, or an auto-generated initial secret and where it is written.
- How authentication is enabled, and whether MFA and SSO are supported.

## File, secret, and API surfaces

- Does it serve or read files from a configurable directory?
- Where does it expect secrets, and does it write any into state, logs, or images?
- API keys, webhooks, or machine tokens, and how they authenticate.

## Vendor documentation

Links to the authoritative pages: configuration reference, security or hardening docs, the
authentication page, and any page that names the defaults above. These are what the guide will cite.

## What you have already checked

Anything you verified yourself (a default confirmed, a probe run), so it does not have to be
rediscovered. Note the version and how you checked.
