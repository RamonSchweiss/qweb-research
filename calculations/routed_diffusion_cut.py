"""
Does a cut-oblivious compiler realise the diffusion's cheap cut, or squander it?

Belongs to designs/design_diffusion_cut_cost_EN.md, section 7, which was
committed before this was run. The companion script
diffusion_cut_arithmetic.py establishes the logical side: the V-chain
decomposition of the diffusion operator has a minimum balanced cut of eight
two-qubit gates at every register size, under free placement of the qubits.
Eight is therefore what a perfect partitioner would find. This script asks
whether SABRE, which minimises total swaps and knows nothing about any module
boundary, lands near it.

The objective registered in section 6, before the run: a cut-oblivious router
on a realistic coupling map achieves a crossing fraction close to the logical
minimum, because the chain structure is local enough that minimising total
swaps also keeps traffic off the cut.

The stopping condition registered in section 10, evaluable without knowing
which way anything moves: with r the median routed crossing fraction, m the
logical minimum fraction and s the spread over router seeds, the objective is
retained at a size only if r - m < max(s, 0.05).

Declared before the run and not adjusted after it: the decomposition (explicit
V-chain over n-2 ancillae, each Toffoli written out in CX form), the two
coupling-map families and their generator, the register sizes, the router and
its heuristic, the trivial initial layout, the five router seeds, the contrast
workload, and the degeneracy rules.

Invalidating condition, from section 8: SABRE minimises total swaps and not
swaps across a declared boundary. Everything below therefore describes a
cut-oblivious router. It establishes no bound on what a cut-aware router could
achieve, and quoting it as "the cost of partitioning" would be describing the
router and calling it the algorithm.

Needs    : numpy, qiskit, partition_topology.py and routed_partition_orbit.py
           from calculations/.
Runtime  : about ten minutes, most of it enumerating bipartitions at P=24.
           The register range reaches n=13 by addendum 2 of 1 November; P=24
           is the largest size at which the bipartitions fit in memory.
"""
import os
import statistics
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
for cand in (HERE, os.path.join(HERE, "..", "calculations")):
    if os.path.isfile(os.path.join(cand, "partition_topology.py")):
        sys.path.insert(0, os.path.abspath(cand))
        break
import partition_topology as pt                                   # noqa: E402

# The coupling-map generators are imported rather than copied, so that the
# heavy-hex start-node rule is literally the one already published.
import routed_partition_orbit as orbit                            # noqa: E402
from diffusion_cut_arithmetic import diffusion_vchain             # noqa: E402

try:                                                              # noqa: E402
    import qiskit
    from qiskit import QuantumCircuit
    from qiskit.transpiler import CouplingMap, Layout, PassManager
    from qiskit.transpiler.passes import (
        ApplyLayout, EnlargeWithAncilla, FullAncillaAllocation, SabreSwap,
        SetLayout)
except ImportError:                       # same convention as the memQ
    qiskit = None                         # cross-check in gate_vs_state_partition.py

SIZES = (4, 5, 6, 7, 8, 9, 10, 11, 12, 13)   # data qubits n; P = 2n-2, 6 to 24
REGISTERED = (4, 5, 6, 7, 8, 9, 10, 11)   # the range the note itself declared
# Addendum 2 of 1 November extended the range to n=13 so that the heavy-hex arm
# could produce a verdict at all. Its section 7 requires the added sizes to be
# reported separately, so that the grid verdict already recorded in addendum 1
# is not quietly recounted.
TOPOLOGIES = ("heavy-hex", "grid")
SEEDS = (11, 23, 37, 53, 71)              # five router seeds, fixed here
HEURISTIC = "decay"
CONTRAST = ("community", "regular")       # QAOA layer families
CONTRAST_DENSITY = 1.5                    # edges per qubit
LOGICAL_CUT = 8                           # from diffusion_cut_arithmetic.py
SLACK = 0.05                              # section 10, declared, not a power calc


# ------------------------------------------------------------------ routing

def route(qc, cm, seed):
    """Route a circuit from the trivial layout and return its physical pairs.

    Every two-qubit gate in the output counts, inserted swaps included: a swap
    carrying a pair across a cut is exactly the cost in question.
    """
    init = Layout({qc.qubits[i]: i for i in range(qc.num_qubits)})
    pm = PassManager([
        SetLayout(init),
        FullAncillaAllocation(cm), EnlargeWithAncilla(), ApplyLayout(),
        SabreSwap(cm, heuristic=HEURISTIC, seed=seed, trials=1),
    ])
    out = pm.run(qc)
    pairs = []
    for ins in out.data:
        if len(ins.qubits) != 2:
            continue
        a = out.find_bit(ins.qubits[0]).index
        b = out.find_bit(ins.qubits[1]).index
        pairs.append((a, b) if a < b else (b, a))
    return pairs


def crossing(P, pairs, S):
    """Minimum over balanced bipartitions of (crossing gates) / (all gates).

    cut_costs with a doubly-counted weight matrix gives each crossing gate a
    weight of exactly one, which is the convention the companion script uses.
    """
    W = np.zeros((P, P))
    for a, b in pairs:
        W[a, b] += 1.0
        W[b, a] += 1.0
    lo = float(pt.cut_costs(W, S).min())
    return lo, lo / len(pairs)


# ----------------------------------------------------------------- the grid

def coupling(name, P):
    """Coupling map and description, by the rule already in the orbit script."""
    return orbit.topology(name, P)


