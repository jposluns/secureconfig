#!/usr/bin/env python3
"""Cases for check_exposure_index.py, run against throwaway repositories.

Every case builds a temporary tree (its own tools/, an exposure-index.md and guides) and runs the
real gate as a subprocess, so the gate's root resolution is exercised end to end.

  1. a guide naming a mapped port passes.
  2. a guide naming an unmapped port in prose fails, naming the guide, line and port.
  3. an unmapped port inside a fenced code block also fails (code blocks count).
  4. an allowlisted pair passes; 5. a stale allowlist entry fails.
  6. a wide range maps a port only for the guides its row cites.
  7. a narrow range (at most 101 ports) maps its ports for every guide.
  8. a number outside every port shape is not a mention (a version, a year, a bare count).
  9. both sides of a published mapping (`-p 3000:8080`) are checked.
 10. meta files (CONTRIBUTING.md) are not guides and are not scanned.
 11. a missing index table fails closed with exit 2.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
INDEX_HEAD = ("# Exposure index\n\n| Port | May be | Documented in |\n| --- | --- | --- |\n"
              "| 9090 | Prometheus | [a.md](a.md) |\n"
              "| 8000-8010 | A narrow range | [a.md](a.md) |\n"
              "| 10002 to 19999 | A wide worker range | [ray.md](ray.md) |\n")


def run(files, allow=None, index=INDEX_HEAD):
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


def main() -> int:
    failures = []

    def check(desc, cond):
        if not cond:
            failures.append(desc)

    rc, out = run({"a.md": "# A\n\nIt listens on port 9090.\n"})
    check(f"1: a mapped port passes (rc={rc}, out={out!r})", rc == 0 and "PASS" in out)

    rc, out = run({"a.md": "# A\n\nIt also listens on port 7777.\n"})
    check(f"2: an unmapped prose port fails (rc={rc}, out={out!r})",
          rc == 1 and "EXPOSURE-INDEX: a.md:3 names port 7777" in out)

    rc, out = run({"a.md": "# A\n\n```sh\nserve --bind 127.0.0.1:7777\n```\n"})
    check(f"3: an unmapped port in a code block fails (rc={rc}, out={out!r})",
          rc == 1 and "a.md:4 names port 7777" in out)

    rc, out = run({"a.md": "# A\n\nIt connects out to port 7777.\n"},
                  allow="a.md 7777  # outbound\n")
    check(f"4: an allowlisted pair passes (rc={rc}, out={out!r})", rc == 0 and "1 allowlisted" in out)

    rc, out = run({"a.md": "# A\n\nIt listens on port 9090.\n"}, allow="a.md 7777  # outbound\n")
    check(f"5: a stale allowlist entry fails (rc={rc}, out={out!r})",
          rc == 1 and "stale allowlist entry `a.md 7777`" in out)

    rc, out = run({"ray.md": "# Ray\n\nWorkers use port 11111.\n",
                   "b.md": "# B\n\nThe proxy uses port 11111.\n"})
    check(f"6: a wide range maps only for cited guides (rc={rc}, out={out!r})",
          rc == 1 and "b.md:3 names port 11111" in out and "ray.md" not in out)

    rc, out = run({"b.md": "# B\n\nThe API uses port 8005.\n"})
    check(f"7: a narrow range maps for every guide (rc={rc}, out={out!r})", rc == 0)

    rc, out = run({"a.md": "# A\n\nVersion 3.12, released in 2026, handles 5000 requests.\n"})
    check(f"8: numbers outside port shapes are not mentions (rc={rc}, out={out!r})", rc == 0)

    rc, out = run({"a.md": "# A\n\n```sh\ndocker run -p 7777:9090 img\n```\n"})
    check(f"9: the host side of a published mapping is checked (rc={rc}, out={out!r})",
          rc == 1 and "names port 7777" in out and "names port 9090" not in out)

    rc, out = run({"CONTRIBUTING.md": "# Contributing\n\nUse port 7777 in examples.\n",
                   "a.md": "# A\n\nport 9090\n"})
    check(f"10: meta files are not scanned (rc={rc}, out={out!r})", rc == 0)

    rc, out = run({"a.md": "# A\n\nport 9090\n"}, index="# No table here\n")
    check(f"11: a missing index table fails closed (rc={rc}, out={out!r})", rc == 2)

    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        print(f"FAIL: {len(failures)} of 11 exposure-index self-test cases failed")
        return 1
    print("PASS: 11 of 11 exposure-index self-test cases passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
