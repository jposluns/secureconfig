#!/usr/bin/env python3
"""Gate: `ss` listener probes in a guide Verify block must be UNFILTERED.

WHAT THIS CATCHES
  SS-GREP-FILTER  a fenced shell command that pipes `ss` into `grep`, i.e. the
                  filtered-listener form `ss ... | grep ...` (short flags, long
                  flags, or none; `sudo ss`, `sudo -n ss`, `timeout 5 ss`,
                  `ss -xlp | grep`, `grep -E`, a `|&` pipe, and pipelines
                  continued after a bare `|` or a backslash). The corpus reads
                  the WHOLE listener table (apache.md/traefik.md document this)
                  rather than grepping to the port a reader expects: a filter
                  cannot reveal a listener on an UNEXPECTED port, and
                  `grep ':(80|443)'` also matches an IPv6 address like
                  `[2001:db8:80::1]:9000`. Fixed guide-by-guide in #113 (rows
                  1.28/1.29), swept corpus-wide in #138 (row 1.74); this gate
                  keeps it from regressing (zero instances at landing).

  Detection uses a small type-aware shell lexer (_lex) that tracks single/double
  quotes ACROSS physical lines, backslash escapes, `#` comments (ended at the
  newline), `$(...)`/backtick command substitutions (kept opaque inside their
  word), redirection operators with their targets, here-doc bodies (skipped as
  data, with the full delimiter grammar: quoted/`<<-`/multiple-per-line/exact
  terminator), and the control operators `| || |& && ; ;; & ( )`. Only a WORD
  token equal to `ss` and a WORD token equal to `grep` that are the command words
  of two commands joined by a real `|`/`|&` produce a finding. A `|` inside a
  `case` pattern list (`ss|grep)`) is alternation, not a pipeline, and is not
  flagged. Because quotes/comments/heredocs are lexed, a quoted or commented
  mention -- even spanning lines -- does not trip the gate.

WHAT THIS IS NOT
  Not a claim that an unfiltered `ss` proves anything (that is the reader's job
  with the whole table in view), and not a full shell parser. A pass is a
  tripwire, not a guarantee.

SCOPE
  Top-level guides only; the roster excludes records that merely quote the old
  pattern (CHANGELOG/DONE/TODO/DECISIONS/PENDING-DECISIONS) and the adapter/meta
  files, and directories are not descended. Fenced blocks come from
  tools/_markdown.py (blockquote markers stripped; four-space-indented fences are
  not fences). bash/sh/shell/zsh and console/terminal fences are scanned; in a
  console fence only `$ `-prefixed command lines (whitespace after `$` required)
  are read, with `> ` continuation folded in.

KNOWN REMAINING BYPASSES (disclosed, matching the sibling probe/guard gates). The
lexer handles the constructs a real Verify block uses; the residue below is exotic
shell grammar that does not occur in these guides. Any surprise false positive is
suppressed with a `# unfiltered-ss: allow <reason>` comment on or above the line.
  FALSE NEGATIVES (a real `ss | grep` missed; acceptable, like the sibling gates):
  - a pipeline hidden inside a command substitution (`x="$(ss -tlnp | grep 443)"`);
    inside a brace group (`{ ss -tlnp | grep 443; }`); or reached through a
    variable, alias, shell function, eval, xargs, or process substitution.
  - a wrapper option that TAKES a value hides the command word: `sudo -u root ss
    ... | grep` reads `root` (`sudo ss`, `sudo -n ss`, `timeout 5 ss` ARE resolved).
  - a `> `-continued console command; a fence with no language tag or a non-shell
    tag; a line the lexer cannot resolve (counted and skipped, never crashed).
  FALSE POSITIVES that need a waiver if they ever occur (the literal text `ss ...
  | grep` sitting as DATA inside an exotic construct the lexer does not model):
  - ANSI-C quoting `$'...'`; arithmetic expansion `$((...))` / arithmetic command
    `((...))`; parameter-expansion default text `${x:-...}`; a `$(...)` nested
    inside double quotes that itself contains double quotes; here-doc delimiters
    with punctuation/whitespace/concatenated quoting; the literal words `case`/`in`
    used as ordinary arguments toggling case-pattern state. None appear in the
    corpus (it scans clean); each is waivable.

EXIT/OUTPUT DISCIPLINE (run_all_checks.sh relies on this)
  Findings print one per line:  path:line: [SS-GREP-FILTER] message
  A gate-result line always prints:
      GATE unfiltered-ss: PASS ...     (exit 0)
      GATE unfiltered-ss: FAIL ...     (exit 1)
  --self-test prints GATE unfiltered-ss-selftest: PASS/FAIL and exits 0/1.
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _markdown import Fences, FENCE_RE  # noqa: E402

GATE = "unfiltered-ss"
NOT_A_GUIDE = frozenset((
    "CONTRIBUTING.md", "CLAUDE.md", "AGENTS.md", "CHANGELOG.md",
    "README.sources.md", "DONE.md", "TODO.md", "DECISIONS.md",
    "PENDING-DECISIONS.md", "SECURITY.md"))
SHELL_INFOS = frozenset(("bash", "sh", "shell", "zsh"))
CONSOLE_INFOS = frozenset(("console", "terminal"))
_BLOCKQUOTE_RE = re.compile(r"^ {0,3}(?:>[ \t]{0,3})+")
WRAPPERS = frozenset((
    "sudo", "doas", "command", "env", "nohup", "nice", "ionice", "timeout",
    "stdbuf"))
KEYWORDS = frozenset((
    "if", "then", "elif", "else", "fi", "while", "until", "do", "done",
    "!", "time"))
DURATION_RE = re.compile(r"^\d[\d.]*[smhd]?$")
ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\+?=")
MESSAGE = ("`ss ... | grep` filters the listener table; read the whole table "
           "unfiltered (a filter hides a listener on an unexpected port, and a "
           "port grep also matches an IPv6 address). See #138 / row 1.74. If this "
           "is a false positive on an exotic shell construct, waive it with a "
           "`# unfiltered-ss: allow <reason>` comment on or above the line.")
WAIVER_RE = re.compile(r"#\s*unfiltered-ss:\s*allow\s+\S")


def _waived_lines(text):
    """File line numbers a `# unfiltered-ss: allow <reason>` comment suppresses:
    the waiver's own line and the line immediately after it (the command it
    guards). The escape-hatch for the disclosed exotic-construct false positives,
    mirroring the sibling guard gate's waiver."""
    waived = set()
    for i, line in enumerate(text.splitlines(), 1):
        if WAIVER_RE.search(line):
            waived.add(i)
            waived.add(i + 1)
    return waived

