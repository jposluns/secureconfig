#!/usr/bin/env python3
"""Cases for check_sitemap_lastmod.py: a current lastmod passes; a stale one or no history fails.

Each case builds a throwaway git repository whose commits carry fixed committer dates, with folder
pages, site/robots.txt and site/sitemap.xml under site/. It copies the shipped gate and the
modules it imports (check_sitemap.py, check_draft.py, check_csp_hashes.py) into the fixture's
tools/, untracked, and runs the gate as a subprocess under `python3 -I -B`, so what is under test
is the shipped entry point against real history. Git runs with no system or global configuration,
and discovery stops at each case's own temporary directory. A must-fail case names the exit status
and the substrings its finding must carry; a pass must print one ok line and no FAIL line.

Each run sets the BASE line of the fixture's copy of check_draft.py to the case's base, so the
cases hold whichever base the shipped file names. The base-path cases take their pages from
scripts/build-site.py. At base /draft/ the staged build sits under site/draft/, unlisted and
undated, beside a live root page. At base /, the shipped value since promotion, the promoted
build (`--base / --out <fixture>/site`) puts the template pages at the root, and writes no page
under draft/ (the live site carries no /draft/ page, baseline SPECIFICATION section 4.1 item 0),
where the sitemap lists the 7 indexable folder pages (INDEXABLE in check_draft.py), each dated by
its own file. One case adds a /draft/ loc with a stale lastmod, and a committed page at
site/draft/index.html, to that sitemap: check_sitemap.page_of refuses the loc by its first segment
at any base, so this gate does not date it. check_sitemap.py also runs on 3 fixtures: it accepts
the stale one, so the staleness is caught only by this gate; it accepts the promoted one, so that
sitemap is one the site could ship; and it refuses the one listing /draft/.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
from check_draft import INDEXABLE  # noqa: E402  (the pages a shipped sitemap lists)

BUILD = TOOLS.parent / "scripts" / "build-site.py"
GATES = ("check_sitemap_lastmod.py", "check_sitemap.py", "check_draft.py", "check_csp_hashes.py")
# The line of check_draft.py that sets the base path, which each run sets to its own base.
BASE_LINE = re.compile(r'^BASE = "[^"\n]*"$', re.M)
ROBOTS = "User-agent: *\nAllow: /\n\nSitemap: https://secureconfig.ai/sitemap.xml\n"
# Twelve lines, so edits to the first and the last line merge without a conflict.
LINES = [f"<p>line {n}</p>\n" for n in range(12)]


def page(title, lines=LINES):
    return f'<!doctype html>\n<meta charset="utf-8">\n<title>{title}</title>\n' + "".join(lines)


def sitemap(*entries):
    """A sitemap of (URL path, lastmod) entries."""
    body = "".join(f"  <url>\n    <loc>https://secureconfig.ai{path}</loc>\n"
                   f"    <lastmod>{lastmod}</lastmod>\n  </url>\n" for path, lastmod in entries)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n")


def environment(ceiling, when=None):
    """The caller's environment without Git selectors, with discovery stopped at `ceiling`."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_CEILING_DIRECTORIES=str(ceiling))
    if when:
        env.update(GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
    return env


class Repo:
    """A fixture repository at tmp/repo, with git discovery stopped at tmp."""

    def __init__(self, tmp, name="repo"):
        self.tmp, self.root = tmp, tmp / name
        self.root.mkdir(parents=True)
        self.git("init", "-q")

    def git(self, *args, when=None):
        done = subprocess.run(
            ["git", "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
             "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main", *args],
            cwd=self.root, capture_output=True, text=True, env=environment(self.tmp, when),
            timeout=60)
        assert done.returncode == 0, (args, done.returncode, done.stdout + done.stderr)
        return done.stdout.strip()

    def write(self, files):
        for relative, text in files.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    def commit(self, when, files=None, message="change"):
        """Commit `files` (relative path: text) and anything else changed, dated `when`."""
        self.write(files or {})
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message, when=when)


