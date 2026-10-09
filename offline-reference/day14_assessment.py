import json,sys
DOMAINS=['Python','Statistics','ML','Deep Learning','NLP','LLM','Prompt Engineering','RAG',
         'AI Agents','MLOps','Cloud AI','DevOps','Java','Modernization','AI Security',
         'System Design','Leadership']
CRITICAL={'Python','ML','RAG','AI Agents','AI Security','Modernization'}
REQUIRED_BOUNDARIES=('tenant_isolation','tool_authorization','leakage_control','approval_binding')
def assess(data):
    scores=data.get('scores',{}); boundaries=data.get('critical_boundaries',{})
    if set(scores)-set(DOMAINS): raise ValueError('unknown scoring domain')
    if not isinstance(data.get('source'),str) or not data['source'].strip(): raise ValueError('score provenance required')
    assessed={}; unknown=[]
    for domain in DOMAINS:
        entry=scores.get(domain)
        if entry is None or entry.get('score') is None:
            unknown.append(domain); continue
        score=entry['score']
        if isinstance(score,bool) or not isinstance(score,(int,float)) or not 0<=score<=100:
            raise ValueError('invalid score')
        if not isinstance(entry.get('evidence'),list) or not entry['evidence']:
            unknown.append(domain); continue
        assessed[domain]=score
    for value in boundaries.values():
        if value not in ['passed','failed','unassessed']: raise ValueError('invalid boundary state')
    failed=[name for name,value in boundaries.items() if value=='failed']
    unknown_boundaries=sorted(set(boundaries)-set(REQUIRED_BOUNDARIES))
    unresolved=[name for name in REQUIRED_BOUNDARIES if boundaries.get(name,'unassessed')!='passed']
    unresolved+=unknown_boundaries
    weak=sorted(assessed,key=lambda d:(0 if d in CRITICAL else 1,assessed[d],d))
    targets=[d for d in weak if assessed[d]<65]+[d for d in unknown if d in CRITICAL]
    targets=list(dict.fromkeys(targets))[:3]
    while len(targets)<3: targets.append(['Capstone defense','Failure tests','Spaced recall'][len(targets)])
    revision=[{'minutes':20,'task':'Recall failed mechanisms without notes'},
      *[{'minutes':60,'task':f'{d}: mechanism 15m, worked example 15m, failure test 20m, closed-book defense 10m'} for d in targets],
      {'minutes':20,'task':'Reassess using actual evidence'},
      {'minutes':20,'task':'Capstone defense and tomorrow checkpoint'}]
    assert sum(x['minutes'] for x in revision)==240
    ready=not unknown and not failed and not unresolved and all(score>=65 for score in assessed.values())
    return {'source':data['source'],'assessment':'deterministic aggregation of human-entered rubric scores',
      'assessed_domains':len(assessed),'total_domains':len(DOMAINS),'unassessed':unknown,
      'mean_assessed':sum(assessed.values())/len(assessed) if assessed else None,
      'critical_failures':failed,'unresolved_boundaries':unresolved,
      'unknown_boundaries':unknown_boundaries,
      'readiness':'local rubric criteria met; not hiring certification' if ready else 'needs evidence or revision',
      'revision_240_minutes':revision}
if __name__=='__main__':
    if len(sys.argv)>1:
        data=json.load(open(sys.argv[1]))
    else:
        data={'source':'synthetic self-assessment example',
              'scores':{'Python':{'score':70,'evidence':['example receipt, replace with yours']},
                        'AI Security':{'score':90,'evidence':['example review, replace with yours']}},
              'critical_boundaries':{'tool_authorization':'failed'}}
    result=assess(data)
    if len(sys.argv)==1:
        assert len(result['unassessed'])==15
        assert result['readiness']=='needs evidence or revision'
        assert result['critical_failures']==['tool_authorization']
        complete={'source':'fixture self-test',
                  'scores':{d:{'score':80,'evidence':['fixture-only']} for d in DOMAINS},
                  'critical_boundaries':{b:'passed' for b in REQUIRED_BOUNDARIES}}
        assert assess(complete)['readiness'].startswith('local rubric criteria met')
        for status in ['failed','unassessed','passed']:
            extra={**complete,'critical_boundaries':{**complete['critical_boundaries'],'egress_policy':status}}
            blocked=assess(extra)
            assert blocked['readiness']=='needs evidence or revision'
            assert blocked['unknown_boundaries']==['egress_policy']
            assert 'egress_policy' in blocked['unresolved_boundaries']
        for boundary in REQUIRED_BOUNDARIES:
            missing={**complete,'critical_boundaries':{k:v for k,v in complete['critical_boundaries'].items() if k!=boundary}}
            assert assess(missing)['readiness']=='needs evidence or revision'
            failed={**complete,'critical_boundaries':{**complete['critical_boundaries'],boundary:'failed'}}
            assert assess(failed)['readiness']=='needs evidence or revision'
    print(json.dumps(result,indent=2))
