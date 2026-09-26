#!/usr/bin/env python3
r"""Flag bracket ranges in fenced bash blocks.

WHY THIS EXISTS. Outside the C locale, ranges can match non-ASCII letters and digits. GNU
grep, GNU sed and Bash [[ =~ ]] accept non-ASCII samples with ASCII-looking ranges under
en_US.utf8. Bash case does so with globasciiranges disabled. Spell out the intended ASCII set,
for example [ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789]. An accept-list
POSIX class needs a C locale covering the whole check; a reject-list class can safely refuse
the locale's wider set. This gate does not interpret LC_ALL or classes.

THREAT MODEL. Under ruling (B), the gate targets locale-dependent ranges written by accident
in accept-list validators. Structural defects, including waiver scope, must be fixed. Runtime
expansion that changes a list, test-word-shaped data and constructed multiline quoting are
disclosed residual classes, not hardening targets. The ship criterion is that neither review
family finds a realistic, accidental fail-open. The fuzzer provides bounded evidence for its
alphabet, lengths, source scaffolds, engines, locales and probe character; it is not a general
Bash analyser or a defence against arbitrary runtime assembly.

THE MODEL. The scanner reads every fenced bash block selected by check_shell_blocks.blocks_of
in guides, README.md, controls-reference.md and CONTRIBUTING.md. It does no shell lexing.
Ordinary bracket parsing recognizes leading ^, literal leading ], ranges, and bounded POSIX
atoms. A glob ! is an ordinary member except before a leading literal ]. Quotes, comments and
heredoc bodies receive the same treatment. A backslash never hides an opener.

Every physical line keeps its own opener scan, including heredoc bodies. Quote parity is never
evidence of closure. A quote-free, escape-free ordinary closed prefix settles the lexical
reading; quotes after that prefix cannot reopen it. Leading literal closes (`[]`, `[^]`,
`[!]`), trailing backslashes, quotes or backslashes before the ordinary close, and unclosed
lists retain an alternative to the end of the same block. A list closing at physical end of
line and a negated list followed by a dot also retain that alternative because byte and
character matching can differ. Only backslash-newline is removed. No shell quote state, escape
decoding or expansion is computed. Quote removal and ordinary and anywhere-range readings
reach the last close in the span. Each spanning opener retains an unclosed finding even
without a literal range. Findings belong to the opener's physical line; waivers bind the entire
physical source span and enclosing block, so changing either invalidates the waiver. The
test-command exemption requires a standalone closing test word on the same physical line; a
bare one-word literal test is scanned too.

For an additional single-line reading, the region ends at the last close on that line. Quotes
or backslashes enable removal of both, and of dollars immediately before quotes. Ordinary
parsing and every interior X-Y are checked after removal. Dollars inside the ordinary list,
empty atom spellings [::], [==], [..], and literal-opener atoms [.[.], [=[=] enable this broad
reading too. Adjacent negated lists are findings because they can consume bytes under C and
characters under UTF-8. Terminal quote-affected closes retain the existing unclosed
alternatives. Each opener produces at most one finding; the ordinary close bounds the outer
scan.

SETTLEMENT. The narrower span trigger is sound for the lexical reading because a literal,
quote-free closed prefix already contains its closing bracket; later quotes cannot remove that
source character. Leading-literal-close alternatives are explicitly excluded from settlement.
Quotes or escapes inside the prefix make closure uncertain and keep the alternative through
the block, regardless of even quote counts. Expansion remains outside this proof. Complete
lists before continuations, quoted data, JSON arrays, comments, subscripts and unrelated
following commands can therefore be over-flagged.

THE ALLOWLIST. tools/bracket_ranges_allow.txt holds four TAB-separated fields:
<guide-file> TAB sha256:<span digest> TAB sha256:<block digest> TAB <reason>.
Each digest is 64 lowercase hex digits. Hash UTF-8 of the extracted, newline-normalized
text: blocks_of converts CRLF and bare CR to LF and removes fence indentation. The span
is the opener line, or, when any opener on that line retains a spanning reading, all lines
from it through block end. Join span lines with LF and add no trailing LF. The block digest
hashes the whole body returned by blocks_of, excluding fence lines. Preserve backslashes
and remaining whitespace; do not hash joined or quote-stripped readings. These are not
raw-file byte digests: a change only from LF to CRLF or bare CR keeps the waiver.
One entry consumes one flagged opener-line occurrence and covers its findings. Independent
later openers still need their own entries. Duplicate occurrences require duplicate entries.
No in-block waiver is accepted. Malformed digests, empty reasons, stale entries and retired
in-guide markers fail the gate. Moving a span to a different block body or editing any
extracted line of its enclosing block makes the entry stale, including lines before or after
the span. Absolute line numbers are not bound: edits elsewhere in the guide and movement
of a whole unchanged block within it keep the waiver. Range-free validator false positives
need a distinguishing reason.

Against qa/360-r7, the broad quote-presence rule adds 228 unwaived findings. Settling
quote-free closed prefixes reduces the final delta to 21 added findings on 19 lines and one
removed false positive. The added lines are egress-metadata.md:154; elasticsearch.md:33, :59,
:166, :188, :226 and :319; kubernetes.md:21; mcp-clients.md:101; model-servers.md:260;
rabbitmq.md:377 and :382; realtime-webhooks.md:124 and :135; and
self-hosted-ci-runners.md:118, :119, :120, :155 and :174. The removed finding is
container-hardening.md:112. Fourteen new waiver entries cover 15 expressions; existing entries
cover six additional expressions. The corpus has 0 unwaived findings in 416 bash blocks across
99 guides, with 39 consumed entries covering 49 expressions. These are false positives,
including the range-free RabbitMQ broker validators; they are not all non-validator text.

After merging main, the corpus delta against qa/360-r9 is 1 added and 0 removed findings:
Python sys.argv[1] indexing in the vLLM TCP probe. Four entries were rebound after main's
rule-7 guard sweep; their spans and reasons are unchanged. All 39 entries bind their intended
spans and blocks; 1274 individual block-line
edits each invalidate the corresponding waiver and leave a stale entry. Run
test_bracket_ranges.py --show-waivers to print every matched location, digests and extracted span.

The deterministic suite has 2892 cases (2830 ordinary, 41 allowlist, 4 quote-removal and 17
joining), 2884 checked behaviours, 8 disclosed blind spots and 17 entry-point runs. The
separate development fuzzer has 17 regression tests. Mutations removing block binding, using
a partial block, accepting legacy entries or malformed block digests, preserving raw line endings, binding only
the opener or skipping stale detection fail the suite. The fixed corpus includes the 1143 earlier
exploratory misses and all 1476 round-8 exploratory misses and 3 targeted misses. Seventeen
terminal-list variants include the 4 terminal exploratory misses. Both quote guards agree with
their original predicates on 776 values under each of C and en_US.utf8, with ordinary and
readonly quote-variable names, including diagnostics and exit status. Literal quote
alternatives have separate bracket-free case arms and assign no quote variables.

The development run uses C and en_US.utf8, 16 workers, lengths 0 through 5 over 17 characters,
and seven multiline scaffolds with insertions of lengths 0 through 4 over the same alphabet:
2,129,785 candidates per engine. Glob: 645,833 parsed, 157,068 live and flagged, 0 missed;
grep -E: 1,250,035 parsed, 18,010 live and flagged, 0 missed; Bash regex: 1,895,043 parsed,
250,686 live and flagged, 0 missed. These counts match round 8. The sample is é; every live
regex candidate must be detected in both its quoted assignment and, when multiline, its quoted
heredoc source. Coverage is bounded by these inputs.

The development fuzzer is excluded from offline gates because its collation locale may be
unavailable. It checks differences in either direction for the sample é; this includes some
non-range locale effects. Regex patterns are scanned as literal shell assignments and, for
multiline patterns, quoted heredoc bodies. Glob patterns retain their original source. Every
engine needs live candidates unless --allow-empty is explicit; startup canaries always require
both locale directions and detection.

RESIDUALS. tr can take ranges without brackets. Classes and \w can depend on locale without a
literal range. Variables or escaped brackets can assemble syntax at runtime. Empty-variable
expansion in [!$a] followed by a quoted newline can change a settled close into a literal
member and hide a later range (codex round-8 P1-1). Constructed multiline quoting is outside
the hardening target. Data shaped like a complete test command, for example re='^ [ a-z x ] +$',
can take the test-word exemption (codex round-8 P1-2). Non-bash fences are not scanned, and
extraction inherits check_shell_blocks.blocks_of limits. The eight blind-spot fixtures assert
known misses, including both P1 examples; they do not claim arbitrary shell coverage.
"""
import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _walk import walk_files  # noqa: E402  fail-closed tree walk
from check_shell_blocks import SKIP_DIRS, blocks_of  # noqa: E402  one definition of a bash block

