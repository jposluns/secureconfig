#!/usr/bin/env python3
"""Cases for check_exposure_index.py, run against throwaway repositories.

Every case builds a temporary tree (its own tools/, an exposure-index.md and guides) and runs the
real gate as a subprocess, so the gate's root resolution is exercised end to end. The fixture
index maps 80, 443, 9090, the narrow range 8000-8010, a 101-port range 10000 to 10100 (the most
that still maps for every guide) and a 102-port range 20000 to 20101 cited only by ray.md.

Detection: at least one case per port shape, each naming an unmapped port 7777 (or 7). A mutation
check (deleting each shape in turn) confirmed that every shape is needed by at least one case:
  D1 prose "port 7777"; D2 prose list tail "ports 80 and 7777"; D3 prose range end "ports 80 to
  7777"; D4 bold "port **7777**"; D5 single digit "port 7"; D6 host:port "0.0.0.0:7777"; D7 IPv6
  literal "https://[2001:db8::1]:7777"; D8 userinfo URL; D9 "TCP 7777"; D10 "7777/tcp";
  D11 "--http-port=7777" (a flag, caught by the key shape); D12 "-p 7777:9090" (host side); D13 "-p 9090:7777" (container side);
  D14 Compose "- 7777:9090"; D15 "listen 7777 ssl;"; D16 "EXPOSE 9090 7777" (not the first port);
  D17 "containerPort: 7777"; D18 "KEY_PORT=7777"; D19 an unmapped port inside a fenced code block;
  D20 a compact plural list "ports 80,7777"; D21 a backticked range after "port" in the clause;
  D22 a quoted "-p \"7777:9090\""; D23 "-p [::]:9090:7777"; D24 a Compose IPv6 "- \"[::]:9090:7777\"";
  D25 lowercase "tcp 7777"; D26 "7777/TCP"; D27 "bind 7777"; D28 "localhost:7777"; D29 a slash list
  "ports 80/7777"; D30 an en-dash range "ports 7000-7777" (written with an en dash); D31 an IPv4 bind
  host on a published mapping "-p 10.0.0.5:7777:9090"; D32 "bind *:7777"; D33 a backticked
  "TCP `7777`"; D34-D36 the "or", "through" and hyphen list separators; D37 "127.0.0.2:7777";
  D38-D39 a backticked range after a camel-case or `_port` identifier; D40-D41 capitalized "To" and
  "THROUGH" separators in a backticked range.
Precision: N1 "TCP 192.168.1.1"; N2 "TCP 7777.2"; N3 "--support=2026" and "--export 2024";
  N4 "transport: 2026" and "report: 2024"; N5 "- 10:30 UTC"; N6 "port 7,777" (an
  unmapped number, so only the thousands rule passes it); N7 versions,
  years and counts in prose; N8 a backticked range with no "port" in the clause; N9 "EXPOSE 999999"
  and N10 "EXPOSE 7777.2" (malformed tokens yield nothing); N11 "report" is not the word "port";
  N12 a decimal list item "7777.5"; N13 a dotted "1.7777/tcp" is not a port.
Mapping: M1 a mapped port passes; M2 a narrow range maps for every guide; M3 a 101-port range maps
  for every guide; M4 a 102-port range maps only for its cited guide (ray.md passes, b.md fails);
  M5 a cited link with an anchor still counts as cited; M6 a compact plural list of mapped ports;
  M7 an index range written with an en dash maps its ports.
Allowlist: A1 an allowlisted pair passes; A2 a stale entry fails; A3 a redundant entry (the port is
  now mapped) fails as redundant.
Other: O1 meta files are not scanned; O2 a missing index table fails closed with exit 2; O3 a port
  above 65535 and O4 port 0 are not mentions.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
INDEX = ("# Exposure index\n\n| Port | May be | Documented in |\n| --- | --- | --- |\n"
         "| 80, 443 | Proxy | [a.md](a.md) |\n"
         "| 8000-8010 | A narrow range | [a.md](a.md) |\n"
         "| 9090 | Prometheus | [a.md](a.md) |\n"
         "| 10000 to 10100 | A 101-port range | [a.md](a.md) |\n"
         "| 20000 to 20101 | A 102-port worker range | [ray.md](ray.md#ports) |\n")


def run(files, allow=None, index=INDEX):
    d = Path(tempfile.mkdtemp())
    try:
        (d / "tools").mkdir()
        for name in ("check_exposure_index.py", "_markdown.py", "check_reasoned_rows.py"):
            shutil.copy(HERE / name, d / "tools" / name)
        if index is not None:
            (d / "exposure-index.md").write_text(index, encoding="utf-8")
        for name, body in files.items():
            (d / name).write_text(body, encoding="utf-8")
        if allow is not None:
            (d / "tools" / "exposure_index_allowlist.txt").write_text(allow, encoding="utf-8")
        r = subprocess.run([sys.executable, "-I", "-B", "tools/check_exposure_index.py"],
                           cwd=d, capture_output=True, text=True)
        return r.returncode, r.stdout.strip()
    finally:
        shutil.rmtree(d, ignore_errors=True)


def guide(body):
    return {"a.md": "# A\n\n" + body + "\n"}


DETECT = [
    ("D1", "It listens on port 7777.", 7777),
    ("D2", "It listens on ports 80 and 7777.", 7777),
    ("D3", "It uses ports 80 to 7777.", 7777),
    ("D4", "It listens on port **7777**.", 7777),
    ("D5", "It listens on port 7.", 7),
    ("D6", "Bound to 0.0.0.0:7777 by default.", 7777),
    ("D7", "Reach it at https://[2001:db8::1]:7777/ over IPv6.", 7777),
    ("D8", "Connect with postgres://app:pw@db.internal:7777/app today.", 7777),
    ("D9", "It serves TCP 7777 to clients.", 7777),
    ("D10", "Open 7777/tcp only on the private interface.", 7777),
    ("D11", "Start it with --http-port=7777 set (the key shape).", 7777),
    ("D12", "```sh\ndocker run -p 7777:9090 img\n```", 7777),
    ("D13", "```sh\ndocker run -p 9090:7777 img\n```", 7777),
    ("D14", "```yaml\nports:\n  - 7777:9090\n```", 7777),
    ("D15", "```nginx\nlisten 7777 ssl;\n```", 7777),
    ("D16", "```dockerfile\nEXPOSE 9090 7777\n```", 7777),
    ("D17", "```yaml\ncontainerPort: 7777\n```", 7777),
    ("D18", "```sh\nKEY_PORT=7777 ./serve\n```", 7777),
    ("D19", "```sh\nserve --bind 127.0.0.1:7777\n```", 7777),
    ("D20", "It listens on ports 80,7777.", 7777),
    ("D21", "The CLI uses its own distribution-port range, by default `7700` through `7777`.", 7777),
    ("D22", "```sh\ndocker run -p \"7777:9090\" img\n```", 7777),
    ("D23", "```sh\ndocker run -p [::]:9090:7777 img\n```", 7777),
    ("D24", "```yaml\nports:\n  - \"[::]:9090:7777\"\n```", 7777),
    ("D25", "Open it on tcp 7777 only.", 7777),
    ("D26", "Open 7777/TCP only on the private interface.", 7777),
    ("D27", "```haproxy\nbind 7777\n```", 7777),
    ("D28", "Browse to localhost:7777 to reach it.", 7777),
    ("D29", "It listens on ports 80/7777.", 7777),
    ("D30", "It listens on ports 7000\N{EN DASH}7777.", 7777),
    ("D31", "```sh\ndocker run -p 10.0.0.5:7777:9090 img\n```", 7777),
    ("D32", "```haproxy\nbind *:7777\n```", 7777),
    ("D33", "It serves TCP `7777` to clients.", 7777),
    ("D34", "It listens on ports 80 or 7777.", 7777),
    ("D35", "It listens on ports 80 through 7777.", 7777),
    ("D36", "It listens on ports 80-7777.", 7777),
    ("D37", "The listener binds 127.0.0.2:7777 locally.", 7777),
    ("D38", "The `listenPort` range is `7700` to `7777`.", 7777),
    ("D39", "The rtc_port range is `7700` to `7777`.", 7777),
    ("D40", "The port range is `7700` To `7777`.", 7777),
    ("D41", "The port range is `7700` THROUGH `7777`.", 7777),
]
PRECISE = [
    ("N1", "The gateway is TCP 192.168.1.1 on the LAN."),
    ("N2", "Protocol version TCP 7777.2 is not a port."),
    ("N3", "Pass --support=2026 and --export 2024 to the tool."),
    ("N4", "```yaml\ntransport: 2026\nreport: 2024\n```"),
    ("N5", "- 10:30 UTC stand-up"),
    ("N6", "It handles port 7,777 rows a day."),
    ("N7", "Version 3.12, released in 2026, handles 5000 requests."),
    ("N8", "See pages `10` to `20` of the manual."),
    ("N9", "```dockerfile\nEXPOSE 999999\n```"),
    ("N10", "```dockerfile\nEXPOSE 7777.2\n```"),
    ("N11", "The report covers years `2020` to `2026`."),
    ("N12", "It listens on ports 80,7777.5 in the release notes."),
    ("N13", "See section 1.7777/tcp of the spec."),
]


def main() -> int:
    failures = []

    def check(desc, cond):
        if not cond:
            failures.append(desc)

    for cid, body, port in DETECT:
        rc, out = run(guide(body))
        check(f"{cid}: detects unmapped port {port} in {body!r} (rc={rc}, out={out!r})",
              rc == 1 and f"names port {port}," in out)

    for cid, body in PRECISE:
        rc, out = run(guide(body))
        check(f"{cid}: {body!r} is not a port mention (rc={rc}, out={out!r})",
              rc == 0 and "PASS" in out)

    rc, out = run(guide("It listens on port 9090 and port 443."))
    check(f"M1: mapped ports pass (rc={rc}, out={out!r})", rc == 0)
    rc, out = run({"b.md": "# B\n\nThe API uses port 8005.\n"})
    check(f"M2: a narrow range maps for every guide (rc={rc}, out={out!r})", rc == 0)
    rc, out = run({"b.md": "# B\n\nThe worker uses port 10100.\n"})
    check(f"M3: a 101-port range maps for every guide (rc={rc}, out={out!r})", rc == 0)
    rc, out = run({"ray.md": "# Ray\n\nWorkers use port 20101.\n",
                   "b.md": "# B\n\nThe proxy uses port 20101.\n"})
    check(f"M4: a 102-port range maps only for its cited guide (rc={rc}, out={out!r})",
          rc == 1 and "b.md:3 names port 20101" in out and "ray.md" not in out)
    rc, out = run({"ray.md": "# Ray\n\nWorkers use port 20050.\n"})
    check(f"M5: a cited link with an anchor counts as cited (rc={rc}, out={out!r})", rc == 0)
    rc, out = run(guide("It listens on ports 80,443 by default."))
    check(f"M6: a compact plural list of mapped ports passes (rc={rc}, out={out!r})", rc == 0)
    rc, out = run({"b.md": "# B\n\nThe API uses port 30005.\n"},
                  index=INDEX + "| 30000\N{EN DASH}30010 | An en-dash range | [a.md](a.md) |\n")
    check(f"M7: an en-dash index range maps its ports (rc={rc}, out={out!r})", rc == 0)

    rc, out = run(guide("It connects out to port 7777."), allow="a.md 7777  # outbound\n")
    check(f"A1: an allowlisted pair passes (rc={rc}, out={out!r})", rc == 0 and "1 allowlisted" in out)
    rc, out = run(guide("It listens on port 9090."), allow="a.md 7777  # outbound\n")
    check(f"A2: a stale entry fails (rc={rc}, out={out!r})",
          rc == 1 and "stale allowlist entry `a.md 7777`" in out)
    rc, out = run(guide("It listens on port 9090."), allow="a.md 9090  # example\n")
    check(f"A3: a redundant entry fails as redundant (rc={rc}, out={out!r})",
          rc == 1 and "redundant allowlist entry `a.md 9090`" in out)

    rc, out = run({"CONTRIBUTING.md": "# Contributing\n\nUse port 7777 in examples.\n",
                   "a.md": "# A\n\nport 9090\n"})
    check(f"O1: meta files are not scanned (rc={rc}, out={out!r})", rc == 0)
    rc, out = run(guide("port 9090"), index="# No table here\n")
    check(f"O2: a missing index table fails closed (rc={rc}, out={out!r})", rc == 2)
    rc, out = run(guide("It listens on port 99999."))
    check(f"O3: a number above 65535 is not a port (rc={rc}, out={out!r})", rc == 0)
    rc, out = run(guide("It listens on port 0 until configured."))
    check(f"O4: port 0 is not a port mention (rc={rc}, out={out!r})", rc == 0)

    total = len(DETECT) + len(PRECISE) + 7 + 3 + 4
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        print(f"FAIL: {len(failures)} of {total} exposure-index self-test cases failed")
        return 1
    print(f"PASS: {total} of {total} exposure-index self-test cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
