#!/usr/bin/env python3
"""Offline cases for plugin/skills/secureconfig/scripts/check-updates.py.

No case reaches the network. Before any case runs, socket.create_connection, socket.getaddrinfo
and the connect and connect_ex methods of socket.socket are replaced with a function that raises,
so a request that slipped past a stub would fail, never be sent. Every online path runs on a stub opener with canned answers.

  - METADATA: the two-section layout (four-backtick and three-backtick json fence before the end
    marker), the legacy front matter, and guides that must give None: no block, invalid JSON,
    a duplicate key, a NaN, no components object, a fence that does not close at the end marker,
    and two start markers;
  - REPO: github.com blob, tree and releases URLs give OWNER/REPO, and other URLs (raw, gist,
    issues, a bare repository, gitlab, http, any explicit port, 443 included, userinfo, a .git
    name) give None; a sources map gives its first such repository, the same repository in
    another case once, and none or two different repositories a skip reason;
  - BASIS: clean releases (4.4.0, v4.4.0, 26.8.0, 2026.09.0, 2.4.20.3, n8n@2.47.2 and
    @sveltejs/kit@2.70.3, keeping the prefix apart) and every skip (a commit hash, a commit
    prefixed "commit", unknown, empty, a date, ranges, series such as 2.4, 15, v262 and 4.x,
    pre-release, build and packaging suffixes, go1.27.0, curl-8_23_0 and a word);
  - COMPARE: same-major newer is drift, a newer major is major, equal and older are current,
    calver and four-part releases compare by number with zero padding;
  - CLASSIFY: tags against a basis, including a tag with another package's prefix, a tag
    without the basis's prefix, a pre-release tag and a non-numeric tag, each "could not check";
  - COLLECT: a fixture folder where a guide holds two releases for one repository (the lower is
    skipped as covered), a duplicate, a docs-only and a commit component, an unparseable block
    and a guide with no block; --guide limits the guides read;
  - NETWORK: fetch_latest() on a stub opener for a 200, 404, 403 rate limit, 429, 500, a
    connection error, a timeout, invalid JSON, a list, no tag_name, a draft flag, a pre-release
    flag and an oversized body, and check_online() asking once per repository, after a rate
    limit sending no further request, and putting a newer draft or pre-release under "could not
    check", never drift; the redirect handler refuses a redirect off api.github.com;
  - ISSUE: the exact title and prefilled URL for a fixture row, decoded back to its title and body;
  - RUN: run() offline prints what it would check and opens nothing, online prints all four
    groups and an issue link per drift or major row, and exits 0 either way; usage errors exit 2;
    --file without authentication files nothing, and with a stub gh files only on yes; with
    standard input not a terminal (a stub isatty, or no standard input), --file asks nothing,
    files nothing, even with a piped yes waiting, and says why.

Exit 0 ok, 1 on a finding.
"""
import importlib.util
import io
import json
import socket
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / 'plugin' / 'skills' / 'secureconfig' / 'scripts' / 'check-updates.py'


def _no_network(*args, **kwargs):
    raise AssertionError('a test tried to open a network connection')


spec = importlib.util.spec_from_file_location('check_updates', SCRIPT)
cu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cu)

# After the import, since ssl subclasses socket.socket while it loads.
socket.create_connection = _no_network
socket.getaddrinfo = _no_network
socket.socket.connect = _no_network
socket.socket.connect_ex = _no_network

failures = []
cases = 0


def check(condition, message):
    global cases
    cases += 1
    if not condition:
        failures.append(message)


# ---------------------------------------------------------------- fixtures

def eof_guide(payload, fence='````'):
    return ('# Title\n\nBody.\n\n' + cu.START + '\n## About the AI assistant section below\n\n'
            'Note.\n\n' + fence + 'json\n' + payload + '\n' + fence + '\n' + cu.END + '\n')


def components(**items):
    return json.dumps({'schema': 1, 'components': items}, indent=2)


