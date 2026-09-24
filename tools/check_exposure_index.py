#!/usr/bin/env python3
"""Fail when a guide names a listening port that exposure-index.md does not map.

exposure-index.md is the corpus's port-to-guide lookup: a reader with a scan result finds the
port there and opens the guides it names. A guide that documents a listener the index never
mentions leaves that reader with nothing to search on, so this gate keeps the two in step.

WHAT COUNTS AS A PORT MENTION. Nine high-precision shapes, in prose and inside fenced code
blocks alike (several real listeners appear only in configuration examples):
  - "port 9090", "ports 80 and 443", "ports 80, 443 and 8080";
  - a host:port on a loopback, any-address or localhost host, or after a scheme
    (`0.0.0.0:9090`, `127.0.0.1:9090`, `localhost:9090`, `[::]:9090`, `https://host:9090`);
  - "TCP 26379" / "UDP 3478";
  - "9090/tcp" / "3478/udp";
  - a port flag (`--port 9090`, `--port=9090`, `--http-port=8080`);
  - a published mapping (`-p 3000:8080`, `--publish 3000:8080`, a Compose `- "3000:8080"`),
    where both sides count: the host side is what a scan sees, the container side is what the
    index rows cite;
  - a line-initial `listen` or `bind` directive (`listen 443 ssl;`, `bind *:443`);
  - a Dockerfile `EXPOSE 9090`;
  - a port key (`port: 9090`, `KEY_PORT=9090`, `"port": 9090`, `containerPort: 9090`).
A broader net (any `word:N`, or any bare four- or five-digit number) was measured at the time
this gate was written and found to be mostly years, sizes, counts and versions, so it is not used.

WHAT COUNTS AS MAPPED. The index table's first column lists single ports, comma lists and
ranges (`9300 to 9400`, `8000-8010`). A single port or a range of at most 101 ports maps that
port for every guide. A wider range (Ray's worker range, coturn's relay range) maps its ports
only for the guides its own row cites, because otherwise it would silently cover every high
port in the corpus.

ALLOWLIST. tools/exposure_index_allowlist.txt lists `<guide> <port>  # reason` pairs that match a
pattern but are not listeners this corpus documents (an outbound destination, an illustrative
number). An entry that no longer matches any mention is STALE and fails the gate, so the list
cannot quietly outlive the text it excuses.

Exit status: 0 when every mention is mapped or allowlisted and no allowlist entry is stale; 1
otherwise; 2 when the index table cannot be found. Everything is offline and reads files as
UTF-8. `--self-test` is not provided here; tools/test_exposure_index.py drives this script
against throwaway trees.
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
TABLE_HEADER = "| Port | May be | Documented in |"
WIDE = 101  # a range wider than this maps its ports only for the guides its row cites

RANGE = re.compile(r"(\d+)\s*(?:to|-|\N{EN DASH})\s*(\d+)")
N = r"(\d{2,5})"
END = r"(?![\d.,]\d)(?!\d)"  # the number ends here: no more digits, no decimal continuation
PATTERNS = {
    "prose_port": re.compile(
        r"(?i)\bports?\s+`?(\d{2,5})`?((?:\s*(?:,|and|or|/)\s*(?:and\s+|or\s+)?`?\d{2,5}`?)*)" + END),
    "hostport": re.compile(
        r"(?:\b(?:0\.0\.0\.0|127\.0\.0\.1|localhost)|\[::1?\]|://[A-Za-z0-9.\-_]+):" + N + END),
    "proto_space": re.compile(r"\b(?:TCP|UDP)\s+`?(\d{2,5})`?(?!\d)"),
    "slash_proto": re.compile(r"(?i)(?<![\d/.:])(\d{2,5})/(?:tcp|udp)\b"),
    "port_flag": re.compile(r"(?i)--?[a-z\-.]*port[=\s]+`?" + N + END),
    "publish": re.compile(
        r"""(?:(?:-p|--publish)[=\s]+|^\s*-\s*["']?)(?:(?:\d{1,3}\.){3}\d{1,3}:)?(\d{2,5}):(\d{2,5})"""
        + END),
    "listen": re.compile(r"(?i)^\s*(?:listen|bind)\s+(?:\[?[\w.:*]*\]?:)?" + N + END),
    "expose": re.compile(r"^\s*EXPOSE\s+" + N + END),
    "port_key": re.compile(r"""(?i)\b\w*port["']?\s*[:=]\s*["']?""" + N + END),
}


def parse_index(root: Path):
    """Return (explicit_ports, wide_cites) from the index table, or None if it is missing.

    explicit_ports maps a port for every guide; wide_cites[port] is the set of guides a wide
    range maps that port for.
    """
    try:
        lines = (root / INDEX).read_text(encoding="utf-8").split("\n")
    except OSError:
        return None
    explicit, wide_cites, in_table, found = set(), {}, False, False
    for line in lines:
        if line.startswith(TABLE_HEADER):
            in_table, found = True, True
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if set(cells[0]) <= set("- "):
            continue  # the separator row
        cited = set(re.findall(r"\]\(([^)#]+\.md)\)", cells[-1]))
        for a, b in RANGE.findall(cells[0]):
            lo, hi = int(a), int(b)
            if hi - lo > WIDE:
                for p in range(lo, hi + 1):
                    wide_cites.setdefault(p, set()).update(cited)
            else:
                explicit.update(range(lo, hi + 1))
        explicit.update(int(n) for n in re.findall(r"\d+", RANGE.sub("", cells[0])))
    return (explicit, wide_cites) if found else None


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
                if name == "prose_port":
                    nums = [m.group(1)] + re.findall(r"\d{2,5}", m.group(2) or "")
                elif name == "publish":
                    nums = [m.group(1), m.group(2)]
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
    explicit, wide_cites = parsed
    allow = load_allowlist(root)
    used, gaps = set(), []
    for path in guides(root):
        for ln, port in mentions(path):
            if port in explicit or path.name in wide_cites.get(port, ()):
                continue
            if (path.name, port) in allow:
                used.add((path.name, port))
                continue
            gaps.append((path.name, ln, port))
    stale = sorted(set(allow) - used)
    for name, ln, port in gaps:
        print(f"EXPOSURE-INDEX: {name}:{ln} names port {port}, which {INDEX} does not map "
              f"(add a row, or allowlist it with a reason in {ALLOWLIST})")
    for name, port in stale:
        print(f"EXPOSURE-INDEX: stale allowlist entry `{name} {port}` "
              f"({ALLOWLIST}:{allow[(name, port)]}) matches no mention; remove it")
    pairs = len({(n, p) for n, _, p in gaps})
    if gaps or stale:
        print(f"FAIL: {pairs} unmapped guide/port pair(s), {len(stale)} stale allowlist entr(y/ies)")
        return 1
    print(f"PASS: every port mention in the guides is mapped by {INDEX} or allowlisted "
          f"({len(allow)} allowlisted)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
