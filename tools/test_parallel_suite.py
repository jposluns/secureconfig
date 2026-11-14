#!/usr/bin/env python3
"""Cases for the opt-in parallel mode of tools/run_all_checks.sh (SECURECONFIG_SUITE_JOBS above 1).

HOW IT RUNS. The suite's own text is cut at its first `# section:` line and its `# end of sections`
line, and stand-in sections (shell bodies that record events, sleep, fail, exit or kill
themselves) are put between them. So the scheduler, the preflight, the helpers and the summary
under test are the committed code, and only the sections are stand-ins. The `# depends:` and
`# exclusive:` lines are replaced per case. python3 is a stand-in first on PATH that prints the
parser preflight's ok line, or its refusal for the preflight cases, and runs nothing else. Every
child's environment pins SECURECONFIG_SUITE_JOBS itself, never inheriting it. The 3 duplicated
cuts that only the real tree can answer (every section's body runs as its own bash process) are
the differential run below. Each case compares the parallel run with the serial run of the same
tree where the claim is "the same as serial".

THE CASES (the plan's numbers, plans/impl-parallel-suite-20261114.md):
  T1  output order: a slow first section does not move the output; jobs=4 and jobs=1 give the same
      bytes, in the file's order.
  T2  concurrency: with jobs=4 two sections overlap; unset, 1 and the preflight-only case never.
  T3  exit status: all pass is 0 and "All gates passed."; each position failing is 1 and "One or
      more gates failed."; --sections gives the selected-pass line; every output equals serial's.
  T4  a preflight refusal: status 2, only the preflight's lines, no section started, both modes.
  T5  SECURECONFIG_SUITE_JOBS refusals (0, -1, abc, empty, 1.5, 65, a newline, a leading space or
      zero, a sign) are status 2 before any heading; 1, 2 and 64 are accepted.
  T6  dependencies: generated-committed starts after llms-full and plugin ended; an unknown need,
      a malformed line, a cycle, and a bad or unknown `# exclusive:` name are refused with 2.
  T7  exclusivity: nothing starts while an exclusive section runs; one that depends on a running
      section waits for every running section, and nothing new starts meanwhile.
  T8  an early abort (a section running `exit 1`) and a signal death of a section end the run as
      the serial run ends: output through that section only, no summary, the same status; later
      sections are killed; an earlier slow section is still printed first.
  T9  HUP, INT and TERM sent to the driver kill every section's process group, remove its temp
      folder and are re-raised, including a TERM sent between a section's launch and the record
      of its PID.
  T10 a section that writes to stdout and stderr in turn prints them in the same order as serial.
  T12 the file's shape: 1 `# preflight` line before the first section, 1 `fail=0` before it, the
      `# exclusive:` lines name sections, `# depends:` stays the only line tools/select_gates.py
      reads, and a driver without its markers refuses instead of skipping the preflight.
  T13 tools/select_gates.py reads the `# depends:` lines only (the `# exclusive:` line is not one).

NOT HERE (run by hand, see main's --differential and --inject, because each runs the real suite
and so doubles its cost, which no gate pays): T11, the output identity of the real suite in both
modes, with the output normalised as DIFFERENTIAL_NORMALISE says and nothing else, and with a
failure injected into a section of each class; T14 and T15 are evidence in the pull request.

Nothing here runs a real gate. Exit 0 ok, 1 on a finding.
"""
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# SECURECONFIG_SUITE_UNDER_TEST names another copy of the suite, which the mutation runs of this test use.
SUITE = Path(os.environ.get("SECURECONFIG_SUITE_UNDER_TEST") or ROOT / "tools" / "run_all_checks.sh")
# Every wait is multiplied by this, so a loaded host can be given longer without a retry.
SCALE = float(os.environ.get("SECURECONFIG_TEST_LOAD_SCALE", "1"))
PREFLIGHT_OK = "  ok    gate parser preflight: stand-in"
PREFLIGHT_REFUSED = "  FAIL  gate parser preflight: stand-in refusal"
STANDIN_PYTHON = f"""#!/usr/bin/env bash
if [ "${{STANDIN_PREFLIGHT:-}}" = refuse ]; then
  printf '{PREFLIGHT_REFUSED}\\n'
  exit 2
fi
printf '{PREFLIGHT_OK}\\n'
"""
# The lines whose text differs from run to run, and what they are normalised to. Nothing else is
# left out of the differential comparison.
DIFFERENTIAL_NORMALISE = (
    # The credential scanner's elapsed time and its /proc sampling counts.
    (re.compile(r"^(  ok    credential scan: .*?; )[0-9.]+s(;.*?; sampling reads: ).*$"),
     r"\1<elapsed>s\2<counts>"),
    # unittest's elapsed time; the test count stays compared.
    (re.compile(r"^(Ran [0-9]+ tests? in )[0-9.]+s$"), r"\1<elapsed>s"),
)


