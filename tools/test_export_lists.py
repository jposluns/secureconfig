#!/usr/bin/env python3
"""Cases for tools/export_lists.py, the parser and checker of the export lists.

THE SHIPPED FILES: the four files under export/ parse with no finding; the root Markdown lines
of the allowlist are exactly the counted guides (the tracked ones, when git can list them),
README.md, controls-reference.md and three named project documents; every exact required copy
line names a regular file in this checkout; the default private directory is absolute and
outside this checkout, and no file under export/ names it; each publishable marker matches its
recorded shapes and none of its recorded near misses; no publishable marker finds a link that
--check-private builds into a shipped deny line, since such a marker would spell out the private
paths, and each such link names a path its deny line keeps private; the tool's source holds no
call that creates or writes a file.

THE PARSERS, on synthetic text: each refusal (a ** outside a deny line, more than one *, a *
outside the last segment, a glob at the root or with no fixed suffix, a duplicate line, a carriage
return, a byte order mark, text that is not UTF-8, a missing final LF, a control or format
character, a line of whitespace, a tab inside a path or a marker's pattern, an unknown kind or
need, a deny line in the allowlist or a copy line among the private paths, a deny line with too
many fields, a source on a copy line or a glob, an absolute path, a . or .. or .git or empty
segment, a character outside the path set, a ** inside a segment, a deny line that denies
everything, an empty file, an exact path another line of the same file also matches, a copy or
render line that can match a path a deny line matches, a marker that can match an empty string,
a marker the compiler warns about, and a marker whose shortest match cannot be worked out) and
the clean twin; overlapping deny patterns, which parse; the glob semantics; the exact overlap of
a publish pattern and a deny pattern; the marker, term and exception rules; and that a finding
about a private list never quotes it, nor a compiler message or warning that would, and that no
compiler warning reaches the warnings module's output.

THE CHECKS: check_tree on synthetic path lists (an unlisted tracked path, a required line
matching no path, an optional line matching none, a path both denied and published, a path two
lines publish, a path two deny lines keep private, among them a latest archive under a denied
directory, a deny glob that overlaps another with no tracked path matching both, a published path
that is a symbolic link or a submodule or whose name leaves the path set, a guide or public export
file without its own exact required copy line); exception verification on fixture files
(current, changed, past the end, no longer a hit, unreadable, a symbolic link); --check on a
fixture checkout with a temporary git index (clean, an untracked file and an untracked guide left
alone, a tracked unlisted file, a tracked symbolic link published, a stale exception, a missing
list, no git); --check-private on fixture private directories built under TMPDIR (clean, from
the environment variable, without printing any list content, each refusal of the directory or a
list, markers whose compiler messages or warnings would quote or locate them, and private markers
that miss a link into a deny line), leaving the fixture directory unchanged; usage errors that
repeat no argument when one starts with --check-private or --private-dir, and no abbreviated
option; the lists read through the directory as first opened when another takes its place; and
an unexpected error that prints only its type.

Every term, marker and path here is synthetic. Nothing reads the default private directory or
the network. Exit 0 ok, 1 on a finding.
"""
import contextlib
import hashlib
import io
import os
import re
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import export_lists as el  # noqa: E402
from _verify_sections import counted_guides  # noqa: E402
from _walk import isolated_git_environment  # noqa: E402

ROOT = TOOLS.parent
TOOL = TOOLS / "export_lists.py"
# Root documents the allowlist copies besides the guides, README.md and controls-reference.md.
ROOT_DOCS = {"README.sources.md", "SECURITY.md", "QUALITY.md"}
# Synthetic protected terms and a synthetic private marker; none is a real term.
TERM_A, TERM_B = "Qwertyfolk", "Zorblat Quennix"
SAMPLE_MARKER = "sample-shape\tSMP-[0-9]{3}\n"
# A synthetic private marker that finds both links --check-private builds into each deny line of
# the fixture checkout.
LINK_MARKER = ("sample-link\t(?:github\\.com/[A-Za-z0-9-]+/secureconfig/blob|raw\\."
               "githubusercontent\\.com/[A-Za-z0-9-]+/secureconfig)/[^/\\s]+/(?:CLAUDE\\.md|"
               "tools/|export/private-paths\\.txt)\n")
# A link into this project's repository.
BLOB = "https://github.com/example-org/secureconfig/blob/main/"

# For each shipped publishable marker: shapes it must find, and near misses it must not.
MARKER_CASES = {
    "id-row": (["see backlog row 9.99 for this", "Rows 9.98 and 9.99", "TODO row 9.97"],
               ["version 1.11.0 of the table", "arrows 9.99", "the third row"]),
    "id-todo": (["open in TODO.md under 9.999", "the second TODO 99 review"],
                ["a TODO comment", "todo 99"]),
    "id-done": (["as DONE 9.999 records"], ["DONE 9", "done 9.999"]),
    "id-d-number": (["(from 9.9.9, D-999)", "OD-9 says"], ["D-Bus", "ID-9", "3D-9", "AD-9"]),
    "id-f-name": (["finding F-FIXTURE-SHAPE"], ["F-35", "F-fixture-shape", "IF-FIXTURE-SHAPE"]),
    "link-history": (["https://github.com/example-org/secureconfig/pull/9",
                      "https://github.com/example-org/secureconfig/commit/abc",
                      "https://github.com/example-org/secureconfig/actions/runs/9"],
                     [BLOB + "README.md", "https://github.com/example-org/other/pull/9"]),
}


class Cases:
    def __init__(self):
        self.count = 0
        self.failures = []

    def check(self, ok, message):
        self.count += 1
        if not ok:
            self.failures.append(message)


def b(text):
    return text.encode("utf-8")


def publish(text):
    return el.parse_paths(b(text), el.ALLOWLIST, el.PUBLISH_KINDS)


def deny(text):
    return el.parse_paths(b(text), el.PRIVATE_PATHS, ("deny",))


def refused(cases, result, needle, label):
    _, findings = result
    cases.check(any(needle in f for f in findings), f"{label}: expected a finding with "
                f"{needle!r}, got {findings!r}")


def clean(cases, result, label):
    _, findings = result
    cases.check(not findings, f"{label}: expected no finding, got {findings!r}")


