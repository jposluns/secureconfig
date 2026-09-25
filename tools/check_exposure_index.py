#!/usr/bin/env python3
"""Fail when a guide names, in a recognized shape, a listening port exposure-index.md does not map.

exposure-index.md is the corpus's port-to-guide lookup: a reader with a scan result finds the
port there and opens the guides it names. A guide that documents a listener the index never
mentions leaves that reader with nothing to search on, so this gate keeps the two in step.

WHAT COUNTS AS A PORT MENTION. The shapes below, in prose and inside fenced code blocks alike
(several real listeners appear only in configuration examples). Where the word "port" itself
names the number, one to five digits count; elsewhere two to five do:
  - "port 9090", "port 7", "port `9090`", "port **9090**", "ports 80 and 443",
    "ports 80, 443 and 8080", "ports 80,443", "ports 5000 to 5010" (both ends); after the
    singular "port" a comma is a thousands separator ("port 80,000"), after "ports" it separates
    list items; and a backticked range after "port" in the same clause, where "port" may also be a
    `_port`/`-port`/camel-case `Port` identifier and the separator is to, through, a hyphen or an
    en dash in any case ("distribution-port
    range, by default `35672` through `35682`", both ends);
  - a host:port on an IPv4 loopback (127.0.0.0/8), the any-address or localhost host, a bracketed IPv6 literal, or after
    a scheme, including userinfo and shell-variable hosts (`0.0.0.0:9090`, `localhost:9090`,
    `[::]:9090`, `https://[2001:db8::1]:9090`, `https://host:9090`, `postgres://u:p@db:9090`);
  - "TCP 26379" / "udp 3478", either case (not followed by a decimal or dotted continuation, so an IP address
    after "TCP" is not a port);
  - "9090/tcp" / "3478/udp";
  - a published mapping, quoted or not and with an optional IPv4 or bracketed IPv6 bind host
    (`-p 3000:8080`, `-p "127.0.0.1:3000:8080"`, `-p [::]:3000:8080`, a Compose `- "3000:8080"`),
    where both sides count: the host side is what a scan sees, the container side is what the
    index rows cite; a Compose-style `- H:C` must end its line, so a bullet such as
    "- 10:30 UTC" is not a mapping;
  - a backticked published pair in prose or a table cell, the code span holding only `H:C` with
    the same optional bind host and an optional `/tcp` or `/udp` (`8888:8080`,
    `127.0.0.1:8888:8080`), both sides counting as for a published mapping; when both sides have
    exactly two digits they must be equal, so `80:80` is a pair while a clock time, duration or
    ratio (`10:30`, `45:30`, `70:30`) is not, and since only an IPv4 or bracketed IPv6 host may
    precede the pair, a bare IPv6 literal or a `file:line:column` reference (`fd00::10:20`,
    `app.py:120:45`) is not one either;
  - a line-initial `listen` or `bind` directive (`listen 443 ssl;`, `bind *:443`);
  - a Dockerfile `EXPOSE`, every whole port token on the line (`EXPOSE 80 443/tcp`); a malformed
    token (`999999`, `7777.2`) yields nothing;
  - a port key whose name is "port", ends in `_port`/`-port`, or ends in a camel-case `Port`
    (`port: 9090`, `KEY_PORT=9090`, `containerPort: 9090`, but not `transport: 2026`).
A port flag needs no shape of its own: `--port 9090` is the prose shape and `--port=9090` or
`--http-port=8080` is the key shape, while `--support=2026` and `--export 2024` match neither.
These shapes are the gate's whole definition of a mention: a port written in any other way is
not seen, so the gate keeps the index complete only over what it can recognize. Known latent edges,
none present in the corpus when this gate was written: a number joined to a port by a list
separator is read as a port ("port 5432, 10 connections" reads 10) and a YAML list of times under
a Compose-like key reads as mappings, and "EXPOSE 80 443/udp 8080/sctp" reads 8080 through the
TCP/UDP shape, all failing closed; "TCP 9000-9010" or "9000-9010/tcp" reads only one end of the
range; and three forms are not seen at all: an EXPOSE range ("EXPOSE 8080-8090"), an unspaced
"-p8080:80", and a port split from its "port" word by a hard line wrap. The backticked pair,
added later, has edges of its own, measured when it was added: an equal two-digit time or a
UID:GID pair alone in a code span (`12:12`, `1000:1000`) reads as a pair and fails closed (none
present); an unequal two-digit mapping (`80:22`) is skipped with the times it resembles (none
present); and a pair inside a longer code span, such as a `kubectl port-forward` argument, is not
seen (four present, whose ports other shapes see).
A broader net (any `word:N`, or any bare four- or five-digit number) was measured when this gate
was written and found to be mostly years, sizes, counts and versions, so it is not used.

WHAT COUNTS AS MAPPED. The index table's first column lists single ports, comma lists and
ranges (`9300 to 9400`, `8000-8010`). A row maps its ports only for the guides it cites, so a
mention is mapped when a row listing that port cites the mentioning guide. When the index lists
the port as a single port or in a range covering at most 101 ports (counting both ends), but no
row listing it cites the guide, the mention is UNCITED: a reader who looks the port up is never
sent to that guide, and the fix is to cite it on the row. A port that only a range covering more
than 101 ports lists (Ray's worker range, coturn's relay range) is not mapped at all for a guide
that range's row does not cite, because such a range would otherwise cover every high port in
the corpus; the fix there is a row of its own.

ROW SHAPE. The page must open with a `# ` heading (so no front matter), and the header line must
appear exactly once, flush left, with a blank line directly above it and no `<`, `$` or
code-fence marker anywhere above it, so the table the gate reads is the one GitHub renders (a
whitelist for the page above the table, not a model of its containers); exactly
`| --- | --- | --- | --- |` must follow it. The table then runs until the first blank line
(spaces and tabs only). That is stricter than GFM, which also ends a table at another block such
as a heading: here such a line is a malformed row, so every line between the separator and the
blank line is checked. Each of those lines must be flush left, start `| ` and end ` |`, and have
four cells split on unescaped pipes, with one space inside each pipe. Every cell must be
printable ASCII (an en dash is allowed in the Port cell). Cells are held to a whitelist rather
than to a model of rendering: every cell but Port must split into single-backtick code,
`[text](target)` links with a simple target, escaped pipes and a fixed set of plain characters;
every link's own text must contain a letter or digit, and so must the text the cell shows
(cell_problem has the detail). The Port cell must be a comma-separated list of ports or ranges
(`N`, `N to N`, `N-N`, or an en dash, each optionally `/TCP` or `/UDP`), every number from 1 to
65535 in ASCII digits with no leading zero and every range ascending. Citations are read from
the Documented in cell outside code spans. "not stated" is the credential value when the cited
guides are silent. A row that breaks this fails the gate and maps nothing.

ALLOWLIST. tools/exposure_index_allowlist.txt lists `<guide> <port>  # reason` pairs that match a
pattern but are not listeners that guide documents (an outbound destination, an illustrative
number), whether the mention is unmapped or uncited. An entry fails the gate when it is STALE (no
mention of that port remains in that guide) or REDUNDANT (the mention remains but the index now
maps it for that guide), so the list cannot outlive the text or the gap it excuses.

Exit status: 0 when every mention is mapped for its guide or allowlisted, every entry is still
needed, and every index row is well formed; 1 otherwise; 2 when the exact header line cannot be
found. Everything is offline and reads files as UTF-8. tools/test_exposure_index.py drives this
script against throwaway trees.
"""
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _markdown import Fences  # noqa: E402  one definition of a fenced block
from check_reasoned_rows import META_EXCLUDE  # noqa: E402  one definition of "not a guide"

