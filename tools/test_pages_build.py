#!/usr/bin/env python3
"""Check that every Python file the Pages build check runs parses as Python 3.11.

scripts/pages-build.sh is the Cloudflare Pages build command, and Cloudflare's build images
document Python 3.11.5 (v2) and 3.13.3 (v3). No 3.11 interpreter is available where this suite
runs, so this test checks what it can offline: every script pages-build.sh runs with `python3`,
and every repository module those scripts import (by `import`, `from ... import`, or a file name
they load, such as scripts/copy-baseline.py), parses with `ast.parse(..., feature_version=(3, 11))`
and reuses no f-string quote inside a replacement field (PEP 701, Python 3.12), which
`feature_version` does not catch.

WHAT IT DOES NOT PROVE: that the files run on 3.11. `feature_version` is a best-effort grammar check;
it does not check that every standard-library name the files use exists in 3.11 (tomllib does, from
3.11), and it runs nothing. Exit 0 ok, 1 on a finding.
"""
import ast
import io
import re
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "pages-build.sh"
RUN = re.compile(r"^\s*python3\s+(?:-\S+\s+)*([\w./-]+\.py)\b", re.M)
FILE_NAME = re.compile(r"^[\w-]+\.py$")


def local(name):
    """The repository file for a module or file name, if tools/ or scripts/ holds one."""
    for folder in ("tools", "scripts"):
        path = ROOT / folder / name
        if path.is_file():
            return path
    return None


def deps(tree):
    """Repository files a parsed module imports or names as a file."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out += [local(a.name.split(".")[0] + ".py") for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            out.append(local(node.module.split(".")[0] + ".py"))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and FILE_NAME.match(node.value):
            out.append(local(node.value))
    return [p for p in out if p]


def pep701_reuse(text):
    """Lines where an f-string's replacement field reuses the f-string's own quote, which parses
    only from Python 3.12 (PEP 701) and which `feature_version` does not catch."""
    out, stack = [], []
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        if tok.type == tokenize.FSTRING_START:
            quote = tok.string.lstrip("fFrRbB")[:1]
            if stack and quote in stack:
                out.append(tok.start[0])
            stack.append(quote)
        elif tok.type == tokenize.FSTRING_END:
            stack.pop()
        elif tok.type == tokenize.STRING and stack:
            quote = tok.string.lstrip("rRbBuU")[:1]
            if quote in stack:
                out.append(tok.start[0])
    return out


def main():
    failures, seen = [], set()
    pending = [ROOT / rel for rel in RUN.findall(BUILD.read_text(encoding="utf-8"))]
    if len(pending) < 5:
        failures.append(f"{BUILD.relative_to(ROOT)} runs {len(pending)} Python files; this test "
                        f"expects at least the 5 gates it documents")
    while pending:
        path = pending.pop()
        if path in seen:
            continue
        seen.add(path)
        rel = path.relative_to(ROOT)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(rel),
                             feature_version=(3, 11))
        except FileNotFoundError:
            failures.append(f"{rel} is run by pages-build.sh but does not exist")
            continue
        except SyntaxError as exc:
            failures.append(f"{rel} does not parse as Python 3.11: {exc}")
            continue
        for line in pep701_reuse(path.read_text(encoding="utf-8")):
            failures.append(f"{rel}:{line}: an f-string reuses its own quote inside a replacement "
                            f"field, which needs Python 3.12")
        pending += deps(tree)
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {len(seen)} Python files that scripts/pages-build.sh runs or imports parse as "
          f"Python 3.11: {', '.join(sorted(p.relative_to(ROOT).as_posix() for p in seen))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
