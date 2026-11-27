"""What a re-partition costs when it buys nothing.

Registered run for designs/design_migration_cost_EN.md of 27 November 2026,
with its addendum 1 of the same day, which declares the two tolerances this
file needs and the note did not name.

Two arms, and the point of the note is that the first one needs no heuristic:

  Section 3, enumeration only. For each graph, O is the set of exactly optimal
  balanced bipartitions and M is the mean pairwise migration distance inside
  it: what a scheduler pays per re-solve for not preferring the assignment it
  already holds. No eigensolver, no random start, nothing to pin. H1, H2, H3.

  Section 4, the heuristic arm. Warm refinement from a pinned incumbent against
  twenty cold restarts, both charged the migration they still owe if they do
  not land on the optimum. H4 unconditional, H5 conditioned as A2.3 was, so
  that the two can never be read as one. Rules E and P of section 5 of the note
  pin the incumbent; a graph they cannot pin is reported ambiguous, never
  resolved by a choice.

Invalidating conditions, all from section 8 of the note:
  - a sampled relabelling that moves the incumbent VOIDS the run;
  - a heuristic optimum used as ground truth: never, enumeration only;
  - kl leaving the balanced class: asserted inside cut_degeneracy.kl;
  - more than one graph in five excluded as ambiguous at a size: that size's
    heuristic arm is reported not evaluable rather than measured on what
    survived.

Verdicts, from design_resolution_limit_EN.md: resolved only if BOTH the
granularity step g = 2 and a 95 per cent percentile bootstrap over graphs
exclude zero; bounded where both arms sit on the same floor; not evaluable
below five units, kept strictly apart from unresolved.

Usage
    python3 migration_cost.py             full run, store and report
    python3 migration_cost.py --report    report from the existing store

Needs   : numpy, partition_topology, findability_scoping, cut_degeneracy.
Runtime : minutes. Enumeration to n = 20 is 92,378 partitions per graph.
"""
import itertools
import json
import os
import sys
import time

import numpy as np

import partition_topology as pt
import findability_scoping as fs
import cut_degeneracy as cd

# ---------------------------------------------------------------- registered
SIZES = (12, 14, 16, 18, 20)          # section 9; n = 10 dropped
SEEDS = tuple(range(10))              # ten per family and size
FAMILIES = cd.FAMILIES                # the seven published families
DENSITY = 1.5
RESTARTS = 20                         # cold route
G = 2.0                               # granularity, one swap, section 2
BOOT = 2000                           # section 7
U_MIN = 5                             # section 7
TAU = 1e-6                            # rule E, section 5
PERMS = 20                            # relabelling gate, section 8
PERM_SEED = 20261127                  # declared
AMBIG_MAX = 0.20                      # section 6, one graph in five
# addendum 1, declared before this run:
EPS_TIE = 1e-9                        # rule P: ties in the Fiedler vector
T_MAX = 200_000                       # rule P: size of T beyond which ambiguous

STORE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "migration_cost_store.json")


# ------------------------------------------------------------------ geometry
def optimal_set(W, n):
    """Every exactly optimal balanced bipartition, by enumeration."""
    S = pt.partitions(n)
    c = pt.cut_costs(W, S)
    best = float(c.min())
    return S[c <= best + 1e-12], best


def mean_pairwise_migration(O):
    """M: mean migration distance over the pairs of the optimal set."""
    d = len(O)
    if d < 2:
        return 0.0
    tot = 0.0
    for i in range(d):
        for j in range(i + 1, d):
            tot += cd.migration(O[i], O[j])
    return tot / (d * (d - 1) / 2)


def nearest_optimal(s, O):
    """Migration still owed from s to the cheapest optimal partition."""
    return min(cd.migration(s, o) for o in O)


