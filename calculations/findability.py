"""
Does a real partitioner find the minimum balanced gate cut?

Belongs to designs/design_findability_EN_v2.md, registered 10 November 2026
before this run. Version 1 of that note made the layer question primary; reading
gate_vs_state_partition.py showed that question to be vacuous for QAOA, because
every layer applies the same gates and nothing can move. Version 2 therefore
asks the question that does vary: whether a heuristic reaches the exact minimum
balanced cut at all, and by how much it misses.

The objective is the GATE cut, which for QAOA is the minimum balanced cut of the
problem graph itself. It is the right objective and not a convenient one:
gate_vs_state_partition.py finding (3) shows that following the
information-optimal cut costs 22 per cent more remote two-qubit gates, because
the gate cut minimises exactly that quantity.

Ground
truth  : exact enumeration of every balanced bipartition, via
         partition_topology.partitions. No heuristic result is ever used as the
         optimum, which is an invalidating condition in section 9 of the note.

Ties   : where the optimum is a set rather than a point, a heuristic that
         returns a different member of that set has NOT missed. Hits and
         different-member hits are counted separately, as section 7 requires.

METIS  : does not guarantee exact balance. Unbalanced answers are reported
         OUTSIDE the comparison class, never as a negative gap.

Needs  : numpy, scipy, partition_topology, pymetis (optional).
Runtime: a few minutes; dominated by enumeration at n = 22 and n = 24.
"""
import sys
import numpy as np
from itertools import combinations

import partition_topology as pt

FAMILIES = ["random", "ring", "path", "regular", "scale-free", "community", "grid"]
SEEDS = (0, 1, 2)
PUBLISHED_N, PUBLISHED_M = 10, 15        # as in gate_vs_state_partition.py
SIZES = (10, 12, 14, 16, 18, 20, 22, 24)
DENSITY = 1.5
RESTARTS = 20                            # registered 4 November, not raised
BOOT = 2000
U_MIN = 5
RNG = np.random.default_rng(20261110)

try:
    import pymetis
    HAVE_METIS = True
except ImportError:                      # declared absence, not a silent drop
    HAVE_METIS = False


# --------------------------------------------------------------- cut machinery

def cut(W, s):
    """Cut cost of one partition, same formula as partition_topology.cut_costs."""
    return float(((s @ W) * (1.0 - s)).sum())


def canonical(s):
    """Side labels are arbitrary; put vertex 0 on side 0."""
    return s if s[0] == 0 else 1.0 - s


def migration(p, q):
    """One ebit per qubit moved, minimised over which processor holds which side."""
    p, q = canonical(p), canonical(q)
    return float(min(np.abs(p - q).sum(), np.abs(p - (1.0 - q)).sum()))


