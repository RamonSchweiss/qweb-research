"""
Does the margin-horizon relation hold in a second circuit family?

EO-1 of the programme agreed with V. Ramamurthy: close the static result with
ONE robustness experiment rather than an endless sequence of families, keeping
every definition fixed and reporting effect size rather than significance.

Everything is as in the earlier scripts. The horizon H_v is the number of
layers the balanced cut chosen at the first informative layer stays within 5 %
of the best cut of the mutual-information graph. The margin is that layer's
(second best - best) / second best, so it is read from one layer and cannot
leak the answer. The only change is the circuit:

    QAOA      |+>^n, then cost and mixer layers          (the family so far)
    Trotter   a Neel product state, then Ising evolution (the new family)

Trotter starts in a product state, so the first layers carry no information
between qubits at all; those dead layers are skipped with the same warm-up
rule partition_topology already uses - the first layer reaching 10 % of the
run's own maximum. For QAOA that rule skips nothing.

Three families of interaction graph rather than seven, as agreed: random,
community and grid, which spanned the range in the earlier work. Twenty-four
seeds each rather than three, because a rank correlation over three graphs
carries no information; the bootstrap interval is reported so the reader can
see how much twenty-four still leaves open.

Findings : (1) the relation survives the change of circuit family. Within
               families, Trotter gives +0.26, +0.70 and +0.09 against QAOA's
               +0.20, +0.77 and +0.31 on the same graphs; pooled, +0.50
               against +0.66;
           (2) it survives in the same ORDER. Community graphs carry the
               relation in both circuits and carry it strongly, random and grid
               graphs carry it weakly in both. Whatever the margin is
               measuring, it is not an accident of the QAOA ansatz;
           (3) the effect size is large where the relation holds. In Trotter,
               the half of the community graphs with the larger margin has a
               median horizon of 39 layers against 10.5 for the other half;
           (4) two of the six intervals exclude zero. With twenty-four graphs
               per family the weak families remain compatible with no relation
               at all, and this experiment does not settle them.

Caveats  : ten qubits, one density, balanced bipartitions, one tolerance.
           Trotter horizons are longer than QAOA's, and 14 of 72 Trotter
           graphs are still viable when the circuit ends, so their horizons
           are lower bounds and the medians below understate them.

Runtime : about thirty seconds.
"""
import sys, pathlib
import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import partition_topology as pt

N, M = 10, 15                      # ten qubits, density 1.5
SEEDS = range(24)
FAMILIES = ["random", "community", "grid"]
_RNG = np.random.default_rng(7)


def measure(snaps, n):
    """Layer-0 margin and the horizon of the partition chosen there."""
    w = pt.warmup(snaps, n)                    # skip product-state layers
    if w is None:
        return None
    costs, best = pt.cost_table(snaps[w:], n)
    srt = np.sort(costs[0])
    margin = float((srt[1] - srt[0]) / srt[1]) if srt[1] > 1e-12 else 0.0
    hv, censored = pt.h_start(costs, best)
    return margin, hv, censored, w

def bootstrap(x, y, B=4000):
    """Percentile interval for the rank correlation, resampling graphs."""
    x, y = np.asarray(x), np.asarray(y)
    out = []
    for _ in range(B):
        i = _RNG.integers(0, len(x), len(x))
        if len(set(x[i])) > 1 and len(set(y[i])) > 1:
            out.append(spearmanr(x[i], y[i])[0])
    return np.percentile(out, [5, 95])

def study(label, circuit):
    print(f"\n  {label}")
    print("    family       n   margin   H_v     rho    90 % interval    "
          "H_v of the high-margin half / low half   censored  warm-up")
    pool_m, pool_h = [], []
    for fam in FAMILIES:
        ms, hs, cens, ws = [], [], 0, []
        for seed in SEEDS:
            E = pt.make_graph(fam, N, M, seed)
            if E is None:
                continue
            r = measure(circuit(E), N)
            if r is None:
                continue
            ms.append(r[0]); hs.append(r[1]); cens += r[2]; ws.append(r[3])
        ms, hs = np.array(ms), np.array(hs)
        lo_i, hi_i = bootstrap(ms, hs)
        cut = np.median(ms)
        hi = np.median(hs[ms >= cut])
        lo = np.median(hs[ms < cut]) if (ms < cut).any() else float("nan")
        print(f"    {fam:10s} {len(ms):3d}   {cut:6.3f} {np.median(hs):6.1f}  "
              f"{spearmanr(ms, hs)[0]:+.2f}   [{lo_i:+.2f}, {hi_i:+.2f}]"
              f"              {hi:5.1f} / {lo:5.1f}                {cens:3d}"
              f"       {int(np.median(ws))}")
        pool_m += list(ms); pool_h += list(hs)
    lo_i, hi_i = bootstrap(pool_m, pool_h)
    print(f"    pooled     {len(pool_h):3d}                 "
          f"{spearmanr(pool_m, pool_h)[0]:+.2f}   [{lo_i:+.2f}, {hi_i:+.2f}]", flush=True)


def main():
    print(f"Does the margin rank with the horizon in a second circuit family?")
    print(f"n = {N}, m = {M}, {pt.DEPTH} layers, {len(list(SEEDS))} seeds per family,"
          f" tolerance {pt.TOL:.0%}")
    study("QAOA - the family measured so far", lambda E: pt.qaoa(N, E, pt.DEPTH))
    study("Trotter - the new family", lambda E: pt.trotter(N, E, pt.DEPTH))
    print("\n  The relation transfers, and it transfers with the same ranking of")
    print("  families: strong in community graphs, weak in random and grid ones,")
    print("  in both circuits. Two of the six intervals exclude zero, so the weak")
    print("  families are not settled by this experiment.")


if __name__ == "__main__":
    main()
