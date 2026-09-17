# Files a web server must never serve: dotfiles, .git, dumps, backups, and client secrets

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
