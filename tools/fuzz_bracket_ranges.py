#!/usr/bin/env python3
r"""Development-only differential check; deliberately absent from run_all_checks.sh.

Run: TMPDIR=/path/to/writable/scratch python3 tools/fuzz_bracket_ranges.py \
    --max-length 6 --multiline-length 4 --jobs 16 --engines glob grep regex
Requires bash, GNU grep and a UTF-8 locale with non-ASCII range collation, normally
en_US.utf8. Startup canaries require both locale directions and gate detection; they reject
C.utf8 when it cannot distinguish the samples from C. --allow-empty permits a zero-live
selection on any engine but never disables those canaries.
Every string of lengths 0 through N over ALPHABET is generated, without sampling.
For a resumed suffix, --start-index requires retaining and adding the preceding prefix counts;
the printed counts cover only the selected suffix.

Glob sources use case "$1" in *[...]*), with globasciiranges disabled. Bash eval
parses each independent function definition. Every accepted definition is also sent
unchanged to a separate bash -n process; its successful exit is mandatory before
counting that batch. This batches syntax checks without approximating Bash's parser.
Arithmetic-expansion failures are excluded from parsed counts.
Each accepted function runs against é under C and the selected UTF-8 locale.

grep and regex use the bare bracket text literally, without shell quote removal.
grep splits literal newlines into pattern alternatives, wrapping each fragment as
^ID:.*(fragment).*$ against ID:é lines so IDs cannot cross-match. Invalid fragments reject
their whole candidate. Indexed diagnostics map back to candidate IDs; unindexed diagnostics
are bisected and confirmed with a direct unwrapped grep invocation, separately per locale.
regex passes the same literal text through a shell
variable to [[ $1 =~ $re ]]. Their parsed count includes only patterns valid in both
locales. Regression fixtures separately cover shell quote removal in assignments.

Each live candidate is written to a real fenced bash block and scanned with scan_path.
Regex engines scan both a shell-quoted literal assignment and, for multiline patterns,
a quoted heredoc body. Source glob candidates retain their
original physical newlines and continuations. The alphabet preserves the original 12
characters and adds newline, [, :, = and ., for 17 distinct characters.
--multiline-length N also inserts every word of lengths 0 through N over that same alphabet,
including $ and backslash, into seven fixed multiline scaffolds. These reach ANSI-C escaped
quotes, mixed quotes, and leading literal closes on the first physical line. A live pattern
is flagged only if every source form is detected. Resume indices include both families.

A live pattern's match result for é differs between C and UTF-8 in either direction.
This predicate also includes locale effects beyond ranges, such as byte-versus-character
matching by a dot following a negated set. "flagged" counts live patterns the
gate flags; all misses are printed as JSON, and any miss fails the run.
Zero live candidates on any engine also fail unless --allow-empty was explicit. Results are
bounded evidence for this alphabet and length, not proof for arbitrary Bash.
"""
import argparse
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import itertools
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile

from check_bracket_ranges import scan_path

ALPHABET = '\'"\\]^!az-x$ \n[:=.'
SAMPLE = "é"


def shell(script, locale="C"):
    return subprocess.run(
        ["bash", "--noprofile", "--norc"], input=script, text=True,
        capture_output=True, env={"PATH": os.environ["PATH"], "LC_ALL": locale},
        check=False,
    )


def glob_batch(words, locale):
    lines = [
        "shopt -u globasciiranges; parsed=0",
        "exec 3> >(bash --noprofile --norc -n); checker=$!",
        'check() { src=$2; if eval "$src" 2>/dev/null; then '
        'printf "%s\\n" "$src" >&3; '
        'LC_ALL=C; probe é 2>/dev/null; c=$?; LC_ALL=' + shlex.quote(locale)
        + '; probe é 2>/dev/null; u=$?; if ((c<2 && u<2)); then ((parsed+=1)); '
        'if ((u!=c)); then echo L "$1"; fi; fi; fi; }',
    ]
    for index, word in enumerate(words):
        source = ('probe() { case "$1" in *[' + word
                  + ']*) return 0;; *) return 1;; esac; }')
        lines.append(f"check {index} " + shlex.quote(source))
    lines += ['exec 3>&-', 'wait "$checker" || exit 3', 'echo P "$parsed"']
    return bash_results(shell("\n".join(lines)), "glob")


