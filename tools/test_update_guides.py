#!/usr/bin/env python3
"""Offline cases for plugin/skills/secureconfig/scripts/update-guides.sh.

No case reaches the network and nothing listens. Each case builds a temporary tree laid out like
the plugin (plugin.json, skills/secureconfig/scripts/update-guides.sh copied from this repository,
skills/secureconfig/references with two guides and a MANIFEST.sha256), because the script finds
plugin.json and the references relative to itself, and runs it as bash <script> with an explicit
minimal environment and a working directory the test controls. A bash shim named curl comes first
on PATH: it serves the GitHub API's releases/latest URL from a fixture JSON file, maps a URL under
https://raw.githubusercontent.com/jposluns/secureconfig/refs/tags/ to a file in the case's fixture
folder, honours -o FILE, ignores -fsS and --max-time N, exits 22 for any other URL (a URL under
main included, and the API when the case has no release), and appends every URL it is asked for
to a log. Each case checks that log, so a fetch the shim did not make fails the case. The script's
URL constants are unchanged; there is no override for them. This process also replaces the
socket connect functions with one that raises. Every case runs with LC_ALL=C except the LOCALE
cases.

  - SHIM: an unknown URL exits 22, -o writes the fixture, and both are logged;
  - GOOD: a release whose tag is vN.N.N, newer than the installed version, with a matching
    VERSION and manifest at that tag, replaces the references, re-pins plugin.json and says so,
    fetching the API answer, then VERSION, the manifest and each guide from refs/tags/<tag>
    through the shim, in that order; a VERSION with no trailing newline and one ending in CR LF
    update the same way;
  - SAME: a release equal to the installed version is "nothing to do", nothing changed, and only
    the API answer is fetched;
  - OLDER: a release older than the installed version is not installed: exit 0, "nothing to do",
    nothing changed, only the API is fetched; the comparison is numeric (1.0.10 is newer than
    1.0.9, not older);
  - NO RELEASE: no API answer (the shim's 22) is refused with exit 1, nothing changed;
  - BAD TAG: a tag_name that is not vN.N.N (no v, two or four parts, a suffix, a trailing line
    end, an escape, non-ASCII digits, a path, a number, null, empty), a draft or pre-release
    object, one missing those fields, and an answer that is not an object or not JSON, are each
    refused with exit 1 and a message that does not echo the value, nothing fetched but the API;
  - TAG MISMATCH: a VERSION at the tag that is not the tag's version is refused;
  - BAD PUBLISHED: 1.0, 1.0.5.6, v1.0.5, 1.0.5-rc1, a terminal escape, a word, a second line, a
    trailing dot, a sign, non-ASCII digits, a huge run of digits, a huge garbage line, a second
    line that stripping whitespace would join into 1.0.56, a trailing blank with and without a
    newline, a leading blank, a blank inside, two trailing newlines, a lone trailing CR, a CR
    inside, and an embedded and a trailing NUL byte are each refused with exit 1 and a message
    that does not echo the value, nothing written and nothing fetched after VERSION; an empty or
    blank VERSION keeps its own message, and a VERSION the shim does not have is refused too;
  - BAD LOCAL: a plugin.json version of "x", none, a number, null, a list, an escape, a second
    line or two parts, and a plugin.json that is not an object, are refused before any fetch,
    with exit 1 and a message that does not echo the value, nothing written;
  - LOCALE: up to two UTF-8 locales from a fixed list, each used only if a bash probe run under it
    shows [0-9] matching an Arabic-Indic digit (no usable locale is a PREREQ failure, and the
    probe under LC_ALL=C is its negative control); under each, Arabic-Indic, superscript and
    fullwidth digits in VERSION are refused as in BAD PUBLISHED, an Arabic-Indic plugin.json
    version is refused as in BAD LOCAL, and a GOOD update still succeeds;
  - ISOLATION: every python3 in the script text carries -I; with a json.py planted in the working
    directory the update succeeds and the plant never runs, and a plain python3 -c 'import json'
    in that same directory does run it (the negative control);
  - MANIFEST: a tampered digest, a line that is not a digest line (sha256sum --strict) and a
    "../x" entry are each refused, nothing changed;
  - BOUND and DEPTH: an answer of exactly 1 MiB is used and one of 1 MiB + 1 is refused, a draft or
    pre-release field of 0 is refused, JSON nested 200000 deep (a RecursionError) in the answer or
    in plugin.json is refused with no traceback, and the script keeps both isascii tests and no
    0-9 range.

Exit 0 ok, 1 on a finding.
"""
import hashlib
import json
import os
import re
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / 'plugin' / 'skills' / 'secureconfig' / 'scripts' / 'update-guides.sh'
API = 'https://api.github.com/repos/jposluns/secureconfig/releases/latest'
RAW_PREFIX = 'https://raw.githubusercontent.com/jposluns/secureconfig/refs/tags/'
INSTALLED = '1.0.4'
PUBLISHED = '1.0.5'
TAG = 'v' + PUBLISHED
RAW = RAW_PREFIX + TAG + '/'
MANIFEST_PATH = 'plugin/skills/secureconfig/references/MANIFEST.sha256'
BAD_TAG_MESSAGE = b'the latest release has no tag of the form vN.N.N'
NO_RELEASE_MESSAGE = b'could not read the latest published release'
MISMATCH_MESSAGE = b'the VERSION file at the release tag does not match the tag'
OLD_GUIDES = {'alpha.md': b'# Alpha\n\nInstalled text.\n',
              'gamma.md': b'# Gamma\n\nOnly in the installed bundle.\n'}
