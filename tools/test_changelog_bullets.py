#!/usr/bin/env python3
"""Exercise recorded CHANGELOG bullet cases through the shipped gate on throwaway trees.

Apart from the fail-closed cases and the legacy-list cases, each failing fixture has a
passing twin that differs only in the defect, so a case fails when its rule is removed
rather than passing for another reason. Fixture cases call the gate's main() with
legacy_max set to the fixture list's length; the LEGACY_MAX cases at the end run the
gate unchanged on a copy of the real CHANGELOG.md. The last cases record limits the gate
does NOT model, so this file cannot quietly start claiming them.
"""
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
GATE = TOOLS / "check_changelog_bullets.py"
OK = "  ok    CHANGELOG.md: "
LEGACY = "tools/changelog_bullets_legacy.txt"
VERSION_FILES = "`VERSION`, `plugin/plugin.json` and `plugin/skills/secureconfig/SKILL.md`"


def words(n, last="."):
    """A sentence of n words: a capital first word, then n - 1 short words."""
    return " ".join(["Word"] + ["w"] * (n - 1)) + last


def bullet(*sentences, ref=" (#1)"):
    return "- " + " ".join(sentences) + ref


def log(*bullets, date="2026-11-28"):
    """A changelog whose preamble has 4 long sentences, then one dated section."""
    return ("# Changelog\n\n" + " ".join([words(30)] * 4) + "\n\n## " + date + "\n\n"
            + "".join(b + "\n" for b in bullets))


def entry(text, date="2026-11-28", ref="#1"):
    return f"{hashlib.sha256(text[2:].encode('utf-8')).hexdigest()} {date} {ref}"


def listed(legacy):
    """The number of distinct hashes in a fixture list."""
    if isinstance(legacy, bytes):
        return 0
    return len({line.split(" ")[0] for line in legacy.split("\n")
                if re.match(r"[0-9a-f]{64} ", line)})


def run(root, *extra, legacy_max=None):
    """Run the gate on root: unchanged, or through main() with legacy_max."""
    if legacy_max is None:
        command = [sys.executable, "-I", "-B", str(GATE), str(root), *extra]
    else:
        code = (f"import sys; sys.path.insert(0, {str(TOOLS)!r}); "
                "import check_changelog_bullets as gate; "
                f"sys.exit(gate.main({[str(root), *extra]!r}, legacy_max={legacy_max}))")
        command = [sys.executable, "-I", "-B", "-c", code]
    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    return result.returncode, result.stdout + result.stderr


def case(changelog, expected=0, needle=OK, *, legacy="", legacy_max=None, also=(), absent=(),
         missing=()):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "tools").mkdir()
        files = {"CHANGELOG.md": changelog, LEGACY: legacy}
        for name, content in files.items():
            if name not in missing:
                data = content if isinstance(content, bytes) else content.encode("utf-8")
                (root / name).write_bytes(data)
        code, output = run(root, legacy_max=listed(legacy) if legacy_max is None else legacy_max)
        assert code == expected, (code, expected, output)
        for text in (needle, *also):
            assert text in output, (text, output)
        for text in absent:
            assert text not in output, (text, output)
        if expected == 0:
            assert "  FAIL  " not in output, output
        return 1


def regenerated(extra_bullet):
    """Copy the real CHANGELOG.md, add a bullet if given, regenerate the list, run the gate."""
    text = (TOOLS.parent / "CHANGELOG.md").read_text(encoding="utf-8")
    if extra_bullet:
        heading = re.search(r"^## [0-9]{4}-[0-9]{2}-[0-9]{2}\n\n", text, re.M)
        text = text[:heading.end()] + extra_bullet + "\n" + text[heading.end():]
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "tools").mkdir()
        (root / "CHANGELOG.md").write_text(text, encoding="utf-8", newline="")
        code, output = run(root, "--list-legacy")
        assert code == 0, output
        (root / LEGACY).write_text(output, encoding="utf-8", newline="")
        return run(root)


