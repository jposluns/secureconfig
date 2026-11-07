#!/usr/bin/env python3
"""Report bundled guides whose recorded version basis an upstream GitHub release has passed.

The plugin bundles its guides so that it works with no network, and each guide records, in its
machine-readable version-basis block, the release of each component it was written against.
This script reads those blocks from the bundled references and, only when it is run with
--check-online, asks GitHub's latest-release API whether each upstream has published a newer
release than the recorded basis.

Egress is opt-in. Without --check-online the script makes no network request: it prints what it
would check and says that egress is needed. With --check-online it sends one GET per upstream
repository to https://api.github.com/repos/OWNER/REPO/releases/latest, with GITHUB_TOKEN or
GH_TOKEN as a bearer token when either is set. --guide NAME, which can be repeated, limits the
run to the named guides, and --references DIR reads another folder of guides.

It skips the cases it can detect that it cannot establish. A component is skipped, and listed
under "Not automatically checkable", when no source is a github.com blob, tree or releases URL
with no explicit port, when its sources name more than one GitHub repository, or when its basis
is not a clean dotted-numeric release of at least three parts (a commit, a range, a date, a
series such as 2.4 or 4.x, a pre-release or packaging suffix, or unknown). Any network, HTTP,
JSON or rate-limit problem, a latest release marked draft or pre-release, and any latest-release
tag that is not a clean release with the same tool prefix as the basis are listed under "Could
not check", never as drift.

A reported drift is a prompt to verify, not a certainty. A repository that releases several
packages under plain version tags with no package prefix passes those checks, but its latest
release may be another package's, and the script cannot tell that it is not this component's.
The script also does not look for an issue that is already open for the same drift.

Drift means only that upstream published a newer release than the recorded basis. It does not
mean the guide is wrong; nobody has yet checked whether the newer release changes its guidance.

With --file, after the report, each drift or major row can be opened as an issue on the
secureconfig repository, through an authenticated gh or a token, and only after the person
running the script types yes at a prompt for that issue. Filing needs an interactive terminal:
when standard input is not a terminal, the script asks nothing and files nothing. Without an
interactive terminal, authentication or that answer, nothing is filed and the prefilled links
in the report are the way to report it.

Exit status: 0 whether or not drift is found, since drift is information and not an error; 2 on
a usage error: an unknown option, --file without --check-online, a references folder that does
not exist, or a --guide that names no guide in it.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ISSUES_REPO = 'jposluns/secureconfig'
ISSUE_NEW = 'https://github.com/' + ISSUES_REPO + '/issues/new'
API = 'https://api.github.com'
API_HOST = 'api.github.com'
USER_AGENT = 'secureconfig-check-updates'
START = '<!-- version-basis:start -->'
END = '<!-- version-basis:end -->'
TIMEOUT = 20
MAX_BYTES = 1 << 20
HERE = Path(__file__).resolve().parent
DEFAULT_REFERENCES = HERE.parent / 'references'
PLUGIN_JSON = HERE.parent.parent.parent / 'plugin.json'

DRIFT = 'Currency drift'
MAJOR = 'Major available'
COULD_NOT = 'Could not check'
NOT_CHECKABLE = 'Not automatically checkable'
GROUPS = (DRIFT, MAJOR, COULD_NOT, NOT_CHECKABLE)


class UsageError(Exception):
    """A usage error; the script exits 2."""


# ---------------------------------------------------------------- reading the guides

def _no_duplicates(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('duplicate key: ' + key)
        result[key] = value
    return result


def _refuse_constant(value):
    raise ValueError('non-JSON number: ' + value)


_EOF_JSON = re.compile(r'\n(?P<fence>`{3,})json\n(?P<json>.*?)\n(?P=fence)\n\Z', re.S)


def guide_metadata(text):
    """Return a guide's version-basis object in either layout, or None when none parses.

    The legacy layout is front matter: a first line of three hyphens, then a line starting
    'version_basis: ' with one JSON object, then a closing line of three hyphens. The two-section
    layout holds the JSON in a json fence that closes immediately before the end marker of the
    version-basis section. Anything else, including invalid JSON, duplicate keys or a
    components entry that is not an object, gives None, and the guide is skipped.
    """
    payload = None
    if text.startswith('---\n'):
        end = text.find('\n---\n', 4)
        if end != -1 and text[4:end].startswith('version_basis: '):
            payload = text[4 + len('version_basis: '):end]
    if payload is None:
        if text.count(START) != 1 or text.count(END) != 1:
            return None
        start, end = text.index(START), text.index(END)
        if start > end:
            return None
        match = _EOF_JSON.search(text[start:end])
        if match is None:
            return None
        payload = match['json']
    try:
        data = json.loads(payload, object_pairs_hook=_no_duplicates,
                          parse_constant=_refuse_constant)
    except ValueError:
        return None
    if not isinstance(data, dict) or not isinstance(data.get('components'), dict):
        return None
    return data


_OWNER = re.compile(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})')
_REPO = re.compile(r'[A-Za-z0-9._-]{1,100}')


def github_repo(url):
    """OWNER/REPO for an https://github.com/OWNER/REPO/(blob|tree|releases)/... URL, else None.

    A URL with any explicit port, 443 included, gives None: a canonical github.com URL has none.
    """
    if not isinstance(url, str):
        return None
    try:
        parts = urllib.parse.urlsplit(url)
        port = parts.port
    except ValueError:
        return None
    if (parts.scheme != 'https' or (parts.hostname or '') not in ('github.com', 'www.github.com')
            or parts.username is not None or port is not None):
        return None
    segments = parts.path.split('/')
    # '', OWNER, REPO, VIEW, ... : the view must be followed by something or end the path.
    if len(segments) < 4 or segments[0] != '' or segments[3] not in ('blob', 'tree', 'releases'):
        return None
    owner, repo = segments[1], segments[2]
    if (not _OWNER.fullmatch(owner) or not _REPO.fullmatch(repo) or repo in ('.', '..')
            or repo.endswith('.git')):
        return None
    return owner + '/' + repo


def repo_from_sources(sources):
    """(OWNER/REPO, None) for the component's one upstream repository, or (None, reason)."""
    if not isinstance(sources, dict):
        return None, 'sources is not a mapping'
    repos = []
    for url in sources.values():
        repo = github_repo(url)
        if repo and repo.lower() not in (known.lower() for known in repos):
            repos.append(repo)
    if not repos:
        return None, 'no source is a github.com blob, tree or releases URL'
    if len(repos) > 1:
        return None, 'sources name more than one GitHub repository (' + ', '.join(repos) + ')'
    return repos[0], None


