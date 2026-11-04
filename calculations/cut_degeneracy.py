"""
How many cuts are equally good, and what it costs to change between them.

Belongs to designs/design_cut_degeneracy_EN.md, version 1, registered
4 November 2026 before this run. H1, H2 and H3 are measured as registered.
The registered OBJECTIVE is not measured, and section 4 of this printout says
why: it is vacuous as written, which is a defect in the registration and not a
result. Its replacement needs its own dated registration first.

The published measurement says the gate-optimal cut does not move: in 21 of 21
problem graphs the exact minimum gate cut is the same at the first layer and at
the last. That is a statement about the cut COST. This asks how many partitions
reach that cost, and what a scheduler pays to change between them.

Currency : one ebit per qubit moved between processors, as in staleness_cost.py.
           Changing from P to Q moves the qubits whose side differs, so the
           migration cost is the Hamming distance of the membership vectors,
           minimised over which processor holds which side. Both partitions
           being balanced, that distance is even and at least two for P != Q.

Ground
truth    : exact enumeration of every balanced bipartition, to n = 20
           (92,378 partitions). No heuristic result is ever used as the
           optimum, which is an invalidating condition in section 5 of the note.

Needs    : numpy, scipy, partition_topology.
Runtime  : a few minutes, dominated by the n = 20 enumerations.
"""
import sys
from itertools import combinations

import numpy as np

import partition_topology as pt

FAMILIES = ["random", "ring", "path", "regular", "scale-free", "community", "grid"]
SEEDS = (0, 1, 2)
SIZES = (10, 12, 14, 16, 18, 20)
DENSITY = 1.5
RESTARTS = 20                      # registered in section 6, not raised
H1_THRESHOLD = 4                   # qubits, registered in section 3
RNG = np.random.default_rng(20261104)


# ------------------------------------------------------------------- mechanics

def cut_of(W, s):
    return float(((s @ W) * (1.0 - s)).sum())


def balanced(s):
    return int(s.sum()) == len(s) // 2


def canonical(s):
    """Membership with qubit 0 on side 0, which is how partitions() prints."""
    return 1.0 - s if s[0] > 0.5 else s


def migration(p, q):
    """Qubits that must move to go from partition p to partition q, in ebits.

    The two processors are interchangeable, so either labelling of q is a valid
    realisation of it and the cheaper one is taken.
    """
    h = float((p != q).sum())
    return min(h, len(p) - h)


def kl(W, s):
    """Pairwise swaps to a local optimum, inside the balanced class.

    The sweep restarts whenever anything moves, so the two sides are never
    stale. Section 5 of the note records what the first version of this routine
    did instead, and why a run whose assertion fires is void.
    """
    s = s.copy()
    n = len(s)
    best = cut_of(W, s)
    moved = True
    while moved:
        moved = False
        A = [i for i in range(n) if s[i] == 0]
        B = [i for i in range(n) if s[i] == 1]
        for a in A:
            for b in B:
                t = s.copy()
                t[a], t[b] = 1.0, 0.0
                c = cut_of(W, t)
                if c < best - 1e-12:
                    s, best, moved = t, c, True
                    break
            if moved:
                break
    if not balanced(s):
        raise AssertionError("kl left the balanced class; this run is void")
    return s, best


