#!/usr/bin/env python3
"""Offline Verify fence marker ratchet; stdlib only.

Declarations begin a prose paragraph, a leading shell/Python '#' or SQL '--'
comment, or a heading suffix '(STATUS: provenance)' / ': STATUS: provenance'.
STATUS is DEMONSTRATED or REASONED, case-insensitively. Nonempty provenance
is required; its truth and scope remain review obligations. A heading covers
direct content only. A paragraph between fences needs an explicit
'preceding block;' or 'following block;' immediately after the colon.
Narrative mentions, command strings and HTML comments are not declarations.

All fence languages count. The small scanner supports ATX headings, backtick
and tilde fences, and space-indented list containers. Unsupported blockquotes,
tab-indented containers and unclosed fences in Verify fail, never disappear.
This is a convention scanner, not a full CommonMark parser.

Fingerprints contain normalized heading ancestry, exact LF-normalized fence
text (including delimiters/info), and adjacent paragraphs in the same list
item. Line numbers and list-item serials are diagnostic, never identity.
Ambiguous paragraphs supply no declaration to either fence. Malformed or
conflicting declarations cannot be grandfathered. --write-baseline is an explicit one-time seed operation.
Normal runs never rewrite it. Strict mode rejects new, changed, duplicate and
stale exemptions. OS/UTF-8 errors exit 2; convention errors exit 1 in strict
mode (also in seed mode). Default mode reports convention findings, exits 0.
"""
import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _markdown import Fences
from _verify_sections import title_text, verify_ranges
from check_reasoned_rows import HEADING, guides

BASELINE = Path("tools/verify_marking_baseline.txt")
DECL = re.compile(
    r"(?i)^(?:\*\*|__)?(DEMONSTRATED|REASONED)(?:\*\*|__)?"
    r":(?:\*\*|__)?[ \t]*(.*)$"
)
LIST = re.compile(r"^( *)(?:[-+*]|[0-9]+[.)])([ ]+)(.*)$")
HEADING_DECL = re.compile(
    r"(?i)(?:^|\([ \t]*|:[ \t]*)(?:\*\*|__)?"
    r"(?:DEMONSTRATED|REASONED)(?:\*\*|__)?:"
)


@dataclass
class Token:
    kind: str
    start: int
    end: int
    text: str
    owner: tuple