# Root-level documents about the repository, which a reader does not copy from: the files
# not_a_guide() in tools/run_all_checks.sh names, less CONTRIBUTING.md, whose example blocks are
# the shapes new guides are built from, and controls-reference.md, which site/llms.txt lists.
NOT_A_GUIDE = frozenset(("CLAUDE.md", "AGENTS.md", "CHANGELOG.md", "README.sources.md", "TODO.md",
                         "DONE.md", "DECISIONS.md", "PENDING-DECISIONS.md", "SECURITY.md"))
# The waivers live here, one `<guide> TAB sha256:<span digest> TAB sha256:<block digest> TAB <reason>` per line.
ALLOWLIST = "bracket_ranges_allow.txt"
# The retired in-block waiver marker. A guide line holding one is a finding, wherever it sits:
# deciding whether such a comment is real is the lexing this gate no longer does.
MARKERISH_RE = re.compile(r"#[ \t]*bracket-ranges:")
# A test-word opener needs these boundaries and a standalone close on the same line.
TEST_BEFORE = " \t;&|(!"
# The interior an atom may carry and still count as one item: a class name, an equivalence
# class or a collating symbol. Anything longer or stranger is scanned as ordinary characters.
ATOM_RE = re.compile(r"[A-Za-z0-9]+\Z")
HINT = ("outside the C locale a bracket range can match non-ASCII letters and digits (GNU grep, "
        "GNU sed and bash [[ =~ ]] were observed doing it under en_US.utf8, and bash case does "
        "it with globasciiranges off), so a validator written with one accepts values it claims "
        "to refuse. Spell the set out, as in "
        "[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789]. Where the range is "
        "not a validator, add a '<guide> TAB sha256:<span digest> TAB sha256:<block digest> TAB <reason>' entry to "
        "tools/bracket_ranges_allow.txt; the entry binds the extracted span and enclosing block, "
        "as documented in tools/check_bracket_ranges.py.")


