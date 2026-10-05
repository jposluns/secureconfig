---
version_basis: {
  "schema": 1,
  "checked": "2026-10-05",
  "documentation_checked": "2026-09",
  "body_sha256": "fd5dcbe53a69e2309c275305c08edeedf01fc6d48abefdbd2025da6d32f49074",
  "components": {
    "totp": {
      "name": "TOTP standard",
      "basis": "unknown",
      "sources": {
        "s3190460e5d2d": "https://www.rfc-editor.org/info/rfc6238/"
      }
    },
    "hotp": {
      "name": "HOTP standard",
      "basis": "unknown",
      "sources": {
        "s05c8bf9b6329": "https://www.rfc-editor.org/info/rfc4226/"
      }
    },
    "uri": {
      "name": "Authenticator key URI format",
      "basis": "unknown",
      "sources": {
        "s4c73b28585c7": "https://github.com/google/google-authenticator/wiki/Key-Uri-Format"
      }
    },
    "webauthn": {
      "name": "WebAuthn standard",
      "basis": "unknown",
      "sources": {
        "sef2c27817118": "https://www.w3.org/TR/webauthn-2/"
      }
    },
    "authelia": {
      "name": "Authelia proxy support",
      "basis": "unknown",
      "sources": {
        "s1409ac8fe3d9": "https://www.authelia.com/integration/proxies/support/"
      }
    },
    "caddy-min": {
      "name": "Caddy forward_auth minimum",
      "basis": "2.5.1",
      "sources": {
        "s1409ac8fe3d9": "https://www.authelia.com/integration/proxies/support/"
      }
    },
    "duo": {
      "name": "Duo editions",
      "basis": "unknown",
      "sources": {
        "sb2b87daf72f0": "https://duo.com/editions-and-pricing"
      }
    },
    "ssh-pam": {
      "name": "SSH and PAM MFA (citation gap)",
      "basis": "unknown",
      "sources": {
        "s3190460e5d2d": "https://www.rfc-editor.org/info/rfc6238/"
      }
    },
    "supabase": {
      "name": "Supabase Auth MFA (citation gap)",
      "basis": "unknown",
      "sources": {
        "s3190460e5d2d": "https://www.rfc-editor.org/info/rfc6238/"
      }
    },
    "access": {
      "name": "Cloudflare Access MFA (citation gap)",
      "basis": "unknown",
      "sources": {
        "s3190460e5d2d": "https://www.rfc-editor.org/info/rfc6238/",
        "sef2c27817118": "https://www.w3.org/TR/webauthn-2/"
      }
    },
    "mysql": {
      "name": "MySQL interactive MFA (citation gap)",
      "basis": "unknown",
      "sources": {
        "sef2c27817118": "https://www.w3.org/TR/webauthn-2/"
      }
    },
    "identity-layers": {
      "name": "authentik, Keycloak and oauth2-proxy MFA (citation gap)",
      "basis": "unknown",
      "sources": {
        "s3190460e5d2d": "https://www.rfc-editor.org/info/rfc6238/",
        "sef2c27817118": "https://www.w3.org/TR/webauthn-2/"
      }
    },
    "entra-docs": {
      "name": "Microsoft Entra documentation",
      "basis": "231747abc59ae3d50c74e215c1cdd592eb980723",
      "sources": {
        "s1341b9dbdad1": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/users/users-revoke-access.md#L58-L62",
        "s2c2f323edbd0": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/policy-all-users-mfa-strength.md#L56-L57",
        "sda22c238526b": "https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/authentication/how-to-mfa-number-match.md#L12"
      }
    },
    "owasp-docs": {
      "name": "OWASP cheat sheets",
      "basis": "668ba7db3d0da5868b8a0305c259f7f6914a6ecd",
      "sources": {
        "se60f5c9f1c55": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Secrets_Management_Cheat_Sheet.md#L218",
        "s2940f630fb71": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Multifactor_Authentication_Cheat_Sheet.md#L154-L155",
        "sa72b5658a19b": "https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Multifactor_Authentication_Cheat_Sheet.md#L142-L143"
      }
    },
    "otp-source": {
      "name": "pquerna/otp source",
      "basis": "617f8d5f3f518bae0f5c3ec14a17ca19f2a6f870",
      "sources": {
        "s7c4c6d57f705": "https://github.com/pquerna/otp/blob/617f8d5f3f518bae0f5c3ec14a17ca19f2a6f870/README.md#L27-L30",
        "s9dc96c06d6a0": "https://github.com/pquerna/otp/blob/617f8d5f3f518bae0f5c3ec14a17ca19f2a6f870/README.md#L15-L18"
      }
    },
    "nist": {
      "name": "NIST digital identity guidelines",
      "basis": "SP 800-63B-4",
      "sources": {
        "s4e1146860142": "https://pages.nist.gov/800-63-4/sp800-63b/authenticators/#look-up-secrets"
      }
    },
    "authelia-source": {
      "name": "Authelia source",
      "basis": "v4.39.28",
      "sources": {
        "sfeb54a05c30d": "https://github.com/authelia/authelia/blob/v4.39.28/docs/content/configuration/second-factor/introduction.md#L21-L31"
      }
    },
    "pyotp-source": {
      "name": "PyOTP source",
      "basis": "cc156832fa9f3d5af7fb9e4e6b86b29dfc5b69f1",
      "sources": {
        "sff126dae123b": "https://github.com/pyauth/pyotp/blob/cc156832fa9f3d5af7fb9e4e6b86b29dfc5b69f1/README.rst#L4-L9"
      }
    },
    "python-qrcode-source": {
      "name": "Python qrcode source",
      "basis": "f92c007498d796e4825638b7d50c14ea51e5457a",
      "sources": {
        "s9481cd1c5c1c": "https://github.com/lincolnloop/python-qrcode/blob/f92c007498d796e4825638b7d50c14ea51e5457a/README.rst#L5-L8"
      }
    },
    "django-otp-source": {
      "name": "django-otp source",
      "basis": "88cf4970423b11f29d6840311f53378d007a3d63",
      "sources": {
        "s3b66277026d8": "https://github.com/django-otp/django-otp/blob/88cf4970423b11f29d6840311f53378d007a3d63/README.rst#L16-L28"
      }
    },
    "otplib-source": {
      "name": "otplib source",
      "basis": "c5c11be2a50fd864b587854bff6d97c5f8aa9c84",
      "sources": {
        "s1cfb4a0cb98d": "https://github.com/yeojz/otplib/blob/c5c11be2a50fd864b587854bff6d97c5f8aa9c84/README.md#L13"
      }
    },
    "node-qrcode-source": {
      "name": "Node qrcode source",
      "basis": "3848ed2c17de5bcdead487417dbf14c5dd017f8d",
      "sources": {
        "s427c06d742cf": "https://github.com/soldair/node-qrcode/blob/3848ed2c17de5bcdead487417dbf14c5dd017f8d/README.md#L2"
      }
    },
    "openssh-source": {
      "name": "OpenSSH portable source",
      "basis": "V_9_9_P2",
      "sources": {
        "sf299a4e3603a": "https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sshd_config.5#L197-L211",
        "s862f0df9ce84": "https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sshd_config.5#L2017-L2026"
      }
    },
    "duo-unix-source": {
      "name": "Duo Unix source",
      "basis": "91e3c987f256afdb166b26be777cef6e1ab2af11",
      "sources": {
        "s1ea7669082c6": "https://github.com/duosecurity/duo_unix/blob/91e3c987f256afdb166b26be777cef6e1ab2af11/pam_duo/pam_duo.8#L44-L53"
      }
    },
    "auth0-docs": {
      "name": "Auth0 archived documentation",
      "basis": "5258d17ede3eea0ed0e330d15f8921a542564f68",
      "sources": {
        "sda6cf0f32c03": "https://github.com/auth0/docs/blob/5258d17ede3eea0ed0e330d15f8921a542564f68/articles/mfa/guides/enable-mfa.md#L12"
      }
    },
    "auth0-rolling": {
      "name": "Auth0 MFA documentation",
      "basis": "unknown",
      "sources": {
        "s22eb9266f40c": "https://auth0.com/docs/secure/multi-factor-authentication/enable-mfa"
      }
    },
    "cognito-api-source": {
      "name": "Amazon Cognito API source",
      "basis": "2ba0e39015ddf9c91c6c378f8a4fb79dcb4353da",
      "sources": {
        "s20a38c138333": "https://github.com/aws/aws-sdk-go-v2/blob/2ba0e39015ddf9c91c6c378f8a4fb79dcb4353da/service/cognitoidentityprovider/api_op_SetUserPoolMfaConfig.go#L67-L76"
      }
    },
    "clerk-docs": {
      "name": "Clerk documentation",
      "basis": "26ef3ace7508d46d6242c377e830a7791b0a2fdb",
      "sources": {
        "s965680da0841": "https://github.com/clerk/clerk-docs/blob/26ef3ace7508d46d6242c377e830a7791b0a2fdb/docs/guides/configure/auth-strategies/sign-up-sign-in-options.mdx#L168-L171"
      }
    },
    "supabase-docs": {
      "name": "Supabase documentation",
      "basis": "10c7379c970ae4d2f30f3158194061cf5ffb8fc5",
      "sources": {
        "sfae0cdf9b1b6": "https://github.com/supabase/supabase/blob/10c7379c970ae4d2f30f3158194061cf5ffb8fc5/apps/docs/content/guides/auth/auth-mfa.mdx#L94-L96",
        "s4fe1e36a064b": "https://github.com/supabase/supabase/blob/10c7379c970ae4d2f30f3158194061cf5ffb8fc5/apps/docs/content/guides/auth/auth-mfa.mdx#L192-L200"
      }
    },
    "cf-docs": {
      "name": "Cloudflare documentation",
      "basis": "c896795b8e8bab68d05ae78d64c9cbcda1fdb104",
      "sources": {
        "s9f8bead847d2": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/integrations/identity-providers/one-time-pin.mdx#L15",
        "s7e793d13cf31": "https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/access-settings/independent-mfa.mdx#L15-L24"
      }
    }
  },
  "claims": {
    "totp-secret": {"text": "Generate a random per-user TOTP secret; verification requires the recoverable secret rather than its hash.", "components": ["totp"], "sources": ["totp:s3190460e5d2d"], "status": "REASONED"},
    "totp-provisioning": {"text": "Provision the authenticator with an otpauth:// URI rendered as a QR code.", "components": ["uri"], "sources": ["uri:s4c73b28585c7"], "status": "REASONED"},
    "totp-storage": {"text": "Encrypt TOTP secrets at rest and exclude them from the repository.", "components": ["totp"], "sources": ["totp:s3190460e5d2d"], "status": "REASONED"},
    "totp-throttling": {"text": "Rate-limit code attempts; repeated wrong codes must hit a rate limit or lockout.", "components": ["hotp", "totp"], "sources": ["hotp:s05c8bf9b6329", "totp:s3190460e5d2d"], "status": "REASONED"},
    "totp-replay": {"text": "Reject an already accepted code within its time step; Verify submits the same valid code twice and expects refusal on reuse.", "components": ["totp"], "sources": ["totp:s3190460e5d2d"], "status": "REASONED"},
    "authelia-proxies": {"text": "Authelia integrates with nginx auth_request, Traefik forwardAuth, Caddy forward_auth from 2.5.1, HAProxy via Lua and Envoy; Apache and IIS are unsupported.", "components": ["authelia", "caddy-min"], "sources": ["authelia:s1409ac8fe3d9", "caddy-min:s1409ac8fe3d9"], "status": "REASONED"},
    "duo-free": {"text": "Duo Free covers up to 10 users with MFA and Duo Mobile as recorded in September 2026; verify current terms.", "components": ["duo"], "sources": ["duo:sb2b87daf72f0"], "status": "REASONED"},
    "webauthn-origin": {"text": "Prefer WebAuthn/passkeys and FIDO2 keys for phishing resistance: credentials are bound to the site origin.", "components": ["webauthn"], "sources": ["webauthn:sef2c27817118"], "status": "REASONED"},
    "webauthn-verification": {"text": "Store the credential public key and sign count; require and verify UV server-side when a passkey stands alone.", "components": ["webauthn"], "sources": ["webauthn:sef2c27817118"], "status": "REASONED"},
    "webauthn-counter": {"text": "Treat sign count as advisory, not a hard clone-block; many synced passkeys report zero.", "components": ["webauthn"], "sources": ["webauthn:sef2c27817118"], "status": "REASONED"},
    "verify-secret-storage": {"text": "Check that no TOTP secret appears in the repository or its history.", "components": ["totp"], "sources": ["totp:s3190460e5d2d"], "status": "REASONED"},
    "mfa-enforcement": {"text": "Give every exposed human-facing login a second factor where viable; prefer native or IdP-enforced MFA, then an identity layer whose own or upstream policy requires MFA, app-level TOTP, then a hosted MFA service. Enrollment alone is not enforcement. General TOTP source; no provider-policy reference in Sources.", "components": ["totp", "entra-docs", "auth0-docs", "auth0-rolling", "cognito-api-source", "clerk-docs", "supabase-docs"], "sources": ["totp:s3190460e5d2d", "entra-docs:s2c2f323edbd0", "auth0-docs:sda6cf0f32c03", "auth0-rolling:s22eb9266f40c", "cognito-api-source:s20a38c138333", "clerk-docs:s965680da0841", "supabase-docs:sfae0cdf9b1b6", "supabase-docs:s4fe1e36a064b"], "status": "REASONED"},
    "push-matching": {"text": "Prefer WebAuthn/passkeys over TOTP or push, and those over email or SMS codes. TOTP and push are not phishing-resistant; push must use number matching or verified push, never bare approve/deny, to resist prompt-bombing. WebAuthn and general Duo pricing sources; no pinned push-policy reference in Sources.", "components": ["webauthn", "duo", "entra-docs"], "sources": ["webauthn:sef2c27817118", "duo:sb2b87daf72f0", "entra-docs:sda22c238526b"], "status": "REASONED"},
    "totp-activation": {"text": "Verify one valid TOTP code before activating the factor. General TOTP source; no pinned implementation reference.", "components": ["totp", "otp-source"], "sources": ["totp:s3190460e5d2d", "otp-source:s7c4c6d57f705"], "status": "REASONED"},
    "recovery-codes": {"text": "Issue single-use recovery codes and store hashes rather than the code values; Verify checks both storage and refusal on reuse. General TOTP source; no recovery-code storage or lifecycle reference in Sources.", "components": ["totp", "nist", "owasp-docs"], "sources": ["totp:s3190460e5d2d", "nist:s4e1146860142", "owasp-docs:sa72b5658a19b"], "status": "REASONED"},
    "factor-changes": {"text": "Require re-verification of the existing factor before disabling or replacing it or minting new recovery codes, so a password-only or stolen session cannot remove MFA. General TOTP source; no factor-change policy reference in Sources.", "components": ["totp", "owasp-docs"], "sources": ["totp:s3190460e5d2d", "owasp-docs:s2940f630fb71"], "status": "REASONED"},
    "admin-factors": {"text": "Give administrators a phishing-resistant passkey or FIDO2 key wherever offered; TOTP is the floor and SMS is unacceptable for administrator accounts. General WebAuthn source; no administrator-policy reference in Sources.", "components": ["webauthn"], "sources": ["webauthn:sef2c27817118"], "status": "REASONED"},
    "authelia-factors": {"text": "The body lists TOTP, WebAuthn/passkeys and mobile push for Authelia. General proxy support matrix only; no pinned factor-support reference in Sources.", "components": ["authelia", "authelia-source"], "sources": ["authelia:s1409ac8fe3d9", "authelia-source:sfeb54a05c30d"], "status": "REASONED"},
    "identity-layer-factors": {"text": "The body lists authentik OIDC/SAML with TOTP and WebAuthn, Keycloak OIDC/SAML with built-in OTP enrollment, and oauth2-proxy with MFA inherited from its upstream provider's enforcement. General TOTP/WebAuthn standards only; Sources has no vendor references for these product capabilities.", "components": ["identity-layers"], "sources": ["identity-layers:s3190460e5d2d", "identity-layers:sef2c27817118"], "status": "REASONED"},
    "totp-libraries": {"text": "The body lists pyotp with qrcode and django-otp, Node otplib with qrcode, and pquerna/otp with QR generation as RFC 6238 implementation options. General TOTP source only; Sources has no library-specific references.", "components": ["totp", "pyotp-source", "python-qrcode-source", "django-otp-source", "otplib-source", "node-qrcode-source", "otp-source"], "sources": ["totp:s3190460e5d2d", "pyotp-source:sff126dae123b", "python-qrcode-source:s9481cd1c5c1c", "django-otp-source:s3b66277026d8", "otplib-source:s1cfb4a0cb98d", "node-qrcode-source:s427c06d742cf", "otp-source:s9dc96c06d6a0"], "status": "REASONED"},
    "ssh-pam-enforcement": {"text": "Make SSH PAM MFA mandatory with UsePAM yes, KbdInteractiveAuthentication yes and AuthenticationMethods publickey,keyboard-interactive:pam; :pam pins the second step to PAM and the public-key-first sequence still runs it for key-based login. General TOTP standard only; Sources has no sshd or PAM vendor reference.", "components": ["ssh-pam", "openssh-source"], "sources": ["ssh-pam:s3190460e5d2d", "openssh-source:sf299a4e3603a", "openssh-source:s862f0df9ce84"], "status": "REASONED"},
    "ssh-nullok": {"text": "Remove nullok after rollout so unenrolled users are denied; the body identifies google-authenticator-libpam as per-user TOTP for SSH and console login with terminal QR enrollment. General TOTP standard only; Sources has no PAM-module vendor reference.", "components": ["ssh-pam"], "sources": ["ssh-pam:s3190460e5d2d"], "status": "REASONED"},
    "duo-unix-failmode": {"text": "Duo Unix pam_duo adds SSH push MFA; set failmode=secure for mandatory MFA because default safe grants access when Duo is unreachable, and keep a separately controlled emergency path. General Duo pricing source; Sources has no Duo Unix configuration reference.", "components": ["duo", "duo-unix-source"], "sources": ["duo:sb2b87daf72f0", "duo-unix-source:s1ea7669082c6"], "status": "REASONED"},
    "supabase-assurance": {"text": "Supabase admits an aal1 session unless app and database policies require aal2; enrollment or enabling a factor is not enforcement, so inspect and test the effective policy. General TOTP standard only; Sources has no Supabase vendor reference.", "components": ["supabase", "supabase-docs"], "sources": ["supabase:s3190460e5d2d", "supabase-docs:sfae0cdf9b1b6", "supabase-docs:s4fe1e36a064b"], "status": "REASONED"},
    "duo-proxy": {"text": "Duo Authentication Proxy speaks RADIUS and LDAP to retrofit MFA onto VPNs and services with RADIUS support. General Duo pricing source; Sources has no Authentication Proxy reference.", "components": ["duo"], "sources": ["duo:sb2b87daf72f0"], "status": "REASONED"},
    "access-mfa": {"text": "An Access emailed one-time PIN proves mailbox control only; require MFA at the connected IdP for this login or Access independent MFA with TOTP or a WebAuthn key. General TOTP/WebAuthn standards only; Sources has no Cloudflare vendor reference.", "components": ["access", "cf-docs"], "sources": ["access:s3190460e5d2d", "access:sef2c27817118", "cf-docs:s9f8bead847d2", "cf-docs:s7e793d13cf31"], "status": "REASONED"},
    "webauthn-library": {"text": "Use a maintained WebAuthn library rather than hand-parsing attestation. General WebAuthn standard; no library-specific reference in Sources.", "components": ["webauthn"], "sources": ["webauthn:sef2c27817118"], "status": "REASONED"},
    "webauthn-recovery": {"text": "Keep a second key or single-use recovery codes to avoid lost-key lockout; for administrators on phishing-resistant keys, prefer a second hardware key because printed codes are phishable, and rate-limit and alert on recovery-code use. General WebAuthn source; no recovery-policy reference in Sources.", "components": ["webauthn", "nist", "owasp-docs"], "sources": ["webauthn:sef2c27817118", "nist:s4e1146860142", "owasp-docs:sa72b5658a19b"], "status": "REASONED"},
    "mysql-factors": {"text": "The body states that MySQL 8 supports up to three factors for interactive human login and its server-side WebAuthn plugin requires Enterprise Edition. General WebAuthn standard only; Sources has no MySQL vendor reference supporting the version, factor count or edition requirement.", "components": ["mysql"], "sources": ["mysql:sef2c27817118"], "status": "REASONED"},
    "unattended-mtls": {"text": "Unattended database and model-server API connections have no interactive second-factor dialogue; use mutual TLS client certificates as the service's possession factor and MFA on human paths through SSH, bastions and admin panels. General MFA standards only; Sources has no mTLS deployment reference.", "components": ["totp", "webauthn"], "sources": ["totp:s3190460e5d2d", "webauthn:sef2c27817118"], "status": "REASONED"},
    "verify-mfa-operation": {"text": "After enrollment and enforcement, a password-only attempt at an MFA-protected operation must fail and completing the second factor must allow it. Opening an aal1 session alone is not a failure when enforcement occurs at the operation. General TOTP source; no provider or app-policy reference in Sources.", "components": ["totp", "supabase-docs"], "sources": ["totp:s3190460e5d2d", "supabase-docs:sfae0cdf9b1b6", "supabase-docs:s4fe1e36a064b"], "status": "REASONED"},
    "verify-recovery-history": {"text": "Verify that no recovery code appears in the repository or its history. General TOTP source; no recovery-code scanning reference in Sources.", "components": ["totp"], "sources": ["totp:s3190460e5d2d"], "status": "REASONED"},
    "verify-offboarding": {"text": "Verify that a departed user's second factor, active sessions and app-level access are revoked; changing only the password is insufficient. General TOTP source; no offboarding or session-revocation reference in Sources.", "components": ["totp", "entra-docs", "owasp-docs"], "sources": ["totp:s3190460e5d2d", "entra-docs:s1341b9dbdad1", "owasp-docs:se60f5c9f1c55"], "status": "REASONED"}
  }
}
---
# Multi-factor authentication (MFA)

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-10-05; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| totp-secret: Generate a random per-user TOTP secret; verification requires the recoverable secret rather than its hash. | TOTP standard unknown | REASONED |
| totp-provisioning: Provision the authenticator with an otpauth:// URI rendered as a QR code. | Authenticator key URI format unknown | REASONED |
| totp-storage: Encrypt TOTP secrets at rest and exclude them from the repository. | TOTP standard unknown | REASONED |
| totp-throttling: Rate-limit code attempts; repeated wrong codes must hit a rate limit or lockout. | HOTP standard unknown; TOTP standard unknown | REASONED |
| totp-replay: Reject an already accepted code within its time step; Verify submits the same valid code twice and expects refusal on reuse. | TOTP standard unknown | REASONED |
| authelia-proxies: Authelia integrates with nginx auth_request, Traefik forwardAuth, Caddy forward_auth from 2.5.1, HAProxy via Lua and Envoy; Apache and IIS are unsupported. | Authelia proxy support unknown; Caddy forward_auth minimum 2.5.1 | REASONED |
| duo-free: Duo Free covers up to 10 users with MFA and Duo Mobile as recorded in September 2026; verify current terms. | Duo editions unknown | REASONED |
| webauthn-origin: Prefer WebAuthn/passkeys and FIDO2 keys for phishing resistance: credentials are bound to the site origin. | WebAuthn standard unknown | REASONED |
| webauthn-verification: Store the credential public key and sign count; require and verify UV server-side when a passkey stands alone. | WebAuthn standard unknown | REASONED |
| webauthn-counter: Treat sign count as advisory, not a hard clone-block; many synced passkeys report zero. | WebAuthn standard unknown | REASONED |
| verify-secret-storage: Check that no TOTP secret appears in the repository or its history. | TOTP standard unknown | REASONED |
| mfa-enforcement: Give every exposed human-facing login a second factor where viable; prefer native or IdP-enforced MFA, then an identity layer whose own or upstream policy requires MFA, app-level TOTP, then a hosted MFA service. Enrollment alone is not enforcement. General TOTP source; no provider-policy reference in Sources. | TOTP standard unknown; Microsoft Entra documentation 231747abc59ae3d50c74e215c1cdd592eb980723; Auth0 archived documentation 5258d17ede3eea0ed0e330d15f8921a542564f68; Auth0 MFA documentation unknown; Amazon Cognito API source 2ba0e39015ddf9c91c6c378f8a4fb79dcb4353da; Clerk documentation 26ef3ace7508d46d6242c377e830a7791b0a2fdb; Supabase documentation 10c7379c970ae4d2f30f3158194061cf5ffb8fc5 | REASONED |
| push-matching: Prefer WebAuthn/passkeys over TOTP or push, and those over email or SMS codes. TOTP and push are not phishing-resistant; push must use number matching or verified push, never bare approve/deny, to resist prompt-bombing. WebAuthn and general Duo pricing sources; no pinned push-policy reference in Sources. | WebAuthn standard unknown; Duo editions unknown; Microsoft Entra documentation 231747abc59ae3d50c74e215c1cdd592eb980723 | REASONED |
| totp-activation: Verify one valid TOTP code before activating the factor. General TOTP source; no pinned implementation reference. | TOTP standard unknown; pquerna/otp source 617f8d5f3f518bae0f5c3ec14a17ca19f2a6f870 | REASONED |
| recovery-codes: Issue single-use recovery codes and store hashes rather than the code values; Verify checks both storage and refusal on reuse. General TOTP source; no recovery-code storage or lifecycle reference in Sources. | TOTP standard unknown; NIST digital identity guidelines SP 800-63B-4; OWASP cheat sheets 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
| factor-changes: Require re-verification of the existing factor before disabling or replacing it or minting new recovery codes, so a password-only or stolen session cannot remove MFA. General TOTP source; no factor-change policy reference in Sources. | TOTP standard unknown; OWASP cheat sheets 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
| admin-factors: Give administrators a phishing-resistant passkey or FIDO2 key wherever offered; TOTP is the floor and SMS is unacceptable for administrator accounts. General WebAuthn source; no administrator-policy reference in Sources. | WebAuthn standard unknown | REASONED |
| authelia-factors: The body lists TOTP, WebAuthn/passkeys and mobile push for Authelia. General proxy support matrix only; no pinned factor-support reference in Sources. | Authelia proxy support unknown; Authelia source v4.39.28 | REASONED |
| identity-layer-factors: The body lists authentik OIDC/SAML with TOTP and WebAuthn, Keycloak OIDC/SAML with built-in OTP enrollment, and oauth2-proxy with MFA inherited from its upstream provider's enforcement. General TOTP/WebAuthn standards only; Sources has no vendor references for these product capabilities. | authentik, Keycloak and oauth2-proxy MFA (citation gap) unknown | REASONED |
| totp-libraries: The body lists pyotp with qrcode and django-otp, Node otplib with qrcode, and pquerna/otp with QR generation as RFC 6238 implementation options. General TOTP source only; Sources has no library-specific references. | TOTP standard unknown; PyOTP source cc156832fa9f3d5af7fb9e4e6b86b29dfc5b69f1; Python qrcode source f92c007498d796e4825638b7d50c14ea51e5457a; django-otp source 88cf4970423b11f29d6840311f53378d007a3d63; otplib source c5c11be2a50fd864b587854bff6d97c5f8aa9c84; Node qrcode source 3848ed2c17de5bcdead487417dbf14c5dd017f8d; pquerna/otp source 617f8d5f3f518bae0f5c3ec14a17ca19f2a6f870 | REASONED |
| ssh-pam-enforcement: Make SSH PAM MFA mandatory with UsePAM yes, KbdInteractiveAuthentication yes and AuthenticationMethods publickey,keyboard-interactive:pam; :pam pins the second step to PAM and the public-key-first sequence still runs it for key-based login. General TOTP standard only; Sources has no sshd or PAM vendor reference. | SSH and PAM MFA (citation gap) unknown; OpenSSH portable source V_9_9_P2 | REASONED |
| ssh-nullok: Remove nullok after rollout so unenrolled users are denied; the body identifies google-authenticator-libpam as per-user TOTP for SSH and console login with terminal QR enrollment. General TOTP standard only; Sources has no PAM-module vendor reference. | SSH and PAM MFA (citation gap) unknown | REASONED |
| duo-unix-failmode: Duo Unix pam_duo adds SSH push MFA; set failmode=secure for mandatory MFA because default safe grants access when Duo is unreachable, and keep a separately controlled emergency path. General Duo pricing source; Sources has no Duo Unix configuration reference. | Duo editions unknown; Duo Unix source 91e3c987f256afdb166b26be777cef6e1ab2af11 | REASONED |
| supabase-assurance: Supabase admits an aal1 session unless app and database policies require aal2; enrollment or enabling a factor is not enforcement, so inspect and test the effective policy. General TOTP standard only; Sources has no Supabase vendor reference. | Supabase Auth MFA (citation gap) unknown; Supabase documentation 10c7379c970ae4d2f30f3158194061cf5ffb8fc5 | REASONED |
| duo-proxy: Duo Authentication Proxy speaks RADIUS and LDAP to retrofit MFA onto VPNs and services with RADIUS support. General Duo pricing source; Sources has no Authentication Proxy reference. | Duo editions unknown | REASONED |
| access-mfa: An Access emailed one-time PIN proves mailbox control only; require MFA at the connected IdP for this login or Access independent MFA with TOTP or a WebAuthn key. General TOTP/WebAuthn standards only; Sources has no Cloudflare vendor reference. | Cloudflare Access MFA (citation gap) unknown; Cloudflare documentation c896795b8e8bab68d05ae78d64c9cbcda1fdb104 | REASONED |
| webauthn-library: Use a maintained WebAuthn library rather than hand-parsing attestation. General WebAuthn standard; no library-specific reference in Sources. | WebAuthn standard unknown | REASONED |
| webauthn-recovery: Keep a second key or single-use recovery codes to avoid lost-key lockout; for administrators on phishing-resistant keys, prefer a second hardware key because printed codes are phishable, and rate-limit and alert on recovery-code use. General WebAuthn source; no recovery-policy reference in Sources. | WebAuthn standard unknown; NIST digital identity guidelines SP 800-63B-4; OWASP cheat sheets 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
| mysql-factors: The body states that MySQL 8 supports up to three factors for interactive human login and its server-side WebAuthn plugin requires Enterprise Edition. General WebAuthn standard only; Sources has no MySQL vendor reference supporting the version, factor count or edition requirement. | MySQL interactive MFA (citation gap) unknown | REASONED |
| unattended-mtls: Unattended database and model-server API connections have no interactive second-factor dialogue; use mutual TLS client certificates as the service's possession factor and MFA on human paths through SSH, bastions and admin panels. General MFA standards only; Sources has no mTLS deployment reference. | TOTP standard unknown; WebAuthn standard unknown | REASONED |
| verify-mfa-operation: After enrollment and enforcement, a password-only attempt at an MFA-protected operation must fail and completing the second factor must allow it. Opening an aal1 session alone is not a failure when enforcement occurs at the operation. General TOTP source; no provider or app-policy reference in Sources. | TOTP standard unknown; Supabase documentation 10c7379c970ae4d2f30f3158194061cf5ffb8fc5 | REASONED |
| verify-recovery-history: Verify that no recovery code appears in the repository or its history. General TOTP source; no recovery-code scanning reference in Sources. | TOTP standard unknown | REASONED |
| verify-offboarding: Verify that a departed user's second factor, active sessions and app-level access are revoked; changing only the password is insufficient. General TOTP source; no offboarding or session-revocation reference in Sources. | TOTP standard unknown; Microsoft Entra documentation 231747abc59ae3d50c74e215c1cdd592eb980723; OWASP cheat sheets 668ba7db3d0da5868b8a0305c259f7f6914a6ecd | REASONED |
<!-- version-basis:end -->