NEW_GUIDES = {'alpha.md': b'# Alpha\n\nPublished text.\n',
              'beta.md': b'# Beta\n\nA new guide.\n'}
PLUGIN_JSON = '{\n  "name": "secureconfig",\n  "version": "1.0.4"\n}\n'
BAD_PUBLISHED_MESSAGE = b'the published version is not of the form N.N.N'
EMPTY_PUBLISHED_MESSAGE = b'could not read the published version; nothing changed'
BAD_LOCAL_MESSAGE = b'plugin.json records no version of the form N.N.N'
MARKER = 'json-was-imported'
# The LOCALE cases run under at most two of these, one per language and territory.
LOCALE_CANDIDATES = ('en_US.UTF-8', 'en_US.utf8', 'de_DE.UTF-8', 'de_DE.utf8',
                     'fr_FR.UTF-8', 'fr_FR.utf8', 'en_IN.UTF-8', 'en_IN.utf8')
# True in a locale where a [0-9] range in bash's [[ =~ ]] matches U+0661 ARABIC-INDIC DIGIT ONE.
LOCALE_PROBE = "[[ $'\u0661' =~ ^[0-9]$ ]]".encode('utf-8')

# The shim is written per case with its log and fixture folder as literals, so it reads no
# environment variable and the script needs none.
SHIM = r'''#!/usr/bin/env bash
# Stand-in for curl, written by tools/test_update_guides.py: fixture files only, no network.
set -u
log=@LOG@
fixtures=@FIXTURES@
api=https://api.github.com/repos/jposluns/secureconfig/releases/latest
prefix=https://raw.githubusercontent.com/jposluns/secureconfig/refs/tags/
out='' url=''
while [ "$#" -gt 0 ]; do
  case "$1" in
    -fsS) shift ;;
    --max-time|-o)
      if [ "$#" -lt 2 ]; then
        echo "curl shim: $1 needs a value" >&2
        exit 2
      fi
      if [ "$1" = -o ]; then
        out=$2
      fi
      shift 2 ;;
    -*) echo "curl shim: unexpected option $1" >&2; exit 2 ;;
    *) url=$1; shift ;;
  esac
done
printf '%s\n' "$url" >> "$log"
case "$url" in
  "$api") path=_api/releases-latest.json ;;
  "$prefix"*) path=${url#"$prefix"} ;;
  *) exit 22 ;;
esac
case "$path" in
  '' | /* | *..*) exit 22 ;;
esac
file="$fixtures/$path"
if [ ! -f "$file" ]; then
  exit 22
fi
if [ -n "$out" ]; then
  cat -- "$file" > "$out"
else
  cat -- "$file"
fi
'''

PLANT = '''import os
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), %r), "w").close()
raise SystemExit(0)
''' % MARKER


def _no_network(*args, **kwargs):
    raise AssertionError('a test tried to open a network connection')


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


BASE_PATH = os.environ.get('PATH') or os.defpath
BASH = shutil.which('bash', path=BASE_PATH)
for tool in ('bash', 'python3', 'sha256sum', 'tr', 'wc', 'mktemp', 'cp', 'mv', 'rm', 'mkdir',
             'cat'):
    if not shutil.which(tool, path=BASE_PATH):
        print(f'  FAIL  PREREQ: {tool} is not on PATH, so update-guides.sh cannot be exercised')
        sys.exit(1)
if not SCRIPT.is_file():
    print(f'  FAIL  PREREQ: {SCRIPT} is missing')
    sys.exit(1)


def locale_is_usable(name):
    """True if bash, run under LC_ALL=name, matches [0-9] against an Arabic-Indic digit."""
    try:
        done = subprocess.run([BASH, '-c', LOCALE_PROBE], env={'PATH': BASE_PATH, 'LC_ALL': name},
                              stdin=subprocess.DEVNULL, capture_output=True, timeout=60)
    except subprocess.TimeoutExpired:
        return False
    return done.returncode == 0


