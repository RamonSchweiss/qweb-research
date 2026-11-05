"""
Does telling the partitioner where the qubits already are make the move cheaper?

Belongs to designs/design_cut_degeneracy_EN_addendum_1.md, section A1.5,
registered 4 November 2026 before this run. Nothing here was chosen after seeing
data: the two routes, the withdrawal condition, the degenerate subset, the
invalidating condition and the stopping condition are all in A1.5.

Why this run exists. The objective registered in the note itself was vacuous:
if the incumbent partition is already optimal, the nearest optimal partition to
it is itself, and pairwise refinement started there makes no move. That was
withdrawn in A1.4, not confirmed. The non-vacuous case is an incumbent that is
NOT optimal, which the scoping run of 4 November showed is common: spectral
bisection misses the exact optimum on 4 to 13 of 21 graphs.

The objective, as registered : the incumbent is the partition spectral
                               bisection returns. From there, compare a
                               refinement WARM-STARTED at the incumbent against
                               a COLD restart from a random start. The warm
                               route reaches the optimum as often as the cold
                               one does, and at strictly lower migration cost
                               from the incumbent.

Withdrawal, fixed in advance  : if the difference in migration cost between the
                               two routes is smaller than the resolution limit
                               of section 6 of the note, measured the same way,
                               the objective is withdrawn as UNRESOLVED rather
                               than reported either way. If the warm route
                               reaches the optimum LESS often, it is withdrawn
                               outright, because a cheaper route to a worse cut
                               is not the claim.

Degenerate subset, declared   : graphs on which spectral bisection already
                               returns an optimal partition. There the incumbent
                               is optimal, the question collapses into A1.4, and
                               the case contributes nothing. Reported separately,
                               never pooled.

Invalidating condition        : using spectral bisection's own cut as the
                               optimum instead of the enumeration. Enumeration
                               only, to n = 20.

Needs    : numpy, scipy, partition_topology, and the two scripts this one
           builds on, so that no routine is reimplemented and allowed to drift.
Runtime  : a few minutes.
"""
import sys
from itertools import combinations

import numpy as np

import partition_topology as pt
import cut_degeneracy as cd                # kl, migration, canonical, cut_of
import findability_scoping as fs           # spectral

FAMILIES = cd.FAMILIES
SEEDS = cd.SEEDS
SIZES = cd.SIZES
DENSITY = cd.DENSITY
RESTARTS = cd.RESTARTS                     # 20, as registered
RNG = np.random.default_rng(20261105)