def comp(basis, *urls):
    return {'name': 'Name', 'basis': basis,
            'sources': {f's{index:012d}': url for index, url in enumerate(urls)}}


class Response:
    def __init__(self, body):
        self.body = body

    def read(self, limit=-1):
        return self.body if limit < 0 else self.body[:limit]

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class StubOpener:
    """Answers per repository path; records every URL it was asked for."""

    def __init__(self, answers):
        self.answers, self.asked, self.requests = answers, [], []

    def open(self, request, timeout=None):
        url = request.full_url
        self.asked.append(url)
        self.requests.append(request)
        check(url.startswith('https://api.github.com/repos/'), 'request to an unexpected URL: ' + url)
        check(request.get_header('User-agent') == cu.USER_AGENT, 'request without User-Agent')
        answer = self.answers.get(url.split('/repos/', 1)[1].rsplit('/releases/', 1)[0])
        if isinstance(answer, BaseException):
            raise answer
        if answer is None:
            raise urllib.error.HTTPError(url, 404, 'Not Found', {}, None)
        return Response(answer)


def http_error(code, headers=None):
    return urllib.error.HTTPError('https://api.github.com/x', code, 'error', headers or {}, None)


def release(tag, **extra):
    return json.dumps(dict({'tag_name': tag, 'draft': False, 'prerelease': False}, **extra)).encode()


# ---------------------------------------------------------------- METADATA

data = cu.guide_metadata(eof_guide(components(a=comp('1.2.3'))))
check(data is not None and data['components']['a']['basis'] == '1.2.3',
      'METADATA: four-backtick EOF block should parse')
data = cu.guide_metadata(eof_guide(components(a=comp('1.2.3')), fence='```'))
check(data is not None, 'METADATA: three-backtick EOF block should parse')
legacy = '---\nversion_basis: {"schema": 1, "components": {"a": {"basis": "2.0.0"}}}\n---\n# T\n'
data = cu.guide_metadata(legacy)
check(data is not None and data['components']['a']['basis'] == '2.0.0',
      'METADATA: legacy front matter should parse')
for desc, text in {
        'no block': '# Title\n\nNo metadata.\n',
        'invalid JSON': eof_guide('{"schema": 1, "components": {'),
        'duplicate key': eof_guide('{"components": {}, "components": {}}'),
        'NaN': eof_guide('{"components": {}, "x": NaN}'),
        'no components object': eof_guide('{"schema": 1, "components": []}'),
        'fence not closing at END': eof_guide(components(a=comp('1.2.3'))).replace(
            '\n````\n' + cu.END, '\n````\nmore\n' + cu.END),
        'two start markers': cu.START + '\n' + eof_guide(components(a=comp('1.2.3'))),
        'unsupported front matter': '---\ntitle: x\n---\n# T\n',
}.items():
    check(cu.guide_metadata(text) is None, f'METADATA: {desc} should give None')

# ---------------------------------------------------------------- REPO

for url, want in {
        'https://github.com/rabbitmq/rabbitmq-server/blob/v4.4.0/deps/rabbit/x.erl#L1': 'rabbitmq/rabbitmq-server',
        'https://github.com/caddyserver/caddy/tree/v2.11.4/modules': 'caddyserver/caddy',
        'https://github.com/n8n-io/n8n/releases/tag/n8n%402.47.2': 'n8n-io/n8n',
        'https://www.github.com/go-gitea/gitea/blob/v1/x.go': 'go-gitea/gitea',
        'https://github.com/a/b.c_d-e/releases': 'a/b.c_d-e',
        'https://raw.githubusercontent.com/a/b/v1.0.0/x': None,
        'https://gist.github.com/a/0123456789': None,
        'https://github.com/a/b/issues/1': None,
        'https://github.com/a/b': None,
        'https://github.com/a/b/wiki/Page': None,
        'https://gitlab.com/a/b/-/blob/v1.0.0/x': None,
        'http://github.com/a/b/blob/v1/x': None,
        'https://github.com:8443/a/b/blob/v1/x': None,
        'https://github.com:443/owner/repo/blob/v1/x': None,
        'https://user@github.com/a/b/blob/v1/x': None,
        'https://github.com/a/b.git/blob/v1/x': None,
        'https://github.com/-a/b/blob/v1/x': None,
        'https://docs.example.com/a/b/blob/v1': None,
        'not a url': None,
}.items():
    check(cu.github_repo(url) == want, f'REPO: {url} should give {want!r}: {cu.github_repo(url)!r}')