def degeneracy(P, cm):
    """Why this size carries no information, or None.

    Two rules, both declared in section 9 and both mechanical: a subgraph whose
    diameter reaches half its size has no interior to keep traffic inside, and
    a tree has no edge that is not a cut edge.
    """
    edges = {tuple(sorted(e)) for e in cm.get_edges()}
    if len(edges) == P - 1:
        return "a tree: every edge is a cut edge"
    A = np.zeros((P, P))
    for a, b in edges:
        A[a, b] = A[b, a] = 1.0
    # breadth-first eccentricity, no scipy needed
    diam = 0
    for s in range(P):
        dist = [-1] * P
        dist[s] = 0
        frontier = [s]
        while frontier:
            nxt = []
            for u in frontier:
                for v in np.flatnonzero(A[u]):
                    if dist[v] < 0:
                        dist[v] = dist[u] + 1
                        nxt.append(int(v))
            frontier = nxt
        diam = max(diam, max(dist))
    if diam >= P / 2:
        return f"diameter {diam} reaches half of {P}: no interior"
    return None


def contrast_circuit(family, P):
    """One QAOA layer on a bounded-degree graph of the declared family."""
    m = int(round(CONTRAST_DENSITY * P))
    edges = pt.make_graph(family, P, m, pt.tag("diffusion-contrast", family, P))
    if edges is None:
        return None
    qc = QuantumCircuit(P)
    for a, b in edges:
        qc.rzz(0.5, a, b)
    return qc


# --------------------------------------------------------------------- run

def measure(qc, P, cm, S):
    """Median and spread of the crossing fraction over the declared seeds."""
    fr, gates, cuts = [], [], []
    for sd in SEEDS:
        pairs = route(qc, cm, sd)
        cut, f = crossing(P, pairs, S)
        fr.append(f); gates.append(len(pairs)); cuts.append(cut)
    return (statistics.median(fr), max(fr) - min(fr),
            statistics.median(gates), statistics.median(cuts))


def main():
    print(__doc__)
    if qiskit is None:
        print("qiskit is not installed; nothing to measure.")
        return

    print(f"Router SABRE/{HEURISTIC}, trivial initial layout, seeds {SEEDS}.")
    print(f"Logical minimum cut {LOGICAL_CUT} gates, from the companion script.")
    print(f"Stopping condition: retain where r - m < max(spread, {SLACK}).\n")

    verdicts = {}
    for name in TOPOLOGIES:
        print(f"\n{name}\n" + "-" * 78)
        print(f"  {'n':>3} {'P':>4} {'gates':>6} {'cut':>5} {'r':>7} "
              f"{'m':>7} {'r-m':>7} {'spread':>7} {'verdict':>10}   note")
        for n in SIZES:
            P = 2 * n - 2
            cm, desc = coupling(name, P)
            why = degeneracy(P, cm)
            S = pt.partitions(P)
            r, spread, gates, cut = measure(diffusion_vchain(n), P, cm, S)
            m = LOGICAL_CUT / gates
            if why:
                verdict, note = "degenerate", why
            else:
                keep = (r - m) < max(spread, SLACK)
                verdict = "retained" if keep else "WITHDRAWN"
                note = desc
                bucket = "registered" if n in REGISTERED else "added"
                verdicts.setdefault((name, bucket), []).append(keep)
            print(f"  {n:>3} {P:>4} {gates:>6.0f} {cut:>5.0f} {r:>7.3f} "
                  f"{m:>7.3f} {r - m:>+7.3f} {spread:>7.3f} "
                  f"{verdict:>10}   {note}")

    print("\n\nContrast: one QAOA layer per family at "
          f"{CONTRAST_DENSITY} edges per qubit")
    print("-" * 78)
    print("  Reported for context, not part of the stopping condition. The")
    print("  diffusion's interaction graph is a chain by construction; these")
    print("  are not, and community is built to split cleanly.\n")
    print(f"  {'family':>10} {'topology':>10} {'P':>4} {'gates':>6} "
          f"{'cut':>5} {'r':>7} {'spread':>7}")
    for family in CONTRAST:
        for name in TOPOLOGIES:
            for n in (7, 9, 11, 13):
                P = 2 * n - 2
                qc = contrast_circuit(family, P)
                if qc is None:
                    print(f"  {family:>10} {name:>10} {P:>4}   no connected "
                          f"graph at this size and density")
                    continue
                cm, _ = coupling(name, P)
                S = pt.partitions(P)
                r, spread, gates, cut = measure(qc, P, cm, S)
                print(f"  {family:>10} {name:>10} {P:>4} {gates:>6.0f} "
                      f"{cut:>5.0f} {r:>7.3f} {spread:>7.3f}")

    print("\n\nThe decision, by section 11, with the two ranges kept apart")
    print("-" * 78)
    print("  Addendum 2 extended the range to n=13 and requires the added")
    print("  sizes to be counted separately from the registered ones.\n")
    for name in TOPOLOGIES:
        for bucket in ("registered", "added"):
            v = verdicts.get((name, bucket), [])
            if not v:
                print(f"  {name:>10}  {bucket:>10}: every size degenerate, "
                      f"nothing decided")
            else:
                print(f"  {name:>10}  {bucket:>10}: retained at {sum(v)} of "
                      f"{len(v)} non-degenerate sizes")
    allv = [x for v in verdicts.values() for x in v]
    if allv and all(allv):
        print("\n  Retained everywhere. The cheap cut survives compilation, and")
        print("  the eight-ebit ledger entry is an engineering number rather")
        print("  than a bound.")
    elif allv and any(allv):
        print("\n  Retained in part. The result is a statement about where it")
        print("  was retained, named, and not about the operator in general.")
    else:
        print("\n  Withdrawn. The cheap cut exists in the circuit and is lost")
        print("  in routing, which is a finding about the compiler and is more")
        print("  interesting than the alternative.")
    print("\n  Cut-oblivious router throughout; see the invalidating condition.")


if __name__ == "__main__":
    main()