def start(tmp, lastmod="2026-10-01", when="2026-10-01T12:00:00+00:00"):
    """A repository whose one commit holds the home page and a sitemap listing it."""
    repo = Repo(tmp)
    repo.commit(when, {"site/index.html": page("home"), "site/robots.txt": ROBOTS,
                       "site/sitemap.xml": sitemap(("/", lastmod))})
    return repo


def install(root, base):
    """Copy the shipped gates into root/tools and set the copied check_draft.py's BASE to base."""
    (root / "tools").mkdir(exist_ok=True)
    for gate in GATES:
        shutil.copy(TOOLS / gate, root / "tools" / gate)
    draft = root / "tools" / "check_draft.py"
    text, count = BASE_LINE.subn(f'BASE = "{base}"', draft.read_text(encoding="utf-8"))
    assert count == 1, f"check_draft.py holds {count} BASE lines; this test sets exactly 1"
    draft.write_text(text, encoding="utf-8")


def run(root, ceiling, base="/draft/", gate="check_sitemap_lastmod.py"):
    install(root, base)
    r = subprocess.run([sys.executable, "-I", "-B", f"tools/{gate}"], cwd=root,
                       env=environment(ceiling), capture_output=True, text=True, timeout=60)
    return r.returncode, (r.stdout + r.stderr).strip()


def build(base, out):
    """Write the generator's pages for `base` under `out`; return their paths relative to out."""
    r = subprocess.run([sys.executable, "-I", "-B", str(BUILD), "--base", base, "--out", str(out)],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, ("build-site.py", base, r.stdout + r.stderr)
    return sorted(p.relative_to(out).as_posix() for p in out.rglob("*.html"))


def current(tmp):
    return start(tmp).root


def stale_repo(tmp):
    """The home page edited on 2026-10-05, after the sitemap dated it 2026-10-01."""
    repo = start(tmp)
    repo.commit("2026-10-05T12:00:00+00:00", {"site/index.html": page("home, edited")})
    return repo


def stale(tmp):
    return stale_repo(tmp).root


def fixed_later(tmp):
    repo = stale_repo(tmp)
    repo.commit("2026-10-06T12:00:00+00:00", {"site/sitemap.xml": sitemap(("/", "2026-10-05"))})
    return repo.root


def one_commit(tmp):
    repo = start(tmp)
    repo.commit("2026-10-05T12:00:00+00:00", {"site/index.html": page("home, edited"),
                                              "site/sitemap.xml": sitemap(("/", "2026-10-05"))})
    return repo.root


def west_of_utc(lastmod):
    # 23:30 at UTC-5 is 04:30 UTC the next day; %cs prints the committer's own date.
    return lambda tmp: start(tmp, lastmod, "2026-10-01T23:30:00-05:00").root


def merged_later(tmp):
    """A branch changes the page and its lastmod on 2026-10-03; main merges it on 2026-10-07."""
    repo = start(tmp)
    repo.git("checkout", "-q", "-b", "topic")
    repo.commit("2026-10-03T12:00:00+00:00", {"site/index.html": page("home, edited"),
                                              "site/sitemap.xml": sitemap(("/", "2026-10-03"))})
    repo.git("checkout", "-q", "main")
    repo.commit("2026-10-04T12:00:00+00:00", {"other.md": "unrelated\n"})
    repo.git("merge", "-q", "--no-ff", "-m", "Merge pull request #2 from o/topic", "topic",
             when="2026-10-07T12:00:00+00:00")
    # The fixture is only meaningful while first-parent history would date the page otherwise.
    assert repo.git("log", "-1", "--first-parent", "--format=%cs", "--",
                    "site/index.html") == "2026-10-07"
    return repo.root


def merged_both_sides(tmp):
    """Main and a branch change different lines of the page, so the merge's page is new."""
    repo = start(tmp)
    repo.git("checkout", "-q", "-b", "topic")
    repo.commit("2026-10-03T12:00:00+00:00",
                {"site/index.html": page("home", ["<p>branch</p>\n"] + LINES[1:]),
                 "site/sitemap.xml": sitemap(("/", "2026-10-03"))})
    repo.git("checkout", "-q", "main")
    repo.commit("2026-10-04T12:00:00+00:00",
                {"site/index.html": page("home", LINES[:-1] + ["<p>main</p>\n"])})
    repo.git("merge", "-q", "--no-ff", "-m", "Merge pull request #2 from o/topic", "topic",
             when="2026-10-07T12:00:00+00:00")
    return repo.root


def tarball(tmp):
    """The tree of a current repository, copied without its .git, as a release tarball holds it."""
    src = start(tmp).root
    dest = tmp / "export"
    shutil.copytree(src / "site", dest / "site")
    return dest


def shallow(tmp):
    src = stale(tmp)
    dest = tmp / "shallow"
    subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{src}", str(dest)],
                   check=True, capture_output=True, env=environment(tmp), timeout=60)
    return dest


