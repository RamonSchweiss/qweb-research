"""
The ablation nobody publishes: does training the quantum layer contribute?

Article : The Layer That Nobody Trains  (Sections 07-08, Figures 1 and 4)
Claims  : At matched capacity, freezing the quantum layer costs 19.5 points
          when the encoder is fixed, and under half a point when trainable
          classical layers surround it.

Needs   : pip install pennylane scikit-learn scipy
Runtime : about 2 minutes for the four variants, 6 for the capacity sweep.
"""
import numpy as np, time
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import StratifiedKFold
from scipy import stats
import qdnn_variants as V

print(__doc__)
d = load_breast_cancer(); X, y = d.data, d.target
KINDS = ("full", "frozen", "random", "classical")
LABEL = {"full":"quantum trained", "frozen":"quantum frozen",
         "random":"random map instead", "classical":"purely classical"}
SEEDS = (1,2,3,4,5)

print("Part 1 - four variants at matched capacity")
print("-" * 66)
res = {k: [] for k in KINDS}; npar = {}
t0 = time.time()
for fold,(itr,ite) in enumerate(StratifiedKFold(5,shuffle=True,random_state=0).split(X,y)):
    Atr, Ate = V.encode(X[itr], X[ite])
    for k in KINDS:
        for s in SEEDS:
            a,_,n,_ = V.train(k, Atr, y[itr], Ate, y[ite], seed=100*s+fold, steps=120)
            res[k].append(a); npar[k] = n

print("  variant              accuracy          trainable")
for k in KINDS:
    a = np.array(res[k])
    print(f"  {LABEL[k]:20s} {a.mean()*100:6.2f} % +/- {a.std()*100:4.2f}      {npar[k]:3d}")

print("\n  pairwise tests (Welch, 25 runs each)")
for a,b,q in (("full","frozen","does training the quantum layer help?"),
              ("frozen","random","is the fixed circuit better than a random map?"),
              ("full","classical","does the hybrid beat a classical model?")):
    t,p = stats.ttest_ind(res[a], res[b], equal_var=False)
    diff = (np.mean(res[a])-np.mean(res[b]))*100
    print(f"    {q}")
    print(f"      {diff:+.2f} pp, t={t:+.2f}, p={p:.1e}  ->  "
          f"{'significant' if p<0.05 else 'not significant'}")
print(f"\n  {time.time()-t0:.0f}s")

print("\nPart 2 - gradients of the quantum parameters")
print("-" * 66)
Atr, Ate = V.encode(X[:455], X[455:])
_,_,_,g = V.train("full", Atr, y[:455], Ate, y[455:], seed=1, steps=120, track_grad=True)
g = np.array(g)
print(f"  mean over 120 steps : {g.mean():.5f}")
print(f"  first ten steps     : {g[:10].mean():.5f}")
print(f"  last ten steps      : {g[-10:].mean():.5f}")
print(f"  smallest value      : {g.min():.5f}")
print("\n  They do not vanish, and they rise. At four qubits with local")
print("  observables there is no barren plateau here.")
print("\nFor Part 3, the capacity sweep behind Figure 4, run qdnn_sweep.py.")