def main():
    count = 0
    three = bullet(words(25), words(25), words(25))
    four = bullet(words(25), words(25), words(25), words(1))
    try:
        # The limits: 3 sentences of 25 words pass; a 4th sentence or a 26th word fails.
        # The preamble's 4 sentences of 30 words are never counted.
        count += case(log(three), needle=OK + "1 bullets, 1 within 3 sentences of 25 words, "
                                          "0 listed in " + LEGACY)
        count += case(log(four), expected=1, needle="  FAIL  CHANGELOG.md:7: bullet (2026-11-28 "
                      "#1), not in " + LEGACY + ", has 4 sentences; at most 3")
        count += case(log(bullet(words(25), words(26), words(25))), expected=1,
                      needle="CHANGELOG.md:7: bullet (2026-11-28 #1), not in " + LEGACY
                             + ", sentence 2 has 26 words; at most 25: 'Word w w",
                      absent=("sentences; at most",))
        # A trailing reference is neither a sentence nor a word; a mid-text #N is a word.
        count += case(log(bullet(words(25), words(25), words(25), ref=" (#1, #2).")))
        count += case(log(bullet(words(24, "") + " (#5) end.")), expected=1,
                      needle="sentence 1 has 26 words")
        count += case(log(bullet(words(23, "") + " (#5) end.")))
        # A code span is one word; a lone "-" is none.
        count += case(log(bullet(words(24, "") + " `a b c`.")))
        count += case(log(bullet(words(24, "") + " a b c.")), expected=1,
                      needle="sentence 1 has 27 words")
        count += case(log(bullet(words(12, "") + " - " + words(13))))
        # Link text is counted and its URL is not.
        link = " [two words](https://example.com/a.b.c)."
        count += case(log(bullet(words(23, "") + link)))
        count += case(log(bullet(words(24, "") + link)), expected=1,
                      needle="sentence 1 has 26 words")
        # D-1096 vote: content over 60 characters, or with more than 8 internal spaces, is
        # counted by its words; edge spaces are not internal.
        sixty = " ".join(["abcdefghi"] * 6) + "j"
        count += case(log(bullet(words(20, "") + f" `{sixty}`.")))
        count += case(log(bullet(words(20, "") + f" `{sixty}k`.")), expected=1,
                      needle="sentence 1 has 26 words")
        count += case(log(bullet(words(20, "") + " `a b c d e f g h i`.")))
        count += case(log(bullet(words(20, "") + " ` a b c d e f g h i `.")))
        count += case(log(bullet(words(20, "") + " `a b c d e f g h i j`.")), expected=1,
                      needle="sentence 1 has 30 words")
        # An unclosed backtick is plain text, and the closed twin is one word.
        count += case(log(bullet(words(20, "") + " `a b c d e f.")), expected=1,
                      needle="sentence 1 has 26 words")
        count += case(log(bullet(words(20, "") + " `a b c d e f`.")))
        # Not boundaries: after e.g., i.e., vs. or cf., in a code span, in a quotation, at a
        # semicolon or colon, at a dot inside a version number; etc. ends a sentence only
        # before a sentence-opening character. Each twin splits.
        for inner, split in (("e.g. Word", "eg. Word"), ("i.e. Word", "ie. Word"),
                             ("vs. Word", "vz. Word"), ("cf. Word", "cz. Word"),
                             ("`a. B`", "a. B"), ('"Stop. Now."', "Stop. Now."),
                             ("a; Word", "a. Word"), ("a: Word", "a. Word"),
                             ("v1.864.1 Word", "v1. 864.1 Word"), ("etc. next", "etc. Next")):
            count += case(log(bullet(words(3), words(3), "Word " + inner + " end.")))
            count += case(log(bullet(words(3), words(3), "Word " + split + " end.")),
                          expected=1, needle="has 4 sentences")
        # Nested items and continuation lines join their bullet.
        count += case(log("- One.\n  - Two.\n  continued here.\n  - Three."))
        count += case(log("- One.\n  - Two.\n  - Three.\n  - Four."), expected=1,
                      needle="CHANGELOG.md:7: bullet (2026-11-28 -), not in")
        # Fail closed on text outside a "- " bullet: a paragraph, a "*" item or an indented
        # item after a blank line, or text right under a heading. Twins are "- " bullets.
        for stray in (words(40), "* " + words(40), "  - " + words(40)):
            count += case(log(three, "", stray), expected=1,
                          needle="  FAIL  CHANGELOG.md:9: text under a dated heading outside")
        count += case(log(three, "", bullet(words(20), ref=" (#2)")))
        count += case(log(three).replace("## 2026-11-28\n\n", "## 2026-11-28\nNote.\n"),
                      expected=1, needle="CHANGELOG.md:6: text under a dated heading outside")
        # Fence lines fail, inside a bullet or not; the twin uses a code span.
        count += case(log(three, "```", "code", "```"), expected=1,
                      needle="CHANGELOG.md:8: fence line under a dated heading",
                      also=("CHANGELOG.md:10: fence line",))
        count += case(log("- One.\n  ~~~\n  x\n  ~~~"), expected=1,
                      needle="CHANGELOG.md:8: fence line under a dated heading")
        count += case(log("- One.\n  `x`"))
        # Duplicate bullet texts fail, listed or not; the twin differs in its reference.
        count += case(log(three, three), expected=1,
                      needle="CHANGELOG.md:8: bullet repeats the text of the bullet at "
                             "CHANGELOG.md:7")
        count += case(log(three, three.replace("(#1)", "(#2)")))
        count += case(log(four, four), legacy=entry(four) + "\n", expected=1,
                      needle="CHANGELOG.md:8: bullet repeats the text")
        # A new fixed-form version sentence fails, even in a compliant bullet; a listed
        # legacy bullet keeps its old one until its batch.
        for form in ("go to 1.0.5.", "stay at main's value, 1.0.7, because main is higher."):
            count += case(log(bullet(words(3), VERSION_FILES + " " + form)), expected=1,
                          needle="CHANGELOG.md:7: bullet (2026-11-28 #1), not in " + LEGACY
                                 + ", restates the version")
        count += case(log(bullet(words(3), VERSION_FILES + " are unchanged.")))
        old = bullet(words(25), words(25), words(25), VERSION_FILES + " go to 1.0.5.")
        count += case(log(old), legacy=entry(old) + "\n")
        # Legacy list: a listed non-compliant bullet passes, and nothing else does.
        count += case(log(four), legacy=entry(four) + "\n",
                      needle=OK + "1 bullets, 0 within 3 sentences of 25 words, 1 listed")
        count += case(log(three), legacy=entry(three) + "\n", expected=1,
                      needle=f"  FAIL  {LEGACY}:1: {entry(three)[:12]} (CHANGELOG.md:7) now "
                             "complies; delete the line")
        edited = four.replace("Word", "Ward", 1)
        count += case(log(edited), legacy=entry(four) + "\n", expected=1,
                      needle=f"{LEGACY}:1: {entry(four)[:12]} matches no bullet",
                      also=("has 4 sentences; at most 3",))
        count += case(log(four), legacy=entry(four) + "\n" + entry(four) + "\n", expected=1,
                      needle=f"{LEGACY}:2: {entry(four)[:12]} repeats line 1")
        other = bullet(words(30), ref=" (#2)")
        lines = sorted([entry(four), entry(other, ref="#2")], reverse=True)
        count += case(log(four, other), legacy="\n".join(lines) + "\n", expected=1,
                      needle="is out of order; sort by hash")
        count += case(log(four, other), legacy="\n".join(sorted(lines)) + "\n",
                      needle="2 listed in")
        count += case(log(four), legacy=entry(four, ref="#9") + "\n", expected=1,
                      needle=f"{LEGACY}:1: says 2026-11-28 #9, but its bullet at "
                             "CHANGELOG.md:7 is 2026-11-28 #1")
        count += case(log(four), legacy="# comment\n" + entry(four)[:-1] + "x\n", expected=1,
                      needle=f"{LEGACY}:2: malformed line")
        # LEGACY_MAX: the list must hold exactly that many entries.
        count += case(log(four), legacy=entry(four) + "\n", legacy_max=0, expected=1,
                      needle=f"  FAIL  {LEGACY}: 1 entries, more than LEGACY_MAX (0)")
        count += case(log(four), legacy=entry(four) + "\n", legacy_max=2, expected=1,
                      needle=f"  FAIL  {LEGACY}: 1 entries, but LEGACY_MAX is 2; lower")
        # --list-legacy prints exactly the non-compliant bullets, sorted, after a header.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "CHANGELOG.md").write_text(log(three, other, four), encoding="utf-8")
            code, output = run(root, "--list-legacy")
            body = [line for line in output.split("\n") if line and not line.startswith("#")]
            assert code == 0 and body == sorted([entry(four), entry(other, ref="#2")]), output
            count += 1
        # Fail closed: CR, no bullet, a missing or non-UTF-8 file.
        count += case(log(three).replace("\n", "\r\n"), expected=1,
                      needle="CHANGELOG.md:1: this line holds a carriage return")
        count += case(log(three), legacy="\r\n", expected=1,
                      needle=f"{LEGACY}: the list holds a carriage return")
        count += case(log(), expected=1, needle="no bullet under a dated")
        count += case(log(three), expected=2, needle="  FAIL  cannot check CHANGELOG.md:",
                      missing=("CHANGELOG.md",))
        count += case(log(three), expected=2, needle=f"  FAIL  cannot check {LEGACY}:",
                      missing=(LEGACY,))
        count += case(log(three).encode("utf-8") + b"\xff\n", expected=2,
                      needle="  FAIL  cannot check CHANGELOG.md: 'utf-8' codec can't decode")
        count += case(log(three), legacy=b"\xff\n", expected=2,
                      needle=f"  FAIL  cannot check {LEGACY}: 'utf-8' codec can't decode")
        # Known limit: a boundary inside parentheses still splits.
        count += case(log(bullet(words(3), words(3), "Word (see a. Word) end.")), expected=1,
                      needle="has 4 sentences")
        # The shipped gate, unchanged, on the real CHANGELOG.md: regenerating the list
        # passes as it stands, and fails once it would exempt a new non-compliant bullet.
        code, output = regenerated("")
        assert code == 0 and "  FAIL  " not in output and " listed in " in output, output
        count += 1
        code, output = regenerated(bullet(words(30), ref=" (#99999)"))
        assert code == 1 and "entries, more than LEGACY_MAX" in output, output
        count += 1
    except (AssertionError, OSError, subprocess.SubprocessError) as exc:
        print(f"  FAIL  changelog-bullets gate self-test: {exc}")
        return 1
    print(f"  ok    {count} recorded cases for the changelog-bullets gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
