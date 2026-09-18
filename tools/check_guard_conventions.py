#!/usr/bin/env python3
"""Gate: the two guard conventions for copy-paste shell in the guides.

WHAT THIS CATCHES
  C1-MISSING-Q   a curl invocation in a fenced shell block with no -q/--disable:
                 the reader's ~/.curlrc (a proxy, `insecure`, an output
                 redirect) silently alters the probe.
  C1-LATE-Q      -q present but not the FIRST argument. curl only skips
                 ~/.curlrc when the first parameter starts with -q or is
                 exactly --disable (man curl, -q/--disable: "If used as the
                 first parameter on the command line"). A late -q parses but
                 is inert. --q-anywhere relaxes this to presence-only (triage).
  C1-MISSING-G   a URL argument (carrying a scheme, so "://") holds a literal
                 [ or { that curl globs (an IPv6 literal, a brace range) while
                 no -g/--globoff is present, so the probe morphs or errors.
                 NARROWED: fires only when such a glob character is actually in
                 a URL -- a plain http://host/ URL with no bracket does not need
                 -g and is not flagged, and a { in a -w format string is not a
                 URL. A schemeless glob URL (no "://") is a disclosed blind spot.
  C2-PROBE-OUTSIDE-GUARD
                 in a fenced shell block that uses the house placeholder-guard
                 idiom (a case arm whose PATTERN contains REPLACE_WITH_), a
                 probe-class command that sits outside every such case...esac
                 span -- the known false-pass shape where the guard prints a
                 warning and the probe runs anyway after esac. NOTE: this rule
                 enforces the HOUSE IDIOM (probe lexically inside the guarded
                 case), so it also flags the semantically-safe variant where
                 the sentinel arm exits and the probe follows esac; that is
                 deliberate style enforcement -- move the probe into the arm
                 or waive it.
  C2-WARN-ONLY-GUARD  (--strict-guards only; NOT registered in run_all_checks)
                 an if/elif whose condition mentions REPLACE_WITH_ but whose
                 body reaches fi without exit/return, followed later in the
                 fence by a probe-class command. Opt-in because a
                 flag-variable guard (MISSING=1 tested later) would
                 false-positive it.

WHAT THIS IS NOT
  This is a TRIPWIRE for the accidental case, and a determined author walks
  past it. A pass is NOT a guarantee that every probe is guarded or immune to
  the reader's environment; it is a guarantee that the specific regressions
  above, written in the corpus's own idiom, do not pass silently.

SCOPE
  Fenced blocks come from tools/_markdown.py (blockquote markers stripped;
  four-space-indented fences are not fences and are not scanned). Fences
  tagged bash/sh/shell/zsh are scanned in full; console/terminal fences scan
  only `$ `-prefixed command lines (with `> ` continuation) plus standalone
  waiver comment lines. Heredoc bodies are data and are skipped UNLESS the
  sink is shell (> *.sh, piped to sh/bash/zsh/dash, or the command word is a
  shell reading the heredoc on stdin), in which case the body is scanned as
  shell. Line continuations are joined with exact shell semantics (no
  inserted space). $(...) bodies are lifted out and analyzed, even inside
  double quotes. Contents of [[ ... ]] and of array initializers X=( ... )
  are NOT scanned (test operands and array data are not invocations);
  `command -v curl` / `command -V curl` are lookups, not invocations, and are
  not checked; `name() { ...; }` function-definition headers are not
  invocations of `name`.

  Deliberate exceptions carry, on their OWN comment line inside the fence,
  immediately before the command:
      # guard-conventions: allow <non-empty reason>
  A waiver covers only the next command line and is counted in the summary.
  A trailing same-line waiver is NOT honored; a bare `allow` without a
  reason is NOT honored.

KNOWN REMAINING BYPASSES (recorded so a pass is never mistaken for a
guarantee)
  - curl reached through a name this gate does not resolve: a variable
    (C=curl; "$C" ...), an alias, a shell function, a wrapper script, eval,
    exec curl, a process substitution (bash <(curl ...) / >(curl ...), whose
    inner curl the lexer keeps as one word rather than a command), a
    printf-built command line, xargs -I{} templates, backtick command
    substitution (only $(...) is lifted), find -exec, parallel, coproc.
  - curl running somewhere else: inside a quoted string handed to bash -c /
    ssh host '...' / eval; container argv (docker run curlimages/curl ... is
    not curl's argv here); shell embedded in non-shell fences (yaml, make).
  - a shell block whose fence has no language tag, or a tag outside
    bash/sh/shell/zsh/console/terminal, is not scanned. In console fences,
    lines without a `$ ` prompt are never scanned.
  - heredoc bodies whose sink is not visibly shell are skipped even if a
    reader will later execute them; $(...) inside an UNQUOTED heredoc body
    executes at write time and is not scanned; a heredoc left unterminated
    inside a fence swallows the rest of that fence.
  - options supplied via expansion (curl $CURL_FLAGS ...) are flagged as
    missing BY DESIGN: the convention is that -q -g are literal, reviewable
    tokens.
  - -g or -q inside a short-option cluster that mixes argument-taking
    letters is not credited (write them as their own tokens or in a
    no-argument cluster such as -qgsS).
  - a literal -q or -g that is really another option's VALUE satisfies the
    presence check (curl -q -H -g URL credits -g wrongly); option-looking
    words after -- can also satisfy it. --next resets per-URL options after
    -q -g were credited; -K/--config loads an explicit config file that -q
    does not block.
  - an unquoted URL containing # truncates the lexed line at the fragment;
    options after it are invisible (house style puts options before the URL).
  - a trailing backslash inside a quoted string mis-joins the next physical
    line (continuation joining is textual).
  - lines the lexer cannot tokenize (unterminated quote) are skipped and
    counted in the summary, not failed.
  - array-built commands are opaque: CMD=(curl ...); "${CMD[@]}" is never
    checked. A multi-line array initializer or a multi-line [[ ]] suppresses
    scanning until its closer.
  - sudo/env with argument-taking options (sudo -u user curl ...) is not
    resolved to curl; `function curl { ...; }`-style definitions are treated
    as a command named `function` (not checked, not flagged).
  - the glob-URL check knows a few payload options (-d/--data*/--json/-H/
    --header/-F/--form*) whose value is not a URL and skips them, but it does
    NOT model full curl argument ownership. So a value-taking option can shadow
    one of them: `curl -A --data https://h/[1-3]` makes `--data` the user-agent
    value, and this gate then skips the following glob URL (a false negative);
    and an attached short data option (-d'{"u":"https://h/{x}"}') is not
    recognized as a payload value, so a URL inside it over-includes (flagged;
    resolve with -g or a waiver). A real URL that also holds an IPv6 host
    (http://[::1]/) or a shell expansion (https://${H}/x) is flagged the same
    way, by design: -g there is harmless, not a defect.
  - convention 2: only the case/REPLACE_WITH_ idiom is gated. Renaming the
    sentinel, if [ -z ... ]-style guards, flag-variable guards, or removing
    the wrapping subshell are not caught by the default gate; the
    warn-without-stop if-shape exists behind --strict-guards only.
  - the waiver comment is greppable; review waivers in code review.

EXIT/OUTPUT DISCIPLINE (run_all_checks.sh relies on this)
  Findings print one per line:  path:line: [CODE] message
  A gate-result line always prints on a completed run:
      GATE guard-conventions: PASS ...        (exit 0)
      GATE guard-conventions: FAIL ...        (exit 1)
  A crash prints no gate-result line and exits non-zero; the runner treats
  that, "findings printed but exit 0", and "non-zero exit without a gate
  result" each as a hard failure. --self-test prints
  GATE guard-conventions-selftest: PASS/FAIL and exits 0/1. --min-curls N
  fails the gate if fewer than N curl invocations were scanned, so a scope
  regression cannot pass vacuously.

INTEGRATION ASSUMPTIONS (the only two things to check when landing this)
  1. _blocks() below assumes iter_fenced_blocks(text) yields blocks carrying
     the info string, the 1-based file line of the FIRST BODY line, and the
     body lines (blockquote markers stripped, indented fences excluded). If
     the real tools/_markdown.py exports a different name or shape, adapt
     ONLY _blocks(); it raises on shapes it does not recognize.
  2. iter_md_files() walks the repo for *.md excluding dot-directories,
     node_modules and __pycache__. Align this roster with
     check_verify_safety's if that gate scopes differently.
"""