_PREFIX = re.compile(r'@?[A-Za-z0-9][A-Za-z0-9._/-]*')
_RELEASE = re.compile(r'[0-9]+(?:\.[0-9]+){2,}')
_COMMIT = re.compile(r'(?:commit )?[0-9A-Fa-f]{7,40}')
_DATE = re.compile(r'[0-9]{4}-[0-9]{2}(?:-[0-9]{2})?')
_SUFFIXED = re.compile(r'[0-9]+(?:\.[0-9]+)+[-+][0-9A-Za-z.+-]+')
_RANGE = re.compile(r'\.\.|\s(?:to|through)\s|\+\Z|[0-9.]\s*-\s*v?[0-9]|[<>=~^*,]')
_SERIES = re.compile(r'(?:[0-9]+\.)*[0-9]+(?:\.[xX*])+|[xX]')
_PARTIAL = re.compile(r'[0-9]+(?:\.[0-9]+)?')


def parse_version(text):
    """((prefix, numbers), None) for a clean release, or (None, reason) to skip it.

    A leading tool prefix ending in '@' (n8n@, @sveltejs/kit@) is kept apart and a leading v is
    dropped. What remains must be at least three dot-separated numbers, such as 4.4.0, 26.8.0 or
    2026.09.0. A commit, unknown, a date, a range, a series (2.4, 4.x), a pre-release, build or
    packaging suffix, or any other form is skipped with its reason.
    """
    if not isinstance(text, str) or not text.strip():
        return None, 'no recorded basis'
    value = text.strip()
    if value == 'unknown':
        return None, 'basis is unknown'
    if _COMMIT.fullmatch(value):
        return None, 'basis is a commit'
    if _DATE.fullmatch(value):
        return None, 'basis is a date'
    prefix = ''
    if '@' in value:
        prefix, _, value = value.rpartition('@')
        if not _PREFIX.fullmatch(prefix):
            return None, 'basis is not a dotted numeric release'
    if value[:1] == 'v' and value[1:2].isdigit():
        value = value[1:]
    if _RELEASE.fullmatch(value):
        return (prefix, tuple(int(part) for part in value.split('.'))), None
    if _SUFFIXED.fullmatch(value):
        return None, 'basis has a pre-release, build or packaging suffix'
    if _RANGE.search(value):
        return None, 'basis is a range'
    if _SERIES.fullmatch(value) or _PARTIAL.fullmatch(value):
        return None, 'basis names a series, not a release'
    return None, 'basis is not a dotted numeric release'