def shipped(cases):
    pub, den, markers, rows, findings = el.load_public(ROOT)
    cases.check(not findings, f"the shipped export files should parse cleanly: {findings!r}")
    root_md = {e.pattern for e in pub if e.kind == "copy" and "/" not in e.pattern
               and e.pattern.endswith(".md")}
    try:
        tracked = set(el.tracked_paths(ROOT))
    except el.Refused:
        tracked = None  # no git: every counted guide is held to the allowlist
    guides = {g for g in counted_guides(ROOT) if tracked is None or g in tracked}
    want = guides | {"README.md", "controls-reference.md"}
    cases.check(root_md - ROOT_DOCS == want and ROOT_DOCS <= root_md,
                f"the allowlist's root Markdown lines should be the guides, README.md, "
                f"controls-reference.md and {sorted(ROOT_DOCS)}: extra "
                f"{sorted(root_md - ROOT_DOCS - want)}, missing {sorted(want - root_md)}")
    for entry in pub:
        if entry.kind == "copy" and entry.need == "required" and "*" not in entry.pattern:
            path = ROOT / entry.pattern
            cases.check(path.is_file() and not path.is_symlink(),
                        f"{el.ALLOWLIST}:{entry.line}: {entry.pattern} is not a regular file "
                        f"in this checkout")
    cases.check(all(e.kind in el.PUBLISH_KINDS for e in pub) and all(e.kind == "deny" for e in den),
                "the allowlist holds only copy and render lines, the private paths only deny lines")
    default = el.DEFAULT_PRIVATE_DIR
    cases.check(os.path.isabs(default) and default.endswith("/")
                and os.path.commonpath([default, str(ROOT)]) not in (default.rstrip("/"), str(ROOT)),
                "the default private directory should be absolute and outside this checkout")
    for path in sorted((ROOT / "export").iterdir()):
        cases.check(default.rstrip("/").encode() not in path.read_bytes(),
                    f"{path.relative_to(ROOT)} names the default private directory")
    by_id = {m.ident: m.regex for m in markers}
    cases.check(set(by_id) == set(MARKER_CASES),
                f"every shipped marker needs recorded cases here: {sorted(set(by_id))} against "
                f"{sorted(MARKER_CASES)}")
    for ident, (hits, misses) in MARKER_CASES.items():
        regex = by_id.get(ident)
        for text in hits:
            cases.check(regex is not None and regex.search(text), f"{ident} should find {text!r}")
        for text in misses:
            cases.check(regex is not None and not regex.search(text),
                        f"{ident} should not find {text!r}")
    # The links --check-private builds into the private paths: each names a path its deny line
    # keeps private, and no publishable marker finds one, since such a marker would spell out the
    # private paths in a published file.
    for entry in den:
        path = el.link_path(entry.pattern)
        cases.check(entry.regex.fullmatch(path),
                    f"the deny line {entry.pattern!r} should keep {path!r} private")
        for label, form in el.LINK_FORMS:
            link = form.format(path)
            hits = sorted(ident for ident, regex in by_id.items() if regex.search(link))
            cases.check(not hits, f"no publishable marker should find {label} link into the deny "
                        f"line {entry.pattern!r}: {hits!r}")
    cases.check(all(r.ref.startswith("marker:") for r in rows),
                "every public exception names a marker")
    source = TOOL.read_text(encoding="utf-8")
    for call in ("mkdir", "makedirs", "write_text", "write_bytes", "O_CREAT", "O_WRONLY",
                 "O_RDWR", "rename", "unlink", "rmtree", "chmod"):
        cases.check(call not in source, f"tools/export_lists.py should create and write "
                    f"nothing, but its source holds {call!r}")