# token kinds
WORD, OP, NL, REDIR = "WORD", "OP", "NL", "REDIR"


def _lang_of(info):
    return info.strip().split()[0].lower() if info.strip() else ""


def _blocks(text):
    fences = Fences()
    bq = False
    info, start, body = "", None, []
    for i, raw in enumerate(text.splitlines(), 1):
        line, marked = raw, False
        m = _BLOCKQUOTE_RE.match(raw)
        if m and (not fences.inside or bq):
            line, marked = raw[m.end():], True
        if fences.inside and bq and not marked and raw.strip():
            fences.close()
            bq = False
            if start is not None:
                yield _lang_of(info), start, body
            info, start, body = "", None, []
        was_inside = fences.inside
        if fences.feed(line):
            if not was_inside:
                bq = marked
                mm = FENCE_RE.match(line)
                info = mm.group(2) if mm else ""
                start, body = i + 1, []
            else:
                if start is not None:
                    yield _lang_of(info), start, body
                info, start, body = "", None, []
            continue
        if fences.inside:
            body.append(line)
    if fences.inside and start is not None:
        yield _lang_of(info), start, body


class LexError(Exception):
    pass


def _heredoc_delims(line):
    """Delimiters opened on a logical line, in order, as (delim, strip_tabs).
    Scans quote/escape state so a `<<EOF` inside quotes or after a `#` comment is
    not treated as an opener. Recognizes `<<` and `<<-`, an optional quote around
    the delimiter, and a leading `\\` before it (all quote the body verbatim)."""
    delims = []
    i, n = 0, len(line)
    sq = dq = False
    while i < n:
        c = line[i]
        if c == "\\" and not sq:
            i += 2
            continue
        if c == "'" and not dq:
            sq = not sq
            i += 1
            continue
        if c == '"' and not sq:
            dq = not dq
            i += 1
            continue
        if c == "#" and not sq and not dq and (i == 0 or line[i - 1].isspace()):
            break
        if not sq and not dq and c == "<" and line[i + 1:i + 2] == "<":
            j = i + 2
            strip = False
            if line[j:j + 1] == "-":
                strip = True
                j += 1
            while j < n and line[j] in " \t":
                j += 1
            # a here-string `<<<` is not a here-doc
            if line[i + 2:i + 3] == "<":
                i += 3
                continue
            q = ""
            if j < n and line[j] in "'\"":
                q = line[j]
                j += 1
            k = j
            if line[k:k + 1] == "\\":
                k += 1
                j = k
            while k < n and (line[k].isalnum() or line[k] in "_-.+"):
                k += 1
            word = line[j:k]
            if q:
                if line[k:k + 1] == q:
                    k += 1
                else:
                    word = line[j:k]  # tolerate a missing close quote
            if word:
                delims.append((word, strip))
            i = k
            continue
        i += 1
    return delims


