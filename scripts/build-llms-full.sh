#!/usr/bin/env bash
# Regenerates site/llms-full.txt (every guide concatenated into one file).
# Run from the repository root after adding or editing guides.
set -euo pipefail

out="site/llms-full.txt"
files=(
  README.md
  controls-reference.md
  free-certificates.md self-signed.md cloudflare.md tailscale.md tunnels.md
  authentication.md mfa.md secrets.md vault.md
  identity-providers.md self-hosted-idp.md oidc-integration.md cloud-identity-proxies.md machine-auth.md fronting-auth.md
  apache.md nginx.md lighttpd.md caddy.md haproxy.md traefik.md
  nodejs.md python.md docker.md kubernetes.md gitops-controllers.md self-hosted-ci-runners.md frontend-frameworks.md container-hardening.md
  nextjs.md go.md dotnet.md java.md php.md ruby.md
  host.md cloud-firewalls.md paas.md egress-metadata.md gpu-clouds.md deployment-lifecycle.md
  postgresql.md connection-poolers.md mysql.md mongodb.md redis.md elasticsearch.md minio.md
  rabbitmq.md mosquitto.md
  kafka.md clickhouse.md neo4j.md memcached.md object-storage.md nats.md search-engines.md sqlite.md sqlite-http-frontends.md surrealdb.md time-series-metrics-stores.md
  jupyter.md ollama.md open-webui.md litellm.md model-servers.md
  gradio.md streamlit.md n8n.md code-server.md self-hosted-error-trackers.md
  vector-databases.md mcp-servers.md mcp-clients.md ray.md mlflow.md agent-builders.md ai-infra-services.md realtime-voice-infra.md
  image-gen-uis.md chat-uis.md llm-observability.md workflow-orchestrators.md
  admin-uis.md observability-components.md devops-uis.md cors.md headers.md firebase-supabase.md supabase-self-hosted.md web-exposure.md realtime-webhooks.md transactional-email-posture.md bi-dashboards.md low-code-builders.md server-admin-panels.md nomad-consul.md pocketbase.md headless-browser-services.md headless-cms-instant-api.md exposure-index.md common-mistakes.md
)

# Say what we build from, so the gate that records it does not have to work it out. This
# block sits immediately before the work on purpose: anything that changes `files` has to
# happen ABOVE it, or the list reported here would not be the list built from below. A
# reviewer demonstrated exactly that drift with an append placed after an earlier position
# of this block.
if [ "${1:-}" = "--list-inputs" ] || [ "${1:-}" = "--list-guides" ]; then
  printf '%s\n' "${files[@]}"
  if [ "${1:-}" = "--list-inputs" ]; then
    printf '%s\n' tools/version_basis.py tools/version_basis_guides.txt tools/version_basis_sources_baseline.txt tools/_markdown.py tools/check_guide_shape.py tools/check_verify_marking.py tools/_verify_sections.py CHANGELOG.md
  fi
  exit 0
fi

# The link check. The bundle is served from https://secureconfig.ai/, where a relative link
# such as (mfa.md) resolves to a page that does not exist, so no link in it may be relative.
# This program parses a bundle with the pinned markdown-it-py in its CommonMark preset, once
# as is and once with tables enabled as the other gates parse, and parses each piece of raw
# HTML the Markdown parser finds with Python's html.parser. It checks the target of every link
# and image, every link reference definition, and these HTML attributes: href, xlink:href, src,
# longdesc, poster, action, formaction, data, cite, background, codebase, classid, usemap,
# manifest, icon, lowsrc, dynsrc and profile, each URL in ping and archive, the url= part of a
# meta content attribute, and each url(...) in a style attribute or style element. A target
# passes only if it is an in-page anchor or has a scheme, and one that urllib.parse cannot split
# fails. An http or https URL whose host is github.com, ignoring case, a leading www. and a
# trailing dot, and whose first two path segments are jposluns and secureconfig in any case is a
# link into this repository. Its blob/main/ and raw/main/ routes must name a file present in
# this checkout and its tree/main/ route a directory, after percent-decoding, with the route
# name in any case and the branch spelled main. An empty path, a leading slash or a .. segment
# fails. Its other routes, such as another branch or commit, a pull request or the repository
# itself, pass as URLs with a scheme and are not checked. Any srcset or imagesrcset fails, as
# does CSS that holds a backslash, @import, image-set( or src(, a url( that does not close, a
# style element that continues outside the HTML that opens it, and raw HTML that html.parser
# leaves unfinished, such as a tag still open at the end of the piece. Code spans, fenced code
# and indented code are code to the parser, so a link-shaped string inside them is not checked.
# A self-test runs before the bundle is read, so what checks the bundle is the shipped rule. It
# has at least one mutation for each form, HTML attribute and CSS form named here and for each
# spelling of a repository link, and clean cases. It reads only the working tree, so it stays
# offline. The build runs it on its output before writing site/llms-full.txt, and the gate in
# tools/run_all_checks.sh runs it on the committed file through --check-links, so the build and
# the gate apply one rule.
IFS= read -r -d '' certify <<'PY' || true
import html.parser
import os
import re
import sys
from urllib.parse import unquote, urlsplit