# This follows the file's own prerequisite convention, as for a missing tool above: when no
# candidate locale makes [0-9] match a non-ASCII digit, the LOCALE cases would prove nothing, so
# the run fails loudly instead of skipping them.
UTF8_LOCALES = []
for name in LOCALE_CANDIDATES:
    if len(UTF8_LOCALES) == 2:
        break
    if any(name.split('.')[0] == chosen.split('.')[0] for chosen in UTF8_LOCALES):
        continue
    if locale_is_usable(name):
        UTF8_LOCALES.append(name)
if not UTF8_LOCALES:
    print('  FAIL  PREREQ: no UTF-8 locale among ' + ', '.join(LOCALE_CANDIDATES) + ' makes '
          "bash's [0-9] match an Arabic-Indic digit, so the LOCALE cases cannot be exercised; "
          'install one of them (for example en_US.UTF-8)')
    sys.exit(1)


# ---------------------------------------------------------------- fixtures

def manifest_for(guides):
    return ''.join(f'{hashlib.sha256(body).hexdigest()}  {name}\n'
                   for name, body in guides.items()).encode()


def release_json(tag=TAG, **fields):
    data = {'tag_name': tag, 'draft': False, 'prerelease': False}
    data.update(fields)
    return json.dumps(data).encode()


def padded_release(size):
    """A valid published-release answer of exactly size bytes."""
    head = release_json()[:-1] + b', "pad": "'
    return head + b'x' * (size - len(head) - 2) + b'"}'


def build(base, version=PUBLISHED.encode() + b'\n', plugin_text=PLUGIN_JSON,
          guides=None, manifest=None, release=None, tag=TAG):
    """A plugin tree, a fixture folder the shim serves, the shim, a working directory.

    release is the bytes the API answers with (default: a published release named tag), or False
    for no release. The VERSION, manifest and guides are served under refs/tags/<tag>/."""
    guides = NEW_GUIDES if guides is None else guides
    plugin = base / 'plugin'
    skill = plugin / 'skills' / 'secureconfig'
    (skill / 'scripts').mkdir(parents=True)
    (skill / 'references').mkdir()
    script = skill / 'scripts' / 'update-guides.sh'
    shutil.copyfile(SCRIPT, script)
    (plugin / 'plugin.json').write_text(plugin_text, encoding='utf-8')
    for name, body in OLD_GUIDES.items():
        (skill / 'references' / name).write_bytes(body)
    (skill / 'references' / 'MANIFEST.sha256').write_bytes(manifest_for(OLD_GUIDES))

    fixtures = base / 'fixtures'
    served = fixtures / tag
    (served / MANIFEST_PATH).parent.mkdir(parents=True)
    (fixtures / '_api').mkdir()
    if release is not False:
        (fixtures / '_api' / 'releases-latest.json').write_bytes(
            release_json(tag) if release is None else release)
    if version is not None:
        (served / 'VERSION').write_bytes(version)
    for name, body in guides.items():
        (served / name).write_bytes(body)
    (served / MANIFEST_PATH).write_bytes(manifest_for(guides) if manifest is None else manifest)

    shim_dir = base / 'bin'
    shim_dir.mkdir()
    log = base / 'curl.log'
    log.write_bytes(b'')
    shim = shim_dir / 'curl'
    shim.write_text(SHIM.replace('@LOG@', shlex.quote(str(log)))
                    .replace('@FIXTURES@', shlex.quote(str(fixtures))), encoding='utf-8')
    shim.chmod(0o755)
    cwd = base / 'cwd'
    cwd.mkdir()
    tmp = base / 'tmp'
    tmp.mkdir()
    env = {'PATH': str(shim_dir) + os.pathsep + BASE_PATH, 'HOME': str(cwd),
           'TMPDIR': str(tmp), 'LC_ALL': 'C'}
    return SimpleNamespace(plugin_json=plugin / 'plugin.json', skill=skill,
                           refs=skill / 'references', script=script, fixtures=fixtures,
                           shim=shim, log=log, cwd=cwd, tmp=tmp, env=env)


def run(t):
    try:
        done = subprocess.run([BASH, str(t.script)], cwd=t.cwd, env=t.env, stdin=subprocess.DEVNULL,
                              capture_output=True, timeout=60)
    except subprocess.TimeoutExpired:
        return None, b'', b'(timed out)'
    return done.returncode, done.stdout, done.stderr


def state(t):
    """plugin.json bytes, every reference file, the skill folder listing and the temp folder."""
    return (t.plugin_json.read_bytes(),
            {p.name: p.read_bytes() for p in sorted(t.refs.iterdir())},
            sorted(p.name for p in t.skill.iterdir()),
            sorted(p.name for p in t.tmp.iterdir()))


def fetched(t):
    return t.log.read_text(encoding='utf-8', errors='replace').splitlines()