def _atom(text, j, n):
    """The close index of the `[:class:]`, `[=x=]` or `[.x.]` atom at text[j], or None.

    An atom counts only when its interior is the single item those forms carry: letters and
    digits, or any one character that is not `[`. Round 3 assembled `[[:` and `:]]` from two
    printf arguments, and an unconstrained forward search swallowed the live validator between
    them as one atom; an interior holding a quote, a space or a `[` is not an atom here, and
    the caller scans it as ordinary characters instead, which fails closed.
    """
    close = text.find(text[j + 1] + "]", j + 2, n)
    if close == -1:
        return None
    interior = text[j + 2:close]
    if ATOM_RE.fullmatch(interior) or (len(interior) == 1 and interior != "["):
        return close
    return None


def _parse_list(text, j, prev):
    """Read a bracket list from text[j], with `prev` the item already read or None.

    Returns (close_index, ranges), or (None, ranges) when the end of the line comes first.
    """
    n, ranges = len(text), []
    while j < n:
        c = text[j]
        if c == "]":
            return j, ranges
        if c == "[" and text[j + 1:j + 2] in (":", "=", "."):
            close = _atom(text, j, n)
            if close is not None:
                # A class cannot be a range endpoint; an equivalence or collating symbol can.
                prev = None if text[j + 1] == ":" else text[j:close + 2]
                j = close + 2
                continue
            # Not an atom: the `[` is an ordinary item, scanned like any other character, so a
            # range hidden past a fake atom opener is still seen.
        if c == "-" and prev is not None and j + 1 < n and text[j + 1] != "]":
            k = j + 1
            if text[k] == "[" and text[k + 1:k + 2] in ("=", "."):
                close = _atom(text, k, n)
                if close is not None:
                    end, j = text[k:close + 2], close + 2
                else:
                    end, j = text[k], k + 1
            elif text[k] == "[" and text[k + 1:k + 2] == ":":
                close = _atom(text, k, n)
                if close is not None:
                    prev, j = None, j + 1
                    continue
                end, j = text[k], k + 1
            else:
                end, j = text[k], k + 1
            ranges.append(prev + "-" + end)
            prev = None
            continue
        prev = c
        j += 1
    return None, ranges


