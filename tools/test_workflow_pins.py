#!/usr/bin/env python3
"""Cases for check_workflow_pins.py, one per check the gate makes, each run against the real gate.

The gate is new, so no reviewer has broken it yet, and these cases are not a record of past rounds
the way the CSP and gensrc files are. They are the answer to the question a reviewer will ask
first: which of the gate's checks can be deleted with the suite still green? The answer should be
none. Every check has at least one case here that fails when the check is removed, and the plan for
row 3.21 lists the mutation behind each.

Three kinds of case appear. Most mutate a workflow and assert the gate FAILS with a message naming
the defect, because an exit code cannot tell a diagnosis from a refusal for the wrong reason. Some
assert the gate REFUSES a line it cannot model, which is how the line reader stays sound. The rest
assert a PASS. Some are the forms the gate accepts (a local action, a Docker digest, a reusable
workflow); the others guard against a false alarm: a `run: |` block full of shell punctuation is
read past, a commented-out step is a comment, and the word in a step name is text. A gate that
alarms on those would be switched off, which is worse than no gate.

The mutations start from the real `checks.yml` wherever they can, so the cases move with the file.
Where a case needs a shape the real files do not have, it writes a small extra workflow beside them.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
C = ".github/workflows/checks.yml"
L = ".github/workflows/linkcheck.yml"
X = ".github/workflows/extra.yml"
CHECKS = (ROOT / C).read_text(encoding="utf-8")
LINKCHECK = (ROOT / L).read_text(encoding="utf-8")

# The checkout pin as checks.yml writes it. If this stops matching, the cases below would mutate
# nothing and pass for the wrong reason, so the file refuses to run instead.
_PIN = re.search(r"actions/checkout@([0-9a-f]{40})  # v[0-9]+\.[0-9]+\.[0-9]+", CHECKS)
if _PIN is None:
    print("  FAIL  checks.yml no longer carries a pinned actions/checkout line for these cases to "
          "mutate; update test_workflow_pins.py")
    sys.exit(1)
PIN, SHA = _PIN.group(), _PIN.group(1)
PIN_LINE = CHECKS[: CHECKS.index(PIN)].count("\n") + 1
MIXED = next(SHA[:k] + SHA[k].upper() + SHA[k + 1:] for k, ch in enumerate(SHA) if ch in "abcdef")
DIGEST = "sha256:" + "0123456789abcdef" * 4
HEAD = "name: t\non: push\njobs:\n  j:\n    runs-on: ubuntu-latest\n    steps:\n"


def swap(new):
    """checks.yml with its checkout pin replaced by `new`."""
    return {C: CHECKS.replace(PIN, new, 1)}


def steps(*lines, path=X):
    """A small extra workflow whose steps are `lines`, each indented to step level."""
    return {path: HEAD + "".join("      " + line + "\n" for line in lines)}


def action(*lines):
    """A composite action's metadata whose steps are `lines`."""
    return ("name: a\nruns:\n  using: composite\n  steps:\n"
            + "".join("    " + line + "\n" for line in lines))


def run_against(files=None, no_workflows=False, gate=None):
    """Run the real gate against a copy of the workflows. Returns (exit, full output).

    `files` maps a repository-relative path to its text (bytes are written as they are); None as a
    value deletes one of the real workflows from the copy. `no_workflows` removes the directory.
    `gate` is an (old, new) pair applied once to the gate SOURCE, for the one case that needs an
    I/O failure no fixture can produce without permission tricks; the pair must match exactly once.
    """
    d = Path(tempfile.mkdtemp())
    try:
        (d / "tools").mkdir()
        shutil.copyfile(TOOLS / "_walk.py", d / "tools" / "_walk.py")
        src = (TOOLS / "check_workflow_pins.py").read_text(encoding="utf-8")
        if gate is not None:
            if src.count(gate[0]) != 1:
                raise ValueError(f"the gate injection {gate[0]!r} no longer matches exactly once")
            src = src.replace(gate[0], gate[1])
        (d / "tools" / "check_workflow_pins.py").write_text(src, encoding="utf-8")
        tree = {C: CHECKS, L: LINKCHECK}
        tree.update(files or {})
        if not no_workflows:
            (d / ".github" / "workflows").mkdir(parents=True)
            for rel, text in tree.items():
                if text is None:
                    continue
                p = d / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(text if isinstance(text, bytes) else text.encode("utf-8"))
        r = subprocess.run([sys.executable, "tools/check_workflow_pins.py"], cwd=d,
                           capture_output=True, text=True)
        return r.returncode, (r.stdout + r.stderr).strip()
    finally:
        shutil.rmtree(d, ignore_errors=True)


