#!/usr/bin/env python3
"""Check the length of CHANGELOG.md bullets: at most 3 sentences, each at most 25 words.

WHY: the maintainer ruled on 2026-11-27 that every CHANGELOG.md bullet has at most 3
sentences of at most 25 words each, that the older bullets are rewritten to it in batches,
and that a gate holds it (DECISIONS.md). Until the last batch lands, the bullets that broke
the rule when the gate was added are listed by hash in tools/changelog_bullets_legacy.txt
and exempt; every new or changed bullet must comply.

WHAT A BULLET IS, reading CHANGELOG.md as LF-separated lines from the first `## YYYY-MM-DD`
heading on: a line that starts with `- ` at column 0, plus each following line up to the
next such line, an ATX heading line, or a blank line. Following lines are stripped and
joined with one space, and a nested item's `- ` marker is dropped. The preamble above the
first dated heading and the ATX heading lines are not bullets. Any other non-blank line
under a dated heading (a `*` or `+` item, an indented item or a paragraph after a blank
line, a line of text right under a heading) is a finding, and so is any fence line (one
that starts with three backticks or tildes after optional indentation and an optional
`- ` marker, so a fence opened on a bullet's own first line counts), inside a bullet or
not: the gate does not model them, so it fails closed.

WHAT IS COUNTED:

- A trailing reference such as `(#1424)`, `(#1288).` or `(#38, #41)` is removed first; a
  `#N` elsewhere is text.
- Sentences are those of split_rendered() in tools/sentence_split.py, the splitter the
  400-character rules use, with its documented limits: no split inside a code span or an
  open quotation, after e.g., i.e., vs. or cf., at a dot with no space after it (as in a
  version number), or at a semicolon or colon; a boundary inside parentheses still splits.
- Words are the tokens of a sentence, as rendered (a link counts as its text), that hold
  at least one letter or digit. Tokens are separated by whitespace and by every character
  in BLANK_CATEGORIES of tools/_reason.py (Unicode categories Cf, Zs, Zl and Zp), so a
  zero-width space such as U+200B, U+2060 or U+FEFF, or a soft hyphen, separates words.
  Known limit: a blank-looking character outside those categories, such as U+3164 (a
  letter, Lo) or U+2800 (a braille blank, So), does not separate words, so it glues the
  words on either side into one. A code span counts as ONE word, glued punctuation
  included, unless its content is over 60 characters or holds more than 8 internal spaces;
  then it is counted by its words. The 60-character test counts the content as CommonMark
  renders it: when the content both begins and ends with a space and is not all spaces,
  one space is stripped from each side, and no more. Internal spaces are those left after
  every leading and trailing space is stripped. A backtick that no run closes is plain
  text, so its words count (a D-1096 vote of 2026-11-27, confirmed by the maintainer on
  2026-11-28).

ALSO FINDINGS: two bullets with the same joined text, wherever they are, and, in a bullet
that is not listed, a Cf character (it still separates words, but it is invisible, so
delete it) and a version sentence that the ruling dropped: `VERSION` listed with
`plugin.json` (as `plugin/plugin.json` or `plugin.json`), optionally followed by `and`
and `SKILL.md` (as `plugin/skills/secureconfig/SKILL.md`, `SKILL.md`, "the plugin's" or
"the plugin" form, code span or not), then "go to", "move to", "stay at", "remain at",
"are bumped", "are updated", "are set", "carry the" or "carry this", "are" or "is"
before a digit, in any of their tenses VERSION_SENTENCE names. "are unchanged" and a
mention such as "`VERSION` to `plugin/plugin.json`'s version" are not findings.

THE LEGACY LIST: one line per exempt bullet, `<sha256> <date> <reference>`, sorted by
hash, where the hash is of the joined bullet text above, as UTF-8, and the reference is
the trailing reference without its brackets, or `-`. Lines starting `#` are comments.
The gate fails when a non-compliant bullet is not listed, a listed hash matches no bullet
(so editing a listed bullet fails twice), a listed bullet now complies, a hash repeats,
a line's date or reference no longer matches its bullet, a line is dated after CUTOFF
(2026-11-27, the ruling's date), the list is out of order or a line is malformed. The
list must hold exactly LEGACY_MAX entries. LEGACY_MAX was set to the length of the list
generated when the gate was added; a batch deletes its lines and lowers LEGACY_MAX by the
same number, and nothing may raise it. `--list-legacy` prints the list for the current
file; rerunning it to exempt a new bullet grows the list past LEGACY_MAX and fails.

THE BASE COPY: an edited legacy bullet has a new hash, and swapping its old line for the
new one would keep the count. So every listed hash must also be in the list as committed
at the base commit: the merge base of HEAD and $BASE_SHA when that variable is set and not
empty (the CI `gates` step sets it to the pull request's base), else of HEAD and
refs/remotes/origin/main. The gate reads that copy with local git only (`git rev-parse`,
`git merge-base`, `git ls-tree`, `git cat-file`), and sets GIT_NO_LAZY_FETCH=1 against
lazy fetching in a partial clone (not tested on one; CI's checkout is a full clone). A
$BASE_SHA that git cannot resolve, a failed `git merge-base`, `git ls-tree` or
`git cat-file blob`, or a base copy that is not UTF-8 is a finding. `git ls-tree` tells a
missing list apart from a git error, which is a finding. The comparison is skipped, with
a SKIP line, when the base commit has neither the list nor this gate: that base predates
the gate, so the change is the one that adds it. Any commit at or after the merge of the
pull request that adds the gate holds this file, so a base that holds the gate but not
the list cannot be that pull request; it is a finding under GitHub Actions. That test
reads only the base commit's tree, so it is deterministic and needs no constant to
change after the merge. Outside GitHub Actions, a base with the gate but no list, a root
that is not the top of a git work tree, git that cannot run, or no base ref is a SKIP;
under GitHub Actions (GITHUB_ACTIONS=true) those four are findings. A local answer
depends on how fresh the local origin/main is.

Fails closed: a missing or non-UTF-8 file is an error (exit 2), and a carriage return
or a changelog with no bullet is a finding (exit 1).

Deterministic and offline: it reads CHANGELOG.md, the legacy list and, through local git,
the base commit's copy of the list.
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _reason import BLANK_CATEGORIES  # noqa: E402
from sentence_split import render, split_rendered  # noqa: E402

CHANGELOG = "CHANGELOG.md"
LEGACY = "tools/changelog_bullets_legacy.txt"
GATE = "tools/check_changelog_bullets.py"
MAX_SENTENCES = 3
MAX_WORDS = 25
SPAN_CHARS = 60
SPAN_SPACES = 8
# The number of entries in LEGACY. Set once, from the generated list; batches only lower it.
LEGACY_MAX = 1254
# The ruling's date: a bullet dated later is new and must comply, never be listed.
CUTOFF = "2026-11-27"

DATED = re.compile(r"## ([0-9]{4}-[0-9]{2}-[0-9]{2})[ \t]*")
ATX = re.compile(r" {0,3}#{1,6}(?:[ \t]|$)")
FENCE = re.compile(r"[ \t]*(?:- )?[ \t]*(?:```|~~~)")
TRAILING_REF = re.compile(r"\s*\((#[0-9]+(?:,\s*#[0-9]+)*)\)\.?\Z")
VERSION_SENTENCE = re.compile(
    r"`VERSION`,?\s+(?:and\s+)?`?(?:plugin/)?plugin\.json`?"
    r"(?:,?\s+and\s+(?:the\s+plugin(?:'s)?\s+)?`?(?:plugin/skills/secureconfig/)?SKILL\.md`?)?"
    r",?\s+(?:go(?:es)?\s+to|went\s+to|gone\s+to|mov(?:e|es|ed|ing)\s+to"
    r"|stay(?:s|ed|ing)?\s+at|remain(?:s|ed|ing)?\s+at"
    r"|(?:are|were|is|was)\s+(?:bumped|updated|set)\b|(?:carry|carries|carried)\s+(?:the|this)\b"
    r"|(?:are|were|is|was)\s+`?[0-9])")
LEGACY_LINE = re.compile(r"([0-9a-f]{64}) ([0-9]{4}-[0-9]{2}-[0-9]{2}) (#[0-9]+(?:, #[0-9]+)*|-)")
HEADER = ("# CHANGELOG.md bullets exempt from tools/check_changelog_bullets.py until their batch.\n"
          "# Generated by its --list-legacy option; each batch only deletes lines.\n")


def separators(text):
    """text with every BLANK_CATEGORIES character replaced by a space."""
    return "".join(" " if unicodedata.category(ch) in BLANK_CATEGORIES else ch for ch in text)


def count_words(rendered, start, end):
    """Words in rendered.text[start:end], with the code-span rules above."""
    text = list(rendered.text[start:end])
    for a, b in sorted(rendered.code, reverse=True):
        if a < start or b > end:
            continue
        span = rendered.text[a:b]
        ticks = len(span) - len(span.lstrip("`"))
        content = span[ticks:len(span) - ticks]
        if len(content) > 1 and content[0] == content[-1] == " " and content.strip(" "):
            content = content[1:-1]
        if len(content) <= SPAN_CHARS and content.strip(" ").count(" ") <= SPAN_SPACES:
            text[a - start:b - start] = ["W"]
    return sum(1 for token in separators("".join(text)).split()
               if any(ch.isalnum() for ch in token))


class Bullet:
    """One bullet: its first line number, date, joined text and per-sentence word counts."""

    def __init__(self, date, parts):
        self.line, self.date = parts[0][0], date
        self.text = " ".join(text for _, text in parts)
        self.digest = hashlib.sha256(self.text.encode("utf-8")).hexdigest()
        match = TRAILING_REF.search(self.text)
        self.ref = re.sub(r",\s*", ", ", match.group(1)) if match else "-"
        rendered = render(self.text[:match.start()] if match else self.text)
        offsets, at = [], 0
        for number, text in parts:
            offsets.append((at, number))
            at += len(text) + 1
        self.sentences = []
        for start, sentence in split_rendered(rendered):
            offset = rendered.src[start]
            number = [n for o, n in offsets if o <= offset][-1]
            self.sentences.append((number, sentence,
                                   count_words(rendered, start, start + len(sentence))))

    def complies(self):
        return (len(self.sentences) <= MAX_SENTENCES
                and all(words <= MAX_WORDS for _, _, words in self.sentences))

    def legacy_line(self):
        return f"{self.digest} {self.date} {self.ref}"


def bullets(lines):
    """(every bullet of the changelog in order, findings for lines outside the model)."""
    found, findings, date, parts = [], [], None, []

    def close():
        nonlocal parts
        if parts:
            found.append(Bullet(date, parts))
        parts = []

    for number, line in enumerate(lines, 1):
        heading = DATED.fullmatch(line)
        if heading:
            close()
            date = heading.group(1)
        elif date is None:
            continue
        elif FENCE.match(line):
            close()
            findings.append((CHANGELOG, number, "fence line under a dated heading; the gate "
                                                "does not model fenced blocks"))
        elif line.startswith("- "):
            close()
            parts = [(number, line[2:].strip())]
        elif not line.strip() or ATX.match(line):
            close()
        elif parts:
            text = line.strip()
            parts.append((number, text[2:].strip() if text.startswith("- ") else text))
        else:
            findings.append((CHANGELOG, number, "text under a dated heading outside a `- ` "
                                                f"bullet: {line.strip()[:60]!r}"))
    close()
    return found, findings


def read_legacy(text, name=LEGACY):
    """(entries as {digest: (line number, date, ref)}, findings) for a legacy list."""
    entries, findings, previous = {}, [], None
    for number, line in enumerate(text.split("\n"), 1):
        if not line or line.startswith("#"):
            continue
        match = LEGACY_LINE.fullmatch(line)
        if not match:
            findings.append((name, number, f"malformed line {line[:80]!r}"))
            continue
        digest, date, ref = match.groups()
        if digest in entries:
            findings.append((name, number, f"{digest[:12]} repeats line {entries[digest][0]}"))
            continue
        if previous is not None and digest < previous:
            findings.append((name, number, f"{digest[:12]} is out of order; sort by hash"))
        previous = digest
        entries[digest] = (number, date, ref)
    return entries, findings


def check(lines, legacy_text, legacy_max=LEGACY_MAX, base=None):
    """(findings as (file, line, message), bullets) for the changelog and legacy list.

    base is None (no comparison) or (commit, text of the list at that commit).
    """
    found, findings = bullets(lines)
    first_cr = next((n for n, line in enumerate(lines, 1) if "\r" in line), None)
    if first_cr:
        findings.append((CHANGELOG, first_cr, "this line holds a carriage return; the gate "
                                              "splits on LF alone"))
    if "\r" in legacy_text:
        findings.append((LEGACY, None, "the list holds a carriage return"))
    entries, list_findings = read_legacy(legacy_text)
    findings += list_findings
    if len(entries) > legacy_max:
        findings.append((LEGACY, None, f"{len(entries)} entries, more than LEGACY_MAX "
                                       f"({legacy_max}); a new or changed bullet must comply, "
                                       "never be listed"))
    elif len(entries) < legacy_max:
        findings.append((LEGACY, None, f"{len(entries)} entries, but LEGACY_MAX is "
                                       f"{legacy_max}; lower LEGACY_MAX in "
                                       f"tools/check_changelog_bullets.py to {len(entries)}"))
    for digest, (number, date, _) in entries.items():
        if date > CUTOFF:
            findings.append((LEGACY, number, f"{digest[:12]} is dated {date}, after the cut-off "
                                             f"{CUTOFF}; a later bullet must comply, never be "
                                             "listed"))
    if base is not None:
        commit, base_text = base
        base_entries = read_legacy(base_text, f"{LEGACY} at {commit[:12]}")[0]
        for digest, (number, _, _) in entries.items():
            if digest not in base_entries:
                findings.append((LEGACY, number, f"{digest[:12]} is not in the list at the base "
                                                 f"commit {commit[:12]}; the list only loses "
                                                 "lines (an edited legacy bullet must comply)"))
    by_digest = {}
    for bullet in found:
        first = by_digest.setdefault(bullet.digest, bullet)
        if first is not bullet:
            findings.append((CHANGELOG, bullet.line, f"bullet repeats the text of the bullet at "
                                                     f"{CHANGELOG}:{first.line}"))
        blank = next((ch for ch in bullet.text if unicodedata.category(ch) == "Cf"), None)
        listed = entries.get(bullet.digest)
        if listed:
            if (listed[1], listed[2]) != (bullet.date, bullet.ref):
                findings.append((LEGACY, listed[0], f"says {listed[1]} {listed[2]}, but its "
                                 f"bullet at {CHANGELOG}:{bullet.line} is {bullet.date} "
                                 f"{bullet.ref}"))
            continue
        where = f"bullet ({bullet.date} {bullet.ref}), not in {LEGACY},"
        if blank:
            findings.append((CHANGELOG, bullet.line, f"{where} holds U+{ord(blank):04X}, an "
                                                     "invisible format character; it separates "
                                                     "words here, but delete it"))
        if VERSION_SENTENCE.search(bullet.text):
            findings.append((CHANGELOG, bullet.line, f"{where} restates the version; the "
                                                     "fixed-form version sentence was dropped"))
        if len(bullet.sentences) > MAX_SENTENCES:
            findings.append((CHANGELOG, bullet.line, f"{where} has {len(bullet.sentences)} "
                                                     f"sentences; at most {MAX_SENTENCES}"))
        for k, (number, sentence, words) in enumerate(bullet.sentences, 1):
            if words > MAX_WORDS:
                findings.append((CHANGELOG, number, f"{where} sentence {k} has {words} words; "
                                                    f"at most {MAX_WORDS}: {sentence[:60]!r}"))
    for digest, (number, _, _) in entries.items():
        bullet = by_digest.get(digest)
        if bullet is None:
            findings.append((LEGACY, number, f"{digest[:12]} matches no bullet; delete the "
                                             "line (an edited legacy bullet must comply)"))
        elif bullet.complies():
            findings.append((LEGACY, number, f"{digest[:12]} ({CHANGELOG}:{bullet.line}) now "
                                             "complies; delete the line"))
    return findings, found


def git(root, *args):
    """Run local git in root; (exit status, stdout bytes, stderr text). Never fetches."""
    env = dict(os.environ, GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
    try:
        result = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                                env=env, timeout=60, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, b"", str(exc)
    return result.returncode, result.stdout, result.stderr.decode("utf-8", "replace").strip()


def base_copy(root):
    """(state, detail) for the base list: ("found", (commit, text)), ("absent", reason) when
    the base predates the gate, ("skip", reason) or ("fail", reason)."""
    status, out, err = git(root, "rev-parse", "--show-toplevel")
    if status is None:
        return "skip", f"git cannot run ({err})"
    if status != 0 or Path(out.decode("utf-8", "replace").strip()).resolve() != root:
        return "skip", "the root is not the top of a git work tree"
    ref = os.environ.get("BASE_SHA", "")
    if ref:
        status, out, err = (1, b"", "") if ref.startswith("-") else git(
            root, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
        if status != 0:
            return "fail", f"BASE_SHA {ref[:40]!r} does not name a local commit"
    else:
        ref = "refs/remotes/origin/main"
        status, out, err = git(root, "rev-parse", "--verify", "--quiet", ref + "^{commit}")
        if status != 0:
            return "skip", "BASE_SHA is unset and refs/remotes/origin/main does not exist"
    status, out, err = git(root, "merge-base", out.decode("ascii", "replace").strip(), "HEAD")
    if status != 0:
        return "fail", f"git merge-base {ref[:40]} HEAD failed: {err[:120] or status}"
    commit = out.decode("ascii", "replace").strip()
    status, out, err = git(root, "ls-tree", "--full-tree", "--name-only", "-z", commit, "--",
                           LEGACY, GATE)
    if status != 0:
        return "fail", f"git ls-tree {commit[:12]} failed: {err[:120] or status}"
    names = out.decode("utf-8", "replace").split("\0")
    if LEGACY not in names:
        if GATE not in names:
            return "absent", f"the base commit {commit[:12]} predates the gate (no {LEGACY})"
        return "skip", f"the base commit {commit[:12]} has {GATE} but no {LEGACY}"
    status, out, err = git(root, "cat-file", "blob", f"{commit}:{LEGACY}")
    if status != 0:
        return "fail", f"cannot read {LEGACY} at {commit[:12]}: {err[:120]}"
    try:
        return "found", (commit, out.decode("utf-8"))
    except UnicodeError as exc:
        return "fail", f"{LEGACY} at {commit[:12]} is not UTF-8: {exc}"


def main(argv=None, legacy_max=LEGACY_MAX):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--list-legacy", action="store_true",
                        help="print the legacy list for the current CHANGELOG.md and exit")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        text = (root / CHANGELOG).read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"  FAIL  cannot check {CHANGELOG}: {exc}")
        return 2
    lines = text.split("\n")
    if text.endswith("\n"):
        lines.pop()
    if args.list_legacy:
        listed = sorted({b.legacy_line() for b in bullets(lines)[0] if not b.complies()})
        sys.stdout.write(HEADER + "".join(f"{line}\n" for line in listed))
        return 0
    try:
        legacy_text = (root / LEGACY).read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"  FAIL  cannot check {LEGACY}: {exc}")
        return 2
    state, detail = base_copy(root)
    in_ci = os.environ.get("GITHUB_ACTIONS") == "true"
    findings, found = check(lines, legacy_text, legacy_max,
                            detail if state == "found" else None)
    notes = []
    if state == "fail" or (state == "skip" and in_ci):
        findings.append((LEGACY, None, f"cannot compare with the base copy: {detail}"))
    elif state in ("skip", "absent"):
        notes.append(f"  SKIP  {LEGACY}: not compared with the base copy: {detail}")
    if not found:
        findings.append((CHANGELOG, None, "no bullet under a dated `## YYYY-MM-DD` heading "
                                          "was found"))
    for note in notes:
        print(note)
    if findings:
        for name, number, message in findings:
            print(f"  FAIL  {name}:{number}: {message}" if number else f"  FAIL  {name}: {message}")
        return 1
    comply = sum(1 for b in found if b.complies())
    based = f", every entry in the list at {detail[0][:12]}" if state == "found" else ""
    print(f"  ok    {CHANGELOG}: {len(found)} bullets, {comply} within {MAX_SENTENCES} "
          f"sentences of {MAX_WORDS} words, {len(found) - comply} listed in {LEGACY} "
          f"(LEGACY_MAX {legacy_max}{based})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