repo, why = cu.repo_from_sources({'s1': 'https://docs.example.com/x',
                                  's2': 'https://github.com/Owner/Repo/blob/v1.0.0/a',
                                  's3': 'https://github.com/owner/repo/tree/v1.0.0/b'})
check((repo, why) == ('Owner/Repo', None),
      f'REPO: the first GitHub source, the same repository in another case once: {repo!r} {why!r}')
repo, why = cu.repo_from_sources({'s1': 'https://docs.example.com/x',
                                  's2': 'https://gitlab.com/a/b/-/tree/v1.0.0'})
check(repo is None and 'no source' in why, f'REPO: docs and GitLab only should skip: {why!r}')
repo, why = cu.repo_from_sources({'s1': 'https://github.com/a/one/blob/v1.0.0/x',
                                  's2': 'https://github.com/a/two/blob/v1.0.0/y'})
check(repo is None and 'more than one' in why, f'REPO: two repositories should skip: {why!r}')
repo, why = cu.repo_from_sources(['https://github.com/a/b/blob/v1/x'])
check(repo is None and why, 'REPO: a sources list that is not a mapping should skip')

# ---------------------------------------------------------------- BASIS

for basis, want in {
        '4.4.0': ('', (4, 4, 0)), 'v4.4.0': ('', (4, 4, 0)), '26.8.0': ('', (26, 8, 0)),
        '2026.09.0': ('', (2026, 9, 0)), 'v2.4.20.3': ('', (2, 4, 20, 3)),
        'n8n@2.47.2': ('n8n', (2, 47, 2)), '@sveltejs/kit@2.70.3': ('@sveltejs/kit', (2, 70, 3)),
}.items():
    version, why = cu.parse_version(basis)
    check(version == want and why is None, f'BASIS: {basis} should parse as {want!r}: {version!r} {why!r}')
for basis, reason in {
        'c896795b8e8bab68d05ae78d64c9cbcda1fdb104': 'commit', '914ec15d1fa4': 'commit',
        'commit 72865b1e': 'commit', 'unknown': 'unknown', '': 'no recorded', '2026-07-28': 'date',
        '2026-07': 'date', '8.19.1 to 8.30.1': 'range', 'v0.71.0...v0.72.0': 'range',
        '4.2 through 5.2': 'range', '2.4.36+': 'range', 'v4-v5': 'range', '2.4': 'series',
        '15': 'series', 'v262': 'series', '4.x': 'series', '2.x': 'series',
        'v2.0.0-rc.2': 'suffix', '2.4.69-1': 'suffix', 'v1.152.0-cluster': 'suffix',
        'go1.27.0': 'not a dotted', 'curl-8_23_0': 'not a dotted', 'September 2025': 'not a dotted',
        'release-1.26.3': 'not a dotted', '@2.0.0': 'not a dotted', 'RFC 9700': 'not a dotted',
}.items():
    version, why = cu.parse_version(basis)
    check(version is None and why and reason in why, f'BASIS: {basis!r} should skip ({reason}): {why!r}')
check(cu.parse_version(None)[0] is None, 'BASIS: a non-string basis should skip')

# ---------------------------------------------------------------- COMPARE