def parsers(cases):
    good = "copy\tdocs/a.md\trequired\n"
    clean(cases, publish("# a comment\n\n" + good), "a clean copy line with comments")
    clean(cases, publish("render\tdocs/a.md\toptional\tsrc/a.md\n"), "a render line with a source")
    clean(cases, publish("copy\tdocs/*.md\trequired\n"), "a narrow glob")
    clean(cases, publish("copy\tsite/x-1.0.*.zip\toptional\n"), "a glob with a prefix")
    clean(cases, deny("deny\ttools/**\ndeny\t**/secret.txt\ndeny\tTODO.md\n"), "deny lines")
    clean(cases, deny("deny\tsite/draft/**\toptional\ndeny\tTODO.md\trequired\n"),
          "deny lines with a need")
    entries, _ = deny("deny\tTODO.md\ndeny\tsite/draft/**\toptional\n")
    cases.check([e.need for e in entries] == ["required", "optional"],
                f"a deny line without a need is required: {entries!r}")
    for text, needle, label in (
        ("copy\tdocs/**\trequired\n", "uses **", "** outside a deny line"),
        ("copy\tdocs/*a*.md\trequired\n", "more than one *", "two * in a segment"),
        ("copy\tdocs/*/a.md\trequired\n", "outside the last segment", "* in a directory"),
        ("copy\tdocs/*/*.md\trequired\n", "more than one *", "two * in a path"),
        ("copy\t*.md\trequired\n", "repository root", "a glob at the root"),
        ("copy\tdocs/a*\trequired\n", "no fixed suffix", "a glob with no suffix"),
        ("copy\tdocs/*.\trequired\n", "no fixed suffix", "a glob ending in a dot"),
        (good + good, "repeats the pattern of line 1", "a duplicate line"),
        ("render\tdocs/a.md\trequired\n" + good, "repeats the pattern", "a path on two kinds"),
        ("copy\tdocs/a.md\trequired\r\n", "carriage return", "a CR"),
        (chr(0xFEFF) + good, "byte order mark", "a BOM"),
        (good[:-1], "does not end in LF", "no final LF"),
        ("copy\tdocs/a\x0b.md\trequired\n", "control or format", "a control character"),
        ("copy\tdocs/a" + chr(0x200B) + ".md\trequired\n", "control or format", "a format character"),
        ("copy\tdocs/a" + chr(0x2028) + ".md\trequired\n", "control or format", "a line separator"),
        ("   \n" + good, "whitespace alone", "a line of whitespace"),
        ("copy\tdocs/a\tb.md\trequired\n", "the need 'b.md'", "a tab inside a path"),
        ("move\tdocs/a.md\trequired\n", "the kind 'move'", "an unknown kind"),
        ("deny\tdocs/a.md\n", "is not copy or render", "a deny line in the allowlist"),
        ("copy\tdocs/a.md\n", "has 2 tab-separated fields", "a copy line with no need"),
        ("copy\tdocs/a.md\tmaybe\n", "the need 'maybe'", "an unknown need"),
        ("copy\tdocs/a.md\trequired\tsrc/a.md\n", "only a render line", "a source on copy"),
        ("render\tdocs/*.md\trequired\tsrc/a.md\n", "one exact path", "a source on a glob"),
        ("render\tdocs/a.md\trequired\tsrc/*.md\n", "exact path is needed", "a glob source"),
        ("copy\t/docs/a.md\trequired\n", "is absolute", "an absolute path"),
        ("copy\tdocs/../a.md\trequired\n", ". or .. segment", "a .. segment"),
        ("copy\t./a.md\trequired\n", ". or .. segment", "a . segment"),
        ("copy\tdocs/\trequired\n", "ends in /", "a trailing slash"),
        ("copy\tdocs//a.md\trequired\n", "empty segment", "an empty segment"),
        ("copy\t.git/config\trequired\n", "names .git", "a .git segment"),
        ("copy\tdocs/a b.md\trequired\n", "holds a character", "a space"),
        ("copy\tdocs/" + chr(0xE9) + ".md\trequired\n", "holds a character", "a non-ASCII letter"),
        ("copy\tdocs\\a.md\trequired\n", "holds a character", "a backslash"),
        ("# only a comment\n", "has no entries", "an empty allowlist"),
        ("", "has no entries", "an empty file"),
        ("copy\tdocs/*.md\trequired\ncopy\tdocs/a.md\trequired\n", "also matched by line 1",
         "an exact path a glob also publishes"),
    ):
        refused(cases, publish(text), needle, label)
    refused(cases, el.parse_paths(b"\xff\n", el.ALLOWLIST, el.PUBLISH_KINDS), "is not UTF-8",
            "text that is not UTF-8")
    for text, needle, label in (
        ("copy\tdocs/a.md\trequired\n", "is not deny", "a copy line among the private paths"),
        ("deny\tdocs/a.md\tmaybe\n", "the need 'maybe'", "a deny line with an unknown need"),
        ("deny\tdocs/a.md\toptional\tx\n", "a deny line has 4", "a deny line with four fields"),
        ("deny\tdocs/**x\n", "inside a segment", "** inside a segment"),
        ("deny\tdocs/*a*\n", "more than one * in a segment", "two * in a deny segment"),
        ("deny\t**\n", "denies every path", "a deny line that denies everything"),
        ("deny\t**/**\n", "denies every path", "a deny line of ** segments alone"),
        ("deny\ttools/**\ndeny\ttools/x.py\n", "'tools/x.py' is also matched by line 1",
         "an exact deny path a deny glob also matches"),
    ):
        refused(cases, deny(text), needle, label)
    # Two deny globs may overlap; only a tracked path both match is refused (see tree_checks).
    clean(cases, deny("deny\ttools/**\ndeny\t**/*-latest.zip\toptional\n"),
          "overlapping deny globs")

    # A copy or render line that can match a path a deny line matches.
    pub, _ = publish("copy\ttools/x.py\trequired\ncopy\ttools/*.py\toptional\n"
                     "copy\tdocs/*.md\trequired\n")
    den, _ = deny("deny\ttools/**\n")
    found = el.overlap_findings(pub, den)
    cases.check(len(found) == 2 and all("can match a path that the deny line" in f for f in found),
                f"an exact path and a glob that a deny line covers should both be refused: {found!r}")
    pub, _ = publish("copy\tdocs/*.md\trequired\n")
    for den_text, want, label in (
        ("deny\tdocs/s*.md\n", 1, "a deny glob narrower than the publish glob"),
        ("deny\t**/*-x.md\n", 1, "a deny glob of any depth"),
        ("deny\tdocs/*.txt\n", 0, "a deny glob with another suffix"),
        ("deny\tdocs/.*.md\n", 0, "a deny glob of dot names, which a publish * never matches"),
        ("deny\tdocs/sub/**\n", 0, "a deny glob one level down"),
    ):
        den, _ = deny(den_text)
        found = el.overlap_findings(pub, den)
        cases.check(len(found) == want, f"{label}: {found!r}")
    for first, second, want in (
        ("docs/*.md", "docs/s*.md", True), ("docs/*.md", "docs/*", True),
        ("docs/a*.md", "docs/*b.md", True), ("docs/a*.md", "docs/b*.md", False),
        ("docs/*.md", "docs/*.txt", False), ("docs/*.md", "docs/.*.md", False),
        ("docs/ab.md", "docs/a*b.md", False), ("docs/axb.md", "docs/a*b.md", True),
        ("docs/.x.md", "docs/*.md", False), ("docs/x.md", "docs/**", True),
        ("docs/x.md", "**/x.md", True), ("docs/x.md", "**/y.md", False),
        ("site/b.html", "site/**/b.html", True), ("site/a/b.html", "site/**/b.html", True),
        ("site", "site/**", False), ("site/x-1.*.zip", "**/*-latest.zip", True),
        ("site/advisories/*.html", "**/*-latest.zip", False),
    ):
        cases.check(el.patterns_meet(first, second) == want,
                    f"{first!r} and {second!r} should {'' if want else 'not '}share a path")

    def matches(pattern, path):
        return bool(el.pattern_regex(pattern).fullmatch(path))

    for pattern, path, want in (
        ("docs/*.md", "docs/a.md", True), ("docs/*.md", "docs/sub/a.md", False),
        ("docs/*.md", "docs/.a.md", False), ("docs/*.md", "docs/.md", False),
        ("docs/*.md", "DOCS/a.md", False), ("docs/*.md", "docs/a.MD", False),
        ("site/x-1.0.*.zip", "site/x-1.0.5.zip", True),
        ("site/x-1.0.*.zip", "site/x-latest.zip", False),
        ("site/x-1.0.*.zip", "site/x-1.0..zip", False),
        ("tools/**", "tools/a", True), ("tools/**", "tools/a/b", True),
        ("tools/**", "tools", False), ("tools/**", "toolsx/a", False),
        ("tools/**", "tools/.hidden", True),
        ("**/secret.txt", "secret.txt", True), ("**/secret.txt", "a/b/secret.txt", True),
        ("**/secret.txt", "a/xsecret.txt", False),
        ("a/**/b.txt", "a/b.txt", True), ("a/**/b.txt", "a/x/y/b.txt", True),
        ("a.md", "a.md", True), ("a.md", "aamd", False),
    ):
        cases.check(matches(pattern, path) == want,
                    f"{pattern!r} should {'' if want else 'not '}match {path!r}")

    # Markers.
    clean(cases, el.parse_markers(b"id-one\tfixture [0-9]+\n", "m", False), "a clean marker")
    for source in (r"\bD-[0-9]+\b", r"(?<=a)b", r"x(?=y)"):
        clean(cases, el.parse_markers(b(f"id-one\t{source}\n"), "m", False),
              f"a marker {source!r} that always spans a character")
    for text, needle, label in (
        ("Bad_ID\tx\n", "is not lowercase", "a marker id with capitals"),
        ("id-one\tx\nid-one\ty\n", "repeats the id of line 1", "a duplicate id"),
        ("id-one x\n", "is not ID<TAB>REGEX", "a marker with no tab"),
        ("id-one\tx\ty\n", "has 3 tab-separated fields", "a tab inside a marker's pattern"),
        ("id-one\t(\n", "does not compile", "a pattern that does not compile"),
        ("id-one\t[z-a]\n", "does not compile (bad character range z-a)",
         "a public marker's compiler message"),
        ("id-one\tx*\n", "can match an empty string", "a pattern matching the empty string"),
        ("id-one\t\\b\n", "can match an empty string", "a word boundary alone"),
        ("id-one\t(?=x)\n", "can match an empty string", "a lookahead alone"),
        ("id-one\t$\n", "can match an empty string", "an end anchor alone"),
        ("id-one\tx|\n", "can match an empty string", "an empty alternative"),
        ("# none\n", "has no markers", "a public marker file with no marker"),
    ):
        refused(cases, el.parse_markers(b(text), "m", False), needle, label)
    clean(cases, el.parse_markers(b"# none\n", "m", True), "an empty private marker file")
    _, findings = el.parse_markers(b"Secret_Shape\tx\n", "m", True, show=False)
    cases.check(findings and not any("Secret_Shape" in f for f in findings),
                f"a private marker finding should not quote the id: {findings!r}")
    for source, fragment in (("(?P<qzx-part>x)", "qzx"), ("\\qzx", "\\q"), ("[z-a]", "z-a"),
                             ("(?P=qzxname)", "qzx"), ("x{2,1}", "2,1")):
        _, findings = el.parse_markers(b(f"sample-shape\t{source}\n"), "m", True, show=False)
        cases.check(findings == ["m:1: the pattern does not compile"]
                    and not any(fragment in f for f in findings),
                    f"a private marker {source!r} should fail without its compiler message: "
                    f"{findings!r}")

    # A compiler warning is a finding, with its message only for a public marker, and is never
    # passed to the warnings module's output, even for a pattern re has compiled before or one
    # that warns and then fails to compile.
    for source, words in (("[[qzx]", "nested set"), ("[a&&qzx]", "set intersection"),
                          ("[*--qzx]", "set difference"), ("[qzx||y]", "set union"),
                          ("[qzv--x]", "set difference")):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                re.compile(source)  # put the pattern in re's cache first
            except re.error:
                pass
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _, public = el.parse_markers(b(f"id-one\t{source}\n"), "m", False)
            _, private = el.parse_markers(b(f"sample-shape\t{source}\n"), "m", True, show=False)
        cases.check(len(public) == 1 and "the regular expression compiler warns about the "
                    "pattern" in public[0] and words in public[0].lower(),
                    f"a public marker {source!r} the compiler warns about: {public!r}")
        cases.check(private == ["m:1: the regular expression compiler warns about the pattern"],
                    f"a private marker {source!r} the compiler warns about should fail with no "
                    f"detail: {private!r}")
        cases.check(not caught, f"a marker {source!r} should send no warning to the warnings "
                    f"module's output: {[str(w.message) for w in caught]!r}")

    # A pattern whose shortest match cannot be worked out is refused for that reason.
    class BrokenParser:
        @staticmethod
        def parse(_source):
            raise RuntimeError("the parser failed")

    saved_parser = el.regex_parser
    el.regex_parser = BrokenParser
    try:
        _, findings = el.parse_markers(b"id-one\tfixture [0-9]+\n", "m", False)
    finally:
        el.regex_parser = saved_parser
    cases.check(findings == ["m:1: the shortest match of the pattern cannot be worked out, so it "
                             "is refused"],
                f"a marker whose shortest match cannot be worked out: {findings!r}")

    # Protected terms.
    terms, findings = el.parse_terms(b(f"# synthetic\n{TERM_A}\n{TERM_B}\n"))
    cases.check(not findings and [t.text for t in terms] == [TERM_A, TERM_B],
                f"two synthetic terms should parse: {terms!r}, {findings!r}")
    for text, needle, label in (
        (f"{TERM_A}\n{TERM_A.lower()}\n", "repeats the term of line 1", "a duplicate term"),
        (f" {TERM_A}\n", "leading or trailing whitespace", "a term with a leading space"),
        (f"{TERM_A} \n", "leading or trailing whitespace", "a term with a trailing space"),
        (f"{TERM_A}\tx\n", "holds a tab", "a term with a tab"),
        ("# none\n", "has no terms", "an empty terms list"),
    ):
        _, findings = el.parse_terms(b(text))
        cases.check(any(needle in f for f in findings), f"{label}: {findings!r}")
        cases.check(not any(TERM_A.lower() in f.lower() for f in findings),
                    f"{label}: a terms finding should not quote the term: {findings!r}")
    regex = el.term_regex(TERM_A)
    for text, want in ((f"a {TERM_A.lower()}'s note", True), (TERM_A.upper(), True),
                       (f"{TERM_A}s", False), (f"x{TERM_A}", False), (f"_{TERM_A}", False)):
        cases.check(bool(regex.search(text)) == want,
                    f"the term should {'' if want else 'not '}match {text!r}")
    cases.check(bool(el.term_regex("Zorb.Q").search("see Zorb.Q.")),
                "a term ending in punctuation should match before a full stop")

    # Exceptions.
    sha = "a" * 64
    ids = {"id-one"}
    priv_terms = {TERM_A.casefold()}
    row = f"docs/a.md\t3\t{sha}\tmarker:id-one\ta reason\n"
    clean(cases, el.parse_exceptions(b(row), "x", ids), "a clean exception")
    clean(cases, el.parse_exceptions(b(f"docs/a.md\t3\t{sha}\tterm:{TERM_A.upper()}\tr\n"), "x",
                                     ids, priv_terms), "a private exception naming a term")
    for text, terms_, needle, label in (
        ("docs/a.md\t3\t" + sha + "\tmarker:id-one\n", None, "not 5", "four fields"),
        (row.replace("docs/a.md", "docs/*.md"), None, "exact path is needed", "a glob path"),
        (row.replace("\t3\t", "\t0\t"), None, "whole number from 1", "line 0"),
        (row.replace("\t3\t", "\t03\t"), None, "without leading zeros", "a leading zero"),
        (row.replace(sha, sha.upper()), None, "64 lowercase", "an uppercase digest"),
        (row.replace(sha, sha[:-1]), None, "64 lowercase", "a short digest"),
        (row.replace("marker:id-one", "marker:id-two"), None, "does not hold", "an unknown id"),
        (row.replace("marker:id-one", f"term:{TERM_A}"), None, "cannot name a term",
         "a public exception naming a term"),
        (row.replace("marker:id-one", f"term:{TERM_B}"), priv_terms, "does not hold",
         "an unknown term"),
        (row.replace("marker:id-one", "id-one"), None, "neither marker:ID", "a bare id"),
        (row.replace("a reason", " "), None, "the reason is empty", "an empty reason"),
        (row.replace("a reason", "a reason "), None, "trailing whitespace", "a trailing space"),
        (row + row, None, "repeats the exception of line 1", "a duplicate exception"),
    ):
        _, findings = el.parse_exceptions(b(text), "x", ids, terms_)
        cases.check(any(needle in f for f in findings), f"{label}: {findings!r}")
    _, findings = el.parse_exceptions(b(f"docs/{TERM_A}/../a.md\t3\t{sha}\tmarker:id-one\tr\n"),
                                      "x", ids, priv_terms, show=False)
    cases.check(findings and not any(TERM_A in f for f in findings),
                f"a private exception finding should not quote the path: {findings!r}")


