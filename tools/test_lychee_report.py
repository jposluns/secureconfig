#!/usr/bin/env python3
"""Run saved lychee JSON fixtures through the workflow's actual inline scripts."""
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parent.parent
workflow = (ROOT / ".github/workflows/linkcheck.yml").read_text(encoding="utf-8")
scripts = re.findall(r"          python3 - <<'PY'\n(.*?)          PY\n", workflow, re.S)
if len(scripts) != 3:
    sys.exit("FAIL: expected preparation and both inline lychee report scripts")
if "          lycheeVersion: v0.24.2\n" not in workflow:
    sys.exit("FAIL: expected the verified lycheeVersion pin")
prepare, *scripts = [textwrap.dedent(script) for script in scripts]

# Recorded with staged lychee 0.24.2 --dump --exclude '[<>]', without network.
# Before: two parent-directory URLs, then two intact URLs. After: four intact URLs.
# The code span remains uncollected. These snapshots do not rerun lychee in the gates.
citation = "https://raw.githubusercontent.com/BerriAI/litellm/v1.85.0/litellm/__init__.py"
escaped = r"https://raw.githubusercontent.com/BerriAI/litellm/v1.85.0/litellm/\_\_init\_\_.py"
dump_after = (citation + "\n") * 4
source = ('---\nversion_basis: {\n  "sources": ["' + citation + '"]\n}\n---\n\n'
          + f"Bare: {citation}\n\n[link]({citation})\n\n<{citation}>\n\n`{citation}`\n")
prepared = ('---\nversion_basis: {\n  "sources": ["' + escaped + '"]\n}\n---\n\n'
            + f"Bare: {escaped}\n\n[link]({escaped})\n\n<{citation}>\n\n`{escaped}`\n")
with tempfile.TemporaryDirectory(prefix="lychee-input-") as directory:
    root = Path(directory)
    (root / "sample.md").write_text(source, encoding="utf-8")
    (root / "sample.html").write_text(source, encoding="utf-8")
    (root / "sample.txt").write_text(source, encoding="utf-8")
    # A second pass must preserve existing escapes and autolinks.
    for _ in range(2):
        result = subprocess.run([sys.executable, "-I", "-B", "-c", prepare],
                                cwd=root, capture_output=True, text=True)
        if result.returncode or (root / "sample.md").read_text(encoding="utf-8") != prepared:
            sys.exit(f"FAIL: Markdown preparation: {result.stderr}")
    for name in ("sample.html", "sample.txt"):
        if (root / name).read_text(encoding="utf-8") != source:
            sys.exit(f"FAIL: preparation changed {name}")
print("  ok    Markdown preparation matches recorded dump input; idempotent; HTML/text retained")

args = shlex.split(re.search(r"          args: >-\n((?:            .*\n)+)", workflow)[1])
excludes = [re.compile(args[i + 1]) for i, arg in enumerate(args) if arg == "--exclude"]
base = "https://api.openai.com/v1"
# Exact match only: no slash, child, query, fragment, alternate scheme or lookalike host.
exclusion_cases = [(base, True)] + [(url, False) for url in (
    base + "/", base + "/models", base + "?docs=1", base + "#docs", base + "0",
    "http://api.openai.com/v1", "https://apiXopenaiXcom/v1",
    "https://api.openai.com.evil.invalid/v1", "https://docs.openai.com/v1",
    "https://api.github.com/user", "https://api.laravel.com/docs/12.x/",
    "https://api.rubyonrails.org/", citation,
)]
for url, expected in exclusion_cases:
    if any(pattern.search(url) for pattern in excludes) != expected:
        sys.exit(f"FAIL: configuration-value exclusion: {url}")
# A newly added component citation must never be hidden by the configuration exclusion.
base_excludes = [pattern for pattern in excludes if pattern.search(base)]
if not base_excludes:
    sys.exit("FAIL: configuration base URL is not excluded")
for path in ROOT.glob("*.md"):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\nversion_basis: "):
        continue
    metadata = json.loads(text.split("\n---", 2)[0].removeprefix("---\nversion_basis: "))
    for component in metadata["components"].values():
        for url in component["sources"].values():
            if any(pattern.search(url) for pattern in base_excludes):
                sys.exit(f"FAIL: configuration exclusion hides citation in {path.name}: {url}")
print(f"  ok    {len(exclusion_cases)} exclusion cases; no component citation excluded")

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
# Synthetic HTTP statuses on the intact citation from the captured dump, not live checks.
for code in (404, 410):
    key = f"citation-{code}"
    fixtures[key] = json.loads(json.dumps(fixtures[str(code)]))
    fixtures[key]["error_map"]["fixture.md"][0]["url"] = dump_after.splitlines()[0]
    cases.append((key, key, "success", "2", 1, False))
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
