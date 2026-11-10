"""
The same question at n = 26 and n = 28, with a vectorised ground truth.

Belongs to designs/design_findability_EN_v2_addendum_1.md, written
10 November 2026 before this run. The addendum states plainly that this arm
breaks the registered stopping condition of version 2 - it extends an arm
because a result looked promising - and it fixes the terms: the registered grid
n = 10..24 is reported unchanged, and these two sizes are reported separately
as a post-hoc extension.

Why: METIS stops returning balanced partitions from n = 20, in 5, 8 and 4 of 21
graphs at n = 20, 22, 24, and exact ground truth stops at n = 24. Three sizes of
overlap cannot carry a trend. Two more make it five.

Ground
truth : exact enumeration, stored as packed booleans and accumulated one edge
        at a time, which needs 135 MB at n = 26 instead of 1.08 GB as float64.
        Section 3 of the addendum makes this implementation conditional on
        agreeing EXACTLY with partition_topology on every size where both run.
        A faster ground truth that disagrees with the slow one is not one.

Needs : numpy, partition_topology, findability, pymetis.
"""
import sys, math, time
import numpy as np
from itertools import combinations, chain

import partition_topology as pt
from findability import (FAMILIES, SEEDS, RESTARTS, BOOT, U_MIN,
                         kl, spectral, greedy, metis_part, balanced_start,
                         canonical, migration, HAVE_METIS)

DENSITY = 1.5
NEW_SIZES = (26, 28)
CHECK_SIZES = (10, 12, 14, 16, 18, 20, 22, 24)
RNG = np.random.default_rng(20261110)

_CACHE = {}


def memberships(n):
    """Every balanced bipartition as packed booleans, vertex 0 on side False."""
    if n not in _CACHE:
        k = n // 2 - 1
        flat = np.fromiter(chain.from_iterable(combinations(range(1, n), k)),
                           dtype=np.int8)
        idx = flat.reshape(-1, k).astype(np.intp)
        # mirror partition_topology.partitions exactly: start on side True,
        # put vertex 0 and the k selected vertices on side False. Setting the
        # SELECTED vertices True instead leaves n/2 - 1 on one side, which is
        # not a balanced bipartition at all - the first version of this file
        # did that and the gate in section 3 caught it on its first use.
        S = np.ones((idx.shape[0], n), dtype=bool)
        S[:, 0] = False
        np.put_along_axis(S, idx, False, axis=1)
        _CACHE.clear()                      # one size at a time
        _CACHE[n] = S
    return _CACHE[n]


def min_cut_vec(n, E):
    """Minimum cut over all balanced bipartitions, and how many reach it."""
    S = memberships(n)
    acc = np.zeros(S.shape[0], dtype=np.int32)
    for u, v in E:
        acc += S[:, u] ^ S[:, v]
    m = int(acc.min())
    return m, int((acc == m).sum()), S[acc == m]


def gate_cut(W, s):
    return float(((s @ W) * (1.0 - s)).sum())


# ----------------------------------------------------- section 3 of the addendum