def _lex(body):
    """Lex a fence body (list of physical lines) into tokens carrying the 1-based
    body-relative line number of their start. Quotes span physical lines;
    comments end at the newline; here-doc bodies are consumed as data;
    `$(...)`/backticks are kept opaque inside a WORD; redirection operators and
    their targets are emitted so the command word is found past them. Raises
    LexError on an unterminated quote."""
    toks = []
    li, n = 0, len(body)
    heredocs = []  # queued (delim, strip_tabs) whose bodies follow the next NL
    while li < n:
        line = body[li]
        i, L = 0, len(line)
        cur, cur_line = [], None

        def flush():
            if cur:
                toks.append((WORD, cur_line, "".join(cur)))
                cur[:] = []

        while i < L:
            c = line[i]
            if c == "\\":
                if i + 1 < L:
                    if cur_line is None:
                        cur_line = li + 1
                    cur.append(line[i:i + 2])
                    i += 2
                    continue
                # trailing backslash: line continuation (join next physical line)
                if li + 1 < n:
                    line = line[:i] + body[li + 1]
                    L = len(line)
                    li += 1
                    continue
                i += 1
                continue
            if c == "'":
                if cur_line is None:
                    cur_line = li + 1
                cur.append(c)
                i += 1
                while True:
                    j = line.find("'", i)
                    if j >= 0:
                        cur.append(line[i:j + 1])
                        i = j + 1
                        break
                    # quote spans to next physical line
                    cur.append(line[i:])
                    if li + 1 >= n:
                        raise LexError("unterminated single quote")
                    li += 1
                    line = body[li]
                    L = len(line)
                    cur.append("\n")
                    i = 0
                continue
            if c == '"':
                if cur_line is None:
                    cur_line = li + 1
                cur.append(c)
                i += 1
                while True:
                    closed = False
                    while i < L:
                        if line[i] == "\\" and i + 1 < L:
                            cur.append(line[i:i + 2])
                            i += 2
                            continue
                        if line[i] == '"':
                            cur.append('"')
                            i += 1
                            closed = True
                            break
                        cur.append(line[i])
                        i += 1
                    if closed:
                        break
                    if li + 1 >= n:
                        raise LexError("unterminated double quote")
                    li += 1
                    line = body[li]
                    L = len(line)
                    cur.append("\n")
                    i = 0
                continue
            if c == "`":
                if cur_line is None:
                    cur_line = li + 1
                cur.append(c)
                i += 1
                while True:
                    j = line.find("`", i)
                    if j >= 0:
                        cur.append(line[i:j + 1])
                        i = j + 1
                        break
                    cur.append(line[i:])
                    if li + 1 >= n:
                        raise LexError("unterminated backtick")
                    li += 1
                    line = body[li]
                    L = len(line)
                    cur.append("\n")
                    i = 0
                continue
            if c == "$" and line[i:i + 2] == "$(":
                if cur_line is None:
                    cur_line = li + 1
                depth = 0
                while i < L:
                    if line[i] == "(":
                        depth += 1
                    elif line[i] == ")":
                        depth -= 1
                        if depth == 0:
                            cur.append(line[i])
                            i += 1
                            break
                    cur.append(line[i])
                    i += 1
                else:
                    # unbalanced $(...): treat rest as opaque word text
                    pass
                continue
            if c == "#" and (i == 0 or line[i - 1] in " \t;&|()<>"):
                break  # comment to end of physical line (word boundary incl. ops)
            # redirection operators (optional leading fd; not the << here-doc)
            mred = re.match(r"\d*(?:>>|>&|>\||>|<&|<)|&>>|&>", line[i:])
            if mred and not (line[i:i + 2] == "<<"):
                flush()
                toks.append((REDIR, li + 1, mred.group(0)))
                i += mred.end()
                continue
            two = line[i:i + 2]
            if two in ("||", "&&", ";;", "|&"):
                flush()
                toks.append((OP, li + 1, two))
                i += 2
                continue
            if c == "<" and line[i + 1:i + 2] == "<":
                # here-doc operator: consumed via _heredoc_delims; emit nothing,
                # skip the operator+delim token text here.
                flush()
                # advance past `<<[-][q]delim[q]`
                mm = re.match(r"<<-?\s*(['\"]?)\\?[A-Za-z0-9_.+-]+\1", line[i:])
                i += mm.end() if mm else 2
                continue
            if c in "|;&()":
                flush()
                toks.append((OP, li + 1, c))
                i += 1
                continue
            if c in " \t":
                flush()
                i += 1
                continue
            if cur_line is None:
                cur_line = li + 1
            cur.append(c)
            i += 1
        flush()
        # end of this logical line
        toks.append((NL, li + 1, ""))
        for d, strip in _heredoc_delims(line):
            heredocs.append((d, strip))
        li += 1
        # consume queued here-doc bodies
        while heredocs and li < n:
            delim, strip = heredocs[0]
            cand = body[li].lstrip("\t") if strip else body[li]
            li += 1
            if cand == delim:
                heredocs.pop(0)
    return toks