def nested(tmp):
    """A copy without .git that sits, untracked, inside another repository's work tree."""
    outer = Repo(tmp, "outer")
    outer.commit("2026-10-01T12:00:00+00:00", {"README": "outer\n"})
    src = start(tmp / "source").root
    dest = outer.root / "export"
    shutil.copytree(src / "site", dest / "site")
    return dest


def uncommitted(tmp):
    repo = start(tmp)
    repo.write({"site/index.html": page("home, not committed")})
    return repo.root


def staged_edit(dated_today):
    """The home page edited and staged with its sitemap, as the suite runs before a commit."""
    def fixture(tmp):
        # Read when the fixture is built, so a run that crosses UTC midnight before the gate
        # reads the clock would see the next day.
        lastmod = datetime.now(timezone.utc).date().isoformat() if dated_today else "2026-10-01"
        repo = start(tmp)
        repo.write({"site/index.html": page("home, staged"),
                    "site/sitemap.xml": sitemap(("/", lastmod))})
        repo.git("add", "-A")
        return repo.root
    return fixture


def untracked(tmp):
    repo = start(tmp)
    repo.write({"site/guides/index.html": page("guides"),
                "site/sitemap.xml": sitemap(("/", "2026-10-01"), ("/guides/", "2026-10-01"))})
    return repo.root


def empty_sitemap(tmp):
    repo = start(tmp)
    repo.commit("2026-10-02T12:00:00+00:00", {"site/sitemap.xml": sitemap()})
    return repo.root


def unmapped(tmp):
    repo = start(tmp)
    repo.commit("2026-10-02T12:00:00+00:00",
                {"site/sitemap.xml": sitemap(("/", "2026-10-01"), ("/404.html", "2026-10-01"))})
    return repo.root


def missing_page(tmp):
    repo = start(tmp)
    repo.commit("2026-10-02T12:00:00+00:00",
                {"site/sitemap.xml": sitemap(("/", "2026-10-01"), ("/guides/", "2026-10-02"))})
    return repo.root


def staged_repo(tmp):
    """Base /draft/: the draft build lands on 2026-10-06 under site/draft/, beside the root page."""
    repo = start(tmp)
    pages = build("/draft/", repo.root / "site" / "draft")
    assert "guides/index.html" in pages, pages
    repo.commit("2026-10-06T12:00:00+00:00")
    return repo


def staged(tmp):
    return staged_repo(tmp).root


def staged_draft_listed(tmp):
    repo = staged_repo(tmp)
    repo.commit("2026-10-07T12:00:00+00:00", {"site/sitemap.xml": sitemap(
        ("/", "2026-10-01"), ("/draft/guides/", "2026-10-06"))})
    return repo.root


def promote(tmp, lastmod=lambda loc: "2026-10-08"):
    """Base /: on 2026-10-08 the draft is removed and the promoted build is written at the root.

    The sitemap lists the build's 7 indexable folder pages, `lastmod(loc path)` each; the root
    build writes no page under draft/. Returns the repo.
    """
    repo = staged_repo(tmp)
    repo.git("rm", "-r", "-q", "site/draft", "site/index.html")
    pages = build("/", repo.root / "site")
    folders = [p for p in pages if p.endswith("index.html")]
    assert not any(p.startswith("draft/") for p in pages), pages
    assert sorted(folders) == sorted(INDEXABLE), pages
    paths = ["/" + p[:-len("index.html")] for p in folders]
    repo.commit("2026-10-08T12:00:00+00:00",
                {"site/sitemap.xml": sitemap(*((p, lastmod(p)) for p in paths))})
    return repo