def section(name, sleep="", extra="", pid_file=True):
    """A stand-in section: its heading, an event row at start and end, and one line of output."""
    lines = [f"# section: {name}", f'echo "== {name} =="',
             f'printf "%s start {name}\\n" "$EPOCHREALTIME" >> "$STANDIN_EVENTS"']
    if pid_file:
        lines.append(f'printf "%s\\n" "$$" > "$STANDIN_DIR/{name}.pid"')
    if sleep:
        lines.append(f"sleep {sleep}")
    if extra:
        lines.append(extra)
    lines += [f'echo "line from {name}"', f'printf "%s end {name}\\n" "$EPOCHREALTIME" >> "$STANDIN_EVENTS"', ""]
    return "\n".join(lines)


def synthetic(sections, depends="", exclusive="", drop=()):
    """The suite's text with stand-in sections, its `# depends:` and `# exclusive:` lines replaced
    (a line per entry), and any text in drop removed."""
    text = SUITE.read_text(encoding="utf-8")
    head = text[:text.index("\n# section: ") + 1]
    tail = text[text.index("# end of sections\n"):]
    head = re.sub(r"^# depends: .*\n", "".join(f"# depends: {d}\n" for d in depends), head, flags=re.M)
    head = re.sub(r"^# exclusive: .*\n", "".join(f"# exclusive: {e}\n" for e in exclusive), head,
                  flags=re.M)
    for part in drop:
        head = head.replace(part, "", 1)
    return head + "".join(sections) + tail


class Tree:
    """A scratch tree holding a suite text, the stand-in python3, and the event log."""

    def __init__(self, text):
        self.d = Path(tempfile.mkdtemp())
        (self.d / "tools").mkdir()
        (self.d / "bin").mkdir()
        (self.d / "tmp").mkdir()
        (self.d / "tools" / "run_all_checks.sh").write_text(text, encoding="utf-8")
        (self.d / "bin" / "python3").write_text(STANDIN_PYTHON, encoding="utf-8")
        (self.d / "bin" / "python3").chmod(0o755)
        (self.d / "events").write_text("", encoding="utf-8")

    def env(self, jobs, extra=None):
        env = dict(os.environ, PATH=f"{self.d / 'bin'}{os.pathsep}{os.environ.get('PATH', '')}",
                   STANDIN_EVENTS=str(self.d / "events"), STANDIN_DIR=str(self.d),
                   TMPDIR=str(self.d / "tmp"))
        env.pop("SECURECONFIG_SUITE_JOBS", None)
        if jobs is not None:
            env["SECURECONFIG_SUITE_JOBS"] = jobs
        env.update(extra or {})
        return env

    def start(self, args=(), jobs=None, extra=None):
        return subprocess.Popen(["bash", str(self.d / "tools" / "run_all_checks.sh"), *args],
                                cwd=self.d, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, env=self.env(jobs, extra), start_new_session=True)

    def run(self, args=(), jobs=None, extra=None):
        """(exit, merged output) of one run; a timeout stops the whole group and the exit is None."""
        p = self.start(args, jobs, extra)
        try:
            out, _ = p.communicate(timeout=120 * SCALE)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL)
            out, _ = p.communicate()
            return None, out
        return p.returncode, out

    def events(self):
        rows = []
        for line in (self.d / "events").read_text(encoding="utf-8").splitlines():
            t, kind, name = line.split()
            rows.append((float(t), kind, name))
        return sorted(rows)

    def when(self, kind, name):
        for t, k, n in self.events():
            if (k, n) == (kind, name):
                return t
        return None

    def leftovers(self):
        """Names of the recorded stand-in processes (section shells and their children) still running."""
        found = []
        for p in sorted(self.d.glob("*.pid")) + sorted(self.d.glob("*.child")):
            if alive(p):
                found.append(p.name)
        return found

    def close(self):
        for p in sorted(self.d.glob("*.pid")) + sorted(self.d.glob("*.child")):
            pid = alive(p)
            if pid:
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass
        shutil.rmtree(self.d, ignore_errors=True)


