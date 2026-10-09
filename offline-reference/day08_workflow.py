from __future__ import annotations
import hashlib,json,tempfile
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
class Stage(str,Enum):
    INSPECT='inspect'; PLAN='plan'; APPROVED='approved'; PATCHED='patched'; CHECKED='checked'; REPORT='report'; BLOCKED='blocked'
@dataclass(frozen=True)
class Proposal:
    path: str
    before: str
    after: str
    source_hash: str
    def digest(self):
        return hashlib.sha256(json.dumps(self.__dict__,sort_keys=True).encode()).hexdigest()
def digest(data): return hashlib.sha256(data).hexdigest()
class Workflow:
    def __init__(self,root):
        self.root=Path(root).resolve(); self.stage=Stage.INSPECT; self.steps=0; self.maximum=8
        self.receipts={}; self.approval=None; self.proposal=None
    def tick(self):
        self.steps+=1
        if self.steps>self.maximum: self.stage=Stage.BLOCKED; raise RuntimeError('step budget exhausted')
    def file(self,relative):
        if relative!='Fixture.java': raise PermissionError('file outside approved scope')
        path=self.root/relative
        if path.is_symlink(): raise PermissionError('symlink denied')
        resolved=path.resolve()
        if not resolved.is_relative_to(self.root): raise PermissionError('path escape')
        return resolved
    def inspect(self):
        self.tick(); path=self.file('Fixture.java'); data=path.read_bytes()
        if len(data)>8192: raise ValueError('read cap exceeded')
        return {'source_hash':digest(data),'bytes':len(data),'unresolved_edges':['reflection not analyzed']}
    def plan(self):
        if self.stage!=Stage.INSPECT: raise RuntimeError('invalid transition')
        evidence=self.inspect(); self.tick()
        self.proposal=Proposal('Fixture.java','return 1;','return 2;',evidence['source_hash'])
        self.stage=Stage.PLAN; return self.proposal
    def approve(self,reviewed_digest):
        self.tick()
        if self.stage!=Stage.PLAN or reviewed_digest!=self.proposal.digest(): raise PermissionError('approval mismatch')
        self.approval=reviewed_digest; self.stage=Stage.APPROVED
    def apply(self):
        self.tick(); proposal=self.proposal; key=proposal.digest()
        if key in self.receipts:
            if digest(self.file(proposal.path).read_bytes())!=self.receipts[key]['output_hash']:
                raise PermissionError('replay artifact drift')
            return self.receipts[key]
        if self.stage!=Stage.APPROVED or key!=self.approval: raise PermissionError('missing or stale approval')
        path=self.file(proposal.path); data=path.read_bytes()
        if digest(data)!=proposal.source_hash: raise PermissionError('source changed since approval')
        text=data.decode()
        if text.count(proposal.before)!=1: raise ValueError('patch precondition failed')
        changed=text.replace(proposal.before,proposal.after,1)
        if len(changed.encode())>8192: raise ValueError('write cap exceeded')
        path.write_text(changed)
        receipt={'action':'local_fixture_patch','status':'executed','input_hash':digest(data),'output_hash':digest(path.read_bytes())}
        self.receipts[key]=receipt; self.stage=Stage.PATCHED
        (self.root/'receipts.json').write_text(json.dumps(self.receipts,indent=2))
        return receipt
    def check(self,passed):
        self.tick()
        if self.stage!=Stage.PATCHED: raise RuntimeError('invalid gate transition')
        self.stage=Stage.CHECKED if passed else Stage.BLOCKED
        return {'gate':'provided_fixture_assertion','passed':passed,'production_test':False}
    def report(self):
        self.tick()
        if self.stage!=Stage.CHECKED: raise RuntimeError('failed or missing gate')
        self.stage=Stage.REPORT
        return {'stage':self.stage.value,'deployment':'not performed','receipts':self.receipts}
if __name__=='__main__':
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp); (root/'Fixture.java').write_text('class Fixture { int value() { return 1; } }')
        flow=Workflow(root); proposal=flow.plan(); flow.approve(proposal.digest())
        first=flow.apply(); assert flow.apply()==first
        flow.check('return 2;' in (root/'Fixture.java').read_text()); print(json.dumps(flow.report(),indent=2))
        try: flow.file('../secret')
        except PermissionError: pass
        else: raise AssertionError('path escape accepted')
        (root/'Fixture.java').write_text('class Fixture { int value() { return 1; } }')
        bad=Workflow(root); p=bad.plan(); bad.approve(p.digest())
        bad.proposal=Proposal(p.path,p.before,'return 9;',p.source_hash)
        try: bad.apply()
        except PermissionError: pass
        else: raise AssertionError('stale approval accepted')
        fail=Workflow(root); p=fail.plan(); fail.approve(p.digest()); fail.apply(); fail.check(False)
        try: fail.report()
        except RuntimeError: pass
        else: raise AssertionError('failed gate released')
        print('path, stale approval, replay and failed gate checks passed')
