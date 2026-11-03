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

THE PALETTE GATE (baseline 1.6.0, mandatory on every site): both runners must carry the exact call
PALETTE_CALL outside a comment, pages-build.sh right after the pin gate that holds the copied gate
to its pin, so that the cases above run it in order and a failure there stops the deploy.

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
    if want in gates and (PIN_GATE not in gates or gates.index(want) != gates.index(PIN_GATE) + 1):
        failures.append(f"scripts/pages-build.sh runs the palette gate, but not right after "
                        f"{PIN_GATE}, the gate that holds it to its pin: {gates!r}")
    return failures


def main():
    failures = run_gate_failures()
    build_failures, build_cases, forms = pages_build_failures()
    failures += build_failures
    failures += palette_gate_failures()
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {len(RUN_GATE_CASES)} run_gate cases and {build_cases} pages-build.sh cases "
          f"(Python 3.10 refused before any gate; with 3.11, every gate in order, and each gate's "
          f"failure stopping the build, in {' and '.join(forms)}), and the palette gate in both "
          f"runners")
    return 0


if __name__ == "__main__":
    sys.exit(main())