def echoes(token, output):
    """True if output holds token not glued into a longer word or number."""
    if not token:
        return False
    pattern = rb'(?<![A-Za-z0-9])' + re.escape(token) + rb'(?![A-Za-z0-9])'
    return re.search(pattern, output) is not None


def show(data, limit=200):
    text = data.decode('utf-8', errors='replace')
    return repr(text if len(text) <= limit else text[:limit] + '...')


def prefixed(label, locale):
    return label if locale == 'C' else f'LOCALE {locale}: {label}'


# ---------------------------------------------------------------- SHIM

with tempfile.TemporaryDirectory() as tmp:
    t = build(Path(tmp))
    done = subprocess.run([str(t.shim), '-fsS', '--max-time', '30', 'https://example.com/VERSION'],
                          cwd=t.cwd, env=t.env, capture_output=True, timeout=60)
    check(done.returncode == 22, f'SHIM: an unknown URL should exit 22: {done.returncode}')
    target = t.tmp / 'out'
    done = subprocess.run([str(t.shim), '-fsS', '--max-time', '30', '-o', str(target), RAW + 'beta.md'],
                          cwd=t.cwd, env=t.env, capture_output=True, timeout=60)
    check(done.returncode == 0 and target.is_file() and target.read_bytes() == NEW_GUIDES['beta.md']
          and not done.stdout, 'SHIM: -o FILE should write the fixture and print nothing')
    check(fetched(t) == ['https://example.com/VERSION', RAW + 'beta.md'],
          f'SHIM: every URL should be logged: {fetched(t)!r}')
    main_url = 'https://raw.githubusercontent.com/jposluns/secureconfig/main/VERSION'
    done = subprocess.run([str(t.shim), '-fsS', '--max-time', '30', main_url],
                          cwd=t.cwd, env=t.env, capture_output=True, timeout=60)
    check(done.returncode == 22, f'SHIM: a URL under main should exit 22: {done.returncode}')
    done = subprocess.run([str(t.shim), '-fsS', '--max-time', '30', API],
                          cwd=t.cwd, env=t.env, capture_output=True, timeout=60)
    check(done.returncode == 0 and json.loads(done.stdout)['tag_name'] == TAG,
          f'SHIM: the API URL should serve the release fixture: {done.returncode} {show(done.stdout)}')
    t = build(Path(tmp) / 'norelease', release=False)
    done = subprocess.run([str(t.shim), '-fsS', '--max-time', '30', API],
                          cwd=t.cwd, env=t.env, capture_output=True, timeout=60)
    check(done.returncode == 22, f'SHIM: no release should make the API URL exit 22: {done.returncode}')

# ---------------------------------------------------------------- GOOD


def check_updated(t, rc, out, err, label):
    check(rc == 0, f'{label}: should exit 0: {rc} {show(err)}')
    try:
        version = json.loads(t.plugin_json.read_text(encoding='utf-8')).get('version')
    except ValueError:
        version = None
    check(version == PUBLISHED, f'{label}: plugin.json should be re-pinned to {PUBLISHED}: {version!r}')
    want = dict(NEW_GUIDES, **{'MANIFEST.sha256': manifest_for(NEW_GUIDES)})
    got = {p.name: p.read_bytes() for p in t.refs.iterdir()}
    check(got == want, f'{label}: references should be the published set: {sorted(got)!r}')
    check(sorted(p.name for p in t.skill.iterdir()) == ['references', 'scripts'],
          f'{label}: no references.new or other leftover: {sorted(p.name for p in t.skill.iterdir())!r}')
    check(f'installed {INSTALLED}, published {PUBLISHED}'.encode() in out
          and f'updated {len(NEW_GUIDES)} guides and re-pinned to {PUBLISHED}'.encode() in out,
          f'{label}: stdout should say it updated: {show(out)}')
    check(fetched(t) == [API, RAW + 'VERSION', RAW + MANIFEST_PATH] + [RAW + n for n in NEW_GUIDES],
          f'{label}: every fetch should go through the shim, in order: {fetched(t)!r}')
    check(not list(t.tmp.iterdir()), f'{label}: the work folder should be removed')


def check_good(desc, version=PUBLISHED.encode() + b'\n', locale='C'):
    with tempfile.TemporaryDirectory() as tmp:
        t = build(Path(tmp), version=version)
        t.env['LC_ALL'] = locale
        rc, out, err = run(t)
        check_updated(t, rc, out, err, prefixed(desc, locale))


check_good('GOOD')
check_good('GOOD: no trailing newline', version=PUBLISHED.encode())
check_good('GOOD: a CR LF line end', version=PUBLISHED.encode() + b'\r\n')

# ---------------------------------------------------------------- SAME