def alive(pid_file):
    """The PID recorded in pid_file when that process still runs and is not a zombie, else 0."""
    try:
        pid = int(pid_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0
    try:
        stat = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
    except OSError:
        return 0
    return 0 if stat.rpartition(") ")[2].startswith("Z") else pid


def wait_for(predicate, seconds):
    deadline = time.monotonic() + seconds * SCALE
    while not predicate() and time.monotonic() < deadline:
        time.sleep(0.05)
    return predicate()


def check(failures, label, ok, detail=""):
    if not ok:
        failures.append(f"{label}: {detail}")


def both(text, names=("a", "b"), args=(), jobs="4", extra=None):
    """Run one suite text serially (unset) and in parallel: ((rc, out), (rc, out), events by mode)."""
    results = []
    for j in (None, jobs):
        t = Tree(text)
        try:
            results.append((*t.run(args, j, extra), t.events()))
        finally:
            t.close()
    return results


def t1_order():
    failures = []
    names = ["a", "b", "c", "d"]
    text = synthetic([section("a", sleep="1.5"), *(section(n) for n in names[1:])], [], [])
    (src, sout, _), (prc, pout, _) = both(text)
    want = "".join(f"== {n} ==\nline from {n}\n" for n in names)
    check(failures, "T1 serial order", src == 0 and want in sout, repr(sout))
    check(failures, "T1 jobs=4 equals jobs unset byte for byte", (prc, pout) == (src, sout),
          f"{prc} {pout!r} vs {src} {sout!r}")
    return failures


def t2_concurrency():
    failures = []
    text = synthetic([section("a", sleep="0.8"), section("b", sleep="0.8"), section("c")], [], [])

    def overlap(events):
        spans = {}
        for t, kind, name in events:
            spans.setdefault(name, {})[kind] = t
        a, b = spans["a"], spans["b"]
        return a["start"] < b["end"] and b["start"] < a["end"]

    for jobs, want in ((None, False), ("1", False), ("4", True)):
        t = Tree(text)
        try:
            rc, out = t.run((), jobs)
            check(failures, f"T2 jobs={jobs} runs", rc == 0, repr(out))
            check(failures, f"T2 jobs={jobs} overlap is {want}", overlap(t.events()) is want,
                  repr(t.events()))
        finally:
            t.close()
    return failures


def t3_status():
    failures = []
    names = ["s1", "s2", "s3", "s4"]
    plain = [section(n) for n in names]
    t = Tree(synthetic(plain, [], []))
    try:
        for jobs in (None, "4"):
            rc, out = t.run((), jobs)
            check(failures, f"T3 all pass, jobs={jobs}", rc == 0 and out.endswith("\nAll gates passed.\n")
                  and "FAIL" not in out, repr(out))
            rc, out = t.run(("--sections", "s2,s4"), jobs)
            check(failures, f"T3 selected pass, jobs={jobs}", rc == 0 and out.endswith(
                "All selected gates passed (s2,s4); the other sections did not run.\n")
                  and "Sections selected: s2,s4\n" in out, repr(out))
    finally:
        t.close()
    for i, bad_one in enumerate(names):
        text = synthetic([section(n, extra=f'bad "{n} failed"' if n == bad_one else "")
                          for n in names], [], [])
        (src, sout, _), (prc, pout, _) = both(text)
        check(failures, f"T3 {bad_one} failing", src == 1 and prc == 1 and sout == pout
              and sout.endswith("\nOne or more gates failed.\n") and f"  FAIL  {bad_one} failed" in pout,
              f"serial {src} {sout!r}, parallel {prc} {pout!r}")
        (src, sout, _), (prc, pout, _) = both(text, args=("--sections", f"{names[0]},{bad_one}"))
        check(failures, f"T3 --sections with {bad_one} failing", src == 1 and prc == 1 and sout == pout,
              f"serial {src} {sout!r}, parallel {prc} {pout!r}")
    return failures


def t4_preflight():
    failures = []
    text = synthetic([section("a"), section("b")], [], [])
    for jobs in (None, "4"):
        t = Tree(text)
        try:
            rc, out = t.run((), jobs, {"STANDIN_PREFLIGHT": "refuse"})
            started = t.events()
            check(failures, f"T4 preflight refusal, jobs={jobs}", rc == 2 and not started
                  and out == f"== gate parser preflight: this python3 has the pinned markdown-it-py ==\n{PREFLIGHT_REFUSED}\n",
                  f"{rc} {out!r} {started!r}")
        finally:
            t.close()
    return failures


def t5_refusals():
    failures = []
    text = synthetic([section("a"), section("b")], [], [])
    for value in ("0", "-1", "abc", "", "1.5", "65", "4\n", " 4", "01", "+2", "4 ", "999", "1e1"):
        for args in ((), ("--sections", "a")):
            t = Tree(text)
            try:
                rc, out = t.run(args, value)
                check(failures, f"T5 SECURECONFIG_SUITE_JOBS={value!r} {args}", rc == 2
                      and out.startswith("  FAIL  SECURECONFIG_SUITE_JOBS is '") and "== " not in out
                      and not t.events(), f"{rc} {out!r}")
            finally:
                t.close()
    for value in ("1", "2", "64"):
        t = Tree(text)
        try:
            rc, out = t.run((), value)
            check(failures, f"T5 SECURECONFIG_SUITE_JOBS={value} accepted", rc == 0
                  and out.endswith("All gates passed.\n"), f"{rc} {out!r}")
        finally:
            t.close()
    return failures


def t6_dependencies():
    failures = []
    base = [section("a"), section("llms-full", sleep="0.4"), section("plugin", sleep="0.8"),
            section("generated-committed"), section("z")]
    t = Tree(synthetic(base, ["generated-committed: llms-full plugin"], ["llms-full plugin"]))
    try:
        rc, out = t.run((), "4")
        start = t.when("start", "generated-committed")
        check(failures, "T6 generated-committed after llms-full and plugin", rc == 0
              and start is not None and start >= t.when("end", "llms-full")
              and start >= t.when("end", "plugin"), repr(t.events()))
    finally:
        t.close()
    # Without the exclusive line the edge alone still orders it: its needs end first.
    t = Tree(synthetic(base, ["generated-committed: llms-full plugin"], []))
    try:
        rc, out = t.run((), "4")
        start = t.when("start", "generated-committed")
        check(failures, "T6 the depends line alone orders it", rc == 0 and start is not None
              and start >= t.when("end", "llms-full") and start >= t.when("end", "plugin"),
              repr(t.events()))
    finally:
        t.close()
    refused = (
        ("an unknown need", ["a: nosuch"], [], "needs 'nosuch', which is not a section"),
        ("a malformed depends line", ["a z"], [], "is not 'NAME: NEED...'"),
        ("a cycle", ["a: z", "z: a"], [], "hold a cycle"),
        ("a self cycle", ["a: a"], [], "hold a cycle"),
        ("an unknown exclusive name", [], ["a nosuch"], "names 'nosuch', which is not a section"),
        ("a bad exclusive name", [], ["a B!"], "names ''"),
    )
    for label, depends, exclusive, text_needed in refused:
        t = Tree(synthetic(base, depends, exclusive))
        try:
            rc, out = t.run((), "4")
            check(failures, f"T6 {label} refused", rc == 2 and text_needed in out and "== " not in out
                  and not t.events(), f"{rc} {out!r}")
        finally:
            t.close()
    return failures


def t7_exclusive():
    failures = []
    secs = [section("p1", sleep="0.3"), section("p2", sleep="1.5"), section("p3", sleep="0.3"),
            section("x", sleep="0.6")]
    t = Tree(synthetic(secs, ["x: p1"], ["x"]))
    try:
        rc, out = t.run((), "2")
        ev = {(k, n): tm for tm, k, n in t.events()}
        check(failures, "T7 runs", rc == 0, repr(out))
        if rc == 0:
            check(failures, "T7 an exclusive section waits for every running section",
                  ev[("start", "x")] >= ev[("end", "p1")] and ev[("start", "x")] >= ev[("end", "p2")],
                  repr(t.events()))
            check(failures, "T7 nothing starts while it runs or while it is ready",
                  ev[("start", "p3")] >= ev[("end", "x")], repr(t.events()))
    finally:
        t.close()
    # With no dependency the exclusive section runs first and alone.
    secs = [section("p1", sleep="0.3"), section("p2", sleep="0.3"), section("x", sleep="0.6")]
    t = Tree(synthetic(secs, [], ["x"]))
    try:
        rc, out = t.run((), "4")
        ev = {(k, n): tm for tm, k, n in t.events()}
        check(failures, "T7 an exclusive section runs first, alone", rc == 0
              and ev[("end", "x")] <= ev[("start", "p1")] and ev[("end", "x")] <= ev[("start", "p2")],
              repr(t.events()))
        check(failures, "T7 and prints in the file's order", rc == 0 and out.index("== p1 ==")
              < out.index("== p2 ==") < out.index("== x =="), repr(out))
    finally:
        t.close()
    return failures


def t8_abort():
    failures = []
    # The run ends at s2 for exit 1 and for a signal death; s1 is slower and still prints first.
    for label, extra, want_rc in (("exit 1", "exit 1", 1), ("KILL", 'kill -KILL "$$"', -9),
                                  ("TERM", 'kill -TERM "$$"', -15)):
        secs = [section("s1", sleep="1.5"), section("s2", extra=extra),
                section("s3", extra='sleep 60 & printf "%s\\n" "$!" > "$STANDIN_DIR/s3.child"; wait'),
                section("s4")]
        results = []
        for jobs in (None, "4"):
            t = Tree(synthetic(secs, [], []))
            try:
                rc, out = t.run((), jobs)
                left = t.leftovers()
                results.append((rc, out))
                check(failures, f"T8 {label}, jobs={jobs}", rc == want_rc and "== s1 ==\nline from s1\n" in out
                      and "== s2 ==" in out and "== s3 ==" not in out and "== s4 ==" not in out
                      and "All gates passed" not in out and "One or more gates failed" not in out
                      and not left, f"{rc} {out!r} still running {left!r}")
            finally:
                t.close()
        # No bash "Killed" or "Terminated" job notice for the dead section: byte for byte as serial.
        check(failures, f"T8 {label}: the same output as serial", results[0][1] == results[1][1],
              f"{results[0][1]!r} vs {results[1][1]!r}")
    # Under --sections the serial run's parent shell exits with 128 plus the signal, and so does this.
    secs = [section("s1"), section("s2", extra='kill -TERM "$$"'), section("s3")]
    (src, sout, _), (prc, pout, _) = both(synthetic(secs, [], []), args=("--sections", "s1,s2,s3"))
    check(failures, "T8 a section killed by TERM under --sections", src == prc == 143, f"{src} {prc}")
    return failures


def sleepers(n):
    return [section(f"s{i}", extra='sleep 60 & printf "%s\\n" "$!" > "$STANDIN_DIR/' + f's{i}.child"; wait')
            for i in range(1, n + 1)]


def signal_run(text, sig, injected=None, wait_names=("s1", "s2", "s3")):
    """Run the parallel suite, send sig to the driver once every wait_names child runs (at once when
    injected), and return (exit, output, leftovers, temp entries left)."""
    t = Tree(injected or text)
    try:
        p = t.start((), "4")
        if injected is None:
            wait_for(lambda: all((t.d / f"{n}.child").exists() for n in wait_names)
                     or p.poll() is not None, 60)
            if p.poll() is None:
                p.send_signal(sig)
        try:
            out, _ = p.communicate(timeout=60 * SCALE)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL)
            out, _ = p.communicate()
            return None, out, ["the driver"], []
        # What the group's sections left is given a moment to end after the driver is gone.
        wait_for(lambda: not t.leftovers(), 5)
        return p.returncode, out, t.leftovers(), sorted(x.name for x in (t.d / "tmp").iterdir())
    finally:
        t.close()


