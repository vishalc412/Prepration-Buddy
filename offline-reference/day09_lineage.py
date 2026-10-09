from __future__ import annotations
import hashlib,json,math,statistics
from dataclasses import asdict,dataclass
@dataclass(frozen=True)
class Bundle:
    version: str
    mean: float
    scale: float
    weight: float
    bias: float
    data_id: str='synthetic-fixture-v1'
    def manifest(self):
        value=asdict(self); value['schema']={'build_minutes':'finite float >= 0'}
        value['artifact_hash']=hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
        return value
V1=Bundle('bundle-v1',4.,2.,.5,-.3)
V2=Bundle('bundle-v2',5.,3.,.7,-.2)
def preprocess(payload,bundle):
    if set(payload)!={'build_minutes'}: raise ValueError('input schema mismatch')
    value=payload['build_minutes']
    if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value) or value<0:
        raise ValueError('invalid duration')
    if not math.isfinite(bundle.scale) or bundle.scale<=0: raise ValueError('invalid preprocessing bundle')
    return (value-bundle.mean)/bundle.scale

def predict(payload,bundle=V1):
    z=bundle.weight*preprocess(payload,bundle)+bundle.bias
    probability=1/(1+math.exp(-max(-700,min(700,z))))
    return {'risk_probability':probability,'bundle_version':bundle.version,
            'artifact_hash':bundle.manifest()['artifact_hash'],'synthetic':True}
class Registry:
    def __init__(self): self.active=V1; self.previous=None
    def promote(self,bundle,gate_passed):
        if not gate_passed: raise RuntimeError('promotion gate failed')
        self.previous,self.active=self.active,bundle
    def rollback(self):
        if self.previous is None: raise RuntimeError('no prior bundle')
        self.active,self.previous=self.previous,None

def drift(reference,current):
    if len(reference)<2 or len(current)<2: raise ValueError('insufficient samples')
    scale=statistics.stdev(reference)
    if scale==0: raise ValueError('constant reference needs another drift statistic')
    shift=abs(statistics.mean(current)-statistics.mean(reference))/scale
    return {'normalized_mean_shift':shift,'alarm':shift>2.,'labels_present':False,
            'claim':'input shift proxy; performance loss unassessed'}
if __name__=='__main__':
    payload={'build_minutes':6.}; serving=predict(payload,V1)
    offline=1/(1+math.exp(-(V1.weight*preprocess(payload,V1)+V1.bias)))
    assert math.isclose(serving['risk_probability'],offline,abs_tol=1e-12)
    for invalid in [{},{'build_minutes':float('nan')},{'build_minutes':-1},{'build_minutes':True},{'build_minutes':3,'tenant':'x'}]:
        try: predict(invalid)
        except ValueError: pass
        else: raise AssertionError('invalid schema accepted')
    registry=Registry(); before=predict(payload,registry.active)
    registry.promote(V2,True); assert predict(payload,registry.active)!=before
    registry.rollback(); assert predict(payload,registry.active)==before
    try: registry.promote(V2,False)
    except RuntimeError: pass
    else: raise AssertionError('failed promotion accepted')
    print(json.dumps({'manifest':V1.manifest(),'prediction':before,
                     'drift':drift([2,3,4,5,6],[12,13,14,15,16])},indent=2))
    print('schema, parity, promotion and full-bundle rollback checks passed')
