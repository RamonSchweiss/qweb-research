"""
Does the partition go stale as fast when the cost is one that is really paid?

The viability horizon H_v is measured on a proxy: the sum of pairwise mutual
information across a balanced cut. gate_vs_state_partition.py showed that
for executing a circuit known in advance the right cost is the number of
remote gates, and that this cost never moves in QAOA. This script takes the
second candidate from that discussion, where the state really is the cost:

    distributed SIMULATION on two classical nodes. Split the qubits into two
    halves A and B. The state across the cut has Schmidt dimension up to
    2^S(A), with S(A) the entanglement entropy. That dimension is what the
    two nodes must hold and exchange - the quantity behind "What a Node
    Actually Holds".

The same QAOA circuits, the same seven families, the same 5 % tolerance and
the same rule as H_v: choose the best balanced cut after layer 1, count the
further layers during which it stays within 5 % of the best. The only change
is the cost: 2^S(A) instead of the mutual-information sum.

Where this sits : candidate 1 from the same discussion - circuits whose later
               gates depend on mid-circuit measurements - was checked by
               reading rather than by computing. In teleportation, measurement-
               based computing, error correction and adaptive phase estimation,
               what depends on a measurement is almost always a single-qubit
               correction or the choice of a measurement basis, often only
               tracked in software. Those cost no communication across a cut.
               The two-qubit structure is fixed at compile time. So the
               candidate that remains is this one.

Findings : (1) the partition lasts far longer on the real cost. Median horizon
               on 2^S is 9.5 layers at ten qubits against 2.5 for H_v, and
               22.5 against 4.5 at twelve qubits, where half the graphs never
               lose the partition within 24 layers;
           (2) the two horizons point the same way. They rank together at
               about 0.35-0.4 inside a family and 0.4-0.55 pooled, so H_v is
               informative - but systematically too pessimistic;
           (3) staleness is cheap on this cost. Keeping the cut chosen after
               layer 1 for the whole circuit costs a median 1-2 % more Schmidt
               dimension than following the optimum layer by layer, at most
               15-25 %;
           (4) weaker entangling parameters lengthen both horizons; at the
               weakest setting they coincide (median 23 layers each). Keeping
               the first cut then costs nothing in the median, but the tail
               grows (90th percentile 6-11 %, maximum 32-40 %), and the two
               horizons stop ranking together (within family 0.12-0.14).

Reading  : across the three measurements now in the repository - remote gates
           (gate_vs_state_partition.py), Schmidt dimension (this script) and
           pairwise mutual information (partition_topology.py) - only the
           proxy goes stale within a few layers. The fast staleness measured so
           far looks more like the volatility of the measure than of any cost.

Caveats  : ten and twelve qubits, one circuit family (QAOA), balanced
           bipartitions only, one tolerance. At this size the states approach
           maximal entanglement within the circuit, which compresses the
           differences between cuts; larger systems in an area-law regime could
           behave differently. The third candidate - link noise that hurts
           correlations across a cut more than local ones - is not tested.

Runtime : about five minutes, most of it the twelve-qubit run.
"""
import sys, pathlib
import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import partition_topology as pt

P = 24                               # layers, as in gate_vs_state_partition.py
SEEDS = range(6)
FAMILIES = ["random", "ring", "path", "regular", "scale-free", "community", "grid"]


def entropy_table_setup(n):
    """Qubit orderings that put side A (the side holding qubit 0) first."""
    sides = [np.where(r == 0)[0] for r in pt.partitions(n)]
    return [(len(A), list(A) + [q for q in range(n) if q not in A]) for A in sides]

def entropies(psi, n, setup):
    """Entanglement entropy S(A) in bits for every balanced bipartition."""
    t = psi.reshape([2] * n)
    out = np.empty(len(setup))
    for i, (k, order) in enumerate(setup):
        s = np.linalg.svd(np.transpose(t, order).reshape(2**k, -1),
                          compute_uv=False) ** 2
        s = s[s > 1e-14]
        out[i] = -(s * np.log2(s)).sum()
    return out

def evolve(n, edges, gamma, beta, setup):
    """Run QAOA; per layer return S(A) of every cut and the mutual information."""
    psi = np.ones(2**n, dtype=complex) / np.sqrt(2**n)
    ent, mi = [], []
    for _ in range(P):
        for a, b in edges: psi = pt.zz(psi, a, b, gamma, n)
        for q in range(n): psi = pt.rx(psi, q, beta, n)
        ent.append(entropies(psi, n, setup))
        mi.append(pt.mutual(psi, n))
    return np.array(ent), mi


def survey(n, gamma, beta):
    m = int(1.5 * n)
    setup = entropy_table_setup(n)
    rows = []
    for fam in FAMILIES:
        for seed in SEEDS:
            E = pt.make_graph(fam, n, m, seed)
            if E is None:
                continue
            ent, mi = evolve(n, E, gamma, beta, setup)
            cost = 2.0 ** ent                            # Schmidt dimension
            best = cost.min(1)
            h_s, censored = pt.h_start(cost, best)
            mc, mb = pt.cost_table(mi, n)
            h_v, _ = pt.h_start(mc, mb)
            k0 = int(cost[0].argmin())
            rows.append(dict(fam=fam, hs=h_s, cens=censored, hv=h_v,
                             keep=float(np.mean(cost[:, k0] / best) - 1),
                             s_end=float(ent[-1].min())))
    return rows

def within_family(rows):
    rs = []
    for fam in FAMILIES:
        sub = [r for r in rows if r["fam"] == fam]
        if len(sub) < 3:
            continue
        a, b = [r["hs"] for r in sub], [r["hv"] for r in sub]
        if len(set(a)) > 1 and len(set(b)) > 1:     # constant columns carry nothing
            rs.append(spearmanr(a, b)[0])
    return float(np.mean(rs)), len(rs)

def report(label, rows):
    hs = np.array([r["hs"] for r in rows]); hv = np.array([r["hv"] for r in rows])
    keep = np.array([r["keep"] for r in rows])
    wf, nf = within_family(rows)
    print(f"  {label}: {len(rows)} graphs, best-cut entropy at the end "
          f"{np.median([r['s_end'] for r in rows]):.2f} bits (median)")
    print(f"     horizon on 2^S    median {np.median(hs):5.1f}   "
          f"never broken within {P} layers: {sum(r['cens'] for r in rows)} of {len(rows)}")
    print(f"     H_v (mutual inf.) median {np.median(hv):5.1f}")
    print(f"     rank correlation  pooled {spearmanr(hs, hv)[0]:+.2f}, "
          f"within family {wf:+.2f} ({nf} families)")
    print(f"     keeping the first cut: extra Schmidt dimension median "
          f"{100*np.median(keep):.1f} %, 90th percentile {100*np.percentile(keep, 90):.0f} %,"
          f" max {100*keep.max():.0f} %\n", flush=True)


def main():
    print("Distributed simulation: how long does the first cut stay good on 2^S?\n")
    print("1. Standard QAOA parameters (gamma 0.5, beta 0.4), as for H_v")
    for n in (10, 12):
        report(f"n = {n}", survey(n, 0.5, 0.4))

    print("2. Weaker entangling parameters, n = 10")
    for g, b in ((0.15, 0.10), (0.05, 0.05)):
        report(f"gamma {g}, beta {b}", survey(10, g, b))

    print("  On the cost that distributed simulation actually pays, the partition")
    print("  chosen at the start stays good far longer than H_v says, and keeping")
    print("  it costs little. H_v points the right way but overstates staleness.")


if __name__ == "__main__":
    main()