INDEX = "exposure-index.md"
ALLOWLIST = Path("tools/exposure_index_allowlist.txt")
TABLE_HEADER = "| Port | May be | Default credential | Documented in |"
COLUMNS = 4  # every data row has exactly this many cells
CELL_NAMES = ("Port", "May be", "Default credential", "Documented in")
SEPARATOR = "| --- | --- | --- | --- |"
_UNESCAPED_PIPE = re.compile(r"(?<!\\)\|")  # GFM: `\|` inside a cell is content, not a boundary
# The whitelist a non-Port cell is built from, as one tokenizer: single-backtick code, a link with
# text and a simple target, an escaped pipe, or one plain character. Every class is ASCII, and
# re.ASCII keeps digit classes ASCII too.
_TOKEN = re.compile(
    r"(?P<code>`(?P<inner>[^`\\]+)`)"
    r"|(?P<link>\[(?P<label>[^\[\]`\\<>&$]*[A-Za-z0-9][^\[\]`\\<>&$]*)\]\((?P<dest>[A-Za-z0-9._/#:?=%+-]+)\))"
    r"|(?P<pipe>\\\|)"
    r"|(?P<plain>(?!!\[)[A-Za-z0-9 .,;:'\"()/+*=?!%_@~^#{}>-])",
    re.ASCII)
