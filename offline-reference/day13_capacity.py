import json,math
from dataclasses import asdict,dataclass
@dataclass(frozen=True)
class Workload:
    repos: int=500
    docs_per_repo: int=100
    revisions_retained: int=3
    average_doc_kib: float=12.
    chunks_per_doc: int=4
    bytes_per_index_chunk: int=2048
    requests_per_day: int=12000
    active_hours: int=8
    peak_multiplier: float=5.
    mean_latency_seconds: float=3.
    input_tokens: int=3000
    output_tokens: int=500

def estimate(w):
    values=asdict(w)
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<=0 for v in values.values()):
        raise ValueError('all workload values must be positive finite numbers')
    integer_fields=['repos','docs_per_repo','revisions_retained','chunks_per_doc','bytes_per_index_chunk','requests_per_day','active_hours','input_tokens','output_tokens']
    if any(type(values[name]) is not int for name in integer_fields): raise ValueError('count fields must be integers')
    documents=w.repos*w.docs_per_repo*w.revisions_retained
    average_qps=w.requests_per_day/(w.active_hours*3600)
    peak_qps=average_qps*w.peak_multiplier
    concurrency=peak_qps*w.mean_latency_seconds
    return {'status':'planning_estimate_not_measured','inputs':values,
      'stored_documents':documents,
      'raw_storage_gib':documents*w.average_doc_kib*1024/2**30,
      'estimated_index_gib':documents*w.chunks_per_doc*w.bytes_per_index_chunk/2**30,
      'average_qps_during_active_hours':average_qps,'peak_qps_assumption':peak_qps,
      'average_concurrency_at_peak_assumption':concurrency,
      'concurrency_limit_with_2x_headroom':math.ceil(2*concurrency),
      'peak_input_tokens_per_minute':peak_qps*w.input_tokens*60,
      'peak_output_tokens_per_minute':peak_qps*w.output_tokens*60,
      'limits':['index overhead assumption must be measured','tail latency excluded from Little law mean',
                'ingestion, provider quotas and tenant bursts require separate budgets']}
ADR={'status':'design_draft','decision':'durable asynchronous jobs for repository analysis',
     'requirement':'large repositories exceed interactive request deadline',
     'alternative':'synchronous single request','reason':'bounded retry and progress survive request disconnect',
     'risk':'queue lag and duplicate deliveries','control':'idempotent input revision plus durable receipts',
     'rollback':'pause admission; retain jobs; revert worker bundle after reconciliation',
     'evidence':'load/recovery test required before production claim'}
STAR={'situation':'Fill real context and your role','task':'Fill actual responsibility',
      'action':'Fill personal actions, alternative and disagreement',
      'result':'Unassessed until supported by real observation',
      'evidence':[],'lesson':'Fill what changed afterward','production_or_lab':'Specify honestly'}
if __name__=='__main__':
    result=estimate(Workload()); assert result['stored_documents']==150000
    assert result['concurrency_limit_with_2x_headroom']>=2*result['average_concurrency_at_peak_assumption']
    try: estimate(Workload(active_hours=0))
    except ValueError: pass
    else: raise AssertionError('zero divisor accepted')
    print(json.dumps({'capacity':result,'decision_record':ADR,'real_story_template':STAR},indent=2))