def _cmd_word(seg):
    """Command word (basename) of a list of WORD/REDIR tokens, or None. Skips
    redirections+targets, env-assignments, shell keywords, and wrappers with
    their options (`command -v/-V` is a query, not a run)."""
    i = 0
    while i < len(seg):
        kind, val = seg[i]
        if kind == REDIR:
            # a redirection is followed by its target WORD (`2>` `/dev/null`,
            # `2>&` `1`); skip both so the target never reads as the command word.
            i += 2 if (i + 1 < len(seg) and seg[i + 1][0] == WORD) else 1
            continue
        if ASSIGNMENT_RE.match(val) or val in KEYWORDS:
            i += 1
            continue
        base = val.rsplit("/", 1)[-1]
        if base in WRAPPERS:
            i += 1
            query = False
            while i < len(seg) and seg[i][0] == WORD and \
                    seg[i][1].startswith("-") and seg[i][1] != "--":
                if base == "command" and ("v" in seg[i][1] or "V" in seg[i][1]):
                    query = True
                i += 1
            if query:
                return None
            if i < len(seg) and seg[i][0] == WORD and seg[i][1] == "--":
                i += 1
            if base == "timeout" and i < len(seg) and seg[i][0] == WORD \
                    and DURATION_RE.match(seg[i][1]):
                i += 1
            continue
        return base
    return None


