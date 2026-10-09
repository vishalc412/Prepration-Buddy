"""Offline evaluation/trace and adoption lab. Synthetic candidate records, not live LLM inference."""
import hashlib
import json
import math
import sqlite3
import tempfile
from pathlib import Path

TENANT = 'alpha'
DOCUMENTS = [
    {'id': 'd1', 'tenant': 'alpha', 'text': 'Refund policy permits refunds within thirty days.', 'claims': {'refund-30'}},
    {'id': 'd2', 'tenant': 'alpha', 'text': 'Password resets require verified account ownership.', 'claims': {'verify-owner'}},
    {'id': 'd3', 'tenant': 'beta', 'text': 'Refund policy permits refunds within ninety days.', 'claims': {'refund-90'}},
]
DATASET = [
    {'id': f'q{i}', 'query': 'refund policy' if i < 5 else 'password resets',
     'gold_label': 'refund' if i < 5 else 'account', 'gold_doc': 'd1' if i < 5 else 'd2'}
    for i in range(10)
]

def retrieve(query, tenant, k=2):
    if not isinstance(query, str) or not query.strip() or type(k) is not int or k < 1:
        raise ValueError('nonempty query and positive integer k required')
    if not isinstance(tenant, str) or not tenant.strip():
        raise ValueError('trusted tenant required')
    terms = set(query.lower().split())
    ranked = sorted((d for d in DOCUMENTS if d['tenant'] == tenant),
                    key=lambda d: (-len(terms & set(d['text'].lower().split())), d['id']))
    return [d for d in ranked if terms & set(d['text'].lower().split())][:k]


def finite(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f'{field} must be a nonnegative finite number')
    return float(value)


def percentile(values, p):
    if not values:
        return None
    return sorted(values)[max(0, math.ceil(p*len(values))-1)]


def wilson(successes, total, z=1.96):
    if type(successes) is not int or type(total) is not int or not 0 <= successes <= total:
        raise ValueError('invalid count')
    if not total:
        return None
    proportion = successes/total
    denom = 1+z*z/total
    center = (proportion+z*z/(2*total))/denom
    radius = z*math.sqrt(proportion*(1-proportion)/total+z*z/(4*total*total))/denom
    return [max(0, center-radius), min(1, center+radius)]


def evaluate(records, tenant=TENANT):
    if not isinstance(records, list) or len(records) != len(DATASET):
        raise ValueError('one record per benchmark item required')
    expected = {q['id']: q for q in DATASET}
    seen = set()
    totals = {'correct': 0, 'accepted': 0, 'claims': 0, 'unsupported': 0, 'retrieved_gold': 0,
              'security_incidents': 0, 'cost': 0., 'tokens': 0}
    timings, traces = [], []
    for row in records:
        if not isinstance(row, dict) or set(row) != {'id', 'tenant', 'label', 'citations', 'claims', 'latency_ms', 'cost_usd', 'tokens'}:
            raise ValueError('record contract mismatch')
        if not isinstance(row['id'], str) or row['id'] not in expected or row['id'] in seen:
            raise ValueError('benchmark identity duplicate or unknown')
        seen.add(row['id'])
        if not isinstance(row['tenant'], str) or not row['tenant'].strip():
            raise ValueError('record tenant required')
        if not isinstance(row['label'], str) or row['label'] not in {'refund', 'account', 'abstain'} or not isinstance(row['citations'], list) or not isinstance(row['claims'], list):
            raise ValueError('invalid label or collection')
        if not all(isinstance(v, str) and v for v in row['citations']+row['claims']):
            raise ValueError('citations and claims must be nonempty strings')
        if len(row['claims']) != len(set(row['claims'])) or len(row['citations']) != len(set(row['citations'])):
            raise ValueError('duplicate claims or citations distort denominator')
        if type(row['tokens']) is not int or row['tokens'] < 0:
            raise ValueError('tokens must be nonnegative integer')
        latency = finite(row['latency_ms'], 'latency_ms')
        cost = finite(row['cost_usd'], 'cost_usd')
        gold = expected[row['id']]
        retrieved = retrieve(gold['query'], tenant)
        allowed = {d['id']: d for d in retrieved}
        cited = [allowed[c] for c in row['citations'] if c in allowed]
        security = row['tenant'] != tenant or any(c not in allowed for c in row['citations'])
        totals['security_incidents'] += int(security)
        totals['retrieved_gold'] += int(gold['gold_doc'] in allowed)
        supported_claims = set().union(*(d['claims'] for d in cited)) if cited else set()
        unsupported = sum(c not in supported_claims for c in row['claims'])
        correct = row['label'] == gold['gold_label']
        # Label accuracy alone does not make a response acceptable.
        accepted = correct and bool(row['claims']) and bool(cited) and not unsupported and not security
        totals['correct'] += int(correct)
        totals['accepted'] += int(accepted)
        totals['claims'] += len(row['claims'])
        totals['unsupported'] += unsupported
        totals['cost'] += cost
        totals['tokens'] += row['tokens']
        timings.append(latency)
        traces.append({'request_id': row['id'], 'query_hash': hashlib.sha256(gold['query'].encode()).hexdigest(),
                       'retrieval_ids': list(allowed), 'citation_ids': row['citations'],
                       'accepted': bool(accepted), 'latency_ms': latency, 'cost_usd': cost, 'tokens': row['tokens']})
    n = len(DATASET)
    result = {'dataset_version': 'synthetic-support-v1', 'requests': n,
              'label_accuracy': totals['correct']/n, 'retrieval_recall_at_2': totals['retrieved_gold']/n,
              'accepted': totals['accepted'], 'accepted_rate': totals['accepted']/n,
              'claim_count': totals['claims'], 'unsupported_count': totals['unsupported'],
              'unsupported_claim_rate': totals['unsupported']/totals['claims'] if totals['claims'] else None,
              'unsupported_wilson_interval': wilson(totals['unsupported'], totals['claims']) if totals['claims'] else None,
              'security_incidents': totals['security_incidents'], 'p95_ms': percentile(timings, .95),
              'cost_usd': totals['cost'], 'cost_per_accepted_usd': totals['cost']/totals['accepted'] if totals['accepted'] else None,
              'tokens': totals['tokens'], 'traces': traces}
    result['gate_pass'] = (result['label_accuracy'] >= .9 and result['accepted_rate'] >= .8
                           and result['unsupported_claim_rate'] is not None and result['unsupported_claim_rate'] <= .1
                           and result['security_incidents'] == 0 and result['p95_ms'] <= 1000
                           and result['cost_per_accepted_usd'] is not None and result['cost_per_accepted_usd'] <= .02)
    return result