def _parse_bracket(text, i):
    """Parse the bracket expression opening at text[i]. Returns (close_index, ranges).

    POSIX rules: a leading `^` negates, a `]` first in the list is a literal and may start a
    range, `[:class:]`, `[=x=]` and `[.x.]` are single items when _atom recognizes them, and a
    hyphen that is neither first nor last joins the items on either side of it into a range. A
    glob's `!` is read as an ordinary character, so `[!0-9]` still holds the range 0-9 and
    `[!-~]`, which a regex reads as the range ! to ~, is flagged; a `]` right after `[!` is
    read as a glob reads it, a literal, whenever a later `]` on the line closes the expression.
    A `[]` or `[^]` that no later `]` on the line closes is the empty pair of a JSON, jq or
    JMESPath expression in this reading; the spanning alternatives still apply. A backslash is an
    ordinary character inside brackets. Returns (None, ranges) when nothing closes the
    expression on this line.
    """
    j = i + 1
    if text[j:j + 1] == "^":
        j += 1
    if text[j:j + 1] == "]" or text[j:j + 2] == "!]":
        close, ranges = _parse_list(text, j + 1 if text[j] == "]" else j + 2, "]")
        if close is not None:
            return close, ranges
    # Nothing later on the line closes it, so `[]` and `[^]` are an empty pair, `[!]` a set.
    return _parse_list(text, j, None)


def _strip_quotes(region):
    """Delete quotes, backslashes and a dollar sign directly before either quote."""
    region = region.replace("$'", "'").replace('$"', '"')
    return region.translate(str.maketrans("", "", "'\"\\"))


def _ambiguous_close(text, start, close):
    """Preserve the old terminal unclosed alternatives; never bound range scanning.

    The full last-close region handles ranges independently of this local fallback.
    """
    before, after = text[close - 1], text[close + 1:close + 2]
    return before in "\\'\"" or (after in ("'", '"') and after in text[start + 1:close])


def _adjacent_negated(text, i):
    """A second negated list after the first list's literal leading member, if any."""
    if text[i:i + 2] not in ("[^", "[!"):
        return False
    j = i + 2
    if text[j:j + 1] == "]":
        j += 1
    close, _ = _parse_list(text, j, None)
    return close is not None and text[close + 1:close + 3] in ("[^", "[!")


def bracket_hits(text, span=None):
    """Yield one description per bracket expression in one line's text holding a range, and per
    `[` left open at the end of the line. Optional span is text or a callable returning
    a span for each opener; stripped ordinary and anywhere-range readings supplement the ordinary parse. Terminal
    unclosed alternatives remain conservative. Only the ordinary close bounds the outer scan.
    A backslash before `[` never hides an opener."""
    i, n = 0, len(text)
    while i < n:
        if text[i] != "[":
            i += 1
            continue
        word_end = i + 2 if text.startswith("[[", i) else i + 1
        if (i == 0 or text[i - 1] in TEST_BEFORE) and word_end < n and text[word_end] in " \t":
            closing = "]]" if word_end == i + 2 else "]"
            end = re.search(r"(?<!\S)" + re.escape(closing) + r"(?=$|[\s;&|)])", text[word_end:])
            if end is not None:
                operands = text[word_end:word_end + end.start()]
                # A bare one-word test is not a validator. Scan its literal argument so
                # heredoc patterns such as [ -z ] do not inherit this exemption.
                if len(operands.split()) > 1 or any(c in operands for c in "'\"\\$"):
                    i = word_end
                    continue
        close, ranges = _parse_bracket(text, i)
        reading = span(i) if callable(span) else span
        extended = text if reading is None else reading
        last = extended.rfind("]", i + 1)
        region = extended[i:last + 1] if last >= 0 else extended[i:]
        affected = reading is not None or any(c in region for c in ("'", '"', chr(92)))
        # The exhaustive glob check found unset variables exposing a leading literal close:
        # [$a]-z] becomes []-z]. A dollar inside the ordinary list gets the broad reading too.
        affected |= "$" in text[i:close + 1 if close is not None else n]
        # Empty atoms and atoms containing '[' need a conservative additional reading.
        # Their apparent close may be internal to a live glob range.
        affected |= any(atom in region for atom in ("[::]", "[==]", "[..]", "[.[.]", "[=[=]"))
        if affected:
            stripped = _strip_quotes(region)
            _, stripped_ranges = _parse_bracket(stripped, 0)
            # Every interior close may be a quoted member. Do not stop at any of them,
            # or let atom recognition hide a range in this deliberately broad reading.
            anywhere = re.findall(r"(?=(.-.))", stripped[1:-1], re.DOTALL)
            ranges = list(dict.fromkeys(ranges + stripped_ranges + anywhere))
        # Preserve terminal unclosed alternatives from round 5, including a buried quoted
        # close at physical end of line. The range readings above need no adjacency rule.
        unclosed = close is None or reading is not None or (
            affected and last >= 0 and (
                _ambiguous_close(extended, i, last) or not extended[last + 1:].strip()))
        if ranges and close is not None:
            noun = "range" if len(ranges) == 1 else "ranges"
            shown = region if affected else text[i:close + 1]
            shown = shown.replace("\n", r"\n")
            listed = ", ".join(ranges).replace("\n", r"\n")
            yield f"{shown} holds the {noun} {listed}"
        elif _adjacent_negated(text, i):
            yield ("adjacent negated bracket lists can consume separate bytes under C "
                   "instead of one UTF-8 character; spell out their intended ASCII sets")
        elif unclosed:
            yield (f"{text[i:i + 60].rstrip()} opens a bracket expression that nothing closes "
                   f"on its physical line in at least one reading, so a range in it cannot "
                   f"be ruled out,")
        # Only the ordinary close bounds the outer scan. The extra readings cannot swallow
        # an independent opener later on this line.
        i = close + 1 if close is not None else i + 1


