#!/usr/bin/env python3
"""Run saved lychee JSON fixtures through the workflow's actual inline scripts."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parent.parent
workflow = (ROOT / ".github/workflows/linkcheck.yml").read_text(encoding="utf-8")
scripts = re.findall(r"          python3 - <<'PY'\n(.*?)          PY\n", workflow, re.S)
if len(scripts) != 2:
    sys.exit("FAIL: expected both inline lychee report scripts")
if "          lycheeVersion: v0.24.2\n" not in workflow:
    sys.exit("FAIL: expected the verified lycheeVersion pin")
scripts = [textwrap.dedent(script) for script in scripts]
fixtures = json.loads((ROOT / "tools/fixtures/lychee.json").read_text(encoding="utf-8"))
cases = [
    ("404", "404", "success", "2", 1, False),
    ("410", "410", "success", "2", 1, False),
    ("301/403/timeout", "advisory", "success", "2", 0, False),
    ("missing JSON", None, "success", "2", 1, True),
    ("malformed JSON", "malformed", "success", "2", 1, True),
    ("zero results", "zero", "success", "0", 1, True),
    ("missing field", "missing", "success", "2", 1, True),
    ("details false", "no_details", "success", "2", 1, True),
    ("download failure", None, "failure", "", 1, True),
    ("crash with valid JSON", "advisory", "success", "101", 1, True),
    ("action failure with exit 2", "advisory", "failure", "2", 1, True),
    ("missing exit code", "advisory", "success", "", 1, True),
    ("exit 0", "advisory", "success", "0", 0, False),
    ("wrong map type", "bad_map", "success", "2", 1, True),
    ("missing status", "missing_status", "success", "2", 1, True),
    ("missing redirects", "missing_redirects", "success", "2", 1, True),
    ("malformed redirect", "bad_redirect", "success", "2", 1, True),
]
for name, fixture, outcome, exit_code, expected, incomplete in cases:
    with tempfile.TemporaryDirectory(prefix="lychee-test-") as directory:
        root = Path(directory)
        (root / "lychee").mkdir()
        if fixture is not None:
            value = fixtures[fixture]
            content = value if isinstance(value, str) else json.dumps(value)
            (root / "lychee/out.json").write_text(content, encoding="utf-8")
        summary = root / "summary"
        env = dict(os.environ, LYCHEE_OUTCOME=outcome, LYCHEE_EXIT_CODE=exit_code,
                   GITHUB_STEP_SUMMARY=str(summary))
        results = [subprocess.run([sys.executable, "-I", "-B", "-c", script],
                                  cwd=root, env=env, capture_output=True, text=True)
                   for script in scripts]
        codes = [result.returncode for result in results]
        actual = int(any(codes))
        report = summary.read_text(encoding="utf-8")
        output = "".join(result.stdout + result.stderr for result in results)
        if (actual != expected or "Traceback" in output
                or ("INCOMPLETE: sweep could not complete:" in report) != incomplete):
            sys.exit(f"FAIL: {name}: exits {codes}\n{output}\n{report}")
        if fixture == "advisory" and not incomplete:
            for text in ("301", "403", "Timeout", "https://example.com/final"):
                if text not in report:
                    sys.exit(f"FAIL: {name}: summary omitted {text}")
        print(f"  ok    {name}: report exits {codes}; job exit {actual}")
print(f"  ok    {len(cases)} lychee fixture cases")
