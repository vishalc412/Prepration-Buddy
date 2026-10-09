import json
import numpy as np
import torch
from torch import nn
from torch.utils.data import TensorDataset,DataLoader
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
SEED=31; torch.manual_seed(SEED); rng=np.random.default_rng(SEED)
X=rng.normal(size=(800,6)).astype('float32')
y=(X[:,0]+.5*X[:,1]+rng.normal(0,.4,800)>0).astype('float32')
order=rng.permutation(len(y)); train,valid=order[:600],order[600:]
xt=torch.from_numpy(X[train]); yt=torch.from_numpy(y[train])
xv=torch.from_numpy(X[valid]); yv=torch.from_numpy(y[valid])
loader=DataLoader(TensorDataset(xt,yt),batch_size=32,shuffle=True)
def network(): return nn.Sequential(nn.Linear(6,12),nn.ReLU(),nn.Dropout(.15),nn.Linear(12,1))
model=network(); loss_fn=nn.BCEWithLogitsLoss(); optimizer=torch.optim.Adam(model.parameters(),lr=.01)
def evaluate(m):
    m.eval()
    before=[p.detach().clone() for p in m.parameters()]
    with torch.no_grad():
        logits=m(xv).squeeze(-1); loss=loss_fn(logits,yv).item()
        probabilities=torch.sigmoid(logits)
    assert all(torch.equal(a,b) for a,b in zip(before,m.parameters()))
    return loss,probabilities
for epoch in range(12):
    model.train(); total=0.
    for features,labels in loader:
        optimizer.zero_grad(set_to_none=True)
        logits=model(features).squeeze(-1)
        assert logits.shape==labels.shape
        loss=loss_fn(logits,labels); loss.backward(); optimizer.step()
        total+=loss.item()*len(labels)
    vl,p=evaluate(model)
    print(epoch,{'train_loss':total/len(train),'validation_loss':vl})
baseline=LogisticRegression(max_iter=1000).fit(X[train],y[train])
print('linear accuracy',accuracy_score(y[valid],baseline.predict(X[valid])))
print('network accuracy',accuracy_score(y[valid],(p.numpy()>=.5)))
torch.save(model.state_dict(),'day04_weights.pt')
metadata={'schema':['f'+str(i) for i in range(6)],'architecture':'6-12-1','seed':SEED,'synthetic':True}
open('day04_schema.json','w').write(json.dumps(metadata))
loaded=network(); loaded.load_state_dict(torch.load('day04_weights.pt',map_location='cpu',weights_only=True))
_,reloaded=evaluate(loaded)
assert torch.allclose(p,reloaded,atol=1e-6,rtol=1e-6)
print('checkpoint parity passed')