def candidate(kind):
    rows = []
    for q in DATASET:
        rows.append({'id': q['id'], 'tenant': TENANT, 'label': q['gold_label'],
                     'citations': [q['gold_doc']], 'claims': ['refund-30' if q['gold_label']=='refund' else 'verify-owner'],
                     'latency_ms': 120 if kind != 'expensive' else 600, 'cost_usd': .002 if kind != 'expensive' else .03, 'tokens': 110})
    if kind == 'cheap_bad':
        rows[0]['claims'] = ['refund-90']
        rows[1]['citations'] = ['d3']  # Even one authorization failure blocks the gate.
    return rows


def choose(reports):
    eligible = [(name, report) for name, report in reports.items() if report['gate_pass']]
    return min(eligible, key=lambda pair: (pair[1]['cost_per_accepted_usd'], pair[0]))[0] if eligible else None


def adoption(before, after):
    # Counts are comparable only if cohort/task mix and review standard match.
    required = {'accepted', 'active_minutes', 'escaped_defects', 'users', 'eligible_users'}
    for row in (before, after):
        if set(row) != required or any(type(row[k]) is not int or row[k] < 0 for k in required):
            raise ValueError('pilot counts must be nonnegative integers')
        if row['users'] > row['eligible_users'] or not row['accepted'] or not row['eligible_users']:
            raise ValueError('pilot denominators invalid')
    old, new = before['active_minutes']/before['accepted'], after['active_minutes']/after['accepted']
    return {'before_minutes_per_accepted': old, 'after_minutes_per_accepted': new,
            'relative_active_time_reduction': (old-new)/old if old else None,
            'after_adoption_rate': after['users']/after['eligible_users'],
            'after_defects_per_accepted': after['escaped_defects']/after['accepted'],
            'limit': 'Synthetic cohorts; no causal productivity or enterprise adoption claim.'}


def main():
    reports = {k: evaluate(candidate(k)) for k in ('cheap_bad', 'cheap_good', 'expensive')}
    assert choose(reports) == 'cheap_good'
    assert reports['cheap_bad']['label_accuracy'] == 1 and not reports['cheap_bad']['gate_pass']
    assert not reports['expensive']['gate_pass']
    all_abstain = candidate('cheap_good')
    for row in all_abstain:
        row.update(label='abstain', citations=[], claims=[])
    report = evaluate(all_abstain)
    assert report['unsupported_claim_rate'] is None and report['cost_per_accepted_usd'] is None and not report['gate_pass']
    for field, value in (('cost_usd',float('nan')),('latency_ms',float('inf')),('tokens',True),('tenant',None)):
        broken = candidate('cheap_good')
        broken[0][field] = value
        try:
            evaluate(broken)
            raise AssertionError('invalid fixture must fail')
        except ValueError:
            pass
    duplicate = candidate('cheap_good')
    duplicate[1]['id'] = duplicate[0]['id']
    try:
        evaluate(duplicate)
        raise AssertionError('duplicate benchmark identity')
    except ValueError:
        pass
    assert len(retrieve('refund policy', 'alpha')) == 1 and all(d['tenant']=='alpha' for d in retrieve('refund policy', 'alpha'))
    assert wilson(0, 10)[1] > .2  # Zero observed errors is not proof of zero population risk.
    pilot = adoption({'accepted':10,'active_minutes':300,'escaped_defects':0,'users':2,'eligible_users':5},
                     {'accepted':10,'active_minutes':210,'escaped_defects':0,'users':4,'eligible_users':5})
    assert math.isclose(pilot['relative_active_time_reduction'], .3)
    with tempfile.TemporaryDirectory(prefix='prep-eval-') as folder:
        db = sqlite3.connect(Path(folder)/'traces.sqlite')
        db.execute('CREATE TABLE traces(request_id TEXT PRIMARY KEY, payload TEXT NOT NULL)')
        db.executemany('INSERT INTO traces VALUES (?,?)', [(t['request_id'],json.dumps(t)) for t in reports['cheap_good']['traces']])
        db.commit()
        assert db.execute('SELECT COUNT(*) FROM traces').fetchone()[0] == 10
        db.close()
    compact = {k:{field:value for field,value in r.items() if field!='traces'} for k,r in reports.items()}
    print(json.dumps({'status':'PASS','selected_candidate':choose(reports),'reports':compact,'pilot':pilot,
                      'checks': ['tenant-filtered retrieval','correct label with unsupported claims rejected','one security incident blocks release',
                                 'zero accepted/no claims denominators remain unknown','finite/type validation','duplicate identity rejected',
                                 'durable SQL trace records','zero errors still has confidence interval','comparable pilot arithmetic'],
                      'limits':['Synthetic outputs and claim labels; not live model quality','Lexical retrieval, not embeddings or ANN',
                                'Manual governance/approval remains separate from quality gate']},indent=2))

if __name__ == '__main__':
    main()