import argparse
import os
import re
import shlex
import sys

# tools/ must be importable for the _markdown sibling even under `python3 -I`
# (isolated mode drops the script directory from sys.path). Stdlib imports sit
# above this line on purpose: they must never resolve from tools/.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _markdown import Fences, FENCE_RE  # noqa: E402

# Top-level guides only, matching check_verify_safety.py: a fenced block in the
# plugin mirror or in .aiqt docs is not something a reader copies from, and the
# mirror would double-count every curl.
NOT_A_GUIDE = frozenset((
    "CONTRIBUTING.md", "CLAUDE.md", "AGENTS.md", "CHANGELOG.md", "README.sources.md"))
_BLOCKQUOTE_RE = re.compile(r"^ {0,3}(?:>[ \t]{0,3})+")

GATE = "guard-conventions"
SENTINEL = "REPLACE_WITH_"
SHELL_INFOS = frozenset(("bash", "sh", "shell", "zsh"))
CONSOLE_INFOS = frozenset(("console", "terminal"))
EXCLUDE_DIRS = frozenset(("node_modules", "__pycache__"))
# curl short options that take no argument; only these may share a cluster
# with q or g.
NOARG_SHORTS = "qgsSfLkviIN46#"
PROBE_CMDS = frozenset((
    "curl", "wget", "nc", "ncat", "netcat", "socat", "ssh", "scp", "sftp",
    "telnet", "dig", "nslookup", "host", "ping", "nmap",
))
KEYWORDS = frozenset((
    "if", "then", "elif", "else", "fi", "while", "until", "do", "done",
    "!", "time", "in",
))
WRAPPERS = frozenset((
    "sudo", "command", "env", "nohup", "nice", "ionice", "timeout", "xargs",
    "stdbuf",
))
SEPARATORS = frozenset((
    ";", ";;", ";&", ";;&", "|", "||", "|&", "&", "&&", "(", ")", "{", "}",
))
REDIRECTS = frozenset((">", ">>", "<", "<<<", ">&", "<&", "&>", "&>>", ">|"))
SHELL_SINKS = frozenset(("sh", "bash", "zsh", "dash"))

WAIVER_RE = re.compile(r"#\s*guard-conventions:\s*allow\s+(\S.*)$")
PATTERN_TOKEN_RE = re.compile(
    r"[*?\[\]|A-Za-z0-9_.-]*REPLACE_WITH_[*?\[\]|A-Za-z0-9_.-]*$")
_NA = re.escape(NOARG_SHORTS)
CLUSTER_G_RE = re.compile(r"-[%s]*g[%s]*$" % (_NA, _NA))
# Options whose VALUE is request payload, not a URL curl globs: a -d/--json body
# or an -H/-F header can carry a "://" and a bracket (a JSON body holding a URL,
# a Link: header) yet is transmitted verbatim. The URL operand and a --url value
# are NOT in this set, so a real glob URL (--url .../[1-3], {http,https}://...)
# is still inspected. Only the spaced form (-H VALUE) and the attached long form
# (--data=VALUE) are skipped; the rarer attached short form is disclosed.
_VALUE_OPTS_NONURL = frozenset((
    "-d", "--data", "--data-raw", "--data-ascii", "--data-binary",
    "--data-urlencode", "--json", "-H", "--header", "--proxy-header",
    "-F", "--form", "--form-string",
))
CLUSTER_Q_RE = re.compile(r"-[%s]*q[%s]*$" % (_NA, _NA))
ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\+?=")
DURATION_RE = re.compile(r"^\d[\d.]*[smhd]?$")
FD_RE = re.compile(r"^\d+$")

# C3: a live credential placed in curl argv (readable via ps / /proc/<pid>/cmdline
# to local observers while it is there, including before curl scrubs supported
# arguments on some platforms). Detected inside the same per-curl walk as C1/C2 and
# waivable with the existing `# guard-conventions: allow <reason>` comment. The
# header policy is a positive denylist of credential-bearing header NAMES, so
# identity/assertion headers (x-amzn-oidc-identity), CF-Access-Client-Id,
# X-...-token-ttl-seconds and content-negotiation headers pass by construction,
# while x-amzn-oidc-accesstoken (a real access token) is flagged. This is a bounded
# lexical scan with DISCLOSED limits, not a full curl parser. Known false negatives,
# covered by rule 5's tracing obligation: a credential reached through a shell
# variable or command substitution in a VALUE (curl "$URL", --json "$BODY") -- so
# the sweep, not this rule, is what fixed object-storage's presigned "$URL"; a curl
# invoked through a variable/alias/eval; a secret in a --form/-F field or -F's @/<
# content reference, an opaque --cookie/-b cookie, or --netrc(-file); and a body
# whose credential key is unicode-escaped. A body match landing in a non-secret
# value is instead a possible false POSITIVE, waivable per case. Flagging every
# "$VAR" positional would false-positive on a guide's own guarded "$1" URL, so that
# case is documented rather than flagged.
CREDENTIAL_HEADER_RE = re.compile(
    r"^(?:authorization|proxy-authorization|cookie|"
    r"x-api-key|api-key|apikey|x-auth-token|private-token|x-goog-api-key|"
    r"x-amzn-oidc-accesstoken|"
    r"(?:[a-z0-9-]+-)?(?:secret|token|api-key|apikey|access-token))$",
    re.I,
)
BODY_SECRET_RE = re.compile(
    r"""["']?(?:password|passwd|client[_-]secret|api[_-]key|apikey|"""
    r"""secret|access[_-]token|refresh[_-]token)["']?\s*[:=]""",
    re.I,
)
URL_USERINFO_RE = re.compile(r"^[a-z][a-z0-9+.-]*://[^/?#@\s]*:[^/?#@\s]+@", re.I)
SIGNED_URL_RE = re.compile(
    r"[?&](?:x-amz-signature|x-goog-signature|signature|sig)=", re.I)
SCHEMELESS_USERINFO_RE = re.compile(r"^[^/?#@\s]+:[^/?#@\s]+@")
_CRED_USER_OPTS = frozenset(("-u", "-U", "--user", "--proxy-user"))
_CRED_HEADER_OPTS = frozenset(("-H", "--header", "--proxy-header"))
_CRED_BODY_OPTS = frozenset((
    "-d", "--data", "--data-ascii", "--data-binary",
    "--data-urlencode", "--json", "--data-raw"))
