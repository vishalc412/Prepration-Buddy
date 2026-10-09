from fastapi import FastAPI,HTTPException
from day09_lineage import predict,V1
app=FastAPI(title='Offline fixture serving contract')
@app.get('/health')
def health(): return {'live':True}
@app.get('/ready')
def ready(): return {'ready':True,'bundle':V1.version}
@app.get('/version')
def version(): return V1.manifest()
@app.post('/predict')
def prediction(payload: dict):
    try: return predict(payload,V1)
    except (ValueError,TypeError) as exc: raise HTTPException(status_code=422,detail=str(exc))
