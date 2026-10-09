"""Offline bounded modernization lab. Only owned temporary Java fixtures are writable.

This is not a Java parser, a general code transformer, an OS sandbox, or a real
identity provider. The credential authority and replay ledger are process-local.
"""
from __future__ import annotations

import argparse
import copy
import difflib
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
TARGET = 'PricePolicy.java'
BEFORE_SHA = '80fac5c4f2cbdbb53262bd25f2fbdd95b451cf475889d7254cc6c06d5b0ead02'
AFTER_SHA = '6fe0938b694cb986d68ee5e0801ee99c519dff75e16ac229d99660823b2318e0'
SOURCE_NAMES = {'PricePolicy.java', 'InvoiceService.java', 'ReceiptApi.java', 'BehaviorProbe.java'}
MAX_FILES = 8
MAX_FILE_BYTES = 32_768
MAX_TOTAL_BYTES = 131_072
RECIPE = 'remove-local-immediate-Integer-box-v1'

class BoundaryFailure(ValueError):
    pass

class ApprovalFailure(ValueError):
    pass

class StalePreview(ValueError):
    pass

class UnsupportedRecipe(ValueError):
    pass

class GateFailure(RuntimeError):
    pass

def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()

def digest(data):
    return hashlib.sha256(data).hexdigest()

def json_copy(value):
    return json.loads(encoded(value))

def templates(version='before'):
    folder = HERE / 'fixtures' / version
    data = {name: (folder / name).read_bytes() for name in sorted(SOURCE_NAMES)}
    expected = BEFORE_SHA if version == 'before' else AFTER_SHA
    if digest(data[TARGET]) != expected:
        raise UnsupportedRecipe('the bundled target template no longer matches the audited recipe')
    return data