def tree_checks(cases):
    base = ("copy\tREADME.md\trequired\ncopy\talpha.md\trequired\n"
            + "".join(f"copy\t{p}\trequired\n" for p in el.PUBLIC_EXPORT_FILES))
    den_text = "deny\ttools/**\ndeny\tCLAUDE.md\n"
    paths = ["CLAUDE.md", "README.md", "alpha.md", "tools/x.py", *el.PUBLIC_EXPORT_FILES]
    pub, f1 = publish(base)
    den, f2 = deny(den_text)
    cases.check(not f1 and not f2 and not el.check_tree(pub, den, paths, ["alpha.md"]),
                f"a clean tree should pass: {f1 + f2 + el.check_tree(pub, den, paths, ['alpha.md'])!r}")

    def tree(pub_text, den_text_, paths_, guides, modes=None):
        p, fa = publish(pub_text)
        d, fb = deny(den_text_)
        return fa + fb + el.check_tree(p, d, paths_, guides, modes)

    def finds(pub_text, den_text_, paths_, guides, needle, label, modes=None):
        found = tree(pub_text, den_text_, paths_, guides, modes)
        cases.check(any(needle in f for f in found), f"{label}: {found!r}")

    def passes(pub_text, den_text_, paths_, guides, label, modes=None):
        found = tree(pub_text, den_text_, paths_, guides, modes)
        cases.check(not found, f"{label}: expected no finding, got {found!r}")

    finds(base, den_text, paths + ["beta.txt"], ["alpha.md"],
          "beta.txt: tracked, but no line", "an unlisted tracked path")
    finds(base + "copy\tgamma.md\trequired\n", den_text, paths, ["alpha.md"],
          "copy 'gamma.md' matches no tracked path", "a required copy line matching nothing")
    finds(base, den_text + "deny\tTODO.md\n", paths, ["alpha.md"],
          "deny 'TODO.md' matches no tracked path", "a deny line matching nothing")
    passes(base + "copy\tdocs/*.zip\toptional\nrender\tgamma.md\toptional\n", den_text, paths,
           ["alpha.md"], "optional copy and render lines matching nothing")
    passes(base, den_text + "deny\tsite/draft/**\toptional\n", paths, ["alpha.md"],
           "an optional deny line matching nothing")
    finds(base + "copy\tdocs/*.md\trequired\n", den_text + "deny\tdocs/secret.md\n",
          paths + ["docs/secret.md", "docs/open.md"], ["alpha.md"],
          "docs/secret.md: matched by the deny line", "a path both denied and published")
    finds(base + "copy\tdocs/*.md\trequired\nrender\tdocs/a*.md\trequired\n", den_text,
          paths + ["docs/ab.md"], ["alpha.md"], "docs/ab.md: matched by 2 lines",
          "a path two globs publish")
    finds(base, den_text + "deny\t**/*.py\n", paths, ["alpha.md"],
          "tools/x.py: kept private by 2 deny lines", "a path two deny lines keep private")
    passes(base, den_text + "deny\t**/*-latest.zip\toptional\n", paths, ["alpha.md"],
           "a deny glob that overlaps another, with no tracked path matching both")
    finds(base, den_text + "deny\t**/*-latest.zip\toptional\n", paths + ["tools/x-latest.zip"],
          ["alpha.md"], "tools/x-latest.zip: kept private by 2 deny lines",
          "a latest archive tracked under a denied directory")
    finds(base.replace("alpha.md\trequired", "alpha.md\toptional"), den_text, paths,
          ["alpha.md"], "alpha.md: needs its own exact copy line", "a guide marked optional")
    finds(base.replace("copy\talpha.md", "render\talpha.md"), den_text, paths, ["alpha.md"],
          "alpha.md: needs its own exact copy line", "a guide rendered")
    finds(base, den_text + "deny\talpha.md\n", paths, ["alpha.md"],
          "alpha.md: matched by the deny line", "a guide denied")
    finds(base.replace(f"copy\t{el.PUBLIC_MARKERS}\trequired\n", ""), den_text,
          [p for p in paths if p != el.PUBLIC_MARKERS], ["alpha.md"],
          f"{el.PUBLIC_MARKERS}: needs its own exact copy line", "a public export file left out")

    # A published tracked path must be a regular file with a name in the path set.
    glob = base + "copy\tdocs/*.md\trequired\n"
    for name, label in (("docs/a" + chr(0x200B) + "b.md", "a zero-width character"),
                        ("docs/" + chr(0xE9) + ".md", "a non-ASCII letter"),
                        ("docs/a b.md", "a space"), ("docs/a\nb.md", "a newline")):
        finds(glob, den_text, paths + [name], ["alpha.md"], "holds a character other than",
              f"a published name with {label}")
    passes(base, den_text + "deny\tdocs/**\n", paths + ["docs/a b.md"], ["alpha.md"],
           "a private name outside the path set")
    modes = {path: "100644" for path in paths}
    for name, mode, needle in (("docs/link.md", "120000", "it is a symbolic link"),
                               ("docs/sub.md", "160000", "it is a submodule"),
                               ("docs/odd.md", "100664", "it is git mode 100664")):
        finds(glob, den_text, paths + [name], ["alpha.md"], needle,
              f"a published {needle[6:]}", dict(modes, **{name: mode}))
    passes(glob, den_text, paths + ["docs/run.md"], ["alpha.md"], "a published executable file",
           dict(modes, **{"docs/run.md": "100755"}))
    passes(base, den_text, paths + ["tools/link"], ["alpha.md"], "a private symbolic link",
           dict(modes, **{"tools/link": "120000"}))


