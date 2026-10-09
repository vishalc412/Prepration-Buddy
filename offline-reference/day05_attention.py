import sys
import numpy as np

def attention(Q,K,V,causal=True):
    Q,K,V=map(np.asarray,(Q,K,V))
    if Q.ndim!=2 or K.ndim!=2 or V.ndim!=2:
        raise ValueError('expected rank-two arrays')
    if Q.shape!=K.shape or K.shape[0]!=V.shape[0] or Q.shape[1]==0 or Q.shape[0]==0:
        raise ValueError('incompatible nonempty shapes')
    if not all(np.isfinite(x).all() for x in (Q,K,V)):
        raise ValueError('nonfinite input')
    scores=Q@K.T/np.sqrt(Q.shape[1])
    if causal: scores=np.where(np.triu(np.ones(scores.shape,dtype=bool),k=1),-np.inf,scores)
    shifted=scores-scores.max(axis=1,keepdims=True)
    weights=np.exp(shifted); weights/=weights.sum(axis=1,keepdims=True)
    return weights@V,weights
rng=np.random.default_rng(41); Q=rng.normal(size=(4,3)); K=rng.normal(size=(4,3)); V=rng.normal(size=(4,2))
out,w=attention(Q,K,V)
assert out.shape==(4,2)
assert np.allclose(w.sum(axis=1),1)
assert np.all(w[np.triu_indices(4,1)]==0)
changed=V.copy(); changed[3]+=999
out2,_=attention(Q,K,changed)
assert np.allclose(out[:3],out2[:3])
one,wo=attention(np.ones((1,2)),np.ones((1,2)),np.ones((1,3)))
assert one.shape==(1,3) and wo[0,0]==1
print('causal attention tests passed',w)
if len(sys.argv)>1:
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(sys.argv[1],local_files_only=True)
    samples={'prose':'Upgrade the service after contract tests.',
      'java':'public record Risk(String repoId, double score) {}',
      'json':'{"repo_id":"orders","runtime_major":21}',
      'multilingual':'नमस्ते दुनिया / こんにちは世界'}
    for name,text in samples.items():
        ids=tokenizer.encode(text,add_special_tokens=True)
        print(name,'tokens',len(ids),'tokenizer',tokenizer.name_or_path,'ids',ids)
else:
    print('Tokenizer experiment not run: supply a locally installed tokenizer directory.')
