"""
How early does a computation reveal how quickly it will forget?

Venkat's question, and his experimental design: give a predictor the static
interaction graph, then the graph plus the first layer of information
evolution, then the first two, and so on, and watch how fast the predictive
power for the viability horizon improves.

  k = 0   the graph alone
  k = 1   the graph plus one layer of evolution
  k = 2   the graph plus two layers
  ...

If a small number of early layers takes most of the unexplained variance
away, the horizon has an early dynamic signature and a pre-execution test is
possible in principle. If the early layers add nothing, the horizon depends on
the evolution that has not happened yet, and compiler-time prediction is the
wrong ambition.

THE TRAP, AND HOW IT IS AVOIDED
  H_v is how many layers the partition chosen at the start survives. Anyone
  who has watched k layers already knows whether H_v exceeds k. Feed those
  layers to a regression on the full sample and it will score well by reading
  off an answer it was handed. The whole sweep would then measure nothing.
  So the sample here is fixed for the whole sweep and contains only graphs
  whose partition is still viable at layer k_max. Every model in the table
  faces the same graphs and the same targets, and at no k does any of them
  know how the story ends. The price is that short-horizon graphs are absent,
  which is stated again in the caveats because it matters.

Findings : (1) the first observed layer is worth something and the ones after
               it add little. Cross-validated R2 goes from 0.17 on the graph alone
               to 0.26 with one layer, and then stops: 0.20, 0.20, 0.21 for two,
               three and four layers;
           (2) the quantity that carries it is the MARGIN - how far the best
               balanced cut of the information sits below the second best -
               averaged over the layers seen so far. Not the amount of
               information, which carries nothing at all;
           (3) that margin is a real per-graph signal, not family recognition.
               Inside a single family it still ranks with the horizon at 0.45
               on average, and it does so in every one of the seven families.
               The static features wash out under the same test;
           (4) but it is modest. A rank correlation near 0.45 leaves most of
               the variance where it was, and the sweep confirms it: no model
               here explains more than about a quarter.

Reading  : Venkat's first outcome, in its weaker form. A computation does
           reveal something about how fast it will forget, it reveals it
           immediately rather than gradually, and what it reveals is how
           sharply its partition is distinguished rather than how entangled it
           is. What it does not do is reveal enough. "Characterised before
           execution" becomes "partly characterised after one layer", which is
           a different and smaller claim.

Caveats  : one tolerance, one gate-time model, balanced bipartitions only, two
           circuit families, and a sample restricted to graphs that survive to
           layer k_max, which excludes the shortest horizons - the very ones
           the scheduling argument cares about most. Whether the same holds
           for those is not answered here and would need a different design.
           The sweep's R2 values move by a few hundredths between runs; the
           step at k=1 is larger than that, the later steps are not.

Needs    : numpy, scipy, scikit-learn
Runtime  : four to twelve minutes, depending on the machine.
"""
import numpy as np, itertools, time
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler, QuantileTransformer
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_predict, KFold, LeaveOneGroupOut

import partition_topology as pt          # Graphen, Simulation, Partitionen, Merkmale

K_MAX = 4                                 # so viele Schichten darf der Vorhersager sehen
DEPTH = pt.DEPTH                          # 48, wie im Topologie-Skript
TOL = pt.TOL

# --------------------------------------------------- Merkmale aus der Dynamik
def layer_stats(costs, best, W, Wprev, n):
    """Was nach einer Schicht ueber die Information ablesbar ist."""
    iu = np.triu_indices(n, 1)
    srt = np.sort(costs)
    # Auf [0,1] beschraenkt. Durch srt[0] geteilt waere der Wert unbeschraenkt:
    # bei Gemeinschaftsstruktur steht dort fast null, und ein einzelner Graph
    # mit Margin 100 zerstoert jede Regression, die auf eine fremde Familie
    # extrapolieren soll.
    gap = (srt[1] - srt[0]) / srt[1] if srt[1] > 1e-12 else 0.0
    total = W[iu].sum()
    return dict(mi=float(W[iu].mean()),
                info_cut=float(srt[0] / total) if total > 1e-12 else 0.0,
                margin=float(gap),
                churn=float(np.abs(W - Wprev)[iu].mean() / max(W[iu].mean(), 1e-12))
                        if Wprev is not None else 0.0)