_NUM = r"[1-9][0-9]{0,4}"  # ASCII digits, no leading zero
_PORT_ITEM = _NUM + r"(?:(?: to |-|\N{EN DASH})" + _NUM + r")?(?:/(?:TCP|UDP))?"
PORT_CELL = re.compile(_PORT_ITEM + r"(?:, " + _PORT_ITEM + r")*", re.ASCII)
_CODE_SPAN = re.compile(r"`[^`\\]+`")
WIDE = 101  # a range covering more ports than this maps them only for the guides its row cites

RANGE = re.compile(r"(\d+)\s*(?:to|-|\N{EN DASH})\s*(\d+)")
N = r"(\d{2,5})"
N1 = r"(\d{1,5})"  # where the word "port" itself names the number
END = r"(?![\d.,]\d)(?!\d)"  # the number ends here: no more digits, no decimal or dotted continuation
EMPH = r"[`*]{0,2}"  # a code span or bold around the number
HOSTPFX = r"(?:(?:\d{1,3}\.){3}\d{1,3}:|\[[0-9A-Fa-f:.]*\]:)?"  # an optional bind host before H:C
LEND = r"(?!\.\d)(?!\d)"  # a list item ends: no decimal continuation (a comma may follow)
SEP = r"(?:,\s+|\s+and\s+|\s+or\s+|\s*/\s*|\s+to\s+|\s+through\s+|\s*-\s*|\s*\N{EN DASH}\s*)"
PATTERNS = {
    # singular "port N": a comma after N is a thousands separator ("port 80,000"), never a list
    "prose_port": re.compile(r"(?i)\bport\s+" + EMPH + N1 + END + EMPH
                             + r"((?:" + SEP + r"(?:and\s+|or\s+)?" + EMPH + r"\d{1,5}" + END + EMPH
                             + r")*)"),
    # plural "ports N, M": a comma always separates items, spaced or compact ("ports 80,443")
    "prose_ports": re.compile(r"(?i)\bports\s+" + EMPH + N1 + LEND + EMPH
                              + r"((?:(?:,\s*|" + SEP + r")(?:and\s+|or\s+)?" + EMPH + r"\d{1,5}" + LEND
                              + EMPH + r")*)"),
    # a backticked numeric range in prose, after "port" earlier in the same clause (the word, or a
    # `_port`/`-port`/camel-case `Port` identifier, as in the key shape; not "report" or "support")
    # ("distribution-port range, by default `35672` through `35682`"), so "pages `10` to `20`" is not one
    "tick_range": re.compile(r"(?:(?<![A-Za-z])(?i:port)|(?<=[a-z])Port)(?i:[^.;]*?)`(\d{2,5})`\s*(?:(?i:to|through)|-|\N{EN DASH})\s*`(\d{2,5})`"),
    "hostport": re.compile(
        r"(?:\b(?:0\.0\.0\.0|127(?:\.\d{1,3}){3}|localhost)|\[[0-9A-Fa-f:.]*\]|://(?:[^@/\s]+@)?[A-Za-z0-9.\-_${}]+):"
        + N + END),
    "proto_space": re.compile(r"(?i)\b(?:TCP|UDP)\s+`?" + N + r"`?" + END),
    "slash_proto": re.compile(r"(?i)(?<![\d/.:])(\d{2,5})/(?:tcp|udp)\b"),
    "publish": re.compile(
        r"""(?:-p|--publish)[=\s]+["']?""" + HOSTPFX + r"(\d{2,5}):(\d{2,5})" + END),
    # a Compose `- H:C` list item must end its line, so "- 10:30 UTC" is not a mapping
    "compose": re.compile(
        r"""^\s*-\s*["']?""" + HOSTPFX + r"(\d{2,5}):(\d{2,5})" + END
        + r"""(?=(?:/(?:tcp|udp))?["']?\s*(?:$|#))"""),
    "listen": re.compile(r"(?i)^\s*(?:listen|bind)\s+(?:\[?[\w.:*]*\]?:)?" + N + END),
    "expose": re.compile(r"^\s*EXPOSE\s+(.+)$"),
    "port_key": re.compile(
        r"""(?:(?<![A-Za-z])(?i:port)|(?<=[a-z])Port)["']?\s*[:=]\s*["']?""" + N1 + END),
}