for basis, latest, want in (
        ((4, 4, 0), (4, 5, 1), 'drift'), ((4, 4, 0), (5, 0, 0), 'major'),
        ((4, 4, 0), (4, 4, 0), 'current'), ((4, 4, 0), (4, 3, 9), 'current'),
        ((2026, 9, 0), (2026, 10, 1), 'drift'), ((26, 8, 0), (27, 0, 0), 'major'),
        ((2, 4, 20, 3), (2, 4, 21), 'drift'), ((2, 4, 20, 3), (2, 4, 20), 'current'),
        ((4, 4, 0), (4, 4, 0, 0), 'current'), ((0, 160, 0), (0, 161, 0), 'drift')):
    check(cu.compare(basis, latest) == want, f'COMPARE: {basis} -> {latest} should be {want}')

# ---------------------------------------------------------------- CLASSIFY


def entry(basis, repo='a/b', guide='g.md', component='c'):
    row = cu._row(guide, component, 'Name', basis, repo, None)
    row['prefix'], row['numbers'] = cu.parse_version(basis)[0]
    return row


for basis, tag, want in (
        ('v4.4.0', 'v4.5.0', cu.DRIFT), ('v4.4.0', 'v5.0.0', cu.MAJOR), ('v4.4.0', 'v4.4.0', None),
        ('4.4.0', 'v4.4.1', cu.DRIFT), ('n8n@2.47.2', 'n8n@2.48.0', cu.DRIFT),
        ('@sveltejs/kit@2.70.3', '@sveltejs/adapter-node@5.0.0', cu.COULD_NOT),
        ('2.47.2', 'n8n@2.48.0', cu.COULD_NOT), ('n8n@2.47.2', '2.48.0', cu.COULD_NOT),
        ('v4.4.0', 'v4.5.0-rc.1', cu.COULD_NOT), ('v4.4.0', 'release-4.5.0', cu.COULD_NOT),
        ('v4.4.0', 'nightly', cu.COULD_NOT), ('v4.4.0', '4.5', cu.COULD_NOT)):
    row = entry(basis)
    got = cu.classify(row, tag)
    check(got == want and row['latest'] == tag, f'CLASSIFY: {basis} with tag {tag} should be {want}: {got}')

# ---------------------------------------------------------------- COLLECT

