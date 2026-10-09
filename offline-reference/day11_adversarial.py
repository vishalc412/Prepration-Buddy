import hashlib,hmac,json
TEST_KEY=b'fixture-only-not-a-production-secret'
# Trusted policy state, established by the human review channel; never copied
# from model output, request approval fields, or a tool receipt.
TRUSTED_REVIEWED_ARTIFACT='reviewed-hash'
def signature(receipt): return hmac.new(TEST_KEY,json.dumps(receipt,sort_keys=True).encode(),hashlib.sha256).hexdigest()
GOOD={'tenant':'tenant-a','role':'engineer','path':'src/Fixture.java','action':'read',
      'resource':'repository','egress':False,'approval':'reviewed-hash','artifact':'reviewed-hash',
      'tokens':200,'region':'approved','output_bytes':100,'instruction_origin':'user'}
RECEIPT={'issuer':'trusted-fixture-executor','status':'executed','artifact':'reviewed-hash'}
def authorize(request,receipt=None,sig=None):
    if request['tenant']!='tenant-a': raise PermissionError('tenant')
    if request['role']!='engineer': raise PermissionError('role')
    path=request['path']
    if path.startswith('/') or '..' in path.split('/') or '\\' in path: raise PermissionError('path')
    if request['action'] not in {'read','propose_patch'}: raise PermissionError('action')
    if request['resource']=='secret': raise PermissionError('secret')
    if request['egress']: raise PermissionError('egress')
    if request['approval']!=TRUSTED_REVIEWED_ARTIFACT or request['artifact']!=TRUSTED_REVIEWED_ARTIFACT:
        raise PermissionError('approval')
    if type(request['tokens']) is not int or not 0<=request['tokens']<=500: raise PermissionError('budget')
    if request['region']!='approved': raise PermissionError('region')
    if type(request['output_bytes']) is not int or not 0<=request['output_bytes']<=8192: raise PermissionError('output')
    if request['instruction_origin']!='user' and request['action']!='read': raise PermissionError('untrusted instruction')
    if receipt is not None:
        if (receipt.get('issuer')!='trusted-fixture-executor'
            or receipt.get('status')!='executed'
            or receipt.get('artifact')!=TRUSTED_REVIEWED_ARTIFACT
            or not isinstance(sig,str)
            or not hmac.compare_digest(signature(receipt),sig)):
            raise PermissionError('receipt')
    return True
CASES=[
 ('cross tenant',{'tenant':'tenant-b'},'tenant'),
 ('unauthorized role',{'role':'viewer'},'role'),
 ('path traversal',{'path':'../.env'},'path'),
 ('arbitrary command',{'action':'shell'},'action'),
 ('secret exfiltration',{'resource':'secret'},'secret'),
 ('network egress',{'egress':True},'egress'),
 ('stale artifact approval',{'artifact':'changed-hash'},'approval'),
 ('budget abuse',{'tokens':999999},'budget'),
 ('forged tool receipt',{},'receipt'),
 ('unapproved region',{'region':'other'},'region'),
 ('oversized tool output',{'output_bytes':999999},'output'),
 ('poisoned README instruction',{'instruction_origin':'retrieved_document','action':'propose_patch'},'untrusted instruction'),
 ('matching attacker-chosen hashes',{'approval':'attacker-hash','artifact':'attacker-hash'},'approval'),
 ('signed failed receipt',{},'receipt'),
 ('signed receipt for another artifact',{},'receipt')]
if __name__=='__main__':
    assert authorize(GOOD,RECEIPT,signature(RECEIPT))
    evidence=[]
    for name,changes,expected in CASES:
        request={**GOOD,**changes}
        receipt=None; sig=None
        if name=='forged tool receipt':
            receipt=RECEIPT; sig='attacker-supplied'
        elif name=='signed failed receipt':
            receipt={**RECEIPT,'status':'failed'}; sig=signature(receipt)
        elif name=='signed receipt for another artifact':
            receipt={**RECEIPT,'artifact':'different-hash'}; sig=signature(receipt)
        try: authorize(request,receipt,sig)
        except PermissionError as exc:
            observed=str(exc); passed=observed==expected
        else: observed='allowed'; passed=False
        evidence.append({'case':name,'expected':expected,'observed':observed,'passed':passed})
    print(json.dumps({'scope':'local toy authorization policy','cases':evidence,
      'passed':sum(x['passed'] for x in evidence),'total':len(evidence)},indent=2))
    assert all(x['passed'] for x in evidence)
