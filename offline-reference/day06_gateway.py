from __future__ import annotations
import json, multiprocessing as mp, time, math
from dataclasses import dataclass
@dataclass(frozen=True)
class Request:
    tenant: str
    evidence: tuple[dict,...]
    context: str
    max_output: int=80

def provider(request: Request) -> dict:
    runtime=next(e for e in request.evidence if e['kind']=='java_runtime')
    return {'action':'assess_java_upgrade','current_runtime':runtime['value'],
            'evidence_ids':[runtime['id']], 'status':'proposal',
            'input_units':len(request.context.split()),'output_units':24,'provider':'offline_stub'}
def child(request,queue,delay):
    time.sleep(delay)
    queue.put(provider(request))
def invoke(request,timeout=.5,delay=0.):
    ctx=mp.get_context('spawn'); queue=ctx.Queue()
    process=ctx.Process(target=child,args=(request,queue,delay))
    process.start()
    try:
        result=queue.get(timeout=timeout)
    except Exception as exc:
        process.terminate(); process.join()
        raise TimeoutError('offline provider deadline exceeded') from exc
    finally:
        if process.is_alive(): process.join(timeout=.1)
        if process.is_alive(): process.terminate(); process.join()
        queue.close()
    return result

def validate(request,result):
    required={'action','current_runtime','evidence_ids','status','input_units','output_units','provider'}
    if set(result)!=required: raise ValueError('response schema mismatch')
    if result['action']!='assess_java_upgrade' or result['status']!='proposal': raise ValueError('unsupported action')
    evidence={e['id']:e for e in request.evidence}
    ids=result['evidence_ids']
    if not isinstance(ids,list) or not ids or any(not isinstance(i,str) or i not in evidence for i in ids):
        raise ValueError('unsupported citation')
    runtime=result['current_runtime']
    if type(runtime) is not int or not any(evidence[i]['kind']=='java_runtime' and evidence[i]['value']==runtime for i in ids):
        raise ValueError('runtime claim not supported by citation')
    for name,cap in [('input_units',len(request.context.split())),('output_units',request.max_output)]:
        if type(result[name]) is not int or not 0<=result[name]<=cap: raise ValueError('usage outside cap')

class Gateway:
    # Teaching unit prices, not current vendor prices; single-process ledger only.
    INPUT_PRICE=.00001; OUTPUT_PRICE=.00002
    def __init__(self): self.balances={'tenant-a':1.0}
    def recommend(self,request,delay=0.):
        if request.tenant not in self.balances: raise PermissionError('unknown tenant')
        if request.max_output<24 or request.max_output>100: raise ValueError('output cap outside policy')
        if not request.evidence or any(e.get('tenant')!=request.tenant for e in request.evidence): raise PermissionError('cross-tenant evidence')
        maximum=len(request.context.split())*self.INPUT_PRICE+request.max_output*self.OUTPUT_PRICE
        if maximum>self.balances[request.tenant]: raise ValueError('budget exceeded before execution')
        self.balances[request.tenant]-=maximum
        try:
            result=invoke(request,delay=delay); validate(request,result)
            actual=result['input_units']*self.INPUT_PRICE+result['output_units']*self.OUTPUT_PRICE
            self.balances[request.tenant]+=maximum-actual
            return result,actual
        except Exception:
            self.balances[request.tenant]+=maximum
            raise

def percentile95(values):
    ordered=sorted(values); return ordered[max(0,math.ceil(.95*len(ordered))-1)]
if __name__=='__main__':
    gateway=Gateway(); reports={}
    for configuration in ['full','selected']:
        latencies=[]; units=0; cost=0.; passed=0
        for task in range(20):
            evidence=({'id':f'runtime-{task}','kind':'java_runtime','value':17,'tenant':'tenant-a'},)
            context='runtime 17' + (' irrelevant fixture details'*80 if configuration=='full' else '')
            request=Request('tenant-a',evidence,context)
            start=time.perf_counter(); result,charged=gateway.recommend(request)
            latencies.append((time.perf_counter()-start)*1000); units+=result['input_units']+result['output_units']; cost+=charged
            passed+=result['current_runtime']==17
        reports[configuration]={'provider':'offline_stub','supported_fixtures':passed,'total_fixtures':20,
                                'p95_stub_ms':percentile95(latencies),'estimated_units':units,'teaching_cost':cost}
    request=Request('tenant-a',({'id':'runtime','kind':'java_runtime','value':17,'tenant':'tenant-a'},),'runtime 17')
    forged=provider(request); forged['evidence_ids']=['missing']
    try: validate(request,forged)
    except ValueError: pass
    else: raise AssertionError('forged citation accepted')
    gateway.balances['tenant-a']=0.
    try: gateway.recommend(request)
    except ValueError: pass
    else: raise AssertionError('budget bypass')
    gateway.balances['tenant-a']=1.
    try: gateway.recommend(request,delay=1.)
    except TimeoutError: pass
    else: raise AssertionError('deadline missing')
    print(json.dumps(reports,indent=2)); print('citation, budget and timeout negative checks passed')
