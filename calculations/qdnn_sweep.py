"""
Capacity sweep: does freezing hurt less with more classical capacity?

Article : The Layer That Nobody Trains  (Section 08, Figure 4)
Claim   : The cost of freezing falls from 19.5 points to under half a point
          as trainable classical layers are added around the circuit.

Usage   : python qdnn_sweep.py 2    (then 4, 8, 16)
          Each run takes about 90 seconds and appends to sweep.json.
"""
import numpy as np, pennylane as qml, time, json
from pennylane import numpy as pnp
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import StratifiedKFold
import qdnn_variants as V

N_Q = V.N_QUBITS
circuit, SHAPE = V.circuit, V.SHAPE

def build(trainable_q, hid, rng):
    """hid = Breite der klassischen Schichten um die Quantenschicht herum."""
    w  = pnp.array(rng.normal(0,0.3,SHAPE), requires_grad=trainable_q)
    W0 = pnp.array(rng.normal(0,0.5,(N_Q,N_Q)), requires_grad=True)   # vor der Schaltung
    b0 = pnp.array(rng.normal(0,0.1,N_Q), requires_grad=True)
    W1 = pnp.array(rng.normal(0,0.5,(N_Q,hid)), requires_grad=True)   # nach der Schaltung
    b1 = pnp.array(rng.normal(0,0.1,hid), requires_grad=True)
    h  = pnp.array(rng.normal(0,0.3,hid+1), requires_grad=True)
    n_cl = N_Q*N_Q + N_Q + N_Q*hid + hid + hid + 1
    if trainable_q:
        def fwd(p, X):
            a = pnp.tanh(pnp.dot(pnp.array(X), p[0]) + p[1]) * np.pi
            q = pnp.stack(circuit(a, p[2])).T
            return pnp.dot(pnp.tanh(pnp.dot(q, p[3]) + p[4]), p[5][:-1]) + p[5][-1]
        return fwd, [W0,b0,w,W1,b1,h], n_cl + int(np.prod(SHAPE)), n_cl
    def fwd(p, X):
        a = pnp.tanh(pnp.dot(pnp.array(X), p[0]) + p[1]) * np.pi
        q = pnp.stack(circuit(a, w)).T
        return pnp.dot(pnp.tanh(pnp.dot(q, p[2]) + p[3]), p[4][:-1]) + p[4][-1]
    return fwd, [W0,b0,W1,b1,h], n_cl, n_cl

def run(trainable_q, hid, Xtr,ytr,Xte,yte, seed, steps=120):
    rng=np.random.default_rng(seed)
    fwd, params, n_tot, n_cl = build(trainable_q, hid, rng)
    opt=qml.AdamOptimizer(0.12)
    for _ in range(steps):
        idx=rng.choice(len(Xtr),min(48,len(Xtr)),replace=False)
        out=opt.step(lambda *p: V.bce(fwd(list(p),Xtr[idx]),ytr[idx]), *params)
        params=list(out) if isinstance(out,(list,tuple)) else [out]
    return float(((np.asarray(fwd(params,Xte))>0).astype(int)==yte).mean()), n_tot, n_cl

import sys, os
HID=int(sys.argv[1])
d=load_breast_cancer(); X,y=d.data,d.target
skf=StratifiedKFold(5,shuffle=True,random_state=0)
accs={True:[],False:[]}
t0=time.time()
for fold,(itr,ite) in enumerate(skf.split(X,y)):
    Atr,Ate=V.encode(X[itr],X[ite])
    for s in (1,2,3):
        for tq in (True,False):
            a,n_tot,n_cl=run(tq,HID,Atr,y[itr],Ate,y[ite],seed=1000*s+10*fold+HID)
            accs[tq].append(a)
f=np.array(accs[True]); z=np.array(accs[False])
rec={"hid":HID,"full":[f.mean(),f.std()],"frozen":[z.mean(),z.std()],
     "gap":(f.mean()-z.mean())*100,"n_classical":n_cl,"n_total":n_tot}
prev=json.load(open("sweep.json")) if os.path.exists("sweep.json") else {}
prev[str(HID)]=rec; json.dump(prev,open("sweep.json","w"))
print(f"  hid={HID}: klassisch {n_cl:3d} Param.  mitgelernt {f.mean()*100:5.2f} %  "
      f"eingefroren {z.mean()*100:5.2f} %  Abstand {(f.mean()-z.mean())*100:+5.2f} pp  ({time.time()-t0:.0f}s)")