def lexical_graph(data):
    """Conservative local class-reference candidates, not resolved Java calls."""
    sources = {name: raw.decode('utf-8') for name, raw in data.items() if name.endswith('.java')}
    cleaned = {}
    owners = {}
    literal = re.compile(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', re.S)
    for name, source in sources.items():
        clean = literal.sub(' ', source)
        declarations = re.findall(r'\bclass\s+([A-Za-z_][A-Za-z_0-9]*)', clean)
        if len(declarations) != 1 or declarations[0] + '.java' != name:
            raise BoundaryFailure('one matching top-level fixture class per Java file required')
        owners[declarations[0]] = name
        cleaned[name] = clean
    dependencies = {}
    for symbol, name in sorted(owners.items()):
        names = set(re.findall(r'\b[A-Z][A-Za-z_0-9]*\b', cleaned[name]))
        dependencies[symbol] = sorted((names & owners.keys()) - {symbol})
    return {'owners': owners, 'dependencies': dependencies,
            'coverage': 'Lexical local-class reference candidates only; no method resolution.',
            'gaps': ['reflection', 'dynamic dispatch', 'build plugins', 'external dependencies', 'cross-language edges']}

def blast_radius(graph, changed='PricePolicy'):
    dependencies = graph['dependencies']
    if changed not in dependencies:
        raise BoundaryFailure('changed symbol absent from fixture graph')
    distances = {changed: 0}
    queue = [changed]
    while queue:
        symbol = queue.pop(0)
        for caller, refs in sorted(dependencies.items()):
            if symbol in refs and caller not in distances:
                distances[caller] = distances[symbol] + 1
                queue.append(caller)
    return [{'symbol': name, 'distance': distance} for name, distance in sorted(distances.items(), key=lambda x: (x[1], x[0])) if name != changed]

class Accelerator:
    """Creates its own sandbox; deliberately accepts no repository path argument."""
    def __init__(self):
        self._temporary = tempfile.TemporaryDirectory(prefix='java-modernization-fixture-')
        self.work = Path(self._temporary.name).resolve()
        self._root = self.work / 'fixture'
        self._root.mkdir()
        self.artifacts = self.work / 'artifacts'
        self.artifacts.mkdir()
        self._root_id = secrets.token_hex(16)
        self._key = secrets.token_bytes(32)
        # A fixture-only credential resolved independently of approval.actor.
        # This readable demo token is not a production authentication system.
        self._credentials = {'reviewer-demo-token': 'fixture-reviewer'}
        self._allowed_actors = {'fixture-reviewer'}
        self._previews = {}
        self._applied = {}
        for name, content in templates().items():
            (self._root / name).write_bytes(content)
        (self._root / '.fixture-owner.json').write_bytes(encoded({'root_id': self._root_id}))

    def __enter__(self):
        return self

    def __exit__(self, *ignored):
        self._temporary.cleanup()

    @property
    def fixture_root(self):
        return self._root

    def snapshot(self):
        if self._root.is_symlink() or self._root.resolve() != self.work / 'fixture':
            raise BoundaryFailure('only the program-owned disposable fixture root is permitted')
        data = {}
        for path in sorted(self._root.iterdir()):
            if path.is_symlink() or not path.is_file() or path.stat().st_nlink != 1:
                raise BoundaryFailure('symlinks, hard links and nested directories are unsupported')
            if path.name not in SOURCE_NAMES | {'.fixture-owner.json'}:
                raise BoundaryFailure('unexpected fixture file')
            size = path.stat().st_size
            if size > MAX_FILE_BYTES:
                raise BoundaryFailure('fixture file exceeds byte limit')
            data[path.name] = path.read_bytes()
        if len(data) > MAX_FILES or sum(map(len, data.values())) > MAX_TOTAL_BYTES:
            raise BoundaryFailure('fixture inventory exceeds bound')
        if set(data) != SOURCE_NAMES | {'.fixture-owner.json'}:
            raise BoundaryFailure('fixture files are incomplete')
        if data['.fixture-owner.json'] != encoded({'root_id': self._root_id}):
            raise BoundaryFailure('fixture ownership marker mismatch')
        manifest = [{'path': name, 'bytes': len(raw), 'sha256': digest(raw)} for name, raw in sorted(data.items())]
        return data, manifest, digest(encoded(manifest))

    def artifact(self, name, value):
        if not re.fullmatch(r'[a-z][a-z0-9-]*\.(json|patch)', name):
            raise BoundaryFailure('invalid artifact name')
        raw = value.encode() if isinstance(value, str) else encoded(value)
        (self.artifacts / name).write_bytes(raw)

    def materialize(self, label, data):
        folder = Path(tempfile.mkdtemp(prefix=label+'-', dir=self.work))
        for name in sorted(SOURCE_NAMES):
            (folder / name).write_bytes(data[name])
        return folder

    def java_gate(self, source_dir, label):
        javac = shutil.which('javac')
        java = shutil.which('java')
        if not javac or not java:
            raise GateFailure('installed JDK with javac and java required; no automatic installation')
        build = Path(tempfile.mkdtemp(prefix=label+'-classes-', dir=self.work))
        env = os.environ.copy()
        for option in ('JAVA_TOOL_OPTIONS', 'JDK_JAVA_OPTIONS', 'JDK_JAVAC_OPTIONS', 'CLASSPATH'):
            env.pop(option, None)
        compile_command = [javac, '--release', '17', '-encoding', 'UTF-8', '-proc:none', '-d', str(build)]
        compile_command.extend(str(source_dir/name) for name in sorted(SOURCE_NAMES))
        commands = [compile_command, [java, '-Xmx64m', '-ea', '-cp', str(build), 'BehaviorProbe']]
        receipts = []
        for command in commands:
            try:
                completed = subprocess.run(command, capture_output=True, text=True, timeout=20, env=env, shell=False)
            except subprocess.TimeoutExpired as exc:
                raise GateFailure('compiler or behavior process exceeded 20-second bound') from exc
            receipt = {'command': command, 'returncode': completed.returncode,
                       'stdout': completed.stdout, 'stderr': completed.stderr}
            receipts.append(receipt)
            if completed.returncode != 0:
                raise GateFailure(json.dumps(receipt))
        try:
            outcome = json.loads(receipts[-1]['stdout'])
        except json.JSONDecodeError as exc:
            raise GateFailure('Java behavior probe did not produce its expected JSON receipt') from exc
        if outcome != {'status':'PASS', 'checks':43, 'receiptA':'tenant-a:3750', 'maxTotal':10_000_000_000}:
            raise GateFailure('unexpected behavior signature or missing asserted cases')
        return {'phase': label, 'commands': receipts, 'outcome': outcome}

    def dry_run(self):
        data, manifest, input_hash = self.snapshot()
        target_hash = digest(data[TARGET])
        if target_hash not in {BEFORE_SHA, AFTER_SHA}:
            raise UnsupportedRecipe('only the exact audited PricePolicy fixture is supported; no fuzzy rewrite')
        graph = lexical_graph(data)
        replacement = templates('after')[TARGET]
        candidate = dict(data)
        candidate[TARGET] = replacement
        changes = [] if data[TARGET] == replacement else [{'path': TARGET, 'before_sha256': target_hash,
                   'after_sha256': digest(replacement), 'after_text': replacement.decode('utf-8')}]
        patch = ''.join(difflib.unified_diff(data[TARGET].decode().splitlines(True), replacement.decode().splitlines(True),
                                            fromfile='a/'+TARGET, tofile='b/'+TARGET))
        before = self.java_gate(self.materialize('before', data), 'before')
        after = self.java_gate(self.materialize('candidate', candidate), 'candidate')
        if before['outcome'] != after['outcome']:
            raise GateFailure('observed before/after behavior differs')
        if self.snapshot()[2] != input_hash:
            raise StalePreview('fixture changed while producing preview')
        body = {'root_id': self._root_id, 'recipe': RECIPE, 'input_hash': input_hash,
                'input_manifest': manifest, 'patch': patch, 'patch_sha256': digest(patch.encode()),
                'changes': changes, 'inventory': manifest, 'graph': graph,
                'blast_radius': blast_radius(graph), 'validation': {'before':before,'candidate':after,'parity':True}}
        preview = {'preview_id': digest(encoded(body)), 'body': body}
        self._previews[preview['preview_id']] = json_copy(preview)
        self.artifact('inventory.json', manifest)
        self.artifact('graph.json', graph)
        self.artifact('preview.json', preview)
        self.artifact('preview.patch', patch)
        self.artifact('validation.json', body['validation'])
        return json_copy(preview)

    def known_preview(self, preview):
        try:
            identifier, body = preview['preview_id'], preview['body']
            valid = digest(encoded(body)) == identifier and self._previews.get(identifier) == preview
        except (KeyError, TypeError, ValueError) as exc:
            raise ApprovalFailure('malformed preview') from exc
        if not valid or body.get('root_id') != self._root_id:
            raise ApprovalFailure('preview is modified, unknown or from another fixture')
        return body

    def approve(self, preview, credential):
        body = self.known_preview(preview)
        if not isinstance(credential, str):
            raise ApprovalFailure('fixture credential must be text')
        actor = self._credentials.get(credential)
        if actor not in self._allowed_actors:
            raise ApprovalFailure('credential did not resolve to a permitted trusted fixture reviewer')
        if self.snapshot()[2] != body['input_hash']:
            raise StalePreview('review cannot approve a stale input snapshot')
        payload = {'actor': actor, 'root_id': self._root_id, 'preview_id': preview['preview_id'],
                   'input_hash':body['input_hash'], 'patch_sha256':body['patch_sha256']}
        approval = {'payload':payload, 'signature':hmac.new(self._key, encoded(payload), hashlib.sha256).hexdigest()}
        self.artifact('approval.json', approval)
        return json_copy(approval)

    def verify_approval(self, preview, approval):
        body = self.known_preview(preview)
        try:
            payload, signature = approval['payload'], approval['signature']
            if not isinstance(payload, dict) or set(payload) != {'actor','root_id','preview_id','input_hash','patch_sha256'}:
                raise ApprovalFailure('approval payload schema mismatch')
            if any(not isinstance(value, str) for value in payload.values()):
                raise ApprovalFailure('approval binding values must be text')
            expected = hmac.new(self._key, encoded(payload), hashlib.sha256).hexdigest()
            if not isinstance(signature, str) or not re.fullmatch(r'[0-9a-f]{64}', signature):
                raise ApprovalFailure('invalid approval signature shape')
            valid = hmac.compare_digest(signature, expected)
            binding = {k:payload.get(k) for k in ('root_id','preview_id','input_hash','patch_sha256')}
            required = {'root_id':self._root_id,'preview_id':preview['preview_id'],
                        'input_hash':body['input_hash'],'patch_sha256':body['patch_sha256']}
            if not valid or binding != required or payload.get('actor') not in self._allowed_actors:
                raise ApprovalFailure('approval actor, signature or input/patch binding failed')
        except (KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, ApprovalFailure):
                raise
            raise ApprovalFailure('malformed approval') from exc
        return body, payload['actor']

    def apply(self, preview, approval):
        body, actor = self.verify_approval(preview, approval)
        data, _, current_hash = self.snapshot()
        prior = self._applied.get(preview['preview_id'])
        if prior is not None:
            if current_hash != prior['after_input_hash']:
                raise StalePreview('already-applied fixture has subsequently changed')
            return {**json_copy(prior), 'status':'already_applied'}
        if current_hash != body['input_hash']:
            raise StalePreview('input changed after preview; create and review a new preview')
        candidate = dict(data)
        for change in body['changes']:
            if change['path'] != TARGET or digest(data[TARGET]) != change['before_sha256']:
                raise ApprovalFailure('change is outside the exact supported recipe')
            raw = change['after_text'].encode()
            if digest(raw) != AFTER_SHA or change['after_sha256'] != AFTER_SHA:
                raise ApprovalFailure('after content is outside audited recipe')
            candidate[TARGET] = raw
        gate = self.java_gate(self.materialize('apply-check', candidate), 'apply-check')
        if gate['outcome'] != body['validation']['before']['outcome']:
            raise GateFailure('apply gate no longer matches approved behavior')
        if self.snapshot()[2] != current_hash:
            raise StalePreview('fixture changed during apply validation')
        # One owned source file only. This is not a multi-file transactional writer.
        if body['changes']:
            temporary = self._root / '.price-policy-write'
            temporary.write_bytes(candidate[TARGET])
            os.replace(temporary, self._root / TARGET)
        receipt = {'status':'applied' if body['changes'] else 'no_change', 'actor':actor,
                   'preview_id':preview['preview_id'], 'input_hash':current_hash,
                   'patch_sha256':body['patch_sha256'], 'after_input_hash':self.snapshot()[2],
                   'changed_paths':[c['path'] for c in body['changes']], 'behavior':gate['outcome']}
        self._applied[preview['preview_id']] = json_copy(receipt)
        self.artifact('apply-receipt.json', receipt)
        return json_copy(receipt)

    def export_report(self, preview, receipt):
        report = {'case':'bounded-java-modernization', 'recipe':RECIPE, 'receipt':receipt,
                  'blast_radius':preview['body']['blast_radius'],
                  'behavior_parity':preview['body']['validation']['parity'],
                  'scope':'owned disposable fixture only',
                  'gaps':preview['body']['graph']['gaps'],
                  'durability':'approval keys and replay ledger are process-local; no restart claim'}
        self.artifact('report.json', report)
        manifest = []
        artifacts = {}
        for path in sorted(self.artifacts.iterdir()):
            if path.name == 'artifact-manifest.json':
                continue
            raw = path.read_bytes()
            manifest.append({'path':path.name, 'bytes':len(raw), 'sha256':digest(raw)})
            artifacts[path.name] = json.loads(raw) if path.suffix == '.json' else raw.decode()
        self.artifact('artifact-manifest.json', {'artifacts':manifest,'self_hash_excluded':True})
        # Embed artifact payloads in stdout so the optional redirected report survives temp cleanup.
        return {'report':report, 'artifact_manifest':manifest, 'artifacts':artifacts}

class BuiltinTests(unittest.TestCase):
    def test_complete_run_parity_graph_preview_approval_replay(self):
        with Accelerator() as app:
            original = app.snapshot()[2]
            preview = app.dry_run()
            self.assertEqual(app.snapshot()[2], original, 'dry run mutated sources')
            self.assertEqual(preview['body']['validation']['before']['outcome']['checks'],43)
            self.assertEqual({x['symbol'] for x in preview['body']['blast_radius']},
                             {'InvoiceService','ReceiptApi','BehaviorProbe'})
            self.assertEqual(preview['body']['graph']['dependencies']['InvoiceService'], ['PricePolicy'])
            self.assertEqual([c['path'] for c in preview['body']['changes']], [TARGET])
            approval = app.approve(preview,'reviewer-demo-token')
            receipt = app.apply(preview, approval)
            self.assertEqual(receipt['status'],'applied')
            self.assertEqual(digest((app.fixture_root/TARGET).read_bytes()), AFTER_SHA)
            replay = app.apply(preview, approval)
            self.assertEqual(replay['status'],'already_applied')
            self.assertEqual(replay['after_input_hash'],receipt['after_input_hash'])
            exported = app.export_report(preview, receipt)
            self.assertEqual(len(exported['artifact_manifest']),8)
            for item in exported['artifact_manifest']:
                self.assertEqual(digest((app.artifacts/item['path']).read_bytes()),item['sha256'])

    def test_unknown_actor_and_forged_identity(self):
        with Accelerator() as app:
            preview = app.dry_run()
            with self.assertRaises(ApprovalFailure):
                app.approve(preview,'fixture-reviewer')  # actor label is not a credential
            with self.assertRaises(ApprovalFailure):
                app.approve(preview,[])
            with self.assertRaises(ApprovalFailure):
                app.apply(preview, {'payload':[], 'signature':'0'*64})
            with self.assertRaises(ApprovalFailure):
                app.apply(preview, {'payload':{'actor':'fixture-reviewer'},'signature':'0'*64})
            approval = app.approve(preview,'reviewer-demo-token')
            forged = copy.deepcopy(approval)
            forged['payload']['actor'] = 'attacker'
            with self.assertRaises(ApprovalFailure):
                app.apply(preview,forged)
            forged['signature'] = 'é'
            with self.assertRaises(ApprovalFailure):
                app.apply(preview,forged)
            self.assertEqual(digest((app.fixture_root/TARGET).read_bytes()),BEFORE_SHA)

    def test_stale_dependency_change_and_tampered_patch(self):
        with Accelerator() as app:
            preview = app.dry_run()
            approval = app.approve(preview,'reviewer-demo-token')
            tampered = copy.deepcopy(preview)
            tampered['body']['changes'][0]['after_text'] += '\n// changed after review\n'
            with self.assertRaises(ApprovalFailure):
                app.apply(tampered,approval)
            dependency = app.fixture_root/'ReceiptApi.java'
            dependency.write_text(dependency.read_text()+'\n// drift outside target\n')
            with self.assertRaises(StalePreview):
                app.apply(preview,approval)
            self.assertEqual(digest((app.fixture_root/TARGET).read_bytes()),BEFORE_SHA)

    def test_preview_cannot_cross_fixture_root(self):
        with Accelerator() as one, Accelerator() as other:
            preview = one.dry_run()
            approval = one.approve(preview,'reviewer-demo-token')
            with self.assertRaises(ApprovalFailure):
                other.apply(preview,approval)

    def test_unsupported_exact_recipe_and_path_boundaries(self):
        with Accelerator() as app:
            target = app.fixture_root/TARGET
            target.write_text(target.read_text()+'\n// semantically harmless but unaudited\n')
            with self.assertRaises(UnsupportedRecipe):
                app.dry_run()
        with Accelerator() as app:
            outside = app.work/'outside.java'
            outside.write_text('outside remains untouched')
            original = outside.read_bytes()
            target = app.fixture_root/TARGET
            target.unlink()
            target.symlink_to(outside)
            with self.assertRaises(BoundaryFailure):
                app.snapshot()
            self.assertEqual(outside.read_bytes(),original)
        with Accelerator() as app:
            (app.fixture_root/'unexpected.java').write_text('class Unknown {}')
            with self.assertRaises(BoundaryFailure):
                app.snapshot()
        with Accelerator() as app:
            (app.fixture_root/'.fixture-owner.json').write_text('{}')
            with self.assertRaises(BoundaryFailure):
                app.snapshot()

    def test_actual_java_semantic_and_compile_failures(self):
        with Accelerator() as app:
            data, _, _ = app.snapshot()
            broken = dict(data)
            broken[TARGET] = templates('after')[TARGET].replace(
                b'return Math.multiplyExact((long) unitCents, quantity);', b'return quantity;')
            with self.assertRaises(GateFailure):
                app.java_gate(app.materialize('semantic-negative',broken),'semantic-negative')
            broken[TARGET] = b'public final class PricePolicy { THIS IS INVALID JAVA }\n'
            with self.assertRaises(GateFailure):
                app.java_gate(app.materialize('compile-negative',broken),'compile-negative')
            self.assertEqual(digest((app.fixture_root/TARGET).read_bytes()),BEFORE_SHA)

    def test_noop_preview_and_drift_after_replay(self):
        with Accelerator() as app:
            preview = app.dry_run()
            approval = app.approve(preview,'reviewer-demo-token')
            app.apply(preview,approval)
            noop = app.dry_run()
            self.assertEqual(noop['body']['changes'],[])
            self.assertEqual(app.apply(noop,app.approve(noop,'reviewer-demo-token'))['status'],'no_change')
            path = app.fixture_root/'InvoiceService.java'
            path.write_text(path.read_text()+'\n// after-apply drift\n')
            with self.assertRaises(StalePreview):
                app.apply(preview,approval)

    def test_inventory_bound_and_hard_link(self):
        with Accelerator() as app:
            (app.fixture_root/'ReceiptApi.java').write_bytes(b'x'*(MAX_FILE_BYTES+1))
            with self.assertRaises(BoundaryFailure):
                app.snapshot()
        with Accelerator() as app:
            target = app.fixture_root/'ReceiptApi.java'
            external = app.work/'hard-linked.java'
            os.link(target,external)
            with self.assertRaises(BoundaryFailure):
                app.snapshot()


def demo():
    with Accelerator() as app:
        preview = app.dry_run()
        approval = app.approve(preview,'reviewer-demo-token')
        receipt = app.apply(preview,approval)
        replay = app.apply(preview,approval)
        exported = app.export_report(preview,receipt)
        exported['replay_status'] = replay['status']
        print(json.dumps(exported,indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--demo',action='store_true')
    options = parser.parse_args()
    if options.demo and options.self_test:
        parser.error('select one mode')
    if options.demo:
        demo()
    else:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(BuiltinTests))
        raise SystemExit(0 if result.wasSuccessful() else 1)
