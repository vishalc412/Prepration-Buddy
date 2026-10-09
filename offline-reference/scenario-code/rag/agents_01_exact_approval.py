import hashlib,hmac,json,tempfile
from pathlib import Path
KEY=b'fixture-executor-key-not-production'
def digest(data): return hashlib.sha256(data).hexdigest()
def sign(receipt): return hmac.new(KEY,json.dumps(receipt,sort_keys=True).encode(),hashlib.sha256).hexdigest()
class Authority:
    def __init__(self,root,before,reviewed_after):
        self.root=Path(root).resolve()
        # Constructed once from actual trusted review, never from request fields.
        self.review={'tenant':'alpha','path':'Fixture.java','input':digest(before),
                     'output':digest(reviewed_after),'gate':'java-fixture-test'}
    def apply(self,verified_principal,request):
        if verified_principal!='reviewed-engineer-alpha' or request.get('tenant')!=self.review['tenant']:
            raise PermissionError('principal/tenant')
        if request.get('path')!=self.review['path']: raise PermissionError('scope')
        proposed=request.get('bytes')
        if not isinstance(proposed,bytes): raise ValueError('bytes required')
        if request.get('approval_hash')!=self.review['output'] or digest(proposed)!=self.review['output']:
            raise PermissionError('exact reviewed artifact required')
        path=self.root/self.review['path']
        if path.is_symlink() or not path.resolve().is_relative_to(self.root): raise PermissionError('path')
        if digest(path.read_bytes())!=self.review['input']: raise PermissionError('input drift')
        path.write_bytes(proposed)
        return {'status':'local_patch_written','artifact':digest(path.read_bytes())}
    def release(self,receipt,signature):
        if not isinstance(signature,str) or not hmac.compare_digest(sign(receipt),signature): raise PermissionError('signature')
        if (receipt.get('issuer')!='trusted-fixture-executor' or receipt.get('status')!='executed'
            or receipt.get('artifact')!=self.review['output'] or receipt.get('gate')!=self.review['gate']):
            raise PermissionError('required exact-artifact gate missing or failed')
        actual=digest((self.root/self.review['path']).read_bytes())
        if actual!=self.review['output']: raise PermissionError('artifact drift after gate')
        return {'status':'eligible_for_human_release_review','deployed':False}
if __name__=='__main__':
    with tempfile.TemporaryDirectory() as temp:
        before=b'class Fixture { int value(){return 1;} }'; after=b'class Fixture { int value(){return 2;} }'
        path=Path(temp)/'Fixture.java'; path.write_bytes(before)
        authority=Authority(temp,before,after)
        request={'tenant':'alpha','path':'Fixture.java','bytes':after,'approval_hash':digest(after)}
        for changes in [{'tenant':'beta'},{'bytes':b'evil','approval_hash':digest(b'evil')},
                        {'path':'../Fixture.java'},{'approval_hash':'forged'}]:
            try: authority.apply('reviewed-engineer-alpha',{**request,**changes})
            except PermissionError: pass
            else: raise AssertionError('request authority bypass')
        authority.apply('reviewed-engineer-alpha',request)
        receipt={'issuer':'trusted-fixture-executor','status':'executed','artifact':digest(after),'gate':'java-fixture-test'}
        assert authority.release(receipt,sign(receipt))['deployed'] is False
        for changes in [{'status':'failed'},{'artifact':'another'},{'gate':'wrong'},{'issuer':'model'}]:
            bad={**receipt,**changes}
            try: authority.release(bad,sign(bad))
            except PermissionError: pass
            else: raise AssertionError('signed invalid receipt accepted')
        path.write_bytes(b'changed after review')
        try: authority.release(receipt,sign(receipt))
        except PermissionError: pass
        else: raise AssertionError('drift accepted')
        print('PASS 10 exact-approval/receipt/drift fixtures; no actual Java tests or deploy')