CO = "actions/checkout"
REUSE_HEAD = "name: t\non: push\njobs:\n  call:\n"
LOCAL_ACTION = ".github/actions/setup/action.yml"

# (description, files, must_fail, expected substring)
CASES = (
    # PASSES. Each guards a false alarm or an accepted form.
    ("the workflows as they stand", None, False, "ok"),
    ("a single space before the release comment, which YAML reads as a comment",
     swap(PIN.replace("  #", " #")), False, "ok"),
    ("a leading --- document marker", {C: "---\n" + CHECKS}, False, "ok"),
    ("CRLF line endings, which are read as LF", {C: CHECKS.replace("\n", "\r\n")}, False, "ok"),
    ("shell punctuation inside a run: | block, which is read past by indentation",
     steps("- run: |", "    echo '# not a comment' && echo \"{ } [ ] & * ! ? : \"",
           "    key: value", "- uses: " + PIN), False, "ok"),
    ("a folded block with a trailing comment on its header, then a pinned step",
     steps("- run: >-  # folded", "    echo one", "", "    echo two", "- uses: " + PIN),
     False, "ok"),
    ("a commented-out step naming a tag", steps("# - uses: actions/checkout@v4", "- run: true"),
     False, "ok"),
    ("the word uses in a plain step name", steps("- name: Check what the job uses", "  run: true"),
     False, "ok"),
    ("a quoted string and an apostrophe elsewhere in a step",
     steps("- name: 'it''s fine'", "  run: echo don't"), False, "ok"),
    ("an escaped quote inside a double-quoted name",
     steps('- name: "say \\"hi\\" # not a comment"', "  run: true"), False, "ok"),
    ("a flow mapping with a bracket inside a quoted value",
     steps("- run: true", '  env: {A: "x]y"}'), False, "ok"),
    ("a remote reusable workflow pinned with its release named",
     {X: REUSE_HEAD + f"    uses: octo-org/example/.github/workflows/ci.yml@{SHA}  # v1.2.3\n"},
     False, "ok"),
    ("a local composite action whose own uses: is pinned",
     {**steps("- uses: ./.github/actions/setup"), LOCAL_ACTION: action("- uses: " + PIN)},
     False, "ok"),
    ("a local reusable workflow",
     {X: REUSE_HEAD + "    uses: ./.github/workflows/reuse.yml\n",
      ".github/workflows/reuse.yml": "on: workflow_call\njobs:\n  r:\n    runs-on: x\n    steps:\n"
                                     "      - uses: " + PIN + "\n"}, False, "ok"),
    ("a Docker action pinned by digest, with a comment naming its tag",
     steps(f"- uses: docker://alpine:3.20@{DIGEST}  # 3.20"), False, "ok"),
    ("a Docker action pinned by digest, with no comment",
     steps(f"- uses: docker://alpine@{DIGEST}"), False, "ok"),

    # REFS. What row 3.17 removed, and its near relatives.
    ("@v4, the floating major tag row 3.17 removed", swap(f"{CO}@v4  # v4.4.0"), True,
     "tag, branch name or expression"),
    ("@main", swap(f"{CO}@main  # v4.4.0"), True, "tag, branch name or expression"),
    ("a branch name with a slash", swap(f"{CO}@releases/v4  # v4.4.0"), True,
     "tag, branch name or expression"),
    ("an expression as the ref", swap(CO + "@$" + "{{ env.SHA }}  # v4.4.0"), True,
     "tag, branch name or expression"),
    ("an abbreviated seven-character SHA", swap(f"{CO}@{SHA[:7]}  # v4.4.0"), True,
     "shorter than 40 characters (7)"),
    ("a 39-character SHA", swap(f"{CO}@{SHA[:39]}  # v4.4.0"), True,
     "shorter than 40 characters (39)"),
    ("a 41-character hex ref", swap(f"{CO}@{SHA}0  # v4.4.0"), True,
     "41 hex characters"),
    ("the SHA in uppercase hex", swap(f"{CO}@{SHA.upper()}  # v4.4.0"), True,
     "uppercase hex"),
    ("one uppercase hex digit in the SHA", swap(f"{CO}@{MIXED}  # v4.4.0"), True,
     "uppercase hex"),
    ("no ref at all", swap(f"{CO}  # v4.4.0"), True, "not an owner/repo"),
    ("an owner with no repository", swap(f"actions@{SHA}  # v4.4.0"), True,
     "not an owner/repo"),
    ("a # glued to the SHA, which YAML reads as part of the value",
     swap(f"{CO}@{SHA}# v4.4.0"), True, "no space before it"),

    # THE RELEASE COMMENT.
    ("no release comment", swap(f"{CO}@{SHA}"), True, "no release comment"),
    ("the release comment moved to the next line",
     swap(f"{CO}@{SHA}\n        # v4.4.0"), True, "no release comment"),
    ("a comment without the v", swap(PIN.replace("# v", "# ")), True, "malformed release comment"),
    ("a two-part version", swap(f"{CO}@{SHA}  # v4.4"), True,
     "malformed release comment"),
    ("a major-only version", swap(f"{CO}@{SHA}  # v4"), True,
     "malformed release comment"),
    ("no space after the #", swap(PIN.replace("# v", "#v")), True, "malformed release comment"),
    ("two spaces after the #", swap(PIN.replace("# v", "#  v")), True,
     "malformed release comment"),
    ("text after the version", swap(PIN + " latest"), True, "malformed release comment"),
    ("a prerelease suffix", swap(PIN + "-rc.1"), True, "malformed release comment"),
    ("a capital V", swap(PIN.replace("# v", "# V")), True, "malformed release comment"),

    # DOCKER.
    ("a Docker image by tag alone", steps("- uses: docker://alpine:3.20  # 3.20"), True,
     "not pinned by an @sha256: digest"),
    ("a Docker image with no tag or digest", steps("- uses: docker://alpine"), True,
     "not pinned by an @sha256: digest"),
    ("a Docker digest in uppercase hex",
     steps(f"- uses: docker://alpine@sha256:{DIGEST[7:].upper()}  # 3.20"),
     True, "not pinned by an @sha256: digest"),
    ("a Docker digest one character short",
     steps(f"- uses: docker://alpine@{DIGEST[:-1]}  # 3.20"),
     True, "not pinned by an @sha256: digest"),
    ("a Docker digest under sha512",
     steps(f"- uses: docker://alpine@{DIGEST.replace('sha256', 'sha512')}"),
     True, "not pinned by an @sha256: digest"),

    # REUSABLE WORKFLOWS AND LOCAL PATHS.
    ("a remote reusable workflow at @main",
     {X: REUSE_HEAD + "    uses: octo-org/example/.github/workflows/ci.yml@main  # v1.2.3\n"},
     True, "tag, branch name or expression"),
    ("a remote reusable workflow at a short SHA",
     {X: REUSE_HEAD + f"    uses: octo-org/example/.github/workflows/ci.yml@{SHA[:12]}  # v1.2.3\n"},
     True, "shorter than 40"),
    ("a local composite action whose own uses: floats",
     {**steps("- uses: ./.github/actions/setup"), LOCAL_ACTION: action(f"- uses: {CO}@v4")},
     True, LOCAL_ACTION + ":"),
    ("a local action with no action.yml", steps("- uses: ./.github/actions/missing"), True,
     "does not resolve"),
    ("a local action directory that exists but carries no action.yml",
     {**steps("- uses: ./.github/actions/empty"), ".github/actions/empty/README.md": "x\n"},
     True, "does not resolve"),
    ("a local path that leaves the repository", steps("- uses: ./../outside"), True,
     "outside the repository"),
    ("a local reusable workflow that does not exist",
     {X: REUSE_HEAD + "    uses: ./.github/workflows/missing.yml\n"}, True, "does not resolve"),
    ("a local reusable workflow outside .github/workflows, which the gate does not read",
     {X: REUSE_HEAD + "    uses: ./docs/reuse.yml\n", "docs/reuse.yml": "on: workflow_call\n"},
     True, "does not resolve"),
    ("an action.yml nobody references, which is still read",
     {"tools/probe/action.yml": action(f"- uses: {CO}@v4")}, True, "tools/probe/action.yml:"),
    ("a workflow in a subdirectory", steps(f"- uses: {CO}@v4", path=".github/workflows/sub/x.yml"),
     True, "sub/x.yml:"),
    ("a workflow with an upper-case .YML suffix",
     steps(f"- uses: {CO}@v4", path=".github/workflows/x.YML"), True, "x.YML:"),
    ("a workflow with a .yaml suffix", steps(f"- uses: {CO}@v4", path=".github/workflows/x.yaml"),
     True, "x.yaml:"),
    ("an action input named uses, held to the same rule",
     steps("- uses: " + PIN, "  with:", "    uses: something"), True, "not an owner/repo"),

    # WHAT THE LINE READER REFUSES. Each is a shape it cannot classify, so it must not guess.
    ("uses in a flow mapping", steps(f"- {{uses: {CO}@v4}}"), True, "inside a flow collection"),
    ("a correctly pinned uses in a flow mapping, still refused",
     steps(f"- {{uses: {CO}@{SHA}}}  # v4.4.0"), True, "inside a flow collection"),
    ("a flow mapping that runs onto the next lines",
     steps("- " + "{", "    uses: " + PIN, "  " + "}"), True, "runs past the end of its line"),
    ("a uses: whose value is a flow sequence", steps("- uses: [a]"), True, "whose value is flow"),
    ("an alias inside a flow sequence", steps("- run: true", "  if: [*cond]"), True, "indicator"),
    ("an anchor on a uses: value", steps("- uses: &co " + PIN), True, "anchor"),
    ("an alias standing in for a step", steps("- uses: " + PIN, "- *co"), True, "alias"),
    ("a merge key", steps("- <<: *base"), True, "nested mapping or an error"),
    ("a tag on a uses: value", steps(f"- uses: !!str {CO}@v4"), True, "tag (!)"),
    ("an explicit key", steps("- ? uses", f"  : {CO}@v4"), True, "explicit key"),
    ("uses: as a folded block scalar", steps("- uses: >-", f"    {CO}@v4"), True,
     "a block scalar"),
    ("uses: as a literal block scalar", steps("- uses: |", f"    {CO}@v4"), True,
     "a block scalar"),
    ("uses: with its value on the next line", steps("- uses:", f"    {CO}@v4"), True,
     "on the next line"),
    ("a plain scalar continued onto a more indented line", steps(f"- uses: {CO}", "    @v4"), True,
     "continues onto"),
    ("a double-quoted scalar across lines", steps('- name: "a', f"    uses: {CO}@v4\""), True,
     "runs past the end of its line"),
    ("a double-quoted key naming uses", steps('- "uses": ' + PIN), True, "quoted key naming uses"),
    ("a single-quoted key naming uses", steps("- 'uses': " + PIN), True, "quoted key naming uses"),
    ("a quoted key the gate cannot read as a name", steps('- "a b": x'), True,
     "cannot read as a plain name"),
    ("a quoted uses: value", steps(f'- uses: "{CO}@{SHA}"  # v4.4.0'), True,
     "whose value is quoted"),
    ("the word uses inside a quoted value", steps(f'- name: "uses: {CO}@v4"', "  run: true"),
     True, "inside a quoted scalar"),
    ("the word uses inside a run: | block, refused rather than trusted as shell",
     steps("- run: |", f"    echo 'uses: {CO}@v4'"), True, "inside a block scalar"),
    ("a uses: key hidden at a block's content indentation",
     steps("- run: |", "    echo hi", f"    uses: {CO}@v4"), True, "inside a block scalar"),
    ("a # inside quotes that would hide a uses: if read as a comment",
     steps(f'- name: "x #" uses: {CO}@v4'), True, "text follows a quoted scalar"),
    ("a # glued to a closing quote, which is text and not a comment",
     steps(f'- name: "x"# uses: {CO}@v4'), True, "text follows a quoted scalar"),
    ("a comment opened inside a flow collection, which leaves it unclosed",
     steps("- run: true", "  env: [a # b]"), True, "runs past the end of its line"),
    ("the word uses in capitals inside a quoted value",
     steps(f'- name: "USES: {CO}@v4"', "  run: true"), True, "inside a quoted scalar"),
    ("Uses: in title case", steps(f"- Uses: {CO}@v4"), True, "in another case"),
    ("USES: in upper case", steps(f"- USES: {CO}@v4"), True, "in another case"),
    ("a tab after the dash", steps(f"-\tuses: {CO}@v4"), True, "a tab"),
    ("a bare dash with the step's keys on the next line", steps("-", f"  uses: {CO}@v4"),
     True, "tag, branch name or expression"),
    ("a line that is neither a key nor a sequence entry",
     {X: HEAD + "      - run: true\nstray\n"}, True, "neither a key nor a sequence entry"),
    ("a block scalar with an indentation indicator", steps("- run: |2", "    echo"), True,
     "indentation indicator"),
    ("a line between a block's content indentation and its key",
     steps("- run: |", "      echo a", f"    uses: {CO}@v4"), True, "invalid YAML"),
    ("a real uses: right after a block scalar ends",
     steps("- run: |", "    echo hi", f"- uses: {CO}@v4"), True, "tag, branch name or expression"),
    ("a real uses: after a block scalar and a less indented comment",
     steps("- run: |", "    echo hi", "  # a note", f"- uses: {CO}@v4"), True,
     "tag, branch name or expression"),
    ("a real uses: after an empty block scalar", steps("- run: |", f"- uses: {CO}@v4"), True,
     "tag, branch name or expression"),
    ("a second YAML document", {C: CHECKS + "---\njobs: {}\n"}, True, "document marker"),
    ("a YAML directive", {C: "%YAML 1.2\n---\n" + CHECKS}, True, "directive"),
    ("a NEL character, a line break to YAML 1.1 and not to 1.2",
     steps("- run: true" + chr(0x85) + f"uses: {CO}@v4"), True, "U+0085"),
    ("a lone CR, which YAML reads as a line break",
     steps("- run: true\r" + f"uses: {CO}@v4"), True, "U+000D"),
    ("a byte order mark", {C: chr(0xFEFF) + CHECKS}, True, "U+FEFF"),

    # THE FILES THEMSELVES.
    ("a workflow that is not UTF-8", {X: b"on: push\n\xff\n"}, True, "could not read"),
    ("workflows with no uses: at all",
     {C: None, L: None, X: "on: push\njobs: {}\n"}, True, "checked nothing"),
    ("a workflows directory with no YAML in it", {C: None, L: None}, True, "no .yml or .yaml"),
    ("no workflows directory", None, True, "does not exist"),
    ("the tree walk failing, which must fail closed and not crash", None, True, "could not walk"),
)