def t9_signals():
    failures = []
    text = synthetic(sleepers(3), [], [])
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        rc, out, left, tmp = signal_run(text, sig)
        check(failures, f"T9 {sig.name} to the driver", rc == -sig and not left and not tmp,
              f"exit {rc}, still running {left!r}, temp left {tmp!r}: {out!r}")
    # A TERM sent just before the record of a launch's PID is held and acted on once it is.
    line = "  par_pid[i]=$!\n"
    src = synthetic(sleepers(3), [], [])
    if src.count(line) != 1:
        failures.append(f"T9 the record of a section's PID, {line!r}, is not in the driver once")
    else:
        injected = src.replace(line, f'  kill -TERM "$BASHPID"\n{line}')
        rc, out, left, tmp = signal_run(text, signal.SIGTERM, injected=injected)
        check(failures, "T9 a TERM between a launch and the record of its PID", rc == -signal.SIGTERM
              and not left and not tmp, f"exit {rc}, still running {left!r}, temp left {tmp!r}: {out!r}")
    return failures


def t10_merged():
    failures = []
    mix = section("mix", extra="echo o1; echo e1 >&2; echo o2; echo e2 >&2; echo o3; echo e3 >&2")
    text = synthetic([mix, section("b")], [], [])
    (src, sout, _), (prc, pout, _) = both(text)
    check(failures, "T10 stdout and stderr keep their order", src == 0 and (prc, pout) == (src, sout)
          and "o1\ne1\no2\ne2\no3\ne3\n" in pout, f"{sout!r} vs {pout!r}")
    return failures


