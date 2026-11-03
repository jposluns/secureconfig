#!/usr/bin/env python3
"""Check that each lastmod in site/sitemap.xml is the date its page last changed in git history.

WHY: tools/check_sitemap.py checks that each `lastmod` is a calendar date and reads no history, so
an edit to a listed page that left its `lastmod` alone stayed green, and the sitemap then told
crawlers the page had not changed. The rule this gate holds is that a page's `lastmod` is the
date of the last commit that changed the page's file.

WHAT IT CHECKS, reading only local git objects and the working tree:

  - the repository root is the top level of a git work tree, so a tarball, or a copy without its
    .git that sits inside some other work tree, is refused; the repository is not a shallow clone;
    and HEAD is a commit. Otherwise it prints one FAIL line saying the history is unavailable and
    exits 2, so it never passes without the history. CI's checkout fetches the full history
    (fetch-depth 0 in .github/workflows/checks.yml);
  - site/sitemap.xml is a regular file, not a symbolic link, that check_sitemap.parse_sitemap
    parses with no finding, and it lists at least one `url`;
  - each `url` holds exactly one `loc` and one `lastmod`, and check_sitemap.page_of maps its `loc`
    to a page that exists as a regular file: site/index.html for `/` and site/<path>/index.html
    for `/<path>/`, at any depth, so every listed page is dated by its own file. While the site
    is staged (tools/check_draft.py's BASE is not `/`), a `loc` under BASE maps to no page and is
    refused, as is a `loc` in any other form;
  - a page that git status shows as changed (staged, unstaged or untracked) has no commit date
    yet, so its `lastmod` must be today's date in UTC, the date its commit gets when made today
    in UTC. This project runs the suite on the staged tree before committing, so that run passes
    for an edited page. A commit made on a later UTC day than the run, or recorded in an offset
    whose date differs, gets another date, and CI fails until the `lastmod` is set to it. The
    check reads git's own status, so a file a contributor marked assume-unchanged or skip-worktree
    shows no change and is dated as committed; that deliberate mark is outside this check;
  - for a page with no such change, the `lastmod` equals `git log -1 --format=%cs -- <page>`: the
    committer date, in the offset the committer recorded, of the last commit that changed the
    file, which CI checks on the committed tree. A mismatch names the page, the commit, both dates
    and the date to write.

MERGES: the log uses git's default history simplification, not --first-parent. A merge whose
version of the page equals one parent's is not counted, and the log follows that parent, so a
pull request merged with a merge commit on a later day keeps the date of its own commit that
changed the page. First-parent history would count the merge instead, whose date no contributor
can know when writing the page. That the log skips, in the same way, the test merge that a pull
request run checks out is inferred from this rule, not observed in CI. A merge whose page
differs from both parents, because both sides changed it, is counted with its own date.
Rewriting a commit (an amend, a rebase, a cherry-pick, or a squash or rebase merge) gives it a
new committer date, so its `lastmod` must be set again.

KEEPING IT GREEN: change the page and set its `lastmod` to the date you commit on, in the time
zone your commit records, in one commit, and rerun this gate. A run before the commit accepts
today's UTC date for the edited page; commit on that UTC day, or set the date again, so CI passes
on the committed tree. On a mismatch, set the `lastmod` to the date the finding names; a commit
that changes only site/sitemap.xml does not move that date.

WHERE IT RUNS: in tools/run_all_checks.sh only, after tools/check_sitemap.py. It is not in
scripts/pages-build.sh, the Pages build check, because that build may run without the history,
where this gate fails closed.

WHAT IT DOES NOT CHECK: the sitemap's form and coverage, which tools/check_sitemap.py checks; that
a committer recorded a true date, since git takes the committer date from the committer; or what a
host or crawler does with the file.

Exit 0 with one ok line, 1 with one FAIL line per finding, or 2 with one FAIL line when the
history cannot be read.
"""
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_sitemap import SITEMAP, page_of, parse_sitemap, regular  # noqa: E402

# Pinned so a user's log.follow or log.showSignature cannot change what the log reports.
GIT = ("git", "-c", "log.follow=false", "-c", "log.showSignature=false")


class NoHistory(Exception):
    """Git or the repository's history cannot be read, so no lastmod can be dated."""


