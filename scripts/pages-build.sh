#!/usr/bin/env bash
# Cloudflare Pages build command for secureconfig.ai: bash scripts/pages-build.sh
#
# The site is served from the committed files under site/; this builds nothing. It runs the offline
# integrity gates that must hold for what is deployed, and fails the build (so Pages keeps serving
# the previous deployment) on any failure:
#   - the copied site template files match .baseline/pin.toml;
#   - the site's palette passes the template's contrast gate, .baseline/check_palette.py, pinned by
#     the gate above (mandatory from baseline 1.6.0; secureconfig.ai has no site-palette.css);
#   - the pages under site/ match a fresh build of their sources at the root;
#   - the site is self-contained and only the /draft/ review page and the 404 are noindex;
#   - every page fits the template page model and site/_headers carries exactly the shared policy;
#   - site/.well-known/security.txt carries the owner's fields.
# It needs bash and Python 3.11 or later (tomllib), and no network.
set -euo pipefail
cd "$(dirname "$0")/.."

if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
  echo "Pages build check: python3 is $(python3 --version 2>&1); these gates need Python 3.11 or later (tomllib)." >&2
  exit 1
fi

python3 -I -B tools/check_baseline_pin.py
python3 -I -B .baseline/check_palette.py --site secureconfig --palettes site/assets/baseline/palettes.css
python3 -I -B scripts/build-site.py --check
python3 -I -B tools/check_draft.py
python3 -I -B tools/check_csp_hashes.py
python3 -I -B tools/check_security_txt.py
echo "Pages build check passed."
