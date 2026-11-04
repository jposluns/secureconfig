#!/usr/bin/env python3
"""Cases for the 2 shell runners of the site gates: run_gate in tools/run_all_checks.sh, and
scripts/pages-build.sh, the Cloudflare Pages build command.

RUN_GATE: the function and the ok and bad helpers it calls are read out of tools/run_all_checks.sh
(a missing or reshaped definition is a finding) and run with bash on stand-in gates. Each case
checks what it prints and whether it set fail=1:
  - an exit 0 with an ok line passes and prints the gate's output, ok on standard error too;
  - an exit 0 without an ok line fails ("exited 0 without an ok line");
  - an exit 0 with a FAIL line fails ("printed findings but exited 0"), an ok line beside it or not;
  - a non-zero exit with a traceback or an `...Error: ` line fails as a crash;
  - a non-zero exit with a FAIL line fails and prints the gate's own lines;
  - a non-zero exit with no FAIL line fails ("exited non-zero without reporting a result"), an ok
    line or not.

PAGES-BUILD.SH: the script is copied into a scratch tree and run with bash, with a stand-in python3
first on PATH that records each call and runs no gate. It runs the script's own `-c` version check
with this interpreter and sys.version_info set to the version it reports (3.10.12 or 3.11.5), so
an inverted or wrong comparison fails the cases below. The gates are read from the script (every
`python3 -I -B <file>.py` call outside a comment, wherever it sits on its line, so a gate behind a
condition is still expected to run), so the cases hold when the script's gate list changes:
  - a python3 that reports 3.10: exit 1, the message naming Python 3.11 on standard error, and no
    gate run (only the version check and `python3 --version` are called);
  - a python3 that reports 3.11: the version check, then every gate in the script's order, each
    once, then exit 0 and "Pages build check passed.";
  - each gate in turn exiting 1: the build exits non-zero at that gate, runs no later gate, and does
    not print the passed line.
The committed script is the promoted root form (promotion made `/` build-site.py's default base
and rewrote tools/check_draft.py for the root), so each case runs on it once; the staged form and
the derived promoted variant this test once ran retired with the staging.

THE PALETTE GATE (mandatory on every site from baseline 1.6.0): both runners must carry the exact call
PALETTE_CALL outside a comment, pages-build.sh right after the pin gate that holds the copied gate
to its pin, so that the cases above run it in order and a failure there stops the deploy; a
pages-build.sh in which the call is not read as a gate is a finding too.

THE PALETTE BLOCK of tools/run_all_checks.sh, which holds the palette gate to its exit code (the
baseline 1.6.1 README: 0 pass, 1 fail or unreadable input, 2 usage error; never the wording of
its RESULT line) rather than through run_gate: the block (from `if palette=$(` to its `fi`) and
the ok and bad helpers are read out of the file and run with bash, with python3 replaced by a
stand-in that records its arguments and runs a stand-in gate body. Each case checks the call it
made, that the gate's output is printed, and whether it set fail=1:
  - an exit 0 passes with the block's ok line whatever it prints: a clean or malformed RESULT
    line, a FAIL in the tables, a `RESULT: fail ` line, a traceback or no output at all;
  - an exit 1 fails whatever it prints. With a line that is exactly `Traceback (most recent call
    last):`, printed by a stand-in or raised by a real interpreter, the message says the gate
    crashed ("exited 1 with a Python traceback: the gate crashed"); otherwise, for a
    `RESULT: fail ` line, a malformed one, a pass line, an error line with no traceback or an
    indented traceback line, it says "exited 1: a palette check failed or its input could not be
    read";
  - an exit 2 fails as a usage error ("exited 2, a usage error"), a pass line or a traceback
    beside it or not;
  - any other code fails as an unexpected error ("exited N, an unexpected error"): an exit 3, and
    a gate killed by a signal (137).

--SECTIONS: tools/run_all_checks.sh is copied into a scratch tree and run with bash, with a stand-in
python3 first on PATH that records each call, prints an ok line (the parser preflight's included)
and runs no gate, unless the call is the 1 it is told to fail. Each case checks the exit status,
what the output holds and lacks, and the stand-in's calls:
  - one name runs the parser preflight and that section only, and ends with the selected-pass
    line, never "All gates passed.";
  - two names given out of order run in the file's order;
  - a selected gate that fails exits 1 with "One or more gates failed.";
  - generated-committed alone also runs llms-full and plugin, which its `# depends:` line names,
    says it added them, and runs both bundle builds (stand-ins that record their call) before
    its own calls; with plugin named, only llms-full is added; llms-full alone adds nothing;
  - an unknown name, alone, beside a known one or in another letter case, an empty name (a
    trailing comma or an empty list), a missing list, a misspelled option and an extra argument
    are each refused with status 2 before any heading prints or the stand-in is called;
  - a name holding anything but letters, digits and hyphens (a known name with a newline after
    it or between it and another, a space, a dot, a glob character) is refused with status 2
    the same way, as a character the list may not hold.
The file is also held to its section shape: every heading after the parser preflight sits right
under a `# section: NAME` line, so a heading cannot escape --sections, and 1 `# end of sections`
line comes before the summary.

Nothing here runs a real gate; tools/run_all_checks.sh runs those. Exit 0 ok, 1 on a finding.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "tools" / "run_all_checks.sh"
BUILD = ROOT / "scripts" / "pages-build.sh"
HELPER = re.compile(r"^(?:ok|bad)\(\)\s+\{.*\}$", re.M)
RUN_GATE = re.compile(r"^run_gate\(\) \{\n.*?^\}$", re.M | re.S)
# A gate call: `python3 -I -B`, a .py file and its arguments, up to a shell operator or line end.
GATE = re.compile(r"python3 -I -B ([\w./-]+\.py(?: [^\s;&|)]+)*)")
PASSED = "Pages build check passed."
# The palette gate's call in both runners (secureconfig.ai has no site-palette.css), and the gate
# that pages-build.sh runs just before it.
PALETTE_CALL = ("python3 -I -B .baseline/check_palette.py --site secureconfig "
                "--palettes site/assets/baseline/palettes.css")
PIN_GATE = "-I -B tools/check_baseline_pin.py"
# The palette block of tools/run_all_checks.sh, from its call to its `fi`.
PALETTE_BLOCK = re.compile(r"^if palette=\$\(python3 .*?^fi$", re.M | re.S)
PALETTE_OK = "  ok    check_palette.py: the secureconfig palette passes in both schemes"
PALETTE_PASS = "RESULT: pass (1 site, 0 failing checks)"
PALETTE_FAILED = "  FAIL  check_palette.py exited 1: a palette check failed or its input could not be read"
PALETTE_CRASHED = ("  FAIL  check_palette.py exited 1 with a Python traceback: the gate crashed; "
                   "the palette is unverified")
PALETTE_USAGE = "  FAIL  check_palette.py exited 2, a usage error; the palette is unverified"
PALETTE_ANY_FAIL = "  FAIL  check_palette.py exited"
TRACEBACK = "Traceback (most recent call last):"
# (stand-in gate body, fail=1 expected, texts the output must hold, texts it must not hold). The
# block decides by the exit code only, so an exit 0 passes whatever it prints and a non-zero exit
# fails whatever it prints; only the message of an exit 1 reads the output, for a traceback line.
# Every case also holds the block to printing the gate's output.
PALETTE_CASES = (
    (f"printf '  site  4.60:1  needs 4.5\\n{PALETTE_PASS}\\n'", False,
     [PALETTE_OK, "  site  4.60:1  needs 4.5", PALETTE_PASS], [PALETTE_ANY_FAIL]),
    (f"printf '  site  4.10:1  needs 4.5  FAIL\\n{PALETTE_PASS}\\n'", False,
     [PALETTE_OK, "  site  4.10:1  needs 4.5  FAIL"], [PALETTE_ANY_FAIL]),
    ("printf '  site  4.60:1  needs 4.5\\n'", False, [PALETTE_OK, "  site  4.60:1  needs 4.5"],
     [PALETTE_ANY_FAIL]),
    ("true", False, [PALETTE_OK], [PALETTE_ANY_FAIL]),
    ("printf 'RESULT: pass\\n'", False, [PALETTE_OK, "RESULT: pass"], [PALETTE_ANY_FAIL]),
    ("printf 'RESULT: pass (2 sites, 0 failing checks)\\n'", False,
     [PALETTE_OK, "RESULT: pass (2 sites"], [PALETTE_ANY_FAIL]),
    (f"printf '{PALETTE_PASS} \\n'", False, [PALETTE_OK, f"{PALETTE_PASS} "], [PALETTE_ANY_FAIL]),
    (f"printf '  {PALETTE_PASS}\\n'", False, [PALETTE_OK, f"  {PALETTE_PASS}"], [PALETTE_ANY_FAIL]),
    ("printf 'RESULT: fail (1 site, 1 failing check)\\n'", False,
     [PALETTE_OK, "RESULT: fail (1 site, 1 failing check)"], [PALETTE_ANY_FAIL]),
    (f"printf '{TRACEBACK}\\nKeyError: 1\\n'", False, [PALETTE_OK, TRACEBACK], [PALETTE_ANY_FAIL]),
    ("printf '  site  4.10:1  needs 4.5  FAIL\\nRESULT: fail (1 site, 1 failing check)\\n'; exit 1",
     True, ["  site  4.10:1  needs 4.5  FAIL", PALETTE_FAILED],
     [PALETTE_OK, PALETTE_USAGE, PALETTE_CRASHED]),
    ("printf 'RESULT: fail (the input could not be checked)\\n'; exit 1", True,
     ["RESULT: fail (the input could not be checked)", PALETTE_FAILED],
     [PALETTE_OK, PALETTE_CRASHED]),
    # A traceback line on an exit 1 is a crash, wherever it sits in the output; an error line
    # without one, or a traceback line that is indented or carries more text, is not.
    (f"printf '{TRACEBACK}\\n  File \"x\", line 1\\nKeyError: 1\\n'; exit 1",
     True, ["KeyError: 1", PALETTE_CRASHED], [PALETTE_OK, PALETTE_FAILED]),
    (f"printf '  site  4.60:1  needs 4.5\\n{TRACEBACK}\\nValueError: bad\\n'; exit 1", True,
     ["  site  4.60:1  needs 4.5", PALETTE_CRASHED], [PALETTE_OK, PALETTE_FAILED]),
    ("printf 'RESULT: fail (1 site, 1 failing check)\\nValueError: bad\\n'; exit 1", True,
     ["ValueError: bad", PALETTE_FAILED], [PALETTE_OK, PALETTE_CRASHED]),
    (f"printf '  {TRACEBACK}\\nKeyError: 1\\n'; exit 1", True,
     [f"  {TRACEBACK}", PALETTE_FAILED], [PALETTE_OK, PALETTE_CRASHED]),
    (f"printf '{TRACEBACK} x\\nKeyError: 1\\n'; exit 1", True,
     [f"{TRACEBACK} x", PALETTE_FAILED], [PALETTE_OK, PALETTE_CRASHED]),
    ("printf 'RESULT:fail (1 site, 1 failing check)\\n'; exit 1", True,
     ["RESULT:fail", PALETTE_FAILED], [PALETTE_OK]),
    ("printf 'RESULT: failed\\n'; exit 1", True, ["RESULT: failed", PALETTE_FAILED], [PALETTE_OK]),
    ("printf '  RESULT: fail (1 site, 1 failing check)\\n'; exit 1", True,
     ["  RESULT: fail", PALETTE_FAILED], [PALETTE_OK]),
    (f"printf '{PALETTE_PASS}\\n'; exit 1", True, [PALETTE_PASS, PALETTE_FAILED], [PALETTE_OK]),
    ("exit 2", True, [PALETTE_USAGE], [PALETTE_OK, PALETTE_FAILED, PALETTE_CRASHED]),
    # Any other code fails too: a usage error that prints a pass line or a traceback, an unknown
    # code, a crash in a real interpreter (exit 1) and a gate killed by a signal (128 + 9).
    (f"printf 'usage: check_palette.py\\n{PALETTE_PASS}\\n'; exit 2", True,
     ["usage: check_palette.py", PALETTE_USAGE], [PALETTE_OK]),
    (f"printf '{TRACEBACK}\\nKeyError: 1\\n'; exit 2", True, [TRACEBACK, PALETTE_USAGE],
     [PALETTE_OK, PALETTE_CRASHED]),
    ("printf 'palette-exit-3-output\\n'; exit 3", True,
     ["palette-exit-3-output",
      "  FAIL  check_palette.py exited 3, an unexpected error; the palette is unverified"],
     [PALETTE_OK]),
    ("python3 -I -c 'raise KeyError(1)'", True, [TRACEBACK, PALETTE_CRASHED],
     [PALETTE_OK, PALETTE_FAILED]),
    ("kill -KILL $$", True,
     ["  FAIL  check_palette.py exited 137, an unexpected error; the palette is unverified"],
     [PALETTE_OK]),
)
# The stand-in python3: it records its arguments, runs the script's `-c` version check with this
# interpreter and sys.version_info set to STANDIN_VERSION, answers --version from STANDIN_VERSION,
# and fails the 1 gate named by STANDIN_FAIL.
STANDIN = """#!/usr/bin/env bash
printf '%s\\n' "$*" >> "$STANDIN_LOG"
case "$1" in
  -c) exec "$STANDIN_PYTHON" -I -B -c 'import sys; sys.version_info = tuple(map(int, sys.argv[1].split("."))); exec(sys.argv[2])' "$STANDIN_VERSION" "$2" ;;
  --version) printf 'Python %s\\n' "$STANDIN_VERSION"; exit 0 ;;