def promoted(tmp):
    return promote(tmp).root


def promoted_by_draft_date(tmp):
    # The root page is a new file; the draft copy it replaced dates nothing.
    return promote(tmp, lambda p: "2026-10-06" if p == "/guides/" else "2026-10-08").root


def promoted_subpage_stale(tmp):
    repo = promote(tmp)
    path = repo.root / "site" / "guides" / "index.html"
    repo.commit("2026-10-10T12:00:00+00:00",
                {"site/guides/index.html": path.read_text(encoding="utf-8") + "\n"})
    return repo.root


def promoted_subpage_current(tmp):
    repo = promote(tmp)
    path = repo.root / "site" / "guides" / "index.html"
    text = (repo.root / "site" / "sitemap.xml").read_text(encoding="utf-8")
    old = "/guides/</loc>\n    <lastmod>2026-10-08</lastmod>"
    assert text.count(old) == 1, text
    repo.commit("2026-10-10T12:00:00+00:00", {
        "site/guides/index.html": path.read_text(encoding="utf-8") + "\n",
        "site/sitemap.xml": text.replace(old, old.replace("2026-10-08", "2026-10-10"))})
    return repo.root


def promoted_draft_loc(tmp):
    # The live site carries no /draft/ page, so at base / check_sitemap.page_of refuses a /draft/
    # loc by its first segment and this gate does not date it, even with a page committed at
    # site/draft/index.html (2026-10-09 here) and a stale lastmod on the loc.
    repo = promote(tmp)
    text = (repo.root / "site" / "sitemap.xml").read_text(encoding="utf-8")
    assert "/draft/</loc>" not in text and text.count("</urlset>") == 1, text
    entry = ("  <url>\n    <loc>https://secureconfig.ai/draft/</loc>\n"
             "    <lastmod>2026-10-06</lastmod>\n  </url>\n")
    repo.commit("2026-10-09T12:00:00+00:00",
                {"site/draft/index.html": page("draft"),
                 "site/sitemap.xml": text.replace("</urlset>\n", entry + "</urlset>\n")})
    return repo.root