def t12_shape():
    failures = []
    text = SUITE.read_text(encoding="utf-8")
    lines = text.split("\n")
    first = next(i for i, line in enumerate(lines) if line.startswith("# section: "))
    marks = [i for i, line in enumerate(lines) if line == "# preflight"]
    check(failures, "T12 one `# preflight` line, before the first section and right above the "
          "preflight heading", len(marks) == 1 and marks[0] < first
          and lines[marks[0] + 1].startswith('echo "== gate parser preflight'), repr(marks))
    zeros = [i for i, line in enumerate(lines) if line == "fail=0"]
    check(failures, "T12 one `fail=0` line, before the preflight", len(zeros) == 1 and marks
          and zeros[0] < marks[0], repr(zeros))
    sections = re.findall(r"^# section: ([a-z0-9-]+)$", text, re.M)
    for line in re.findall(r"^# exclusive:.*$", text, re.M):
        m = re.fullmatch(r"# exclusive: ([a-z0-9-]+(?: [a-z0-9-]+)*)", line)
        check(failures, f"T12 {line!r} is `# exclusive: NAME...` naming sections",
              m is not None and all(n in sections for n in m[1].split()), "")
    # A driver whose markers are gone must refuse, never run without its preflight.
    for label, drop in (("no `# preflight` line", "# preflight\n"), ("no `fail=0` line", "\nfail=0\n")):
        src = synthetic([section("a")], [], [])
        if drop not in src:
            failures.append(f"T12 {label}: the text to drop, {drop!r}, is not in the suite")
            continue
        t = Tree(src.replace(drop, "\n" if drop.startswith("\n") else "", 1))
        try:
            rc, out = t.run((), "4")
            check(failures, f"T12 a driver with {label} refuses", rc == 2 and "no gate ran" in out
                  and PREFLIGHT_OK not in out and not t.events(), f"{rc} {out!r}")
        finally:
            t.close()
    return failures