esac
if [ "$*" = "$STANDIN_FAIL" ]; then
  printf '  FAIL  stand-in finding\\n'
  exit 1
fi
printf '  ok    stand-in\\n'
"""

# (stand-in gate body, fail=1 expected, texts the output must hold, texts it must not hold)
RUN_GATE_CASES = (
    ("printf '  ok    gate passed\\n'", False, ["  ok    gate passed"], ["FAIL"]),
    ("printf '  ok    gate passed\\n' >&2", False, ["  ok    gate passed"], ["FAIL"]),
    ("printf 'all good\\n'", True, ["  FAIL  stand-in exited 0 without an ok line"], []),
    ("true", True, ["  FAIL  stand-in exited 0 without an ok line"], []),
    ("printf '  ok    x\\n  FAIL  y\\n'", True, ["  FAIL  stand-in printed findings but exited 0"], []),
    ("printf '  FAIL  y\\n'", True, ["  FAIL  stand-in printed findings but exited 0"], []),
    ("printf 'Traceback (most recent call last):\\n  FAIL  z\\n'; exit 1", True,
     ["  FAIL  stand-in crashed"], []),
    ("printf 'ValueError: bad\\n'; exit 1", True, ["  FAIL  stand-in crashed"], []),
    ("printf '  FAIL  a finding\\n'; exit 1", True, ["  FAIL  a finding"],
     ["crashed", "without reporting"]),
    ("exit 2", True, ["  FAIL  stand-in exited non-zero without reporting a result"], []),
    ("printf '  ok    x\\n'; exit 1", True,
     ["  FAIL  stand-in exited non-zero without reporting a result"], []),
)


# The --sections stand-in python3: it records its arguments, fails the 1 call named by
# STANDIN_FAIL, and otherwise prints an ok line that also satisfies the parser preflight.
SECTIONS_STANDIN = """#!/usr/bin/env bash
printf '%s\\n' "$*" >> "$STANDIN_LOG"
if [ "$*" = "$STANDIN_FAIL" ]; then
  printf '  FAIL  stand-in finding\\n'
  exit 1