def write(root, relative, data, mode=None):
    path = Path(root) / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data if isinstance(data, bytes) else b(data))
    if mode is not None:
        path.chmod(mode)
    return path


def git(root, *args):
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, timeout=60)


def run(*args, env=None):
    result = subprocess.run([sys.executable, "-I", "-B", str(TOOL), *map(str, args)],
                            capture_output=True, text=True, timeout=120, env=env)
    return result.returncode, result.stdout + result.stderr


ALPHA = f"# Alpha\n\nA guide.\n\nIt cites D-999 and names {TERM_A}.\n"
FIXTURE_ALLOWLIST = ("copy\tREADME.md\trequired\ncopy\talpha.md\trequired\n"
                     "render\trendered.txt\trequired\n"
                     + "".join(f"copy\t{p}\trequired\n" for p in el.PUBLIC_EXPORT_FILES))


def fixture_checkout(root):
    """A small checkout: two root documents, a guide, a denied tool and the export files."""
    alpha_line = ALPHA.split("\n")[4].encode()
    write(root, "README.md", "# Readme\n")
    write(root, "CLAUDE.md", "# Adapter\n")
    write(root, "alpha.md", ALPHA)
    write(root, "rendered.txt", "rendered later\n")
    write(root, "tools/x.py", "print('x')\n")
    write(root, el.ALLOWLIST, FIXTURE_ALLOWLIST)
    write(root, el.PRIVATE_PATHS, "deny\tCLAUDE.md\ndeny\ttools/**\ndeny\texport/private-paths.txt\n")
    write(root, el.PUBLIC_MARKERS, "id-d\t\\bD-[0-9]+\\b\n")
    write(root, el.PUBLIC_EXCEPTIONS,
          f"alpha.md\t5\t{el.line_sha256(alpha_line)}\tmarker:id-d\ta synthetic case\n")