def compare(basis, latest):
    """'drift' (newer, same major), 'major' (newer major) or 'current' (not newer)."""
    width = max(len(basis), len(latest))
    left = basis + (0,) * (width - len(basis))
    right = latest + (0,) * (width - len(latest))
    if right <= left:
        return 'current'
    return 'major' if right[0] > left[0] else 'drift'


def collect(references, guides=None):
    """Read the guides under references; return (checkable, skipped, unreadable guides).

    With guides, a set of file names, only those guides are read.

    Each checkable entry is a dict with guide, component, name, basis, repo, prefix and
    numbers. In one guide, entries with the same repository and tool prefix are reduced to the
    highest basis, because a lower one kept beside it (a recorded demonstration, for example)
    is covered by the higher one. Equal entries are kept once. The lower ones are listed as
    skipped, with the basis they are covered by.
    """
    checkable, skipped, unparsed = [], [], []
    for path in sorted(Path(references).glob('*.md')):
        if guides is not None and path.name not in guides:
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            unparsed.append(path.name)
            continue
        data = guide_metadata(text)
        if data is None:
            if START in text or text.startswith('---\nversion_basis: '):
                unparsed.append(path.name)
            continue
        best = {}
        for cid, component in data['components'].items():
            if not isinstance(component, dict):
                skipped.append(_row(path.name, cid, '', None, None, 'component is not an object'))
                continue
            basis = component.get('basis')
            name = component.get('name') if isinstance(component.get('name'), str) else cid
            repo, why = repo_from_sources(component.get('sources'))
            if repo is None:
                skipped.append(_row(path.name, cid, name, basis, None, why))
                continue
            version, why = parse_version(basis)
            if version is None:
                skipped.append(_row(path.name, cid, name, basis, repo, why))
                continue
            entry = _row(path.name, cid, name, basis, repo, None)
            entry['prefix'], entry['numbers'] = version
            key = (repo.lower(), entry['prefix'])
            held = best.get(key)
            if held is None:
                best[key] = entry
                continue
            order = compare(held['numbers'], entry['numbers'])
            if order == 'current' and compare(entry['numbers'], held['numbers']) == 'current':
                continue  # the same release again: keep it once
            lower, higher = (held, entry) if order != 'current' else (entry, held)
            best[key] = higher
            lower['reason'] = ('covered by basis ' + str(higher['basis']) + ' for the same '
                               'repository in this guide')
            skipped.append(lower)
        checkable.extend(best.values())
    return checkable, skipped, unparsed


def _row(guide, component, name, basis, repo, reason):
    return {'guide': guide, 'component': component, 'name': name,
            'basis': basis if isinstance(basis, str) else '-', 'repo': repo,
            'latest': None, 'reason': reason}


# ---------------------------------------------------------------- the network, opt-in only