def _scan_tokens(toks, path, findings):
    """Walk tokens, building commands split on control operators, and flag a
    command word `ss` joined by a real pipe to the next command word `grep`.
    A `|` inside a `case` pattern list is alternation, not a pipeline."""
    seg = []            # current command's (kind, val) tokens
    seg_line = 0        # 1-based line of the current command's first token
    prev_word = None    # command word of the previous command in this pipeline
    prev_pipe = False   # was the previous command terminated by a real pipe?
    case_depth = 0
    expect_in = 0       # = case_depth after `case`, until its `in`
    in_pattern = False  # inside a case pattern list, before its `)`

    def close():
        nonlocal prev_word, seg, seg_line
        word = _cmd_word(seg)
        if prev_pipe and prev_word == "ss" and word == "grep":
            findings.append((path, seg_line))
        prev_word = word
        seg = []
        seg_line = 0

    for kind, lineno, val in toks:
        if kind in (WORD, REDIR):
            if not seg:
                seg_line = lineno
            if kind == WORD:
                if val == "case":
                    case_depth += 1
                    expect_in = case_depth
                elif val == "in" and case_depth and expect_in == case_depth:
                    in_pattern = True
                    expect_in = 0
                elif val == "esac" and case_depth:
                    case_depth -= 1
                    in_pattern = False
            seg.append((kind, val))
            continue
        # a newline right after a trailing pipe continues the pipeline
        if kind == NL and not seg and prev_pipe:
            continue
        # kind is OP or NL: the current command ends here
        if kind == OP and val == ")" and case_depth and in_pattern:
            in_pattern = False   # end of the pattern list; its body follows
            seg = []
            seg_line = 0
            prev_word, prev_pipe = None, False
            continue
        close()
        prev_pipe = (kind == OP and val in ("|", "|&") and not in_pattern)
        if kind == OP and val == ";;" and case_depth:
            in_pattern = True    # the next pattern list begins


def _command_pairs(lang, body, start):
    if lang not in CONSOLE_INFOS:
        return list(body), start
    out, i = [], 0
    while i < len(body):
        m = re.match(r"^\s*\$\s(.*)$", body[i])
        if m:
            cmd = m.group(1)
            # fold `> ` prompt continuations into subsequent physical lines? keep
            # them as separate body lines so line numbers stay meaningful; the
            # lexer treats a trailing backslash as continuation.
            out.append((start + i, cmd))
        i += 1
    return out, None


def scan_text(path, text, findings, stats):
    for lang, start, body in _blocks(text):
        if lang not in SHELL_INFOS and lang not in CONSOLE_INFOS:
            continue
        stats["fences"] += 1
        if lang in CONSOLE_INFOS:
            pairs, _ = _command_pairs(lang, body, start)
            # lex each console command independently (its own line number)
            for lineno, cmd in pairs:
                stats["lines"] += 1
                try:
                    toks = _lex([cmd])
                except LexError:
                    stats["unparseable"] += 1
                    continue
                _scan_line_tokens(toks, path, lineno, findings)
        else:
            try:
                toks = _lex(list(body))
            except LexError:
                stats["unparseable"] += 1
                continue
            # count logical command lines for the scope stat
            stats["lines"] += sum(1 for t in toks if t[0] == NL)
            _scan_offset_tokens(toks, path, start - 1, findings)


def _scan_offset_tokens(toks, path, line_offset, findings):
    adj = [(k, (ln + line_offset) if ln else ln, v) for (k, ln, v) in toks]
    _scan_tokens(adj, path, findings)


def _scan_line_tokens(toks, path, lineno, findings):
    adj = [(k, lineno, v) for (k, ln, v) in toks]
    _scan_tokens(adj, path, findings)


def iter_md_files(roots):
    files = []
    for root in roots:
        if os.path.isfile(root):
            files.append(root)
            continue
        for fn in sorted(os.listdir(root)):
            path = os.path.join(root, fn)
            if (os.path.isfile(path) and fn.lower().endswith(".md")
                    and fn not in NOT_A_GUIDE):
                files.append(path)
    return sorted(set(files))


def run_scan(opts):
    findings = []
    stats = {"files": 0, "fences": 0, "lines": 0, "unparseable": 0}
    for path in iter_md_files(opts.roots):
        stats["files"] += 1
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        local = []
        scan_text(path, text, local, stats)
        waived = _waived_lines(text)
        findings.extend(f for f in local if f[1] not in waived)
    # dedupe (a line can only be reported once)
    findings = sorted(set(findings))
    for path, lineno in findings:
        print("%s:%d: [SS-GREP-FILTER] %s" % (path, lineno, MESSAGE))
    print("checked %d file(s), %d shell fence(s), %d command line(s); "
          "%d unparseable line(s) skipped"
          % (stats["files"], stats["fences"], stats["lines"],
             stats["unparseable"]))
    if findings:
        print("GATE %s: FAIL -- %d finding(s)" % (GATE, len(findings)))
        return 1
    print("GATE %s: PASS" % GATE)
    return 0