# value is a URL whose userinfo or signature query may carry a credential
_CRED_URLVAL_OPTS = frozenset(("--url", "-x", "--proxy", "-e", "--referer"))
_CRED_SHORT = {"-u": "user", "-U": "user", "-H": "header", "-d": "body"}
# Other value-taking curl options: skip their value so it is not read as a URL.
# Credential-bearing options above are handled explicitly, not skipped here.
_SKIP_VALUE_OPTS = frozenset((
    "-o", "--output", "-w", "--write-out", "-X", "--request",
    "--connect-timeout", "--max-time", "--noproxy", "-A", "--user-agent",
    "--resolve", "--cacert", "--capath", "--cert", "--key",
    "--range", "-r", "--retry", "--limit-rate", "-m", "--interface",
    "--dns-servers", "-K", "--config", "-c", "--cookie-jar",
    "-b", "--cookie", "-F", "--form", "--form-string",
))

MESSAGES = {
    "C1-MISSING-Q": "curl lacks -q/--disable: the reader's ~/.curlrc (proxy, "
                    "insecure, output redirect) can silently alter this probe",
    "C1-LATE-Q": "-q is not the first curl argument; curl only skips "
                 "~/.curlrc when the FIRST parameter starts with -q (or is "
                 "--disable), so this -q is inert",
    "C1-MISSING-G": "curl lacks -g/--globoff: [...] or {...} in the URL is "
                    "globbed and the probe morphs or errors",
    "C2-PROBE-OUTSIDE-GUARD": "probe sits outside every REPLACE_WITH_ case "
                              "guard in this block; a guard that warns and "
                              "falls through to the probe is the known "
                              "false-pass shape (move the probe into the "
                              "guarded arm, or waive with a reason)",
    "C2-WARN-ONLY-GUARD": "(strict) probe follows a REPLACE_WITH_ if-guard "
                          "whose body never exits/returns; the probe runs "
                          "even when the placeholder is unedited",
    "C3-USER-ARGV": "curl user:password (or a $-expanded credential) is in "
                    "argv, world-readable via ps / /proc/<pid>/cmdline; pipe a "
                    "config line 'user = \"...\"' to curl --config - instead",
    "C3-HEADER-ARGV": "a credential-bearing curl header (Authorization, "
                      "*-Secret, *-Token, *-Api-Key, --oauth2-bearer, or a "
                      "whole $-expanded header) is in argv; pipe the header "
                      "line to curl --header @- instead",
    "C3-BODY-ARGV": "a credential-bearing request body is in curl argv; move "
                    "it into a --config - stream ('data-binary = \"...\"') or "
                    "feed it from a file with @file",
    "C3-URL-ARGV": "a credential-bearing URL (user:password userinfo or a "
                   "presigned signature) is in curl argv; pipe a config line "
                   "'url = \"...\"' to curl --config - instead",
    "C3-NO-VALUE": "a curl credential option lacks a statically readable "
                   "value; move the credential onto stdin (--config - / "
                   "--header @-) so this gate can see it is not in argv",
}


class Stats(object):
    def __init__(self):
        self.files = 0
        self.fences = 0
        self.curls = 0
        self.probes = 0
        self.guard_fences = 0
        self.waivers = 0
        self.unparseable = 0


def _lang_of(info):
    return info.strip().split()[0].lower() if info.strip() else ""


def _blocks(text):
    """Single integration point with tools/_markdown.py (assumption 1).

    Built on _markdown.Fences (the shared line-oriented fence tracker) rather
    than an iter_fenced_blocks() helper the module does not export. Yields
    (lang, start, lines): lang is the lowercased first word of the info string,
    start is the 1-based line number of the first body line, lines are the body
    lines with blockquote markers stripped. Mirrors check_verify_safety.py's
    blockquote handling so a `> ```bash` block is scanned exactly as a reader
    copies it, and a quotation ending mid-fence closes the fence with it.
    """
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


def _odd_trailing_backslashes(s):
    n = 0
    for ch in reversed(s):
        if ch == "\\":
            n += 1
        else:
            break
    return n % 2 == 1


def _tokenize(line):
    lx = shlex.shlex(line, posix=True, punctuation_chars="();<>|&")
    lx.whitespace_split = True
    lx.commenters = "#"
    return list(lx)


def _lift_cmdsubs(line):
    """Extract $(...) bodies (outside single quotes) so a curl inside a quoted
    command substitution is still analyzed. Returns (outer, [inner, ...])."""
    out, inners = [], []
    i, n = 0, len(line)
    in_sq = in_dq = False
    while i < n:
        c = line[i]
        if c == "\\" and not in_sq and i + 1 < n:
            out.append(line[i:i + 2]); i += 2; continue
        if c == "'" and not in_dq:
            in_sq = not in_sq; out.append(c); i += 1; continue
        if c == '"' and not in_sq:
            in_dq = not in_dq; out.append(c); i += 1; continue
        if c == "$" and not in_sq and line[i + 1:i + 2] == "(":
            depth, j = 1, i + 2
            jsq = jdq = False
            while j < n and depth:
                d = line[j]
                if d == "\\" and not jsq and j + 1 < n:
                    j += 2; continue
                if d == "'" and not jdq:
                    jsq = not jsq
                elif d == '"' and not jsq:
                    jdq = not jdq
                elif not jsq and not jdq:
                    if d == "(":
                        depth += 1
                    elif d == ")":
                        depth -= 1
                j += 1
            inners.append(line[i + 2:j - 1] if depth == 0 else line[i + 2:j])
            out.append("__CMDSUB__")
            i = j
            continue
        out.append(c); i += 1
    return "".join(out), inners


def _expand(line):
    """The logical line plus every lifted $(...) body, recursively."""
    queue, texts = [line], []
    while queue:
        cur = queue.pop(0)
        outer, inners = _lift_cmdsubs(cur)
        queue.extend(inners)
        texts.append(outer)
    return texts


def _strip_wrappers(cmd):
    toks = list(cmd)
    while toks:
        t = toks[0]
        if t in KEYWORDS or ASSIGNMENT_RE.match(t):
            toks.pop(0); continue
        if t in REDIRECTS:
            toks = toks[2:]; continue
        if FD_RE.match(t) and len(toks) > 1 and toks[1] in REDIRECTS:
            toks = toks[3:]; continue
        if t in WRAPPERS:
            toks.pop(0)
            opts = []
            while toks and toks[0].startswith("-") and toks[0] != "--":
                opts.append(toks.pop(0))
            if t == "command" and any("v" in o or "V" in o for o in opts):
                return []  # `command -v curl` is a lookup, not an invocation
            if toks and toks[0] == "--":
                toks.pop(0)
            if t == "timeout" and toks and DURATION_RE.match(toks[0]):
                toks.pop(0)
            continue
        break
    return toks


def _sinks_to_shell(toks):
    stripped = _strip_wrappers(toks)
    if stripped and stripped[0].rsplit("/", 1)[-1] in SHELL_SINKS:
        return True
    for k, t in enumerate(toks):
        if (t in (">", ">>") and k + 1 < len(toks)
                and toks[k + 1].endswith(".sh")):
            return True
        if t in ("|", "|&"):
            rest = [x for x in toks[k + 1:] if x not in WRAPPERS]
            if rest and rest[0].rsplit("/", 1)[-1] in SHELL_SINKS:
                return True
    return False


