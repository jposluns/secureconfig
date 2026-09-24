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
"-p8080:80", and a port split from its "port" word by a hard line wrap.
A broader net (any `word:N`, or any bare four- or five-digit number) was measured when this gate
was written and found to be mostly years, sizes, counts and versions, so it is not used.

WHAT COUNTS AS MAPPED. The index table's first column lists single ports, comma lists and
ranges (`9300 to 9400`, `8000-8010`). A single port, or a range covering at most 101 ports
(counting both ends), maps its ports for every guide. A range covering more than 101 ports
(Ray's worker range, coturn's relay range) maps them only for the guides its own row cites,
because otherwise it would silently cover every high port in the corpus.

ROW SHAPE. The header line must appear exactly, and exactly `| --- | --- | --- | --- |` must follow
it. As in GitHub-flavored Markdown, the table then runs until the first blank line, so every
non-blank line after the separator is a table row and must be in the table's form: flush left,
starting `| ` and ending ` |`, four cells split on unescaped pipes (a backslash-escaped pipe
is content), one space inside each pipe, and visible text in every cell (an HTML comment,
`&nbsp;` or a zero-width character does not count). The Port cell must be a comma-separated
list of ports or ranges (`N`,
`N to N`, `N-N`, or an en dash, each optionally `/TCP` or `/UDP`), every number from 1 to 65535
and every range ascending. "not stated" is the credential value when the cited guides are
silent. A row that breaks this fails the gate and maps nothing. A second table later in the file
is not read.

ALLOWLIST. tools/exposure_index_allowlist.txt lists `<guide> <port>  # reason` pairs that match a
pattern but are not listeners this corpus documents (an outbound destination, an illustrative
number). An entry fails the gate when it is STALE (no mention of that port remains in that
guide) or REDUNDANT (the mention remains but the index now maps it), so the list cannot outlive
the text or the gap it excuses.

Exit status: 0 when every mention is mapped or allowlisted, every allowlist entry is still
needed, and every index row is well formed; 1 otherwise; 2 when the exact header line cannot be
found. Everything is offline and reads files as UTF-8. tools/test_exposure_index.py drives this
script against throwaway trees.
"""
import re
import sys
import unicodedata
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
_INVISIBLE = re.compile(r"<!--.*?-->|&(?:nbsp|#160|#x[aA]0|ZeroWidthSpace|#8203|#x200[bB]);")
_PORT_ITEM = r"\d{1,5}(?:(?: to |-|\N{EN DASH})\d{1,5})?(?:/(?:TCP|UDP))?"
PORT_CELL = re.compile(_PORT_ITEM + r"(?:, " + _PORT_ITEM + r")*")
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


def visible(cell: str) -> bool:
    """True iff the cell renders some text: comments, blank entities and format characters do not count."""
    text = _INVISIBLE.sub("", cell)
    return any(not ch.isspace() and unicodedata.category(ch) not in ("Cc", "Cf", "Zs", "Zl", "Zp")
               for ch in text)


def row_problem(line: str):
    """Name what is wrong with a table line, or return None when it is in the table's form."""
    if line != line.lstrip():
        return "is indented; write table rows flush left"
    cells = split_row(line)
    if not visible(cells[0]):
        return "has an empty Port cell"
    if not (line.startswith("| ") and line.endswith(" |")):
        return ("does not start with `| ` and end with ` |`; every line up to the blank line after the "
                "table is a table row")
    if len(cells) != COLUMNS:
        return f"has {len(cells)} cells; the table has {COLUMNS}"
    for name, cell in zip(CELL_NAMES, cells):
        if not visible(cell):
            if name == "Default credential":
                return (
                    "has an empty Default credential cell; write `not stated` when the cited guides are silent")
            return f"has an empty {name} cell"
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
    """Return (explicit_ports, wide_cites, malformed) from the index table, or None if it is missing.

    explicit_ports maps a port for every guide; wide_cites[port] is the set of guides a wide
    range maps that port for; malformed lists (line, label, problem) for a missing or wrong
    separator row and for every table line that breaks the row grammar (see ROW SHAPE). A
    malformed row maps nothing.
    """
    try:
        lines = (root / INDEX).read_text(encoding="utf-8").split("\n")
    except OSError:
        return None
    if TABLE_HEADER not in lines:
        return None
    start = lines.index(TABLE_HEADER) + 1
    explicit, wide_cites, malformed = set(), {}, []
    if start >= len(lines) or lines[start] != SEPARATOR:
        malformed.append((start + 1, "---", f"is not a {COLUMNS}-cell separator row `{SEPARATOR}`"))
    else:
        start += 1
    for ln, line in enumerate(lines[start:], start + 1):
        if not line.strip():
            break  # as in GFM, the table runs until a blank line
        problem = row_problem(line)
        if problem:
            malformed.append((ln, split_row(line)[0] or "(blank)", problem))
            continue
        port, docs = split_row(line)[0], split_row(line)[3]
        if not port_cell_ok(port):
            malformed.append(
                (ln, port, "has a Port cell that is not a list of ports or ranges from 1 to 65535"))
            continue
        cited = set(re.findall(r"\]\(([^)#]+\.md)(?:#[^)]*)?\)", docs))
        for lo_s, hi_s in RANGE.findall(port):
            lo, hi = int(lo_s), int(hi_s)
            if hi - lo + 1 > WIDE:
                for p in range(lo, hi + 1):
                    wide_cites.setdefault(p, set()).update(cited)
            else:
                explicit.update(range(lo, hi + 1))
        explicit.update(int(n) for n in re.findall(r"\d+", RANGE.sub("", port)))
    return explicit, wide_cites, malformed


def guides(root: Path):
    for path in sorted(p for p in root.iterdir() if p.is_file() and p.suffix == ".md"):
        if path.name not in META_EXCLUDE and path.name != INDEX:
            yield path


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
    used, mapped_mentions, gaps = set(), set(), []
    for path in guides(root):
        for ln, port in mentions(path):
            if port in explicit or path.name in wide_cites.get(port, ()):
                mapped_mentions.add((path.name, port))
                continue
            if (path.name, port) in allow:
                used.add((path.name, port))
                continue
            gaps.append((path.name, ln, port))
    unneeded = sorted(set(allow) - used)
    for name, ln, port in gaps:
        print(f"EXPOSURE-INDEX: {name}:{ln} names port {port}, which {INDEX} does not map "
              f"(add a row, or allowlist it with a reason in {ALLOWLIST})")
    for name, port in unneeded:
        where = f"{ALLOWLIST}:{allow[(name, port)]}"
        if (name, port) in mapped_mentions:
            print(f"EXPOSURE-INDEX: redundant allowlist entry `{name} {port}` ({where}): {INDEX} "
                  f"now maps it; remove the entry")
        else:
            print(f"EXPOSURE-INDEX: stale allowlist entry `{name} {port}` ({where}) matches no "
                  f"mention; remove it")
    pairs = len({(n, p) for n, _, p in gaps})
    for ln, first, problem in malformed:
        print(f"EXPOSURE-INDEX: {INDEX}:{ln} row `{first}` {problem}")
    if gaps or unneeded or malformed:
        print(f"FAIL: {pairs} unmapped guide/port pair(s), {len(unneeded)} allowlist entr(y/ies) "
              f"no longer needed, {len(malformed)} malformed index row(s)")
        return 1
    print(f"PASS: every port mention in the guides is mapped by {INDEX} or allowlisted "
          f"({len(allow)} allowlisted)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
