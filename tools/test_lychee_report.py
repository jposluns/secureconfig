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

# Recorded with lychee 0.24.2 --dump --exclude '[<>]' on 2026-10-12, offline.
# Each front-matter row stores input, prepared text, before dump and after dump.
# These tests prove preparation bytes and idempotence for these inputs and exercise
# the report scripts with saved JSON. They do not rerun lychee or prove URL liveness.
URLS = (
    "https://github.com/qa/__init__.py",
    "https://github.com/qa/p?q=__init__.py",
    "https://github.com/qa/p#__init__.py",
)
FRONT = '---\nversion_basis: {{\n  "sources": ["{u}"]\n}}\n---\n'
ESCAPED = FRONT.replace('{u}', '{e}')
# Empty dump strings mean that the recording extracted no URL.
preparation_cases = [
    ('front-matter', FRONT, ESCAPED, '{b}\n', '{u}\n'),
    ('compact-layout', '---\nversion_basis: {{"sources": ["{u}"]}}\n---\n', None, '', ''),
    ('unknown-layout', FRONT.replace('version_basis:', 'other:'), None, '{b}\n', '{b}\n'),
    ('already-escaped', ESCAPED, None, '{u}\n', '{u}\n'),
    ('ending-underscore', FRONT.replace('{u}', '{u}_'), None, '{b}\n', '{b}\n'),
    ('invalid-json', FRONT.replace('["{u}"]', '["{u}",]'), None, '{b}\n', '{b}\n'),
    ('unclosed-front-matter', FRONT.removesuffix('---\n'), None, '{b}\n', '{b}\n'),
    ('no-front-matter', 'See {u}\n', None, '{b}\n', '{b}\n'),
    ('quoted-match-required', FRONT.replace('{u}', 'See {u}'), None, '{b}\n', '{b}\n'),
    ('stop-less-than', FRONT.replace('{u}', '<tag> {u}'), None, '{b}\n', '{b}\n'),
    ('stop-greater-than', FRONT.replace('{u}', '> {u}'), None, '{b}\n', '{b}\n'),
    ('stop-backtick', FRONT.replace('{u}', '` {u}'), None, '{b}\n', '{b}\n'),
]
body_cases = [
    ('body-whitespace', 'See {u}\n'),
    ('body-list', '- {u}\n'),
    ('body-table', '| URL | Other |\n| --- | --- |\n| {u} | next_cell |\n'),
    ('round1-emphasis-regression', '_{u}_\n'),
    ('round1-closing-emphasis-regression', '_https://github.com/qa/plain_\n'),
    ('round1-href-double-regression', '<a href="{u}">x</a>\n'),
    ('round1-href-single-regression', "<a href='{u}'>x</a>\n"),
    ('body-code-span', '`{u}`\n'),
    ('body-fenced-block', '```text\n{u}\n```\n'),
    ('body-autolink', '<{u}>\n'),
    ('body-explicit-link', '[link]({u})\n'),
]
recorded = []
body_count = 0
with tempfile.TemporaryDirectory(prefix="lychee-input-") as directory:
    root = Path(directory)

    def check(name, source, expected):
        for suffix in ("md", "html", "txt"):
            (root / f"sample.{suffix}").write_bytes(source)
        for iteration in range(2):
            result = subprocess.run([sys.executable, "-I", "-B", "-c", prepare],
                                    cwd=root, capture_output=True, text=True)
            if result.returncode or (root / "sample.md").read_bytes() != expected:
                sys.exit(f"FAIL: preparation {name}, pass {iteration + 1}: {result.stderr}")
        for suffix in ("html", "txt"):
            if (root / f"sample.{suffix}").read_bytes() != source:
                sys.exit(f"FAIL: preparation changed {suffix}")

    for position, url in zip(("path", "query", "fragment"), URLS):
        values = dict(u=url, e=url.replace("_", r"\_"), b=url.split("__")[0])
        for name, source, prepared, before, after in preparation_cases:
            source_bytes = source.format(**values).encode("utf-8")
            expected = (source if prepared is None else prepared).format(**values).encode("utf-8")
            recorded.append((before.format(**values), after.format(**values)))
            check(f"{name}/{position}", source_bytes, expected)
        for name, body in body_cases:
            body_bytes = body.format(**values).encode("utf-8")
            # Exercise each body alone and after front matter that actually changes.
            for prefix, prepared_prefix in ((b"", b""), (
                    FRONT.format(**values).encode(), ESCAPED.format(**values).encode())):
                check(f"{name}/{position}", prefix + body_bytes, prepared_prefix + body_bytes)
                body_count += 1
    # CRLF front matter is an unknown layout; mixed-ending bodies remain byte-exact.
    for source, expected in (
        (FRONT.format(**values).replace("\n", "\r\n").encode(),
         FRONT.format(**values).replace("\n", "\r\n").encode()),
        (FRONT.format(**values).encode() + b"See https://github.com/qa/a_b\r\n",
         ESCAPED.format(**values).encode() + b"See https://github.com/qa/a_b\r\n"),
    ):
        check("CRLF", source, expected)
    for defect in ("non-UTF-8", "unreadable"):
        sample = root / "sample.md"
        sample.unlink()
        if defect == "non-UTF-8":
            sample.write_bytes(b"\xff")
        else:
            sample.symlink_to(root / "missing-target")
        result = subprocess.run([sys.executable, "-I", "-B", "-c", prepare],
                                cwd=root, capture_output=True, text=True)
        if not result.returncode or not result.stderr:
            sys.exit(f"FAIL: preparation did not fail loudly on {defect}")
print(f"  ok    {len(recorded)} recorded preparation cases; {body_count} body cases; "
      "2 CRLF cases; all twice; HTML/text retained; 2 input failures surfaced")
# Use a restored citation present in a saved after-dump for synthetic status fixtures.
citation = recorded[0][1].strip()

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
    fixtures[key]["error_map"]["fixture.md"][0]["url"] = citation
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
