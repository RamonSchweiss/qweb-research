"""
Does the viability-horizon result survive system size and graph density?

Joint work with Venkateswaran Ramamurthy, in progress.
Companion to partition_information.py, which establishes the effect at one size
and one density. This one varies both.

Findings : (1) the ratio between QAOA and Trotter viability times is 4 to 6 across
               eight to fourteen qubits, with no trend in system size - the spread
               between individual graphs is larger than the spread between sizes;
           (2) density has two opposing effects that nearly cancel. Denser graphs
               need more concurrent rounds, so layers take longer; but they also
               entangle faster, so the horizon shrinks. Over a fourfold range of
               density the permissible distance moves by a factor of only 1.5,
               and by almost exactly the same factor for both algorithms;
           (3) single graphs are not informative. Individual ratios range from
               1.0 to 19.5; only the average over several is stable.

Caveats  : two circuit families, one gate-time model, greedy edge colouring rather
           than optimal, and balanced bipartitions only.

SUPERSEDED: this inherits the capped, depth-dependent horizon from
           partition_information.py, and finding (2) above does not survive.
           The density cancellation holds for graphs without a distinguished
           cut - which is what random sampling produces - and reverses for
           graphs that have one. See partition_topology.py, which measures the
           horizon once from the start and varies the topology. This script is
           kept as the record of where the work stood, not as a current result.

Needs    : numpy
Runtime  : about three minutes.
"""
import numpy as np, itertools, time

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

def qaoa(n, edges, p, gamma=0.5, beta=0.4):
    psi=np.ones(2**n,dtype=complex)/np.sqrt(2**n); out=[]
    for _ in range(p):
        for a,b in edges: psi=zz(psi,a,b,gamma,n)
        for q in range(n): psi=rx(psi,q,beta,n)
        out.append(mutual(psi,n))
    return out

def trotter(n, edges, steps, J=1.0, h=0.5, dt=0.15):
    psi=np.zeros(2**n,dtype=complex)
    psi[sum((1<<(n-1-i)) for i in range(n) if i%2==1)]=1.0
    out=[]
    for _ in range(steps):
        for a,b in edges: psi=zz(psi,a,b,-J*dt,n)
        for q in range(n):  psi=rx(psi,q,h*dt,n)
        out.append(mutual(psi,n))
    return out

# ---------- Uhr und Partitionierung ----------
def parallel_rounds(edges):
    colour={}
    for e in edges:
        used={colour[f] for f in colour if set(f)&set(e)}
        c=0
        while c in used: c+=1
        colour[e]=c
    return max(colour.values())+1

def cut_cost(W,part):
    return sum(W[a,b] for a,b in itertools.combinations(range(len(part)),2) if part[a]!=part[b])

def best_partition(W,n):
    best=None; bestc=np.inf
    for sel in itertools.combinations(range(1,n), n//2-1):
        part=[0 if i in (0,)+sel else 1 for i in range(n)]
        c=cut_cost(W,part)
        if c<bestc: bestc,best=c,part
    return best,bestc

def tau_viable(snaps,n,tol=0.05):
    lives=[]
    for L0 in range(len(snaps)-1):
        part,_=best_partition(snaps[L0],n); life=0
        for L in range(L0+1,len(snaps)):
            _,best=best_partition(snaps[L],n)
            if best>1e-12 and (cut_cost(snaps[L],part)-best)/best>tol: break
            life+=1
        lives.append(life)
    return float(np.mean(lives))

C=299_792_458
def trial(n, m, seed):
    ap=list(itertools.combinations(range(n),2))
    rng=np.random.default_rng(seed)
    edges=[ap[i] for i in rng.choice(len(ap), m, replace=False)]
    sq=qaoa(n,edges,8); st=trotter(n,edges,20)
    iu=np.triu_indices(n,1)
    idx=[L for L,W in enumerate(st,1) if W[iu].mean()>0.02]
    if not idx: return None
    tq=tau_viable(sq,n); tt=tau_viable(st[idx[0]-1:],n)
    if tq<=0: return None
    tl=parallel_rounds(edges)*60e-9 + 20e-9
    return dict(rounds=parallel_rounds(edges), tl=tl, tq=tq, tt=tt,
                ratio=tt/tq, dq=tq*tl*C/2, dt=tt*tl*C/2)

print(__doc__)
t0=time.time()

print("1 - Does the effect survive system size?")
print("-"*72)
print("  Density held at 1.5 edges per qubit, six graphs per size.\n")
print("    n   edges   tau QAOA   tau Trotter   ratio (median)   QAOA distance")
for n in (8,10,12,14):
    m=int(round(1.5*n))
    res=[r for g in range(6) if (r:=trial(n,m,1000*n+g))]
    R=np.array([x['ratio'] for x in res])
    print(f"   {n:2d}     {m:3d}      {np.mean([x['tq'] for x in res]):5.2f}        "
          f"{np.mean([x['tt'] for x in res]):5.2f}         {R.mean():5.2f} ({np.median(R):.1f})"
          f"          {np.mean([x['dq'] for x in res]):4.0f} m")
print("\n  No trend in n. The spread between individual graphs is larger than the")
print("  spread between sizes, which is itself worth knowing: a single graph says")
print("  nothing. Individual ratios in these runs range from 1.0 to 19.5.\n")

print("2 - What does graph density do?")
print("-"*72)
print("  Twelve qubits, six graphs per density. Two effects pull against each other:")
print("  denser graphs need more concurrent rounds, so layers take longer; but they")
print("  also entangle faster, so the horizon shrinks.\n")
print("   density  edges  rounds  us/layer   tau QAOA  tau Trot   QAOA dist  Trot dist")
first=last=None
for d in (0.8,1.5,2.5,3.5):
    m=int(round(d*12))
    res=[r for g in range(6) if (r:=trial(12,m,int(d*1000)+g))]
    row=dict(d=d,m=m,r=np.mean([x['rounds'] for x in res]),tl=np.mean([x['tl'] for x in res]),
             tq=np.mean([x['tq'] for x in res]),tt=np.mean([x['tt'] for x in res]),
             dq=np.mean([x['dq'] for x in res]),dt=np.mean([x['dt'] for x in res]))
    if first is None: first=row
    last=row
    print(f"     {d:.1f}     {m:3d}    {row['r']:4.1f}     {row['tl']*1e6:.2f}       "
          f"{row['tq']:5.2f}     {row['tt']:5.2f}      {row['dq']:5.0f} m    {row['dt']:5.0f} m")

print(f"\n  Over a fourfold range of density:")
print(f"    layer duration grows by {last['tl']/first['tl']:.1f}x")
print(f"    the QAOA horizon shrinks by {last['tq']/first['tq']:.2f}x")
print(f"    and the distance - their product - moves by only {last['dq']/first['dq']:.2f}x")
print(f"\n  For Trotter the same three factors are {last['tl']/first['tl']:.1f}, "
      f"{last['tt']/first['tt']:.2f} and {last['dt']/first['dt']:.2f}.")
print("\n  The two effects very nearly cancel, and by almost the same amount for both")
print("  algorithms. The permissible distance is therefore far less sensitive to the")
print("  graph than either quantity is on its own - which makes it a better thing to")
print("  quote than the horizon in layers.")
print(f"\n  {time.time()-t0:.0f}s")