with tempfile.TemporaryDirectory() as tmp:
    refs = Path(tmp)
    (refs / 'one.md').write_text(eof_guide(components(
        new=comp('26.8.2', 'https://github.com/keycloak/keycloak/blob/26.8.2/x'),
        old=comp('26.7.4', 'https://github.com/keycloak/keycloak/blob/26.7.4/x'),
        same=comp('26.8.2', 'https://github.com/keycloak/keycloak/tree/26.8.2/docs'),
        docs=comp('1.2.3', 'https://docs.example.com/x'),
        pinned=comp('4e9a5751518ed8223a8dcde53693badddd72604f', 'https://github.com/a/b/blob/4e9a575/x'),
    )), encoding='utf-8')
    (refs / 'two.md').write_text(eof_guide('{not json'), encoding='utf-8')
    (refs / 'three.md').write_text('# No metadata\n', encoding='utf-8')
    (refs / 'four.md').write_text(eof_guide(components(
        x=comp('v1.0.0', 'https://github.com/x/y/releases/tag/v1.0.0'))), encoding='utf-8')
    checkable, skipped, unparsed = cu.collect(refs)
    got = sorted((row['guide'], row['component'], row['basis']) for row in checkable)
    check(got == [('four.md', 'x', 'v1.0.0'), ('one.md', 'new', '26.8.2')],
          f'COLLECT: checkable rows should be the highest basis per repository, once: {got!r}')
    reasons = {row['component']: row['reason'] for row in skipped}
    check(set(reasons) == {'old', 'docs', 'pinned'}, f'COLLECT: skipped components: {reasons!r}')
    check('covered by basis 26.8.2' in reasons.get('old', ''), 'COLLECT: the lower basis should be covered')
    check('no source' in reasons.get('docs', ''), 'COLLECT: docs-only should be not checkable')
    check('commit' in reasons.get('pinned', ''), 'COLLECT: a commit basis should be not checkable')
    check(unparsed == ['two.md'], f'COLLECT: only two.md has an unparseable block: {unparsed!r}')
    checkable, skipped, unparsed = cu.collect(refs, {'four.md'})
    check([row['guide'] for row in checkable] == ['four.md'] and not skipped and not unparsed,
          'COLLECT: a guide filter should read only that guide')

    # ------------------------------------------------------------ RUN (offline and online)
    out = io.StringIO()
    opener = StubOpener({})
    rc = cu.run(['--references', str(refs)], out=out, opener=opener)
    text = out.getvalue()
    check(rc == 0 and not opener.asked, f'RUN: offline should exit 0 and ask nothing: {rc} {opener.asked!r}')
    check('Egress is off: no network request was made.' in text and 'Would check (2)' in text
          and 'four.md  x  basis v1.0.0  latest -  x/y' in text
          and 'Not automatically checkable (3)' in text, 'RUN: offline report text: ' + text)

    opener = StubOpener({'keycloak/keycloak': release('26.9.0'), 'x/y': release('v2.0.0')})
    out = io.StringIO()
    rc = cu.run(['--references', str(refs), '--check-online'], out=out, opener=opener, environ={})
    text = out.getvalue()
    check(rc == 0, f'RUN: online with drift should exit 0: {rc}')
    check(len(opener.asked) == 2, f'RUN: one request per repository: {opener.asked!r}')
    for heading in ('Currency drift (1)', 'Major available (1)', 'Could not check (0)',
                    'Not automatically checkable (3)', 'No newer release found: 0 components'):
        check(heading in text, f'RUN: online report should have {heading!r}: {text}')
    check('one.md  new  basis 26.8.2  latest 26.9.0  keycloak/keycloak' in text,
          'RUN: the drift row line format: ' + text)
    check(text.count('    report: ' + cu.ISSUE_NEW + '?title=') == 2,
          'RUN: one issue link per drift or major row: ' + text)

    opener = StubOpener({'keycloak/keycloak': release('26.8.2'), 'x/y': http_error(500)})
    out = io.StringIO()
    rc = cu.run(['--references', str(refs), '--check-online'], out=out, opener=opener, environ={})
    text = out.getvalue()
    check(rc == 0 and 'Currency drift (0)' in text and 'Could not check (1)' in text
          and 'No newer release found: 1 components' in text and 'report:' not in text,
          'RUN: a current release and an HTTP 500 give no drift and no link: ' + text)

    for argv, desc in ((['--file'], '--file without --check-online'),
                       (['--bogus'], 'an unknown option'),
                       (['--references', str(refs / 'missing')], 'a missing references folder'),
                       (['--references', str(refs), '--guide', 'nope.md'], 'an unknown guide'),
                       (['--references', str(refs), '--guide', '../one.md'], 'a guide path')):
        err, saved = io.StringIO(), sys.stderr
        sys.stderr = err
        try:
            rc = cu.run(argv, out=io.StringIO(), opener=StubOpener({}))
        finally:
            sys.stderr = saved
        check(rc == 2, f'RUN: {desc} should exit 2: {rc}')

    # ------------------------------------------------------------ --file
    class StubStdin(io.StringIO):
        """Standard input holding a piped yes, with a stubbed isatty answer."""

        def __init__(self, tty):
            super().__init__('yes\n')
            self.tty = tty

        def isatty(self):
            return self.tty

    saved_stdin = sys.stdin
    sys.stdin = StubStdin(True)  # the consent cases below run as if at a terminal
    calls = []
    out = io.StringIO()
    rc = cu.run(['--references', str(refs), '--check-online', '--file'], out=out,
                opener=StubOpener({'keycloak/keycloak': release('26.9.0'), 'x/y': release('v1.0.0')}),
                environ={}, ask=lambda prompt: 'yes', gh_check=lambda: False,
                gh_file=lambda *a: calls.append(a) or ('url', None))
    check(rc == 0 and not calls and 'Not filing: no authenticated gh' in out.getvalue(),
          'RUN: --file with no gh and no token should file nothing: ' + out.getvalue())
    for answer, filed in (('no', 0), ('', 0), ('yes', 1), ('YES ', 1)):
        calls = []
        out = io.StringIO()
        rc = cu.run(['--references', str(refs), '--check-online', '--file'], out=out,
                    opener=StubOpener({'keycloak/keycloak': release('26.9.0'), 'x/y': release('v1.0.0')}),
                    environ={}, ask=lambda prompt, answer=answer: answer, gh_check=lambda: True,
                    gh_file=lambda title, body: calls.append((title, body)) or ('https://example.com/1', None))
        check(rc == 0 and len(calls) == filed, f'RUN: --file answered {answer!r} should file {filed}: {calls!r}')
    if calls:
        check(calls[0][0] == 'Version currency: keycloak/keycloak 26.8.2 -> 26.9.0 (one.md)',
              f'RUN: the filed title: {calls[0][0]!r}')

    def eof(prompt):
        raise EOFError

    calls = []
    rc = cu.run(['--references', str(refs), '--check-online', '--file'], out=io.StringIO(),
                opener=StubOpener({'keycloak/keycloak': release('26.9.0'), 'x/y': release('v1.0.0')}),
                environ={}, ask=eof, gh_check=lambda: True,
                gh_file=lambda *a: calls.append(a) or ('url', None))
    check(rc == 0 and not calls, 'RUN: --file at end of input should file nothing')

    calls = []
    rc = cu.run(['--references', str(refs), '--check-online', '--file'], out=io.StringIO(),
                opener=StubOpener({'keycloak/keycloak': release('26.9.0'), 'x/y': release('v1.0.0')}),
                environ={'GITHUB_TOKEN': 'test-token'}, ask=lambda prompt: 'yes',
                gh_check=lambda: False,
                token_file=lambda title, body, token, opener: calls.append(token) or ('u', None))
    check(calls == ['test-token'], f'RUN: --file with a token and no gh should use the token: {calls!r}')

    # Standard input that is not a terminal: a piped yes waits on it, and the real input() is the
    # prompt, so a missing check would read that yes and file.
    sys.stdin = StubStdin(False)
    calls, gh_checks = [], []
    out = io.StringIO()
    rc = cu.run(['--references', str(refs), '--check-online', '--file'], out=out,
                opener=StubOpener({'keycloak/keycloak': release('26.9.0'), 'x/y': release('v1.0.0')}),
                environ={}, ask=input, gh_check=lambda: gh_checks.append(1) or True,
                gh_file=lambda *a: calls.append(a) or ('url', None))
    check(rc == 0 and not calls and not gh_checks
          and 'Not filing: issues are filed only from an interactive terminal' in out.getvalue()
          and 'Share the report links above instead.' in out.getvalue(),
          'RUN: --file with standard input not a terminal should file nothing and say so: '
          + out.getvalue())
    check(sys.stdin.read() == 'yes\n' and 'Type yes' not in out.getvalue(),
          'RUN: --file with standard input not a terminal should not prompt or read the piped yes')
    calls = []
    sys.stdin = StubStdin(False)
    rc = cu.run(['--references', str(refs), '--check-online', '--file'], out=io.StringIO(),
                opener=StubOpener({'keycloak/keycloak': release('26.9.0'), 'x/y': release('v1.0.0')}),
                environ={'GITHUB_TOKEN': 'test-token'}, ask=lambda prompt: 'yes',
                gh_check=lambda: False,
                token_file=lambda title, body, token, opener: calls.append(token) or ('u', None))
    check(rc == 0 and not calls, f'RUN: --file with a token and no terminal should file nothing: {calls!r}')
    calls = []
    sys.stdin = None
    out = io.StringIO()
    rc = cu.run(['--references', str(refs), '--check-online', '--file'], out=out,
                opener=StubOpener({'keycloak/keycloak': release('26.9.0'), 'x/y': release('v1.0.0')}),
                environ={}, ask=lambda prompt: 'yes', gh_check=lambda: True,
                gh_file=lambda *a: calls.append(a) or ('url', None))
    check(rc == 0 and not calls and 'only from an interactive terminal' in out.getvalue(),
          'RUN: --file with no standard input should file nothing: ' + out.getvalue())
    sys.stdin = saved_stdin

