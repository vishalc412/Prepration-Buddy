import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix, precision_score, recall_score
SEED=17
X,y=make_classification(n_samples=2000,n_features=10,n_informative=5,
    weights=[.95,.05],flip_y=.005,random_state=SEED)
indices=np.arange(len(y))
train,valid=train_test_split(indices,test_size=.3,stratify=y,random_state=SEED)
assert not set(train)&set(valid)
models={
 'majority':DummyClassifier(strategy='most_frequent'),
 'linear':make_pipeline(StandardScaler(),LogisticRegression(max_iter=1000,random_state=SEED)),
 'tree':DecisionTreeClassifier(max_depth=5,min_samples_leaf=10,random_state=SEED)}
for name,model in models.items():
    model.fit(X[train],y[train]); predicted=model.predict(X[valid])
    tn,fp,fn,tp=confusion_matrix(y[valid],predicted,labels=[0,1]).ravel()
    print(name,{'tn':int(tn),'fp':int(fp),'fn':int(fn),'tp':int(tp),
                'precision':precision_score(y[valid],predicted,zero_division=0),
                'recall':recall_score(y[valid],predicted,zero_division=0),
                'cost_fp1_fn20':int(fp+20*fn),'review_count':int(tp+fp)})
prior,sensitivity,fpr=.01,.90,.05
posterior=prior*sensitivity/(prior*sensitivity+(1-prior)*fpr)
assert abs(posterior-2/13)<1e-12
print('P(event | alert)',posterior,'synthetic demonstration only')