# ------------------------------------------------------- the pinned incumbent
def incumbent(W, n):
    """Rules E and P of section 5. Returns (partition, None) or (None, reason)."""
    L = np.diag(W.sum(1)) - W
    w, V = np.linalg.eigh(L)
    lam_max = float(w[-1])
    if lam_max <= 0:
        return None, "rule E: degenerate Laplacian"
    if (float(w[2]) - float(w[1])) / lam_max < TAU:
        return None, "rule E: eigenvector not determined"

    f = V[:, 1]
    order = np.argsort(f, kind="stable")
    half = n // 2
    v_lo, v_hi = f[order[half - 1]], f[order[half]]
    if v_hi - v_lo > EPS_TIE:
        s = np.ones(n)
        s[order[:half]] = 0.0
        return cd.canonical(s), None

    # Ties across the median: every balanced split consistent with the
    # ordering is a candidate, and only the cut may choose between them.
    v = 0.5 * (v_lo + v_hi)
    below = [i for i in range(n) if f[i] < v - EPS_TIE]
    tied = [i for i in range(n) if abs(f[i] - v) <= EPS_TIE]
    k = half - len(below)
    if k < 0 or k > len(tied):
        return None, "rule P: no consistent balanced split"
    import math
    if math.comb(len(tied), k) > T_MAX:
        return None, f"rule P: |T| exceeds {T_MAX}"

    cands = []
    for pick in itertools.combinations(tied, k):
        s = np.ones(n)
        for i in below:
            s[i] = 0.0
        for i in pick:
            s[i] = 0.0
        cands.append(cd.canonical(s))
    cuts = np.array([cd.cut_of(W, s) for s in cands])
    win = [cands[i] for i in np.flatnonzero(cuts <= cuts.min() + 1e-12)]
    uniq = {tuple(s.tolist()) for s in win}
    if len(uniq) > 1:
        return None, "rule P: minimum-cut split not unique"
    return win[0], None


def relabel_gate(W, n, base, rng):
    """Section 8, as refined by addendum 1 before this run.

    Returns "ok", "moved" or "ambiguous". The registered condition is that a
    relabelling which moves the incumbent to a DIFFERENT partition voids the
    run. A relabelling under which rules E or P no longer pin anything is a
    different thing: the rules disagree across labellings, which is the
    ambiguity they exist to report, so the graph is excluded and counted and
    the run continues. Addendum 1 draws that line, in advance.
    """
    for _ in range(PERMS):
        p = rng.permutation(n)
        inc, _why = incumbent(W[np.ix_(p, p)], n)
        if inc is None:
            return "ambiguous"
        back = np.zeros(n)
        back[p] = inc
        if not np.array_equal(cd.canonical(back), base):
            return "moved"
    return "ok"


