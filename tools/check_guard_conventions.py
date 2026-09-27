#!/usr/bin/env python3
"""Gate: guard conventions for copy-paste shell in the guides.

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
                 in a fenced shell block with a recognized case PATTERN
                 containing REPLACE_WITH_, a probe-class command without
                 coverage from a guard. Recognition activates checking even
                 for quoted or ineffective sentinel lookalikes.

                 Coverage requires an effective unquoted sentinel alternative.
                 The bounded accepted shape is one or more stars, REPLACE_WITH_,
                 an optional literal suffix of letters, digits, underscore,
                 dot or hyphen, and one or more trailing stars. Brackets,
                 pinned prefixes/suffixes and uncertain shapes earn no coverage.
                 Before the first effective sentinel arm, any arm not proven
                 disjoint from placeholder values must have a termination
                 certificate; otherwise neither ordinary nor extended coverage
                 is granted. Ineffective sentinel lookalikes cannot certify.

                 An eligible case covers its lexical case...esac span.
                 A straight-line case whose every recognized sentinel arm
                 has a termination certificate may extend coverage to the
                 close of its execution scope.

                 A certificate requires a literal, unwrapped exit or return,
                 with no argument or one literal decimal status from 0 to
                 255, no redirection, and an unconditional arm-level command
                 prefix. Compound operators revoke certification. Nested
                 blocks, function definitions and command substitutions do
                 not supply an arm-level termination certificate. return
                 additionally requires a function-body scope.

                 Extension stops at the relevant subshell or function
                 boundary; exit may pass through ordinary brace groups.
                 Conditional, loop, pipeline and background contexts deny
                 extension. Invalid or unterminated cases grant no coverage.
                 A sentinel arm cannot use its own case to cover its probes;
                 cases with ;& or ;;& grant no coverage.
  C2-WARN-ONLY-GUARD  (--strict-guards only; NOT registered in run_all_checks)
                 an if/elif whose condition mentions REPLACE_WITH_ but whose
                 body reaches fi without exit/return, followed later in the
                 fence by a probe-class command without effective C2
                 guard coverage for every operand variable. Unknown subjects
                 or operands do not grant strict suppression. Opt-in because a
                 flag-variable guard (MISSING=1 tested later) would
                 false-positive it.

  C3-TOOL-ARGV  a known non-curl credential flag or credential positional
                 argument, env assignment or URI carries a value in argv.
                 Whole REPLACE_WITH_ userinfo passwords are exempt, but
                 query credentials are checked independently. Visible shell
                 builtin URI delivery is exempt; external wrappers are not.
                 Other literal values,
                 placeholders and expansions are all checked, independently
                 of C2's network-probe roster. The allowlist and bounded
                 argument ownership are in _tool_credential_flags. Prompt,
                 file and documented stdin forms pass; a waiver uses the
                 same preceding-comment mechanism as curl's C3 checks.

WHAT THIS IS NOT
  This is a tripwire for the accidental case; a determined author walks
  past it. It is not a general safety proof for shell programs. A guard over $1 proves nothing about a later
  probe of $2 or of a reassigned variable. A pass does not establish that
  every probe is guarded or immune to the reader's environment.

  Any claim of zero false negatives on a reviewed corpus depends on human
  inspection of every cleared and residual finding, not on this parser
  establishing placeholder dataflow. The shared tokenizer also loses quote
  identity: C2 uses additional lexical metadata to deny uncertain coverage,
  but cannot recover commands already hidden by the shared array scanner.

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
  - strict C2: subject/operand matching tracks variable names, not values.
    Reassignment (including set/shift of positional parameters, or
    function-parameter re-binding) or aliasing between guard and probe is not
    followed. Simple positional and named references, with optional braces, are
    supported; compound subjects, parameter operators, concatenated quoting and
    opaque operands deny suppression.
    All argument variables are included, so options unrelated to the target
    may over-flag.
    Two further name-matched-but-value-unsafe shapes are NOT caught (both
    require deliberate authoring; neither occurs in the corpus): a guard whose
    sentinel pattern rejects a DIFFERENT placeholder than the probe carries
    (e.g. a *REPLACE_WITH_Y* arm crediting a probe of $1=REPLACE_WITH_X),
    because the subject variable is matched but the arm pattern is not checked
    against the probe's value; and a probe that concatenates several
    separately-guarded variables (e.g. "$1$2") whose fragments each pass their
    own guard while the concatenation assembles a placeholder no single guard
    rejected.
  - the waiver comment is greppable; review waivers in code review.
  - C2: composite adjacent punctuation such as );, )& or )) can confuse
    command and scope boundaries. Write the guard in the standard
    sentinel-first *REPLACE_WITH_*) form on its own line, probe on its own line.
  - C2: function name { } and case-bodied functions can lose function scope.
    Write the guard in the standard sentinel-first *REPLACE_WITH_*) form on
    its own line, probe on its own line.
  - C2: a DEBUG trap with extdebug can skip a credited exit or return.
    Write the guard in the standard sentinel-first *REPLACE_WITH_*) form on
    its own line, probe on its own line.
  - C2: negated/bracket sentinel patterns such as *REPLACE_WITH_[!..]* can
    miss recognition entirely. Write the guard in the standard sentinel-first
    *REPLACE_WITH_*) form on its own line, probe on its own line.
  - C2: time -p can hide the probe command behind an unrecognized prefix.
    Write the guard in the standard sentinel-first *REPLACE_WITH_*) form on
    its own line, probe on its own line.
  - C2: quoted '<<' can be mistaken for a heredoc operator and hide commands.
    Write the guard in the standard sentinel-first *REPLACE_WITH_*) form on
    its own line, probe on its own line.
  - C2: a backslash at the end of a comment can swallow the following line.
    Write the guard in the standard sentinel-first *REPLACE_WITH_*) form on
    its own line, probe on its own line.
  - C2: a child-heredoc waiver can leak across execution domains.
    Write the guard in the standard sentinel-first *REPLACE_WITH_*) form on
    its own line, probe on its own line.
  - C2: case-subject $(...) substitution can confuse command/scope tracking.
    Write the guard in the standard sentinel-first *REPLACE_WITH_*) form on
    its own line, probe on its own line.
  - C2: eval, source or enable -n can redefine or disable exit without
    revoking its certificate. Write the guard in the standard sentinel-first
    *REPLACE_WITH_*) form on its own line, probe on its own line.
  - C2: a literal DIFFERENT placeholder in a probe can be cleared by an
    unrelated guard; placeholder dataflow is not checked. Write the guard in
    the standard sentinel-first *REPLACE_WITH_*) form on its own line, probe
    on its own line.

  This formatting guidance keeps the idiom reviewable; it does not repair
  these bypasses or prove that a guard checks the value actually probed.

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

# C2 only. Keep the shared tokenizer, keyword set, and probe recognition intact.
_C2_BLOCK_OPEN = frozenset(("if", "for", "while", "until", "select"))
_C2_BLOCK_CLOSE = frozenset(("fi", "done"))
_C2_COMPOUND = frozenset(("&&", "||", "|", "|&", "&"))
_C2_CONTINUATION = frozenset(("&&", "||", "|", "|&"))
_C2_ARM_KILL = frozenset((
    "if", "elif", "else", "then", "do", "done",
    "for", "while", "until", "select", "case", "{", "(", "[[",
))
_C2_STATUS_RE = re.compile(r"[0-9]+")
_C2_SENTINEL_GLOB_RE = re.compile(r"\*+REPLACE_WITH_[A-Za-z0-9_.-]*\*+")
_C2_PLAIN_PATTERN_RE = re.compile(r"[A-Za-z0-9_./:-]*")

# Build-gated hardening: disable together with fixtures 28 and 29 only if
# the existing-fixture/corpus review requires the documented fallback.
_C2_HARDENING = True


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
# content reference, an opaque --cookie/-b cookie, an -e/--referer URL, or --netrc(-file); and a body
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
_CRED_URLVAL_OPTS = frozenset(("--url",))
_CRED_PROXY_OPTS = frozenset(("-x", "--proxy"))
_CRED_SHORT = {"-u": "user", "-U": "user", "-H": "header", "-d": "body"}
# Other value-taking curl options: skip their value so it is not read as a URL.
# Credential-bearing options above are handled explicitly, not skipped here.
_SKIP_VALUE_OPTS = frozenset((
    "-o", "--output", "-w", "--write-out", "-X", "--request",
    "--connect-timeout", "--max-time", "--noproxy", "-A", "--user-agent",
    "--resolve", "--cacert", "--capath", "--cert", "--key",
    "--range", "-r", "--retry", "--limit-rate", "-m", "--interface",
    "--dns-servers", "-K", "--config", "-c", "--cookie-jar",
    "-b", "--cookie", "-F", "--form", "--form-string", "-e", "--referer",
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
    "C3-TOOL-ARGV": "a non-curl credential is in argv; use the tool's stdin, "
                    "protected file or prompt input, or document and waive "
                    "the CONTRIBUTING rule 7 argv-only exception",
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


def _strip_wrappers(cmd, env_credentials=None):
    # C3 opts into env option ownership; C1/C2 keep their existing walk.
    toks = list(cmd)
    while toks:
        t = toks[0]
        if t in KEYWORDS or ASSIGNMENT_RE.match(t):
            toks.pop(0); continue
        if t in REDIRECTS:
            toks = toks[2:]; continue
        if FD_RE.match(t) and len(toks) > 1 and toks[1] in REDIRECTS:
            toks = toks[3:]; continue
        if t.rsplit("/", 1)[-1] == "env" and env_credentials is not None:
            # The outermost env already owns every nested env URI operand.
            seen_uri = "URI credential" in env_credentials
            env_credentials.extend(
                flag for flag in _env_credential_flags(toks[1:])
                if flag != "URI credential" or not seen_uri)
            toks = _drop_redirections(toks[1:])
            toks = toks[_env_operand_start(toks):]
            continue
        if t in WRAPPERS or t.rsplit("/", 1)[-1] == "env":
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
            elif URL_USERINFO_RE.match(val) or SIGNED_URL_RE.search(val):
                codes.append("C3-URL-ARGV")
            continue
        if name in _CRED_PROXY_OPTS:
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
        if len(t) > 2 and not t.startswith("--") and t[:2] == "-x":
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


# C3-TOOL-ARGV: explicit tool/flag allowlist, independent of PROBE_CMDS.
# These flags accept credential values, including placeholders and expansions.
# OpenSSL 3.5: password sources (including the subcommand-specific names below)
# and enc's legacy -k password / -kfile filename:
# https://docs.openssl.org/3.5/man1/openssl-passphrase-options/
# https://docs.openssl.org/3.5/man1/openssl-enc/
# https://docs.openssl.org/3.5/man1/openssl-pkcs12/
# https://docs.openssl.org/3.5/man1/openssl-s_client/
# https://docs.openssl.org/3.5/man1/openssl-s_server/
# https://docs.openssl.org/3.5/man1/openssl-cmp/
# https://docs.openssl.org/3.5/man1/openssl-dgst/ (-macopt key:/hexkey:)
# "inline" options prompt without an attached value; "optional" options prompt
# without a following value. A dash is stdin ONLY for documented consumers.
_TOOL_SECRET_OPTS = {
    "lk": {"--api-key": "value", "--api-secret": "value"},
    "turnutils_uclient": {"-w": "value", "-W": "value"},
    "mysql": dict.fromkeys(("-p", "--password", "--password1",
                           "--password2", "--password3"), "inline"),
    "mariadb": {"-p": "inline", "--password": "inline"},
    "redis-cli": {"-a": "value", "--pass": "value",
                  "--cluster-from-pass": "value"},
    "mongosh": {"-p": "optional", "--password": "optional"},
    "clickhouse-client": {"--password": "optional"},
    "docker": {"-p": "stdin", "--password": "stdin"},
    "openssl": {
        **dict.fromkeys(("-pass", "-passin", "-passout", "-password",
                         "-passcerts", "-proxy_pass", "-dpass", "-secret",
                         "-keypass", "-newkeypass", "-otherpass", "-tls_keypass",
                         "-srv_secret", "-srv_keypass", "-rsp_keypass"), "source"),
        "-hmac": "value", "-k": "value",
    },
    "kubectl": {"--token": "value"},
    "influx": {"-t": "value", "--token": "value"},
    "cypher-shell": {"-p": "value", "--password": "value"},
    "mosquitto_pub": {"-P": "value", "--pw": "value"},
    "mosquitto_sub": {"-P": "value", "--pw": "value"},
}
# Bounded argument ownership, not a complete parser for every tool. Skip known
# non-secret option values so a flag-looking value is not reinterpreted.
_TOOL_SKIP_OPTS = {
    "lk": "--url --project --subdomain --config --room --identity --valid-for",
    "turnutils_uclient": "-u -e -p -r -L -d -i -k -z -l -n -m",
    "mysql": "-h --host -P --port -u --user -e --execute --ssl-ca",
    "mariadb": "-h --host -P --port -u --user -e --execute --ssl-ca",
    # Redis 7.4.2 parseOptions: values are not the command name.
    # https://raw.githubusercontent.com/redis/redis/7.4.2/src/redis-cli.c
    "redis-cli": "-h -p -s -n -r -i -d -D -u -t -X --user --cacert --cacertdir "
                 "--cert --key --sni --tls-ciphers --tls-ciphersuites "
                 "--pipe-timeout --show-pushes --lru-test --pattern --count "
                 "--quoted-pattern --intrinsic-latency --rdb --functions-rdb "
                 "--memkeys-samples --keystats-samples --cursor --top --eval "
                 "--test_hint --test_hint_file --cluster-replicas "
                 "--cluster-master-id --cluster-from --cluster-to "
                 "--cluster-from-user --cluster-weight --cluster-slots "
                 "--cluster-timeout --cluster-pipeline --cluster-threshold",
    "mongosh": "--host --port -u --username --eval --file --tlsCAFile "
               "--tlsCertificateKeyFile --authenticationDatabase "
               "--authenticationMechanism",
    "clickhouse-client": "--host --port --user --query --config-file",
    "docker": "-u --username --config -H --host --context",
    "openssl": "-in -out -key -cert -CAfile -connect -servername -subj -kfile",
    "kubectl": "-n --namespace --context --kubeconfig --user -o --output -f",
    "influx": "--host --host-url -o --org --org-id -c --active-config",
    "cypher-shell": "-a --address --uri -u --username -d --database -f --file",
    "mosquitto_pub": "-h --host -p --port -u --username -o -t --topic -m --message",
    "mosquitto_sub": "-h --host -p --port -u --username -o -t --topic",
    "mc": "--config-dir -C --api --path",
    "vault": "-method -path -address -namespace -format -field -ca-cert "
             "-ca-path -client-cert -client-key",
    "htpasswd": "-C -r",
    "mosquitto_passwd": "-H",
}


# Only known no-argument letters may precede a credential-taking short option.
# MySQL no-argument options; MariaDB uses the shared batch/quiet forms.
# https://dev.mysql.com/doc/refman/8.4/en/mysql-command-options.html
# https://mariadb.com/docs/server/clients-and-utilities/mariadb-client/mariadb-command-line-client
# Coturn 4.6.3 getopt string:
# https://github.com/coturn/coturn/blob/4.6.3/src/apps/uclient/mainuclient.c
_TOOL_CLUSTER_NOARG = {
    "mysql": "?ABCEGHLNTUVWXbcfijnoqrstvw", "mariadb": "BNsv",
    "turnutils_uclient": "bZvsyhcxXgtTSAPDNOUMRIGBJ",
}
# Vault login K=V credentials. '-' and '@path' use stdin and files.
# https://developer.hashicorp.com/vault/docs/commands#passing-command-arguments
# https://developer.hashicorp.com/vault/docs/auth/userpass
# https://developer.hashicorp.com/vault/docs/auth/github
# https://developer.hashicorp.com/vault/docs/auth/ldap
# https://developer.hashicorp.com/vault/docs/auth/okta
# https://developer.hashicorp.com/vault/docs/auth/radius
_VAULT_LOGIN_KEY = dict.fromkeys(("userpass", "ldap", "okta", "radius"), "password")
_VAULT_LOGIN_KEY.update(token="token", github="token")


# Whole URI arguments only. Mask simple shell parameter expansions before
# looking for URI delimiters, so ${PW:?} does not start a query.
_URI_PARAMETER_RE = re.compile(r"\$\{[^{}]*\}")
_URI_SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.I)
_URI_QUERY_KEYS = frozenset((
    "password", "passwd", "pass", "pwd", "sslpassword", "token", "secret",
    "accesstoken", "refreshtoken", "sessiontoken", "authtoken", "clientsecret",
    "apikey", "accesskey", "secretkey", "signature", "sig",
    "xamzsignature", "xgoogsignature",
))
# libpq accepts password and sslpassword in URI queries:
# https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING-URIS


def _uri_credential(value):
    """Visible URI userinfo or query credentials, without value dataflow.

    Only whole userinfo REPLACE_WITH_ passwords are exempt. Query credentials
    are checked independently, including when userinfo contains a placeholder.
    """
    value = _URI_PARAMETER_RE.sub("__PARAM__", value)
    if not _URI_SCHEME_RE.match(value):
        return False
    match = URL_USERINFO_RE.match(value)
    if match:
        password = match.group().split("://", 1)[1][:-1].split(":", 1)[1]
        if not re.fullmatch(re.escape(SENTINEL) + r"[A-Z0-9_]+", password):
            return True
    query = value.split("#", 1)[0].partition("?")[2]
    for pair in re.split(r"[&;]", query):
        key, eq, val = pair.partition("=")
        key = key.lower().replace("_", "").replace("-", "")
        if eq and val and key in _URI_QUERY_KEYS:
            return True
    return False


_ENV_CREDENTIAL_NAMES = frozenset((
    "MYSQL_PWD", "REDISCLI_AUTH", "PGPASSWORD",
    "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
))
_ENV_SECRET_RE = re.compile(
    r"(?:^|_)(?:SECRET|PASSWORD|PASSWD|TOKEN|PWD|PASS)(?:_|$)|"
    r"(?:^|_)(?:API|PRIVATE|ACCESS)_KEY$")
_ENV_NONSECRET_RE = re.compile(
    r"(?:_URL|_URI|_ENDPOINT|_HOST|_PORT|_PATH|_FILE|_DIR|_NAME|"
    r"_KEY_ID|_PUBLIC_KEY|_TTL|_TTL_SECONDS)$")
_ENV_VALUE_OPTS = frozenset(("-u", "--unset", "-C", "--chdir",
                            "-a", "--argv0", "-f", "--file"))
_ENV_NOARG_OPTS = frozenset((
    "-i", "--ignore-environment", "-v", "--debug", "-0", "--null",
    "--list-signal-handling", "--block-signal", "--default-signal",
    "--ignore-signal",
))
# env's lone '-' ends option processing like '-i --'. Signal names are
# optional attached values; -u/-C/-a/-f take required values.
# https://www.gnu.org/software/coreutils/manual/html_node/env-invocation.html
# -f/--file is a uutils extension:
# https://uutils.org/coreutils/docs/utils/env.html


def _env_operand_start(args):
    """Locate assignments without treating option values as assignments.

    Unknown options and split strings stop resolution: their ownership or
    injected command cannot be inferred. Never execute or expand a split string.
    """
    i = 0
    while i < len(args):
        t = args[i]
        if t in ("--", "-"):
            return i + 1
        if not t.startswith("-"):
            break
        opt, eq, _tail = t.partition("=")
        if opt in _ENV_VALUE_OPTS:
            i += 1 if eq else 2
        elif opt in _ENV_NOARG_OPTS:
            i += 1
        elif not t.startswith("--"):
            j = 1
            while j < len(t) and t[j] in "iv0":
                j += 1
            if j == len(t):
                i += 1
            elif "-" + t[j] in _ENV_VALUE_OPTS:
                i += 1 if j + 1 < len(t) else 2
            else:
                return len(args)
        else:
            return len(args)
    return i


def _env_credential_flags(args):
    """Check visible env argv URIs before resolving assignment ownership."""
    a = _drop_redirections(args)
    flags = [
        "URI credential" for t in a
        if _uri_credential(t) or ("=" in t and _uri_credential(t.split("=", 1)[1]))]
    for t in a[_env_operand_start(a):]:
        if not ASSIGNMENT_RE.match(t):
            break
        name, _, value = t.partition("=")
        upper = name.upper()
        secret_name = (
            upper not in ("KEY_ID", "PUBLIC_KEY", "PWD")
            and not _ENV_NONSECRET_RE.search(upper)
            and (upper in _ENV_CREDENTIAL_NAMES
                 or _ENV_SECRET_RE.search(upper)
                 or BODY_SECRET_RE.fullmatch(name + "=")
                 or CREDENTIAL_HEADER_RE.fullmatch(name.replace("_", "-"))))
        # A URI value was already counted, even under a credential name.
        if value and secret_name and not _uri_credential(value):
            flags.append(name)
    return flags


_URI_BUILTINS = frozenset(("printf", "echo", ":", "read"))


def _uri_builtin_context(cmd):
    """Credit only a visible shell builtin, never an external wrapper/path."""
    a = _drop_redirections(cmd)
    while a and (a[0] in KEYWORDS or ASSIGNMENT_RE.match(a[0])):
        a.pop(0)
    while a and a[0] in ("command", "builtin"):
        wrapper = a.pop(0)
        if wrapper == "command" and a[:1] == ["-p"]:
            a.pop(0)
        if a[:1] == ["--"]:
            a.pop(0)
    return bool(a) and a[0] in _URI_BUILTINS


def _uri_builtins_uncertain(records):
    """Visible shell mutation or builtin definitions deny fence-wide credit."""
    flat = [t for _line, _raw, lines, _waived in records
            for toks in lines for t in toks]
    for i, t in enumerate(flat):
        if t in ("enable", "alias", "unalias", "eval", "source", ".", "function"):
            return True
        if t in _URI_BUILTINS or t in ("command", "builtin"):
            tail = flat[i + 1:i + 3]
            if tail[:1] == ["()"] or tail == ["(", ")"]:
                return True
    return False


def _tool_credential_flags(word, args, shell_builtin=False):
    """Return flag names, never secret values. Reuse C3's value/redirection
    helpers and the shared command walk, wrappers, heredocs and waivers.

    Deliberately bounded: unknown option ownership, short clusters outside
    _TOOL_CLUSTER_NOARG, arbitrary positional
    secrets, expanded option names, aliases, shell strings and array-built
    commands remain outside this rule.
    In particular, sudo -u and timeout -s remain unresolved. env handles
    -/--, -i/-v/-0 clusters, --ignore-environment/--debug/--null,
    --list-signal-handling, --block-signal/--default-signal/--ignore-signal
    (optional =SIGNAL), and -u/-C/-a/-f or --unset/--chdir/--argv0/--file
    (separate or attached values). Unknown options, abbreviated long options,
    -S/--split-string and assignments from env files remain unresolved.
    Visible URI operands on env's own argv are checked before child resolution,
    including when split-string resolution stops the command walk.
    Env names match whole body names, header names and the explicit
    _ENV_CREDENTIAL_NAMES; generic _ENV_SECRET_RE words must be underscore-
    delimited components (case-insensitive).
    Bare AUTH, CREDENTIAL, CREDENTIALS, KEY and arbitrary application names
    are not covered. PWD (working directory), *_URL, *_URI, *_ENDPOINT,
    *_HOST, *_PORT, *_PATH, *_FILE, *_DIR, *_NAME, KEY_ID, *_KEY_ID,
    PUBLIC_KEY, *_PUBLIC_KEY, *_TTL and *_TTL_SECONDS are treated as metadata,
    unless their value visibly contains a credential URI. Other *_ID names
    retain credential-name matching, including SECRET_ID and TOKEN_ID.
    No value dataflow is done.
    Vault login checks only _VAULT_LOGIN_KEY's methods/keys; its known
    value-taking flags accept one/two dashes and =/separate values. Other
    flags, abbreviated names and options supplied through expansion are not
    parsed for ownership.
    URI checks cover whole arguments and NAME=URI/--option=URI values, not
    opaque URL variables, attached short-option URIs, schemeless userinfo,
    nested parameter expansions or URIs embedded in larger payloads.
    Simple ${...} expansions are masked before parsing delimiters. Query
    keys are exactly _URI_QUERY_KEYS, ignoring case, hyphens and underscores;
    percent-encoded keys, other key names and non-&/; separators are not
    recognized. Empty query values pass; query placeholders are not exempt.
    Userinfo requires a nonempty password and forbids literal /?#@ or space
    within it; encoded password characters are accepted without decoding.
    User-only URIs pass. Curl retains its existing URI policy and limits.
    URI operands of visible printf/echo/:/read builtins (also command -p/--
    and builtin --) pass, assuming ordinary shell builtins on entry. Paths
    and external wrappers remain checked. Visible alias/enable/eval/source,
    any function-keyword definition, printf/echo/:/read/command/builtin ()
    definitions and unparseable lines deny builtin credit for the whole fence;
    inherited shell redefinitions cannot be determined.
    Heredoc/herestring data follows the shared scanner's limits above.
    OpenSSL -macopt checks literal key:/hexkey: prefixes, not opaque values.
    Non-shell configuration fences retain the shared scanner's scope limit.
    A shell assignment prefix is distinct from an env argv value.
    Redis/Mosquitto and OpenSSL options require separate values (or the
    explicit equals form recognized here). Other supported short value options
    accept attached values. htpasswd handles -b clusters.
    Redis command data and htpasswd/mosquitto_passwd positional operands are
    never reinterpreted as options once the first positional word is reached.
    Redis --cluster instead permits CLI options after its operation/operands.
    OpenSSL source expansions are uncertain and flagged unless a literal
    file:/env:/fd: prefix or stdin establishes an out-of-argv input.
    """
    name = word.rsplit("/", 1)[-1]
    a = _drop_redirections(args)
    # Curl keeps its existing C3-URL-ARGV policy and diagnostics.
    uri_flags = [] if name == "curl" or shell_builtin else [
        "URI credential" for t in a
        if _uri_credential(t) or ("=" in t and _uri_credential(t.split("=", 1)[1]))]
    if name not in _TOOL_SKIP_OPTS:
        return uri_flags
    specs = _TOOL_SECRET_OPTS.get(name, {})
    skip = _TOOL_SKIP_OPTS[name].split()
    flags, positional, batch = list(uri_flags), [], ""
    method = "token"
    redis_cluster = False
    i = 0
    while i < len(a):
        t = a[i]
        if name == "redis-cli" and t == "--cluster":
            # Cluster-manager operands may precede further CLI options.
            redis_cluster = True
            i += 2  # the next word names the cluster operation
            continue
        if ((name in ("htpasswd", "mosquitto_passwd")
             or (name == "redis-cli" and not redis_cluster))
                and (not t.startswith("-") or t == "-")):
            # These tools stop parsing options at the first operand. Preserve
            # all subsequent words, including "--" and option-looking passwords
            # or Redis command data.
            positional.extend(a[i:])
            break
        if t == "--":
            positional.extend(a[i + 1:])
            break
        opt, eq, tail = t.partition("=")
        # Vault uses Go flag syntax, accepting one or two leading dashes.
        # https://pkg.go.dev/flag#hdr-Command_line_flag_syntax
        if name == "vault" and opt.startswith("--"):
            opt = opt[1:]
        mode = specs.get(opt)
        if name == "openssl" and opt == "-macopt":
            val, i = _cred_value(a, i, bool(eq), tail)
            if val:
                key, colon, value = val.partition(":")
                if colon and key in ("key", "hexkey") and value:
                    flags.append("-macopt " + key)
            continue
        if not mode and name in _TOOL_CLUSTER_NOARG and t.startswith("-"):
            j = 1
            while j < len(t) and t[j] in _TOOL_CLUSTER_NOARG[name]:
                j += 1
            short = "-" + t[j:j + 1]
            if j > 1 and short in specs:
                opt, mode, tail = short, specs[short], t[j + 1:]
                eq = bool(tail)  # required values may be the next word
        if not mode and t.startswith("-") and not t.startswith("--"):
            # Do not confuse OpenSSL's single-dash long options with shorts.
            short = t[:2]
            if (len(t) > 2 and short in specs
                    and name not in ("redis-cli", "mosquitto_pub",
                                     "mosquitto_sub", "openssl")):
                opt, mode, eq, tail = short, specs[short], True, t[2:]
        if mode:
            if not eq and mode == "inline":
                i += 1  # mysql -p db: db is a database, not a password
                continue
            if (not eq and mode == "optional"
                    and (i + 1 == len(a) or a[i + 1].startswith("-"))):
                i += 1
                continue
            val, i = _cred_value(a, i, bool(eq), tail)
            if not val:
                continue  # no secret value in argv
            if mode == "stdin" and val == "-":
                continue
            if mode == "source" and (
                    val == "stdin" or val.startswith(("file:", "env:", "fd:"))):
                continue
            if mode != "source" or val.startswith("pass:") or "$" in val or "__CMDSUB__" in val:
                flags.append(opt)
            continue
        if opt in skip:
            val, i = _cred_value(a, i, bool(eq), tail)
            if name == "vault" and opt == "-method":
                method = val
            continue
        if name in ("htpasswd", "mosquitto_passwd") and t.startswith("-") and t != "-":
            batch += t[1:]
        elif not t.startswith("-") or t == "-":
            positional.append(t)
        i += 1
    if name == "docker" and (not positional or positional[0] != "login"):
        return uri_flags  # docker run -p is port publication
    if name == "mc" and positional[:2] == ["alias", "set"]:
        flags.extend(label for label, val in zip(
            ("ACCESSKEY", "SECRETKEY"), positional[4:6]) if val)
    if name == "vault" and positional[:1] == ["login"]:
        credential = _VAULT_LOGIN_KEY.get(method)
        for val in positional[1:]:
            if "=" in val:
                key, _, val = val.partition("=")
                if key != credential:
                    continue
            elif method != "token":
                continue
            if val and val != "-" and not val.startswith("@"):
                flags.append(credential)
    if name in ("htpasswd", "mosquitto_passwd") and "b" in batch:
        at = 1 if name == "htpasswd" and "n" in batch else 2
        if len(positional) > at and positional[at]:
            flags.append("-b")
    return flags


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


_STRICT_VAR_RE = re.compile(
    r"\$(?:([0-9]|[A-Za-z_][A-Za-z0-9_]*)|\{([0-9]+|[A-Za-z_][A-Za-z0-9_]*)\})")


def _strict_tokens(text, toks):
    """Preserve uncertainty lost by quote removal, without changing the lexer."""
    marker = "\ue001"
    while marker in text:
        marker += "\ue001"
    marked, quote, i = [], None, 0
    while i < len(text):
        ch = text[i]
        if ch == "\\" and quote != "'" and i + 1 < len(text):
            if quote is None or text[i + 1] in ("$", '`'):
                marked.append(marker)
            marked.extend(text[i:i + 2])
            i += 2
            continue
        if ch in ("'", '"'):
            boundaries = " \t\r\n();<>|&"
            if quote is None:
                if i and text[i - 1] not in boundaries:
                    marked.append(marker)
                quote = ch
            elif quote == ch:
                if i + 1 < len(text) and text[i + 1] not in boundaries:
                    marked.append(marker)
                quote = None
        if ch == "$" and quote == "'":
            marked.append(marker)
        marked.append(ch)
        i += 1
    try:
        annotated = _tokenize("".join(marked))
    except ValueError:
        return [None] * len(toks)
    if [t.replace(marker, "") for t in annotated] != toks:
        return [None] * len(toks)
    return [None if marker in t else t for t in annotated]


def _strict_subject(word):
    match = _STRICT_VAR_RE.fullmatch(word) if word is not None else None
    return (match.group(1) or match.group(2)) if match else None


def _strict_operand_vars(args):
    # Include every argument variable, even option values: over-flagging is
    # preferable to silently omitting a placeholder-relevant operand.
    variables = set()
    for word in args:
        if (word is None or SENTINEL in word or "__CMDSUB__" in word
                or '`' in word):
            return None
        for match in _STRICT_VAR_RE.finditer(word):
            variables.add(match.group(1) or match.group(2))
        if "$" in _STRICT_VAR_RE.sub("", word):
            return None  # unsupported expansion, not a partial match
    return variables or None


def _strict_if_guards(path, records, probes, guarded_probes, findings):
    # Opt-in (--strict-guards): an if/elif mentioning the sentinel whose body
    # reaches fi without exit/return, with an uncovered probe after the fi.
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
        for pseq, plineno, name, waived in probes:
            if pseq not in guarded_probes and not waived and plineno > fi_line:
                findings.append((path, plineno, "C2-WARN-ONLY-GUARD",
                                 " (probe: %s)" % name))
                break


def _c2_literal_tokens(text, toks):
    """Return unquoted/unescaped flags aligned with the shared token list.

    Mark quoted or escaped words, tokenize with the existing tokenizer, then
    remove the marker and require exact agreement with the shared tokens.
    Failure is uncertainty, never permission to grant C2 coverage.
    """
    marker = "\ue000"
    while marker in text:
        marker += "\ue000"
    marked = []
    quote = None
    i = 0
    while i < len(text):
        ch = text[i]
        if quote is not None:
            marked.append(ch)
            if ch == quote:
                quote = None
            elif ch == "\\" and quote == '"' and i + 1 < len(text):
                i += 1
                marked.append(text[i])
        elif ch in ("'", '"'):
            quote = ch
            marked.extend((ch, marker))
        elif ch == "\\":
            marked.extend((marker, ch))
            if i + 1 < len(text):
                i += 1
                marked.append(text[i])
        elif ch == "#":
            marked.append(text[i:])
            break
        else:
            marked.append(ch)
        i += 1
    try:
        annotated = _tokenize("".join(marked))
    except ValueError:
        return None
    if [t.replace(marker, "") for t in annotated] != toks:
        return None
    return [marker not in t for t in annotated]


def _c2_shadows_termination(records):
    """Visible redefinitions deny every termination certificate in the fence.

    Quote removal is intentional here: quoted function names and alias
    assignments must also deny certification. Over-detection is safe.
    """
    flat = [t for _line, _raw, lines, _waived in records
            for toks in lines for t in toks]
    alias_seen = False
    for i, t in enumerate(flat):
        if t in SEPARATORS:
            alias_seen = False
        elif t == "alias":
            alias_seen = True
        if t in ("exit", "return"):
            tail = flat[i + 1:i + 3]
            if tail[:1] == ["()"] or tail == ["(", ")"]:
                return True
            if i and flat[i - 1] == "function":
                return True
        # Includes alias exit='...' and alias -- 'return=...'.
        # Never infer restoration from a later unalias/unset.
        if alias_seen and t.startswith(("exit=", "return=")):
            return True
    return False


def _analyze_fence(path, lang, start, body, findings, stats, opts):
    stats.fences += 1
    unparseable_before = stats.unparseable
    shell_heredoc_bodies = []
    if lang in CONSOLE_INFOS:
        lls = _logical_lines(_console_pairs(body, start), stats,
                             shell_heredoc_bodies)
    else:
        lls = _logical_lines([(start + j, ln) for j, ln in enumerate(body)],
                             stats, shell_heredoc_bodies)
    # Keep the shared physical command order, but tag each executable
    # heredoc with its own C2 domain, including recursively queued bodies.
    c2_origins = {line: 0 for line, _raw in lls}
    origin_count = 1
    while shell_heredoc_bodies:
        child_lines = _logical_lines(shell_heredoc_bodies.pop(0), stats,
                                     shell_heredoc_bodies)
        c2_origins.update((line, origin_count) for line, _raw in child_lines)
        origin_count += 1
        lls.extend(child_lines)
    lls.sort(key=lambda p: p[0])

    records = []  # (line, raw, [token list per expanded text], waived)
    c2_records = []  # aligned [(literal flags, lifted), ...]
    strict_records = []  # aligned tokens retaining unknown value references
    pending_waiver = False
    for lineno, raw in lls:
        wm = WAIVER_RE.search(raw)
        if wm and raw.lstrip().startswith("#") and wm.group(1).strip():
            pending_waiver = True
            stats.waivers += 1
            continue
        token_lines = []
        c2_lines = []
        strict_lines = []
        for expanded_no, text in enumerate(_expand(raw)):
            try:
                toks = _tokenize(text)
                token_lines.append(toks)
                c2_lines.append((_c2_literal_tokens(text, toks),
                                 expanded_no != 0))
                strict_lines.append(
                    _strict_tokens(text, toks) if opts.strict_guards else toks)
            except ValueError:
                stats.unparseable += 1
        records.append((lineno, raw, token_lines, pending_waiver))
        c2_records.append(c2_lines)
        strict_records.append(strict_lines)
        if raw.strip():
            pending_waiver = False

    termination_shadowed = _c2_shadows_termination(records)
    uri_builtins_uncertain = (
        stats.unparseable > unparseable_before
        or _uri_builtins_uncertain(records))

    # The shared command walk and sequence numbering are retained. Everything
    # added to its structural bookkeeping below belongs to C2.
    seq = 0
    probes = []          # (seq, line, name, waived)
    curl_findings = []   # (line, code, waived)
    case_stack = []
    guard_spans = []
    probe_exclusions = {}
    probe_domains = {}
    probe_operands = {}
    array_depth = 0
    in_dbrackets = False
    c2_array_depth = 0
    c2_uncertain = False
    saw_sentinel = False
    funcdef_pending = False
    in_compound_stmt = False
    continuation = False
    live_handles = []
    inherited_exclusions = set()
    buf_is_literal = True
    boundary_literal = True

    def new_scope(kind, function_body=False, eligible=True):
        return {
            "id": object(),
            "kind": kind,
            "open_seq": seq,
            "deferred": [],
            "block_depth": 0,
            "function_body": function_body,
            "eligible": eligible,
            "valid": True,
            "closed": False,
        }

    fence = new_scope("fence")
    nest = [fence]

    def save_c2_state():
        return (fence, nest, case_stack, funcdef_pending,
                in_compound_stmt, continuation, live_handles,
                inherited_exclusions, c2_array_depth)

    def restore_c2_state(state):
        nonlocal fence, nest, case_stack, funcdef_pending
        nonlocal in_compound_stmt, continuation, live_handles
        nonlocal inherited_exclusions, c2_array_depth
        (fence, nest, case_stack, funcdef_pending,
         in_compound_stmt, continuation, live_handles,
         inherited_exclusions, c2_array_depth) = state

    origin_states = {}
    active_origin = 0

    def current_scope():
        return next(f for f in reversed(nest) if f["kind"] != "case")

    def kill_arms(revoke=False):
        for f in case_stack:
            arm = f["arm"]
            if arm is not None and arm["active"]:
                arm["clean_prefix"] = False
                if revoke:
                    arm["exits"] = False

    def finish_arm(f, terminator):
        arm = f["arm"]
        if terminator in (";&", ";;&"):
            f["has_nonstandard_terminator"] = True
        certified = (
            terminator in (";;", "esac") and arm is not None
            and arm["owner"] is f["id"] and arm["active"] and arm["exits"])
        if certified:
            if arm["sentinel"]:
                f["sentinel_certified"] += 1
            f["uses_return"] = f["uses_return"] or arm["uses_return"]
        if arm is not None:
            if (arm["before_effective"] and arm["may_overlap"]
                    and not certified):
                f["preempted"] = True
            arm["active"] = False
        f["current_sentinel"] = False

    def finish_scope(f, end_seq):
        f["closed"] = True
        if f["block_depth"]:
            f["valid"] = False
        for span in f["deferred"]:
            if (not span["revoked"]
                    and all(s["valid"] for s in span["scopes"])
                    and all(s["closed"] for s in span["chain"])):
                span["end"] = end_seq

    def commit(cmd, line, waived, strict_cmd):
        nonlocal seq, live_handles
        seq += 1
        if cmd[0] == "case":
            return
        if cmd[0] == "esac":
            if case_stack and buf_is_literal and boundary_literal:
                f = case_stack.pop()
                if nest[-1] is not f or cmd != ["esac"]:
                    f["valid"] = False
                finish_arm(f, "esac")
                nest[:] = [n for n in nest if n is not f]
                # C2 hardening hook 1: fallthrough cases grant no span.
                deny_span = (_C2_HARDENING
                             and f["has_nonstandard_terminator"])
                if (f["valid"] and f["effective_seen"]
                        and not f["preempted"] and not deny_span):
                    span = {
                        "case_id": f["id"],
                        "subject": f["subject"],
                        "domain": active_origin,
                        "start": f["start"],
                        "esac": seq,
                        "end": seq,
                        "revoked": False,
                        "scopes": f["scopes"],
                        "chain": (),
                    }
                    guard_spans.append(span)
                    certified = (
                        f["sentinel_certified"] == f["sentinel_seen"]
                        and not f["has_nonstandard_terminator"])
                    eligible = (
                        f["eligible"]
                        and all(s["valid"] and s["eligible"]
                                and s["block_depth"] == 0
                                for s in f["scopes"]))
                    target = None
                    if certified and eligible:
                        if f["uses_return"]:
                            candidate = f["scopes"][-1]
                            if candidate["function_body"]:
                                target = candidate
                        else:
                            target = next(
                                (s for s in reversed(f["scopes"])
                                 if s["kind"] in ("subshell", "fence")
                                 or s["function_body"]),
                                None)
                    if target is not None:
                        target_at = next(
                            i for i, s in enumerate(f["scopes"])
                            if s is target)
                        span["chain"] = f["scopes"][target_at:]
                        target["deferred"].append(span)
                        live_handles = [span]
            return

        # C2 certificate: inspect the original buffer, before wrapper or
        # redirection stripping. A quoted separator is not a command boundary.
        exact_status = len(cmd) == 1
        if len(cmd) == 2 and _C2_STATUS_RE.fullmatch(cmd[1]):
            decimal = cmd[1].lstrip("0") or "0"
            exact_status = len(decimal) <= 3 and int(decimal) <= 255
        if (not termination_shadowed
                and cmd[0] in ("exit", "return") and exact_status
                and buf_is_literal and boundary_literal and case_stack):
            f = case_stack[-1]
            arm = f["arm"]
            if (arm is not None and arm["active"]
                    and arm["owner"] is f["id"]
                    and len(nest) == arm["base_depth"]
                    and arm["clean_prefix"]):
                target = current_scope()
                if cmd[0] == "exit" or target["function_body"]:
                    arm["exits"] = True
                    arm["uses_return"] = (
                        arm["uses_return"] or cmd[0] == "return")

        env_credentials = []
        stripped = _strip_wrappers(cmd, env_credentials)
        if not waived:
            for flag in env_credentials:
                findings.append((path, line, "C3-TOOL-ARGV",
                                 " (tool: env, argument: %s)" % flag))
        if stripped:
            word = stripped[0]
            shell_builtin = (not uri_builtins_uncertain
                             and _uri_builtin_context(cmd))
            for flag in _tool_credential_flags(word, stripped[1:], shell_builtin):
                if flag == "URI credential" and flag in env_credentials:
                    continue  # already checked on the outer env's argv
                if not waived:
                    findings.append((path, line, "C3-TOOL-ARGV",
                                     " (tool: %s, argument: %s)"
                                     % (word.rsplit("/", 1)[-1], flag)))
        # The broader env resolution above belongs only to C3-TOOL-ARGV.
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
            probe_domains[seq] = active_origin
            if opts.strict_guards:
                # _strip_wrappers returns a suffix of cmd; preserve alignment.
                probe_operands[seq] = _strict_operand_vars(
                    strict_cmd[len(cmd) - len(stripped) + 1:])
            # C2 hardening hook 2: a sentinel arm cannot protect its own probe.
            probe_exclusions[seq] = inherited_exclusions | {
                f["id"] for f in case_stack if f["current_sentinel"]
            }

    for record_no, (lineno, _raw, token_lines, waived) in enumerate(records):
        origin = c2_origins[lineno]
        if origin != active_origin:
            origin_states[active_origin] = save_c2_state()
            if origin not in origin_states:
                child = new_scope("fence")
                origin_states[origin] = (
                    child, [child], [], False, False, False, [], set(), 0)
            restore_c2_state(origin_states[origin])
            active_origin = origin
        raw_substitution = "$(" in _raw or "`" in _raw
        row_exclusions = inherited_exclusions | {
            f["id"] for f in case_stack if f["current_sentinel"]
        }
        for token_no, toks in enumerate(token_lines):
            literals, lifted = c2_records[record_no][token_no]
            strict_toks = strict_records[record_no][token_no]
            if literals is None:
                literals = [False] * len(toks)
                c2_uncertain = True
                kill_arms(revoke=True)

            # A lifted body shares the existing command numbering and C1/C3
            # scanner, but none of the parent's C2 execution state.
            saved = None
            if lifted:
                saved = save_c2_state()
                fence = new_scope("subshell")
                nest = [fence]
                case_stack = []
                funcdef_pending = False
                in_compound_stmt = False
                continuation = False
                live_handles = []
                inherited_exclusions = set(row_exclusions)
                c2_array_depth = 0

            # A completed statement's newline ends the compound flag.
            # An unfinished &&, ||, | or |& still conditions the next line.
            in_compound_stmt = continuation
            continuation = False
            live_handles = []
            if raw_substitution:
                kill_arms(revoke=True)

            buf = []
            strict_buf = []
            buf_is_literal = True
            boundary_literal = True
            k = 0
            while k < len(toks):
                t = toks[k]
                literal = literals[k]
                if raw_substitution or "$(" in t or "`" in t:
                    kill_arms(revoke=True)

                # C2's array boundary check uses quote metadata. The existing
                # shared array scanner immediately below remains unchanged.
                if c2_array_depth and literal:
                    if t == "(":
                        c2_array_depth += 1
                    elif t == ")":
                        c2_array_depth -= 1
                if array_depth:
                    if t == "(":
                        array_depth += 1
                    elif t == ")":
                        array_depth -= 1
                    if bool(array_depth) != bool(c2_array_depth):
                        c2_uncertain = True
                    k += 1
                    continue
                if in_dbrackets:
                    if t == "]]":
                        in_dbrackets = False
                        buf = []
                        strict_buf = []
                        buf_is_literal = True
                        if not literal:
                            c2_uncertain = True
                    k += 1
                    continue
                if t == "[[":
                    kill_arms()
                    if not literal:
                        c2_uncertain = True
                    in_dbrackets = True
                    k += 1
                    continue
                if (t == "(" and buf and buf[-1].endswith("=")
                        and ASSIGNMENT_RE.match(buf[-1])):
                    buf.pop()
                    strict_buf.pop()
                    array_depth = 1
                    c2_array_depth = 1 if literal else 0
                    if not literal:
                        c2_uncertain = True
                    kill_arms()
                    k += 1
                    continue
                if (literal and t == "()" and len(buf) == 1
                        and buf[0] not in KEYWORDS):
                    kill_arms()
                    funcdef_pending = literal and buf_is_literal
                    strict_buf = []
                    buf = []  # `name ()` function definition, not a command
                    buf_is_literal = True
                    k += 1
                    continue
                if (literal and t == "(" and len(buf) == 1 and buf[0] not in KEYWORDS
                        and k + 1 < len(toks) and toks[k + 1] == ")"):
                    kill_arms()
                    funcdef_pending = (
                        literal and literals[k + 1] and buf_is_literal)
                    buf = []
                    strict_buf = []
                    buf_is_literal = True
                    k += 2
                    continue

                function_body = (
                    funcdef_pending and literal and t in ("(", "{"))
                funcdef_pending = False
                pattern_case = None
                if (literal and t == ")" and nest[-1]["kind"] == "case"
                        and nest[-1]["in_pattern"]):
                    pattern_case = nest[-1]
                pattern_open = (
                    literal and t == "(" and nest[-1]["kind"] == "case"
                    and nest[-1]["in_pattern"])

                # Accumulate the entire arm pattern, across alternatives
                # and logical lines. Header operands before 'in' do not count.
                if nest[-1]["kind"] == "case" and nest[-1]["in_pattern"]:
                    f = nest[-1]
                    if not f["pattern_started"]:
                        if literal and t == "in":
                            f["pattern_started"] = True
                    elif not (literal and t in ("(", ")", "|")):
                        f["pattern_tokens"].append((t, literal))

                if t in SEPARATORS:
                    if buf:
                        boundary_literal = literal
                        commit(buf, lineno, waived, strict_buf)
                        buf = []
                        strict_buf = []
                        buf_is_literal = True
                        boundary_literal = True
                    continuation = False
                    if not literal:
                        # The shared scanner still treats this as a separator.
                        # C2 must not mistake that split for shell structure.
                        kill_arms(revoke=True)
                        for span in live_handles:
                            span["revoked"] = True
                            span["end"] = span["esac"]
                        live_handles = []
                        k += 1
                        continue

                    if pattern_case is not None:
                        f = pattern_case
                        patterns = f["pattern_tokens"]
                        sentinel = any(
                            SENTINEL in word
                            and PATTERN_TOKEN_RE.fullmatch(word) is not None
                            for word, _is_literal in patterns)
                        # A deliberately small accepted language: an unquoted
                        # marker with unrestricted stars on both sides, no
                        # bracket expressions, expansions or pinned affixes.
                        effective = any(
                            is_literal
                            and _C2_SENTINEL_GLOB_RE.fullmatch(word) is not None
                            for word, is_literal in patterns)
                        # Only simple fixed strings without the marker are
                        # proven disjoint. Wildcards, expansions, quote/escape
                        # ambiguity and unfamiliar syntax may overlap.
                        may_overlap = not patterns or any(
                            SENTINEL in word
                            or _C2_PLAIN_PATTERN_RE.fullmatch(word) is None
                            for word, _is_literal in patterns)
                        before_effective = not f["effective_seen"] and not effective
                        if effective:
                            f["effective_seen"] += 1
                        f["in_pattern"] = False
                        f["current_sentinel"] = sentinel
                        f["arm"] = {
                            "owner": f["id"],
                            "active": True,
                            "sentinel": sentinel,
                            "before_effective": before_effective,
                            "may_overlap": may_overlap,
                            "base_depth": len(nest),
                            # Retain the conservative refusal to certify
                            # ineffective sentinel lookalikes, even with exit.
                            "clean_prefix": effective or not sentinel,
                            "exits": False,
                            "uses_return": False,
                        }
                        if sentinel:
                            f["sentinel_seen"] += 1
                            saw_sentinel = True
                            row_exclusions.add(f["id"])
                        in_compound_stmt = False
                        live_handles = []
                    elif pattern_open:
                        # POSIX's optional '(' before a case pattern.
                        live_handles = []
                    elif t in (";;", ";&", ";;&"):
                        if case_stack:
                            f = case_stack[-1]
                            if nest[-1] is not f:
                                f["valid"] = False
                            finish_arm(f, t)
                            f["in_pattern"] = True
                            f["pattern_started"] = True
                            f["pattern_tokens"] = []
                        in_compound_stmt = False
                        live_handles = []
                    elif t in _C2_COMPOUND:
                        # Flush happened above: revoke even an exit that
                        # committed immediately before this separator.
                        kill_arms(revoke=True)
                        for span in live_handles:
                            span["revoked"] = True
                            span["end"] = span["esac"]
                        live_handles = []
                        in_compound_stmt = True
                        continuation = t in _C2_CONTINUATION
                    elif t == ";":
                        in_compound_stmt = False
                        live_handles = []
                    elif t in ("(", "{"):
                        kill_arms()
                        nest.append(new_scope(
                            "subshell" if t == "(" else "brace",
                            function_body=function_body,
                            eligible=not in_compound_stmt))
                        live_handles = []
                    elif t in (")", "}"):
                        expected = "subshell" if t == ")" else "brace"
                        if len(nest) > 1 and nest[-1]["kind"] == expected:
                            f = nest.pop()
                            finish_scope(f, seq)
                            # Keep exported brace deferrals revocable when
                            # the whole enclosing group has a trailing list
                            # or pipeline/background operator.
                            live_handles = [
                                span for span in guard_spans
                                if span["chain"] and any(
                                    s is f for s in span["scopes"])
                            ]
                        else:
                            c2_uncertain = True
                            for f in case_stack:
                                f["valid"] = False
                            live_handles = []
                else:
                    # Retain revocation handles through trailing redirections
                    # and their operands. Only a real statement boundary or
                    # disposition settles the preceding compound command.
                    continuation = False
                    at_command_start = all(x in KEYWORDS for x in buf)
                    if literal and at_command_start:
                        scope = current_scope()
                        if t in _C2_BLOCK_OPEN:
                            scope["block_depth"] += 1
                        elif t in _C2_BLOCK_CLOSE:
                            if scope["block_depth"] == 0:
                                scope["valid"] = False
                            scope["block_depth"] = max(
                                0, scope["block_depth"] - 1)
                    if literal and t in _C2_ARM_KILL:
                        kill_arms()
                    if (literal and t == "case"
                            and all(x in KEYWORDS for x in buf)):
                        scopes = tuple(
                            f for f in nest if f["kind"] != "case")
                        f = {
                            "id": object(),
                            "kind": "case",
                            "subject": (
                                _strict_subject(strict_toks[k + 1])
                                if opts.strict_guards and k + 2 < len(toks)
                                and toks[k + 2] == "in" and literals[k + 2]
                                else None),
                            "start": seq + 1,
                            "scopes": scopes,
                            "eligible": (
                                not case_stack and not in_compound_stmt
                                and all(s["block_depth"] == 0
                                        and s["eligible"] and s["valid"]
                                        for s in scopes)),
                            "sentinel_seen": 0,
                            "effective_seen": 0,
                            "preempted": False,
                            "sentinel_certified": 0,
                            "has_nonstandard_terminator": False,
                            "valid": True,
                            "in_pattern": True,
                            "pattern_started": False,
                            "pattern_tokens": [],
                            "current_sentinel": False,
                            "arm": None,
                            "uses_return": False,
                        }
                        case_stack.append(f)
                        nest.append(f)
                    buf.append(t)
                    strict_buf.append(strict_toks[k])
                    buf_is_literal = buf_is_literal and literal
                k += 1
            if buf:
                boundary_literal = True
                commit(buf, lineno, waived, strict_buf)

            if lifted:
                # Inclusive end: the next parent command gets seq + 1 and
                # cannot be covered by this lifted body's certificate.
                finish_scope(fence, seq)
                restore_c2_state(saved)

    # Only the implicit fence is closed here. Still-open cases grant nothing;
    # scope-trapped deferrals retain their original short end.
    origin_states[active_origin] = save_c2_state()
    for state in origin_states.values():
        finish_scope(state[0], seq + 1)
        if state[-1]:
            c2_uncertain = True
    if array_depth or in_dbrackets:
        c2_uncertain = True
    for span in guard_spans:
        if (span["chain"]
                and (not all(s["closed"] for s in span["chain"])
                     or not all(s["valid"] for s in span["scopes"]))):
            span["end"] = span["esac"]

    # Keep main C2 coverage unchanged. Strict mode refines it below, even
    # under --no-c2 or when no sentinel activates the default C2 diagnostic.
    unguarded_probes = set()
    for pseq, _lineno, _name, _waived in probes:
        excluded = (probe_exclusions.get(pseq, set())
                    if _C2_HARDENING else set())
        if not any(
                not c2_uncertain
                and span["domain"] == probe_domains[pseq]
                and span["case_id"] not in excluded
                and span["start"] < pseq <= span["end"]
                for span in guard_spans):
            unguarded_probes.add(pseq)

    for lineno, code, waived in curl_findings:
        if not waived:
            findings.append((path, lineno, code, ""))
    if saw_sentinel:
        stats.guard_fences += 1
        if not opts.no_c2:
            for pseq, lineno, name, waived in probes:
                if not waived and pseq in unguarded_probes:
                    findings.append((path, lineno, "C2-PROBE-OUTSIDE-GUARD",
                                     " (probe: %s)" % name))
    if opts.strict_guards:
        guarded_probes = set()
        for pseq, _lineno, _name, _waived in probes:
            operands = probe_operands[pseq]
            if pseq in unguarded_probes or not operands:
                continue
            subjects = {
                span["subject"] for span in guard_spans
                if span["domain"] == probe_domains[pseq]
                and span["case_id"] not in probe_exclusions.get(pseq, set())
                and span["start"] < pseq <= span["end"]
                and span["subject"] is not None
            }
            if operands <= subjects:
                guarded_probes.add(pseq)
        _strict_if_guards(path, records, probes, guarded_probes, findings)


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
     [], ()),
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
    ("strict-mosquitto-case-guard-clean",
     r"""```bash
if mosquitto_sub -P 'REPLACE_WITH_DEVICE_PASSWORD'; then
  echo "connected"
else
  echo "check CONNACK"
fi
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste whole block"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "need one value"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute host";;
    *) nc -vz -w 5 "$1" 1883 || true;;
  esac
)
```
""", ["C3-TOOL-ARGV"], ("--strict-guards",)),
    ("strict-mosquitto-case-guard-clean-no-c2",
     r"""```bash
if mosquitto_sub -P 'REPLACE_WITH_DEVICE_PASSWORD'; then
  echo "connected"
else
  echo "check CONNACK"
fi
(
  set -- PASTE_WHOLE_BLOCK 'REPLACE_WITH_HOST'
  [ "${1-}" = PASTE_WHOLE_BLOCK ] || { echo "paste whole block"; exit; }
  shift
  [ "$#" -eq 1 ] || { echo "need one value"; exit; }
  case "$1" in
    *REPLACE_WITH_*|"") echo "substitute host";;
    *) nc -vz -w 5 "$1" 1883 || true;;
  esac
)
```
""", ["C3-TOOL-ARGV"], ("--strict-guards", "--no-c2")),
    ("strict-skips-guarded-probe-flags-unguarded",
     r"""```bash
if [ "$1" = REPLACE_WITH_HOST ]; then
  echo "warning"
fi
case "$1" in
  *REPLACE_WITH_*|"") echo "substitute host";;
  *) nc -vz -w 5 "$1" 1883;;
esac
nc -vz -w 5 "$1" 1883
```
""", ["C2-PROBE-OUTSIDE-GUARD", "C2-WARN-ONLY-GUARD"],
     ("--strict-guards",)),
    ("strict-unguarded-probe-still-flagged-no-c2",
     r"""```bash
if [ "$1" = REPLACE_WITH_HOST ]; then
  echo "warning"
fi
nc -vz -w 5 "$1" 1883
```
""", ["C2-WARN-ONLY-GUARD"], ("--strict-guards", "--no-c2")),
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
    ("c3-referer-not-scanned-scheme-less-is-proxy-only",
     "```bash\ncurl -q --referer 'mailto:help@example.com' https://h/\n"
     "curl -q -e 'https://ref/?sig=x' https://h/\n```\n", [], ()),
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


SELF_TEST_CASES += [
    ("exit-guard-top-level",
     "```bash\n"
     "case \"$1\" in *REPLACE_WITH_T*) echo 'edit target' >&2; exit 2;; esac\n"
     "curl -q -g -- \"$1\"\n"
     "curl -q -g -- \"$1\"\n"
     "```\n", [], ()),

    ("exit-guard-own-scope-and-outer-probe",
     "```bash\n"
     "(\n"
     "  case \"$1\" in *REPLACE_WITH_T*) exit 2;; esac\n"
     "  curl -q -g -- \"$1\"\n"
     ")\n"
     "curl -q -g \"https://fixed.example/\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("return-arm-terminates-in-subshell",
     "```bash\n"
     "run() (\n"
     "  case \"$1\" in *REPLACE_WITH_T*) echo warn >&2; return 1;; esac\n"
     "  curl -q -g \"https://$1/healthz\"\n"
     ")\n"
     "```\n", [], ()),

    ("return-guard-function-boundary",
     "```bash\n"
     "check_target() {\n"
     "  case \"$1\" in *REPLACE_WITH_T*) echo 'edit target' >&2; return 2;; esac\n"
     "  curl -q -g -- \"$1\"\n"
     "}\n"
     "check_target \"$1\"\n"
     "curl -q -g \"https://fixed.example/\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("return-without-function-context",
     "```bash\n"
     "(\n"
     "  case \"$1\" in *REPLACE_WITH_T*) return 2;; esac\n"
     "  curl -q -g -- \"$1\"\n"
     ")\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("conditional-and-exit",
     "```bash\n"
     "case \"$1\" in\n"
     "  *REPLACE_WITH_T*) [ -n \"$x\" ] && exit 2;;\n"
     "esac\n"
     "curl -q -g -- \"$1\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("conditional-if-exit",
     "```bash\n"
     "case \"$1\" in\n"
     "  *REPLACE_WITH_T*) if [ -n \"$x\" ]; then exit 2; fi;;\n"
     "esac\n"
     "curl -q -g -- \"$1\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("nested-subshell-exit-is-not-arm-exit",
     "```bash\n"
     "case \"$1\" in\n"
     "  *REPLACE_WITH_T*) ( exit 2 ); echo 'still running';;\n"
     "esac\n"
     "curl -q -g -- \"$1\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("substitution-exit-is-not-arm-exit",
     "```bash\n"
     "case \"$1\" in\n"
     "  *REPLACE_WITH_T*) message=$(exit 2); echo 'still running';;\n"
     "esac\n"
     "curl -q -g -- \"$1\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("pipeline-exit-is-not-arm-exit",
     "```bash\n"
     "case \"$1\" in\n"
     "  *REPLACE_WITH_T*) exit 2 | cat;;\n"
     "esac\n"
     "curl -q -g -- \"$1\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("background-guard-does-not-protect-parent",
     "```bash\n"
     "case \"$1\" in *REPLACE_WITH_T*) exit 2;; esac &\n"
     "wait\n"
     "curl -q -g -- \"$1\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("conditional-guard-can-be-skipped",
     "```bash\n"
     "if false; then\n"
     "  case \"$1\" in *REPLACE_WITH_T*) exit 2;; esac\n"
     "fi\n"
     "curl -q -g -- \"$1\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("continue-and-break-are-not-scope-exits",
     "```bash\n"
     "(\n"
     "  for item in one; do\n"
     "    case \"$1\" in *REPLACE_WITH_T*) echo 'skip'; continue;; esac\n"
     "  done\n"
     "  curl -q -g -- \"$1\"\n"
     ")\n"
     "(\n"
     "  while :; do\n"
     "    case \"$1\" in *REPLACE_WITH_T*) echo 'stop loop'; break;; esac\n"
     "    break\n"
     "  done\n"
     "  curl -q -g -- \"$1\"\n"
     ")\n"
     "```\n",
     ["C2-PROBE-OUTSIDE-GUARD", "C2-PROBE-OUTSIDE-GUARD"], ()),

    ("loop-continue-not-terminating",
     "```bash\n"
     "for h in a b; do\n"
     "  case \"$1\" in *REPLACE_WITH_T*) echo skip >&2; continue;; esac\n"
     "  curl -q -g \"https://$1/$h\"\n"
     "done\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("multiple-sequential-exit-guards",
     "```bash\n"
     "(\n"
     "  case \"$1\" in *REPLACE_WITH_A*) exit 2;; esac\n"
     "  curl -q -g -- \"$1\"\n"
     "  case \"$2\" in *REPLACE_WITH_B*) exit 2;; esac\n"
     "  curl -q -g -- \"$2\"\n"
     ")\n"
     "```\n", [], ()),

    ("every-sentinel-arm-must-terminate",
     "```bash\n"
     "case \"$1\" in\n"
     "  *REPLACE_WITH_A*) exit 2;;\n"
     "  *REPLACE_WITH_B*) echo 'edit B';;\n"
     "  *) :;;\n"
     "esac\n"
     "curl -q -g -- \"$1\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("exit-in-default-arm-does-not-count",
     "```bash\n"
     "case \"$1\" in\n"
     "  *REPLACE_WITH_T*) echo 'edit target';;\n"
     "  *) exit 2;;\n"
     "esac\n"
     "curl -q -g -- \"$1\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("nested-case-exit-does-not-certify-outer-arm",
     "```bash\n"
     "case \"$1\" in\n"
     "  *REPLACE_WITH_T*)\n"
     "    case \"$x\" in\n"
     "      yes) exit 2;;\n"
     "      *) echo 'still running';;\n"
     "    esac\n"
     "    ;;\n"
     "esac\n"
     "curl -q -g -- \"$1\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("quoted-exit-is-diagnostic-text",
     "```bash\n"
     "case \"$1\" in\n"
     "  *REPLACE_WITH_T*) printf '%s\\n' 'exit 2';;\n"
     "esac\n"
     "curl -q -g -- \"$1\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("wrapped-exit-does-not-count",
     "```bash\n"
     "case \"$1\" in\n"
     "  *REPLACE_WITH_T*) env exit 2;;\n"
     "esac\n"
     "curl -q -g -- \"$1\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("invalid-exit-arguments-do-not-count",
     "```bash\n"
     "case \"$1\" in\n"
     "  *REPLACE_WITH_T*) exit 2 extra;;\n"
     "esac\n"
     "curl -q -g -- \"$1\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("exit-redirection-can-prevent-execution",
     "```bash\n"
     "case \"$1\" in\n"
     "  *REPLACE_WITH_T*) exit 2 > /dev/null/impossible;;\n"
     "esac\n"
     "curl -q -g -- \"$1\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("scope-parentheses-disambiguation",
     "```bash\n"
     "(\n"
     "  case \"$1\" in\n"
     "    (''|*REPLACE_WITH_T*) echo 'edit target'; exit 2;;\n"
     "    (*) :;;\n"
     "  esac\n"
     "  values=( \"(\" \")\" \"exit\" )\n"
     "  [[ \"(\" == \")\" ]] || :\n"
     "  helper() { :; }\n"
     "  helper_spaced ( ) { :; }\n"
     "  curl -q -g -- \"$1\"\n"
     ")\n"
     "curl -q -g \"https://fixed.example/\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("sibling-scopes-do-not-share-certificates",
     "```bash\n"
     "(\n"
     "  case \"$1\" in *REPLACE_WITH_T*) exit 2;; esac\n"
     "  curl -q -g -- \"$1\"\n"
     ")\n"
     "(\n"
     "  curl -q -g -- \"$1\"\n"
     ")\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("subshell-arm-boundary-tracked",
     "```bash\n"
     "(\n"
     "  case \"$1\" in *REPLACE_WITH_T*) exit 1;; esac\n"
     "  ( curl -q -g \"https://$1/nested\" )\n"
     ")\n"
     "curl -q -g \"https://$1/outer\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("uncalled-function-exit-guard",
     "```bash\n"
     "check_target() {\n"
     "  case \"$1\" in *REPLACE_WITH_T*) exit 2;; esac\n"
     "}\n"
     "curl -q -g -- \"$1\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("function-def-in-arm-does-not-certify",
     "```bash\n"
     "case \"$1\" in\n"
     "  *REPLACE_WITH_T*) trap_exit() { exit 1; }; echo warn;;\n"
     "esac\n"
     "curl -q -g -- \"$1\"\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("sentinel-fallthrough-reaches-default-probe",
     "```bash\n"
     "case \"$1\" in\n"
     "  *REPLACE_WITH_T*) echo 'edit target';&\n"
     "  *) curl -q -g -- \"$1\";;\n"
     "esac\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("probe-in-sentinel-arm-is-not-protected",
     "```bash\n"
     "case \"$1\" in\n"
     "  *REPLACE_WITH_T*) echo 'edit target'; curl -q -g -- \"$1\";;\n"
     "  *) :;;\n"
     "esac\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("unterminated-case-grants-no-coverage",
     "```bash\n"
     "case \"$1\" in\n"
     "  *REPLACE_WITH_T*) exit 2;;\n"
     "  *) curl -q -g -- \"$1\";;\n"
     "```\n", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("no-c2-suppresses-new-conditional-diagnostic",
     "```bash\n"
     "case \"$1\" in\n"
     "  *REPLACE_WITH_T*) [ -n \"$x\" ] && exit 2;;\n"
     "esac\n"
     "curl -q -g -- \"$1\"\n"
     "```\n", [], ("--no-c2",)),
]


# Additional C2 line assertions; fixture tuples retain their existing format.
SELF_TEST_CASES += [
    ("fn-a-placeholder-first-warn",
     r"""```bash
case "$1" in
  *REPLACE_WITH_T*|"") echo 'edit target first' >&2 ;;
esac
curl -q -g "https://$1/healthz"
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("fn-a-placeholder-first-exit",
     r"""```bash
