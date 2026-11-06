#!/usr/bin/env python3
"""Check that every Python file the Pages build check runs parses as Python 3.11, as far as an
offline check can tell.

scripts/pages-build.sh is the Cloudflare Pages build command, and Cloudflare's build images
document Python 3.11.5 (v2) and 3.13.3 (v3). No 3.11 interpreter is available where this suite
runs, so this test checks what it can offline. For every script pages-build.sh runs with
`python3`, the template's palette gate .baseline/check_palette.py among them (baseline 1.6.0,
whose absence from the script is itself a finding), and every repository module under tools/ or
scripts/ that a checked file reaches, at any depth (by `import`, by `from ... import`, by a call
to __import__ or importlib.import_module whose module name is a string literal, or by a string
literal that is a file name, such as "copy-baseline.py"):

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
    would shift every later row);
  - it imports only the standard library (this interpreter's sys.stdlib_module_names) and
    repository modules under tools/ or scripts/, at any depth in the file, a function body
    included, by an import statement or by a call to __import__ or importlib.import_module
    (IMPORT_FUNCTIONS), and every such call names an absolute module in a nonempty string
    literal, because the Pages build installs nothing: no markdown-it-py, so
    scripts/build-site.py reads README.md's install section with its own standard-library reader.

Before the files, it runs its own cases (SELF_CASES): each of those 4 forms is refused, the
backslash both in a string and as a line continuation (the continuation also after a line
holding a form feed), while a double-quoted key inside a triple-double-quoted f-string, a
single-quoted key inside a double-quoted f-string, a line break inside a triple-quoted f-string's
field (also after a form feed, below a line of backslashes), a backslash in literal text, and
literal backslashes beside escaped `{{` and `}}` (on 1 line, across a backslash-newline, and in a
triple-quoted f-string) pass. Its IMPORT_CASES report a third-party import at the top of a file
and inside a function, and one made by __import__, builtins.__import__ with a keyword argument,
importlib.import_module and import_module under a `from importlib import ... as` name; they report
a call whose module name is a variable or a relative name, and pass standard-library and
repository imports, by statement or by those calls. Its DEP_CASES write a small tree to a
temporary folder and check it as the Pages files are checked: a repository helper that the entry
script loads by __import__, by importlib.import_module in a function, or by import_module under a
`from importlib import ... as` name is checked itself, so its third-party import fails, and a
helper that imports only the standard library passes.

WHAT IT DOES NOT PROVE: that the files run on 3.11. `feature_version` is a best-effort grammar
check, the tokenizer used is this interpreter's, nothing checks that every standard-library name
the files use exists in 3.11 (tomllib does, from 3.11), and nothing is run. An import made by
other means is not seen. These are examples, and the list is not exhaustive: an import function
reached under another name (by assignment or getattr) or by subscript access (such as
__builtins__["__import__"] or vars(builtins)["__import__"]), pkgutil.resolve_name, exec or eval,
runpy, and a module placed in sys.modules. A file that an importlib.util loader loads is checked
only when a checked file holds its file name as a string literal, as above. Exit 0 ok, 1 on a
finding.
"""
import ast
import io
import re
import sys
import tempfile
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "pages-build.sh"
RUN = re.compile(r"^\s*python3\s+(?:-\S+\s+)*([\w./-]+\.py)\b", re.M)
FILE_NAME = re.compile(r"^[\w-]+\.py$")
# The copied template gate the build must run (baseline 1.6.0, SPECIFICATION section 4 item 3).
PALETTE_GATE = ROOT / ".baseline" / "check_palette.py"


def local(name, root=ROOT):
    """The repository file for a module or file name, if tools/ or scripts/ under root holds one."""
    for folder in ("tools", "scripts"):
        path = root / folder / name
        if path.is_file():
            return path
    return None