def bash_results(result, engine):
    if result.returncode or result.stderr:
        raise RuntimeError((engine, result.returncode, result.stderr))
    live, parsed = set(), None
    for line in result.stdout.splitlines():
        tag, value = line.split()
        if tag == "L":
            live.add(int(value))
        elif tag == "P":
            parsed = int(value)
        else:
            raise RuntimeError(("unexpected bash output", line))
    if parsed is None:
        raise RuntimeError("missing bash parsed count")
    return parsed, live


def regex_batch(words, locale):
    lines = [
        "parsed=0",
        'check() { re=$2; LC_ALL=C; [[ é =~ $re ]] 2>/dev/null; c=$?; LC_ALL='
        + shlex.quote(locale) + '; [[ é =~ $re ]] 2>/dev/null; u=$?; '
        'if ((c<2 && u<2)); then ((parsed+=1)); '
        'if ((u!=c)); then echo L "$1"; fi; fi; }',
    ]
    for index, word in enumerate(words):
        lines.append(f"check {index} " + shlex.quote("[" + word + "]"))
    lines.append('echo P "$parsed"')
    return bash_results(shell("\n".join(lines)), "regex")


def grep_locale(words, locale, directory):
    active = list(range(len(words)))
    path = directory / "patterns"
    data = "".join(f"{i}:{SAMPLE}\n" for i in active)
    while active:
        # grep treats a newline as a pattern separator. Wrap every fragment with its
        # candidate ID, and map diagnostics back to the owner of that physical line.
        fragments = [(i, part) for i in active for part in ("[" + words[i] + "]").split("\n")]
        path.write_text("".join(f"^{i}:.*({part}).*$\n" for i, part in fragments),
                        encoding="utf-8")
        result = subprocess.run(
            ["grep", "-E", "-f", str(path)], input=data, text=True,
            capture_output=True,
            env={"PATH": os.environ["PATH"], "LC_ALL": locale},
            check=False,
        )
        if result.returncode in (0, 1):
            if result.stderr:
                raise RuntimeError(("grep warning", result.stderr))
            matches = {int(line.split(":", 1)[0]) for line in result.stdout.splitlines()}
            return set(active), matches
        # GNU grep identifies every rejected expression by its pattern-file line.
        bad, unindexed = set(), False
        prefix = "grep: " + str(path) + ":"
        for line in result.stderr.splitlines():
            if not line.startswith(prefix):
                unindexed = True
                continue
            number, separator, _ = line[len(prefix):].partition(":")
            if not separator or not number.isdecimal():
                raise RuntimeError(("unindexed grep error", line))
            position = int(number) - 1
            if not 0 <= position < len(fragments):
                raise RuntimeError(("bad grep error index", line))
            bad.add(fragments[position][0])
        if not bad:
            if not unindexed or result.returncode != 2:
                raise RuntimeError(("grep failed without indexed errors", result.stderr))
            if len(active) == 1:
                # Confirm the rejected candidate with the unwrapped, direct oracle.
                direct = subprocess.run(
                    ["grep", "-E", "--", "[" + words[active[0]] + "]"],
                    input=SAMPLE + "\n", text=True, capture_output=True,
                    env={"PATH": os.environ["PATH"], "LC_ALL": locale}, check=False)
                if direct.returncode != 2:
                    raise RuntimeError(("inconsistent grep rejection", direct))
                return set(), set()
            # Some GNU grep diagnostics omit line numbers (for example [:x:]).
            # Bisect to attribute those failures without dropping valid neighbours.
            valid, matches = set(), set()
            middle = len(active) // 2
            for group in (active[:middle], active[middle:]):
                good, hit = grep_locale([words[i] for i in group], locale, directory)
                valid.update(group[i] for i in good)
                matches.update(group[i] for i in hit)
            return valid, matches
        if not bad.intersection(active):
            raise RuntimeError(("grep diagnostics removed no candidate", result.stderr))
        active = [value for value in active if value not in bad]
    return set(), set()