with tempfile.TemporaryDirectory() as tmp:
    t = build(Path(tmp), version=INSTALLED.encode() + b'\n', tag='v' + INSTALLED)
    before = state(t)
    rc, out, err = run(t)
    check(rc == 0 and f'already at {INSTALLED}; nothing to do'.encode() in out,
          f'SAME: should exit 0 and say nothing to do: {rc} {show(out)} {show(err)}')
    check(state(t) == before, 'SAME: nothing should change')
    check(fetched(t) == [API], f'SAME: only the API answer should be fetched: {fetched(t)!r}')

# ---------------------------------------------------------------- OLDER

for desc, installed, tag in (('one patch older', INSTALLED, 'v1.0.3'),
                             ('numerically older, textually later', '1.0.10', 'v1.0.9'),
                             ('older with leading zeros', INSTALLED, 'v1.0.03')):
    with tempfile.TemporaryDirectory() as tmp:
        t = build(Path(tmp), version=tag[1:].encode() + b'\n', tag=tag,
                  plugin_text=PLUGIN_JSON.replace(INSTALLED, installed))
        before = state(t)
        rc, out, err = run(t)
        check(rc == 0 and f'installed {installed} is newer than the latest release {tag[1:]}; '
              'nothing to do'.encode() in out and not err,
              f'OLDER {desc}: should exit 0 and report, not downgrade: {rc} {show(out)} {show(err)}')
        check(state(t) == before, f'OLDER {desc}: nothing should change')
        check(fetched(t) == [API], f'OLDER {desc}: only the API answer should be fetched: {fetched(t)!r}')

# A later release whose number is textually earlier is newer: 1.0.10 over an installed 1.0.9.
with tempfile.TemporaryDirectory() as tmp:
    t = build(Path(tmp), version=b'1.0.10\n', tag='v1.0.10',
              plugin_text=PLUGIN_JSON.replace(INSTALLED, '1.0.9'))
    rc, out, err = run(t)
    got = json.loads(t.plugin_json.read_text(encoding='utf-8')).get('version')
    check(rc == 0 and got == '1.0.10' and fetched(t)[:2] == [API, RAW_PREFIX + 'v1.0.10/VERSION'],
          f'OLDER: 1.0.10 over an installed 1.0.9 should update: {rc} {got!r} {show(err)}')

# ---------------------------------------------------------------- NO RELEASE

with tempfile.TemporaryDirectory() as tmp:
    t = build(Path(tmp), release=False)
    before = state(t)
    rc, out, err = run(t)
    check(rc == 1 and NO_RELEASE_MESSAGE in err and not out,
          f'NO RELEASE: should refuse with exit 1: {rc} {show(out)} {show(err)}')
    check(b'refused the request, as it does at a rate limit' in err,
          f'NO RELEASE: the message should name a refusal such as a rate limit (403, 429): {show(err)}')
    check(state(t) == before, 'NO RELEASE: nothing should change')
    check(fetched(t) == [API], f'NO RELEASE: only the API should be asked: {fetched(t)!r}')

# ---------------------------------------------------------------- BAD TAG


def check_bad_release(desc, release, tokens, locale='C'):
    """An API answer that holds release is refused: exit 1, BAD_TAG_MESSAGE on stderr only, no
    token echoed, nothing changed, only the API fetched."""
    with tempfile.TemporaryDirectory() as tmp:
        t = build(Path(tmp), release=release)
        t.env['LC_ALL'] = locale
        before = state(t)
        rc, out, err = run(t)
        both = out + b'\n' + err
        label = prefixed(f'BAD TAG: {desc}', locale)
        check(rc == 1 and BAD_TAG_MESSAGE in err and not out,
              f'{label}: should refuse with exit 1 on stderr only: {rc} {show(out)} {show(err)}')
        check(not any(echoes(token, both) for token in tokens) and b'\x1b' not in both,
              f'{label}: the value should not be echoed: {show(err)}')
        check(b'Traceback' not in err, f'{label}: no Python traceback should reach stderr: {show(err)}')
        check(state(t) == before, f'{label}: nothing should change')
        check(fetched(t) == [API], f'{label}: only the API should be fetched: {fetched(t)!r}')


for desc, tag in (
        ('no v', '1.0.5'), ('a capital V', 'V1.0.5'), ('two parts', 'v1.0'),
        ('four parts', 'v1.0.5.6'), ('a pre-release suffix', 'v1.0.5-rc1'),
        ('a trailing line end', 'v1.0.5\n'), ('a leading blank', ' v1.0.5'),
        ('a second line', 'v1.0.5\nv1.0.6'), ('a terminal escape', 'v1.0.5\x1b[31m'),
        ('non-ASCII digits', 'v١.٠.٥'), ('a path', 'v1.0.5/../../main'),
        ('a word', 'latest'), ('empty', ''), ('a v alone', 'v')):
    shown = tag.strip().encode() if tag.isascii() and any(c.isdigit() for c in tag) else b''
    check_bad_release(desc, release_json(tag), [shown] if shown else [])

