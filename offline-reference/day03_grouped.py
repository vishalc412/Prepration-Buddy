import json
import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit,GroupKFold,GridSearchCV
from sklearn.metrics import confusion_matrix,brier_score_loss
SEED=23; rng=np.random.default_rng(SEED); n=1800
frame=pd.DataFrame({'age':rng.integers(0,15,n),'dependencies':rng.integers(0,90,n),
                    'language':rng.choice(['java','dotnet'],n)})
groups=np.repeat(np.arange(60),30)
prob=1/(1+np.exp(-(-4+.20*frame.age+.035*frame.dependencies)))
y=(rng.random(n)<prob).astype(int)
trainval,test=next(GroupShuffleSplit(n_splits=1,test_size=.2,random_state=SEED).split(frame,y,groups))
a,b=next(GroupShuffleSplit(n_splits=1,test_size=.25,random_state=SEED+1).split(frame.iloc[trainval],y[trainval],groups[trainval]))
train,valid=trainval[a],trainval[b]
assert not set(groups[train])&set(groups[valid])
assert not set(groups[test])&(set(groups[train])|set(groups[valid]))
features=['age','dependencies','language']
def validate(df):
    if set(features)-set(df.columns): raise ValueError('missing required features')
    if df[features].isna().any().any(): raise ValueError('missing feature values')
    if not np.isfinite(df[['age','dependencies']].to_numpy(dtype=float)).all(): raise ValueError('nonfinite numeric values')
validate(frame)
pre=ColumnTransformer([('numbers',StandardScaler(),['age','dependencies']),
                       ('language',OneHotEncoder(handle_unknown='ignore'),['language'])])
pipe=Pipeline([('features',pre),('model',LogisticRegression(max_iter=1000,random_state=SEED))])
search=GridSearchCV(pipe,{'model__C':[.1,1,10]},cv=GroupKFold(3),scoring='neg_log_loss')
search.fit(frame.iloc[train],y[train],groups=groups[train])
model=search.best_estimator_; pv=model.predict_proba(frame.iloc[valid])[:,1]
candidates=[]
for t in np.linspace(0,1,101):
    pred=(pv>=t).astype(int); tn,fp,fn,tp=confusion_matrix(y[valid],pred,labels=[0,1]).ravel()
    if pred.mean() <= .60:
        candidates.append((int(fp+10*fn),float(t)))
cost,threshold=min(candidates)
pt=model.predict_proba(frame.iloc[test])[:,1]; predicted=(pt>=threshold).astype(int)
print('frozen threshold',threshold,'validation cost',cost,'test confusion',confusion_matrix(y[test],predicted,labels=[0,1]).tolist())
print('test Brier',brier_score_loss(y[test],pt))
for low in np.arange(0,1,.2):
    mask=(pt>=low)&(pt<low+.2+1e-12)
    if mask.any(): print('probability bin',round(float(low),1),'n',int(mask.sum()),'mean_probability',float(pt[mask].mean()),'observed_rate',float(y[test][mask].mean()))
for language in ['java','dotnet']:
    mask=frame.iloc[test].language.to_numpy()==language
    print('slice',language,'n',int(mask.sum()),'confusion',confusion_matrix(y[test][mask],predicted[mask],labels=[0,1]).tolist())
unknown=frame.iloc[[test[0]]].copy(); unknown['language']='unknown'
assert model.predict_proba(unknown).shape==(1,2)
try: validate(unknown.drop(columns='age'))
except ValueError: pass
else: raise AssertionError('missing schema not rejected')
manifest={'synthetic':True,'seed':SEED,'features':features,'sklearn':sklearn.__version__,
 'params':search.best_params_,'threshold':threshold,
 'groups':{name:sorted(map(int,set(groups[idx]))) for name,idx in [('train',train),('validation',valid),('test',test)]}}
print(json.dumps(manifest,indent=2))