fi
printf '  ok    gate parser preflight: stand-in\\n'
"""
# The stand-in bundle builds, which record their call in the same log and change nothing, so the
# llms-full and plugin sections pass on the stand-in tree's files.
BUILD_STANDINS = {"build-llms-full.sh": "printf 'build-llms-full.sh\\n' >> \"$STANDIN_LOG\"\n",
                  "build-plugin.sh": "printf 'build-plugin.sh\\n' >> \"$STANDIN_LOG\"\n"}
WALKER = "== shared walker scans tracked files only =="
SECRETS_TESTS = "== secrets scan fails closed on read errors =="
LLMS_FULL = "== llms-full.txt is current =="
PLUGIN = "== the plugin bundle is current =="
GENERATED = "== the committed generated files match a fresh build of the commit =="
LLMS_LINKS = "== llms-full.txt links are absolute"
PREFLIGHT_CALL = "-I -B tools/check_parser_pin.py"
WALKER_CALL = "-B tools/test_walk.py"
SECRETS_CALL = "-I -B tools/test_secrets_scan.py"
# generated-committed's self-test and gate, after the two builds its clean-tree skip relies on.
GENERATED_CALLS = ["build-llms-full.sh", "build-plugin.sh",
                   "-I -B tools/test_generated_committed.py",
                   "-I -B tools/check_generated_committed.py"]
ADDED = "Sections added: "
USAGE = "usage: tools/run_all_checks.sh [--sections NAME[,NAME...]]"
REFUSED = "which is not a section of tools/run_all_checks.sh; no gate ran"
CHARACTER = "which holds a character other than a letter, a digit or a hyphen; no gate ran"
# (arguments, exit status, texts the output must hold, texts it must not hold, the stand-in's
# calls, the call to fail)
SECTIONS_CASES = (
    (["--sections", "walker"], 0,
     [WALKER, "All selected gates passed (walker); the other sections did not run."],
     [SECRETS_TESTS, "All gates passed.", "  FAIL  "], [PREFLIGHT_CALL, WALKER_CALL], ""),
    (["--sections", "secrets-tests,walker"], 0,
     [WALKER, SECRETS_TESTS, "All selected gates passed (secrets-tests,walker)"],
     ["All gates passed.", "  FAIL  "], [PREFLIGHT_CALL, WALKER_CALL, SECRETS_CALL], ""),
    (["--sections", "walker"], 1, [WALKER, "  FAIL  test_walk.py failed", "One or more gates failed."],
     ["All selected gates passed"], [PREFLIGHT_CALL, WALKER_CALL], WALKER_CALL),
    # generated-committed's `# depends:` line adds llms-full and plugin, in the file's order.
    (["--sections", "generated-committed"], 0,
     [f"{ADDED}llms-full,plugin, which a named section depends on", LLMS_FULL, PLUGIN, GENERATED,
      "All selected gates passed (generated-committed,llms-full,plugin); the other sections "
      "did not run."],
     ["All gates passed.", "  FAIL  ", LLMS_LINKS], [PREFLIGHT_CALL, *GENERATED_CALLS], ""),
    (["--sections", "plugin,generated-committed"], 0,
     [f"{ADDED}llms-full, which", LLMS_FULL, PLUGIN, GENERATED,
      "All selected gates passed (plugin,generated-committed,llms-full)"],
     ["All gates passed.", "  FAIL  ", LLMS_LINKS], [PREFLIGHT_CALL, *GENERATED_CALLS], ""),
    (["--sections", "llms-full"], 0, [LLMS_FULL, "All selected gates passed (llms-full)"],
     [ADDED, PLUGIN, GENERATED, "  FAIL  "], [PREFLIGHT_CALL, "build-llms-full.sh"], ""),
    (["--sections", "no-such-section"], 2, [f"  FAIL  --sections names 'no-such-section', {REFUSED}"],
     ["== "], [], ""),
    (["--sections", "walker,no-such-section"], 2, [f"names 'no-such-section', {REFUSED}"],
     ["== "], [], ""),
    (["--sections", "Walker"], 2, [f"names 'Walker', {REFUSED}"], ["== "], [], ""),
    (["--sections", "walker,"], 2, [f"names '', {REFUSED}"], ["== "], [], ""),
    (["--sections", ""], 2, [f"names '', {REFUSED}"], ["== "], [], ""),
    (["--sections", "walker\n"], 2, [f"names 'walker\n', {CHARACTER}"], ["== "], [], ""),
    (["--sections", "walker\nsecrets"], 2, [f"names 'walker\nsecrets', {CHARACTER}"], ["== "],
     [], ""),
    (["--sections", "secrets,\nwalker"], 2, [f"names '\nwalker', {CHARACTER}"], ["== "], [], ""),
    (["--sections", "walker x"], 2, [f"names 'walker x', {CHARACTER}"], ["== "], [], ""),
    (["--sections", "walker.sh"], 2, [f"names 'walker.sh', {CHARACTER}"], ["== "], [], ""),
    (["--sections", "walk*"], 2, [f"names 'walk*', {CHARACTER}"], ["== "], [], ""),
    (["--sections"], 2, [USAGE], ["== "], [], ""),
    (["--section", "walker"], 2, [USAGE], ["== "], [], ""),
    (["--sections", "walker", "secrets"], 2, [USAGE], ["== "], [], ""),
)


def sections_failures():
    """Run a copy of tools/run_all_checks.sh with --sections on each of SECTIONS_CASES."""
    failures = []
    text = SUITE.read_text(encoding="utf-8")
    lines = text.split("\n")
    heads = [i for i, line in enumerate(lines) if line.startswith('echo "== ')]
    loose = [lines[i] for i in heads[1:] if not lines[i - 1].startswith("# section: ")]
    if not heads or "preflight" not in lines[heads[0]] or loose:
        failures.append(f"tools/run_all_checks.sh: a heading after the parser preflight is not "
                        f"right under a `# section: NAME` line: {loose!r}")
    end = [i for i, line in enumerate(lines) if line == "# end of sections"]
    if len(end) != 1 or end[0] < heads[-1]:
        failures.append(f"tools/run_all_checks.sh needs 1 `# end of sections` line after the last "
                        f"section, found {len(end)}")
    d = Path(tempfile.mkdtemp())
    try:
        for sub in ("tools", "bin", "scripts", "site", "plugin"):
            (d / sub).mkdir()
        (d / "tools" / "run_all_checks.sh").write_text(text, encoding="utf-8")
        for name, body in BUILD_STANDINS.items():
            (d / "scripts" / name).write_text(body, encoding="utf-8")
        (d / "site" / "llms-full.txt").write_text("bundle\n", encoding="utf-8")
        (d / "plugin" / "plugin.json").write_text("{}\n", encoding="utf-8")
        standin = d / "bin" / "python3"
        standin.write_text(SECTIONS_STANDIN, encoding="utf-8")
        standin.chmod(0o755)
        log = d / "calls.log"
        for args, want_rc, needs, refuses, want_calls, fail in SECTIONS_CASES:
            log.write_text("", encoding="utf-8")
            env = dict(os.environ, PATH=f"{d / 'bin'}{os.pathsep}{os.environ.get('PATH', '')}",
                       STANDIN_LOG=str(log), STANDIN_FAIL=fail)
            r = subprocess.run(["bash", str(d / "tools" / "run_all_checks.sh"), *args],
                               capture_output=True, text=True, timeout=60, env=env)
            out = r.stdout + r.stderr
            calls = log.read_text(encoding="utf-8").splitlines()
            missing = [n for n in needs if n not in out]
            present = [n for n in refuses if n in out]
            if r.returncode != want_rc or missing or present or calls != want_calls:
                failures.append(f"--sections {args!r}: expected exit {want_rc} and calls "
                                f"{want_calls!r}; got exit {r.returncode}, calls {calls!r}, the "
                                f"output lacking {missing!r} or holding {present!r}: {out!r}")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return failures


def run_gate_source():
    """The ok and bad helpers and run_gate, read out of tools/run_all_checks.sh."""
    text = SUITE.read_text(encoding="utf-8")
    helpers = HELPER.findall(text)
    body = RUN_GATE.search(text)
    if len(helpers) != 2 or body is None:
        raise LookupError(f"tools/run_all_checks.sh no longer defines ok, bad and run_gate in the "
                          f"shape this test reads ({len(helpers)} helpers, run_gate "
                          f"{'found' if body else 'missing'})")
    return "\n".join(helpers) + "\n" + body.group(0) + "\n"


def run_gate_failures():
    failures = []
    try:
        source = run_gate_source()
    except (OSError, LookupError) as exc:
        return [f"run_gate: {exc}"]
    script = "fail=0\n" + source + 'run_gate stand-in bash -c "$STANDIN_GATE"\nprintf "fail=%s\\n" "$fail"\n'
    for gate, want_fail, needs, refuses in RUN_GATE_CASES:
        r = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=60,
                           env=dict(os.environ, STANDIN_GATE=gate))
        out = r.stdout + r.stderr
        lines = out.rstrip("\n").split("\n")
        got_fail = lines[-1] == "fail=1"
        if r.returncode or lines[-1] not in ("fail=0", "fail=1"):
            failures.append(f"run_gate on {gate!r}: the harness exited {r.returncode}: {out!r}")
        elif got_fail is not want_fail:
            failures.append(f"run_gate on {gate!r}: expected fail={int(want_fail)}: {out!r}")
        missing = [n for n in needs if n not in out]
        present = [n for n in refuses if n in out]
        if missing or present:
            failures.append(f"run_gate on {gate!r}: the output lacks {missing!r} or holds "
                            f"{present!r}: {out!r}")
    return failures


def build(script_text, version, fail=""):
    """Run a copy of pages-build.sh with the stand-in python3: (exit, stdout, stderr, calls)."""
    d = Path(tempfile.mkdtemp())
    try:
        (d / "scripts").mkdir()
        (d / "bin").mkdir()
        (d / "scripts" / "pages-build.sh").write_text(script_text, encoding="utf-8")
        standin = d / "bin" / "python3"
        standin.write_text(STANDIN, encoding="utf-8")
        standin.chmod(0o755)
        log = d / "calls.log"
        log.write_text("", encoding="utf-8")
        env = dict(os.environ, PATH=f"{d / 'bin'}{os.pathsep}{os.environ.get('PATH', '')}",
                   STANDIN_LOG=str(log), STANDIN_VERSION=version, STANDIN_PYTHON=sys.executable,
                   STANDIN_FAIL=fail)
        r = subprocess.run(["bash", str(d / "scripts" / "pages-build.sh")], capture_output=True,
                           text=True, timeout=60, env=env)
        return r.returncode, r.stdout, r.stderr, log.read_text(encoding="utf-8").splitlines()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def gates_of(text):
    """The stand-in's record of each gate call in a pages-build.sh text, outside comments."""
    return ["-I -B " + g for line in text.splitlines() if not line.lstrip().startswith("#")
            for g in GATE.findall(line)]