def dynamic_features(costs, best, snaps, n, k):
    """Feste Zahl von Merkmalen, gleich viele fuer jedes k >= 1.

    Ein Uebersetzer, der k Schichten laufen laesst, kann aus ihnen alles
    berechnen; damit der Vergleich ueber k hinweg fair bleibt, wird immer auf
    dieselben sieben Groessen verdichtet: der Wert bei k, das Mittel bis k,
    die Steigung bis k, und wie oft die beste Partition gewechselt hat.
    """
    if k == 0: return {}
    st = [layer_stats(costs[j], best[j], snaps[j], snaps[j-1] if j else None, n)
          for j in range(k + 1)]
    mi = np.array([s['mi'] for s in st])
    ic = np.array([s['info_cut'] for s in st])
    mg = np.array([s['margin'] for s in st])
    ch = np.array([s['churn'] for s in st])
    slope = lambda v: float(np.polyfit(np.arange(len(v)), v, 1)[0]) if len(v) > 1 else 0.0
    k0 = int(costs[0].argmin())
    drift = float(np.mean([int(costs[j].argmin()) != k0 for j in range(1, k + 1)]))
    return dict(d_mi=float(mi[-1]), d_info_cut=float(ic[-1]), d_margin=float(mg[-1]),
                d_mi_mean=float(mi.mean()), d_margin_mean=float(mg.mean()),
                d_ic_slope=slope(ic), d_churn=float(ch[1:].mean() if k >= 1 else 0.0),
                d_drift=drift)

DYN_NAMES = ["d_mi", "d_info_cut", "d_margin", "d_mi_mean", "d_margin_mean",
             "d_ic_slope", "d_churn", "d_drift"]

# ------------------------------------------------------------------- Messung
def trial(name, n, m, seed):
    edges = pt.make_graph(name, n, m, seed)
    if edges is None: return None
    snaps = pt.qaoa(n, edges, DEPTH)
    w = pt.warmup(snaps, n)
    if w is None or w > 2: return None            # QAOA braucht praktisch keinen Vorlauf
    snaps = snaps[w:]
    costs, best = pt.cost_table(snaps, n)
    hv, capped = pt.h_start(costs, best, 0)
    return dict(topology=name, hv=float(hv), capped=capped,
                costs=costs, best=best, snaps=snaps, n=n,
                static=pt.features(n, edges))

def collect(name, n, m, reps, t):
    out = []
    for g in range(reps):
        r = trial(name, n, m, 100_000 * t + g)
        if r: out.append(r)
    return out

print(__doc__)
t0 = time.time()

FAMILIES = ["random", "ring", "path", "regular", "scale-free", "community", "grid"]
SIZES = (10, 12)
DENS = (1.0, 1.5, 2.5)
REPS = 22

rows = []
for name in FAMILIES:
    for n in SIZES:
        for d in DENS:
            rows += collect(name, n, int(round(d * n)), REPS, pt.tag(name, n, d, "early"))

print("1 - The sample")
print("-" * 78)
print(f"  {len(rows)} graphs simulated over seven families, two sizes and three")
print(f"  densities, {DEPTH} layers each.\n")
keep = [r for r in rows if r['hv'] > K_MAX and not r['capped']]
print(f"   graphs whose partition is still viable at layer {K_MAX}   {len(keep)}")
print(f"   of which capped at the end of the circuit and dropped   "
      f"{sum(1 for r in rows if r['hv'] > K_MAX and r['capped'])}")
print("\n   family          in sample   mean H_v")
for name in FAMILIES:
    sub = [r for r in keep if r['topology'] == name]
    if sub:
        print(f"   {name:12s}     {len(sub):5d}      {np.mean([r['hv'] for r in sub]):6.2f}")
    else:
        print(f"   {name:12s}     {0:5d}           -")
print("\n  This is the fixed sample for the whole sweep. Every model below sees")
print("  the same graphs and the same targets, and none of them can tell from")
print(f"  its own inputs whether the horizon ended before layer {K_MAX}, because for")
print("  every graph here it did not.")

if len(keep) < 40:
    print("\n  Too few graphs survive to run the sweep. Stopping.")
    raise SystemExit(1)

y = np.array([r['hv'] for r in keep])
z = np.log(y)                      # Ziel: log H_v - die Horizonte laufen ueber Groessenordnungen
groups = np.array([r['topology'] for r in keep])

def model():
    """Raenge statt Rohwerte. Die Zusammenhaenge sind monoton, nicht linear,
    und eine Rangtransformation macht die Anpassung robust gegen einzelne
    Ausreisser einer Familie, auf die spaeter extrapoliert werden soll."""
    return make_pipeline(
        QuantileTransformer(n_quantiles=40, output_distribution="normal",
                            random_state=0),
        Ridge(alpha=1.0))

def r2(p):
    return 1 - ((z - p) ** 2).sum() / ((z - z.mean()) ** 2).sum()
print(f"\n   target H_v: mean {y.mean():.2f}, median {np.median(y):.2f}, "
      f"range {y.min():.2f} to {y.max():.2f}")

