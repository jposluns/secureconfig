#!/usr/bin/env python3
"""Cases for check_draft.py: each way the staged draft could leak into search or out of /draft/.

Each failing case copies the real draft and the live files the gate reads, makes 1 change and
asserts that the gate exits 1 with a message naming the defect; the pristine copy must pass. A
mutation that no longer applies RAISES, so a page edit cannot turn a case into a pristine run.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
LIVE = ("_headers", "llms.txt", "robots.txt", "index.html", "404.html")


def run(mutate=None):
    d = Path(tempfile.mkdtemp())
    try:
        shutil.copytree(ROOT / "site" / "draft", d / "site" / "draft")
        for name in LIVE:
            shutil.copyfile(ROOT / "site" / name, d / "site" / name)
        if mutate is not None:
            mutate(d)
        r = subprocess.run([sys.executable, "-I", "-B", str(TOOLS / "check_draft.py"), "--root",
                            str(d)], capture_output=True, text=True, timeout=60)
        return r.returncode, (r.stdout + r.stderr).strip()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def edit(rel, old, new):
    def mutate(d):
        path = d / rel
        text = path.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"mutation {old!r} no longer matches {rel}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return mutate


def append(rel, extra):
    def mutate(d):
        path = d / rel
        path.write_text(path.read_text(encoding="utf-8") + extra, encoding="utf-8")
    return mutate


def write(rel, text):
    def mutate(d):
        (d / rel).write_text(text, encoding="utf-8")
    return mutate


HOME = "site/draft/index.html"
GUIDES = "site/draft/guides/index.html"
META = '<meta name="robots" content="noindex, nofollow">'
CASES = [
    ("a draft page without the robots meta", edit(HOME, META + "\n", ""), "exactly 1"),
    ("a draft page with a second robots meta", edit(HOME, META, META + META), "exactly 1"),
    ("a link to a live page", edit(HOME, 'href="/draft/guides/"', 'href="/guides/"'),
     "outside the base path"),
    ("a stylesheet loaded from the live root",
     edit(HOME, 'href="/draft/assets/baseline/baseline.css"', 'href="/assets/baseline.css"'),
     "outside the base path"),
    ("a relative link", edit(HOME, 'href="/draft/guides/"', 'href="guides/"'), "relative path"),
    ("a link to a draft page that does not exist",
     edit(HOME, 'href="/draft/guides/"', 'href="/draft/nowhere/"'), "names no file"),
    ("an absolute link to this site's own host",
     edit(HOME, 'href="/draft/guides/"', 'href="https://secureconfig.ai/"'), "own host"),
    ("a javascript: URL", edit(HOME, 'href="/draft/guides/"', 'href="javascript:void(0)"'),
     "javascript: scheme"),
    ("a scheme-relative URL", edit(HOME, 'href="/draft/guides/"', 'href="//example.net/"'),
     "scheme-relative"),
    ("a new-tab link without the hidden hint",
     edit(GUIDES, 'free-certificates<span class="vh"> (opens in a new tab)</span>', "free-certificates"),
     "does not say so"),
    ("the /draft/* rule without X-Robots-Tag",
     edit("site/_headers", "  X-Robots-Tag: noindex\n", ""), "X-Robots-Tag: noindex"),
    ("a second /draft/* rule", append("site/_headers", "\n/draft/*\n  X-Robots-Tag: noindex\n"),
     "2 /draft/* rules"),
    ("llms.txt naming the draft", append("site/llms.txt", "\n- [draft](https://secureconfig.ai/draft/)\n"),
     "site/llms.txt names a /draft path"),
    ("a live page linking the draft", edit("site/index.html", "</footer>",
                                           '<a href="/draft/">draft</a></footer>'),
     "is a live page and names a /draft path"),
    ("a stylesheet url() outside the draft",
     write("site/draft/assets/site.css", ".statement { --sw: 14; }\n.x { background: url(/logo.svg); }\n"),
     "is not a relative path"),
    ("site.css setting another property",
     write("site/draft/assets/site.css", ".statement { --sw: 14; color: red; }\n"), "may set only"),
    ("an inner page linking the Licence page",
     edit(GUIDES, '<a href="/draft/for-ai/">', '<a href="/draft/license/">Licence</a><a href="/draft/for-ai/">'),
     "only the landing page"),
    ("the pristine draft", None, "8 draft pages"),
]


def main():
    failures = []
    for desc, mutate, expected in CASES:
        want = 0 if mutate is None else 1
        rc, out = run(mutate)
        if rc != want:
            failures.append(f"{desc}: expected exit {want}, got {rc}: {out!r}")
        elif expected not in out:
            failures.append(f"{desc}: expected the output to contain {expected!r}: {out!r}")
        if "Traceback (most recent call last):" in out:
            failures.append(f"{desc}: the gate crashed: {out!r}")
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {len(CASES)} draft noindex and self-containment cases "
          f"({len(CASES) - 1} refusals and the pristine draft)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
