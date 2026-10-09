import json
from collections import deque
CAPABILITIES={
 'identity':{'azure':'workload identity','aws':'IAM workload role','gcp':'workload identity'},
 'ingress':{'azure':'API gateway boundary','aws':'API gateway boundary','gcp':'API gateway boundary'},
 'queue':{'azure':'durable queue service','aws':'durable queue service','gcp':'durable queue service'},
 'objects':{'azure':'object storage','aws':'object storage','gcp':'object storage'},
 'metadata':{'azure':'managed relational database','aws':'managed relational database','gcp':'managed relational database'},
 'workers':{'azure':'container workers','aws':'container workers','gcp':'container workers'},
 'model':{'azure':'approved model endpoint','aws':'approved model endpoint','gcp':'approved model endpoint'},
 'secrets':{'azure':'managed secret/key store','aws':'managed secret/key store','gcp':'managed secret/key store'}}
class RegionalQueue:
    def __init__(self,region,allowed,limit):
        if region not in allowed: raise PermissionError('unapproved region')
        if limit<1: raise ValueError('positive quota required')
        self.region=region; self.limit=limit; self.used=0; self.window=None
        self.pending=deque(); self.known=set(); self.completed={}
    def submit(self,job_id,tenant):
        if not job_id or not tenant: raise ValueError('identity missing')
        key=(tenant,job_id)
        if key in self.known: return 'duplicate'
        self.known.add(key); self.pending.append(key); return 'pending'
    def tick(self,minute):
        if self.window is not None and minute<self.window: raise ValueError('clock moved backwards')
        if minute!=self.window: self.window=minute; self.used=0
        executed=[]
        while self.pending and self.used<self.limit:
            key=self.pending.popleft(); self.used+=1
            self.completed[key]={'status':'simulated_completed','region':self.region,'minute':minute}
            executed.append(key)
        return {'executed':executed,'deferred':len(self.pending),'used':self.used}
if __name__=='__main__':
    queue=RegionalQueue('approved-region',{'approved-region'},2)
    for i in range(5): assert queue.submit(f'job-{i}','tenant-a')=='pending'
    first=queue.tick(0); assert len(first['executed'])==2 and first['deferred']==3
    assert queue.tick(0)['executed']==[]
    assert queue.submit('job-0','tenant-a')=='duplicate'
    queue.tick(1); queue.tick(2); assert len(queue.completed)==5 and not queue.pending
    try: RegionalQueue('other-region',{'approved-region'},2)
    except PermissionError: pass
    else: raise AssertionError('regional policy bypass')
    plan={'status':'architecture_only','paid_deployment':False,'capabilities':CAPABILITIES,
          'policy':{'fallback':'queue within approved region; no silent relocation',
                    'identity':'user tenant authorization plus narrow worker identity',
                    'quota':'central admission; persistent jobs; bounded retry after reconciliation'},
          'rotation':['new credential','overlap window','update workers','verify','revoke prior','audit']}
    print(json.dumps(plan,indent=2)); print('regional quota simulation passed',first)