case "$1" in
  *REPLACE_WITH_T*|"") exit 2 ;;
esac
curl -q -g "https://$1/healthz"
```
""", [], ()),

    ("fn-b-heredoc-child-guard",
     r"""```bash
bash -s -- "$1" <<'SH'
case "$1" in *REPLACE_WITH_T*) exit 2;; esac
SH
curl -q -g -w "PROBE_RAN\n" -- "$1"
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("fn-b-heredoc-script-exit",
     r"""```bash
case "$A" in
  *REPLACE_WITH_*)
    cat <<'EOF' > script.sh
exit 1
EOF
    ;;
esac
curl $A
```
""", ["C1-MISSING-Q", "C2-PROBE-OUTSIDE-GUARD"], ()),

    ("fn-c-quoted-separator",
     r"""```bash
case "$1" in
  *REPLACE_WITH_T*) printf '%s\n' ';' exit 2;;
esac
curl -q -g -w "PROBE_RAN\n" -- "$1"
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("fn-d-redirect-background",
     r"""```bash
{ case "$1" in *REPLACE_WITH_T*) exit 2;; esac; } >/dev/null &
wait
curl -q -g -w "PROBE_RAN\n" -- "$1"
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("fn-d-redirect-pipeline",
     r"""```bash
{ case "$1" in *REPLACE_WITH_T*) exit 2;; esac; } >/dev/null | cat
wait
curl -q -g -w "PROBE_RAN\n" -- "$1"
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("fn-e-shadowed-exit",
     r"""```bash
exit() { :; }
set -- 'file:///dev/null#REPLACE_WITH_T'
case "$1" in *REPLACE_WITH_T*) exit 2;; esac
curl -q -g -w "PROBE_RAN\n" -- "$1"
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("fn-f-quoted-wildcards",
     r"""```bash
case "$1" in '*REPLACE_WITH_T*') exit 2;; esac
curl -q -g -w "PROBE_RAN\n" -- "$1"
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("fn-a-multiline-alternatives",
     r"""```bash
case "$1" in
  *REPLACE_WITH_T* | \
  *YOUR_PUBLIC_IP* | \
  "") exit 2;;
