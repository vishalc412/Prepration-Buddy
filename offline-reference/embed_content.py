"""Rebuild the self-contained offline curriculum from authored local content."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
reference = root / 'offline-reference'
html = root / 'index.html'
text = html.read_text()

def strip_block(source, begin, end):
    if begin in source:
        a, b = source.index(begin), source.index(end) + len(end)
        if a and source[a-1] == '\n':
            a -= 1
        if source[b:b+1] == '\n':
            b += 1
        return source[:a] + source[b:]
    return source

def read(name):
    return json.loads((reference / f'{name}.json').read_text())

def safe_json(data):
    return json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')

text = strip_block(text, '// OFFLINE_CONTENT_BEGIN', '// OFFLINE_CONTENT_END')
text = strip_block(text, '// COURSE_EXTENSION_BEGIN', '// COURSE_EXTENSION_END')
data = {name: read(name) for name in ('answers', 'lessons', 'labs', 'resources')}
mid = read('midcourse')
data['lessons'].append(mid['lesson'])
extended = [read('extended-foundations'), read('extended-production')]
new_days = []
for part in extended:
    new_days.extend(part['days'])
    for name in ('lessons', 'labs'):
        data[name].extend(part[name])
    for name in ('daily', 'design'):
        data['answers'][name].extend(part[name])
data['client'] = read('client-foundations') + read('client-production')
data['jd'] = read('jd-alignment')
data['coverage'] = read('jd-coverage')
data['videos'] = read('video-catalog')
data['cases'] = [read(f'case-{name}') for name in ('modernization', 'mcp', 'enterprise', 'evaluation')]
for case in data['cases']:
    folder = reference / 'case-code' / case['id'].removeprefix('case-')
    for file in case['files']:
        relative = Path(file['name'])
        assert not relative.is_absolute() and '..' not in relative.parts and '\\' not in file['name']
        assert (folder / relative).read_text() == file['code'], file['name']
assert len(data['jd']) == 8 and len({q['id'] for q in data['jd']}) == 8
data['client'].sort(key=lambda q: q['id'])
assert [q['id'] for q in data['client']] == [f'client-{i:02}' for i in range(1, 51)]
assert [d['n'] for d in new_days] == list(range(15, 31))
assert [d['day'] for d in data['lessons']] == list(range(1, 31))
assert [d['day'] for d in data['labs']] == list(range(1, 31))
assert len(data['answers']['baseline']) == 30 and len(data['answers']['final']) == 12
assert len(data['answers']['daily']) == len(data['answers']['design']) == 30
assert all(len(row) == 5 for row in data['answers']['daily'])
for n in range(15, 31):
    subject = f'client-day-{n}'
    queries = [q for q in data['client'] if q['day'] == n]
    refs = {s['url']: s for q in queries for s in q['sources']}
    video = read('advanced-resources')[str(n)]
    data['resources']['subjects'][subject] = {'videos': [video], 'references': list(refs.values())}
    data['resources']['days'][str(n)] = subject
assert all(str(n) in data['resources']['days'] for n in range(1, 31))
assert all(v['videos'] and v['references'] for v in data['resources']['subjects'].values())
data['resources']['verifiedOn'] = '2026-10-08'
data['scenarios'] = []
for part in ('python', 'frameworks', 'rag'):
    data['scenarios'].extend(read(f'scenarios-{part}'))
assert len(data['scenarios']) == 48 and len({s['id'] for s in data['scenarios']}) == 48
assert sum(bool(s['assignment']) for s in data['scenarios']) == 24
assert all(len(s['hints']) == 3 and len(s['questions']) >= 2 for s in data['scenarios'])
assert all(len(s['requirements']) >= 4 and len(s['acceptance']) >= 4 for s in data['scenarios'])
assert all(Path(f['name']).name == f['name'] and '/' not in f['name'] and '\\' not in f['name'] for s in data['scenarios'] if s['assignment'] for f in s['assignment']['files'])
# Extend days BEFORE old-backup normalization so day15..30 scores and selection survive reload/import.
course = '\n// COURSE_EXTENSION_BEGIN\nDAYS[13] = ' + safe_json(mid['day']) + ';\nDAYS.push(...' + safe_json(new_days) + ');\n// COURSE_EXTENSION_END\n'
text = text.replace('const BASELINE=[', course + 'const BASELINE=[', 1)
engines = ('offline-teacher.js', 'scenario-studio.js', 'simple-ui.js', 'cockpit.js', 'client-studio.js', 'jd-studio.js', 'practical-studio.js', 'video-studio.js')
engine = '\n'.join((reference / filename).read_text() for filename in engines)
bundle = '\n// OFFLINE_CONTENT_BEGIN\nconst OFFLINE = ' + safe_json(data) + ';\n' + engine + '\n// OFFLINE_CONTENT_END\n'
text = text.replace('</script>', bundle + '</script>', 1)
text = strip_block(text, '/* COCKPIT_THEME_BEGIN */', '/* COCKPIT_THEME_END */')
css = (reference / 'cockpit.css').read_text()
text = text.replace('</style>', '\n/* COCKPIT_THEME_BEGIN */\n' + css + '\n/* COCKPIT_THEME_END */\n</style>', 1)
html.write_text(text)
print(f'Bundled 30 days, {sum(len(d["modules"]) for d in data["lessons"])} modules, '
      f'{len(data["labs"])} labs, {len(data["client"])} client questions into {len(text.encode()):,}-byte standalone HTML.')