def version_check(calls):
    """True when the first call is the script's Python 3.11 check."""
    return bool(calls) and calls[0].startswith("-c ") and "(3, 11)" in calls[0]


def pages_build_failures():
    failures, count = [], 0
    committed = BUILD.read_text(encoding="utf-8")
    forms = {"the committed script": committed}
    for name, text in forms.items():
        gates = gates_of(text)
        if not gates:
            failures.append(f"pages-build.sh, {name}: no `python3 -I -B` gate call was found")
            continue
        rc, out, err, calls = build(text, "3.10.12")
        count += 1
        if (rc != 1 or "python3 is Python 3.10.12" not in err or "Python 3.11 or later" not in err
                or not version_check(calls) or calls[1:] != ["--version"] or PASSED in out):
            failures.append(f"pages-build.sh, {name}, with a python3 that reports 3.10 should stop "
                            f"before any gate: exit {rc}, calls {calls!r}, stdout {out!r}, "
                            f"stderr {err!r}")
        rc, out, err, calls = build(text, "3.11.5")
        count += 1
        if (rc != 0 or not version_check(calls) or calls[1:] != gates
                or out.rstrip("\n").split("\n")[-1] != PASSED):
            failures.append(f"pages-build.sh, {name}, with Python 3.11 should run the version "
                            f"check and then the gates {gates!r} in order: exit {rc}, calls "
                            f"{calls!r}, stdout {out!r}, stderr {err!r}")
        for i, gate in enumerate(gates):
            rc, out, err, calls = build(text, "3.11.5", fail=gate)
            count += 1
            if rc == 0 or not version_check(calls) or calls[1:] != gates[:i + 1] or PASSED in out:
                failures.append(f"pages-build.sh, {name}, with {gate!r} failing should stop there "
                                f"without passing: exit {rc}, calls {calls!r}, stdout {out!r}")
    return failures, count, list(forms)


