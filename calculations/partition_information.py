"""
What is state knowledge worth when partitioning a distributed computation?

Joint work with Venkateswaran Ramamurthy, in progress.

Question : a scheduler can infer a partition from the circuit graph alone, or
           compute one from the running state. How much does the second buy?
Measure  : quantum mutual information I(a:b) = S(a) + S(b) - S(ab) across each
           pair, which is what a cut actually costs.

Findings : (1) with clear community structure the circuit graph already gives the
               optimal partition - the gap is zero;
           (2) without it the gap reaches 71 per cent;
           (3) the optimal partition changes almost every layer, but early changes
               are near-ties, so viability matters more than optimality;
           (4) a partition stays within 5 per cent of optimal for about one layer,
               which puts the staleness crossover near 130 m - considerably tighter
               than the 1.8 km estimated from an assumed 200-gate horizon.

Caveats  : one circuit family, ten qubits, fixed gamma and beta. Not general.
Needs    : numpy, scipy
Runtime  : about three minutes.
"""
import numpy as np, itertools, time
from scipy.stats import spearmanr

# ---------- Zustandssimulation ----------
def zz(psi,a,b,g,n):
    idx=np.indices([2]*n)
    return (psi.reshape([2]*n)*np.exp(-1j*g*(1-2*idx[a])*(1-2*idx[b]))).reshape(-1)

def rx(psi,a,beta,n):
    c,s=np.cos(beta),-1j*np.sin(beta); U=np.array([[c,s],[s,c]])
    t=np.moveaxis(psi.reshape([2]*n),a,0).reshape(2,-1)
    return np.moveaxis((U@t).reshape([2]+[2]*(n-1)),0,a).reshape(-1)

def vn(rho):
    ev=np.linalg.eigvalsh(rho).real; ev=ev[ev>1e-12]
    return float(-(ev*np.log2(ev)).sum())

def rdm(psi,keep,n):
    order=list(keep)+[i for i in range(n) if i not in keep]
    t=np.transpose(psi.reshape([2]*n),order).reshape(2**len(keep),-1)
    return t@t.conj().T

def mutual(psi,n):
    S1=[vn(rdm(psi,[i],n)) for i in range(n)]
    W=np.zeros((n,n))
    for a,b in itertools.combinations(range(n),2):
        W[a,b]=W[b,a]=S1[a]+S1[b]-vn(rdm(psi,[a,b],n))
    return W

def run_qaoa(n, edges, p, gamma=0.5, beta=0.4):
    psi=np.ones(2**n,dtype=complex)/np.sqrt(2**n)
    return [mutual((lambda s: s)(psi:=_layer(psi,edges,gamma,beta,n)), n) for _ in range(p)]

def _layer(psi, edges, gamma, beta, n):
    for a,b in edges: psi=zz(psi,a,b,gamma,n)
    for q in range(n): psi=rx(psi,q,beta,n)
    return psi

# ---------- Partitionierung ----------
def cut_cost(W, part):
    return sum(W[a,b] for a,b in itertools.combinations(range(len(part)),2) if part[a]!=part[b])

