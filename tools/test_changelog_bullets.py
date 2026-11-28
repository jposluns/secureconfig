#!/usr/bin/env python3
"""Exercise recorded CHANGELOG bullet cases through the shipped gate on throwaway trees.

Apart from the fail-closed cases and the legacy-list cases, each failing fixture has a
passing twin that differs only in the defect, so a case fails when its rule is removed
rather than passing for another reason. Fixture cases call the gate's main() with
legacy_max set to the fixture list's length; the LEGACY_MAX cases at the end run the
gate unchanged on a copy of the real CHANGELOG.md. The base-copy cases build throwaway
git repositories with local git only. Every run drops BASE_SHA, GITHUB_ACTIONS and the
GIT_ variables it inherits, so a CI run sees the same fixtures as a local one. The last
cases record limits the gate does NOT model, so this file cannot quietly start claiming
them.
"""
import hashlib
import os
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
GIT_ENV = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.com",
           "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.com"}


def words(n, last="."):
    """A sentence of n words: a capital first word, then n - 1 short words."""
    return " ".join(["Word"] + ["w"] * (n - 1)) + last


def bullet(*sentences, ref=" (#1)"):
    return "- " + " ".join(sentences) + ref


def log(*bullets, date="2026-11-27"):
    """A changelog whose preamble has 4 long sentences, then one dated section."""
    return ("# Changelog\n\n" + " ".join([words(30)] * 4) + "\n\n## " + date + "\n\n"
            + "".join(b + "\n" for b in bullets))


def entry(text, date="2026-11-27", ref="#1"):
    return f"{hashlib.sha256(text[2:].encode('utf-8')).hexdigest()} {date} {ref}"


def listed(legacy):
    """The number of distinct hashes in a fixture list."""
    if isinstance(legacy, bytes):
        return 0
    return len({line.split(" ")[0] for line in legacy.split("\n")
                if re.match(r"[0-9a-f]{64} ", line)})


def clean_env(extra=None):
    """The inherited environment without BASE_SHA, GITHUB_ACTIONS or GIT_*, plus extra."""
    env = {k: v for k, v in os.environ.items()
           if k not in ("BASE_SHA", "GITHUB_ACTIONS") and not k.startswith("GIT_")}
    env.update(extra or {})
    return env


def run(root, *extra, legacy_max=None, env=None):
    """Run the gate on root: unchanged, or through main() with legacy_max."""
    if legacy_max is None:
        command = [sys.executable, "-I", "-B", str(GATE), str(root), *extra]
    else:
        code = (f"import sys; sys.path.insert(0, {str(TOOLS)!r}); "
                "import check_changelog_bullets as gate; "
                f"sys.exit(gate.main({[str(root), *extra]!r}, legacy_max={legacy_max}))")
        command = [sys.executable, "-I", "-B", "-c", code]
    result = subprocess.run(command, capture_output=True, text=True, timeout=120,
                            env=clean_env(env))
    return result.returncode, result.stdout + result.stderr


def verify(code, output, expected, needle, also, absent):
    assert code == expected, (code, expected, output)
    for text in (needle, *also):
        assert text in output, (text, output)
    for text in absent:
        assert text not in output, (text, output)
    if expected == 0:
        assert "  FAIL  " not in output, output
    return 1


def write(root, files):
    (root / "tools").mkdir(exist_ok=True)
    for name, content in files.items():
        data = content if isinstance(content, bytes) else content.encode("utf-8")
        (root / name).write_bytes(data)


def case(changelog, expected=0, needle=OK, *, legacy="", legacy_max=None, also=(), absent=(),
         missing=()):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        write(root, {name: content for name, content in
                     {"CHANGELOG.md": changelog, LEGACY: legacy}.items() if name not in missing})
        code, output = run(root, legacy_max=listed(legacy) if legacy_max is None else legacy_max)
        return verify(code, output, expected, needle, also, absent)


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                            timeout=60, env=clean_env(GIT_ENV))
    assert result.returncode == 0, (args, result.stderr)
    return result.stdout.strip()


