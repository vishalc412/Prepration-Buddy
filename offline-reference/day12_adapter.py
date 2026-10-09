from __future__ import annotations
import hashlib,json,shutil,subprocess,tempfile
from pathlib import Path

def sha(data): return hashlib.sha256(data).hexdigest()
def execute(action,root):
    commands={'compile_java8':['javac','--release','8','QuoteFixture.java'],
              'compile_java17':['javac','--release','17','QuoteFixture.java'],
              'java_version':['java','-version'],
              'test_java':['java','-cp',str(root),'QuoteFixture']}
    if action not in commands: raise PermissionError('unsupported tool action')
    cmd=commands[action]
    if shutil.which(cmd[0]) is None:
        return {'action':action,'status':'not_executed','reason':'JDK tool not installed'}
    try:
        result=subprocess.run(cmd,cwd=root,timeout=15,capture_output=True,text=True)
    except subprocess.TimeoutExpired:
        return {'action':action,'status':'failed','reason':'timeout; reconcile workspace before retry'}
    stdout=result.stdout[:8192]; stderr=result.stderr[:8192]
    return {'action':action,'status':'executed' if result.returncode==0 else 'failed',
            'exit_code':result.returncode,'stdout':stdout,'stderr':stderr,
            'stdout_hash':sha(stdout.encode()),'stderr_hash':sha(stderr.encode())}

def java_gate(root,compile_action):
    compile_receipt=execute(compile_action,root)
    receipts=[compile_receipt]
    if compile_receipt['status']=='executed':
        test_receipt=execute('test_java',root); receipts.append(test_receipt)
        passed=test_receipt['status']=='executed' and 'PASS 5 Java behavior cases' in test_receipt.get('stdout','')
    else: passed=False
    return passed,receipts

def apply(path,before,after,approved_hash):
    current=path.read_bytes()
    proposed={'path':path.name,'input_hash':sha(current),'before':before,'after':after}
    expected=sha(json.dumps(proposed,sort_keys=True).encode())
    if approved_hash!=expected: raise PermissionError('approval does not bind proposed patch')
    text=current.decode()
    if text.count(before)!=1: raise ValueError('patch precondition failed')
    output=text.replace(before,after,1).encode(); path.write_bytes(output)
    return {'status':'executed','action':'approved_local_patch','approval_hash':expected,
            'input_hash':sha(current),'output_hash':sha(output)}

def dotnet_adapter_plan(root):
    return {'adapter_language':'python','target_ecosystem':'dotnet',
      'status':'dry_run','execution':'not_executed',
      'capabilities':['inventory','supported_tool_assessment','approved_tool_migration','build','contract_tests'],
      'workspace':str(root),'commands':[['dotnet','--info'],['dotnet','build','--no-restore']],
      'conditions':['supported modernization tool installed and pinned','source/target compatibility reviewed',
                    'isolated workspace','approved exact patch','no secrets or unauthorized egress'],
      'receipt_required':['tool_version','input_revision','scope_hash','exit_status','artifact_hash','gate_results']}
if __name__=='__main__':
    source=Path(__file__).with_name('QuoteFixture.java')
    with tempfile.TemporaryDirectory(prefix='bootcamp-java-') as temp:
        root=Path(temp); path=root/'QuoteFixture.java'; shutil.copyfile(source,path)
        baseline_ok,baseline=java_gate(root,'compile_java8')
        report={'scope':'Java 8 to 17 compiler-target upgrade plus local null-check recipe',
                'source_target':{'before_release':8,'after_release':17,'runtime_execution':'same installed JDK; not separate Java 8/17 runtime certification'},
                'installed_runtime':execute('java_version',root),'baseline':baseline,
                'dotnet':dotnet_adapter_plan(root),'deployment':'not performed'}
        before='if (value == null) throw new IllegalArgumentException("value required");'
        after='if (java.util.Objects.isNull(value)) throw new IllegalArgumentException("value required");'
        proposal={'path':path.name,'input_hash':sha(path.read_bytes()),'before':before,'after':after}
        approval=sha(json.dumps(proposal,sort_keys=True).encode())
        if baseline_ok:
            report['patch']=apply(path,before,after,approval)
            post_ok,post=java_gate(root,'compile_java17'); report['post_transform']=post
            report['covered_parity_passed']=post_ok
            assert post_ok
            try: apply(path,after,before,approval)
            except PermissionError: report['stale_approval_rejected']=True
            else: raise AssertionError('changed artifact accepted stale approval')
        else:
            report['patch']={'status':'not_executed','reason':'baseline unavailable or failed'}
        print(json.dumps(report,indent=2))
