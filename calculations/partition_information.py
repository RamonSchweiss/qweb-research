"""
What is state knowledge worth when partitioning a distributed computation?

Joint work with Venkateswaran Ramamurthy, in progress.

Question : a scheduler can infer a partition from the circuit graph alone, or
           compute one from the running state. How much does the second buy,
           and how quickly does it go stale?

Measures : the cut is priced by quantum mutual information I(a:b) = S(a)+S(b)-S(ab).
           The primary quantity is the VIABILITY TIME - the physical time over
           which a partition stays within an acceptable cost margin. Distance is
           derived from it through a latency model, rather than assumed.

Findings : (1) with clear community structure the circuit graph already gives the
               optimal partition - the gap is zero;
           (2) without it the gap reaches 71 per cent;
           (3) the optimal partition changes almost every layer, but early changes
               are near-ties, so viability matters more than optimality;
           (4) the viability time is about 0.4 us for QAOA and 2.1 us for a
               Trotterised evolution on the same graph - a factor between three
               and six, so the horizon depends on the algorithm and not on the
               hardware alone;
           (5) counting gates serially overstates the horizon by about three,
               because two-qubit gates on disjoint pairs run concurrently. The
               parallel round count is an edge colouring of the interaction graph.

Caveats  : two circuit families, ten qubits, one graph, one gate-time model.
           Real hardware adds readout and classical processing latency, which
           would shorten the permissible distance further.

SUPERSEDED: the viability time here is averaged over every starting layer of an
           eight-layer circuit. A lifetime cannot exceed what is left of the
           circuit, so that average is capped at four layers, and it moves with
           the circuit depth. partition_topology.py measures it once from the
           start on a circuit deep enough not to cap it. Where the two disagree,
           that one is the later measurement. This script is kept as the record
           of where the work stood, not as a current result.

Needs    : numpy, scipy
Runtime  : about one minute.
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

# ---------- Wie lange dauert eine Schicht wirklich? ----------
def parallel_rounds(edges):
    """Greedy edge colouring: each colour is one concurrently executable round."""
    colour={}
    for e in edges:
        used={colour[f] for f in colour if set(f)&set(e)}
        c=0
        while c in used: c+=1
        colour[e]=c
    return max(colour.values())+1

def layer_time(edges, n, t2=60e-9, t1=20e-9, serial=False):
    """Physical duration of one layer. Serial counting overstates it."""
    if serial: return len(edges)*t2 + n*t1
    return parallel_rounds(edges)*t2 + t1

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

def run_trotter(n, edges, steps, J=1.0, h=0.5, dt=0.15):
    """First-order Trotter for H = -J sum ZZ - h sum X, from a Neel state."""
    psi=np.zeros(2**n,dtype=complex)
    psi[sum((1<<(n-1-i)) for i in range(n) if i%2==1)]=1.0
    snaps=[]
    for _ in range(steps):
        for a,b in edges: psi=zz(psi,a,b,-J*dt,n)
        for q in range(n):  psi=rx(psi,q,h*dt,n)
        snaps.append(mutual(psi,n))
    return snaps

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

# ---------- Teil 3: Viabilitaetszeit und Staleness ----------
print("\n3 - The viability time, and the clock it is measured on")
print("-"*70)
rounds=parallel_rounds(edges)
t_ser=layer_time(edges,N,serial=True); t_par=layer_time(edges,N)
deg=np.zeros(N,int)
for a,b in edges: deg[a]+=1; deg[b]+=1
print(f"  The interaction graph has maximum degree {deg.max()}, and a greedy edge")
print(f"  colouring needs {rounds} rounds. So the {len(edges)} two-qubit gates of a layer do")
print(f"  not run one after another - they run in {rounds} concurrent rounds.\n")
print(f"    counting serially   {t_ser*1e6:.2f} us per layer")
print(f"    counting in rounds  {t_par*1e6:.2f} us per layer   ({t_ser/t_par:.1f}x shorter)\n")
print("  Which matters, because a layer is an algorithmic abstraction and the")
print("  scheduler experiences wall-clock time. The primary quantity should")
print("  therefore be a duration, not a layer count.\n")
print("   tolerance   layers   viability time")
for tol in (0.02,0.05,0.10,0.20):
    print(f"      {tol*100:3.0f} %      {taus[tol]:.2f}      {taus[tol]*t_par*1e6:6.2f} us")

print("\n  Distance then follows from a latency model rather than being assumed.")
print("  With signals at c and a round trip, staleness reaches one at:\n")
c=299_792_458
print("   tolerance   viability time   crossover distance")
for tol in (0.02,0.05,0.10,0.20):
    v=taus[tol]*t_par
    print(f"      {tol*100:3.0f} %       {v*1e6:6.2f} us          {v*c/2:6.0f} m")
print("\n  Staleness S = latency / viability time. Below one the information")
print("  arrives while it still describes the state; above one it does not.")
print("\n  Note how much the clock matters: the same layer counts give")
print(f"  {taus[0.05]*t_ser*c/2:.0f} m if gates are counted serially and {taus[0.05]*t_par*c/2:.0f} m if they are counted in rounds.")

# ---------- Teil 4: QAOA gegen Trotter ----------
print("\n4 - Does the algorithm change the answer?")
print("-"*70)
print("  Same graph, but a Trotterised time evolution instead of QAOA: the state")
print("  flows through the interaction structure rather than being stirred by it.\n")
tr=run_trotter(N, edges, 20)
iu=np.triu_indices(N,1)
start=next(L for L,W in enumerate(tr,1) if W[iu].mean()>0.02)
print(f"  The Neel start is a product state, so nothing is entangled at first.")
print(f"  Mutual information becomes appreciable at step {start}; measuring from there.\n")
print("   tolerance    QAOA      Trotter     ratio")
for tol in (0.02,0.05,0.10,0.20):
    tq=taus[tol]; tt=tau_viable(tr[start-1:], tol)
    print(f"      {tol*100:3.0f} %      {tq:.2f}       {tt:.2f}       {tt/tq:.1f}x")

print("\n  As durations, on the parallel clock:\n")
tl=layer_time(edges,N)
print("   tolerance      QAOA           Trotter        crossover distance")
for tol in (0.02,0.05,0.10,0.20):
    tt=tau_viable(tr[start-1:], tol)
    vq=taus[tol]*tl; vt=tt*tl
    print(f"      {tol*100:3.0f} %     {vq*1e6:5.2f} us        {vt*1e6:5.2f} us       {vq*c/2:4.0f} m  /  {vt*c/2:4.0f} m")

print("\n  A partition stays usable three to six times longer under time evolution")
print("  than under QAOA. On the parallel clock that is a viability time of about")
print("  0.4 microseconds against 2.1 - and a permissible separation of roughly")
print("  sixty metres against three hundred.")
print("\n  The reason is visible in the construction: each QAOA mixing layer stirs the")
print("  whole entanglement structure, while a time evolution lets it grow along the")
print("  couplings, gradually, with a front.")
print("\n  Which suggests the viability horizon is a property of the computation and")
print("  the hardware together. Network-level observables alone cannot determine it,")
print("  because they do not see the evolving state that sets it.")
print(f"\n  {time.time()-t0:.0f}s")
