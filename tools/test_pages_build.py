#!/usr/bin/env python3
"""Check that every Python file the Pages build check runs parses as Python 3.11, as far as an
offline check can tell.

scripts/pages-build.sh is the Cloudflare Pages build command, and Cloudflare's build images
document Python 3.11.5 (v2) and 3.13.3 (v3). No 3.11 interpreter is available where this suite
runs, so this test checks what it can offline. For every script pages-build.sh runs with
`python3`, and every repository module those scripts import (by `import`, `from ... import`, or a
file name they load, such as scripts/copy-baseline.py):

  - the file parses with `ast.parse(..., feature_version=(3, 11))`;
  - it uses none of the f-string forms that Python 3.12 (PEP 701) added and that
    `feature_version` does not catch: a string literal in a replacement field that reuses an
    enclosing f-string's delimiter (its quote character for a single-quoted f-string, the same
    3-quote delimiter for a triple-quoted one), a backslash anywhere in a replacement field (in a
    token, or in the source text between 2 tokens, which is where a line continuation sits), a `#`
    comment in a replacement field, or a line break in a replacement field of a single-quoted
    f-string. The source text between 2 tokens is read from the file's lines as the tokenizer
    reads them, broken only after `\\n` (`str.splitlines` also breaks at `\\r` and `\\r\\n`, and at
    `\\x0b`, `\\x0c`, `\\x1c` to `\\x1e`, U+0085, U+2028 and U+2029, any of which but `\\r\\n`
    would shift every later row).

Before the files, it runs its own cases (SELF_CASES): each of those 4 forms is refused, the
backslash both in a string and as a line continuation (the continuation also after a line
holding a form feed), while a double-quoted key inside a triple-double-quoted f-string, a
single-quoted key inside a double-quoted f-string, a line break inside a triple-quoted f-string's
field (also after a form feed, below a line of backslashes), a backslash in literal text, and
literal backslashes beside escaped `{{` and `}}` (on 1 line, across a backslash-newline, and in a
triple-quoted f-string) pass.

WHAT IT DOES NOT PROVE: that the files run on 3.11. `feature_version` is a best-effort grammar check,
the tokenizer used is this interpreter's, nothing checks that every standard-library name the files
use exists in 3.11 (tomllib does, from 3.11), and nothing is run. Exit 0 ok, 1 on a finding.
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


def delimiter(token_text):
    """A string token's full delimiter (3 quotes or 1), after any prefix letters."""
    body = token_text.lstrip("fFrRbBuUtT")
    return body[:3] if body[:3] in ('"""', "'''") else body[:1]


def pep701_forms(text):
    """(line, form) for each Python 3.12-only f-string form in text; see the docstring."""
    out, stack, prev = [], [], None
    # The rows the tokenizer counts: broken only after \n, unlike str.splitlines.
    lines = io.StringIO(text).readlines()

    def between(start, end):
        """The source text between 2 token positions (rows 1-based, columns 0-based)."""
        (r1, c1), (r2, c2) = start, end
        if r1 == r2:
            return lines[r1 - 1][c1:c2]
        return lines[r1 - 1][c1:] + "".join(lines[r1:r2 - 1]) + lines[r2 - 1][:c2]

    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        if not stack:
            if tok.type == tokenize.FSTRING_START:
                stack.append(delimiter(tok.string))
            prev = tok
            continue
        line = tok.start[0]
        # A backslash between 2 tokens inside an f-string is a line continuation in a replacement
        # field, which produces no token of its own.
        if prev is not None and "\\" in between(prev.end, tok.start):
            out.append((line, "a backslash in a replacement field"))
        prev = tok
        if tok.type == tokenize.FSTRING_END:
            stack.pop()
        elif tok.type == tokenize.FSTRING_MIDDLE:
            # Literal text of a nested f-string sits inside the outer f-string's replacement field.
            if len(stack) > 1 and "\\" in tok.string:
                out.append((line, "a backslash in a replacement field"))
        elif tok.type in (tokenize.STRING, tokenize.FSTRING_START):
            d = delimiter(tok.string)
            if any(d == outer if len(outer) == 3 else d[0] == outer for outer in stack):
                out.append((line, "a string that reuses an enclosing f-string's delimiter"))
            if "\\" in tok.string:
                out.append((line, "a backslash in a replacement field"))
            if tok.type == tokenize.FSTRING_START:
                stack.append(d)
        elif tok.type == tokenize.COMMENT:
            out.append((line, "a # comment in a replacement field"))
        elif tok.type == tokenize.NL:
            if any(len(outer) == 1 for outer in stack):
                out.append((line, "a line break in a replacement field of a single-quoted f-string"))
        elif "\\" in tok.string:
            out.append((line, "a backslash in a replacement field"))
    return out


SELF_CASES = (
    ('x = {"a": 1}\ny = f"{x["a"]}"\n', "reuses"),
    ("y = f\"{'\\\\n'.join([])}\"\n", "backslash"),
    ('x = 1\ny = f"""{x  # note\n}"""\n', "comment"),
    ('x = 1\ny = f"{x\n+ 1}"\n', "line break"),
    ('x = 1\ny = f"""{x + \\\n1}"""\n', "backslash"),
    ('x = {"a": 1}\ny = f"""{x["a"]}"""\n', None),
    ("x = {'a': 1}\ny = f\"{x['a']}\"\n", None),
    ('x = 1\ny = f"""{x\n+ 1}"""\n', None),
    ('x = 1\ny = f"a\\n{x}b"\n', None),
    # A form feed before an f-string: str.splitlines rows would read the line above.
    ('x = 1\n\x0cy = "\\\\\\\\\\\\\\\\"\nz = f"""{x\n+ 1}"""\n', None),
    ('x = 1\n\x0cy = 2\nz = f"""{x + \\\n1}"""\n', "backslash"),
    # Literal backslashes beside escaped braces, which the tokenizer splits into pieces.
    ('x = 1\ny = f"{x}{{\\\\}}{x}"\n', None),
    ('x = 1\ny = f"a{{\\\n}}\\\\{x}"\n', None),
    ('x = 1\ny = f"""{{\\\n{x}}}\\\\"""\n', None),
)


def self_test():
    failures = []
    for source, want in SELF_CASES:
        found = [form for _, form in pep701_forms(source)]
        if want is None and found:
            failures.append(f"self-test: {source!r} parses on 3.11 but was flagged: {found}")
        elif want is not None and not any(want in form for form in found):
            failures.append(f"self-test: {source!r} needs 3.12 ({want}) but was not flagged: {found}")
    return failures


def main():
    failures, seen = self_test(), set()
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
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(rel), feature_version=(3, 11))
        except FileNotFoundError:
            failures.append(f"{rel} is run by pages-build.sh but does not exist")
            continue
        except SyntaxError as exc:
            failures.append(f"{rel} does not parse as Python 3.11: {exc}")
            continue
        for line, form in pep701_forms(source):
            failures.append(f"{rel}:{line}: an f-string carries {form}, which needs Python 3.12")
        pending += deps(tree)
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {len(SELF_CASES)} f-string self-test cases, and {len(seen)} Python files that "
          f"scripts/pages-build.sh runs or imports parse with feature_version (3, 11) and use no "
          f"3.12-only f-string form: {', '.join(sorted(p.relative_to(ROOT).as_posix() for p in seen))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