for desc, release in (
        ('a number', release_json(105)), ('null', release_json(None)),
        ('a list', release_json(['v1.0.5'])),
        ('no tag_name', json.dumps({'draft': False, 'prerelease': False}).encode()),
        ('a draft', release_json(draft=True)), ('a pre-release', release_json(prerelease=True)),
        ('no draft field', json.dumps({'tag_name': TAG, 'prerelease': False}).encode()),
        ('no prerelease field', json.dumps({'tag_name': TAG, 'draft': False}).encode()),
        ('draft as a string', release_json(draft='false')),
        ('draft as the number 0', release_json(draft=0)),
        ('prerelease as the number 0', release_json(prerelease=0)),
        ('nested 200000 deep (a RecursionError)', b'[' * 200000),
        ('one byte over the bound', padded_release(1048577)),
        ('a list answer', json.dumps([{'tag_name': TAG}]).encode()),
        ('not JSON', b'<html>rate limited</html>'), ('empty body', b''),
        ('a NUL byte', b'{"tag_name": "v1.0.5\\u0000", "draft": false, "prerelease": false}'),
        ('too large', b'{"tag_name": "' + TAG.encode() + b'", "draft": false, "prerelease": false, '
         b'"body": "' + b'x' * 1048576 + b'"}')):
    check_bad_release(desc, release, [b'rate limited'])

# The bound is exact: a valid answer of exactly 1 MiB is read and used, one byte more is refused
# (above), so a bound off by one fails one of the two.
check(len(padded_release(1048576)) == 1048576 and len(padded_release(1048577)) == 1048577,
      'BOUND: the fixtures should be exactly 1 MiB and 1 MiB + 1 bytes')
with tempfile.TemporaryDirectory() as tmp:
    t = build(Path(tmp), release=padded_release(1048576))
    rc, out, err = run(t)
    check_updated(t, rc, out, err, 'BOUND: a valid answer of exactly 1 MiB')

# Defence in depth that no behaviour case can separate: both checks of an ASCII-only tag, the
# python isascii test and the explicit digit list in the regex, must stay, each covering the other.
_text = SCRIPT.read_text(encoding='utf-8')
check(_text.count('.isascii()') == 2 and '0-9' not in re.sub(r'#.*', '', _text),
      'DEPTH: both python blocks should test isascii and no regex should use a 0-9 range')

# ---------------------------------------------------------------- TAG MISMATCH

with tempfile.TemporaryDirectory() as tmp:
    t = build(Path(tmp), version=b'1.0.6\n')
    before = state(t)
    rc, out, err = run(t)
    check(rc == 1 and MISMATCH_MESSAGE in err and b'1.0.6' not in err,
          f'TAG MISMATCH: a VERSION that differs from its tag should be refused: {rc} {show(err)}')
    check(state(t) == before, 'TAG MISMATCH: nothing should change')
    check(fetched(t) == [API, RAW + 'VERSION'],
          f'TAG MISMATCH: nothing after VERSION should be fetched: {fetched(t)!r}')

# ---------------------------------------------------------------- BAD PUBLISHED


def check_bad_published(desc, raw, locale='C'):
    """VERSION holding raw is refused: exit 1, the message on stderr only, the value not echoed,
    nothing changed and nothing fetched after VERSION."""
    with tempfile.TemporaryDirectory() as tmp:
        t = build(Path(tmp), version=raw)
        t.env['LC_ALL'] = locale
        before = state(t)
        rc, out, err = run(t)
        both = out + b'\n' + err
        label = prefixed(f'BAD PUBLISHED: {desc}', locale)
        check(rc == 1, f'{label}: should exit 1: {rc}')
        check(BAD_PUBLISHED_MESSAGE in err and not out,
              f'{label}: should say so on stderr only: {show(out)} {show(err)}')
        # The value as stripping every whitespace byte and dropping every NUL would leave it (an
        # earlier form of the script read "1.0.5\n6\n" as 1.0.56), and each blank-separated
        # piece without its NUL bytes; none of them may appear in the output.
        stripped = bytes(b for b in raw if b not in b' \t\n\r\v\f\x00')
        tokens = [stripped] + [piece.replace(b'\x00', b'') for piece in raw.split()]
        check(not any(echoes(token, both) for token in tokens)
              and b'\x1b' not in both and b'\x07' not in both and b'\x00' not in both,
              f'{label}: the raw value should not be echoed: {show(err)}')
        check(state(t) == before, f'{label}: nothing should change')
        check(fetched(t) == [API, RAW + 'VERSION'],
              f'{label}: nothing after VERSION should be fetched')


