#!/usr/bin/env python3
"""Compare the guide guards with their original predicates, including readonly names.

Offline default: python3 tools/test_quote_guards.py
Locale replay: python3 tools/test_quote_guards.py --locale en_US.utf8
NUL is excluded because Bash arguments cannot contain it.
"""
import argparse
import os
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
VALUES = [prefix + chr(n) for prefix in ("", "/tmp/", "https://s3.internal/")
          for n in range(1, 256)] + ["", "/tmp/ca.pem", "https://s3.internal/file",
                                     "REPLACE_WITH_CA", "example.com", "<x>",
                                     "éÉß", "日本語", "Kſ", "٣²", "a\\\"'z"]


def guards():
    postgres = ROOT.joinpath("postgresql.md").read_text()
    storage = ROOT.joinpath("object-storage.md").read_text()
    pg = next(block for block in re.findall(r'case "\$2" in\n.*?\besac', postgres, re.S)
              if "use a CA path" in block)
    pg_start = postgres.index(pg)
    pg = postgres[postgres.rfind("esac", 0, pg_start) + 4:pg_start + len(pg)]
    signing = storage.index('          set -- "$2" "$(aws s3 presign')
    obj = storage[storage.index("\n", signing) + 1:]
    obj = obj[:obj.index('            https://*)')] + '*) echo SAFE ;; esac'
    old_pg = r'''case "$2" in
      *[[:space:]]*|*"'"*|*\\*) echo "use a CA path without whitespace, quotes or backslashes; not probing"; exit 1 ;;
    esac'''
    old_obj = r'''case "$2" in
      *REPLACE_WITH_*|*'<'*|*'>'*|*example.com*|""|*[[:cntrl:]]*|*'"'*|*\\*)
        echo "signing failed or returned an unsafe URL; not probing" ;;
      *) echo SAFE ;; esac'''
    return (("postgresql", old_pg, pg), ("object-storage", old_obj, obj))


def evaluate(guard, locale, readonly):
    # Each value runs in the same subshell structure as the guide. Record output and status,
    # so the object-storage guard's diagnostic-only rejection is not changed into an exit.
    script = "readonly single_quote=x double_quote=x\n" if readonly else ""
    script += "probe() (\n" + guard + "\n)\n"
    for value in VALUES:
        script += "probe unused " + shlex.quote(value) + "; printf ' status=%s\\n' \"$?\"\n"
    result = subprocess.run(["bash", "--noprofile", "--norc"], input=script,
                            text=True, capture_output=True,
                            env=dict(os.environ, LC_ALL=locale))
    assert result.returncode == 0 and not result.stderr, (result.returncode, result.stderr)
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locale", default="C")
    args = parser.parse_args()
    for name, old, new in guards():
        reference = evaluate(old, args.locale, False)
        assert evaluate(new, args.locale, False) == reference, name
        assert evaluate(old, args.locale, True) == reference, name
        assert evaluate(new, args.locale, True) == reference, name
    print(f"  ok    2 guards agree on {len(VALUES)} values under {args.locale}, "
          "with ordinary and readonly quote names; diagnostics and status agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