def _logical_lines(pairs, stats, shell_heredoc_bodies):
    """pairs: [(file_line, text)]. Joins backslash continuations (no inserted
    space -- exact shell semantics) and resolves heredocs: bodies are skipped
    unless the sink is shell, in which case they are queued for a nested
    pass."""
    out = []
    i, n = 0, len(pairs)
    heredocs = []  # FIFO of [delimiter, tab_tolerant, scan_as_shell, body]
    while i < n:
        lineno, text = pairs[i]
        if heredocs:
            delim, tab_ok, as_shell, body = heredocs[0]
            cand = text.lstrip("\t") if tab_ok else text
            if cand.rstrip() == delim:
                heredocs.pop(0)
                if as_shell and body:
                    shell_heredoc_bodies.append(body)
            elif as_shell:
                body.append((lineno, text))
            i += 1
            continue
        buf = text
        while _odd_trailing_backslashes(buf) and i + 1 < n:
            i += 1
            buf = buf[:-1] + pairs[i][1]
        i += 1
        out.append((lineno, buf))
        try:
            toks = _tokenize(buf)
        except ValueError:
            continue
        for k, t in enumerate(toks):
            if t == "<<" and k + 1 < len(toks):
                delim = toks[k + 1]
                tab_ok = delim.startswith("-")
                if tab_ok:
                    delim = delim[1:]
                heredocs.append([delim, tab_ok, _sinks_to_shell(toks), []])
    return out


def _drop_redirections(args):
    out, i = [], 0
    while i < len(args):
        t = args[i]
        if t in REDIRECTS:
            i += 2; continue
        if (FD_RE.fullmatch(t) and i + 1 < len(args)
                and args[i + 1] in REDIRECTS):
            i += 3; continue
        out.append(t); i += 1
    return out


def _cmd_is(word, names):
    return (word.rsplit("/", 1)[-1] if "/" in word else word) in names


def _url_needs_globoff(a):
    """A curl URL argument that holds a literal [ or { curl would glob (a brace
    range, a globbed scheme). A token counts when it carries a scheme (contains
    "://") EXCEPT when it is the value of a data/header/form option, which is
    payload curl transmits verbatim and never globs: a -d JSON body or an -H
    Link: header can carry a "://" and a bracket without being a URL. The URL
    operand and a --url/--url= value are still inspected. The -w format string
    like \'%{http_code}\' carries { but no "://", so it never counts.

    This is a tripwire, and it over-includes rather than misses: a real URL that
    also holds an IPv6 host (http://[::1]/) or a shell expansion (https://${H}/x)
    is still flagged, because -g there is harmless house style, not a defect.
    A schemeless glob URL (no "://"), and an attached short data option
    (-d{...}), are the disclosed boundaries.
    """
    i = 0
    while i < len(a):
        t = a[i]
        if t in _VALUE_OPTS_NONURL:
            i += 2
            continue
        if any(t.startswith(o + "=") for o in _VALUE_OPTS_NONURL if o.startswith("--")):
            i += 1
            continue
        if "://" in t and ("[" in t or "{" in t):
            return True
        i += 1
    return False


def _cred_value(a, i, eq, tail):
    """Return (value, next_index); value None means expected-but-absent."""
    if eq:
        return tail, i + 1
    if i + 1 < len(a):
        return a[i + 1], i + 2
    return None, i + 1


def _cred_header_code(val):
    """C3-HEADER-ARGV when a header VALUE carries a credential; [] for the safe
    @-/@file stdin forms and non-secret header names."""
    if val.startswith("@"):
        return []
    hn, colon, rest = val.partition(":")
    if colon and rest.strip() and CREDENTIAL_HEADER_RE.match(hn.strip()):
        return ["C3-HEADER-ARGV"]
    if not colon and "$" in val:
        return ["C3-HEADER-ARGV"]
    return []


def _credential_codes(a):
    """a: curl argument tokens (after 'curl', redirections dropped). Returns the
    C3-* codes for a live credential placed in curl argv. Safe stdin forms
    (--header @-, --config -) and identity/non-secret headers do not match. See
    the C3 comment above CREDENTIAL_HEADER_RE for the disclosed false negatives."""
    codes = []
    i, n = 0, len(a)
    while i < n:
        t = a[i]
        name, sep, tail = t.partition("=")
        eq = bool(sep)
        if name in _CRED_USER_OPTS:
            val, i = _cred_value(a, i, eq, tail)
            if val is None:
                codes.append("C3-NO-VALUE")
            elif ":" in val or "$" in val:
                codes.append("C3-USER-ARGV")
            continue
        if name == "--oauth2-bearer":
            _val, i = _cred_value(a, i, eq, tail)
            codes.append("C3-HEADER-ARGV")
            continue
        if name in _CRED_HEADER_OPTS:
            val, i = _cred_value(a, i, eq, tail)
            if val is None:
                codes.append("C3-NO-VALUE")
            else:
                codes.extend(_cred_header_code(val))
            continue
        if name in _CRED_BODY_OPTS:
            val, i = _cred_value(a, i, eq, tail)
            if val is None:
                codes.append("C3-NO-VALUE")
            else:
                fromfile = (name != "--data-raw") and val.startswith("@")
                if not fromfile and BODY_SECRET_RE.search(val):
                    codes.append("C3-BODY-ARGV")
            continue
        if name in _CRED_URLVAL_OPTS:
            val, i = _cred_value(a, i, eq, tail)
            if val is None:
                codes.append("C3-NO-VALUE")
            elif (URL_USERINFO_RE.match(val) or SCHEMELESS_USERINFO_RE.match(val)
                  or SIGNED_URL_RE.search(val)):
                codes.append("C3-URL-ARGV")
            continue
        if len(t) > 2 and not t.startswith("--") and t[:2] in _CRED_SHORT:
            kind, val = _CRED_SHORT[t[:2]], t[2:]
            if kind == "user":
                if ":" in val or "$" in val:
                    codes.append("C3-USER-ARGV")
            elif kind == "header":
                codes.extend(_cred_header_code(val))
            elif kind == "body":
                if not val.startswith("@") and BODY_SECRET_RE.search(val):
                    codes.append("C3-BODY-ARGV")
            i += 1
            continue
        if len(t) > 2 and not t.startswith("--") and t[:2] in ("-x", "-e"):
            val = t[2:]
            if (URL_USERINFO_RE.match(val) or SCHEMELESS_USERINFO_RE.match(val)
                    or SIGNED_URL_RE.search(val)):
                codes.append("C3-URL-ARGV")
            i += 1
            continue
        if len(t) > 2 and t.startswith("-") and not t.startswith("--"):
            cluster = t[1:]
            j = 0
            while j < len(cluster) and cluster[j] in NOARG_SHORTS:
                j += 1
            if 0 < j < len(cluster) and cluster[j] in ("u", "U", "H", "d"):
                credc = cluster[j]
                rest = cluster[j + 1:]
                if rest:
                    val = rest
                    i += 1
                else:
                    val, i = (a[i + 1], i + 2) if i + 1 < n else (None, i + 1)
                if val is None:
                    codes.append("C3-NO-VALUE")
                elif credc in ("u", "U"):
                    if ":" in val or "$" in val:
                        codes.append("C3-USER-ARGV")
                elif credc == "H":
                    codes.extend(_cred_header_code(val))
                elif credc == "d":
                    if not val.startswith("@") and BODY_SECRET_RE.search(val):
                        codes.append("C3-BODY-ARGV")
                continue
        if t in _SKIP_VALUE_OPTS:
            i += 2
            continue
        if not t.startswith("-"):
            if URL_USERINFO_RE.match(t) or SIGNED_URL_RE.search(t):
                codes.append("C3-URL-ARGV")
            i += 1
            continue
        i += 1
    return codes