SELF_TEST_CASES = [
    # -- the anti-pattern, various forms (expect 1) --
    ("filtered-flagged", "```bash\nss -tlnp | grep 11211\n```\n", 1),
    ("filtered-sudo-flagged", "```bash\nsudo ss -tuln | grep :443\n```\n", 1),
    ("filtered-sudo-n-flagged", "```bash\nsudo -n ss -tlnp | grep 443\n```\n", 1),
    ("filtered-timeout-flagged",
     "```bash\ntimeout 5 ss -tlnp | grep 443\n```\n", 1),
    ("filtered-egrep-flagged", "```bash\nss -tlnp | grep -E ':(80|443)'\n```\n", 1),
    ("filtered-noflags-flagged", "```bash\nss | grep 443\n```\n", 1),
    ("filtered-longflags-flagged",
     "```bash\nss --listening --tcp --numeric | grep 443\n```\n", 1),
    ("filtered-if-prefix-flagged",
     "```bash\nif ss -tlnp | grep -q 443; then echo found; fi\n```\n", 1),
    ("filtered-continuation-flagged",
     "```bash\nss -tlnp | \\\n  grep 443\n```\n", 1),
    ("filtered-dangling-pipe-flagged",
     "```bash\nss -tlnp |\n  grep 443\n```\n", 1),
    ("filtered-pipe-amp-flagged", "```bash\nss -tlnp |& grep 443\n```\n", 1),
    ("filtered-stderr-redir-flagged",
     "```bash\nss -tlnp 2>&1 | grep 443\n```\n", 1),
    ("filtered-stderr-redir2-flagged",
     "```bash\nss -tlnp 2>>errors.log | grep 443\n```\n", 1),
    ("filtered-cmdsub-arg-flagged",
     "```bash\nss -tlnp $(printf '') | grep 443\n```\n", 1),
    ("ss-x-socket-grep-flagged", "```bash\nss -xlp | grep admin.sock\n```\n", 1),
    ("console-fence-flagged", "```console\n$ ss -tlnp | grep 6379\n```\n", 1),
    ("blockquoted-fence-flagged",
     "> ```bash\n> ss -tlnp | grep 443\n> ```\n", 1),
    ("real-after-heredoc-flagged",
     "```bash\ncat <<'EOF'\nnoise\nEOF\nss -tlnp | grep 443\n```\n", 1),
    ("real-after-quoted-block-flagged",
     "```bash\nprintf '%s\\n' 'a\nb'\nss -tlnp | grep 443\n```\n", 1),
    # -- must NOT flag (false-positive guards) (expect 0) --
    ("unfiltered-clean",
     "```bash\nss -tlnp   # read every listener; 3000 on 127.0.0.1 only\n```\n", 0),
    ("ss-no-grep-clean", "```bash\nss -tlnp\n```\n", 0),
    ("other-grep-clean", "```bash\nps aux | grep caddy\n```\n", 0),
    ("semicolon-not-a-pipeline-clean",
     "```bash\nss -tlnp; ps aux | grep caddy\n```\n", 0),
    ("logical-or-not-a-pipe-clean",
     "```bash\nss -tlnp || grep 443 /dev/null\n```\n", 0),
    ("quoted-mention-not-flagged",
     "```bash\nprintf '%s\\n' 'avoid sudo ss -tlnp | grep 443'\n```\n", 0),
    ("quoted-operators-not-flagged",
     "```bash\nprintf '%s\\n' ';' ss '|' grep 443\n```\n", 0),
    ("multiline-quoted-text-not-flagged",
     "```bash\nprintf '%s\\n' 'Avoid:\nss -tlnp | grep 443\n'\n```\n", 0),
    ("nested-quoted-cmdsub-not-flagged",
     "```bash\nprintf '%s\\n' \"$(printf '%s\\n' \\\"x; ss -tlnp | grep 443;\\\")\"\n```\n", 0),
    ("escaped-pipe-not-flagged", "```bash\nss -tlnp \\| grep 443\n```\n", 0),
    ("command-v-not-flagged", "```bash\ncommand -v ss | grep ss\n```\n", 0),
    ("case-pattern-not-flagged",
     "```bash\ncase \"$tool\" in\n  ss|grep) command -v \"$tool\" ;;\nesac\n```\n", 0),
    ("comment-line-not-flagged",
     "```bash\n# never write ss -tlnp | grep 443; read the whole table\n```\n", 0),
    ("inline-comment-mentioning-pattern-not-flagged",
     "```bash\nss -tlnp   # not ss -tlnp | grep 443\n```\n", 0),
    ("comment-after-semicolon-not-flagged",
     "```bash\nss -tlnp;# avoid | grep 443\n```\n", 0),
    ("heredoc-literal-not-flagged",
     "```bash\ncat <<'EOF'\nss -tlnp | grep 443\nEOF\n```\n", 0),
    ("heredoc-hyphen-delim-not-flagged",
     "```bash\ncat <<-END_T\n\tss -tlnp | grep 443\n\tEND_T\n```\n", 0),
    ("heredoc-two-on-one-cmd-not-flagged",
     "```bash\ncat <<FIRST <<SECOND\nx\nFIRST\nss -tlnp | grep 443\nSECOND\n```\n", 0),
    ("heredoc-trailing-space-terminator-not-early-closed",
     "```bash\ncat <<EOF\nEOF \nss -tlnp | grep 443\nEOF\n```\n", 0),
    ("redir-target-ss-not-flagged",
     "```bash\nprintf '%s\\n' done >>/var/log/ss | grep done\n```\n", 0),
    ("sudo-value-option-disclosed-bypass",
     "```bash\nsudo -u root ss -tlnp | grep 443\n```\n", 0),
    ("prose-outside-fence-not-flagged", "ss -tlnp | grep x\n", 0),
    ("console-output-line-not-flagged",
     "```console\n$ printf x\nss -tlnp | grep 443\n```\n", 0),
    ("console-no-space-prompt-not-flagged",
     "```console\n$ss -tlnp | grep 443\n```\n", 0),
    ("untagged-fence-not-scanned", "```\nss -tlnp | grep 443\n```\n", 0),
    ("grep-before-ss-not-flagged", "```bash\ngrep ss | ss -tlnp\n```\n", 0),
    # fixed false positives (realistic)
    ("comment-after-operator-not-flagged",
     "```bash\ntrue;# example; ss -tlnp | grep 443\n```\n", 0),
    ("leading-redir-hides-command-not-flagged",
     "```bash\n2>/var/log/ss printf done | grep done\n```\n", 0),
    # fixed false negative (leading redirection no longer hides ss)
    ("leading-redir-then-ss-flagged",
     "```bash\n2>/dev/null ss -tlnp | grep 443\n```\n", 1),
    # waiver escape-hatch for the disclosed exotic-construct false positives
    ("waiver-above-line-suppresses",
     "```bash\n# unfiltered-ss: allow example output shown in docs\n"
     "ss -tlnp | grep 443\n```\n", 0),
    ("waiver-same-line-suppresses",
     "```bash\nss -tlnp | grep 443   # unfiltered-ss: allow counterexample\n```\n", 0),
]


def run_self_test():
    failures = 0
    for name, md, expect in SELF_TEST_CASES:
        findings = []
        stats = {"files": 0, "fences": 0, "lines": 0, "unparseable": 0}
        scan_text("<%s>" % name, md, findings, stats)
        waived = _waived_lines(md)
        got = len(set(f for f in findings if f[1] not in waived))
        ok = got == expect
        print("%s %-50s expect=%d got=%d"
              % ("PASS" if ok else "FAIL", name, expect, got))
        if not ok:
            failures += 1
    if failures:
        print("GATE %s-selftest: FAIL -- %d of %d case(s)"
              % (GATE, failures, len(SELF_TEST_CASES)))
        return 1
    print("GATE %s-selftest: PASS -- %d case(s)" % (GATE, len(SELF_TEST_CASES)))
    return 0


def parse_args(argv):
    ap = argparse.ArgumentParser(prog="check_unfiltered_ss.py",
                                 description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("roots", nargs="*", default=None)
    opts = ap.parse_args(argv)
    if not opts.roots:
        opts.roots = ["."]
    return opts


def main(argv):
    opts = parse_args(argv)
    if opts.self_test:
        return run_self_test()
    return run_scan(opts)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