def best_partition(W, n):
    best=None; bestc=np.inf
    for sel in itertools.combinations(range(1,n), n//2-1):
        part=[0 if i in (0,)+sel else 1 for i in range(n)]
        c=cut_cost(W,part)
        if c<bestc: bestc,best=c,part
    return best,bestc

print(__doc__)
N=10
t0=time.time()

# ---------- Teil 1: Struktur gegen Zustand ----------
print("1 - Does the circuit graph already give the right partition?")
print("-"*70)
clean=[(0,1),(0,2),(1,2),(2,3),(1,4),(3,4),(5,6),(5,7),(6,7),(7,8),(6,9),(8,9),(4,5)]
A=np.zeros((N,N))
for a,b in clean: A[a,b]=A[b,a]=1
snaps=run_qaoa(N, clean, 6)
partA,_=best_partition(A,N)
print(f"  Graph with two communities and a single bridge (4,5).")
print(f"  Partition from structure: {partA}\n")
print("   layer   cost of structural cut   best cut from state    gap")
for L,W in enumerate(snaps,1):
    cA=cut_cost(W,partA); _,cB=best_partition(W,N)
    print(f"     {L}            {cA:.4f}                {cB:.4f}          {(cA-cB)/cA*100:5.1f} %")
print("\n  Zero throughout. Where the community structure is plain, the graph suffices.\n")

print("  Now the same on random graphs with no built-in structure:\n")
rng=np.random.default_rng(7)
ap=list(itertools.combinations(range(N),2))
print("   graph   edges   mean gap   max gap")
for g in range(4):
    m=int(rng.integers(12,20))
    edges=[ap[i] for i in rng.choice(len(ap),m,replace=False)]
    Ar=np.zeros((N,N))
    for a,b in edges: Ar[a,b]=Ar[b,a]=1
    sn=run_qaoa(N,edges,5)
    pa,_=best_partition(Ar,N)
    gaps=[]
    for W in sn:
        cA=cut_cost(W,pa); _,cB=best_partition(W,N)
        gaps.append((cA-cB)/cA*100 if cA>1e-12 else 0.0)
    print(f"     {g+1}      {m:3d}     {np.mean(gaps):6.2f} %   {max(gaps):6.2f} %")
print("\n  Without community structure, state knowledge is worth a great deal.\n")

# ---------- Teil 2: Viabilitaet statt Optimalitaet ----------
print("2 - How long does a partition stay usable?")
print("-"*70)
rng=np.random.default_rng(3)
edges=[ap[i] for i in rng.choice(len(ap),15,replace=False)]
snaps=run_qaoa(N,edges,14)
print("  The optimal partition changes almost every layer. But early on the")
print("  runner-up costs barely more, so the label changing means little.\n")
print("   layer   best    runner-up   difference")
for L,W in enumerate(snaps[:6],1):
    costs=sorted(cut_cost(W,[0 if i in (0,)+sel else 1 for i in range(N)])
                 for sel in itertools.combinations(range(1,N),N//2-1))
    print(f"     {L}     {costs[0]:.4f}   {costs[1]:.4f}      {(costs[1]-costs[0])/costs[0]*100:5.1f} %")
print("\n  So the question is not how long a partition stays optimal, but how long")
print("  it stays within an acceptable margin. That is the viability question.\n")

def tau_viable(snaps, tol):
    lives=[]
    for L0 in range(len(snaps)-1):
        part,_=best_partition(snaps[L0],N); life=0
        for L in range(L0+1,len(snaps)):
            _,best=best_partition(snaps[L],N)
            if best>1e-12 and (cut_cost(snaps[L],part)-best)/best>tol: break
            life+=1
        lives.append(life)
    return float(np.mean(lives))

print("   tolerance   layers a partition stays usable")
taus={}
for tol in (0.02,0.05,0.10,0.20):
    taus[tol]=tau_viable(snaps,tol)
    print(f"      {tol*100:3.0f} %            {taus[tol]:.2f}")

# ---------- Teil 3: Staleness ----------
print("\n3 - Information staleness = latency / change timescale")
print("-"*70)
print("  Venkat's quantity. Below one, the information outlives the round trip.")
print("  Above one, the answer is stale before it arrives.\n")
c=299_792_458; t_layer=len(edges)*60e-9
print(f"  {len(edges)} two-qubit gates per layer at 60 ns each = {t_layer*1e6:.2f} us per layer.\n")
print("   tolerance    tau       crossover distance")
for tol,t in taus.items():
    print(f"      {tol*100:3.0f} %     {t:.2f}         {t*t_layer*c/2:7.0f} m")
print("\n  Which is tighter than the 1.8 km quoted in the QWeb architecture article.")
print("  That figure assumed a 200-gate horizon; here the horizon is measured,")
print("  and comes out at roughly fifteen gates for this circuit family.")
print(f"\n  {time.time()-t0:.0f}s")