for desc, raw in (
        ('two parts', b'1.0\n'),
        ('four parts', b'1.0.5.6\n'),
        ('a v prefix', b'v1.0.5\n'),
        ('a pre-release suffix', b'1.0.5-rc1\n'),
        ('a terminal escape', b'1.0.5\x1b[31m\n'),
        ('a word', b'abc\n'),
        ('a second line', b'1.0.5\n1.0.6\n'),
        ('a trailing dot', b'1.0.5.\n'),
        ('a sign', b'+1.0.5\n'),
        ('non-ASCII digits', '١.٠.٥\n'.encode()),
        ('a huge run of digits', b'9' * 200000 + b'\n'),
        ('a huge garbage line', b'garbage\x07' * 25000 + b'\n'),
        ('a second line that stripping would join into 1.0.56', b'1.0.5\n6\n'),
        ('a trailing blank before the newline', b'1.0.5 \n'),
        ('a trailing blank and no newline', b'1.0.5 '),
        ('a leading blank', b' 1.0.5\n'),
        ('a blank inside', b'1.0 .5\n'),
        ('two trailing newlines', b'1.0.5\n\n'),
        ('a lone trailing CR', b'1.0.5\r'),
        ('a CR inside', b'1.0\r.5\n'),
        ('an embedded NUL', b'1.0.\x005\n'),
        ('a trailing NUL', b'1.0.5\x00')):
    check_bad_published(desc, raw)

for desc, raw in (('empty', b''), ('a newline', b'\n'), ('blanks', b'  \t\n\n')):
    with tempfile.TemporaryDirectory() as tmp:
        t = build(Path(tmp), version=raw)
        before = state(t)
        rc, out, err = run(t)
        label = f'BAD PUBLISHED: {desc}'
        check(rc == 1 and EMPTY_PUBLISHED_MESSAGE in err and not out,
              f'{label}: should keep the empty-value message: {rc} {show(err)}')
        check(state(t) == before, f'{label}: nothing should change')
        check(fetched(t) == [API, RAW + 'VERSION'],
              f'{label}: nothing after VERSION should be fetched')

with tempfile.TemporaryDirectory() as tmp:
    t = build(Path(tmp), version=None)
    before = state(t)
    rc, out, err = run(t)
    check(rc not in (0, None) and state(t) == before and fetched(t) == [API, RAW + 'VERSION'],
          f'BAD PUBLISHED: a VERSION the shim does not have should refuse, nothing changed: {rc}')

# ---------------------------------------------------------------- BAD LOCAL


def check_bad_local(desc, text, tokens, locale='C'):
    """plugin.json holding text is refused before any fetch: exit 1, the message on stderr only,
    no token echoed, nothing written."""
    with tempfile.TemporaryDirectory() as tmp:
        t = build(Path(tmp), plugin_text=text)
        t.env['LC_ALL'] = locale
        before = state(t)
        rc, out, err = run(t)
        both = out + b'\n' + err
        label = prefixed(f'BAD LOCAL: {desc}', locale)
        check(rc == 1, f'{label}: should exit 1: {rc}')
        check(BAD_LOCAL_MESSAGE in err and not out,
              f'{label}: should say so on stderr only: {show(out)} {show(err)}')
        check(not any(echoes(token, both) for token in tokens) and b'\x1b' not in both,
              f'{label}: the local value should not be echoed: {show(err)}')
        check(b'Traceback' not in err, f'{label}: no Python traceback should reach stderr: {show(err)}')
        check(state(t) == before, f'{label}: nothing should be written')
        check(fetched(t) == [], f'{label}: nothing should be fetched: {fetched(t)!r}')


for desc, text, tokens in (
        ('"x"', '{"name": "secureconfig", "version": "x"}\n', [b'x']),
        ('no version key', '{"name": "secureconfig"}\n', []),
        ('a number', '{"name": "secureconfig", "version": 105}\n', [b'105']),
        ('null', '{"name": "secureconfig", "version": null}\n', [b'None', b'null']),
        ('a list', '{"name": "secureconfig", "version": ["1.0.4"]}\n', [b'1.0.4']),
        ('an escape', '{"name": "secureconfig", "version": "1.0.4\\u001b[31m"}\n', [b'1.0.4', b'\x1b']),
        ('a second line', '{"name": "secureconfig", "version": "1.0.4\\n1.0.6"}\n', [b'1.0.4', b'1.0.6']),
        ('two parts', '{"name": "secureconfig", "version": "1.0"}\n', [b'1.0']),
        ('not an object', '["1.0.4"]\n', [b'1.0.4']),
        ('nested 200000 deep (a RecursionError)', '[' * 200000 + '\n', [])):
    check_bad_local(desc, text, tokens)

# ---------------------------------------------------------------- LOCALE

