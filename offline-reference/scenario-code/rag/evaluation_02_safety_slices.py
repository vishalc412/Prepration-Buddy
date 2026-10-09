import json
REQUIRED=('tenant_isolation','tool_authorization','approval_binding','leakage_control')
def gate(cases,boundaries):
    if not cases or len({c['id'] for c in cases})!=len(cases): raise ValueError('unique nonempty cases required')
    failed=[k for k,v in boundaries.items() if v=='failed']
    if any(v not in {'passed','failed','unassessed'} for v in boundaries.values()): raise ValueError('unknown state')
    unknown=sorted(set(boundaries)-set(REQUIRED))
    unresolved=[k for k in REQUIRED if boundaries.get(k,'unassessed')!='passed']+unknown
    slices={}
    for case in cases:
        if type(case['correct']) is not bool or not case['slice']: raise ValueError('invalid correctness/slice')
        slices.setdefault(case['slice'],[]).append(case['correct'])
    report={name:{'n':len(values),'correct':sum(values),'accuracy':sum(values)/len(values),
                  'sample_sufficient':len(values)>=2} for name,values in slices.items()}
    quality=all(s['sample_sufficient'] and s['accuracy']>=.75 for s in report.values())
    return {'promote':not failed and not unresolved and quality,'total_n':len(cases),
            'aggregate_accuracy':sum(c['correct'] for c in cases)/len(cases),
            'slices':report,'worst_slice_accuracy':min(s['accuracy'] for s in report.values()),
            'failed_boundaries':failed,'unresolved_boundaries':unresolved}
if __name__=='__main__':
    cases=[{'id':f'java-{i}','slice':'java','correct':True} for i in range(8)]+[
      {'id':'dotnet-0','slice':'dotnet','correct':False},{'id':'dotnet-1','slice':'dotnet','correct':False}]
    boundaries={k:'passed' for k in REQUIRED}
    result=gate(cases,boundaries); assert result['aggregate_accuracy']==.8 and not result['promote']
    fixed=[{**c,'correct':True} for c in cases]; assert gate(fixed,boundaries)['promote']
    for extra in ['failed','unassessed','passed']:
        assert not gate(fixed,{**boundaries,'egress':extra})['promote']
    for boundary in REQUIRED:
        assert not gate(fixed,{**boundaries,boundary:'failed'})['promote']
        assert not gate(fixed,{k:v for k,v in boundaries.items() if k!=boundary})['promote']
    assert not gate([fixed[0]],boundaries)['promote']
    print(json.dumps(result,indent=2)); print('PASS 14 aggregate/slice/safety/unknown/denominator fixtures')