@isolated_git_environment()
def check_cli(cases):
    with tempfile.TemporaryDirectory() as directory:
        # git must not find a repository above the fixture, whatever TMPDIR is.
        os.environ["GIT_CEILING_DIRECTORIES"] = directory
        root = Path(directory) / "repo"
        root.mkdir()
        fixture_checkout(root)
        rc, out = run("--check", "--root", root)
        cases.check(rc == 2 and "git cannot list the tracked files" in out,
                    f"--check outside a git checkout should exit 2: {rc}, {out!r}")
        git(root, "init", "-q")
        git(root, "add", ".")
        rc, out = run("--check", "--root", root)
        cases.check(rc == 0 and "  ok    export lists: all 9 tracked paths" in out
                    and "  FAIL  " not in out, f"--check on a clean fixture: {rc}, {out!r}")
        write(root, "notes.txt", "untracked\n")
        rc, out = run("--check", "--root", root)
        cases.check(rc == 0, f"an untracked file should be left alone: {rc}, {out!r}")
        write(root, "beta.md", "# Beta\n\nAn untracked guide.\n")
        rc, out = run("--check", "--root", root)
        cases.check(rc == 0 and "each of the 1 tracked guides" in out,
                    f"an untracked guide should be left alone: {rc}, {out!r}")
        (root / "beta.md").unlink()
        git(root, "add", "notes.txt")
        rc, out = run("--check", "--root", root)
        cases.check(rc == 1 and "  FAIL  notes.txt: tracked, but no line" in out,
                    f"a tracked unlisted file should fail: {rc}, {out!r}")
        git(root, "rm", "-q", "--cached", "notes.txt")
        (root / "link.txt").symlink_to("README.md")
        write(root, el.ALLOWLIST, FIXTURE_ALLOWLIST + "copy\tlink.txt\trequired\n")
        git(root, "add", "link.txt")
        rc, out = run("--check", "--root", root)
        cases.check(rc == 1 and "  FAIL  'link.txt': published by the copy line" in out
                    and "it is a symbolic link, not a regular file" in out,
                    f"a tracked symbolic link that a copy line publishes should fail: {rc}, {out!r}")
        git(root, "rm", "-q", "--cached", "link.txt")
        (root / "link.txt").unlink()
        write(root, el.ALLOWLIST, FIXTURE_ALLOWLIST)
        write(root, "alpha.md", ALPHA.replace("D-999", "D-998"))
        rc, out = run("--check", "--root", root)
        cases.check(rc == 1 and "stale: alpha.md:5 no longer has the recorded SHA-256" in out,
                    f"a changed excepted line should fail: {rc}, {out!r}")
        write(root, "alpha.md", ALPHA)
        (root / el.PUBLIC_MARKERS).unlink()
        rc, out = run("--check", "--root", root)
        cases.check(rc == 2 and f"cannot read {el.PUBLIC_MARKERS}" in out,
                    f"a missing marker file should exit 2: {rc}, {out!r}")


def snapshot(directory):
    return sorted((p.name, p.stat().st_mode, p.stat().st_mtime_ns, p.read_bytes())
                  for p in Path(directory).iterdir())


def private_dir(parent, terms=f"{TERM_A}\n", markers=SAMPLE_MARKER + LINK_MARKER, exceptions=""):
    directory = Path(parent) / "private"
    directory.mkdir(mode=0o700)
    directory.chmod(0o700)
    write(directory, el.TERMS, terms, 0o600)
    write(directory, el.PRIVATE_MARKERS, markers, 0o600)
    write(directory, el.PRIVATE_EXCEPTIONS, exceptions, 0o600)
    return directory