NO_WORKFLOWS = {"no workflows directory"}
# Cases carried by a run_against argument rather than a file override.
EXTRA_ARGS = {
    "the tree walk failing, which must fail closed and not crash":
        {"gate": ("walk_files(wf_dir, SKIP_DIRS)", "walk_files(wf_dir / 'absent', SKIP_DIRS)")},
}


def main() -> int:
    failures = []
    for desc, files, must_fail, expected in CASES:
        rc, out = run_against(files, no_workflows=desc in NO_WORKFLOWS, **EXTRA_ARGS.get(desc, {}))
        if "Traceback (most recent call last)" in out:
            failures.append(f"{desc}: the gate crashed: {out!r}")
        elif bool(rc) != must_fail:
            want = "fail" if must_fail else "pass"
            failures.append(f"{desc}: expected the gate to {want}, it did not ({out!r})")
        elif expected not in out:
            failures.append(
                f"{desc}: the gate's exit status was right but its message was not. "
                f"Expected it to contain {expected!r}. It said: {out!r}")

    # A finding has to name the line a maintainer can go to.
    rc, out = run_against(swap(f"{CO}@v4  # v4.4.0"))
    if f"{C}:{PIN_LINE}:" not in out:
        failures.append(f"the @v4 finding does not name {C}:{PIN_LINE}, where the pin is. "
                        f"It said: {out!r}")

    # Findings accumulate across files: two floating tags in two files are two findings, so a
    # maintainer fixing one is not surprised by the next.
    rc, out = run_against({**swap(f"{CO}@v4  # v4.4.0"),
                           L: LINKCHECK.replace(PIN, f"{CO}@main  # v4.4.0", 1)})
    if out.count("FAIL  ") != 2 or L not in out or C not in out:
        failures.append(f"two floating tags in two files did not produce one finding each: {out!r}")

    # The pass line counts what it checked, so a gate that silently skipped a file would show it.
    rc, out = run_against()
    want = sum(len(re.findall(r"^\s*(?:- )?uses: ", t, re.M)) for t in (CHECKS, LINKCHECK))
    if f"ok    {want} uses: lines across 2 files" not in out:
        failures.append(f"the pass line does not count the {want} uses: lines in the real "
                        f"workflows: {out!r}")

    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {len(CASES)} recorded cases for the workflow-pin gate, plus line, "
          f"accumulation and count checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