sys.path.insert(0, "tools")
from check_verify_marking import ParserUnavailable, gate_parser

SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
REPO = "https://github.com/jposluns/secureconfig"
# The routes into this repository's main branch that name a path, and what each path must be.
ROUTES = {"blob": "file", "raw": "file", "tree": "directory"}
# HTML attributes whose value is one URL, and those whose value is a space-separated URL list.
ONE_URL = {
    "href", "xlink:href", "src", "longdesc", "poster", "action", "formaction", "data", "cite",
    "background", "codebase", "classid", "usemap", "manifest", "icon", "lowsrc", "dynsrc", "profile",
}
URL_LIST = {"ping", "archive"}
# Each candidate in these is a URL with an optional descriptor, so neither is ever certified.
CANDIDATES = {"srcset", "imagesrcset"}
CSS_URL = re.compile(r"url\(\s*([\"']?)(.*?)\1\s*\)", re.I | re.S)
CSS_OPEN = re.compile(r"url\(", re.I)
CSS_OTHER = re.compile(r"\\|@import|image-set\(|src\(", re.I)
REFRESH = re.compile(r"url\s*=\s*[\"']?([^\"']*)", re.I)
HEADER = "=" * 70
# Each mutation must fail the check; each clean case must pass it.
MUTATIONS = [
    "[x](mfa.md)",
    "[x](./mfa.md#a)",
    '[x](mfa.md "title")',
    "[x](<mfa.md>)",
    '[x]( <mfa.md> "title")',
    "[x](foo(1).md)",
    "[x](\nmfa.md)",
    "[x]()",
    "[x](//example.com/a)",
    "![i](mfa.png)",
    "[x]: mfa.md",
    '   [x]: <mfa.md> "title"',
    "> - [x]: mfa.md",
    "[x]:\nmfa.md",
    "[a\nb]: mfa.md",
    "[`m`]: mfa.md",
    "a ` b\nc ` [x](mfa.md) ` d",
    '<a href="mfa.md">x</a>',
    "<img src='mfa.png'>",
    "<a HREF=mfa.md>x</a>",
    'See <a href\n="mfa.md">x</a>.',
    '<img\nsrc="mfa.png">',
    'See <img src\n= "mfa.png">.',
    '<img srcset="https://example.com/a.png 1x">',
    'See <img\nsrcset="https://example.com/a.png 1x">.',
    '<a href="https://example.com/" ping="https://example.com/p track">x</a>',
    '<img src="https://example.com/a.png" longdesc="mfa.md">',
    '<link rel="preload" as="image" imagesrcset="https://example.com/a.png 1x">',
    '<div style="background: url(mfa.png)">x</div>',
    "<div style='background: url(\"mfa.png\")'>x</div>",
    '<div style="background: u\\72l(mfa.png)">x</div>',
    '<div style="background: url(https://example.com/a.png">x</div>',
    "<style>\na { background: url(mfa.png) }\n</style>",
    "See <style>a { color: red }",
    '<video poster="mfa.png"></video>',
    '<form action="mfa.md"></form>',
    '<button formaction="mfa.md">x</button>',
    '<object data="mfa.md"></object>',
    '<q cite="mfa.md">x</q>',
    '<table><tr><td background="mfa.png">x</td></tr></table>',
    '<svg><a xlink:href="mfa.md">x</a></svg>',
    '<meta http-equiv="refresh" content="0; url=mfa.md">',
    '<object codebase="mfa/"></object>',
    '<object classid="mfa.md"></object>',
    '<img src="https://example.com/a.png" usemap="mfa.md">',
    '<html manifest="mfa.md">',
    '<command icon="mfa.png">',
    '<img src="https://example.com/a.png" lowsrc="mfa.png">',
    '<img src="https://example.com/a.png" dynsrc="mfa.png">',
    '<head profile="mfa.md">',
    '<applet archive="https://example.com/a.jar mfa.jar"></applet>',
    "<style>\n@import 'https://example.com/a.css';\n</style>",
    "<div style='background: image-set(\"https://example.com/a.png\" 1x)'>x</div>",
    '<div style="background: src(https://example.com/a.png)">x</div>',
    '<div>\n<a href="mfa.md"\n\ntitle="y">x</a></div>',
    '<a href="http://[nope/a">x</a>',
    f"[x]({REPO}/blob/main/nope-missing.md)",
    f"[x]({REPO}/blob/main/tools/)",
    f"[x]({REPO}/tree/main/mfa.md/)",
    f"[x]({REPO}/blob/main/../mfa.md)",
    f"[x]({REPO}/blob/main//etc/hostname)",
    f"[x]({REPO}/blob/main/)",
    f"[x]({REPO}/blob/main)",
    f"[x]({REPO}/tree/main/)",
    f"[x]({REPO}/blob/main/nope%2Dmissing.md)",
    f"[x]({REPO}/raw/main/nope-missing.md)",
    f"[x]({REPO}/Blob/main/nope-missing.md)",
    "[x](https://GITHUB.COM/jposluns/secureconfig/blob/main/nope-missing.md)",
    "[x](https://GITHUB.COM/jposluns/secureconfig/blob/main/)",
    "[x](http://github.com/jposluns/secureconfig/blob/main/nope-missing.md)",
    "[x](http://github.com/jposluns/secureconfig/tree/main/mfa.md/)",
    "[x](https://www.github.com/jposluns/secureconfig/blob/main/nope-missing.md)",
    "[x](https://www.github.com:443/jposluns/secureconfig/blob/main/tools/)",
    "[x](https://github.com/JPosluns/SecureConfig/blob/main/nope-missing.md)",
    "[x](https://github.com./jposluns/secureconfig/blob/main/nope-missing.md)",
    f"[x]: {REPO}/blob/main/nope-missing.md",
    f'<a href="{REPO}/blob/main/nope-missing.md">x</a>',
    '<a href="HTTP://GitHub.com/jposluns/secureconfig/blob/main/nope-missing.md">x</a>',
]
CLEAN = [
    f"[x]({REPO}/blob/main/mfa.md)",
    f'[x]({REPO}/blob/main/mfa.md#a "title")',
    f"[x](<{REPO}/tree/main/tools/>)",
    f"[x]({REPO}/blob/main/m%66a.md) and [y]({REPO}/raw/main/mfa.md)",
    "[x](http://github.com/jposluns/secureconfig/blob/main/mfa.md)",
    "[x](https://WWW.GitHub.com/JPosluns/SecureConfig/tree/main/tools/)",
    f"[x]({REPO}) and [y]({REPO}/pull/450) and [z]({REPO}/blob/0123abc/nope-missing.md)",
    f"[x]: {REPO}/blob/main/mfa.md",
    f'<a href="{REPO}/blob/main/mfa.md" ping="https://example.com/p">x</a>',
    f'See <a href\n="{REPO}/blob/main/mfa.md">x</a>.',
    '<div style="background: url(https://example.com/a.png)">x</div>',
    "[x](#a) and [y](https://example.com/a_(b)) and <https://example.com/c>",
    "[x]( and [y]: mfa.md",
    "[x]:",
    '`[x](mfa.md)` and ``[y]: mfa.md`` and `<a href="mfa.md">`',
    "a `b\n[x](mfa.md) c` d",
    '```\n[x](mfa.md)\n[y]: mfa.md\n<a href="mfa.md">\n```',
    "~~~~md\n![i](mfa.png)\n~~~~",
    'Text.\n\n    [x](mfa.md)\n    <a href="mfa.md">x</a>',
    '<!-- <a href="mfa.md">x</a> -->',
    '<a id="ai-assistant-prompt"></a>',
]