def tokenize(text):
    """Return lines, headings and block tokens; keep source for fingerprints."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    heads, tokens, stack = [None] * len(lines), [], []
    fences = Fences()
    start, fence_owner, comment = 0, (), False
    for i, raw in enumerate(lines):
        if raw.strip(" ") and not fences.inside:
            indent = len(raw) - len(raw.lstrip(" "))
            while stack and indent < stack[-1][0]:
                stack.pop()
        offset = stack[-1][0] if stack else 0
        line = raw[offset:] if raw.startswith(" " * offset) else raw
        if not fences.inside:
            # Ignore HTML comments only in prose, never rewrite code.
            visible = ""
            while line:
                end = line.find("-->" if comment else "<!--")
                if end < 0:
                    if not comment:
                        visible += line
                    break
                if not comment:
                    visible += line[:end]
                line = line[end + (3 if comment else 4):]
                comment = not comment
            line = visible
            match = LIST.match(line)
            if match:
                width = len(line) - len(match[3])
                stack.append((offset + width, i))
                line = match[3]
        owner = tuple(item[1] for item in stack)
        was_inside = fences.inside
        if was_inside and stack and raw.strip(" ") and not raw.startswith(" " * offset):
            raise ValueError(f"line {i + 1}: unclosed list fence")
        if fences.feed(line):
            if was_inside:
                tokens.append(Token("fence", start, i + 1,
                                    "\n".join(lines[start:i + 1]), fence_owner))
            else:
                start, fence_owner = i, owner
            continue
        if fences.inside:
            continue
        match = HEADING.match(line)
        if match:
            heads[i] = (len(match[1]), title_text(match[2] or ""))
            kind = "heading"
        elif not line.strip(" "):
            kind = "break"
        elif line.startswith((">", "\t", "|")) or re.fullmatch(r" *[-*_]{3,} *", line):
            kind = "unsupported" if line.startswith((">", "\t")) else "break"
        else:
            kind = "paragraph"
        if (kind == "paragraph" and tokens and tokens[-1].kind == kind
                and tokens[-1].end == i and tokens[-1].owner == owner):
            tokens[-1].end = i + 1
            tokens[-1].text += "\n" + line
        else:
            tokens.append(Token(kind, i, i + 1, line, owner))
    if fences.inside:
        raise ValueError(f"line {start + 1}: unclosed fence")
    return lines, heads, tokens


def declaration(text):
    """Return (status, direction), None, or raise for an empty declaration."""
    match = DECL.fullmatch(" ".join(text.strip().split("\n")))
    if not match:
        return None
    detail = match[2].strip()
    direction = ""
    for name in ("preceding", "following"):
        prefix = name + " block;"
        if detail.lower().startswith(prefix):
            direction, detail = name, detail[len(prefix):].strip()
    if not detail.strip("*_ \t"):
        raise ValueError("declaration needs scope and provenance")
    return match[1].upper(), direction


def scan_guide(text):
    lines, heads, tokens = tokenize(text)
    selected = {i for a, b in verify_ranges(heads) for i in range(a, b)}
    ancestry, paths = [], {}
    for i, head in enumerate(heads):
        if head:
            while ancestry and ancestry[-1][0] >= head[0]:
                ancestry.pop()
            ancestry.append(head)
        paths[i] = list(ancestry)
    # Blank lines do not break paragraph attachment; other block types do.
    blocks = [t for t in tokens if t.kind != "break" or t.text.strip()]
    units, errors = [], []
    for k, token in enumerate(blocks):
        if token.start not in selected:
            continue
        if token.kind == "unsupported":
            errors.append(f"line {token.start + 1}: unsupported container syntax")
        if token.kind != "fence":
            continue
        context, statuses = [], []
        try:
            for delta, direction in ((-1, "following"), (1, "preceding")):
                neighbor = blocks[k + delta] if 0 <= k + delta < len(blocks) else None
                para = (neighbor and neighbor.kind == "paragraph"
                        and neighbor.owner == token.owner and neighbor.start in selected)
                context.append(neighbor.text if para else "")
                if not para:
                    continue
                mark = declaration(neighbor.text)
                if mark:
                    other = k + 2 * delta
                    shared = (0 <= other < len(blocks)
                              and blocks[other].kind == "fence"
                              and blocks[other].owner == token.owner)
                    if shared and not mark[1]:
                        continue  # no unambiguous attachment; each fence needs its own marker
                    if not mark[1] or mark[1] == direction:
                        statuses.append(mark[0])
            heading = paths[token.start][-1][1] if paths[token.start] else ""
            match = HEADING_DECL.search(heading)
            if match:
                mark = declaration(heading[match.start():].lstrip("(: ").rstrip(") "))
                if mark:
                    statuses.append(mark[0])
            opening = re.search(r"(?:`{3,}|~{3,})([^\n]*)", lines[token.start])
            language = opening[1].strip().lower() if opening else ""
            prefix = "--" if language == "sql" else "#" if language in {
                "sh", "shell", "bash", "python", "py"
            } else None
            body = lines[token.start + 1:token.end - 1]
            first = next((line.strip() for line in body if line.strip()), "")
            if prefix and first.startswith(prefix):
                mark = declaration(first[len(prefix):].strip())
                if mark:
                    statuses.append(mark[0])
            if len(set(statuses)) > 1:
                raise ValueError("conflicting declarations; split or label the whole block REASONED")
        except ValueError as exc:
            errors.append(f"line {token.start + 1}: {exc}")
        payload = [paths[token.start], token.text, context]
        digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False,
                                          separators=(",", ":")).encode("utf-8")).hexdigest()
        units.append((token.start + 1, digest, bool(statuses)))
    return units, errors


def scan(root):
    counts, locations, errors, marked = Counter(), {}, [], 0
    for path in guides(root):
        try:
            units, findings = scan_guide(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            # UnicodeError is handled by main as an input error, not a convention.
            if isinstance(exc, UnicodeError):
                raise
            errors.append(f"{path.name}: {exc}")
            continue
        errors.extend(f"{path.name}: {finding}" for finding in findings)
        for line, digest, has_mark in units:
            if has_mark:
                marked += 1
            else:
                key = (path.name, "fence", digest)
                counts[key] += 1
                locations.setdefault(key, []).append(line)
    return counts, locations, errors, marked


def load_baseline(path):
    counts = Counter()
    for number, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if (len(fields) != 4 or not re.fullmatch(r"[^/\\\s]+\.md", fields[0])
                or fields[1] != "fence" or not re.fullmatch(r"[0-9a-f]{64}", fields[2])
                or not re.fullmatch(r"[1-9][0-9]*", fields[3])):
            raise ValueError(f"baseline line {number}: malformed entry")
        key = tuple(fields[:3])
        if key in counts:
            raise ValueError(f"baseline line {number}: duplicate key")
        counts[key] = int(fields[3])
    return counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--strict", action="store_true")
    mode.add_argument("--write-baseline", action="store_true")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    try:
        current, locations, errors, marked = scan(root)
        if args.write_baseline:
            if errors:
                for error in errors:
                    print(f"  FAIL  VERIFY-MARK {error}")
                return 1
            body = "# Explicit one-time seed; remove exemptions as fences are marked.\n"
            body += "# guide<TAB>fence<TAB>sha256<TAB>count; no automatic refresh.\n"
            body += "".join("\t".join(key) + f"\t{count}\n"
                            for key, count in sorted(current.items()))
            (root / BASELINE).write_text(body, encoding="utf-8")
            print(f"  ok    wrote {sum(current.values())} grandfathered fences")
            return 0
        baseline = load_baseline(root / BASELINE)
        retained = 0
        for key in sorted(current.keys() | baseline.keys()):
            actual, allowed = current[key], baseline[key]
            where = f"{key[0]}:{','.join(map(str, locations.get(key, [])))}"
            if actual > allowed:
                errors.append(f"{where} new/changed/excess fence {key[2]} ({actual} > {allowed})")
            if actual < allowed:
                errors.append(f"{key[0]} stale baseline {key[2]} ({actual} < {allowed}); remove it")
            kept = min(actual, allowed)
            if kept:
                retained += kept
                print(f"  BASELINE  {where} {key[2]} retained {kept}")
        for error in errors:
            print(f"  FAIL  VERIFY-MARK {error}")
        print(f"  {'FAIL' if errors else 'ok  '}  Verify marking: {marked} marked, "
              f"{retained} grandfathered fences retained, {len(errors)} findings")
        return 1 if errors and args.strict else 0
    except (OSError, UnicodeError) as exc:
        print(f"  FAIL  VERIFY-MARK input error: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"  FAIL  VERIFY-MARK {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
