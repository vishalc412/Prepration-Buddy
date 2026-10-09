"""Offline FastAPI evidence/classification service. Run only on loopback for this case."""
from __future__ import annotations
import argparse
from contextlib import asynccontextmanager, contextmanager
import hashlib, json, os, re, sqlite3, uuid
from pathlib import Path
from typing import Annotated, Literal
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError
import uvicorn

# Explicit trusted fixture map; replace with verified identity/authorization in production.
PRINCIPALS={
    'Bearer token-acme-editor':{'actor':'alice','tenant':'acme','role':'editor'},
    'Bearer token-acme-viewer':{'actor':'eve','tenant':'acme','role':'viewer'},
    'Bearer token-bravo-editor':{'actor':'bob','tenant':'bravo','role':'editor'},
}
DATABASE:Path|None=None
FIXTURE=Path(__file__).with_name('seed_sources.json')

@contextmanager
def connection():
    if DATABASE is None: raise RuntimeError('explicit database path required')
    db=sqlite3.connect(DATABASE,timeout=3,isolation_level=None)
    db.row_factory=sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    try:yield db
    finally:db.close()

class Source(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    tenant:str=Field(min_length=1,max_length=40)
    source_id:str=Field(min_length=1,max_length=80)
    version:int=Field(ge=1)
    text:str=Field(min_length=1,max_length=4000)

class Assistance(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    question:str=Field(min_length=1,max_length=1000)
    ticket_text:str=Field(min_length=1,max_length=2000)
    # Fault injection exists solely in this teaching fixture, not a public production API.
    fixture_mode:Literal['normal','malformed','invalid_enum']='normal'

class Classification(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    category:Literal['billing','technical','general']
    urgency:Literal['low','high']

def initialize():
    sources=[Source.model_validate(x) for x in json.loads(FIXTURE.read_text())]
    with connection() as db:
        db.executescript('''
          CREATE TABLE IF NOT EXISTS sources(tenant TEXT NOT NULL,source_id TEXT NOT NULL,version INTEGER NOT NULL,text TEXT NOT NULL,PRIMARY KEY(tenant,source_id));
          CREATE TABLE IF NOT EXISTS tickets(ticket_id TEXT PRIMARY KEY,tenant TEXT NOT NULL,actor TEXT NOT NULL,request_json TEXT NOT NULL,result_json TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS commands(tenant TEXT NOT NULL,idem_key TEXT NOT NULL,request_hash TEXT NOT NULL,ticket_id TEXT NOT NULL REFERENCES tickets(ticket_id),response_json TEXT NOT NULL,PRIMARY KEY(tenant,idem_key));
          CREATE TABLE IF NOT EXISTS outbox(event_id TEXT PRIMARY KEY,ticket_id TEXT NOT NULL UNIQUE REFERENCES tickets(ticket_id),event_type TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'pending');
        ''')
        db.execute('BEGIN IMMEDIATE')
        try:
            for s in sources:db.execute('INSERT OR IGNORE INTO sources VALUES(?,?,?,?)',(s.tenant,s.source_id,s.version,s.text))
            db.execute('COMMIT')
        except Exception:
            db.execute('ROLLBACK');raise

@asynccontextmanager
async def lifespan(app):
    initialize()
    yield

app=FastAPI(lifespan=lifespan)
def principal(authorization:Annotated[str|None,Header()]=None):
    p=PRINCIPALS.get(authorization or '')
    if p is None:raise HTTPException(401,'verified demo principal required',headers={'WWW-Authenticate':'Bearer'})
    return p
Identity=Annotated[dict,Depends(principal)]

def token_set(text):return set(re.findall(r'[a-z0-9]+',text.lower()))
def provider_fixture(request):
    if request.fixture_mode=='malformed':return '{"category":'
    if request.fixture_mode=='invalid_enum':return '{"category":"pay_now","urgency":"critical"}'
    words=token_set(request.ticket_text)
    category='billing' if words&{'refund','refunds','bill','invoice'} else 'technical' if words&{'error','crash'} else 'general'
    urgency='high' if words&{'urgent','outage'} else 'low'
    return json.dumps({'category':category,'urgency':urgency})

def infer(request,tenant):
    # Validate output separately; syntactic JSON never grants permissions.
    try:classification=Classification.model_validate(json.loads(provider_fixture(request)))
    except (json.JSONDecodeError,ValidationError):raise HTTPException(502,'offline provider output contract failed')
    with connection() as db:
        rows=db.execute('SELECT source_id,version,text FROM sources WHERE tenant=? ORDER BY source_id',(tenant,)).fetchall()
    scored=[(len(token_set(request.question)&token_set(r['text'])),r) for r in rows]
    relevant=[r for score,r in sorted(scored,key=lambda pair:(-pair[0],pair[1]['source_id'])) if score>0][:2]
    # A complete literal source excerpt is the answer fixture; no semantic LLM claims.
    return {'classification':classification.model_dump(),
            'status':'answer' if relevant else 'no_answer',
            'answer':'\n'.join(r['text'] for r in relevant),
            'citations':[{'source_id':r['source_id'],'version':r['version']} for r in relevant]}

@app.get('/health')
def health():return {'status':'ready','implementation':'FastAPI'}
@app.post('/assist')
def assist(request:Assistance,identity:Identity):return infer(request,identity['tenant'])

@app.post('/tickets')
def create_ticket(request:Assistance,identity:Identity,idempotency_key:Annotated[str|None,Header()]=None):
    if identity['role']!='editor':raise HTTPException(403,'editor role required')
    if idempotency_key is None or re.fullmatch(r'[A-Za-z0-9_-]{1,80}',idempotency_key) is None:
        raise HTTPException(422,'bounded Idempotency-Key required')
    payload=json.dumps({'schema_version':1,'actor':identity['actor'],'tenant':identity['tenant'],'request':request.model_dump()},sort_keys=True,separators=(',',':'))
    digest=hashlib.sha256(payload.encode()).hexdigest()
    with connection() as db:
        # Lookup before inference makes accepted replays independent of provider availability.
        old=db.execute('SELECT request_hash,response_json FROM commands WHERE tenant=? AND idem_key=?',(identity['tenant'],idempotency_key)).fetchone()
        if old:
            if old['request_hash']!=digest:raise HTTPException(409,'idempotency key payload conflict')
            return json.loads(old['response_json'])
    result=infer(request,identity['tenant'])
    ticket_id=uuid.uuid4().hex
    response={'ticket_id':ticket_id,'tenant':identity['tenant'],'result':result}
    with connection() as db:
        db.execute('BEGIN IMMEDIATE')
        try:
            # Recheck inside transaction: two concurrent requests may both pass the first lookup.
            old=db.execute('SELECT request_hash,response_json FROM commands WHERE tenant=? AND idem_key=?',(identity['tenant'],idempotency_key)).fetchone()
            if old:
                if old['request_hash']!=digest:raise HTTPException(409,'idempotency key payload conflict')
                response=json.loads(old['response_json'])
            else:
                encoded=json.dumps(response,sort_keys=True)
                db.execute('INSERT INTO tickets VALUES(?,?,?,?,?)',(ticket_id,identity['tenant'],identity['actor'],payload,json.dumps(result,sort_keys=True)))
                db.execute('INSERT INTO commands VALUES(?,?,?,?,?)',(identity['tenant'],idempotency_key,digest,ticket_id,encoded))
                db.execute('INSERT INTO outbox VALUES(?,?,?,?)',(uuid.uuid4().hex,ticket_id,'ticket.created','pending'))
            db.execute('COMMIT')
        except Exception:
            db.execute('ROLLBACK');raise
    return response

@app.get('/tickets/{ticket_id}')
def read_ticket(ticket_id:str,identity:Identity):
    with connection() as db:
        row=db.execute('SELECT result_json FROM tickets WHERE tenant=? AND ticket_id=?',(identity['tenant'],ticket_id)).fetchone()
    if row is None:raise HTTPException(404,'ticket not found in allowed scope')
    return {'ticket_id':ticket_id,'tenant':identity['tenant'],'result':json.loads(row['result_json'])}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,required=True);parser.add_argument('--db',type=Path,required=True)
    args=parser.parse_args();DATABASE=args.db
    uvicorn.run(app,host='127.0.0.1',port=args.port,log_level='warning')
