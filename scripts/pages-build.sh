#!/usr/bin/env bash
# Cloudflare Pages build command for secureconfig.ai: bash scripts/pages-build.sh
#
# The site is served from the committed files under site/; this builds nothing. It runs the offline
# integrity gates that must hold for what is deployed, and fails the build (so Pages keeps serving
# the previous deployment) on any failure:
#   - the copied site template files match .baseline/pin.toml;
#   - the pages under site/draft/ match a fresh build of their sources;
#   - the draft stays noindex, out of the live indexes and inside /draft/;
#   - every page's inline blocks and the site/_headers policies pass the CSP gate;
#   - site/.well-known/security.txt carries the owner's fields.
# It needs bash and Python 3.11 or later (tomllib), and no network.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
  echo "Pages build check: python3 is $(python3 --version 2>&1); these gates need Python 3.11 or later (tomllib)." >&2
  exit 1
fi

python3 -I -B tools/check_baseline_pin.py
python3 -I -B scripts/build-site.py --check
python3 -I -B tools/check_draft.py
python3 -I -B tools/check_csp_hashes.py
python3 -I -B tools/check_security_txt.py
echo "Pages build check passed."