def check_private_cli(cases):
    alpha_line = ALPHA.split("\n")[4].encode()
    good_row = f"alpha.md\t5\t{el.line_sha256(alpha_line)}\tterm:{TERM_A}\tsynthetic\n"
    rendered_row = f"rendered.txt\t1\t{'b' * 64}\tmarker:sample-shape\tsynthetic\n"
    secrets = (TERM_A, TERM_B, "sample-shape", "SMP-", "sample-link", "alpha.md", "synthetic")
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory) / "repo"
        root.mkdir()
        fixture_checkout(root)

        def case(label, want_rc, needle, extra=(), **lists):
            with tempfile.TemporaryDirectory() as holder:
                priv = private_dir(holder, **lists)
                before = snapshot(priv)
                rc, out = run("--check-private", "--private-dir", priv, "--root", root)
                cases.check(rc == want_rc and needle in out, f"{label}: {rc}, {out!r}")
                cases.check(not any(s in out for s in secrets + tuple(extra))
                            and str(priv) not in out,
                            f"{label}: the output should quote no list content: {out!r}")
                cases.check(snapshot(priv) == before,
                            f"{label}: the private directory should be left unchanged")

        case("a clean private directory", 0, "  ok    private lists: 1 protected terms, "
             "2 private markers and 2 exceptions parse; 1 exceptions match their lines in the "
             "checkout and 1 name rendered files, which this tool does not check; the private "
             "markers find both links into each of the 3 deny lines",
             exceptions=good_row + rendered_row)
        case("the list digests", 0, f"        {el.TERMS} sha256 "
             f"{hashlib.sha256(b(TERM_A + chr(10))).hexdigest()}")
        case("a duplicate term", 1, f"  FAIL  {el.TERMS}:2: repeats the term of line 1",
             terms=f"{TERM_A}\n{TERM_A.upper()}\n")
        case("an empty terms list", 1, "has no terms", terms="# none\n")
        case("a marker that does not compile", 1, f"{el.PRIVATE_MARKERS}:1: the pattern does "
             "not compile", markers="sample-shape\t(\n")
        case("a marker whose group name a compiler message would quote", 1,
             f"  FAIL  {el.PRIVATE_MARKERS}:1: the pattern does not compile\n",
             extra=("qzx",), markers="sample-shape\t(?P<qzx-part>x)\n")
        case("a marker whose bad escape a compiler message would quote", 1,
             f"  FAIL  {el.PRIVATE_MARKERS}:1: the pattern does not compile\n",
             extra=("qzx", "\\q"), markers="sample-shape\t\\qzx\n")
        case("a zero-width private marker", 1, f"{el.PRIVATE_MARKERS}:1: the pattern can match "
             "an empty string", extra=("qzx",), markers="sample-shape\t(?=qzx)\n")
        case("a tab inside a private marker's pattern", 1, f"{el.PRIVATE_MARKERS}:1: is not "
             "ID<TAB>REGEX: it has 3 tab-separated fields", extra=("qzx", "QZX"),
             markers="sample-shape\tQZX\tqzx\n")
        for source in ("[[qzx]", "[a&&qzx]", "[*--qzx]", "[qzv--x]"):
            case(f"a private marker the compiler warns about, {source}", 1,
                 f"  FAIL  {el.PRIVATE_MARKERS}:2: the regular expression compiler warns about "
                 "the pattern\n", extra=("qzx", "Warning", "position", "nested", "set "),
                 markers=LINK_MARKER + f"sample-shape\t{source}\n")
        case("private markers that miss the links into one deny line", 1,
             f"  FAIL  {el.PRIVATE_PATHS}:2: no private marker finds a github.com blob link into "
             "a path this deny line keeps private\n", extra=("tools/x",),
             markers=SAMPLE_MARKER + LINK_MARKER.replace("tools/|", ""))
        case("private markers that miss the raw link into a deny line", 1,
             f"  FAIL  {el.PRIVATE_PATHS}:1: no private marker finds a raw.githubusercontent.com "
             "link into a path this deny line keeps private\n",
             markers=SAMPLE_MARKER + "sample-link\tgithub\\.com/[^/\\s]+/secureconfig/blob/"
                                     "[^/\\s]+/(?:CLAUDE\\.md|tools/|export/private-paths\\.txt)\n")
        case("no private marker at all", 1, f"  FAIL  {el.PRIVATE_PATHS}:3: no private marker "
             "finds a raw.githubusercontent.com link", markers="# none\n")
        case("a stale private exception", 1, f"{el.PRIVATE_EXCEPTIONS}:1: stale: the line it "
             "names no longer has the recorded SHA-256",
             exceptions=good_row.replace(el.line_sha256(alpha_line), "c" * 64))
        case("an exception whose term is no longer on its line", 1, "stale: what it names no "
             "longer matches the line it names",
             terms=f"{TERM_A}\n{TERM_B}\n", exceptions=good_row.replace(TERM_A, TERM_B))
        case("an exception naming an unpublished path", 1, "names a path the allowlist does not "
             "publish", exceptions=good_row.replace("alpha.md", "CLAUDE.md"))

        def refusal(label, needle, prepare, *, relative=False, trailing=""):
            with tempfile.TemporaryDirectory() as holder:
                priv = private_dir(holder)
                target = prepare(Path(holder), priv)
                arg = os.path.relpath(target) if relative else str(target) + trailing
                rc, out = run("--check-private", "--private-dir", arg, "--root", root)
                cases.check(rc == 2 and needle in out and TERM_A not in out
                            and str(holder) not in out, f"{label}: {rc}, {out!r}")

        refusal("a missing directory", "does not exist, so the private lists were not supplied",
                lambda h, p: h / "absent")
        refusal("a relative path", "is not an absolute path", lambda h, p: p, relative=True)
        refusal("a symbolic link to the directory", "is a symbolic link",
                lambda h, p: (h / "link").symlink_to(p) or h / "link")
        refusal("a symbolic link given with a trailing slash", "is a symbolic link",
                lambda h, p: (h / "link").symlink_to(p) or h / "link", trailing="/")
        refusal("a file, not a directory", "is not a directory", lambda h, p: p / el.TERMS)
        refusal("a group-writable directory", "is group- or world-writable",
                lambda h, p: p.chmod(0o770) or p)
        refusal("a world-writable directory", "is group- or world-writable",
                lambda h, p: p.chmod(0o702) or p)
        refusal("a list with mode 0644", f"{el.TERMS} has mode 0644, not 0600",
                lambda h, p: (p / el.TERMS).chmod(0o644) or p)
        refusal("a list that is a symbolic link", f"{el.PRIVATE_MARKERS} is not a regular file",
                lambda h, p: ((p / el.PRIVATE_MARKERS).unlink(),
                              (p / el.PRIVATE_MARKERS).symlink_to(p / el.TERMS))[0] or p)
        refusal("a list that is a FIFO", f"{el.PRIVATE_EXCEPTIONS} is not a regular file",
                lambda h, p: ((p / el.PRIVATE_EXCEPTIONS).unlink(),
                              os.mkfifo(p / el.PRIVATE_EXCEPTIONS, 0o600))[0] or p)
        refusal("a missing list", f"the private directory has no {el.PRIVATE_EXCEPTIONS}",
                lambda h, p: (p / el.PRIVATE_EXCEPTIONS).unlink() or p)
        inside = root / "private-inside"
        inside.mkdir(mode=0o700)
        rc, out = run("--check-private", "--private-dir", inside, "--root", root)
        cases.check(rc == 2 and "is inside the repository worktree" in out,
                    f"a private directory inside the checkout: {rc}, {out!r}")
        rc, out = run("--check-private", "--private-dir", root.parent, "--root", root)
        cases.check(rc == 2 and "is inside the repository worktree, or holds it" in out,
                    f"a private directory holding the checkout: {rc}, {out!r}")

        # Where the private directory comes from.
        cases.check(el.private_directory(None, {}) == el.DEFAULT_PRIVATE_DIR
                    and el.private_directory(None, {el.PRIVATE_DIR_ENV: "/a"}) == "/a"
                    and el.private_directory("/b", {el.PRIVATE_DIR_ENV: "/a"}) == "/b"
                    and el.private_directory(None, {el.PRIVATE_DIR_ENV: ""}) == "",
                    "--private-dir wins over the environment variable, which wins over the "
                    "default, even when it is set to an empty value")
        with tempfile.TemporaryDirectory() as holder:
            priv = private_dir(holder)
            env = dict(os.environ, **{el.PRIVATE_DIR_ENV: str(priv)})
            rc, out = run("--check-private", "--root", root, env=env)
            cases.check(rc == 0 and "  ok    private lists" in out and str(priv) not in out,
                        f"the private directory named by {el.PRIVATE_DIR_ENV}: {rc}, {out!r}")
            env = dict(os.environ, **{el.PRIVATE_DIR_ENV: str(Path(holder) / "absent")})
            rc, out = run("--check-private", "--private-dir", priv, "--root", root, env=env)
            cases.check(rc == 0 and "  ok    private lists" in out,
                        f"--private-dir should win over {el.PRIVATE_DIR_ENV}: {rc}, {out!r}")
            env = dict(os.environ, **{el.PRIVATE_DIR_ENV: ""})
            rc, out = run("--check-private", "--root", root, env=env)
            cases.check(rc == 2 and "is not an absolute path" in out,
                        f"an empty {el.PRIVATE_DIR_ENV} should be refused: {rc}, {out!r}")

            # A usage error repeats no argument once one starts with --check-private or
            # --private-dir, since an argument may be the private directory's path.
            quiet = ("error: the arguments do not parse; with --check-private or --private-dir "
                     "no argument is repeated")
            stray = str(priv) + "-stray"
            for label, args in (
                ("a private directory given without --private-dir",
                 ("--check-private", "--root", root, stray)),
                ("an unknown option beside --private-dir",
                 ("--check", "--private-dir", priv, "--root", root, "--" + stray)),
                ("--check-private given a value", (f"--check-private={stray}", "--root", root)),
                ("--check-private beside --check", ("--check-private", "--check", stray)),
                ("--private-dir with no mode", (f"--private-dir={stray}",)),
            ):
                rc, out = run(*args)
                cases.check(rc == 2 and quiet in out and "usage:" in out
                            and str(holder) not in out and "stray" not in out,
                            f"{label}: a usage error should repeat no argument: {rc}, {out!r}")
            rc, out = run("--check", "--root", root, "stray-argument")
            cases.check(rc == 2 and "unrecognized arguments: stray-argument" in out
                        and quiet not in out,
                        f"a usage error without the private options names its argument: "
                        f"{rc}, {out!r}")
            # No abbreviated option is taken for --check-private.
            env = dict(os.environ, **{el.PRIVATE_DIR_ENV: str(Path(holder) / "absent")})
            rc, out = run("--check-priv", "--root", root, env=env)
            cases.check(rc == 2 and "usage:" in out and "private directory" not in out
                        and "private lists" not in out,
                        f"an abbreviated --check-private should not run: {rc}, {out!r}")

        # The lists are read through the directory as it was opened, even when another directory
        # takes its path after the checks.
        with tempfile.TemporaryDirectory() as holder:
            priv = private_dir(holder)
            fd = el.open_private_dir(str(priv), str(root))
            try:
                priv.rename(Path(holder) / "moved")
                private_dir(holder, terms=f"{TERM_B}\n")
                data = el.read_private(fd, el.TERMS)
            finally:
                os.close(fd)
            cases.check(data == b(f"{TERM_A}\n"),
                        f"the lists should be read from the directory first opened: {data!r}")

        # An unexpected error prints its type and nothing it carries.
        with tempfile.TemporaryDirectory() as holder:
            priv = private_dir(holder)
            saved = el.parse_terms

            def broken(*_args, **_kwargs):
                raise ValueError(f"{TERM_A} SMP-123")

            el.parse_terms = broken
            buffer = io.StringIO()
            try:
                with contextlib.redirect_stdout(buffer):
                    rc = el.main(["--check-private", "--private-dir", str(priv),
                                  "--root", str(root)])
            except Exception as exc:  # noqa: BLE001  the case fails, it does not stop the run
                rc = f"raised {type(exc).__name__}"
            finally:
                el.parse_terms = saved
            out = buffer.getvalue()
            cases.check(rc == 2 and "  FAIL  --check-private stopped on an unexpected ValueError"
                        in out and TERM_A not in out and "SMP-" not in out,
                        f"an unexpected error should print only its type: {rc}, {out!r}")


