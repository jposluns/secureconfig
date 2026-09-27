---
version_basis: {
  "schema": 1,
  "checked": "2026-09-26",
  "documentation_checked": "2026-09",
  "body_sha256": "7818b12bbc9a7750cc8a6c7f2a4656b60c99881a6bf4cc543f7633ca9c8a6985",
  "components": {
    "nginx": {
      "name": "nginx documentation",
      "basis": "unknown",
      "sources": {
        "s0e5162d1ce2b": "https://nginx.org/en/docs/http/ngx_http_access_module.html",
        "sbd17bad53c9d": "https://nginx.org/en/docs/http/ngx_http_autoindex_module.html",
        "s40bdf1af1596": "https://nginx.org/en/docs/http/ngx_http_core_module.html"
      }
    },
    "apache": {
      "name": "Apache documentation",
      "basis": "2.4",
      "sources": {
        "s24f06763d14a": "https://httpd.apache.org/docs/2.4/mod/core.html#directorymatch",
        "se24e9bbc0443": "https://httpd.apache.org/docs/2.4/mod/core.html#filesmatch",
        "s97468bf1f299": "https://httpd.apache.org/docs/2.4/mod/core.html#options",
        "s7313b1b624d5": "https://httpd.apache.org/docs/2.4/mod/mod_authz_core.html",
        "sef5ff46eddf7": "https://httpd.apache.org/docs/2.4/mod/mod_autoindex.html"
      }
    },
    "caddy": {
      "name": "Caddy documentation",
      "basis": "unknown",
      "sources": {
        "se9ab71afc4ba": "https://caddyserver.com/docs/caddyfile/directives/respond",
        "s38b1b78ce980": "https://caddyserver.com/docs/caddyfile/matchers"
      }
    },
    "next": {
      "name": "Next.js documentation",
      "basis": "unknown",
      "sources": {
        "sb98bee5b61c8": "https://nextjs.org/docs/pages/guides/environment-variables"
      }
    },
    "vite": {
      "name": "Vite documentation",
      "basis": "unknown",
      "sources": {
        "s3fc0892e0f58": "https://vite.dev/guide/env-and-mode"
      }
    },
    "cra": {
      "name": "Create React App documentation",
      "basis": "unknown",
      "sources": {
        "scfb24624addd": "https://create-react-app.dev/docs/adding-custom-environment-variables/"
      }
    }
  },
  "claims": {
    "nginx-dotfiles": {"text": "Deny dot-prefixed paths by regex; ACME longest-prefix ^~ location skips regex matching.", "components": ["nginx"], "sources": ["nginx:s0e5162d1ce2b", "nginx:s40bdf1af1596"], "status": "REASONED"},
    "nginx-backups": {"text": "Dotfile regex misses dump.sql/backup.tar.gz; keep exports outside root or add explicit sql/dump/bak/tar.gz deny.", "components": ["nginx"], "sources": ["nginx:s0e5162d1ce2b", "nginx:s40bdf1af1596"], "status": "REASONED"},
    "apache-directories": {"text": "DirectoryMatch denies dot-prefixed filesystem segments; exact well-known exemption permits the whole directory, not well-known-backup lookalikes.", "components": ["apache"], "sources": ["apache:s24f06763d14a", "apache:s7313b1b624d5"], "status": "REASONED"},
    "apache-files": {"text": "FilesMatch uses basenames, not enough for .git/config; retain for top-level dotfiles and sql/dump/bak files.", "components": ["apache"], "sources": ["apache:se24e9bbc0443", "apache:s7313b1b624d5"], "status": "REASONED"},
    "apache-listing": {"text": "Guide records Debian/Ubuntu Indexes FollowSymLinks and DirectoryIndex defaults without a packaging citation; index-less directories can expose other filenames.", "components": ["apache"], "sources": ["apache:s97468bf1f299", "apache:sef5ff46eddf7"], "status": "REASONED"},
    "apache-forbidden": {"text": "mod_autoindex hides 403 subrequests unless ShowForbidden is enabled; denies do not protect unrelated archives/CSV exports.", "components": ["apache"], "sources": ["apache:sef5ff46eddf7"], "status": "REASONED"},
    "apache-options": {"text": "Options -Indexes removes listing, preserving inherited options; Apache 2.4 rejects mixing relative +/- and bare options.", "components": ["apache"], "sources": ["apache:s97468bf1f299"], "status": "REASONED"},
    "nginx-listing": {"text": "nginx autoindex defaults off.", "components": ["nginx"], "sources": ["nginx:sbd17bad53c9d"], "status": "REASONED"},
    "caddy-listing": {"text": "Guide says Caddy lists only with file_server browse; Sources omit a file_server reference.", "components": ["caddy"], "sources": ["caddy:se9ab71afc4ba", "caddy:s38b1b78ce980"], "status": "REASONED"},
    "caddy-deny": {"text": "Caddy rules return 404 only for /.git/*, /.env and /.env.*; extend coverage or keep other sensitive files outside the served tree.", "components": ["caddy"], "sources": ["caddy:se9ab71afc4ba", "caddy:s38b1b78ce980"], "status": "REASONED"},
    "caddy-acme": {"text": "Broader Caddy denies must exempt legitimate .well-known paths; independent ACME handling lacks a direct Sources citation.", "components": ["caddy"], "sources": ["caddy:se9ab71afc4ba", "caddy:s38b1b78ce980"], "status": "REASONED"},
    "backup-storage": {"text": "Keep SQL dumps/backups outside document roots or in object storage; filename denies are only a backstop.", "components": ["nginx", "apache", "caddy"], "sources": ["nginx:s40bdf1af1596", "apache:s24f06763d14a", "caddy:s38b1b78ce980"], "status": "REASONED"},
    "next-public": {"text": "NEXT_PUBLIC_ embeds values in browser JavaScript; keep provider keys server-side behind backend routes.", "components": ["next"], "sources": ["next:sb98bee5b61c8"], "status": "REASONED"},
    "vite-public": {"text": "VITE_ embeds values in browser JavaScript; reserve for public values.", "components": ["vite"], "sources": ["vite:s3fc0892e0f58"], "status": "REASONED"},
    "cra-public": {"text": "Deprecated Create React App embeds REACT_APP_ values in browser builds.", "components": ["cra"], "sources": ["cra:scfb24624addd"], "status": "REASONED"},
    "source-maps": {"text": "Guide warns against external/inline maps for private code; removing sourceMappingURL does not unpublish deployed maps. Sources omit a direct map reference.", "components": ["next", "vite"], "sources": ["next:sb98bee5b61c8", "vite:s3fc0892e0f58"], "status": "REASONED"},
    "verify-dotfiles": {"text": "Plant a real readable dotfile exclusively; expect 403/404 without planted content. Missing plants are inconclusive, other paths need real files; remove only created probes.", "components": ["nginx", "apache", "caddy"], "sources": ["nginx:s0e5162d1ce2b", "apache:s7313b1b624d5", "caddy:se9ab71afc4ba"], "status": "REASONED", "verify": [1]},
    "verify-listing": {"text": "Existing nonempty index-less uploads must not produce 200 autoindex; absent/unwritable directories are inconclusive.", "components": ["apache"], "sources": ["apache:s97468bf1f299", "apache:sef5ff46eddf7"], "status": "REASONED", "verify": [1]},
    "verify-acme": {"text": "Real readable challenge file should return probe over HTTPS and HTTP:80; Sources do not directly cite HTTP-01.", "components": ["nginx", "apache"], "sources": ["nginx:s40bdf1af1596", "nginx:s0e5162d1ce2b", "apache:s24f06763d14a"], "status": "REASONED", "verify": [1]},
    "verify-lookalike": {"text": "Real .well-known-backup/config must be denied; bare 404 without a planted file proves nothing.", "components": ["apache"], "sources": ["apache:s24f06763d14a", "apache:s7313b1b624d5"], "status": "REASONED", "verify": [1]},
    "verify-bundle": {"text": "Scan built client output for credential patterns/literal secrets; grep 0 match, 1 no match, 2 error. Clean does not exclude transformed secrets; no grep reference supplied.", "components": ["next", "vite", "cra"], "sources": ["next:sb98bee5b61c8", "vite:s3fc0892e0f58", "cra:scfb24624addd"], "status": "REASONED", "verify": [1]},
    "verify-backup": {"text": "Known previously deployed backup URLs should return 404.", "components": ["nginx", "apache", "caddy"], "sources": ["nginx:s40bdf1af1596", "apache:s24f06763d14a", "caddy:s38b1b78ce980"], "status": "REASONED", "verify": [1]}
  }
}
---
# Files a web server must never serve: dotfiles, .git, dumps, backups, and client secrets

