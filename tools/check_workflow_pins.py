#!/usr/bin/env python3
r"""Check that every `uses:` in the workflows, and in any action.yml they can call, is pinned to a commit.

WHY: a tag or branch is a pointer its owner can move, so `uses: actions/checkout@v4` runs whatever
that pointer names on the day of the run. Row 3.17 (#348) replaced every floating tag in
`.github/workflows/` with a full commit SHA and a trailing `# vX.Y.Z` naming the release the SHA was
taken from. Nothing held that in place: the next `uses: some/action@v2` would have merged green.
This gate is row 3.21.

WHAT IT ACCEPTS, and nothing else:

  - a remote action or reusable workflow, `owner/repo[/path]@<ref>  # vX.Y.Z`, where `<ref>` is
    exactly 40 LOWERCASE hex characters and the comment is exactly `# v` and three dot-separated
    numbers. A shorter or longer SHA, uppercase hex, a tag, a branch, an expression, or a missing or
    differently written comment is a finding. Lowercase is required because it is the form git
    prints; whether the runner reads an uppercase string as a commit or as a ref name is not
    something this gate relies on;
  - a Docker action, `docker://<image>[:<tag>]@sha256:<64 lowercase hex>`, pinned by digest. A tag
    alone is a finding. A trailing comment is allowed and not checked;
  - a local action or local reusable workflow, `./<path>`, with no comment required, because it is
    this repository's own code at the commit being run. The path must resolve inside the
    repository to a workflow file or to an `action.yml`/`action.yaml` that this gate also reads,
    so a local composite action cannot carry a floating tag one hop away.

WHICH FILES: every `.yml`/`.yaml` (any case) under `.github/workflows/`, subdirectories included,
and every file named `action.yml`/`action.yaml` (any case) anywhere in the tree outside `.git`,
`node_modules` and `__pycache__`. That is a superset of what GitHub reads, so a file GitHub ignores
is still held to the rule, which costs nothing. No workflow directory, no workflow file, or no
`uses:` anywhere, fails: a gate that checked nothing must not print a pass.

WHY IT READS LINES AND NOT YAML. The suite is standard library only and has no YAML parser, and
these are short hand-written files. A line reader is sound here because it does not try to model
YAML. It models a small, declared subset and refuses every line outside it. Each line outside a
block scalar's content must be one of:

  - blank, or a comment;
  - `[- ...]key: value`, where the key is plain (`[A-Za-z0-9_][A-Za-z0-9_.-]*`) or a quoted
    string of that shape with no backslash, and the value is empty, a block scalar header, a plain
    scalar, a quoted scalar closed on the same line, or a flow collection closed on the same line
    with each bracket closed by its own kind;
  - `- value`, with the same value forms.

Everything else is refused as outside the model: a tab outside a block scalar, an anchor (`&`), an
alias (`*`), a tag (`!`), a merge key, an explicit key (`?`), a directive, a second document marker,
a quoted scalar or flow collection that runs past the end of its line, a flow collection closed by
the wrong kind of bracket (`[a}`), a double-quoted scalar carrying a backslash inside a flow
collection, a plain scalar that continues onto a more indented line, a block scalar with an
explicit indentation indicator, and a control or Unicode line-separator character that one YAML
version treats as a line break and another does not.
CRLF line endings are read as LF; a lone CR is refused.

`uses` is then held to a stricter rule. A key spelled `uses` in any case other than exactly `uses`,
a quoted key containing the word, the word inside a quoted scalar, a flow collection or a block
scalar's content, and a `uses:` whose value is empty, quoted, a block scalar or a flow collection are
all refused. A quoted or flow `uses` is either a key GitHub reads as `uses` or text that looks like
one, and this gate refuses both rather than tell them apart. An escape spells the key without the
word: YAML reads `"u\x73es"`, `"\u0075ses"`, `"us\U00000065s"` and every other escape of those
letters as `uses`. So a quoted key in block context must have the plain key shape, which has no
backslash, and inside a flow collection every double-quoted scalar carrying a backslash is refused,
key or value, rather than decide which it is. A single-quoted scalar has no escapes, and a
double-quoted scalar in block context is a key only when a `:` follows it, which the key rule above
covers; any other text after it is refused. The word in a plain scalar or a comment line is text
and is not refused, because a plain scalar cannot carry a nested key (a `: ` inside one is refused)
and a comment line is nothing to YAML.

WHY READING PAST BLOCK SCALARS IS SAFE. The workflows carry `run: |` and `args: >-` blocks of
shell. Those lines are scalar content, not keys, so the gate reads past them, and the only fail-open
a line reader could have is reading past a line that is really structure. YAML fixes a block scalar's
extent by indentation alone: its content indentation is the first non-blank line's, which must be
deeper than the key (or dash) that opened it, and the content runs until a non-blank line is less
indented. The gate applies exactly that rule. A line that is less indented than the content but
deeper than the key is invalid YAML and is refused rather than guessed at. As a second guard, the
word `uses` anywhere in a block scalar's content is refused too, so even a wrong reading of a
block's extent cannot hide a `uses:` key; shell that must say the word goes in a step's plain text
or in a script file. Comment detection follows YAML: `#` starts a comment only outside a quoted
scalar and only after whitespace or at the start of the line.

WHAT IT DOES NOT PROVE, stated rather than left to be found:

  - that a SHA exists, lies in the named repository's history, or is the commit the named release
    points at. All three need the network, and the gates are offline by design. The comment is a
    claim a reviewer checks when a pin is bumped;
  - anything about `container:`, `services:` or an action's `runs.image`, which name Docker images
    through keys other than `uses:` and may float by tag;
  - what a pinned action itself fetches at run time (its own unpinned actions, images or downloads);
  - that a key named `uses` is a step's action: an action input named `uses` under `with:` is held
    to the same rule and fails it, which is the fail-closed direction.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _walk import walk_files  # noqa: E402  fail-closed tree walk (os.walk, not rglob)

WORKFLOWS = Path(".github") / "workflows"
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
YAML_SUFFIXES = (".yml", ".yaml")
ACTION_FILES = ("action.yml", "action.yaml")

KEY = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]*")
USES_WORD = re.compile(r"\buses\b", re.I)
SHA = re.compile(r"[0-9a-f]{40}")
HEX = re.compile(r"[0-9a-fA-F]+")
REMOTE = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*")
DOCKER = re.compile(r"docker://[A-Za-z0-9][A-Za-z0-9._:/-]*@sha256:[0-9a-f]{64}")
RELEASE_COMMENT = re.compile(r"# v[0-9]+\.[0-9]+\.[0-9]+")
BLOCK_HEADER = re.compile(r"[|>][+-]?[ \t]*(?:#.*)?")
# Characters one YAML version reads as a line break and another does not (NEL, LS, PS), a BOM, and
# the C0/C1 controls other than tab and newline. Reading these as ordinary text could put a key on a
# line this gate never sees. Built with chr() so this source file stays plain ASCII.
FORBIDDEN_CHARS = re.compile("[\x00-\x08\x0b-\x1f\x7f-\x9f"
                             + chr(0x2028) + chr(0x2029) + chr(0xFEFF) + "]")


class OutsideModel(Exception):
    """A line this gate cannot classify. Always a finding."""


def quote_end(s, i):
    """Index of the quote closing the scalar that opens at s[i], or None if the line ends first."""
    q, j = s[i], i + 1
    while j < len(s):
        if q == '"' and s[j] == "\\":
            j += 2
            continue
        if s[j] == q:
            if q == "'" and j + 1 < len(s) and s[j + 1] == "'":
                j += 2
                continue
            return j
        j += 1
    return None


def trailing_comment(rest, what):
    """The comment after a closed scalar or collection, or refuse text that follows it."""
    stripped = rest.lstrip(" ")
    if not stripped:
        return None
    if stripped.startswith("#") and len(stripped) < len(rest):
        return stripped
    raise OutsideModel(f"text follows {what} on the same line")


def flow_end(s):
    """Index just past the flow collection opening at s[0], refusing what the model excludes."""
    openers, i, at_start = [], 0, True
    while i < len(s):
        ch = s[i]
        if at_start and ch in "\"'":
            j = quote_end(s, i)
            if j is None:
                raise OutsideModel("a quoted scalar inside a flow collection runs past the end of "
                                   "its line")
            # An escape spells a key the word check never sees: YAML reads "u\x73es" as `uses`.
            if ch == '"' and "\\" in s[i:j]:
                raise OutsideModel("a double-quoted scalar with a backslash escape inside a flow "
                                   "collection, which can spell a key this gate cannot read")
            i, at_start = j + 1, False
            continue
        if ch in "[{":
            openers.append(ch)
            at_start = True
        elif ch in "]}":
            if openers.pop() != {"]": "[", "}": "{"}[ch]:
                raise OutsideModel(f"a flow collection closed by {ch!r}, which does not match "
                                   f"the bracket that opened it")
            at_start = False
            if not openers:
                return i + 1
        elif ch in ",:":
            at_start = True
        elif ch == "#" and s[i - 1] == " ":
            break
        elif ch != " ":
            if at_start and ch in "&*!?|>%@`":
                raise OutsideModel(f"a flow collection contains the indicator {ch!r}, an "
                                   f"anchor, alias, tag or other construct this gate does not model")
            at_start = False
        i += 1
    raise OutsideModel("a flow collection runs past the end of its line")


def node(s):
    """Classify the node text starting at s (at a node start, leading spaces removed).

    Returns (kind, text, comment), kind one of empty, block, quoted, flow, plain.
    """
    if not s:
        return "empty", "", None
    ch = s[0]
    if ch == "#":
        return "empty", "", s
    if ch == "&":
        raise OutsideModel("an anchor (&), which lets one node stand in for another elsewhere in "
                           "the file")
    if ch == "*":
        raise OutsideModel("an alias (*), which repeats a node defined elsewhere in the file")
    if ch == "!":
        raise OutsideModel("a tag (!), which changes how a node is read")
    if ch in "?%@`":
        raise OutsideModel(f"a node starting with {ch!r}, an explicit key or reserved "
                           f"indicator")
    if ch in "|>":
        if not BLOCK_HEADER.fullmatch(s):
            raise OutsideModel("a block scalar header with an indentation indicator or trailing "
                               "text; only |, >, and their + or - chomping forms are modelled")
        return "block", "", None
    if ch in "\"'":
        j = quote_end(s, 0)
        if j is None:
            raise OutsideModel("a quoted scalar that runs past the end of its line")
        return "quoted", s[: j + 1], trailing_comment(s[j + 1:], "a quoted scalar")
    if ch in "[{":
        j = flow_end(s)
        return "flow", s[:j], trailing_comment(s[j:], "a flow collection")
    m = re.search(r"(?:^|[ \t])#", s)
    text, comment = (s[: m.start()], s[m.start():].lstrip(" \t")) if m else (s, None)
    text = text.rstrip(" ")
    if ": " in text or text.endswith(":"):
        raise OutsideModel("a plain scalar containing ': ', which is a nested mapping or an error")
    return "plain", text, comment


def parse_line(line):
    """Split one structural line. Returns None for a blank or comment line, else a dict."""
    if "\t" in line:
        raise OutsideModel("a tab, which YAML forbids in indentation and this gate does not model "
                           "anywhere outside a block scalar")
    body = line.lstrip(" ")
    if not body or body.startswith("#"):
        return None
    col, parent = len(line) - len(body), None
    while body == "-" or body.startswith("- "):
        parent = col
        rest = body[1:].lstrip(" ")
        col += len(body) - len(rest)
        body = rest
    key = None
    if body.startswith(("'", '"')):
        j = quote_end(body, 0)
        after = body[j + 1:] if j is not None else ""
        if j is not None and re.match(r" *:(?: |$)", after):
            raw = body[1:j]
            if USES_WORD.search(raw):
                raise OutsideModel("a quoted key naming uses; write the key plain, as `uses:`")
            if "\\" in raw or not KEY.fullmatch(raw):
                raise OutsideModel("a quoted key this gate cannot read as a plain name")
            key, body = raw, after.lstrip(" ")[1:]
    else:
        m = KEY.match(body)
        if m and re.match(r":(?: |$)", body[m.end():]):
            key, body = m.group(), body[m.end() + 1:]
    if key is not None:
        parent = col
    elif parent is None:
        raise OutsideModel("a line that is neither a key nor a sequence entry, which is how a "
                           "multi-line plain scalar continues")
    kind, text, comment = node(body.lstrip(" "))
    return {"key": key, "parent": parent, "kind": kind, "text": text, "comment": comment}


def check_uses(value, comment, where, targets):
    """Findings for one plain, single-line `uses:` value. Local paths are queued for resolution."""
    if "#" in value:
        return [f"{where}: `uses: {value}` has a # with no space before it, so YAML "
                f"reads it as part of the value and not as a comment"]
    if value.startswith("./"):
        targets.append((where, value))
        return []
    if value.startswith("docker://"):
        if not DOCKER.fullmatch(value):
            return [f"{where}: `uses: {value}` is a Docker image not pinned by an "
                    f"@sha256: digest of 64 lowercase hex characters; a tag can be repushed"]
        return []
    name, at, ref = value.partition("@")
    if not at or not REMOTE.fullmatch(name):
        return [f"{where}: `uses: {value}` is not an owner/repo[/path]@ref, a "
                f"./local path or a docker:// image"]
    if not SHA.fullmatch(ref):
        if HEX.fullmatch(ref) and len(ref) == 40:
            why = "uses uppercase hex; write the SHA in lowercase, as git prints it"
        elif HEX.fullmatch(ref) and len(ref) < 40:
            why = f"is a SHA shorter than 40 characters ({len(ref)}); pin the full commit SHA"
        elif HEX.fullmatch(ref):
            why = f"is {len(ref)} hex characters, not a 40-character commit SHA"
        else:
            why = ("is a tag, branch name or expression, which its owner can move; pin the full "
                   "commit SHA")
        return [f"{where}: `uses: {value}`: the ref {ref!r} {why}"]
    if comment is None:
        return [f"{where}: `uses: {value}` has no release comment; write "
                f"`  # vX.Y.Z` naming the release the SHA was taken from"]
    if not RELEASE_COMMENT.fullmatch(comment):
        return [f"{where}: `uses: {value}` has a malformed release comment "
                f"{comment!r}; write exactly `# vX.Y.Z`"]
    return []


def skip_block(lines, i, parent, path, findings):
    """Index of the first line after a block scalar's content, or None after a refusal.

    The content is read for the word `uses`, which is refused: see the docstring.
    """
    j = i
    while j < len(lines) and not lines[j].strip(" \t"):
        j += 1
    if j == len(lines):
        return j
    content = len(lines[j]) - len(lines[j].lstrip(" "))
    if content <= parent:
        return j
    while j < len(lines):
        line = lines[j]
        if line.strip(" \t"):
            indent = len(line) - len(line.lstrip(" "))
            if indent < content:
                if indent > parent:
                    findings.append(f"{path}:{j + 1}: a line less indented than its "
                                    f"block scalar's content but more than the key that opened "
                                    f"it, which is invalid YAML")
                    return None
                return j
            if USES_WORD.search(line):
                findings.append(f"{path}:{j + 1}: the word `uses` inside a block "
                                f"scalar, which this gate refuses rather than trust its reading of "
                                f"where the block ends; move that text out of the block")
                return None
        j += 1
    return j


def scan(text, path, targets, counts):
    """Findings for one file's text. A refusal stops the file: what follows it is unmodelled."""
    text = text.replace("\r\n", "\n")
    bad = FORBIDDEN_CHARS.search(text)
    if bad:
        line = text[: bad.start()].count("\n") + 1
        return [f"{path}:{line}: character U+{ord(bad.group()):04X} is outside "
                f"this gate's model; some YAML readers treat it as a line break"]
    lines = text.split("\n")
    findings, i, seen_content, continuation_limit = [], 0, False, None
    while i < len(lines):
        line, where = lines[i], f"{path}:{i + 1}"
        body = line.strip(" ")
        if continuation_limit is not None and body and not body.startswith("#"):
            if len(line) - len(line.lstrip(" ")) > continuation_limit:
                findings.append(f"{where}: a scalar from an earlier line continues onto "
                                f"this more indented line, which this gate does not model")
                return findings
            continuation_limit = None
        if body.startswith("%") or body in ("---", "...") or body.startswith(("--- ", "... ")):
            if body == "---" and not seen_content:
                seen_content = True
                i += 1
                continue
            findings.append(f"{where}: a YAML directive or document marker; this gate "
                            f"models one document with at most a leading ---")
            return findings
        try:
            parsed = parse_line(line)
        except OutsideModel as exc:
            findings.append(f"{where}: outside what this gate can read ({exc}); "
                            f"rewrite the line in the plain form the gate models, or extend the "
                            f"gate deliberately")
            return findings
        if parsed is None:
            i += 1
            continue
        seen_content = True
        key, kind = parsed["key"], parsed["kind"]
        if key is not None and key != "uses" and key.lower() == "uses":
            findings.append(f"{where}: the key {key!r} is `uses` in another case; "
                            f"this gate reads only `uses:` exactly")
            return findings
        if kind in ("quoted", "flow") and USES_WORD.search(parsed["text"]):
            what = "a quoted scalar" if kind == "quoted" else "a flow collection"
            findings.append(f"{where}: `uses` inside {what}, which this gate refuses "
                            f"rather than decide whether it is a key")
            return findings
        if key == "uses":
            if kind != "plain":
                what = {"empty": "on the next line", "block": "a block scalar"}.get(kind, kind)
                findings.append(f"{where}: a `uses:` whose value is {what}; write "
                                f"it plain, on the key's line")
                return findings
            counts["uses"] += 1
            findings += check_uses(parsed["text"], parsed["comment"], where, targets)
        if kind == "block":
            i = skip_block(lines, i + 1, parsed["parent"], path, findings)
            if i is None:
                return findings
            continue
        if kind != "empty":
            continuation_limit = parsed["parent"]
        i += 1
    return findings


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    wf_dir = root / WORKFLOWS
    if not wf_dir.is_dir():
        print(f"  FAIL  {WORKFLOWS} does not exist, so there is nothing for this gate to "
              f"check")
        return 1
    try:
        workflows = sorted(p for p in walk_files(wf_dir, SKIP_DIRS)
                           if p.suffix.lower() in YAML_SUFFIXES)
        actions = sorted(p for p in walk_files(root, SKIP_DIRS)
                         if p.name.lower() in ACTION_FILES)
    except OSError as exc:
        print(f"  FAIL  could not walk the tree: {exc}")
        return 1
    if not workflows:
        print(f"  FAIL  no .yml or .yaml file under {WORKFLOWS}, so there is nothing for "
              f"this gate to check")
        return 1
    files = sorted(set(workflows) | set(actions))

    findings, targets, counts = [], [], {"uses": 0}
    for p in files:
        rel = p.relative_to(root).as_posix()
        try:
            # Bytes, decoded here: read_text() would fold CR and CRLF into LF before the gate
            # could see them, and scan() decides what a CR means.
            text = p.read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            findings.append(f"could not read {rel}: {exc}")
            continue
        findings += scan(text, rel, targets, counts)

    # A local action is this repository's code, but its own `uses:` lines are held to the same
    # rule, so the path has to land on a file this gate has just read.
    scanned = {p.resolve() for p in files}
    for where, value in targets:
        target = (root / value[2:]).resolve()
        if not target.is_relative_to(root.resolve()):
            findings.append(f"{where}: `uses: {value}` resolves outside the repository")
            continue
        if target.suffix.lower() in YAML_SUFFIXES:
            candidates = [target]
        else:
            candidates = [target / name for name in ACTION_FILES]
        if not any(c.is_file() and c.resolve() in scanned for c in candidates):
            findings.append(f"{where}: `uses: {value}` does not resolve to a workflow "
                            f"file or an action.yml/action.yaml this gate reads, so its own "
                            f"`uses:` lines would go unchecked")

    if not findings and counts["uses"] == 0:
        findings.append(f"no `uses:` line in {len(files)} files; a gate that checked "
                        f"nothing must not print a pass")
    if findings:
        for f in findings:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {counts['uses']} uses: lines across {len(files)} files are "
          f"pinned to a full commit SHA with a release comment, a Docker digest, or a local path")
    return 0


if __name__ == "__main__":
    sys.exit(main())
