import json

def metrics(ranked,relevant,k):
    if type(k) is not int or k<1: raise ValueError('positive k required')
    if not relevant: raise ValueError('unlabeled/no-relevant query requires separate abstention cohort')
    if len(ranked)!=len(set(ranked)): raise ValueError('duplicate result IDs')
    top=ranked[:k]; relevant=set(relevant)
    recall=len(set(top)&relevant)/len(relevant)
    reciprocal=next((1/rank for rank,item in enumerate(top,1) if item in relevant),0.)
    return {'recall_at_k':recall,'reciprocal_rank_at_k':reciprocal}
FIXTURES=[{'id':'q1','relevant':['a','b'],'baseline':['x','a','b'],'candidate':['a','x','b']},
          {'id':'q2','relevant':['c'],'baseline':['c','x'],'candidate':['x','y']},
          {'id':'q3','relevant':['d'],'baseline':['x','d'],'candidate':['d','x']}]

def compare(fixtures,k):
    if not fixtures or len({f['id'] for f in fixtures})!=len(fixtures): raise ValueError('unique paired query IDs required')
    pairs=[]
    for f in fixtures:
        baseline=metrics(f['baseline'],f['relevant'],k); candidate=metrics(f['candidate'],f['relevant'],k)
        pairs.append({'id':f['id'],'baseline':baseline,'candidate':candidate,
                      'recall_delta':candidate['recall_at_k']-baseline['recall_at_k']})
    return {'k':k,'queries':len(pairs),'mean_paired_recall_delta':sum(p['recall_delta'] for p in pairs)/len(pairs),
       'baseline_MRR_at_k':sum(p['baseline']['reciprocal_rank_at_k'] for p in pairs)/len(pairs),
       'candidate_MRR_at_k':sum(p['candidate']['reciprocal_rank_at_k'] for p in pairs)/len(pairs),
       'regressions':[p['id'] for p in pairs if p['recall_delta']<0],'pairs':pairs}
if __name__=='__main__':
    assert metrics(['x','a'],{'a','b'},2)=={'recall_at_k':.5,'reciprocal_rank_at_k':.5}
    result=compare(FIXTURES,2)
    assert result['regressions']==['q2'] and result['queries']==3
    assert abs(result['mean_paired_recall_delta']+1/3)<1e-12
    for ranked,relevant,k in [(['a','a'],{'a'},2),(['a'],set(),2),(['a'],{'a'},0)]:
        try: metrics(ranked,relevant,k)
        except ValueError: pass
        else: raise AssertionError('invalid metric denominator/input accepted')
    try: compare([FIXTURES[0],FIXTURES[0]],2)
    except ValueError: pass
    else: raise AssertionError('duplicate pairs accepted')
    print(json.dumps(result,indent=2)); print('PASS 6 rank-metric/paired-input fixtures')