def git(root, *args):
    """Run git in root and return its standard output; raise NoHistory when it fails."""
    try:
        done = subprocess.run([*GIT, *args], cwd=root, capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError) as exc:
        raise NoHistory(f"git {args[0]} could not run: {exc}") from exc
    if done.returncode:
        detail = done.stderr.decode("utf-8", "replace").strip() or f"exit {done.returncode}"
        raise NoHistory(f"git {' '.join(args[:2])} failed: {detail}")
    return done.stdout.decode("utf-8")


def history(root):
    """Raise NoHistory unless root is the top level of a work tree with its full history."""
    top = git(root, "rev-parse", "--show-toplevel").strip()
    if Path(top).resolve() != root.resolve():
        raise NoHistory(f"git finds the work tree {top}, not {root}, so {root} has no history "
                        f"of its own")
    if git(root, "rev-parse", "--is-shallow-repository").strip() != "false":
        raise NoHistory("the repository is a shallow clone, so a page's last change may lie "
                        "outside the fetched history")
    try:
        git(root, "rev-parse", "--verify", "--quiet", "HEAD^{commit}")
    except NoHistory as exc:
        raise NoHistory(f"HEAD is not a commit: {exc}") from exc


def check(root):
    """(findings, lastmods checked) for the sitemap under `root`; raises NoHistory."""
    history(root)
    reason = regular(root, SITEMAP)
    if reason:
        return [reason], 0
    try:
        text = (root / SITEMAP).read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"cannot read {SITEMAP} as UTF-8: {exc}"], 0
    entries, parsed = parse_sitemap(text)
    if parsed:
        return parsed, 0
    if not entries:
        return [f"{SITEMAP} lists no <url>, so no lastmod was checked"], 0

    findings, checked = [], 0
    for entry in entries:
        line = f"{SITEMAP}:{entry['line']}"
        if len(entry["loc"]) != 1 or len(entry["lastmod"]) != 1:
            findings.append(f"{line}: a <url> must hold exactly one <loc> and one <lastmod>; it "
                            f"holds {len(entry['loc'])} and {len(entry['lastmod'])}")
            continue
        loc, lastmod = entry["loc"][0].strip(), entry["lastmod"][0].strip()
        page, reason = page_of(loc)
        if reason:
            findings.append(f"{line}: {reason}, so its lastmod cannot be dated")
            continue
        reason = regular(root, page)
        if reason:
            findings.append(f"{line}: loc {loc!r} names {page}, but {reason}")
            continue
        status = git(root, "status", "--porcelain=v1", "--untracked-files=all", "--",
                     page.as_posix()).strip()
        if status:
            today = datetime.now(timezone.utc).date().isoformat()
            checked += 1
            if lastmod != today:
                findings.append(f"{line}: {page} has a change that is not committed ({status!r}), "
                                f"so its lastmod must be today's UTC date, {today}, the date its "
                                f"commit gets when made today in UTC, but its lastmod is "
                                f"{lastmod!r}; a commit made on a later UTC day fails CI until "
                                f"the lastmod is set to that day")
            continue
        last = git(root, "log", "-1", "--format=%h %cs", "--", page.as_posix()).split()
        if len(last) != 2:
            findings.append(f"{line}: no commit in this history changed {page}, so its lastmod "
                            f"cannot be dated")
            continue
        commit, changed = last
        checked += 1
        if lastmod != changed:
            findings.append(f"{line}: {page} last changed in commit {commit} on {changed} "
                            f"(git log -1 --format=%cs -- {page}), but its lastmod is "
                            f"{lastmod!r}; set the lastmod of {loc} to {changed}")
    return findings, checked


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        findings, count = check(root)
    except NoHistory as exc:
        print(f"  FAIL  git history is unavailable, so no lastmod in {SITEMAP} was checked: {exc}. "
              f"This gate needs the full history, which CI fetches with fetch-depth 0; it fails "
              f"rather than pass without it")
        return 2
    if findings:
        for finding in findings:
            print(f"  FAIL  {finding}")
        return 1
    print(f"  ok    all {count} lastmod(s) in {SITEMAP} equal the committer date of the last "
          f"commit that changed their page (git log -1 --format=%cs), or today's UTC date for a "
          f"page with a change that is not committed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