def _check_curl(args, q_anywhere_ok):
    codes = []
    a = _drop_redirections(args)
    q_first = bool(a) and (a[0].startswith("-q") or a[0] == "--disable")
    q_any = any(t == "--disable" or CLUSTER_Q_RE.fullmatch(t) for t in a)
    if q_first:
        pass
    elif q_any:
        if not q_anywhere_ok:
            codes.append("C1-LATE-Q")
    else:
        codes.append("C1-MISSING-Q")
    has_g = any(t in ("-g", "--globoff") or CLUSTER_G_RE.fullmatch(t)
                for t in a)
    if not has_g and _url_needs_globoff(a):
        codes.append("C1-MISSING-G")
    codes.extend(_credential_codes(a))
    return codes


def _console_pairs(body, start):
    pairs, i = [], 0
    while i < len(body):
        line = body[i]
        if line.lstrip().startswith("#") and WAIVER_RE.search(line):
            pairs.append((start + i, line))
            i += 1
            continue
        m = re.match(r"^\s*\$\s?(.*)$", line)
        if m:
            lineno, cmd = start + i, m.group(1)
            while _odd_trailing_backslashes(cmd) and i + 1 < len(body):
                i += 1
                cmd = cmd[:-1] + re.sub(r"^\s*>\s?", "", body[i])
            pairs.append((lineno, cmd))
        i += 1
    return pairs


def _strict_if_guards(path, records, probes, findings):
    # Opt-in (--strict-guards): an if/elif mentioning the sentinel whose body
    # reaches fi without exit/return, with a probe after the fi.
    # Flag-variable guards WILL false-positive here; that is why this is not
    # registered in run_all_checks.sh.
    flat = []
    for lineno, raw, token_lines, _waived in records:
        for toks in token_lines:
            cur = []
            for t in toks:
                if t in SEPARATORS:
                    if cur:
                        flat.append((lineno, raw, cur))
                    cur = []
                else:
                    cur.append(t)
            if cur:
                flat.append((lineno, raw, cur))
    for idx, (lineno, raw, cmd) in enumerate(flat):
        if not cmd or cmd[0] not in ("if", "elif") or SENTINEL not in raw:
            continue
        depth, stops, fi_at = 1, False, None
        for j in range(idx + 1, len(flat)):
            c = flat[j][2]
            if c and c[0] == "if":
                depth += 1
            elif c and c[0] == "fi":
                depth -= 1
                if depth == 0:
                    fi_at = j
                    break
            if depth == 1 and c and c[0] in ("exit", "return"):
                stops = True
        if fi_at is None or stops:
            continue
        fi_line = flat[fi_at][0]
        for _pseq, plineno, name, waived in probes:
            if not waived and plineno > fi_line:
                findings.append((path, plineno, "C2-WARN-ONLY-GUARD",
                                 " (probe: %s)" % name))
                break


def _analyze_fence(path, lang, start, body, findings, stats, opts):
    stats.fences += 1
    shell_heredoc_bodies = []
    if lang in CONSOLE_INFOS:
        lls = _logical_lines(_console_pairs(body, start), stats,
                             shell_heredoc_bodies)
    else:
        lls = _logical_lines([(start + j, ln) for j, ln in enumerate(body)],
                             stats, shell_heredoc_bodies)
    while shell_heredoc_bodies:
        lls.extend(_logical_lines(shell_heredoc_bodies.pop(0), stats,
                                  shell_heredoc_bodies))
    lls.sort(key=lambda p: p[0])

    records = []  # (line, raw, [token list per expanded text], waived)
    pending_waiver = False
    for lineno, raw in lls:
        wm = WAIVER_RE.search(raw)
        if wm and raw.lstrip().startswith("#") and wm.group(1).strip():
            pending_waiver = True
            stats.waivers += 1
            continue
        token_lines = []
        for text in _expand(raw):
            try:
                token_lines.append(_tokenize(text))
            except ValueError:
                stats.unparseable += 1
        records.append((lineno, raw, token_lines, pending_waiver))
        if raw.strip():
            pending_waiver = False

    # Sequential walk: simple commands get sequence numbers; `case` is pushed
    # eagerly at command position so a sentinel pattern on the SAME line (a
    # single-line guard) is still credited; `pattern )` marks the open case.
    # Array initializers and [[ ]] contents are opaque; `name ( )` function
    # definitions are not invocations.
    seq = 0
    probes = []          # (seq, line, name, waived)
    curl_findings = []   # (line, code, waived)
    case_stack = []      # [start_seq, saw_sentinel_pattern]
    guard_spans = []     # (start_seq, end_seq)
    array_depth = 0
    in_dbrackets = False

    def commit(cmd, line, waived):
        nonlocal seq
        seq += 1
        if cmd[0] == "case":
            return
        if cmd[0] == "esac":
            if case_stack:
                start_seq, sentinel = case_stack.pop()
                if sentinel:
                    guard_spans.append((start_seq, seq))
            return
        stripped = _strip_wrappers(cmd)
        if not stripped:
            return
        word = stripped[0]
        if _cmd_is(word, ("curl",)):
            stats.curls += 1
            for code in _check_curl(stripped[1:], opts.q_anywhere):
                curl_findings.append((line, code, waived))
        if _cmd_is(word, PROBE_CMDS) or (
                _cmd_is(word, ("openssl",)) and len(stripped) > 1
                and stripped[1] == "s_client"):
            stats.probes += 1
            probes.append((seq, line, word.rsplit("/", 1)[-1], waived))

    for lineno, _raw, token_lines, waived in records:
        for toks in token_lines:
            buf = []
            k = 0
            while k < len(toks):
                t = toks[k]
                if array_depth:
                    if t == "(":
                        array_depth += 1
                    elif t == ")":
                        array_depth -= 1
                    k += 1
                    continue
                if in_dbrackets:
                    if t == "]]":
                        in_dbrackets = False
                        buf = []
                    k += 1
                    continue
                if t == "[[":
                    in_dbrackets = True
                    k += 1
                    continue
                if (t == "(" and buf and buf[-1].endswith("=")
                        and ASSIGNMENT_RE.match(buf[-1])):
                    buf.pop()
                    array_depth = 1
                    k += 1
                    continue
                if (t == "()" and len(buf) == 1
                        and buf[0] not in KEYWORDS):
                    buf = []  # `name ()` function definition, not a command
                    k += 1
                    continue
                if (t == "(" and len(buf) == 1 and buf[0] not in KEYWORDS
                        and k + 1 < len(toks) and toks[k + 1] == ")"):
                    buf = []
                    k += 2
                    continue
                if (t == ")" and k > 0 and case_stack
                        and SENTINEL in toks[k - 1]
                        and PATTERN_TOKEN_RE.fullmatch(toks[k - 1])):
                    case_stack[-1][1] = True
                if t in SEPARATORS:
                    if buf:
                        commit(buf, lineno, waived)
                        buf = []
                else:
                    if t == "case" and all(x in KEYWORDS for x in buf):
                        case_stack.append([seq + 1, False])
                    buf.append(t)
                k += 1
            if buf:
                commit(buf, lineno, waived)

    for start_seq, sentinel in case_stack:  # unterminated case: lenient span
        if sentinel:
            guard_spans.append((start_seq, seq + 1))

    for lineno, code, waived in curl_findings:
        if not waived:
            findings.append((path, lineno, code, ""))
    if guard_spans:
        stats.guard_fences += 1
        if not opts.no_c2:
            for pseq, lineno, name, waived in probes:
                if not waived and not any(s < pseq <= e
                                          for s, e in guard_spans):
                    findings.append((path, lineno, "C2-PROBE-OUTSIDE-GUARD",
                                     " (probe: %s)" % name))
    if opts.strict_guards:
        _strict_if_guards(path, records, probes, findings)