def git_case(base, work, expected=0, needle=OK, *, origin=True, env=None, also=(), absent=()):
    """Commit base (a file map) as the base, point origin/main at it unless origin is false,
    write work over it uncommitted, and run the gate with env ({"BASE_SHA": None} sets
    BASE_SHA to the base commit)."""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        git(root, "init", "-q")
        write(root, base)
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "base")
        commit = git(root, "rev-parse", "HEAD")
        if origin:
            git(root, "update-ref", "refs/remotes/origin/main", commit)
        for name in base:
            if name not in work:
                (root / name).unlink()
        write(root, work)
        extra = dict(GIT_ENV)
        for key, value in (env or {}).items():
            extra[key] = commit if value is None else value
        legacy = work.get(LEGACY, "")
        code, output = run(root, legacy_max=listed(legacy), env=extra)
        return verify(code, output, expected, needle, also, absent)


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
        count += case(log(four), expected=1, needle="  FAIL  CHANGELOG.md:7: bullet (2026-11-27 "
                      "#1), not in " + LEGACY + ", has 4 sentences; at most 3")
        count += case(log(bullet(words(25), words(26), words(25))), expected=1,
                      needle="CHANGELOG.md:7: bullet (2026-11-27 #1), not in " + LEGACY
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
        # D-1096 vote: content over 60 characters, or with more than 8 spaces, is counted by
        # its words. Both tests strip every leading and trailing space first.
        sixty = " ".join(["abcdefghi"] * 6) + "j"
        count += case(log(bullet(words(20, "") + f" `{sixty}`.")))
        count += case(log(bullet(words(20, "") + f" `{sixty}k`.")), expected=1,
                      needle="sentence 1 has 26 words")
        count += case(log(bullet(words(20, "") + f" `  {sixty}  `.")))
        count += case(log(bullet(words(20, "") + f" `  {sixty}k  `.")), expected=1,
                      needle="sentence 1 has 26 words")
        count += case(log(bullet(words(20, "") + " `a b c d e f g h i`.")))
        count += case(log(bullet(words(20, "") + " ` a b c d e f g h i `.")))
        count += case(log(bullet(words(20, "") + " `a b c d e f g h i j`.")), expected=1,
                      needle="sentence 1 has 30 words")
        # An unclosed backtick is plain text, and the closed twin is one word.
        count += case(log(bullet(words(20, "") + " `a b c d e f.")), expected=1,
                      needle="sentence 1 has 26 words")
        count += case(log(bullet(words(20, "") + " `a b c d e f`.")))
        # Zero-width and other Cf characters separate words, and an unlisted bullet holding
        # one fails; the twin drops the character. A listed bullet keeps it until its batch.
        for blank in ("\u200b", "\u2060", "\ufeff", "\u00ad"):
            count += case(log(bullet(words(24, "") + f" a{blank}b.")), expected=1,
                          needle="sentence 1 has 26 words",
                          also=(f"holds U+{ord(blank):04X}, an invisible format character",))
        count += case(log(bullet(words(24, "") + " ab.")))
        glued = bullet(words(25), words(25), words(25), "A\u200bb.")
        count += case(log(glued), legacy=entry(glued) + "\n", absent=("U+200B",))
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
                      needle="CHANGELOG.md:7: bullet (2026-11-27 -), not in")
        # Fail closed on text outside a "- " bullet: a paragraph, a "*" item or an indented
        # item after a blank line, or text right under a heading. Twins are "- " bullets.
        for stray in (words(40), "* " + words(40), "  - " + words(40)):
            count += case(log(three, "", stray), expected=1,
                          needle="  FAIL  CHANGELOG.md:9: text under a dated heading outside")
        count += case(log(three, "", bullet(words(20), ref=" (#2)")))
        count += case(log(three).replace("## 2026-11-27\n\n", "## 2026-11-27\nNote.\n"),
                      expected=1, needle="CHANGELOG.md:6: text under a dated heading outside")
        # Fence lines fail, inside a bullet or not, and on a bullet's own first line or a
        # nested item's; the twins use a code span.
        count += case(log(three, "```", "code", "```"), expected=1,
                      needle="CHANGELOG.md:8: fence line under a dated heading",
                      also=("CHANGELOG.md:10: fence line",))
        count += case(log("- One.\n  ~~~\n  x\n  ~~~"), expected=1,
                      needle="CHANGELOG.md:8: fence line under a dated heading")
        count += case(log("- One.\n  `x`"))
        for opener in ("- ```", "- ~~~python", "-  ```", "  - ```"):
            count += case(log(three, opener, "code"), expected=1,
                          needle="CHANGELOG.md:8: fence line under a dated heading")
        count += case(log(three, "- `x`"))
        # Duplicate bullet texts fail, listed or not; the twin differs in its reference.
        count += case(log(three, three), expected=1,
                      needle="CHANGELOG.md:8: bullet repeats the text of the bullet at "
                             "CHANGELOG.md:7")
        count += case(log(three, three.replace("(#1)", "(#2)")))
        count += case(log(four, four), legacy=entry(four) + "\n", expected=1,
                      needle="CHANGELOG.md:8: bullet repeats the text")
        # A new version sentence fails, in each recorded form, even in a compliant bullet;
        # a listed legacy bullet keeps its old one until its batch. The twins name the files
        # without assigning a version.
        for form in (VERSION_FILES + " go to 1.0.5.",
                     VERSION_FILES + " stay at main's value, 1.0.7, because main is higher.",
                     VERSION_FILES + " go to the pull request's version.",
                     VERSION_FILES.replace(" and", ", and") + " go to 1.0.5.",
                     "`VERSION`, `plugin/plugin.json` and `SKILL.md` go to 1.0.1328.",
                     "`VERSION`, `plugin.json` and `SKILL.md` are 1.0.1319.",
                     "`VERSION`, `plugin/plugin.json` and the plugin's `SKILL.md` move to "
                     "`1.0.1289`.",
                     "`VERSION`, `plugin/plugin.json` and the plugin SKILL.md move to 1.0.1294.",
                     "`VERSION`, `plugin/plugin.json` and the plugin's `SKILL.md` carry the "
                     "version bump.",
                     "`VERSION` and `plugin/plugin.json` are bumped.",
                     "`VERSION` and `plugin/plugin.json` are updated.",
                     "`VERSION` and `plugin/plugin.json` stay at main's value.",
                     "`VERSION` and `plugin/plugin.json` move to this pull request's number.",
                     "`VERSION` and `plugin/plugin.json`  stays  at 1.0.9."):
            count += case(log(bullet(words(3), form)), expected=1,
                          needle="CHANGELOG.md:7: bullet (2026-11-27 #1), not in " + LEGACY
                                 + ", restates the version")
        for form in (VERSION_FILES + " are unchanged.",
                     "A gate compares `VERSION` to `plugin/plugin.json`'s version.",
                     "`VERSION` and `plugin/plugin.json` are read by the gate."):
            count += case(log(bullet(words(3), form)))
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
                      needle=f"{LEGACY}:1: says 2026-11-27 #9, but its bullet at "
                             "CHANGELOG.md:7 is 2026-11-27 #1")
        count += case(log(four), legacy="# comment\n" + entry(four)[:-1] + "x\n", expected=1,
                      needle=f"{LEGACY}:2: malformed line")
        # The cut-off: a listed bullet dated after 2026-11-27 fails; the twin is dated on it.
        count += case(log(four, date="2026-11-28"), legacy=entry(four, date="2026-11-28") + "\n",
                      expected=1, needle=f"{LEGACY}:1: {entry(four)[:12]} is dated 2026-11-28, "
                                         "after the cut-off 2026-11-27")
        # LEGACY_MAX: the list must hold exactly that many entries.
        count += case(log(four), legacy=entry(four) + "\n", legacy_max=0, expected=1,
                      needle=f"  FAIL  {LEGACY}: 1 entries, more than LEGACY_MAX (0)")
        count += case(log(four), legacy=entry(four) + "\n", legacy_max=2, expected=1,
                      needle=f"  FAIL  {LEGACY}: 1 entries, but LEGACY_MAX is 2; lower")
        # The base copy: every listed hash must be in the list at the merge base. An edited
        # legacy bullet relisted under its new hash fails; its twin is the unedited bullet.
        base = {"CHANGELOG.md": log(four, other),
                LEGACY: "\n".join(sorted([entry(four), entry(other, ref="#2")])) + "\n"}
        same = {"CHANGELOG.md": log(four), LEGACY: entry(four) + "\n"}
        count += git_case({"CHANGELOG.md": log(four), LEGACY: entry(four) + "\n"}, same,
                          needle=", every entry in the list at ", absent=("  SKIP  ",))
        count += git_case(same, {"CHANGELOG.md": log(edited), LEGACY: entry(edited) + "\n"},
                          expected=1, needle=f"{LEGACY}:1: {entry(edited)[:12]} is not in the "
                                             "list at the base commit")
        # A batch only deletes lines: rewriting one listed bullet and deleting its line passes.
        count += git_case(base, {"CHANGELOG.md": log(four, bullet(words(20), ref=" (#2)")),
                                 LEGACY: entry(four) + "\n"},
                          needle=", every entry in the list at ")
        # BASE_SHA names the base when set; one git cannot resolve fails.
        count += git_case(same, same, origin=False, env={"BASE_SHA": None},
                          needle=", every entry in the list at ")
        count += git_case(same, same, env={"BASE_SHA": "0" * 40}, expected=1,
                          needle=f"  FAIL  {LEGACY}: cannot compare with the base copy: "
                                 "BASE_SHA '0000")
        count += git_case(same, same, env={"BASE_SHA": "--all"}, expected=1,
                          needle="does not name a local commit")
        # A base with no list (the pull request that adds the gate) is skipped, not failed.
        count += git_case({"CHANGELOG.md": log(four)}, same,
                          needle=f"  SKIP  {LEGACY}: not compared with the base copy: the base "
                                 "commit ", also=(OK,))
        # No base ref: a SKIP locally, a finding under GitHub Actions; the same holds outside
        # a work tree, as in every fixture case above.
        count += git_case(same, same, origin=False,
                          needle="BASE_SHA is unset and refs/remotes/origin/main does not exist",
                          also=(OK,))
        count += git_case(same, same, origin=False, env={"GITHUB_ACTIONS": "true"}, expected=1,
                          needle=f"  FAIL  {LEGACY}: cannot compare with the base copy: "
                                 "BASE_SHA is unset")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write(root, same)
            code, output = run(root, legacy_max=1, env={"GITHUB_ACTIONS": "true"})
            count += verify(code, output, 1, "not the top of a git work tree", (), ())
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
        # Known limits: a boundary inside parentheses still splits, and a blank-looking
        # letter (U+3164) is a letter, so it glues words.
        count += case(log(bullet(words(3), words(3), "Word (see a. Word) end.")), expected=1,
                      needle="has 4 sentences")
        count += case(log(bullet(words(24, "") + " a\u3164b.")))
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