class _ApiOnlyRedirect(urllib.request.HTTPRedirectHandler):
    """Follow a redirect only to https://api.github.com, so a token never leaves that host."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parts = urllib.parse.urlsplit(newurl)
        if parts.scheme != 'https' or parts.hostname != API_HOST or parts.port not in (None, 443):
            raise urllib.error.HTTPError(newurl, code, 'redirect away from ' + API_HOST
                                         + ' refused', headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def build_opener():
    return urllib.request.build_opener(_ApiOnlyRedirect())


def token_from_env(environ=None):
    """GITHUB_TOKEN, else GH_TOKEN, when it is printable ASCII with no space; else None."""
    environ = os.environ if environ is None else environ
    for name in ('GITHUB_TOKEN', 'GH_TOKEN'):
        value = environ.get(name, '')
        if value and all(33 <= ord(char) <= 126 for char in value):
            return value
    return None


def api_headers(token):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': USER_AGENT,
               'X-GitHub-Api-Version': '2022-11-28'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    return headers


def fetch_latest(repo, opener, token):
    """(tag, None, False) for the latest release, else (None, reason, rate_limited).

    Every failure is returned as a reason, never raised, so one bad answer cannot stop the run
    or be read as drift.
    """
    owner, name = repo.split('/', 1)
    url = (API + '/repos/' + urllib.parse.quote(owner, safe='') + '/'
           + urllib.parse.quote(name, safe='') + '/releases/latest')
    request = urllib.request.Request(url, headers=api_headers(token))
    try:
        with opener.open(request, timeout=TIMEOUT) as response:
            raw = response.read(MAX_BYTES + 1)
    except urllib.error.HTTPError as exc:
        headers = exc.headers or {}
        if exc.code == 429 or (exc.code == 403 and (headers.get('X-RateLimit-Remaining') == '0'
                                                     or headers.get('Retry-After'))):
            return None, f'GitHub rate limit reached (HTTP {exc.code})', True
        if exc.code == 404:
            return None, 'no published release, or the repository is not visible (HTTP 404)', False
        return None, f'HTTP {exc.code}', False
    except Exception as exc:  # noqa: BLE001  every other failure is "could not check"
        return None, 'request failed (' + type(exc).__name__ + ')', False
    if len(raw) > MAX_BYTES:
        return None, 'response larger than ' + str(MAX_BYTES) + ' bytes', False
    try:
        data = json.loads(raw.decode('utf-8'))
    except (UnicodeDecodeError, ValueError):
        return None, 'response is not JSON', False
    if not isinstance(data, dict) or not isinstance(data.get('tag_name'), str):
        return None, 'response has no tag_name', False
    if data.get('draft') is True or data.get('prerelease') is True:
        return None, 'latest release is marked draft or pre-release', False
    return data['tag_name'], None, False


def classify(entry, tag):
    """Set entry['latest'] and return its group for a fetched tag; never drift on doubt."""
    entry['latest'] = tag
    version, _ = parse_version(tag)
    if version is None:
        entry['reason'] = 'latest release tag is not a clean dotted numeric release'
        return COULD_NOT
    if version[0] != entry['prefix']:
        entry['reason'] = 'latest release tag names another package than the basis'
        return COULD_NOT
    order = compare(entry['numbers'], version[1])
    if order == 'drift':
        return DRIFT
    if order == 'major':
        return MAJOR
    return None


def check_online(checkable, opener, token):
    """Group the checkable entries by their upstream's latest release; one request per repo."""
    groups = {group: [] for group in GROUPS}
    current = []
    answers = {}
    limited = False
    for entry in checkable:
        key = entry['repo'].lower()
        if key not in answers:
            if limited:
                answers[key] = (None, 'not requested: GitHub rate limit reached earlier in this run')
            else:
                tag, reason, rate_limited = fetch_latest(entry['repo'], opener, token)
                answers[key] = (tag, reason)
                limited = limited or rate_limited
        tag, reason = answers[key]
        if tag is None:
            entry['reason'] = reason
            groups[COULD_NOT].append(entry)
            continue
        group = classify(entry, tag)
        (groups[group] if group else current).append(entry)
    return groups, current


# ---------------------------------------------------------------- the report

def bundle_version(path=PLUGIN_JSON):
    try:
        version = json.loads(Path(path).read_text(encoding='utf-8')).get('version')
    except (OSError, ValueError, AttributeError):
        return 'unknown'
    return version if isinstance(version, str) and version else 'unknown'


def issue_title(entry):
    return (f"Version currency: {entry['repo']} {entry['basis']} -> {entry['latest']} "
            f"({entry['guide']})")


