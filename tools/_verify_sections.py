"""Verification roots shared by the marking and demonstration-row gates.

Only whole canonical titles (optionally numbered) open a root. Descendants
belong to that root, including headings that happen to contain "verify".
Legacy parenthesized status suffixes remain section titles, not declarations.
"""
import re

TITLE = re.compile(
    r"(?i)^(?:[0-9]+[.)][ \t]+)?"
    r"(?:Verify|Verification checklist|Quick checks)"
    r"(?:[ \t]*\((?:DEMONSTRATED|REASONED)(?::[^\n]*)?\)"
    r"|[ \t]*:[ \t]*(?:DEMONSTRATED|REASONED):[^\n]*)?$"
)


def title_text(title):
    """Remove optional ATX closing hashes; normalize horizontal whitespace."""
    title = re.sub(r"[ \t]+#+[ \t]*$", "", title)
    return re.sub(r"[ \t]+", " ", title.strip(" \t"))


def verify_ranges(heads):
    """Yield disjoint [start, end) ranges from fence-aware (level, title) heads."""
    i = 0
    while i < len(heads):
        head = heads[i]
        if not head or not TITLE.fullmatch(title_text(head[1])):
            i += 1
            continue
        end = i + 1
        while end < len(heads):
            if heads[end] and heads[end][0] <= head[0]:
                break
            end += 1
        yield i, end
        i = end