# ---------------------------------------------------------------- NETWORK

for desc, answer, want in (
        ('a 200', release('v2.0.0'), ('v2.0.0', None, False)),
        ('a 404', None, (None, 'HTTP 404', False)),
        ('a 403 rate limit', http_error(403, {'X-RateLimit-Remaining': '0'}), (None, 'rate limit', True)),
        ('a 429', http_error(429), (None, 'rate limit', True)),
        ('a 403 without rate-limit headers', http_error(403), (None, 'HTTP 403', False)),
        ('a 500', http_error(500), (None, 'HTTP 500', False)),
        ('a connection error', urllib.error.URLError('refused'), (None, 'URLError', False)),
        ('a timeout', TimeoutError('slow'), (None, 'TimeoutError', False)),
        ('invalid JSON', b'{not json', (None, 'not JSON', False)),
        ('a JSON list', b'[]', (None, 'no tag_name', False)),
        ('no tag_name', b'{"name": "x"}', (None, 'no tag_name', False)),
        ('a draft flag', release('v2.0.0', draft=True), (None, 'draft', False)),
        ('a pre-release flag', release('v2.0.0', prerelease=True), (None, 'pre-release', False)),
        ('an oversized body', b' ' * (cu.MAX_BYTES + 1), (None, 'larger than', False))):
    tag, reason, limited = cu.fetch_latest('a/b', StubOpener({'a/b': answer}), None)
    ok = tag == want[0] and limited == want[2] and (want[1] is None if reason is None else want[1] in reason)
    check(ok, f'NETWORK: {desc} should give {want!r}: {(tag, reason, limited)!r}')

