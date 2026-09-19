"""
Is the viability horizon a property of the graph, and can it be seen before the
circuit runs?

Joint work with Venkateswaran Ramamurthy, in progress. Third in a series:
partition_information.py establishes the horizon at one size and one density,
partition_robustness.py varies size and density, this one adds topology and
asks whether the horizon can be predicted without simulating the circuit.

Venkat's framing, kept throughout: the network has an observable latency, the
computation has an evolving information horizon, viability exists where the two
remain compatible. The two clocks are reported separately - H_v in layers is the
information clock, microseconds per layer is the execution clock, and distance
is their product and an engineering consequence, not a primary quantity.

Findings : (0) the measure came first, and it was wrong. The earlier runs averaged
               the partition's lifetime over every starting layer of an eight-layer
               circuit. A lifetime cannot exceed what is left of the circuit, so
               that average is capped at half the depth, and it mixes starting
               early with starting late. Measured that way the horizon moves with
               the circuit depth - up for some families, down for others - and
               never settles. Measured once from the start it settles as soon as
               the circuit is longer than the horizon being measured - which for
               the longest-lived families is past layer 24, and at 48 layers holds
               for all but the occasional graph. Everything below uses the settled
               measure, so the numbers are not comparable with the earlier two
               scripts;
           (1) structure moves the horizon where size does not. At identical n and
               identical edge count, H_v differs by a factor of 17 between graph
               families - community and regular longest, random shortest. The
               earlier cap had compressed that to a factor of about 3;
           (2) it does not explain the graph-to-graph spread away, and makes it
               worse. Family membership accounts for 24 per cent of the variance
               between individual graphs, and the scatter inside one family is
               larger than its own mean. A single graph stays uninformative even
               when its family is known;
           (3) the density cancellation reported earlier is not general. Density
               shortens the horizon sharply for random graphs, leaves scale-free
               graphs about where they were, and LENGTHENS it for regular and
               community graphs, where added edges sit inside the groups and
               sharpen an existing split instead of blurring it. Only where it
               shortens do the two clocks pull against each other in distance;
           (4) Venkat's two questions get different answers, and neither is a
               single answer. Which partition is optimal is readable from the
               graph where the graph splits cleanly (76 per cent of layers for
               grids, 63 for community structure) and barely better than a guess
               where it does not (34 per cent for random graphs, 23 for
               scale-free). How long that partition survives is only weakly
               predictable from static features (cross-validated R2 of 0.24 for
               QAOA, 0.28 for Trotter), and leaving a whole family out costs
               little, so the signal that exists is not family recognition;
           (5) one quantity carries most of both answers: the graph's own
               normalised minimum balanced cut. It is the heaviest weight in the
               regression and correlates with the horizon and, more strongly, with
               the partition hit rate. Dropping the family built to have a clean
               cut weakens the first and leaves the second intact.

Reading  : on "does a computation possess an intrinsic information horizon that
           can be characterised before execution?" - partly, and less than the
           partition question. Structure predicts the horizon in the mean and not
           for the individual graph. The unexplained variance is the result here,
           because it says the missing quantity is not a static graph property.

Caveats  : two circuit families, one gate-time model, one tolerance, greedy edge
           colouring rather than optimal, balanced bipartitions only, and fixed
           circuit parameters. Seven topologies is not a survey of graphs, and the
           community family is built with the fewest bridges that keep it
           connected, which is the most favourable case for a durable partition.
           The Trotter warm-up is skipped by a threshold relative to each run's
           own maximum, which is a choice and not a measurement.

Needs    : numpy, scipy, scikit-learn
Runtime  : about five minutes.
"""
import numpy as np, itertools, time, zlib
from scipy.sparse.csgraph import connected_components, shortest_path
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_predict, KFold, LeaveOneGroupOut

C = 299_792_458
TOL = 0.05          # eine Partition gilt als brauchbar, solange ihr Schnitt
                    # hoechstens fuenf Prozent ueber dem bestmoeglichen liegt
GATE_NS = 60.0      # Dauer einer Gatterrunde
OVERHEAD_NS = 20.0  # Einzelqubit-Schicht
DEPTH = 48          # tief genug, dass kaum eine Partition die Schaltung ueberlebt
                    # und die Messung damit nicht an der Laenge haengt