class Html(html.parser.HTMLParser):
    """The URL-valued attributes and the CSS in one piece of raw HTML."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found, self.css, self.styling = [], [], False

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            value = (value or "").strip(" \t\n\f\r")
            if name in ONE_URL:
                self.found.append((name, value))
            elif name in URL_LIST:
                self.found.extend((name, part) for part in value.split() or [""])
            elif name in CANDIDATES:
                self.found.append((name, None))
            elif name == "style":
                self.css.append(value)
            elif name == "content" and tag == "meta":
                self.found.extend(("meta url=", part.strip()) for part in REFRESH.findall(value))
        if tag == "style":
            self.styling = True

    def handle_endtag(self, tag):
        if tag == "style":
            self.styling = False

    def handle_data(self, data):
        if self.styling:
            self.css.append(data)


def styles(css):
    """Each url(...) target in some CSS; None for a form that is never certified."""
    if CSS_OTHER.search(css):
        yield "CSS with a backslash, @import, image-set( or src(", None
    for start in CSS_OPEN.finditer(css):
        match = CSS_URL.match(css, start.start())
        yield ("url()", match.group(2).strip()) if match else ("a url( that does not close", None)


def pieces(parser, text):
    """Each (line, form, target) in parsed text; a target of None is never certified."""
    pending = [(token, 0) for token in reversed(parser.parse(text))]
    while pending:
        token, line = pending.pop()
        if token.map:
            line = token.map[0] + 1
        if token.type == "link_open":
            yield line, "link", token.attrs.get("href", "")
        elif token.type == "image":
            yield line, "image", token.attrs.get("src", "")
        elif token.type == "definition":
            yield line, "definition", token.meta["url"]
        elif token.type in ("html_inline", "html_block"):
            raw = Html()
            raw.feed(token.content)
            # Text html.parser holds back, such as a tag still open at the end of the piece, is
            # not reported to Html, so it fails rather than pass unread.
            unread = raw.rawdata.strip(" \t\n\f\r")
            raw.close()
            if unread:
                yield line, "raw HTML that html.parser leaves unfinished", None
            for form, target in raw.found:
                yield line, form, target
            for css in raw.css:
                for form, target in styles(css):
                    yield line, form, target
            if raw.styling:
                yield line, "a style element that continues outside its HTML", None
        pending.extend((child, line) for child in reversed(token.children or []))


def verdict(form, target):
    """A problem with one target, or None, and whether it points into this repository."""
    if target is None:
        return f"{form} is never certified", False
    if target.startswith("#"):
        return None, False
    try:
        parts = urlsplit(target)
        host = (parts.hostname or "").casefold().rstrip(".").removeprefix("www.")
    except ValueError:
        return f'{form} target "{target}" cannot be split as a URL', False
    segments = parts.path.split("/")
    owner, repo, route, ref = [unquote(segment) for segment in segments[1:5] + ["", "", "", ""]][:4]
    if (parts.scheme in ("http", "https") and host == "github.com" and owner.casefold() == "jposluns"
            and repo.casefold() == "secureconfig" and route.casefold() in ROUTES and ref == "main"):
        what, path = ROUTES[route.casefold()], unquote("/".join(segments[5:])).rstrip("/")
        found = os.path.isdir(path) if what == "directory" else os.path.isfile(path)
        if not path or path.startswith("/") or ".." in path.split("/") or not found:
            return f"{form} {target} names no {what} in this checkout", True
        return None, True
    if SCHEME.match(target):
        return None, False
    return f'{form} target "{target}" is not absolute, a scheme or an in-page anchor', False


def check(text):
    """The problems in some Markdown, and how many of its links point into this repository."""
    lines = text.split("\n")
    guides = [(n + 1, lines[n][4:]) for n in range(1, len(lines) - 1)
              if lines[n].startswith("==> ") and lines[n - 1] == HEADER == lines[n + 1]]
    problems, counts = {}, []
    for parser in PARSERS:
        count = 0
        for line, form, target in pieces(parser, text):
            problem, own = verdict(form, target)
            count += own
            if problem:
                guide = next((g for start, g in reversed(guides) if start <= line), None)
                where = f"line {line} ({guide})" if guide else f"line {line}"
                problems.setdefault(f"{where}: {problem}")
        counts.append(count)
    return list(problems), counts[0]


try:
    PARSERS = [gate_parser(required=True), gate_parser(required=True).disable("table")]
except ParserUnavailable as exc:
    sys.exit(f"the link check needs the pinned parser: {exc}")
for parser in PARSERS:
    parser.options["inline_definitions"] = True
problems = []
for case in MUTATIONS:
    if not check(case)[0]:
        problems.append(f"self-test: mutation passed: {case!r}")
for case in CLEAN:
    failed = check(case)[0]
    if failed:
        problems.append(f"self-test: clean case failed: {case!r}: {failed[0]}")
with open(sys.argv[1], encoding="utf-8") as handle:
    found, links = check(handle.read())
problems += found
for problem in problems:
    print(problem)
if problems:
    sys.exit(1)
print(links)
PY

if [ "${1:-}" = "--check-links" ]; then
  exec python3 -c "$certify" "$out"
fi

python3 tools/version_basis.py --check

# Because of the relative-link problem the link check describes, each relative link outside code
# is rewritten to the same path in the repository on GitHub: blob/main/<path> for a file and
# tree/main/<path>/ for a directory, keeping any #anchor. That covers an inline link or image,
# with or without angle brackets or a title, and a link reference definition such as
# [m]: mfa.md. In-page anchors, links with a scheme, fenced blocks and code spans stay exactly
# as written, using the fence rule the gates use.
#
# The ref is the branch name main, not a commit SHA. The build has to be offline and
# deterministic, and the commit that will carry this file does not exist while the file is
# being built, so a SHA could only name an earlier commit: stale from the moment it merged, and
# a hand bump on every change. The branch name main is a constant the build knows offline, it
# is the ref that site/llms.txt and README.md already use, and the freshness gate keeps the
# committed bundle equal to the guides it was built from, so on main a link and the text around
# it describe the same revision.
#
# A link that leaves the repository, or names a path absent from this checkout, fails the
# build, so a broken target cannot reach the bundle as a dead GitHub URL. The rewrite works one
# line at a time, so it does not handle every form the parser does, such as a relative HTML
# attribute or a definition whose label spans lines. The link check above therefore runs on the
# built text before it replaces site/llms-full.txt, and any target it cannot certify fails the
# build. The build also parses each guide before and after the rewrite and fails if any code
# span, code block or raw HTML changed, so a line the rewrite reads as prose but the parser reads
# as code is refused rather than altered.
IFS= read -r -d '' absolutize <<'PY' || true
import os
import posixpath
import re
import sys

sys.path.insert(0, "tools")
from _markdown import Fences
from check_verify_marking import ParserUnavailable, gate_parser

BASE = "https://github.com/jposluns/secureconfig"
REF = "main"
KEEP = re.compile(r"^(?:[A-Za-z][A-Za-z0-9+.-]*:|#)")
TICKS = re.compile(r"`+")
# An inline link or image target, bare or in angle brackets, followed by a title or ")".
INLINE = re.compile(r"(\]\([ \t]*)(?:<([^<>\n]*)>|([^\s<>()]+)(?=[ \t]|\)))")
# A link reference definition at the start of a line, inside a block quote or list item or not.
DEFINE = re.compile(r"^([ \t>]*(?:(?:[-+*]|\d{1,9}[.)])[ \t]+)*\[[^\]]+\]:[ \t]*)(?:<([^<>\n]*)>|(\S+))")
LITERAL = ("code_inline", "code_block", "fence", "html_inline", "html_block")
name = sys.argv[1]


def absolute(target):
    if not target or any(c.isspace() for c in target):
        sys.exit(f'{name}: link target "{target}" is empty or holds whitespace, so it cannot be rewritten')
    path, mark, anchor = target.partition("#")
    clean = posixpath.normpath(path)
    if path.startswith("/") or clean == ".." or clean.startswith("../"):
        sys.exit(f"{name}: link {target} does not name a path inside the repository")
    if not os.path.exists(clean) or (path.endswith("/") and not os.path.isdir(clean)):
        sys.exit(f"{name}: link {target} names no file or directory in the repository")
    kind = "tree" if os.path.isdir(clean) else "blob"
    slash = "/" if path.endswith("/") else ""
    return f"{BASE}/{kind}/{REF}/{clean}{slash}{mark}{anchor}"


def swap(match):
    head, angled, bare = match.groups()
    target = bare if angled is None else angled
    if not KEEP.match(target):
        target = absolute(target)
    return head + (target if angled is None else f"<{target}>")


def prose(text, first):
    # Only the text before a line's first code span can start a reference definition.
    text = INLINE.sub(swap, text)
    return DEFINE.sub(swap, text, count=1) if first else text


def rewrite(line):
    # A code span is literal text, so a link-shaped string inside one is left alone. A run of
    # backticks with no later run of the same length on its line is literal, as in CommonMark.
    runs = list(TICKS.finditer(line))
    out, pos, k = [], 0, 0
    while k < len(runs):
        n = len(runs[k].group(0))
        close = next((j for j in range(k + 1, len(runs)) if len(runs[j].group(0)) == n), None)
        if close is None:
            k += 1
            continue
        out.append(prose(line[pos:runs[k].start()], not out))
        out.append(line[runs[k].start():runs[close].end()])
        pos, k = runs[close].end(), close + 1
    out.append(prose(line[pos:], not out))
    return "".join(out)


def literal(text):
    """The text of each code span, code block and piece of raw HTML, in order."""
    found, pending = [], list(reversed(parser.parse(text)))
    while pending:
        token = pending.pop()
        if token.type in LITERAL:
            found.append((token.type, token.content))
        pending.extend(reversed(token.children or []))
    return found


try:
    parser = gate_parser(required=True)
except ParserUnavailable as exc:
    sys.exit(f"{name}: the build needs the pinned parser: {exc}")
fences = Fences()
source = sys.stdin.buffer.read().decode("utf-8")
lines = source.split("\n")
for i, line in enumerate(lines):
    if not fences.feed(line) and not fences.inside:
        lines[i] = rewrite(line)
result = "\n".join(lines)
if literal(result) != literal(source):
    sys.exit(f"{name}: the rewrite changed a code span, code block or raw HTML, which must stay as written")
sys.stdout.buffer.write(result.encode("utf-8"))
PY

built=$(mktemp)
trap 'rm -f "$built"' EXIT
{
  echo "# secureconfig.ai: all guides in one file"
  echo
  echo "> Generated from https://github.com/jposluns/secureconfig (CC0 1.0, except the AIQT Guardrails material listed in .aiqt/PIN, Apache-2.0)."
  echo "> Per-guide index: https://secureconfig.ai/llms.txt"
  echo "> Each file below starts with a line such as \`==> nginx.md\` between two lines of \`=\` characters."
  echo "> Every link to a guide or another repository file is an absolute URL in https://github.com/jposluns/secureconfig on the \`main\` branch, not a page on secureconfig.ai. If GitHub is unreachable, a guide's text is the section below that starts with its file name."
  for f in "${files[@]}"; do
    echo
    echo "======================================================================"
    echo "==> ${f}"
    echo "======================================================================"
    echo
    # Strip legacy front matter; retain each two-section guide whole, including JSON. Then
    # rewrite its relative links to absolute GitHub URLs, as described above.
    python3 tools/version_basis.py --no-advisory --bundle "$f" | python3 -c "$absolutize" "$f"
  done
} > "$built"

# The link check, on the built text before it replaces the committed file.
if ! links=$(python3 -c "$certify" "$built"); then
  printf '%s\n' "$links" >&2
  echo "scripts/build-llms-full.sh: the link check refused the built text; $out is unchanged" >&2
  exit 1
fi
cat "$built" > "$out"

echo "wrote $out ($(wc -c < "$out") bytes, ${#files[@]} files, $links links into this repository)"
