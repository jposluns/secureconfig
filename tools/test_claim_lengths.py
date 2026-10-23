#!/usr/bin/env python3
"""Exercise recorded claim-length cases through the shipped gate on throwaway trees."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent

START = "<!-- version-basis:start -->"
END = "<!-- version-basis:end -->"
NOTE = "## About the AI assistant section below"


def legacy(claims):
    """A minimal legacy front-matter guide carrying only the claims the gate reads."""
    return f"---\nversion_basis: {json.dumps({'claims': claims})}\n---\n# T\n\nBody.\n"


def two_section(claims):
    """A minimal two-section guide: the EOF grammar split() accepts, nothing more."""
    payload = json.dumps({"claims": claims})
    return (f"# T\n\nBody.\n\n{START}\n{NOTE}\n\nGenerated note.\n\n"
            f"````json\n{payload}\n````\n{END}\n")


def escaped_legacy(count):
    """A legacy guide whose claim text is `count` JSON-escaped ``\\u0078`` characters."""
    text = "\\u0078" * count
    return (f'---\nversion_basis: {{"claims": {{"c": {{"text": "{text}"}}}}}}\n---\n'
            f"# T\n\nBody.\n")


def case(files, baseline="", expected=0, needle="  ok    claim lengths:", *,
         guides=None, absent=(), also=(), no_baseline=False):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "tools").mkdir()
        names = list(files) if guides is None else guides
        (root / "tools/version_basis_guides.txt").write_text(
            "".join(name + "\n" for name in names), encoding="utf-8")
        if not no_baseline:
            if isinstance(baseline, bytes):
                (root / "tools/claim_length_baseline.txt").write_bytes(baseline)
            else:
                (root / "tools/claim_length_baseline.txt").write_text(
                    baseline, encoding="utf-8")
        for name, content in files.items():
            if isinstance(content, bytes):
                (root / name).write_bytes(content)
            else:
                (root / name).write_text(content, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(TOOLS / "check_claim_lengths.py"), str(root)],
            capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        assert result.returncode == expected, (result.returncode, expected, output)
        for text in (needle, *also):
            assert text in output, (text, output)
        for text in absent:
            assert text not in output, (text, output)
        if expected == 0:
            assert "  FAIL  " not in output, output
        return 1


def main():
    count = 0
    short, long_401, long_450 = "x" * 400, "x" * 401, "x" * 450
    try:
        # Clean corpora: at the limit, under it, and in both stored layouts.
        count += case({"a.md": legacy({"c": {"text": short}, "d": {"text": "y"}})})
        count += case({"a.md": two_section({"c": {"text": short}})})
        # The 400/401 boundary: 401 is the first failing length.
        count += case({"a.md": legacy({"c": {"text": long_401}})}, expected=1,
                      needle="  FAIL  a.md: claim c: 401 characters exceeds the "
                             "400-character limit and has no baseline entry")
        count += case({"a.md": two_section({"c": {"text": long_401}})}, expected=1,
                      needle="401 characters exceeds the 400-character limit")
        # Lengths are Unicode code points: 401 two-byte characters fail as 401,
        # and 400 of them pass even though the UTF-8 text is 800 bytes.
        count += case({"a.md": legacy({"c": {"text": "é" * 401}})}, expected=1,
                      needle="a.md: claim c: 401 characters exceeds")
        count += case({"a.md": legacy({"c": {"text": "é" * 400}})})
        # JSON escaping does not change the count: 401 characters stored as
        # \u0078 escapes fail as 401, and 400 of them pass, even though the
        # stored JSON string is six bytes per character.
        count += case({"a.md": escaped_legacy(401)}, expected=1,
                      needle="a.md: claim c: 401 characters exceeds")
        count += case({"a.md": escaped_legacy(400)})
        # A baselined claim passes at exactly its recorded length.
        count += case({"a.md": legacy({"c": {"text": long_450}})}, "a.md\tc\t450\n")
        count += case({"a.md": two_section({"c": {"text": long_450}})},
                      "# seeded\n\na.md\tc\t450\n")
        # A digit-bearing claim id is within CLAIM_RE and can be baselined.
        count += case({"a.md": legacy({"c2": {"text": long_450}})}, "a.md\tc2\t450\n")
        # A claim id outside CLAIM_RE fails closed: over 400 it fails like any
        # other claim, and no baseline entry can list it, because the entry
        # grammar refuses the id.
        count += case({"a.md": legacy({"C": {"text": long_450}})}, expected=1,
                      needle="  FAIL  a.md: claim C: 450 characters exceeds the "
                             "400-character limit and has no baseline entry")
        count += case({"a.md": legacy({"C": {"text": long_450}})}, "a.md\tC\t450\n",
                      expected=1, needle="malformed entry")
        count += case({"a.md": legacy({"c\td": {"text": long_450}})},
                      "a.md\tc\td\t450\n", expected=1, needle="malformed entry")
        # A listed claim that grew past its allowance fails.
        count += case({"a.md": legacy({"c": {"text": "x" * 451}})}, "a.md\tc\t450\n",
                      expected=1,
                      needle="  FAIL  a.md: claim c: grew to 451 characters from its "
                             "baselined 450 (limit 400)")
        # Stale entries: the claim shrank under the limit (remove) or toward it (shrink).
        count += case({"a.md": legacy({"c": {"text": short}})}, "a.md\tc\t450\n",
                      expected=1,
                      needle="  FAIL  a.md: claim c: now 400 characters, at or under the "
                             "400-character limit; remove its stale baseline entry")
        count += case({"a.md": legacy({"c": {"text": "x" * 420}})}, "a.md\tc\t450\n",
                      expected=1,
                      needle="  FAIL  a.md: claim c: shrank to 420 characters from its "
                             "baselined 450; shrink the entry to 420 (limit 400)")
        # Entries must name an enrolled guide and an existing claim.
        count += case({"a.md": legacy({"c": {"text": "y"}})}, "z.md\tc\t450\n",
                      expected=1, needle="z.md: claim c: baseline entry names an "
                                         "unenrolled guide; remove it (limit 400)")
        count += case({"a.md": legacy({"c": {"text": "y"}})}, "a.md\tgone\t450\n",
                      expected=1, needle="a.md: claim gone: baseline entry names a claim "
                                         "the guide no longer has; remove it (limit 400)")
        # Malformed baselines fail closed before any comparison.
        for line in ("a.md\tc\n", "a.md\tc\t450\textra\n", "a.md\tc\tmany\n",
                     "a.md\tc\t0450\n", "a.md\tc\t-450\n", "a.md\tC\t450\n",
                     "A.md\tc\t450\n", "a.md c 450\n", "a.md\tc\t400\n",
                     "a.md\tc\t399\n"):
            count += case({"a.md": legacy({"c": {"text": long_450}})}, line,
                          expected=1, needle="malformed entry",
                          absent=("grew", "shrank", "no baseline entry"))
        # Unsorted or duplicated entries fail closed too.
        for text in ("b.md\tc\t450\na.md\tc\t450\n",
                     "a.md\td\t450\na.md\tc\t450\n",
                     "a.md\tc\t450\na.md\tc\t450\n"):
            count += case({"a.md": legacy({"c": {"text": long_450},
                                           "d": {"text": long_450}}),
                           "b.md": legacy({"c": {"text": long_450}})}, text,
                          expected=1, needle="must be sorted by guide then claim id")
        # Comments and blank lines are skipped; order is checked across them.
        count += case({"a.md": legacy({"c": {"text": long_450}})},
                      "# comment\n\na.md\tc\t450\n")
        count += case({"a.md": legacy({"c": {"text": long_450}}),
                       "b.md": legacy({"c": {"text": long_450}})},
                      "b.md\tc\t450\n# comment\n\na.md\tc\t450\n",
                      expected=1, needle="must be sorted by guide then claim id")
        # Baseline lines are split on LF alone, and any other line-separator or
        # control character in a line is refused, so a '#' comment cannot hide
        # a live entry behind a character that str.splitlines() breaks on.
        for ch in ("\u2028", "\u2029", "\u0085", "\x0c", "\r"):
            count += case({"a.md": legacy({"c": {"text": long_450}})},
                          f"# hidden{ch}a.md\tc\t450\n", expected=1,
                          needle="control or line-separator character")
        # Missing inputs and unreadable metadata fail closed, never pass.
        count += case({"a.md": legacy({"c": {"text": "y"}})}, guides=["a.md", "b.md"],
                      expected=2, needle="  FAIL  cannot check claim lengths:")
        count += case({"a.md": legacy({"c": {"text": "y"}})}, expected=2, no_baseline=True,
                      needle="  FAIL  cannot check claim lengths:")
        count += case({}, guides=[], expected=2,
                      needle="tools/version_basis_guides.txt is empty")
        count += case({"a.md": legacy({"c": {"text": "y"}})}, guides=["a.md", "a.md"],
                      expected=2, needle="empty, duplicated or malformed")
        count += case({"A.md": legacy({"c": {"text": "y"}})}, expected=2,
                      needle="empty, duplicated or malformed")
        count += case({"a.md": "# T\n\nNo metadata.\n"}, expected=2,
                      needle="a.md: missing version_basis claims")
        count += case({"a.md": "---\nversion_basis: not json\n---\n# T\n"}, expected=2,
                      needle="a.md: unreadable version_basis metadata")
        count += case({"a.md": legacy({"c": {"text": 7}})}, expected=2,
                      needle="a.md: claim c has no text string")
        # Non-UTF-8 inputs fail closed: a baseline or a guide the gate cannot
        # decode is an error, not a pass. The guide's bad byte sits inside
        # otherwise valid JSON, so only the strict decode can refuse it.
        count += case({"a.md": legacy({"c": {"text": "y"}})}, b"\xff\xfe\n",
                      expected=2, needle="  FAIL  cannot check claim lengths:")
        count += case({"a.md": b'---\nversion_basis: {"claims": {"c": {"text": "\xff"}}}\n'
                               b"---\n# T\n\nBody.\n"}, expected=2,
                      needle="  FAIL  cannot check claim lengths: 'utf-8' codec can't decode")
        # A baseline saved with CRLF endings is refused line by line, not
        # silently read; .gitattributes pins the baseline to LF in checkouts.
        count += case({"a.md": legacy({"c": {"text": long_450}})},
                      b"# seeded\r\na.md\tc\t450\r\n", expected=1,
                      needle="claim-length baseline line 1: control or line-separator "
                             "character '\\r' is not allowed",
                      also=("claim-length baseline line 2: control or line-separator "
                            "character '\\r' is not allowed",),
                      absent=("no baseline entry",))
        # Findings list every violating claim, one line each.
        count += case({"a.md": legacy({"c": {"text": long_401},
                                       "d": {"text": "x" * 500}})},
                      expected=1, needle="a.md: claim c: 401 characters exceeds",
                      also=("a.md: claim d: 500 characters exceeds",))
        # What the gate does NOT catch, recorded so this file cannot quietly
        # start claiming that coverage: the gate reads the tree only, so a
        # change that raises an entry alongside its grown claim, or adds an
        # entry alongside a new over-length claim, passes and is refused only
        # in review. "The baseline only shrinks" is upheld by review, not here.
        count += case({"a.md": legacy({"c": {"text": "x" * 460}})}, "a.md\tc\t460\n")
        count += case({"a.md": legacy({"c": {"text": long_450},
                                       "d": {"text": "x" * 500}})},
                      "a.md\tc\t450\na.md\td\t500\n")
    except (AssertionError, OSError, subprocess.SubprocessError) as exc:
        print(f"  FAIL  claim-length gate self-test: {exc}")
        return 1
    print(f"  ok    {count} recorded cases for the claim-length gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