# Negative control for the probe: under LC_ALL=C, [0-9] does not match an Arabic-Indic digit, so a
# probe that passed there would be broken, not the locale useful.
check(not locale_is_usable('C'),
      'LOCALE: negative control: the probe should be false under LC_ALL=C, or it proves nothing')

ARABIC_INDIC = '\u0661.\u0660.\u0665'  # ARABIC-INDIC DIGIT ONE, ZERO, FIVE
for locale in UTF8_LOCALES:
    for desc, raw in (
            ('Arabic-Indic digits', (ARABIC_INDIC + '\n').encode()),
            # U+00B9 SUPERSCRIPT ONE, then U+2075 SUPERSCRIPT FIVE
            ('a superscript first digit', '\u00b9.0.5\n'.encode()),
            ('a superscript last digit', '1.0.\u2075\n'.encode()),
            # U+FF11, U+FF10, U+FF15: FULLWIDTH DIGIT ONE, ZERO, FIVE
            ('fullwidth digits', '\uff11.\uff10.\uff15\n'.encode())):
        check_bad_published(desc, raw, locale)
    # python3 already empties a version that is not ASCII, so this case shows that the refusal
    # before any fetch holds under this locale; it does not reach version_re with the digits.
    check_bad_local('Arabic-Indic digits',
                    '{"name": "secureconfig", "version": "' + ARABIC_INDIC + '"}\n',
                    [ARABIC_INDIC.encode()], locale)
    check_bad_release('Arabic-Indic digits', release_json('v' + ARABIC_INDIC), [], locale)
    check_good('GOOD', locale=locale)

# ---------------------------------------------------------------- ISOLATION

script_text = SCRIPT.read_text(encoding='utf-8')
calls = [script_text[m.end():m.end() + 4] for m in re.finditer(r'\bpython3\b', script_text)]
check(len(calls) >= 2 and all(re.match(r' -I\s', rest) for rest in calls),
      f'ISOLATION: every python3 in the script should be "python3 -I": {calls!r}')

with tempfile.TemporaryDirectory() as tmp:
    t = build(Path(tmp))
    (t.cwd / 'json.py').write_text(PLANT, encoding='utf-8')
    marker = t.cwd / MARKER
    rc, out, err = run(t)
    check(not marker.exists(), 'ISOLATION: the planted json.py ran inside update-guides.sh')
    check_updated(t, rc, out, err, 'ISOLATION')
    python3 = shutil.which('python3', path=t.env['PATH'])
    done = subprocess.run([python3, '-c', 'import json'], cwd=t.cwd, env=t.env,
                          stdin=subprocess.DEVNULL, capture_output=True, timeout=60)
    check(marker.exists(),
          'ISOLATION: negative control: python3 -c "import json" without -I in the planted folder '
          f'should run the plant, or this case proves nothing: {done.returncode}')

# ---------------------------------------------------------------- MANIFEST

bad_digest = manifest_for({'alpha.md': NEW_GUIDES['alpha.md'], 'beta.md': b'something else\n'})
escape = manifest_for(NEW_GUIDES) + manifest_for({'../x': b'x\n'})
# sha256sum without --strict only warns on a line that is not a digest line and checks the rest, so
# the guide on that line would be installed unverified.
malformed = b'zz-not-a-digest  alpha.md\n' + manifest_for({'beta.md': NEW_GUIDES['beta.md']})
for desc, manifest, message in (
        ('a tampered digest', bad_digest, b'a fetched guide did not match its published digest'),
        ('a malformed digest line', malformed,
         b'a fetched guide did not match its published digest'),
        ('a "../x" entry', escape, b'the manifest lists an unexpected file name')):
    with tempfile.TemporaryDirectory() as tmp:
        t = build(Path(tmp), manifest=manifest)
        before = state(t)
        rc, out, err = run(t)
        label = f'MANIFEST: {desc}'
        check(rc == 1 and message in err, f'{label}: should refuse: {rc} {show(err)}')
        check(state(t) == before, f'{label}: nothing should change')
        check(fetched(t)[:3] == [API, RAW + 'VERSION', RAW + MANIFEST_PATH]
              and not any('..' in url for url in fetched(t)),
              f'{label}: fetches through the shim, never the "../x" entry: {fetched(t)!r}')
        check(not (t.tmp / 'x').exists() and not (Path(tmp) / 'x').exists(),
              f'{label}: nothing written outside the work folder')

if failures:
    for failure in failures:
        print(f'  FAIL  {failure}')
    sys.exit(1)
print(f'  ok    {cases} cases for update-guides.sh, offline on a curl shim: the shim itself, an '
      'update from the latest release tag, nothing to do, an older release not installed, no '
      'release, refused tags, release objects and tag mismatch, refused published and local '
      'versions, non-ASCII digits refused '
      'and an update under ' + ' and '.join(UTF8_LOCALES) + ', python3 -I against a planted '
      'json.py with its negative control, and refused manifests')