# The import functions foreign_imports() and deps() also read: the builtin __import__ and
# importlib.import_module, called by these names, as an attribute of any object
# (builtins.__import__, importlib.import_module) or under a name a `from importlib import ... as`
# or `from builtins import ... as` gives them.
IMPORT_FUNCTIONS = ("__import__", "import_module")


def import_names(tree):
    """The names a parsed file can call an IMPORT_FUNCTIONS function by, as a bare name."""
    called = set(IMPORT_FUNCTIONS)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module in ("importlib", "builtins"):
            called |= {a.asname for a in node.names if a.name in IMPORT_FUNCTIONS and a.asname}
    return called


def import_call(node, called):
    """(True, name) when node calls an IMPORT_FUNCTIONS function, name being the module its first
    argument (or its name= keyword) gives as a nonempty string literal naming an absolute module,
    or None when this test cannot tell the module; (False, None) for any other node."""
    if not (isinstance(node, ast.Call) and (
            isinstance(node.func, ast.Name) and node.func.id in called
            or isinstance(node.func, ast.Attribute) and node.func.attr in IMPORT_FUNCTIONS)):
        return False, None
    arg = node.args[0] if node.args else next(
        (k.value for k in node.keywords if k.arg == "name"), None)
    if (isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value
            and not arg.value.startswith(".")):
        return True, arg.value
    return True, None


def deps(tree, root=ROOT):
    """Repository files a parsed module imports, by an import statement or by an IMPORT_FUNCTIONS
    call whose module name is a string literal, or names as a file in a string literal."""
    called, out = import_names(tree), []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out += [local(a.name.split(".")[0] + ".py", root) for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            out.append(local(node.module.split(".")[0] + ".py", root))
        elif (isinstance(node, ast.Constant) and isinstance(node.value, str)
              and FILE_NAME.match(node.value)):
            out.append(local(node.value, root))
        else:
            is_call, name = import_call(node, called)
            if is_call and name:
                out.append(local(name.split(".")[0] + ".py", root))
    return [p for p in out if p]


def foreign_imports(tree, root=ROOT):
    """(line, name) for each module a parsed file imports, at any depth, that is neither in the
    standard library nor a repository module under tools/ or scripts/, by an import statement or
    by a call to an IMPORT_FUNCTIONS function; name is None for such a call whose module name is
    not a nonempty string literal naming an absolute module, whose module this test cannot tell."""
    called, out = import_names(tree), []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            names = [node.module]
        else:
            is_call, name = import_call(node, called)
            if not is_call:
                continue
            if name is None:
                out.append((node.lineno, None))
                continue
            names = [name]
        for name in names:
            top = name.split(".")[0]
            if top not in sys.stdlib_module_names and local(top + ".py", root) is None:
                out.append((node.lineno, top))
    return out


# (source, the names foreign_imports must report)
IMPORT_CASES = (
    ("import json\nfrom pathlib import Path\nimport importlib.util\n", []),
    ("from check_csp_hashes import name_suffix\n", []),
    ("from markdown_it import MarkdownIt\n", ["markdown_it"]),
    ("import json\n\n\ndef parse():\n    import mdurl.parse\n", ["mdurl"]),
    ('import importlib\nimportlib.import_module("json")\n__import__("check_csp_hashes")\n', []),
    ('__import__("markdown_it")\n', ["markdown_it"]),
    ('import builtins\n\n\ndef load():\n    builtins.__import__(name="mdurl")\n', ["mdurl"]),
    ('import importlib\nimportlib.import_module("markdown_it.main")\n', ["markdown_it"]),
    ('from importlib import import_module as load\nload("markdown_it")\n', ["markdown_it"]),
    ('import importlib\nname = "json"\nimportlib.import_module(name)\n', [None]),
    ('import importlib\nimportlib.import_module(".main", "markdown_it")\n', [None]),
)

# (the entry script tools/pages_entry.py, the helper tools/pages_helper.py it loads, and the
# failures scan() must report, each as (file, line, third-party module)): a helper reached only
# through an import function is checked like any other repository module.
DEP_CASES = (
    ('__import__("pages_helper")\n', "import markdown_it\n",
     [("tools/pages_helper.py", 1, "markdown_it")]),
    ('import importlib\n\n\ndef load():\n    return importlib.import_module("pages_helper")\n',
     "import json\n\n\ndef parse():\n    import mdurl\n",
     [("tools/pages_helper.py", 5, "mdurl")]),
    ('from importlib import import_module as load\nload("pages_helper")\n', "import json\n", []),
)


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
    for source, want in IMPORT_CASES:
        found = [name for _, name in foreign_imports(ast.parse(source))]
        if found != want:
            failures.append(f"self-test: {source!r} should report the imports {want} outside the "
                            f"standard library and this repository, not {found}")
    for entry, helper, want in DEP_CASES:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "tools").mkdir()
            (root / "tools" / "pages_entry.py").write_text(entry, encoding="utf-8")
            (root / "tools" / "pages_helper.py").write_text(helper, encoding="utf-8")
            found, seen = scan([root / "tools" / "pages_entry.py"], root)
        expected = [f"{rel}:{line}: imports {name}, which is neither the standard library nor a "
                    f"module of this repository; the Pages build installs nothing"
                    for rel, line, name in want]
        if found != expected or len(seen) != 2:
            failures.append(f"self-test: an entry script {entry!r} that loads a repository helper "
                            f"{helper!r} should check both files and report {expected}, not "
                            f"{found} from {len(seen)} files")
    return failures


