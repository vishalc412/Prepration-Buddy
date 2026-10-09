"""Independent practical-case checks; --execute runs four disposable local harnesses.

Framework execution requires a prepared Python environment, JDK and offline Maven
cache. No packages are installed. Enterprise HTTP is loopback-only. Temporary
directories and AST guards are not an OS security sandbox. Learner storage is not
read or written. Outputs are reviewer receipts, not learner or production results.
"""
from __future__ import annotations
import argparse
import ast
import base64
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
from urllib.parse import urlparse
import zipfile

ROOT = Path(__file__).resolve().parent
ORDER = ['modernization', 'mcp', 'enterprise', 'evaluation']
PRIMARY_HOSTS = {
    'modelcontextprotocol.io', 'docs.python.org', 'docs.oracle.com', 'openjdk.org',
    'docs.spring.io', 'spring.io', 'fastapi.tiangolo.com', 'docs.pydantic.dev',
    'www.uvicorn.org', 'maven.apache.org', 'docs.openrewrite.org', 'openrewrite.org',
    'developers.openai.com', 'dora.dev', 'opentelemetry.io', 'docs.github.com',
    'csrc.nist.gov', 'www.nist.gov', 'genai.owasp.org', 'slsa.dev', 'kubernetes.io',
    'docs.docker.com', 'docs.aws.amazon.com', 'aws.amazon.com', 'learn.microsoft.com',
    'git-scm.com', 'www.sqlite.org', 'sqlite.org',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(name):
    return json.loads((ROOT / name).read_text())


def prose(value, minimum, label):
    require(isinstance(value, str) and len(value.split()) >= minimum,
            f'{label}: expected at least {minimum} words')


def safe_name(name):
    require(isinstance(name, str) and 0 < len(name) <= 240
            and not any(c in name for c in ('\\', ':', '\x00', '\r', '\n')),
            f'Unsafe file/ZIP name {name!r}')
    parts = name.split('/')
    require(not name.startswith('/') and all(re.fullmatch(r'[A-Za-z0-9_.-]+', p)
            and p not in ('.', '..') for p in parts), f'Unsafe file/ZIP path {name!r}')
    require(PurePosixPath(name).as_posix() == name, f'Noncanonical ZIP path {name!r}')


def py_guard(code, name):
    tree = ast.parse(code, filename=name)
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name.split('.')[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            require(not node.level, f'{name}: relative imports need independent review')
            names = [(node.module or '').split('.')[0]]
        for module in names:
            require(module in sys.stdlib_module_names | {'fastapi', 'pydantic', 'uvicorn'},
                    f'{name}: unreviewed third-party import {module}')
        if isinstance(node, ast.Call):
            require(not (isinstance(node.func, ast.Name) and node.func.id in {'eval', 'exec', '__import__'}),
                    f'{name}: dynamic execution needs review')
            require(not any(k.arg == 'shell' and isinstance(k.value, ast.Constant)
                            and k.value.value is True for k in node.keywords),
                    f'{name}: shell command execution prohibited')


def cases():
    rows = [read(f'case-{name}.json') for name in ORDER]
    require([r.get('id') for r in rows] == [f'case-{name}' for name in ORDER], 'Exactly four ordered practical cases required')
    fingerprints = {}
    for row, folder in zip(rows, ORDER):
        label = row['id']
        for field, floor in [('title', 5), ('context', 60), ('architecture', 20), ('answer', 70)]:
            prose(row.get(field), floor, f'{label} {field}')
        days = row.get('days')
        require(isinstance(days, list) and days and all(type(n) is int and 1 <= n <= 30 for n in days)
                and len(set(days)) == len(days), f'{label}: unique linked days within course required')
        for field, count in [('requirements', 3), ('acceptance', 5), ('hints', 3), ('limits', 3), ('run', 1)]:
            require(isinstance(row.get(field), list) and len(row[field]) >= count, f'{label}: {field} missing')
            for text in row[field]:
                prose(text, 2, f'{label} {field}')
        require(len(row['hints']) == 3, f'{label}: exactly three hints required')
        require(isinstance(row.get('walkthrough'), list) and len(row['walkthrough']) >= 4, f'{label}: four walkthrough stages required')
        for stage in row['walkthrough']:
            prose(stage.get('title'), 3, f'{label} stage title')
            prose(stage.get('body'), 45, f'{label} stage explanation')
        assignment = row.get('assignment', {})
        prose(assignment.get('objective'), 20, f'{label} assignment objective')
        require(isinstance(assignment.get('steps'), list) and len(assignment['steps']) >= 3, f'{label}: assignment sessions required')
        for step in assignment['steps']:
            prose(step, 10, f'{label} assignment session')
        require(isinstance(row.get('followups'), list) and len(row['followups']) >= 2, f'{label}: followups missing')
        for followup in row['followups']:
            prose(followup.get('question'), 4, f'{label} followup question')
            prose(followup.get('answer'), 25, f'{label} followup answer')
        require(isinstance(row.get('sources'), list) and row['sources'], f'{label}: primary sources required')
        for source in row['sources']:
            prose(source.get('title'), 2, f'{label} source title')
            url = urlparse(source.get('url', ''))
            require(url.scheme == 'https' and url.hostname in PRIMARY_HOSTS and not url.username
                    and not url.password and url.port in (None, 443), f'{label}: primary source provenance needs review: {source}')
        require(isinstance(row.get('files'), list) and row['files'], f'{label}: downloadable source files required')
        names = []
        for file in row['files']:
            name, code = file.get('name'), file.get('code')
            safe_name(name)
            safe_name(label + '/' + name)
            require(isinstance(code, str) and code.strip(), f'{label}/{name}: source missing')
            require(isinstance(file.get('language'), str) and file['language'], f'{label}/{name}: language missing')
            require(name not in names, f'{label}: duplicate downloadable name {name}')
            names.append(name)
            source = ROOT / 'case-code' / folder / name
            require(source.is_file() and not source.is_symlink(), f'{label}/{name}: actual source file missing or symlink')
            require(source.read_text() == code, f'{label}/{name}: embedded source differs from actual file')
            fingerprints[label + '/' + name] = hashlib.sha256(code.encode()).hexdigest()
            if name.endswith('.py'):
                py_guard(code, name)
        inventory = {p.relative_to(ROOT / 'case-code' / folder).as_posix()
                     for p in (ROOT / 'case-code' / folder).rglob('*') if p.is_file()
                     and not {'target', '__pycache__'}.intersection(p.relative_to(ROOT / 'case-code' / folder).parts)
                     and not p.name.endswith('.pyc') and p.name != 'classpath.txt'}
        require(set(names) == inventory, f'{label}: source/download inventory mismatch: {set(names)^inventory}')
    return rows, fingerprints


def coverage(rows):
    data = read('jd-coverage.json')
    expected = {'requirements': 45, 'modernizationPatterns': 15, 'mlClusters': 22, 'platformScope': 72}
    jd_ids = {r['id'] for r in read('jd-alignment.json')}
    scenario_ids = {r['id'] for name in ['scenarios-python.json', 'scenarios-frameworks.json', 'scenarios-rag.json'] for r in read(name)}
    lab_names = {f['name'] for name in ['labs.json', 'extended-foundations.json', 'extended-production.json']
                 for row in (read(name) if name == 'labs.json' else read(name)['labs']) for f in row['files']}
    client_ids = {r['id'] for name in ['client-foundations.json', 'client-production.json'] for r in read(name)}
    case_ids = {r['id'] for r in rows}
    seen = set()
    for group, count in expected.items():
        require(isinstance(data.get(group), list) and len(data[group]) == count, f'{group}: expected {count} mapped entries')
        for row in data[group]:
            identifier = row.get('id')
            require(isinstance(identifier, str) and identifier and identifier not in seen, 'Coverage IDs missing or duplicated')
            seen.add(identifier)
            prose(row.get('requirement'), 1, identifier)
            require(row.get('status') in data['statuses'], f'{identifier}: unsupported coverage status')
            require(isinstance(row.get('days'), list) and (row['days'] or row['status'] == 'credential/experience')
                    and all(type(n) is int and 1 <= n <= 30 for n in row['days']), f'{identifier}: linked days missing')
            for field, allowed in [('lessonIds', jd_ids), ('scenarioIds', scenario_ids), ('labFiles', lab_names),
                                   ('clientQuestionIds', client_ids), ('caseIds', case_ids)]:
                require(isinstance(row.get(field), list) and set(row[field]) <= allowed, f'{identifier}: unresolved {field} {row.get(field)}')
            for field in ('evidence', 'limits', 'nextAction'):
                prose(row.get(field), 5, f'{identifier} {field}')
    require(len(data.get('gapGrid', [])) == 17, '17 honest gap rows required')
    for row in data['gapGrid']:
        require(set(row.get('coverageIds', [])) <= seen and row.get('coverageIds'), 'Gap-grid coverage reference missing')
        require(set(row.get('lessonIds', [])) <= jd_ids, 'Gap-grid lesson reference missing')
        require(row.get('status') in data['statuses'], 'Gap-grid unknown status')
    require({r['id'] for r in data.get('cases', [])} == case_ids, 'Coverage case catalog differs from actual cases')
    return data


def execute(rows, enterprise_python):
    commands = {'modernization': [sys.executable, '-I', 'modernization_case.py', '--self-test'],
                'mcp': [sys.executable, '-I', 'client.py'],
                'enterprise': [enterprise_python, 'integration_test.py', '--offline-maven'],
                'evaluation': [sys.executable, '-I', 'evaluate.py']}
    require(Path(enterprise_python).is_file(), 'Prepared enterprise Python interpreter required; validator does not install packages')
    receipts = []
    for name, row in zip(ORDER, rows):
        with tempfile.TemporaryDirectory(prefix=f'practical-{name}-review-') as temp:
            work = Path(temp)
            for file in row['files']:
                target = work / file['name']
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(file['code'])
            env = dict(os.environ)
            for option in ('JAVA_TOOL_OPTIONS', 'JDK_JAVA_OPTIONS', 'JDK_JAVAC_OPTIONS', 'CLASSPATH',
                           'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy'):
                env.pop(option, None)
            env['NO_PROXY'] = '127.0.0.1,localhost'
            result = subprocess.run(commands[name], cwd=work, env=env, capture_output=True, text=True, timeout=300)
            receipt = {'case': row['id'], 'command': commands[name], 'exit_code': result.returncode,
                       'stdout_tail': result.stdout[-5000:], 'stderr_tail': result.stderr[-3000:],
                       'execution_boundary': 'independent reviewer; disposable local fixture, not learner work'}
            receipts.append(receipt)
            require(result.returncode == 0 and ('PASS' in result.stdout or 'OK' in result.stderr), f'{row["id"]}: execution failed {receipt}')
    return receipts


def zip_roundtrip(rows):
    # Run the exact bounded browser ZIP function in Node, then inspect bytes with
    # Python's independent ZIP reader. No extraction, browser or learner state.
    runtime = (ROOT / 'practical-studio.js').read_text()
    match = re.search(r'(function practicalZip\(files\)[\s\S]+?)\nfunction practicalDownload', runtime)
    require(match is not None, 'ZIP writer boundary missing')
    script = match.group(1) + "\n(async()=>{const fs=require('node:fs');const files=JSON.parse(fs.readFileSync(0,'utf8'));const archive=practicalZip(files);process.stdout.write(Buffer.from(await archive.arrayBuffer()).toString('base64'))})().catch(e=>{process.stderr.write(String(e));process.exit(1)});"
    receipts = []
    for row in rows:
        result = subprocess.run(['node', '-e', script], input=json.dumps(row['files']),
                                capture_output=True, text=True, timeout=10, check=True)
        raw = base64.b64decode(result.stdout, validate=True)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            require(archive.testzip() is None, f'{row["id"]}: ZIP checksum failure')
            require(archive.namelist() == [f['name'] for f in row['files']], f'{row["id"]}: ZIP file list differs')
            for file in row['files']:
                safe_name(file['name'])
                require(archive.read(file['name']) == file['code'].encode(), f'{row["id"]}: ZIP bytes differ for {file["name"]}')
        receipts.append({'case': row['id'], 'files': len(row['files']), 'bytes': len(raw),
                         'status': 'PASS', 'boundary': 'exact JavaScript writer, independent Python ZIP reader'})
    return receipts


def audit(run=False, html=False, enterprise_python='/private/tmp/enterprise-case-validation/bin/python', zip_check=False):
    rows, fingerprints = cases()
    mapped = coverage(rows)
    report = {'status': 'PASS', 'case_count': len(rows), 'coverage_entries': 154, 'gap_rows': 17,
              'source_files': len(fingerprints), 'fingerprints': fingerprints, 'execution': [],
              'limits': ['Author/reviewer execution does not mark learner work complete.',
                         'Coverage links and length checks do not prove professional proficiency.',
                         'Actual framework packages/JDK/offline Maven cache are prepared prerequisites.',
                         'Local prototype tests do not certify production, OAuth or current MCP interoperability.']}
    if html:
        text = (ROOT.parent / 'index.html').read_text()
        embedded, _ = json.JSONDecoder().raw_decode(text.split('const OFFLINE = ', 1)[1])
        require(embedded.get('cases') == rows, 'Case payload differs from HTML')
        require(embedded.get('coverage') == mapped, 'Coverage payload differs from HTML')
        require((ROOT / 'practical-studio.js').read_text().strip() in text, 'Practical runtime source differs from HTML')
        report['embedded_parity'] = 'PASS'
        report['artifact_sha256'] = hashlib.sha256(text.encode()).hexdigest()
        report['artifact_bytes'] = len(text.encode())
    if run:
        report['execution'] = execute(rows, enterprise_python)
    if zip_check:
        report['zip_roundtrip'] = zip_roundtrip(rows)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--html', action='store_true')
    parser.add_argument('--zip', action='store_true', help='Execute browser ZIP writer in Node and inspect with Python')
    parser.add_argument('--enterprise-python', default='/private/tmp/enterprise-case-validation/bin/python')
    args = parser.parse_args()
    try:
        print(json.dumps(audit(args.execute, args.html, args.enterprise_python, args.zip), indent=2))
    except (ValueError, SyntaxError, KeyError, OSError, subprocess.TimeoutExpired, subprocess.CalledProcessError, zipfile.BadZipFile) as error:
        print(json.dumps({'status': 'FAIL', 'error': str(error)}, indent=2))
        raise SystemExit(1)