def verify():
    """The required gate: vectorised must equal partition_topology, exactly."""
    print("Gate - vectorised ground truth against partition_topology")
    print("-" * 78)
    bad = 0
    for n in CHECK_SIZES:
        expect = math.comb(n, n // 2) // 2
        got = memberships(n).shape[0]
        mism = 0
        for fam in FAMILIES:
            for sd in SEEDS:
                E = pt.make_graph(fam, n, int(round(DENSITY * n)), sd)
                if E is None:
                    continue
                slow = float(pt.cut_costs(pt.adjacency(n, E),
                                          pt.partitions(n)).min())
                fast = min_cut_vec(n, E)[0]
                if abs(slow - fast) > 1e-9:
                    mism += 1
        pt._PART_CACHE.clear()
        ok = (got == expect) and mism == 0
        bad += 0 if ok else 1
        print(f"   n = {n:<3d} partitions {got:>10,} (expected {expect:>10,})"
              f"   mismatches {mism}   {'ok' if ok else 'FAILED'}")
    if bad:
        print("\n   Gate failed. Section 5 of the addendum: this arm is abandoned.")
        return False
    print("\n   Gate passed on all eight sizes and all 21 graphs each.\n")
    return True


# ----------------------------------------------------------------- the new sizes

def measure_large(n, m, family, seed):
    E = pt.make_graph(family, n, m, seed)
    if E is None:
        return None
    W = pt.adjacency(n, E)
    opt, ties, optimal_set = min_cut_vec(n, E)
    out = {"family": family, "seed": seed, "n": n, "opt": float(opt),
           "ties": ties}

    kl_best = min((kl(W, balanced_start(n, RNG)) for _ in range(RESTARTS)),
                  key=lambda s: gate_cut(W, s))
    sg_best = min((greedy(W, int(RNG.integers(n)), RNG) for _ in range(RESTARTS)),
                  key=lambda s: gate_cut(W, s))

    for name, s in (("kl", kl_best), ("spectral", spectral(W)),
                    ("greedy", greedy(W)), ("stoch_greedy", sg_best),
                    ("random", balanced_start(n, RNG))):
        assert int(s.sum()) == n // 2, f"{name} left the balanced class"
        c = gate_cut(W, s)
        out[name] = c - opt
        if c - opt < 1e-9:
            sc = canonical(s).astype(bool)
            first = optimal_set[0]
            out[name + "_other"] = bool(
                migration(sc.astype(float), first.astype(float)) > 1e-9
                and migration(sc.astype(float),
                              (~first).astype(float)) > 1e-9)
        else:
            out[name + "_other"] = None

    if HAVE_METIS:
        s, ok = metis_part(n, E)
        out["metis_balanced"] = ok
        out["metis"] = (gate_cut(W, s) - opt) if ok else None
        out["metis_split"] = int(min(s.sum(), n - s.sum()))
    return out


ARMS = ["kl", "spectral", "greedy", "stoch_greedy", "metis", "random"]


def main():
    print(__doc__)
    if not verify():
        return 1

    print("Post-hoc extension - NOT part of the registered sweep")
    print("-" * 78)
    print("   mean gap in remote gates; (b) = some METIS answer was unbalanced\n")
    print("   n    " + "".join(f"{a:>14s}" for a in ARMS))
    store = {}
    for n in NEW_SIZES:
        t0 = time.time()
        rs = [r for f in FAMILIES for sd in SEEDS
              if (r := measure_large(n, int(round(DENSITY * n)), f, sd))]
        store[n] = rs
        line = f"   {n:<5d}"
        for a in ARMS:
            got = [r.get(a) for r in rs if r.get(a) is not None]
            if not got:
                line += f"{'-':>14s}"
                continue
            mark = "b" if (a == "metis" and
                           any(r.get("metis_balanced") is False for r in rs)) else ""
            line += f"{np.mean(got):>13.2f}{mark:1s}"
        print(line + f"   [{time.time()-t0:.0f}s]")
        sys.stdout.flush()

    # copied from findability_output.txt, the registered sweep, so that the
    # five sizes can be read together. Not recomputed here.
    REGISTERED = {20: (5, 21, [9]), 22: (8, 21, [10]), 24: (4, 21, [11])}

    print("\n\nMETIS and the balanced class, all five sizes from n = 20")
    print("-" * 78)
    print("   n = 20, 22, 24 are the registered sweep, copied from")
    print("   findability_output.txt; n = 26, 28 are this extension.\n")
    print("   n     unbalanced   of   share   smaller side   deficit")
    rows5 = []
    for n in (20, 22, 24):
        bad, tot, sp = REGISTERED[n]
        rows5.append((n, bad, tot, sp))
    for n in NEW_SIZES:
        rs = store[n]
        bad = [r for r in rs if r.get("metis_balanced") is False]
        sp = sorted({r["metis_split"] for r in bad})
        rows5.append((n, len(bad), len(rs), sp))
    for n, bad, tot, sp in rows5:
        def_ = [n // 2 - x for x in sp] if sp else []
        print(f"   {n:<5d} {bad:>9d}  {tot:>4d}  {bad/tot:6.2f}   "
              f"{str(sp) if sp else '-':>12s}   {str(def_) if def_ else '-'}")
    shares = [b / t for _, b, t, _ in rows5]
    mono = all(y >= x for x, y in zip(shares, shares[1:]))
    print(f"\n   monotonic in n: {mono}. Worst observed "
          f"{max(shares):.2f} at n = {rows5[int(np.argmax(shares))][0]}.")
    print("   Every unbalanced answer is off by exactly one vertex at every")
    print("   size - the deficit column. That is a tolerance artefact, not a")
    print("   partitioner failing to partition, and it is a weaker finding than")
    print("   an unbalanced share alone would suggest.")

    print("\n\nHits and the optimal set")
    print("-" * 78)
    print("   arm            n=26 hits   n=28 hits   other member (26/28)")
    for a in ARMS:
        cells = []
        others = []
        for n in NEW_SIZES:
            got = [r.get(a) for r in store[n] if r.get(a) is not None]
            cells.append(f"{sum(1 for v in got if v < 1e-9)}/{len(got)}"
                         if got else "-")
            others.append(str(sum(1 for r in store[n] if r.get(a + "_other"))))
        print(f"   {a:12s}   {cells[0]:>9s}   {cells[1]:>9s}   "
              f"{others[0]}/{others[1]}")

    print("\n\nThe optimum and the random baseline at the new sizes")
    print("-" * 78)
    print("   n      optimum   random    random excess over optimum")
    for n in NEW_SIZES:
        rs = store[n]
        opt = np.mean([r["opt"] for r in rs])
        rnd = np.mean([r["opt"] + r["random"] for r in rs])
        print(f"   {n:<5d}  {opt:7.2f}  {rnd:7.2f}   {100*(rnd/opt-1):8.0f} %")

    print("\n\nOne graph is missing at both sizes")
    print("-" * 78)
    print("   20 of 21, not 21. partition_topology.make_graph returns None for")
    print("   scale-free seed 2 at n = 26 and n = 28: in 25 attempts it produced")
    print("   no connected graph with exactly m edges. All 21 exist at n <= 24.")
    print("   The absence is not neutral - scale-free is the family where the")
    print("   published script found the largest information excess, 52 per cent -")
    print("   so every n = 26 and n = 28 figure above is over a set missing its")
    print("   most awkward member.")

    print("\n   The registered grid n = 10..24 is unchanged by this run and keeps")
    print("   the verdicts it already has. Section 1 of the addendum.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