esac
curl -q -g -- "$1"
```
""", [], ()),

    ("fn-b-parent-span-does-not-cover-script",
     r"""```bash
case "$1" in
  *REPLACE_WITH_T*) exit 2;;
  *) cat <<'SH' > script.sh
curl -q -g -- "$1"
SH
  ;;
esac
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("fn-b-multiline-child-guard-own-probe",
     r"""```bash
bash -s -- "$1" <<'SH'
case "$1" in
  *REPLACE_WITH_T*|"") exit 2;;
esac
curl -q -g -- "$1"
SH
curl -q -g -- "$1"
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("fn-e-shadowed-exit-spaced",
     r"""```bash
exit () { :; }
case "$1" in *REPLACE_WITH_T*) exit 2;; esac
curl -q -g -- "$1"
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("fn-e-shadowed-exit-function-keyword",
     r"""```bash
function exit { :; }
case "$1" in *REPLACE_WITH_T*) exit 2;; esac
curl -q -g -- "$1"
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("fn-e-shadowed-exit-alias",
     r"""```bash
alias exit=':'
case "$1" in *REPLACE_WITH_T*) exit 2;; esac
curl -q -g -- "$1"
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("fn-e-shadowed-return",
     r"""```bash
return() { :; }
check_target() {
  case "$1" in *REPLACE_WITH_T*) return 2;; esac
  curl -q -g -- "$1"
}
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("fn-e-shadowed-return-alias",
     r"""```bash
alias return=':'
check_target() {
  case "$1" in *REPLACE_WITH_T*) return 2;; esac
  curl -q -g -- "$1"
}
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("fn-f-quoted-first-alternative",
     r"""```bash
case "$1" in '*REPLACE_WITH_T*'|"") exit 2;; esac
curl -q -g -- "$1"
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("fn-f-quoted-arm-beside-real-arm",
     r"""```bash
case "$1" in
  '*REPLACE_WITH_T*') exit 2;;
  *REPLACE_WITH_OTHER*) exit 2;;
esac
curl -q -g -- "$1"
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),
]


SELF_TEST_CASES += [
    ("c2-quoted-sentinel-default-probe",
     r"""```bash
case "$1" in
  "*REPLACE_WITH_*") exit;;
  *) curl -q file:///dev/null;;
