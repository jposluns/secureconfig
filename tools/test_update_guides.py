#!/usr/bin/env python3
"""Offline cases for plugin/skills/secureconfig/scripts/update-guides.sh.

No case reaches the network and nothing listens. Each case builds a temporary tree laid out like
the plugin (plugin.json, skills/secureconfig/scripts/update-guides.sh copied from this repository,
skills/secureconfig/references with two guides and a MANIFEST.sha256), because the script finds
plugin.json and the references relative to itself, and runs it as bash <script> with an explicit
minimal environment and a working directory the test controls. A bash shim named curl comes first
on PATH: it maps a URL under https://raw.githubusercontent.com/jposluns/secureconfig/main/ to a
file in the case's fixture folder, honours -o FILE, ignores -fsS and --max-time N, exits 22 for
any other URL, and appends every URL it is asked for to a log. Each case checks that log, so a
fetch the shim did not make fails the case. The script's RAW constant is unchanged; there is no
override for it. This process also replaces the socket connect functions with one that raises.

  - SHIM: an unknown URL exits 22, -o writes the fixture, and both are logged;
  - GOOD: a newer N.N.N with a matching manifest replaces the references, re-pins plugin.json and
    says so, fetching VERSION, the manifest and each guide through the shim, in that order;
  - SAME: the published version equal to the installed one is "nothing to do", nothing changed;
  - BAD PUBLISHED: 1.0, 1.0.5.6, v1.0.5, 1.0.5-rc1, a terminal escape, a word, a second line, a
    trailing dot, a sign, non-ASCII digits, a huge run of digits and a huge garbage line are each
    refused with exit 1 and a message that does not echo the value, nothing written and nothing
    fetched after VERSION; an empty or blank VERSION keeps its own message, and a VERSION the
    shim does not have is refused too;
  - BAD LOCAL: a plugin.json version of "x", none, a number, null, a list, an escape, a second
    line or two parts, and a plugin.json that is not an object, are refused before any fetch,
    with exit 1 and a message that does not echo the value, nothing written;
  - ISOLATION: every python3 in the script text carries -I; with a json.py planted in the working
    directory the update succeeds and the plant never runs, and a plain python3 -c 'import json'
    in that same directory does run it (the negative control);
  - MANIFEST: a tampered digest and a "../x" entry are each refused, nothing changed.

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
RAW = 'https://raw.githubusercontent.com/jposluns/secureconfig/main/'
MANIFEST_PATH = 'plugin/skills/secureconfig/references/MANIFEST.sha256'
INSTALLED = '1.0.4'
PUBLISHED = '1.0.5'
OLD_GUIDES = {'alpha.md': b'# Alpha\n\nInstalled text.\n',
              'gamma.md': b'# Gamma\n\nOnly in the installed bundle.\n'}
NEW_GUIDES = {'alpha.md': b'# Alpha\n\nPublished text.\n',
              'beta.md': b'# Beta\n\nA new guide.\n'}
PLUGIN_JSON = '{\n  "name": "secureconfig",\n  "version": "1.0.4"\n}\n'
BAD_PUBLISHED_MESSAGE = b'the published version is not of the form N.N.N'
EMPTY_PUBLISHED_MESSAGE = b'could not read the published version; nothing changed'
BAD_LOCAL_MESSAGE = b'plugin.json records no version of the form N.N.N'
MARKER = 'json-was-imported'

# The shim is written per case with its log and fixture folder as literals, so it reads no
# environment variable and the script needs none.
SHIM = r'''#!/usr/bin/env bash
# Stand-in for curl, written by tools/test_update_guides.py: fixture files only, no network.
set -u
log=@LOG@
fixtures=@FIXTURES@
prefix=https://raw.githubusercontent.com/jposluns/secureconfig/main/
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
for tool in ('bash', 'python3', 'sha256sum', 'tr', 'mktemp', 'cp', 'mv', 'rm', 'mkdir', 'cat'):
    if not shutil.which(tool, path=BASE_PATH):
        print(f'  FAIL  PREREQ: {tool} is not on PATH, so update-guides.sh cannot be exercised')
        sys.exit(1)
if not SCRIPT.is_file():
    print(f'  FAIL  PREREQ: {SCRIPT} is missing')
    sys.exit(1)


# ---------------------------------------------------------------- fixtures

def manifest_for(guides):
    return ''.join(f'{hashlib.sha256(body).hexdigest()}  {name}\n'
                   for name, body in guides.items()).encode()


def build(base, version=PUBLISHED.encode() + b'\n', plugin_text=PLUGIN_JSON,
          guides=None, manifest=None):
    """A plugin tree, a fixture folder the shim serves, the shim, a working directory."""
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
    (fixtures / MANIFEST_PATH).parent.mkdir(parents=True)
    if version is not None:
        (fixtures / 'VERSION').write_bytes(version)
    for name, body in guides.items():
        (fixtures / name).write_bytes(body)
    (fixtures / MANIFEST_PATH).write_bytes(manifest_for(guides) if manifest is None else manifest)

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
    check(fetched(t) == [RAW + 'VERSION', RAW + MANIFEST_PATH] + [RAW + n for n in NEW_GUIDES],
          f'{label}: every fetch should go through the shim, in order: {fetched(t)!r}')
    check(not list(t.tmp.iterdir()), f'{label}: the work folder should be removed')


with tempfile.TemporaryDirectory() as tmp:
    t = build(Path(tmp))
    rc, out, err = run(t)
    check_updated(t, rc, out, err, 'GOOD')

# ---------------------------------------------------------------- SAME

with tempfile.TemporaryDirectory() as tmp:
    t = build(Path(tmp), version=INSTALLED.encode() + b'\n')
    before = state(t)
    rc, out, err = run(t)
    check(rc == 0 and f'already at {INSTALLED}; nothing to do'.encode() in out,
          f'SAME: should exit 0 and say nothing to do: {rc} {show(out)} {show(err)}')
    check(state(t) == before, 'SAME: nothing should change')
    check(fetched(t) == [RAW + 'VERSION'], f'SAME: only VERSION should be fetched: {fetched(t)!r}')

# ---------------------------------------------------------------- BAD PUBLISHED

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
        ('a huge garbage line', b'garbage\x07' * 25000 + b'\n')):
    with tempfile.TemporaryDirectory() as tmp:
        t = build(Path(tmp), version=raw)
        before = state(t)
        rc, out, err = run(t)
        both = out + b'\n' + err
        label = f'BAD PUBLISHED: {desc}'
        check(rc == 1, f'{label}: should exit 1: {rc}')
        check(BAD_PUBLISHED_MESSAGE in err and not out,
              f'{label}: should say so on stderr only: {show(out)} {show(err)}')
        stripped = bytes(b for b in raw if b not in b' \t\n\r\v\f')
        check(not any(echoes(token, both) for token in [stripped] + raw.split())
              and b'\x1b' not in both and b'\x07' not in both,
              f'{label}: the raw value should not be echoed: {show(err)}')
        check(state(t) == before, f'{label}: nothing should change')
        check(fetched(t) == [RAW + 'VERSION'], f'{label}: nothing after VERSION should be fetched')

for desc, raw in (('empty', b''), ('a newline', b'\n'), ('blanks', b'  \t\n\n')):
    with tempfile.TemporaryDirectory() as tmp:
        t = build(Path(tmp), version=raw)
        before = state(t)
        rc, out, err = run(t)
        label = f'BAD PUBLISHED: {desc}'
        check(rc == 1 and EMPTY_PUBLISHED_MESSAGE in err and not out,
              f'{label}: should keep the empty-value message: {rc} {show(err)}')
        check(state(t) == before, f'{label}: nothing should change')
        check(fetched(t) == [RAW + 'VERSION'], f'{label}: nothing after VERSION should be fetched')

with tempfile.TemporaryDirectory() as tmp:
    t = build(Path(tmp), version=None)
    before = state(t)
    rc, out, err = run(t)
    check(rc not in (0, None) and state(t) == before and fetched(t) == [RAW + 'VERSION'],
          f'BAD PUBLISHED: a VERSION the shim does not have should refuse, nothing changed: {rc}')

# ---------------------------------------------------------------- BAD LOCAL

for desc, text, tokens in (
        ('"x"', '{"name": "secureconfig", "version": "x"}\n', [b'x']),
        ('no version key', '{"name": "secureconfig"}\n', []),
        ('a number', '{"name": "secureconfig", "version": 105}\n', [b'105']),
        ('null', '{"name": "secureconfig", "version": null}\n', [b'None', b'null']),
        ('a list', '{"name": "secureconfig", "version": ["1.0.4"]}\n', [b'1.0.4']),
        ('an escape', '{"name": "secureconfig", "version": "1.0.4\\u001b[31m"}\n', [b'1.0.4', b'\x1b']),
        ('a second line', '{"name": "secureconfig", "version": "1.0.4\\n1.0.6"}\n', [b'1.0.4', b'1.0.6']),
        ('two parts', '{"name": "secureconfig", "version": "1.0"}\n', [b'1.0']),
        ('not an object', '["1.0.4"]\n', [b'1.0.4'])):
    with tempfile.TemporaryDirectory() as tmp:
        t = build(Path(tmp), plugin_text=text)
        before = state(t)
        rc, out, err = run(t)
        both = out + b'\n' + err
        label = f'BAD LOCAL: {desc}'
        check(rc == 1, f'{label}: should exit 1: {rc}')
        check(BAD_LOCAL_MESSAGE in err and not out,
              f'{label}: should say so on stderr only: {show(out)} {show(err)}')
        check(not any(echoes(token, both) for token in tokens) and b'\x1b' not in both,
              f'{label}: the local value should not be echoed: {show(err)}')
        check(state(t) == before, f'{label}: nothing should be written')
        check(fetched(t) == [], f'{label}: nothing should be fetched: {fetched(t)!r}')

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
for desc, manifest, message in (
        ('a tampered digest', bad_digest, b'a fetched guide did not match its published digest'),
        ('a "../x" entry', escape, b'the manifest lists an unexpected file name')):
    with tempfile.TemporaryDirectory() as tmp:
        t = build(Path(tmp), manifest=manifest)
        before = state(t)
        rc, out, err = run(t)
        label = f'MANIFEST: {desc}'
        check(rc == 1 and message in err, f'{label}: should refuse: {rc} {show(err)}')
        check(state(t) == before, f'{label}: nothing should change')
        check(fetched(t)[:2] == [RAW + 'VERSION', RAW + MANIFEST_PATH]
              and not any('..' in url for url in fetched(t)),
              f'{label}: fetches through the shim, never the "../x" entry: {fetched(t)!r}')
        check(not (t.tmp / 'x').exists() and not (Path(tmp) / 'x').exists(),
              f'{label}: nothing written outside the work folder')

if failures:
    for failure in failures:
        print(f'  FAIL  {failure}')
    sys.exit(1)
print(f'  ok    {cases} cases for update-guides.sh, offline on a curl shim: the shim itself, an '
      'update, nothing to do, refused published and local versions, python3 -I against a planted '
      'json.py with its negative control, and refused manifests')
