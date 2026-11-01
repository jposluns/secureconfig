#!/usr/bin/env python3
"""Recorded cases for tools/check_parser_pin.py and the suite block that runs it.

The version source is injected, so no case needs the network, a second venv or any
particular markdown-it-py on this host. The suite cases run the real preflight block
from tools/run_all_checks.sh with a stub python3, as test_python_version_notice.py does
for its block.
"""
import io
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import check_parser_pin as pin  # noqa: E402

HASH = " --hash=sha256:" + "a" * 64
LOCK = f"# comment\nmarkdown-it-py==4.2.0{HASH}\nmdurl==0.1.2{HASH}\n"
INTERPRETER = "/opt/example/bin/python3"
HOST = "this is a host problem, not a code finding"
START = 'echo "== gate parser preflight: this python3 has the pinned markdown-it-py =="'
END = 'echo "== the gate parser preflight still refuses what it should =="'


def version(value):
    return lambda: value


def raises(exc):
    def source():
        raise exc
    return source


class Preflight(unittest.TestCase):
    def run_case(self, source, lock_text=LOCK, lock_bytes=None, missing=False):
        with tempfile.TemporaryDirectory() as directory:
            lock = Path(directory) / "requirements-gates.txt"
            if lock_bytes is not None:
                lock.write_bytes(lock_bytes)
            elif not missing:
                lock.write_text(lock_text, encoding="utf-8")
            return pin.preflight(lock, source, INTERPRETER)

    def assert_refusal(self, result, *fragments):
        status, line = result
        self.assertEqual(status, 2, line)
        self.assertTrue(line.startswith("  FAIL  gate parser preflight: "), line)
        self.assertNotIn("\n", line)
        self.assertIn(f"python3 at {INTERPRETER}", line)
        for fragment in fragments:
            self.assertIn(fragment, line)

    def assert_host_refusal(self, result, *fragments):
        self.assert_refusal(result, "pins 4.2.0", HOST, "put DIR/bin first on PATH",
                            "-r tools/requirements-gates.txt", *fragments)

    def test_mismatch(self):
        self.assert_host_refusal(self.run_case(version("3.0.0")), "has markdown-it-py 3.0.0")

    def test_missing_package(self):
        missing = ModuleNotFoundError("No module named 'markdown_it'", name="markdown_it")
        self.assert_host_refusal(self.run_case(raises(missing)),
                                 "has no markdown-it-py (markdown_it is not installed)")

    def test_failed_import(self):
        for exc in (ModuleNotFoundError("No module named 'mdurl'", name="mdurl"),
                    ImportError("cannot import name 'x'"), SyntaxError("broken"),
                    AttributeError("module 'markdown_it' has no attribute '__version__'")):
            with self.subTest(exc=type(exc).__name__):
                self.assert_host_refusal(self.run_case(raises(exc)),
                                         "has a failed import of markdown_it ("
                                         + type(exc).__name__)

    def test_non_string_version_is_a_failed_import(self):
        self.assert_host_refusal(self.run_case(version(None)),
                                 "a failed import of markdown_it (__version__ is None)")

    def test_unreadable_pin(self):
        for label, kwargs in (("missing", {"missing": True}),
                              ("not UTF-8", {"lock_bytes": b"\xff\n"})):
            with self.subTest(label=label):
                result = self.run_case(version("4.2.0"), **kwargs)
                self.assert_refusal(result, "has markdown-it-py 4.2.0",
                                    "the pinned version is unknown: cannot read "
                                    "tools/requirements-gates.txt", "restore it from main")
                self.assertNotIn(HOST, result[1])

    def test_unparsable_pin(self):
        for label, text, fragment in (
                ("no pin", f"mdurl==0.1.2{HASH}\n", "expected one markdown-it-py pin, found 0"),
                ("two pins", LOCK + f"markdown-it-py==4.2.0{HASH}\n",
                 "expected one markdown-it-py pin, found 2"),
                ("range, not a pin", f"markdown-it-py>=4.2.0{HASH}\n", "line 1"),
                ("no hash", "markdown-it-py==4.2.0\n", "line 1"),
                ("leading space", f" markdown-it-py==4.2.0{HASH}\n", "line 1")):
            with self.subTest(label=label):
                result = self.run_case(version("4.2.0"), lock_text=text)
                self.assert_refusal(result, "the pinned version is unknown: cannot parse",
                                    fragment)
                self.assertNotIn(HOST, result[1])

    def test_match(self):
        status, line = self.run_case(version("4.2.0"))
        self.assertEqual((status, line), (0, (
            f"  ok    gate parser preflight: python3 at {INTERPRETER} has markdown-it-py "
            "4.2.0, as tools/requirements-gates.txt pins")))

    def test_pin_is_read_from_the_lock(self):
        lock = LOCK.replace("4.2.0", "9.8.7")
        self.assertEqual(self.run_case(version("9.8.7"), lock_text=lock)[0], 0)
        self.assert_refusal(self.run_case(version("4.2.0"), lock_text=lock), "pins 9.8.7")

    def test_shipped_lock_pins_one_version(self):
        self.assertRegex(pin.pinned_version(), r"\A[0-9]+(\.[0-9]+)*\Z")


