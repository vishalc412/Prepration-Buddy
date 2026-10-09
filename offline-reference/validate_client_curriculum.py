"""Validate authored client content and new offline reference fixtures.

python3 offline-reference/validate_client_curriculum.py [--execute] [--html]
No package installation, browser storage access, cloud/model invocation or old
framework reference execution. --execute runs only Days 15–30 Python fixtures
in temporary workspaces. Static guards are not an operating-system sandbox.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
PRIMARY_HOSTS = {
    'arxiv.org', 'aws.amazon.com', 'docs.aws.amazon.com', 'developers.openai.com',
    'openai.com', 'cdn.openai.com', 'docs.python.org', 'faiss.ai', 'genai.owasp.org', 'huggingface.co',
    'neo4j.com', 'reference.langchain.com', 'www.iso.org', 'www.w3.org',
    'docs.langchain.com', 'langchain-ai.github.io', 'docs.pytorch.org', 'pytorch.org',
    'numpy.org', 'pandas.pydata.org', 'scikit-learn.org', 'docs.scipy.org',
    'docs.pydantic.dev', 'fastapi.tiangolo.com', 'learn.microsoft.com',
    'docs.oracle.com', 'docs.spring.io', 'docs.djangoproject.com', 'flask.palletsprojects.com',
    'github.com', 'www.nist.gov', 'nvlpubs.nist.gov', 'cloud.google.com',
    'modelcontextprotocol.io', 'docs.github.com', 'docs.openrewrite.org', 'dora.dev',
    'spring.io', 'csrc.nist.gov', 'kubernetes.io', 'opentelemetry.io', 'slsa.dev',
    'www.typescriptlang.org',
}
PRIMARY_GITHUB_REPOS = {
    ('state-spaces', 'mamba'), ('facebookresearch', 'faiss'), ('openai', 'tiktoken'),
    ('microsoft', 'BitNet'), ('openai', 'openai-python'), ('langchain-ai', 'langchain'), ('langchain-ai', 'langgraph'),
    ('huggingface', 'transformers'), ('huggingface', 'diffusers'),
    ('github', 'docs'),
}
BLOCKED_MODULES = {'socket', 'http', 'urllib', 'ssl', 'subprocess', 'multiprocessing',
                   'webbrowser', 'ftplib', 'smtplib', 'xmlrpc'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def words(value, minimum, label):
    require(isinstance(value, str) and len(value.split()) >= minimum,
            f'{label}: expected nonempty substantive text, minimum {minimum} words')


def read(name):
    path = ROOT / name
    require(path.is_file(), f'Missing authored shard: {name}')
    return json.loads(path.read_text())


def sources(rows, label):
    require(isinstance(rows, list) and len(rows) >= 1, f'{label}: source list required')
    for source in rows:
        require(isinstance(source, dict), f'{label}: source object required')
        words(source.get('title'), 2, f'{label} source title')
        parsed = urlparse(source.get('url', ''))
        require(parsed.scheme == 'https' and parsed.hostname in PRIMARY_HOSTS
                and not parsed.username and not parsed.password and parsed.port in (None, 443),
                f'{label}: unsupported primary-source URL {source.get("url")}')
        if parsed.hostname == 'github.com':
            repo = tuple(parsed.path.strip('/').split('/')[:2])
            require(repo in PRIMARY_GITHUB_REPOS, f'{label}: review GitHub primary provenance {repo}')


def quiz(check, label):
    require(isinstance(check, dict), f'{label}: quiz object required')
    words(check.get('question'), 3, f'{label} question')
    choices = check.get('options')
    require(isinstance(choices, list) and len(choices) == 3, f'{label}: exactly three options')
    require(all(isinstance(x, str) and x.strip() for x in choices), f'{label}: empty option')
    require(len(set(choices)) == 3, f'{label}: duplicate options')
    require(type(check.get('answer')) is int and 0 <= check['answer'] < 3,
            f'{label}: correct-answer index outside options')
    words(check.get('explanation'), 4, f'{label} explanation')


def validate_clients():
    groups = [read('client-foundations.json'), read('client-production.json')]
    require(all(isinstance(x, list) for x in groups), 'Client shards must be lists')
    require([len(x) for x in groups] == [15, 35], 'Client shard counts must be 15 and 35')
    rows = groups[0] + groups[1]
    expected = [f'client-{n:02}' for n in range(1, 51)]
    require([x.get('id') for x in rows] == expected, 'Exactly ordered client-01 through client-50 required')
    minimums = {'question': 3, 'plain': 25, 'mechanism': 55, 'answer': 70, 'example': 30}
    for row in rows:
        label = row['id']
        require(type(row.get('day')) is int and 15 <= row['day'] <= 30, f'{label}: invalid course day')
        words(row.get('topic'), 1, f'{label} topic')
        for key, minimum in minimums.items():
            words(row.get(key), minimum, f'{label} {key}')
        require(isinstance(row.get('pitfalls'), list) and len(row['pitfalls']) >= 3, f'{label}: three pitfalls required')
        require(isinstance(row.get('hints'), list) and len(row['hints']) == 3, f'{label}: three hints required')
        for key in ('pitfalls', 'hints'):
            for i, text in enumerate(row[key]):
                words(text, 2 if key == 'hints' else 3, f'{label} {key}[{i}]')
        require(isinstance(row.get('followups'), list) and len(row['followups']) >= 2, f'{label}: two followups required')
        for i, followup in enumerate(row['followups']):
            words(followup.get('question'), 4, f'{label} followup[{i}] question')
            words(followup.get('answer'), 10, f'{label} followup[{i}] answer')
        require(isinstance(row.get('checks'), list) and len(row['checks']) == 2, f'{label}: two quizzes required')
        for i, check in enumerate(row['checks']):
            quiz(check, f'{label} check[{i}]')
        sources(row.get('sources'), label)
    return rows


def validate_jd():
    rows = read('jd-alignment.json')
    require(isinstance(rows, list) and len(rows) == 8, 'Exactly eight revised JD drills required')
    ids = [row.get('id') for row in rows]
    require(all(isinstance(identifier, str) and re.fullmatch(r'jd-[a-z0-9-]+', identifier)
                for identifier in ids) and len(set(ids)) == 8, 'JD IDs must be unique nonempty jd-* identifiers')
    for row in rows:
        label = row['id']
        for field, minimum in [('title', 2), ('requirement', 8), ('explanation', 80),
                               ('answer', 55), ('scenario', 30), ('assignment', 30)]:
            words(row.get(field), minimum, f'{label} {field}')
        days = row.get('days')
        require(isinstance(days, list) and days
                and all(type(day) is int and 1 <= day <= 30 for day in days)
                and len(set(days)) == len(days),
                f'{label}: unique linked days within 1–30 required')
        for field in ('hints', 'checks'):
            require(isinstance(row.get(field), list) and len(row[field]) == 3,
                    f'{label}: exactly three {field} required')
            for i, text in enumerate(row[field]):
                words(text, 3, f'{label} {field}[{i}]')
        require(isinstance(row.get('followups'), list) and len(row['followups']) == 2,
                f'{label}: exactly two followups required')
        for i, followup in enumerate(row['followups']):
            require(isinstance(followup, dict), f'{label}: followup object required')
            words(followup.get('question'), 4, f'{label} followup[{i}] question')
            words(followup.get('answer'), 20, f'{label} followup[{i}] answer')
        sources(row.get('sources'), label)
    return rows


def safe_file(file, label):
    name = file.get('name', '')
    require(isinstance(name, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', name),
            f'{label}: unsafe fixture filename {name!r}')
    code = file.get('code')
    require(isinstance(code, str) and code.strip(), f'{label}: missing code')
    require(name.endswith('.py'), f'{label}: new references must be Python stdlib fixtures')
    tree = ast.parse(code, filename=name)
    for node in ast.walk(tree):
        modules = []
        if isinstance(node, ast.Import):
            modules = [entry.name.split('.')[0] for entry in node.names]
        elif isinstance(node, ast.ImportFrom):
            require(not node.level, f'{label}: relative fixture imports require review')
            modules = [(node.module or '').split('.')[0]]
        for module in modules:
            require(module in sys.stdlib_module_names and module not in BLOCKED_MODULES,
                    f'{label}: non-stdlib or network/process import {module}')
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                require(node.func.id not in {'eval', 'exec', '__import__'}, f'{label}: dynamic execution prohibited')
            if isinstance(node.func, ast.Attribute):
                require(node.func.attr not in {'system', 'popen', 'spawn', 'fork', 'urlopen'},
                        f'{label}: external execution/network call prohibited')
    return name, code


def validate_extensions(execute):
    shards = [read('extended-foundations.json'), read('extended-production.json')]
    combined = {key: [] for key in ('days', 'lessons', 'labs', 'daily', 'design')}
    receipts = []
    files = []
    for shard, numbers in zip(shards, (list(range(15, 21)), list(range(21, 31)))):
        require(isinstance(shard, dict), 'Extended shard must be object')
        for key in combined:
            require(isinstance(shard.get(key), list) and len(shard[key]) == len(numbers), f'{key}: day count mismatch')
            combined[key].extend(shard[key])
        require([d.get('n') for d in shard['days']] == numbers, 'Extended day IDs inconsistent')
        require([d.get('day') for d in shard['lessons']] == numbers, 'Extended lesson day IDs inconsistent')
        require([d.get('day') for d in shard['labs']] == numbers, 'Extended lab day IDs inconsistent')
    for row in combined['days']:
        for field in ('title', 'topics', 'deliverable', 'proficiency', 'design'):
            words(row.get(field), 2, f'Day {row["n"]} {field}')
        require(isinstance(row.get('lab'), list) and len(row['lab']) >= 3, f'Day {row["n"]}: lab tasks missing')
        require(isinstance(row.get('checks'), list) and len(row['checks']) >= 3, f'Day {row["n"]}: evidence checks missing')
        require(isinstance(row.get('questions'), list) and len(row['questions']) == 5, f'Day {row["n"]}: five questions needed')
    for row in combined['lessons']:
        require(isinstance(row.get('modules'), list) and len(row['modules']) == 5, f'Day {row["day"]}: five detailed modules required')
        for i, module in enumerate(row['modules']):
            label = f'Day {row["day"]} module {i+1}'
            for field, minimum in [('title', 2), ('explanation', 45), ('workedExample', 20), ('pitfall', 6), ('teachBack', 8)]:
                words(module.get(field), minimum, f'{label} {field}')
            require(isinstance(module.get('hints'), list) and len(module['hints']) == 3, f'{label}: three hints required')
            for hint in module['hints']:
                words(hint, 2, f'{label} hint')
            quiz(module.get('check'), label)
    for i, (daily, design) in enumerate(zip(combined['daily'], combined['design']), 15):
        require(isinstance(daily, list) and len(daily) == 5, f'Day {i}: five daily answers required')
        for answer in daily:
            words(answer, 35, f'Day {i} daily answer')
        words(design, 70, f'Day {i} design answer')
    for lab in combined['labs']:
        label = f'Day {lab["day"]} lab'
        words(lab.get('explanation'), 50, f'{label} explanation')
        words(lab.get('limits'), 20, f'{label} limits')
        for field in ('steps', 'checks', 'pitfalls'):
            require(isinstance(lab.get(field), list) and len(lab[field]) >= 3, f'{label}: {field} missing')
        require(isinstance(lab.get('files'), list) and lab['files'], f'{label}: fixture files missing')
        checked = [safe_file(file, label) for file in lab['files']]
        files.extend(name for name, _ in checked)
        if execute:
            with tempfile.TemporaryDirectory(prefix=f'client-day{lab["day"]}-qa-') as folder:
                work = Path(folder)
                for name, code in checked:
                    (work / name).write_text(code)
                for name, code in checked:
                    result = subprocess.run([sys.executable, '-I', name], cwd=work,
                                            capture_output=True, text=True, timeout=25)
                    receipt = {'day': lab['day'], 'file': name,
                               'sha256': hashlib.sha256(code.encode()).hexdigest(),
                               'exit_code': result.returncode,
                               'stdout_tail': result.stdout[-3000:], 'stderr_tail': result.stderr[-1500:]}
                    receipts.append(receipt)
                    require(result.returncode == 0, f'{label} execution failed: {receipt}')
    require(len(set(files)) == len(files), 'New reference filenames must be unique')
    return combined, receipts, files


def audit(execute=False, html=False):
    client = validate_clients()
    jd = validate_jd()
    midcourse = read('midcourse.json')
    require(midcourse.get('day', {}).get('n') == 14 and midcourse.get('lesson', {}).get('day') == 14, 'Midcourse must be Day 14')
    require(len(midcourse['lesson'].get('modules', [])) == 5, 'Day 14 requires five authored modules')
    for i, module in enumerate(midcourse['lesson']['modules']):
        words(module.get('explanation'), 45, f'Day 14 module {i+1} explanation')
        quiz(module.get('check'), f'Day 14 module {i+1}')
    extended, receipts, files = validate_extensions(execute)
    teacher = (ROOT / 'offline-teacher.js').read_text()
    block_text = re.search(r'const STUDY_BLOCKS=(\[[^;]+\]);', teacher)
    require(block_text is not None, 'Teaching blocks missing')
    minutes = [int(n) for n in re.findall(r',\s*(\d+)\]', block_text.group(1))]
    require(len(minutes) == 6 and sum(minutes) == 240, f'Teaching blocks must sum to 240: {minutes}')
    report = {'status': 'PASS', 'client_questions': len(client), 'client_checks': sum(len(x['checks']) for x in client),
              'jd_drills': len(jd), 'jd_followups': sum(len(x['followups']) for x in jd),
              'client_followups': sum(len(x['followups']) for x in client), 'extended_days': len(extended['days']),
              'extended_modules': sum(len(d['modules']) for d in extended['lessons']),
              'extended_labs': len(extended['labs']), 'daily_minutes': sum(minutes),
              'reference_files': files, 'executed_fixtures': len(receipts), 'execution': receipts,
              'limits': ['Length/schema checks do not prove factual accuracy or teaching effectiveness.',
                         'Primary-domain allowlist checks provenance shape, not page availability.',
                         'Only new Days 15–30 fixtures execute; no unchanged framework suites run.',
                         'Static AST guards and temporary cwd do not constitute an OS security sandbox.']}
    if html:
        text = (ROOT.parent / 'index.html').read_text()
        require('const OFFLINE = ' in text, 'Embedded OFFLINE object missing')
        embedded, _ = json.JSONDecoder().raw_decode(text.split('const OFFLINE = ', 1)[1])
        extension = re.search(r'// COURSE_EXTENSION_BEGIN([\s\S]*?)// COURSE_EXTENSION_END', text)
        require(extension is not None, 'Embedded authored day extension marker missing')
        mid_marker = re.search(r'DAYS\[13\]\s*=\s*', extension.group(1))
        days_marker = re.search(r'DAYS\.push\(\.\.\.\s*', extension.group(1))
        require(mid_marker is not None and days_marker is not None, 'Authored day insertion markers missing')
        authored_mid, _ = json.JSONDecoder().raw_decode(extension.group(1)[mid_marker.end():])
        authored_days, _ = json.JSONDecoder().raw_decode(extension.group(1)[days_marker.end():])
        require(authored_mid == midcourse['day'], 'Embedded midcourse day differs from source')
        require(authored_days == extended['days'], 'Embedded Days 15–30 differ from source shards')
        require(embedded.get('client') == client, 'Embedded client data differs from source shards')
        require(embedded.get('jd') == jd, 'Embedded JD data differs from authored shard')
        for key in ('lessons', 'labs'):
            require([d for d in embedded[key] if d['day'] >= 15] == extended[key], f'Embedded new {key} differ')
        require([d['day'] for d in embedded['lessons']] == list(range(1, 31)), 'Expected 30 ordered day lesson records')
        require(embedded['lessons'][13] == midcourse['lesson'], 'Embedded midcourse lesson differs')
        require([d['day'] for d in embedded['labs']] == list(range(1, 31)), 'Expected 30 ordered lab solutions')
        require(len(embedded['answers']['daily']) == len(embedded['answers']['design']) == 30,
                'Expected 30 daily answer/design sets')
        for key in ('daily', 'design'):
            require(embedded['answers'][key][14:] == extended[key], f'Embedded new {key} answers differ')
        require((ROOT / 'client-studio.js').read_text().strip() in text, 'Embedded client teacher differs')
        require((ROOT / 'jd-studio.js').read_text().strip() in text, 'Embedded revised JD teacher differs')
        require(not re.search(r'\b(?:fetch|WebSocket|EventSource)\s*\(|XMLHttpRequest|<script[^>]*\bsrc\s*=', text),
                'Required external browser execution path detected')
        report['embedded_parity'] = 'PASS'
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--html', action='store_true', help='Check finalized single-file embed parity')
    args = parser.parse_args()
    try:
        print(json.dumps(audit(args.execute, args.html), indent=2))
    except (ValueError, SyntaxError, subprocess.TimeoutExpired) as error:
        print(json.dumps({'status': 'FAIL', 'error': str(error)}, indent=2))
        raise SystemExit(1)
