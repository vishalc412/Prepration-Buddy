import json,math,statistics
# All prices and durations are fixed teaching fixtures, not vendor rates or live measurements.
PRICES={'input_per_million':2.,'output_per_million':8.}
def summarize(rows):
    if not rows or len({r['id'] for r in rows})!=len(rows): raise ValueError('unique nonempty rows required')
    for r in rows:
        if type(r['correct']) is not bool or type(r['completed']) is not bool: raise ValueError('boolean outcome required')
        for field in ['input_tokens','output_tokens']:
            if type(r[field]) is not int or r[field]<0: raise ValueError('invalid token usage')
        if isinstance(r['ms'],bool) or not isinstance(r['ms'],(float,int)) or not math.isfinite(r['ms']) or r['ms']<0:
            raise ValueError('invalid latency')
    completed=[r for r in rows if r['completed']]
    costs=sum((r['input_tokens']*PRICES['input_per_million']+r['output_tokens']*PRICES['output_per_million'])/1_000_000 for r in rows)
    ordered=sorted(r['ms'] for r in completed)
    p95=ordered[math.ceil(.95*len(ordered))-1] if ordered else None
    return {'attempts':len(rows),'completed':len(completed),'failed':len(rows)-len(completed),
      'correct_of_attempts':sum(r['correct'] and r['completed'] for r in rows),
      'quality_per_attempt':sum(r['correct'] and r['completed'] for r in rows)/len(rows),
      'p95_completed_ms':p95,'estimated_fixture_cost':costs,'cost_includes_failed_attempt_usage':True}
def paired_decision(base,candidate):
    if {r['id'] for r in base}!={r['id'] for r in candidate}: raise ValueError('matched task IDs required')
    b,c=summarize(base),summarize(candidate)
    accepted=(c['quality_per_attempt']>=b['quality_per_attempt'] and c['failed']==0
              and c['p95_completed_ms'] is not None and c['p95_completed_ms']<=500)
    return {'accepted_fixture_configuration':accepted,'baseline':b,'candidate':c,
            'judge':'not used; correctness supplied by fixture labels','production_quality':'unassessed'}
if __name__=='__main__':
    base=[{'id':f'q{i}','input_tokens':2000,'output_tokens':200,'ms':350+i*10,'correct':True,'completed':True} for i in range(10)]
    candidate=[{**r,'input_tokens':500,'ms':200+r['ms']/10} for r in base]
    result=paired_decision(base,candidate); assert result['accepted_fixture_configuration']
    assert result['candidate']['estimated_fixture_cost']<result['baseline']['estimated_fixture_cost']
    failed=[dict(r) for r in candidate]; failed[0].update(completed=False,correct=False,ms=1000)
    assert not paired_decision(base,failed)['accepted_fixture_configuration']
    assert summarize(failed)['failed']==1 and summarize(failed)['attempts']==10
    slow=[{**r,'ms':900} for r in candidate]; assert not paired_decision(base,slow)['accepted_fixture_configuration']
    try: paired_decision(base,candidate[:-1])
    except ValueError: pass
    else: raise AssertionError('unpaired comparison')
    bad=[{**candidate[0],'ms':float('nan')}]
    try: summarize(bad)
    except ValueError: pass
    else: raise AssertionError('NaN latency accepted')
    print(json.dumps(result,indent=2)); print('PASS 7 cost/latency/quality/denominator fixtures')