class Allowlist:
    """The entries of tools/bracket_ranges_allow.txt, each consumable by one flagged source span.

    `findings` holds what loading itself flagged (a malformed entry, an empty field); `take`
    consumes one entry for one flagged occurrence of a source span; `stale` names every entry nothing
    consumed, so an entry cannot outlive the span and block it was written for.
    """

    def __init__(self):
        self.findings, self.n_entries, self._avail = [], 0, {}

    @classmethod
    def load(cls, path):
        """Read the allowlist at `path`. A missing file is an empty allowlist, which only
        refuses more; a file that exists but cannot be read raises (OSError or
        UnicodeDecodeError), which main turns into a failed gate rather than an empty list."""
        allow = cls()
        if not path.exists():
            return allow
        where = f"tools/{path.name}"
        for lineno, raw in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
            if not raw.strip() or raw.startswith("#"):
                continue
            parts = raw.split("\t")
            guide = parts[0]
            if len(parts) != 4 or not guide.strip() or not all(parts[1:3]):
                allow.findings.append(f"{where}:{lineno}: malformed allowlist entry: four "
                                      f"TAB-separated fields: guide, SHA-256 span, "
                                      f"SHA-256 block, reason")
                continue
            _, text, block, reason = parts
            if re.fullmatch(r"sha256:[0-9a-f]{64}", text) is None:
                allow.findings.append(f"{where}:{lineno}: malformed allowlist span: "
                                      f"expected sha256: followed by 64 lowercase hex digits")
                continue
            if re.fullmatch(r"sha256:[0-9a-f]{64}", block) is None:
                allow.findings.append(f"{where}:{lineno}: malformed allowlist block: "
                                      f"expected sha256: followed by 64 lowercase hex digits")
                continue
            if not reason.strip():
                allow.findings.append(f"{where}:{lineno}: allowlist entry with an empty "
                                      f"reason: say why the line is not a validator")
                continue
            allow._avail.setdefault((guide, text, block), []).append((lineno, where))
            allow.n_entries += 1
        return allow

    def take(self, guide, text, block):
        """Consume one entry for a flagged `text` in its extracted `block` and `guide`."""
        digest = "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()
        block_digest = "sha256:" + hashlib.sha256(block.encode("utf-8")).hexdigest()
        left = self._avail.get((guide, digest, block_digest))
        if not left:
            return False
        left.pop(0)
        return True

    def stale(self):
        """One finding per entry that no flagged span consumed."""
        out = []
        for (guide, _, _), left in self._avail.items():
            out.extend((lineno, f"{where}:{lineno}: stale allowlist entry: no flagged span of "
                                f"{guide} matches its extracted span and enclosing block")
                       for lineno, where in left)
        return [msg for _, msg in sorted(out)]