def scan(pending, root=ROOT):
    """(failures, files checked) for the files in pending and every repository file under root
    that deps() reaches from them, at any depth."""
    failures, seen, pending = [], set(), list(pending)
    while pending:
        path = pending.pop()
        if path in seen:
            continue
        seen.add(path)
        rel = path.relative_to(root).as_posix()
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=rel, feature_version=(3, 11))
        except FileNotFoundError:
            failures.append(f"{rel} is run by pages-build.sh but does not exist")
            continue
        except SyntaxError as exc:
            failures.append(f"{rel} does not parse as Python 3.11: {exc}")
            continue
        for line, form in pep701_forms(source):
            failures.append(f"{rel}:{line}: an f-string carries {form}, which needs Python 3.12")
        for line, name in foreign_imports(tree, root):
            if name is None:
                failures.append(f"{rel}:{line}: calls __import__ or importlib.import_module with a "
                                f"module name that is not a nonempty string literal naming an "
                                f"absolute module, so this test cannot tell what it imports; the "
                                f"Pages build installs nothing")
            else:
                failures.append(f"{rel}:{line}: imports {name}, which is neither the standard "
                                f"library nor a module of this repository; the Pages build "
                                f"installs nothing")
        pending += deps(tree, root)
    return failures, seen


def main():
    failures = self_test()
    pending = [ROOT / rel for rel in RUN.findall(BUILD.read_text(encoding="utf-8"))]
    if len(pending) < 6:
        failures.append(f"{BUILD.relative_to(ROOT)} runs {len(pending)} Python files; this test "
                        f"expects at least the 6 gates it documents")
    if PALETTE_GATE not in pending:
        failures.append(f"{BUILD.relative_to(ROOT)} does not run "
                        f"{PALETTE_GATE.relative_to(ROOT)}, the palette gate baseline 1.6.0 makes "
                        f"mandatory in the build")
    found, seen = scan(pending)
    failures += found
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {len(SELF_CASES)} f-string, {len(IMPORT_CASES)} import and {len(DEP_CASES)} "
          f"dependency self-test cases, and {len(seen)} Python files that scripts/pages-build.sh "
          f"runs or reaches by an import statement, by an __import__ or importlib.import_module "
          f"call naming the module in a string literal, or by a file name in a string literal, "
          f"parse with feature_version (3, 11), use no 3.12-only f-string form and import only "
          f"the standard library and this repository: "
          f"{', '.join(sorted(p.relative_to(ROOT).as_posix() for p in seen))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