def balanced_start(n, rng):
    s = np.ones(n)
    s[rng.permutation(n)[: n // 2]] = 0.0
    return s


# ------------------------------------------------------------------ heuristics

def kl(W, s):
    """Kernighan-Lin with locking and best-prefix acceptance.

    Balance is preserved by construction: every move is a swap of one vertex
    from each side. The assertion is not decoration - on 4 November a mutating
    sweep with stale side lists left the balanced class and reported a cut
    BELOW the balanced optimum, which looked like a perfect result.
    """
    n = len(s)
    s = s.copy()
    while True:
        locked = np.zeros(n, bool)
        cur = s.copy()
        seq, total = [], 0.0
        for _ in range(n // 2):
            A = np.flatnonzero((cur == 0) & ~locked)
            B = np.flatnonzero((cur == 1) & ~locked)
            if len(A) == 0 or len(B) == 0:
                break
            same = cur[:, None] == cur[None, :]
            D = (W * (~same)).sum(1) - (W * same).sum(1)
            g = D[A][:, None] + D[B][None, :] - 2.0 * W[np.ix_(A, B)]
            i, j = np.unravel_index(int(np.argmax(g)), g.shape)
            a, b = int(A[i]), int(B[j])
            total += float(g[i, j])
            cur[a], cur[b] = 1.0, 0.0
            locked[a] = locked[b] = True
            seq.append((total, a, b))
        if not seq:
            break
        k = int(np.argmax([t for t, _, _ in seq]))
        if seq[k][0] <= 1e-12:
            break
        for _, a, b in seq[: k + 1]:
            s[a], s[b] = 1.0 - s[a], 1.0 - s[b]
        assert int(s.sum()) == n // 2, "KL left the balanced class"
    assert int(s.sum()) == n // 2, "KL left the balanced class"
    return s


def spectral(W):
    """Fiedler vector split at the median. Balanced by construction, no restarts."""
    n = W.shape[0]
    L = np.diag(W.sum(1)) - W
    V = np.linalg.eigh(L)[1]
    order = np.argsort(V[:, 1])
    s = np.zeros(n)
    s[order[n // 2:]] = 1.0
    assert int(s.sum()) == n // 2
    return s


def greedy(W, seed_vertex=None, rng=None):
    """Grow one side by always adding the vertex most attached to it."""
    n = W.shape[0]
    if seed_vertex is None:
        seed_vertex = int(np.argmax(W.sum(1)))
    side = [seed_vertex]
    rest = [v for v in range(n) if v != seed_vertex]
    while len(side) < n // 2:
        link = np.array([W[v, side].sum() for v in rest])
        best = np.flatnonzero(link == link.max())
        pick = int(rng.choice(best)) if rng is not None else int(best[0])
        side.append(rest.pop(pick))
    s = np.ones(n)
    s[side] = 0.0
    assert int(s.sum()) == n // 2
    return s


def metis_part(n, E):
    """METIS. Returns (partition, balanced?) - balance is NOT guaranteed."""
    adj = [[] for _ in range(n)]
    for a, b in E:
        adj[a].append(b)
        adj[b].append(a)
    s = np.array(pymetis.part_graph(2, adjacency=adj)[1], dtype=float)
    return s, int(s.sum()) == n // 2


# ------------------------------------------------------------------ one graph

def measure(n, m, family, seed):
    E = pt.make_graph(family, n, m, seed)
    if E is None:
        return None
    W = pt.adjacency(n, E)
    S = pt.partitions(n)
    costs = pt.cut_costs(W, S)
    opt = float(costs.min())
    optimal_set = S[costs <= opt + 1e-9]
    ties = len(optimal_set)

    def classify(s):
        """Gap, and whether a zero-gap answer is a different member of the set."""
        c = cut(W, s)
        gap = c - opt
        if gap > 1e-9:
            return gap, None
        sc = canonical(s)
        same_as_first = migration(sc, optimal_set[0]) < 1e-9
        return 0.0, (not same_as_first)

    out = {"family": family, "seed": seed, "n": n, "opt": opt, "ties": ties}

    # KL and stochastic greedy get the registered restart budget
    kl_best = min((kl(W, balanced_start(n, RNG)) for _ in range(RESTARTS)),
                  key=lambda s: cut(W, s))
    sg_best = min((greedy(W, int(RNG.integers(n)), RNG) for _ in range(RESTARTS)),
                  key=lambda s: cut(W, s))

    for name, s in (("kl", kl_best), ("spectral", spectral(W)),
                    ("greedy", greedy(W)), ("stoch_greedy", sg_best),
                    ("random", balanced_start(n, RNG))):
        gap, other_member = classify(s)
        out[name] = gap
        out[name + "_other"] = other_member

    if HAVE_METIS:
        s, ok = metis_part(n, E)
        out["metis_balanced"] = ok
        out["metis"] = (cut(W, s) - opt) if ok else None
        out["metis_split"] = int(min(s.sum(), n - s.sum()))
    return out


# ----------------------------------------------------------------- statistics

def boot_mean_ci(xs):
    """Percentile bootstrap over graphs, the declared unit of analysis."""
    xs = np.asarray([x for x in xs if x is not None], dtype=float)
    if len(xs) < U_MIN:
        return None, None, None, len(xs)
    draws = RNG.choice(xs, size=(BOOT, len(xs)), replace=True).mean(1)
    return float(xs.mean()), float(np.percentile(draws, 2.5)), \
        float(np.percentile(draws, 97.5)), len(xs)


def verdict(xs):
    """Resolution limit v2: granularity is exactly 1 remote gate."""
    mean, lo, hi, u = boot_mean_ci(xs)
    if mean is None:
        return f"not evaluable ({u} < {U_MIN} units)"
    if all(abs(x) < 1e-9 for x in xs if x is not None):
        return "exact zero in every graph"
    if mean < 1.0 and lo <= 0.0 <= hi:
        return f"unresolved (mean {mean:.2f} < granularity 1, CI {lo:.2f}..{hi:.2f})"
    if lo > 0.0:
        return f"resolved (mean {mean:.2f}, CI {lo:.2f}..{hi:.2f})"
    return f"unresolved (CI {lo:.2f}..{hi:.2f} contains zero)"


ARMS = ["kl", "spectral", "greedy", "stoch_greedy", "metis", "random"]


def main():
    print(__doc__)
    print(f"Restart budget: {RESTARTS} for KL and stochastic greedy; "
          f"spectral and greedy are deterministic (1).")
    print(f"METIS available: {HAVE_METIS}\n")

    # ------------------------------------------------- 1, the published config
    print("1 - The published configuration: n = 10, m = 15, the same 21 graphs")
    print("-" * 78)
    rows = [r for f in FAMILIES for sd in SEEDS
            if (r := measure(PUBLISHED_N, PUBLISHED_M, f, sd))]
    print(f"   {len(rows)} graphs\n")
    print("   arm            hits  other member   misses   worst gap   mean gap")
    for a in ARMS:
        vals = [r.get(a) for r in rows]
        if all(v is None for v in vals):
            print(f"   {a:12s}   not run")
            continue
        got = [v for v in vals if v is not None]
        hits = sum(1 for v in got if v < 1e-9)
        other = sum(1 for r in rows if r.get(a + "_other"))
        print(f"   {a:12s}  {hits:4d}/{len(got):<3d} {other:9d}      "
              f"{len(got)-hits:5d}   {max(got):9.1f}   {np.mean(got):8.2f}")
    print("\n   'other member' counts zero-gap answers that are a DIFFERENT member")
    print("   of the optimal set than the first enumerated one. Those are hits.")
    tie = [r["ties"] for r in rows]
    print(f"   optimal set size (ties): min {min(tie)}, median "
          f"{int(np.median(tie))}, max {max(tie)}")

    print("\n   H1 - gap zero in the large majority at n = 10:")
    for a in ARMS:
        vals = [r.get(a) for r in rows]
        if all(v is None for v in vals):
            continue
        print(f"     {a:12s} {verdict(vals)}")

    # ------------------------------------------------------- 2, the size sweep
    print("\n\n2 - Size sweep, density 1.5, same families and seeds")
    print("-" * 78)
    print("   mean gap in remote gates; (b) = some METIS answer was unbalanced\n")
    hdr = "   n    " + "".join(f"{a:>14s}" for a in ARMS)
    print(hdr)
    sweep = {}
    for n in SIZES:
        pt._PART_CACHE.clear()                    # the n = 24 matrix is large
        rs = [r for f in FAMILIES for sd in SEEDS
              if (r := measure(n, int(round(DENSITY * n)), f, sd))]
        sweep[n] = rs
        line = f"   {n:<5d}"
        for a in ARMS:
            vals = [r.get(a) for r in rs]
            got = [v for v in vals if v is not None]
            if not got:
                line += f"{'-':>14s}"
                continue
            mark = ""
            if a == "metis" and any(r.get("metis_balanced") is False for r in rs):
                mark = "b"
            line += f"{np.mean(got):>13.2f}{mark:1s}"
        print(line)
        sys.stdout.flush()

    print("\n   H2 - does the mean gap grow with n?")
    for a in ARMS:
        ms = []
        for n in SIZES:
            got = [r.get(a) for r in sweep[n] if r.get(a) is not None]
            ms.append(np.mean(got) if got else np.nan)
        if np.all(np.isnan(ms)):
            continue
        first, last = ms[0], ms[-1]
        print(f"     {a:12s} n=10 {first:6.2f}  ->  n=24 {last:6.2f}   "
              f"{verdict([r.get(a) for r in sweep[SIZES[-1]]])}")

    # ------------------------------------------------------------- 3, METIS
    print("\n\n3 - METIS and the comparison class")
    print("-" * 78)
    if not HAVE_METIS:
        print("   pymetis not installed - this section is not run.")
    else:
        for n in SIZES:
            rs = sweep[n]
            bad = [r for r in rs if r.get("metis_balanced") is False]
            splits = sorted({r["metis_split"] for r in bad})
            print(f"   n = {n:<3d} unbalanced in {len(bad):2d} of {len(rs)} graphs"
                  + (f"; smaller side {splits}" if bad else ""))
        print("\n   An unbalanced cut minimises over a larger set than the balanced")
        print("   optimum, so it can be smaller. Those answers are excluded above")
        print("   rather than reported as a negative gap.")

    # --------------------------------------------- 4, the flattering baseline
    print("\n\n4 - How flattering is a random balanced baseline?")
    print("-" * 78)
    print("   arXiv 2605.01974 normalises seven partitioners against exactly this.\n")
    print("   n      optimum   random    random excess over optimum")
    for n in SIZES:
        rs = sweep[n]
        opt = np.mean([r["opt"] for r in rs])
        rnd = np.mean([r["opt"] + r["random"] for r in rs])
        print(f"   {n:<5d}  {opt:7.2f}  {rnd:7.2f}   {100*(rnd/opt-1):8.0f} %")
    print("\n   Measured against the optimum instead, the room a partitioner has to")
    print("   look good against the random baseline is this large.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