def _grep_batch(words, locale):
    with tempfile.TemporaryDirectory(prefix="bracket-fuzz-") as directory:
        c_valid, c_matches = grep_locale(words, "C", Path(directory))
        u_valid, u_matches = grep_locale(words, locale, Path(directory))
    valid = c_valid & u_valid
    return len(valid), (u_matches ^ c_matches) & valid


def grep_batch(words, locale):
    # ID-prefixed DFA construction grows steeply with batch size. Bound it independently
    # of the Bash batch, keeping every candidate and the same direct grep comparisons.
    parsed, live = 0, set()
    for offset in range(0, len(words), 128):
        count, matches = _grep_batch(words[offset:offset + 128], locale)
        parsed += count
        live.update(offset + index for index in matches)
    return parsed, live


def candidate_sources(pattern, engine):
    """Scan the source spelling that the oracle evaluates, including literal heredocs."""
    if engine == "glob":
        return ['case "$1" in *' + pattern + '*) :;; esac']
    sources = ["re=" + shlex.quote(pattern)]
    if "\n" in pattern:
        sources.append("re=$(cat <<'BRACKET_FUZZ_EOF'\n" + pattern
                       + "\nBRACKET_FUZZ_EOF\n)")
    return sources


def multiline_words(word):
    """Long quote and leading-close scaffolds with an exhaustively varied insertion."""
    return (
        "!$'x]y\\'" + word + "\n'a-z",
        "!'a\"b'\"x]y" + word + "\n\"a-z",
        "^]a\"\"''" + word + "\n-z",
        "]a\"\"''" + word + "\n-z",
        "!]a" + word + "\n-z",
        "]a" + word + "\n-z",
        "^]a" + word + "\n-z",
    )


def check_batch(words, locale, engines):
    results = {}
    for engine in engines:
        parsed, live = {"glob": glob_batch, "grep": grep_batch,
                        "regex": regex_batch}[engine](words, locale)
        missed = []
        with tempfile.TemporaryDirectory(prefix="bracket-scan-") as directory:
            path = Path(directory) / "candidate.md"
            for index in sorted(live):
                pattern = "[" + words[index] + "]"
                missed_source = False
                for source in candidate_sources(pattern, engine):
                    path.write_text("```bash\n" + source + "\n```\n", encoding="utf-8")
                    if not scan_path(path)[0]:
                        missed_source = True
                if missed_source:
                    missed.append(pattern)
        results[engine] = dict(generated=len(words), parsed=parsed, live=len(live),
                               flagged=len(live) - len(missed), missed=missed)
    return results


def batches(max_length, size, skip=0):
    for length in range(max_length + 1):
        count = len(ALPHABET) ** length
        if skip >= count:
            skip -= count
            continue
        source = itertools.islice(itertools.product(ALPHABET, repeat=length), skip, None)
        skip = 0
        while words := list(itertools.islice(source, size)):
            yield ["".join(word) for word in words]


