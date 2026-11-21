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

THE CASES (numbered as in the implementation plan, which is not in this repository):
  T1  output order: a slow first section does not move the output; jobs=4 and jobs=1 give the same
      bytes, in the file's order.
  T2  concurrency: with jobs=4 two sections overlap; unset and 1 never.
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
      sections are killed; an earlier slow section is still printed first. Under --sections a
      death by TERM, KILL or HUP is 128 plus the signal in both modes, and an unbound variable in a
      section is 1 in a whole run and 127 under --sections in both modes.
  T9  HUP, INT and TERM sent to the driver kill every section's process group, remove its temp
      folder and are re-raised, including a TERM sent between a section's launch and the record
      of its PID, judged only after a bounded wait for the files an unstopped section writes; and
      the driver's own death by an untrapped USR1 just after a launch, by a TERM before its traps
      are set, or by a failed fork leaves no temp folder (rows 3.103 and 3.113).
  T10 a section that writes to stdout and stderr in turn prints them in the same order as serial.
  T11 (the part that needs no real suite) the normaliser of the differential run rewrites or drops
      only the fields and lines it names (the job notice in its TERM, KILL, HUP, ABRT, "I/O
      possible" and "Real-time signal N" forms);
      the differential itself is below.
  T12 the file's shape: 1 `# preflight` line before the first section, 1 `fail=0` before it, the
      `# exclusive:` lines name sections, `# depends:` stays the only line tools/select_gates.py
      reads, and a driver without its markers refuses instead of skipping the preflight.
  T13 tools/select_gates.py reads the `# depends:` lines only (the `# exclusive:` line is not one).
  T16 SECURECONFIG_SUITE_TIMES gets one row per section in parallel mode and none in serial mode,
      changes no output, and a caller's setting never reaches these stand-in runs.
  T17 (serial mode, not the parallel one, with its own ok line, and alone with --terminal) the
      serial run of one stand-in section, whose foreground gate sleeps and then writes to the
      terminal, on a pseudo-terminal. A job-control shell (JOBCTL) starts the driver in a process
      group of its own and makes it the terminal's foreground group. Under --sections: Ctrl-C ends
      the run by INT with the section's shell and the gate gone; Ctrl-Z stops the driver, the
      section's shell and the gate, and fg resumes them to a run that ends with 0; under `stty
      tostop` the run ends with 0 and no stop. A TERM sent only to the driver's PID, under
      --sections and in a whole run, ends the driver by TERM with nothing printed after the
      section's heading, and 3 seconds later the section's shell and its gate are gone and the
      gate wrote nothing late (row 3.49, which the serial run's supervisor fixed). A KILL and a
      USR1 sent only to the driver's PID in a whole run of 2 sections end the driver by that
      signal, and no output follows the exit: within 15 seconds the section's shell, its gate and
      the rest of the driver's process group are gone, the gate wrote nothing late and the second
      section never started (the supervisor's watcher). Without a pseudo-terminal the group prints
      a SKIP line saying why.

NOT HERE (run by hand, see main's --differential and --inject, because each runs the real suite
and so doubles its cost, which no gate pays): T11, the output identity of the real suite in both
modes, with the output normalised as DIFFERENTIAL_NORMALISE says and nothing else, and with a
failure injected into a section of each class; T14 and T15 are evidence in the pull request.

Nothing here runs a real gate. Exit 0 ok, 1 on a finding.
"""
import os
import pty
import re
import select
import shutil
import signal
import subprocess
import sys
import tempfile
import termios
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
# The real mktemp is the first one on PATH after the tree's bin, which Tree.env puts first.
STANDIN_MKTEMP = """#!/usr/bin/env bash
made=$(PATH=${PATH#*:} mktemp "$@") || exit
printf '%s\\n' "$made"
kill -TERM 0
"""
# The lines whose text differs from run to run, and what they are normalised to. Nothing else is
# left out of the differential comparison.
DIFFERENTIAL_NORMALISE = (
    # The credential scanner's elapsed time and its /proc sampling counts.
    (re.compile(r"^(  ok    credential scan: .*?; )[0-9.]+s(;.*?; sampling reads: ).*$"),
     r"\1<elapsed>s\2<counts>"),
    # unittest's elapsed time; the test count stays compared.
    (re.compile(r"^(Ran [0-9]+ tests? in )[0-9.]+s$"), r"\1<elapsed>s"),
    # The job notice bash prints, only for the serial `--sections` run, when the shell running the
    # cut copy dies by a signal: a line dropped, not rewritten. For TERM it is the bare notice
    # ("Terminated   bash -c '. /dev/fd/3' ..."); for KILL, HUP, ABRT and the others bash puts the
    # script's name, a line number and the PID before it ("<script>: line 485: 1234567 Killed   ..."),
    # and ABRT adds "(core dumped)"; INT prints none, and PIPE printed none with bash 5.3.9 in the
    # #1312 review. A 4-digit PID follows two spaces, as in "line 485:  7200 Killed" (row 3.88).
    # The description is bash's text for the signal, so it may hold "/" or "-" ("I/O possible",
    # "Real-time signal 3"). Only TERM's notice is bare, and only a notice for this exact command
    # line is dropped. The parallel run prints none, and the exit status is the same.
    (re.compile(r"^(?:\S.*: line [0-9]+: +[0-9]+ [A-Z][A-Za-z0-9 /-]*?|Terminated) +(?:\(core dumped\) )?"
                r"bash -c '\. /dev/fd/3' \"\$PWD/tools/run_all_checks\.sh\" 3<<< \"\$script\"$"), None),
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
        # A caller's timing file is the caller's: these stand-in runs never add rows to it.
        env.pop("SECURECONFIG_SUITE_TIMES", None)
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
        launched = self.d / "launched.pid"
        if launched.exists():
            try:
                os.killpg(int(launched.read_text(encoding="utf-8")), signal.SIGKILL)
            except (OSError, ValueError):
                pass
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
    # Under --sections the serial run's parent shell exits with 128 plus the signal, and so does
    # this; the outputs differ only in the job notice the normaliser drops.
    for sig, want in (("TERM", 143), ("KILL", 137), ("HUP", 129)):
        secs = [section("s1"), section("s2", extra=f'kill -{sig} "$$"'), section("s3")]
        (src, sout, _), (prc, pout, _) = both(synthetic(secs, [], []), args=("--sections", "s1,s2,s3"))
        check(failures, f"T8 a section killed by {sig} under --sections", src == prc == want
              and normalise(sout) == normalise(pout) and "== s3 ==" not in pout,
              f"serial {src} {sout!r}, parallel {prc} {pout!r}")
    # A fatal shell error in a section (an unbound variable under set -u) ends a whole run with 1
    # and a --sections run with 127, the status of the sourced cut copy, in both modes. Only bash's
    # own diagnostic line differs (the header says how), so the rest is compared without it.
    secs = [section("s1"), section("s2", extra='echo "$no_such_variable_here"'), section("s3")]
    for args, want in (((), 1), (("--sections", "s1,s2,s3"), 127)):
        (src, sout, _), (prc, pout, _) = both(synthetic(secs, [], []), args=args)

        def rest(out):
            return [x for x in out.splitlines() if not x.endswith(": no_such_variable_here: unbound variable")]

        check(failures, f"T8 an unbound variable in a section, args {args}", src == prc == want
              and rest(sout) == rest(pout) and "== s3 ==" not in pout
              and "no_such_variable_here: unbound variable" in pout,
              f"serial {src} {sout!r}, parallel {prc} {pout!r}")
    return failures


def sleepers(n):
    return [section(f"s{i}", extra='sleep 60 & printf "%s\\n" "$!" > "$STANDIN_DIR/' + f's{i}.child"; wait')
            for i in range(1, n + 1)]


def signal_run(text, sig, injected=None, wait_names=("s1", "s2", "s3"), late=(), extra_bin=None):
    """Run the parallel suite, send sig to the driver once every wait_names child runs (at once when
    injected), and return (exit, output, leftovers, temp entries left). With late, once the driver
    is gone, first wait up to 3 seconds for those files under the tree, which a section forked
    just before the signal writes when it is not stopped; launched.pid among them also counts every
    live process of that PID's process group as left over. extra_bin maps a name to the text of a
    stand-in command put first on PATH."""
    t = Tree(injected or text)
    for name, body in (extra_bin or {}).items():
        (t.d / "bin" / name).write_text(body, encoding="utf-8")
        (t.d / "bin" / name).chmod(0o755)
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
        if late:
            wait_for(lambda: all((t.d / n).exists() for n in late), 3)

        def left():
            found = t.leftovers()
            launched = t.d / "launched.pid"
            if launched.exists():
                try:
                    found += [f"group {launched.read_text(encoding='utf-8').strip()} member {pid}"
                              for pid in group_alive(int(launched.read_text(encoding="utf-8")))]
                except ValueError:
                    found.append("launched.pid unreadable")
            return found

        # What the group's sections left is given a moment to end after the driver is gone.
        wait_for(lambda: not left(), 5)
        return p.returncode, out, left(), sorted(x.name for x in (t.d / "tmp").iterdir())
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
    # The driver itself writes the launched section's PID (its process group) to launched.pid, then
    # waits, bounded, until the section runs (its own .pid file exists), and only then sends the
    # TERM, still before the record of the PID. Without that wait a driver that does not hold the
    # signal removes its temp folder before the section's bash has opened its script, the section
    # ends by itself, and the broken hold goes unseen (6 of 10 runs of that mutant). Once the
    # driver is gone the case waits, bounded, for s1.pid and s1.child, and then judges what is left,
    # counting every live process of the launched group.
    line = "  par_pid[i]=$!\n"
    src = synthetic(sleepers(3), [], [])
    if src.count(line) != 1:
        failures.append(f"T9 the record of a section's PID, {line!r}, is not in the driver once")
    else:
        hold = max(1, int(1000 * SCALE))
        injected = src.replace(line, '  printf "%s\\n" "$!" > "$STANDIN_DIR/launched.pid"\n'
                                     f'  for _ in $(seq {hold}); do [ -e "$STANDIN_DIR/$name.pid" ] && break; '
                                     'sleep 0.01; done\n'
                                     f'  kill -TERM "$BASHPID"\n{line}')
        rc, out, left, tmp = signal_run(text, signal.SIGTERM, injected=injected,
                                        late=("launched.pid", "s1.pid", "s1.child"))
        check(failures, "T9 a TERM between a launch and the record of its PID", rc == -signal.SIGTERM
              and not left and not tmp, f"exit {rc}, still running {left!r}, temp left {tmp!r}: {out!r}")
        # Rows 3.103 and 3.113: the driver's own death, however it comes, leaves no temp folder.
        # A USR1, which the driver does not trap, just after a launch's PID is recorded (row 3.103's
        # window, where no EXIT trap was set), and a TERM once the folder exists and before the
        # driver's traps are set (row 3.113). The USR1 does not stop the sections, which run on in
        # their own process groups, so only the exit and the temp folder are judged; Tree.close
        # stops the sections.
        usr1 = src.replace(line, f'{line}  kill -USR1 "$BASHPID"\n')
        rc, out, left, tmp = signal_run(text, signal.SIGUSR1, injected=usr1)
        check(failures, "T9 a USR1 just after the record of a launch's PID", rc == -signal.SIGUSR1
              and not tmp, f"exit {rc}, temp left {tmp!r}: {out!r}")
    # A stand-in mktemp, first on PATH, makes the folder with the real one, prints its name and
    # sends a TERM to the driver's process group, so the TERM arrives once the folder exists and
    # before the driver can set its traps, wherever in the driver mktemp runs.
    rc, out, left, tmp = signal_run(text, None, injected=text, extra_bin={"mktemp": STANDIN_MKTEMP})
    check(failures, "T9 a TERM once the temp folder exists, before the driver's traps are set",
          rc == -signal.SIGTERM and not left and not tmp,
          f"exit {rc}, still running {left!r}, temp left {tmp!r}: {out!r}")
    # A failed fork ends the driver with 254 (bash 5.3.9). ulimit -u 1 fails every fork of the
    # driver from the second launch on and changes no other process's limit; root is not held to it.
    fork = "  set -m\n"
    if os.geteuid() == 0:
        failures.append("T9 runs as root, which ulimit -u does not hold, so a failed fork cannot be made")
    elif src.count(fork) != 1:
        failures.append(f"T9 the launch's {fork!r} is not in the driver once")
    else:
        failed = src.replace(fork, f'  [ "$i" -lt 1 ] || ulimit -u 1\n{fork}')
        rc, out, left, tmp = signal_run(text, None, injected=failed)
        check(failures, "T9 a failed fork of a launch", rc == 254 and "fork: Resource temporarily "
              "unavailable" in out and not tmp, f"exit {rc}, temp left {tmp!r}: {out!r}")
    return failures


def group_alive(pgid):
    """The PIDs of live (not zombie) processes in process group pgid."""
    found = []
    for stat in Path("/proc").glob("[0-9]*/stat"):
        try:
            fields = stat.read_text(encoding="utf-8").rpartition(") ")[2].split()
        except OSError:
            continue
        if len(fields) > 2 and fields[2] == str(pgid) and not fields[0].startswith("Z"):
            found.append(stat.parent.name)
    return found


def t10_merged():
    failures = []
    mix = section("mix", extra="echo o1; echo e1 >&2; echo o2; echo e2 >&2; echo o3; echo e3 >&2")
    text = synthetic([mix, section("b")], [], [])
    (src, sout, _), (prc, pout, _) = both(text)
    check(failures, "T10 stdout and stderr keep their order", src == 0 and (prc, pout) == (src, sout)
          and "o1\ne1\no2\ne2\no3\ne3\n" in pout, f"{sout!r} vs {pout!r}")
    return failures


def t16_times():
    """SECURECONFIG_SUITE_TIMES: one row per section in parallel mode, none in serial mode, the
    output unchanged, and a caller's setting never reaches the stand-in runs."""
    failures = []
    names = ["a", "b", "c"]
    text = synthetic([section(n) for n in names], [], [])
    t = Tree(text)
    outer = t.d / "outer-times"
    saved = os.environ.get("SECURECONFIG_SUITE_TIMES")
    os.environ["SECURECONFIG_SUITE_TIMES"] = str(outer)
    try:
        check(failures, "T16 the harness's child environment drops a caller's SECURECONFIG_SUITE_TIMES",
              "SECURECONFIG_SUITE_TIMES" not in t.env("4"), "")
        rc, plain = t.run((), "4")
        check(failures, "T16 a caller's SECURECONFIG_SUITE_TIMES gets no row from a stand-in run",
              rc == 0 and not outer.exists(), f"{rc} {outer.read_text(encoding='utf-8') if outer.exists() else ''!r}")
    finally:
        if saved is None:
            os.environ.pop("SECURECONFIG_SUITE_TIMES", None)
        else:
            os.environ["SECURECONFIG_SUITE_TIMES"] = saved
    try:
        for jobs, label in ((None, "serial"), ("4", "parallel")):
            times = t.d / f"times-{label}"
            rc, out = t.run((), jobs, {"SECURECONFIG_SUITE_TIMES": str(times)})
            check(failures, f"T16 {label} output is unchanged by SECURECONFIG_SUITE_TIMES",
                  rc == 0 and out == plain, f"{rc} {out!r} vs {plain!r}")
            if jobs is None:
                check(failures, "T16 a serial run writes no row", not times.exists(), "")
                continue
            rows = times.read_text(encoding="utf-8").splitlines() if times.exists() else []
            good = [r.split() for r in rows]
            check(failures, "T16 a parallel run writes `<section> <start> <end> <status>` per section in "
                  "the file's order", [r[0] for r in good if len(r) == 4] == names
                  and all(len(r) == 4 and float(r[1]) <= float(r[2]) and r[3] == "0" for r in good),
                  repr(rows))
    finally:
        t.close()
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
          depends == {"generated-committed": ["llms-full", "plugin", "instructions"]}
          or depends == {"generated-committed": ("llms-full", "plugin", "instructions")},
          repr(depends))
    return failures


def t11_normaliser():
    """The line classes DIFFERENTIAL_NORMALISE leaves out, and nothing else, on recorded lines."""
    failures = []
    scan = ("  ok    credential scan: 315 cases; 0 skips; {t}s; {{'CHECK': 19, 'FOUND': 164}}; "
            "sampling reads: {c} cmdline, 5 environ, 1 denied")
    same = (normalise(scan.format(t="36.30", c="50948")) == normalise(scan.format(t="35.57", c="1"))
            and "36.30" not in normalise(scan.format(t="36.30", c="50948"))
            and "'FOUND': 164" in normalise(scan.format(t="36.30", c="50948")))
    check(failures, "T11 the scanner's elapsed time and sampling counts are left out, its case counts "
          "are not", same, normalise(scan.format(t="36.30", c="50948")))
    check(failures, "T11 unittest's elapsed time is left out and its test count is not",
          normalise("Ran 118 tests in 288.973s") == normalise("Ran 118 tests in 279.186s")
          and normalise("Ran 118 tests in 288.973s") != normalise("Ran 117 tests in 288.973s"),
          normalise("Ran 118 tests in 288.973s"))
    command = "bash -c '. /dev/fd/3' \"$PWD/tools/run_all_checks.sh\" 3<<< \"$script\""
    # TERM, KILL, HUP and ABRT are the forms bash 5 printed for the serial --sections run in the
    # stand-in harness, with the line number since updated from 466 to 485; IO and RTMIN were
    # written by hand from bash's "I/O possible" and "Real-time signal N" descriptions, padded to
    # 27 columns as bash 5.3.9 padded them in the #1312 review. The 4-digit KILL and HUP PIDs,
    # each after two spaces, are from the suite log that row 3.88 quotes.
    notices = (
        ("TERM", f"Terminated                 {command}"),
        ("KILL", f"/var/tmp/tmpfoankz4g/tools/run_all_checks.sh: line 485: 1546593 Killed                     {command}"),
        ("HUP", f"/var/tmp/tmpr4bf6bbz/tools/run_all_checks.sh: line 485: 1547209 Hangup                     {command}"),
        ("KILL with a 4-digit PID", f"/var/tmp/tmpfoankz4g/tools/run_all_checks.sh: line 485:  7200 Killed                     {command}"),
        ("HUP with a 4-digit PID", f"/var/tmp/tmpr4bf6bbz/tools/run_all_checks.sh: line 485:  7439 Hangup                     {command}"),
        ("ABRT", f"/var/tmp/tmp75kjtsgn/tools/run_all_checks.sh: line 485: 1548285 Aborted                    (core dumped) {command}"),
        ("IO", f"/var/tmp/tmpq3x9d1aa/tools/run_all_checks.sh: line 485: 1549001 I/O possible               {command}"),
        ("RTMIN", f"/var/tmp/tmpq3x9d1bb/tools/run_all_checks.sh: line 485: 1549102 Real-time signal 3         {command}"),
    )
    for sig, notice in notices:
        check(failures, f"T11 the serial job notice for a cut copy killed by {sig} is dropped",
              normalise(f"== a ==\n{notice}\n== b ==") == "== a ==\n== b ==", normalise(notice))
        padded = re.match(r"^(?:\S.*: line [0-9]+: +[0-9]+ )?(.*?)(?:\(core dumped\) )?" + re.escape(command) + "$",
                          notice)
        check(failures, f"T11 the {sig} sample pads its description to 27 columns",
              padded is not None and len(padded.group(1)) == 27, padded and padded.group(1))
    for line in ("  ok    commit 4d110e793449: x", "  FAIL  walker failed", "Ran 118 tests",
                 "Terminated by the user", "  ok    credential scan: 315 cases",
                 f"Terminated                 {command} extra",
                 f"  FAIL  Killed {command}", f"FAIL Something {command}", f"Killed {command}",
                 "/dev/fd/3: line 552: no_such_variable_here: unbound variable"):
        check(failures, f"T11 {line!r} is compared as is", normalise(line) == line, normalise(line))
    return failures


# T17's job-control shell. It runs in a session of its own with the pseudo-terminal as its
# controlling terminal, starts the driver in a process group of its own, gives that group the
# terminal, and reports on the pipe named by its second argument: "pid N", "stopped SIG",
# "continued" and "exit N" (the negative signal number for a death by a signal). On a stop it takes
# the terminal back and waits for a line on the pipe named by its first argument: "fg" gives the
# group the terminal again and sends it SIGCONT, as an interactive shell's fg does. Once the driver
# has ended it holds the session until that pipe gives it a line or closes, so that its exit cannot
# hang up what the driver left in the foreground before the case has looked.
JOBCTL = r"""
import fcntl, os, signal, sys, termios
ctl = os.fdopen(int(sys.argv[1]), "r")
rep = int(sys.argv[2])
argv = sys.argv[3:]
def say(text):
    os.write(rep, (text + "\n").encode())
fcntl.ioctl(0, termios.TIOCSCTTY, 0)
held = (signal.SIGINT, signal.SIGQUIT, signal.SIGTSTP, signal.SIGTTIN, signal.SIGTTOU)
for sig in held:
    signal.signal(sig, signal.SIG_IGN)
pid = os.fork()
if pid == 0:
    os.setpgid(0, 0)
    os.tcsetpgrp(0, os.getpgrp())
    for sig in held:
        signal.signal(sig, signal.SIG_DFL)
    os.close(rep)
    ctl.close()
    os.execvp(argv[0], argv)
try:
    os.setpgid(pid, pid)
except OSError:
    pass
os.tcsetpgrp(0, pid)
say(f"pid {pid}")
while True:
    _, status = os.waitpid(pid, os.WUNTRACED)
    if os.WIFSTOPPED(status):
        os.tcsetpgrp(0, os.getpgrp())
        say(f"stopped {os.WSTOPSIG(status)}")
        if ctl.readline().strip() != "fg":
            sys.exit(0)
        os.tcsetpgrp(0, pid)
        os.killpg(pid, signal.SIGCONT)
        say("continued")
        continue
    say(f"exit {os.waitstatus_to_exitcode(status)}")
    break
ctl.readline()
"""


class Terminal:
    """One run of a tree's driver under a pseudo-terminal, started by JOBCTL. out is every byte the
    terminal printed so far, and reports the lines JOBCTL wrote."""

    def __init__(self, tree, args, tostop=False):
        self.out = b""
        self.reports = []
        self.tree = tree
        # Every fd is opened inside the try, so a failure at any step, from openpty() on, closes
        # each fd already opened: no Terminal exists for the caller to close.
        opened = []
        try:
            self.master, slave = pty.openpty()
            opened += [self.master, slave]
            ctl_r, self.ctl = os.pipe()
            opened += [ctl_r, self.ctl]
            self.rep, rep_w = os.pipe()
            opened += [self.rep, rep_w]
            attrs = termios.tcgetattr(slave)
            attrs[3] = (attrs[3] | termios.TOSTOP) if tostop else (attrs[3] & ~termios.TOSTOP)
            termios.tcsetattr(slave, termios.TCSANOW, attrs)
            self.tostop = bool(termios.tcgetattr(self.master)[3] & termios.TOSTOP)
            self.p = subprocess.Popen(
                [sys.executable, "-I", "-B", "-c", JOBCTL, str(ctl_r), str(rep_w), "bash",
                 str(tree.d / "tools" / "run_all_checks.sh"), *args],
                stdin=slave, stdout=slave, stderr=slave, cwd=tree.d, env=tree.env(None),
                start_new_session=True, pass_fds=(ctl_r, rep_w))
        except BaseException:
            for fd in opened:
                os.close(fd)
            raise
        # JOBCTL holds its own copies of the slave, ctl_r and rep_w.
        for fd in (slave, ctl_r, rep_w):
            os.close(fd)
        self.open = [self.master, self.rep]

    def pump(self, predicate, seconds):
        """Read the terminal and the reports until predicate() holds or seconds (scaled) pass."""
        deadline = time.monotonic() + seconds * SCALE
        while not predicate() and time.monotonic() < deadline and self.open:
            ready, _, _ = select.select(self.open, [], [], 0.05)
            for fd in ready:
                try:
                    data = os.read(fd, 65536)
                except OSError:
                    data = b""
                if not data:
                    self.open.remove(fd)
                elif fd == self.master:
                    self.out += data
                else:
                    self.reports += data.decode("ascii").splitlines()
        return predicate()

    def report(self, prefix):
        """The value of the first report starting with prefix, or None."""
        for line in self.reports:
            if line.startswith(prefix + " "):
                return line[len(prefix) + 1:]
        return None

    def ended(self):
        return self.report("exit") is not None

    def send(self, command):
        try:
            os.write(self.ctl, command.encode("ascii") + b"\n")
        except OSError:
            pass

    def observed(self):
        """What was seen of the run, for a case whose gate never started: how the driver stopped or
        ended by JOBCTL's reports, whether the section's shell recorded its PID, and each stopped
        process of the run, with whether its process group had the terminal."""
        seen = []
        stop, end = self.report("stopped"), self.report("exit")
        if stop is not None:
            seen.append(f"the driver stopped by {signal.Signals(int(stop)).name}")
        if end is not None:
            seen.append(f"the driver ended with exit {end}")
        if stop is None and end is None:
            seen.append("the driver neither stopped nor ended")
        section = alive(self.tree.d / "g.pid")
        if not (self.tree.d / "g.pid").exists():
            seen.append("the section's shell recorded no PID")
        elif not section:
            seen.append("the section's shell had ended")
        try:
            foreground = os.tcgetpgrp(self.master)
        except OSError:
            foreground = None
        held = [(pid, pgrp, name) for pid, pgrp, state, name in session_processes(self.p.pid)
                if state == "T" and pid != self.p.pid]
        for pid, pgrp, name in held:
            who = "the section's shell" if pid == section else name
            where = "the" if pgrp == foreground else "not the"
            seen.append(f"{who} (PID {pid}) was stopped in process group {pgrp}, {where} "
                        "terminal's foreground group")
        if not held and stop is None and end is None:
            seen.append("no process of the run was stopped")
        return "; ".join(seen)

    def kill_run(self):
        """SIGKILL the driver's process group once JOBCTL has reported its PID, the process group
        of every process in JOBCTL's session (which holds the driver before that report and a
        section that moved to a group of its own), and the group of each running process that a
        pid file of the tree records when that process is in JOBCTL's session; never JOBCTL's own
        group or this test's."""
        groups = {pgrp for _, pgrp, _, _ in session_processes(self.p.pid)}
        pid = self.report("pid")
        if pid:
            groups.add(int(pid))
        # A recorded process that has ended could have its PID reused by an unrelated process, so
        # its group is taken only when one read of its stat gives JOBCTL's session as its session.
        # This test has not reaped JOBCTL yet, and Linux reuses no PID that a process, even a
        # zombie, still has as its PID, group or session, so no other session can have that ID.
        for pid_file in sorted(self.tree.d.glob("*.pid")) + sorted(self.tree.d.glob("*.child")):
            recorded = alive(pid_file)
            if recorded:
                try:
                    stat = Path(f"/proc/{recorded}/stat").read_text(encoding="utf-8",
                                                                    errors="replace")
                except OSError:
                    continue
                fields = stat.rpartition(") ")[2].split()
                if len(fields) > 3 and fields[3] == str(self.p.pid):
                    groups.add(int(fields[2]))
        for group in groups - {self.p.pid, os.getpgrp()}:
            if group > 1:
                try:
                    os.killpg(group, signal.SIGKILL)
                except OSError:
                    pass

    def close(self):
        """End the run and everything it started, whether or not JOBCTL reported the driver's PID,
        so that no process group is left for the kernel to clean up, then close the pipes and the
        terminal. It takes about 5 seconds at most. Its timed waits end at a deadline 5 seconds
        after it starts; past that deadline it finishes the step it is in, which may be a pause of
        0.05 seconds or, once it has sent JOBCTL SIGKILL, a wait with no time limit for JOBCTL to
        end, then makes at most one more pass over JOBCTL's session, killing what it finds."""
        deadline = time.monotonic() + 5
        self.kill_run()
        self.send("quit")
        os.close(self.ctl)
        try:
            self.p.wait(timeout=max(deadline - time.monotonic(), 0))
        except subprocess.TimeoutExpired:
            self.p.kill()
            self.p.wait()
        # JOBCTL has ended. Whatever is still in its session, such as a child it forked and had
        # not yet moved to the driver's group, is killed until nothing is left or the 5 seconds
        # have passed.
        while True:
            left = session_processes(self.p.pid)
            for pid, _, _, _ in left:
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass
            if not left or time.monotonic() >= deadline:
                break
            time.sleep(0.05)
        for fd in (self.master, self.rep):
            os.close(fd)


def session_processes(sid):
    """(PID, process group, state, name) of each process in session sid that is not a zombie."""
    found = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        try:
            stat = Path(f"/proc/{entry}/stat").read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        name = stat[stat.find("(") + 1:stat.rfind(")")]
        fields = stat.rpartition(") ")[2].split()
        if len(fields) > 3 and fields[3] == str(sid) and fields[0] != "Z":
            found.append((int(entry), int(fields[2]), fields[0], name))
    return found


def terminal_text(text):
    """text as the terminal prints it, with a CR before each LF (the ONLCR output mode)."""
    return text.replace("\n", "\r\n").encode("ascii")


def stopped(pid_file):
    """Whether the process recorded in pid_file is stopped (state T)."""
    pid = alive(pid_file)
    if not pid:
        return False
    try:
        return Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").rpartition(") ")[2].startswith("T")
    except OSError:
        return False


# The gate of T17's section: a foreground child shell that records its PID, sleeps, writes a line
# to the terminal and then a file. A late file means it ran to its end.
TERMINAL_GATE = ("bash -c 'printf \"%s\\n\" \"$$\" > \"$STANDIN_DIR/gate.pid\"; sleep {sleep}; "
                 "echo \"gate wrote this\"; : > \"$STANDIN_DIR/gate.late\"'")
TERMINAL_WHOLE_HEAD = ("== gate parser preflight: this python3 has the pinned markdown-it-py ==\n"
                       f"{PREFLIGHT_OK}\n== g ==\n")
TERMINAL_HEAD = "Sections selected: g\n" + TERMINAL_WHOLE_HEAD
TERMINAL_TAIL = ("gate wrote this\nline from g\n\n"
                 "All selected gates passed (g); the other sections did not run.\n")


def t17_terminal(notes):
    """The serial run on a pseudo-terminal, in 7 cases. Under --sections g, of a tree with one
    section g: Ctrl-C, a TERM sent only to the driver's PID, Ctrl-Z then fg, and `stty tostop`
    with a section whose gate writes to the terminal. In a whole run: a TERM sent only to the
    driver's PID, in the same one-section tree, and a KILL and a USR1 sent only to the driver's
    PID while g's gate sleeps, in a tree of sections g and h. Without a pseudo-terminal the group
    is skipped and notes says why."""
    failures = []
    try:
        for fd in pty.openpty():
            os.close(fd)
    except OSError as exc:
        notes.append(f"  SKIP  T17, the serial run on a pseudo-terminal: no pseudo-terminal "
                     f"is available ({exc})")
        return failures

    # The time limits of a case's waits add up to at most 32 seconds, for a KILL or a USR1 to the
    # driver's PID (5 for the gate, 1 for the output, 5 for the end, 15 for what is left, 1 for late
    # output and 5 for Terminal.close), each but the last multiplied by SECURECONFIG_TEST_LOAD_SCALE.
    # A wait can run a little past its limit, which is checked between steps, and Terminal.close's
    # wait for JOBCTL after a SIGKILL has no limit.
    def run(label, sleep, act, tostop=False, args=("--sections", "g"), more=()):
        """Start the run, wait for its gate, then act(term, tree); every case ends its run. more
        holds sections after g."""
        tree = Tree(synthetic([section("g", extra=TERMINAL_GATE.format(sleep=sleep)), *more]))
        term = None
        try:
            term = Terminal(tree, args, tostop)
            if term.pump(lambda: alive(tree.d / "gate.pid"), 5):
                act(term, tree)
            else:
                failures.append(f"T17 {label}: the gate recorded no PID in {5 * SCALE:g} seconds; "
                                f"{term.observed()}; TOSTOP set {term.tostop}, reports "
                                f"{term.reports!r}, output {term.out!r}")
        finally:
            if term is not None:
                term.close()
            tree.close()

    def settled(term, want):
        """Whether the terminal printed exactly want, once it printed as many bytes, since an echo
        can reach the terminal's reader after the report it caused."""
        term.pump(lambda: len(term.out) >= len(want), 1)
        return term.out == want

    def ctrl_c(term, tree):
        os.write(term.master, b"\x03")
        term.pump(term.ended, 5)
        gone = wait_for(lambda: not tree.leftovers(), 3)
        check(failures, "T17 Ctrl-C ends the run by INT, with the gate and the section's shell gone, "
              "and the terminal shows ^C after the section's heading",
              term.reports[1:] == ["exit -2"] and gone and not (tree.d / "gate.late").exists()
              and settled(term, terminal_text(TERMINAL_HEAD) + b"^C"),
              f"reports {term.reports!r}, still running {tree.leftovers()!r}, output {term.out!r}")

    def term_to_driver(head, shape):
        """A TERM sent only to the driver's PID, judged against the output head of the run."""
        def act(term, tree):
            os.kill(int(term.report("pid")), signal.SIGTERM)
            term.pump(term.ended, 5)
            check(failures, f"T17 a TERM to the driver's PID {shape} ends it by TERM, with nothing "
                  "printed after the section's heading", term.reports[1:] == ["exit -15"]
                  and settled(term, terminal_text(head)),
                  f"reports {term.reports!r}, output {term.out!r}")
            gone = wait_for(lambda: not tree.leftovers(), 3)
            check(failures, f"T17 a TERM to the driver's PID {shape} stops the section's shell and "
                  "its gate within 3 seconds, and the gate writes nothing late (row 3.49)",
                  gone and not (tree.d / "gate.late").exists(),
                  f"still running {tree.leftovers()!r}, the gate wrote late "
                  f"{(tree.d / 'gate.late').exists()}, output {term.out!r}")
        return act

    def untrapped_to_driver(sig):
        """sig, which the driver cannot trap (KILL) or does not trap (USR1), sent only to the
        driver's PID in a whole run of sections g and h while g's gate runs."""
        def act(term, tree):
            pid = int(term.report("pid"))
            head = terminal_text(TERMINAL_WHOLE_HEAD)
            settled(term, head)
            os.kill(pid, sig)
            term.pump(term.ended, 5)
            at_exit = term.out
            gone = wait_for(lambda: not tree.leftovers() and not group_alive(pid), 15)
            term.pump(lambda: False, 1)
            check(failures, f"T17 a {sig.name} to the driver's PID in a whole run ends it by "
                  f"{sig.name}, and no section output appears after the exit: within 15 seconds the "
                  "section's shell, its gate and the rest of the driver's process group are gone, "
                  "the gate wrote nothing late and section h never started (M1 of #1377's QA)",
                  term.reports[1:] == [f"exit {-sig}"] and at_exit == head and term.out == at_exit
                  and gone and not (tree.d / "gate.late").exists() and not (tree.d / "h.pid").exists(),
                  f"reports {term.reports!r}, output at the exit {at_exit!r}, output now "
                  f"{term.out!r}, still running {tree.leftovers()!r}, group {group_alive(pid)!r}, "
                  f"the gate wrote late {(tree.d / 'gate.late').exists()}")
        return act

    def ctrl_z(term, tree):
        os.write(term.master, b"\x1a")
        term.pump(lambda: term.report("stopped") is not None or term.ended(), 5)
        all_stopped = wait_for(lambda: stopped(tree.d / "g.pid") and stopped(tree.d / "gate.pid"), 3)
        check(failures, "T17 Ctrl-Z stops the driver by TSTP, and the section's shell and its gate "
              "with it", term.reports[1:] == [f"stopped {int(signal.SIGTSTP)}"] and all_stopped,
              f"reports {term.reports!r}, output {term.out!r}")
        term.send("fg")
        term.pump(term.ended, 8)
        check(failures, "T17 after Ctrl-Z, fg resumes the run, which ends with 0 and its whole output",
              term.reports[1:] == [f"stopped {int(signal.SIGTSTP)}", "continued", "exit 0"]
              and (tree.d / "gate.late").exists()
              and settled(term, terminal_text(TERMINAL_HEAD) + b"^Z" + terminal_text(TERMINAL_TAIL)),
              f"reports {term.reports!r}, output {term.out!r}")

    def tostop(term, tree):
        term.pump(term.ended, 8)
        check(failures, "T17 under `stty tostop` the section and its gate write to the terminal, and "
              "the run ends with 0 and no stop", term.tostop and term.reports[1:] == ["exit 0"]
              and (tree.d / "gate.late").exists()
              and settled(term, terminal_text(TERMINAL_HEAD + TERMINAL_TAIL)),
              f"TOSTOP set {term.tostop}, reports {term.reports!r}, output {term.out!r}")

    run("Ctrl-C", 8, ctrl_c)
    # The gate's sleep is scaled like the waits before the TERM cases judge, so that a larger scale
    # does not give the gate the time to end on its own first.
    run("TERM to the driver's PID", 8 * SCALE, term_to_driver(TERMINAL_HEAD, "under --sections"))
    run("TERM to the driver's PID in a whole run", 8 * SCALE,
        term_to_driver(TERMINAL_WHOLE_HEAD, "in a whole run"), args=())
    # The gate sleeps for 4 seconds, scaled, so that a run the driver's death does not stop prints
    # the gate's line and section h well within the 15 seconds the case waits.
    for sig in (signal.SIGKILL, signal.SIGUSR1):
        run(f"{sig.name} to the driver's PID in a whole run", 4 * SCALE, untrapped_to_driver(sig),
            args=(), more=(section("h"),))
    run("Ctrl-Z then fg", 2, ctrl_z)
    run("stty tostop", 0.5, tostop, tostop=True)
    if not failures:
        notes.append("  ok    T17, 7 cases of the serial run on a pseudo-terminal (under --sections "
                     "Ctrl-C, a TERM to the driver's PID, Ctrl-Z then fg and stty tostop, and in a "
                     "whole run a TERM, a KILL and a USR1 to the driver's PID), each signal to the "
                     "driver's PID stopping the section's shell and its gate (row 3.49)")
    return failures


CASES = (t1_order, t2_concurrency, t3_status, t4_preflight, t5_refusals, t6_dependencies,
         t7_exclusive, t8_abort, t9_signals, t10_merged, t11_normaliser, t12_shape, t13_select_gates,
         t16_times)


def normalise(output):
    """output with each DIFFERENTIAL_NORMALISE substitution applied line by line."""
    lines = []
    for line in output.split("\n"):
        for pattern, repl in DIFFERENTIAL_NORMALISE:
            if repl is None:
                if pattern.match(line):
                    line = None
                    break
            else:
                line = pattern.sub(repl, line)
        if line is not None:
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
    def tree_state():
        """git status and the hash of every tracked and untracked file, ignoring ignored ones."""
        files = subprocess.run(["git", "ls-files", "-co", "--exclude-standard", "-z"], cwd=ROOT,
                               stdout=subprocess.PIPE, check=True).stdout.split(b"\0")
        hashed = subprocess.run(["git", "hash-object", "--stdin-paths"], cwd=ROOT, check=True,
                                input=b"\n".join(f for f in files if f), stdout=subprocess.PIPE).stdout
        return hashed

    before = tree_state()
    src, sout, st = run_real(ROOT, None)
    middle = tree_state()
    prc, pout, pt = run_real(ROOT, jobs)
    after = tree_state()
    print(f"serial {st:.0f} s exit {src}; parallel (JOBS={jobs}) {pt:.0f} s exit {prc}; load "
          f"{open('/proc/loadavg').read().split()[0]} at the end")
    if not (before == middle == after):
        print("  FAIL  the tracked and untracked files differ after a run: "
              f"before/serial {before == middle}, serial/parallel {middle == after}")
        return 1
    print("  ok    every tracked and untracked file hashes the same before, after the serial run and "
          "after the parallel run (the write audit)")
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
    notes = []
    terminal_only = "--terminal" in sys.argv
    if not terminal_only:
        for case in CASES:
            failures += case()
    failures += t17_terminal(notes)
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    if not terminal_only:
        print(f"  ok    {len(CASES)} groups of cases of the parallel mode of run_all_checks.sh (output "
              f"order and bytes equal to serial, real concurrency, exit status, preflight and "
              f"SECURECONFIG_SUITE_JOBS refusals, dependencies and cycles, exclusive sections, early "
              f"abort and signal death of a section, HUP, INT and TERM to the driver including between "
              f"a launch and the record of its PID, no temp folder after the driver's death by USR1, "
              f"an early TERM or a failed fork, merged streams, the file's shape, "
              f"SECURECONFIG_SUITE_TIMES)")
    for note in notes:
        print(note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