# ----------------------------------------------------------------- Simulation
def zz(psi, a, b, g, n):
    idx = np.indices([2] * n)
    return (psi.reshape([2]*n) * np.exp(-1j*g*(1-2*idx[a])*(1-2*idx[b]))).reshape(-1)

def rx(psi, a, beta, n):
    c, s = np.cos(beta), -1j*np.sin(beta)
    U = np.array([[c, s], [s, c]])
    t = np.moveaxis(psi.reshape([2]*n), a, 0).reshape(2, -1)
    return np.moveaxis((U @ t).reshape([2] + [2]*(n-1)), 0, a).reshape(-1)

def vn(rho):
    ev = np.linalg.eigvalsh(rho).real
    ev = ev[ev > 1e-12]
    return float(-(ev * np.log2(ev)).sum())

def rdm(psi, keep, n):
    order = list(keep) + [i for i in range(n) if i not in keep]
    t = np.transpose(psi.reshape([2]*n), order).reshape(2**len(keep), -1)
    return t @ t.conj().T

def mutual(psi, n):
    """Gegenseitige Information I(a:b) = S(a) + S(b) - S(ab) fuer jedes Paar."""
    S1 = [vn(rdm(psi, [i], n)) for i in range(n)]
    W = np.zeros((n, n))
    for a, b in itertools.combinations(range(n), 2):
        W[a, b] = W[b, a] = S1[a] + S1[b] - vn(rdm(psi, [a, b], n))
    return W

def qaoa(n, edges, p, gamma=0.5, beta=0.4):
    psi = np.ones(2**n, dtype=complex) / np.sqrt(2**n)
    out = []
    for _ in range(p):
        for a, b in edges: psi = zz(psi, a, b, gamma, n)
        for q in range(n): psi = rx(psi, q, beta, n)
        out.append(mutual(psi, n))
    return out

def trotter(n, edges, steps, J=1.0, h=0.5, dt=0.15):
    psi = np.zeros(2**n, dtype=complex)
    psi[sum((1 << (n-1-i)) for i in range(n) if i % 2 == 1)] = 1.0
    out = []
    for _ in range(steps):
        for a, b in edges: psi = zz(psi, a, b, -J*dt, n)
        for q in range(n):  psi = rx(psi, q, h*dt, n)
        out.append(mutual(psi, n))
    return out

# ------------------------------------------------- Topologien bei gleichem m
def _fill(n, edges, m, rng):
    E = {tuple(sorted(e)) for e in edges}
    pool = [e for e in itertools.combinations(range(n), 2) if e not in E]
    rng.shuffle(pool)
    while len(E) < m and pool: E.add(pool.pop())
    return sorted(E)[:m]

def g_random(n, m, rng):
    ap = list(itertools.combinations(range(n), 2))
    return sorted(tuple(ap[i]) for i in rng.choice(len(ap), m, replace=False))

def g_ring(n, m, rng):
    return _fill(n, [tuple(sorted((i, (i+1) % n))) for i in range(n)], m, rng)

def g_path(n, m, rng):
    return _fill(n, [(i, i+1) for i in range(n-1)], m, rng)

def g_regular(n, m, rng):
    """Moeglichst gradregulaer: immer die Kante zwischen den zwei schwaechsten Knoten."""
    E, deg = set(), np.zeros(n, int)
    pool = list(itertools.combinations(range(n), 2))
    while len(E) < m:
        rng.shuffle(pool)
        pool.sort(key=lambda e: deg[e[0]] + deg[e[1]])
        for e in pool:
            if e not in E:
                E.add(e); deg[e[0]] += 1; deg[e[1]] += 1; break
        else:
            break
    return sorted(E)

def g_scalefree(n, m, rng):
    """Bevorzugte Anbindung - wenige stark verbundene Knoten, viele schwache."""
    E, deg = {(0, 1)}, np.ones(n)
    for v in range(2, n):
        k = max(1, min(v, int(round(m / n))))
        w = deg[:v] / deg[:v].sum()
        for t in rng.choice(v, size=min(k, v), replace=False, p=w):
            E.add(tuple(sorted((int(t), v)))); deg[t] += 1; deg[v] += 1
    return _fill(n, E, m, rng)

