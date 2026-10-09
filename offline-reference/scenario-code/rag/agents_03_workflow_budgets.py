from dataclasses import dataclass
import json
@dataclass
class Budget:
    steps: int=0
    milliseconds: int=0
    tokens: int=0
    bytes: int=0
    def consume(self,steps,ms,tokens,bytes_):
        numbers=(steps,ms,tokens,bytes_)
        if any(type(x) is not int or x<0 for x in numbers): raise ValueError('invalid consumption')
        next_values=(self.steps+steps,self.milliseconds+ms,self.tokens+tokens,self.bytes+bytes_)
        if any(v>cap for v,cap in zip(next_values,(6,1000,500,8192))): raise RuntimeError('workflow budget exhausted')
        self.steps,self.milliseconds,self.tokens,self.bytes=next_values
class Workflow:
    ALLOWED={'inspect':('new','inspected'),'plan':('inspected','planned'),
             'propose':('planned','proposed'),'validate':('proposed','checked'),'report':('checked','reported')}
    def __init__(self): self.state='new'; self.budget=Budget(); self.receipts=[]
    def call(self,verified_principal,action,*,passed=True,ms=100,tokens=20,bytes_=100):
        if verified_principal!='verified-alpha-reader': raise PermissionError('principal')
        if action not in self.ALLOWED: raise PermissionError('unsupported capability')
        before,after=self.ALLOWED[action]
        if self.state!=before: raise RuntimeError('invalid transition')
        try: self.budget.consume(1,ms,tokens,bytes_)
        except RuntimeError: self.state='blocked'; raise
        if action=='validate' and passed is not True:
            self.state='blocked'; self.receipts.append({'action':action,'status':'failed'})
            return self.receipts[-1]
        self.state=after; self.receipts.append({'action':action,'status':'simulated_executed'})
        return self.receipts[-1]
def normal():
    flow=Workflow()
    for action in ['inspect','plan','propose','validate','report']: flow.call('verified-alpha-reader',action)
    return flow
if __name__=='__main__':
    flow=normal(); assert flow.state=='reported' and flow.budget.steps==5
    for consumption in [{'ms':1001},{'tokens':501},{'bytes_':8193}]:
        bad=Workflow()
        try: bad.call('verified-alpha-reader','inspect',**consumption)
        except RuntimeError: assert bad.state=='blocked'
        else: raise AssertionError('cap bypass')
    fail=Workflow()
    for action in ['inspect','plan','propose']: fail.call('verified-alpha-reader',action)
    fail.call('verified-alpha-reader','validate',passed=False)
    try: fail.call('verified-alpha-reader','report')
    except RuntimeError: pass
    else: raise AssertionError('failed gate report')
    for actor,action in [('model','inspect'),('verified-alpha-reader','shell')]:
        try: Workflow().call(actor,action)
        except PermissionError: pass
        else: raise AssertionError('authority bypass')
    budget=Budget(steps=6)
    try: budget.consume(1,0,0,0)
    except RuntimeError: pass
    else: raise AssertionError('step cap bypass')
    print(json.dumps({'state':flow.state,'budget':flow.budget.__dict__,'receipts':flow.receipts},indent=2))
    print('PASS 8 bounded-workflow fixtures; costs/time are supplied simulation units')