def split_row(line: str) -> list:
    """Cells of a table line: one outer pipe per side, then a split on unescaped pipes."""
    body = line.strip()
    body = body[1:] if body.startswith("|") else body  # one outer pipe per side, so `||` keeps
    body = body[:-1] if body.endswith("|") and not body.endswith("\\|") else body  # its empty cell
    return [c.strip() for c in _UNESCAPED_PIPE.split(body)]


def cell_problem(name: str, cell: str):
    """Name what is wrong with one cell's content, or return None.

    This is a whitelist, not a model of what a renderer shows. Every cell must be printable ASCII
    (the Port cell may also use an en dash, and has its own grammar in port_cell_ok). A non-Port
    cell must split, left to right with nothing left over, into these tokens: a single-backtick
    code span with no backslash; a link `[text](target)` whose own text contains an ASCII letter or
    digit and no bracket, backtick, backslash, `<`, `>`, `&` or `$`, and whose target uses only
    letters, digits and `._/#:?=%+-`; an escaped pipe; or one plain character from the ASCII
    letters, digits, space and `.,;:'"()/+*=?!%_@~^#{}>-` (so no `<`, `&`, `$`, bracket, backtick
    or backslash in plain text, and no `![`). Some plain characters do open GitHub constructs
    (emphasis, strikethrough, emoji shortcodes); the requirement that follows is what keeps those
    visible: the text the tokens show (code content, link text and plain characters, never a link
    target) must include a letter or digit. Anything else (HTML, entities, math, images, empty or
    reference links, multi-backtick code, other escapes) is rejected rather than interpreted. Every
    row of the current table already meets this.
    """
    if not cell:
        if name == "Default credential":
            return "has an empty Default credential cell; write `not stated` when the cited guides are silent"
        return f"has an empty {name} cell"
    if any(not (" " <= ch <= "~" or (name == "Port" and ch == "\N{EN DASH}")) for ch in cell):
        return f"has a character outside printable ASCII in its {name} cell"
    if name == "Port":
        return None
    shown, pos = [], 0
    for m in _TOKEN.finditer(cell):
        if m.start() != pos:
            break
        shown.append(m.group("inner") or m.group("label") or m.group("plain") or "")
        pos = m.end()
    if pos != len(cell):
        return (f"has content outside the table's cell grammar in its {name} cell (allowed: plain "
                "ASCII text, single-backtick code, [text](target) links, and an escaped pipe)")
    if not re.search(r"[A-Za-z0-9]", "".join(shown)):
        return f"has no letter or digit in its {name} cell"
    return None