def random_start(n):
    s = np.zeros(n)
    s[RNG.permutation(n)[: n // 2]] = 1.0
    return s


def measure(n, family, seed):
    m = int(round(DENSITY * n))
    E = pt.make_graph(family, n, m, seed)
    if E is None:
        return None
    W = pt.adjacency(n, E).astype(float)
    S = pt.partitions(n)
    c = pt.cut_costs(W, S)
    opt = float(c.min())                   # enumeration, never the heuristic

    inc = cd.canonical(fs.spectral(W))
    inc_cut = cd.cut_of(W, inc)
    if inc_cut <= opt + 1e-9:
        return {"degenerate": True}        # incumbent already optimal

    # the warm route: refinement started at the incumbent
    pw, cw = cd.kl(W, inc.copy())
    warm_hits = cw <= opt + 1e-9
    warm_cost = cd.migration(inc, cd.canonical(pw))

    # the cold route: independent random starts, as in H2
    cold_hits, cold_costs = 0, []
    for _ in range(RESTARTS):
        pc, cc = cd.kl(W, random_start(n))
        if cc <= opt + 1e-9:
            cold_hits += 1
            cold_costs.append(cd.migration(inc, cd.canonical(pc)))
    return {"degenerate": False,
            "warm_hits": bool(warm_hits), "warm_cost": warm_cost,
            "cold_rate": cold_hits / RESTARTS,
            "cold_cost": float(np.mean(cold_costs)) if cold_costs else None,
            "excess": inc_cut - opt}


def main():
    print(__doc__)

    data = {}
    for n in SIZES:
        for f in FAMILIES:
            for sd in SEEDS:
                r = measure(n, f, sd)
                if r is not None:
                    data[(n, f, sd)] = r

    # --------------------------------------------------------------- 1
    print("1 - The declared degenerate subset, and how large it is")
    print("-" * 78)
    print("  Graphs where spectral bisection already returns an optimal")
    print("  partition. There the incumbent IS the destination and the")
    print("  question collapses into A1.4. Named before the run; reported")
    print("  here because a result that is mostly a subset of zeros has to")
    print("  say so.\n")
    print(f"  {'n':>4} {'graphs':>8} {'degenerate':>12} {'usable':>8} "
          f"{'share usable':>14}")
    usable_counts = {}
    for n in SIZES:
        rs = [data[(n, f, sd)] for f in FAMILIES for sd in SEEDS
              if (n, f, sd) in data]
        deg = sum(1 for r in rs if r["degenerate"])
        use = len(rs) - deg
        usable_counts[n] = use
        print(f"  {n:>4} {len(rs):>8} {deg:>12} {use:>8} {use / len(rs):>14.2f}")

    # --------------------------------------------------------------- 2
    print("\n\n2 - Does the warm route reach the optimum as often?")
    print("-" * 78)
    print("  The warm route is deterministic: on each usable graph it either")
    print("  reaches the exact optimum or it does not. The cold rate is the")
    print("  share of the twenty independent starts that reach it. If the warm")
    print("  route reaches it LESS often, A1.5 withdraws the objective")
    print("  outright.\n")
    print(f"  {'n':>4} {'usable':>8} {'warm reaches':>14} {'cold per start':>16} "
          f"{'warm >= cold':>14}")
    warm_ok = True
    for n in SIZES:
        rs = [data[(n, f, sd)] for f in FAMILIES for sd in SEEDS
              if (n, f, sd) in data and not data[(n, f, sd)]["degenerate"]]
        if not rs:
            print(f"  {n:>4} {0:>8} {'-':>14} {'-':>16} {'-':>14}")
            continue
        w = sum(1 for r in rs if r["warm_hits"]) / len(rs)
        c = float(np.mean([r["cold_rate"] for r in rs]))
        ok = w >= c - 1e-12
        warm_ok &= ok
        print(f"  {n:>4} {len(rs):>8} {w:>14.2f} {c:>16.2f} "
              f"{'yes' if ok else 'NO':>14}")

    # --------------------------------------------------------------- 3
    print("\n\n3 - Migration cost from the incumbent, both routes")
    print("-" * 78)
    print("  Qubits that must move to get from the incumbent to the partition")
    print("  the route returns, in ebits. Only graphs where BOTH routes reach")
    print("  the exact optimum are counted, because comparing the cost of")
    print("  arriving somewhere worse is not the registered comparison.\n")
    print(f"  {'n':>4} {'pairs':>7} {'warm':>8} {'cold':>8} {'diff':>8} "
          f"{'resolution':>12} {'verdict':>12}")
    verdicts = []
    for n in SIZES:
        rows = [(f, sd, data[(n, f, sd)]) for f in FAMILIES for sd in SEEDS
                if (n, f, sd) in data]
        use = [(f, sd, r) for f, sd, r in rows
               if not r["degenerate"] and r["warm_hits"]
               and r["cold_cost"] is not None]
        if not use:
            print(f"  {n:>4} {0:>7} {'-':>8} {'-':>8} {'-':>8} {'-':>12} "
                  f"{'no data':>12}")
            verdicts.append("no data")
            continue
        mw = float(np.mean([r["warm_cost"] for _f, _s, r in use]))
        mc = float(np.mean([r["cold_cost"] for _f, _s, r in use]))
        diff = mc - mw
        spreads = []
        for f in FAMILIES:
            v = [r["warm_cost"] for g, _s, r in use if g == f]
            if len(v) > 1:
                spreads.append(max(v) - min(v))
        res = float(np.mean(spreads)) if spreads else float("nan")
        if np.isnan(res):
            verdict = "no spread"
        elif abs(diff) < res:
            verdict = "UNRESOLVED"
        elif diff > 0:
            verdict = "warm cheaper"
        else:
            verdict = "warm dearer"
        verdicts.append(verdict)
        print(f"  {n:>4} {len(use):>7} {mw:>8.2f} {mc:>8.2f} {diff:>+8.2f} "
              f"{res:>12.2f} {verdict:>12}")

    print()
    print("  'resolution' is the limit of section 6, measured the same way as")
    print("  in A1.2: the mean within-family range of the warm figure across")
    print("  the three graph seeds. A difference smaller than it is unresolved,")
    print("  including where it agrees with the objective.")

    # --------------------------------------------------------------- 4
    print("\n\n4 - The verdict on the registered objective")
    print("-" * 78)
    if not warm_ok:
        print("  The warm route reaches the optimum less often than the cold")
        print("  one at at least one size. A1.5 withdraws the objective")
        print("  OUTRIGHT on that ground: a cheaper route to a worse cut is")
        print("  not the claim, and no cost comparison rescues it.")
    resolved = [v for v in verdicts if v in ("warm cheaper", "warm dearer")]
    unres = [v for v in verdicts if v == "UNRESOLVED"]
    print(f"  Cost comparison: {len(resolved)} of {len(verdicts)} sizes resolve,"
          f" {len(unres)} are unresolved.")
    if resolved:
        print(f"  Of those that resolve: "
              f"{sum(1 for v in resolved if v == 'warm cheaper')} warm cheaper, "
              f"{sum(1 for v in resolved if v == 'warm dearer')} warm dearer.")
    print()
    print("  Usable graphs per size:",
          ", ".join(f"n={n}: {usable_counts[n]}" for n in SIZES))
    print("  The usable set is what the declared degenerate subset leaves")
    print("  behind, and it is small. Where it is very small, the resolution")
    print("  limit is wide and the comparison cannot settle anything - which")
    print("  is a fact about the instrument, not a result about warm starts.")

    print("\n" + "=" * 78)
    print("  Bounds as registered: two parts, balanced bipartitions, one")
    print("  density, the interaction graph as written, enumeration to n = 20")
    print("  as the only ground truth, one heuristic family. The incumbent is")
    print("  spectral bisection and nothing else; a different single-shot")
    print("  heuristic would give a different incumbent and is not tested.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