Passwords fail through phishing, reuse, and credential stuffing; a second factor keeps a stolen password from becoming access. This guide names the options and the references; it deliberately stops short of per-product walkthroughs, because an AI assistant that knows which option fits can implement it from the linked project documentation. The per-tool guides in this repository state what is viable for each stack.

## What to do (AI assistants)

1. Give every human-facing login on an exposed service a second factor where viable.
2. Prefer, in this order:
   1. Platform-native MFA, or OIDC/SSO login with MFA enforced at the identity provider.
   2. An identity-aware layer in front of the app (Cloudflare Access, or a self-hosted portal below), which adds MFA without changing the app, but only when the layer's own policy, or the identity provider it delegates to, requires a second factor.
   3. App-level TOTP through a library (below).
   4. A hosted MFA service such as Duo.
3. Prefer phishing-resistant factors (WebAuthn/passkeys) over TOTP and push, and any of those over emailed or SMS codes. Neither TOTP nor push is phishing-resistant, and a bare approve/deny push also invites prompt-bombing (MFA fatigue), so a push factor must use number matching or verified push, never a single tap.
4. When implementing TOTP yourself, the required pieces are: a random per-user secret; an `otpauth://` provisioning URI rendered as a QR code for the user's authenticator app; verification of 1 valid code before the factor activates; single-use recovery codes (stored hashed); rate limiting on code attempts; rejection of a code that has already been accepted for its time step (RFC 6238 forbids accepting a code twice); and TOTP secrets encrypted at rest and excluded from the repository (they cannot be hashed, since the server must read them to verify codes). Require the existing factor to be re-verified before a user disables it, replaces it, or mints new recovery codes, so a password-only or stolen session cannot remove MFA.
5. Give administrators a phishing-resistant factor (a passkey or a FIDO2 hardware key) wherever the platform offers one. TOTP is the floor; SMS is not acceptable for administrator accounts.
6. Enrolment is not enforcement. After users enrol, require the factor at the point of access (provider policy such as Conditional Access, Supabase `aal2` in policies, or the app's own check) and test that a password-only session is refused.

## Identity layers and auth proxies (open source)

- **Authelia**: authentication portal that sits in front of a reverse proxy; per its support matrix it integrates with nginx (`auth_request`), Traefik (`forwardAuth`), Caddy (`forward_auth`, 2.5.1 and later), HAProxy (through a Lua module), and Envoy, while Apache and IIS are documented as unsupported. Second factors: TOTP, WebAuthn/passkeys, and mobile push. https://www.authelia.com/
- **authentik**: self-hosted identity provider (OIDC and SAML) with TOTP and WebAuthn factors; apps behind it inherit its MFA. https://goauthentik.io/
- **Keycloak**: full OIDC/SAML identity provider with built-in OTP enrolment; the standard choice when you also need user federation and roles. https://www.keycloak.org/
- **oauth2-proxy**: puts any upstream behind an OIDC/OAuth2 provider; MFA is whatever that provider enforces. https://github.com/oauth2-proxy/oauth2-proxy

## App-level TOTP libraries

Each generates and verifies RFC 6238 codes and pairs with a QR library so users can enrol any authenticator app (Google Authenticator, Microsoft Authenticator, Aegis, FreeOTP, and password managers with TOTP support).

- Python: [pyotp](https://github.com/pyauth/pyotp) with [qrcode](https://pypi.org/project/qrcode/); [django-otp](https://pypi.org/project/django-otp/) integrates this into Django.
- Node.js: [otplib](https://github.com/yeojz/otplib) with [qrcode](https://www.npmjs.com/package/qrcode).
- Go: [pquerna/otp](https://github.com/pquerna/otp), which includes QR image generation.

## SSH and host logins

- [google-authenticator-libpam](https://github.com/google/google-authenticator-libpam): PAM module adding per-user TOTP to SSH and console logins, with QR enrolment in the terminal (`libpam-google-authenticator` package on Debian/Ubuntu).
- Duo Unix (`pam_duo`) adds push-approval MFA to SSH: https://duo.com/docs/duounix
- Make the PAM factor mandatory, or it is not enforced: with `UsePAM yes` and `KbdInteractiveAuthentication yes`, set `AuthenticationMethods publickey,keyboard-interactive:pam` in sshd (the `:pam` device pins the second step to the PAM stack, since a bare `keyboard-interactive` can route to another backend, and requiring the public key first means a key-based login still runs it), drop `nullok` once rollout is done so an un-enrolled user is denied rather than waved through, and set Duo's `failmode=secure` (its default `safe` grants access when Duo is unreachable) with a separately controlled emergency path.

## Hosted MFA

- **Hosted identity providers** (Microsoft Entra ID, Google Workspace, Auth0, Amazon Cognito, Clerk, Supabase Auth, and others) can enforce MFA for the apps that sign in through them, but the enforcement lives in a layer that varies by provider: a tenant or Conditional-Access policy, a per-user requirement, or authorization in your own app and database (Supabase, for example, still admits an `aal1` session unless your policies require `aal2`). Enrolment, or merely enabling a factor, does not enforce it; inspect and test the effective policy. Which tiers include MFA, and which do not, is in [identity-providers.md](identity-providers.md); wiring is in [oidc-integration.md](oidc-integration.md).
- **Duo**: the Duo Free edition covers up to 10 users with MFA and the Duo Mobile authenticator app (per https://duo.com/editions-and-pricing as of September 2026; verify current terms). Its Authentication Proxy speaks RADIUS and LDAP, which retrofits MFA onto VPNs and onto services with RADIUS support.
- **Cloudflare Access** ([cloudflare.md](cloudflare.md)): the emailed one-time PIN proves control of a mailbox only. Either enforce MFA at a connected identity provider (Access inherits it only when that provider's policy requires it for the login), or use Access's own independent MFA to require a second factor (a TOTP authenticator or a WebAuthn key) without relying on the IdP.

Enforcing MFA once at a central identity provider is easier to operate and audit than separate factors per app; prefer it when more than 1 service is involved.

## Passkeys and hardware keys

WebAuthn passkeys and FIDO2 hardware keys (YubiKey and similar) resist phishing because the credential is bound to the site's origin; a look-alike domain gets nothing. Every hosted provider in [identity-providers.md](identity-providers.md) offers them at some tier. When implementing them yourself, use a maintained WebAuthn library rather than parsing attestation by hand, store the credential public key and sign count, and require and verify the user-verification (UV) flag server-side where a passkey stands alone, or the ceremony proves possession only, not a second factor. Treat the sign count as advisory (many synced passkeys always report 0), not a hard clone-block. Keep a recovery path (a second key or single-use recovery codes) so a lost key is not a lockout, but note that for an admin on a phishing-resistant key the printed codes become the weakest, phishable link: prefer a second hardware key, and rate-limit and alert on recovery-code use.

## Where direct MFA is not viable

Unattended machine connections (service-to-service database and model-server APIs) have no interactive second-factor dialogue, though some databases do offer native MFA for an interactive human login (MySQL 8 supports up to three factors; its server-side WebAuthn plugin requires Enterprise Edition). For the unattended connections the pattern is: mutual TLS client certificates as the possession factor for the service itself, and MFA on every human path that reaches the host (SSH, bastions, admin panels). The database guides in this repository apply this pattern.

## Verify

- With only the password, attempt an MFA-protected operation, not just a login: once the factor is enrolled AND enforcement is on (provider policy, Supabase `aal2`, or the app's own check, per rule 6) the operation is refused, and completing the second factor then allows it. Some layers still open a password-only (`aal1`) session and enforce at the operation, so a session opening is not itself a failure; a protected operation that succeeds without a second factor is, and the user is not protected.
- Recovery codes are single-use, and their hashes rather than their values are stored.
- Repeated wrong codes hit a rate limit or lockout.
- Submitting the same valid TOTP code a second time within its time step is refused.
- No TOTP secret or recovery code appears in the repository or its history.
- A departed user's second factor, active sessions, and app-level access are revoked, not only their password changed. Enforcing MFA is not the end; offboarding belongs in the access lifecycle too, and [deployment-lifecycle.md](deployment-lifecycle.md) has the checklist.

## Standards and sources (checked September 2026)

- TOTP: https://www.rfc-editor.org/info/rfc6238/ ; HOTP: https://www.rfc-editor.org/info/rfc4226/
- `otpauth://` key URI format: https://github.com/google/google-authenticator/wiki/Key-Uri-Format
- WebAuthn: https://www.w3.org/TR/webauthn-2/
- Authelia proxy support matrix (Caddy 2.5.1 and later): https://www.authelia.com/integration/proxies/support/
- Duo editions and pricing: https://duo.com/editions-and-pricing
- Microsoft Entra documentation `231747abc59ae3d50c74e215c1cdd592eb980723`, application session revocation (checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/users/users-revoke-access.md#L58-L62
- OWASP cheat sheets `668ba7db3d0da5868b8a0305c259f7f6914a6ecd`, revocation of unneeded or compromised secrets (checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Secrets_Management_Cheat_Sheet.md#L218
- pquerna/otp source `617f8d5f3f518bae0f5c3ec14a17ca19f2a6f870`, TOTP enrollment validation (checked October 2026): https://github.com/pquerna/otp/blob/617f8d5f3f518bae0f5c3ec14a17ca19f2a6f870/README.md#L27-L30
- OWASP cheat sheets `668ba7db3d0da5868b8a0305c259f7f6914a6ecd`, reauthentication before factor changes (checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Multifactor_Authentication_Cheat_Sheet.md#L154-L155
- NIST digital identity guidelines `SP 800-63B-4`, single-use look-up secrets and hashed storage (checked October 2026): https://pages.nist.gov/800-63-4/sp800-63b/authenticators/#look-up-secrets
- OWASP cheat sheets `668ba7db3d0da5868b8a0305c259f7f6914a6ecd`, recovery codes and alternate factors (checked October 2026): https://github.com/OWASP/CheatSheetSeries/blob/668ba7db3d0da5868b8a0305c259f7f6914a6ecd/cheatsheets/Multifactor_Authentication_Cheat_Sheet.md#L142-L143
- Authelia source `v4.39.28`, TOTP, WebAuthn security keys and Duo push factors (checked October 2026): https://github.com/authelia/authelia/blob/v4.39.28/docs/content/configuration/second-factor/introduction.md#L21-L31
- PyOTP source `cc156832fa9f3d5af7fb9e4e6b86b29dfc5b69f1`, OTP generation, verification and RFC 6238 support (checked October 2026): https://github.com/pyauth/pyotp/blob/cc156832fa9f3d5af7fb9e4e6b86b29dfc5b69f1/README.rst#L4-L9
- Python qrcode source `f92c007498d796e4825638b7d50c14ea51e5457a`, QR code generation (checked October 2026): https://github.com/lincolnloop/python-qrcode/blob/f92c007498d796e4825638b7d50c14ea51e5457a/README.rst#L5-L8
- django-otp source `88cf4970423b11f29d6840311f53378d007a3d63`, Django integration and HOTP/TOTP implementations (checked October 2026): https://github.com/django-otp/django-otp/blob/88cf4970423b11f29d6840311f53378d007a3d63/README.rst#L16-L28
- otplib source `c5c11be2a50fd864b587854bff6d97c5f8aa9c84`, HOTP/TOTP and Node support (checked October 2026): https://github.com/yeojz/otplib/blob/c5c11be2a50fd864b587854bff6d97c5f8aa9c84/README.md#L13
- Node qrcode source `3848ed2c17de5bcdead487417dbf14c5dd017f8d`, QR code generation (checked October 2026): https://github.com/soldair/node-qrcode/blob/3848ed2c17de5bcdead487417dbf14c5dd017f8d/README.md#L2
- pquerna/otp source `617f8d5f3f518bae0f5c3ec14a17ca19f2a6f870`, TOTP/HOTP generation, validation and QR images (checked October 2026): https://github.com/pquerna/otp/blob/617f8d5f3f518bae0f5c3ec14a17ca19f2a6f870/README.md#L15-L18
- OpenSSH portable source `V_9_9_P2`, ordered authentication methods and the PAM device (checked October 2026): https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sshd_config.5#L197-L211
- OpenSSH portable source `V_9_9_P2`, UsePAM and keyboard-interactive authentication (checked October 2026): https://github.com/openssh/openssh-portable/blob/V_9_9_P2/sshd_config.5#L2017-L2026
- Duo Unix source `91e3c987f256afdb166b26be777cef6e1ab2af11`, pam_duo failmode and push approval (checked October 2026): https://github.com/duosecurity/duo_unix/blob/91e3c987f256afdb166b26be777cef6e1ab2af11/pam_duo/pam_duo.8#L44-L53
- Microsoft Entra documentation `231747abc59ae3d50c74e215c1cdd592eb980723`, Conditional Access MFA authentication-strength requirement (checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/conditional-access/policy-all-users-mfa-strength.md#L56-L57
- Microsoft Entra documentation `231747abc59ae3d50c74e215c1cdd592eb980723`, Authenticator push number matching (checked October 2026): https://github.com/MicrosoftDocs/entra-docs/blob/231747abc59ae3d50c74e215c1cdd592eb980723/docs/identity/authentication/how-to-mfa-number-match.md#L12
- Auth0 archived documentation `5258d17ede3eea0ed0e330d15f8921a542564f68`, factor enablement and separate MFA enforcement choice (checked October 2026): https://github.com/auth0/docs/blob/5258d17ede3eea0ed0e330d15f8921a542564f68/articles/mfa/guides/enable-mfa.md#L12
- Auth0 MFA documentation, current factor and enforcement policy documentation (rolling documentation, checked October 2026): https://auth0.com/docs/secure/multi-factor-authentication/enable-mfa
- Amazon Cognito API source `2ba0e39015ddf9c91c6c378f8a4fb79dcb4353da`, required versus optional MFA (checked October 2026): https://github.com/aws/aws-sdk-go-v2/blob/2ba0e39015ddf9c91c6c378f8a4fb79dcb4353da/service/cognitoidentityprovider/api_op_SetUserPoolMfaConfig.go#L67-L76
- Clerk documentation `26ef3ace7508d46d6242c377e830a7791b0a2fdb`, application-wide versus user-selected MFA (checked October 2026): https://github.com/clerk/clerk-docs/blob/26ef3ace7508d46d6242c377e830a7791b0a2fdb/docs/guides/configure/auth-strategies/sign-up-sign-in-options.mdx#L168-L171
- Supabase documentation `10c7379c970ae4d2f30f3158194061cf5ffb8fc5`, server-side MFA enforcement beyond enrollment UI (checked October 2026): https://github.com/supabase/supabase/blob/10c7379c970ae4d2f30f3158194061cf5ffb8fc5/apps/docs/content/guides/auth/auth-mfa.mdx#L94-L96
- Supabase documentation `10c7379c970ae4d2f30f3158194061cf5ffb8fc5`, restrictive RLS requiring aal2 (checked October 2026): https://github.com/supabase/supabase/blob/10c7379c970ae4d2f30f3158194061cf5ffb8fc5/apps/docs/content/guides/auth/auth-mfa.mdx#L192-L200
- Cloudflare documentation `c896795b8e8bab68d05ae78d64c9cbcda1fdb104`, email one-time PIN login (checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/integrations/identity-providers/one-time-pin.mdx#L15
- Cloudflare documentation `c896795b8e8bab68d05ae78d64c9cbcda1fdb104`, independent MFA with TOTP and WebAuthn security keys (checked October 2026): https://github.com/cloudflare/cloudflare-docs/blob/c896795b8e8bab68d05ae78d64c9cbcda1fdb104/src/content/docs/cloudflare-one/access-controls/access-settings/independent-mfa.mdx#L15-L24