# (description, fixture, base, expected exit, substrings a refusal's output must carry)
CASES = [
    ("a current lastmod", current, "/draft/", 0, ()),
    ("a stale lastmod after a later page edit", stale, "/draft/", 1,
     ("site/index.html last changed in commit", "on 2026-10-05", "its lastmod is '2026-10-01'",
      "set the lastmod of https://secureconfig.ai/ to 2026-10-05")),
    ("a later commit to the sitemap alone that sets the named date", fixed_later, "/draft/", 0,
     ()),
    ("the page edit and its lastmod in one commit", one_commit, "/draft/", 0, ()),
    ("a committer west of UTC, dated in its own offset", west_of_utc("2026-10-01"), "/draft/", 0,
     ()),
    ("a committer west of UTC, dated by the UTC day", west_of_utc("2026-10-02"), "/draft/", 1,
     ("on 2026-10-01", "its lastmod is '2026-10-02'")),
    ("a pull request merged on a later day keeps its own commit's date", merged_later, "/draft/",
     0, ()),
    ("a merge whose page differs from both parents is dated by the merge", merged_both_sides,
     "/draft/", 1, ("on 2026-10-07", "its lastmod is '2026-10-03'")),
    ("missing history: a tree without .git", tarball, "/draft/", 2,
     ("git history is unavailable", "not a git repository")),
    ("missing history: a shallow clone", shallow, "/draft/", 2,
     ("git history is unavailable", "shallow clone")),
    ("missing history: a copy inside another work tree", nested, "/draft/", 2,
     ("git history is unavailable", "has no history of its own")),
    ("a listed page with an uncommitted edit", uncommitted, "/draft/", 1,
     ("site/index.html has a change that is not committed", "must be today's UTC date")),
    ("a listed page that was never committed", untracked, "/draft/", 1,
     ("site/guides/index.html has a change that is not committed", "must be today's UTC date")),
    ("a staged page edit dated today in UTC, before its commit", staged_edit(True), "/draft/", 0,
     ()),
    ("a staged page edit dated another day", staged_edit(False), "/draft/", 1,
     ("site/index.html has a change that is not committed", "must be today's UTC date",
      "its lastmod is '2026-10-01'", "after committing, CI fails if the recorded committer date differs from the lastmod")),
    ("a sitemap with no url", empty_sitemap, "/draft/", 1, ("lists no <url>",)),
    ("a loc this gate cannot map to a page", unmapped, "/draft/", 1,
     ("the only URL form this gate maps to a page", "cannot be dated")),
    ("a listed page that does not exist", missing_page, "/draft/", 1,
     ("site/guides/index.html is missing",)),
    ("base /draft/: the draft build, unlisted, beside a current root page", staged, "/draft/", 0,
     ()),
    ("base /draft/: a listed draft page", staged_draft_listed, "/draft/", 1,
     ("is a /draft/ page", "cannot be dated")),
    ("base /: the 7 indexable promoted pages, each dated by the promotion", promoted, "/", 0, ()),
    ("base /: a promoted page dated by its draft copy", promoted_by_draft_date, "/", 1,
     ("site/guides/index.html last changed", "on 2026-10-08", "its lastmod is '2026-10-06'")),
    ("base /: a promoted subpage edited later, its lastmod left", promoted_subpage_stale, "/", 1,
     ("site/guides/index.html last changed", "on 2026-10-10",
      "set the lastmod of https://secureconfig.ai/guides/ to 2026-10-10")),
    ("base /: a promoted subpage edited later, with its lastmod", promoted_subpage_current, "/",
     0, ()),
    ("base /: a /draft/ loc is refused, not dated, even with a page under site/draft/",
     promoted_draft_loc, "/", 1,
     ("is a /draft/ page; the live site carries no /draft/ page", "cannot be dated")),
]
# check_sitemap.py, which reads no history, on 3 of the fixtures above (same columns as CASES).
FORM_CASES = [
    ("check_sitemap.py on the stale lastmod, which only this gate catches", stale, "/draft/", 0,
     ()),
    ("check_sitemap.py on the promoted sitemap, one the site could ship", promoted, "/", 0, ()),
    ("check_sitemap.py on a promoted sitemap listing /draft/", promoted_draft_loc, "/", 1,
     ("is a /draft/ page; the live site carries no /draft/ page",)),
]


def verdict(desc, rc, out, expected, wanted):
    """The failures for one run, as display strings."""
    failures = []
    if rc != expected:
        failures.append(f"{desc}: expected exit {expected}, got {rc}: {out!r}")
    elif expected == 0 and ("  FAIL  " in out or not out.startswith("ok    ")):
        failures.append(f"{desc}: a pass must print one ok line and no FAIL line: {out!r}")
    elif expected != 0 and not out.startswith("FAIL  "):
        failures.append(f"{desc}: a refusal must print a FAIL line: {out!r}")
    for text in wanted:
        if text not in out:
            failures.append(f"{desc}: expected the output to contain {text!r}: {out!r}")
    if "Traceback (most recent call last):" in out:
        failures.append(f"{desc}: the gate crashed: {out!r}")
    return failures


def main() -> int:
    failures = []
    for desc, fixture, base, expected, wanted in CASES:
        tmp = Path(tempfile.mkdtemp())
        try:
            root = fixture(tmp)
            rc, out = run(root, tmp, base)
            failures += verdict(desc, rc, out, expected, wanted)
        except AssertionError as exc:
            failures.append(f"{desc}: the fixture could not be built: {exc}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    for desc, fixture, base, expected, wanted in FORM_CASES:
        tmp = Path(tempfile.mkdtemp())
        try:
            root = fixture(tmp)
            rc, out = run(root, tmp, base, gate="check_sitemap.py")
            failures += verdict(desc, rc, out, expected, wanted)
        except AssertionError as exc:
            failures.append(f"{desc}: the fixture could not be built: {exc}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    if failures:
        for f in failures:
            print(f"  FAIL  {f}")
        return 1
    print(f"  ok    {len(CASES) + len(FORM_CASES)} recorded cases for the sitemap lastmod gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