def palette_gate_failures():
    """Both runners carry PALETTE_CALL outside a comment; pages-build.sh right after the pin gate."""
    failures = []
    for path in (BUILD, SUITE):
        lines = [line for line in path.read_text(encoding="utf-8").splitlines()
                 if not line.lstrip().startswith("#")]
        if not any(PALETTE_CALL in line for line in lines):
            failures.append(f"{path.relative_to(ROOT)} does not run the palette gate as "
                            f"{PALETTE_CALL!r}")
    gates = gates_of(BUILD.read_text(encoding="utf-8"))
    want = PALETTE_CALL[len("python3 "):]
    if want not in gates:
        failures.append(f"scripts/pages-build.sh: the palette call is not read as a gate, so the "
                        f"cases above do not run it: {gates!r}")
    elif PIN_GATE not in gates or gates.index(want) != gates.index(PIN_GATE) + 1:
        failures.append(f"scripts/pages-build.sh runs the palette gate, but not right after "
                        f"{PIN_GATE}, the gate that holds it to its pin: {gates!r}")
    return failures


def palette_block_source():
    """The ok and bad helpers and the palette block, read out of tools/run_all_checks.sh."""
    text = SUITE.read_text(encoding="utf-8")
    helpers = HELPER.findall(text)
    blocks = PALETTE_BLOCK.findall(text)
    if len(helpers) != 2 or len(blocks) != 1 or PALETTE_CALL not in blocks[0]:
        raise LookupError(f"tools/run_all_checks.sh no longer holds the ok and bad helpers and 1 "
                          f"palette block running {PALETTE_CALL!r} in the shape this test reads "
                          f"({len(helpers)} helpers, {len(blocks)} palette blocks)")
    return "\n".join(helpers) + "\n" + blocks[0] + "\n"


