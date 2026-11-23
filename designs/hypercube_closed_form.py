"""Does the global-qubit selection problem have a closed form? Brute force says yes.

Evidence for addendum 2 to designs/design_hypercube_global_qubits_EN.md,
written before the study's first measurement run. It uses the instance set of
the findability study -- seven families, three seeds, density 1.5 -- through
partition_topology.make_graph, so the graphs are the published ones and not
new ones.

Cost model, from addendum 1 and the hop measurement in hypercube_cost_probe.py,
in units of 2^(n-2) amplitude-hops:

    diagonal gate, any placement            0
    RX on a global qubit                    2
    CNOT, target global                     1   (control global or not)
    CNOT, target local                      0
    XX+YY, exactly one qubit global         1
    XX+YY, both qubits global               2   (two hops: a real detour)

What is checked here, on every registered cell:

  1. Separability. For the XX+YY family the cost of a global set S is claimed
     to equal sum of deg(v) over v in S, plus the constant 2|S| from the mixer.
     For the oriented CNOT family, sum of in-degree. If that identity holds,
     the objective is linear and separable in the chosen qubits, and the
     problem has no combinatorial content.

  2. The consequence. Exhaustive enumeration of all C(n, g) subsets must then
     be beaten by nothing, and in particular must be attained exactly by the
     rule "take the g qubits of lowest degree".

Run from the calculations/ directory of the repository.

Ramon Schweiss, QWeb (c) Research, 23 November 2026.
"""
import itertools
import sys

import numpy as np
import partition_topology as pt

FAMILIES = ["random", "ring", "path", "regular", "scale-free", "community",
            "grid"]
SEEDS = (0, 1, 2)
SIZES = (12, 16, 20)
GS = (2, 3, 4)
DENSITY = 1.5


def oriented(edges):
    """The orientation rule declared in addendum 1: lower index to higher."""
    return [(min(a, b), max(a, b)) for a, b in edges]


def cost_xy(edges, S, n):
    """XX+YY on every edge, plus a mixer rotation on every qubit."""
    c = 0
    for a, b in edges:
        k = (a in S) + (b in S)
        c += (1 if k == 1 else 2 if k == 2 else 0)
    return c + 2 * len(S)


def cost_cnot(edges, S, n):
    """One CNOT per oriented edge, plus a mixer rotation on every qubit."""
    c = sum(1 for _, t in oriented(edges) if t in S)
    return c + 2 * len(S)


def degrees(edges, n):
    d = [0] * n
    for a, b in edges:
        d[a] += 1
        d[b] += 1
    return d


def in_degrees(edges, n):
    d = [0] * n
    for _, t in oriented(edges):
        d[t] += 1
    return d


def main():
    print(__doc__)
    cells = ident = mismatch = rule_fail = 0
    worst_rule = 0
    for n in SIZES:
        m = int(round(DENSITY * n))
        for family in FAMILIES:
            for seed in SEEDS:
                E = pt.make_graph(family, n, m, seed)
                if E is None:
                    print(f"  no connected graph: {family} n={n} seed={seed}")
                    continue
                deg, ind = degrees(E, n), in_degrees(E, n)
                for g in GS:
                    for cost, weight, label in ((cost_xy, deg, "XY"),
                                                (cost_cnot, ind, "CNOT")):
                        cells += 1
                        best, opt = None, None
                        for S in itertools.combinations(range(n), g):
                            Ss = set(S)
                            c = cost(E, Ss, n)
                            # check 1: separability, cell by cell
                            if c - 2 * g != sum(weight[v] for v in Ss):
                                mismatch += 1
                            else:
                                ident += 1
                            if opt is None or c < opt:
                                best, opt = S, c
                        # check 2: the degree rule attains the optimum
                        rule = sorted(range(n), key=lambda v: (weight[v], v))[:g]
                        got = cost(E, set(rule), n)
                        if got != opt:
                            rule_fail += 1
                            worst_rule = max(worst_rule, got - opt)
                            print(f"  rule misses: {label} {family} n={n} "
                                  f"g={g} seed={seed}: {got} vs {opt}")

    print(f"\n  cells (family x graph x size x g)        {cells}")
    print(f"  subsets with cost = sum of degrees       {ident}")
    print(f"  subsets where that identity failed       {mismatch}")
    print(f"  cells where the degree rule missed       {rule_fail}")
    print(f"  worst miss, in units                     {worst_rule}")

    print("""
  The identity is why. For XX+YY the two cases combine as
  1*[one endpoint global] + 2*[both global] = |{a,b} and S|, so summing over
  edges gives sum of deg(v) over v in S. The detour that a second global qubit
  costs is exactly the overlap that an edge-counting model would have saved,
  and the two cancel. The objective is therefore linear and separable, the
  greedy rule by degree is exactly optimal, and there is nothing left to
  search. The same holds for the oriented family with in-degree.""")
    return 0 if (mismatch == 0 and rule_fail == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