def selected_batches(max_length, multiline_length, size, skip=0):
    """Resume over one stable order: ordinary candidates, then multiline scaffolds."""
    ordinary = sum(len(ALPHABET) ** n for n in range(max_length + 1))
    if skip < ordinary:
        yield from batches(max_length, size, skip)
    skip = max(0, skip - ordinary)
    if multiline_length is not None:
        words = (candidate for batch in batches(multiline_length, size)
                 for word in batch for candidate in multiline_words(word))
        words = itertools.islice(words, skip, None)
        while batch := list(itertools.islice(words, size)):
            yield batch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-length", type=int, default=6)
    parser.add_argument("--multiline-length", type=int,
                        help="also insert lengths 0 through N into seven multiline scaffolds")
    parser.add_argument("--start-index", type=int, default=0,
                        help="resume a contiguous suffix; add the preceding prefix counts")
    parser.add_argument("--batch-size", type=int, default=4096)
    parser.add_argument("--jobs", type=int, default=16)
    parser.add_argument("--locale", default="en_US.utf8")
    parser.add_argument("--engines", nargs="+", choices=("glob", "grep", "regex"),
                        default=["glob", "grep", "regex"])
    parser.add_argument("--allow-empty", action="store_true",
                        help="allow a selected suffix with zero live candidates on an engine")
    args = parser.parse_args()
    if (args.max_length < 0 or args.jobs < 1 or args.batch_size < 1
            or (args.multiline_length is not None and args.multiline_length < 0)):
        parser.error("length must be nonnegative; jobs and batch size must be positive")
    # No vacuous all-green result when the available UTF-8 locale collates like C.
    for engine in args.engines:
        samples = ["a-z", "!a-z" if engine == "glob" else "^a-z"]
        result = check_batch(samples, args.locale, [engine])[engine]
        if (result["parsed"] != 2 or result["live"] != 2
                or result["flagged"] != 2 or result["missed"]):
            parser.error(f"{engine}: locale {args.locale!r} failed the bidirectional live/detection canary")
        control = check_batch(["^a"], args.locale, [engine])[engine]
        if control["parsed"] != 1 or control["live"] != 0:
            parser.error(f"{engine}: bare negated-set canary changed matching semantics")
    totals = {engine: dict(generated=0, parsed=0, live=0, flagged=0, missed=0)
              for engine in args.engines}
    expected = sum(len(ALPHABET) ** n for n in range(args.max_length + 1))
    if args.multiline_length is not None:
        expected += 7 * sum(len(ALPHABET) ** n for n in range(args.multiline_length + 1))
    if not 0 <= args.start_index < expected:
        parser.error("start index must identify a generated candidate")
    source = iter(selected_batches(args.max_length, args.multiline_length,
                                   args.batch_size, args.start_index))
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        pending = deque()
        for _ in range(2 * args.jobs):
            if (words := next(source, None)) is not None:
                pending.append(pool.submit(check_batch, words, args.locale, args.engines))
        completed = 0
        while pending:
            results = pending.popleft().result()
            for engine, result in results.items():
                for pattern in result["missed"]:
                    print(json.dumps(dict(engine=engine, missed=pattern)), flush=True)
                for field in ("generated", "parsed", "live", "flagged"):
                    totals[engine][field] += result[field]
                totals[engine]["missed"] += len(result["missed"])
            completed += 1
            if completed % 100 == 0:
                print(json.dumps(dict(progress=totals)), flush=True)
            if (words := next(source, None)) is not None:
                pending.append(pool.submit(check_batch, words, args.locale, args.engines))
    expected -= args.start_index
    assert all(result["generated"] == expected for result in totals.values()), totals
    print(json.dumps(dict(locale=args.locale, max_length=args.max_length,
                          start_index=args.start_index, alphabet=ALPHABET,
                          multiline_length=args.multiline_length,
                          allow_empty=args.allow_empty, results=totals)), flush=True)
    empty = [engine for engine, result in totals.items() if result["live"] == 0]
    if empty and not args.allow_empty:
        print("zero live candidates: " + ", ".join(empty) + "; use --allow-empty to opt in",
              flush=True)
    return int(any(result["missed"] for result in totals.values())
               or (bool(empty) and not args.allow_empty))


if __name__ == "__main__":
    raise SystemExit(main())