# ----------------------------------------------------------------- the routes
def routes(W, n, inc, O, best, rng):
    """Warm from the incumbent against twenty cold restarts, both charged."""
    s_w, c_w = cd.kl(W, inc.copy())
    s_w = cd.canonical(s_w)
    cost_w = cd.migration(inc, s_w)
    hit_w = c_w <= best + 1e-12
    if not hit_w:
        cost_w += nearest_optimal(s_w, O)

    best_c, s_c = None, None
    for _ in range(RESTARTS):
        s0 = np.ones(n)
        s0[rng.permutation(n)[:n // 2]] = 0.0
        s1, c1 = cd.kl(W, s0)
        if best_c is None or c1 < best_c - 1e-12:
            best_c, s_c = c1, cd.canonical(s1)
    cost_c = cd.migration(inc, s_c)
    hit_c = best_c <= best + 1e-12
    if not hit_c:
        cost_c += nearest_optimal(s_c, O)
    return dict(warm=cost_w, cold=cost_c, hit_warm=bool(hit_w),
                hit_cold=bool(hit_c))


# -------------------------------------------------------------------- verdict
def verdict(d, lo, hi, units, floored):
    if units < U_MIN:
        return "not evaluable", f"fewer than {U_MIN} units"
    if floored:
        return "bounded", "both arms on the floor"
    t1 = abs(d) >= G
    t2 = (lo > 0) == (hi > 0)
    if t1 and t2:
        return "resolved", ""
    if not t1:
        return "unresolved", "below one granularity step"
    return "unresolved", "interval covers zero"


def boot(vals, rng):
    v = np.asarray(vals, float)
    if len(v) == 0:
        return 0.0, 0.0, 0.0
    m = float(v.mean())
    draws = rng.integers(0, len(v), size=(BOOT, len(v)))
    means = v[draws].mean(1)
    return m, float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


# ------------------------------------------------------------------- the run
def run():
    rng_perm = np.random.default_rng(PERM_SEED)
    recs, t0 = [], time.time()
    for n in SIZES:
        m = int(round(DENSITY * n))
        for fam in FAMILIES:
            for seed in SEEDS:
                E = pt.make_graph(fam, n, m, seed)
                if E is None:
                    continue
                W = pt.adjacency(n, E).astype(float)
                O, best = optimal_set(W, n)
                r = dict(family=fam, n=n, seed=seed, D=len(O), best=best,
                         M=mean_pairwise_migration(O))
                inc, why = incumbent(W, n)
                if inc is None:
                    r.update(ambiguous=True, reason=why)
                else:
                    g = relabel_gate(W, n, inc, rng_perm)
                    if g == "moved":
                        print("  INVALIDATING CONDITION: a sampled relabelling "
                              f"moved the incumbent at {fam} n={n} seed={seed}.")
                        print("  This run is void. Nothing is written.")
                        return 2
                    if g == "ambiguous":
                        r.update(ambiguous=True,
                                 reason="rules E/P do not pin it under "
                                        "relabelling")
                        recs.append(r)
                        continue
                    r.update(ambiguous=False, reason="")
                    opt_inc = bool(cd.cut_of(W, inc) <= best + 1e-12)
                    r["incumbent_optimal"] = opt_inc
                    if not opt_inc:
                        rng = np.random.default_rng(1000 * n + 10 * seed
                                                    + FAMILIES.index(fam))
                        r.update(routes(W, n, inc, O, best, rng))
                recs.append(r)
        print(f"  n={n:>2} done, {time.time() - t0:6.1f}s elapsed")
    with open(STORE, "w", encoding="utf-8") as fh:
        json.dump(recs, fh, indent=1, sort_keys=True)
    print(f"\n  {len(recs)} records written to {os.path.basename(STORE)}")
    return 0


# ---------------------------------------------------------------- the report
def report():
    with open(STORE, encoding="utf-8") as fh:
        recs = json.load(fh)
    rng = np.random.default_rng(PERM_SEED + 1)
    print(__doc__)

    print("1 - The grid, and what fell out of it")
    print("-" * 78)
    print(f"  {'n':>4} {'graphs':>7} {'D=1':>6} {'D>1':>6} {'ambiguous':>10} "
          f"{'inc optimal':>12} {'usable (sec 4)':>15}")
    for n in SIZES:
        g = [r for r in recs if r["n"] == n]
        amb = [r for r in g if r["ambiguous"]]
        use = [r for r in g if not r["ambiguous"]
               and not r.get("incumbent_optimal", True)]
        print(f"  {n:>4} {len(g):>7} {sum(r['D'] == 1 for r in g):>6} "
              f"{sum(r['D'] > 1 for r in g):>6} {len(amb):>10} "
              f"{sum(1 for r in g if r.get('incumbent_optimal')):>12} "
              f"{len(use):>15}")
    reasons = {}
    for r in recs:
        if r["ambiguous"]:
            reasons[r["reason"]] = reasons.get(r["reason"], 0) + 1
    print("\n  Why a graph was ambiguous:")
    if not reasons:
        print("    nowhere; rules E and P pinned every graph on this grid.")
    for k, v in sorted(reasons.items(), key=lambda kv: -kv[1]):
        print(f"    {v:>4}  {k}")

    print("\n\n2 - H1: is M at least one granularity step where D > 1?")
    print("-" * 78)
    print(f"  {'n':>4} {'D>1':>6} {'M>=2':>6} {'share':>7} {'median M':>10} "
          f"{'max M':>7}  H1")
    h1 = []
    for n in SIZES:
        g = [r for r in recs if r["n"] == n and r["D"] > 1]
        if len(g) < U_MIN:
            print(f"  {n:>4} {len(g):>6} {'-':>6} {'-':>7} {'-':>10} {'-':>7}"
                  f"  not evaluable")
            h1.append("not evaluable")
            continue
        ok = [r for r in g if r["M"] >= G - 1e-12]
        share = len(ok) / len(g)
        mm = [r["M"] for r in g]
        hit = "holds" if share >= 0.5 else "FAILS"
        h1.append(hit)
        print(f"  {n:>4} {len(g):>6} {len(ok):>6} {share:>7.2f} "
              f"{np.median(mm):>10.2f} {max(mm):>7.2f}  {hit}")

    print("\n\n3 - H2: does M rise with the register?")
    print("-" * 78)
    lo_g = [r["M"] for r in recs if r["n"] == SIZES[0] and r["D"] > 1]
    hi_g = [r["M"] for r in recs if r["n"] == SIZES[-1] and r["D"] > 1]
    print(f"  n={SIZES[0]}: {len(lo_g)} graphs, median M "
          f"{np.median(lo_g) if lo_g else float('nan'):.2f}")
    print(f"  n={SIZES[-1]}: {len(hi_g)} graphs, median M "
          f"{np.median(hi_g) if hi_g else float('nan'):.2f}")
    if len(lo_g) >= U_MIN and len(hi_g) >= U_MIN:
        d = float(np.median(hi_g) - np.median(lo_g))
        bl = [float(np.median(rng.choice(hi_g, len(hi_g))) -
                    np.median(rng.choice(lo_g, len(lo_g))))
              for _ in range(BOOT)]
        lo, hi = np.percentile(bl, [2.5, 97.5])
        v, why = verdict(d, lo, hi, min(len(lo_g), len(hi_g)), False)
        print(f"  difference of medians {d:+.2f}  95% [{lo:+.2f}, {hi:+.2f}]"
              f"  -> {v}  {why}")
    else:
        print("  -> not evaluable")

    print("\n\n4 - H3: is the family ordering of M stable across sizes?")
    print("-" * 78)
    orders = {}
    for n in SIZES:
        per = {}
        for fam in FAMILIES:
            g = [r["M"] for r in recs
                 if r["n"] == n and r["family"] == fam and r["D"] > 1]
            if len(g) >= U_MIN:
                per[fam] = float(np.median(g))
        if len(per) < 4:
            print(f"  n={n:>2}: only {len(per)} families with >= {U_MIN} "
                  f"graphs -> not evaluable")
            orders[n] = None
            continue
        o = sorted(per, key=lambda f_: -per[f_])
        orders[n] = o
        print(f"  n={n:>2}: " + " > ".join(f"{f_}({per[f_]:.1f})" for f_ in o))
    got = [o for o in orders.values() if o]
    if len(got) >= 2:
        common = set(got[0])
        for o in got[1:]:
            common &= set(o)
        seqs = {tuple(f_ for f_ in o if f_ in common) for o in got}
        print(f"\n  on the {len(common)} families present at every evaluable "
              f"size: {'SAME ordering' if len(seqs) == 1 else 'ORDERING MOVES'}")
        print(f"  H3: {'holds' if len(seqs) == 1 else 'FAILS'}")
    else:
        print("\n  H3: not evaluable")

    print("\n\n5 - H4 and H5: the heuristic arm")
    print("-" * 78)
    print(f"  {'n':>4} {'units':>6} {'warm':>7} {'cold':>7} {'d':>7} "
          f"{'95% interval':>20} {'verdict':>14}  which")
    for n in SIZES:
        g = [r for r in recs if r["n"] == n and not r["ambiguous"]
             and not r.get("incumbent_optimal", True) and "warm" in r]
        allg = [r for r in recs if r["n"] == n]
        amb = sum(1 for r in allg if r["ambiguous"])
        if allg and amb / len(allg) > AMBIG_MAX:
            print(f"  {n:>4} {'-':>6} {'-':>7} {'-':>7} {'-':>7} "
                  f"{'-':>20} {'not evaluable':>14}  "
                  f"{amb}/{len(allg)} ambiguous, over the one-in-five bar")
            continue
        for label, sub in (("H4 all", g),
                           ("H5 both hit",
                            [r for r in g if r["hit_warm"] and r["hit_cold"]])):
            if not sub:
                print(f"  {n:>4} {0:>6} {'-':>7} {'-':>7} {'-':>7} "
                      f"{'-':>20} {'not evaluable':>14}  {label}")
                continue
            dd = [r["cold"] - r["warm"] for r in sub]
            mw = float(np.mean([r["warm"] for r in sub]))
            mc = float(np.mean([r["cold"] for r in sub]))
            d, lo, hi = boot(dd, rng)
            floored = abs(mw - G) < 1e-9 and abs(mc - G) < 1e-9
            v, why = verdict(d, lo, hi, len(sub), floored)
            print(f"  {n:>4} {len(sub):>6} {mw:>7.2f} {mc:>7.2f} {d:>+7.2f} "
                  f"  [{lo:>+7.2f}, {hi:>+7.2f}] {v:>14}  {label} {why}")

    print("\n\n6 - What this run does not show")
    print("-" * 78)
    print("  Two parts, balanced bipartitions, one density, the interaction")
    print("  graph as written, no routing, n <= 20. Section 4 speaks about")
    print("  spectral bisection with pairwise refinement and about no other")
    print("  partitioner. M is the price of re-solving without preferring the")
    print("  incumbent; it is not the price of a layer, because whether the")
    print("  optimal SET moves between layers is not established - the")
    print("  published measurement says the optimal cut COST does not.")
    print("  That an incumbent-preferring tie-break pays zero instead is")
    print("  arithmetic and is not a finding of this run.")
    return 0


def main():
    if "--report" in sys.argv:
        return report()
    print("Registered run: migration cost, 27 November 2026")
    print("-" * 78)
    rc = run()
    if rc:
        return rc
    print()
    return report()


if __name__ == "__main__":
    sys.exit(main())