def issue_body(entry, group, version='unknown'):
    kind = ('a newer release in the same major version' if group == DRIFT
            else 'a newer major version')
    return '\n'.join([
        f"Guide: {entry['guide']}",
        f"Component: {entry['component']} ({entry['name']})",
        f"Recorded basis: {entry['basis']}",
        f"Latest upstream release: {entry['latest']}",
        f"Upstream repository: https://github.com/{entry['repo']}",
        f'Kind: {kind}',
        f'Bundled skill version: {version}',
        '',
        'Found by the secureconfig skill\'s scripts/check-updates.py --check-online, from '
        'GitHub\'s latest-release API. It shows only that upstream published a newer release '
        'than the guide\'s recorded basis; nobody has yet checked whether that release changes '
        'the guide\'s guidance.',
    ])


def issue_url(entry, group, version='unknown'):
    query = urllib.parse.urlencode({'title': issue_title(entry),
                                    'body': issue_body(entry, group, version)},
                                   quote_via=urllib.parse.quote)
    return ISSUE_NEW + '?' + query


def line(entry):
    latest = entry['latest'] if entry['latest'] is not None else '-'
    text = (f"{entry['guide']}  {entry['component']}  basis {entry['basis']}  latest {latest}  "
            f"{entry['repo'] or '-'}")
    return text + (f"  ({entry['reason']})" if entry['reason'] else '')


def print_offline(checkable, skipped, unparsed, out):
    repos = {entry['repo'].lower() for entry in checkable}
    print('Egress is off: no network request was made.', file=out)
    print(f'With --check-online this would ask GitHub for the latest release of {len(repos)} '
          f'repositories, covering {len(checkable)} components; that needs network egress.',
          file=out)
    print('GitHub rate-limits unauthenticated requests, so a long run without GITHUB_TOKEN or '
          'GH_TOKEN can stop early; --guide NAME limits the run to the guides that matter.',
          file=out)
    print('', file=out)
    print(f'Would check ({len(checkable)})', file=out)
    for entry in checkable:
        print('  ' + line(entry), file=out)
    _print_group(NOT_CHECKABLE, skipped, out)
    _print_unparsed(unparsed, out)


def print_online(groups, current, unparsed, out, version):
    for group in GROUPS:
        _print_group(group, groups[group], out, version if group in (DRIFT, MAJOR) else None)
    _print_unparsed(unparsed, out)
    print('', file=out)
    print(f'No newer release found: {len(current)} components', file=out)


def _print_group(group, rows, out, version=None):
    print('', file=out)
    print(f'{group} ({len(rows)})', file=out)
    for entry in rows:
        print('  ' + line(entry), file=out)
        if version is not None:
            print('    report: ' + issue_url(entry, group, version), file=out)


def _print_unparsed(unparsed, out):
    if unparsed:
        print('', file=out)
        print(f'Guides with no parseable version-basis block ({len(unparsed)}): '
              + ', '.join(unparsed), file=out)


# ---------------------------------------------------------------- filing, with consent only

