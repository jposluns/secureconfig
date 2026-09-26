#!/usr/bin/env python3
"""Development-only fuzzer regressions; requires en_US.utf8, Bash and GNU grep."""
import contextlib
import io
import itertools
import os
import shlex
import subprocess
import sys
import unittest
from unittest.mock import patch

import fuzz_bracket_ranges as fuzz


class FuzzerTests(unittest.TestCase):
    def cli(self, *args):
        with patch.object(sys, "argv", ["fuzz", *args]), contextlib.redirect_stdout(io.StringIO()):
            return fuzz.main()

    def test_alphabet(self):
        self.assertEqual(set(fuzz.ALPHABET), set("'\"\\]^!az-x$ \n[:=."))
        self.assertEqual(len(fuzz.ALPHABET), 17)

    def test_both_locale_directions(self):
        for engine in ("glob", "grep", "regex"):
            result = fuzz.check_batch(["a-z", "^a-z", "!a-z"], "en_US.utf8", [engine])[engine]
            self.assertEqual((result["parsed"], result["live"], result["flagged"],
                              result["missed"]), (3, 3, 3, []))

    def test_arithmetic_errors_are_not_match_results(self):
        self.assertEqual(fuzz.glob_batch(["$[^]", "$[!]", "a-z"], "en_US.utf8"),
                         (1, {2}))

    def test_multiline_candidates_use_real_fences(self):
        seen = []
        scan = fuzz.scan_path

        def observe(path):
            seen.append(path.read_text())
            return scan(path)

        with patch.object(fuzz, "scan_path", observe):
            result = fuzz.check_batch(['!"x]y"\\\na-z'], "en_US.utf8", ["glob"])["glob"]
        self.assertEqual((result["live"], result["flagged"], result["missed"]), (1, 1, []))
        self.assertEqual(seen, ['```bash\ncase "$1" in *[!"x]y"\\\na-z]*) :;; esac\n```\n'])

    def test_literal_regex_source_is_shell_quoted(self):
        seen = []
        scan = fuzz.scan_path

        def observe(path):
            seen.append(path.read_text())
            return scan(path)

        pattern = "[]'-z\n]"
        with patch.object(fuzz, "scan_path", observe):
            result = fuzz.check_batch([pattern[1:-1]], "en_US.utf8", ["regex"])["regex"]
        self.assertEqual((result["live"], result["flagged"], result["missed"]), (1, 1, []))
        self.assertEqual(seen, ["```bash\nre=" + shlex.quote(pattern) + "\n```\n"])

    def test_grep_newline_fragments_keep_candidate_identity(self):
        words = ["a-z", "^a-z", "]\n[a-z", "a\n-z", "az", "[:x:]", ":x:", ":x:", "a-z]\n[a-z"]
        valid, live = set(), set()
        for i, word in enumerate(words):
            codes = [subprocess.run(["grep", "-qE", "[" + word + "]"], input="é\n",
                                    text=True, capture_output=True,
                                    env=dict(os.environ, LC_ALL=locale)).returncode
                     for locale in ("C", "en_US.utf8")]
            if all(code < 2 for code in codes):
                valid.add(i)
                if codes[0] != codes[1]:
                    live.add(i)
        self.assertEqual(fuzz.grep_batch(words, "en_US.utf8"), (len(valid), live))

    def test_canary_requires_both_detection_counts(self):
        original = fuzz.check_batch
        for field, value in (("flagged", 0), ("missed", ["[a-z]"])):
            def corrupt(words, locale, engines):
                results = original(words, locale, engines)
                if words == ["a-z", "!a-z"]:
                    results["glob"][field] = value
                return results

            with patch.object(fuzz, "check_batch", corrupt):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exc:
                    self.cli("--max-length", "0", "--allow-empty", "--engines", "glob")
                self.assertEqual(exc.exception.code, 2)

    def test_empty_runs_fail_unless_explicit(self):
        for engine in ("glob", "grep", "regex"):
            for suffix in (["--max-length", "0"],
                           ["--max-length", "1", "--start-index", "17"]):
                args = [*suffix, "--engines", engine, "--jobs", "1"]
                self.assertEqual(self.cli(*args), 1)
                self.assertEqual(self.cli(*args, "--allow-empty"), 0)

    def test_each_engine_must_have_live_candidates(self):
        original = fuzz.check_batch

        def empty_regex(words, locale, engines):
            results = original(words, locale, engines)
            if words == [""]:
                results["glob"].update(parsed=1, live=1, flagged=1)
                results["regex"]["live"] = 0
            return results

        # Real CLI zero-length evidence covers all three engines independently above.
        # This controlled result also pins "any engine", even if another has live evidence.
        with patch.object(fuzz, "check_batch", empty_regex):
            self.assertEqual(self.cli("--max-length", "0", "--engines", "glob", "regex"), 1)

    def test_empty_gate_fails_canary_even_with_allow_empty(self):
        for engine in ("glob", "grep", "regex"):
            with patch.object(fuzz, "scan_path", return_value=([], 1, 0)):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exc:
                    self.cli("--max-length", "0", "--allow-empty", "--engines", engine)
                self.assertEqual(exc.exception.code, 2)

    def test_unusable_locale_fails_canary(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as exc:
            self.cli("--max-length", "0", "--allow-empty", "--locale", "C.utf8")
        self.assertEqual(exc.exception.code, 2)

    def test_batch_and_resume_enumeration(self):
        expected = ["".join(word) for length in range(3)
                    for word in itertools.product(fuzz.ALPHABET, repeat=length)]
        for size in (1, 7, 128, 4096):
            for skip in (0, 1, 17, 18, len(expected) - 1):
                self.assertEqual([word for batch in fuzz.batches(2, size, skip)
                                  for word in batch], expected[skip:])


if __name__ == "__main__":
    unittest.main()
