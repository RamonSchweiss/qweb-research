"""
Does the finding hold on other datasets?

Article : The Layer That Nobody Trains  (Section 08, Figure 5)
Claim   : On three datasets the pattern is the same. With a fixed encoder,
          freezing the quantum layer costs 19.6 to 30.6 points. With trainable
          classical layers either side it costs nothing significant.

Usage   : python qdnn_replicate.py breast_cancer
          also: wine, digits.  About two minutes each.
"""
import numpy as np, sys, time, json, os
from sklearn.datasets import load_breast_cancer, load_wine, load_digits
from sklearn.model_selection import StratifiedKFold
from scipy import stats
import qdnn_variants as V, qdnn_sweep as S

def get(name):
    if name=="breast_cancer":
        d=load_breast_cancer(); return d.data, d.target, "Wisconsin breast cancer"
    if name=="wine":
        d=load_wine(); m=(d.target==0)|(d.target==1)
        return d.data[m], d.target[m], "wine, cultivars 0 vs 1"
    if name=="digits":
        d=load_digits(); m=(d.target==3)|(d.target==8)
        return d.data[m], (d.target[m]==8).astype(int), "handwritten digits, 3 vs 8"
    raise ValueError(name)

if len(sys.argv) < 2:
    print(__doc__)
    print("No dataset given. Try one of:")
    for n in ("breast_cancer", "wine", "digits"):
        print(f"    python qdnn_replicate.py {n}")
    sys.exit(0)
name=sys.argv[1]
X,y,label = get(name)
print(f"\n{label}: {len(X)} samples, {X.shape[1]} features\n")
skf=StratifiedKFold(5,shuffle=True,random_state=0)
t0=time.time()

# --- A: vier Varianten, fester Encoder ---
res={k:[] for k in ("full","frozen","random","classical")}
for fold,(itr,ite) in enumerate(skf.split(X,y)):
    Atr,Ate=V.encode(X[itr],X[ite])
    for k in res:
        for s in (1,2,3):
            a,_,n,_=V.train(k,Atr,y[itr],Ate,y[ite],seed=100*s+fold,steps=120)
            res[k].append(a)
print("  A - fixed encoder, four variants (15 runs each)")
for k in ("full","frozen","random","classical"):
    a=np.array(res[k]); print(f"      {k:10s} {a.mean()*100:6.2f} % +/- {a.std()*100:4.2f}")
gapA=(np.mean(res['full'])-np.mean(res['frozen']))*100
t,p=stats.ttest_ind(res['full'],res['frozen'],equal_var=False)
print(f"      cost of freezing: {gapA:+.2f} pp   (p = {p:.1e})")

# --- B: mit trainierbaren klassischen Schichten ---
accs={True:[],False:[]}
for fold,(itr,ite) in enumerate(skf.split(X,y)):
    Atr,Ate=V.encode(X[itr],X[ite])
    for s in (1,2,3):
        for tq in (True,False):
            a,_,_=S.run(tq,4,Atr,y[itr],Ate,y[ite],seed=1000*s+10*fold)
            accs[tq].append(a)
f=np.array(accs[True]); z=np.array(accs[False])
gapB=(f.mean()-z.mean())*100
t2,p2=stats.ttest_ind(f,z,equal_var=False)
print(f"\n  B - trainable classical layers either side (15 runs each)")
print(f"      trained  {f.mean()*100:6.2f} % +/- {f.std()*100:4.2f}")
print(f"      frozen   {z.mean()*100:6.2f} % +/- {z.std()*100:4.2f}")
print(f"      cost of freezing: {gapB:+.2f} pp   (p = {p2:.1e})")

rec={"label":label,"n":len(X),"gap_fixed":gapA,"p_fixed":float(p),
     "gap_trainable":gapB,"p_trainable":float(p2),
     "A":{k:[float(np.mean(v)),float(np.std(v))] for k,v in res.items()}}
prev=json.load(open("replicate.json")) if os.path.exists("replicate.json") else {}
prev[name]=rec; json.dump(prev,open("replicate.json","w"))
print(f"\n  {time.time()-t0:.0f}s")