def gh_ready(which=shutil.which, run=subprocess.run):
    if not which('gh'):
        return False
    try:
        result = run(['gh', 'auth', 'status', '--hostname', 'github.com'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60, check=False)
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def file_with_gh(title, body, run=subprocess.run):
    try:
        result = run(['gh', 'issue', 'create', '--repo', ISSUES_REPO, '--title', title,
                      '--body', body], capture_output=True, text=True, timeout=120, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, 'gh could not run (' + type(exc).__name__ + ')'
    if result.returncode != 0:
        return None, 'gh exited ' + str(result.returncode) + ': ' + ' '.join(result.stderr.split())
    return result.stdout.strip() or 'filed', None


def file_with_token(title, body, token, opener):
    request = urllib.request.Request(
        API + '/repos/' + ISSUES_REPO + '/issues', method='POST',
        data=json.dumps({'title': title, 'body': body}).encode('utf-8'),
        headers=dict(api_headers(token), **{'Content-Type': 'application/json'}))
    try:
        with opener.open(request, timeout=TIMEOUT) as response:
            data = json.loads(response.read(MAX_BYTES).decode('utf-8'))
    except urllib.error.HTTPError as exc:
        return None, f'HTTP {exc.code}'
    except Exception as exc:  # noqa: BLE001  reported, never raised
        return None, 'request failed (' + type(exc).__name__ + ')'
    url = data.get('html_url') if isinstance(data, dict) else None
    return (url if isinstance(url, str) else 'filed'), None


def stdin_is_terminal():
    """True only when standard input is an open interactive terminal."""
    try:
        return sys.stdin is not None and sys.stdin.isatty()
    except (AttributeError, ValueError, OSError):
        return False


def file_issues(rows, out, ask, token, opener, gh_check=gh_ready, gh_file=file_with_gh,
                token_file=file_with_token, version='unknown', interactive=stdin_is_terminal):
    """Offer each (entry, group) row as an issue; file it only on an answer of yes.

    The answer must come from a person at an interactive terminal, so when standard input is not
    one, nothing is asked and nothing is filed.
    """
    if not rows:
        print('', file=out)
        print('Nothing to file: no drift or major row.', file=out)
        return 0
    if not interactive():
        print('', file=out)
        print('Not filing: issues are filed only from an interactive terminal, and standard input '
              'is not one. Share the report links above instead.', file=out)
        return 0
    use_gh = gh_check()
    if not use_gh and not token:
        print('', file=out)
        print('Not filing: no authenticated gh and no GITHUB_TOKEN or GH_TOKEN. Share the report '
              'links above instead.', file=out)
        return 0
    filed = 0
    for entry, group in rows:
        title, body = issue_title(entry), issue_body(entry, group, version)
        print('', file=out)
        print('Issue: ' + title, file=out)
        try:
            answer = ask(f'File this issue on {ISSUES_REPO} with your GitHub account? '
                         'Type yes to file it: ')
        except EOFError:
            answer = ''
        if answer.strip().lower() != 'yes':
            print('  not filed', file=out)
            continue
        where, error = (gh_file(title, body) if use_gh
                        else token_file(title, body, token, opener))
        if error:
            print('  not filed: ' + error, file=out)
        else:
            filed += 1
            print('  filed: ' + where, file=out)
    return filed


# ---------------------------------------------------------------- entry point

def parse_args(argv):
    parser = argparse.ArgumentParser(
        prog='check-updates.py',
        description='Report bundled guides whose upstream GitHub release has moved past the '
                    "guide's recorded version basis. Makes no network request unless "
                    '--check-online is given.')
    parser.add_argument('--check-online', action='store_true',
                        help='ask the GitHub API for each upstream repository\'s latest release '
                             '(network egress)')
    parser.add_argument('--file', action='store_true',
                        help='after the report, offer to open each drift or major row as an '
                             'issue, filing only after you type yes (needs --check-online, an '
                             'interactive terminal and an authenticated gh or '
                             'GITHUB_TOKEN/GH_TOKEN)')
    parser.add_argument('--guide', metavar='NAME', action='append',
                        help='check only this guide, such as nginx.md; repeat for more')
    parser.add_argument('--references', metavar='DIR', default=str(DEFAULT_REFERENCES),
                        help='folder of guides to read (default: the bundled references)')
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 0:
            raise  # --help
        raise UsageError(None) from exc
    if args.file and not args.check_online:
        raise UsageError('--file needs --check-online: there is nothing to file without the '
                         'online check')
    if not Path(args.references).is_dir():
        raise UsageError('no references folder at ' + args.references)
    for name in args.guide or ():
        if '/' in name or not name.endswith('.md') or not (Path(args.references) / name).is_file():
            raise UsageError('no guide named ' + name + ' in ' + args.references)
    return args


def run(argv, out=sys.stdout, opener=None, environ=None, ask=input, **filing):
    try:
        args = parse_args(argv)
    except UsageError as exc:
        if exc.args and exc.args[0]:
            print('check-updates.py: ' + exc.args[0], file=sys.stderr)
        return 2
    checkable, skipped, unparsed = collect(args.references,
                                           set(args.guide) if args.guide else None)
    if not args.check_online:
        print_offline(checkable, skipped, unparsed, out)
        return 0
    token = token_from_env(environ)
    opener = build_opener() if opener is None else opener
    version = bundle_version()
    groups, current = check_online(checkable, opener, token)
    groups[NOT_CHECKABLE] = skipped + groups[NOT_CHECKABLE]
    print_online(groups, current, unparsed, out, version)
    if args.file:
        rows = [(entry, group) for group in (DRIFT, MAJOR) for entry in groups[group]]
        file_issues(rows, out, ask, token, opener, version=version, **filing)
    return 0


if __name__ == '__main__':
    sys.exit(run(sys.argv[1:]))
