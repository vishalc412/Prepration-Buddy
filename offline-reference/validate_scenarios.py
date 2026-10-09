"""Audit scenario coverage/parity and execute local reference entrypoints.

Usage: python validate_scenarios.py [--execute --runtime /absolute/python]
No dependency installation, cloud access, provider calls or browser storage writes.
"""
import argparse
import ast
import importlib.metadata
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TRACKS = {'Python': 'python', 'Async Python': 'python', 'FastAPI': 'frameworks',
          'Django': 'frameworks', 'Flask': 'frameworks', 'RAG': 'rag',
          'Agents': 'rag', 'Evaluation': 'rag'}

def audit(execute=False, runtime='python3'):
    scenarios = []
    for shard in ('python', 'frameworks', 'rag'):
        rows = json.loads((ROOT / f'scenarios-{shard}.json').read_text())
        assert isinstance(rows, list)
        scenarios.extend(rows)
    assert len(scenarios) == len({s['id'] for s in scenarios}) == 48
    report = {'status': 'PASS', 'scenarios': 48,
              'questions': sum(len(s['questions']) for s in scenarios),
              'assignments': sum(bool(s['assignment']) for s in scenarios),
              'tracks': {}, 'execution': [], 'reference_files': []}
    assert report['questions'] == 96 and report['assignments'] == 24
    for track in TRACKS:
        rows = [s for s in scenarios if s['track'] == track]
        assert len(rows) == 6 and sum(bool(s['assignment']) for s in rows) == 3, track
        report['tracks'][track] = {'scenarios': 6, 'assignments': 3}
    for s in scenarios:
        assert re.fullmatch(r'[a-z]+-\d{2}', s['id']), s['id']
        assert s['level'] in {'Foundation', 'Applied', 'Principal'}
        assert 90 <= s['minutes'] <= 180
        assert len(s['hints']) == 3 and len(s['requirements']) >= 4 and len(s['acceptance']) >= 4
        assert len(s['questions']) == 2
        for q in s['questions']:
            assert len(q['checks']) >= 3 and len(q['answer'].split()) >= 80, s['id']
        assert len(s['solution'].split()) >= 90, s['id']
        for source in s.get('sources', []):
            assert source['url'].startswith('https://'), source
        a = s['assignment']
        if not a:
            continue
        assert len(a['steps']) >= 4 and a['run'] and a['files'] and a['limits']
        folder = ROOT / 'scenario-code' / TRACKS[s['track']]
        for f in a['files']:
            assert Path(f['name']).name == f['name'] and '/' not in f['name'] and '\\' not in f['name']
            assert (folder / f['name']).read_text() == f['code'], f['name']
            if f['name'].endswith('.py'):
                ast.parse(f['code'], filename=f['name'])
            report['reference_files'].append(f['name'])
        # Execute only a Python script listed in the authored run instructions.
        candidates = [f for f in a['files'] if f['name'].endswith('.py') and
                      any(re.search(r'\bpython(?:3)?\s+' + re.escape(f['name']) + r'(?:\s|$)', cmd)
                          for cmd in a['run'])]
        assert candidates, ('No executable entrypoint', s['id'])
        if execute:
            for f in candidates:
                result = subprocess.run([runtime, f['name']], cwd=folder,
                                        capture_output=True, text=True, timeout=30)
                receipt = {'scenario': s['id'], 'file': f['name'], 'exit_code': result.returncode,
                           'stdout': result.stdout[-4000:], 'stderr': result.stderr[-4000:]}
                report['execution'].append(receipt)
                assert result.returncode == 0, receipt
    report['unique_reference_files'] = len(set(report['reference_files']))
    return report

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--execute', action='store_true')
    p.add_argument('--runtime', default='python3')
    p.add_argument('--report', type=Path)
    args = p.parse_args()
    report = audit(args.execute, args.runtime)
    text = json.dumps(report, indent=2)
    if args.report:
        args.report.write_text(text + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in {'execution', 'reference_files'}}))
    print(f"Executed {len(report['execution'])} reference entrypoints.")
