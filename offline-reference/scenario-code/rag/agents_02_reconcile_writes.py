import json,sqlite3,tempfile
from pathlib import Path
class Ledger:
    def __init__(self,path):
        self.db=sqlite3.connect(path)
        self.db.execute('CREATE TABLE IF NOT EXISTS effects (tenant TEXT, key TEXT, intent TEXT, artifact TEXT, PRIMARY KEY(tenant,key))')
        self.db.commit()
    def invoke(self,principal,tenant,key,intent,artifact,lose_response=False):
        if principal!='verified-alpha-worker' or tenant!='alpha': raise PermissionError('worker/tenant')
        previous=self.db.execute('SELECT intent,artifact FROM effects WHERE tenant=? AND key=?',(tenant,key)).fetchone()
        if previous:
            if previous!=(intent,artifact): raise ValueError('idempotency key intent mismatch')
            return {'status':'reconciled_existing','tenant':tenant,'key':key,'artifact':artifact}
        # Side effect and idempotency record deliberately share this transaction.
        with self.db:
            self.db.execute('INSERT INTO effects VALUES (?,?,?,?)',(tenant,key,intent,artifact))
        if lose_response: raise TimeoutError('response lost after commit; outcome uncertain to caller')
        return {'status':'executed','tenant':tenant,'key':key,'artifact':artifact}
    def count(self): return self.db.execute('SELECT COUNT(*) FROM effects').fetchone()[0]
    def close(self): self.db.close()
if __name__=='__main__':
    with tempfile.TemporaryDirectory() as temp:
        path=Path(temp)/'ledger.sqlite'; ledger=Ledger(path)
        try: ledger.invoke('verified-alpha-worker','alpha','run-1','create-fixture','hash-v1',True)
        except TimeoutError: pass
        else: raise AssertionError('uncertain write not simulated')
        assert ledger.count()==1; ledger.close()
        resumed=Ledger(path)
        receipt=resumed.invoke('verified-alpha-worker','alpha','run-1','create-fixture','hash-v1')
        assert receipt['status']=='reconciled_existing' and resumed.count()==1
        assert resumed.invoke('verified-alpha-worker','alpha','run-1','create-fixture','hash-v1')==receipt
        try: resumed.invoke('verified-alpha-worker','alpha','run-1','different-intent','hash-v2')
        except ValueError: pass
        else: raise AssertionError('key reused for different intent')
        try: resumed.invoke('verified-alpha-worker','beta','run-1','create-fixture','hash-v1')
        except PermissionError: pass
        else: raise AssertionError('cross tenant write')
        resumed.close(); print(json.dumps(receipt)); print('PASS 5 timeout/restart/replay/mismatch/tenant fixtures')