def verify_cases(cases):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        write(root, "docs/a.md", "one\ntwo D-999\nthree\n")
        line = el.line_sha256(b"two D-999")
        regex = {"marker:id-d": re.compile(r"\bD-[0-9]+\b")}

        def verify(text):
            rows, findings = el.parse_exceptions(b(text), "x", {"id-d"})
            return findings + el.verify_exceptions(rows, "x", root, regex.get)

        cases.check(not verify(f"docs/a.md\t2\t{line}\tmarker:id-d\tr\n"),
                    "a current exception should pass")
        for text, needle, label in (
            (f"docs/a.md\t2\t{'d' * 64}\tmarker:id-d\tr\n", "stale: docs/a.md:2 no longer has",
             "a changed line"),
            (f"docs/a.md\t4\t{line}\tmarker:id-d\tr\n", "past the end of the file",
             "a line past the end"),
            (f"docs/a.md\t1\t{el.line_sha256(b'one')}\tmarker:id-d\tr\n",
             "what it names no longer matches docs/a.md:1", "a line with no hit"),
            (f"docs/b.md\t1\t{line}\tmarker:id-d\tr\n", "cannot read docs/b.md", "a missing file"),
        ):
            found = verify(text)
            cases.check(any(needle in f for f in found), f"{label}: {found!r}")
        (root / "docs" / "link.md").symlink_to(root / "docs" / "a.md")
        found = verify(f"docs/link.md\t2\t{line}\tmarker:id-d\tr\n")
        cases.check(any("cannot read docs/link.md (it is a symbolic link)" in f for f in found),
                    f"an exception on a symbolic link: {found!r}")


def main():
    cases = Cases()
    try:
        shipped(cases)
        parsers(cases)
        tree_checks(cases)
        verify_cases(cases)
        check_cli(cases)
        check_private_cli(cases)
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, el.Refused) as exc:
        print(f"  FAIL  export-lists self-test could not run: {exc!r}")
        return 1
    if cases.failures:
        for failure in cases.failures:
            print(f"  FAIL  {failure}")
        return 1
    print(f"  ok    {cases.count} recorded cases for the export lists")
    return 0


if __name__ == "__main__":
    sys.exit(main())