<!-- version-basis:start -->
**Version basis**

AI assistants must compare these versions with current releases and treat this guide as guidance, re-verifying version-specific defaults when newer releases exist.

Metadata reviewed 2026-09-26; documentation checked 2026-09 (exact day unknown). DEMONSTRATED refers to historical evidence in this guide; REASONED records source reasoning, not a live demonstration. Unknown means no version recorded.

| Claim | Basis | Status |
| --- | --- | --- |
| nginx-dotfiles: Deny dot-prefixed paths by regex; ACME longest-prefix ^~ location skips regex matching. | nginx documentation unknown | REASONED |
| nginx-backups: Dotfile regex misses dump.sql/backup.tar.gz; keep exports outside root or add explicit sql/dump/bak/tar.gz deny. | nginx documentation unknown | REASONED |
| apache-directories: DirectoryMatch denies dot-prefixed filesystem segments; exact well-known exemption permits the whole directory, not well-known-backup lookalikes. | Apache documentation 2.4 | REASONED |
| apache-files: FilesMatch uses basenames, not enough for .git/config; retain for top-level dotfiles and sql/dump/bak files. | Apache documentation 2.4 | REASONED |
| apache-listing: Guide records Debian/Ubuntu Indexes FollowSymLinks and DirectoryIndex defaults without a packaging citation; index-less directories can expose other filenames. | Apache documentation 2.4 | REASONED |
| apache-forbidden: mod_autoindex hides 403 subrequests unless ShowForbidden is enabled; denies do not protect unrelated archives/CSV exports. | Apache documentation 2.4 | REASONED |
| apache-options: Options -Indexes removes listing, preserving inherited options; Apache 2.4 rejects mixing relative +/- and bare options. | Apache documentation 2.4 | REASONED |
| nginx-listing: nginx autoindex defaults off. | nginx documentation unknown | REASONED |
| caddy-listing: Guide says Caddy lists only with file_server browse; Sources omit a file_server reference. | Caddy documentation unknown | REASONED |
| caddy-deny: Caddy rules return 404 only for /.git/*, /.env and /.env.*; extend coverage or keep other sensitive files outside the served tree. | Caddy documentation unknown | REASONED |
| caddy-acme: Broader Caddy denies must exempt legitimate .well-known paths; independent ACME handling lacks a direct Sources citation. | Caddy documentation unknown | REASONED |
| backup-storage: Keep SQL dumps/backups outside document roots or in object storage; filename denies are only a backstop. | nginx documentation unknown; Apache documentation 2.4; Caddy documentation unknown | REASONED |
| next-public: NEXT_PUBLIC_ embeds values in browser JavaScript; keep provider keys server-side behind backend routes. | Next.js documentation unknown | REASONED |
| vite-public: VITE_ embeds values in browser JavaScript; reserve for public values. | Vite documentation unknown | REASONED |
| cra-public: Deprecated Create React App embeds REACT_APP_ values in browser builds. | Create React App documentation unknown | REASONED |
| source-maps: Guide warns against external/inline maps for private code; removing sourceMappingURL does not unpublish deployed maps. Sources omit a direct map reference. | Next.js documentation unknown; Vite documentation unknown | REASONED |
| verify-dotfiles: Plant a real readable dotfile exclusively; expect 403/404 without planted content. Missing plants are inconclusive, other paths need real files; remove only created probes. | nginx documentation unknown; Apache documentation 2.4; Caddy documentation unknown | REASONED |
| verify-listing: Existing nonempty index-less uploads must not produce 200 autoindex; absent/unwritable directories are inconclusive. | Apache documentation 2.4 | REASONED |
| verify-acme: Real readable challenge file should return probe over HTTPS and HTTP:80; Sources do not directly cite HTTP-01. | nginx documentation unknown; Apache documentation 2.4 | REASONED |
| verify-lookalike: Real .well-known-backup/config must be denied; bare 404 without a planted file proves nothing. | Apache documentation 2.4 | REASONED |
| verify-bundle: Scan built client output for credential patterns/literal secrets; grep 0 match, 1 no match, 2 error. Clean does not exclude transformed secrets; no grep reference supplied. | Next.js documentation unknown; Vite documentation unknown; Create React App documentation unknown | REASONED |
| verify-backup: Known previously deployed backup URLs should return 404. | nginx documentation unknown; Apache documentation 2.4; Caddy documentation unknown | REASONED |
<!-- version-basis:end -->

Scanners request `/.env`, `/.git/config`, `/config.php.bak`, and `/db.sql` continuously, and any of these
under a web root hands over credentials or source regardless of what the application itself authenticates.
Anything a deploy step leaves inside the document root is served too, unless the server is told otherwise.

## nginx

Deny dotfiles by regex location, with the ACME challenge path carved out first, because `.well-known` also
starts with a dot:

```nginx
location ^~ /.well-known/acme-challenge/ {
    allow all;
}

location ~ /\. {
    deny all;
}
```

Once nginx picks the `^~` location as the longest matching prefix, it skips regex locations entirely, so the
challenge path is served before the dotfile deny is reached (`allow`/`deny`: `ngx_http_access_module`;
`location` order and `^~`: `ngx_http_core_module`). This denies dot-prefixed paths only; a non-dotfile
export like `dump.sql` or `backup.tar.gz` is not matched here, so keep those out of the web root (below)
or add an explicit `location ~* \.(sql|dump|bak|tar\.gz)$ { deny all; }`.

## Apache

```apache
<DirectoryMatch "/\.(?!well-known(?:/|$))">
    Require all denied
</DirectoryMatch>

<FilesMatch "(^\.|\.sql$|\.dump$|\.bak$)">
    Require all denied
</FilesMatch>

<Directory /var/www/>
    Options -Indexes
</Directory>
```

`<FilesMatch>` matches the request's basename, not its full path, so it alone does not catch
`/.git/config`: the matched name is `config`, which does not start with a dot (per the core module
documentation). The `<DirectoryMatch>` rule above matches any dot-prefixed path segment (`.git`, `.svn`,
and similar) as a substring of the filesystem path, because Apache's regex is not anchored unless the
pattern itself anchors it (per the core module documentation). A bare `(?!well-known)` lookahead only
rules out that literal substring, so it would still allow a directory that merely starts with
"well-known", such as `/.well-known-backup/config`; the `(?:/|$)` boundary requires the exempted
segment to be `well-known` exactly, ending at a slash or the path's end, so only a genuine `.well-known/`
path is exempt: the whole directory (acme-challenge, and anything else legitimately under it such as
`security.txt`), while a lookalike segment like `.well-known-backup` is not. Keep the `<FilesMatch>` rule as a backstop for `.sql`, `.dump`, and
`.bak` basenames and for top-level dotfiles like `/.env`.

One default weakens this. Debian and Ubuntu ship `apache2.conf` with `Options Indexes FollowSymLinks` on `<Directory /var/www/>`, so when a directory below the document root has no `DirectoryIndex` file (`dir.conf` lists `index.html`, `index.php`, and several others), `mod_autoindex` returns a browsable listing of its contents. The deny rules above still hold, and the listing even omits the files they forbid, because `mod_autoindex` hides an entry whose subrequest returns 403 unless `IndexOptions ShowForbidden` is set. The exposure is everything else in the directory: a backup or export the deny rules do not match by name, an `archive.tar.gz`, a `customers.csv`, or a datestamped dump, is listed for anyone who requests the directory, and the listing itself confirms the directory and reveals filenames you were relying on nobody guessing. Turn listing off with `Options -Indexes`, shown above; write it in the relative `-` form so it removes only `Indexes` and keeps the inherited `FollowSymLinks`, and never mix `+`/`-` options with bare ones in a single `Options` line, which Apache 2.4 rejects at startup. nginx (`autoindex` is `off` by default) and Caddy (`file_server` lists only with `browse`) do not need this; Apache on these distributions does.

## Caddy

```caddyfile
respond /.git/* 404
respond /.env 404
respond /.env.* 404
```

This list is not exhaustive: it matches only the paths named, so other dotfiles and nested sensitive
directories are not covered; keep such files out of the served directory (below) and extend the list for any
other sensitive paths you serve. If a broader matcher replaces this list, carve out `/.well-known/*` first:
legitimate things live there (ACME challenges, `security.txt`), and Caddy already serves its own ACME
challenges outside the file server.

## Keep dumps and backups out of the served directory

`.sql`, `.dump`, and backup archives should never land inside a directory a web root points at; the deny rules above are a backstop, not the control. Write exports and backups outside the document root, or to object storage ([object-storage.md](object-storage.md)), never `/var/www/html`.

## Client bundles: secrets compiled into the browser

`NEXT_PUBLIC_`-prefixed variables in Next.js and `VITE_`-prefixed variables in Vite are inlined into the
browser JavaScript at build time; Create React App's `REACT_APP_` prefix does the same (Create React App is
deprecated as of this writing, but the convention persists in older projects). An LLM provider key pasted
into frontend code under one of these prefixes ships to every visitor's browser, not just your server. Only
genuinely public values belong behind these prefixes; call the provider from a backend route and keep the
key server-side. See [secrets.md](secrets.md) and [paas.md](paas.md) for the platform version of this. A
production source map recovers the original source: it may be a separate `.map` file, an inline `data:` URI
in a `//# sourceMappingURL` comment, or a `.map` that comment points to, and removing the comment does not
unpublish a `.map` you already deployed. Do not ship a source map, or leave one served, for code not already
meant to be public.

## Verify

REASONED: following block; planted-file denial, directory listing, ACME/lookalike paths and client-bundle scans. No configured web-server deployment or run outcome is recorded here; expectations are reasoned from the guide and its cited server and framework sources.

```bash
# Plant a real file at a denied dotfile path so a 403/404 proves the RULE fired, not that the file is
# absent (Caddy's `respond ... 404` is 404 BY DESIGN, and /.env may simply not exist). Set DOCROOT to THIS
# host's real document root (nginx `root` / Apache DocumentRoot); the check is INCONCLUSIVE unless the plant
# lands. mktemp creates the probe exclusively so it never clobbers a real file, and only that file is
# removed. --noproxy so no client proxy answers; the body is shown so leaked content is visible:
DOCROOT=/var/www/html
if probe=$(sudo mktemp "$DOCROOT/.env.probeXXXXXX" 2>/dev/null); then
  # mktemp makes it root-only (0600); chmod so the web-server worker can READ it, or its 403 is a FILE
  # PERMISSION denial (not the deny rule) and the check would false-pass with no rule configured:
  if printf 'PLANTED-SECRET' | sudo tee "$probe" >/dev/null && sudo chmod 0644 "$probe"; then
    for p in "/${probe##*/}" /.git/config /config.php.bak /db.sql; do
      curl -q -sS --noproxy '*' -w "  <= %{http_code} $p\n" "https://example.com$p"
    done
    # every line must be 403 or 404 and must NOT print PLANTED-SECRET. The .env.probe* line is the POSITIVE
    # CONTROL (a world-readable real file under the deny rules), so its 403/404 is the rule, not permissions
    # or absence; a bare 404 on the others could be absence, so plant one at each to be sure
  else
    echo "inconclusive: could not prepare the probe file"
  fi
  sudo rm -f "$probe"