def row_problem(line: str):
    """Name what is wrong with a table line, or return None when it is in the table's form."""
    if line != line.lstrip():
        return "is indented; write table rows flush left"
    cells = split_row(line)
    if not cells[0]:
        return "has an empty Port cell"
    if not (line.startswith("| ") and line.endswith(" |")):
        return ("does not start with `| ` and end with ` |`; every line up to the blank line after the "
                "table is a table row")
    if len(cells) != COLUMNS:
        return f"has {len(cells)} cells; the table has {COLUMNS}"
    for name, cell in zip(CELL_NAMES, cells):
        problem = cell_problem(name, cell)
        if problem:
            return problem
    if " | ".join(cells) != line[2:-2]:
        return "is not in the table's `| a | b | c | d |` form (one space inside each pipe)"
    return None


def port_cell_ok(cell: str) -> bool:
    """True iff the Port cell is a list of ports or ranges, every number 1 to 65535, ranges ascending."""
    if not PORT_CELL.fullmatch(cell):
        return False
    for item in cell.split(", "):
        nums = [int(n) for n in re.findall(r"\d+", item)]
        if any(not 1 <= n <= 65535 for n in nums) or nums != sorted(nums):
            return False
    return True


def parse_index(root: Path):
    """Return (explicit_cites, wide_cites, malformed) from the index table, or None if it is missing.

    explicit_cites[port] is the set of guides cited by the rows that list the port singly or in a
    range of at most WIDE ports; wide_cites[port] is the same for the wider ranges (see WHAT
    COUNTS AS MAPPED); malformed lists (line, label, problem) for a page that does not
    open with a `# ` heading, a missing blank line above the header, `<`, `$` or a fence marker
    above it, a repeated header, a missing or wrong separator row, and every table line that
    breaks the row grammar (see ROW SHAPE). A malformed row maps nothing.
    """
    try:
        lines = (root / INDEX).read_text(encoding="utf-8").split("\n")
    except OSError:
        return None
    if TABLE_HEADER not in lines:
        return None
    header = lines.index(TABLE_HEADER)
    start = header + 1
    explicit, wide_cites, malformed = {}, {}, []
    # The table must be the one GitHub renders. Rather than model which containers above it could
    # swallow it (a list item, a blockquote, an HTML block, a fence opened inside a list item), the
    # page above the header is held to a whitelist: it opens with a `# ` heading (so no front
    # matter), it has no `<` anywhere (so no HTML block or comment can open), no `$` (so no math
    # block) and no code-fence marker, and a blank line sits directly above the header (so the
    # header, flush left, starts a new block rather than continuing a list item or blockquote).
    if not lines[0].startswith("# "):
        malformed.append((1, "top", "must open the page with a `# ` heading; front matter or other "
                          "leading blocks can hide the table"))
    if header == 0 or lines[header - 1].strip(" \t"):
        malformed.append((header + 1, "header", "must have a blank line directly above it, so the table "
                          "starts a new block"))
    for k, line in enumerate(lines[:header]):
        if "<" in line:
            malformed.append((k + 1, "above", "puts `<` above the table, which can open an HTML block that "
                              "hides it; keep `<` out of the text above the table"))
            break
    for k, line in enumerate(lines[:header]):
        if "$" in line:
            malformed.append((k + 1, "above", "puts `$` above the table, which can open a math block that "
                              "hides it; keep `$` out of the text above the table"))
            break
    for k, line in enumerate(lines[:header]):
        if "```" in line or "~~~" in line:
            malformed.append((k + 1, "above", "puts a code-fence marker above the table, which can hide it; "
                              "keep fences below the table"))
            break
    for k in range(header + 1, len(lines)):
        if lines[k] == TABLE_HEADER:
            malformed.append((k + 1, "header", "repeats the table header; this page has one table"))
    if start >= len(lines) or lines[start] != SEPARATOR:
        malformed.append((start + 1, "---", f"is not a {COLUMNS}-cell separator row `{SEPARATOR}`"))
    else:
        start += 1
    for ln, line in enumerate(lines[start:], start + 1):
        if not line.strip(" \t"):
            break  # a blank line (spaces and tabs only, as CommonMark defines it) ends the table
        problem = row_problem(line)
        if problem:
            malformed.append((ln, split_row(line)[0] or "(blank)", problem))
            continue
        port, docs = split_row(line)[0], split_row(line)[3]
        if not port_cell_ok(port):
            malformed.append(
                (ln, port, "has a Port cell that is not a list of ports or ranges from 1 to 65535"))
            continue
        cited = set(re.findall(r"\]\(([^)#]+\.md)(?:#[^)]*)?\)", _CODE_SPAN.sub("", docs)))
        for lo_s, hi_s in RANGE.findall(port):
            lo, hi = int(lo_s), int(hi_s)
            if hi - lo + 1 > WIDE:
                for p in range(lo, hi + 1):
                    wide_cites.setdefault(p, set()).update(cited)
            else:
                for p in range(lo, hi + 1):
                    explicit.setdefault(p, set()).update(cited)
        for n in re.findall(r"\d+", RANGE.sub("", port)):
            explicit.setdefault(int(n), set()).update(cited)
    return explicit, wide_cites, malformed


