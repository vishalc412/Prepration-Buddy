from dataclasses import dataclass
import json,re
@dataclass(frozen=True)
class Principal:
    user: str
    tenant: str
    roles: frozenset
# Fixture authentication middleware state; request bodies cannot create/replace it.
VERIFIED_SESSIONS={'session-alice':Principal('alice','alpha',frozenset({'engineer'})),
                   'session-viewer':Principal('viewer','alpha',frozenset({'viewer'}))}
CHUNKS=[
 {'tenant':'alpha','source':'orders.md','version':1,'chunk':'c1','roles':{'engineer'},'text':'orders java 8 upgrade'},
 {'tenant':'alpha','source':'orders.md','version':2,'chunk':'c1','roles':{'engineer'},'text':'orders java 17 contract serialization'},
 {'tenant':'alpha','source':'orders.md','version':2,'chunk':'c2','roles':{'engineer'},'text':'orders java 17 contract serialization'},
 {'tenant':'alpha','source':'portal.md','version':1,'chunk':'c1','roles':{'engineer'},'text':'portal identity redirects'},
 {'tenant':'beta','source':'private.md','version':9,'chunk':'c1','roles':{'engineer'},'text':'orders java 17 contract serialization confidential'},
 {'tenant':'alpha','source':'restricted.md','version':1,'chunk':'c1','roles':{'admin'},'text':'orders java 17 secret'}]
def terms(text): return set(re.findall(r'[a-z0-9_]+',text.lower()))
def retrieve(session,requested_tenant,query,k=3):
    principal=VERIFIED_SESSIONS.get(session)
    if principal is None: raise PermissionError('unverified session')
    if requested_tenant!=principal.tenant: raise PermissionError('requested tenant not authorized')
    if type(k) is not int or not 1<=k<=5: raise ValueError('k cap')
    # ACL is enforced BEFORE latest-version selection, deduplication and scoring.
    eligible=[c for c in CHUNKS if c['tenant']==principal.tenant and c['roles']&principal.roles]
    latest={}
    for c in eligible: latest[c['source']]=max(latest.get(c['source'],0),c['version'])
    current=[c for c in eligible if c['version']==latest[c['source']]]
    dedup={}
    for c in sorted(current,key=lambda c:(c['source'],c['chunk'])):
        dedup.setdefault((c['source'],c['version'],c['text']),c)
    ranked=[]; scored=[]; wanted=terms(query)
    for c in dedup.values():
        scored.append(c['source']); score=len(wanted&terms(c['text']))
        if score: ranked.append((score,c))
    ranked.sort(key=lambda item:(-item[0],item[1]['source'],item[1]['chunk']))
    hits=[{'citation':f"{c['tenant']}:{c['source']}@v{c['version']}#{c['chunk']}",
           'source':c['source'],'version':c['version'],'text':c['text']} for _,c in ranked[:k]]
    return {'hits':hits,'scored_sources':scored,'method':'lexical token overlap; no embeddings'}
if __name__=='__main__':
    result=retrieve('session-alice','alpha','orders java 17')
    assert len(result['hits'])==1
    assert result['hits'][0]['citation']=='alpha:orders.md@v2#c1'
    assert 'private.md' not in result['scored_sources'] and 'restricted.md' not in result['scored_sources']
    assert retrieve('session-viewer','alpha','orders')['hits']==[]
    assert retrieve('session-alice','alpha','unrepresented')['hits']==[]
    for session,tenant in [('session-alice','beta'),('forged-session','alpha')]:
        try: retrieve(session,tenant,'orders')
        except PermissionError: pass
        else: raise AssertionError('principal/tenant bypass')
    print(json.dumps(result,indent=2)); print('PASS 7 ACL/version/dedup/citation fixtures')