def random_start(n):
    s = np.zeros(n)
    s[RNG.permutation(n)[: n // 2]] = 1.0
    return s


def measure(n, family, seed):
    """Everything about one graph. Returns None where the family has none."""
    m = int(round(DENSITY * n))
    E = pt.make_graph(family, n, m, seed)
    if E is None:
        return None
    W = pt.adjacency(n, E).astype(float)
    S = pt.partitions(n)
    c = pt.cut_costs(W, S)
    opt = float(c.min())
    O = S[c <= opt + 1e-9]
    D = len(O)

    diam = 0.0
    if D > 1:
        diam = max(migration(O[i], O[j]) for i, j in combinations(range(D), 2))

    # H2: what two independent randomised runs actually return
    reached = []
    for _ in range(RESTARTS):
        s, cc = kl(W, random_start(n))
        if cc <= opt + 1e-9:
            reached.append(canonical(s))
    realised = None
    if len(reached) > 1:
        realised = float(np.mean([migration(reached[i], reached[j])
                                  for i, j in combinations(range(len(reached)), 2)]))
    return {"D": D, "diam": diam, "realised": realised,
            "hits": len(reached), "opt": opt}


# ---------------------------------------------------------------------- report

def main():
    print(__doc__)

    data = {}
    for n in SIZES:
        for f in FAMILIES:
            for sd in SEEDS:
                r = measure(n, f, sd)
                if r is not None:
                    data[(n, f, sd)] = r

    # ------------------------------------------------------------------ 1
    print("1 - H1: can a re-partition be expensive while buying nothing?")
    print("-" * 78)
    print("  Registered: among graphs with D > 1, the diameter of the optimal")
    print("  set is at least 4 qubits - 8 ebits at zero gate benefit - for at")
    print("  least half of them, at every size. Per family, never pooled alone")
    print("  (section 4 of the note makes pooling an invalidating condition).\n")
    print(f"  {'family':<12}" + "".join(f"{'n=' + str(n):>11}" for n in SIZES))
    print(f"  {'':<12}" + "".join(f"{'D / diam':>11}" for _ in SIZES))
    for f in FAMILIES:
        cells = []
        for n in SIZES:
            rs = [data[(n, f, sd)] for sd in SEEDS if (n, f, sd) in data]
            if not rs:
                cells.append(f"{'-':>11}")
                continue
            cells.append(f"{np.mean([r['D'] for r in rs]):>4.1f} /"
                         f"{np.mean([r['diam'] for r in rs]):>5.1f}")
        print(f"  {f:<12}" + "".join(cells))

    print()
    print(f"  {'n':>4} {'graphs D>1':>12} {'diam >= 4':>12} {'share':>8} "
          f"{'H1':>10}")
    h1_all = True
    for n in SIZES:
        rs = [data[(n, f, sd)] for f in FAMILIES for sd in SEEDS
              if (n, f, sd) in data]
        nd = [r for r in rs if r["D"] > 1]
        if not nd:
            print(f"  {n:>4} {0:>12} {'-':>12} {'-':>8} {'vacuous':>10}")
            continue
        hit = sum(1 for r in nd if r["diam"] >= H1_THRESHOLD)
        share = hit / len(nd)
        ok = share >= 0.5
        h1_all &= ok
        print(f"  {n:>4} {len(nd):>12} {hit:>12} {share:>8.2f} "
              f"{'holds' if ok else 'FAILS':>10}")
    print(f"\n  H1 {'holds at every size' if h1_all else 'FAILS at least once'}.")

    # ------------------------------------------------------------------ 2
    print("\n\n2 - H2: is the realised cost below the diameter?")
    print("-" * 78)
    print("  Registered: the distance between the optimal partitions two")
    print("  independent randomised runs return is smaller than the diameter,")
    print("  because refinement from a random start does not sample the")
    print("  optimal set uniformly. Twenty starts per graph, as registered.\n")
    print(f"  {'n':>4} {'graphs':>8} {'mean diam':>11} {'mean realised':>15} "
          f"{'ratio':>7} {'spread over seeds':>19}")
    for n in SIZES:
        rs = [(f, sd, data[(n, f, sd)]) for f in FAMILIES for sd in SEEDS
              if (n, f, sd) in data]
        use = [(f, sd, r) for f, sd, r in rs
               if r["D"] > 1 and r["realised"] is not None]
        if not use:
            print(f"  {n:>4} {0:>8} {'-':>11} {'-':>15} {'-':>7} {'-':>19}")
            continue
        md = float(np.mean([r["diam"] for _f, _s, r in use]))
        mr = float(np.mean([r["realised"] for _f, _s, r in use]))
        # resolution: spread of the realised figure across graph seeds
        spreads = []
        for f in FAMILIES:
            v = [r["realised"] for g, s, r in use if g == f]
            if len(v) > 1:
                spreads.append(max(v) - min(v))
        res = float(np.mean(spreads)) if spreads else float("nan")
        print(f"  {n:>4} {len(use):>8} {md:>11.2f} {mr:>15.2f} "
              f"{mr / md if md else float('nan'):>7.2f} {res:>19.2f}")

    print()
    print("  'spread over seeds' is the resolution limit declared in section 6:")
    print("  the mean within-family range of the realised figure across the")
    print("  three graph seeds. A difference smaller than it is reported as")
    print("  unresolved, including where it agrees with a hypothesis.")

    # ------------------------------------------------------------------ 3
    print("\n\n3 - H3: does the family ordering by diameter follow the one by D?")
    print("-" * 78)
    print("  Registered: the ordering of families by diameter matches their")
    print("  ordering by D, at every size. Families with D = 1 have diameter 0")
    print("  by definition and are excluded, since they would co-rank for free.\n")
    print(f"  {'n':>4} {'families used':>15} {'Spearman rho':>14}")
    for n in SIZES:
        pairs = []
        for f in FAMILIES:
            rs = [data[(n, f, sd)] for sd in SEEDS if (n, f, sd) in data]
            if not rs:
                continue
            mD = float(np.mean([r["D"] for r in rs]))
            if mD <= 1.0 + 1e-9:
                continue
            pairs.append((mD, float(np.mean([r["diam"] for r in rs]))))
        if len(pairs) < 3:
            print(f"  {n:>4} {len(pairs):>15} {'too few':>14}")
            continue
        a = np.argsort(np.argsort([p[0] for p in pairs]))
        b = np.argsort(np.argsort([p[1] for p in pairs]))
        rho = float(np.corrcoef(a, b)[0, 1])
        print(f"  {n:>4} {len(pairs):>15} {rho:>14.2f}")

    # ------------------------------------------------------------------ 4
    print("\n\n4 - The registered objective is vacuous, and that is a defect")
    print("-" * 78)
    print("  Section 3 of the note registered this objective: an")
    print("  incumbent-preferring tie-break - among all exactly optimal")
    print("  partitions, return the one nearest the current assignment -")
    print("  reduces the realised migration cost to zero without giving up a")
    print("  crossing gate.")
    print()
    print("  It does, and it cannot do otherwise. If the incumbent is itself")
    print("  optimal, the nearest optimal partition to it IS it, at distance")
    print("  zero. No run can come out any other way. The same holds for a")
    print("  refinement warm-started at the incumbent: pairwise swapping only")
    print("  accepts strict improvements, so from an optimal partition it makes")
    print("  no move at all.")
    print()
    print("  This is an objective whose outcome was fixed before the")
    print("  measurement, which is the failure the design notes exist to")
    print("  prevent. It is reported as a WITHDRAWAL of the objective, not as")
    print("  a confirmation of it, and the defect is mine and in the")
    print("  registration rather than in the data.")
    print()
    print("  The non-vacuous question sits one step away: the interesting case")
    print("  is an incumbent that is NOT optimal, which the scoping run showed")
    print("  happens in 1 to 13 of 21 graphs depending on the heuristic. Then")
    print("  a warm-started refinement may or may not reach the optimum, and")
    print("  may or may not cost less to get there than a cold restart does.")
    print("  That has a real answer and is NOT measured here: it needs its own")
    print("  dated registration first, and measuring it in the same run that")
    print("  found the defect would be choosing the question after seeing the")
    print("  data.")

    print("\n" + "=" * 78)
    print("  Bounds, as registered in section 7: two parts, balanced")
    print("  bipartitions, one density, the interaction graph as WRITTEN, so")
    print("  nothing here speaks about routing. Registers above n = 20 are")
    print("  outside the enumeration ceiling and outside this note. The")
    print("  heuristic family is spectral-free random starts with pairwise")
    print("  refinement; METIS and KaHyPar are not tested. The oracle is")
    print("  assumed and not counted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