def guides(root: Path):
    for path in sorted(p for p in root.iterdir() if p.is_file() and p.suffix == ".md"):
        if path.name not in META_EXCLUDE and path.name != INDEX:
            yield path


# The backticked pair shape. A span counts only when its whole content is a `[host:]H:C` pair
# (`8888:8080`, `127.0.0.1:8888:8080`, `[::]:9090:7777/udp`), so a pair inside a longer span, or a
# single-backtick pair nested in a double-backtick span, is not one. Two unequal two-digit sides
# read as a time, duration or ratio (`10:30`, `70:30`) and are dropped.
TICK_PAIR = re.compile(HOSTPFX + r"(\d{2,5}):(\d{2,5})(?:/(?i:tcp|udp))?")


def code_spans(line):
    """Yield the content of each CommonMark code span on one line.

    Outside a span a backslash escapes the next character, so an escaped backtick is literal; a
    backtick run then opens a span that the next run of exactly the same length closes, and inside
    a span a backslash is literal. A run with no closing run is literal. One space of padding on
    each side is stripped when both are present and the content is not all spaces. Raw HTML and
    autolinks, which take precedence over a span in CommonMark, are not modelled; when this was
    written, the result matched markdown-it on every backticked line outside fences in the guides.
    """
    i, n = 0, len(line)
    while i < n:
        if line[i] == "\\":
            i += 2
            continue
        if line[i] != "`":
            i += 1
            continue
        j = i
        while j < n and line[j] == "`":
            j += 1
        run, k, close = j - i, j, -1
        while k < n:
            if line[k] == "`":
                m = k
                while m < n and line[m] == "`":
                    m += 1
                if m - k == run:
                    close = k
                    break
                k = m
            else:
                k += 1
        if close < 0:
            i = j
            continue
        body = line[j:close]
        if len(body) > 2 and body[0] == body[-1] == " " and body.strip(" "):
            body = body[1:-1]
        yield body
        i = close + run


