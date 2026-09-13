"""
Vier Varianten mit ABGEGLICHENER Kapazitaet.

Alle haben dieselbe Zahl trainierbarer Parameter. Der einzige Unterschied
ist, WAS in der Mitte sitzt und ob es mitgelernt wird.
"""
import numpy as np, pennylane as qml
from pennylane import numpy as pnp
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

N_QUBITS, N_LAYERS = 4, 2
SHAPE = qml.StronglyEntanglingLayers.shape(N_LAYERS, N_QUBITS)
N_Q = int(np.prod(SHAPE))            # 24 Quantenparameter

dev = qml.device("default.qubit", wires=N_QUBITS)
@qml.qnode(dev, interface="autograd")
def circuit(x, w):
    qml.AngleEmbedding(x, wires=range(N_QUBITS), rotation="Y")
    qml.StronglyEntanglingLayers(w, wires=range(N_QUBITS))
    return [qml.expval(qml.PauliZ(i)) for i in range(N_QUBITS)]

def encode(Xtr, Xte):
    """Fester klassischer Encoder: 30 Merkmale -> 4, auf [-pi,pi] skaliert."""
    sc = StandardScaler().fit(Xtr)
    pca = PCA(n_components=N_QUBITS, random_state=0).fit(sc.transform(Xtr))
    ref = np.abs(pca.transform(sc.transform(Xtr))).max(axis=0) + 1e-9
    prep = lambda X: np.clip(pca.transform(sc.transform(X))/ref, -1, 1)*np.pi
    return prep(Xtr), prep(Xte)

def _head(F, h):
    return pnp.dot(F, h[:-1]) + h[-1]

def bce(z, y):
    s = 2*pnp.array(y) - 1
    return pnp.mean(pnp.log(1 + pnp.exp(-s*z)))

def build(kind, rng):
    """Gibt (forward, params, n_trainable) zurueck. Kapazitaet abgeglichen auf N_Q + 5."""
    TARGET = N_Q + N_QUBITS + 1                      # 29
    w  = pnp.array(rng.normal(0, 0.3, SHAPE), requires_grad=False)
    # feste zufaellige Projektion, milde skaliert damit tanh nicht saettigt
    P  = pnp.array(rng.normal(0, 1.0/np.sqrt(N_QUBITS), (N_QUBITS, N_QUBITS)), requires_grad=False)
    bb = pnp.array(rng.uniform(-0.5, 0.5, N_QUBITS), requires_grad=False)

    if kind == "full":                               # Quantenschicht wird mitgelernt
        wt = pnp.array(w, requires_grad=True)
        h  = pnp.array(rng.normal(0,0.3,N_QUBITS+1), requires_grad=True)
        fwd = lambda p, X: _head(pnp.stack(circuit(pnp.array(X), p[0])).T, p[1])
        return fwd, [wt, h], N_Q + N_QUBITS + 1

    if kind == "frozen":                             # Quantenschicht fest, Rest aufgefuellt
        hid = 4
        W1 = pnp.array(rng.normal(0,0.5,(N_QUBITS,hid)), requires_grad=True)
        b1 = pnp.array(rng.normal(0,0.1,hid), requires_grad=True)
        h  = pnp.array(rng.normal(0,0.3,hid+1), requires_grad=True)
        def fwd(p, X):
            q = pnp.stack(circuit(pnp.array(X), w)).T
            return _head(pnp.tanh(pnp.dot(q, p[0]) + p[1]), p[2])
        return fwd, [W1, b1, h], N_QUBITS*hid + hid + hid + 1

    if kind == "random":                             # Zufallsabbildung statt Schaltung
        hid = 4
        W1 = pnp.array(rng.normal(0,0.5,(N_QUBITS,hid)), requires_grad=True)
        b1 = pnp.array(rng.normal(0,0.1,hid), requires_grad=True)
        h  = pnp.array(rng.normal(0,0.3,hid+1), requires_grad=True)
        def fwd(p, X):
            r = pnp.tanh(pnp.dot(pnp.array(X), P) + bb)
            return _head(pnp.tanh(pnp.dot(r, p[0]) + p[1]), p[2])
        return fwd, [W1, b1, h], N_QUBITS*hid + hid + hid + 1

    # rein klassisch, gleiche Gesamtzahl wie frozen/random
    hid = 4
    W1 = pnp.array(rng.normal(0,0.5,(N_QUBITS,hid)), requires_grad=True)
    b1 = pnp.array(rng.normal(0,0.1,hid), requires_grad=True)
    h  = pnp.array(rng.normal(0,0.3,hid+1), requires_grad=True)
    def fwd(p, X):
        return _head(pnp.tanh(pnp.dot(pnp.array(X), p[0]) + p[1]), p[2])
    return fwd, [W1, b1, h], N_QUBITS*hid + hid + hid + 1

def train(kind, Xtr, ytr, Xte, yte, seed, steps=120, batch=48, lr=0.12, track_grad=False):
    rng = np.random.default_rng(seed)
    fwd, params, n_tr = build(kind, rng)
    opt = qml.AdamOptimizer(lr)
    grads = []
    for step in range(steps):
        idx = rng.choice(len(Xtr), min(batch,len(Xtr)), replace=False)
        Xb, yb = Xtr[idx], ytr[idx]
        out = opt.step(lambda *p: bce(fwd(list(p), Xb), yb), *params)
        params = list(out) if isinstance(out,(list,tuple)) else [out]
        if track_grad and kind=="full":
            g = qml.grad(lambda w_: bce(fwd([w_,params[1]], Xb), yb))(params[0])
            grads.append(float(np.abs(np.asarray(g)).mean()))
    acc = lambda X,y: float(((np.asarray(fwd(params,X))>0).astype(int)==y).mean())
    return acc(Xte,yte), acc(Xtr,ytr), n_tr, grads