rows = [entry('v1.0.0', repo='a/one'), entry('v1.0.0', repo='a/one', guide='h.md'),
        entry('v1.0.0', repo='a/two'), entry('v1.0.0', repo='a/three')]
opener = StubOpener({'a/one': release('v1.1.0'),
                     'a/two': http_error(403, {'X-RateLimit-Remaining': '0'}),
                     'a/three': release('v9.0.0')})
groups, current = cu.check_online(rows, opener, None)
check(len(opener.asked) == 2, f'NETWORK: one request for a/one, none after the rate limit: {opener.asked!r}')
check(len(groups[cu.DRIFT]) == 2 and not groups[cu.MAJOR] and len(groups[cu.COULD_NOT]) == 2,
      f'NETWORK: groups after a rate limit: { {k: len(v) for k, v in groups.items()} }')
check('earlier in this run' in groups[cu.COULD_NOT][-1]['reason'],
      'NETWORK: a repository after the rate limit should say it was not requested')
for flag in ('draft', 'prerelease'):
    rows = [entry('v1.0.0', repo='a/flagged')]
    groups, current = cu.check_online(rows, StubOpener({'a/flagged': release('v1.1.0', **{flag: True})}),
                                      None)
    check(not groups[cu.DRIFT] and not groups[cu.MAJOR] and not current
          and len(groups[cu.COULD_NOT]) == 1
          and 'draft or pre-release' in groups[cu.COULD_NOT][0]['reason'],
          f'NETWORK: a newer release marked {flag} should be could not check, never drift: '
          f'{ {k: len(v) for k, v in groups.items()} }')
opener = StubOpener({'a/b': release('v1.0.0')})
cu.fetch_latest('a/b', opener, 'tok')
check(opener.requests[0].get_header('Authorization') == 'Bearer tok'
      and opener.asked == ['https://api.github.com/repos/a/b/releases/latest'],
      'NETWORK: a token is sent as a bearer header to the latest-release URL')