def _may_span(text):
    """Settle only the lexical closed prefix; retain every ambiguous alternative.

    Leading literal closes are never settled by the empty-pair fallback. The dot rule
    preserves the fuzzer's non-range byte/character counterexamples. Expansion is not parsed.
    """
    if text.endswith("\\") or text.startswith(("[]", "[^]", "[!]")):
        return True
    close, _ = _parse_bracket(text, 0)
    if close is not None and not text[close + 1:].strip():
        return True
    if close is not None and text.startswith("[^") and text[close + 1:].startswith("."):
        return True
    return close is None or any(c in text[:close] for c in "'\"\\")


def joined_reading(lines, idx, opener=None):
    """Keep unresolved alternatives within this block; remove backslash-newline only.

    No later quote count proves closure, so these alternatives stay open to block end.
    Calling per opener prevents a quote in a preceding command from tainting a plain set.
    """
    text = lines[idx]
    if opener is None:
        opener = text.find("[")
    if opener < 0 or not _may_span(text[opener:]):
        return None
    for tail in lines[idx + 1:]:
        text = (text[:-1] if text.endswith("\\") else text + "\n") + tail
    return text


def scan_blocks(name, blocks, allow):
    """Scan one guide's bash blocks, one physical line at a time, against `allow`.

    Returns (findings, n_blocks, n_waived). Every physical line is read the same way, a
    here-document body like any other. A covered source span consumes one entry for that
    occurrence; n_waived counts expressions, not entries.
    """
    findings, n_blocks, n_waived = [], 0, 0
    for start, body in blocks:
        n_blocks += 1
        lines = body.split("\n")
        for idx, raw in enumerate(lines):
            spans = []

            def reading(opener):
                joined = joined_reading(lines, idx, opener)
                if joined is not None:
                    spans.append(joined)
                return joined

            hits = list(bracket_hits(raw, reading))
            if not hits:
                continue
            # Bind extracted, newline-normalized text, retaining backslash-newlines.
            # A spanning reading currently extends through the end of its Bash block.
            key = "\n".join(lines[idx:]) if spans else raw
            if allow.take(name, key, body):
                n_waived += len(hits)
                continue
            findings.extend(f"{name}:{start + idx}: {what} and no allowlist entry covers its "
                            f"source span" for what in hits)
    return findings, n_blocks, n_waived


def scan_path(path, allow=None):
    """Scan one guide file: its whole text for the retired in-block marker, and every physical
    line of its bash blocks for ranges, unclosed alternatives and adjacent negated lists. Raises what blocks_of raises on a
    file it cannot read. With no allowlist given, nothing is waived."""
    allow = Allowlist() if allow is None else allow
    findings = [f"{path.name}:{lineno}: in-guide bracket-ranges marker: waivers live in "
                f"tools/{ALLOWLIST}, keyed by the guide, complete physical span and enclosing block"
                for lineno, raw in enumerate(path.read_text(encoding="utf-8").split("\n"), 1)
                if MARKERISH_RE.search(raw)]
    found, n_blocks, n_waived = scan_blocks(path.name, list(blocks_of(path)), allow)
    return findings + found, n_blocks, n_waived


def scan_repo(root):
    """Scan every guide under root against the allowlist.

    Returns (findings, n_files, n_blocks, n_waived), the stale-entry findings included.
    """
    allow = Allowlist.load(root / "tools" / ALLOWLIST)
    paths = sorted(walk_files(root, SKIP_DIRS, suffixes={".md"}))
    findings, n_files, n_blocks, n_waived = list(allow.findings), 0, 0, 0
    for path in paths:
        if path.parent != root or path.name in NOT_A_GUIDE:
            continue
        try:
            found, blocks_here, waived = scan_path(path, allow)
        except Exception as exc:
            findings.append(f"{path.name}: unreadable ({exc})")
            continue
        findings.extend(found)
        n_blocks += blocks_here
        n_waived += waived
        n_files += 1 if blocks_here else 0
    findings.extend(allow.stale())
    return findings, n_files, n_blocks, n_waived


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        findings, n_files, n_blocks, n_waived = scan_repo(root)
    except Exception as exc:
        print(f"  FAIL  could not scan the repository: {exc}")
        return 1
    if not findings and not n_blocks:
        # A pass over nothing is not a pass.
        findings.append("no bash block was found in any guide, so nothing was checked")
    if findings:
        for f in findings:
            print(f"  FAIL  {f}")
        print(f"  FAIL  {HINT}")
        return 1
    print(f"  ok    no unwaived bracket range in {n_blocks} bash blocks across {n_files} "
          f"guides ({n_waived} expressions waived by tools/{ALLOWLIST})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