def t13_select_gates():
    failures = []
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        import select_gates
    finally:
        sys.path.pop(0)
    depends = select_gates.suite_depends(SUITE.read_text(encoding="utf-8"))
    check(failures, "T13 select_gates reads the `# depends:` line and not `# exclusive:`",
          depends == {"generated-committed": ["llms-full", "plugin"]}
          or depends == {"generated-committed": ("llms-full", "plugin")}, repr(depends))
    return failures


CASES = (t1_order, t2_concurrency, t3_status, t4_preflight, t5_refusals, t6_dependencies,
         t7_exclusive, t8_abort, t9_signals, t10_merged, t12_shape, t13_select_gates)


def normalise(output):
    """output with each DIFFERENTIAL_NORMALISE substitution applied line by line."""
    lines = []
    for line in output.split("\n"):
        for pattern, repl in DIFFERENTIAL_NORMALISE:
            line = pattern.sub(repl, line)
        lines.append(line)
    return "\n".join(lines)


def run_real(root, jobs, args=(), env_extra=None):
    """The real suite of the tree at root: (exit, merged output, seconds)."""
    env = dict(os.environ, **(env_extra or {}))
    env.pop("SECURECONFIG_SUITE_JOBS", None)
    if jobs:
        env["SECURECONFIG_SUITE_JOBS"] = str(jobs)
    t0 = time.monotonic()
    p = subprocess.run([str(root / "tools" / "run_all_checks.sh"), *args], cwd=root,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
    return p.returncode, p.stdout, time.monotonic() - t0


def differential(jobs="8"):
    """T11: the real suite on this tree, serial and parallel, compared after normalise()."""
    src, sout, st = run_real(ROOT, None)
    prc, pout, pt = run_real(ROOT, jobs)
    print(f"serial {st:.0f} s exit {src}; parallel (JOBS={jobs}) {pt:.0f} s exit {prc}")
    a, b = normalise(sout).split("\n"), normalise(pout).split("\n")
    diff = [(i, x, y) for i, (x, y) in enumerate(zip(a, b)) if x != y]
    if src != prc or len(a) != len(b) or diff:
        print(f"  FAIL  serial and parallel differ: exits {src}/{prc}, lines {len(a)}/{len(b)}, "
              f"first differences {diff[:5]!r}")
        return 1
    print(f"  ok    {len(a)} lines identical after normalising {len(DIFFERENTIAL_NORMALISE)} line "
          f"classes; exit {src} in both")
    return 0


# T11's injected failures: (label, section, line put right after the section's heading, sections run).
INJECTIONS = (
    ("a class P section fails", "walker", 'bad "injected failure"', "walker,secrets-tests"),
    ("plugin fails", "plugin", 'bad "injected failure"', "plugin,walker"),
    ("generated-committed fails", "generated-committed", 'bad "injected failure"',
     "generated-committed,walker"),
    ("a class P section exits 1", "walker", "exit 1", "walker,secrets-tests"),
    ("a section kills itself with TERM", "secrets-tests", 'kill -TERM "$$"', "walker,secrets-tests"),
)


def inject(jobs="8"):
    """T11, with a failure injected into a section of a clone of HEAD: for each of INJECTIONS the
    suite runs serial and parallel on --sections, and the exit status (or signal) and the
    normalised output must be equal."""
    scratch = Path(tempfile.mkdtemp(prefix="parallel-inject."))
    tree = scratch / "tree"
    code = 0
    try:
        subprocess.run(["git", "clone", "-q", "--local", str(ROOT), str(tree)], check=True)
        original = (tree / "tools" / "run_all_checks.sh").read_text(encoding="utf-8")
        for label, name, line, sections in INJECTIONS:
            text, n = re.subn(rf'(^# section: {re.escape(name)}\necho "[^\n]*"\n)', rf"\g<1>{line}\n",
                              original, flags=re.M)
            if n != 1:
                print(f"  FAIL  {label}: section {name} not found once")
                code = 1
                continue
            (tree / "tools" / "run_all_checks.sh").write_text(text, encoding="utf-8")
            src, sout, st = run_real(tree, None, ("--sections", sections))
            prc, pout, pt = run_real(tree, jobs, ("--sections", sections))
            same = src == prc and normalise(sout) == normalise(pout)
            print(f"  {'ok  ' if same else 'FAIL'}  {label}: serial exit {src} in {st:.0f} s, parallel "
                  f"exit {prc} in {pt:.0f} s, {len(sout.splitlines())} lines")
            if not same:
                code = 1
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return code


def main():
    if "--inject" in sys.argv:
        return inject()
    if "--differential" in sys.argv:
        return differential(sys.argv[sys.argv.index("--differential") + 1]
                            if len(sys.argv) > sys.argv.index("--differential") + 1 else "8")
    failures = []
    for case in CASES:
        failures += case()
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {len(CASES)} groups of cases of the parallel mode of run_all_checks.sh (output "
          f"order and bytes equal to serial, real concurrency, exit status, preflight and "
          f"SECURECONFIG_SUITE_JOBS refusals, dependencies and cycles, exclusive sections, early "
          f"abort and signal death of a section, HUP, INT and TERM to the driver including between "
          f"a launch and the record of its PID, merged streams, the file's shape)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