def mentions(path: Path):
    """Yield (line_number, port) for every port-shaped mention in a guide, code included."""
    fences = Fences()
    for ln, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        if fences.feed(line):
            continue
        seen = set()  # one mention per port per line, however many shapes match it
        for name, rx in PATTERNS.items():
            for m in rx.finditer(line):
                if name in ("prose_port", "prose_ports"):
                    nums = [m.group(1)] + re.findall(r"\d{1,5}", m.group(2) or "")
                elif name in ("publish", "compose", "tick_range"):
                    nums = [m.group(1), m.group(2)]
                elif name == "expose":
                    nums = [tok.split("/")[0] for tok in m.group(1).split()
                            if re.fullmatch(r"\d{1,5}(?:/(?:tcp|udp))?", tok)]
                else:
                    nums = [m.group(1)]
                for n in nums:
                    if 1 <= int(n) <= 65535 and int(n) not in seen:
                        seen.add(int(n))
                        yield ln, int(n)
        for body in code_spans(line):
            pair = TICK_PAIR.fullmatch(body)
            if not pair:
                continue
            host, cont = pair.group(1), pair.group(2)
            for n in ([] if len(host) == len(cont) == 2 and host != cont else [host, cont]):
                if 1 <= int(n) <= 65535 and int(n) not in seen:
                    seen.add(int(n))
                    yield ln, int(n)


def load_allowlist(root: Path):
    """Return {(guide, port): line_number} from the allowlist; an absent file is empty."""
    try:
        text = (root / ALLOWLIST).read_text(encoding="utf-8")
    except OSError:
        return {}
    entries = {}
    for ln, line in enumerate(text.split("\n"), 1):
        body = line.split("#", 1)[0].split()
        if len(body) == 2 and body[1].isdigit():
            entries[(body[0], int(body[1]))] = ln
    return entries


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parsed = parse_index(root)
    if parsed is None:
        print(f"error: the `{TABLE_HEADER}` table was not found in {INDEX}; fail-closed")
        return 2
    explicit, wide_cites, malformed = parsed
    allow = load_allowlist(root)
    used, mapped_mentions, gaps, uncited = set(), set(), [], []
    for path in guides(root):
        for ln, port in mentions(path):
            if path.name in explicit.get(port, ()) or path.name in wide_cites.get(port, ()):
                mapped_mentions.add((path.name, port))
                continue
            if (path.name, port) in allow:
                used.add((path.name, port))
                continue
            # listed singly or in a narrow range, but on no row that cites this guide: uncited
            (uncited if port in explicit else gaps).append((path.name, ln, port))
    unneeded = sorted(set(allow) - used)
    for name, ln, port in gaps:
        print(f"EXPOSURE-INDEX: {name}:{ln} names port {port}, which {INDEX} does not map "
              f"(add a row, or allowlist it with a reason in {ALLOWLIST})")
    for name, ln, port in uncited:
        print(f"EXPOSURE-INDEX: {name}:{ln} names port {port}, which {INDEX} lists on no row that "
              f"cites {name} (cite it on the row, or allowlist it with a reason in {ALLOWLIST})")
    for name, port in unneeded:
        where = f"{ALLOWLIST}:{allow[(name, port)]}"
        if (name, port) in mapped_mentions:
            print(f"EXPOSURE-INDEX: redundant allowlist entry `{name} {port}` ({where}): {INDEX} "
                  f"now maps it for that guide; remove the entry")
        else:
            print(f"EXPOSURE-INDEX: stale allowlist entry `{name} {port}` ({where}) matches no "
                  f"mention; remove it")
    pairs = len({(n, p) for n, _, p in gaps})
    uncited_pairs = len({(n, p) for n, _, p in uncited})
    for ln, first, problem in malformed:
        print(f"EXPOSURE-INDEX: {INDEX}:{ln} row `{first}` {problem}")
    if gaps or uncited or unneeded or malformed:
        print(f"FAIL: {pairs} unmapped guide/port pair(s), {uncited_pairs} uncited guide/port "
              f"pair(s), {len(unneeded)} allowlist entr(y/ies) no longer needed, {len(malformed)} "
              f"malformed index row(s)")
        return 1
    print(f"PASS: every port mention in the guides is mapped by a row of {INDEX} that cites its "
          f"guide, or allowlisted ({len(allow)} allowlisted)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
