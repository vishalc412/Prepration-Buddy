from __future__ import annotations
import json,re
from dataclasses import dataclass
@dataclass(frozen=True)
class Document:
    id: str
    tenant: str
    roles: frozenset[str]
    text: str
    source: str
    version: str

def tokens(text): return set(re.findall(r'[a-z0-9_]+',text.lower()))
DOCS=[Document(f'{tenant}-note-{i}',tenant,frozenset({'engineer'}),
      f'repository repo_{i} migration topic_{i} runtime {17+i%2} contract serialization endpoint api_{i}',
      f'notes/repo_{i}.md','fixture-v1') for tenant in ['tenant-a','tenant-b'] for i in range(15)]
QUERIES=[{'id':f'q-{tenant}-{i}','tenant':tenant,'roles':['engineer'],
          'query':f'repo_{i} topic_{i} api_{i}','relevant':[f'{tenant}-note-{i}']}
         for tenant in ['tenant-a','tenant-b'] for i in range(15)]

def retrieve(query,tenant,roles,k=3):
    if not tenant or k<1 or k>10: raise ValueError('invalid retrieval request')
    authorized=[d for d in DOCS if d.tenant==tenant and d.roles&set(roles)]
    wanted=tokens(query)
    ranked=sorted(authorized,key=lambda d:(-len(wanted&tokens(d.text)),d.id))
    hits=[d for d in ranked if wanted&tokens(d.text)][:k]
    assert all(d.tenant==tenant and d.roles&set(roles) for d in hits)
    return hits

def evaluate(k):
    cases=[]
    for fixture in QUERIES:
        hits=retrieve(fixture['query'],fixture['tenant'],fixture['roles'],k)
        found={d.id for d in hits}; relevant=set(fixture['relevant'])
        if not relevant: raise ValueError('query missing relevance labels')
        recall=len(found&relevant)/len(relevant)
        cases.append({'query_id':fixture['id'],'retrieved':sorted(found),'recall':recall})
    return {'method':'lexical token overlap; no semantic embeddings','k':k,
      'documents':len(DOCS),'queries':len(cases),'macro_recall':sum(c['recall'] for c in cases)/len(cases),
      'failures':[c for c in cases if c['recall']<1]}
if __name__=='__main__':
    assert len(DOCS)==30 and len(QUERIES)==30
    for fixture in QUERIES:
        assert all(d.tenant==fixture['tenant'] for d in retrieve(fixture['query'],fixture['tenant'],fixture['roles']))
    assert retrieve('repo_0','tenant-a',['viewer'])==[]
    assert retrieve('repo_0','tenant-unknown',['engineer'])==[]
    assert {d.id for d in retrieve('repo_0','tenant-a',['engineer'])}=={'tenant-a-note-0'}
    print(json.dumps([evaluate(k) for k in [1,3,5]],indent=2))
    print('ACL negative checks passed; synthesis/faithfulness unassessed')
