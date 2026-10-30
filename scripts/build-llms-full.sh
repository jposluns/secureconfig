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

python3 tools/version_basis.py --check

# The bundle is served from https://secureconfig.ai/, where a guide's relative link such as
# (mfa.md) resolves to a page that does not exist. So each relative link outside code is
# rewritten to the same path in the repository on GitHub: blob/main/<path> for a file and
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
# build, so a broken target cannot reach the bundle as a dead GitHub URL. After the rewrite,
# any link target that is not absolute, a scheme or an in-page anchor also fails the build:
# a relative HTML attribute such as href or src, any srcset, a definition whose target is on
# the next line, and a relative inline target that holds parentheses or whitespace. The gate in
# tools/run_all_checks.sh applies the same rule to the built file.
IFS= read -r -d '' absolutize <<'PY' || true
import os
import posixpath
import re
import sys

sys.path.insert(0, "tools")
from _markdown import Fences

BASE = "https://github.com/jposluns/secureconfig"
REF = "main"
KEEP = re.compile(r"^(?:[A-Za-z][A-Za-z0-9+.-]*:|#)")
TICKS = re.compile(r"`+")
# An inline link or image target, bare or in angle brackets, followed by a title or ")".
INLINE = re.compile(r"(\]\([ \t]*)(?:<([^<>\n]*)>|([^\s<>()]+)(?=[ \t]|\)))")
# A link reference definition at the start of a line, inside a block quote or list item or not.
DEFINE = re.compile(r"^([ \t>]*(?:(?:[-+*]|\d{1,9}[.)])[ \t]+)*\[[^\]]+\]:[ \t]*)(?:<([^<>\n]*)>|(\S+))")
# Where a target starts in each form that is certified after the rewrite, as the gate does.
OPEN = re.compile(r"\]\([ \t]*<?")
OPEN_DEFINE = re.compile(r"^[ \t>]*(?:(?:[-+*]|\d{1,9}[.)])[ \t]+)*\[[^\]]+\]:[ \t]*<?")
ATTRIBUTE = re.compile(
    r"(?i)(?<![\w-])(href|src|srcset|poster|action|formaction|cite|data|background)[ \t]*=[ \t]*[\"']?"
)
TARGET = re.compile(r"[^\s<>()\"']*")
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


def uncertified(text, first):
    """Each target left in text that is not absolute, a scheme or an in-page anchor."""
    starts = [match.end() for match in OPEN.finditer(text)]
    define = OPEN_DEFINE.match(text) if first else None
    if define:
        starts.append(define.end())
    found = [target for target in (TARGET.match(text, s).group(0) for s in starts) if not KEEP.match(target)]
    for match in ATTRIBUTE.finditer(text):
        target = TARGET.match(text, match.end()).group(0)
        if match.group(1).lower() == "srcset" or not KEEP.match(target):
            found.append(f"{match.group(1)}={target}")
    return found


def prose(text, first):
    # Only the text before a line's first code span can start a reference definition.
    text = INLINE.sub(swap, text)
    if first:
        text = DEFINE.sub(swap, text, count=1)
    for target in uncertified(text, first):
        sys.exit(f'{name}: link target "{target}" cannot be certified as absolute, a scheme or an in-page anchor, and the build does not rewrite its form')
    return text


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


fences = Fences()
lines = sys.stdin.buffer.read().decode("utf-8").split("\n")
for i, line in enumerate(lines):
    if not fences.feed(line) and not fences.inside:
        lines[i] = rewrite(line)
sys.stdout.buffer.write("\n".join(lines).encode("utf-8"))
PY

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
} > "$out"

echo "wrote $out ($(wc -c < "$out") bytes, ${#files[@]} files)"