esac
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("c2-bracket-sentinel-no-coverage",
     r"""```bash
case "$1" in
  [REPLACE_WITH_]) exit;;
esac
curl -q file:///dev/null
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("c2-pinned-prefix-no-coverage",
     r"""```bash
case "$1" in
  prefix*REPLACE_WITH_*) exit;;
esac
curl -q file:///dev/null
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("c2-catchall-before-sentinel",
     r"""```bash
case "$1" in
  *) :;;
  *REPLACE_WITH_*) exit;;
esac
curl -q file:///dev/null
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("c2-overlap-before-sentinel",
     r"""```bash
case "$1" in
  REPLACE_*) :;;
  *REPLACE_WITH_*) exit;;
esac
curl -q file:///dev/null
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("c2-quoted-parens-preserve-curl",
     r"""```bash
(
  case "$1" in
    *REPLACE_WITH_*) exit;;
  esac
)
curl "()" file:///dev/null
```
""", ["C1-MISSING-Q", "C2-PROBE-OUTSIDE-GUARD"], ()),

    ("c2-standard-sentinel-default-clean",
     r"""```bash
case "$1" in
  *REPLACE_WITH_*) exit;;
  *) curl -q file:///dev/null;;
esac
```
""", [], ()),

    ("c2-empty-alternative-extended-clean",
     r"""```bash
case "$1" in
  ""|*REPLACE_WITH_*) exit;;
esac
curl -q file:///dev/null
```
""", [], ()),

    ("c2-catchall-denies-ordinary-span",
     r"""```bash
case "$1" in
  *) :;;
  *REPLACE_WITH_*) exit;;
  other) curl -q file:///dev/null;;
esac
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("c2-overlap-denies-ordinary-span",
     r"""```bash
case "$1" in
  REPLACE_*) :;;
  *REPLACE_WITH_*) exit;;
  *) curl -q file:///dev/null;;
