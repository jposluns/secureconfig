#!/usr/bin/env bash
# Cloudflare Pages build command for secureconfig.ai: bash scripts/pages-build.sh
#
# The site is served from the committed files under site/; this builds nothing. It runs the offline
# integrity gates that must hold for what is deployed, and fails the build (so Pages keeps serving
# the previous deployment) on any failure:
#   - the copied site template files match .baseline/pin.toml;
#   - the pages under site/draft/ match a fresh build of their sources;
#   - site/.well-known/security.txt passes its gate, once that gate exists.
# It needs bash and Python 3.11 or later (tomllib), and no network.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -I -B tools/check_baseline_pin.py
python3 -I -B scripts/build-site.py --check
if [ -f tools/check_security_txt.py ]; then
  python3 -I -B tools/check_security_txt.py
fi
echo "Pages build check passed."