def g_community(n, m, rng, bridges=2):
    """Zwei Gruppen, dicht innen, so wenige Kanten dazwischen wie moeglich."""
    A, B = list(range(n//2)), list(range(n//2, n))
    inside = [tuple(sorted(e)) for e in itertools.combinations(A, 2)] + \
             [tuple(sorted(e)) for e in itertools.combinations(B, 2)]
    cross = [tuple(sorted((a, b))) for a in A for b in B]
    rng.shuffle(inside); rng.shuffle(cross)
    # reicht das Innere nicht fuer m Kanten, muessen mehr Bruecken her
    bridges = max(bridges, m - len(inside))
    E = set(cross[:min(bridges, m)])
    for e in inside:
        if len(E) >= m: break
        E.add(e)
    return sorted(E)

def g_grid(n, m, rng):
    r = int(round(np.sqrt(n)))
    while n % r: r -= 1
    c = n // r
    base = []
    for i in range(r):
        for j in range(c):
            if j+1 < c: base.append(tuple(sorted((i*c+j, i*c+j+1))))
            if i+1 < r: base.append(tuple(sorted((i*c+j, (i+1)*c+j))))
    if len(base) > m:
        rng.shuffle(base); base = base[:m]
    return _fill(n, base, m, rng)

TOPOLOGIES = {"random": g_random, "ring": g_ring, "path": g_path,
              "regular": g_regular, "scale-free": g_scalefree,
              "community": g_community, "grid": g_grid}

def adjacency(n, edges):
    A = np.zeros((n, n))
    for a, b in edges: A[a, b] = A[b, a] = 1.0
    return A

def make_graph(name, n, m, seed):
    """Zusammenhaengenden Graphen der gewuenschten Familie liefern, sonst None."""
    for k in range(25):
        rng = np.random.default_rng(seed * 131 + k)
        E = TOPOLOGIES[name](n, m, rng)
        if len(E) != m: continue
        if connected_components(adjacency(n, E), directed=False)[0] == 1:
            return E
    return None

# ------------------------------------------- Partitionen als Matrixprodukt
_PART_CACHE = {}
def partitions(n):
    """Alle ausgewogenen Zweiteilungen als 0/1-Matrix, Knoten 0 stets in Teil 0."""
    if n not in _PART_CACHE:
        rows = []
        for sel in itertools.combinations(range(1, n), n//2 - 1):
            v = np.ones(n); v[0] = 0
            for i in sel: v[i] = 0
            rows.append(v)
        _PART_CACHE[n] = np.array(rows)          # (K, n), Eintrag 1 = Teil B
    return _PART_CACHE[n]

def cut_costs(W, S):
    """Schnittkosten aller Partitionen auf einmal: sum_ab W[a,b] s_a (1-s_b)."""
    return ((S @ W) * (1.0 - S)).sum(1)

def cost_table(snaps, n):
    S = partitions(n)
    costs = np.array([cut_costs(W, S) for W in snaps])
    return costs, costs.min(1)

def life_from(costs, best, L0, tol=TOL):
    """Wie viele Schichten bleibt die in L0 beste Partition brauchbar?
    Zweiter Rueckgabewert: ob sie bis zum Schaltungsende durchhaelt und die
    Messung damit nach unten begrenzt ist."""
    k = int(costs[L0].argmin()); life = 0
    for L in range(L0 + 1, len(costs)):
        if best[L] > 1e-12 and (costs[L, k] - best[L]) / best[L] > tol: break
        life += 1
    return life, (L0 + 1 + life >= len(costs))

def h_start(costs, best, L0=0):
    """Das Mass, das zur Frage passt: einmal am Anfang partitionieren."""
    return life_from(costs, best, L0)

def h_mean(costs, best, L0=0):
    """Das frueher benutzte Mass: Mittel ueber alle Startschichten."""
    return float(np.mean([life_from(costs, best, L)[0]
                          for L in range(L0, len(costs) - 1)]))

def parallel_rounds(edges):
    """Gierige Kantenfaerbung - wie viele Gatterrunden laufen nacheinander?"""
    colour = {}
    for e in edges:
        used = {colour[f] for f in colour if set(f) & set(e)}
        c = 0
        while c in used: c += 1
        colour[e] = c
    return max(colour.values()) + 1

def warmup(snaps, n, frac=0.10):
    """Erste Schicht, in der ueberhaupt Information zwischen Qubits steht.

    Trotter startet in einem Produktzustand ohne jede Verschraenkung; diese
    toten Anfangsschichten gehoeren nicht in die Messung. QAOA startet in
    |+>^n und ist nach der ersten Schicht verschraenkt, braucht also meist
    nichts uebersprungen. Die Schwelle ist ein Anteil des Maximums dieses
    Laufs, nicht ein fester Wert: die mittlere paarweise Information faellt
    mit der Zahl der Paare, eine feste Schwelle wuerde dichte Graphen und
    grosse Systeme faelschlich verwerfen.
    """
    iu = np.triu_indices(n, 1)
    m = np.array([W[iu].mean() for W in snaps])
    if m.max() <= 1e-9: return None
    return int(np.argmax(m >= frac * m.max()))

# ------------------------------------------------ statische Graphmerkmale
def features(n, edges):
    """Alles hier ist aus dem Graphen allein ablesbar - keine Simulation."""
    A = adjacency(n, edges)
    deg = A.sum(1)
    ev = np.linalg.eigvalsh(np.diag(deg) - A)
    lam2, lammax = float(ev[1]), float(ev[-1])
    cc = []
    for i in range(n):
        nb = np.flatnonzero(A[i])
        if len(nb) < 2: cc.append(0.0); continue
        links = sum(A[a, b] for a, b in itertools.combinations(nb, 2))
        cc.append(2 * links / (len(nb) * (len(nb) - 1)))
    d = shortest_path(A, directed=False, unweighted=True)
    S = partitions(n)
    return dict(density=len(edges) / n,
                deg_spread=float(deg.std() / deg.mean()),
                lam2=lam2, gap=lam2 / lammax,
                clustering=float(np.mean(cc)),
                mean_path=float(d[np.triu_indices(n, 1)].mean()),
                graph_cut=float(cut_costs(A, S).min() / len(edges)),
                size=float(n))

FEATURE_NAMES = ["density", "deg_spread", "lam2", "gap",
                 "clustering", "mean_path", "graph_cut", "size"]

# ------------------------------------------------------------------ Messung
def tag(*parts):
    """Reproduzierbarer Startwert - Pythons hash() waere pro Lauf verschieden."""
    return zlib.crc32(repr(parts).encode()) % 100_000

def trial(name, n, m, seed, depth=DEPTH):
    edges = make_graph(name, n, m, seed)
    if edges is None: return None
    sq, st = qaoa(n, edges, depth), trotter(n, edges, depth)
    wq, wt = warmup(sq, n), warmup(st, n)
    if wq is None or wt is None: return None
    cq, bq = cost_table(sq, n)
    ct, bt = cost_table(st, n)
    hq, censq = h_start(cq, bq, wq)
    ht, censt = h_start(ct, bt, wt)
    rounds = parallel_rounds(edges)
    tl = (rounds * GATE_NS + OVERHEAD_NS) * 1e-9
    # Frage 1: trifft der Schnitt des Graphen den Schnitt der Information?
    kg = int(cut_costs(adjacency(n, edges), partitions(n)).argmin())
    hit = float(np.mean([(cq[L, kg] - bq[L]) / bq[L] <= TOL
                         for L in range(wq, len(cq)) if bq[L] > 1e-12]))
    return dict(topology=name, n=n, m=m, rounds=rounds, tl=tl,
                hq=float(hq), ht=float(ht), cens_q=censq, cens_t=censt,
                hq_mean=h_mean(cq, bq, wq), ht_mean=h_mean(ct, bt, wt),
                ratio=ht / hq if hq else np.nan,
                dq=hq * tl * C / 2, dt=ht * tl * C / 2,
                graph_cut_hit=hit, **features(n, edges))

def collect(name, n, m, reps, t, depth=DEPTH):
    return [r for g in range(reps)
            if (r := trial(name, n, m, 10_000*t + g, depth))]

def mean(rs, k): return float(np.mean([x[k] for x in rs]))

# --------------------------------------------------------------------- Lauf
def main():
    print(__doc__)
    t0 = time.time()

    print("1 - The measure had to be fixed before the matrix meant anything")
    print("-" * 78)
    print("  Earlier runs averaged the partition's lifetime over every starting layer")
    print("  of an eight-layer circuit. Two things are wrong with that. A lifetime")
    print("  cannot exceed what is left of the circuit, so the average is capped at")
    print("  half the depth; and starting late is not the same question as starting")
    print("  early. Both show up as a dependence on a number nobody meant to choose.\n")
    print("  Same graphs throughout, QAOA, twelve qubits, eighteen edges, six graphs")
    print("  per family. 'capped' counts graphs whose partition outlived the circuit.\n")
    print("   topology      averaged over all starts        from the start, once")
    print("                 p=8   p=16  p=24  p=48      p=8   p=16  p=24  p=48   capped at 48")
    DEPTHS = (8, 16, 24, 48)
    for name in TOPOLOGIES:
        rows = []
        for g in range(6):
            E = make_graph(name, 12, 18, tag(name)*10_000 + g)
            if E is None: continue
            deep = qaoa(12, E, max(DEPTHS))
            w = warmup(deep, 12)
            if w is None: continue
            r = {}
            for p in DEPTHS:
                c, b = cost_table(deep[:p], 12)
                r[('m', p)] = h_mean(c, b, w)
                r[('s', p)], r[('c', p)] = h_start(c, b, w)
            rows.append(r)
        if not rows: continue
        a = "".join(f"{np.mean([r[('m', p)] for r in rows]):5.1f} " for p in DEPTHS)
        # '>' markiert Spalten, in denen mindestens ein Graph die Schaltung ueberlebt
        s = "".join(f"{np.mean([r[('s', p)] for r in rows]):5.1f}"
                    f"{'>' if any(r[('c', p)] for r in rows) else ' '}" for p in DEPTHS)
        cap = sum(r[('c', max(DEPTHS))] for r in rows)
        print(f"   {name:12s}  {a}    {s}    {cap}/{len(rows)}")
    print("\n  The averaged measure moves with depth - up for some families, down for")
    print("  others - and never settles: it reports the circuit's length as much as")
    print("  the graph's dynamics. Measured once from the start, the number settles as")
    print("  soon as the circuit outlasts the horizon it is measuring - visible in the")
    print("  right-hand block, where a family stops moving once it is no longer capped.")
    print("  Past that point the families separate much further than the cap could show.")
    print("  Everything below uses the settled measure, which means the numbers here")
    print("  are not comparable with the two earlier scripts.")

    print("\n\n2 - Does structure matter, at identical size and identical edge count?")
    print("-" * 78)
    print(f"  Twelve qubits, eighteen edges, eight connected graphs per family,")
    print(f"  {DEPTH} layers. H_v is the information clock and is counted in layers;")
    print("  microseconds per layer is the execution clock; only their product is")
    print("  a distance.\n")
    print("   topology      H_v QAOA   H_v Trot   ratio   capped   rounds  us/layer   QAOA dist")
    sec1, ALL = {}, []
    for name in TOPOLOGIES:
        res = collect(name, 12, 18, 8, tag(name))
        if not res: continue
        sec1[name] = res; ALL += res
        print(f"   {name:12s}  {mean(res,'hq'):6.2f}    {mean(res,'ht'):6.2f}"
              f"    {np.nanmean([x['ratio'] for x in res]):5.2f}"
              f"    {sum(x['cens_q'] for x in res)}/{len(res)}"
              f"     {mean(res,'rounds'):5.1f}    {mean(res,'tl')*1e6:.2f}"
              f"     {mean(res,'dq'):5.0f} m")

    hi = max(sec1, key=lambda k: mean(sec1[k], 'hq'))
    lo = min(sec1, key=lambda k: mean(sec1[k], 'hq'))
    f = mean(sec1[hi], 'hq') / mean(sec1[lo], 'hq')
    allh = np.array([x['hq'] for v in sec1.values() for x in v])
    between = sum(len(v) * (mean(v, 'hq') - allh.mean())**2 for v in sec1.values())
    eta2 = between / ((allh - allh.mean())**2).sum()
    cv_in = np.mean([np.std([x['hq'] for x in v]) / mean(v, 'hq') for v in sec1.values()])
    rho_alg = float(spearmanr([mean(v, 'hq') for v in sec1.values()],
                              [mean(v, 'ht') for v in sec1.values()]).statistic)
    print(f"\n  Between families the horizon moves by a factor of {f:.0f} "
          f"({hi} longest, {lo} shortest),")
    print(f"  at the same n and the same m. The capped measure could only show a factor")
    print(f"  of about three here, so most of that separation was hidden by the cap.")
    print(f"  The two algorithms rank the families at Spearman {rho_alg:+.2f} - similarly,")
    print(f"  not identically, so the effect is not purely a property of either circuit.")
    print(f"\n  Family membership still explains only {eta2*100:.0f} % of the variance between")
    print(f"  individual graphs, and the scatter inside one family is {cv_in*100:.0f} % of its own")
    print("  mean. Knowing the family narrows the horizon; it does not determine it.")
    print("  A single graph stays uninformative even when its family is known.")

    print("\n\n3 - The matrix: algorithm x topology x density x size")
    print("-" * 78)
    print("  Five families, three densities, three sizes, five graphs per cell.")
    print("  Entries are H_v in layers, measured from the start: QAOA / Trotter.\n")
    MAT, SIZES, DENS = ["random", "ring", "regular", "scale-free", "community"], \
                       (10, 12, 14), (1.0, 1.5, 2.5)
    cells = {}
    print("   topology     " + "".join(f"  n={n} d={d}  " for n in SIZES for d in DENS))
    for name in MAT:
        row = f"   {name:12s}"
        for n in SIZES:
            for d in DENS:
                res = collect(name, n, int(round(d*n)), 5, tag(name, n, d))
                cells[(name, n, d)] = res; ALL += res
                row += (f" {mean(res,'hq'):5.1f}/{mean(res,'ht'):4.1f} "
                        if res else "     -/-    ")
        print(row)

    print("\n  What density does, per family (1.0 -> 2.5 edges per qubit, twelve qubits).")
    print("  The earlier run found the two clocks nearly cancelling in distance. Held")
    print("  against other structures, that turns out not to be general.\n")
    print("   topology      layer duration   H_v QAOA    QAOA distance   graph cut")
    signs = {}
    for name in MAT:
        a, b = cells.get((name, 12, 1.0)), cells.get((name, 12, 2.5))
        if not a or not b: continue
        ftl, fh = mean(b,'tl')/mean(a,'tl'), mean(b,'hq')/mean(a,'hq')
        signs[name] = fh
        print(f"   {name:12s}     x{ftl:5.2f}        x{fh:5.2f}       x{mean(b,'dq')/mean(a,'dq'):5.2f}"
              f"        {mean(b,'graph_cut'):5.3f}")
    down = [k for k, v in signs.items() if v < 0.9]
    flat = [k for k, v in signs.items() if 0.9 <= v <= 1.1]
    up = [k for k, v in signs.items() if v > 1.1]
    rho_gc = float(spearmanr([signs[k] for k in signs],
                             [mean(cells[(k, 12, 2.5)], 'graph_cut') for k in signs]).statistic)
    print(f"\n  Density does not have one effect on the horizon; it has two, and which")
    print(f"  one applies depends on the structure. Shorter for "
          f"{', '.join(down) or 'no family'}; about unchanged")
    print(f"  for {', '.join(flat) or 'no family'}; longer for {', '.join(up) or 'no family'}.")
    print("  Only where it shortens do the two clocks pull against each other and the")
    print("  distance stay nearly put - which is what the earlier run, sampling random")
    print("  graphs only, was able to see.")
    print(f"\n  The rightmost column tracks the direction (Spearman {rho_gc:+.2f} across the")
    print("  five families, which on five points is a tendency and not a demonstration):")
    print("  where the graph's own minimum balanced cut is small, added edges sit inside")
    print("  the groups and sharpen an existing split instead of blurring it.")

    print("\n  And size, checked on the same data at 1.5 edges per qubit:\n")
    print("   topology       n=10    n=12    n=14")
    for name in MAT:
        v = [cells.get((name, n, 1.5)) for n in SIZES]
        if not all(v): continue
        print(f"   {name:12s}  " + "".join(f"{mean(c,'hq'):6.1f}  " for c in v))
    print("\n  No consistent direction - the earlier finding that size carries no trend")
    print("  survives the change of measure, which is worth having, because almost")
    print("  nothing else about the earlier numbers did.")

    print("\n\n4 - Venkat's question: can the horizon be characterised before execution?")
    print("-" * 78)
    print(f"  {len(ALL)} graphs in total. Everything used below is read off the graph;")
    print("  none of it requires running the circuit.\n")
    print("  4a - Is the optimal partition predictable from the graph alone?")
    print("       Take the graph's own balanced minimum cut and ask how often it stays")
    print("       within tolerance of the information-optimal cut, layer by layer.\n")
    print("       topology       share of layers within tolerance")
    for name in TOPOLOGIES:
        rs = [x for x in ALL if x['topology'] == name]
        if rs: print(f"       {name:12s}   {mean(rs,'graph_cut_hit')*100:5.1f} %")
    print(f"\n       overall {mean(ALL,'graph_cut_hit')*100:.1f} %")

    X = np.array([[x[f] for f in FEATURE_NAMES] for x in ALL])
    groups = np.array([x['topology'] for x in ALL])
    print("\n  4b - Is the horizon predictable from the graph alone?")
    print("       Ridge regression on the same features, cross-validated two ways:")
    print("       random folds, and leaving one whole topology family out.\n")
    print("       target      random 5-fold R2    leave-one-family-out R2")
    for label, key in (("H_v QAOA", 'hq'), ("H_v Trotter", 'ht')):
        y = np.array([x[key] for x in ALL])
        mdl = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
        r2 = lambda p: 1 - ((y - p)**2).sum() / ((y - y.mean())**2).sum()
        p1 = cross_val_predict(mdl, X, y, cv=KFold(5, shuffle=True, random_state=0))
        p2 = cross_val_predict(mdl, X, y, cv=LeaveOneGroupOut(), groups=groups)
        print(f"       {label:11s}    {r2(p1):8.2f}           {r2(p2):8.2f}")

    y = np.array([x['hq'] for x in ALL])
    w = make_pipeline(StandardScaler(), Ridge(alpha=1.0)).fit(X, y)[-1].coef_
    print("\n       Which features carry it (standardised weights, H_v QAOA):")
    for i in np.argsort(-np.abs(w))[:5]:
        print(f"         {FEATURE_NAMES[i]:12s} {w[i]:+6.2f}")

    print("\n  4c - One quantity does most of the work in both answers.")
    print("       The graph's own normalised minimum balanced cut - how cleanly the")
    print("       graph itself splits in two - against each measured quantity. The")
    print("       second column drops the family built to have a clean cut, to check")
    print("       that the relation is not carried by that family alone.\n")
    rest = [x for x in ALL if x['topology'] != 'community']
    gc, gcr = np.array([x['graph_cut'] for x in ALL]), np.array([x['graph_cut'] for x in rest])
    print("       against                               all   without community")
    for label, key in (("H_v QAOA", 'hq'), ("H_v Trotter", 'ht'),
                       ("layers the graph cut wins", 'graph_cut_hit')):
        a = float(spearmanr(gc, [x[key] for x in ALL]).statistic)
        b = float(spearmanr(gcr, [x[key] for x in rest]).statistic)
        print(f"       {label:32s}  {a:+.2f}        {b:+.2f}")

    print("\n  Read together: the two questions have different answers, and neither has")
    print("  a single one. Which partition is optimal is readable from the graph where")
    print("  the graph splits cleanly and is barely better than a guess where it does")
    print("  not. How long that partition survives is only weakly predictable from")
    print("  static features - and leaving a whole family out costs little, so the")
    print("  signal that exists is not family recognition. It is one structural")
    print("  quantity, and most of the variance is still unaccounted for. That names")
    print("  what to look for next rather than settling it.")
    print(f"\n  {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