esac
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("c2-pinned-suffix-no-coverage",
     r"""```bash
case "$1" in
  *REPLACE_WITH_X-suffix) exit;;
esac
curl -q file:///dev/null
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("c2-fixed-marker-no-coverage",
     r"""```bash
case "$1" in
  REPLACE_WITH_X) exit;;
esac
curl -q file:///dev/null
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("c2-earlier-overlap-exits-clean",
     r"""```bash
case "$1" in
  REPLACE_*) exit;;
  *REPLACE_WITH_*) exit;;
esac
curl -q file:///dev/null
```
""", [], ()),

    ("c2-earlier-disjoint-literal-clean",
     r"""```bash
case "$1" in
  safe) :;;
  *REPLACE_WITH_*) exit;;
esac
curl -q file:///dev/null
```
""", [], ()),

    ("c2-earlier-conditional-exit-denied",
     r"""```bash
case "$1" in
  REPLACE_*) false && exit;;
  *REPLACE_WITH_*) exit;;
esac
curl -q file:///dev/null
```
""", ["C2-PROBE-OUTSIDE-GUARD"], ()),

    ("c2-split-quoted-parens-preserve-curl",
     r"""```bash
(
  case "$1" in
    *REPLACE_WITH_*) exit;;
  esac
)
curl "(" ")" file:///dev/null
```
""", ["C1-MISSING-Q", "C2-PROBE-OUTSIDE-GUARD"], ()),
]


# Subject/operand regressions run in both modes: --no-c2 must not disable
# strict coverage analysis. Existing cases above are retained unchanged.
_STRICT_VALUE_CASES = [
    ("same-arm-nc",
     'case "$1" in *REPLACE_WITH_*|"") echo sub;; '
     '*) nc -vz "$1" 1883;; esac\n', []),
    ("same-exit",
     'case "$1" in *REPLACE_WITH_*) exit;; esac\n'
     'curl -q -g "$1"\n', []),
    ("codex-mismatch",
     'case "$2" in *REPLACE_WITH_*|"") echo sub;; '
     '*) curl -q -g "https://$1/";; esac\n', ["C2-WARN-ONLY-GUARD"]),
    ("gemini-mismatch",
     'case "$2" in *REPLACE_WITH_Y*) exit 1;; esac\n'
     'curl "https://$1/"\n', ["C1-MISSING-Q", "C2-WARN-ONLY-GUARD"]),
    ("unguarded",
     'nc -vz "$1" 1883\n', ["C2-WARN-ONLY-GUARD"]),
    ("braced-positional",
     'case "${1}" in *REPLACE_WITH_*) exit;; esac\n'
     'curl -q -g "$1"\n', []),
    ("braced-multidigit",
     'case "${10}" in *REPLACE_WITH_*) exit;; esac\n'
     'curl -q -g "${10}"\n', []),
    ("named",
     'case "$HOST" in *REPLACE_WITH_*) exit;; esac\n'
     'curl -q -g "https://${HOST}/"\n', []),
    ("partial-coverage",
     'case "$1" in *REPLACE_WITH_*) exit;; esac\n'
     'curl -q -g "https://$1/$2"\n', ["C2-WARN-ONLY-GUARD"]),
    ("all-operands-covered",
     'case "$1" in *REPLACE_WITH_*) exit;; esac\n'
     'case "$2" in *REPLACE_WITH_*) exit;; esac\n'
     'curl -q -g "https://$1/$2"\n', []),
    ("matching-span-out-of-scope",
     '(\ncase "$1" in *REPLACE_WITH_*) exit;; esac\n)\n'
     'case "$2" in *REPLACE_WITH_*) exit;; esac\n'
     'curl -q -g "$1"\n', ["C2-WARN-ONLY-GUARD"]),
    ("unknown-subject",
     'case fixed in *REPLACE_WITH_*) exit;; esac\n'
     'curl -q -g "$1"\n', ["C2-WARN-ONLY-GUARD"]),
    ("literal-subject",
     "case '$1' in *REPLACE_WITH_*) exit;; esac\n"
     'curl -q -g "$1"\n', ["C2-WARN-ONLY-GUARD"]),
    ("escaped-subject",
     'case \\$1 in *REPLACE_WITH_*) exit;; esac\n'
     'curl -q -g "$1"\n', ["C2-WARN-ONLY-GUARD"]),
    ("compound-subject",
     'case "$1$2" in *REPLACE_WITH_*) exit;; esac\n'
     'curl -q -g "$1"\n', ["C2-WARN-ONLY-GUARD"]),
    ("unknown-operand",
     'case "$1" in *REPLACE_WITH_*) exit;; esac\n'
     'curl -q -g https://fixed.example/\n', ["C2-WARN-ONLY-GUARD"]),
    ("parameter-operator",
     'case "$1" in *REPLACE_WITH_*) exit;; esac\n'
     'curl -q -g "$1/${2:-fallback}"\n', ["C2-WARN-ONLY-GUARD"]),
    ("literal-operand",
     'case "$1" in *REPLACE_WITH_*) exit;; esac\n'
     "curl -q -g '$1'\n", ["C2-WARN-ONLY-GUARD"]),
    ("escaped-operand",
     'case "$1" in *REPLACE_WITH_*) exit;; esac\n'
     'curl -q -g \\$1\n', ["C2-WARN-ONLY-GUARD"]),
    ("opaque-operand",
     'case "$1" in *REPLACE_WITH_*) exit;; esac\n'
     'curl -q -g "$1/$(printf host)"\n', ["C2-WARN-ONLY-GUARD"]),
    ("ansi-subject",
     "case $'1' in *REPLACE_WITH_*) exit;; esac\n"
     'curl -q -g "$1"\n', ["C2-WARN-ONLY-GUARD"]),
    ("ansi-operand",
     'case "$HOST" in *REPLACE_WITH_*) exit;; esac\n'
     "curl -q -g $'HOST'\n", ["C2-WARN-ONLY-GUARD"]),
    ("concatenated-subject",
     'case "$H"OST in *REPLACE_WITH_*) exit;; esac\n'
     'curl -q -g "$HOST"\n', ["C2-WARN-ONLY-GUARD"]),
    ("concatenated-operand",
     'case "$HOST" in *REPLACE_WITH_*) exit;; esac\n'
     'curl -q -g "$H"OST\n', ["C2-WARN-ONLY-GUARD"]),
    ("escaped-name",
     'case "$HOST" in *REPLACE_WITH_*) exit;; esac\n'
     'curl -q -g $H\\OST\n', ["C2-WARN-ONLY-GUARD"]),
    ("literal-placeholder",
     'case "$1" in *REPLACE_WITH_*) exit;; esac\n'
     'curl -q -g "https://$1/REPLACE_WITH_PATH"\n',
     ["C2-WARN-ONLY-GUARD"]),
]
SELF_TEST_CASES.extend(
    ("strict-value-" + name + ("-no-c2" if no_c2 else ""),
     '~~~bash\nif [ "$1" = REPLACE_WITH_X ]; then echo warn; fi\n'
     + shell + '~~~\n', expected,
     ("--strict-guards", "--no-c2") if no_c2 else ("--strict-guards",))
    for name, shell, expected in _STRICT_VALUE_CASES
    for no_c2 in (False, True)
)

_C2_EXPECT_LINES = {
    "fn-b-parent-span-does-not-cover-script": [5],
    "fn-b-multiline-child-guard-own-probe": [8],
    "unguarded-second-probe": [3],
    "exit-guard-own-scope-and-outer-probe": [6],
    "return-guard-function-boundary": [7],
    "continue-and-break-are-not-scope-exits": [6, 13],
    "scope-parentheses-disambiguation": [13],
    "sibling-scopes-do-not-share-certificates": [7],
    "subshell-arm-boundary-tracked": [6],
}


# Explicit expected outcomes for the non-curl credential rule.
_TOOL_ARGV_CASES = [
    ("vault login token=-", 0),
    ("vault login token=@private.txt", 0),
    ("vault login @private.txt", 0),
    ("vault login token=", 0),
    ("mosquitto_passwd -b - user pw", 1),
    ("htpasswd -nb user -", 1),
    ("lk --api-secret @file", 1),
    ("redis-cli --pass @file", 1),
    ("clickhouse-client --password pw", 1),
    ("clickhouse-client --password=pw", 1),
    ("clickhouse-client --password", 0),
    ("clickhouse-client --config-file private.xml --query SELECT --password", 0),
    ("lk --api-key REPLACE_WITH_KEY --api-secret \"$secret\"", 2),
    ("lk --api-key=key --api-secret=secret", 2),
    ("lk token create --room test", 0),
    ("lk --room --api-secret", 0),
    ("LIVEKIT_API_SECRET=\"$secret\" lk token create", 0),
    ("turnutils_uclient -w \"$pw\" -Wsecret host", 2),
    ("turnutils_uclient -wpw -W secret host", 2),
    ("turnutils_uclient -w - host", 1),
    ("turnutils_uclient -e peer host", 0),
    ("mysql -ppw --password=pw --password1=pw --password2=pw --password3=pw", 5),
    ("mysql -p db --password --password1 --password2 --password3", 0),
    ("mysql --password= -p''", 0),
    ("mysql -p-", 1),
    ("mariadb -p\"$pw\" --password=REPLACE_WITH_PASSWORD", 2),
    ("mariadb -p db --password", 0),
    ("redis-cli -a \"$pw\" --pass REPLACE_WITH_PASSWORD", 2),
    ("redis-cli --askpass -p 6379", 0),
    ("redis-cli -a -", 1),
    ("mongosh -p pw --password=\"$pw\"", 2),
    ("mongosh -ppw --password pw", 2),
    ("mongosh -p --host db --password", 0),
    ("docker login -ppw --password=pw", 2),
    ("docker --context local login -p pw --password pw", 2),
    ("docker login -u user --password-stdin", 0),
    ("docker login -p - --password=-", 0),
    ("docker login -u user", 0),
    ("docker run -p 8080:80 image", 0),
    ("htpasswd -b file user pw", 1),
    ("htpasswd -nbB -C 12 user \"$pw\"", 1),
    ("htpasswd -B -C 12 file user", 0),
    ("htpasswd -bi file user pw", 1),
    ("htpasswd -ci file user", 0),
    ("openssl enc -pass pass:pw -passin pass:pw -passout pass:pw", 3),
    ("openssl dgst -hmac \"$hmac\"", 1),
    ("openssl enc -pass \"$source\" -passin \"$(cat source)\"", 2),
    ("openssl enc -pass stdin -passin file:secret -passout fd:3", 0),
    ("openssl enc -pass env:PW -passin \"file:$path\"", 0),
    ("mc alias set local https://s3.example.com key secret", 2),
    ("mc --config-dir private alias set --api S3v4 local https://s3.example.com \"$key\" \"$secret\"", 2),
    ("mc alias import local < private.json", 0),
    ("vault login token", 1),
    ("vault login -method=token token=\"$token\"", 1),
    ("vault login -address https://vault.example.com \"$token\"", 1),
    ("vault login -", 0),
    ("vault login", 0),
    ("vault login -method=userpass username=user", 0),
    ("kubectl --token=\"$token\" get pods", 1),
    ("kubectl get pods --token REPLACE_WITH_TOKEN", 1),
    ("kubectl --kubeconfig private get pods", 0),
    ("kubectl exec pod -- app --token non-kubectl-argument", 0),
    ("influx query --token \"$token\" -t token", 2),
    ("influx query --token=token", 1),
    ("influx query --active-config private", 0),
    ("cypher-shell -p pw --password=pw", 2),
    ("cypher-shell -u user", 0),
    ("mosquitto_pub -P pw --pw pw", 2),
    ("mosquitto_sub -P \"$pw\" --pw pw", 2),
    ("mosquitto_pub -o private.conf -p 8883", 0),
    ("mosquitto_sub -o private.conf -p 8883", 0),
    ("mosquitto_passwd -b file user pw", 1),
    ("mosquitto_passwd -c file user", 0),
    ("echo 'lk --api-secret secret'", 0),
    ("command -v lk", 0),
    ("lk --api-secret ''", 0),
    ("lk --api-secret", 0),
]
# Option boundaries: a leading dash belongs to the positional operand.
_TOOL_ARGV_CASES += [
    ('htpasswd -nb user "-s3cr3t-value"', 1),
    ('htpasswd -nb user --', 1),
    ('htpasswd -nb user -C', 1),
    ('htpasswd -b file user -n', 1),
    ('htpasswd -nb -- user --', 1),
    ('htpasswd -b file -user -C', 1),
    ('htpasswd -n user', 0),
    ('htpasswd file -b', 0),
    ('htpasswd -i file -b', 0),
    ('htpasswd -nb user ""', 0),
    ('mosquitto_passwd -b file user "-s3cr3t-value"', 1),
    ('mosquitto_passwd -b file user --', 1),
    ('mosquitto_passwd -b file user -H', 1),
    ('mosquitto_passwd -b file -user -c', 1),
    ('mosquitto_passwd -H sha512 -b file user --', 1),
    ('mosquitto_passwd file -b', 0),
    ('mosquitto_passwd -c file -b', 0),
    ('mosquitto_passwd -b file user ""', 0),
    ('redis-cli SET key -a', 0),
    ('redis-cli SET --pass public-value', 0),
    ('redis-cli SET key --pass=public-value', 0),
    ('redis-cli -h host -p 6379 SET --pass public-value', 0),
    ('redis-cli --user -a SET key value', 0),
    ('redis-cli -- SET --pass public-value', 0),
    ('redis-cli -a secret SET key -a', 1),
    ('redis-cli --pass "$PW" SET --pass public-value', 1),
    ('redis-cli -n 1 --pass secret GET key', 1),
    ('redis-cli -s /run/redis.sock -a secret GET key', 1),
    ('redis-cli -r 2 -i 1 --pass secret GET key', 1),
    ('redis-cli -n 1 --askpass SET --pass public-value', 0),
    ('openssl enc -k secret', 1),
    ('openssl enc -k "$PW"', 1),
    ('openssl enc -k -kfile', 1),
    ('openssl enc -kfile private.txt', 0),
    ('openssl enc -kfile "$path"', 0),
    ('openssl enc -kfile -k', 0),
    ('openssl enc -kfile private.txt -k secret', 1),
    ('openssl enc -k ""', 0),
    ('openssl enc -key key.pem', 0),
    ('openssl enc -kfile private.txt -pass env:PW', 0),
]
# Redis value ownership must not hide later credentials or reparse command data.
for _options in (
    "-t 2", "-X tag", "-d separator", "-D separator",
    "--sni redis.internal", "--cacertdir certs", "--tls-ciphers DEFAULT",
    "--tls-ciphersuites TLS_AES_128_GCM_SHA256", "--pipe-timeout 10",
    "--show-pushes no", "--lru-test 10", "--pattern key:*", "--count 10",
    "--quoted-pattern key:*", "--intrinsic-latency 1", "--rdb dump.rdb",
    "--functions-rdb dump.rdb", "--memkeys-samples 10", "--keystats-samples 10",
    "--cursor 0", "--top 10", "--eval script.lua",
    "--test_hint hint", "--test_hint_file hints.txt",
):
    _TOOL_ARGV_CASES.extend((
        ("redis-cli %s -a secret" % _options, 1),
        ("redis-cli %s SET --pass public-value" % _options, 0),
    ))
_TOOL_ARGV_CASES += [
    ('redis-cli --eval script.lua key , --pass public-value', 0),
    ('redis-cli --cluster check host:6379 -a secret', 1),
    ('redis-cli --cluster check -a secret host:6379', 1),
    ('redis-cli --cluster check host:6379 --askpass', 0),
    ('redis-cli --cluster import host:6379 --cluster-from-pass secret', 1),
    ('redis-cli --cluster import host:6379 --cluster-from-askpass', 0),
    ('redis-cli SET --cluster --pass public-value', 0),
]
for _options in (
    "--cluster-replicas 1", "--cluster-master-id node",
    "--cluster-from host:6379", "--cluster-to node", "--cluster-from-user user",
    "--cluster-weight node=1", "--cluster-slots 10", "--cluster-timeout 10",
    "--cluster-pipeline 10", "--cluster-threshold 2",
):
    _TOOL_ARGV_CASES.extend((
        ("redis-cli --cluster check host:6379 %s -a secret" % _options, 1),
        ("redis-cli --cluster check host:6379 %s --askpass" % _options, 0),
    ))
# Each documented source option gets literal, expansion and external-input cases.
# Keep the expectations independent of the implementation's option table.
for _subcommand, _option in (
    ("enc", "-pass"), ("pkey", "-passin"), ("req", "-passout"),
    ("pkcs12", "-password"), ("pkcs12 -export", "-password"),
    ("pkcs12 -export", "-passcerts"), ("s_client", "-proxy_pass"),
    ("s_server", "-dpass"), ("cmp", "-secret"), ("cmp", "-keypass"),
    ("cmp", "-newkeypass"), ("cmp", "-otherpass"), ("cmp", "-tls_keypass"),
    ("cmp", "-srv_secret"), ("cmp", "-srv_keypass"), ("cmp", "-rsp_keypass"),
):
    for _source, _count in (
        ("pass:secret", 1), ('"pass:$PW"', 1), ('"$source"', 1),
        ("stdin", 0), ("file:private.txt", 0), ("env:PW", 0), ("fd:3", 0),
    ):
        _TOOL_ARGV_CASES.append(
            ("openssl %s %s %s" % (_subcommand, _option, _source), _count))

# Row 3.29: formerly passing accidental exposures and adjacent safe forms.
_TOOL_ARGV_CASES += [
    ('mysql -Bp"$PW"', 1),
    ('mysql -BNpsecret', 1),
    ('mysql -ABNrp"$PW"', 1),
    ('mysql -Bhpsecret', 0),
    ('mysql -svpREPLACE_WITH_PASSWORD', 1),
    ('mariadb -BNp"$PW"', 1),
    ('mysql -Bp db', 0),
    ('mysql -BNp"" db', 0),
    ('mysql -BN --password', 0),
    ('mysql -e "-Bpsecret"', 0),
    ('mysql -Bepublic', 0),
    ('mysql -- -Bpsecret', 0),
    ('turnutils_uclient -vw"$PW" host', 1),
    ('turnutils_uclient -tvW"$SECRET" host', 1),
    ('turnutils_uclient -vwREPLACE_WITH_PASSWORD host', 1),
    ('turnutils_uclient -v host', 0),
    ('turnutils_uclient -u "-vwpublic" host', 0),
    ('turnutils_uclient -vepeerwpublic host', 0),
    ('turnutils_uclient -- -vwpublic', 0),
    ('env API_KEY=secret tool', 1),
    ('env API_KEY="$KEY" tool', 1),
    ('env PASSWORD="$(cat private)" tool', 1),
    ('env VAULT_TOKEN="$TOKEN" vault status', 1),
    ('sudo env -i -- DB_PASSWORD="$PW" tool', 1),
    ('/usr/bin/env --ignore-environment CLIENT_SECRET=secret tool', 1),
    ('env API_KEY=secret env TOKEN=secret tool', 2),
    ('env API_KEY=secret', 1),
    ('env API_KEY=REPLACE_WITH_KEY tool', 1),
    ('env API_KEY=@private tool', 1),
    ('env API_KEY=- tool', 1),
    ('env API_KEY= tool', 0),
    ('env API_KEY="" tool', 0),
    ('env PUBLIC_PORT=443 tool', 0),
    ('env PASSWORD_FILE=/run/private tool', 0),
    ('env TOKEN_TTL_SECONDS=60 tool', 0),
    ('env tool API_KEY=ordinary-data', 0),
    ('API_KEY="$KEY" tool', 0),
    ('export API_KEY="$KEY"', 0),
    ('command -v env', 0),
    ('env -u API_KEY tool', 0),
    ('openssl dgst -mac HMAC -macopt key:secret', 1),
    ('openssl dgst -mac HMAC -macopt "key:$KEY"', 1),
    ('openssl dgst -mac HMAC -macopt hexkey:0123abcd', 1),
    ('openssl dgst -macopt="hexkey:$HEXKEY"', 1),
    ('openssl dgst -macopt key:REPLACE_WITH_KEY', 1),
    ('openssl dgst -macopt key:env:KEY', 1),
    ('openssl dgst -macopt key: -macopt hexkey:', 0),
    ('openssl dgst -macopt digest:SHA256', 0),
    ('openssl dgst -macopt', 0),
    ('openssl dgst -out "-macopt" key:public', 0),
    ('openssl dgst -macopt digest:SHA256 -macopt key:secret', 1),
    ('psql "postgresql://user:secret@db/app"', 1),
    ('mongosh "mongodb://user:$PW@db/app"', 1),
    ('redis-cli -u "redis://user:secret@db"', 1),
    ('tool --url="https://user:secret@example.com/"', 1),
    ('tool URI="custom+tls://user:secret@host/path"', 1),
    ('tool "https://REPLACE_WITH_USER:secret@REPLACE_WITH_HOST/"', 1),
    ('tool "https://user:prefixREPLACE_WITH_PASSWORD@host/"', 1),
    ('tool "https://user:REPLACE_WITH_PASSWORD-suffix@host/"', 1),
    ('env DATABASE_URL="postgresql://user:secret@db/app" tool', 1),
    ('psql "postgresql://user:REPLACE_WITH_PASSWORD@db/app"', 0),
    ('tool --uri="nats-route://route:REPLACE_WITH_URL_ENCODED_ROUTE_PASSWORD@host"', 0),
    ('tool "https://user:$REPLACE_WITH_PASSWORD@host/"', 1),
    ('psql "postgresql://user@db/app"', 0),
    ('tool "https://user:@host/"', 0),
    ('tool "https://host/path/user:pass@data"', 0),
    ('tool "$URL"', 0),
    ('URL="postgresql://user:secret@db/app" tool', 0),
    ('tool > "https://user:pass@host"', 0),
    ('echo "psql postgresql://user:secret@db/app"', 0),
]
for _method, _key in (
    ("userpass", "password"), ("ldap", "password"), ("okta", "password"),
    ("radius", "password"), ("github", "token"), ("token", "token"),
):
    for _value, _count in (
        ("secret", 1), ('"$SECRET"', 1), ("REPLACE_WITH_SECRET", 1),
        ("", 0), ("-", 0), ("@private.txt", 0),
    ):
        _TOOL_ARGV_CASES.append((
            "vault login -method=%s %s=%s" % (_method, _key, _value), _count))
_TOOL_ARGV_CASES += [
    ('vault login -method userpass -path employees username=user password="$PW"', 1),
    ('vault login -method=ldap username=user', 0),
    ('vault login -method=github', 0),
    ('vault login -method=cert -client-key private.pem', 0),
    ('vault login -method=cert password=unused token=unused', 0),
    ('vault status password=ordinary-data', 0),
    ('vault login -method=userpass username=password=public', 0),
    ('vault login -method=userpass -path password=public username=user', 0),
]
# The shared wrapper/waiver path must apply to every new form.
for _cmd in (
    'mysql -Bp"$PW"', 'turnutils_uclient -vw"$PW" host',
    'vault login -method=userpass password="$PW"',
    'env API_KEY="$KEY" tool', 'openssl dgst -macopt "key:$KEY"',
    'psql "postgresql://user:$PW@db/app"',
):
    SELF_TEST_CASES.extend((
        ("c3-gap-wrapped-" + _cmd, "~~~sh\nsudo " + _cmd + "\n~~~\n",
         ["C3-TOOL-ARGV"], ()),
        ("c3-gap-waived-" + _cmd,
         "~~~sh\n# guard-conventions: allow documented exception\n"
         + _cmd + "\n~~~\n", [], ()),
    ))


# Round-1 QA: required/optional values, spelling siblings and URI context.
_ROUND1_ARGV_CASES = [
    ('turnutils_uclient -w "$PW" host', 1),
    ('turnutils_uclient -W "$S" host', 1),
    ('turnutils_uclient -vw "$PW" host', 1),
    ('turnutils_uclient -vW "$S" host', 1),
    ('turnutils_uclient -tvW "-secret" host', 1),
    ('turnutils_uclient -vw "" host', 0),
    ('turnutils_uclient -vW "" host', 0),
    ('turnutils_uclient -u "-vw" host', 0),
    ('turnutils_uclient -vewpublic host', 0),
    ('turnutils_uclient -- -vw "$PW"', 0),
    ('mysql -p "$DB"', 0),
    ('mysql -BNp "$DB"', 0),
    ('mariadb -BNp "$DB"', 0),
    ('mysql -BNp"$PW" db', 1),
]
for _spelling in ("-method=", "--method=", "-method ", "--method "):
    for _method, _key in (("ldap", "password"), ("userpass", "password"),
                          ("okta", "password"), ("radius", "password"),
                          ("github", "token"), ("token", "token")):
        for _value, _count in (('"$PW"', 1), ("-", 0), ("@private.txt", 0)):
            _ROUND1_ARGV_CASES.append((
                "vault login %s%s username=user %s=%s"
                % (_spelling, _method, _key, _value), _count))
        _ROUND1_ARGV_CASES.append((
            "vault login %s%s username=user" % (_spelling, _method), 0))
_ROUND1_ARGV_CASES += [
    ('vault login --method ldap --path password=public username=user', 0),
    ('vault login --method=cert --client-key private.pem', 0),
    ('vault login --method token "$TOKEN"', 1),
    ('vault login --method token -', 0),
]
for _name in (
    "MYSQL_PWD", "REDISCLI_AUTH", "PGPASSWORD", "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN", "SECRET_KEY", "PRIVATE_KEY", "ACCESS_KEY",
    "APP_SECRET_VALUE", "APP_PASSWORD_VALUE", "APP_PASSWD_VALUE",
    "APP_PWD_VALUE", "APP_TOKEN_VALUE", "RABBITMQ_PASS", "OPENAI_API_KEY",
):
    _ROUND1_ARGV_CASES.extend((
        ('env %s="$PW" tool' % _name, 1),
        ('env %s= tool' % _name, 0),
        ('%s="$PW" tool' % _name, 0),
    ))
for _name in (
    "MYSQL_PWD_FILE", "REDISCLI_AUTH_PATH", "PASSWORD_FILE", "TOKEN_PATH",
    "SECRET_KEY_FILE", "PRIVATE_KEY_PATH", "KEY_ID", "PUBLIC_KEY",
    "AWS_ACCESS_KEY_ID", "APP_PUBLIC_KEY", "SECRET_KEY_ID",
    "TOKEN_TTL_SECONDS", "TOKEN_TTL", "LANG", "PORT", "PWD", "UPWD", "UPWD_HASH",
):
    _ROUND1_ARGV_CASES.append(('env %s=public tool' % _name, 0))
for _options in (
    "-", "--debug", "-iv", "--ignore-environment --debug",
    "-u OLD", "--unset OLD", "--unset=OLD", "-uOLD", "-ivuOLD",
    "-C /work", "--chdir=/work", "-a tool", "--argv0=tool",
    "-f settings", "--file=settings", "--ignore-signal=PIPE",
    "--default-signal --block-signal=INT --list-signal-handling", "--",
):
    _ROUND1_ARGV_CASES.extend((
        ('env %s MYSQL_PWD="$PW" tool' % _options, 1),
        ('env %s LANG=C tool' % _options, 0),
        ('env %s mysql -p"$PW"' % _options, 1),
    ))
_ROUND1_ARGV_CASES += [
    ('env -u PASSWORD=public tool', 0),
    ('env --unset=PASSWORD=public tool', 0),
    ('env -C PASSWORD=public tool', 0),
    ('env --argv0 MYSQL_PWD=public tool', 0),
    ('env tool MYSQL_PWD=public', 0),
    ('env --debug MYSQL_PWD_FILE="/run/mysql" mysql', 0),
    ('sudo /usr/bin/env --debug MYSQL_PWD="$PW" mysql', 1),
    ('env PASSWORD_FILE="postgresql://user:$PW@db/app" tool', 1),
]
for _password in ('${PW:?}', '${PW:-x}', '${PW:?missing password}',
                  '${PW:-https://fallback}', '$PW', 'literal%3Fpassword'):
    _ROUND1_ARGV_CASES.append((
        'psql "postgresql://user:%s@db/app"' % _password, 1))
for _key in (
    "password", "pass", "pwd", "passwd", "sslpassword", "token", "secret",
    "access_token", "refresh-token", "sessionToken", "authToken",
    "client_secret", "api_key", "access_key", "secret_key",
    "signature", "sig", "X-Amz-Signature", "X-Goog-Signature",
):
    _ROUND1_ARGV_CASES.extend((
        ('psql "postgresql://db/app?user=app&%s=${PW:?}"' % _key, 1),
        ('psql "postgresql://user:REPLACE_WITH_PASSWORD@db/app?%s=$PW"'
         % _key, 1),
        ('psql "postgresql://db/app?%s="' % _key, 0),
    ))
_ROUND1_ARGV_CASES += [
    ('psql "postgresql://db/app?password=REPLACE_WITH_PASSWORD"', 1),
    ('psql "postgresql://db/app?user=app;password=$PW"', 1),
    ('psql "postgresql://user:REPLACE_WITH_PASSWORD@db/app?sslmode=require"', 0),
    ('psql "postgresql://db/app?user=app&connect_timeout=10"', 0),
    ('psql "postgresql://db/app#password=$PW"', 0),
    ('tool --uri="postgresql://db/app?password=$PW"', 1),
    ('env DATABASE_URL="postgresql://db/app?password=$PW" tool', 1),
]
for _command in (
    "printf '%s\\n'", "echo", ":", "read -r -p",
    "command printf '%s\\n'", "command -p -- echo", "builtin printf '%s\\n'",
    "VALUE=public printf '%s\\n'", ">connection.txt printf '%s\\n'",
):
    _ROUND1_ARGV_CASES.append((
        _command + ' "postgresql://user:${PW:?}@db/app" >connection.txt', 0))
for _command in (
    "/usr/bin/printf '%s\\n'", "/bin/echo", "env echo", "sudo printf '%s\\n'",
    "command /bin/echo", "nohup echo", "timeout 1 echo", "exec echo",
):
    _ROUND1_ARGV_CASES.append((
        _command + ' "postgresql://user:$PW@db/app" >connection.txt', 1))
_ROUND1_ARGV_CASES += [
    ('printf "%s\\n" "postgresql://db/app?password=$PW" | cat >connection.txt', 0),
    ('cat <<<"postgresql://user:$PW@db/app" >connection.txt', 0),
    ('read -r URI <<<"postgresql://db/app?password=$PW"', 0),
    ("cat <<'EOF' >connection.txt\npostgresql://user:$PW@db/app\nEOF", 0),
    ('cat <<EOF >connection.txt\npostgresql://db/app?password=$PW\nEOF', 0),
    ('bash <<EOF\npsql "postgresql://db/app?password=$PW"\nEOF', 1),
    ('printf "%s" "$(psql "postgresql://db/app?password=$PW")"', 1),
    ('enable -n echo\necho "postgresql://user:$PW@db/app"', 1),
    ('echo() { /bin/echo "$@"; }\necho "postgresql://user:$PW@db/app"', 1),
    ('alias echo=/bin/echo\necho "postgresql://user:$PW@db/app"', 1),
    ('source settings\necho "postgresql://user:$PW@db/app"', 1),
]
_TOOL_ARGV_CASES.extend(_ROUND1_ARGV_CASES)
SELF_TEST_CASES.append((
    "c3-env-resolution-keeps-c2-scope",
    "~~~bash\ncase $1 in\n*REPLACE_WITH_*) echo substitute ;;\nesac\n"
    "env -u OLD curl -q https://203.0.113.10/\n~~~\n", [], ()))


# Round-2 QA: env's own argv, wrapper definitions and name components.
_ROUND2_ARGV_CASES = []
for _options in ("-S echo", "--split-string echo", "--split-string=echo",
                 "-Secho", "-iS echo"):
    for _operand, _count in (
        ('"postgresql://user:$PW@db/app"', 1),
        ('"postgresql://db/app?password=$PW"', 1),
        ('URI="postgresql://user:$PW@db/app"', 1),
        ('--url="postgresql://user:$PW@db/app"', 1),
        ('PASSWORD_FILE="postgresql://user:$PW@db/app"', 1),
        ('"postgresql://user:REPLACE_WITH_PASSWORD@db/app"', 0),
        ('"postgresql://user@db/app"', 0),
        ('> "postgresql://user:$PW@db/app"', 0),
        ('<<< "postgresql://user:$PW@db/app"', 0),
    ):
        _ROUND2_ARGV_CASES.append(('env %s %s' % (_options, _operand), _count))
_ROUND2_ARGV_CASES += [
    ('sudo /usr/bin/env -S echo "postgresql://user:$PW@db/app"', 1),
    ('env -S echo "postgresql://user:$PW@db/app" "redis://user:$PW@db"', 2),
    ('env PASSWORD="postgresql://user:$PW@db/app" tool', 1),
    ('env env echo "postgresql://user:$PW@db/app"', 1),
    ('env -S echo <<<"postgresql://user:$PW@db/app"', 0),
    ('env MYSQL_PWD="$PW" env -S echo "postgresql://user:$PW@db/app"', 2),
    ('env TOKENIZERS_PARALLELISM=false python3 app.py', 0),
]
for _wrapper, _builtin in (("command", "printf '%s\\n'"), ("builtin", "echo")):
    for _definition in (
        '%s() { /bin/echo "$@"; }',
        '%s () { /bin/echo "$@"; }',
        'function %s { /bin/echo "$@"; }',
        'function %s() { /bin/echo "$@"; }',
    ):
        _ROUND2_ARGV_CASES.append((
            (_definition % _wrapper) + '\n' + _wrapper + ' ' + _builtin
            + ' "postgresql://user:$PW@db/app"', 1))
    _ROUND2_ARGV_CASES.append((
        _wrapper + ' ' + _builtin + ' "postgresql://user:$PW@db/app"', 0))
for _name in (
    "TOKENIZER_CACHE", "APP_TOKENIZER_CACHE", "TOKENIZERS_PARALLELISM",
    "MYTOKEN", "APP_MYTOKEN", "TOKENIZATION", "APP_TOKENIZATION_MODE",
    "SECRETARY", "APP_SECRETARY", "PASSWORDLESS", "APP_PASSWORDLESS",
    "PASSWDDB", "APP_PASSWDDB",
):
    _ROUND2_ARGV_CASES.append(('env %s=false tool' % _name, 0))
for _name in (
    "PGPASSWORD", "MYSQL_PWD", "REDISCLI_AUTH", "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN", "GITHUB_TOKEN", "API_TOKEN", "APP_TOKEN", "TOKEN",
    "APP_TOKEN_VALUE", "TOKEN_VALUE", "APP_SECRET_VALUE", "APP_PASSWORD_VALUE",
    "APP_PASSWD_VALUE", "APP_PWD_VALUE", "APP_PASS_VALUE", "github_token",
):
    _ROUND2_ARGV_CASES.append(('env %s="$PW" tool' % _name, 1))
_TOOL_ARGV_CASES.extend(_ROUND2_ARGV_CASES)

# Round-3 QA: final locator components do not hide credential-bearing URIs.
_ROUND3_ARGV_CASES = []
for _suffix in ("URL", "URI", "ENDPOINT", "HOST", "PORT", "PATH", "FILE",
                "DIR", "NAME"):
    for _value, _count in (
        ("https://example.com/token", 0),
        ("https://u:$PW@h/token", 1),
        ("https://example.com/token?access_token=$T", 1),
    ):
        _ROUND3_ARGV_CASES.append((
            'env X_TOKEN_%s=%s tool' % (_suffix, _value), _count))
_ROUND3_ARGV_CASES += [
    ('env OAUTH_TOKEN_ENDPOINT=https://example.com/token tool', 0),
    ('env app_password_url=https://example.com/login tool', 0),
    ('env OPENAI_API_KEY_FILE=/run/key tool', 0),
    ('env TOKENIZERS_PARALLELISM=false tool', 0),
    ('env X_TOKEN_URL_VALUE="$T" tool', 1),
    ('env SECRET_ID="$T" tool', 1),
    ('env TOKEN_ID="$T" tool', 1),
    ('env APP_ID=public tool', 0),
    ('env AWS_ACCESS_KEY_ID=public tool', 0),
]
for _name in ("GITHUB_TOKEN", "HF_TOKEN", "API_TOKEN", "TOKEN",
              "AWS_SESSION_TOKEN"):
    _ROUND3_ARGV_CASES.append(('env %s=$T tool' % _name, 1))
_TOOL_ARGV_CASES.extend(_ROUND3_ARGV_CASES)

for _i, (_cmd, _count) in enumerate(_TOOL_ARGV_CASES):
    SELF_TEST_CASES.append((
        "c3-tool-%d" % _i, "~~~bash\n" + _cmd + "\n~~~\n",
        ["C3-TOOL-ARGV"] * _count, ()))

for _wrapper in ("sudo", "command", "env A=1", "nohup", "nice", "ionice",
                 "timeout 5s", "xargs", "stdbuf -oL"):
    SELF_TEST_CASES.append((
        "c3-tool-wrapper-" + _wrapper,
        "~~~bash\n" + _wrapper + " /usr/bin/lk --api-secret \"$s\"\n~~~\n",
        ["C3-TOOL-ARGV"], ()))

SELF_TEST_CASES += [
    ("c3-tool-lifted-and-continued",
     "~~~bash\nx=$(lk token create \\\n --api-secret \"$s\")\n~~~\n",
     ["C3-TOOL-ARGV"], ()),
    ("c3-tool-waiver-next-command",
     "~~~bash\n# guard-conventions: allow documented argv-only exception\n"
     "turnutils_uclient -w \"$pw\" host\nlk --api-secret secret\n~~~\n",
     ["C3-TOOL-ARGV"], ()),
    ("c3-tool-bare-and-trailing-waivers",
     "~~~bash\n# guard-conventions: allow\nlk --api-secret secret\n"
     "lk --api-secret secret # guard-conventions: allow reason\n~~~\n",
     ["C3-TOOL-ARGV", "C3-TOOL-ARGV"], ()),
    ("c3-tool-console",
     "~~~console\n$ lk --api-secret secret\nlk --api-secret output\n~~~\n",
     ["C3-TOOL-ARGV"], ()),
    ("c3-tool-heredoc-data",
     "~~~bash\ncat <<'EOF'\nlk --api-secret secret\nEOF\n~~~\n", [], ()),
    ("c3-tool-heredoc-shell",
     "~~~bash\nbash <<'EOF'\nlk --api-secret secret\nEOF\n~~~\n",
     ["C3-TOOL-ARGV"], ()),
    ("c3-tool-no-c2-does-not-disable-c3",
     "~~~bash\nlk --api-secret \"$s\"\n~~~\n",
     ["C3-TOOL-ARGV"], ("--no-c2",)),
    ("c3-tool-wrapper-limit-disclosed",
     "~~~bash\nsudo -u user lk --api-secret secret\n~~~\n", [], ()),
]


# Exercise new forms through console and waiver boundaries.
_ROUND1_CONTEXT_CASES = []
for _cmd in (
    'turnutils_uclient -vw "$PW" host',
    'vault login --method ldap username=user password="$PW"',
    'env --debug MYSQL_PWD="$PW" mysql',
    'psql "postgresql://user:${PW:?}@db/app"',
    'psql "postgresql://db/app?password=$PW"',
):
    _ROUND1_CONTEXT_CASES.extend((
        ("round1-console-" + _cmd, "~~~console\n$ " + _cmd + "\n~~~\n",
         ["C3-TOOL-ARGV"], ()),
        ("round1-waiver-" + _cmd,
         "~~~bash\n# guard-conventions: allow documented exception\n"
         + _cmd + "\n~~~\n", [], ()),
    ))
SELF_TEST_CASES.extend(_ROUND1_CONTEXT_CASES)
SELF_TEST_CASES.append((
    "c3-unknown-env-option-keeps-c1-scope",
    "~~~bash\nenv --future-option curl https://example.com/\n~~~\n",
    ["C1-MISSING-Q"], ()))


def run_self_test():
    failures = 0
    for name, mdtext, expect, flags in SELF_TEST_CASES:
        opts = parse_args(list(flags))
        findings, stats = [], Stats()
        scan_text("<%s>" % name, mdtext, findings, stats, opts)
        got = sorted(code for _p, _l, code, _x in findings)
        exp = sorted(expect)
        ok = got == exp
        if name in _C2_EXPECT_LINES:
            got_lines = sorted(
                line for _p, line, code, _x in findings
                if code == "C2-PROBE-OUTSIDE-GUARD")
            expected_lines = _C2_EXPECT_LINES[name]
            if got_lines != expected_lines:
                ok = False
                print("  C2 lines expect=%s got=%s"
                      % (expected_lines, got_lines))
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