def scan_text(path, text, findings, stats, opts):
    for lang, start, body in _blocks(text):
        if lang in SHELL_INFOS or lang in CONSOLE_INFOS:
            _analyze_fence(path, lang, start, body, findings, stats, opts)


def iter_md_files(roots):
    """Top-level guides only (roster shared with check_verify_safety.py).

    A directory root contributes its DIRECT *.md children, excluding NOT_A_GUIDE;
    it is not descended, so the plugin mirror and .aiqt docs are not scanned and
    no curl is counted twice. An explicit file root is always included.
    """
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
    findings, stats = [], Stats()
    for path in iter_md_files(opts.roots):
        stats.files += 1
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            scan_text(path, fh.read(), findings, stats, opts)
    findings.sort(key=lambda f: (f[0], f[1], f[2]))
    for path, lineno, code, extra in findings:
        print("%s:%d: [%s] %s%s" % (path, lineno, code, MESSAGES[code], extra))
    print("checked %d file(s), %d shell fence(s), %d curl invocation(s), "
          "%d probe(s), %d guard fence(s); %d waiver(s); "
          "%d unparseable line(s) skipped"
          % (stats.files, stats.fences, stats.curls, stats.probes,
             stats.guard_fences, stats.waivers, stats.unparseable))
    failed = bool(findings)
    if stats.curls < opts.min_curls:
        print("scope regression: scanned %d curl invocation(s), expected at "
              "least %d -- the gate is no longer seeing the corpus"
              % (stats.curls, opts.min_curls))
        failed = True
    if failed:
        print("GATE %s: FAIL -- %d finding(s)" % (GATE, len(findings)))
        return 1
    print("GATE %s: PASS" % GATE)
    return 0


# --------------------------- self-test ---------------------------
# Recorded cases: each proves one behavior the gate claims, including the
# round-2..4 QA mutations (-q removed, -g removed, probe moved after esac)
# and the clean forms. Codes only are compared; messages are cosmetic.

SELF_TEST_CASES = [
    # (name, markdown, expected finding codes, extra CLI flags)
    ("clean-curl",
     "```bash\ncurl -q -g \"https://example.com/healthz\"\n```\n", [], ()),
    ("mutation-q-removed",
     "```bash\ncurl -g https://example.com/healthz\n```\n",
     ["C1-MISSING-Q"], ()),
    ("mutation-g-removed",
     "```bash\ncurl -q \"https://example.com/[1-3]\"\n```\n",
     ["C1-MISSING-G"], ()),
    ("late-q-inert",
     "```bash\ncurl -g -q https://example.com/\n```\n", ["C1-LATE-Q"], ()),
    ("late-q-relaxed",
     "```bash\ncurl -g -q https://example.com/\n```\n", [],
     ("--q-anywhere",)),
    ("disable-long-form",
     "```bash\ncurl --disable -g https://example.com/\n```\n", [], ()),
    ("globoff-long-form",
     "```bash\ncurl -q --globoff https://example.com/\n```\n", [], ()),
    ("cluster-ok",
     "```bash\ncurl -qgsS https://example.com/\n```\n", [], ()),
    ("qg-bundle",
     "```bash\ncurl -qg https://example.com/\n```\n", [], ()),
    ("mixed-cluster-not-credited",
     "```bash\ncurl -qog \"https://example.com/[1-3]\"\n```\n", ["C1-MISSING-G"], ()),
    ("c1-still-enforced-under-no-c2",
     "```bash\ncurl https://example.com/\n```\n", ["C1-MISSING-Q"], ("--no-c2",)),
    ("url-in-data-body-not-globbed",
     "```bash\ncurl -q --data '{\"u\":\"https://e.com/{x}\"}' https://e.com/\n```\n", [], ()),
    ("url-in-header-value-not-globbed",
     "```bash\ncurl -q -H 'Link: <https://e.com/[1]>' https://e.com/\n```\n", [], ()),
    ("url-flag-value-glob-still-caught",
     "```bash\ncurl -q --url 'https://e.com/[1-3]'\n```\n", ["C1-MISSING-G"], ()),
    ("url-flag-attached-glob-still-caught",
     "```bash\ncurl -q --url=https://e.com/{a,b}\n```\n", ["C1-MISSING-G"], ()),
    ("globbed-scheme-still-caught",
     "```bash\ncurl -q {http,https}://e.com/\n```\n", ["C1-MISSING-G"], ()),
    ("data-value-that-is-a-url-not-globbed",
     "```bash\ncurl -q --data 'https://e.com/[1]' https://e.com/\n```\n", [], ()),
    ("comment-curl-ignored",
     "```bash\n# curl without -q in prose\ncurl -q -g https://e.com/\n```\n",
     [], ()),
    ("curlimages-not-a-command",
     "```bash\ndocker pull curlimages/curl\n```\n", [], ()),
    ("curl-in-echo-string-ignored",
     "```bash\necho \"never run curl without flags\"\n```\n", [], ()),
    ("heredoc-data-skipped",
     "```bash\ncat <<'EOF' > notes.txt\ncurl http://plain.example/\nEOF\n"
     "```\n", [], ()),
    ("heredoc-to-script-scanned",
     "```bash\ncat <<'EOF' > probe.sh\ncurl http://plain.example/[1-3]\nEOF\n"
     "```\n", ["C1-MISSING-G", "C1-MISSING-Q"], ()),
    ("heredoc-piped-to-bash-scanned",
     "```bash\ncat <<EOF | bash\ncurl -g http://plain.example/\nEOF\n```\n",
     ["C1-MISSING-Q"], ()),
    ("heredoc-stdin-of-bash-scanned",
     "```bash\nbash <<'EOF'\ncurl -g http://plain.example/\nEOF\n```\n",
     ["C1-MISSING-Q"], ()),
    ("continuation-joined",
     "```bash\ncurl \\\n  -q -g https://example.com/\n```\n", [], ()),
    ("continuation-split-flag",
     "```bash\ncurl -\\\nq -g https://example.com/\n```\n", [], ()),
    ("multiline-house-idiom",
     "```bash\ncurl -q -g \\\n  --max-time 5 \\\n"
     "  -H \"Accept: application/json\" \\\n"
     "  \"https://example.com/healthz\"\n```\n", [], ()),
    ("cmdsub-quoted-lifted",
     "```bash\nbody=\"$(curl -g https://example.com/)\"\n```\n",
     ["C1-MISSING-Q"], ()),
    ("wrapper-sudo",
     "```bash\nsudo curl -g https://example.com/\n```\n",
     ["C1-MISSING-Q"], ()),
    ("command-dash-v-not-an-invocation",
     "```bash\ncommand -v curl >/dev/null || exit 1\n```\n", [], ()),
    ("redirect-prefix",
     "```bash\n2>/dev/null curl -g https://example.com/\n```\n",
     ["C1-MISSING-Q"], ()),
    ("function-def-not-an-invocation",
     "```bash\ncurl() { printf x; }\n```\n", [], ()),
    ("array-initializer-opaque",
     "```bash\ndeps=(curl jq)\nCMD+=(-q -g)\n```\n", [], ()),
    ("dbrackets-operand-ignored",
     "```bash\n[[ x || curl ]]\n```\n", [], ()),
    ("dbrackets-then-real-curl",
     "```bash\n[[ -z \"$x\" ]] || curl -g https://e.com/\n```\n",
     ["C1-MISSING-Q"], ()),
    ("negated-probe-clean",
     "```bash\nif ! curl -q -g https://e.com/; then\n  echo down\nfi\n```\n",
     [], ()),
    ("pipe-xargs",
     "```bash\nprintf '%s\\n' https://e.com/ | xargs curl -g\n```\n",
     ["C1-MISSING-Q"], ()),
    ("console-prompt-lines-only",
     "```console\n$ curl -g http://e.com/\ncurl: (7) connection refused\n"
     "```\n", ["C1-MISSING-Q"], ()),
    ("console-continuation",
     "```console\n$ curl \\\n>   -q -g http://e.com/\nok\n```\n", [], ()),
    ("console-waiver-honored",
     "```console\n# guard-conventions: allow install check, no URL\n"
     "$ curl -q http://e.com/\n```\n", [], ()),
    ("untagged-fence-not-scanned",
     "```\ncurl http://e.com/\n```\n", [], ()),
    ("indented-fence-not-scanned",
     "Text\n\n    ```bash\n    curl http://e.com/\n    ```\n", [], ()),
    ("blockquoted-fence-scanned",
     "> ```bash\n> curl -g http://e.com/\n> ```\n", ["C1-MISSING-Q"], ()),
]