opener = StubOpener({'a/b': release('v1.0.0')})
cu.fetch_latest('a/b', opener, None)
check(opener.requests[0].get_header('Authorization') is None,
      'NETWORK: no Authorization header without a token')
handler = cu._ApiOnlyRedirect()
for target, allowed in (('https://api.github.com/repositories/1/releases/latest', True),
                        ('https://example.com/steal', False), ('http://api.github.com/x', False),
                        ('https://api.github.com:8443/x', False)):
    request = urllib.request.Request('https://api.github.com/repos/a/b/releases/latest',
                                     headers={'Authorization': 'Bearer tok'})
    try:
        handler.redirect_request(request, None, 301, 'Moved', {}, target)
        refused = False
    except urllib.error.HTTPError:
        refused = True
    check(refused != allowed, f'NETWORK: a redirect to {target} should be {"followed" if allowed else "refused"}')
check(cu.token_from_env({'GITHUB_TOKEN': 'a b', 'GH_TOKEN': 'good'}) == 'good'
      and cu.token_from_env({}) is None and cu.token_from_env({'GITHUB_TOKEN': 'x\n'}) is None,
      'NETWORK: a token with a space or control character is not used')
check('Authorization' not in cu.api_headers(None) and cu.api_headers('t')['Authorization'] == 'Bearer t',
      'NETWORK: the bearer header is set only with a token')

# ---------------------------------------------------------------- ISSUE

row = cu._row('rabbitmq.md', 'rabbitmq', 'RabbitMQ server', 'v4.4.0', 'rabbitmq/rabbitmq-server', None)
row['latest'] = 'v4.5.0'
title = cu.issue_title(row)
check(title == 'Version currency: rabbitmq/rabbitmq-server v4.4.0 -> v4.5.0 (rabbitmq.md)',
      f'ISSUE: title: {title!r}')
url = cu.issue_url(row, cu.DRIFT, '1.0.1')
want_prefix = ('https://github.com/jposluns/secureconfig/issues/new?title=Version%20currency%3A%20'
               'rabbitmq%2Frabbitmq-server%20v4.4.0%20-%3E%20v4.5.0%20%28rabbitmq.md%29&body=')
check(url.startswith(want_prefix), f'ISSUE: URL prefix: {url[:len(want_prefix) + 20]!r}')
query = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
check(query.get('title') == [title], 'ISSUE: title should decode back')
body = query.get('body', [''])[0]
check(body == cu.issue_body(row, cu.DRIFT, '1.0.1'), 'ISSUE: body should decode back')
for part in ('Guide: rabbitmq.md', 'Component: rabbitmq (RabbitMQ server)', 'Recorded basis: v4.4.0',
             'Latest upstream release: v4.5.0',
             'Upstream repository: https://github.com/rabbitmq/rabbitmq-server',
             'Kind: a newer release in the same major version', 'Bundled skill version: 1.0.1'):
    check(part in body, f'ISSUE: body should name {part!r}')
check('a newer major version' in cu.issue_body(row, cu.MAJOR), 'ISSUE: a major row says so')
check(not any(char in url for char in ' \n#') and url.count('&') == 1,
      'ISSUE: the URL carries no raw space, newline or # and exactly one &')

# ---------------------------------------------------------------- the bundled references

checkable, skipped, unparsed = cu.collect(cu.DEFAULT_REFERENCES)
check(checkable and not unparsed,
      f'BUNDLE: the bundled references should all parse and give checkable rows: {unparsed!r}')

if failures:
    for failure in failures:
        print(f'  FAIL  {failure}')
    sys.exit(1)
print(f'  ok    {cases} offline cases for scripts/check-updates.py: metadata, repositories, '
      'bases, comparison, tags, collection, the stubbed network, issue links and runs')