class Command(unittest.TestCase):
    def test_real_run_is_one_line_and_agrees_with_this_interpreter(self):
        result = subprocess.run([sys.executable, "-I", "-B", str(TOOLS / "check_parser_pin.py")],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout.count("\n"), 1, result.stdout)
        self.assertIn(f"python3 at {sys.executable} ", result.stdout)
        status, _ = pin.preflight()
        self.assertEqual(result.returncode, status, result.stdout)
        self.assertIn(result.returncode, (0, 2))


class SuiteBlock(unittest.TestCase):
    def run_block(self, stub):
        suite = (TOOLS / "run_all_checks.sh").read_text(encoding="utf-8")
        self.assertEqual((suite.count(START), suite.count(END)), (1, 1))
        block = suite.split(START, 1)[1].split(END, 1)[0]
        result = subprocess.run(
            ["bash", "-c", "set -uo pipefail\nfail=0\n" + stub + "\n" + block
             + '\necho "NEXT GATE RAN"\nexit "$fail"\n'],
            capture_output=True, text=True, timeout=60)
        return result.returncode, result.stdout + result.stderr

    def test_refusal_stops_the_suite_with_status_2(self):
        status, output = self.run_block(
            "python3() { printf '  FAIL  gate parser preflight: stub\\n'; return 2; }")
        self.assertEqual(status, 2, output)
        self.assertEqual(output, "  FAIL  gate parser preflight: stub\n")

    def test_crash_stops_the_suite_with_status_2(self):
        status, output = self.run_block("python3() { echo 'Traceback'; return 1; }")
        self.assertEqual(status, 2, output)
        self.assertIn("  FAIL  gate parser preflight did not complete (exit 1)", output)
        self.assertNotIn("NEXT GATE RAN", output)

    def test_exit_0_without_ok_line_stops_the_suite(self):
        status, output = self.run_block("python3() { echo 'something else'; }")
        self.assertEqual(status, 2, output)
        self.assertIn("exited 0 without its ok line", output)
        self.assertNotIn("NEXT GATE RAN", output)

    def test_match_continues_unchanged(self):
        status, output = self.run_block(
            "python3() { printf '  ok    gate parser preflight: stub\\n'; }")
        self.assertEqual((status, output),
                         (0, "  ok    gate parser preflight: stub\nNEXT GATE RAN\n"))

    def test_block_runs_the_module_in_the_house_form(self):
        status, output = self.run_block(
            "python3() { printf '  ok    gate parser preflight: %s\\n' \"$*\"; }")
        self.assertEqual(status, 0, output)
        self.assertTrue(re.search(r"preflight: -I -B tools/check_parser_pin\.py\n", output),
                        output)


def main():
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(stream=stream, verbosity=1).run(suite)
    if not result.wasSuccessful():
        print(stream.getvalue())
        print(f"  FAIL  gate parser preflight self-test: {len(result.failures)} failures, "
              f"{len(result.errors)} errors in {result.testsRun} tests")
        return 1
    print(f"  ok    {result.testsRun} recorded tests for the gate parser preflight")
    return 0


if __name__ == "__main__":
    sys.exit(main())