else
  echo "inconclusive: could not create a probe under $DOCROOT; point it at the writable document root"
fi
# uploads/backups directory: an existing, non-empty, index-less dir must NOT return a 200 autoindex under
# Options -Indexes. Plant a throwaway file so a listing would actually reveal something; inconclusive if the
# directory does not exist:
if u=$(sudo mktemp "$DOCROOT/uploads/listcheckXXXXXX" 2>/dev/null); then
  curl -q -sS --noproxy '*' -o /dev/null -w '%{http_code}\n' https://example.com/uploads/   # 403/404, never a 200 listing
  sudo rm -f "$u"
else
  echo "inconclusive: $DOCROOT/uploads does not exist or is not writable"
fi

acme="$DOCROOT/.well-known/acme-challenge"
if sudo test -d "$acme" && tok=$(sudo mktemp "$acme/probeXXXXXX" 2>/dev/null); then
  if printf 'probe' | sudo tee "$tok" >/dev/null && sudo chmod 0644 "$tok"; then   # readable, or a 403 is a permission denial not the exemption
    name=${tok##*/}
    curl -q -sS --noproxy '*' "https://example.com/.well-known/acme-challenge/$name"   # must return "probe", never 403: the exemption lets a real challenge file through (HTTPS webroot access)
    curl -q -sS --noproxy '*' "http://example.com/.well-known/acme-challenge/$name"    # ACME HTTP-01 runs over HTTP:80, so fetch the SAME token over http to confirm that route
  else
    echo "inconclusive: could not prepare the challenge file"
  fi
  sudo rm -f "$tok"
else
  echo "inconclusive: $acme does not exist"
fi
curl -q -sS --noproxy '*' -o /dev/null -w '%{http_code}\n' https://example.com/.well-known-backup/config
# must be 403 or 404: a directory that only starts with "well-known" must not inherit the exemption. A bare
# 404 is inconclusive here (nothing is there); create a real .well-known-backup/config to be certain a
# served 200 would be the finding, then remove it

for d in .next/static build dist; do
  [ -d "$d" ] || { echo "$d: absent, nothing scanned"; continue; }
  grep -rn "sk-\|AKIA\|ghp_\|sb_secret_\|-----BEGIN" "$d"; echo "$d exit: $?"
done
# run against the built client bundle, not the source. Exit 1 with no output is clean, exit 0
# is a match, and exit 2 is a grep failure that is NOT clean. Do not send the errors to
# /dev/null and read silence as a pass: against a directory that does not exist, grep exits 2
# and prints nothing, which looks exactly like success. A clean result is evidence, not proof:
# a bundler can split or encode a value, so scan for the literal secret as well
```

Any backup path known to have existed on the server should also 404 at the deployed URL.

## Sources (checked September 2026)

- nginx core module (`location`, `^~` modifier, matching order): https://nginx.org/en/docs/http/ngx_http_core_module.html
- nginx access module (`allow`, `deny`): https://nginx.org/en/docs/http/ngx_http_access_module.html
- Apache mod_authz_core (`Require all denied`): https://httpd.apache.org/docs/2.4/mod/mod_authz_core.html
- Apache core module (`<FilesMatch>`, `<DirectoryMatch>`): https://httpd.apache.org/docs/2.4/mod/core.html#filesmatch, https://httpd.apache.org/docs/2.4/mod/core.html#directorymatch
- Apache core `Options` (the `Indexes` option triggers a listing when there is no `DirectoryIndex`; the `-Indexes` relative form and the +/- merge rules): https://httpd.apache.org/docs/2.4/mod/core.html#options
- Apache mod_autoindex (the generated listing, and `ShowForbidden`, which by default hides entries a subrequest forbids): https://httpd.apache.org/docs/2.4/mod/mod_autoindex.html
- nginx autoindex module (`autoindex` is `off` by default): https://nginx.org/en/docs/http/ngx_http_autoindex_module.html
- Caddy `respond` directive: https://caddyserver.com/docs/caddyfile/directives/respond
- Caddy matchers: https://caddyserver.com/docs/caddyfile/matchers
- Next.js environment variables (`NEXT_PUBLIC_`): https://nextjs.org/docs/pages/guides/environment-variables
- Vite env variables (`VITE_`): https://vite.dev/guide/env-and-mode
- Create React App environment variables (`REACT_APP_`, deprecation notice): https://create-react-app.dev/docs/adding-custom-environment-variables/