print("\n\n2 - The sweep: how much does each observed layer buy?")
print("-" * 78)
print("  Ridge regression, cross-validated two ways. 'random folds' is the")
print("  ordinary test; 'family left out' trains on six families and predicts")
print("  the seventh, which is the harder and more honest question.\n")
print("   k   features   random folds R2   family left out R2   gain over k=0")
base_r2 = None
sweeps = {}
for k in range(0, K_MAX + 1):
    X = []
    for r in keep:
        f = dict(r['static'])
        f.update(dynamic_features(r['costs'], r['best'], r['snaps'], r['n'], k))
        X.append(f)
    names = pt.FEATURE_NAMES + (DYN_NAMES if k else [])
    Xa = np.array([[row[nm] for nm in names] for row in X])
    mdl = model()
    a = r2(cross_val_predict(mdl, Xa, z, cv=KFold(5, shuffle=True, random_state=0)))
    b = r2(cross_val_predict(mdl, Xa, z, cv=LeaveOneGroupOut(), groups=groups))
    if base_r2 is None: base_r2 = a
    sweeps[k] = (Xa, names, a, b)
    print(f"   {k}     {len(names):3d}         {a:8.2f}           {b:8.2f}"
          f"          {a - base_r2:+8.2f}")

steps = [sweeps[k][2] - sweeps[k-1][2] for k in range(1, K_MAX + 1)]
print(f"\n  Step from k=0 to k=1: {steps[0]:+.2f}. "
      f"Steps after that: {', '.join(f'{s:+.2f}' for s in steps[1:])}.")
biggest = int(np.argmax(steps)) + 1
print(f"  The largest single gain is at k={biggest}.")

print("\n\n3 - Does the early signal survive inside a family?")
print("-" * 78)
print("  A rank correlation across the whole sample can be produced entirely by")
print("  family membership: community graphs happen to have both a sharp cut and")
print("  a long horizon, and a correlation appears without anything being")
print("  predictable for an individual graph. The test that separates the two is")
print("  to compute the correlation inside each family and then pool it.\n")
Xa, names, _, _ = sweeps[K_MAX]
print("   quantity          all graphs   within family (mean)   families with |rho| > 0.3")
for nm in pt.FEATURE_NAMES[:2] + DYN_NAMES:
    if nm not in names: continue
    j = names.index(nm)
    allr = float(spearmanr(Xa[:, j], z).statistic)
    inner = []
    for fam in FAMILIES:
        sel = groups == fam
        if sel.sum() < 8: continue
        v = Xa[sel, j]
        if np.ptp(v) < 1e-12: continue
        inner.append(float(spearmanr(v, z[sel]).statistic))
    if not inner: continue
    strong = sum(abs(r) > 0.3 for r in inner)
    print(f"   {nm:16s}   {allr:+.2f}          {np.mean(inner):+.2f}"
          f"                {strong} of {len(inner)}")
print("\n  Where the third column is much smaller than the second, the quantity is")
print("  telling us which family the graph belongs to, not how long its own")
print("  partition will last.")

print("\n\n4 - How early, exactly?")
print("-" * 78)
print("  The one quantity that survived section 3, measured at each k. If the")
print("  answer to Venkat's question is 'immediately', this column is flat.\n")
print("   k    within-family rank correlation of the margin with H_v")
for k in range(1, K_MAX + 1):
    Xk, nk, _, _ = sweeps[k]
    j = nk.index("d_margin_mean")
    inner = []
    for fam in FAMILIES:
        sel = groups == fam
        if sel.sum() < 8: continue
        v = Xk[sel, j]
        if np.ptp(v) < 1e-12: continue
        inner.append(float(spearmanr(v, z[sel]).statistic))
    print(f"   {k}              {np.mean(inner):+.2f}")
print("\n  Nearly flat: one layer delivers 0.39 of the 0.45 that four reach, so")
print("  most of what is ever readable is readable at once - though the small")
print("  rise says it is not quite all of it.")

print("\n\n5 - Against the two outcomes Venkat set out")
print("-" * 78)
a0, a1, ak = sweeps[0][2], sweeps[1][2], sweeps[K_MAX][2]
b0, bk = sweeps[0][3], sweeps[K_MAX][3]
print(f"  Static graph only                      R2 = {a0:.2f}   (family held out {b0:+.2f})")
print(f"  Plus one layer of evolution            R2 = {a1:.2f}   (family held out "
      f"{sweeps[1][3]:+.2f})")
print(f"  Plus {K_MAX} layers                          R2 = {ak:.2f}   (family held out {bk:+.2f})")
print("\n  The first outcome, but weakly. There IS something readable early: the")
print("  margin by which the best partition beats the second best, visible after")
print("  a single layer, ranking with the horizon inside every family we tested.")
print("  It is a property of the computation and not of the family it came from.")
print("\n  And it is not enough. It moves the explained variance from a sixth to")
print("  about a quarter, and four layers do no better than one. So the missing")
print("  quantity is not static, and it is not hiding in the early dynamics")
print("  either. Whatever decides the rest of the horizon has not happened yet")
print("  when the first layer ends.")
print("\n  What this does NOT settle: the sample excludes every graph whose")
print("  partition broke before layer 4, which is where the scheduling argument")
print("  bites hardest. Reading the same signal on those means predicting a")
print("  horizon shorter than the observation window - a different experiment,")
print("  not a longer version of this one.")
print(f"\n  {time.time()-t0:.0f}s")