def palette_block_failures():
    """Run the palette block of tools/run_all_checks.sh on each of PALETTE_CASES."""
    try:
        source = palette_block_source()
    except (OSError, LookupError) as exc:
        return [f"palette block: {exc}"]
    standin = 'python3() { printf \'%s\\n\' "$*" >> "$STANDIN_LOG"; bash -c "$STANDIN_GATE"; }\n'
    script = "fail=0\n" + standin + source + 'printf "fail=%s\\n" "$fail"\n'
    want_call = [PALETTE_CALL[len("python3 "):]]
    failures = []
    d = Path(tempfile.mkdtemp())
    try:
        log = d / "calls.log"
        for gate, want_fail, needs, refuses in PALETTE_CASES:
            log.write_text("", encoding="utf-8")
            r = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=60,
                               env=dict(os.environ, STANDIN_GATE=gate, STANDIN_LOG=str(log)))
            out = r.stdout + r.stderr
            lines = out.rstrip("\n").split("\n")
            calls = log.read_text(encoding="utf-8").splitlines()
            if r.returncode or lines[-1] not in ("fail=0", "fail=1"):
                failures.append(f"palette block on {gate!r}: the harness exited {r.returncode}: "
                                f"{out!r}")
            elif (lines[-1] == "fail=1") is not want_fail:
                failures.append(f"palette block on {gate!r}: expected fail={int(want_fail)}: "
                                f"{out!r}")
            if calls != want_call:
                failures.append(f"palette block on {gate!r}: expected the 1 call {want_call!r}, "
                                f"got {calls!r}")
            missing = [n for n in needs if n not in out]
            present = [n for n in refuses if n in out]
            if missing or present:
                failures.append(f"palette block on {gate!r}: the output lacks {missing!r} or holds "
                                f"{present!r}: {out!r}")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return failures


def main():
    failures = run_gate_failures()
    build_failures, build_cases, forms = pages_build_failures()
    failures += build_failures
    failures += palette_gate_failures()
    failures += palette_block_failures()
    failures += sections_failures()
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {len(RUN_GATE_CASES)} run_gate cases and {build_cases} pages-build.sh cases "
          f"(Python 3.10 refused before any gate; with 3.11, every gate in order, and each gate's "
          f"failure stopping the build, in {' and '.join(forms)}), the palette gate in both "
          f"runners, {len(PALETTE_CASES)} cases of run_all_checks.sh's palette block (decided "
          f"by the exit code only: 0 passes, 1, 2, any other code and a crash fail, and an "
          f"exit 1 with a traceback line is reported as a crash), and "
          f"{len(SECTIONS_CASES)} cases of run_all_checks.sh --sections (only the named sections "
          f"and those they depend on after the preflight, in the file's order; an unknown or "
          f"empty name, or one holding "
          f"anything but letters, digits and hyphens, refused before any gate)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