SELF_TEST_CASES += [
    ("waiver-honored",
     "```bash\n# guard-conventions: allow vendor URL needs globbing here\n"
     "curl -q \"http://e.com/[1-3]\"\n```\n", [], ()),
    ("bare-waiver-not-honored",
     "```bash\n# guard-conventions: allow\ncurl -q \"http://e.com/[1-3]\"\n```\n",
     ["C1-MISSING-G"], ()),
    ("trailing-waiver-not-honored",
     "```bash\ncurl -q \"http://e.com/[1-3]\" # guard-conventions: allow x\n```\n",
     ["C1-MISSING-G"], ()),
    ("multiple-findings-per-block",
     "```bash\ncurl -g https://e.com/\ncurl -q \"https://e.com/[1-3]\"\n"
     "curl -q -g https://e.com/\n```\n",
     ["C1-MISSING-G", "C1-MISSING-Q"], ()),
    ("no-g-no-glob-clean",
     "```bash\ncurl -q https://example.com/\n```\n", [], ()),
    ("g-on-glob-url-clean",
     "```bash\ncurl -q -g \"https://example.com/[1-3]\"\n```\n", [], ()),
    ("brace-range-url-flagged",
     "```bash\ncurl -q \"https://example.com/{a,b}\"\n```\n",
     ["C1-MISSING-G"], ()),
    ("w-format-brace-not-a-url",
     "```bash\ncurl -q -w '%{http_code}\\n' https://example.com/\n```\n",
     [], ()),
    ("guard-clean",
     "```bash\n(\n  case \"$1\" in\n"
     "    *REPLACE_WITH_TARGET*) echo \"edit the target first\" >&2; "
     "exit 1;;\n"
     "    *) curl -q -g \"https://$1/healthz\";;\n  esac\n)\n```\n", [], ()),
    ("mutation-probe-after-esac",
     "```bash\n(\n  case \"$1\" in\n"
     "    *REPLACE_WITH_TARGET*) echo \"edit the target first\" >&2;;\n"
     "  esac\n  curl -q -g \"https://$1/healthz\"\n)\n```\n",
     ["C2-PROBE-OUTSIDE-GUARD"], ()),
    ("terminating-arm-variant-flagged-as-idiom-deviation",
     "```bash\n(\n  case \"$1\" in\n    *REPLACE_WITH_TARGET*) exit 2;;\n"
     "  esac\n  curl -q -g -- \"$1\"\n)\n```\n",
     ["C2-PROBE-OUTSIDE-GUARD"], ()),
    ("single-line-guard-ssh-after-esac",
     "```bash\ncase \"$1\" in *REPLACE_WITH_T*) echo warn;; esac\n"
     "ssh admin@$1 uptime\n```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),
    ("guard-nc-clean",
     "```bash\n(\n  case \"$1\" in\n"
     "    *REPLACE_WITH_TARGET*) echo \"edit first\" >&2; exit 1;;\n"
     "    *) nc -z $1 443;;\n  esac\n)\n```\n", [], ()),
    ("two-guarded-cases",
     "```bash\ncase \"$1\" in *REPLACE_WITH_A*) exit 1;; "
     "*) curl -q -g \"https://$1/\";; esac\n"
     "case \"$2\" in *REPLACE_WITH_B*) exit 1;; "
     "*) curl -q -g \"https://$2/\";; esac\n```\n", [], ()),
    ("nested-inner-case-probe-still-inside-outer-guard",
     "```bash\ncase \"$1\" in\n  *REPLACE_WITH_T*) exit 1;;\n  *)\n"
     "    case \"$2\" in\n      a) mode=x;;\n    esac\n"
     "    curl -q -g \"https://$1/\"\n    ;;\nesac\n```\n", [], ()),
    ("sentinel-in-body-not-a-guard",
     "```bash\ncase \"$mode\" in prod) curl -q -g "
     "\"https://REPLACE_WITH_HOST/x\";; esac\n"
     "curl -q -g \"https://fixed.example/\"\n```\n", [], ()),
    ("unguarded-second-probe",
     "```bash\n( case \"$1\" in *REPLACE_WITH_T*) exit 1;; "
     "*) curl -q -g x;; esac )\n"
     "curl -q -g \"https://fixed.example/\"\n```\n",
     ["C2-PROBE-OUTSIDE-GUARD"], ()),
    ("unguarded-probe-waived",
     "```bash\n( case \"$1\" in *REPLACE_WITH_T*) exit 1;; "
     "*) curl -q -g x;; esac )\n"
     "# guard-conventions: allow fixed vendor URL, no reader input\n"
     "curl -q -g \"https://fixed.example/\"\n```\n", [], ()),
    ("keyword-prefixed-case-position",
     "```bash\nif x; then case \"$1\" in *REPLACE_WITH_T*) exit 1;; "
     "*) curl -q -g y;; esac; fi\n```\n", [], ()),
    ("strict-warn-only-guard",
     "```bash\nif [ \"$T\" = \"REPLACE_WITH_TARGET\" ]; then\n"
     "  echo \"warning: placeholder\" >&2\nfi\n"
     "curl -q -g \"https://$T/\"\n```\n",
     ["C2-WARN-ONLY-GUARD"], ("--strict-guards",)),
    ("strict-shape-off-by-default",
     "```bash\nif [ \"$T\" = \"REPLACE_WITH_TARGET\" ]; then\n"
     "  echo \"warning: placeholder\" >&2\nfi\n"
     "curl -q -g \"https://$T/\"\n```\n", [], ()),
    ("strict-exit-guard-clean",
     "```bash\nif [ \"$T\" = \"REPLACE_WITH_TARGET\" ]; then\n"
     "  echo \"edit T\" >&2\n  exit 1\nfi\n"
     "curl -q -g \"https://$T/\"\n```\n", [], ("--strict-guards",)),
    ("unparseable-line-skipped-not-failed",
     "```bash\necho don't panic\ncurl -q -g https://e.com/\n```\n", [], ()),
    ("c2-demotion-flag",
     "```bash\n(\n  case \"$1\" in\n"
     "    *REPLACE_WITH_TARGET*) echo \"edit the target first\" >&2;;\n"
     "  esac\n  curl -q -g \"https://$1/healthz\"\n)\n```\n", [],
     ("--no-c2",)),
    ("c3-user-argv-basic",
     "```bash\ncurl -q -u admin:REPLACE_WITH_PASSWORD https://h/\n```\n",
     ["C3-USER-ARGV"], ()),
    ("c3-user-argv-attached-and-var",
     "```bash\ncurl -q -uadmin:pw https://h/\ncurl -q -u \"$CREDS\" https://h/\n```\n",
     ["C3-USER-ARGV", "C3-USER-ARGV"], ()),
    ("c3-user-colon-free-ok",
     "```bash\ncurl -q -u admin https://h/\n```\n", [], ()),
    ("c3-header-argv-authorization",
     "```bash\ncurl -q -g -H \"Authorization: Bearer REPLACE_WITH_KEY\" https://h/\n```\n",
     ["C3-HEADER-ARGV"], ()),
    ("c3-header-argv-secret-and-var",
     "```bash\ncurl -q --header=X-Api-Key:secret https://h/\n"
     "curl -q -H \"$HDR\" https://h/\n```\n",
     ["C3-HEADER-ARGV", "C3-HEADER-ARGV"], ()),
    ("c3-header-oauth2-bearer",
     "```bash\ncurl -q --oauth2-bearer REPLACE_WITH_T https://h/\n```\n",
     ["C3-HEADER-ARGV"], ()),
    ("c3-header-stdin-safe",
     "```bash\nprintf 'Authorization: Bearer %s\\n' \"$1\" | "
     "curl -q -g -sS -H @- http://h/x\n```\n", [], ()),
    ("c3-header-nonsecret-and-identity-ok",
     "```bash\ncurl -q -H \"Content-Type: application/json\" https://h/\n"
     "curl -q -H \"x-amzn-oidc-identity: admin\" https://h/\n"
     "curl -q -H \"CF-Access-Client-Id: REPLACE_WITH_ID\" https://h/\n```\n",
     [], ()),
    ("c3-body-argv-secret",
     "```bash\ncurl -q --data-urlencode password=x https://h/\n```\n",
     ["C3-BODY-ARGV"], ()),
    ("c3-body-file-and-nonsecret-ok",
     "```bash\ncurl -q --json @body.json https://h/\n"
     "curl -q -d '{\"model\":\"ping\"}' https://h/\n```\n", [], ()),
    ("c3-url-userinfo-and-signature",
     "```bash\ncurl -q https://user:pw@h/\n"
     "curl -q 'https://b.example/o?X-Amz-Signature=abc&x=1'\n```\n",
     ["C3-URL-ARGV", "C3-URL-ARGV"], ()),
    ("c3-url-generic-token-not-gated",
     "```bash\ncurl -q 'https://h/o?token=abc'\n```\n", [], ()),
    ("c3-config-stdin-safe",
     "```bash\nprintf 'user = \"admin:%s\"\\n' \"$1\" | "
     "curl -q -g -sS --config - -o /dev/null -w '%{http_code}\\n' https://h/\n```\n",
     [], ()),
    ("c3-user-argv-waived",
     "```bash\n# guard-conventions: allow documented teaching example\n"
     "curl -q -u admin:pw https://h/\n```\n", [], ()),
    ("c3-cluster-user-flagged",
     "```bash\ncurl -q -suadmin:secret https://h/\n```\n",
     ["C3-USER-ARGV"], ()),
    ("c3-proxy-userinfo-flagged",
     "```bash\ncurl -q --proxy 'https://u:pw@proxy/' https://h/\n```\n",
     ["C3-URL-ARGV"], ()),
    ("c3-form-and-cookie-are-documented-limits",
     "```bash\ncurl -q --form 'password=hunter2' https://h/\n"
     "curl -q --form 'password=@-' https://h/\n"
     "curl -q --cookie 'session=opaque' https://h/\n```\n", [], ()),
    ("c3-proxy-schemeless-userinfo-flagged",
     "```bash\ncurl -q --proxy 'admin:secret@proxy:8080' https://h/\n```\n",
     ["C3-URL-ARGV"], ()),
    ("c3-empty-user-url-flagged",
     "```bash\ncurl -q https://:secret@h/\n```\n", ["C3-URL-ARGV"], ()),
    ("c3-oidc-accesstoken-flagged-identity-not",
     "```bash\ncurl -q -H \"x-amzn-oidc-accesstoken: REAL\" https://h/\n"
     "curl -q -H \"x-amzn-oidc-identity: admin\" https://h/\n```\n",
     ["C3-HEADER-ARGV"], ()),
    ("c3-config-value-not-a-url",
     "```bash\ncurl -q --config './settings?sig=public' https://h/\n```\n",
     [], ()),
    ("c3-cookie-opaque-session-not-flagged",
     "```bash\ncurl -q --cookie 'session=opaquevalue' https://h/\n```\n",
     [], ()),
    ("c3-credential-option-no-value",
     "```bash\ncurl -q https://h/ -u\n```\n", ["C3-NO-VALUE"], ()),
]


def run_self_test():
    failures = 0
    for name, mdtext, expect, flags in SELF_TEST_CASES:
        opts = parse_args(list(flags))
        findings, stats = [], Stats()
        scan_text("<%s>" % name, mdtext, findings, stats, opts)
        got = sorted(code for _p, _l, code, _x in findings)
        exp = sorted(expect)
        ok = got == exp
        print("%s %-48s expect=%s got=%s"
              % ("PASS" if ok else "FAIL", name, exp, got))
        if not ok:
            failures += 1
    if failures:
        print("GATE %s-selftest: FAIL -- %d of %d case(s)"
              % (GATE, failures, len(SELF_TEST_CASES)))
        return 1
    print("GATE %s-selftest: PASS -- %d case(s)"
          % (GATE, len(SELF_TEST_CASES)))
    return 0


def parse_args(argv):
    ap = argparse.ArgumentParser(prog="check_guard_conventions.py",
                                 description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true", dest="self_test",
                    help="run the recorded still-catches-what-it-claims cases")
    ap.add_argument("--strict-guards", action="store_true",
                    dest="strict_guards",
                    help="also apply the warn-without-stop if-guard check "
                         "(may false-positive on flag-style guards; not for "
                         "CI)")
    ap.add_argument("--no-c2", action="store_true", dest="no_c2",
                    help="demote convention 2: skip C2-PROBE-OUTSIDE-GUARD "
                         "(tracked-row fallback if the idiom rule proves "
                         "noisy on real guides)")
    ap.add_argument("--q-anywhere", action="store_true", dest="q_anywhere",
                    help="accept -q in any position (triage aid; curl only "
                         "honors a FIRST-position -q)")
    ap.add_argument("--min-curls", type=int, default=0, dest="min_curls",
                    help="fail unless at least N curl invocations were "
                         "scanned (guards against silent scope regressions)")
    ap.add_argument("roots", nargs="*", default=None,
                    help="files or directories to scan (default: .)")
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
